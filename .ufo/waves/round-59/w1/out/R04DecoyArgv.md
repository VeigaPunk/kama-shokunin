# R04DecoyArgv — round 59, kama — argv-routing decoy vs C1 checker/counter

Seat: leaf, advisory falsification. Axes: operability, calibration (calibration=7 lowest assigned).
Milestone: round59 claim falsification. Attacked claim/clause: freeze.txt C1-r59 sentence,
clause **"or routes its argv to `python3 other-script --counter` must not meet"** (and adjacent
clause "emits a decoy `--counter`"). All measurements pinned to the frozen C1 tip
`aca8d0067ea25627c5015c2193c843965148bc8e` (lane HEAD has moved to `4a541190b6d494a4e99116249632e99aab80adcc`;
every blob read used the pinned tip). Fleet `/home/vgpnk/Projects/shokunin` and `/home/vgpnk/Projects/shokuknow` untouched.
No installs performed (system python3 3.14 + git only; nothing to record under the tooling directive).

## Construction (smallest no-op)

`D1` = committed `tests/round58-battery-variants/genuine.py` blob at the tip with exactly two
argv[1] sites changed, `str(TEST)` → `"other-script"` (genuine 4012 B → 4022 B; full diff:
`.ufo/waves/round-59/w1/out/R04DecoyArgv/d1-vs-genuine.diff`):

```diff
-    p = subprocess.run(["python3", str(TEST), "--counter", str(counter), "--expect", expected],
+    p = subprocess.run(["python3", "other-script", "--counter", str(counter), "--expect", expected],
```
(second identical site in `assert_mutant_breaks_detection`). Every leg therefore makes exactly
**one** subprocess call whose argv contains `--counter` and `--expect`, and **no argv references
the committed counter runner** `tools/round56-env-leg-test.py`. Honesty note: the decoy retains the
now-unused constant `TEST = LANE / "tools/round56-env-leg-test.py"`; the path string appears once
as that inert constant, argv references = 0 (driver asserts `"str(TEST)" not in d1`).

## Scoring protocol (all in scratch, per counter's own logic)

Fixtures replicated exactly as the committed counter builds them (blob set: preregistration.json,
`tools/round56-env-leg-battery.py` overridden by the variant, + 3 SIDE files; `git -C <fixture>`
init/add; `git rev-parse --show-toplevel` asserted equal to the fixture dir **before** committing;
throwaway identity passed only with `-C <fixture>`). Checker = committed tip bytes written to
`<work>/outcome-checker.py`, invoked exactly as the counter does:
`python3 outcome-checker.py --repo <fixture> --tip HEAD`. Driver archived at
`.ufo/waves/round-59/w1/out/R04DecoyArgv/drive.py`.

## Control (frozen C1 counter command, unmodified)

`cwd=<lane>`: `python3 tools/round59-c1-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip aca8d0067ea25627c5015c2193c843965148bc8e --work /fast/scratch/hyaku/kama-r59/R04DecoyArgv/work`
→ **exit 0**, `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True` (full output:
`R04DecoyArgv/c1-counter-control.stdout.txt`). Lane worktree counter verified byte-identical to the
tip blob via `git show <tip>:tools/round59-c1-counter.py | cmp - <worktree file>` → `counter worktree==tip-blob`.

## Findings

**F1 — Falsification (high). Unlisted argv-routing no-op is ACCEPTED by the measured C1 checker.**
Command: `python3 outcome-checker.py --repo <D1 fixture> --tip HEAD` → **exit 0**, `runs=5 passed=5/5 errors=0 met=True`.
Baseline: all four legs `call=true returned_true=true`, exit 0. Each fault run: exactly the faulted
leg `returned_true=false`, exit 1, others true — perfect one-leg fault propagation. Full output:
`R04DecoyArgv/D1-decoy-argv.stdout.txt`. The decoy's argv never invokes the committed counter
runner, yet every clause of the checker's own predicate ("each named leg returns a bound expected
outcome; one-leg faults propagate") is satisfied. Under the frozen sentence, a leg that "routes its
argv to `python3 other-script --counter`" **must not meet** — it meets. Under exact frozen reading,
C1-r59 is not met: the decoy-routing clause of the predicate sentence is falsified at the measured tip.

**F2 — Mechanism (medium). N16's rejection is incidental to call count, not to decoy routing.**
`round59-battery-outcome-check.py` main(): `calls_ok[label] = len(calls) == 1 and "--counter" in calls[0]
and "--expect" in calls[0]`; `fake_run` derives the observed state solely from the value after the
`--counter` token, resolved against the committed tree by suffix match (`blob_for`); `argv[0]`/`argv[1]`
are never validated. N16 (`R04DecoyArgv/n16-vs-genuine.diff`: exactly one added decoy line, so 2 calls
per leg) is rejected only because `len(calls)==2`. Deleting its genuine call — the D1 mutation — flips
reject→accept. The committed "decoy --counter" control therefore does not test where argv points.

**F3 — Negative control (informational). Decoy fails closed only when `--counter` stops resolving to committed bytes.**
D3 = D1 with `--counter` value `"other-counter.py"` (uncommitted) → child errors ×5, **exit 1**,
`met=False` (`R04DecoyArgv/D3-decoy-uncommitted-value.stdout.txt`). Acceptance thus requires only
that the `--counter` value resolve to committed counter bytes; the checker scores the counter's
committed source bytes, never its invocation. This matches the freeze's round-58 lesson
`unlisted-noop-survivors`: the enumerated 16/16 all reject while the unlisted routing decoy survives.

## Bounds honored

Lane read-only except this out dir; no lane/fleet commits or pushes; shokuknow untouched; counter,
counters, kill rules, fixtures unaltered after seeing results (all controls built fresh from tip
blobs; decoy constructed before any scoring run). Scratch was
`/fast/scratch/hyaku/kama-r59/R04DecoyArgv/` with `TMPDIR` set explicitly and removed before this
report's completion. Raw evidence archived under `.ufo/waves/round-59/w1/out/R04DecoyArgv/`
(counter control, D1/D3 stdout, decoy sources, diffs, driver).

## Residual risk / verification gaps

- The counter itself cannot score D1: its 17-name list is frozen and the lane is read-only for this
  seat, so the acceptance is demonstrated at the checker layer the counter delegates to (counter runs
  the same committed checker bytes per fixture). The `--checker` flag substitutes the checker script,
  not the battery, so no injection path was available — stated, not assumed.
- Only the two decoy forms above were scored; other routing shapes (env-var routing, argv built by
  concatenation) untested.
- C2 and the external S517/S518 spot-check are out of seat scope; no discernment progress claimed.
- Lane HEAD drift past the frozen tip was not measured beyond noting it; all reads pinned to
  `aca8d0067ea25627c5015c2193c843965148bc8e` per freeze.
