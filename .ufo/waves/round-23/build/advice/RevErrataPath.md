# RevErrataPath: errata load/apply review (round 23, build wave)

Scope: `tools/report-landing-audit.py` errata path only: `load_errata`, `apply_errata`, `parse_errata`, the errata lines of `render`, and output/exit handling in `main`. Findings only. No production edit, no commit, no install.

## Target and timeline

- Final reviewed file: lane working copy `tools/report-landing-audit.py`, sha256 `684764108872cea153284dfec89848d5efdf5b30dd37db026434dea2b623e210`, 924 lines. It is `M` against HEAD `4fe9339f8fc3a4a4a479d9c938a850da12f1124d`. Base copy used for comparison: `git cat-file blob 4fe9339:tools/report-landing-audit.py` (sha256 starts `09ecd63bdc3a5be5`).
- Assigned lines 330-360 are base lines: `load_errata` 330-341, `apply_errata` 343-360, `parse_errata` 315-327, `git()` 87-97 (`text=True` at 90). In the final working copy the same functions are at `load_errata` 365-375, `apply_errata` 378-399, `parse_errata` 350-364, `git()` 109-128.
- The lane working copy changed twice during the review (`d0a96599...` at first check, then `79d9e124...`, then `684764...`). I did not edit it. I probed `79d9e124...` and `684764...`; errata outcomes were identical in both. The only errata-adjacent diff between them is the `apply_errata` hex-regex move (`invalid` no longer re-checks the regex; `status` only holds hex corrections, so results are equivalent).

## Verdict

- Closed on the errata path (base fails each channel below; the working copy closes every probed channel, open items O1-O4 excepted): non-UTF-8 ledger (A1), locale-dependent decode (A2), `refs/replace` on the ledger blob (A3), fabricated correction made to resolve by replace (A4), valid correction made to look missing by replace (A5), hidden report token by replace (A15), symbolic correction `HEAD` (A14), ref-only abbreviated correction (A19), promisor lazy fetch executing `core.sshCommand` (A6, A6b), `info/grafts` (A9). `--no-replace-objects` (line 94) also covers the ledger read, not only correction lookups: in base, the forged row was the ledger content itself.
- Open on the errata path: O2 (a bare CR splits one ledger line into two applied rows, verdict clean), O3 (correction validity is object existence, so dangling and alternates-only commits validate; docstring overstates), O1 (output-encoding failure exits 1 with a traceback), O4 (symlink ledger accepted).
- Recommendation: fix O2 and O1 (small, testable), fix O4, and decide O3 (reword or add reachability) before claiming "lane/fleet commit". Reconcile grid case O01 with the docstring (see O3).

## Probe evidence

Reproducer: `.ufo/waves/round-23/build/out/RevErrataPath/errata-fault-probe.py` (`--frozen <base copy> --current <working copy> --work <tmp dir>`). Fixtures are fresh temp repos with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`. The promisor probe uses `ssh://example.invalid` and a marker script in place of ssh. Real lane and fleet repos were never audited or written. Run against `684764...` and again against `79d9e124...`; outcomes matched.

| ID | Fixture | Base `4fe9339` (rc, observed) | Working `684764` (rc, observed) | Status |
|---|---|---|---|---|
| A0 | valid committed ledger (control) | 0 clean | 0 clean | control |
| A1 | committed ledger with Latin-1 byte, UTF-8 locale | 1, uncaught `UnicodeDecodeError` traceback | 2, `could-not-evaluate: ... output is not UTF-8` | fixed |
| A2 | valid UTF-8 ledger, `LC_ALL=C PYTHONUTF8=0` | 1, `decoding with 'ANSI_X3.4-1968' codec failed` (false "failed") | 0 clean | fixed |
| A3 | `refs/replace/<ledger blob>` to a forged row | 0 clean (forged row applied) | 1, uncorrected | fixed |
| A4 | fabricated correction, `refs/replace/<fake>` to a commit | 0 clean | 1, errata-invalid | fixed |
| A5 | valid unreachable correction, `refs/replace` to a blob | 1, errata-invalid (false "failed") | 0 clean | fixed |
| A6 | promisor remote + `core.sshCommand` marker, fake correction | 1; marker shows ssh invoked (`example.invalid git-upload-pack '/none.git'`) | 2, `partial clone (extensions.partialclone)`; no marker | fixed |
| A6b | promisor remote config only | 1; marker invoked | 2, `partial clone (remote.origin.promisor)`; no marker | fixed |
| A7 | textconv + smudge bound to ledger path | 1; no driver executed | 1; no driver executed | H1 (no default-path exploit) |
| A8 | textconv bound to fleet report path | 1; no driver executed | 1; no driver executed | H1 (no default-path exploit) |
| A9 | `info/grafts` hides omitted round commit | 0 clean | 2, `... rewrites history` | fixed |
| A10 | ASCII stdout, non-ASCII token in unmatched row | 1, `UnicodeEncodeError` traceback | 1, same | open O1 |
| A10c | UTF-8 stdout control | 1, `status=failed` (unmatched) | 1 | control |
| A11 | `--errata` file not UTF-8 | 2 | 2 | control, correct |
| A12 | UTF-8 BOM before ledger comment | 2, `malformed row` | 2 | I1 |
| A13 | ledger path is a symlink whose target text is a row | 0 clean | 0 clean | open O4 |
| A14 | correction `HEAD` | 0 clean | 1, errata-invalid | fixed |
| A15 | `refs/replace` hides fabricated report token | 0 clean, `defects=0` | 1, uncorrected | fixed |
| A16 | one committed line with a bare CR holding two rows (`git show` shows 1 line) | 0 clean, 2 corrections applied | 0 clean, 2 corrections applied | open O2 |
| A17 | correction reachable only via `objects/info/alternates` | 0 clean | 0 clean | open O3 (documented residual) |
| A18 | dangling commit (no ref, no replace) as correction | 0 clean | 0 clean | open O3 |
| A19 | 7-hex correction that exists only as a branch name | 0 clean (accepted) | 2, `citation deadbee names a ref` (bare pass, lines 140-141; guard 162-164) | fixed |
| A19b | 40-hex correction that exists only as a branch name | 1, errata-invalid | 1, errata-invalid | control (object wins for full hex) |

## Findings (severity order)

### O2. Medium. A bare CR inside one ledger line creates a second, unseen row

- Evidence: A16. `git show` of the ledger gives one line; both arms apply two corrections (`corrected=2`, `status=clean`).
- Cause: `git()` maps every `\r` to `\n` (line 128). `parse_errata` splits on `\n` (line 352).
- Impact: a row a reviewer reading the ledger does not see can correct a defect, and the verdict is clean.
- Fix: read the ledger bytes raw in `load_errata` (no CR translation) and fail closed on any `\r` (`EvalError`, exit 2). Expected A16 then gives rc 2. Not run. Not covered by the grid (C07/C08 are report-side CR cases).

### O3. Medium (semantics). "Correction is a lane/fleet commit" means only "object exists in the audited view"

- Evidence: A18 (dangling commit) and A17 (object only via alternates) both give rc 0 on both arms. Validity is `status.get(correction) == "found"` (`apply_errata`, lines 396-398), where `lookup` runs `cat-file --batch-check` (line 145). That is existence, not reachability.
- Docstring: line 39 says "is not a lane/fleet commit"; lines 53-54 admit alternates as a residual.
- Grid cross-check: `tests/report-audit/repo-state-grid.py --arm current --case O01-alternates-foreign-object` prints `exit=0 kinds=[] ... NOT-MET`; the case expects exit 1 with unresolved kinds. That expectation contradicts the docstring's residual statement, and A17 shows the current tool resolves such objects. One of the two must change.
- Fix options: (a) reword line 39 to "present in the audited object view" and fix O01's expectation; or (b) require reachability (`git merge-base --is-ancestor <correction> <tip>` for lane-side, fleet HEAD for fleet-side). `landed-omitted` corrections are already reachable by construction (they must equal a `pre` commit). Choosing between (a) and (b) is a policy call for L1.

### O1. Low (exit contract). Output-encoding failure exits 1 with a traceback

- Evidence: A10 on both arms: `UnicodeEncodeError: 'ascii' codec can't encode character '\xe9'`, rc 1.
- Path: unmatched and invalid rows are printed raw (`render`, lines 520 and 522). `main` prints at 909-910 and catches only `EvalError` (912-914) and `OSError` (915-918). `UnicodeEncodeError` is neither.
- Contract: docstring lines 42-46 say output failure is 2, "Errors are never verdicts", and rc 1 means failed.
- Trigger: a non-UTF-8 stdout encoding plus a valid non-ASCII token, kind or correction in an unmatched or invalid row. Python's C-locale coercion probably avoids this on most hosts [INFERENCE]; it is reachable when coercion is off.
- Fix: write the rendered text as UTF-8 bytes to `sys.stdout.buffer` (or `ascii()`-escape raw ledger fields), and/or catch `UnicodeError` in `main` and return 2. Not covered by the grid.

### O4. Low. A symlink at the ledger path is parsed as ledger text

- Evidence: A13 on both arms; the symlink target `1<TAB>unresolved-full-hash<TAB><MASH><TAB><c1><TAB>sym` was applied.
- Inconsistency: `load_source_urls` requires a regular blob with mode 100644 or 100755 (lines 254-255). `load_errata` (lines 374-375) checks no tree-entry type.
- Fix: apply the same `ls-tree` type and mode check to `ERRATA`, or refuse non-regular entries with `EvalError`. Not covered by the grid.

### H1. Hardening, no present exploit. Ledger and report read with porcelain `git show`

- Lines: ledger read at 374, report read at 301. SOURCES uses `cat-file blob` (line 257).
- Control (A7/A8): textconv and smudge drivers bound through `.git/info/attributes` and `.git/config` are not executed by default `git show` on git 2.56.0 (no marker file, raw output). `git show --textconv` does run the driver, and `check-attr` confirms the attributes are live. So there is no present exploit on the default path.
- Fix: use `git cat-file blob <rev>:<path>` for the ledger and report reads, matching SOURCES. Not in the grid. Older git not tested.

### I1. Info. UTF-8 BOM before a comment is refused

- A12 gives rc 2 on both arms (`malformed row`). This is fail-closed, but a BOM'd ledger cannot be audited. Optional: strip a leading `\ufeff` in `load_errata`.

### I2. Info [code-read, not run]. Cross-repo abbreviation ambiguity resolves to `found`

- `lookup` (lines 153-156) records `ambiguous` only when the status is not already `found`. An abbreviation unique in one repo and ambiguous in the other is therefore `found`.

### I3. Info [code-read, not run]. Raw ledger fields reach the terminal

- `render` (lines 520, 522) prints token, kind and correction unescaped. Control characters in a ledger field would reach the terminal.

### I4. Info [design, code-read]. Evidence is never validated; non-resolvable corrections are not validated

- The evidence column is free text. For `landed-section-missing` (not in `RESOLVABLE`) the correction is never validated (`invalid` checks RESOLVABLE only, lines 396-398). A row with token `-` and any correction text clears that defect.

### I5. Info [design]. Unselected-round rows still fail the run

- `invalid` has no round filter (lines 396-398), so an invalid row for an unselected round fails the run. `unmatched` is checked only for selected rounds (lines 388-389). Consistent with the docstring; noted for the asymmetry.

### Nits

- `load_errata` labels parse errors with `args.branch` while reading `tip` (line 374-375).
- The usage line shows `[--errata PATH | --no-errata]`, but argparse does not enforce it. `--no-errata` silently wins (line 366).

## Grid coverage (`tests/report-audit/repo-state-grid.py`, read-only; I ran two single cases)

- Already covered: F16 (invalid UTF-8 ledger, A1), F17 (`HEAD` correction, A14), F03-F05 (replace on omission, citation, report), F06 (lazy fetch, A6), F10/F11 (shallow, grafts, A9), F13 (ref-named abbreviation on citations; the errata peel path is protected by the bare pass, A19), F23 (promisor pack without config), O01 (alternates; conflict in O3).
- Not covered by any grid case: A2 control, A3 ledger-blob replace, A5 correction-to-blob replace, A10 output encoding, A11 `--errata` flag, A12 BOM, A13 symlink ledger, A16 CR split, A18 dangling correction, A19 ref-only abbreviated correction.
- F20 (quotePath) still MET after the working copy dropped `core.quotePath=true` from `GIT_ISOLATION` (lines 94-97). No regression seen there.

## Not verified

- `--selftest` and the full grid were not run; only the O01 and F20 single cases. The "50/50" selftest claim is unchecked.
- Only git 2.56.0 and Python 3.14.8. Behavior of `--no-lazy-fetch` on git below 2.45 was not tested.
- Encodings tested: C.UTF-8, ASCII without coercion, ASCII stdout. No others.
- Promisor probe used a marker script on `example.invalid`; no network contact.
- I2 and I3 are code-read only.
- Line numbers refer to sha `684764...`. Re-check if the file changes again.

## Files written

- `.ufo/waves/round-23/build/advice/RevErrataPath.md` (this report).
- `.ufo/waves/round-23/build/out/RevErrataPath/errata-fault-probe.py` (reproducer).
- Throwaway, under /tmp only: `/tmp/kama-r23-rev-errata/` (`frozen.py` = base blob, `current.py` = `79d9e124...` copy, `current-2.py` = `684764...` copy, `probe2.json`, `fx/`, `bin/ssh-marker.sh`), and `/tmp/kama-r23-rev-errata-probe{,2,3}/`.
- Installs or updates: none.
