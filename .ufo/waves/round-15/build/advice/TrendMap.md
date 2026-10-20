# TrendMap-3 — connector: quality repair vs unchanged expansion; outside discovery credit

Seat `KamaR15.TrendMap-3` (connector). This is author-side advice only. It is not an outside spot-check (`corpus/QUALITY.md:15-20`).
Lane root: `/home/vgpnk/Projects/shokunin/kama-shokunin`. Every lane path below is relative to that root. Fleet files are given as absolute paths.
I wrote only this report. I edited nothing else and ran no tests, gates, census, git commands or probes. I installed and updated nothing; the operator's pacman pause is acknowledged, and this slice needs no tool.

## Axes and trends checked

- **Axes:** C1 calibration (7 → 7, delta 0) and operability (8, not claimed), from the kama row at `/home/vgpnk/Projects/shokunin/shokunin.conf:52`. Depth, freshness, coverage and adjacency are unchanged.
- **Trends:** expansion, quality and discernment. The definitions are in `/home/vgpnk/Projects/shokunin/LEARNING.md:31-35`.
- **Axis-to-trend mapping:** calibration maps to discernment. Operability, depth and freshness map to quality. Coverage and adjacency map to expansion (`/home/vgpnk/Projects/shokunin/AXES.md:20-23`, `LEARNING.md:84-88`).

## Evidence

| # | Fact | Where |
|---|---|---|
| E1 | Expansion improves only when one of these appears: a new admitted `knowledge/` entry on uncovered ground, a new frontier area, a new kind of source, or a new SCORECARD capability. Source rows alone do not count. | `LEARNING.md:33`; `/home/vgpnk/Projects/shokunin/CORPUS.md:123-125` |
| E2 | Quality improves only when an entry is re-verified, deepened or superseded. Quality is harmed when an entry is "found false or stale and left unmarked". | `LEARNING.md:34` |
| E3 | Discernment improves when the outside check agrees with the gate, or when a disagreement becomes a lesson plus a grounded criterion. Mining a mistake into a criterion is a separate rule, LEARNING step 3. | `LEARNING.md:35`, `:19-21`, `:40-48` |
| E4 | Precedent 1: gate machinery alone is not quality. Round 12's author claimed quality improved partly because of a fail-capable repair (`corpus/lessons/round-12.md:268-272`). The round-12 closure re-grounded that verdict in the knowledge entry "instead of treating gate green as learning". The round-13 closure then corrected the attribution "to credit D4, not gate machinery". | `corpus/lessons/round-12-verifier-spotcheck.md:122`; `corpus/lessons/round-13-verifier-spotcheck.md:239-241,255-258` |
| E5 | The round-14 closure on this exact R1: quality unchanged, "No quality improvement is claimed from the gate alone". Discernment improved, but that credit covers only the new outside sample. The closure says "R1 narrows an ancillary guard guarantee rather than rejecting the sampled capability". R1 is "status-neutral conformance debt, not a demonstrated failure of the fixed capability claim". | `corpus/lessons/round-14-verifier-spotcheck.md:7,134-136,142` |
| E6 | The round-14 Gate has no row for the runner's duplicate promise. Its five rows cover only the classifier, readiness, normalization and the historical table. | `corpus/lessons/round-14.md:13-19` |
| E7 | PROVINCE owns serving surfaces only: probe/listeners, baseURL pins, served-model reconciliation, probe conventions, drift history and the consumer registry. A measurement-harness corpus guard is lane test infrastructure, not a province surface. | `PROVINCE.md:3-15,51-53` |
| E8 | Round 15 already writes expansion unchanged and adds no capability row. "Final measured revision, counts and verdict are appended after execution." | `SCORECARD.md:501-506`; `corpus/README.md:179,195-200` |
| E9 | The discovery is credited outside. LOG says "Both discoveries are credited to CloseKamaR14". KQ18's motivating-lesson cell says the repair "claims no credit for discovery or admission". R2 "adds no criterion". | `LOG.md:856-859`; `corpus/QUALITY.md:81-83,87`; `corpus/lessons/round-15.md:36-38` |
| E10 | S034 is a mined own-work row, tier A, cited only by a lesson. Its `teaches` cell restates R1's diagnosis without naming R1. The search log presents the question as the lane's own ("Question: does the original measurement guard enforce…"). SCORECARD says "S034 sources the original guard diagnosis". Only the lesson frames it correctly: "C1 rests on S034 plus the actual outside R1". The own-work kind is not new: S030 already uses it. | `corpus/SOURCES.md:42,46,80-87`; `SCORECARD.md:504`; `corpus/lessons/round-15.md:62-64`; `build/advice/Sources.md:48` |
| E11 | The replay knowledge entry says the wrapper "`.ufo/waves/round-14/measure.py` … is a round artifact, not a permanent lane command". Round 15 repairs that wrapper in place and registers a gate whose default runner is that path. The round-15 supplement covers the repair and the tests, but not this change of status. | `corpus/knowledge/ollama-evidence-replay.md:87-89,317-355`; `SKILL.md:495`; `tests/ollama-corpus-guard/check.py:61` |
| E12 | Every copy of the false promise is now either true or marked. (a) The current runner docstring and LIMITS are true once the guard is in place. (b) The round-14 receipt holds four embedded copies, marked by the lesson's named correction. (c) The frozen red control is pinned by its manifest. | `.ufo/waves/round-14/measure.py:13-14,77,358-359`; `.ufo/waves/round-14/acceptance.json` (four runs' `limits[3]`); `corpus/lessons/round-15.md:32-34`; `.ufo/waves/round-15/frozen/manifest.json`; corroborated by `build/advice/ReceiptReview.md:59` and `build/advice/R1Correction.md:38-39` |
| E13 | The guard output identifies its own inputs. It records `runner_sha256` and `classifier_sha256`, so red and green results can be tied to the frozen runner (sha `fda61e…`) or the repaired one. That keeps C1 repair credit separable from discovery credit. | `tests/ollama-corpus-guard/check.py:640-643` |

## Contradictions

1. **"Reliability" wording versus R1's ruling.** `SCORECARD.md:502-503` says "repaired reliability of the existing replay repertoire". R1 calls the issue status-neutral debt, not a failure of the capability (E5). The supplement says the classifier is unchanged (`ollama-evidence-replay.md:335-337`). Only the harness's corpus-admission promise was repaired; the classifier repertoire was never shown to be unreliable.
2. **Wrapper status drift.** The knowledge entry calls the wrapper "a round artifact, not a permanent lane command" (`:87-89`). A registered gate now uses that path as its default runner (E11). The entry does not mark this change. A strict outside reviewer could apply LEARNING's quality-harmed rule (E2).
3. **Registry wording versus outside discovery.** The S034 and search-log text (E10) omit the routed trigger. LOG and KQ18 credit the discovery to CloseKamaR14 (E9).
4. **KQ18 versus discernment's disagreement clause.** R1 was not a disagreement with a gate decision (E5, E6). KQ18 is mistake-mining (LEARNING step 3). Presenting KQ18 as satisfying `LEARNING.md:35` would be self-attested discernment, which the closure has not ruled on.

## Proposed move: write the pending verdict as a one-owner trend ledger

This is one bounded move. It fills the "verdict appended after execution" slot (`SCORECARD.md:506`) and the matching final disposition in `corpus/lessons/round-15.md`. Every round-15 artifact gets exactly one credit owner. It also needs one append marking the wrapper's new status, without which the "quality not harmed" row is not true.

**Ledger text for the final append:**

> Trends: expansion **unchanged**. No new knowledge entry, capability row, frontier ground or source kind is added. S034 is an own-work row cited only by a lesson; rows are not expansion. The round-14 capability still meets its fixed 51/51-unique bar. Quality **unchanged**. The repair fixes a measurement-harness corpus-admission promise, not a serving-knowledge entry. The classifier and its capability row are unchanged. Operability stays 8, and the repaired harness is credited once, under C1 calibration. Every copy of the false promise is now true (current runner) or preserved and marked (round-14 receipt, frozen baseline). Discernment **unchanged pending outside round-15 admit/reject sampling**. KQ18 mines outside R1 as a Mistake. Whether that also counts as learning a disagreement is for the closure to rule, because the round-14 closure classified R1 as narrowing an ancillary guarantee, not rejecting a sampled gate decision. CloseKamaR14 discovered R1 and R2; that discovery earns this lane no claim, axis or trend credit. S034 only locates the predicate that R1 diagnosed.

**Status append to `corpus/knowledge/ollama-evidence-replay.md`:** add one bullet strictly after `:355`, so no earlier anchor moves (KQ7/KQ14 append rule):

> - **Wrapper status since round 15.** §Literal replay interface (`:87–89`) still holds that the wave-local wrapper is not a classifier command. From round 15 the same path is repaired in place and is the default runner of the registered gate `python3 tests/ollama-corpus-guard/check.py`. Re-derive round-14 receipt results only from the git blob at `e545ed99aaa519196a2a7779b0a293b2ce4c765c` or from `.ufo/waves/round-15/frozen/measure-before.py` with its manifest, never from the current path. This marks a status change and adds no quality or capability credit.

**Optional:** append the same attribution clause after `corpus/SOURCES.md:93` ("question routed by outside R1 (CloseKamaR14); S034 carries no discovery, expansion or discernment credit"). Prose append only; S034's cells stay intact under `CORPUS.md:116-118`.

**What this changes:**
- **Calibration:** claim strength now matches evidence. Credit goes only to the fail-capable repair (E13), not to the discovery (E9). The score is unchanged.
- **Quality trend:** a strict "harmed" ruling on contradiction 2 is no longer possible, and quality is not inflated by gate machinery (E4).
- **Expansion:** S034 and the census delta cannot be counted as growth.
- **Discernment:** the closure keeps its unawarded options. Since the round-14 discernment credit excluded R1 (E5), any closure upgrade here would not be double credit.
- **No harm** to operability, depth, freshness, coverage or adjacency. Nothing touches runtime, classifier, receipt or serving surfaces.

## Risks

- **Too conservative.** The closure may grant quality or discernment "improved". An author "unchanged" is the safe floor: earlier closures upgraded pending author verdicts without editing filed text (E4, E5; `round-11-verifier-spotcheck.md:198-200`).
- **Depends on the guard landing.** If the measured red/green fails, the current runner's docstring and LIMITS stay false. The "every copy now true" clause must then be replaced by a mark, and the C1 verdict changes. The expansion row does not depend on this.
- **Placement.** The knowledge bullet must be appended, never inserted mid-file, and must not read as a deepening or quality claim.
- **Unknown commit state.** I did not check whether the round-15 files are committed. Phrasing everything as an append is safe either way.

## Read-only checks for L1 after integration

1. `grep -n "round artifact" corpus/knowledge/ollama-evidence-replay.md` should show the original `:88` plus the appended bullet after `:355`. The start prefix of the entry should be byte-preserved, as in the round-14 `preservation.json` method.
2. The round-15 SCORECARD append should hold exactly the three trend verdicts above. The capabilities table should still have one row.
3. Grep the round-15 lesson, SCORECARD, LOG, README and SOURCES for `S034`, `discover` and `disagreement`. No sentence should claim the lane discovered R1, and none should claim KQ18 satisfies `LEARNING.md:35`.
4. The before and after guard receipts should show `runner_sha256` as the frozen `fda61e…` versus the repaired digest. `classifier_sha256` should be identical in both, and the cases oracle should still be `4a4de0…`.
5. The final census delta (rows 33 → 34, A 30 → 31, mined 23 → 24) should be labelled non-expansion.

## Limitations

- Everything here comes from static reading; I executed nothing. I read `check.py` only at `:1-83` plus targeted grep hits, and I did not open the 12 fixture files.
- Treating the frozen copy as equal to the measured-revision blob is **[INFERENCE]**. It rests on `round-14-verifier-spotcheck.md:5,82` and `build/advice/R1Correction.md:39`, not a git comparison by me.
- My inventory of false-promise copies is my own grep over the lane, cross-checked against the sibling advice files ReceiptReview and R1Correction.
- No other seat had mapped the trends; a grep of `build/advice` found only `AttackSource.md:5` and `ReceiptReview.md:29` touching trend terms. I sent no peer messages.

Report: .ufo/waves/round-15/build/advice/TrendMap.md
