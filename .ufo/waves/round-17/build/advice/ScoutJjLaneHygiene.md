VERDICT: n/a — read-only lane-hygiene census; all four asked items answered from observed git/metadata evidence, no gate graded.

# ScoutJjLaneHygiene — untracked/ignored runtime files, .gitignore, lock/state ignore status, jj-audit debt

Snapshot 2026-10-20T12:19:48-03:00, lane root `/home/vgpnk/Projects/shokunin/kama-shokunin`.
Lane tip `master` = `cff9e62f05aa7cfb9059444f62eb787100719713` (`git rev-parse master`); `HEAD` is detached at the same hash (`.git/HEAD` holds the bare hash; `git symbolic-ref -q HEAD` exits 1). Per the lane contract the tip is `master`, not `HEAD`.

## 1. Modified / untracked / ignored

Tracked modifications at the snapshot (uncommitted): `.gitignore`, `AGENTS.md` — `git diff --stat` = `2 files changed, 2 insertions(+)`.
Post-snapshot (later read, ~12:21): sibling seats added worktree edits — `.ufo/waves/round-13/measure.py`, `tests/llamacpp-live/check-receipt.py`, `tests/probe-verdicts/check.py` — `git diff --stat` = `5 files changed, 183 insertions(+), 21 deletions(-)`; at that moment the round-13 diff was docstring-only (no hunk touches `worktree_matches_head` or the exit map code).

Untracked (`git status --porcelain --untracked-files=all | grep '^??'`), 18 paths at the first read → 29 → 56 at 12:19:48 while sibling seats wrote:

- `.ufo/waves/round-17/build/**` — 46 files: `dispatch.json`, `spec.json`, `spawn-result.json` (443,487 B, largest), `make_spec.py` (55,226 B), `record.stdout`, `dispatch.exit`, `dispatch.stderr`, `validation.json`, `attempts.json`, `assignments.json`, `advice/**`, `drafts/**`, `swarm-registry.json`.
- `.ufo/waves/round-17/frozen/**` — 6 files: `manifest.json`, `round-13_measure.py`, `tests_probe-verdicts_check.py`, `tests_llamacpp-live_check-receipt.py`, `tools_kama-llamacpp-live.py`, `tools_kama-probe.sh`.
- `.ufo/waves/round-17/sources-before-validate.txt`.
- `tools/sources-append-only.py` (another seat's new tool) and `tools/__pycache__/sources-append-only.cpython-314.pyc`.

No `.ufo/waves/**` path is ignored: the root `.gitignore` only covers two `.ufo/` subtrees (§2).

Ignored, excluding interactive-sessions content (top-level ignored dir name only as instructed):

- `!! .jj/` — 59 files at file granularity (`git status --porcelain --ignored --untracked-files=all | grep -c '^!! \.jj/'` → 59); `.jj/.gitignore` is `/*`.
- `!! registry/history/.lock` and two dated snapshots `20261014T124232Z.json`, `20261014T124525Z.json`.
- `.ufo/interactive-sessions/` exists as a top-level dir and is ignored by `.gitignore:1`; its content was not listed (privacy bound).

## 2. Current .gitignore

`.gitignore:1-2`:

```
.ufo/interactive-sessions/
.ufo/state/
```

Line 2 is **uncommitted**: `git show master:.gitignore` returns the single line `.ufo/interactive-sessions/`; `git diff -- .gitignore` shows `+.ufo/state/` only.

## 3. `registry/history/.lock` — ignored, not tracked

- `git check-ignore -v --no-index registry/history/.lock` → `registry/history/.gitignore:3:.lock	registry/history/.lock`.
- `git ls-files --error-unmatch registry/history/.lock` → `error: pathspec 'registry/history/.lock' did not match any file(s) known to git`.
- Present: 0 bytes, mode 0600, mtime 2026-10-14 09:45.
- Whole directory: tracked = `.gitignore`, `DELTA.md`, `latest.tsv` (`git ls-files registry/history`); ignored = `.lock` plus the two dated `*.json` via `registry/history/.gitignore:2:*.json` (`# Dated snapshots are local run evidence; the normalized baseline and ledger are tracked.`).

Consequence: `JjTrialKama.md:113` asked to add `.lock` "currently protected only by pathspec discipline", but a **tracked** nested rule already ignores it; that half of the recommendation is stale, not outstanding.

## 4. `.ufo/state/` — ignored only by the uncommitted rule, not tracked, absent

- `git check-ignore -v --no-index .ufo/state/scratch.txt` → `.gitignore:2:.ufo/state/`.
- `git ls-files .ufo/state` → empty; `ls -ld .ufo/state` → `No such file or directory`.
- Because `master:.gitignore` lacks the line, the protection lives only in the worktree copy until `.gitignore` is committed. The `.ufo/state/` never-commit invariant from `JjAuditKama.md` §4 holds today only by absence (no such dir) plus an unlanded rule.

## 5. jj-audit recommendations still unimplemented

### JjAuditKama.md §6 (`/home/vgpnk/Projects/shokunin/.ufo/waves/hyaku/jj-w1/reports/JjAuditKama.md:178-183`)

| # | Recommendation (line) | Status | Evidence |
|---|---|---|---|
| 1 | Leave nine named-gate git reads (178) | HELD | `git log 726f737..master` = 2 commits (`ccc4bb3`, `cff9e62`) touching neither `tools/`, `tests/`, `.ufo/waves/round-12`, `.ufo/waves/round-13` nor `.ufo/waves/round-16/measure.py`; cited sites still match: `.ufo/waves/round-12/fidelity.py:115` `git_run(repo, 'rev-parse', '--show-toplevel')`, `.ufo/waves/round-13/measure.py:295` `oid = git_read(['rev-parse', 'HEAD'], commands)...`, `:385` `git_read(['cat-file', 'blob', f'{head}:{QUALITY_GIT_PATH}'], commands)`, `.ufo/waves/round-16/measure.py:116`. |
| 2 | Enforce helper `commit` → round-13 live (179) | **NOT IMPLEMENTED as a lane rule; code fix in flight, uncommitted** | `SKILL.md:411-445` (round-13 section) contains no ordering rule; the only written statement is the round-13 artifact `.ufo/waves/round-13/advice/SafetyPaths.md:27` "L1 must commit before the live run." The new `AGENTS.md:6` covers only "Gates that need git writes run in a `/tmp` clone." Hazard intact in `master`: `.ufo/waves/round-13/measure.py:446` `if not worktree_matches_head:` maps an uncommitted QUALITY.md to exit 1 `documentation_mismatch`. Post-snapshot a sibling added docstring text to that file announcing exit 4 `worktree_not_at_measured_revision` ("A real content or integrity failure still exits 1 even when the worktree diverges."), but the executable hunks at read time were docstring-only. |
| 3 | Use branch refs, never `HEAD`/`@{u}`/`--abbrev-ref`/`--show-current` (180) | IMPLEMENTED, UNCOMMITTED (doc only) | `AGENTS.md:6` "never `@{u}`, `--abbrev-ref HEAD` or `branch --show-current`". No lane script uses those tokens (grep over tools/, tests/, root, excluding `.ufo`, `.git`, `.jj`). Residual: five old lessons still prescribe `@{u}..HEAD` — `corpus/lessons/round-11-verifier-spotcheck.md:44`, `round-12:31`, `round-13:39`, `round-14:32`, `round-15:33`; observed now: `git rev-parse '@{u}'` → `fatal: HEAD does not point to a branch`, exit 128 (old lessons may not be edited). |
| 4 | No `.gitattributes` filters/eol, no git hooks expected to fire (181) | SATISFIED | `ls .gitattributes` → `No such file or directory`; `ls .git/hooks \| grep -v '\.sample$'` empty; `AGENTS.md:6` "jj ignores git hooks and `.gitattributes` eol/filters: add neither expecting them to fire." |
| 5 | `jj file track` for every new path + non-empty commit (182) | IMPLEMENTED pre-commit; post-commit assertion absent | `/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh:210` `"$JJ_BIN" file track --include-ignored -- "${files[@]}"`, `:214` (dirs), `:218-219` `if [ -z "$("$JJ_BIN" diff --summary -- ...)" ]; then echo "nothing to commit"`. No `jj diff --summary -r <hash>` check after `commit`. |
| 6 | `round-16/measure.py:116` parity: `--no-replace-objects` + `GIT_*` scrub (183) | **NOT IMPLEMENTED** | `.ufo/waves/round-16/measure.py:116` is `["git", "-C", str(LANE), "cat-file", "blob", spec],` — the only git call in that file; contrast `.ufo/waves/round-13/measure.py:278` `argv = ['git', '--no-pager', '--no-replace-objects', '-C', str(LANE)] + list(args)` with `git_env()` at `:264` stripping `GIT_*`, and `.ufo/waves/round-12/fidelity.py:95` `command = ['git', '--no-pager', '--no-replace-objects']`. |

### JjTrialKama.md §Recommendations (`JjTrialKama.md:112-115`)

| # | Recommendation (line) | Status | Evidence |
|---|---|---|---|
| 1 | Keep helper `init` exactly as-is — `snapshot.auto-track="none()"`, `trunk()=master@origin`, lane identity (112) | **PARTIAL — repo-scope config not persisted** | `.jj` exists (mtime 2026-10-20 11:16) and its op log contains the exact init argv `jj --config 'snapshot.auto-track="none()"' git init --colocate .` plus `bookmark track master@origin`, `metaedit --update-author`, `commit`, `bookmark set master`, `git push`. **No `jj config set` op exists and `.jj/repo/config.toml` is absent** (`find .jj -name 'config*'` → only `.jj/repo/config-id`), although helper init persists four repo-scope keys at `jj-lane.sh:152-155` (auto-track, `user.name`, `user.email`, `trunk()`). Sibling lanes `tameshi-shokunin` and `mado-shokunin` show the same absent-config layout, so this is not a jj-0.45.1 path artefact [INFERENCE from layout equality, not from jj output]. |
| 1-effect | Is auto-track actually off today? | Appears off, from some scope | The only working-copy snapshot op is `jj diff --summary -- corpus/lessons/round-16-verifier-spotcheck.md`; after it `git status` still shows `??` for new files and **no intent-to-add `A` entries**, so `none()` is effective from some config scope. Repository scope has no file, so the source is user/global config, which is unreadable under the privacy bound — [INFERENCE]. The lane-local guarantee the helper intends is absent: another HOME/user config reverts to jj's default `all()` (Trial measured 94 phantom adds). `trunk()` revsets would also be unresolved repo-locally [INFERENCE; `jj` was not run per contract]. |
| 2 | Add `.ufo/state/` and `registry/history/.lock` to `kama-shokunin/.gitignore` (113) | PARTIAL / half superseded | `.ufo/state/` present at `.gitignore:2` but uncommitted; `.lock` needs nothing — already ignored by tracked `registry/history/.gitignore:3` (and `*.json` at `:2`). |
| 3 | Document VCS rules in lane AGENTS.md (114) | IMPLEMENTED IN WORKTREE, UNCOMMITTED | `AGENTS.md:6` is the new paragraph; `git diff -- AGENTS.md` shows a single added line (`+ VCS (round 17, 2026-10-20): this repo is jj-colocated...`). Nothing in `master` has it. |
| 4 | No `snapshot.max-new-file-size` override (115) | SATISFIED vacuously | No repo config file exists at all, so no override; largest untracked file today `spawn-result.json` 443,487 B < 1 MiB default, and helper files are tracked with `--include-ignored` anyway. |

## 6. Adjacent hygiene facts that bear on the next commit

- `tools/__pycache__/sources-append-only.cpython-314.pyc` is untracked and **not ignored** (`git check-ignore` exits 1). The helper's directory mode tracks like `git add <dir>`, so naming `tools/` as a commit path would sweep the `.pyc` in; commit explicit file paths (the helper already prefers them) or add a `__pycache__/`/`*.pyc` rule. No `.pyc` is tracked today (`git ls-files | grep -c '\.pyc$'` → 0).
- The two jj-readiness edits (`.gitignore:2`, `AGENTS.md:6`) are worktree-only; if L1 commits round-17 artifacts without them, both the `.ufo/state/` guard and the VCS instructions stay unlanded and the lane's repo config remains absent.
- `.ufo/waves/round-17/**` will need `jj file track` for every file; the helper does this automatically for explicitly named existing paths (`jj-lane.sh:210`), including oversize ones.
- HEAD/`master` both resolve to `cff9e62…`, so the detached state is *at the tip*, not ahead: a round-13 live run right now would still fail on any uncommitted QUALITY.md edit, not on HEAD drift.

## 7. Limitations

- `jj` was not executed anywhere in the lane (lane contract), so "auto-track effective" is inferred from the recorded op log plus the absence of intent-to-add entries; a user-scope `snapshot.auto-track="none()"` could not be read (`~/.config` is privacy-bounded).
- Counts are a timestamped snapshot of a live build wave: untracked went 18 → 29 → 56 during this read; the per-directory tally (55) and the count (56) differ by one file written between two commands seconds apart.
- The round-16 unguarded `cat-file` and the round-13 ordering hazard were not executed; status is code-level, matching the audit's own read-only mandate.
- The lane is being edited concurrently by sibling seats; observations are timestamped and later reads showed new tracked modifications (§1). An in-flight round-13 docstring edit advertises exit 4 but its code had not changed when read.
- No gate, mutant runner or control suite was run (measurements belong to L1).

## 8. Tool installs

None. No package, binary or config was installed or modified; only this Report was written.
