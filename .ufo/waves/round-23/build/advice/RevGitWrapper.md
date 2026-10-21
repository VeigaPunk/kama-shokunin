# RevGitWrapper: exception escapes in `git()` / `git_env()` (round 23)

Seat: CloseKama22.RevGitWrapper (leaf reviewer). Findings only; no production edits; no subagents.

## Baseline and comparison

- **base** = `tools/report-landing-audit.py` at 4fe9339f (`git show 4fe9339f:tools/report-landing-audit.py`, 847 lines, sha256[:16] `09ecd63bdc3a5be5`). Scratch copy: `/tmp/kama-r23/RevGitWrapper/base/report-landing-audit.py`.
- **cur** = the lane working tree as it stood at my first eval step (921 lines, sha256[:16] `79d9e124e8171b47`). The file changed under me during review (my reads returned 847, then 864, then 921 lines), so `cur` is a snapshot, not necessarily the final candidate. Scratch copy: `/tmp/kama-r23/RevGitWrapper/current/report-landing-audit.py`.
- Interpreter: Python 3.14.8, git 2.56.0 (system). Default `--rounds` is `10-` (base line 820).

## Headline

1. **Base has three uncaught-exception classes that escape `main()`**, which catches only `EvalError` and `OSError` (base 835–843): `UnicodeDecodeError` (6 sites), `ValueError` from the CPython integer-digit limit (6 `int()` call sites), and `UnicodeEncodeError` (1 site, `print`). Each one exits **1**, the same status as a `failed` verdict. This contradicts the docstring "Errors are never verdicts" (base line 45).
2. **cur removes every `UnicodeDecodeError` escape I built** (bytes-mode `git()`, cur 107–126; stderr decoded with `errors='replace'`). It does **not** remove the `ValueError` or `UnicodeEncodeError` escapes.
3. **cur adds a silent false clean** (A2a): an invalid-UTF-8 author on a required round commit is dropped. Base crashed (exit 1); cur exits 0.
4. **Both versions false-clean a required lane commit** whose author name contains 0x1f (D1). Plain `git commit` stores it, and `round_commits` drops the commit silently.

## Reproduction

`out/CloseKama22.RevGitWrapper/probe-exceptions.py BASE CUR` (≈4 s). It builds fresh fixture repos in temp dirs with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`, never reads or writes the lane or fleet repos, and prints one row per case per script. Full output: `out/CloseKama22.RevGitWrapper/probe-output.txt`. The "Observed" column below is copied from that run.

Notation: **TB** = uncaught traceback (exit 1); **rc2** = could-not-evaluate (handled); **rc0/rc1** = clean/failed verdict.

## Enumeration: exception escapes in base

Why these escape: `git()` (base 87–97) converts only `OSError` (92–93). `subprocess.run(text=True)` decodes stdout and stderr inside the call (89–91) before the rc check (94–96). Callers catch `EvalError` only, except where noted. Non-git sites are listed under classes B and C.

### Class A: `UnicodeDecodeError`

| id | base site | concrete trigger | base | cur |
|---|---|---|---|---|
| A1a | `round_commits` `git log` (148–149) | lane `.git/config` `i18n.logOutputEncoding=ISO-8859-1` + non-ASCII subject (repo-controlled) | TB (0xe9) | rc0 |
| A1c | same | raw commit object with invalid-UTF-8 subject; round commit not cited | TB | rc1 `landed-omitted` (correct) |
| A1d | same | raw commit with invalid-UTF-8 author on a non-round commit | TB | rc1 (correct) |
| A2a | same | raw commit with invalid-UTF-8 author on the round commit; not cited | TB | **rc0 false clean** (X2) |
| A3 | `audit_round` `git show HEAD:rel` (266; `except EvalError` only, 267) | fleet report bytes not valid UTF-8 (fleet-controlled) | TB | rc2 |
| A4 | `load_errata` `git show branch:ERRATA` (339–340; unwrapped, unlike `--errata` at 334–338) | errata blob on lane branch not valid UTF-8 | TB | rc2 |
| A5 | `parse_rounds` `git ls-tree -r --name-only HEAD -- .ufo/reports` (381–382) | fleet `core.quotePath=false` + committed non-UTF-8 path under `.ufo/reports`. Run with `--rounds 1-`; default `10-` takes the same branch | TB | rc0 |
| A6 | `git()` stderr decode before the rc check (89–96) | CLI `--lane $'\xff'`: `git show` error echoes the bytes, so exit 1 instead of 2 | TB | rc2 |
| A7 | `git()` stdout decode, locale encoding | `LC_ALL=C PYTHONUTF8=0 PYTHONCOERCECLOCALE=0` (ASCII) + valid non-ASCII subject (env-only) | TB | rc0 |
| A8 | `lookup` `git cat-file --batch-check` (114–115) | ASCII locale + non-ASCII errata correction, which cat-file echoes | TB (decode) | **TB (encode at print, class C)** |

Control rows: A1b (same config, ASCII subject) rc0; A2c (valid author, not cited) rc1 `landed-omitted`; A4c (invalid errata via `--errata PATH`, wrapped 334–338) rc2; A9 (invalid `corpus/SOURCES.md`, wrapped 210–213 and 221–224) rc2.

### Class B: `ValueError` "Exceeds the limit (4300 digits) for integer string conversion"

| id | base site | trigger | base | cur |
|---|---|---|---|---|
| B1 | `parse_errata` `int(parts[0])` (324), reached from `load_errata` (339) | errata row whose round field has ≥4301 digits (lane-controlled). `load_errata` runs on every run without `--no-errata`, so this crashes with any `--rounds` selection (observed with `--rounds 1`) | TB | TB (cur 357) |
| B2 | `parse_rounds` comprehension `int(m.group(1))` (384) | fleet HEAD path `.ufo/reports/round-<4301 digits>/kama.md`, open-ended rounds (fleet-controlled). The int runs for every match before the `n >= lo` filter | TB | TB (cur 420) |
| B3 | `parse_rounds` `int(part)` (368), `int(m.group(1))` (373), `int(m.group(2))` (375); `run` `int(key)` for `--report` (398) | CLI `--rounds` with ≥4301 digits. Only the bare-number form (368 / cur 404) was run; the range bounds (373, 375; cur 409, 411) and the `--report` key (398; cur 470) are by reading | TB | TB (cur 404 run; 409, 411, 470 by reading) |

Not reachable: `report_cutoff` `int(out[-1])` (168) receives git `%at` output only. Not tested with `log.showSignature`.

### Class C: `UnicodeEncodeError`

| id | base site | trigger | base | cur |
|---|---|---|---|---|
| C1 | `main` `print(render(doc))` (832–833); errata lines in `render` (443, 445) | non-ASCII errata `correction`/`token` + non-UTF-8 stdout (`PYTHONIOENCODING=ascii`) | TB | TB (cur print 906) |
| C1c | control: `--json` | ASCII-escaped output | rc1 clean | rc1 clean |

### Handled correctly in both (exit 2, no escape)

- E1: symlink loop as `--lane-repo`. Python 3.14 `Path.resolve()` does not raise; git fails (rc128) → rc2.
- E2: stdout pipe closed before output → rc2 `could-not-evaluate: output: [Errno 32] Broken pipe`. No exit 120 observed.
- Read errors (`read_report`, 171–177), missing `--report` file, and `--errata` path errors are wrapped.

### Other exception checks

- Checked by reading every `[...]`, `int()`, `split`, `re`, and `Path` call: no `KeyError`, `IndexError`, `TypeError`, `AttributeError`, `RuntimeError`, or `re.error` is reachable from the base code paths I traced. Guards (e.g. `len(fields) != 4` before `fields[2]`, `len(cells) != 13`) hold.
- `--selftest` on base and cur: `selftest cases=50 failed=0`, rc0, no traceback (E4).

## Silent-verdict findings (not exceptions; same parser)

**X1 [High; base and cur] Framing false clean.** D1: a plain `git commit` with `GIT_AUTHOR_NAME=$'kama-shokunin\x1f1700000000'` is stored verbatim. Observed raw record: `<sha>\x1fkama-shokunin\x1f1700000000\x1f1700000000\x1fround-1: work\x1e`. Base 156 and cur 188 use `split(SEP, 3)`, so the extra SEP is absorbed into the last field. `fields[2]` still passes the digit check, and `pat.match("1700000000\x1fround-1: work")` fails silently. Result: base and cur both rc0 (`defects=0`), while the control D1c (plain author, same report) gives rc1 `landed-omitted`. cur's new sha check (189–190) does not catch this. Minimal fix: split without `maxsplit` and require exactly 4 fields, so the case becomes could-not-evaluate. Alternative: NUL-delimited format.

**X2 [High, cur regression; plumbing-only trigger] Invalid-UTF-8 author.** A2a: base crashes (exit 1); cur exits 0 with `defects=0`. Cause: cur 180–181 decodes the whole `round_commits` record with `errors="surrogateescape"`, so `author == f"{lane}-shokunin"` (193) fails silently for a lane author with invalid bytes. Fix: strict-decode the author field (EvalError on failure), and keep surrogateescape only for subject matching.

**X3 [Negative] textconv is not reached.** With a repo-local `diff.rep.textconv` and `.git/info/attributes` `diff=rep` (`check-attr` confirmed `rep`): default `git show HEAD:rel` (0 runs), `git log --diff-filter=A` (0), `git cat-file blob` (0), and the audit run (0). `git show --textconv` (1) and `git log -p` (1) do run it.

**X4 [Note] `git commit` re-encodes invalid bytes.** Commit `caf\xe9 work` is stored as `caf\xc3\xa9 work` (observed), and an invalid author is rewritten the same way. Invalid-UTF-8 metadata needs plumbing (`hash-object -t commit --literally`). A normal lane commit cannot produce it.

## Exit-status consequence

Every TB row exits 1 (observed). Python's uncaught-exception status equals the audit's `failed` status. A consumer that gates on exit 1 reads a tool error as a failed audit, and the cause appears only in stderr.

## Recommendations (for L1 decision; nothing implemented)

- **B:** replace bare `int()` on untrusted digit strings with a bounded parse that raises EvalError (length check or `try/except ValueError`) at lines 324, 368/373/375/384, and 398. Avoid changing `sys.set_int_max_str_digits` globally.
- **C:** make rendered errata text ASCII-safe (escape it) or reconfigure stdout errors in `main`.
- **X1:** `split(SEP)` without `maxsplit`, and require `len == 4`.
- **X2:** strict author decoding, as above.
- Keep cur's bytes-mode `git()` and stderr `errors='replace'`. Every UnicodeDecodeError trigger I built is handled by it (A1c/A1d/A2c/A3/A4/A5/A6/A7).

## Not verified

- Python below 3.11: no integer-digit limit, so class B would not occur. Not run, only 3.14.8 present. [INFERENCE]
- B3 `--report` digit key (read, not run); `report_cutoff` and `round_commits` with `log.showSignature` / gpg output (needs keys; ScoutShowSignature covers it).
- Lazy fetch / sshCommand, replace refs, grafts, alternates, safe.directory, fsmonitor: outside this seat's grid; not tested here.
- Historical ledger (rounds 10–22) under cur: not run (HistoricalNoHarm).
- cur beyond snapshot 79d9e124: the lane file kept changing, so results describe that snapshot only.
- Non-English git messages (`LANG`) affecting stderr: not tested.
- Real lane and fleet repos: not run against. I read only blob 4fe9339f:tools/report-landing-audit.py from the lane (read-only).
- Harness caveat: the eval kernel exports `PYTHONIOENCODING=utf-8`, so my first r5 row (cur, ASCII locale) showed success falsely. The probe and a bash rerun without that override show the expected `UnicodeEncodeError`. The table above uses the probe.

## Tooling

No installs or updates. Used the system `python3` 3.14.8 and `git` 2.56.0.

## Files written

- `.ufo/waves/round-23/build/advice/RevGitWrapper.md` (this report)
- `.ufo/waves/round-23/build/out/CloseKama22.RevGitWrapper/probe-exceptions.py` (reproducible probe)
- `.ufo/waves/round-23/build/out/CloseKama22.RevGitWrapper/probe-output.txt` (probe output)
- Scratch, not deliverables: `/tmp/kama-r23/RevGitWrapper/base/report-landing-audit.py`, `/tmp/kama-r23/RevGitWrapper/current/report-landing-audit.py`, `/tmp/kama-r23/RevGitWrapper/fx/` (earlier fixtures), `/tmp/kama-r23/RevGitWrapper/tmp/`, `/tmp/kama-r23/RevGitWrapper/out-*.txt`, `/tmp/kama-r23/RevGitWrapper/err-*.txt`, `/tmp/kama-r23/RevGitWrapper/closed.err`

## Revision note

Before handoff, the B3 row was corrected: only the bare-number `--rounds` branch (cur 404) was run; the range bounds (base 373, 375; cur 409, 411) and the `--report` key (base 398; cur 470) are checked by reading only. No other content changed.
