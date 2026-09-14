import subprocess
from pathlib import Path


SERVICE_ACCOUNT_HELPER = (
    "/usr/local/sbin/"
    "svxlink_dashboard_service_account_prepare"
)


def helper_available():
    """Return whether the service-account helper is installed."""
    return Path(SERVICE_ACCOUNT_HELPER).is_file()


def prepare_service_account(require_gpio):
    """
    Prepare the existing svxlink service account.

    GPIO platforms receive audio, plugdev, gpio and dialout
    membership together with persistent GPIO device access.

    Non-GPIO platforms receive audio, plugdev and dialout
    membership.
    """
    mode = "gpio" if require_gpio else "no-gpio"

    command = [
        "sudo",
        "-n",
        SERVICE_ACCOUNT_HELPER,
        mode,
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
