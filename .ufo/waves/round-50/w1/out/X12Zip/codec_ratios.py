#!/usr/bin/env python3
"""Codec ratio and decode-rate sample for seat X12Zip: 256 MiB of zero bytes
through each codec tarfile's ``r:*`` accepts (gzip, bz2, xz). This sizes the
amplification the frozen record-time bounds do not cover; it runs no archive
member and no lane tool.

Usage: codec_ratios.py   (writes codec-ratios.txt next to itself)
"""
import bz2
import gzip
import lzma
import os
import sys
import tempfile
import time

N = 256 << 20
CHUNK = b'\0' * (1 << 20)


def measure(label, opener, suffix):
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    try:
        t0 = time.perf_counter()
        with open(path, 'wb') as raw:
            with opener(raw) as w:
                for _ in range(N >> 20):
                    w.write(CHUNK)
        warm = time.perf_counter() - t0
        compressed = os.path.getsize(path)
        reader = {'.gz': gzip.open, '.bz2': bz2.open, '.xz': lzma.open}[suffix]
        t0 = time.perf_counter()
        total = 0
        with reader(path, 'rb') as fh:
            while True:
                block = fh.read(1 << 20)
                if not block:
                    break
                total += len(block)
        decode = time.perf_counter() - t0
        return (f'{label}: decompressed {total} B, compressed {compressed} B, '
                f'ratio {total / compressed:.0f}x, decode {total / decode / 1e6:.0f} MB/s, '
                f'compress {warm:.2f} s, decode {decode:.2f} s')
    finally:
        os.unlink(path)


def main(argv):
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'codec-ratios.txt')
    lines = [f'256 MiB of zero bytes, python {sys.version.split()[0]}, '
             f'{time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}']
    lines.append(measure('gzip-1', lambda raw: gzip.GzipFile(
        filename='', mode='wb', fileobj=raw, compresslevel=1, mtime=0), '.gz'))
    lines.append(measure('gzip-9', lambda raw: gzip.GzipFile(
        filename='', mode='wb', fileobj=raw, compresslevel=9, mtime=0), '.gz'))
    lines.append(measure('bz2-9', lambda raw: bz2.BZ2File(
        raw, 'wb', compresslevel=9), '.bz2'))
    lines.append(measure('xz-1', lambda raw: lzma.LZMAFile(
        raw, 'wb', preset=1), '.xz'))
    with open(out, 'w') as fh:
        fh.write('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
