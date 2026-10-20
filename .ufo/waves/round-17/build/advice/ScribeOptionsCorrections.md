VERDICT: confirm — all four named statements say "every non-frontend path" and overstate by OPTIONS; append-ready corrections drafted and grounded at the pinned copy's lines.

# Scope
Owned file: `.ufo/waves/round-17/build/drafts/options-corrections.md` (created; the path did not exist). Draft-only: no lane document edited, no jj or git writes, no subagents, no servers started, no lane gate run. Access date for all sources: 2026-10-20.

# Findings (pinned copy, verified this session)
Pinned copy: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/sources/llama.cpp-704366d/server-http.cpp`, 940 lines, sha256 `24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb` (matches S036 in `corpus/SOURCES.md:48`). Upstream: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-http.cpp

1. OPTIONS bypasses the gate. `server-http.cpp:347` — "If this is OPTIONS request, skip validation because browsers don't include Authorization header" (comment verbatim at :346); `:352` returns `Handled` before the state gate at `:354`.
2. Exempt set is the frontend set only. `:309-311` — "frontend asset, allow it to load and show "loading"". `/health` and `/v1/health` are not exempt from the gate: `:251-258` `get_public_endpoints` is used only at `:267` in the API-key check.
3. Envelope fields. `:318` `"Loading model"`; `:319` `"unavailable_error"`; `:320` `{"code", 503}`; `:314` `res.status = 503`.
4. Order. `:354` `middleware_server_state` precedes `:357` `middleware_validate_api_key`.

Located statements and drafted corrections (all in the draft file, Appends A–D):
- A. `corpus/README.md:206` (round-16 row) — append after the file's last line (228). Quote at :206: "every non-frontend path 503 before the API key".
- B. `corpus/knowledge/endpoint-identity.md:202` — "answers every non-frontend path with that 503 body while not ready". Append after line 216.
- C. `corpus/knowledge/runtime-health-surface-matrix.md:65` — "served by the 503 middleware on every non-frontend path, `/v1/models` included". Append after line 75.
- D. `SKILL.md:519` — "Error signature (llama.cpp b11755 single-model, every non-frontend path while loading, before the API-key check)". Append after line 553.
- E (extra, not in the four named targets). `corpus/SOURCES.md:48` S036 cell carries the same overstatement; the lane's own lesson `corpus/lessons/round-16-verifier-spotcheck.md:185` (item 4) asks for it to be narrowed and cited 319-320. The registry contract allows no in-place cell edit, so the draft proposes an append-only note at the file end; L1 decides placement.

# Other located statements (not drafted; routing for L1)
- `tools/kama-probe.sh:422-424` — code comment "every non-frontend path returns 503". Owned by another seat.
- `tests/probe-verdicts/LoadingEnvelope.json:143-145` — fixture name `every-non-frontend-path`. Matrix bytes are pinned by round-16 `measure.py`; do not edit; route to C1.
- `.ufo/waves/round-16/build/advice/ConnectKengaku.md:45`, `ReviewLogConvention.md:165`, and other wave advice carry the phrase; these are artifacts, not lane docs.
- `.ufo/waves/round-16/build/advice/ReviewKq19Interplay.md:198` already asks for "every non-frontend, non-OPTIONS path"; consistent with the drafts.

# Limitations
- Only the pinned copy was read. The live-server behaviour was not exercised; no fake server or llama-server was started, so the OPTIONS and `/health` claims are source-level only, not observed at runtime.
- `is_ready` set points were taken from a grep excerpt of `server.cpp` (lines 460, 515 at 704366d); `server.cpp` itself was not opened in full this session.
- Router-mode behaviour (`server-models.cpp`) and any proxy relay of the envelope were not examined; the drafts make no claim about them.
- Lane docs were read only where the draft's append point needed checking (README tail 216-228, endpoint-identity tail 208-216, SKILL.md tail 536-553, SOURCES.md section headers). Line 14 of the health matrix was not re-checked.
- Lane-doc append points are the file ends as read this session; if L1 edits any of these files first, re-anchor.

# Installs
None. No tool installed or updated.
