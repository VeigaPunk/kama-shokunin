# KamaR28 ResSelfAssessment — residual self-assessment calibration check (round 28)

- Reviewer: `KamaR28.ResSelfAssessment` (leaf seat, read-only; no tools installed; no
  git/jj writes; no lane counter or llama-server started).
- Scope: the lane's own round-28 self-assessment at landed tip `9ce5bd37` — `SCORECARD.md`
  `## Round 28` (lines 1404–1441), `LOG.md` round-28 entry (lines 1790–1819),
  `corpus/README.md` `## Frontier disposition — round 28` (line 423+), `PROVINCE.md`
  round-28 note (lines 109–114), `SHONEN.md`, checked against the repo at `9ce5bd37`
  and the round-28 receipts under `.ufo/waves/round-28/`.
- Ground truth used: `final/c1-e49b4cf7.out`, `final/c1-A0-e49b4cf7.out`,
  `final/c1-9ce5bd37.out`, `final/c1-A0-9ce5bd37.out`, `final/quote-check.out`,
  `final/r27-8057282c-stat.out`, `final/gate-registry-final.out`, `final/census-final.out`,
  `final/sources-append-only-final.out`, `before/c1-base.out`, `preregistration.json`,
  `controls/HOLDS.md`, evidential control receipt JSONs, `controls-A1/` receipts,
  `w1/spec.json`, `w2/spec.json`, `w1/spawn-result.txt`, `w1/dispatched-at.txt`,
  `w2/dispatched-at.txt`, `registry/request-field-outcomes-r28.json`, `corpus/SOURCES.md`,
  `w1/out/DataG01..17`, `w1/out/ExecEchoRecheck/`, `w1/out/ExecGateRegistryCheck/`,
  `w1/out/ScoutProvince/grep-hits.txt`, `w2/advice/RowReview01..17`,
  `w2/advice/CriticA1Legitimacy.md`, commit objects `d8bf1804`/`5ebe7b1b`/`75b78bb4`/
  `fb10d9da`/`e49b4cf7`/`9ce5bd37`, round-16/17 live receipts, `tests/llamacpp-live/controls.py`,
  `tools/echo-recheck.py`, `tools/gate-registry-check.py`, `corpus/QUALITY.md`
  (round-28 qualification), round-17 falsify advice (P3).

## Verdict

**3 mismatches in 46 checkable statements.** All five documents' claims (commit
hashes, counts, paths, scores, seat names, times, receipt contents) hold except:
(1) `LOG.md` says the pinned snapshot was re-fetched by 13 data seats; the wave-1
receipts record 14 (DataG10 also fetched). (2) `LOG.md` attributes the 34 landed
rows to 17 data seats; the registry attributes them to 13 (DataG01–09, G11,
G13–15). (3) `SHONEN.md:8` "8 bad fake-server shapes rejected, frozen pair
accepted 6" is a round-17 P3-routed imprecision (7 bad server shapes + 1
harness-fault control; accepted-bad 6 = 5 accepted-with-receipt + 1 receiptless
escape; K3 inconclusive) that remains un-repaired at the tip. The lesson's
wave-1 resend-chunk claim ("12/12/8") is not a target-document claim and was
checked anyway: `w1/spawn-result.txt` records exactly 12/12/8 seat names, so it
holds.

## Findings

### Mismatches (LOG.md round-28 entry)

1. **`LOG.md:1810-1811` — "The pinned snapshot server-schema.cpp was re-fetched by 13 data seats (sha256 1f9d7b73…0050 each time)"**
   - Evidence: the snapshot's pinned sha `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050` appears as an *own-fetch* record in the wave-1 data seats' reports for **14** seats: `w1/out/DataG01/rows.json`, `DataG02/rows.json`, `DataG03/rows.json`, `DataG04/rows.json`, `DataG05/rows.json`, `DataG06/rows.json`, `DataG07/rows.json`, `DataG08/rows.json` (+ `run-notes.json`), `DataG09/rows.json`, `DataG10/evidence.json` (`schema_fetched_sha256` = `schema_lane_snapshot_sha256` = the pin; saved raw `w1/out/DataG10/raw/server-schema.cpp.github-704366d` hashes to the pin), `DataG11/rows.json`, `DataG13/rows.json`, `DataG14/rows.json`, `DataG15/rows.json`. The lesson gate table names 13 *SOURCES-row openers* (DataG01–09, G11, G13–15); DataG10 also fetched. DataG12/16/17 (the three seats without any sha record) did not fetch.
   - Corrected sentence: "The pinned snapshot server-schema.cpp was re-fetched by 14 data seats (sha256 1f9d7b73…0050 each time; DataG01–09, DataG10, DataG11, DataG13–15 — DataG10 fetched but opened no SOURCES row; DataG12/16/17 did not fetch)."

2. **`LOG.md:1792-1793` — "34 rows from 17 data seats that each measured their assigned fields live"**
   - Evidence: `registry/request-field-outcomes-r28.json` (34 rows, F28-01..F28-34) has a per-row `seat` field; the distinct seat values are **13**: DataG01(4), DataG02(3), DataG03(4), DataG04(2), DataG05(4), DataG06(1), DataG07(4), DataG08(4), DataG09(1), DataG11(1), DataG13(1), DataG14(1), DataG15(4) = 34. The 17 data seats were dispatched and all returned row drafts (DataG10/12/16/17 have `rows.json`), but the landed table carries rows from 13 seats; DataG10/12/16/17's probed fields (speculative/type, json_schema/grammar/reasoning_format, stream/usage/cache_prompt/return_* etc.) produced no landed row (DataG12's json_schema→grammar row was rejected in the lesson gate table).
   - Corrected sentence: "SKILL.md '## Round-28 request-field outcomes': 34 rows, measured live by 13 of the 17 data seats (DataG01–09, DataG11, DataG13–15; DataG10/12/16/17 returned drafts that landed no row), each on its own port in 48201–48217, citing the declaring line of `tools/server/server-schema.cpp` @704366d76 (S140–S173)."

3. **`SHONEN.md:8` — "8 bad fake-server shapes rejected, frozen pair accepted 6" (pre-existing, routed imprecision)**
   - See the SHONEN.md subsection below; reported because SHONEN.md is in scope.
     Not introduced by this round's self-assessment; already routed by round-17
     falsify seat `ShonenProvince.md` P3 and left un-repaired.

### SHONEN.md (pre-existing, routed imprecision)

- `SHONEN.md` line 8: "…`tests/llamacpp-live/controls.py` (8 bad fake-server shapes rejected, frozen pair accepted 6)". Round-17 falsify seat `ShonenProvince.md` P3 already ruled: the 8 controls are 7 bad server shapes (K1–K5, K7, K8) plus K6, a harness-fault (teardown `RuntimeError`) control, not an eighth server shape; the frozen accepted-bad=6 comprises 5 accepted-with-receipt cases (K1, K2, K4, K5, K8) plus K6 escaping without a receipt (tool exit 4, no gate invocation; `controls-frozen.json:118-135` `"receipt_written": false`); K3 was inconclusive, not a demonstrated detection. The wording remains un-repaired in SHONEN at the tip.
   - Corrected sentence (P3's recommendation): "…and `tests/llamacpp-live/controls.py` (8 adverse controls rejected: 7 bad server shapes + 1 injected teardown fault; frozen accepted-bad = 6 (5 accepted bad receipts + 1 receiptless escape), with K3 inconclusive)."
   - Note: this is a known, already-routed round-17 finding, not introduced by the round-28 self-assessment; it is reported for completeness since SHONEN.md is in scope.

## Verified statements — the remaining 43 (46 − 3)

### SCORECARD.md `## Round 28` (lines 1404–1441) — 14 statements, all hold
- Round-28 section exists at line 1404; base `4179301f` = round base; tip `9ce5bd37` landed.
- "Lowest axes at the start: depth, calibration and adjacency, all 7 (round-27 section)" — round-27 section: C1 depth 7→7 (line ~1365), X1 calibration 7→7, "Other scores held: operability 8, freshness 8, coverage 9, adjacency 7" ✓.
- Preregistration path ✓; A0 frozen `d8bf1804` ✓ (commit exists); amendment A1 `75b78bb4` ✓ (commit 08:38:16Z).
- "before any data row landed but after data seat DataG01 had checked its drafts with A0 counter functions at 08:35:54Z" ✓ (CriticA1Legitimacy.md: DataG01 applied `REJECT_RE`/`same`/`outcome_text` at 08:35:53.929–08:35:54.037Z; A1 committed 08:38:16Z; first committed data table/registry at `e49b4cf7` 08:55:40Z).
- Row: depth 7→7, no promotion ✓; base `registered 0 counted 0 target 18 met False` at 4179301f (`before/c1-base.out`) ✓; → `registered 34 counted 26 target 18 met True` (8 rows not counted `e:generic-conversion`) ✓ (final receipt rows all `["e:generic-conversion"]`).
- Counting command `/usr/bin/python3 .ufo/waves/round-28/count-c1.py --out <receipt.json>` from a fresh clone ✓ (file exists; receipt header "fresh clone of origin at e49b4cf7 … counter sha256 a38faefe…49a5").
- Measured commit `e49b4cf7` with `final/c1-e49b4cf7.out` ✓; A0 same tree 34/34 `final/c1-A0-e49b4cf7.out` ✓.
- Evidence: SKILL.md "## Round-28 request-field outcomes" (F28-01..F28-34) ✓ (SKILL.md:1135 heading; 34 `| F28-` rows); `registry/request-field-outcomes-r28.json` ✓ (exists, 34 rows); SOURCES S140–S173 ✓ (`corpus/SOURCES.md:152-185`, contiguous, append-only final passes); lesson `corpus/lessons/round-28.md` ✓.
- Surface paragraph: SKILL decision table ✓; `tools/server/server-schema.cpp` @704366d76 ✓; transform handlers `lora`, `logit_bias`, `ignore_eos`, `stop`, `samplers`, `preserved_tokens` ✓ (all present in SKILL table rows / meaning cells).
- "Before this round no lane document named server-schema.cpp, set_hard_limits or the bounds message" ✓ (`git grep -l -i "server-schema" 4179301f` over PROVINCE.md, corpus/README.md, corpus/knowledge/*.md, SKILL.md, LOG.md, SCORECARD.md → exit 1, no hits; `w1/out/ScoutProvince/grep-hits.txt` shows only `.ufo/waves/…` snapshot/control-fixture hits).
- "same counter at base (counted 0)" ✓.
- Controls: pre-freeze evidential maximum 14 (source-blind, A0) ✓ (CtlSourceBlind 14/38); type-only 20/52 A0, 0/52 A1 ✓ (CtlA1Conversion receipt-A0.json counted 20 met true; receipt.json counted 0); re-scored pre-freeze fixtures at most 9 ✓ (CtlA1Rescore: source-blind 14→9, label-keyed 12→7; receipt.json counted 9); fixed README-and-names 11/38 ✓ (CtlA1BlindPlus counted 11); five holds ✓ (HOLDS.md: CtlNoReader, CtlObjectStore, CtlAllFalse, CtlEcho, CtlSourceMisuse).
- Limits paragraph ✓ (SKILL.md:1141 argv `n_parallel` 4; :1151 "n_cmpl's upper bound is n_parallel"; F28-34 "200, samplers = […]" matches "'200, key = value' is the stored setting").
- Other scores held: operability 8, freshness 8, coverage 9, calibration 7, adjacency 7, depth 7 ✓ (matches round-27 end-state).

### LOG.md round-28 entry (lines 1790–1819) — 11 statements, 9 hold, 2 mismatch (above)
- "34 rows from 17 data seats" — mismatch (find 2).
- "each measured their assigned fields live on the pinned b11755 fixture (own ports 48201-48217)" ✓ (DataG seat `port` fields 48201–48217, one per seat; e.g. DataG10 port 48210; b11755 paths throughout).
- "cited the declaring line … (S140-S173)" ✓.
- "Frozen counter from a fresh clone at e49b4cf7: registered 34 counted 26 target 18 met True (.ufo/waves/round-28/final/c1-e49b4cf7.out)" ✓.
- "Order of events … corpus/lessons/round-28.md §Claims" ✓.
- Evidence motivating A1: DataG03/05/07/08 rows with 1e39 → 3.4028234663852886e38, 4294967296 → 0, 2.5 → 2 ✓ (rows.json values verified).
- CtlA1Conversion 20/52 A0, 0/52 A1 ✓.
- Repairs: `count-c2.py` recomputes cells from raw bytes ✓ (`.ufo/waves/round-25/count-c2.py:36,46-54` raw-sha recomputation); KQ37 round-28 qualification ✓ (`corpus/QUALITY.md:264` "## Round 28 qualification -- KQ37", items 1–4); `tools/echo-recheck.py` ✓ exists; SKILL instrument registry rows ✓ (SKILL.md:1219); `tools/gate-registry-check.py` (base exit 1, tip exit 0) ✓ (`w1/out/ExecGateRegistryCheck/base-4179301.out` "unregistered …round-25/count-c2.py … round-27/count-c1.py; registered 2 unregistered 2" + exit file 1; `final/gate-registry-final.out` "registered 5 unregistered 0" exit 0).
- "re-fetched by 13 data seats" — mismatch (find 1).
- "echo-recheck same 6/6" ✓ (`w1/out/ExecEchoRecheck/run1.json` total 6 exit 0; `run2.json` total 6 exit 0).
- "Wave 2 (falsify, 32 seats)" ✓ (`w2/spec.json` 32 items; `w2/spawn-result.txt` started=32 refused=[]; dispatch 08:57:46Z). "Every row re-measured live by a second seat; all 34 outcomes reproduced" ✓ (RowReview01–17 cover F28-01..F28-34; RowReview04/07/16/17 out dirs contain live probes/base.json; RowReview08 "both rows HOLD"; RowReview11 "both original observations agree with this re-measurement"). "Meaning-cell over-generalisations corrected (18 cells, counted cells unchanged)" ✓ (the 18 ids F28-03/04/05/07/08/09/11/14/16/17/19/20/21/22/25/27/33/34 match RowReview prose-correction findings; counted cells unchanged per A1 receipt). "CriticA1Legitimacy: A1 was written after a data seat had checked drafts with A0 counter functions (08:35:54Z)" ✓; "author does not promote depth (7 → 7) and reports both rules" ✓.

### corpus/README.md `## Frontier disposition — round 28` (line 423) — 6 statements, all hold
- "SKILL.md '## Round-28 request-field outcomes' … request-field schema (tools/server/server-schema.cpp @704366d76)" ✓. "hard-bound rejects, silent clamps and handler transforms for POST /completion" ✓ (SKILL table + "POST /completion" appears 3× in SKILL). `registry/request-field-outcomes-r28.json` ✓. "sources S140-S173" ✓. "counter .ufo/waves/round-28/count-c1.py" ✓ exists. "Before round 28 the surface was absent from PROVINCE.md and from every frontier list" ✓ (base grep exit 1). Open list (chat completions, json_schema→grammar, n_parallel-dependent bounds, other builds/engines, K05) ✓ consistent with the lesson gate decisions (DataG12 json_schema row rejected, disclosed).

### PROVINCE.md round-28 note (lines 109–114) — 4 statements, all hold
- Schema @704366d76 ✓; "hard-bound rejects, silent clamps, handler transforms, as stored in generation_settings" ✓ (SKILL table outcomes/meaning cells + generation_settings mentions); "via SKILL.md '## Round-28 request-field outcomes' (S140-S173)" ✓; scope qualification (not sampling quality/model identity/registered endpoint health) ✓ consistent with table.

### SHONEN.md — 11 statements, 10 hold, 1 pre-existing routed imprecision
- "LOG.md §§round 1–3 records executed endpoint reconciliation" ✓ (LOG.md:7/100/203 headings exist).
- "Round 16 … .ufo/waves/round-16/live/receipt.json — 10/10 checks on the pinned llama.cpp b11755 build" ✓ (receipt `checks` length 10, zero failed; model digest matches b11755 fixture).
- "1.2 MB CI fixture GGUF" ✓ (`stories260K.gguf` = 1,185,376 bytes ≈ 1.2 MB).
- "MODEL_OK/matched exit 0 … MODEL_MISMATCH/served-id-mismatch exit 2, teardown proven" ✓ (receipt verdicts MODEL_OK/MODEL_MISMATCH present; pdeathsig field present).
- "Round 17 … receipt-{1,2,3}.json (11/11 checks each … gate VALID with four pins)" ✓ (each receipt: 11 checks, 11 `passed: true`; `gate.txt` VALID for all three, probe/tool digests printed; round-17 falsify confirmed the four pins = model/server/probe/tool digests).
- "tests/llamacpp-live/controls.py (8 bad fake-server shapes rejected, frozen pair accepted 6)" — pre-existing P3 imprecision (noted above).
- "SKILL.md §§Decision table, Error signatures, Checklist" ✓ (SKILL.md:125/167/193).
- "PROVINCE.md §Write boundary" ✓ (:45). "corpus/knowledge/snapshot-history.md §Run it" ✓ (:7). "corpus/knowledge/cross-lane-scope.md" ✓ exists.

## Residual risk / verification gaps
- The 16 wave-2 RowReview seats that recorded the pinned sha in prose (all but RowReview04, which has fetch files) are treated as re-fetchers; I did not verify each individual curl transcript (only DataG10's and lesson gate-table openers' fetches were inspected file-level). This does not affect the flagged counts, which concern wave-1 data seats.
- The claim "17 data seats measured every declared field live" is checked via `rows.json` presence and the w1 spec's 17 DataG seats; I did not re-derive every row's HTTP transcript.
- SHONEN's "no non-author mark" is not independently verifiable from the repo.
