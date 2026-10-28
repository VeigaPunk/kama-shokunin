# X06Reconciler - C2 closure pointer (reconciler conjunct `closure_ptr`)

Clone: scratch clone of lane at freeze f6a4ea9a (base tip of the work). No lane file edited. Deliverables in `.ufo/waves/round-64/b/out/X06Reconciler/`.
No tools installed or upgraded.

## What was built (tools/round42-selfdesc-reconcile.py)
- `closure_ptr(repo, tip, cal_row)`: reads the `| calibration |` row of `## Axes` (the same `rowtext` the `rel` fact uses, from the git blob at tip), requires exactly one
  `latest outside closure \`corpus/lessons/round-N-verifier-spotcheck.md\``, N == int-max over `git ls-tree corpus/lessons/` names matching
  `round-N-verifier-spotcheck.md` at the tip (numeric, not lexicographic), and every `including round K` in the row has K == N (the stale `including round 57` clause
  sits in the same sentence; the L1 may drop that sub-check if the frozen predicate is read narrowly - it is isolated in `closure_ptr`).
- Output line now `... rel=0 closure_ptr=1 mismatches=0 maxN=63 met=True`; a false conjunct adds 1 to mismatches and prints `detail: closure_ptr: <why>`.
  `closure_ptr` is a truth flag (1 = pointer right), not a mismatch counter like the other fields.
- `--selftest --repo R --tip T --work W` (W absent/empty): shared clone into W, commits 5 SCORECARD variants in the fixture, scores each with the full evaluator.
  Pass = ok variant `closure_ptr=1 mismatches=0`; each of stale_ptr (pointer round-57, including-clause right), stale_both (row says round-57 everywhere: the assigned case),
  stale_incl (only the `including round` clause stale), no_ptr (pointer removed) gives `closure_ptr=0` and mismatches == ok+1 (>=1).
  Works whether or not the tip row is already corrected (ok variant is committed with --allow-empty; first run failed on that and was fixed).

## Receipts (out/X06Reconciler/)
- before, old tool at f6a4ea9 (blind): `r41=0 ... rel=0 mismatches=0 maxN=63 met=True`  (before-old-tool-base-f6a4ea9.out)
- new tool, stale row at tip (clone commit 8e404c7): `... rel=0 closure_ptr=0 mismatches=1 maxN=63 met=False`, detail `calibration row latest outside closure is round-57; newest at tip is round-63` (before-new-tool-stale-row.out)
- new tool, corrected row (clone tip 0913c70): `... rel=0 closure_ptr=1 mismatches=0 maxN=63 met=True` (after-new-tool-clone-tip.out; also after-tip-corrected-row.out at 347a2ee)
- selftest, clean tool: `SELFDESC_SELFTEST newest=63 planted_stale=57 ok:closure_ptr=1,mismatches=0 stale_ptr:closure_ptr=0,mismatches=1 stale_both:closure_ptr=0,mismatches=1 stale_incl:closure_ptr=0,mismatches=1 no_ptr:closure_ptr=0,mismatches=1 pass=5 fail=0` exit 0
- selftest mutants of the tool (mutants.out), each caught by the selftest (exit 1):
  - M1 pointer compare disabled: KILLED `pass=4 fail=1` (stale_ptr stayed closure_ptr=1)
  - M2 `including round` check disabled: KILLED `pass=4 fail=1` (stale_incl stayed 1)
  - M3 closure_ptr always true: KILLED `pass=1 fail=4`
  - M4 min instead of max: KILLED `pass=0 fail=5`
  - Earlier 4-variant selftest let M1-equivalent survive (stale_ptr also had a stale `including` clause); the 5-variant design fixes this.
- Reconciler flags no clause other than the closure pointer at f6a4ea9 (all other fields 0).

## Patches
- `round42-selfdesc-reconcile.tool.patch` (diff vs f6a4ea9) and the full file `round42-selfdesc-reconcile.py`.
- `scorecard-calibration-closure.patch` (a/ b/ prefixed, `git apply --check` clean at f6a4ea9): one substitution in SCORECARD.md line 18
  `latest outside closure \`corpus/lessons/round-57-verifier-spotcheck.md\` (rejected-honest-stop), including round 57;` ->
  `latest outside closure \`corpus/lessons/round-63-verifier-spotcheck.md\` (rejected-honest-stop), including round 63;` (round-63 verdict rejected-honest-stop per its line 7). `replacement-clause.txt` has the exact text.
  Applied in the clone it keeps all other reconciler fields at 0 (see receipt above).

## Risks / for the L1
- Interface: other callers of `evaluate()` (tools/round63-c2-counter.py, any r64 C2 counter) that unpack 5 values must take the 6th (`closure_ptr`); grep before integrating.
- Row text is edited each round: the next closure (round 64) will make the pointer stale again unless the closing integrator updates the row - the conjunct will then fail, by design.
- Not run: round41/other tools' tests; no live server or full-gate checks (not assigned).

counter output: `closure_ptr=1 mismatches=0 met=True` at clone tip 0913c70d79d8eae2867954d6ac357f9a88cf4430 (corrected row); base blind tool `mismatches=0`, new tool on stale row `closure_ptr=0 mismatches=1`.
