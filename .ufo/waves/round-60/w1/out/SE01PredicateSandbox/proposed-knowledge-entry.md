source: S519 (Python 3.14 `eval` namespace semantics), S520 (PEP 709 comprehension inlining), S521 (generator expressions); own-work: tools/round60-c2-counter.py at lane tip 11f2d667, exercised in `.ufo/waves/round-60/w1/out/SE01PredicateSandbox/repro/`
verified-at: 2026-10-27 — counter tip 11f2d667, host CPython 3.14.8, probes run under `ulimit -v 2000000` and `timeout 10`
recheck: on-release — re-run `.ufo/waves/round-60/w1/out/SE01PredicateSandbox/repro/attack-matrix.tsv` against any change to safe_compile/evaluate/ALLOWED_NODES/ALLOWED_CALLS; reopen S519–S521 when the Python pages change

# A restricted-expression counter is bounded by its grammar, not by its builtins override

`tools/round60-c2-counter.py` runs lane-authored predicate text with
`eval(compile(tree, "<pred>", "eval"), {"__builtins__": {}, **ALLOWED_CALLS}, {"c": caps})`
after an AST allowlist pass. This entry records what that construction actually
guarantees, so a later reader does not credit it with safety or with coverage it does
not have.

## The builtins override is not the boundary (S519)

S519 is explicit that overriding `__builtins__` "can be used to restrict or change the
available names, but this is not a security mechanism: the executed code can still
access all builtins." The counter's safety therefore rests entirely on two things:
`ast.Attribute` is refused, and a `Call` is refused unless its callee is a bare `Name`
among eleven whitelisted builtins. Remove either and the empty `__builtins__` buys
nothing.

Measured on the tip: `__import__('os').system('id')` → `call not allowed`;
`c.__class__` and `(x for x in c).gi_frame` → `node Attribute not allowed`;
`len.__globals__` → `node Attribute not allowed`; `'x'.upper()` and `'-'.join(...)`
→ `call not allowed`; `__import__` alone → `dunder name`; `getattr`, `compile`,
`hash`, `id`, `repr`, `frozenset` → `call not allowed`. String-subscript tricks
(`c['__builtins__']`, `str(c)['__class__']`) pass the allowlist and then die on
`KeyError`/`TypeError`; `isinstance(c['x'], type)` dies on `NameError` because `type`
is not in scope. Subscripting a builtin *type object* is legal in 3.9+
(`list[int]`, `dict['x']` → truthy `GenericAlias`; `str[0]` → `TypeError`), which makes
a tautology that is then refused by the falsifiability gate, not by the allowlist.

## Comprehension forms do not resolve `c` alike (S520, S521)

`evaluate` supplies `c` only in the *locals* mapping. S520 says dict/list/set
comprehensions are inlined into the enclosing frame; S521 says a generator expression
is a function-like frame. The consequence is that a genexp body that reads `c` raises
`NameError: name 'c' is not defined`, while the same expression inside a list
comprehension works:

```
any(x for x in c['version'])            -> True         (iterable of the outermost for
                                                        is evaluated in the enclosing frame)
any(c['version'] for x in c['version']) -> NameError    (body runs in the genexp frame)
all(all(y for y in c['version']) for _ in c['version']) -> NameError
[ c['version'] for _ in c['version']]   -> True         (PEP 709 inlined)
```

`evaluate` swallows that `NameError` into `None`, and `score()` treats `None` as a row
to skip **without counting an error**. A lane reading `errors=0` has not been told that
one of its live rows was never evaluated. Putting `c` into the globals mapping makes
all six forms evaluate and changes nothing else in the grammar.

## What multiplies work, and what cannot

- Banned by the allowlist: `BinOp` (so `[0]*10**9`, `10**9`, string repetition),
  `Lambda`, `Starred`, `keyword`, `NamedExpr`, `JoinedStr`, `Dict`, `Attribute`.
  A multiplication/exponent allocation bomb is therefore impossible.
- Admitted and multiplying: nested comprehensions. Three levels over the receipt's
  512-element `show.model_info['tokenizer.ggml.tokens']` is 181 bytes of registry text,
  costs 1.95 s per evaluation and needs more than 600 MB (MemoryError at
  `ulimit -v 600000`); four or five levels do not complete in 10 s.
- The control suite re-evaluates every predicate many times: measured 2912 `evaluate`
  calls for a 14-row registry over a 14-line population (208 per row), growing roughly
  as `10R² + 5RP`. One slow predicate therefore costs its per-evaluation time times
  ~200. Measured end to end: a 14-row registry with cheap predicates 418 ms; the same
  registry with one 181-byte nested-comprehension row 254 859 ms — both `met=True`.

## Crash paths (rejection vs. crash)

`safe_compile` calls `ast.parse` and `score` catches only `(SyntaxError, ValueError)`.
CPython 3.14 raises `RecursionError` for deeply nested subscriptions and `MemoryError`
("Parser stack overflowed") for a long `not` chain; both escape the counter, which
then exits 1 with a traceback and prints no verdict line and runs no controls. Nested
parentheses, by contrast, raise `SyntaxError` and are counted as `errors`. Separately,
`receipt_caps` parses each capture body with `json.loads` and catches `ValueError` only:
a schema-correct, hash-correct receipt whose body nests arrays ~200k deep crashes the
counter the same way. A body that simply fails to parse is silently dropped while
`receipt_ok` stays 1 — the committed receipt already has one (`root`).

## Rules for a predicate author

1. Put the capture namespace where comprehension frames can see it; prefer a
   single-level list/set comprehension or a genexp whose body does not touch `c`.
2. Keep the predicate well under a few hundred AST nodes; do not nest comprehensions.
3. `not`, `and`, `or`, comparisons, `in`, `is`, conditional expressions, subscripts and
   slicing are admitted; negative literals (`-1`), `{}` literals and keyword arguments
   (`sorted(..., key=…)`) are not.
4. A subscript chain that ends in a slice (`c['a'][:5]`) yields no chain for the
   falsifiability mutation, so the row is never credited — slice after the chain, not
   inside it.
5. Treat `errors=0` as "no rejection recorded", never as "every row was evaluated";
   `silent` (rows whose predicate evaluated to `None`) is the missing counter.

## Limits

Measured on one host CPython (3.14.8) and one committed receipt; the comprehension
inlining asymmetry is a 3.12+ behaviour and the parser exception types are
implementation-defined. Nothing here is a claim that the evaluator is sandboxed, nor
that a met verdict from this counter is safe to run on a registry from an untrusted
author.
