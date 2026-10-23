/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim — let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.

# Item ExecRepairReport — report-commit and digest discipline (round-30 defects 1 and 2)
Claims served: none (routed repairs).
Produce `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w1/out/ExecRepairReport/checklist.md`: (a) the exact command
sequence that lists every lane commit of a round (`git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --format='%H %cI %s'
<round-start>..<round-end>`) and the rule that the report's Landed-changes table names every one of
them; (b) a command that extracts the report's cited commit tokens and verifies each is an ancestor
of the lane tip (`git cat-file -t`, `git merge-base --is-ancestor`); (c) the dating rule: a
completion digest must not postdate the lane tip's committer time — give the command that compares
them. Run all three against the round-30 report and lane tip and paste the output (this is a check
of the previous round's record, not a claim).
