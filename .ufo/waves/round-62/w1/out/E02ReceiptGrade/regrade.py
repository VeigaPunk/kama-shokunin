#!/usr/bin/env python3
"""E02ReceiptGrade: independent re-grade of a kama-completion-live/v1 receipt.

Reads the receipt JSON, re-hashes every captured body, re-derives every
`checks` entry from those bytes (plus independently re-hashed model/server
files and filesystem evidence), and prints recomputed vs stored per check.

No import of tools/round62-c1-counter.py or tools/kama-completion-live.py:
predicates are re-implemented here from the receipt schema and the frozen
check reasons. The only thing read from the tool source is the pair of
digest pins the receipt is supposed to be graded against.

Usage: python3 regrade.py RECEIPT.json [--tool-source PATH] [--hold-dir DIR]
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys

FP_RE = re.compile(r'^b\d+-[0-9a-f]{9,40}$')


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def jbody(cap):
    try:
        return json.loads(cap.get('body') or '')
    except (ValueError, TypeError):
        return None


def utc(s):
    return dt.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ').replace(
        tzinfo=dt.timezone.utc)


def listen_ports():
    """Ports in LISTEN state from /proc, no external tools."""
    ports = set()
    for f in ('/proc/net/tcp', '/proc/net/tcp6'):
        try:
            with open(f) as fh:
                next(fh)
                for line in fh:
                    p = line.split()
                    local, state = p[1], p[3]
                    if state == '0A':
                        ports.add(int(local.rsplit(':', 1)[1], 16))
        except (OSError, StopIteration):
            pass
    return ports


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('receipt')
    ap.add_argument('--tool-source', default=None)
    ap.add_argument('--hold-dir', default=None)
    a = ap.parse_args()

    r = json.load(open(a.receipt))
    caps = r.get('captures') or {}
    stored = r.get('checks') or {}
    alias = r.get('alias')
    argv = r.get('argv') or []
    out = {}          # name -> recomputed True/False/None
    evidence = {}     # name -> how it was re-derived
    integrity = {}

    # -- capture integrity -------------------------------------------- #
    for name, c in caps.items():
        body = c.get('body') or ''
        h = sha256_bytes(body.encode('utf-8'))
        integrity[name] = {
            'body_sha256_stored': c.get('body_sha256'),
            'body_sha256_recomputed': h,
            'match': h == c.get('body_sha256'),
            'body_truncated': c.get('body_truncated'),
        }

    def cap(name):
        c = caps.get(name) or {}
        if not integrity.get(name, {}).get('match'):
            return None
        return c

    # -- byte-derived checks ------------------------------------------- #
    hc = cap('health')
    out['health_ready'] = bool(
        hc is not None and hc.get('status') == 200
        and hc.get('body') == '{"status":"ok"}')
    evidence['health_ready'] = 'health.body == {"status":"ok"} and status 200'

    mc = cap('models')
    mj = jbody(mc) if mc else None
    ids = ([d.get('id') for d in mj.get('data') or [] if isinstance(d, dict)]
           if isinstance(mj, dict) else None)
    out['models_alias_id'] = bool(
        mc is not None and mc.get('status') == 200 and ids == [alias])
    evidence['models_alias_id'] = f'models.data[].id == [{alias!r}] (got {ids})'

    pc = cap('props')
    pj = jbody(pc) if pc else None
    out['props_alias'] = bool(
        isinstance(pj, dict) and pj.get('model_alias') == alias)
    evidence['props_alias'] = (
        f'props.model_alias == {alias!r} '
        f'(got {(pj or {}).get("model_alias")!r})')

    c1 = cap('completion')
    cj = jbody(c1) if c1 else None
    ch0 = ((cj.get('choices') or [{}])[0]
           if isinstance(cj, dict) else {})
    env = bool(
        c1 is not None and c1.get('status') == 200
        and isinstance(cj, dict)
        and cj.get('object') == 'text_completion'
        and isinstance(cj.get('choices'), list) and cj['choices']
        and isinstance(ch0.get('text'), str))
    out['completion_envelope'] = env
    evidence['completion_envelope'] = (
        'completion status 200 + object=text_completion + '
        'choices[0].text str')
    out['completion_finish_reason'] = bool(
        env and ch0.get('finish_reason') in ('length', 'stop'))
    evidence['completion_finish_reason'] = (
        f'finish_reason in (length,stop) (got {ch0.get("finish_reason")!r})')
    out['completion_model_id'] = bool(
        env and cj.get('model') == alias)
    evidence['completion_model_id'] = (
        f'completion.model == {alias!r} (got {(cj or {}).get("model")!r})')
    fp = (cj or {}).get('system_fingerprint')
    out['completion_fingerprint'] = bool(
        env and isinstance(fp, str) and FP_RE.match(fp))
    evidence['completion_fingerprint'] = (
        f'system_fingerprint matches ^b\\d+-[0-9a-f]{{9,40}}$ (got {fp!r})')
    u = (cj or {}).get('usage') or {}
    out['completion_usage'] = bool(
        env
        and isinstance(u.get('completion_tokens'), int)
        and isinstance(u.get('prompt_tokens'), int)
        and isinstance(u.get('total_tokens'), int)
        and u['completion_tokens'] >= 1 and u['prompt_tokens'] >= 1
        and u['total_tokens'] == u['completion_tokens'] + u['prompt_tokens'])
    evidence['completion_usage'] = (
        'usage ints >=1 and total == prompt+completion '
        f'(got {u.get("prompt_tokens")}+{u.get("completion_tokens")}'
        f'={u.get("total_tokens")})')
    t = (cj or {}).get('timings') or {}
    out['completion_timings'] = bool(
        env and isinstance(t.get('predicted_n'), int)
        and t.get('predicted_n') == u.get('completion_tokens')
        and isinstance(t.get('predicted_ms'), (int, float)))
    evidence['completion_timings'] = (
        'timings.predicted_n == usage.completion_tokens and numeric '
        f'predicted_ms (got {t.get("predicted_n")} vs '
        f'{u.get("completion_tokens")}, {t.get("predicted_ms")})')
    c2 = cap('completion2')
    c2j = jbody(c2) if c2 else None
    ch02 = ((c2j.get('choices') or [{}])[0]
            if isinstance(c2j, dict) else {})
    temp = (r.get('request') or {}).get('temperature')
    out['completion_deterministic'] = bool(
        temp == 0.0 and env and c2 is not None and c2.get('status') == 200
        and isinstance(c2j, dict)
        and ch02.get('text') == ch0.get('text'))
    evidence['completion_deterministic'] = (
        'temperature==0 and completion2 choices[0].text == completion '
        f'choices[0].text (got {ch02.get("text")!r} vs {ch0.get("text")!r})')
    bc = cap('bad_request')
    bj = jbody(bc) if bc else None
    out['bad_request_graded'] = bool(
        bc is not None and bc.get('status') in (400, 500)
        and isinstance(bj, dict) and isinstance(bj.get('error'), dict))
    evidence['bad_request_graded'] = (
        f'bad_request status in (400,500) with error object '
        f'(got {bc.get("status") if bc else None})')

    # -- digest pins, read from the pinned tool source by text ---------- #
    pins = {}
    if a.tool_source:
        src = open(a.tool_source, encoding='utf-8').read()
        pins['model'] = re.search(
            r"DEFAULT_MODEL_SHA\s*=\s*\(\s*'([0-9a-f]{64})'", src).group(1)
        pins['server'] = re.search(
            r"DEFAULT_SERVER_SHA\s*=\s*'([0-9a-f]{64})'", src).group(1)
        pins['fingerprint_re'] = bool(re.search(
            r"FINGERPRINT_RE\s*=\s*re\.compile\(r'\^b\\d\+-\[0-9a-f\]\{9,40\}\$'\)",
            src))
        pins['source_sha256'] = sha256_file(a.tool_source)
    else:
        pins['model'] = r['model']['sha256']
        pins['server'] = r['server']['sha256']

    model_path = (r.get('model') or {}).get('path')
    server_path = (r.get('server') or {}).get('path')
    model_now = sha256_file(model_path) if model_path and os.path.isfile(
        model_path) else None
    server_now = sha256_file(server_path) if server_path and os.path.isfile(
        server_path) else None
    out['model_digest'] = bool(
        model_now is not None and model_now == pins['model']
        and r['model'].get('sha256') == pins['model'])
    evidence['model_digest'] = (
        f'rehash {model_path} -> {model_now}; pinned {pins["model"]}; '
        f'recorded {r["model"].get("sha256")}')
    out['server_digest'] = bool(
        server_now is not None and server_now == pins['server']
        and r['server'].get('sha256') == pins['server'])
    evidence['server_digest'] = (
        f'rehash {server_path} -> {server_now}; pinned {pins["server"]}; '
        f'recorded {r["server"].get("sha256")}')

    # -- lifecycle checks: evidence-bearing where possible -------------- #
    hold = r.get('hold') or {}
    hold_dir = a.hold_dir or hold.get('dir')
    rel = os.path.join(hold_dir, 'release') if hold_dir else None
    rel_ok = bool(rel and os.path.isfile(rel))
    rel_meta = {}
    if rel_ok:
        st = os.stat(rel)
        at = utc(r['at'])
        rel_meta = {
            'bytes': open(rel, 'rb').read().decode('utf-8', 'replace')[:16],
            'mtime_utc': dt.datetime.fromtimestamp(
                st.st_mtime, dt.timezone.utc).isoformat(),
            'seconds_after_at': round(st.st_mtime - at.timestamp(), 3),
        }
    out['hold_released'] = bool(
        hold.get('released') is True and rel_ok
        and rel_meta.get('bytes') not in (None, '')
        and 0 <= rel_meta.get('seconds_after_at', -1) <= 180)
    evidence['hold_released'] = (
        f'hold.released={hold.get("released")} and release file '
        f'{rel} {rel_meta}')

    td = r.get('teardown') or {}
    out['teardown_clean'] = bool(
        td.get('child_pre_dead') is False
        and td.get('returncode') in (0, -15))
    evidence['teardown_clean'] = (
        f'child_pre_dead={td.get("child_pre_dead")} '
        f'returncode={td.get("returncode")} (rc 0/-15)')
    port = r.get('port')
    live_ports = listen_ports()
    out['teardown_port_closed'] = bool(
        td.get('port_closed') is True and port not in live_ports)
    evidence['teardown_port_closed'] = (
        f'teardown.port_closed={td.get("port_closed")}; /proc LISTEN now '
        f'{"contains" if port in live_ports else "does not contain"} '
        f'port {port}')

    # listener_owned is a live observation at run time; the receipt stores
    # no listener evidence, so it cannot be re-derived post hoc.
    out['listener_owned'] = None
    pid = r.get('child_pid')
    pid_state = 'exists' if pid and os.path.isdir('/proc/%s' % pid) else 'gone'
    evidence['listener_owned'] = (
        'not recomputable from captured bytes: no listener evidence is '
        'stored; the tool recorded it after _live.port_owned_by(pid, port) '
        'at run time (child_pid=%s, port=%s; /proc/%s %s)'
        % (pid, port, pid, pid_state))

    # -- argv / registration consistency (extra, not a stored check) ---- #
    def argv_val(flag):
        for i, x in enumerate(argv[:-1]):
            if x == flag:
                return argv[i + 1]
        return None

    extra = {
        'argv_alias_matches': argv_val('--alias') == alias,
        'argv_port_matches': argv_val('--port') == str(port),
        'argv_model_matches': argv_val('--model') == model_path,
        'argv_server0_matches': bool(argv) and argv[0] == server_path,
        'argv_host_loopback': argv_val('--host') == '127.0.0.1',
        'port_not_listening_now': port not in live_ports,
    }

    # -- compare -------------------------------------------------------- #
    rows = []
    agree = mismatch = nonre = 0
    for name in stored:
        rec = out.get(name)
        stv = stored[name].get('passed')
        if name not in out:
            status = 'MISSING-FROM-REGRAde'
        elif rec is None:
            status = 'NOT-RECOMPUTABLE'
            nonre += 1
        elif rec == stv:
            status = 'AGREE'
            agree += 1
        else:
            status = 'MISMATCH'
            mismatch += 1
        rows.append({'check': name, 'recomputed': rec, 'stored': stv,
                     'status': status, 'evidence': evidence.get(name)})
    unlisted = sorted(set(out) - set(stored))

    evaluated = all(v.get('evaluated') for v in stored.values())
    all_pass = all(v.get('passed') for v in stored.values())
    verdict_expected = 'REQUEST_OK' if (evaluated and all_pass) else 'FAIL'
    verdict_ok = r.get('verdict') == verdict_expected

    result = {
        'verdict_recomputed': verdict_expected,
        'verdict_consistent': verdict_ok,
        'receipt': a.receipt,
        'schema': r.get('schema'),
        'verdict': r.get('verdict'),
        'nonce': r.get('nonce'),
        'at': r.get('at'),
        'alias': alias,
        'port': port,
        'child_pid': r.get('child_pid'),
        'capture_integrity': integrity,
        'pins': pins,
        'extra': extra,
        'checks': rows,
        'tally': {'stored': len(stored), 'recomputed_true': sum(
            1 for v in out.values() if v is True),
            'recomputed_false': sum(1 for v in out.values() if v is False),
            'agree': agree, 'mismatch': mismatch,
            'not_recomputable': nonre,
            'recomputed_not_in_stored': unlisted},
    }
    print(json.dumps(result, indent=1, sort_keys=True))
    ok = (mismatch == 0 and verdict_ok and integrity and
          all(v['match'] and not v['body_truncated']
              for v in integrity.values()))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
