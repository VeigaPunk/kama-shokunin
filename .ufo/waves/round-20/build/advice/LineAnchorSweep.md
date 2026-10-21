VERDICT: partial - 20/24 checkable anchors resolve at the lane tip

# Round-20 line-anchor sweep
Axes per assignment: operability 8; calibration 7 (lowest assigned axis). Target lane revision: `37bd4c5bd456a2f8a54d3312c28495c321715856`.
## Method and counts
I read `SCORECARD.md`, `LOG.md`, and `corpus/lessons/round-17.md` through `round-19.md` from that revision in a scratch clone. The exact `<file>.md:<n>[-<m>]` syntax occurs **15** times in those five files, not 25. To provide the requested 25-pointer sample without inventing exact tokens, I included all 15 exact Markdown pointers plus 10 contextual prose line anchors (`lines N-M` / `line N`) that identify Markdown ranges (P01-P10 below). Writing commit (W) is the commit blamed for the citing line / introduction of that pointer; targets were opened from W and from the target revision. “Resolves” means the cited location still identifies the intended content, not merely that the line number is within file bounds.

| At W | At `37bd4c5` | Count / interpretation |
|---|---|---|
| 21/24 | 20/24 | Resolve; the 24 are assessable pointers. One additional host-config pointer cannot be verified historically. |
| 3/24 | 4/24 | Do not resolve: three old external line numbers already stale at W; plus one lane range that drifted by one line by tip. |
| 1/25 | 1/25 | Unverifiable: external `~/.config` file is absent now and has no tracked history; see command evidence. |
The 3 historical external values are explicitly recorded as old-to-corrected numbers in `LOG.md` (not as current citations): `THE-TICK.md:40 → :29`, `run-logic.md:556 → :495`, and `wwkd/SKILL.md:131 → :129`. They failed at W and remain stale at the base-revision date. S15 is the only new lane drift found.
## Pointer sample (W → target revision)
`Y` = resolves; `N` = stale; `?` = not historically verifiable. For external targets, W and tip were checked at the latest target-repository commits available by the corresponding dates; those commits are not pinned by the lane.

| # | Citing pointer → target line(s) | W | W → tip |
|---|---|---|---|
| S01 | `SCORECARD.md:192` → fleet `MISSION.md:29` | `1e41928ab` | Y → Y |
| S02 | `SCORECARD.md:654` → `SKILL.md:533` | `54a29268e` | Y → Y |
| S03 | `SCORECARD.md:740` → `corpus/lessons/round-17-verifier-spotcheck.md:217-221` | `c6dc46fab` | Y → Y |
| S04 | `LOG.md:45` → `~/.config/opencode/agents/janitor.md:21` | `c6199a254` | ? → ? |
| S05 | `LOG.md:221` → ufo-fsd-alpha `docs/THE-TICK.md:40` | `ea72c3eae` | N → N |
| S06 | `LOG.md:223` → ufo-fsd-alpha `.omp/skills/ufo/references/run-logic.md:556` | `ea72c3eae` | N → N |
| S07 | `LOG.md:223` → ufo-fsd-alpha `.omp/skills/wwkd/SKILL.md:131` | `ea72c3eae` | N → N |
| S08 | `LOG.md:277` → fleet `MISSION.md:29` | `e246c40ec` | Y → Y |
| S09 | `LOG.md:518` → fleet `MISSION.md:29` | `1e41928ab` | Y → Y |
| S10 | `LOG.md:1081` → `corpus/lessons/round-17-verifier-spotcheck.md:217-221` | `c6dc46fab` | Y → Y |
| S11 | `corpus/lessons/round-17.md:16` → `SKILL.md:533` | `54a29268e` | Y → Y |
| S12 | `corpus/lessons/round-17.md:85` → `corpus/SOURCES.md:53` | `54a29268e` | Y → Y |
| S13 | `corpus/lessons/round-17.md:85` → `corpus/lessons/round-16.md:147-149` | `54a29268e` | Y → Y |
| S14 | `corpus/lessons/round-18.md:87` → `corpus/lessons/round-17.md:309` | `c6dc46fab` | Y → Y |
| S15 | `corpus/lessons/round-18.md:285` → `corpus/SOURCES.md:209-213` | `0c75c6114` | Y → N (+1 line) |
| P01 | `SCORECARD.md:560` → `SCORECARD.md:6-13` | `b8e485cc6` | Y → Y |
| P02 | `SCORECARD.md:560` → `SCORECARD.md:45-55` | `b8e485cc6` | Y → Y |
| P03 | `SCORECARD.md:561` → `SCORECARD.md:132` | `b8e485cc6` | Y → Y |
| P04 | `SCORECARD.md:595` → `SCORECARD.md:26-28` | `b8e485cc6` | Y → Y |
| P05 | `SCORECARD.md:611` → `SCORECARD.md:26-28` | `ccc4bb312` | Y → Y |
| P06 | `SCORECARD.md:622` → `SCORECARD.md:122-128` | `ccc4bb312` | Y → Y |
| P07 | `SCORECARD.md:741` → `SCORECARD.md:702` | `c6dc46fab` | Y → Y |
| P08 | `LOG.md:1080` → `SCORECARD.md:702` | `c6dc46fab` | Y → Y |
| P09 | `LOG.md:646` → `LOG.md:547-548` | `33f46685b` | Y → Y |
| P10 | `LOG.md:647` → `LOG.md:594-595` | `33f46685b` | Y → Y |

## Findings and evidence
- **S15 stale at tip, +1 line.** At W, `0c75c6114:corpus/SOURCES.md:209-213` contains the complete S051 clarification ending “ReopenS051”. At tip, line 209 is blank; the text begins at 210 and ends at 214. Thus the old `209-213` range loses the final line; the current full range is `210-214`.
- The three external stale values are confirmed by the corrections themselves. At `964f443e` (the target repo snapshot for W), `docs/THE-TICK.md:40` is `## Invocation`, while `:29` begins “The shared backend is `http://127.0.0.1:34113/…`”. At the same snapshot, `wwkd/SKILL.md:131` begins “Each widening is reviewed…”, while line 129 is “- More endpoints (without changing data scope)”. `run-logic.md:556` is unrelated telemetry text at W; the line-223 correction names `:495` instead. These old numbers are historical error records, not current evidence anchors.
- Fleet `MISSION.md:29` resolves at all three lane writing dates and the base-revision date. For example, `f9ddcc9:MISSION.md:29` reads `  kama:       { cwd: kama-shokunin/,   axes: "operability + freshness (local model serving/endpoints)" }`; the same text is present at writing-date fleet commits `f2df270` and `322639d`.
- Lane examples that remain exact: `54a29268e:SKILL.md:533` is the “Probe verdict stub matrix” row; `c6dc46fab:corpus/lessons/round-17-verifier-spotcheck.md:217` starts “**discernment: improved**”. Both target spans are byte-identical at `37bd4c5`.

## Commands / verification
- `python3 extract.py > pointers.json` (scratch clone): **exit 0**, found 15 exact `.md:<n>` occurrences; the full list is represented by S01-S15.
- `python3 sweep.py > sweep.jsonl` (scratch clone): **exit 0**; `git blame` / `git show` opened lane targets at W and tip.
- Selected-lane count script: **exit 0**; 18/18 selected lane targets in bounds at W and tip, 17/18 unchanged at tip; only S15 differs.
- Fleet target-line checks for `f2df270`, `322639d`, `f9ddcc9`, and fleet HEAD: **exit 0**; line 29 matched as quoted above.
- ufo-fsd-alpha target checks for `964f443e` and `31c465f1`: **exit 0**; old and corrected lines reported above.
- `test -e ~/.config/opencode/agents/janitor.md`: **exit 1** (absent). `git -C ~/.config ls-files opencode/agents/janitor.md`: **exit 0**, no output (not tracked).
- No tools were installed or updated. Scratch clone and scripts were removed after collecting the results.
## Residual risk / verification gap
The external MISSION and ufo-fsd-alpha snapshots are date-matched, independent repositories; the lane does not pin those commits, and uncommitted external working-tree state cannot be reconstructed. **[INFERENCE]** The missing/untracked janitor file may have existed when `LOG.md:45` was written, but no historical snapshot was available to prove or disprove it. The strict-token population is only 15; P01-P10 are the additional contextual Markdown line anchors used to make the requested 25-pointer sample.