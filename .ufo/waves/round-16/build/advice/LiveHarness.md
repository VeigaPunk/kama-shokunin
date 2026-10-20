# LiveHarness — kama-llamacpp-live.py (C2 operability / capability acquisition)

## Files written
- `tools/kama-llamacpp-live.py` (stdlib only, executable, `py_compile` clean)
- `.ufo/waves/round-16/build/advice/LiveHarness.md` (this report)

No other lane files touched. No installs or upgrades performed.

## What it does
1. Resolves `--server` (default `shutil.which('llama-server')`); records realpath + sha256 + `install_tree` ({basename: sha256} over regular files only, symlinks excluded) + `install_tree_sha256` (sha256 of sorted "name sha" lines) + `server_impl_sha256` (libllama-server-impl.so when present). `--model`/`--model-sha256` verified pre-launch (mismatch → exit 3). Probe identity `probe: {path, sha256}`. Registry TSV unreadable → setup_error exit 2 (fail closed, R6).
2. Port selection: `bind(127.0.0.1:0)` refused-and-retried against `port_refusal_set` = {8080, 34113} ∪ every host:port/`--port N`/`port=N`/`host:N` token in `registry/endpoint-consumers.tsv`; optional `--port N` runs the same gate plus a connect-probe (in-use → exit 2). Port 0 is never passed to llama-server.
3. Launch: `[server, -m, model, --alias, alias, --host, 127.0.0.1, --port, P, -c, ctx, -t, threads, --no-webui, --offline]`, `start_new_session`, stdin DEVNULL, stdout+stderr to temp log, `env` = allowlist {PATH, HOME, LANG, LC_ALL, TMPDIR} (names recorded as `child_env_keys`, values never). PR_SET_PDEATHSIG via preexec_fn; result byte reported back through a `pass_fds` pipe → `pdeathsig: {requested: true, prctl_ok: true|false|'unknown'}` (R11, honest EOF→unknown).
4. Readiness loop from t=0 alternates `/health` + `/v1/models` (urllib, 0.5 s, proxy-free, bodies capped at 65536 bytes with `body_read_truncated` flag — R3). Transitions record t_ms, path, status/error class, body sha256, verbatim body ≤4096 (`body_over_cap`), Server/Content-Type, folded `repeats`. First 503 kept verbatim as `loading_503`; `loading_envelope_exact` = true only for the exact b11755 envelope (message=="Loading model" ∧ type=="unavailable_error" ∧ int code==503), null when no 503, not a check.
5. R1 liveness gate `verify_live(proc, port, label)`: child must be running (`poll() is None`) AND provably own the LISTEN socket (`/proc/net/tcp{,6}` inode ∈ `/proc/<pid>/fd`); ownership None counts as failure (`port-listener-ownership-unproven`), False as `port-listener-not-our-child`. Applied at readiness, immediately before `ready_captures`, before EACH probe (`pre-probe-1`, `pre-probe-2`), and once after the probes (`post-probes`); any failure → setup_error, exit 2. Last observed ownership recorded as `port_listener_ownership` ('child'|'foreign'|'unproven').
6. Ready captures: `/health`, `/v1/models` (body+headers, ≤64 KiB), `/props` (5 specified fields), `/slots` (status+element_count), `/metrics` (status).
7. Probes: `bash PROBE check --port P --expect E --json --timeout 2 --connect-timeout 1`, subprocess timeout 60 s, run under the same allowlisted env (R5).
8. Teardown (R2: SIGINT/SIGTERM/SIGHUP set to SIG_IGN first, handlers restored only after teardown + model rehash): SIGTERM process group → 10 s → SIGKILL; proves returncode + port refusal; reduces only the last 64 KiB of the temp log (`log_tail_truncated`) to `build|model loaded|listening|loading` lines then deletes it; `model_sha256_post` rehash → check `model_unchanged`.
9. Receipt `kama-llamacpp-live/v1` written atomically (sibling tempfile + `os.replace`) or to stdout.

Exit: 0 all checks | 1 any check fails | 2 setup error | 3 digest mismatch.

## Checks array (10)
`health_ready`, `models_alias_id`, `models_owned_by_llamacpp`, `metrics_not_enabled` (exactly 501), `props_alias`, `probe_model_ok` (MODEL_OK/matched/exit 0), `probe_mismatch` (MODEL_MISMATCH/served-id-mismatch/exit 2), `teardown_exited`, `teardown_port_closed`, `model_unchanged`.

## Receipt top-level keys
`schema`, `started_utc`, `ended_utc`, `server`{arg,realpath,sha256,install_tree,install_tree_sha256,server_impl_sha256}, `model`{path,sha256}, `model_sha256_post`, `probe`{path,sha256}, `alias`, `ctx`, `threads`, `port`, `port_refusal_set`, `child_env_keys`, `argv`, `transitions`, `loading_503`, `loading_observed`, `loading_envelope_exact`, `captures`, `probes`, `teardown`, `checks`, `setup_error`, `port_pick_note`, `port_listener_ownership`, `pdeathsig`{requested,prctl_ok}.

## Dev-run evidence (development only — NOT a measurement)
- Pre-hardening run (batch-1 code): exit 0, all 9 checks passed, port 44385, teardown proven via `ss -ltn`. Batches 1+2 applied since; live tool NOT re-run per L1 instruction. `py_compile` clean; `--offline` verified in b11755 `llama-server --help` (line 215); b11755 `llama-server --version` → build 11755, commit 704366d76.
- Wrong `--model-sha256` → exit 3 pre-launch; `--port 8080`/`34113` → `port-refused-registered:*` exit 2; `--port 631` → `port-in-use:631` exit 2.
- `loading_observed` false in dev (stories260K loads ~20 ms); loading-503 verbatim + envelope paths unexercised at this model size.

## Peer input incorporated
- ScoutPortPolicy: `--port` override through the same gate; never `--port 0` downstream.
- ReviewHarnessDesignRisk batch 1: listener-ownership proof, PR_SET_PDEATHSIG.
- ReviewHarnessDesignRisk batch 2 (via L1): R1 ownership-None = setup error + four liveness gates; R2 signals ignored during teardown; R3 64 KiB body/log caps; R5 probe `--timeout 2 --connect-timeout 1` + allowlist env + 60 s cap; R6 registry fail-closed; R11 measured `prctl_ok` via pipe; atomic receipt write.

## Known limitations
- bind(:0) release→rebind collision window remains; ownership proof converts a lost race into clean exit 2.
- Ownership proof is Linux `/proc`-only; an unreadable `/proc` now fails closed (`unproven` → setup error) rather than degrading.
- `loading_503` unexercised in dev; `stderr_tail` on probe records is capped at 2000 chars.
