#!/usr/bin/env python3
"""Build native documentation-only AGPC Apps and its legacy-name transition."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = 'agpc-apps'
LEGACY = 'agent-apps'
VERSION = '0.3.0-1'
DEPENDENCIES = {'jujue': '0.2.0-1', 'iagent': '1.0.0-1', 'ss-webos': '2.0.0-12',
                'mdesk': '3.0.0-6', 'uchat': '3.2.0-4', 'agent-sphere': '0.3.0-1',
                'agent-ultra': '0.1.0-1'}


def git(*args):
    top = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', '--show-toplevel'], text=True).strip()
    if Path(top).resolve() != ROOT:
        raise ValueError("source provenance requires this package's own Git repository")
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()


def fields(text):
    result = {}
    key = None
    for line in text.splitlines():
        if line.startswith(' ') and key:
            result[key] += '\n' + line
        elif line:
            key, value = line.split(':', 1)
            if key in result:
                raise ValueError('duplicate control field: ' + key)
            result[key] = value.strip()
    return result


def control_path(name=PACKAGE):
    if name not in (PACKAGE, LEGACY):
        raise ValueError('unknown package')
    return ROOT / 'packaging' / ('control' if name == PACKAGE else 'agent-apps.control')


def control(name=PACKAGE):
    return fields(control_path(name).read_text())


def check_control(meta):
    name = meta.get('Package')
    if meta != control(name):
        raise ValueError('package metadata differs from reviewed control')
    if meta['Architecture'] != 'all' or meta['Version'] != VERSION:
        raise ValueError('wrong package identity')
    if set(meta) != {'Package', 'Version', 'Architecture', 'Section', 'Priority',
                    'Maintainer', 'Homepage', 'Depends', 'Description'}:
        raise ValueError('unexpected control fields')
    if name == PACKAGE:
        expected_depends = ', '.join(f'{dependency} (>= {version})' for dependency, version in DEPENDENCIES.items())
    else:
        expected_depends = f'{PACKAGE} (= {VERSION})'
    if meta['Depends'] != expected_depends:
        raise ValueError('dependency boundary or version floor violation')


def compatibility():
    check_control(control())
    check_control(control(LEGACY))
    contract = json.loads((ROOT / 'dependency-contract.json').read_text())
    if (contract['schema'] != 'agpc-apps-dependency-contract/v1' or contract['version'] != VERSION
            or contract['dependencies'] != DEPENDENCIES or contract['package'] != PACKAGE
            or contract['recommends'] or contract['suggests']):
        raise ValueError('application dependency contract differs from control')
    if contract['transition'] != {'package': LEGACY, 'version': VERSION,
                                  'depends': f'{PACKAGE} (= {VERSION})', 'removal_required': False}:
        raise ValueError('legacy-name migration contract differs from control')
    unresolved = {name for name, version in DEPENDENCIES.items() if version is None}
    if set(contract['native_release_gates']) != unresolved:
        raise ValueError('unbuilt native application dependencies must remain explicit')
    if contract['installable'] is not False or contract['readiness'] is not False:
        raise ValueError('composition metadata cannot establish installation or runtime readiness')
    if set(DEPENDENCIES) != {'jujue', 'iagent', 'ss-webos', 'mdesk', 'uchat', 'agent-sphere', 'agent-ultra'}:
        raise ValueError('wrong application ownership boundary')
    return contract


def archive(path, flag):
    return tarfile.open(fileobj=io.BytesIO(subprocess.check_output(['dpkg-deb', flag, str(path)])))


def verify(path):
    with archive(path, '--ctrl-tarfile') as arc:
        files = [m for m in arc if not m.isdir()]
        if len(files) != 1 or files[0].name.removeprefix('./') != 'control' or not files[0].isfile():
            raise ValueError('control archive must contain only control; hooks are forbidden')
        meta = fields(arc.extractfile(files[0]).read().decode())
        check_control(meta)
    doc = 'usr/share/doc/' + meta['Package']
    payload = {doc + '/README.md', doc + '/copyright'}
    with archive(path, '--fsys-tarfile') as arc:
        files = set()
        allowed_dirs = {'', 'usr', 'usr/share', 'usr/share/doc', doc}
        for member in arc:
            name = member.name.removeprefix('./').rstrip('/')
            name = '' if name == '.' else name
            if member.uid != 0 or member.gid != 0:
                raise ValueError('archive member is not root-owned')
            if member.isdir():
                if name not in allowed_dirs or member.mode != 0o755:
                    raise ValueError('unexpected directory or permission: ' + name)
            else:
                if not member.isfile() or name not in payload or member.mode != 0o644 or name in files:
                    raise ValueError('unexpected payload or permission: ' + name)
                source = ROOT / ('README.md' if name.endswith('README.md') else 'packaging/copyright')
                if arc.extractfile(member).read() != source.read_bytes():
                    raise ValueError('documentation bytes differ: ' + name)
                files.add(name)
        if files != payload:
            raise ValueError('incomplete documentation payload')


def build(out, name=PACKAGE):
    meta = control(name)
    check_control(meta)
    out.mkdir(parents=True, exist_ok=True)
    (ROOT / 'build').mkdir(exist_ok=True)
    epoch = int(os.environ.get('SOURCE_DATE_EPOCH') or git('log', '-1', '--format=%ct'))
    with tempfile.TemporaryDirectory(prefix=name + '-', dir=ROOT / 'build') as tmp:
        stage = Path(tmp) / 'root'
        (stage / 'DEBIAN').mkdir(parents=True)
        docs = stage / 'usr/share/doc' / name
        docs.mkdir(parents=True)
        shutil.copyfile(control_path(name), stage / 'DEBIAN/control')
        shutil.copyfile(ROOT / 'README.md', docs / 'README.md')
        shutil.copyfile(ROOT / 'packaging/copyright', docs / 'copyright')
        for path in [stage, *stage.rglob('*')]:
            path.chmod(0o755 if path.is_dir() else 0o644)
            os.utime(path, (epoch, epoch))
        result = out / f'{name}_{VERSION}_all.deb'
        subprocess.run(['dpkg-deb', '--build', '--root-owner-group', '-Zxz', '-z9',
                        str(stage), str(result)], check=True,
                       env={**os.environ, 'SOURCE_DATE_EPOCH': str(epoch)})
    verify(result)
    return result


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(out):
    """Bind both local artifacts to reviewed source; no publication/readiness claim."""
    contract = compatibility()
    if contract['native_release_gates']:
        raise ValueError('release blocked: actual application package artifacts and versions are required')
    paths = [out / f'{name}_{VERSION}_all.deb' for name in (PACKAGE, LEGACY)]
    for path in paths:
        verify(path)
    if git('status', '--porcelain'):
        raise ValueError('manifest requires clean committed source')
    data = {'schema': 'agpc-apps-release/v1', 'package': PACKAGE, 'version': VERSION,
            'architecture': 'all', 'status': 'unpublished-composition-review', 'installable': False,
            'readiness': False, 'native_release_gates': contract['native_release_gates'],
            'source': 'https://github.com/motebus/agent-apps-deb', 'source_commit': git('rev-parse', 'HEAD'),
            'asset': paths[0].name, 'sha256': digest(paths[0]), 'dependency_contract': contract,
            'artifacts': [{'package': name, 'version': VERSION, 'asset': path.name, 'sha256': digest(path)}
                          for name, path in zip((PACKAGE, LEGACY), paths)]}
    record = out / 'release-manifest.json'
    record.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')
    (out / 'SHA256SUMS').write_text(''.join(digest(p) + '  ' + p.name + '\n' for p in (*paths, record)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'verify', 'compatibility', 'manifest'])
    parser.add_argument('path', nargs='?', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    if args.action == 'build':
        for name in (PACKAGE, LEGACY):
            print(build(args.path.resolve(), name))
    elif args.action == 'verify':
        verify(args.path.resolve())
        print('Package boundary audit passed')
    elif args.action == 'compatibility':
        print(json.dumps(compatibility(), indent=2))
    else:
        manifest(args.path.resolve())
