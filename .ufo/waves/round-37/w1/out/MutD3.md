# MutD3 — R36-D3 legs re-derived from committed bytes

No file outside this report path was created, edited, or deleted. All mutation
was string-level, in memory.

## Committed-byte location

The three cited artifacts are tracked in the lane repo at exactly one commit:

| path | blob state |
|---|---|
| `.ufo/waves/round-36/w3/out/seat-exit-codes.json` | added at `2e8beda5`, unchanged at `6a4afdfe` |
| `.ufo/waves/round-36/w3/out/ScribeLog/seat.log` | added at `2e8beda5`, unchanged at `6a4afdfe` |
| `.ufo/waves/round-36/w3/out/RevQ206/seat.log` | added at `2e8beda5`, unchanged at `6a4afdfe` |

- `2e8beda5` ("round-36: claim work …") is the parent of `6a4afdfe`, which is
  `master` and the C1 `BASE`. Prior history: `2e8beda5 → 9014843c → e5a8ecec`.
- The current `HEAD` is **detached** at `873c5d77` (the sandbox mutation line,
  `873c5d77 → f3bdcd03 → f3517a16 → 10094ed1 → 28a8bf50 → 9014843c`). At that
  HEAD the three paths are **absent from the tree** (`git cat-file -e
  HEAD:.ufo/…/seat-exit-codes.json` → "exists on disk, but not in 'HEAD'").
  Deviation under the counter: `load_facts(HEAD)` yields `exitcodes_len=0`,
  `seatlogs_len=0`, so even the true row fails `holds` there. This is a
  sandbox-HEAD artifact; at `BASE`/`master` (`6a4afdfe`) the facts load as
  `exitcodes_len=5736`, `seatlogs_len=4387`. `--selftest` at detached HEAD
  prints `pass=0` (`lesson_unchanged 0`, lesson blob `0418795f…` ≠ the frozen
  `6fb1ec15…`), while at `6a4afdfe` the lesson blob is exactly `6fb1ec15…` and
  the fleet report blob is exactly `8b7408e6…`. A round-37 tip descending from
  `BASE` therefore has the facts; a tip on the sandbox line does not.

## rc=1 seats (re-derived)

Parsing `git show 6a4afdfe:.ufo/waves/round-36/w3/out/seat-exit-codes.json`
(32 entries; rc histogram `{0: 24, 143: 6, 1: 2}`):

| seat | role | pid | rc | timed_out | log_bytes |
|---|---|---|---|---|---|
| ScribeLog | scribe | 3932019 | 1 | false | 156 |
| RevQ206 | reviewer | 3931925 | 1 | false | 4247 |

So **exactly two** seats are rc=1, and neither timed out: rc=1 here is the
provider error, not the harness timeout. The six rc=143 seats, all
`timed_out: true`, are CritC1Sound, MutLessonRow, MutRowPipe, ExecCounters,
ScribeQual, SentFinal.

## Log markers

Both committed logs contain both markers, once each:

| seat.log | bytes | `rate_limit` | `429` |
|---|---|---|---|
| ScribeLog/seat.log | 156 | 1 | 1 |
| RevQ206/seat.log | 4247 | 1 | 1 |

ScribeLog is nothing but `kimi version 2.3.1` + `error: failed to run prompt:
provider.rate_limit: 429 Rate limit reached for requests` + the log pointer.
RevQ206 is a full review transcript that terminates on the same two lines — it
was cut off mid-response. `git show 6a4afdfe:<path> | grep -o … | wc -l` gives
the counts above in both cases.

## Mutation probe

Mutant: the smallest behavior-bearing point — flip the two rc=1 entries'
`"rc": 1` to `"rc": 143` in the committed JSON (`re.sub(r'"rc": 1(\s*[,\}])')`),
leaving every other byte intact. Detector: `tools/round37-statement-audit.py`'s
own `score()`/`holds()`/`forbidden_in()` with the real base facts, a synthetic
lesson carrying all four correct rows, and the frozen lesson/report blob
constants.

Outputs (verbatim `emit`):

```
A true row: uncorrected 0 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met True forbidden=None
B six rc=143 only: uncorrected 0 false_corrections 1 lesson_unchanged 1 report_unchanged 1 met False forbidden='rc=143'
C six rc=143 + true names: uncorrected 0 false_corrections 1 lesson_unchanged 1 report_unchanged 1 met False forbidden='rc=143'
D restated as rc=0: uncorrected 0 false_corrections 1 lesson_unchanged 1 report_unchanged 1 met False forbidden='rc=0'
E true row vs mutated exitcodes (0 rc=1): uncorrected 0 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met True forbidden=None
```

Baseline legs on pristine bytes: `holds("R36-D3", true_row) = True`,
`rc1_count_literal 8` (`"rc": 1` substring-matches `"rc": 143`). Mutant is
valid JSON with histogram `{0: 24, 143: 8}` and **zero** rc=1 names.

**Verdict on the requested row: FAIL.** A row naming the six rc=143 seats is
killed twice over — `forbidden_in` returns `"rc=143"` on the literal (row B),
and it also lacks the required `ScribeLog`/`RevQ206` names and `429` (row C
supplies them and still loses to the `rc=143` literal). Note which leg does the
work: the failure comes from the forbidden-literal check and the required-name
check, **not** from `rc1` — the rc1 gate is vacuous, see below.

**Surviving mutant (coverage finding, not a contract change):** row E passes
`met True` against a file whose rc=1 count is zero, because
`exitcodes.count('"rc": 1')` also matches `"rc": 143` (8 ≥ 2). The rc1 leg
therefore does not discriminate rc=1 from rc=143 at all; it only fails when no
entry has an rc value beginning with `1`. Any future reliance on "rc1" as the
discriminator needs an exact-value parse, but the frozen predicate must not be
touched here.

## Restoration evidence

No target bytes were written, so before == after:

| file | sha256 before probe | sha256 after probe | committed (6a4afdfe) |
|---|---|---|---|
| seat-exit-codes.json | `bc75db5f05adacf2a77872357cac5d9bfb916557389fad0b59d3e5889799ea0a` | same | same |
| ScribeLog/seat.log | `908b38e3930819dc55a7ccc3ed0849ad8bf6a644dc91bce88b3f4155cc09ab91` | same | same |
| RevQ206/seat.log | `6d0cb7c6ec35bcc60ce6e88a7256a3b40a4297190895a41685426949300e7ef9` | same | same |

On-disk and committed bytes are identical for all three artifacts. Mutant hash
(in memory only): `0b37e8a8dd20b91a9fb84e3e9c5d3ecc851c4cc8bbeabb54963ebdee3b4b911e`.
No `git`/`jj` mutating command, no subagent, no network fetch was run.
