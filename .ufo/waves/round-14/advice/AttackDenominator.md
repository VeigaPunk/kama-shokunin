# AttackDenominator — round 14 (critic, read-only)

Scope: is C1's before → after an honest **new-capability** count, not a disguised semantic repair? Is outside D2 kept **supplemental**, not a second claim? Static review only. No tests, builds or harness runs. One exit-code fact check (A1) was run against a nonexistent path, not against any deliverable. Tools installed/updated: none.

State at review: `tools/kama-ollama-evidence.py` was absent. `tests/ollama-evidence/` existed but was empty. `.ufo/waves/round-14/measure.py` was absent. The contract says these are pending, not defects. `corpus/lessons/round-14.md` (L1 draft, 40 lines) was present and was reviewed.

## Baseline facts (observed)

- `git ls-tree -r --name-only e1b3d746…` lists only `tools/kama-probe.sh`, `tools/test-snapshot.sh` and `.ufo/waves/round-13/measure.py` under tools/measure paths. No Ollama classifier exists at the start commit.
- A case-insensitive grep of `tools/` for `api/tags|api/ps|remote_model|remote_host` returned nothing. The only prior identity logic is `kama-probe.sh:370-371` `normalize_id`, which takes the basename and strips `.gguf` for live `/v1/models`. It cannot consume tags/ps captures offline.
- Prior knowledge is prose. It labels the digest join a candidate, not a fact (`served-identity-crosswalk.md:45`: "the tags-to-ps digest join is an [INFERENCE] candidate"). Case 3 (`:35`) says ps absence "must not be concluded either way".

So the only true baseline is **unsupported**: there is no executable to fail. No old behavior misclassified anything, and nothing here can show that it would have. Any "red-before" wording claiming a semantic error would be **false provenance**.

## Counterexamples

### A1 — RESOLVED in the committed harness (was HIGH): an absent tool could score as passing on exit-2 cases
`python3 /nonexistent-kama-tool.py …` gives **exit 2** (observed: "can't open file … [Errno 2]"). An argparse usage error also exits 2, with no JSON. The contract maps `unknown` and `invalid_input` to exit 2, and these are the largest expected class: malformed, missing, duplicate, GGUF/case, missing-ps.

Consider a harness that checks exit codes alone, or one that lets an exit match count as partial credit when stdout is not JSON. Its "before" run would show roughly half the cases passing with no tool present. That corrupts the denominator in both directions: the before value is no longer N, and a broken after-tool still passes those cases.

**Smallest fix (Harness):**
1. Before spawning anything, check that `--tool` is a regular file. If it is not, every record gets `observed_finding: "tool_unavailable"` (or similar), `observed_exit: null`, and `pass: false`, without spawning.
2. A case passes only if the exit matches **and** stdout parses as a JSON object with schema `kama-ollama-evidence/v1` **and** `finding_id` matches.
3. Never let a parse failure match an exit-2 expectation.

**Disposition (static read of `measure.py`, after Harness replied):** resolved.
- `measure.py:319` checks `tool.is_file()` before running anything. An absent tool becomes `unsupported_record`: `passed` false, `observed_exit` null, finding `unsupported`. The child is never spawned.
- `:286-289` passes a case only when there is no stdout/parse problem **and** the exit is equal **and** the JSON `finding_id` string is equal.
- `:251` catches a child that fails to start (`OSError`) and records it as unsupported.
- `:349` emits `cases_sha256`, which pins before/after to the same fixtures.

Residual (low): schema equality does not affect pass/fail; it is only recorded (`observed_schema`). A tool printing a bare `{"finding_id": …}` could pass without declaring `kama-ollama-evidence/v1`. This is acceptable under L1's literal exit+ID pass rule, provided the report states that the schema is recorded, not checked.

### A2 — HIGH: the before→after delta measures only that the tool exists
With the tool absent, the before value equals `len(cases)` no matter what the cases contain. "N failed → 0 failed" therefore only says that a co-authored tool now agrees with fixtures written alongside it. Fixtures was told to "coordinate concrete fields with Classifier".

**Fix (lesson/report wording):**
- Before: "N/N unsupported (no classifier at start commit, from git ls-tree; harness `--tool <absent>` gives `tool_unavailable` × N)".
- After: "N/N literal matches".
- Do not call this red→green, "fixed misclassification" or "repaired".
- Both runs must record the same `cases.json` SHA-256. If the fixtures change between runs, the comparison is void.
- The before run is a retrospective baseline taken at measurement time, not an observation from the start of the round. Say so.

### A3 — MEDIUM: discriminating power is not shown by N/N
A classifier that always returns the same `finding_id` still passes every case of that class. If cases are mostly `invalid_input`/`unknown`, a fail-closed constant stub scores near half. If there is only **one** `loaded_same_digest` case, a classifier that never returns loaded scores N−1 out of N.

**Fix (Fixtures + report), no new tooling:**
- Report the count of each `expected_finding` class and the bound "constant-output maximum = largest class / N".
- Use at least two positive `loaded_same_digest` cases with different shapes, for example: an extra unrelated ps entry; and the match by `name` versus by `model` (only if the ambiguity owners pin that `model`-field selection is non-conflicting).
- Mark which cases are overclaim traps: inputs where a naive reading would say loaded or available (remote with equal digest, digest mismatch, missing-ps input, duplicate selected, GGUF/case, non-string remote). Report that subset count separately. It is the calibration-relevant part of the denominator (compare the round-11 `verification/ClaimAxis.md` "same measurement, different label" warning).

### A4 — MEDIUM: selftest and harness are one measurement, not two
`--selftest` and `measure.py` read the same committed `cases.json`. Two green runs over the same oracle are not corroboration.

**Fix:** report them as the same fixture oracle run by two runners. The lesson Gate row's "independent literal fixtures" should say "separately committed same-round literal fixtures". They are independent of the implementation file but not of its authors.

### A5 — MEDIUM: the D2 row is entangled with C1 (draft `round-14.md:29`)
The D2 Mistakes row's fix column says "KQ17 and replay fixtures separate finding IDs, aggregate exit and readiness. Failure-capable controls must reject available-only/remote/malformed…". This ties D2 to the C1 fixtures, so the replay corpus reads as part of the D2 fix (and the reverse).

D2 is a prose clarification of `round-12.md:213`. It has no counting command and no red-before. The verifier classes it as "status-neutral historical presentation debt, not a falsified round-13 C1 or new axis harm" (`round-13-verifier-spotcheck.md:266-267`).

**Smallest fix:**
- The D2 row fix is only "appended named clarification (§Named historical clarification); old lesson/receipt/code unchanged".
- Discovery credit goes to the round-13 outside verifier.
- Move the replay-control obligation to the C1 Gate/claim.
- Exclude D2 from the C1 count and from every axis or trend delta.
- In `round-14.md:34`, change "routed-debt closure" to "routed-debt clarification; closure is for outside review". The author cannot certify closure.
- KQ17 may state the general rule ("outer verdict distinct from selected sub-count"), but a KQ count of 16 → 17 is not a D2 measurement.

### A6 — MEDIUM: Mistakes row 2 blames earlier prose that was correct (`round-14.md:30`)
The class "unsupported operational inference" with evidence "crosswalk holds a prose digest join but no runnable offline classifier" frames a missing capability as an earlier error. The crosswalk already labeled the join `[INFERENCE]` (`:45`) and forbade concluding from ps absence (`:35`). This is the "new capability presented as repaired old behavior" failure this seat is asked to catch.

**Fix:** remove the row from Mistakes, or reclass it as "capability gap (no prior defect)" and state that the crosswalk is not corrected. Mistakes then hold only D2 plus any real defects found during this round.

### A7 — LOW: the finding name conflicts with existing knowledge unless glossed
`available_not_loaded` read without a qualifier contradicts crosswalk `:35`. This is a second authority, not an additive capability. AttackStaleness CE2 and HistoricalIntegrity reached the same conclusion.

**Fix:** reasons and the replay entry should say "absent from the supplied ps capture". Do not rename the contract ID.

### A8 — LOW: axis double counting
The same N→N count must not support "improved" on more than one axis. Calibration gets the fail-closed/overclaim-refusal substance (A3 subset). Operability stays unchanged because no serving runtime is involved. Expansion may credit new runnable repertoire only, not new knowledge, per `round-14.md:7` and PriorCoverage. Quality and discernment get no credit from this count. Numeric calibration stays 7 → 7, delta 0, as drafted.

## What already holds in the draft
- `:7` "new runnable repertoire, not a claim that the conceptual tags/ps distinction is new".
- `:9` readiness is unknown and the join is labeled [INFERENCE].
- `:34` the old bytes are unchanged and the text says "not a second axis claim".
- The Gate rejects GGUF normalization and readiness claims.

Except for A5/A6, the claim framing is honest. The remaining risk is mechanical (A1) and in how the denominator is reported (A2–A4).

## Limits
- The classifier, fixtures and harness were absent, so A1/A3 are contract- and fact-derived candidates, not observed defects.
- Class distribution and the positive-case count cannot be measured until `cases.json` lands.
- No seat output is outside admission.

## Owner notes sent
- Harness: A1.
- Fixtures: A3.
- QualityCriterion, to forward to the lesson owner: A5 and A6.
- No shared files were edited.

## Follow-up — KQ17 (static read of `corpus/QUALITY.md:72`)
- **A5 is satisfied inside KQ17.**
  - D2 is credited to the round-13 non-author verifier.
  - It is labeled "append-only historical clarification … not a round-14 measured case, axis or trend".
  - The outer finding/exit is kept separate from the anchored count, and no KQ count is offered as a D2 measurement.
- **The A5/A6 lesson rows are still open.** They belong to the L1 lesson owner, not QualityCriterion; QualityCriterion routed them to `KamaR14`.
- **New coupling (low).** The KQ17 motivating-lesson cell cites `round-14.md §Mistakes (… unsupported operational inference)`. A6 recommends removing or relabeling that row. If L1 does, KQ17's citation must change in the same integration, or it points at a row that no longer exists.
- **A7 is partly covered.** KQ17's reject column forbids reading tags presence as loaded. It does not gloss `available_not_loaded` as "absent from the supplied ps capture".

## Final disposition (static re-read, after QualityCriterion reply)
- **A5 resolved.** `round-14.md:29`:
  - The D2 fix is the appended clarification.
  - It reads "Discovery credit belongs to CloseKamaR13; no C1 count or axis/trend credit".
  - It reads "Outside review determines routed-debt closure".
  - `:34` reads "supplementary historical clarification pending outside disposition, not a second axis claim".
- **A6 resolved.**
  - The "unsupported operational inference" row is replaced by `ambiguous design precedence` (`:30`), a real defect in this round's spec.
  - `:34` states "A missing executable replay tool was a capability gap, not an error in the already-correct conceptual crosswalk."
- **Coupling resolved.** KQ17 now cites `ambiguous design precedence` and `verdict/count conflation` (round-13 outside D2). The cite to the removed row is gone.
- **A7 resolved in KQ17.** KQ17 now glosses `available_not_loaded` as "absent from the supplied ps capture only". The replay knowledge entry and the classifier's `reasons` should carry the same gloss; their owners have not confirmed it yet.
- **Still open for L1's final report:**
  - A2: wording plus the same `cases_sha256` in both runs.
  - A3: the count for each finding class, the bound a constant-answer classifier could reach, and at least 2 `loaded_same_digest` cases. This needs the final `cases.json`.
  - A4: selftest and harness read the same fixtures, so they are one check, not two.
  - A8: the measurement supports "improved" on calibration only.
