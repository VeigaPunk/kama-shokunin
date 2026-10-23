/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim — let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.

# Item ExecCensus — the mandatory corpus census, before and after
Claims served: frontier step (SOURCES conformance).
Run, from `/home/vgpnk/Projects/shokunin`:
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`
and record its exit code and full output in
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w1/out/ExecCensus/census-start.txt`. Then count the SOURCES rows and the
tiers (`grep -c '^| S[0-9]' /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`, and the tier column distribution) and write
`counts.txt`. Do not edit SOURCES.md; the L1 lands rows. If the census exits nonzero, paste its
stderr verbatim and name which row fails.
