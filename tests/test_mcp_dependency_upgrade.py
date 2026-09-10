"""Real offline APT resolution of the MCP rename; metadata fixtures, no DPKG."""
import hashlib
import os
from pathlib import Path
import pwd
import subprocess
import tempfile
import unittest

import test_package
package=test_package.package


class McpDependencyUpgradeTests(unittest.TestCase):
    def plan(self, missing=None):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);repo=root/'repo';repo.mkdir();etc=root/'etc';etc.mkdir()
            for name in ('apt.conf.d','sources.list.d','preferences.d','trusted.gpg.d'):(etc/name).mkdir()
            (etc/'sources.list').write_text(f'deb [trusted=yes] file:{repo} ./\n')
            config=root/'apt.conf';config.write_text(f'Dir::Etc "{etc}";\n')
            def fields(name,version):
                f={'Package':name,'Version':version,'Architecture':'all','Maintainer':'Fixture <fixture@example.invalid>',
                   'Description':'Offline dependency metadata fixture'}
                if name=='agent-apps':
                    f['Depends']=package.control()['Depends']
                    if version=='0.1.0-2':f['Depends']=f['Depends'].replace('mote-mcpd (>= 3.0.0-3)','mote-bridge-mcp (>= 3.0.0-2)').replace('cx-agent (>= 0.3.4-3)','cx-agent (>= 0.3.4-2)').replace('codex-mesh (>= 1.0.0-2)','codex-mesh (>= 1.0.0-1)')
                if name=='cx-agent':f['Depends']='mote-bridge-mcp' if version=='0.3.4-2' else 'mote-mcpd (>= 3.0.0-3)'
                if name=='codex-mesh':f['Depends']='mote-bridge-mcp (>= 2.0.0-1)' if version=='1.0.0-1' else 'mote-mcpd (>= 3.0.0-3)'
                if name=='mote-mcpd':f.update(Conflicts='mote-bridge-mcp',Replaces='mote-bridge-mcp')
                return f
            installed={**package.DEPENDENCIES,'agent-apps':'0.1.0-2','cx-agent':'0.3.4-2','codex-mesh':'1.0.0-1','mote-bridge-mcp':'3.0.0-2'}
            installed.pop('mote-mcpd')
            status=root/'status';status.write_text('\n\n'.join('\n'.join(f'{k}: {v}' for k,v in dict(fields(n,v),Status='install ok installed').items()) for n,v in installed.items())+'\n')
            before=status.read_bytes();index=[]
            candidates=set(installed.items())|set(package.DEPENDENCIES.items())|{('agent-apps',package.VERSION)}
            for name,version in sorted(candidates):
                if (name,version)==missing:continue
                f=fields(name,version);stage=root/(name+version)/'DEBIAN';stage.mkdir(parents=True)
                (stage/'control').write_text('\n'.join(f'{k}: {v}' for k,v in f.items())+'\n')
                deb=repo/f'{name}_{version}_all.deb'
                subprocess.run(['dpkg-deb','--build','--root-owner-group',str(stage.parent),str(deb)],check=True,capture_output=True)
                f.update(Filename='./'+deb.name,Size=deb.stat().st_size,SHA256=hashlib.sha256(deb.read_bytes()).hexdigest())
                index.append('\n'.join(f'{k}: {v}' for k,v in f.items()))
            (repo/'Packages').write_text('\n\n'.join(index)+'\n')
            for p in ('state/lists/partial','cache/archives/partial','log'):(root/p).mkdir(parents=True)
            command=['apt-get','-o',f'Dir::Etc={etc}','-o',f'Dir::State={root}/state','-o',f'Dir::State::status={status}',
                     '-o',f'Dir::Cache={root}/cache','-o',f'Dir::Log={root}/log','-o','APT::Architecture=amd64',
                     '-o','Acquire::Languages=none','-o','Dir::Cache::pkgcache=','-o','Dir::Cache::srcpkgcache=',
                     '-o','APT::Sandbox::User='+pwd.getpwuid(os.getuid()).pw_name]
            env=dict(os.environ,LC_ALL='C',APT_CONFIG=str(config))
            update=subprocess.run([*command,'update'],env=env,capture_output=True,text=True)
            self.assertEqual(update.returncode,0,update.stderr)
            result=subprocess.run([*command,'--simulate','install','agent-apps='+package.VERSION],env=env,capture_output=True,text=True)
            self.assertEqual(status.read_bytes(),before)
            return result

    def test_rename_forces_both_existing_dependents_to_upgrade(self):
        result=self.plan();self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        installs={line.split()[1] for line in result.stdout.splitlines() if line.startswith('Inst ')}
        removals={line.split()[1] for line in result.stdout.splitlines() if line.startswith('Remv ')}
        self.assertEqual(installs,{'agent-apps','mote-mcpd','cx-agent','codex-mesh'},result.stdout)
        self.assertEqual(removals,{'mote-bridge-mcp'},result.stdout)

    def test_missing_aligned_dependent_prevents_the_rename(self):
        for item in [('cx-agent','0.3.4-3'),('codex-mesh','1.0.0-2')]:
            with self.subTest(item=item):
                result=self.plan(missing=item)
                self.assertNotEqual(result.returncode,0,result.stdout+result.stderr)
