# L1Lowthr — round-47 sub-20-line deletion census (C1 calibration attack)

**Verdict: hypothesis FALSIFIED.** Below the 20-line threshold the contract's files show **22 deletion events in `corpus/lessons/*.md`** (all unrestored; the claim asserts none at all), **0 in `registry/history/DELTA.md`** (that clause holds), and **12 in `LOG.md`** of which only 4 were restored, 7 are in-place rewrites (corrections that replace old lines rather than append), and 1 (ed135b3cb869, −7, partial) lost a 6-line record (the HOURS.md ledger-opening entry) that was never restored and nothing superseded. One unexplained loss falsifies; there are several.

## Method and command

Read-only clone of the lane into scratch (`git clone --shared`), then the frozen v2 tool at the build commit:

```
$ python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py \
    --repo $S/lane --to 3a09a1d93dcc16799cf6c4b48786e6440af134c4 \
    --contract /home/vgpnk/Projects/shokunin/kama-shokunin/registry/append-only-contract.tsv \
    --threshold 1 --json > audit-threshold1.json
exit=1
```

- schema `append-only-audit/v2`, to `3a09a1d93dcc16799cf6c4b48786e6440af134c4`, threshold 1, 303 commits, 85 files (contract expansion incl. 79 `corpus/lessons/*.md` and `registry/history/DELTA.md`), **91 events**: 5 with `deleted >= 20`, 86 with `deleted < 20`.
- Each sub-20 event's `-U0` diff was read (full `-U0` diff per event in `sub20-diffs.txt`; the deleted lines themselves in `sub20-deleted.txt`; per-event table in `sub20-events-classified.tsv`).
- `--threshold 1` does not change the audit semantics; it only lowers the event gate so every non-empty deletion is reported (the tool requires hunk count == numstat for every event, so the counts are byte-exact).

## Counts per class (sub-20 events)

| class | events | restored | partial | unrestored |
|---|---|---|---|---|
| corpus/lessons/*.md | **22** | 0 | 0 | 22 |
| registry/history/DELTA.md | **0** | 0 | 0 | 0 |
| LOG.md | **12** | 4 | 1 | 7 |
| SCORECARD.md (info) | 24 | 2 | 4 | 18 |
| corpus/README.md (info) | 7 | 1 | 1 | 5 |
| corpus/QUALITY.md (info) | 1 | 0 | 0 | 1 |
| corpus/SOURCES.md (info) | 20 | 2 | 0 | 18 |

## Part A — "no deletion in corpus/lessons/*.md at all": FALSE

22 deletion events in filed lessons, 1–17 deleted lines each, **all** `unrestored` (restored_max = 0 — the deleted bytes never reappear in that file later):

- `ea72c3eae4ec` round-1.md −2 (path-fix + appended errata)
- `ccc4bb31267f` round-16.md −11 (paragraph rewritten; 93 lines appended)
- `028235e6f28d` round-18.md −1; `1b85a24eca4d` round-18.md −1; `30ed37837782` round-18.md −1; `f1790e25b421` round-18.md −1
- `028235e6f28d` round-19.md −1; `5b108c1a7e94` round-19.md −3; `f1790e25b421` round-19.md −2
- `a46a61815f79` round-25.md −2; `c0a9b029c035` round-25.md −8
- `fd48f9a3b7ca` round-26.md −17 (14 hunks rewritten)
- `4d2e74f421bc` round-27.md −5; `d183ec572a5e` round-27.md −8
- `9ce5bd377562` round-28.md −3; `c23ebaa4883a` round-28.md −3
- `cc4698035927` round-32-verifier-spotcheck.md −1 (typo fix)
- `d854475aecc1` round-38.md −11 (11-line paragraph collapsed to 1 line)
- `47f3aedd6fa3` round-4-recensus.md −1 (path `./` → `../`)
- `2429f48e2c67` round-40.md −1; `8bc8e3758248` round-42.md −4; `9307b15e0731` round-43.md −1

Most are in-place corrections (old wording replaced by corrected wording), which is exactly what `A-corr` says must NOT happen to a filed lesson ("filed lessons stay; corrections appended" — contract row `corpus/lessons/*.md`). Whether read as corrections or losses, the categorical claim "no deletion at all" is false.

## Part B — "no deletion in registry/history/DELTA.md at all": HOLDS

The audit reports no DELTA.md events at threshold 1. Direct cross-check (independent numstat scan of all 303 commits for `registry/history/DELTA.md`): total deleted lines = 0; file exists at tip with 22 lines (its two history touches are additions-only).

## Part C — "every LOG.md deletion of 1–19 lines was restored or is an appended correction": FALSE

12 events, the 8 non-restored ones are **in-place line replacements**, not appends (the old line is deleted and a corrected line occupies the same spot), and one is a genuine removal:

| commit | − | status | what happened |
|---|---|---|---|
| `33b167ecccab` | 1 | restored | exact bytes reappear later |
| `83bee7faf5a7` | 1 | restored | exact bytes reappear later |
| `84a81304d7b0` | 1 | restored | exact bytes reappear later |
| `ea72c3eae4ec` | 1 | restored | exact bytes reappear later |
| `ed135b3cb869` | 7 | **partial** | **HOURS.md ledger-opening entry (6 lines) deleted and never restored; nothing in LOG.md or the tree at tip mentions it; HOURS.md does not exist — unexplained loss** |
| `2c0181074050` | 1 | unrestored | sentence rephrased (added R42A05 needle-weakness clause); 2 lines appended |
| `47f3aedd6fa3` | 1 | unrestored | path reference fixed (`./` → `../`) |
| `8bee4e56a995` | 2 | unrestored | two bullets corrected numerically (nine→"base control and seven" controls; six→five Mistakes rows) |
| `9cb3abae9d48` | 1 | unrestored | "working-tree tool" → "landed tool at the round's tip" |
| `ce41bae692c8` | 4 | unrestored | draft placeholder finalization: `{{MEASURED_COMMIT}}`, `{{C1_AFTER_LINE}}`, `{{C2_AFTER_LINE}}`, `{{C3_AFTER_LINE}}` replaced by real values |
| `f4066979096e` | 3 | unrestored | wave-1 candidate sentence reworded (58 → 57 candidate entries + scout details) |
| `fd48f9a3b7ca` | 5 | unrestored | E26 "before" statement partially contradicted and corrected; dead-ports wording corrected; counts clarified; 3 paragraphs appended |

So: 4/12 restored; 7/12 are corrections that edit history in place (neither "restored" nor "appended"); 1/12 (ed135b3cb869) lost a log record outright. The HOURS-ledger removal alone falsifies Part C; the in-place rewrites contradict the lane's own `A-corr` note for LOG.md ("corrections land as new entries").

## Context: ≥20 events (C1 calibration window, same run)

- `dd9f5dc6c0e6` SCORECARD.md −31, partial (24/31 restored)
- `0718b6abbda6` LOG.md −2292, restored
- `0718b6abbda6` SCORECARD.md −2421, partial (2420/2421 restored) — matches the contract note that head-section re-anchors are expected partials
- `0718b6abbda6` corpus/QUALITY.md −375, restored
- `0718b6abbda6` corpus/README.md −663, restored

## Findings

1. **The <20-line appendix of the lane's append-only self-description does not hold.** The instrument (v2) itself only scores ≥20-line events; the sub-20 history contains 86 deletions, including 22 in filed lessons and 12 in LOG.md, with one clear content loss (HOURS ledger entry) and seven in-place log rewrites.
2. The lesson/LOG edits are overwhelmingly corrections (replacement of a wrong line by a right one at the same location). Under an append-only rule they should instead be new appended entries; the recorded practice edits in place.
3. DELTA.md is the one contract class with a clean record (zero deletions ever).

## Proposed smallest safe correction (finding, not a fix in place)

If the lane wants the sub-20 claim to survive, it must (a) stop in-place edits to `corpus/lessons/*.md` and `LOG.md` by making the append-only check operate at threshold 1 (or at least emit warnings for 1–19-line deletions), and (b) either restore or append an entry covering the 2026-10-13 HOURS.md ledger opening. Alternatively, weaken the claim to "no *unrestored* deletion of substantive content" — but that would still fail on ed135b3cb869.

## Evidence artifacts written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/L1Lowthr.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/L1Lowthr/audit-threshold1.json` (tool JSON output, exit 1)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/L1Lowthr/sub20-events-classified.tsv` (all 91 events, class/commit/file/deleted/status/restored_max)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/L1Lowthr/sub20-deleted.txt` (deleted lines per event)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/L1Lowthr/sub20-diffs.txt` (full `-U0` diffs per event)
