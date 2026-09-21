#!/usr/bin/env python3

import tempfile
import unittest

from pathlib import Path

from services.dual_usb_service import (
    inspect_dual_usb_hardware,
)


def make_usb_card(
    index,
    name,
    description,
):
    return {
        "index": index,
        "name": name,
        "description": description,
        "has_playback": True,
        "has_capture": True,
        "audio_dev": (
            f"alsa:plughw:CARD={name},DEV=0"
        ),
    }


def create_hidraw_identity(
    sys_class_hidraw,
    device_name,
    vendor="00000D8C",
    product="0000000C",
):
    device_directory = (
        Path(sys_class_hidraw)
        / device_name
        / "device"
    )
    device_directory.mkdir(
        parents=True,
        exist_ok=True,
    )
    (
        device_directory / "uevent"
    ).write_text(
        (
            "DRIVER=hid-generic\n"
            f"HID_ID=0003:{vendor}:{product}\n"
        ),
        encoding="utf-8",
    )


class DualUsbServiceTests(unittest.TestCase):

    def test_two_cmedia_interfaces_are_ready(self):
        cards = [
            make_usb_card(
                2,
                "Set",
                "USB-Audio C-Media USB Headphone Set",
            ),
            make_usb_card(
                3,
                "Device",
                "USB-Audio C-Media USB Audio Device",
            ),
        ]

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dev = root / "dev"
            sys_class = root / "sys" / "class" / "hidraw"

            dev.mkdir()

            hidraw0 = dev / "hidraw0"
            hidraw1 = dev / "hidraw1"
            hidraw0.touch()
            hidraw1.touch()

            create_hidraw_identity(
                sys_class,
                "hidraw0",
                product="0000000C",
            )
            create_hidraw_identity(
                sys_class,
                "hidraw1",
                product="00000012",
            )

            result = inspect_dual_usb_hardware(
                cards=cards,
                hidraw_devices=(
                    hidraw0,
                    hidraw1,
                ),
                sys_class_hidraw=sys_class,
                access_check=lambda path, mode: True,
            )

        self.assertTrue(result["ready"])
        self.assertEqual(result["errors"], [])
        self.assertEqual(
            result["ports"][0]["audio_index"],
            2,
        )
        self.assertEqual(
            result["ports"][0]["audio_dev"],
            "alsa:plughw:CARD=Set,DEV=0",
        )
        self.assertEqual(
            result["ports"][1]["audio_index"],
            3,
        )
        self.assertEqual(
            result["ports"][1]["audio_dev"],
            "alsa:plughw:CARD=Device,DEV=0",
        )
        self.assertEqual(
            result["ports"][0]["audio_name"],
            "Set",
        )
        self.assertEqual(
            result["ports"][1]["audio_name"],
            "Device",
        )
        self.assertTrue(
            result["ports"][0]["hidraw_is_cmedia"]
        )
        self.assertTrue(
            result["ports"][1]["hidraw_is_cmedia"]
        )

    def test_missing_second_interface_is_rejected(self):
        cards = [
            make_usb_card(
                2,
                "Set",
                "USB-Audio C-Media USB Headphone Set",
            ),
        ]

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dev = root / "dev"
            sys_class = root / "sys" / "class" / "hidraw"

            dev.mkdir()

            hidraw0 = dev / "hidraw0"
            hidraw1 = dev / "hidraw1"
            hidraw0.touch()

            create_hidraw_identity(
                sys_class,
                "hidraw0",
            )

            result = inspect_dual_usb_hardware(
                cards=cards,
                hidraw_devices=(
                    hidraw0,
                    hidraw1,
                ),
                sys_class_hidraw=sys_class,
                access_check=lambda path, mode: True,
            )

        self.assertFalse(result["ready"])
        self.assertTrue(
            any(
                "Exactly two duplex USB audio devices"
                in error
                for error in result["errors"]
            )
        )
        self.assertTrue(
            any(
                "Port 2 requires a duplex USB audio device"
                in error
                for error in result["errors"]
            )
        )
        self.assertTrue(
            any(
                "hidraw1"
                in error
                for error in result["errors"]
            )
        )

    def test_non_cmedia_or_inaccessible_hidraw_is_rejected(self):
        cards = [
            make_usb_card(
                2,
                "Set",
                "USB-Audio C-Media USB Headphone Set",
            ),
            make_usb_card(
                3,
                "Device",
                "USB-Audio C-Media USB Audio Device",
            ),
        ]

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dev = root / "dev"
            sys_class = root / "sys" / "class" / "hidraw"

            dev.mkdir()

            hidraw0 = dev / "hidraw0"
            hidraw1 = dev / "hidraw1"
            hidraw0.touch()
            hidraw1.touch()

            create_hidraw_identity(
                sys_class,
                "hidraw0",
            )
            create_hidraw_identity(
                sys_class,
                "hidraw1",
                vendor="00001234",
            )

            def access_check(path, mode):
                return Path(path).name != "hidraw0"

            result = inspect_dual_usb_hardware(
                cards=cards,
                hidraw_devices=(
                    hidraw0,
                    hidraw1,
                ),
                sys_class_hidraw=sys_class,
                access_check=access_check,
            )

        self.assertFalse(result["ready"])
        self.assertTrue(
            any(
                "hidraw0" in error
                and "not readable and writable" in error
                for error in result["errors"]
            )
        )
        self.assertTrue(
            any(
                "hidraw1" in error
                and "not a C-Media interface" in error
                for error in result["errors"]
            )
        )


if __name__ == "__main__":
    unittest.main()
