source: S545 — Git `gitmodules(5)`, https://git-scm.com/docs/gitmodules, §`submodule.<name>.ignore` (docs, tier A, mined, accessed 2026-11-03; row in `corpus/SOURCES.md`): "`all` makes the submodule never considered modified while it can still be staged" — the value the `submodule` case must not be defeated by. `plans/round-73-claims.md` §C1 (frozen predicate, fixed case population, survivor classes A5/A6/A7); `tools/round73-round-scope-cases.py` (v2 counter) over the byte-frozen base `tools/round72-round-scope.py`.
verified-at: bc9e3059 — plan §C1, the base counter's `_label_findings`/`_stray_findings`/`_ignored_findings` at that revision, the committed fixtures `.ufo/waves/round-73/controls/build-survivors.py`, and the pre-freeze receipt `.ufo/waves/round-73/measured/before/score-survivors-base.out` (read, not re-run: three `BASE_C1 ... exit=0 verdict=GREEN` lines; `SURVIVORS c1 base_green=3 v2_killed=0 v2=absent`). No v2 run is claimed here.
recheck: `python3 tools/round73-round-scope-cases.py --repo . --round 73 --tip master`

# Round-scope survivor cases — the three classes the r72 counter accepted

Round 72 claimed its pre-report cleanliness arm "cannot be satisfied vacuously". Its own closure
recorded three classes that pass it anyway — A5 linked worktree, A6 a valid older-round label
hiding another round's ignored work, A7 `submodule.<name>.ignore=all`. Round 73 keeps the three
inherited cases and adds one case per survivor; the base tool's bytes stay unchanged and its
graders are imported, not copied.

## The three survivors

| Survivor | Why the base counter passes it | Fixture (`.ufo/waves/round-73/controls/build-survivors.py`) | v2 case and the command it runs |
|---|---|---|---|
| A5 linked worktree | `stray` runs `git status --porcelain -uall` in the primary worktree; a linked worktree is a separate working tree, so its dirt never appears there | `c1_a5`: `git worktree add -q --detach <wt>`, then edit `<wt>/LOG.md` and add `<wt>/stray-in-wt.txt` | `worktree`: `git worktree list --porcelain`, then `git -C <path> status --porcelain -uall` for every path but the resolved primary; records graded like `stray` against `--allow`; an unreadable worktree is a finding |
| A6 valid older label hides newer ignored work | `ignored` runs `git status --porcelain -uall --ignored -- .ufo/waves/round-<N>` with `N` from `--round`; a valid `--round 71` never reaches `round-72`'s pathspec | `c1_a6e`: seed plan for round 71 (valid heading), then `.ufo/waves/round-72/hidden.log` (the seed `.gitignore` holds `*.log`) | `ignored-older-label`: enumerate `.ufo/waves/round-<M>` directories present with `M >= N` (parse the name, skip non-parsing), run `git status --porcelain -uall --ignored -- <dir>` per directory; every `!!` record is a finding |
| A7 `submodule.<name>.ignore=all` | the parent `git status --porcelain -uall` honours `.gitmodules` `ignore=all`, so a dirty submodule reads clean | `c1_a7sub2`: `git -c protocol.file.allow=always submodule add` a scratch repo at `sub`; `git config -f .gitmodules submodule.sub.ignore all`; commit; edit `sub/child.txt`, add `sub/leak.txt` | `submodule`: `git config -f .gitmodules --get-regexp path`, then `git -C <path> status --porcelain -uall` per existing worktree; plus parent `git status --porcelain -uall --ignore-submodules=none`, each record a finding naming the submodule path |

The v2 verdict is one line, `ROUND_SCOPE_V2 round=<N> cases=6 findings=<f>`; exit 0 clean, 1
findings, 2 could-not-evaluate (a scored run never exits 2 for a finding). Findings print as
`ROUND_SCOPE_V2_FINDING <case> <detail>`; the case population and its order are fixed:
`label, stray, ignored, worktree, ignored-older-label, submodule`.

## The `M >= N` bound

The `ignored-older-label` population is every `.ufo/waves/round-<M>` directory present in the
worktree with `M >= N`, where `N` is the `--round` argument. The bound is directional on purpose:

- The round's own dir (`M = N`) is always in, so the inherited `ignored` case is a subset of it.
- Later rounds (`M > N`) are in, which closes A6: a valid older label no longer hides a newer
  round's ignored work.
- Older rounds (`M < N`) are out. The lane's committed-then-ignored leftovers (`__pycache__/*.pyc`)
  live there; they belong to an older round's record, and no current round can clean them without
  rewriting it. Grading them would make the arm permanently red for a reason outside every round's
  authority. This is the plan's stated exclusion, not a convenience.

## Limits

- **No `--allow-ignored` escape.** The plan's non-goal: a round that needs an ignored file under
  its own wave dir declares it in `claims.md` first; `ignored` and `ignored-older-label` take no
  allow list. `--allow` reaches `stray` and `worktree` only.
- **An uninitialised submodule is skipped**, named in the output, not graded: a path from
  `.gitmodules` with no worktree directory has no status to read. A path whose directory exists
  but whose `git -C` fails is a finding, never a pass.
- **Git state only.** The cases grade uncommitted and ignored paths, not committed content and not
  whether a receipt is true (that is `receipt-tip-binding.md`). Plan non-goal: no product or
  serving claim.
- **A red fixture proves the counter, not the lane.** The survivor fixtures are the kill rule; the
  lane's own `--round 73` run is the evidence the lane is clean, and it must exit 0.
- **The r72 red pairs stay red.** The inherited cases keep their r72 kill fixtures; the new cases
  add survivors, they do not relax the old ones.

## Control and after-measurement

The pre-freeze control ran the byte-frozen base counter over the same three fixtures: `BASE_C1`
all `exit=0 verdict=GREEN` and `SURVIVORS c1 base_green=3 v2_killed=0 v2=absent`
(`.ufo/waves/round-73/measured/before/score-survivors-base.out`). It cannot satisfy the target, so
the target is not reachable by doing nothing; the after run is the same scorer with the v2 tool
present.

## L1 implementation correction — round 73

CRT01's F3 counterexamples exposed two incomplete enumerations in the first implementation.
The final module recursively visits initialized nested submodule worktrees and enumerates the
`M >= N` ignored-wave population in every linked worktree as well as the primary. The predicate
and six-case population are unchanged. The committed replay-f3.sh under CRT01ClaimCritic's wave
directory rebuilds both counterexamples; both final invocations exit 1 with the named finding.
The scorer's exit 0 alone is never target evidence: require its `v2=present`, `v2_killed=3`
and `clean=green` fields plus the direct module verdict and module digest.
