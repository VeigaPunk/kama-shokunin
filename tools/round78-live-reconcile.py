#!/usr/bin/env python3
"""Round-78 C3 trial; never a registered-consumer readiness gate.

Axis: operability. Run --self-test to exercise all four red controls. Scratch
and child lifecycle are confined to the calling seat's scratch root.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import http.server
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

PREDICATE = (
    '`python3 tools/round78-live-reconcile.py --repo <lane>` prints one `LIVE_RECONCILE rows=3 '
    'model_ok=1 mismatch=1 dead=1 probe_exit=2 runtime=llama.cpp served=stories260K` line and exits '
    '0 only when it starts the pinned `llama-server` (binary and model sha256 recorded) as a child '
    'on a loopback port that is neither a registered consumer port nor currently listening, writes '
    'a three-row scratch registry under its own scratch root — a row whose expected id normalises to '
    'the served id, a row whose expected id does not, and a row naming an unserved port — runs '
    '`bash tools/kama-probe.sh check --registry <scratch>` and observes `MODEL_OK` on the first, '
    '`MODEL_MISMATCH` on the second and `DEAD` on the third, requires the live row’s probe evidence '
    'to name `runtime=llama.cpp` and the served id to be the pinned fixture model, refuses any '
    'registered consumer port before probing, tears the child down and writes a receipt carrying the '
    'child’s exit status; it exits 1 naming `LIVE_RECONCILE_FINDING <class> <detail>` when a verdict '
    'differs, when a responder without llama.cpp runtime evidence reaches `MODEL_OK`, or when a '
    'registered port was probed, and 2 on could-not-evaluate (pinned binary, model or probe absent; '
    'CLI misuse).'
).replace('row’s', "row's").replace('child’s', "child's")
SERVER = Path.home() / '.local/opt/llama-b11755/llama-server'
MODEL = Path.home() / '.cache/kama-shokunin/models/stories260K.gguf'
SERVER_SHA = 'b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804'
MODEL_SHA = '270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d'
SUCCESS = 'LIVE_RECONCILE rows=3 model_ok=1 mismatch=1 dead=1 probe_exit=2 runtime=llama.cpp served=stories260K'
ARMS = ('fake-responder', 'registered-port', 'wrong-expect', 'no-teardown')
SCRATCH = Path('/fast/scratch/hyaku/kama-r78/EX03C3Live')


class Finding(Exception):
    pass


def digest(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def listening_ports() -> set[int]:
    # All interfaces, including IPv6 and wildcard listeners; no endpoint probe.
    ports = set()
    for name in ('tcp', 'tcp6'):
        for line in Path('/proc/net', name).read_text().splitlines()[1:]:
            fields = line.split()
            if fields[3] == '0A':
                ports.add(int(fields[1].split(':')[1], 16))
    return ports


def registered_ports(repo: Path) -> set[int]:
    ports = {8080, 34113}
    for line in (repo / 'registry/endpoint-consumers.tsv').read_text().splitlines():
        if not line.strip() or line.startswith('#') or line.startswith('id\t'):
            continue
        fields = line.split('\t')
        if len(fields) != 6:
            raise ValueError('malformed registered consumer row')
        url = urllib.parse.urlsplit(fields[3])
        ports.add(url.port or (443 if url.scheme == 'https' else 80))
    return ports


def refuse_ports(ports: list[int], registered: set[int]) -> None:
    if set(ports) & registered:
        raise Finding('registered-port registry names a registered consumer port')
    if listening_ports() & registered:
        raise Finding('registered-port registered consumer port is listening')


def free_port(excluded: set[int]) -> int:
    for _ in range(100):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        if port not in excluded and port not in listening_ports():
            return port
    raise OSError('no free unregistered loopback port')


def normalize(value: str) -> str:
    return value.rsplit('/', 1)[-1].removesuffix('.gguf')


def grade(receipt: dict) -> None:
    rows = receipt.get('rows', [])
    expected = [('live-match', 'MODEL_OK'), ('live-mismatch', 'MODEL_MISMATCH'), ('dead-row', 'DEAD')]
    if [(row.get('id'), row.get('verdict')) for row in rows] != expected:
        raise Finding('verdict three-row reconciliation differs')
    if receipt.get('probe_exit') != 2 or receipt.get('summary') != {
        'registry_rows_evaluated': 3, 'model_ok': 1, 'drift': 2, 'exit': 2
    }:
        raise Finding('verdict probe summary or exit differs')
    for row in rows[:2]:
        if 'runtime=llama.cpp;' not in row.get('evidence', ''):
            raise Finding('fake-responder live evidence lacks runtime=llama.cpp')
        if normalize(row.get('served_model', '')) != 'stories260K':
            raise Finding('served-id live served id is not stories260K')
        if row.get('file_match') != 'yes':
            raise Finding('pin scratch consumer pin did not resolve')
    if not isinstance(receipt.get('child_exit'), int):
        raise Finding('no-teardown child exit status absent')
    if not receipt.get('port_closed'):
        raise Finding('no-teardown child port remains listening')


def run_probe(repo: Path, work: Path, ports: list[int], registered: set[int], receipt: dict) -> None:
    refuse_ports(ports, registered)
    rows = []
    for name, port, expect in (
        ('live-match', ports[0], 'stories260K'),
        ('live-mismatch', ports[0], 'definitely-not-the-model'),
        ('dead-row', ports[1], 'stories260K'),
    ):
        url = f'http://127.0.0.1:{port}/v1'
        pin = work / f'{name}.json'
        pin.write_text(json.dumps({'baseURL': url}))
        rows.append('\t'.join((name, str(pin), 'json:/baseURL', url, expect, 'lane-owned fixture')))
    registry = work / 'consumers.tsv'
    registry.write_text('\n'.join(rows) + '\n')
    receipt['registry'] = registry.read_text()
    # Recheck the actual registry immediately before invoking the probe.
    refuse_ports([urllib.parse.urlsplit(row.split('\t')[3]).port for row in rows], registered)
    argv = ['bash', str(repo / 'tools/kama-probe.sh'), 'check', '--registry', str(registry),
            '--timeout', '2', '--connect-timeout', '1', '--json']
    receipt['probe_argv'] = argv
    env = dict(os.environ, TMPDIR=str(work), NO_PROXY='*', no_proxy='*')
    proc = subprocess.run(argv, capture_output=True, text=True, timeout=45, cwd=work, env=env)
    receipt.update(probe_stdout=proc.stdout, probe_stderr=proc.stderr, probe_exit=proc.returncode)
    if proc.returncode not in (0, 2):
        raise Finding('probe ' + proc.stderr.strip())
    parsed = json.loads(proc.stdout)
    receipt.update(rows=parsed['rows'], summary=parsed['summary'])
    summary = parsed['summary']
    receipt['probe_summary_line'] = 'registry_rows_evaluated={registry_rows_evaluated} model_ok={model_ok} drift={drift} exit={exit}'.format(**summary)


def trial(repo: Path, scratch: Path, arm: str | None = None) -> tuple[dict, int]:
    receipt = {'schema': 'round78-live-reconcile/v1', 'predicate': PREDICATE,
               'arm': arm, 'argv': sys.argv, 'child_exit': None, 'rows': []}
    child = None
    fake = None
    thread = None
    work = None
    code = 2
    try:
        for path in (SERVER, MODEL, repo / 'tools/kama-probe.sh'):
            if not path.is_file():
                raise OSError(f'pinned prerequisite absent: {path}')
        receipt['sha256s'] = {'server': digest(SERVER), 'model': digest(MODEL)}
        if receipt['sha256s'] != {'server': SERVER_SHA, 'model': MODEL_SHA}:
            raise Finding('pin binary or model digest differs from fixture pin')
        registered = registered_ports(repo)
        refuse_ports([], registered)
        port = free_port(registered)
        dead = free_port(registered | {port})
        receipt['ports'] = {'live': port, 'dead': dead, 'registered': sorted(registered)}
        if arm == 'registered-port':
            refuse_ports([8080, dead], registered)
        scratch.mkdir(parents=True, exist_ok=True)
        work = Path(tempfile.mkdtemp(prefix='trial-', dir=scratch))
        receipt['scratch'] = str(work)
        refuse_ports([port, dead], registered)
        if port in listening_ports() or dead in listening_ports():
            raise Finding('port chosen port became occupied before launch')
        argv = [str(SERVER), '--model', str(MODEL), '--host', '127.0.0.1',
                '--port', str(port), '-c', '512', '-t', '1', '--no-webui']
        receipt['child_argv'] = argv
        with (work / 'server.log').open('w+') as log:
            try:
                child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=log,
                                         stderr=subprocess.STDOUT, cwd=work)
                receipt['child_pid'] = child.pid
                opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
                deadline = time.monotonic() + 60
                while True:
                    if child.poll() is not None:
                        raise Finding('child pinned server exited before readiness')
                    try:
                        with opener.open(f'http://127.0.0.1:{port}/v1/models', timeout=1) as response:
                            models_body = response.read()
                            if response.status == 200:
                                break
                    except (OSError, urllib.error.URLError):
                        if time.monotonic() >= deadline:
                            raise Finding('child pinned server readiness timed out')
                        time.sleep(0.1)
                receipt['models_body'] = models_body.decode()
                if arm == 'fake-responder':
                    child.terminate()
                    receipt['child_exit'] = child.wait(timeout=10)
                    class Handler(http.server.BaseHTTPRequestHandler):
                        def do_GET(self):
                            self.send_response(200)
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            self.wfile.write(models_body)
                        def log_message(self, *_args):
                            pass
                    fake = http.server.ThreadingHTTPServer(('127.0.0.1', port), Handler)
                    thread = threading.Thread(target=fake.serve_forever, daemon=True)
                    thread.start()
                run_probe(repo, work, [port, dead], registered, receipt)
                if arm == 'wrong-expect':
                    receipt['rows'][0]['verdict'] = 'MODEL_MISMATCH'
            finally:
                if fake is not None:
                    fake.shutdown()
                    fake.server_close()
                    thread.join(timeout=5)
                if child is not None:
                    if child.poll() is None:
                        child.terminate()
                        try:
                            child.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            child.kill()
                            child.wait(timeout=10)
                    receipt['child_exit'] = child.returncode
                log.flush()
                log.seek(0)
                receipt['child_log'] = log.read()
        receipt['port_closed'] = port not in listening_ports()
        if arm == 'no-teardown':
            receipt.pop('child_exit', None)
        grade(receipt)
        code = 0
    except Finding as exc:
        receipt['finding'] = str(exc)
        code = 1
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        receipt['error'] = str(exc)
        code = 2
    finally:
        if work is not None:
            shutil.rmtree(work)
        receipt['exit'] = code
    return receipt, code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--scratch-root', type=Path, default=SCRATCH)
    parser.add_argument('--receipt', type=Path)
    parser.add_argument('--arm', choices=ARMS)
    parser.add_argument('--self-test', '--selftest', action='store_true')
    args = parser.parse_args()
    repo = args.repo.resolve()
    scratch = args.scratch_root.resolve()
    allowed = Path('/fast/scratch/hyaku/kama-r78').resolve()
    if not scratch.is_relative_to(allowed) or scratch == allowed:
        parser.error('--scratch-root must name a seat root under /fast/scratch/hyaku/kama-r78')
    after = repo / '.ufo/waves/round-78/measured/after'
    output = args.receipt or after / 'c3-live.json'
    try:
        if args.self_test:
            receipts = []
            lines = []
            for arm in ARMS:
                receipt, code = trial(repo, scratch, arm)
                receipts.append(receipt)
                detail = receipt.get('finding', receipt.get('error', 'unexpected green'))
                lines.append(f'{arm} exit={code} LIVE_RECONCILE_FINDING {detail}')
            passed = sum(r['exit'] == 1 and r.get('finding', '').startswith(r['arm'] if r['arm'] != 'wrong-expect' else 'verdict') for r in receipts)
            lines.append(f'LIVE_RECONCILE_SELFTEST pass={passed} fail={len(ARMS) - passed}')
            after.mkdir(parents=True, exist_ok=True)
            (after / 'c3-selftest.out').write_text('\n'.join(lines) + '\n')
            (after / 'c3-selftest.json').write_text(json.dumps(receipts, indent=2) + '\n')
            print('\n'.join(lines))
            return 0 if passed == len(ARMS) else 1
        receipt, code = trial(repo, scratch, args.arm)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(receipt, indent=2) + '\n')
        if code == 0:
            print(SUCCESS)
        elif code == 1:
            print('LIVE_RECONCILE_FINDING ' + receipt['finding'])
        else:
            print('LIVE_RECONCILE_ERROR ' + receipt['error'])
        return code
    finally:
        # Only remove the root owned by this invocation when it is empty.
        if scratch.exists():
            try:
                scratch.rmdir()
            except OSError:
                pass


if __name__ == '__main__':
    raise SystemExit(main())
