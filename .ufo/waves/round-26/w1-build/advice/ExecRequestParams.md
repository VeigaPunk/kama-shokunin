VERDICT: Two distinct `/completion` prompt-validation signatures reproduced in two independent fixture launches each; both counted in the scratch counter (2/2), while the global target remains 12.

## Confirmed candidates

The candidate signatures include the literal backslashes before the quotes. This is intentional: the channel is the raw HTTP JSON response body, which carries `\"prompt\"`, and the pinned C++ literal carries the same bytes. The candidate registry contains two `id: TBD` / `source.row: TBD` entries as requested. The `R26RP01`/`R26RP02` IDs and `S901`/`S902` rows below were scratch-only counter placeholders; no production SKILL or SOURCES files were changed.

1. **Prompt object of an unsupported type** — signature: `\"prompt\" elements must be a string, a list of tokens, a JSON object containing a prompt string, or a list of mixed strings & tokens.` Source: [`server-common.cpp`, line 1114](https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1114). Fresh raw fetch URL: `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp`; access date 2026-10-23. Fetched SHA256 `b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442` equals the pinned snapshot. Located source quote (25 words): `\"prompt\" elements must be a string, a list of tokens, a JSON object containing a prompt string, or a list of mixed strings & tokens.`
   - Trigger: `POST /completion` with `{"prompt":{"not_prompt":true}}`.
   - Runs on ports 47661 and 47662 both returned HTTP 400 with the exact signature in the raw response body. Run 47660 also returned 400 on both `/completion` and `/v1/completions`.

2. **Empty prompt list** — signature: `\"prompt\" must not be empty`. Source: [`server-common.cpp`, line 1129](https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1129), same fresh fetch and hash above; opened 2026-10-23. Located source quote: `\"prompt\" must not be empty`.
   - Trigger: `POST /completion` with `{"prompt":[]}`.
   - Runs on ports 47661 and 47662 both returned HTTP 400 with the exact signature in the raw response body. `/v1/completions` also returned 400 on both launches.

Counter/source handling context:
- [`server-context.cpp`, line 4929](https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L4929), fresh raw URL `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp`, opened 2026-10-23; fetched SHA256 `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329` matches the pinned snapshot. Quote: `inputs = tokenize_input_prompts(ctx_server.vocab, ctx_server.mctx, prompt, true, true, ctx_server.init_opt);` The surrounding handler catches exceptions at lines 4968–4970 and returns an invalid-request response.
- [`server-task.cpp`, line 1505](https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-task.cpp#L1505), freshly fetched from `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-task.cpp`, opened 2026-10-23; fetched SHA256 `4c3f413b9b54d4cc0e7b5998e6979a2389f5ff716e20cb1510ca7745fa233495` matches the pinned snapshot. Quote: `json res = format_error_response(err_msg, err_type);` The surveyed task-result formatter supplied no additional pinned request-validation signature.

## Counter result

The frozen counter was run in a `git archive` extract of `a23c0e042114016a909eb15173aa6df74b5b7eb0`; its SHA256 matched the preregistered `6501737c749926be9d6b37761175d76f89876976c46bd5951fc1a3520c796588`. Scratch-only SKILL and SOURCES rows plus the registry were added there. Final output: `registered 2 counted 2 target 12 met False not-counted []` (exit 0). Both rows have `a_skill_row`, `b_long`, `b_new_at_base`, `c_source_row`, `d_source_pinned`, `d_in_source`, `e_error_shown`, `e_signature_seen`, `e_not_echoed`, `f_absent_from_baseline`, and `g_distinct` true in `counter-receipt.json`.

The first scratch counter attempt printed `registered 2 counted 0 target 12 met False not-counted ['R26RP01:d_in_source', 'R26RP02:d_in_source']`. That caught an encoding mistake: plain quote bytes do not match the raw JSON/C++ escaped-quote bytes. I corrected the signatures to include the literal backslashes and reran the unchanged frozen counter; the final run counted both. The first output is retained in `counter-first-output.txt`.

## Falsifiers and exclusions

- `n_probs:"bad"` on `/completion` returned HTTP 400, but its message was `Field 'n_probs': [json.exception.type_error.302] type must be number, but is string`; no matching constant was located in the pinned source files, so it is not a candidate.
- `samplers:["not-a-real-sampler"]` returned HTTP 200 on `/completion` and `/v1/completions`; the server log warns that it could not match the sampler. It did not reproduce an HTTP error.
- `logit_bias:"bad"` returned HTTP 200, so it was not a validation error on this fixture.
- The grammar/JSON-schema conflict returned HTTP 500 on `/v1/chat/completions`, but `/completion` returned 200. The HTTP-500 case is outside the assigned `/completion` and `/v1/completions` route scope and is excluded.
- Misuse of `/tokenize` and `/detokenize` returned HTTP 400 with generic `json.exception.type_error.302` messages; these strings are not pinned C++ source literals in the allowed source snapshot, so they are excluded.

## Retained files

Files written under the assigned output directory:
- `candidates.json`
- `RUNS.txt`
- `probe1.json`, `probe1-server.log`, `probe2.json`, `probe2-server.log`, `probe3.json`, `probe3-server.log` (full request/response bodies and merged server output)
- `counter-first-output.txt`, `counter-output.txt`, `counter-receipt.json`
- `.ufo/waves/round-26/w1-build/advice/ExecRequestParams.md` (this report)

Scratch-only files: the frozen archive extract at `/fast/scratch/hyaku/kama-r26/ExecRequestParams/counter-tree/` (only its registry, SKILL.md, and corpus/SOURCES.md were amended); fresh source fetches `server-common.cpp`, `server-context.cpp`, and `server-task.cpp`; and `help.out` / `version.out` captures under `/fast/scratch/hyaku/kama-r26/ExecRequestParams/`. No tools were installed.

## Risks and blockers

- This seat contributes two rows, not the global target of 12. The L1 must assign real IDs/source rows, verify fleet-wide distinctness, and integrate the candidate rows.
- The candidate registry retains required `TBD` placeholders; it is not a production registry ready to merge unchanged.
- An `llama-server` process was observed during the run on port 47654 (PIDs 3778099/3778102), outside this seat's block; it was not touched. The final process query had no output (exit 1), and all four assigned ports were closed. The 47654 process was not established as belonging to this seat.
- No LSP tool is exposed in this seat's tool inventory; symbols were inspected from the freshly fetched, pinned text sources instead.
