# SrcReopen3 — scoped findings (round-31 w2)

Item: re-open registry rows S184 and S185 in corpus/SOURCES.md against the pinned
snapshot `.ufo/waves/round-31/sources/llama.cpp-704366d/server-common.cpp`
(SNAPSHOT.json-verified: sha256 b4f4aae7…d442, 75061 bytes — matches manifest).

## One-line verdicts

- `S184: quote-verbatim yes; words 9; line match yes; used-by corpus/knowledge/chat-adapter-outcomes.md, registry/chat-param-outcomes-r31.json exists yes`
- `S185: quote-verbatim yes; words 10; line match yes; used-by corpus/knowledge/chat-adapter-outcomes.md, registry/chat-param-outcomes-r31.json exists yes`

## Evidence summary

- S184 (SOURCES.md:196) cites server-common.cpp#L1399 @ 704366d, quote `throw std::invalid_argument("Assistant message must contain either 'content' or 'tool_calls'!");`. `sed -n '1399p'` on the pinned file returns that exact statement; grep confirms the quote body occurs only at line 1399. 9 words (≤25).
- S185 (SOURCES.md:197) cites L1411, quote `throw std::invalid_argument("Expected 'content' to be a string or an array");`. `sed -n '1411p'` returns it verbatim; grep shows it only at 1411. 10 words (≤25).
- Both used-by cells name `corpus/knowledge/chat-adapter-outcomes.md` and `registry/chat-param-outcomes-r31.json`; both files exist at the lane root.
- Access/opened date on both rows: 2026-10-23 (today); anchor cells read `L1399 @ 704366d, opened 2026-10-23` / `L1411 @ 704366d, opened 2026-10-23`.

## Disagreements

None on the checked axes. One layout note (not a row defect): SNAPSHOT.json lives at
`.ufo/waves/round-31/sources/SNAPSHOT.json`, one level above `llama.cpp-704366d/`,
not inside it as the item text implied; the pin was still found and verified.

## Not established

Remote URL freshness (no network fetch compared), back-citations from the used-by
files into SOURCES.md, semantic fidelity of the `scope` prose to surrounding adapter
logic, and all other rows (S180–S183, S186–S191).

Full commands/exit codes/verbatim tails: `.ufo/waves/round-31/w2/out/SrcReopen3/report.md`
and `receipts.txt` in the same directory. No tools installed; no tracked file touched.
