VERDICT: confirm — both C1 invariants hold on all 72 live rows; served_model ungraded + row.get traceback both demonstrated on a scratch copy.

Seat KamaR17.ProbeServedModel-2. Owned file written:
`.ufo/waves/round-17/build/drafts/probe-served-model.md` — full per-row method,
derived rule, line-cited cross-check of `classify()`, and repair formulation.
Lane source files untouched; the nine `tests/probe-verdicts/*.json` are
byte-identical (copied to `/tmp`, never modified).

## Findings

1. **served_model rule (kama-probe.sh:453-570, 335-377, 380-397).**
   `C_SERVED` is set only inside the `2xx && body_has_model_array` branch
   (kama-probe.sh:524-529); every other path leaves the `-` default
   (kama-probe.sh:455). Predicted `served_model` derived solely from each row's
   own stub `/v1/models` route (falling back to `default_route`, per
   check.py:215-221): raw ids via `served_ids()` precedence `data[].id` →
   `models[].id` → `models[].name` → `models[].model` → top-level `id`,
   comma-joined, first non-empty group wins; `-` otherwise. Diff over all 72
   rows vs observed: **0 mismatches** — no row where the probe's served_model
   looks wrong. Non-dash rows: 8 MODEL_OK + 3 MODEL_MISMATCH only; all 17
   MODEL_LOADING and all 5 UNAUTHORIZED rows report `-` (early returns at
   kama-probe.sh:505-510 and 496-503).
   Raw, unnormalised ids are reported (`ReadyControls.served-id-carries-gguf-suffix`
   → `kama-ready.gguf`); normalisation is comparison-only
   (kama-probe.sh:380-397). `MODEL_MISMATCH`/`unresolvable-id` yields `-`, not
   the expected id — no matrix row covers it today.
2. **Route-match.** All 71 stub-mode rows record `GET /v1/models` as the first
   request (the one closed-port row records none, correctly — nothing
   listened). Follow-ons match classify() evidence fetches: `/`+`/metrics` for
   FOREIGN, `/health` for LOADING/2xx-model rows, `/` for UNAUTHORIZED.
3. **Current check.py gaps (live-demonstrated, scratch copy + wrapper probes
   in /tmp):**
   - `row.get` at check.py:337-338 sits outside the guarded parse
     (check.py:330-332); `{"rows":[5]}` → uncaught
     `AttributeError: 'int' object has no attribute 'get'` at check.py:338 —
     traceback, remaining tests lost. Only OSError/HarnessError are caught
     (check.py:349, 479).
   - A probe fetching only `/health` and emitting a fabricated
     `served_model:"FABRICATED-NOT-SERVED"` with `MODEL_OK` passes the row
     (`passed: true`, `requests:[GET /health]`) — served_model and route-match
     are recorded but never graded (grading is check.py:340-347 only;
     requests only non-emptiness-checked at 323-328).
4. **Repair formulation** (detail in draft): served_model invariant = pure
   function of the row's own stub routes → predicted raw-id string (or `-`);
   route-match invariant = `GET /v1/models` membership in `requests` for
   stub-mode rows; malformed output must wrap `row.get`/row typing inside the
   recorded-failure guard.

## Limitations

- Run used the real probe with python3 present (`HAVE_PY=1`); grep-fallback
  extraction (kama-probe.sh:371-376) unexercised — [INFERENCE] its output can
  differ on exotic bodies, but a stub-route-derived invariant is
  probe-version independent by construction.
- `served_model` string equality assumes contract v2 order/dedup; strict
  compare is intentional (kama-probe.sh:43-48 documents the semantics).
- Scratch harness note: writing any `*.json` into a copy of
  `tests/probe-verdicts/` breaks `load_matrix` (it globs the dir); output
  must be redirected outside.

## Files written (sha256)

- `.ufo/waves/round-17/build/drafts/probe-served-model.md`
  `8388157f794935929366d169b207e67f47e4cd53ceab14a6e64e5ae146e94030`
- `.ufo/waves/round-17/build/advice/ProbeServedModel.md` (this file;
  final sha256 reported in the handoff message since self-reference shifts it)

Scratch `/tmp/ProbeServedModel-{a,b}` removed before finish. No installs; no
lane gates run; no forbidden ports bound (verified `ss -ltn`).
