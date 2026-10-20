VERDICT: confirm — duplicate-name case writes only under a TemporaryDirectory, all 4 original malformed cases still rejected, and SKILL.md's "5 rejected schema cases" is accurate at 54a2926.

Seat: KamaR17.CheckPySelftestScope · Round 17 falsify · target revision
`54a29268e2083caa2b1e0d54ee1e7d90961302f3` (clone verified at that SHA,
clean tree). All paths below relative to the lane root unless absolute.

## Attacked

1. Write scope of `tests/probe-verdicts/check.py --selftest`: does the
   duplicate-name case ever write outside `tempfile.TemporaryDirectory`
   (i.e. into the matrix dir)?
2. Do the 4 original malformed selftest cases survive unchanged and still get
   rejected by the current validator?
3. Is `SKILL.md:570` "5 rejected schema cases (4 malformed + duplicate name,
   in a temporary directory)" accurate?
4. Runtime behavior: full-matrix-first, exit codes, port usage, residue.

## Findings

**F1 (A1, confirm) — duplicate-name case writes only under TemporaryDirectory;
matrix dir untouched.**
Code: `tests/probe-verdicts/check.py:541-547` writes `a.json`/`b.json` under
`tempfile.TemporaryDirectory(prefix="kama-check-selftest-")` and calls
`load_matrix(tmp_path)` with the temp dir explicitly — the `CHECK_DIR` default
is never used in the selftest (`check.py:547`, "Proven in a temp dir — never
in the real matrix directory"). `load_matrix` itself only globs and reads
(`check.py:152-175`).
Runtime (strace 7.2, `strace -f -qq -e trace=openat`, whole run incl. probe
children): 24,198 openat calls; 959 write-mode opens, of which 670 under
`/dev`, the rest under `/tmp` — **0 write-mode opens under the clone tree,
0 under the lane tree**. The only selftest-originated writes were
`/tmp/kama-check-selftest-ctcey64k/a.json` and `.../b.json` (one temp dir,
exactly the two files). The other `/tmp` writes are the probe's own
`/tmp/kama-probe.*` mktemp scratch (72 dirs, all self-cleaned). All 255 clone
openats are read-only (check.py, the 9 matrix `*.json`, `tools/kama-probe.sh`,
dir listings). File-list snapshot before vs after: identical (903 files), and
post-run `git status --porcelain` in the clone is empty (0 lines), which also
rules out rename/unlink/in-place content edits that openat-only tracing would
miss.

**F2 (A2, confirm) — the 4 original malformed cases are byte-unchanged and all
still rejected.**
`check.py:494-515` `SELFTEST_MALFORMED` vs frozen copy
`.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py:359-380`: identical
tuples; the frozen→current diff (299 lines) touches the selftest section only
in docstring wording, `--help` text and the added temp-dir duplicate block —
no `+`/`-` line on any of the 4 malformed entries. Runtime, each rejected with
its intended detector:
- `unknown test key` → "unknown test keys: ['bogus']"
- `non-integer route status` → "route.status must be an integer"
- `exit outside {0,2}` → "expected.exit must be 0 or 2"
- `MODEL_OK paired with exit 2` → "expected.exit 2 inconsistent with verdict
  MODEL_OK (probe exits 0)"
(and the added `duplicate test name across files` → "duplicate test name
'selftest-dup' (first defined in a.json)"). JSON doc: `malformed_tests=5,
rejected=5, passed=true`.

**F3 (A3, confirm) — SKILL.md "5 rejected schema cases" is accurate.**
`SKILL.md:570`: "`--selftest`: full matrix plus 5 rejected schema cases
(4 malformed + duplicate name, in a temporary directory)". Observed: exactly
5 results, 5 rejected; matrix 72/72 first. Consistent with
`check.py:29-31` ("feeds 4 embedded malformed tests … checks the duplicate-name
guard across two files") and `--help` (`check.py:613-615`, "4 embedded
malformed tests and a duplicate name") and with
`corpus/lessons/round-17.md` §Measurements "check.py --selftest 72/72 + 5/5".
Nuance, not a defect: the "in a temporary directory" clause attaches to the
duplicate-name case; the 4 malformed cases are validated in memory and never
touch the filesystem. Cosmetic nit only: the JSON key `malformed_tests: 5`
counts the duplicate case as "malformed" (`check.py:555`) — a label misnomer
in machine output; the human summary and SKILL.md wording are correct.

**F4 (context, confirm) — full-matrix-first, exit codes, ports.**
`main()` loads and grades the real 72-row matrix before running the selftest
(`check.py:626-640`, `grade()` loop), matching SKILL.md "full matrix plus".
Stubs bind `("127.0.0.1", 0)` (`check.py:429`) and closed-port rows use
`bind_closed_port()` on port 0 (`check.py:267-275`) — kernel-assigned
ephemeral loopback only; 8080, 34113 and no registry consumer port contacted.
Selftest failure propagates: `code = 1` when `st["passed"]` is false
(`check.py:651-654`) — not exercised to failure here (out of scope: the claim
under attack is scope/coverage, not the failure path; the fault-detector side
is covered by `fault-controls.py` F1-F8 per C1).

## Commands run (all in /tmp/KamaR17.CheckPySelftestScope-clone, cwd=clone root)

- `git clone -q <lane> /tmp/KamaR17.CheckPySelftestScope-clone && git -C …
  checkout -q 54a2926…` → HEAD `54a29268e2083caa2b1e0d54ee1e7d90961302f3`,
  `status --porcelain` 0 lines. Exit 0.
- `strace -f -qq -e trace=openat -o … env PYTHONDONTWRITEBYTECODE=1 python3
  tests/probe-verdicts/check.py --selftest --json` → exit 0; 72/72 passes,
  selftest 5/5; tree snapshot before==after (`TREE_UNCHANGED`, 903 files).
- `PYTHONDONTWRITEBYTECODE=1 python3 tests/probe-verdicts/check.py --selftest`
  (plain) → exit 0; "tests=72 passes=72 failures=0 / selftest: 5/5 malformed
  tests rejected (ok)".
- `diff -u frozen/tests_probe-verdicts_check.py clone/tests/probe-verdicts/
  check.py` → exit 1 (expected; 299 diff lines), selftest hunks inspected.
- `git -C clone status --porcelain | wc -l` after the strace run → 0.
- `ss -ltnp` → no listener of mine; 127.0.0.1:879x held by host shim services
  (`~/.local/share/*-shim/shim.py`, PIDs 1511-1517, started 09:57:11 today,
  hours before this seat). No llama-server started; nothing to tear down.

## Limitations

- strace traced `openat` only; completeness of "matrix dir untouched" rests on
  the post-run `git status --porcelain` (content) + file-list diff
  (existence), which together cover create/modify/delete/rename of tracked
  files. Untracked leftovers: none (status empty).
- 504 strace lines were `<unfinished …>` interleavings; sampled ones are
  O_RDONLY library/locale loads. A write-mode open hiding in an unfinished
  line would still have left content evidence, which `git status` excludes.
- `malformed probe output` grading itself (F8) not re-derived here; sibling
  seats own the fault-control and mutant-grid numbers.
- One transient `/tmp/kama-probe.*` dir observed between my runs and gone on
  recheck — [INFERENCE] a sibling seat's concurrent probe scratch; names are
  mktemp-unique, no collision risk observed.

## Installs

None. Used host `strace 7.2` (`/usr/bin/strace`), Python 3.14.8, git 2.56.0.

## Scratch

`/tmp/KamaR17.CheckPySelftestScope-clone` and all
`/tmp/KamaR17.CheckPySelftestScope-*` files removed after writing this
report. No lane file other than this report was written.
