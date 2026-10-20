# Draft — SOURCES rows S042–S045 and round-17 Gate lines

Owner: ScribeSourcesRows (round 17, BUILD). Status: append-ready prose for L1. No lane
doc was edited. Ids S042–S045 are provisional until L1 integrates. Every source below was
opened on 2026-10-20 (UTC) by this seat, with the fetch method and location stated per row.

## Registry rows (append after S041; 11-column shape of S035–S041)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S042 | llama.cpp `/health` route handler @ 704366d76 (release b11755) — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp | code | A | llama.cpp `/health` success body at commit 704366d76 only; the 503 loading refusal belongs to the middleware (S036), and `/v1/models` is not this handler | `server_routes::init_routes`, `get_health` lines 5288-5297 (comment 5289; body `res->ok({{"status", "ok"}});` at 5297); `/health` registered as public at `server.cpp:278`; raw file sha256 dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329 | The handler's only success body is `{"status": "ok"}`; its own comment says "error and loading states are handled by middleware", so a `/health` 200 body other than that object is not this handler's output. [INFERENCE] The middleware gate runs before the handler, per S036's pre-routing order. | mined | 2026-10-20 | on-release | corpus/knowledge/llamacpp-loading-lifecycle.md |
| S043 | llama.cpp shutdown and signal path @ 704366d76 (release b11755) — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp | code | A | how a llama-server process exits on SIGINT/SIGTERM at commit 704366d76, single-model and router; not SIGKILL behaviour and not the exit status of any kama run | `signal_handler` lines 26-37 (second interrupt `exit(1)` at 34); single-model `shutdown_handler` 519-523 calling `ctx_server.terminate()` at 522; `sigaction` for SIGINT and SIGTERM at 533-534; `ctx_server.start_loop()` at 576 with the blocking comment at 575; `return 0;` at 590; `llama_server(argc, argv)` returns `result` at 122-124; raw file sha256 2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4 (same file as S037) | SIGTERM and SIGINT share one handler. The first signal runs the shutdown handler, which terminates the queue loop; `start_loop()` returns, `clean_up` and `join` run, and the normal path returns 0 at line 590. A second signal calls `exit(1)`. [INFERENCE] The code has no handler for SIGKILL, which cannot be caught. | mined | 2026-10-20 | on-release | corpus/lessons/round-17.md |
| S044 | Python `subprocess` — `Popen.returncode` — https://docs.python.org/3/library/subprocess.html#subprocess.Popen.returncode | docs | A | meaning of the harness-observed return code of a child process under Python: `None` until termination, negative `-N` for death by signal N on POSIX; not llama.cpp exit semantics | §`Popen.returncode` (anchor `subprocess.Popen.returncode`), page fetched as docs.python.org/3/ (resolves to 3.15.0); the same sentences appear on https://docs.python.org/3.13/library/subprocess.html | "A negative value -N indicates that the child was terminated by signal N (POSIX only)." The attribute is set only when `poll()`, `wait()` or `communicate()` detect termination; `None` means not yet terminated at the last call. | mined | 2026-10-20 | 90d | corpus/lessons/round-17.md |
| S045 | Jia & Harman, "An Analysis and Survey of the Development of Mutation Testing", IEEE Trans. Software Eng. 37(5), pp. 649–678, 2011 — DOI https://doi.org/10.1109/TSE.2010.62 (publisher page https://ieeexplore.ieee.org/document/5487526); definitions quoted from the open technical report http://crest.cs.ucl.ac.uk/fileadmin/crest/sebasepaper/JiaH09b.pdf (TR-09-06) | docs | A | definitions only, for mutant, killed/survived, equivalent mutant and mutation score in mutation analysis; not evidence that any test set is adequate and not a kama measurement | Publisher record: DOI 10.1109/TSE.2010.62, Vol. 37 Issue 5, pp. 649-678, published 17 June 2010 (IEEE page, opened). Quoted text: TR-09-06 §1 Introduction (PDF p.1) and §II.B "The Process of Mutation Analysis" (PDF p.5) | "the mutant p′ is said to be “killed”, otherwise it is said to have “survived”." The mutation score is "the ratio of the number of killed mutants over the total number of non-equivalent mutants." The IEEE article body is paywalled; the killed/survived and score wording is from the TR, not the published article. | mined | 2026-10-20 | 90d | corpus/lessons/round-17.md |

Row notes for L1 (not cells):
- S043 reuses the URL of S037 (`server.cpp` at 704366d76). The rows differ in anchor and
  scope. L1 decides whether a shared URL is acceptable under the registry or whether S043
  should cite a fragment such as `…/server.cpp#L26-L37`. This seat chose the plain URL to
  match the S037 precedent.
- S042 and S043 are source-level facts at commit 704366d76. Release b11755 is pinned to that
  commit by S038. The shipped binary was not inspected, so no row claims the installed
  binary matches these lines.
- S045's tier and kind follow the requested "docs". The tier criteria are not written in
  `corpus/SOURCES.md` (it says only that tiers are scoped to `scope`); tier A is chosen by
  precedent from S035–S041 and is [INFERENCE].
- Backup definition source, not drafted as a row: PIT home page, https://pitest.org/ (opened
  2026-10-20), section "What is mutation testing?": "If your tests fail then the mutation is
  killed , if your tests pass then the mutation lived ." It is a tool's own wording, and it
  says "lived" rather than "survived".

## Gate lines (for `lessons/round-17.md` §Gate; the same table shape as round-16)

All sources opened 2026-10-20. Quotes are verbatim and at most 25 words.

| Candidate | Decision | Source, location, quote |
|---|---|---|
| `/health` 200 body is exactly `{"status": "ok"}` as the handler's output | admit | S042 `server-context.cpp:5297` `res->ok({{"status", "ok"}});`; `server-context.cpp:5289` "error and loading states are handled by middleware" |
| `/health` needs no API key | admit | S042 registration `server.cpp:278` "public endpoint (no API key check)" |
| A `/health` 200 proves the handler produced it while the model is loading | reject | S042 `server-context.cpp:5289` "error and loading states are handled by middleware"; the loading gate is S036 `server-http.cpp:312` "no endpoints are allowed to be accessed when the server is not ready" |
| SIGINT and SIGTERM both reach one handler | admit | S043 `server.cpp:533-534` `sigaction(SIGTERM, &sigint_action, NULL);` with `sigaction(SIGINT, …)` at 533; `server.cpp:29-37` (`signal_handler`) |
| A second signal forces immediate exit with status 1 | admit | S043 `server.cpp:33-34` "Received second interrupt, terminating immediately." then `exit(1);` |
| A graceful signal teardown reaches `return 0` on the single-model path | admit, scoped | S043 `server.cpp:575` "this call blocks the main thread until queue_tasks.terminate() is called"; `server.cpp:590` `return 0;` (code path read, not a run) |
| Negative return code means death by signal N on POSIX | admit | S044 Python docs §`Popen.returncode` "A negative value -N indicates that the child was terminated by signal N (POSIX only)." |
| Return code `-9` proves SIGKILL, from a llama.cpp source row | reject as cited | no llama.cpp row says so; S044 gives only the `-N` rule. The number 9 for SIGKILL is not sourced by any row opened this round (unknown here, not checked against signal(7)). |
| A mutant is "killed" when its output differs from the original on a test | admit | S045 TR-09-06 PDF p.5 §II.B "the mutant p′ is said to be “killed”, otherwise it is said to have “survived”." |
| Mutation score is killed over non-equivalent mutants | admit | S045 TR-09-06 PDF p.5 "The mutation score (MS) is the ratio of the number of killed mutants over the total number of non-equivalent mutants." |
| S045 definitions are the published TSE article's wording | reject as stated | the IEEE page (https://ieeexplore.ieee.org/document/5487526, opened) shows abstract and §1 only; the killed/survived text is paywalled. The quotes are from the open TR-09-06 PDF. |

## Search-log supplement (draft, round 17, 2026-10-20)

**Round-17 build — C2 predicates and mutation definition (ScribeSourcesRows).** Question:
which first-party code locations and documents ground the `/health` ready body, the signal
and teardown exit path, the Python return-code meaning, and the mutant/killed/mutation-score
definition? Where: llama.cpp `server-context.cpp`, `server.cpp` and `server-http.cpp` at
704366d76, fetched from raw.githubusercontent.com and matched byte-for-byte (sha256) to the
round-16 pinned copies under `.ufo/waves/round-16/sources/llama.cpp-704366d/`; Python
`subprocess` documentation at docs.python.org/3/ and 3.13/; the Jia & Harman IEEE TSE publisher
page and the open TR-09-06 PDF; PIT home page as a backup. Identified 5 sources, screened 5,
included 4 new rows (S042–S045), excluded 1 (PIT page as a backup only). S043 shares a URL with
S037. The IEEE article body was not readable without a subscription. Stop: each row's
location and quote opened and checked against the pinned text.
