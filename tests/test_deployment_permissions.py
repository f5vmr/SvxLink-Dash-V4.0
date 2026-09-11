#!/usr/bin/env python3

import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from models.node_model import new_node_model
from services import node_info_service
from services.svxlink_service import write_text_file


class DeploymentPermissionTests(unittest.TestCase):

    def test_generated_text_file_uses_managed_mode(self):

        with tempfile.TemporaryDirectory() as directory:
            target = (
                Path(directory)
                / "svxlink.d"
                / "ModuleEchoLink.conf"
            )

            write_text_file(
                target,
                "NAME=EchoLink\n",
            )

            mode = target.stat().st_mode & 0o777

        self.assertEqual(mode, 0o664)

    def test_node_info_json_uses_managed_mode(self):

        model = new_node_model()

        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "node_info.json"

            with patch.object(
                node_info_service,
                "NODE_INFO_FILE",
                target,
            ):
                written = (
                    node_info_service.write_node_info_json(
                        model
                    )
                )

            mode = target.stat().st_mode & 0o777

        self.assertEqual(written, target)
        self.assertEqual(mode, 0o664)


if __name__ == "__main__":
    unittest.main()
