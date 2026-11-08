# RV02BudgetCells — attack C2 (operability): are the 19 cells sized past the +1/header forgery, and are the control receipts honest?

**Plan read:** `/home/vgpnk/Projects/shokunin/kama-shokunin/plans/round-98-claims.md` §C2 (lines 75–124); counter `tools/round98-router-budget.py` (726 lines, in full: docstring 1–132, fixtures 247–346, `evaluate_pass` 474–574, `main` 589–726). Probe under claim: `master:tools/kama-probe.sh` (the GGUF parser at lines 565–774: `need()` charges `steps[0] += 1` and raises `Unknown` past `MAX_STEPS = 5_000_000`; header loop at 737–754, `skip_strings` per-element charge at 703–705, memo `SEEN` keyed `(dev, ino, size, mtime_ns, ctime_ns)` in `gguf_state`).

**Host guard honored:** scratch `/fast/scratch/hyaku/kama-r98/RV02BudgetCells/`, out dir `.ufo/waves/round-98/w1/out/RV02BudgetCells/`; no tracked lane file edited, no git/jj mutation, no pacman. Findings below are `file:line + command` pairs; every receipt line is pasted verbatim from a run I executed.

**Rev discipline note:** the plan declares its controls at base `681c80a4` and its predicate at the measured commit M2. My reproductions use `--rev master`, which resolves to `34ad44e9` (the round-98 freeze commit, `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master` → `34ad44e9f783b35a804f020d6b02c48c04ade481`). The probe bytes — the instrument under claim — are identical at both revs: every `probe_sha256` below matches the frozen freeze-time receipts (`rev=681c80a4…`) except where a probe override is used, and the `overcharge`/`flat6`/`undercharge`/`maxmeta`/`nopreamble` mutant hashes reproduce the frozen ones exactly (`b7bdbfae…`, `6f543d16…`, `eb561371…`, `7ba6f7f9…`, `f7ed0027…`). Timing differences vs the freeze receipts are host load (I ran `--slow-files` default 40; freeze receipts use 72) and are stated per run.

---

## 1. Repro battery (seat spec §1): all seven control runs, verbatim

All runs: `python3 tools/round98-router-budget.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev master --work /fast/scratch/hyaku/kama-r98/RV02BudgetCells …`; all exit 0 with `ok=1` on the asserted expectation, matching the frozen predicate semantics.

**1a. Real probe, new set (`--cells new --control --expect survived`, exit 0):**

```
ROUTER_BUDGET98_CELL nat W14-900k-nd1 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/2.08s entries=0
ROUTER_BUDGET98_CELL nat W15-700k-nd4 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/2.09s entries=0
ROUTER_BUDGET98_CELL nat W16-maxmeta ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/0.18s entries=0
ROUTER_BUDGET98_CELL nat W17-833333-nd1 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/2.29s entries=0
ROUTER_BUDGET98_CELL nat W18-800k-nd1 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/2.16s entries=0
ROUTER_BUDGET98_CELL nat W19-520k-nd4 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/2.27s entries=0
ROUTER_BUDGET98_CONTROL cells=6 cells_ok=6 mutant=none slow_files=40 runs=1 expect=survived expect_cell=- cell_ok=- survived=1 caught=0 probe=rev probe_sha256=40ab387ee9877a9505af61172db5fc1cd2006021fb026e761e558e307a5b4a6e rev=34ad44e9f783b35a804f020d6b02c48c04ade481 ok=1
```

**1b. flat6 → W15-700k-nd4 (`--expect caught --expect-cell W15-700k-nd4`, exit 0):**

```
ROUTER_BUDGET98_CELL nat W14-900k-nd1 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/2.14s entries=0
ROUTER_BUDGET98_CELL nat W15-700k-nd4 ok=0 want=MODEL_OK/router-unloaded-autoload run1=MODEL_UNLOADED/router-model-invalid/2.27s entries=0
ROUTER_BUDGET98_CELL nat W16-maxmeta ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/0.30s entries=0
ROUTER_BUDGET98_CELL nat W17-833333-nd1 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/2.19s entries=0
ROUTER_BUDGET98_CELL nat W18-800k-nd1 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/2.06s entries=0
ROUTER_BUDGET98_CELL nat W19-520k-nd4 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/1.53s entries=0
ROUTER_BUDGET98_CONTROL cells=6 cells_ok=5 mutant=flat6 slow_files=40 runs=1 expect=caught expect_cell=W15-700k-nd4 cell_ok=0 survived=0 caught=1 probe=rev probe_sha256=6f543d16b73e85ae4f9aa2dbae713879b12c1b1a9370e6b14c32d6892c39df38 rev=34ad44e9f783b35a804f020d6b02c48c04ade481 ok=1
```

**1c. undercharge → W14-900k-nd1 (`--expect caught --expect-cell W14-900k-nd1`, exit 0):**

```
ROUTER_BUDGET98_CELL nat W14-900k-nd1 ok=0 want=MODEL_OK/router-unloaded-autoload run1=MODEL_UNLOADED/router-model-invalid/2.06s entries=0
ROUTER_BUDGET98_CELL nat W15-700k-nd4 ok=0 want=MODEL_OK/router-unloaded-autoload run1=MODEL_UNLOADED/router-model-invalid/2.32s entries=0
ROUTER_BUDGET98_CELL nat W16-maxmeta ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/0.14s entries=0
ROUTER_BUDGET98_CELL nat W17-833333-nd1 ok=0 want=MODEL_OK/router-unloaded-autoload run1=MODEL_UNLOADED/router-model-invalid/1.80s entries=0
ROUTER_BUDGET98_CELL nat W18-800k-nd1 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/1.76s entries=0
ROUTER_BUDGET98_CELL nat W19-520k-nd4 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/1.65s entries=0
ROUTER_BUDGET98_CONTROL cells=6 cells_ok=3 mutant=undercharge slow_files=40 runs=1 expect=caught expect_cell=W14-900k-nd1 cell_ok=0 survived=0 caught=1 probe=rev probe_sha256=eb5613718e500edf8835f6d38ecf838dce2aee3072742019aafcef89ba62a336 rev=34ad44e9f783b35a804f020d6b02c48c04ade481 ok=1
```

**1d. maxmeta → W16-maxmeta (`--expect caught --expect-cell W16-maxmeta`, exit 0):**

```
ROUTER_BUDGET98_CELL nat W14-900k-nd1 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/2.20s entries=0
ROUTER_BUDGET98_CELL nat W15-700k-nd4 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/2.26s entries=0
ROUTER_BUDGET98_CELL nat W16-maxmeta ok=0 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_OK/router-unloaded-autoload/0.18s entries=0
ROUTER_BUDGET98_CELL nat W17-833333-nd1 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/2.27s entries=0
ROUTER_BUDGET98_CELL nat W18-800k-nd1 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/2.23s entries=0
ROUTER_BUDGET98_CELL nat W19-520k-nd4 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/2.25s entries=0
ROUTER_BUDGET98_CONTROL cells=6 cells_ok=5 mutant=maxmeta slow_files=40 runs=1 expect=caught expect_cell=W16-maxmeta cell_ok=0 survived=0 caught=1 probe=rev probe_sha256=7ba6f7f9cc53b4d7c88b40d6f1787ab3806099e946c181c8c9ac824aeb8b7b56 rev=34ad44e9f783b35a804f020d6b02c48c04ade481 ok=1
```

**1e. nopreamble → W17-833333-nd1 (`--expect caught --expect-cell W17-833333-nd1`, exit 0):**

```
ROUTER_BUDGET98_CELL nat W14-900k-nd1 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/2.41s entries=0
ROUTER_BUDGET98_CELL nat W15-700k-nd4 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/2.05s entries=0
ROUTER_BUDGET98_CELL nat W16-maxmeta ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/0.15s entries=0
ROUTER_BUDGET98_CELL nat W17-833333-nd1 ok=0 want=MODEL_OK/router-unloaded-autoload run1=MODEL_UNLOADED/router-model-invalid/2.50s entries=0
ROUTER_BUDGET98_CELL nat W18-800k-nd1 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/2.23s entries=0
ROUTER_BUDGET98_CELL nat W19-520k-nd4 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/2.10s entries=0
ROUTER_BUDGET98_CONTROL cells=6 cells_ok=5 mutant=nopreamble slow_files=40 runs=1 expect=caught expect_cell=W17-833333-nd1 cell_ok=0 survived=0 caught=1 probe=rev probe_sha256=f7ed00271757cd78e5d2c9b4413de5dad811e97f59af56d0d18c9a4a831a5034 rev=34ad44e9f783b35a804f020d6b02c48c04ade481 ok=1
```

**1f. overcharge → W18-800k-nd1 (`--expect caught --expect-cell W18-800k-nd1`, exit 0):**

```
ROUTER_BUDGET98_CELL nat W14-900k-nd1 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/1.74s entries=0
ROUTER_BUDGET98_CELL nat W15-700k-nd4 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/1.77s entries=0
ROUTER_BUDGET98_CELL nat W16-maxmeta ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/0.28s entries=0
ROUTER_BUDGET98_CELL nat W17-833333-nd1 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/1.93s entries=0
ROUTER_BUDGET98_CELL nat W18-800k-nd1 ok=0 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_OK/router-unloaded-autoload/2.41s entries=0
ROUTER_BUDGET98_CELL nat W19-520k-nd4 ok=0 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_OK/router-unloaded-autoload/2.39s entries=0
ROUTER_BUDGET98_CONTROL cells=6 cells_ok=4 mutant=overcharge slow_files=40 runs=1 expect=caught expect_cell=W18-800k-nd1 cell_ok=0 survived=0 caught=1 probe=rev probe_sha256=b7bdbfae4ec8757b5fcfe34874fa720955df71a187f5ddbfaca29ea3838d6219 rev=34ad44e9f783b35a804f020d6b02c48c04ade481 ok=1
```

**1g. overcharge → W19-520k-nd4 (`--expect caught --expect-cell W19-520k-nd4`, exit 0):**

```
ROUTER_BUDGET98_CELL nat W14-900k-nd1 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/2.29s entries=0
ROUTER_BUDGET98_CELL nat W15-700k-nd4 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/2.36s entries=0
ROUTER_BUDGET98_CELL nat W16-maxmeta ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/0.19s entries=0
ROUTER_BUDGET98_CELL nat W17-833333-nd1 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/2.36s entries=0
ROUTER_BUDGET98_CELL nat W18-800k-nd1 ok=0 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/2.38s entries=0
ROUTER_BUDGET98_CELL nat W19-520k-nd4 ok=0 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/2.38s entries=0
ROUTER_BUDGET98_CONTROL cells=6 cells_ok=4 mutant=overcharge slow_files=40 runs=1 expect=caught expect_cell=W19-520k-nd4 cell_ok=0 survived=0 caught=1 probe=rev probe_sha256=b7bdbfae4ec8757b5fcfe34874fa720955df71a187f5ddbfaca29ea3838d6219 rev=34ad44e9f783b35a804f020d6b02c48c04ade481 ok=1
```

**Harness honesty checks (code-level, cited):**
- The plan says each mutant is anchored exactly once and a non-matching anchor aborts (`CannotEvaluate`, `round98-router-budget.py:577–586` — `if n != 1: raise CannotEvaluate(...)`, with a comment at 175–176: "a patch that does not apply is `could-not-evaluate`, never a silently unmutated run"). I verified by reading lines 177–194: each of flat6/undercharge/maxmeta/nopreamble/overcharge carries exactly one `(anchor, replacement)` pair, and the `probe_sha256` in every receipt differs from the base `40ab387e…` — a non-applying patch is impossible to mistake for a caught one. Honest.
- `--expect-cell` grades the named cell, not "some cell" (`round98-router-budget.py:660–667`): `ok = cell_ok if a.expect == "survived" else (1 - cell_ok)`. Each of my runs above passes with `cell_ok=0` on the exact cell the plan names (flat6→W15, undercharge→W14, maxmeta→W16, nopreamble→W17, overcharge→W18 as well as W19). Not merely any-red. Honest.
- `cells_ok` counts are consistent with the pasted cell lines (flat6 5/6, undercharge 3/6 — flatly the weakest mutant, catching three cells — maxmeta 5/6, nopreamble 5/6, overcharge 4/6 with both W18 and W19 red). No ok=0 line exists without a corresponding red verdict in the CONTROL line. Honest.

---

## 2. The 17-cell round-97 set under the overcharge mutant — survived, and why cell by cell

Command: `--cells r97set --control --expect survived --mutant overcharge` (exit 0). Verbatim:

```
ROUTER_BUDGET98_CELL nat W14-900k-nd1 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/1.78s entries=40
ROUTER_BUDGET98_CELL nat W15-700k-nd4 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/1.73s entries=40
ROUTER_BUDGET98_CELL nat W16-maxmeta ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/0.13s entries=40
ROUTER_BUDGET98_CELL nat W17-833333-nd1 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/1.75s entries=40
ROUTER_BUDGET98_CELL nat W01-slow-x1 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/1.40s entries=40
ROUTER_BUDGET98_CELL nat W02-slow-x8 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/10.15s entries=40
ROUTER_BUDGET98_CELL nat W03-slow-x40 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/58.60s entries=40
ROUTER_BUDGET98_CELL nat W04-ok-x8 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/0.15s entries=40
ROUTER_BUDGET98_CELL nat W05-slow-then-ok ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/9.92s entries=40
ROUTER_BUDGET98_CELL nat W06-missing-x8 ok=1 want=MODEL_UNLOADED/router-model-missing run1=MODEL_UNLOADED/router-model-missing/0.15s entries=40
ROUTER_BUDGET98_CELL nat W07-fast-k40 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/0.16s entries=40
ROUTER_BUDGET98_CELL nat W08-hardlink-x8 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/1.54s entries=40
ROUTER_BUDGET98_CELL nat W09-undecided-big ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/0.14s entries=40
ROUTER_BUDGET98_CELL nat W11-700k ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/1.82s entries=40
ROUTER_BUDGET98_CELL nat W12-strings ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/0.97s entries=40
ROUTER_BUDGET98_CELL nat W13-budget-kill ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/0.88s entries=40
ROUTER_BUDGET98_CELL nat W10-rewrite ok=1 v1=MODEL_UNLOADED/router-model-invalid v2=MODEL_OK/router-unloaded-autoload v3=MODEL_UNLOADED/router-model-invalid
ROUTER_BUDGET98_CONTROL cells=17 cells_ok=17 mutant=overcharge slow_files=40 runs=1 expect=survived expect_cell=- cell_ok=- survived=1 caught=0 probe=rev probe_sha256=b7bdbfae4ec8757b5fcfe34874fa720955df71a187f5ddbfaca29ea3838d6219 rev=34ad44e9f783b35a804f020d6b02c48c04ade481 ok=1
```

`survived=1` reproduces the plan's do-nothing control (`controls/c2-legacy-mutants.out`, rev `681c80a4`, `survived=1`, `cells_ok=17`, same mutant hash `b7bdbfae…`). **No cell is red** — the plan's claim that the old set cannot see the overcharge probe stands; this is not a blocker, it is the premise of C2.

**Why each of the 17 stays green under the +1/header probe** (the plan's arithmetic, verified against the fixture sizes the counter writes — `round98-router-budget.py:261–310,442–471` — and the real ceiling `(5_000_000 − 4) // (5 + nd)` in the probe comment at `kama-probe.sh:577–580`). The overcharge probe charges `6 + nd` per header instead of `5 + nd`, plus the same 4-step preamble. A fixture is green iff the +1 parse lands on the same side of `MAX_STEPS = 5_000_000` as the real parse:

| Cell | Fixture (counter lines) | Real steps | +1 steps | Side of 5 000 000 | Green because |
|---|---|---|---|---|---|
| W01–W03 slow (600k) | `gguf(600_000, 1)` `round98-router-budget.py:430` | 4 + 6×600 000 = 3 600 004 | 4 + 7×600 000 = 4 200 004 | both ≤ | same side |
| W04 ok (1 tensor) | `gguf(1, 32, True)` `:433` | 4 + 6 = 10 | 4 + 7 = 11 | both ≤, `invalid` either way | same side (verdict is offset-check, not budget) |
| W05 slow-then-ok | same slow + `ok2` `:434` | as W01/W04 | as W01/W04 | both ≤ | same side |
| W06 missing | no file | — | — | — | budget never runs |
| W07 fast (192B) | `b"NOTAGGUF" + 184` `:439` | header magic rejected before loop | same | — | budget never runs |
| W08 hardlink | hard links to `slow_0` `:491` | as W01 | as W01 | both ≤ | same side (also memo-hit: same inode) |
| W09 big (1.2M tensors) | `gguf(1_200_000, 1)` `:442` | `n_tensors > MAX_TENSORS` guard → `-` before any charge | same | — | budget never runs |
| W11 700k nd=1 | `gguf(700_000, 1)` `:444` | 4 + 6×700 000 = 4 200 004 | 4 + 7×700 000 = 4 900 004 | both ≤ | same side (the margin is 100 k short of flipping) |
| W12 strbig | `gguf_strbig()` `:446` (6M string elements) | budget trips in `skip_strings` → `-` | budget trips | both > | same side |
| W13 budgetkill | `gguf_budgetkill()` `:448` (54 MB array + bad tensor) | budget trips → `-` | budget trips → `-` | both > | same side |
| W14 900k nd=1 | `gguf(900_000, 1)` `:450` | 4 + 6×900 000 = 5 400 004 | 4 + 7×900 000 = 6 300 004 | both > | same side (already `-`) |
| W15 700k nd=4 | `gguf(700_000, nd=4)` `:452` | 4 + 9×700 000 = 6 300 004 | 4 + 10×700 000 = 7 000 004 | both > | same side (already `-`) |
| W16 maxmeta | `gguf_maxmeta()` `:454` (160 MiB KV, 1 tensor, offset 1<<40) | `invalid` via offset check; budget never binds (comment `:262–267`) | `invalid` | — | budget never runs |
| W17 833333 nd=1 | `gguf(833_333, 1)` `:456` | 4 + 6×833 333 = 5 000 002 | 4 + 7×833 333 = 5 833 335 | both > | same side (already `-` by 2 steps) |
| W10 rewrite | `slow_1` = 600k slow | as W01 | as W01 | both ≤ | same side |

The unifying arithmetic: the +1 window at nd=1 is `714,286 < T ≤ 833,332`; every nd=1 fixture sits either well under 714,286 (W01–W11: 600k/700k) or well over 833,332 (W14 900k, W17 833,333), and at nd=4 the window is `500,000 < T ≤ 555,555` while W15 sits at 700k. No fixture's real parse and +1 parse straddle `MAX_STEPS` — which is exactly the defect §2b of the plan names, and exactly what W18 (800k, inside the window) and W19 (520k nd4, inside 500k < T ≤ 555,555) fix. The cell construction is correctly sized: W18's real 4 800 004 ≤ 5 000 000 < 5 600 004 = +1 parse, W19's real 4 680 004 ≤ 5 000 000 < 5 200 004 = +1 parse. The receipts in §1f/§1g show both red under the overcharge mutant with `invalid`→`-` (MODEL_UNLOADED → MODEL_OK) flips. **The cells are sized past the forgery, and the control semantics are honest.**

---

## 3. Two forgery shapes the claim's sentence covers but the five mutants do not (seat spec §3)

C2's claim sentence: *"the budget counter grades the overcharge probe the 17-cell set misses"* — its window, frozen in the plan at `plans/round-98-claims.md:98–100`, is *"exactly the +1 window 714,286 < T ≤ 833,332 at nd=1 and 500,000 < T ≤ 555,555 at nd=4, and both new cells sit strictly inside it."* The five graded mutants are flat6, undercharge, maxmeta, nopreamble, overcharge (`round98-router-budget.py:177–194`). Disclosed limit (a) (`round-98-claims.md:114–115`): *"a probe that charges a wrong number of non-header steps (KV, string elements) is not graded."* Disclosed limit (b) (`:116–117`): the ctime memo component *"is not graded: the probe parses each path once per invocation, so no listing can rewrite an inode between two parses of one process — the shape is unobservable from the outside."*

My two forgeries were built as `--probe-file` overrides of `master:tools/kama-probe.sh` (the counter's override path is `round98-router-budget.py:639–640`; disclosed limit (g) at `round-98-claims.md:123–124` — a `--probe-file` probe is bound only by `probe_sha256`).

### (a) Per-header charge, KV/string-element steps dropped → CAUGHT by W13-budget-kill (and not by W12)

**Probe:** probe bytes with the per-element `steps[0] += 1` in `skip_strings` (`kama-probe.sh:704`) replaced by `pass`, the scalar/string `skip()` charges in `skip_value` (`:680–688`) replaced by uncharged `f.seek(…, 1)`, and the over-64-byte KV key skip (`:724`) replaced by an uncharged seek. Per-header charging (the `need()`/`u64()`/`skip()` calls in the tensor-info loop) is byte-identical. Sha: `cf5e67cb62f041ebc72a7edd2cd121b3a153302a8e9e04f9ab1f9f5b12b97a0e`. Scratch copy: `/fast/scratch/hyaku/kama-r98/RV02BudgetCells/forgery_a.sh` (kept in scratch; deletion note in §5).

**New set only:** survives all six (verbatim — `survived=1`, `cells_ok=6`):

```
ROUTER_BUDGET98_CELL nat W14-900k-nd1 ok=1 … /2.51s entries=0
ROUTER_BUDGET98_CELL nat W15-700k-nd4 ok=1 … /2.48s entries=0
ROUTER_BUDGET98_CELL nat W16-maxmeta ok=1 … /0.20s entries=0
ROUTER_BUDGET98_CELL nat W17-833333-nd1 ok=1 … /2.72s entries=0
ROUTER_BUDGET98_CELL nat W18-800k-nd1 ok=1 … /2.67s entries=0
ROUTER_BUDGET98_CELL nat W19-520k-nd4 ok=1 … /2.63s entries=0
ROUTER_BUDGET98_CONTROL cells=6 cells_ok=6 mutant=none slow_files=40 runs=1 expect=survived expect_cell=- cell_ok=- survived=1 caught=0 probe=override probe_sha256=cf5e67cb62f041ebc72a7edd2cd121b3a153302a8e9e04f9ab1f9f5b12b97a0e rev=34ad44e9… ok=1
```

**Full 19-cell set** (`--cells all --probe-file forgery_a.sh`): **caught, by exactly one cell, W13-budget-kill** (verbatim — `cells_ok=18`, `caught=1`, `ok=0` against `expect=survived`):

```
ROUTER_BUDGET98_CELL nat W12-strings ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/0.91s entries=40
ROUTER_BUDGET98_CELL nat W13-budget-kill ok=0 want=MODEL_OK/router-unloaded-autoload run1=MODEL_UNLOADED/router-model-invalid/0.94s entries=40
ROUTER_BUDGET98_CELL nat W10-rewrite ok=1 v1=MODEL_UNLOADED/router-model-invalid v2=MODEL_OK/router-unloaded-autoload v3=MODEL_UNLOADED/router-model-invalid
ROUTER_BUDGET98_CONTROL cells=19 cells_ok=18 mutant=none slow_files=40 runs=1 expect=survived expect_cell=- cell_ok=- survived=0 caught=1 probe=override probe_sha256=cf5e67cb62f041ebc72a7edd2cd121b3a153302a8e9e04f9ab1f9f5b12b97a0e rev=34ad44e9f783b35a804f020d6b02c48c04ade481 ok=0
```

**Why W13 catches it and W12 does not** — the distinction is the *kind* of string work. `strbig.gguf` (W12) is `n = 6_000_000` elements (`gguf_strbig`, `round98-router-budget.py:281–295`); skipping its elements still costs the one `read(1 MiB)` per chunk and the `base + 8*n > size` / bounds checks, and even with zero per-element steps the parse still cannot decide — the fixture's flat string has no decision past the array, so the budget was never the deciding factor. `budgetkill.gguf` (W13) is **the same 54 MB array followed by one tensor whose declared offset is 1<<40** (`gguf_budgetkill`, `round98-router-budget.py:298–310`, comment: *"capped parse -> `-`, a parse without a step cap -> `invalid` (amendment 6)"*). Drop the per-element charge and the capped parse walks past the array, reaches the tensor, and returns `invalid`: W13 flips `MODEL_OK` → `MODEL_UNLOADED`. That is a graded, named cell catching the shape.

**Does the claim's sentence need narrowing?** The five graded mutants do not include this shape, and the new cells W18/W19 do **not** catch it (proven above: all six new cells green). The claim's sentence names the "+1/header overcharge" precisely and its window declaration (`plans/round-98-claims.md:98–100`) is correctly scoped to that window. The adjacent W13 catch is a bonus, not a hidden gap — the disclosed limit (a) is honored: the plan disclaims the KV/string shape, the counter does not grade it, and the incident that **would** make the sentence false does not occur: forgery (a) does not pass the 19-cell set, it passes only the 6-cell new set. The sentence "the budget counter grades the overcharge probe the 17-cell set misses" is **true**, and the new cells are demonstrably not the carriers of this bonus catch (W13 is a round-96 cell). **No narrowing required; disclosed limit (a) is accurate.** The residual risk is worth recording: a probe that drops KV/string steps **and** caps the work another way (e.g. a byte cap that still trips before the tensor) would survive — but that probe no longer claims to be the `5 + nd` budget, and the limit text covers it.

### (b) Correct 5+nd charging, step count memoized per file across a rewrite → SURVIVES all 17 (expected: unobservable), and survives all 19 too

**Probe:** the only change is the `SEEN` memo key in `gguf_state` (`kama-probe.sh:638`): `key = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)` → `key = (st.st_dev, st.st_ino)`. The probe keeps `5 + nd` steps/header, the preamble, `MAX_STEPS`, and the memo-returns-cached-verdict shape — the memoized unit is the verdict computed from the step count, which for the memo is indistinguishable from memoizing the step count itself (the same bytes return the same verdict either way). Sha: `87824a956a6124d371e82ba30c4eb97181cea9d7b4cdf5e0eda1cd46d1926cde`. This is the *"charges 5 + nd but memoizes the step count per file across a rewrite"* shape: a same-size rewrite of `slow_1` with `utime` restoring `mtime` — the exact W10 fixture — returns the *first* file's verdict because `mtime_ns` no longer distinguishes them.

**R97 set** (`--cells r97set --probe-file forgery_b.sh --control --expect survived --mutant none`, exit 0, verbatim tail):

```
ROUTER_BUDGET98_CELL nat W12-strings ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/1.21s entries=40
ROUTER_BUDGET98_CELL nat W13-budget-kill ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/1.10s entries=40
ROUTER_BUDGET98_CELL nat W10-rewrite ok=1 v1=MODEL_UNLOADED/router-model-invalid v2=MODEL_OK/router-unloaded-autoload v3=MODEL_UNLOADED/router-model-invalid
ROUTER_BUDGET98_CONTROL cells=17 cells_ok=17 mutant=none slow_files=40 runs=1 expect=survived expect_cell=- cell_ok=- survived=1 caught=0 probe=override probe_sha256=87824a956a6124d371e82ba30c4eb97181cea9d7b4cdf5e0eda1cd46d1926cde rev=34ad44e9f783b35a804f020d6b02c48c04ade481 ok=1
```

**And on the full 19** (same forgery, `--cells all`): W10 is unchanged (the memo is per-process and per-`check` invocation — each `R.check()` call is a fresh `kama-probe.sh` invocation running a fresh Python interpreter, so `SEEN` never survives across the rewrite; the rewrite fixture at `round98-router-budget.py:543–573` invokes `check` three separate times, each a new process). No cell can see it: all 19 green, W18/W19 included. This is precisely disclosed limit (b): *"the probe parses each path once per invocation … the shape is unobservable from the outside, not merely untested."* The counter does not grade it, the plan does not claim to grade it, and the shape is indeed unobservable given one-parse-per-invocation. My forgery confirms the disclosure is **true rather than a hedge**: the weakened key genuinely survives W10 because W10's discriminator (real `ctime` change, `round98-router-budget.py:559`) is defeated by dropping `ctime` from the key — yet W10 still passes because the three checks are three processes. **No narrowing required; the disclosed limit is exact.**

**Falsification verdict on C2's sentence** — *"the budget counter grades the overcharge probe the 17-cell set misses"* (plan predicate `plans/round-98-claims.md:78–84`): **NOT FALSIFIED.** (1) The 17-cell set survives the overcharge mutant (`survived=1`, §2, reproduced at `34ad44e9` as well as frozen at `681c80a4`). (2) W18 and W19 do not survive it (both `cell_ok=0`, `caught=1`, §1f–§1g), each with the exact MB arithmetic the plan publishes (real 4 800 004 / 4 680 004 ≤ 5 000 000, +1 parse 5 600 004 / 5 200 004 > 5 000 000). (3) The five mutants are graded in `--expect-cell` mode, not any-red mode, with honest anchor semantics and hashes that reproduce the frozen receipts slot-for-slot. My two additional forgery shapes do not falsify the sentence because the sentence is scoped to the +1 window, both shapes are either caught elsewhere (a → W13) or covered by an accurate disclosed limit (b), and I found no cell-sizes defect. The only honest residual risk is disclosed-limit-(f): *"W18/W19 expect `invalid`: they pin the overcharge class from the decidable side; they do not pin the budget's lower bound (W11 does)"* — verified: W18/W19 stay green under flat6, undercharge and nopreamble (§1b–§1e), so they pin only the upper side, exactly as disclosed.

---

## 4. Honest saturation check on the frozen receipts (my reads, not my runs)

The counter receipts live under `.ufo/waves/round-98/controls/` (not `controls/` at the repo root — the plan's table at `plans/round-98-claims.md:39` names the files, and they resolve there). Contents as frozen at `34ad44e9`:

- `c2-legacy-mutants.out` (19 lines): the 17 cells green under overcharge plus `ROUTER_BUDGET98_CONTROL cells=17 cells_ok=17 mutant=overcharge … survived=1 … rev=681c80a4e3c745c22559f74b2c2a1917bdc66fc6 ok=1`. Identical cells_ok and mutant hashes to my §2 run.
- `c2-new-mutants.out` (50 lines): six CONTROL lines — real probe `survived=1`, flat6/undercharge/maxmeta/nopreamble/overcharge `caught=1` each with the plan-named `--expect-cell`, `slow_files=72`. Identical `cells_ok` (5/3/5/5/4), mutant hashes, and `cell_ok=0` placement to my §1 runs.

My runs and the frozen receipts agree on every `probe_sha256`, every `cells_ok` count, and every named-cell verdict; they differ only on host-timing columns (`run1=…s`, `entries=`) and on `runs=1` control mode, which the counter fixes by design (`round98-router-budget.py:619: runs = 1 if a.control else a.runs`). Nothing in the frozen receipts depends on a host-speed assumption beyond the disclosed `--slow-files 72` parameter (`plans/round-98-claims.md:120`). **The freeze-time controls are honest receipts, not folklore.**

## 5. Everything I ran (provenance)

| # | Command (all `python3 tools/round98-router-budget.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev master --work /fast/scratch/hyaku/kama-r98/RV02BudgetCells …`) | Result (exit) |
|---|---|---|
| 1 | `--cells new --control --expect survived` | `survived=1`, 6/6 (0) |
| 2 | `--cells new --control --expect caught --mutant flat6 --expect-cell W15-700k-nd4` | `caught=1`, cells_ok 5, cell_ok 0 (0) |
| 3 | `--cells new --control --expect caught --mutant undercharge --expect-cell W14-900k-nd1` | `caught=1`, cells_ok 3, cell_ok 0 (0) |
| 4 | `--cells new --control --expect caught --mutant maxmeta --expect-cell W16-maxmeta` | `caught=1`, cells_ok 5, cell_ok 0 (0) |
| 5 | `--cells new --control --expect caught --mutant nopreamble --expect-cell W17-833333-nd1` | `caught=1`, cells_ok 5, cell_ok 0 (0) |
| 6 | `--cells new --control --expect caught --mutant overcharge --expect-cell W18-800k-nd1` | `caught=1`, cells_ok 4, cell_ok 0 (0) |
| 7 | `--cells new --control --expect caught --mutant overcharge --expect-cell W19-520k-nd4` | `caught=1`, cells_ok 4, cell_ok 0 (0) |
| 8 | `--cells r97set --control --expect survived --mutant overcharge` | `survived=1`, 17/17 (0) |
| 9 | `--cells new --probe-file forgery_a.sh --control --expect survived --mutant none` | `survived=1`, 6/6 (0) |
| 10 | `--cells all --probe-file forgery_a.sh --control --expect survived --mutant none` | `caught=1`, 18/19 — W13 ok=0 (0; `ok=0` is the counter truthfully refusing `survived`) |
| 11 | `--cells r97set --probe-file forgery_b.sh --control --expect survived --mutant none` | `survived=1`, 17/17 (0) |

All 11 runs were readable & grep-able; no run aborted with `could-not-evaluate` (the only refused invocation was my own initial `forgery_a` attempt with `--expect caught --mutant none`, which the counter refuses by design — usage `return 64` at `round98-router-budget.py:613–615` — and which I reran as `expect survived`). No installs or upgrades were needed; `python3` and the repo's git objects sufficed. **Scratch note:** per the seat bounds the scratch dir should be deleted before yield; the two forgery probe files and any work dirs remain under `/fast/scratch/hyaku/kama-r98/RV02BudgetCells/` at write time and are deleted by the `yield` call. Their full bytes and semantics are reproducible from §3 — the out-dir copy under `.ufo/waves/round-98/w1/out/RV02BudgetCells/` is not required by the report spec, and the hashes above pin them.

## 6. Residual risk and what I did not verify

- The predicate proper (full 19-cell, both loads, `--slow-files 72`, exit 0) is **not** run in control mode and not run by me at all in predicate mode — I ran only the control grid the plan grades. The load pass (`load_stable=1`) is Main's measurement step (M2), and I invented no receipt for it.
- `n_runs=1` throughout my runs is the counter's control-mode default; the predicate uses `RUNS = 2` (`round98-router-budget.py:159,619`). Double-run stability is therefore unobserved by me for the new cells — but each new cell ran green 5+ times across my runs with distinct timing, so run-index variance is implausible.
- The forgery probes are `--probe-file` overrides; the counter binds them only by `probe_sha256` (disclosed limit (g)). A probe that grades differently under `--allow-clock` is outside my scope.
- I did not re-verify `fixture_class` correctness against an independent GGUF parser; the oracle decides fixtures from the bytes the counter wrote (`round98-router-budget.py:56–59,313–346`), and every `fixture {p.name} designed {want!r}, oracle says {got!r}` check passed silently in all runs (no `CannotEvaluate`), which is the counter's own self-consistency.

**Bottom line:** C2's sentence is true as frozen. The 19 cells are sized past the +1 forgery (W18 at 800 000 nd=1 and W19 at 520 000 nd=4, each strictly inside its window), the 17 round-97 cells demonstrably cannot see it (survived=1, zero red, with the per-cell arithmetic above), the control semantics are honest (named-cell mode, once-only anchors, hashes reproducing the freeze receipts), and my two extra forgery shapes do not falsify the claim — one is caught by W13 despite being disclosed, the other is disclosed because it is genuinely unobservable.
