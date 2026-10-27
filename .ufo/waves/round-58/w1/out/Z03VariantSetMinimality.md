# Round 58 Z03 — do the 11 no-op variants add distinct coverage?

Verdict: **C1 not falsified** — the frozen predicate holds (11/11 rejected, 0 errors, `met=True`).
Finding is a **coverage-minimality LIMIT**, not a predicate change: 10 of the 11 variants are
rejected by the single clause `executed`, 7 of them with byte-identical checker-observable output.

## Evidence (exact commands, exit codes)
- `python3 tools/round58-c1-counter.py --repo <clone> --tip e4891d8a4c9c70e97124980c2ec9aee5762a7f0a --checker-blob e4891d8a...:tools/round58-battery-exec-check.py` → `genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True`, rc=0 (receipt `counter-receipt.txt`).
- Same counter with base `--checker-blob 2f53614e...:tools/round56-prereg-check.py` → `genuine=1/1 benign=1/3 noop_rejected=1/11 met=False`, rc=1 — reproduces the frozen before-row exactly (`base-through-counter-receipt.txt`), so this fixture pipeline matches the frozen counter's semantics.
- Per-variant: one throwaway fixture per variant from frozen blobs (`git init -q` under scratch, `--show-toplevel` asserted, every git call `-C <fixture>`), then `python3 CHECKER --repo <fixture> --tip HEAD`; frames from the checker's own `--harness` mode; single-conjunct ablations of a **scratch copy** of the checker (anchor counts asserted ==1), original blob never edited. Exit 0=accept, 1=reject: `matrix.txt`, `results.json`, `harness/*.json`.

| variant | rc | roster_match | kills | controls | executed | legs | assert frames(sub) | false conjunct(s) of executed | single-conjunct flip |
|---|---|---|---|---|---|---|---|---|---|
| N01-calls-removed | 1 | 1 | 1 | 2 | 0 | 0/3 | 0 | legs + assert_ok | executed |
| N02-if-false | 1 | 1 | 1 | 2 | 0 | 0/3 | 0 | legs + assert_ok | executed |
| N03-unused-function | 1 | 1 | 1 | 2 | 0 | 0/3 | 0 | legs + assert_ok | executed |
| N04-early-return | 1 | 1 | 1 | 2 | 0 | 0/3 | 0 | legs + assert_ok | executed |
| N05-env-guard | 1 | 1 | 1 | 2 | 0 | 0/3 | 0 | legs + assert_ok | executed |
| N06-run-body-noop | 1 | 1 | 1 | 2 | 0 | 0/3 | 1 (sub 1) | legs | executed, legs |
| N07-mutant-assert-noop | 1 | 1 | 1 | 2 | 0 | 3/3 | 1 (sub 0) | assert_ok | executed, assert_ok |
| N08-main-not-invoked | 1 | 1 | 1 | 2 | 0 | 0/3 | 0 | legs + assert_ok | executed |
| N09-empty-loop | 1 | 1 | 1 | 2 | 0 | 0/3 | 0 | legs + assert_ok | executed |
| N10-run-rebound | 1 | 1 | 1 | 2 | 0 | 0/3 | 1 (sub 1) | legs | executed, legs |
| N11-try-else | 1 | 1 | 1 | 2 | 0 | 0/3 | 0 | legs + assert_ok | executed |

Clauses: `met = roster_match AND executed AND kills==1 AND controls==2`; `executed = bool(expected) AND expected<=ran AND assert_ok`.

## Findings
1. **Which clause alone rejects each variant**: for all 11 the sole false top-level clause is `executed` (ablating it alone flips every variant to accept). None of the 11 moves `roster_match`, `kills`, or `controls` — the claim's "roster literal intact" is confirmed.
2. **Executed sub-conjunct attribution**: N01–N05, N08, N09, N11 falsify `legs` **and** `assert_ok` jointly (forcing either alone still rejects; the assert leg is never invoked). N06 and N10 falsify `legs` alone; N07 falsifies `assert_ok` alone.
3. **Redundant variants (reported, not deleted)**: N01, N02, N03, N04, N05, N08, N09, N11 produce byte-identical harness payloads (`sha256 f62d79caabe4`) and an identical verdict line (`legs=0/3 mutant_assert=0`) — 8 distinct source shapes of one runtime state (the leg block never executes), so 7 add no discriminator for this checker. N06 and N10 share that verdict line and flip set but differ in frames (3 `run` frames with 0 `--counter` invocations vs. no `run` frame), so their redundancy holds only at clause/verdict granularity. **N07 alone adds a discriminator no other variant exercises** (sole witness of `assert_ok`: ablating it accepts N07 and nothing else).
4. Minimal representative set preserving every observed signature: 4 (one 8-class member, N06, N10, N07); preserving only the printed verdict line: 3. The predicate requires 11/11 and the set is frozen — no deletion proposed.
5. The 8-class members are **not** mutually redundant as a regression corpus: the round-57 syntactic checker accepts N02, N03, N04, N05, N08, N09, N11 (rejecting only N01), so 7 of them individually witness the r57→r58 fix while sharing one r58 observable.

## Limits (seat-found, no predicate change)
- `tools/round58-c1-counter.py` discards the checker's stdout (verdict by exit code only), so its `detail:` lines cannot attribute a rejection to a clause; per-clause attribution requires re-running the checker over fixtures as done here.
- No variant exercises the `roster_match`, `kills`, `controls`, missing-blob, or parse-error paths; that coverage rests on the committed do-nothing controls, not on this set.
- The 8-way collapse is a property of execution-bound observables, not a claim that the mutations are semantically equivalent (they differ textually and 7/8 differ under the base checker).

Attacks: C1 claim's variant-set coverage-minimality and the frozen counter's attribution granularity; the C1 verdict itself is reproduced intact. No tool installs; scratch removed; lane read-only (blobs via `git show`) and no production file touched.
