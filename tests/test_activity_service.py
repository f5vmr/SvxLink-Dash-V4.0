#!/usr/bin/env python3

import unittest

from datetime import datetime, timezone
from unittest.mock import patch

from services import activity_service


class ReflectorActivityTests(unittest.TestCase):

    def test_activity_uses_rotation_aware_log_reader(self):

        timestamp = datetime.now(
            timezone.utc
        ).strftime("%a %b %d %H:%M:%S %Y")

        lines = [
            (
                f"{timestamp}: ReflectorLogic: Talker stop "
                "on TG #235: G4NAB"
            ),
            (
                f"{timestamp}: ReflectorLogic: Talker start "
                "on TG #235: G4NAB"
            ),
        ]

        with patch.object(
            activity_service,
            "read_recent_svxlink_log_lines",
            return_value=lines,
        ) as log_mock:
            activity = (
                activity_service.get_reflector_activity()
            )

        self.assertEqual(len(activity), 1)
        self.assertEqual(activity[0]["callsign"], "G4NAB")
        self.assertEqual(activity[0]["tg"], "235")
        self.assertTrue(activity[0]["active"])
        log_mock.assert_called_once_with(300)


if __name__ == "__main__":
    unittest.main()
