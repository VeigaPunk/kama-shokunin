#!/usr/bin/env python3
"""kama-context-capacity.py — live context-capacity cells K1-K8 (kama round-25, C2).

Declared versus served context capacity on the lane-owned llama-server
fixture. The eight cells are the preregistered ones (preregistration.json
claims[1].cells); their `args` strings are used verbatim and their
`prediction` strings are copied into the receipt verbatim. Each cell runs
one llama-server child at a time on 127.0.0.1, inside the assigned port
range, and is torn down (process group signalled, port proven closed)
before the next cell starts.

What a cell records:
  - the exact argv handed to the server
  - /props default_generation_settings.n_ctx and /props total_slots
  - every /slots entry's n_ctx
  - /v1/models data[0].meta.n_ctx_train
  - the server log lines matching n_ctx, n_ctx_seq, n_ctx_slot, kv_unified,
    n_seq_max, plus any warning line about n_ctx versus n_ctx_train
  - the server binary sha256 and the model sha256
  - start and stop UTC stamps
  - the teardown result: child exit status and port-closed proof
  - `observed`: true only when /props AND /slots were both read
  - `prediction`: the preregistered string, verbatim
  - `prediction_match`: true / false / unknown, graded from the observed
    per-slot n_ctx only where the prediction states a number

Port safety: the refused-port set and the port picker are reused from
tools/kama-llamacpp-live.py by import (module located at runtime); the
registered consumer ports and the hard pins are therefore never served.

Receipt schema: `kama-context-capacity/v1` with a top-level `cells` list.

Exit codes:
    0  every cell ran and produced an observed record
    1  at least one cell was not observed (server/setup failure)
    2  setup error (bad arguments, missing fixture, prereg disagreement)
    1  selftest failure (with --selftest)
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shlex
import signal
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = 'kama-context-capacity/v1'
SCRIPT = Path(__file__).resolve()
HOST = '127.0.0.1'
DEFAULT_SERVER = Path.home() / '.local/bin/llama-server'
DEFAULT_MODEL = Path.home() / '.cache/kama-shokunin/models/stories260K.gguf'
DEFAULT_PORT_RANGE = (47400, 47419)
DEFAULT_SCRATCH = Path('/fast/scratch/hyaku/kama-r25/ExecCapacityTool')
PREREG_REL = '.ufo/waves/round-25/preregistration.json'
CHILD_ENV_KEYS = ('PATH', 'HOME', 'LANG', 'LC_ALL', 'TMPDIR')
TERM_GRACE = 10.0
READY_POLL = 0.5
HOST_IDLE_TIMEOUT = 900.0

# The eight preregistered cells (preregistration.json, claims[1].cells).
# `args` and `prediction` are byte-for-byte the preregistered strings.
CELLS = (
    {'id': 'K1', 'args': '-c 0',
     'prediction': 'total_slots 4 (auto), kv_unified true, per-slot n_ctx 2048 (training context)'},
    {'id': 'K2', 'args': '-c 2048 -np 2 --no-kv-unified',
     'prediction': 'per-slot n_ctx 1024'},
    {'id': 'K3', 'args': '-c 2048 -np 2 --kv-unified',
     'prediction': 'per-slot n_ctx 2048'},
    {'id': 'K4', 'args': '-c 1024 -np 1',
     'prediction': 'kv_unified false (slots set explicitly), per-slot n_ctx 1024'},
    {'id': 'K5', 'args': '-c 4096 -np 1',
     'prediction': 'per-slot n_ctx capped at training context 2048'},
    {'id': 'K6', 'args': '-c 1000 -np 3 --no-kv-unified',
     'prediction': 'unknown: padding of n_ctx and per-sequence division; recorded as observed'},
    {'id': 'K7', 'args': '-np 2 --kv-unified-per-slot 512',
     'prediction': 'pool 1024, per-slot n_ctx 512'},
    {'id': 'K8', 'args': '-c 4096 -np 4 --kv-unified --kv-unified-per-slot 512',
     'prediction': 'per-slot n_ctx 512'},
)

# Log-line selection. The first five patterns are the ones the claim names
# literally; the sixth keeps any warning line about n_ctx versus
# n_ctx_train.
LOG_PATTERNS = (
    ('n_ctx_seq', re.compile(r'n_ctx_seq')),
    ('n_ctx_slot', re.compile(r'n_ctx_slot')),
    ('n_ctx', re.compile(r'n_ctx')),
    ('kv_unified', re.compile(r'kv_unified')),
    ('n_seq_max', re.compile(r'n_seq_max')),
)
WARN_RE = re.compile(r'warn', re.IGNORECASE)
CTX_RE = re.compile(r'n_ctx|context|train', re.IGNORECASE)

# The number a prediction states for the per-slot n_ctx, if any. Only this
# number is graded, and only against the observed /slots n_ctx values.
PER_SLOT_NUM_RE = re.compile(
    r'per-slot n_ctx\s+(?:capped at training context\s+)?(\d+)')


def _utc_now():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace(
        '+00:00', 'Z')


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def extract_log_lines(text):
    """Select the claim-named server log lines from a server log body.

    Returns a list of {'line': str, 'matched': [tag, ...]} in file order.
    A line matching no pattern is dropped. A warning line about n_ctx
    versus n_ctx_train is kept even when it names no pattern."""
    out = []
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        matched = [tag for tag, pat in LOG_PATTERNS if pat.search(line)]
        is_ctx_warning = bool(WARN_RE.search(line) and CTX_RE.search(line))
        if matched or is_ctx_warning:
            tags = list(matched)
            if is_ctx_warning and 'warn_ctx' not in tags:
                tags.append('warn_ctx')
            out.append({'line': line, 'matched': tags})
    return out


def grade_prediction(prediction, slot_ctx_values):
    """Grade a preregistered prediction against the observed per-slot n_ctx.

    Returns (match, expected, basis). `match` is True, False or None
    (unknown). A prediction that states no per-slot n_ctx number is
    unknown, never a pass and never a fail. No observation is unknown too.
    """
    m = PER_SLOT_NUM_RE.search(prediction or '')
    if not m:
        return None, None, 'prediction states no per-slot n_ctx number'
    expected = int(m.group(1))
    if not slot_ctx_values:
        return None, expected, 'no observed per-slot n_ctx values'
    ok = all(value == expected for value in slot_ctx_values)
    return ok, expected, 'all observed per-slot n_ctx values equal the ' \
        'predicted number' if ok else 'at least one observed per-slot ' \
        'n_ctx value differs from the predicted number'


# ---------------------------------------------------------------------------
# Port safety, reused from tools/kama-llamacpp-live.py by import.
# ---------------------------------------------------------------------------

def find_repo_root():
    """Nearest ancestor holding registry/endpoint-consumers.tsv."""
    for parent in [SCRIPT.parent] + list(SCRIPT.parent.parents):
        if (parent / 'registry' / 'endpoint-consumers.tsv').is_file():
            return parent
    return SCRIPT.parent


def locate_live_module():
    """Path of tools/kama-llamacpp-live.py, from this script's location.

    Works both when this tool sits next to it in tools/ and when it sits
    in the round-25 build output tree."""
    candidates = [SCRIPT.parent / 'kama-llamacpp-live.py']
    for parent in [SCRIPT.parent] + list(SCRIPT.parent.parents):
        candidates.append(parent / 'tools' / 'kama-llamacpp-live.py')
    for cand in candidates:
        if cand.is_file():
            return cand
    return None


def load_live_module(path):
    spec = importlib.util.spec_from_file_location('kama_llamacpp_live', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pick_free_port(live, refused, low, high, used):
    """First port in [low, high] that the lane picker accepts and we have
    not used yet. The picker raises when the port is registered or busy."""
    for port in range(low, high + 1):
        if port in used:
            continue
        try:
            chosen = live.pick_port(refused, port)
        except Exception:
            continue
        if chosen == port:
            return port
    return None


def ss_listen_lines(port):
    """Lines of `ss -ltn` that name the port (empty when the port is free)."""
    try:
        proc = subprocess.run(['ss', '-ltn'], capture_output=True, text=True,
                              timeout=20)
    except (OSError, subprocess.SubprocessError) as exc:
        return None, f'ss-failed:{type(exc).__name__}'
    needle = f':{port} '
    hits = [ln for ln in proc.stdout.splitlines() if needle in ln]
    return hits, None


def _is_zombie(pid):
    try:
        stat = Path(f'/proc/{pid}/stat').read_text()
    except OSError:
        return False
    try:
        fields = stat.rsplit(')', 1)[1].split()
        return fields[0] == 'Z'
    except IndexError:
        return False


def live_llama_server_pids():
    """Live (non-zombie) llama-server pids on the host, or None if unknown."""
    try:
        proc = subprocess.run(['pgrep', '-x', 'llama-server'],
                              capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    pids = []
    for token in proc.stdout.split():
        try:
            pid = int(token)
        except ValueError:
            continue
        if _is_zombie(pid):
            continue
        pids.append(pid)
    return pids


def wait_for_host_idle(timeout):
    """Wait until no other llama-server child is alive on the host.

    The lane contract allows one llama-server child at a time. Returns
    (ok, waited_seconds, observed_pids)."""
    t0 = time.monotonic()
    seen = []
    while True:
        pids = live_llama_server_pids()
        if pids is None:
            return True, round(time.monotonic() - t0, 3), seen
        if not pids:
            return True, round(time.monotonic() - t0, 3), seen
        for pid in pids:
            if pid not in seen:
                seen.append(pid)
        if time.monotonic() - t0 >= timeout:
            return False, round(time.monotonic() - t0, 3), seen
        time.sleep(2.0)


# ---------------------------------------------------------------------------
# One cell.
# ---------------------------------------------------------------------------

def run_cell(cell, cfg, live, refused, port):
    """Run one cell: launch, read, tear down, prove the port closed."""
    record = {
        'id': cell['id'],
        'args': cell['args'],
        'prediction': cell['prediction'],
        'prediction_match': None,
        'prediction_expected_per_slot_n_ctx': None,
        'prediction_observed_per_slot_n_ctx': None,
        'prediction_basis': None,
        'port': port,
        'argv': None,
        'props_default_generation_settings_n_ctx': None,
        'props_total_slots': None,
        'slots_n_ctx': [],
        'slots': [],
        'models_n_ctx_train': None,
        'models_n_ctx': None,
        'log_lines': [],
        'server_sha256': cfg['server_sha256'],
        'model_sha256': cfg['model_sha256'],
        'started_utc': None,
        'stopped_utc': None,
        'props_read': False,
        'slots_read': False,
        'observed': False,
        'teardown': {
            'sigterm_sent': False,
            'sigkill_sent': False,
            'child_returncode': None,
            'port_closed': False,
            'ss_listen_lines_after': None,
            'error': None,
        },
        'error': None,
    }

    argv = [
        cfg['server_real'], '-m', cfg['model_real'],
        '--host', HOST, '--port', str(port),
        '--no-webui', '--offline',
    ] + shlex.split(cell['args'])
    record['argv'] = argv

    log_path = Path(cfg['scratch']) / f"server-{cell['id']}-port{port}.log"
    child_env = {key: os.environ[key] for key in CHILD_ENV_KEYS
                 if key in os.environ}

    proc = None
    log_file = None
    try:
        log_file = open(log_path, 'wb')
        proc = subprocess.Popen(argv, stdin=subprocess.DEVNULL,
                                stdout=log_file,
                                stderr=subprocess.STDOUT,
                                start_new_session=True,
                                env=child_env)
    except OSError as exc:
        record['error'] = f'launch-failed:{type(exc).__name__}'
        if log_file is not None:
            log_file.close()
        return record
    finally:
        if log_file is not None:
            try:
                log_file.close()
            except OSError:
                pass

    record['started_utc'] = _utc_now()
    try:
        ready = False
        deadline = time.monotonic() + cfg['ready_timeout']
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                record['error'] = f'server-exited-early-rc{proc.returncode}'
                break
            result = live.http_get(port, '/props', timeout=5.0)
            if result.get('status') == 200:
                ready = True
                break
            time.sleep(READY_POLL)
        if not ready and record['error'] is None:
            record['error'] = 'ready-timeout'

        if record['error'] is None:
            props = _get_json(live, port, '/props')
            slots = _get_json(live, port, '/slots')
            models = _get_json(live, port, '/v1/models')
            health = live.http_get(port, '/health', timeout=5.0)
            record['health_status'] = health.get('status')

            if isinstance(props, dict):
                record['props_read'] = True
                dgs = props.get('default_generation_settings')
                if isinstance(dgs, dict):
                    record['props_default_generation_settings_n_ctx'] = \
                        dgs.get('n_ctx')
                record['props_total_slots'] = props.get('total_slots')
            if isinstance(slots, list):
                record['slots_read'] = True
                entries = []
                for entry in slots:
                    if not isinstance(entry, dict):
                        continue
                    entries.append({'id': entry.get('id'),
                                    'n_ctx': entry.get('n_ctx')})
                record['slots'] = entries
                record['slots_n_ctx'] = [e['n_ctx'] for e in entries
                                         if isinstance(e.get('n_ctx'), int)]
            if isinstance(models, dict):
                data = models.get('data')
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    meta = data[0].get('meta')
                    if isinstance(meta, dict):
                        record['models_n_ctx_train'] = meta.get('n_ctx_train')
                        record['models_n_ctx'] = meta.get('n_ctx')
                    record['models_id'] = data[0].get('id')
    finally:
        record['stopped_utc'] = _utc_now()
        record['teardown'] = _teardown(proc, port, log_path)

    try:
        text = log_path.read_text(encoding='utf-8', errors='replace')
    except OSError:
        text = ''
    record['log_lines'] = extract_log_lines(text)

    record['observed'] = bool(record['props_read'] and record['slots_read'])
    match, expected, basis = grade_prediction(cell['prediction'],
                                               record['slots_n_ctx'])
    record['prediction_match'] = match
    record['prediction_expected_per_slot_n_ctx'] = expected
    record['prediction_observed_per_slot_n_ctx'] = record['slots_n_ctx']
    record['prediction_basis'] = basis
    return record


def _get_json(live, port, path):
    result = live.http_get(port, path, timeout=10.0)
    if result.get('status') != 200:
        return None
    try:
        return json.loads(result.get('body') or '')
    except (ValueError, TypeError):
        return None


def _teardown(proc, port, log_path):
    """Kill the child process group and prove the port is closed."""
    out = {'sigterm_sent': False, 'sigkill_sent': False,
           'child_returncode': None, 'port_closed': False,
           'ss_listen_lines_after': None, 'error': None}
    if proc is None:
        out['error'] = 'no-child'
        return out
    try:
        os.killpg(proc.pid, signal.SIGTERM)
        out['sigterm_sent'] = True
    except (ProcessLookupError, PermissionError, OSError) as exc:
        out['error'] = f'sigterm:{type(exc).__name__}'
    try:
        out['child_returncode'] = proc.wait(timeout=TERM_GRACE)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
            out['sigkill_sent'] = True
        except (ProcessLookupError, PermissionError, OSError) as exc:
            out['error'] = (out['error'] or '') + f'sigkill:{type(exc).__name__}'
        try:
            out['child_returncode'] = proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            out['error'] = (out['error'] or '') + 'wait-timeout'
    # The port must refuse connections after teardown.
    deadline = time.monotonic() + 10.0
    closed = False
    while time.monotonic() < deadline:
        try:
            socket.create_connection((HOST, port), timeout=1.0).close()
        except ConnectionRefusedError:
            closed = True
            break
        except OSError:
            pass
        time.sleep(0.5)
    out['port_closed'] = closed
    hits, err = ss_listen_lines(port)
    out['ss_listen_lines_after'] = hits if hits is not None else err
    return out


# ---------------------------------------------------------------------------
# Preregistration cross-check.
# ---------------------------------------------------------------------------

def load_prereg_cells(repo_root):
    """The preregistered cells as written in preregistration.json, or None."""
    path = repo_root / PREREG_REL
    if not path.is_file():
        return None, path
    try:
        doc = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None, path
    for claim in doc.get('claims', []):
        if claim.get('id') == 'C2':
            cells = claim.get('cells')
            if isinstance(cells, list):
                return cells, path
    return None, path


def compare_cells(embedded, prereg):
    """List of disagreements between the embedded cells and the prereg."""
    problems = []
    if prereg is None:
        return ['preregistration C2 cells not found']
    prereg_map = {}
    for cell in prereg:
        if isinstance(cell, dict) and 'id' in cell:
            prereg_map[cell['id']] = cell
    for cell in embedded:
        other = prereg_map.get(cell['id'])
        if other is None:
            problems.append(f"{cell['id']}: absent from the preregistration")
            continue
        if other.get('args') != cell['args']:
            problems.append(f"{cell['id']}: args differ from the preregistration")
        if other.get('prediction') != cell['prediction']:
            problems.append(f"{cell['id']}: prediction differs from the "
                            'preregistration')
    for pid in prereg_map:
        if pid not in {c['id'] for c in embedded}:
            problems.append(f'{pid}: preregistered cell not implemented')
    return problems


# ---------------------------------------------------------------------------
# Selftest: no server, no network.
# ---------------------------------------------------------------------------

SELFTEST_LOG = """\
load_model: initializing, n_slots = 2, n_ctx_slot = 1024, kv_unified = 'false'
llama_context: n_ctx = 1024 (n_ctx_train = 2048), n_seq_max = 1024
print_info: n_ctx = 1024
warning: the requested context size exceeds the model training context
main: server is listening on http://127.0.0.1:47400
"""


def _selftest():
    """Argument parsing, log-line extraction, prediction grading.

    The KAMA_SELFTEST_BREAK environment variable injects one deliberately
    wrong expectation so the selftest can be shown to fail."""
    break_id = os.environ.get('KAMA_SELFTEST_BREAK', '').strip()
    results = []

    def check(name, condition, detail=''):
        results.append({'check': name, 'passed': bool(condition),
                        'detail': detail})
        return bool(condition)

    # 1. argument parsing
    parser = build_parser()
    args = parser.parse_args([
        '--server', '/opt/llama-server', '--model', '/tmp/m.gguf',
        '--out', '/tmp/receipt.json', '--port-range', '47500-47510',
        '--scratch', '/tmp/scratch'])
    check('arg_parse_fields',
          args.server == '/opt/llama-server' and args.model == '/tmp/m.gguf'
          and args.out == '/tmp/receipt.json'
          and args.port_range == '47500-47510'
          and args.scratch == '/tmp/scratch',
          f'parsed={args.server},{args.model},{args.out},'
          f'{args.port_range},{args.scratch}')
    default_args = parser.parse_args([])
    check('arg_parse_defaults',
          default_args.port_range == '47400-47419'
          and default_args.selftest is False,
          f'port_range={default_args.port_range}')
    bad_range = False
    try:
        parser.parse_args(['--port-range', 'not-a-range'])
    except SystemExit:
        bad_range = True
    check('arg_parse_rejects_bad_range', bad_range,
          'a malformed --port-range must exit non-zero')
    parsed_range = parse_port_range('47400-47419')
    check('arg_parse_range_tuple', parsed_range == (47400, 47419),
          f'parsed_range={parsed_range}')

    # 2. log-line extraction on fixed strings
    lines = extract_log_lines(SELFTEST_LOG)
    texts = [row['line'] for row in lines]
    want_kept = [
        "load_model: initializing, n_slots = 2, n_ctx_slot = 1024, kv_unified = 'false'",
        "llama_context: n_ctx = 1024 (n_ctx_train = 2048), n_seq_max = 1024",
        'print_info: n_ctx = 1024',
        'warning: the requested context size exceeds the model training context',
    ]
    if break_id == 'log_extract':
        want_kept = want_kept[:-1]
    check('log_extract_kept_lines', texts == want_kept,
          f'kept={texts!r}')
    check('log_extract_drops_unrelated',
          not any('server is listening' in t for t in texts),
          'an unrelated line must be dropped')
    tagged = [tag for row in lines for tag in row['matched']]
    if break_id == 'log_tags':
        tagged = [t for t in tagged if t != 'warn_ctx']
    check('log_extract_tags',
          'n_ctx_slot' in tagged and 'kv_unified' in tagged
          and 'n_seq_max' in tagged and 'warn_ctx' in tagged,
          f'tags={sorted(set(tagged))}')

    # 3. prediction grading
    k1 = next(c for c in CELLS if c['id'] == 'K1')
    k6 = next(c for c in CELLS if c['id'] == 'K6')
    ok, expected, basis = grade_prediction(k1['prediction'],
                                            [2048, 2048, 2048, 2048])
    if break_id == 'prediction_true':
        ok = not ok
    check('prediction_true', ok is True and expected == 2048,
          f'ok={ok} expected={expected} basis={basis}')
    bad, expected2, _ = grade_prediction(k1['prediction'], [1024, 1024])
    if break_id == 'prediction_false':
        bad = not bad
    check('prediction_false', bad is False and expected2 == 2048,
          f'ok={bad} expected={expected2}')
    unknown, expected3, _ = grade_prediction(k6['prediction'], [1000, 1000, 1000])
    check('prediction_unknown', unknown is None and expected3 is None,
          f'ok={unknown} expected={expected3}')
    no_obs, expected4, _ = grade_prediction(k1['prediction'], [])
    check('prediction_unknown_without_observation',
          no_obs is None and expected4 == 2048,
          f'ok={no_obs} expected={expected4}')
    k7 = next(c for c in CELLS if c['id'] == 'K7')
    k7ok, k7expected, _ = grade_prediction(k7['prediction'], [512, 512])
    check('prediction_reads_pool_number_correctly',
          k7ok is True and k7expected == 512,
          f'ok={k7ok} expected={k7expected}')

    # 4. the embedded cells still match the preregistration
    repo_root = find_repo_root()
    prereg, prereg_path = load_prereg_cells(repo_root)
    problems = compare_cells(list(CELLS), prereg)
    if break_id == 'prereg':
        problems = list(problems) + ['injected preregistration disagreement']
    check('prereg_cells_agree', not problems,
          f'path={prereg_path} problems={problems}')

    failed = [r for r in results if not r['passed']]
    for row in results:
        status = 'PASS' if row['passed'] else 'FAIL'
        print(f'{status} {row["check"]}: {row["detail"]}')
    print(f'selftest: {len(results) - len(failed)}/{len(results)} checks '
          f'passed; break={break_id or "none"}')
    return 0 if not failed else 1


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------

def _port_range_arg(text):
    """argparse type for --port-range: validate now, keep the raw string."""
    try:
        parse_port_range(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc))
    return text


def build_parser():
    parser = argparse.ArgumentParser(
        prog='kama-context-capacity.py',
        description='Run the preregistered context-capacity cells K1-K8 '
                    'against the lane-owned llama-server fixture.')
    parser.add_argument('--server', default=str(DEFAULT_SERVER),
                        help='llama-server binary (default: %(default)s)')
    parser.add_argument('--model', default=str(DEFAULT_MODEL),
                        help='GGUF model (default: %(default)s)')
    parser.add_argument('--out', default=None,
                        help='receipt JSON path (default: stdout only)')
    parser.add_argument('--port-range', default='47400-47419',
                        type=_port_range_arg,
                        help='inclusive loopback port range to serve on '
                             '(default: %(default)s)')
    parser.add_argument('--scratch', default=str(DEFAULT_SCRATCH),
                        help='directory for the per-cell server logs '
                             '(default: %(default)s)')
    parser.add_argument('--ready-timeout', type=float, default=180.0,
                        help='seconds to wait for the server to serve '
                             '/props (default: %(default)s)')
    parser.add_argument('--host-idle-timeout', type=float,
                        default=HOST_IDLE_TIMEOUT,
                        help='seconds to wait for the host to have no other '
                             'llama-server child (default: %(default)s)')
    parser.add_argument('--only', default=None,
                        help='comma-separated cell ids to run (default: all)')
    parser.add_argument('--selftest', action='store_true',
                        help='run the offline selftest and exit')
    return parser


def parse_port_range(text):
    m = re.fullmatch(r'\s*(\d{1,5})\s*-\s*(\d{1,5})\s*', text or '')
    if not m:
        raise ValueError(f'bad port range: {text!r}')
    low, high = int(m.group(1)), int(m.group(2))
    if not (1 <= low <= high <= 65535):
        raise ValueError(f'bad port range: {text!r}')
    return low, high


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        try:
            return _selftest()
        except BaseException as exc:
            print(f'kama-context-capacity selftest: {type(exc).__name__}: '
                  f'{exc}', file=sys.stderr)
            return 1
    try:
        port_range = parse_port_range(args.port_range)
    except ValueError as exc:
        parser.error(str(exc))
        return 2

    receipt = {
        'schema': SCHEMA,
        'started_utc': None,
        'ended_utc': None,
        'tool': {'path': str(SCRIPT), 'sha256': None},
        'host': HOST,
        'port_range': list(port_range),
        'server': {'arg': None, 'realpath': None, 'sha256': None,
                   'version': None},
        'model': {'arg': None, 'realpath': None, 'sha256': None,
                  'size_bytes': None},
        'preregistration': {'path': None, 'cells_agree': None,
                            'disagreements': None},
        'port_refusal_set': [],
        'host_idle': None,
        'cells': [],
        'summary': {},
        'exit_code': 2,
        'error': None,
    }

    try:
        receipt['started_utc'] = _utc_now()
        receipt['tool']['sha256'] = _sha256_file(SCRIPT)

        live_path = locate_live_module()
        if live_path is None:
            raise SetupError('kama-llamacpp-live.py-not-found')
        live = load_live_module(live_path)
        receipt['port_safety_module'] = str(live_path)

        repo_root = find_repo_root()
        prereg, prereg_path = load_prereg_cells(repo_root)
        receipt['preregistration']['path'] = str(prereg_path)
        problems = compare_cells(list(CELLS), prereg)
        receipt['preregistration']['cells_agree'] = not problems
        receipt['preregistration']['disagreements'] = problems
        if problems:
            raise SetupError('preregistration-disagreement')

        server_arg = Path(args.server)
        if not server_arg.is_file():
            raise SetupError(f'server-not-found:{args.server}')
        server_real = os.path.realpath(server_arg)
        model_arg = Path(args.model)
        if not model_arg.is_file():
            raise SetupError(f'model-not-found:{args.model}')
        model_real = os.path.realpath(model_arg)
        model_path = Path(model_real)
        receipt['server'].update({
            'arg': str(server_arg), 'realpath': server_real,
            'sha256': _sha256_file(server_real)})
        receipt['model'].update({
            'arg': str(model_arg), 'realpath': model_real,
            'sha256': _sha256_file(model_real),
            'size_bytes': model_path.stat().st_size})
        try:
            ver = subprocess.run([server_real, '--version'],
                                 capture_output=True, text=True, timeout=60)
            receipt['server']['version'] = ver.stdout.strip() or \
                ver.stderr.strip()
        except (OSError, subprocess.SubprocessError) as exc:
            receipt['server']['version'] = f'version-failed:{type(exc).__name__}'

        refused = live.refused_ports()
        receipt['port_refusal_set'] = sorted(refused)
        for hard in (8080, 34113):
            if hard not in refused:
                raise SetupError(f'hard-pin-missing:{hard}')

        scratch = Path(args.scratch)
        scratch.mkdir(parents=True, exist_ok=True)
        cfg = {'server_real': server_real, 'model_real': model_real,
               'server_sha256': receipt['server']['sha256'],
               'model_sha256': receipt['model']['sha256'],
               'scratch': str(scratch),
               'ready_timeout': args.ready_timeout}

        selected = list(CELLS)
        if args.only:
            wanted = {x.strip() for x in args.only.split(',') if x.strip()}
            selected = [c for c in CELLS if c['id'] in wanted]
            if not selected:
                raise SetupError('no-cells-selected')

        used_ports = []
        for cell in selected:
            idle_ok, waited, seen = wait_for_host_idle(args.host_idle_timeout)
            receipt['host_idle'] = {'ok': idle_ok, 'waited_s': waited,
                                    'other_pids_seen': seen,
                                    'cell': cell['id']}
            if not idle_ok:
                raise SetupError(f'host-not-idle-before-{cell["id"]}')
            port = pick_free_port(live, refused, port_range[0], port_range[1],
                                  used_ports)
            if port is None:
                raise SetupError(f'no-free-port-in-range-for-{cell["id"]}')
            used_ports.append(port)
            hits, err = ss_listen_lines(port)
            if hits is None:
                raise SetupError(f'ss-check-failed:{err}')
            if hits:
                raise SetupError(f'port-not-free:{port}')
            record = run_cell(cell, cfg, live, refused, port)
            receipt['cells'].append(record)

        observed = [c for c in receipt['cells'] if c.get('observed')]
        receipt['summary'] = {
            'cells': len(receipt['cells']),
            'observed': len(observed),
            'prediction_true': sum(1 for c in receipt['cells']
                                   if c.get('prediction_match') is True),
            'prediction_false': sum(1 for c in receipt['cells']
                                    if c.get('prediction_match') is False),
            'prediction_unknown': sum(1 for c in receipt['cells']
                                      if c.get('prediction_match') is None),
            'ports_used': used_ports,
            'all_ports_closed': all(c['teardown']['port_closed']
                                    for c in receipt['cells']),
        }
        receipt['exit_code'] = 0 if len(observed) == len(receipt['cells']) else 1
    except SetupError as exc:
        receipt['error'] = str(exc)
        receipt['exit_code'] = 2
    except BaseException as exc:
        receipt['error'] = f'internal:{type(exc).__name__}:{exc}'
        receipt['exit_code'] = 2
    finally:
        observed_cells = [c for c in receipt['cells'] if c.get('observed')]
        receipt['summary'] = {
            'cells': len(receipt['cells']),
            'observed': len(observed_cells),
            'prediction_true': sum(1 for c in receipt['cells']
                                   if c.get('prediction_match') is True),
            'prediction_false': sum(1 for c in receipt['cells']
                                    if c.get('prediction_match') is False),
            'prediction_unknown': sum(1 for c in receipt['cells']
                                      if c.get('prediction_match') is None),
            'ports_used': [c.get('port') for c in receipt['cells']],
            'all_ports_closed': all(c['teardown']['port_closed']
                                    for c in receipt['cells']),
        }
        receipt['ended_utc'] = _utc_now()

    text = json.dumps(receipt, ensure_ascii=True, indent=2, sort_keys=True)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text + '\n', encoding='utf-8')
    sys.stdout.write(json.dumps(receipt['summary'], sort_keys=True) + '\n')
    if receipt.get('error'):
        sys.stderr.write(f'kama-context-capacity: {receipt["error"]}\n')
    return receipt['exit_code']


class SetupError(Exception):
    """Fatal pre-check failure; mapped to exit 2 with a stable reason token."""


if __name__ == '__main__':
    sys.exit(main())
