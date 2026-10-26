# D9Receipts — round-48 item report (lane kama, round 47 closure D9 audit)

**Verdict: CONFIRMED DEFECT — report claims not backed by receipts.** `/home/vgpnk/Projects/shokunin/.ufo/reports/round-47/kama.md:99` states "The r41, r42, r43 and pointer checks were re-run at the final tip `6b7e6cf8` with `met=True`", but the only committed receipts for those instruments record `tip=3442d707…` (r41/r42/r43) or carry no hash field at all (pointer-final), and no receipt anywhere in the lane at `6b7e6cf8` mentions `6b7e6cf8`. Three explicit tip disagreements + one unbackable claim; five more receipts cited by the report have no provenance field and cannot prove which commit they measured.

## 1. Evidence: report statement vs receipt `tip=` — full tabulation

Method: every "measured / re-measured / re-run / holds at `<hash>`" statement in `/home/vgpnk/Projects/shokunin/.ufo/reports/round-47/kama.md` was paired with the receipt file it cites (or, for the L99 instrument list, with the instrument's last existing receipt by suffix priority `-final` > `-fix` > `-after`), and the receipt's `tip=` line compared to the claimed hash. Receipt copies cited below are in `receipts/` next to this report (originals under `.ufo/waves/round-47/measured/`).

| # | report:line | Claim (abridged) | Claimed tip | Receipt | Receipt `tip=` (file:line) | Verdict |
|---|---|---|---|---|---|---|
| 1 | 8 | measured commit `383f1fc7`; "Re-measured at `3442d707`" | 383f1fc7 / 3442d707 | (unnamed; realized by rows 2–5) | — | consistent |
| 2 | 70 | "Measured `383f1fc7`" (C1) | 383f1fc7 | c1-after.out:2 | `tip=383f1fc780573d…` | AGREE |
| 3 | 70 | "same result holds at `3442d707`" | 3442d707 | c1-fix.out:2 | `tip=3442d707fdf926e…` | AGREE |
| 4 | 81 | "Measured `383f1fc7`" (C2) | 383f1fc7 | c2-after.out:2 | `tip=383f1fc780573d…` | AGREE |
| 5 | 81 | "same result holds at `3442d707`" | 3442d707 | c2-fix.out:2 | `tip=3442d707fdf926e…` | AGREE |
| 6 | 89–92 | "Tip regressions at `383f1fc7` and `3442d707`": r41 after/fix | both | r41-after.out:1, r41-fix.out:1 | `tip=383f1fc7…` / `tip=3442d707…` | AGREE |
| 7 | 89–92 | r42 after/fix | both | r42-after.out:1, r42-fix.out:1 | `tip=383f1fc7…` / `tip=3442d707…` | AGREE |
| 8 | 89–92 | r43 after/fix | both | r43-after.out:1, r43-fix.out:1 | `tip=383f1fc7…` / `tip=3442d707…` | AGREE |
| 9 | 90–97 | gate/cap/digest/hexrun `-after`/`-fix` at both commits | both | gate-*, cap-*, digest-*, hexrun-*.out | **no tip/commit field** | UNVERIFIABLE |
| 10 | 96 | "hexrun-census … exit 0 at `3442d707`" | 3442d707 | hexrun-fix.out | **no tip field** (values unknown=0 ledger_bad=0 exit=0 do match) | UNVERIFIABLE |
| 11 | 98 | "pointer check `met=True` at the tip" | the tip (= 6b7e6cf8 per L99) | pointer-final.out | **no tip field** | UNVERIFIABLE |
| 12 | **99** | **"r41 … re-run at the final tip `6b7e6cf8`"** | **6b7e6cf8** | **r41-fix.out:1** | **`tip=3442d707fdf926e…`** | **DISAGREE** |
| 13 | **99** | **same for r42** | **6b7e6cf8** | **r42-fix.out:1** | **`tip=3442d707fdf926e…`** | **DISAGREE** |
| 14 | **99** | **same for r43** | **6b7e6cf8** | **r43-fix.out:1** | **`tip=3442d707fdf926e…`** | **DISAGREE** |
| 15 | **99** | **same for pointer** | **6b7e6cf8** | **pointer-final.out** | **no tip field** | **DISAGREE (unbackable)** |

Score: 8 AGREE, 3 DISAGREE (explicit tip mismatch), 3 UNVERIFIABLE (receipt lacks any hash field), 1 consistent-by-implication.

## 2. Why the DISAGREE rows are real, not a naming artifact

Git topology in the lane (read-only commands, no mutation):

```
$ git -C kama-shokunin log --format='%H %s' --first-parent -6 6b7e6cf8d30b5794ed72fe97eb0e666f9b0572a9
6b7e6cf8… round-47: late seat report revisions (S9Cap, S9Scorecard)
76a7aaff… round-47: measured results, wave results, end census, misroot sweep, fix-commit receipts
3442d707… round-47: post-measure fixes - replay checks the archive member digest before executing …
383f1fc7… round-47: integration (measured) …
```

- Every `-fix`/`-final` receipt was **added by `76a7aaff`** — the commit *before* the final tip:
  `git log --diff-filter=A 6b7e6cf8… -- .ufo/waves/round-47/measured/<f>` → `76a7aaff` for pointer-final.out, r41-fix.out, r42-fix.out, r43-fix.out, hexrun-fix.out, c1-fix.out, c2-fix.out.
- `git grep -c 6b7e6cf8 6b7e6cf8d30b… -- .ufo/waves/round-47/measured/` → **no match**: zero receipts at the final tip record the final tip.
- `6b7e6cf8` itself only revised two seat reports (S9Cap, S9Scorecard); it added no counter receipts.

So at the final tip the newest receipt evidence for r41/r42/r43/pointer is the `3442d707`-era set. L99's "re-run at the final tip `6b7e6cf8`" is either an unrecorded run or an overstated tip. Note r41's own receipt pins `tip=3442d707` *inside the receipt*, so the mismatch is machine-checkable, exactly the class of drift D9 exists to catch.

**Proposed fix (either, author's choice):**
(a) re-run the four checks at `6b7e6cf8` and commit `r41-final.out`, `r42-final.out`, `r43-final.out` (each with `tip=6b7e6cf8d30b5794ed72fe97eb0e666f9b0572a9`) and a `pointer-final.out` that carries the same `tip=` line; or
(b) correct kama.md:99 to "re-run at `3442d707`", which is what the committed receipts show.
Additionally (schema fix, lane-side convention, not edited in place by this seat): every receipt in `measured/` should carry a `tip=` line. Today gate-after/fix, cap-after/fix, digest-after/fix, hexrun-after/fix, pointer-after/final, seat-yield-w1.out, misroot-sweep.out and both selftest receipts have no provenance field, so rows 9–11 and 15 can never be verified retroactively. A one-line addition at receipt-write time (`echo "tip=$(git rev-parse HEAD)"`) closes the whole class.

## 3. Checker (delivered, stdlib-only)

`tip-receipt-check.py` (same directory as this report) flags exactly such mismatches. Pseudo-code:

```
for each report line:
  hashes  = all hex runs >= 8 chars            (skip sha256 literals)
  refs    = cited receipts  <name>.out         (globs like *-fix.out ignored)
  instru  = instrument tokens (r40-49, pointer, gate, cap, digest, hexrun, c1, c2)
  if refs:      # Form A — pair each receipt with the NEAREST hash before it
      for ref: compare claimed hash with receipt's tip= field -> AGREE/MISMATCH/NO_TIP
  elif instru and claim-marker("measured|re-run|holds| at `") and hashes:
      for name: # Form B — resolve instrument to last receipt: -final > -fix > -after
          compare claimed hash with that receipt's tip= field
receipt tip field regex: ^\s*(tip|commit|lane_oid|head)\s*[=:]\s*<40-hex>\b
prefix match allowed (reports cite 8-char prefixes)
exit 1 on any MISMATCH (or NO_TIP/MISSING under --strict)
```

Runs (all four recorded in this directory):

```
$ python3 tip-receipt-check.py --report /home/vgpnk/Projects/shokunin/.ufo/reports/round-47/kama.md \
    --receipts /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/measured
FAIL  kama.md:99  r41-fix.out  claimed=6b7e6cf8  receipt=3442d707fdf926ec5ea3f34363cf2f0899cc79b5:1
FAIL  kama.md:99  r42-fix.out  claimed=6b7e6cf8  receipt=3442d707fdf926ec5ea3f34363cf2f0899cc79b5:1
FAIL  kama.md:99  r43-fix.out  claimed=6b7e6cf8  receipt=3442d707fdf926ec5ea3f34363cf2f0899cc79b5:1
warn  kama.md:99  pointer-final.out  claimed=6b7e6cf8  receipt=<no hash field>
warn  kama.md:96  hexrun-fix.out     claimed=3442d707  receipt=<no hash field>
summary claims=9 agree=4 mismatch=3 no_tip=2 missing=0 failed=1 exit=1     # exit 1 — fails on the D9 case
```

Control (same checker, only L99's hash corrected `6b7e6cf8 → 3442d707`, copy kept as `kama-corrected-control.md`): `summary claims=9 agree=7 mismatch=0 … exit=0` — the checker is not a constant failure; with `--strict` the control also exits 1 solely on the two receipts that lack a hash field.

Checker bugs found and fixed during this item (recorded for honesty): v1's `tip=` regex anchored `$` and missed receipts with trailing fields (`… base=…`, `… started=…`), mislabeling c1/c2 receipts NO_TIP; v1 also scanned sha256 literals (`bf94332a…`) as claim hashes. Both fixed in the delivered version; run1/run3 outputs above are from the fixed version.

## 4. Residual risk and verification gaps

- Whether an unrecorded r41/r42/r43/pointer re-run at `6b7e6cf8` actually happened is unknowable from the lane: the receipts that would prove it do not exist. Only the report text asserts it.
- Rows 9–11 (gate, cap, digest, hexrun, pointer receipts) have no provenance field at all; their commit attribution rests entirely on the surrounding report text and on which commit added the files (`76a7aaff`), not on receipt content.
- The checker's Form B resolves an instrument to one receipt (latest existing); it does not verify that `-after` and `-fix` receipts both exist, and it cannot detect a receipt whose `tip=` line was hand-edited to match the report — that requires signing receipts (e.g., `tip` + commit of the receipt file itself).
- Lane and fleet repo were used strictly read-only (git log/cat-file/grep + file reads); no counters were re-run for this item (not needed: the D9 mismatch is fully determined by committed bytes).

## Files written

- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/D9Receipts.md (this report)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/D9Receipts/tip-receipt-check.py
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/D9Receipts/run1-real-default.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/D9Receipts/run2-real-strict.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/D9Receipts/run3-control-default.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/D9Receipts/run4-control-strict.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/D9Receipts/kama-corrected-control.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/D9Receipts/receipts/ (c1-after/fix, c2-after/fix, r41-after/fix, r42-fix, r43-fix, hexrun-fix, pointer-final)
