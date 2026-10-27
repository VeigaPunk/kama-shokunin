# F21C2AstEscape — C2 AST sandbox falsification

Axes: operability and calibration (calibration judged; operability nominally held). Frozen C2-r60 predicate unchanged.

## Counterexample
No code escape found in W1: allowlisted AST rejects attribute access/import routes. Strongest counterexample is resource exhaustion from valid grammar: a 181-byte, three-level nested list comprehension iterates 512 tokenizer tokens cubically. On the committed receipt, W1 measured 6.168s for one evaluate/falsifiability probe under `ulimit -v 2000000`; at 600000 KB evaluation returned `None` after 0.7456s. At counter level, a 14-row registry otherwise met=True in 418ms, but replacing one predicate with that comprehension yielded the same met=True after 254859ms (610x). A deeper comprehension timed out at 300s. This is an allowed-call-free expression; merely removing dangerous calls does not bound execution.

Additional failure mode: repeated subscript text (800001 bytes) raises uncaught `RecursionError` in `ast.parse`; the counter emits no verdict and exits 1. The proposed W1 evidence contains command/output/exits and limits; I did not rerun the costly probes.

## Evidence / impact
W1 artifact `.ufo/waves/round-60/w1/out/SE01PredicateSandbox.md`, lines 19-37, 85-135, 137-184; matrix `.../SE01PredicateSandbox/repro/attack-matrix.tsv`. These are W1 reported measurements, not new executions. Dunder/import/attribute probes were rejected, so no demonstrated code-execution escape. Resource amplification undermines C2 calibration and counter operability: met=True does not mean timely completion; parser crash prevents a verdict. No lane edits or predicate changes.

## Smallest safe correction
Bound expression source length and AST node count, reject nested comprehensions, and classify `RecursionError`/`MemoryError` as invalid rows at both parse and score boundaries. Run evaluation in a resource/time-bounded worker if the counter must tolerate adversarial but admitted expressions; static complexity caps alone cannot guarantee bounded work for every admitted call/comprehension.