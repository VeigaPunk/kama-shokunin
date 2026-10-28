#!/usr/bin/env python3
"""Mechanism control for E12KillSwitch: PR_SET_PDEATHSIG positive and negative.

No server, no port, no llama: a scratch harness spawns `sleep 300` twice — once with
prctl(PR_SET_PDEATHSIG, SIGKILL) and once without — and the conductor SIGKILLs each
harness. A: the child must die (pdeathsig works). B: without the prctl the child must
survive (so the live-run observation is attributable to pdeathsig, not to something
else in the environment). The survivor is killed by this conductor, which spawned it.
"""
import json
import os
import signal
import subprocess
import sys
import time

SCRATCH = os.path.dirname(os.path.abspath(__file__))
HARNESS = r'''
import ctypes, os, signal, sys, time
pidfile = sys.argv[1]
mode = sys.argv[2]          # "1"=child-side prctl, "0"=none, "2"=parent-side prctl
use_prctl = mode == "1"
harness_pid = os.getpid()
if mode == "2":
    libc = ctypes.CDLL(None, use_errno=True)
    libc.prctl(1, signal.SIGKILL, 0, 0, 0)   # wrong process: cleared by fork(2)
child = os.fork()
if child == 0:
    if use_prctl:
        # the setting is cleared for the child of fork(2) and survives exec:
        # it must be requested by the process that will outlive its parent
        libc = ctypes.CDLL(None, use_errno=True)
        libc.prctl(1, signal.SIGKILL, 0, 0, 0)   # PR_SET_PDEATHSIG
        if os.getppid() != harness_pid:
            os._exit(1)
    os.execvp("sleep", ["sleep", "300"])
with open(pidfile, "w") as fh:
    fh.write(str(child))
time.sleep(300)
'''


def stat(pid):
    try:
        with open('/proc/%d/stat' % pid, 'rb') as fh:
            raw = fh.read().decode()
    except OSError:
        return None
    rp = raw.rfind(')')
    rest = raw[rp + 2:].split()
    return {'pid': pid, 'comm': raw[raw.find('(') + 1:rp], 'state': rest[0],
            'ppid': int(rest[1])}


def alive(pid):
    st = stat(pid)
    return st is not None and st['state'] not in ('Z', 'X', 'x')


def case(name, use_prctl, mode=None):
    pidfile = os.path.join(SCRATCH, 'ctrl-%s.pid' % name)
    try:
        os.unlink(pidfile)
    except OSError:
        pass
    h = subprocess.Popen([sys.executable, '-c', HARNESS, pidfile,
                          mode or ('1' if use_prctl else '0')],
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, start_new_session=True)
    deadline = time.monotonic() + 10
    child = None
    while time.monotonic() < deadline:
        if os.path.exists(pidfile):
            with open(pidfile) as fh:
                txt = fh.read().strip()
            if txt:
                child = int(txt)
                break
        time.sleep(0.005)
    rec = {'case': name, 'pdeathsig_requested': use_prctl,
           'prctl_holder': {'1': 'child-before-exec',
                            '2': 'parent-before-fork',
                            '0': 'none'}[mode or ('1' if use_prctl else '0')],
           'harness_pid': h.pid, 'child_pid': child}
    if child is None:
        rec['failure'] = 'no child pid'
        h.kill()
        return rec
    # child is reparented to the harness (fork -> parent harness). Confirm chain.
    rec['before'] = {'harness': stat(h.pid), 'child': stat(child),
                     'child_alive': alive(child)}
    t_kill = time.monotonic()
    os.kill(h.pid, signal.SIGKILL)
    h.wait(timeout=10)
    death = None
    deadline = t_kill + 3.0
    while time.monotonic() < deadline:
        if not alive(child):
            death = {'latency_ms': round((time.monotonic() - t_kill) * 1000),
                     'final_stat': stat(child)}
            break
        time.sleep(0.0005)
    rec['kill'] = {'signal': 'SIGKILL', 'sent_to': h.pid,
                   'at_monotonic': t_kill}
    rec['child_died'] = death is not None
    rec['death'] = death
    rec['child_alive_after_500ms'] = alive(child)
    if alive(child):
        rec['cleanup'] = 'conductor SIGKILLed the survivor it spawned'
        os.kill(child, signal.SIGKILL)
        time.sleep(0.05)
    rec['child_state_final'] = stat(child)
    return rec


def main():
    out = {'positive': case('positive-child-side-pdeathsig', True),
           'negative': case('negative-no-pdeathsig', False),
           'parent_side': case('naive-parent-side-pdeathsig', True, '2')}
    with open(os.path.join(SCRATCH, 'out', 'pdeathsig-control.json'), 'w') as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps({
        'positive_child_died': out['positive']['child_died'],
        'positive_latency_ms': (out['positive']['death'] or {}).get('latency_ms'),
        'negative_child_survived_kill': not out['negative']['child_died'],
        'parent_side_child_survived_kill': not out['parent_side']['child_died'],
        'parent_side_latency_ms': (out['parent_side']['death'] or {}).get('latency_ms'),
        'negative_child_alive_after_500ms': out['negative']['child_alive_after_500ms'],
    }, indent=1, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
