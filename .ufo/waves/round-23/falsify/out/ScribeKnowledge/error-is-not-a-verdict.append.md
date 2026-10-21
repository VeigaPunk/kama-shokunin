
## Exit-class collision by uncaught exception: round-23 catch-all and pinned-reason grid — S095 (2026-10-21 draft)

Source: S095 (Python 3.14.9 `bytes.decode`, strict default), S061/S065
(`sys.exit`), corpus/lessons/round-23.md#00FE. Lane pin: 245a37f6 — read
`tools/report-landing-audit.py:42-46,108-127,362-372,399-423,887-924` and
`tests/report-audit/repo-state-grid.py:526-596,600-635,648-710`. Grid
numbers are the L1 run as reported in the lesson; this draft did not re-run
them.

### Mechanism

An unhandled Python exception exits 1 (round-20 probes; see the Exit status
ambiguity section above). An auditor whose verdict code is also 1 ("failed")
therefore lets a crash look like a defect verdict. The round-23 frozen auditor
(blob 4fe9339f) did this on repository-state faults: crashes exited 1, the
`failed` code.

S095 names the common source. Under the default `strict` handler,
`bytes.decode` raises `UnicodeError` on undecodable bytes. Unmapped, that
exception is one more path to exit 1.

The current tool separates the classes in two places:

- Call-site mapping: `git()` converts a `UnicodeDecodeError` into `EvalError`
  (`:122-126`), and the errata reader does the same (`:369`). The message
  is pinned, for example "output is not UTF-8".
- Backstop: `main()` returns 2 for `EvalError`, `OSError`, and any other
  `Exception`, printing `could-not-evaluate:` to stderr (`:909-924`).

After this split, exit 1 means only "verdict reached by code" and exit 2
means "not evaluated". Exit 2 is also the only status for a fail-closed
crash, so a pinned stderr reason is the only way to tell the two apart.

### Grid pattern

1. One row per named channel, with an expected exit and expected verdict
   kinds. Every exit-2 row pins a stderr substring in `REASONS` (11 rows:
   F02, F06, F10, F11, F13, F15, F16, F21, F23, F24, F26).
2. A row is met only when all of these hold (`repo-state-grid.py:627-630`):
   no timeout, no `Traceback (most recent call last)` in stderr, no marker
   file created by an executed program, exit equal to the expected exit, the
   stdout JSON kinds equal the expected kinds (crash output parses as
   `unparseable`), and the pinned reason is present.
3. Positive controls (C01–C08) cover clean and genuine-defect cases. An
   always-2 or always-1 classifier cannot satisfy the suite.
4. The frozen arm is the negative control. The grid is only evidence when
   it can fail: the L1 run reports frozen 0/26 faults met with 8 tracebacks
   and 2 executed programs, and current 26/26 with 0 tracebacks, 0
   executions, and 0 timeouts; controls are 8/8 in both arms.

### Limit: a catch-all can satisfy a pinned row

F24 (5000-digit round number) is pinned to
`could-not-evaluate: internal: ValueError` (`REASONS`, `:589`). That string is
the catch-all's own output. `parse_rounds` calls `int()` on a value past
Python's int-conversion limit (`:399-423`), so the row passes because the
catch-all fired, not because a refusal was designed.

Record this as fail-closed exit 2, not a targeted refusal. The rule in the
Limits section applies: a probe-checker crash may be a row failure under a
fail-closed policy, which is different from a targeted kill. A later
targeted refusal for this input should replace the pin.

### Not claimed

- The grid's own `main()` uses the same split: 1 for a violation, 2 for
  `Premise` or any other `Exception` (`:687-710`).
- Code outside the `try` in `main()` (argparse, path setup) and
  `BaseException` subclasses are outside the catch-all. Their exit status is
  whatever CPython produces, and the traceback check is the only guard in the
  grid.
- [INFERENCE, not registered in SOURCES.md] CPython argparse usage errors also
  exit 2. The grid's argv is fixed, so no row can reach that path silently; a
  pinned reason would reject it.
- Signals and timeouts yield `code=None`; `None` never equals an expected exit,
  so those rows are not met.

### Rule (draft wording for the Gate section)

- A nonzero exit that a grid expects as a refusal must pin that refusal's own
  stderr text. A catch-all's text is fail-closed evidence, not a refusal.
- An exit code shared with an uncaught-exception path (1 for CPython) is never
  a verdict by status alone. The classifier also requires parsed verdict
  output and no traceback.
- Keep positive controls and a frozen or known-bad arm in every grid that
  claims a classifier works.

### Frontmatter (proposed edit, not applied)

`source:` gains `S095` and `corpus/lessons/round-23.md`. The `recheck:` line
gains the grid path `tests/report-audit/repo-state-grid.py`.
