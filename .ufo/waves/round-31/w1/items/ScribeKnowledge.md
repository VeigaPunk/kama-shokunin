/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim — let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.

# Item ScribeKnowledge — corpus knowledge entry for the chat adapter
Claim served: C1 (depth), corpus expansion.
Write `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w1/out/ScribeKnowledge/entry.md`: a new knowledge entry
`corpus/knowledge/chat-adapter-outcomes.md` in the shape the lane's entries use (read
`/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/instrument-run-agreement.md` and `.../context-capacity.md` for the header
trio `source:` / `verified-at:` / `recheck:`). Content: the three outcome classes the adapter
produces, the refusal envelope (`error` object with exactly `code`, `message`, `type`; adapter
messages vs schema bounds messages; one adapter error surfaces as HTTP 500 `server_error`), the
alias mapping rule (schema-declared aliases resolve OpenAI names; unknown keys are copied then
pruned, which is why they are silently ignored), and the observability boundary (`/slots` params).
Cite the pinned lines by file:line @ 704366d. Keep it to what the frozen counter can re-derive;
state the limits explicitly.
