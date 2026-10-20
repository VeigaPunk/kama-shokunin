VERDICT: confirm — v3 gate contract implemented; frozen v1/v2 verdicts preserved.

## Delivered files
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/C1Gate-2/check-receipt.py` — SHA-256 `51557608ce46e7411370d8c102f5665f416056c6539a929c0c555a0b8f1e508c`.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/C1Gate-2/check-receipt.py.diff` — unified diff against the frozen round-start gate; SHA-256 `6b70a9c572a51903587cc1da0a17bce2d213192f1e51967b6d461a2ea9d6fd16`.
- This report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/advice/C1Gate.md`.

## Findings
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/check-receipt.py:269-285` — v3 schema, `internal_fault`/`setup_error` mirror and accepted schema set. A v3 `outcome` is re-derived from setup-error, false checks, and null checks (`:1355-1368`).
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/check-receipt.py:799-822` — `passed`/`evaluated` tri-state validation; the only unevaluated check is `loading_envelope_graded`, with reason `no-loading-503-observed` and no `/v1/models` 503.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/check-receipt.py:495-515` — exact server argv reconstructed from server realpath, `model.arg`, alias, host, port, ctx and threads; duplicates and extra flags fail.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/check-receipt.py:545-575` — v3 transition status typing rejects a string `"503"`; every `/v1/models` transition 503 body is checked for the exact envelope and rejected if truncated. The v3 loading-check path compares transition digests/repeats against the deduplicated body ledger and rejects an unretained body (`:1177-1320`).
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/check-receipt.py:113-158` — source-binding pinned check/path/URL/line/file/span identities plus span digest and line-count re-derivation. V3 observed fields are also compared with stored check evidence (`:857-859`, `:889-977`, `:1103-1138`, `:1337-1340`).
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/check-receipt.py:2065-2110` — minimum `--require-schema v1|v2|v3`; valid null-only v3 receipts print `NOT-EVALUATED` and exit 3.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/check-receipt.py:1847-2002` — v3 good/not-evaluated fixtures and rejection mutations, including extra/duplicate argv, string-status/non-exact transition envelopes, child ownership, source-binding tamper, internal-fault mismatch, evidence-field drift, invalid tri-state/outcome combinations, and the synthetic 257-distinct-body truncation case.

## Verification and commands
Executed in `/tmp/kama-r18-C1Gate-2`:
- `python3 -m py_compile tests/llamacpp-live/check-receipt.py` — exit 0.
- `python3 tests/llamacpp-live/check-receipt.py --selftest` — exit 0; `selftest: 5 VALID and 1 NOT-EVALUATED receipts accepted; 61 mutations + unreadable case rejected`.

Legacy parity command: a loop invoked both the frozen gate (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_llamacpp-live_check-receipt.py`) and the clone gate with `--expect-model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`, `--expect-server-sha256 b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`, and the per-receipt probe/tool pins below. Loop exit 0; both gates printed the same `VALID <receipt>` line and exited 0 for all five receipts:
- Round 16 `receipt.json`: probe `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`, tool `b8c5e8d402595f3b919ea82f29c87f9a2b5d5c2d88bccffa48f1f8880c2f4fe4`.
- Round 16 `receipt-frozen-probe.json`: probe `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64`, same tool pin.
- Round 17 `receipt-1.json`, `receipt-2.json`, `receipt-3.json`: probe `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`, tool `0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac`.

The first parity attempt used the current probe pin `36b649…` for the frozen-probe receipt; both gates rejected it with exit 1 because that receipt records `93ee…`. Re-running with the receipt’s recorded `93ee…` pin yielded matching `VALID`/0 results.

Delivery command: `diff -u <frozen gate> <clone gate> > <delivered diff>` — diff exit 1 (expected changed file); copy and SHA-256 calculation succeeded. `read xd://lsp` returned “No such tool” (the mounted-device list had no LSP), so no LSP symbol/reference operations were available. No tools were installed or updated.

## Design choices, limitations, and blockers
- v1/v2 checking remains on its legacy paths; the five receipts above retained frozen verdict lines and exit codes. V3 failures and setup-error receipts are INVALID/1; a valid receipt whose only shortfall is the allowed loading-check null is NOT-EVALUATED/3.
- The source-binding gate uses the round-pinned identities and verifies literal span text against the pinned span hash; it does not fetch upstream files. Consequently it cannot independently prove a whole-file digest against the upstream file bytes or authenticate source provenance beyond those locally pinned constants.
- The gate rejects a nonzero `loading_bodies_dropped`, and detects ledger omissions by comparing the retained body digest/repeat map with `/v1/models` 503 transition evidence. If a producer removes an observation from both the transition list and body ledger and reconciles every counter, no receipt-only gate can detect the absent event without independent runtime evidence.
- Truncated health/models captures are rejected and their stored body hashes are re-derived. The producer does not retain raw props/slots/metrics bodies, so those capture hashes cannot be recomputed from the receipt. A consistently rewritten receipt is not cryptographically authenticated.
- The 257-body case is synthetic; no real v3 producer receipt or live server was exercised while the producer implementation was being written concurrently. Integration against its final receipt remains for L1’s gate.
- No other blockers or installs.
