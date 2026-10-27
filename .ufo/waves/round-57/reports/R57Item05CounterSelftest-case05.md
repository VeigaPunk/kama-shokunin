# R57Item05CounterSelftest — case 5 (executor, mixed build/attack wave)

Seat `E03CounterSelftest`. Axes under measurement: operability (C1) + calibration (C2), per
lane `SCORECARD.md`/`shokunin.conf`; the `MISSION.md:29` "operability + freshness" text is a
historical conflict and is not resolved here. No shared/source/lane-tracked file was edited,
no fleet file written, no commit/push/jj mutation, no tool installed. All probe traffic used
private scratch `/fast/scratch/hyaku/kama-r57/E03CounterSelftest/` (removed after receipts were
copied here) and isolated fixture repos whose `git rev-parse --show-toplevel` was asserted equal
to the fixture root before every commit.

## What was built

A runnable selftest that judges an *instrument*, not a claim. Two modes:

* `--mode c1` — instrument shape of `tools/round56-prereg-check.py`. Seven isolated fixtures:
  genuine battery, no-op battery with the exact ROSTER literal and `main(): return 0`
  (frozen round-57 control shape), no-op with calls after an unconditional `return`, no-op with
  calls in a never-called function, literal-only no-op, stale roster (one designation mutated),
  absent files, unparseable preregistration.
* `--mode c2` — instrument shape of `tools/round42-selfdesc-reconcile.py`. Six isolated fixtures
  built from the frozen base `b89bdab2cc114735ec5d331c6c610134258f7864`: stale spotcheck count
  (declared 42, tree 43), repaired count (declared 43), repaired count with one spotcheck lesson
  deleted (tree 42), SCORECARD truncated at `## Round 47` (heading max 46), SCORECARD with an
  appended `## Round 99` heading, and a tree with no SCORECARD.

The selftest never trusts the instrument's summary. For every fixture it re-derives the fact
independently from committed bytes (`git ls-tree -r` for the spotcheck population,
`git cat-file -p` for the declared literal, `^## Round (\d+)` for maxN), then compares. A green
summary that did not read the tree therefore fails; a stale self-description count is flagged
even when the instrument prints `met=True`. `--require-witness` additionally demands the sha256
of the bytes the instrument read (`battery_sha256`/`prereg_sha256`, `sc_sha256`).

Artifacts: `measured/R57Item05CounterSelftest/bin/selftest.py` (the control),
`bin/build-fixtures.py` (fixture builder), `bin/dump-evidence.py`, `bin/ref/ref-c1-execbind.py`,
`bin/ref/ref-c2-witness.py` (reference instruments), `bin/prereg-pre-repair.py`,
`bin/prereg-candidate.py`, `bin/frozen-noop.py`, `bin/noop-c1-instrument.py`,
`out/fixtures.json` (fixture tips), `out/evidence-c1.txt`, `out/evidence-c2.txt`,
`out/c1/*.out`, `out/c2/*.out`.

## C1 (operability): the no-op defect is real and the committed repair is incomplete

Instrument `bin/prereg-pre-repair.py` = `git show 7c873d7:tools/round56-prereg-check.py`,
sha256 `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853` — identical to the
`counter_sha256` frozen in `.ufo/waves/round-56/preregistration.json` C2.

```
$ python3 bin/selftest.py --mode c1 --instrument bin/prereg-pre-repair.py --label prereg-pre-repair
check c1-genuine/green PASS expected=exit=0 met=True observed=exit=0 met=True
check c1-noop-deadcode/red FAIL expected=exit!=0 met=False observed=exit=0 met=True
check c1-noop-unusedfn/red FAIL expected=exit!=0 met=False observed=exit=0 met=True
check c1-noop-literal/red FAIL expected=exit!=0 met=False observed=exit=0 met=True
check c1-stale-roster/red PASS expected=exit!=0 met=False roster_match=0 observed=exit=1 met=False roster_match=0
check c1-absent/red PASS expected=exit=1 present=0 met=False observed=exit=1 present=0 met=False
check c1-badjson/exit2 PASS expected=exit=2 observed=exit=2
SELFTEST mode=c1 instrument=prereg-pre-repair checks=7 failed=3 verdict=FAIL
exit=1
```

Instrument `bin/prereg-candidate.py` = committed repair at
`7b74e2f2515a6f598918488fa5144658ff29925f` (`round-57: bind prereg roster to executed calls`),
sha256 `dee6f922d0d93b10512f9a799b94f36a1e0f080404a525e08121a223b2e90ced`:

```
$ python3 bin/selftest.py --mode c1 --instrument bin/prereg-candidate.py --label prereg-candidate
check c1-genuine/green PASS expected=exit=0 met=True observed=exit=0 met=True
check c1-noop-deadcode/red FAIL expected=exit!=0 met=False observed=exit=0 met=True
check c1-noop-unusedfn/red FAIL expected=exit!=0 met=False observed=exit=0 met=True
check c1-noop-literal/red PASS expected=exit!=0 met=False observed=exit=1 met=False
check c1-stale-roster/red PASS expected=exit!=0 met=False roster_match=0 observed=exit=1 met=False roster_match=0
check c1-absent/red PASS expected=exit=1 present=0 met=False observed=exit=1 present=0 met=False
check c1-badjson/exit2 PASS expected=exit=2 observed=exit=2
SELFTEST mode=c1 instrument=prereg-candidate checks=7 failed=2 verdict=FAIL
exit=1
```

The outer two checks now discriminate: the frozen no-op shape is killed, but a battery that
*declares* the roster and places the same `run(label, …)` calls after an unconditional `return`
(or inside a never-called function) still prints `present=1 roster_match=1 kills=1 controls=2
met=True`, exit 0. The repair uses `ast.walk`, which counts unreachable call sites as execution;
it is not execution binding. Raw per-fixture output: `out/evidence-c1.txt`.

Reference instrument `bin/ref-c1-execbind.py` (same CLI/summary, plus digests and
`executed=<n>/<m>`) computes reachability from the `if __name__ == "__main__"` block, skips
constant-false branches, stops at an unconditional `return`/`raise`, and follows locally
defined functions:

```
$ python3 bin/selftest.py --mode c1 --instrument bin/ref-c1-execbind.py --label ref-c1-execbind --require-witness
check c1-genuine/green PASS ...
check c1-noop-deadcode/red PASS expected=exit!=0 met=False observed=exit=1 met=False
check c1-noop-unusedfn/red PASS expected=exit!=0 met=False observed=exit=1 met=False
check c1-noop-literal/red PASS expected=exit!=0 met=False observed=exit=1 met=False
check c1-stale-roster/red PASS ...
check c1-absent/red PASS ...
check c1-badjson/exit2 PASS ...
check c1-genuine/witness PASS expected=battery_sha256=69b77a6a64f2667757842c2471ddc256d12ceb5ccca6df0a57b88bbe17ab51c5 prereg_sha256=fa4b5a100a9fd6ceaec93c537f3d9264a0883fac873368243ff1ae041d82ee68 observed=present
SELFTEST mode=c1 instrument=ref-c1-execbind checks=8 failed=0 verdict=PASS
exit=0
```

Deliberate no-op instrument `bin/noop-c1-instrument.py` (prints the target summary, reads
nothing): 7 of 8 checks fail, `verdict=FAIL`, exit 1.

## C2 (calibration): the stale count is detected independently, and the frozen no-op is rejected

Fixture `c2-base` is the frozen base tree `b89bdab2…` (fixture commit
`059afa6b8c55ff3b496080526a2b7da5b95adb09`). Committed instrument
`bin/ref/round42-selfdesc-reconcile.py` (`git show 7b74e2f:tools/round42-selfdesc-reconcile.py`,
sha256 `9736923ec3086c6e56512cd67fa7c00a22cbb8ac63022bef45a676f2200f9ef0`):

```
$ python3 bin/selftest.py --mode c2 --instrument bin/ref/round42-selfdesc-reconcile.py --label round42-selfdesc-reconcile --require-witness
check c2-base/red PASS expected=exit=1 mismatches>=1 detail names verifier-spotcheck observed=exit=1 mismatches=1 detail=True
check c2-base/indep-stale PASS expected=declared!=observed (declared=42 observed=43) observed=declared=42 observed=43 stale=True
check c2-fixed/green PASS expected=exit=0 mismatches=0 met=True observed=exit=0 mismatches=0 met=True
check c2-fixed/indep-fresh PASS expected=declared==observed observed=declared=43 observed=43
check c2-fixed-minus-lesson/red PASS expected=exit=1 mismatches>=1 observed=exit=1 mismatches=1
check c2-fixed-minus-lesson/indep-stale PASS expected=declared!=observed observed=declared=43 observed=42
check c2-maxn-trim/maxN PASS expected=maxN=46 (independent heading max) observed=maxN=46 exit=1
check c2-maxn-inflated/maxN PASS expected=maxN=99 (independent heading max) observed=maxN=99 exit=1
check c2-no-scorecard/exit2 PASS expected=exit=2 observed=exit=2
check c2/met-agrees-with-independent-staleness PASS expected=met==False iff independent staleness observed=agree=True
check c2-fixed/sc-witness FAIL expected=sc_sha256=e5e396fac31d8351f3f7b7f8413ed39b58de03a54db9fdf14a57c9a18c63d9a5 observed=absent
SELFTEST mode=c2 instrument=round42-selfdesc-reconcile checks=11 failed=1 verdict=FAIL
exit=1
```

So the committed counter is behaviourally correct on the stale-count defect — it re-derives the
count and fails on the stale tree, is green on the repaired tree, and goes red again when one
lesson blob is deleted (proving the fact is tree-derived, not hardcoded) — but it emits no
content witness, which is the only cheap proof a green summary came from the tree.

Reference instrument `bin/ref/ref-c2-witness.py` (committed counter unchanged + three witness
lines) passes all 11 checks including the digest: `verdict=PASS`, exit 0. Raw per-fixture
output, including `declared_spotcheck`/`observed_spotcheck` and `sc_sha256`, is in
`out/evidence-c2.txt`.

Frozen no-op control `bin/frozen-noop.py` (the round-57 `controls/c1-noop.py` body, which
prints `mismatches=0 maxN=46 met=True` and reads nothing), run through the C2 matrix:

```
check c2-base/red FAIL ... observed=exit=0 mismatches=0 detail=False
check c2-fixed-minus-lesson/red FAIL ... observed=exit=0 mismatches=0
check c2-maxn-inflated/maxN FAIL expected=maxN=99 observed=maxN=46
check c2-no-scorecard/exit2 FAIL expected=exit=2 observed=exit=0
check c2/met-agrees-with-independent-staleness FAIL observed=agree=False
SELFTEST mode=c2 instrument=frozen-noop checks=10 failed=5 verdict=FAIL
exit=1
```

## Frozen-claim calibration findings (reported, not resolved)

1. The pre-amendment freeze text ordering ("C1 calibration—… maxN=56 instead of expected 46")
   does not match the measured tree. Committed `SCORECARD.md` at the frozen base
   `b89bdab2…` has `## Round` headings whose maximum is 56, and the counter prints
   `maxN=56`; there is no committed state in which the derived maximum is 46 while the counter
   says 56. `controls/freeze-amendment.txt` supersedes the ordering, and its C2 statement —
   calibration run "expects 42" while the committed outside verifier-spotcheck count is 43 — is
   exactly what the fixtures reproduce (`declared=42 observed=43`). The maxN=56 field is not
   stale at base; the stale value is the spotcheck count literal.
2. The frozen no-op `controls/c1-noop.py` produced `mismatches=0 maxN=46 met=True` exit 0; the
   selftest rejects that instrument on 5 of 10 checks. `maxN=46` happens to equal the
   `c2-maxn-trim` heading maximum, which is why a hardcoded field survives that one check — the
   inflated fixture (independent max 99) is what kills it.
3. Lane HEAD advanced while this seat ran (`b89bdab2` → `7c873d7` → `7b74e2f`); every fixture
   tip is pinned in `out/fixtures.json`. At `7b74e2f` the lane counter is green
   (`mismatches=0 maxN=56 met=True`, exit 0), but the C1 repair there still does not bind
   execution (deadcode/unusedfn survivors above), so a green lane output does not imply an
   operative C1 gate.

## Viable integration design

1. Land `tools/round56-counter-selftest.py` (this `bin/selftest.py`) with the fixture matrix as
   its data: the builder materialises fixtures under a scratch root from a pinned tip, then the
   matrix asserts (a) genuine-green, (b) every no-op shape red, (c) content mutations flip the
   verdict, (d) fail-closed exit 2 on malformed input, and (e) content digests for
   `--require-witness`.
2. Require `--require-witness` for any instrument admitted as a lane capability counter, i.e.
   the counter must print the sha256 of every blob whose content it graded. This is the only
   control that defeats a no-op that hardcodes both the green and the red answers.
3. For C1 specifically, replace the static `ast.walk` invocation set with reachability from the
   `__main__` guard (reference implementation `bin/ref-c1-execbind.py`, 8/8 checks). If the
   battery is cheap enough, prefer real execution with per-label receipt lines over any static
   analysis; unreachable-call fixtures then become unrepresentable.
4. Keep the maxN field derived, and test it with the trim/inflate pair rather than a literal
   expectation; the pair proves the field tracks the tree in both directions.
5. Wire the selftest into the counter's own kill rule: an instrument that fails the matrix is
   not admissible even if its summary is green on the measured tip.

## Risks / blockers

* The fixture builder extracts the committed tree at a pinned tip; the round-36 nested probe
  dump `.ufo/waves/round-36/w3/out/MutRowPipe` is excluded because it is a 400 MB self-similar
  tree that no C2 check reads. If a future C2 check cites a receipt under that path, the
  exclusion must be revisited.
* The C1 deadcode/unusedfn fixtures are Python-AST constructions. If the battery moves to a
  non-Python driver, the reachability predicate does not transfer and the fixture would need a
  behavioural (execution-receipt) replacement.
* Fixture repos carry synthetic identities (`e03 <e03@selftest>`); they are scratch-only and
  never pushed.
* Tooling: no install or update was performed; no pacman transaction was attempted; `python3`
  and `git` are host-provided.

Distinct case 5 evidence, produced by a separate derivation path, is in
`reports/R57Item05CounterSelftest-case05-evidence.md`.
