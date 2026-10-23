# Per-row reasons (generated from the two receipts)

## A0 (counter sha256 382c511f…)

`registered 55 counted 21 target 15 met True`

| id | counted | why | live profile | control | status | message (first 70) |
|---|---|---|---|---|---|---|
| E27-01 | yes | — | default | 200 | 400 | 'messages' is required |
| E27-02 | yes | — | default | 200 | 400 | Expected 'messages' to be an array |
| E27-03 | yes | — | default | 200 | 400 | All non-assistant messages must contain 'content' |
| E27-04 | yes | — | default | 200 | 400 | Assistant message must contain either 'content' or 'tool_calls'! |
| E27-05 | yes | — | default | 200 | 400 | Expected 'content' to be a string or an array |
| E27-06 | yes | — | default | 200 | 400 | unsupported content[].type |
| E27-07 | yes | — | default | 200 | 400 | response_format type must be one of "text" or "json_object", but got:  |
| E27-08 | yes | — | no-jinja | 200 | 500 | tools param requires --jinja flag |
| E27-09 | yes | — | no-jinja | 200 | 500 | tool_choice param requires --jinja flag |
| E27-10 | yes | — | default | 200 | 500 | Cannot use both json_schema and grammar |
| E27-11 | yes | — | default | 200 | 400 | invalid type for "enable_thinking" (expected boolean, got string) |
| E27-12 | yes | — | default | 200 | 400 | Cannot have 2 or more assistant messages at the end of the list. |
| E27-13 | yes | — | default | 200 | 400 | Cannot set both add_generation_prompt and continue_final_message to tr |
| E27-14 | yes | — | default | 200 | 400 | Cannot continue an assistant message that contains tool calls. |
| E27-15 | yes | — | default | 200 | 400 | top_logprobs requires logprobs to be set to true |
| E27-16 | yes | — | default | 200 | 400 | Cannot use custom grammar constraints with tools. |
| E27-17 | yes | — | default | 200 | 400 | logprobs is not supported with tools + stream |
| E27-18 | yes | — | embeddings | 200 | 400 | "input" or "content" must be provided |
| E27-19 | yes | — | default | 200 | 400 | "prompt" elements must be a string, a list of tokens, a JSON object co |
| E27-20 | yes | — | default | 200 | 400 | "prompt" must not be empty |
| E27-21 | yes | — | embeddings | 200 | 400 | "input" must not be empty |
| E27-31 | no | b:held-at-base, c:no-new-sources-row, e:not-shown | default | 200 | 200 | — |
| E27-51 | no | b:held-at-base, e:not-shown | default | 200 | 200 | — |
| E27-32 | no | b:held-at-base, c:no-new-sources-row, e:bad-request, e:bad-control | — | — | — | — |
| E27-52 | no | b:held-at-base, e:bad-request, e:bad-control | — | — | — | — |
| E27-33 | no | b:held-at-base, c:no-new-sources-row, e:bad-request, e:bad-control | — | — | — | — |
| E27-53 | no | b:held-at-base, e:bad-request, e:bad-control | — | — | — | — |
| E27-34 | no | b:held-at-base, c:no-new-sources-row, g:control-failed | default | 501 | 501 | This server does not support changing global properties. Start it with |
| E27-54 | no | b:held-at-base, g:control-failed | default | 501 | 501 | This server does not support changing global properties. Start it with |
| E27-35 | no | b:held-at-base, c:no-new-sources-row, g:control-failed | default | 501 | 501 | This server does not support embeddings. Start it with `--embeddings` |
| E27-55 | no | b:held-at-base, g:control-failed | default | 501 | 501 | This server does not support embeddings. Start it with `--embeddings` |
| E27-36 | no | b:held-at-base, c:no-new-sources-row, g:control-failed | embeddings | 400 | 400 | Pooling type 'none' is not OAI compatible. Please use a different pool |
| E27-56 | no | b:held-at-base, g:control-failed | embeddings | 400 | 400 | Pooling type 'none' is not OAI compatible. Please use a different pool |
| E27-37 | no | b:held-at-base, c:no-new-sources-row, d:not-a-literal-on-line, g:control-failed, e:not-shown | embeddings | 400 | 400 | Pooling type 'none' is not OAI compatible. Please use a different pool |
| E27-57 | no | b:held-at-base, d:not-a-literal-on-line, g:control-failed, e:not-shown | embeddings | 400 | 400 | Pooling type 'none' is not OAI compatible. Please use a different pool |
| E27-38 | no | b:held-at-base, c:no-new-sources-row, g:control-failed | default | 501 | 501 | This server does not support reranking. Start it with `--reranking` |
| E27-58 | no | b:held-at-base, g:control-failed | default | 501 | 501 | This server does not support reranking. Start it with `--reranking` |
| E27-39 | no | b:held-at-base, c:no-new-sources-row, g:control-failed | default | 501 | 501 | Infill is not supported by this model: prefix token is missing. suffix |
| E27-59 | no | b:held-at-base, g:control-failed | default | 501 | 501 | Infill is not supported by this model: prefix token is missing. suffix |
| E27-40 | no | b:held-at-base, c:no-new-sources-row | embeddings | 200 | 500 | input (4352 tokens) is too large to process. increase the physical bat |
| E27-60 | no | b:held-at-base | embeddings | 200 | 500 | input (4352 tokens) is too large to process. increase the physical bat |
| E27-41 | no | b:held-at-base, c:no-new-sources-row | default | 200 | 400 | Request body must be an array |
| E27-61 | no | b:held-at-base | default | 200 | 400 | Request body must be an array |
| E27-42 | no | b:held-at-base, c:no-new-sources-row, g:control-failed | default | 501 | 501 | The current model does not support audio input. |
| E27-62 | no | b:held-at-base, g:control-failed | default | 501 | 501 | The current model does not support audio input. |
| E27-43 | no | b:held-at-base, c:no-new-sources-row | default | 200 | 500 | audio input is not supported - hint: if this is unexpected, you may ne |
| E27-63 | no | b:held-at-base | default | 200 | 500 | audio input is not supported - hint: if this is unexpected, you may ne |
| E27-44 | no | b:held-at-base, c:no-new-sources-row, d:not-a-literal-on-line, e:not-shown | default | 200 | 400 | "prompt" elements must be a string, a list of tokens, a JSON object co |
| E27-64 | no | b:held-at-base, d:not-a-literal-on-line, e:not-shown | default | 200 | 400 | "prompt" elements must be a string, a list of tokens, a JSON object co |
| E27-45 | no | b:held-at-base, a:no-skill-row, c:no-new-sources-row, d:unpinned-file, e:not-shown | default | 200 | 200 | — |
| E27-65 | no | b:held-at-base, a:no-skill-row, d:unpinned-file, e:not-shown | default | 200 | 200 | — |
| E27-46 | no | b:held-at-base, a:no-skill-row, c:no-new-sources-row, d:unpinned-file, e:not-shown | default | 200 | 200 | — |
| E27-66 | no | b:held-at-base, a:no-skill-row, d:unpinned-file, e:not-shown | default | 200 | 200 | — |
| E27-47 | no | b:held-at-base, a:no-skill-row, c:no-new-sources-row, d:not-a-literal-on-line, d:no-error-token, e:not-shown | default | 200 | 200 | — |
| E27-67 | no | b:held-at-base, a:no-skill-row, d:not-a-literal-on-line, d:no-error-token, e:not-shown | default | 200 | 200 | — |

## A1 (counter sha256 780c9156…)

`registered 55 counted 20 target 15 met True`

| id | counted | why | live profile | control | status | message (first 70) |
|---|---|---|---|---|---|---|
| E27-01 | yes | — | default | 200 | 400 | 'messages' is required |
| E27-02 | no | d:literal-not-unique:chat.cpp:347 | default | 200 | 400 | Expected 'messages' to be an array |
| E27-03 | yes | — | default | 200 | 400 | All non-assistant messages must contain 'content' |
| E27-04 | yes | — | default | 200 | 400 | Assistant message must contain either 'content' or 'tool_calls'! |
| E27-05 | yes | — | default | 200 | 400 | Expected 'content' to be a string or an array |
| E27-06 | yes | — | default | 200 | 400 | unsupported content[].type |
| E27-07 | yes | — | default | 200 | 400 | response_format type must be one of "text" or "json_object", but got:  |
| E27-08 | yes | — | no-jinja | 200 | 500 | tools param requires --jinja flag |
| E27-09 | yes | — | no-jinja | 200 | 500 | tool_choice param requires --jinja flag |
| E27-10 | yes | — | default | 200 | 500 | Cannot use both json_schema and grammar |
| E27-11 | yes | — | default | 200 | 400 | invalid type for "enable_thinking" (expected boolean, got string) |
| E27-12 | yes | — | default | 200 | 400 | Cannot have 2 or more assistant messages at the end of the list. |
| E27-13 | yes | — | default | 200 | 400 | Cannot set both add_generation_prompt and continue_final_message to tr |
| E27-14 | yes | — | default | 200 | 400 | Cannot continue an assistant message that contains tool calls. |
| E27-15 | yes | — | default | 200 | 400 | top_logprobs requires logprobs to be set to true |
| E27-16 | yes | — | default | 200 | 400 | Cannot use custom grammar constraints with tools. |
| E27-17 | yes | — | default | 200 | 400 | logprobs is not supported with tools + stream |
| E27-18 | yes | — | embeddings | 200 | 400 | "input" or "content" must be provided |
| E27-19 | yes | — | default | 200 | 400 | "prompt" elements must be a string, a list of tokens, a JSON object co |
| E27-20 | yes | — | default | 200 | 400 | "prompt" must not be empty |
| E27-21 | yes | — | embeddings | 200 | 400 | "input" must not be empty |
| E27-31 | no | b:held-at-base, c:no-new-sources-row, e:not-shown | default | 200 | 200 | — |
| E27-51 | no | b:held-at-base, e:not-shown | default | 200 | 200 | — |
| E27-32 | no | b:held-at-base, c:no-new-sources-row, e:bad-request, e:bad-control | — | — | — | — |
| E27-52 | no | b:held-at-base, e:bad-request, e:bad-control | — | — | — | — |
| E27-33 | no | b:held-at-base, c:no-new-sources-row, e:bad-request, e:bad-control | — | — | — | — |
| E27-53 | no | b:held-at-base, e:bad-request, e:bad-control | — | — | — | — |
| E27-34 | no | b:held-at-base, c:no-new-sources-row, g:control-failed | default | 501 | 501 | This server does not support changing global properties. Start it with |
| E27-54 | no | b:held-at-base, g:control-failed | default | 501 | 501 | This server does not support changing global properties. Start it with |
| E27-35 | no | b:held-at-base, c:no-new-sources-row, g:control-failed | default | 501 | 501 | This server does not support embeddings. Start it with `--embeddings` |
| E27-55 | no | b:held-at-base, g:control-failed | default | 501 | 501 | This server does not support embeddings. Start it with `--embeddings` |
| E27-36 | no | b:held-at-base, c:no-new-sources-row, g:control-failed | embeddings | 400 | 400 | Pooling type 'none' is not OAI compatible. Please use a different pool |
| E27-56 | no | b:held-at-base, g:control-failed | embeddings | 400 | 400 | Pooling type 'none' is not OAI compatible. Please use a different pool |
| E27-37 | no | b:held-at-base, c:no-new-sources-row, d:not-a-literal-on-line, g:control-failed, e:not-shown | embeddings | 400 | 400 | Pooling type 'none' is not OAI compatible. Please use a different pool |
| E27-57 | no | b:held-at-base, d:not-a-literal-on-line, g:control-failed, e:not-shown | embeddings | 400 | 400 | Pooling type 'none' is not OAI compatible. Please use a different pool |
| E27-38 | no | b:held-at-base, c:no-new-sources-row, g:control-failed | default | 501 | 501 | This server does not support reranking. Start it with `--reranking` |
| E27-58 | no | b:held-at-base, g:control-failed | default | 501 | 501 | This server does not support reranking. Start it with `--reranking` |
| E27-39 | no | b:held-at-base, c:no-new-sources-row, g:control-failed | default | 501 | 501 | Infill is not supported by this model: prefix token is missing. suffix |
| E27-59 | no | b:held-at-base, g:control-failed | default | 501 | 501 | Infill is not supported by this model: prefix token is missing. suffix |
| E27-40 | no | b:held-at-base, c:no-new-sources-row | embeddings | 200 | 500 | input (4352 tokens) is too large to process. increase the physical bat |
| E27-60 | no | b:held-at-base | embeddings | 200 | 500 | input (4352 tokens) is too large to process. increase the physical bat |
| E27-41 | no | b:held-at-base, c:no-new-sources-row | default | 200 | 400 | Request body must be an array |
| E27-61 | no | b:held-at-base | default | 200 | 400 | Request body must be an array |
| E27-42 | no | b:held-at-base, c:no-new-sources-row, g:control-failed | default | 501 | 501 | The current model does not support audio input. |
| E27-62 | no | b:held-at-base, g:control-failed | default | 501 | 501 | The current model does not support audio input. |
| E27-43 | no | b:held-at-base, c:no-new-sources-row | default | 200 | 500 | audio input is not supported - hint: if this is unexpected, you may ne |
| E27-63 | no | b:held-at-base | default | 200 | 500 | audio input is not supported - hint: if this is unexpected, you may ne |
| E27-44 | no | b:held-at-base, c:no-new-sources-row, d:not-a-literal-on-line, e:not-shown | default | 200 | 400 | "prompt" elements must be a string, a list of tokens, a JSON object co |
| E27-64 | no | b:held-at-base, d:not-a-literal-on-line, e:not-shown | default | 200 | 400 | "prompt" elements must be a string, a list of tokens, a JSON object co |
| E27-45 | no | b:held-at-base, a:no-skill-row, c:no-new-sources-row, d:unpinned-file, e:not-shown | default | 200 | 200 | — |
| E27-65 | no | b:held-at-base, a:no-skill-row, d:unpinned-file, e:not-shown | default | 200 | 200 | — |
| E27-46 | no | b:held-at-base, a:no-skill-row, c:no-new-sources-row, d:unpinned-file, e:not-shown | default | 200 | 200 | — |
| E27-66 | no | b:held-at-base, a:no-skill-row, d:unpinned-file, e:not-shown | default | 200 | 200 | — |
| E27-47 | no | b:held-at-base, a:no-skill-row, c:no-new-sources-row, d:not-a-literal-on-line, d:no-error-token, e:not-shown | default | 200 | 200 | — |
| E27-67 | no | b:held-at-base, a:no-skill-row, d:not-a-literal-on-line, d:no-error-token, e:not-shown | default | 200 | 200 | — |

