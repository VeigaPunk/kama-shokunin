/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim — let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.

# Item CriticIgnoredClass — attack the `ignored` outcome class
Claim served: C1 (depth), falsification.
The C1 rows K31-13/14/15 claim `user`, `parallel_tool_calls` and `tools` are ignored: no slot
parameter changes and the normalized response is unchanged. In your own scratch clone, measure
those three live (pinned server, free port, base body
`{"messages":[{"role":"user","content":"hi"}],"max_tokens":1}`) and look specifically for effects
the counter's normalization would miss: the server log, `/metrics` if enabled, prompt token counts,
timings, choice text distribution over 20 repeats, and whether `tools` changes the rendered prompt
(`usage.prompt_tokens`). Write `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w1/out/CriticIgnoredClass/findings.md`
with, per parameter, `ignored-confirmed` or `ignored-wrong` plus the observation that decides it, and
say which of the three is the weakest claim.
