Verdict: R4 delivered and self-tested — `seat-report-immutability.py` (lane-ready, `--repo/--rev/--rounds`, `--selftest` 13/13, exits 0/1/2, TMPDIR-honouring, read-only) grades 720 seat reports in rounds 46–52 at `c22602bd` and finds **8 rewritten in place, 1 rewritten then restored, 0 ungradable** (exit 1); the same instrument over the whole lane history reproduces exactly the ten reports the round-52 prototype named.

# X9Immut — round-53 w1, seat-report immutability instrument + measurement

Lane read through a `git clone --shared` at `/fast/scratch/hyaku/kama-r53/X9Immut/lane`
(`git rev-parse --show-toplevel` → that path). No lane file was edited; no fleet-root file
was written. No counter, preregistration or control was touched.

## 1. Deliverable

`seat-report-immutability.py` — sha256 `b346abe33b74a5363c6fde66f4db4d44cc3aafc692292b75ae4a92cfb6d5458e`,
24125 bytes, mode 0755. Written to this out directory; nothing was placed in `tools/`.

Contract (docstring is authoritative):

- **Population**: tracked paths matching `.ufo/waves/round-<N>/<wave>/out/**/*.md` at `--rev`,
  `<N>` selected by `--rounds` (`46-52`, `46,48,50-52`, `52`; default = every round present).
  `<stem>.late-rewrite.md` (the round-52 authorised-divergence sibling) is not a seat report.
- **Baseline**: the report's most recent *add* commit reachable from `--rev`, and that
  commit's blob. Delete+re-add and rename (no rename detection: read as D+A) restart the
  baseline, so a re-created report is not scored against its predecessor's bytes.
- **Violation**: tip blob ≠ baseline blob. A restoration (tip == baseline) prints
  `RESTORED`, not a violation. A present sibling does not excuse a divergent tip; it is
  reported as `sibling=matches|differs` on the same line.
- **Output**: one `REWRITTEN <path> first_add=… first_blob=… tip_blob=… commits=… later_blobs=… sibling=…`
  line per violation (commits and later blobs oldest-first; a deletion is `-`), `RESTORED`/
  `UNBASED` lines, and a `… rev=… rounds=… reports=… rewritten=… restored=… unbased=… met=…` summary.
- **Exits**: 0 clean; 1 ≥1 violation; 2 could-not-evaluate (not a repo, unresolvable `--rev`,
  git failure, empty population, or a report with no reachable add commit — an `UNBASED`
  report makes the whole evaluation incomplete, so it exits 2).
- **TMPDIR**: `_workdir()` calls `tempfile.mkdtemp(dir=os.environ.get("TMPDIR") or tempfile.gettempdir())`;
  the selftest asserts the fixture lives under `$TMPDIR` (`tmpdir-honoured` arm).
- **Repository**: every tree path is repository-root relative, so the tool re-binds to
  `git rev-parse --show-toplevel` and `--repo` may name any directory inside the worktree
  (`--repo <lane>/.ufo` grades the same 119 reports for round 46).
- **Read-only**: only `git rev-parse`, `git ls-tree`, `git log`, `git cat-file` (one log walk
  plus one batched `cat-file --batch-check`, so 720 reports grade in ~0.15 s). Verified:
  `git -C $S/lane status --porcelain` → empty after all runs.

Improvements over the prototype (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/W3Mistakes/seat-report-immutability.py`)
that matter for grading: batched git reads (~0.15 s vs ~2 min), the whole commit chain and each
intermediate blob instead of `mods[:1]`, restoration graded as `RESTORED` rather than skipped,
sibling bytes actually compared (`matches` iff the sibling holds a divergent blob), explicit
delete+re-add semantics, `--rounds` selection, and a tri-state exit that can say
could-not-evaluate (the prototype folded "no adds" into `continue`).

## 2. Selftest — 13 arms, 0 fail

Command and output: `selftest.out` (exit 0).

```
PASS tmpdir-honoured                        fixture=$TMPDIR/sri-… TMPDIR=…
PASS untouched-reported-once                reports=2 violations=0 exit=0
PASS late-rewrite-sibling-not-a-report      paths=2
PASS rewritten-in-place-exits-1             rewritten=1 exit=1 commits=eb1bfab27b14
PASS untouched-still-clean-in-same-tree     untouched_in_violations=False
PASS cli-prints-fields-and-exits-1          exit=1 lines=1
PASS sibling-matching-divergent-bytes       sibling=matches
PASS restoration-exits-0                    restored=1 violations=0 exit=0
PASS restoration-names-both-commits         commits=eb1bfab27b140f279a918cde
PASS delete-re-add-restarts-baseline        violations=0 exit=0
PASS rounds-filter                          exit(46-52)=0 exit(99)=1
PASS could-not-evaluate-exits-2             codes=[2, 2, 2]
PASS non-repository-exits-2                 code=2
SEAT_REPORT_IMMUTABILITY_SELFTEST pass=13 fail=0
```

Fixture commits carry fixed `GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE`
(`2026-10-27T00:00:00+00:00`) and `TZ=UTC`, so the arm output — including the `commits=`
prefixes above — is byte-stable between runs (two consecutive runs diff clean modulo the
random `sri-` fixture suffix).

The fixture is `D=$(mkdtemp -p $TMPDIR)`; `git -C "$D" init -q` runs first and the arm
asserts `git -C "$D" rev-parse --show-toplevel` (realpath) equals `D` before the first commit;
every fixture commit carries `-c user.name=sri-selftest -c user.email=sri-selftest@invalid
-c commit.gpgsign=false`. The required pair is `untouched-reported-once` (untouched report,
**exit 0**) and `rewritten-in-place-exits-1` (one report edited after its add, **exit 1**);
`untouched-still-clean-in-same-tree` shows the untouched report stays clean while its
neighbour is flagged in the same tree.

## 3. Real lane run at `c22602bd8d83ab26349d1087e916ca537ee4f9d1`, rounds 46–52

```
$ ./seat-report-immutability.py --repo $S/lane --rev c22602bd8d83ab26349d1087e916ca537ee4f9d1 --rounds 46-52
… seat-report-immutability rev=c22602bd8d83ab26349d1087e916ca537ee4f9d1 rounds=46-52 \
    reports=720 rewritten=8 restored=1 unbased=0 met=False
exit=1
```
Full receipt: `real-run.out`. Population cross-check: `git ls-tree -r --name-only c22602bd --
.ufo/waves | grep -E '^\.ufo/waves/round-(4[6-9]|5[0-2])/.*/out/.*\.md$' | grep -vc
'late-rewrite\.md$'` → **720**, equal to `reports=720` (per-round: 119/103/114/110/103/84/87,
one less than the raw `.md` count in round 51 = the `X7Regen.late-rewrite.md` sibling).

### Every committed seat report rewritten after its first add, rounds 46–52

| path | first add | first blob | later blob(s), in order | later commit(s) |
|---|---|---|---|---|
| `.ufo/waves/round-47/w1/out/S9Cap.md` | `383f1fc780573d46b6ea8bc1044b21f604e6ba3e` | `43aa30a9666d771d4c122942e6fd582a4bfcc3b4` | `833338b0e57c82e69f3b6bd8416fe1a9ae2616b8` | `6b7e6cf8d30b5794ed72fe97eb0e666f9b0572a9` |
| `.ufo/waves/round-47/w1/out/S9Cap/companion-head-and-province.md` | `383f1fc780573d46b6ea8bc1044b21f604e6ba3e` | `e5ed526043fb3a66b182e2cd51ff97bbd6876f72` | `b74d9e8cdab8e3dd783d8b7ccbf83ff02e716b0c` | `6b7e6cf8d30b5794ed72fe97eb0e666f9b0572a9` |
| `.ufo/waves/round-47/w1/out/S9Cap/receipt.md` | `383f1fc780573d46b6ea8bc1044b21f604e6ba3e` | `ef1878f304edc7f4edaeec548faa1c21655288ee` | `3a5a2c7d7696713d369f1cdc6ff3c28a6879a85f` | `6b7e6cf8d30b5794ed72fe97eb0e666f9b0572a9` |
| `.ufo/waves/round-47/w1/out/S9Scorecard/head-reanchors.md` | `383f1fc780573d46b6ea8bc1044b21f604e6ba3e` | `9d46d5cb776e3cfdef0fecd64473cbed5979de7e` | `8cd9ca9a17906300097acd7ce8a54841f9980426` | `6b7e6cf8d30b5794ed72fe97eb0e666f9b0572a9` |
| `.ufo/waves/round-48/w1/out/Sen2Live.md` | `f5c607875cdd9a4e057dfc893db6a6af2216a7b1` | `2c956487aeb6e7a6bb7bda44b6189682c4b8d8de` | `ca6ec2846cead0d83ca3fdca821f3608e2361094` | `4d8334af1c45bce74fa6a3904a7f6aa3a1ec630e` |
| `.ufo/waves/round-49/w1/out/Sen1Witness.md` | `24e906f034bc5635ee46d9743b1aa9ff93707362` | `1d324b1d2155b745befe4cf0965e0501debcf9e6` | `b072c16279c9e1da1fe6528f5aa324f976c21909` | `19c07aa9b3c25e0def4c3b09f3dbb1765f3ae84d` |
| `.ufo/waves/round-49/w1/out/X1Kill.md` | `24e906f034bc5635ee46d9743b1aa9ff93707362` | `647bc0e310106a2daef5f6dc50c9b6041637fe48` | `2284c057bab95cdcd3d46a79d66f6ab8a8b5c091`, then `14d3fb2797b3ec56c124014927a64af25e80a853` | `7fab24e74865cc18c53498e47670307569694d88`, then `19c07aa9b3c25e0def4c3b09f3dbb1765f3ae84d` |
| `.ufo/waves/round-49/w1/out/X1Sparse/table.md` | `24e906f034bc5635ee46d9743b1aa9ff93707362` | `72a0e48bf74976248defebcd94183f31c83f9f07` | `f62ca5761f62e0528edb6bca737f4d9430f6cc84` | `19c07aa9b3c25e0def4c3b09f3dbb1765f3ae84d` |

Every row has `sibling=absent`: none of these eight rewrites is accompanied by a
`<stem>.late-rewrite.md`.

Rewrite commits: `6b7e6cf8` "round-47: late seat report revisions (S9Cap, S9Scorecard)"
(2026-10-26T18:48:30-03:00); `4d8334af` "round-48: wave results (69/69 settled), seat yield,
late Sen2Live report" (19:54:23-03:00); `7fab24e7` "round-49: measured results at 24e906f0,
end census, misroot sweep" (20:41:53-03:00); `19c07aa9` "round-49: wave results, seat yield,
late seat reports and mutation findings" (20:43:13-03:00). The three round-47 rewrites share
one committing commit, as do three of the round-49 rows.

### Rewritten then restored (disclosed, not a violation)

```
RESTORED .ufo/waves/round-51/a2w1/out/X7Regen.md first_add=1ab1de3916d180a084ca9025b3f059aa6a5f38ce
  first_blob=d0be0660a46a26698499c1f0576c424d34564092 tip_blob=d0be0660a46a26698499c1f0576c424d34564092
  commits=9ff76b1f763512be2f554cbbfd0b2213b63b0847,5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8
  later_blobs=cc480230e7c18da9e6933269c0554e540274ca99,d0be0660a46a26698499c1f0576c424d34564092
  sibling=matches
```
`git rev-parse c22602bd:.ufo/waves/round-51/a2w1/out/X7Regen.late-rewrite.md` →
`cc480230e7c18da9e6933269c0554e540274ca99`, i.e. the sibling really holds the divergent bytes
the round-52 build (`5dacf2c7`) moved there.

## 4. Calibration evidence

- **Agrees with the independent prototype.** Round-52 Mistakes #8 named ten reports: `X7Regen.md`
  plus nine "still differ from their first-add blobs" — round-25 `a2-build/out/ReviewerC1Patch/evidence.md`,
  the four round-47 paths, round-48 `Sen2Live.md`, round-49 `Sen1Witness.md`, `X1Kill.md`,
  `X1Sparse/table.md`. This instrument reproduces that set exactly: rounds 46–52 give the eight
  above (all named by the prototype) plus `X7Regen` as `RESTORED`, and the whole-history run
  (`allrounds-run.out`, default `--rounds`, rounds 11–53, 1893 reports) gives
  `rewritten=9 restored=1` with the ninth row
  `.ufo/waves/round-25/a2-build/out/ReviewerC1Patch/evidence.md first_blob=708a42098c3e1206d91699b9f7715e10c6af0913
  tip_blob=3fa3f113f4564b00f4b420a7c2e2ddd9bb9dbda4 commits=c0a9b029c0355fedb6880541d95982849026f626`.
  Two independently written instruments, one path set, and mine adds the restored/disclosed split.
- **Fails before the fix it is meant to detect.** At `9ff76b1f` (round-51 salvage, before the
  round-52 restore) the same command reports `rewritten=9 restored=0` and a `REWRITTEN
  …X7Regen.md … tip_blob=cc480230… sibling=absent` row (`prerestore-run.out`, exit 1); at the
  build the same path is `RESTORED` (exit 1 on the other eight). A counter that could not see
  the pre-restore state would be vacuous here.
- **Discriminates per round** (`perround.out`): round 46 `rewritten=0 met=True` exit 0;
  47 `4` exit 1; 48 `1` exit 1; 49 `3` exit 1; 50 `0` exit 0; 51 `0 rewritten, 1 restored` exit 0;
  52 `0` exit 0.
- **Base is the same measurement, not a mutation.** At the round-52 tip `4229ea1b` the output is
  identical to `real-run.out` in every field except the printed `rev=` (`diff real-run.out
  base-run.out` → `10c10` only, the summary line), which is expected: the round-53 build
  touched no rounds 46–52 report, and the X7Regen restoration landed in `5dacf2c7`, before
  the base.
- **Exit-code arms** (`exitcodes.out`): `--rev no-such-rev` → exit 2
  (`could-not-evaluate: cannot resolve --rev`); `--rounds 46` → exit 0
  (`reports=119 rewritten=0`); `--rounds 46-52` → exit 1; a directory outside any repository
  (`$TMPDIR/not-a-repo`) → exit 2 (`… is not inside a git repository`); `--repo <lane>/.ufo`
  (a subdirectory of the worktree) → exit 0 with `reports=119`, showing the toplevel re-bind.
- **Independent blob checks** (plain git, not the tool): `git rev-parse
  "$(git log --diff-filter=A --format=%H c22602bd -- <p> | tail -1):<p>" c22602bd:<p>` for
  `S9Cap.md` → `43aa30a9…`/`833338b0…`; for `X1Kill.md` → `647bc0e3…`/`14d3fb27…`; for
  `X7Regen.md` → `d0be0660…`/`d0be0660…`. Per-commit blobs of `X1Kill.md`:
  `git rev-parse 7fab24e7:…` → `2284c057…`, `19c07aa9:…` → `14d3fb27…`. All equal the tool's rows.

## 5. Limits (stated so a reader does not over-read the 8)

1. Population is the tree at `--rev`: a committed report later *deleted* is out of scope. In
   rounds 46–52 no `.md` report was added and later deleted — the only two A→D paths in the
   range are `.ufo/waves/round-49/w1/out/Sen1Witness/evidence/validate-patch2.out` and
   `…/Sen1Witness/scripts/runFE-inf-and-sigkill.py` (both added `24e906f0`, deleted `19c07aa9`).
2. Rename is read as D+A, so a moved report restarts its baseline rather than being flagged.
   Measured: 0 paths in the range carry more than one add event.
3. `git log` is invoked without `-m`, so a report edited *only inside* a merge commit would be
   invisible. Two merge commits are reachable; `unbased=0` at `c22602bd`, so no report here is
   ungradable — but the instrument cannot prove a merge-only edit absent.
4. `sibling=matches` still exits 1. The lane rule is "never rewrite", so retention of the bytes
   is disclosure, not permission; the tool reports it rather than excusing it.
5. It grades bytes, not authorship or intent: an authorised L1 correction and a seat re-editing
   its own report are indistinguishable. Round-47/48/49's "late seat report revisions" commits
   are attributed to the committing commit only.
6. `--rounds` accepts only `N` / `N-M` / comma lists; no glob, no per-wave narrowing.

## 6. Integration note (not performed here)

`SCORECARD.md:3021` (§Planned (round 53), item 2) already names this deliverable: "land seat
W3Mistakes' seat-report-immutability and cited-path-exists checks as lane instruments". To land
it, copy this file byte-exact to `tools/seat-report-immutability.py` (sha256 above) and add a
`SKILL.md` instrument-registry row in the columns `gate-registry-check.py` grades (`Name | Kind /
entry command | Exit map | Self-test / pinned values | Write scope`), e.g. entry
`python3 tools/seat-report-immutability.py --repo . --rev <commit> --rounds <N-M>`, exit map
`0 none / 1 rewritten / 2 could-not-evaluate`, self-test `--selftest: 13 arms, fixture shows
0 and 1`, write scope `read-only`. `gate-registry-check.py` would then grade the row; no lane
edit was made from this seat.

Tools installed/updated: **none**. Servers started: **none** (`pgrep -af llama-server` → empty).
Scratch `/fast/scratch/hyaku/kama-r53/X9Immut` removed after the final runs; every cited receipt
is copied into this out directory.
