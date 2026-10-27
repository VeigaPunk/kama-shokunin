# W02ReportAudit — round-59 report-contract completeness checklist

Seat W02ReportAudit (scribe, leaf). Object of audit: **the round-59 report contract and its
evidence supply**, for the six named areas — claims, census, trend verdicts, SHONEN,
stale-lane, source. Output is a checklist only; no final report is drafted and no claim is
graded. Lane tree read-only except this file; fleet root and sibling lanes untouched; no
git/jj mutation; no seat dispatched.

Contract authorities read (exact):
- `templates/round-prompt.md:99-130` (§4 Report contract + marker rule), `:49-79` (§2b frontier step).
- `.ufo/prompts/kama-round-59.md:99-130` (round-59 instance of §4), `:49-79` (§2b), `:455-482` (§6 extras/commit), `:595-620` (§10 quarantine / considerthese), `:240-250` (§10 standing duty).
- `AXES.md:20-23` (trend↔axis map), `:24-49` (claim rules, separability, lowest-axis floor, exploratory).
- Machine predicates: `scripts/shokunin-watchdog.sh:54` (`MIN_REPORT_BYTES=400`), `:186-207`
  (`report_of`: SHONEN marker regex + byte floor + same-round digest baseline), `:347-364`
  (`report_sources_conformance`: heading regex `^#{1,6}[[:space:]]+Sources[[:space:]]*&[[:space:]]*frontier`).
- Frozen claim bytes: `.ufo/waves/round-59/controls/freeze.txt` (sha256
  `3f7c1c3f8dcfc67f45ad8be44de78978fa2a1941c4c47f336ac65cbe9d7544d7`).

Status vocabulary: **READY** = the required artifact already exists in committed/observable
bytes; **OPEN** = not yet produced (normal mid-wave, blocks filing); **DEFECT** = the contract
as written cannot be satisfied by the artifacts it names; **N/A** = clause does not apply.

## A. Claims (contract §2 steps 1-5; `AXES.md:24-49`; report "Work performed" + "Before → after")

| # | Requirement (clause) | Required artifact | Observed now | Status |
|---|---|---|---|---|
| A1 | 1-3 claims, each one axis-move on a **distinct** axis (§2.2, AXES.md:32-37) | 2 claims: C1 operability, C2 calibration | `freeze.txt` lines "C1 operability 8 -> 8", "C2 calibration 7 -> 7" — two axes, two claims | READY |
| A2 | ≥1 claim on the lowest-scoring non-retired axis unless nudge waives (AXES.md:37-40) | calibration is lowest (7 < operability 8) | `freeze.txt` C2 heading: "lowest assigned axis; observed calibration 7 < operability 8; nudge inactive"; `SCORECARD.md:6` current-authority line repeats it | READY |
| A3 | Causal separability — each claim verifiable without the other landing (§2.3) | per-claim independent scoring receipt | C1 scored at `aca8d006` (`.ufo/waves/round-59/controls/c1-candidate-final.out`), C2 at `2c7443ab` (`.ufo/waves/round-59/controls/c2-after.out`) — different commits, different counters | OPEN (receipt exists; no separability run recorded in lane yet — K03 seat in flight) |
| A4 | Per-claim counting command + **the commit it was measured against** (§4) | exact argv + measured rev | argv supplied for both (`round59-c1-counter.py --repo/--tip/--work`; `round59-c2-counter.py --repo/--tip/--fleet-ref HEAD`); measured revs `aca8d006`, `2c7443ab` appear as `tip=` inside both receipts | READY |
| A5 | Before→after per claim (§4) | before arm + after arm | C1: `c1-oldchecker-final.out` `genuine=1/1 benign=3/3 noop_rejected=13/16 errors=0 met=False` (exit 1, `c1-oldchecker-final.exit`) → `c1-candidate-final.out` `noop_rejected=16/16 met=True` (exit 0). C2: `c2-base.out` `mismatches=3 met=False` (exit 1) → `c2-after.out` `mismatches=0 met=True` (exit 0); plus live-HEAD replay `c2-after-current-head.out` `fleet=3f3dd973… met=True` (exit 0) | READY |
| A6 | SCORECARD per-claim row: score delta, evidence pointer, counting command, measured commit (§2.5) | `## Round 59` section with claim table | `grep -n '^## Round 59' SCORECARD.md` → no match (exit 1). Only `SCORECARD.md:3187 ### Planned (round 59)` (two plan sentences, no table). `494c1657` changed `SCORECARD.md` by 2 lines (calibration-row counter reference), not a claim table | OPEN |
| A7 | No post-freeze narrowing; predicate identical in plan, counter code, receipt label (§9; freeze line "This predicate is frozen") | frozen predicate reused verbatim | `freeze.txt` holds predicate/sentence/counter/kill rule per claim; counters unchanged after measurement (`git diff --stat aca8d006..HEAD -- tools/round59-c1-counter.py tools/round59-battery-outcome-check.py tests/round59-variants…` → empty; `2c7443ab..HEAD -- tools/round59-c2-counter.py SCORECARD.md` → empty; exit 0 both) | READY (label-vs-code parity is K02's attack, not audited here) |
| A8 | Admission reported, not asserted: every claim verifies and no axis harmed; "No claim is admitted on seat consensus alone" (freeze tail) | report states verdicts, no admission claim | not yet written; C1/C2 axes both `→` same value, so "no scalar" must be stated | OPEN |

## B. Census (§2b.2; `CORPUS.md` §SOURCES.md; report "Sources & frontier")

| # | Requirement | Required artifact | Observed now | Status |
|---|---|---|---|---|
| B1 | Round-start census output + exit code, mandated command `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root … kama` | `census/start.out`, `census/start.exit` | both present; `start.exit` = `0`; `start.out` = validate-format W01/W04 lines + `ok …/corpus/SOURCES.md` | READY (format matches validate mode; invocation itself not provable from the file) |
| B2 | Round-end census output + exit 0 (required for conformance) | `census/end.out`, `census/end.exit` | absent — `.ufo/waves/round-59/census/` contains only `start.*` | OPEN |
| B3 | Rows before→after **with the counting command** (§4) | a command that prints a row count | mandated `validate` mode prints **no row count** (see D1); `census` mode does: `sources-census.sh census --root … kama` → `kama rows 259` (exit 0) | DEFECT-as-written (contract names the validate command but requires a count; see D1) |
| B4 | Exit-2 condition only for a missing registry at round start | n/a | `corpus/SOURCES.md` exists; start exit 0 | N/A |
| B5 | Census conformance is not a pass predicate (driver warning only) | report records defect if any | no defect yet because start is clean | READY |

## C. Trend verdicts (§4 "Trend verdicts"; AXES.md:20-23)

| # | Requirement | Required artifact | Observed now | Status |
|---|---|---|---|---|
| C1 | One verdict each for `expansion`, `quality`, `discernment` from the closed set (`improved`/`harmed`/`unchanged`/`unprovable-but-better`), with evidence, **no scalar** | three verdict lines | none in lane (`grep -n 'round 59\|Round 59' SCORECARD.md` → only `:53`, `:3187`; `LOG.md` → no match at all) | OPEN |
| C2 | Discernment must not claim progress without a recorded outside S517/S518 admit/reject spot-check (assignment bound: "do not claim discernment progress"; freeze: "No claim is admitted on seat consensus alone") | `unchanged`/`unprovable` verdict naming the absent outside record | no `corpus/lessons/round-58-verifier-spotcheck.md` (`ls corpus/lessons | grep round-58` → only `round-58.md`); no S517/S518 outside disposition anywhere in lane; r58 report already lands `unprovable-but-better`, which must not be upgraded | OPEN (constraint active) |
| C3 | No score increase claimed; claim axes are `→` same-value | verdict text | `freeze.txt`: "No score increases or capability acquisition claimed"; `SCORECARD.md:6` scores operability 8 / calibration 7 | READY |
| C4 | Trend↔axis consistency (discernment ↔ calibration, AXES.md:20-23) | verdict wording mapped to axes | not written; a `quality — improved` on C1-only evidence would need the depth/freshness/operability mapping stated | OPEN |

## D. SHONEN (§4 "SHONEN"; §6 item 4 grep gate; watchdog `report_of`)

| # | Requirement | Required artifact | Observed now | Status |
|---|---|---|---|---|
| D1 | `## SHONEN` heading exactly once, one line per SHONEN.md box | 4 `[x]`/`[~]`/`[ ]` lines | `SHONEN.md` has 4 boxes (`grep -c '^\- \[' SHONEN.md` → `4`), all `[~]` author assertions; report file absent | OPEN |
| D2 | `[x]` only with a named non-author verifier | pointer per `[x]` | no non-author verifier recorded for any box; all four are author assertions citing lane bytes | OPEN (four `[~]` lines are the conforming form) |
| D3 | Pre-commit `grep -c '^## SHONEN'` prints 1 (§6 item 4, `lane-addendum.md:332-333`) | grep output in the filing step | not yet runnable (no report); r58 precedent prints `1` (`.ufo/reports/round-58/kama.md`) | OPEN |
| D4 | Watchdog marker: `^#+[[:space:]]*SHONEN([^[:alnum:]_]|$)` **or** `- **SHONEN**`, plus file ≥400 bytes; same-round digest must differ from baseline | heading + size | `.ufo/state/kama.report-baseline` = `59 e3b0c442…b855` (round 59, digest of the empty string) → any real report differs; floor 400 B (`shokunin-watchdog.sh:54,186-207`) | READY (predicate understood; artifact absent) |

## E. Stale-lane (§6 item 6; r58 precedent `.ufo/reports/round-58/kama.md:50`)

| # | Requirement | Required artifact | Observed now | Status |
|---|---|---|---|---|
| E1 | A `Stale-lane` line: respawn-per-round driver; no other mission of this lane open | one line in the report | absent (no report) | OPEN |
| E2 | Any liveness/age claim must be command-backed | watchdog counts | `grep -n 'kama round=59' .ufo/watchdog.log` → only `:1784 2026-10-27T17:13:51-03:00 launch kama round=59 pgid=3879171 driver=hyaku-inline attempt=1`; `grep -nE 'complete kama round=59|lane-dead-no-report kama round=59'` → no match | OPEN (a "closed" claim would be unsupported; a launch-only citation is supported) |
| E3 | Tool installs line (§6 item 6, §6 item 7 disclosure rule) | "none" or tool/version/channel/reason | nothing observed in round-59 wave evidence; no pacman/uv action by this seat | READY if stated as "none identified" |

## F. Source — "Sources & frontier" + §2b.1/§2b.3/§2b.4 + §10 (§4)

| # | Requirement | Required artifact | Observed now | Status |
|---|---|---|---|---|
| F1 | `SOURCES.md` rows before→after with the counting command | start count + end count | start `259` (census mode, exit 0); end absent (B2). Tiers at start: `tier.A 245 / tier.B 10 / tier.C 4`; statuses `mined 234 / queued 8 / rejected 17` | OPEN |
| F2 | Rows added by tier | count per tier | none added yet: rows at freeze base `8f7f58cd` = `259` (same grep), max id `S518`; no r59 append | OPEN |
| F3 | Rows touched old→new (`status`/`recheck`/`used-by`) | old→new list | none recorded in lane for r59 | OPEN |
| F4 | Frontier rows advanced (README/coverage map) | pointer | `git diff --stat 8f7f58cd..HEAD -- corpus/` → empty (exit 0): no `corpus/README.md`, no lesson, no knowledge entry changed this round | OPEN |
| F5 | **≥1 sourced claim resting on a row opened *this round*** (§2b.4) | new `S###` row opened r59 + citation from the claim's evidence | **DEFECT risk**: the freeze's C1 is "sourced on S517", but S517 is a round-58 row (`corpus/SOURCES.md:270`, `status mined`, `used-by` includes `corpus/lessons/round-58.md`, `tools/round58-battery-exec-check.py`); its `opened` cell is 2026-10-27 but the round is 58. No row was added in r59 (`259` rows at base and at tip) | DEFECT (unmet unless r59 opens a row or records the conformance defect) |
| F6 | `corpus/lessons/round-59.md` `## Gate` with URL, access date, ≤25-word located quote for **every** new row; ≥1 admit and ≥1 reject | lesson file | absent (`ls corpus/lessons/round-59.md` → No such file); latest lesson is `round-58.md` | OPEN |
| F7 | `## Mistakes` row: class · evidence · captured-by · fix (or the sweep that found none) (§2b.3) | lesson section | same file absent | OPEN |
| F8 | Quarantine: verdict per register-slice row (hand-checked this round; `payload-absent` rows refused/unverifiable, never appended) | 7 row verdicts | `.ufo/waves/round-59/quarantine-slice.txt` = `S200 S202 S206 S210 S211 S224 S230`, each `payload-absent`; no verdict list in lane yet (S05 seat output only, which is lane-dispatched advice) | OPEN |
| F9 | `Assimilation: none` (allowed, no penalty) or adoption evidence + id-collision/renumber paste (§10) | one report line (+ pastes if adopting) | no `.ufo/waves/round-59/assimilation/` directory (`ls` exit 2) → no `reg-ids`/`staged-ids`/`collisions`/renumber map can exist to paste; adoption closed | READY (the "none" line is the conforming form) |
| F10 | `considerthese/` proposal named in the report, or "none fits" (`:217`, `:615-620`) | one report line | newest file `considerthese/2026-10-26.md`; nothing records a r59 selection | OPEN |
| F11 | Watchdog conformance heading must literally match `^#{1,6} [+]*Sources[[:space:]]*&[[:space:]]*frontier` (case-insensitive, `&` required) | report heading | predicate at `shokunin-watchdog.sh:356`; a `### Sources and frontier` or bold-only marker logs `sources-conformance-defect` | READY (form is known; artifact absent) |
| F12 | Sources & frontier and Trend verdicts are **not** marker predicates — absence is `ok` + minimum-content defect, never a relaunch (`:121-127`) | report discipline | predicate text read; must not be presented as a pass/fail gate in the report | READY |

## G. Filing mechanics (operability of the report itself; §4/§5/§6 item 4)

| # | Requirement | Required artifact | Observed now | Status |
|---|---|---|---|---|
| G1 | Report path `{{FLEET_ROOT}}/.ufo/reports/round-59/kama.md` | file | absent (`ls .ufo/reports/round-59/` → chousa, kake, kotoba, kotodama, kumitate) | OPEN (and outside this seat's write bounds) |
| G2 | Pre-report gate: `git -C … ls-remote origin refs/heads/master` prints the final lane hash | command output | lane branch `master` = `4a541190b6d494a4e99116249632e99aab80adcc` (`git rev-parse master`); not re-checked against origin here (no network read attempted) | OPEN |
| G3 | Report committed only via `fleet-commit.sh --as kama -m "round-59: kama report" -- .ufo/reports/round-59/kama.md`, lands last, cites pushed lane hash | commit | not filed | OPEN |
| G4 | `MIN_REPORT_BYTES` floor 400 and SHONEN marker satisfied (watchdog) | file size/marker | baseline round 59 with empty-string digest exists; floor 400 | READY (predicate) |

## Findings (each names the clause attacked and the exact observation)

**W02-1 — Census contract names a command that cannot produce the number the report must show (B3/D1).**
`scripts/sources-census.sh:17-25` documents `validate` output as E/W codes only and `census`
output as `rows | tier.X | status.X`. The r59 start file confirms it:
`census/start.exit` = `0`, `census/start.out` ends `ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`
with no row line. Running the other mode read-only:
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin kama` →
`kama rows 259 / tier.A 245 / tier.B 10 / tier.C 4 / status.mined 234 / status.queued 8 / status.rejected 17 / FLEET.rows 259 / … / missing 0`, exit `0`.
The r58 precedent worked around this with an unnamed `grep -cE` (`round-58/kama.md` Sources section).
Checklist consequence: the report must paste the mandated validate output **and** an explicitly
named counting invocation (census mode or the grep), or "rows before→after" is unsourced.

**W02-2 — §2b.4 "a row opened this round" is not met by S517 (F5).**
C1's freeze line says "sourced on S517"; `corpus/SOURCES.md:270` shows S517 as a round-58 row
(`used-by` = `tools/round58-battery-exec-check.py, corpus/knowledge/battery-execution-evidence.md,
corpus/lessons/round-58.md`), and r58's report records it as opened in round 58. Row counts:
`grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` → `259` at `8f7f58cd` and `259` at
`4a541190`. So no row was opened in round 59. The report can satisfy the clause only by opening a
row this round (with its Gate quote) or by logging this as a minimum-content conformance defect.

**W02-3 — No SCORECARD claim table and no LOG entry for round 59 (A6, and "Landed changes").**
`grep -n '^## Round 59' SCORECARD.md` → no match; only `:3187 ### Planned (round 59)`.
`grep -n 'round-59\|round 59' LOG.md` → no match; last heading `LOG.md:2466 ## Round 58`.
Meanwhile six round-59 commits exist (`git log --oneline -8`: `4a541190`, `114fdf78`, `aca8d006`,
`2c7443ab`, `494c1657`, `5d957d24`), and the whole round-59 change set is 30 files / 3595 insertions /
1 deletion (`git diff --stat 8f7f58cd..HEAD`), of which the only non-wave, non-tool, non-test files
are `SCORECARD.md` (2 lines, one replaced) and `corpus/` (no change at all — empty diff). §4 "Landed
changes" requires every change tied to a LOG entry *and* the commit that carries it; §2.5 requires
the score-delta/evidence/counting-command/measured-commit row. Both are unsatisfied until the L1
writes them.

**W02-4 — Measured commits precede the tip, but the counted inputs are provably unchanged (A4).**
Measured `aca8d006` (C1) and `2c7443ab` (C2); tip is `4a541190`. No-change proof, exit 0 both:
`git diff --stat aca8d006..HEAD -- tools/round59-c1-counter.py tools/round59-battery-outcome-check.py tests/round59-battery-variants tests/round58-battery-variants tools/round56-env-leg-battery.py`
→ empty; `git diff --stat 2c7443ab..HEAD -- tools/round59-c2-counter.py SCORECARD.md` → empty.
`114fdf78` and `4a541190` touch only `controls/*.out|exit` and `w1/{spec,dispatch,swarm-registry}.json`.
The report may cite the measured commits **if** it states this no-change proof; otherwise the
"commit it was measured against" clause invites the objection that the tip was not measured.

**W02-5 — Discernment is constrained by an absent outside record (C2).**
No `corpus/lessons/round-58-verifier-spotcheck.md` exists (prompt §6 item 5's conditional read has
no target), and no outside S517/S518 admit/reject disposition exists in the lane. The assignment
and the freeze both forbid seat-consensus admission. The conforming verdict is
`discernment — unchanged` (or `unprovable`), explicitly attributing the absence; r58's
`unprovable-but-better` must not be re-scored upward on the strength of r59's 64 lane seats.

**W02-6 — Stale-lane can cite a launch but not a close (E2).**
`.ufo/watchdog.log:1784` is the only `kama round=59` line (launch, 2026-10-27T17:13:51-03:00,
pgid 3879171, `hyaku-inline attempt=1`); zero `complete` and zero `lane-dead-no-report` lines.
A report sentence claiming a closed round or a measured age must cite those two counts rather than
assert them.

**W02-7 — The watchdog's Sources heading is stricter than prose suggests (F11/D4).**
`shokunin-watchdog.sh:356` requires a heading matching
`^#{1,6}[[:space:]]+Sources[[:space:]]*&[[:space:]]*frontier` (case-insensitive, literal `&`).
`report_of` (`:186-207`) separately requires a SHONEN heading/bold marker and ≥`MIN_REPORT_BYTES`
(400, `:54`), and rejects a same-round file whose digest equals the baseline — the round-59 baseline
is `59 e3b0c442…b855` (empty-string digest), so only a genuinely non-empty report can land.

**W02-8 — Source-side §10 obligations have no pasteable artifacts yet (F8/F9/F10).**
Quarantine slice is present with 7 `payload-absent` rows and no lane verdict list;
`.ufo/waves/round-59/assimilation/` does not exist (`ls` exit 2), so the collision/renumber pastes
required *if* anything is adopted cannot exist; adoption is therefore closed and the report should
carry `Assimilation: none`. `considerthese/2026-10-26.md` is the newest operator file and nothing in
the lane records a selected proposal, so the "say which in the report" line is still open.

## Limits of this audit

- No counter, checker, battery, or wave seat was executed here; every claim-side fact is read from
  committed receipts (`controls/*.out|exit`) or `git show`/`git diff` output. The single executed
  command was the read-only `sources-census.sh census …` above (stdout only, exit 0); no `--out`.
- Claim truth is not graded: whether C1's 16/16 and C2's `mismatches=0` actually satisfy the frozen
  predicates is the canonical judge's call, and K02/K14/R-seat attacks are in flight.
- The mandated census invocation for `start.out` is inferred from output shape, not from a recorded
  argv (no argv log in `census/`).
- No install, upgrade, or PATH write. No pacman action (host pause respected). Scratch
  `/fast/scratch/hyaku/kama-r59/W02ReportAudit` created, `TMPDIR` set explicitly for the census run,
  and removed before yield.

## Touched surfaces

- Written: this file only (`.ufo/waves/round-59/w1/out/W02ReportAudit.md`).
- Read: lane docs/tools/controls/census, fleet `templates/`, `.ufo/prompts/`, `scripts/`, `.ufo/reports/`, `.ufo/state/`, `.ufo/watchdog.log`.
- Out of scope and untouched: `.ufo/reports/round-59/kama.md` (fleet root is read-only for this seat
  and the report is not drafted), `SCORECARD.md`, `LOG.md`, `SHONEN.md`, `corpus/`, `tools/`,
  sibling lanes, `/home/vgpnk/Projects/shokuknow`.

Report: .ufo/waves/round-59/w1/out/W02ReportAudit.md
