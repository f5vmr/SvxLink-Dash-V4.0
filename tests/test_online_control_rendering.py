#!/usr/bin/env python3

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from models.node_model import new_node_model
from renderers import svxlink_renderer as renderer
from services import model_store as store


EXPECTED_MANUAL_BLOCK = "\n".join([
    "# Emergency DTMF logic control.",
    "# Replace XXXXXX with a private six-digit command.",
    "# Enter XXXXXX0# to take this logic offline.",
    "# Enter XXXXXX1# to return this logic online.",
    "# Prefix the command with * if a module is active.",
    "# DTMF muting prevents the digits being retransmitted.",
    "#ONLINE_CMD=XXXXXX",
    "#ONLINE=1",
])


class OnlineControlRenderingTests(unittest.TestCase):

    def capture_values(self, render_call):
        captured = {}

        def capture(template_name, values):
            captured["template"] = template_name
            captured["values"] = values
            return "rendered"

        with patch.object(
            renderer,
            "render_config_template",
            side_effect=capture,
        ):
            result = render_call()

        self.assertEqual(result, "rendered")
        return captured

    def test_every_logic_uses_commented_manual_block(self):
        for node_type in (
            "simplex",
            "repeater",
        ):
            with self.subTest(
                scope="single",
                node_type=node_type,
            ):
                model = new_node_model()
                model["node"].update({
                    "type": node_type,
                    "callsign": "G4NAB",
                })

                captured = self.capture_values(
                    lambda: renderer.render_active_logic(
                        model
                    )
                )

                self.assertEqual(
                    captured["values"][
                        "ONLINE_CONTROL_BLOCK"
                    ],
                    EXPECTED_MANUAL_BLOCK,
                )

        for role in (
            "simplex",
            "repeater",
        ):
            with self.subTest(
                scope="port",
                role=role,
            ):
                model = new_node_model()
                node = {
                    "role": role,
                    "callsign": "G4NAB",
                    "ident": {},
                    "cw": {},
                    "repeater": {},
                    "squelch": {
                        "method": "gpiod",
                        "ctcss_tx": False,
                    },
                }

                captured = self.capture_values(
                    lambda: renderer.render_port_logic(
                        model,
                        "2",
                        node,
                    )
                )

                self.assertEqual(
                    captured["values"][
                        "ONLINE_CONTROL_BLOCK"
                    ],
                    EXPECTED_MANUAL_BLOCK,
                )

    def test_enabled_control_reaches_each_logic(self):
        for role in ("simplex", "repeater"):
            with self.subTest(scope="single", role=role):
                model = new_node_model()
                model["node"].update({
                    "type": role,
                    "callsign": "G4NAB",
                })
                model["online_control"] = {
                    "enabled": True,
                    "command": "012345",
                }

                captured = self.capture_values(
                    lambda: renderer.render_active_logic(model)
                )
                lines = captured["values"]["ONLINE_CONTROL_BLOCK"].splitlines()

                self.assertIn("ONLINE_CMD=012345", lines)
                self.assertIn("ONLINE=1", lines)

            with self.subTest(scope="port", role=role):
                node = {
                    "role": role,
                    "callsign": "G4NAB",
                    "online_control": {
                        "enabled": True,
                        "command": "654321",
                    },
                }

                captured = self.capture_values(
                    lambda: renderer.render_port_logic(model, "2", node)
                )
                lines = captured["values"]["ONLINE_CONTROL_BLOCK"].splitlines()

                self.assertIn("ONLINE_CMD=654321", lines)
                self.assertIn("ONLINE=1", lines)
                self.assertNotIn("ONLINE_CMD=012345", lines)

                node.pop("online_control")
                captured = self.capture_values(
                    lambda: renderer.render_port_logic(model, "2", node)
                )

                self.assertEqual(
                    captured["values"]["ONLINE_CONTROL_BLOCK"],
                    EXPECTED_MANUAL_BLOCK,
                )

    def test_enabled_control_rejects_invalid_commands(self):
        for command in (
            "",
            "12345",
            "1234567",
            "12345#",
            "123 56",
            "１２３４５６",
            123456,
            None,
        ):
            with self.subTest(command=command):
                with self.assertRaises(ValueError):
                    renderer.render_online_control({
                        "enabled": True,
                        "command": command,
                    })

    def test_save_preserves_online_command(self):
        model = new_node_model()
        model["online_control"] = {
            "enabled": True,
            "command": "345678",
        }

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "node_model.json"

            with patch.object(
                store,
                "CONFIG_DIR",
                root,
            ), patch.object(
                store,
                "MODEL_FILE",
                target,
            ):
                store.save_node_model(model)

            saved = json.loads(
                target.read_text(
                    encoding="utf-8"
                )
            )

        expected = {
            "enabled": True,
            "command": "345678",
        }

        self.assertEqual(
            model["online_control"],
            expected,
        )
        self.assertEqual(
            saved["online_control"],
            expected,
        )


if __name__ == "__main__":
    unittest.main()
