# CR01PredicateCritic — claim-sizing falsification (kama r86 w1)

Seat: critic (author-side advisory). No claim admission, no edit, no commit, no integration;
the L1 is the sole committer and the non-author closure is the admission rule.

Measured revisions: base `3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d`, freeze
`c07e1f909414aafb2d8de5605a81fd3bd4e3550e`, repair `67eddac89f44e768b670301ea0feff06e766f32d`
(the current HEAD at measurement). The worktree instruments are byte-identical to the freeze
(`00-env.receipt`): `round86-rendered-cells.py`, `round86-mutant-owners.py`,
`round86-pin-origin.py`, `count.py` and `round81-append-debt.py` all `same=yes`.

Every re-measurement below is the frozen counter invoked with an explicit `--rev`; every fixture
is a module-level call into the committed instrument with an injected fetcher/tree. Receipts in
`.ufo/waves/round-86/w1/out/CR01PredicateCritic/`.

## C1 — calibration / rendered-cell identity

**Do-nothing test.** Base and freeze are both red and reproduce the frozen before-receipt exactly
(`01-c1-base.receipt`, `01-c1-freeze.receipt`, rc=1):

```
RENDERED_CELLS facts=3 mismatches=3 gate=0 closure=0 disposition=0 newest_gate=85 newest_closure=85
RENDERED_CELLS_FINDING gate declared round=84 newest terminal receipt round=85 (.ufo/waves/round-85/measured/after/gate.out)
RENDERED_CELLS_FINDING closure row names round-84 newest committed closure is round-85 (corpus/lessons/round-85-verifier-spotcheck.md)
RENDERED_CELLS_FINDING disposition row does not name `round85 rejected-honest-stop`
```

A do-nothing tree at base or at the freeze cannot reach `mismatches=0`. The L1's repair commit
`67eddac8` is green (`01-c1-repair.receipt`, rc=0, `facts=3 mismatches=0 gate=1 closure=1
disposition=1`), so the target is reached by the repair, not by the freeze. **But the green is
transient:** the round's own terminal gate receipt is the newest once committed, and the cell
names round 85. A fixture adding `.ufo/waves/round-86/measured/after/gate.out` with
`PRE_REPORT round=86 …` turns the same green into `gate=0` (`10-c1-gate-receipt-supersedes.receipt`).
The final measurement must therefore be taken after the round-86 gate receipt and the cell must
name it in the same commit; the `67eddac8` receipt is not the final state.

**Before-state real.** Yes, byte-for-byte the frozen `c1.out`; the base and freeze lines are
identical.

**Kill rule on the round's own false green.** Yes. `--selftest` is 11/11 PASS
(`04-selftest-round86-rendered-cells.receipt`): `fenced-shadow`, `comment-shadow`,
`tilde-fence-shadow` and `indent-shadow` all `mismatches=3 gate=0`; `unclosed-fence` exits 2;
`contradictory-receipt`, `missing-receipt`, `command-round-disagrees`, `closure-only-stale` and
`no-closure-population` all red/exit 2. The round-85 fenced false green is red here.

**Weakest clause (false green).** The gate fact does not bind the named receipt to the newest
receipt. The frozen sentence says the cell "names the newest terminal gate receipt with its
revision, command and receipt bytes coupled"; the code uses `newest[0]` (the round number) only,
never `newest[1]` (path) or `newest[2]` (token), and `gate_fact` accepts **any** backticked
`.out` whose bytes at the graded revision carry the token. Counterexamples:

- a live cell naming `alt-receipt.out` (not the newest receipt) while
  `.ufo/waves/round-85/measured/after/gate.out` remains newest → `mismatches=0 gate=1`
  (`10-c1-nonnewest-receipt.receipt`);
- a `.out` under `.ufo/waves/round-1/measured/after/` carrying `PRE_REPORT round=85 …` is selected
  as `newest` (path order among equal rounds) and the cell naming it is green
  (`10-c1-round1-receipt-defines-newest.receipt`).

Cheapest fixture: one extra `.out` carrying the token plus one string replace in the live cell.
Smallest safe correction: require the cell's named receipt path to equal `newest[1]` and its bytes
at the named revision R to carry the token; derive the receipt's round from the wave directory and
reject a token round that disagrees with it.

**Secondary C1 clauses.** (a) `disposition_of` returns the first disposition word in the fixed
tuple order `(rejected-harmed, rejected-honest-stop, admitted)`, not the closure's verdict; a body
that says "prior round rejected-harmed; this round rejected-honest-stop" returns
`rejected-harmed` (`10-c1-disposition-tuple-order.receipt`). The round-85 body is safe (it has
`admitted` and `rejected-honest-stop` only), but the round-86 closure is likely to cite r83
`rejected-harmed`, so the next C1 would misread it. (b) `ROW_CLOSURE` requires the literal phrase
`latest outside closure …`; a semantically correct row saying `latest closure …` is red
(`10-c1-closure-wording.receipt`). (c) The "receipt bytes at R" clause reads the receipt at the
graded revision, not at R (confirmed independently by EX02CoupledBinding); a paragraph whose
"measured at R" state is false at R still couples.

**Axis naming.** C1 edits `SCORECARD.md`; the number it produces is `mismatches=0` — a
self-report-integrity count. The calibration score stays 7 and the round claims no score move, so
the axis label follows the row's home axis (the surface), not a calibration number. Advisory:
label the capability "rendered-cell identity", not a calibration delta.

## C2 — operability / mutant owners and summary cardinality

**Do-nothing test — this is the strongest sizing defect.** Base is red and reproduces the frozen
receipt exactly (`02-c2-base.receipt`, rc=1): `killed=3 escaped=2 invalid=0 arms=unknown
cardinality=ok owners=3/5`, M5/M6 `escaped green summary`. **The freeze commit is already green**
(`02-c2-freeze.receipt`, rc=0): `killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5`,
M5 `arm-count`, M6 `summary-cardinality`. The freeze commit `c07e1f90` contains the production
repair itself — `tools/round81-append-debt.py` gained `EXPECTED_ARMS=34`, the
`APPEND_DEBT_SELFTEST_ARMS` line, the summary `arms=` field and the exit condition
(`git diff 3ff23da3 c07e1f90 -- tools/round81-append-debt.py`). The plan's freeze order names
"this plan, the three instruments and the frozen counter" and the before receipts, not the
production subject. So the wave starts green; the before receipt is at base, which is not the
wave's starting tree, and a tree that does nothing after the freeze already reaches the target.
Smallest safe correction: move the `round81-append-debt.py` hunk to the integration commit and
re-freeze the before receipt at the freeze (it would read `arms=unknown`, M5/M6 escaped), so the
after receipt measures the L1's repair rather than the freeze.

**Before-state real.** Yes, the base line is exact.

**Kill rule on M5/M6.** Yes at the freeze: M5 `arms=33 != expected=34` (owner `arm-count`), M6
`summary pass+fail=0 != arms=34` (owner `summary-cardinality`). But the round-85 forged shape is
not killed: `classify` on `APPEND_DEBT_SELFTEST_ARMS arms=34 expected=34 fail_lines=0` +
`APPEND_DEBT_SELFTEST pass=0 fail=0` (no `arms=` field) returns `('escaped',
'summary-cardinality', 'green summary')` (`11-c2-forged-summary-no-arms.receipt`). The
`forged-summary` control adds `arms=34`, which is not the round-85 shape. The `pass + fail ==
arms` clause is conditional on an optional summary field; the predicate says "each completed
summary reconciles with its arm population". Cheapest fixture: one `classify` call.

**Target line not pinned.** The instrument exits 0 with `arms=33`: a copy of the source with 33
real arms and `EXPECTED_ARMS=33` prints `DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0
invalid=0 arms=33 cardinality=ok owners=5/5`, rc=0 (`12-c2-arms33.receipt`). The frozen target line
requires `arms=34`; `main`'s exit condition checks `killed/escaped/invalid/owners/cardinality`
only, not `arms`. Smallest safe correction: pin `arms == "34"` (or require the pristine ARMS
`expected == 34` independently of the source constant).

**`cardinality` is constant.** Base and freeze both print `cardinality=ok`. The field is `ok`
iff no mutant run is `invalid`, so the base's two escapes print `ok`; the claim's "summary
cardinality" is carried entirely by `killed/escaped`. Smallest safe correction:
`cardinality="bad"` when any run lacks exactly one ARMS line or any summary fails reconciliation;
the base then reads `cardinality=bad` and the target `ok` discriminates.

**Axis naming.** The number `killed=5 escaped=0` is a fault-detection count, on-axis for
operability. The `cardinality` field is named by the claim but does not move; the `arms=34`
literal is the population the claim asserts but the instrument does not pin.

**Weakest clause.** The forged summary without `arms=` (round-85 shape) is classified escaped;
cheapest fixture is the single `classify` call above. The strongest sizing defect is the
freeze pre-satisfaction, not a clause.

## C3 — freshness / pin-origin corroboration

**Do-nothing test.** Base is `could-not-evaluate: no tools/round86-pin-origin.py at
3ff23da3…`, rc=2 (`03-c3-base.receipt`) — exact. The freeze has the instrument, so a tree that
does nothing after the freeze can run it and, if the network and anchors are honest, print
`verified=5`. This is a capability acquisition: the instrument is the subject, and the freeze
order does list the instruments. The before receipt therefore measures instrument absence, not a
row failure; no row was stale. `verified=5` is a capability receipt, not a freshness delta. The
axis label follows the pin surface; the number is origin agreement. Advisory, not a false green.

The live leg is not re-executed by this seat (this item names no URL). The local half is measured:
all nine committed anchor headers' `sha256` match their stored bodies
(`03-c3-local-digests.receipt`), so the `bad=0` side is intact; origin agreement against the live
URLs remains the instrument's own after receipt.

**Kill rule on the fabricated extract.** Yes. `--selftest` is 7/7 PASS
(`04-selftest-round86-pin-origin.receipt`): `fabricated-hash-consistent` → `mismatch`,
`digest-lie`/`malformed-header`/`missing-anchor` → `bad`, `unreachable` → `unreachable`,
`range-outside-upstream` → `mismatch`. The hash-consistent fabricated extract is not `verified`.

**Weakest clause (unfalsified population).** The "two committed anchor extracts" are not bound to
the row's `ref`/`newest` or the anchor's `ref`; the row's columns other than the two extract paths
are never read. Counterexamples:

- `extract_pin == extract_newest == corpus/anchors/one.txt` → `verified=1`
  (`13-c3-same-anchor.receipt`); one file counted twice satisfies "two extracts";
- row `ref=NOT-THE-REF` with anchors declaring `ref=v1`/`v2` → `verified=1`
  (`13-c3-row-ref-mismatch.receipt`).

The predicate's "every row's two committed anchor extracts match the live upstream bytes" is
satisfied by one file twice; the pin side is not corroborated. Cheapest fixture: duplicate the pin
path. Smallest safe correction: require the two paths to differ, parse the URL's ref segment and
the anchor `ref`, and require them to equal the row's `ref`/`newest`.

**Target line not pinned.** `rows=5` is not an exit condition: a 4-row register, all rows
verified, prints `PIN_ORIGIN rows=4 verified=4 mismatch=0 unreachable=0 bad=0` and the exit
condition is 0 (`14-c3-rows4.receipt`). The frozen line requires `rows=5`. Smallest safe
correction: require `rows == 5` (or a declared expected count) in the exit condition.

**Live robustness.** `check_anchor` catches `URLError, OSError, ValueError` but not
`http.client.HTTPException`; a `BadStatusLine` propagates, and `main` catches only
`CouldNotEvaluate`, so the run is a traceback/exit 1 with no `PIN_ORIGIN` line
(`15-c3-http-exception.receipt`). The docstring's "unreachable" / exit 2 contract is not met on
that path. Smallest safe correction: catch `http.client.HTTPException` in `check_anchor` (map to
`unreachable`) and `OSError`/`CalledProcessError` in `main` (map to 2).

**Axis naming.** The number `verified=5` is live-byte agreement; the freshness score is unchanged
and no row moved. The axis is named by the pin surface, not by a freshness delta; the capability
is real but the label is a home-axis tag.

**Weakest clause.** The row binding (same-anchor / ref-mismatch); cheapest fixture is the
duplicated pin path.

## Cross-cutting — the frozen counter grades the working tree, not `--rev`

`count.py` builds `[sys.executable, pathlib.Path(args.repo).resolve() / script, …]` and never
extracts the instrument at `--rev`, despite its docstring "delegates to the committed instrument".
A scratch git fixture proves the false provenance (`20-counter-provenance-*`): the committed
instrument at `HEAD` prints `mismatches=1`, rc=1
(`20-counter-provenance-committed-run.receipt`); the worktree instrument is edited to print
`mismatches=0`, rc=0, and is left uncommitted (`M tools/round86-rendered-cells.py`,
`20-counter-provenance-status.receipt`); `count.py c1 --repo <fixture> --rev HEAD` then prints
`RENDERED_CELLS facts=3 mismatches=0 …`, rc=0 (`20-counter-provenance-counter.receipt`). The
receipt says `--rev HEAD`; the verdict came from uncommitted bytes. The C2 before receipt is a
live instance: at base the instrument did not exist, yet the counter printed a verdict.

Smallest safe correction: add `--instrument-rev` (default `--rev`; the before receipts pass the
freeze) and materialise the instrument with `git show <instrument-rev>:<script>` into `--work`
before executing it, or refuse when `git diff --quiet <rev> -- <script>` fails and no explicit
instrument revision is given. c3's `REQUIRES_AT_REV` checks presence at `--rev` but still runs the
worktree file, so the presence gate gives a false sense of pinning. The before receipts should
also record the instrument revision, which they currently do not.

## Findings summary (advisory)

| Claim | Before real | Target unreachable by do-nothing tree | Kill fires on named false green | Weakest clause / sizing defect |
|---|---|---|---|---|
| C1 | yes (base and freeze exact) | yes at base/freeze; repair `67eddac8` green | yes (fenced/comment/tilde/indent red) | named receipt not bound to newest; non-newest/round-1 `.out` greens; green is transient w.r.t. the round-86 gate receipt |
| C2 | yes (base exact) | **no at the freeze** — `c07e1f90` already green; repair is in the freeze commit | yes for M5/M6 at the freeze; **no** for the round-85 forged shape without `arms=` | freeze pre-satisfaction; `cardinality=ok` constant; `arms=34` not pinned; forged summary without `arms=` escapes |
| C3 | yes (exit 2 at base) | no at the freeze (capability is the instrument); before is instrument absence, not a row failure | yes (fabricated extract → mismatch) | two extracts not bound to row `ref`/`newest` or distinctness; `rows=5` not pinned; live `HTTPException` uncaught |

The before receipts are real and the three selftests are reproducible. The strongest sizing defect
is C2's freeze pre-satisfaction plus the constant `cardinality` field; the strongest false-green
clause is C1's non-newest receipt; the strongest population hole is C3's row binding. None of these
is a claim admission or a closure verdict; they are the corrections the L1 must decide on.
