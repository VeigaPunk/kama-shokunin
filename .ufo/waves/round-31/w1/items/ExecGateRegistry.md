/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim — let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.

# Item ExecGateRegistry — instrument registry completeness gate
Claims served: operability (repairs).
Run `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/gate-registry-check.py --rev 0e6f8ed6891c09d5208ac1fdcb294ed9a842832e` from the lane root and record the
full output and exit code in `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w1/out/ExecGateRegistry/gate.out`. Then list
every tracked `.ufo/waves/round-*/count-*.py` path at 0e6f8ed6891c09d5208ac1fdcb294ed9a842832e that does NOT occur in SKILL.md
(`git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree -r --name-only 0e6f8ed6891c09d5208ac1fdcb294ed9a842832e | grep -E '^\.ufo/waves/round-[0-9]+/count-.*\.py$'`)
and the SKILL.md line that registers each of the others. Write `unregistered.txt` and a
`recommendation.md`: the exact registry row text the round must add for round-31's two counters so
the gate passes at the landing tip.
