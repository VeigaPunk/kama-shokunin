VERDICT: n/a — no domain overlap between mado and kama C1/C2; the transferable content is process convention, and two jj premises in the round context are already stale.

# ConnectMado — mado/kama overlap scan (round 17 BUILD)

## Bounds of this scan

Read: mado `SKILL.md`, `PROVINCE.md`, `corpus/QUALITY.md` only (per assignment; mado `AGENTS.md`/`.gitignore` deliberately not read). Kama: `PROVINCE.md`, `AGENTS.md`, `.gitignore`, `registry/history/.gitignore`, `corpus/QUALITY.md`, `SKILL.md:531-536`, `build/spec.json`, `frozen/manifest.json`, read-only git `status`/`show`/`check-ignore`/`rev-parse`. Fleet: `JjAuditKama.md`, `JjTrialKama.md`, `scripts/hyaku/jj-lane.sh`. No `jj` command, no gate, no counter, no install.

## Findings

### F1 — Product-surface contest: none; the handoff is already written

mado `PROVINCE.md:14-15`: "**Refuses:** secrets in configs (shape-only, → kagi), model endpoints (→ kama), model quality (→ kengaku)." Kama `PROVINCE.md:40-43` defines the matching boundary: "kama answers *'is the thing at this baseURL the model this config believes it is, right now'*". C1 (`tests/probe-verdicts/`) and C2 (`tools/kama-llamacpp-live.py`) contain no mado surface. Kama must not route C1/C2 artifacts to mado, and nothing from mado can carry a C1/C2 verdict. [OBS]

### F2 — Policy contest: do not import mado's source-only pause into C2

mado `SKILL.md:39-42`: "Host-wide package pause until an explicit operator recovery decision: no package transactions or service/compositor mutations." Lines 41-42 additionally suspend live reads and producer execution for mado's round. That is **mado's round scope, not kama's**: kama `PROVINCE.md:55-60` authorizes a lane-owned `llama-server` child "on a free loopback port that is never a registered consumer port or a listening port". Absorbing mado's no-live rule would delete C2's operability claim; exporting it as fleet policy would overreach into the operator's host-pause decision. Any generalization stays with L0/operator. [OBS] + [INFERENCE]

### F3 — Stale premise: both "unguarded" runtime paths are already ignored

The round context says `.ufo/state/` and `registry/history/.lock` are not gitignored. Measured otherwise: worktree `.gitignore:2` is `.ufo/state/`, and tracked `registry/history/.gitignore:3` is `.lock` (`git show HEAD:registry/history/.gitignore` reproduces it). `git check-ignore -v registry/history/.lock .ufo/state/x` prints `registry/history/.gitignore:3:.lock` and `.gitignore:2:.ufo/state/`. JjTrialKama.md:113's recommendation ("`Add to kama-shokunin/.gitignore` … `.ufo/state/` and `registry/history/.lock`") is therefore fully satisfied for `.lock` and satisfied in the worktree for `.ufo/state/`. Do not add a duplicate `registry/history/.lock` line; repeating the stale claim in the lesson would inscribe a false defect. [OBS]

### F4 — The jj docs exist only in the worktree; no dispatch item owns them

`git status --porcelain` at scan time: ` M .gitignore`, ` M AGENTS.md`, `?? .ufo/waves/round-17/`. No round-17 item in `build/spec.json` targets `.gitignore` or `AGENTS.md`; the only items naming them are read-only seats (`ScoutJjLaneHygiene`, `ReviewAgentsDoc`). The helper commits only named paths (`jj-lane.sh:230`: `commit -m "$msg" -- "${existing[@]}"`), so if L1's path list omits these two files the entire jj-colocation rule and the `.ufo/state/` ignore stay unlanded while every gate reads green. This is the highest-value operability fix found in the scan. [OBS]

### F5 — AGENTS.md wording: the LOG debt has no owner (mado's model solves it)

kama `AGENTS.md:4`: "Every change appends a LOG.md entry with the evidence that motivated it." Leaf seats cannot write `LOG.md`. mado hit the same conflict and recorded the debt instead of dropping it: `SKILL.md:924-925`: "`LOG.md` entry for round 6 is owed by the scribe/finalizer lane (AGENTS.md:3); this lane's write scope was this file only." Under jj there is no later `git add -A` sweep, so an uncommitted `LOG.md` entry stays uncommitted. Proposed append to `AGENTS.md:4`: *"A seat whose write scope excludes LOG.md names the owed entry in its Report; the scribe/finalizer item lands it."* Round 17 already dispatches `ScribeLogEntry`, so this is coordination, not new scope. [OBS]/[INFERENCE]

### F6 — AGENTS.md wording: no rule for pre-commit measurements

`AGENTS.md:6` says "cite only the hash it prints as `landed`/`pushed`" but says nothing about a count produced before that commit. mado `corpus/QUALITY.md:13`: "label work-window hashes provisional and bind them again at the commit"; `:15`: "label mid-edit failures in-flight, never as settled defects"; `:16`: "Report each count as `<n> — <command> <date>`". C1's `survived` and C2's `accepted_bad` are exactly such work-window counts. Proposed second sentence: *"A measurement run before the helper commit is provisional; bind its counts to the landed revision by re-derivation or by a recorded `revision` + input sha."* [OBS]

### F7 — Reusable convention: the boundary sentence belongs in C1's output

mado `SKILL.md:241-242`: "A probe pass ends only when the config trees are byte-identical", and `:299`: "Substrate byte-identical before/after (sha256), pass <date>." C1's hard constraint (nine matrix `*.json` byte-identical) has the same shape. Have `mutants.py` print `Matrix set byte-identical before/after (sha256 <set>), pass <date>` and abort on delta. Round 16 already pins the set digest (`bf9068d8…`), so this is one output line plus one comparison — no new machinery, and it turns a procedural constraint into an observable one. [OBS]

### F8 — Reusable convention: a gate row is not admissible without a killing mutant

mado `SKILL.md:923`: "Neither may ship as gate rows without a mutant that kills the clause." This is the rule C1's `fault-controls.py` and C2's `controls.py` exist to satisfy. Two kama rows still state the pre-repair claim: `SKILL.md:533` says the gate "grades verdict, reason, exit and drift", and `:534`'s counting row predates the new invariants. The already-dispatched `ScribeSkillRows` item must update both; this seat must not edit `SKILL.md`. [OBS]

### F9 — jj helps the C1/C2 sha bindings, with one condition

`JjAuditKama.md:95` (F6): "jj ignores `.gitattributes` text/eol normalization"; re-measured here, `git check-attr -a` over `check.py`, `kama-llamacpp-live.py` and `check-receipt.py` returns zero lines (`git ls-files --eol` shows the `attr/` column empty). Therefore a sha256 over worktree bytes before the helper commit equals the committed blob sha after it — stronger than git-with-filters. C1/C2 can bind tool/gate/probe sha pre-commit and re-verify at the landed commit with `git cat-file blob <landed>:<path> | sha256sum`. Condition: never add `.gitattributes`/filters (already forbidden at `AGENTS.md:6`). [OBS]/[INFERENCE]

### F10 — `.gitignore` is not a commit guard under the helper

`jj-lane.sh:201-204`: "`--include-ignored` … applies only to paths named as FILES; a named directory is tracked like `git add <dir>`". An explicitly named ignored file is therefore admitted; `.ufo/state/` is protected by the helper's own reject at `:182-183` ("driver runtime is never committed by a lane"), not by `.gitignore`. Keep the ignore lines for plain-git seats and directory listings; do not treat them as the enforcement point. [OBS]

### F11 — Repo-scoped jj config is not visible in `.jj/repo`; effective auto-track is UNKNOWN here

`.jj/repo/` contains `config-id` but no `config.toml`; jj 0.45's own strings reference `config-id`, `repos` and `workspace-config.toml`, i.e. repo/workspace config may live under a user config path this seat may not read (privacy bound). The helper writes four repo settings at init (`jj-lane.sh:152-155`, including `snapshot.auto-track "none()"`). Whether the live lane still resolves `none()` is UNKNOWN to this seat. JjTrial measured the default at 94 phantom adds and 124 ms vs ~10 ms (`JjTrialKama.md:45-47`), so this is not cosmetic. L1 must run `jj config list --repo` (or an equivalent helper read) once before the first commit. [OBS]/[INFERENCE]/[UNK]

### F12 — Frozen round-13 gate still has the pre-fix jj behavior; order it after commit

Frozen `.ufo/waves/round-17/frozen/round-13_measure.py:295` reads `git rev-parse HEAD`; `:397` sets `worktree_matches_head = final == head_quality`; `:446` turns a diff into exit 1. `JjAuditKama.md:179`: "helper `commit` → then round-13 live." The live fix belongs to item `JjRound13Gate`; the frozen copy is never edited. Any round-17 parity run of the frozen gate before the helper commit must label exit 1 a jj worktree divergence, not a `documentation_mismatch` in QUALITY.md. Hand the run order to L1. [OBS]

## What kama must hand off rather than absorb

1. **Fleet helper** `scripts/hyaku/jj-lane.sh`: R3 silent empty commit (`JjAuditKama.md:158`), `--include-ignored` file semantics, branch detection, repo-config persistence (F11). Do not patch the helper from the lane.
2. **Round-13 `measure.py`** (live) → item `JjRound13Gate`; frozen copy untouched. Only run-order guidance belongs to L1.
3. **Fleet-wide AGENTS.md jj paragraph** → hyaku jj-w1; `AGENTS.md:6` is a lane-local instance, not a template kama may impose.
4. **mado's host pause / source-only policy** → operator/L0; kama's live fixture authority is `PROVINCE.md:55-66` (pending L0 ratification) and must not be broadened or cited as fleet policy.
5. **`registry/history/.lock` top-level ignore** → nobody; already covered (F3), do not duplicate.

## Proposed move (one, bounded)

Give **both** counting commands the same four-key provenance block in their new JSON schemas: `revision` = `git rev-parse --verify refs/heads/master` captured at run start; `worktree_dirty` = non-empty `git status --porcelain -- <measured paths>`; `input_sha256` for `check.py` / tool / gate; `probe_sha256`. `C2Controls` already specifies `tool_sha256`/`gate_sha256` (`build/spec.json`, C2Controls); `C1MutantRunner` currently specifies only `{id, site_found, killed, evidence}` plus totals. Cost: four additive keys in two new schemas with no existing consumer. Effect: the round's before/after counts become citable as `<n> — <command> <date> at <master>` and re-verifiable at the landed blob, satisfying mado `QUALITY.md:13/15/16/19` without changing any check or mutant semantics. This is a compatible synthesis of mado's revision-binding conventions and jj's raw-byte commit property (F9).

Risk: `worktree_dirty=true` by construction before the commit — it is the "provisional" marker, not a failure; and a file edited between run and commit invalidates the sha (re-run or re-bind).

## Risks and contradictions

- **Stale context (F3/F4):** two stated defects are already fixed or unlanded-doc-only; a lesson that repeats them will be false. The live issue is *committing* the fix, not *making* it.
- **F11 vs F9:** if auto-track is still `all()`, the helper's snapshot can add untracked files as intent-to-add, polluting `git status` for plain-git gates. The pre-commit sha remains valid, but config must be checked before the first commit.
- **Provenance is not authority:** kama `corpus/QUALITY.md:61` (KQ16) already separates capture from comparison. `revision`/sha are provenance, not a verdict; do not let them upgrade a count.
- **Evidence placement:** `mutants.py --out` and `controls.py --json` outputs must live under the lane and be committed; mado `QUALITY.md:19`: "Evidence meant to outlive a round is a committed path or quoted lines plus sha; `/tmp` records provenance only." `.ufo/waves/round-17/` is currently entirely untracked.

## Verification L1 should run

- `git -C <lane> check-ignore -v registry/history/.lock .ufo/state/x` → the two rules above (already measured).
- `git -C <lane> status --porcelain` → confirm `.gitignore` and `AGENTS.md` are in the helper commit path list.
- After the helper commit: `git show <landed>:.gitignore`, `git show <landed>:AGENTS.md`, and `git cat-file blob <landed>:<measured path> | sha256sum` equal to the recorded `input_sha256`.
- `jj config list --repo` once before the first commit (F11).
- Frozen round-13 parity only after the commit, or with exit 1 labelled jj-divergence.

## Limitations

- Read-only seat; no `jj`, gate, or counter executed; no measurement run.
- mado `AGENTS.md` and `.gitignore` were not read by assignment constraint, so mado's actual jj wording is outside this scan; the mado citations above are limited to the three permitted files.
- `git status` and the tree state are a timestamped snapshot (2026-10-20, during concurrent seats).
- F11's effective config is UNKNOWN because the deciding file lies under a privacy-bounded path; only L1's jj read can settle it.
- `JjAuditKama.md`/`JjTrialKama.md` measurements are cited, not re-run.

## Installs

None. No package, binary, or tool was installed or upgraded for this scan.
