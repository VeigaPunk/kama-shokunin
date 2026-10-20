VERDICT: partial — all 8 literal oracles (verdict, reason, exit) are correct against the landed `classify()` and the C1 rule, but one `why` clause is empirically false, one `why` provenance claim is ungrounded, and 3 of the 8 rows are exact cross-family duplicates.

# What I ran

| # | Command | Exit | Result |
|---|---|---|---|
| 1 | `python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --json --only <8 Overbroad503 names>` | **0** | `passes 8 / 8` (machine doc captured under `/tmp/kama-r16-FamilyOverbroad503/`, removed per contract) |
| 2 | same with `--probe .ufo/waves/round-16/frozen/kama-probe-before.sh` | **0** | `passes 8 / 8` (frozen also passes all 8 → negative controls) |
| 3 | 15 scratch probes under `/tmp/kama-r16-FamilyOverbroad503/` (removed per contract; `bash -n` exit 0 each), same `check.py --only` set | 0 or 1 | `passes/8`: current 8, frozen 8, M1 4, M2 3, M3 6, M4 8, M5 7, M6 7, M7 7, M8 4, M9 8, M10 2, M11 7, M12 7, M13 8, M14 0, M15 7, M17 3 (all `/8`; check.py exit 0 iff 8/8) |
| 4 | 9 stub runs (8 distinct stimuli) over ephemeral loopback ports: 401/403/200/404/500 + HTML; 503 + HTML body no CT; 503 + `text/html` CT with non-HTML body; 200 + HTML CT + model array | per case | table in §F2 |
| 5 | JSON deep-equality of all 72 rows across the 8 matrix files (`routes`, `port_mode`, `default_route`, `expect`, `expected`) | 0 | 3 exact duplicate groups |
| 6 | `grep -n "no slot available\|Loading model"` over fresh fetches of `server-context.cpp`, `server-models.cpp`, `server-task.cpp` @ `704366d76` (`curl` exit 0, 264205/117111/67241 B) | 0 | only `server-context.cpp:5396` |
| 7 | read lane pins `.ufo/waves/round-16/sources/llama.cpp-704366d/{server-http.cpp:300-335,server-common.cpp:100-125}` and `sources/pins.json` | — | see §F3 |
| 8 | `git status --porcelain .ufo/waves/round-16/` after a mishap (§Deviations) | 0 | receipts clean after restore |
| 9 | re-run of run 1 against the working-tree probe as it stood at 11:03 (`sha256 36b64978…`) | **0** | `passes 8 / 8`; the 11:03 delta is comment-only — reversing the 5 new header comment lines reproduces `6edd3c4c…` byte-for-byte |

Probe identity: all oracle and mutant evidence is against `tools/kama-probe.sh` **sha256 `6edd3c4cfdf3f86c98202cef58859c29406d4a9cec17495454c514ac5972fa50`** (the hash `check.py` recorded). A concurrent, comment-only edit landed at 11:03 (`36b64978…`, header lines 34–38, verified by reverse-mapping to `6edd3c4c…`); run 9 shows the oracles are unchanged under it.

No full-matrix replay and no `measure.py` (prohibited); receipt evidence used read-only (`run-before.json`, `run-after.json`), then restored (§Deviations).

# Oracle audit — 8/8 confirmed

Observed under the landed probe (run 1), identical under the frozen probe (run 2):

| row | observed verdict / reason / probe_exit | expected | |
|---|---|---|---|
| nginx-html-503 | FOREIGN_SERVICE / html-non-model / 2 | same | ✅ |
| error-string | FOREIGN_SERVICE / non-2xx-non-model-http / 2 | same | ✅ |
| no-slot-available | FOREIGN_SERVICE / non-2xx-non-model-http / 2 | same | ✅ |
| lowercase-loading | FOREIGN_SERVICE / non-2xx-non-model-http / 2 | same | ✅ |
| server-error-type | FOREIGN_SERVICE / non-2xx-non-model-http / 2 | same | ✅ |
| code-string | FOREIGN_SERVICE / non-2xx-non-model-http / 2 | same | ✅ |
| no-error-wrapper | FOREIGN_SERVICE / non-2xx-non-model-http / 2 | same | ✅ |
| plaintext-loading | FOREIGN_SERVICE / non-2xx-non-model-http / 2 | same | ✅ |

Mechanism, traced in `tools/kama-probe.sh`: all seven JSON/plaintext rows fail `body_is_llamacpp_loading` (428–447) at exactly one predicate each (wrapper 438–440, message 442, type 442, int-code 441–443, parse/first-byte for plaintext 432–435), then reach the generic branch at 563–565 → `non-2xx-non-model-http`. The nginx row fails the JSON parse and the `<html` sniff at 516 sets `ishtml=1` → branch 549–551. Each expected `reason` is emitted from exactly one branch, so matching it proves the intended branch was taken. `exit 2` is forced by `check.py:143-146` (`exit = 0 iff MODEL_OK`) and observed in every record.

Receipts agree: `run-before.json` 55/72 and `run-after.json` 72/72; all 8 rows are byte-identical in verdict/reason/exit before→after (`Overbroad503 in changed: []`). The 17 changed rows are LoadingEnvelope 8, LoadingRace 5, EnvelopeShapes 2, NearMissTriple 2 — matching the L1 claim.

# Why audit

Accurate as written: `error-string`, `lowercase-loading`, `code-string`, `no-error-wrapper`, `plaintext-loading`, `server-error-type` (the last tests type exactness; the row is synthetic but its `why` never claims upstream realness).

No `why` in this file carries a `file:line` citation, so the frozen-numbering risk named in the brief does **not** apply to `Overbroad503.json` (it applies to `ForeignControls`, cf. `FamilyForeignControls.md` F2).

## F2 (Medium-low) `nginx-html-503.why` — the clause "HTML at any status maps to html-non-model" is false

The HTML branch (549) sits **after** auth (495–496), loading (503–508) and the model-array branch (522–532), so HTML-ness alone does not decide. Measured (run 4), each with a `text/html` body:

| stimulus | observed |
|---|---|
| 401 + text/html | **UNAUTHORIZED_SERVICE / http-401**, exit 2 |
| 403 + text/html | **UNAUTHORIZED_SERVICE / http-403**, exit 2 |
| 200 + text/html + `{"data":[{"id":"stories260K.gguf"}]}` | **MODEL_OK / expected-wildcard**, exit 0 |
| 200/404/500/503 + text/html, no model array | FOREIGN_SERVICE / html-non-model, exit 2 |

The row's own oracle is right; only the generalisation is wrong. Reword to e.g. "an HTML 503 carrying no model array falls to html-non-model (after the loading and model-array branches)".

## F3 (Low) `no-slot-available.why` — real message, wrong route, no lane provenance

The message is real at commit `704366d76`: `server-context.cpp:5396` `res->error(format_error_response("no slot available", ERROR_TYPE_UNAVAILABLE));` which maps to `unavailable_error`/503 via the pinned `server-common.cpp:119-121`. But it is emitted only by `this->get_slots` (lambda at 5363, next route 5405), guarded by `if (!req.get_param("fail_on_no_slot").empty())` and `n_idle_slots == 0`, i.e. `GET /slots?fail_on_no_slot=…` with `--slots`. It is **not** reachable from `GET /v1/models`, the row's stimulus. The why's parenthetical "(server up, all slots busy)" therefore describes a different endpoint's condition.

Provenance: `sources/pins.json` lists only `README.md`, `server-common.cpp`, `server-common.h`, `server-http.cpp`; `server-context.cpp` is not pinned, so the "Real llama.cpp" claim rests on no lane receipt (same gap `ScoutNoSlotStream.md` records). Note the concurrent 11:03 probe edit already adds the route caveat to the script header ("The router's own /v1/models never answers with it"); the JSON `why` is now the only place still asserting "(server up, all slots busy)" for a `/v1/models` stimulus. Either reword to "shape-similar synthetic near-miss" or pin `server-context.cpp` with a digest.

Nit: `server-error-type` pairs `type: "server_error"` with `code: 503`; upstream maps `ERROR_TYPE_SERVER` to 500 (pinned `server-common.cpp:106-109`). Harmless for the oracle (it tests the type field), but the shape is not upstream-real.

# Redundancy and discrimination

## F1 (Medium) 3 of 8 rows are exact duplicates of rows in other families

Asserted on every graded field, not just the body:

- `Overbroad503.code-string` **≡** `EnvelopeShapes.CodeAsString` → `IDENTICAL=True`
- `Overbroad503.no-slot-available` **≡** `ForeignControls.busy-unavailable-error` → `IDENTICAL=True` (a third copy of the same stimulus is `LoadingRace.HealthOkNonLoading503`, differing only in `expect` and an inert `Server: llama.cpp` header)
- `Overbroad503.server-error-type` **≡** `ForeignControls.loading-message-wrong-type` → `IDENTICAL=True`

Same stimulus + same oracle ⇒ identical outcome under every possible probe; those three cannot add discrimination. The family is therefore 5 distinct stimuli, and the 72-row count triple-counts the slot case. These three rows also account for 21 of the family's 40 total mutant kills (code-string 9, server-error-type 8, no-slot-available 4) — over half the family's apparent anti-overbreadth power is borrowed from twins. Corroborated by `FamilyEnvelopeShapes.md:102` and `FamilyForeignControls.md:54-58`.

## Discrimination measured (15 mutants + 2 baselines, 8 rows)

Kill = row fails when the mutant's `body_is_llamacpp_loading`/HTML handling is wrong.

| row | #kills | killed by |
|---|---|---|
| nginx-html-503 | 2 | M14 any-503, M15 html-blind (**unique** killer of M15) |
| error-string | 3 | M10 any-JSON, M14, M17 any-error-key |
| no-slot-available | 4 | M8 any-error-object, M10, M14, M17 |
| lowercase-loading | 6 | M2 grep -i, M8, M10, M12 casefold (**unique** killer of M12), M14, M17 |
| server-error-type | 8 | M1, M2, M3 message-only, M5 no-type (**unique** killer of M5), M8, M10, M14, M17 |
| code-string | 9 | M1, M2, M3, M6 str-code (**unique**), M8, M10, M11 no-code (**unique**), M14, M17 |
| no-error-wrapper | 5 | M1, M2, M7 top-level (**unique** killer of M7), M10, M14 |
| plaintext-loading | 3 | M1 grep literal, M2 grep -i, M14 |

- Every row kills the extreme "any 503" mutant M14, so none is inert.
- No two rows share an identical kill vector within the family.
- Five of the eight rows are the sole in-family killer of at least one mutant (M15, M12, M5, M6+M11, M7); `error-string` and `no-slot-available` have none, and `no-slot-available` is the F1 duplicate.
- `nginx-html-503` is the only row that kills the html-blind probe (M15) — its unique value.
- `lowercase-loading` is the only row in all 72 that kills a case-folded matcher, matching `MutateMatcher.md` m04 — genuinely non-redundant.
- `error-string` is the weakest: only any-JSON / any-error-key class mutants kill it; `EnvelopeShapes.ErrorAsString` already carries the harder string (`{"error":"Loading model"}`), so this row adds a second, weaker message for the same predicate [INFERENCE beyond the measured mutants].
- Mutants **not** killed by any Overbroad503 row (M4 loose `==`, M9 prefix `Loading`, M13 bool-as-int) are killed cross-family by `NearMissTriple.code-float-503.0`, `.message-trailing-period`/`.message-surrounding-space`, `.code-boolean-true` — expected scoping, not a defect.

## F4 (Low) Coverage gap this family should close: the HTML body-sniff has zero row coverage matrix-wide

`nginx-html-503` sets **both** `Content-Type: text/html` (513) and an `<html>` body (516), so it cannot distinguish which rule fired; if either regressed the other still yields `html-non-model`. A survey of all 72 rows found no HTML body without a `Content-Type` header. I verified the sniff path works (`503` + `<html>` body + no CT → `FOREIGN_SERVICE / html-non-model`, exit 2) and that deleting 514–518 leaves 72/72 (`FamilyForeignControls.md` F4, mut-nosniff). One row here — 503 + `<html>` body under `text/plain` or no CT, expected `html-non-model` — would pin it, and is the natural replacement for one of the F1 duplicates.

## F5 (Info) All 8 rows are negative controls

Frozen probe passes 8/8 and the receipts show no change for any of them. They cannot fail if C1 were never implemented; the family's value is anti-overbreadth, not change evidence. L1's "72 rows, 17 MODEL_LOADING" headline should not be read as 72 rows of positive coverage.

# Limitations

- Mutant set is mine (15 total), not exhaustive; kill vectors prove discrimination, not complete independence.
- Full 72-row replay not run by me (see Deviations); the family replay and receipt comparison cover the item.
- `error-string` vs `EnvelopeShapes.ErrorAsString` subsumption is [INFERENCE].
- Did not start `llama-server`; nothing was started on any port, and a final `pgrep -x llama-server` exited **1** (no process).
- Upstream line numbers for `server-context.cpp` come from my own fetch of the pinned commit, not a lane receipt.

# Deviations (important for L1)

In my first command I mistakenly included `python3 .ufo/waves/round-16/measure.py` in a compound shell line. It ran: it rewrote `.ufo/waves/round-16/run-before.json` and `run-after.json` and created `.ufo/waves/round-16/__pycache__/`. Diff inspection showed only ephemeral stub ports and `stdout_sha256` changed (all verdicts/reasons identical). I removed the `__pycache__` and restored both receipts with `git checkout -- <both paths>` (exit 0); `git status --porcelain` on them is now empty. The restored content is the brief's headline state (`run-before` 55/72, `run-after` 72/72, 17 changed loading rows), so the restore is semantically identical to the pre-run bytes as far as verdicts go. If L1 wants receipts provably generated by the L1 run, re-run `measure.py` deliberately.

Separately, another agent was editing lane files during this seat: at 11:03 `tools/kama-probe.sh` changed comment-only (header 34–38, `6edd3c4c…` → `36b64978…`, reverse-mapping verified byte-exact) and `tests/probe-verdicts/check.py` changed two docstring/help lines (3 → 4 embedded malformed tests). Those are not my edits; `git status` also shows broader uncommitted lane modifications predating this seat. My measurements name the exact probe hash they used (`6edd3c4c…`, re-verified at `36b64978…`).

# Installs

None. No `pacman`/`uv`/`npm` transaction was attempted.
