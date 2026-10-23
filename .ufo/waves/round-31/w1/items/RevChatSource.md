/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim — let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.

# Item RevChatSource — reverse-check the adapter source against the planned rows
Claim served: C1 (depth), falsification.
Read the pinned `server-common.cpp` chat parser end to end
(/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/sources/llama.cpp-704366d/server-common.cpp around lines 1326-1560) and
write `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w1/out/RevChatSource/findings.md`:
1. For each of these planned rows, state whether the source alone predicts the outcome class or
   whether the live measurement is required: max_tokens (alias), logprobs/top_logprobs, `user`,
   `parallel_tool_calls`, `tools`, `n`, `stream`, `stream_options`, the four adapter rejections,
   json_schema+grammar (status class).
2. Name at least three candidate rows the source suggests that the plan does not have, and which
   observable would decide them (slot delta, response check, status).
3. Name any planned row you believe will FAIL the counter's discrimination rule (e.g. because the
   schema declares it or the message is a schema bounds message) and why.
