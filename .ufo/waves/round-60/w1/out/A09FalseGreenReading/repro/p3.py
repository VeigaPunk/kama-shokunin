#!/usr/bin/env python3
"""kama-ollama-live.py — ephemeral lane-owned Ollama server lifecycle harness (round 60).

Domain: local model serving & endpoint health (kama-shokunin). Capability
acquisition tool, the Ollama counterpart of ``kama-llamacpp-live.py``: it starts
the digest-pinned official Ollama release binary (``registry/ollama-live-pin.tsv``)
on a free loopback port that is never a registered consumer port, imports the
digest-pinned lane fixture GGUF as a model named after a caller-supplied nonce,
captures the HTTP surfaces (``/api/version``, ``/api/tags``, ``/api/ps``,
``/v1/models``, ``/v1/models/<id>``, ``/api/show``), replays the captures through
``tools/kama-ollama-evidence.py`` before and after one short generation, then tears
the server down and proves the teardown.

It is a lane-owned child, not service restoration: no ``~/.config``, ``~/.omp`` or
systemd write; HOME, model store and log live under the caller's ``--work`` dir
(which the tool never deletes - the caller owns cleanup). It does not touch any
registered consumer or listening port. Like the llama.cpp fixture it proposes a
narrowing of "L0 must approve any endpoint outside the declared registry" only for
the process this tool starts, pending L0 ratification.

Usage:
  python3 tools/kama-ollama-live.py --work DIR [--nonce N] [--out receipt.json]
         [--ollama-bin PATH] [--model-gguf PATH] [--no-generate]

Exit codes: 0 every evaluated check passed (verdict MODEL_OK); 1 at least one
check failed; 2 setup error or not evaluated (including a binary whose sha256 is
not the pinned release's: verdict BINARY_DIGEST_MISMATCH).
Receipt schema ``kama-ollama-live/v1``: nonce echo, pin block, per-capture
``{status, sha256, body}``, per-check ``{id, passed, evaluated, detail}``,
``observations`` (non-graded facts such as the empty ``/v1/models`` body form),
teardown proof. Environment values are never recorded.

A green receipt proves one lane-owned child served one fixture model on one
loopback port for the length of the run. It is not registered-consumer health, not
model quality, not GPU/CPU placement evidence and not other Ollama versions.
Deps: python3 stdlib only.
"""
from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
import re
import secrets
import signal
import socket
import subprocess
import sys
import time

SCHEMA = 'kama-ollama-live/v1'
REPO = '/home/vgpnk/Projects/shokunin/kama-shokunin'
PIN_FILE = os.path.join(REPO, 'registry', 'ollama-live-pin.tsv')
REGISTERED_PORTS = {8080, 34113}
NONCE_RE = re.compile(r'^[a-z0-9]{8,32}$')
READY_TIMEOUT = 90.0
CREATE_TIMEOUT = 180
GENERATE_TIMEOUT = 180
TEARDOWN_TIMEOUT = 30.0


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def load_pin(path=PIN_FILE):
    pin = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or not line.strip() or line.startswith('key\t'):
                continue
            parts = line.rstrip('\n').split('\t')
            if len(parts) >= 2:
                pin[parts[0]] = parts[1]
    for key in ('version', 'bin_sha256', 'archive_sha256', 'model_sha256', 'default_home',
                'default_model'):
        if key not in pin:
            raise ValueError(f'pin file lacks {key}')
    return pin


def listening_ports():
    ports = set()
    for name in ('/proc/net/tcp', '/proc/net/tcp6'):
        try:
            with open(name) as f:
                next(f)
                for line in f:
                    cols = line.split()
                    if len(cols) > 3 and cols[3] == '0A':
                        ports.add(int(cols[1].rsplit(':', 1)[1], 16))
        except OSError:
            pass
    return ports


def free_port():
    for _ in range(50):
        s = socket.socket()
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
        s.close()
        if port not in REGISTERED_PORTS and port not in listening_ports():
            return port
    raise RuntimeError('no free unregistered loopback port')


def listener_inodes(port):
    inodes = set()
    for name in ('/proc/net/tcp', '/proc/net/tcp6'):
        try:
            with open(name) as f:
                next(f)
                for line in f:
                    cols = line.split()
                    if len(cols) > 9 and cols[3] == '0A' and int(cols[1].rsplit(':', 1)[1], 16) == port:
                        inodes.add(cols[9])
        except OSError:
            pass
    return inodes


def pid_owns_listener(pid, port):
    want = {f'socket:[{i}]' for i in listener_inodes(port)}
    if not want:
        return False
    try:
        for fd in os.listdir(f'/proc/{pid}/fd'):
            try:
                if os.readlink(f'/proc/{pid}/fd/{fd}') in want:
                    return True
            except OSError:
                pass
    except OSError:
        return False
    return False


def http_call(port, method, path, body=None, timeout=30):
    conn = http.client.HTTPConnection('127.0.0.1', port, timeout=timeout)
    try:
        headers = {}
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            headers['Content-Type'] = 'application/json'
        conn.request(method, path, body=data, headers=headers)
        resp = conn.getresponse()
        raw = resp.read()
        return resp.status, raw
    finally:
        conn.close()


def capture(name, status, raw):
    return {'name': name, 'status': status, 'sha256': hashlib.sha256(raw).hexdigest(),
            'body': raw.decode('utf-8', 'replace')}


def port_closed(port):
    s = socket.socket()
    s.settimeout(2)
    try:
        s.connect(('127.0.0.1', port))
        return False
    except OSError:
        return True
    finally:
        s.close()


def child_env(work, port):
    home = os.path.join(work, 'home')
    return {
        'PATH': '/usr/bin:/bin',
        'HOME': home,
        'OLLAMA_HOST': f'127.0.0.1:{port}',
        'OLLAMA_MODELS': os.path.join(work, 'models'),
        'OLLAMA_NO_CLOUD': '1',
        'OLLAMA_NOPRUNE': '1',
        'CUDA_VISIBLE_DEVICES': '-1',
        'HIP_VISIBLE_DEVICES': '-1',
        'GGML_VK_VISIBLE_DEVICES': '-1',
    }


def run_evidence(work, tags_raw, ps_raw, expect, label):
    tags_path = os.path.join(work, f'evidence-{label}-tags.json')
    ps_path = os.path.join(work, f'evidence-{label}-ps.json')
    with open(tags_path, 'wb') as f:
        f.write(tags_raw)
    with open(ps_path, 'wb') as f:
        f.write(ps_raw)
    p = subprocess.run([sys.executable, os.path.join(REPO, 'tools', 'kama-ollama-evidence.py'),
                        '--tags', tags_path, '--ps', ps_path, '--expect', expect],
                       capture_output=True, text=True, timeout=60)
    try:
        finding = json.loads(p.stdout).get('finding_id')
    except ValueError:
        finding = None
    return finding, p.returncode


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--work', required=True, help='scratch dir for HOME, model store, log (caller deletes)')
    ap.add_argument('--nonce', default=None)
    ap.add_argument('--out', default=None)
    ap.add_argument('--ollama-bin', default=None)
    ap.add_argument('--model-gguf', default=None)
    ap.add_argument('--no-generate', action='store_true')
    args = ap.parse_args(argv)

    started = time.time()
    receipt = {'schema': SCHEMA, 'verdict': 'NOT_EVALUATED', 'nonce': None, 'pin': None,
               'checks': [], 'captures': {}, 'observations': {}, 'teardown': None,
               'argv_child': None}
    checks = receipt['checks']

    def check(cid, passed, detail, evaluated=True):
        checks.append({'id': cid, 'passed': bool(passed) if evaluated else None,
                       'evaluated': evaluated, 'detail': detail})
        return bool(passed) if evaluated else False

    def finish(verdict, code):
        receipt['verdict'] = verdict
        receipt['elapsed_s'] = round(time.time() - started, 2)
        text = json.dumps(receipt, indent=1, sort_keys=True)
        if args.out:
            with open(args.out, 'w', encoding='utf-8') as f:
                f.write(text + '\n')
        print(text)
        return code

    try:
        pin = load_pin()
    except (OSError, ValueError) as exc:
        receipt['setup_error'] = f'pin-unreadable: {exc}'
        return finish('SETUP_ERROR', 2)
    receipt['pin'] = {k: pin[k] for k in ('version', 'bin_sha256', 'archive_sha256', 'model_sha256')}
    nonce = args.nonce or secrets.token_hex(6)
    if not NONCE_RE.match(nonce):
        receipt['setup_error'] = 'nonce-invalid'
        return finish('SETUP_ERROR', 2)
    receipt['nonce'] = nonce
    work = os.path.abspath(args.work)
    os.makedirs(os.path.join(work, 'home'), exist_ok=True)
    os.makedirs(os.path.join(work, 'models'), exist_ok=True)

    binary = os.path.realpath(os.path.expanduser(args.ollama_bin or os.path.join(os.path.expanduser(pin['default_home']), 'bin', 'ollama')))
    gguf = os.path.realpath(os.path.expanduser(args.model_gguf or pin['default_model']))
    try:
        bin_sha = sha256_file(binary)
    except OSError as exc:
        receipt['setup_error'] = f'binary-unreadable: {exc.strerror}'
        return finish('SETUP_ERROR', 2)
    receipt['binary_sha256'] = bin_sha
    if not check('binary-digest', bin_sha == pin['bin_sha256'],
                 f'sha256 of the server file is {"" if bin_sha == pin["bin_sha256"] else "not "}the pinned release binary'):
        return finish('BINARY_DIGEST_MISMATCH', 2)
    try:
        model_sha = sha256_file(gguf)
    except OSError as exc:
        receipt['setup_error'] = f'model-unreadable: {exc.strerror}'
        return finish('SETUP_ERROR', 2)
    if not check('model-digest', model_sha == pin['model_sha256'], 'fixture GGUF sha256 equals the pinned digest'):
        return finish('MODEL_DIGEST_MISMATCH', 2)

    port = free_port()
    receipt['port'] = port
    check('port-unregistered', port not in REGISTERED_PORTS and port not in listening_ports(),
          'chosen loopback port is neither a registered consumer port nor listening before start')
    env = child_env(work, port)
    log_path = os.path.join(work, 'serve.log')
    receipt['argv_child'] = [binary, 'serve']
    log = open(log_path, 'wb')
    proc = subprocess.Popen([binary, 'serve'], env=env, stdout=log, stderr=subprocess.STDOUT,
                            cwd=work, start_new_session=True)
    rc_fail = False
    try:
        deadline = time.time() + READY_TIMEOUT
        ready = False
        while time.time() < deadline and proc.poll() is None:
            try:
                st, raw = http_call(port, 'GET', '/', timeout=3)
                if st == 200:
                    receipt['captures']['root'] = capture('root', st, raw)
                    ready = raw.strip() == b'Ollama is running'
                    break
            except (OSError, http.client.HTTPException):
                time.sleep(0.3)
        check('ready', ready, 'GET / returned 200 "Ollama is running" before the timeout')
        if not ready:
            rc_fail = True
            raise RuntimeError('not-ready')

        st, raw = http_call(port, 'GET', '/api/version')
        receipt['captures']['version'] = capture('version', st, raw)
        try:
            version = json.loads(raw).get('version')
        except ValueError:
            version = None
        check('version', st == 200 and version == pin['version'], f'/api/version reports {version!r}; pin {pin["version"]!r}')
        try:
            exe_sha = sha256_file(f'/proc/{proc.pid}/exe')
        except OSError:
            exe_sha = None
        check('running-exe-digest', exe_sha == pin['bin_sha256'], '/proc/<child pid>/exe sha256 equals the pinned binary')
        check('listener-owned', pid_owns_listener(proc.pid, port), 'the listening socket on the port is held by the child pid')
        try:
            with open(f'/proc/{proc.pid}/environ', 'rb') as _ef:
                _envdump = _ef.read()
        except OSError:
            _envdump = b''
        with open(os.path.join(work, 'child-environ.txt'), 'wb') as _f:
            _f.write(_envdump)

        st, raw = http_call(port, 'GET', '/api/tags')
        receipt['captures']['tags-empty'] = capture('tags-empty', st, raw)
        try:
            tags0 = json.loads(raw)
        except ValueError:
            tags0 = None
        check('tags-empty-before-create', st == 200 and isinstance(tags0, dict) and tags0.get('models') == [],
              '/api/tags on a fresh model store holds an empty models array')
        st, raw = http_call(port, 'GET', '/v1/models')
        receipt['captures']['v1-models-empty'] = capture('v1-models-empty', st, raw)
        try:
            v10 = json.loads(raw)
        except ValueError:
            v10 = None
        receipt['observations']['v1_models_empty_data_form'] = (
            'null' if isinstance(v10, dict) and 'data' in v10 and v10['data'] is None
            else 'list' if isinstance(v10, dict) and v10.get('data') == [] else 'other')

        name = f'kama-{nonce}'
        modelfile = os.path.join(work, 'Modelfile')
        with open(modelfile, 'w') as f:
            f.write(f'FROM {gguf}\n')
        p = subprocess.run([binary, 'create', name, '-f', modelfile], env=env, capture_output=True,
                           text=True, timeout=CREATE_TIMEOUT, cwd=work)
        check('create', p.returncode == 0, f'ollama create {name} exited {p.returncode}')
        qualified = f'{name}:latest'

        st, tags_raw = http_call(port, 'GET', '/api/tags')
        receipt['captures']['tags'] = capture('tags', st, tags_raw)
        try:
            tags = json.loads(tags_raw)
            entries = [m for m in tags.get('models', []) if m.get('name') == qualified]
        except (ValueError, AttributeError):
            entries = []
        tag_digest = entries[0].get('digest') if len(entries) == 1 else None
        check('tags-lists-model', st == 200 and len(entries) == 1 and entries[0].get('model') == qualified
              and isinstance(tag_digest, str) and re.fullmatch(r'[0-9a-f]{64}', tag_digest) is not None,
              f'/api/tags holds exactly one entry named {qualified} with equal name/model and a 64-hex digest')

        st, raw = http_call(port, 'GET', '/v1/models')
        receipt['captures']['v1-models'] = capture('v1-models', st, raw)
        try:
            ids = [m.get('id') for m in json.loads(raw).get('data') or []]
        except (ValueError, AttributeError):
            ids = []
        check('v1-models-lists-model', st == 200 and qualified in ids, f'/v1/models lists id {qualified}')
        st, raw = http_call(port, 'GET', f'/v1/models/{name}')
        receipt['captures']['v1-model-single'] = capture('v1-model-single', st, raw)
        try:
            single_id = json.loads(raw).get('id')
        except (ValueError, AttributeError):
            single_id = None
        receipt['observations']['v1_single_id'] = single_id
        receipt['observations']['v1_single_id_equals_list_id'] = single_id == qualified
        st, raw = http_call(port, 'POST', '/api/show', {'model': qualified})
        receipt['captures']['show'] = capture('show', st, raw)

        st, ps_raw = http_call(port, 'GET', '/api/ps')
        receipt['captures']['ps-before'] = capture('ps-before', st, ps_raw)
        finding, ec = run_evidence(work, tags_raw, ps_raw, qualified, 'before')
        check('evidence-before-load', finding == 'available_not_loaded' and ec == 1,
              f'kama-ollama-evidence over tags+ps before any generation: {finding} exit {ec}')

        if not args.no_generate:
            st, raw = http_call(port, 'POST', '/api/generate',
                                {'model': qualified, 'prompt': 'Once', 'stream': False,
                                 'options': {'num_predict': 4}}, timeout=GENERATE_TIMEOUT)
            receipt['captures']['generate'] = capture('generate', st, raw)
            try:
                gen = json.loads(raw)
            except ValueError:
                gen = {}
            check('generate', st == 200 and gen.get('done') is True and isinstance(gen.get('response'), str),
                  'POST /api/generate returned done=true with a response string (not a quality claim)')
            st, ps_raw = http_call(port, 'GET', '/api/ps')
            receipt['captures']['ps-after'] = capture('ps-after', st, ps_raw)
            try:
                ps_entries = [m for m in json.loads(ps_raw).get('models', []) if m.get('name') == qualified]
            except (ValueError, AttributeError):
                ps_entries = []
            check('ps-lists-loaded', len(ps_entries) == 1 and ps_entries[0].get('digest') == tag_digest,
                  '/api/ps lists the model with the digest /api/tags reported')
            finding, ec = run_evidence(work, tags_raw, ps_raw, qualified, 'after')
            check('evidence-after-load', finding == 'loaded_same_digest' and ec == 0,
                  f'kama-ollama-evidence over tags+ps after generation: {finding} exit {ec}')
    except Exception as exc:  # noqa: BLE001 - a lifecycle fault becomes a graded receipt
        receipt['fault'] = f'{type(exc).__name__}: {exc}'[:300]
        rc_fail = True
    finally:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except OSError:
            pass
        try:
            returncode = proc.wait(timeout=TEARDOWN_TIMEOUT)
            killed = False
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except OSError:
                pass
            returncode = proc.wait()
            killed = True
        log.close()
        time.sleep(0.5)
        receipt['teardown'] = {'returncode': returncode, 'sigkill_needed': killed,
                               'port_closed': port_closed(port), 'log_path': log_path}
        check('teardown', receipt['teardown']['port_closed'] and not killed,
              'SIGTERM ended the child without SIGKILL and the port refuses connections')

    evaluated_failed = [c for c in checks if c['evaluated'] and not c['passed']]
    if rc_fail and not evaluated_failed:
        return finish('NOT_EVALUATED', 2)
    if evaluated_failed:
        return finish('FAIL', 1)
    return finish('MODEL_OK', 0)


if __name__ == '__main__':
    sys.exit(main())
