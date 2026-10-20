VERDICT: confirm — jj-audit risk R1 was real (live worktree divergence folded into `clean`, yielding failed-gate `documentation_mismatch`/1); now a distinct could-not-evaluate finding `worktree_not_at_measured_revision`/4, selftest-proven 13/13.

# Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-13/measure.py` — sha256 `38b8123920d3963f22de7164f33e88ac4117827272300bd4a2c07fb0b18c736b` (was `2399d64dcde477dd26f6f1092819b6392fc812dc5a64a949f8e075d6a0918fd6`). Only file written; `frozen/expected.json` did not need changes.

# What changed

- `FINDINGS` gains `worktree_not_at_measured_revision: 4` (codes 0-3 were taken).
- `run_live` (measure.py:466-486): `clean` no longer includes `worktree_matches_head`. If every other check is clean but the `--quality` bytes differ from the blob committed at the measured HEAD → finding `worktree_not_at_measured_revision`, exit 4. Any other check failure keeps precedence → `documentation_mismatch`/1; the `worktree_not_at_measured_revision` observation is still appended either way (was already emitted as observation). Per reviewer correction: live-mode input/git failures remain `probe_error`/3 via GateError; only content failures are exit 1.
- Docstring: live-mode bullet, selftest-scope paragraph, exit-code table updated; `LIMITS` gains two entries (exit-4 precedence semantics; sandbox repin disclosure).
- `run_selftest` gains three live-mode cases in a sandbox git repo inside its `TemporaryDirectory` (never the lane; scratch deleted by tempfile cleanup):
  - `live_worktree_divergent_clean`: HEAD = before-commit, worktree = pinned after bytes → exit 4 / `worktree_not_at_measured_revision`.
  - `live_committed_clean`: HEAD = after-commit, worktree = pinned after bytes → exit 0 / `clean`.
  - `live_worktree_divergent_content_failure`: HEAD = before-commit, worktree = after bytes minus the exit-map literal → exit 1 / `documentation_mismatch` (precedence proven).
- Sandbox mechanics: `git init` repo at `<tmp>/live-sandbox/lane` with two commits (frozen before bytes, then frozen after bytes); a byte-identical copy of measure.py is placed at `<tmp>/live-sandbox/lane/.ufo/waves/round-13/measure.py` so `LANE = parents[2]` resolves to the sandbox; the copy's `BEFORE_REVISION` literal is repinned to the sandbox before-commit with an asserted exactly-one replacement (`source.count(pin_literal) != 1` → GateError). No `--repository` flag was added — `canonical_quality` still compares against the LANE-derived default, so no foreign-repo grading hole. Per-case HEAD selection uses `git reset --hard <oid>` inside the sandbox only; no git/jj write ran in the lane.

# Exercised verification

`python3 -m py_compile` clean; `python3 .ufo/waves/round-13/measure.py --selftest` → `verdict_exit 0`, `passed: 13`, `failed: 0`, all `observed` fields equal `expected` (three new cases observed 4/`worktree_not_at_measured_revision`, 0/`clean`, 1/`documentation_mismatch`).

# Old-sha pin grep (mandated exclusions applied; interactive-sessions/.git/.jj unsearched)

`2399d64d` appears in: `.ufo/waves/round-13/advice/Measure.md:9` and `SafetyPaths.md:8` (both committed — historical records of the revision reviewed, now stale w.r.t. the live file), `.ufo/waves/round-17/frozen/manifest.json:9` (not yet git-tracked; pins the frozen copy `round-13_measure.py`, verified still byte-identical at that sha — correctly unchanged), and round-17 build dispatch/spec copies of my own assignment text. No committed file pins the old sha as a constraint on the live gate; nothing else requires updating.

# For the SkillRows scribe (per KamaR17.ReviewJjRiskMap-2)

`SKILL.md:430` (round-13 gate row) still declares exits 0-3 and "undeclared nonzero codes could-not-evaluate"; the row must declare exit 4 `worktree_not_at_measured_revision` and the selftest-scope claim should mention the sandbox repo + repinned script copy.

# Limitations

- Exit 4 is emitted only when divergence is the sole failure; a divergent worktree plus any other failure still reports `documentation_mismatch` with the divergence as observation — precedence is documented in docstring + LIMITS, not separately negotiable.
- The live selftest grades a repinned copy, not the lane script in place; the repin is exactly-one-asserted but a future edit duplicating the `BEFORE_REVISION = '...'` literal would fail construction, not silently mis-pin.
- Sandbox cases cover before/after HEAD positions only; an unrelated third-commit divergence is structurally identical (worktree≠HEAD blob comparison).

# Installs

None (no tools installed or updated; pacman pause respected).
