# Draft — capabilities-table row for `tools/kama-context-capacity.py`

Round 25, attempt 2, C2 (capability row). Author: `ScribeCapabilityRow`
(scribe seat). This is a draft for the L1 to paste, after filling the
placeholders `receipt path` and `count-c2.py output` from committed bytes.
Per AXES.md §Capabilities, the row enters the table only through a round that
demonstrates the capability running; this draft does not itself demonstrate it.

## Row (exact four-column format of the capabilities table)

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| context-capacity-live-measurement | Launch the pinned llama-server b11755 fixture (stories260K.gguf, sha256 `270cba1b…256d`) cell-by-cell on 127.0.0.1 inside a free unregistered loopback port; per registered cell record /props `default_generation_settings.n_ctx` and `total_slots`, every /slots `n_ctx`, /v1/models `meta.n_ctx_train`, and captured server-log lines including the KV-pool `llama_context: n_ctx` line, plus server/model sha256 and teardown proof (child killed, port proven closed); write a receipt the strict counter accepts, and run one child at a time. Not consumer health, model quality, or other-engine integration | `receipt path`; `count-c2.py output` | 25 |

Notes for L1:
- Capability name is a proposal; keep it dash-separated like the existing rows
  (`live-llamacpp-lifecycle`, `gguf-declared-identity-replay`).
- The counter's default receipt constant already is
  `.ufo/waves/round-25/final/context-capacity-receipt.json` (`count-c2.py:18`);
  the expected counting output is `registered 14 observed 14 bound True missing []`
  (exit 0). Bind the actual `receipt path` value and the actual
  `count-c2.py output` string in the evidence-pointer cell.
- The row should also state the fixture scope limits (one engine, host paths,
  unregistered loopback port) so the row does not overclaim.
- Where pasted: round-25 section (like rounds 14/20 appended a row in their
  section) and/or the next canonical capabilities list.
