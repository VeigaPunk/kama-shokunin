#!/usr/bin/env python3
"""E12KillSwitch driver — SIGKILL the completion tool during its hold window and
observe the pdeathsig teardown of the llama-server child and its port.

Writes out/teardown-receipt.json. Never contacts a registered consumer port:
the only server is the one tools/kama-completion-live.py itself spawns on a port it
picked as free + unregistered; the driver reads /proc, `ss` and does one bind test.
"""
import importlib.util
import json
import os
import re
import signal
import socket
import subprocess
import sys
import time

LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'
TOOL = os.path.join(LANE, 'tools', 'kama-completion-live.py')
SCRATCH = os.path.dirname(os.path.abspath(__file__))
LABEL = os.environ.get('E12_LABEL', 'run1')
# per-attempt dirs: a leftover ready.json from an earlier run in the same dir is
# the documented stale-witness hazard, so the driver never reuses a hold dir
HOLD = os.path.join(SCRATCH, 'hold-%s-%d' % (LABEL, os.getpid()))
WORK = os.path.join(SCRATCH, 'work-%s-%d' % (LABEL, os.getpid()))
OUT = os.path.join(SCRATCH, 'out')

_spec = importlib.util.spec_from_file_location(
    'kama_llamacpp_live', os.path.join(LANE, 'tools', 'kama-llamacpp-live.py'))
_live = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_live)


def proc_stat(pid):
    """Kernel truth for one pid: state char, ppid, pgrp, sid, comm."""
    try:
        with open('/proc/%d/stat' % pid, 'rb') as fh:
            raw = fh.read().decode('utf-8', 'replace')
    except (FileNotFoundError, ProcessLookupError):
        return None
    except OSError:
        return None
    rp = raw.rfind(')')
    comm = raw[raw.find('(') + 1:rp]
    rest = raw[rp + 2:].split()
    # rest[0]=state rest[1]=ppid rest[2]=pgrp rest[3]=session
    # stat field 52 = exit_code (kernel >= 4.1); rest index 49
    exit_code = int(rest[49]) if len(rest) > 49 else None
    return {'pid': pid, 'comm': comm, 'state': rest[0], 'ppid': int(rest[1]),
            'pgrp': int(rest[2]), 'sid': int(rest[3]),
            'exit_code': exit_code,
            'exit_signal': (exit_code & 0x7f) if exit_code is not None else None}


def alive(pid):
    st = proc_stat(pid)
    return st is not None and st['state'] not in ('Z', 'X', 'x')


def proc_exe(pid):
    try:
        return os.readlink('/proc/%d/exe' % pid)
    except OSError as exc:
        return 'ERR:%s' % exc


def proc_cmdline(pid):
    try:
        with open('/proc/%d/cmdline' % pid, 'rb') as fh:
            return fh.read().decode('utf-8', 'replace').split('\x00')[:-1]
    except OSError:
        return []


def snapshot_tree(root_pid):
    """root_pid plus every descendant, straight from /proc (no shell)."""
    rows = []
    for name in os.listdir('/proc'):
        if not name.isdigit():
            continue
        st = proc_stat(int(name))
        if st is not None:
            rows.append(st)
    by_parent = {}
    for st in rows:
        by_parent.setdefault(st['ppid'], []).append(st)
    out, stack = [], [root_pid]
    while stack:
        pid = stack.pop()
        st = next((r for r in rows if r['pid'] == pid), None)
        if st is None:
            continue
        out.append(st)
        stack.extend(c['pid'] for c in by_parent.get(pid, []))
    return out


def ss_dump(port):
    cp = subprocess.run(['ss', '-ltnp', 'sport', '= :%d' % port],
                        capture_output=True, text=True)
    return cp.stdout.strip()


def port_free_by_bind(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('127.0.0.1', port))
        return True, None
    except OSError as exc:
        return False, '%s:%s' % (type(exc).__name__, exc.strerror)
    finally:
        s.close()


def _probe(port, path):
    """_live.http_get result with its bytes body decoded so the receipt dumps."""
    got = _live.http_get(port, path, timeout=2.0)
    body = got.get('body')
    if isinstance(body, (bytes, bytearray)):
        body = body.decode('utf-8', 'replace')
    return {'status': got.get('status'), 'error': got.get('error'),
            'body': body}


def registry_tokens_for(port):
    """Every registry row whose text mentions this port as an explicit token."""
    path = os.path.join(LANE, 'registry', 'endpoint-consumers.tsv')
    hits = []
    pat = re.compile(r'(?:^|[^0-9])%d(?:[^0-9]|$)' % port)
    try:
        with open(path, 'r') as fh:
            for i, line in enumerate(fh, 1):
                if line.startswith('#') or not line.strip():
                    continue
                if pat.search(line):
                    hits.append('%d:%s' % (i, line.strip()[:120]))
    except OSError as exc:
        hits.append('ERR:%s' % exc)
    return hits


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(WORK, exist_ok=True)
    rec = {'driver': 'E12KillSwitch/driver.py', 'lane': LANE, 'tool': TOOL,
           'scratch': SCRATCH, 'started_monotonic': time.monotonic(),
           'started_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    tool_out = open(os.path.join(OUT, 'tool-%s.stdout' % LABEL), 'wb')
    argv = [sys.executable, TOOL, '--work', WORK, '--hold-dir', HOLD,
            '--out', os.path.join(OUT, 'tool-receipt-%s.json' % LABEL),
            '--hold-timeout', '180', '--nonce', 'e12-killswitch-r62']
    rec['tool_argv'] = argv
    t0 = time.monotonic()
    proc = subprocess.Popen(argv, stdout=tool_out, stderr=subprocess.STDOUT,
                            cwd=SCRATCH, start_new_session=True,
                            stdin=subprocess.DEVNULL)
    rec['tool_pid'] = proc.pid
    rec['tool_pid_stat_at_spawn'] = proc_stat(proc.pid)

    ready_path = os.path.join(HOLD, 'ready.json')
    hold_path = os.path.join(HOLD, 'hold.json')
    deadline = t0 + 120.0
    ready = None
    spawn_wall = time.time()
    rejected = []
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            rec['failure'] = 'tool exited before hold window (rc=%s)' % proc.returncode
            break
        if os.path.exists(ready_path):
            try:
                with open(ready_path) as fh:
                    cand = json.load(fh)
                cst = proc_stat(cand.get('pid'))
                fresh = (os.stat(ready_path).st_mtime >= spawn_wall - 0.001
                         and cst is not None and cst.get('ppid') == proc.pid)
                if fresh:
                    ready = cand
                    break
                rejected.append({'ready': cand,
                                 'reason': 'stale/unbound announcement '
                                           '(not this tool pid, or written '
                                           'before this spawn)',
                                 'child_stat': cst})
            except (ValueError, OSError):
                pass
        time.sleep(0.005)
    rec['rejected_announcements'] = rejected
    rec['ready_latency_ms'] = round((time.monotonic() - t0) * 1000)
    if not ready:
        tool_out.close()
        rec['failure'] = rec.get('failure') or 'no ready.json within 120s'
        with open(os.path.join(OUT, 'teardown-receipt-%s.json' % LABEL), 'w') as fh:
            json.dump(rec, fh, indent=1, sort_keys=True)
        print(json.dumps(rec, indent=1, sort_keys=True))
        return 3
    rec['ready'] = ready
    child_pid = ready['pid']
    port = ready['port']
    rec['hold_json'] = None
    if os.path.exists(hold_path):
        with open(hold_path) as fh:
            rec['hold_json'] = json.load(fh)

    # the hold window must actually be open and serving before the kill
    gate_deadline = time.monotonic() + 20.0
    while time.monotonic() < gate_deadline:
        if _live.port_owned_by(child_pid, port):
            break
        time.sleep(0.005)

    before = {
        'at_monotonic': time.monotonic(),
        'tool_stat': proc_stat(proc.pid),
        'child_stat': proc_stat(child_pid),
        'child_exe': proc_exe(child_pid),
        'child_cmdline': proc_cmdline(child_pid),
        'child_descendants': [s for s in snapshot_tree(child_pid)
                              if s['pid'] != child_pid],
        'tree': snapshot_tree(proc.pid),
        'listen_inodes': sorted(_live._listen_inodes(port)),
        'port_owned_by_child': _live.port_owned_by(child_pid, port),
        'ss': ss_dump(port),
        'bind_free_before_kill': port_free_by_bind(port),
        'registry_port_tokens': registry_tokens_for(port),
        'hold_dir_listing': sorted(os.listdir(HOLD)),
        # the server must be ANSWERING at kill time, not merely listening
        'live_health': _probe(port, '/health'),
        'live_models': _probe(port, '/v1/models'),
        'child_ppid_equals_tool': (proc_stat(child_pid) or {}).get('ppid') == proc.pid,
        'child_start_vs_kill': 'kill lands inside the --hold-dir window (ready.json + hold.json present)',
    }
    rec['before_kill'] = before
    rec['port'] = port
    rec['child_pid'] = child_pid

    # ---- the kill: SIGKILL the tool (parent) only, never the child ----------
    t_kill = time.monotonic()
    os.kill(proc.pid, signal.SIGKILL)
    rec['kill'] = {'signal': 'SIGKILL', 'sent_to': proc.pid,
                   'at_monotonic': t_kill,
                   'sent_to_child': False}
    proc.wait(timeout=10)
    rec['kill']['tool_returncode'] = proc.returncode
    rec['kill']['tool_reaped_ms'] = round((time.monotonic() - t_kill) * 1000)

    # ---- observe the child: alive -> dead ----------------------------------
    death = None
    deadline = t_kill + 10.0
    while time.monotonic() < deadline:
        st = proc_stat(child_pid)
        if st is None or st['state'] in ('Z', 'X', 'x'):
            death = {'pid': child_pid, 'at_monotonic': time.monotonic(),
                     'latency_ms': round((time.monotonic() - t_kill) * 1000),
                     'final_stat': st}
            break
        time.sleep(0.0005)
    if death and death['final_stat'] is None:
        death['final_stat'] = 'reaped before the zombie could be sampled'
    rec['child_death'] = death or {'pid': child_pid, 'still_alive': True}

    # ---- observe the port: listening inodes -> empty, then bindable --------
    port_gone = None
    deadline = t_kill + 10.0
    while time.monotonic() < deadline:
        now = sorted(_live._listen_inodes(port))
        if not now:
            port_gone = {'at_monotonic': time.monotonic(),
                         'latency_ms': round((time.monotonic() - t_kill) * 1000)}
            break
        time.sleep(0.0005)
    rec['port_release'] = port_gone or {'still_listening': True,
                                        'inodes': sorted(_live._listen_inodes(port))}
    time.sleep(0.2)
    rec['after_kill'] = {
        'at_monotonic': time.monotonic(),
        'tool_stat': proc_stat(proc.pid),
        'child_stat': proc_stat(child_pid),
        'child_descendants': snapshot_tree(child_pid),
        'tree_root_snapshot': snapshot_tree(proc.pid),
        'listen_inodes': sorted(_live._listen_inodes(port)),
        'port_owned_by_child': _live.port_owned_by(child_pid, port),
        'ss': ss_dump(port),
        'bind_free_after_kill': port_free_by_bind(port),
        'connect_probe': None,
        'hold_dir_listing': sorted(os.listdir(HOLD)),
    }
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.settimeout(1.0)
    try:
        conn.connect(('127.0.0.1', port))
        rec['after_kill']['connect_probe'] = 'CONNECTED (still serving)'
    except OSError as exc:
        rec['after_kill']['connect_probe'] = '%s:%s' % (type(exc).__name__,
                                                        exc.strerror)
    finally:
        conn.close()

    # evidence files: any child that was not ours must not be reported as ours
    for name in ('server.log',):
        p = os.path.join(WORK, name)
        if os.path.exists(p):
            with open(p, 'rb') as fh:
                fh.seek(max(0, os.path.getsize(p) - 2000))
                rec['server_log_tail'] = fh.read().decode('utf-8', 'replace')
    tool_out.close()
    with open(os.path.join(OUT, 'tool-%s.stdout' % LABEL), 'rb') as fh:
        rec['tool_stdout'] = fh.read().decode('utf-8', 'replace')[-2000:]

    rec['outcome'] = {
        'child_died': bool(death) and not rec['child_death'].get('still_alive', False),
        'child_death_latency_ms': rec['child_death'].get('latency_ms'),
        'port_freed': bool(port_gone),
        'port_release_latency_ms': (rec['port_release'] or {}).get('latency_ms'),
        'port_bindable_after': rec['after_kill']['bind_free_after_kill'][0],
        'listener_after': bool(rec['after_kill']['listen_inodes']),
    }
    with open(os.path.join(OUT, 'teardown-receipt-%s.json' % LABEL), 'w') as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)
    print(json.dumps(rec['outcome'], indent=1, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
