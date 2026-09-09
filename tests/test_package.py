import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("package", ROOT / "scripts/package.py")
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.environment = mock.patch.dict(os.environ, {"SOURCE_DATE_EPOCH": "1788901200"})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        (ROOT / "build").mkdir(exist_ok=True)

    def test_reproducible_documentation_only_build(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmp:
            first = package.build(Path(tmp) / "first")
            second = package.build(Path(tmp) / "second")
            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_legacy_agos_is_rejected_and_missing_runtime_is_explicit(self):
        report = package.compatibility()
        self.assertFalse(report["installable"])
        self.assertFalse(report["readiness"])
        self.assertEqual(report["missing_dependencies"][0]["name"], "agos")

    def test_final_package_boundary_without_suggested_retired_runtimes(self):
        expected = {"agos": "2.0.0-2", "ss-webos": "2.0.0-11", "mdesk": "3.0.0-6",
                    "mote-bridge-mcp": "3.0.0-2", "cx-agent": "0.3.4-2", "uchat": "2.0.0-3",
                    "mote-vault-sync": "1.1.0-3", "mote-vault-syncd": "1.1.0-3", "mote-secd": "1.0.0-2",
                    "codex-mesh": "1.0.0-1", "obsidian": "1.13.7", "model-router": "0.1.0-1", "model-llm": "0.1.0-3"}
        self.assertEqual(package.DEPENDENCIES, expected)
        report = package.compatibility()
        self.assertEqual(report["dependencies"], expected)
        self.assertEqual(report["suggests"], [])
        self.assertNotIn("Suggests", package.control())
        self.assertEqual(report["version"], "0.1.0-2")
        self.assertEqual({item["name"] for item in report["missing_dependencies"]}, {"agos", "model-router", "model-llm", "cx-agent", "mote-vault-sync", "mote-vault-syncd", "obsidian"})
        self.assertEqual(report["retired_dependencies"], ["ultra-mcp-ssh", "mcp-run", "model-node"])
        self.assertNotIn("on_demand_only", report)
        self.assertEqual(report["agos_resource_dependencies"], {"model-router": "0.1.0-1", "model-llm": "0.1.0-3"})
        self.assertTrue(set(report["agos_resource_dependencies"]).issubset(report["dependencies"]))
        self.assertNotIn("model-grid", report["dependencies"])

    def test_retired_ultra_mcp_ssh_cannot_reenter_composition(self):
        for depends in [package.control()["Depends"] + ", ultra-mcp-ssh (>= 2.0.0-1)",
                        package.control()["Depends"].replace("mote-vault-syncd (>= 1.1.0-3)", "ultra-mcp-ssh (>= 2.0.0-1)")]:
            altered = {**package.control(), "Depends": depends}
            with self.subTest(depends=depends), mock.patch.object(package, "control", return_value=altered):
                with self.assertRaisesRegex(ValueError, "dependency boundary"):
                    package.check_control(altered)

    def test_retired_mcp_run_cannot_become_a_dependency_or_suggestion(self):
        self.assertIn("mcp-run", package.compatibility()["retired_dependencies"])
        for field, value in [("Depends", package.control()["Depends"] + ", mcp-run (>= 2.0.0-1)"),
                             ("Suggests", "model-node, mcp-run")]:
            altered = {**package.control(), field: value}
            with self.subTest(field=field), mock.patch.object(package, "control", return_value=altered):
                with self.assertRaises(ValueError):
                    package.check_control(altered)

    def test_old_sync_names_or_lower_vault_floors_cannot_satisfy_composition(self):
        for new, old in [("mote-vault-sync", "mote-sync"), ("mote-vault-syncd", "mote-syncd")]:
            for replacement in [f"{old} (>= 1.1.0-3)", f"{new} (>= 1.1.0-2)"]:
                altered = package.control()
                altered["Depends"] = altered["Depends"].replace(f"{new} (>= 1.1.0-3)", replacement)
                with self.subTest(replacement=replacement), mock.patch.object(package, "control", return_value=altered):
                    with self.assertRaisesRegex(ValueError, "dependency boundary"):
                        package.check_control(altered)

    def test_retired_model_node_cannot_be_a_dependency_or_suggestion(self):
        self.assertIn("model-node", package.compatibility()["retired_dependencies"])
        for field, value in [("Depends", package.control()["Depends"] + ", model-node (>= 1.0.0-1)"),
                             ("Suggests", "model-node")]:
            altered = {**package.control(), field: value}
            with self.subTest(field=field), mock.patch.object(package, "control", return_value=altered):
                with self.assertRaises(ValueError):
                    package.check_control(altered)

    def test_obsidian_requires_exact_external_provisioning_without_fetch_hooks(self):
        report = package.compatibility()
        provision = report["external_provisioning"]["obsidian"]
        self.assertEqual(provision["version"], "1.13.7")
        self.assertEqual(provision["architecture"], "amd64")
        self.assertEqual(provision["sha256"], "17dc33b49cb3e785ecc27edd2ea0c79e40207798b554fd2886e36ebee7af9ae0")
        self.assertEqual(provision["acquisition_owner"], "agent-computer-top-level-installer")
        self.assertFalse(provision["rehost_on_motebus"])
        self.assertTrue(provision["joint_apt_input_required"])
        altered = package.control()
        altered["Depends"] = altered["Depends"].replace(", obsidian (>= 1.13.7)", "")
        with mock.patch.object(package, "control", return_value=altered):
            with self.assertRaisesRegex(ValueError, "dependency boundary"):
                package.check_control(altered)

    def test_native_cx_floor_cannot_be_lowered_to_historical_runtime(self):
        altered = package.control()
        altered["Depends"] = altered["Depends"].replace("cx-agent (>= 0.3.4-2)", "cx-agent (>= 0.3.4-1)")
        with mock.patch.object(package, "control", return_value=altered):
            with self.assertRaisesRegex(ValueError, "version floor"):
                package.check_control(altered)

    def test_no_cycle_alias_or_fake_provider_is_allowed(self):
        for field, value in (("Depends", package.control()["Depends"] + ", agent-sphere"),
                             ("Provides", "agos"), ("Provides", "agent-app"),
                             ("Suggests", "agos, model-node")):
            with self.subTest(field=field, value=value):
                altered = {**package.control(), field: value}
                with self.assertRaises(ValueError):
                    package.check_control(altered)

    def test_reviewed_control_cannot_lower_agos_floor(self):
        altered = package.control()
        altered["Depends"] = altered["Depends"].replace("agos (>= 2.0.0-2)", "agos (>= 1.0.0-16)")
        with mock.patch.object(package, "control", return_value=altered):
            with self.assertRaisesRegex(ValueError, "version floor"):
                package.check_control(altered)

    def test_hooks_and_runtime_payload_are_rejected(self):
        for extra in ("DEBIAN/postinst", "usr/bin/agos", "etc/agent-apps.conf",
                      "usr/lib/systemd/system/agent-apps.service"):
            with self.subTest(extra=extra), tempfile.TemporaryDirectory(dir=ROOT / "build") as tmp:
                original = package.build(Path(tmp) / "base")
                stage = Path(tmp) / "stage"
                subprocess.run(["dpkg-deb", "--raw-extract", str(original), str(stage)], check=True)
                target = stage / extra
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("#!/bin/sh\nexit 0\n")
                target.chmod(0o755)
                artifact = Path(tmp) / "bad.deb"
                subprocess.run(["dpkg-deb", "--build", "--root-owner-group", str(stage), str(artifact)], check=True)
                with self.assertRaises(ValueError):
                    package.verify(artifact)


if __name__ == "__main__":
    unittest.main()
