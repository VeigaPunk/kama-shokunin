# X1Banner — round 48, lane kama (attack + frontier)

**Verdict: the build's banner finding is verified as stated.** `tools/append-only-audit.py` v3 exits 1 with `regressed=1` at the round-47 closure `33e00582` and exits 0 with `regressed=0` at the build `380bcdff`; the single graded line behind the difference is the round-45 authority banner (`SCORECARD.md` line 6 at `21945c61`, the parent of the `0718b6ab` truncation), and the two banners the build appended are byte-exact copies of their source lines. Beyond that: **three earlier authority banners (rounds 42, 43 and 44) are still lost**, each deleted by a sub-20-line rewrite that no v3 event can grade; a byte-exact block to restore them is drafted in §5 (`06-proposed-block.md`, `07-scorcard-append.diff`).

## 1. C1 at both tips

Clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` (one live clone, `$S=/fast/scratch/hyaku/kama-r48/X1Banner`). Contract: `registry/append-only-contract.tsv` (unmodified lane file). Both runs used the frozen tool bytes from the lane.

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py \
  --repo "$S/lane" --to 33e005827742b29772b153cda036ec9f27f653be \
  --contract /home/vgpnk/Projects/shokunin/kama-shokunin/registry/append-only-contract.tsv --json
→ exit 1
  summary: commits=309 events=5 files=89 restored=5 partial=0 unrestored=0
           regressed=1 ungraded_lines=89 bad_declarations=0 vanished=0 unmatched=0

python3 .../append-only-audit.py --repo "$S/lane" --to 380bcdff9c8af06997c482f6eb03db926a794a2b \
  --contract .../registry/append-only-contract.tsv --json
→ exit 0
  summary: commits=311 events=5 files=89 restored=5 partial=0 unrestored=0
           regressed=0 ungraded_lines=89 bad_declarations=0 vanished=0 unmatched=0
```

Events are identical at both tips except for one field (`01-audit-base-33e00582.json`, `02-audit-build-380bcdff.json`):

| event | file | deleted | graded | ungraded | restored_max | held@base | held@build | status |
|---|---|---|---|---|---|---|---|---|
| dd9f5dc6 | SCORECARD.md | 31 | 14 | 17 | 14 | 14 | 14 | restored |
| 0718b6ab | LOG.md | 2292 | 2292 | 0 | 2292 | 2292 | 2292 | restored |
| **0718b6ab** | **SCORECARD.md** | **2421** | **2349** | **72** | **2349** | **2348** | **2349** | restored |
| 0718b6ab | corpus/QUALITY.md | 375 | 375 | 0 | 375 | 375 | 375 | restored |
| 0718b6ab | corpus/README.md | 663 | 663 | 0 | 663 | 663 | 663 | restored |

`restored_max - held_at_to = 1` at the base tip, `0` at the build: the whole `regressed` verdict is one line.

## 2. The one graded line

The counter reports the count, not the line (`tools/append-only-audit.py` has no per-line regressed output; `--json` stops at `held_at_to`). I recomputed the frozen definitions on my own code path (`09-recompute-single-graded-line.py`) and **validated the reproduction against the tool before trusting it**: at `0718b6ab` it yields `graded=2349 ungraded=72` (tool: `2349`/`72`) and `held` in `{2348 at base, 2349 at build}` (tool: `2348`/`2349`). The per-unique-line deficit at the base tip is exactly one line:

- parent (`21945c61`) position **6**, section `None` (before the first `## ` heading, so never in an exempt region and always graded), deficit 1 at `33e00582`, deficit 0 at `380bcdff`;
- the line is `**Current authority (round 45):** …` — `sha256(line+LF) = 8f56ab3ffeb6abf8db00b9173031440ef6eee53eb13e55f8ead9d15bcd57acb5`, full text in `03-single-graded-line.txt`.

Mechanism, read off `git diff --numstat <c>^ <c> -- SCORECARD.md` (`04-banner-replacement-ledger.txt`): the `0718b6ab` truncation (`2421` deletions, file cut to 17 lines) deleted the r45 banner along with the body; the repair `82b5e9d3` restored it; `4340cf2f` then rewrote line 6 to the round-46 banner (1 of 8 deleted lines, below the 20-line threshold) and `383f1fc7` to the round-47 banner (1 of 9). Line 6 reads `ef73f99bb956eb0f` (r47) at **both** tips, so the r45 banner had no carrier at `33e00582` — the counter is right and the build's reading of *why* is right.

## 3. The appended banners are byte-exact

Build state: `### Superseded head banners (kept verbatim; round 48)` at `380bcdff:SCORECARD.md:2736`, note at `:2738`, banners at `:2740` (r45) and `:2742` (r46), file ends at `:2742`.

```
git show 82b5e9d3:SCORECARD.md | sed -n 6p > src45.txt
git show 380bcdff9c8af06997c482f6eb03db926a794a2b:SCORECARD.md > sc_build.md
sed -n 2740p sc_build.md > app45.txt ; cmp src45.txt app45.txt   # → identical, exit 0
8f56ab3ffeb6abf8db00b9173031440ef6eee53eb13e55f8ead9d15bcd57acb5  src45.txt
8f56ab3ffeb6abf8db00b9173031440ef6eee53eb13e55f8ead9d15bcd57acb5  app45.txt

git show 42ea1204:SCORECARD.md | sed -n 6p > src46.txt
sed -n 2742p sc_build.md > app46.txt ; cmp src46.txt app46.txt   # → identical, exit 0
87a437e7d22908d2709d3fcc3a0798e41e78bbf24c0d3d49452add231e392fe3  src46.txt
87a437e7d22908d2709d3fcc3a0798e41e78bbf24c0d3d49452add231e392fe3  app46.txt
```

Both appended lines have exactly one occurrence each in the build file (no duplication elsewhere), and at `33e00582` neither occurs (`grep -c "Current authority (round 4[56])"` → `0`; `Superseded head banners` → `0`).

## 4. Every preamble line `SCORECARD.md` has held since round 42

Walked `0b606b03..380bcdff` (65 commits, 22 distinct SCORECARD.md blobs; `05-preamble-ledger.txt`), taking for each blob every line before the first `## ` and line 6 separately. Seven distinct authority banners were ever line 6 (the `0718b6ab` blob has no `## ` heading at all — it is the truncation, its "preamble" is the whole 17-line file — so its blank line 6 is not a banner state):

| banner | first at | bytes | sha256[:16] | occurrences in `380bcdff:SCORECARD.md` | lost? |
|---|---|---|---|---|---|
| round 5 (blocked attempt; multi-line, first line) | 0bfd47ab | 75 | 5ca7b5b7e10a1182 | 1 (§Historical head sections) | no |
| round 42 | dd9f5dc6 | 713 | b618dd40cfef8db1 | **0** | **yes** |
| round 43 | 44fa5627 | 742 | 9b47ae8c90c8fe51 | **0** | **yes** |
| round 44 | d48e8cc3 | 750 | 5fa2c435db24f53c | **0** | **yes** |
| round 45 | 21945c61 / 82b5e9d3 | 754 | 8f56ab3ffeb6abf8 | 1 (`:2740`) | restored by the build |
| round 46 | 4340cf2f / 42ea1204 | 758 | 87a437e7d22908d2 | 1 (`:2742`) | restored by the build |
| round 47 | 383f1fc7 | 762 | ef73f99bb956eb0f | 1 (`:6`) | current |

All other preamble lines are held: `# kama-shokunin — SCORECARD`, the blank separator after it, `Contract per `AXES.md` §SCORECARD.md contract. Scores are 0–10, self-assessed,`, `each bound to an evidence pointer and the round that last changed it.`, the blank before line 6, and the eight lines of the round-5 blocked-attempt banner (`0bfd47ab:6-13`, one occurrence each inside §Historical head sections at `:139`+). The 10 non-blank lines that only existed inside the `0718b6ab` truncation are all held at the build too, so the ledger's only unserialised losses are the three banners above.

Why they fell through: each was replaced by a rewrite whose numstat was `9`, `1` and `3` deleted lines (`44fa5627`, `d48e8cc3`, `21945c61`) — all below the frozen 20-line event threshold, so no event ever graded them, and unlike r45 they were never caught inside a large deletion. They are below-threshold losses, not counter defects; I am not proposing a counter change (C1 is frozen).

Adjacency check, so this is not a re-report: `380bcdff:SCORECARD.md:2626-2641` (round-47 F2) documents a *different* shortfall — the superseded `## Axes` **rows** not being archived under §Historical head sections; and the build note at `:2738` says "the banners **rounds 45 and 46** replaced", which is accurate and forward-scoped ("from round 48 on, each round appends the banner it replaces here"). Neither covers r42–r44, which are not `## Axes` rows and predate the note.

## 5. Draft: byte-exact block restoring the r42–r44 banners

Pure append after `:2742`; no existing line moves or changes, so the appended r45/r46 lines stay byte-identical and no graded line is deleted (`07-scorcard-append.diff`: 0 deletions, 15 additions; `patch -p1 --dry-run` exit 0 against a copy of `380bcdff:SCORECARD.md`). Each banner is `git show <commit>:SCORECARD.md | sed -n 6p` verbatim — sources in `banner-sources/r42-line6.txt`, `-r43-`, `-r44-` (`b618dd40…acc3`, `9b47ae8c…0df4`, `5fa2c435…a7b`), oldest first, mirroring the existing block's layout (heading, one note paragraph, banners separated by blank lines):

```

### Superseded head banners (rounds 42-44, kept verbatim; round 48)

Round-48 seat X1Banner: the round-42, round-43 and round-44 banners were rewritten in place
too, but each replacement deleted only 9, 1 and 3 lines (`44fa5627`, `d48e8cc3`,
`21945c61`), below the 20-line event threshold of `tools/append-only-audit.py`, so no
v3 event ever graded them; the round-45 banner was readable only because `0718b6ab`
deleted it among 2421 lines. Appended byte-exact below (`git show
<commit>:SCORECARD.md | sed -n 6p`), oldest first.

**Current authority (round 42):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35). Latest measured round: 42. Calibration 7 is the lowest assigned axis, below operability 8, and below the saturation line, so the stagnation nudge is inactive. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` (round-42 claim C1); the round-5 banner and the head sections they replace are kept verbatim under §Historical head sections. Completed rounds are counted by the fleet's `MANIFEST.json`, not by this file.

**Current authority (round 43):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35). Latest measured round: 43. Calibration 7 is the lowest assigned axis, below operability 8, and below the saturation line, so the stagnation nudge is inactive. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` (round-42 claim C1) and kept current in round 43; the round-5 banner and the head sections they replace are kept verbatim under §Historical head sections. Completed rounds are counted by the fleet's `MANIFEST.json`, not by this file.

**Current authority (round 44):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35). Latest measured round: 44. Calibration 7 is the lowest assigned axis, below operability 8, and below the saturation line, so the stagnation nudge is inactive. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` (round-42 claim C1) and kept current in rounds 43 and 44; the round-5 banner and the head sections they replace are kept verbatim under §Historical head sections. Completed rounds are counted by the fleet's `MANIFEST.json`, not by this file.
```

Proposed `SCORECARD.md` tail diff:

```diff
diff --git a/SCORECARD.md b/SCORECARD.md
index 7d899b7..0117e7c 100644
--- a/SCORECARD.md
+++ b/SCORECARD.md
@@ -2740,3 +2740,18 @@ Round-48 C1 build finding: `tools/append-only-audit.py` v3 at the round-47 tip r
 **Current authority (round 45):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35). Latest measured round: 45. Calibration 7 is the lowest assigned axis, below operability 8, and below the saturation line, so the stagnation nudge is inactive. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` (round-42 claim C1) and kept current in rounds 43, 44 and 45; the round-5 banner and the head sections they replace are kept verbatim under §Historical head sections. Completed rounds are counted by the fleet's `MANIFEST.json`, not by this file.
 
 **Current authority (round 46):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35). Latest measured round: 46. Calibration 7 is the lowest assigned axis, below operability 8, and below the saturation line, so the stagnation nudge is inactive. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` (round-42 claim C1) and kept current in rounds 43, 44, 45 and 46; the round-5 banner and the head sections they replace are kept verbatim under §Historical head sections. Completed rounds are counted by the fleet's `MANIFEST.json`, not by this file.
+
+### Superseded head banners (rounds 42-44, kept verbatim; round 48)
+
+Round-48 seat X1Banner: the round-42, round-43 and round-44 banners were rewritten in place
+too, but each replacement deleted only 9, 1 and 3 lines (`44fa5627`, `d48e8cc3`,
+`21945c61`), below the 20-line event threshold of `tools/append-only-audit.py`, so no
+v3 event ever graded them; the round-45 banner was readable only because `0718b6ab`
+deleted it among 2421 lines. Appended byte-exact below (`git show
+<commit>:SCORECARD.md | sed -n 6p`), oldest first.
+
+**Current authority (round 42):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35). Latest measured round: 42. Calibration 7 is the lowest assigned axis, below operability 8, and below the saturation line, so the stagnation nudge is inactive. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` (round-42 claim C1); the round-5 banner and the head sections they replace are kept verbatim under §Historical head sections. Completed rounds are counted by the fleet's `MANIFEST.json`, not by this file.
+
+**Current authority (round 43):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35). Latest measured round: 43. Calibration 7 is the lowest assigned axis, below operability 8, and below the saturation line, so the stagnation nudge is inactive. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` (round-42 claim C1) and kept current in round 43; the round-5 banner and the head sections they replace are kept verbatim under §Historical head sections. Completed rounds are counted by the fleet's `MANIFEST.json`, not by this file.
+
+**Current authority (round 44):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35). Latest measured round: 44. Calibration 7 is the lowest assigned axis, below operability 8, and below the saturation line, so the stagnation nudge is inactive. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` (round-42 claim C1) and kept current in rounds 43 and 44; the round-5 banner and the head sections they replace are kept verbatim under §Historical head sections. Completed rounds are counted by the fleet's `MANIFEST.json`, not by this file.
```

Effect on the frozen measure, computed with the reproduction that matches the tool (`09-recompute-single-graded-line.py`): the `0718b6ab` event's graded population stays 2349 and `graded_held` stays `2349/2349` for the proposed file (build tip: `2349/2349`); the appended lines are inert for every other event, no line's section changes (the new heading is `###`, not `## `, and it is after the last existing line), and a pure append cannot lower `held`, raise `vanished`, or add an event. I did not run the frozen counter over a repo carrying this block (that needs a fixture history with the lane's 311 commits, which I did not build), so this paragraph is a recomputation, not a counter run.

## 6. Limits of what was run

- The line-level identification is a **reproduction**, not the frozen counter; it agrees with the counter on `graded`, `ungraded` and `held_at_to` at both tips before being used to name the line.
- The counter has no `--threshold` variant run here (default 20 at both tips); the sub-threshold claim rests on `git diff --numstat`, which is the same quantity the tool's event gate compares.
- `SCORECARD.md` was the only file examined for losses; the other four events are `restored` with `held_at_to == restored_max` at both tips, so they carry no equivalent gap.
- No lane file, index, jj state or service was touched; no tool was installed or upgraded.

## Files (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Banner.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Banner/01-audit-base-33e00582.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Banner/02-audit-build-380bcdff.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Banner/03-single-graded-line.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Banner/04-banner-replacement-ledger.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Banner/05-preamble-ledger.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Banner/06-proposed-block.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Banner/07-scorcard-append.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Banner/08-SCORECARD.at-380bcdff.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Banner/09-recompute-single-graded-line.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Banner/banner-sources/r42-line6.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Banner/banner-sources/r43-line6.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Banner/banner-sources/r44-line6.txt`
