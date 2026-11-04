# Round 86 — frozen claims

Base revision `3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d` (master, clean and pushed at round start;
`jj-lane.sh state` printed `local=3ff23da3 remote=3ff23da3 ahead=0 behind=0 tracked=0 untracked=0`).
Freeze date 2026-11-04. This is a **fresh-start round**: the current three-rejection pause on kama r86
was lifted once (operator "Resume all eight once", run-15 amendment 11), history retained. The last
three rejected closures were read before declaring anything: `corpus/lessons/round-83-verifier-spotcheck.md`
(rejected-harmed: stale live self-assessment cells), `round-84-verifier-spotcheck.md`
(rejected-honest-stop: a frozen auxiliary disclosure instruction was missed and the counter's
two-fact population could not see it), `round-85-verifier-spotcheck.md` (rejected-honest-stop: the
frozen C1 kill rule fired on fenced/comment shadow cells that a raw-line selector accepted as live).

Assigned axes operability 8 / calibration 7 (`shokunin.conf`). Calibration is the lowest assigned
axis, below the saturation line 8; no stagnation waiver. Three claims on three distinct axes, each
causally separable and each measured on its own receipt. No axis score is claimed to move; three
capabilities enter the repertoire.

## C1 — calibration: rendered-cell identity binds the live self-assessment cells

Predicate (frozen verbatim; the same sentence is `tools/round86-rendered-cells.py`'s `PREDICATE`):

> `python3 tools/round86-rendered-cells.py --repo <lane> --rev <rev>` prints one
> `RENDERED_CELLS facts=3 mismatches=<m> gate=<0|1> closure=<0|1> disposition=<0|1> newest_gate=<N> newest_closure=<N>` line and exits 0 only when the rendered (fence- and comment-free, column-0) head authority cell names the newest terminal gate receipt with its revision, command and receipt bytes coupled, the rendered calibration row names the newest committed verifier spotcheck, and that row names its disposition; it exits 1 naming every mismatch as `RENDERED_CELLS_FINDING <fact> <detail>`.

Frozen population — three cells, not a whole-record census:

1. `gate` — the first **top-level, rendered** `**Current authority (round N):**` line must name the
   newest terminal gate receipt committed in the tree, and the claim is one coupled assertion: a
   40-hex revision `R` in the same paragraph, the backticked receipt path, the exact
   `PRE_REPORT round=… arms=… failed=… uncommitted=…` token, `R` an ancestor of the graded revision,
   the receipt's bytes at `R` containing that exact token, and the backticked
   `tools/pre-report-gate.py … --round M` command naming the token's round. This is R85V1's
   "revision/command/receipt as one assertion".
2. `closure` — the first top-level `| calibration |` row inside the first `## Axes` section must name
   the newest committed `corpus/lessons/round-<N>-verifier-spotcheck.md`, resolved by **highest round
   number** (the round-69 counter's date ordering exits 2 on the undated round-10 closure; round
   number is the invariant the row is about).
3. `disposition` — that row must name `round<N> <disposition>` for the newest closure, and the word
   must occur in the closure body.

Rendered-cell selector (the round-85 counter's defect, R85V1): HTML comment blocks, fenced code blocks
(backtick or tilde, CommonMark 0.31.2 §4.4/§4.5), `round-<N> correction` sections and non-column-0
lines are not rendered cells. A correct token that exists only inside a fence, a comment, an indented
code block or a historical correction block is not a live cell.

Before / no-work control (measured before any edit, receipt `.ufo/waves/round-86/measured/before/c1.out`):
`RENDERED_CELLS facts=3 mismatches=3 gate=0 closure=0 disposition=0 newest_gate=85 newest_closure=85`,
exit 1 — the banner names the round-84 gate while round-85's terminal receipt exists, the calibration
row names the round-84 closure while round-85's closure exists, and the row never names round-85's
disposition. A do-nothing tree cannot reach `mismatches=0`.

Controls frozen in the instrument (`--selftest`, 11 arms, receipt
`.ufo/waves/round-86/measured/before/c1-selftest.out`): green; fenced-shadow; comment-shadow;
tilde-fence-shadow; indent-shadow; unclosed-fence (fails closed, exit 2); contradictory-receipt;
missing-receipt; command-round-disagrees; closure-only-stale; no-closure-population (exit 2). The
round-85 false green (`fenced-shadow` with stale live cells) must be red here.

Work: repair the two live cells in place (round-42 convention) and append dated corrections; do not
rewrite filed history. Kill: any remaining mismatch, or any control that stops discriminating.

## C2 — operability: every mutant maps to a declared owning arm and the summary reconciles

Predicate (frozen verbatim; the same sentence is `tools/round86-mutant-owners.py`'s `PREDICATE`):

> `python3 tools/round86-mutant-owners.py --repo <lane> --rev <rev> --work <dir>` prints one `DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5` line and exits 0 only when all five declared mutants of the delivered debt selftest are killed on their declared owning arms, each completed summary reconciles with its arm population and its failure-line cardinality, and the pristine selftest is green.

Frozen population — five named mutations of `tools/round81-append-debt.py` read as committed bytes,
each with one declared owning arm: M2 `deletion != accepting` → `note-deletion-equals-subject`;
M3 `!=` → `<` → `note-deletion-above-subject`; M4 drop the `continue` after
`note-wrong-deletion-round` → `note-subject-exact-summary`; **M5 drop one `cases.append` arm** →
`arm-count`; **M6 forge the summary (`pass=0 fail=0`)** → `summary-cardinality`. M5 and M6 are the
round-85 survivors: the frozen round-85 counter classified a green `pass=33 fail=0` and a forged
`pass=0 fail=0` as legitimate results.

Reconciliation clauses: exactly one summary line and at most one `APPEND_DEBT_SELFTEST_ARMS` line;
`pass + fail == arms`; the ARMS line's `arms == expected`; ARMS `fail_lines == summary fail ==`
the number of `APPEND_DEBT_SELFTEST_FAIL` lines actually printed; empty stderr; no traceback.

Before / no-work control (`.ufo/waves/round-86/measured/before/c2.out`):
`DEBT_MUTANT_OWNERS mutants=5 killed=3 escaped=2 invalid=0 arms=unknown cardinality=ok owners=3/5`,
exit 1 — M5 and M6 escape on the base bytes.

Controls frozen in the instrument (`--selftest`, 10 arms, `.ufo/waves/round-86/measured/before/c2-selftest.out`):
pristine-green, owned-failure, forged-summary, dropped-arm, fail-lines-disagree, two-summaries,
foreign-owner, traceback, exit-two, green-with-fail.

Work: add `EXPECTED_ARMS` and the ARMS line to the debt selftest, assert the declared arm population,
and reconcile the summary against the failure lines; production grading behaviour is unchanged
(the round-85 receipts' three actual kills stay). Kill: any survivor, invalid execution, pristine
regression, or a cardinality clause that a forged summary can satisfy.

## C3 — freshness: pin-recheck rows corroborate against live source bytes, not hash integrity

Predicate (frozen verbatim; the same sentence is `tools/round86-pin-origin.py`'s `PREDICATE`):

> `python3 tools/round86-pin-origin.py --repo <lane> --rev <rev> --rows registry/pin-recheck-rows.tsv` prints one `PIN_ORIGIN rows=5 verified=5 mismatch=0 unreachable=0 bad=0` line and exits 0 only when every row's two committed anchor extracts match the live upstream bytes at their declared ranges; a hash-consistent extract whose bytes differ from upstream is `mismatch`, never `verified`.

This is a **capability acquisition** (AXES §Capabilities): the round-83/84 `holds` verdicts prove two
committed extracts agree with each other; they never prove either was acquired from the named URL
(R84V3/R85V3, still open). The new leg re-reads each anchor header, recomputes the digest over the
stored body, fetches the URL live and compares the stored body with the upstream range byte for byte.

Before / no-work control (`.ufo/waves/round-86/measured/before/c3.out`): the frozen counter refuses
`could-not-evaluate: no tools/round86-pin-origin.py at 3ff23da3…`, exit 2 — a do-nothing tree cannot
print the target line. The old instrument's `PIN_RECHECK … holds=5` line is hash integrity, not origin.

Controls frozen in the instrument (`--selftest`, 7 arms, `.ufo/waves/round-86/measured/before/c3-selftest.out`):
verified; **fabricated-hash-consistent** (must be `mismatch`); digest-lie; malformed-header;
missing-anchor; unreachable; range-outside-upstream.

Work: land the instrument, run it live on this Linux host, retain the receipt, and enter the
capability row. Kill: any mismatch/unreachable/bad row, or a fabricated hash-consistent extract that
grades `verified`.

## Frontier, sources and routed corrections

Run-start census `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`
printed `kama ok …/corpus/SOURCES.md`, exit 0, 317 rows (pre-existing W01/W04 warnings unchanged).
This round re-opens the CommonMark 0.31.2 specification for the fence and comment rules that ground
C1's selector (§4.2 ATX headings, row S576, opened this round; §4.4/§4.5 fenced and indented code, new
row) and appends only the rows the admitted lesson cites. C1 is the sourced claim.

Routed defects disposition: **R85V1** → C1 (rendered-block identity, fenced/comment red controls
retained); **R85V2** → C2 (owning arms, unique summary, cardinality); **R85V3/R84V3** → C3 (origin
corroboration distinct from integrity); **R84V1** stays an honest miss — no fabricated event-loss
disclosure is manufactured; **R84V2** was closed in round 85 (S577 rejected row); **R84V5** receives
an append-only provenance erratum in the round-86 lesson; **R85V4** — the L1 holds the planner seat
(validator rejects a planner role), and the wave results' per-seat status is reported verbatim,
including any empty seat output.

`considerthese/` is operator-authored input: at most one still-unimplemented proposal is mined this
round, grounded through the lane's own bar, and lands as a lesson/QUALITY/SOURCES pointer. The
`corpus-expansion-1` package at `/home/vgpnk/Projects/shokuknow/merge/kama/` is read-only; if no
theme fits the round's claims the report says `Assimilation: none` with the reason.

## Shape and evidence

ONE v1 wave `w1`, 12 seats under `ufo-wave-policy.json` (band 8–16): 3 executor, 2 mutation-tester,
2 reviewer, 1 critic, 1 scout, 1 scribe, 1 connector, 1 sentinel. Attack share 5/12 (42 %), one
connector seat, roles span the run-15 map (executor/reviewer on `@m_zfl`, critic/mutation-tester/
sentinel/executor on `@m_flash`, scout/scribe on `@m_mim`, connector on `@m_antigravity`); the route
table decides, the prompt never passes a model. No planner seat is dispatched — the validator refuses
the role and the L1 holds the canonical §3 planner seat. Every seat writes only its own
`.ufo/waves/round-86/w1/out/<name>/`; the L1 is the sole integrator and the only committer. Scratch
root `/fast/scratch/hyaku/kama-r86/<seat>/`, removed on exit. The wave is dispatched through
`.ufo/waves/round-86/w1.ready` (inline handoff); `task` is never called by the L1.

Freeze order: this plan, the three instruments and the frozen counter are committed **before** any
seat scores anything; the before receipts are committed with them. Final measurements run on
committed master after integration; the publication commits follow. All three claims must verify and
no axis may be harmed; otherwise the round is an honest stop.
