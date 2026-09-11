#!/usr/bin/env python3

import unittest

from hw_platforms import get_platform_profile
from services.hardware_profile_service import load_hardware_profile
from services.ics_prepare_service import VALID_ICS_PROFILES

class HardwareMatrixTests(unittest.TestCase):

    def test_supported_platform_profiles_are_os_release_independent(self):
        expectations = {
            "raspberry_pi": {
                "name": "Raspberry Pi",
                "interfaces": {
                    "gpiod",
                    "hidraw",
                    "hybrid",
                },
            },
            "nanopi_neo": {
                "name": "NanoPi-Neo",
                "interfaces": {
                    "gpiod",
                    "hidraw",
                },
            },
            "linux_server": {
                "name": "Generic Linux Server",
                "interfaces": {
                    "hidraw",
                    "serial",
                },
            },
        }

        for platform_id, expected in expectations.items():
            with self.subTest(platform_id=platform_id):
                profile = get_platform_profile(platform_id)

                self.assertTrue(profile["supported"])
                self.assertEqual(
                    profile["name"],
                    expected["name"],
                )
                self.assertEqual(
                    set(profile["allowed_interface_modes"]),
                    expected["interfaces"],
                )
                self.assertEqual(
                    set(profile["allowed_node_types"]),
                    {"simplex", "repeater"},
                )

    def test_generic_and_dual_usb_hardware_profiles(self):
        generic = load_hardware_profile(
            "generic_single"
        )
        dual = load_hardware_profile("dual_usb")

        self.assertEqual(generic["type"], "generic")
        self.assertEqual(generic["ports"], 1)
        self.assertFalse(
            generic["preparation"]["required"]
        )

        self.assertEqual(
            dual["family"],
            "usb_multi_interface",
        )
        self.assertEqual(dual["ports"], 2)
        self.assertEqual(
            dual["audio"]["backend"],
            "alsa_multi_device",
        )
        self.assertEqual(
            set(dual["control"]["supported_methods"]),
            {"hidraw", "gpiod", "serial"},
        )

        for port_id in ("1", "2"):
            with self.subTest(port=port_id):
                port = dual["port_map"][port_id]

                self.assertEqual(
                    port["rx_audio"],
                    (
                        "alsa:plughw:0"
                        if port_id == "1"
                        else "alsa:plughw:1"
                    ),
                )
                self.assertEqual(
                    port["tx_audio"],
                    port["rx_audio"],
                )
                self.assertEqual(
                    port["hidraw_device"],
                    (
                        "/dev/hidraw0"
                        if port_id == "1"
                        else "/dev/hidraw1"
                    ),
                )
                self.assertEqual(
                    port["hidraw_sql_pin"],
                    "VOL_DN",
                )
                self.assertEqual(
                    port["hidraw_ptt_pin"],
                    "GPIO3",
                )

    def test_all_ics_profiles_have_consistent_port_limits(self):
        expected_i2c = {
            "ics_1x": ["0x20"],
            "ics_2x": ["0x20"],
            "ics_4x": ["0x26", "0x27"],
            "ics_8x": ["0x25", "0x26", "0x27"],
        }

        for port_count in (1, 2, 4, 8):
            profile_id = f"ics_{port_count}x"

            with self.subTest(profile_id=profile_id):
                hardware_profile = (
                    load_hardware_profile(profile_id)
                )
                preparation_profile = (
                    VALID_ICS_PROFILES[profile_id]
                )

                self.assertEqual(
                    hardware_profile["family"],
                    "ics",
                )
                self.assertEqual(
                    hardware_profile["type"],
                    "port_based",
                )
                self.assertEqual(
                    hardware_profile["ports"],
                    port_count,
                )
                self.assertTrue(
                    hardware_profile["preparation"][
                        "required"
                    ]
                )
                self.assertTrue(
                    hardware_profile["preparation"][
                        "requires_reboot"
                    ]
                )
                self.assertEqual(
                    preparation_profile["max_ports"],
                    port_count,
                )
                self.assertEqual(
                    preparation_profile["expected_i2c"],
                    expected_i2c[profile_id],
                )

                if port_count in (4, 8):
                    port_map = hardware_profile[
                        "port_map"
                    ]
                    self.assertEqual(
                        set(port_map),
                        {
                            str(port)
                            for port in range(
                                1,
                                port_count + 1,
                            )
                        },
                    )

                    for port_id, port in port_map.items():
                        self.assertEqual(
                            port["rx_audio"],
                            f"alsa:rx{port_id}",
                        )
                        self.assertEqual(
                            port["tx_audio"],
                            f"alsa:tx{port_id}",
                        )
                        self.assertEqual(
                            port["ptt"],
                            f"TX_{port_id}",
                        )
                        self.assertEqual(
                            port["cos"],
                            f"RX_{port_id}",
                        )
