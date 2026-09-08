#!/usr/bin/env python3

import unittest

from models.node_model import new_node_model
from services.node_info_service import build_node_info_json


class NodeInfoServiceTests(unittest.TestCase):

    def test_disabled_location_information_produces_empty_json(self):
        model = new_node_model()
        model["location_info"]["enabled"] = False
        model["node_info"].update({
            "nodeLocation": "Northumberland",
            "qth_name": "Alnwick",
            "sysop": "G4NAB",
        })

        self.assertEqual(
            build_node_info_json(model),
            {},
        )

    def test_single_port_uses_rx1_and_tx1(self):
        model = new_node_model()
        model["location_info"]["enabled"] = True
        model["node_info"].update({
            "rx_freq": "145.500",
            "tx_freq": "145.500",
        })

        data = build_node_info_json(model)
        qth = data["qth"][0]

        self.assertEqual(
            qth["rx"]["K"]["name"],
            "Rx1",
        )
        self.assertEqual(
            qth["tx"]["K"]["name"],
            "Tx1",
        )

    def test_multiport_uses_selected_primary_port_names(self):
        model = new_node_model()
        model["location_info"]["enabled"] = True
        model["ports"] = {
            "enabled": ["1", "2"],
        }
        model["installation"]["primary_port_id"] = "2"
        model["node_info"].update({
            "rx_freq": "433.500",
            "tx_freq": "434.500",
        })

        data = build_node_info_json(model)
        qth = data["qth"][0]

        self.assertEqual(
            qth["rx"]["K"]["name"],
            "Rx2",
        )
        self.assertEqual(
            qth["tx"]["K"]["name"],
            "Tx2",
        )

    def test_single_port_ctcss_is_published_as_ctcss(self):
        model = new_node_model()
        model["location_info"]["enabled"] = True
        model["squelch"]["method"] = "ctcss"

        data = build_node_info_json(model)

        self.assertEqual(
            data["qth"][0]["rx"]["K"]["sqlType"],
            "CTCSS",
        )

    def test_multiport_primary_physical_sql_is_published_as_cor(self):
        model = new_node_model()
        model["location_info"]["enabled"] = True
        model["ports"] = {
            "enabled": ["1", "2"],
        }
        model["installation"]["primary_port_id"] = "2"
        model["nodes"] = {
            "1": {
                "squelch": {
                    "method": "ctcss",
                },
            },
            "2": {
                "squelch": {
                    "method": "hidraw",
                },
            },
        }

        data = build_node_info_json(model)

        self.assertEqual(
            data["qth"][0]["rx"]["K"]["sqlType"],
            "COR",
        )

if __name__ == "__main__":
    unittest.main()
