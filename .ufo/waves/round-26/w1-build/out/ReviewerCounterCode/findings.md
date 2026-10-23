# ReviewerCounterCode findings: frozen C1 counter (count-c1.py at a23c0e04)

Verdict: the frozen counter is not a sound falsifier. With fabricated rows it counted 6 of 14 in one run: 2 rows were warnings attached to an unrelated fault, 2 were decoded request echoes, and 2 were echoes of file contents. Separately, any registry with more than 19 runnable rows cannot be evaluated at all (exit 2).

Counter identity: `sha256sum` of `.ufo/waves/round-26/count-c1.py` at a23c0e04 and of the scratch copy is `6501737c749926be9d6b37761175d76f89876976c46bd5951fc1a3520c796588`, which equals preregistration.json `counter_sha256`.

## How the evidence was produced

- Scratch extract: `git archive a23c0e042114016a909eb15173aa6df74b5b7eb0 | tar -x -C /fast/scratch/hyaku/kama-r26/ReviewerCounterCode/pristine`. Each run tree is a copy of it plus a registry, a SKILL.md section and SOURCES rows S951-S990. All of these come from `gen.py` (copied here). The rows are falsifier fixtures, not claim data.
- Every counter run: `cd <tree> && flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 900 python3 .ufo/waves/round-26/count-c1.py --out ../<run>.json`, with optional `env VAR=...` in front. Receipts are in `receipts/` and registries in `registries/`.
- The counter itself used ports 47560-47579. It started no other servers. After the last run, `pgrep -af llama-server | grep -E '475[67][0-9]'` printed nothing (exit 1) and `ss -ltn | grep -cE ':475[67][0-9]\b'` printed 0.
- No tools were installed or updated.

| Run | Rows | Printed line | Exit |
|---|---|---|---|
| runA | RA01-RA14 | `registered 14 counted 6 ... not-counted ['RA02:e_signature_seen', 'RA04:g_distinct', 'RA09:g_distinct', 'RA10:a_skill_row,g_distinct', 'RA11:a_skill_row,g_distinct', 'RA12:e_signature_seen', 'RA13:e_signature_seen', 'RA14:e_signature_seen']` | 0 |
| runB | RB01-RB20 | `could-not-evaluate: no free port in 47560-47579` (receipt: 19 rows evaluated) | 2 |
| runC | RC01, RC02 | `could-not-evaluate: RC02: port did not close` | 2 |
| runD | RD01 (no `channel` key) | `KeyError: 'channel'` traceback at count-c1.py:279, no receipt written | 1 |
| runE | RE04, RE01, RE03 | `registered 3 counted 1 ... not-counted ['RE01:g_distinct', 'RE03:g_distinct']` | 0 |
| runF-plain | RF01 | `registered 1 counted 1` | 0 |
| runF-envdefrag | RF01, with `LLAMA_ARG_DEFRAG_THOLD=0.1` | `registered 1 counted 0 ... not-counted ['RF01:f_absent_from_baseline']` | 0 |
| runF-envapikey | RF01, with `LLAMA_ARG_API_KEY=dummy-not-a-secret` | `registered 1 counted 1` | 0 |
| runF-proxy | RF01, with `http_proxy=http://127.0.0.1:9` | `could-not-evaluate: baseline server never became healthy` | 2 |

## Findings by severity

### F1 HIGH: a warning printed on an unrelated failure counts as an error signature, so one fault yields many rows

Defect: for startup rows, clause (e) only checks that the process exits non-zero and that the signature appears somewhere in stdout+stderr (count-c1.py:279-284, 381-383). Clause (f) checks only one default-argument baseline (count-c1.py:229-254). As a result, any line printed because of an extra argument counts, as long as some other fault makes the process exit non-zero. Clause (g) does not stop this, because each warning row has a different trigger and different signature text.

Row set (runA, model `missing`, so every row has the same missing-model fault):
- RA01: args `["-dt","0.1"]`, signature `--defrag-thold is deprecated and no longer necessary to specify` (arg.cpp:2542, a `LOG_WRN`). Result: **counted**. The log starts with `0.00.000.374 W DEPRECATED: --defrag-thold is deprecated ...` and exits with 1.
- RA03: args `["--embedding","-b","1024","-ub","256"]`, signature `embeddings enabled with n_batch (` (server.cpp:164, `SRV_WRN`). Result: **counted**. The log shows `W srv llama_server: embeddings enabled with n_batch (1024) > n_ubatch (256)` and exits with 1.
- RA04: the genuine missing-model row, signature `failed to load model` (common.cpp:1423). Result: **not counted** (`g_distinct`), because RA01 and RA03 already counted and their logs contain the same missing-model error text.

Both counted rows are warning-level (`W`) lines, and neither caused the exit. The counter cannot tell them apart from the error that did (`E ... exiting due to model loading error`, in receipts/runA-log_file-bypass.txt).

[INFERENCE] Any argument-dependent warning works the same way. RA13 (`-sm none`) and RA14 (`-ngl 1`) did not reproduce on this host, because the RPC backend makes `llama_supports_gpu_offload()` return true (llama.cpp:102-108).

Fix proposal: give each startup row its own healthy control. Run the same argv with the `fixture` model and a free port, and with any registry-declared `fault_args` removed. Refuse the row if the signature appears in that control's output. Also require the signature to fall on an error-level line (log level `E`, or the untimestamped `error:` lines that argument parsing prints).

### F2 HIGH: request echo check is bypassed with JSON unicode escapes

Defect: `e_not_echoed` compares the signature with the raw registry text of the request (count-c1.py:369-374, 384). The server decodes JSON escapes before it echoes a field. server-common.cpp:1375 echoes `response_format.type` in its 400 message: `"response_format type must be one of \"text\" or \"json_object\", but got: " + response_type`. Because of this, any pinned-source literal can be "reproduced" from a request. The registry stores the literal with its first character written as `\u00XX`, so the raw text never contains it.

Row set (runA, http `POST /v1/chat/completions`, string body `{"messages":[{"role":"user","content":"Hi"}],"response_format":{"type":"\u0043annot run multiple aLoRAs in a single request"}}`):
- RA05: signature `Cannot run multiple aLoRAs in a single request` (server-context.cpp:1877). Result: **counted**, with status 400 and body `{"error":{"code":400,"message":"response_format type must be one of \"text\" or \"json_object\", but got: Cannot run multiple aLoRAs in a single request","type":"invalid_request_error"}}`.
- RA06: signature `failed to reload model after sleeping` (server-context.cpp:1076, a `GGML_ABORT`, so it is never an HTTP error). Result: **counted**, with the same pattern.

There is no limit on how many rows this produces. Every row has a distinct body and therefore a distinct trigger, and no row's signature occurs in another row's text.

Fix proposal: build the comparison text from decoded request content as well as raw text. For a string body, parse it with `json.loads` and add every decoded string key and value. Also add `urllib.parse.unquote(path)`, and header values. Refuse the row if the signature occurs in any of these, or if any decoded request string of at least 8 bytes occurs inside the signature's line in the channel text.

### F3 HIGH: request echo check is bypassed when arguments name a file whose contents reach the log

Defect: the echo check covers argument strings only, not the contents of files those arguments name. The chat-template parser prints the whole template when it rejects it.

Row set (runA, startup, model `fixture`):
- RA07: args `["--chat-template-file", ".../fixtures/tmpl-if.jinja"]`. The file contains `{% if %}Restored prompt does not fit in the slot context`, and the signature is `Restored prompt does not fit in the slot context` (server-context.cpp:3091). Result: **counted**, exit 1. The log shows `E error: the supplied chat template is not supported: {% if %}Restored prompt does not fit in the slot context`.
- RA08: same pattern with tmpl-endfor.jinja, signature `No available space in KV cache or invalid slot save file` (server-context.cpp:3084). Result: **counted**.

[INFERENCE] Other arguments that read files could carry the same bypass, for example `-f`, `--grammar-file`, `-jf`, `--models-preset`, `--lora` and `--mmproj`. Only `--chat-template-file` was exercised.

Fix proposal: add the contents of every argument value that is an existing file to the comparison text. Alternatively, allow file-path arguments only when they point at counter-generated fixtures.

### F4 HIGH: the count cannot be evaluated once 20 rows pass the static checks (port exhaustion)

Defect: `pick_port` adds each port to `used` and never removes it (count-c1.py:148-153, 230, 262). With 20 ports, the baseline takes one, so at most 19 triggers can run. The 20th run raises `CannotEvaluate`, and the whole receipt becomes could-not-evaluate.

Row set: runB has 20 genuine-shape startup rows (RB01-RB20, missing model, `-t 1` to `-t 20`). The receipt holds 19 evaluated rows, then `could-not-evaluate: no free port in 47560-47579`, exit 2.

Impact: the lane's dispatch roster has more than 20 executor seats. If more than 19 rows pass clauses (a)-(d), the claim has no score at all.

Fix proposal: after `teardown` confirms the port is closed, call `used.discard(port)`. Alternatively, drop `used` and probe the ports again for each run.

### F5 MEDIUM: one bad row aborts the whole count

Defect:
- Forbidden arguments return a result without `port_closed` (count-c1.py:265-266), and the caller then raises `CannotEvaluate("port did not close")` (count-c1.py:379-380).
- A missing `channel` or `request` key raises `KeyError` (count-c1.py:279, 291). This exits 1, which is not one of the documented exit codes, and writes no receipt.
- An unknown `model` kind raises `CannotEvaluate` (count-c1.py:222).

Row set:
- runC: RC01 (a valid missing-model row) followed by RC02 with args `["--path","/tmp"]` gives `could-not-evaluate: RC02: port did not close`, exit 2. The message names the wrong cause.
- runD: RD01 without `channel` gives a traceback at line 279 and exit 1, with no `--out` file written.

Fix proposal: validate each entry's schema before choosing a port. Record schema or forbidden-argument failures as row-level check failures, for example `schema_ok=false` or `args_allowed=false`. Keep `CannotEvaluate` for host-level failures only.

### F6 MEDIUM: the forbidden-argument list can be bypassed

Defect: arg.cpp:826-827 rewrites `_` to `-` in every `--` argument before looking it up. `FORBIDDEN_ARGS` (count-c1.py:78-79) is matched exactly. The list also misses the `-hfr` alias of `--hf-repo` (arg.cpp:3074) and `-hff`/`--hf-file` (arg.cpp:3084).

Row set: runA RA09 used args `["--log_file", "<scratch>/runA-log_file-bypass.txt"]`. The forbidden check let it through, and the server wrote a 1502-byte log file (copied to receipts/runA-log_file-bypass.txt). [INFERENCE] `--hf_repo` or `-hfr` would make the counter download from the network. This was not run.

Fix proposal: before checking, normalise `--` arguments with `_` to `-`, and also split `--x=y` forms. Better still, use an allowlist of argument names taken from arg.cpp at 704366d.

### F7 HIGH (integrity): the server pin covers a 17,864-byte launcher, not the server code

Defect: count-c1.py:320 hashes only `~/.local/bin/llama-server`, which resolves to `/home/vgpnk/.local/opt/llama-b11755/llama-server` (17,864 bytes). `readelf -d` shows `RUNPATH [$ORIGIN]`, and `ldd` resolves these libraries from that directory: `libllama-server-impl.so` (7,671,544 bytes, holding the server code), `libllama-common.so.0`, `libllama.so.0`, `libmtmd.so.0`, `libggml.so.0` and `libggml-base.so.0`. ggml also loads `libggml-cpu-*.so` and `libggml-rpc.so` at run time from the same directory. None of these files is hashed. Popen also inherits `LD_LIBRARY_PATH` and `LD_PRELOAD`, which take precedence over the RUNPATH.

[INFERENCE] The no-reader control (fake binary, "could-not-evaluate (server sha pin)") therefore covers only a replaced launcher. A replaced library, or one injected through the environment, could print any pinned literal. This was not exercised, because writing `~/.local/opt` is out of bounds for this seat.

Fix proposal: pin the sha256 of every regular file in `~/.local/opt/llama-b11755/` that the server loads, including the dynamically loaded backends, and start the server with `LD_*` removed from the environment.

### F8 MEDIUM: results depend on the caller's environment

Defect: Popen and `subprocess.run` inherit the full environment (count-c1.py:176-177, 248-249). arg.cpp:795-808 applies `LLAMA_ARG_*` variables, and urllib honours `http_proxy`.

Row set:
- RF01 counts 1 in a plain environment (runF-plain) and 0 with `LLAMA_ARG_DEFRAG_THOLD=0.1` (runF-envdefrag, `f_absent_from_baseline`).
- `http_proxy=http://127.0.0.1:9` makes the baseline never become healthy, so the count is could-not-evaluate (runF-proxy, exit 2).
- `LLAMA_ARG_API_KEY=dummy-not-a-secret` did not change the result (runF-envapikey, counted 1).

Fix proposal: pass a fixed minimal environment (`PATH=/usr/bin`, `HOME`, `LANG=C`) to every child process. Build urllib requests with `build_opener(ProxyHandler({}))`. Record the environment in the receipt.

### F9 MEDIUM: clause (g) is greedy, so the result depends on registry order

Defect: (g) compares each row only with rows already counted (count-c1.py:392-395). The same set of overlapping rows therefore scores differently depending on order.

Row set: runA, with the warning rows first, counted RA01 and RA03 and blocked the genuine RA04. runE has the same three triggers with the genuine row first: it counted RE04 and blocked RE01 and RE03 (`registered 3 counted 1`). The same fault scored 2 in one order and 1 in the other. The preregistered L1 generic2 control shows the same effect: G26-05 blocked G26-08.

Fix proposal: once F1 is fixed, make (g) independent of order. Build the overlap graph among rows that pass (a)-(f) and count one row per connected component, choosing the lowest id. Alternatively, sort by id and document that rule.

### F10 MEDIUM: markdown row matching rejects genuine rows

Defect: count-c1.py:131-139 and 353-356 have three problems:
- The id must be bare in the first cell.
- Any line starting with `#` ends the section, including `###` subheadings and `#` lines inside fenced code.
- The signature is matched against the raw line. A signature containing `|` must be escaped as `\|` in a GFM table cell, so it never matches.

Row set:
- runA RA10 has its id written in backticks (`` | `RA10` | ``), and fails `a_skill_row`.
- runA RA11 is under `### Rows under a subheading of the same section`, and fails `a_skill_row`.

[INFERENCE] A signature containing a pipe can never pass (a) in a table that renders correctly. The only pinned message of at least 20 bytes that contains `|` is server.cpp:87, `got another exception: %s | while handling exception: %s`; the survey listed all four pipe-containing literals.

Fix proposal:
- End the section only at headings of level 2 or higher, and skip fenced blocks.
- Split cells on unescaped `|` and strip backticks and `*` from the id cell.
- Compare the signature with the row after replacing `\|` with `|`.

### F11 LOW: clause (c) accepts a SOURCES row that names a different file

Defect: `sfile in row_text` (count-c1.py:361) is a substring test. The file name `llama.cpp` occurs in every `github.com/ggml-org/llama.cpp/...` URL.

Row set: runA RA12 has `source.file = "llama.cpp"`, but its SOURCES row S962 names only `tools/server/server-context.cpp`. Even so, `c_source_row` is true; RA12 failed only `e_signature_seen`.

Fix proposal: require the 704366d URL path of the pinned file, for example `/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama.cpp#L`, using a fixed map from file name to path.

### F12 LOW: one registry string must match both the source's C escaping and the channel's escaping

Defect: (d) matches raw source bytes, while (e) matches log text (unescaped) or JSON body text. For http the two forms happen to agree: `\"` in C and `\"` in JSON (runA RA05's body carries `\"text\"`, as server-common.cpp:1375 does). For startup they do not. arg.cpp:876 has `error while handling argument \"`, but the log prints `error while handling argument "--connect-code": ...` (runA RA02 excerpt). A startup signature that spans a quote, a `%%`, or any other escape can therefore never count.

Fix proposal: decode the C string literal for (d). Compare the decoded form with the startup log, and the JSON-encoded form with the http body; alternatively, parse the body and match `error.message`.

### F13 INFO: startup exit semantics (checked; no row demonstrates a defect)

- `rc != 0` includes negative return codes, so death by a signal (for example SIGABRT from `GGML_ABORT`) counts as "exits non-zero". The predicate does not say whether a signal counts as an exit. Recommend recording `signal=-rc` separately in the receipt. [INFERENCE] No startup row in this review died by signal.
- No error path exits 0. The `exit(0)` sites in arg.cpp are 1306 (usage), 1310 (completion), 1458 (`--version`), 1470 (`--cache-list`) and 2754 (`--list-devices`), and all are informational. Argument errors throw (arg.cpp:830, 875-878), and main returns 1 (server.cpp:113-114).

### F14 LOW [INFERENCE]: teardown and port races

- `teardown` signals the process group only while the leader is still alive (count-c1.py:181). A child of a leader that has already exited (`server_child`, or `llama-connect` from `--connect`, server.cpp:549) would survive, and only the main port is checked.
- `port_free` uses a connect probe (count-c1.py:142-145), which does not see a socket that is bound but not listening. That would make a genuine http row fail with `ready False`.
- Neither case was observed.

## Checked and clean

- git grep at base. `survey.py` checked 2025 string-literal occurrences in the 13 pinned sources against the base tree. It found 0 literals that `git grep -F` reports absent but that occur at base after whitespace normalisation (`receipts/survey.json`, `"wrapped": []`). `git grep` also matches binary files, and `-q` returns 0 on a match, so binary corpus files cannot hide a match. The pathspecs `SKILL.md` and `corpus` resolve from the repository root through `-C`.
- The pinned source snapshot. `sha256sum` of all 13 files equals `SOURCE_SHA256`.
- No llama-server or counter process from this seat remains, and the ports are closed.

## Files written
- `.ufo/waves/round-26/w1-build/out/ReviewerCounterCode/findings.md` (this file)
- `.ufo/waves/round-26/w1-build/out/ReviewerCounterCode/gen.py`, `survey.py`
- `.ufo/waves/round-26/w1-build/out/ReviewerCounterCode/fixtures/tmpl-if.jinja`, `tmpl-endfor.jinja`
- `.ufo/waves/round-26/w1-build/out/ReviewerCounterCode/registries/run{A,B,C,D,E,F}.registry.json`
- `.ufo/waves/round-26/w1-build/out/ReviewerCounterCode/receipts/` (runA, runB, runC, runE, runF-plain, runF-envdefrag, runF-envapikey `.json` and `.out`; runD.out; runF-proxy.out; runA-log_file-bypass.txt; survey.json)
- `.ufo/waves/round-26/w1-build/advice/ReviewerCounterCode.md`
- Scratch: `/fast/scratch/hyaku/kama-r26/ReviewerCounterCode/` (pristine, base, run trees)
