/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim — let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.

# Item MutC2 — mutate SCORECARD and see whether the C2 counter notices
Claim served: C2 (calibration), fail-capability of the instrument.
In your own scratch clone at 0e6f8ed6891c09d5208ac1fdcb294ed9a842832e, apply five mutations to SCORECARD.md, one commit each, and run
the frozen C2 counter at each commit:
M1 delete one claim row from a table; M2 change a claim row's measured-commit token to a
non-existent hash; M3 point one row's evidence at a path that does not exist; M4 replace a pinned
counter sha256 with a wrong full digest; M5 duplicate a claim row id.
Write `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w1/out/MutC2/results.md` with the exact summary line per mutation
and a verdict per mutation: `caught` (met False or the expected counter class changes) or
`survived` (the counter still says met True). A survivor is a defect to report; do not edit the
counter.
