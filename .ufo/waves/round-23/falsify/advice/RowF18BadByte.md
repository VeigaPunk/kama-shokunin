# F18-bad-byte-unrelated-subject — falsification attempt

**Verdict: HOLDS.** The fault premise is real and reproduces in the frozen arm
(exit 1, UnicodeDecodeError traceback), and the graded expectation (exit 0,
no defects) is the semantically correct outcome, not merely what the current
arm happens to do. I found no undeclared wrong verdict in the same
non-UTF-8-log-output channel. One adjacent, non-C1 observation (13-digit
author timestamps now refused) is recorded below; it is a deliberate cap
(mutant M25), not a crash/flip/hang/execution and not a falsifier of F18.

All line numbers below are at lane commit
`245a37f69628c2c6bb29bbf17897d8fb5946c857` (clone
`/tmp/kama-r23w2/RowF18BadByte-2`, `git rev-parse HEAD` verified equal).
Frozen blob is
`4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py`.

## Fixture under test (grid definition at 245a37f6)

`tests/report-audit/repo-state-grid.py:414-421` (`_bad_subject`) builds:
lane with `round-1: work` (author `kama-shokunin`, author time 1000, cited),
then a raw commit on the same tree, parent = cited commit, message
`note caf\xe9\n` (lone 0xe9), author `kama-shokunin`, author time 1100,
`refs/heads/master` moved to it; fleet commits the report citing the first
commit (author time 2000). Row and expectation:
`tests/report-audit/repo-state-grid.py:560`
`("F18-bad-byte-unrelated-subject", "fault", f_bad_subject, 0, [])`.

`caf\xe9` is Latin-1 é. The object is creatable by ordinary `git hash-object`
(no `--literally`): git fsck accepts non-UTF-8 message bytes, so this is
plain repository-local state, not a crafted malformed object.

## Method — hand rebuild, no grid import

I rebuilt the fixture by hand with git plumbing in fresh `/tmp` repos
(`GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`, explicit identity,
author/committer dates pinned), using `git hash-object -t commit -w --stdin`
for the raw commit and `git update-ref refs/heads/master`. I did not import
`repo-state-grid.py` anywhere in the rebuild or the oracle. Repro script:
`/tmp/kama-r23w2/f18lab.py`; standalone plumbing repro:
`/tmp/repro` (built by the bash snippet in this seat's run).

Hand-fixture observation with the exact log invocation the auditor uses:

```
$ git log -z --format=%H%x00%an%x00%at%x00%s refs/heads/master   # raw byte check
  stdout contains ... \x00note caf\xe9\x00 ...   (strict UTF-8 decode fails)
$ python3 <frozen blob> --lane-repo lane --fleet-repo fleet --json --rounds 1 --no-errata
  exit 1
  Traceback (most recent call last):
    ...
    File "/usr/lib/python3.14/subprocess.py", line 1099, in _translate_newlines
      data = data.decode(encoding, errors)
  UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 68: invalid continuation byte
$ python3 tools/report-landing-audit.py --lane-repo lane --fleet-repo fleet --json --rounds 1 --no-errata
  exit 0
  {"summary": {"defects": 0, "uncorrected": 0, "status": "clean", "required_commits": 1, ...},
   "results": [{"round": 1, "required": 1, "round_commits": 1, "defects": []}]}
```

Cross-check with the committed grid itself (read-only, temp only):

```
$ python3 tests/report-audit/repo-state-grid.py --arm both \
    --case F18-bad-byte-unrelated-subject --json
  frozen : exit 1, kinds "unparseable", traceback true,
           "UnicodeDecodeError: ... byte 0xe9 in position 68", met false
  current: exit 0, kinds [], traceback false, met true
  auditor sha256 current f228f174...928a7 / frozen 09ecd63b...b3f3f
```

### (1) Fault premise: REAL, observed in frozen

- Frozen's `git()` decodes via `subprocess.run(..., text=True)` with no
  error policy — frozen blob `:87-91`; the decode happens inside
  `subprocess._translate_newlines`, so `UnicodeDecodeError` escapes the
  `except OSError` and exits 1 as a traceback (never `EvalError`). The crash
  is in `round_commits` -> `git log` (frozen `:148-150`), i.e. the same
  command the current fix hardened.
- The fault materializes for a *non-round* commit's subject, exactly as the
  row claims: the bad byte is not needed for any verdict decision, yet the
  frozen arm dies before evaluating.
- Current arm impact: none. `round_commits` at `tools/report-landing-audit.py:180-201`
  decodes with `errors="surrogateescape"` (`:184`) and never re-emits the
  subject (the render path prints only round/required/post_report counts and
  hex defect tokens; `subject` is stored but unused after the prefix match).

### (2) Expected outcome (exit 0, no defects): CORRECT

Independent reasoning against the documented contract
(`tools/report-landing-audit.py:21-24`): a `landed-omitted` defect is "a lane
commit by `<lane>-shokunin` whose subject starts `round-N:` or
`checkpoint(rN)` and whose AUTHOR time is no later than [the report cutoff],
not cited". In this fixture the only such commit is the cited `round-1: work`
commit. The `note café` commit fails the subject-prefix predicate in its own
bytes (its first bytes are `note caf`), so it is not a required commit; the
report cites every required commit. Correct result: exit 0, `defects: []`.

The expectation is not vacuous and not "whatever current does": the same
channel with the byte moved into a round-prefixed subject must produce
`landed-omitted`, and both the grid row F19 and my hand probes do:

```
$ # same fixture, message "round-1: caf\xe9\n"
  current: exit 1, kinds ["landed-omitted"], required 2 (grid F19 met; V1/N8/N12)
  frozen : exit 1, traceback (no verdict)
```

So a resolver cannot pass F18 by blanket-swallowing bad bytes; the auditor
still keys the required set off the exact ASCII prefix and still reports the
omission when the bytes are in a required subject.

Exit 2 (refusal, documented at `:42-46`) would also satisfy C1's literal
prohibition (no crash/flip/hang/program), but it would be strictly worse here:
the required set is decidable byte-for-byte because the prefix match and the
author comparison are ASCII-only, and `surrogateescape` is a 1:1 byte
mapping. Exit 0 is the better and, I judge, the correct expectation.

### (3) Near variants of the same channel — none produce a wrong verdict

All hand-built, both arms run, clean env. `frozen`/`current` exit, kinds:

| Variant | frozen | current | correct? |
|---|---|---|---|
| bad byte in unrelated subject (F18) | 1 tb | 0 [] | yes |
| bad byte in round subject, uncited (F19) | 1 tb | 1 [landed-omitted] | yes |
| bad byte in round subject, cited (`checkpoint(r1)`) | 1 tb | 0 [] | yes |
| bad byte in author NAME of unrelated commit | 1 tb | 0 [] | yes |
| bad byte in author NAME of a round commit (not `kama-shokunin`) | 1 tb | 0 [] | yes — author predicate exact |
| bad byte only in message BODY | 0 [] | 0 [] | yes |
| bad byte in COMMITTER name (author clean, cited) | 0 [] | 0 [] | yes — `%an` only |
| `encoding X-NOT-A-CODEC` header | 1 tb | 0 [] | yes — git passes bytes, auditor ignores |
| `encoding caf\xe9` header (invalid bytes in value) | 1 tb | 0 [] | yes |
| repo `i18n.commitEncoding=ISO-8859-1` + raw 0xe9 | 1 tb | 0 [] | yes — `-c i18n.logOutputEncoding=UTF-8` does not reinterpret stored bytes |
| repo `i18n.commitEncoding=UTF-16` + UTF-16 message | 1 tb | 0 [] | yes — git emits BOM bytes, subject truncated at NUL |
| `encoding ISO-8859-1` header on the raw 0xe9 commit | 0 [] | 0 [] | yes — git re-encodes to valid UTF-8 |
| `.mailmap` / `mailmap.blob` mapping lane author away, `log.mailmap` false or **true** | 1 [landed-omitted] | 1 [landed-omitted] | yes — `-c log.mailmap=false` wins |
| `.mailmap` forging a stranger as `kama-shokunin` | 0 [] | 0 [] | yes — not honored |
| committed `corpus/SOURCES.md` containing `\xff` | 2 | 2 (EvalError, "not UTF-8") | yes — refusal, not crash |
| bad bytes before/inside the `round-1:` prefix, or `round-1:` mid-subject | — | 0 [] | yes — prefix is anchored |
| crafted NUL inside subject + forged record | 0 [] | 0 [] | yes (see below) |
| crafted NUL inside author name (`--literally` only) | 2 | 2 (EvalError, field shape) | yes — refusal, not crash |
| **valid 13-digit author timestamp (year ~33658)** | **0 []** | **2 (EvalError, "unexpected git log record")** | **over-refusal (see below)** |

**NUL injection is closed by git itself, not by luck.** The docstring at
`tools/report-landing-audit.py:181-182` claims git truncates names/subjects at
NUL. Verified with the auditor's exact invocation on a `--literally` commit
whose subject is `note\0ffff...\0kama-shokunin\01100\0round-1: forged`:

```
$ git log -z --format=%H%x00%an%x00%at%x00%s refs/heads/master
  fields: [sha, 'kama-shokunin', '1200', 'note', sha(lc), 'kama-shokunin', '1000', 'round-1: work']
  # %s is truncated at the NUL: no forged record, no field shift
```

A NUL in the author name makes `%at` empty (the date follows the name in the
author line), which current refuses with `EvalError` (exit 2), not a crash.
`git hash-object` without `--literally` rejects NUL commits (`nulInCommit`),
so that object is not ordinary repository-local state anyway.

**Randomized fuzz (oracle independent of the auditor):** 40 fixtures, bad
bytes 0x80/0x9f/0xa0/0xc3/0xe9/0xfe/0xff injected into unrelated subjects,
required subjects, cited required subjects, author suffixes and bodies;
expected verdict computed from the constructed bytes (author exactly
`kama-shokunin`, subject starts `round-1:`/`checkpoint(r1)`, uncited ⇒ one
`landed-omitted`). Result: `fuzz cases=40 mismatches=0` — no traceback, no
flip, no timeout.

**Adjacent observation (not the bad-byte channel, not a C1 breach):**
`round_commits` requires `atime` to match `[0-9]{1,12}`
(`tools/report-landing-audit.py:195-197`). A valid commit whose author time is
`1000000000000` (13 digits; git prints it and fsck accepts it) exits 2 with
"unexpected git log record", while the frozen arm evaluated it (exit 0). This
looks deliberate — `tests/report-audit/isolation-mutants.py:69-70` mutates
exactly this regex (M25) and the F26 reasons entry pins the refusal string —
so it is a declared-by-test shape cap, but it is not in the prose tradeoff
list and it is a coverage regression versus frozen. It cannot become a flip
(it raises `EvalError`), so it does not falsify C1 or F18.

## What I did NOT verify

- I did not re-run the full 26-row grid, the 8 controls, or
  `isolation-mutants.py`; the "26/26 faults met" and "22 killed" claims are
  outside this row. I ran only F18/F19/F20 rows (all `met: true` for current).
- I did not run the selftest or the rounds 10-22 ledger comparison.
- I did not test other lanes, other rounds, foreign-object alternates (O01),
  gitfile redirect (O02), ambiguous-abbreviation overwrite, second Landed
  section, or errata CR handling.
- I did not verify behaviour on git < 2.45 (the documented floor) or on
  Python versions other than 3.14.8 / git 2.56.0 on this host.
- No installs or upgrades were performed.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/falsify/advice/RowF18BadByte.md` (this report)
- `/tmp/kama-r23w2/RowF18BadByte-2/` (assignment clone at 245a37f6; no lane tracked file touched)
- `/tmp/kama-r23w2/RowF18BadByte-2-frozen-audit.py` (frozen blob copy)
- `/tmp/kama-r23w2/f18lab.py`, `/tmp/kama-r23w2/f18lab2.py`, `/tmp/kama-r23w2/f18fuzz.py` (hand fixtures/oracle)
- `/tmp/repro/`, `/tmp/f18lab-*`, `/tmp/f18lab2-*`, `/tmp/f18fuzz-*`, `/tmp/f18edge-*`, `/tmp/f18nl-*`, `/tmp/cfgprobe/` (scratch fixtures)
