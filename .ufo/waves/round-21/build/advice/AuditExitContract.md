VERDICT: partial - documented exit-2 inputs hold (missing report, bad UTF-8, unusable repo, malformed ledger), but missing git, a reversed --rounds range, output-channel errors and selftest aborts exit 1 or 0 as verdicts
Reviewer KamaR21.AuditExitContract-6 | target tools/report-landing-audit.py at a29bb84 (live copy cmp-identical) | git 2.56.0, Python 3.14.8 | 2026-10-21
Evidence: build/out/AuditExitContract/repro-exit-contract.sh (transcript repro-output.txt, 17 probe groups, read-only) and timestamp-probe.sh (timestamp-probe-output.txt). No tools installed. Scratch clone removed.
C1 counts reproduce: raw 9 (repro 0b), corrected 0 uncorrected (repro 0a), selftest cases=15 failed=0 (repro 0c).

## Findings (ordered by convention impact; every exit below was observed)
1. HIGH exit 1 traceback: git missing. `git()` (L61-67) checks only a nonzero rc; `subprocess.run` raises FileNotFoundError, which `main()` does not catch (L396 catches EvalError, ValueError). Repro 1: rc=1. Lane rule, error-is-not-a-verdict.md: "Missing docs/git already returned citation-checker exit 2". SKILL.md:652: "2 could-not-evaluate (unusable registry/docs/git)".
2. HIGH exit 0 vacuous pass: `--rounds 20-10 --no-errata` gives `reports=0 defects=0 ... status=clean`, rc=0 (repro 2). `parse_rounds` (L184-192) returns [] unchecked; `run` (L225-226) inspects only defect counts. With default errata the same selection gives rc=1 for the wrong reason (9 unmatched rows).
3. HIGH false failed from override handling. (a) `--report 19` (no =PATH) is accepted as "" (L199-201): rc=1 with 4 spurious landed-omitted; baseline `--rounds 19 --no-errata` rc=0 (repro 4). (b) L110 `cutoff = report_cutoff(...) if path is None else None` gives every explicit path now-cutoff. Docstring L22-24 says only uncommitted reports use now. `--report 19=<committed fleet path>` gives `report_committed=False`, rc=1; without override `True` (repro 5).
4. MED git failure recorded as a defect. `is_object` (L70-76) maps any nonzero `cat-file -e X^{commit}` to "absent". Ambiguous prefix f530ce0 becomes `UNCORRECTED landed-unresolved`, rc=1 (repro 11), while git exits 128 "short object ID f530ce0 is ambiguous" (bash probe). Absent-with-peel also exits 128 (repro 17), so exit status alone cannot separate absent from error.
5. MED clean verdict becomes exit 1 on output errors. `--json > /dev/full` gives an OSError ENOSPC traceback, rc=1 (repro 6). Reader closes early: BrokenPipeError, rc=1 (repro 7). `print` (L399) sits outside every handler. Closed stdout: rc=0 with no output (repro 8).
6. MED selftest abort exits 1. `if args.selftest: return selftest()` (L392-393) is outside the try; `_sh` (L256-258) uses check=True. A HOME gitconfig with `commit.gpgsign=true` gives a CalledProcessError traceback, rc=1 (repro 10), the same status as a failing selftest.
7. MED partial scope always fails. `apply_errata` (L170-175) marks rows of unselected rounds unmatched, so rc=1. `--rounds 10`: corrected=1 uncorrected=0 errata_unmatched=8, rc=1 (repro 3).
8. LOW-MED ledger classes. A correction that is not a commit gives `errata-invalid`, rc=1 (repro 14); an unknown kind gives rc=2 (repro 15). The stated convention says malformed ledger = 2. [INFERENCE] a git lookup failure (e.g. shallow clone) would also land in errata-invalid; not probed.
9. LOW over-broad exit 2. `str.splitlines()` (L90) splits on U+2028 in an unrelated commit subject: "not enough values to unpack", rc=2 for the whole audit (repro 12; control rc=0).
10. LOW hang. A FIFO as report path never returns: rc=124 under timeout 5 (repro 9). No exit code at all.

## Named suspects (all probed)
- split('\t',3) (L91): not an exit-1 path. A tab in an author name gives rc=0 (eval probe), because int() (L93) runs only for lane round rows. Only splitlines fragments fail the unpack (finding 9), so exit 2.
- int() on odd timestamps: unreachable. git refuses `@-1` and `@99999999999999999999` ("fatal: invalid date format"); `@0` and `@1700000000 +9999` give rc=0 (timestamp-probe). `report_cutoff` int (L100) only sees digits.
- UnicodeDecodeError on a report: exit 2 (repro 13). Invalid-UTF-8 commit subject: git re-encodes it, rc=0 (eval probe); no crash found.
- Symlink-loop repo path: git rc=128 gives exit 2 (bash probe); not an escape.

## Adjacent (not exit code)
- Numeric tokens in Landed changes are checked as commits: `1234567` and `20261021` give `landed-unresolved`, rc=1 (timestamp-probe). ABBREV (L51) matches any 7-40 hex run.
- Errata are read from the lane working tree (L207-208) while commits come from `--branch` (L86-87): the verdict depends on uncommitted state. [code read]
- `main` maps every ValueError to exit 2 (L396). [INFERENCE] a future bug of that type would report as could-not-evaluate.

## Coverage gaps
- `registry/error-injection-cells.json` (17 cells) has no cell for this tool; no SKILL.md row names it (repro 16 finds only the tool and its ledger).
- The selftest (15 cases, repro 0c) covers none of: missing git, empty range, output errors, FIFO, ambiguous prefix, committed-path override, U+2028.

## Suggested fixes (L1 decides; nothing applied)
- `git()`: catch OSError and raise EvalError. `run()`: EvalError on an empty round set; reject lo>hi in `parse_rounds`.
- `--report`: require a non-empty PATH; take cutoff from fleet history whenever the report exists there (drop `if path is None`).
- `is_object`: one `git cat-file --batch-check='%(objectname) %(objecttype)'` per repo: `missing` = absent, `ambiguous` = own defect kind, any rc!=0 = EvalError (verified rc=0, repro 17).
- `main()`: catch OSError around print and map to 2. `selftest()`: try/except to 2; add `-c commit.gpgsign=false` to selftest commits.
- `apply_errata`: unmatched only for selected rounds. errata-invalid = 2 unless the lookup said "missing".
- Reports/errata: check `stat.S_ISREG` else EvalError; use `split("\n")`, not `splitlines()`.
- Turn the 17 repro probes into selftest cases or error-injection cells.

## Not probed (verification gaps)
- MemoryError from huge --rounds ranges (parse_rounds materializes a list) [INFERENCE].
- GIT_DIR / GIT_INDEX_FILE leaking into selftest temp repos [INFERENCE].
- Corrupt-object or I/O errors in cat-file (only ambiguity was exercised).

Re-run: `bash build/out/AuditExitContract/repro-exit-contract.sh <lane> /home/vgpnk/Projects/shokunin <audit.py>` (about 8 s; read-only on lane and fleet).
