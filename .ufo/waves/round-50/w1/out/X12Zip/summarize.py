#!/usr/bin/env python3
"""Turn the X12Zip probe receipts into summary.md and summary.csv.

Reads run1/run2/run3 (frozen tool at 97c864b) and run1p/run2p (the proposed fix
for the same cases); case manifests under cases/ supply the case shape.

Usage: summarize.py <this-dir>
"""
import json
import os
import sys

RUNS_FROZEN = ('run1', 'run2', 'run3')
RUNS_PATCHED = ('run1p', 'run2p', 'run3p')
ORDER = [
    'a_20000_tiny', 'b_truncated_declared_size', 'b2_padded_wrong_data',
    'c_gzip_zeros_huge', 'c2_gzip_seek_512m', 'c2_gzip_seek_2g',
    'c3_gzip_seek_past_eof', 'e_xz_seek_4g', 'f_bz2_seek_256m',
    'f_bz2_seek_8g', 'f_bz2_seek_32g', 'f_bz2_seek_past_eof',
    'boundary_4096_ok', 'boundary_4097_cap', 'd_valid_many',
]


def load_runs(root, runs):
    out = {}
    for run in runs:
        path = os.path.join(root, run, 'results.json')
        if not os.path.exists(path):
            continue
        with open(path) as fh:
            payload = json.load(fh)
        for row in payload['results']:
            row['_run'] = run
            out[row['case']] = row
    return out


def load_manifests(root):
    out = {}
    d = os.path.join(root, 'cases')
    for name in sorted(os.listdir(d)):
        path = os.path.join(d, name, 'case.json')
        if os.path.exists(path):
            with open(path) as fh:
                out[name] = json.load(fh)
    return out


def decompressed(spec):
    for key in ('decompressed_present_bytes', 'decompressed_bytes', 'declared_skip_bytes'):
        if key in spec:
            return spec[key], key
    return None, None


def fmt_bytes(n):
    if n is None:
        return '-'
    for unit, scale in (('GiB', 1 << 30), ('MiB', 1 << 20), ('KiB', 1 << 10)):
        if n >= scale:
            return f'{n / scale:.2f} {unit}'
    return f'{n} B'


def main(argv):
    root = argv[1] if len(argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    frozen = load_runs(root, RUNS_FROZEN)
    patched = load_runs(root, RUNS_PATCHED)
    specs = load_manifests(root)
    names = [n for n in ORDER if n in frozen or n in patched]
    names += sorted((set(frozen) | set(patched)) - set(names))

    rows = []
    for name in names:
        spec = specs.get(name, {})
        dec, dec_key = decompressed(spec)
        f = frozen.get(name, {})
        p = patched.get(name, {})
        ratio = (dec / f['archive_bytes']) if dec and f.get('archive_bytes') else None
        rows.append({
            'case': name,
            'archive_bytes': f.get('archive_bytes') or p.get('archive_bytes'),
            'decompressed_bytes': dec,
            'decompressed_source': dec_key,
            'ratio': f'{ratio:.0f}x' if ratio else '-',
            'frozen_token': f.get('token') or ('accepted' if 'returned' in f else f.get('result')),
            'frozen_seconds': f.get('seconds'),
            'frozen_rss_kb': f.get('peak_rss_kb'),
            'frozen_member_hashed': f.get('member_hashed_before_verdict'),
            'frozen_extractfile_calls': f.get('extractfile_calls'),
            'frozen_member_hash_bytes': f.get('member_hash_bytes'),
            'frozen_tar_walk_offsets': (f.get('tar_walk') or {}).get('next_calls'),
            'frozen_decompressed_consumed': (f.get('tar_walk') or {}).get('last_tell'),
            'patched_token': p.get('token') or ('accepted' if 'returned' in p else p.get('result')),
            'patched_seconds': p.get('seconds'),
            'patched_rss_kb': p.get('peak_rss_kb'),
            'run': f.get('_run'),
            'patched_run': p.get('_run'),
        })

    header = ['case', 'archive_bytes', 'decompressed_bytes', 'decompressed_source',
              'frozen_token', 'frozen_seconds', 'frozen_rss_kb',
              'frozen_member_hashed', 'frozen_extractfile_calls',
              'frozen_member_hash_bytes', 'frozen_decompressed_consumed',
              'patched_token', 'patched_seconds', 'run', 'patched_run']
    with open(os.path.join(root, 'summary.csv'), 'w') as fh:
        fh.write(','.join(header) + '\n')
        for r in rows:
            fh.write(','.join('' if r.get(k) is None else str(r.get(k))
                              for k in header) + '\n')

    with open(os.path.join(root, 'summary.md'), 'w') as fh:
        fh.write('# X12Zip probe summary\n\n')
        fh.write('Frozen tool: tools/kama-llamacpp-live.py at lane commit '
                 '97c864bead3ee4a2f629574e77263d33834ec98a. Patched = the proposed\n'
                 'fix in proposed/. RSS is the whole-child peak (interpreter '
                 'baseline ~27 MB).\n\n')
        fh.write('| case | archive | decompressed / declared | token | s | peak RSS | '
                 'member hashed | extractfile | decompressed consumed | patched token | '
                 'patched s |\n')
        fh.write('|---|---|---|---|---|---|---|---|---|---|---|\n')
        for r in rows:
            fh.write('| {} | {} | {} | {} | {} | {} MB | {} | {} | {} | {} | {} |\n'.format(
                r['case'], fmt_bytes(r['archive_bytes']),
                fmt_bytes(r['decompressed_bytes']),
                r['frozen_token'], r['frozen_seconds'],
                round((r['frozen_rss_kb'] or 0) / 1024), r['frozen_member_hashed'],
                r['frozen_extractfile_calls'],
                fmt_bytes(r['frozen_decompressed_consumed']),
                r['patched_token'], r['patched_seconds']))
        fh.write('\n## Cost of a declared skip through verify_archive_member (frozen)\n\n')
        for name in ('f_bz2_seek_256m', 'f_bz2_seek_8g', 'f_bz2_seek_32g',
                     'e_xz_seek_4g', 'c2_gzip_seek_2g'):
            r = next((x for x in rows if x['case'] == name), None)
            if not r or not r['decompressed_bytes'] or not r['frozen_seconds']:
                continue
            rate = r['decompressed_bytes'] / r['frozen_seconds'] / 1e6
            fh.write(f'- {name}: {r["archive_bytes"]} B on disk, '
                     f'{fmt_bytes(r["decompressed_bytes"])} decoded in '
                     f'{r["frozen_seconds"]} s ({rate:.0f} MB/s), '
                     f'ratio {r["ratio"]}\n')
    print(json.dumps({'cases': len(rows), 'summary': os.path.join(root, 'summary.md')}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
