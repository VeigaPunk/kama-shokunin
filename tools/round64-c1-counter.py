#!/usr/bin/env python3
"""Round-64 C1 counter: the process that answers is the pinned llama-server.

Usage: python3 tools/round64-c1-counter.py --repo REPO --tip REV --work DIR

Predicate as amended (AMENDMENT 1, .ufo/waves/round-64/controls/freeze.txt;
the original sentence is kept there verbatim):
  C1-r64: at the tip, the byte-pinned tools/kama-completion-live.py (schema
  kama-completion-live/v3) runs one counter-opened hold-mode live request-
  plane lifecycle on the pinned llama.cpp fixture, sending the request
  (prompt, n_predict, seed) the counter drew for this run, and the counter -
  from procfs and its own code alone, loading nothing from the tip - binds
  the process that answers to the pinned server: every holder of the
  run-port listener is the hold pid, its /proc/<pid>/exe re-hashes to the
  pinned llama-server digest at the server path the counter chose, its argv
  is exactly the tool's argv, its initial environment holds only the
  counter's own PATH/HOME/LANG/LC_ALL values, its mapped files are the
  pinned set, it shares the counter's namespaces, is not traced and is not
  stopped, it is a descendant of the tool process started after the tool
  did, the hold.json is fresh, and teardown (the holder gone, the port
  closed) is observed by the counter after the counter's own release; the
  held child's answers to two outside probes drawn at random per run
  (prompt length and n_predict), and the receipt's own request and answer,
  agree with a reference pinned server the counter itself starts; and all
  91 targeted controls - including live forged tools (the round-63
  forgeries replayed, a detached server, a forwarding proxy, a canned
  answerer, stale holds, a preload, a path-copied server, a replayed
  receipt) - are each rejected by the check each names, family by family
  at the declared counts, and the counter's own evaluator judges all 8
  planted cases correctly, errors=0.

The counter never trusts receipt-claimed results and imports nothing from
the tip. A control counts as rejected only when the failure set of its
re-score contains the named check and stays within the cap (5; 30 for the
envelope break; 14 for a live patched-tool forgery); a live fake tool that
holds a genuine receipt copy has no cap but must show no receipt-level
failure. Output: one line, exit 0 iff met; a --work that already holds
files exits 2 (`work-reused`). Every scratch path is under --work.
"""
import argparse
import hashlib
import json
import math
import os
import random
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

MODEL_SHA = '270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d'
SERVER_SHA = 'b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804'
ALIAS = 'kama-completion-probe'
FP_RE = re.compile(r'^b\d+-[0-9a-f]{9,40}$')
SCHEMA = 'kama-completion-live/v3'
PROMPT = 'The cat sat on the'   # the tool's default prompt (round-63 value)
EXPECT_EVAL_SELFTEST = 8
MAX_COLLATERAL = 5      # failing checks a one-field control may cause
ENVELOPE_CAP = 30       # an envelope failure legitimately cascades
SCENARIO_CAP = 14       # a live forged tool cascades through its run
EXPECT_FAMILIES = {
    'stale': 1, 'log': 1, 'tamper': 8, 'predead': 1, 'sigterm': 1,
    'hold': 1, 'outside': 1, 'hdr': 2, 'trunc': 2, 'timing': 4,
    'shape': 4, 'idcr': 3, 'ptok': 2, 'reqbind': 2, 'listener': 1,
    'digest': 1, 'schema': 1, 'witness': 5,
    # round-64 families
    'bind': 30, 'runfield': 4, 'detach': 1, 'forge': 3, 'proxy': 1,
    'canned': 1, 'stalehold': 2, 'preload': 1, 'pathcopy': 1, 'relabel': 1,
    'receiptbind': 4, 'replay': 1,
}
EXPECT_CONTROLS = sum(EXPECT_FAMILIES.values())
STORED = {
    'health_ready', 'models_alias_id', 'props_alias', 'completion_envelope',
    'completion_headers', 'completion_untruncated', 'completion_choice_shape',
    'completion_finish_reason', 'completion_model_id',
    'completion_fingerprint', 'completion_id_created', 'completion_usage',
    'completion_timings', 'completion_prompt_tokens',
    'completion_request_bound', 'completion_deterministic',
    'bad_request_graded', 'listener_owned', 'listener_holders_pinned',
    'model_digest', 'server_digest', 'hold_released', 'teardown_clean',
    'teardown_port_closed'}
RECEIPT_LEVEL = STORED | {'schema', 'nonce_match', 'verdict'}
RECEIPT_BIND = {'receipt_req', 'receipt_ref_text', 'receipt_ref_usage'}
# sha256 of every library file in the pinned llama.cpp b11755 release
# directory (the server's own mappings must be members of this table)
LIBS = {
    'libggml-base.so.0.27.0':
        '574946133f3fd58a87cf4c7b70955a51fe71a6b7841b75eb419074d56b791e2f',
    'libggml-cpu-alderlake.so':
        '147bafeeb86639404750bcd20823cfd46520790dcffe72b03ae92211adc4a0a1',
    'libggml-cpu-cannonlake.so':
        'ecf0a02e19adc1e9996cd0bc0dde60de132470a2ecd326aa53223951705757ef',
    'libggml-cpu-cascadelake.so':
        '81cafe6a6ce3023f12a0d6bfea5581ba21bfaaf31ce2404a9e81bca874497b6b',
    'libggml-cpu-cooperlake.so':
        '3a7cc9d0711ce5699a4b7941fef6031ebc52bc6735200cd80848f8b7f029f4df',
    'libggml-cpu-haswell.so':
        '476b43e924d1b956a8e0b41b399d57a1a52cadfb8b6d4e23efa9e2806389d356',
    'libggml-cpu-icelake.so':
        'aec99e3c63c781ecc33a4531933781c2eeeac30178eb480c79c5d76aeb715623',
    'libggml-cpu-ivybridge.so':
        'a4f945a8472a47259d2995cac73bb7f9616cf24003e7a0e7a7470e4f7d345c53',
    'libggml-cpu-piledriver.so':
        'ffe1ff67e508a82a796174ee8179ddabaf0796fc433bab5c866942987da3cd83',
    'libggml-cpu-sandybridge.so':
        'e30b3764002a27237c3fdca7daff26459e4545e904a443ed0eee998348aad08b',
    'libggml-cpu-sapphirerapids.so':
        '084aa87d46db0b252416b10ce82248441408b0617c8d302610c732ad38fb22d2',
    'libggml-cpu-skylakex.so':
        '89b02a4e0eaa40a165d1ac30b2e6342f3dd302cc17dca07188c6e02795e37d07',
    'libggml-cpu-sse42.so':
        'ca3dd82f297aa34907cb6f979c17af240bcd9e4eb886da7319a1a1394a736bdd',
    'libggml-cpu-x64.so':
        '6643e910752ae8724d967824c1834bf8bcfa3b08ff614f6826085f07bc6cc96d',
    'libggml-cpu-zen4.so':
        '65f7908e0fa582ef863a629e3b450f48e604a57ed69fc9f62cb3c74d7afef475',
    'libggml-rpc.so':
        'e28139e2d982fb057b88d243e5b2e9d72c52f8b98ae910b1cf751240ef1f9803',
    'libggml.so.0.27.0':
        '8643a58bb37af6fb153e2ea98b48efa227855725ee51c05f4ca76b9867956463',
    'libllama-batched-bench-impl.so':
        'a69a1abbca090c7ab3fa286adcb9fa51b710730c7950c02796a9a84197ef00c7',
    'libllama-bench-impl.so':
        'e4ca59722bb4c5567fde2d5e07deb2116211e88d6d1afc43deabc5278a575ddb',
    'libllama-cli-impl.so':
        '085ffb43408aac8202d35dcd24e0fb3800e1d952925f862c0de3d6fd2f13bb82',
    'libllama-common.so.0.7.0':
        '3270bc668b9377617bad776d64712b3ee1bc22f1539a4cc143b546988e5fe37e',
    'libllama-completion-impl.so':
        '0d3d7ae4cdeafbce5d765f9027371506f5205eeb3203553e463035bc4babae23',
    'libllama-fit-params-impl.so':
        '397ce456786d0c161b14dd0ee225378d1f1ff875cbc428d32fda7dcaf15e306b',
    'libllama-perplexity-impl.so':
        '357dc3ef0ebe6fe69b35c965db701452f44cc08a01f77a22c609b4aa96afbca9',
    'libllama-quantize-impl.so':
        '8dd43c1fb15f2e6096237a5cc3aa52694b04978c176f10db28c27d15d6c1adcc',
    'libllama-server-impl.so':
        'e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed',
    'libllama.so.0.7.0':
        '983e1a2a037c6e6a393848e3be9f5e6e00d7ee3022aca4c2f17ed093de819fb6',
    'libmtmd.so.0.7.0':
        'adbb5fce4dcdcd60abfca9d80a2245251cf71aaa0045937f2a6f1be9f9b94721',
    'llama-server': SERVER_SHA,
}
SYSTEM_PREFIXES = ('/usr/lib/', '/lib/', '/usr/lib64/', '/lib64/')
SYSTEM_FILES = ('/etc/ld.so.cache',)
VOCAB = ('river stone lamp cloud garden window paper silver copper forest '
         'bridge candle mirror harbor meadow thunder velvet anchor ribbon '
         'lantern orchard pebble quartz saddle tunnel violet whistle').split()
NONCE = ''
TOOL_REQ = {}   # the request the counter told the tool to send (per run)
_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
_HASH_CACHE = {}
_TOOL_ENV_KEYS = ('PATH', 'HOME', 'LANG', 'LC_ALL', 'TMPDIR')
# the keys the tool's server child may inherit (tools/kama-completion-live.py
# filters its own environment; the counter passes none of the others)
TOOL_CHILD_ENV = ('PATH', 'HOME', 'LANG', 'LC_ALL')


def git(repo, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    return subprocess.run(['git', '-C', str(repo), *args],
                          capture_output=True, env=env)


def blob(repo, rev, path):
    p = git(repo, 'show', f'{rev}:{path}')
    return p.stdout if p.returncode == 0 else None


def sha256_b(b):
    return hashlib.sha256(b).hexdigest()


def sha256_path(path, cache=False):
    """sha256 of a file, hashed afresh on every call (wave-b RV02 D9: a
    path-keyed cache returned the old digest after the file was replaced).
    `cache` is accepted for call-site compatibility and ignored."""
    try:
        h = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(1 << 20), b''):
                h.update(chunk)
        return h.hexdigest()
    except (OSError, TypeError):
        return None


def jbody(cap):
    try:
        return json.loads((cap or {}).get('body', ''))
    except (ValueError, TypeError):
        return None


def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def is_num(v):
    return (isinstance(v, (int, float)) and not isinstance(v, bool)
            and math.isfinite(v))


def ctype_json(headers):
    ct = (headers or {}).get('content-type') or ''
    return ct.split(';')[0].strip().lower() == 'application/json'


def http(port, path, payload=None, timeout=10.0):
    """One loopback request on the proxy-free opener. Returns
    (status|None, headers, body_text, request_bytes|None)."""
    data = None if payload is None else json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        f'http://127.0.0.1:{port}{path}', data=data,
        headers={'Content-Type': 'application/json'} if data else {},
        method='POST' if data is not None else 'GET')
    try:
        with _OPENER.open(req, timeout=timeout) as r:
            return (r.status, {k.lower(): v for k, v in r.headers.items()},
                    r.read().decode('utf-8', 'replace'), data)
    except urllib.error.HTTPError as e:
        return (e.code, {k.lower(): v for k, v in (e.headers or {}).items()},
                e.read().decode('utf-8', 'replace'), data)
    except Exception as e:
        return None, {}, type(e).__name__, data


# ----------------------------------------------------------- procfs plane #
# Everything below is the counter's own procfs reading (proc_pid_fd(5),
# proc_net_tcp rst, proc_pid_exe(5), proc_pid_maps(5), proc_pid_stat(5),
# proc_pid_environ(5), proc_pid_cmdline(5)); nothing is imported from the
# tree under judgment.

def _hex_loopback(addr_hex):
    a = addr_hex.upper()
    if len(a) == 8:
        return a == '0100007F'
    if len(a) == 32:
        return a in ('00000000000000000000000001000000',
                     '0000000000000000FFFF00000100007F')
    return False


def listeners(port):
    """[(inode, loopback)] for every LISTEN socket on `port` (any address)."""
    out = []
    for path in ('/proc/net/tcp', '/proc/net/tcp6'):
        try:
            with open(path, encoding='ascii') as fh:
                next(fh, None)
                for line in fh:
                    f = line.split()
                    if len(f) < 10 or f[3] != '0A':
                        continue
                    addr, _, p = f[1].partition(':')
                    if int(p, 16) != port:
                        continue
                    out.append((int(f[9]), _hex_loopback(addr)))
        except (OSError, ValueError, IndexError):
            continue
    return out


def holder_pids(inodes, retries=4):
    """(pids holding a socket:[inode] fd, pids whose fd table stayed
    unreadable, any uid). A process in the middle of execve is briefly
    unreadable, so an unreadable table is re-read a few times before the
    caller grades it (host churn made a single read flake). Unreadable
    tables that persist are graded by the caller."""
    wanted = {f'socket:[{i}]' for i in inodes}

    def scan(pid):
        """True: holds it; False: readable, does not; None: unreadable;
        False for a pid that vanished."""
        try:
            fds = os.listdir(f'/proc/{pid}/fd')
        except PermissionError:
            return None
        except OSError:
            return False
        for fd in fds:
            try:
                if os.readlink(f'/proc/{pid}/fd/{fd}') in wanted:
                    return True
            except OSError:
                continue
        return False

    pids, unreadable = set(), set()
    for name in os.listdir('/proc'):
        if not name.isdigit():
            continue
        pid = int(name)
        r = scan(pid)
        if r is True:
            pids.add(pid)
        elif r is None:
            unreadable.add(pid)
    for _ in range(retries):
        if not unreadable:
            break
        time.sleep(0.05)
        for pid in sorted(unreadable):
            r = scan(pid)
            if r is True:
                pids.add(pid)
                unreadable.discard(pid)
            elif r is False:
                unreadable.discard(pid)
    return pids, unreadable


def stat_fields(pid):
    """(ppid, starttime_ticks) from /proc/<pid>/stat, (None, None) if gone."""
    try:
        s = open(f'/proc/{pid}/stat', encoding='ascii').read()
        rest = s[s.rindex(')') + 2:].split()
        return int(rest[1]), int(rest[19])
    except (OSError, ValueError, IndexError):
        return None, None


def ppid_chain(pid, limit=8):
    chain = []
    cur = pid
    for _ in range(limit):
        pp, _ = stat_fields(cur)
        if pp is None or pp <= 0:
            break
        chain.append(pp)
        cur = pp
    return chain


def read_maps(pid, server_dir):
    """Distinct file-backed mappings of a process: path, deleted flag and
    sha256 of the file when it lies under the server directory."""
    out, seen = [], set()
    try:
        lines = open(f'/proc/{pid}/maps', encoding='utf-8',
                     errors='replace').read().splitlines()
    except OSError:
        return None
    for ln in lines:
        parts = ln.split(None, 5)
        if len(parts) < 6:
            continue
        path = parts[5].strip()
        if path in seen:
            continue
        seen.add(path)
        deleted = path.endswith(' (deleted)')
        real = path[:-len(' (deleted)')] if deleted else path
        sha = None
        if (not deleted and real.startswith('/')
                and os.path.realpath(real).startswith(
                    server_dir.rstrip('/') + '/')):
            sha = sha256_path(os.path.realpath(real))
        out.append({'path': path, 'deleted': deleted, 'sha256': sha,
                    'dev': parts[3], 'inode': parts[4]})
    return out


REF_FILES = []   # file-backed mappings of the counter's reference server


def file_set(ms):
    """Sorted (path, dev, inode) of every file-backed mapping."""
    return sorted({(m['path'], m.get('dev'), m.get('inode'))
                   for m in ms or [] if str(m.get('path', '')).startswith('/')})


NS_NAMES = ('mnt', 'pid', 'net', 'user', 'ipc', 'uts')


def ns_of(pid):
    """Namespace identities of a process (proc_pid_ns links), None when
    unreadable."""
    try:
        return {n: os.readlink(f'/proc/{pid}/ns/{n}') for n in NS_NAMES}
    except OSError:
        return None


def holder_record(pid, server_dir):
    """One holder's procfs record. None fields mean unreadable."""
    rec = {'pid': pid}
    try:
        rec['exe'] = os.readlink(f'/proc/{pid}/exe')
        rec['exe_sha256'] = sha256_path(f'/proc/{pid}/exe')
    except OSError:
        rec['exe'] = rec['exe_sha256'] = None
    try:
        raw = open(f'/proc/{pid}/cmdline', 'rb').read()
        rec['cmdline'] = [a.decode('utf-8', 'replace')
                          for a in raw.split(b'\0') if a != b'']
    except OSError:
        rec['cmdline'] = None
    try:
        raw = open(f'/proc/{pid}/environ', 'rb').read()
        env = {}
        for e in raw.split(b'\0'):
            if e:
                k, _, v = e.partition(b'=')
                env[k.decode('utf-8', 'replace')] = v.decode(
                    'utf-8', 'replace')
        rec['environ'] = env
    except OSError:
        rec['environ'] = None
    try:
        st = open(f'/proc/{pid}/status', encoding='utf-8',
                  errors='replace').read()
        m = re.search(r'^State:\s+(\S)', st, re.M)
        rec['state'] = m.group(1) if m else None
        m = re.search(r'^TracerPid:\s+(\d+)', st, re.M)
        rec['tracer_pid'] = int(m.group(1)) if m else None
    except OSError:
        rec['state'] = rec['tracer_pid'] = None
    rec['ns'] = ns_of(pid)
    rec['maps'] = read_maps(pid, server_dir)
    pp, ticks = stat_fields(pid)
    rec['ppid'] = pp
    rec['start_ticks'] = ticks
    rec['ppids'] = ppid_chain(pid)
    return rec


def collect(port, hold_doc, hold_mtime_ns, t0_ns, tool_pid, tool_ticks,
            server_path, model_path):
    """The counter's own snapshot of who holds the run-port listener."""
    ls = listeners(port)
    pids, unreadable = holder_pids([i for i, _ in ls])
    sdir = os.path.dirname(server_path)
    return {
        'port': port, 'hold_pid': (hold_doc or {}).get('pid'),
        'hold_port': (hold_doc or {}).get('port'),
        'hold_schema': (hold_doc or {}).get('schema'),
        'hold_mtime_ns': hold_mtime_ns, 't0_ns': t0_ns,
        'collected_ns': time.time_ns(),
        'tool_pid': tool_pid, 'tool_start_ticks': tool_ticks,
        'server_path': server_path, 'model_path': model_path,
        'self_ns': ns_of(os.getpid()),
        'expect_env': {k: os.environ[k] for k in TOOL_CHILD_ENV
                       if k in os.environ},
        'listeners': [{'inode': i, 'loopback': lo} for i, lo in ls],
        'unreadable_own': sorted(
            p for p in unreadable
            if (start_ticks_of(p) or 0) >= (tool_ticks or 0)),
        'unreadable_old': len(unreadable),
        'holders': [holder_record(p, sdir) for p in sorted(pids)],
    }


def _flag_values(argv, flag):
    out = []
    for i, a in enumerate(argv or []):
        if a == flag and i + 1 < len(argv):
            out.append(argv[i + 1])
        elif a.startswith(flag + '='):
            out.append(a.split('=', 1)[1])
    return out


def grade_binding(raw):
    """Pure function of a raw procfs snapshot -> {check: bool}."""
    if not isinstance(raw, dict):
        return {k: False for k in BIND_CHECKS}
    hs = raw.get('holders') or []
    sp = raw.get('server_path')
    mp = raw.get('model_path')
    sdir = os.path.dirname(sp) if sp else ''
    out = {}
    ls = raw.get('listeners') or []
    out['bind_listener'] = bool(ls) and all(
        isinstance(x, dict) and x.get('loopback') is True for x in ls)
    hp = raw.get('hold_pid')
    out['bind_holders'] = bool(
        hs and is_int(hp) and {h.get('pid') for h in hs} == {hp}
        and not raw.get('unreadable_own')
        and raw.get('hold_port') == raw.get('port'))
    out['bind_exe'] = bool(hs) and all(
        h.get('exe') == sp and h.get('exe_sha256') == SERVER_SHA
        for h in hs)

    def argv_ok(h):
        a = h.get('cmdline')
        return (isinstance(a, list)
                and a == expected_argv(sp, mp, raw.get('port'))
                and sha256_path(mp) == MODEL_SHA)
    out['bind_argv'] = bool(hs) and all(argv_ok(h) for h in hs)

    def env_ok(h):
        e = h.get('environ')
        ex = raw.get('expect_env') or {}
        return isinstance(e, dict) and all(
            k in ex and e[k] == ex[k] for k in e)
    out['bind_env'] = bool(hs) and all(env_ok(h) for h in hs)
    sn = raw.get('self_ns')
    out['bind_ns'] = bool(hs and sn) and all(
        h.get('ns') == sn for h in hs)
    out['bind_trace'] = bool(hs) and all(
        h.get('tracer_pid') == 0 for h in hs)
    out['bind_state'] = bool(hs) and all(
        h.get('state') in ('S', 'R', 'D') for h in hs)

    def maps_ok(h):
        ms = h.get('maps')
        if not ms:
            return False
        for m in ms:
            p = m.get('path') or ''
            if m.get('deleted') or p.endswith('(deleted)'):
                return False
            if p.startswith('['):
                continue
            if p == '':
                continue
            if p in SYSTEM_FILES or p.startswith(SYSTEM_PREFIXES):
                continue
            real = os.path.realpath(p)
            if real == mp:
                continue
            if sdir and real.startswith(sdir.rstrip('/') + '/'):
                if LIBS.get(os.path.basename(real)) == m.get('sha256') \
                        and m.get('sha256'):
                    continue
                return False
            return False
        return True
    out['bind_maps'] = bool(hs) and all(maps_ok(h) for h in hs)
    tp = raw.get('tool_pid')
    out['bind_ancestry'] = bool(hs) and all(
        tp in (h.get('ppids') or []) for h in hs)
    tt = raw.get('tool_start_ticks')
    mt = raw.get('hold_mtime_ns')
    t0 = raw.get('t0_ns')
    now = raw.get('collected_ns')
    out['hold_fresh'] = bool(
        hs and is_int(mt) and is_int(t0) and mt > t0 and is_int(tt)
        and is_int(now) and mt <= now + 1_000_000_000
        and all(is_int(h.get('start_ticks')) and h['start_ticks'] >= tt
                for h in hs)
        and raw.get('hold_schema') == 'kama-completion-hold/v1')
    return out


def expected_argv(server_path, model_path, port):
    """The tool's exact child argv (tools/kama-completion-live.py, run())."""
    return [server_path, '--model', model_path, '--alias', ALIAS,
            '--port', str(port), '--host', '127.0.0.1', '-c', '512',
            '-t', '1']


BIND_CHECKS = ('bind_listener', 'bind_holders', 'bind_exe', 'bind_argv',
               'bind_env', 'bind_ns', 'bind_trace', 'bind_state',
               'bind_maps', 'bind_ancestry', 'hold_fresh')


def holders_signature(raw):
    return sorted((h.get('pid'), h.get('start_ticks'), h.get('exe_sha256'))
                  for h in (raw or {}).get('holders') or [])


# ---------------------------------------------------------------- grading #

def grade(receipt):
    """Recompute every receipt check from captured bytes and re-hashed
    files. Returns (recomputed {name: bool}, inconsistent [str])."""
    caps = receipt.get('captures') or {}
    td = receipt.get('teardown') or {}
    hold = receipt.get('hold') or {}
    stored = receipt.get('checks') or {}
    out = {}

    def cap(name):
        c = caps.get(name)
        if not isinstance(c, dict):
            return None
        body = c.get('body')
        if not isinstance(body, str):
            return None
        if sha256_b(body.encode()) != c.get('body_sha256'):
            return None
        return c

    out['schema'] = receipt.get('schema') == SCHEMA
    h = cap('health')
    out['health_ready'] = (h is not None and h.get('status') == 200
                           and h.get('body') == '{"status":"ok"}')
    m = cap('models')
    mj = jbody(m) if m else None
    ids = ([d.get('id') for d in mj.get('data') or [] if isinstance(d, dict)]
           if isinstance(mj, dict) else None)
    out['models_alias_id'] = (m is not None and m.get('status') == 200
                              and ids == [ALIAS])
    pr = cap('props')
    prj = jbody(pr) if pr else None
    out['props_alias'] = (isinstance(prj, dict)
                          and prj.get('model_alias') == ALIAS)
    c = cap('completion')
    cj = jbody(c) if c else None
    chs = cj.get('choices') if isinstance(cj, dict) else None
    ch0 = chs[0] if isinstance(chs, list) and chs and isinstance(
        chs[0], dict) else {}
    env = (c is not None and c.get('status') == 200
           and isinstance(cj, dict) and cj.get('object') == 'text_completion'
           and isinstance(chs, list) and len(chs) >= 1
           and isinstance(ch0.get('text'), str))
    out['completion_envelope'] = bool(env)
    out['completion_headers'] = bool(env and ctype_json(c.get('headers')))
    cl = (c.get('headers') or {}).get('content-length') if c else None
    out['completion_untruncated'] = bool(
        env and c.get('body_truncated') is False
        and is_int(c.get('body_bytes'))
        and c['body_bytes'] == len(c['body'].encode())
        and (cl is None or (str(cl).isdigit() and int(cl) == c['body_bytes'])))
    out['completion_choice_shape'] = bool(
        env and len(chs) == 1 and ch0.get('index') == 0
        and not isinstance(ch0.get('index'), bool)
        and ch0.get('text') != '' and ch0.get('logprobs') is None)
    out['completion_finish_reason'] = bool(
        env and ch0.get('finish_reason') in ('length', 'stop'))
    out['completion_model_id'] = bool(env and cj.get('model') == ALIAS)
    fp = cj.get('system_fingerprint') if isinstance(cj, dict) else None
    out['completion_fingerprint'] = bool(
        env and isinstance(fp, str) and FP_RE.match(fp))
    out['completion_id_created'] = bool(
        env and isinstance(cj.get('id'), str) and cj['id'] != ''
        and is_int(cj.get('created')) and cj['created'] > 1_000_000_000)
    u = (cj.get('usage') if isinstance(cj, dict) else None) or {}
    pd = u.get('prompt_tokens_details')
    out['completion_usage'] = bool(
        env and is_int(u.get('completion_tokens'))
        and is_int(u.get('prompt_tokens')) and is_int(u.get('total_tokens'))
        and u['completion_tokens'] >= 1 and u['prompt_tokens'] >= 1
        and u['total_tokens'] == u['completion_tokens'] + u['prompt_tokens']
        and isinstance(pd, dict) and is_int(pd.get('cached_tokens'))
        and 0 <= pd['cached_tokens'] <= u['prompt_tokens'])
    t = (cj.get('timings') if isinstance(cj, dict) else None) or {}
    out['completion_timings'] = bool(
        env and isinstance(t, dict) and is_int(t.get('predicted_n'))
        and t['predicted_n'] == u.get('completion_tokens')
        and is_int(t.get('cache_n')) and t['cache_n'] >= 0
        and is_int(t.get('prompt_n')) and t['prompt_n'] >= 0
        and is_num(t.get('predicted_ms')) and t['predicted_ms'] >= 0)
    tk = cap('tokenize')
    tkj = jbody(tk) if tk else None
    toks = tkj.get('tokens') if isinstance(tkj, dict) else None
    out['completion_prompt_tokens'] = bool(
        env and tk is not None and tk.get('status') == 200
        and isinstance(toks, list) and len(toks) >= 1
        and u.get('prompt_tokens') == len(toks))
    rb = c.get('request_body') if c else None
    try:
        rj = json.loads(rb) if isinstance(rb, str) else None
    except ValueError:
        rj = None
    out['completion_request_bound'] = bool(
        env and isinstance(rj, dict) and isinstance(rb, str)
        and sha256_b(rb.encode()) == c.get('request_sha256')
        and rj.get('prompt') == TOOL_REQ.get('prompt'))
    c2 = cap('completion2')
    c2j = jbody(c2) if c2 else None
    c2c = c2j.get('choices') if isinstance(c2j, dict) else None
    ch02 = c2c[0] if isinstance(c2c, list) and c2c and isinstance(
        c2c[0], dict) else {}
    out['completion_deterministic'] = bool(
        env and c2 is not None and c2.get('status') == 200
        and ch02.get('text') == ch0.get('text')
        and ch0.get('text') not in (None, '')
        and c2.get('request_sha256') == c.get('request_sha256'))
    b = cap('bad_request')
    bj = jbody(b) if b else None
    out['bad_request_graded'] = bool(
        b is not None and b.get('status') in (400, 500)
        and isinstance(bj, dict) and isinstance(bj.get('error'), dict))
    mdl = receipt.get('model') or {}
    srv = receipt.get('server') or {}
    out['model_digest'] = bool(
        mdl.get('sha256') == MODEL_SHA
        and sha256_path(mdl.get('path')) == MODEL_SHA)
    out['server_digest'] = bool(
        srv.get('sha256') == SERVER_SHA
        and sha256_path(srv.get('path')) == SERVER_SHA)
    rh = receipt.get('listener_holders')
    out['listener_holders_pinned'] = bool(
        isinstance(rh, list) and len(rh) == 1 and isinstance(rh[0], dict)
        and rh[0].get('pid') == receipt.get('child_pid')
        and rh[0].get('exe') == srv.get('path')
        and rh[0].get('exe_sha256') == SERVER_SHA)
    if 'hold_released' in stored:
        out['hold_released'] = bool(hold.get('released'))
    out['teardown_clean'] = bool(not td.get('child_pre_dead')
                                 and td.get('returncode') in (0, -15))
    out['teardown_port_closed'] = td.get('port_closed') is True
    out['nonce_match'] = bool(NONCE) and receipt.get('nonce') == NONCE

    inconsistent = [k for k, v in out.items()
                    if k in stored and stored[k].get('passed') is not None
                    and stored[k].get('passed') != v]
    if not STORED.issubset(stored):
        inconsistent.append('missing-checks')
    if set(stored) - STORED:
        inconsistent.append('unexpected-checks')
    return out, inconsistent


def probe_fails(p, ref, idx):
    """Failing live_* names for one outside probe against the reference
    server's answer to the same request."""
    f = set()
    if not isinstance(p, dict):
        return {f'live_probe{idx}'}
    if p.get('status') != 200:
        f.add('live_status')
    if not ctype_json(p.get('headers')):
        f.add('live_ctype')
    if p.get('object') != 'text_completion':
        f.add('live_object')
    if not (p.get('model') == ALIAS):
        f.add('live_model')
    if not (isinstance(p.get('text'), str) and p['text'] != ''):
        f.add('live_text')
    if not (is_int(p.get('created')) and p['created'] > 1e9
            and isinstance(p.get('id'), str) and p['id'] != ''):
        f.add('live_created')
    if not (isinstance(p.get('fingerprint'), str)
            and FP_RE.match(p['fingerprint'])):
        f.add('live_fp_shape')
    up, tc = p.get('usage_prompt_tokens'), p.get('tokenize_count')
    if not (is_int(up) and is_int(tc) and up == tc >= 1):
        f.add('live_ptok')
    n = p.get('n_predict')
    uc = p.get('usage_completion_tokens')
    pn, cn = p.get('timings_prompt_n'), p.get('timings_cache_n')
    if not (is_int(uc) and is_int(n) and 1 <= uc <= n
            and (p.get('finish_reason') != 'length' or uc == n)
            and p.get('timings_predicted_n') == uc
            and is_int(pn) and is_int(cn) and is_int(up)
            and pn + cn == up):
        f.add('live_run_field')
    r = ref[idx] if isinstance(ref, list) and idx < len(ref) else None
    if not (isinstance(r, dict) and p.get('text') == r.get('text')
            and isinstance(p.get('text'), str)):
        f.add('live_ref_text')
    if not (isinstance(r, dict) and p.get('usage_prompt_tokens')
            == r.get('usage_prompt_tokens')
            and p.get('usage_completion_tokens')
            == r.get('usage_completion_tokens')):
        f.add('live_ref_usage')
    return f


def score(receipt, witness, binding):
    """Re-score a receipt against the counter's outside witness and its own
    procfs binding. Returns {'met': bool, 'fails': set of check names}."""
    recomputed, inconsistent = grade(receipt)
    fails = {k for k, v in recomputed.items() if v is not True}
    fails |= {'inconsistent:' + i for i in inconsistent}
    if receipt.get('verdict') != 'REQUEST_OK':
        fails.add('verdict')
    stored = receipt.get('checks') or {}
    if (stored.get('listener_owned') or {}).get('passed') is not True:
        fails.add('listener_owned')
    w = witness or {}
    bnd = binding or {}
    caps = receipt.get('captures') or {}
    ccj = jbody(caps.get('completion') or {})
    cfp = ccj.get('system_fingerprint') if isinstance(ccj, dict) else None
    probes = w.get('probes') or []
    if len(probes) != 2:
        fails.add('live_probes')
    ref = w.get('ref') or []
    for i, p in enumerate(probes):
        fails |= probe_fails(p, ref, i)
    p0 = probes[0] if probes and isinstance(probes[0], dict) else {}
    if not (isinstance(cfp, str) and p0.get('fingerprint') == cfp):
        fails.add('live_fp_capture')
    if not (len(probes) == 2 and isinstance(probes[1], dict)
            and (p0.get('n_predict'), p0.get('sent_prompt'))
            != (probes[1].get('n_predict'), probes[1].get('sent_prompt'))):
        fails.add('live_probes')
    if not (w.get('server_sha256') == SERVER_SHA
            and (receipt.get('server') or {}).get('sha256') == SERVER_SHA):
        fails.add('live_server_sha')
    if w.get('model_sha256') != MODEL_SHA:
        fails.add('live_model_sha')
    if not (w.get('hold_pid') is not None
            and w.get('hold_pid') == receipt.get('child_pid')):
        fails.add('live_pid')
    if not (w.get('hold_port') is not None
            and w.get('hold_port') == receipt.get('port')):
        fails.add('live_port')
    # the receipt's own request/answer must be this run's: the counter chose
    # the tool's prompt, n_predict and seed, and its reference server
    # answered the same request (wave-b MT13/RV02 D1: a genuine child with a
    # replayed receipt passed a counter that bound only the live probes)
    tr = w.get('tool_req') or {}
    rt = w.get('ref_tool') or {}
    ccap = caps.get('completion') or {}
    try:
        rjs = json.loads(ccap.get('request_body') or '')
    except ValueError:
        rjs = None
    if not (isinstance(rjs, dict) and tr
            and rjs.get('prompt') == tr.get('prompt')
            and rjs.get('n_predict') == tr.get('n_predict')
            and rjs.get('seed') == tr.get('seed')):
        fails.add('receipt_req')
    chs0 = (ccj.get('choices') or [{}])[0] if isinstance(
        ccj, dict) and isinstance(ccj.get('choices'), list) else {}
    rtext = chs0.get('text') if isinstance(chs0, dict) else None
    if not (isinstance(rtext, str) and rtext != ''
            and rtext == rt.get('text')):
        fails.add('receipt_ref_text')
    ru = (ccj.get('usage') if isinstance(ccj, dict) else None) or {}
    if not (rt and ru.get('prompt_tokens') == rt.get('usage_prompt_tokens')
            and ru.get('completion_tokens')
            == rt.get('usage_completion_tokens')):
        fails.add('receipt_ref_usage')
    raw_a, raw_b = bnd.get('raw_a'), bnd.get('raw_b')
    for k, v in grade_binding(raw_a).items():
        if v is not True:
            fails.add(k)
    # the held child maps exactly the files (path, device, inode) the
    # counter's own reference server maps: a bind-mounted or copied model,
    # a swapped library or a dlopen-injected pinned-but-unloaded library
    # differs (wave-b MT06)
    rf = w.get('ref_files')
    hs_a = (raw_a or {}).get('holders') or []
    if not (rf and hs_a and all(
            [list(x) for x in file_set(h.get('maps'))] == rf
            for h in hs_a)):
        fails.add('bind_ref_files')
    gb = grade_binding(raw_b)
    for k in ('bind_state', 'bind_trace'):
        if gb.get(k) is not True:
            fails.add(k)
    if holders_signature(raw_a) != holders_signature(raw_b) or not raw_b:
        fails.add('bind_stable')
    rh = receipt.get('listener_holders')
    mine = sorted((h.get('pid'), h.get('exe'), h.get('exe_sha256'))
                  for h in (raw_a or {}).get('holders') or [])
    theirs = sorted((h.get('pid'), h.get('exe'), h.get('exe_sha256'))
                    for h in (rh if isinstance(rh, list) else [])
                    if isinstance(h, dict))
    if mine != theirs:
        fails.add('bind_claim')
    td = bnd.get('teardown') or {}
    if not (td.get('gone') is True and td.get('port_closed') is True):
        fails.add('teardown_observed')
    return {'met': not fails, 'fails': fails}


# ------------------------------------------------------- live run + probes #

def free_port():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    p = s.getsockname()[1]
    s.close()
    return p


def start_ticks_of(pid):
    return stat_fields(pid)[1]


def draw_requests(rng, nonce):
    """Three requests drawn per run (prompt length, n_predict, seed): two
    outside probes for the held child and the request the counter tells the
    tool to send. All distinct; the nonce is in every prompt."""
    out, used = [], set()
    while len(out) < 3:
        k = rng.randint(2, 24)
        n = rng.randint(3, 9)
        if (k, n) in used:
            continue
        used.add((k, n))
        words = ' '.join(rng.choice(VOCAB) for _ in range(k))
        out.append({'prompt': f'{nonce} {words}', 'n_predict': n,
                    'seed': rng.randint(1, 9999)})
    return out[:2], out[2]


def probe(port, req):
    payload = {'prompt': req['prompt'], 'n_predict': req['n_predict'],
               'temperature': 0.0, 'seed': req['seed'],
               'timings_per_token': False}
    st, hdr, body, raw = http(port, '/v1/completions', payload)
    try:
        wj = json.loads(body)
    except ValueError:
        wj = {}
    if not isinstance(wj, dict):
        wj = {}
    sent = json.loads(raw.decode())['prompt']
    chs = wj.get('choices')
    ch0 = chs[0] if isinstance(chs, list) and chs and isinstance(
        chs[0], dict) else {}
    tst, _, tbody, _ = http(port, '/tokenize',
                            {'content': sent, 'add_special': True})
    try:
        tj = json.loads(tbody)
    except ValueError:
        tj = {}
    toks = tj.get('tokens') if isinstance(tj, dict) else None
    usage = wj.get('usage') if isinstance(wj.get('usage'), dict) else {}
    tim = wj.get('timings') if isinstance(wj.get('timings'), dict) else {}
    return {
        'status': st, 'headers': hdr, 'object': wj.get('object'),
        'model': wj.get('model'), 'fingerprint': wj.get('system_fingerprint'),
        'text': ch0.get('text'), 'finish_reason': ch0.get('finish_reason'),
        'created': wj.get('created'), 'id': wj.get('id'),
        'sent_prompt': sent, 'n_predict': req['n_predict'],
        'usage_prompt_tokens': usage.get('prompt_tokens'),
        'usage_completion_tokens': usage.get('completion_tokens'),
        'timings_prompt_n': tim.get('prompt_n'),
        'timings_cache_n': tim.get('cache_n'),
        'timings_predicted_n': tim.get('predicted_n'),
        'tokenize_count': (len(toks) if tst == 200
                           and isinstance(toks, list) else None),
    }


def reference_run(server, model, reqs, work):
    """The counter's own pinned server: same flags as the tool, its own
    port, the same probe requests. Returns [probe dict | None]."""
    port = free_port()
    log = open(os.path.join(work, 'ref-server.log'), 'wb')
    proc = subprocess.Popen(
        [server, '--model', model, '--alias', ALIAS, '--port', str(port),
         '--host', '127.0.0.1', '-c', '512', '-t', '1'],
        stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
        env={k: v for k, v in os.environ.items() if k in _TOOL_ENV_KEYS})
    out = []
    try:
        t0 = time.monotonic()
        ok = False
        while time.monotonic() - t0 < 60:
            st, _, body, _ = http(port, '/health', timeout=2.0)
            if st == 200 and body == '{"status":"ok"}':
                ok = True
                break
            if proc.poll() is not None:
                break
            time.sleep(0.2)
        if ok:
            for r in reqs:
                out.append(probe(port, r))
            REF_FILES[:] = file_set(read_maps(proc.pid, os.path.dirname(
                server)))
    finally:
        if proc.poll() is None:
            proc.send_signal(signal.SIGTERM)
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=10)
        log.close()
    return out


def pid_gone(pid, ticks):
    """True when the pid no longer exists, was reused (different start
    ticks), or is a zombie / dead entry (its sockets are closed; only the
    exit status is pending). Unknown start ticks fail closed: not gone."""
    pp, tk = stat_fields(pid)
    if pp is None:
        return True
    if ticks is None:
        return False
    if tk != ticks:
        return True
    try:
        s = open(f'/proc/{pid}/stat', encoding='ascii').read()
        return s[s.rindex(')') + 2] in 'ZX'
    except (OSError, ValueError, IndexError):
        return False


def kill_if_same(pid, ticks):
    """SIGKILL a recorded pid only while it is still the observed process."""
    if ticks is None or pid_gone(pid, ticks):
        return
    try:
        os.kill(pid, signal.SIGKILL)
    except OSError:
        pass


def witness_run(work, label, tool_path, server_path, model_path, reqs,
                tool_req, extra_env=None):
    """Run one tool (the tip tool or a planted forger) in hold mode. The
    counter creates the hold dir, owns hold.json's freshness, tells the tool
    which request to send, probes the listener, releases, and observes
    teardown itself; every holder it saw and the tool's process group are
    killed on the way out. Returns
    (receipt|None, witness|None, binding|None, nonce, notes)."""
    wd = os.path.join(work, label)
    os.makedirs(wd)       # a reused directory is refused, never tolerated
    hold = os.path.join(wd, 'hold')
    os.makedirs(hold, mode=0o700)
    nonce = 'r64-' + hashlib.sha256(os.urandom(16)).hexdigest()[:10]
    out_path = os.path.join(wd, 'receipt.json')
    env = {k: v for k, v in os.environ.items() if k in _TOOL_ENV_KEYS}
    env.update(extra_env or {})
    notes = []
    t0_ns = time.time_ns()
    proc = subprocess.Popen(
        [sys.executable, tool_path, '--nonce', nonce,
         '--work', os.path.join(wd, 'tool-work'), '--server', server_path,
         '--model', model_path, '--model-sha256', MODEL_SHA,
         '--server-sha256', SERVER_SHA, '--alias', ALIAS,
         '--prompt', tool_req['prompt'],
         '--n-predict', str(tool_req['n_predict']),
         '--seed', str(tool_req['seed']),
         '--hold-dir', hold, '--hold-timeout', '90', '--out', out_path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env,
        start_new_session=True)
    tool_ticks = start_ticks_of(proc.pid)
    witness = binding = None
    seen = {}
    receipt = None
    try:
        t0 = time.monotonic()
        hp = os.path.join(hold, 'hold.json')
        while time.monotonic() - t0 < 120:
            if os.path.exists(hp):
                try:
                    hold_doc = json.load(open(hp))
                    mtime = os.stat(hp).st_mtime_ns
                except (ValueError, OSError):
                    time.sleep(0.2)
                    continue
                if not isinstance(hold_doc, dict):
                    break
                port = hold_doc.get('port')
                if not is_int(port):
                    notes.append('hold.json without an int port')
                    break
                raw_a = collect(port, hold_doc, mtime, t0_ns, proc.pid,
                                tool_ticks, server_path, model_path)
                for h in raw_a['holders']:
                    seen[h['pid']] = h.get('start_ticks')
                probes = [probe(port, r) for r in reqs]
                raw_b = collect(port, hold_doc, mtime, t0_ns, proc.pid,
                                tool_ticks, server_path, model_path)
                for h in raw_b['holders']:
                    seen[h['pid']] = h.get('start_ticks')
                witness = {
                    'probes': probes, 'hold_pid': hold_doc.get('pid'),
                    'hold_port': port, 'server_sha256':
                    hold_doc.get('server_sha256'),
                    'model_sha256': hold_doc.get('model_sha256'),
                    'alias': hold_doc.get('alias'), 'tool_req': tool_req}
                binding = {'raw_a': raw_a, 'raw_b': raw_b}
                break
            if proc.poll() is not None:
                notes.append('tool exited before hold.json')
                break
            time.sleep(0.1)
        # counter-owned release, then counter-observed teardown
        open(os.path.join(hold, 'release'), 'w').write('go\n')
        if binding is not None:
            hs = (binding['raw_a'] or {}).get('holders') or []
            gone = port_closed = False
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                gone = bool(hs) and all(
                    pid_gone(h['pid'], h.get('start_ticks')) for h in hs)
                port_closed = not listeners(witness['hold_port'])
                if gone and port_closed:
                    break
                time.sleep(0.2)
            binding['teardown'] = {'gone': gone, 'port_closed': port_closed}
        try:
            proc.wait(timeout=60)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)
        try:
            receipt = json.load(open(out_path))
        except (ValueError, OSError):
            pass
    finally:
        for pid, ticks in seen.items():
            kill_if_same(pid, ticks)
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except OSError:
            pass
        if proc.poll() is None:
            proc.kill()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                pass
    return receipt, witness, binding, nonce, notes


# --------------------------------------------------------- planted forgers #

FAKE_COMMON = r'''
import argparse, json, os, signal, socket, subprocess, sys, time
import http.server, threading, urllib.request, urllib.error
ap = argparse.ArgumentParser()
for a in ('--nonce', '--work', '--server', '--model', '--model-sha256',
          '--server-sha256', '--alias', '--hold-dir', '--hold-timeout',
          '--out', '--prompt', '--n-predict', '--seed'):
    ap.add_argument(a)
A = ap.parse_args()
TPL = json.load(open(os.environ['KAMA_FAKE_TEMPLATE']))
MODE = os.environ['KAMA_FAKE_MODE']
os.makedirs(A.work, exist_ok=True)
def free_port():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]
    s.close(); return p
def spawn_real(port, extra_env=None, exe=None):
    env = {k: v for k, v in os.environ.items()
           if k in ('PATH', 'HOME', 'LANG', 'LC_ALL')}
    env.update(extra_env or {})
    return subprocess.Popen(
        [exe or A.server, '--model', A.model, '--alias', A.alias,
         '--port', str(port), '--host', '127.0.0.1', '-c', '512', '-t', '1'],
        stdout=open(os.path.join(A.work, 'srv.log'), 'wb'),
        stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, env=env)
def wait_health(port, t=60):
    import urllib.request
    t0 = time.time()
    while time.time() - t0 < t:
        try:
            r = urllib.request.urlopen(
                f'http://127.0.0.1:{port}/health', timeout=2)
            if r.status == 200: return True
        except Exception:
            pass
        time.sleep(0.2)
    return False
def hold_and_release(doc):
    hp = os.path.join(A.hold_dir, 'hold.json')
    json.dump(doc, open(hp, 'w'))
    t0 = time.time()
    while time.time() - t0 < float(A.hold_timeout):
        if os.path.exists(os.path.join(A.hold_dir, 'release')): break
        time.sleep(0.1)
    try: os.unlink(hp)
    except OSError: pass
def write_receipt(child_pid, port, holders):
    r = json.loads(json.dumps(TPL))
    r['nonce'] = A.nonce
    r['child_pid'] = child_pid
    r['port'] = port
    r['listener_holders'] = holders
    r['hold'] = {'dir': A.hold_dir, 'released': True}
    json.dump(r, open(A.out, 'w'))
def hold_doc(pid, port):
    return {'schema': 'kama-completion-hold/v1', 'port': port, 'pid': pid,
            'alias': A.alias, 'model_sha256': A.model_sha256,
            'server_sha256': A.server_sha256, 'prompt': 'x',
            'at': '2026-10-28T00:00:00Z'}
def good_holders(pid):
    return [{'pid': pid, 'exe': A.server, 'exe_sha256': A.server_sha256}]
class Fwd(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.0'
    target = 0
    def _go(self, body):
        import urllib.request
        req = urllib.request.Request(
            f'http://127.0.0.1:{Fwd.target}{self.path}', data=body,
            method=self.command, headers={'Content-Type': 'application/json'})
        op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            r = op.open(req, timeout=30)
            code, data, ct = r.status, r.read(), r.headers.get('Content-Type')
        except urllib.error.HTTPError as e:
            code, data, ct = e.code, e.read(), e.headers.get('Content-Type')
        self.send_response(code)
        self.send_header('Content-Type', ct or 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers(); self.wfile.write(data)
    def do_GET(self): self._go(None)
    def do_POST(self):
        n = int(self.headers.get('Content-Length') or 0)
        self._go(self.rfile.read(n))
    def log_message(self, *a): pass
def serve(handler, port):
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv
'''

FAKE_MODES = {
    # a pinned server that is not a descendant of the tool (double fork)
    'detach': r'''
port = free_port()
pid_file = os.path.join(A.work, 'detached.pid')
if os.fork() == 0:
    if os.fork() == 0:
        os.setsid()
        p = spawn_real(port)
        open(pid_file, 'w').write(str(p.pid)); p.wait(); os._exit(0)
    os._exit(0)
wait_health(port)
time.sleep(0.5)
pid = int(open(pid_file).read())
hold_and_release(hold_doc(pid, port))
os.kill(pid, signal.SIGTERM)
write_receipt(pid, port, good_holders(pid))
''',
    # a forwarding proxy in front of the real child on the advertised port
    'proxy': r'''
real = free_port(); front = free_port()
p = spawn_real(real); wait_health(real)
Fwd.target = real
srv = serve(Fwd, front)
hold_and_release(hold_doc(p.pid, front))
srv.shutdown(); p.terminate(); p.wait()
write_receipt(p.pid, front, good_holders(p.pid))
''',
    # a canned answerer: the held pid is a sleeper, the listener is ours
    'canned': r'''
front = free_port()
sleeper = subprocess.Popen([sys.executable, '-c',
                            'import time; time.sleep(600)'])
class Canned(Fwd):
    def _go(self, body):
        import json as j
        b = j.dumps({'status': 'ok'}).encode()
        self.send_response(200); self.send_header('Content-Type',
            'application/json'); self.send_header('Content-Length', str(len(b)))
        self.end_headers(); self.wfile.write(b)
srv = serve(Canned, front)
hold_and_release(hold_doc(sleeper.pid, front))
srv.shutdown(); sleeper.kill(); sleeper.wait()
write_receipt(sleeper.pid, front, good_holders(sleeper.pid))
''',
    # a hold.json copied from an earlier run, mtime pushed into the past
    'stale_old': r'''
old = json.load(open(os.environ['KAMA_FAKE_STALE']))
hp = os.path.join(A.hold_dir, 'hold.json')
json.dump(old, open(hp, 'w'))
os.utime(hp, (1, 1))
t0 = time.time()
while time.time() - t0 < float(A.hold_timeout):
    if os.path.exists(os.path.join(A.hold_dir, 'release')): break
    time.sleep(0.1)
os.unlink(hp)
write_receipt(old['pid'], old['port'], good_holders(old['pid']))
''',
    # the same stale hold.json with the mtime pushed into the future
    'stale_future': r'''
old = json.load(open(os.environ['KAMA_FAKE_STALE']))
hp = os.path.join(A.hold_dir, 'hold.json')
json.dump(old, open(hp, 'w'))
fut = time.time() + 3600
os.utime(hp, (fut, fut))
t0 = time.time()
while time.time() - t0 < float(A.hold_timeout):
    if os.path.exists(os.path.join(A.hold_dir, 'release')): break
    time.sleep(0.1)
os.unlink(hp)
write_receipt(old['pid'], old['port'], good_holders(old['pid']))
''',
    # the pinned server started under LD_PRELOAD
    'preload': r'''
port = free_port()
p = spawn_real(port, {'LD_PRELOAD': '/usr/lib/libm.so.6'})
wait_health(port)
hold_and_release(hold_doc(p.pid, port))
p.terminate(); p.wait()
write_receipt(p.pid, port, good_holders(p.pid))
''',
    # a genuine pinned child holds the port and answers, but the receipt is
    # a copy of an earlier run's (the counter asked for a new request)
    'replay': r'''
port = free_port()
p = spawn_real(port)
wait_health(port)
hold_and_release(hold_doc(p.pid, port))
p.terminate(); p.wait()
write_receipt(p.pid, port, good_holders(p.pid))
''',
    # the pinned bytes copied to another path (same sha256, not the path
    # the counter chose)
    'pathcopy': r'''
import shutil
d = os.path.join(A.work, 'copy'); os.makedirs(d, exist_ok=True)
src = os.path.dirname(A.server)
for n in os.listdir(src):
    sp = os.path.join(src, n)
    dp = os.path.join(d, n)
    if os.path.exists(dp) or os.path.lexists(dp): continue
    if os.path.islink(sp): os.symlink(os.readlink(sp), dp)
    elif n == 'llama-server': shutil.copy2(sp, dp)
    elif n.startswith('lib'): os.symlink(sp, dp)
exe = os.path.join(d, 'llama-server')
port = free_port()
p = spawn_real(port, exe=exe); wait_health(port)
hold_and_release(hold_doc(p.pid, port))
p.terminate(); p.wait()
write_receipt(p.pid, port, [{'pid': p.pid, 'exe': A.server,
                             'exe_sha256': A.server_sha256}])
''',
}


def write_fake(work, mode):
    path = os.path.join(work, f'fake-{mode}.py')
    with open(path, 'w') as f:
        f.write(FAKE_COMMON + FAKE_MODES[mode])
    return path


def apply_patch(tip_tool_text, patch_text, workdir, name):
    """Apply a unified diff to the tool text with `patch`. Returns
    (patched text | None, reason). A dry run must succeed and the real
    run must report no fuzz (offsets are accepted, a fuzzed hunk is not)."""
    d = os.path.join(workdir, name)
    os.makedirs(os.path.join(d, 'tools'), exist_ok=True)
    tp = os.path.join(d, 'tools', 'kama-completion-live.py')
    with open(tp, 'w') as f:
        f.write(tip_tool_text)
    pp = os.path.join(d, 'x.patch')
    with open(pp, 'w') as f:
        f.write(patch_text)
    dry = subprocess.run(['patch', '-p1', '--dry-run', '-i', pp, '-d', d],
                         capture_output=True, text=True)
    if dry.returncode != 0 or 'fuzz' in dry.stdout.lower():
        return None, 'dry-run failed or fuzzed: ' + dry.stdout[-200:]
    r = subprocess.run(['patch', '-p1', '-i', pp, '-d', d],
                       capture_output=True, text=True)
    if r.returncode != 0 or 'fuzz' in r.stdout.lower():
        return None, 'patch failed or fuzzed: ' + r.stdout[-200:]
    return open(tp).read(), ''


def splice_before_main(text, code):
    """Insert `code` before the tool's `if __name__ == '__main__':` guard
    so it is defined before main() runs. None when the guard is absent."""
    marker = "\nif __name__ == '__main__':"
    i = text.rfind(marker)
    if i < 0:
        return None
    return text[:i] + '\n' + code + text[i:]


# The forger fabricates the tool's own holder bookkeeping so the tool-side
# check cannot be what rejects it: structurally (a Popen recorder and a
# replacement `_proc_holders`), independent of the tool's source text.
FORGE_CLAIM = '''
_FP_LAST = {}
_FP_POPEN = subprocess.Popen
class _FPopen(_FP_POPEN):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        _FP_LAST['p'] = self
subprocess.Popen = _FPopen
def _proc_holders(port):
    p = _FP_LAST.get('p')
    srv = os.path.realpath(sys.argv[sys.argv.index('--server') + 1])
    return [{'pid': p.pid, 'exe': srv, 'exe_sha256': DEFAULT_SERVER_SHA}]
'''

# A v3-schema tool whose receipt is v2-shaped: the holder bookkeeping is
# removed from what it writes.
RELABEL_WRAP = '''
_orig_run = run
def run(args):
    r, rc = _orig_run(args)
    r.pop('listener_holders', None)
    r['checks'].pop('listener_holders_pinned', None)
    return r, rc
'''


def forge_variants(repo, tip, work):
    """Planted forged tools: the round-63 patches replayed on the tip tool
    (A: canned fake behind the real child's inherited listener; B: no
    llama-server at all) and each with the tool's own holder bookkeeping
    fabricated. Returns ({name: tool text}, [error strings])."""
    tool = blob(repo, tip, 'tools/kama-completion-live.py')
    pa = blob(repo, tip,
              '.ufo/waves/round-64/controls/forge-A-realchild.patch')
    pb = blob(repo, tip,
              '.ufo/waves/round-64/controls/forge-B-sleeper-delta.patch')
    if not (tool and pa and pb):
        return {}, ['forge patch or tool blob missing at the tip']
    errs = []
    a, why = apply_patch(tool.decode(), pa.decode(), work, 'forgeA-build')
    if a is None:
        return {}, ['forge A: ' + why]
    ab, why = apply_patch(a, pb.decode(), work, 'forgeAB-build')
    if ab is None:
        errs.append('forge B: ' + why)
    out = {'forgeA': a}
    a2 = splice_before_main(a, FORGE_CLAIM)
    if a2 is None:
        errs.append('forge A2: no main guard to splice before')
    else:
        out['forgeA2'] = a2
    if ab is not None:
        b2 = splice_before_main(ab, FORGE_CLAIM)
        if b2 is None:
            errs.append('forge B2: no main guard to splice before')
        else:
            out['forgeB2'] = b2
    return out, errs


# --------------------------------------------------------------- controls #

def clone(o):
    return json.loads(json.dumps(o))


def reseal(c):
    c['body_sha256'] = sha256_b(c['body'].encode())
    c['body_bytes'] = len(c['body'].encode())


def edit_body(rcpt, name, fn):
    """Mutate the JSON body of one capture and re-seal its hash, so the
    mutation is rejected by the grader and not by the hash comparison."""
    m = clone(rcpt)
    c = m['captures'][name]
    obj = json.loads(c['body'])
    fn(obj)
    c['body'] = json.dumps(obj, separators=(',', ':'))
    reseal(c)
    if 'content-length' in c.get('headers', {}):
        c['headers']['content-length'] = str(c['body_bytes'])
    return m


def edit(rcpt, fn):
    m = clone(rcpt)
    fn(m)
    return m


def is_hit(s, expect, cap=MAX_COLLATERAL):
    """Credit only when the re-score rejects, the named check is among the
    failures and the failure set stays within the cap."""
    return (not s['met']) and expect in s['fails'] and len(
        s['fails']) <= cap


def build_controls(receipt, witness, binding, work):
    """(family, receipt, witness, binding, expected fail name, cap) tuples
    of offline mutations of the genuine run."""
    decoy = os.path.join(work, 'decoy-model.bin')
    with open(decoy, 'wb') as f:
        f.write(b'not-the-pinned-model')
    ctl = []

    def add(fam, expect, m=None, wm=None, bm=None, cap=MAX_COLLATERAL):
        ctl.append((fam, m if m is not None else receipt, wm, bm, expect,
                    cap))

    add('stale', 'nonce_match',
        edit(receipt, lambda m: m.update({'nonce': 'r60-dead'})))
    add('log', 'health_ready', edit(receipt, lambda m: m['captures'][
        'health'].update({'body': '{"status":"OK"}'})))
    add('tamper', 'completion_envelope', edit_body(
        receipt, 'completion', lambda o: o.update(
            {'object': 'chat.completion'})), cap=ENVELOPE_CAP)
    add('tamper', 'hold_released', edit(receipt, lambda m: m['hold'].update(
        {'released': False})))
    add('tamper', 'teardown_clean', edit(receipt, lambda m: m[
        'teardown'].update({'child_pre_dead': True})))
    add('tamper', 'teardown_clean', edit(receipt, lambda m: m[
        'teardown'].update({'returncode': 137})))
    add('tamper', 'teardown_port_closed', edit(receipt, lambda m: m[
        'teardown'].update({'port_closed': False})))
    add('tamper', 'verdict', edit(receipt,
                                  lambda m: m.update({'verdict': 'FAIL'})))

    def swap_text(o):
        o['choices'][0]['text'] = o['choices'][0]['text'] + '!'
    add('tamper', 'completion_deterministic',
        edit_body(receipt, 'completion2', swap_text))
    add('tamper', 'model_digest', edit(receipt, lambda m: (
        m['model'].update({'sha256': '0' * 64}),
        m['server'].update({'sha256': '0' * 64}))))
    add('predead', 'teardown_clean', edit(receipt, lambda m: m[
        'teardown'].update({'child_pre_dead': True})))
    add('sigterm', 'teardown_clean', edit(receipt, lambda m: m[
        'teardown'].update({'returncode': -9})))
    add('hold', 'hold_released', edit(receipt, lambda m: m['hold'].update(
        {'released': False})))
    add('outside', 'completion_model_id', edit_body(
        receipt, 'completion', lambda o: o.update({'model': 'other-alias'})))
    add('hdr', 'completion_headers', edit(receipt, lambda m: m['captures'][
        'completion']['headers'].update({'content-type': 'text/plain'})))
    add('hdr', 'completion_headers', edit(receipt, lambda m: m['captures'][
        'completion']['headers'].pop('content-type')))
    add('trunc', 'completion_untruncated', edit(
        receipt, lambda m: m['captures']['completion'].update(
            {'body_truncated': True})))
    add('trunc', 'completion_untruncated', edit(
        receipt, lambda m: m['captures']['completion']['headers'].update(
            {'content-length': str(
                m['captures']['completion']['body_bytes'] + 1)})))

    def timing(**kw):
        return lambda o: o['timings'].update(kw)
    add('timing', 'completion_timings', edit_body(
        receipt, 'completion', timing(predicted_ms=-1.0)))
    add('timing', 'completion_timings', edit_body(
        receipt, 'completion', timing(predicted_ms=True)))
    add('timing', 'completion_timings', edit_body(
        receipt, 'completion', timing(predicted_ms=float('inf'))))
    add('timing', 'completion_timings', edit_body(
        receipt, 'completion', lambda o: o['timings'].pop('cache_n')))
    add('shape', 'completion_choice_shape', edit_body(
        receipt, 'completion',
        lambda o: o['choices'].append(dict(o['choices'][0]))))
    add('shape', 'completion_choice_shape', edit_body(
        receipt, 'completion', lambda o: o['choices'][0].update(
            {'index': 1})))
    add('shape', 'completion_choice_shape', edit_body(
        receipt, 'completion', lambda o: o['choices'][0].update(
            {'text': ''})))
    add('shape', 'completion_choice_shape', edit_body(
        receipt, 'completion', lambda o: o['choices'][0].update(
            {'logprobs': {}})))
    add('idcr', 'completion_id_created', edit_body(
        receipt, 'completion', lambda o: o.update({'id': ''})))
    add('idcr', 'completion_id_created', edit_body(
        receipt, 'completion', lambda o: o.update({'created': True})))
    add('idcr', 'completion_id_created', edit_body(
        receipt, 'completion', lambda o: o.update({'created': 5})))

    def ptok(o):
        o['usage']['prompt_tokens'] += 1
        o['usage']['total_tokens'] += 1
    add('ptok', 'completion_prompt_tokens',
        edit_body(receipt, 'completion', ptok))
    add('ptok', 'completion_prompt_tokens', edit_body(
        receipt, 'tokenize', lambda o: o['tokens'].append(7)))

    def req_prompt(m):
        c = m['captures']['completion']
        c['request_body'] = c['request_body'].replace(
            TOOL_REQ['prompt'], 'Other text')
        c['request_sha256'] = sha256_b(c['request_body'].encode())
    add('reqbind', 'completion_request_bound', edit(receipt, req_prompt))
    add('reqbind', 'completion_request_bound', edit(
        receipt, lambda m: m['captures']['completion'].update(
            {'request_sha256': '0' * 64})))
    add('listener', 'listener_owned', edit(
        receipt, lambda m: m['checks']['listener_owned'].update(
            {'passed': False})))
    add('digest', 'model_digest', edit(
        receipt, lambda m: m['model'].update({'path': decoy})))
    add('schema', 'schema', edit(
        receipt, lambda m: m.update({'schema': 'kama-completion-live/v2'})))

    # ---- witness mutations (the receipt is the genuine one) ------------ #
    def wm(i, **kw):
        def f(w):
            w = clone(w)
            w['probes'][i].update(kw)
            return w
        return f
    add('witness', 'live_fp_capture', wm=wm(0, fingerprint='b1-aaaaaaaaa'))
    add('witness', 'live_ptok', wm=lambda w: wm(
        0, usage_prompt_tokens=w['probes'][0]['usage_prompt_tokens'] + 1)(w))
    add('witness', 'live_object', wm=wm(0, object='chat.completion'))
    add('witness', 'live_text', wm=wm(0, text=''))
    add('witness', 'live_pid', wm=lambda w: {**clone(w), 'hold_pid': 1})
    # ---- run-field: the answer must carry this run's fields ------------ #
    def swap_answer(w):
        w = clone(w)
        keep = ('sent_prompt', 'n_predict')
        a, b = w['probes'][0], w['probes'][1]
        w['probes'][1] = {**a, **{k: b[k] for k in keep}}
        return w
    add('runfield', 'live_ref_text', wm=swap_answer)
    add('runfield', 'live_run_field', wm=wm(1, usage_completion_tokens=99))
    add('runfield', 'live_run_field', wm=lambda w: wm(
        1, timings_prompt_n=w['probes'][1]['timings_prompt_n'] + 1)(w))
    add('runfield', 'live_ref_usage', wm=lambda w: wm(
        0, usage_prompt_tokens=w['probes'][0]['usage_prompt_tokens'] + 1,
        tokenize_count=w['probes'][0]['tokenize_count'] + 1,
        timings_prompt_n=w['probes'][0]['timings_prompt_n'] + 1)(w))
    # ---- binding mutations of the counter's own procfs snapshot -------- #
    def bm(fn):
        def f(b):
            b = clone(b)
            fn(b['raw_a'])
            return b
        return f
    add('bind', 'bind_exe', bm=bm(
        lambda r: r['holders'][0].update({'exe_sha256': '0' * 64})))
    add('bind', 'bind_exe', bm=bm(
        lambda r: r['holders'][0].update({'exe': '/usr/bin/python3'})))
    add('bind', 'bind_holders', bm=bm(
        lambda r: r['holders'].append({**r['holders'][0], 'pid': 1})))
    add('bind', 'bind_holders', bm=bm(
        lambda r: r.update({'hold_pid': r['hold_pid'] + 1})))
    add('bind', 'bind_holders', bm=bm(
        lambda r: r.update({'unreadable_own': [999999]})))
    add('bind', 'bind_listener', bm=bm(
        lambda r: r['listeners'][0].update({'loopback': False})))
    add('bind', 'bind_argv', bm=bm(
        lambda r: r['holders'][0].update({'cmdline': [
            r['holders'][0]['cmdline'][0], '--port', '1']})))
    add('bind', 'bind_argv', bm=bm(lambda r: r['holders'][0].update(
        {'cmdline': r['holders'][0]['cmdline'] + ['--port', '2']})))
    add('bind', 'bind_argv', bm=bm(lambda r: r['holders'][0].update(
        {'cmdline': r['holders'][0]['cmdline'] + ['--model', decoy]})))
    add('bind', 'bind_argv', bm=bm(lambda r: r['holders'][0].update(
        {'cmdline': r['holders'][0]['cmdline'] + ['-c', '4096']})))
    add('bind', 'bind_argv', bm=bm(lambda r: r['holders'][0].update(
        {'cmdline': r['holders'][0]['cmdline'] + ['-m', decoy]})))

    def envp(fn):
        return bm(lambda r: r['holders'][0].update(
            {'environ': fn(dict(r['holders'][0]['environ']))}))
    add('bind', 'bind_env', bm=envp(
        lambda e: {**e, 'LD_PRELOAD': '/x.so'}))
    add('bind', 'bind_env', bm=envp(
        lambda e: {**e, 'GLIBC_TUNABLES': 'glibc.malloc.check=3'}))
    add('bind', 'bind_env', bm=bm(
        lambda r: r['holders'][0].update({'environ': None})))
    add('bind', 'bind_env', bm=envp(
        lambda e: {**e, 'LLAMA_ARG_MODEL': '/other.gguf'}))
    add('bind', 'bind_env', bm=envp(
        lambda e: {**e, 'PATH': '/evil:' + e.get('PATH', '')}))
    add('bind', 'bind_ns', bm=bm(lambda r: r['holders'][0].update(
        {'ns': {**r['holders'][0]['ns'], 'mnt': 'mnt:[1]'}})))
    add('bind', 'bind_trace', bm=bm(
        lambda r: r['holders'][0].update({'tracer_pid': 4242})))
    add('bind', 'bind_state', bm=bm(
        lambda r: r['holders'][0].update({'state': 'T'})))
    add('bind', 'bind_maps', bm=bm(lambda r: r['holders'][0]['maps'].append(
        {'path': '/memfd:evil (deleted)', 'deleted': True, 'sha256': None})))
    add('bind', 'bind_maps', bm=bm(lambda r: r['holders'][0]['maps'].append(
        {'path': '/tmp/evil.so', 'deleted': False, 'sha256': '0' * 64})))
    add('bind', 'bind_maps', bm=bm(lambda r: next(
        m for m in r['holders'][0]['maps']
        if m.get('sha256') and m['path'].endswith('.so.0.7.0')).update(
        {'sha256': '1' * 64})))
    add('bind', 'bind_ancestry', bm=bm(
        lambda r: r.update({'tool_pid': 999999999})))
    add('bind', 'hold_fresh', bm=bm(
        lambda r: r.update({'hold_mtime_ns': r['t0_ns'] - 1})))
    add('bind', 'hold_fresh', bm=bm(lambda r: r['holders'][0].update(
        {'start_ticks': r['tool_start_ticks'] - 1})))
    add('bind', 'teardown_observed', bm=lambda b: {
        **clone(b), 'teardown': {'gone': False, 'port_closed': True}})
    add('bind', 'bind_stable', bm=lambda b: {**clone(b), 'raw_b': {
        **clone(b['raw_b']), 'holders': []}})
    add('bind', 'hold_fresh', bm=bm(lambda r: r.update(
        {'hold_mtime_ns': r['collected_ns'] + 10_000_000_000})))

    def ref_wm(fn):
        def f(w):
            w = clone(w)
            fn(w['ref_files'])
            return w
        return f
    add('bind', 'bind_ref_files', wm=ref_wm(
        lambda rf: rf[0].__setitem__(2, '1')))
    add('bind', 'bind_ref_files', bm=bm(lambda r: r['holders'][0][
        'maps'].append({
            'path': os.path.join(os.path.dirname(r['server_path']),
                                 'libllama-cli-impl.so'),
            'deleted': False, 'dev': '00:2e', 'inode': '4242',
            'sha256': LIBS['libllama-cli-impl.so']})))

    # ---- the receipt's own request and answer must be this run's ------ #
    def both(fn):
        def f(m):
            for n in ('completion', 'completion2'):
                c = m['captures'][n]
                o = json.loads(c['body'])
                fn(o)
                c['body'] = json.dumps(o, separators=(',', ':'))
                reseal(c)
                if 'content-length' in c.get('headers', {}):
                    c['headers']['content-length'] = str(c['body_bytes'])
        return f
    add('receiptbind', 'receipt_ref_text', edit(receipt, both(
        lambda o: o['choices'][0].update({'text': ' FABRICATED BY TOOL'}))))

    def usage_plus(m):
        both(lambda o: (o['usage'].update(
            {'prompt_tokens': o['usage']['prompt_tokens'] + 1,
             'total_tokens': o['usage']['total_tokens'] + 1})))(m)
        tk = m['captures']['tokenize']
        o = json.loads(tk['body'])
        o['tokens'].append(7)
        tk['body'] = json.dumps(o, separators=(',', ':'))
        reseal(tk)
    add('receiptbind', 'receipt_ref_usage', edit(receipt, usage_plus))

    def other_prompt(m):
        for n in ('completion', 'completion2'):
            c = m['captures'][n]
            o = json.loads(c['request_body'])
            o['prompt'] = o['prompt'] + ' again'
            c['request_body'] = json.dumps(o)
            c['request_sha256'] = sha256_b(c['request_body'].encode())
    add('receiptbind', 'receipt_req', edit(receipt, other_prompt))

    def other_n(m):
        for n in ('completion', 'completion2'):
            c = m['captures'][n]
            o = json.loads(c['request_body'])
            o['n_predict'] = o['n_predict'] + 1
            c['request_body'] = json.dumps(o)
            c['request_sha256'] = sha256_b(c['request_body'].encode())
    add('receiptbind', 'receipt_req', edit(receipt, other_n))
    return ctl


def tool_files(repo, tip, work):
    """Write the tip's tool + dependency to work/tip. Returns tool path or
    None; errors via the second value."""
    tool_blob = blob(repo, tip, 'tools/kama-completion-live.py')
    if not tool_blob:
        return None, 'tools/kama-completion-live.py absent at tip'
    root = os.path.join(work, 'tip')
    os.makedirs(os.path.join(root, 'tools'), exist_ok=True)
    os.makedirs(os.path.join(root, 'registry'), exist_ok=True)
    tp = os.path.join(root, 'tools', 'kama-completion-live.py')
    with open(tp, 'wb') as f:
        f.write(tool_blob)
    dep = blob(repo, tip, 'tools/kama-llamacpp-live.py')
    if not dep:
        return None, 'tip lacks tools/kama-llamacpp-live.py'
    with open(os.path.join(root, 'tools', 'kama-llamacpp-live.py'),
              'wb') as f:
        f.write(dep)
    reg = blob(repo, tip, 'registry/endpoint-consumers.tsv')
    if reg:
        with open(os.path.join(root, 'registry',
                               'endpoint-consumers.tsv'), 'wb') as f:
            f.write(reg)
    return tp, None


def pick_server():
    cand = shutil.which('llama-server')
    paths = [os.path.realpath(cand)] if cand else []
    paths.append(os.path.expanduser(
        '~/.local/opt/llama-b11755/llama-server'))
    for p in paths:
        if sha256_path(p) == SERVER_SHA:
            return p
    return None


def families_match(tot, ok):
    """Every family present at exactly its declared count, credited in full."""
    return tot == EXPECT_FAMILIES and ok == EXPECT_FAMILIES


def credit_rule(s, expect, cap, clean_receipt=False):
    """One control's credit: rejected, the named check among the failures,
    within the cap; a fake tool holding a genuine receipt copy must in
    addition show no receipt-level failure (a garbled receipt is a crashed
    fake, not the named reason). Declared in freeze.txt AMENDMENT 1."""
    hit = is_hit(s, expect, cap)
    if hit and clean_receipt:
        hit = not any(k in RECEIPT_LEVEL or k in RECEIPT_BIND
                      or k.startswith('inconsistent:') for k in s['fails'])
    return hit


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True)
    ap.add_argument('--tip', required=True)
    ap.add_argument('--work', required=True)
    args = ap.parse_args(argv)
    work = os.path.abspath(args.work)
    if os.path.isdir(work) and os.listdir(work):
        print('error: work-reused: --work already holds files; the counter '
              'refuses a reused scratch directory (pass a fresh one)',
              file=sys.stderr)
        print('tool_present=0 live_ok=0/1 controls_targeted=0/0 '
              'work_reused=1 errors=1 met=False')
        return 2
    os.makedirs(work, exist_ok=True)
    errors = []
    global NONCE

    server = pick_server()
    model = os.path.realpath(os.path.expanduser(
        '~/.cache/kama-shokunin/models/stories260K.gguf'))
    if server is None:
        errors.append('no llama-server with the pinned sha256 found')
    if sha256_path(model) != MODEL_SHA:
        errors.append('fixture model absent or not the pinned sha256')
    tool_path, err = tool_files(args.repo, args.tip, work)
    tool_present = 1 if tool_path else 0
    if err:
        errors.append(err)
    receipt = witness = binding = None
    live_ok = 0
    st = 0
    fam_tot, fam_ok, detail = {}, {}, []
    probe_nonce = reqs = None
    if not errors:
        rng = random.Random(int.from_bytes(os.urandom(8), 'big'))
        probe_nonce = 'r64p' + hashlib.sha256(os.urandom(8)).hexdigest()[:8]
        ref_all = []
        for _attempt in range(8):
            reqs, tool_req = draw_requests(rng, probe_nonce)
            ref_all = reference_run(server, model, reqs + [tool_req], work)
            texts = [(r or {}).get('text') for r in ref_all]
            if (len(ref_all) == 3 and all(isinstance(t, str) and t
                                          for t in texts)
                    and len(set(texts)) == 3):
                break
        else:
            errors.append('no draw gave three distinct reference answers')
        if not errors:
            TOOL_REQ.clear()
            TOOL_REQ.update(tool_req)
            receipt, witness, binding, nonce, notes = witness_run(
                work, 'live', tool_path, server, model, reqs, tool_req)
            NONCE = nonce
            if receipt is None or witness is None or binding is None:
                errors.append('live: no receipt/witness produced '
                              + '; '.join(notes))
            else:
                witness['ref'] = ref_all[:2]
                witness['ref_tool'] = ref_all[2]
                witness['ref_files'] = [list(x) for x in REF_FILES]
                s = score_run(receipt, witness, binding, probe_nonce)
                live_ok = 1 if s['met'] else 0
                if not s['met']:
                    errors.append('live: ' + json.dumps(sorted(s['fails'])))
    if live_ok == 1:
        run_controls(args, work, tool_path, server, model, receipt,
                     witness, binding, reqs, probe_nonce, rng, fam_tot,
                     fam_ok, detail, errors)
        st = eval_selftest_run(receipt, witness, binding, probe_nonce)
    total = sum(fam_tot.values())
    rejected = sum(fam_ok.values())
    fam_match = families_match(fam_tot, fam_ok)
    met = (tool_present == 1 and live_ok == 1 and fam_match
           and st == EXPECT_EVAL_SELFTEST and not errors)
    fams = ' '.join(f'{k}={fam_ok.get(k, 0)}/{v}'
                    for k, v in sorted(fam_tot.items()))
    missing = sorted(set(EXPECT_FAMILIES) - set(fam_tot))
    print(f'tool_present={tool_present} live_ok={live_ok}/1 '
          f'controls_targeted={rejected}/{total} of {EXPECT_CONTROLS} '
          f'families_exact={int(fam_match)} missing_families={missing} '
          f'eval_selftest={st}/{EXPECT_EVAL_SELFTEST} '
          f'errors={len(errors)} met={met} families[{fams}]')
    for e in errors[:8] + detail[:12]:
        print(f'error: {e}', file=sys.stderr)
    return 0 if met else 1


def score_run(receipt, witness, binding, probe_nonce, nonce=None):
    """score() under this run's globals: the tool nonce (nonce_match), the
    request the counter asked of the tool (completion_request_bound), and
    the per-run probe nonce every outside probe prompt must carry."""
    global NONCE
    saved_n, saved_t = NONCE, dict(TOOL_REQ)
    if nonce is not None:
        NONCE = nonce
    tr = (witness or {}).get('tool_req')
    if tr:
        TOOL_REQ.clear()
        TOOL_REQ.update(tr)
    try:
        s = score(receipt, witness, binding)
    finally:
        NONCE = saved_n
        TOOL_REQ.clear()
        TOOL_REQ.update(saved_t)
    if not all(probe_nonce in ((p or {}).get('sent_prompt') or '')
               for p in (witness or {}).get('probes') or []):
        s['fails'].add('live_nonce')
    s['met'] = not s['fails']
    return s


def eval_selftest_run(receipt, witness, binding, probe_nonce):
    """Eight planted cases the evaluator must judge correctly: three that
    must NOT be credited (wrong reason, over-cap cascade, a passing check
    named), three that MUST be (a one-field break, the envelope break at its
    cap, a missing probe nonce), the clean-receipt veto, and a misfiled
    family table. Returns the number judged correctly (expected 8)."""
    n = 0
    stale = edit(receipt, lambda m: m.update({'nonce': 'r60-dead'}))
    n += int(not is_hit(score_run(stale, witness, binding, probe_nonce),
                        'live_ptok'))
    env = edit_body(receipt, 'completion',
                    lambda o: o.update({'object': 'chat.completion'}))
    n += int(not is_hit(score_run(env, witness, binding, probe_nonce),
                        'completion_envelope'))
    n += int(not is_hit(score_run(receipt, witness, binding, probe_nonce),
                        'nonce_match'))
    health = edit(receipt, lambda m: m['captures']['health'].update(
        {'body': '{"status":"OK"}'}))
    n += int(is_hit(score_run(health, witness, binding, probe_nonce),
                    'health_ready'))
    n += int(is_hit(score_run(env, witness, binding, probe_nonce),
                    'completion_envelope', ENVELOPE_CAP))
    nonce_w = clone(witness)
    nonce_w['probes'][0]['sent_prompt'] = 'no nonce here'
    n += int(is_hit(score_run(receipt, nonce_w, binding, probe_nonce),
                    'live_nonce'))
    n += int(not credit_rule(
        {'met': False, 'fails': {'bind_exe', 'health_ready'}},
        'bind_exe', 99, clean_receipt=True))
    bad_tot = dict(EXPECT_FAMILIES)
    bad_tot['stale'] = 0
    bad_tot['log'] = EXPECT_FAMILIES['log'] + 1
    n += int(not families_match(bad_tot, bad_tot))
    return n


def run_controls(args, work, tool_path, server, model, receipt, witness,
                 binding, reqs, probe_nonce, rng, fam_tot, fam_ok, detail,
                 errors):
    tool_req = witness['tool_req']
    ref = witness['ref']
    ref_tool = witness['ref_tool']

    def credit(fam, s, expect, cap, label, clean_receipt=False):
        hit = credit_rule(s, expect, cap, clean_receipt)
        fam_tot[fam] = fam_tot.get(fam, 0) + 1
        fam_ok[fam] = fam_ok.get(fam, 0) + int(hit)
        if not hit:
            detail.append(f'escape {fam}/{label} expect={expect} '
                          f'met={s["met"]} nfails={len(s["fails"])} '
                          f'fails={sorted(s["fails"])[:8]}')

    def scenario(fam, label, expect, cap, clean, tool, treq=None, tref=None,
                 extra_env=None):
        """One live forged-tool run scored through the same path as the
        genuine run; a run that cannot be scored counts as a control that
        was not rejected (and is reported)."""
        treq = treq or tool_req
        tref = tref or ref_tool
        try:
            r, w, b, nonce, notes = witness_run(
                work, label, tool, server, model, reqs, treq, extra_env)
        except Exception as e:  # a control that cannot run is not credit
            errors.append(f'{label}: {type(e).__name__}: {e}')
            fam_tot[fam] = fam_tot.get(fam, 0) + 1
            return
        if r is None or w is None or b is None:
            detail.append(f'{label}: no receipt/witness {notes}')
            fam_tot[fam] = fam_tot.get(fam, 0) + 1
            return
        w['ref'] = ref
        w['ref_tool'] = tref
        w['ref_files'] = witness['ref_files']
        credit(fam, score_run(r, w, b, probe_nonce, nonce=nonce), expect,
               cap, label, clean)

    for fam, m, wm, bm, expect, cap in build_controls(
            receipt, witness, binding, work):
        w = wm(witness) if wm else witness
        b = bm(binding) if bm else binding
        credit(fam, score_run(m, w, b, probe_nonce), expect, cap, expect)

    # live forged tools, all through the same witness_run + score path
    tpl = os.path.join(work, 'genuine-receipt.json')
    with open(tpl, 'w') as f:
        json.dump(receipt, f)
    stale_doc = os.path.join(work, 'stale-hold.json')
    with open(stale_doc, 'w') as f:
        json.dump({'schema': 'kama-completion-hold/v1',
                   'port': witness.get('hold_port'),
                   'pid': witness.get('hold_pid'),
                   'alias': ALIAS, 'model_sha256': MODEL_SHA,
                   'server_sha256': SERVER_SHA, 'prompt': PROMPT,
                   'at': '2026-10-28T00:00:00Z'}, f)
    env_base = {'KAMA_FAKE_TEMPLATE': tpl, 'KAMA_FAKE_STALE': stale_doc}
    plan = [('detach', 'detach', 'detach', 'bind_ancestry'),
            ('proxy', 'proxy', 'proxy', 'bind_holders'),
            ('canned', 'canned', 'canned', 'bind_exe'),
            ('stale_old', 'stalehold', 'stale_old', 'hold_fresh'),
            ('stale_future', 'stalehold', 'stale_future', 'hold_fresh'),
            ('preload', 'preload', 'preload', 'bind_env'),
            ('pathcopy', 'pathcopy', 'pathcopy', 'bind_exe')]
    for mode, fam, label, expect in plan:
        fake = write_fake(work, mode)
        scenario(fam, 'fake-' + label, expect, 99, True, fake,
                 extra_env=dict(env_base, KAMA_FAKE_MODE=mode))

    # replay: a genuine pinned child holds the port but the tool writes a
    # receipt from an earlier run; the counter asked for a NEW request
    texts = {(r or {}).get('text') for r in [*ref, ref_tool]}
    ref2 = []
    for _try in range(8):
        _, tool_req2 = draw_requests(rng, probe_nonce)
        ref2 = reference_run(server, model, [tool_req2], work)
        if len(ref2) == 1 and ref2[0].get('text') not in texts \
                and ref2[0].get('text'):
            break
    else:
        ref2 = []
    if len(ref2) == 1:
        fake = write_fake(work, 'replay')
        scenario('replay', 'fake-replay', 'receipt_ref_text', SCENARIO_CAP,
                 False, fake, treq=tool_req2, tref=ref2[0],
                 extra_env=dict(env_base, KAMA_FAKE_MODE='replay'))
    else:
        errors.append('replay: no draw with a new reference answer')
        fam_tot['replay'] = fam_tot.get('replay', 0) + 1

    tool_text = (blob(args.repo, args.tip, 'tools/kama-completion-live.py')
                 or b'').decode()
    forged, ferrs = forge_variants(args.repo, args.tip, work)
    errors.extend(ferrs)
    root = os.path.dirname(os.path.dirname(tool_path))

    def planted_tool(name, text):
        d = os.path.join(work, 'planted-' + name)
        os.makedirs(os.path.join(d, 'tools'))
        os.makedirs(os.path.join(d, 'registry'))
        shutil.copy(os.path.join(root, 'tools', 'kama-llamacpp-live.py'),
                    os.path.join(d, 'tools', 'kama-llamacpp-live.py'))
        rg = os.path.join(root, 'registry', 'endpoint-consumers.tsv')
        if os.path.exists(rg):
            shutil.copy(rg, os.path.join(d, 'registry',
                                         'endpoint-consumers.tsv'))
        fp = os.path.join(d, 'tools', 'kama-completion-live.py')
        with open(fp, 'w') as f:
            f.write(text)
        return fp

    for name in ('forgeA', 'forgeA2', 'forgeB2'):
        if name not in forged:
            fam_tot['forge'] = fam_tot.get('forge', 0) + 1
            continue
        scenario('forge', 'forged-' + name, 'bind_holders', SCENARIO_CAP,
                 False, planted_tool(name, forged[name]))
    relabelled = splice_before_main(tool_text, RELABEL_WRAP)
    if relabelled is None:
        errors.append('relabel: no main guard to splice before')
        fam_tot['relabel'] = fam_tot.get('relabel', 0) + 1
    else:
        scenario('relabel', 'relabel-run', 'bind_claim', SCENARIO_CAP,
                 False, planted_tool('relabel', relabelled))


if __name__ == '__main__':
    sys.exit(main())
