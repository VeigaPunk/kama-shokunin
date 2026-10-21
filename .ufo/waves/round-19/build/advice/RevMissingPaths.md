VERDICT: partial - S054/S055/S056 paths and upstream anchors resolve at their cited revisions, but the recovery gate token binds eb78788b whose bytes describe live/, and several S055/Gate pins name no revision and resolve to other generations.

# RevMissingPaths — S055 / S056 / S057 / Gate-row path check (round 19)

Scope: every path or URL cited by SOURCES S054–S057, round-18 lesson Gate rows 41–54, and the round-18 erratum / citation tokens. Pinned to lane HEAD `7229fa95eb122310e9e5334ad799ee3006293ebd`. Round-start `1b85a24` is an ancestor (exit 0). HEAD advanced `8bf99ca` → `7229fa9` during the run. Committed bytes only. Full evidence: `/tmp/kama-r19-RevMissingPaths/out/` (`inventory.md`, `receipts.md` with every exit code, `pins-by-revision.tsv`, `lane-revision-path-matrix.tsv`, `checker-advisory-HEAD.json`, `upstream/`, `blobs/`). No lane mutation, no installs, no servers.

## Exists at cited revision (verified)
- `common/arg.cpp` @704366d76: fetched sha256 `bf4c58c1…822d` equals the S054/S056 pin; git blob id equals the GitHub tree entry. Cited lines 829–837, 3338, 3354, 3538, 4321 and 833 hold the cited text.
- S055 receipts: all 15 `source_binding` spans (`server-context.cpp` 5288–5299, `server-http.cpp` 314–325, `server.cpp` 519–523 / 529–534 / 575–590) are byte-identical to @704366d76.
- `runs/commands.json` @1c325b2 (sha `ce7dc79c…`) matches registry token `s055-commands`; `measured_commit` c6dc46f; 32 commands.
- Gate upstream rows: linux v7.2 tag → `8d3ae592…`; `tcp_ipv6.c:2176`, `in6.h:38`, `proc_net_tcp.rst:8/18`; RFC 4291 474 / 551–552 / 570; python, pytest and automake quotes; S057 quotes in the man7 page.

## Revision-without-path and pointer defects
1. **SOURCES.md:67 (S055)** — revision `c6dc46f` named for `runs/commands.json`; `.ufo/waves/round-18/runs/commands.json` is ABSENT at c6dc46f (`cat-file` exit 128). The relative form `round-18/runs/commands.json` is not a repo path. Fix: cite @1c325b2, `.ufo/waves/round-18/runs/commands.json`, sha256 `ce7dc79c…`.
2. **lessons/round-18.md:416–419 (erratum token)** — `cite(eb78788b…, runs/live-gate-1.stdout, sha256=b2043ba8…)` passes the checker (bytes match), but the blob is one line, `VALID …/live/receipt-1.json`. The sentence beside it says this output describes `live-recovery/`. The recovery output is `1cb5a41b…` at 1b85a24 and 7229fa9 (`VALID …/live-recovery/receipt-1.json`); no token pins it. Fix: add `cite(1b85a24eca4d1fe81ef8d9ddf513fda1aad93e0e, .ufo/waves/round-18/runs/live-gate-1.stdout, sha256=1cb5a41bbfeb8f0f9306d9bf86df83d33cf9bc3aa46887c574e1dd07875574c7)` for the recovery claim; relabel the eb78788b token as the checkpoint gate.
3. **lessons/round-18.md:53 (Gate row S055)** — no revision at all. `runs/live-gate-1.stdout` and `runs/commands.json` are checkpoint bytes at 1c325b2 / 101f3991 / eb78788b (four pins; measured c6dc46f) and recovery bytes at 1b85a24 / 7229fa9 (five pins; measured eb78788b). The row pairs `live/` receipts with whichever generation the tip holds.
4. **SOURCES.md:67 (S055) pins with no revision** — tool `dc036d7d…` (`tools/kama-llamacpp-live.py`) holds at c6dc46f and 1c325b2 only among checked revisions (101f3991 = `ec7a7567`; 0c75c611 onward = `83eac5c0`). `runs/run.py` changes at each step: `e3c957ca` (1c325b2, 101f3991), `529a4c1a` (0c75c611, 888cd384), `66ac6f05` (eb78788b…8bf99ca), `5add39f7` (7229fa9); ABSENT at c6dc46f. The gate `check-receipt.py` is `c5715641` at c6dc46f / 1c325b2 (four `--expect` pins in argv); `e69f91b3` at 101f3991; `10912f24` at 7229fa9 (five pins in argv from 1b85a24). The checkpoint 101f3991 therefore changed the tool and gate bytes that S055 pins.
5. **Measured revision is not the evidence revision (recovery)** — lesson:362–363 names eb78788b as the measured tree; `live-recovery/receipt-1.json` (lesson:382–383, no revision) is ABSENT at eb78788b and first appears at 1b85a24 (`89728a02…`). [INFERENCE: run output is committed in the following commit, as with c6dc46f → 1c325b2.]
6. **SCORECARD.md:773–777** says `runs/commands.json` at harness commit eb78788b records `measured_commit` = eb78788b. At eb78788b it records c6dc46f (`ce7dc79c…`, two nonexpected exits). The statement is true from 1b85a24.
7. **SCORECARD.md:790** — "the earlier exit-2 pass at `c6dc46f`": the c6dc46f tree has no C2 artifact (`runs/c2-survivors.{stdout,json}` and `runs/pre-repair/c2-survivors.json` are ABSENT). The pre-repair file first appears at 888cd384.
8. **SCORECARD.md:781** — "five-pin gate VALID in `runs/live-gate-{1,2,3}.stdout`": no revision; resolves to the recovery generation, while S055's `live/` generation is four-pin.
9. **LOG.md:1106–1109** — revisions named, no paths. Receipt bytes are identical at 1c325b2…7229fa9 (`e616f67e…`), so the receipt claim holds; the tool/gate generation is not stated.
10. **lessons/round-18.md:42** — "`server-queue.cpp:279` resets … `running = false;` at 134": line 279 is `running = true;` (start_loop); `running = false;` is line 134 (terminate). Wording fix only; both lines exist. `server.cpp` (basename) resolves uniquely to `tools/server/server.cpp` @704366d76.
11. **SOURCES.md:69 (S057) and Gate rows 47–49** — URLs with no commit or sha pin in the row (man7 rolling page, python 3.14 docs, pytest `stable`, automake release tarball). Quotes verified against today's fetches; S057 man7 sha256 `d9b7737e…`. The S057 used-by paths (`corpus/lessons/round-19.md`, `registry/required-citations.json`) exist at 7229fa9 and not at 8bf99ca.

## Drift and worktree state
- The S057 row text changed during the run. First read: "(11 words)" and "$ORIGIN … (14 words)". HEAD 7229fa9: "(10 words)" and "This expands to the directory containing the program or shared object (11 words …)", which matches the page.
- Uncommitted at the last snapshot (not analysed): `runs/commands.json` (worktree `measured_commit` = 7229fa95…, sha prefix `50e70962…`), `registry/required-citations.json`, `tools/citation-provenance.py`, `runs/gate-selftest.stdout`, `runs/tool-selftest.stdout`. If these are committed, re-run this check.

## Advisory checker (not an official count)
`python3 tools/citation-provenance.py --lane <lane> --json` on a `git archive` of 7229fa9: exit 0; required 3, verified 3, missing 0, mismatch 0. It passes defect 2 because it verifies bytes, not what the row claims.

## Suggested corrections (advice only; not applied)
- SOURCES.md:67 — cite `runs/commands.json` @1c325b2 (`ce7dc79c…`), `live/receipt-{1,2,3}.json` @1c325b2, tool `dc036d7d…` @c6dc46f/1c325b2, `run.py` `e3c957ca…` @1c325b2; drop the bare "measured c6dc46f" path revision.
- lessons/round-18.md:416–419 — add the 1b85a24 token for the recovery claim (above); relabel the eb78788b token as the checkpoint gate; register the new row in `registry/required-citations.json`.
- lessons/round-18.md:53 — qualify each path by revision and generation.
- SCORECARD.md:773–777, 781, 790 — as in defects 6–8.

Installs/updates: none. Lane writes: this file only.
