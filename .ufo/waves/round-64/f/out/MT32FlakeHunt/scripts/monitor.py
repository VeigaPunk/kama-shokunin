#!/usr/bin/env python3
"""Diagnostic sampler for the C1 flake hunt (read-only).

Samples every 0.25 s: load average, and the set of /proc/<pid> whose fd
table is unreadable to this uid (PermissionError), split by whether the
pid's start ticks are older or newer than a reference. Also records the
number of processes and the number of llama-server processes.

Usage: monitor.py <outfile> <duration-seconds> [reference-tool-start-ticks]
"""
import json
import os
import sys
import time


def unreadable_pids():
    out = []
    try:
        names = os.listdir('/proc')
    except OSError:
        return out
    for name in names:
        if not name.isdigit():
            continue
        try:
            os.listdir(f'/proc/{name}/fd')
        except PermissionError:
            out.append(int(name))
        except OSError:
            pass
    return out


def stat_fields(pid):
    try:
        s = open(f'/proc/{pid}/stat', encoding='ascii').read()
        rest = s[s.rindex(')') + 2:].split()
        return int(rest[1]), int(rest[19])
    except (OSError, ValueError, IndexError):
        return None, None


def llama_servers():
    n = 0
    for name in os.listdir('/proc'):
        if not name.isdigit():
            continue
        try:
            c = open(f'/proc/{name}/cmdline', 'rb').read().decode(
                'utf-8', 'replace')
        except OSError:
            continue
        if 'llama-server' in c:
            n += 1
    return n


def main():
    out_path = sys.argv[1]
    dur = float(sys.argv[2])
    ref = int(sys.argv[3]) if len(sys.argv) > 3 else None
    samples = []
    t0 = time.monotonic()
    while time.monotonic() - t0 < dur:
        un = unreadable_pids()
        new = []
        old = []
        unknown = []
        for p in un:
            _, tk = stat_fields(p)
            if tk is None:
                unknown.append(p)
            elif ref is not None and tk >= ref:
                new.append(p)
            else:
                old.append(p)
        la = os.getloadavg()
        samples.append({
            't': round(time.monotonic() - t0, 2),
            'load1': round(la[0], 2),
            'nproc': len(os.listdir('/proc')),
            'llama': llama_servers(),
            'unreadable_new': new,
            'unreadable_old': old,
            'unreadable_unknown': unknown,
        })
        time.sleep(0.25)
    with open(out_path, 'w') as f:
        json.dump({'reference_ticks': ref, 'samples': samples}, f, indent=1)
    print(f'wrote {out_path}: {len(samples)} samples')


if __name__ == '__main__':
    main()
