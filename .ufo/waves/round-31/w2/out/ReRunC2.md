# ReRunC2 — scoped findings (advisory evidence, not a verdict)

Full report + receipts: `.ufo/waves/round-31/w2/out/ReRunC2/report.md` (RESULTS
block, verbatim outputs; `c2.json`, `c2-list.json`, `c2-list.stdout.txt`,
`indep.py`, `indep.out` beside it).

- Fresh clone (`git clone --no-hardlinks --no-checkout`, `checkout --detach`) at
  `382d11b2107d335705875da1a4d889b074bd6fa6`; `sha256sum` of
  `.ufo/waves/round-31/count-c2.py` = `2d06f38d5a686b4d7a316c8db67256ff862fa6e922c1603c156341ff9a33c6fe`
  — matches the frozen pin.
- Frozen command run verbatim, exit 0, summary verbatim:
  `rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0 unresolved 3 append_only True met False tip 382d11b2107d`
- Independent re-derivation AGREES with `unresolved 3`:
  (a) 30 claim-table data rows confirmed by an independent walk, file:line each
      (rounds 10–18, 20–22, 25–31; 18 tables; the 2 round-31 rows at
      SCORECARD.md:1581–1582 account for 30 vs the preregistration's 28);
  (b) the three `unresolved` receipt strings are literally `"C1"` — the Claim
      cells of SCORECARD.md:266 (round 11), :320 (round 12), :379 (round 13),
      all class p1, observed `p1:no-revision`; a 4th exact-`C1` row at :1322
      (round 26) resolves normally and is not one of them;
  (c) `append_only` is decided by count-c2.py:155
      `append_only = base_raw is not None and raw.startswith(base_raw)` — the
      tip blob (124857 B) byte-for-byte prefixes the base blob (117789 B);
      appended head is the round-31 section.
- Note for the L1: `unresolved == 0` is structurally unreachable on this tree —
  the `(row, class)` correction key (count-c2.py:257–268) collapses three
  distinct failing rows onto `("C1","p1")`; one correction would resolve all
  three (met True), a second makes both false. `unresolved 3` is the honest
  residue of that defect, consistent with `controls/RefRepair/` (`valid 10
  false 3 unresolved 3` with all 13 corrections appended).
- No lane tracked file edited; no lane git write; no tools installed.
