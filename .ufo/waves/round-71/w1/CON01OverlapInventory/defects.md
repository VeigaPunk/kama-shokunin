# Inherited-defect inventory — round-70 verifier spot-check §7, status at tip `b43e71a8`

Seat CON01OverlapInventory, kama r71 w1. Five status-neutral defects routed by
`corpus/lessons/round-70-verifier-spotcheck.md` §7. Status judged **at tip `b43e71a8`** (the round-71
freeze commit; `git -C kama-shokunin rev-parse --short HEAD` → `b43e71a8` at scan time, worktree read
only through `git show` / `git ls-tree` / `git grep` / `git status`). No lane file was edited.

| # | Defect | Status at `b43e71a8` | Closed by |
|---|---|---|---|
| 1 | Uncommitted round work at the round-70 tip | **CLOSED** (0 uncommitted under `.ufo/waves/round-70`) | the freeze commit `b43e71a8` itself landed the 26 files; **C1** is the counter that keeps it closed in future rounds |
| 2 | Stale receipt cited as "final" in the round-70 lesson | **OPEN** — the lesson still names `measured/after/census-at-tip.out` (with `waived=0`) among "Final green receipts at the landing tips"; no correction line exists | **no claim** — C1/C2/C3 counters do not grade receipt *freshness*; only the wave's scribe (lessons/corrections) item can carry it |
| 3 | Unreceipted final-tip re-run claim (`61f3ec42`, `380ac279`) | **OPEN** — no receipt under `measured/**` names either tip; the report's remedy (cite the invariance diff) is absent | **no claim** — the receipt-pointer audit grades `measured/` *pointer resolution*, not "a claimed run has a receipt" |
| 4 | C2 boundary control not registered (`controls/refused-member-control.py`) | **OPEN at the freeze** (0 registry occurrences) | **C2** — in kind: it registers `census-waiver-boundary` as a gate row; the round-70 control file itself stays a wave artifact (out of `gate-registry-check`'s declared population) |
| 5 | Supplementary receipts cite scratch tips (`af6e1c84…`, `a7ae13ab…`) | **OPEN** — both objects are still not objects in the lane; the receipts still carry the `tip=` values | **no claim** — C1's audit ignores free-text `tip=` fields inside receipts |

## 1 — Uncommitted round work at the tip: CLOSED by the freeze commit, kept closed by C1

```
$ git -C kama-shokunin status --porcelain -uall -- .ufo/waves/round-70 | wc -l
0
$ git -C kama-shokunin show --numstat --format= b43e71a8 -- .ufo/waves/round-70 | wc -l
26
$ git -C kama-shokunin show --stat --oneline b43e71a8 | head -3
b43e71a8 round-71: freeze, controls and base receipts; land the inherited round-70 wave files
```

The freeze landed exactly the 26 files the closure counted (7 modified seat outputs + 7 untracked paths,
`-uall` expanding the `MT01Mutants/logs/` directory). The pre-freeze evidence is preserved as
`.ufo/waves/round-71/measured/before/git-status.out` (14 status entries; the last line `?? .ufo/waves/round-71/`
is the wave dir the freeze created).

Consequence for C1 worth stating: `uncommitted=0` is **green by construction** at the round-71 report tip
unless a round-71 file is left uncommitted, so the target is only meaningful together with the kill-rule
fixture that plants a fresh uncommitted file under `.ufo/waves/round-71/` (and with the do-nothing control,
which reproduces `uncommitted=26` on a fixture at `af6eb6c2`). No residue of defect 1 remains to be graded.

## 2 — Stale "final" receipt in the round-70 lesson: OPEN, no claim closes it

```
$ git -C kama-shokunin log --oneline b43e71a8 -- corpus/lessons/round-70.md
910e6747 round-70 frontier: round-70 lesson (Gate S052 re-open, Mistakes 1-4, L1 integration addendum), ...
$ git -C kama-shokunin show b43e71a8:corpus/lessons/round-70.md | grep -n 'census-at-tip\|census-at-af6eb6c2'
75:`measured/after/census-at-tip.out` (`HOST_CENSUS pass=22 fail=0 not_evaluated=0 waived=0 total=22`, ...
$ git -C kama-shokunin show b43e71a8:corpus/lessons/round-70.md | grep -ci 'correction'
0
```

Both receipts exist; the *later* one is the corrected form and the lesson cites only the earlier one:

```
$ git show b43e71a8:.ufo/waves/round-70/measured/after/census-at-tip.out | tail -2
HOST_CENSUS pass=22 fail=0 not_evaluated=0 waived=0 total=22 tierA_fail=0 tierB_fail=0
EXIT=0
$ git show b43e71a8:.ufo/waves/round-70/measured/after/census-at-af6eb6c2.out | tail -2
HOST_CENSUS pass=22 fail=0 not_evaluated=0 total=22 tierA_fail=0 tierB_fail=0
EXIT=0
```

`census-at-tip.out` was measured at `73597158`, before the `af6eb6c2` readability landing removed the
unused `waived=` token; the lesson's "Final green receipts at the landing tips" therefore still quotes a
pre-landing output as final. The required fix is an **append-only correction** naming the post-landing
receipts (the closure's own words), which no round-71 counter grades: the receipt-pointer audit resolves
the citation (the file exists), so C1's arm is green on the defective state.

Observed while scanning (not part of the tip status): the *worktree* already carries a 22-line append to
`corpus/lessons/round-70.md` (`git diff --stat` → `22 +`), whose text names
`measured/after/census-at-af6eb6c2.out` and `measured/final/census.out` — i.e. the scribe item is closing
#2 as this inventory is written, uncommitted at scan time. The freeze-tip status above is unchanged.

## 3 — Unreceipted final-tip re-run: OPEN, no claim closes it

```
$ sed -n '40p' /home/vgpnk/Projects/shokunin/.ufo/reports/round-70/kama.md
- **After**, measured at `7be07423` and re-measured at the receipt tip `73597158`: … and at the final
  graded tip `a8df1af5` / `61f3ec42` / `380ac279` unchanged (`measured/final/reconciler.out`; re-run by
  the L1 at `61f3ec42` and `380ac279`: exit 0). …
$ git -C kama-shokunin grep -l '380ac279\|61f3ec42' b43e71a8 -- '.ufo/waves/round-70/measured/*'
(empty)
$ git -C kama-shokunin show b43e71a8:.ufo/waves/round-70/measured/final/reconciler.out | head -1
tip=a8df1af54ca21509f7a91dd99a4cc58c62d5687c r41=0 … closure_ptr=1 mismatches=0 maxN=70 met=True
$ grep -c 'invariance\|diff 61f3ec42' /home/vgpnk/Projects/shokunin/.ufo/reports/round-70/kama.md
0
```

`61f3ec42` is real (`git cat-file -t` → `commit`; subject "round-70 final receipts at a8df1af5: …"),
so the *receipts* were committed there but *measured* at `a8df1af5`. The only textual mention of
`61f3ec42` under the wave tree is a mutation-seat driver transcript
(`.ufo/waves/round-70/w1/out/MT01Mutants/report.md:280-281`), not an instrument receipt. The closure's
two acceptable remedies — ship the receipt, or cite `git diff 61f3ec42 380ac279` (which touches only
`w1.ready.dispatched` and `w1/w1-results.json`) — are both absent at `b43e71a8`.

Cross-lane note: the instrument that grades this exact class already exists and is registered —
tameshi `tools/receipt-revision-gate.py` (`SKILL.md:1547`) requires a receipt's `rev=` to equal the
certified revision, or to name a revision byte-identical on every path listed in `--paths` (the closure's
"cite the invariance" resolution, mechanised). Kama's C1 does not include it, so defect 3 is a *missing
arm* in kama, not an unsolved problem in the fleet.

## 4 — C2 boundary control unregistered: OPEN at the freeze; C2 closes it in kind

```
$ git -C kama-shokunin show b43e71a8:SKILL.md | grep -c 'refused-member-control'
0
$ git -C kama-shokunin ls-tree -r --name-only b43e71a8 -- .ufo/waves/round-70/controls
.ufo/waves/round-70/controls/freeze.txt
.ufo/waves/round-70/controls/refused-member-control.py
$ git -C kama-shokunin ls-tree -r --name-only b43e71a8 -- tools/ | grep -c 'census-waiver-boundary\|pre-report-gate\|round71-province'
0
```

Two scopes must be kept apart, because they disagree:

- Under `gate-registry-check.py`'s **declared population** (`.ufo/waves/round-*/count-*.py` or
  `tools/round<N>-*.py`) the round-70 control is *out of scope* — it is neither shape — so the gate
  cannot report it unregistered even if it were never named.
- Under the closure's Gate standard §Delivery it is a committed, re-runnable verdict script with expected
  values in the freeze, i.e. a gate that owes a registry row.

C2 satisfies the second reading by landing a *new* registered instrument (`census-waiver-boundary`,
expected row 80-82 of the frozen 79 → 82 delta) that carries the five-shim kill battery. It does **not**
give `controls/refused-member-control.py` a row, and nothing in C2's predicate requires one. Residual:
the round-70 file stays an unregistered wave artifact; that is acceptable only while the registered
boundary is the instrument the round cites.

Sibling shape, same class: tameshi's `tools/arm-liveness.py` is also absent from its own `SKILL.md`
(`grep -c arm-liveness tameshi-shokunin/SKILL.md` → `0`), so the "verdict script with expected values but
no registry row" defect is a fleet-wide habit, not a kama-only miss — which is why C2's registration is
the right closure even though the round-70 file is left where it is.

## 5 — Supplementary receipts cite scratch tips: OPEN, no claim closes it

```
$ for h in af6e1c84 a7ae13ab; do printf '%s: ' "$h"; git -C kama-shokunin cat-file -t "$h" 2>&1 | head -1; done
af6e1c84: fatal: Not a valid object name af6e1c84
a7ae13ab: fatal: Not a valid object name a7ae13ab
$ git -C kama-shokunin git grep -c 'af6e1c84\|a7ae13ab' b43e71a8 -- .ufo/waves/round-70
b43e71a8:.ufo/waves/round-70/measured/after/check-kill-probe-gutted.out:1
b43e71a8:.ufo/waves/round-70/measured/after/check-kill-probe-intact.out:1
b43e71a8:.ufo/waves/round-70/measured/after/reconciler-record-only-dry.out:1
```

The three receipts still name tips that resolve nowhere in the lane, and no provenance note (scratch
path, dry-run marker in the `tip=` field) was added at or before the freeze. They are dry-run/fixture
receipts rather than claim evidence, so the defect is a pointer-resolution hazard, not a false claim —
but C1's receipt-pointer audit reads only `measured/<rest>` *citations in the self-record*, so it cannot
see a `tip=` value inside a receipt body and leaves this class ungraded.

## Cross-read: which of the five the round's own counters cover

| Counter | Covers | Leaves |
|---|---|---|
| C1 `pre-report-gate` (four arms + wave-clean arm) | #1 (keeps it closed; its own before-state is the 26-file class) | #2 freshness, #3 receipt-existence, #5 in-receipt `tip=` fields |
| C2 `census-waiver-boundary` | #4 in kind (registered boundary replaces the unregistered control) | — |
| C3 `round71-province-host-claims` | nothing in §7 | #2, #3, #5 remain open; C3's subject is PROVINCE host claims, not round-70 receipts |

The three open defects (#2, #3, #5) therefore ride on the wave's scribe (lessons/corrections) item or on
a future round; none of them can be closed by a counter this round claims to have.
