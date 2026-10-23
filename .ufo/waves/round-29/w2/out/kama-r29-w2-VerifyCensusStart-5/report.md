# w2 / VerifyCensusStart — `.ufo/waves/round-29/before/census-start.out` provenance + row count

Seat: kama-r29-w2-VerifyCensusStart-5 · 2026-10-23 · Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin` (branch master)

## Verdict

**The file is the attempt-1 round-start registry receipt: it was committed in the attempt-1 freeze commit `827d136546b85059a984b34970f5b493d9a71290` (2026-10-23T07:55:43-03:00), before any seat ran; its recorded exit code is `0`; its summary line is `kama ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`. It reproduces byte-for-byte from a fresh clone at base `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d` except for the `ok` line's path field.**

**BUT the assignment's premise is defective, and the L1 must know this before landing the narrative: the file records NO row count.** It is the output of `sources-census.sh validate` (mode `validate`), not of `sources-census.sh census` (mode `census`). The mode `census` is the only mode that emits a `rows` line; this file contains 83 `W04` warning lines, one `ok` line, and a seat-added `exit 0` trailer — zero `rows` lines. Consequently the check "verify the row count it records matches the base tree" has no row count to verify *in this artifact*. I therefore verified the row count by the two independent routes available, both of which agree on **173** at base.

Two further defects, both documentation-grade, are recorded below.

## The file, verbatim facts

Path: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/before/census-start.out`

| Property | Value | How measured |
|---|---|---|
| Bytes | 10843 | `wc -c` |
| Lines | 85 | `wc -l` |
| SHA-256 | `8871163aa09128650da1e805583dfa0e756ed03752dea468c8e95e4efa314cdf` | `sha256sum` |
| Git blob id | `eabf64031f5830b356677ccd2f9128f6fa4aa043` | `git hash-object` (== `git rev-parse HEAD:<path>`) |
| Recorded exit code | `0` | line 85: `exit 0` (space-separated; seat-authored trailer, not script output) |
| Recorded summary line | `kama<TAB>ok<TAB>/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md` | line 84 |
| E-code findings | **0** | `grep -cP '\tE[0-9]+\t'` → 0 |
| W-code findings | **83**, all `W04` | `grep -oP '\tW[0-9]+\t' \| sort \| uniq -c` → `83 \tW04\t` |
| Distinct S-ids in the W04 set | 83; max S-id = `S173` | `cut -f3 \| sort -u \| wc -l` |

### "Attempt-1 round-start" — confirmed by provenance, not by content

```
$ git log --format='%H %cI %s' -- .ufo/waves/round-29/before/census-start.out
827d136546b85059a984b34970f5b493d9a71290 2026-10-23T07:55:43-03:00 round-29: C1 freeze (calibration): counter, preregistration, base receipt, census start; before any seat

$ git show --stat --format='%H %s' 827d136546b85059a984b34970f5b493d9a71290
 .ufo/waves/round-29/before/c1-base.json     | 760 ++++++
 .ufo/waves/round-29/before/c1-base.out      |   2 +
 .ufo/waves/round-29/before/census-start.out |  85 +++
 .ufo/waves/round-29/count-c1.py             | 368 ++++++
 .ufo/waves/round-29/preregistration.json    |  52 ++
```

- The file was added by the freeze commit itself and by no other commit; `git log` on the path returns exactly one commit.
- Its blob is identical at the freeze commit, at `HEAD` (`513eba3ba51a142c9936553e3a85918345eb5c4c`) and in the working tree (`git rev-parse HEAD:<path>` == `git hash-object <path>` == `eabf6403…`) — i.e. it is untouched by attempt 2 and by the wave-1 edits.
- The freeze commit is the *first* commit after base: `git log 2aa46e24..827d136` returns only `827d136`. Base `2aa46e24` is dated `2026-10-23T06:55:34-03:00`, freeze `827d136` `2026-10-23T07:55:43-03:00` (= `10:55:45Z`, matching the assignment's stated freeze time).
- `corpus/SOURCES.md` is byte-identical at base and at the freeze commit (`git rev-parse 2aa46e24:corpus/SOURCES.md` == `827d136:corpus/SOURCES.md` == `dccc147ffbdf0098afb17276c37a59605a15d487`), so the registry the receipt describes is the base registry.
- The file's own mtime (`2026-10-23 07:55:13 -0300`) sits between the base commit (06:55:34) and the freeze commit (07:55:43), consistent with "captured at round start, committed at freeze".

## Reproduction from a fresh base clone — byte-for-byte

Scratch (this seat's own, deletable): `/tmp/kama-r29-w2-VerifyCensusStart-5/` — a `git clone --no-hardlinks` of the lane checked out at base `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d`, plus a copy of the fleet `shokunin.conf` so the census script resolves the `kama` lane by name. Nothing in the lane, the fleet repo, or the Git index was touched.

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /tmp/kama-r29-w2-VerifyCensusStart-5/root kama
exit=0 ; 84 lines ; cut -f2 | sort | uniq -c  ->  1 ok ; 83 W04

$ diff <(grep -v '^exit ' …/before/census-start.out) validate-clone.out
84c84
< kama	ok	/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
---
> kama	ok	/tmp/kama-r29-w2-VerifyCensusStart-5/root/kama-shokunin/corpus/SOURCES.md
```

**Exactly one differing line, and it is the `ok` line's path field** (absolute path of the tree that was checked). All 83 `W04` lines are identical in text and in order:

```
$ diff <(grep -P '\tW04\t' recorded) <(grep -P '\tW04\t' validate-clone.out)   -> W04-SET-IDENTICAL
$ diff <(… | cut -f3)              <(… | cut -f3)                              -> IDS-IDENTICAL
```

The same run against the **live** lane also exits 0 with the identical 83-W04 set (`diff` of the W04 blocks: `SAME`) — the four uncommitted `S174`–`S177` rows introduce no new warning and no error.

## Row count at base = 173 (both prescribed and script routes agree)

The assignment's check: `git show 2aa46e24:corpus/SOURCES.md | grep -c '^| S'`

```
$ git show 2aa46e24:corpus/SOURCES.md | grep -c '^| S'
173
$ git show 2aa46e24:corpus/SOURCES.md | grep -c '^| S[0-9]'
173
```

The census script's own parser on the same blob (`census --file <copy of the base blob>`) independently reports the same number:

```
file	rows	173
file	tier.A	168
file	tier.B	2
file	tier.C	3
file	status.mined	154
file	status.queued	8
file	status.rejected	11
FLEET	rows	173  …  FLEET	missing	0        (exit 0)
```

Cross-checks: base ids are contiguous `S001`–`S173` (no gaps, no duplicates); the highest S-id appearing in the receipt's own W04 set is `S173`, i.e. the last row of the base registry — consistent with the receipt having been taken against the base registry.

**Live (working tree) for contrast:** `census --root … kama` → `kama rows 177` (tier.A 172, tier.B 2, tier.C 3; mined 158 / queued 8 / rejected 11), exit 0. The +4 is exactly the uncommitted `S174`–`S177` rows in the working tree diff of `corpus/SOURCES.md`.

## Defects found (L1 must decide; I did not edit any lane file)

### D1 — MEDIUM: the receipt records no row count, so the narrative's row figure has no committed receipt

`census-start.out` is `sources-census.sh **validate**` output, not `census` output. Evidence:

- `scripts/sources-census.sh:766-780` — the `case "$MODE" in census)` block is the only place that emits `rows`, `tier.*`, `status.*`; `validate` (`:737-748`) emits only E/W findings plus the `kama ok <file>` line. The recorded file has 83 `W04` + `ok` + trailer and **no `rows` line** (`grep -c 'rows'` → 0; same for the round-28 file, so this is a lane-wide naming habit, not new in round 29).
- `grep -rlP '\trows\t\d+' .ufo/waves/round-29/` → **no matches**: no round-29 artifact carries a `rows` record. There is no `census-final` / `sources-census-after` receipt anywhere in the round.

Consequence: the attempt-1 narrative line in `LOG.md` (uncommitted diff, `LOG.md` +32) —

> "Sources S174-S177 (git-blame, git-merge-base, git-gitgrep + gitglossary, pretty-formats) opened this round; **census 173 → 177 rows, exit 0**."

— is *factually correct* (I measured 173 at base and 177 live, both exit 0) but is **not backed by any committed receipt**. The "173" and "177" and the "exit 0" for the after-state have no artifact in the round directory. A reader cannot re-derive them from what the round ships. The L1 should land a `census` receipt alongside the narrative (e.g. `.ufo/waves/round-29/final/census-<rev>.out` containing `census` mode output at the tip, and/or a `before/census-rows-base.out`), or cite the commands inline in the LOG entry.

### D2 — LOW: the receipt's trailer is seat-authored, not script output, and names neither the command nor the revision

Line 85 is literally `exit 0` (space, not `exit=0`). `scripts/sources-census.sh` never prints an `exit N` line — its only three `exit 0` occurrences are the script's own exit statements (`:100`-area, selftest path, `:803` final `exit 0`); stdout is TSV only. So `exit 0` is a hand-appended annotation. It is correct here (the run does exit 0, verified above), but the file records neither the command, the revision, the date, nor the run identity.

The lane's own round-27 precedent does better: `.ufo/waves/round-27/a3/census-start-0ec32cac.out` (committed) ends with

> `exit=0  # run 2026-10-23 by KamaR27A3: sources-census.sh validate --root /fast/scratch/hyaku/kama-r27/census-base kama, on a clone of the lane at 0ec32cac09b58a213450ff9f67c319100f21ac27 (round state before attempt 3; corpus/ unchanged since base a720399e), with the fleet shokunin.conf copied to …`

and `.ufo/waves/round-27/w1a3/advice/ReviewCensusStart.md` audited exactly that trailer ("Content is data; it does not alter the census contract"). The round-29 receipt carries no such annotation. Since the round-29 file's content is nonetheless fully reproducible from the freeze commit (shown above), this is a provenance-annotation gap, not a correctness defect — but it is worth restoring the round-27 trailer form, because the file as shipped gives a reader no way to know *which* tree produced it (the `ok` line points at the live lane path, which is the one thing that is *not* frozen).

### D3 — LOW: the `ok` line pins an absolute live-lane path into a frozen artifact

Line 84 ends `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`. In the round-27 artifact the same line pointed at the scratch clone the run actually used, so the path was itself evidence of the run's tree. Here it points at the live lane working tree, which is *not* the tree the receipt is frozen against (the receipt is committed at freeze and the working tree has since gained `S174`–`S177`). Reproduction is nevertheless exact (one path field differs), so this is cosmetic. Note the same absolute-path pattern recurs in the committed round-28 receipt, so it is inherited convention.

### D4 — INFO: the receipt's W04 set grew 50 → 83 versus round 28

Round 28's `before/census-start.out` (at base `2aa46e24`) carries 50 `W04` ids; round 29's carries 83. The 33 new ids are exactly `S141`–`S173` (the round-28 `server-schema.cpp` block). No round-28 id disappeared. This is expected — the `W04` "same URL across scopes" count grows with the registry — but it means "one known warning" wording carried in older lane advice (e.g. round-12/13/15 `CountsConnection.md`, `ReportScribe.md`: "one known scoped warning W04 S031") is stale for this round and must not be reused in the round-29 narrative. The round-29 receipt has **83** warnings, not one.

## Scope discipline

- Read-only everywhere except this seat's own output directory
  `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/kama-r29-w2-VerifyCensusStart-5/`
  and the scratch clone `/tmp/kama-r29-w2-VerifyCensusStart-5/`.
- No lane file was edited; no lane commit, `git add`, `checkout`, `reset`, or index mutation; no fleet repo, `.ufo/state/`, `MANIFEST.json`, or fleet script was touched. `git status --porcelain` in the lane is unchanged from the state I found (6 modified files + the same untracked entries).
- The census script is read-only by construction (`scripts/sources-census.sh:8` — "Read-only: … writes only stdout or --out"); I ran it with `--root` pointed at my scratch tree and with `--file` pointed at a copy of the base blob, and never with `--out` inside the lane.
- No tool was installed: every check used the already-present `git`, `bash`, `gawk`, `python3`, `sha256sum`, `diff`, `comm`. Nothing installed, nothing upgraded.

## Commands an integrator can re-run

```sh
# the receipt itself
sha256sum .ufo/waves/round-29/before/census-start.out          # 8871163a…4cdf
git rev-parse HEAD:.ufo/waves/round-29/before/census-start.out  # eabf6403…a043
git log --format='%H %cI %s' -- .ufo/waves/round-29/before/census-start.out   # 827d1365 only

# base row count (prescribed route) and script route
git show 2aa46e24:corpus/SOURCES.md | grep -c '^| S'            # 173
git show 2aa46e24:corpus/SOURCES.md > /tmp/base.md
scripts/sources-census.sh census --file /tmp/base.md            # file rows 173

# reproduction from a base clone (scratch only)
git clone --no-hardlinks <lane> /tmp/x/root/kama-shokunin
git -C /tmp/x/root/kama-shokunin checkout 2aa46e24
cp /home/vgpnk/Projects/shokunin/shokunin.conf /tmp/x/root/
scripts/sources-census.sh validate --root /tmp/x/root kama      # exit 0; 83 W04 + ok
diff <(grep -v '^exit ' .ufo/waves/round-29/before/census-start.out) /tmp/x/validate.out
# -> only the ok line's path differs
```

## Risks / blockers

- None blocking for C1: the receipt is authentic, pre-seat, and reproducible.
- The one thing this seat could **not** discharge as literally assigned ("the row count it records") does not exist in the artifact; the row count was therefore established by independent measurement (173 at base, 177 live) and the mismatch between the two is reported as D1 rather than papered over.
- The L1 owns every fix. D1 in particular needs a committed `census`-mode receipt if the round is to claim "173 → 177 rows" as evidence rather than as an assertion.
