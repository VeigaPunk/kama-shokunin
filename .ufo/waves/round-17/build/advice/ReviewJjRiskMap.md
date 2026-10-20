VERDICT: n/a — risk map, not a claim: R1 is already owned, two recommendations were pre-satisfied (one on a wrong premise), three are fleet-owned, and two need lane action (uncommitted docs, lessons still teaching `@{u}`).

# ReviewJjRiskMap — jj-migration risks for `kama`, decided per item

Read-only seat. No `jj` subcommand, no lane gate, no `make_spec.py`/`mutants.py`/`controls.py` execution.
Sources reviewed: `/home/vgpnk/Projects/shokunin/.ufo/waves/hyaku/jj-w1/reports/JjAuditKama.md` (below "Audit"),
`/home/vgpnk/Projects/shokunin/.ufo/waves/hyaku/jj-w1/reports/JjTrialKama.md` (below "Trial").

## Evidence gathered this seat (read-only, live lane)

- `git symbolic-ref -q HEAD` → exit 1; `git rev-parse HEAD` = `git rev-parse master` = `cff9e62f05aa7cfb9059444f62eb787100719713`.
  **HEAD is detached right now**, so the Audit's F2/R1 premise is live, not hypothetical.
- `git rev-parse '@{u}'` → exit 128 `fatal: HEAD does not point to a branch`; `--abbrev-ref HEAD` prints `HEAD`; `branch --show-current` prints nothing (exit 0).
- `git status --porcelain` → `M .gitignore`, `M AGENTS.md`, `?? .ufo/waves/round-17/`.
- `git check-ignore -v registry/history/.lock .ufo/state/foo` → `registry/history/.gitignore:3:.lock`, `.gitignore:2:.ufo/state/`.
- `.git` is 7.5 MB; `941bb32c…` is a reachable commit and an ancestor of `master`; `git replace -l` = 0, no `.git/refs/replace`.
- No `.gitattributes` outside `.git/.jj`; `.git/hooks` has only `*.sample`; `grep -rn '\bgit\b' tools/ tests/` = no matches.
- `.ufo/waves/round-13/measure.py` diverged from the frozen `2399d64d…` during this review (`git diff --numstat` = `36 7`): docstring, `FINDINGS` exit 4, `LIMITS`, and the live-mode exit-4 branch (`:474-486`); the advertised live-mode sandbox selftest is still absent.
- `git diff --quiet -- corpus/QUALITY.md` → exit 0 (QUALITY.md currently equals HEAD, so R1 has no live exposure today).

## 1. JjAuditKama — each risk / recommendation

| # | Audit item | Decision | Owner / file | Basis |
|---|---|---|---|---|
| R1 | round-13 live gate folds worktree≠HEAD into `clean` | **Fix in lane — already dispatched** | `.ufo/waves/round-13/measure.py`; seat `JjRound13Gate` (`make_spec.py:104-106`: "Own ONLY {LANE}/.ufo/waves/round-13/measure.py") | At review time exit 4 is reachable and the precedence is correct (`run_live` `:474-486`: clean-and-divergent → 4, any other failure → 1). Remaining blocker: the docstring (`:56-62`) and `LIMITS` (`:144`) promise a live-mode sandbox selftest that does not exist — `run_selftest` has no new case. `SKILL.md:430` still declares only 0–3. |
| R2 | Unborn HEAD aborts `rev-parse HEAD` | **Not applicable** | — | Lane always has commits (helper `init` clones an existing remote). Both sites fail honestly, not clean: `measure.py:295` raises → `probe_error` exit 3; `fidelity.py:449` "cannot read repository HEAD" in selftest. Editing historical gates for a window this lane cannot enter adds risk without benefit. |
| R3 | Hand-run `jj commit <untracked>` silently commits nothing, exit 0 | **Fleet-owned** | `/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh:209-214` | Helper `jj file track`s files (`--include-ignored`) and dirs before committing; the lane-side mitigation is already AGENTS.md:6 "never a mutating `jj` command here". No lane file to change. |
| §6.1 | Leave the nine named-gate git reads alone | **Accept, no change** | — | All 15 sites are class D or temp-dir class B; lane `tools/` and `tests/` contain zero git calls (re-verified). |
| §6.2 | Commit before running round-13 live | **Superseded by R1** (until then, ordering) | `.ufo/waves/round-13/measure.py` | Once divergence is its own could-not-evaluate exit, a dirty QUALITY.md no longer reads as a documentation failure. Today QUALITY.md equals HEAD, so no live run is exposed. |
| §6.3 | Use `refs/heads/master`; never `HEAD`/`@{u}`/`--abbrev-ref`/`--show-current` | **Already in lane, uncommitted** | `AGENTS.md:6` — "read the tip with `git rev-parse master` or `jj-lane.sh state`, never `@{u}`, `--abbrev-ref HEAD` or `branch --show-current`" | Nit: `refs/heads/master` is stricter than `master`; no tags exist, so latent only. Must land (see §3.1). |
| §6.4 | Never add `.gitattributes` filters/eol or git hooks | **Already stated + verified absent** | `AGENTS.md:6` — "jj ignores git hooks and `.gitattributes` eol/filters: add neither expecting them to fire." | No attributes, no active hooks. No change. |
| §6.5 | `jj file track` before `jj commit`; prefer the helper | **Fleet-owned** | `jj-lane.sh:209-214` | Already implemented; lane only must not hand-run jj. |
| §6.6 | `round-16/measure.py:116` lacks `--no-replace-objects` + GIT_* scrub | **Fix in lane, deferred** | `.ufo/waves/round-16/measure.py:116` = `["git", "-C", str(LANE), "cat-file", "blob", spec]` | Not a jj-compat defect and currently latent: zero replace refs, `GIT_DIR`/`GIT_WORK_TREE`/`GIT_INDEX_FILE` unset. That file is the named `counting_command` in `.ufo/waves/round-16/acceptance.json:6`; editing it mid-wave perturbs C1's before/after detector. Reviewer `R16MeasureParity` (`make_spec.py:193`) owns the fix-or-explain call. If fixed: additive only, after C1's counting run. |

## 2. JjTrialKama — each recommendation

| # | Trial item | Decision | Owner / file | Basis |
|---|---|---|---|---|
| 1 | Keep helper `init` as-is (`auto-track=none()`, `trunk()=master@origin`) | **Fleet-owned, agree** | `scripts/hyaku/jj-lane.sh` | No lane config addition needed; `none()` is load-bearing (Trial measured 94 phantom adds and 124 ms under `all()`), and the lane has no repo config to change. |
| 2 | Add `.ufo/state/` and `registry/history/.lock` to `.gitignore` | **Premise partly wrong; one half already satisfied, other half done-but-uncommitted** | `registry/history/.gitignore:3` = `.lock`; `.gitignore:2` = `.ufo/state/` | Trial said `.gitignore` "contains exactly `.ufo/interactive-sessions/`", but it missed the nested `registry/history/.gitignore`, which already ignores `.lock` at HEAD (verified with `git check-ignore`). Only `.ufo/state/` was genuinely missing. Belt-and-suspenders anyway: helper state defaults *outside* the lane (`jj-lane.sh:34` `STATE=${HYAKU_STATE:-$HOME/.local/state/shokunin-hyaku}`) and commit refuses `.ufo/state/*` (`jj-lane.sh:182`). |
| 3 | Document "never `git add`/`commit`/…; use `jj-lane.sh`" in lane docs | **Done in worktree, uncommitted** | `AGENTS.md:6` | Wording matches the Trial's recommendation. Must be committed or it is not landed. |
| 4 | No `snapshot.max-new-file-size` override needed | **Not applicable now** | — | Largest round-17 artifact is `spawn-result.json` at 443,487 B (<1 MiB); helper names files with `--include-ignored`, which per its own comment admits files over the 1 MiB default. Re-check only if a single >1 MiB commit-eligible file appears. |

## 3. Lane findings this review adds (actionable)

### 3.1 Two doc edits are unowned and uncommitted — they can silently fail to land
`git status --porcelain` shows `M .gitignore`, `M AGENTS.md`. `assignments.json` contains **zero** references to either path; the only writers named anywhere are read-only reviewers (`AgentsDoc`, `make_spec.py:194`; `JjLaneHygiene`, `:172`). If L1's round-17 commit does not name both paths, neither the ignore rule nor the jj VCS bullet lands, and the only implemented part of Trial rec 2/3 becomes invisible to future rounds.
Action: L1 adds `.gitignore AGENTS.md` to the helper `commit` path list (or reverts them).

### 3.2 Five carry-forward lessons still teach `@{u}..HEAD`, which now exits 128
Verified live: `git -C kama-shokunin rev-list --count '@{u}..HEAD'` → exit 128 `fatal: HEAD does not point to a branch`.
Sites: `corpus/lessons/round-11-verifier-spotcheck.md:44`, `round-12-verifier-spotcheck.md:31`, `round-13-verifier-spotcheck.md:39`, `round-14-verifier-spotcheck.md:32`, `round-15-verifier-spotcheck.md:33` — e.g. round-15: "`git -C … rev-list --count '@{u}..HEAD'`".
The wave contract forbids editing old lessons, so the fix is a new lesson (suggested `corpus/lessons/round-17-jj-colocation.md`) with the replacements:
- landed: `git -C <lane> merge-base --is-ancestor <cited-hash> master` (exit 0)
- ahead/behind + detached state: `/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh state <lane>` (prints `ahead=… behind=… head=detached`); round-16 lesson already uses it (`round-16-verifier-spotcheck.md:27`).
Without this, a verifier following the round-11..15 recipe gets a fatal where it expects `0`.

### 3.3 The wave spec repeats a now-false premise
`.ufo/waves/round-17/build/make_spec.py:20` says "`.ufo/state/` and `registry/history/.lock` not gitignored". The `.lock` half was already false at HEAD (`registry/history/.gitignore:3`); the `.ufo/state/` half is stale (added at `.gitignore:2`, uncommitted). L1 must not copy this into the round claim/report as an unimplemented risk.

### 3.4 R1's sandbox selftest cannot be built with a plain `git init`
Constraints the `JjRound13Gate` seat must respect (already messaged to it); line numbers below are from the pre-edit file, and the in-flight docstring/FINDINGS inserts shift them:
- `git_read` hardcodes `-C str(LANE)` (`measure.py:278`) and `LANE` derives from `__file__` (`:71-72`), so a synthetic repo is only addressable by running a copy of the script from `<tmp>/lane/.ufo/waves/round-13/`.
- `before_is_pinned_start = oid == BEFORE_REVISION` (`:394`) needs the real `941bb32c…` object; a synthetic repo cannot fabricate a SHA-1 preimage, and loosening this predicate would weaken a real check. The seat's chosen route is legitimate: run a byte-identical script copy whose `BEFORE_REVISION` line is repinned to the sandbox commit, so the predicate compares against the sandbox pin — assert the rewrite hit exactly once (§3.6).
- Alternative hermetic recipe: `git clone --shared` the lane into the temp lane (7.5 MB, objects hardlinked), set HEAD to a tree whose `corpus/QUALITY.md` is the pinned before text, place the pinned after bytes in the worktree. Every check then passes except divergence.
- Exit code 4 is free (`FINDINGS`, `:107-112`); `finish()` indexes that dict (`:374-375`), so the new finding id needs an entry; the docstring exit table (`:53-55`) and `SKILL.md:430` row must declare it (SKILL side owned by the `SkillRows` scribe, `make_spec.py:241` "round-13 gate new finding").
- Do **not** add an unrestricted `--repository`: `canonical_quality` (`:395`) compares against the LANE-derived default path, so a foreign repo could otherwise supply a clean HEAD while the canonical-path check still passes — a grading hole on the calibration axis.
- A `git init` sandbox also needs an initial commit, else `rev-parse HEAD` → 128 → `probe_error`.

### 3.5 Detached HEAD and prior git writes are already covered, no further action
`AGENTS.md:6` forbids git writes and names `jj-lane.sh state` as the tip reader; round-16 recorded a seat that "restored them with `git checkout`" (`corpus/lessons/round-16.md:169`), which under jj would also reset the index — now forbidden by the bullet. `.gitattributes`/hooks, index reads, the `change-id` header, and the repo-copy warning are all non-findings for this lane (absent or informational).

### 3.6 In-flight review of the R1 diff (snapshot at review time)

`git diff --numstat` on `.ufo/waves/round-13/measure.py` = `36 7`. Present: docstring exit table and sandbox description, `FINDINGS['worktree_not_at_measured_revision'] = 4` (`:127`), two `LIMITS` lines (`:144-145`), and the live-mode precedence branch (`:474-486`). The branch matches the assignment: `clean` excludes `worktree_matches_head`; `clean and not worktree_matches_head` → exit 4; every other failure stays 1; the divergence observation is retained in both. Absent: the advertised selftest — `run_selftest` still has only the ten frozen-mode cases and the file contains no `git init`, script copy, or repin. So `:57-62` and `LIMITS` `:144` overclaim the selftest scope, the same documentation-versus-behaviour defect one level up. Do not commit until the cases land or the docstring/`LIMITS` drop the claim; the scribe must not update `SKILL.md:430` from the docstring alone. Requirements for the selftest as specified:

1. **Docstring overclaims integrity handling.** `:43` says "A real content or integrity failure still exits 1 even when the worktree diverges." Live-mode integrity failures are not exit 1: `historical_quality` raises `GateError` (`:337` "empty historical QUALITY blob; refusing a vacuous comparison") and `git_read` raises on any nonzero git exit (`:306`), both surfacing as `probe_error` (3). Only *content* failures are `documentation_mismatch` (1). Suggested wording: "A real content failure still exits 1 even when the worktree diverges; an unreadable input or failed git read stays probe_error (3)."
2. **Copy depth and constant rewrite must be enforced, not assumed.** The copied script must live at `<tmp>/lane/.ufo/waves/round-13/measure.py` so `LANE = WAVE.parents[2]` (`:71-72`) resolves to the sandbox, and the `BEFORE_REVISION` rewrite (`:93`) must assert exactly one substitution. If the rewrite no-ops, the child runs the lane's pinned revision against the sandbox repo → `resolved_before` fails → `probe_error`, so the case fails loudly; assert anyway so the failure names the rewrite.
3. **Divergence needs HEAD ≠ worktree at the same commit.** The stated cases are only mutually consistent if the sandbox uses two commits: C0 contains the pinned before bytes and is the copied `BEFORE_REVISION`; C1 contains the pinned after bytes. Then (a) HEAD=C0 + after bytes in the worktree → exit 4; (b) HEAD=C1 + after bytes → clean 0; (c) HEAD=C0 + a content-failing worktree → exit 1. Committing before and after into one commit cannot produce case (a).

## 4. Limitations

- No `jj` command and no lane gate was executed; jj-model claims rest on the two reports plus the read-only git observations listed above.
- The Trial's measurements (124 ms status, 94 phantom adds, rebase-recovery) were not reproduced; only its structural conclusions are used.
- The R1 implementation was in flight during this review: the diff moved from `19 5` to `36 7`; §3.6 describes the last observed snapshot (exit-4 branch present, advertised selftest absent), not the eventual implementation.
- Whether any driver other than `jj-lane.sh` creates an in-lane `.ufo/state/` is unverified; the ignore is harmless either way [INFERENCE].

## 5. Installs

None. No package, binary, or config was installed or modified.
