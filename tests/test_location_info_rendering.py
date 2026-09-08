#!/usr/bin/env python3

import unittest
from unittest.mock import patch

from models.node_model import new_node_model
from renderers.svxlink_renderer import render_location_info
from pathlib import Path


class LocationInfoRenderingTests(unittest.TestCase):

    def test_disabled_location_info_renders_nothing(self):
        model = new_node_model()
        model["location_info"]["enabled"] = False

        self.assertEqual(
            render_location_info(model),
            "",
        )

    def test_location_info_never_advertises_ctcss(self):
        model = new_node_model()
        model["location_info"].update({
            "enabled": True,
            "advertised_ctcss": "88.5",
        })

        captured = {}

        def capture(template_name, values):
            captured["template"] = template_name
            captured["values"] = values
            return "rendered"

        with patch(
            "renderers.svxlink_renderer.render_config_template",
            side_effect=capture,
        ):
            result = render_location_info(model)

        self.assertEqual(result, "rendered")
        self.assertEqual(
            captured["template"],
            "location_info.template",
        )
        self.assertEqual(
            captured["values"]["TONE"],
            "0",
        )

    def test_multiport_location_info_uses_primary_repeater(self):
        model = new_node_model()
        model["ports"] = {
            "enabled": ["1", "2"],
        }
        model["installation"]["primary_port_id"] = "2"
        model["nodes"] = {
            "1": {
                "role": "simplex",
                "callsign": "G4NAB-1",
            },
            "2": {
                "role": "repeater",
                "callsign": "G4NAB-2",
            },
        }
        model["location_info"].update({
            "enabled": True,
            "tx_offset_khz": -7600,
            "antenna_gain": "6",
            "antenna_height_unit": "feet",
            "beacon_interval": 10,
        })
        model["node_info"].update({
            "lat_dms": "55.10.51N",
            "long_dms": "01.32.45W",
            "tx_freq": "439.500",
            "tx_power": "10W",
            "antenna_height": "30",
            "antenna_direction": "omni",
        })

        captured = {}

        def capture(template_name, values):
            captured["template"] = template_name
            captured["values"] = values
            return "rendered"

        with patch(
            "renderers.svxlink_renderer.render_config_template",
            side_effect=capture,
        ):
            result = render_location_info(model)

        self.assertEqual(result, "rendered")
        values = captured["values"]

        self.assertEqual(values["CALLSIGN"], "G4NAB-2")
        self.assertEqual(values["FREQUENCY"], "439.500")
        self.assertEqual(values["TX_OFFSET"], "-7600")
        self.assertEqual(values["ANTENNA_HEIGHT"], "30feet")
        self.assertEqual(values["ANTENNA_DIR"], "-1")
        self.assertEqual(values["SYMBOL"], "/r")
        self.assertEqual(values["TONE"], "0")
        self.assertEqual(values["PRIMARY_LOGIC"], "Port2Logic")

    def test_echolink_repeater_callsign_uses_er_prefix(self):
        model = new_node_model()
        model["location_info"]["enabled"] = True
        model["echolink"].update({
            "enabled": True,
            "callsign": "G4NAB-R",
        })

        captured = {}

        def capture(template_name, values):
            captured["values"] = values
            return "rendered"

        with patch(
            "renderers.svxlink_renderer.render_config_template",
            side_effect=capture,
        ):
            render_location_info(model)

        self.assertEqual(
            captured["values"]["CALLSIGN"],
            "ER-G4NAB",
        )

    def test_single_simplex_uses_normal_callsign_and_symbol(self):
        model = new_node_model()
        model["location_info"]["enabled"] = True
        model["node"].update({
            "type": "simplex",
            "callsign": "G4NAB",
        })

        captured = {}

        def capture(template_name, values):
            captured["values"] = values
            return "rendered"

        with patch(
            "renderers.svxlink_renderer.render_config_template",
            side_effect=capture,
        ):
            render_location_info(model)

        values = captured["values"]

        self.assertEqual(values["CALLSIGN"], "G4NAB")
        self.assertEqual(values["SYMBOL"], "/n")
        self.assertEqual(
            values["PRIMARY_LOGIC"],
            "SimplexLogic",
        )

    def test_echolink_link_callsign_uses_el_prefix(self):
        model = new_node_model()
        model["location_info"]["enabled"] = True
        model["echolink"].update({
            "enabled": True,
            "callsign": "G4NAB-L",
        })

        captured = {}

        def capture(template_name, values):
            captured["values"] = values
            return "rendered"

        with patch(
            "renderers.svxlink_renderer.render_config_template",
            side_effect=capture,
        ):
            render_location_info(model)

        self.assertEqual(
            captured["values"]["CALLSIGN"],
            "EL-G4NAB",
        )

    def test_location_info_template_retains_fixed_options(self):
        template = Path(
            "templates/config/location_info.template"
        ).read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "#SOURCE_CALLSIGN=MYCALL-1",
            template,
        )
        self.assertIn(
            "#LOGIN_CALLSIGN=MYCALL-XX",
            template,
        )
        self.assertIn(
            "NARROW=1",
            template,
        )
        self.assertIn(
            "TONE={{TONE}}",
            template,
        )
        self.assertIn(
            "#STATISTICS_INTERVAL=10",
            template,
        )
        self.assertIn(
            "#STATISTICS_LOGIC={{PRIMARY_LOGIC}}",
            template,
        )

if __name__ == "__main__":
    unittest.main()
