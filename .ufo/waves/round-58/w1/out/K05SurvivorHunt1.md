# K05SurvivorHunt1 — Round 58 C1 survivor hunt

Axes: operability (C1 checker execution evidence); calibration (limits to frozen claim, not predicate changes).

Checker: `tools/round58-battery-exec-check.py` at build tip `e4891d8a4c9c70e97124980c2ec9aee5762a7f0a`. I built each isolated fixture from that tip's round-56 preregistration and side files, changed only its battery, committed inside the fixture after checking its top-level path, then ran checker `--repo <fixture> --tip HEAD`. No production files changed.

Command: `python3 /fast/scratch/hyaku/kama-r58/K05SurvivorHunt1/run.py` — exit 0.

| New battery variant / attack | Checker result | Exit | Finding |
|---|---|---:|---|
| Conditional-expression label (`"base-old-counter" if True else "decoy"`) | `met=True`, legs 3/3 | 0 | Survivor: execution frame still carries the genuine label. |
| Separate `run`-external subprocess invokes `other-counter.py --counter x`; roster `run` frame remains intact | `met=True`, legs 3/3 | 0 | Survivor: this is a decoy; it does not replace/remove a roster leg. |
| Decoy subprocess with `--counter bogus`; remove actual test subprocess's `--counter` argument | `met=True`, legs 3/3 | 0 | Survivor. The harness records the decoy while the run frame is active and only tests for argument token `--counter`, not the target counter/expected semantics. |
| `run` unconditionally sets `ok = True`, ignoring return code and parsed field | `met=True`, legs 3/3 | 0 | Survivor: checker verifies invocation, not result use or correctness of the battery's assertion. |
| `os._exit(0)` at start of `main`, before legs | `could-not-evaluate: harness failed rc=0` | 2 | Rejected as evaluation error, not a clean non-met result; not a survivor. |

Per-run receipts (exact checker stdout; `tip` is each fixture's generated commit):

```text
conditional_label: exit=0
tip=eda71098c1a81c52586613cc7655f3465dc2b269
present=1 roster_match=1 kills=1 controls=2 executed=1 legs=3/3 mutant_assert=1 met=True

different_counter_run: exit=0
tip=1b5d8d0da7d2e3522edc11b49541c31938f6e096
present=1 roster_match=1 kills=1 controls=2 executed=1 legs=3/3 mutant_assert=1 met=True

decoy_subprocess: exit=0
tip=8549f68aa3cd084fa83a4fff903fe11cb82593b3
present=1 roster_match=1 kills=1 controls=2 executed=1 legs=3/3 mutant_assert=1 met=True

ignored_results: exit=0
tip=a861a11b792ee5ff6d18f3022ec6f2b94fa0d78a
present=1 roster_match=1 kills=1 controls=2 executed=1 legs=3/3 mutant_assert=1 met=True

os_exit: exit=2
could-not-evaluate: harness failed rc=0
```

Evidence in checker lines 73–77: every subprocess call inside watched frames is recorded, and fake_run returns canned success/output. Lines 130–131 count any recorded argv containing `--counter`; lines 204–208 require those counts plus roster equality, not battery result assertion. Consequently decoy call satisfies counter evidence, and ignored result survives. The conditional-label survivor is compatible with intended behavior-preserving rewrite but demonstrates no-op labels can be represented dynamically. `os._exit` bypasses child result receipt; outer checker reports evaluation error.

Attacks: C1 frozen predicate's unenumerated survivor space only (LIMITS, not grounds to alter frozen kill rule); operability evidence semantics. No C2/calibration SCORECARD/SCORECARD-row finding tested. Smallest safe correction for future calibration: ensure a watched `run` invocation's counter-bearing call is the actual leg command (e.g. compare expected command identity/arguments), and do not equate invocation with assertion outcome. The current frozen predicate remains as frozen; report these survivors as limits.
