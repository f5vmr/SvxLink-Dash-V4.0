import re
import subprocess
from pathlib import Path


NANOPI_HELPER = (
    "/usr/local/sbin/"
    "svxlink_dashboard_nanopi_prepare"
)

I2C_DEVICE = Path("/dev/i2c-0")
ASOUND_CARDS = Path("/proc/asound/cards")

ANALOG_CODEC_PATTERN = re.compile(
    r"(?:H3\s+Audio\s+Codec|sun8i[^\n]*codec)",
    re.IGNORECASE,
)


def _run_helper(*args):
    command = [
        "sudo",
        "-n",
        NANOPI_HELPER,
        *args,
    ]
    result = subprocess.run(
        command,
        text=True,
        capture_output=True,
    )
    return {
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "command": " ".join(command),
    }


def helper_available():
    """Return whether the installed NanoPi helper exists."""
    return Path(NANOPI_HELPER).is_file()


def check_boot_configuration():
    """Return the helper's read-only boot-overlay status."""
    return _run_helper("status")


def configure_boot():
    """Request persistent NanoPi I2C and codec overlays."""
    return _run_helper("configure")


def i2c_available():
    """Return whether the NanoPi I2C bus is exposed."""
    return I2C_DEVICE.exists()


def read_sound_cards():
    """Return the current ALSA card listing."""
    try:
        return ASOUND_CARDS.read_text(
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return ""


def analog_codec_available():
    """Return whether ALSA reports the H3 analog codec."""
    return bool(
        ANALOG_CODEC_PATTERN.search(
            read_sound_cards()
        )
    )


def boot_configuration_ready(result):
    """Return whether helper output reports both overlays."""
    return bool(
        result.get("ok")
        and "READY=yes" in result.get("stdout", "")
    )


def build_nanopi_status():
    """Return NanoPi preparation state for the web page."""
    status = {
        "helper_available": helper_available(),
        "boot_check": None,
        "boot_configured": False,
        "i2c_available": i2c_available(),
        "analog_codec_available": (
            analog_codec_available()
        ),
    }

    if status["helper_available"]:
        status["boot_check"] = (
            check_boot_configuration()
        )
        status["boot_configured"] = (
            boot_configuration_ready(
                status["boot_check"]
            )
        )

    status["ready"] = all([
        status["helper_available"],
        status["boot_configured"],
        status["i2c_available"],
        status["analog_codec_available"],
    ])

    return status