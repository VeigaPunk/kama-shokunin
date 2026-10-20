VERDICT: confirm — all five frozen mutants survive their selftests and main-run decisions; shared F6 and dropped attribution change diagnostics, not acceptance.

# MutBaselineDetectors — C2 before-evidence

Advisory mutation probe only; L1 owns integration and official measurement. Named axes: **calibration / detector sensitivity**, **operability / honest exit classification**, **fault isolation**, and **reproducibility / exact restoration**. This read-only seat will not change the lane's tracked sources.

## Preregistered additional mutants (not executed)

These four proposals are separate, single-site mutants against the round-18 frozen files, not additions to the five assigned reproduction probes. The expected hardened detections below are [INFERENCE], not observed kills. Each old string is exact, including indentation; each is to be replaced once.

### FC-X1 — accept an own-fault check exit as a detected fault

Source: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_probe-verdicts_fault-controls.py:495-498`; quote: `if exit_code != want_exit:`.

```python
OLD = '    if exit_code != want_exit:\n'
NEW = '    if (positive and exit_code != 0) or (not positive and exit_code == 0):\n'
```

[INFERENCE] A hardened classifier selftest should supply identical well-formed targeted-failure records at exits 1 and 2: exit 1 is detected, exit 2 is not. The mutant accepts exit 2. Positive-control exit 0 handling remains unchanged.

### FC-X2 — aggregate a multi-run fault with any instead of every run

Source: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_probe-verdicts_fault-controls.py:597-605`; quote: `"detected": all(runs_detected),`.

```python
OLD = '        "detected": all(runs_detected),\n'
NEW = '        "detected": any(runs_detected),\n'
```

[INFERENCE] A hardened selftest should exercise `run_fault` with two actual classifier results, one detected and one accepted, and require aggregate `detected: false`. The mutant returns true.

### AO-X1 — stop comparing the immutable kind cell

Source: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tools_sources-append-only.py:172`; quote: `immutable_cols = [c for c in header if c not in MUTABLE_CELLS and c != "id"]`.

```python
OLD = '    immutable_cols = [c for c in header if c not in MUTABLE_CELLS and c != "id"]\n'
NEW = '    immutable_cols = [c for c in header if c not in MUTABLE_CELLS and c not in {"id", "kind"}]\n'
```

[INFERENCE] A hardened selftest should change only S001's `kind` from `docs` to `code`, require exit 1, and require the exact violation cell `kind`. The mutant accepts it.

### AO-X2 — silently suppress the added-row inventory

Source: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tools_sources-append-only.py:189-190`; quote: `added = sorted(rid for rid in to_rows if rid not in from_rows)`.

```python
OLD = '    added = sorted(rid for rid in to_rows if rid not in from_rows)\n'
NEW = '    added = []\n'
```

[INFERENCE] A hardened selftest should add only S003, require exit 0, no violations, and exact `added == ["S003"]`. The mutant returns an empty added list. This tests reporting as well as the exit decision; the tool explicitly promises added-row reporting at frozen `tools_sources-append-only.py:17` (quote: `allowed and reported as added`).

## Reproduction contract and assigned mutations

Only the five named frozen-byte mutants are executed. The **primary detector is each tool's own `--selftest`**: healthy baseline and restored runs must exit 0; a selftest rejects the mutant only if the mutant no longer passes that same detector. Main runs are additional, separately reported evidence. For `fault-controls`, compare the decision tuple `(exit, F0 detected, detected count, accepted count, F1…F8 detected vector)`; also compare the entire JSON after deleting only top-level `seconds`. Diagnostic-only changes are not silently called unchanged. A strict full-output comparator and a decision comparator are different detectors, explicitly distinguished below.

Every physical scratch copy receives its own pristine, mutant, and restored invocations. The frozen gate under test is round-18's `tests_probe-verdicts_check.py`, not round-17's older round-16 gate. No `--skip-slow` or `--only-fault` narrowing is used; F7 and all six F8 variants remain. `CHECK_RUN_TIMEOUT=150`, `HANG_SECONDS=40`, and the gate's probe timeout remain untouched (source: frozen `tests_probe-verdicts_fault-controls.py:67-69`; quote: `CHECK_RUN_TIMEOUT = 150`).

Guard main runs use the known-bad S041 pair (`b8e485c` → `ccc4bb3`, expected exit 1) and the complete pre-round range (`cff9e62f05aa7cfb9059444f62eb787100719713` → `e75cf680b53484a61709ee1b2787d8dbc6419f74`, expected exit 0). Expected S041 rejection is a healthy baseline, not an inconclusive failing detector.

Historical reproduction sources: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/falsify/advice/MutFaultControlsSelf.md:34-39,74-79,97-104` (quote: `Both available check.py versions pass F0`); `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/falsify/advice/MutAppendOnlyGuard.md:27-38,54-55` (quote: `M3a survives the selftest and both real pairs`). Outside routing: `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17-verifier-spotcheck.md:249-254` (quote: `detectors of detectors and provenance`); retained debt: `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17.md:250-267` (quote: `Kept as debt`).

Exact substitutions (one occurrence each; no edits to frozen files):

### FC-F0 — bypass positive-control enforcement

Site: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_probe-verdicts_fault-controls.py:764-767`; quote: `if not positive["detected"]:`.

```python
OLD = '            if not positive["detected"]:\n'
NEW = '            if False and not positive["detected"]:\n'
```

Scratch subject: `/tmp/kama-r18-MutBaselineDetectors/seat/fc-f0.py`. F0 still runs and reports honestly; only abort-on-unhealthy-F0 enforcement is disabled.

### FC-F6 — share one cached output across four distinct rows

Site: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_probe-verdicts_fault-controls.py:99-102,156`; quote: `a shared cache cannot tell rows apart`.

```python
OLD = '        "runs": _per_row("f6", "/health", F6_ROWS),\n'
NEW = '        "runs": [{"mode": "f6", "touch": "/health", "rows": F6_ROWS}],\n'
```

Scratch subject: `/tmp/kama-r18-MutBaselineDetectors/seat/fc-f6.py`.

### FC-TARGET — remove the targeted-conjunct requirement

Site: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_probe-verdicts_fault-controls.py:523-538`; quote: `if target:`.

```python
OLD = '    if target:\n'
NEW = '    if False and target:\n'
```

Scratch subject: `/tmp/kama-r18-MutBaselineDetectors/seat/fc-target.py`.

### AO-OPENED — omit opened from immutable comparison

Site: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tools_sources-append-only.py:172`; quote: `immutable_cols = [c for c in header if c not in MUTABLE_CELLS and c != "id"]`.

```python
OLD = '    immutable_cols = [c for c in header if c not in MUTABLE_CELLS and c != "id"]\n'
NEW = '    immutable_cols = [c for c in header[:8] if c not in MUTABLE_CELLS and c != "id"]\n'
```

Scratch subject: `/tmp/kama-r18-MutBaselineDetectors/seat/guard-opened.py`. Slicing the header, not the seven-element immutable list, drops `opened`; slicing that shorter list at 8 would be a null mutant.

### AO-BLANK — stop after the first post-header blank line

Site: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tools_sources-append-only.py:116-121`; quote: `line = lines[idx]`.

```python
OLD = '        line = lines[idx]\n'
NEW = '        line = lines[idx]\n        if header is not None and not line.strip():\n            break\n'
```

Scratch subject: `/tmp/kama-r18-MutBaselineDetectors/seat/guard-blank.py`. This reproduces the prior report's surviving M4b, not M4a: the blank immediately after `## Registry` must still be skipped before the header exists.

## Results

**Completed:** 36 bounded child invocations: 15 selftests, nine complete fault-control suites, and 12 guard history comparisons. Every physical mutant has a healthy pristine run and an exact-byte-restored rerun. No outer timeout fired; every child stderr stream was empty. These are scratch-only advice, not L1's official measurements.

### Verdict table

Exit triples below are **pristine / mutated / restored**. Every FC suite retained F0 healthy, `detected=8`, `accepted=0`, and the F1…F8 detected vector `T T T T T T T T`.

| Mutant | Selftest exits | Main exits | Does main output change beyond timing? | Primary selftest / decision verdict |
|---|---|---|---|---|
| FC-F0 | 0 / 0 / 0 | 0 / 0 / 0 | No; complete JSON matches after removing only `seconds`. | **SURVIVED / SURVIVED** |
| FC-F6 | 0 / 0 / 0 | 0 / 0 / 0 | Yes: F6 `runs`, `check_exit` shape, and `why`; decisions stay unchanged. | **SURVIVED / SURVIVED** |
| FC-TARGET | 0 / 0 / 0 | 0 / 0 / 0 | Yes: every fault's `why` loses conjunct attribution; decisions stay unchanged. | **SURVIVED / SURVIVED** |
| AO-OPENED | 0 / 0 / 0 | S041 1 / 1 / 1; round range 0 / 0 / 0 | No: all selftest and history stdout bytes are identical. | **SURVIVED / SURVIVED** |
| AO-BLANK | 0 / 0 / 0 | S041 1 / 1 / 1; round range 0 / 0 / 0 | No: all selftest and history stdout bytes are identical. | **SURVIVED / SURVIVED** |

**Detector qualification:** a strict full-JSON equality detector excluding only timing **does distinguish / kill FC-F6 and FC-TARGET**. It does not distinguish FC-F0 or either append-only mutant. The five-survivor finding concerns the tools' own passing selftests and main acceptance decisions, not byte-invisibility of every mutant.

### Finding 1 — F0 enforcement is untested by a healthy identity input

At the FC-F0 site cited above (`tests_probe-verdicts_fault-controls.py:764-767`, quote: `if not positive["detected"]:`), bypassing the branch leaves complete normalized output unchanged. Actual pristine/mutated/restored F0 fields:

```json
{"id":"F0","runs":1,"check_exit":0,"detected":true,"why":"check exited 0 with JSON; all 5 rows passed (positive control healthy)"}
```

This selects fields, not the full F0 object. [INFERENCE] The fixed honest gate supplies no unhealthy-F0 witness to exercise the disabled enforcement branch. This does not show enforcement is unnecessary.

### Finding 2 — F6 isolation loss remains a successful suite

At the FC-F6 site cited above (`tests_probe-verdicts_fault-controls.py:99-102,156`, quote: `each row gets its own check invocation`), the mutation coalesces four isolated replays into one replay of shared cached data. Actual F6 fields:

```text
pristine/restored: runs=4; check_exit=[1,1,1,1]; detected=true
mutated:          runs=1; check_exit=1;         detected=true
```

The mutated diagnostic is exactly:

```text
check exited 1 with JSON; all 4 faulted rows failed the 'route' conjunct (expect-exact-id:exit,reason,route,verdict expect-different-id:route canonical-alias:reason,route,served_model,verdict openmetrics-text:reason,route,served_model,verdict)
```

Pristine/restored diagnostics attribute only `route` on each separate row. Shared-cache corruption is **visible**, including off-target failures, but is not rejected by the selftest or suite decision.

### Finding 3 — target attribution disappears without changing detection counts

At the FC-TARGET site cited above (`tests_probe-verdicts_fault-controls.py:523-538`, quote: `if target:`), every `why` changes but no `detected`, row list, run count, or exit changes. Example F1 output:

```text
pristine/restored: check exited 1 with JSON; all 3 faulted rows failed the 'reason' conjunct (expect-exact-id:reason expect-different-id:reason canonical-alias:reason)
mutated:          check exited 1 with JSON; all 3 faulted rows passed=false
```

The selftest is a table validator, not a classifier challenge: frozen `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_probe-verdicts_fault-controls.py:635-637` explicitly says `without invoking check.py`. Actual stdout is byte-identical in all nine FC selftests:

```json
{
  "selftest": "kama-fault-controls/selftest-v1",
  "matrix_files": 9,
  "matrix_tests": 72,
  "matrix_sha256": "bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32",
  "rows_checked": 5,
  "families_covered": [
    "DEAD",
    "FOREIGN_SERVICE",
    "MODEL_LOADING",
    "MODEL_MISMATCH",
    "MODEL_OK"
  ],
  "problems": [],
  "passed": true
}
```

### Findings 4–5 — opened omission and post-header truncation evade all assigned surfaces

The two AO sites and exact edits are cited above. The frozen header places `opened` after the first eight columns: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tools_sources-append-only.py:264-266` (quote: `| status | opened | recheck | used-by |`). Its selftest cases, `:294-377`, do not rewrite `opened` or place a data row after a blank line between data blocks; `_doc` joins rows with a single newline (`:281-282`, quote: `"\n".join(rows)`). Both are genuine mutants, not null edits.

Actual stdout from **each** AO selftest, in all three phases:

```text
ok: identical (want exit 0, got exit 0)
ok: status-only change (want exit 0, got exit 0)
ok: teaches change (want exit 1 ids ['S001'], got exit 1 ids ['S001'])
ok: removed row (want exit 1 ids ['S002'], got exit 1 ids ['S002'])
ok: added row (want exit 0, got exit 0)
ok: reordered rows (want exit 0, got exit 0)
ok: pipe inside backticks (want exit 0, got exit 0)
ok: escaped pipe (want exit 0, got exit 0)
ok: recheck and used-by change (want exit 0, got exit 0)
ok: anchor change (want exit 1 ids ['S001'], got exit 1 ids ['S001'])
ok: malformed row width (want exit 2, got exit 2)
ok: duplicate id (want exit 2, got exit 2)
ok: missing registry (want exit 2, got exit 2)
ok: source change (want exit 1 ids ['S001'], got exit 1 ids ['S001'])
14/14 selftest cases passed
```

All six S041 comparisons return one S041 violation object with **both** `anchor` and `teaches` changes, `added: []`, `ok: false`, exit 1. All six round-range comparisons return exactly:

```json
{
  "from": "cff9e62f05aa7cfb9059444f62eb787100719713",
  "to": "e75cf680b53484a61709ee1b2787d8dbc6419f74",
  "path": "corpus/SOURCES.md",
  "violations": [],
  "added": [
    "S042",
    "S043",
    "S044",
    "S045",
    "S046",
    "S047"
  ],
  "ok": true
}
```

## Commands, bounds, and exits

Setup, all exit 0:

```sh
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-MutBaselineDetectors
git -C /tmp/kama-r18-MutBaselineDetectors switch -q -c seat/MutBaselineDetectors e75cf680b53484a61709ee1b2787d8dbc6419f74
python3 --version
```

Version stdout: `Python 3.14.8`. The five subjects were byte-copied from the two named frozen tools, and the scratch gate/probe from their round-18 frozen copies, using `cp`. Every before-hash matched the supplied frozen manifest. The exact substitutions above were applied surgically, once per physical copy, then reversed before the final phase.

These successful phase commands each exited 0, with cwd `/tmp/kama-r18-MutBaselineDetectors` and a tool deadline of 1,800 seconds:

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 /tmp/kama-r18-MutBaselineDetectors/seat/run-probes.py pristine
env PYTHONDONTWRITEBYTECODE=1 python3 /tmp/kama-r18-MutBaselineDetectors/seat/run-probes.py mutated
env PYTHONDONTWRITEBYTECODE=1 python3 /tmp/kama-r18-MutBaselineDetectors/seat/run-probes.py restored
```

The first attempt to launch `restored` asynchronously was refused before execution with `Background job limit reached (100)`. The synchronous invocation above then executed successfully once. This tool-launch refusal is not a detector failure, baseline failure, or mutant kill.

### Exact child-command expansion

All 36 child argv/env combinations are specified by the table and template below. For each phase `P` in `pristine`, `mutated`, `restored`, every listed `(T, M)` pair ran once. Variables only abbreviate absolute paths; cwd was always `/tmp/kama-r18-MutBaselineDetectors`.

```sh
R=/tmp/kama-r18-MutBaselineDetectors
env PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/tmp/kama-r18-MutBaselineDetectors/seat/guard \
    TMPDIR=/tmp/kama-r18-MutBaselineDetectors/seat/tmp \
    KAMA_MUT_SAFETY_LOG="$R/seat/runs/$P-$T-$M.safety.jsonl" \
    /usr/bin/python3 "$R/seat/$T.py" ARGS
```

| T values | M | Exact ARGS | Outer cap | Exit pristine / mutated / restored |
|---|---|---|---|---|
| `fc-f0`, `fc-f6`, `fc-target` | `selftest` | `--selftest --matrix-dir /tmp/kama-r18-MutBaselineDetectors/tests/probe-verdicts` | 20s | 0 / 0 / 0 each |
| `fc-f0`, `fc-f6`, `fc-target` | `main` | `--check /tmp/kama-r18-MutBaselineDetectors/seat/check.py --probe /tmp/kama-r18-MutBaselineDetectors/seat/kama-probe.sh --matrix-dir /tmp/kama-r18-MutBaselineDetectors/tests/probe-verdicts --json` | 300s | 0 / 0 / 0 each |
| `guard-opened`, `guard-blank` | `selftest` | `--selftest` | 20s | 0 / 0 / 0 each |
| `guard-opened`, `guard-blank` | `s041` | `--repo /tmp/kama-r18-MutBaselineDetectors --from b8e485c --to ccc4bb3 --json` | 20s | 1 / 1 / 1 each |
| `guard-opened`, `guard-blank` | `round17` | `--repo /tmp/kama-r18-MutBaselineDetectors --from cff9e62f05aa7cfb9059444f62eb787100719713 --to e75cf680b53484a61709ee1b2787d8dbc6419f74 --json` | 20s | 0 / 0 / 0 each |

The driver used `Popen(..., start_new_session=True)`, captured stdout/stderr, and `communicate(timeout=cap)`. FC suites were sequential (at most one fake server at a time); the independent no-network AO streams ran concurrently. After every child it attempted SIGKILL only on groups attributed to that invocation through its startup log. All `cleaned_process_groups` lists were empty: none remained to kill. Every phase ended with `ss -ltnp` (exit 0), matching listener PIDs against its own logged PIDs; every `owned_listeners` list was empty.

These output comparisons each exited 1. FC-F0 differed only in `seconds`; FC-F6 in `seconds` plus F6's three fields above; FC-TARGET in `seconds` plus all eight faults' `why` strings:

```sh
diff -u /tmp/kama-r18-MutBaselineDetectors/seat/runs/pristine-fc-f0-main.stdout /tmp/kama-r18-MutBaselineDetectors/seat/runs/mutated-fc-f0-main.stdout
diff -u /tmp/kama-r18-MutBaselineDetectors/seat/runs/pristine-fc-f6-main.stdout /tmp/kama-r18-MutBaselineDetectors/seat/runs/mutated-fc-f6-main.stdout
diff -u /tmp/kama-r18-MutBaselineDetectors/seat/runs/pristine-fc-target-main.stdout /tmp/kama-r18-MutBaselineDetectors/seat/runs/mutated-fc-target-main.stdout
```

## Hash and restoration evidence

Before/restored SHA-256 **FC** = `d3eaadeb8a061b4e322868d569df77afbd7331089d06b06c86a2063fdc31b312`; **AO** = `c477a172cd5ae1512a9f75456da216a7df8cfde1df7c28fd09e60b76054b1e05`.

| Subject | Before hash | Mutated SHA-256 | Restored hash |
|---|---|---|---|
| FC-F0 | FC | `636c419f7791da234cf37f1e15ef7fa859c56dc2c75f1c13714e8605635861be` | FC |
| FC-F6 | FC | `e20eb8c4caf0e82a3bf7d560907cdffbe038f81d7f924d86f7527448711b9c35` | FC |
| FC-TARGET | FC | `3bd9d084a7488ea8df58e7f001d4994f6380ec12ab779442ea1bead1f0198b35` | FC |
| AO-OPENED | AO | `d9153107472fbf92ba7024d4728a0955d2dc47fdc91f2e62d2bf8d310db0000e` | AO |
| AO-BLANK | AO | `00c4bef2dfd4183558b86b1d84f916ea50f843425df6430b65123e81b1c728bd` | AO |

After all restored reruns, five `cmp SCRATCH FROZEN` commands (each subject above against its respective absolute original frozen path) exited 0. A following `sha256sum` printed FC for all three FC files and AO for both AO files. This proves exact restoration, not merely semantic equivalence. The edit tool also returned the original snapshots `2066` for all FC files and `E756` for both AO files after reversal.

Supporting bytes were unchanged across all three phase manifests:

| File | SHA-256 |
|---|---|
| `/tmp/kama-r18-MutBaselineDetectors/seat/check.py` | `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099` |
| `/tmp/kama-r18-MutBaselineDetectors/seat/kama-probe.sh` | `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3` |
| `/tmp/kama-r18-MutBaselineDetectors/seat/guard/sitecustomize.py` | `fabe9e3af7b1d088a890d6f7242a93a766cd11009690a7e5a0f1ad6ac342dbe3` |
| `/tmp/kama-r18-MutBaselineDetectors/seat/run-probes.py` | `03e10a27e490aece1d7c7aa5088b4ffcfaa9ee7380f585c443a0712a36aeab35` |

Normalized full-JSON hashing was exactly `sha256(json.dumps({k:v for k,v in doc.items() if k != "seconds"}, sort_keys=True, separators=(",", ":")).encode())`; no diagnostic, count, field, source hash, path, or exit was removed.

| Main FC output | Normalized SHA-256 |
|---|---|
| Every pristine FC suite; FC-F0 mutant; every restored FC suite | `4927c2104cbbd90b80a0aa24439959f19be82797a0ae633d978118636eb55479` |
| FC-F6 mutant | `2d2b0024c3e40a38a7e82d6d0e3ab2087a404fbf4d24bec702bdebfa5e77b7be` |
| FC-TARGET mutant | `8bfa4aa56bca66317bac6821f7b2b9642717ee68a6777bab809e5f7ee311ed9b` |

Raw stdout hashes; all stderr hashes were empty-byte SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`:

| Output | Pristine SHA-256 | Mutated SHA-256 | Restored SHA-256 |
|---|---|---|---|
| FC-F0 main | `b11bb3cea1608674967e6b17b328573883d9b0603899e931a391d8947db7555d` | `9a1802a90aa9ba325c8b2e278fe0a62b2acb03e31f5c90314ffe5c7d8eafa7fb` | `841a9d3da06ffe610cd19138c3941f32bd4875692577ae0fe916147beca04bc4` |
| FC-F6 main | `4e101b57bb80edf4f7b2b0c8c7a5d5918984052cec765f8a8d491a858fa1c290` | `d182f38e54cab47f795a8d42261d2c34f90ead8afb607ca9216ed336c92b398a` | `07ae6136cf3fc8669f429fd52d04bb12efddc225d27fbe384884c5bf3d49c230` |
| FC-TARGET main | `9a1802a90aa9ba325c8b2e278fe0a62b2acb03e31f5c90314ffe5c7d8eafa7fb` | `8958b93b984484ce865783c2d7d7ceaec0eafb03618cf907d134d2cfce4022a3` | `9a1802a90aa9ba325c8b2e278fe0a62b2acb03e31f5c90314ffe5c7d8eafa7fb` |

The remaining 27 child outputs are byte-identical across each relevant physical copy and phase:

| Output class | Raw stdout SHA-256 |
|---|---|
| All nine FC selftests | `f1291120839dbea009b450e460bbe9df7e49ba1f54d2af343fd15a14fec4cabe` |
| All six AO selftests | `7388661f90b127c0b59e5bbbe46b675a6e1fbd776f3c2f729b4dd5ea283a6448` |
| All six AO S041 comparisons | `2a65c87a4f3bf1c4277f392ee08d7d50071d2857305ec53970a36f97c2f22ffd` |
| All six AO round-range comparisons | `8799478efbf189f015b82b3272ca558d6cdca332d2a50def89613045e6d256d8` |

## Safety, limitations, installs, and cleanup

- The only lane write is this Report. Mutation, staging, logs, temporary harness directories, and scaffolding stay under `/tmp/kama-r18-MutBaselineDetectors`. No tracked lane source, frozen copy, old receipt/lesson, jj state, fleet file, runtime installation, or sibling checkout was modified. No subagent was dispatched.
- Scratch `sitecustomize.py` guarded Python socket binds and attributed process groups. It permitted only `127.0.0.1` / `::1`, rejected ports 8080 and 34113, and substituted an available port in 45200–46199 for requested port 0. Each phase logged 177 binds, all `127.0.0.1`, using only ports 45200 and 45201; forbidden-port lists were empty. Registry bounds: `/home/vgpnk/Projects/shokunin/kama-shokunin/registry/endpoint-consumers.tsv:35-37` (quote: `http://127.0.0.1:34113`); its only other registered port is 8080. `ss -ltnp` found no attributed listener after each phase. No llama-server was launched.
- No hardened/current C2 implementation was executed. The four additional mutants were written before this seat's first pristine detector run and were **not applied or run**. Their proposed hardened kills are [INFERENCE]. No repaired-sensitivity conclusion follows from this before-evidence.
- This reruns the existing selftests and real history surfaces. It does not repeat the old reports' synthetic `opened`-rewrite or second-block-removal witness repos, nor inject a newly failing F0 check. Surviving fixed inputs is a coverage finding, not permission to change the contract or proof a defect is harmless.
- Main acceptance and full output equality are separate. Calling changed F6/target diagnostics invisible would overstate the result; calling continued exit 0 a successful self-rejection would also be false.
- Installs/updates: **none**. No package-manager transaction, download, service restart, or runtime modification occurred. Operator tooling rules were read before execution; the host-wide pacman pause was respected.
- Exact restoration and all restored reruns completed before scratch deletion. Cleanup evidence is appended after deletion below; this Report retains exact mutation strings, commands, actual exits/output excerpts, and subject/output hashes.

### Cleanup completed

After exact restoration, all restored reruns, output comparisons, and phase-end `ss -ltnp` checks, this command ran from `/tmp` and exited 0:

```sh
rm -rf -- /tmp/kama-r18-MutBaselineDetectors && test ! -e /tmp/kama-r18-MutBaselineDetectors && printf 'scratch-absent\n'
```

Actual stdout:

```text
scratch-absent
```

The clone, all five restored scratch subjects, wrapper/driver scaffolding, temporary directories, and raw logs were removed together. No seat-owned server or attributed listener remained at the final completed phase check. This Report is the sole retained seat artifact.
