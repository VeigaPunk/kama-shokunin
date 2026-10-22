# KQ36 able-to-fail verification log — ReviewerQualityKQ36 (wave 2, round 25, attempt 2)

Item pin: `corpus/QUALITY.md` KQ36 at `fa3b62ae6475d111eb466d79af616aeebb08bbb9`.
All git invocations against the lane repo are read-only (`show`, `rev-parse`,
`log`, `diff`, `status`, `merge-base --is-ancestor`); the two instrument runs
execute in my own clone. No llama-server child started. No tools installed.

## Bytes identity of the reviewed text

- `git -C <lane> status --porcelain -- corpus/QUALITY.md` → empty; exit 0.
- `git -C <lane> diff --stat fa3b62ae -- corpus/QUALITY.md` → empty; exit 0.
  Working-tree QUALITY.md bytes == fa3b62ae bytes; all reads below are the
  pinned bytes.
- `git -C <lane> diff --stat fa3b62ae HEAD -- corpus/QUALITY.md` → empty
  (exit 0). QUALITY.md unchanged by the 3 commits that landed after
  fa3b62ae; lane HEAD at check time `46be41cf674301953837c8863cd2026e8a21fcb0`.
- `git -C <lane> diff --numstat 147f5bdd fa3b62ae -- corpus/QUALITY.md` →
  `6	0	corpus/QUALITY.md`: append-only holds (KQ36 added at file end,
  QUALITY.md:199-203; no existing line moved).

## KQ36 row text (QUALITY.md:203, full)

| KQ36 | A round that changes a source measured by a registered counting command (one cited by a SCORECARD row, or a claim's registered command) re-runs that command at the round's landed tip and pastes the output. An instrument that cannot evaluate there (its unique-match guard fails, exit 2) is reported as stale, and the value it supports is unverified at that tip. A re-anchor names, per mutant, whether its last recorded kill still holds, so a survivor caused by a moved code path is not hidden by a same-line literal. | A registered command is left stale after its source changes; a could-not-evaluate run is recorded as a pass, hidden, or counted as zero defects; the re-run uses a revision other than the landed tip; a re-anchored mutant's change from killed to surviving is not reported. | `lessons/round-25.md` §Mistakes rows 1-2; `round-24-verifier-spotcheck.md:80-82`. Shown able to fail: the C1 command prints `registered 27 stale 2` at efe58e96 and `registered 28 stale 0` at 1fc41e34; the full instrument exits 2 at efe58e96 (after ten mutants) and 0 at 1fc41e34 with survivors M17 and M20 (`.ufo/waves/round-25/a2-build/advice/ExecC1BaseRun.md`, `.ufo/waves/round-25/final/c1/`). |

## Commit topology

- `git rev-parse --verify efe58e96e6cfbef88a0fba9d64505e18b7ad7356^{commit}` → resolves.
- `git rev-parse --verify 1fc41e346853afd98cbd7010af5db4e54dc877f7^{commit}` → resolves.
- `git merge-base --is-ancestor 1fc41e34 fa3b62ae` → exit 0 (ANCESTOR_OK).
- `git log --oneline 147f5bdd..fa3b62ae -- tools/report-landing-audit.py` →
  empty (exit 0): round 25 did NOT change the measured auditor. The
  instrument changed twice: 1fc41e3 (re-anchor, +30/−3, instrument only) and
  fa3b62a (docstring, +7/−0, instrument only;
  `git diff 1fc41e3 fa3b62ae -- tests/report-audit/isolation-mutants.py` →
  7 inserted docstring lines, no code).

## Registered command — my own runs (extracted committed bytes, mirrored layout, no lane writes)

Command (verbatim from preregistration.json C1.command), run with cwd set to
each revision's extracted tree:

```
registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']
exit=0 rev=efe58e96
registered 28 stale 0 []
exit=0 rev=1fc41e34
registered 28 stale 0 []
exit=0 rev=fa3b62ae
```

The before and after values match the KQ36 row. The third line is new
evidence: the count also holds at the round's actual landed tip fa3b62ae,
which no seat had recorded (all landed tip-run evidence is at 1fc41e34).

## Full instrument — recorded evidence (resolves)

- `.ufo/waves/round-25/final/c1/c1-tip-mutants.exit` → `exit=0`.
- `.ufo/waves/round-25/final/c1/c1-tip-mutants.err` → empty.
- `.ufo/waves/round-25/final/c1/c1-tip-mutants.json` → `"killed": 26`,
  `"mutants": 28`, `"pristine": "passed"`, `"surviving":
  ["M17-ref-shadow", "M20-log-sha-shape"]`, M33 row killed with
  `F13-ref-named-abbreviation` (grid_exit 1). Matches the KQ36 evidence cell.
- `.ufo/waves/round-25/a2-build/advice/ExecC1BaseRun.md` → records exit 2 at
  efe58e96 after M01–M10 grid-evaluated (stderr
  `could-not-evaluate: M11-listing-surrogates: pattern matches 0 times`,
  wall 349.20 s vs pristine grid 33 s), plus `--only` ordering experiments.
  Matches "exits 2 ... (after ten mutants)".
- Guard description verified in source:
  `tests/report-audit/isolation-mutants.py:204-210` —
  `if source.count(old) != 1:` → print `could-not-evaluate: <name>: pattern
  matches N times` → `return 2`, fail-fast inside the per-mutant loop (so
  earlier mutants have run first). "its unique-match guard fails, exit 2" is
  accurate for this instrument.

## Full instrument — my own runs (heavy replication, async job bg_2677, completed)

Script `/fast/scratch/hyaku/kama-r25a2w2/ReviewerQualityKQ36/run-heavy.sh`
in clone `/fast/scratch/hyaku/kama-r25a2w2/ReviewerQualityKQ36/clone`:
checkout fa3b62ae → `python3 tests/report-audit/isolation-mutants.py --json`;
then checkout efe58e96 → same. Output (job bg_2677, 1333.49 s total):

```
=== full instrument at landed tip fa3b62ae ===
fa3b62ae6475d111eb466d79af616aeebb08bbb9
dirty_before=0
tip_exit=0 wall=984s
=== full instrument at pre-repair efe58e96 ===
efe58e96e6cfbef88a0fba9d64505e18b7ad7356
base_exit=2 wall=349s
=== outputs ===
5959 tip-fa3b62ae.json
   0 base-efe58e96.json
--- tip stderr ---        (empty)
--- base stderr ---
could-not-evaluate: M11-listing-surrogates: pattern matches 0 times
dirty_after=4             (my four redirect output files, untracked)
```

- Tip run at the actual landed tip fa3b62ae: exit 0, 26 `killed: true` rows;
  the JSON is byte-identical to the committed
  `.ufo/waves/round-25/final/c1/c1-tip-mutants.json`
  (both sha256 `75ad1e03dff31571dcfe85eca26d7154e509daa60ca092238d6942459c56eda1`
  — the same digest ExecC1TipReplicate recorded for their 1fc41e34 run).
  The 1fc41e3→fa3b62ae instrument delta (7 docstring lines) has zero effect
  on the instrument's verdict document.
- Base run at efe58e96: exit 2, no stdout JSON, stderr exactly as recorded by
  ExecC1BaseRun; wall 349 s matches their 349.20 s (pristine grid ~33 s +
  ten ~31 s mutant grid runs, abort on M11).

## Cross-checks

- SCORECARD.md:1166 registers `python3 tests/report-audit/isolation-mutants.py
  --json` (KQ36 registration route A holds); Round 25 table (SCORECARD:1256)
  registers the C1 one-liner and names measured commit 1fc41e34 with the
  disclosure "(instrument unchanged since, except its docstring)".
- C2 tip-drift shape: `git diff --stat 5c95c8f1 fa3b62ae --
  .ufo/waves/round-25/count-c2.py
  .ufo/waves/round-25/final/context-capacity-receipt.json` → empty (exit 0):
  counter and receipt bytes identical at the landed tip; same pattern,
  immaterial there.
- Motivating citations resolve: `corpus/lessons/round-24-verifier-spotcheck.md:80-82`
  is the stale M-series bullet; `lessons/round-25.md` §Mistakes rows 1-2 are
  the stale-anchor and survival-hidden rows. Evidence files named in the row
  exist (`a2-build/advice/ExecC1BaseRun.md`, `final/c1/`).
- SKILL.md M17-survival check (grep over whole file): the only M17 mentions
  are line 883 (superseded round-24 paragraph: "M17 follows the current
  local-store spelling") and the registry row line 889 ("M11 and M17
  re-anchored; M33 is the second call site of the M17 refusal ... unchanged
  isolation elements remain explicit"). No line of SKILL.md says M17
  survives — while `lessons/round-25.md` Mistakes row 2 fix cell claims
  "the instrument docstring and SKILL registry row now say M17 survives and
  why". The instrument docstring (fa3b62a diff) does say it; the SKILL
  registry row does not.
