#!/usr/bin/env python3
"""Build the record-time archive cases for seat X12Zip (round 50).

Target contract: tools/kama-llamacpp-live.py::verify_archive_member at lane commit
97c864bead3ee4a2f629574e77263d33834ec98a (ARCHIVE_MAX_BYTES = 1 GiB,
MEMBER_MAX_COUNT = 4096). Nothing here executes an archive member: the "server" is
inert stub bytes, and every case is only fed to the frozen verifier.

Usage: build_cases.py <casedir> <stub-file>
Writes <casedir>/<case>/archive plus <casedir>/<case>/case.json.
"""
import gzip
import hashlib
import io
import json
import os
import sys
import tarfile
import time

MEMBER = 'rel/llama-server'
TINY_MEMBERS = 20000
MANY_MEMBERS = 4000


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def write_case(root, name, archive, asset_sha, server_sha, server_size,
               expected=None, note='', extra=None):
    d = os.path.join(root, name)
    os.makedirs(d, exist_ok=True)
    os.replace(archive, os.path.join(d, 'archive'))
    spec = {
        'case': name,
        'archive': os.path.join(d, 'archive'),
        'archive_bytes': os.path.getsize(spec_path(d, 'archive')),
        'archive_sha256': asset_sha,
        'member': MEMBER,
        'server_sha256': server_sha,
        'server_size': server_size,
        'expected': expected,
        'note': note,
    }
    if extra:
        spec.update(extra)
    with open(os.path.join(d, 'case.json'), 'w') as fh:
        json.dump(spec, fh, indent=2, sort_keys=True)
        fh.write('\n')
    return spec


def spec_path(d, leaf):
    return os.path.join(d, leaf)


def tar_bytes(members, compress=None):
    """members: list of (name, data-or-None). Returns bytes of a tar(.gz)."""
    buf = io.BytesIO()
    mode = 'w:' + compress if compress else 'w'
    with tarfile.open(fileobj=buf, mode=mode, format=tarfile.GNU_FORMAT) as tf:
        for name, data in members:
            ti = tarfile.TarInfo(name)
            ti.mtime = 0
            if data is None:
                ti.type = tarfile.DIRTYPE
                ti.size = 0
                tf.addfile(ti)
            else:
                ti.size = len(data)
                tf.addfile(ti, io.BytesIO(data))
    return buf.getvalue()


def build(root, stub):
    stub_sha = hashlib.sha256(stub).hexdigest()
    stub_size = len(stub)
    out = {}

    # (d first: it is the positive control the others are read against)
    # positive control: 4000 members plus the real member, valid digests, correct size
    cases = []
    for i in range(MANY_MEMBERS):
        cases.append((f'rel/f{i:05d}', b''))
    cases.append((MEMBER, stub))
    many_path = os.path.join(root, 'd_valid_many.tar.gz')
    with open(many_path, 'wb') as fh:
        fh.write(tar_bytes(cases, 'gz'))
    out['d_valid_many'] = write_case(
        root, 'd_valid_many', many_path, sha256_file(many_path), stub_sha, stub_size,
        expected='accepted',
        note='positive control: 4001 members, correct archive sha, member sha and size')

    # (a) count cap: 20000 tiny members before the real member
    cases = [(f'rel/t{i:05d}', b'') for i in range(TINY_MEMBERS)]
    cases.append((MEMBER, stub))
    tiny_path = os.path.join(root, 'a_20000_tiny.tar')
    with open(tiny_path, 'wb') as fh:
        fh.write(tar_bytes(cases))
    out['a_20000_tiny'] = write_case(
        root, 'a_20000_tiny', tiny_path, sha256_file(tiny_path), stub_sha, stub_size,
        expected='provenance-archive-too-many-members',
        note='20000 zero-length members then the real member; cap is 4096 entries')

    # (b) member declares the server size but the archive data is truncated
    full = tar_bytes([(f'rel/head', b'x'), (MEMBER, stub)])
    member_hdr = full.index(MEMBER.encode())
    header_off = member_hdr - 0  # name starts at the member header
    data_off = header_off + 512
    truncated = bytearray(full[:data_off + stub_size // 2 + 7])
    trunc_path = os.path.join(root, 'b_truncated_declared_size.tar')
    with open(trunc_path, 'wb') as fh:
        fh.write(truncated)
    out['b_truncated_declared_size'] = write_case(
        root, 'b_truncated_declared_size', trunc_path, sha256_file(trunc_path),
        stub_sha, stub_size,
        expected='provenance-archive-unreadable (data cut at half the declared size)',
        note='header declares the server size; data present is half of it, no EOF blocks')

    # (c) gzip stream of zeros decompressing to a huge empty tar (no header at all)
    huge = 4 << 30
    zpath = os.path.join(root, 'c_gzip_zeros_huge.tar.gz')
    t0 = time.time()
    with open(zpath, 'wb') as raw, \
            gzip.GzipFile(filename='', mode='wb', fileobj=raw, compresslevel=1,
                          mtime=0) as gz:
        chunk = b'\0' * (1 << 20)
        for _ in range(huge >> 20):
            gz.write(chunk)
    out['c_gzip_zeros_huge'] = write_case(
        root, 'c_gzip_zeros_huge', zpath, sha256_file(zpath), stub_sha, stub_size,
        expected='provenance-member-absent',
        note=f'{huge} decompressed zero bytes, no tar header anywhere',
        extra={'decompressed_bytes': huge, 'build_seconds': round(time.time() - t0, 3)})

    # (c2) gzip whose decompressed index is a header declaring a huge size for a
    # non-member name: tarfile must skip the declared size, i.e. decompress it
    for label, declared in (('c2_gzip_seek_512m', 512 << 20),
                            ('c2_gzip_seek_2g', 2 << 30)):
        path = os.path.join(root, label + '.tar.gz')
        ti = tarfile.TarInfo('rel/other')
        ti.size = declared
        ti.mtime = 0
        header = ti.tobuf(format=tarfile.GNU_FORMAT)
        assert len(header) == 512, len(header)
        t0 = time.time()
        with open(path, 'wb') as raw, \
                gzip.GzipFile(filename='', mode='wb', fileobj=raw, compresslevel=1,
                              mtime=0) as gz:
            gz.write(header)
            chunk = b'\0' * (1 << 20)
            for _ in range(declared >> 20):
                gz.write(chunk)
        out[label] = write_case(
            root, label, path, sha256_file(path), stub_sha, stub_size,
            expected='skip costs the declared size, then EOF -> refusal',
            note=f'header declares {declared} bytes for rel/other; zeros after it',
            extra={'declared_skip_bytes': declared,
                   'build_seconds': round(time.time() - t0, 3)})

    # (c3) same header declaring far more than the stream holds (EOF mid-skip)
    declared = 64 << 30
    present = 256 << 20
    path = os.path.join(root, 'c3_gzip_seek_past_eof.tar.gz')
    ti = tarfile.TarInfo('rel/other')
    ti.size = declared
    ti.mtime = 0
    header = ti.tobuf(format=tarfile.GNU_FORMAT)
    with open(path, 'wb') as raw, \
            gzip.GzipFile(filename='', mode='wb', fileobj=raw, compresslevel=1,
                          mtime=0) as gz:
        gz.write(header)
        chunk = b'\0' * (1 << 20)
        for _ in range(present >> 20):
            gz.write(chunk)
    out['c3_gzip_seek_past_eof'] = write_case(
        root, 'c3_gzip_seek_past_eof', path, sha256_file(path), stub_sha, stub_size,
        expected='decompresses every present byte, then EOF -> refusal',
        note=f'declares {declared} but holds {present}; cost should stop at the stream end',
        extra={'declared_skip_bytes': declared, 'decompressed_present_bytes': present})

    return out


def main(argv):
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2
    casedir, stub_path = argv[1], argv[2]
    os.makedirs(casedir, exist_ok=True)
    with open(stub_path, 'rb') as fh:
        stub = fh.read()
    specs = build(casedir, stub)
    with open(os.path.join(casedir, 'cases.json'), 'w') as fh:
        json.dump(specs, fh, indent=2, sort_keys=True)
        fh.write('\n')
    for name, spec in sorted(specs.items()):
        print(json.dumps({'case': name, 'archive_bytes': spec['archive_bytes'],
                          'expected': spec['expected']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
