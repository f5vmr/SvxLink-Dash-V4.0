#!/usr/bin/env python3

import unittest

from models.node_model import new_node_model
from services.build_svxlink import render_all


class BuildCombinationTests(unittest.TestCase):

    def single_model(self, node_type):
        model = new_node_model()
        model["node"].update({
            "type": node_type,
            "callsign": "G4NAB",
        })
        model["reflector"]["enabled"] = False
        model["reflector"]["route"] = "none"
        return model

    def enable_federation(self, model):
        model["reflector"]["enabled"] = True
        model["reflector"]["route"] = "federation"
        model["reflector"]["operational"].update({
            "default_tg": 310,
            "monitor_tgs": ["310", "3100"],
            "tg_select_timeout": 60,
        })
        model["reflector"]["federation"].update({
            "network_id": "north_america",
            "name": "North America",
            "host": "north.america.svxlink.net",
            "port": 35300,
            "auth_key": "1234567890ABCDEF",
        })
        return model

    def ics_model(self, port_count):
        model = new_node_model()
        model["hardware"] = {
            "family": "ics",
        }
        model["hardware_profile_id"] = (
            f"ics_{port_count}x"
        )

        enabled_ports = [
            str(port)
            for port in range(1, port_count + 1)
        ]

        model["ports"] = {
            "enabled": enabled_ports,
        }
        model["installation"]["primary_port_id"] = "1"
        model["nodes"] = {
            port_id: {
                "role": "simplex",
                "callsign": f"G4NAB-{port_id}",
                "audio": {
                    "rx_audio": f"alsa:rx{port_id}",
                    "tx_audio": f"alsa:tx{port_id}",
                },
                "squelch": {
                    "method": "gpiod",
                },
                "gpio": {},
            }
            for port_id in enabled_ports
        }
        model["topology"] = {
            "reflector_link": {
                "name": "LinkToReflector",
                "ports": [],
                "default_active": True,
                "timeout": 300,
            },
            "local_links": [],
            "independent_ports": list(enabled_ports),
        }
        return model

    def test_single_simplex_without_reflector(self):
        rendered = render_all(
            self.single_model("simplex")
        )

        self.assertEqual(
            set(rendered),
            {"svxlink.conf"},
        )

        configuration = rendered["svxlink.conf"]

        self.assertIn(
            "LOGICS=SimplexLogic\n",
            configuration,
        )
        self.assertIn(
            "[SimplexLogic]\n",
            configuration,
        )
        self.assertIn(
            "TYPE=Simplex\n",
            configuration,
        )
        self.assertIn(
            "#LINKS=LinkToReflector\n",
            configuration,
        )
        self.assertNotIn(
            "[ReflectorLogic]\n",
            configuration,
        )

    def test_single_repeater_without_reflector(self):
        rendered = render_all(
            self.single_model("repeater")
        )

        self.assertEqual(
            set(rendered),
            {"svxlink.conf"},
        )

        configuration = rendered["svxlink.conf"]

        self.assertIn(
            "LOGICS=RepeaterLogic\n",
            configuration,
        )
        self.assertIn(
            "[RepeaterLogic]\n",
            configuration,
        )
        self.assertIn(
            "TYPE=Repeater\n",
            configuration,
        )
        self.assertIn(
            "#LINKS=LinkToReflector\n",
            configuration,
        )
        self.assertNotIn(
            "[ReflectorLogic]\n",
            configuration,
        )

    def test_single_simplex_with_federation(self):
        model = self.enable_federation(
            self.single_model("simplex")
        )

        rendered = render_all(model)
        configuration = rendered["svxlink.conf"]

        self.assertIn(
            "LOGICS=SimplexLogic,ReflectorLogic\n",
            configuration,
        )
        self.assertIn(
            "LINKS=LinkToReflector\n",
            configuration,
        )
        self.assertIn(
            "[SimplexLogic]\n",
            configuration,
        )
        self.assertIn(
            "[ReflectorLogic]\n",
            configuration,
        )
        self.assertIn(
            "TYPE=ReflectorV2\n",
            configuration,
        )
        self.assertIn(
            "HOSTS=north.america.svxlink.net\n",
            configuration,
        )
        self.assertIn(
            'AUTH_KEY="1234567890ABCDEF"\n',
            configuration,
        )
        self.assertIn(
            "DEFAULT_TG=310\n",
            configuration,
        )
        self.assertIn(
            "MONITOR_TGS=310,3100\n",
            configuration,
        )

    def test_single_repeater_with_federation(self):
        model = self.enable_federation(
            self.single_model("repeater")
        )

        rendered = render_all(model)
        configuration = rendered["svxlink.conf"]

        self.assertIn(
            "LOGICS=RepeaterLogic,ReflectorLogic\n",
            configuration,
        )
        self.assertIn(
            "LINKS=LinkToReflector\n",
            configuration,
        )
        self.assertIn(
            "[RepeaterLogic]\n",
            configuration,
        )
        self.assertIn(
            "TYPE=Repeater\n",
            configuration,
        )
        self.assertIn(
            "[ReflectorLogic]\n",
            configuration,
        )
        self.assertIn(
            "TYPE=ReflectorV2\n",
            configuration,
        )
        self.assertIn(
            "HOSTS=north.america.svxlink.net\n",
            configuration,
        )
        self.assertIn(
            "DEFAULT_TG=310\n",
            configuration,
        )

    def test_single_node_with_independent_protocol_2(self):
        model = self.single_model("simplex")
        model["reflector"]["enabled"] = True
        model["reflector"]["route"] = "v2"
        model["reflector"]["operational"].update({
            "default_tg": 235,
            "monitor_tgs": ["235", "2350"],
            "tg_select_timeout": 60,
        })
        model["reflector"]["v2"].update({
            "name": "Independent Network",
            "host": "v2.example.test",
            "port": 5300,
            "auth_key": "short-password",
        })

        rendered = render_all(model)
        configuration = rendered["svxlink.conf"]

        self.assertIn(
            "LOGICS=SimplexLogic,ReflectorLogic\n",
            configuration,
        )
        self.assertIn(
            "LINKS=LinkToReflector\n",
            configuration,
        )
        self.assertIn(
            "[ReflectorLogic]\n",
            configuration,
        )
        self.assertIn(
            "TYPE=ReflectorV2\n",
            configuration,
        )
        self.assertIn(
            "HOSTS=v2.example.test\n",
            configuration,
        )
        self.assertIn(
            "HOST_PORT=5300\n",
            configuration,
        )
        self.assertIn(
            'AUTH_KEY="short-password"\n',
            configuration,
        )
        self.assertNotIn(
            "north.america.svxlink.net",
            configuration,
        )

    def test_single_node_with_protocol_3(self):
        model = self.single_model("simplex")
        model["reflector"]["enabled"] = True
        model["reflector"]["route"] = "v3"
        model["reflector"]["operational"].update({
            "default_tg": 235,
            "monitor_tgs": ["235", "2350"],
            "tg_select_timeout": 60,
        })
        model["reflector"]["v3"].update({
            "name": "Certificate Network",
            "host": "v3.example.test",
            "port": 5300,
        })
        model["reflector"]["v3"]["subject"].update({
            "given_name": "Chris",
            "surname": "Jackson",
            "organizational_unit": "Amateur Radio",
            "organization": "Test Network",
            "locality": "Ashington",
            "state_or_province": "Northumberland",
            "country": "GB",
            "email": "test@example.test",
        })

        rendered = render_all(model)
        configuration = rendered["svxlink.conf"]

        self.assertIn(
            "LOGICS=SimplexLogic,ReflectorLogic\n",
            configuration,
        )
        self.assertIn(
            "LINKS=LinkToReflector\n",
            configuration,
        )
        self.assertIn(
            "[ReflectorLogic]\n",
            configuration,
        )
        self.assertIn(
            "TYPE=Reflector\n",
            configuration,
        )
        self.assertNotIn(
            "TYPE=ReflectorV2\n",
            configuration,
        )
        self.assertIn(
            "HOSTS=v3.example.test\n",
            configuration,
        )
        self.assertIn(
            "CERT_KEYFILE=/var/lib/svxlink/pki/G4NAB.key\n",
            configuration,
        )
        self.assertIn(
            "CERT_SUBJ_givenName=Chris\n",
            configuration,
        )
        self.assertIn(
            "CERT_SUBJ_surname=Jackson\n",
            configuration,
        )
        self.assertIn(
            "CERT_SUBJ_countryName=GB\n",
            configuration,
        )
        self.assertIn(
            "CERT_EMAIL=test@example.test\n",
            configuration,
        )
        self.assertIn(
            '#AUTH_KEY="Change this key now!"\n',
            configuration,
        )

    def test_ics_1x_uses_multiport_rendering_path(self):
        model = new_node_model()
        model["hardware"] = {
            "family": "ics",
        }
        model["hardware_profile_id"] = "ics_1x"
        model["ports"] = {
            "enabled": ["1"],
        }
        model["installation"]["primary_port_id"] = "1"
        model["nodes"] = {
            "1": {
                "role": "simplex",
                "callsign": "G4NAB-1",
                "audio": {
                    "rx_audio": "alsa:rx1",
                    "tx_audio": "alsa:tx1",
                },
                "squelch": {
                    "method": "gpiod",
                },
                "gpio": {},
            },
        }
        model["topology"] = {
            "reflector_link": {
                "name": "LinkToReflector",
                "ports": [],
                "default_active": True,
                "timeout": 300,
            },
            "local_links": [],
            "independent_ports": ["1"],
        }

        rendered = render_all(model)
        configuration = rendered["svxlink.conf"]

        self.assertIn(
            "LOGICS=Port1Logic\n",
            configuration,
        )
        self.assertIn(
            "#LINKS=\n",
            configuration,
        )
        self.assertIn(
            "[Port1Logic]\n",
            configuration,
        )
        self.assertIn(
            "TYPE=Simplex\n",
            configuration,
        )
        self.assertIn(
            "RX=Rx1\n",
            configuration,
        )
        self.assertIn(
            "TX=Tx1\n",
            configuration,
        )
        self.assertIn(
            "DTMF_CTRL_PTY=/dev/shm/port1_dtmf_ctrl\n",
            configuration,
        )
        self.assertIn(
            "[Rx1]\n",
            configuration,
        )
        self.assertIn(
            "AUDIO_DEV=alsa:rx1\n",
            configuration,
        )
        self.assertIn(
            "[Tx1]\n",
            configuration,
        )
        self.assertIn(
            "AUDIO_DEV=alsa:tx1\n",
            configuration,
        )
        self.assertNotIn(
            "[SimplexLogic]\n",
            configuration,
        )

    def test_two_ports_with_reflector_on_primary_only(self):
        model = self.enable_federation(
            self.ics_model(2)
        )
        model["topology"]["reflector_link"]["ports"] = [
            "1",
        ]
        model["topology"]["independent_ports"] = ["2"]

        rendered = render_all(model)
        configuration = rendered["svxlink.conf"]

        self.assertIn(
            "LOGICS=Port1Logic,Port2Logic,ReflectorLogic\n",
            configuration,
        )
        self.assertIn(
            "LINKS=LinkToReflector\n",
            configuration,
        )
        self.assertIn(
            "[Port1Logic]\n",
            configuration,
        )
        self.assertIn(
            "[Port2Logic]\n",
            configuration,
        )
        self.assertIn(
            (
                "CONNECT_LOGICS="
                "Port1Logic:9,ReflectorLogic\n"
            ),
            configuration,
        )
        self.assertNotIn(
            (
                "CONNECT_LOGICS="
                "Port1Logic:9,Port2Logic:9,"
                "ReflectorLogic\n"
            ),
            configuration,
        )

    def test_two_ports_with_both_ports_on_reflector(self):
        model = self.enable_federation(
            self.ics_model(2)
        )
        model["topology"]["reflector_link"]["ports"] = [
            "1",
            "2",
        ]
        model["topology"]["independent_ports"] = []

        rendered = render_all(model)
        configuration = rendered["svxlink.conf"]

        self.assertIn(
            "LOGICS=Port1Logic,Port2Logic,ReflectorLogic\n",
            configuration,
        )
        self.assertIn(
            "LINKS=LinkToReflector\n",
            configuration,
        )
        self.assertIn(
            (
                "CONNECT_LOGICS="
                "Port1Logic:9,Port2Logic:9,"
                "ReflectorLogic\n"
            ),
            configuration,
        )
        self.assertIn(
            "ACTIVATE_ON_ACTIVITY=Port1Logic\n",
            configuration,
        )

    def test_two_port_local_link_without_reflector(self):
        model = self.ics_model(2)
        model["topology"]["local_links"] = [
            {
                "name": "LocalRadioLink",
                "ports": ["1", "2"],
                "default_active": True,
                "timeout": 300,
            },
        ]
        model["topology"]["independent_ports"] = []

        rendered = render_all(model)
        configuration = rendered["svxlink.conf"]

        self.assertIn(
            "LOGICS=Port1Logic,Port2Logic\n",
            configuration,
        )
        self.assertIn(
            "LINKS=LocalRadioLink\n",
            configuration,
        )
        self.assertIn(
            "[LocalRadioLink]\n",
            configuration,
        )
        self.assertIn(
            "CONNECT_LOGICS=Port1Logic:9,Port2Logic:9\n",
            configuration,
        )
        self.assertIn(
            "DEFAULT_ACTIVE=1\n",
            configuration,
        )
        self.assertIn(
            "TIMEOUT=300\n",
            configuration,
        )
        self.assertNotIn(
            "[ReflectorLogic]\n",
            configuration,
        )
        self.assertNotIn(
            "[LinkToReflector]\n",
            configuration,
        )

    def test_four_port_mixed_topology(self):
        model = self.enable_federation(
            self.ics_model(4)
        )
        model["nodes"]["2"]["role"] = "repeater"
        model["topology"]["reflector_link"]["ports"] = [
            "1",
        ]
        model["topology"]["local_links"] = [
            {
                "name": "LocalRadioLink",
                "ports": ["2", "3"],
                "default_active": True,
                "timeout": 180,
            },
        ]
        model["topology"]["independent_ports"] = ["4"]

        rendered = render_all(model)
        configuration = rendered["svxlink.conf"]

        self.assertIn(
            (
                "LOGICS=Port1Logic,Port2Logic,"
                "Port3Logic,Port4Logic,ReflectorLogic\n"
            ),
            configuration,
        )
        self.assertIn(
            "LINKS=LinkToReflector,LocalRadioLink\n",
            configuration,
        )
        self.assertIn(
            "CONNECT_LOGICS=Port1Logic:9,ReflectorLogic\n",
            configuration,
        )
        self.assertIn(
            "CONNECT_LOGICS=Port2Logic:9,Port3Logic:9\n",
            configuration,
        )
        self.assertIn(
            "[Port4Logic]\n",
            configuration,
        )
        self.assertIn(
            "DTMF_CTRL_PTY=/dev/shm/port4_dtmf_ctrl\n",
            configuration,
        )
        self.assertEqual(
            configuration.count("[ReflectorLogic]"),
            1,
        )
        self.assertEqual(
            configuration.count("[LocalRadioLink]"),
            1,
        )

    def test_eight_port_model_rendering_stress(self):
        model = self.enable_federation(
            self.ics_model(8)
        )

        for port_id in ("2", "4", "6", "8"):
            model["nodes"][port_id]["role"] = "repeater"

        model["topology"]["reflector_link"]["ports"] = [
            "1",
            "2",
        ]
        model["topology"]["local_links"] = [
            {
                "name": "LocalLinkA",
                "ports": ["3", "4"],
                "default_active": True,
                "timeout": 180,
            },
            {
                "name": "LocalLinkB",
                "ports": ["5", "6"],
                "default_active": False,
                "timeout": 120,
            },
        ]
        model["topology"]["independent_ports"] = [
            "7",
            "8",
        ]

        rendered = render_all(model)
        configuration = rendered["svxlink.conf"]

        expected_logics = (
            "LOGICS=Port1Logic,Port2Logic,"
            "Port3Logic,Port4Logic,"
            "Port5Logic,Port6Logic,"
            "Port7Logic,Port8Logic,"
            "ReflectorLogic\n"
        )
        self.assertIn(expected_logics, configuration)
        self.assertIn(
            (
                "LINKS=LinkToReflector,"
                "LocalLinkA,LocalLinkB\n"
            ),
            configuration,
        )

        for port in range(1, 9):
            with self.subTest(port=port):
                self.assertEqual(
                    configuration.count(
                        f"[Port{port}Logic]"
                    ),
                    1,
                )
                self.assertEqual(
                    configuration.count(f"[Rx{port}]"),
                    1,
                )
                self.assertEqual(
                    configuration.count(f"[Tx{port}]"),
                    1,
                )
                self.assertIn(
                    (
                        "DTMF_CTRL_PTY="
                        f"/dev/shm/port{port}_dtmf_ctrl\n"
                    ),
                    configuration,
                )

        self.assertEqual(
            configuration.count("[ReflectorLogic]"),
            1,
        )
        self.assertEqual(
            configuration.count("[LocalLinkA]"),
            1,
        )
        self.assertEqual(
            configuration.count("[LocalLinkB]"),
            1,
        )

if __name__ == "__main__":
    unittest.main()
