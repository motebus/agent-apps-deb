#!/usr/bin/env python3
"""Read-only four-package resolution audit; incomplete native versions block it."""
import argparse
import json
from pathlib import Path
import re
import subprocess
from package import DEPENDENCIES

CORE={'sphered':'4.1.0-2','moted':'3.6.0-2','mote-proxy':'2.0.0-5','mote-transportd':'2.0.0-6',
      'mlink':'2.1.0-1','mote-secd':'1.0.0-2','agos':'2.0.0-2','model-router':'0.1.0-1',
      'model-llm':'0.1.0-3','cx-agent':'0.3.4-3','mote-mcpd':'3.0.0-3','codex-mesh':'1.0.0-2'}
ULTRA={'redixs':None,'comm':None,'obsidian':'1.13.7','mote-vault-sync':'1.1.0-3','mote-vault-syncd':'1.1.0-3'}
REQUIRED={'agent-sphere':'0.2.0-1','agent-ultra':'0.1.0-1','sphere-manager':'0.1.0-1',
          'agent-apps':'0.2.0-1','medge':'3.1.0-1',**CORE,**ULTRA,**DEPENDENCIES}
RETIRED={'mote-bridge-mcp','mote-sync','mote-syncd','cx-node','model-node','model-grid','mcp-run','ultra-mcp-ssh','agent-app'}


def audit(plan,inventory):
    unresolved=sorted(name for name,version in REQUIRED.items() if version is None)
    if unresolved:raise ValueError('native package versions and artifacts are unresolved: '+', '.join(unresolved))
    state={}
    for line in inventory.splitlines():
        fields=line.split('\t')
        if len(fields)!=3:raise ValueError('malformed package inventory')
        name=fields[0].split(':')[0]
        if fields[2].strip()=='ii':
            if name in state:raise ValueError('ambiguous package inventory')
            state[name]=fields[1]
    planned=set()
    for line in plan.splitlines():
        if line.startswith(('Remv ','Purg ','E:')):raise ValueError('removal, purge or APT error requires separate reviewed handling')
        if line.startswith('Inst '):
            match=re.match(r'Inst ([a-z0-9+.-]+)(?::[a-z0-9-]+)?(?: \[[^]]+\])? \(([^\s)]+)',line)
            if not match or match[1] in planned:raise ValueError('invalid or duplicate APT installation record')
            planned.add(match[1]);state[match[1]]=match[2]
    if RETIRED.intersection(state):raise ValueError('active retired package remains in the resulting state')
    if 'mote-chatd' in state and state['mote-chatd']!='2.0.0-6':raise ValueError('unreviewed transport retention record')
    for name,version in REQUIRED.items():
        if name not in state or subprocess.run(['dpkg','--compare-versions',state[name],'ge',version]).returncode:
            raise ValueError('required package floor is missing: '+name)
    return {'dependency_plan_valid':True,'runtime_ready':False,'resolved':{n:state[n] for n in REQUIRED}}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('plan',type=Path);parser.add_argument('inventory',type=Path);args=parser.parse_args()
    print(json.dumps(audit(args.plan.read_text(),args.inventory.read_text()),indent=2,sort_keys=True))
