#!/usr/bin/env python3

import json
import unittest

from unittest.mock import MagicMock, patch
from urllib.error import URLError

from services.metar_validation import (
    MetarVerificationUnavailable,
    find_unavailable_metar_airports,
    is_valid_icao_format,
)


class MetarValidationTests(unittest.TestCase):

    def test_icao_format_requires_exactly_four_letters(self):

        self.assertTrue(is_valid_icao_format("egnt"))
        self.assertFalse(is_valid_icao_format("EGN"))
        self.assertFalse(is_valid_icao_format("EGNT1"))
        self.assertFalse(is_valid_icao_format("EG1T"))

    def test_missing_station_is_returned(self):

        response = MagicMock()
        response.getcode.return_value = 200
        response.read.return_value = json.dumps([
            {
                "icaoId": "EGNT",
                "siteType": ["METAR", "TAF"],
            },
            {
                "icaoId": "EGNV",
                "siteType": ["METAR"],
            },
        ]).encode("utf-8")

        with patch(
            "services.metar_validation.urlopen",
        ) as urlopen_mock:
            urlopen_mock.return_value.__enter__.return_value = (
                response
            )

            missing = find_unavailable_metar_airports(
                ["EGNT", "EGNV", "ZZZZ"]
            )

        self.assertEqual(missing, ["ZZZZ"])
        urlopen_mock.assert_called_once()

    def test_no_content_marks_all_codes_unavailable(self):

        response = MagicMock()
        response.getcode.return_value = 204

        with patch(
            "services.metar_validation.urlopen",
        ) as urlopen_mock:
            urlopen_mock.return_value.__enter__.return_value = (
                response
            )

            missing = find_unavailable_metar_airports(
                ["ZZZZ"]
            )

        self.assertEqual(missing, ["ZZZZ"])

    def test_source_failure_is_not_reported_as_invalid_station(self):

        with patch(
            "services.metar_validation.urlopen",
            side_effect=URLError("offline"),
        ):
            with self.assertRaises(
                MetarVerificationUnavailable
            ):
                find_unavailable_metar_airports(["EGNT"])


if __name__ == "__main__":
    unittest.main()
