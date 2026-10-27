# R57Item07LessonDraft — distinct case 7 (independent evidence)

Seat: `S02LessonDraft` (scribe, leaf; no subagent dispatch). Item: draft §Gate and §Mistakes additions
for `corpus/lessons/round-57.md` from the round-56 outside closure and the frozen round-57 claims; no
source-tree, lesson, SCORECARD, fleet, or git mutation by this seat.

Case 7 test target: every factual assertion the draft puts into §Gate/§Mistakes is re-derived here
from committed bytes, frozen receipts, or a live source fetch. Read-only against the lane; the only
writes are this file, `.ufo/waves/round-57/w1/out/S02LessonDraft.md`, and the raw receipts under
`.ufo/waves/round-57/reports/case7-receipts/`.

## Tip log (the lane advanced under this seat; every commit below is another agent's, not mine)

| Observed tip | What was observed there |
|---|---|
| `b89bdab2cc114735ec5d331c6c610134258f7864` | frozen base for all round-57 controls; base counter red; 43 committed spotcheck files |
| `7c873d7b4e3839489a93d6334cdf93fe5d34d19f` | pre-data ordering correction (`freeze-amendment.txt`) |
| `7b74e2f2515a6f598918488fa5144658ff29925f` | C1 repair committed; counter `met=True maxN=56`; `measured/{noop-c1,c2-final}.out` untracked |
| `77e7f5eef2b0c759b7509056c7c511255477496d` | lesson committed; §Round 57 in SCORECARD; `maxN=57`; measured receipts committed |
| `8a7f19760242bbe523fa2d7d1b22528b587633c1` | final observation: lesson Gate adds S516; §Round 57 cites a brace-expanded receipt token; counter `met=True maxN=57` |

All commands below name the tip they ran against.

## 1. C2 (calibration) — frozen base

Command A:
`python3 tools/round42-selfdesc-reconcile.py --repo . --tip b89bdab2cc114735ec5d331c6c610134258f7864`

Observed (stdout, exit 1):
```
tip=b89bdab2cc114735ec5d331c6c610134258f7864
r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False
detail: r41 calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '42' (exit 0)
```

Mismatch cause, both sides separately:
`git show b89bdab2:SCORECARD.md` → calibration row cites `→ 42`;
`git ls-tree --name-only b89bdab2 corpus/lessons/ | grep -c verifier-spotcheck` → `43`.
Verdict: the sole frozen mismatch is the stale calibration literal (`42` vs `43`). `caps=0`; the
canonical-capability predicate is not the failing check at base.

## 2. C2 — after state, and `maxN` instability

| Tip | Stdout | Exit |
|---|---|---|
| `7b74e2f25` | `r41=0 ... mismatches=0 maxN=56 met=True` | 0 |
| `77e7f5ee` | `r41=0 ... mismatches=0 maxN=57 met=True` | 0 |
| `8a7f1976` | `r41=0 ... mismatches=0 maxN=57 met=True` | 0 |

`maxN` moved 56 → 57 with no change to any measured file: it is `max(re.match(r"^## Round (\d+)", l))`
over the whole SCORECARD (`tools/round42-selfdesc-reconcile.py:167-168`), so appending the
`## Round 57` section changed only that field. The C2 predicate (`mismatches`) did not depend on it.

## 3. C2 — the counter's target is still forgeable (no-op)

Observed while the frozen control existed in the worktree: `python3
.ufo/waves/round-57/controls/c1-noop.py` printed `mismatches=0 maxN=46 met=True`, exit 0.
`controls/noop-c2.out` records `canonical_table_reads=0`, `self_description_reads=0`, summary
`mismatches=0 maxN=46 met=True`, `exit=0`.

These files were later deleted from the working tree by another seat (`git status` shows
`D .ufo/waves/round-57/controls/{c1-noop.py,noop-c1.out,noop-c2.out}` at observation end) and a new
`controls/noop-fixture/` directory appeared; both blobs and outputs remain committed at `89dc4f52`.
Exact frozen bytes archived at `case7-receipts/frozen-{c1-noop.py,noop-c1.out,noop-c2.out}`
(`git show 89dc4f52:.ufo/waves/round-57/controls/<name>`).

Verdict: the `mismatches=0 met=True` target is reachable by a three-line script that reads no input.
C2 is a stale-fact correction, not counter fidelity; the round-56 §9 do-nothing rule applies to any
reading that treats it as fidelity.

## 4. C1 (operability) — before/after and the limit of "executed"

Fixtures built under `/fast/scratch/hyaku/kama-r57/S02LessonDraft/` (git toplevel asserted equal to
the fixture directory before every fixture commit; scratch removed after the receipts were copied).
Each fixture carries the round-56 `preregistration.json` blob and a battery whose `ROSTER` literal is
byte-identical to the roster records; only `main()` differs.

`fixture-noop` battery body (verbatim):
```python
def run(label):
    return label


def assert_mutant_breaks_detection(label):
    return label


ROSTER = {
    "base-old-counter": {"designation": "control", "expected": "missed"},
    "round56-counter": {"designation": "positive-control", "expected": "detected"},
    "m-drop-ldaudit": {"designation": "kill", "expected": "missed"},
}


def main():
    return 0
```

`fixture-static-calls` battery `main()` (verbatim; calls statically present, never executed):
```python
def main():
    if False:
        run('base-old-counter')
        run('round56-counter')
        assert_mutant_breaks_detection('m-drop-ldaudit')
    return 0
```

Checker blobs: old = `7c873d7b:tools/round56-prereg-check.py`, SHA-256
`c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853`; new =
`7b74e2f25:tools/round56-prereg-check.py`, SHA-256
`dee6f922d0d93b10512f9a799b94f36a1e0f080404a525e08121a223b2e90ced`.

| Case | Command | Stdout | Exit | Receipt |
|---|---|---|---|---|
| before, no-op | `python3 old-checker.py --repo fixture-noop --tip HEAD` | `present=1 roster_match=1 kills=1 controls=2 met=True` | 0 | `case7-receipts/old-checker_noop.txt` |
| after, no-op | `python3 new-checker.py --repo fixture-noop --tip HEAD` | `present=1 roster_match=1 kills=1 controls=2 met=False` | 1 | `case7-receipts/new-checker_noop.txt` |
| after, genuine | `python3 new-checker.py --repo <lane> --tip 7b74e2f25` | `present=1 roster_match=1 kills=1 controls=2 met=True` | 0 | `case7-receipts/new-checker_genuine.txt` |
| after, static-only calls | `python3 new-checker.py --repo fixture-static-calls --tip HEAD` | `present=1 roster_match=1 kills=1 controls=2 met=True` | 0 | `case7-receipts/new-checker_static-calls.txt` |

Verdicts:
- The frozen C1 predicate is reproduced: matching-roster no-op `met=True`/0 → `met=False`/1; genuine
  battery `met=True`/0.
- The repair binds an **AST call-site inventory**, not execution: a battery whose only calls sit under
  `if False:` is accepted. The checker's local is named `executed`
  (`tools/round56-prereg-check.py:61-71`), which overstates the binding. SCORECARD §Round 57 limits
  the claim to "call-site inventory in the committed battery AST"; any "executed entries" reading is
  falsified by the static fixture.

## 5. S515 non-author spot-check (re-opened live this round)

Fetched `https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT` on
2026-10-27 (native fetch). Page carries `git-config last updated in 2.56.0`.
Located passage at §`GIT_CONFIG_COUNT`:
"all environment pairs GIT_CONFIG_KEY_<n> and GIT_CONFIG_VALUE_<n> up to that number will be added to
the process’s runtime configuration" — **18 words** (whitespace-delimited), byte-equal to
`corpus/lessons/round-56.md:18` and `corpus/SOURCES.md:268` modulo the HTML line break.
Snapshot cross-check: `.ufo/waves/round-56/sources/git-docs-git-config.html` contains
`all environment pairs`. Row S515: tier `B`, status `mined`, `used-by` `corpus/lessons/round-56.md`.
Verdict: supported. This seat is a lane author; this is advisory evidence for the non-author closure,
not the outside spot-check itself.

## 6. S516 (own-work source row) — quote present, word count wrong

Filed Gate text (committed, `corpus/lessons/round-57.md:14` at `8a7f1976`) quotes
`results.append(run("base-old-counter", OLD, "missed", OUT / "base-c1.out"))` and states
"(5 words)".
Independent checks:
- The quote is a byte substring of `tools/round56-env-leg-battery.py` at base `b89bdab2`, at line 70
  (inside the cited `main()` lines 69–83 range).
- Whitespace-delimited tokens of the quote:
  1. `results.append(run("base-old-counter",`
  2. `OLD,`
  3. `"missed",`
  4. `OUT`
  5. `/`
  6. `"base-c1.out"))`
  = **6**, not 5. The lane's own convention counts whitespace-delimited words: `corpus/SOURCES.md:194`
  says "(17 whitespace-delimited words)" for its own-work docstring quote, and S512/S514/S515 doc
  quotes count the same way.
- The ≤25-word limit is unaffected (6 ≤ 25); the S516 admit itself stands (quote located, own-work
  tier consistent with precedent S194; `corpus/SOURCES.md` count 256 → 257, one added row, no existing
  cell changed: `git diff b89bdab2 8a7f1976 -- corpus/SOURCES.md` is one insertion).
Verdict: a one-word documentation error in the filed Gate; append a correction.

## 7. S513 disagreement (round-56 outside discernment defect)

`corpus/lessons/round-56-verifier-spotcheck.md:30` marks S513 `disagree`; `:39` says "this outside
sample disagrees with the S513 rejection, and the lesson contains no learned correction/grounded new
QUALITY criterion."
Committed snapshot `.ufo/waves/round-56/sources/ld.so.8.html`:
`Dynamic string tokens` ×4, `dynamic string tokens` ×1, `secure-execution` ×11,
`Secure-execution` ×1, `LD_AUDIT` ×5.
`corpus/lessons/round-56.md:15` names S513's flip as "secure-execution, dynamic string tokens, or
loader namespace semantics" — the same topics present in the rejected source.
Verdict: reproducible. The filed lesson row `discernment-disagreement` records the disagreement; the
counts and the criterion hold are not in it.

## 8. Round-56 defect 4 — append-only audit and invalid declarations

Committed receipt `.ufo/waves/round-56/measured/append-only-audit-at-784.out`:
`... unrestored=2 ... bad_declarations=4`, `threshold=1 exit=1`, naming
`SCORECARD.md -> corpus/README.md:761; corpus/QUALITY.md -> corpus/README.md:761; corpus/README.md ->
corpus/README.md:761; corpus/lessons/*.md -> corpus/README.md:1239`.
Read of the pointed lines: `corpus/README.md:761` is release-pin prose; `:1239` is a "Carried over
unchanged" bullet. Neither declares the corresponding file(s) append-only.
Verdict: reproducible; no round-57 repair exists.

## 9. Citation-at-tip and the counter's coverage gap

`SCORECARD.md` §Round 57 at `8a7f1976` cites three tokens; the counter's own `expand()` (brace
expansion) resolves four paths, and every expanded path exists at that tip:
```
OK .ufo/waves/round-57/controls/base-c1.out
OK .ufo/waves/round-57/measured/c2-committed-tip.out
OK .ufo/waves/round-57/measured/noop-c1.out
OK .ufo/waves/round-57/measured/c1-committed-tip.out
```
Verdict (gate): citations are sound at this tip. Limit: `tools/round42-selfdesc-reconcile.py` checks
cited receipts only for `RECEIPT_ROUNDS = (40, 41)` (defined `:75`; the filter and existence check are
`:240-251`); its `receipts=0` says nothing about round-57 citations, so the per-path
`git cat-file -e` check above must be run by hand (or by the closure) at the final tip.

## 10. Claim-text precision test (`maxN`, canonical rows, "expected 46")

- `maxN` is the maximum `## Round N` heading across SCORECARD (`tools/round42-selfdesc-reconcile.py:167-168`);
  observed 56 before the §Round 57 section, 57 after.
- `maxN=46` occurs in the wave only as the hardcoded literal of the do-nothing control
  (`controls/c1-noop.py:3`, `controls/noop-c1.out:3`, `controls/noop-c2.out`); no counter, SCORECARD
  field, or receipt expects `46` (`grep -rn "expected 46" SCORECARD.md tools/` → no match).
- Canonical capability selection at base: `canon()` → heading round `49`, 11 rows
  (`sources-registry` … `live-receipt-replay`); frozen base output `caps=0`.
Verdict: the seat-context sentence "C1 calibration … stale canonical capability row count … maxN=56
instead of expected 46" is not derivable from any frozen artifact: the axes are swapped relative to
`controls/freeze-amendment.txt` and the lesson, `caps=0`, and `46` is a fixture literal.

## 11. Axis-authority conflict (round-56 defect 1)

- `MISSION.md:29`: `kama:       { cwd: kama-shokunin/,   axes: "operability + freshness (local model serving/endpoints)" }`
- `shokunin.conf:52`: `kama|kama-shokunin|operability + calibration (local model serving and endpoint health)`
Recorded; not resolved by this seat.

## Receipts

- `.ufo/waves/round-57/reports/case7-receipts/{old-checker_noop,new-checker_noop,new-checker_genuine,new-checker_static-calls}.txt` (this seat's runs)
- `.ufo/waves/round-57/reports/case7-receipts/frozen-{c1-noop.py,noop-c1.out,noop-c2.out}` (`git show 89dc4f52:...` copies)
- Fixture bodies are embedded verbatim in §4; scratch fixtures were removed after the receipts were
  copied into the wave path.
