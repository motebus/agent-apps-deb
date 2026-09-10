#!/usr/bin/env python3
"""Audit a C-locale joint APT simulation; never execute or authorize an install."""
import argparse
import json
from pathlib import Path
import re
import subprocess

from package import DEPENDENCIES

REQUIRED = {"agent-sphere": "0.1.0-9", "agent-apps": "0.1.0-3", **DEPENDENCIES,
            "sphered": "4.1.0-2", "moted": "3.6.0-2", "mote-proxy": "2.0.0-5",
            "mote-transportd": "2.0.0-6", "medge": "3.0.0-3", "mlink": "2.1.0-1"}
RETENTION_GUARD_VERSION = "2.0.0-6"
RETIRED = {"ultra-mcp-ssh", "mcp-run", "model-node", "model-grid", "mote-sync", "mote-syncd", "cx-node", "agent-app", "mote-bridge-mcp"}
NAME = r"[a-z0-9][a-z0-9+.-]*(?::[a-z0-9-]+)?"


def audit(plan, inventory):
    installed = {}
    for line in inventory.splitlines():
        parts = line.split("\t")
        if len(parts) != 3 or not re.fullmatch(NAME, parts[0]):
            raise ValueError("inventory requires package, version and dpkg status tab-separated")
        if parts[2].strip() == "ii":
            if parts[0] in installed:
                raise ValueError("duplicate installed package")
            installed[parts[0]] = parts[1]
    installs = {}
    removals = []
    for line in plan.splitlines():
        if line.startswith("E:") or line.startswith("Purg "):
            raise ValueError("APT reported failure or package purge")
        if line.startswith("Inst "):
            match = re.match(rf"Inst ({NAME})(?: \[[^\]]+\])? \(([^\s)]+)(?:[\s)]|$)", line)
            if not match or match[1] in installs:
                raise ValueError("malformed or duplicate APT installation record")
            installs[match[1]] = match[2]
        if line.startswith("Remv "):
            match = re.match(rf"Remv ({NAME})(?:\s|$)", line)
            if not match:
                raise ValueError("malformed APT removal record")
            removals.append(match[1])
    if removals:
        raise ValueError("package removals require a separate reviewed transaction guard; mote-chatd retention must not be removed")
    resulting = {name: version for name, version in installed.items()
                 if name.split(":")[0] not in {item.split(":")[0] for item in removals}}
    for name, version in installs.items():
        # APT may omit the native architecture suffix used by dpkg-query.
        for old in list(resulting):
            if old.split(":")[0] == name.split(":")[0]:
                resulting.pop(old)
        resulting[name] = version
    resolved = {}
    for name, minimum in REQUIRED.items():
        candidates = [version for package, version in resulting.items() if package.split(":")[0] == name]
        if len(candidates) != 1:
            raise ValueError(f"missing or ambiguous required package: {name}")
        version = candidates[0]
        comparison = subprocess.run(["dpkg", "--compare-versions", version, "ge", minimum]).returncode
        if comparison != 0:
            raise ValueError(f"{name} {version} does not satisfy >= {minimum}")
        resolved[name] = version
    guards = [version for name, version in resulting.items() if name.split(":")[0] == "mote-chatd"]
    if guards and guards != [RETENTION_GUARD_VERSION]:
        raise ValueError("old physical mote-chatd is not the exact configuration retention guard")
    if any(name.split(":")[0] in RETIRED for name in resulting):
        raise ValueError("retired runtime remains in the supplied resulting package inventory")
    return {"schema": "agent-computer-apt-plan-review/v1", "dependency_plan_valid": True,
            "runtime_ready": False, "resolved": resolved, "removals": removals,
            "retention_guard_version": guards[0] if guards else None,
            "retention_payload_verified": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("inventory", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.plan.read_text(), args.inventory.read_text()), indent=2, sort_keys=True))
