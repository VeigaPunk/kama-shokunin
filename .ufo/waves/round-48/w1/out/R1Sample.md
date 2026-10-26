# R1Sample — hand-check of v3's ungraded lines (round-48 C1, SCORECARD.md)

**Verdict:** the build's counts are correct — at `380bcdff` v3 grades `dd9f5dc6`/SCORECARD.md **14 graded / 17 ungraded** and `0718b6ab`/SCORECARD.md **2349 / 72**, reproduced line-by-line here with the frozen counter's own semantics; the entire 17-vs-8 gap to Rev1Restore's round-47 proposal (23/8) is exactly the **9 deleted `## Planned` lines (parent 60–68)**, which the window-maximum rule exempts because that section regrew to **18 lines at round-43 `9307b15e0731`** (≥ parent 12) while every tip holds only 4; **none of the 9 is a real loss** — all 9 survive verbatim at the tip under `## Historical head sections (superseded in round 42)` — but the exemption is granted by a content-blind count (the regrown 18 lines are different text), a designed and selftest-covered trade-off; at `0718b6ab` the 72 ungraded lines decompose **Axes 42 / Capabilities 18 / Planned 4 / Retired 4 / Saturation 4**, are identical under both rules, and **7 of the 72 are no longer present at the tip** (declared re-derived head rows re-anchored in place by rounds 46–47 — ungraded by declaration, not by the window rule). No defect found in the build or the frozen counters.

## 1. Method and grounding

Semantics taken from the frozen contract, not re-derived: `tools/round48-append-audit-v3-check.py` docstring `section` :48-50, `count(T,x)` :51, `eligible` :52-53, `graded G` :54-56, `ungraded` :57, `status` :60-61, `regressed` :62, `exit` :63-65; implementation `sections()` :267-274, **`window = order[i:]`** :339 (the event commit and every commit after it, up to `--to`), eligible max-over-window :350-353, graded loop :354-360. Same definitions in the build-tip tool (`git show 380bcdff:tools/append-only-audit.py`, 898 lines; docstring :22-29, `sections()` :231, `window = commits[i:]` :404, eligible :409-411). My analysis script **imports the frozen counter module and calls its own `sections`/`del_positions`/`Blobs`** — zero re-implementation drift (copy: `out/R1Sample/analyze.py`).

Grounding runs of the real instrument (receipts copied to `out/R1Sample/`):

```
python3 aoa-v3-at-build.py --repo $S/lane --to 380bcdff9c8af06997c482f6eb03db926a794a2b \
        --contract contract-at-build-tip.tsv --json     # exit 0
#   dd9f5dc6c0e6 SCORECARD.md deleted 31 graded 14 ungraded 17 restored_max 14 restored_best dd9f5dc6 status restored
#   0718b6abbda6 SCORECARD.md deleted 2421 graded 2349 ungraded 72 restored_max 2349 restored_best 82b5e9d3 status restored
#   summary: events 5 restored 5 ungraded_lines 89 regressed 0 vanished 0 bad_declarations 0
python3 aoa-v3-at-build.py --repo $S/lane --to 33e005827742b29772b153cda036ec9f27f653be \
        --contract contract-at-build-tip.tsv --json     # exit 1
#   same events, but 0718b6ab held_at_to 2348 < restored_max 2349 -> regressed 1
```

This confirms both claimed counts and the build's own banner finding (at the base the round-45 authority banner, a section-`None` line, had been rewritten in place by rounds 46–47; the build re-appended it byte-exact, restoring `held_at_to` 2349 at the tip).

## 2. `dd9f5dc6` (parent `0bfd47ab`, round-42 pre-state) — the 31 deleted lines, one by one

Per-line TSV with every field: `out/R1Sample/dd9-perline.tsv`. The 31 deleted parent positions form six contiguous runs:

| parent lines | parent section | n | eligible under v3 window-max? (line counts) | ungraded by v3 | ungraded by Rev1 tip-only | old text present at tip beyond kept |
|---|---|---|---|---|---|---|
| 6–13 | `None` — round-5 authority banner, before the first `## ` heading | 8 | n/a — `None` is not a declared exempt title, so graded by the `graded G` rule (:54-56) | no (graded) | no | yes (8/8) |
| 17 | `## Axes` — the "Reconciled in round 41 …" paragraph | 1 | **yes** — parent 43, window max 43 @ `dd9f5dc6` itself | **yes** | yes | **no** — re-derived in place (new sha256s/scores) |
| 21–26 | `## Axes` — the six axis rows (operability…adjacency) | 6 | **yes** — 43 ≥ 43 | **yes** | yes | **no** — re-derived in place |
| 60–68 | `## Planned` — round-5 plan body (incl. blank line 65) | 9 | **yes** — parent 12, window max **18 @ `9307b15e0731`** (round-43) | **yes** | **no (graded)** — tip 4 < 12 | **yes** — 8 non-blank at tip lines 156–164, blank trivially |
| 72–77 | `## Retired` — "None. Both assigned axes…" body | 6 | **no** — parent 9, window max 4 @ `dd9f5dc6`, never regrew | no (graded) | no | yes (6/6) |
| 143 | `## Saturation` — the `## Saturation` heading line itself | 1 | **yes** — 4 ≥ 4 | **yes** | yes | yes |

Totals: deleted 31 = 8+1+6+9+6+1. **v3: graded 14 = banner 8 + Retired 6; ungraded 17 = Axes 7 + Planned 9 + Saturation 1** (matches the tool: graded 14, ungraded 17, restored_max 14, restored at `dd9f5dc6` itself). **Tip-only: graded 23 = banner 8 + Planned 9 + Retired 6; ungraded 8 = Axes 7 + Saturation 1** (matches Rev1Restore's measured `deleted=31 graded=23 exempt=8` at their tip `3a09a1d9`, and my recomputation of their guard at both tips).

Counts per exempt title (`count(T,x)`, the "show the line counts" table; `## Capabilities` has 0 deleted lines at this event, shown for completeness):

| title | parent `0bfd47ab` | @`dd9f5dc6` | @`82b5e9d3` | r47 tip `3a09a1d9` | base `33e00582` | tip `380bcdff` | window max (argmax) | eligible window-max | eligible tip-only |
|---|---|---|---|---|---|---|---|---|---|
| `## Axes` | 43 | 43 | 43 | 43 | 43 | 43 | 43 @ `dd9f5dc6` | yes | yes |
| `## Capabilities` | 8 | 17 | 18 | 19 | 20 | 20 | 20 @ `383f1fc7` (r47 integration) | yes | yes |
| `## Planned` | **12** | 4 | 4 | 4 | 4 | **4** | **18 @ `9307b15e0731`** (round-43) | **yes** | **no** |
| `## Retired` | **9** | 4 | 4 | 4 | 4 | 4 | 4 @ `dd9f5dc6` | **no** | no |
| `## Saturation` | 4 | 4 | 4 | 4 | 4 | 4 | 4 @ `dd9f5dc6` | yes | yes |

Independent cross-check of the argmax (plain section walk over `git show`, same `## ` rule): `## Planned` = **18** at `9307b15e0731`, **12** at parent `0bfd47ab`, **4** at tip `380bcdff`.

## 3. Why 17, not 8

Rev1Restore's guard: honour a title only when the section holds at least as many lines **at the audited revision (tip)** as at the event's parent (Rev1Restore.md §3). v3's guard: the **maximum over the window** (event commit → tip, counter :339/:350-353). Since the tip is in the window, window-max is strictly more permissive; the delta is precisely sections that shrank by the tip but regrew mid-window. 2×2 decomposition for this event:

| rule × tip | graded/ungraded |
|---|---|
| window-max @ `380bcdff` (the build) | **14/17** |
| window-max @ `3a09a1d9` (r47 tip) | 14/17 — the round-43 argmax `9307b15e` is an ancestor of the r47 tip (`git merge-base --is-ancestor` rc=0) |
| tip-only @ `380bcdff` | 23/8 |
| tip-only @ `3a09a1d9` (Rev1's measured run) | 23/8 |

So the difference is **entirely the rule, not the tip move**: the 9 delta lines are parent 60–68, all `## Planned` (the round-5 plan body: "After operator-owned route/binding repair…", "Declared-vs-served context size…", plus the blank line 65). `## Planned` shrank 12→4 at `dd9f5dc6` and never exceeded 4 at any tip, so tip-only grades its 9 deleted lines; the window max catches round-43's unrelated regrowth to 18 and exempts them.

## 4. Are the 9 extra ungraded lines a real loss hidden by the window rule?

**No.** Per-line beyond-kept presence at tip `380bcdff`: all 8 non-blank texts sit at tip lines 156–164 under section `## Historical head sections (superseded in round 42)` — relocated verbatim by `dd9f5dc6` itself (the same commit that deleted them; the graded set's `restored_best=dd9f5dc6` shows the same relocation pattern); the blank line 65 is trivially present. Aggregate: 162 deleted-text occurrences present beyond kept at the tip — 139 blank lines plus 23 non-blank texts, each present exactly once beyond kept (the round-5 banner texts are not duplicated; the build's appended `### Superseded head banners` carry the r45/r46 banner text).

But the exemption is **not granted by that survival**. At the window argmax `9307b15e0731` the deleted texts sit under `## Historical…` (line 168 there), and `## Planned`'s 18 lines are later rounds' different content — the rule checks a count, not content. This is designed and selftest-covered: `t_exempt_gutted_then_regrown` (`tools/append-only-audit.py` at `380bcdff` :774-782) commits a section gutted at the event and regrown with different content, and asserts eligible → ungraded → exit 0. So the honest characterization: **nothing is hidden in this history (survival verified per line), and the behavior is intended — but the protection these 9 lines received is accidental to their relocation.** Had the round-42 commit rewritten the `## Planned` body in place (as it did the 7 `## Axes` rows, whose old text is genuinely gone at the tip), the same regrowth eligibility would have ungraded a real 9-line loss. Closing that would need a content-survival check for exempt lines — out of scope for the frozen contract; recorded as residual risk, not a defect.

Related asymmetry worth recording: `## Planned` (exempt) and `## Retired` (graded) received the **identical** treatment at `dd9f5dc6` — both bodies relocated verbatim under `## Historical…` — yet are classified differently, solely because `## Planned` later regrew (round-43, unrelated content) and `## Retired` never exceeded 4. Under Rev1's tip-only guard both are graded and both restored; the verdict (exit 0) is the same either way — the difference is bookkeeping plus the future-loss exposure above.

## 5. `0718b6ab` (parent `21945c61`, round-45 pre-truncation) — the 72 ungraded lines

The round-45 append-bug truncation (2429 → 17 lines), repaired byte-exact at `82b5e9d3` except the depth row. Deleted 2421 by parent section:

| parent section | deleted | ungraded by v3 | ungraded by tip-only |
|---|---|---|---|
| `None` (head banner lines) | 4 | 0 (graded) | 0 |
| `## Axes` | 42 | **42** | 42 |
| `## Capabilities` | 18 | **18** | 18 |
| `## Planned` | 4 | **4** | 4 |
| `## Retired` | 4 | **4** | 4 |
| `## Saturation` | 4 | **4** | 4 |
| dated/other `## ` sections | 2345 | 0 (graded) | 0 |
| **total** | **2421** | **72** | 72 |

Graded 2349 = 4 + 2345. All five exempt titles are eligible under **both** rules at both tips (parent 43/18/4/4/4 vs tip `380bcdff` 43/20/4/4/4; window argmax: Axes 43 @ `82b5e9d3`, Capabilities 20 @ `383f1fc7`, Planned 17 @ `4991ecc2` (round-46), Retired 4 @ `82b5e9d3`, Saturation 4 @ `82b5e9d3`). **v3 equals Rev1Restore's proposal exactly on this event** (their `deleted=2421 graded=2349 exempt=72`, same per-section split) — no rule sensitivity here. `restored_max` 2349 = graded, `restored_by 82b5e9d3`; `held_at_to` 2349 at the tip (2348 at the base → the regressed=1 banner finding, §1).

Observation: **7 of the 72 ungraded lines are no longer present at the tip beyond kept** — parent 16 (`## Axes` depth row, rewritten already in the repair, as Rev1Restore found), and parent 17 (coverage row), 18 (calibration row), 53 (`## Planned` "Superseded in round 42…" pointer), 57 (`## Retired` "None. 6 axes…" line), 117 (`## Capabilities` mirror line), 135 (`## Saturation` "8/10" line) — the latter six present at the repair commit `82b5e9d3` and re-anchored in place later by the declared head re-anchors of rounds 46–47; all seven already absent at the base `33e00582`. All seven sit in the five declared re-derived head sections, so they are ungraded **by declaration under both rules** — not a window-rule artifact, and the same class as the build's banner finding except that the banner (section `None`) is graded, which is why the build had to re-append it byte-exact while these needed nothing. Recorded for calibration honesty: ungraded ≠ present.

## 6. Findings

1. **No defect.** Build counts confirmed byte-level: `dd9f5dc6` 14/17, `0718b6ab` 2349/72, `ungraded_lines=89`, exit 0 at `380bcdff`, exit 1 with regressed=1 at the base — all as claimed; per-line reproduction used the frozen counter's own functions.
2. **Observation (calibration; no contract change proposed):** window-max eligibility is a content-blind count proxy — designed and selftest-covered (`t_exempt_gutted_then_regrown`, tool :774-782). At `dd9f5dc6` it ungrades 9 `## Planned` lines whose survival is verified, but the grant comes from round-43's unrelated regrowth to 18; a real loss in a regrown exempt section would be ungraded. Residual risk as designed.
3. **Observation:** 7 of `0718b6ab`'s 72 ungraded lines are absent from the tip (declared re-derived head rows, re-anchored rounds 46–47). Consistent with `SCORECARD.md:6`'s declaration and with both guards; not hidden by the window rule.
4. **Observation:** the `## Planned`-vs-`## Retired` classification asymmetry at `dd9f5dc6` (identical relocation, different verdict) is driven by unrelated later section growth; verdict-neutral here (exit 0 under both rules).

No tool installs or upgrades were performed (operator directive 2026-10-19: nothing to record).

## 7. Commands

```
S=/fast/scratch/hyaku/kama-r48/R1Sample
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"   # read-only use only
git -C "$S/lane" show 380bcdff9c8af06997c482f6eb03db926a794a2b:tools/append-only-audit.py > "$S/aoa-v3-at-build.py"
git -C "$S/lane" show 380bcdff9c8af06997c482f6eb03db926a794a2b:registry/append-only-contract.tsv > "$S/contract-build.tsv"
python3 "$S/aoa-v3-at-build.py" --repo "$S/lane" --to 380bcdff9c8af06997c482f6eb03db926a794a2b --contract "$S/contract-build.tsv" --json   # exit 0
python3 "$S/aoa-v3-at-build.py" --repo "$S/lane" --to 33e005827742b29772b153cda036ec9f27f653be --contract "$S/contract-build.tsv" --json   # exit 1, regressed 1
python3 "$S/analyze.py"                 # imports the frozen counter; per-line tables + eligibility + presence checks
# targeted checks (inline in session): tip locations of the 9 Planned texts; 7-of-72 presence at
# tip/base/r47tip/82b5e9d3; merge-base --is-ancestor for the 2x2; independent ## Planned counts (18/12/4)
```

## 8. Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/R1Sample.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/R1Sample/dd9-perline.tsv` (the 31 deleted lines: position, section, all three rule verdicts, tip presence, text)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/R1Sample/0718-ungraded-lines.txt` (the 72 ungraded lines with parent position and section)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/R1Sample/tool-tip380.json`, `tool-base33e00582.json` (real-instrument grounding receipts)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/R1Sample/summary.json` (counts, eligibility sets, delta lines)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/R1Sample/analyze.py`, `append-only-audit-v3-at-380bcdff.py`, `contract-at-build-tip.tsv` (method reproducibility)

Scratch `/fast/scratch/hyaku/kama-r48/R1Sample` removed at completion.
