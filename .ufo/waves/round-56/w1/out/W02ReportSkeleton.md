# W02ReportSkeleton — round-56 report checklist and evidence inventory

Seat: W02ReportSkeleton (scribe, axis calibration). Lane: `kama-shokunin`, read-only.
Snapshot: **2026-10-27T16:11Z** (`13:11 -03`), lane tip `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7`
(parent/base `e10b6d39af450e8d652be9ac2986768b531fe13f`). Wave `kama-r56-w1` was **live and still
writing** during this inventory: seat reports grew from 8 to 12 between 16:09Z and 16:11Z. No
counter, battery, census, replay or git/jj mutation was run by this seat.

**Verdict: the six required report sections are enumerated with their contract obligations, the
evidence that exists at the snapshot is mapped by pointer and provenance class, and every gap is
named. No measurement, wave result, tally, trend verdict or SHONEN mark is invented.**

## Behavior

1. Read the report contract at `/home/vgpnk/Projects/shokunin/templates/round-prompt.md:99-127`
   (six sections in order; marker rule) and the round-55 lane precedent
   `.ufo/waves/round-55/w1/out/Sc3Report.md`.
2. Inventoried the frozen artifacts, working-tree wave outputs and lane documents with read-only
   commands (`git rev-parse`, `git show --stat`, `git status --porcelain`, `sha256sum`,
   `git show <tip>:<path> | sha256sum`, `grep -cE`, `ls`, `find`, `date`). No test command was
   rerun.
3. Classified every artifact by provenance (below) and drafted the checklist, evidence map,
   calibration cautions and a marker-only fill skeleton for the L1 report.

### Provenance classes used in this file

| Class | Meaning |
|---|---|
| **C** | Committed at freeze `efc6b3ec`; worktree sha256 equals the committed blob (verified for every artifact so marked). |
| **U** | Present only in the lane working tree (`git status` untracked/modified); no commit carries these bytes. |
| **S** | Seat-authored report/receipt under `w1/out/<Seat>/`; advisory, uncommitted, not re-run by this seat. |
| **A** | Absent at snapshot, or no artifact found by the stated command. |

## Gates

Verified by this seat (read-only):

- Freeze commit exists and carries 10 files: `git show --stat efc6b3ec` → 10 files, 2634 insertions
  (`controls/base-c1.out`, `controls/base-c2.out`, `preregistration.json`,
  `sources/ld.so.8.html`, `sources/rtld-audit.7.html`, `corpus/SOURCES.md`, and the four
  `tools/round56-*.py` files).
- Worktree bytes equal freeze blobs for the seven artifacts checked (`sha256sum` vs
  `git show efc6b3ec:<path> | sha256sum`; all `MATCH`): preregistration, both controls, battery,
  env-leg harness, prereg checker, replay counter.
- `measured/`, `census/`, `w1/`, `w1.ready*`, `build_spec.py` and `corpus/lessons/round-56.md`
  are untracked (`git status --porcelain`); `SCORECARD.md` is modified; the round-55 leftovers are
  also still modified/untracked in this working tree (outside round-56 evidence; V04LateOutputs
  is inventorying them).
- `SOURCES.md` row counts: base `e10b6d39` = 252, freeze `efc6b3ec` = 254, worktree = 254
  (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` and the same command
  against `git show <tip>:corpus/SOURCES.md`).
- Document state: `LOG.md` last round heading is `## Round 53` (`LOG.md:2435`); `SCORECARD.md`
  has no `## Round 56` section (grep exit 1) although its head paragraph at `SCORECARD.md:6`
  cites “SCORECARD §Round 56”; SHONEN.md has 4 boxes, all currently `[~]`; the filing target
  `/home/vgpnk/Projects/shokunin/.ufo/reports/round-56/kama.md` does not exist.

Explicitly **not** verified here: claim outcomes (no reruns), wave tally/attack share, trend
verdicts, promotion boxes, or the authorship/chronology of untracked receipts. Seat reports S are
cited as artifacts, not adopted as findings.

## Required-section checklist

Contract: `/home/vgpnk/Projects/shokunin/templates/round-prompt.md:99-127`. Required headings, in
order, with what exists now. Status: **E** = evidence exists, **P** = partial, **A** = absent.

| # | Section (contract line) | Must contain | Evidence that exists at snapshot | Status |
|---|---|---|---|---|
| 1 | **Work performed** (`:104`) | Opens with the round's 1–3 claims and target axes; one bullet per work item, each with an evidence pointer | Claims C1/C2 with axes and scores in `.ufo/waves/round-56/preregistration.json:8-27`; freeze commit `efc6b3ec`; counter/harness/checker sources; S512/S513 rows; 12 seat reports at `w1/out/*.md`; wave spec 64 seats at `w1/spec.json` | P — wave tally/attack share and post-freeze integration items are not yet written |
| 2 | **Landed changes** (`:107`) | Every change tied to a LOG.md entry and to the commit hash carrying it | Freeze commit `efc6b3ec` (10 files); uncommitted `SCORECARD.md` authority/table edit; untracked `corpus/lessons/round-56.md`, `measured/`, `census/`, `w1/` | P — no round-56 LOG entry, no `## Round 56` SCORECARD section, several artifacts uncommitted |
| 3 | **Before → after measurements** (`:109`) | One per claim, with the counting command and the commit measured against | C1: base control `controls/base-c1.out` (C), freeze receipts `measured/{build-c1,m-drop-ldaudit}.out` (U); C2: base control `controls/base-c2.out` (C), freeze output `measured/build-c2.out` (U, no exit field) plus X02 run (S); commands are the two frozen tools | E with caveats — see C1/C2 map and F3/F4/F5 |
| 4 | **Sources & frontier** (`:111`) | SOURCES rows before→after with the counting command; rows added by tier; rows touched old→new; frontier rows advanced; else a line beginning `SOURCES: unchanged —` | Rows 252→254; tiers A=241/B=9/C=4 now (base census A=239/B=9/C=4); S512 mined, S513 rejected (tier A); census start receipt (U) + X06 exit receipt (S); `census/end.out` absent | P — end census and the old→new touched-row list are missing |
| 5 | **Trend verdicts** (`:116`) | One verdict each for `expansion`, `quality`, `discernment` (`improved`/`harmed`/`unchanged`/`unprovable-but-better`) with evidence; no scalar | None found. `registry/verdict-ledger.tsv` tail rows are round 43; no round-56 verdict row observed | A |
| 6 | **SHONEN** (`:118`) | One line per box: `[x]` only with a named non-author verifier, `[~]` with a resolvable pointer, `[ ]` if untouched | `SHONEN.md` has 4 boxes, all `[~]` with author assertions; no named non-author verifier in the file | A (round-56 update) |

Lane precedent (not in the six): round-55 reports also carried **Notes for the closure** and a
**Reported conflicts** block (`Sc3Report.md`); `mori.md` added **Extras**. Treat these as optional
unless the L1 wants parity with round 55.

### 1. Work performed — fill requirements

- Name claims exactly as frozen: C1 operability 8→8 (LD_AUDIT environment-name rejection) and C2
  calibration 7→7 (preregistration/battery roster fidelity); both scores are **declared** in
  `preregistration.json:10,20`, not measured increases.
- For each work item, cite one pointer: path:line, exact command output, or commit hash. Existing
  pointers: `tools/round56-replay-code-audit.py:147` (`BAD_ENV` gains `"LD_AUDIT"` vs
  `tools/round54-replay-code-audit.py:146`), `tools/round56-prereg-check.py`, both control
  receipts, S512/S513 rows, snapshots in `sources/`, and the freeze commit.
- Wave item: `w1/spec.json` declares 64 seats (`reviewer` 16, `critic` 8, `mutation-tester` 8,
  `executor` 8, `scout` 8, `sentinel` 4, `revenger` 4, `scribe` 4, `connector` 2,
  `simplifier` 2; sum 64) and `maxLanes` 64. Do **not** write completed/tallied seat counts or an
  attack share until the wave settles and the L1 counts them; at 16:11Z, 12 seat reports existed
  and 8 seat directories had no same-name report.
- Mark unmeasured items with `[L1: …]` rather than inferring.

### 2. Landed changes — fill requirements

- Freeze commit `efc6b3ec` carries the counter/harness/checker, preregistration, two red base
  controls, both source snapshots, and the +2 SOURCES rows. This is the only round-56 commit seen.
- Missing before the section can be complete:
  - a `LOG.md` round-56 entry (last heading `## Round 53`, `LOG.md:2435`);
  - a `## Round 56` SCORECARD section (absent; `SCORECARD.md:6` cites it; last round section is
    `## Round 55` at `SCORECARD.md:3057`, live plan at `:3105`);
  - commit hashes carrying `corpus/lessons/round-56.md`, `measured/`, `census/`, `w1/`.
- The `SCORECARD.md` working-tree diff (6 lines, uncommitted) changes the authority paragraph
  round 55→56, the depth row’s re-anchor round 54→55, and the calibration run-fact 41→42 /
  latest-closure pointer 53→55. Report those as uncommitted edits, not landed commits.

### 3. Before → after — exact evidence available

**C1 (operability).** Counting command shape (as frozen):

```
python3 tools/round56-env-leg-test.py --counter <counter> --expect {missed,detected}
```

| Leg | Observed receipt | Observed fields | Class |
|---|---|---|---|
| base-old-counter (`tools/round54-replay-code-audit.py`, `BAD_ENV` at `:146` lacks LD_AUDIT) | `controls/base-c1.out` | `ld_audit=missed pid=1758490 problems=[]`, `exit=0` | C |
| base-old-counter rerun | `measured/base-c1.out` | `ld_audit=missed pid=1759696 problems=[]`, `exit=0` | U |
| round56-counter (`:147` adds `"LD_AUDIT"`) | `measured/build-c1.out` | `ld_audit=detected pid=1759698 problems=['env: server environment carries LD_AUDIT']`, `exit=0` | U |
| one-line mutant (`m-drop-ldaudit`) | `measured/m-drop-ldaudit.out` | `ld_audit=missed pid=1759704 problems=[]`, `exit=0` | U |
| mutant vs `--expect detected` (claim's wording) | X04 `harness-mutant-expect-detected.out`; X01 `replay-m-drop-ldaudit-expect-detected.out` | `ld_audit=missed`, **exit=1** | S |

Every C1 receipt also carries glibc stderr:
`ERROR: ld.so: object '/usr/lib/libexpat.so.1' cannot be loaded as audit interface: undefined symbol: la_version; ignored.`
This matches the preregistration `limits` (name-presence test, not successful auditor injection).

**C2 (calibration).** Counting command:

```
python3 tools/round56-prereg-check.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip <tip>
```

| Leg | Observed receipt | Observed fields | Class |
|---|---|---|---|
| base `e10b6d39` | `controls/base-c2.out` | `present=0 roster_match=0 kills=0 controls=0 met=False`, `exit=1` (third line) | C |
| freeze `efc6b3ec` | `measured/build-c2.out` (2 lines, no exit field) | `present=1 roster_match=1 kills=1 controls=2 met=True` | U |
| freeze `efc6b3ec` assigned run | X02 `freeze-c2.out` | same fields, **exit 0** | S |
| one-field designation mutation | X02 `mutant-designation-c2.out` | `present=1 roster_match=0 kills=1 controls=2 met=False`, exit 1 | S |

Roster equality: battery `ROSTER` (`tools/round56-env-leg-battery.py:15`) equals
`preregistration.json` `battery.roster` — 3 entries: `base-old-counter` control/`missed`,
`round56-counter` positive-control/`detected`, `m-drop-ldaudit` kill/`missed` (verified by X01/X02;
source bytes read here).

**Frozen digests:** `tools/round56-replay-code-audit.py` =
`fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f` (equals C1
`counter_sha256`); `tools/round56-prereg-check.py` =
`c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853` (equals C2
`counter_sha256`). The env-leg harness (`ec7a2519…82ac`) and battery (`79b19596…335c`) have **no**
frozen digest.

### 4. Sources & frontier — fill requirements

- Counting commands are the registry’s own (`/home/vgpnk/Projects/shokunin/CORPUS.md:134-141`):
  `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` for rows, and the
  tier/status `awk` lines at `:139,:141`.
- Observed: rows 252 (base) → 254 (freeze and worktree); tiers now A=241, B=9, C=4; base census
  (X06 S) reported rows 252, A=239, B=9, C=4, mined 228, queued 8, rejected 16, missing 0; the
  worktree census receipt `X06Census/census-now.out` (S) reports rows 254, A=241, B=9, C=4,
  mined 229, queued 8, rejected 17, missing 0.
- Rows added: S512 (`rtld-audit(7)`, docs/A/mined) and S513 (`ld.so(8)`, docs/A/rejected) — both
  tier A; freeze diff is +4 lines (two rows, two blank lines). No existing row status/recheck
  change appears in the freeze diff.
- Frontier evidence: S512 quote/lesson Gate (`corpus/lessons/round-56.md`, U), snapshot
  `.ufo/waves/round-56/sources/rtld-audit.7.html` (C), X07 quote-anchor check (S); census
  `start.out` (U, 99 lines, sha256 `bdc5c03c…43e1`) with measured equivalent exit 0
  (`X06Census/exits.txt`), and **`census/end.out` absent**. The “After” line in the lesson
  explicitly defers to that missing file.
- The report must either supply the end-of-round census or state the conformance defect; do not
  present start as end.

### 5. Trend verdicts — fill requirements

No verdict artifact exists to copy. The L1 must write three verdicts with evidence; the contract
says a report missing this section (and Sources & frontier) is **not** a marker failure but is a
minimum-content conformance defect (`templates/round-prompt.md:121-127`). Do not derive verdicts
from the frozen score strings or from seat reports automatically.

### 6. SHONEN — fill requirements

`SHONEN.md` (11 lines) has four boxes, all `[~]`:
SKILL.md decision tables; one end-to-end logged task; executable-without-oral-context;
no cross-domain bleed. For round 56, `[x]` may be used only with a named non-author verifier; a
`[~]` needs a resolvable pointer. No named non-author verifier for these boxes was found in the
file. The wave supplies non-author seats, but none is recorded as a promotion verifier.

## Claim evidence map (compact)

| Claim | Frozen predicate/target | Base observation | Freeze observation | Falsifier status in observed artifacts |
|---|---|---|---|---|
| C1 | Base counter misses; round-56 detects; mutant misses and fails expected-detected; counter digest frozen | `missed`, exit 0 (C + U) | `detected` with named problem, exit 0 (U) | No observed falsifier: base missed, new detected, mutant missed, digest equal. Expected-detected exit 1 is S-only (X01/X04), not in `measured/`. |
| C2 | Exact roster match with 1 kill + 2 controls; base red; freeze green; digest frozen | `present=0 … met=False`, exit 1 (C) | `present=1 roster_match=1 kills=1 controls=2 met=True` (U; exit 0 only in S) | No observed falsifier: freeze green, base red, digest equal, one-field mutation `roster_match=0 met=False` (S). |

## Evidence inventory at snapshot

| Path | What exists | Class |
|---|---|---|
| `.ufo/waves/round-56/preregistration.json` | Claims, scores, targets, kill rules, roster, controls, limits; sha256 `fa4b5a10…ee68` | C |
| `.ufo/waves/round-56/controls/base-c1.out`, `base-c2.out` | Red base controls, 3 lines each; sha256 `48a6f745…acec`, `13d5516a…d9fc` | C |
| `.ufo/waves/round-56/measured/{base-c1,build-c1,build-c2,m-drop-ldaudit}.out` | Freeze measurement receipts; sha256 `ece98c2f…`, `1aea0d27…`, `01d95f52…`, `93813bd7…` | U |
| `.ufo/waves/round-56/sources/{rtld-audit.7,ld.so.8}.html` | Source snapshots for S512/S513 | C |
| `tools/round56-{replay-code-audit,env-leg-test,env-leg-battery,prereg-check}.py` | Committed counter, harness, battery, checker; only the counter and checker carry preregistered digests | C |
| `corpus/SOURCES.md` | Rows 252→254; S512/S513 appended in freeze commit | C (rows) |
| `.ufo/waves/round-56/census/start.out` | 99-line start validation; sha256 `bdc5c03c…` (per X06); stale by the S513 warning; no recorded exit field | U |
| `.ufo/waves/round-56/census/end.out` | End-of-round census | A |
| `corpus/lessons/round-56.md` | Claims, Gate (S512/S513), Mistakes, census-before sentence; sha256 `d2875ca8…30ee`; “After” deferred to missing end.out | U |
| `.ufo/waves/round-56/w1/spec.json`, `dispatch.json`, `validate.out` | 64-seat wave spec, dispatch, validation output | U |
| `.ufo/waves/round-56/w1/out/*.md` | 12 seat reports at 16:11Z: `M01DropAudit`, `R03C1Build`, `S02Scratch`, `S03SecretScan`, `V01RouteDefects`, `V04LateOutputs`, `X01ReplayC1`, `X02ReplayC2`, `X03CleanEnv`, `X04EnvNames`, `X06Census`, `X07Anchors` | S |
| `.ufo/waves/round-56/w1/out/<Seat>/` | 19 seat directories; 8 had no same-name report at snapshot: `Q03CorpusContract`, `R11C2Mutation`, `R13Lesson`, `S01WriteScope`, `S04Policy`, `V02StaleLesson`, `X05ControlSeparation`, `X08ExitReceipts` | S |
| `SCORECARD.md` | Authority paragraph already says round 56 and cites a `§Round 56` that does not exist; diff is uncommitted (6 lines) | U |
| `LOG.md` | No round-56 entry; last heading Round 53 | A (round 56) |
| `SHONEN.md` | 4 boxes, all `[~]`; no named non-author verifier | existing state |
| `.ufo/reports/round-56/kama.md` (fleet repo) | Filing target | A |

## Calibration cautions (report must not overclaim)

- **F1 — `measured/` is untracked.** All four measurement receipts are `??` in
  `git status --porcelain`. Do not call them “committed receipts.” Either commit them before
  filing or label them working-tree receipts with their sha256s.
- **F2 — `census/start.out` is untracked and stale by one committed row.** X06 measured the live
  output at 100 lines (98 `W04`) vs the receipt’s 99 (97 `W04`), the delta being the S513 warning;
  the receipt itself records no exit code (exit 0 is the equivalent command’s measured exit).
  `census/end.out` is absent.
- **F3 — the frozen C1 digest covers one file, but C1 names two.** `counter_sha256` equals
  `tools/round56-replay-code-audit.py`; the harness `tools/round56-env-leg-test.py` and battery
  have no frozen digest. Write “the counter digest is frozen; the harness/battery are not,” not
  “both counters are frozen.”
- **F4 — `measured/build-c2.out` has no exit field.** The checker writes two lines and returns
  through its exit status; X08 marks this receipt `FAIL — missing-field:exit`. The freeze exit 0
  is evidenced only by X02’s run (`freeze-c2.out`), which is S, not U/C.
- **F5 — control receipts contain `exit=` lines their tools do not print.** The checker emits two
  lines; `controls/base-c2.out` carries a third operator-appended `exit=1`. The env-leg harness
  prints one stdout line and exits; `controls/base-c1.out`/`measured/*` carry an added `exit=`
  line (the battery adds it only to its own `OUT` receipts). Values agree with the frozen targets,
  but the line’s producer is not self-recorded. Do not claim byte-reproducibility from the frozen
  tool alone.
- **F6 — C1’s “expected-detected assertion” is not what the committed battery runs.** The battery
  gives `m-drop-ldaudit` `expected="missed"` (`tools/round56-env-leg-battery.py:18,50`), so its
  `pass` means “missed.” The expected-detected failure is a separate invocation measured by X01
  and X04 (exit 1). Say both; a battery-exit-0-only reading would not discriminate.
- **F7 — “round-55 counter” names `tools/round54-replay-code-audit.py`.** At the round-55 base tip
  `e10b6d39` that is the newest replay counter (X01 D2; X04 digest `c81fe971…`). Use the file name
  to avoid a false impression that a `round55-*.py` exists.
- **F8 — the battery is not seat-runnable unmodified.** It writes fixed `OUT` under the lane and a
  fixed `/fast/scratch/hyaku/kama-r56/l1-battery` scratch root (X01 D1). A replay in the report
  must say a copy with only those two constants changed was used, or name the write-bound
  violation.
- **F9 — scores are declared, not measured.** `8 -> 8` and `7 -> 7` are the frozen claim strings
  (`preregistration.json:10,20`); no capability row enters. Do not write “improved by N.”
- **F10 — SCORECARD/LOG are not ready.** The authority paragraph cites `SCORECARD §Round 56`
  which is absent; the SCORECARD edit is uncommitted; LOG has no round-56 heading. The
  “Landed changes” section cannot be complete until the L1 adds them.
- **F11 — the lesson is untracked and has an unfinished-looking fragment.** `corpus/lessons/round-56.md:19`
  ends with the literal text `Fix shown…`; the Census “After” section points at the missing
  `census/end.out`. Confirm or finish before citing the lesson as landed evidence.
- **F12 — no trend verdicts or SHONEN update exist.** Do not infer them from the score table or
  from seat reports. The verdict ledger’s last rows are round 43; SHONEN remains at its
  pre-round state.

## Ready-to-fill skeleton (headings and marker slots only)

The L1 report belongs at `/home/vgpnk/Projects/shokunin/.ufo/reports/round-56/kama.md` (fleet
repo; absent at snapshot). Fill in this order; every `[L1: …]` must resolve to a path:line,
command output or commit hash before filing.

`[H2]` below denotes the literal `##` heading in the L1 report; the token is spelled this way so
this checklist’s own heading scan is not polluted.

```
# kama — round 56 report
[L1: declared claims C1 operability 8->8, C2 calibration 7->7; no capability]
[H2] Work performed
[L1: bullet per work item; freeze commit efc6b3ec; S512/S513; wave item + settled tally]
[H2] Landed changes
[L1: LOG.md round-56 entry + commit hash per change; SCORECARD §Round 56; lesson/measured/census commits]
[H2] Before → after measurements
[L1: C1 command + base/measured receipts + expected-detected exit 1; C2 command + base/freeze + mutant; commits]
[H2] Sources & frontier
[L1: rows 252->254 command; A=239->241; S512/S513; end census or named conformance defect]
[H2] Trend verdicts
[L1: expansion / quality / discernment + evidence; not derivable from frozen scores]
[H2] SHONEN
[L1: 4 lines; [x] only with named non-author; [~] pointer; [ ] untouched]
```

Marker rule check before filing: no placeholder text; all six headings present in order; every
numeric and verdict resolves to a pointer; missing Sources & frontier/Trend verdicts would be a
conformance defect but not a marker predicate (`templates/round-prompt.md:121-127`).

## Out of scope

- Rerunning the counter, harness, battery, census, replay, or any verification seat work.
- Adjudicating C1/C2, seat findings, conflicts, wave outcomes, trend verdicts or SHONEN marks.
- Editing the lane, preregistration, counters, receipts, SCORECARD/LOG/SHONEN, or the fleet repo;
  filing the L1 report.
- Fixing any defect named above; all proposed fixes remain proposals for the L1/next round.

## Bounds observed

- Only written path: `.ufo/waves/round-56/w1/out/W02ReportSkeleton.md` (this file). No lane file,
  git/jj state, fleet-root file or sibling lane touched.
- Scratch `/fast/scratch/hyaku/kama-r56/W02ReportSkeleton/` created with `TMPDIR` set explicitly
  and removed before yielding; `/tmp` unused.
- No pacman, uv, npx or other install; no tools changed. `tool_installs: []`.

## Artifacts

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-56/w1/out/W02ReportSkeleton.md`
- `/fast/scratch/hyaku/kama-r56/W02ReportSkeleton/` (created, then removed)
