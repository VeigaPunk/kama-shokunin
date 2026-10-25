# RevLeftovers — r35 leftover status vs the C1 R35-KEEP arm (round 36, wave 3)

Seat: RevLeftovers. Leaf, no subagents. No tools installed. No add/commit/delete/stash/checkout/reset in the lane;
no jj command; lane git index untouched (`git diff --cached` = 0 paths, before and after). All git writes were
`add`/`commit` inside sandbox clones under my seat directory `.ufo/waves/round-36/w3/out/RevLeftovers/` (the
sanctioned sandbox location); the lane was only read.

## Verdict

All seven r35 leftovers are still uncommitted and nothing is staged. Committing **4 of the 7** (report overwrite,
mixed mirror, both helper-skipped HTML files) breaks the C1 R35-KEEP arm — each via a distinct sub-check,
verified by running the frozen counter (`tools/round36-statement-audit.py`) against sandbox tips that commit
exactly one leftover class on top of a landed round-36 lesson. Committing the **3 seat-log flushes** does **not**
break the arm (measured `met True`), though the preregistration still forbids sweeping them ("none of them is
swept").

## The seven paths (measured: `git status --porcelain`, lane tip `9014843cb7de8fbe87a97954c13832b67d55f046`)

| # | Path | Status | Class | Still uncommitted? |
|---|------|--------|-------|--------------------|
| 1 | `.ufo/waves/round-35/w1/out/ConnSibling/seat.log` | ` M` | seat-log flush | Yes |
| 2 | `.ufo/waves/round-35/w1/out/ExecDisposition/seat.log` | ` M` | seat-log flush | Yes |
| 3 | `.ufo/waves/round-35/w1/out/ScoutCoverageAbsence/seat.log` | ` M` | seat-log flush | Yes |
| 4 | `.ufo/waves/round-35/w1/out/ExecDisposition.md` | ` M` | report overwrite | Yes |
| 5 | `.ufo/waves/round-35/assimilation/validate/` | `??` | mixed mirror | Yes |
| 6 | `.ufo/waves/round-35/w1/out/ScribeGate/fetch/docker-dockerfile.html` | `??` | helper-skipped HTML | Yes |
| 7 | `.ufo/waves/round-35/w1/out/ScribeGate/fetch/dockerfile.html` | `??` | helper-skipped HTML | Yes |

These are exactly the seven `KEEP_PATHS` in `tools/round36-statement-audit.py`, and the live round-35 porcelain
subset is still exactly these seven lines. The full porcelain has grown (67 → 92 lines during this seat) from
other seats' round-36 outputs — out of scope here. The ` M` entries are worktree-only (leading space = not
staged); staged count is 0.

## Measured byte facts behind each class

- **Seat-log flushes (1–3):** numstat `142/1`, `2011/1`, `144/1` — the single deleted line in each is the
  committed last line lacking a trailing newline, re-emitted and extended, i.e. post-commit flushes, not rewrites
  (`66bcd07` "post-settlement seat log flushes" landed at 21:32:28; these mtimes are 21:33:xx).
- **Report overwrite (4):** HEAD blob `9307c5d61c1942857a17cb259b4313460b37d0da` (== `DISP_BLOB` in the counter)
  is a 1994-line seat-log dump; worktree blob `54be93f73868b2f46032d61c1066c12925106889` is a 125-line late
  report. Committing the worktree bytes replaces the pinned blob.
- **Mixed mirror (5):** 11 symlinks + 84 regular files; `validate/.ufo` →
  `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo` (absolute, recursive back into the live lane tree); zero
  paths under that prefix are currently tracked.
- **Helper-skipped HTML (6–7):** both 1066624 bytes (over the 1 MiB snapshot skip threshold), untracked while
  all smaller siblings in the same `fetch/` dir were committed at `f45f616`.

## Does committing break the C1 R35-KEEP arm? — measured in sandbox clones

Method: in each sandbox (`sbA`–`sbE`, fresh `git clone --shared` of the lane at `9014843c`), first commit the
untracked `corpus/lessons/round-36.md` draft (so the four correction rows exist and the arm is evaluable), then
commit exactly one leftover class, then run the frozen counter unchanged with `--tip <sandbox HEAD>`:

| Run | Tip contains | Counter output | R35-KEEP |
|-----|--------------|----------------|----------|
| do-nothing | lane tip as-is (lesson not landed) | `uncorrected 4 … met False` | control, matches frozen claim |
| A | lesson only | `uncorrected 0 false_corrections 0 … met True` | holds |
| B | lesson + 3 seat-log flushes | `… met True` | **holds — flushes do not kill it** |
| C | lesson + ExecDisposition.md overwrite | `false_corrections 1 … met False` | **broken** via `disp_blob != DISP_BLOB` |
| D | lesson + validate/ mirror | `false_corrections 1 … met False` | **broken** via `mirror_clear` |
| E | lesson + 2 helper-skipped HTMLs | `false_corrections 1 … met False` | **broken** via `html_clear` |

Inference from the counter code (consistent with B–E): the arm's only tracked-set checks are
`HTML_PATHS not in tracked` and nothing under `.ufo/waves/round-35/assimilation/validate/` tracked; its only
blob pins are the r35 lesson blob, the r35 fleet-report blob, and `ExecDisposition.md == 9307c5d6…`. Seat-log
blobs and trackedness are not checked anywhere in the arm.

## Findings by severity

1. **Verdict (high confidence, measured):** committing paths 4, 5, 6, or 7 — in any combination — flips C1 from
   `met True` to `met False` post-landing. The landing must exclude all four.
2. **Calibration note (measured, counterintuitive):** committing the three seat-log flushes alone leaves
   R35-KEEP holding (`met True`, run B). The prohibition on sweeping them is a preregistration process rule
   ("none of them is swept"), not a counter kill. Reporting them as predicate-breaking would be a calibration
   defect; reporting them as sweep-safe would also be wrong — both facts belong in the disposition.
3. **Info:** the do-nothing control at the lane tip prints `met False / uncorrected 4` because the corrections
   are not yet landed at `9014843c` — expected and consistent with the frozen claims; not a defect. (I did not
   re-derive the C1 7→7 / C2 9→9 calibrations; both are frozen.)
4. **Info:** live porcelain is not a stable set while wave seats run (67 → 92 lines this seat); only the seven
   round-35 lines are the stable leftover set. Classify against the round-35 subset, not the full output.

## Residual risk and verification gaps

- Runs A–E assume the landing commits the lesson draft in its current bytes; if the lesson's R35-KEEP row is
  edited before landing, run A's baseline would need re-measurement (the row itself is one of the wave-3 bytes
  under attack elsewhere — out of my scope).
- The kill on path 4 is specific to the worktree overwrite bytes (`54be93f7…`); committing a byte-identical
  restoration of `9307c5d6…` would not break `disp_blob` — irrelevant in practice, since the overwrite is the
  worktree state.
- I did not examine the C2 predicate (out of scope) nor re-verify the 82-identical/2-stale split inside the
  mirror; symlink/regular counts (11/84) were re-measured directly.
- Other seats may append to the seat logs or touch the four kill paths while this report is read; path classes
  and blob ids were current as of lane tip `9014843cb7de8fbe87a97954c13832b67d55f046` on 2026-10-24.
