# DRAFT registry rows — round-20 new instruments (RegNewTools)

Status: DRAFT for the L1 integrator. Not written to `SKILL.md`. Tool files do
not exist at lane HEAD `37bd4c5bd456a2f8a54d3312c28495c321715856` (`git cat-file -e`
exit 128 for both paths), so every command, flag and exit below is a PROPOSED
contract marked `[INFERENCE]` until L1 integrates the tool and runs it.
`<L1 fills>` marks measured tallies and any contract detail L1 must confirm.

## Row A — C1 error-verdict census (new section, owner: kama)

| Name | Kind / entry command | Verdict map | Self-test | Pinned values | Write scope | Owner |
|---|---|---|---|---|---|---|
| Error-verdict census | measurement: `python3 tools/error-verdict-census.py [--json]` `[INFERENCE: flags and entry point; L1 fills]` | 0 every frozen-arm and current-arm cell in `registry/error-injection-cells.json` classified as its expected class (verdict vs could-not-evaluate/error); 1 a cell misclassified (an error counted as a verdict, or the reverse); 2 registry or frozen instrument bytes unreadable or the frozen revision unusable `[INFERENCE: L1 fills exact mapping]` | `--selftest`: `<L1 fills>` cases | frozen arm = `git show 37bd4c5bd456a2f8a54d3312c28495c321715856:<path>`; cell count `<L1 fills>`; known red cells: `tests/llamacpp-live/install-tree-grid.py:110` (`rejected` on any gate exit 1; gate verdict is stdout `INVALID ` with exit 1 at `tests/llamacpp-live/check-receipt.py:2233`), round-18 selftest-kill arm `.ufo/waves/round-18/c2/survivors.py` (exists at frozen rev) | stdout; `--json` to stdout only `[INFERENCE]` | kama |

Measured tallies (`<L1 fills>`): cells total `<L1 fills>`; frozen arm misclassified
`<L1 fills>`; current arm misclassified `<L1 fills>`; frozen-arm exit `<L1 fills>`;
current-arm exit `<L1 fills>`.

Boundary: a could-not-evaluate or error is never a verdict. This row says nothing
about whether any instrument is correct in general; it grades only the enumerated
cells.

## Row B — C2 GGUF declared identity (new section, owner: kama)

| Name | Kind / entry command | Verdict map | Self-test | Pinned values | Write scope | Owner |
|---|---|---|---|---|---|---|
| GGUF declared identity | capability: `python3 tools/gguf-identity.py PATH [--json]` `[INFERENCE: flags; L1 fills]`; reconciliation: `python3 tools/gguf-identity.py PATH --receipt RECEIPT [--json]` `[INFERENCE]` | `[INFERENCE: L1 fills]` 0 decoded and (with `--receipt`) sha256 bound to `model_sha256_post`; 1 reconciliation mismatch, including declared `llama.context_length` vs served `default_generation_settings.n_ctx` difference `[INFERENCE: whether a difference is 1 or reported only; L1 fills]`; 2 unreadable, not GGUF, or any fail-closed bound exceeded | `--selftest`: `<L1 fills>` synthetic fixtures; oracle comparison `<L1 fills>` | stories260K pins (verified in this row's draft, see below) | stdout only `[INFERENCE]` | kama |

Oracle and pins (executed for this draft):
- Oracle: gguf-py `0.19.0` via `uv run --quiet --with gguf python` (exit 0).
- File `/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf`: 1185376 bytes;
  sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` (matches
  the pin in the command). Header bytes: magic `GGUF`, version 3, tensor_count 48,
  kv_count 22 (raw `struct` read, exit 0; gguf-py agrees: 48 tensors, 22 fields).
- Decoded by gguf-py: `general.architecture`=`llama`; `general.name`=`llama`;
  `llama.context_length`=2048; `llama.embedding_length`=64; `llama.block_count`=5;
  `llama.attention.head_count`=8; `llama.attention.head_count_kv`=4;
  `llama.feed_forward_length`=172; `tokenizer.ggml.model`=`llama`.
- ABSENT in this file (oracle returns None): `general.file_type`,
  `general.alignment`. The tool must report absence, never a default.
- Receipt `.ufo/waves/round-18/live-recovery/receipt-1.json` (schema
  `kama-llamacpp-live/v3`): `model_sha256_post` equals the file sha256 above;
  `captures.props.fields["default_generation_settings.n_ctx"]` = 256. Declared
  2048 vs served 256 is a real, present difference; the row must state the policy
  for it (`<L1 fills>`) rather than let it pass silently.

Measured tallies (`<L1 fills>`): synthetic fixtures accepted/rejected `<L1 fills>`;
oracle field agreement `<L1 fills>`; fail-closed bound cases `<L1 fills>`.

Boundary: declared identity from the header, not the weights' behaviour; the
served-context comparison is a reported difference, not a health verdict.
