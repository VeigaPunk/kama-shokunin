# SB01RoundDrafts — kama round 90 w1

## Scope

Drafted the round-90 record text from the frozen plan and the committed receipts: (1) a `## Round 90` SCORECARD
section with both predicates, base→after numbers, B/F/M/M2, two capability rows and `### Planned (round 91)`;
(2) a LOG.md entry; (3) a `corpus/lessons/round-90.md` draft with Gate (S587/S588 admits + SC01 placeholder),
two mined mistakes and the r89 closure R1–R5 dispositions. Read-only in the lane: no tracked file edited, no
commit/push/fetch, no endpoint touched, no subagent, no tool installed. Read: `plans/round-90-claims.md` (full),
`SCORECARD.md` §Round 89/§Axes/§Planned, the round-89 LOG entry and lesson, the r89 verifier spot-check, every
round-90 receipt, and the probe/counter sources.

## Commands and outputs (exit codes)

- `python3 tools/round90-reason-rows.py --repo . --rev 2ee0b55f4d3fd0cb3157d26b03280c1d21e27b2d` →
  `REASON_ROWS population=23 documented=23 rows=24 bound=24 unbound=0 missing=0 duplicates=0 additional=1
  receipt=current probe_sha256=c197912f… rev=2ee0b55f…`, **exit 0** (read-only re-derivation; identical to
  `measured/c2.out:26`).
- `python3 tools/round90-reason-rows.py --repo . --rev 99cdb4d6… | tail -2` → base summary
  `documented=0 rows=0 … missing=23`; shell **exit 0** because the pipeline reports `tail` — the counter's own
  exit 1 is the committed `controls/c2-base.out:25`, not this run.
- `git show <rev>:tools/{round90-hostile-answers,round90-reason-rows}.py | sha256sum` at `6f6d7873`,
  `f968fb19`, `2ee0b55f` → `345b12b3…` / `fa4c3177…` at every revision, **exit 0** (counters unchanged from
  freeze). `git show 6f6d7873:tools/round90-reason-capture.py` → **exit 128** (path absent at freeze); the
  empty-stream hash `e3b0…` is not a file hash. At `2ee0b55f` the capture tool is `dea89996…`.
- `git show <rev>:tools/kama-probe.sh | sha256sum` → `c15ffca8…` at `99cdb4d6`/`6f6d7873`; `c197912f…` at
  `f968fb19`/`2ee0b55f`, **exit 0**.
- `git diff --stat f968fb19 2ee0b55f` → 6 files (`measured/c1.out`, `harm-M.out`, `reason-capture.out`,
  `reason-cells.jsonl`, `SKILL.md`, `tools/round90-reason-capture.py`), **exit 0**.
- `git status --porcelain` → the L1's uncommitted edits (`SCORECARD.md`, `corpus/README.md`,
  `corpus/SOURCES.md`, `corpus/knowledge/probe-answer-bounds.md`, `corpus/lessons/round-90.md`,
  `measured/c2.out`, `measured/c1-counter-hash.out`, wave dirs); I wrote only my out dir, **exit 0**.
- `curl --version | head -1` → `curl 8.23.0`; `python3 --version` → `Python 3.14.8`, **exit 0**.
- `git grep -n -i -E 'max-filesize|control char|U\+001F' 99cdb4d6 -- corpus/knowledge SKILL.md` → one hit,
  `corpus/knowledge/snapshot-history.md:51`, **exit 0**.
- `grep -n`/`sed -n` line-number checks on every receipt line cited in the drafts; all cited line numbers were
  read from the files, **exit 0**. A first `python3 -c` read of `w1-spec.json` from the wrong cwd failed
  (`FileNotFoundError`, **exit 1**); re-run from `.ufo/waves/round-90/`, **exit 0**.
- C1 was **not** re-run by this seat (it starts stub listeners and needs `--work`); its numbers are from the
  committed `measured/c1.out` (committed at M2, names M) and `measured/harm-M.out`.

## Findings

- **DEFECT (record integrity, working-tree edit in progress)** — `SCORECARD.md`'s depth row currently carries
  literal placeholders `SKILLSHA`, `SKILLLINES`, `SKILLH2`; committing the axes edit as-is would publish them.
  Evidence: `git diff SCORECARD.md` (depth row). The L1 must fill them before commit.
- **NOTE (becomes a DEFECT if sealed as-is)** — `measured/c2.out` is untracked at draft time; the assignment's
  C2 after-number is nevertheless correct: my read-only run at M2 printed the same summary as
  `measured/c2.out:26` (`documented=23 rows=24 bound=24 … additional=1`, exit 0). The L1 must commit the
  receipt before the record is sealed. Evidence: `.ufo/waves/round-90/measured/c2.out:26`; my run above.
- **NOTE** — the L1's working-tree lesson (`corpus/lessons/round-90.md`) carries three mistakes (H4
  non-discrimination, a stub header-buffer fault caught by the positive cells, the C2 expectation miscount).
  My draft carries the two the seat spec names (H4, C2 expectation); the stub-fault mistake is real and the L1
  may keep it as a third — its shape is reproduced by F1 (`controls/c1-f1-blanket-refusal.out`:
  `mismatches=6 positive_mismatches=5`). Evidence: `corpus/lessons/round-90.md` M2 vs `lesson-round90.md`.
- **NOTE** — the H4 first draft's non-discrimination mechanism is exact: `check` joins served ids with commas
  (`tools/kama-probe.sh:901`, `tr '\n' ','`), so a newline never starts a line; the fixed cell's header-column
  condition is what makes base red (`header_cols=9 empty_header_cols=2`) and M green (`header_cols=7
  empty_header_cols=0`). Evidence: `controls/c1-base.out` H4; `measured/c1.out` H4.
- **NOTE** — `additional=1` in the C2 summary is the declared `body-too-large` row, not a failure: the counter
  docstring says additional rows are "reported, not a failure". The predicate's printed shape is met with
  `additional=1` present. Evidence: `measured/c2.out:26`; `tools/round90-reason-rows.py` docstring.
- **NOTE** — the S587/S588 source rows, the knowledge entry, the README round-90 block, the SCORECARD axes
  edits and the lesson were uncommitted at draft time; the drafts mark them. Evidence:
  `git status --porcelain`.
- **NOTE** — no wave-1 seat report had landed at draft time (only `EX02HarmLatency` and
  `MT02ReasonRowMutants` artifacts); the SC01 reject row and the wave dispositions are placeholders exactly
  as the seat spec requires. Evidence: `find .ufo/waves/round-90/w1/out -type f`.

## Deliverables

- `.ufo/waves/round-90/w1/out/SB01RoundDrafts/scorecard-round90.md`
- `.ufo/waves/round-90/w1/out/SB01RoundDrafts/log-round90.md`
- `.ufo/waves/round-90/w1/out/SB01RoundDrafts/lesson-round90.md`
- `.ufo/waves/round-90/w1/SB01RoundDrafts.md` (this report)

VERDICT: partial — drafts complete and receipt-backed; C2's measured receipt is uncommitted and the SC01 reject row plus wave dispositions are left for the L1 as specified.
