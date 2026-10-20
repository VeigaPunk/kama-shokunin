VERDICT: partial — all 8 ForeignControls oracles are literally right on the landed `classify()` and on the frozen probe (8/8, 8/8), but every inline line citation is frozen-numbered, two rows are byte-identical duplicates of `Overbroad503` rows, and one row's `why` claims a C1 test the row does not perform.

# What I ran

| # | command | exit | result |
|---|---|---|---|
| 1 | `python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --only <8 names> --json` | **0** | passes 8, failures 0; `probe_exit` = [2,2,2,2,2,2,2,2] |
| 2 | same, `--probe .ufo/waves/round-16/frozen/kama-probe-before.sh` | **0** | passes 8, failures 0 (separability control holds) |
| 3 | `check.py --probe /tmp/…/mut-nosniff.sh --json` (HTML body-sniff, current 514–518, removed) | 0 | **72/72 pass** |
| 4 | `check.py --probe /tmp/…/mut-msgonly.sh --json` (gate → `message` only) | [INFERENCE: 1] | 65 pass / **7 fail** |
| 5 | `check.py --probe /tmp/…/mut-nocode.sh --json` (drop `code` check) | [INFERENCE: 1] | 67 pass / **5 fail** |
| 6 | `check.py --probe /tmp/…/mut-any5xx.sh --json` (gate accepts any 5xx) | [INFERENCE: 1] | 69 pass / **3 fail** |
| 7 | `check.py --probe /tmp/…/mut-keypresence.sh --json` (`key in doc` vs `isinstance(list)`) | **1** | 71 pass / **1 fail** |

Mutants are `/tmp` copies of the current probe; no lane file was edited. Runs 4–6 were launched detached after an eval-kernel timeout, so only their JSON was captured — `check.py:493` sets `code = 0 if doc["failures"] == 0 else 1`, and run 7 (1 failure → exit 1) plus runs 1–3 (0 failures → exit 0) confirm that mapping.

Provenance of the control run: current probe sha256 `6edd3c4c…`, frozen sha256 `93ee4302…` — byte-equal to `.ufo/waves/round-16/frozen/manifest.json` `"sha256"`. So run 2 exercised the pinned artifact, not a drifting copy. Lane HEAD `b8e485c`.

# F1 — the literal oracles are correct (no refutation)

| row | expected | observed (runs 1 and 2) |
|---|---|---|
| html-index | FOREIGN_SERVICE / html-non-model / 2 | same |
| openmetrics-text | FOREIGN_SERVICE / non-model-2xx / 2 | same |
| json-no-model-array | FOREIGN_SERVICE / schema-unrecognized / 2 | same |
| json-data-object-not-array | FOREIGN_SERVICE / schema-unrecognized / 2 | same |
| not-found-json | FOREIGN_SERVICE / non-2xx-non-model-http / 2 | same |
| server-error-json | FOREIGN_SERVICE / non-2xx-non-model-http / 2 | same |
| busy-unavailable-error | FOREIGN_SERVICE / non-2xx-non-model-http / 2 | same |
| loading-message-wrong-type | FOREIGN_SERVICE / non-2xx-non-model-http / 2 | same |

Each reason string is emitted from exactly one branch (`html-non-model` 551, `schema-unrecognized` 559, `non-model-2xx` 560, `non-2xx-non-model-http` 564, `llamacpp-loading` 505), so matching `reason` proves the intended branch was taken rather than a coincidentally equal verdict. The CT split is exercised both ways: `application/json` → 559, `application/openmetrics-text…` → 560 (the `*json*` case test is a substring match, and that CT contains none). `exit 2` is correct for every row: `check.py:143-146` enforces exit = 0 iff `MODEL_OK`, and `probe_exit` was 2 in all 16 runs.

# F2 — every citation is frozen-numbered while naming `tools/kama-probe.sh` (should fix)

The five citations are exact against the **frozen** file and wrong against the file they name. Two distinct offsets, because the C1 insertion sits between the helper and `classify()`:

| row | citation | frozen lines it matches (correct there) | current lines it should cite | shift |
|---|---|---|---|---|
| html-index | `kama-probe.sh:506-511` | 506-511 = HTML branch | **549-554** | +43 |
| openmetrics-text | `kama-probe.sh:514-519` | 514-519 = `is2` CT split | **557-562** | +43 |
| json-no-model-array | `392-411` and `reason at 516` | 392-414 = `body_has_model_array`; 516 = `schema-unrecognized` | **399-422** and **559** | +7 / +43 |
| json-data-object-not-array | `kama-probe.sh:403-405` | 403-405 = `for key` / `isinstance` / `exit 0` | **410-412** | +7 |
| not-found-json | `kama-probe.sh:520-522` | 520-522 = `else` / reason / evidence | **563-565** | +43 |

All five land on real code in the current file, which is what makes them dangerous. Example: a reader chasing `514-519` for `non-model-2xx` lands on the HTML sniff instead — `tools/kama-probe.sh:514` `if [ "$ishtml" -eq 0 ] && [ -s "$FBODY" ]; then`, and on `tools/kama-probe.sh:516` `'<html'*|'<!doctype'*'html'*) ishtml=1 ;;`. Chasing `506-511` lands on the MODEL_LOADING evidence/return and `local is2=0 ishtml=0 has_models=0`, not on the HTML branch. For `non-model-2xx` the cited frozen range starts at `C_VERDICT=FOREIGN_SERVICE` (frozen 514); the reason token itself is frozen 517.

Fix: renumber to the current ranges above, or (if the intent was to cite the baseline) write the frozen path `.ufo/waves/round-16/frozen/kama-probe-before.sh` instead of `kama-probe.sh`. Nothing documents a frozen-numbering convention — `grep -rn 'frozen\|before.sh' tests/probe-verdicts/` returns nothing.

# F3 — two rows are byte-identical duplicates of `Overbroad503` rows (should fix)

Asserted on all graded fields (`port_mode`, `routes`, `default_route`, `expect`, `expected`):

- `ForeignControls.busy-unavailable-error` **≡** `Overbroad503.no-slot-available` → `identical graded fields: True`. Same 503, same `application/json`, same `{"error":{"code":503,"message":"no slot available","type":"unavailable_error"}}`. Same stimulus ⇒ same verdict/reason/exit under every possible probe; the row cannot add discrimination. A third copy of the same stimulus is `LoadingRace.HealthOkNonLoading503` (`expected` equal; differs only in the inert `expect` and a `Server: llama.cpp` header).
- `ForeignControls.loading-message-wrong-type` **≡** `Overbroad503.server-error-type` → `identical graded fields: True` (503 / `application/json` / `{"error":{"code":503,"message":"Loading model","type":"server_error"}}`).

So 2 of the 8 rows contribute zero new information to the 72-row count. Both rows are *correct*; they are just not independent. Cheapest fix: drop `busy-unavailable-error` (its twin lives in the family actually named for the over-broad-503 question) and retarget the slot at F4's missing row.

# F4 — `html-index` does not pin the body-sniff rule; the rule has zero coverage matrix-wide (coverage gap)

`mut-nosniff` — deleting current lines 514–518 entirely — gives **72/72 pass**. No row anywhere fails when the sniff is removed, because both HTML rows (`html-index`, `Overbroad503.nginx-html-503`) carry `Content-Type: text/html`, so `case "$F_CT" in *html*)` (current 513) fires first and the sniff never decides. `html-index`'s own `why` is honest about this ("ishtml via Content-Type"), so the row is not wrong — but the landed comment at current 512 promises "header, **or a body sniff** (v3 rule 4)", and that half is untested.

Concrete repair: one row with an `<!doctype html>` / `<html` body under `Content-Type: text/plain` (or no Content-Type), expected `FOREIGN_SERVICE` / `html-non-model` / exit 2. I verified this discriminates: under `mut-nosniff` it becomes `non-model-2xx` and fails. This is also the natural replacement for the F3 duplicate.

# F5 — `server-error-json`'s `why` overstates what the row tests (should fix the prose, not the oracle)

The `why` says "C1 may only match message+type+code exactly". The row cannot show that: all three fields already differ (`message: "Internal server error"`, `type: "server_error"`, `code: 500`), and the status alone (500) short-circuits the gate at current 503 (`if [ "$F_CODE" = "503" ]`) before the body is read. Empirically, `mut-any5xx` (gate accepts any 5xx) produces 3 failures — all `NonLoadingStatuses.err500/err502/err504-envelope` — and **zero** ForeignControls failures. So `server-error-json` passes under the very over-broadening its `why` invokes; the 503-only precondition is pinned entirely by another family.

It remains a valid outcome oracle (a generic 500 with a `server_error` object must not be read as loading), and it is not redundant with `not-found-json` if one cares about a "5xx→DEAD" regression specifically. Reword to "a generic 500 server_error must stay non-2xx-non-model-http" and drop the exactness claim, or move it to `NonLoadingStatuses`.

# F6 — `json-data-object-not-array` is the strongest row in the family (positive)

`mut-keypresence` (replace `isinstance(doc.get(key), list)` with `key in doc`) gives **71 pass / 1 fail**, and the single failure is `ForeignControls.json-data-object-not-array` (`got MODEL_OK/expected-wildcard | want FOREIGN_SERVICE/schema-unrecognized`). It is the **only** row in all 72 that catches a key-presence-instead-of-list-type regression; `json-no-model-array` passes under that mutant because it has no `data`/`models` key at all. The two rows are therefore genuinely distinct, not padding.

# F7 — minor: `not-found-json` is subsumed by `NonLoadingStatuses.err404-envelope` [INFERENCE]

Same 404, same `application/json`, same expected reason; only the body differs (`{"error": "not found"}` vs the exact loading envelope with `code: 404`). `classify()` never inspects the body on the non-2xx path, so no mutation of that path can separate the two; `err404-envelope` is strictly stronger (it additionally proves the envelope alone does not win at 404). Safe to keep as a cheap control, but it adds no discrimination.

# F8 — minor: `expect: "*"` is inert in all 8 rows [INFERENCE from code path]

`classify()` consults `expected` only inside the `is2 && has_models` branch (current 522-543). None of these 8 rows reaches it (`has_models=0` in every one), so tightening `expect` cannot strengthen the family; the graded axes are verdict/reason/exit only. Not a defect, just not a lever.

# Limitations

- This family is one-sided: 8/8 expect `FOREIGN_SERVICE`/exit 2, so a probe hard-wired to answer `FOREIGN_SERVICE` would pass all 8. That is the intended role of controls (the `MODEL_OK` direction is pinned by `ReadyControls`/`LoadingRace`), but the family alone proves nothing about not under-classifying.
- I audited duplicate stimuli across all 72 rows, but did not review the other families' `why` prose.
- Mutant exit codes for runs 4–6 were not captured (detached after an eval timeout); counts come from the emitted JSON and the 0/1 mapping at `check.py:493`.
- I did not run `.ufo/waves/round-16/measure.py` (forbidden) and did not touch any lane, fleet, state, or sibling file.

# Installs

None. No `pacman`, `uv`, `npx`, or binary installs were performed (host pacman pause irrelevant here); no tool versions changed.
