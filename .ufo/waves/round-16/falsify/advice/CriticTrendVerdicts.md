VERDICT: partial — round-16 trend verdicts (expansion, quality, discernment) against LEARNING.md:31-46, at lane commit b8e485c

Seat: KamaR16.CriticTrendVerdicts (critic, lane-dispatched, so this is **not** the outside spot-check; LEARNING.md:45-46 "A subagent the lane dispatched is still the lane").
Nothing at b8e485c states a round-16 trend verdict yet: SCORECARD.md:571-598 ends "Measured values are appended below after execution", and LOG.md:952-953 says "Measured results follow in the next entry". So these are proposals for L1, each with the strongest counterexample I could find.

## Proposed verdicts

| Trend | Proposal | Condition / counterexample |
|---|---|---|
| expansion | **improved, conditional**. Not admissible as landed. | (a) the `live-llamacpp-lifecycle` capability row does not exist in SCORECARD yet; (b) the new entry fails KQ6 for its engine-contrast sentences (E2). If (b) is not fixed, LEARNING:33's `harmed` clause ("an admitted entry fails the bar it was admitted under") applies, and the round becomes a trade, not an improvement. |
| quality | **improved**, provided Q2 and Q3 are fixed. The evidence can be checked mechanically; it does not rest on author judgment alone. | A weaker README-derived claim (round 11) is superseded by stronger pinned code and marked in place. Two leftover defects work against the "no admitted entry failing its re-check" condition. |
| discernment | **unchanged** (pending outside round-16 sample). An `improved` here would rest on author-only judgment, so I refute it. Not `harmed`. | There is no non-author admit/reject sample for round 16. KQ19 does have a lesson behind it. |

## Evidence: commands run (all from the lane root unless noted)

- `sha256sum .ufo/waves/round-16/sources/llama.cpp-704366d/*` gave exit 0. The digests equal pins.json and S035/S036/S037: README `714c067b…6a37`, server-http.cpp `24ede172…5fdb`, server.cpp `21439622…aef4`. pins.json lists four files; server.cpp is missing from it, although its digest matches the S037 cell. This is a minor gap in the manifest.
- `sed -n` on the pinned server-http.cpp and server.cpp gave exit 0 and confirmed each cited line:
  - 307-325: the gate returns 503 with `{"message","Loading model"},{"type","unavailable_error"},{"code",503}`.
  - 354-358: order is OPTIONS, then state, then API key.
  - server.cpp:460: the router sets `is_ready.store(true)` right after `start()`.
  - 493-515: comment "start the HTTP server before loading the model", then `load_model`, then `is_ready.store(true)`.
  - `frontend_paths` (server-http.cpp:242-248) is `"/"` plus UI assets only, so `/v1/models` is **not** exempt.
  - The only `is_ready` stores are at server.cpp:460 and 515.
- Upstream key order: I fetched `common/json.h`, `common/json.cpp` and `server-common.h` at 704366d76 into /tmp with curl (rc 0). `server-common.h:25 using json = common_json;` and `json.cpp:14 using nlohmann::ordered_json;` plus the storage `static_assert` show that common_json wraps ordered_json. Insertion order `message, type, code` is therefore supported by code. See Q4.
- `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-16/live/receipt.json` gave exit 0, `VALID`. The same gate on `receipt-frozen-probe.json` gave exit 0, `VALID`. Both reads are offline; no server was started.
- I parsed the stored `run-before.json` / `run-after.json` in Python without rerunning them:
  - before: exit 1, tests 72, passes 55, failures 17;
  - after: exit 0, 72/72/0;
  - the failed set equals the changed `(verdict, reason, exit)` set equals the set expecting `MODEL_LOADING`, 17 each, `True`.
  - `measure-stdout.txt` says "directional: loading_expectations=17 before_failed=17 changed=17 equal=True".
- `sha256sum frozen/kama-probe-before.sh` and `git cat-file blob 20e392e:tools/kama-probe.sh | sha256sum` both give `93ee4302…cd64`. Frozen lines 513-522 read `C_VERDICT=FOREIGN_SERVICE` … `C_REASON=non-2xx-non-model-http`, so the M1 anchor holds.
- Things I did not run: measure.py (forbidden), the probe-verdict stub matrix (it binds ephemeral loopback ports, and no command was named to me), and any llama-server.

## Expansion

What counts as new ground:
- The code-level gate covers `/v1/models` at b11755, and it fires before the API key (a loading server answers 503, not 401). Source: S036/S037, new sourced distinctions.
- The `MODEL_LOADING` probe mapping.
- The live capability.
- A new **source kind**: `dataset` (S039). It is the only dataset row; all other S035-S041 kinds already existed. An awk census of the SOURCES kinds gave `dataset: S039`.
- Every S-row the entry cites is `mined` (awk over SOURCES.md: S017 and S035-S041 all `mined`). Its coverage-map row is at corpus/README.md:206.

Counterexamples:
- **E1, capability not admitted.** A grep of SCORECARD.md for `live-llamacpp-lifecycle` finds only :588 (planned prose). The Capability tables are at :124 and :457, and neither has this row. `lessons/round-16.md:94` cites `.ufo/waves/round-16/acceptance.json`; `ls` gave exit 2, no such file. Until L1 appends the row and the receipt, no expansion credit can come from "a capability admitted to SCORECARD.md" (LEARNING:33). The precedent is round 14, where the row entered only after the demonstration (round-14.md:168).
- **E2, KQ6 failure inside the admitted entry.**
  - `llamacpp-loading-lifecycle.md:68-74` states vendor facts. Quotes: "vLLM v0.32.0, TGI v3.3.7 and KoboldCpp 1.123.1 (default mode) do not listen until ready"; "SGLang v0.5.22 answers `/v1/models` 200 while `/health` is 503"; "LM Studio documents no 503".
  - `:80-83` adds the b6000-b7502 history. All of these cite only `.ufo/waves/round-16/build/advice/` files.
  - KQ6 (QUALITY.md, round-10 table) requires a vendor statement to cite "an opened `SOURCES.md` row whose tier fits that scope".
  - SOURCES.md search log (:111-112): "kept as wave advice, not rows".
  - The advice files do carry pins (ScoutVllmStartup:18 v0.32.0; ScoutTgiStartup:8 `dfb3fbe7…`; ScoutSglangStartup:7 `baa9bef…`; ScoutKoboldCppServer:8 `9be8c136…`; ScoutLocalAiStartup:9 `58830f7a…`), so this is a fixable bookkeeping defect, not a false claim.
  - The Gate's reject row (round-16.md:52) rejects *generalizing* MODEL_LOADING. It does not admit the contrasting facts, yet the entry states them as knowledge.
  - "LM Studio documents no 503" and "None of these emits this body" are also negative claims under KQ9, which needs a full-set read on record.
- **E3, overlap not disclosed (KQ12).** The entry's "Earlier corpus ground" (:17-20) and README:209-211 credit only the round-10 `/health` body. But lifecycle items 5-6 (router `status`, sleep served from cache) were already held by `served-identity-crosswalk.md:28,34` (round 11, S001). Credit must exclude router and sleep.

Smallest safe correction:
- (i) L1 appends the capability row plus acceptance.json after measurement.
- (ii) Either add pinned SOURCES rows for the engine scans and the llama.cpp tag history (S042+, pins already in the advice) and update used-by, **or** append a dated correction to the entry that demotes :68-74 and :80-83 to "[wave advice, not admitted knowledge; no SOURCES row]".
- (iii) Append one line naming crosswalk rows 28/34 as prior router/sleep coverage.

With (i)-(iii): expansion is **improved**. With (i) only: the strict reading is a trade (`improved` plus an admitted entry failing KQ6), and it is not admitted.

## Quality

The strongest supporting evidence, which I checked independently:
- The round-11 crosswalk claimed as *new* "llama.cpp `/v1/models` answering while loading (S001)" (`served-identity-crosswalk.md:13`, also :33, :52, :63). That reading was README-derived at c0fd7862.
- Round 16 supersedes it, at b11755, with pinned code: S036 gate, `frontend_paths` without `/v1/models`, and S037 ordering. The digests and lines are verified above.
- The supersession is marked in place by a scoped, revision-limited correction ("does not hold for direct llama-server at b11755"; crosswalk §Correction round 16).
- `runtime-health-surface-matrix.md:14` (README @c0fd7862) is re-checked as "consistent with that code" at the newer pin.
- `endpoint-identity.md:188-197` marks the line-3 "vocabulary is fixed", line-163 and rule-5 overreach.
- S040 supersedes the dead-URL S021 by row, without editing S021's cells.
- This matches LEARNING:34 "a weaker entry is superseded by a stronger one". It is also revision-honest: RevengerEnvelopeHistory:24-25 shows `/v1/models` was exempt at b6000-b7502, so the old README reading may have been true at older builds, and the correction does not say otherwise.

Counterexamples:
- **Q2.** `runtime-health-surface-matrix.md:35` asserts KQ6 clearance: "every engine statement names engine + documented revision … and cites an opened `SOURCES.md` row". The round-16 append at :66-72 adds engine statements about vLLM v0.32.0, TGI v3.3.7, SGLang v0.5.22 and Ollama that cite only advice files. That is the same E2 defect, and it now makes an existing admitted entry's own clearance false.
- **Q3.** `endpoint-identity.md:126` (anti-pattern table) still reads "A live non-`2xx` non-HTML response is a foreign service", which is the rule-5 overreach restated. The round-16 correction names lines 3, 17, 161 and 163 but not 126. Under LEARNING:34 `harmed` ("found false or stale and left unmarked"), this is minor but literal.
- **Q4.** This one is about attribution, not truth. `llamacpp-loading-lifecycle.md:48-50` says "The live server sends keys in `message, type, code` order". No receipt captured a 503: receipt.json has `loading_observed: false` and `loading_503: null`. The only live witness is the unreceipted L1 smoke (LOG.md:930-934; entry :105-106). The claim is true by code (ordered_json, above), but as worded it rests on an author-only, unreceipted observation. Fix: re-attribute it to code (`common/json.cpp:14` at 704366d76) or label it "unreceipted L1 smoke".
- Not a defect: every re-check here is against code or docs, not a live loading server. Do not describe the loading claims as live-verified (the entry's own limit at :121-122 already says so).

Smallest safe correction: append the Q2 fix (same as E2(ii)), add one appended line in endpoint-identity naming :126, and re-attribute Q4. With these, quality is **improved**.

## Discernment

- `ls corpus/lessons | grep -c round-16` gave 1: only `round-16.md` exists, with no `round-16-verifier-spotcheck.md`.
- `round-16.md` §Gate (:36-58) has no spot-check result, although LEARNING:71-72 requires "the spot-check result".
- The QUALITY.md round-16 header says "author-appended; no outside review yet".
- M2 (round-16.md:65) is "Captured-by: outside the author: `SimplifierHarness.md`, `ReviewShonenEvidence.md`". Those are lane-dispatched build seats, so this is **not** outside discernment evidence and must not be cited as such.
- This falsify wave, including this seat, is lane-dispatched too.
- So `improved` would be author-only and I refute it. `harmed` does not apply: KQ19's motivating lesson is "`round-16.md` §Mistakes M1 and §Gate" plus the run receipts (QUALITY.md:109 tail), so the criterion has a lesson behind it. The round-15 outside sample recorded no disagreement (round-16.md:85-86), so no criterion was owed.
- The upgrade path is the precedent of round-14/15 verifier-spotcheck files. A non-author samples at least one admit (for example Gate :42, the KQ19 triple) and at least one reject (for example :44 widen-to-any-503, or :52 cross-engine generalization) and records agree or disagree with reasons.

## Impacted axes

- calibration: the KQ6/KQ12 bookkeeping in E2/E3/Q2.
- coverage/adjacency: this is where expansion credit lands.
- depth/freshness: quality.

C1/C2 score claims (7→7, 8→8) are not contested by this seat. The stored receipts reproduce 55/17 → 72/0 with changed set equal to the loading set (17), and both live receipts are VALID.

## Limitations

- I did not open the engine-scan upstream pages myself. E2 is a provenance defect; I did not test whether the claims are true.
- The stub matrix and live harness were not re-run.
- Later L1 appends (capability row, acceptance.json, trend lines) may resolve E1.

## Installs

None. Scratch `/tmp/kama-r16-CriticTrendVerdicts/` was removed. No llama-server was started.
