# MT02ReasonRowMutants — C2 reason-row binding, mutation report

## Scope

Mutation-tested C2's frozen binding counter `tools/round90-reason-rows.py` at the measured commit
M2 `2ee0b55f4d3fd0cb3157d26b03280c1d21e27b2d` (lane `master`, tree clean at M2). Work ran in one
`git clone --shared` scratch clone; toplevel asserted as
`/fast/scratch/hyaku/kama-r90/MT02ReasonRowMutants/wt` before any commit. Every mutation is one commit
whose parent is M2 (commits made with `-c user.name=fixture -c user.email=fixture@invalid`), and the
clone was `git reset --hard 2ee0b55f…` between mutations. No tracked lane file was written; my lane
writes are this report and `.ufo/waves/round-90/w1/out/MT02ReasonRowMutants/` only.

Bytes measured at M2: counter `fa4c31771783e533aabd68bd82437fbb681e058c6a19debe3e3fbe2c90d2f095`
(identical at freeze F `6f6d7873…` — K1 clean), probe `c197912f8b3b5567e3ffd38178cb3a6e87187d7fb13136308c9a461ba8d2ef97`,
SKILL.md `282e0c15fb541640360779a76fd3565316ff336ef2711695c1ec8e9c9af490ce`, receipt `7165e9ab4fe9619ccc04775bffc1c73ef6ddcf4ce5d85a7b24a47ff4f8daa262`.

## Commands and outputs

```
WT=/fast/scratch/hyaku/kama-r90/MT02ReasonRowMutants/wt
OUT=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-90/w1/out/MT02ReasonRowMutants
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round90-reason-rows.py --repo "$WT" --rev HEAD
```

Baseline at M2: exit 0,
`REASON_ROWS population=23 documented=23 rows=24 bound=24 unbound=0 missing=0 duplicates=0 additional=1 receipt=current probe_sha256=c197912f8b3b5567e3ffd38178cb3a6e87187d7fb13136308c9a461ba8d2ef97 rev=2ee0b55f4d3fd0cb3157d26b03280c1d21e27b2d`
(`out/baseline-m2.out:25`). Matches the C2 predicate.

Per mutation: edit in clone → `git -C "$WT" -c user.name=fixture -c user.email=fixture@invalid commit -aqm "<label>"`
→ `python3 …/round90-reason-rows.py --repo "$WT" --rev HEAD` → record exit → `git reset --hard 2ee0b55f…`.
Full commit diffs: `out/mutants.patch`; per-run stdout: the listed `.out` file.

| # | Mutation (commit) | Expected | Observed (evidence) | Exit | Verdict |
|---|---|---|---|---|---|
| 1 | swap verdicts of `matched` and `served-id-mismatch` rows (`73e47b91c48e36637badb424a6b9b5e065f4a81a`) | both rows unbound | `bound=22 unbound=2`; `REASON_ROW matched bound=0`, `REASON_ROW served-id-mismatch bound=0` (`out/m1-swap-verdicts.out:25`) | 1 | killed |
| 2 | rename row cell `R-matched`→`R-matched-renamed` (`fd9246916ef87126009ee06058648621577fcbd1`) | that row unbound | `bound=23 unbound=1`; `REASON_ROW matched bound=0` (`out/m2-rename-cell.out:25`) | 1 | killed |
| 3 | delete the `matched` row (`3bb575a6e4fc670695ea5c5ecd9ce9b94b063c07`) | missing=1, rows=23 | `documented=22 rows=23 missing=1`; `REASON_MISSING matched` (`out/m3-delete-row.out:25`) | 1 | killed |
| 4 | duplicate the `matched` row verbatim (`64ba0bd22d13acea976deb215bf341400ea2d241`) | duplicates=1; duplicate binds too | `rows=25 bound=25 duplicates=1`; two `REASON_ROW matched bound=1` (`out/m4-duplicate-row.out:26`) | 1 | killed |
| 5 | move `matched` below the next `## ` heading (`85d53886a8c6a4b7c3936b6b54374892790b28e4`) | row ignored, missing=1 | `documented=22 rows=23 missing=1`; `REASON_MISSING matched` (`out/m5-row-after-heading.out:25`) | 1 | killed |
| 6 | edit receipt `R-matched` verdict `MODEL_OK`→`MODEL_LOADING` (`bbe0e15aa19ab4a0f6b7d805422dbd2aceaaf130`) | that row unbound | `bound=23 unbound=1 receipt=current`; `REASON_ROW matched bound=0` (`out/m6-receipt-verdict.out:25`) | 1 | killed |
| 7 | change one probe byte (comment `Round`→`round`; probe sha256→`9dd8ddd5dcffdd85dc4aecf888adef975a7953f52d76595451a4ab8577e35133`) (`2758511dfae0c2e80651741e6b58e2f188c6ddb9`) | stale receipt binds nothing | `bound=0 unbound=24 receipt=stale` (`out/m7-probe-byte.out:25`) | 1 | killed |
| 8 | delete the receipt (`6cd4cd5cf806864605bfcf18ef210e27e72a9c36`) | receipt=absent, bound=0 | `bound=0 unbound=24 receipt=absent` (`out/m8-delete-receipt.out:25`) | 1 | killed |
| 9 | probe mutant rc 63 → `NOT_HTTP`/`no-http-response`, then re-capture receipt and commit both (`a012e123bb9aa3a359197bfbb10d8d2a9ac4a8af`) | `body-too-large` row unbinds | capture: `R-body-too-large verdict=NOT_HTTP reason=no-http-response`; rows: `REASON_ROW body-too-large bound=0`, `bound=23 unbound=1 additional=0 receipt=current` (`out/m9b-capture-probe-mutant.out`, `out/m9c-rows-after-recapture.out:25`) | 0 (capture) / 1 (rows) | killed |
| X1 | receipt line `R-matched` `exit` 0→2, verdict kept `MODEL_OK` (`807562cba1403a618605a78fbf68c808073301e4`) | counter ignores `exit` | `bound=24 unbound=0 duplicates=0` (`out/x2-receipt-exit-contradiction.out:25`) | 0 | escaped (out of predicate) |
| X2 | SKILL `matched` trigger prose replaced by a sentence that contradicts its receipt cell (`1bff3acde405b0de000de960c8761e50ce589c20`) | counter reads no prose (K2 is reviewer read) | `bound=24 unbound=0` (`out/x1-trigger-prose-lie.out:25`) | 0 | escaped (out of predicate) |
| X3 | add a fifth column to the `matched` row (`c1215efecf697eb3e0cdbfbc15d5c7971768fb03`) | row not exactly 4 cells → unbound | `bound=23 unbound=1`; `REASON_ROW matched bound=0` (`out/x3-extra-column.out:25`) | 1 | killed |

Capture control (pristine probe, M2):
`TMPDIR=$S/tmp-base python3 …/tools/round90-reason-capture.py --repo "$WT" --rev HEAD --work $S/work-base --out $S/receipt-base.jsonl`
exited 0; `cmp` against the committed receipt was identical, sha256 `7165e9ab4fe9619ccc04775bffc1c73ef6ddcf4ce5d85a7b24a47ff4f8daa262`
(`out/m9a-capture-pristine.out`; `out/m9a-receipt-pristine.jsonl`). This confirms the producer is deterministic
and attributes the rc-63 change to the probe bytes, not to capture noise. Clone ended at M2 with
`git status --porcelain` empty after every reset.

Note for mutant 5: at M2 the `## Probe reason codes` section is the last section of SKILL.md (file is 1867
lines; no `## ` heading follows the table), so the fixture appended `## Post-table mutation heading` and moved
the row beneath it; the boundary rule is still exercised.

## Findings

- NOTE — C2's binding holds at M2 and every assigned mutant is killed by the frozen counter alone: baseline
  24/24 bound, exit 0; mutants 1–9 all produce the expected binding loss with exit 1 and the claimed counts
  (`out/baseline-m2.out:25`, `out/m1-swap-verdicts.out:25` … `out/m9c-rows-after-recapture.out:25`).
- NOTE — Surviving surface 1: the counter never reads the trigger prose column, so a row whose trigger
  contradicts its own receipt cell still binds (`out/x1-trigger-prose-lie.out:25`, commit `1bff3ac…`). This is
  consistent with frozen C2 kill rule K2 (reviewer read), not a predicate violation; the counter cannot
  substitute for that read.
- NOTE — Surviving surface 2: the receipt `exit` field is not cross-checked against `verdict`, so a
  `MODEL_OK` line carrying `exit=2` still binds (`out/x2-receipt-exit-contradiction.out:25`, commit `807562c…`).
  The predicate only freezes cell/reason/verdict plus probe sha256; re-running the capture producer and `cmp`
  is the control that catches fabricated receipts, and it did reproduce byte-identically.
- NOTE — Mutant 4 confirms the freeze note: a verbatim duplicate binds exactly like its original and the
  mutant dies only through `duplicates=1` (`bound=25 duplicates=1`, `out/m4-duplicate-row.out:26`).
- NOTE — Lane state I did not create: `git status --porcelain` in the lane lists `SCORECARD.md`,
  `corpus/README.md`, `corpus/SOURCES.md` modified and untracked `.ufo/waves/round-90/*` files. My commands
  never wrote those paths; lane HEAD remained `2ee0b55f4d3fd0cb3157d26b03280c1d21e27b2d`.

No BLOCKER and no DEFECT found against the frozen C2 predicate.

## Deliverables

All under `.ufo/waves/round-90/w1/out/MT02ReasonRowMutants/`:
`baseline-m2.out`, `m1-swap-verdicts.out`, `m2-rename-cell.out`, `m3-delete-row.out`, `m4-duplicate-row.out`,
`m5-row-after-heading.out`, `m6-receipt-verdict.out`, `m7-probe-byte.out`, `m8-delete-receipt.out`,
`m9a-capture-pristine.out`, `m9a-receipt-pristine.jsonl`, `m9b-capture-probe-mutant.out`,
`m9-receipt-after-probe-mutant.jsonl`, `m9c-rows-after-recapture.out`, `x1-trigger-prose-lie.out`,
`x2-receipt-exit-contradiction.out`, `x3-extra-column.out`, `mutants.patch`.

VERDICT: holds — C2's counter prints documented=23 rows=24 bound=24 exit 0 at M2 and kills all 8 assigned mutants plus the rc-63 recapture; the two survivors are outside the frozen predicate (prose and receipt `exit`) and are reported as NOTE.
