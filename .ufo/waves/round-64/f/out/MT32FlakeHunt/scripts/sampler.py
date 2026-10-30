#!/usr/bin/env python3
"""Sampler for the counter's `unreadable_own` risk window (read-only).

The counter grades bind_holders as failed when ANY process on the host
whose /proc/<pid>/fd table is unreadable to the counter's uid started at
or after the tool process started (counter: collect() ->
unreadable_own; grade_binding -> bind_holders). This sampler measures the
same quantity over time: the number of live fd-unreadable processes whose
start ticks fall inside a sliding window of the last W seconds, i.e. the
population the counter would grade as unreadable_own for a tool that
started W seconds ago.

Usage: sampler.py <out.json> <duration_s> <window_s>
"""
import json
import os
import sys
import time

HZ = os.sysconf('SC_CLK_TCK')


def ticks(pid):
    try:
        s = open(f'/proc/{pid}/stat', encoding='ascii').read()
        r = s[s.rindex(')') + 2:].split()
        return int(r[19])
    except Exception:
        return None


def scan_unreadable():
    """(pid -> start_ticks) for live processes whose fd table we may not
    read (other uid)."""
    out = {}
    for name in os.listdir('/proc'):
        if not name.isdigit():
            continue
        pid = int(name)
        try:
            os.listdir(f'/proc/{pid}/fd')
            continue
        except PermissionError:
            pass
        except OSError:
            continue
        t = ticks(pid)
        if t is not None:
            out[pid] = t
    return out


def main():
    out_path, dur, win = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
    win_ticks = int(win * HZ)
    samples = []
    t0 = time.monotonic()
    while time.monotonic() - t0 < dur:
        now_ticks = int(float(open('/proc/uptime').read().split()[0]) * HZ)
        u = scan_unreadable()
        in_win = [p for p, t in u.items() if t >= now_ticks - win_ticks]
        samples.append({
            't': round(time.monotonic() - t0, 2),
            'load1': round(os.getloadavg()[0], 2),
            'unreadable_total': len(u),
            'unreadable_in_window': len(in_win),
            'in_window_pids': sorted(in_win),
        })
        time.sleep(0.2)
    with open(out_path, 'w') as f:
        json.dump({'window_s': win, 'samples': samples}, f, indent=1)
    peaks = sorted((s['unreadable_in_window'] for s in samples), reverse=True)[:10]
    print(f'wrote {out_path}: {len(samples)} samples; '
          f'top unreadable_in_window counts: {peaks}')


if __name__ == '__main__':
    main()
