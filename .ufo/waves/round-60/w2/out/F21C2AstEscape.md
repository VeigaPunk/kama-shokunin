# F21C2AstEscape — W2
- Axes: calibration (judged), operability.
- Counterexample: 181-byte nested comprehension over 512-token receipt capture yields cubic work; W1 measured counter `met=True` in 254859ms vs 418ms baseline (610x); deeper case >300s.
- A 800001-byte subscript chain escaped parser handling as uncaught `RecursionError`: no verdict, exit 1.
- Dunder/import/attribute attacks rejected; no code escape demonstrated.
- Evidence: `.ufo/waves/round-60/w1/out/SE01PredicateSandbox.md` lines 19-37, 85-135, 137-184; cited W1 runs, not repeated.
- Impact: unbounded allowed evaluation weakens C2 calibration and operability; met=True has no time bound.
- Correction: source/node caps, reject nested comprehensions, catch parser resource exceptions; isolate evaluation with CPU/memory/time bounds if adversarial expressions remain admitted.
- Lane bytes and frozen predicates unchanged; no tools installed.