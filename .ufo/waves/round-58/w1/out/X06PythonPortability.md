# X06PythonPortability — round-58 interpreter portability (C1 operability, C2 calibration)

Frozen tip `e4891d8a…`; all inputs read as committed blobs; lane read-only (`git show`), git mutation only in
scratch fixtures. Method: `python3.X tools/round58-c1-counter.py --repo <lane> --tip e4891d8a… --checker-blob
e4891d8a…:tools/round58-battery-exec-check.py --work $S/w-<ver>`; counter, checker and harness child all
propagate `sys.executable`, so one run covers the chain over all 15 variants. Axes — **operability** (does the
frozen predicate hold per interpreter) and **calibration** (which version-dependent semantics the tools rely on).

| interpreter | predicate | exit | receipt |
|---|---|---|---|
| CPython 3.9.25 | met=True 1/1 3/3 11/11 err=0 | 0 | c1-cpython-3.9.25.txt |
| CPython 3.10.22 | met=True 1/1 3/3 11/11 err=0 | 0 | c1-cpython-3.10.22.txt |
| CPython 3.11.17 | met=True 1/1 3/3 11/11 err=0 | 0 | c1-cpython-3.11.17.txt |
| CPython 3.12.15 | met=True 1/1 3/3 11/11 err=0 | 0 | c1-cpython-3.12.15.txt |
| CPython 3.13.16 | met=True 1/1 3/3 11/11 err=0 | 0 | c1-cpython-3.13.16.txt |
| CPython 3.14.8 (host default `/usr/bin/python3`) | met=True 1/1 3/3 11/11 err=0 | 0 | c1-cpython-3.14.8.txt |
| CPython 3.14.8 free-threaded | met=True 1/1 3/3 11/11 err=0 | 0 | c1-cpython-3.14.8-freethreaded.txt |
| CPython 3.15.0 | met=True 1/1 3/3 11/11 err=0 | 0 | c1-cpython-3.15.0.txt |
| **PyPy 3.11.16** | **met=False genuine=0/1 benign=1/3 noop=11/11 errors=0** | **1** | c1-pypy-3.11.16.txt |

## F1 — PyPy 3.11.16 breaks the accept half (LIMIT on C1 operability, not a counterexample on the frozen runtime)
Root cause is an unclosed write, not the profiler: checker line 190 `open(src, "wb").write(bat.stdout)`
leaves the harness battery unflushed. CPython flushes by refcounting at end of statement, PyPy does not,
so the child execs an empty or partial module.
- `flush-semantics.txt`: size right after that write — PyPy **0**, CPython 2775 (both 2775 with a `with` block).
  `pypy-src-size-per-variant.txt`: **12/15** batteries are 0 bytes at child spawn under PyPy (B2, N05, N11 land
  whole; GC timing, 3/3 runs identical); CPython 3.14 is 15/15 complete.
- Chain: empty module ⇒ only `<module>` call/return ⇒ `frames=[]` ⇒ `executed=0`;
  `pypy-spawned-child-profiler.txt`: `raw_events=17 frames=0` under a PyPy parent vs `raw_events=12419
  frames=4` with an intact file.
- Causality: a scratch copy with `with open(...)` around those two writes passes the sweep under PyPy —
  `genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True`, exit 0 (`c1-pypy-3.11.16-fixed-checker.txt`);
  not a `setprofile` or `f_locals` defect.
- Blast radius is the accept half: all 11 no-ops still reject under PyPy (an unexecuted battery also fails
  `executed`), so F1 never lets a no-op survive.
## F2 — same fatal pattern, latent, in the C2 counter
`tools/round58-c2-counter.py` 113/115 write the round42/round41 reconcile tools with the same unclosed
`open(f, "wb").write(...)`, then spawn `sys.executable` on them — identical fatal shape. Not observed live:
`--manifest-rev 941acf70583a…` is a fleet-root commit, absent from kama-shokunin, and campaign tools are not run
there; the C2 consequence is `[INFERENCE]` from F1's mechanism. Non-fatal siblings (checker 159/214, counter 132)
write `--out` files read only after exit.
## Calibration on the named risks
- `sys.setprofile` event shape: `call`/`return` for watched functions on every CPython 3.9–3.15 (incl. 3.14t)
  and on PyPy with an intact file; `c_call`/`c_return` throughout. Labels come from watched frames, not
  comprehensions (3.12 inlining off-path); `co_argcount` is guarded (`*args`-only `run` ⇒ label `None`);
  `co_filename` matches because the harness compiles with `src_path`.
- `f_locals`: 3.13.16/3.14.8/3.14t/3.15.0 return `FrameLocalsProxy`, 3.9–3.12 a `dict`; the checker only reads
  (`f_locals.get(first)`) and proxy `.get` returns the label on all four, so PEP 667 write-through is not relied
  on. Off-path probe: writing `f_locals["label"]` in a call hook changes the callee's value on CPython 3.9–3.15,
  not on PyPy — only a label-rewriting checker would care.
## Host inventory, side effects, limits
PATH: `/usr/bin/python3` = 3.14.8, `~/.local/bin/python3.11|3.12|3.13`, `pypy3.11`; the 3.8 symlink dangles, so 3.8
is not live. `uv python install 3.10 3.15 3.9 cpython-3.14.8+freethreaded` (uv channel, reason: widen the matrix)
added `~/.local/bin` symlinks `python3.9/3.10/3.15/3.14t`; those four were removed to restore the prior PATH state
— a disclosed deviation from the PATH guard; uv interpreters stay under `~/.local/share/uv/python` (outside PATH).
No CPython version dependence found: 8 CPython runtimes meet the frozen predicate, so the claim's `sys.setprofile`
grounding is interpreter-stable where refcounted flush holds; the one failure is a non-CPython runtime that
self-heals under a two-line close fix, outside this seat's bounds. Scratch removed; 14 receipts in
`.ufo/waves/round-58/w1/out/X06PythonPortability/receipts/`.
