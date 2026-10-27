#!/usr/bin/env python3
"""Drive the X12Zip record-time archive probe: build cases, measure each in its own
process, write results.json/results.txt.

Usage: run_probe.py --out <dir> --scratch <dir> --tool <kama-llamacpp-live.py>
The tool is read, never edited; the cases are inert data (no member is executed).
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

# generous; the seek-bomb cases are the point of the exercise
TIMEOUTS = {
    'c_gzip_zeros_huge': 120,
    'c2_gzip_seek_512m': 180,
    'c2_gzip_seek_2g': 300,
    'c3_gzip_seek_past_eof': 120,
    'f_bz2_seek_256m': 120,
    'f_bz2_seek_8g': 300,
    'f_bz2_seek_past_eof': 300,
    'e_xz_seek_4g': 300,
}
DEFAULT_TIMEOUT = 120


def make_stub(path):
    body = bytes(((i * 37 + 11) % 251) for i in range(8192))
    body = b'\x7fELF' + body[4:]
    with open(path, 'wb') as fh:
        fh.write(body)
    return body


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--scratch', required=True)
    ap.add_argument('--tool', required=True)
    ap.add_argument('--builder', default='build_cases.py')
    ap.add_argument('--reuse', action='store_true',
                    help='use an existing <scratch>/cases instead of rebuilding')
    args = ap.parse_args(argv[1:])
    os.makedirs(args.out, exist_ok=True)
    os.makedirs(args.scratch, exist_ok=True)
    casedir = os.path.join(args.scratch, 'cases')
    stub = os.path.join(args.scratch, 'stub-server')
    make_stub(stub)

    t0 = time.time()
    if not (args.reuse and os.path.exists(os.path.join(casedir, 'cases.json'))):
        subprocess.run([sys.executable, '-I', os.path.join(HERE, args.builder),
                        casedir, stub], check=True)
    build_seconds = round(time.time() - t0, 2)
    with open(os.path.join(casedir, 'cases.json')) as fh:
        specs = json.load(fh)

    results = []
    for name in sorted(specs):
        spec_path = os.path.join(casedir, name, 'case.json')
        timeout = TIMEOUTS.get(name, DEFAULT_TIMEOUT)
        t0 = time.time()
        try:
            proc = subprocess.run(
                [sys.executable, '-I', os.path.join(HERE, 'measure_case.py'),
                 '--tool', args.tool, '--spec', spec_path],
                capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            results.append({'case': name, 'result': 'timeout', 'timeout_s': timeout,
                            'wall_seconds': round(time.time() - t0, 2)})
            print(f'{name}: TIMEOUT after {timeout}s', file=sys.stderr)
            continue
        wall = round(time.time() - t0, 2)
        if proc.returncode != 0:
            results.append({'case': name, 'result': 'probe-failure',
                            'returncode': proc.returncode,
                            'stderr': proc.stderr[-2000:], 'wall_seconds': wall})
            print(f'{name}: probe exit {proc.returncode}: {proc.stderr[-400:]}',
                  file=sys.stderr)
            continue
        row = json.loads(proc.stdout)
        row['wall_seconds'] = wall
        results.append(row)

    payload = {'tool': args.tool, 'tool_sha256': sha256_file(args.tool),
               'build_seconds': build_seconds, 'results': results}
    with open(os.path.join(args.out, 'results.json'), 'w') as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write('\n')
    with open(os.path.join(args.out, 'results.txt'), 'w') as fh:
        fh.write(f"tool {args.tool}\ntool_sha256 {payload['tool_sha256']}\n\n")
        for r in results:
            fh.write(f"case {r['case']}\n")
            for key in ('archive_bytes', 'result', 'token', 'returned', 'seconds',
                        'wall_seconds', 'peak_rss_kb', 'hash_instances',
                        'archive_hash_bytes', 'member_hash_instances',
                        'member_hash_bytes', 'member_hashed_before_verdict',
                        'extractfile_calls', 'member_bytes_read', 'tar_walk',
                        'note', 'error'):
                if key in r:
                    fh.write(f'  {key}: {r[key]}\n')
            fh.write('\n')
    for r in results:
        print(json.dumps({k: r.get(k) for k in
                          ('case', 'result', 'token', 'seconds', 'peak_rss_kb',
                           'member_hashed_before_verdict', 'archive_bytes')},
                         sort_keys=True))
    return 0


def sha256_file(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
