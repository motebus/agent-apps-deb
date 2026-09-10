import sys
from pathlib import Path
import unittest
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import apt_plan


class FourPackagePlanTests(unittest.TestCase):
    def test_complete_shape_has_twenty_seven_unique_packages(self):
        self.assertEqual(len(apt_plan.REQUIRED),27)
        self.assertNotIn('medge',apt_plan.CORE)
        self.assertTrue({'redixs','comm','obsidian'}.issubset(apt_plan.ULTRA))
        self.assertTrue({'agent-sphere','agent-ultra','sphere-manager','agent-apps'}.issubset(apt_plan.REQUIRED))

    def test_unbuilt_native_names_cannot_be_declared_installable(self):
        for plan,inventory in [('', ''),('Inst jujue (99.0 fixture)','')]:
            with self.assertRaisesRegex(ValueError,'comm, iagent, jujue, redixs'):apt_plan.audit(plan,inventory)

    def test_reviewed_plan_still_rejects_removal_and_has_no_runtime_claim(self):
        # Synthetic resolved versions exercise parser policy only. They are
        # never written into the production unresolved release contract.
        floors={n:(v or '1.0') for n,v in apt_plan.REQUIRED.items()}
        inventory='\n'.join(f'{n}\t{v}\tii ' for n,v in floors.items())
        with mock.patch.object(apt_plan,'REQUIRED',floors):
            self.assertFalse(apt_plan.audit('',inventory)['runtime_ready'])
            for plan in ['Remv mote-bridge-mcp [3.0.0-2]','Purg mote-chatd','E: unresolved']:
                with self.assertRaises(ValueError):apt_plan.audit(plan,inventory)
            with self.assertRaisesRegex(ValueError,'required package'):apt_plan.audit('',inventory.replace('agos\t2.0.0-2','agos\t1.0.0-1'))
