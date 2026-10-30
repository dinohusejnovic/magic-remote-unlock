#!/usr/bin/env python3
"""Build dist/<id>_<version>_all.ipk and dist/<id>.manifest.json (no dependencies)."""
import gzip, hashlib, io, json, os, shutil, sys, tarfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = json.load(open(os.path.join(ROOT, 'package/app/appinfo.json')))
SVC = json.load(open(os.path.join(ROOT, 'package/service/services.json')))
APP_ID, VERSION, SVC_ID = APP['id'], APP['version'], SVC['id']
REPO = 'https://github.com/dinohusejnovic/magic-remote-unlock'

def add_tree(tar, src, dst):
    for base, dirs, files in sorted(os.walk(src)):
        dirs.sort()
        rel = os.path.relpath(base, src)
        for name in sorted(files):
            add_file(tar, os.path.join(base, name), os.path.normpath(os.path.join(dst, rel, name)))

def add_file(tar, src, arcname):
    data = open(src, 'rb').read()
    ti = tarfile.TarInfo('./' + arcname)
    ti.size, ti.mtime, ti.mode, ti.uid, ti.gid, ti.uname, ti.gname = len(data), 0, 0o755 if os.access(src, os.X_OK) else 0o644, 0, 0, 'root', 'root'
    tar.addfile(ti, io.BytesIO(data))

def add_dirs(tar, names):
    for n in names:
        ti = tarfile.TarInfo('./' + n); ti.type = tarfile.DIRTYPE; ti.mode = 0o755; ti.mtime = 0
        ti.uname = ti.gname = 'root'; tar.addfile(ti)

def tgz(build):
    raw = io.BytesIO()
    with gzip.GzipFile(fileobj=raw, mode='wb', mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode='w', format=tarfile.GNU_FORMAT) as tar:
            build(tar)
    return raw.getvalue()

def data(tar):
    add_dirs(tar, ['usr', 'usr/palm', 'usr/palm/applications/' + APP_ID,
                   'usr/palm/packages/' + APP_ID, 'usr/palm/services/' + SVC_ID])
    add_tree(tar, os.path.join(ROOT, 'package/app'), 'usr/palm/applications/' + APP_ID)
    add_tree(tar, os.path.join(ROOT, 'package/service'), 'usr/palm/services/' + SVC_ID)
    # single source of truth for the boot script: scripts/, copied into the service dir
    add_file(tar, os.path.join(ROOT, 'scripts/50-magic-remote-unlock'),
             'usr/palm/services/%s/50-magic-remote-unlock' % SVC_ID)
    info = json.dumps({'id': APP_ID, 'version': VERSION, 'app': APP_ID, 'services': [SVC_ID]}, indent=2).encode()
    ti = tarfile.TarInfo('./usr/palm/packages/%s/packageinfo.json' % APP_ID)
    ti.size, ti.mode, ti.mtime, ti.uname, ti.gname = len(info), 0o644, 0, 'root', 'root'
    tar.addfile(ti, io.BytesIO(info))

def control(tar):
    text = ('Package: %s\nVersion: %s\nSection: misc\nPriority: optional\nArchitecture: all\n'
            'Installed-Size: 64\nMaintainer: Dino Husejnovic <noreply@users.noreply.github.com>\n'
            'Description: Use older LG Magic Remotes on 2025+ webOS TVs.\n'
            'webOS-Package-Format-Version: 2\nwebOS-Packager-Version: x.y.x\n') % (APP_ID, VERSION)
    b = text.encode()
    ti = tarfile.TarInfo('./control'); ti.size, ti.mode, ti.mtime, ti.uname, ti.gname = len(b), 0o644, 0, 'root', 'root'
    tar.addfile(ti, io.BytesIO(b))

def ar(members):
    out = b'!<arch>\n'
    for name, blob in members:
        out += ('%-16s%-12d%-6d%-6d%-8s%-10d`\n' % (name, 0, 0, 0, '100644', len(blob))).encode()
        out += blob + (b'\n' if len(blob) % 2 else b'')
    return out

ipk_name = '%s_%s_all.ipk' % (APP_ID, VERSION)
blob = ar([('debian-binary', b'2.0\n'), ('control.tar.gz', tgz(control)), ('data.tar.gz', tgz(data))])
dist = os.path.join(ROOT, 'dist'); shutil.rmtree(dist, ignore_errors=True); os.makedirs(dist)
open(os.path.join(dist, ipk_name), 'wb').write(blob)
manifest = {'id': APP_ID, 'version': VERSION, 'type': 'web', 'title': APP['title'],
            'appDescription': APP['appDescription'],
            'iconUri': 'https://raw.githubusercontent.com/dinohusejnovic/magic-remote-unlock/main/assets/icon160.png',
            'sourceUrl': REPO, 'rootRequired': True, 'ipkUrl': ipk_name,
            'ipkHash': {'sha256': hashlib.sha256(blob).hexdigest()}}
open(os.path.join(dist, APP_ID + '.manifest.json'), 'w').write(json.dumps(manifest, separators=(',', ':')))
print(ipk_name, len(blob), 'bytes sha256', manifest['ipkHash']['sha256'])
