author: hyaku closure (non-author integrator, @m_opus)

# Round 25 — verifier spot-check (non-author closure, hyaku)

A fresh closure subagent wrote this file. The hyaku orchestrator dispatched it,
not the lane. It did not author the round, and it was not one of the round's
seats. The runtime model reported to this session was
`anthropic/claude-opus-5-5`. `@m_opus` in the header is the closure-role label,
not proof of which provider answered. No review seats were dispatched; every
check below was run by this closure. The checks covered committed bytes only:
base `147f5bdd3228ab712520b5f377346cb2d9a64769` and head
`a46a61815f79c558992e3fdea5e01b738442d6a8`. Scratch extracts were made with
`git archive <rev>` under `/fast/scratch/hyaku/kama-r25-closure/`.

## Decision

Status **ok**, admitted **false**, verdict **rejected-honest-stop**. No axis
is harmed.

- The C1 measured value verifies, but C1 is not a calibration axis-move. It
  counts mismatches between instrument anchors and the auditor's source, not
  mismatches between the lane's self-assessment (SCORECARD/SHONEN) and the
  repo. The lane's own report, lesson and SCORECARD concede this. Calibration
  is therefore `unchanged`. The claim is not relabelled after landing.
- The lowest-axis obligation (AXES.md) is not met. Calibration, depth and
  adjacency are all 7, C2 is on coverage (9), and no stagnation waiver
  applies.
- C2 verifies as measured, and coverage is `improved`.

## Dispatch and completion digest (`.ufo/watchdog.log`, copied)

    2026-10-22T05:16:40-03:00 launch kama round=25 pgid=370096 driver=hyaku-inline attempt=1
    2026-10-22T05:31:20-03:00 lane-dead-no-report kama round=25; retry same round (hyaku-inline attempt=1: stood down at 2026-10-22T08:30Z by Main: process job limit 100 (config says 200) left 8 lanes without seats; lanes in flight cut 8 to 4; capacity decision, not a lane fault; fresh attempt later)
    2026-10-22T06:19:51-03:00 launch kama round=25 pgid=1077911 driver=hyaku-inline attempt=2
    2026-10-22T07:42:41-03:00 complete kama round=25; hyaku-inline attempt=2

Attempt 1 committed `efe58e96` at 05:29:44-03:00, before the 08:30Z
stand-down. Attempt 2 landed the other ten commits.

## Step-1 conformance

| Check | Command | Observed | Result |
|---|---|---|---|
| Report committed by the lane | `git log --format='%an %H' -- .ufo/reports/round-25/kama.md` | `kama-shokunin f1a75c9e4cecf926a2d665e21115a5136e3e3f1f`, committed 07:19:21-03:00; lane tip committed 07:17:40-03:00 | pass (report landed last) |
| SHONEN heading | read report §SHONEN | four lines, all `[~]` with pointers | pass |
| Cited commits are ancestors of the branch | `git merge-base --is-ancestor <h> master` for all 11 cited hashes | all 11 `ok` | pass |
| Pushed | `jj-lane.sh state` | `local=remote=a46a6181… ahead=0 behind=0 tracked=3 untracked=39` | pushed, `ahead=0` |
| Remote tip | `git ls-remote origin refs/heads/master` | `a46a61815f79c558992e3fdea5e01b738442d6a8` | pass |
| Uncommitted round work | `git status --porcelain` | 42 entries, all under `.ufo/waves/round-25/a2-falsify/` | **defect** (below) |
| Prompt carries the contract | `.ufo/prompts/kama-round-25.md`, committed `e4cd8af3`, clean | 350 lines; SHONEN, report path, write scope, L0, push, frontier step, MISSION/AXES and Claim sizing are all present | pass |
| Census | `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` | exit 0, `kama ok`, W04 duplicate-URL warnings only (S108, S109, S110, S112) | pass |
| Rows before → after | `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` over `git show <rev>:corpus/SOURCES.md` | 105 → 113 | matches the report |
| No llama-server left | `pgrep -a llama-server` | none | pass |

**Ruling on the 42 uncommitted paths.** They are uncommitted round work. Late
falsify seats that the lane dispatched wrote them, and a seat the lane
dispatched counts as the lane (LEARNING.md). By `find -newermt` they were
written between 07:17 and 07:41 (-03:00): after the last lane commit and
before the `complete` line. This is a step-1 conformance defect. It does not
change the status. The lane must resolve these paths before its next report,
either by committing them under an entry or by reverting them.

No committed evidence was overwritten. The branch tip and the remote are
both `a46a6181`, and git objects are immutable. Only the working tree
differs, on three tracked paths:

- `advice/CriticC1NoNewHarm.md` is modified. The seat qualified its own
  wording and filled in its pending full-run result (exit 0, 28 mutants,
  26 killed).
- `out/RerunC2Counter/RUNS.txt` gained an appended R7 block.
- `out/RerunC2Counter/receipt-fa3b62ae.copy-from-git-show.json` is deleted.
  It was a byte-identical copy of the committed receipt: both hash to sha256
  `78c51385…b98c` at a46a6181. Nothing is lost.

The L1 released the wave-2 gate reservation while 18 seats were still
running. The report says "the wave-2 reservation is still held", and
`~/.local/state/shokunin-hyaku/wave-slots` now has no kama r25 row. This is a
seat-accounting defect.

## Per-claim re-check

**C1.** I re-measured this claim; I did not rely on the lane's evidence for
the counting value. I ran the preregistered `C1.command` from
`preregistration.json` in each extracted tree:

    147f5bdd: registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']  exit=0
    efe58e96: registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']  exit=0
    1fc41e34: registered 28 stale 0 []  exit=0
    a46a6181: registered 28 stale 0 []  exit=0

`AUDIT` resolves from the instrument's own path (`LANE / "tools/report-landing-audit.py"`).
`git diff --stat 147f5bdd a46a6181 -- tools/report-landing-audit.py` is empty.
Between 1fc41e34 and a46a6181, `isolation-mutants.py` gained 7 docstring lines
and nothing else. These match the reported values.

The supporting full run was verified from committed evidence, not re-run:
`final/c1/c1-tip-mutants.exit` reads `exit=0`, and the JSON reads
`pristine passed, mutants 28, killed 26, surviving [M17-ref-shadow, M20-log-sha-shape]`.

The non-narrowing rules hold. M11 and M17 keep their elements, M33 is a new
id for the second call site, and no id was retired or reused.

Axis fit: **not established.** See the Decision section.

**C2.** I re-measured this claim:

- `python3 .ufo/waves/round-25/count-c2.py` at a46a6181 printed
  `registered 14 observed 14 bound True missing []`, exit 0.
- At efe58e96 there is no counter and no `final/`.
- At 5388b7cf it printed `cannot read receipt … exit=2`.

The before → after matches the report. The counter does not check raw
hashes, so I checked them separately. All 70 sha256 values in the receipt's
`cells[].raw` match files in `final/raw/`: 70 of 70, 0 unmatched. The receipt
records `exit_code 0` and `all_ports_closed true`.

Each cell's per-slot value, slot count and pool equals the entry's table at
lines 25-35:

- K1 2048/4/2048
- X1 2048/4/8192
- X3 512/4/2048
- K7 512/2/1024

L1 shows two HTTP 500 responses, and L2 and L3 show two HTTP 200 each. The
L1 raw log has `Context size has been exceeded.` at lines 1848-1849 and 1863,
and both slots are released at `n_tokens = 1025` (lines 1852 and 1866).

## Per-axis verdicts

| Axis | Verdict | Reason |
|---|---|---|
| calibration | unchanged | C1 does not count self-assessment-versus-repo mismatches. It does not meet the claim-sizing rule for calibration. |
| coverage | improved | C2 verified. K05 had been deferred in the base README (`corpus/README.md` line 125 at 147f5bdd); a new entry now covers it on the lane fixture. |
| freshness | unchanged | The C1 anchor repair is real freshness work, but it was not declared on this axis. It is not credited after landing. |
| operability | unchanged | The capability runs (verified receipt). The tool-safety risks the sentinel listed stay open, and the lane does not claim them fixed. |
| depth | unchanged | SKILL round-25 rows were added. The row-1 `meta.n_ctx_train` error found at fa3b62ae is fixed at head (`SKILL.md:687` names `meta.n_ctx`). |
| adjacency | unchanged | kengaku's capture is cited in the entry, not absorbed. |

No axis is harmed. SCORECARD's round-25 section (+60 lines, appended
without deletion) states the C1 axis-fit correction itself.

## Discernment spot-check

I opened the sources at llama.cpp commit
`704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` through
`raw.githubusercontent.com`. Their sha256 values match the anchor cells:
fit.cpp `1f83da2a…`, server.cpp `21439622…`, server-context.cpp `dd1de0f2…`
and llama-kv-cache.cpp `d0739eaf…`.

| Item | Gate decision | Re-opened source | Agree? | Reason |
|---|---|---|---|---|
| `knowledge/context-capacity.md` | admit | committed receipt plus 70 raw files; K5 and L1 raw logs | agree | The cell values match the receipt, and the three sentences flagged as wrong at fa3b62ae are fixed at head (lines 2, 80-87, 208-209). Two wording defects remain (routed). |
| S108 (server.cpp) | admit, tier A, mined | server.cpp lines 169-186 | agree | The quotes are exact: line 172 `params.n_parallel = 4;`, line 173 `params.kv_unified = true;`, line 184 `params.n_ctx = params.n_parallel * params.kv_unified_per_slot;`. |
| S109 (new row quote) | admit, tier A | server-context.cpp | agree | Line 4301 has `err = "Context size has been exceeded.";`, guarded at line 4298 by `if (n_batch == 1 && ret == 1) {`. The quote is ≤25 words and located. |
| S106 (new row quote) | admit, tier A | fit.cpp | agree on the admit and the quote; partial disagreement on `teaches` | The line 270 quote is exact. The teaches cell says "resolved before measuring", but line 264 measures first and line 276 re-measures. It also omits the `global_surplus < 0` precondition at line 384 and the floor path at lines 414 and 441-444. The lane disclosed this in its report but did not correct it (routed). |
| SrcServerSlotsAuto reading | reject (no row for server-context.cpp) | server-context.cpp and server.cpp | agree | `grep 'n_parallel < 0\|n_parallel = 4'` finds 0 matches in server-context.cpp; the auto branch is server.cpp:169-174. |

**KQ36 ruling.** I upheld the reviewer finding, but only as a defect to
correct; KQ36 is not ungrounded.

KQ36 is grounded. Its motivating lesson row 1 and the round-24 non-author
spot-check (`round-24-verifier-spotcheck.md:80-82`, stale M-series anchors)
support it, and I reproduced the evidence it gives that it can fail (stale 2
→ 0). So it is not a "criterion added with no lesson behind it", and
discernment is not harmed. Two defects stand:

- **F1, "landed tip".** The criterion's own C1 run sits at 1fc41e34, not at
  the landing commit. A run's record can only be committed after the run, so
  the literal text cannot be met. My re-run at a46a6181 gives the same output,
  and the instrument differs only in its docstring, so no landed harm follows.
  The wording needs a qualification.
- **F2, false attribution.** KQ36 cites "§Mistakes rows 1-2". Row 2's fix
  cell says the SKILL registry row "now say[s] M17 survives". At a46a6181,
  `SKILL.md` mentions M17 only at lines 883 and 889, and neither line says it
  survives. That lesson sentence is false and has no erratum.

## Trend verdicts

- **Expansion: improved.**
  - One admitted entry, `context-capacity.md`, covers K05 ground that the
    base coverage map held as deferred. Its `source:` cites the mined rows
    S106-S113 and S060.
  - One capability was shown running: `context-capacity-receipt` (receipt
    5c95c8f1, 70/70 hashes, exit 0).
  - No admitted entry fails its bar on the values checked.
- **Quality: unchanged.**
  - No weaker admitted entry was superseded. The round-20 rule it corrects
    lives in wave evidence, as entry lines 97-98 say.
  - The C1 repair re-verifies tooling, not corpus entries.
  - Remaining imprecisions are wording defects: S106, S109 and S113
    `teaches` cells, entry lines 55-56 and line 137. None of them makes an
    entry's fact false or stale, so quality is not harmed.
- **Discernment: unchanged.**
  - The sampled admits and the reject agree with the gate.
  - However, the round's one new criterion cites a lesson row with a false
    attribution.
  - The C1 axis was misfiled. The lane's own critics caught it under the
    prompt rule, and the round added no criterion for it.
  - The SCORECARD trend line (discernment improved, quality
    unchanged-to-improved) contradicts the report (both unchanged).

## Routed defects (the lane fixes these next round)

1. Resolve the 42 uncommitted `a2-falsify/` paths, either by committing them
   under an entry or by reverting them. The deleted receipt copy may stay
   deleted; it duplicates the committed receipt.
2. KQ36: append a qualification that defines "landed tip" (bytes of the
   measured source and the instrument identical to the landing commit, and
   any later change disclosed). Append an erratum to lesson round-25
   §Mistakes row 2: the SKILL registry row does not say M17 survives. Either
   add that statement to the row or correct the lesson.
3. Append `supersedes` rows (KQ31) for S106: measurement at line 264 comes
   before resolution at 270-276, reduction needs `global_surplus < 0` at 384,
   and the floor path is at 414/441-444. Do the same for S109 (the idle-slot
   purge precondition) and S113 ("per layer"). The lane also reports S107 and
   S112 corrections; I did not verify those.
4. Entry wording:
   - Lines 55-56: "the only trace is a log warning" is overstated. `K5.server.log:1083`
     also has `the slot context (4096) exceeds the training context … capping`.
   - Line 137: each slot held 1024 cells; the logged 1025 includes the token
     that could not be placed.
5. `count-c2.py` accepts receipts without checking raw hashes. Late attack
   seats report receipt mutants that it accepted. Add a hash binding or
   register the limit.
6. Calibration self-check: the SCORECARD round-25 trend line disagrees with
   the report. Append a correction.
7. The wave-2 seat-gate reservation was released while seats were still
   running. Hold it until every seat returns.
8. Next round, work a lowest axis (calibration, depth or adjacency, all at
   7). A calibration claim must count statements in SCORECARD or SHONEN that
   are false against the repo at the before revision.

SHONEN: all four boxes stay `[~]`. This closure re-verified the evidence
behind boxes 2-3 (receipt, command). Promotion is operator-owned. Installs:
none.
