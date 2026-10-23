ATTACK SKILL.md '## Round-26 live error signatures' prose (header, cited-not-absorbed note, observed-not-registered paragraph): BREAKS

Two statements are false: the reason given for not registering the SIGSEGV, and "beyond one example". Three more overreach or leave out facts that change how a reader uses the section. The other 19 statements hold. The table rows are out of scope except where the prose makes a claim about them.

Seat: KamaR26.ReviewerSkillProse (reviewer, wave 2 FALSIFY, round 26). Tree read: lane working copy at landed tip f4066979 (SKILL.md lines 1062-1111). No server started (this seat has no port block), counter not run, no tools installed.

## Findings by severity

### F-1 (high, false statement) The SIGSEGV reason contradicts the counter and row E26-17

- Claim, SKILL.md:1110-1111: the crash was "not registered, because the counter needs a status or a clean non-zero exit."
- Counter, `.ufo/waves/round-26/count-c1.py:279-285`: for the startup channel, `rc = proc.wait(timeout=STARTUP_WAIT)` and then `out["error_shown"] = rc is not None and rc != 0`. A death by signal gives a negative `rc` and passes. Nothing requires a "clean" exit.
- Receipt, `.ufo/waves/round-26/final/c1-tip-receipt.json`: row E26-17 has `counted True` and `observed.exit -6`, which is SIGABRT. That row is itself an unclean signal death that counted. Wave-1 evidence agrees: `w1-build/out/ExecBadArgs/RUNS.txt:75` says "ctx-size row exit -6 (SIGABRT)".
- Actual reason: the crash happens after the server is healthy, while it serves a request (`w1-build/out/ExecEmbeddingsInput/RUNS.txt:17-20`: `/health -> 200`, then `POST /completion -> 000`). The http channel needs a response with status >= 400. When the connection dies, `http()` returns -1 (`count-c1.py:170-171`), so `error_shown` is False (`:296`). The startup channel sends no request, so this server would still be alive at 30 s (`rc None`). Neither channel can see the crash.
- Smallest correction: "not registered: the crash needs a request to a server that is already healthy. The counter's http channel needs an HTTP status >= 400, and its startup channel sends no request, so neither channel can observe it."

### F-2 (medium, false statement) "per-flag argument validation messages beyond one example": no such example is registered

- Claim, SKILL.md:1107-1108.
- Registry `registry/error-signatures-r26.json`: none of E26-01..E26-17 cites `arg.cpp`. The startup rows are E26-15 and E26-16 (`gguf.cpp`) and E26-17 (`llama-context.cpp`).
- E26-17 is not argument validation. Its own row (SKILL.md:1100) says a negative context "passes argument parsing".
- The unknown-flag message `error: invalid argument: ` is in the "already held" group (SKILL.md:1105), and it reports an unknown flag, not a per-flag value check.
- Source of the miscount: `w1-build/advice/ExecBadArgs.md:14-25` delivered 10 per-flag value messages (`--parallel 0`, `--flash-attn bogus`, `--repeat-penalty 0`, `--sleep-idle-seconds 0`, `--cache-type-k bogus`, `--log-colors bogus`, `--reasoning bogus`, `--presence-penalty nan`, `--frequency-penalty inf`, `--checkpoint-min-step -1`). `corpus/lessons/round-26.md:63` calls them "nine further", which implies one was registered. None was.
- Smallest correction: "...and ten per-flag argument value messages (for example `error: invalid value for n_parallel` for `--parallel 0`), held back by the counter's 19-row limit." Change "nine further" to "ten" in round-26.md:63 to match.

### F-3 (medium, misleading by omission) The paragraph leaves out the largest held-back group and the main reason for it

- SKILL.md:1102-1108 lists four reasons: already held, error-type labels, router-only, per-flag. The lesson's §Gate table, which the paragraph points to, also lists:
  - nine or more live-confirmed embeddings, rerank and control messages (`round-26.md:64`);
  - 17 chat-completions validation messages, "live-confirmed twice each and counted 17 of 17 in the seat's scratch run" (`round-26.md:65`).
- Both groups were held back only by "the 19-row evaluation limit" (ReviewerCounterCode F4). That is a counter capacity limit, not a judgment of the messages' value.
- A reader of SKILL.md alone would conclude that every observed signature was either registered or rejected on merit. That understates coverage of the chat-completions validation messages by about 26 genuine signatures.
- Smallest correction: add "and about 26 genuine, live-confirmed request-validation messages (embeddings, rerank and chat-completions), held back only because the counter can evaluate at most 19 rows (ReviewerCounterCode F4); candidates for a later round."

### F-4 (low, overreach) "emits on the lane fixture (`stories260K.gguf` ...)" does not hold for every row

- Claim, SKILL.md:1064-1065: "Each row is an error that llama-server ... emits on the lane fixture (`stories260K.gguf`, ...)".
- Registry: E26-15 uses `"model": "missing"`, which `count-c1.py:216-217` maps to `/nonexistent/kama-r26/missing.gguf`. E26-16 uses `"model": "junk"`, a 58-byte text file (`count-c1.py:218-221`). Neither row runs on the fixture.
- The same overreach appears at SKILL.md:1071-1072 ("relaunches every trigger against the sha256-pinned binary and model"). Also, the counter launches a row only when all static checks pass (`count-c1.py:375-390`, `skipped_run`). At the tip all 17 passed, so this second point has no effect today.
- Smallest correction: "...emits on the lane fixture, or, for E26-15 and E26-16, on a missing path and a non-GGUF file..." and "relaunches every trigger whose static checks pass against the sha256-pinned binary (and the fixture model where the row uses it)".

### F-5 (low, unclear wording) The `\"` sentence conflates two escapes and does not say where to match

- Claim, SKILL.md:1068-1069: "Inside `http body` signatures, `\"` is the JSON escape the server sends, byte for byte as in the C++ source."
- The bytes do match. Source line 6151 and the receipt body both contain `\"input\"`, and I confirmed the signature is in the raw body.
- But in C++, `\"` is a C string escape that puts a bare `"` into the message. The server's JSON writer then escapes it again. The two byte strings match by coincidence, not because they are the same escape.
- Practical effect: after `json.loads(body)["error"]["message"]`, the signature does not match. Observed: `E26-07 sig_in_raw= True sig_in_decoded_message= False`, and the same for E26-14. A consumer that matches the parsed message field will miss both rows.
- Smallest correction: "Match http signatures against the raw response body. Rows E26-07 and E26-14 contain `\"`, which appears in the raw body (the server's JSON escape) and in the C++ source (a C escape), but not in the parsed `error.message` field, which holds a plain `"`."

### F-6 (low, omission against the cited connector) The cited-not-absorbed note drops kumitate

- The note (SKILL.md:1077-1080) cites `w1-build/advice/ConnectorSiblingOverlap.md`. The connector's proposed move (`:43-45`) asks for a note "naming the four sibling owners", including "kumitate omp dispatch" (§3, `kumitate-shokunin/SKILL.md:437-441`: 429/401/403/400 mapped to error types).
- The note names three owners. Kumitate is relevant here because the closing paragraph discusses error-type labels (`invalid_request_error`, `authentication_error`), and kumitate owns that route-failure taxonomy.
- The connector citation sits after the tsukuroi clause only, so it reads as sourcing tsukuroi alone.
- Smallest correction: insert "omp route, fallback and error-type taxonomy is kumitate's;" and move the connector citation to the end of the sentence, covering all owners.

### F-7 (low, wording) The SIGSEGV sentence omits that it happened once and that the request was ordinary, and implies an untested condition

- Holds as observed: `RUNS.txt:15-21`, `server_probe1.log` ends `processing task, is_child = 0` / `timeout: the monitored command dumped core`, and `coredumpctl list` shows `Fri 2026-10-23 00:36:17 -03 3310053 ... SIGSEGV ... llama-b11755/llama-server`. This is the only SIGSEGV among the llama-server dumps; the other 11 are SIGABRT.
- Caveats:
  - It was seen once and never re-run. Probes 3 and 4 ran default-pooling servers but sent only `/v1/embeddings` (`RUNS.txt:34-45`). The wave-1 advice calls it "reproducible" (`ExecEmbeddingsInput.md:57`), which has no support; SKILL.md correctly does not repeat that.
  - The request was an ordinary completion, `{"prompt": "Once upon a time", "n_predict": 4}` (scratch `req_completion.json`). This is the operationally important part, and SKILL.md does not say it.
  - "and no pooling override" implies that pooling matters. No `/completion` request was sent to the `--pooling mean` server (probe 2), so that contrast is untested.
- Smallest correction: "Also observed once on this build (not re-run): a server launched with `--embeddings` (default pooling; other pooling settings not tried) crashed with SIGSEGV on an ordinary `POST /completion` ..."

### F-8 (low, wording) E26-17's "exit status 134" is the shell's encoding, not the process exit status

- Under the header claim "exit statuses were observed on this build only" (SKILL.md:1075), row E26-17 says "exit status 134, SIGABRT, observed".
- 134 is `$?` for a child that died by signal 6 under `timeout` in a shell (`ExecBadArgs/RUNS.txt:47-48`). The counter recorded `-6` (tip receipt), and a service manager reports status 6/ABRT.
- Smallest correction: "process killed by SIGABRT (signal 6; shell `$?` 134, Python returncode -6)".

## Statement ledger (every factual statement in scope)

| # | statement (SKILL.md line) | verdict | evidence |
|---|---|---|---|
| 1 | heading "(b11755 fixture, owner: kama)" (1062) | holds | binary sha256 `b6a31a8e...cd804` (this seat: `sha256sum ~/.local/bin/llama-server`); `ExecBadArgs/raw/version.txt`: `version: 0.7.0-dev (build 11755, commit 704366d76)` |
| 2 | "llama-server build 11755 (commit 704366d76)" (1064) | holds | same as row 1 |
| 3 | "emits on the lane fixture (`stories260K.gguf` ...)" (1064-1065) | overreach | F-4: E26-15 uses a missing path, E26-16 a junk file |
| 4 | "loopback, one child at a time" (1065) | holds | `count-c1.py:75` HOST 127.0.0.1; one launch, then teardown before the next (`:261-305`, `:377-380`) |
| 5 | signature is a verbatim substring of the observed output and of the pinned source line named by the SOURCES row (1066-1068) | holds | this seat: 17/17 signatures sit on the exact line in the row's URL anchor, once per file; files fetched fresh at 704366d: sha256 of server-context.cpp, server-common.cpp, gguf.cpp and llama-context.cpp equal the lane snapshot and `SOURCE_SHA256`; tip receipt: all 17 `e_signature_seen`. The counter checks the file, not the line (`count-c1.py:365`), so the line-level part was verified here, not by the counter |
| 6 | `\"` is the JSON escape the server sends, byte for byte as in the C++ source (1068-1069) | holds as bytes, unclear | F-5 |
| 7 | re-derivation command relaunches every trigger against the pinned binary and model (1070-1072) | partly holds | binary pin `count-c1.py:320-321` holds; model and "every" overreach (F-4) |
| 8 | it prints `counted N` (1072) | holds (shortened) | actual line: `registered 17 counted 17 target 12 met True not-counted []` (`final/c1-tip.out`) |
| 9 | frozen predicate is in preregistration.json; registry path (1072-1074) | holds | lane `count-c1.py` sha256 `6501737c...c796588` equals `preregistration.json` `counter_sha256` and `final/tip-counter-sha.txt` |
| 10 | "Other builds: re-observe before relying on a row" (1074-1075) | holds (guidance) | n/a |
| 11 | status codes and exit statuses observed on this build only (1075) | holds | tip receipt statuses match every row: 501 for E26-01/02/04/05/08/09/12; 400 for 03/06/07/11/14; 500 for 10/13; exit 1 for 15/16; E26-17 -6 (F-8 wording) |
| 12 | API-key and authentication errors are kagi's (1077) | holds | `ConnectorSiblingOverlap.md:5-6, 21-26` |
| 13 | the lane already holds `Invalid API Key` in "Historical error signatures" (1078) | holds | SKILL.md:181 (as a historical binary string, not a live error) |
| 14 | served-model quality is kengaku's (1079) | holds | connector §1; SKILL.md:29 ("kama never answers 'is the model good'") |
| 15 | OS and service-manager errors are tsukuroi's (1079-1080) | holds | connector §4 |
| 16 | the note reflects the connector (implied by the citation) (1080) | incomplete | F-6: kumitate dropped |
| 17 | reasons are in `corpus/lessons/round-26.md` §Gate (1102-1103) | holds | rejected-candidates table at round-26.md:57-68, under `## Gate` (line 11) |
| 18 | the four strings were already held in earlier wave evidence (1103-1105) | holds | `git archive 1560e4d8` extract, `rg -uu -lF`, counting wave files outside source snapshots: metrics 6 (e.g. `.ufo/waves/round-16/falsify/advice/ScoutMetricsSource.md`), context size 13 (round-25), bind 1 (`round-18/build/advice/ScoutLlamaArgParse.md:67`, live observation O2), invalid argument 4 (ScoutLlamaArgParse.md:66,71; round-25 `CriticLearningBar/fit-params.out`). Note: E26-16's source line also appears at base, as a source excerpt rather than an observation (`round-20/build/out/SrcGgufPyReader/source-excerpts.txt:209`). The standard is consistent only if "held" means observed output; the prose does not say so |
| 19 | error-type labels `authentication_error`, `invalid_request_error` (1105-1106) | holds | round-26.md:62 |
| 20 | router-only model errors cannot be reached by a single-model launch (1106-1107) | holds | `w1-build/advice/ExecRouterModels.md:60-63` (`-m` forces single-model mode, `server.cpp:152-154`); round-26.md:68 |
| 21 | per-flag argument validation messages "beyond one example" (1107-1108) | false | F-2 |
| 22 | the list of unregistered groups is complete (implied) (1102-1108) | misleading by omission | F-3 |
| 23 | SIGSEGV with `--embeddings` while serving `/completion`, wave-1 ExecEmbeddingsInput RUNS.txt (1108-1110) | holds, imprecise | F-7: coredumpctl pid 3310053; seen once |
| 24 | not registered because the counter needs a status or a clean non-zero exit (1110-1111) | false | F-1 |

## Residual risk and verification gaps

- I did not re-run the counter or any trigger; this seat has no port block. The statuses and exits above are read from `final/c1-tip-receipt.json` (tree 7e5ff9b5), not reproduced. The prose was read at f4066979; I did not diff the section between 7e5ff9b5 and f4066979.
- The SIGSEGV was not reproduced, by wave 1 or by this seat.
- The `lsp` device does not apply: the targets are Markdown, JSON and receipts. Cross-references were checked by literal search, which is the stated fallback.
- The F-3 count of about 26 is the lesson's own tally (9 or more plus 17). I did not re-count the wave-1 candidate files.

## Commands run (exit codes)

- `curl -sSfL` of four files at 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad into scratch `fetch/`: exit 0 each. sha256 matches the lane snapshot for gguf.cpp `7505d6a4...`, llama-context.cpp `2a25e556...`, server-common.cpp `b4f4aae7...` and server-context.cpp `dd1de0f2...`. Accessed 2026-10-23.
- Python line check of each registry signature against its SOURCES URL `#L` line in the fresh files: 17/17 `on_cited_line= True`, one hit each.
- `env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE git -C <lane> archive 1560e4d8 | tar -x` into scratch `base-1560e4d8/`: exit 0. A first `rg` without `-uu` skipped `.ufo/` and wrongly showed 0 hits; the `-uu` re-run gives the counts in ledger row 18.
- `coredumpctl list --no-pager | rg llama`: 1 SIGSEGV (pid 3310053) and 11 SIGABRT.
- JSON decode check on the receipt excerpts for E26-07 and E26-14: `sig_in_raw= True sig_in_decoded_message= False`.
- `sha256sum .ufo/waves/round-26/count-c1.py`: `6501737c749926be9d6b37761175d76f89876976c46bd5951fc1a3520c796588`.
- `pgrep -af llama-server`: no output (none of mine; I started none).

## Files written

- `.ufo/waves/round-26/w2-falsify/advice/ReviewerSkillProse.md` (this report)
- Scratch only: `/fast/scratch/hyaku/kama-r26w2/ReviewerSkillProse/fetch/` (4 fresh source files) and `/fast/scratch/hyaku/kama-r26w2/ReviewerSkillProse/base-1560e4d8/` (base archive extract)

No tools were installed or updated.
