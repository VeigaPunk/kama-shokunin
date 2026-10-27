# R02ProfileHookSemantics — round-58 falsification: sys.setprofile frame tracking in tools/round58-battery-exec-check.py (build tip e4891d8a4c9c70e97124980c2ec9aee5762a7f0a)

Attacks: C1 predicate sentence "executed ... every ... label was passed to a `run` frame that **issued** at least
one subprocess invocation carrying `--counter`", and the C1 kill rule's coverage ("any no-op accepted").
No LSP server device is available in this session; all checks below are command runs against extracted blobs.

Baseline (instrument sanity): frozen counter reproduced the frozen build-tip row exactly —
`python3 tools/round58-c1-counter.py --repo <lane> --tip e4891d8a --checker <tip checker>` (checker+counter extracted
via `git archive` to scratch): genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True, exit 0.
Receipts: receipts/c1-counter-buildtip.out. Survivors below are net-new, outside the 11 enumerated variants → LIMITS.

## F1 (major, no-op survivor outside the enumerated 11) — legs recorded run-with-counter; zero subprocesses belonged to any watched frame
Fixture X01-ghost-thread (receipts + full source: variants/X01-ghost-thread/): ROSTER literal identical
(checker: roster_match=1 kills=1 controls=2); `run`/`assert_mutant_breaks_detection` bodies issue NO subprocess —
each only enqueues a label to a daemon worker thread and sleeps 50 ms. The ghost thread issues all 4
`--counter` invocations. sys.setprofile is thread-local, so the worker carries no hook; the harness recorder's
`stack` list is shared, so its fake_run appends each ghost invocation to whichever watched record is top of the
main thread's stack.
Result: `met=True executed=1 legs=3/3 mutant_assert=1`, checker exit 0 — a fully no-op battery ACCEPTED.
Frames receipt: 4 frames, each sub=1 counter=1, while the frame bodies contain no subprocess call.
This is exactly "a leg recorded as run-with-counter but no counter subprocess belonged to that frame".
Causality control X01-noghost (identical, ghost not started): executed=0 legs=0/3 met=False, exit 1 —
the acceptance is caused exactly by cross-thread invocation attribution.
Receipts: receipts/X01-ghost-thread.verdict.out, .frames.json, X01-noghost.*.
Per the frozen kill rule this is a LIMIT to report, never a retroactive predicate change; it does not alter C1's
frozen verdict (counter row above stands), but the kill rule's "any no-op accepted" clause is demonstrably leaky.

## F2 (semantic misbinding) — "issued" is implemented as time-slice attribution, not issuance
The checker measures "a subprocess argv was recorded while this frame's record was top-of-stack **on the main
thread**", regardless of which thread issued it. Fixture F also shows the inverse: watched `run` frames executing
on a worker thread emit no call events at all (thread-local hook) and their invocations are dropped or miscredited
to a concurrent main-thread frame (probe probe_xrec_thread.py sections E/F; frames receipt X02: frames=0).
So the C1 execution binding does not prove the battery's own frames invoke the counter; a kill-designated leg
could be satisfied by any background thread active inside any watched window.

## F3 (false negative) — threaded legs are invisible to the binding
Fixture X02-all-threads: every leg genuinely issues its invocation from inside a run()/assert frame, on worker
threads → frames=0, executed=0, met=False, checker exit 1. A behaviour-preserving rewrite that moves legs to
threads (an execution detail) is rejected; the checker's "binds declared roster to *executed* legs" claim is blind
off the main thread. Receipts: receipts/X02-all-threads.verdict.out, .frames.json.

## Stack-pop correctness (seat question) — verified clean paths, Python 3.14.8
- Exception raised inside `run`: unwind emits a `return` event; pop balanced (probe section C).
- Recursion / nested watched calls: push/pop strictly nested, depth returns to 0 (section D).
- Generator watched fn: `call` at first next(), `return` at the yield (suspension pops), `call` re-fires on
  resume, `return` at exhaustion — balanced; no stale record left on top (probe_events.py A/B). Side effect: one
  logical generator frame yields multiple records with the same label; harmless only because `ran` is a set.

## Residual risk and verification gaps
- `id(frame)` is stored as int and the pop guard compares ints only; CPython id reuse after free could in principle
  pop a stale record. No reachable schedule found where a stale record is top-of-stack (all observed paths balance),
  so this stays a risk note, not a finding.
- X01's 50 ms windows are sleeps; deterministic here because fake_run is pure-Python and instant (4/4 landed), but a
  ghost landing at a frame boundary would credit an adjacent label — affects which label, not the hole's existence.
- Not attacked: c_call/c_return events, monkeypatched `sys.setprofile` inside the battery, os.exec-style escapes
  (Popen blocked by the allow-list), or the C2 counter.
- Scratch /fast/scratch/hyaku/kama-r58/R02ProfileHookSemantics removed after receipt copy; no pacman use, no tool
  installs; lane tree untouched; fixture repos lived only under scratch with asserted toplevels.

Report paths (this file): .ufo/waves/round-58/w1/out/R02ProfileHookSemantics.md; evidence:
.ufo/waves/round-58/w1/out/R02ProfileHookSemantics/ (receipts/, variants/, probes, driver.sh).
