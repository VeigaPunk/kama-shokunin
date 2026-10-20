VERDICT: partial — the frozen gate ACCEPTS 3/5 requested forgeries; literal API-key append and a vacuous v2 loading pass are rejected.

# MutBaselineForgeries — C1 before-evidence / R6

## Axes and scope

- **Operability:** challenge the frozen receipt gate's schema, argv and loading-evidence boundaries.
- **Calibration:** distinguish accepted forgeries from rejected ones, and do not count a failing baseline as a kill.
- Read-only advisory probe, not an official round measurement, admission judgment or integration. No lane source, frozen file, historical receipt, runtime or model was changed.
- Interpreter observed: `Python 3.14.8`. No installs or updates.

All lane paths below are rooted at `/home/vgpnk/Projects/shokunin/kama-shokunin`:

- Input: `.ufo/waves/round-17/live/receipt-1.json`.
- Detector: `.ufo/waves/round-18/frozen/tests_llamacpp-live_check-receipt.py`.
- Scratch clone: `/tmp/kama-r18-MutBaselineForgeries-2`, branch `seat/MutBaselineForgeries-2`; deleted after exact restoration.

The executed detector for **every pristine, mutated and restored receipt** was:

```sh
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_llamacpp-live_check-receipt.py /tmp/kama-r18-MutBaselineForgeries-2/forgeries/CASE/receipt.json --expect-model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d
```

`CASE` was replaced by the exact case name in the table below. Cwd was the scratch clone. Each subprocess had a 10-second bound and its own process group. The five independent case triplets ran concurrently; each triplet remained pristine → mutation → exact-byte restoration. Restoration was in `finally`.

The frozen usage declares `0 receipt valid, 1 receipt invalid` at `.ufo/waves/round-18/frozen/tests_llamacpp-live_check-receipt.py:38-45`; its CLI exposes the optional model/server/probe/tool pins at lines 1358-1369. This probe used the requested model pin only. It did not execute the probe or rehash the installed server/model.

## Observed outcomes

Expected detector behavior is rejection of an extra/duplicate argv flag, a non-exact loading transition, and a true loading grade without observations. A minimum-schema policy should also reject a downgrade when such a policy is requested; the frozen invocation has no such option.

| Case / mutant | Pristine exit | Mutant exit | Restored exit | Frozen gate | Mutation result |
|---|---:|---:|---:|---|---|
| `v1-schema-with-v1-check-ids` | 0 | 0 | 0 | ACCEPTS | survived the requested downgrade probe; see compatibility limitation |
| `api-key-literal-append` | 0 | 1 | 0 | REJECTS | killed by the argv-tail check |
| `duplicate-port-before-tail` | 0 | 0 | 0 | ACCEPTS | survived |
| `nonexact-models-503-transition` | 0 | 0 | 0 | ACCEPTS | survived |
| `zero-loading-check-claims-pass` | 0 | 1 | 0 | REJECTS | killed by the loading-evidence checks |

Counting the captured run record with the following jq selector via the read tool returned the JSON below:

```jq
{
  accepted: ([.cases[] | select(.mutated.exit == 0)] | length),
  rejected: ([.cases[] | select(.mutated.exit == 1)] | length),
  inconclusive: ([.cases[] | select(.verdict == "inconclusive")] | length),
  baseline_passes: ([.cases[] | select(.pristine.exit == 0)] | length),
  restored_passes: ([.cases[] | select(.restored.exit == 0)] | length),
  exact_restorations: ([.cases[] | select(.restored_bytes_equal)] | length),
  timeouts: ([.cases[] | (.pristine, .mutated, .restored) | select(.timed_out)] | length)
}
```

```json
{"accepted":3,"rejected":2,"inconclusive":0,"baseline_passes":5,"restored_passes":5,"exact_restorations":5,"timeouts":0}
```

## Findings and located evidence

1. **The requested v1 relabelling is accepted.** Changed only the semantic schema/check-set pair: `schema` → `kama-llamacpp-live/v1`; removed `loading_envelope_graded`; renamed `teardown_graceful` → `teardown_exited`. All underlying observations stayed pristine. Frozen gate lines 203-208 select the path using `is_v2 = schema == RECEIPT_SCHEMA_V2`; lines 653-660 select the required check IDs from that declaration. The CLI at lines 1358-1373 has no minimum-schema option. **Limitation:** this is also a structurally legitimate legacy v1 conversion. This run demonstrates acceptance and absence of a floor, not that a separately corrupted v2 predicate was bypassed. Rejecting every v1 receipt would violate the stated compatibility requirement.

2. **Appending `--api-key X` literally to the end is rejected, not accepted.** Only `argv` changed, using `.extend(['--api-key', 'X'])`. Frozen gate `.ufo/waves/round-18/frozen/tests_llamacpp-live_check-receipt.py:419-421` requires `tail = argv[-2:]` to equal `['--no-webui', '--offline']`. Its exact reported failure was `argv tail ['--api-key', 'X'] != ['--no-webui', '--offline']`. This kill does **not** establish credential-flag filtering: the terminal suffix was the failing predicate. A tail-preserving API-key insertion was not run and is not claimed accepted here. Round-17's broader extra-flag debt at `corpus/lessons/round-17.md:256-262` says “extra argv flags”; the literal-append result must not be quoted as an acceptance.

3. **A duplicate `--port` is accepted when the required tail is preserved.** Only `argv` changed, by inserting `['--port', '40089']` immediately before `--no-webui --offline`. The original `--port 40089` remained. Frozen gate `.ufo/waves/round-18/frozen/tests_llamacpp-live_check-receipt.py:169-176` scans from the beginning and returns `return argv[i + 1]`; lines 407-410 compare that first value with the receipt port. The extra occurrence did not cause rejection. No server was launched, so no claim is made about actual duplicate-flag parsing by llama-server.

4. **A non-exact `/v1/models` 503 transition body is accepted while `loading_503_bodies` stays exact.** Exactly one leaf changed: `transitions[1].body`, replacing message `Loading model` with `Warming`. The body became `{"error":{"message":"Warming","type":"unavailable_error","code":503}}`. The original `loading_503`, `loading_503_bodies`, check and transition `body_sha256` were intentionally unchanged to retain the requested single-field mutation. Frozen gate `.ufo/waves/round-18/frozen/tests_llamacpp-live_check-receipt.py:441-443` checks transition presence with `t.get("status") == 503`; lines 920-935 grade `bodies = receipt.get("loading_503_bodies")`. Exact message matching is defined at lines 107-116 as `err.get("message") == "Loading model"`. The corrupted transition was nevertheless `VALID`. This is direct before-evidence for the transition-body part of R6; the retained stale body hash is an additional inconsistency in this same one-leaf fixture, not a separately measured mutant.

5. **A v2 receipt claiming a true loading grade after zero observations is rejected.** Made a coherent zero-observation state: `loading_observed=false`, `loading_503=null`, `loading_503_bodies=[]`, `loading_envelope_exact=null`, removed all status-503 transitions, and zeroed the loading check's observed counts/booleans while retaining `passed=true`. This necessarily changes related evidence fields, not one JSON leaf. Frozen gate `.ufo/waves/round-18/frozen/tests_llamacpp-live_check-receipt.py:908-935` says “nothing to grade cannot pass it” and rejects absent/empty evidence plus the forged true grade. This probe does not measure the producer's zero-observation exit classification or a legitimate v3 null grade.

All numbered findings refer to the frozen gate, not the gate being built by other seats.

## Actual detector output

All fifteen invocations had empty stderr. No invocation timed out. `[pristine]`, `[mutated]` and `[restored]` labels and exit annotations below identify the captured runs; the following lines are their stdout.

### v1-schema-with-v1-check-ids

```text
[pristine, exit 0]
VALID /tmp/kama-r18-MutBaselineForgeries-2/forgeries/v1-schema-with-v1-check-ids/receipt.json
[mutated, exit 0]
VALID /tmp/kama-r18-MutBaselineForgeries-2/forgeries/v1-schema-with-v1-check-ids/receipt.json
[restored, exit 0]
VALID /tmp/kama-r18-MutBaselineForgeries-2/forgeries/v1-schema-with-v1-check-ids/receipt.json
```

### api-key-literal-append

```text
[pristine, exit 0]
VALID /tmp/kama-r18-MutBaselineForgeries-2/forgeries/api-key-literal-append/receipt.json
[mutated, exit 1]
INVALID /tmp/kama-r18-MutBaselineForgeries-2/forgeries/api-key-literal-append/receipt.json: 1 problem(s)
  - argv tail ['--api-key', 'X'] != ['--no-webui', '--offline']
[restored, exit 0]
VALID /tmp/kama-r18-MutBaselineForgeries-2/forgeries/api-key-literal-append/receipt.json
```

### duplicate-port-before-tail

```text
[pristine, exit 0]
VALID /tmp/kama-r18-MutBaselineForgeries-2/forgeries/duplicate-port-before-tail/receipt.json
[mutated, exit 0]
VALID /tmp/kama-r18-MutBaselineForgeries-2/forgeries/duplicate-port-before-tail/receipt.json
[restored, exit 0]
VALID /tmp/kama-r18-MutBaselineForgeries-2/forgeries/duplicate-port-before-tail/receipt.json
```

### nonexact-models-503-transition

```text
[pristine, exit 0]
VALID /tmp/kama-r18-MutBaselineForgeries-2/forgeries/nonexact-models-503-transition/receipt.json
[mutated, exit 0]
VALID /tmp/kama-r18-MutBaselineForgeries-2/forgeries/nonexact-models-503-transition/receipt.json
[restored, exit 0]
VALID /tmp/kama-r18-MutBaselineForgeries-2/forgeries/nonexact-models-503-transition/receipt.json
```

### zero-loading-check-claims-pass

```text
[pristine, exit 0]
VALID /tmp/kama-r18-MutBaselineForgeries-2/forgeries/zero-loading-check-claims-pass/receipt.json
[mutated, exit 1]
INVALID /tmp/kama-r18-MutBaselineForgeries-2/forgeries/zero-loading-check-claims-pass/receipt.json: 3 problem(s)
  - loading_envelope_graded: no loading_503 body stored, nothing graded
  - loading_envelope_graded: loading_503_bodies missing or empty in a v2 receipt
  - check 'loading_envelope_graded': claims passed=True but evidence re-derivation gives False
[restored, exit 0]
VALID /tmp/kama-r18-MutBaselineForgeries-2/forgeries/zero-loading-check-claims-pass/receipt.json
```

## Hashes and restoration evidence

Every scratch receipt's before **and** restored SHA-256 was:

```text
f34afb545db28fc37b2df8179f5872d2e84a20a140a0f3367a9f60d1864702a4
```

Every restored receipt also passed direct byte equality against the original input, not only hash equality. All five restored detectors exited 0.

| Case | Mutated SHA-256 |
|---|---|
| `v1-schema-with-v1-check-ids` | `0df5267526264976b05c620377c0a7c8a7265cd2cc595266a19a3482611fe3b1` |
| `api-key-literal-append` | `63c7244f342cf1e03118278d7e0b20e7c1d134c9d3bdba29f41392b8fcd5691f` |
| `duplicate-port-before-tail` | `83d41beca59c8eb29bdfc500c3a74554862d87a20d4830e56b7f15b033f7659d` |
| `nonexact-models-503-transition` | `8d75d41ab3a2f57c02b28e8585b0ed2057b33423a81cd02b44c5eefd2ca3667e` |
| `zero-loading-check-claims-pass` | `17aa4322b25a7fd9b6b8f03696dba2357d023c602276fe9bc2872e6702935b0d` |

Original lane input and frozen gate were hashed before and after the triplets:

| Lane artifact | Before SHA-256 | After SHA-256 |
|---|---|---|
| `.ufo/waves/round-17/live/receipt-1.json` | `f34afb545db28fc37b2df8179f5872d2e84a20a140a0f3367a9f60d1864702a4` | `f34afb545db28fc37b2df8179f5872d2e84a20a140a0f3367a9f60d1864702a4` |
| `.ufo/waves/round-18/frozen/tests_llamacpp-live_check-receipt.py` | `ad6801791f2ada896a7ee188609391aac86185c47320dbf415331869ca9cd2a5` | `ad6801791f2ada896a7ee188609391aac86185c47320dbf415331869ca9cd2a5` |

The gate hash matches `.ufo/waves/round-18/frozen/SHA256SUMS:4`, whose recorded filename is `tests_llamacpp-live_check-receipt.py`.

After recording the restored runs, executed:

```sh
rm -rf -- /tmp/kama-r18-MutBaselineForgeries-2 && test ! -e /tmp/kama-r18-MutBaselineForgeries-2 && printf 'scratch_removed=yes\n'
```

Observed:

```text
scratch_removed=yes
```

No server, listener or other runtime was started. Only the requested report remains as a lane write.

## Retained executed harness for reproduction

The following is the executed scratch harness, retained here because the scratch files were removed. It generates the five fixtures from the read-only original, prints the complete run record, and restores exact bytes even if detection fails. It is not a new lane gate.

Scratch setup and invocation used:

```sh
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-MutBaselineForgeries-2
git -C /tmp/kama-r18-MutBaselineForgeries-2 switch -q -c seat/MutBaselineForgeries-2
python3 /tmp/kama-r18-MutBaselineForgeries-2/forgery_probe.py
```

`forgery_probe.py` contents:

```python
#!/usr/bin/env python3
"""Isolated R18 before-evidence: mutate receipt fixtures, never lane bytes."""
import concurrent.futures
import copy
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess

ROOT = Path('/tmp/kama-r18-MutBaselineForgeries-2')
LANE = Path('/home/vgpnk/Projects/shokunin/kama-shokunin')
SOURCE = LANE / '.ufo/waves/round-17/live/receipt-1.json'
GATE = LANE / '.ufo/waves/round-18/frozen/tests_llamacpp-live_check-receipt.py'
MODEL_SHA = '270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d'
BASE = SOURCE.read_bytes()
GATE_BYTES = GATE.read_bytes()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def detect(path):
    argv = ['python3', str(GATE), str(path), '--expect-model-sha256', MODEL_SHA]
    proc = subprocess.Popen(argv, cwd=ROOT, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True,
                            start_new_session=True)
    timed_out = False
    try:
        stdout, stderr = proc.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(proc.pid, signal.SIGKILL)
        stdout, stderr = proc.communicate()
    return {'argv': argv, 'timeout_seconds': 10, 'timed_out': timed_out,
            'exit': proc.returncode, 'stdout': stdout, 'stderr': stderr}


def downgrade(receipt):
    receipt['schema'] = 'kama-llamacpp-live/v1'
    receipt['checks'] = [c for c in receipt['checks']
                         if c['id'] != 'loading_envelope_graded']
    next(c for c in receipt['checks']
         if c['id'] == 'teardown_graceful')['id'] = 'teardown_exited'


def append_api_key(receipt):
    receipt['argv'].extend(['--api-key', 'X'])


def duplicate_port(receipt):
    receipt['argv'][-2:-2] = ['--port', str(receipt['port'])]


def malformed_transition(receipt):
    row = next(t for t in receipt['transitions']
               if t.get('path') == '/v1/models' and t.get('status') == 503)
    row['body'] = '{"error":{"message":"Warming","type":"unavailable_error","code":503}}'


def zero_loading_pass(receipt):
    receipt['loading_observed'] = False
    receipt['loading_503'] = None
    receipt['loading_503_bodies'] = []
    receipt['loading_envelope_exact'] = None
    receipt['transitions'] = [t for t in receipt['transitions']
                              if t.get('status') != 503]
    check = next(c for c in receipt['checks']
                 if c['id'] == 'loading_envelope_graded')
    check['passed'] = True
    check['observed'] = {'all_exact': False, 'bodies_dropped': 0,
                         'distinct_bodies': 0, 'exact': None,
                         'loading_observed': False, 'total_503_responses': 0}


def changed_paths(before, after, prefix='$'):
    if type(before) is not type(after):
        return [prefix]
    if isinstance(before, dict):
        return [p for key in sorted(before.keys() | after.keys())
                for p in ([f'{prefix}.{key}'] if key not in before or key not in after
                          else changed_paths(before[key], after[key], f'{prefix}.{key}'))]
    if isinstance(before, list):
        if len(before) != len(after):
            return [prefix]
        return [p for index, (left, right) in enumerate(zip(before, after))
                for p in changed_paths(left, right, f'{prefix}[{index}]')]
    return [] if before == after else [prefix]


def probe_case(case):
    name, mutation = case
    case_dir = ROOT / 'forgeries' / name
    case_dir.mkdir(parents=True)
    path = case_dir / 'receipt.json'
    path.write_bytes(BASE)
    row = {'name': name, 'path': str(path), 'before_sha256': sha(path.read_bytes())}
    try:
        row['pristine'] = detect(path)
        original = json.loads(BASE)
        receipt = copy.deepcopy(original)
        mutation(receipt)
        row['changed_paths'] = changed_paths(original, receipt)
        mutated = (json.dumps(receipt, indent=2, sort_keys=True) + '\n').encode()
        path.write_bytes(mutated)
        row['mutant_sha256'] = sha(path.read_bytes())
        row['mutated'] = detect(path)
    finally:
        path.write_bytes(BASE)
        row['restored_sha256'] = sha(path.read_bytes())
        row['restored_bytes_equal'] = path.read_bytes() == BASE
        row['restored'] = detect(path)
    good_controls = all(row[phase]['exit'] == 0 and not row[phase]['timed_out']
                        for phase in ('pristine', 'restored'))
    mutant = row['mutated']
    if not good_controls or mutant['timed_out'] or not row['restored_bytes_equal']:
        row['verdict'] = 'inconclusive'
    elif mutant['exit'] == 1:
        row['verdict'] = 'killed'
    elif mutant['exit'] == 0:
        row['verdict'] = 'survived'
    else:
        row['verdict'] = 'inconclusive'
    return row


CASES = [('v1-schema-with-v1-check-ids', downgrade),
         ('api-key-literal-append', append_api_key),
         ('duplicate-port-before-tail', duplicate_port),
         ('nonexact-models-503-transition', malformed_transition),
         ('zero-loading-check-claims-pass', zero_loading_pass)]
with concurrent.futures.ThreadPoolExecutor(max_workers=len(CASES)) as executor:
    results = list(executor.map(probe_case, CASES))
summary = {'source': str(SOURCE), 'gate': str(GATE), 'cwd': str(ROOT),
           'python_version': subprocess.check_output(['python3', '--version'], text=True).strip(),
           'source_before_sha256': sha(BASE), 'source_after_sha256': sha(SOURCE.read_bytes()),
           'gate_before_sha256': sha(GATE_BYTES), 'gate_after_sha256': sha(GATE.read_bytes()),
           'cases': results}
output_path = ROOT / 'forgery-results.json'
output_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
print(json.dumps(summary, indent=2, sort_keys=True))
```

## Limitations and installs

- Before-evidence only. No current/v3 gate was executed; neither official `measure.py` nor `survivors.py` was run.
- The v1 case preserves good raw evidence; it is not independently sufficient to prove escape from a failing v2 behavioral predicate.
- Literal API-key append was rejected because of suffix placement. No unexecuted placement variant is asserted accepted.
- Duplicate port used the same value, and no real server parsing behavior was measured.
- The transition mutant changed only `body`, not its stored hash; both the exact aggregate loading body and its aggregate grade remained pristine.
- The zero-loading fixture was internally normalized but deliberately retained `passed=true`; it was not a well-formed v3 not-evaluated receipt.
- No new live serving or registered-consumer health claim. No surviving mutant authorizes a contract change.
- Installs/updates: **none**.
