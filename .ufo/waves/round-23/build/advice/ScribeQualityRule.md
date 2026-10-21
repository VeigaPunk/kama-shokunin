# ScribeQualityRule — KQ34 draft report (round 23 build)

Seat: CloseKama22.ScribeQualityRule (leaf; no subagent dispatch). Scope: draft KQ34 only.
QUALITY.md was not edited.

## Behavior

Drafted KQ34 as a single row in the existing four-column format (ID | Admit only when |
Reject or limit when | Motivating lesson), intended as a new `## Criterion added — round 23`
section after KQ33. It requires, for each named repo-local channel, a fixed fault case with
an unfaulted control, injection proof, a KQ20-style kill when the isolation element is
removed, a committed rerunnable grid, and an exception path shown to exit with the
could-not-evaluate code (audit exit 2) rather than a traceback, exit 1, or a verdict.

## Gates

- ID collision: none. QUALITY.md's highest ID is KQ33; `grep` found no KQ34 row.
- Format: matches the table of rows in the round 21–22 sections; no existing line moved.
- Anchors: KQ28 (clean exit 0 as forged by repo-local state), KQ32 (scope limit preserved),
  KQ33 (committed-source load failures must not become a clean fallback). Each anchor is
  stated with its relation in the draft.

## Touched surfaces

- Written: `.ufo/waves/round-23/build/out/ScribeQualityRule/KQ34.md` (draft, 5635 bytes).
- Written: `.ufo/waves/round-23/build/advice/ScribeQualityRule.md` (this report).
- Not written: `corpus/QUALITY.md`, lane tracked files, the `.jj` or Git index, any commit.
  `advice/swarm-registry.json` (mode 0600, owned by another writer) was not opened.
- Created directories: `.ufo/waves/round-23/build/out/ScribeQualityRule/`.

## Out-of-scope items

- The grid fixes and the `tools/report-landing-audit.py` repair are owned by other seats;
  I did not evaluate their correctness.
- No probe, selftest, or fault grid was run. The task scope did not require it. Main agent
  should run `python3 tools/report-landing-audit.py --selftest` after integration.

## Findings (exact)

1. `corpus/QUALITY.md` (read at lane HEAD 4fe9339) has rows KQ1–KQ33 in the four-column
   format, with KQ33 as the latest ID. No KQ34 exists.
2. The lane checkout is dirty: `git status --short` showed ` M tools/report-landing-audit.py`
   and `?? .ufo/waves/round-23/`. The base blob at 4fe9339 has no `GIT_ISOLATION` and no
   `logOutputEncoding`/`sshCommand`/`no-replace` strings (`git show 4fe9339:... | grep` exit 1).
   The working tree now has `GIT_ISOLATION` at lines 83–85 and strict-UTF-8 decode at
   lines 106–114. This is someone else's in-progress edit; I did not touch it.
3. The selftest in the working tree has no case that sets a replace ref, promisor remote,
   `core.sshCommand`, `i18n.logOutputEncoding`, or non-UTF-8 input (`grep` for those strings
   in `tools/report-landing-audit.py` returns only the isolation tuple and its comments).
   The round-23 fault grid is therefore not in-repo evidence under KQ34.
4. `main()` (base and working tree) catches `EvalError` and `OSError` only; the exit-2
   could-not-evaluate path is taken for those. An uncaught `UnicodeDecodeError` from the
   base `git()` (`text=True` decode) is not an `OSError`, so it escapes as a traceback.
   This matches probe item (a)/(b) from the L1 brief. Not re-run here.
5. `lessons/` is absent from this lane checkout (`ls: cannot access 'lessons'`), so
   `lessons/round-22.md` D4/M4, cited by KQ32/KQ33 and by the new row, could not be opened.
   That motivating reference is unverified in this seat. The L1 probe observations were
   taken from the assignment brief (`/tmp/kama-r23-probe/probe.sh` exists; not run).

## Unverified

- Whether the working-tree `GIT_ISOLATION` repair passes the existing 50 selftest cases.
- The grid results for items (a)–(e) under the repaired tool.
- The lessons file content behind the motivating-lesson citations.
- Whether channels beyond the round-23 grid (`core.fsmonitor`, `core.hooksPath`,
  `info/grafts`, `shallow`, `core.worktree`) matter; the draft names them as open, not as
  covered.

## Tooling

No installs or updates performed.

## Artifacts

- `.ufo/waves/round-23/build/out/ScribeQualityRule/KQ34.md`
- `.ufo/waves/round-23/build/advice/ScribeQualityRule.md`
