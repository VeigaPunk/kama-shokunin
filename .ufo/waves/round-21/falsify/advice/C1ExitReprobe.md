VERDICT: partial - 7/10 wave-1 findings fixed at a661714, finding 4 still open and its integrated fix is dead code (landed-ambiguous unreachable), finding 5 partially fixed, none newly broken in the 17 probe groups.
FALSIFY target: wave-1 exit-contract findings on tools/report-landing-audit.py, re-run at a6617149722c73d90e142fbdc8154d6967055f7e (vs wave-1's a29bb84; `git diff --stat a29bb84 a661714` on the file: 345+/187-).
Reviewer KamaR21.C1ExitReprobe | git 2.56.0, Python 3.14.8 | 2026-10-21 | no tools installed.
Commands: `bash .ufo/waves/round-21/build/out/AuditExitContract/repro-exit-contract.sh /tmp/kama-r21-C1ExitReprobe/lane /home/vgpnk/Projects/shokunin <clone>/tools/report-landing-audit.py` (exit 0) and `timestamp-probe.sh <fleet> <audit.py>` (exit 0); transcripts under falsify/out/C1ExitReprobe/. Every exit below was observed on the a661714 clone.

## Findings status (wave-1 numbering)
1. FIXED. git missing from PATH: `could-not-evaluate: cannot run git: [Errno 2] ... 'git'`, exit 2 (was exit 1 traceback). git() catches OSError -> EvalError (tool L81-90).
2. FIXED. `--rounds 20-10`: `could-not-evaluate: --rounds: empty range '20-10'`, exit 2 (was exit 0 vacuous pass). Documented in exit-2 list.
3. FIXED both halves. (a) `--report 19`: exit 2 `--report wants N=PATH, got '19'`; baseline `--rounds 19 --no-errata` exit 0. (b) `--report 19=<committed fleet path>`: exit 0, json report_committed=True cutoff=1792565257 required=8, byte-identical to no-override (was False/12 vs True/8, exit 1). Docstring: committed fleet report keeps first-add cutoff.
4. STILL OPEN + NEW DEFECT. Ambiguous 7-hex prefix: exit 1 `UNCORRECTED landed-unresolved f530ce0` — surface identical to wave-1 (ambiguity still conflated with absence, a verdict defect). NEW: the integrated `landed-ambiguous` kind (docstring L17, KINDS L61, C1 declared 5-kind list) is UNREACHABLE: Landed lookups pass peel `^{commit}` (tool L189), and `git cat-file --batch-check` answers `f530ce0^{commit} missing` for an ambiguous abbreviation (rc=0; `ambiguous` only without peel) — verified for f530ce0, 8c96006, d797c58 in a second 60k-commit repo (out/C1ExitReprobe/second-amb-sample-output.txt: landed-ambiguous_emitted=False x3). The elif at L194-195 can only fire from lookup states that the peel prevents; the no-peel path serves only 40-hex tokens, which cannot be ambiguous. Selftest (32 cases) has no landed-ambiguous case (grep 'ambig' over the tool: no case name). Does not taint the official b76727f3 measurement: its 9 confirmed defects are unresolved-full-hash/landed-omitted only.
5. PARTIALLY FIXED. (a) stdout=/dev/full: exit 2 `could-not-evaluate: output: [Errno 28] No space left on device` (was 1). (b) broken pipe: exit 2 `output: [Errno 32] Broken pipe` (was 1). (c) STILL OPEN: stdout closed (`>&-`) on a clean run: exit 0, 0 bytes stdout/stderr (repro 8; verified again in amb-and-stdout-probe-output.txt). Cause: CPython sees fd 1 closed at startup -> sys.stdout is None -> print() is a silent no-op, so the "output failure" the docstring promises to map to 2 never raises.
6. FIXED. selftest under HOME with commit.gpgsign=true + missing gpg: `selftest cases=32 failed=0`, exit 0 (was CalledProcessError, exit 1). git_env() strips GIT_*, pins GIT_CONFIG_GLOBAL=os.devnull.
7. FIXED. `--rounds 10` with default ledger: errata_unmatched=0, status=clean, exit 0 (was unmatched=8, exit 1). Unmatched rows now restricted to selected rounds.
8. RESOLVED AS DOCUMENTED (behavior unchanged from wave-1). Correction-not-a-commit -> `errata-invalid line=3`, status=failed, exit 1; unknown kind -> exit 2. Now consistent: docstring "0 clean (no uncorrected defect, no unmatched/invalid errata row); ... 2 ... malformed ledger" and SKILL.md:683 say the same, so exit 1 is the documented contract, not a convention conflict.
9. FIXED. Unrelated commit subject containing U+2028: control exit 0 and audited run exit 0 clean (was exit 2 unpack crash); records split on SEP/END sentinels, errata on split("\n").
10. FIXED. FIFO report path: exit 2 immediately (was hang, 124 under timeout 5); read_report checks stat.S_ISREG -> EvalError "not a regular file" (tool L158-161).

## Adjacent (wave-1 "Named suspects") re-checked
- Numeric tokens `20261021`/`1234567` in Landed: NO landed-unresolved anymore (timestamp-probe: defects=1, only the true `landed-omitted add59f7...`, exit 1). checkable_abbrev now requires a digit AND [a-f], so counting-only tokens are not citations — omission detection unaffected (required=1 still fires). Wave-1 adjacent complaint fixed; the probe script's stale "expect landed-unresolved lines for both" comment no longer describes the tool.
- Odd timestamps: git refuses @-1/@99999999999999999999; @0 and @1700000000 +9999 -> exit 0 clean. No int() crash. Unchanged-safe.

## Baselines (C1 cross-check)
0a default: reports=11 defects=9 corrected=9 status=clean exit 0; 0b --no-errata: uncorrected=9 exit 1; 0c selftest cases=32 failed=0 exit 0 (wave-1 had 15 cases) — matches the declared C1 numbers at b76727f3.
Controls (repro 13) all exit 2. Probe 16 now lists 5 referencing files (tool, ledger, corpus/QUALITY.md, corpus/lessons/round-21.md, SKILL.md:683-691): wave-1's coverage gap "no SKILL.md row" is closed; SKILL.md:688-691 adds the pre-commit checklist.

## Newly broken
None of the 17 repro groups regressed; the one new defect is finding 4's unreachable landed-ambiguous branch (advertised kind that cannot fire; git 2.56.0 semantics observed).

## Suggested fix (L1 decides)
Look up Landed tokens without peel, then peel-resolve only tokens whose bare batch-check says found: missing = landed-unresolved; bare-ambiguous = landed-ambiguous (docstring already promises this); rc/short-output = EvalError. Add a selftest case with a 60k-commit ambiguous repo and one asserting the kind. [INFERENCE for the exact patch shape; the observed git behavior is fact.]

## Not probed (gaps)
MemoryError from huge ranges; corrupt-object cat-file failures; blob-vs-commit ambiguity (only commit-commit ambiguity sampled, 4 prefixes total).
Scratch /tmp/kama-r21-C1ExitReprobe deleted after writing this report.
