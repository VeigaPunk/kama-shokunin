# RV02BudgetCells — final output (verbatim from w1-results.json by the L1)

Seat `RV02BudgetCells`, agent `reviewer`, wave kama r97 w1. This file is the seat's final
output string copied verbatim from `.ufo/waves/round-97/w1-results.json`; the L1 added only
this header. The seat's own receipts sit beside it.

```
{
  "seat": "RV02BudgetCells",
  "round": "kama r97 w1",
  "report": ".ufo/waves/round-97/w1/RV02BudgetCells.md",
  "receipts": ".ufo/waves/round-97/w1/out/RV02BudgetCells/",
  "rev_graded": "e057166e (probe sha 0897ebff, counter sha 24e2fad7 = freeze 9e605d41; K1 holds)",
  "verdict_on_c2_sentence": "Instrument survives; the sentence does not as written. The 17 cells do catch the four named arithmetic classes (W15/W16/W17 each uniquely necessary), and the 13 legacy cells are green under the shipped mutants. But (1) the predicate's receipt clause says 'three new cells' of four (plan:77, counter docstring:13, committed w1-spec '16 cells'); (2) the shipped nopreamble mutant charges ZERO parser steps, not four fewer, so it is not the preamble-drop forgery the plan maps to W17; (3) the only exit-0 measurement is amendment 1's --slow-files 72 run, whose receipt records neither the flag nor the 72-entry count, labels the cell 'W03-slow-x40', and ran with load1_nat=89.53 (saturated by sibling probes, including mine). The verbatim frozen command exits 2 (committed receipt).",
  "findings": [
    {
      "severity": "blocker",
      "id": "F1",
      "finding": "C2 predicate says 'three new cells' of four; plan:77, counter:13, w1-spec.json (committed in freeze) say 16 cells/three mutants while CELLS=17 and NEW_CELLS/MUTANTS are four. Receipt clause ungradable as written."
    },
    {
      "severity": "major",
      "id": "F2",
      "finding": "nopreamble patch (counter:174-176) is a fixed point: steps[0] += 0 if steps[0] < 4 else 1 never increments. Measured 0 steps on t900k/t833333/mid4; a true 4-step drop gives 4,999,998 at W17 and stays '-' at W14/W15. My shape A (call-counter patch) reds W17 only; the shipped receipt reds W14/W15/W17, proving it is an all-need-free (undercharge-class) probe, not the claimed shape."
    },
    {
      "severity": "major",
      "id": "F3",
      "finding": "W03 docstring (counter:93) says the guard fires below 1.5 x 60 s; MARGIN=1.25 (line 157) fires at 75 s. Same false-constant class as round-96 routed defect 1, now inside a frozen counter."
    },
    {
      "severity": "major",
      "id": "F4",
      "finding": "Amended predicate receipt cannot prove its own command: --slow-files not echoed (grep -c slow_files in measured/c2.out = 0), W03 id hardcoded 'W03-slow-x40' at 72 entries (counter:487), summary prints w03_seconds but not the count (counter:674). A 40-file loaded run (my legacy flat6, W03 223.95s at load 71-118) produces an indistinguishable receipt."
    },
    {
      "severity": "major",
      "id": "F5",
      "finding": "The passing measured run (exit 0, exact predicate line) records load1_nat=89.53 and burners=64; its 'natural' leg ran under sibling wave-1 probes (my own controls 08:26-08:49 included). Margin satisfied by contention, not host speed; amendment 1's 72x1.37s=99s idle figure is unverified."
    },
    {
      "severity": "major",
      "id": "F6",
      "finding": "Frozen legacy/new mutant receipts were produced at rev 40763bd2 (probe sha 11e5b01b), not the freeze probe (0897ebff); mutant shas differ (14efbe6f/2e31ff3b/6b5f6db4/9035b55e vs cae7b367/3a709856/22c311f1/b27dc8bf). The base->freeze probe diff is comment-only, and my runs at e057166e reproduce every verdict, but the receipts do not themselves show 'patches of the probe under claim'."
    },
    {
      "severity": "minor",
      "id": "F7",
      "finding": "KILL=1200s (counter:148) is below the probe's derived pass limit 20+25*72=1820s for the amended W03 fixture; latent counter-side timeout on a ~12x slower host."
    },
    {
      "severity": "minor",
      "id": "F8",
      "finding": "Amendment 1 says 'before any C2 cell scored' while the exit-2 run printed all 17 natural cells ok=1; 'same 17 cells' hides W03's 40->72 fixture change with an x40 label."
    }
  ],
  "non_findings": [
    "flat6 is genuinely constant 6: measured 4,200,004 steps on mid4 (my initial static count of 5 was refuted by measurement; skip(u64()) charges two steps).",
    "W16 is the unique catcher of the 100 MiB MAX_META mutant; W15 unique for constant 6-7; W17 unique for a true 4-step preamble drop.",
    "K1: counter bytes identical at freeze/HEAD/worktree; probe at HEAD equals freeze.",
    "The 13-cell blind spot is structural: every legacy fixture's complete parse is also its designed class, and W12/W13 charge through the string-array loop (probe:703), not need(); the shell flips to MODEL_OK when any candidate is undecidable (probe:939, nbad<ncand)."
  ],
  "shapes": {
    "shipped_flat6": "caught, W15 only; legacy survived=1 (my run at e057166e)",
    "shipped_undercharge": "caught, W14/W15/W17; legacy survived (frozen)",
    "shipped_maxmeta": "caught, W16 only; legacy survived (frozen)",
    "shipped_nopreamble": "caught, W14/W15/W17 at 0 steps; NOT the claimed 4-step drop; legacy survived (frozen)",
    "shapeA_true_preamble_drop": "W17 only red (4,999,998 on t833333); all 13 legacy + W14/W15/W16 green; cells_ok=16",
    "shapeB_persistent_step_memo_no_ctime": "caught by legacy W02/W03/W08/W10, all four new cells green; cells_ok=13; new-cell set blind to it",
    "shapeC_constant7": "W15 only red (4,900,004 on mid4); constant 8 would be caught by W11 at nd=1"
  },
  "amendment_2_note": "plans/round-97-amendment-2.md is untracked at observation and unapplied. Its C2 v2 plans fix the count prose and add --expect-cell, but does not address F2 (patch replacement), F3 (1.5/1.25), F4 (slow_files echo/W03 label), F5 (load confound), or F7 (KILL); K1 restatement needs a new declared baseline.",
  "verification_gaps": [
    "No LSP device mounted in this seat; text-level caller check only (no Python importers of the counter).",
    "Passing measured/c2.out is uncommitted at observation (M in git status); graded at its 08:48:40 bytes.",
    "Legacy survival for undercharge/maxmeta/nopreamble taken from frozen base-rev receipts plus the comment-only probe diff; I ran the legacy set myself only for flat6.",
    "My own seat's counters contributed to the authoritative run's load1_nat=89.53.",
    "Shape B's predicate-mode amplification (W11 second run) is inferred, not run."
  ],
  "hygiene": "No tracked lane file edited; no git/jj mutations; no packages installed; scratch /fast/scratch/hyaku/kama-r97/RV02BudgetCells deleted; receipts and forged-probe scripts copied to the out dir (264K)."
}
```
