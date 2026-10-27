# SE01PredicateSandbox — attack on the restricted predicate evaluator

Round 60, kama, wave w1 — advisory leaf. Axes: operability (hold), calibration (the seat's judged
axis, 7). Base `ec3b0d583ed4eb05c7ae935dc59f560e86b0a80b`, freeze commit
`e0b5b1ead9adb7a5a4744caca8837ec6496e1ca1`, controls commit
`8b9f3060966c22bede3094d748974caf041b4c33`, tip under test
`11f2d667f8bd89d127a4fb81dab44007c4c86c7f` (`tools/round60-c2-counter.py`, sha256
`d2e9a722416b8e482224dc2e6e17ced14bb87fb0ebd7de4464b04776b86a8fe5`).

Scope: `safe_compile`, `evaluate`, `ALLOWED_NODES`, `ALLOWED_CALLS`, and every other path in the
counter that executes registry or receipt text. No lane edits were made; the tip file was copied to
scratch (`git show 11f2d667:tools/round60-c2-counter.py`) so that importing it never created
`__pycache__` inside the lane. Every probe ran as
`( ulimit -v 2000000; timeout 10|20|300 python3 -B <driver> <case> )`; nothing ran unbounded, and
fixture repos were created with `git -C "$D" init -q` after asserting
`git -C "$D" rev-parse --show-toplevel` equals `$D`, with the throwaway identity passed per command
(`-c user.name=fixture -c user.email=fixture@localhost`) and never written to any config.

## 1. Headline

**No sandbox escape.** Seventy-seven probe expressions across the named vectors — generator-expression
frames, subscript on builtins, str methods through allowed calls, comprehension-variable shadowing of
`c`, `[0]*10**9`-style allocation and exponent bombs, deep nesting, `sorted` with a key, `isinstance`
on type objects, dunder through string subscripts — produced **no** reachable builtin, frame object,
attribute, filesystem, network or import path. The allowlist holds because `ast.Attribute` and non-Name
callees are refused, and the builtins mapping is empty.

**Three defects, all on availability and calibration, not on code execution.** They are worth more
than an escape would be for this axis, because the closure judge re-runs the counter and reads one
output line:

| id | severity | one-line |
|---|---|---|
| F1 | high | a registry row can crash the counter with an uncaught `RecursionError`/`MemoryError` from `ast.parse`; exit 1, traceback, **no verdict line, controls never run** |
| F2 | high | nested comprehensions are an exponential work amplifier inside allowed nodes; **418 ms → 254 859 ms (610×)** from one 181-byte row, and the verdict is still `met=True` |
| F3 | medium | a generator expression that reads `c` evaluates to `None` and is **silently dropped with `errors=0`** — the row is never judged, so it can never be contradicted |
| F4 | medium | a schema-correct, hash-correct receipt whose capture body nests arrays ~200k deep crashes `receipt_caps` (uncaught `RecursionError`); unparsable bodies are silently dropped while `receipt_ok=1` |
| F5 | low | the admitted grammar is narrower than the docstring implies (`-1`, `{}`, `key=`, `min/max/sum`, slice-in-chain) → loud `errors=1` or silent drop; and the gate over-credits pure emptiness tests |

## 2. What held — attempts and outcomes

Full machine-readable matrix: `repro/attack-matrix.tsv` (77 rows: case, expression, `safe_compile`
outcome, rejection node, `evaluate`, `falsifiable`, timings). Selected attempts, all at the tip:

| attempt | expression | outcome |
|---|---|---|
| import | `__import__('os').system('id')` | **rejected** `ValueError: call not allowed` |
| dunder name | `__import__` | **rejected** `ValueError: dunder name` |
| attribute on a builtin | `len.__globals__` | **rejected** `node Attribute not allowed` |
| attribute on a capture | `c.__class__` | **rejected** `node Attribute not allowed` |
| genexp frame | `(x for x in c).gi_frame` | **rejected** `node Attribute not allowed` |
| str method via allowed call | `'x'.upper()`, `'-'.join(c['version'])` | **rejected** `call not allowed` |
| `getattr`/`compile`/`hash`/`id`/`repr`/`frozenset` | `getattr(c,'version')` … | **rejected** `call not allowed` |
| `sorted` with a key | `sorted(c['tags']['models'], key=str)` | **rejected** `node keyword not allowed` |
| `sorted(..., reverse=True)` | — | **rejected** `node keyword not allowed` |
| huge exponent / allocation | `10**9`, `[0]*10**9` | **rejected** `node BinOp not allowed` |
| lambda | `(lambda: 1)()` | **rejected** `call not allowed` |
| walrus | `(x := 1)` | **rejected** `node NamedExpr not allowed` |
| f-string | `f'{c}'` | **rejected** `node JoinedStr not allowed` |
| starred / kwargs | `len(*c)`, `len(**c)` | **rejected** `node Starred` / `node keyword` |
| dict literal | `c['version'] == {}` | **rejected** `node Dict not allowed` |
| subscript on builtins | `str[0]` | **accepted**, then `TypeError` → `None` |
| subscript on builtins | `list[int]`, `dict['x']` | **accepted**, returns truthy `GenericAlias`; tautology → `falsifiable=False` → row refused |
| subscript on builtins | `isinstance[0]` | **accepted**, `TypeError` → `None` |
| dunder via string subscript | `c['__builtins__']` | **accepted**, `KeyError` → `None` |
| dunder via string subscript | `str(c)['__class__']` | **accepted**, `TypeError` → `None` |
| `isinstance` on type objects | `isinstance(c, type)` | **accepted**, `NameError` → `None` (`type` is out of scope) |
| shadowing `c` | `[c for c in c['tags']['models']]` (eval `True`, falsifiable `True`); `[c['version'] for c in c['tags']]` (eval `None`: the shadowed `c` is a key string); `[c for c in [1,2]]` (eval `True`, falsifiable `False` → refused) | **accepted**; shadowing stays local to the comprehension, the iterable still reads the outer `c`; no escape |
| generator-expression frames | `any(x for x in c['version'])` | **accepted**, `True` — the outer iterable is evaluated in the enclosing frame |
| generator-expression frames | `any(c['version'] for x in c['version'])` | **accepted**, then `NameError` swallowed → `None` (**F3**) |

Tautologies that the falsifiability gate refuses (`falsifiable=False`, so the row is not credited):
`True`, `[0]`, `len`, `list[int]`, `dict['x']`, `{1} == c['version']`, `str(c)`, `(x for x in …)`,
`sorted((1,2))`, `any([1]) or c['version']`, `c['version'] is not None or True`,
`len(c['version']) == len(c['version'])`, `sorted([c['version']]) == sorted([c['version']])`,
`[c for c in [1,2]]`. That gate — not the allowlist — is what stops credit theft, and it held against
every tautology I could build.

It certifies *dependence*, not *content*: `bool(c['version'])` and `c['version'] and True` both return
`falsifiable=True` (a mutation empties the capture and flips them), so a row asserting nothing about
the capture's values is credited as a live, sensitive predicate. Under this round's definition that is
a pass, but it is the cheapest way to reach `evaluated>=5 / eval_lines>=4`, so "live predicate" credit
should not be read as "the claim asserts something" (see also F5).

## 3. F1 — a registry row crashes the counter (uncaught parser exceptions)

Contract clause attacked: the counter's own output line (`met=…`, `errors=…`) as the artifact a closure
judge reads, i.e. "the instrument rejects bad registry text" — it does not; it dies.

`safe_compile` line 85 calls `ast.parse`, and `score` line 210 wraps it in `except (SyntaxError,
ValueError)`. CPython 3.14 raises two other classes:

- deep subscripts → `RecursionError`;
- a long `not` chain → `MemoryError: Parser stack overflowed - Python source too complex to parse`.

Both escape. Evidence (fixture `fixA`: one population line, one registry row whose predicate is
`c['tags']` repeated 100 000 times, 800 001 bytes; receipt is the committed one):

```
$ ( ulimit -v 2000000; timeout 30 python3 -B tools/round60-c2-counter.py --repo $S/fixA --tip HEAD --base HEAD )
Traceback (most recent call last):
  File ".../tools/round60-c2-counter.py", line 310, in <module>
    sys.exit(main())
  ...
  File ".../tools/round60-c2-counter.py", line 209, in score
    tree = safe_compile(r["predicate"])
  File ".../tools/round60-c2-counter.py", line 85, in safe_compile
    tree = ast.parse(expr, mode="eval")
RecursionError: Stack overflow (used 8140 kB) during compilation
exit=1   wall=279 ms   (re-run from the packaged builder: 289 ms)
```

No `population=… met=…` line is printed and `controls()` never runs (`c_n` never counts). Reproduced
with the `not`-chain case at driver level (`cases2/42-not-chain-100k.expr` →
`MemoryError: Parser stack overflowed`), so this is a class, not one spelling. Nested parentheses
(100 000) raise `SyntaxError` and are counted as `errors` — the asymmetry is what makes the crash
silent rather than loud.

Impact. The judge cannot distinguish "registry defective" from "judge crashed"; a claim that asserts
`errors=0` is neither met nor refuted, it is simply absent, and the 5 control families are not run at
all (0/0, which `main` would then treat as `met=False` only if it survived). For a round whose whole
closure is "the counter re-runs the committed registry", a one-line registry row is enough to remove
the verdict.

Smallest remediation (in the proposed patch, not applied to the lane):

```python
    try:
        tree = ast.parse(expr, mode="eval")
    except (RecursionError, MemoryError) as e:
        raise ValueError(f"source too complex: {type(e).__name__}") from None
```
plus widening the call-site tuple to `except (SyntaxError, ValueError, RecursionError, MemoryError)`.
Measured effect: `fixA` goes from "traceback, no output, exit 1" to
`… controls_rejected=5/5 errors=1 met=False`, exit 1, **224 ms**.

## 4. F2 — work amplification inside allowed nodes (the reevaluation multiplier)

Contract clause attacked: `bidirectional` "every predicate is falsifiable … its recorded verdict equals
its evaluation" and the counter's implicit promise that it terminates. Nothing in the counter bounds
time, nodes or allocation (`signal` is never imported; `falsifiable` re-evaluates up to `1 + 3·chains`
times; `controls()` re-runs `score()` once per row per family).

The amplifier, 181 bytes, using only `ast.ListComp`, `ast.Name`, `ast.Subscript`, `ast.comprehension`:

```
[[[t for t in c['show']['model_info']['tokenizer.ggml.tokens']] for _ in c['show']['model_info']['tokenizer.ggml.tokens']] for _ in c['show']['model_info']['tokenizer.ggml.tokens']]
```

`c['show'].model_info['tokenizer.ggml.tokens']` has 512 elements in the committed receipt → 512³.
`BinOp` is banned, so `[0]*10**9` is impossible — but a comprehension is a multiplication without an
operator.

Single-evaluation measurements (`repro/attack-matrix.tsv`):

```
$ ( ulimit -v 2000000; timeout 20 python3 -B driver.py cases2/48-comp3-512tok.expr full )
{"safe_compile": "accepted", "evaluate": true, "eval_s": 1.9539, "falsifiable": true, "falsifiable_s": 3.7842}   wall 6 168 ms
$ ( ulimit -v 600000;   timeout 20 python3 -B driver.py cases2/48-comp3-512tok.expr full )
{"safe_compile": "accepted", "evaluate": null, "eval_s": 0.7456}   -> a 181-byte predicate demands > 600 MB
$ ( ulimit -v 2000000; timeout 10 python3 -B driver.py cases2/49-comp4-512tok.expr full )   -> exit 124 (>10 s, no result)
$ ( ulimit -v 2000000; timeout 10 python3 -B driver.py cases2/57-comp5-512tok.expr full )   -> exit 124
```

The row is *credited* (`falsifiable=true`), so it is exactly the shape a lane would keep. Number of
`evaluate` calls per predicate, measured by monkey-patching `evaluate` on synthetic registries of R
rows over R population lines: `R=1 → 13`, `R=5 → 365`, `R=14 → 2912` (208 per row), `R=20 → 5960`,
`R=28 → 11704` — i.e. roughly `10R² + 5RP`, because the verdict-flip and quote-corrupt families each
re-run the whole `score()` once per row.

End-to-end, the two registries differ in one field of one row:

```
# fixF: 14 rows, 14 population lines, every predicate `c['version']['version'] != ''`
population=14 rows=14 covered=14/14 evaluated=14 eval_lines=14 sensitive=14/14 bound=14 contradicted=0 amended=0/0 receipt_ok=1 controls_rejected=44/44 errors=0 met=True
exit=0   wall=418 ms   (re-run: 353 ms)

# fixD: identical, except row R0 carries the 181-byte nested comprehension above
population=14 rows=14 covered=14/14 evaluated=14 eval_lines=14 sensitive=14/14 bound=14 contradicted=0 amended=0/0 receipt_ok=1 controls_rejected=44/44 errors=0 met=True
exit=0   wall=254 859 ms   (4 m 15 s)
```

610× the wall clock, same verdict. With a nested comprehension one level deeper the counter does not
finish inside a 300 s bound; with a registry of 20+ rows the same 181 bytes scales quadratically.

Smallest remediation (in the patch): bound the *source*, not the runtime — a source-length cap, a node
budget, and a refusal of any comprehension nested inside another comprehension. Those three rules are
what make the exponential impossible (the multiplier needs a comprehension inside a comprehension and
nothing else in the admitted grammar compounds work):

```python
MAX_SRC, MAX_NODES, MAX_COMP = 2048, 256, 2
# ... len(expr) > MAX_SRC -> ValueError; walk counts nodes; > MAX_NODES -> ValueError;
# two comprehension nodes where one is inside the other -> ValueError
```

Measured: the bomb is refused in **212 ms** (`fixB` → `errors=1 met=False` instead of 12 689 ms), and
legitimate registries are untouched — `fixF` still `met=True` (418 ms) and `fixE` still evaluates its
genexp row (see F3). A wall-clock guard (`signal.setitimer` + `SIGALRM` with the top frame re-raised)
would be the belt to this braces, but the static caps are enough for every multiplier the grammar admits.

## 5. F3 — generator expressions cannot see `c`, and the miss is silent

Contract clause attacked: `errors=0` as reported by the counter, and the documented predicate language
("A predicate is a restricted Python expression over `c`").

`evaluate` (line 98) passes the capture namespace as `eval`'s **locals**:
`eval(compile(...), {"__builtins__": {}, **ALLOWED_CALLS}, {"c": caps})`. S520 says list/dict/set
comprehensions are inlined into the enclosing frame; S521 says a generator expression is a function
frame. So a genexp body that reads `c` resolves it against globals only:

```
any(x for x in c['version'])               -> evaluate True
any(c['version'] for x in c['version'])    -> evaluate None   (NameError: name 'c' is not defined)
all(all(y for y in c['version']) for _ in c['version']) -> None
[c['version'] for _ in c['version']]       -> True            (PEP 709 inlined)
```

`evaluate` catches it (`except Exception → None`), and `score` line 214 does `if res is None: continue`
— **no `errors` increment, no diagnostic**. `errors=0` is printed for a registry in which a live row was
never evaluated. A row that is never evaluated also can never be contradicted, so
`contradicted == amended` is computed over a silently smaller registry than the one the lane committed.

Evidence, fixture `fixE` (4 rows, 2 population lines, one row is
`all(m['digest'] == c['tags']['models'][0]['digest'] for m in c['ps-after']['models'])`):

```
$ .../tools/round60-c2-counter.py --repo $S/fixE --tip HEAD --base HEAD      # tip 11f2d667
population=2 rows=4 covered=1/2 evaluated=1 eval_lines=1 sensitive=1/1 bound=1 contradicted=0 amended=0/0 receipt_ok=1 controls_rejected=12/12 errors=0 met=False
exit=1  wall=228 ms
$ .../counter-patched.py          --repo $S/fixE --tip HEAD --base HEAD      # proposed one-line fix
population=2 rows=4 covered=2/2 evaluated=2 eval_lines=2 sensitive=2/2 bound=2 contradicted=0 amended=0/0 receipt_ok=1 controls_rejected=12/12 errors=0 met=False
exit=1  wall=235 ms
```

(`fixE` holds four honest rows over two population lines; the row that uses a genexp body reading
`c` is the second population line. Both runs are reproduced by
`repro/build_fixtures.py` + the command above.)

Only the namespace changes; `fixF` (cheap, 14 rows) still reports `met=True` under the patch, so the
fix does not manufacture coverage.

Smallest remediation: one line — put `c` in the same mapping the comprehension frames read:

```python
        scope = {"__builtins__": {}, **ALLOWED_CALLS, "c": caps}
        return bool(eval(compile(tree, "<pred>", "eval"), scope, {}))
```

No escape is opened: the grammar is unchanged, `c` is a plain JSON-decoded dict, and the empty
`__builtins__` remains. Belt: emit `silent=N` (rows whose predicate compiled but evaluated to `None`)
on the output line so the state is visible even before the fix lands — this is the state the counter
already computes and then discards.

## 6. F4 — receipt_caps recursion, and a silent capture hole

`receipt_caps` verifies each body's sha256 and then parses it, catching `ValueError` only (lines
172-174); the outer parse catches `(ValueError, KeyError, TypeError, AttributeError)` (line 191).
`json.loads` on deeply nested JSON raises `RecursionError`, which escapes to `main` line 295 and kills
the counter. The bodies are HTTP responses from the server child — network-origin data, not lane prose
— and the receipt can be perfectly well-formed and hash-correct:

```
# fixture fixC: schema "kama-ollama-live/v1", one capture whose body is 200 000 nested "[" "]", sha256 matches
$ .../tools/round60-c2-counter.py --repo $S/fixC --tip HEAD --base HEAD
  File ".../tools/round60-c2-counter.py", line 172, in receipt_caps
    caps[name] = json.loads(cap["body"])
RecursionError: Stack overflow (used 8140 kB) while decoding a JSON array from a unicode string
exit=1   wall=281 ms        (no verdict line, no controls)
```

Depth probe on the module directly: depth 1 000 → `ok=True`, 50 000 → `ok=True`, 200 000 →
`RecursionError`. Under the patch (`RecursionError` added to both excepts) `fixC` prints
`receipt_ok=1 controls_rejected=5/5 met=False` and exits 1 in 224 ms.

Second, quieter half of the same function: a body that fails to parse is dropped with `pass` while
`receipt_ok` stays 1. The **committed** receipt already has one — `root`, body `404 page not found` —
so `caps` holds 10 of the receipt's 11 captures and a predicate over `c['root']` is silently
unevaluable (same silent-`None` path as F3). Optional fix: `ok = False` when a body fails to parse.

## 7. F5 — grammar narrower than documented (false rejects)

Loud (`errors=1` → `met=False`): `-1` (`node USub not allowed`), `{}` (`node Dict not allowed`),
`sorted(..., key=…)` and `sorted(..., reverse=True)` (`node keyword not allowed`), and `min`, `max`,
`sum`, `abs`, `tuple`, `float`, `range`, `enumerate`, `zip`, `map`, `repr` (not in `ALLOWED_CALLS`).

Silent: a chain whose outermost subscript is a slice — `c['show']['modelfile'][:5] != ''` — makes
`chains()` return no chain (the walk stops at the `ast.Slice`), so `falsifiable()` is `False` and the
row is dropped without an error even though the predicate genuinely reads `c`. Same for
`len(c['show']['modelfile'][:5]) == 5`.

Cheapest remediation: state the exact admitted grammar in the counter docstring (nodes in, nodes out,
calls in) and either add `USub`/`Dict`/whitelisted `keyword` or document their absence; treat a slice
at the end of a chain as chain-transparent in `chains()`.

The opposite error exists too, and it is the one that matters for calibration: the gate over-credits
emptiness tests. `bool(c['version'])` and `c['version'] and True` evaluate `True` and are
`falsifiable=True` (the "empty" mutation flips them), so a row whose predicate asserts nothing about
the capture's values is counted in `evaluated`, `eval_lines` and `sensitive` — the three numbers the
C2 predicate's minimums (`evaluated>=5`, `eval_lines>=4`) are read from. The definition in the freeze
("a mutation of a capture it reads flips its result") is satisfied, so this is not a defect against the
frozen text; it is a limit of what that text certifies, and the reason a reviewer should read the
registry's predicates rather than the counters derived from them.

## 8. Proposed patch (not applied to the lane)

`repro/patch.diff` (unified, against the tip), `repro/counter-patched.py`:

1. `safe_compile`: `try: ast.parse(...) except (RecursionError, MemoryError) -> ValueError`; source cap
   2048 bytes; node cap 256; refuse a comprehension inside a comprehension.
2. `evaluate`: `c` moved into the globals mapping, locals omitted.
3. `score`: call-site except widened to `(SyntaxError, ValueError, RecursionError, MemoryError)`.
4. `receipt_caps`: `RecursionError` added to both excepts (`MemoryError` on the outer one).

Effect matrix (all measured, `repro/run-log.tsv`): `fixA` crash → `errors=1 met=False` (224 ms);
`fixC` crash → clean line (224 ms); `fixB` 12 689 ms → 212 ms `errors=1`; `fixE` `covered=1/2` →
`covered=2/2`; `fixF` unchanged `met=True`. The escape surface is unchanged: of the 59 cheap probes
re-run against both copies, 57 decide identically and the 2 that differ (`cases4/68`, `cases4/69`) are
the nested-comprehension shape the cap is aimed at. The tradeoff is explicit and should be chosen by
the L1, not by me: a legitimate two-level comprehension (`any(x for x in [y for y in c['tags']['models']])`)
is refused too. The alternative is to keep nesting and add a wall-clock alarm (`signal.setitimer` +
`SIGALRM`, re-raising at the top frame), which bounds the time while still admitting the construct —
but it makes the counter's cost depend on the host's speed instead of on a static property of the text.

## 9. Frontier step (proposed artifacts, for the L1 to integrate)

Drafted in this seat's out dir because the lane tree is read-only here:

- `.ufo/waves/round-60/w1/out/SE01PredicateSandbox/proposed-sources-S519.md` — **three new SOURCES
  rows S519–S521** (census 259 → 262), all opened live on 2026-10-27 with byte-identical HTML
  snapshots and sha256s in `repro/doc-snapshots.sha256`:
  S519 (Python 3.14 `eval`, §eval) carries the load-bearing sentence *"Overriding `__builtins__` …
  this is not a security mechanism: the executed code can still access all builtins."*;
  S520 (PEP 709 comprehension inlining) carries the inlining asymmetry;
  S521 (§6.2.9 generator expressions) carries the genexp frame.
- `.ufo/waves/round-60/w1/out/SE01PredicateSandbox/proposed-mined-mistake.md` — **one mined mistake**:
  the counter reports `errors=0` for a registry it never fully evaluated (F3 + the unparsable-capture
  hole), with the one-line fix and the `fixE` before/after that shows the fix able to fail and able to
  pass.
- `.ufo/waves/round-60/w1/out/SE01PredicateSandbox/proposed-knowledge-entry.md` — **one knowledge
  entry**, `corpus/knowledge/predicate-sandbox-limits.md`: what the evaluator actually guarantees, what
  multiplies work, the crash paths, and five rules for a predicate author.

One-line census note for the integrator: `grep -c "^| S[0-9]" corpus/SOURCES.md` = 259 at tip
`11f2d667`; the rows above are numbered from S519, which matches "next free id S519" in the freeze.

## 10. Limits, and what this seat does not claim

- One host CPython (3.14.8), one committed receipt (19 270 bytes, 11 captures, 10 parseable), one
  fixture model. The comprehension-inlining asymmetry is 3.12+; the parser exception classes are
  implementation-defined (a host on 3.11 would fail every comprehension that reads `c`, loudly).
- Only the counter's code paths were attacked. The *claims* the registry will make — quote coverage,
  verdict/amendment semantics — were not evaluated; `registry/ollama-live-claims-r60.tsv` and
  `corpus/knowledge/ollama-live-amendment-r60.md` do not exist yet at the tip, so no wave-w1 registry
  was available to run against. Every fixture therefore uses a synthetic registry with the committed
  receipt unchanged.
- No C2 verdict is offered. What is offered: three defects with exact reproductions and exit codes, one
  patch with measured before/after, and the frontier drafts above.
- `bash tools/test-snapshot.sh`, the evidence selftest and the SOURCES census were **not** run by this
  seat (they write inside the lane tree, which is read-only for a leaf seat). The admission floor is
  the L1's to re-establish after integrating anything from §8/§9.
- **Explicitly unrun or abandoned.** After the original fixtures were measured, `repro/build_fixtures.py`
  rebuilt all six and the decisive runs were repeated from the packaged artifacts: `fixA` crash (289 ms),
  `fixA` patched `errors=1` (229 ms), `fixE` `covered=1/2` → `2/2` (228/235 ms), `fixB` 13 081 ms → 225 ms,
  `fixC` patched clean line (259 ms), `fixF` `met=True` (353 ms). The only number **not** re-measured is
  the `fixD` wall clock: a duplicate run was started from the packaged builder and cancelled on a peer's
  finalise request, so `254 859 ms` is the single observation (the ratio against `fixF` is then 353–418 ms,
  i.e. 610×–722×). `bash tools/test-snapshot.sh`, `tools/kama-ollama-evidence.py --selftest` and the
  SOURCES census were **not run** by this seat — they write inside the lane tree, which is read-only here.
  No live Ollama server was started or needed for this item: every probe used the committed receipt and
  synthetic registries only. Nothing in this report depends on the C1 live surface.
- The 610× number is a single measurement on this host under a 2 GB address-space cap; it is the
  *order* that matters (quadratic in row count times exponential in nesting depth), not the third
  digit.

## 11. Artifact index

All paths relative to `kama-shokunin/`. The `repro/` directory is self-contained: with
`round60-c2-counter.py` (tip blob, sha256 `d2e9a72…a8fe5`) and `receipt.json` beside it, any probe
re-runs as `( ulimit -v 2000000; cd repro && timeout 10 python3 -B driver.py cases/<case>.expr full )`.

```
repro/round60-c2-counter.py     pristine copy of the tip instrument under test (git show 11f2d667:tools/…)
repro/receipt.json              copy of .ufo/waves/round-60/live/receipt.json (sha256 49d06600…90c2a6)
repro/TIP-COPY.sha256           digests proving the two copies above are what they claim
repro/driver.py                 probe harness: safe_compile -> evaluate -> falsifiable, one JSON line out
repro/cases/                    68 probe expressions stored verbatim (small ones)
repro/make_big_cases.py         regenerates the 10 oversized probes (deep nesting, parser-stack, 1e6 literal, 5 MB string)
repro/attack-matrix.tsv         77 probes: expression, safe_compile verdict, evaluation, falsifiability, timings
repro/run-log.tsv               every decisive command, its exit code, wall time and output tail
repro/counter-patched.py        proposed fix (scratch copy; the lane tree is untouched)
repro/patch.diff                unified diff tip -> proposed
repro/build_fixtures.py         deterministic builder for fixA..fixF (asserts toplevel, per-command identity)
repro/fixtures.sh               the commands to run against the built fixtures
repro/doc-snapshots/            S519/S520/S521 HTML snapshots as fetched 2026-10-27
repro/doc-snapshots.sha256      snapshot digests
proposed-sources-S519.md        frontier rows S519-S521 (draft for the L1)
proposed-mined-mistake.md       mined mistake + the one-line fix, shown able to fail and able to pass
proposed-knowledge-entry.md     draft of corpus/knowledge/predicate-sandbox-limits.md
```
