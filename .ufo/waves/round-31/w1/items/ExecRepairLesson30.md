/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim — let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.

# Item ExecRepairLesson30 — round-30 routed defects 1, 5, 6, 7
Claims served: none (routed repairs).
Read `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-30.md` and `round-30-verifier-spotcheck.md` (defects 1, 5, 6, 7).
Produce `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w1/out/ExecRepairLesson30/corrections.md` containing four
appended correction records, each with a one-command proof:
(1) list the two round-30 report commits the spot-check found missing from the landed-changes table
(`git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --format='%h %cI %s' 52ac3af8..043ba425`), so the round-31 report lists them;
(5) correct the two wrong receipt pointers in the lesson's `## Mistakes` (row 1's failing run has no
committed receipt; row 3 cites `long-digest-fix.json` for the `bound 68 unbound 4` reading that lives
in `bound68.json`) — re-derive both with `grep`/`git show` and paste the observed bytes;
(6) draft the reject rows the round-30 `## Gate` lacks (the C2 subject refusal and the CtlEditInPlace
rejection), each with the committed evidence path;
(7) note the frozen counter docstring drift (`## Round 29`/`SA29:` vs the code accepting Round 30 and
`SA30:`) as a limit of round-30's counter, to be cited (not fixed) by round 31.
Do not edit the lesson file; write the appended records only.
