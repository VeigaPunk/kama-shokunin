# Round 97 — amendment 1 (C2 predicate: the W03 host-speed parameter)

Recorded `2026-11-08` before any C2 cell scored. The frozen C2 predicate
(`plans/round-97-claims.md` §C2) was run verbatim at the freeze commit
`9e605d416c199b3c9913a2125b04f9c5a16f5668`:

    python3 tools/round97-router-budget.py --repo . --rev 9e605d41 --work <private>

It exited **2** (`could-not-evaluate`), not 0/1, with
`W03 natural pass 55.0s < 1.25 x 60s — the round-94 constant wrapper would not truncate this
listing on this host, so no discriminator is claimed` (receipt
`.ufo/waves/round-97/controls/c2-could-not-evaluate.out`). No cell was scored: every natural-pass
cell was `ok=1` and the run stopped at the guard before the load pass, so nothing in C2's claim was
measured.

The guard is round-96's W03 discriminator (does the round-94 constant wrapper truncate the listing?),
`--slow-files` is its declared host-speed parameter (counter docstring `MARGIN_HELP`), and round-96's
receipt measured 161 s on a loaded host where today's host measures 55 s. C2's claim does not rest on
W03: it rests on the four new cells and the mutant controls.

**Amendment:** the C2 predicate command gains the declared host-speed parameter
`--slow-files 72` (72 × ~1.37 s ≈ 99 s, above the 75 s guard on this host). Nothing else changes:
same counter bytes (kill rule K1 unchanged), same 17 cells, same two host loads, same four mutants,
same controls, same target sentence. The guard itself is not widened or bypassed — the cell count is
sized so the discriminator it protects exists on this host.

The frozen sentence, cells, control receipts and kill rules are otherwise exactly as declared.
