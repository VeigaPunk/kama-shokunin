VERDICT: partial — H5–H7 survive fault-controls and the pair; H8's two-row acceptance already exists in pristine bytes and is not a new mutant.

# Scoped mutation advice: C1 preregistered H5–H8

Attacked revision: `54a29268e2083caa2b1e0d54ee1e7d90961302f3`. This is mutation evidence for L1, not round admission or a runtime judgment. Axes named: **calibration** (C1's claims about its instrument) and **detector coverage**, with **isolation/exact restoration** as safety constraints. C2 and live llama.cpp behavior were not attacked.

Claim under attack: `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17.md:156-165` reports the fixed detector's accepted-fault decrease and current/full 10/10 kills; `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md:680` says "current 10 of 10" for the registered mutant set. These runs do not contradict that finite ten-mutant count; they test three additional behavior-bearing changes and identify an inapplicable fourth registration.

## Results and deciding detector

Each independent copy ran the same complete F0 + F1–F8 suite (including slow F7 and every F8 malformed/non-UTF-8 variant), and both 72-row probe arms, in pristine, mutation, and restored phases. No baseline was inconclusive. The historical arm's exit 1 / 55 passes / 17 failures is the expected negative reference, not an unexpected baseline failure.

| Registration | Actual single-site change | Pair | Fault-controls | Deciding evidence / status |
|---|---|---|---|---|
| H5 | Normalize each observed and expected served ID with `lower().removesuffix(".gguf")` before equality | survived; zero normalized row/total/exit differences | survived; exit 0, detected 8, accepted 0 | **SURVIVED**; neither detector distinguishes the mutation |
| H6 | Set `record["passed"] = True` immediately before the no-stub-requests return | survived; zero differences | survived; exit 0, detected 8, accepted 0 | **SURVIVED**; neither detector distinguishes the mutation |
| H7 | Select `rows[-1]` instead of `rows[0]` | survived; zero differences | survived; exit 0, detected 8, accepted 0 | **SURVIVED**; neither detector distinguishes the mutation |
| H8 | Accept two probe rows | unchanged control, not a mutant | unchanged control, not a mutant | **N/A: behavior already present**; a real-probe two-row witness passes pristine bytes, exit 0, 1/1 |

Applied-mutant count: **0 killed / 3 survived / 0 inconclusive**, plus **1 n/a**. H8 is not falsely counted as either a kill or a fourth genuine survivor. The H8 copy stayed byte-identical in all three phases.

### F1 — H5 escapes the existing served-ID fault

Source site: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:470-471`, quote: `record["served_model"] == record["served_model_expected"]`.

The exact original two-line assignment was replaced only in H5 by:

```python
        record["served_model_ok"] = (
            [sid.lower().removesuffix(".gguf")
             for sid in (record["served_model"] or "").split(",")]
            == [sid.lower().removesuffix(".gguf")
                for sid in record["served_model_expected"].split(",")])
```

Expected deciding detector: fault-controls' served-model fault F5 (or any pair-vector change). Actual F5 still detects its existing unrelated forged ID; no detector output changes. `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/fault-controls.py:292-293` fixes that corruption to `row["served_model"] = "kama-forged-id"`. [INFERENCE] It does not discriminate exact equality from normalization of an otherwise matching ID. This is a coverage finding, not permission to normalize the production contract.

### F2 — H6 escapes both route and malformed-output controls

Source site: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:454-459`, quote: "stub accepted no requests; probe never". The sole insertion, after original line 458 and before the return, was:

```python
            record["passed"] = True
```

Expected deciding detector: fault-controls' behavioral/error controls, especially route F6 or malformed F8, or the pair. Actual: no change. `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/fault-controls.py:242-243` deliberately executes `hit("/health")`, while lines 253-264 run the real probe before corrupting stdout. F7 takes the earlier timeout return (`/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:447-451`). [INFERENCE] Those inputs do not exercise the normal-return-with-zero-stub-requests acceptance branch changed by H6. The mutation was not generalized to other error branches.

### F3 — H7 escapes malformed-output controls

Source site: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:397`, quote: `row = rows[0]`. The only replacement was:

```python
    row = rows[-1]
```

Expected deciding detector: malformed-output fault F8 or the pair. Actual: both survive, with F8 still detecting all six variants. `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/fault-controls.py:170-187` supplies empty/missing rows, one non-object/null row, non-JSON, and non-UTF-8, but no distinct first and last objects. [INFERENCE] The exercised singleton valid outputs and malformed variants cannot distinguish the two indices.

### F4 — H8 is pre-existing policy, not a newly introduced defect

Source: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:382-383`, quote: "Contract: one JSON object whose "rows" is a non-empty list"; lines 395-397 reject empty lists and select only the first row. There is no exact-one-row guard to weaken. I did not insert an artificial no-op or tighten an unrelated cardinality condition merely to manufacture a fourth mutant.

The witness runs the real probe, appends a second object carrying verdict `FORGED_SECOND_ROW`, reason `ungraded-second-row`, and served ID `not-the-served-id`, and preserves the real probe's exit code. On pristine, unchanged-H8 mutation-phase, and restored bytes it produced:

```json
{"tests":1,"passes":1,"failures":0,"record":{"name":"ReadyControls.expect-exact-id","verdict":"MODEL_OK","reason":"matched","served_model":"kama-ready","route_ok":true,"served_model_ok":true,"error":null,"passed":true},"exit":0}
```

The recorded requests were GET `/v1/models` and GET `/health`; this was not a fake result that bypassed the serving route. This witness demonstrates current acceptance, **not a contract violation**: the documented validator explicitly grades the first object in a non-empty list.

## Actual detector outputs

The following actual output tuple occurred independently in **every** H5/H6/H7/H8 copy in **all three** phases:

```text
before probe: tests=72 passes=55 failures=17; exit=1
current probe: tests=72 passes=72 failures=0; exit=0
fault-controls: detected=8 accepted=0; exit=0
F0: check_exit=0 detected=true
F1/F2/F3/F4/F5/F7: check_exit=1 detected=true
F6: check_exit=[1,1,1,1] detected=true
F8: check_exit=[1,1,1,1,1,1] detected=true
```

F0's actual explanation: "check exited 0 with JSON; all 5 rows passed (positive control healthy)". There were no outer timeout, JSON-parse, or process-spawn errors.

The existing pair comparator was reused from `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/c1/mutants.py:809-846`, not replaced by a pass/fail-count-only comparison. It compares totals, row presence and every `SIG_FIELDS` value, normalizing requests as a unique `(method,path)` set. For each applied mutant and each restored copy its returned lists were literally `{"before":[],"current":[]}`.

As an additional reproducibility fingerprint, the canonical normalized pair output (exit, totals, records with `SIG_FIELDS`) had these hashes in every copy and phase:

- before: `1f7bdc0816c61da94234036cebffc7c3bad8cd2628e32644441cd1c461b1ec2c`
- current: `48b79b4ad9139cb3160c490e96f26aafde619ecd3b821cd586315661febe1bce`

Volatile ports, source paths, probe hashes and request retry counts were excluded exactly as the existing comparison requires. `served_model_expected` is not a `SIG_FIELDS` member; the comparator itself was left unchanged.

## Before, mutant and exact-restoration hashes

Original check SHA-256: `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099`.

| Copy | Pristine SHA-256 | Mutation-phase SHA-256 | Restored SHA-256 | Exact restored-byte comparison |
|---|---|---|---|---|
| H5 | `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099` | `fab14d2da26568cce976747d10e2a8a5a1264621941b67e237330e85f9dba1e6` | `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099` | `true` |
| H6 | `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099` | `30623b53c544b6e2f6011375ab22aea81a07ef0a650c8ff942dcd0b68519004f` | `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099` | `true` |
| H7 | `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099` | `eb7b2ad5008fb6e6593055f444ec0cd46c183b57dd85337570250e18f9632d05` | `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099` | `true` |
| H8 | `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099` | `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099` | `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099` | `true` |

The three edited copies were surgically restored by reversing only their own insertion/replacement, then the detectors were rerun on those restored bytes. An actual full-byte comparison against the untouched clone original returned true for each copy, in addition to matching hashes.

Other unchanged input hashes:

- fault-controls: `d3eaadeb8a061b4e322868d569df77afbd7331089d06b06c86a2063fdc31b312`
- current probe: `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`
- historical probe: `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64`
- nine-file / 72-row matrix-set digest (existing runner's formula): `bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32`

## Exact commands and exit codes

All command paths were absolute. Scratch paths below are historical/reproduction targets, not surviving evidence dependencies: outputs, edits and the complete short drivers are embedded in this report. The only persistent write is this report.

Clone command, exit **0**:

```sh
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17.MutC1Preregistered2-clone && git -C /tmp/KamaR17.MutC1Preregistered2-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3
```

Initial fingerprint / tool-version / listener command, exit **0**:

```sh
sha256sum /tmp/KamaR17.MutC1Preregistered2-clone/tests/probe-verdicts/check.py /tmp/KamaR17.MutC1Preregistered2-clone/tests/probe-verdicts/fault-controls.py /tmp/KamaR17.MutC1Preregistered2-clone/tools/kama-probe.sh /tmp/KamaR17.MutC1Preregistered2-clone/.ufo/waves/round-16/frozen/kama-probe-before.sh && python3 --version && ss -ltnp
```

Observed existing Python: `Python 3.14.8`. The staging command, exit **0**:

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 /tmp/KamaR17.MutC1Preregistered2-clone/probe.py stage
```

The following three driver commands each exited **0**, in this order. Independent detector invocations used a six-worker executor. An initial asynchronous attempt at the pristine command was refused by the tool with "Background job limit reached (100)" **before execution**; the same command was then executed synchronously once. The restored command's completion was delivered as background job `bg_6426`; it was not rerun.

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17.MutC1Preregistered2-clone/guard TMPDIR=/tmp/KamaR17.MutC1Preregistered2-clone/tmp python3 /tmp/KamaR17.MutC1Preregistered2-clone/probe.py detect pristine
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17.MutC1Preregistered2-clone/guard TMPDIR=/tmp/KamaR17.MutC1Preregistered2-clone/tmp python3 /tmp/KamaR17.MutC1Preregistered2-clone/probe.py detect mutated
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17.MutC1Preregistered2-clone/guard TMPDIR=/tmp/KamaR17.MutC1Preregistered2-clone/tmp python3 /tmp/KamaR17.MutC1Preregistered2-clone/probe.py detect restored
```

Exact child argv below; each command ran once in each phase. The working directory was the corresponding absolute `/tmp/KamaR17.MutC1Preregistered2-clone/scratch/H5`, H6, H7 or H8 directory. All inherited the identical `PYTHONDONTWRITEBYTECODE=1`, guard `PYTHONPATH`, and clone-local `TMPDIR` shown above. Column exits are pristine / mutation / restored.

| Copy / detector | Exact executed command | Exits |
|---|---|---|
| H5 / before | `/usr/bin/python3 /tmp/KamaR17.MutC1Preregistered2-clone/scratch/H5/check.py --probe /tmp/KamaR17.MutC1Preregistered2-clone/.ufo/waves/round-16/frozen/kama-probe-before.sh --json` | 1 / 1 / 1 |
| H5 / current | `/usr/bin/python3 /tmp/KamaR17.MutC1Preregistered2-clone/scratch/H5/check.py --probe /tmp/KamaR17.MutC1Preregistered2-clone/tools/kama-probe.sh --json` | 0 / 0 / 0 |
| H5 / controls | `/usr/bin/python3 /tmp/KamaR17.MutC1Preregistered2-clone/tests/probe-verdicts/fault-controls.py --check /tmp/KamaR17.MutC1Preregistered2-clone/scratch/H5/check.py --json` | 0 / 0 / 0 |
| H6 / before | `/usr/bin/python3 /tmp/KamaR17.MutC1Preregistered2-clone/scratch/H6/check.py --probe /tmp/KamaR17.MutC1Preregistered2-clone/.ufo/waves/round-16/frozen/kama-probe-before.sh --json` | 1 / 1 / 1 |
| H6 / current | `/usr/bin/python3 /tmp/KamaR17.MutC1Preregistered2-clone/scratch/H6/check.py --probe /tmp/KamaR17.MutC1Preregistered2-clone/tools/kama-probe.sh --json` | 0 / 0 / 0 |
| H6 / controls | `/usr/bin/python3 /tmp/KamaR17.MutC1Preregistered2-clone/tests/probe-verdicts/fault-controls.py --check /tmp/KamaR17.MutC1Preregistered2-clone/scratch/H6/check.py --json` | 0 / 0 / 0 |
| H7 / before | `/usr/bin/python3 /tmp/KamaR17.MutC1Preregistered2-clone/scratch/H7/check.py --probe /tmp/KamaR17.MutC1Preregistered2-clone/.ufo/waves/round-16/frozen/kama-probe-before.sh --json` | 1 / 1 / 1 |
| H7 / current | `/usr/bin/python3 /tmp/KamaR17.MutC1Preregistered2-clone/scratch/H7/check.py --probe /tmp/KamaR17.MutC1Preregistered2-clone/tools/kama-probe.sh --json` | 0 / 0 / 0 |
| H7 / controls | `/usr/bin/python3 /tmp/KamaR17.MutC1Preregistered2-clone/tests/probe-verdicts/fault-controls.py --check /tmp/KamaR17.MutC1Preregistered2-clone/scratch/H7/check.py --json` | 0 / 0 / 0 |
| H8 / before | `/usr/bin/python3 /tmp/KamaR17.MutC1Preregistered2-clone/scratch/H8/check.py --probe /tmp/KamaR17.MutC1Preregistered2-clone/.ufo/waves/round-16/frozen/kama-probe-before.sh --json` | 1 / 1 / 1 |
| H8 / current | `/usr/bin/python3 /tmp/KamaR17.MutC1Preregistered2-clone/scratch/H8/check.py --probe /tmp/KamaR17.MutC1Preregistered2-clone/tools/kama-probe.sh --json` | 0 / 0 / 0 |
| H8 / controls | `/usr/bin/python3 /tmp/KamaR17.MutC1Preregistered2-clone/tests/probe-verdicts/fault-controls.py --check /tmp/KamaR17.MutC1Preregistered2-clone/scratch/H8/check.py --json` | 0 / 0 / 0 |
| H8 / two-row-witness | `/usr/bin/python3 /tmp/KamaR17.MutC1Preregistered2-clone/scratch/H8/check.py --probe /tmp/KamaR17.MutC1Preregistered2-clone/two-row.sh --only ReadyControls.expect-exact-id --json` | 0 / 0 / 0 |

Comparison/restoration/listener command, exit **0** (it internally ran `ss -ltnp`, exit **0**):

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 /tmp/KamaR17.MutC1Preregistered2-clone/compare.py
```

Actual listener audit extracted from that command:

```json
{
  "command": "ss -ltnp",
  "exit": 0,
  "owned_bind_count": 2439,
  "owned_process_count": 279,
  "min_bound_port": 49159,
  "max_bound_port": 65534,
  "forbidden_binds": [],
  "owned_pids_still_listening": []
}
```

All owned binds were to `127.0.0.1`, within 49152–65535; the actual observed range was 49159–65534. No llama-server was started. The safety guard only changes ephemeral-listener allocation, identically in every phase; it rejects non-loopback and protected binds and logs owned PID/port pairs. Neither protected consumer port was bound or contacted by these probes. Existing unrelated listeners were not stopped.

## Limitations and installs

- This is a bounded synthetic probe-harness mutation exercise, not a live runtime validation, round judgment, integration, or shipping decision.
- H5–H7 are hold-out mutation survivors. Their count does not replace or disprove the lesson's original ten-mutant result. The existing F0–F8 controls still reject their eight registered faults in these runs.
- H8 is an inapplicable registration because acceptance was already present; it was tested as an unchanged control and separate input-admission witness, not mislabeled as a novel mutation.
- No extra detector was added to turn a survivor into a kill, and no production contract or lane source was changed.
- Raw subprocess documents were held only in disposable scratch; the report preserves observed counts, per-fault exit vectors, zero pair diffs, hashes, exact commands and reproduction drivers inline.
- One report-evidence loader initially failed with `JSONDecodeError` because a bare tool `:raw` read delivered only 300 lines plus a continuation footer. Explicit `:1-850:raw` reads recovered the existing receipts without rerunning any detector. This tool behavior was reported to `xd://report_issue`.
- **Installs/updates: none.** Only existing Python 3.14.8, git, bash/curl dependencies of the probe, sha256sum and ss were used. No pacman transaction, host restart or other runtime invocation occurred.

## Embedded reproduction drivers

Materialize each named file under the same disposable clone, preserving the final newline of every code block. Stage once; run pristine; apply exactly the three edits above; run mutation; reverse those exact edits; run restored; then compare. H8 remains untouched throughout.

### `/tmp/KamaR17.MutC1Preregistered2-clone/probe.py`

```python
#!/usr/bin/env python3
"""Scoped H5-H8 probe. All generated files stay in this disposable clone."""
import argparse
import concurrent.futures
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import sys

ROOT = Path('/tmp/KamaR17.MutC1Preregistered2-clone')
SPEC = importlib.util.spec_from_file_location('r17_mutants', ROOT / '.ufo/waves/round-17/c1/mutants.py')
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)
SEATS = ('H5', 'H6', 'H7', 'H8')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def stage():
    matrix, matrix_digest = RUNNER.matrix_set()
    source = RUNNER.CHECK_CURRENT.read_text(encoding='utf-8')
    for name in SEATS:
        RUNNER.stage_check(ROOT / 'scratch' / name, source, matrix)
    (ROOT / 'tmp').mkdir(exist_ok=True)
    doc = {'source_sha256': digest(RUNNER.CHECK_CURRENT),
           'matrix_sha256': matrix_digest, 'matrix_files': len(matrix),
           'scratch': [str(ROOT / 'scratch' / name) for name in SEATS]}
    print(json.dumps(doc, indent=2))
    return 0

def invoke(name, kind, phase, before):
    directory = ROOT / 'scratch' / name
    if kind == 'controls':
        command = [sys.executable, str(RUNNER.FAULT_CONTROLS), '--check', str(directory / 'check.py'), '--json']
        timeout = 240
    elif kind == 'two-row-witness':
        command = [sys.executable, str(directory / 'check.py'), '--probe', str(ROOT / 'two-row.sh'), '--only', 'ReadyControls.expect-exact-id', '--json']
        timeout = 60
    else:
        probe = before if kind == 'before' else RUNNER.PROBE_CURRENT
        command = [sys.executable, str(directory / 'check.py'), '--probe', str(probe), '--json']
        timeout = 180
    observation = RUNNER.run_cmd(command, cwd=str(directory), timeout=timeout)
    target = ROOT / 'evidence' / phase / name
    target.mkdir(parents=True, exist_ok=True)
    (target / (kind + '.json')).write_text(json.dumps(observation, indent=2) + '\n', encoding='utf-8')
    try:
        doc = json.loads(observation['stdout'])
        parse_error = None
    except (ValueError, TypeError) as error:
        doc, parse_error = None, str(error)
    summary = {'seat': name, 'detector': kind, 'command': shlex.join(command),
               'cwd': str(directory), 'exit': observation['exit'],
               'error': observation['error'], 'parse_error': parse_error}
    if isinstance(doc, dict):
        for key in ('schema', 'tests', 'passes', 'failures', 'detected', 'accepted'):
            if key in doc:
                summary[key] = doc[key]
        if kind == 'controls':
            summary['positive_control'] = doc.get('positive_control')
            summary['faults'] = doc.get('faults')
        if kind == 'two-row-witness':
            summary['records'] = doc.get('records')
        if kind in ('before', 'current'):
            signature = {'exit': observation['exit'],
                         'totals': {key: doc.get(key) for key in ('tests', 'passes', 'failures')},
                         'records': [{field: RUNNER.norm_field(field, row.get(field)) for field in RUNNER.SIG_FIELDS}
                                     for row in doc.get('records', [])]}
            canonical = json.dumps(signature, sort_keys=True, separators=(',', ':'))
            summary['pair_signature_sha256'] = hashlib.sha256(canonical.encode()).hexdigest()
    return summary

def detect(phase):
    before, label = RUNNER.choose_before_probe()
    tasks = [(seat, kind) for seat in SEATS for kind in ('before', 'current', 'controls')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(invoke, seat, kind, phase, before) for seat, kind in tasks]
        observations = [future.result() for future in futures]
    observations.append(invoke('H8', 'two-row-witness', phase, before))
    doc = {'phase': phase, 'before_label': label,
           'check_hashes': {seat: digest(ROOT / 'scratch' / seat / 'check.py') for seat in SEATS},
           'observations': observations}
    for seat in SEATS:
        pair = [o for o in observations if o['seat'] == seat and o['detector'] in ('before', 'current')]
        controls = next(o for o in observations if o['seat'] == seat and o['detector'] == 'controls')
        valid = (all(o.get('error') is None and o.get('parse_error') is None for o in pair)
                 and all((o['exit'], o.get('passes'), o.get('failures')) == ((1, 55, 17) if o['detector'] == 'before' else (0, 72, 0)) for o in pair)
                 and controls['exit'] == 0 and controls.get('accepted') == 0
                 and controls.get('detected') == 8
                 and controls.get('positive_control', {}).get('detected') is True)
        doc.setdefault('expected_detector_outputs', {})[seat] = valid
    target = ROOT / 'evidence' / phase / 'summary.json'
    target.write_text(json.dumps(doc, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(doc, indent=2))
    return 0 if all(doc['expected_detector_outputs'].values()) else 1

parser = argparse.ArgumentParser()
parser.add_argument('mode', choices=('stage', 'detect'))
parser.add_argument('phase', nargs='?', choices=('pristine', 'mutated', 'restored'))
args = parser.parse_args()
if args.mode == 'stage':
    sys.exit(stage())
if args.phase is None:
    parser.error('detect requires a phase')
sys.exit(detect(args.phase))
```

### `/tmp/KamaR17.MutC1Preregistered2-clone/guard/sitecustomize.py`

```python
"""Keep all probe-owned listeners away from registered-consumer ports."""
import errno
import json
import os
from pathlib import Path
import secrets
import socket

_BIND = socket.socket.bind
_FORBIDDEN = {8080, 34113}
_LOG = Path('/tmp/KamaR17.MutC1Preregistered2-clone/binds.jsonl')

def safe_bind(sock, address):
    if isinstance(address, tuple) and len(address) == 2:
        host, port = address
        if host != '127.0.0.1' or port in _FORBIDDEN:
            raise PermissionError('scoped probe refuses non-loopback or protected listener')
        if port == 0:
            for _ in range(256):
                candidate = 49152 + secrets.randbelow(65536 - 49152)
                try:
                    result = _BIND(sock, (host, candidate))
                except OSError as error:
                    if error.errno == errno.EADDRINUSE:
                        continue
                    raise
                break
            else:
                raise OSError(errno.EADDRINUSE, 'scoped high-port candidates exhausted')
        else:
            result = _BIND(sock, address)
        record = json.dumps({'pid': os.getpid(), 'host': host, 'port': sock.getsockname()[1]}) + '\n'
        fd = os.open(_LOG, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
        try:
            os.write(fd, record.encode())
        finally:
            os.close(fd)
        return result
    return _BIND(sock, address)

socket.socket.bind = safe_bind
```

### `/tmp/KamaR17.MutC1Preregistered2-clone/two-row.sh`

```sh
#!/usr/bin/env bash
exec python3 - "$@" <<'TWO_ROW_EOF'
import json
import subprocess
import sys
probe = '/tmp/KamaR17.MutC1Preregistered2-clone/tools/kama-probe.sh'
result = subprocess.run(['bash', probe, *sys.argv[1:]], capture_output=True)
doc = json.loads(result.stdout)
doc['rows'].append({'verdict': 'FORGED_SECOND_ROW', 'reason': 'ungraded-second-row', 'drift': True, 'served_model': 'not-the-served-id'})
print(json.dumps(doc))
sys.stderr.buffer.write(result.stderr)
sys.exit(result.returncode)
TWO_ROW_EOF
```

### `/tmp/KamaR17.MutC1Preregistered2-clone/compare.py`

```python
#!/usr/bin/env python3
"""Compare completed observations using the lane's existing pair comparator."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path('/tmp/KamaR17.MutC1Preregistered2-clone')
spec = importlib.util.spec_from_file_location('r17_mutants', ROOT / '.ufo/waves/round-17/c1/mutants.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

def raw(phase, seat, kind):
    return json.loads((ROOT / 'evidence' / phase / seat / (kind + '.json')).read_text())

def pair(phase, seat, kind):
    observation = raw(phase, seat, kind)
    return {'exit': observation['exit'], 'doc': json.loads(observation['stdout']),
            'error': observation['error'], 'stderr_tail': observation['stderr'][-400:]}

result = {'mutants': {}, 'original_sha256': runner.sha256_file(runner.CHECK_CURRENT),
          'matrix_sha256': runner.matrix_set()[1]}
for seat in ('H5', 'H6', 'H7', 'H8'):
    phases = {phase: json.loads((ROOT / 'evidence' / phase / 'summary.json').read_text()) for phase in ('pristine', 'mutated', 'restored')}
    item = {'sha256': {phase: doc['check_hashes'][seat] for phase, doc in phases.items()}}
    item['restored_bytes_exact'] = (ROOT / 'scratch' / seat / 'check.py').read_bytes() == runner.CHECK_CURRENT.read_bytes()
    for phase in ('mutated', 'restored'):
        item[phase + '_pair_diffs'] = {kind: runner.diff_observations(pair('pristine', seat, kind), pair(phase, seat, kind)) for kind in ('before', 'current')}
        base = json.loads(raw('pristine', seat, 'controls')['stdout'])
        current = json.loads(raw(phase, seat, 'controls')['stdout'])
        item[phase + '_controls'] = {
            'exit': raw(phase, seat, 'controls')['exit'],
            'accepted': current['accepted'], 'detected': current['detected'],
            'accepted_delta': current['accepted'] - base['accepted'],
            'accepted_ids': [fault['id'] for fault in current['faults'] if not fault['detected']],
            'positive_healthy': current['positive_control']['detected']}
    item['status'] = 'n/a (two-row acceptance already present)' if seat == 'H8' else ('killed' if any(item['mutated_pair_diffs'].values()) or item['mutated_controls']['accepted_delta'] != 0 else 'survived')
    result['mutants'][seat] = item
binds = [json.loads(line) for line in (ROOT / 'binds.jsonl').read_text().splitlines()]
ss = subprocess.run(['ss', '-ltnp'], text=True, capture_output=True)
listener_pids = {int(pid) for pid in re.findall(r'pid=(\d+)', ss.stdout)}
owned_pids = {bind['pid'] for bind in binds}
result['listeners'] = {'command': 'ss -ltnp', 'exit': ss.returncode,
                       'stdout': ss.stdout, 'stderr': ss.stderr,
                       'owned_bind_count': len(binds), 'owned_process_count': len(owned_pids),
                       'min_bound_port': min(bind['port'] for bind in binds),
                       'max_bound_port': max(bind['port'] for bind in binds),
                       'forbidden_binds': [bind for bind in binds if bind['port'] in {8080, 34113} or bind['host'] != '127.0.0.1'],
                       'owned_pids_still_listening': sorted(listener_pids & owned_pids)}
(ROOT / 'evidence' / 'comparison.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
```

## Final cleanup evidence

Executed from `/tmp`, exit **0**:

```sh
rm -rf -- /tmp/KamaR17.MutC1Preregistered2-clone && test ! -e /tmp/KamaR17.MutC1Preregistered2-clone && printf '%s\n' 'scratch_removed=true' && ss -ltnp
```

Actual output began `scratch_removed=true`. The final `ss -ltnp` output contained no listener in the guarded 49152–65535 range. The earlier PID-matched audit independently reported `owned_pids_still_listening: []`. All owned scratch, raw outputs, copied source, wrappers, safety guard and short drivers were removed. No lane source, matrix, manifest, fleet file or sibling was edited; only this report remains as the scoped deliverable.
