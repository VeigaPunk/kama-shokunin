# CtlAllFalse (mutation-tester)

Policy: all-false. Run the frozen counter once with `--list` on the clone at the freeze commit (output to /fast/scratch/... not the lane) only to obtain the list of ALL statement sids (`all_statements`), but ignore its `holds`/`observed` fields. Append the frozen heading and one row per statement (69 rows) asserting the class's failure string as observed: P -> `p:absent`, H -> `h:absent`, N -> `n:absent`, C -> `c:unresolved`, T -> `t:future`, Q -> `q:no-artifact`. Commit and score.

Your item name: CtlAllFalse. Output dir: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlAllFalse/. Clone path: /fast/scratch/hyaku/kama-r29/ctl/CtlAllFalse/repo.
