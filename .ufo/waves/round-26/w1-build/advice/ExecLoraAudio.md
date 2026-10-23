# ExecLoraAudio — wave-1 advice (C1 candidate signature rows)

Verdict: 3 confirmed candidate error signatures for C1 (LoRA adapter endpoint misuse + audio/multimodal input to a text-only model), each reproduced live twice on my port block 47656-47659; the frozen counter counts all 3 (`registered 3 counted 3`) in a scratch extract.

## Candidates (candidates.json, one entry per confirmed distinct fault)

| id | channel | status | signature (verbatim, >= 20 bytes) | source file:line |
|---|---|---|---|---|
| EXECLORAAUDIO-LORA1 | http POST /lora-adapters | 400 | `Request body must be an array` | server-context.cpp:5998 |
| EXECLORAAUDIO-TRN1 | http POST /v1/audio/transcriptions | 501 | `The current model does not support audio input.` | server-context.cpp:5655 |
| EXECLORAAUDIO-CHAT1 | http POST /v1/chat/completions | 500 | `audio input is not supported - hint: if this is unexpected, you may need to provide the mmproj` | server-common.cpp:1272 |

All use fixture model, no extra args, occupy_port false. Source rows are placeholders S901-S903 in the scratch extract; final S### numbering must be assigned by the L1 at integration (SOURCES.md rows do not exist at base; the scratch rows carry the file basename and `704366d`).

## Live reproduction (two independent launches, ports 47656 and 47657)

Server: `~/.local/bin/llama-server` sha256 b6a31a8e…cd804 (matches counter pin), model stories260K.gguf sha256 270cba1b…256d, each launch `-m <fixture> --host 127.0.0.1 --port <47656|47657> -t 2` wrapped in `timeout 120`, logs `server2.log`/`server3.log` (scratch).

Port 47656 (run 2) and port 47657 (run 2) responses, byte-identical across ports:

```
POST /lora-adapters  body {"id":0,"scale":1.0}
  -> 400 {"error":{"code":400,"message":"Request body must be an array","type":"invalid_request_error"}}
POST /v1/audio/transcriptions  body {}
  -> 501 {"error":{"code":501,"message":"The current model does not support audio input.","type":"not_supported_error"}}
POST /v1/chat/completions  body {"messages":[{"role":"user","content":[{"type":"input_audio","input_audio":{"data":"data:audio/wav;base64,UklGRg==","format":"wav"}}]}]}
  -> 500 {"error":{"code":500,"message":"audio input is not supported - hint: if this is unexpected, you may need to provide the mmproj","type":"server_error"}}
```

Run 1 on port 47656 gave identical bodies/statuses. Raw outputs: `out/ExecLoraAudio/repro_port47656.out`, `repro_port47657.out`, `server2.log`, `server3.log`; every command + exit code in `out/ExecLoraAudio/RUNS.txt`.

Notes on the 500 chat-completions path: the throw originates at server-common.cpp:1272 (`std::runtime_error("audio input is not supported - hint: …")`) inside `oaicompat_content_load_media`, which runs before `tokenize_input_subprompt`; `ex_wrapper` (server.cpp:56-91) catches `std::exception` as ERROR_TYPE_SERVER → 500 body with type `server_error`. The same string also appears in the server log (`got exception: {"error":…}`).

## Counter validation (scratch extract only)

Extract: `/fast/scratch/hyaku/kama-r26/ExecLoraAudio/counter_extract` (`git archive a23c0e042114016a909eb15173aa6df74b5b7eb0`; env GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE unset). Placeholder edits only inside the extract: wrote `registry/error-signatures-r26.json`, appended the `## Round-26 live error signatures` section (3 rows) to SKILL.md, appended S901-S903 to corpus/SOURCES.md.

Run:
```
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 900 python3 .ufo/waves/round-26/count-c1.py --out /fast/scratch/hyaku/kama-r26/ExecLoraAudio/counter_receipt.json
registered 3 counted 3 target 12 met False not-counted []     (exit code 0)
```

Receipt `counter_receipt.json` (copied to output dir): every row passes all 12 checks (id_unique, a_skill_row, b_long, b_new_at_base, c_source_row, d_source_pinned, d_in_source, e_error_shown, e_signature_seen, e_not_echoed, f_absent_from_baseline, g_distinct); observed statuses 400/501/500; channel excerpts contain the signatures verbatim. Baseline sha256 4c74acb8ce831335a9d706ab20a92afc1f4b8712ea6adcdb6d104d35d52a7131.

Pre-checks:
- Base absence (clause b): `git -C <lane> grep -F -q -e '<sig>' 1560e4d83f42b04f40336357de6f9637eafa0f4b -- SKILL.md corpus` returned 1 (absent) for each signature.
- Help/version (clause f): `llama-server --help` (rc 0) and `--version` (rc 0) do not contain any candidate signature.
- No signature occurs in any other candidate's channel text and no candidate trigger echoes a signature (clause g).

## Source citations (this round, pinned 704366d)

All quotes located in the lane's committed snapshot `.ufo/waves/round-26/sources/llama.cpp-704366d/` (sha256 matches `count-c1.py` SOURCE_SHA256: server-context.cpp dd1de0f2…, server-common.cpp b4f4aae7…). Fetch URLs pinned to commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad, accessed 2026-10-23:

- server-context.cpp:5998: `if (!body.is_array()) { res->error(format_error_response("Request body must be an array", ERROR_TYPE_INVALID_REQUEST));` (16 words) — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5998
- server-context.cpp:5655: `res->error(format_error_response("The current model does not support audio input.", ERROR_TYPE_NOT_SUPPORTED));` (15 words) — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5655
- server-common.cpp:1272: `throw std::runtime_error("audio input is not supported - hint: if this is unexpected, you may need to provide the mmproj");` (18 words) — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1272

## Files written

- `.ufo/waves/round-26/w1-build/out/ExecLoraAudio/candidates.json` (3 entries)
- `.ufo/waves/round-26/w1-build/out/ExecLoraAudio/RUNS.txt`
- `.ufo/waves/round-26/w1-build/out/ExecLoraAudio/repro_port47656.out`, `repro_port47657.out`, `server2.log`, `server3.log`, `counter_receipt.json`
- This advice file.

## Risks / notes for the L1

- Source rows S901-S903 are placeholders in the scratch extract only; final row ids must be integrated into `corpus/SOURCES.md` by the L1 with the real row text (URL, access date, quote, sha256), and SKILL.md rows built from `candidates.json` + final row ids.
- EXECLORAAUDIO-CHAT1 returns 500/`server_error` (an internal-exception path). It is a genuine, deterministic, observed fault on the pinned build with a verbatim pinned-source constant; if the lane prefers only "designed" 4xx errors, drop CHAT1 (the other two are 400/501 designed paths).
- `FR body must be an array` also applies to the same encode with a scalar body; I used an object body (cleanest non-array case). No valid-array trigger produces an error, and out-of-range adapter ids are silently ignored in `construct_lora_list` (no error string exists for bad ids) — noted, not registered.
- No server of mine remains: ports 47656-47659 confirmed free after killing both my PIDs; the other llama-server instances on 47605/47618/47624/47652 belong to other seats and were left untouched.
- No tool installs were needed or performed this run.
