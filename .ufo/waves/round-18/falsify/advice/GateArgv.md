VERDICT: confirm — all five insertion payloads rejected at every position via exact-equality, raw relative model.arg survives a genuine live run and gate, one scoped legacy-surface residual noted.

# GateArgv — falsification report (round 18, seat GateArgv)

## Target claim
C1 "exact argv" hardening: the v3 receipt gate must reject any tampered server argv — including api-key, duplicate host, duplicate port, short alias, or ctx-size inserted *before* the required suffix, not only at argv end — and the raw relative `model.arg` must remain valid on a genuine receipt.

## Environment & method
- Clone: `git clone /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-falsify-GateArgv/repo`; `git switch -c seat/GateArgv 1c325b2e58fcfdc6761f645b44cedfb1d65243e6` (HEAD `1c325b2 round-18: retain measured arms and repair counter classification seams`). Git status clean (0 modified files) before and after.
- Pristine hashes (verified unchanged at end):
  - `tests/llamacpp-live/check-receipt.py` = `c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335`
  - `tools/kama-llamacpp-live.py` = `dc036d7dcfe2933827c07f8bc0dedba68a24f7b099309871f6cb25ccb811a04b` (matches official `--expect-tool-sha256` in `runs/commands.json`)
- No installs performed. Python 3.14.8.

## Baseline (green)
`python3 tests/llamacpp-live/check-receipt.py --selftest` → exit 0, `selftest: 5 VALID and 1 NOT-EVALUATED receipts accepted; 61 mutations + unreadable case rejected`.

## Experiment 1 — insertion matrix (synthetic v3 receipt)
Harness source: full script reproduced in Report appendix. Method: `importlib`-loaded the gate, took `_selftest_receipt_v3()`, inserted each payload at three positions, wrote to `/tmp/kama-r18-falsify-GateArgv/cases/*.json`, ran the gate CLI with the four `--expect-*` pins (same pins as official `live-gate-*` commands).

Payloads × positions: `--api-key sk-attack`, `--host 0.0.0.0`, `--port 45679`, `--alias kama`, `-c 512` at **front@2** (after `argv[0] -m`), **pre-tail@-2** (before `--no-webui --offline`), and **end**.

Result: **15/15 rejected (exit 1)**, and in every one of the 15 cases the exact-equality check fired — message `argv does not exactly match the producer's server.realpath/model.arg/alias/host/port/ctx/threads command` (check-receipt.py:506–514). Sample stdout, e.g. `v3-dup-port-pre-tail@-2`:
```
INVALID /tmp/kama-r18-falsify-GateArgv/cases/v3-dup-port-pre-tail@-2.json: 1 problem(s)
  - argv does not exactly match the producer's server.realpath/model.arg/alias/host/port/ctx/threads command
```
Attribution: for the `argv_flag()`-blind positions (front@2, pre-tail@-2), the flag-based per-flag checks can't see the duplicate (first occurrence unchanged), so in 5/5 pre-tail cases the exact-equality check was the **sole** problem — i.e., it is the load-bearing detector, exactly the claimed design. front@2 additionally trips `-m` mismatch (payload shifts `argv_flag(argv,'-m')`), which corroborates rather than substitutes.

## Experiment 2 — raw relative model.arg on a genuine receipt (no-harm)
Ran the real installed tool from a scratch cwd with a relative `--model`:
```
cd /tmp/kama-r18-falsify-GateArgv/cwd
python3 /tmp/kama-r18-falsify-GateArgv/repo/tools/kama-llamacpp-live.py \
  --server /home/vgpnk/.local/opt/llama-b11755/llama-server \
  --model ./stories260K.gguf --model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d \
  --probe ./kama-probe.sh --alias kama-r18-relarg \
  --out /tmp/kama-r18-falsify-GateArgv/rel-live/receipt-rel.json
```
Exit 0, `outcome: pass`. Receipt records `'model': {'arg': './stories260K.gguf', 'path': '/tmp/kama-r18-falsify-GateArgv/cwd/stories260K.gguf', 'sha256': '270cba…256d'}` and `'argv': [..., '-m', './stories260K.gguf', ...]` — the tool passes the raw arg through to the child argv (it launches fine because the child inherits the tool's cwd) while storing the resolved realpath separately. Then gated with the same four `--expect-*` pins plus `--require-schema v3`:
```
VALID /tmp/kama-r18-falsify-GateArgv/rel-live/receipt-rel.json
GATE_EXIT=0
```
So a genuine receipt with a raw (non-realpath) `model.arg` passes; the exact-argv check compares `model.arg` to `argv[-m]` (not to `model.path`), so it does not force realpath normalization — no over-tightening. Control: if argv is normalized but `model.arg` stays relative, gate exits 1 with `-m` mismatch (check-receipt.py:474–477) — exact-equality is bidirectionally strict.

Negative control on the negative path: running with a model genuinely absent from cwd → exit 2, `setup_error: model-not-found:./stories260K.gguf`, confirming the run wasn't accidentally succeeding for the wrong reason.

## Findings
1. **CONFIRMED (main claim):** all five insertion payloads rejected at all three positions, including before the suffix; each rejection attributable to the exact-equality check (pre-tail cases: only problem emitted). No gap found in the v3 exact-argv floor.
2. **Residual, survive-visible (scoped, not a defect of the claim):** the same payload inserted into a **v2** receipt still gates VALID when run without `--require-schema v3` (case `v2-dup-port-no-floor`: exit 0, `VALID …`). Executed: exit 0, stdout `VALID /tmp/.../v2-dup-port-no-floor.json`. With `--require-schema v3` it exits 1. This is the intended schema-floor design (v2/v1 are legacy formats without the exact-argv rule), not a hidden hole — but any real gate usage must carry the `--require-schema v3` flag, which all three official `live-gate-*` commands in `runs/commands.json` do. Keeping it visible per protocol.
3. Minor observational note: the producer emits `argv` with the raw model arg while `model.path` holds the realpath — consistent and internally checked; no action needed.

## Limitations
- Insertions were tested on the gate's own synthetic v3 receipt and on one genuine committed receipt (`receipt-1.json`, also rejected, exit 1, exact fired) — plus one genuine fresh live run for the relative-arg direction. Did not exhaustively test arbitrary payloads (e.g. flag-order shuffles of existing pairs) beyond the five assigned.
- Live run used loopback 127.0.0.1 only, port auto-picked, child torn down by the tool; verified no seat-owned listener remains (`ss -ltnp | grep 41379` → no output; no `llama-server` processes). Pre-existing unrelated listeners (other seats) observed and untouched.

## Cleanup
Scratch at `/tmp/kama-r18-falsify-GateArgv` — cases, rel-live receipt, mutate.py, relative.sh — to be removed before finish; report is the only copy-out (this file). Production tree untouched.

## Report appendix — experiment source (mutate.py)
```python
#!/usr/bin/env python3
"""Gate argv-insertion attack harness (seat GateArgv, clone-only)."""
import copy, importlib.util, json, os, subprocess, sys

REPO = '/tmp/kama-r18-falsify-GateArgv/repo'
GATE = os.path.join(REPO, 'tests/llamacpp-live/check-receipt.py')
CASES = '/tmp/kama-r18-falsify-GateArgv/cases'
os.makedirs(CASES, exist_ok=True)

spec = importlib.util.spec_from_file_location('gate', GATE)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

EXPECT = ['--expect-model-sha256', 'a' * 64,
          '--expect-server-sha256', 'b' * 64,
          '--expect-probe-sha256', 'c' * 64,
          '--expect-tool-sha256', '9' * 64]

EXACT_MSG = 'argv does not exactly match'

PAYLOADS = {
    'api-key':     ['--api-key', 'sk-attack'],
    'dup-host':    ['--host', '0.0.0.0'],
    'dup-port':    ['--port', '45679'],
    'short-alias': ['--alias', 'kama'],
    'dup-ctx':     ['-c', '512'],
}
POSITIONS = {'front@2': 2, 'pre-tail@-2': -2, 'end': None}

rows = []

def run_case(name, receipt, extra=EXPECT):
    path = os.path.join(CASES, name + '.json')
    with open(path, 'w') as fh:
        json.dump(receipt, fh)
    p = subprocess.run([sys.executable, GATE, path, *extra],
                       capture_output=True, text=True)
    out = p.stdout.strip()
    return {'name': name, 'exit': p.returncode, 'stdout': out,
            'stderr': p.stderr.strip()[:200]}

def insert(argv, payload, idx):
    argv = list(argv)
    if idx is None:
        return argv + payload
    argv[idx:idx] = payload
    return argv

print('== A/B: v3 insertion matrix (payload x position) ==')
for pname, payload in PAYLOADS.items():
    for posname, idx in POSITIONS.items():
        r = copy.deepcopy(g._selftest_receipt_v3())
        r['argv'] = insert(r['argv'], payload, idx)
        res = run_case(f'v3-{pname}-{posname}', r)
        problems = [ln.strip()[2:] for ln in res['stdout'].splitlines()
                    if ln.strip().startswith('- ')]
        exact_hits = [p for p in problems if p.startswith(EXACT_MSG)]
        res['n_problems'] = len(problems)
        res['exact_equality_fired'] = bool(exact_hits)
        res['all_problems'] = problems
        rows.append(res)
        print(f"{res['name']:34s} exit={res['exit']} "
              f"problems={res['n_problems']} exact={res['exact_equality_fired']}")

print('== C: raw relative model.arg must stay VALID ==')
rel = copy.deepcopy(g._selftest_receipt_v3())
rel['model']['arg'] = 'models/stories260K.gguf'
rel['argv'][2] = 'models/stories260K.gguf'
res = run_case('v3-relative-arg-valid', rel)
print(f"relative-arg synthetic: exit={res['exit']} (want 0)")

print('== D: v2 legacy hole (expected survive-visible residual) ==')
v2 = copy.deepcopy(g._selftest_receipt_v2())
v2['argv'] = insert(v2['argv'], ['--port', '45679'], -2)
res = run_case('v2-dup-port-no-floor', v2, extra=[])
print(f"v2 insertion, no schema floor: exit={res['exit']} (0=survived)")
res = run_case('v2-dup-port-floor-v3', v2, extra=EXPECT + ['--require-schema', 'v3'])
print(f"v2 insertion, --require-schema v3: exit={res['exit']} (want 1)")

print('== E: genuine committed receipt insertions (receipt-1.json) ==')
with open(os.path.join(REPO, '.ufo/waves/round-18/live/receipt-1.json')) as fh:
    genuine = json.load(fh)
for pname in ('api-key', 'dup-host', 'dup-port'):
    r = copy.deepcopy(genuine)
    r['argv'] = insert(r['argv'], PAYLOADS[pname], -2)
    res = run_case(f'genuine-{pname}-pre-tail@-2', r, extra=EXPECT)
    problems = [ln.strip() for ln in res['stdout'].splitlines()
                if ln.strip().startswith('- ')]
    exact_hits = [p for p in problems if EXACT_MSG in p]
    print(f"genuine-{pname}: exit={res['exit']} exact_fired={bool(exact_hits)}")
```
