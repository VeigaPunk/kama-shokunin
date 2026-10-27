# X05NoopSubsetB — rerun N06–N11 variants; preserve outputs; verify roster literal intact

Axes: operability (C1), calibration (C2 secondary — only C1 is in scope here).
Mode: seat falsification, advisory. Leaf only; no dispatch, no source edits, no commits.

- Lane tree: `/home/vgpnk/Projects/shokunin/kama-shokunin` (read-only), HEAD `4a541190b6d494a4e99116249632e99aab80adcc` (advanced past measured tip; see drift check).
- Measured tip attacked: `aca8d0067ea25627c5015c2193c843965148bc8e`.
- Frozen counter/checker/variants verified byte-identical to that tip (sha256 worktree == `git show tip:` blob) and `git diff aca8d006..HEAD -- tools/round59-c1-counter.py tools/round59-battery-outcome-check.py tools/round56-env-leg-battery.py tests/round58-battery-variants tests/round59-battery-variants` is empty (exit 0).
- Scratch: `/fast/scratch/hyaku/kama-r59/X05NoopSubsetB` (TMPDIR set there; removed before yield). Python 3.14.8. No installs/updates performed.

## Attacked claim / clause

C1-r59 sentence, first clause: each round-56 battery leg is accepted only when **its own** named expected outcome is tied to that leg's actual observed field/value **and exit**; and "A leg that discards its result ... must not meet."
My subset is the six generic no-ops N06–N11: `run-body-noop`, `mutant-assert-noop`, `main-not-invoked`, `empty-loop`, `run-rebound`, `try-else`. Killing these is the operability floor for a checker: a structurally inert battery must never be accepted.

## Commands (exact)

Frozen counter, unmodified, whole battery (subset-B lines are N06–N11):

```
cd /home/vgpnk/Projects/shokunin/kama-shokunin
TMPDIR=/fast/scratch/hyaku/kama-r59/X05NoopSubsetB/tmp \
python3 tools/round59-c1-counter.py --repo . \
  --tip aca8d0067ea25627c5015c2193c843965148bc8e \
  --work /fast/scratch/hyaku/kama-r59/X05NoopSubsetB/work \
  --out  .ufo/waves/round-59/w1/out/X05NoopSubsetB/c1-full-rerun.out      # exit 0
```

Scoped per-variant rerun (same frozen fixture-build and same frozen checker invocation as the counter, restricted to `genuine` + N06–N11, capturing each variant's checker verdict and injected-fault matrix):

```
python3 <scratch>/deep-subsetB.py    # exit 0
  -> per variant: fixture git init/add/commit (inside /fast/scratch, toplevel == fixture dir asserted),
     then: python3 <tip>:tools/round59-battery-outcome-check.py --repo <fixture> --tip HEAD
```

## Result — whole-counter replication (independent rerun)

`c1-full-rerun.out`, exit 0:

```
tip=aca8d0067ea25627c5015c2193c843965148bc8e
predicate=C1-r59 outcome-binding checker accepts genuine+3/3 benign and rejects 16/16 no-ops, errors=0
genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True
detail: genuine accept exit=0
detail: B1-rename-comment accept exit=0
detail: B2-helper-leg accept exit=0
detail: B3-concat-labels accept exit=0
detail: N01-calls-removed reject exit=1
...
detail: N06-run-body-noop reject exit=1
detail: N07-mutant-assert-noop reject exit=1
detail: N08-main-not-invoked reject exit=1
detail: N09-empty-loop reject exit=1
detail: N10-run-rebound reject exit=1
detail: N11-try-else reject exit=1
...
detail: N16-decoy-counter-call reject exit=1
```

Identical to the pre-data control `controls/c1-candidate-final.out` on every field. Genuine + 3/3 benign accepted, 16/16 rejected, 0 errors.

## Result — scoped N06–N11 verdicts (`subsetB-rerun.tsv`)

| variant | verdict | checker exit | checker `met` | inner matrix |
|---|---|---|---|---|
| genuine (control) | accept | 0 | True | runs=5 passed=5/5 errors=0 |
| N06-run-body-noop | reject | 1 | False | runs=5 passed=0/5 errors=0 |
| N07-mutant-assert-noop | reject | 1 | False | runs=5 passed=0/5 errors=0 |
| N08-main-not-invoked | reject | 1 | False | runs=5 passed=0/5 errors=0 |
| N09-empty-loop | reject | 1 | False | runs=5 passed=0/5 errors=0 |
| N10-run-rebound | reject | 1 | False | runs=5 passed=0/5 errors=0 |
| N11-try-else | reject | 1 | False | runs=5 passed=0/5 errors=0 |

Grounds for each rejection (from the frozen checker's own `per_leg` output, `checker-N0*.verdict.txt`), i.e. not error/timeout:

- **N06** baseline `exit=0` and `labels=true`, but `base-old-counter/round56-counter/m-drop-ldaudit` each report `call=false, returned_true=true` — the leg returned True without issuing its bound `--counter/--expect` child. Rejected on the call/outcome binding, not on exit.
- **N07** baseline `exit=0`, all three `run` legs `call=true`, but `mutant-assert` is `call=false, returned_true=true` (assert function short-circuited). Rejected on the mutant-assert binding.
- **N08** every fault case `labels=false`, `exit=0`, all four legs `call=false, returned_true=false` — `main` never invoked; no frames at all.
- **N09** same shape: empty `for _leg in []` leaves `results=[]`, `exit=0`, no frames.
- **N10** `run` rebound to `lambda *a, **k: True`; the three run frames exist but `call=false` (no child), `mutant-assert` alone still `call=true`; `exit=0` for four cases.
- **N11** `try/raise/except-pass/else:` never enters the else block: no frames, `exit=0`.

No case produced `error`/timeout (`errors=0` in both the aggregate run and each variant matrix).

## Roster literal integrity (`roster-literal.txt`, `roster-overlap.txt`)

`ROSTER` block at `tests/round58-battery-variants/genuine.py` lines 15–19, 240 bytes,
sha256 `36e8beb7713c21e34e3cfd51e8b1b145ab23581e0cd99df3ec571836e81cb226`.

All six variants carry a byte-identical `ROSTER` block (same sha256/byte count, `identical_to_genuine=True`). Change-region analysis (difflib opcodes vs genuine) shows every mutation lands outside lines 15–19 (`overlaps_roster=False` for all six): N06 insert@38, N07 insert@52, N08 newline-only replace@87, N09 replace@69–82, N10 insert@64–66, N11 replace@69–87. Per-variant unified diffs preserved as `diff-*.diff`.

Consequence: each rejection is attributable to the one named mutation, not to a tampered roster, and the frozen fixture roster was not rewritten by this seat (lane tracked tree clean: `git status --porcelain --untracked-files=no` empty after all runs; the checker's `write_text`/`mkdir` are virtualized, so the battery's lane `OUT` path was never written).

## Verdict on the attacked clause (my subset only)

- Subset verdict: **holds** — N06, N07, N08, N09, N10, N11 are each rejected (6/6) by the frozen checker at the measured tip, with zero evaluation errors, with genuine and 3/3 benign still accepted; roster literal intact and single-change attribution confirmed.
- Calibration honesty caveat (recorded, not scored): these six are generic structural no-ops and were already rejected by the prior r58 per-frame checker (`controls/c1-oldchecker-final.out`: N06–N11 all `reject`). My subset therefore exercises the operability floor and does **not** discriminate r59's marginal claim; the discriminating delta sits in N12/N14/N16 (other seats). A pass here is not evidence of improvement over r58.
- Operability read: the checker rejects an inert leg even when the battery process exits 0 (N06/N07/N10), which is the behaviour the frozen sentence demands ("and exit" alone is insufficient); no reliance on aggregate exit status for these six.

## Preserved artifacts (this seat's output dir)

`.ufo/waves/round-59/w1/out/X05NoopSubsetB/`: `c1-full-rerun.out`, `c1-full-rerun.stdout`, `subsetB-rerun.tsv`, `roster-literal.txt`, `roster-overlap.txt`, `checker-genuine.{out,verdict.txt}`, `checker-N06..N11.{out,verdict.txt}`, `diff-N06..N11.diff`.

## Risks / limits

- Only C1/subset B evaluated; C2 untouched, per assignment.
- The counter's own aggregate line reports exit codes only; the per-variant reason evidence above came from re-running the same frozen checker per fixture (same invocation the counter uses), not from the counter's aggregate output.
- `[INFERENCE]` All six fixtures ran from blobs at `aca8d006`; fixture commit ids differ per variant by design, so hashes of fixture repos are not comparable across runs — verdict lines are.
