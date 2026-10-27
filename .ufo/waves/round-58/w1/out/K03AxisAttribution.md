# Round 58 — K03 axis attribution

## Finding
- **C1 is an operability claim, narrowly:** the artifact under evaluation is an executable Python checker, and the frozen counter actually launches it against a genuine battery, three rewrites, and eleven committed variants. This is stronger evidence of runnable behavior than source-shape inspection. It does not establish operational usability of the battery's real subprocess work: `round58-battery-exec-check.py` deliberately replaces subprocess calls with canned success, blocks process creation, and virtualizes writes. Accordingly, attribute the gain to *checker discrimination under a hermetic execution harness*, not live battery operability or endpoint health. The frozen C1 claim itself names checker behavior, so this boundary is a limitation, not grounds to change the predicate.
- **C2 is calibration:** its counter compares SCORECARD's stated closure pointer (round, repeated round, verdict) against the highest committed spotcheck lesson and a pinned MANIFEST revision; separately it runs the round-42 reconcile. This directly checks self-description against observed repository/ledger state.
- **C1 and C2 are causally separable in the frozen counters:** C1 takes lane repo/tip and a checker; it assesses fixture outcomes and does not read SCORECARD or MANIFEST. C2 reads SCORECARD, lesson tree, pinned fleet MANIFEST, and round-42 tool; it does not invoke C1 checker or battery variants. Caveat: the claims are operationally separable as measurements, not necessarily independent interventions—both report at a measured repository tip and a shared integrated change could affect both. No observed dependency means no basis to merge their axes.

## Strong counterexample / limits
C1's strongest demonstrated counterexample is not an enumerated mutant but the trust boundary in its harness: `fake_run` returns `CompletedProcess(..., 0, "ld_audit=detected\n", "")` for every recorded invocation, while writes are swallowed and `Popen`/`os.system` blocked. A battery that reaches the expected calls with incorrect arguments or would fail against a real endpoint can therefore still look operational to this checker. The frozen roster predicate only requires invocation carrying `--counter`, not argument correctness, endpoint reachability, or truthful output. The frozen kill rule explicitly says survivors outside the eleven variants are limits, not retroactive predicate changes. Report this as scope, not a newly invented failure criterion.

C2 has a related scope boundary: regexes validate the first matching claim and inclusion phrase on the first calibration row in the first `## Axes` section; they do not establish lesson content truth or that the referenced closure is substantively valid. Its calibration statement is specifically pointer freshness/verdict agreement plus r42 reconciliation, not a universal audit of all self-assessments.

No universal clause is evident in either frozen predicate: C1 is bounded to named genuine/benign/no-op fixtures and zero evaluation errors; C2 to the highest-numbered spotcheck blob and a specific pinned manifest verdict. Avoid interpreting “0 mismatches” as universal correctness beyond those enumerated checks.

## Evidence
- `tools/round58-c1-counter.py` lines 10–16, 99–145: committed fixture inputs; checker invoked for each; scored genuine/benign/no-op outcomes and evaluation errors.
- `tools/round58-battery-exec-check.py` lines 7–23, 73–103: hermetic harness, canned subprocess output, swallowed writes, blocked process calls.
- `tools/round58-c2-counter.py` lines 12–25, 50–60, 78–123: defined measured objects, row selection, max lesson round, pinned MANIFEST verdict, and independent r42 count.
- `.ufo/waves/round-58/controls/freeze.txt` lines 4–30: frozen predicates, kill rule, and explicit survivor treatment.

## Commands / checks
- `read skill://godspeed` — skill instructions returned; exit 0 (tool success).
- `read /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-58/controls/freeze.txt` — frozen claims read; exit 0.
- `read /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round58-c1-counter.py:1-130` — counter source read; exit 0.
- `read /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round58-c1-counter.py:3-17,71-146` — fixture execution details read; exit 0.
- `read /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round58-battery-exec-check.py:1-180` — checker source read; exit 0.
- `read /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round58-c2-counter.py:1-130` — C2 source read; exit 0.
- No campaign check was run; conclusions are source/frozen-text review only.
