#!/usr/bin/env python3

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from services import build_svxlink as pipeline


class BuildPipelineResultTests(unittest.TestCase):

    def run_pipeline(self, restart, service_status):
        model = {
            "node": {
                "type": "simplex",
                "callsign": "G4NAB",
            },
            "ports": {
                "enabled": [],
            },
            "nodes": {},
        }

        replacements = {
            "validate_build": Mock(return_value={
                "validation_errors": [],
                "platform_errors": [],
            }),
            "render_all": Mock(return_value={
                "svxlink.conf": "rendered",
            }),
            "backup_active_config": Mock(return_value=[]),
            "deploy_rendered_files": Mock(return_value=[
                "/etc/svxlink/svxlink.conf",
            ]),
            "render_motd_script": Mock(return_value="motd"),
            "deploy_motd_script": Mock(return_value=(
                "/etc/update-motd.d/10-uname"
            )),
            "write_node_info_json": Mock(return_value=Path(
                "/etc/svxlink/node_info.json"
            )),
            "ensure_language_pack": Mock(return_value=(
                "/usr/share/svxlink/sounds/en_GB"
            )),
            "deploy_required_logic_files": Mock(return_value=[]),
            "apply_va_barred_cw_symbol": Mock(return_value=Path(
                "/usr/share/svxlink/events.d/local/CW.tcl"
            )),
            "apply_courtesy_tone": Mock(return_value=Path(
                "/usr/share/svxlink/events.d/local/Logic.tcl"
            )),
            "restart_svxlink": Mock(),
            "svxlink_status": Mock(return_value=service_status),
        }

        with patch.multiple(
            pipeline,
            **replacements,
        ):
            return pipeline.build_svxlink_configuration(
                model,
                restart=restart,
            )

    def test_requested_restart_requires_active_service(self):
        result = self.run_pipeline(
            restart=True,
            service_status="failed",
        )

        self.assertFalse(result["success"])
        self.assertTrue(result["service_restarted"])
        self.assertEqual(result["service_status"], "failed")
        self.assertIn(
            "Configuration files were deployed, but SvxLink "
            "finished in the failed state.",
            result["deployment_errors"],
        )
        self.assertIn(
            "/etc/svxlink/svxlink.conf",
            result["rendered_files"],
        )

    def test_configuration_only_build_does_not_require_active_service(self):
        result = self.run_pipeline(
            restart=False,
            service_status="inactive",
        )

        self.assertTrue(result["success"])
        self.assertFalse(result["service_restarted"])
        self.assertEqual(
            result["service_status"],
            "inactive",
        )
        self.assertEqual(result["deployment_errors"], [])

    def test_successful_restart_reports_success(self):
        result = self.run_pipeline(
            restart=True,
            service_status="active",
        )

        self.assertTrue(result["success"])
        self.assertTrue(result["service_restarted"])
        self.assertEqual(result["service_status"], "active")
        self.assertEqual(result["deployment_errors"], [])


if __name__ == "__main__":
    unittest.main()
