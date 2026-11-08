# Round 95 — amendment 4 (C1 filed on the narrowed property; instrument gaps routed)

Date: 2026-11-08. Author: L1 `KamaR95`. Frozen plan `c798e831`; amendments 1 (`719214fa`, `bba10f75`), 2
(`7db1c54a`), 3 (`ed3bd05f`, `a9b5014c`). This is the file the closure reads for C1: the plan's sentence was
falsified by four of the round's own attack seats, and the claim below is what survives.

## Falsified wording

The plan's C1 sentence — "the router file-state verdict is a function of the file's bytes" — and the disclosures
that leaned on it:

- `w1/RV01ProbeDiff.md` (**falsified**): in the first revision (`f6325660`) the pass wrapper decided the verdict
  (`timeout 35` on a 49M-element KV file → `MODEL_OK` in 2/4 runs at load1 155–158), `MAX_STEPS` did not price
  string-array work (766 014 steps for 8 s CPU), and `ncand`-priced allowance reproduced a base-green/new-red
  regression. Repaired at `c810f51e`.
- `w1/SC01HeldOutListings.md` (**falsified**): "the verdict is a function of the bytes" does not hold — the
  pass-level wrapper is still a wall clock.
- `w1/CR01BudgetCounter.md` (**falsified**, five BLOCKERs): W10 cannot observe the memo key it claims to grade (each
  `check` is a fresh process); no cell reaches a header above `MAX_META`; no cell contains an unreadable file; the
  only valid fixtures have ≤2 tensors; the `DEADLINE` guard passes only because of its value. Plus DEFECT 1
  (`KILL=400` is tighter than the probe's own derived limit), DEFECT 2 (the margin guard is load-dependent and
  swallows the exact round-94 defect), DEFECT 3 (`--skip-load` sets `loaded = natural`, so the summary still prints
  `load_cells=10 load_stable=1 … burners=64` with no second pass — a receipt that misstates what ran).
- `w1/MT01ProbeMutants.md` (**partial**): 7/12 mutants survive the frozen cells; `MAX_STEPS` removed/raised and
  `MAX_META` removed/doubled all print `mismatches=0`, and W10 is green under a ctime-less key. F3 adds that the
  margin guard turns truncating mutants into `could-not-evaluate` (exit 2), not red.

## Filed property (C1, narrowed)

1. **The per-file file-state decision contains no clock.** `tools/kama-probe.sh` at `c810f51e`: no `time` import,
  no `DEADLINE`, no `PER_FILE_SECONDS` in `ROUTER_PY`; the parse is bounded by `MAX_STEPS` (one per string element)
  and `MAX_META`. Verifiable by read (`grep -n 'time\.\|DEADLINE' ` over the extracted `ROUTER_PY` is empty) and by
  the round's own probe-level work (RV01 measured identical states for identical bytes at load1 90–158 after the
  repair).
2. **The pass allowance is derived from the work a listing implies:** `20 + 25 * npaths`, where `npaths` is the
  number of model-path occurrences across the candidate entries (`ROUTER_PY` `count` verb), not a constant and not
  per entry. Verifiable by read (`tools/kama-probe.sh:850-870`) and by the three-distinct-200 MB-path shape that
  regressed in revision 1 and completes after it (RV01's DEFECT-3 reproduction).
3. **Measurement:** at M1b `c810f51e`, `python3 tools/round95-router-budget.py --repo . --rev c810f51e --work
  <scratch>` prints `ROUTER_BUDGET95 cells=10 mismatches=0 positive_mismatches=0 load_cells=10 load_stable=1
  budget=work probe=rev … w03_seconds=99.7 load1_nat=137.85 burners=48` and exits 0 with **both** passes executed
  (`measured/c1-m1b.out`), the counter's bytes identical to the freeze commit.

**Not claimed (disclosed, routed to round 96):** that the verdict is a pure function of the bytes at the *pass*
level (the wrapper is still a wall clock — SC01); that `MAX_STEPS`/`MAX_META` are the operative bounds *as graded by
the counter* (no frozen cell exercises them — MT01 F1, CR01 BLOCKERs 1–5); that the ctime memo key is
regression-covered (W10 cannot see it — MT01 F2); that the margin guard cannot mask a truncating probe (F3/CR01
DEFECT 2); that `--skip-load` receipts carry load evidence (CR01 DEFECT 3 — the base control's `load_cells=10
load_stable=1` in `controls/c1-base.out` is **nominal**, and only its natural-load `W03` mismatch is evidence);
and that a slow `/props` answer does not decide the verdict (round-94 SC02 F4, still reproduced).

## Added after the twelfth seat reported (`w1/SC02LiveRouter.md`)

- **F2 (live confirmation of C1's win).** On a real lane-owned b12177 router with 40 distinct invalid fixtures, the
  round-94 probe graded `MODEL_OK/router-unloaded-autoload` in both repetitions at 60.33 s / 60.43 s (its constant
  `timeout 60` truncating the pass) while the round-95 tip graded `MODEL_UNLOADED/router-model-invalid` at 133.42 s /
  158.35 s inside its derived ceiling, with the router oracle rejecting all 40 files. The stub discriminator is real
  on a live router.
- **F1 (BLOCKER against the tip's disclosed limit as worded).** With per-element charging the tip spends **6 steps
  per tensor header**, so a 700 000-tensor file needs 4.2 M steps > `MAX_STEPS` and its state is `-` (undecidable →
  loadable): the tip graded `MODEL_OK/router-unloaded-autoload` for all 8 fixtures while the router oracle reports
  `failed=true exit_code=1`. The effective tensor ceiling is therefore ≈666 666 tensors, **not** the
  `MAX_TENSORS = 1 000 000` that the plan's disclosed limit (a) named, and the branch that bites first on a live
  listing is graded by no frozen cell (`W09` uses 1 200 000 tensors and exercises the `MAX_TENSORS` branch instead).
  Corrected limit: *a candidate that needs more than `MAX_STEPS` steps — on the round-95 probe that includes a file
  with more than ~666 666 tensor headers — is `-` and therefore loadable.* Routed to round 96 with the cell that
  would grade it (a 700 000-tensor fixture must grade `MODEL_UNLOADED` or the counter must say what it decides).

## Consequence

C1 is filed **verified on the three numbered properties above**, with the plan's wider sentence withdrawn by this
amendment. The round's own wave falsified the wide sentence, repaired one regression in-round, and routed five
instrument gaps; the deliverable is the narrowing plus the repair, and the closure should read C1 against these
three lines only.
