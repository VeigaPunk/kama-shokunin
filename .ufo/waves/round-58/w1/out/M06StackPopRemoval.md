# M06StackPopRemoval

Axes: operability and calibration. Target: `tools/round58-battery-exec-check.py` profile hook, specifically its frame-stack pop at `stack.pop()` on matching `return`.

Mutant: replaced only `stack.pop()` with `pass`; no roster or counter changes. This tests whether the frozen C1 detector notices watched-frame stack bookkeeping failing to unwind.

Expected detector: frozen C1 counter, `tools/round58-c1-counter.py`, at tip `e4891d8a4c9c70e97124980c2ec9aee5762a7f0a`. A killed mutant would fail frozen predicate (genuine/benign rejection, no-op acceptance, or evaluation error).

Command for each stage (same bounded detector, same tip):
`python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round58-c1-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip e4891d8a4c9c70e97124980c2ec9aee5762a7f0a --checker /fast/scratch/hyaku/kama-r58/M06StackPopRemoval/<stage>.py`

Outputs and exit codes:
- Pristine: `genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True`; exit 0.
- Mutated: `genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True`; exit 0.
- Restored: `genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True`; exit 0.
- All 15 fixture details were identical: genuine and B1/B2/B3 accepted; N01–N11 rejected; no evaluation errors.

Verdict: **survived** (coverage limit, not a frozen-predicate change). Failing to pop the return frame leaves stale records in `stack`; however, these watched functions return in the tested battery execution such that later relevant subprocess recordings and the counter's aggregate evidence still satisfy the predicate. Thus C1 does not establish correct stack unwinding, only the enumerated acceptance/rejection behavior.

Restoration evidence: source and pristine/restored SHA-256 `89ad4e5d5c15c883eacf39126c6d1a0859382c54142976b4ed8539680832eec5`; mutant SHA-256 `89af59f7d761c6d9db1a9d0f06f45f4f9463f00e96549a093277609d06738c61`. Restored bytes equal source exactly. Scratch was removed after receipt capture.
