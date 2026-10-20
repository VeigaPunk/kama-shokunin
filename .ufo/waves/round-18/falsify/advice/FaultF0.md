VERDICT: partial — F0 gate enforcement and reject-everything refusal hold (bypass mutant killed, forged instruments refused), but an empty fault list scores exit 0 vacuously and fault-run records are unanchored against a lying instrument.

Seat KamaR18.FaultF0, leaf falsifier, 2026-10-20. Attack target: `tests/probe-verdicts/fault-controls.py` (sha256 pristine `58dac1f71346734532bddc60a2d20f95f640406e924b1aec00a0b750feed072a`) at lane master `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`, all runs inside `/tmp/kama-r18-falsify-FaultF0` (clone + `forge/` scratch). No installs (stock `python3` only). No writes outside my report and scratch; clone restored byte-exact after each mutant (`git checkout --`, tracked tree clean, pristine selftest re-run green).

# Findings, by severity

## F0-1 HIGH — empty fault list passes vacuously with exit 0 on the main scoring path
`main()` accepts `--only-fault F0` (F0 is in `known`, fault-controls.py:1529) but then filters over `FAULTS` only, so F0 is silently dropped and `faults = []` (fault-controls.py:1535). `run_suite` still runs the F0 identity control, then returns `0 if accepted_n == 0 else 1` (fault-controls.py:1008) — with zero faults, `accepted_n` is 0 and the suite **exits 0**. There is no nonempty-faults guard anywhere in `main()` (fault-controls.py:1523-1578) or `run_suite`; contrast the existing `n_matrix == 0` refusal at fault-controls.py:967-968.

Executed (clone cwd, pristine instrument):
`python3 tests/probe-verdicts/fault-controls.py --check /tmp/kama-r18-falsify-FaultF0/tests/probe-verdicts/check.py --probe /tmp/kama-r18-falsify-FaultF0/tools/kama-probe.sh --matrix-dir /tmp/kama-r18-falsify-FaultF0/tests/probe-verdicts --only-fault F0 --json` → **exit 0**, doc: `"positive_control.detected": true` ("check exited 0 with JSON; all 5 rows passed", real probes, `seconds: 2.3`), **`"faults": []`, `"accepted": 0`**, `"skipped": ["F1"…"F17"]`. A run that evaluates nothing reports success. Same result in 0.0 s with forged instrument G2 (`forge/G2_accept_everything.py` as `--check`, exit 0, `faults: []`).

Impact boundary (honest): the doc shape satisfies `fc_decision`/`classify_a`'s healthy-baseline/survived predicate (exit 0, accepted 0, f0_detected true — `.ufo/waves/round-18/c2/survivors.py:844-858, 884-904`). No official consumer passes an empty fault list today (`survivors.py:1095-1098` main runs have no `--only-fault`), so no official count is wrong; this is a live scoring hazard on the main path, exactly the invariant my item names ("empty … fault list must not pass vacuously"). Fresh wave-2 finding, separate from the named round-17 denominator.

## F0-2 MEDIUM (fresh, separate denominator) — a lying instrument scores a perfect suite; fault-run records are never anchored to wrapper bytes
Forged instrument G3 (`forge/G3_env_liar.py`, source below) never runs the probe: it reads `FAULT_MODE` (set verbatim by `run_env`, fault-controls.py:775-779), claims all rows passed during the F0 identity pass and all rows failed during fault runs. `classify_run`/`failed_conjuncts` grade only check.py's stdout records (fault-controls.py:685-752, 640-682); nothing compares them to the bytes the harness-owned wrapper actually emitted.

Executed: `python3 tests/probe-verdicts/fault-controls.py --check forge/G3_env_liar.py --probe /tmp/.../tools/kama-probe.sh --matrix-dir tests/probe-verdicts --only-fault F1 --json` → **exit 0, detected 1, accepted 0**: F0 "healthy" in `seconds: 0.0` (no probe execution at all), F1 "detected" on fabricated records ("all 3 faulted rows failed the 'reason' conjunct"). A forger gets full detector credit.

Boundary honesty: the named C2 ledger row is only "a reject-everything subject cannot give the detector credit → F0 adversarial check instrument in selftest". G1 (below) confirms exactly that statement; G3 is outside the named universe and must stay a fresh wave-2 survivor, not be folded into the 15-item denominator or read as a C2 refutation. The harness-owned anchors (matrix digest pin, wrapper staging, prepass cache) constrain honest instruments, not subjects that fabricate their own records.

## F0-3 MEDIUM-LOW — empty F0 row list: `run_suite` itself has no zero-row guard; only the selftest's static invariant catches it
Mutant E6 (`"runs": [{"mode": "pass", "touch": None, "rows": []}]` in POSITIVE_CONTROL, mutant sha256 `f8489a8a4fb42bbb1aae7e6a3945a61534872c8b9c4cb680eb61f7055fdf3711`):
- `--selftest --matrix-dir tests/probe-verdicts` → **exit 1**, `passed: false`, three targeted problems: `"fault rows outside the F0 identity run: [all 5 rows]"` (static invariant, fault-controls.py:1077-1078), plus both F0-gate outcome mismatches (each suite attempt died `own fault: fault rows outside…`). Red attributable to the empty-row mutation; pristine restored after (sha256 `58dac1f7…`, clean status).
- But `--only-fault F0` with absolute probe under the mutant → **exit 0**, `"positive_control.detected": true, why: "check exited 0 with JSON; all 0 rows passed (positive control healthy)"` (the zero-rows positive branch, fault-controls.py:729-730), `faults: []`. The `outside` refusal (fault-controls.py:963-965) only fires when faults are nonempty, so with an empty fault list nothing rejects the zero-row F0. Pristine table is nonempty, and survivors.py runs the selftest for family b, so the lane's pipeline is covered — but a direct CLI caller with a corrupted table gets a vacuous exit 0.

## F0-4 LOW — relative `--probe` silently yields suite INVALID with a misleading F0-failure message
`run_env` puts `FAULT_PROBE` verbatim into the wrapper env (fault-controls.py:777) while `run_check` spawns check.py with `cwd=scratch` tempdir (fault-controls.py:558-561); a relative probe path cannot resolve from there. Executed: CLI `--probe tools/kama-probe.sh` (relative) ×6 → **exit 2** every time, `"suite INVALID — positive control F0 failed: check exited 1 (wanted 0)"`; identical conditions with the absolute probe → 7/7 exit 0 / F0 healthy. Diagnostic (T3rel, source below) names the row errors: every row `"stub accepted no requests; probe never reached a listening socket"` / `"malformed probe output: stdout is not JSON … stdout=''"`. Fail-safe direction (code 2, doc None, nothing scored). Officials are unaffected: the default `DEFAULT_PROBE` is absolute (`SELF.resolve()`-based) and survivors.py passes staged absolute paths. Note: my first three INVALID runs (E4, D2) were this single deterministic cause, not load flakiness — the closed-port row passed with genuine `rc=7` evidence in all absolute-probe runs (D1).

## Confirmations — the claimed F0 behavior holds where claimed
- Pristine selftest (E0, and again post-restore E7a): `python3 tests/probe-verdicts/fault-controls.py --selftest --matrix-dir tests/probe-verdicts` → exit 0, `passed: true`, matrix 9 files/72 tests, digest `bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32`, 18 faults, 23 classifier cases, 35 wrapper checks — content-identical to the official `.ufo/waves/round-18/runs/fault-controls-selftest.stdout` (PIDs differ only).
- E1, forged reject-everything G1 as `--check`, `--only-fault F1` → **exit 2**, stderr `fault-controls: suite INVALID — positive control F0 failed: check exited 1 (wanted 0); stdout[:120]='{"records": [{"name": "ReadyControls.expect-exact-id", "passed": false, "error": "forged-reject"}…`. Doc None: a rejecting/bad identity prevents all scoring. Confirms the ledger row "a reject-everything subject cannot give the detector credit".
- E2, forged accept-everything G2 as `--check`, `--only-fault F1` → **exit 1**, `accepted: 1`, F1 `detected: false` ("check exited 0 (wanted 1)"). An accepting forger gets no credit.
- E5, F0-bypass mutant (gate disabled: `if False and not positive["detected"]:`, mutant sha256 `7543540b72b7e7f90bf5991d288c039f58049a1174f4b6872836b38f16d9df59`): selftest → **exit 1** with exactly one problem, `"F0 gate: a reject-everything check.py was not refused before any fault counted: {'code': 0, 'accepted': 0, 'error': None}"` — red attributable to the targeted F0-gate assertion; and the scoring consequence: G1 reject-everything under the mutant → **exit 0, accepted 0** while F0 itself failed (`positive_control.detected: false`). Enforcement removal turns the refused instrument into a perfect score. This independently reproduces the official FC-f0gate self-mutant kill (`.ufo/waves/round-18/runs/c2-survivors.json:2869-2881`: current selftest exit 1, gate reject-everything `code 0`). Green pristine → red mutant → byte-exact restore (`58dac1f7…`, `git status --porcelain` clean for the file) completed for E5 and E6 both.

# Bounds compliance
Clone-only execution at `1c325b2e…`; no official counting command touched the live lane. Ports: only check.py's own transient `ThreadingHTTPServer(("127.0.0.1", 0))` stubs and bind-then-close DEAD ports inside suite runs, one run at a time; slow faults F7/F17 never executed (out of item scope). Teardown proof at finish: `pgrep -af 'fault-controls|wrap\.py|probe-verdicts/check\.py'` shows **no** process under `/tmp/kama-r18-falsify-FaultF0` (all hits are sibling seats' scratch dirs); `ss -ltnp` shows **no** listener owned by any of my processes and none on 8080/34113. No installs or tool changes (nothing beyond stock python3; nothing to record).

# Residual risk and verification gaps
- G3-style liar was tested only against F1; replay-mode faults (F6/F11/F13) were not attacked with it (prepass caching is harness-owned, but the same record-fabrication lie should apply — untested).
- Slow faults F7/F17 unexercised here; their selftest detectors were green in every pristine selftest run.
- F0-1 is demonstrated via CLI; no current official consumer passes an empty fault list, so today it is latent, not an active miscount.
- Shared host with ~40 active sibling seats; all my absolute-probe F0 runs were healthy, so no cross-seat interference was observed in final evidence.

# Experiment sources (exact, executed from clone cwd; scratch removed after this report)
`forge/G1_reject_everything.py`:
```python
import json
import sys

# Falsifier G1: forged check instrument, reject-everything.
# Independent of fault-controls.FAKE_CHECK: parses --only NAME pairs itself,
# marks every requested row failed, always exits 1.
names = []
args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--only" and i + 1 < len(args):
        names.append(args[i + 1])
        i += 2
    else:
        i += 1
print(json.dumps({"records": [{"name": n, "passed": False,
                               "error": "forged-reject"} for n in names]}))
sys.exit(1)
```
`forge/G2_accept_everything.py`:
```python
import json
import sys

# Falsifier G2: forged check instrument, accept-everything.
# Every requested row passes, always exits 0.
names = []
args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--only" and i + 1 < len(args):
        names.append(args[i + 1])
        i += 2
    else:
        i += 1
print(json.dumps({"records": [{"name": n, "passed": True} for n in names]}))
sys.exit(0)
```
`forge/G3_env_liar.py`:
```python
import json
import os
import sys

# Falsifier G3: forged check instrument, env-sniffing liar.
# Never runs the probe. During the F0 identity pass (FAULT_MODE=pass) it
# claims every row passed; during any fault run (FAULT_MODE=<fault mode>) it
# claims every requested row failed, so failed_conjuncts() credits the target
# conjunct. If the suite accepts this, no wrapper-output anchoring binds
# check.py records to the probe bytes.
names = []
args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--only" and i + 1 < len(args):
        names.append(args[i + 1])
        i += 2
    else:
        i += 1
mode = os.environ.get("FAULT_MODE", "pass")
if mode == "pass":
    print(json.dumps({"records": [{"name": n, "passed": True}
                                  for n in names]}))
    sys.exit(0)
print(json.dumps({"records": [{"name": n, "passed": False}
                              for n in names]}))
sys.exit(1)
```
`forge/t3_rel.py` (suite-conditions reproduction with relative probe; `t3_suite_f0.py` is the same body with `probe = (Path.cwd() / "tools" / "kama-probe.sh").resolve()`, and `t3_loop.py` repeats that body six times printing per-iteration results):
```python
import importlib.util
import json
import tempfile
from pathlib import Path

# T3rel: identical to the suite's F0 conditions but with a RELATIVE probe
# path (what the CLI receives when invoked as --probe tools/kama-probe.sh).
spec = importlib.util.spec_from_file_location(
    "fc", "tests/probe-verdicts/fault-controls.py")
fc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fc)
matrix = Path("tests/probe-verdicts").resolve()
with tempfile.TemporaryDirectory(prefix="t3rel-") as tmp:
    n, cache = fc.stage_scratch(tmp, matrix / "check.py", matrix)
    rel_probe = "tools/kama-probe.sh"          # relative, as on the CLI
    env = fc.run_env(fc.POSITIVE_CONTROL, fc.POSITIVE_CONTROL["runs"][0], 0,
                     rel_probe, cache)
    code, out, err = fc.run_check(tmp, fc.ROWS_FULL, env)
    print("check exit:", code)
    print("FAULT_PROBE:", env["FAULT_PROBE"])
    try:
        doc = json.loads(out)
        for r in doc.get("records", []):
            print(r.get("name"), "| passed =", r.get("passed"),
                  "| error =", str(r.get("error"))[:160])
    except Exception as exc:
        print("stdout unparsable:", exc, out[:400])
```
Mutant diffs (applied in the clone, each restored byte-exact afterwards): E5 replaced `if not positive["detected"]:` with `if False and not positive["detected"]:` (fault-controls.py:977); E6 replaced `"rows": ROWS_FULL` with `"rows": []` in `POSITIVE_CONTROL` (fault-controls.py:172).

# Command ledger (clone cwd `/tmp/kama-r18-falsify-FaultF0`, exits as measured)
| id | command (abridged, absolute scratch paths elided as `/tmp/...`) | exit |
|---|---|---|
| E0 | `python3 tests/probe-verdicts/fault-controls.py --selftest --matrix-dir tests/probe-verdicts` | 0 |
| E1 | `--check forge/G1_reject_everything.py --probe /tmp/.../tools/kama-probe.sh --matrix-dir tests/probe-verdicts --only-fault F1 --json` | 2 |
| E2 | `--check forge/G2_accept_everything.py … --only-fault F1 --json` | 1 |
| E3 | `--check forge/G3_env_liar.py … --only-fault F1 --json` | 0 |
| E4/E4r1/E4r2/T3C×3 | `--check tests/probe-verdicts/check.py --probe tools/kama-probe.sh … --only-fault F0 --json` (relative probe) | 2 ×6 |
| E4abs | `--check /tmp/.../tests/probe-verdicts/check.py --probe /tmp/.../tools/kama-probe.sh … --only-fault F0 --json` (absolute) | 0 |
| D3 | `--check forge/G2_accept_everything.py … --only-fault F0 --json` | 0 |
| T1 | `python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --json --only <5 F0 rows>` | 0 |
| T3L | `python3 forge/t3_loop.py` (6 suite-condition F0 iterations, absolute probe) | 0/6 failed |
| E5a | selftest under gate-removal mutant (sha `7543540b…`) | 1 |
| E5b | `--check forge/G1_reject_everything.py … --only-fault F1 --json` under mutant | 0 |
| E6a | selftest under empty-F0-rows mutant (sha `f8489a8a…`) | 1 |
| E6b | `--only-fault F0 --json` (absolute probe) under mutant | 0 |
| E7a | pristine selftest after restores | 0 |
