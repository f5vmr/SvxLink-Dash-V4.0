#!/usr/bin/env python3

import unittest
from unittest.mock import patch

import app as dashboard
from models.node_model import new_node_model


class NodeInfoConfigurationTests(unittest.TestCase):

    def test_british_isles_uses_documented_aprs_suggestion(self):
        model = new_node_model()
        model["environment"] = {
            "region": "british_isles",
        }

        self.assertEqual(
            dashboard.get_aprs_server_suggestion(model),
            "euro.aprs2.net:14580",
        )

    def test_other_environment_does_not_invent_aprs_suggestion(self):
        model = new_node_model()
        model["environment"] = {
            "region": "north_america",
        }

        self.assertEqual(
            dashboard.get_aprs_server_suggestion(model),
            "",
        )

    def test_echolink_publication_requires_echolink(self):
        model = new_node_model()
        model["echolink"]["enabled"] = False

        location_info = (
            dashboard.update_location_information_from_form(
                model,
                {
                    "location_info_enabled": "yes",
                    "publish_echolink_status": "yes",
                },
            )
        )

        self.assertFalse(
            location_info["publish_echolink_status"]
        )

    def test_echolink_publication_can_be_selected_when_enabled(self):
        model = new_node_model()
        model["echolink"]["enabled"] = True

        location_info = (
            dashboard.update_location_information_from_form(
                model,
                {
                    "location_info_enabled": "yes",
                    "publish_echolink_status": "yes",
                },
            )
        )

        self.assertTrue(
            location_info["publish_echolink_status"]
        )

    def test_protected_edit_rebuilds_configuration(self):
        model = new_node_model()

        with patch.object(
            dashboard,
            "load_node_model",
            return_value=model,
        ), patch.object(
            dashboard,
            "save_node_model",
        ) as save_mock, patch.object(
            dashboard,
            "build_svxlink_configuration",
            return_value={
                "success": True,
            },
        ) as build_mock:
            with dashboard.app.test_request_context(
                "/edit/node-info",
                method="POST",
                data={
                    "location_info_enabled": "no",
                },
            ):
                dashboard.session["authorised"] = True
                response = dashboard.node_info_edit_page()

        save_mock.assert_called_once_with(model)
        build_mock.assert_called_once_with(
            model,
            restart=True,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["Location"],
            "/edit/node-info?saved=1",
        )

    def test_custom_signed_offset_is_preserved(self):
        model = new_node_model()

        location_info = (
            dashboard.update_location_information_from_form(
                model,
                {
                    "location_info_enabled": "yes",
                    "tx_offset_khz": "custom",
                    "custom_tx_offset_khz": "-7123",
                },
            )
        )

        self.assertEqual(
            location_info["tx_offset_khz"],
            -7123,
        )

if __name__ == "__main__":
    unittest.main()
