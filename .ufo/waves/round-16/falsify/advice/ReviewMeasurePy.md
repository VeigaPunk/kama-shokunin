VERDICT: partial — `.ufo/waves/round-16/measure.py`'s frozen pinning and directional set equality are real and genuinely fail-capable, but the counting command returns exit 0 on a one-row matrix and never gates `check.py`'s exit code, so a PASS carries no matrix-breadth evidence.

Item attacked: frozen verification (manifest + git blob), directional set equality, exit codes, and whether the gate can pass vacuously.

## What I ran and what happened

| # | Command (cwd = lane root unless noted) | Exit | Result |
|---|---|---|---|
| 1 | `python3 .ufo/waves/round-16/measure.py` **not run** — prohibited; it rewrites L1 receipts | — | gate exercised by importing the shipped file and replacing only `run_check` (harness below) |
| 2 | `python3 - <<'PY' … importlib load measure.py; m.WAVE=/tmp/…; m.run_check=fake … PY` (fabricated receipts, 10 cases A–J) | 0 | cases A/B/C/G passed; D/E/F/H/I/J failed, each with the named reason |
| 3 | `python3 /tmp/…/matrix1/check.py --probe .ufo/waves/round-16/frozen/kama-probe-before.sh --json` (real check.py + real frozen probe, matrix = one real row `LoadingEnvelope.canonical-alias`) | 1 | `tests 1 passes 0 failures 1 verdict FOREIGN_SERVICE` |
| 4 | `python3 /tmp/…/matrix1/check.py --probe tools/kama-probe.sh --json` (same one-row matrix, current probe) | 0 | `tests 1 passes 1 failures 0 verdict MODEL_LOADING` |
| 5 | gate fed #3 and #4 (`one_row_gate.py`) | **0** | `directional: loading_expectations=1 before_failed=1 changed=1 equal=True` / `result: PASS — … all MODEL_LOADING expectations` |
| 6 | `python3 /tmp/…/matrix/check.py --probe …frozen… --json` (matrix = real `LoadingEnvelope.json` + `LoadingRace.json`, 17 rows, 13 loading) | 1 | `tests 17 passes 4 failures 13` |
| 7 | same 17/13 matrix against `tools/kama-probe.sh` | 0 | `tests 17 passes 17 failures 0` |
| 8 | gate fed #6 and #7 | **0** | `directional: loading_expectations=13 … equal=True` / `result: PASS — before red (13 failures) … 13 verdict change(s)` |
| 9 | `python3 tests/probe-verdicts/check.py --probe …frozen… --json > /tmp/…/full-before.json` | 1 | `tests 72 passes 55 failures 17` |
| 10 | `python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --json > /tmp/…/full-after.json` | 0 | `tests 72 passes 72 failures 0` |
| 11 | row-level diff #9/#10 vs `run-before.json`/`run-after.json` (`passed, verdict, reason, probe_exit` per name) | 0 | `row-level differences: 0 []` for both arms; same names; totals identical |
| 12 | exit-path suite on `load_manifest`/`verify_frozen`/`main` (12 cases) | see below | 3/3/3 for manifest faults; 4/4/4/4 for frozen faults; 2/2 for usage; digest for the real manifest |
| 13 | `git rev-parse 20e392e:tools/kama-probe.sh`, `git merge-base --is-ancestor 20e392e HEAD` | 0 / 0 | blob `447e29b397405a3ee9813ca2e44aedf88abe2763` (= manifest `source_blob`); ancestor yes |
| 14 | `git status --porcelain .ufo/waves/round-16`; `git diff` over both receipts | 0 | both receipts **modified** vs b8e485c at that moment; `non_port_diff_lines=0`; later re-checked clean (`git diff --quiet` exit 0 both) — see F4 |
| 15 | `grep` for any digest/pin of the matrix or `check.py`; any executable `72`/`9`/`17` assertion | 1 | none (only prose in `falsify/make_spec.py`, `build/advice/*`) |

## Confirmed sound

**Frozen verification (manifest + git blob) — confirm.** One-byte tamper → `SystemExit(4)` `sha256 mismatch: frozen is cef635…, manifest declares 93ee43…`; byte-count lie → 4; bogus `source_commit` → 4 (`git cat-file … exited 128`); bogus `source_path` → 4; missing/invalid/`sha256`-less manifest → `SystemExit(3)`. The real manifest + real frozen file returns `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64`. On every 3/4 path the harness was not invoked and no receipt was written (tmp `wave/` stayed empty), matching `measure.py:6-34` and SKILL.md's map. Manifest `source_blob` is not read by the tool (`grep` in #15) but is independently true.

**Directional set equality — confirm, and it is load-bearing.** Fabricated-receipt matrix (case: exit):

- A baseline shape (55 pass + 17 flip) → 0.
- D `after` identical to `before` (no-op change) → **1** (`after failures 17 (need 0)`; `changed=0 equal=False`).
- I `before` entirely green → **1** (`before failures 0 (need >=1)`; `missing_failed=` 17 names).
- E no `MODEL_LOADING` expectation → **1**.
- H one extra red non-loading row in `before` → **1** (`extra_failed=F0.t0`).
- J red set = loading + one extra, after green → **1** (`extra_failed=F17.t17`).

So a null or over-broad change cannot reach exit 0, and extra reds are named. `receipt["exit"]` values 3/4/2/1/0 match the documented map.

**Reproducibility — confirm.** A fresh full run of the real matrix on both real probes reproduces every one of the 144 `(name, passed, verdict, reason, probe_exit)` tuples exactly (`row-level differences: 0 []`), with the same `72/55/17` and `72/72/0` totals and 9 families. The L1 numbers are real, not fabricated.

## Findings

### F1 (medium) — PASS is not anchored to matrix breadth; the gate passes vacuously on a reduced matrix

Evidence: a matrix containing **one** real row passed the gate (rows 3–5 above; exit 0, `loading_expectations=1`), and the honest 17-row/13-loading subset also passed (rows 6–8; exit 0, `loading_expectations=13`). A fabricated single-row matrix (case C) and a 17-row all-loading matrix (case B) pass identically.

Cause, three places:

- `measure.py:344-361` reads only `failures`/`passes` and the `records` list; it never reads `parsed["tests"]`, `matrix_sources`, `schema` or `probe_sha256`. There is no `EXPECTED_TESTS`/`EXPECTED_LOADING` constant.
- `tests/probe-verdicts/check.py:150-172` enumerates `sorted(CHECK_DIR.glob("*.json"))` with no expected file set or row total, so a deleted matrix file silently shrinks the corpus and still reports `failures=0`.
- Nothing anywhere in the wave digests `tests/probe-verdicts/check.py` (`fd49ff7c…`) or the nine matrix JSONs; the only sha256 pin is the frozen probe.

Consequences, precisely stated:

- `measure.py` exit 0 means "for the rows that exist, the frozen arm fails exactly the rows labelled MODEL_LOADING and the current arm passes all of them." It does **not** mean the round's `72 rows, 9 families, 17 MODEL_LOADING`, and it does **not** establish KQ19's "passes every other row" in the general case (with one row there is no "other row").
- The escape hatch is **deletion** (or addition of synthetic rows), not relabeling: raising a row's expected verdict to `MODEL_LOADING` without a matching frozen failure is caught as `missing_failed` (cases H/J), so the oracle cannot be silently widened — only shrunk. The minimal passing matrix is 1 row; any subset of the 55 non-loading rows may be deleted without changing exit 0.

This is the same defect class the lane already recorded as KQ18 (declared vs observed corpus count) and the build advice concedes it: `.ufo/waves/round-16/build/advice/MeasureRunner.md:68-69` — "If the harness drops tests, check `tests` totals in the two run files" — a manual step, not a gate. The tool conforms to its own docstring (`measure.py:20-23`), which is weaker than the count claims in `corpus/lessons/round-16.md:64,92` and `SKILL.md:531`.

Minimal fix (advice only): in `main()`, require `parsed["tests"] == EXPECTED_TESTS` and `len(loading_names) == EXPECTED_LOADING` (or compare against digest-pinned matrix files) before `ok`; fail exit 1 with the observed counts in the reason. Today the current PASS is safe only because the matrix is intact, which I verified independently (row 11).

### F2 (low, latent) — `check.py`'s exit code is printed but never gated

`measure.py:155` stores `proc.returncode`, `:304` prints it, and `:361` never consults it. Demonstrated: an `after` receipt with `exit=2` and a clean JSON document yields exit **0** (case G). With today's `check.py` this is unreachable — every `return 2` in `check.py:453-481` precedes document construction, so exit 2 arrives with `parsed=None` and the gate fails — but the gate's "exit" column has no discriminating power. The build advice's premise that "harness exit 2 still lands in the receipt with `parsed` set or null" (`MeasureRunner.md:63-65`) is false for this check.py: exit 2 can only be `null`. Recommend `receipt["exit"] != 0` on the `after` arm (and `not in (3,4)` generally) or an explicit comment that failures, not exits, are the gate.

### F3 (low) — only the "before" arm is content-pinned

`verify_frozen` proves the frozen bytes equal `20e392e:tools/kama-probe.sh` (ancestor of HEAD, blob sha1 = manifest `source_blob`). It cannot prove that commit is the "pre-round" state — that is an external assertion — and the oracle (`check.py` + nine JSONs) has no digest. Manifest fields `snapshot`, `capture`, `source_blob` are dead to the tool (it hardcodes `FROZEN` at `:43`); all three are currently accurate. A manifest whose commit holds tampered bytes would pass, but that is content-addressing working as designed; the real risk is the unfrozen oracle in F1.

### F4 (low) — receipt provenance is mutable; the evidence changed under review

Mechanism: `run_check` writes with `Path.write_text` (`:170`) **before** the gate decides, so a failing run clobbers the last good receipt and keeps no history; `stdout_sha256` necessarily changes every run because ports are random, so it identifies a run rather than pinning content.

Observed, not merely inferred: at row 14 both receipts were **modified** against b8e485c (`git status` showed `M .ufo/waves/round-16/run-before.json`; `git diff --stat` = 148 changed lines each) with `non_port_diff_lines=0` — a post-commit re-run with identical verdicts. By the end of this review both files were clean and byte-identical to HEAD again (`git diff --quiet` exit 0 for both; `parsed_equal True`), i.e. another actor re-ran and/or restored them mid-review. So the cited evidence bytes are not stable over the review window, and a reader cannot tell from the tree whether `run-*.json` describe the committed code or a later working-tree probe. The substantive verdicts were identical in both states (row 11 plus the port-only diff), so no current claim is affected; the hazard is that a later run in the same window *could* have changed them silently and no committed baseline would object. Corroborating hazard: this wave's own spec forbids reviewers from running `measure.py` for exactly this reason.

### F5 (info) — failure diagnostics

On unparseable stdout, `receipt["parsed"]=None` and the only kept bytes are `stdout_sha256`; `stderr_tail` is 600 chars (`:163`). A `parsed=null` failure therefore cannot be diagnosed from the receipt. Not gated in the wrong direction.

## Limitations / inferences

- I did not execute `measure.py` (prohibited). Gate-path tests imported the shipped file by path and replaced only `run_check` and `WAVE`; receipts were directed at `/tmp` and the tmp `wave/` directory remained empty on the 3/4 paths, confirming no harness run occurred. [INFERENCE] The imported module is the shipped bytes (same path, no writes to it).
- Rows 3–10 are honest harness output: only the *matrix directory* was trimmed (real rows copied verbatim from `tests/probe-verdicts/*.json`, real `check.py`, real probes). Cases B/C/F/G in the fabricated suite are labelled fabricated and test gate logic, not the pipeline.
- Case F (forged `failures=0` over failing records) still failed closed because `directional` reads records; the summary fields alone cannot flip a result. Confirmed.
- Exit-code reachability claims for F2 are from reading `check.py:453-481`; I did not try to make it emit JSON with exit 2.

## Verification gaps for L1

- One concrete conjunct is missing (F1). Adding a `tests`/loading-count assertion would make the tool's 0 mean what the round's prose claims; until then, any citation of "72/72" must be backed by `parsed["tests"]` and the `9`/`17` counts read out of the receipts, which are present and correct today (row 11). No other attacked property is false: frozen pinning, directional equality, and the 3/4/2/1/0 exit map all behave as documented.

Installs: none (nothing to install; pacman pause irrelevant). No `llama-server` started; no port 8080/34113 bound or probed.
