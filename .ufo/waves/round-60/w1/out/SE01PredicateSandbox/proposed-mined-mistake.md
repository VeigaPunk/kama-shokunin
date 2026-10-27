# Mined mistake (proposed for the round-60 frontier step)

Seat: SE01PredicateSandbox. Proposed, not applied — the lane tree is read-only for
this seat. The lane's own instrument, not a sibling lane, is the subject.

## The mistake

`tools/round60-c2-counter.py` at tip `11f2d667` accepts registry predicates that it
cannot actually evaluate, and reports them as a **clean run**: `evaluate()` returns
`None` on any exception, and `score()` treats `None` as "skip this row" (`if res is
None: continue`, tip line 214) without touching `errors`. The counter therefore prints
`errors=0` for a registry in which a live row was never evaluated at all.

Two concrete ways a lane reaches that state, both measured on fixtures that use the
committed receipt unchanged:

1. **Generator expression that reads `c` in its body.** `evaluate()` passes `c` as
   `eval`'s *locals* (`{"c": caps}` third argument, tip line 98). A genexp body runs in
   its own frame and resolves free names through globals, so it raises
   `NameError: name 'c' is not defined`, which `evaluate` swallows.
   `any(c['version'] for x in c['version'])` → `None`; `any(x for x in c['version'])`
   → `True`. Fixture `fixE` (4 rows, 2 population lines) with one such row:
   tip counter prints `covered=1/2 evaluated=1 … errors=0 met=False`.
2. **A capture body that does not parse.** `receipt_caps()` silently `pass`es on a
   body `json.loads` cannot read (tip lines 172-174) while `receipt_ok` stays 1. The
   committed receipt already has one such capture (`root`, body
   `404 page not found`): `caps` has 10 of the receipt's 11 captures, and a predicate
   over `c['root']` is silently unevaluable with `errors=0`.

The cost of the mistake is on the calibration axis, not on safety: the counter's output
line is the only artifact a closure judge reads, and it says `errors=0` while one row
was never judged. A row that is never evaluated can never be *contradicted* either, so
the amendment obligation (`contradicted == amended`) is computed over a silently
smaller population than the registry claims.

## The fix, and why it is the smallest one

One line at the `eval` call site — put the capture namespace in globals, where
comprehension frames look for it:

```python
def evaluate(tree, caps):
    try:
        scope = {"__builtins__": {}, **ALLOWED_CALLS, "c": caps}
        return bool(eval(compile(tree, "<pred>", "eval"), scope, {}))
    except Exception:
        return None
```

Optionally, and separately: `ok = False` in `receipt_caps` when a body fails to parse,
so an unparsable capture is a receipt defect rather than an invisible hole.

## Fix shown able to fail (and able to pass)

Same fixture, same tip receipt, two counter copies differing only by the patch
(`repro/counter-patched.py`, `repro/patch.diff`):

```
# tip 11f2d667
$ ( ulimit -v 2000000; timeout 120 python3 -B tools/round60-c2-counter.py --repo $S/fixE --tip HEAD --base HEAD )
population=2 rows=6 covered=1/2 evaluated=1 eval_lines=1 sensitive=1/1 bound=1 contradicted=0 amended=0/0 receipt_ok=1 controls_rejected=16/16 errors=0 met=False
exit 1

# patched scratch copy
$ ( ulimit -v 2000000; timeout 300 python3 -B counter-patched.py --repo $S/fixE --tip HEAD --base HEAD )
population=2 rows=6 covered=2/2 evaluated=2 eval_lines=2 sensitive=2/2 bound=2 contradicted=0 amended=0/0 receipt_ok=1 controls_rejected=16/16 errors=0 met=False
exit 1
```

The patched row set gains `covered=2/2 evaluated=2 sensitive=2/2`; nothing else in the
line moves, and `fixF` (14 rows, all cheap) still reports
`covered=14/14 … sensitive=14/14 … met=True` (exit 0, 418 ms), so the fix does not
manufacture credit. The fixture still ends `met=False` for an unrelated reason (row
count/amendment shape of a toy registry), which is what makes it a usable control: the
fix changes exactly the counter that the mistake corrupts.

## Supersession-style trap this mistake resembles

Round 59's mined mistake was a supersession whose flip condition fired while the row
went unmarked. The analogous hazard here is a *silent skip*: the instrument has a state
("row not evaluated") that is not one of its reported states (errors / bound /
contradicted). Adding `silent=N` to the output line — rows whose predicate compiled but
evaluated to `None` — would make the state visible even before the fix lands, and would
be the cheapest closure-side check: `silent == 0` for any registry the lane signs.
