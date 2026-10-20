VERDICT: partial — Frozen-gate oracle recorded; reproduction by the round-18 gate remains unverified because no C1 candidate was available.

## Axis and oracle

Axis: C1 gate backwards compatibility. Round 16 requires the real receipts to remain `VALID` under all four pins and explicitly records the frozen-probe/current-probe mismatch as exit 1 (`corpus/lessons/round-16.md:131-132`, “real receipts `VALID` with all four pins; the frozen-probe receipt fails with the current probe's pin (exit 1)”). Round 17 repeats both v1 receipt expectations and records three v2 receipt results (`corpus/lessons/round-17.md:176-179`; `.ufo/waves/round-17/live/gate.txt:1-7`, “VALID .ufo/waves/round-17/live/receipt-1.json”).

I cloned lane `master` at `e75cf680b53484a61709ee1b2787d8dbc6419f74` to `/tmp/kama-r18-RevV2Compat-2`, then ran its `tests/llamacpp-live/check-receipt.py` against the cloned receipts. The clone's gate and the round-18 frozen gate both hashed to `ad6801791f2ada896a7ee188609391aac86185c47320dbf415331869ca9cd2a5`, matching `.ufo/waves/round-18/frozen/SHA256SUMS:4` (“ad6801791f2ada896a7ee188609391aac86185c47320dbf415331869ca9cd2a5  tests_llamacpp-live_check-receipt.py”). No server was started. The scratch clone was removed after the replay.

The command for each row was `python3 tests/llamacpp-live/check-receipt.py <receipt> --expect-model-sha256 <M> --expect-server-sha256 <S> --expect-probe-sha256 <P> --expect-tool-sha256 <T>`. Values: common model pin **M** = `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` and server pin **S** = `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804` (receipt evidence: round-16 `receipt.json:216-218,392,399`; round-17 `receipt-1.json:251,434`).

| Receipt | Probe pin P | Tool pin T | Frozen-gate stdout | Exit |
|---|---|---|---|---:|
| `.ufo/waves/round-16/live/receipt.json` | `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3` | `b8c5e8d402595f3b919ea82f29c87f9a2b5d5c2d88bccffa48f1f8880c2f4fe4` | `VALID .ufo/waves/round-16/live/receipt.json` | 0 |
| `.ufo/waves/round-16/live/receipt-frozen-probe.json` | `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64` | `b8c5e8d402595f3b919ea82f29c87f9a2b5d5c2d88bccffa48f1f8880c2f4fe4` | `VALID .ufo/waves/round-16/live/receipt-frozen-probe.json` | 0 |
| `.ufo/waves/round-17/live/receipt-1.json` | `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3` | `0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac` | `VALID .ufo/waves/round-17/live/receipt-1.json` | 0 |
| `.ufo/waves/round-17/live/receipt-2.json` | `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3` | `0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac` | `VALID .ufo/waves/round-17/live/receipt-2.json` | 0 |
| `.ufo/waves/round-17/live/receipt-3.json` | `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3` | `0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac` | `VALID .ufo/waves/round-17/live/receipt-3.json` | 0 |

Pin provenance: round-16 receipt files contain the model, server, probe and tool digests (`receipt.json:216-232,392,399,420-421`; frozen-probe receipt `:216-232`). Round-17's `gate.txt:7` records the probe/tool pair, and `receipt-1.json:251,267,434,529` records the corresponding model/server/probe/tool fields. All five commands above produced the listed stdout and exit when run against the frozen gate in the clone.

### Required negative pin control

Re-ran the frozen-probe receipt with the same M/S/T pins, but with the current probe pin P=`36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3` instead of its recorded P=`93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64`.

Exact stdout:

```text
INVALID .ufo/waves/round-16/live/receipt-frozen-probe.json: 1 problem(s)
  - probe.sha256 93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64 != expected 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3
```

Exit: **1**. This matches the historical control (`.ufo/waves/round-16/live/controls.txt:16-20`, “gate_frozen_with_current_probe_pin_exit=1 (expect 1)”) and round-17's recorded compatibility behavior (`corpus/lessons/round-17.md:177-179`).

## New-gate reproduction requirement and gap

The C1 candidate was not present in `.ufo/waves/round-18/build/out/` when inspected (the listing contained `C2Provenance-2/` only), so I could not check reproduction against the new gate. This report establishes the frozen oracle, not a pass by the new gate. [INFERENCE] Compare the new gate in its backward-compatible minimum-schema mode (default or `--require-schema v1`): `--require-schema v2`/`v3` deliberately makes lower-schema v1 receipts invalid, and would not be an equivalent compatibility invocation. The new gate should reproduce all five `VALID` stdout/exit-0 rows above and the frozen-probe/current-probe `INVALID` stdout/exit-1 control with these exact pins.

No tool installed or updated.