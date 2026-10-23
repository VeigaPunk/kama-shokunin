# CtlDuplicate (executor)

Policy: duplicated rows. Run the counter at the freeze commit to get the 11 mismatches with exact observed values, append the frozen heading and every correct row TWICE (22 rows), commit and score. Then, as a second receipt (receipt-2.json, counter-2.out), keep one copy and add one extra row naming a statement that holds, with its observed string `ok`; commit and score again.

Your item name: CtlDuplicate. Output dir: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlDuplicate/. Clone path: /fast/scratch/hyaku/kama-r29/ctl/CtlDuplicate/repo.
