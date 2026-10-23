VERDICT: Confirmed one embeddings-disabled fault twice; one candidate passed every frozen-counter predicate and contributes one of the round's 12 target rows.

## Findings

- The fixture server was the pinned `llama-server` b11755, commit `704366d76`; SHA-256 `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`. The fixture model SHA-256 was `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`.
- Run 1 on `127.0.0.1:47616`: `POST /v1/embeddings` with `{"model":"stories260K","input":"hello"}` returned HTTP 501 and `{"error":{"code":501,"message":"This server does not support embeddings. Start it with `--embeddings`","type":"not_supported_error"}}`. `POST /embedding` with `{"content":"hello"}` returned the same 501 body. Raw outputs: `w1-build/out/ExecEmbeddingsOff/run1-v1embeddings.out`, `run1-embedding.out`; startup log: `run1-server.log`.
- Run 2 on `127.0.0.1:47617`: the same `POST /v1/embeddings` returned HTTP 501 with the identical body. Raw output: `run2-v1embeddings.out`; startup log: `run2-server.log`. The endpoint pair uses the same `handle_embeddings_impl` gate, so these are one fault family and one candidate row, not two.
- The healthy no-`--embeddings` run on port `47618` returned HTTP 200 for `/health`, `/v1/models`, `/props`, `/slots`, `/completion`, `/v1/chat/completions`, and `/tokenize`; startup log is `healthy-baseline-server.log`. Full baseline and informational-output searches, plus the counter's own healthy baseline, are recorded in `RUNS.txt`; the counter reports `f_absent_from_baseline=true` for the selected signature.
- The selected 28-byte signature is ``Start it with `--embeddings```. Exact base check: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin grep -F -q -e 'Start it with `--embeddings`' 1560e4d8 -- SKILL.md corpus; rc=$?; echo "base-grep rc=$rc"; exit 0` → `base-grep rc=1` (no match).
- Pinned source: `server-context.cpp:6132`, URL `https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L6132`, accessed 2026-10-23. Located quote (line 6132, 10 words): “This server does not support embeddings. Start it with `--embeddings`”. The pinned snapshot SHA-256 and fresh fetch SHA-256 both equal `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329`.
- Scratch-only frozen counter command: `flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 900 python3 .ufo/waves/round-26/count-c1.py --out /fast/scratch/hyaku/kama-r26/ExecEmbeddingsOff/counter-receipt.json` from the `git archive a23c0e042114016a909eb15173aa6df74b5b7eb0` extract. Output: `registered 1 counted 1 target 12 met False not-counted []`. Receipt marks each predicate true, including source pin, source literal, live HTTP error, no request echo, baseline absence, and distinct trigger. The normal completion path exits 0 (`count-c1.py:419`). Scratch placeholders `E-EMB-OFF` and `S900` are not lane data.
- Cleanup: all three launches were terminated; final `pgrep -af 'llama-server.*4761[6-9]'` and `ss -ltn | grep -E '4761[6-9]'` returned no matches (both rc=1). The second-run and baseline async `$!` cleanup attempts did not capture their PIDs; each was then identified with `pgrep` and killed explicitly. Their process exit codes were not separately captured.

## Risks and blockers

- This seat confirmed one of the 12 target rows; it does not meet the aggregate target alone. Both HTTP routes yield the same error string, so counting both as separate faults would duplicate one fault family.
- The API-key/CORS warning in the server logs was emitted by the fixture server; no credential values were read or used. No tools were installed.
- No blockers to this scoped candidate. The counter's aggregate target remains for the lane integration.

## Files written

Lane output files:
- `.ufo/waves/round-26/w1-build/out/ExecEmbeddingsOff/candidates.json`
- `.ufo/waves/round-26/w1-build/out/ExecEmbeddingsOff/RUNS.txt`
- `.ufo/waves/round-26/w1-build/out/ExecEmbeddingsOff/run1-v1embeddings.out`
- `.ufo/waves/round-26/w1-build/out/ExecEmbeddingsOff/run1-embedding.out`
- `.ufo/waves/round-26/w1-build/out/ExecEmbeddingsOff/run2-v1embeddings.out`
- `.ufo/waves/round-26/w1-build/out/ExecEmbeddingsOff/run1-server.log`
- `.ufo/waves/round-26/w1-build/out/ExecEmbeddingsOff/run2-server.log`
- `.ufo/waves/round-26/w1-build/out/ExecEmbeddingsOff/healthy-baseline-server.log`
- `.ufo/waves/round-26/w1-build/out/ExecEmbeddingsOff/counter-output.txt`
- `.ufo/waves/round-26/w1-build/out/ExecEmbeddingsOff/counter-receipt.json`
- `.ufo/waves/round-26/w1-build/advice/ExecEmbeddingsOff.md`

Scratch-only additions/edits: `/fast/scratch/hyaku/kama-r26/ExecEmbeddingsOff/extract/SKILL.md`, `.../extract/corpus/SOURCES.md`, `.../extract/registry/error-signatures-r26.json`, `.../counter-receipt.json`, `.../run1-server.log`, `.../run1-v1embeddings.out`, `.../run1-embedding.out`, `.../run2-server.log`, `.../run2-v1embeddings.out`, and `.../baseline-server.log`. The extract itself was created from the frozen archive under the same scratch directory.
