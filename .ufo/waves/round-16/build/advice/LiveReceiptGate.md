# LiveReceiptGate — round-16 build advice (v2, rebound to producer)

## Files changed
- `tests/llamacpp-live/check-receipt.py` (new, executable, stdlib only). Rebound to the producer's exact emitted keys after LiveHarness's hardening batch; the earlier tolerant `_key`/`_walk` alias layer was deleted.

## Binding source
`tools/kama-llamacpp-live.py` @ 10:43 (-03), 33177 bytes: receipt assembly lines 682-718, argv tail `--no-webui --offline` (720-729), `child_env = {k: ... for k in CHILD_ENV_KEYS}` (731), `loading_envelope_exact` bool|null (171-187, 771), `metrics_not_enabled` requires `status == 501` (799-803), probes list `{expect,argv,exit,result,stderr_tail}` with `result.rows[0]` (812-832), teardown `{returncode, port_refuses, ...}` (846-856), `model_sha256_post` + `model_unchanged` check (858-864). Final key list confirmed by LiveHarness message.

## Validated (exit 0 valid / 1 invalid list-all / 2 unreadable)
- `schema` == `kama-llamacpp-live/v1`; `setup_error` must be null for a valid receipt.
- `started_utc`/`ended_utc` parse; ended >= started.
- `port` int 1-65535, not 8080/34113, and not inside the receipt's own `port_refusal_set` (which must be a sorted, duplicate-free non-empty int list containing both hard pins).
- `server{arg,realpath,sha256}`; `server.install_tree` is `basename->sha256`, must contain the realpath basename whose digest equals `server.sha256`; `server.install_tree_sha256` and `server.server_impl_sha256` are 64-hex or null.
- `model{path,sha256}`, `model_sha256_post` (64-hex, null, or `rehash-error:*`), `probe{path,sha256}`; `--expect-{model,server,probe}-sha256` equality when supplied; malformed `--expect-*` is itself a problem (exit 1).
- `child_env_keys`: sorted unique list, bare names only (no `=`), all within allowlist PATH/HOME/LANG/LC_ALL/TMPDIR.
- `argv`: `--alias` == receipt alias, `--port` == receipt port, `--host`/`-c`/`-t` present, tail == `[--no-webui, --offline]`.
- `loading_observed` bool and consistent with `loading_503` null-ness; `loading_envelope_exact` (field, not a check) re-derived from the stored `loading_503.body` using the producer's rule (message=="Loading model", type=="unavailable_error", code int 503; null when no 503 seen).
- `port_listener_ownership` in child|foreign|unknown; 'foreign' is a problem.
- Captures: `health.status`==200; `models.body` re-parsed — every `data[].id` == alias and every `owned_by` == "llamacpp"; `metrics.status`==501 exactly; `props.fields.model_alias` == alias.
- Probes: exactly 2 records, expects must be {alias, `kama-not-this-model`}; each `result.schema`=="kama-probe/v1", `summary.exit`==recorded `exit`, rows[0] `drift`/`reason`/`expected_model_id`/`declared` consistent; verdict↔exit contract enforced (MODEL_OK⇒0, else⇒2).
- Teardown dict present; `returncode` int|null, `port_refuses` bool|null.
- All 10 required check ids present exactly once (extras flagged), `passed` strict bool true, `documented_by` non-empty, `observed` an object; each check's `observed` snapshot must agree with the re-derived raw evidence.
- `model_unchanged` re-derived: `model.sha256` == `model_sha256_post` (plus observed.pre/post agreement when hexes recorded).

## Selftest
16 mutations + unreadable case, all rejected; valid literal (built in the producer's exact emitted shape) accepted. Observed: `selftest: 16 mutations + unreadable case all rejected; valid receipt accepted`. Mutations cover: schema, missing `model_unchanged`, duplicated id, port 34113, port inside refusal set, wrong digest vs `--expect`, post-digest change, missing teardown, MODEL_OK-with-exit-2, stored-probe-vs-check contradiction, metrics 200, ended<started, mismatch-probe-expects-alias, envelope flag inconsistency, off-allowlist env key, missing `--offline`.

## Checks run on own file
`python3 -m py_compile`, `--selftest` — pass. No lane measurements (L1 owns those).

## Known limitations
- No live verification: the validator never opens sockets or re-runs the probe; it audits internal consistency of stored evidence.
- A setup-error receipt (setup_error non-null) is reported INVALID rather than "valid-but-failed" — deliberate: L1 asked for a valid-run gate.
- `install_tree_sha256`/`server_impl_sha256` allow null per the producer (dir listing / missing impl .so).

## Installs
None.
