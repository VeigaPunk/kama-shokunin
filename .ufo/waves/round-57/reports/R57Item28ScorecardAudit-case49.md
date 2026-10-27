# R57Item28ScorecardAudit — distinct case 49 (independent stale-count test)

Separate evidence file for distinct case 49. Independent of `tools/round42-selfdesc-reconcile.py`:
a small instrument that re-derives the SCORECARD calibration row's `verifier-spotcheck` count
two ways and tests only that case. Committed bytes only; fixture repos live under
`/fast/scratch/hyaku/kama-r57/R57Item28ScorecardAudit/case49/fx` and were removed after the
receipts were copied into the lane wave path.

## Instrument (`calib-count-audit.py`)

Contract:

- reads `SCORECARD.md` from `git show <tip>:SCORECARD.md` (never the working tree);
- finds the `## Axes` row whose axis is `calibration`, then the `run ... → ...` fact whose
  command mentions `verifier-spotcheck`; the arrow token is the claim;
- `tree_count`: `git ls-tree -r --name-only <tip> corpus/lessons`, basenames ending
  `verifier-spotcheck.md` (execution-free);
- `exec_count`: that same command, run with `cwd` = a `git archive --format=tar <tip>` export;
- `stale = claim != tree_count or claim != exec_count`;
- exit `0` fresh, `1` stale, `2` cannot evaluate (missing row/fact, non-integer claim, or a
  counting command that emits no integer). Read-only on `--repo`.

Unlike the frozen counter, it never accepts a match because "some stdout line equals the claim"
alone: the tree count is a second, execution-free derivation, so a claim cannot be satisfied by a
command that ignores the tree.

## Fixture battery (`run-fixtures.sh`, receipt `fixtures.out`)

Base fixture is a copy of lane tip `8a7f1976` re-committed in scratch
(`fixture_toplevel=/fast/scratch/hyaku/kama-r57/R57Item28ScorecardAudit/case49/fx`); each mutation
is committed on top and undone with `git reset --hard <base>` in the same scratch repo.

```text
--- F1-fixture-base-fresh
claim=43 tree_count=43 exec_count=43 stale=False reason=claim==tree==exec
exit=0
applied=claim+1
--- F2-claim-44-vs-tree-43
claim=44 tree_count=43 exec_count=43 stale=True reason=claim!=tree
exit=1
applied=cmd-noop
--- F3-counting-command-emits-no-integer
claim=43 tree_count=43 exec_count=none stale=indeterminate reason=counting-command-produced-no-integer
exit=2
--- F4-one-blob-deleted-tree-42-vs-claim-43
claim=43 tree_count=42 exec_count=42 stale=True reason=claim!=tree
exit=1
--- F5-reset-back-to-base-fresh
claim=43 tree_count=43 exec_count=43 stale=False reason=claim==tree==exec
exit=0
--- F6-commit-with-no-SCORECARD
cannot-evaluate: git show 46ad6fb9...:SCORECARD.md: fatal: path 'SCORECARD.md' does not exist in ...
exit=2
```

Mutations: `claim+1` rewrites the arrow token 43 → 44 in the fixture's SCORECARD; `cmd-noop`
replaces the glob command with `python3 -c "print('verifier-spotcheck')"` (keeps the needle, emits
no integer); F4 deletes `corpus/lessons/round-56-verifier-spotcheck.md` and commits.

What each fixture establishes:

- F1/F5 — the repaired row is accepted, and acceptance is not sticky (a reset returns to fresh).
- F2 — a wrong claim is rejected even when the tree and the command agree with each other.
- F3 — a counting command that produces no integer is `cannot-evaluate`, not a pass.
- F4 — the check is content-bound: removing one closure blob makes the same claim stale, so a
  harness that never opens `corpus/lessons` cannot pass it.
- F6 — fail-closed when no SCORECARD exists at the tip.

## On the lane (receipts `lane-tips.out`, `final-tip.out`)

```text
tip=b89bdab2...  claim=42 tree_count=43 exec_count=43 stale=True  exit=1
tip=7c873d7b...  claim=42 tree_count=43 exec_count=43 stale=True  exit=1
tip=8640e34c...  claim=43 tree_count=43 exec_count=43 stale=False exit=0
tip=8a7f1976...  claim=43 tree_count=43 exec_count=43 stale=False exit=0
```

The tools' own verdicts agree: `mismatches=1 maxN=56 met=False` (exit 1) at `b89bdab2` and
`7c873d7b`; `mismatches=0 maxN=57 met=True` (exit 0) at `8640e34c` and `8a7f1976`.

## The frozen no-op cannot pass this case (receipt `controls-vs-instrument.out`)

The stub path below existed when the receipt was captured (15:14) and has since been removed by the
integrator's reorganisation of `controls/`; the receipt is the authoritative record.

```text
$ python3 .ufo/waves/round-57/controls/c1-noop.py
mismatches=0 maxN=46 met=True
exit=0

$ python3 calib-count-audit.py --repo <lane> --tip b89bdab2
claim=42 tree_count=43 exec_count=43 stale=True reason=claim!=tree
exit=1
```

The stub's `maxN=46` is neither the claim (42) nor the observed count (43); it is a copy of the
round-46 regression value that also appears at SCORECARD line 2676. That is the concrete link
between the "expected 46" wording and a false green.

## Limits of case 49

- One row, one fact. It does not test hashes, line counts, planned/retired/saturation predicates,
  or the capability census — those are the frozen counter's other predicates and were green at
  the tip (`r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0
  province=0 rel=0`).
- It executes the row's own command (trusted bytes at the tip) beside an execution-free tree
  count; a command that counts something other than the named blobs would need its own case.
- It requires a commit; a working-tree repair is invisible to it, as it is to the frozen counter.

Report: .ufo/waves/round-57/reports/R57Item28ScorecardAudit-case49.md
