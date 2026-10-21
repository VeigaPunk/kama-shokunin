source: S061 (Python 3.14 sys.exit), S062 (Stryker mutant taxonomy), S064 (subprocess signal returncodes); S063 (PIT counterexample, rejected as universal-rule support); corpus/lessons/round-20.md Gate
verified-at: 2026-10-21 — pinned round-20 source openings and named error-injection regression set
recheck: on-release — run tools/error-verdict-census.py on its pinned cell registry; reopen the Python and mutation-policy sources when their revisions change

# Error classification is not mutation-kill credit

A gate may correctly fail closed if its subject crashes. A mutation counter
claiming a targeted rejection needs more: a declared exit code and the
subject's emitted verdict, with evidence that the intended check ran.
This is a scoped lane measurement rule, not a universal testing convention.

## Exit status ambiguity

S061 states that `sys.exit` with a noninteger object prints it to stderr and
exits 1. Uncaught exceptions also produced 1 in round-20 host Python probes
(`build/advice/SrcPySysExit.md`). The same status can therefore mean an
intentional verdict or a crash. S064 describes negative POSIX returncodes as
signal termination; that alone is not a subject verdict either.

For the live-receipt grid, an actual rejection is exit 1 with the gate's
`INVALID ` line. A silent 1, traceback-only 1, signal, timeout or unknown
exit is visible error evidence and must not increase rejected counts or
produce a clean overall grid. A positive genuine-rejection control prevents
an always-error classifier from satisfying the regression suite.

A targeted `FAIL` literal before a selftest abort is insufficient kill
credit. The completed target assertion and complete enumeration must be
observed. Preserving a partial transcript is useful but not completion.

## Precedent is not universal authority

S062 Stryker distinguishes failed-test Killed from Runtime error and excludes
runtime errors from its score. S063 PIT instead marks `RUN_ERROR(true)` and
counts it in detected totals. Thus the inference "all mutation tools exclude
crashes" is rejected. The lane explicitly chooses its stricter evidence
policy rather than borrowing a universal numbering or scoring convention.

## Limits

The round-20 cells cover the named grid and selftest-arm repairs, not every
historical counter. Probe-checker subject crashes may still be row failures
(fail-closed policy); that is different from claiming a targeted kill.
Other historical mutation runners and post-verdict crashes are disclosed
residuals. Missing docs/git already returned citation-checker exit 2 at the
round-start commit; no improvement is credited for those correct paths.

## `sys.exit(None)` scope qualification — S065 (2026-10-21)

S061's status-1 statement applies to non-`None` noninteger exit objects. Python
3.14.8 says “None is equivalent to passing zero” in the `sys.exit` argument
paragraph; the other noninteger object case prints to stderr and produces exit
1. S065 supersedes only the overbroad exception wording in S061; this does not
change the evidence rule that an exit status alone is not an emitted verdict.

## Round-23 deepening — the auditor's own exit class

Appended 2026-10-21 (round 23); the frontmatter above describes the
round-20 sources. `tools/report-landing-audit.py` used `1` for `failed`, and
its `main()` mapped only `EvalError`/`OSError` to `2`. Its git calls used
`text=True`, so captured output was decoded by the io.TextIOWrapper default
(S097), which raises on invalid bytes (S098); git may emit non-UTF-8 log text
verbatim (S093). A repository-local `i18n.logOutputEncoding`, a non-UTF-8
committed report or errata blob, or a 5000-digit field therefore crashed it
into exit 1: an error read as a verdict. The round-23 grid observes 9 such
frozen-arm tracebacks (F01, F02, F16, F18, F19, F20, F22, F24, F26); the
lesson's first count of 8 predates F26.

The fix has two layers: decode git output as bytes with an explicit `strict`
UTF-8 decode mapped to a typed refusal (S096), and catch any remaining
exception as could-not-evaluate. A grid credits a refusal only when its
stderr carries the pinned reason, so the catch-all cannot launder an
unrelated failure into a "met" row. The catch-all alone meets exactly one
fault row (F24) yet removes all 9 tracebacks (falsify-wave ablation,
CritSeparabilityW2), so "0 tracebacks" is not evidence of isolation; only
per-row reasons and per-element mutants that the grid kills on a named row
are (KQ34). A mutant "kill" counts only on grid exit 1, never on a grid that
could not evaluate.

source: S093, S096, S097, S098, corpus/lessons/round-23.md; evidence
`tests/report-audit/repo-state-grid.py`, `tests/report-audit/isolation-mutants.py`.

## Round24 — isolation is not evidence availability

The round23 containment work did not justify its metadata-only refusal.
Outside closure rounds[428] reproduced a correct clean verdict lost on a
complete promisor-marked clone. Disclosure of that trade did not waive the
no-trade rule; KQ35 and the round24 paired controls learn that disagreement.

Keep three questions separate:

1. **May the tool acquire evidence?** No: the global `--no-lazy-fetch`,
   no-replace-objects and signature/log suppression boundary remains.
2. **Can the required local evidence be read?** A failed history, tree,
   source, report, ledger or tag-target read is could-not-evaluate, not
   empty data. Promisor packaging alone answers nothing (S103).
3. **What does a negative local lookup mean?** A locally absent fabricated
   citation keeps the ordinary finite finding and authorized errata.
   But when the token names content referenced locally and unavailable, or
   an opaque missing tree/commit conceals that dependency, the required
   evidence is unevaluable. An unrelated blob hole is not that token.
   The same rule applies with or without promisor metadata.

S102 documents the `?`-prefixed encountered-missing output used only as
a bounded diagnostic, not a global completeness precondition or proof
about a remote object universe. Rejected S104 shows why fsck green cannot
substitute for required-object availability. A locally present wrong-type
blob in Landed is still a genuine finding, not an unavailable object.

The initial round24 preregistration conflated metadata with unknown
citations and would block the historical errata-corrected spliced hash.
That expectation is retained, withdrawn/not-achieved, and separately
reported; `oracle-amendment-1.json` prospectively follows the original
local-object contract. The 44-case snapshot predates L1 source inspection;
`oracle-supplement-2.json` adds independent opaque-dependency cases.
No candidate result was used to silently rewrite those filed outcomes.

source: S102, S103, S104 (rejected candidate); `corpus/lessons/round-24.md`;
evidence: `tests/report-audit/promisor-grid.py` with its committed expectation
manifest, `.ufo/waves/round-24/` registration/oracle history.
