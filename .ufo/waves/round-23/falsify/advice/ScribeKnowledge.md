# ScribeKnowledge — round-23 falsify: error-is-not-a-verdict draft

Verdict: drafted. The appended section is in
`.ufo/waves/round-23/falsify/out/ScribeKnowledge/error-is-not-a-verdict.append.md`.
The corpus file `corpus/knowledge/error-is-not-a-verdict.md` was NOT edited
(draft only, per assignment).

## Behavior drafted

- Exit-class collision by uncaught exception: CPython's unhandled exception
  exits 1, the same status as the audit's `failed` verdict. The frozen blob
  4fe9339f let repo-state crashes exit 1.
- S095 (strict `bytes.decode` raises `UnicodeError`) is the decode-path source.
  The current tool maps it at call sites (`git()` `:122-126`, errata `:369`) and
  backstops with a catch-all returning 2 (`main()` `:909-924`).
- Grid pattern: pinned stderr reasons on all 11 exit-2 rows (`REASONS`
  `:579-591`), traceback/execution/timeout/JSON-kinds checks (`:627-630`),
  8 positive controls, frozen arm as negative control.

## Gates

- Lane pin confirmed: `git rev-parse HEAD` = 245a37f69628c2c6bb29bbf17897d8fb5946c857.
- Read at lane HEAD: `tools/report-landing-audit.py` (`:42-46,108-127,362-372,399-423,887-924`),
  `tests/report-audit/repo-state-grid.py` (`:526-596,600-635,648-710`),
  `corpus/lessons/round-23.md#00FE`, `corpus/knowledge/error-is-not-a-verdict.md#5A53`,
  `corpus/SOURCES.md` row S095 (line 107), S061 (line 73), S065 (line 77).

## Findings

1. F24 is pinned to `could-not-evaluate: internal: ValueError` (`repo-state-grid.py:589`).
   That is the catch-all's own output, so the row passes as fail-closed exit 2,
   not as a targeted refusal. The draft says so explicitly. The lesson's
   "Refusals (exit 2, reason pinned in the grid)" list counts it among targeted
   refusals; that wording overstates F24 and should be corrected in the lesson
   (L1 integration item, not a knowledge-file change).
2. Dangling reference: the knowledge file cites `build/advice/SrcPySysExit.md`.
   `test -e` at lane checkout 245a37f6 reports it missing (it may be untracked
   build output). The draft does not repeat the citation. The L1 should confirm
   whether that path is intended to be committed.
3. `.ufo/waves/round-23/falsify/advice/ScribeKnowledge.md` did not exist before
   this write (the advice dir was empty).

## Not verified

- S095 page was not re-opened; the quote and version (3.14.9) are taken from
  `corpus/lessons/round-23.md` and the SOURCES row, both as recorded by L1.
- Grid and selftest were not run; the 26/26, 0/26, and 8/8 figures are the L1
  report. Per assignment and lane rules, no verification was run.
- The argparse exit-2 point is marked [INFERENCE] in the draft; it is not
  registered as a source.

## Installs / updates

None. No tools were installed or upgraded.

## Files written

- `.ufo/waves/round-23/falsify/out/ScribeKnowledge/error-is-not-a-verdict.append.md` (new)
- `.ufo/waves/round-23/falsify/advice/ScribeKnowledge.md` (new)

No other files were written. No commits, pushes, or jj commands. No subagents spawned.

## Suggested checks for main agent

- Compare the draft against `corpus/knowledge/error-is-not-a-verdict.md` for
  heading style before any integration.
- Decide on the F24 wording in `corpus/lessons/round-23.md` (see Finding 1).
- Decide on `build/advice/SrcPySysExit.md` (Finding 2).
