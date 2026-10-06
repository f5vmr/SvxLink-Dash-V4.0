#!/usr/bin/env python3

import subprocess


NATIVE_ICS_RX_LINES = {
    "ics_1x": {
        "1": {
            "chip": "gpiochip0",
            "line": 26,
        },
    },
    "ics_2x": {
        "1": {
            "chip": "gpiochip0",
            "line": 26,
        },
        "2": {
            "chip": "gpiochip0",
            "line": 23,
        },
    },
}


def discover_gpiod_lines(required_line_names):
    """
    Discover which gpiochip currently owns each named GPIO line.

    required_line_names:
        iterable of stable gpio-line-names, for example:
        ["RX_1", "TX_1", "PCM_PDWN"]

    Returns:
        {
            "RX_1": {
                "chip": "gpiochip3",
                "line": "RX_1",
                "offset": 6,
            },
            ...
        }
    """

    required = set(required_line_names)
    discovered = {}

    result = subprocess.run(
        ["gpioinfo"],
        text=True,
        capture_output=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "gpioinfo failed: "
            + (result.stderr.strip() or result.stdout.strip())
        )

    current_chip = None

    for raw_line in result.stdout.splitlines():
        line = raw_line.strip()

        if line.startswith("gpiochip"):
            current_chip = line.split()[0].rstrip(":")
            continue

        if not current_chip:
            continue

        # Example:
        # line   6:       "RX_1"    "SvxLink"   input  active-high [used]
        if not line.startswith("line "):
            continue

        before_colon, after_colon = line.split(":", 1)
        parts = before_colon.split()

        if len(parts) < 2:
            continue

        try:
            offset = int(parts[1])
        except ValueError:
            continue

        for name in list(required):
            if f'"{name}"' in after_colon:
                discovered[name] = {
                    "chip": current_chip,
                    "line": name,
                    "offset": offset,
                }
                required.remove(name)
                break

    return discovered


def required_ics_line_names(model):
    """
    Build the named GPIO lines required by the selected ICS profile.

    ICS 1X and 2X receive COS from fixed native Raspberry Pi GPIO
    lines, so only their MCP23017 TX lines require named discovery.
    ICS 4X and 8X expose both RX and TX through named GPIO lines.
    """

    hardware = model.get("hardware", {})
    profile_id = (
        model.get("hardware_profile_id")
        or hardware.get("profile_id")
        or hardware.get("id")
    )

    enabled_ports = model.get("ports", {}).get("enabled", [])

    line_names = []

    for port in enabled_ports:
        port_id = str(port)

        if profile_id not in NATIVE_ICS_RX_LINES:
            line_names.append(f"RX_{port_id}")

        line_names.append(f"TX_{port_id}")

    if profile_id in ("ics_4x", "ics_8x"):
        line_names.append("PCM_PDWN")

    return line_names


def update_model_gpiod_discovery(model):
    """
    Discover and store GPIOD chip/line mappings in node_model data.
    """

    hardware = model.get("hardware", {})
    profile_id = (
        model.get("hardware_profile_id")
        or hardware.get("profile_id")
        or hardware.get("id")
    )

    native_rx_lines = NATIVE_ICS_RX_LINES.get(
        profile_id,
        {},
    )

    line_names = required_ics_line_names(model)
    discovered = discover_gpiod_lines(line_names)

    missing = [
        name
        for name in line_names
        if name not in discovered
    ]

    model.setdefault("gpiod", {})
    model["gpiod"]["resolved_lines"] = discovered
    model["gpiod"]["missing_lines"] = missing

    nodes = model.get("nodes", {})

    for port in model.get("ports", {}).get("enabled", []):
        port_id = str(port)
        node = nodes.get(port_id, {})

        rx_name = f"RX_{port_id}"
        tx_name = f"TX_{port_id}"

        rx = (
            native_rx_lines.get(port_id)
            or discovered.get(rx_name, {})
        )
        tx = discovered.get(tx_name, {})

        node.setdefault("gpio", {})
        node["gpio"]["cos_chip"] = rx.get("chip", "")
        node["gpio"]["cos_line"] = rx.get("line", rx_name)

        if "offset" in rx:
            node["gpio"]["cos_offset"] = rx["offset"]
        else:
            node["gpio"].pop("cos_offset", None)

        node["gpio"]["ptt_chip"] = tx.get("chip", "")
        node["gpio"]["ptt_line"] = tx.get("line", tx_name)
        node["gpio"]["ptt_offset"] = tx.get("offset")

        nodes[port_id] = node

    model["nodes"] = nodes

    return model