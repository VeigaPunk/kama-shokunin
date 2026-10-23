# VerifyRow07 — correction row 7 hand verification

Seat: kama-r29-w2-VerifyRow07 · 2026-10-23 · No subagents used. The frozen counter was NOT executed; every check below is hand-derived (git plumbing only).

## Verdict

```json
{"sid": "SA29:SCORECARD.md:Q:4c5d902830:0", "verdict": "confirmed-false", "observed": "q:no-artifact"}
```

The correction row's last cell equals the hand-derived observed value exactly.

## Evidence trail

### 0. Preconditions
- Counter hash: `sha256sum .ufo/waves/round-29/count-c1.py` → `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` — matches the frozen value.
- Commits resolve: base `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d`, data `513eba3ba51a142c9936553e3a85918345eb5c4c`, controls `35b90184f638ab6a4149092b93143c7a2b873787`, freeze `827d136546b85059a984b34970f5b493d9a71290`.

### 1. Correction row (data commit `513eba3b`, SCORECARD.md:1460, under `## Round 29 — self-assessment corrections`)
```
| SA29:SCORECARD.md:Q:4c5d902830:0 | SCORECARD.md:824 | Q | `required=3 found=3 verified=3 missing=0 mismatch=0` | 7229fa95 | quoted citation-provenance after-run; no committed file at W holds this text | q:no-artifact |
```
Sid occurs exactly 1× in the file at `513eba3b` (no duplicate).

### 2. Base statement
`git show 2aa46e2481d2:SCORECARD.md` line 824 (matches the row's "line at base" cell):
```
`required=3 found=3 verified=3 missing=0 mismatch=0` exit 0, selftest 5 cases.
```
- Line content hash (no trailing newline, per extractor): sha256 = `4c5d902830bd68394940a2e66cb0b93411afa1ac1308962e82179a7c34b16022` → first 10 hex `4c5d902830` = sid field 4. ✓
- Q-class qualification by hand: span 51 chars (6–200 ✓); contains digits ✓ and `=` ✓; starts with none of python3/python/bash/"sh "/git/node/./tools/// ✓. It is the line's only backticked span (2 backticks total) → index k=0. ✓ Checkable Q statement, per the frozen docstring rule and `extract()` (`sid = f"{fname}:{cls}:{lsha}:{k}"`).
- Line unchanged at data commit: line 824 of `513eba3b:SCORECARD.md` hashes identically (`4c5d902830bd…6022`) — append-only holds for this statement.

### 3. Writing revision W
`git blame --line-porcelain 2aa46e2481d2 -L 824,824 -- SCORECARD.md` →
```
7229fa95eb122310e9e5334ad799ee3006293ebd 824 824 1
summary round-19: citation provenance, install-tree pin, r18 defect corrections
	`required=3 found=3 verified=3 missing=0 mismatch=0` exit 0, selftest 5 cases.
```
W = `7229fa95eb122310e9e5334ad799ee3006293ebd` (committer time 2026-10-21 03:34:47 -0300, parent `8bf99cae`). The row's W cell `7229fa95` matches blame exactly. ✓

**Note on the item wording** ("confirm W's prefix matches the sid"): per the frozen extractor, the sid's 4th field is the *statement line's* sha256 prefix, not W's prefix. The correct correspondence — both verified — is lsha `4c5d902830` (sid) and W `7229fa95` (row cell 5). No defect in the data; the item instruction misdescribed the sid format.

### 4. Q rule applied by hand at W — observed value
Rule (count-c1.py docstring): the span must occur verbatim in ≥1 blob of the tree at W other than SCORECARD.md, SHONEN.md, LOG.md, corpus/**; else `q:no-artifact`. The counter's `check()` implements this as `git grep -F -q -e <span> W -- . :(exclude)SCORECARD.md :(exclude)SHONEN.md :(exclude)LOG.md :(exclude)corpus`; I ran the identical grep by hand (counter not executed):
- With the counter's excludes: exit **1** → no committed artifact at W holds the span → statement **FALSE at W** → observed = **`q:no-artifact`**.
- Whole tree, no excludes: the span occurs at W **only** in `7229fa95:SCORECARD.md` (the claiming file itself) — corroborates the row's cause text ("no committed file at W holds this text").
- Span contains no newline, so line-wise grep ≡ whole-blob substring search; result is exact.

### 5. Row cell equality
Row last cell `q:no-artifact` == hand-derived observed `q:no-artifact` — exact string. ✓

## Conclusion
Row 7 is a valid correction: the base statement (Q, SCORECARD.md:824) is false at its writing revision `7229fa95`, and the row's last cell reproduces the observed value exactly. Sid fields, base line number, class, statement token, and W cell all check out; no duplicate row.

## Residual risk / gaps
- I verified this one row only, not the other 10 (sibling seats own those) or the aggregate receipt.
- The counter itself was never executed (by design); if the frozen binary diverged from its docstring, my docstring+`check()` reading could diverge with it — mitigated by the sha256 match and by reading `check()`'s actual grep line, which my hand run reproduces parameter-for-parameter.
- Append-only was spot-checked for this statement's line only, not the whole file prefix.

## Tooling
No tools installed (existing git/sha256sum sufficed). No pacman used. No lane file mutated; scratch work was read-only git queries.
