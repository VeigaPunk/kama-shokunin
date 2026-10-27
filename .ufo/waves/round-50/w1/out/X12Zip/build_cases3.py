#!/usr/bin/env python3
"""Third battery for seat X12Zip: one large-dose bz2 skip so the cost curve is pinned
at 4x the 8 GiB point (linearity and per-GiB constant), not extrapolated from two
points. Same inert-data contract as build_cases.py / build_cases2.py.

Usage: build_cases3.py <casedir> <stub-file>
"""
import bz2
import hashlib
import json
import os
import sys
import tarfile

MEMBER = 'rel/llama-server'
DECLARED = 32 << 30


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main(argv):
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2
    casedir, stub_path = argv[1], argv[2]
    os.makedirs(casedir, exist_ok=True)
    with open(stub_path, 'rb') as fh:
        stub = fh.read()
    ti = tarfile.TarInfo('rel/other')
    ti.size = DECLARED
    ti.mtime = 0
    header = ti.tobuf(format=tarfile.GNU_FORMAT)
    assert len(header) == 512
    name = 'f_bz2_seek_32g'
    d = os.path.join(casedir, name)
    os.makedirs(d, exist_ok=True)
    dest = os.path.join(d, 'archive')
    with open(dest, 'wb') as raw:
        with bz2.BZ2File(raw, 'wb', compresslevel=9) as w:
            w.write(header)
            chunk = b'\0' * (1 << 20)
            for _ in range(DECLARED >> 20):
                w.write(chunk)
    spec = {
        'case': name,
        'archive': dest,
        'archive_bytes': os.path.getsize(dest),
        'archive_sha256': sha256_file(dest),
        'member': MEMBER,
        'server_sha256': hashlib.sha256(stub).hexdigest(),
        'server_size': len(stub),
        'expected': 'member-absent after decompressing the declared skip',
        'note': 'one 512-byte header declaring a 32 GiB non-member, then zeros',
        'declared_skip_bytes': DECLARED,
    }
    with open(os.path.join(d, 'case.json'), 'w') as fh:
        json.dump(spec, fh, indent=2, sort_keys=True)
        fh.write('\n')
    with open(os.path.join(casedir, 'cases.json'), 'w') as fh:
        json.dump({name: spec}, fh, indent=2, sort_keys=True)
        fh.write('\n')
    print(json.dumps({'case': name, 'archive_bytes': spec['archive_bytes']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
