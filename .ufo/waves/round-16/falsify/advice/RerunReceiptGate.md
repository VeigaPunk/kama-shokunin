VERDICT: partial — both L1 receipts validate with all three digest pins and the 16-mutation selftest passes, but 3/6 required hand mutations and 23/24 supplemental bypass probes are accepted; the 10 check verdicts are genuinely re-derived, while launch identity (model, bind address, argv[0]), manifest/body digests, and lifecycle transitions are not.

# Attack executed

Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin` at `b8e485c`. Gate: `tests/llamacpp-live/check-receipt.py` (1014 lines). Server pin: `sha256(~/.local/opt/llama-b11755/llama-server)` = `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`. Model pin: `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`.

## Baseline runs (all exit codes observed)

| # | Command | Exit | Output |
|---|---|---|---|
| B1 | `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-16/live/receipt.json --expect-model-sha256 270cba1b…d256d --expect-server-sha256 b6a31a8e…cd804` | **0** | `VALID .ufo/waves/round-16/live/receipt.json` |
| B2 | same on `.ufo/waves/round-16/live/receipt-frozen-probe.json` | **0** | `VALID …receipt-frozen-probe.json` |
| B3 | `python3 tests/llamacpp-live/check-receipt.py --selftest` | **0** | `selftest: 16 mutations + unreadable case all rejected; valid receipt accepted` |
| B4 | B1 + `--expect-probe-sha256 6edd3c4c…fa50` (current probe) | **0** | `VALID` |
| B5 | B2 + `--expect-probe-sha256 93ee4302…2cd64` (frozen probe) | **0** | `VALID` |
| B6 | B2 + `--expect-probe-sha256 6edd3c4c…fa50` (wrong probe, separability control) | **1** | `probe.sha256 93ee4302… != expected 6edd3c4c…` |

So the committed receipts pass even with probe identity pinned; the pin is effective (B6). The selftest count is accurate: 16 `mut()` cases plus the unreadable-file case (`grep -c '    mut('` → 16).

## Out-of-band verification of the committed receipts

The gate never reads disk and never recomputes any digest (`grep hashlib tests/llamacpp-live/check-receipt.py` → no match), so I re-derived the claims myself:

- `receipt.json` and `receipt-frozen-probe.json`: recorded `model.sha256` == actual GGUF digest; `server.sha256` == actual binary digest; `server.install_tree` == the 51 regular files in `~/.local/opt/llama-b11755/` (name-for-name, digest-for-digest); `install_tree_sha256` recomputes to the recorded `6c216313…5a2c`; `server_impl_sha256` == tree entry `libllama-server-impl.so` == actual file; probe sha matches the probe file each receipt names (`6edd3c4c…fa50`, `93ee4302…2cd64`); every stored `body_sha256` (captures, transitions, loading_503) matches its stored body; both probe rows' `declared` equal `http://127.0.0.1:<port>/v1` and both probe `argv` carry the same port.
- `argv[0] == server.realpath`, `argv -m == model.path`, `argv --host == 127.0.0.1`, `-c`/`-t` match `ctx`/`threads`, `port_listener_ownership == "child"`, `pdeathsig.prctl_ok == true` in both receipts.

Conclusion for the **current** files: the evidence is internally and externally consistent; the accepted mutations below are gate-coverage gaps, not defects in the committed receipts.

# Six required hand mutations (only `/tmp` copies)

All ran as `check-receipt.py <mutant> --expect-model-sha256 270cba1b… --expect-server-sha256 b6a31a8e…`. None of these classes is in `_selftest()` (`tests/llamacpp-live/check-receipt.py:901-937`).

| # | Mutation | Exit | Accepted? | Gate message / why |
|---|---|---|---|---|
| P1 | Both probe rows' `declared` set to `null` | **0** | **ACCEPTED** | `declared` is checked only when it is a string (`:476-480`), so a non-string silently drops the endpoint binding |
| P2 | `child_env_keys = ["HOME","LANG","PATH=/home/vgpnk/.ssh/id_ed25519"]` | 1 | rejected | `child_env_keys element 'PATH=…' is not a bare variable name` |
| P3 | `port_refusal_set` += current `port` (sorted) | 1 | rejected | `port 32845 is inside the receipt's own port_refusal_set` |
| P4 | `install_tree` with `"llama-server"` removed (50 entries kept) | 1 | rejected | `server.install_tree does not contain the server basename 'llama-server'` |
| P5 | `argv --host` changed `127.0.0.1` → `0.0.0.0` | **0** | **ACCEPTED** | Only presence of `--host` is checked (`:329-331`), never its value |
| P6 | `argv -m` changed to `/tmp/not-the-model.gguf` (model block untouched) | **0** | **ACCEPTED** | `-m` is never inspected; `model.sha256` is only compared to the CLI pin, never to the spawned argv |

Result: **3 accepted / 3 rejected**. The named examples are mostly rejected in their literal form (P2, P3, P4-as-non-empty); the same intent succeeds through null (P1), value substitution (P5), and an unchecked flag (P6). Adding the current port to `port_refusal_set` is already a selftest case (`:910-911`); removing the server basename is rejected only while the tree is non-empty (see S2/S11).

# Supplemental bypass probes (24; 23 accepted)

S22 was a discarded no-op revalidation of the unmutated base and is excluded.

| # | Mutation | Exit | Note |
|---|---|---|---|
| S1 | Probe `declared` = `http://127.0.0.1:9/v1` (string) | 1 | rejected: endpoint mismatch — proves P1 is a type-guard bypass, not a missing check |
| S2 | `install_tree = {}` | **0** | basename/entry checks skipped by `if tree and …` (`:248`) |
| S3 | `install_tree_sha256 = "0"*64` | **0** | only hex-format checked (`:254-256`); never recomputed |
| S4 | `server_impl_sha256 = "0"*64` | **0** | only hex-format checked (`:257-259`); not bound to tree entry |
| S5 | Matching probe's recorded `argv` `--port` → `9` (row unchanged) | **0** | `probes[].argv` is never read by `validate()` |
| S6 | `transitions = []` | **0** | only `isinstance(list)` (`:370-371`) |
| S7 | `pdeathsig = null` | **0** | field unchecked |
| S8 | `argv -c` → `999`, receipt `ctx` still 256 | **0** | `-c`/`-t` values unchecked (`:329-331`) |
| S9 | `server.arg = "/bin/true"` | **0** | `arg` not bound to `realpath` |
| S10 | Every `checks[].observed = {}` | **0** | optional-key checks skip absent keys |
| S11 | `server.realpath = "llama-server"` (no `/`) | **0** | whole basename block skipped (`:247-253`) |
| S12 | `argv[0] = "/bin/true"` | **0** | `argv[0]` never compared to `server.realpath` |
| S13 | `transitions[1]` rewritten to a 200 empty `/v1/models` row (contradicts captures.models) | **0** | transitions contents unvalidated |
| S13b | `loading_503` 503 envelope + `loading_observed=true`, but matching transitions row rewritten to 200 | **0** | loading record and transitions never cross-checked |
| S14 | `captures.models.body_sha256 = "0"*64` | **0** | body digests never recomputed |
| S15 | `loading_503.body_sha256 = "0"*64` (valid envelope body) | **0** | same |
| S16 | Every `checks[].documented_by = "x"` | **0** | only non-empty string checked (`:514-516`) |
| S17 | `loading_503.status = 200` with a valid envelope body, `loading_observed=true` | **0** | status/path of the loading record unchecked (`:336-360`) |
| S18 | `port_listener_ownership = "unknown"` | **0** | only `"foreign"` is rejected (`:362-368`) |
| S19 | `ended_utc = started_utc` | **0** | `ended < started` is rejected, equality accepted |
| S20 | `port_pick_note` removed | **0** | field optional/unchecked |
| S21 | `loading_503.path = "/health"` (status 503, envelope body) | **0** | path unchecked |
| S23 | `captures.health.body = "not json"`, status 200 | **0** | health body never parsed; documented envelope not enforced |
| S24 | `captures.props.fields["default_generation_settings.n_ctx"] = 999` | **0** | `ctx` not bound to props (only `model_alias` is checked) |

# Findings by severity

## High

1. **The launched model is not bound to the digest-pinned model (P6).** `validate()` checks `argv --alias`, `--port`, presence of `--host/-c/-t`, and the tail, but never `-m` (`tests/llamacpp-live/check-receipt.py:316-334`). `model.sha256` is only compared with `--expect-model-sha256` (`:261-283`). A receipt can pair the pinned GGUF metadata with an argv that loads a different file and still pass all 10 checks, because the checks assert the served alias and HTTP surfaces, not the bytes the server loaded. The actual receipts are consistent (`argv -m == model.path` in both; the producer builds it that way at `tools/kama-llamacpp-live.py:773-782`), but the gate does not enforce it. Fix: require `os.path.realpath(argv_flag(argv, "-m")) == model.path`; optionally hash `model.path` when that file is present, or state in the docstring that only the CLI pin, not the file, is bound.
2. **The bind address is unconstrained (P5).** Only the presence of `--host` is checked (`:329-331`); `0.0.0.0` validates. The capability's premise is a loopback-only server (`tools/kama-llamacpp-live.py:5-6`, "free loopback port"), and the probe-endpoint check hardcodes `127.0.0.1` (`:476-480`). A drifted/tampered producer that exposed the model on all interfaces would still yield `VALID`. Fix: require `argv_flag(argv, "--host") == "127.0.0.1"` (and extend the same value check to `-c == str(ctx)`, `-t == str(threads)`).
3. **Manifest digests are decoration (S3, S4).** `install_tree_sha256` is recomputable from the stored tree with the producer's documented formula (`tools/kama-llamacpp-live.py:161-165`) yet the gate only checks its hex shape (`:254-256`); `server_impl_sha256` is likewise unbound to `install_tree["libllama-server-impl.so"]` (`:257-259`). Forging either to `0*64` validates. The committed receipts' values match my recomputation, but the gate cannot tell. Fix: recompute the combined digest from `install_tree` and require equality whenever the recorded digest is non-null (and require it non-null whenever the tree is non-empty), and require the impl digest to equal the tree entry when non-null.

## Medium

4. **Probe endpoint/command evidence is optional (P1, S5, S1).** A null `declared` bypasses the endpoint check while a wrong string is rejected (`:476-480`); the recorded `probes[].argv` is never read, so the row can claim port 32845 while the recorded probe command says `--port 9`. Fix: require `declared` to be exactly `http://127.0.0.1:{port}/v1`, and check the probe argv's `--port` (and, if present, that the script path/digest equal `receipt.probe`).
5. **Install-tree evidence can be erased (S2, S11).** `{}` skips the basename/entry comparison because of `if tree and …` (`:248`), and a `realpath` without `/` skips the whole block (`:247-253`). Fix: require `install_tree` non-empty and `realpath` an absolute path; then require the basename entry unconditionally.
6. **Lifecycle evidence is not cross-checked (S6, S13, S13b, S17, S21).** `loading_503` is checked as an object and its body is re-derived to the documented envelope (`:336-360`), but its `status` and `path` are free, and `transitions` only has to be a list (`:370-371`). Accepted receipts can omit the transition history, contradict it, or call a 200/`/health` response "loading observed". Fix: require `loading_503.status == 503` and `path == "/v1/models"`; require a matching transitions row (same path, status, body_sha256) whenever `loading_503` is present; cross-check the final healthy transition with `captures.health`.
7. **Body digests are never re-derived (S14, S15).** There is no `hashlib` import; `body_sha256` fields on captures/transitions/loading_503 are trusted. Fix: hash each stored `body` and compare.
8. **Listener ownership accepts "unknown" (S18).** The gate rejects only `"foreign"` (`:362-368`), although `"child"` is what the capability claims (the process-group teardown story depends on it). Fix: require `"child"` when `health_ready` passes, or make ownership one of the 10 re-derived checks.
9. **Health response body is not parsed (S23).** `health_ready` re-derives only `status == 200`; the documented `{"status":"ok"}` body can be replaced with garbage. Fix: parse the stored body and require `status == "ok"`.
10. **argv[0] is unbound (S12).** The receipt may claim `server.realpath` while the recorded argv starts `/bin/true`; `argv[0]` is never compared. Fix: require `argv[0] == server.realpath`. (`server.arg` itself is only the resolution input; the producer uses `server_real` in argv, so binding argv[0] is the meaningful check.)

## Low

- S7 `pdeathsig` (null accepted), S10 `observed` may be `{}`, S16 `documented_by` may be any non-empty string, S19 zero-duration timestamps accepted, S20 `port_pick_note` optional, S24 props `n_ctx` not bound to `ctx`.
- [INFERENCE] `teardown.returncode` accepts any int and `sigkill_sent`/`term_wait_ms` are not cross-checked; a receipt could claim an abnormal exit while `teardown_exited` passes.
- The frozen receipt's `probe.path` is relative (`.ufo/waves/round-16/frozen/kama-probe-before.sh`); the gate never resolves it, so this is cosmetic for the gate but the receipt is not portable outside the lane root.

# What this means for the round

- The committed receipts are sound: both validate with model/server/probe pins, and my independent recomputation matches every file, tree, and body digest. The `10/10` check claims are real, not just `"passed": true`.
- The gate's docstring overclaims: "Every claim is re-derived from the stored evidence" (`tests/llamacpp-live/check-receipt.py:16`). The 10 check verdicts are re-derived; model identity, bind address, manifest/impl/body digests, probe command, listener ownership, and transitions are not. If L1 cites the gate as proof of loopback-only binding, pinned-model serving, or supply-chain tree integrity, that citation overreaches — the proof for the current receipts is the out-of-band recomputation above, not `VALID`.
- Minimal fix batch (all stored-evidence, no network): `argv[0] == realpath`, `--host == 127.0.0.1`, `-m` realpath == `model.path`, `-c`/`-t` == `ctx`/`threads`, non-empty absolute install tree + recomputed tree digest + impl == tree entry, `declared` strict string, probe argv `--port` bound, `loading_503.status/path` exact, transitions cross-checked, `body_sha256` recomputed, ownership == `"child"`, health body parsed. Add one `mut()` per new assertion to `_selftest()`; the current 16 do not cover any accepted class.
- Also record the exact gate argv in `controls.txt` (it currently records only exit codes). If the frozen-probe separability control is meant to pin `--expect-probe-sha256`, the command should show it; B6 proves the pin would work.
- No runtime script calls the gate (`grep -rln check-receipt --include='*.py' --include='*.sh'` → only the gate itself plus the two wave spec generators), so `--expect-*` pinning is an operator convention, not an enforced one. A passing `VALID` without pins carries only the self-asserted digests.

# Limitations

- No live server was started; `pgrep -x llama-server` was empty (exit 1) before and after the attack. I did not run `measure.py`, and I did not run the sibling `MutateReceiptGate` mutant-gate attack.
- Mutation results are from `/tmp/kama-r16-RerunReceiptGate/*.json` (scratch, not retained evidence). The receipt copy was byte-identical before mutation; only the named field per case was changed unless the table says otherwise.
- The gate is an offline validator by design; whether it should hash the model/server files from disk is a design choice. All the fixes above are recomputations from data already inside the receipt, so they do not change that boundary.
- The L1 `controls.txt` does not record the gate command line, so I cannot confirm which `--expect-*` pins L1 actually used; I ran both receipts with all three pins (B4/B5) and both pass.

# Installs

None. Tools used: python3 (stdlib), sha256sum, grep, pgrep (all pre-installed).
