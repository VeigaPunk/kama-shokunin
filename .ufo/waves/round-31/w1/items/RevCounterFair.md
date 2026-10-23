/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim — let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.

# Item RevCounterFair — is the C1 counter honest about its own class?
Claim served: C1 (depth) and calibration.
Read `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/count-c1.py` (frozen, sha256 d86c4a94…) and its docstring. Build,
in your own scratch clone, three adversarial fixtures and report what happens:
1. a row whose `ignored` claim is true only because the normalized response check omits a field that
   actually changed (find a body key whose effect escapes (top_keys, n_choices, choice_keys,
   has_logprobs, usage_keys, prompt_tokens)) — e.g. try a parameter that changes generation without
   changing any of those;
2. a row whose `slot` value matches only because the base request already had that value (an
   identity claim dressed as a mapping: `set` key ≠ param but value equal to the base's);
3. a `reject` row whose message is copied from the schema bounds text (should be refused as
   not-adapter).
Write `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w1/out/RevCounterFair/findings.md` with the exact counter output
for each fixture and a verdict per fixture: `counter-holds` or `counter-defect` (with the fix the L1
should apply only if the counter is not yet frozen — it is frozen, so name the limitation instead).
