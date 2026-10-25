# R39-06 — indent trap S471 id intersection

**Axes:** calibration (whether the guard-trap report is faithfully grounded); coverage (whether the alleged S471 intersection affects the S472 continuation). Read-only observations of the lane scratch working tree and frozen base; no product files changed. The requested report is the sole write.

## Findings

- The frozen-base registry-ID artifact `.ufo/waves/round-39/assimilation/reg-ids` contains 203 unique IDs, S001–S194 with gaps followed by S196, S205, S206, S209, S223, S324, S327–S329. `staged-ids` contains 142 unique IDs, S330–S471. `comm -12 <(sort reg-ids) <(sort staged-ids)` produced no output; the stored `collisions` file is zero bytes. Thus the actual pre-append registry/staged intersection is empty.
- The two trap inputs are exactly `  | S471 | trap` and `  | S471 | staged`. Stored `trap-reg-ids`, `trap-stage-ids`, and `trap-collisions` each contain `S471`; the strict column-zero extraction returned no matches on these inputs. The stored evidence supports the lesson's point: accepting up to three leading spaces in both ID extractions causes a false collision for this fixture, while the actual source ID sets do not intersect.
- The exact extraction command is not present among the trap evidence files. The lesson says the expression is in the prompt/evidence; the 0–3-space pattern itself is visible in the prior round-37 report, but not as a per-run command receipt for this round. Treat the fixture result as confirmed from stored outputs, not as an independently captured execution transcript.
- Important scope correction: S471 is present in the staged package (`assimilation/staged-ids` ends at S471, and staged source material includes S471). It is inaccurate to say S471 appears nowhere outside the lesson and trap fixtures. What is established is that **the lane's pre-append registry** has no S471: its maximum is S329. Round-39's appended lane row is S472, and the stored `claim-after.out` records registry rows 203→204.
- The lesson's stated 0-collision real intersection and the S472-next-ID conclusion are consistent with these artifacts. The fixed records do not indicate a calibration or coverage-claim falsification on this item. They do not independently establish broader calibration or coverage beyond the frozen claim predicates.

## Evidence paths

- `.ufo/waves/round-39/assimilation/{reg-ids,staged-ids,collisions}`
- `.ufo/waves/round-39/assimilation/{registry-trap.md,staged-trap.md,trap-reg-ids,trap-stage-ids,trap-collisions}`
- `.ufo/waves/round-39/assimilation/claim-after.out`
- `corpus/lessons/round-39.md:25`
- `.ufo/waves/round-37/w1/out/ScoutGate.md:78-88` (prior recorded extraction command and empty result)

No tools installed or updated. No checks rerun; no code, judge, commit, push, publication, or deployment performed.