#!/usr/bin/env python3

"""
SvxLink log path resolver.

Determines the active SvxLink log file from /etc/default/svxlink.
"""

from pathlib import Path
import shlex
import gzip


DEFAULT_FILE = Path("/etc/default/svxlink")

PREFERRED_LOG = Path("/var/log/svxlink.log")
LEGACY_LOG = Path("/var/log/svxlink")


def get_svxlink_log_path():
    """
    Determine active SvxLink log path.

    Preferred source:
    - LOGFILE from /etc/default/svxlink

    Fallback:
    - /var/log/svxlink.log
    - /var/log/svxlink
    """

    if DEFAULT_FILE.exists():

        try:
            for line in DEFAULT_FILE.read_text(
                encoding="utf-8",
                errors="ignore",
            ).splitlines():

                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                if line.startswith("LOGFILE="):

                    value = line.split("=", 1)[1].strip()

                    if value:
                        value = shlex.split(value)[0]
                        return Path(value)

        except Exception:
            pass

    if PREFERRED_LOG.exists():
        return PREFERRED_LOG

    return LEGACY_LOG

def read_recent_svxlink_log_lines(max_lines=300):

    """
    Return a bounded chronological view across the most recent
    SvxLink log rotation.

    The immediately previous log is read before the active log so
    runtime state remains coherent when rotation occurs.
    """

    if max_lines <= 0:
        return []

    log_path = get_svxlink_log_path()

    previous_path = Path(f"{log_path}.1")
    compressed_previous_path = Path(f"{log_path}.1.gz")

    lines = []

    try:
        if previous_path.exists():
            lines.extend(
                previous_path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                ).splitlines()[-max_lines:]
            )
        elif compressed_previous_path.exists():
            with gzip.open(
                compressed_previous_path,
                mode="rt",
                encoding="utf-8",
                errors="ignore",
            ) as handle:
                lines.extend(
                    handle.read().splitlines()[-max_lines:]
                )
    except Exception:
        pass

    try:
        if log_path.exists():
            lines.extend(
                log_path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                ).splitlines()[-max_lines:]
            )
    except Exception:
        pass

    return lines[-max_lines:]
