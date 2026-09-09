import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import apt_plan


class AptPlanTests(unittest.TestCase):
    def plan(self, omit=()):
        return "\n".join(f"Inst {name} ({version} MoteBus:stable [amd64])"
                         for name, version in apt_plan.REQUIRED.items() if name not in omit)

    def test_complete_joint_plan_passes_without_claiming_runtime_readiness(self):
        result = apt_plan.audit(self.plan(), "")
        self.assertTrue(result["dependency_plan_valid"])
        self.assertFalse(result["runtime_ready"])
        self.assertEqual(set(result["resolved"]), set(apt_plan.REQUIRED))

    def test_missing_or_historical_agos_fails(self):
        for plan, installed in ((self.plan(("agos",)), ""),
                                (self.plan(("agos",)), "agos\t1.0.0-16\tii \n")):
            with self.subTest(installed=installed), self.assertRaisesRegex(ValueError, "agos"):
                apt_plan.audit(plan, installed)

    def test_all_twenty_one_required_packages_and_added_resources_are_checked(self):
        self.assertEqual(len(apt_plan.REQUIRED), 21)
        self.assertNotIn("ultra-mcp-ssh", apt_plan.REQUIRED)
        self.assertNotIn("model-node", apt_plan.REQUIRED)
        self.assertNotIn("mcp-run", apt_plan.REQUIRED)
        for name in ("uchat", "mote-vault-sync", "mote-vault-syncd", "mote-secd", "codex-mesh", "obsidian", "model-router", "model-llm"):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, name):
                apt_plan.audit(self.plan((name,)), "")
        with self.assertRaisesRegex(ValueError, "cx-agent"):
            apt_plan.audit(self.plan(("cx-agent",)), "cx-node\t0.3.4-1\tii \n")

    def test_old_sync_packages_cannot_substitute_or_expand_removal_permission(self):
        inventory = "mote-sync\t1.1.0-2\tii \nmote-syncd\t1.1.0-2\tii \n"
        with self.assertRaisesRegex(ValueError, "mote-vault-sync"):
            apt_plan.audit(self.plan(("mote-vault-sync", "mote-vault-syncd")), inventory)
        with self.assertRaisesRegex(ValueError, "removals"):
            apt_plan.audit(self.plan() + "\nRemv mote-sync [1.1.0-2]", inventory)

    def test_retirement_does_not_expand_the_removal_exception(self):
        with self.assertRaisesRegex(ValueError, "removals"):
            apt_plan.audit(self.plan() + "\nRemv ultra-mcp-ssh [2.0.0-1]", "ultra-mcp-ssh\t2.0.0-1\tii \n")

    def test_existing_configured_packages_can_satisfy_plan(self):
        inventory = "\n".join(f"{name}:amd64\t{version}\tii " for name, version in apt_plan.REQUIRED.items())
        self.assertTrue(apt_plan.audit("", inventory)["dependency_plan_valid"])
        with self.assertRaisesRegex(ValueError, "missing"):
            apt_plan.audit("", inventory.replace("\tii ", "\tiU "))

    def test_chatd_removal_is_always_rejected_including_configuration_guard(self):
        plan = self.plan() + "\nRemv mote-chatd [2.0.0-4]\n"
        inventory = "mote-chatd\t2.0.0-4\tii \n"
        with self.assertRaisesRegex(ValueError, "removals"):
            apt_plan.audit(plan, inventory)
        with self.assertRaisesRegex(ValueError, "removals"):
            apt_plan.audit(plan, "")
        with self.assertRaisesRegex(ValueError, "removals"):
            apt_plan.audit(plan, "mote-chatd\t2.0.0-6\tii \n")

    def test_exact_guard_may_remain_but_metadata_is_not_payload_verification(self):
        result = apt_plan.audit(self.plan(), "mote-chatd\t2.0.0-6\tii \n")
        self.assertEqual(result["retention_guard_version"], "2.0.0-6")
        self.assertFalse(result["retention_payload_verified"])
        self.assertEqual(len(result["resolved"]), 21)

    def test_native_floors_and_retired_runtime_inventory_are_enforced(self):
        for name, old in (("agent-sphere", "0.1.0-2"), ("medge", "2.0.0-2"),
                          ("moted", "3.5.0-8"), ("mlink", "2.0.0-3"), ("mote-transportd", "2.0.0-5")):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, name):
                apt_plan.audit(self.plan((name,)), f"{name}\t{old}\tii \n")
        for name in apt_plan.RETIRED:
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "retired runtime"):
                apt_plan.audit(self.plan(), f"{name}\t1.0.0-1\tii \n")
        self.assertTrue(apt_plan.audit(self.plan(), "model-node\t0.1.0-2\trc \n")["dependency_plan_valid"])

    def test_old_physical_package_cannot_remain_in_resulting_state(self):
        with self.assertRaisesRegex(ValueError, "old physical"):
            apt_plan.audit(self.plan(), "mote-chatd\t2.0.0-4\tii \n")

    def test_any_other_removal_or_error_is_rejected(self):
        for extra in ("Remv medge [2.0.0-2]", "Remv mote-chatd\nRemv openssh-server",
                      "Purg mote-chatd", "E: Unmet dependencies", "Remv mote-chatd\nRemv mote-chatd"):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                apt_plan.audit(self.plan() + "\n" + extra, "")

    def test_invalid_or_duplicate_plan_records_fail(self):
        for extra in ("Inst agos (1.0.0-16 unknown)", "Inst agos", "Remv "):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                apt_plan.audit(self.plan() + "\n" + extra, "")


if __name__ == "__main__":
    unittest.main()
