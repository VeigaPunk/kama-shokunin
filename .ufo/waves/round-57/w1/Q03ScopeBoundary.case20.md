# Q03ScopeBoundary — case 20 independent evidence (C1/C2 boundary check)

Seat: Q03ScopeBoundary (connector, leaf). Lane: kama, round 57, wave kama-r57-w1.
Scope: read-only over the lane tree; writes only this file, the seat report, and `receipts/Q03ScopeBoundary/`.
Scratch: `/fast/scratch/hyaku/kama-r57/Q03ScopeBoundary/` (fixtures removed after capture; receipts copied here first).
Tool installs or updates in this seat: none.

## A. Chronology of round-57 claim text (git, read-only)

Command: `git log --format='%h %ci %s' b89bdab2cc114735ec5d331c6c610134258f7864..HEAD`

```
8640e34c 2026-10-27 15:10:17 -0300 kama-shokunin round-57: record measured counter outcomes
7b74e2f2 2026-10-27 15:08:48 -0300 kama-shokunin round-57: bind prereg roster to executed calls
7c873d7b 2026-10-27 15:06:45 -0300 kama-shokunin round-57: correct frozen claim targets before data
89dc4f52 2026-10-27 15:05:51 -0300 kama-shokunin round-57: freeze counter claims and no-op controls
```

`git show b89bdab…:` is the frozen base. `git show HEAD:` for SCORECARD.md and round-42 counter: the calibration row says `43` at HEAD and `42` at the base.

## B. Frozen claim text vs amendment text

`controls/freeze.txt` (commit 89dc4f52), verbatim:

```
base=b89bdab2cc114735ec5d331c6c610134258f7864
claims=C1 calibration stale canonical-table count; C2 operability canonical-row execution binding
base_counter=1
noop_C1=met=True exit=0 despite skipping data
noop_C2=met=True exit=0 despite skipping data
```

`controls/freeze-amendment.txt` (commit 7c873d7b), key clauses verbatim:

- "supersedes the earlier round-57 freeze's claim ordering only, not its base/control evidence"
- "C1 is the frozen round56-prereg-check no-op control defect, operability axis"
- "C2 is the tools/round42-selfdesc-reconcile.py stale calibration count, calibration axis"
- "Round-56 outside verification finding is authoritative; no post-seat target change."

Control receipts actually frozen in `controls/` (not changed by the amendment):

```
$ cat controls/noop-c1.out     -> fixture=c1-noop.py ... mismatches=0 maxN=46 met=True  exit=0
$ cat controls/noop-c2.out     -> control=no-op instrument; canonical_table_reads=0; self_description_reads=0; summary=mismatches=0 maxN=46 met=True  exit=0
$ cat controls/c1-noop.py      -> print("mismatches=0 maxN=46 met=True")
```

No file under `controls/` references `round56-prereg-check`. Both frozen no-op controls are round-42-shaped (self-description counter, canonical table reads).

Finding B1 (resolved as a fact): the amendment does not only reorder labels. The frozen operability target was the round-42 counter's canonical-row binding (`canonical_table_reads=0` control). The amendment replaces it with the round-56 prereg roster check. Different counter, different surface. The label swap for the round-42 calibration item is consistent across spec, freeze and amendment.

## C. Frozen "expected 46 / maxN" claim vs repo

Commands and exact outputs (read-only):

```
$ git show b89bdab…:SCORECARD.md | grep -c '^## Round'        -> 58
$ git show b89bdab…:SCORECARD.md | grep -n '^## Round 56'     -> 3121:## Round 56 — LD_AUDIT environment classifier and roster-fidelity gate (2026-10-27)
$ git show b89bdab…:SCORECARD.md | grep -o 'len(glob.glob(.corpus/lessons/\*verifier-spotcheck.md.)))"` → `[0-9]*`'
   -> len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` → `42`
$ git ls-tree --name-only b89bdab… corpus/lessons/ | grep -c verifier-spotcheck   -> 43
$ ls corpus/lessons | grep -c verifier-spotcheck                                  -> 43   (working tree)
$ git show HEAD:SCORECARD.md | grep -o '...verifier-spotcheck.md.)))"` → `[0-9]*`'   -> ...→ `43`
$ git diff --stat b89bdab… HEAD -- SCORECARD.md                                   -> 1 file, 2 lines (the 42→43 row)
```

Canonical capability table (python parse of the highest `canonical list as of round N**` table, same rule as `tools/round42-selfdesc-reconcile.py:canon`):

```
frozen-tip canon round 49 data rows 11
```

Finding C1 (boundary, open for the claim text): the frozen C1 wording "counter currently reports maxN=56 instead of expected 46" does not match the repo.
- `maxN=56` is the correct latest round heading (`## Round 56` at line 3121). The counter is right on this value.
- `46` occurs only as a hard-coded literal in the do-nothing control files (`c1-noop.py`, `noop-c2.out`). No repo source derives 46.
- The canonical table at the frozen tip has 11 rows, not 46.
- The only failing fact in the base receipt is the calibration run: SCORECARD states `42`, the glob at the tip counts `43` (`controls/base-c1.out` detail line: "no stdout line == '42' (exit 0)"). This matches the amendment's description and not the frozen one.

## D. Predicate boundary of the repaired operability counter (independent fixture test)

Question: does the repaired `tools/round56-prereg-check.py` (commit 7b74e2f2, `executed = expected <= invoked`, where `invoked` is the set of constant string labels appearing as the first argument of any `run(...)`/`assert_mutant_breaks_detection(...)` call anywhere in the AST) reject a harness that declares the matching roster but executes none of its entries?

Fixtures (committed in throwaway `git init` repos under scratch; each asserted `git rev-parse --show-toplevel` equal to its own dir before commit; battery and preregistration taken from lane `HEAD:` blobs `8640e34c`):

- `genuine`: unchanged battery at HEAD.
- `noop-literal`: ROSTER literal kept, `def main(): return 0`, no call sites.
- `deadcall`: ROSTER literal kept, `def main():` first statement is `return 0`, followed by the original `run(...)` / `assert_mutant_breaks_detection` call sites. The call sites are unreachable at runtime; zero battery entries execute. They are still present in the AST.

Commands (run from the scratch driver; lane counter invoked read-only with `--repo <fixture>`):

```
$ python3 tools/round56-prereg-check.py --repo .../fx-genuine      --tip fc3cf268…  -> tip=fc3cf268… / present=1 roster_match=1 kills=1 controls=2 met=True   / exit=0
$ python3 tools/round56-prereg-check.py --repo .../fx-noop-literal --tip b4b244de…  -> present=1 roster_match=1 kills=1 controls=2 met=False  / exit=1
$ python3 tools/round56-prereg-check.py --repo .../fx-deadcall     --tip 60e95981…  -> present=1 roster_match=1 kills=1 controls=2 met=True   / exit=0
```

Receipts (copied): `receipts/Q03ScopeBoundary/prereg-genuine.out`, `prereg-noop-literal.out`, `prereg-deadcall.out`.

Result: the literal no-op is rejected; the dead-call no-op is accepted. The amendment's C1 predicate ("the measured checker rejects a no-op that declares the matching roster but executes none") is therefore not satisfied by the repaired counter. This is a predicate-shape gap (AST presence instead of runtime execution), not a boundary of ownership. Routed to the attack seats (R03NoopAttack, R07KillDesign, R09CounterMutation) for confirmation; this seat did not change any counter.

## E. Axis attribution of the prereg no-op defect across sources (verbatim quotes)

- `SCORECARD.md` round-56 current authority / round-56 section table: "C2 (preregistration/battery roster fidelity, calibration)".
- `tools/round56-prereg-check.py` docstring line 1: "Round-56 C2 calibration counter: compare the frozen battery roster to preregistration."
- `corpus/lessons/round-56-verifier-spotcheck.md` claims re-check: "C2 calibration 7→7 — unprovable"; routed defects: "Strengthen C2-style calibration gates to bind actual executed battery entries and test SCORECARD/SHONEN disagreement; a roster literal/no-op harness must fail."
- Round-57 spec (`w1-spec.json` context) and freeze: C2 = operability (canonical-row binding); C1 = calibration (count).
- Round-57 amendment: prereg no-op = operability (as C1); count = calibration (as C2).

So three round-56 sources put the prereg no-op on calibration; the round-57 amendment, which cites the round-56 outside finding as authoritative, puts it on operability. The amendment's own cited authority contradicts its axis. Left open for the operator/closure to rule.

## F. Limits of this file

- No counter was modified. No lane file was edited. The frozen counter was not run on the working tree; numbers above come from committed blobs.
- Working tree at the late check: `corpus/lessons/round-57.md` modified (+3/−1) per `git diff --stat -- SCORECARD.md tools corpus/lessons`. An earlier `git diff --stat HEAD` had also shown `SCORECARD.md` (+18/−2), which was no longer dirty by that later check. Not authored by this seat; not evaluated.
- The §9 do-nothing rule cited in round-56 SCORECARD is not located as text in `PROTOCOL.md`, `PROTOCOL-APPENDIX.md`, `AXES.md`, `LEARNING.md`, `CORPUS.md`, `corpus/QUALITY.md`, or `corpus/README.md` (`grep -n 'do-nothing'` returned no rule text). Recorded as an open reference, not resolved.
