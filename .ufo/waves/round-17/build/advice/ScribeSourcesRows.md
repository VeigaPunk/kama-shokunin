VERDICT: partial — four rows S042–S045 drafted from sources opened 2026-10-20; S043 shares S037's URL, and the mutant-killed definition is quoted from the open TR, not the paywalled TSE article.

# ScribeSourcesRows — round 17 BUILD report

Draft: `.ufo/waves/round-17/build/drafts/sources-rows.md` (rows, Gate lines, search-log supplement). No lane doc was edited. No `jj`, no git write, no installs, no servers started, no ports bound.

## Behaviour (what was produced)
- Four provisional rows in the 11-column shape of S035–S041: S042 llama.cpp `/health` handler (code, A); S043 llama.cpp shutdown/signal path (code, A); S044 Python `Popen.returncode` (docs, A); S045 Jia & Harman mutation-analysis definitions (docs, A).
- Gate lines in the round-16 table shape (Candidate | Decision | Source, location, quote), plus a search-log paragraph.

## Sources opened (all 2026-10-20)
Fetch method: `curl` to raw.githubusercontent.com and docs.python.org, and the read tool for the TR PDF and IEEE page. The pinned llama.cpp files match the round-16 copies by sha256 (`server-context.cpp` dd1de0f2…2329, `server.cpp` 2143962217…5aef4, `server-http.cpp` 24ede172…3fdb, `server-models.cpp` 9c5a6f2c…8b4a).

- S042 `https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp` lines 5288–5297 (`get_health`):
  - 5289: "error and loading states are handled by middleware"
  - 5297: `res->ok({{"status", "ok"}});`
- S042 registration, `…/tools/server/server.cpp` line 278: "public endpoint (no API key check)".
- S043 `…/tools/server/server.cpp`:
  - 33–34: "Received second interrupt, terminating immediately." then `exit(1);`
  - 533–534: `sigaction(SIGTERM, &sigint_action, NULL);`
  - 575: "this call blocks the main thread until queue_tasks.terminate() is called"
  - 576: `ctx_server.start_loop();`
  - 590: `return 0;`
- S044 `https://docs.python.org/3/library/subprocess.html#subprocess.Popen.returncode`: "A negative value -N indicates that the child was terminated by signal N (POSIX only)." The same sentence is on `https://docs.python.org/3.13/library/subprocess.html`. The page is served as 3.15.0.
- S045 `https://doi.org/10.1109/TSE.2010.62` (publisher page `https://ieeexplore.ieee.org/document/5487526`, opened): Vol 37 Issue 5, pp. 649–678, dated 17 June 2010; the intro sentence "Mutation Testing is a fault-based testing technique which provides a testing criterion called the “mutation adequacy score.”" is on that page.
- S045 quotes from `http://crest.cs.ucl.ac.uk/fileadmin/crest/sebasepaper/JiaH09b.pdf` (TR-09-06): PDF p.5 §II.B "the mutant p′ is said to be “killed”, otherwise it is said to have “survived”." and "The mutation score (MS) is the ratio of the number of killed mutants over the total number of non-equivalent mutants."

## Findings and inferences
1. S043 reuses S037's URL (same file, same commit). L1 must decide whether a shared URL is allowed or whether a fragment should be used. [INFERENCE: S037 precedent]
2. The killed/survived and score wording is from the TR, not the published TSE article. The IEEE body is paywalled (`Sign In or Purchase`); the article text was not reached. The gate line says so.
3. Tier criteria are not written in `corpus/SOURCES.md` (its header says only "Tiers are scoped to `scope`"). Tier A for the four rows follows precedent from S035–S041. [INFERENCE]
4. The `/health` 200 body is `{"status": "ok"}` from the handler. A 503 loading body comes from the middleware (S036 `server-http.cpp:312`), so the handler by itself cannot prove readiness. [INFERENCE: middleware runs before the handler, per S036's order]
5. For C2, graceful teardown reaches `return 0` on the single-model path (S043 line 590). The Python rule gives `-N` for signal death, so a `-9` return from the harness is a signal death. The number 9 for SIGKILL is not sourced by any row opened here (unknown; I did not check signal(7) or POSIX).
6. The `/health` and teardown rows do not show that the installed b11755 binary behaves this way. S038 ties b11755 to 704366d76 by tag and digest; the binary was not run, so this is a source-level claim only.

## Unknowns (stated, not filled)
- The TSE article's killed/survived wording: not reached (paywall). Quotes are TR-09-06.
- The POSIX number for SIGKILL: not sourced this round.
- Whether the registry allows two rows with the same URL: not verified; L1 decides.
- Whether a `llamacpp-loading-lifecycle.md` section for S042/S043 exists yet: not checked. The used-by cells are proposals.
- The host Python version: not read (`python3` version not checked); S044 is stated for the docs pages fetched.

## Proposed cells (L1 to confirm)
- S042 used-by: `corpus/knowledge/llamacpp-loading-lifecycle.md`.
- S043 used-by: `corpus/lessons/round-17.md`.
- S044 used-by: `corpus/lessons/round-17.md`.
- S045 used-by: `corpus/lessons/round-17.md`.
- Existing rows (S017, S035–S041): not edited by this seat.

## Tool installs and updates
None. Only `curl` and the built-in read tool were used (no new tools).

## Checks for L1 (not run by this seat)
- Confirm the S043 URL decision, the tier A scope for S045, and the used-by cells, then append the rows.
- Re-read the S042 and S043 line ranges against the round-16 pinned copies, and recheck the S044 page version.

## Artifact paths
- `.ufo/waves/round-17/build/drafts/sources-rows.md` (owned draft)
- `.ufo/waves/round-17/build/advice/ScribeSourcesRows.md` (this report)
