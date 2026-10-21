# RevRoundCommits: `round_commits()` and `report_cutoff()` in round 23

Seat: `CloseKama22.RevRoundCommits` (leaf, findings only). No production edits, no commits, no writes to the lane's tracked files, git index, or `.jj`. Scratch: `/tmp/kama-r23/CloseKama22.RevRoundCommits/`.

## Pins

- Base: `4fe9339f` (round-22). Blob `tools/report-landing-audit.py` = `fcc255ce5115a749dfbd09cf992ba9851a2dc90a`. The assignment's lines 147–168 match this base: `round_commits` 147–162, `report_cutoff` 165–168.
- The lane checkout changed during this review (tags `#D359`, `#8D0A`, `#0889` on successive reads). Two snapshots were probed:
  - S-A: sha256 `79d9e124e8171b47…`, blob `9755654a…`.
  - S-B: sha256 `684764108872cea1…`, blob `76fbf442…`, the checkout at write time. Current layout: `GIT_ISOLATION` 94–97, `round_commits` 181–197, `report_cutoff` 200–203, callers at 305 and 320, `check_history_repo` call at 479 (inside `run()`).
  - The `round_commits` and `report_cutoff` bodies are identical in S-A and S-B. The probe tables are identical (`results-79d9e124.txt` = `results-684764.txt`).
  - Against base, `round_commits` differs in two places: `errors="surrogateescape"` (line 183) and the 40-hex and digit guard (lines 191–192). `report_cutoff` is unchanged.
- Tools: git 2.56.0 and Python 3.14.8, both already installed. No installs or upgrades. No pacman.

## Summary

- Closed in S-B (verdict-changing or executing in base): `log.follow` (fleet), `i18n.logOutputEncoding` (lane), `log.showSignature` exec (lane), `log.showRoot` (fleet), `refs/replace` (lane and fleet), grafts and shallow (lane; refused by `check_history_repo`), a tag shadowing the branch name (lane; `resolve_branch`), and invalid UTF-8 in an unrelated subject (base traceback, S-B clean).
- No channel in these fixtures: `log.mailmap`, `diff.renames=copies`, `core.fsmonitor`, `log.diffMerges`, `diff.merges`, `trace2.eventTarget`.
- Open in S-B, all in record parsing of `round_commits`:
  1. Injected field separators forge atime, so a required commit is hidden: false clean (S10).
  2. Injected END forges a required record: false fail (S11).
  3. A 5000-digit field raises `ValueError` and exits 1 (S12). Exit 1 reads as a failed verdict.
  4. A subject in a non-ASCII-compatible encoding is invisible to `^round-N:`: false clean (S13, S13b, S13c).
  5. Forward-dated lane commits are `post_report` (S20). Design-level and documented as a limitation; not in the round-23 grid.
- A fail-closed parse candidate (probe only, not applied) refuses S10–S13c and leaves S0, S1, S14 unchanged. S20 needs a time rule.

## Probe method

- `probe/harness.py` builds 24 fixture pairs under `probe/fx/` (fresh repos under `/tmp`; `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`; `GIT_*` scrubbed). Commits are raw objects from `git hash-object --literally -t commit`, so header and message bytes are exact. It runs the CLI (`--rounds 23 --no-errata`) against base and S-B and prints function-level rows and cutoffs.
- Controls behave as expected in both: S0 (both cited) is clean, S1 (one cited) fails with `landed-omitted`.
- "correct" below means the verdict the file's own stated rules give for that fixture.

## Results (CLI rc; base = 4fe9339f, S-B = 684764)

| case | channel | base | S-B | correct | state |
|---|---|---|---|---|---|
| S2 | lane `i18n.logOutputEncoding=ISO-8859-1`, non-ASCII subject | rc1 UnicodeDecodeError | rc0 | 0 | closed |
| S3 | fleet `log.follow=true`, report renamed from draft.md | rc0, cutoff 1700000050 | rc1, cutoff 1700000200 | 1 | closed |
| S5 | lane `log.showSignature=true` + `gpg.program` marker + gpgsig commit | rc0, marker written | rc0, no marker | 0 | exec closed |
| S6 | lane `.git/info/grafts` hides L1 | rc0, rows [L2] | rc2 refusal | 2 | closed |
| S7 | lane `.git/shallow` hides L1 | rc0, rows [L2] | rc2 refusal | 2 | closed |
| S8 | lane `refs/replace/<L1>` | rc0, rows [L2] | rc1, L1 omitted | 1 | closed |
| S9 | lane tag `master` at L1, branch at L2 | rc0, rows [L1] | rc1, L2 omitted | 1 | closed |
| S14 | unrelated lane subject with `\xff\xfe` | rc1 UnicodeDecodeError | rc0 | 0 | closed |
| S15 | fleet `log.showRoot=false`, root commit adds report | rc2 no fleet commit | rc0 | 0 | closed (base refusal) |
| S21 | fleet `refs/replace` of add commit, date moved earlier (ad hoc, `probe/proto.py`) | rc0, cutoff 1700000010 | rc1, cutoff 1700000200 | 1 | closed |
| S4 | lane `log.mailmap=true` | rc0 | rc0 | 0 | no effect |
| S16a/b | report added by a merge; `log.diffMerges=separate` | rc2 | rc2 | refusal | no effect (add invisible by default) |
| S17 | fleet `diff.renames=copies` | rc0 | rc0 | 0 | no effect |
| S18 | lane `core.fsmonitor` marker | no marker | no marker | 0 | no channel |
| S19 | fleet `trace2.eventTarget` | no file | no file | 0 | no channel observed |
| S10 | lane author `kama-shokunin\x1f4000000000\x1fround-23: x` | rc0, rows [L2@4000000000] | rc0, same | 1 | OPEN, false clean |
| S11 | lane subject `…\x1e<fake 40-hex>\x1fkama-shokunin\x1f1700000000\x1fround-23: fake` | rc1, `landed-omitted` on fake | rc1, same | 0 | OPEN, false fail |
| S12 | lane author with 5000-digit field | rc1, ValueError traceback | rc1, same | 2 | OPEN, exit 1 |
| S13 | lane message UTF-16LE, no header | rc0, rows [L1] | rc0, same | 1 | OPEN, false clean |
| S13b | same, `encoding x-no-such-enc` | rc0 | rc0 | 1 | OPEN, false clean |
| S13c | same, `encoding UTF-16LE` (not a control: git did not transcode) | rc0 | rc0 | 1 | OPEN, false clean |
| S20 | lane author date 4000000000, uncited | rc0, rows [L2@4000000000] | rc0, same | design | OPEN |

## Findings (round_commits)

### F1. Injected separators forge atime (S10; high; open)

- L190: `fields = record.split(SEP, 3)`. `maxsplit=3` puts any extra 0x1f inside `%an` into the atime slot. The guard at L191–192 accepts digits, so it cannot see the injection.
- Observed: `rows [('L2', 4000000000), ('L1', 1700000000)]`. L2 is `post_report`, the report cites L1 only, and the verdict is rc0.
- [INFERENCE] A plain `git commit` with `GIT_AUTHOR_NAME` would keep a mid-name 0x1f (ident crud rules strip only the ends). The fixture used `hash-object --literally`, so the push and fsck path is untested.

### F2. Injected END forges a required record (S11; high-ish; open)

- L186: `for record in out.split(END):`. A 0x1e inside a subject starts a new record. That record is parsed as a kama round-23 commit with an attacker-chosen SHA. It is required (atime ≤ cutoff) and uncited, so it fails as `landed-omitted`, rc1.
- Direction: false fail, not false clean. The defect token was `1234567890abcdef1234567890abcdef12345678`.

### F3. Unbounded digit field exits 1 with a traceback (S12; medium; open)

- L196: `int(atime)` after the `[0-9]+` guard (L192), with no length bound. Python 3.14 limits int-string conversion to 4300 digits, so this raises `ValueError`. The exit code is 1, which is the failed-verdict code. The file's contract says errors are never verdicts.

### F4. Subjects that git cannot transcode are invisible (S13, S13b, S13c; high; open)

- `%s` of a UTF-16LE message is `r`, because git truncates at the first NUL. `git cat-file commit` shows `r\x00o\x00…`. `^round-N:` cannot match, so the commit disappears from `rows` with no error.
- The `encoding UTF-16LE` header (S13c) did not help. [INFERENCE] git re-encodes the whole buffer, and the ASCII header bytes make that iconv call fail, so the raw bytes pass through.
- `i18n.logOutputEncoding=UTF-8` in `GIT_ISOLATION` does not help. `surrogateescape` (L183) does not see the problem, because NUL is valid UTF-8.

### F5. Lane-authored times are trusted (S20; design; open)

- The docstring says lane commits "authored after the report are `post_report` and not required", and that clock skew across repositories is not detectable. A commit dated 2096 is not skew between two clocks that are both current. A `now + slack` refusal would catch it. [INFERENCE] Not run.

### F6. `report_cutoff` takes walk-order `out[-1]` (low; design)

- ORDER fixture: branch A adds the report (author 1700000100). Branch B adds it (author 1700000050, committer 1700000300). Merge M is TREESAME to A. `git log --diff-filter=A --format=%h %at %ct -- rel` lists only A's add. The cutoff is 1700000100 in both base and S-B. The earliest author time among the adds is 1700000050.
- History simplification hides the other parent's add. The effect is a later cutoff, so more commits are required. That can produce a false defect, not a false clean.

## Candidate fail-closed parse (probe only: `probe/proto.py`; not applied)

1. `git rev-list <tip>`, then `git cat-file --batch` over every commit. Refuse on a NUL byte or a non-UTF-8 `encoding` header.
2. `git log -z --format=%H%x00%an%x00%at%x00%s`: four NUL-separated fields per record, arity checked.
3. Refuse any record whose author or subject contains a control byte other than TAB.
4. atime must match `[0-9]{1,18}`.

Function-level results (`probe/proto-results.txt`):

- S0 and S1: same rows as before. S14: accepted, no regression.
- S10, S11, S12: `EvalError`, control byte in record.
- S13, S13b, S13c: `EvalError`, NUL byte in commit. The `encoding` rule is not isolated by any fixture; the NUL rule fires first.
- S20: accepted. Still open; needs F5.

Costs: it refuses the whole audit if any branch commit has control bytes, a NUL, or a non-UTF-8 encoding. It adds one `cat-file` over all of history. Exit 2 for S10–S13c through the CLI is inferred from `EvalError` → `main()`, not run, because no production edit was made.

## Recommendations (for L1; none applied)

1. Replace the in-band parse in `round_commits` with the fail-closed form above. This closes F1–F4.
2. Decide F5: refuse lane round commits dated beyond now + slack, or state the limitation in the docstring. Not validated.
3. Define `report_cutoff` explicitly: the minimum author time over add events, or refuse when more than one add event exists. Low priority.
4. `check_history_repo` (grafts, shallow, promisor) runs only from `run()` at L479. Either call it from the two functions or document that they assume it.
5. Add S10–S13c, S12, and S20 to the selftest. I did not run the selftest, so its status against S-B is unknown.
6. Consider `-c core.commitGraph=false` in `GIT_ISOLATION`. Not tested: I did not build a forged commit-graph.

## Not verified

- The selftest and the historical ledger were not run. No lane tests were run.
- Forged commit-graph, `.git` gitfile indirection, and alternates (documented as legitimate).
- Whether a push of these raw objects is accepted under default `receive.fsckObjects`. The fixtures bypass fsck.
- Outside my two functions, not re-run: `lookup()`, ref-named citations, promisor and lazy-fetch (faults c–e of the L1 probe, beyond S8, S9, S21), and invalid UTF-8 in the fleet report (fault b).
- Git versions other than 2.56.0.
- The lane file moved twice during the review. Findings apply to S-A and S-B only.

## Reproduce

```
cd /tmp/kama-r23/CloseKama22.RevRoundCommits
python3 probe/harness.py probe/snap-684764.py   # writes probe/results.txt
python3 probe/proto.py  probe/snap-684764.py    # writes probe/proto-results.txt
```

## Files written

- `.ufo/waves/round-23/build/advice/RevRoundCommits.md` (this report).
- `.ufo/waves/round-23/build/out/CloseKama22.RevRoundCommits/`: `harness.py`, `proto.py`, `results-79d9e124.txt`, `results-684764.txt`, `proto-results.txt`, `snap-79d9e124.py`, `snap-684764.py`, `base-4fe9339f.py`.
- Scratch only, outside the lane: `/tmp/kama-r23/CloseKama22.RevRoundCommits/` (clone at 4fe9339f; `probe/fx/` fixtures; `probe/t2/` trace2 probe).
