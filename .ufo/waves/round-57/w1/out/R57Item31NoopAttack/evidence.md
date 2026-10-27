# R57Item31NoopAttack — independent C2 attack, case 52

Axes: calibration and operability. This is an attack-only report; no shared source edits or installs. Tooling authorization was read at `/home/vgpnk/.omp/agent/RULES.md`; pacman transactions remain paused.

## Findings

The actual frozen round-42 counter is vulnerable to the stated output-hardcode attack. Replacing its entrypoint with `print('mismatches=0 maxN=46 met=True')` exits 0 and prints the exact green summary while reading no SCORECARD and evaluating no canonical rows. Therefore an assertion based only on summary text/exit cannot establish canonical-row execution/content binding (case 52 decisive bypass).

The frozen no-op receipt independently records `canonical_table_reads=0`, `self_description_reads=0`, summary `mismatches=0 maxN=46 met=True`, exit 0. The frozen actual counter at the stated base reports `r41=1 ... mismatches=1 maxN=56 met=False`, exit 1, with detail that the calibration run expecting `42` found no stdout line equal to `42` (the amendment corrects target to 43). The no-op does not represent a valid canonical evaluation.

Mutation attempts against a minimal private fixture showed the real counter exits 1 with mismatches on omitted-row and stale-derived-table variants; these fixtures lacked the full tracked tree and consequently also report unrelated r41/receipt failures. Thus they establish refusal on those altered fixtures, not isolated canonical-row detector sensitivity. Hardcode control exit 0 is a full bypass and is the stronger attack result.

## Commands and exact observations

1. Read `tools/round42-selfdesc-reconcile.py:1-297`, in particular `evaluate()` lines 149-270 and output/exit lines 281-293. It reads SCORECARD from `git cat-file` at requested tip, obtains canonical rows via `canon()`, checks capability names, and derives summary from counters. However, this describes the unmodified code only; the output-hardcoded replacement bypasses it entirely.
2. Read `.ufo/waves/round-57/controls/noop-c2.out`: exact fields `canonical_table_reads=0`, `self_description_reads=0`, `summary=mismatches=0 maxN=46 met=True`, `exit=0`.
3. Read `.ufo/waves/round-57/controls/base-c2-frozen.out`: `tip=b89bdab2cc114735ec5d331c6c610134258f7864`; `r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False`; detail states `corpus/lessons/*verifier-spotcheck.md` run expecting `42` had no matching stdout; receipt says `exit=1`.
4. Executed actual counter on frozen base:
   `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round42-selfdesc-reconcile.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip b89bdab2cc114735ec5d331c6c610134258f7864`
   stdout exactly matched `base-c2-frozen.out`; stderr empty; exit 1.
5. Private case fixture setup used `/fast/scratch/hyaku/kama-r57/R57Item31NoopAttack`, guarded each initialized git fixture with `git -C <fixture> rev-parse --show-toplevel` equality. The scratch was removed via shell trap. The hardcode fixture ran the replacement entrypoint with `--repo <fixture> --tip HEAD`; exact stdout `mismatches=0 maxN=46 met=True`, stderr empty, exit 0. This is an intentionally successful fake green, not acceptance evidence.
6. The actual counter on minimal isolated row-drop fixture: exit 1, summary begins `r41=30 ... mismatches=39 maxN=56 met=False`; isolated stale-table fixture: exit 1, summary begins `r41=27 ... saturation=1 ... mismatches=37 maxN=56 met=False`. Both include unrelated failures because the fixtures are intentionally incomplete; do not attribute all mismatches to row mutation.

## Minimal control implication

A proposed acceptance harness must invoke a pinned executable/counter and bind the output to that invocation (not trust a declared summary), require evidence that the canonical SCORECARD bytes at the frozen/evaluated revision were read, and demonstrate both no-op rejection and genuine-path acceptance. Then mutate the selected canonical table (drop, add, rename, and content edit) and stale table-derived values independently. A subprocess returning a forged green string cannot itself be treated as successful execution. The existing counter's parsing checks support row/table mismatch detection but do not prevent replacement/skip of the entrypoint; that is a harness/identity gap, distinct from the stale C1 calibration literal.

Case 52 was executed independently; no sibling evidence was used to derive results.

Report: .ufo/waves/round-57/w1/out/R57Item31NoopAttack/evidence.md
