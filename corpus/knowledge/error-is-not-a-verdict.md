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
