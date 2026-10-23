/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim — let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.

# Item ExecC2CrossCheck — independent second derivation of the C2 population
Claim served: C2 (calibration), falsification seat.
Independently re-derive the C2 population from `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md` at 0e6f8ed6891c09d5208ac1fdcb294ed9a842832e WITHOUT reading
count-c2.py's code: enumerate every data row of every table whose first column header is `Claim`
(write your own small script; put it in
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w1/out/ExecC2CrossCheck/census.py`), and for each row record whether a
commit token in the row resolves (`git rev-parse --verify --quiet <tok>^{commit}`) and is an
ancestor of 0e6f8ed6891c09d5208ac1fdcb294ed9a842832e (`git merge-base --is-ancestor`), and whether at least one named path exists at
the tip (`git cat-file -e <tip>:<path>`). Write `census.tsv` and a `diff.md` that compares your
population and your failing set with the counter's `--list` output (run the counter only after your
own census is written). Any row where you and the counter disagree is a counter defect: name it.
