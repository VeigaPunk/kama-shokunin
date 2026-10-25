# ScribeCorrection — round 35, wave 1, attempt 1

Seat: ScribeCorrection. Judged on calibration. Draft only. Leaf; no subagent dispatch.

## Behavior

Read `tools/round35-statement-audit.py` and re-derived the four committed-byte facts `facts()` checks. Replaced the four lines in the seat draft so each id has one line the counter accepts. Did not edit `corpus/lessons/round-35.md`. Did not rewrite the filed r34 fleet report. Did not change either frozen predicate. No score move is claimed.

Axes:

- Calibration (judged): draft rows only. C1 remains 7 → 7 for the L1. This seat does not treat its draft as the landing of the frozen counting command.
- Coverage: not touched. C2 counter not run.
- Operability, depth, adjacency, discernment: not this seat's judged axes. Not touched.
- Axis authority: not touched. `MISSION.md` was not opened and not edited.

A prior `rows.md` and a prior `ScribeCorrection.md` were already on disk when this seat read them. Their command transcript is not this session's execution. The prior MAP line said the report sentence "is not a committed map edit". This seat had not diffed the round, so that line was replaced. The prior four lines were not passed to the counter before replacement.

## Gates

Predicate left unchanged: A frozen r34 self-assessment statement is corrected iff corpus/lessons/round-35.md contains a correction row naming its id, the counter re-derives the cited committed-byte fact, and the r34 fleet report blob is unchanged.

Draft check, after the final LIVE-line edit. This is not the frozen counting command.

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round35-statement-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --lesson /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-35/w1/out/ScribeCorrection/rows.md
```

Outcome, exit 0:

```
uncorrected 0 false_corrections 0 report_unchanged 1 met True
draft_exit:0
```

The same draft command, run once on the pre-edit four lines (LIVE cell still said `false`), also printed `uncorrected 0 false_corrections 0 report_unchanged 1 met True` and `draft_exit:0`. The file cited below is the post-edit text. That earlier pass is not re-used as the final draft result.

Frozen counting command, run once after the first draft write and before the LIVE edit:

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round35-statement-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin
```

Outcome, exit 0:

```
uncorrected 0 false_corrections 0 report_unchanged 1 met True
canonical_exit:0
```

That pass is the lesson file on the default path, not `rows.md`. The tool uses `corpus/lessons/round-35.md` unless `--lesson` is set. This seat did not write that lesson. See Conflicts.

On-disk do-nothing receipt, read, not re-executed: `.ufo/waves/round-35/controls/c1-noop.out` contains `uncorrected 4 false_corrections 0 report_unchanged 1 met False`. `.ufo/waves/round-35/controls/c1-selftest.out` contains `SELFTEST missing_met=False bad_met=False pass=1`. Neither file was regenerated here.

## Touched surfaces

- Replaced `.ufo/waves/round-35/w1/out/ScribeCorrection/rows.md`. Final observed size 993 bytes, 4 lines, mtime `2026-10-24T21:29:11-0300`. Not committed.
- Replaced this report, `.ufo/waves/round-35/w1/out/ScribeCorrection.md`. Not committed.

Not written by this seat: `corpus/lessons/round-35.md` (still mtime `2026-10-24T21:27:33-0300`, 5266 bytes, after the draft edits), the fleet report, product code, sibling seats, the Git index, jj state.

## Out of scope

- C2 coverage block, `corpus/knowledge/endpoint-health-probe-conventions.md`, and `tools/round35-coverage-audit.py`. Not written, not run. The lesson's Gate section was read and not judged.
- Candidate reject `hosted-health-route-configuration.md`. Not written.
- Staged package, quarantine rows, and `considerthese`. Not edited. Lesson quarantine notes were not re-derived.
- `MISSION.md`. Not opened, not edited. Axis authority not touched.
- Filed r34 report `/home/vgpnk/Projects/shokunin/.ufo/reports/round-34/kama.md`. Not rewritten.
- Working-tree `.ufo/waves/round-34/w1/out/dispatch-manifest.json`. Read only. Not staged, not edited.
- Service restoration, secrets, endpoint-admin state. Not touched.
- No commit, push, publish, deploy, or other runtime. No `git status` (it can refresh the index).

## Findings

A correction row is one line beginning `| R34-`. Required tokens must sit on that line. A row whose tokens disagree with the re-derived fact is a false correction.

| id | line must contain | line must not contain | fact this seat re-derived |
|---|---|---|---|
| R34-MAP | `false`, `719655f`, `serving-alias-contract.md`, `served-model-id-resolution.md` | `still on the map` | report contains `coverage map gains two entries` (count 1); `719655f:corpus/README.md` contains each filename 0 times |
| R34-R33COUNT | `false`, `23 untracked`, `1 modified` | `22 was correct` | report contains `22 untracked` (count 1); spotcheck contains `23 untracked` (count 2) and `1 modified` (count 1) |
| R34-LIVE | `not carried forward` | `processes are still live` | report contains `2 lane processes still live` (count 1); spotcheck contains `Do not carry that live count forward` (count 1) |
| R34-MANIFEST | `b784e1ab`, `lacks`, `Cannot combine --prompt with --auto` | (none coded) | report contains `dispatch-manifest.json` (count 1); committed manifest contains the error string 0 times |

Draft lines, the file just read back:

```
| R34-MAP | false | corpus/README.md at 719655f12517a9ce6b1a5ca44316897fed8420b0 contains serving-alias-contract.md 0 times and served-model-id-resolution.md 0 times; the frozen report sentence "coverage map gains two entries" naming those two files is false relative to that committed file |
| R34-R33COUNT | false | committed corpus/lessons/round-34-verifier-spotcheck.md at 719655f12517a9ce6b1a5ca44316897fed8420b0 states 23 untracked and 1 modified, against the frozen report's 22 untracked; that report count is not the spotcheck count |
| R34-LIVE | the frozen report sentence "2 lane processes still live" is not carried forward; committed spotcheck at 719655f12517a9ce6b1a5ca44316897fed8420b0 says "Do not carry that live count forward" |
| R34-MANIFEST | false | frozen report cites dispatch-manifest.json as recording the spawn error; committed .ufo/waves/round-34/w1/out/dispatch-manifest.json at b784e1ab273472eaa750fc10918ca4be67fa7697 lacks Cannot combine --prompt with --auto |
```

R34-LIVE does not use the word `false`. The counter does not require it. This seat did not re-check process liveness or seat-log mtimes. The cited fact is the spotcheck sentence, not a new live-process observation.

Frozen report quotes, from `git show 16cf603211cd08240e640ef72969d8eddb1410bd:.ufo/reports/round-34/kama.md`. Working-tree `git hash-object` of that path returned the same blob, so the working-tree read is the same bytes.

- Line 186: `coverage map gains two entries on the served-name/alias theme`, then `corpus/knowledge/serving-alias-contract.md` and `corpus/knowledge/served-model-id-resolution.md`.
- Line 114: `left 22 untracked`.
- Line 103: `2 lane processes still live`.
- Lines 104–105: `` `error: Cannot combine --prompt with --auto.` `` then `it is recorded in` `.ufo/waves/round-34/w1/out/dispatch-manifest.json`.

Pinned spotcheck quotes, from `git show 719655f12517a9ce6b1a5ca44316897fed8420b0:corpus/lessons/round-34-verifier-spotcheck.md`:

- Line 95: `porcelain shows 23 untracked plus 1 modified registry`.
- Line 96: `Do not carry that live count forward`.

Committed manifest at `b784e1ab273472eaa750fc10918ca4be67fa7697` parsed as JSON with keys `dispatchedAt`, `seats` (33), `transport`, `wave`. No `note` key. Error substring count 0. Blob length 7131. `dispatchedAt` value observed: `2026-10-24T20:37:01-0300`.

`corpus/README.md` at `719655f` has a `## Coverage map` table. The two reported filenames were not in the `knowledge/` lines extracted from that blob, matching the 0 counts. Nearby different names (`knowledge/alias-endpoint-normalization.md`, `knowledge/served-model-identity.md`) are present. This seat does not claim those other rows are the two the report named.

## Commands, outcomes, provenance

Read-only git. No `git add`, commit, checkout, reset, or mutating jj.

1. `git -C /home/vgpnk/Projects/shokunin rev-parse 16cf603211cd08240e640ef72969d8eddb1410bd:.ufo/reports/round-34/kama.md` → `7610d532696f5c6e214840fa2ec4112584589252`. Repeated after the draft edits; same hash. `git -C /home/vgpnk/Projects/shokunin hash-object .ufo/reports/round-34/kama.md` → the same hash, both times. `git merge-base --is-ancestor 16cf603211cd08240e640ef72969d8eddb1410bd HEAD` in the fleet repo → exit 0. `git cat-file -t 7610d532696f5c6e214840fa2ec4112584589252` → `blob`.

2. Report `git show` counts: `coverage map gains two entries` 1, `22 untracked` 1, `2 lane processes still live` 1, `dispatch-manifest.json` 1, `serving-alias-contract.md` 2, `served-model-id-resolution.md` 2, `Cannot combine --prompt with --auto` 1. Show stdout bytes 16816.

3. Lane `git rev-parse --verify` and `merge-base --is-ancestor` for `719655f12517a9ce6b1a5ca44316897fed8420b0` and `b784e1ab273472eaa750fc10918ca4be67fa7697` both ancestor exits 0. `git rev-parse HEAD` → `719655f12517a9ce6b1a5ca44316897fed8420b0`.

4. `git show 719655f12517a9ce6b1a5ca44316897fed8420b0:corpus/README.md`: `serving-alias-contract.md` 0, `served-model-id-resolution.md` 0. Blob from `rev-parse` of that spec: `df71357b4605858a014f90c08ca2c5fedb8f1a45`. Show bytes 35771.

5. `git show 719655f12517a9ce6b1a5ca44316897fed8420b0:corpus/lessons/round-34-verifier-spotcheck.md`: `23 untracked` 2, `1 modified` 1, `Do not carry that live count forward` 1, `22 untracked` 2, `2 lane processes still live` 1. Blob: `2888879c06d6bd4667219148e13c99e95abcba5f`. Show bytes 15309.

6. `git show b784e1ab273472eaa750fc10918ca4be67fa7697:.ufo/waves/round-34/w1/out/dispatch-manifest.json`: `Cannot combine --prompt with --auto` 0, `--auto` 0, `pid2` 0. Blob: `b32113564fd019bfaa60d14511abd91d080cfe74`.

7. Early `Path.exists` on `corpus/lessons/round-35.md` printed `round35_lesson_exists=False`. Later, after the lesson was on disk, the same check printed `True`. This seat did not create the file.

8. Draft and canonical audit outputs are under Gates. Draft audit was re-run once after the LIVE edit. Canonical audit was not re-run after that.

## Conflicts (verbatim for the L1)

1. Frozen counting command versus the do-nothing receipt, and versus this seat's first existence check.

Early this seat:

```
round35_lesson_exists=False
```

Later live command:

```
uncorrected 0 false_corrections 0 report_unchanged 1 met True
canonical_exit:0
```

Receipt file `.ufo/waves/round-35/controls/c1-noop.out`, read and not re-run:

```
uncorrected 4 false_corrections 0 report_unchanged 1 met False
```

The live pass is the lesson that appeared between those observations. It is not evidence that `rows.md` was copied into the lesson. Lesson mtime stayed `2026-10-24T21:27:33-0300` across this seat's draft edits.

2. Lesson rows already present, different from this draft. File header says `author: Kimi fresh L1`. This seat was ordered not to edit the lesson. Do not paste `rows.md` over these lines; `correction_line` keeps the first match per id.

Lesson lines 17–20:

```
| R34-MAP | false | README at 719655f lacks serving-alias-contract.md and served-model-id-resolution.md |
| R34-R33COUNT | false | the spot-check records 23 untracked and 1 modified |
| R34-LIVE | not carried forward | the r34 live-seat count is not a current fact |
| R34-MANIFEST | b784e1ab lacks Cannot combine --prompt with --auto |
```

The lesson LIVE cell says `is not a current fact`. This seat did not observe current process liveness. The draft does not say that. Both wordings satisfy `row_ok` given the derived facts this seat re-derived. Which sentence is the lesson's correction is the L1's verdict.

3. Committed manifest versus dirty working tree. Grep of the working-tree file, not edited:

```
.ufo/waves/round-34/w1/out/dispatch-manifest.json:271: "note": "first dispatch attempt failed instantly: 'error: Cannot combine --prompt with --auto.' -- 33 seats died at spawn, no seat work ran; re-dispatched with the --auto flag removed (same validated taskCall, same 33 lanes, no seat replaced or split)"
```

A later read of that working-tree file: bytes 8086, error-string count 1, `note` key present. Committed `b784e1ab` lacks the string. The draft cites the commit only.

4. Prior seat report, read before this replacement, claimed the frozen command exited 1 and that the lesson did not exist. That text is not this session's later command. This report replaces it. The prior `rows.md` MAP clause `is not a committed map edit` was not counter-checked before deletion.

5. Assignment text, not re-opened as `MISSION.md`, not edited, predicates not changed:

```
MISSION.md:29 still says operability + freshness. Do not edit it. Name the conflict if you touch axis authority. Do not change either predicate.
```

The lesson file, which this seat read and did not write, repeats that naming. This seat did not verify line 29 by opening `MISSION.md`.

## Known limits

- `23 untracked` and `1 modified` are committed spotcheck strings. This seat did not run `git status --porcelain` and does not recount round-33 leftovers.
- R34-LIVE is "not carried forward" per the committed spotcheck. No pid check was run.
- README absence is at `719655f12517a9ce6b1a5ca44316897fed8420b0`, which is also `HEAD`. No round-range diff was run to prove the file was never edited and reverted.
- `report_unchanged 1` is the fleet blob at `16cf603211cd08240e640ef72969d8eddb1410bd` matching `7610d532696f5c6e214840fa2ec4112584589252`, and the working-tree hash-object matching that blob at both checks. Not a new commit.
- Draft `met True` is `--lesson rows.md` only. Canonical `met True` is the pre-existing lesson. Neither is a calibration score change by this seat.

## Artifact paths

- `.ufo/waves/round-35/w1/out/ScribeCorrection/rows.md`
- `.ufo/waves/round-35/w1/out/ScribeCorrection.md`

Report: .ufo/waves/round-35/w1/out/ScribeCorrection.md
