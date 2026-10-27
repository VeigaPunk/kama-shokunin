# R03NoopAttack — distinct case 11

Axes: operability (counter actually observes canonical data); calibration (a claimed count follows the selected canonical table rather than literals).

Scope: attack the frozen C2 target, `tools/round42-selfdesc-reconcile.py`, using read-only committed tree plus the frozen do-nothing fixture. No shared/source changes.

## Reproducible observations

From lane root:

```
$ python3 tools/round42-selfdesc-reconcile.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip HEAD
 tip=7c873d7b4e3839489a93d6334cdf93fe5d34d19f
 r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False
 detail: r41 calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '42' (exit 0)
$ echo $?
1
```

This falsifies the old C2 framing in `freeze.txt` as-written: the current HEAD counter still reports the frozen stale count defect (mismatches=1/maxN=56). The pre-data `freeze-amendment.txt` explicitly reassigns the no-op battery defect to C1 and stale count to C2; this seat attacks the stale-count target as amended. The independent no-op control remains direct evidence of a false green for that earlier target:

```
$ cat .ufo/waves/round-57/controls/noop-c2.out
control=no-op instrument
canonical_table_reads=0
self_description_reads=0
summary=mismatches=0 maxN=46 met=True
exit=0
```

The associated no-op script is exactly three lines and only prints `mismatches=0 maxN=46 met=True`; it reads neither the repository nor table. It therefore survives any assertion checking only its output string / exit status, but is killed by the frozen control's `canonical_table_reads=0` and `self_description_reads=0` evidence if those are actually measured rather than supplied by the script.

## Attack matrix (survivors/kills)

| Variant | Observed result | Assessment |
|---|---|---|
| No-op / hardcoded `mismatches=0 maxN=46 met=True` | Frozen receipt reports `met=True exit=0` while recording zero canonical-table and self-description reads. | **Survives** output-only or exit-only pass checks; **killed** only if reads are independently instrumented/bound. |
| Delete/omit a canonical row | No isolated mutation fixture ran in this seat; the round42 checker evaluates committed blobs at `--tip`, so an uncommitted edit in the worktree cannot affect it. | **Not tested**; the checker source alone does not establish deletion sensitivity. A valid mutation check needs a private Git fixture and tip bound to that fixture. |
| Stale canonical table / stale expected number | Frozen base reports `maxN=56`, mismatch 1, exit 1; frozen no-op reports maxN=46, mismatch 0, exit 0 without reads. | **Counter kills current stale baseline** (nonzero); no-op **survives** without data. |
| Fixture-label output / hardcoded output | No fixture-label mutation executed. A literal printer can trivially claim all expected fields; receipt's read counters distinguish only if captured outside the instrument. | **Output-only check vulnerable**; stronger instrumentation not validated here. |

## Source-level counterexample / smallest correction

`canon()` chooses the greatest heading matching `canonical list as of round N**` (lines 120–127), then `table_rows()` returns rows from that heading's following table (110–117). In the chosen section, `evaluate()` derives `maxn` from those rows (not output text); its result then returns `met = (mism == 0)` (285–293). This is better than hardcoding output but the current observed `maxN=56` means the count/predicate remains stale relative to frozen target 46. Smallest safe correction is to update only the relevant canonical capability row/heading count expectation that currently drives maxN and retain the existing committed-tip, content-derived calculation; do not replace it with a literal printer or trust a fixture label. Separately, require a selftest that mutates/deletes a selected canonical row in a private Git fixture and proves the measured checker changes/fails; otherwise row omission sensitivity remains unestablished.

## Limits

No mutations, tests, installs, or source edits were made. Row deletion and fixture-label mutant outcomes are explicitly untested, not claimed killed. No admission/verdict is made.