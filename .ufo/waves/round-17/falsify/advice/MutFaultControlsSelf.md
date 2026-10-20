VERDICT: partial — The claimed 3→0 accepted-fault count reproduces, but three detector weakenings survive decision comparison; nonzero-only grading changes the frozen arm.

# MutFaultControlsSelf — detector-self mutation probe

Advisory evidence for L1, not a round-admission or integration verdict. Attacked only C1's detector `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/fault-controls.py` at lane commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3`. No check.py, matrix, probe, live harness, gate, fleet state, or sibling source was edited. The only lane write is this Report.

## Named axes and comparison contract

Probe dimensions: **calibration/sensitivity**, **targeted-conjunct attribution**, **row-cache isolation**, **positive-control validity**, and **reproducibility / write-and-port safety**. These are this investigation's dimensions, not additional lane score claims. Independent frozen/current arms and independent mutants ran concurrently within each phase. A leaf seat dispatched no subagents.

The decision detector used the tuple `(process exit, F0 detected, detected count, accepted count, F1…F8 detected booleans)` compared with the pristine arm. The diagnostic comparison additionally compared the entire JSON document after deleting only `seconds`; no findings, reasons, run counts, paths, hashes, or exits were discarded. Selftest output was compared unchanged. A mutation is **killed** here only when the frozen/current decision tuple changes relative to its healthy baseline; diagnostic-only differences are explicitly separated. This comparison is an external observation of outputs, not a claim that a committed meta-test enforces it.

Pristine F0 was healthy on both check.py versions; all selftests passed. Frozen exit 1 is the *expected* accepted-fault result, not an inconclusive baseline failure. All 18 full-suite invocations retained F7, all six F8 variants, the original check-run cap of 150 seconds, and the original probe timeout. The external per-suite cap was 300 seconds; no external timeout fired. Nine selftests also ran, for 27 child invocations total. All detector stderr streams were empty.

## Actual results

`D/A` = detected faults / accepted faults, excluding F0. `T/F` vectors are F1…F8. A shared pristine run is valid for all four byte-identical staged copies; every individual copy was subsequently restored and rerun.

| Bytes | Frozen D/A; suite exit | Current D/A; suite exit | Selftest exit | Decision mutation outcome |
|---|---|---|---|---|
| Pristine | 5/3; 1 | 8/0; 0 | 0 | Healthy baseline |
| (a) No target requirement | 5/3; 1 | 8/0; 0 | 0 | **SURVIVED** both arms; only `why` diagnostics changed |
| (b) Any nonzero = detected | 6/2; 1 | 8/0; 0 | 0 | **KILLED by frozen JSON decision comparison**, not by suite exit or selftest; survives current-only observation |
| (c) F6 shared cache across rows | 5/3; 1 | 8/0; 0 | 0 | **SURVIVED** decision comparison; F6 diagnostics reveal contamination |
| (d) Bypass F0 identity gate | 5/3; 1 | 8/0; 0 | 0 | **SURVIVED**; full JSON also unchanged except `seconds` |
| Restored (a), (b), (c), (d), each | 5/3; 1 | 8/0; 0 | 0 each | Full JSON matches pristine except `seconds`, for every copy |

Frozen pristine / restored / (a)/(c)/(d) vector: `T T T T F F T F`. Frozen (b): `T T T T F F T T`. Current vector: `T T T T T T T T` in every phase. F0 returned check exit 0, `detected: true`, five identity rows passing in every full-suite invocation, including (d), which bypassed enforcement rather than collection.

## Findings, mutations, and actual output evidence

### (a) Target-attribution removal has no decision consequence on either fixed gate

Source: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/fault-controls.py:523-538`, quote: `if target:`. At line 523 the scratch mutation was exactly:

```diff
-    if target:
+    if False and target:
```

This preserves JSON parsing, row presence, per-row `passed: false`, exits, and F0, but bypasses only the targeted-conjunct verification. The intended detector is the frozen/current decision comparison plus the tool's selftest. Both decision tuples and selftest output remain identical to pristine. Current F1's observed `why` loses attribution:

```text
pristine/restored: check exited 1 with JSON; all 3 faulted rows failed the 'reason' conjunct (expect-exact-id:reason expect-different-id:reason canonical-alias:reason)
mutated: check exited 1 with JSON; all 3 faulted rows passed=false
```

Only `why` changes (F1–F4/F7/F8 on frozen, F1–F8 on current); no `detected`, `accepted`, `check_exit`, row set, run count, or F0 changes. **SURVIVED**, with a visible diagnostic weakening rather than an invisible byte-for-byte output. [INFERENCE] These two fixed gate versions do not supply the off-target failing-row counterexample needed to exercise this guard; deleting the guard is not shown harmless.

### (b) Frozen F8 exposes exit-only false detection; current-only and exit-status-only checks do not

Source: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/fault-controls.py:495-507`, quote: `stdout is not parseable`. After line 490 the scratch mutation inserted exactly:

```python
    if not positive:
        return exit_code != 0, f"check exited {exit_code}; any nonzero exit counts"
```

F0's identity classification is retained. Fault-run parsing, complete-row and target checks are bypassed at one classifier entry point. Frozen F8's `check_exit` stays `[1,1,1,1,1,1]`, but `detected` flips `false → true`; detected/accepted changes `5/3 → 6/2`. The frozen suite still exits 1 because F5/F6 remain accepted. Actual frozen diagnostics include:

```text
pristine/restored [row-not-object]: check exited 1 but stdout is not parseable JSON (traceback or human text); stdout[:120]=''
pristine/restored [row-null]: check exited 1 but stdout is not parseable JSON (traceback or human text); stdout[:120]=''
pristine/restored [non-utf8]: check exited 1 but stdout is not parseable JSON (traceback or human text); stdout[:120]=''
mutated [row-not-object]: check exited 1; any nonzero exit counts
mutated [row-null]: check exited 1; any nonzero exit counts
mutated [non-utf8]: check exited 1; any nonzero exit counts
```

Thus the frozen arm's output *does* reveal the weakening, and comparison against the persisted claimed 3-accepted count would catch it. **KILLED by the two-arm JSON decision comparison**; **SURVIVED** both current-only decisions and every selftest. No exit-2 or outer-timeout counterexample was injected; the observed witness is exit-1 with empty/non-JSON stdout, not an inferred exit-2 result.

### (c) Shared F6 cache is visible in diagnostics but not rejected as a bad control

Source: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/fault-controls.py:99-102`, quote: `a shared cache cannot tell rows apart`; implementation at lines 156 and 573–584. The scratch line 156 was replaced exactly:

```diff
-        "runs": _per_row("f6", "/health", F6_ROWS),
+        "runs": [{"mode": "f6", "touch": "/health", "rows": F6_ROWS}],
```

This invokes one four-row prepass using one `FAULT_CACHE`, followed by one four-row replay; it does not alter the wrapper or either check.py. In both arms F6 `runs` changes `4 → 1`. Frozen F6 `check_exit` changes `[0,0,0,0] → 1`, but F6 remains `detected: false` because the observed diagnostic is:

```text
faulted rows still passed: ['ReadyControls.expect-different-id']
```

The current arm remains F6 detected and suite 8/0. Its actual diagnostic is:

```text
check exited 1 with JSON; all 4 faulted rows failed the 'route' conjunct (expect-exact-id:exit,reason,route,verdict expect-different-id:route canonical-alias:reason,route,served_model,verdict openmetrics-text:reason,route,served_model,verdict)
```

Pristine/restored current F6 instead reports only `route` for each of the four separate rows. The mutation therefore introduces off-target exit/reason/verdict/served-model failures in three rows, rather than the advertised isolated route corruption. The remaining matching row keeps the frozen arm from falsely claiming F6 detected; the every-row requirement still helps. **SURVIVED** aggregate/per-fault decisions and selftest, although `runs`, `check_exit`, and `why` expose the weakened fixture. This is not a claim that shared-cache replay is invisible in all output.

### (d) F0 enforcement can be disabled without any normalized output change

Source: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/fault-controls.py:762-767`, quote: `if not positive["detected"]:`. The scratch mutation at line 764 was exactly:

```diff
-            if not positive["detected"]:
+            if False and not positive["detected"]:
```

This interpretation of “skip F0 identity gate” disables the abort/exit-2 gate, retaining F0's diagnostic execution and honest `positive_control` output. It does not fabricate a passing F0, change the fault table, or also mutate check.py. Both available check.py versions pass F0, so the disabled branch is never distinguished. **SURVIVED** every decision, every selftest, and the *entire* JSON comparison after deleting only timing. [INFERENCE] A check.py whose identity arm fails is the missing discriminator; no such third check.py variant was run in this assigned four-mutation probe.

### All four detector weakenings survive the tool's own selftest

Source: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/fault-controls.py:635-637`, quote: `without invoking check.py`; table-validation implementation at lines 656–707. The pristine, four mutant, and four restored selftests all produced exactly the same JSON and exit 0. Actual output:

```json
{"selftest":"kama-fault-controls/selftest-v1","matrix_files":9,"matrix_tests":72,"matrix_sha256":"bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32","rows_checked":5,"families_covered":["DEAD","FOREIGN_SERVICE","MODEL_LOADING","MODEL_MISMATCH","MODEL_OK"],"problems":[],"passed":true}
```

This is bounded evidence about detector meta-coverage, not a refutation of the baseline numbers. The lesson's stated frozen/current counts (`/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17.md:156-165`) and scorecard (`/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md:680`) reproduce. The present fixed input pair is insensitive to three decision-level detector weakenings; adding every diagnostic byte to the observation still leaves (d) undistinguished.

## Source and restoration hashes

SHA-256; original detector hash is the before and restored hash for **each** scratch copy. Reversing the exact edits restored all four byte-for-byte before their final reruns.

| Artifact | Before / restored SHA-256 | Mutated SHA-256 |
|---|---|---|
| detector (a) | `d3eaadeb8a061b4e322868d569df77afbd7331089d06b06c86a2063fdc31b312` | `3bd9d084a7488ea8df58e7f001d4994f6380ec12ab779442ea1bead1f0198b35` |
| detector (b) | `d3eaadeb8a061b4e322868d569df77afbd7331089d06b06c86a2063fdc31b312` | `28a2d64eda9305675999f670790ead89d1e903f8b061bec5653076e1543694f2` |
| detector (c) | `d3eaadeb8a061b4e322868d569df77afbd7331089d06b06c86a2063fdc31b312` | `e20eb8c4caf0e82a3bf7d560907cdffbe038f81d7f924d86f7527448711b9c35` |
| detector (d) | `d3eaadeb8a061b4e322868d569df77afbd7331089d06b06c86a2063fdc31b312` | `636c419f7791da234cf37f1e15ef7fa859c56dc2c75f1c13714e8605635861be` |
| frozen check.py (unchanged) | `b853576edd54e006c4d8742c1a7335a0d6cca475d107acce7792da75b6145762` | not mutated |
| current check.py (unchanged) | `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099` | not mutated |
| real probe (unchanged) | `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3` | not mutated |

All 27 outputs report the pinned matrix digest `bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32`, nine files / 72 rows. All twelve restored outputs (eight suites, four selftests) match pristine JSON with only `seconds` removed. Canonicalization was `json.dumps({k:v for k,v in doc.items() if k != "seconds"}, sort_keys=True, separators=(",", ":")).encode()` followed by SHA-256. Baseline, mutant (d), and every restored copy share these normalized output hashes:

| Arm | Normalized output SHA-256 |
|---|---|
| frozen | `37698b2d8367910a219b43f58678d0e42649d675db8f653eb48ab937d1e766ea` |
| current | `517a9d49c024719cfbf912a28aa53af28fdad6133e06d601b7f081d6ff202cd5` |
| selftest | `f39831d05e6a41e7245b523ea7fb3ff746bd56ed37a641f292805d661a301abf` |

## Exact commands and exit codes

All executed lane-tool invocations used the isolated clone as cwd, never the lane directory. Clone/setup commands (exit 0 each):

```sh
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17-MutFaultControlsSelf-clone && git -C /tmp/KamaR17-MutFaultControlsSelf-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3
mkdir -p /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors /tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs /tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard /tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp && cp /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts/fault-controls.py /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/a.py && cp /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts/fault-controls.py /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/b.py && cp /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts/fault-controls.py /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/c.py && cp /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts/fault-controls.py /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/d.py
python3 --version && sha256sum /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts/fault-controls.py /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts/check.py /tmp/KamaR17-MutFaultControlsSelf-clone/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py /tmp/KamaR17-MutFaultControlsSelf-clone/tools/kama-probe.sh
sha256sum /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/a.py /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/b.py /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/c.py /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/d.py /tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard/sitecustomize.py /tmp/KamaR17-MutFaultControlsSelf-clone/seat/run-detectors.py
sha256sum /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/a.py /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/b.py /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/c.py /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/d.py /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts/check.py /tmp/KamaR17-MutFaultControlsSelf-clone/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py /tmp/KamaR17-MutFaultControlsSelf-clone/tools/kama-probe.sh
```

The fourth command recorded mutant hashes; the fifth recorded restored hashes. The Python version output was `Python 3.14.8`. Guard SHA-256: `01a208a1305283a5e2cea807865935fe5ab967b6ef15f3f913ff8efec7d769df`; runner SHA-256: `10fca3be1136dc40bd7e0608b8235b89b0dd088adbb2fe8fe646703cf51081a3`. New scaffolding was written with the write tool; mutations and reversals used surgical edit, not a source-edit script.

Phase-driver commands (exit 0 each):

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/run-detectors.py pristine
env PYTHONDONTWRITEBYTECODE=1 python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/run-detectors.py mutated
env PYTHONDONTWRITEBYTECODE=1 python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/run-detectors.py restored
```

The first attempt to launch `pristine` with the bash tool's async option was refused with `Background job limit reached (100)` before command execution; the synchronous attempt above executed once. The output-comparison Eval cell exceeded its 30-second tool deadline while returning its computed comparison; its state/output remained intact and the subsequent socket-attribution cell completed. Neither event is a detector failure or a mutant kill.

Exact child commands follow. `exit` is the actual detector process status, not the phase driver's status. Every `timeout` was false. Raw stdout SHA-256 is recorded beside each command; raw stderr was empty throughout.

### pristine-original-frozen — exit 1

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/pristine-original-frozen.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts/fault-controls.py --check /tmp/KamaR17-MutFaultControlsSelf-clone/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py --probe /tmp/KamaR17-MutFaultControlsSelf-clone/tools/kama-probe.sh --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts --json
```

stdout SHA-256: `65bb011ae8405351f356d0ff2a348675d8f48549a095949ee1ad3c85a9a99527`.

### pristine-original-current — exit 0

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/pristine-original-current.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts/fault-controls.py --check /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts/check.py --probe /tmp/KamaR17-MutFaultControlsSelf-clone/tools/kama-probe.sh --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts --json
```

stdout SHA-256: `3da9f839ecba289dbeb3575684a8c5ba682b12851dd242507229e14aa925171b`.

### pristine-original-selftest — exit 0

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/pristine-original-selftest.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts/fault-controls.py --selftest --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts
```

stdout SHA-256: `f1291120839dbea009b450e460bbe9df7e49ba1f54d2af343fd15a14fec4cabe`.

### mutated-a-frozen — exit 1

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/mutated-a-frozen.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/a.py --check /tmp/KamaR17-MutFaultControlsSelf-clone/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py --probe /tmp/KamaR17-MutFaultControlsSelf-clone/tools/kama-probe.sh --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts --json
```

stdout SHA-256: `a9c8f5099d4635211bb9a5b8ce8dd27728c0115b7052e2ea2b6645b42399d4b7`.

### mutated-a-current — exit 0

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/mutated-a-current.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/a.py --check /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts/check.py --probe /tmp/KamaR17-MutFaultControlsSelf-clone/tools/kama-probe.sh --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts --json
```

stdout SHA-256: `307f6513b922a84dc937c4ec4d49413c85a6fa24f077cf9469b107be6463951e`.

### mutated-a-selftest — exit 0

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/mutated-a-selftest.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/a.py --selftest --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts
```

stdout SHA-256: `f1291120839dbea009b450e460bbe9df7e49ba1f54d2af343fd15a14fec4cabe`.

### mutated-b-frozen — exit 1

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/mutated-b-frozen.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/b.py --check /tmp/KamaR17-MutFaultControlsSelf-clone/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py --probe /tmp/KamaR17-MutFaultControlsSelf-clone/tools/kama-probe.sh --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts --json
```

stdout SHA-256: `20e8ab358ead019fef7e1a677ba2de8bbd9671a4445ffde799ec25f97edd52fc`.

### mutated-b-current — exit 0

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/mutated-b-current.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/b.py --check /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts/check.py --probe /tmp/KamaR17-MutFaultControlsSelf-clone/tools/kama-probe.sh --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts --json
```

stdout SHA-256: `cd3cf4309359192aa86bcadda57783a90055978592656d85c3ee010da05bac67`.

### mutated-b-selftest — exit 0

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/mutated-b-selftest.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/b.py --selftest --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts
```

stdout SHA-256: `f1291120839dbea009b450e460bbe9df7e49ba1f54d2af343fd15a14fec4cabe`.

### mutated-c-frozen — exit 1

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/mutated-c-frozen.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/c.py --check /tmp/KamaR17-MutFaultControlsSelf-clone/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py --probe /tmp/KamaR17-MutFaultControlsSelf-clone/tools/kama-probe.sh --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts --json
```

stdout SHA-256: `888fd3d1bba6b5548c45c767cf654f628a6b164393382625a5f0244deb56f047`.

### mutated-c-current — exit 0

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/mutated-c-current.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/c.py --check /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts/check.py --probe /tmp/KamaR17-MutFaultControlsSelf-clone/tools/kama-probe.sh --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts --json
```

stdout SHA-256: `fe115b6194651ed4a223825a51c59a7e1d9db4ce51f20e56c1bc5863b86e7202`.

### mutated-c-selftest — exit 0

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/mutated-c-selftest.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/c.py --selftest --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts
```

stdout SHA-256: `f1291120839dbea009b450e460bbe9df7e49ba1f54d2af343fd15a14fec4cabe`.

### mutated-d-frozen — exit 1

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/mutated-d-frozen.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/d.py --check /tmp/KamaR17-MutFaultControlsSelf-clone/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py --probe /tmp/KamaR17-MutFaultControlsSelf-clone/tools/kama-probe.sh --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts --json
```

stdout SHA-256: `e86b66f904a78c4afd92d0d04efc0ddfb7ad84ba9f6ee50c5611301e6b2a4233`.

### mutated-d-current — exit 0

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/mutated-d-current.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/d.py --check /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts/check.py --probe /tmp/KamaR17-MutFaultControlsSelf-clone/tools/kama-probe.sh --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts --json
```

stdout SHA-256: `6b3618192cd89749609642d52590901f394712003a48b486fe88bb0a59c9630f`.

### mutated-d-selftest — exit 0

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/mutated-d-selftest.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/d.py --selftest --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts
```

stdout SHA-256: `f1291120839dbea009b450e460bbe9df7e49ba1f54d2af343fd15a14fec4cabe`.

### restored-a-frozen — exit 1

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/restored-a-frozen.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/a.py --check /tmp/KamaR17-MutFaultControlsSelf-clone/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py --probe /tmp/KamaR17-MutFaultControlsSelf-clone/tools/kama-probe.sh --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts --json
```

stdout SHA-256: `650624840feaa1759202d68b8be1116b052b01c06997b2c67b4ebc8f2c050894`.

### restored-a-current — exit 0

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/restored-a-current.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/a.py --check /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts/check.py --probe /tmp/KamaR17-MutFaultControlsSelf-clone/tools/kama-probe.sh --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts --json
```

stdout SHA-256: `e4c512b4a4a8aa4ac8559e213b5f484daa594ed608411d6af485d82e1abaf7bf`.

### restored-a-selftest — exit 0

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/restored-a-selftest.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/a.py --selftest --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts
```

stdout SHA-256: `f1291120839dbea009b450e460bbe9df7e49ba1f54d2af343fd15a14fec4cabe`.

### restored-b-frozen — exit 1

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/restored-b-frozen.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/b.py --check /tmp/KamaR17-MutFaultControlsSelf-clone/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py --probe /tmp/KamaR17-MutFaultControlsSelf-clone/tools/kama-probe.sh --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts --json
```

stdout SHA-256: `650624840feaa1759202d68b8be1116b052b01c06997b2c67b4ebc8f2c050894`.

### restored-b-current — exit 0

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/restored-b-current.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/b.py --check /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts/check.py --probe /tmp/KamaR17-MutFaultControlsSelf-clone/tools/kama-probe.sh --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts --json
```

stdout SHA-256: `cc28a51ad67c60d1d912e638eaa179bedd351e6f78ed18c64ede66563b1bf3ed`.

### restored-b-selftest — exit 0

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/restored-b-selftest.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/b.py --selftest --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts
```

stdout SHA-256: `f1291120839dbea009b450e460bbe9df7e49ba1f54d2af343fd15a14fec4cabe`.

### restored-c-frozen — exit 1

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/restored-c-frozen.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/c.py --check /tmp/KamaR17-MutFaultControlsSelf-clone/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py --probe /tmp/KamaR17-MutFaultControlsSelf-clone/tools/kama-probe.sh --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts --json
```

stdout SHA-256: `650624840feaa1759202d68b8be1116b052b01c06997b2c67b4ebc8f2c050894`.

### restored-c-current — exit 0

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/restored-c-current.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/c.py --check /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts/check.py --probe /tmp/KamaR17-MutFaultControlsSelf-clone/tools/kama-probe.sh --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts --json
```

stdout SHA-256: `e4c512b4a4a8aa4ac8559e213b5f484daa594ed608411d6af485d82e1abaf7bf`.

### restored-c-selftest — exit 0

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/restored-c-selftest.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/c.py --selftest --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts
```

stdout SHA-256: `f1291120839dbea009b450e460bbe9df7e49ba1f54d2af343fd15a14fec4cabe`.

### restored-d-frozen — exit 1

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/restored-d-frozen.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/d.py --check /tmp/KamaR17-MutFaultControlsSelf-clone/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py --probe /tmp/KamaR17-MutFaultControlsSelf-clone/tools/kama-probe.sh --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts --json
```

stdout SHA-256: `650624840feaa1759202d68b8be1116b052b01c06997b2c67b4ebc8f2c050894`.

### restored-d-current — exit 0

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/restored-d-current.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/d.py --check /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts/check.py --probe /tmp/KamaR17-MutFaultControlsSelf-clone/tools/kama-probe.sh --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts --json
```

stdout SHA-256: `e4c512b4a4a8aa4ac8559e213b5f484daa594ed608411d6af485d82e1abaf7bf`.

### restored-d-selftest — exit 0

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard TMPDIR=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp KAMA_MUT_BIND_LOG=/tmp/KamaR17-MutFaultControlsSelf-clone/seat/runs/restored-d-selftest.binds python3 /tmp/KamaR17-MutFaultControlsSelf-clone/seat/detectors/d.py --selftest --matrix-dir /tmp/KamaR17-MutFaultControlsSelf-clone/tests/probe-verdicts
```

stdout SHA-256: `f1291120839dbea009b450e460bbe9df7e49ba1f54d2af343fd15a14fec4cabe`.

## Reproduction scaffolding and safety

The only runtime-safety instrumentation, identical in every phase, was a `sitecustomize.py` socket-bind guard loaded through `PYTHONPATH`. It maps loopback port-zero fixture allocation to random available ports in `[49152,61000)`, refuses explicit 8080/34113, and records successful fixture bind PID/port pairs. This avoids even transient binding of reserved consumer ports without modifying frozen/current check.py bytes or any HTTP/grade logic. No source/registry/config port was contacted. No llama-server, model runtime, service restart, tool install, or tool upgrade occurred.

Safety log totals: **954 successful fixture allocations**, **914 distinct ports**, range **49152–60957**, forbidden-port intersection **[]**; 366 distinct fixture-owning PIDs. `TMPDIR` kept the detector's own temporary directories under `/tmp/KamaR17-MutFaultControlsSelf-clone/seat/tmp`.

`ss -ltnp` was executed before probes and twice after them (exit 0 each). The final capture was compared against every recorded fixture-owning PID: `owned_listener_lines: []`. Other concurrent seats' listeners were not treated as this seat's residue and were not touched. The final capture had no seat-owned listening socket. No process was killed outside the bounded probe runner's ownership.

Guard file `/tmp/KamaR17-MutFaultControlsSelf-clone/seat/guard/sitecustomize.py` (complete source, reproduced here because scratch is removed):

```python
"""Seat safety only: keep port-zero fixture binds away from reserved ports."""
import errno
import os
import random
import socket

_original_bind = socket.socket.bind
_rng = random.SystemRandom()


def _seat_bind(sock, address):
    if isinstance(address, tuple) and address[0] == "127.0.0.1":
        if address[1] in {8080, 34113}:
            raise OSError(errno.EACCES, "seat-reserved port")
        if address[1] == 0:
            for _ in range(256):
                selected = _rng.randrange(49152, 61000)
                try:
                    result = _original_bind(sock, (address[0], selected))
                except OSError as exc:
                    if exc.errno == errno.EADDRINUSE:
                        continue
                    raise
                path = os.environ.get("KAMA_MUT_BIND_LOG")
                if path:
                    fd = os.open(path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
                    try:
                        os.write(fd, f"{os.getpid()} {selected}\n".encode())
                    finally:
                        os.close(fd)
                return result
            raise OSError(errno.EADDRINUSE, "seat allocator exhausted")
    return _original_bind(sock, address)


socket.socket.bind = _seat_bind
```

Runner file `/tmp/KamaR17-MutFaultControlsSelf-clone/seat/run-detectors.py` (complete source):

```python
#!/usr/bin/env python3
"""Run only this seat's detector probes, with saved commands and bounded children."""
import argparse
import asyncio
import hashlib
import json
import os
import shlex
import signal
from pathlib import Path

ROOT = Path('/tmp/KamaR17-MutFaultControlsSelf-clone')
SEAT = ROOT / 'seat'
RUNS = SEAT / 'runs'
CHECKS = {
    'frozen': ROOT / '.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py',
    'current': ROOT / 'tests/probe-verdicts/check.py',
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


async def invoke(phase, name, detector, arm):
    label = f'{phase}-{name}-{arm}'
    bind_log = RUNS / f'{label}.binds'
    command = [
        'env', 'PYTHONDONTWRITEBYTECODE=1',
        f'PYTHONPATH={SEAT / "guard"}', f'TMPDIR={SEAT / "tmp"}',
        f'KAMA_MUT_BIND_LOG={bind_log}', 'python3', str(detector),
    ]
    if arm == 'selftest':
        command += ['--selftest', '--matrix-dir', str(ROOT / 'tests/probe-verdicts')]
    else:
        command += [
            '--check', str(CHECKS[arm]), '--probe', str(ROOT / 'tools/kama-probe.sh'),
            '--matrix-dir', str(ROOT / 'tests/probe-verdicts'), '--json',
        ]
    child = await asyncio.create_subprocess_exec(
        *command, cwd=ROOT, stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE, start_new_session=True,
    )
    timed_out = False
    try:
        stdout, stderr = await asyncio.wait_for(child.communicate(), timeout=300)
    except asyncio.TimeoutError:
        timed_out = True
        os.killpg(child.pid, signal.SIGKILL)
        stdout, stderr = await child.communicate()
    (RUNS / f'{label}.stdout').write_bytes(stdout)
    (RUNS / f'{label}.stderr').write_bytes(stderr)
    try:
        output = json.loads(stdout)
    except (ValueError, UnicodeError):
        output = None
    allocations = []
    if bind_log.exists():
        allocations = [tuple(map(int, row.split())) for row in bind_log.read_text().splitlines()]
    result = {
        'label': label, 'command': shlex.join(command), 'cwd': str(ROOT),
        'exit': child.returncode, 'timeout': timed_out,
        'detector_sha256': digest(detector.read_bytes()),
        'stdout_sha256': digest(stdout), 'stderr_sha256': digest(stderr),
        'stderr': stderr.decode('utf-8', errors='replace'), 'output': output,
        'bind_count': len(allocations),
        'bind_ports': sorted({port for _, port in allocations}),
        'bind_pids': sorted({pid for pid, _ in allocations}),
    }
    if output is not None and arm != 'selftest':
        result['decision'] = {
            'exit': child.returncode,
            'F0': output.get('positive_control', {}).get('detected'),
            'detected': output.get('detected'), 'accepted': output.get('accepted'),
            'faults': {row['id']: row['detected'] for row in output.get('faults', [])},
        }
    print(json.dumps({k: result[k] for k in ('label', 'exit', 'timeout', 'bind_count')}), flush=True)
    return result


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['pristine', 'mutated', 'restored'])
    args = parser.parse_args()
    detectors = {'original': ROOT / 'tests/probe-verdicts/fault-controls.py'} if args.phase == 'pristine' else {
        name: SEAT / 'detectors' / f'{name}.py' for name in 'abcd'
    }
    results = await asyncio.gather(*(
        invoke(args.phase, name, detector, arm)
        for name, detector in detectors.items()
        for arm in ('frozen', 'current', 'selftest')
    ))
    (RUNS / f'{args.phase}.json').write_text(json.dumps(results, indent=2) + '\n')
    return 0 if all(not row['timeout'] and row['output'] is not None for row in results) else 2


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
```

## Limitations and scope

- These are detector-self mutations, not additional check.py mutants, a new runtime exercise, or a re-run of the separate ten-mutant grid.
- (d) bypasses F0's **enforcement gate** while retaining its diagnostic invocation. Complete omission of F0 collection was not the tested mutation.
- A positive F0 on both fixed check.py inputs cannot distinguish disabled F0 enforcement. Off-target failure records, failing-identity check.py variants, exit 2 and outer-timeout behavior were not separately injected.
- (a)/(c) are surviving **decision-level** mutants; their diagnostic differences are retained above, not hidden. Only (d) is also normalized-output-invisible. (b)'s frozen-arm distinction relies on JSON decisions, since top-level exit status does not change.
- All four mutants survive the existing selftest; that observation does not itself decide whether C1's bounded repair is admissible. L1 owns disposition. No integration, shipping, score change, or contract change was performed.
- Privacy exclusions were respected; no recursive search, prohibited session/config/credential store, jj command, or lane git write was used. Reads of the operator rules and relevant skill/protocol instructions were read-only.
- **Installs / updates: none.** Existing Python 3.14.8, git, bash, curl/probe dependencies, coreutils, and ss were reused; no pacman transaction was attempted.

## Cleanup and restoration evidence

The source/hash and restored-output evidence above was captured before removal. The only durable artifact is this Report. Cleanup completed after the full restored reruns and socket-attribution check, before this Report was written.

```sh
rm -rf -- /tmp/KamaR17-MutFaultControlsSelf-clone && test ! -e /tmp/KamaR17-MutFaultControlsSelf-clone && printf 'scratch_removed=/tmp/KamaR17-MutFaultControlsSelf-clone\n'
```

Observed exit **0**, output:

```text
scratch_removed=/tmp/KamaR17-MutFaultControlsSelf-clone
```

All four modified detectors had their exact original bytes restored before this deletion; all four restored suites on both gates and all four restored selftests completed first. Scratch sources, raw logs, guard, and runner were removed together. This Report retains the actual result excerpts, all 27 exact child commands and stdout digests, reconstruction code, before/mutated/restored hashes, and cleanup evidence.
