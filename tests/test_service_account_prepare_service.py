#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch

from services import service_account_prepare_service as service


class ServiceAccountPrepareServiceTests(unittest.TestCase):

    def test_gpio_mode_calls_common_helper(self):
        completed = Mock(
            returncode=0,
            stdout="",
            stderr="",
        )

        with patch.object(
            service.subprocess,
            "run",
            return_value=completed,
        ) as run:
            result = service.prepare_service_account(
                require_gpio=True
            )

        self.assertTrue(result["ok"])
        run.assert_called_once_with(
            [
                "sudo",
                "-n",
                service.SERVICE_ACCOUNT_HELPER,
                "gpio",
            ],
            text=True,
            capture_output=True,
        )

    def test_non_gpio_mode_calls_common_helper(self):
        completed = Mock(
            returncode=0,
            stdout="",
            stderr="",
        )

        with patch.object(
            service.subprocess,
            "run",
            return_value=completed,
        ) as run:
            result = service.prepare_service_account(
                require_gpio=False
            )

        self.assertTrue(result["ok"])
        run.assert_called_once_with(
            [
                "sudo",
                "-n",
                service.SERVICE_ACCOUNT_HELPER,
                "no-gpio",
            ],
            text=True,
            capture_output=True,
        )

    def test_helper_failure_is_returned(self):
        completed = Mock(
            returncode=1,
            stdout="",
            stderr="account preparation failed",
        )

        with patch.object(
            service.subprocess,
            "run",
            return_value=completed,
        ):
            result = service.prepare_service_account(
                require_gpio=True
            )

        self.assertFalse(result["ok"])
        self.assertEqual(result["returncode"], 1)
        self.assertEqual(
            result["stderr"],
            "account preparation failed",
        )

    def test_helper_available_checks_installed_path(self):
        with patch.object(
            service.Path,
            "is_file",
            return_value=True,
        ):
            self.assertTrue(service.helper_available())


if __name__ == "__main__":
    unittest.main()
