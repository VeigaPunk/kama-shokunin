VERDICT: partial — all five current bindings match pinned/upstream bytes, but the gate accepts forged binding metadata and teardown citations omit the callback body.

## Scope attacked
Receipt v2 `source_binding` in `.ufo/waves/round-17/live/receipt-1.json`, its producer and gate, the pinned llama.cpp source tree, and row mappings to S036/S042/S043.

## Findings

### Medium — receipt gate does not validate `source_binding`
`tools/kama-llamacpp-live.py:840-841` says the literal span lets “the gate re-derive span_sha256 without network access.” The landed `tests/llamacpp-live/check-receipt.py:80-92` enumerates the 11 v2 checks, with no source-binding obligation; literal search for `source_binding` in that file returned no matches. The round-17 build note explicitly records the gate-level obligation as “NOT implemented” (`.ufo/waves/round-17/build/advice/C2ReceiptGate.md:37`).

Reproduction on a clone of commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3`: changed entry 0 to `row=S999`, `commit=bad`, `path=not-upstream`, `lines=[1,1]`, zero `file_sha256`, `span_text="forged span\n"`, and all-`f` `span_sha256`; then ran the gate. It printed `VALID /tmp/KamaR17.SourceBindingCheck-corrupt.json` and exited 0. Thus current receipt values are independently correct (see table), but the gate gives no guarantee against later mis-citation or alteration of this block.

### Low — teardown binding omits the callback-to-shutdown bridge [INFERENCE]
`tools/kama-llamacpp-live.py:118-128` describes SIGTERM installation, `shutdown_handler`, and the `start_loop()` return path. Its binding literals (`:902-927`) cover `server.cpp` lines 529-534, 519-523, and 575-590, but not lines 29-38. In the pinned source, `signal_handler` calls `shutdown_handler(signal)` at line 37 (and the second signal exits 1 at line 34; `server.cpp:29-38`). That missing span is the code-level bridge from the installed callback to the cited shutdown handler. S043’s registry anchor does include `signal_handler` lines 26-38 (`corpus/SOURCES.md:55`), so this is a completeness gap in the receipt-bound spans, not a false hash or false range. Adding the handler span would make the transition independently bound.

## Recomputed bindings and row mapping
For each row below, I hashed the exact 1-based inclusive lines as raw UTF-8 bytes and compared those bytes with `span_text.encode('utf-8')`. Both equality and the receipt’s `span_sha256` matched. Each whole-file digest also matched the receipt and the raw URL at commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`.

| Check | Receipt row → registry row | File lines | Recomputed `span_sha256` |
|---|---|---:|---|
| `health_ready` | null → S042 | `server-context.cpp:5288-5299` | `2ff50edd63f4b7a37ccfcd21210c29f781f777f010eb6e2963ed8585ad3447dd` |
| `loading_envelope_graded` | S036 | `server-http.cpp:314-325` | `4c5aac23af4cacc39abc525dceeed59f8e95e8584771e6e1a84a752c719da775` |
| `teardown_graceful` | null → S043 | `server.cpp:529-534` | `f14a9b67bce667741f028a3fb33239b96281c21de0688a14e3a66da251b1e163` |
| `teardown_graceful` | null → S043 | `server.cpp:519-523` | `97408c516bf5c805b12ca6fa407956473489277ec626b41511e3abe6e2510a70` |
| `teardown_graceful` | null → S043 | `server.cpp:575-590` | `d0f09fae6947f25b42ccf00ef09231c9e8f9bf46b5499d9e1f070a58d8ad163d` |

Content checks: `server-context.cpp:5297` contains `res->ok({{"status", "ok"}});`; `:4868-4871` sets status 200 and serializes the JSON. `server-http.cpp:314-325` contains status 503, the `Loading model`/`unavailable_error`/503 JSON envelope, and `return false`. The three teardown ranges contain the SIGTERM registration, `ctx_server.terminate()`, and blocking loop/cleanup/`return 0` respectively. The S036 range and digest match its `corpus/SOURCES.md:48` anchor. The null mappings are accurately documented in `corpus/lessons/round-17.md:76-79`: health → S042 (`SOURCES.md:54`), teardown → S043 (`SOURCES.md:55`). All five receipt entries name check IDs present in `.checks`; the `source_binding` arrays in receipts 1, 2, and 3 are identical.

Whole-file SHA-256 checks against raw upstream URLs also matched:
- `server-context.cpp`: `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329`
- `server-http.cpp`: `24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb`
- `server.cpp`: `2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4`

## Commands and verification
- Upstream fetch/hash, exit 0:
  `mkdir -p /tmp/KamaR17.SourceBindingCheck-src && cd /tmp/KamaR17.SourceBindingCheck-src && curl -fsSL --max-time 60 -o server-context.cpp https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp && curl -fsSL --max-time 60 -o server-http.cpp https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-http.cpp && curl -fsSL --max-time 60 -o server.cpp https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp && sha256sum server-context.cpp server-http.cpp server.cpp`
- Required clone/checkout, exit 0:
  `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17.SourceBindingCheck-clone && git -C /tmp/KamaR17.SourceBindingCheck-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3`
- Corrupted-binding gate probe in that clone (`PYTHONDONTWRITEBYTECODE=1 python3 /tmp/KamaR17.SourceBindingCheck-clone/tests/llamacpp-live/check-receipt.py /tmp/KamaR17.SourceBindingCheck-corrupt.json`), gate exit 0, output `VALID /tmp/KamaR17.SourceBindingCheck-corrupt.json`.
- In-memory Python byte-slice/hash recomputation: corrected run exited 0 and produced the five matching digests above. Initial attempt exited 1 with `TypeError: sequence item 0: expected str instance, bytes found`; no results from that attempt were used.
- Scratch cleanup: `rm -rf /tmp/KamaR17.SourceBindingCheck-src /tmp/KamaR17.SourceBindingCheck-clone /tmp/KamaR17.SourceBindingCheck-corrupt.json`, exit 0.
- LSP unavailable: `read xd://lsp` returned “No such tool.” No LSP references/definition/diagnostics were available; literal grep was used only to check field-name presence, and the corrupted-receipt gate probe establishes the gate behavior.
- No installs. No lane gate, tests, or runtime were run; the gate probe ran only from the required temporary clone.