#!/usr/bin/env python3
"""List release zip layouts from their central directories over HTTP Range
requests: about three small requests per asset, no asset downloaded in full.
Only .zip assets are read; .tar.gz layouts cannot be listed this way.

usage: python3 -B zip-layouts.py --tsv release-b11755-assets.tsv [--json OUT.json]
tsv columns: name, browser_download_url, size. Produce it with:
  gh api repos/ggml-org/llama.cpp/releases/tags/b11755 \
    --jq '.assets[] | [.name, .browser_download_url, (.size|tostring)] | @tsv'
"""
import argparse
import io
import json
import urllib.request
import zipfile

MAX_READ = 64 << 20


class RangeFile(io.RawIOBase):
    """Read-only seekable file over HTTP Range requests."""

    def __init__(self, url, size):
        super().__init__()
        self.url, self.size, self.pos = url, size, 0
        self.requests, self.fetched = 0, 0

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=0):
        base = {0: 0, 1: self.pos, 2: self.size}[whence]
        self.pos = base + offset
        return self.pos

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.size - self.pos
        n = max(0, min(n, self.size - self.pos))
        if n == 0:
            return b''
        if n > MAX_READ:
            raise RuntimeError('refusing a large read')
        start, end = self.pos, self.pos + n - 1
        req = urllib.request.Request(
            self.url, headers={'Range': f'bytes={start}-{end}',
                               'User-Agent': 'kama-r21-C2ClaimCritic/1.0'})
        with urllib.request.urlopen(req, timeout=120) as resp:
            code = resp.status
            data = resp.read()
        if code != 206 or len(data) != n:
            raise RuntimeError(f'range not honoured: status={code} got={len(data)} want={n}')
        self.pos += n
        self.requests += 1
        self.fetched += n
        return data


def summarize(url, size):
    rf = RangeFile(url, size)
    with zipfile.ZipFile(rf) as zf:
        infos = zf.infolist()
    dirs = [i.filename for i in infos if i.filename.endswith('/')]
    files = [i for i in infos if not i.filename.endswith('/')]
    links = [i.filename for i in infos
             if ((i.external_attr >> 16) & 0o170000) == 0o120000]
    per_dir = {}
    for i in files:
        if '/' in i.filename:
            top = i.filename.split('/')[0] + '/'
            per_dir[top] = per_dir.get(top, 0) + 1
    return {
        'size': size,
        'entries': len(infos),
        'dir_entries': len(dirs),
        'symlink_entries': len(links),
        'files_under_subdir': sum(per_dir.values()),
        'files_per_top_dir': per_dir,
        'dirs': dirs[:20],
        'requests': rf.requests,
        'bytes_fetched': rf.fetched,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--tsv', required=True)
    ap.add_argument('--json')
    args = ap.parse_args()
    results = {}
    with open(args.tsv) as fh:
        for line in fh:
            name, url, size = line.rstrip('\n').split('\t')
            if not name.endswith('.zip'):
                continue
            try:
                results[name] = summarize(url, int(size))
            except Exception as exc:  # report, do not hide
                results[name] = {'error': repr(exc)[:240]}
    if args.json:
        with open(args.json, 'w') as fh:
            json.dump(results, fh, indent=1, sort_keys=True)
    for name in sorted(results):
        v = results[name]
        if 'error' in v:
            print(f"ERROR {name}: {v['error']}")
            continue
        print(f"{name}: entries={v['entries']} dirs={v['dir_entries']} "
              f"symlinks={v['symlink_entries']} files_under_subdir={v['files_under_subdir']} "
              f"per_top_dir={v['files_per_top_dir']} dir_entries={v['dirs'][:4]} "
              f"fetched={v['bytes_fetched']}B requests={v['requests']}")


if __name__ == '__main__':
    main()
