# EX04Gate — round77-instruments

Axes: operability (ordered, timeout-bounded, fail-closed composition); compatibility (existing arm order and per-arm checks retained).

## Files changed

- `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/pre-report-gate.py`
- This exclusive report.

Added arm 10, `round77-instruments`, after arm 9. It invokes citation-baseline, append-registers, selfrecord-round76 in that order, each with `--selftest`, through the existing 600-second subprocess runner/process-group timeout handling. Each must exit zero and its last nonempty output line must fully match `*_SELFTEST pass=N fail=0`. Missing modules, nonzero exits, timeout/spawn failures and missing/malformed summaries fail the arm with exit 1 and identify the script. All three instruments are attempted in fixed order so failures remain visible.

Existing live instrument arms and their grading arguments are unchanged. Existing 21 selftest cases retain their independent pass counts; their aggregate gate-width expectations necessarily change from 9 to 10. Added one composite case for green execution order and each instrument's missing/nonzero/no-summary/red-summary/trailing-output/timeout failures. Expected aggregate selftest tally is 22; this is an expectation, not an observed result. Added round-77 documentation inside the same tool; historical predicate/documentation is retained with an explicit new-arm addendum.

## Retained evidence and limitations

- Read the entire frozen `plans/round-77-claims.md` before editing; it was not changed.
- Read-only command `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master HEAD`, exit 0: both lines were `7d60e2ab58866a0366937d61c9712483be57b36e`.
- Source discovery `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round77*` returned no files at inspection time. The three module implementations are sibling-owned and were not edited.
- LSP is unavailable in this seat's exposed tools; used bounded source reads and anchored edits instead.
- No tools installed or updated. No lane git writes, commits, or orchestration performed.
- Initial scratch setup failed before command execution because its selected cwd did not yet exist: `Working directory does not exist: /fast/scratch/hyaku/kama-r77/EX04Gate`. Retried creation from an existing cwd successfully. The scratch directory is removed before handoff.

## Verification ownership / receipts

No build, lint, formatter, selftest, gate or probe was executed: the higher-priority fleet-executor instruction explicitly reserves post-integration gate execution to the parent and forbids tests during this editing wave. The specific receipt-run conflict was sent to Main. Consequently there are no observed gate exit codes or red-arm outputs to report, and the following requested receipt files were intentionally NOT fabricated:

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/measured/after/gate-selftest.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/measured/after/gate-run.out`

Parent post-integration commands (cwd `/home/vgpnk/Projects/shokunin/kama-shokunin`, TMPDIR under its own assigned scratch):

1. `python3 tools/pre-report-gate.py --selftest` — capture actual exit and verbatim output; expected final line `PRE_REPORT_SELFTEST pass=22 fail=0`.
2. `python3 tools/pre-report-gate.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --round 77 --tip master` — capture actual exit and verbatim output, including every red arm. The user's literal no-argument command is not a scored gate invocation: the existing CLI requires `--round`; this CLI behavior was deliberately not changed.

Risks: unexecuted wiring/selftests; sibling instrument modules absent at inspection; final-summary labels must use the normal uppercase `*_SELFTEST` convention. The existing frozen predicate still describes its historical nine-arm population; the addendum describes the ten-arm extension without rewriting prior claims.

Self-evaluation: accuracy 4 (implementation unexecuted); completeness 4 (receipt execution reserved to parent); clarity 4 (historical nine-arm prose preserved with addendum); actionability 4 (exact parent commands and missing receipts named); conciseness 4 (handoff includes required ownership conflict). Overall 4.0. Highest-impact next action: parent executes both commands after integration and records the real receipts. No green result is claimed.
