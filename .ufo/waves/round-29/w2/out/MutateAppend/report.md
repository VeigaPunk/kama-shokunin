# MutateAppend — C1 (calibration) correction-table mutation probe

Round 29 attempt 2, wave w2. Seat `MutateAppend` (leaf; no subagents, no services).

## Objects under test

- Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`, branch `master`, data commit
  `513eba3ba51a142c9936553e3a85918345eb5c4c`; base `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d`.
- Frozen counter `.ufo/waves/round-29/count-c1.py`,
  sha256 `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` (matches the frozen value).
- Scratch clone only: `/tmp/kama-r29-w2-MutateAppend` (full clone of the lane, checked out at
  `513eba3b`). No git write command was run with the lane as `-C`/cwd; the lane index, jj state and
  working tree are untouched. My only lane write is `w2/out/MutateAppend/`.

Blob evidence (computed in the clone):

| object | sha256 |
|---|---|
| `2aa46e2:SCORECARD.md` (1441 lines) | `7af59cc0226f05b534c2f628345a53b8d9866bef2245c0092bb3758b4752d1db` |
| `2aa46e2:SHONEN.md` (11 lines) | `1ff9e2f363baedc09ae913c2036d79b53dcd270c851419ef33b8dc337a6d3fb5` |
| `513eba3b:SCORECARD.md` (1464 lines) | `a46bcc744032bbab69738e654c657f58ee45c2ee55c8ee84f800251ab922f7b9` |
| `513eba3b:SHONEN.md` | `1ff9e2f363baedc09ae913c2036d79b53dcd270c851419ef33b8dc337a6d3fb5` |

## Pristine baseline (control run)

Command (from the clone):

    python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py \
      --repo /tmp/kama-r29-w2-MutateAppend --tip 513eba3b --list \
      --out /tmp/kama-r29-w2-MutateAppend/baseline.json

Output, exit 0:

    statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip 513eba3ba51a

This reproduces the inherited fresh-clone receipt line exactly. Receipt
`out/MutateAppend/baseline.json` sha256 `88be242e1547799c270159cc80b15b38ed4a6738b620cc8b892ca967c40a1914`.
The 11 mismatched sids (4 P, 7 Q) are in that receipt; the one at base line 1349 is
`SCORECARD.md:P:1c6c1f3e4c:0`, token `.ufo/reports/round-25/kama.md:120-129`, W `7f84cd0e`,
observed `p:absent`.

## Mutation A — in-place "correction" of the line-1349 pointer

Change (commit `bbfbf9b0f5f7062a72545736586a18e04614f745`, 1 file, +1/−1; not in the lane):

    -(`.ufo/reports/round-25/kama.md:120-129`: quality unchanged, discernment
    +(`/home/vgpnk/Projects/shokunin/.ufo/reports/round-25/kama.md:120-129`: quality unchanged, discernment

The absolute target exists on disk (`/home/vgpnk/Projects/shokunin/.ufo/reports/round-25/kama.md`,
177 lines; lines 120–129 are the quality/discernment-unchanged verdicts), so this is a genuine
pointer correction, not a decoy.

Run: counter at `--tip bbfbf9b0`. Output, exit 0:

    statements 69 mismatched_at_base 11 append_only False valid_corrections 11 false_corrections 0 unresolved 69 met False tip bbfbf9b0f5f7

Expected `append_only False` — **confirmed**. `unresolved` becomes all 69 statement ids: the
receipt's `unresolved_ids` has length 69 (first `SCORECARD.md:C:04234244c5:0`, last
`SCORECARD.md:T:fbf3797714:0`), matching preregistration C1.predicate: "a tip SCORECARD.md that
does not begin with the base bytes makes every base statement unresolved." The statement set and
the 11-item mismatch list are *identical* to baseline (same sids, lines, tokens, observed values) —
the tip is never read for extraction, so the only detector effect is the byte-prefix guard.
Receipt `out/MutateAppend/mutA.json`, sha256 `1c20d84065c3099ddf93b35ded3ca01ed3d8f315f0769355a79707397b18bb45`.
Verdict: mutant **killed** (met True→False, unresolved 11→69); exit stays 0.
Determinism: second run `mutA2.json` equals `mutA.json` field for field.

Restore: `git reset --hard 513eba3b`; `SCORECARD.md` sha256 back to
`a46bcc744032bbab69738e654c657f58ee45c2ee55c8ee84f800251ab922f7b9`; re-run produced the exact
baseline line (`out/MutateAppend/restored.json`, sha256
`f3c7a43907d44a4780593e4a12d07b71950e7fd32debb27f144c7dc0069dd504`).

## Mutation B — one appended row keyed on a HOLDING sid

Restored tree at `513eba3b` (hash above), then one row appended after the last table row (tip file
line 1464; base bytes remain an exact prefix), under `## Round 29 — self-assessment corrections`:

    | SA29:SCORECARD.md:P:103e323011:0 | SCORECARD.md:654 | P | `SKILL.md:533` | 54a29268 | synthetic probe row: this statement holds at base, so it is not a mismatch; observed copied from the counter | ok |

`SCORECARD.md:P:103e323011:0` is a HOLDING base statement (base line 654, token `SKILL.md:533`,
W `54a292680e2083caa2b1e0d54ee1e7d90961302f3`, counter observed `ok`), so `ok` is a plausible
last cell. Commit `88d5fbc71b1249ae0bd47fe85d6badc963fd9e8e` (1 file, +1).

Run: counter at `--tip 88d5fbc7`. Output, exit 0:

    statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 1 unresolved 1 met False tip 88d5fbc71b12

Receipt fields (`out/MutateAppend/mutB.json`, sha256
`b6b5cfcdf1f1fa2554aee178e779417f78362b6d0f7ba7d98f3d1cc8e8c7a687`):

    correction_rows   = 12
    valid_corrections = 11
    false_corrections = [{"sid": "SCORECARD.md:P:103e323011:0", "observed": "ok", "why": "not-a-mismatch"}]
    unresolved        = 1
    unresolved_ids    = []
    met               = False

Confirmed: `false_corrections 1`, the 11 true rows still valid (`valid_corrections 11`, the false
list contains only the probe row), `met False`. Determinism: `mutB2.json` equals `mutB.json`.

**Deviation from the item's stated expectation.** The item text expects `unresolved 0`; the frozen
counter prints `unresolved 1`. This is the counter's frozen contract, not a defect:
`count-c1.py:327` computes `unresolved = len(unresolved_ids) + len(false_rows)`; the docstring
(`count-c1.py:39`) says a false correction "is itself counted as unresolved"; preregistration
C1.predicate says "every false correction row (names a holding statement or no base statement,
wrong observed value, duplicate sid) counts as one more unresolved." `unresolved_ids` is empty, so
"0 unresolved *statements*" is true, but the receipt field the item names reads 1. The item's
expected string should read `false_corrections 1 unresolved 1 (unresolved_ids []) met False`, or
say "unresolved_ids 0". Either way the mutation is **killed** and the 11 true rows survive.

Restore: `git reset --hard 513eba3b`; `SCORECARD.md` sha256
`a46bcc744032bbab69738e654c657f58ee45c2ee55c8ee84f800251ab922f7b9`, `SHONEN.md`
`1ff9e2f363baedc09ae913c2036d79b53dcd270c851419ef33b8dc337a6d3fb5`; final run reproduced the
baseline line byte for byte (`out/MutateAppend/restored-final.json`, same sha256
`f3c7a43…d504` as the A restore). `git status --porcelain` in the clone lists only my untracked
dump files; tracked tree clean at `513eba3b`.

## Verdicts

| probe | expected | observed | verdict |
|---|---|---|---|
| A: in-place line-1349 pointer correction | `append_only False` | `append_only False … unresolved 69 met False` | **killed**, as expected |
| B: appended false row on holding sid | `false_corrections 1`, 11 true rows valid | `false_corrections 1 valid_corrections 11`, `unresolved 1`, `met False` | **killed**; item's `unresolved 0` is wrong vs frozen counter+prereg (`unresolved_ids []`) |
| baseline/restore control | `met True … unresolved 0` | identical both times | control holds |

## Coverage observations (reported, not acted on)

1. Absolute-path pointers sit outside the extractor: `in_lane()` (`count-c1.py:118-120`) rejects
   any path starting with `/`, and extraction reads only the BASE blob. A statement written with
   an absolute path would therefore never be a base statement — the absolute form used in mutation
   A is a potential evasion shape for future base text (it cannot change the current 69).
2. The append-only guard is a whole-file byte prefix, so any single in-place byte edit costs the
   whole census (69 unresolved) even when the mismatch list is untouched — by design per the
   preregistration, confirmed here.

## Tooling

None installed. Used `/usr/bin/git` and the system `python3` standard library only; no pacman, no
network. Pacman guard respected.

## Artifacts

`out/MutateAppend/baseline.json` (with `--list`), `mutA.json`, `mutB.json`, `restored.json`,
`restored-final.json`.

Scratch clone retained at `/tmp/kama-r29-w2-MutateAppend` (disposable; nothing outside it was
deleted).
