# RV01PlanFreezeReview — kama r87 plan/controls freeze review

Measured at freeze commit **94e8fe7b911a5e6f8d1e1a07bff110d3ff6cb659**; plan file sha256
29c28735eb91308678ae964cb3a603d302425dacfbcda7718eb835ac724fffd6; base 362b0d4a241520c9bc79b204c042d9fcefbb06ea.
Scratch clone `--shared`, detached at the freeze commit, `rev-parse --show-toplevel` asserted. The
clone's `tools/round86-rendered-cells.py` (f9d36b5be0683fdc…6e633b), `tools/pre-report-gate.py`
(0ad6a80aa20af72e…04316979) and the plan file are sha256-identical to the lane tree — frozen bytes ran.
Paths relative to `/home/vgpnk/Projects/shokunin/kama-shokunin/`.

## Commands and outputs (true exit codes)
```
mkdir -p $D $D/tmp; export TMPDIR=$D/tmp
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $D/wt            (rc 0)
git -C $D/wt checkout --detach 94e8fe7b…  ; git -C $D/wt rev-parse --show-toplevel == $D/wt

python3 controls/c1-probes.py $D/tools-copy/round86-rendered-cells.py          rc 1
  C1_PROBE control-stale-live-no-shadow red
  C1_PROBE P-A-list-marker-closes-fence escape
  C1_PROBE P-B-wrong-disposition-word-in-row escape
  C1_PROBE P-C-extra-revision-without-receipt escape
  C1_PROBES probes=3 escapes=3 control=red        # byte-identical to c1-probes-before.out lines 1..5

python3 $D/wt/tools/round86-rendered-cells.py --repo $D/wt --rev 362b0d4a…     rc 1
  RENDERED_CELLS facts=3 mismatches=2 gate=1 closure=0 disposition=0 newest_gate=86 newest_closure=86
  RENDERED_CELLS_FINDING closure row names round-85 newest committed closure is round-86 (…round-86…)
  RENDERED_CELLS_FINDING disposition row does not name `round86 rejected-harmed`
                                                   # byte-identical to c1-live-before.out

c2-gate-before.out: PRE_REPORT round=87 arms=13 failed=4; grep -c round86-instruments -> 0  (receipt)
re-run gate on the freeze tree (scratch tools dir), round=87 --tip master       rc 2
  arms=13 failed=3: round-scope green (plan file now exists at the freeze tree; the pre-freeze control
  had it FAIL `status=absent`), round75-instruments FAIL (count-short instead of `no frozen plan`);
  both arms still FAIL, arm list/order and every base-ok arm identical

python3 tools/round86-rendered-cells.py  --selftest  RENDERED_CELLS_SELFTEST pass=17 fail=0 rc 0
python3 tools/round86-mutant-owners.py   --selftest  DEBT_MUTANT_OWNERS_SELFTEST pass=13 fail=0 rc 0
python3 tools/round86-pin-origin.py      --selftest  PIN_ORIGIN_SELFTEST pass=7 fail=0 rc 0
python3 tools/round81-append-debt.py --repo . --round 87 -> APPEND_DEBT … unaccepted=11 (count-short FAILs), rc 1
python3 $O/nw.py tools/round86-rendered-cells.py    rc 1          # no-work probes (see Findings item 2)
  closure-file-only -> mismatches=2 closure=0 disposition=0 newest_closure=86 exit 1
  scorecard-row-only -> mismatches=1 closure=0 disposition=1 newest_closure=85 exit 1
  both-edits -> mismatches=0 exit 0   # rewrites tracked closure body — forbidden by plan L8 fresh-start
```

Evidence: `.ufo/waves/round-87/w1/out/RV01PlanFreezeReview/` — `item1-probes-rerun.txt`,
`item1-live-rerun.txt`, `item1-selftest-*.txt`, `item1-append-debt-rerun.txt`, `nw-results.txt`,
`nw.py`, `fixtures-note.md` (all receipts re-produced at out-dir paths after scratch removal; every
output byte re-verified against the frozen lane tree).

## Findings

**(1) controls real and red — ok.** Probe battery re-run byte-matches `c1-probes-before.out`; live
`--rev 362b0d4a…` re-run byte/exit-matches `c1-live-before.out` (mismatches=2, closure=0 disposition=0,
exit 1); `c2-gate-before.out` carries `arms=13 failed=4` with zero `round86-instruments` mentions. One
nuance, not a defect: at the freeze tree the same gate prints `arms=13 failed=3` because the freeze
commit added `plans/round-87-claims.md` (round-scope flips green; round75-instruments's denial cause
changes shape, stays FAIL). No base-ok arm turned red either way.

**(2) no-work escape for C1 — closed for SCORECARD-only; defect in the C2 harm rule.**
- SCORECARD-text-only correction (row → round-86 + `round86 rejected-honest-stop`, nothing else): frozen
  selector still grades `mismatches=1 closure=0` at newest closure round-85/86 — `mismatches=0` is not
  reachable without C1 work (`nw-results.txt`, variant `scorecard-row-only`).
- The data-only path that clears the round-86 selector needs a closure-file edit too (`nw-results.txt`,
  variant `both-edits`: row + body → mismatches=0) — rewriting a tracked closure, which the plan's
  fresh-start clause forbids ("history is retained and not repaired"). No-work cannot satisfy C1 at all.
- Always-ok arm for C2: closed — a stub that exits 0 with a failing summary fails the C2.2 fault
  harness by construction, and the three component selftests all pass at the freeze tree.
- **Defect R1**: the harm rule ("every arm ok at base stays ok at R", plan L99) names no counting
  command, so the C2 counting list cannot prove it. Required fix: extend the C2 counting-command list
  with a gate-at-base vs gate-at-R arm-verdict diff (e.g. an `ARMS_GONE_GREEN`/`ARMS_GONE_RED` summary
  line from diffing both runs' `PRE_REPORT_ARM` verdict columns).

**(3) successor rule R2 decidable from the round-86 closure — ok.**
`corpus/lessons/round-86-verifier-spotcheck.md:76` is the file's only `verdict \``-formed line and reads
``verdict `rejected-honest-stop` `` in the plan's own L12 shape; token = **rejected-honest-stop**;
grep-over-file confirmed it is unique (the carried-defect block at :78 carries none). R2 is precisely
what the live cell needs: the closure's own R2-shaped verdict line already names that token, so no
closure edit is required by C1 — only the row and the selector fence/disposition oracle fix.

**(4) universal clauses and enumeration — defect R2.**
Enumerated: L42 both predicates; L45 RENDERED_CELLS byte-shape; L57 single R2 token; L92 three summary
shapes. **Partly**: L55 R1 closer shape — named §4.5 only; no probe enumerates other closer variants
(nested, wider fence, marker+space); P-A covers one. **Not enumerated**: L63 R4 population unchanged
(no diffing command named); L99 harm rule "every ok arm" (≈ defect R1).
**Defect R2** (required before data): correct the CommonMark §-id in the plan text (fence closer is §4.6;
§4.5 is the info-string rule the round-86 selector keeps; list items §5.2 per the R86 root cause), and
add a population-diff step for R4 — e.g. a docstring byte-diff of the successor's population block
(`tools/round86-rendered-cells.py:16-22`) against the frozen one.

**(5) C1/C2 causally separable — ok.** The three composed instrument selftests run offline fixtures (no
SCORECARD/live data) and pass at the frozen cell state; `round86-instruments` and its fault harness
depend on none of: the corrected calibration cell, the C1 selector text, or C2. What DOES depend on the
SCORECARD calibration cell: the four base-red arms the plan allows to turn green (`selfdesc`,
`newest-closure`, `round-scope`, `round75-instruments`, plan L100-101); their cell-shaped FAIL causes are
visible in `c2-gate-before.out` (round-scope's cause is the plan file itself). This matches the plan's
own seam statement at L19-20.

**(6) fresh-start reads — ok (one cosmetic).**
- `corpus/lessons/round-84-verifier-spotcheck.md:63` — "Round verdict: rejected-honest-stop; status ok;
  admitted false." Plan L10 matches; note round-84 has no R2-shaped (backticked) verdict line, but no C1
  predicate reads it (it is never the newest closure at any R), so no fix needed.
- `corpus/lessons/round-85-verifier-spotcheck.md:66` — status/verdict block, **rejected-honest-stop**; plan L11 matches.
- `corpus/lessons/round-86-verifier-spotcheck.md:76` — **rejected-honest-stop**; plan L12 matches; the
  freeze commit adds the closure's routed-defect block (:78) and R86V1's three strays as committed
  ground truth. Line :76 is the only verdict line of any shape in the body (single grep hit).

**Cosmetic (no fix required):** plan L8 cites the run-15 amendment marker stem
`blocked/.kama.run15-20261105-N`; the marker on disk is `.kama.run15-20261105-1` (`-N` is a stem
placeholder, not a literal file). No tool reads the literal `N` form.

## Verification gaps

- My gate re-run is the freeze baseline (no `round86-instruments` arm yet); the L1 owns integration and
  its own gate run against a candidate.
- Fault-harness end-to-end (C2.2 `ARM14_FAULTS faults=3 killed=3 escaped=0`) is EX03's candidate; I
  pinned the acceptance line and that each targeted instrument's selftest passes at the freeze tree.
- Tooling: no install/upgrade, no pacman transaction, no network GET. Scratch dir removed after copying
  receipts into the out dir (real, re-run receipts live in the out dir).

VERDICT: ok — controls replays match frozen receipts; two bounded fixes required before data: (R1) put the harm-rule arm-delta into the C2 counting-command list, (R2) correct the CommonMark §-ids in R1 and add a population-diff step for R4.
