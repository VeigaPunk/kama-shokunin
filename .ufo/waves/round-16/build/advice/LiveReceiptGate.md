# LiveReceiptGate — round-16 build advice (v3, falsify bindings applied)

## Files changed
- `tests/llamacpp-live/check-receipt.py` (executable, stdlib only). Rebound to producer @ 10:50 (-03), 37901 bytes.

## Binding source + falsify-wave deltas applied
`tools/kama-llamacpp-live.py`: `port_listener_ownership` vocabulary is `child|foreign|unproven` (lines ~850, verify_live ~453-461); `pdeathsig` is `{requested, prctl_ok}`; probes run as `bash PROBE check --port P --expect E --json --timeout 2 --connect-timeout 1` under child_env (run_probe ~533-542); `install_tree_sha256` = sha256 over sorted `name sha\n` lines (install_tree ~144-168); models checks use `e.get()` predicates that admit None entries.

New rules bound (L1 falsify list):
- `port_listener_ownership` must be exactly `child` for VALID (foreign/unproven rejected; `unknown` not in vocabulary).
- argv: argv[0] == server.realpath; `-m` == model.path; `--alias` == alias; `--host` == 127.0.0.1; `--port` == port; `-c` == ctx; `-t` == threads; tail == [`--no-webui`, `--offline`].
- probes[].argv: must contain `check`, `--port <port>` equal to served port, `--expect` equal to the record's expect. `result.rows[0].declared` must equal `http://127.0.0.1:<port>/v1` — null or any other value rejected.
- Loading: `loading_observed` == (`loading_503` is not null) == (any transition with status 503); a stored loading_503 must have status 503 and path ∈ {/v1/models, /health}; `loading_envelope_exact` (bool|null field, not a check) re-derived per producer rule (message "Loading model", type "unavailable_error", int code 503; null iff no 503 row).
- `server.install_tree_sha256` recomputed over `install_tree` (sorted `name sha\n` lines); `install_tree[basename(server.realpath)]` == `server.sha256`.
- models_alias_id / models_owned_by_llamacpp keep `e.get()` results verbatim (None entries fail the all() predicates — fail closed, matching the producer).
- Optional `tool{path, sha256}` block + `--expect-tool-sha256`; flag given with absent block is a problem.

## Carried from v2 (unchanged)
Schema id, setup_error null, started_utc/ended_utc ordered, port int ∉ hard pins and ∉ port_refusal_set (sorted, deduped, must contain 8080+34113), digest 64-hex checks for server/model/probe (+expect equality), child_env_keys sorted-subset-of-allowlist, captures re-derivation (health 200, data[] ids all == alias, owned_by all llamacpp, metrics status exactly 501, props.fields.model_alias == alias), probe verdict/reason/exit contract (MODEL_OK⇒0/matched, MODEL_MISMATCH⇒2/served-id-mismatch, drift flags, summary.exit==exit), teardown returncode/port_refuses evidence, all 10 check ids once each with strict passed/documented_by/observed, observed-vs-raw agreement, model_unchanged == (model.sha256 == model_sha256_post).

## Selftest
Observed: `selftest: 26 mutations + unreadable case all rejected; valid receipt accepted`.
New mutations added for the falsify survivors: ownership-unproven, argv0-not-realpath, argv-wrong-host, probe-argv-missing-check, probe-declared-null, loading-observed-without-503-transition, loading-503-wrong-path, install-tree-sha-tampered, models-entry-missing-id, tool-sha-mismatch-expect — plus the carried set (schema, missing model_unchanged, duplicate id, port pins/refusal set, digest mismatches, missing teardown, MODEL_OK-with-exit-2, stored-probe-vs-check contradiction, metrics 200, ended<started, mismatch-expects-alias, envelope flag, off-allowlist env key, missing --offline).

## Checks run on own file
`python3 -m py_compile`, `--selftest` — pass. No lane measurements (L1 owns those).

## Known limitations
- Pure consistency audit of stored evidence; never opens sockets or re-runs the probe.
- `tool` absent is valid until LiveHarness lands it; supplying `--expect-tool-sha256` against an absent block fails.
- setup_error non-null → INVALID (gate is for complete valid runs).

## Installs
None.
