#!/usr/bin/env python3
"""Build and audit the documentation-only Agent Apps composition package."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0-2"
DEPENDENCIES = {'agos': '2.0.0-2',
 'ss-webos': '2.0.0-11',
 'mdesk': '3.0.0-6',
 'mote-bridge-mcp': '3.0.0-2',
 'cx-agent': '0.3.4-2',
 'uchat': '2.0.0-3',
 'mote-vault-sync': '1.1.0-3',
 'mote-vault-syncd': '1.1.0-3',
 'mote-secd': '1.0.0-2',
 'codex-mesh': '1.0.0-1',
 'obsidian': '1.13.7',
 'model-router': '0.1.0-1',
 'model-llm': '0.1.0-3'}
AGOS_RESOURCE_DEPENDENCIES = {'model-router': '0.1.0-1', 'model-llm': '0.1.0-3'}
PUBLIC_RELEASE_GATES = [{'name': 'agos',
  'minimum_version': '2.0.0-2',
  'status': 'compatible-public-release-unverified',
  'rejected_historical_version': '1.0.0-16'},
 {'name': 'cx-agent',
  'minimum_version': '0.3.4-2',
  'status': 'compatible-public-release-unverified',
  'replaces_package': 'cx-node',
  'rejected_historical_version': '0.3.4-1'},
 {'name': 'mote-vault-sync',
  'minimum_version': '1.1.0-3',
  'status': 'compatible-public-release-unverified',
  'replaces_package': 'mote-sync',
  'rejected_historical_version': '1.1.0-2'},
 {'name': 'mote-vault-syncd',
  'minimum_version': '1.1.0-3',
  'status': 'compatible-public-release-unverified',
  'replaces_package': 'mote-syncd',
  'rejected_historical_version': '1.1.0-2'},
 {'name': 'model-router',
  'minimum_version': '0.1.0-1',
  'status': 'compatible-public-release-unverified'},
 {'name': 'model-llm',
  'minimum_version': '0.1.0-3',
  'status': 'compatible-public-release-unverified'}]
RENAMED_DEPENDENCIES = {'mote-sync': 'mote-vault-sync', 'mote-syncd': 'mote-vault-syncd', 'cx-node': 'cx-agent'}
EXTERNAL_PROVISIONING_GATE = {'name': 'obsidian', 'minimum_version': '1.13.7', 'status': 'external-upstream-provisioning-required'}
EXTERNAL_PROVISIONING = {'obsidian': {'source': 'official-upstream-deb',
              'version': '1.13.7',
              'architecture': 'amd64',
              'sha256': '17dc33b49cb3e785ecc27edd2ea0c79e40207798b554fd2886e36ebee7af9ae0',
              'acquisition_owner': 'agent-computer-top-level-installer',
              'rehost_on_motebus': False,
              'joint_apt_input_required': True}}
DOC = "usr/share/doc/agent-apps/"
PAYLOAD = {DOC + "README.md", DOC + "copyright"}


def git(*args):
    top = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "--show-toplevel"], text=True).strip()
    if Path(top).resolve() != ROOT:
        raise ValueError("source provenance requires this package's own Git repository")
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def fields(text):
    result = {}
    key = None
    for line in text.splitlines():
        if line.startswith(" ") and key:
            result[key] += "\n" + line
        elif line:
            key, value = line.split(":", 1)
            if key in result:
                raise ValueError("duplicate control field: " + key)
            result[key] = value.strip()
    return result


def control():
    return fields((ROOT / "packaging/control").read_text())


def check_control(meta):
    if meta != control():
        raise ValueError("package metadata differs from reviewed control")
    if meta["Package"] != "agent-apps" or meta["Architecture"] != "all" or meta["Version"] != VERSION:
        raise ValueError("wrong package identity")
    if set(meta) != {"Package", "Version", "Architecture", "Section", "Priority",
                    "Maintainer", "Homepage", "Depends", "Description"}:
        raise ValueError("unexpected control fields")
    deps = meta["Depends"].split(",")
    matches = [re.fullmatch(r"([a-z][a-z0-9-]*) \(>= ([0-9][0-9A-Za-z.+:~\-]*)\)", d.strip()) for d in deps]
    if len(deps) != 13 or not all(matches) or {m[1]: m[2] for m in matches} != DEPENDENCIES:
        raise ValueError("dependency boundary or version floor violation")


def compatibility():
    check_control(control())
    contract = json.loads((ROOT / "dependency-contract.json").read_text())
    if contract["version"] != VERSION or contract["dependencies"] != DEPENDENCIES or contract["suggests"] != []:
        raise ValueError("dependency contract differs from control")
    if contract.get("on_demand_only"):
        raise ValueError("retired packages must not be advertised as active on-demand dependencies")
    if contract["retired_dependencies"] != ["ultra-mcp-ssh", "mcp-run", "model-node"]:
        raise ValueError("retired ultra-mcp-ssh, mcp-run, and model-node must remain excluded")
    if contract["renamed_dependencies"] != RENAMED_DEPENDENCIES:
        raise ValueError("vault package rename mapping differs from the reviewed contract")
    if contract["installable"] is not False or contract["readiness"] is not False:
        raise ValueError("installation and runtime acceptance have not been established")
    if contract["agos_resource_dependencies"] != AGOS_RESOURCE_DEPENDENCIES:
        raise ValueError("AGOS Router/LLM resource dependency contract differs")
    if contract["external_provisioning"] != EXTERNAL_PROVISIONING:
        raise ValueError("Obsidian must use the exact reviewed external upstream artifact")
    if contract["missing_dependencies"] != PUBLIC_RELEASE_GATES + [EXTERNAL_PROVISIONING_GATE]:
        raise ValueError("native AGOS, CX Agent, Router/LLM, vault-sync, and external Obsidian installation gates must remain explicit")
    for gate in PUBLIC_RELEASE_GATES:
        if "rejected_historical_version" not in gate:
            continue
        if subprocess.run(["dpkg", "--compare-versions", gate["rejected_historical_version"],
                           "ge", DEPENDENCIES[gate["name"]]]).returncode != 1:
            raise ValueError("historical component must not satisfy " + gate["name"] + " requirement")
    return contract


def archive(path, flag):
    return tarfile.open(fileobj=io.BytesIO(subprocess.check_output(["dpkg-deb", flag, str(path)])))


def verify(path):
    with archive(path, "--ctrl-tarfile") as arc:
        files = [m for m in arc if not m.isdir()]
        if len(files) != 1 or files[0].name.removeprefix("./") != "control" or not files[0].isfile():
            raise ValueError("control archive must contain only control; hooks are forbidden")
        check_control(fields(arc.extractfile(files[0]).read().decode()))
    with archive(path, "--fsys-tarfile") as arc:
        files = set()
        allowed_dirs = {"", "usr", "usr/share", "usr/share/doc", "usr/share/doc/agent-apps"}
        for member in arc:
            name = member.name.removeprefix("./").rstrip("/")
            name = "" if name == "." else name
            if member.uid != 0 or member.gid != 0:
                raise ValueError("archive member is not root-owned")
            if member.isdir():
                if name not in allowed_dirs or member.mode != 0o755:
                    raise ValueError("unexpected directory or permission: " + name)
            else:
                if not member.isfile() or name not in PAYLOAD or member.mode != 0o644 or name in files:
                    raise ValueError("unexpected payload or permission: " + name)
                source = ROOT / ("README.md" if name.endswith("README.md") else "packaging/copyright")
                if arc.extractfile(member).read() != source.read_bytes():
                    raise ValueError("documentation bytes differ: " + name)
                files.add(name)
        if files != PAYLOAD:
            raise ValueError("incomplete documentation payload")


def build(out):
    meta = control()
    check_control(meta)
    out.mkdir(parents=True, exist_ok=True)
    (ROOT / "build").mkdir(exist_ok=True)
    epoch = int(os.environ.get("SOURCE_DATE_EPOCH") or git("log", "-1", "--format=%ct"))
    with tempfile.TemporaryDirectory(prefix="agent-apps-", dir=ROOT / "build") as tmp:
        stage = Path(tmp) / "root"
        (stage / "DEBIAN").mkdir(parents=True)
        docs = stage / DOC
        docs.mkdir(parents=True)
        shutil.copyfile(ROOT / "packaging/control", stage / "DEBIAN/control")
        shutil.copyfile(ROOT / "README.md", docs / "README.md")
        shutil.copyfile(ROOT / "packaging/copyright", docs / "copyright")
        for path in [stage, *stage.rglob("*")]:
            path.chmod(0o755 if path.is_dir() else 0o644)
            os.utime(path, (epoch, epoch))
        result = out / ("agent-apps_" + meta["Version"] + "_all.deb")
        subprocess.run(["dpkg-deb", "--build", "--root-owner-group", "-Zxz", "-z9",
                        str(stage), str(result)], check=True,
                       env={**os.environ, "SOURCE_DATE_EPOCH": str(epoch)})
    verify(result)
    return result


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(out):
    """Bind a local review artifact; this is not a publication or readiness gate."""
    contract = compatibility()
    path = out / ("agent-apps_" + control()["Version"] + "_all.deb")
    verify(path)
    if git("status", "--porcelain"):
        raise ValueError("manifest requires clean committed source")
    commit = git("rev-parse", "HEAD")
    data = {"schema": "agent-apps-release/v1", "package": "agent-apps", "version": control()["Version"],
            "architecture": "all", "status": "unpublished-composition-review", "installable": False,
            "readiness": False, "missing_dependencies": contract["missing_dependencies"],
            "source": "https://github.com/motebus/agent-apps-deb", "source_commit": commit,
            "asset": path.name, "sha256": digest(path), "dependency_contract": contract}
    record = out / "release-manifest.json"
    record.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    (out / "SHA256SUMS").write_text("".join(digest(p) + "  " + p.name + "\n" for p in (path, record)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["build", "verify", "compatibility", "manifest"])
    parser.add_argument("path", nargs="?", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    if args.action == "build":
        print(build(args.path.resolve()))
    elif args.action == "verify":
        verify(args.path.resolve())
        print("Package boundary audit passed")
    elif args.action == "compatibility":
        print(json.dumps(compatibility(), indent=2))
    else:
        manifest(args.path.resolve())
