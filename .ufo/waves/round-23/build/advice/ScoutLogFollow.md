# ScoutLogFollow — repo-local `log.follow` vs `report_cutoff()` (round 23, C1 calibration)

Seat: `CloseKama22.ScoutLogFollow` (leaf, no dispatch). Scope: ONE repo-local state channel —
`log.follow` × `git log --diff-filter=A` with a single pathspec — in
`tools/report-landing-audit.py` at base `master=4fe9339f8fc3a4a4a479d9c938a850da12f1124d`
(git 2.56.0). Base was audited from the **HEAD blob**, not the working tree: the lane checkout's
`tools/report-landing-audit.py` is modified (`git status --porcelain` → ` M`) and already contains
`GIT_ISOLATION` with `-c log.follow=false`; `git show HEAD:tools/report-landing-audit.py | grep -c log.follow` → `0`.

## 1. Verdict

**affects-verdict** — a repo-local `log.follow=true` flips a `failed` audit to a false `clean`
(exit 1 → 0, `landed-omitted` defect disappears). Not "crashes" and not "executes" for valid
boolean values. `-c log.follow=false` restores the default exactly (verified end-to-end).
Separate, pre-existing channel: a malformed boolean (`log.follow=maybe`) is a typed refusal
(exit 2, `EvalError`) at base and **`-c log.follow=false` does not cure it** (§7).

Fault conditions, both required:
1. `$GIT_DIR/config` (or `$GIT_DIR/config.worktree`) sets `log.follow=true`. `git_env()`
   (`tools/report-landing-audit.py:79-85` base) only sets `GIT_CONFIG_GLOBAL=/dev/null` and
   `GIT_CONFIG_NOSYSTEM=1`; repository-local config is still read, despite the docstring claim
   that "neither the audited repos ... can be redirected" (base `:80-81`).
2. The report path was created by a rename that `--follow` can detect (default rename
   similarity; a pure `git mv` or small edit qualifies, a full rewrite does not — §5).

## 2. Mechanism in the audited code (base blob 4fe9339f)

- `tools/report-landing-audit.py:165-168` — `report_cutoff()`:
  `git(fleet_repo, "log", "--diff-filter=A", "--format=%at", "--", rel).split()` then
  `int(out[-1])`. `git log` is newest-first, so `out[-1]` is the **oldest** add commit of `rel`.
- `:286-287` — `pre = [c for c in commits if c["atime"] <= cutoff]`,
  `post = [... > cutoff]`; `:302` emits `landed-omitted` for each uncited `pre` commit.
- `:87-95` — `git()` runs plain `git -C <repo> <args>` with `text=True`; no `-c` isolation at base.
- Only `report_cutoff` uses a path-limited log. `round_commits` (`:147-150`) calls
  `git log --format=... branch` with **no** pathspec; no other subcommand is path-limited
  (`show` `:266`, `ls-tree` `:211`, `cat-file` `:222`, `rev-parse` `:403-404`).

With `log.follow=true`, git behaves as if `--follow` was given (single path), traverses the
rename, and the oldest `--diff-filter=A` commit becomes the **pre-rename creation** commit —
earlier than the rename that actually landed the report. `cutoff` moves earlier by the
rename interval; lane commits in that interval move from `pre` (required to be cited) to
`post` (ignored), so genuine omissions disappear. In my fixture the rename commit itself was
not emitted under `--follow`; either way `out[-1]` is the pre-rename timestamp.

## 3. Reproduction (fresh temp repos; `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`)

Fixture (`/tmp/kama-r23-logfollow/{lane,fleet}`, script `/tmp/kama-r23-logfollow/probe2.sh`):
fleet: root commit adds `reports/old-name.md` at `1700000000` (T0), filler at `+600`, then
`git mv` to `.ufo/reports/round-7/kama.md` at `1700003600` (T1). Lane: one `round-7:` commit
authored `kama-shokunin` at `1700001800` (Tmid), uncited in the report's `## Landed changes`.
Audit invocation (base = HEAD bytes saved as `/tmp/kama-r23-logfollow/audit-base.py`):

```
python3 audit-base.py --lane-repo .../lane --fleet-repo .../fleet \
    --branch master --lane kama --rounds 7 --no-errata --json
```

| fleet `$GIT_DIR/config` | `report_cutoff` | defect | summary | exit |
|---|---|---|---|---|
| `log.follow` unset | `1700003600` | `landed-omitted 8fffffab…` | `required_commits=1 defects=1 status=failed` | **1** |
| `log.follow=true` (repo-local) | `1700000000` | none | `required_commits=0 defects=0 status=clean`, `post_report=["8fffffab…"]` | **0** |
| `log.follow=true` + `-c log.follow=false` (only patch; see §4) | `1700003600` | `landed-omitted 8fffffab…` | `status=failed` | **1** |

Raw git in the same repo:

```
$ git log --diff-filter=A --format='%h %at %s' -- .ufo/reports/round-7/kama.md
b42e0ce 1700003600 land round-7 report

$ git config log.follow true
$ git log --diff-filter=A --format='%h %at %s' -- .ufo/reports/round-7/kama.md
69bfdb7 1700000000 draft report

$ git -c log.follow=false log --diff-filter=A --format='%h %at %s' -- .ufo/reports/round-7/kama.md
b42e0ce 1700003600 land round-7 report

$ git log --no-follow --diff-filter=A --format='%h %at %s' -- .ufo/reports/round-7/kama.md
b42e0ce 1700003600 land round-7 report
```

The audit's unset run reproduces the correct failure (report landed at T1, after the Tmid
round commit, which is not cited); the `log.follow=true` run reproduces the false clean.

## 4. `-c log.follow=false` restores the default

Verified two ways: the raw commands above, and an on-disk copy of the base script whose only
edit was `["git", "-C", str(repo)` → `["git", "-c", "log.follow=false", "-C", str(repo)`
(producing `/tmp/kama-r23-logfollow/audit-fix.py`; the working-tree candidate's
`GIT_ISOLATION` is the same clause in git-global position). With repo-local `log.follow=true`
that patch returns `cutoff=1700003600`, `landed-omitted`, `status=failed`, exit 1 — the unset
control byte-for-byte.

Placement matters: `-c` is a git-global option and must precede `-C`/the subcommand. A
mis-ordered helper of mine (`git log ... -c log.follow=false ...`) produced
`fatal: bad revision 'log.follow=false'` (exit 128) — that was my bug, not an audit behavior,
but it shows the clause cannot be appended after `log`. `--no-follow` (explicit negation) also
restores the default (`exit=0`), so `-c log.follow=false` is not the only channel; it is the
one that survives the generic `git()` wrapper.

## 5. Boundaries (when it does NOT change the first-add commit)

- Plain add at the final path (no rename): control file `.ufo/reports/round-7/other.md` added at
  T1 → `1700003600` under both unset and `log.follow=true`.
- Delete then re-add of the same path: outputs identical both ways —
  `21f49cf 1700003000 readd` and `e7f9931 1700001000 add1`; `out[-1]` stays `1700001000`.
  No opposite-direction (later-cutoff) flip found in this shape.
- Rename not detected: with every line rewritten at rename time, `-M` reports
  `A d/new.md` / `D d/old.md` (no R), and both configs return the rename commit `1700000900`.
  With a one-line append, `-M` reports `R099` and follow returns the pre-rename `1700000500`.
  So the fault needs `--follow`-visible rename similarity (git's default 50% threshold).
- Worktree scope: `git config extensions.worktreeConfig true; git config --worktree log.follow true`
  also flips (`1700000500` under follow vs `1700000900` default); `-c log.follow=false` overrides.
- No collateral: `git log --format=%H master` (round_commits shape) is byte-identical under
  `log.follow=true` (`cmp` → `IDENTICAL`, exit 0); `git show HEAD:<report>` sha256 identical
  (`751b95a3…`). `-c log.follow=false` cannot break these (log without a path ignores it).

## 6. Real-history status: latent, not live

- `log.follow` unset: lane `git config --local --get log.follow` → unset; fleet
  (`/home/vgpnk/Projects/shokunin/.git`) → unset.
- All 20 committed `.ufo/reports/round-*/kama.md` paths in the fleet repo give **identical**
  `--diff-filter=A` cutoffs under `-c log.follow=false` vs `-c log.follow=true`
  (rounds 1,2,4,6–22; e.g. round-22 `1792593755`). No historical verdict is changed today.
- Base selftest cannot catch the channel: the base blob contains zero `log.follow` matches and
  no `git mv`/rename of report paths (fixtures use plain `_commit` adds in fresh repos), so the
  clause is inert for the existing 50/50 selftest. I did **not** run the selftest.

## 7. Malformed boolean — separate, unchanged by `-c`

`git config log.follow maybe` then `git log --diff-filter=A ... -- path` →
`fatal: bad boolean config value 'maybe' for 'log.follow'`, rc 128. `git show HEAD:<report>`
also dies (rc 128), and `-c log.follow=false` **does not** cure it (git validates the local
value even when overridden), nor does `--no-follow`. Base audit outcome: exit **2**,
`could-not-evaluate: round 7: .ufo/reports/round-7/kama.md not committed in fleet HEAD`
(the `EvalError` wrapper around `git show`, base `:266`). That is already a typed refusal, not
a traceback and not a verdict; the candidate clause leaves it at exit 2. If L1 wants this
channel gone it needs a different mechanism (e.g. a dedicated config file/-c-only invocation
still cannot mask an invalid local boolean; only telling git not to read local config could).

## 8. Documentation (all accessed 2026-10-21, git-scm.com, 2.56.0)

- `log.follow` — https://git-scm.com/docs/git-config#Documentation/git-config.txt-logfollow
  (reader lines 5750-5754). Quote (19 words): "If `true`, `git` `log` will act as if the
  `--follow` option was used when a single <path> is given." Followed by: "This has the same
  limitations as `--follow`, i.e. it cannot be used to follow multiple files."
- `--follow` — https://git-scm.com/docs/git-log#Documentation/git-log.txt---follow
  (lines 320-323). Quote (15 words): "Continue listing the history of a file beyond renames
  (works only for a single file)." The page's own example (lines 3340-3343) says it shows
  commits "including those commits that occurred before the file was given its current name" —
  exactly the cutoff shift observed.
- Config scopes/precedence — https://git-scm.com/docs/git-config#SCOPES (lines 768-790):
  `local` = `$GIT_DIR/config`; `command` = GIT_CONFIG_{COUNT,KEY,VALUE} env + "the `-c` option";
  §FILES (lines 730-751): repo config is read and "The files are read in the order given above,
  with last value found taking precedence over values read earlier."
- `git -c` — https://git-scm.com/docs/git (lines 346-348). Quote (16 words): "Pass a
  configuration parameter to the command. The value given will override values from
  configuration files."

## 9. What I did NOT verify

- Did not run the base or candidate selftest; the "50/50 unchanged" claim rests on source
  inspection (no `log.follow`, no rename fixtures), not execution.
- Did not test non-linear/merge history (`--follow` "does not work well on non-linear history");
  my fixtures are linear.
- Did not test `--follow` with multiple pathspecs (audit passes one).
- Did not test other git versions; all observations are git 2.56.0 on this host.
- Did not run the audit against the real lane/fleet repos (read-only `git config`/`git log`
  queries only, per bounds). No installs or upgrades were needed or performed.
- Did not test whether a real renamed-round report could arrive by merge; none exists today.

## 10. Files written

- `.ufo/waves/round-23/build/advice/ScoutLogFollow.md` (this report; append-only).
- Scratch only, outside the lane: `/tmp/kama-r23-logfollow/probe.sh`,
  `/tmp/kama-r23-logfollow/probe2.sh`, `/tmp/kama-r23-logfollow/audit-base.py`,
  `/tmp/kama-r23-logfollow/audit-fix.py`, and fixture repos under `/tmp/kama-r23-logfollow/`.
- No lane file, no out/ artifact, no registry/lesson write.
