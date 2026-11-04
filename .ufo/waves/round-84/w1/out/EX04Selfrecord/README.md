# EX04Selfrecord — calibration

Deliverable: `round84-selfrecord-round83.py` → integration target `tools/round84-selfrecord-round83.py`. No production lane file changed. Report is `EX04Selfrecord.md` here: the out-only write boundary overrides the conflicting trailer location.

## Retained evidence

- `red-selfrecord.out`: HEAD `eb03a64bcd8e2faab0f4f9bcdc55bfc5c1ed2c85`, lesson absent; `SELFRECORD_R83 claims=8 mismatches=6 corrected=0 unbacked=6`, exit **1**. F6/F7 hold.
- `selftest.out`: `SELFRECORD_R83_SELFTEST pass=16 fail=0`, exit **0**, real committed disposable fixtures.
- `initial-red-selfrecord.out`, `initial-selftest.out`: first implementation attempt, exits **1**, **0** respectively. The initial red exposed a real extraction bug: unbounded `population=` matched `out_of_population=0`. Fixed by a key-boundary regex and added that shadow key to the fixture. These are superseded, not acceptance receipts.
- `commands.json`: exact argv/cwd/exit for both clone/root-check/red/selftest sequences. Both clones and both root checks exited **0**. Scratch was deleted in `finally` after each sequence.

Requested executable commands (each executed twice, exact cwd/argv also in JSON):

```
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r84/EX04Selfrecord/wt
# exit 0
git -C /fast/scratch/hyaku/kama-r84/EX04Selfrecord/wt rev-parse --show-toplevel
# exit 0; matched clone root
# cwd=/fast/scratch/hyaku/kama-r84/EX04Selfrecord/wt
python3 tools/round84-selfrecord-round83.py --repo .
# exit 1
python3 tools/round84-selfrecord-round83.py --selftest --work /fast/scratch/hyaku/kama-r84/EX04Selfrecord
# exit 0
```

Discovery shell commands (exit **0** for each complete invocation):

1. Lane `git rev-parse master`, `git log --oneline -3 master`, and `git ls-tree --name-only HEAD -- corpus/lessons/` piped to `tail -5`; final `echo exit=0`. The latter listed directories, not definitive absence; the requested red establishes absent lesson behavior.
2. Lane `git cat-file -t` on SEALED and BASE; `git cat-file -e HEAD:<path>` for all seven frozen receipt paths; sealed `cat-file -e` for `tools/round69-newest-closure-counter.py` and `corpus/lessons/round-83-verifier-spotcheck.md`; worktree lesson existence `test`; `wc -l tools/round83-selfrecord-round82.py`. Entire invocation exit 0. Individual discovery subcommand statuses were not separately retained; no exact per-subcommand status is asserted. These were discovery only.
3. Lane `git show ae4323171596126a9265f7f6c8af4164d499ba09:SCORECARD.md`, exit 0.
4. Seven chained lane `git show HEAD:<receipt>` commands, all exit 0: round-83 final `c1-legA.out`, `c1-pending.out`, `c1-delta.out`, `c2.out`, `c3.out`, `c3-selftest.out`; round-82 before `c2-late-delta-base.out`.

All lane git invocations used `git -C /home/vgpnk/Projects/shokunin/kama-shokunin`. No git mutation there or in the fleet root. Tool-backed reads/writes are not shell commands and have no process exit code. Fixture subprocess command definitions and their return-code checks are retained in the tool: `git init -q`, root assertion before each mutation, `add -A`, identity-local unsigned `commit -qm fixture`, `reset --hard <fixture-sealed>`; read-only `show`, `rev-parse`, `ls-tree`. Successful fixture mutations exited 0 or the selftest would have aborted; intentionally absent blob `show` failures are mapped to unreadable/missing evidence.

## Contract details and integration

SEALED is `ae4323171596126a9265f7f6c8af4164d499ba09`; correction `at=` is BASE `aca4f33ac1e2a8cf815d97daab3b3a5cfa0d78e0`, explicitly different per frozen plan. Reads use committed HEAD, not master or worktree. Baseline witnesses at BASE prevent tip receipt rewriting from converting a frozen stale fact into a hold. F8 uses the round-69 date/round-order rule over committed closures since round 63.

F2 serializes the two coupled values as one no-whitespace token:
`r83c1-window=8,r83c1-falls=yes` → `r83c1-window=7,r83c1-falls=no`.
The whole comma-joined new token must occur in the named fix file outside excluded restatements.

**Explicit L1-directed formatting divergence:** frozen table abbreviates F3's disposition to `r83c1-delta=113/103/10`. L1 requested binding its bad count too; tool uses `r83c1-delta=123/103/20/0` → `r83c1-delta=113/103/10/10`. Frozen plan was not edited. Scribe `SCR01LessonSources` was notified of F2/F3 exact serialization.

Remaining stale tokens: `r83c1-late=23` → `r83c1-late=22`; `r82c2-new=0` → `r82c2-new=15`; `r83c3-selftest=11` → `r83c3-selftest=14`; `r83-closure=round-82-verifier-spotcheck.md` → `r83-closure=round-83-verifier-spotcheck.md`. Holds have no correction lines. Fix paths cannot be lessons, absolute paths, or traverse `..`.

Integrate the tool and six lesson corrections plus non-restatement fix occurrences, then parent runs the frozen C2 predicate and selftest. This seat did not run a production-green C2 tree or full gate. No build/lint/formatter was run. No tools installed or updated. LSP tools are not exposed in this seat's inventory; architecture discovery used textual reads, not an empty LSP response.

## Self-evaluation

Accuracy 4/5: final red and 16 fixtures retained; full integrated green remains parent-owned. Completeness 4/5: required implementation/receipts delivered, global gate deliberately unrun. Clarity 4/5: exact serialization documented, F3 requires explicit divergence disclosure. Actionability 4/5: integration target and commands supplied; parent must land lesson/fix bytes. Conciseness 4/5: command accounting makes this handoff longer. Overall 4.0/5. Highest-impact parent check: confirm integrated six correction tokens exactly match final fact lines; retain F3 divergence. User agreement expected given explicit evidence and limits.
