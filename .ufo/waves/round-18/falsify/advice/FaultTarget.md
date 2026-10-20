VERDICT: partial — full guard deletion is caught, but a multi-row-only guard loss survives and launders an off-target F9 row.

## Findings (severity order)

### Medium — multi-row attribution loss survives `--selftest` and awards false detection credit

**Evidence / path.** On pinned clone revision `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`, `tests/probe-verdicts/fault-controls.py` SHA-256 was `58dac1f71346734532bddc60a2d20f95f640406e924b1aec00a0b750feed072a`; `tests/probe-verdicts/check.py` SHA-256 was `12367de62efafa02641c4acb497e50f1be5019b54879a9ac6da13efd5f8071a5`. The nine-matrix digest reported by the control is `bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32`.

The delivery's `classify_run` re-derives failed conjuncts and rejects a row unless its target is among them (`tests/probe-verdicts/fault-controls.py:735-752`); the real fault runner uses this classifier (`:914-915`). The selftest classifier creates one fixed row and invokes `classify_run(..., [row], ...)` for every case (`:1137-1195`; especially `:1191`). Thus every off-target negative case is single-row.

**Pristine baseline.** Command from the clone:

```text
python3 tests/probe-verdicts/fault-controls.py --selftest --json
```

Exit `0`; parsed output: `passed=True`, `problems=[]`, `classifier_cases=23`, `faults_checked=18`. This is consistent with the official `runs/fault-controls-selftest.stdout` (same result modulo the two escape-test PIDs); the official `c2-survivors.json` names the same `fault_controls_sha256` above.

**Exact full-drop mutant.** I copied the pinned detector to a scratch file and changed only the target rejection:

```diff
-        if off_target:
+        if False:
```

Command (matrix path explicit because the mutant was in scratch):

```text
python3 scratch/fc-mut-attrib-full.py --selftest --json --matrix-dir "$PWD/tests/probe-verdicts"
```

Exit `1`, `passed=False`, `classifier_cases=23`; the only problems were:

```text
classifier: target-conjunct attribution: reason fault failed on verdict only: got True, want False
classifier: reason fault failed on error only: got True, want False
classifier: route fault failed on reason only: got True, want False
```

So the selftest catches complete removal of the target check. The same full-drop mutant, when given the multi-row off-target F9 witness described below, exited `0`, `detected=1`, `accepted=0`: the selftest red is causally tied to the lost check, rather than to a behaviorally inert edit.

**Fresh survivor (the finding).** A narrower loss preserves the single-row selftest behavior but bypasses attribution for multi-row faults. Exact source mutation:

```diff
-        if off_target:
+        if off_target and len(run_rows) == 1:
```

Command:

```text
python3 scratch/fc-mut-attrib-single.py --selftest --json --matrix-dir "$PWD/tests/probe-verdicts"
```

Exit `0`; output: `passed=True`, `classifier_cases=23`, `problems=[]`.

I then fed F9 a five-row check result whose rows failed **only on verdict**, while F9's declared target is `reason`. The scratch check was copied from the pinned `check.py` and still ran the real probe and row stubs; after grading the `reason-case` wrapper output it restored each emitted `reason` to the matrix expectation, changed `verdict` to an `X`-prefixed value, and kept `drift` consistent with that changed verdict. The check's already-false `passed` value remained false. F0 (`FAULT_MODE=pass`) was unchanged and passed.

Exact injected source (inserted immediately after `records = [grade(entry, probe) for entry in entries]` in the scratch copy):

```python
import os as _os
if _os.environ.get("FAULT_MODE") == "reason-case":
    for _r in records:
        _r["reason"] = _r["expected"]["reason"]
        _r["verdict"] = "X" + str(_r["verdict"])
        _r["drift"] = _r["verdict"] != "MODEL_OK"
```

The source transformation asserted that the anchor occurred exactly once:

```python
from pathlib import Path
src = Path("tests/probe-verdicts/check.py").read_text()
old = '''    try:
        records = [grade(entry, probe) for entry in entries]
    except HarnessError as exc:
        print(f"harness error: {exc}", file=sys.stderr)
        return 2'''
new = '''    try:
        records = [grade(entry, probe) for entry in entries]
        import os as _os
        if _os.environ.get("FAULT_MODE") == "reason-case":
            for _r in records:
                _r["reason"] = _r["expected"]["reason"]
                _r["verdict"] = "X" + str(_r["verdict"])
                _r["drift"] = _r["verdict"] != "MODEL_OK"
    except HarnessError as exc:
        print(f"harness error: {exc}", file=sys.stderr)
        return 2'''
assert src.count(old) == 1
Path("scratch/check-mut-f9-offtarget.py").write_text(src.replace(old, new))
```

Pristine detector command:

```text
python3 tests/probe-verdicts/fault-controls.py --check scratch/check-mut-f9-offtarget.py --only-fault F9 --json
```

Exit `1`; `positive_control.detected=True`, `detected=0`, `accepted=1`; F9 was `detected=False`, with:

```text
rows failed but NOT on the targeted 'reason' conjunct: ['ReadyControls.expect-exact-id', 'ReadyControls.expect-different-id', 'LoadingEnvelope.canonical-alias', 'ForeignControls.openmetrics-text', 'AuthAndDead.closed-port-connection-refused'] (expect-exact-id:verdict expect-different-id:verdict canonical-alias:verdict openmetrics-text:verdict closed-port-connection-refused:verdict)
```

The same F9 command using the multi-row-only mutant as the detector:

```text
python3 scratch/fc-mut-attrib-single.py --check "$PWD/scratch/check-mut-f9-offtarget.py" --probe "$PWD/tools/kama-probe.sh" --matrix-dir "$PWD/tests/probe-verdicts" --only-fault F9 --json
```

Exit `0`; `positive_control.detected=True`, `detected=1`, `accepted=0`; F9 was `detected=True`, and the diagnostic listed `verdict` as the failed conjunct for each of the five rows while claiming the target `reason` had failed. This is a concrete multi-row-only survivor and false detection credit, not a timeout, missing mutation site, or invalid baseline. The matching full-drop detector also accepts this witness (`exit=0`, `detected=1`, `accepted=0`). The missing coverage is a multi-row off-target classifier selftest case (or an equivalent invariant that exercises every row in a multi-row run).

## Exit-2 / own-fault check

The ordinary check-exit-2 classifier case expects `False` (`fault-controls.py:1173`); wrapper exit 9 and a row declaring `probe_exit=9` raise `OwnFault` (`:697-699, :718-720`). `run_suite` catches `OwnFault` and returns code 2 with `doc=None` (`:985-986`), so there is no detection count to consume.

Two F0-passing synthetic check instruments attempted to launder the own-fault:

```text
python3 tests/probe-verdicts/fault-controls.py --check scratch/fake-exit9.as-check.py --only-fault F1 --json
exit=2
stderr: fault-controls: own fault: wrapper fault: check exited 9 (stderr: fault-wrapper error)

python3 tests/probe-verdicts/fault-controls.py --check scratch/fake-exit9-record.as-check.py --only-fault F1 --json
exit=2
stderr: fault-controls: own fault: wrapper fault: probe exited 9 on ['ReadyControls.expect-exact-id', 'ReadyControls.expect-different-id', 'LoadingEnvelope.canonical-alias']; no fault was injected there
```

Both produced no JSON result / no counted faults. A separate detector mutant changed both exit-9 `raise OwnFault(...)` sites to `return True`; `--selftest` exited `1` with exactly `classifier: wrapper died (probe exit 9): got True, want 'own-fault'`. Thus the stated exit-2 own-fault handling held, and its direct laundering mutant was selftest-killed.

## Residual risk and verification gaps

- The actionable finding is bounded to multi-row fault runs: the single-row negative cases do not detect the `len(run_rows) != 1` bypass. The F9 five-row witness demonstrates that exact path; the full detector suite/counter was not rerun with this mutant.
- Attribution is derived from the subject check's emitted record fields (`failed_conjuncts`, `:653-683`), not independently re-graded from raw probe stdout by fault-controls. A subject that fabricates internally consistent failure records is outside the evidence established here.
- The F7 error-target trial shows co-failures are accepted when `error` is among them; no assertion of exclusive attribution is supported by this code or this experiment.
- Only assigned selftests and bounded `--only-fault F9` / `--only-fault F7` experiments were run; no build, lint, formatter, official counter, or full fault suite was run. The F7 command took about 33 seconds. No tool was installed or updated.
- LSP review device is unavailable in this seat: `read xd://lsp` returned `No such tool: xd://lsp`; no LSP status/references/definition/diagnostics were available. Source behavior above is grounded in the pinned-file reads and executed experiments, not text-search output.
- Code identity/restoration: clone HEAD stayed `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`; pristine file hashes matched `git show HEAD:...`. No production source file was edited. The loopback checks used only check.py's ephemeral stubs; final `pgrep` for the clone returned none, `ss` found no listener attributable to this clone and no `8080`/`34113` listener. Other unrelated host listeners were not touched.

## Experiment-source hashes

```text
pristine fault-controls.py  58dac1f71346734532bddc60a2d20f95f640406e924b1aec00a0b750feed072a
pristine check.py            12367de62efafa02641c4acb497e50f1be5019b54879a9ac6da13efd5f8071a5
full-drop detector mutant    7d1d71745b452d2f5b4a117bd6e65597cf60748dd7e231290ab09f584500f1a1
multirow-only mutant         3d938b8877ba2c011d557429155dd356093d577d2bcaeb31d5c9ce8bfc932504
F9 off-target check mutant   a4074f2a77eb3ac96b3c54d608c44270c036539da9fc1ef195446abe01a9a90e
F7 timeout check mutant      37f9f09865f42358fd35a5cb1e162c8ac78569094a12fcd344150155fa2756c6
matrix set                   bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32
```
