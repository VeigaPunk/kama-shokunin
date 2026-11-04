# report.md — EX01ReconHarness, round 70 w1, lane kama — axes: operability + calibration (judged: calibration)

## Scope executed
Milestone C1: "run facts execute against a tip checkout". Repaired the run-fact harness in
`tools/round41-scorecard-reconcile.py` (imported unchanged by `tools/round42-selfdesc-reconcile.py`).
Read-only on the lane throughout; all writes were my out dir + scratch (`/fast/scratch/hyaku/kama-r70/EX01ReconHarness`,
deleted before yield, TMPDIR-honored, 0 bytes left in /tmp). No subagents and no labrat probe were needed or
spawned. No tools installed/upgraded (host python3 3.14.8 + git 2.56.0 sufficient; pacman untouched). No LSP
available in this seat's tool inventory — symbol-level navigation was not used; plain reads/grep sufficed.

## Files delivered (out dir)
1. `round41-scorecard-reconcile.py` — full candidate bytes. Three hunks, nothing else:
   - docstring RUN bullet: documents the throwaway checkout (round 70: `git clone --shared --no-checkout` +
     `checkout --detach`, replacing the metadata-free `git archive | tar -x` export), truthful and dated;
   - footer: read-only surface now states `clone --shared`, checkout under TMPDIR deleted at exit;
   - `evaluate()` export block: same `tempfile.mkdtemp(prefix="r41c1-")`, same atexit/SIGTERM hooks (round-42
     comments preserved), then clone --shared --no-checkout --quiet, a branch-ref mirror loop (see Rationale),
     and `checkout --detach --quiet <tip>`.
   Every check, counter name, regex, needle, threshold and the `mismatches` arithmetic is byte-identical:
   `run_fact`, `RUN_RE`, counters, details, and main() are untouched. Compiled clean (py_compile exit 0).
2. `diff.patch` — unified diff base-bytes vs candidate (`a/tools/… b/tools/…` paths, 55 lines). Verified:
   `git apply --check` + `git apply` in a fresh fixture repo → `cmp` byte-identical to the candidate.
3. `demo.md` — every command and measured output with exit codes: (a) old bytes r41=2 at base (byte-equal to the
   committed `measured/before/reconciler-at-base.out`), (b) new bytes r41=1 at base with all other counters
   byte-identical (3-line diff) plus a fixture where content is true: old `run_bad=2 mismatches=2 met=False` →
   new `run_bad=0 mismatches=0 met=True`, (c) round42 selftest old vs new (ok arm 9→8; planted arms always ok+1;
   pass=4 fail=1 at base until the citation is re-anchored — the freeze's pass=5 fail=0 target is for the
   landing tip), (d) git-dependent facts (gate, round69 counter) and a git-independent fact (grep) reproduce in
   checkout vs archive-export, (e) checkout==tip proofs (`rev-parse HEAD` == tip, `status --porcelain` empty,
   `diff -r --exclude=.git` vs archive export → TREES-IDENTICAL), patch verification, cleanup proof.
4. This report.

## Rationale and design notes
- Clone primitive matches the house pattern already used by round42's selftest (`git clone -q --shared` +
  `checkout --detach`); `--no-checkout` avoids materializing the default worktree before detaching.
- Detached-HEAD sources (the lane itself has detached HEAD — measured `symbolic-ref -q HEAD` → DETACHED; and
  every round42 selftest fixture is detached) produce clones with NO local branch refs, which would still break
  git-dependent facts that name a branch (the registry gate's lane-tip arm resolves `master`). The mirror loop
  (`for-each-ref refs/heads/` in the source → `update-ref` in the clone) restores the source's branch refs.
  It deliberately uses `update-ref`, NOT `git fetch +refs/heads/*:refs/heads/*`: fetching into the clone's own
  checked-out branch is refused by git (measured: that variant crashed the lane run with an uncaught EvalError
  traceback through round42 — see Findings F3).
- Checkout tree equals the tip tree: measured `diff -r --exclude=.git` against a `git archive | tar -x` export →
  identical (no `.gitattributes` at base, so no export-ignore/filters ever diverged the two). The only addition
  visible to fact commands is the `.git` metadata — which is the point of the repair.
- Cleanup semantics unchanged: same `mkdtemp` (TMPDIR-honored), same `atexit.register(shutil.rmtree, …)` and
  SIGTERM hook; measured 0 leftover `r41c1-*` dirs in TMPDIR and /tmp after all runs.
- Error-path parity: clone/checkout/update-ref failures raise EvalError exactly like the old `git archive` call
  (exit 2 via round41 main); the old `tar … check=True` CalledProcessError path disappeared (strictly narrower
  failure surface). round41's own exit contract (0/1/2) unchanged.

## Measured results (all commands + outputs in demo.md)
| measurement | old bytes | new bytes |
|---|---|---|
| round42 at base 6035e952 | r41=2 mismatches=10 exit 1 (matches committed receipt) | r41=1 mismatches=9 exit 1; all other counters identical |
| gate selftest in checkout | n/a (would be pass=6 fail=1 in export) | GATE_SELFTEST pass=7 fail=0, exit 0 |
| round69 counter in checkout | exit 2 COULD_NOT_EVALUATE in export | exit 1, honest `row_current=false` + STALE_CALIBRATION (agrees with closure_ptr=0) |
| grep fact (`^## ` SKILL.md) | 48 in export | 48 in checkout (identical) |
| fixture (true content) | run_bad=2 mismatches=2 met=False exit 1 | run_bad=0 mismatches=0 met=True exit 0 |
| round42 selftest at base | pass=4 fail=1 (ok arm = 9) | pass=4 fail=1 (ok arm = 8) |

## Findings for the L1 (actionable)
- **F1 — citation defect exposed (blocks r41=0 and the freeze selftest target).** The `## Axes` calibration
  cell cites `NEWEST_CLOSURE … row_current=true` (U+2026 ellipsis; present at base and HEAD). `run_fact` needs a
  stripped stdout line == citation, and the counter prints a full line
  (`NEWEST_CLOSURE newest=corpus/lessons/round-N-verifier-spotcheck.md date=YYYY-MM-DD round=N row_names=… row_current=true`).
  No environment can make that fact pass as cited. Additionally, AT BASE the row is genuinely stale (names
  round-68; newest round-69) so the fact is honestly red there — consistent with the independent closure_ptr=0.
  L1 action at landing: (i) re-anchor the row's closure pointer/`including round` to the newest closure and
  (ii) replace the citation with the exact line printed at the landing tip. Pasteable derivation:
  `cd <landing checkout> && python3 tools/round69-newest-closure-counter.py --since-round 63` → take the
  `NEWEST_CLOSURE …` line verbatim into the backticks after `→` in the calibration row.
- **F2 — the seat's demo spec "new bytes give r41=0 at base" is not achievable at base** for F1's two reasons;
  measured truth is r41=1 at base with every other counter unchanged, and 2→0 (met=True) on the fixture where
  the self-description is true. The harness milestone itself is fully met.
- **F3 — intermediate fetch-variant caution.** A `git fetch +refs/heads/*:refs/heads/*` inside the harness clone
  is refused when the clone has a checked-out branch (attached-HEAD source) and round42 does not catch round41's
  EvalError (it surfaced as a traceback instead of exit 2). The delivered bytes avoid fetch entirely
  (update-ref mirror). Pre-existing gap, unchanged by this work: round42's except-clause does not include
  round41's EvalError; consider adding it if exit-2-on-git-failure is desired there.
- **F4 — landing observed mid-flight.** While this seat measured, the lane working tree's
  `tools/round41-scorecard-reconcile.py` was changed to my candidate bytes plus one addendum hunk
  (`git(export, "update-ref", "refs/heads/master", tip)` after the mirror loop — pins the checkout's master at
  the measured tip). Measured from a copy: base output byte-identical to my candidate and selftest identical
  (ok arm 8, pass=4 fail=1) — behavior-neutral on every measured path. Note the mirror loop already restores
  `refs/heads/master` from the source; the addendum changes its target from "source master" to "measured tip",
  which also makes the gate's lane-tip arm evaluate the measured tip inside round42 selftest fixtures. If both
  stay, the L1 owns that combined semantics; `diff.patch` remains valid for the base→candidate transition.
- **F5 — concurrent sibling edits.** `git status --porcelain` on the lane also shows modified
  `PROVINCE.md`, `SCORECARD.md`, `tools/round65-host-census.py` and new `.ufo/waves/round-70/measured/after/` —
  other seats landing C1/C2 content in parallel. My diff.patch is against base bytes only; land it (or the
  already-present candidate bytes) before/with the content re-anchoring to avoid double-apply.

## Not verified / limits
- The freeze KILL RULE mutation runs (disabling a fact check must flip the verdict) are the L1's landing-gate
  procedure; not run here (would require mutating lane files).
- Behavior at tips newer than base beyond HEAD 0e14facd was not measured; measurements used base (the round's
  frozen measured tip) and my fixture derived from it.
- The landed addendum hunk was measured only at base + selftest at base/HEAD-tip fixtures.

## Deliverable status
Candidate bytes + verified patch + full demo + this report are in
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-70/w1/out/EX01ReconHarness/`.
A copy of this report is at `.ufo/waves/round-70/w1/out/EX01ReconHarness.md` (the validator's trailer path).
Scratch deleted; nothing written outside my out dir, the trailer file, and scratch.
