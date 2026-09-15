#!/usr/bin/env python3

import unittest
from unittest.mock import patch

from renderers import svxlink_renderer


class LibraryPathTests(unittest.TestCase):

    def test_supported_architecture_library_paths(self):
        cases = (
            (
                "armv7l",
                "/usr/lib/arm-linux-gnueabihf/svxlink",
            ),
            (
                "armhf",
                "/usr/lib/arm-linux-gnueabihf/svxlink",
            ),
            (
                "aarch64",
                "/usr/lib/aarch64-linux-gnu/svxlink",
            ),
            (
                "arm64",
                "/usr/lib/aarch64-linux-gnu/svxlink",
            ),
            (
                "x86_64",
                "/usr/lib/x86_64-linux-gnu/svxlink",
            ),
            (
                "amd64",
                "/usr/lib/x86_64-linux-gnu/svxlink",
            ),
            (
                "i386",
                "/usr/lib/i386-linux-gnu/svxlink",
            ),
            (
                "i486",
                "/usr/lib/i386-linux-gnu/svxlink",
            ),
            (
                "i586",
                "/usr/lib/i386-linux-gnu/svxlink",
            ),
            (
                "i686",
                "/usr/lib/i386-linux-gnu/svxlink",
            ),
            (
                "x86",
                "/usr/lib/i386-linux-gnu/svxlink",
            ),
        )

        for machine, expected in cases:
            with self.subTest(machine=machine):
                with patch.object(
                    svxlink_renderer.platform,
                    "machine",
                    return_value=machine,
                ):
                    self.assertEqual(
                        svxlink_renderer.get_library_path(),
                        expected,
                    )

    def test_unknown_architecture_uses_fallback(self):
        with patch.object(
            svxlink_renderer.platform,
            "machine",
            return_value="unknown-cpu",
        ):
            self.assertEqual(
                svxlink_renderer.get_library_path(),
                "/usr/lib/svxlink",
            )


if __name__ == "__main__":
    unittest.main()
