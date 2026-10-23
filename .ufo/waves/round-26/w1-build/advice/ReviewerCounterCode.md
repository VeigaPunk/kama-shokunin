# ReviewerCounterCode advice: frozen C1 counter review (round 26, wave 1)

Verdict: the frozen counter at a23c0e04 (sha256 6501737c…6588) is not a sound falsifier. Fabricated rows reached counted 6 of 14 through three bypasses. Separately, a registry with more than 19 runnable rows cannot be scored (exit 2).

The full findings, with evidence and a fix proposal for each, are in `.ufo/waves/round-26/w1-build/out/ReviewerCounterCode/findings.md`. Receipts are in `out/ReviewerCounterCode/receipts/`. All runs were made in scratch copies of `git archive a23c0e04` under `/fast/scratch/hyaku/kama-r26/ReviewerCounterCode/`, using `flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 900 python3 .ufo/waves/round-26/count-c1.py --out ...`.

## Findings (severity, short evidence)

1. HIGH. A warning printed on an unrelated fault counts as an error signature, so one fault produces many rows.
   - runA RA01 (`-dt 0.1`, `--defrag-thold is deprecated ...`, arg.cpp:2542, a `W` line) and RA03 (`--embedding -b 1024 -ub 256`, `embeddings enabled with n_batch (`, server.cpp:164) both counted on the missing-model fault.
   - The genuine missing-model row RA04 was then blocked by clause (g).
   - Fix: run a per-row healthy control with the same arguments, and require the signature on an error-level line.
2. HIGH. JSON `\u` escapes bypass the request echo check.
   - server-common.cpp:1375 echoes the decoded `response_format.type`.
   - runA RA05 (`Cannot run multiple aLoRAs in a single request`) and RA06 (`failed to reload model after sleeping`, which in the source is a `GGML_ABORT`) both counted with status 400.
   - Fix: also compare against the decoded body, the unquoted path and header values.
3. HIGH. File contents bypass the echo check.
   - `--chat-template-file` templates are printed back in the parse error.
   - runA RA07 and RA08 both counted with source literals placed inside the template files.
   - Fix: add the contents of any file named in the arguments to the comparison text, or allow only counter fixtures.
4. HIGH. Ports run out: `used` never releases a port.
   - runB (20 rows) evaluated 19 rows, then printed `could-not-evaluate: no free port in 47560-47579` and exited 2.
   - Fix: call `used.discard(port)` after teardown confirms the port is closed.
5. HIGH (integrity). The server pin covers only a 17,864-byte launcher.
   - The server code is in the unpinned `libllama-server-impl.so`, plus libllama, libllama-common, libggml* and libmtmd, all loaded through `RUNPATH $ORIGIN`.
   - `LD_*` variables are inherited. [INFERENCE] A library swap would pass the no-reader control.
   - Fix: pin every loaded library and scrub `LD_*`.
6. MEDIUM. One bad row aborts the whole count.
   - runC: a row with `--path` gives `could-not-evaluate: RC02: port did not close` (exit 2, wrong cause).
   - runD: a row with no `channel` gives a `KeyError` traceback, exit 1 and no receipt.
   - Fix: make these row-level check failures.
7. MEDIUM. The forbidden-argument list can be bypassed.
   - arg.cpp:826-827 turns `_` into `-`. runA RA09 passed `--log_file` and the server wrote the file.
   - The list also misses `-hfr` and `-hff`/`--hf-file`.
   - Fix: normalise argument names, or use an allowlist.
8. MEDIUM. Results depend on the environment.
   - `LLAMA_ARG_DEFRAG_THOLD=0.1` changed RF01 from counted 1 to 0.
   - `http_proxy=http://127.0.0.1:9` made the count could-not-evaluate.
   - Fix: give child processes a minimal environment and bypass proxies in urllib.
9. MEDIUM. Clause (g) depends on registry order.
   - runA counted the two warning rows. runE, with the same triggers but the genuine row first, counted 1.
   - Fix: count one row per overlap component, choosing the lowest id.
10. MEDIUM. Markdown matching rejects genuine rows.
    - runA RA10 (id in backticks) and RA11 (row under a `###` subheading) failed `a_skill_row`.
    - [INFERENCE] A signature containing a pipe cannot match inside a GFM table.
    - Fix: parse the table cells, and end the section only at a heading of level 2 or higher.
11. LOW. Clause (c) uses substring file matching.
    - runA RA12 (file `llama.cpp`) passed `c_source_row` with a SOURCES row that cites only server-context.cpp.
12. LOW. The same string must satisfy both C escaping (source) and log or JSON escaping (channel).
    - Startup signatures that span `\"` or `%%` can never count (arg.cpp:876 compared with the log of runA RA02).
13. INFO. Startup exit semantics.
    - A negative return code (death by signal) counts as non-zero.
    - No error path exits 0; the arg.cpp `exit(0)` sites are informational only.
14. LOW [INFERENCE]. Teardown and port races.
    - Children of an already-exited process-group leader are not killed.
    - The connect probe does not see a socket that is bound but not listening.

Checked and clean:
- git grep at base. A survey of 2025 pinned-source literal occurrences found 0 that occur at base only across line wraps. Binary files are matched.
- All 13 pinned source sha256 values match.

## Exact observations (command output, exit code)
- runA: `registered 14 counted 6 target 12 met False not-counted ['RA02:e_signature_seen', 'RA04:g_distinct', 'RA09:g_distinct', 'RA10:a_skill_row,g_distinct', 'RA11:a_skill_row,g_distinct', 'RA12:e_signature_seen', 'RA13:e_signature_seen', 'RA14:e_signature_seen']`, exit 0.
- runB: `could-not-evaluate: no free port in 47560-47579`, exit 2.
- runC: `could-not-evaluate: RC02: port did not close`, exit 2.
- runD: `KeyError: 'channel'` (count-c1.py:279), exit 1.
- runE: `registered 3 counted 1 ... not-counted ['RE01:g_distinct', 'RE03:g_distinct']`, exit 0.
- runF-plain: `registered 1 counted 1`, exit 0. runF-envdefrag: `counted 0 ... ['RF01:f_absent_from_baseline']`, exit 0. runF-envapikey: `counted 1`, exit 0. runF-proxy: `could-not-evaluate: baseline server never became healthy`, exit 2.
- `ldd ~/.local/opt/llama-b11755/llama-server` resolves `libllama-server-impl.so`, `libllama-common.so.0`, `libmtmd.so.0`, `libllama.so.0`, `libggml.so.0` and `libggml-base.so.0` from `/home/vgpnk/.local/opt/llama-b11755/`. `readelf -d` shows `RUNPATH [$ORIGIN]`.
- Cleanup: `pgrep -af llama-server | grep -E '475[67][0-9]'` exited 1 with no output, and `ss -ltn | grep -cE ':475[67][0-9]\b'` printed 0.

No tools were installed or updated, and no lane file outside my output directory and this report was written.

## Files written
- `.ufo/waves/round-26/w1-build/advice/ReviewerCounterCode.md` (this report)
- `.ufo/waves/round-26/w1-build/out/ReviewerCounterCode/findings.md`, `gen.py`, `survey.py`, `fixtures/*.jinja`, `registries/*.registry.json`, `receipts/*`
- Scratch: `/fast/scratch/hyaku/kama-r26/ReviewerCounterCode/`
