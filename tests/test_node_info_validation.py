#!/usr/bin/env python3

import unittest
from models.node_model import new_node_model
from services.build_svxlink import validate_build
from services.node_info_validation import (
    validate_dms,
    validate_node_information,
)


class NodeInfoValidationTests(unittest.TestCase):

    def test_signed_decimal_coordinates_are_preserved_as_valid(self):
        errors = validate_node_information(
            {
                "lat": "-34.5000",
                "long": "-58.4000",
            },
            {
                "enabled": False,
            },
        )

        self.assertEqual(errors, [])

    def test_decimal_coordinate_ranges_are_enforced(self):
        errors = validate_node_information(
            {
                "lat": "90.1",
                "long": "-180.1",
            },
            {
                "enabled": False,
            },
        )

        self.assertIn(
            "Decimal latitude must be between -90 and 90.",
            errors,
        )
        self.assertIn(
            "Decimal longitude must be between -180 and 180.",
            errors,
        )

    def test_valid_svxlink_dms_coordinates(self):
        self.assertIsNone(
            validate_dms("55.10.51N", "latitude")
        )
        self.assertIsNone(
            validate_dms("001.32.45W", "longitude")
        )

    def test_dms_directions_are_coordinate_specific(self):
        self.assertEqual(
            validate_dms("55.10.51E", "latitude"),
            "Latitude DMS must end with N or S.",
        )
        self.assertEqual(
            validate_dms("01.32.45N", "longitude"),
            "Longitude DMS must end with E or W.",
        )

    def test_maidenhead_lengths_and_characters(self):
        for locator in (
            "IO84",
            "IO84AB",
            "IO84AB12",
        ):
            with self.subTest(locator=locator):
                self.assertEqual(
                    validate_node_information(
                        {
                            "locator": locator,
                        },
                        {
                            "enabled": False,
                        },
                    ),
                    [],
                )

        errors = validate_node_information(
            {
                "locator": "ZZ99",
            },
            {
                "enabled": False,
            },
        )

        self.assertIn(
            "Maidenhead locator must contain 4, 6 or 8 valid "
            "locator characters.",
            errors,
        )

    def test_location_comment_is_limited_to_36_characters(self):
        errors = validate_node_information(
            {
                "lat_dms": "55.10.51N",
                "long_dms": "01.32.45W",
                "tx_freq": "439.500",
                "tx_power": "10",
                "antenna_height": "20",
            },
            {
                "enabled": True,
                "aprs_server_list": "euro.aprs2.net:14580",
                "antenna_gain": "6",
                "antenna_height_unit": "m",
                "tx_offset_khz": 0,
                "beacon_interval": 10,
                "comment": "X" * 37,
            },
        )

        self.assertIn(
            "LocationInfo comment must not exceed 36 characters.",
            errors,
        )

    def test_build_validation_includes_node_information(self):
        model = new_node_model()
        model["node_info"]["lat"] = "90.1"
        model["location_info"]["enabled"] = False

        result = validate_build(model)

        self.assertIn(
            "Decimal latitude must be between -90 and 90.",
            result["validation_errors"],
        )

if __name__ == "__main__":
    unittest.main()
