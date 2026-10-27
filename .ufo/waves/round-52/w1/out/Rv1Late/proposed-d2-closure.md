# D2 closure — ready-to-paste text (proposed by seat Rv1Late, round 52 w1)

Closure D2 says: "The report says it landed with '50 of 66' seat reports and lists V1Review as still
running. `1ab1de39` holds 51 seat reports, V1Review among them. File the correction (51/66, 15 running)
in the round-52 report."

The reconstruction refines that number (`timeline.md` §3). Paste the version below, because `51/66, 15
running` is right only under the top-level-`<Seat>.md` rule, and 4 of the 15 had already filed a report
inside their own seat dir.

## 1. Correction paragraph for the round-52 report (Wave / round shape or Errata section)

> **Round-51 D2 correction (count at filing).** The round-51 report of record (`39877b17`, fleet) says it
> landed with 50 of 66 seat reports and 16 still running. Recomputed over the tree that report cites
> (`1ab1de39`, lane): **51** top-level `<Seat>.md` reports, and **55** when a seat's report inside its own
> dir counts (the rule the wave's own `out/X6Hygiene/count_reports.py` applies: `K2Design/design.md`,
> `T4Quality/criteria.md`, `T6Skill/skill.md`, `Sim1/Sim1.md`). Command (exit 0):
> `git -C kama-shokunin ls-tree --name-only 1ab1de39 .ufo/waves/round-51/a2w1/out/ | grep -cE '\.md$'` → `51`;
> the any-`.md` rule is `timeline.md` §5.1 rule B → `55`. No commit yields 50. The `50` is one seat
> (`V1Review`, committed in `1ab1de39`) short of the tree: the count was taken while the report was being
> composed and never re-derived after the evidence commit. Sixteen names were listed as running; three
> (`M1Ctr`, `M2Live`, `V3Review`) kept working for another 19 min and landed in the salvage `9ff76b1f`;
> the other thirteen either had already filed inside their dir (4) or never filed (8: `Sen1Exe`,
> `Rev2Arow`, `Sen3Ledger`, `L6Slice`, `T1Lesson`, `X3R41`, `X5Census`, `X8Restore`). Final state at the
> round-52 tip `34d82600`: 54 top-level reports, 58 by the any-`.md` rule.

## 2. Proposed QUALITY row (append after KQ93; renumber to the next free id)

```
| KQ94 | A wave's seat count and "still running" list in a round report are derived by a stated command over the evidence commit — run after that commit — or are not written; if the round must be filed before the wave settles, the count names its commit, rule and command, and an erratum is appended when the wave settles (never an in-place rewrite) | a bare integer composed from a directory listing (round-51 report: `50 of 66`, no commit yields 50 — `1ab1de39` gives 51 top-level / 55 by the wave's own rule; `V1Review` landed between the count and the commit); a "still running" name with no liveness receipt; a corrected count left uncorrected in the report of record | `corpus/lessons/round-51-verifier-spotcheck.md` D1, D2; seat Rv1Late `.ufo/waves/round-52/w1/out/Rv1Late/timeline.md` |
```

Why calibration and not depth: the defect is a self-report that its own bytes falsify, and it survived the
lane's own instrument (X6Hygiene counted 52/66 and 52 at a stated second, `late-sample.txt` `### 4c`)
because the report cited no receipt. The criterion makes the receipt the admission condition.

## 3. Note for the L1, not a request to rewrite

`39877b17` is a committed report of record with exactly one commit; the family convention after filing is an
**appended** erratum (`round-37/kasegi.md` "WAVE-DONE addendum (appended after filing)",
`round-65/kumitate.md` "Erratum (appended after filing; supersedes …)"), and a round-51 seat's in-place
rewrite of its own committed report is D1's other half (restored at the round-52 build: `X7Regen.md`,
late rewrite filed as `X7Regen.late-rewrite.md`). So: land the correction in the round-52 report and
`QUALITY.md`, and leave the round-51 bytes alone.

## 4. Schema note the count cannot fix

`a2w1-results.json` has 66 entries, each `{name, agent, output, note}` — no `id`, no `status`, although the
prompt specifies both (`.ufo/prompts/kama-round-52.md:231`). Eight of the 66 `output` values are raw
transcript (`<think>` blocks, mid-sentence). A count read from that file therefore cannot separate a settled
seat from a dead one, which is why the round-51 sentence "no seat has been reported dead" is unfalsifiable
rather than false. If the L1 wants a checkable wave-status line this round, take it from the tree, not from
`results.json`; round-65 recorded the same gap in its erratum.
