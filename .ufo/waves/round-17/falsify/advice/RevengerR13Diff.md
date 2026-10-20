VERDICT: partial — exit 4 and frozen evidence reproduce; Round-17 documents the new map but leaves SKILL.md:430 unamended.

# Attacked

Round-17 lane commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3` change to `.ufo/waves/round-13/measure.py`, its selftests, and the claims that the frozen round-13 evidence remains valid and SKILL.md:430 is superseded.

# Findings

1. **The behavior change is a classification correction, not a new divergence detector.** At `cff9e62`, live `clean` included `worktree_matches_head`; every non-clean result returned `documentation_mismatch` (exit 1). The diff removes that equality condition from the other-content checks and classifies an otherwise-clean mismatch as `worktree_not_at_measured_revision` (exit 4). The divergence observation was already recorded at the baseline; what changed is the verdict/exit. Current code documents exit 4 and preserves exit 1 for content failure (`.ufo/waves/round-13/measure.py:39-44`: “whenever every other check is clean”; `:463-485`: divergence observation and the 4/0/1 selection). The finding map adds the ID at `:121-127`.

2. **The three selftest additions exercise the changed distinction in a temporary git sandbox.** `live_worktree_divergent_clean` expects 4, `live_committed_clean` expects 0, and `live_worktree_divergent_content_failure` expects 1 (`.ufo/waves/round-13/measure.py:798-826`). The sandbox is under `TemporaryDirectory`; the script copy is repinned to the sandbox before commit (`:891-941`), not to the lane. Running the current selftest in the required clone returned exit 0, 13 passed / 0 failed. Running the baseline selftest at `cff9e62` returned exit 0, 10 passed / 0 failed.

   Direct divergent-worktree reproduction used an appended LF, leaving the KQ16 assessment clean (0 missing assertions): at `54a29268`, the live gate returned exit 4 / `worktree_not_at_measured_revision`; the same input at `cff9e62` returned exit 1 / `documentation_mismatch`. The current committed-worktree live run returned exit 0 / `clean`; the new selftest also observed the divergent-content-failure case as exit 1. This confirms the false-failure mechanism while preserving content-failure precedence. This reproduces byte divergence, not a jj runtime.

3. **No frozen round-13 receipt or snapshot pin was falsified.** The round-13 directory diff contains only `measure.py`; `frozen/expected.json` remains unchanged. Its before/after hashes and expected findings remain `157495…173cf` / `documentation_mismatch` and `596f87…13da` / `clean` (`.ufo/waves/round-13/frozen/expected.json:7-23`). In the clone at the round commit, frozen manifest replay returned aggregate exit 0 / `clean`; the explicit before case returned exit 1 / `documentation_mismatch`, and after returned exit 0 / `clean`, both with `input_digests: true`. The committed round-13 acceptance record identifies its measured revision as `641e1b6f…` (`acceptance.json:2`); SCORECARD records that the historical live run matched measured HEAD and that the original ten selftests passed (`SCORECARD.md:381-387`). Those are historical observations and remain true; the new code does not rewrite their meaning.

4. **The round-13 Measure advice digest remains valid as a historical digest, not as the current source digest.** `advice/Measure.md:9` records source SHA-256 `2399d64d…18fd6`, which matches both the `cff9e62` source blob and Round-17's frozen pre-change copy; the current source hash is `38b81239…c736b`. Thus the old digest statement is not false: it identifies the old source. Its ten-case/0–3 exit inventory (`Measure.md:24-26`) is likewise historical and must not be used as the current inventory. Its statement that a clean live verdict requires HEAD/worktree equality (`:22`) remains true: divergence now yields exit 4 rather than exit 0. The round-13 advice files were not changed by this diff.

5. **SKILL.md:430 is not literally updated, although §Round-17 adds the current exit-4 entry.** The old row still lists 0–3 and says “undeclared nonzero codes could-not-evaluate” (`SKILL.md:430`). Exit 4 is now declared in the gate. §Round-17 says “The round-13 row at line 430 gains exit 4” (`SKILL.md:565-566`) and adds a separate Round-13 row with the exit-4 meaning (`:577`). But the Round-17 SKILL diff has its hunk at the appended section around line 552, not at line 430. Consequently, line 430's 0–3 mappings remain valid, but its catch-all does not classify a now-declared exit 4. [INFERENCE] The later line-577 row is intended to supersede/extend the earlier row for the current live gate; as written, the prose claims an update that the table itself does not show. This is a documentation inconsistency, not evidence that the gate's result or frozen receipt is wrong.

# Commands run and exits

Read-only lane inspections (all exited 0):

```text
git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff cff9e62 54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- .ufo/waves/round-13/measure.py
git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --stat cff9e62 54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- .ufo/waves/round-13/
git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --unified=1 cff9e62 54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- SKILL.md
```

Clone setup exited 0 and checked out the requested round commit with clean status:

```text
rm -rf /tmp/RevengerR13Diff-clone && git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/RevengerR13Diff-clone && git -C /tmp/RevengerR13Diff-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3 && git -C /tmp/RevengerR13Diff-clone rev-parse HEAD && git -C /tmp/RevengerR13Diff-clone status --porcelain | wc -l
```

Gate runs used `/tmp/RevengerR13Diff-clone` as `cwd`; these are the exact shell command strings, including output capture. The printed `exit=` is the gate process status:

```text
PYTHONDONTWRITEBYTECODE=1 python3 .ufo/waves/round-13/measure.py --selftest > /tmp/RevengerR13Diff-selftest.json; rc=$?; printf 'exit=%s\n' "$rc"
PYTHONDONTWRITEBYTECODE=1 python3 .ufo/waves/round-13/measure.py --manifest .ufo/waves/round-13/frozen/expected.json > /tmp/RevengerR13Diff-frozen-aggregate.json; rc=$?; printf 'exit=%s\n' "$rc"
PYTHONDONTWRITEBYTECODE=1 python3 .ufo/waves/round-13/measure.py --manifest .ufo/waves/round-13/frozen/expected.json --quality .ufo/waves/round-13/frozen/before/corpus/QUALITY.md > /tmp/RevengerR13Diff-frozen-before.json; rc=$?; printf 'exit=%s\n' "$rc"
PYTHONDONTWRITEBYTECODE=1 python3 .ufo/waves/round-13/measure.py --manifest .ufo/waves/round-13/frozen/expected.json --quality .ufo/waves/round-13/frozen/after/corpus/QUALITY.md > /tmp/RevengerR13Diff-frozen-after.json; rc=$?; printf 'exit=%s\n' "$rc"
PYTHONDONTWRITEBYTECODE=1 python3 .ufo/waves/round-13/measure.py --quality corpus/QUALITY.md > /tmp/RevengerR13Diff-live-clean.json; rc=$?; printf 'exit=%s\n' "$rc"
cp corpus/QUALITY.md /tmp/RevengerR13Diff-quality-save && printf '\n' >> corpus/QUALITY.md && PYTHONDONTWRITEBYTECODE=1 python3 .ufo/waves/round-13/measure.py --quality corpus/QUALITY.md > /tmp/RevengerR13Diff-live-divergent.json; rc=$?; cp /tmp/RevengerR13Diff-quality-save corpus/QUALITY.md; printf 'exit=%s\n' "$rc"
git checkout -q cff9e62 && cp corpus/QUALITY.md /tmp/RevengerR13Diff-quality-old-save && printf '\n' >> corpus/QUALITY.md; PYTHONDONTWRITEBYTECODE=1 python3 .ufo/waves/round-13/measure.py --quality corpus/QUALITY.md > /tmp/RevengerR13Diff-live-old-divergent.json; rc=$?; cp /tmp/RevengerR13Diff-quality-old-save corpus/QUALITY.md; printf 'exit=%s\n' "$rc"; git rev-parse HEAD
PYTHONDONTWRITEBYTECODE=1 python3 .ufo/waves/round-13/measure.py --selftest > /tmp/RevengerR13Diff-selftest-old.json; rc=$?; printf 'exit=%s\n' "$rc"
```

Results in that order: current selftest 0 (13/13), frozen aggregate 0/clean, frozen before 1/`documentation_mismatch`, frozen after 0/`clean`, current live clean 0, current divergent clean 4/`worktree_not_at_measured_revision`, baseline divergent clean 1/`documentation_mismatch`, baseline selftest 0 (10/10). Both divergent assessments had 0 missing assertions. The frozen outputs had `input_digests: true`.

Read-only hash commands (exit 0):

```text
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show cff9e62:.ufo/waves/round-13/measure.py | sha256sum
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 54a29268e2083caa2b1e0d54ee1e7d90961302f3:.ufo/waves/round-13/measure.py | sha256sum
sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/round-13_measure.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-13/measure.py
```

The first and frozen-copy hashes were `2399d64d…18fd6`; the current hash was `38b81239…c736b`. Owned `/tmp/RevengerR13Diff-*` scratch was removed with `rm -rf /tmp/RevengerR13Diff-*` (exit 0).

# Limitations and installs

No jj execution or runtime integration was attempted; the live divergence was reproduced with a temporary byte edit in the clone. No tools were installed or updated.