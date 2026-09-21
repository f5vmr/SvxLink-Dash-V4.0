#!/usr/bin/env python3

"""
Inspect the two-device USB audio and HIDRAW installation.
"""

import os

from pathlib import Path

from services.sound_discovery import discover_sound_cards


CMEDIA_VENDOR_ID = "00000D8C"

EXPECTED_AUDIO_INDICES = (0, 1)

EXPECTED_HIDRAW_DEVICES = (
    Path("/dev/hidraw0"),
    Path("/dev/hidraw1"),
)

SYS_CLASS_HIDRAW = Path("/sys/class/hidraw")


def is_duplex_usb_card(card):
    """Return True for a duplex USB audio device."""

    description = (
        f"{card.get('name', '')} "
        f"{card.get('description', '')}"
    ).lower()

    return (
        bool(card.get("has_playback"))
        and bool(card.get("has_capture"))
        and "usb" in description
    )


def read_hidraw_uevent(
    device,
    sys_class_hidraw=SYS_CLASS_HIDRAW,
):
    """Read the kernel identity record for one HIDRAW device."""

    device = Path(device)
    uevent_path = (
        Path(sys_class_hidraw)
        / device.name
        / "device"
        / "uevent"
    )

    try:
        return uevent_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )
    except OSError:
        return ""


def is_cmedia_hidraw(
    device,
    sys_class_hidraw=SYS_CLASS_HIDRAW,
):
    """Return True when a HIDRAW device belongs to C-Media."""

    uevent = read_hidraw_uevent(
        device,
        sys_class_hidraw=sys_class_hidraw,
    )

    for line in uevent.splitlines():
        if not line.startswith("HID_ID="):
            continue

        components = line.partition("=")[2].split(":")

        if len(components) != 3:
            return False

        return components[1].upper() == CMEDIA_VENDOR_ID

    return False


def inspect_dual_usb_hardware(
    cards=None,
    hidraw_devices=EXPECTED_HIDRAW_DEVICES,
    sys_class_hidraw=SYS_CLASS_HIDRAW,
    access_check=os.access,
):
    """
    Inspect the fixed two-port USB interface contract.

    Port 1 uses ALSA card 0 and /dev/hidraw0.
    Port 2 uses ALSA card 1 and /dev/hidraw1.
    """

    if cards is None:
        cards = discover_sound_cards()

    usb_cards = sorted(
        (
            card
            for card in cards
            if is_duplex_usb_card(card)
        ),
        key=lambda card: int(card.get("index", -1)),
    )

    cards_by_index = {
        int(card["index"]): card
        for card in usb_cards
    }

    errors = []
    ports = []

    if len(usb_cards) != 2:
        errors.append(
            "Exactly two duplex USB audio devices are required; "
            f"{len(usb_cards)} were detected."
        )

    hidraw_devices = [
        Path(device)
        for device in hidraw_devices
    ]

    for port_number, audio_index in enumerate(
        EXPECTED_AUDIO_INDICES,
        start=1,
    ):
        card = cards_by_index.get(audio_index)

        hidraw_device = (
            hidraw_devices[port_number - 1]
            if len(hidraw_devices) >= port_number
            else Path(f"/dev/hidraw{audio_index}")
        )

        hidraw_exists = hidraw_device.exists()
        hidraw_accessible = (
            hidraw_exists
            and access_check(
                hidraw_device,
                os.R_OK | os.W_OK,
            )
        )
        hidraw_is_cmedia = (
            hidraw_exists
            and is_cmedia_hidraw(
                hidraw_device,
                sys_class_hidraw=sys_class_hidraw,
            )
        )

        if card is None:
            errors.append(
                f"Port {port_number} requires duplex USB "
                f"audio card {audio_index}."
            )

        if not hidraw_exists:
            errors.append(
                f"Port {port_number} HID device was not found: "
                f"{hidraw_device}"
            )
        elif not hidraw_is_cmedia:
            errors.append(
                f"Port {port_number} HID device is not a "
                f"C-Media interface: {hidraw_device}"
            )
        elif not hidraw_accessible:
            errors.append(
                f"Port {port_number} HID device is not readable "
                f"and writable: {hidraw_device}"
            )

        ports.append({
            "port": str(port_number),
            "audio_index": audio_index,
            "audio_dev": f"alsa:plughw:{audio_index}",
            "audio_name": (
                card.get("name", "")
                if card
                else ""
            ),
            "audio_description": (
                card.get("description", "")
                if card
                else ""
            ),
            "hidraw_device": str(hidraw_device),
            "hidraw_exists": hidraw_exists,
            "hidraw_accessible": hidraw_accessible,
            "hidraw_is_cmedia": hidraw_is_cmedia,
        })

    return {
        "ready": not errors,
        "ports": ports,
        "errors": errors,
    }
