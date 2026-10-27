#!/usr/bin/env python3
"""Second battery for seat X12Zip: codec amplification and boundary cases.

Same contract target as build_cases.py: tools/kama-llamacpp-live.py::verify_archive_member
at 97c864bead3ee4a2f629574e77263d33834ec98a. Every case is inert data for the frozen
verifier; no member is executed.

Usage: build_cases2.py <casedir> <stub-file>
"""
import bz2
import hashlib
import io
import json
import lzma
import os
import sys
import tarfile

MEMBER = 'rel/llama-server'


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def record(root, name, src, stub_sha, stub_size, expected, note, extra=None):
    d = os.path.join(root, name)
    os.makedirs(d, exist_ok=True)
    dest = os.path.join(d, 'archive')
    os.replace(src, dest)
    spec = {
        'case': name,
        'archive': dest,
        'archive_bytes': os.path.getsize(dest),
        'archive_sha256': sha256_file(dest),
        'member': MEMBER,
        'server_sha256': stub_sha,
        'server_size': stub_size,
        'expected': expected,
        'note': note,
    }
    if extra:
        spec.update(extra)
    with open(os.path.join(d, 'case.json'), 'w') as fh:
        json.dump(spec, fh, indent=2, sort_keys=True)
        fh.write('\n')
    return spec


def tar_bytes(members, compress=None, fmt=tarfile.GNU_FORMAT):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w:' + compress if compress else 'w',
                      format=fmt) as tf:
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


def write_stream(path, opener, header, declared):
    """Write `header` then `declared` zero bytes through a compressing stream."""
    with open(path, 'wb') as raw:
        with opener(raw) as w:
            w.write(header)
            chunk = b'\0' * (1 << 20)
            for _ in range(declared >> 20):
                w.write(chunk)


def skip_header(name, size):
    ti = tarfile.TarInfo(name)
    ti.size = size
    ti.mtime = 0
    hdr = ti.tobuf(format=tarfile.GNU_FORMAT)
    assert len(hdr) == 512
    return hdr


def build(root, stub):
    stub_sha = hashlib.sha256(stub).hexdigest()
    stub_size = len(stub)
    out = {}

    # boundary: exactly MEMBER_MAX_COUNT entries with the real member last
    entries = [(f'rel/b{i:05d}', b'') for i in range(4095)] + [(MEMBER, stub)]
    p = os.path.join(root, 'boundary_4096_ok.tar')
    with open(p, 'wb') as fh:
        fh.write(tar_bytes(entries))
    out['boundary_4096_ok'] = record(
        root, 'boundary_4096_ok', p, stub_sha, stub_size, 'accepted',
        '4096 entries exactly (cap is >4096), real member last')

    entries = [(f'rel/b{i:05d}', b'') for i in range(4096)] + [(MEMBER, stub)]
    p = os.path.join(root, 'boundary_4097_cap.tar')
    with open(p, 'wb') as fh:
        fh.write(tar_bytes(entries))
    out['boundary_4097_cap'] = record(
        root, 'boundary_4097_cap', p, stub_sha, stub_size,
        'provenance-archive-too-many-members',
        '4097 entries, one past the cap')

    # padded wrong data: declared size equals the server size, bytes differ -> the
    # refusal is *after* hashing exactly server_size member bytes (the hashing bound)
    wrong = b'\xaa' * stub_size
    p = os.path.join(root, 'b2_padded_wrong_data.tar')
    with open(p, 'wb') as fh:
        fh.write(tar_bytes([(MEMBER, wrong)]))
    out['b2_padded_wrong_data'] = record(
        root, 'b2_padded_wrong_data', p, stub_sha, stub_size,
        'provenance-member-digest-mismatch',
        'declared size == server size so the size check passes; bytes are wrong')

    # bz2: 256 MiB of zeros behind one header is ~208 bytes on disk
    p = os.path.join(root, 'f_bz2_seek_256m.tar.bz2')
    write_stream(p, lambda raw: bz2.BZ2File(raw, 'wb', compresslevel=9),
                 skip_header('rel/other', 256 << 20), 256 << 20)
    out['f_bz2_seek_256m'] = record(
        root, 'f_bz2_seek_256m', p, stub_sha, stub_size,
        'member-absent after decompressing the declared skip',
        'one 512-byte header declaring a 256 MiB non-member, then zeros',
        {'declared_skip_bytes': 256 << 20})

    # bz2 8 GiB: same shape, 32x the decompressed work
    p = os.path.join(root, 'f_bz2_seek_8g.tar.bz2')
    write_stream(p, lambda raw: bz2.BZ2File(raw, 'wb', compresslevel=9),
                 skip_header('rel/other', 8 << 30), 8 << 30)
    out['f_bz2_seek_8g'] = record(
        root, 'f_bz2_seek_8g', p, stub_sha, stub_size,
        'member-absent after decompressing the declared skip',
        'one 512-byte header declaring an 8 GiB non-member, then zeros',
        {'declared_skip_bytes': 8 << 30})

    # bz2 declaring far more than the stream holds: cost stops at stream end
    p = os.path.join(root, 'f_bz2_seek_past_eof.tar.bz2')
    write_stream(p, lambda raw: bz2.BZ2File(raw, 'wb', compresslevel=9),
                 skip_header('rel/other', 64 << 30), 8 << 30)
    out['f_bz2_seek_past_eof'] = record(
        root, 'f_bz2_seek_past_eof', p, stub_sha, stub_size,
        'provenance-archive-unreadable after decompressing every present byte',
        'declares 64 GiB, holds 8 GiB of zeros',
        {'declared_skip_bytes': 64 << 30, 'decompressed_present_bytes': 8 << 30})

    # xz: ratio ~7e3, decode ~0.7 GB/s
    p = os.path.join(root, 'e_xz_seek_4g.tar.xz')
    write_stream(p, lambda raw: lzma.LZMAFile(raw, 'wb', preset=1),
                 skip_header('rel/other', 4 << 30), 4 << 30)
    out['e_xz_seek_4g'] = record(
        root, 'e_xz_seek_4g', p, stub_sha, stub_size,
        'member-absent after decompressing the declared skip',
        'one header declaring a 4 GiB non-member, then zeros, xz preset 1',
        {'declared_skip_bytes': 4 << 30})

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
