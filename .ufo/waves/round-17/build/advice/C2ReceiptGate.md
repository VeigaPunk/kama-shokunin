VERDICT: confirm — kama-llamacpp-live/v2 validation landed beside an unchanged v1 path; 2 valid + 38 mutations + unreadable all behave per exit contract.

# Files written

- `tests/llamacpp-live/check-receipt.py` — sha256 `14a0d2853edde490dd4e48669f356c9e6e0520bb7f2e3b1d98c90d2d37b76d3c` (1379 lines). Only file touched.

# What changed

- `RECEIPT_SCHEMA_V2 = "kama-llamacpp-live/v2"`; `validate()` sets `is_v2` from `receipt["schema"]`. Unknown schemas still bad and fall through the v1 derivation path (unchanged pre-existing behavior).
- `REQUIRED_CHECKS_V1` (renamed constant, same tuple, v1 path byte-identical logic) vs `REQUIRED_CHECKS_V2` (11 ids): health_ready, models_alias_id, models_owned_by_llamacpp, metrics_not_enabled, props_alias, probe_model_ok, probe_mismatch, teardown_graceful, teardown_port_closed, loading_envelope_graded, model_unchanged. A v1 check id (`teardown_exited`) inside a v2 receipt is flagged "unexpected check id"; a missing v2 id is "required check absent".
- v2 teardown fields type-checked: `sigterm_sent`, `sigkill_sent`, `alive_at_teardown_start` must be bool.
- New `claim(cid, want)`: v2 only — each check's claimed `passed` must equal the value re-derived from stored evidence, never trusted. Applied to all 11 v2 checks.
- v2 re-derivations:
  - `health_ready`: status 200 AND parsed health body == `{"status":"ok"}` (`HEALTH_READY_DOC`); a 200 `{"status":"degraded"}` or extra key fails.
  - `teardown_graceful`: `alive_at_teardown_start is True` AND `sigterm_sent is True` AND `sigkill_sent is False` AND `returncode == 0`. Round-16 receipt semantics (`returncode 0, sigterm_sent true, term_wait_ms 3`) are the graceful shape; -15/-9/1/None all fail.
  - `teardown_port_closed`: requires `port_listener_ownership == "child"` (recorded child ownership) AND `port_refuses is True`; ownership "unproven"/"foreign" fails even when the port refuses.
  - `loading_envelope_graded`: claimed passed must equal `want_lef is True` where `want_lef` is re-derived from the stored `loading_503` body via `loading_envelope_ok`; unobserved loading (`want_lef None`) or non-exact envelope fails — the check can no longer be silently unconsumed.
  - Shared checks (models_*, metrics, props, probe_*, model_unchanged) keep the v1 evidence bads; v2 additionally claim-compares.
- `--selftest`: v1 matrix untouched (26 mutations) plus a `v2-valid` case and 12 v2 single-field mutations: degraded health body, sigkill_sent true, returncode -15, returncode 1, sigterm_sent false with rc 0, ownership unproven + port_refuses true, loading exact false with observed loading, non-exact 503 while check claims pass, missing loading_envelope_graded, v1 id in v2 receipt, alive_at_teardown_start false, health body extra key.

# Exercised verification

- `python3 -m py_compile` clean.
- `--selftest`: "2 valid receipt(s) accepted; 38 mutations + unreadable case all rejected".
- `.ufo/waves/round-16/live/receipt.json` → VALID; `.ufo/waves/round-16/live/receipt-frozen-probe.json` → VALID (each run individually; CLI takes one positional).
- `--help` works; description now "v1 or /v2".

# Design choices / coordination

- C2LiveTool's `tools/kama-llamacpp-live.py` was still `SCHEMA = 'kama-llamacpp-live/v1'` at edit time — implemented to the contract text. Field names chosen: `teardown.alive_at_teardown_start` (bool) is the one new evidence field name not pinned by the contract; everything else reuses v1 keys. If C2LiveTool picks a different name (e.g. `child_alive_at_teardown`), only the `teardown_graceful` block and the selftest literal need renaming — flagging for L1.
- Body check is parsed-JSON equality against `{"status":"ok"}` (whitespace-tolerant, key-exact), per "health body equals the documented ready body".
- A v2 receipt with an honestly-failed check (passed=false matching bad evidence) is still INVALID — consistent with v1's "all checks passed" gate.
- Unknown-schema receipts run the v1 derivation (pre-existing lenient fallthrough; deliberately unchanged so the v1 path is byte-equivalent).

# Peer advice — deferred to L1

- `KamaR17.ConnectKaidoku-2` proposed a gate-level `source_binding` obligation (span-text/sha grounding against corpus/SOURCES.md rows S036/S037) as a non-check field. NOT implemented here: out of this item's scope — it would add an 12th obligation on a field name the producer does not yet emit, and the contract fixes the v2 id set at 11. Recording verbatim intent for L1: "each sourced predicate carries {row, commit, path, lines, file_sha256, span_text, span_sha256}; fail when span_text is not a contiguous slice of the declared lines, file_sha256 != the row's recorded raw digest, a grounded token is outside span_text, or the row's scope cannot ground the proposition". Today check-receipt.py has zero SOURCES.md references, so mis-citation is invisible to the gate [INFERENCE: matches CriticC2Predicates' remit].

# Limitations

- v2 field naming (`alive_at_teardown_start`) is my contract-text choice; must match C2LiveTool's emitted key.
- No v2 receipts exist yet in the lane to validate end-to-end; only the selftest literal exercises the v2 path.
- No installs performed. No scratch files left.
