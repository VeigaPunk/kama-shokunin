# ScribeLessonMistakes — round 16 advice

Owned output: `.ufo/waves/round-16/build/drafts/lesson-mistakes.md` (append-ready `## Mistakes`). Access date for all sources: 2026-10-20. No tools installed or updated. No lane gate, harness, test, or probe was run. No session, history, or credential store was opened.

## Sources opened (path:line; quote ≤25 words)

1. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/frozen/kama-probe-before.sh`
   - lines 458–461: `401) C_VERDICT=UNAUTHORIZED_SERVICE; C_REASON=http-401 ;;` and `403) ...` only. No 503 case.
   - line 469: `# HTML at ANY status: header, or a body sniff (v3 rule 4)` (12 tokens).
   - line 513: `C_VERDICT=FOREIGN_SERVICE`.
   - line 521: `C_REASON=non-2xx-non-model-http` for non-2xx, non-HTML, no model array.
2. `https://raw.githubusercontent.com/ggml-org/llama.cpp/b11755/tools/server/server-http.cpp`, opened as artifact raw lines 305–330. Line 318 (counted by this scribe): "no endpoints are allowed to be accessed when the server is not ready" (13 words), the in-source comment directly above `res.status = 503;` at line 320. The body literal `"Loading model"` is at line 324 (2 words). Line numbers are this scribe's count, not a tool-reported index; the brief's 307–325 range is not exact.
3. `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-15.md` lines 25–30 (Mistakes table format), 94–99 (session grep disclosure), 197–201 (scribe and AST incidents). Quote line 197: "A scribe disclosed in-process evaluation of the committed guard despite its no-execution instruction" (14 words).
4. `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-15-verifier-spotcheck.md` lines 58–61 (status-neutral incidents), 165–168 (routed defect 3). Quote line 167: "Keep code/corpus searches explicitly bounded away from historical session directories" (10 words).

## Findings

- The loading-state verdict bug is traceable in the frozen probe: a JSON 503 from a loading server has no 503 case in `classify()`, falls to the non-2xx branch, and is labelled `FOREIGN_SERVICE` with `non-2xx-non-model-http`. The llama.cpp b11755 source confirms the 503 body is the loading-state body, served by `middleware_server_state` for every non-frontend path.
- No prior lesson captured this. Captured-by is "none" in the draft.
- The round-15 process entry has no mechanical capture; the disclosure and the outside closure's routed defect 3 are the only record. The round-16 fix is textual: two context-bounding clauses and a no-subagents line in the round-16 seat contract. Compliance is not observed.

## Unknowns (not verified this session)

- `KQ19`: the draft cites it because the brief names it. I did not open a KQ19 record, so its existence and text are unverified.
- The stub matrix red/green result: L1's measurement; not observed here.
- The `v3 rules` document: not opened; only the in-file comment at line 469.
- README `GET /health` claim at llama.cpp b11755: not opened.
- Whether `body_has_model_array` returns 0 for the loading body: not opened; the path reading is an inference.
- Whether any round-16 seat complies with the bounding clauses: not observed.

## Advice to L1

- Integrate the draft table as the round-16 `## Mistakes` section. Replace the draft's line-number counts for llama.cpp with a tool-reported index if you re-open the source.
- Confirm KQ19 exists before citing it as a fix reference.
- Keep the process entry as an incident, not a win, per the round-15 closure's framing.
