import unittest
from unittest.mock import Mock, patch

from services.nanopi_prepare_service import (
    NANOPI_HELPER,
    _run_helper,
    analog_codec_available,
    boot_configuration_ready,
    build_nanopi_status,
)


class NanoPiPrepareServiceTests(unittest.TestCase):

    @patch(
        "services.nanopi_prepare_service."
        "subprocess.run"
    )
    def test_helper_uses_fixed_privileged_command(
        self,
        run_mock,
    ):
        run_mock.return_value = Mock(
            returncode=0,
            stdout="READY=yes\n",
            stderr="",
        )

        result = _run_helper("status")

        run_mock.assert_called_once_with(
            [
                "sudo",
                "-n",
                NANOPI_HELPER,
                "status",
            ],
            text=True,
            capture_output=True,
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["stdout"], "READY=yes")

    @patch(
        "services.nanopi_prepare_service."
        "read_sound_cards",
        return_value=(
            " 0 [Codec         ]: H3 Audio Codec "
            "- H3 Audio Codec\n"
        ),
    )
    def test_h3_analog_codec_is_detected(
        self,
        read_mock,
    ):
        self.assertTrue(analog_codec_available())

    @patch(
        "services.nanopi_prepare_service."
        "read_sound_cards",
        return_value=(
            " 0 [USB           ]: USB-Audio "
            "- Generic USB Audio\n"
        ),
    )
    def test_usb_sound_card_is_not_h3_codec(
        self,
        read_mock,
    ):
        self.assertFalse(analog_codec_available())

    def test_boot_configuration_requires_ready_marker(
        self,
    ):
        self.assertTrue(
            boot_configuration_ready({
                "ok": True,
                "stdout": "READY=yes",
            })
        )
        self.assertFalse(
            boot_configuration_ready({
                "ok": True,
                "stdout": "READY=no",
            })
        )
        self.assertFalse(
            boot_configuration_ready({
                "ok": False,
                "stdout": "READY=yes",
            })
        )

    @patch(
        "services.nanopi_prepare_service."
        "analog_codec_available",
        return_value=True,
    )
    @patch(
        "services.nanopi_prepare_service."
        "i2c_available",
        return_value=True,
    )
    @patch(
        "services.nanopi_prepare_service."
        "check_boot_configuration",
        return_value={
            "ok": True,
            "returncode": 0,
            "stdout": "READY=yes",
            "stderr": "",
            "command": "",
        },
    )
    @patch(
        "services.nanopi_prepare_service."
        "helper_available",
        return_value=True,
    )
    def test_status_is_ready_after_reboot(
        self,
        helper_mock,
        boot_mock,
        i2c_mock,
        codec_mock,
    ):
        status = build_nanopi_status()

        self.assertTrue(status["boot_configured"])
        self.assertTrue(status["i2c_available"])
        self.assertTrue(
            status["analog_codec_available"]
        )
        self.assertTrue(status["ready"])

    @patch(
        "services.nanopi_prepare_service."
        "analog_codec_available",
        return_value=False,
    )
    @patch(
        "services.nanopi_prepare_service."
        "i2c_available",
        return_value=False,
    )
    @patch(
        "services.nanopi_prepare_service."
        "check_boot_configuration",
        return_value={
            "ok": True,
            "returncode": 0,
            "stdout": (
                "i2c0=missing\n"
                "analog-codec=missing\n"
                "READY=no"
            ),
            "stderr": "",
            "command": "",
        },
    )
    @patch(
        "services.nanopi_prepare_service."
        "helper_available",
        return_value=True,
    )
    def test_status_is_not_ready_before_configuration(
        self,
        helper_mock,
        boot_mock,
        i2c_mock,
        codec_mock,
    ):
        status = build_nanopi_status()

        self.assertFalse(status["boot_configured"])
        self.assertFalse(status["i2c_available"])
        self.assertFalse(
            status["analog_codec_available"]
        )
        self.assertFalse(status["ready"])


if __name__ == "__main__":
    unittest.main()
