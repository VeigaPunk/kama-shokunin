# VerifyRefPaste — correction rows vs frozen-counter observed values (round-29 w2)

**Verdict: PASS — 11/11 correction rows at tip `513eba3b` match the frozen counter's observed value exactly; no mismatch.**

Evidence (full report: `.ufo/waves/round-29/w2/out/kama-r29-w2-VerifyRefPaste/report.md`, artifacts `receipt.json`, `diff-out.json`, `diff.py` alongside):

- Fresh clone `/tmp/kama-r29-w2-VerifyRefPaste/clone` at `513eba3ba51a142c9936553e3a85918345eb5c4c`.
- Counter hash in clone == lane tree copy == frozen `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`.
- Run: `python3 .ufo/waves/round-29/count-c1.py --repo <clone> --tip 513eba3b… --out receipt.json --list` → exit 0, stdout `statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip 513eba3ba51a` (matches inherited receipt byte-for-byte).
- Independent mechanical diff of the 11 rows under `## Round 29 — self-assessment corrections` in `513eba3b:SCORECARD.md` against per-statement `observed`: `rows_exactly_match_counter 11/11`, `rows_not_matching []`, `duplicate_sids []`, row-sid set == mismatch-sid set, append-only independently confirmed (tip blob 107,505 B is strict prefix-extension of base `2aa46e2` blob 104,553 B).
- Observed cells: 7× `q:no-artifact` (Q sids `f4c42debcc:0`, `f4c42debcc:2`, `4f8083e30a:0`, `0ccd533544:0`, `4c5d902830:0`, `f1021c03db:0`, `a7e98b1030:0`), 4× `p:absent` (P sids `980355388a:0`, `312b3e69b1:0`, `1c6c1f3e4c:0`, `17a7db7c81:0`) — every row's last cell equals the counter's observed string verbatim.

No tool installs; system python3 + `/usr/bin/git` only. No lane mutation.
