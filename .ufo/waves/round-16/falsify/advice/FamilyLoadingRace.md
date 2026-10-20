VERDICT: partial — all 9 literal oracles in `tests/probe-verdicts/LoadingRace.json` are correct against the landed `classify()`/C1 rule and pass 9/9 (frozen probe: 4/9, failing exactly the five MODEL_LOADING rows), but one `why` claim is false about b11755 reachability, three of the five loading rows are graded/mutant-equivalent duplicates, and the family alone cannot detect a type/code-ignoring or expect-gated matcher.

Target: `tests/probe-verdicts/LoadingRace.json` @ sha256 `5644e10ed47ad8521eeadc3b9137553d5303790447575085580e6570ad95c108` (9 rows, 5 MODEL_LOADING). Probe under test: the blob committed at `b8e485c`, sha256 `6edd3c4cfdf3f86c98202cef58859c29406d4a9cec17495454c514ac5972fa50`. At report time the working tree carried an uncommitted comment-only header hunk in `tools/kama-probe.sh` (5 insertions / 3 deletions, no code line changed; tree sha256 `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`); the 9 rows pass 9/9 on both blobs. Line citations below refer to the committed blob; the working tree shifts code lines by +2. No lane file was modified by this seat.

# 1. Literal oracles — confirm (9/9)

Derivation read from `tools/kama-probe.sh` (committed blob): `classify()` at :451, loading gate at :503-507, model-array path at :522-546, generic non-2xx tail at :556-565. All expected triples reproduce exactly:

| Row | `/v1/models` stimulus | Path reached | Oracle |
|---|---|---|---|
| HealthAlreadyOk | 503 + exact envelope | :503-507 | MODEL_LOADING / llamacpp-loading / 2 ✓ |
| HealthExplicit404 | 503 + exact envelope | :503-507 | MODEL_LOADING / llamacpp-loading / 2 ✓ |
| HealthUnlisted | 503 + exact envelope | :503-507 | MODEL_LOADING / llamacpp-loading / 2 ✓ |
| HealthAlsoLoading | 503 + exact envelope | :503-507 | MODEL_LOADING / llamacpp-loading / 2 ✓ |
| HealthConnClosed | 503 + exact envelope | :503-507 | MODEL_LOADING / llamacpp-loading / 2 ✓ |
| InverseHealthLoadingModelsOk | 200 + `data[].id` = expect | :534-537 | MODEL_OK / matched / 0 ✓ |
| InverseWildcardExpect | 200 + `data[].id`, expect `*` | :530-532 | MODEL_OK / expected-wildcard / 0 ✓ |
| InverseHealthLoadingIdMismatch | 200 + `stories260K`, expect `qwen3-8b` | :535-539 | MODEL_MISMATCH / served-id-mismatch / 2 ✓ |
| HealthOkNonLoading503 | 503 + different `unavailable_error` body | :556-565 | FOREIGN_SERVICE / non-2xx-non-model-http / 2 ✓ |

The one non-obvious case, `HealthOkNonLoading503`: `body_is_llamacpp_loading` rejects `message: "no slot available"` (:442), the body is not 2xx, not HTML, has no model array, so the non-2xx FOREIGN_SERVICE tail sets exactly `non-2xx-non-model-http`. Exit 2 is also the harness-consistent drift exit (`check.py` validates `exit == (0 if verdict == MODEL_OK else 2)`).

Source claims in the rows check out against the pinned b11755 tree:
- `server-http.cpp:307` `middleware_server_state`, `:308` `if (!is_ready.load())`, `:314-325` status 503 + `{"message":"Loading model"},{"type":"unavailable_error"},{"code",503}`.
- `frontend_paths` is only `/` + embedded UI assets (`server-http.cpp:242-249`); `/health` is *not* exempt (it is in `get_public_endpoints` at :253 for API-key bypass only), so "b11755 serves the envelope on /health too" is correct.
- Pre-routing order `:331-359` gates before routing, so the registered `/health` handler (`server.cpp:278-279`, `server-context.cpp:5288`, always `{"status":"ok"}` once reached) is unreachable while not ready.

# 2. `why` accuracy — one real defect, two wording nits

**R1 (medium, false reachability claim).** `LoadingRace.HealthAlreadyOk` says: "Synthetic race (not reachable on b11755, where one atomic is_ready gates both paths)". The *instantaneous* state is unreachable, but the exact observation this row encodes is reachable on b11755: `classify()` fetches `/v1/models` first (:454) and only then probes `/health` for the evidence string (:506), while `is_ready` is stored true once after `load_model` returns (`server.cpp:511-515`) and never stored false in the pinned sources. A readiness flip between the two GETs therefore yields precisely `/v1/models` 503-loading + `/health` 200 — the row models the mid-transition observation, not an unobservable state, and its evidence string is what a live probe would emit. [INFERENCE: reasoned from code; llama-server was not started under this seat.] The `why` should say "the simultaneous state is unreachable; the probe's two sequential samples can observe this pair during the transition" instead of calling the row unreachable. Consequence if left: a future maintainer can delete the family's only transition-representative row on the stated rationale.

**R2 (low, wording).** `HealthExplicit404` says `/health` "answers a bare 404", but the route carries `{"error":{"message":"Not Found","type":"not_found_error","code":404}}` and `Content-Type: application/json`. `probe_short` uses `-o /dev/null -w '%{http_code}|%{content_type}'`, so that body is inert (only the header shows in evidence); "bare" is inaccurate and the body suggests an inspection that does not happen.

**R3 (low, mislabel).** `HealthOkNonLoading503`'s "Race boundary" frames a synthetic exactness control as a race. `/v1/models` is not a slot-allocating endpoint, so a real server does not return the `no slot available` envelope there; this row is the "no slot available" stimulus already covered by `ForeignControls.busy-unavailable-error` and `Overbroad503.no-slot-available` (identical `/v1/models` status/body; only `expect` and the `Server: llama.cpp` header differ).

**R4 (info, citation limit).** "one atomic is_ready" — the gate and the two `.store(true)` sites are pinned (`server.cpp:460,515`), and `.load()`/`.store()` syntax implies `std::atomic`, but the declaration lives in a header outside the pinned set (`server-http.h`/`server-context.h`), so "atomic" itself is [INFERENCE].

No row in `LoadingRace.json` contains a line-number citation (`grep -nE ':[0-9]+|lines? [0-9]+'` → no match), so the "frozen numbering" hazard does not apply inside this file. The probe/knowledge citations I checked (307-328, 314-325, 354) match the pristine pinned source.

# 3. Redundancy / discrimination — confirmed redundant block

Graded output for the five loading rows collapses to one tuple: `(MODEL_LOADING, llamacpp-loading, exit 2, drift true, served '-')`. They share an identical `/v1/models` route; only `/health` differs, and `/health` is evidence-only and not graded (`check.py` grades verdict/reason/exit/drift).

I built five one-line probe mutants in `/tmp` and ran the 9 rows through each (`python3 tests/probe-verdicts/check.py --probe <mutant> --json --only <9 names>`):

| Row | status-only-503 | health-must-be-200 | health-must-be-503 | message-only | expect-gated |
|---|---|---|---|---|---|
| HealthAlreadyOk | pass | pass | **FAIL** | pass | pass |
| HealthExplicit404 | pass | **FAIL** | **FAIL** | pass | pass |
| HealthUnlisted | pass | **FAIL** | **FAIL** | pass | pass |
| HealthConnClosed | pass | **FAIL** | **FAIL** | pass | pass |
| HealthAlsoLoading | pass | **FAIL** | pass | pass | pass |
| Inverse* (3 rows) | pass | pass | pass | pass | pass |
| HealthOkNonLoading503 | **FAIL** | pass | pass | pass | pass |

- `Explicit404` / `Unlisted` / `ConnClosed` are an exact equivalence class: identical pass/fail vector `(P,F,F,P,P)` under every mutant, and the 404 body/CT and TCP-close shapes are never inspected beyond `code|content_type`/`err-rc`. Three rows encode one property ("/health need not answer"); any one of them kills the health-gated mutant.
- `HealthAlsoLoading` has an empty unique kill set (its kills are covered by `HealthAlreadyOk` for health-must-be-503 and by the trio for health-must-be-200), yet it is the only row that mirrors the real on-build loading surface (both endpoints 503 + exact envelope). Recommendation: keep it as the canonical loading row and trim the non-200 `/health` trio to one, rather than deleting it.
- `HealthOkNonLoading503` is the family's only exactness control (sole killer of status-only-503) but is the third matrix copy of the `no slot available` stimulus; it adds no discrimination matrix-wide.

# 4. Family-local coverage gaps (mutants that survive all 9 rows)

- `message-only` mutant (predicate reduced to `message == "Loading model"`, dropping `type` and integer `code`): **9/9 pass** in LoadingRace (`check.py` exit 0). It is killed matrix-wide by 7 rows: `EnvelopeShapes.MissingCode`, `EnvelopeShapes.CodeAsString`, `ForeignControls.loading-message-wrong-type`, `NearMissTriple.code-float-503.0`, `NearMissTriple.code-boolean-true`, `Overbroad503.server-error-type`, `Overbroad503.code-string` (65/72, exit 1).
- `expect-gated` mutant (`MODEL_LOADING` only when `expected == "stories260K"`): **9/9 pass** in LoadingRace, while all five loading rows pin `expect: stories260K`. Killed matrix-wide (65/72, exit 1) by `EnvelopeShapes.ExtraFieldsAllowed`, `EnvelopeShapes.Padding64KiB`, `LoadingEnvelope.wildcard-expect`, `LoadingEnvelope.dash-expect`, `LoadingEnvelope.plain-json-content-type`, `LoadingEnvelope.pretty-printed-body`, `NearMissTriple.exact-envelope-labelled-html`.

Interpretation: LoadingRace cannot stand alone as evidence for the exact-triple rule or for loading-verdict independence from `--expect`; the matrix as a whole covers both. If per-family self-containment is required, swap one redundant `/health`-failure row for (a) a loading row with `expect: "*"` and (b) a loading row with a wrong `type`/`code` — accepting the deliberate duplication with EnvelopeShapes/LoadingEnvelope.

# 5. Frozen-vs-current consistency (family contribution to C1)

`python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --json --only <all 9>` → **exit 0**, stderr `tests=9 passes=9 failures=0`.
`... --probe .ufo/waves/round-16/frozen/kama-probe-before.sh ...` → **exit 1**, `tests=9 passes=4 failures=5`; the five failures are exactly the MODEL_LOADING rows (frozen grades them FOREIGN_SERVICE / non-2xx-non-model-http). This family contributes 5 of the matrix's 17 `expected.verdict == MODEL_LOADING` rows (counted across all 9 matrix files), consistent with L1's scope claim "changed set == the 17 loading rows" for this family.

# Limitations

- llama-server was not started (not authorized by this item), so R1's transition observation is a code-level inference, not a live capture; L1's receipts record `loading_observed=false` (ScoutPromiseInventoryLive F1), so no live artifact contradicts or confirms the mid-transition pairing.
- `is_ready`'s declaration and the sleep path (`server-context.h` / sleep implementation) are outside the pinned file set; the inverse rows' "unreachable" claims assume readiness never regresses on sleep (pinned sources contain no `store(false)`; the knowledge entry itself marks sleep as `[INFERENCE … not run]`).
- Mutants were scratch copies under `/tmp/kama-r16-FamilyLoadingRace/` (deleted), one-line semantic edits only; current/frozen runs used the real matrix and harness. Two full-matrix mutant runs were executed; the rest were the 9-row `--only` subset.
- An earlier harness invocation mistakenly ran `check.py` under `bash`, which invoked ImageMagick's `import` and hung; all reported results above use `python3`. No lane file was touched.

Installs/updates: none.
