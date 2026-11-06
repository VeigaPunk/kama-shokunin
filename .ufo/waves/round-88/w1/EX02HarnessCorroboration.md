# EX02HarnessCorroboration — independent corroboration of C1 through the lane's own stub harness

## Scope

- Re-ran C1's router readiness rule through `tests/probe-verdicts/check.py` (the existing stub-matrix harness), **not** through `tools/round88-router-cells.py`, so the two instruments are independent.
- Harness bytes are identical at B, M and T: `sha256(tests/probe-verdicts/check.py) = 12367de62efafa02641c4acb497e50f1be5019b54879a9ac6da13efd5f8071a5` at `9b4c7af1…`, `138a7543…` and `f77d2ae9…` (no matrix file in `tests/probe-verdicts/` carries a router `status` object, verified by grep for `"value"`).
- Wrote a new 21-cell matrix `RouterStatus.json` in this seat's out dir only; `tests/` untouched. It covers loaded / unloaded / loading / downloading / sleeping / incomplete / failed-between / unknown string, single-match, two-entry precedence (loaded wins, status-less wins, loading beats unloaded, non-match ignored), wildcard (no status / loaded wins / all unready), `normalize_id` matching, plus three boundary cells (non-string value, empty-string value, loading-class reason order).
- Scratch clone-free: probe bytes extracted with `git show <rev>:tools/kama-probe.sh` into `/fast/scratch/hyaku/kama-r88/EX02HarnessCorroboration/`; matrix dir copied there so the harness never reads the lane's `tests/`.
- Probe extraction is the measured one: `probe-M sha256 bd7a6a2228d04b69abcc5d19f2907a9caf737347ef96ff92722edbc3180e7bdf` == `probe_sha256` printed in `.ufo/waves/round-88/measured/c1.out:19`.

## Commands and outputs (true exit codes)

```
# setup
cp -r tests/probe-verdicts <scratch>/probe-verdicts; cp RouterStatus.json <scratch>/probe-verdicts/
git show 9b4c7af1…:tools/kama-probe.sh > <scratch>/probe-B.sh     # exit 0
git show 138a7543…:tools/kama-probe.sh > <scratch>/probe-M.sh     # exit 0

python3 <scratch>/probe-verdicts/check.py --probe <scratch>/probe-M.sh --json       # exit 1  tests=93 passes=79 failures=14
python3 <scratch>/probe-verdicts/check.py --probe <scratch>/probe-B.sh --json       # exit 1  tests=93 passes=80 failures=13
python3 <scratch>/probe-verdicts/check.py --probe <scratch>/probe-M.sh --only <21 RouterStatus names> --json
                                                                                    # exit 1  tests=21 passes=7 failures=14 (repeat of the M run: identical outcomes)
python3 <scratch>/probe-verdicts/check.py --probe <scratch>/probe-B.sh --only RouterStatus.unloaded-single   # exit 1
python3 <scratch>/probe-verdicts/check.py --probe <scratch>/probe-M.sh --only RouterStatus.loaded-single     # exit 0
python3 <scratch>/probe-verdicts/check.py --probe <scratch>/probe-M.sh --only RouterStatus.unloaded-single   # exit 1
```

Per-cell table at B and M: `out/EX02HarnessCorroboration/router-cells.txt`. Summary of it:

- M, verdict+reason+exit agreement with the frozen rule: **19 / 21**. The two exceptions are the boundary cells `nonstring-status-value` and `empty-string-status-value` (finding D2).
- M, harness-level PASS: 7 / 21. The other 12 cells have verdict+reason+exit exactly as the frozen rule requires and are failed **only** by `served_model_ok` (finding D1).
- B, verdict+reason+exit agreement: 8 / 21. Every drift-expecting cell answers `MODEL_OK` at B (`matched`, or `expected-wildcard`), exit 0 — the motivating false green reproduced at seam level.
- The 72 pre-existing tests pass 72/72 in both runs (`m.json`, `b.json`), reproducing `.ufo/waves/round-88/measured/harm.out` (`tests=72 passes=72`) on a second, independent invocation of the same harness bytes.

## Findings

**DEFECT — D1 (harness, not the claim): `check.py` cannot grade any non-OK router cell.**
`tests/probe-verdicts/check.py:357-373` returns `served_model == "-"` for every verdict outside `{MODEL_OK, MODEL_MISMATCH}`, justified by the docstring premise (lines 360-366) that `classify()` "only ever rewrites [C_SERVED] inside the `is2 && has_models` arm, the arm whose verdicts are MODEL_OK / MODEL_MISMATCH". That premise no longer holds: `tools/kama-probe.sh` at M sets `C_SERVED` to the parsed ids at `592-594`, then `router_refine` mutates the verdict **inside that same arm** at `610` into `MODEL_UNLOADED` (`512`) or router-flavoured `MODEL_LOADING` (`511`), so `served_model` legitimately carries the ids. The pass predicate then ANDs `served_model_ok` (`check.py:492-500`), and the matrix schema offers no way to override it (`check.py:60-62`, unknown-expected-key rejection at `138-140`) — so a matrix authoring exactly the frozen rule is forced into a FAIL. Evidence: `out/EX02HarnessCorroboration/m.txt` (12 FAIL lines whose only diff is `served_model='…' (expected '-')`) and `router-cells.txt`. Impact: does not touch predicate C1 (graded by the counter) and does not touch the harm conjunct (72/72 unchanged); it blocks adding router coverage to `tests/probe-verdicts/` for any future round, and it makes my own matrix un-landable as-is. Fix belongs in the harness, not the probe: `expected_served_model` must treat `MODEL_UNLOADED` like `MODEL_OK`/`MODEL_MISMATCH`, and treat `MODEL_LOADING` as id-bearing **only** when that row's `/v1/models` body carries a router `status` object (the 503-envelope path must keep `-`).

**DEFECT — D2 (frozen rule under-specified; implementation extends it) — `status.value` sentinel `?`.**
The frozen rule (`plans/round-88-claims.md:47-51`) refines only when a matching entry "carries an object `status` with a string `value`"; a non-string value is therefore outside the rule and the literal reading keeps today's `MODEL_OK/matched`, and an **empty** string is a string value whose literal reason is `router-`. The implementation collapses both to the sentinel `?` (`tools/kama-probe.sh:485`) and reports `MODEL_UNLOADED reason=router-?` (`506`, `512`). Measured at M: `nonstring-status-value` → `MODEL_UNLOADED/router-?/2` where the rule says `MODEL_OK/matched/0`, and `empty-string-status-value` → `MODEL_UNLOADED/router-?/2` where the rule says `MODEL_UNLOADED/router-/2`. Direction is fail-closed (never a false green) and no conforming llama.cpp router can produce it — the pinned README (S581, commit `704366d7…`, lines 2059-2118) documents `status.value` only as the strings `unloaded|loading|loaded|sleeping|downloading|incomplete`, with `failed:true` on the unloaded example. So this is a rule-text gap plus a deliberate defensive extension, not a reproduced false green; it does mean the predicate's printed vocabulary contains a value (`router-?`) the rule cannot derive.

**NOTE — N1 (rule gap):** with both `downloading` and `loading` present the rule says only "any loading/downloading → `MODEL_LOADING` reason `router-<value>`" and never says which value names the reason. Cell `loading-class-reason-order` (unloaded, downloading, loading in that order) yields `router-downloading`, i.e. first-in-entry-order (`tools/kama-probe.sh:505`). Deterministic across the repeat run, but unpinned by the frozen text.

**NOTE — N2 (harm conjunct, independent):** `check.py` at T, run from my scratch copy with 21 extra rows, still passes all 72 pre-existing tests at B and at M — a second, independent reproduction of `measured/harm.out`.

**NOTE — N3 (base false green, independent):** at B, `RouterStatus.unloaded-single` gives `MODEL_OK/matched exit 0` with a 200 `/health` beside it (`x-b-fail.txt`); at M the same stub gives `MODEL_UNLOADED/router-unloaded exit 2` (`x-m-unloaded.txt`). The harness, not just the round-88 counter, witnesses the regression fix.

**NOTE — N4 (consistency):** across all 21 cells at M the harness's `drift` invariant (`drift == (verdict != MODEL_OK)`) holds and `route_ok` is never False; the 21-cell repeat run produced byte-for-byte identical verdicts/reasons/exits. `MODEL_UNLOADED` is also wired outside `check` (model surface in `listeners` at `tools/kama-probe.sh:844`, baseline vocabulary at `1060`) — reading only, not exercised by my cells.

**No BLOCKER.** C1's frozen predicate is not falsified: every in-spec cell matched exactly at M, and the counter/receipt chain (`probe_sha256`) is corroborated by my independent extraction.

## Deliverables (all under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-88/w1/out/EX02HarnessCorroboration/`)

- `RouterStatus.json` — 21-cell matrix, schema `kama-probe-verdicts/v1`, sha256 `7d50873fa01d45737046214fb6784aafbfac2e32454ebc47e9948a0312ceb39f`; names all prefixed `RouterStatus.` so it can land in `tests/probe-verdicts/` once D1 is fixed.
- `m.json`, `m.txt` — harness machine document + human summary at M (93 tests, 79 passes, 14 failures).
- `b.json`, `b.txt` — same at B (93 tests, 80 passes, 13 failures).
- `m-repeat.json`, `m-repeat.txt` — repeat of the 21 router cells at M (determinism).
- `router-cells.txt` — per-cell B/M table with verdict/reason/exit and served_model comparison.
- `x-exits.txt`, `x-b-fail.txt`, `x-m-pass.txt`, `x-m-unloaded.txt` — captured true exit codes and the single-cell receipts.
- `receipts.txt` — hashes (matrix, harness, both probe extractions) and exact commands.
- No tool installs or upgrades were made (nothing was needed; no pacman, no network installs). Network use: one read-only GET of the pinned llama.cpp `tools/server/README.md` at `704366d7…` to check `status.value` typing (S581).

VERDICT: partial — C1's frozen router rule is corroborated cell-for-cell through the independent stub harness at M (19/21 exact, B 8/21), but 12 otherwise-correct cells are ungradable because `check.py:357-373` still asserts the pre-r88 `served_model` contract, and two out-of-spec `status.value` shapes diverge from the literal rule via the `?` sentinel.
