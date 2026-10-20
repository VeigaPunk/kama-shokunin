# FrontierScribe — round 11 frontier fragment (read-only)

Round label: kama round 11 (steered date 2026-10-19).
verified-at: 2026-10-20T02:14:33Z (actual UTC review date, `date -u`). Round-10 observations cited below are the dated 2026-10-19 records and are quoted unchanged; no new access is claimed for them. No endpoint, service, host config, or build/test was touched.
Tools installed or updated: none.

## Axes

1. Census integrity of the `sources-*-before.json` baseline (MISSION axes: operability, freshness; C2 coverage).
2. Status-vocabulary consistency of `corpus/SOURCES.md` for S001/S010/S011/S012/S016.
3. Falsifiability of the round-10 stale-authority criterion (KQ7) and its lesson row.

## 1. Census baseline (`.ufo/waves/round-11/sources-census-before.json`, `sources-validate-before.json`)

- Census `kama` line: rows 30, tier.A 27, tier.C 3, tier.B 0, status.mined 17, status.queued 8, status.rejected 5. FLEET lines equal the kama lines; missing 0; invalid 0. Validate: `kama ok .../corpus/SOURCES.md`, exit 0.
- Checked by reading the registry (not by rerunning the census): tier C = S027, S028, S029; tier A = S001–S026 plus S030 (27). Queued = S011, S012, S016, S021, S022, S023, S025, S029 (8). Rejected = S024, S026, S027, S028, S030 (5). Mined = the other 17. Totals reconcile.
- Limit: the census script `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` sits outside the lane and was not opened. The baseline is consistent with the registry; it does not prove the script's logic.

## 2. Old statuses (`corpus/SOURCES.md`, rows at lines 13, 22, 23, 24, 28)

| id | status now | used-by now | Note |
|---|---|---|---|
| S001 | mined | runtime-health-surface-matrix.md, serving-metrics-crosswalk.md | Add crosswalk path per SourceCurator target |
| S010 | mined | runtime-health-surface-matrix.md | Add crosswalk path per SourceCurator target |
| S011 | queued | — | `GET /api/tags`; "availability is distinct from running state" |
| S012 | queued | — | `GET /api/ps`; "Separates running models from the available-model list" |
| S016 | queued | — | OpenAI list; "does not establish local-server health or loaded weights" |

Status-vocabulary defects (found by reading; not yet acted on):

- SOURCES.md:6 says "Every row was opened in round 10", and the Gate (round-10.md:56) carries quotes for S011, S012, S016. Yet `queued` means "admitted, not yet used by a knowledge entry", not "opened". The vocabulary has no value that means "opened, unused". Proposed SourceCurator change (queued → mined for S011/S012/S016) is consistent with the census; the vocabulary gap remains.
- SOURCES.md:55 (search log, community sweep) says "included 3 (S027–S029)". Registry statuses are S027 rejected, S028 rejected, S029 queued. The search-log wording and the registry disagree; the log line is the one that should be corrected by an appended note, not rewritten.
- KQ6 (QUALITY.md:28) admits claims that cite "an opened SOURCES.md row". Queued rows therefore support the C2 crosswalk under KQ6, but the crosswalk should still state their status honestly.

## 3. Lesson Gate and Mistakes vocabulary (shape only; no lesson authored)

- Gate shape, round-10 (`corpus/lessons/round-10.md:54-90`): heading `## Gate`, one sentence stating the opening date, then a table `| id | URL | accessed | quote | location |`. Quotes verbatim, ≤25 words. Revision pins are a trailing paragraph. The round-11 `accessed` value for new opens must be the actual `date -u` date (2026-10-20 UTC), not 2026-10-19.
- Mistakes shape, round-10 (`round-10.md:7`): `| # | class | mistake | evidence pointer | captured-by criterion or none | fix |`. Next free number is 26 (17 is absent from the table; 18–25 exist).
- Class vocabulary: codes `Cnn/X` (e.g. `C01/C`, `C10/S`). No definition of the `C01…C13` or the `I/M/C/S/P` suffix letters exists in the repo (grep across corpus/*.md, SKILL.md and the lessons found only round-10 uses). `C10`–`C13` also appear as listener-census identifiers in `corpus/knowledge/listener-census.md:53-59, 229-245`, a different namespace. The class column is therefore ungrounded; any new row must either reuse the code by example or flag it [INFERENCE].
- Pointer defect: round-10 Mistake 18 (round-10.md:25) cites `MISSION.md:29`. MISSION.md is at `/home/vgpnk/Projects/shokunin/MISSION.md`, outside the kama lane root; the relative pointer does not resolve from the lane.

## 4. Candidate earlier mistake: the round-10 stale-authority count (Mistake 14 / KQ7)

Mistake 14 (round-10.md:22): "46 stale `current` lines survived round-1 review; 15 named lines still read as current at round 10". Its captured-by column says `none`, its fix says "target 15 to 0".

What round 10 later established (the chain):

1. round-10.md:37 publishes `stale_named_lines` (grep count) as the pasteable count.
2. round-10.md:116-119 publishes the ledger loop "uncorrected" count: 50 before, 0 after.
3. round-10.md:142 retires the `stale_named_lines` count: "It measured 15 at base `35e9175` and measures 29 at `1e41928`: its substring greps also match this round's correction lines … so it cannot distinguish a stale line from its correction." Its fix column is withdrawn.
4. round-10.md:143 corrects the meaning of the 0: `"Uncorrected 0" means every ledger row has an appended dated correction; it does not mean every row was re-anchored.`
5. round-10.md:151 reports the validator result: `rows=50 resolved=48 terminal=2 unresolved=0`; A17 and A51 are terminal, not re-anchored.

Current state (fresh read-only check, 2026-10-20T02:14Z UTC onward): the same grep chain in round-10.md:37 returns 29 on the working tree (matches the errata). The ledger `.ufo/round-10/audit/stale-anchors.tsv` has 50 data rows. Corpus files other than `lessons/round-10.md` are unchanged (git status shows only `.ufo/` untracked).

The live authority still cites the withdrawn criterion:

- `corpus/QUALITY.md:29` (KQ7): "A correction round publishes a stale-anchor ledger and a pasteable count that reaches 0." Motivating lesson: `lessons/round-10.md` Mistake 14. KQ7 does not name which count, and the only pasteable count in the lesson was retired at line 142.
- `corpus/lessons/round-10.md:22` still reads "Run the count below each correction round; … target 15 to 0" with captured-by `none`.
- `corpus/README.md:94` describes the round-10 lesson as "stale-anchor corrections, closed plan claim" without the errata.

So the admitted bar (KQ7) passes a state the round's own errata says is not fully re-anchored (2 terminal rows), and the count it names was withdrawn.

Classification (proposal): `C01/C` (stale-anchor attribution; same code as rows 5, 14) — [INFERENCE] because the code's meaning is not defined in the repo.

### Captured-by criterion (proposal; parent owns QUALITY.md)

Do not edit KQ7 bytes. Append a supersession row (e.g. KQ11) that:

- admits a correction round only when every ledger row has (a) an appended dated correction and (b) a `new` pointer that resolves in bounds with content correspondence checked by a sampled reviewer, and reports `terminal` rows separately;
- rejects any count whose pattern matches correction lines (quotes of old pointers) rather than the stale line itself;
- rejects citation of a withdrawn count as a criterion.

Named: `corpus/QUALITY.md` KQ7 (existing, unchanged) and a proposed appended KQ11 (new row). Round-10 Mistake 14 row remains byte-unchanged; the round-11 lesson records the mapping (append-only).

### Fail-before experiment (proposal; not run)

Goal: show the criterion as published (KQ7 "uncorrected 0") passes a state that the proposed criterion fails.

1. Use the round-10 ledger as published (50 rows; errata state: resolved=48, terminal=2). Compute:
   - published check: uncorrected count (round-10.md:116-119 loop). Expected 0 (the errata says so). This is the "before" pass that KQ7 accepts.
   - proposed check: rows with `new` terminal or unresolved, plus uncorrected. Expected 2 (A17, A51). A nonzero result means the published criterion would have admitted an incomplete re-anchor; the fail-before reproduces the round-10 defect.
2. Negative control (validator, per round-10 errata): in a temp copy of the ledger, rewrite one `new` pointer to `SKILL.md:9999`. The bounds check must report `unresolved=1`. A second row using `nope.md:1` → `unresolved=2`. Any zero here means the validator cannot discriminate and the candidate is rejected.
3. Stale-count discriminator: run the retired grep chain (round-10.md:37) on a temp copy in which only the correction lines are removed, and on the current tree. The count must differ by exactly the correction lines; if it does not, the proposal to reuse any grep count fails.

Run order when the round-11 lesson is authored: step 1 and step 2 on temp copies under `/dev/shm`; step 3 optional. None of these need a service, endpoint, or host config.

## 5. Alternate (secondary) candidate, already corrected

`corpus/README.md:47` reads "6–17 (in progress; loop 1 final)" for the free-tier entry; round-10 Mistakes 19 and 24 cite it. It was corrected by an appended entry at README:82 (A50, anchor `free-tier-provider-limits.md:26-57`). Captured-by: KQ3 (QUALITY.md:11). Fail-before: grep `6–17` against `free-tier-provider-limits.md` before and after the append; the "before" count must show a range the entry does not state (rounds 6–9). Use this as the fallback if Mistake 14 is judged too process-heavy for the lesson.

## Limits and defects

- Census script not opened; its logic is unverified. Baseline counts reconcile with the registry by reading, not by rerun.
- Quotes in this report are from files in the lane; no public vendor source was reopened (not needed for this slice).
- New verification date: 2026-10-20T02:14:33Z. Historical rows keep their 2026-10-19 access dates. Any new SourceCurator reopen must record its own actual `date -u` value, not 2026-10-19.
- Lesson not authored (per target).

## Handoff for parent

- Confirm `queued` vocabulary before SourceCurator edits S011/S012/S016 (add an "opened, unused" value or document that queued means that).
- Decide KQ7 supersession row (KQ11) vs keep KQ7 with an errata note; the round-10 table row 14 stays unchanged.
- Correct or annotate SOURCES.md:55 "included 3 (S027–S029)" with an appended note.
- Define or cite the class codes (`C01…C13`, I/M/C/S/P) before adding Mistake 26; resolve the listener-census collision.
