# ReviewContract — round 11 C1/C2 claim separability, axes, score derivability, census contract

Seat: ReviewContract (reviewer, author advisor — not a non-author verifier).
Steered round label: kama round 11, 2026-10-19 (heading keeps steered date).
verified-at: 2026-10-20T02:14:56Z — actual UTC review (`date -u`). Historic observations keep their original dates: round-10 source rows opened 2026-10-19 (`corpus/SOURCES.md`), round-10 knowledge entries verified 2026-10-19.
Scope: read-only review of repo files and read-only local greps/hashes. No sources opened, no network, no host config, no tests, builds, lint or formatters. No files modified except this report. Tools installed: none.

## Verdict

NOT ADMISSIBLE as currently framed. Four blockers are mechanical or authority conflicts the author wave cannot clear alone; one is structural (no non-author reviewer available to this wave). No synthetic pass is recorded.

## 1. Axes — named and assigned (blocker A1–A3)

Axis set in play:

| Source | kama axes |
|---|---|
| `shokunin.conf:52` (current roster) | `operability + calibration (local model serving and endpoint health)` |
| `MISSION.md:29` (cited as authority by SCORECARD round 10 and the round-11 spec) | `operability + freshness` |
| `SCORECARD.md` §Round 10 (scores) | operability 8, freshness 8, depth 7, calibration 7, adjacency 7, coverage 9 |

- **A1 — the freshness assignment rests on a line the mission file labels non-current.** `MISSION.md:16` reads "Historical example — the upstream fleet's initial nine-lane config, not the current roster (axes preserved):", and `MISSION.md:29` sits inside that block. `SCORECARD.md` round 10 cites `MISSION.md:29` as "Axis authority", and the round-11 spec states "MISSION assigns operability+freshness". `MISSION.md` §Axes also says "Axis assignments in `shokunin.conf` are initial; lanes may add/remove axes on evidence (falsifiable claim per move)." I found no SCORECARD row recording a change from `operability + calibration` to `operability + freshness` on evidence. The current authority is `shokunin.conf:52`, which does not list freshness.
- **A2 — coverage is off-assignment under both sources.** Neither `shokunin.conf:52` nor the historical block lists coverage. Round 10 already moved coverage 8→9 (SCORECARD erratum), and round-11 C2 claims coverage again. No assignment change for coverage is recorded.
- **A3 — the "lowest LIVE tie" rule is not derivable from AXES.** `AXES.md` requires a claim on "the lane's **lowest-scoring non-retired axis**". By the recorded scores, depth, calibration and adjacency (7) sit below freshness and operability (8). "Lowest LIVE" holds only if the owned set is {operability, freshness}, which contradicts the conf. Under the conf's {operability, calibration}, calibration (7) is the lowest and neither C1 nor C2 touches it. The round-10 SCORECARD §Planned had item (3) calibration; the round-11 spec drops it with no recorded reason.

Required before admission: a SCORECARD-recorded axis-assignment decision (operator/L0 ruling, or a conf edit with evidence) naming the owned set, and a rule for which axis is "lowest". Until then C1 (freshness) and C2 (coverage) are both off the current roster.

## 2. Claim separability (blocker S1–S3)

- **S1 — C1 moves the round-10 coverage counter without adding coverage.** The round-10 coverage score is derived from `grep -lE '^source: S[0-9]{3}' corpus/knowledge/*.md | wc -l` (SCORECARD erratum: "0 → 3"). I re-ran it read-only on 2026-10-20: result **3**, with 12 knowledge files. The 9 legacy files currently have zero column-zero `source:`/`verified-at:`/`recheck:` lines (counted 0 each). Legacy1's supplement instructions require column-zero `source:` lines whose source "must cite retained historical evidence" — any `source: S0xx` line moves the counter from 3 toward 12. C1 therefore contaminates the coverage denominator-numerator, and `SOURCES-CONTRACT-v1` rule 4 likewise counts entries "whose `source:` cites a `mined` row" toward expansion. Required: either legacy supplements may not start a line with `source: S` (use a distinct label for historical evidence), or the coverage counter is restricted to entries admitted in the round, with the exclusion written into the SCORECARD formula.
- **S2 — C2 cannot be separated from SourceCurator.** Contract rule 4 requires the C2 entry's `source:` to cite a `mined` row. `SourceCurator` flips S011/S012/S016 queued→mined. The census check E11 (`scripts/sources-census.sh`, documented in its header) fails when a `mined` row's `used-by` path is not on disk. So `SourceCurator` cannot validate until the Crosswalk file exists. This is a true ordering dependency: Crosswalk file → SourceCurator cells → `validate`. The spec states no ordering.
- **S3 — C2's "missing" ground is partly covered.** `runtime-health-surface-matrix.md:17` already states Ollama `/api/tags` = available models and `/api/ps` = running models, with the identity route in the same row. That row cites only S009 and S010. S010's `teaches` column in `SOURCES.md` covers the OpenAI-compatible `/v1/models` subset; S009 covers base URLs. Neither row's `teaches` covers `/api/tags` or `/api/ps` (those are S011/S012, both still `queued`). So the existing row is a citation mismatch under KQ6, and C2 is a fix to that mismatch plus the uncovered llama.cpp alias/id and readiness separation, not a wholly new ground. Round 11 must either (a) correct the row by appended supersession citing S011/S012 after they are mined, or (b) state the duplication in the claim. Row growth is not expansion (`AttackCoverage` remit).

## 3. Score derivability (blocker D1–D4)

- **D1 — C1 has no freshness measurement.** AXES defines freshness as "Drift detection — skill claims re-verified against live surfaces". C1's measured quantity is presence of three metadata lines (27 → 0). Presence is not re-verification; the supplements are designed to say "none — historical record". A numeric freshness move cannot be derived from it. Under AXES this is at most `unprovable-but-better`, which requires a named non-author reviewer (see §4, B1). Round-10's freshness move (50 stale anchors → 0) was a drift count; the round-11 spec has no equivalent.
- **D2 — "missing-fields" is gameable and the false-freshness check is unmechanised.** Measure's stated rule is presence of three column-zero lines, once each. A line `verified-at: 2026-10-19 — ...` passes. The spec's rule against `verified-at` "falsely saying live revalidated today" is explicitly "report wording considerations, no speculative parser", i.e. human judgment with no reviewer on record.
- **D3 — "today" is the steered date in the spec, the actual date in the census.** `scripts/sources-census.sh` defaults `TODAY` to `date -u +%F`. The round-11 supplement heading may keep "(2026-10-19)", but the `verified-at` value must state the actual review date (`2026-10-20`, UTC) and the original observation date separately, per the parent instruction. Measure must not hard-code 2026-10-19 as "today"; the check should read `date -u`.
- **D4 — denominator mismatch.** `SCORECARD.md` §Planned (round 11) says "the 18 pre-round-10 entries". `legacy-baseline.json` lists 9 files × 3 fields = 27, which I re-verified (all 9 SHA-256 and byte counts match current bytes). The planned count is stale or counts something other than files, and must be corrected by an appended SCORECARD erratum before any score is stated against it.

Score rule proposed for the author wave (not a pass): C1 is recorded as "provenance metadata, freshness unchanged" unless a drift counter is defined and measured; C2 is coverage only if the duplication in S3 is resolved and the entry is counted once.

## 4. Census contract (blocker K1–K3) and outside review (blocker B1)

- **K1 — the measure CLI does not exist.** `.ufo/waves/round-11/measure.py` is absent (checked 2026-10-20). Its specified checks (prefix SHA of first `bytes` against `legacy-baseline.json`, three column-zero fields, `verified-at` wording) are unimplemented. Feasibility note: the baseline stores whole-file SHA-256 and byte length at baseline time, so prefix-verification is `sha256(file[:bytes]) == sha256` — implementable, but the spec's phrase "SHA256 first original bytes" must be written exactly that way.
- **K2 — the existing census does not cover C1 or C2 provenance.** `SOURCES-CONTRACT-v1` (`.ufo/waves/kaika/SOURCES-CONTRACT-v1.md`, frozen, 81 lines) and `scripts/sources-census.sh` validate row shape, enums, duplicates, tiers and `used-by` existence only. Nothing mechanises `source:` lines in `knowledge/`. The baseline `sources-census-before.json` (`rows 30`, `tier.A 27`, `tier.C 3`, `status.mined 17`, `queued 8`, `rejected 5`, `missing 0`, exit 0) and `sources-validate-before.json` (`kama ok`, exit 0) are accurate records and I did not contest them.
- **K3 — status change is not evidenced by the census.** The census counts `mined` but cannot tell whether the reopen happened. The Gate (URL, access date, ≤25-word quote) in the round lesson is the only evidence. `opened` must stay the historical 2026-10-19 (contract rule 2: only status, recheck and used-by change in place), so the reopen date cannot be written into `opened`; it goes to the lesson with the actual UTC access date.
- **K4 — inherited-state attribution does not match the repo.** `.ufo/waves/round-11/inherited-state.json` says round-10 leftovers are "committed under round-11 log". `git status --short` (2026-10-20) still shows `?? .ufo/round-10/SEAT-PROTOCOL.md`, `?? .ufo/round-10/plan.json`, and `?? .ufo/waves/`. The claim is unmet at this moment; treat leftovers as untracked until committed.
- **QUALITY gap.** `corpus/QUALITY.md` has KQ1–KQ10 and no criterion for appended provenance metadata. `LEARNING.md` requires each criterion to cite a lesson. An admission criterion (e.g. "appended provenance must separate original observation date from review date and cannot raise a freshness score") must be appended before C1 is admitted.

- **B1 — no outside non-author review is obtainable from this wave.** `LEARNING.md`: a non-author "a fresh reviewer or the operator — spot-checks a sample… at least one admit and one reject… A subagent the lane dispatched is still the lane." `AXES.md`: an exploratory claim needs "a named non-author reviewer on record (… a dispatched subagent does not count)". The round-11 spec states "Parent-dispatched seats are author advisors, not outside non-author verifiers." Every reviewer in this wave (including this seat) is therefore author-side. Round 10 used fresh orchestrator-dispatched verifiers (`corpus/lessons/round-10-verifier-spotcheck.md`, "W3ReviewKama"; full reports at `.ufo/waves/kaika-w3/kama-review.md`, which I did not open). The round-11 wording now excludes that mechanism. Result: the round cannot record a non-author admit/reject spot-check, and no `unprovable-but-better` verdict is admissible. Only the operator or an outside reviewer can clear B1.

## 5. Blocker list for admission

| # | Blocker | Cleared by |
|---|---|---|
| A1 | Freshness assignment cites a historical-example line; conf says calibration | Recorded operator/L0 ruling or conf edit with evidence |
| A2 | Coverage off-assignment | Same ruling; else coverage claim withdrawn |
| A3 | "Lowest LIVE" not derivable from AXES; calibration dropped without record | SCORECARD rule naming owned set and lowest axis |
| S1 | C1 inflates round-10 coverage/expansion counter | Column-zero `source: S` rule or counter restriction, written into SCORECARD formula |
| S2 | C2 depends on SourceCurator and E11 on-disk path | Explicit ordering: Crosswalk file → SourceCurator → census validate |
| S3 | Existing matrix row cites S009/S010 for `/api/tags`/`/api/ps` | Appended supersession after S011/S012 mined; or claim states duplication |
| D1 | No freshness measurement for C1 | Re-scope C1 as provenance metadata, freshness unchanged |
| D2 | Verified-at wording check has no mechanism | Remove "falsely revalidated" check from the score, or assign to named non-author reviewer |
| D3 | Measure "today" must be `date -u`, not steered date | Specify in measure contract; verified-at states actual date 2026-10-20 |
| D4 | "18 entries" vs 9 files | Appended SCORECARD erratum |
| K1 | measure.py absent | Implement per contract; parent runs mutations |
| K2/K3 | No census for knowledge provenance; reopen evidence only in lesson | Lesson Gate with URL, UTC access date, ≤25-word quote |
| K4 | inherited-state claims commit that is not in git status | Commit or relabel leftovers as untracked |
| QUALITY | No criterion for appended provenance | Appended KQ row citing lesson |
| B1 | No non-author reviewer in wave | Operator or outside reviewer; without it, no admit |

Admission remains **blocked**. I did not assign any score; no axis is claimed as moved by this seat.

## 6. Negative controls (described only, not run)

- Delete one trio line from a legacy file → expect missing_fields > 0 and exit 1.
- Change one byte within the first `bytes` of a legacy file → expect a prefix violation and exit 1.
- Append `source: S011 …` at column zero to a legacy file → expect the coverage counter (S1) to change; the admission must either exclude it or fail.

## 7. Limits

- I did not open any public source; S011/S012/S016 status and quotes are as recorded in `SOURCES.md` and the round-10 lesson.
- I did not verify `.ufo/waves/kaika-w3/kama-review.md` or the round-10 verifier reports.
- `.ufo/waves/round-11/` gained files during this review (`baseline-revision.json`, `record-result.json`, `routing-observed.json`, `frozen/`). I did not read them; their contents are unverified here.
- Counts above are single-run, read-only, at 2026-10-20T02:14Z.
