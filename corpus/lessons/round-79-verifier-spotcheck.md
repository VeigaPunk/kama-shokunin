author: hyaku closure (non-author integrator, @m_zfl)

# kama round 79 — verifier spot-check (non-author closure)

Lane: kama, round 79 (attempt 1). Base `ee53f1a25eab93a8ab55bbb877e49e2e731df535`; lane tip
after the round `a9b4543f14625d0f37daa42ef664ee6f6ea975ea` (branch `master`, remote-verified).
Report: `.ufo/reports/round-79/kama.md` (fleet `618ee25ca104d0eb7dc1366bd1b613e136449270`,
descendant of fleet `origin/master` `afbb6796b699aa2502604a9c392654ec815f1f82`). I did not
author this round; I verified it. Review date 2026-11-04.

Method note: PROTOCOL §Gate standard forbids executing a sibling lane's gate, so the C1/C3
counters and the pre-report gate are **evidence-verified** from their committed receipts (frozen
line, self-test tally, revision measured); their **grounds** are **re-measured** by me with
plain counts over committed bytes (`git show`, `grep`, `wc`, `sha256sum`, the fleet census). The
one admit and one reject in the lesson's `## Gate` were re-opened live with `curl` (status,
bytes, digest, line, quote).

## 1. Conformance (step 1)

| Check | Result |
|---|---|
| Report committed in the fleet repo by the lane identity | PASS — `git log --format='%an <%ae> %H' -1 -- .ufo/reports/round-79/kama.md` → `kama-shokunin <kama@shokunin.local> 618ee25ca104d0eb7dc1366bd1b613e136449270`; `git merge-base --is-ancestor 618ee25 origin/master` exit 0 |
| `## SHONEN` heading, one line per box | PASS — one `## SHONEN` heading, four `[~]` lines against the four boxes, each with a pointer; no `[x]` written by the lane |
| Every cited lane commit exists and is an ancestor of the branch | PASS — all 17 hashes in the Landed-changes table (`3310370 f7442de d6408a6 5ac1a8d 9100605 b574397 f4a35f6 1cda045 1f82cc3 078253d 5785cdf c6ec06f 6fb6885 b756571 4af44f7 a9b4543`, plus sealed `7a3cd982`, base `ee53f1a`) resolve and `git merge-base --is-ancestor <h> master` holds; `fa65ce2c` and `381b53dc` (named in the pre-correction receipt) resolve, and `fa65ce2c` is an ancestor of the base |
| Lane repo clean and pushed | PASS — `scripts/hyaku/jj-lane.sh state kama-shokunin` → `branch=master local=a9b4543f… remote=a9b4543f… ahead=0 behind=0 head=detached tracked=0 untracked=0`; `git status --porcelain` → empty; `git ls-remote origin refs/heads/master` → `a9b4543f…` |
| Prompt carries the template contract | PASS — `.ufo/prompts/kama-round-79.md` (704 lines) carries the round-level items (§1 MISSION/AXES binding, §2 claims, §3 L2 floor `≥8` l.82, commit-then-push l.133, push scope l.135, L0 l.137) and all five child-lane items (report path l.101, commit-hash citation l.106–107, `SHONEN` heading l.118, report lands last l.513, write scope l.445); §6 hyaku addendum present. No model alias is pinned: the prompt routes through `task.agentModelOverrides` (l.395), and `MISSION.md` §L2 carries role-class buckets only (no alias list), so no route map contradicts the current mission bucket |
| Wave shape | PASS — `.ufo/waves/round-79/w1-spec.json` has 14 seats (4 executor, 3 scribe, 2 scout, 1 connector, 1 reviewer, 2 critic, 1 mutation-tester; attack 4/14 = 29 %) under the 8–16 band, one v1 wave, `w1.ready.dispatched` present; `w1-results.json` has 14 results, 11 non-empty, 3 empty (`EX02GateArm`, `EX03ProbeClass`, `EX04CensusCounter`) exactly as reported |
| Report is a real report, not a marker | PASS — Work performed, Landed changes tied to `LOG.md:3213`, Before → after table, Sources & frontier with the census command, three trend verdicts, checkable hash citations; misroot sweep matches the fleet `git status` (only orchestrator `.scratch/*`, `.ufo/l0-questions.md` (mado's appended line), sibling reports, `after`, `agent:/`) |

Conformance defects (status-neutral; they do not change the status):

1. **SCORECARD overstates C2.** `SCORECARD.md:6` (current-authority banner) says "C2 operability
   verified"; the §Round 79 claim table (`SCORECARD.md:4587`) ends `**verified**`; the live
   operability row (`SCORECARD.md:14`) cites "the scored run `PRE_REPORT round=79 arms=10
   failed=0 uncommitted=0`". The committed receipt prints the opposite:
   `.ufo/waves/round-79/measured/after/c2-gate.out` (`rev: b756571e…`) →
   `PRE_REPORT round=79 arms=10 failed=1 uncommitted=0`, `EXIT=1`. The same table's before cell
   also prints `PRE_REPORT_SELFTEST pass=26` where the cited
   `.ufo/waves/round-79/measured/before/c2-gate-arms.out` prints `pass=22`. The §Gate subsection
   and the report's before→after row are honest (`NOT VERIFIED (honest stop)`); the overstatement
   is confined to the banner, the claim table and the axes row.
2. **LOG summary overstates the same fact.** `LOG.md:3217` says "Three claims, three distinct
   axes, all verified on their receipts"; C2 is not verified. `LOG.md` is append-only, so the
   correction is a named appended entry in the next round, never a rewrite.
3. **C1 counter docstring lists the wrong facts.** `tools/round79-selfrecord-round78.py:23-25`
   describes F1 as the record's "Scores hold: …" sentence and F2 as "the three new capabilities";
   the code grades F1 lowest-axis (`f1`, l.281) and F2 population (`f2`, l.292), matching the
   plan's frozen table. Not disclosed among the freeze divergences.
4. **Rejected candidate has no SOURCES row.** The `docs/preset.md` rejection (correct decision,
   see §3) is recorded only in the lesson's `## Gate`; the frontier contract says "Rejections
   stay as rows with reason and flip", and the census confirms it (`status.rejected` 21 → 21).
5. **Validate warning inventory.** The report says the validate run is "exit 0 (W04 duplicate-URL
   warnings only)". The run also prints a `W01 S481 tierC mined used-by=…` line (pre-existing: the
   SOURCES diff adds only S553 and touches no existing row). Wording defect only.
6. **C3 control input is a scratch path.** `measured/control/c3-base-probe.out` runs
   `--probe /fast/scratch/hyaku/kama-r79/base-probe.sh`; the file exists on this host (49801
   bytes, 2026-11-04 06:49) but is not resolvable at closure from committed bytes. The reproducible
   form is `git show ee53f1a25…:tools/kama-probe.sh` written to a temp path.
7. **S553 anchor names a region label.** The row's anchor says "§Router mode"; no heading carries
   that name (the lesson's appended correction says so and names `### GET /models: List available
   models`, heading line 2197, note 1, line 2227).
8. **Gate arm numbering in prose.** The gate docstring says "Round 79 adds arm 11" while
   `SKILL.md:309` and the verdict line say arm 10 (partly disclosed as freeze divergence 2: the
   prose keeps historical numbering).

## 2. Claims (step 2)

### C1 — calibration: the round-78 self-record's six declared facts re-derive or are answered by dated value-bound corrections

- **Grounds re-measured by me at the sealed revision `7a3cd982…`** (plain `git show`/`grep`/`wc`
  counts): F1 — the sealed `## Axes` table reads operability 8, freshness 8, depth 7, coverage 9,
  calibration 7, adjacency 7, and the assigned pair is operability + calibration, so the lowest
  is `calibration:7`; the sealed §Round 78 section carries the exact sentence "the lowest
  assigned axis (calibration 7) carries C1". F2 —
  `git show 7a3cd982:corpus/SOURCES.md | grep -c '^| S[0-9]'` → `292`; knowledge blobs 53 minus
  the two filtered (`engine-sides`, `processes`) → `51`; `SKILL.md` 1736 lines sha256
  `a50f6f7445402de8f09d52d9fa1fb2d3017769ec4ea372ff4bd3baa036df672d`; `PROVINCE.md` 331 lines
  sha256 `6b8c604f045d7275aa77e8788ba318e7cf51dfbc2ae29ffed4564cb34edcd3c9`. F3 — sealed
  `w1-spec.json` 12 items `{executor 3, scribe 3, scout 1, connector 1, reviewer 1, critic 2,
  mutation-tester 1}`, attack 4/12. F4 — sealed `w1-results.json` returned 3
  (`EX01C1Selfrecord`, `SC02Lesson`, `SCT01Recon`), empty 9. F5 — `SCORECARD.md:4538` at the
  sealed revision reads "The tip accounting is the round-77 counter, which is green at
  `rev=22cce544`"; `22cce544b23670984fa9e42bea673d603881aae7` is an ancestor of `7a3cd982…`, not
  the sealed tip. F6 — `git grep -l 'mismatches=1' 7a3cd982… -- .ufo/waves/round-78/` returns
  0 blobs while the record's freeze-divergence item 4 claims both runs "are both in the lesson".
  All six declared/observed relations match the counter's frozen table (F1–F4 fresh, F5–F6 stale).
- **Corrections re-derived:** `corpus/lessons/round-79.md` §Corrections carries exactly two
  backticked blocks, both `at=7a3cd982…`. F5 `new=tip-accounting=rev:22cce544/is-tip:false`
  re-derives (the named rev is an ancestor of the tip's master); F6
  `new=c1-pre-correction-run=committed:.ufo/waves/round-79/measured/v2/c1-pre-correction.out`
  re-derives (`git show a9b4543:.ufo/waves/round-79/measured/v2/c1-pre-correction.out` carries
  `SELFRECORD_R77 claims=6 mismatches=1 corrected=4 unbacked=0`, `EXIT=1`).
- **Evidence-verified receipts:** `measured/after/c1-green.out` (`# rev: 5ac1a8d…`) prints
  `SELFRECORD_R78 claims=6 mismatches=0 corrected=2 unbacked=0 | sealed=7a3cd982… tip=5ac1a8d…`,
  `EXIT=0`, with F1–F4 fresh and F5/F6 `stale corrected=yes`; `measured/after/c1-selftest.out`
  nine named arms, `SELFRECORD_R78_SELFTEST pass=9 fail=0`; the pre-freeze enumeration
  `measured/before/c1-enum.out` prints `stale=2 corrected=0`, `EXIT=1`; the no-correction control
  `measured/before/c1-score-nocorrections.out` prints `mismatches=2 corrected=0`, `EXIT=1`;
  the self-test at the tip `measured/v3/c1-selftest.out` prints `pass=8 fail=0` for the round-77
  counter. The module's `PREDICATE` is the plan blockquote **verbatim** (476 normalised
  characters, equal), and `git diff --numstat 5ac1a8d a9b4543 -- tools/` is empty, so the
  instruments are unchanged after the measured revision; the §Corrections block changed by zero
  `corrected F` lines between that revision and the tip.
- **Verdict: verified.** Axis calibration — **improved** (score holds 7; the instrument is new
  and the two stale facts are repaired value-bound).

### C2 — operability: the pre-report gate composes the three round-78 instruments as its own arm

- **Evidence-verified:** `measured/after/c2-selftest.out` (`# rev: 5ac1a8d…`) has 26 `PASS` lines
  and prints `PRE_REPORT_SELFTEST pass=26 fail=0`, `EXIT=0`; the four new cases are
  `round78-instruments-red`, `-missing`, `-green`, `-malformed`; the arm itself prints
  `PRE_REPORT_ARM round78-instruments exit=0 ok … SELFRECORD_R77_SELFTEST pass=8 fail=0 |
  APPEND_REGISTERS_SELFTEST pass=7 fail=0 | LIVE_RECONCILE_SELFTEST pass=4 fail=0`; the before
  state is `BASE_ARM_ORDER 9 …`, `PRE_REPORT_SELFTEST pass=22 fail=0`. `SKILL.md:309` is
  re-anchored to ten arms, `pass=26`, `round78-instruments`.
- **The frozen target's second clause fails.** `measured/after/c2-gate.out`
  (`# rev: b756571e…`) prints `PRE_REPORT round=79 arms=10 failed=1 uncommitted=0`, `EXIT=1`:
  arm 8 `round75-instruments` is red with
  `APPEND_ACCEPTED events=58 accepted=53 unaccepted=5 bad_rows=0 bad_declarations=0`, and the
  finding names `9100605d…` `corpus/lessons/round-79.md`. Arm 10 is green. The count of five
  unaccepted events is this round's own in-place record edits, so the predicate's `failed=0`
  clause is not met at the tip.
- **Verdict: not verified** (honest stop; the lane's report and SCORECARD §Gate say so, and the
  two overstatements above are routed). Axis operability — **unchanged**: score holds 8, the
  instrument landed, no capability regressed.

### C3 — coverage: the probe reports an unregistered serving listener as its own census class

- **Grounds re-measured in the committed bytes:** `tools/kama-probe.sh` at the tip (sha256
  `0943fb461d0226e29d1b8a3b6af67740d4fe6863505ee6ed771719a30fdc3d19`, 1188 lines) has
  `classify_registration` (`yes` when a model-API listener's port is a registry row's declared
  port, `no` when it answers a model API ungoverned, `-` otherwise), the `registered` table
  column (l.768) and the JSON row key (l.787), and the summary keys `governed`/`unregistered`/
  `registry` (l.799/794); `tools/round79-unregistered-census.py` writes two scratch registries
  (declaring the fixture port, then not), runs the probe's `listeners --json` with `--port` on
  both, and grades the same listener both ways. The probe did not change after the receipt
  revision (`git diff --numstat 5ac1a8d a9b4543 -- tools/` empty).
- **Evidence-verified:** `measured/after/c3-census.out` (`# rev: 5ac1a8d…`) prints
  `UNREGISTERED_CENSUS port=46671 unregistered=1 governed=1 class_missing=0 rows=1`, `EXIT=0`
  (plus the non-gating live leg `UNREGISTERED_CENSUS_LIVE model_endpoints=8 governed=0
  unregistered=8`); `measured/after/c3-selftest.out` `pass=4 fail=0` with `both-legs`,
  `class-missing`, `probe-error`, `absent-probe`; the control
  `measured/control/c3-base-probe.out` prints `unregistered=0 governed=0 class_missing=1`,
  `EXIT=1`. The base probe input is a scratch copy (defect 6), but the counter's `--probe` path
  is the reproducible knob.
- **Sourced claim:** the entry `corpus/knowledge/unregistered-listener-census.md` opens
  `source: S553`, `verified-at: 2026-11-04` and a recheck line that is the counter's own target.
- **Verdict: verified.** Axis coverage — **improved** (score holds 9; a new class and its census
  surface, one admitted entry on ground the coverage map did not hold).

### Axis harm check

`git diff ee53f1a a9b4543 -- SCORECARD.md`: the axis vector holds 8/8/7/9/7/7; no score dropped,
no axis retired, no admitted entry found false and left unmarked; the two new `## ` decisions
(KQ130/KQ131) cite their lessons; `PROVINCE.md` records mado's `CHECK96 unregistered=` vocabulary
collision and kengaku's shared listener as reported, not absorbed. **No axis harmed.** The one
false pointer class (C2 `failed=0` in SCORECARD/LOG) is a conformance defect routed below; it
moves no score.

## 3. Discernment spot-check (step 3, non-author)

| Item | Decision | Re-opened source | Agree/disagree | Reason |
|---|---|---|---|---|
| S553 llama.cpp router `GET /models` | admit | live `https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/tools/server/README.md` → HTTP 200, 135608 bytes, sha256 `8fd5abde2fb52de3b30f30a170631d4c0d92febecc8da44d0541e48b132b35c6` | **agree** | the 16-word quote is verbatim at line 2227 under note 1's `?reload=1` bullet ("If a model is not running, it will be added or updated according to the source"); the bytes and digest match the row; the scope ("a model list is an inventory, not a loaded-model or readiness claim") is exactly what the note supports; tier A docs fits; `used-by` resolves |
| llama.cpp INI presets (`docs/preset.md`) | reject | live `https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/docs/preset.md` → HTTP 200, 4090 bytes, sha256 `3e6643541e12ff3dfee2a23c23a57357403bf4500beced780f010eaebbbdfe13` | **agree with the decision; defect on the record** | the document is a configuration-format reference; the round's class reads the model list and the probe parses no preset, so no claim reads it; the flip (a round that grades preset-inherited parameters on the fixture) is concrete — but the rejection was not filed as a `REJECTED` row (defect 4) |
| S553 `corpus/SOURCES.md` row | new row | `corpus/SOURCES.md:308` + live line 2227 | **agree with a minor anchor defect** | `teaches` and the quote are within the contract, `status=mined`, `opened=2026-11-04`, `recheck=on-release`, `used-by` resolves; the anchor's "§Router mode" is a region label, not a heading (defect 7) |

Census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root
/home/vgpnk/Projects/shokunin kama` → exit 0; only pre-existing warnings (W04 duplicate URLs and
the W01 S481 tier-C-mined row), no malformed row, no duplicate id, no tier inflation; S553 is
valid and its URL is not a duplicate.

## 4. Axis and trend verdicts

| Axis | Verdict | Evidence |
|---|---|---|
| calibration | **improved** | C1 verified: six facts re-derived by me at `7a3cd982`; two value-bound corrections re-derive; receipts `c1-green`, `c1-selftest` 9/9, control red; score holds 7 |
| operability | **unchanged** | C2's selftest target met (`pass=26 fail=0`, arm 10 green) but the scored target is red (`failed=1`, arm 8, `unaccepted=5`); score holds 8, no regression |
| coverage | **improved** | C3 verified: class bytes in the probe, two-registry legs, census exit 0, control exit 1; one admitted entry, one coverage row; score holds 9 |
| depth | **unchanged** | no claim; `SKILL.md` 1736 lines sha256 `0a391ae2…` (registry-row repair only) |
| freshness | **unchanged** | no claim; S553 is the pinned-build docs row, not an engine-pin move (`engine-pins.tsv` untouched) |
| adjacency | **unchanged** | no claim; mado's `unregistered=` vocabulary and kengaku's shared listener reported, not absorbed; `registry/endpoint-consumers.tsv` untouched |

| Trend | Verdict | Evidence |
|---|---|---|
| expansion | **improved** | My census, same command at both revisions (`scripts/sources-census.sh census --file <blob>`, exit 0): base `3310370` rows 292 (A 277 / B 11 / C 4; mined 263, queued 8, rejected 21) → after `5ac1a8d` 293 (A 278 / B 11 / C 4; mined 264, queued 8, rejected 21); one admitted entry (filtered knowledge 51 → 52, `unregistered-listener-census.md`) on coverage-map ground the map did not hold, its `source:` citing mined S553; coverage row `corpus/README.md:1741`; three capability rows running (`selfrecord-round78`, `gate-arm-composition`, `unregistered-census`). Bound: one entry, one row, no package assimilation |
| quality | **improved, bound** | two stale self-descriptions (F5/F6) repaired and re-derived at the tip; three mistakes mined into KQ130/KQ131 with lesson citations; three controls committed red on the base; the gate now executes the round's own instruments. Bound/regression: the round's SCORECARD banner, claim table and axes row and the LOG summary assert C2 verified / `failed=0` while the receipt prints `failed=1` (defects 1–2, routed) |
| discernment | **improved** | this spot-check agrees with the sampled admit (S553) and reject (INI presets); the lane's own source seat caught the 14 → 16 word miscount and the region-label anchor, and the lesson carries the appended correction rather than a rewrite; two criteria cite their lessons. Bound: the reject has no SOURCES row (defect 4) |

## 5. Routed defects the lane must fix next round

1. **R79V1 — SCORECARD C2 overstatement.** Correct the banner, the §Round 79 claim table and the
   operability row: `measured/after/c2-gate.out` prints `failed=1` at `b756571`, and the before
   tally is `pass=22`, not `pass=26`. Name the claim `not verified (honest stop)` as the report
   does; keep the §Gate text.
2. **R79V2 — LOG correction entry.** Append a named correction for `LOG.md:3217` ("all verified")
   against the C2 honest stop; append-only, never a rewrite.
3. **R79V3 — C1 counter docstring.** Fix the `Facts` list in
   `tools/round79-selfrecord-round78.py:23-25` (F1 lowest-axis, F2 population) to match the code
   and the frozen plan; it is reader-facing gate documentation.
4. **R79V4 — rejected-source row.** File the `docs/preset.md` rejection as a `REJECTED` SOURCES
   row with its reason and flip, or record in the plan why a rejection need not be rowed.
5. **R79V5 — C3 control reproducibility.** Re-run or re-document the base-probe control from
   `git show ee53f1a25…:tools/kama-probe.sh` so the control input resolves at closure.
6. **R79V6 — S553 anchor.** Supersede the row's anchor to name `### GET /models: List available
   models` note 1, line 2227 (region label replaced), per the lesson's own correction.
7. **R79V7 — warning inventory and arm prose.** Say the validate run also prints the pre-existing
   W01 S481 line; align the gate docstring's "arm 11" prose with `SKILL.md`'s arm 10.

## 6. Verdict

Status `ok` (real report, real committed work, every cited hash landed and pushed). **Not
admitted**: C1 and C3 verify by re-measurement, C2 is an honest miss on its frozen `failed=0`
clause, and no axis is harmed. Verdict `rejected-honest-stop`.
