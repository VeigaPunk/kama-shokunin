# Frontier step (proposed, not committed) — SOURCES rows S519–S521

Seat: SE01PredicateSandbox (round 60, kama, wave w1). The lane tree is read-only for
this seat, so these rows are **drafts for the L1 to integrate**, not lane edits.
Census arithmetic: `grep -c "^| S[0-9]" corpus/SOURCES.md` = **259** at base
`ec3b0d58`, next free id **S519**; integrating all three takes the census to 262
(the round-end census must still exit 0 — `tools/sources-census.py`, not run here).

All three URLs were opened live on 2026-10-27 with
`curl -sSL --max-time 40 -o <snapshot> <url>`; the byte-identical HTML snapshots are
copied to `.ufo/waves/round-60/w1/out/SE01PredicateSandbox/repro/doc-snapshots/`
with sha256s in `repro/doc-snapshots.sha256`:

```
3c57ac0d27e0558ca5c2f5981e5726b3025bfe0cd8fa4511e49cce7a8ddb9492  https___docs.python.org_3.14_library_functions.html.html
b3c32f4931ad67ef8acb5d8f7c8a919b23f0810aaff3a23c1b97ca28e98d7dba  https___docs.python.org_3.14_reference_expressions.html.html
31933f6463c45f99a49f09c071bce1a3d574c103db74c7f0cabe6fe1968a07d0  https___docs.python.org_3.14_whatsnew_3.12.html.html
```

## Ready-to-paste rows

| S519 | Python 3.14 library reference, `eval` — https://docs.python.org/3.14/library/functions.html#eval | docs | A | namespace semantics of `eval()` in a restricted evaluator: whether overriding `__builtins__` is a security boundary | §eval, Python 3.14 documentation, fetched 2026-10-27 (HTML sha256 `3c57ac0d…b9492`), quoted: "Overriding `__builtins__` can be used to restrict or change the available names, but this is not a security mechanism: the executed code can still access all builtins." | A restricted evaluator cannot rest on `{"__builtins__": {}}`; only the admitted syntax and the admitted names bound its reach, and every name the allowlist admits is fully reachable from inside the expression | mined | 2026-10-27 | on-release | corpus/knowledge/predicate-sandbox-limits.md; .ufo/waves/round-60/w1/out/SE01PredicateSandbox.md (findings F2, verdict) |
| S520 | Python 3.12 release notes, PEP 709 comprehension inlining — https://docs.python.org/3.14/whatsnew/3.12.html#pep-709-inlined-comprehensions | docs | A | which comprehension forms share the enclosing frame and which keep a function scope, for code `eval()`uated with separate globals and locals | §PEP 709, fetched 2026-10-27 (HTML sha256 `31933f64…a07d0`), quoted: "Dictionary, list, and set comprehensions are now inlined, rather than creating a new single-use function object for each execution of the comprehension." and "Comprehension iteration variables remain isolated and don't overwrite a variable of the same name in the outer scope, nor are they visible after the comprehension." | List/dict/set comprehensions are inlined into the enclosing frame, so a name supplied only as `eval`'s `locals` is visible inside them; generator expressions are absent from that list and keep their own frame — the asymmetry that makes `any(<c-expr> for x in …)` resolve `c` differently from `[<c-expr> for x in …]` | mined | 2026-10-27 | on-release | corpus/knowledge/predicate-sandbox-limits.md; .ufo/waves/round-60/w1/out/SE01PredicateSandbox.md (finding F3) |
| S521 | Python 3.14 language reference, generator expressions — https://docs.python.org/3.14/reference/expressions.html#generator-expressions | docs | A | generator-expression execution model: a genexp evaluates to a generator iterator, "roughly equivalent to defining and calling" a generator function | §6.2.9, fetched 2026-10-27 (HTML sha256 `b3c32f49…98d7dba`), quoted: "At runtime, a generator expression evaluates to a generator iterator which yields the same values as the corresponding list comprehension" and "roughly equivalent to defining and calling the following generator function" | A genexp body runs in a function-like frame with its own name resolution; the deferred body therefore does not see a caller's local mapping, only globals/builtins. Pairs with S520 to explain why `c` supplied as `eval` locals raises `NameError` inside a genexp body but not inside a list comprehension | mined | 2026-10-27 | on-release | corpus/knowledge/predicate-sandbox-limits.md; .ufo/waves/round-60/w1/out/SE01PredicateSandbox.md (finding F3) |

## Notes for the integrator

- None of the three rows is claimed as a C2 predicate row; they source the *instrument
  limits* knowledge entry, and S519 is the sentence that says the counter's builtins
  override is not what keeps it safe.
- The `teaches` column deliberately states what the lane may *infer*, not just the
  page topic: S519 forbids the inference "an empty `__builtins__` makes this a
  sandbox"; S520/S521 forbid the inference "the same expression resolves `c` the same
  way in every comprehension form".
- `status` is `mined` (the pages were opened and the statements were exercised against
  the counter in this seat); no upstream revision pin is available for docs.python.org,
  so `recheck` is `on-release` per the S001 precedent.
- If the L1 prefers a single row, S520 carries the load-bearing asymmetry and S519 the
  load-bearing safety statement; S521 is the mechanism. Dropping S521 would leave the
  genexp-frame claim sourced only by absence from a list.
