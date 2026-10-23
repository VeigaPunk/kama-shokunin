# VerifyRefPaste — correction rows vs frozen-counter observed values (round-29 w2)

**Seat:** kama-r29-w2-VerifyRefPaste · **Claim:** C1 (calibration) · **Item:** mechanically diff the 11 SCORECARD.md correction rows at tip `513eba3b` against the frozen counter's per-statement observed values.

## Verdict

**PASS — 11/11 correction rows match the counter's observed value exactly. No mismatch found; nothing to report to the L1.**

## Method (fresh clone, frozen counter, committed objects only)

1. Fresh clone of `/home/vgpnk/Projects/shokunin/kama-shokunin` into `/tmp/kama-r29-w2-VerifyRefPaste/clone`, checked out at the data commit:
   - `git rev-parse HEAD` → `513eba3ba51a142c9936553e3a85918345eb5c4c`
2. Counter hash freeze verified in the clone **and** against the lane working-tree copy (read-only):
   - `sha256(clone/.ufo/waves/round-29/count-c1.py) = fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`
   - `sha256(/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py)` = identical → the file I ran is the frozen counter.
3. Ran: `python3 .ufo/waves/round-29/count-c1.py --repo /tmp/kama-r29-w2-VerifyRefPaste/clone --tip 513eba3ba51a142c9936553e3a85918345eb5c4c --out receipt.json --list` (exit 0)
   - stdout: `statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip 513eba3ba51a`
   - byte-for-byte match with the inherited fresh-clone receipt.
4. Independently re-parsed `513eba3b:SCORECARD.md` corrections section (heading `## Round 29 — self-assessment corrections`, em-dash) and mechanically diffed each row's **last cell** (observed column; 7-col table `| id | line at base | class | statement token | W | cause | observed |`) against `receipt.json` per-statement `observed`. Diff script: `…/w2/out/kama-r29-w2-VerifyRefPaste/diff.py`; full machine output: `…/out/kama-r29-w2-VerifyRefPaste/diff-out.json`; receipt: `…/out/kama-r29-w2-VerifyRefPaste/receipt.json`.

## Per-row diff (11 rows; `row_cell` vs `counter_observed`, exact string equality after backtick/whitespace strip — same normalization the counter applies)

| # | sid | row last cell | counter observed | match |
|---|-----|---------------|------------------|-------|
| 1 | `SCORECARD.md:Q:f4c42debcc:0` (line 20, W `ea72c3ea`) | `q:no-artifact` | `q:no-artifact` | ✅ |
| 2 | `SCORECARD.md:Q:f4c42debcc:2` (line 20, W `ea72c3ea`) | `q:no-artifact` | `q:no-artifact` | ✅ |
| 3 | `SCORECARD.md:P:980355388a:0` (line 192, W `1e41928a`) | `p:absent` | `p:absent` | ✅ |
| 4 | `SCORECARD.md:Q:4f8083e30a:0` (line 211, W `40660352`) | `q:no-artifact` | `q:no-artifact` | ✅ |
| 5 | `SCORECARD.md:P:312b3e69b1:0` (line 740, W `c6dc46fa`) | `p:absent` | `p:absent` | ✅ |
| 6 | `SCORECARD.md:Q:0ccd533544:0` (line 823, W `7229fa95`) | `q:no-artifact` | `q:no-artifact` | ✅ |
| 7 | `SCORECARD.md:Q:4c5d902830:0` (line 824, W `7229fa95`) | `q:no-artifact` | `q:no-artifact` | ✅ |
| 8 | `SCORECARD.md:Q:f1021c03db:0` (line 833, W `7229fa95`) | `q:no-artifact` | `q:no-artifact` | ✅ |
| 9 | `SCORECARD.md:Q:a7e98b1030:0` (line 834, W `7229fa95`) | `q:no-artifact` | `q:no-artifact` | ✅ |
| 10 | `SCORECARD.md:P:1c6c1f3e4c:0` (line 1349, W `7f84cd0e`) | `p:absent` | `p:absent` | ✅ |
| 11 | `SCORECARD.md:P:17a7db7c81:0` (line 1375, W `d183ec57`) | `p:absent` | `p:absent` | ✅ |

Also checked, all true:
- `rows_not_matching = []` · `duplicate_sids = []`
- Row sid set **==** counter mismatch sid set (no extra rows, no missing rows; `mismatch_sids_without_row = []`, `row_sids_not_in_mismatches = []`) — consistent with "exactly one correction row per false statement".
- All 11 false statements are in SCORECARD.md (7 Q of 25, 4 P of 10); SHONEN.md contributed 0 of the 11 (by_class C27 H2 N2 P10 Q25 T3 = 69).
- Independent append-only check: `tip:SCORECARD.md` (107,505 B) is a strict byte-prefix extension of `base 2aa46e2:SCORECARD.md` (104,553 B); appended bytes begin `\n## Round 29 — self-assessment corrections…`.

## Residual risk / verification gaps

- The counter's `observed` strings are class-level diagnostics (`p:absent`, `q:no-artifact`) defined by `check()`; equality is exact against those strings — a wrong *cause* narrative in a row is out of this item's scope (w1 Confirm seats own per-cause verification).
- Single counter execution (deterministic inputs: pinned `/usr/bin/git`, `--no-replace-objects`, committed blobs only; no reason to expect nondeterminism, not re-run).
- My row parser mirrors the counter's row grammar (`SA29:` first cell, last cell = observed); the raw table lines in `diff-out.json` make the parse auditable.

## Tooling record

No tools installed (operator 2026-10-19 authorization unused). Used system `python3` and git (`/usr/bin/git`, the counter's pinned binary). No pacman. No lane repo/index/jj mutation; scratch confined to `/tmp/kama-r29-w2-VerifyRefPaste` and this seat's out dir.
