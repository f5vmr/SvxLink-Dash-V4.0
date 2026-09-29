#!/usr/bin/env python3

import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from models.node_model import new_node_model
from services import svxlink_service


class CourtesyToneServiceTests(unittest.TestCase):

    def test_selected_cw_letter_is_inserted_into_logic_tcl(self):
        model = new_node_model()
        model["tones"]["courtesy_mode"] = "R"

        with tempfile.TemporaryDirectory() as directory:
            logic_directory = Path(directory)
            logic_file = logic_directory / "Logic.tcl"

            logic_file.write_text(
                "playTone 440 500 100\n",
                encoding="utf-8",
            )

            with patch.object(
                svxlink_service,
                "LOGIC_DIR_DST",
                logic_directory,
            ):
                svxlink_service.apply_courtesy_tone(model)

            rendered = logic_file.read_text(
                encoding="utf-8"
            )

        self.assertIn(
            'CW::play "R"',
            rendered,
        )
        self.assertNotIn(
            "playTone 440 500 100",
            rendered,
        )


    def test_legacy_beep_mode_does_not_generate_a_tone(self):
        model = new_node_model()
        model["tones"]["courtesy_mode"] = "beep"

        with tempfile.TemporaryDirectory() as directory:
            logic_directory = Path(directory)
            logic_file = logic_directory / "Logic.tcl"

            logic_file.write_text(
                "playTone 440 500 100\n",
                encoding="utf-8",
            )

            with patch.object(
                svxlink_service,
                "LOGIC_DIR_DST",
                logic_directory,
            ):
                svxlink_service.apply_courtesy_tone(model)

            rendered = logic_file.read_text(
                encoding="utf-8"
            )

        self.assertIn(
            "# playTone 440 500 100",
            rendered,
        )
        self.assertNotIn(
            "playTone 800 800 60",
            rendered,
        )


if __name__ == "__main__":
    unittest.main()
