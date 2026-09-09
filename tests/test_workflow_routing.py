#!/usr/bin/env python3

import unittest
from unittest.mock import patch

import app as dashboard
from pathlib import Path
from models.node_model import new_node_model


class WorkflowRoutingTests(unittest.TestCase):

    def multiport_model(self):
        model = new_node_model()
        model["hardware"] = {
            "family": "usb_multi_interface",
        }
        model["hardware_profile_id"] = "dual_usb"
        model["ports"] = {
            "enabled": ["1", "2"],
        }
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
        model["modules_multi"] = {
            "echolink_port": None,
            "metar_ports": [],
        }
        model["metar"].update({
            "region": "ukwide",
            "startdefault": None,
            "airports": [],
        })
        return model

    def post_port_modules(self, model, reconfigure=False):
        form = {
            "echolink_port": "none",
            "metar_ports": "1",
        }

        if reconfigure:
            form["reconfigure"] = "1"

        with patch.object(
            dashboard,
            "load_node_model",
            return_value=model,
        ), patch.object(
            dashboard,
            "save_node_model",
        ):
            with dashboard.app.test_request_context(
                "/port-modules",
                method="POST",
                data=form,
            ):
                return dashboard.port_modules_page()

    def test_initial_port_modules_sets_explicit_metar_return(self):
        model = self.multiport_model()

        response = self.post_port_modules(model)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["Location"],
            "/metar-default?return_to=port_ident",
        )
        self.assertNotIn(
            "return_after_metar",
            model.get("build", {}),
        )
        self.assertNotIn(
            "return_after_modules",
            model.get("build", {}),
        )

    def test_reconfigured_port_modules_returns_metar_to_build(self):
        model = self.multiport_model()

        response = self.post_port_modules(
            model,
            reconfigure=True,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["Location"],
            "/metar-default?return_to=build",
        )

    def test_metar_default_preserves_explicit_return(self):
        model = self.multiport_model()
        airport = next(
            iter(dashboard.METAR_REGIONS["ukwide"])
        )

        with patch.object(
            dashboard,
            "load_node_model",
            return_value=model,
        ), patch.object(
            dashboard,
            "save_node_model",
        ):
            with dashboard.app.test_request_context(
                "/metar-default",
                method="POST",
                data={
                    "startdefault": airport,
                    "return_to": "build",
                },
            ):
                response = dashboard.metar_default_page()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["Location"],
            "/metar-airports?return_to=build",
        )

    def test_metar_airports_returns_to_port_ident(self):
        model = self.multiport_model()
        airport = next(
            iter(dashboard.METAR_REGIONS["ukwide"])
        )
        model["metar"]["startdefault"] = airport

        with patch.object(
            dashboard,
            "load_node_model",
            return_value=model,
        ), patch.object(
            dashboard,
            "save_node_model",
        ):
            with dashboard.app.test_request_context(
                "/metar-airports",
                method="POST",
                data={
                    "return_to": "port_ident",
                },
            ):
                response = dashboard.metar_airports_page()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["Location"],
            "/port-ident",
        )

    def test_metar_airports_returns_to_build(self):
        model = self.multiport_model()
        airport = next(
            iter(dashboard.METAR_REGIONS["ukwide"])
        )
        model["metar"]["startdefault"] = airport

        with patch.object(
            dashboard,
            "load_node_model",
            return_value=model,
        ), patch.object(
            dashboard,
            "save_node_model",
        ):
            with dashboard.app.test_request_context(
                "/metar-airports",
                method="POST",
                data={
                    "return_to": "build",
                },
            ):
                response = dashboard.metar_airports_page()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["Location"],
            "/build",
        )

    def test_reflector_completion_routes_to_node_information(self):
        for model in (
            new_node_model(),
            self.multiport_model(),
        ):
            with self.subTest(
                multiport=dashboard.is_multiport_build(model),
            ):
                with dashboard.app.test_request_context():
                    self.assertEqual(
                        dashboard.next_after_reflector(model),
                        "/node-info",
                    )
    def test_authentication_setup_continues_to_review(self):
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
            "generate_password_hash",
            return_value="test-password-hash",
        ):
            with dashboard.app.test_request_context(
                "/setup-auth",
                method="POST",
                data={
                    "username": "operator",
                    "password": "private-test-password",
                },
            ):
                response = dashboard.setup_auth_page()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["Location"],
            "/review",
        )
        self.assertEqual(
            model["dashboard_auth"]["username"],
            "operator",
        )
        self.assertEqual(
            model["dashboard_auth"]["password_hash"],
            "test-password-hash",
        )
        save_mock.assert_called_once_with(model)

    def test_node_information_uses_correct_next_step(self):
        cases = (
            (
                new_node_model(),
                "/setup-auth",
            ),
            (
                self.multiport_model(),
                "/topology",
            ),
        )

        for model, expected_location in cases:
            with self.subTest(
                expected_location=expected_location,
            ):
                with patch.object(
                    dashboard,
                    "load_node_model",
                    return_value=model,
                ), patch.object(
                    dashboard,
                    "save_node_model",
                ) as save_mock, patch.object(
                    dashboard,
                    "update_node_information_from_form",
                    return_value=model["node_info"],
                ), patch.object(
                    dashboard,
                    "update_location_information_from_form",
                    return_value=model["location_info"],
                ), patch.object(
                    dashboard,
                    "validate_node_information",
                    return_value=[],
                ):
                    with dashboard.app.test_request_context(
                        "/node-info",
                        method="POST",
                        data={},
                    ):
                        response = dashboard.node_info_page()

                self.assertEqual(response.status_code, 302)
                self.assertEqual(
                    response.headers["Location"],
                    expected_location,
                )
                save_mock.assert_called_once_with(model)

    def test_multiport_final_validation_uses_correct_destination(self):
        cases = (
            (
                False,
                False,
                "/setup-auth",
            ),
            (
                True,
                False,
                "/review",
            ),
            (
                True,
                True,
                "/build",
            ),
        )

        for authenticated, reconfigure, expected_location in cases:
            with self.subTest(
                authenticated=authenticated,
                reconfigure=reconfigure,
            ):
                model = self.multiport_model()
                model.setdefault("build", {}).update({
                    "topology_configured": True,
                    "tones_configured": True,
                })

                for node in model["nodes"].values():
                    node.update({
                        "node_details_configured": True,
                        "squelch_configured": True,
                        "ident_configured": True,
                        "cw_configured": True,
                        "repeater_configured": True,
                    })

                if authenticated:
                    model["dashboard_auth"] = {
                        "username": "operator",
                        "password_hash": "test-password-hash",
                    }

                form = {}

                if reconfigure:
                    form["reconfigure"] = "1"

                with patch.object(
                    dashboard,
                    "load_node_model",
                    return_value=model,
                ), patch.object(
                    dashboard,
                    "save_node_model",
                ) as save_mock, patch.object(
                    dashboard,
                    "validate_topology",
                    return_value=[],
                ):
                    with dashboard.app.test_request_context(
                        "/port-final-review",
                        method="POST",
                        data=form,
                    ):
                        response = (
                            dashboard.port_final_review_page()
                        )

                self.assertEqual(response.status_code, 302)
                self.assertEqual(
                    response.headers["Location"],
                    expected_location,
                )
                self.assertTrue(
                    model["build"][
                        "port_final_review_confirmed"
                    ]
                )
                save_mock.assert_called_once_with(model)

    def test_echolink_form_omits_managed_location_prefix(self):
        model = new_node_model()
        model["echolink"].update({
            "enabled": True,
            "callsign": "G4NAB-R",
            "password": "test-password",
            "sysopname": "Chris",
            "location": "[Svx] London",
        })

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
            return_value=model,
        ), patch.object(
            dashboard,
            "render_template",
            side_effect=capture_template,
        ):
            with dashboard.app.test_request_context(
                "/echolink",
                method="GET",
            ):
                response = dashboard.echolink_page()

        self.assertEqual(response, "rendered")
        self.assertEqual(
            captured["template_name"],
            "echolink.html",
        )
        self.assertEqual(
            captured["context"]["location_text"],
            "London",
        )

    def test_reconfigured_modules_use_explicit_build_return(self):
        cases = (
            (
                {
                    "reconfigure": "1",
                },
                "/build",
            ),
            (
                {
                    "reconfigure": "1",
                    "module_echolink": "yes",
                },
                "/echolink?return_to=build",
            ),
            (
                {
                    "reconfigure": "1",
                    "module_metar": "yes",
                },
                "/metar-default?return_to=build",
            ),
        )

        for form, expected_location in cases:
            with self.subTest(
                expected_location=expected_location,
            ):
                model = new_node_model()

                with patch.object(
                    dashboard,
                    "load_node_model",
                    return_value=model,
                ), patch.object(
                    dashboard,
                    "save_node_model",
                ) as save_mock:
                    with dashboard.app.test_request_context(
                        "/modules",
                        method="POST",
                        data=form,
                    ):
                        response = dashboard.modules_page()

                self.assertEqual(response.status_code, 302)
                self.assertEqual(
                    response.headers["Location"],
                    expected_location,
                )
                save_mock.assert_called_once_with(model)

    def test_reconfigured_echolink_preserves_build_return(self):
        cases = (
            (
                False,
                "/build",
            ),
            (
                True,
                "/metar-default?return_to=build",
            ),
        )

        for metar_enabled, expected_location in cases:
            with self.subTest(
                metar_enabled=metar_enabled,
            ):
                model = new_node_model()
                model["metar"]["enabled"] = metar_enabled

                with patch.object(
                    dashboard,
                    "load_node_model",
                    return_value=model,
                ), patch.object(
                    dashboard,
                    "save_node_model",
                ) as save_mock:
                    with dashboard.app.test_request_context(
                        "/echolink",
                        method="POST",
                        data={
                            "return_to": "build",
                            "echolink_callsign": "G4NAB-R",
                            "echolink_password": "test-password",
                            "echolink_sysopname": "Chris",
                            "echolink_location": "London",
                        },
                    ):
                        response = dashboard.echolink_page()

                self.assertEqual(response.status_code, 302)
                self.assertEqual(
                    response.headers["Location"],
                    expected_location,
                )
                self.assertEqual(
                    model["echolink"]["location"],
                    "[Svx] London",
                )
                save_mock.assert_called_once_with(model)

    def test_reconfigured_node_information_returns_to_build(self):
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
            "update_node_information_from_form",
            return_value=model["node_info"],
        ), patch.object(
            dashboard,
            "update_location_information_from_form",
            return_value=model["location_info"],
        ), patch.object(
            dashboard,
            "validate_node_information",
            return_value=[],
        ), patch.object(
            dashboard,
            "build_svxlink_configuration",
        ) as build_mock:
            with dashboard.app.test_request_context(
                "/edit/node-info",
                method="POST",
                data={
                    "reconfigure": "1",
                },
            ):
                dashboard.session["authorised"] = True
                response = dashboard.node_info_edit_page()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["Location"],
            "/build",
        )
        save_mock.assert_called_once_with(model)
        build_mock.assert_not_called()

    def test_reconfiguration_menu_includes_shared_targets(self):
        for model in (
            new_node_model(),
            self.multiport_model(),
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
                return_value=model,
            ), patch.object(
                dashboard,
                "render_template",
                side_effect=capture_template,
            ):
                with dashboard.app.test_request_context(
                    "/reconfigure",
                    method="GET",
                ):
                    response = dashboard.reconfigure_page()

            self.assertEqual(response, "rendered")
            self.assertEqual(
                captured["template_name"],
                "reconfigure.html",
            )

            target_ids = {
                target["id"]
                for target in captured["context"][
                    "reconfigure_targets"
                ]
            }

            self.assertTrue({
                "modules",
                "reflector",
                "node_info",
                "tones",
                "build",
                "full_reset",
            }.issubset(target_ids))

    def test_reflector_selection_template_matches_current_route(self):
        template_text = Path(
            "templates/reflector.html"
        ).read_text(
            encoding="utf-8"
        )

        dashboard.app.jinja_env.parse(template_text)

        self.assertIn(
            'name="reflector_route"',
            template_text,
        )
        self.assertIn(
            'value="none"',
            template_text,
        )
        self.assertIn(
            'value="federation"',
            template_text,
        )
        self.assertIn(
            'value="v2"',
            template_text,
        )
        self.assertIn(
            'value="v3"',
            template_text,
        )
        self.assertIn(
            "SvxLink Dashboard password",
            template_text,
        )
        self.assertNotIn(
            'name="connect"',
            template_text,
        )

    def test_reconfiguration_back_links_return_to_menu(self):
        template_names = (
            "environment.html",
            "timezone.html",
            "node.html",
            "interface.html",
            "squelch.html",
            "ident.html",
            "cw.html",
            "courtesy.html",
            "repeater.html",
            "modules.html",
            "reflector.html",
            "topology.html",
            "port_final_review.html",
        )

        for template_name in template_names:
            with self.subTest(
                template_name=template_name,
            ):
                template_text = (
                    Path("templates") / template_name
                ).read_text(
                    encoding="utf-8"
                )

                self.assertIn(
                    "reconfigure_page",
                    template_text,
                )

    def test_invalid_model_cannot_start_build(self):
        model = new_node_model()
        validation = {
            "validation_errors": [
                "Callsign is required.",
            ],
            "platform_errors": [],
        }
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
            return_value=model,
        ), patch.object(
            dashboard,
            "validate_build",
            return_value=validation,
        ) as validate_mock, patch.object(
            dashboard,
            "build_svxlink_configuration",
        ) as build_mock, patch.object(
            dashboard,
            "render_template",
            side_effect=capture_template,
        ):
            with dashboard.app.test_request_context(
                "/build",
                method="POST",
                data={},
            ):
                response = dashboard.build_page()

        self.assertEqual(response, "rendered")
        self.assertEqual(
            captured["template_name"],
            "build.html",
        )
        self.assertFalse(
            captured["context"]["build_allowed"],
        )
        self.assertEqual(
            captured["context"]["validation_errors"],
            validation["validation_errors"],
        )
        validate_mock.assert_called_once_with(model)
        build_mock.assert_not_called()

    def test_valid_model_may_start_build(self):
        model = new_node_model()
        validation = {
            "validation_errors": [],
            "platform_errors": [],
        }
        build_result = {
            "success": True,
            "service_status": "active",
        }
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
            return_value=model,
        ), patch.object(
            dashboard,
            "validate_build",
            return_value=validation,
        ), patch.object(
            dashboard,
            "build_svxlink_configuration",
            return_value=build_result,
        ) as build_mock, patch.object(
            dashboard,
            "render_template",
            side_effect=capture_template,
        ):
            with dashboard.app.test_request_context(
                "/build",
                method="POST",
                data={},
            ):
                response = dashboard.build_page()

        self.assertEqual(response, "rendered")
        self.assertEqual(
            captured["template_name"],
            "done.html",
        )
        build_mock.assert_called_once_with(
            model,
            restart=True,
        )

    def test_invalid_review_cannot_continue_to_build(self):
        model = new_node_model()
        model["dashboard_auth"] = {
            "username": "operator",
            "password_hash": "test-password-hash",
        }
        validation = {
            "validation_errors": [
                "Callsign is required.",
            ],
            "platform_errors": [],
        }
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
            return_value=model,
        ), patch.object(
            dashboard,
            "validate_build",
            return_value=validation,
        ), patch.object(
            dashboard,
            "render_template",
            side_effect=capture_template,
        ):
            with dashboard.app.test_request_context(
                "/review",
                method="POST",
                data={},
            ):
                response = dashboard.review_page()

        self.assertEqual(response, "rendered")
        self.assertEqual(
            captured["template_name"],
            "review.html",
        )
        self.assertFalse(
            captured["context"]["review_allowed"],
        )
        self.assertEqual(
            captured["context"]["validation_errors"],
            validation["validation_errors"],
        )

    def test_valid_review_continues_to_build(self):
        model = new_node_model()
        model["dashboard_auth"] = {
            "username": "operator",
            "password_hash": "test-password-hash",
        }
        validation = {
            "validation_errors": [],
            "platform_errors": [],
        }

        with patch.object(
            dashboard,
            "load_node_model",
            return_value=model,
        ), patch.object(
            dashboard,
            "validate_build",
            return_value=validation,
        ) as validate_mock:
            with dashboard.app.test_request_context(
                "/review",
                method="POST",
                data={},
            ):
                response = dashboard.review_page()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["Location"],
            "/build",
        )
        validate_mock.assert_called_once_with(model)

    def test_review_template_contains_final_validation_summary(self):
        template_text = Path(
            "templates/review.html"
        ).read_text(
            encoding="utf-8"
        )

        dashboard.app.jinja_env.parse(template_text)

        required_labels = (
            "Primary-port completion",
            "Reflector-route completion",
            "ReflectorLogic callsign",
            "Runtime-managed talkgroups",
            "Installation-wide tones",
            "LocationInfo completion",
            "Reflector link ports",
            "Independent ports",
            "Local link",
            "Resolve Configuration Issues",
            "Repair Node Information",
        )

        for label in required_labels:
            with self.subTest(label=label):
                self.assertIn(label, template_text)

if __name__ == "__main__":
    unittest.main()
