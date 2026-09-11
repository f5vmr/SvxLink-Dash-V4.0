#!/usr/bin/env python3

import gzip
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from services.log_service import (
    read_recent_svxlink_log_lines,
)


class RecentSvxLinkLogTests(unittest.TestCase):

    def test_reads_active_log(self):

        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "svxlink.log"
            log_path.write_text(
                "active-1\nactive-2\n",
                encoding="utf-8",
            )

            with patch(
                "services.log_service.get_svxlink_log_path",
                return_value=log_path,
            ):
                lines = read_recent_svxlink_log_lines(10)

        self.assertEqual(
            lines,
            [
                "active-1",
                "active-2",
            ],
        )

    def test_previous_log_precedes_active_log(self):

        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "svxlink.log"
            previous_path = Path(f"{log_path}.1")

            previous_path.write_text(
                "previous-1\nprevious-2\n",
                encoding="utf-8",
            )
            log_path.write_text(
                "active-1\nactive-2\n",
                encoding="utf-8",
            )

            with patch(
                "services.log_service.get_svxlink_log_path",
                return_value=log_path,
            ):
                lines = read_recent_svxlink_log_lines(3)

        self.assertEqual(
            lines,
            [
                "previous-2",
                "active-1",
                "active-2",
            ],
        )

    def test_reads_compressed_previous_log(self):

        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "svxlink.log"
            previous_path = Path(f"{log_path}.1.gz")

            with gzip.open(
                previous_path,
                mode="wt",
                encoding="utf-8",
            ) as handle:
                handle.write("previous-1\nprevious-2\n")

            log_path.write_text(
                "active-1\n",
                encoding="utf-8",
            )

            with patch(
                "services.log_service.get_svxlink_log_path",
                return_value=log_path,
            ):
                lines = read_recent_svxlink_log_lines(3)

        self.assertEqual(
            lines,
            [
                "previous-1",
                "previous-2",
                "active-1",
            ],
        )


if __name__ == "__main__":
    unittest.main()
