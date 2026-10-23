# SrcReopen2 — scoped findings (S182, S183)

Falsified the two assigned SOURCES.md rows against the pinned snapshot
`.ufo/waves/round-31/sources/llama.cpp-704366d/` (commit 704366d; snapshot
file sha256 `b4f4aae7…d442` matches `SNAPSHOT.json` for
`tools/server/server-common.cpp`). Full commands + verbatim output:
`.ufo/waves/round-31/w2/out/SrcReopen2/report.md`; raw receipts in the same
directory (`receipt-line-checks.txt`, `receipt-cells-and-usedby.txt`).

## Per-row verdicts

- `S182: quote-verbatim yes; words 7; line match yes; used-by corpus/knowledge/chat-adapter-outcomes.md+registry/chat-param-outcomes-r31.json exists yes`
- `S183: quote-verbatim yes; words 7; line match yes; used-by corpus/knowledge/chat-adapter-outcomes.md+registry/chat-param-outcomes-r31.json exists yes`

## Evidence

- Both rows are inside `## Registry` (section opens L9, rows at L194–195 of
  `corpus/SOURCES.md`).
- `sed -n '1390p'` prints `throw std::invalid_argument("Expected 'messages' to
  be an array");` — the row quote occurs verbatim (grep -cF = 1), 7 words.
- `sed -n '1395p'` prints `throw std::invalid_argument("All non-assistant
  messages must contain 'content'");` — verbatim on line, 7 words.
- Both throws sit inside the guards the rows' `scope` cells describe
  (messages-not-array at ~L1389; non-assistant-without-content at ~L1394).
- used-by targets both exist at the tip: `corpus/knowledge/chat-adapter-outcomes.md`
  (cites `S180-S191` + `server-common.cpp:1390`/`:1395`),
  `registry/chat-param-outcomes-r31.json` (K31-06 `"row": "S182"` line 1390,
  K31-07 `"row": "S183"` line 1395); SKILL.md rows K31-06/K31-07 cite the
  same ids.

No disagreement. Nothing edited outside
`.ufo/waves/round-31/w2/out/SrcReopen2/` and `/tmp/kama-r31w2/SrcReopen2/`.
No tools installed; no servers touched; no git/jj writes.

Limits: verbatim is line-presence, not uniqueness; the URL was checked via the
sha256-pinned local snapshot (the counter's source of truth), not a re-fetch;
the registry's live-request outcomes were not re-measured by this seat.
