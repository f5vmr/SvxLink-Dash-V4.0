#!/usr/bin/env python3

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from services import dtmf_service
import app as dashboard

class DtmfControlPathTests(unittest.TestCase):

    def get_path(self, model, selected_port=None):
        with tempfile.TemporaryDirectory() as directory:
            model_path = Path(directory) / "node_model.json"
            model_path.write_text(
                json.dumps(model),
                encoding="utf-8",
            )

            with patch.object(
                dtmf_service,
                "NODE_MODEL",
                model_path,
            ):
                return dtmf_service.get_dtmf_control_path(
                    selected_port=selected_port,
                )

    def test_multiport_uses_selected_port_pty(self):
        model = {
            "installation": {
                "primary_port_id": "1",
            },
            "ports": {
                "enabled": ["1", "2"],
            },
            "nodes": {
                "1": {
                    "role": "simplex",
                },
                "2": {
                    "role": "repeater",
                },
            },
        }

        self.assertEqual(
            self.get_path(model, selected_port="2"),
            Path("/dev/shm/port2_dtmf_ctrl"),
        )

    def test_eight_port_build_uses_selected_port_pty(self):
        enabled_ports = [
            str(port)
            for port in range(1, 9)
        ]

        model = {
            "ports": {
                "enabled": enabled_ports,
            },
            "nodes": {
                port_id: {
                    "role": (
                        "repeater"
                        if int(port_id) % 2 == 0
                        else "simplex"
                    ),
                }
                for port_id in enabled_ports
            },
        }

        self.assertEqual(
            self.get_path(model, selected_port="8"),
            Path("/dev/shm/port8_dtmf_ctrl"),
        )

    def test_missing_selection_uses_first_enabled_port(self):
        model = {
            "ports": {
                "enabled": ["3", "4"],
            },
            "nodes": {
                "3": {
                    "role": "simplex",
                },
                "4": {
                    "role": "repeater",
                },
            },
        }

        self.assertEqual(
            self.get_path(model),
            Path("/dev/shm/port3_dtmf_ctrl"),
        )

    def test_single_repeater_retains_existing_pty(self):
        model = {
            "node": {
                "type": "repeater",
            },
        }

        self.assertEqual(
            self.get_path(model),
            Path("/dev/shm/repeater_dtmf_ctrl"),
        )

    def test_single_simplex_retains_existing_pty(self):
        model = {
            "node": {
                "type": "simplex",
            },
        }

        self.assertEqual(
            self.get_path(model),
            Path("/dev/shm/simplex_dtmf_ctrl"),
        )

    def test_send_dtmf_passes_selected_port_to_path_resolver(self):
        with tempfile.TemporaryDirectory() as directory:
            dtmf_path = Path(directory) / "port8_dtmf_ctrl"
            dtmf_path.touch()

            with patch.object(
                dtmf_service,
                "get_dtmf_control_path",
                return_value=dtmf_path,
            ) as path_mock:
                result = dtmf_service.send_dtmf(
                    "91235#",
                    selected_port="8",
                )

            path_mock.assert_called_once_with(
                selected_port="8",
            )
            self.assertEqual(result, "91235#")
            self.assertEqual(
                dtmf_path.read_text(encoding="utf-8"),
                "91235#",
            )

class DtmfRouteTests(unittest.TestCase):

    def test_route_sends_to_selected_port_and_returns_to_it(self):
        model = {
            "ports": {
                "enabled": ["1", "2"],
            },
            "nodes": {
                "1": {
                    "role": "simplex",
                },
                "2": {
                    "role": "repeater",
                },
            },
        }

        with patch.object(
            dashboard,
            "load_node_model",
            return_value=model,
        ), patch.object(
            dashboard,
            "send_dtmf",
        ) as send_mock:
            with dashboard.app.test_request_context(
                "/dtmf?selected_port=2",
                method="POST",
                data={
                    "command": "91235#",
                },
            ):
                response = dashboard.dtmf_page()

        send_mock.assert_called_once_with(
            "91235#",
            selected_port="2",
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["Location"],
            "/status?port=2",
        )

if __name__ == "__main__":
    unittest.main()
