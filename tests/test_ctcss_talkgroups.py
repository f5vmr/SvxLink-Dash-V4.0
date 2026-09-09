#!/usr/bin/env python3

import unittest

from unittest.mock import patch

import app as dashboard

from models.node_model import new_node_model


class CtcssTalkgroupPageTests(unittest.TestCase):

    def setUp(self):
        self.model = new_node_model()
        self.model["node"].update({
            "type": "simplex",
            "callsign": "G4NAB",
        })

    def render_page(
        self,
        path="/ctcss-talkgroups",
    ):
        captured = {}

        def capture_template(
            template_name,
            **context,
        ):
            captured["template_name"] = template_name
            captured["context"] = context
            return "rendered"

        with patch.object(
            dashboard,
            "load_node_model",
            return_value=self.model,
        ), patch.object(
            dashboard,
            "render_template",
            side_effect=capture_template,
        ):
            with dashboard.app.test_request_context(
                path
            ):
                dashboard.session["authorised"] = True
                response = (
                    dashboard.ctcss_talkgroups_page()
                )

        return response, captured

    def test_unauthorised_access_redirects(self):
        with dashboard.app.test_request_context(
            "/ctcss-talkgroups"
        ):
            response = (
                dashboard.ctcss_talkgroups_page()
            )

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            "/authorise",
            response.headers["Location"],
        )

    def test_single_port_is_selected(self):
        response, captured = self.render_page()

        self.assertEqual(response, "rendered")
        self.assertEqual(
            captured["template_name"],
            "ctcss_talkgroups.html",
        )
        self.assertFalse(
            captured["context"]["multiport"]
        )
        self.assertEqual(
            captured["context"]["logic_label"],
            "Simplex",
        )
        self.assertIs(
            captured["context"]["configuration"],
            self.model["ctcss_to_tg"],
        )

    def test_single_ctcss_sql_is_unavailable(self):
        self.model["squelch"].update({
            "method": "ctcss",
            "ctcss_freq": "88.5",
        })

        _response, captured = self.render_page()

        self.assertEqual(
            captured["context"]["logic_label"],
            "",
        )

    def configure_multiport(self):
        self.model["ports"] = {
            "enabled": ["1", "2"],
        }
        self.model["nodes"] = {
            "1": {
                "name": "Local simplex",
                "role": "simplex",
                "squelch": {
                    "method": "gpiod",
                },
                "ctcss_to_tg": {
                    "enabled": False,
                    "delay_ms": 0,
                    "mappings": [],
                },
            },
            "2": {
                "name": "Protected repeater",
                "role": "repeater",
                "squelch": {
                    "method": "ctcss",
                    "ctcss_freq": "88.5",
                },
                "ctcss_to_tg": {
                    "enabled": False,
                    "delay_ms": 0,
                    "mappings": [],
                },
            },
        }

    def test_multiport_lists_only_eligible_ports(self):
        self.configure_multiport()

        _response, captured = self.render_page()

        self.assertEqual(
            captured["context"]["eligible_ports"],
            [
                {
                    "id": "1",
                    "label": "Local simplex",
                },
            ],
        )
        self.assertEqual(
            captured["context"]["selected_port"],
            "1",
        )

    def test_ineligible_requested_port_falls_back(self):
        self.configure_multiport()

        _response, captured = self.render_page(
            "/ctcss-talkgroups?port=2"
        )

        self.assertEqual(
            captured["context"]["selected_port"],
            "1",
        )
        self.assertEqual(
            captured["context"]["logic_label"],
            "Local simplex",
        )

    def test_valid_single_port_form_saves_and_rebuilds(self):
        form = {
            "enabled": "yes",
            "delay_ms": "1000",
            "tone_0": "88.5",
            "talkgroup_0": "000235",
            "tone_1": "123.0",
            "talkgroup_1": "2350",
        }

        with patch.object(
            dashboard,
            "load_node_model",
            return_value=self.model,
        ), patch.object(
            dashboard,
            "save_node_model",
        ) as save_mock, patch.object(
            dashboard,
            "build_svxlink_configuration",
            return_value={"success": True},
        ) as build_mock:
            with dashboard.app.test_request_context(
                "/ctcss-talkgroups",
                method="POST",
                data=form,
            ):
                dashboard.session["authorised"] = True
                response = (
                    dashboard.ctcss_talkgroups_page()
                )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["Location"],
            "/ctcss-talkgroups?saved=1",
        )
        self.assertEqual(
            self.model["ctcss_to_tg"],
            {
                "enabled": True,
                "delay_ms": 1000,
                "mappings": [
                    {
                        "tone": "88.5",
                        "talkgroup": "235",
                    },
                    {
                        "tone": "123.0",
                        "talkgroup": "2350",
                    },
                ],
            },
        )
        save_mock.assert_called_once_with(self.model)
        build_mock.assert_called_once_with(
            self.model,
            restart=True,
        )

    def test_valid_multiport_form_updates_selected_port(self):
        self.configure_multiport()

        form = {
            "enabled": "yes",
            "delay_ms": "500",
            "tone_0": "77.0",
            "talkgroup_0": "999",
        }

        with patch.object(
            dashboard,
            "load_node_model",
            return_value=self.model,
        ), patch.object(
            dashboard,
            "save_node_model",
        ) as save_mock, patch.object(
            dashboard,
            "build_svxlink_configuration",
            return_value={"success": True},
        ):
            with dashboard.app.test_request_context(
                "/ctcss-talkgroups?port=1",
                method="POST",
                data=form,
            ):
                dashboard.session["authorised"] = True
                response = (
                    dashboard.ctcss_talkgroups_page()
                )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            self.model["nodes"]["1"]["ctcss_to_tg"],
            {
                "enabled": True,
                "delay_ms": 500,
                "mappings": [
                    {
                        "tone": "77.0",
                        "talkgroup": "999",
                    },
                ],
            },
        )
        self.assertFalse(
            self.model["nodes"]["2"][
                "ctcss_to_tg"
            ]["enabled"]
        )
        save_mock.assert_called_once_with(self.model)

    def test_invalid_form_does_not_save_or_rebuild(self):
        captured = {}

        def capture_template(
            template_name,
            **context,
        ):
            captured["template_name"] = template_name
            captured["context"] = context
            return "invalid"

        form = {
            "enabled": "yes",
            "delay_ms": "-1",
            "tone_0": "88.5",
            "talkgroup_0": "235",
            "tone_1": "88.5",
            "talkgroup_1": "23.5",
        }

        with patch.object(
            dashboard,
            "load_node_model",
            return_value=self.model,
        ), patch.object(
            dashboard,
            "save_node_model",
        ) as save_mock, patch.object(
            dashboard,
            "build_svxlink_configuration",
        ) as build_mock, patch.object(
            dashboard,
            "render_template",
            side_effect=capture_template,
        ):
            with dashboard.app.test_request_context(
                "/ctcss-talkgroups",
                method="POST",
                data=form,
            ):
                dashboard.session["authorised"] = True
                response = (
                    dashboard.ctcss_talkgroups_page()
                )

        self.assertEqual(response, "invalid")
        self.assertEqual(
            captured["template_name"],
            "ctcss_talkgroups.html",
        )

        errors = " ".join(
            captured["context"]["errors"]
        )

        self.assertIn(
            "delay must be a whole number",
            errors,
        )
        self.assertIn(
            "tone 88.5 Hz is entered more than once",
            errors,
        )
        self.assertIn(
            "positive whole-number TalkGroup",
            errors,
        )
        save_mock.assert_not_called()
        build_mock.assert_not_called()

    def test_rebuild_failure_is_reported(self):
        captured = {}

        def capture_template(
            template_name,
            **context,
        ):
            captured["context"] = context
            return "failed rebuild"

        form = {
            "delay_ms": "0",
        }

        with patch.object(
            dashboard,
            "load_node_model",
            return_value=self.model,
        ), patch.object(
            dashboard,
            "save_node_model",
        ) as save_mock, patch.object(
            dashboard,
            "build_svxlink_configuration",
            return_value={"success": False},
        ), patch.object(
            dashboard,
            "render_template",
            side_effect=capture_template,
        ):
            with dashboard.app.test_request_context(
                "/ctcss-talkgroups",
                method="POST",
                data=form,
            ):
                dashboard.session["authorised"] = True
                response = (
                    dashboard.ctcss_talkgroups_page()
                )

        self.assertEqual(response, "failed rebuild")
        self.assertIn(
            "rebuild or",
            " ".join(
                captured["context"]["errors"]
            ),
        )
        self.assertEqual(
            self.model["ctcss_to_tg"],
            {
                "enabled": False,
                "delay_ms": 0,
                "mappings": [],
            },
        )
        save_mock.assert_called_once_with(self.model)

if __name__ == "__main__":
    unittest.main()
