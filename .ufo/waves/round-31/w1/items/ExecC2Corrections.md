/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim — let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.

# Item ExecC2Corrections — the C2 correction rows
Claim served: C2 (calibration, predicate frozen).
In your own scratch clone of the lane at 0e6f8ed6891c09d5208ac1fdcb294ed9a842832e, run
`/usr/bin/python3 .ufo/waves/round-31/count-c2.py --repo . --tip 0e6f8ed6891c09d5208ac1fdcb294ed9a842832e --list --out out.json`
and capture every failing row (id, round, class, exact observed string). Then write the appended
section body for `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w1/out/ExecC2Corrections/corrections.md`:
the heading `## Round 31 — claim-row evidence corrections`, one sentence of provenance (counter
sha256, tip), then the table `| id | row | class | observed |` with one row per failure, id =
`CR31:<round>:<row id verbatim>:<class>`, observed byte-identical to the counter's string.
Then prove it: append that section to your clone's SCORECARD.md, commit, and run the counter again;
paste the before and after summary lines in `receipt.txt`. It must read
`rows 28 base_mismatched 13 ... valid_corrections 13 false_corrections 0 unresolved 0
append_only True met True`; if any count differs, report the exact difference instead of adjusting
the predicate.
