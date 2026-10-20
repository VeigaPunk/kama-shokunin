VERDICT: partial — no measured C1/C2 arm rides on dead weight, but the new tool/gate/controls/counter carry avoidable dead alternatives, two dead fields, one dead assignment and one 30-line duplicate block; none of the suggested cuts changes a check outcome, problem string, count or self-mutant anchor (any edit does of course change that file's own sha256, and for the tool the `tool.sha256` recorded in future receipts).

All repo paths below are relative to `/home/vgpnk/Projects/shokunin/kama-shokunin/`; every command used absolute paths. Reviewed commit `1c325b2e58fcfdc6761f645b44cedfb1d65243e6` in a clean clone `/tmp/kama-r18-falsify-SimplifyC1` (`git switch -q -c seat/SimplifyC1 1c325b2…`; `git status --porcelain` → 0 lines). No production edit, no runtime/gate/controls/counter execution, no official counting command, no installs or upgrades.

# Axes and method

- Operability: remove dead exception alternatives and dead fields without touching argv, ownership, teardown or receipt emission.
- Calibration: keep every targeted detector and the 3-anchor self-mutant table intact; a cut is rejected if it weakens a named check.
- Method (static only): ruff 0.17.1 (`F` rules), Python 3.14.8 AST scans for unreferenced defs/locals/params/constants, statements after terminators, structural clones and exception-tuple subsumption, plus an import-and-compare of the producer's and gate's pinned span texts. Scripts are in the appendix.

# Deletion candidates, highest confidence first

## 1. Dead exception alternatives (zero behavior change)

Python 3.14.8: `ProcessLookupError` and `PermissionError` are `OSError` subclasses, `socket.timeout is TimeoutError`, `TimeoutError` is an `OSError` subclass, and `UnicodeDecodeError` is a `ValueError` subclass. Each tuple below therefore catches exactly what `OSError` (or the surviving member) already catches; every handler body is `pass` or records `type(exc).__name__`, so the observed behavior is identical.

| File:line (current) | Tuple | Cut to |
|---|---|---|
| `tools/kama-llamacpp-live.py:450` | `(OSError, socket.timeout, TimeoutError)` | `OSError` |
| `tools/kama-llamacpp-live.py:811` | `(ProcessLookupError, PermissionError, OSError)` | `OSError` |
| `tools/kama-llamacpp-live.py:822` | same | `OSError` |
| `tools/kama-llamacpp-live.py:1439` | same | `OSError` |
| `tests/llamacpp-live/controls.py:809` | same | `OSError` |
| `tests/llamacpp-live/controls.py:812` | same | `OSError` |
| `.ufo/waves/round-18/c1/measure.py:377` | `(UnicodeDecodeError, ValueError, RecursionError)` | `(ValueError, RecursionError)` |

Preserved: the set of caught exceptions is unchanged, so no receipt, gate problem line, count or selftest case moves. `measure.py:246` and `survivors.py:388/430` deliberately name only `(ProcessLookupError, PermissionError)` with no `OSError` in the tuple; those are narrowed catches and must stay.

Adjacent C2 sites of the same class (not this seat's files; flagging for the C2 owner): `.ufo/waves/round-18/c2/survivors.py:340`, `.ufo/waves/round-18/dispatch-provenance.py:248,295,493,555`. The latter's line 295 alone is `(OSError, ValueError, UnicodeDecodeError)`.

## 2. Dead assignment in the controls selftest

`tests/llamacpp-live/controls.py:1698` — `strict, lax = _FakeGate(), _FakeGate('lax')`. Ruff 0.17.1 reports `F841 Local variable 'lax' is assigned to but never used`. The only lax-mode gate used afterwards is `frozen = _FakeGate('lax', no_flag=True)` at 1699. Cut to `strict = _FakeGate()`. The selftest counter `n[0]` is incremented only inside `expect()`, so the measured line "selftest: 70 cases, 0 failure(s)" is unchanged.

## 3. Dead field in probe_info

`tests/llamacpp-live/check-receipt.py:691` — `probe_info[name] = {"rec": rec, "row": row, "res": res}`. `rec` and `row` are read at 984 and 1019; no `["res"]` or `.get("res")` read exists anywhere in the file (grep returns only this assignment). The local `res` is still needed for the `summary.exit` check at 692–700; only the dict entry is dead. Cut `, "res": res`.

## 4. Dead field in the gate-result normaliser

`tests/llamacpp-live/controls.py:920` — `'stderr_tail': (stderr or '')[-400:] or None` in `_gate_result` (908–921). The literal appears exactly once in the file (AST count), and rows expose `tool_stderr_tail` (1161, 1318) instead. The `stderr` parameter stays because it feeds `usage_error` at 918. Cut the entry; no consumer changes.

## 5. Dead default argument

`tools/kama-llamacpp-live.py:640` — `def _discard_bodies(transitions, loading_503, loading_bodies=())`. Both call sites (614, 628) pass all three arguments. Cut `=()` so the parameter is mandatory; no call site or output changes.

## 6. Optional: duplicate belt-and-braces `_kill_fake` in controls main

`tests/llamacpp-live/controls.py:1303` is the load-bearing cleanup inside `run_tool_control`'s `finally`; it runs on normal return and on exception before `_read_receipt`/`grade_tool_row`. Main then calls `_kill_fake` again in a `finally` for the k0-base run (1836–1841) and for every non-forgery control (1848–1852). By construction no fake process can be alive at those outer calls: `_kill_fake` itself does not raise (it swallows pidfile/all-signal OSErrors), and no later step starts a process. Removing the two outer `try/finally` wrappers is behavior-preserving; keeping them is acceptable only as a stated belt-and-braces property. Tradeoff: if `run_tool_control` is later refactored to return before its kill, the outer net would be the only cleanup.

## 7. Optional: the 30-line duplicate probe-check block

`tests/llamacpp-live/check-receipt.py:983-1017` (`probe_model_ok`) and `1018-1052` (`probe_mismatch`) are 34/35 normalized lines with `difflib` ratio 0.87; only the `probe_info` key, the `matching`/`mismatch` label, and the `(MODEL_OK, matched, 0)` vs `(MODEL_MISMATCH, served-id-mismatch, 2)` constants differ. A local helper such as

```python
def _grade_probe(cid, info_key, label, want_exit, want_verdict, want_reason):
    ...
```

called in the current ok→mismatch order, reproduces every `bad()` string, every `require_observed` key and the problem-line order. This is the only material duplication in the C1 files. Tradeoff: one shared predicate path instead of two; k13/k14 plus the gate's 61-case matrix still target both checks independently, so the controls contract is unchanged. Acceptance must be a byte-diff of one doctored receipt's gate stdout before/after, not just the selftest exit.

## 8. Optional: counter scaffolding duplication

`.ufo/waves/round-18/c1/measure.py:355-383` (`run_controls`) and `386-400` (`run_selftest_of`) repeat the same `mkdtemp`/`run_child`/`reap_scratch`/`rmtree` skeleton. A `_run_in_scratch(argv, scratch, label, timeout)` helper returning `(obs, leaked, rundir)` removes ~10 lines without changing either record shape. Low value; not worth a dedicated rerun.

# Deliberate duplication that must NOT be cut

- Producer/gate mirrors are the validator contract, not accidental copies: `_envelope_ok` (`tools/kama-llamacpp-live.py:205-219`) vs `loading_envelope_ok` (`tests/llamacpp-live/check-receipt.py:171-180`); combined install-tree digest (`kama-llamacpp-live.py:178-202`) vs `install_tree_sha` (`check-receipt.py:163-168`); exact argv (`kama-llamacpp-live.py:1241-1252`) vs the re-derived `expected_argv` (`check-receipt.py:506-517`); `HARD_REFUSED_PORTS` (`kama-llamacpp-live.py:68`) vs `HARD_PINS` (`check-receipt.py:49`); controls `CHECK_IDS` (`controls.py:185-190`) vs gate `REQUIRED_CHECKS_V2` (`check-receipt.py:68-80`). Merging any of these makes the gate trust the producer and removes the independent re-derivation that v3 is built on.
- The five pinned source texts are byte-identical in the producer (`source_bindings()`, `kama-llamacpp-live.py:925-997`) and the gate's selftest fixture (`_selftest_source_binding`, `check-receipt.py:1395-1465`): 1,709 bytes total, all five hashes equal to the gate's `SOURCE_BINDING_EXPECTED` pins (verified by import/compare below). The gate needs its own literal to build a valid fixture without network or producer imports; importing the producer would let a producer edit silently validate itself.
- C2 exact clone `tests/probe-verdicts/check.py:311-344` vs `tests/probe-verdicts/fault-controls.py:574-604` (`served_ids_of`): `.ufo/waves/round-18/c2/survivors.py` stages a mutated copy of the whole `probe-verdicts` tree, so if `fault-controls.py` imported `check.py` it would import the mutant and the H5 expectation would move with the subject. The independent copy is load-bearing.
- Synthetic fixtures (`_syn_receipt`, `_FakeGate`, the `rawbefore_k16` projection in `measure.py`) are test oracles, not another production path; the `rawbefore_k16` literal is an exact pinned projection of the observed `runs/c1-measure.json` k16 row and pins the bucket/classification seam seen in the failed official run.

# Stale name / authority note (not a cut)

`tools/kama-llamacpp-live.py:895-899` says `row` null means "this round still owes a row", yet the health span (5288-5299) is exactly S042's cited span, and the 529-534 and 519-523 teardown spans are exactly S043's cited spans; 575-590 contains S043/S047's cited 575-576 and 590. Either the null encodes a narrower judgment (S047 is only the necessary ordering condition, never a termination guarantee), in which case the comment should say so, or it is stale. Do not change it in this measured pass: `row` is emitted in every v3 receipt and is pinned in the gate's `SOURCE_BINDING_EXPECTED`, so a value change would invalidate `live/receipt-{1,2,3}.json` unless those receipts are regenerated; they are measured evidence, not scratch.

# Preserved contract and measured baseline

`runs/c1-measure.json` is the retained **could-not-evaluate** run (`runs/c1-measure.exit` = 2; stderr `c1-measure: fault: before: misclassified=1 but 0 row(s) classified misclassified`; command stdout sha256 `3ad738fc…`, stderr `62554bae…`). Its raw arms are before `accepted_bad 5, good_rejected 1, misclassified 1, uncontrolled_checks []` and after `0,0,0,[]`; `gate_flip_arms` 16→17, `gate_flip_bad` 0→0; per-side controls stdout sha256 `87f4b5b4…` and `7dd9e4da…`. The 1c325b2 counter fix has only selftest-level evidence, not a rerun: `runs/c1-counter-selftest.stdout` = `selftest: 36/36 cases passed`, and the official `c1-self-mutants` run (`commands.json` entry 11, exit 0) reports `drop-gate-flip-arm, k6-any-nonzero, loosen-k0-exit` all killed, with no faults.

Other measured baselines a cut must not move: `runs/tool-selftest.stdout` = `selftest: ok; closed tcp6 listeners …`; `runs/controls-selftest.stdout` = `selftest: 70 cases, 0 failure(s)`; `runs/gate-selftest.stdout` = `selftest: 5 VALID and 1 NOT-EVALUATED receipts accepted; 61 mutations + unreadable case rejected`. The three self-mutant anchors are unique and untouched by candidates 1–8: `controls.py:1135`, `1028`, `1031`.

None of candidates 1–5 touches a check outcome, problem string, check id, count or anchor; 6–8 touch internal code only. The narrow acceptance check for any of them is the existing selftest trio plus the controls-output invariant: the same `70/0` controls selftest, the same `5/1/61` gate selftest, the same tool selftest exit 0, and identical per-control `classification`/`bucket`, gate exits and the four counts for the same tool/gate pair. Raw digests necessarily move when a tool file changes (receipts embed `tool.sha256`), so a byte-diff is not the invariant. The official c1-measure rerun remains L1's; this seat did not run it.

# Limits and teardown

Static review only. I opened no sockets, started no server, ran no gate/controls/counter and no official command. Tools used were already installed: `ruff 0.17.1` at `~/.local/bin/ruff`, Python `3.14.8`; no install/upgrade. Scope limits: this is not a correctness or falsification verdict on C1/C2; it does not re-derive the live receipts; and a consistently-wrong but self-consistent counter remains outside what these static cuts can detect. The clone `/tmp/kama-r18-falsify-SimplifyC1` and its `.scratch-tmp` are removed; no scratch remains, and the only file written in the lane is this report.

# Appendix — exact experiment source

All blocks ran with `cwd=/tmp/kama-r18-falsify-SimplifyC1` at `1c325b2…`.

```sh
# 1. static lint (exactly one finding)
~/.local/bin/ruff check --no-cache --select F --output-format concise \
  tools/kama-llamacpp-live.py tests/llamacpp-live/check-receipt.py \
  tests/llamacpp-live/controls.py .ufo/waves/round-18/c1/measure.py \
  .ufo/waves/round-18/c2/survivors.py tools/sources-append-only.py \
  .ufo/waves/round-18/dispatch-provenance.py tests/probe-verdicts/check.py \
  tests/probe-verdicts/fault-controls.py
# stdout: tests/llamacpp-live/controls.py:1698:13: F841 Local variable `lax` is assigned to but never used
#         Found 1 error. (exit 1)
```

```python
# 2. exception-tuple subsumption
import ast, importlib, sys
files=["tools/kama-llamacpp-live.py","tests/llamacpp-live/check-receipt.py",
       "tests/llamacpp-live/controls.py",".ufo/waves/round-18/c1/measure.py",
       ".ufo/waves/round-18/c2/survivors.py","tools/sources-append-only.py",
       ".ufo/waves/round-18/dispatch-provenance.py",
       "tests/probe-verdicts/check.py","tests/probe-verdicts/fault-controls.py"]
import subprocess, http.client, socket, json
mods={'subprocess':subprocess,'http':http.client,'socket':socket,'json':json}
def resolve(name):
    parts=name.split('.'); base=parts[0]
    if base in dir(__builtins__) if isinstance(__builtins__,dict) else hasattr(__builtins__,base):
        return eval(name)
    if base in mods:
        obj=mods[base]
        for p in parts[1:]: obj=getattr(obj,p)
        return obj
    return None
class V(ast.NodeVisitor):
    def __init__(self,f): self.f=f
    def visit_Try(self,node):
        for h in node.handlers:
            if h.type is None: continue
            names=[]
            def walk(t):
                if isinstance(t,ast.Tuple):
                    for e in t.elts: walk(e)
                elif isinstance(t,ast.Attribute): names.append(ast.unparse(t))
                elif isinstance(t,ast.Name): names.append(t.id)
            walk(h.type)
            cls=[]
            for n in names:
                try: cls.append((n,resolve(n)))
                except Exception: cls.append((n,None))
            for i,(ni,ci) in enumerate(cls):
                if ci is None: continue
                for j,(nj,cj) in enumerate(cls):
                    if i!=j and cj is not None and issubclass(ci,cj) and ci is not cj:
                        print(f'{self.f}:{h.lineno}: {ni} is subclass of {nj} in tuple {names}')
        self.generic_visit(node)
for f in files: V(f).visit(ast.parse(open(f).read()))
# output: tool 450/811/822/1439, controls 809/812, measure 377,
#         C2 survivors 340, dispatch-provenance 248/295/493/555.
# hierarchy check also run: socket.timeout is TimeoutError -> True;
# ProcessLookupError/PermissionError subclass OSError -> True/True.
```

```python
# 3a. unreferenced defs (false positives only: decorator-registered controls,
#     overrides, interface-parity params)
import ast
files=["tools/kama-llamacpp-live.py","tests/llamacpp-live/check-receipt.py",
       "tests/llamacpp-live/controls.py",".ufo/waves/round-18/c1/measure.py",
       ".ufo/waves/round-18/c2/survivors.py","tools/sources-append-only.py",
       ".ufo/waves/round-18/dispatch-provenance.py",
       "tests/probe-verdicts/check.py","tests/probe-verdicts/fault-controls.py"]
for f in files:
    src=open(f).read(); t=ast.parse(src)
    defs={n.name:n for n in ast.walk(t) if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
    used=set()
    for n in ast.walk(t):
        if isinstance(n,ast.Name) and isinstance(n.ctx,ast.Load): used.add(n.id)
        if isinstance(n,ast.Attribute): used.add(n.attr)
    dead=[(d.name,d.lineno,d.end_lineno) for d in defs.values() if d.name not in used]
    if dead: print(f, dead)
# no dead functions beyond decorator/override names.

# 3b. unused module constants and parameters
import ast
files=["tools/kama-llamacpp-live.py","tests/llamacpp-live/check-receipt.py",
       "tests/llamacpp-live/controls.py",".ufo/waves/round-18/c1/measure.py"]
for f in files:
    t=ast.parse(open(f).read())
    assigns={}
    for n in t.body:
        if isinstance(n,(ast.Assign,ast.AnnAssign)):
            tgts=n.targets if isinstance(n,ast.Assign) else [n.target]
            for tg in tgts:
                if isinstance(tg,ast.Name): assigns[tg.id]=n.lineno
    loads={n.id for n in ast.walk(t) if isinstance(n,ast.Name) and isinstance(n.ctx,ast.Load)}
    dead={k:v for k,v in assigns.items() if k not in loads and not k.startswith('__')}
    if dead: print(f,dead)
for f in files:
    t=ast.parse(open(f).read())
    for fn in [n for n in ast.walk(t) if isinstance(n,ast.FunctionDef)]:
        args=[a.arg for a in fn.args.args+fn.args.kwonlyargs]
        used={n.id for n in ast.walk(fn) if isinstance(n,ast.Name) and isinstance(n.ctx,ast.Load)}
        unused=[a for a in args if a not in used and a not in ('self','cls')]
        if unused: print(f'{f} {fn.name}:{fn.lineno} unused params {unused}')
# 3c. statements after return/raise/continue/break: none in the nine files.
```

```python
# 4. structural clones (normalize names/constants/attributes, hash def ASTs >=8 lines)
import ast, collections, hashlib, re, os
files=["tools/kama-llamacpp-live.py","tests/llamacpp-live/check-receipt.py",
       "tests/llamacpp-live/controls.py",".ufo/waves/round-18/c1/measure.py",
       ".ufo/waves/round-18/c2/survivors.py","tools/sources-append-only.py",
       ".ufo/waves/round-18/dispatch-provenance.py",
       "tests/probe-verdicts/check.py","tests/probe-verdicts/fault-controls.py"]
def norm(node):
    class N(ast.NodeTransformer):
        def visit_Name(self,n): return ast.copy_location(ast.Name(id='V',ctx=n.ctx),n)
        def visit_Constant(self,n): return ast.copy_location(ast.Constant(value=type(n.value).__name__),n)
        def visit_arg(self,n): return ast.copy_location(ast.arg(arg='a',annotation=None),n)
        def visit_Attribute(self,n):
            self.generic_visit(n); n.attr='A'; return n
    try:
        t=N().visit(ast.parse(ast.unparse(node)))
        return ast.dump(t)
    except Exception as e: return 'ERR'+str(e)
bodies=collections.defaultdict(list)
for f in files:
    t=ast.parse(open(f).read())
    for n in ast.walk(t):
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
            if n.end_lineno-n.lineno+1 < 8: continue
            h=hashlib.sha256(norm(n).encode()).hexdigest()[:12]
            bodies[h].append((f,n.name,n.lineno,n.end_lineno,n.end_lineno-n.lineno+1))
for h,items in sorted(bodies.items(), key=lambda kv:-max(i[4] for i in kv[1])):
    if len(items)>1: print(h,items)
# output: only check.py:311-344 <-> fault-controls.py:574-604 (served_ids_of)
```

```python
# 5. probe-block similarity (blocks extracted by sed 983-1017 / 1018-1052)
import difflib,re
def norm(p):
    return [re.sub(r"'[^']*'|\"[^\"]*\"",'S',re.sub(r'\s+',' ',l.strip()))
            for l in open(p).read().splitlines() if l.strip()]
a,b=norm('.scratch-tmp/p1'),norm('.scratch-tmp/p2')
print('lines',len(a),len(b),'ratio',round(difflib.SequenceMatcher(None,a,b).ratio(),3))
# output: lines 34 35 ratio 0.87
```

```python
# 6. producer/gate span equality + pins
import importlib.util, hashlib
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
tool=load('tl','tools/kama-llamacpp-live.py')
gate=load('cr','tests/llamacpp-live/check-receipt.py')
prod=tool.source_bindings(); fix=gate._selftest_source_binding()
for i,(a,b) in enumerate(zip(prod,fix)):
    print(i, a['check'], a['span_text']==b['span_text'],
          hashlib.sha256(a['span_text'].encode()).hexdigest()==a['span_sha256'],
          a['span_sha256']==gate.SOURCE_BINDING_EXPECTED[i][5], a['row'])
# output: all five text_equal=True, prod_hash_ok=True, pinned_ok=True;
# rows None, S036, None, None, None; span byte lengths 441/412/272/163/421 = 1709.
```
