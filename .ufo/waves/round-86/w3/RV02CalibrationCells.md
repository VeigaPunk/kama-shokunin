RV02CalibrationCells — calibration cells, three-claim terminal audit (tip `bafae7afb41843564ac2468d28beb8e0bb98e8e6`).

**Result: two live authority cells verified in both forms; terminal numbers all re-derive. Two
provenance-consistency findings live in the round's own narrative, both already superseded by dated
errata in the round-87 discoverable byte base (`0fec2861` and the following terminal-commit notes;
each surfaces as an appending correction of the round's mined counts/receipt shapes).**

- Two live cell boundary conditions set (9–10 / 24–25):
  - Delivery: ` Duel behaviors required for rendering: a fence opener rendered
    inside the **"fenced code block against correction` blocks"** do not count as a live cell
    boundary; an `unclosed-fence-fails-closed` terminates (exit `2`) a caveat.
  - Terminal calibration condition measures `S576→gate 17/0` on both sides; those exact manual
    pre- and post-verify numbers are also scalars of one correct rendered identity of the boundary
    records named by the 9-10 / 24-25 receipt cells, correctly mirrored from receipt bytes;
    "in each sentence's read, one per round" — corroborated by the docs the two live cells
    bind (`S576` pre-parameter and `S578/S579` post-the-ten-space correction), which the
    count presented as one receipt each. The `RENDERED_CELLS` receipt of that record's anchor is
    ` .ufo/waves/round-86/measured/after/c1.out` at exit 0 and
    ` .ufo/waves/round-86/measured/before/c1.out` at exit 1 — both are bound to the
    base and correct our gate names; the `mutants=10 killed=10 escaped=0` receipts of that
    same record shape (c1-mutants, mutated-source driver) confirm all ten are killed.
    - Two live cell boundary count (consideration of five-ten w1 nuances: the record's number
      `17/0` is the *frozen* instrument's selftest line name (one selftest per cell of the
      three-fact field), the `10/10` the *mutant* driver; both match every receipt.
- Two receipt/commit bindings set: no kill could be isolated from a commit that its tagged byte
  does not contain and that is not itself in the record's commit chain, because each such I ran
  the count (through `-C` over "ONE clone of the lane committed fork shows the tip
  photos committed at the record cited HEAD; no commit's receipt had a dangling tip).
  - `.ufo/waves/round-86/measured/before/c1.out`: matches my own re-run, exit 1, `newest_gate=85
    newest_closure=85`, three-finding footer.
  - `after/c1.out`: matches my re-run exit 0 (`gate=1 closure=1 disposition=1`).
  - `after/c2.out` ends `APPEND_DEBT_SELFTEST pass=34 fail=0 arms=34`; the tip instrument's
    summary line dropped the `arms=` suffix at c5a32443, so this receipt is not producible at its
    tips. THE ROUND KNOWS: the terminal commit `0fec2861` appends a paragraph that names it a
    "Superseded intermediate receipt"; non-fatal — my re-run reproduces terminal c2 byte-for-byte.
  - `after/c3.out` at tip: matches `rows=5 verified=5 mismatch=0 unreachable=0 bad=0`.
- The five pin rows (llama.cpp / b11755, /b7200, `/39febd2a…`, sglang /v0.5.22,
  vLLM /v0.32.0) are two-anchors-each; I independently re-fetched **two** of the ten anchor URLs
  (`llamacpp ↔ b11755 tools/server/README.md` and
  `vllm ↔ v0.32.0 docs/design/prefix_caching.md`), and both upstream slices' byte digests equal
  the corresponding committed body digests. The remaining eight are not re-fetched by me; they are
  re-derived only by the instrument's own 2/2 anchors claim, in line with the record's "row count
  5 × 2 anchors" claim.
- **Provenance finding 1 — M3 count drift** (`corpus/lessons/round-86.md`, line 59):
  at `bafae7af`, "7/7 source mutants are now killed" and "`RENDERED_CELLS_MUTANTS mutants=7
  killed=7 escaped=0`" appear, while the cited receipt
  `.ufo/waves/round-86/measured/after/c1-mutants.out` line 12 says
  `RENDERED_CELLS_MUTANTS mutants=10 killed=10 escaped=0`. The frozen bytes are internally
  inconsistent as committed. Round 87-5 correction (`0fec2861`): a dated erratum was appended to
  the same lesson, naming the receipt as authority and noting the `7/7` shipped before the two
  extra mutants were added. Verdict at `bafae7af` itself: **mismatched, corrected at the
  following round's last byte**; my re-run reproduces `mutants=10 killed=10 escaped=0`, exit 0,
  with one red_arms line per mutant (each exit 1).
- **Provenance finding 2 — terminated C2 after-receipt shape** (`measured/after/c2.out`): the
  `pass=34 fail=0 arms=34` summary that the receipt ends with doesn't reproduce at the tip. The
  correct receipt shape is bound in the round's own erratum text as "superseded intermediate
  receipt". Non-fatal: the terminal receipts — which the record's SCORECARD row 3 and LOG entry
  fully cite — reproduce byte-for-byte.
- **Other succeeded checks** (all `matches`, per-command evidence in the full findings file):
  gate-arm selftest of `pre-report-gate.py` = `PRE_REPORT_SELFTEST pass=35 fail=0` (exit 0, tip);
  the append-debt (`round81-append-debt`) acquisition says it pins `ARMS arms=34 expected=34
  fail_lines=0` — my own run reproduces this in scratch; so if the asserted claim is
  `pass + fail == arms` in the summary, all three clauses hold. The C2's five
  declared mutants (M2/M3/M4/M5/M6) all kill on named owning arms with the right fail-class.
  The static C1 mutant-driver source's four (ten) mutations each map to one declared arm.
- **Log- and SCORECARD-side notes**:
  - SCORECARD row3 claims `selftest 17/0`, `selftest 13/0`, `selftest 7/0`, `mutants=5 killed=5`,
    `arms=34` — all are reproduced at tip / stated against the same receipts I audited.
  - LOG entry's "15 rows in `registry/append-only-late.tsv`" matches the stated total
    (15 new rows; 114→129).
  - I independently re-fetched the specified 2 anchor URLs only; for the remaining 8, the
    pin-origin mutations and the instrument's own 2/2 anchors statement remain bound to the
    record. Everything else (2-2 bindings) re-derives from committed bytes.

For the full command-by-command evidence table, see
`.ufo/waves/round-86/w3/out/RV02CalibrationCells/findings.md`.
