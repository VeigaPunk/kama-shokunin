# Row F12-tag-shadows-branch — independent hand rebuild

**Verdict: HOLDS as graded; PARTIAL as a closed channel.**
The fault premise is real and reproduces on the frozen arm (flip to a clean
verdict); the graded expectation (exit 1, `landed-omitted`) is the correct
substantive verdict, established by a no-tag counterfactual, not merely by
current's output. But the same tag-over-branch substitution still happens on
the fallback path of `resolve_branch` when `refs/heads/<name>` **exists but
cannot be peeled**: adding a same-named tag flips a refusal (exit 2) into a
clean verdict (exit 0), and can manufacture a `landed-omitted` defect from the
tag's history. That variant is ungraded and has no mutant.

Base `245a37f69628c2c6bb29bbf17897d8fb5946c857`. Clone
`/tmp/kama-r23w2/RowF12TagShadows-2` HEAD verified equal. Auditor blobs:
current `f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7`;
frozen `09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f`
(extracted from `4fe9339…:tools/report-landing-audit.py`). Runtime: git 2.56.0,
CPython 3.14.8. No installs or upgrades were needed or made.

## 1. Premise and frozen arm — observed

The fixture was rebuilt by hand from `tests/report-audit/repo-state-grid.py:363-367`
(`f_tag_shadow`), **not** by importing the grid: lane `master` has
`round-1: work` @1000 (A) then `round-1: more` @1500 (B), both author
`kama-shokunin`; fleet `HEAD` has `.ufo/reports/round-1/kama.md` @2000 citing
only A; then `git tag master A` (row declared at `:553`; pass condition
`:627-630`).

Observed with git 2.56.0 in that repository:

```
refs/heads/master   rev-list --count = 2   (round-1: more, round-1: work)
refs/tags/master    rev-list --count = 1   (round-1: work)
master              rev-list --count = 1   stderr: warning: refname 'master' is ambiguous.
```

Hand run of both arms (`--branch master --rounds 1 --no-errata --json`):
frozen **exit=0, defects=[], round_commits=1, required=1** (NOT-MET);
current **exit=1, kinds=[landed-omitted], round_commits=2, required=2** (met).
No traceback, no hang, no execution.

Grid cross-check on the clone:

```
$ python3 tests/report-audit/repo-state-grid.py --case F12-tag-shadows-branch --arm both
frozen F12-tag-shadows-branch fault exit=0 kinds=[] tb=0 exec=0 timeout=0 NOT-MET
current F12-tag-shadows-branch fault exit=1 kinds=['landed-omitted'] tb=0 exec=0 timeout=0 met
grid-exit=1
```

Frozen cause: `git(lane_repo, "rev-parse", "--verify", f"{args.branch}^{{commit}}")`
at frozen line 403, and `args.branch` is passed to `load_source_urls` and
`audit_round` at frozen lines 405-406 (log, `ls-tree`, `show` all resolve the
unqualified name, i.e. the tag). Current pins the tip once at
`tools/report-landing-audit.py:477` via `resolve_branch`
(`:451-459`), whose first attempt is `refs/heads/<name>^{commit}`.

## 2. Is the expected outcome correct? — yes (observed counterfactual)

The same fixture **with the tag removed** gives, on both arms:
`exit=1, kinds=[landed-omitted], round_commits=2`. The tag does not change the
branch's history, so the truthful verdict for the repository is exit 1 with
`landed-omitted`; that is exactly the graded expectation. A refusal
(exit 2, "refname is ambiguous") would also avoid a flip under C1's minimum,
but would be the weaker answer: the branch is an unambiguous subject, and the
row's own premise names the branch as the subject. [INFERENCE] The expectation
is therefore correct, and stricter than a mere "don't flip" check.

Mirror-sign check (branch clean, `tag master` → a parentless commit whose
subject is `round-1: orphan`): frozen **exit=1 `landed-omitted`** (false
defect), current **exit=0**. Current resists the flip in both directions.

## 3. Near variant current still gets wrong — yes

`except EvalError` at `tools/report-landing-audit.py:457` cannot distinguish
"branch absent" (fallback intended by the docstring at `:452-453`, "other
revisions as given") from "branch ref exists but is unreadable or does not
peel to a commit". In both cases it falls back to `{branch}^{commit}`, and
git's unqualified precedence resolves `refs/tags/<branch>` ahead of
`refs/heads/<branch>`.

Hand-built pairs; "control" is the identical fixture with no tag, "with tag"
adds `tag master A`:

| case | control (current) | with tag (current) | frozen with tag |
|---|---|---|---|
| `refs/heads/master` → tree object (V10/C10) | exit=2 `fatal: Needed a single revision` | **exit=0, [], round_commits=1** | exit=0 |
| `refs/heads/master` → missing object `000…0` (V11/C11) | exit=2 | **exit=0, [], 1** | exit=0 |
| `refs/heads/master` dangling symref → `refs/heads/gone` (V4/CV4) | exit=2 | **exit=0, [], 1** | exit=0 |
| branch absent (renamed `main`), tag `master` (V3/CV3) | exit=2 | **exit=0, [], 1** | exit=0 |
| branch absent, `refs/remotes/master` (V13/CV13) | exit=2 | **exit=0, [], 1** | exit=0 |

Fabricated-defect sign: dangling branch symref plus `tag master` → a
parentless commit subject `round-1: orphan` (V9/CV9): control exit=2; current
**exit=1 `landed-omitted`, round_commits=1** — a defect assessed on the tag's
history while the branch resolves to nothing. git's own stderr on the
fallback: `warning: ignoring dangling symref refs/heads/master`, then the tag
resolves successfully.

Why this is wrong, not a design choice: for V4/V10/V11 the branch ref
**exists**; the repository is broken and the truthful outcome is refusal. For
V9 the verdict is computed from a ref the operator did not name. Every row
above changes outcome solely by adding a tag, which is the C1 flip class F12
claims to close. The grid's `M18-branch-heads` mutant
(`tests/report-audit/isolation-mutants.py:53-54`) only rewrites the first
`refs/heads/…` expression; nothing mutates or grades the fallback.

Boundary I do **not** claim as a bug: V3/V5/V13 are consistent with the
docstring's "other revisions as given" (a plain name absent as a branch may
legitimately resolve to a tag or remote ref). The distinction that matters is
the existing-but-unpeelable branch ref (V4/V10/V11), where the branch is
present and then shadowed.

[INFERENCE] Repair direction for L1 (not implemented): after the first
failure, probe whether the branch ref exists (`git show-ref --verify --quiet
refs/heads/<name>`, or `rev-parse --symbolic-full-name`); if it exists and
does not peel to a commit, refuse instead of falling back. Restrict the
unqualified fallback to syntactically explicit revisions/full refs/hex, or at
minimum refuse when a same-named tag exists alongside an unreadable branch.

## 4. What current gets right on this channel (observed)

- No-tag exact fixture: exit 1 `landed-omitted`, 2 commits, both arms.
- Mirror (clean branch, tag → uncited orphan): frozen false defect, current clean.
- Annotated `tag -a master A`, valid branch (V6): frozen exit 0 flip, current
  exit 1 `landed-omitted` (2 commits).
- `tag master` → blob, valid clean branch (V7): frozen exit 2, current exit 0.
- Tag at branch tip (V8): both exit 1 `landed-omitted`.
- Exact F12 after `git pack-refs --all` (V12): frozen exit 0 NOT-MET, current
  exit 1 met — packing does not restore the shadow.

## 5. Not verified

- Whole-grid claims (frozen 0/26 faults and 8/8 controls; current 26/26;
  22/24 mutants with M02/M20 defensive; selftest 50/50; rounds 10–22 ledger
  byte-identity; S089–S095 and lesson text) — outside this slice; only the
  F12 row was run.
- git versions other than 2.56.0 (the declared floor is ≥2.45); tag-before-head
  unqualified precedence on other versions is inference, untested.
- No traceback/hang/program-execution channel is reachable from ref names in
  the fixtures tested; execution paths (F09) were not exercised.
- Proposed repair not implemented or tested; current `--selftest` not run.
- O01/O02, ambiguity overwrite, second Landed section, errata CR: untouched.
- No network fixtures; no URLs cited. `out/` harness copies are archival:
  `build2.py` imports `build.py` from the hardcoded `/tmp/f12-lab` path.

## 6. Files written

- `.ufo/waves/round-23/falsify/advice/RowF12TagShadows.md` (this report)
- `.ufo/waves/round-23/falsify/out/RowF12TagShadows-2/build.py`
- `.ufo/waves/round-23/falsify/out/RowF12TagShadows-2/build2.py`
- `.ufo/waves/round-23/falsify/out/RowF12TagShadows-2/frozen-audit-4fe9339.py`
  (sha256 `09ecd63b…`)
- `.ufo/waves/round-23/falsify/out/RowF12TagShadows-2/run.log`
- scratch outside the lane: `/tmp/kama-r23w2/RowF12TagShadows-2` (clone),
  `/tmp/f12-lab/{frozen-audit.py,build.py,build2.py,fixtures,fixtures2,fixtures3,fixtures4,fixtures5}`

No tracked lane file, index, `.jj`, sibling lane, global config or `~/.omp`
was written; no commits, pushes or jj commands.
