# R39-19 — census-start missing-config record

## Scope / evidence
Read-only inspection of the lane scratch working copy `/fast/scratch/hyaku/kama-r39` and the committed report repository. The frozen base is `6a4afdfe48b0b54239d127761d21a5cf21b5b0ea`. No source, Git/JJ state, or index was modified; no tools were installed.

## Observable findings
- `.ufo/waves/round-39/assimilation/census-start.out:1` records: `census before: rows=203; /home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin kama (fleet config unavailable to scratch root); exit=2 as noted`.
- This is an explicit failed census invocation, not a successful census receipt. The recorded cause is fleet configuration unavailable from the scratch root; the record itself gives the exit code 2. Thus the recorded 203 is a declared count, not independently substantiated by successful execution of that census command.
- The census script usage documents `--root DIR` and its self-tests explicitly check a `census-missing` case and exit 1 (`scripts/sources-census.sh:10, 153-154`). The script also contains a config-not-found failure path (`:454-455`). This is consistent with configuration being a prerequisite, but does not prove the exact runtime cause for the recorded invocation beyond what the receipt states.
- `.ufo/waves/round-39/assimilation/census-end.out` is a successful-looking output listing W04 rows and an `ok` path for `corpus/SOURCES.md`; it is an after-state artifact and does not repair the failed start receipt.
- The frozen preregistration (`assimilation/preregistration-frozen.json:2-3, 15-21`) fixes C1 at 7→7 and C2 at 9→9, with predicates frozen before data. This investigation does not alter those predicates or scores.

## Axes / verdict
- **Calibration:** The start record accurately discloses an exit-2/config-unavailable attempt, but cannot serve as executable evidence that the pre-change census succeeded or that its 203-row count was produced by the maintained census. The record does not by itself falsify the frozen C1/C2 outcome predicates.
- **Coverage:** The recorded before-state census evidence is incomplete as a successful command receipt; the later `census-end.out` is not a substitute for it. No additional assertion about the frozen scores is supported by this narrow evidence.

## Limits
I read the committed start/end artifacts and relevant script lines; I did not rerun the census or validate the source tree. The exact environment/configuration state at the time of the recorded command is not independently recoverable from these artifacts. No product files or frozen claims were changed.