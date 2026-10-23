# Round-26 C1 source gates — `server-context.cpp`

Pinned source URL base: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp
Access date for each line: 2026-10-23. Each quote is at most 25 words and was checked against the fresh fetch at `/fast/scratch/hyaku/kama-r26/ScribeSourcesContext/server-context.cpp`.

- S114 — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5304; accessed 2026-10-23; quote at 5304: `This server does not support metrics endpoint.`; guard at 5303: `if (!params.endpoint_metrics)`.
- S115 — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5366; accessed 2026-10-23; quote at 5366: `This server does not support slots endpoint.`; guard at 5365: `if (!params.endpoint_slots)`.
- S116 — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5408; accessed 2026-10-23; quote at 5408: `This server does not support slots action.`; guard at 5407: `if (params.slot_save_path.empty())`.
- S117 — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5453; accessed 2026-10-23; quote at 5453: `This server does not support changing global properties.`; guard at 5452: `if (!params.endpoint_props)`.
- S118 — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L6132; accessed 2026-10-23; quote at 6132: `This server does not support embeddings.`; guard at 6131: `if (!params.embedding)`.
- S119 — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L6137; accessed 2026-10-23; quote at 6137: `Pooling type 'none' is not OAI compatible. Please use a different pooling type`; guard at 6136: `if (res_type != TASK_RESPONSE_TYPE_NONE && meta->pooling_type == LLAMA_POOLING_TYPE_NONE)`.
- S120 — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L6151; accessed 2026-10-23; quote at 6151: `\"input\" or \"content\" must be provided`; guards at 6145 and 6147: `if (body.count("input") != 0)` and `else if (body.contains("content"))`; final `else` at 6150 emits the error.
- S121 — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L6161; accessed 2026-10-23; quote at 6161: `The format to return the embeddings in. Can be either float or base64`; guard at 6160: `else if (format != "float")` (the preceding accepted value is `base64` at 6158-6159).
- S122 — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L6183; accessed 2026-10-23; quote at 6183: `\"input\" must not be empty`; guard at 6182: `if (tokenized_prompts.empty())`.
- S123 — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5803; accessed 2026-10-23; quote at 5803: `This server does not support reranking.`; guard at 5802: `if (!params.embedding || params.pooling_type != LLAMA_POOLING_TYPE_RANK)`.
- S124 — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5822; accessed 2026-10-23; quote at 5822: `\"query\" must be provided`; guard at 5815: `if (body.count("query") == 1)`; the `else` at 5821 emits this error.
- S125 — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5829; accessed 2026-10-23; quote at 5829: `\"documents\" must be a non-empty string array`; guard at 5828: `if (documents.empty())`.
- S126 — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5476; accessed 2026-10-23; quote at 5476: `Infill is not supported by this model: %s`; guard at 5475: `if (!err.empty())`; `err` is built from the missing FIM-token checks at 5466, 5469, and 5472.
- S127 — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L3378; accessed 2026-10-23; quote at 3378: `context shift is disabled`; guard at 3375: `if (!params_base.ctx_shift)`; the generation/context-boundary precondition is at 3374.
- S128 — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L3678; accessed 2026-10-23; quote at 3678-3679: `request (%d tokens) exceeds the available context size (%d ` / `tokens), try increasing it`; guard at 3676: `if (slot.task->n_tokens() >= slot.n_ctx)` inside the non-splitting branch at 3675.
- S129 — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L2466; accessed 2026-10-23; quote at 2466: `Failed to format input: `; guard at 2465: `catch (const std::exception & e)`.
- S130 — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5998; accessed 2026-10-23; quote at 5998: `Request body must be an array`; guard at 5997: `if (!body.is_array())`.
- S131 — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5655; accessed 2026-10-23; quote at 5655: `The current model does not support audio input.`; guard at 5654: `if (!meta->has_mtmd || !meta->chat_params.allow_audio)`.

## Fetched-byte line-number search output

The following matched lines are copied from the line-numbered `functions.grep` result for the fresh fetched bytes (unmatched context omitted):

```text
2466:            send_error(task, std::string("Failed to format input: ") + e.what(), ERROR_TYPE_INVALID_REQUEST);
3378:                    send_error(slot, "context shift is disabled", ERROR_TYPE_SERVER);
3678:                                           string_format("request (%d tokens) exceeds the available context size (%d "
3679:                                                         "tokens), try increasing it",
5304:            res->error(format_error_response("This server does not support metrics endpoint. Start it with `--metrics`", ERROR_TYPE_NOT_SUPPORTED));
5366:            res->error(format_error_response("This server does not support slots endpoint. Start it with `--slots`", ERROR_TYPE_NOT_SUPPORTED));
5408:            res->error(format_error_response("This server does not support slots action. Start it with `--slot-save-path`", ERROR_TYPE_NOT_SUPPORTED));
5453:            res->error(format_error_response("This server does not support changing global properties. Start it with `--props`", ERROR_TYPE_NOT_SUPPORTED));
5476:            res->error(format_error_response(string_format("Infill is not supported by this model: %s", err.c_str()), ERROR_TYPE_NOT_SUPPORTED));
5655:            res->error(format_error_response("The current model does not support audio input.", ERROR_TYPE_NOT_SUPPORTED));
5803:            res->error(format_error_response("This server does not support reranking. Start it with `--reranking`", ERROR_TYPE_NOT_SUPPORTED));
5822:            res->error(format_error_response("\"query\" must be provided", ERROR_TYPE_INVALID_REQUEST));
5829:            res->error(format_error_response("\"documents\" must be a non-empty string array", ERROR_TYPE_INVALID_REQUEST));
5998:            res->error(format_error_response("Request body must be an array", ERROR_TYPE_INVALID_REQUEST));
6132:        res->error(format_error_response("This server does not support embeddings. Start it with `--embeddings`", ERROR_TYPE_NOT_SUPPORTED));
6137:        res->error(format_error_response("Pooling type 'none' is not OAI compatible. Please use a different pooling type", ERROR_TYPE_INVALID_REQUEST));
6151:        res->error(format_error_response("\"input\" or \"content\" must be provided", ERROR_TYPE_INVALID_REQUEST));
6161:            res->error(format_error_response("The format to return the embeddings in. Can be either float or base64", ERROR_TYPE_INVALID_REQUEST));
6183:        res->error(format_error_response("\"input\" must not be empty", ERROR_TYPE_INVALID_REQUEST));
```
