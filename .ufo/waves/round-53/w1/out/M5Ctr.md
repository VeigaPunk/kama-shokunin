Killed 21 of 22 valid C2 mutants; one fleet-root mutant survived the two requested trees, exposing a coverage gap.

## Detector and controls

- Pristine counter: `tools/round53-cited-path-check.py`, copied to scratch; SHA-256 before/after: `1afb8b9d32fd0706d0625a4ea70270890039f93fc32635c28b12fa71b13e3080` (matches the lane source).
- Build detector: `python3 <counter> --repo /fast/scratch/hyaku/kama-r53/M5Ctr/lane --tip c22602bd8d83ab26349d1087e916ca537ee4f9d1 --scratch <scratch>`; exit 0, `fixture=1 lane=1 scenarios=8/8 cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True`. Full output: `out/M5Ctr/pristine-build.out`.
- Base control detector, same command with `--tip 4229ea1b9a789148dded1f159c20967d9a01373f`; exit 1, `fixture=1 lane=0 scenarios=8/8 cited=679 unresolved=16 disclosed=0 undisclosed=16 bad=0 stale=0 dropped=0 met=False`. Full output: `out/M5Ctr/pristine-base.out`.
- These pristine results agree with the recorded build and base predicates. Each valid mutant was run against both revisions using the same detector. A mutant is killed when its exit/output differs from pristine on either revision. The build and base share one isolated `git clone --shared` at the build commit; the counter selects revisions by `--tip`.
- Mutant runner outputs and summaries are in `out/M5Ctr/`. The initial BAD_CHARS text replacement did not match and made no mutant; it was corrected and M02 was rerun on both trees. M02 outcomes below are from that corrected variant (`out/M5Ctr/M02-bad-chars.py`, `badchar-*.out`).

## Mutant outcomes

| ID | Behavior mutation | Result | Detecting tree / note |
|---|---|---|---|
| M01 | Fence toggle | Killed | build and base |
| M02 | BAD_CHARS adds `*?` | Killed | build and base; cited counts change |
| M03 | Restrict LANE_ROOTS | Killed | build and base |
| M04 | Restrict FLEET_ROOTS to scripts only | Survived | Neither build nor base contains a citation whose only applicable fleet root is `templates/`. Killing scenario: add an outside-fence SCORECARD citation `` `templates/__m5ctr_probe_missing__.txt` `` to a fixture tip where that path is absent in both trees. The frozen parser should count an unresolved citation; this mutant ignores it, changing `cited`/`unresolved`. |
| M05 | Remove SKILL.md from TOP | Killed | build and base |
| M06 | Narrow anchor regex | Killed | build and base |
| M07 | Disable brace alternatives | Killed | build and base |
| M08 | Break glob matching | Killed | build and base |
| M09 | Break directory matching | Killed | build and base |
| M10 | Prefer fleet tree over lane tree | Killed | build and base |
| M11 | Accept any line count for beyond-EOF anchors | Killed | build and base |
| M12 | Disable deleted-class re-derivation | Killed | build and base |
| M13 | Disable never-class re-derivation | Killed | build and base |
| M14 | Disable moved-class blob comparison | Killed | build and base |
| M15 | Disable eof-class line-history check | Killed | build and base |
| M16 | Bypass upstream URL validation | Killed | build and base |
| M17 | Bypass untracked-class fleet check | Killed | build and base |
| M18 | Bypass fixed-class token/base checks | Killed | build and base |
| M19 | Disable stale-row detection | Killed | build and base |
| M20 | Disable dropped-SCORECARD-citation detection | Killed | build and base |
| M21 | Change SCENARIOS from 8 to 7 | Killed | build and base |
| M22 | Change met conjunction to disjunction | Killed | build and base |

The existing eight internal fixture scenarios also reported 8/8 on each pristine detector run. M04 is a coverage finding only; the counter and contract were not modified.

## Restoration and cleanup evidence

The pristine working copy was not edited; the corrected and other mutant programs were separate scratch variants. The source and pristine-copy hashes match as recorded above. `pgrep -af llama-server` returned no processes. Scratch was removed after evidence was copied to `out/M5Ctr/`.

## Evidence paths

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/M5Ctr.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/M5Ctr/`
