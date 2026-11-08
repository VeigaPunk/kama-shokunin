# EX02BudgetControl — final output (verbatim from w1-results.json by the L1)

Seat `EX02BudgetControl`, agent `executor`, wave kama r97 w1. This file is the seat's final
output string copied verbatim from `.ufo/waves/round-97/w1-results.json`; the L1 added only
this header. The seat's own receipts sit beside it.

```
{
  "seat": "EX02BudgetControl",
  "milestone": "kama r97 w1 / C2 operability",
  "report": ".ufo/waves/round-97/w1/EX02BudgetControl.md",
  "receipts_dir": ".ufo/waves/round-97/w1/out/EX02BudgetControl/",
  "revision_pins": {
    "rev_master_resolved": "e057166e09ec069725bd0b0433fc50275ecd03ea",
    "counter_sha256": "24e2fad7c4fb58e9f3a4b56d8bbff776beac7ebd4a27fef581fae529fcb6ca2c",
    "probe_sha256_master": "0897ebffc304fe8d487eff4194f39e42210c3dbc2116e5511fbc472237487ca8",
    "probe_sha256_base_40763bd2": "11e5b01b8d01b5c56ad0200f04c0871a95d398eafc71a3819cb2629fc561e709",
    "note": "base..freeze probe diff is comment-only (5 + nd text); counter bytes identical at 9e605d41/e057166e/HEAD"
  },
  "results": {
    "new_none_real": {
      "rc": 0,
      "cells_ok": 4,
      "survived": 1,
      "wall_s": 17.2
    },
    "new_flat6": {
      "rc": 0,
      "caught": 1,
      "red_cells": [
        "W15"
      ],
      "wall_s": 22.3
    },
    "new_undercharge": {
      "rc": 0,
      "caught": 1,
      "red_cells": [
        "W14",
        "W15",
        "W17"
      ],
      "wall_s": 23.3
    },
    "new_maxmeta": {
      "rc": 0,
      "caught": 1,
      "red_cells": [
        "W16"
      ],
      "wall_s": 23.3
    },
    "new_nopreamble": {
      "rc": 0,
      "caught": 1,
      "red_cells": [
        "W14",
        "W15",
        "W17"
      ],
      "wall_s": 23.4
    },
    "legacy_undercharge": {
      "rc": 0,
      "cells": 13,
      "cells_ok": 13,
      "survived": 1,
      "wall_s": 140,
      "w03_s": 70.12,
      "all_13_pass": true
    },
    "exit_codes": {
      "met": 0,
      "violated": 1,
      "could_not_evaluate": 2,
      "usage": 64,
      "probed_cases": [
        "survived(mutated expectation)=1",
        "caught+mutant-none=64",
        "unresolvable rev=2",
        "anchor count 0=2"
      ]
    },
    "oracle": {
      "t900k": {
        "designed": "-",
        "derived": "-",
        "steps": 5400004
      },
      "mid4": {
        "designed": "-",
        "derived": "-",
        "steps": 6300004
      },
      "maxmeta": {
        "designed": "invalid",
        "derived": "invalid",
        "steps": 15,
        "why": "offset 1<<40 != expect 0 at pos 167772205 < 512MiB"
      },
      "t833333_bonus": {
        "designed": "-",
        "derived": "-",
        "steps": 5000002
      },
      "disagreements": 0,
      "fixture_sha256": {
        "t900k": "0e0a51cf5ff7c9c91b07d4126ff239e3a45d8961b6fe5d56a929211aab6be8f4",
        "mid4": "868d489bbce0cbd5108af0e5c94c588d30bfac84a21b73ddaaea1064479164c6",
        "maxmeta": "d2e18f445c4b342c85c644b188207e843843e8fb09563bbbebf8d28a18a09be8",
        "t833333": "90d60f50b1d1aafc31467bfc9ae16f5b9246fb06c67fef21496aedba24e01882"
      }
    }
  },
  "findings": [
    {
      "id": "D1",
      "severity": "calibration/medium",
      "file": "tools/round97-router-budget.py:174-175",
      "finding": "shipped `nopreamble` patch `steps[0] += 0 if steps[0] < 4 else 1` is dead code (steps[0] never reaches 4), so it removes ALL need() charging, not the preamble. Its red-cell signature (W14/W15/W17) is identical to `undercharge`; no frozen mutant exercises the true preamble-drop class. A real `steps = [-4]` patch flips W17 only (t900k -, mid4 -, t833333 invalid), verified by direct probe runs.",
      "evidence": "out/EX02BudgetControl/preamble_drop_probe.out; new-nopreamble.out; freeze nopreamble sha reconstruction 9035b55e..."
    },
    {
      "id": "D2",
      "severity": "latent robustness/low",
      "file": "tools/round97-router-budget.py:622-630",
      "finding": "control summary computes survived=int(n_ok==n) with no n==len(selected) assertion; a zero-cell selection would print survived=1 and exit 0. Not reachable via current CLI (line 455 forces n_slow>=8 for legacy), but the completeness guard is absent."
    },
    {
      "id": "D3",
      "severity": "calibration/low",
      "file": ".ufo/waves/round-97/controls/c2-new-mutants.out",
      "finding": "freeze control receipts pin the base probe sha 11e5b01b (40763bd2), not the probe under claim 0897ebff (freeze/amendment probe). Behavior identical (comment-only diff); my re-run at master reproduces all cell outcomes and patched shas, but the receipt does not bind M2 probe bytes."
    },
    {
      "id": "D4",
      "severity": "informational",
      "file": "wave brief vs plans/round-97-claims.md",
      "finding": "brief says '16 cells; W14/W15/W16 catch three mutants'; frozen plan/counter say 17 cells (13+W14-W17) and four mutants. Graded the frozen 17-cell set per binding plan."
    },
    {
      "id": "D5",
      "severity": "limit",
      "file": "tools/round97-router-budget.py:622-630",
      "finding": "`caught` = any cell red on a single natural pass (runs=1); no per-mutant expected-cell assertion and no repeat, so a transient failure could certify caught; `--control --expect caught --mutant none` is rejected (rc=64), blocking arbitrary external-probe certification."
    }
  ],
  "lane_files_modified": [],
  "tracked_files_modified_by_me": [],
  "scratch_removed": true,
  "tools_installed": [],
  "blockers": [],
  "risks": [
    "legacy timing measured with a light concurrent single-process analysis overlapping part of the run; W03 inner 70.12s < 75s margin confirms amendment-1 rationale but does not affect control-mode survival grading",
    "freeze receipts' mutant hashes reproduce exactly from base probe + frozen patch table (flat6/undercharge/maxmeta/nopreamble all matched)"
  ]
}
```
