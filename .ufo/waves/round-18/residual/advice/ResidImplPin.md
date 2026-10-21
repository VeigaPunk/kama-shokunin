VERDICT: confirm — the fifth `--expect-server-impl-sha256` pin is wired end to end and refuses every impl-field forgery I rebuilt with exit 1 while four-pin legacy replay stays exit 0; residual tree-level gaps remain, as executed below.

## Evidence

Copy: `cp -a ... /tmp/kama-r18-res-ResidImplPin` (lane HEAD `101f3991d3`, uncommitted fix present). All runs use absolute `/tmp` paths; lane untouched.

Five pins used: model `270cba1b…`, server `b6a31a8e…`, impl `sha256sum ~/.local/opt/llama-b11755/libllama-server-impl.so` = `e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed`, probe `36b64978…`, tool `ec7a7567…`.

Forgeries rebuilt from `ConnectTsukuroi.md` §3 and run against `/tmp` receipt-1 (all `tree_sha` recomputed with the finding's algorithm; launcher sha untouched):

| mutant | contents | with 5 pins | without impl pin |
|---|---|---|---|
| receipt-1 | pristine | exit 0 VALID | exit 0 VALID |
| A implonly | `server_impl_sha256='a'*64` | exit 1, names field + expected | exit 0 VALID |
| B implswap | impl member + `install_tree_sha256` + impl field = `b` | exit 1, names field + expected | exit 0 VALID |
| C rpcswap | `ggml-rpc-server` + tree sha only | **exit 0 VALID** | exit 0 VALID |
| D rpcswap + impl field | C plus impl field = `d` | exit 1, names field | exit 0 VALID |
| E treeswap/field genuine | impl member + tree sha, field left genuine | **exit 0 VALID** | exit 0 VALID |
| F common swap | `libllama-common.so.0.7.0` + tree sha only | **exit 0 VALID** | exit 0 VALID |
| N null | `server_impl_sha256=null` | exit 1: "given but receipt has no server.server_impl_sha256 digest" | exit 0 VALID |
| M absent | key deleted | exit 1: same message | n/a |

Example (B): `- server.server_impl_sha256 bbbb… != expected e404…`; exactly one problem, so no collateral trip.

Format refusal (`receipt-1` + pin `zz`, 63-hex, uppercase, empty): each exit 1 with `- --expect-server-impl-sha256 '<val>' is not 64 lowercase hex chars`; malformed pin on the null receipt emits both that line and the absent-digest line, exit 1. Flag is refused after receipt load (unreadable receipt still exits 2 first), acceptable per acceptance.

Null cannot satisfy: executed above (N/M, exit 1). Gate order: `check_digest(... allow_none=True)` then pin block at `tests/llamacpp-live/check-receipt.py:383-395`; format loop at `:431-435`; argparse at `:2133`.

Legacy: replayed round-16 `receipt.json`, `receipt-frozen-probe.json` and round-17 `receipt-{1,2,3}.json` with each receipt's own four recorded pins, no impl pin, against both `frozen/tests_llamacpp-live_check-receipt.py` and current gate — all ten runs exit 0 VALID (schemas v1/v1/v2/v2/v2).

Runner: `run.py:40-42` resolves `server.parent/'libllama-server-impl.so'`; on the real FS it exists (7,671,544 B), same dir as the non-symlink launcher, sha `e404…` matches every receipt and the recorded `live-gate-{1,2,3}` argv (all exit 0, `as_expected true`). Missing sibling replicated under `/tmp`: `SystemExit: impl library missing: /tmp/.../libllama-server-impl.so`. `run.py:48` passes the pin as `sha(impl)` (host-derived, like the launcher). Producer hashes `sha256_file(dirname(server_real)/libllama-server-impl.so)` and records both tree and impl (`tools/kama-llamacpp-live.py:1222-1224`).

Gate selftest: `--selftest` exit 0, "5 VALID and 1 NOT-EVALUATED … 69 mutations + unreadable case rejected".

## Findings

- **P2 — the pin binds the field, not the tree member; no cross-check exists.** E (tree impl member swapped with recomputed tree sha, `server_impl_sha256` left genuine) is VALID with the impl pin, exit 0. The finding's remediation item 1 also asked for `server_impl_sha256 == install_tree["libllama-server-impl.so"]`; the diff adds only the pin. A self-consistent receipt can name a different impl .so in its tree than the pinned field.
- **P2 — one of 51 files is pinned; the impl's own dependencies are not.** Executed `objdump -p` on the impl: `NEEDED libllama-common.so.0, libggml.so.0, libllama.so.0, libmtmd.so.0`. F swaps `libllama-common.so.0.7.0` (server-relevant, not the rpc helper) consistently and remains VALID even with the impl pin. The inline comment at `check-receipt.py:388-389` ("this pin is what binds the code that implements the lifecycle") overstates the binding: the implementing library's dependencies are only self-recorded in `install_tree`. [INFERENCE] A genuine pre-run swap of such a member would also pass, since `run.py` derives the impl pin from the same install and never pins `install_tree_sha256`; producer-side expected-impl precondition (finding item 4) was not added.
- **P3 — selftest has no consistent-swap witness.** Only `impl-sha-mismatch-expect` and `impl-digest-absent-expect` reference the pin (`:1835-1840`); the finding's item 3 mutant (`impl-consistent-swap`, expect 1 only with the pin) is absent, so the B/F acceptance boundary is not encoded in the gate's own matrix.
- **P3 — runner existence check is one-shot.** It runs before the receipt loop but after all selftests/c1/c2 (`run.py:30-42`); `sha(impl)` at `:48` would raise an uncaught `OSError` if the file vanished mid-loop rather than the named `SystemExit`. [INFERENCE] No observed failure; operability nit only.

## Limits

- Did not execute `run.py` against any lane; path resolution and the missing-file branch were replicated in isolation under `/tmp`. Live receipts were not regenerated.
- Did not audit the unrelated checker hunks (child_env_keys redaction, loading-envelope grading) — sibling residual scope.
- The `NOT-EVALUATED` tri-state is evaluated after `problems` (`:2181-2189`), so a not-evaluated receipt with a null impl plus the pin exits 1, not 3; not exercised with a real not-evaluated fixture, and producer ordering makes the producer hash impl before the not-evaluated outcomes arise.
- `/tmp/kama-r18-res-ResidImplPin` deleted after these runs; no host install, service, or lane state modified.
