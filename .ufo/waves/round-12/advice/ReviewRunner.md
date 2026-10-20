# Round 12 — ReviewRunner static review (author advisor, not closure)

Scope: runner contract for `.ufo/waves/round-12/reproduce.py`. No runs, builds, tests, git commands, or writes outside this report. Tools installed/updated: none.

## Inputs examined

- `.ufo/waves/round-12/reproduce.py`: **absent** at review time (read returned not found).
- `.ufo/waves/round-12/fidelity.py`: **absent** at review time.
- `.ufo/waves/round-12/spec.json` (contract text), `claims.json`.
- `.ufo/waves/round-11/reproduce.py` (reference template, read only).
- `corpus/lessons/round-11-verifier-spotcheck.md` (routed D1–D5 and the D1 truncated-snapshot evidence).

Because neither file exists yet, every finding below is against the written contract and the round-11 template. Re-review is required once the files land.

## Findings by severity

### High — would let a defect pass or misreport

1. **Expected outcomes are not independent of the lane.** The round-11 template loads `frozen/expected.json` and trusts its `exit` and field values. It verifies digests of the inputs *listed in* that file, but never pins `expected.json` itself. A coherent edit to `expected.json` plus its inputs passes with `ok: true`. Fix: hard-code the expected exits (`old=1 source_mismatch`, `new=0 clean`, `selftest=0`, attack `1 source_mismatch`) in `reproduce.py` and/or pin the SHA-256 of `expected.json` as a constant in the runner. Evidence: round-11 `reproduce.py` lines 29–34, 44–46.

2. **Coherent-mutation attack can pass on the wrong failure.** The contract says a snapshot+manifest coherent mutation must be caught by source correspondence. If the runner accepts any nonzero exit as "detected", `snapshot_tampered` (exit 2) satisfies it. Fix: require exit 1 **and** `verdict == "source_mismatch"`. Reject exit 0 (undetected) and exit 2 (wrong class). Also require the mutated snapshot bytes to differ from the frozen snapshot, so the attack is not vacuous.

3. **Verdict asserted only by exit code.** Exit codes can coincide with a wrong verdict string. Assert the JSON `verdict` field (`clean` / `source_mismatch`) for every CLI record, not only the exit.

4. **Could-not-evaluate collapses into verdict failure.** Contract exit semantics: 0 = expected, 1 = unexpected verdict, 2 = could not evaluate. Round-11 has no guard around `json.loads(record['stdout'])` (lines 43, 51, 76, 86). Empty or non-JSON stdout raises an uncaught `JSONDecodeError`, which exits 1 by traceback. That is indistinguishable from a verdict mismatch. Fix: wrap parsing, timeouts, and missing files; map them to exit 2 with a receipt entry.

### Medium

5. **Measured revision captured too late and unchecked.** Round-11 runs `git rev-parse HEAD` *after* all subprocesses (lines 89–90), with `check=True`, so a missing git raises a traceback (exit 1) instead of exit 2. The HEAD is also not compared before vs after, so a mid-run change goes undetected. Fix: capture HEAD before the first subprocess and again after; fail if they differ; record both. Record the fixed source commit `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad` separately.

6. **Revision in claims does not match the source pin.** `claims.json` `before` is `79fa257719e8688692ed1dc443589331ba22b7fe`. `spec.json` fixes the source commit at `2f7303c…`. These are different identities. Do not conflate them: the runner should compare the snapshot to `2f7303c`, and report the measured HEAD separately. Not verified here (no git run); L1 must confirm how `79fa257` relates to `2f7303c` and whether it is the round-12 starting HEAD.

7. **No subprocess timeout.** `subprocess.run` in `run()` (round-11 line 23) has no timeout. A hung `git show` stalls the runner indefinitely. Fix: set a timeout and map `TimeoutExpired` to exit 2.

8. **Selftest passes on exit code alone.** `records['selftest']` checks exit 0 only (line 57) and has no `matches_expected` key (lines 56–57), so consumers reading the key get `KeyError`. Require the four named outcomes (clean, mismatch, tamper, unavailable) in the selftest output, and fail when any is absent.

9. **Frozen tree not re-hashed after controls.** Round-11 writes controls only into temp copies (correct), but never re-checks `frozen/**` and `expected.json` after the run. Fix: hash those files before and after; any change fails the run.

10. **CLI cwd and repo not pinned.** `run()` sets no `cwd` and no `--repo`. Pass `--repo ROOT` explicitly on every fidelity call so the git blob source is not inferred from the caller's working directory.

### Low

11. **Ambiguous "no manifest" semantics.** The contract says a snapshot override without a manifest should observe the old mismatch. It is not stated whether the CLI still applies the default `expected.json` when only `--snapshot` is passed. If it does, the old snapshot reports `snapshot_tampered` (exit 2) and the runner (expecting exit 1) fails visibly, which is the right outcome. The CLI owner should confirm the rule; the runner should expect exit 1 and not silently accept exit 2.

12. **Round-11 contract details carried over correctly (keep):** `check=False` with exit preserved; full command/stdout/stderr/exit captured per record; control fixtures written only into `tempfile.TemporaryDirectory` copies; frozen digests verified before any gate comparison; `ROOT` derived from `__file__`.

## Checks for L1 (main agent, once, after integration — not run here)

1. `python3 .ufo/waves/round-12/reproduce.py` → exit 0, `ok: true`; `measured_commit` equals HEAD both before and after.
2. Old frozen snapshot record: exit 1, `verdict == source_mismatch`, `--manifest` absent.
3. New snapshot record with default manifest: exit 0, `verdict == clean`.
4. Selftest record: four named cases present and passing.
5. Coherent attack record: exit 1, `verdict == source_mismatch`; mutated snapshot SHA ≠ frozen SHA.
6. `sha256sum` of `frozen/corpus/SOURCES.md` and `frozen/expected.json` unchanged across the run.
7. Independent correspondence: `git -C ROOT show 2f7303c242319c1dc96c6bcf7702ac18b3ca1aad:corpus/SOURCES.md | sha256sum` equals the new snapshot SHA (expected `52665cf…` is the *old frozen* value and must not match the new one; the old-frozen-vs-actual hashes are `52665cf2…` vs `9dc40d25…` from D1).
8. Grep `reproduce.py` for `shell=True`, `json.loads` without guard, `check=True`, and any write path not under a temp directory.
9. Negative control: with a deliberately wrong expected value in a temporary copy, the runner must exit 1 (not 0).

## Residual risk

- The contract's source correspondence depends on the git blob at `2f7303c…` remaining reachable. If `source_unavailable` occurs, the result must be exit 2, never a pass.
- Coherent snapshot+manifest mutation is detected only by source correspondence; digest pinning alone cannot catch it. Any shortcut that compares digests without the git blob reopens D1.
- Nothing here establishes capability, serving readiness, or any scalar change. Claim C1 remains calibration-only.
