# MT01Forgeries — final output (verbatim from w1-results.json by the L1)

Seat `MT01Forgeries`, agent `mutation-tester`, wave kama r97 w1. This file is the seat's final
output string copied verbatim from `.ufo/waves/round-97/w1-results.json`; the L1 added only
this header. The seat's own receipts sit beside it.

```
{
  "report": ".ufo/waves/round-97/w1/MT01Forgeries.md",
  "out_dir": ".ufo/waves/round-97/w1/out/MT01Forgeries/",
  "scratch": "/fast/scratch/hyaku/kama-r97/MT01Forgeries (created, 1.2G peak, removed; receipts copied first)",
  "lane_untouched": "tools/kama-probe.sh sha256 0897ebffc304fe8d487eff4194f39e42210c3dbc2116e5511fbc472237487ca8 unchanged; only .ufo outputs written",
  "mutants": {
    "A_one_step_per_header": "de49e3f1f8889545eb536b3706eefed90f595bd46eb295b8b39f8647f0ab9d1b",
    "B_constant6": "7cd3894278eb70e9192aa8e41465c48a5ed10a049fcf3f2a7f4302dd6d38a990",
    "C_maxmeta_100MiB": "0c6e7c2797a50ed9798335f8421162b38df2b95feb5cf5cd43fd71872216edef",
    "D_ctime_dropped": "2901ca9f1af551aab40e1d2cd08a494aab8031ba3c866a932452b9898399fcb4",
    "E_true_preamble_drop": "f9e6507f1b22b95a35620d812972617e3e428f8ca4407153ccee23808c151103",
    "G_maxsteps_lowered_4M": "bd52585d51643617ccfe209d24010bd7f8aeddc1b100a6e5f43f73a0397de14e"
  },
  "matrix": {
    "round96_13cells": "P/A/B/C/D/E all 13/13 green -> survives; legacy set discriminates none",
    "r97_legacy_13": "P/A/B/C/D/E all cells=13 cells_ok=13 survived=1",
    "r97_new_4": {
      "P": "4/4 survived=1",
      "A": "1/4 (W14,W15,W17 red) caught",
      "B": "3/4 (W15 red) caught",
      "C": "3/4 (W16 red) caught",
      "D": "4/4 survived=1 (disclosed miss)",
      "E": "3/4 (W17 red only) caught",
      "G": "4/4 survived=1 (one-sided false green)"
    }
  },
  "findings": [
    "F1: W14/W15/W16/W17 are sized past the four named forgery classes; P pristine is 4/4 and 13/13; margins computed (W14 catches any integer per-header charge <=5 at nd=1; W17 is the unique discriminating integer count).",
    "F2 (receipt honesty): the counter's nopreamble mutant at tools/round97-router-budget.py:174 charges `0 if steps[0] < 4 else 1`, and steps stays 0 for every header-only file, so it is a no-budget mutant, not a preamble mutant: identical to `undercharge` on all 8 fixtures and same cells_ok=1. Its W17 red is unbounded-header evidence; my E is the first isolating proof that W17 catches a true preamble drop (W14/W15 green).",
    "F3: `--cells new --control` is one-sided (3 of 4 cells expect '-'); MAX_STEPS=4,000,000 scores cells=4 cells_ok=4 survived=1, yet flips the W11 shape (P m700k1 invalid vs G '-'). Only the union with legacy W11 pins the lower bound.",
    "F4: freeze-time control receipts patched probe 11e5b01b (rev 40763bd2), not the freeze probe 0897ebff; git diff shows 2 changed lines, both comments -> behaviourally identical, but the receipts do not name the bytes under claim.",
    "F5: stale 'three' vs four: tools/round97-router-budget.py:13 and plans/round-97-claims.md:76-77 say three new cells/control receipts while NEW_CELLS has four, CELLS=17; C1 does not grade this prose.",
    "F6: D (ctime) is unobservable from the public path - SEEN is per-process, one parse per inode per invocation (1 path 2.89s, 4 hardlinks 2.83s, 4 copies 11.07s); only a concurrent external writer could change ctime between two stat() calls, which is non-deterministic. P and D identical on all 8 fixtures incl. the two-invocation W10 rewrite, so W10 does not exercise the ctime key either.",
    "F7: the new-cell baseline receipt in c2-new-mutants.out is the round-96 probe (rev 40763bd2); my freeze-bytes baseline is 4/4 survived=1.",
    "F8: W16 grades only lowered caps (<160MiB); a raised MAX_META survives - matches the declared class.",
    "C3 depth audit (secondary): rows do recompute from the probe's MAX_STEPS - raising MAX_STEPS to 6,000,000 flips 3 of 6 rows (mismatches=4 incl. the literal 5,000,000 check); steps, comparison and required-row mutations each give mismatches=1; an extra wrong row is graded; a correct duplicate passes (benign). Predicate at 9e605d41: rows=6 checks=8 mismatches=0 met=True rc 0."
  ],
  "false_greens": [
    "new-cells-only control survives a too-small budget (G)",
    "nopreamble receipt proves a different class than it names",
    "D all-green but correctly disclosed as unobservable"
  ],
  "tooling": "none installed; bash + python3 stdlib + read-only git only",
  "limits": "natural-pass/control grading only (no synthetic-load pass); graded the four named classes plus E and G"
}
```
