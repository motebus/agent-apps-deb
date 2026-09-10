import sys
from pathlib import Path
import unittest
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import apt_plan


class FourPackagePlanTests(unittest.TestCase):
    def test_complete_shape_has_twenty_six_unique_packages(self):
        self.assertEqual(len(apt_plan.REQUIRED),26)
        self.assertNotIn('medge',apt_plan.CORE)
        self.assertTrue({'redixs','comm','obsidian'}.issubset(apt_plan.ULTRA))
        self.assertTrue({'agent-sphere','agent-ultra','sphere-manager','agent-apps'}.issubset(apt_plan.REQUIRED))

    def test_incomplete_inventory_cannot_be_declared_resolved(self):
        for plan,inventory in [('', ''),('Inst jujue (99.0 fixture)','')]:
            with self.assertRaisesRegex(ValueError,'required package floor'):apt_plan.audit(plan,inventory)

    def test_reviewed_plan_still_rejects_removal_and_has_no_runtime_claim(self):
        # Synthetic inventory exercises parser policy only, not artifacts
        # or native runtime availability.
        floors={n:(v or '1.0') for n,v in apt_plan.REQUIRED.items()}
        inventory='\n'.join(f'{n}\t{v}\tii ' for n,v in floors.items())
        with mock.patch.object(apt_plan,'REQUIRED',floors):
            self.assertFalse(apt_plan.audit('',inventory)['runtime_ready'])
            for plan in ['Remv mote-bridge-mcp [3.0.0-2]','Purg mote-chatd','E: unresolved']:
                with self.assertRaises(ValueError):apt_plan.audit(plan,inventory)
            with self.assertRaisesRegex(ValueError,'required package'):apt_plan.audit('',inventory.replace('agos\t2.1.0-1','agos\t1.0.0-1'))
