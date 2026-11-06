# RV03CounterReview — round88-router-cells.py as an instrument vs plan C1

## Scope
Reviewed `tools/round88-router-cells.py` (bytes identical at F=fb76e7f2, M=138a7543, worktree T=f77d2ae9;
sha256 `576a1b374c9150dbd3f58acf26a69c794bd5ac724911aba29f62291ed3435e21` in all three) against the frozen
verdict rule and predicate in `plans/round-88-claims.md`, sentence by sentence. Read `tools/kama-probe.sh`
at M (sha256 `bd7a6a2228d04b69abcc5d19f2907a9caf737347ef96ff92722edbc3180e7bdf`) where the counter's
grading assumptions (row shape, GET-only side effects, verdict vocabulary) had to be checked. Evidence:
counter copy + probe copy in my out dir (line refs below are `counter-F.py` / `probe-M.sh` there).
No subagents, no edits outside out dir + scratch, no traffic to 127.0.0.1:1234.

## Commands and outputs (all from scratch; TMPDIR=scratch/tmp; full logs in out dir)
1. `python3 counter-F.py --repo <lane> --rev 138a7543… --work <scratch>/w-m` → predicate line verbatim
   `ROUTER_CELLS cells=17 mismatches=0 canned=14 live=3 probe=rev probe_sha256=bd7a6a2…`, `exit=0`
   (`rerun-M.out`; run twice, identical). Matches `measured/c1.out` and pins probe bytes = `git show M`.
2. `… --rev 9b4c7af1… --probe-file <lane>/.ufo/waves/round-88/controls/f2-any-loaded.sh` →
   `mismatches=4 probe=override probe_sha256=f542dc2a…`, `exit=1` (`rerun-f2.out`) — byte-identical to
   `controls/c1-f2.out`; f2 file sha256 matches receipt. Discriminating cells: C03/C06 (loading→unloaded
   forged), C10/C11 (expected id ignored). Do-nothing control holds (≥1 mismatch).
3. Synthetic probe emitting rows[0]=WRONG + rows[1]=MODEL_OK (`--probe-file x-extra-row.sh`) → all 17 cells
   `observed=WRONG reason=decoy-first`, mismatches=17, `exit=1` (`probe-extra-row.out`): the counter grades
   `rows[0]` only (counter-F.py:92).
4. Synthetic probe emitting `{"rows":[]}` → all 17 `observed=UNPARSEABLE reason=exit0`, mismatches=17,
   `exit=1` (`probe-zero-rows.out`): zero/missing rows fail safe red, no crash.
5. `--rev deadbeef…` → `ROUTER_CELLS could-not-evaluate: git show … failed`, `exit=2` (`probe-badrev.out`);
   missing `--rev` → argparse `exit=2`.
6. `git diff --stat 9b4c7af1 138a7543`: no `tests/` change base→M; `grep -r MODEL_UNLOADED tests/probe-verdicts/`
   → no match; `measured/harm.out` shows `tests=72 passes=72`, no MODEL_UNLOADED case anywhere.

## Findings
No DEFECT, no BLOCKER. Every behaviour the predicate names reproduces exactly (runs 1, 2, 5). Sentence-by-sentence:

- **Consistent:** all 14 CANNED cells match the frozen verdict rule (C01 loaded→OK; C02/C05/C07/C14
  other-values→UNLOADED; C03/C06 loading/downloading→LOADING; C04 failed→UNLOADED; C08 status-less keeps
  OK; C09/C10 id-match precedence incl. other-id-loaded ignored; C11 absent-id→MISMATCH, sanctioned by the
  plan's deference to the CANNED table; C12/C13 wildcard precedence). Live sequence matches plan: sha-pinned
  binary+model (counter-F.py:185-189), `--no-models-autoload --models-max 1` on a free port, L01/L02/L03 with
  real load/unload between cells, probe then independent oracle (200→OK; 400 "model is not loaded"→UNLOADED;
  else CannotEvaluate, counter-F.py:175-182), child torn down via process group (209-218). Probe-side safety:
  `kama-probe.sh check` issues GETs only (probe-M.sh:306-309, 338-340; no POST anywhere), so the
  oracle-after-probe ordering cannot be corrupted by the probe loading the model. Summary is byte-exact vs
  the plan format; `probe_sha256` independently pins the graded bytes. Exit codes 0/1/2 exercised.
- **NOTE [instrument under-measures the rule's reason/exit sentences]:** grading is
  `expected == observed` on the verdict string only (counter-F.py:232-236; CANNED carries no reason column);
  `reason` is printed (run 1 shows rule-correct `router-unloaded[-failed]`, `matched`) but never compared, and
  the probe's exit code is discarded (counter-F.py:87-96). The rule sentences "`reason router-<value>`
  [-failed]" and "MODEL_UNLOADED is drift (exit 2)" are therefore not graded here — and since base→M adds no
  test cases (run 6), they are graded nowhere in the frozen instrument set. A probe with right
  verdicts but wrong reasons/exit would satisfy predicate C1 as written. Does not flip today's verdict.
- **NOTE [CANNED coverage gaps]:** untested rule branches: several entries matching the SAME id (precedence
  across duplicates — C09/C10 vary only non-matching ids); wildcard `-` and empty expectation (rule names
  `*`, `-`, empty; cells use `*` only); wildcard with no `status` objects (unchanged OK); non-string/empty
  `status.value` (probe maps to `?`→UNLOADED, probe-M.sh:474-486, beyond the rule's wording). Bounds what the
  green proves; nothing flips today.
- **NOTE [unexpected-exception paths]:** non-CannotEvaluate faults (probe hang >60s → TimeoutExpired,
  OSError in copy/socket setup) escape uncaught from the canned loop → traceback, exit 1, no summary line —
  neither graded mismatch nor the spec's could-not-evaluate(2) (only `live_cells` is wrapped,
  counter-F.py:246-253). Environment-fault robustness only; not reachable via probe verdict behaviour.
- **NOTE [extraction semantics, demonstrated]:** extra rows → only `rows[0]` graded (run 3); a decoy first row
  cannot manufacture a pass unless the forged probe crafts the graded row itself — exactly what the f1/f2
  canned controls catch (run 2 reproduces f2). Zero rows/no verdict key → UNPARSEABLE mismatch (run 4).
  Today's `check --port` structurally emits exactly one row (probe-M.sh:962-974), so multi-row is
  out-of-contract.
- **NOTE [unexercised paths]:** pinned-prereq absent/sha-mismatch and wait_status/oracle-timeout
  CannotEvaluate paths are code-read only (counter-F.py:175-182, 185-189, 163-172) — hiding host files to
  trigger them is outside lane bounds. `free_port()` bind-then-close TOCTOU is a theoretical race.

## Deliverables
`…/round-88/w1/out/RV03CounterReview/`: `counter-F.py`, `probe-M.sh`, `rerun-M.out`, `rerun-f2.out`,
`probe-extra-row.out`, `probe-zero-rows.out`, `probe-badrev.out`, `x-extra-row.sh`, `x-zero-rows.sh`.
Scratch removed after copy. No tool installs (none needed).

VERDICT: holds — counter measures the frozen C1 predicate faithfully end to end; residual gaps (reason/exit not graded, four untested rule branches) are NOTES that cannot flip today's verdict.
