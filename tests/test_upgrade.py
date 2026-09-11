"""Real APT simulation from installed Apps/uChat 2.x; no host package changes."""
import json
import os
from pathlib import Path
import pwd
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class UpgradeTest(unittest.TestCase):
    def plan(self, missing_daemon=False):
        contract = json.loads((ROOT / 'dependency-contract.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, etc = root / 'repo', root / 'etc'
            repo.mkdir(); etc.mkdir()
            for name in ('apt.conf.d', 'sources.list.d', 'preferences.d', 'trusted.gpg.d'):
                (etc / name).mkdir()
            (etc / 'sources.list').write_text(f'deb [trusted=yes] file:{repo} ./\n')
            config = root / 'apt.conf'; config.write_text(f'Dir::Etc "{etc}";\n')
            def record(name, version, depends=''):
                return (f'Package: {name}\nVersion: {version}\nArchitecture: all\n'
                        'Maintainer: Fixture <fixture@example.invalid>\nDescription: Offline fixture\n'
                        + (f'Depends: {depends}\n' if depends else ''))
            old_depends = ', '.join(f'{name} (>= {"2.0.0-3" if name == "uchat" else version})'
                                    for name, version in contract['dependencies'].items())
            installed = [record(name, '2.0.0-3' if name == 'uchat' else version)
                         for name, version in contract['dependencies'].items()]
            installed.append(record('agent-apps', '0.2.0-1', old_depends))
            status = root / 'status'
            status.write_text('\n'.join(item + 'Status: install ok installed\n' for item in installed))
            before = status.read_bytes()
            controls = [(ROOT / 'packaging/control').read_text(),
                        record('uchat', '3.0.0-1', 'uchatd (>= 0.1.0-1)'),
                        record('redis-server', '5:7.0.0')]
            if not missing_daemon:
                controls.append(record('uchatd', '0.1.0-1', 'redis-server (>= 5:6.2)'))
            # Synthetic metadata archives supply valid downloadable APT records.
            index = []
            for number, control in enumerate(controls):
                stage = root / str(number) / 'DEBIAN'; stage.mkdir(parents=True)
                (stage / 'control').write_text(control)
                deb = repo / f'fixture-{number}.deb'
                subprocess.run(['dpkg-deb', '--build', str(stage.parent), str(deb)],
                               check=True, capture_output=True)
                index.append(control + f'Filename: ./{deb.name}\nSize: {deb.stat().st_size}\n')
            (repo / 'Packages').write_text('\n'.join(index))
            for name in ('state/lists/partial', 'cache/archives/partial', 'log'):
                (root / name).mkdir(parents=True)
            command = ['apt-get', '-o', f'Dir::Etc={etc}', '-o', f'Dir::State={root}/state',
                       '-o', f'Dir::State::status={status}', '-o', f'Dir::Cache={root}/cache',
                       '-o', f'Dir::Log={root}/log', '-o', 'APT::Architecture=amd64',
                       '-o', 'Acquire::Languages=none', '-o', 'Dir::Cache::pkgcache=',
                       '-o', 'Dir::Cache::srcpkgcache=',
                       '-o', 'APT::Sandbox::User=' + pwd.getpwuid(os.getuid()).pw_name]
            env = dict(os.environ, LC_ALL='C', APT_CONFIG=str(config))
            subprocess.run(command + ['update'], check=True, capture_output=True, env=env)
            result = subprocess.run(command + ['--simulate', '--no-remove', 'install',
                                               'agent-apps=' + contract['version']],
                                    capture_output=True, text=True, env=env)
            self.assertEqual(status.read_bytes(), before)
            return result

    def test_existing_apps_upgrades_client_and_adds_private_daemon(self):
        result = self.plan()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual({line.split()[1] for line in result.stdout.splitlines() if line.startswith('Inst ')},
                         {'agent-apps', 'uchat', 'uchatd', 'redis-server'})
        self.assertNotIn('Remv ', result.stdout)

    def test_missing_daemon_refuses_incomplete_upgrade(self):
        result = self.plan(missing_daemon=True)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
