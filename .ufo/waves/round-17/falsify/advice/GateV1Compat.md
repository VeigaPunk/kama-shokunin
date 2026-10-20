VERDICT: confirm — the specified v1 receipt and pin-compatibility checks pass; no v1 predicate weakening found.

## Scope attacked

Receipt-v1 no-harm for `tests/llamacpp-live/check-receipt.py`: both round-16 pinned receipts, the frozen-probe/current-probe mismatch, the selftest mutation split, and the frozen-to-current validator diff.

## Findings by severity

None actionable.

The two round-16 receipt files used from the `/tmp` clone were byte-identical to the lane copies: `receipt.json` SHA-256 `076865e5b2de909604c5783d48ec5bf691310763949439d333c42ee5bdbd4669`; `receipt-frozen-probe.json` SHA-256 `8dd144ff4cc4a564bffa4bde962218363907e8085b6e2fc78c0a6d66cb18ef8c`.

Current gate results (each invocation supplied all four `--expect-*-sha256` pins):

- `receipt.json` with its model/server/current-probe/tool pins: `VALID`, exit 0.
- `receipt-frozen-probe.json` with its model/server/frozen-probe/tool pins: `VALID`, exit 0.
- The frozen-probe receipt with the current probe pin: `INVALID` specifically because recorded probe `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64` differs from expected current probe `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`; exit 1.
- Current `--selftest`: exit 0, `2 valid receipt(s) accepted; 39 mutations + unreadable case all rejected`. The frozen v1 gate's `--selftest` also exited 0 with `26 mutations + unreadable case all rejected`; current source adds 13 `mut2` rejection cases (current gate lines 1280–1321), giving the expected 26 v1 + 13 v2 split.

Frozen-to-current diff review found no weakened v1 predicate. The v1 check-ID tuple is retained as `REQUIRED_CHECKS_V1` (current `tests/llamacpp-live/check-receipt.py:67-78`); dispatch selects it for every non-v2 receipt (`:653-660`, quote: `required = REQUIRED_CHECKS_V2 if is_v2 else REQUIRED_CHECKS_V1`). The frozen v1 teardown check is unconditional for its required ID (`.ufo/waves/round-17/frozen/tests_llamacpp-live_check-receipt.py:745-757`, quote: `if "teardown_exited" in by_id:`); current code adds `not is_v2` to that guard (`tests/llamacpp-live/check-receipt.py:834-845`), which leaves the v1 path unchanged because v1 makes `is_v2` false. The new graceful-teardown rule is separately gated to v2 (`:847-874`, quote: `if is_v2 and "teardown_graceful" in by_id:`). In the complete diff, other new evidence-to-claim checks are likewise under `if is_v2`; the existing v1 re-derivations remain in place. The frozen v1 check list and current v1 list match in the reviewed diff.

## Commands and exit codes

All gate runs were against the commit-pinned clone, with `PYTHONDONTWRITEBYTECODE=1`.

- `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/GateV1Compat-clone && git -C /tmp/GateV1Compat-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3` — exit 0.
- `git -C /tmp/GateV1Compat-clone cat-file -p cff9e62:tests/llamacpp-live/check-receipt.py | sha256sum` — exit 0; frozen file digest matched manifest SHA-256 `6b9576a13dde1872977a6af4547599a75cf484f37fe6fe0f4f5557349b09ced6`.
- `cd /tmp/GateV1Compat-clone && git diff --stat cff9e62 54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- tests/llamacpp-live/check-receipt.py` — exit 0; 274 insertions, 18 deletions. `git diff cff9e62 54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- tests/llamacpp-live/check-receipt.py > /tmp/GateV1Compat-work-diff.txt && wc -l /tmp/GateV1Compat-work-diff.txt` — exit 0; 474 diff lines reviewed.
- `PYTHONDONTWRITEBYTECODE=1 python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-16/live/receipt.json --expect-model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d --expect-server-sha256 b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804 --expect-probe-sha256 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3 --expect-tool-sha256 b8c5e8d402595f3b919ea82f29c87f9a2b5d5c2d88bccffa48f1f8880c2f4fe4` — exit 0.
- `PYTHONDONTWRITEBYTECODE=1 python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-16/live/receipt-frozen-probe.json --expect-model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d --expect-server-sha256 b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804 --expect-probe-sha256 93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64 --expect-tool-sha256 b8c5e8d402595f3b919ea82f29c87f9a2b5d5c2d88bccffa48f1f8880c2f4fe4` — exit 0.
- `PYTHONDONTWRITEBYTECODE=1 python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-16/live/receipt-frozen-probe.json --expect-model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d --expect-server-sha256 b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804 --expect-probe-sha256 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3 --expect-tool-sha256 b8c5e8d402595f3b919ea82f29c87f9a2b5d5c2d88bccffa48f1f8880c2f4fe4` — exit 1, expected.
- `PYTHONDONTWRITEBYTECODE=1 python3 tests/llamacpp-live/check-receipt.py --selftest` — exit 0.
- `PYTHONDONTWRITEBYTECODE=1 python3 /tmp/GateV1Compat-frozen-gate.py --selftest` — exit 0.
- `sha256sum` over both clone receipts and both lane receipts — exit 0; paired digests matched as reported above.
- `ss -ltnp` — exit 0. No llama-server or fake service was started by this review.
- `rm -rf /tmp/GateV1Compat-clone /tmp/GateV1Compat-work /tmp/GateV1Compat-work-diff.txt /tmp/GateV1Compat-frozen-gate.py && test ! -e /tmp/GateV1Compat-clone && test ! -e /tmp/GateV1Compat-work-diff.txt && test ! -e /tmp/GateV1Compat-frozen-gate.py` — exit 0; reviewer scratch removed.

## Residual risk and verification gaps

Coverage is the two specified round-16 receipts plus the gate's selftest cases; it is not an exhaustive external corpus of all historical v1 receipts. LSP status/references/definition/diagnostics were unavailable: `read xd://lsp` returned `No such tool: xd://lsp`, so review used the complete frozen-to-current source diff and runtime gate results instead. No tools were installed.