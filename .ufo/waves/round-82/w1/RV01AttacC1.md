# RV01 — attack C1's counter (round 82)

Target `tools/round82-selfrecord-round81.py` sha256 `381e8639…5c526` (hash-identical copy used); lane master
at close `384ef1d5` (clone cut at `bacae07`, sealed `1b64f66d`). Commands: `python3 counter.py --repo <clone>`
(defaults = the frozen invocation, no flags) and `… --enumerate`; one commit per case on the clone's master.
Fixture diff + both outputs per case: `.ufo/waves/round-82/w1/RV01AttacC1/receipts/<case>.out`;
`$S=/fast/scratch/hyaku/kama-r82/RV01AttacC1` (deleted). Case 00 is the positive control.

| case | fixture bytes | observed `SELFRECORD_R81 …` | exit | verdict |
|---|---|---|---|---|
| 00 | none (clone tip) | `claims=6 mismatches=0 corrected=5 unbacked=0` | 0 | target reproduced |
| 01 | F1 block moved under `## Mistakes` | `mismatches=1 corrected=4 unbacked=0` | 1 | refused |
| 02 | F6 block added (holding fact) | `mismatches=1 corrected=5 unbacked=1` | 1 | refused |
| 03 | F1 block duplicated | `mismatches=1 corrected=4 unbacked=2` | 1 | refused |
| 04 | F1 `old=sc81c2-pending=4` (witness, not declared) | `mismatches=1 corrected=4 unbacked=1` | 1 | refused |
| 05 | F1 `at=<clone tip sha>`, not the sealed revision | `mismatches=1 corrected=4 unbacked=1` | 1 | refused |
| 06 | F1 `fix=SKILL.md` (exists, carries no `new` token) | `mismatches=1 corrected=4 unbacked=1` | 1 | refused |
| 07 | `## Corrections` heading deleted, blocks kept | `mismatches=5 corrected=0 unbacked=0` | 1 | refused |
| 08 | debt receipt `pending=12` (declared 1, witness 12) | `mismatches=2 corrected=3 unbacked=2`; enum `stale=5` | 1 | refused (exact) |
| 09 | SCORECARD carries only `sc81c2-pending=44` | `claims=6 mismatches=0 corrected=5 unbacked=0` | 0 | **escape** |
| 10 | record tokens stripped; five `fix=corpus/lessons/round-82.md` | `mismatches=0 corrected=5 unbacked=0` | 0 | **escape** |
| 11 | heading `## Corrections considered and rejected (not applied)` | `mismatches=0 corrected=5 unbacked=0` | 0 | **escape** |
| 12 | `corpus/lessons/round-82-verifier-spotcheck.md` added at tip | `mismatches=1 corrected=4 unbacked=1` | 1 | honest set fails |
| 13 | tip edits: receipt `pending=1`, gate `arms=10`, round-81 closure deleted, plan `Base revision`→301-row commit; lesson stripped | `mismatches=0 corrected=0 unbacked=0`; enum `stale=0`, exit 0 | 0 | **escape** |
| 14 | honest tip + `--no-corrections` | `mismatches=5 corrected=0 unbacked=0` | 1 | refused |
| 15 | real lesson stripped, `--lesson corpus/lessons/round-82-alt.md` | `mismatches=0 corrected=5 unbacked=0` | 0 | flag-only |

escapes (exact admitting lines):
- **09** line 298 `new not in fixed` is substring containment, not token equality: `sc81c2-pending=44` backs `new=…=4`; the target line prints with a wrong record value.
- **10** lines 297-298: `fix` may name `corpus/lessons/round-82.md` itself (its own `new=` satisfies the check); five lesson lines buy the target line, no SCORECARD/LOG append.
- **11** line 98 (`line.startswith("## ") and prefix in line`) + 252-255: any `## ` heading whose text contains `Corrections` is the container, so `## Corrections considered and rejected (not applied)` is admitted.
- **13** witnesses are read at the tip, not the sealed revision: lines 157,192,217,231 (`read("TIP", …)`), 207 (F4 closure), 319-324 (base revision from the tip plan); tip-only edits give `corrected=0`, exit 0 and `--enumerate` `stale=0`, exit 0 (control 1's `stale=5` is not stable).

residual risk / gaps:
- case 12: F4's witness is the highest-numbered `round-*-verifier-spotcheck.md` at the tip; a round-82 closure landing before grading reds the honest set (F4 `new=…round-81…` unbacked). Sequencing-fragile.
- F2: the counter binds the witness to the base revision (302 rows), while the frozen plan's witness cell says "the tip registry row count" (305 at `384ef1d5`); a plan-literal grader calls `new=…302` unbacked. Documented as a freeze divergence.
- invocation: `--lesson` (case 15), `--sealed` and `--no-corrections` change the verdict; the graded command must be exactly `--repo .`.
- selftest: `--selftest` at the lane tip prints `SELFRECORD_R81_SELFTEST pass=19 fail=0`, exit 0; control 3's mutants are covered, the four escapes are outside that class.
- live: target reproduced at lane tip `384ef1d5` (exit 0; enum `stale=5`, exit 1) and at clone tip `bacae07` (case 00).
