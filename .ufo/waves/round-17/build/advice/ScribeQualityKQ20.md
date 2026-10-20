VERDICT: partial — KQ20 draft written and grounded in opened sources; no detector, mutant or fault control was run, so the admission is unverified.

## Behavior

- Wrote one append-ready section (preamble + KQ20 row in the four-column shape of `corpus/QUALITY.md`) to `.ufo/waves/round-17/build/drafts/quality-kq20.md`. No lane doc, gate, frozen copy or matrix was edited.
- Preamble: KQ20 supersedes nothing; KQ1–KQ19 stay in force, except KQ14 already replaces KQ7's sufficiency (append-only rule kept) and KQ16 already replaces KQ15's exit-class and capture wording.
- KQ20 admits a documented grading only with (a) a killing mutant, (b) fault-injected wrong values for that field, (c) before/after counts on the frozen and repaired gate, (d) digest-pinned detector with no fixture bytes edited.

## Sources opened (all accessed 2026-10-20)

- `corpus/QUALITY.md:17` — "Author and parent-dispatched advisor agreement are not an outside spot-check." (review boundary; basis for the author-recorded limit).
- `corpus/QUALITY.md:22-24` — "appended so no existing line moves" (append-only convention followed by the draft's heading).
- `corpus/QUALITY.md:41` — KQ14 "(supersedes KQ7's sufficiency, preserves its append-only rule)" (basis for the preamble).
- `corpus/QUALITY.md:49` (raw) — KQ15 full row, read to confirm the exit-class/capture clauses and the frozen-snapshot correspondence wording.
- `corpus/QUALITY.md:53-54` — KQ16 "supersedes only KQ15's two inaccurate formulations" (basis for the preamble).
- `corpus/QUALITY.md:109` (raw) — KQ19 full row (latest row; column shape and "frozen probe fails exactly the expected-loading rows" wording).
- `.ufo/waves/round-16/falsify/advice/MutateHarness.md:13` — "The bounded detector was the **pair of complete 72-row runs**" (detector identity).
- `.ufo/waves/round-16/falsify/advice/MutateHarness.md:18` — a mutant is SURVIVED if it "preserves that pair and the per-row pass/fail vector" (basis for the per-row vector rule).
- `.ufo/waves/round-16/falsify/advice/MutateHarness.md:20` — every row's "`verdict`, `reason`, `probe_exit`, `drift`, `passed`, and `error`" preserved (basis for the totals-only reject).
- `.ufo/waves/round-16/falsify/advice/MutateHarness.md:148` — "Ignoring exit or drift removed comparisons that rejected no observed row in either probe version." (basis for the "never counted" reject).
- `.ufo/waves/round-16/falsify/advice/MutateHarness.md:150` — "The timeout exception path was not exercised." (basis for the unreached-path reject).
- `.ufo/waves/round-16/falsify/advice/MutateHarness.md:152` — "not independent evidence that reason, exit, drift, verdict-case, and timeout grading are load-bearing" (basis for the limit wording).
- `corpus/lessons/round-16-verifier-spotcheck.md:187` (Routed defects 6) — "`served_model` is not graded and there is no route-match assertion." (motivating lesson pointer).
- `tests/probe-verdicts/check.py:297, 338` — `served_model` is recorded (297) and copied from the row (338) but not compared in the pass expression (340-347).
- `tests/probe-verdicts/check.py:320` — "probe timed out after {PROBE_TIMEOUT}s" (timeout path that records an error and returns before grading).
- `tests/probe-verdicts/check.py:329-338` — `row = doc["rows"][0]` sits inside the `try` (329-336) but `row.get(key)` (338) sits outside it. [INFERENCE from reading, not executed] A non-object row (for example a string) would raise `AttributeError` uncaught at 338, which is the traceback the round-17 C1 brief describes.
- `tests/probe-verdicts/check.py:340-346` — pass expression grades verdict, reason, exit and drift only. Line numbers differ by one from the brief's "336-347"; the grading block is 337-347.
- Identity check: `sha256sum` of `tests/probe-verdicts/check.py`, `.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py` and `git show cff9e62:tests/probe-verdicts/check.py` all equal `b853576edd54e006c4d8742c1a7335a0d6cca475d107acce7792da75b6145762`. The current gate is therefore byte-identical to the frozen gate at the pinned commit.

No URLs were used. Quotes are ≤25 words and located as above.

## Findings

1. The round-16 detector counted survivors by pair totals, which cannot see fields no row distinguishes. KQ20 therefore requires per-row vectors (MutateHarness.md:18, :20).
2. The timeout path has no fault input at all (check.py:319-321; MutateHarness.md:150). KQ20 rejects its claimed coverage until a fault-injected slow subject is run, or records it as unexercised.
3. `served_model` is recorded but never compared (check.py:297, :338, :340-347), matching the routed defect (round-16 lesson, Routed defects 6). KQ20 is the rule that makes this a required detector, not an admitted grading.
4. The unguarded `row.get` (check.py:338) means a malformed row can end as a traceback rather than a recorded per-row failure. KQ20 rejects a "killed" count that comes from a traceback (see Limitations).

## Limitations

- Nothing was executed. The mutant runner, fault controls and check.py were not run; the detector's kill counts are unknown.
- The draft cannot know how many mutants round-17 C1 will enumerate, so no count is written into the row.
- KQ20 has no outside review; under QUALITY.md:17 it stays author-recorded.
- The "correct subject never produces that wrong value" test is a judgment that a non-author reviewer must check against each field.
- Unknown: whether the fault-suite wrappers and mutant runner exist at the time of integration.

## Installs

None. No tool was installed or updated; the read-only `sha256sum` and `git show` used the system's existing binaries.

## Checks for L1 after integration

- Confirm KQ20's table cell renders with the same four columns as KQ19 and contains no unescaped `|`.
- Run the round-17 mutant runner against frozen and repaired gates, and insert the before/after counts only if the detector produces them.
- Verify the check.py SHA (`b853576e…5762`) before and after any C1 edit to confirm the frozen-gate comparison remains valid.
