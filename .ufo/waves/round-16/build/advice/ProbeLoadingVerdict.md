# ProbeLoadingVerdict — C1 MODEL_LOADING implementation advice

## Files changed

- `tools/kama-probe.sh` (only file touched). `bash -n` passes. Diff vs frozen
  baseline `.ufo/waves/round-16/frozen/kama-probe-before.sh`: +50/-8 lines, every
  change scoped to C1.

## What was implemented

1. **Vocabulary** — `MODEL_LOADING` appended (last position, byte-append, no
   reordering) at:
   - header vocabulary comment `tools/kama-probe.sh:29-34` — includes the required
     one-line citation of llama.cpp b11755 `tools/server/server-http.cpp:307-325`
     plus a two-line envelope description;
   - `VOCAB` `tools/kama-probe.sh:60`;
   - `usage()` verdict line `tools/kama-probe.sh:115`.

2. **Exact-envelope helper** — `body_is_llamacpp_loading()` at
   `tools/kama-probe.sh:418-445` (placed after `body_has_model_array`, before the
   classify banner, matching the file's helper-then-consumer layout). Follows the
   existing HAVE_PY/python3 heredoc pattern. Returns 0 iff the body parses to a
   JSON object whose `error` is an object with `message == "Loading model"`,
   `type == "unavailable_error"`, and `code` an integer equal to 503
   (`isinstance(code, bool)` is rejected explicitly; floats like `503.0` and
   strings like `"503"` also fail — exact as specified). With python3 absent it
   returns 1 unconditionally — fail closed to the old path; no grep approximation,
   since grep cannot prove the exact envelope.

3. **classify() branch** — `tools/kama-probe.sh:501-506`, inserted after the
   401/403 early-return `fi` and before the `is2/ishtml/has_models` prelude that
   feeds the HTML/FOREIGN_SERVICE fallbacks:
   ```bash
   if [ "$F_CODE" = "503" ] && [ -s "$FBODY" ] && body_is_llamacpp_loading "$FBODY"; then
     C_VERDICT=MODEL_LOADING
     C_REASON=llamacpp-loading
     C_EVIDENCE="$base (llama.cpp loading envelope: not ready, not a foreign service); GET /health -> $(probe_short "$port" "/health")"
     return 0
   fi
   ```
   Verbatim per the assignment, including evidence string and the `/health`
   probe_short (during load llama.cpp answers `/health` with the same 503
   envelope, so the recorded `503|application/json` is honest evidence).

4. **diff_baseline whitelist** — `*\ MODEL_LOADING\ *` appended to the verdict
   case at `tools/kama-probe.sh:937`, so a persisted MODEL_LOADING baseline row is
   trusted, not dropped as malformed.

5. **cmd_listeners counters** — new `n_loading` counter, `MODEL_LOADING) n_loading…`
   case arm, and a new `model_loading` key appended to both summary lines
   (`tools/kama-probe.sh:721,731,741-742,746-747`). Every existing summary key is
   unchanged; the new key is last, so key order for the original six is preserved.

## Design choices

- `MODEL_LOADING` appended (not grouped beside MODEL_OK) everywhere so all
  pre-existing lines change by append-only edits; no reordered bytes.
- MODEL_LOADING is counted separately (`n_loading`), not folded into
  `model_endpoints` — a loading server is not yet a model endpoint and the spec
  permitted either; a separate counter keeps `model_endpoints` semantically
  identical to before while still surfacing the count.
- No other verdict/reason touched: `"no slot available"` unavailable_error,
  non-JSON 503s, 503 with string/float code, and any non-503 status all still fall
  through to `FOREIGN_SERVICE non-2xx-non-model-http` (or the schema/HTML paths),
  exactly as before.
- Drift semantics are automatic: `eval_rows` marks drift iff verdict != MODEL_OK,
  so MODEL_LOADING yields `drift: true` and `check` exit 2 — matching the claim.

## Known limitations

- The gate requires python3 (`HAVE_PY=1`). Without it a loading llama.cpp keeps
  the old `FOREIGN_SERVICE non-2xx-non-model-http` verdict — deliberate fail-
  closed behavior, matching the assignment.
- The envelope match is intentionally exact; llama.cpp builds before the
  `unavailable_error` envelope existed, or forks with different wording, are not
  recognized (scope limit per claim).
- Only the `/v1/models` body is inspected for the envelope; `/health` is recorded
  in evidence but not required to match.

## Verification run here

- `bash -n tools/kama-probe.sh` → OK.
- `diff -u .ufo/waves/round-16/frozen/kama-probe-before.sh tools/kama-probe.sh`
  → reviewed in full; only the six C1 hunks above.
- Stub-matrix measurement intentionally not run — reserved for L1.

## Installs

None (no new tools needed; pacman pause observed).
