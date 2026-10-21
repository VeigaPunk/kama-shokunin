#!/usr/bin/env python3
"""Condense the state logs (S*-*.txt, written by run.sh) into a readable summary.

Usage: python3 summarize.py OUTDIR   (run.sh redirects stdout to summary.txt)
Every command block keeps its exit status. Loader, ldd -r, identity and digest lines
are only copied out of the blocks; nothing is inferred here.
"""
import glob
import os
import re
import sys


def blocks_of(lines):
    """Command blocks of one state log: [{'cmd', 'out', 'exit'}, ...]."""
    found, cur = [], None
    for ln in lines[1:]:
        if ln.startswith('$ '):
            cur = {'cmd': ln[2:], 'out': [], 'exit': None}
            found.append(cur)
        elif cur is not None and cur['exit'] is None and ln.startswith('[exit '):
            cur['exit'] = int(ln[len('[exit '):-1])
        elif cur is not None:
            cur['out'].append(ln)
    return found


def loaded(body, soname):
    """(path opened, mapped size) for the object the loader mapped under soname."""
    last_try = None
    for i, ln in enumerate(body):
        if 'trying file=' in ln and soname in ln:
            last_try = ln.split('trying file=', 1)[1].strip()
        elif 'generating link map' in ln and re.search(r'file=(\S*/)?' + re.escape(soname) + r' \[0\];', ln):
            m = re.search(r'size: (0x[0-9a-f]+)', body[i + 1]) if i + 1 < len(body) else None
            return last_try, (m.group(1) if m else '?')
    return None, None


def summarize(path):
    with open(path, encoding='utf-8', errors='replace') as fh:
        lines = fh.read().splitlines()
    print(f'== {os.path.basename(path)}')
    print(f'   {lines[0][2:]}')
    for blk in blocks_of(lines):
        cmd, rc, body = blk['cmd'], blk['exit'], [ln for ln in blk['out'] if ln.strip()]
        if 'LD_DEBUG' in cmd:
            print(f'   [exit {rc}] ld.so --list (LD_DEBUG=libs,files)')
            for ln in body:
                if re.match(r'\s+libggml\.so\.0 => ', ln):
                    print('      stdout ' + ln.strip())
                elif 'error while loading' in ln:
                    print('      stderr ' + ln.strip())
            for soname in ('libllama-server-impl.so', 'libggml.so.0'):
                path_, size = loaded(body, soname)
                if path_:
                    print(f'      {soname}: opened {path_}  mapped size {size}')
        elif '/usr/bin/ldd -r' in cmd:
            undef = [ln.strip() for ln in body if 'undefined symbol' in ln]
            lookup = [ln for ln in body if 'symbol lookup error' in ln]
            names = sorted({m.group(1) for ln in undef for m in [re.search(r'undefined symbol: (\S+)', ln)] if m})
            print(f'   [exit {rc}] ldd -r (LD_BIND_NOW=1, trace): undefined-symbol lines {len(undef)}, '
                  f'unique {len(names)}, symbol-lookup-error lines {len(lookup)}')
            if names:
                print('      ' + ' '.join(names))
        elif '/usr/bin/ldd ' in cmd:
            print(f'   [exit {rc}] ldd (trace mode)')
            for ln in body:
                if re.match(r'\s+libggml\.so\.0 => ', ln):
                    print('      stdout ' + ln.strip())
        elif cmd.startswith('ident'):
            print(f'   [exit {rc}] {cmd}')
            for ln in body:
                print('      ' + ln)
        elif 'digests.py' in cmd:
            print(f'   [exit {rc}] lane digests of {cmd.split()[-1]}')
            for ln in body:
                if ln.startswith('install_'):
                    print('      ' + ln)
        elif cmd.startswith('find'):
            print(f'   [exit {rc}] soname-level symlinks')
            for ln in body:
                print('      ' + ln)
        else:
            print(f'   [exit {rc}] {cmd}')


for state_log in sorted(glob.glob(os.path.join(sys.argv[1], 'S*-*.txt'))):
    summarize(state_log)
