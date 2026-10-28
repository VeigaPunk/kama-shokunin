#!/usr/bin/env python3
"""Round-64 C1 counter: the process that answers is the pinned llama-server.

Usage: python3 tools/round64-c1-counter.py --repo REPO --tip REV --work DIR

Frozen predicate (same sentence as .ufo/waves/round-64/controls/freeze.txt):
  C1-r64: at the tip, the byte-pinned tools/kama-completion-live.py (schema
  kama-completion-live/v3) runs one counter-opened hold-mode live request-
  plane lifecycle on the pinned llama.cpp fixture whose receipt the counter
  re-derives from captured bytes, and the counter - from procfs and its own
  code alone, loading nothing from the tip - binds the process that answers
  to the pinned server: every holder of the run-port listener is the hold
  pid, its /proc/<pid>/exe re-hashes to the pinned llama-server digest at
  the server path the counter chose, its argv, initial environment and
  mapped files are the pinned set, it is a descendant of the tool process
  started after the tool did, the hold.json is fresh, and teardown (the
  holder gone, the port closed) is observed by the counter after the
  counter's own release; the held child's answers to two outside probes
  drawn at random per run (prompt length and n_predict) agree with a
  reference pinned server the counter itself starts; and all 76 targeted
  controls - including live forged tools (the round-63 forgeries replayed,
  a detached server, a forwarding proxy, a canned answerer, stale holds,
  a preload, a path-copied server) - are each rejected by the check each
  names, family by family at the declared counts, and the counter's own
  evaluator refuses all 3 planted wrong-reason controls, errors=0.

The counter never trusts receipt-claimed results and imports nothing from
the tip. A control counts as rejected only when the failure set of its
re-score contains the named check and stays within the cap. Output: one
line, exit 0 iff met. Every scratch path is under --work.
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
PROMPT = 'The cat sat on the'
EXPECT_EVAL_SELFTEST = 3
MAX_COLLATERAL = 5      # failing checks a one-field control may cause
ENVELOPE_CAP = 30       # an envelope failure legitimately cascades
SCENARIO_CAP = 14       # a live forged tool cascades through its run
EXPECT_FAMILIES = {
    'stale': 1, 'log': 1, 'tamper': 8, 'predead': 1, 'sigterm': 1,
    'hold': 1, 'outside': 1, 'hdr': 2, 'trunc': 2, 'timing': 4,
    'shape': 4, 'idcr': 3, 'ptok': 2, 'reqbind': 2, 'listener': 1,
    'digest': 1, 'schema': 1, 'witness': 5,
    # round-64 families
    'bind': 20, 'runfield': 4, 'detach': 1, 'forge': 3, 'proxy': 1,
    'canned': 1, 'stalehold': 2, 'preload': 1, 'pathcopy': 1, 'relabel': 1,
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
_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
_HASH_CACHE = {}
_TOOL_ENV_KEYS = ('PATH', 'HOME', 'LANG', 'LC_ALL', 'TMPDIR')


def git(repo, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    return subprocess.run(['git', '-C', str(repo), *args],
                          capture_output=True, env=env)


def blob(repo, rev, path):
    p = git(repo, 'show', f'{rev}:{path}')
    return p.stdout if p.returncode == 0 else None


def sha256_b(b):
    return hashlib.sha256(b).hexdigest()


def sha256_path(path, cache=True):
    if cache and path in _HASH_CACHE:
        return _HASH_CACHE[path]
    try:
        h = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(1 << 20), b''):
                h.update(chunk)
        d = h.hexdigest()
    except (OSError, TypeError):
        d = None
    if cache:
        _HASH_CACHE[path] = d
    return d


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


def holder_pids(inodes):
    """(pids holding a socket:[inode] fd, own-uid pids whose fd table was
    unreadable). Fails closed on unreadable own-uid tables."""
    wanted = {f'socket:[{i}]' for i in inodes}
    pids, unreadable = set(), set()
    me = os.getuid()
    for name in os.listdir('/proc'):
        if not name.isdigit():
            continue
        pid = int(name)
        try:
            fds = os.listdir(f'/proc/{pid}/fd')
        except PermissionError:
            try:
                if os.stat(f'/proc/{pid}').st_uid == me:
                    unreadable.add(pid)
            except OSError:
                pass
            continue
        except OSError:
            continue
        for fd in fds:
            try:
                if os.readlink(f'/proc/{pid}/fd/{fd}') in wanted:
                    pids.add(pid)
                    break
            except OSError:
                continue
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
        out.append({'path': path, 'deleted': deleted, 'sha256': sha})
    return out


def holder_record(pid, server_dir):
    """One holder's procfs record. None fields mean unreadable."""
    rec = {'pid': pid}
    try:
        rec['exe'] = os.readlink(f'/proc/{pid}/exe')
        rec['exe_sha256'] = sha256_path(f'/proc/{pid}/exe', cache=False)
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
        rec['environ_keys'] = sorted(
            e.split(b'=', 1)[0].decode('utf-8', 'replace')
            for e in raw.split(b'\0') if e)
    except OSError:
        rec['environ_keys'] = None
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
        'tool_pid': tool_pid, 'tool_start_ticks': tool_ticks,
        'server_path': server_path, 'model_path': model_path,
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
        if not a or os.path.realpath(a[0]) != sp:
            return False
        port = _flag_values(a, '--port')
        host = _flag_values(a, '--host')
        alias = _flag_values(a, '--alias')
        model = _flag_values(a, '--model')
        return (port == [str(raw.get('port'))] and host == ['127.0.0.1']
                and alias == [ALIAS] and len(model) == 1
                and os.path.realpath(model[0]) == mp
                and sha256_path(os.path.realpath(model[0])) == MODEL_SHA)
    out['bind_argv'] = bool(hs) and all(argv_ok(h) for h in hs)
    out['bind_env'] = bool(hs) and all(
        h.get('environ_keys') is not None and not any(
            k.startswith('LD_') or k.startswith('GLIBC_TUNABLES')
            for k in h['environ_keys']) for h in hs)

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
    out['hold_fresh'] = bool(
        hs and is_int(mt) and is_int(t0) and mt > t0 and is_int(tt)
        and all(is_int(h.get('start_ticks')) and h['start_ticks'] >= tt
                for h in hs)
        and raw.get('hold_schema') == 'kama-completion-hold/v1')
    return out


BIND_CHECKS = ('bind_listener', 'bind_holders', 'bind_exe', 'bind_argv',
               'bind_env', 'bind_maps', 'bind_ancestry', 'hold_fresh')


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
        and rj.get('prompt') == PROMPT)
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
    raw_a, raw_b = bnd.get('raw_a'), bnd.get('raw_b')
    for k, v in grade_binding(raw_a).items():
        if v is not True:
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


def draw_probes(rng, nonce):
    """Two probe requests whose prompt length and n_predict are drawn per
    run; distinct from each other and from the tool's fixed request."""
    out, used = [], set()
    while len(out) < 2:
        k = rng.randint(2, 24)
        n = rng.randint(3, 9)
        if (k, n) in used:
            continue
        used.add((k, n))
        words = ' '.join(rng.choice(VOCAB) for _ in range(k))
        out.append({'prompt': f'{nonce} {words}', 'n_predict': n,
                    'seed': rng.randint(1, 9999)})
    return out


def probe(port, req):
    payload = {'prompt': req['prompt'], 'n_predict': req['n_predict'],
               'temperature': 0.0, 'seed': req['seed']}
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
    """True when the pid no longer exists, was reused, or is a zombie /
    dead entry (its sockets are closed; only the exit status is pending)."""
    pp, tk = stat_fields(pid)
    if pp is None or tk != ticks:
        return True
    try:
        s = open(f'/proc/{pid}/stat', encoding='ascii').read()
        return s[s.rindex(')') + 2] in 'ZX'
    except (OSError, ValueError, IndexError):
        return True


def witness_run(work, label, tool_path, server_path, model_path, reqs,
                extra_env=None):
    """Run one tool (the tip tool or a planted forger) in hold mode. The
    counter creates the hold dir, owns hold.json's freshness, probes the
    listener, releases, and observes teardown itself. Returns
    (receipt|None, witness|None, binding|None, nonce, notes)."""
    wd = os.path.join(work, label)
    os.makedirs(wd, exist_ok=True)
    hold = os.path.join(wd, 'hold')
    os.makedirs(hold, mode=0o700, exist_ok=True)
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
         '--hold-dir', hold, '--hold-timeout', '90', '--out', out_path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
    tool_ticks = start_ticks_of(proc.pid)
    witness = binding = None
    hold_doc = None
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
            probes = [probe(port, r) for r in reqs]
            raw_b = collect(port, hold_doc, mtime, t0_ns, proc.pid,
                            tool_ticks, server_path, model_path)
            witness = {
                'probes': probes, 'hold_pid': hold_doc.get('pid'),
                'hold_port': port, 'server_sha256':
                hold_doc.get('server_sha256'),
                'model_sha256': hold_doc.get('model_sha256'),
                'alias': hold_doc.get('alias')}
            binding = {'raw_a': raw_a, 'raw_b': raw_b}
            break
        if proc.poll() is not None:
            notes.append('tool exited before hold.json')
            break
        time.sleep(0.1)
    # counter-owned release, then counter-observed teardown
    open(os.path.join(hold, 'release'), 'w').write('go\n')
    gone = port_closed = False
    if binding is not None:
        hs = (binding['raw_a'] or {}).get('holders') or []
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            gone = all(pid_gone(h['pid'], h.get('start_ticks'))
                       for h in hs)
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
    receipt = None
    try:
        receipt = json.load(open(out_path))
    except (ValueError, OSError):
        pass
    return receipt, witness, binding, nonce, notes


# --------------------------------------------------------- planted forgers #

FAKE_COMMON = r'''
import argparse, json, os, signal, socket, subprocess, sys, time
import http.server, threading, urllib.request, urllib.error
ap = argparse.ArgumentParser()
for a in ('--nonce', '--work', '--server', '--model', '--model-sha256',
          '--server-sha256', '--alias', '--hold-dir', '--hold-timeout',
          '--out'):
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
           if k in ('PATH', 'HOME', 'LANG', 'LC_ALL', 'TMPDIR')}
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
    # a fake that writes a genuine receipt copy and dies before hold.json
    'crash': r'''
r = json.loads(json.dumps(TPL))
r['nonce'] = A.nonce
json.dump(r, open(A.out, 'w'))
sys.exit(3)
''',
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
    """Apply a unified diff to the tool text with `patch`; returns the
    patched text or None."""
    d = os.path.join(workdir, name)
    os.makedirs(os.path.join(d, 'tools'), exist_ok=True)
    tp = os.path.join(d, 'tools', 'kama-completion-live.py')
    with open(tp, 'w') as f:
        f.write(tip_tool_text)
    pp = os.path.join(d, 'x.patch')
    with open(pp, 'w') as f:
        f.write(patch_text)
    r = subprocess.run(['patch', '-p1', '-F3', '-s', '-i', pp, '-d', d],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return open(tp).read()


def forge_variants(repo, tip, work):
    """Planted forged tools: the round-63 patches replayed on the tip tool
    (A: canned fake behind the real child's inherited listener; B: no
    llama-server at all) and each with the tool's own holder bookkeeping
    fabricated so the tool-side check cannot be what rejects it."""
    tool = blob(repo, tip, 'tools/kama-completion-live.py')
    pa = blob(repo, tip, '.ufo/waves/round-64/controls/forge-A-realchild.patch')
    pb = blob(repo, tip, '.ufo/waves/round-64/controls/forge-B-sleeper-delta.patch')
    if not (tool and pa and pb):
        return {}
    tool = tool.decode()
    a = apply_patch(tool, pa.decode(), work, 'forgeA-build')
    if a is None:
        return {}
    ab = apply_patch(a, pb.decode(), work, 'forgeAB-build')
    fab = "holders = [{'pid': proc.pid, 'exe': server, 'exe_sha256': server_sha}]"
    out = {'forgeA': a}
    if 'holders = _proc_holders(port)' in a:
        out['forgeA2'] = a.replace('holders = _proc_holders(port)', fab)
    if ab is not None and 'holders = _proc_holders(port)' in ab:
        out['forgeB2'] = ab.replace('holders = _proc_holders(port)', fab)
    return out


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
        c['request_body'] = c['request_body'].replace(PROMPT, 'Other text')
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
    add('bind', 'bind_env', bm=bm(lambda r: r['holders'][0].update(
        {'environ_keys': r['holders'][0]['environ_keys'] + ['LD_PRELOAD']})))
    add('bind', 'bind_env', bm=bm(lambda r: r['holders'][0].update(
        {'environ_keys': r['holders'][0]['environ_keys']
         + ['GLIBC_TUNABLES']})))
    add('bind', 'bind_env', bm=bm(
        lambda r: r['holders'][0].update({'environ_keys': None})))
    add('bind', 'bind_maps', bm=bm(lambda r: r['holders'][0]['maps'].append(
        {'path': '/memfd:evil (deleted)', 'deleted': True, 'sha256': None})))
    add('bind', 'bind_maps', bm=bm(lambda r: r['holders'][0]['maps'].append(
        {'path': '/tmp/evil.so', 'deleted': False, 'sha256': '0' * 64})))
    add('bind', 'bind_maps', bm=bm(lambda r: next(
        m for m in r['holders'][0]['maps']
        if m.get('sha256') and m['path'].endswith('.so.0.7.0')).update(
        {'sha256': '1' * 64})))
    add('bind', 'bind_ancestry', bm=bm(
        lambda r: r.update({'tool_pid': 1})))
    add('bind', 'hold_fresh', bm=bm(
        lambda r: r.update({'hold_mtime_ns': r['t0_ns'] - 1})))
    add('bind', 'hold_fresh', bm=bm(lambda r: r['holders'][0].update(
        {'start_ticks': r['tool_start_ticks'] - 1})))
    add('bind', 'teardown_observed', bm=lambda b: {
        **clone(b), 'teardown': {'gone': False, 'port_closed': True}})
    add('bind', 'bind_stable', bm=lambda b: {**clone(b), 'raw_b': {
        **clone(b['raw_b']), 'holders': []}})
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


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True)
    ap.add_argument('--tip', required=True)
    ap.add_argument('--work', required=True)
    args = ap.parse_args(argv)
    work = os.path.abspath(args.work)
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
    if not errors:
        rng = random.Random(int.from_bytes(os.urandom(8), 'big'))
        probe_nonce = 'r64p' + hashlib.sha256(os.urandom(8)).hexdigest()[:8]
        reqs = draw_probes(rng, probe_nonce)
        ref = reference_run(server, model, reqs, work)
        if len(ref) != 2:
            errors.append('reference server produced no answers')
        receipt, witness, binding, nonce, notes = witness_run(
            work, 'live', tool_path, server, model, reqs)
        NONCE = nonce
        # the probes carry the probe nonce; the receipt carries the tool
        # nonce: bind both to this run
        if witness is not None:
            witness['ref'] = ref
        if receipt is None or witness is None or binding is None:
            errors.append('live: no receipt/witness produced ' + '; '.join(
                notes))
        else:
            s = score_run(receipt, witness, binding, probe_nonce)
            live_ok = 1 if s['met'] else 0
            if not s['met']:
                errors.append('live: ' + json.dumps(sorted(s['fails'])))
    if live_ok == 1:
        run_controls(args, work, tool_path, server, model, receipt,
                     witness, binding, reqs, probe_nonce, fam_tot, fam_ok,
                     detail, errors)
        st = eval_selftest_run(receipt, witness, binding, probe_nonce)
    total = sum(fam_tot.values())
    rejected = sum(fam_ok.values())
    fam_match = fam_tot == EXPECT_FAMILIES and fam_ok == EXPECT_FAMILIES
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


def score_run(receipt, witness, binding, probe_nonce):
    """score() with the per-run probe nonce standing in for the witness
    nonce check (the tool's own nonce is graded through nonce_match)."""
    s = score(receipt, witness, binding)
    # the probes carry the per-run probe nonce
    if not all(probe_nonce in ((p or {}).get('sent_prompt') or '')
               for p in (witness or {}).get('probes') or []):
        s['fails'].add('live_nonce')
    s['met'] = not s['fails']
    return s


def eval_selftest_run(receipt, witness, binding, probe_nonce):
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
    return n


def run_controls(args, work, tool_path, server, model, receipt, witness,
                 binding, reqs, probe_nonce, fam_tot, fam_ok, detail,
                 errors):
    global NONCE
    def credit(fam, s, expect, cap, label, clean_receipt=False):
        hit = is_hit(s, expect, cap)
        if hit and clean_receipt:
            # a forger holding a genuine receipt copy passes every
            # receipt-level check; a receipt-level failure means the fake
            # crashed or garbled the receipt, which is not the named reason
            hit = not any(k in RECEIPT_LEVEL or k.startswith('inconsistent:')
                          for k in s['fails'])
        fam_tot[fam] = fam_tot.get(fam, 0) + 1
        fam_ok[fam] = fam_ok.get(fam, 0) + int(hit)
        if not hit:
            detail.append(f'escape {fam}/{label} expect={expect} '
                          f'met={s["met"]} nfails={len(s["fails"])} '
                          f'fails={sorted(s["fails"])[:8]}')

    for fam, m, wm, bm, expect, cap in build_controls(
            receipt, witness, binding, work):
        w = wm(witness) if wm else witness
        b = bm(binding) if bm else binding
        credit(fam, score_run(m, w, b, probe_nonce), expect, cap, expect)

    # relabel control: the base-style v2 tool with its schema string
    # changed to v3 (no holder bookkeeping) must not pass
    tool = blob(args.repo, args.tip, 'tools/kama-completion-live.py')
    # live forged tools, all through the same witness_run + score path
    tpl = os.path.join(work, 'genuine-receipt.json')
    with open(tpl, 'w') as f:
        json.dump(receipt, f)
    stale_doc = os.path.join(work, 'stale-hold.json')
    with open(stale_doc, 'w') as f:
        json.dump({'schema': 'kama-completion-hold/v1',
                   'port': (witness or {}).get('hold_port'),
                   'pid': (witness or {}).get('hold_pid'),
                   'alias': ALIAS, 'model_sha256': MODEL_SHA,
                   'server_sha256': SERVER_SHA, 'prompt': PROMPT,
                   'at': '2026-10-28T00:00:00Z'}, f)
    env_base = {'KAMA_FAKE_TEMPLATE': tpl, 'KAMA_FAKE_STALE': stale_doc}
    plan = [('crash', 'detach', 'crash', 'bind_ancestry'),
            ('proxy', 'proxy', 'proxy', 'bind_holders'),
            ('canned', 'canned', 'canned', 'bind_exe'),
            ('stale_old', 'stalehold', 'stale_old', 'hold_fresh'),
            ('stale_future', 'stalehold', 'stale_future', 'hold_fresh'),
            ('preload', 'preload', 'preload', 'bind_env'),
            ('pathcopy', 'pathcopy', 'pathcopy', 'bind_exe')]
    for mode, fam, label, expect in plan:
        try:
            fake = write_fake(work, mode)
            env = dict(env_base, KAMA_FAKE_MODE=mode)
            r, w, b, nonce, notes = witness_run(
                work, 'fake-' + label, fake, server, model, reqs, env)
            ref = (witness or {}).get('ref')
            if w is not None:
                w['ref'] = ref
            if r is None:
                detail.append(f'fake {label}: no receipt/witness '
                              f'{notes}')
                fam_tot[fam] = fam_tot.get(fam, 0) + 1
                continue
            saved, NONCE = NONCE, nonce
            try:
                s = score_run(r, w, b, probe_nonce)
            finally:
                NONCE = saved
            credit(fam, s, expect, 99, label, clean_receipt=True)
        except Exception as e:  # a control that cannot run is not credit
            errors.append(f'fake {label}: {type(e).__name__}: {e}')
            fam_tot[fam] = fam_tot.get(fam, 0) + 1
    forged = forge_variants(args.repo, args.tip, work)
    for name in ('forgeA', 'forgeA2', 'forgeB2'):
        fam_tot_before = fam_tot.get('forge', 0)
        if name not in forged:
            fam_tot['forge'] = fam_tot.get('forge', 0) + 1
            detail.append(f'forge {name}: patch did not apply to the tip tool')
            continue
        d = os.path.join(work, 'forge-' + name)
        os.makedirs(os.path.join(d, 'tools'), exist_ok=True)
        # the forged tool imports tools/kama-llamacpp-live.py from its tree
        shutil.copy(os.path.join(os.path.dirname(tool_path),
                                 'kama-llamacpp-live.py'),
                    os.path.join(d, 'tools', 'kama-llamacpp-live.py'))
        os.makedirs(os.path.join(d, 'registry'), exist_ok=True)
        rg = os.path.join(os.path.dirname(os.path.dirname(tool_path)),
                          'registry', 'endpoint-consumers.tsv')
        if os.path.exists(rg):
            shutil.copy(rg, os.path.join(d, 'registry',
                                         'endpoint-consumers.tsv'))
        fp = os.path.join(d, 'tools', 'kama-completion-live.py')
        with open(fp, 'w') as f:
            f.write(forged[name])
        try:
            r, w, b, nonce, notes = witness_run(
                work, 'forged-' + name, fp, server, model, reqs)
            if w is not None:
                w['ref'] = (witness or {}).get('ref')
            if r is None or w is None or b is None:
                # a forger whose tool crashes is not a forgery that was
                # rejected by the named check: no credit
                detail.append(f'forge {name}: no receipt/witness {notes}')
                fam_tot['forge'] = fam_tot.get('forge', 0) + 1
                continue
            saved, NONCE = NONCE, nonce
            try:
                s = score_run(r, w, b, probe_nonce)
            finally:
                NONCE = saved
            credit('forge', s, 'bind_holders', SCENARIO_CAP, name)
        except Exception as e:
            errors.append(f'forge {name}: {type(e).__name__}: {e}')
            fam_tot['forge'] = fam_tot.get('forge', 0) + 1
    # relabel: the tip tool with its holder bookkeeping stripped while it
    # keeps the v3 schema string - what a v2 tool that only changed its
    # schema line would emit
    relabel_ok = False
    text = (tool or b'').decode()
    mark = "receipt['listener_holders'] = holders"
    if mark in text and "check('listener_holders_pinned'," in text:
        stripped = text.replace(
            mark, "receipt.pop('listener_holders', None)").replace(
            "check('listener_holders_pinned',",
            "check('listener_holders_pinned_x',")
        d = os.path.join(work, 'relabel')
        os.makedirs(os.path.join(d, 'tools'), exist_ok=True)
        os.makedirs(os.path.join(d, 'registry'), exist_ok=True)
        shutil.copy(os.path.join(os.path.dirname(tool_path),
                                 'kama-llamacpp-live.py'),
                    os.path.join(d, 'tools', 'kama-llamacpp-live.py'))
        rg = os.path.join(os.path.dirname(os.path.dirname(tool_path)),
                          'registry', 'endpoint-consumers.tsv')
        if os.path.exists(rg):
            shutil.copy(rg, os.path.join(d, 'registry',
                                         'endpoint-consumers.tsv'))
        fp = os.path.join(d, 'tools', 'kama-completion-live.py')
        with open(fp, 'w') as f:
            f.write(stripped)
        try:
            r, w, b, nonce, notes = witness_run(
                work, 'relabel-run', fp, server, model, reqs)
            if w is not None:
                w['ref'] = (witness or {}).get('ref')
            if r is not None and w is not None and b is not None:
                saved, NONCE = NONCE, nonce
                try:
                    s = score_run(r, w, b, probe_nonce)
                finally:
                    NONCE = saved
                credit('relabel', s, 'bind_claim', SCENARIO_CAP, 'relabel')
                relabel_ok = True
        except Exception as e:
            errors.append(f'relabel: {type(e).__name__}: {e}')
    if not relabel_ok:
        fam_tot['relabel'] = fam_tot.get('relabel', 0) + 1
        detail.append('relabel: could not run')


if __name__ == '__main__':
    sys.exit(main())
