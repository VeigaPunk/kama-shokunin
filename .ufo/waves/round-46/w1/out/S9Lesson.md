Verdict: **the round-46 lesson skeleton is drafted with four mistake rows (two mined from the round-45 closure), each fix run and shown to fail, and a 33-item routed-sweep with its false-negative rate stated** — 1 lane defect found (S485 still carries no model re-fetch locator at the base), 1 counter blind spot (seat-yield cannot evaluate a stalled wave), 1 forward defect in this round's own receipts (scratch log pointers), 1 undisclosed status (two SCORECARD events stay `partial` by supersession), and 1 process finding (the "facts, not sufficiency" family lost its carrier).

Seat: S9Lesson (leaf, wave `kama-r46-w1`). No lane file was edited; nothing was committed, fetched into a shared clone or written outside my out directory.

## 1. Deliverables

| Path (absolute) | What |
|---|---|
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Lesson/round-46.md` | the round lesson skeleton (`## Claims` / `## Gate` / `## Mistakes` + sweep / `## Wave`), shaped on `corpus/lessons/round-45.md` |
| `…/out/S9Lesson.md` | this report |
| `…/out/S9Lesson/sweep-closures-vs-lessons.py`, `sweep.out` | the closure→lesson sweep: extraction rule, 33 items, 15 bare |
| `…/out/S9Lesson/probe-receipt-durability.py`, `durability-r45.out`, `durability-r46.out`, `durability-fixture.out` | fixes for the round-45 N-E/D3 defect and for row 3, run in both directions |
| `…/out/S9Lesson/probe-wave-yield-fallback.py`, `wave-yield-r44.out`, `-r45.out`, `-r46.out` | fix for the round-45 N-D stall-blind defect |
| `…/out/S9Lesson/seat-yield-r44.out`, `seat-yield-r45.out` | the existing counter's positive control and its blind spot |
| `…/out/S9Lesson/probe-append-partial.py`, `append-partial-base.out`, `append-partial-injected.out` | fix for mistake row 4: classifies a `partial` append-only event's missing lines as superseded / prose-dropped / lost, shown both ways |
| `…/out/S9Lesson/c2-at-base.out` | C2's lane leg re-run at the base, independently |
| `…/out/S9Lesson/fixture-live/` (104 K) | the in-tree fixture that makes `durability-fixture.out` reproducible without scratch |

## 2. Evidence

All commands ran from `/home/vgpnk/Projects/shokunin/kama-shokunin` or from the out directory; every one is read-only on the lane.

```
$ python3 tools/append-only-audit.py --repo . --to 0163fea2dab3f282ebd70c71da9ab5de4cedf733
event dd9f5dc6c0e6 SCORECARD.md deleted=31 restored_at_tip=24 status=partial restored_by=-
event 0718b6abbda6 SCORECARD.md deleted=2417 restored_at_tip=2416 status=partial restored_by=-
event 0718b6abbda6 LOG.md deleted=2290 restored_at_tip=2290 status=restored restored_by=82b5e9d33a19
event 0718b6abbda6 corpus/QUALITY.md deleted=375 restored_at_tip=375 status=restored restored_by=82b5e9d33a19
event 0718b6abbda6 corpus/README.md deleted=663 restored_at_tip=663 status=restored restored_by=82b5e9d33a19
summary commits=292 events=5 restored=3 partial=2 unrestored=0
exit=1
```

This reproduces the assignment's C2 base figure (5 events) from my own run, at `0163fea2`, not from a receipt.

```
$ git show 0163fea2:corpus/SOURCES.md | sed -n 238p | grep -c 'models-moved\|huggingface'
0
$ git grep -n 'models-moved' 0163fea2 -- tools/        # no output
$ ls registry/release-recheck-b11906.tsv
ls: cannot access 'registry/release-recheck-b11906.tsv': No such file or directory
$ git status --porcelain | head -4
?? .ufo/waves/round-46/c1/
?? .ufo/waves/round-46/w1.ready
?? .ufo/waves/round-46/w1.ready.partial
?? .ufo/waves/round-46/w1/out/
$ git rev-parse HEAD
96d329186e777080c03ac89fdd2366714d504dc3
```

So: the b11906 ledger does not exist yet, the round's live receipts are untracked at HEAD `96d32918`, and the S485 row carries no re-fetch locator at the base (row 1; Gate reject 5).

Facts I verified from the round's own evidence files (not from the report or the assignment):

- `.ufo/waves/round-46/c1/release-b11906.json`: `tag_name` b11906, `target_commitish` `4d71b42fd87db24b8b7c808c151b713aa4459cfd`, `published_at` 2026-10-26T19:45:36Z, `prerelease` true, asset `llama-b11906-bin-ubuntu-x64.tar.gz` 22478121 bytes, `digest sha256:064ade62…1eeef3`.
- `.ufo/waves/round-46/c1/live/install.txt`: downloaded tarball sha256 equals that digest; extracted `/home/vgpnk/.local/opt/llama-b11906/llama-server` sha256 `c949950e…f3ff`; `--version` "build 11906, commit 4d71b42fd".
- `receipt-{1,2,3}.json`: schema `kama-llamacpp-live/v3`, `outcome` pass, ports 33179 / 46073 / 44923, model sha256 `270cba1b…256d`, tool sha256 `8c0dbb2b…62f3` (equal to `sha256sum tools/kama-llamacpp-live.py`), `/health` 200 `{"status":"ok"}`, `/metrics` 501, `teardown.term_wait_ms` 3 / 3 / 3 (b11889 receipts: 15 / 9 / 7).
- `.ufo/waves/round-46/c1/live/model-fetch.txt`: url `https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf`, 1185376 bytes, sha256 `270cba1b…256d` — the record r45-D3 asked for, as a seat-side file.
- `.ufo/waves/round-46/freeze/prereg-time-check.out`: `rev=5790944350ae…`, `RESULT pass`, `exit=0`.

Append-only partials at the base (mistake row 4; counts match the seat S9Quality's independent read, and I re-derived every missing line):

```
$ python3 …/probe-append-partial.py --repo . --to 0163fea2…
partial dd9f5dc6c0e6 SCORECARD.md missing=7 superseded=6 prose-dropped=1 lost=0
  superseded: row:**operability** row:**freshness** row:depth row:coverage row:calibration row:adjacency
  prose-dropped: Reconciled in round 41 against the measured commit (`tools/round41-scorecard-reconcile.py`, claim C1): every h…
partial 0718b6abbda6 SCORECARD.md missing=1 superseded=1 prose-dropped=0 lost=0
  superseded: row:depth
summary partials=2 missing=8 superseded=7 prose-dropped=1 lost=0      exit=0
$ … --inject '| zzz | **7** | a head row whose key is gone |'
summary partials=2 missing=10 superseded=7 prose-dropped=1 lost=2      exit=1
```

The eight missing lines are the old depth head row (`91440eb8…`, 1420 lines) and the six pre-round-42 head-axis rows plus the "Reconciled in round 41 …" prose line, all replaced by the round-42 head — supersession, which round-45's lesson row 5 does not say.

Probe runs (full transcripts in the receipts named above):

```
$ python3 probe-receipt-durability.py --dir .ufo/waves/round-45/c1/live
receipt receipt-1.json model=fail:no-side-record-of-sha server=pass log=fail:dead-pointer   (×3)
summary receipts=3 fail=3      exit=1

$ python3 probe-receipt-durability.py --dir .ufo/waves/round-46/c1/live
receipt receipt-1.json model=pass server=pass log=fail:dead-pointer                          (×3)
summary receipts=3 fail=3      exit=1

$ python3 probe-receipt-durability.py --dir .ufo/waves/round-46/w1/out/S9Lesson/fixture-live
receipt receipt-1.json model=pass server=pass log=pass:copied-beside-receipt                 (×3)
summary receipts=3 fail=0      exit=0

$ python3 tools/seat-yield.py .ufo/waves/round-44/w1 --expect-reports 65
wave=w1 seats=65 status=unknown:65 reports=65 missing=0      exit=0
$ python3 tools/seat-yield.py .ufo/waves/round-45/w1 --expect-reports 64
could-not-evaluate: no *-results.json or results.json in .ufo/waves/round-45/w1      exit=2

$ python3 probe-wave-yield-fallback.py --wave .ufo/waves/round-44/w1
wave=kama-r44-w1 seats=65 reports=65 missing=0 driver-log=9      exit=0
$ python3 probe-wave-yield-fallback.py --wave .ufo/waves/round-45/w1
wave=kama-r45-w1 seats=64 reports=0 missing=64 driver-log=18      exit=1
$ python3 probe-wave-yield-fallback.py --wave .ufo/waves/round-46/w1   # 2026-10-26T20:03:04Z
wave=kama-r46-w1 seats=65 reports=32 missing=33 driver-log=5      exit=1
```

Sweep (the item's required grep; command and output are also pasted verbatim in the lesson's `## Mistakes`):

```
$ python3 .ufo/waves/round-46/w1/out/S9Lesson/sweep-closures-vs-lessons.py > …/sweep.out
summary items=33 uncited_by_label=24 uncited_by_both=15
```

Hand-read of the 15 bare rows: 3 are closed and cited in a later lesson without the label (r40 D3 → `corpus/lessons/round-41.md:117`; r42 #4 → `corpus/lessons/round-43-verifier-spotcheck.md:38`; r43 D4 → `corpus/lessons/round-44.md:54`), 4 are operator/driver items still open by statement, 3 are r45 items already dispositioned in the round-46 preregistration `routed` block, 1 is closed in `SCORECARD.md` (r42 #3 → spot-check count 31), and the remaining family (r41 #1, r42 #2, r43 #6, r44 #5, r45 #4 — "counters prove facts, not sufficiency") is not a lesson row anywhere and is absent from the round-46 preregistration (`grep -c sufficiency` → `0`).

## 3. Defects (exact location, command, proposed fix)

1. **`corpus/SOURCES.md:238` (S485 `recheck` cell): r45-D3 is not closed at the registry level.** The row cites the receipts and states the statements that hold, but names no locator for the model, and no tool under `tools/` mentions the re-fetch URL at the base. Command: `git show 0163fea2:corpus/SOURCES.md | sed -n 238p | grep -c 'models-moved\|huggingface'` → `0`; `git grep -n 'models-moved' 0163fea2 -- tools/` → empty. Shown able to fail: `probe-receipt-durability.py` on `.ufo/waves/round-45/c1/live` → `model=fail:no-side-record-of-sha`, `exit=1`. Proposed fix (lane's call, text to append to the S485 `recheck` cell, not applied): `model re-fetch: https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf, 1185376 bytes, sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d, re-fetched 2026-10-26T19:57:36Z (.ufo/waves/round-46/c1/live/model-fetch.txt)`. The round-46 variant should also carry it, so this is a proposal for both rows.
2. **`tools/seat-yield.py` `locate()`: `exit 2` on a wave that never wrote a results JSON** — the case the tool exists for. Command: `python3 tools/seat-yield.py .ufo/waves/round-45/w1 --expect-reports 64` → `could-not-evaluate: no *-results.json`, `exit=2` (round-44 control passes: `reports=65`, `exit=0`). Proposed fix, already written and run: `probe-wave-yield-fallback.py` (denominator `dispatch.json` `taskCall.tasks[].name`, numerator `out/<seat>.md` and `out/<seat>/<seat>.md`) — `r45 0/64 exit=1`, `r44 65/65 exit=0`. Landing it in `tools/` is a lane decision (I am read-only on `tools/`).
3. **`.ufo/waves/round-46/c1/live/receipt-{1,2,3}.json` `teardown.log_path`** → `/fast/scratch/hyaku/kama-r46/X1Live/kama-llamacpp-live-*.log`, a path the operator scratch directive deletes. Command: `probe-receipt-durability.py --dir .ufo/waves/round-46/c1/live` → `log=fail:dead-pointer` 3/3. The receipts inline a 3-line tail, so this is a pointer defect, not an evidence hole. Proposed fix: `tools/kama-llamacpp-live.py` writes the run log beside `--receipt-dir` (or records `log_path` only when it is in-tree); the probe's log leg then passes — shown by `fixture-live/` → `log=pass:copied-beside-receipt`, `exit=0`.
4. **Process, not code: the sufficiency family lost its carrier** (see §2). Proposed rule, written into the lesson: a carried item that survives three closures without a lesson row must be either written as a row with a fail-capable check or dropped with a stated reason.
5. **`SCORECARD.md` and `corpus/lessons/round-45.md` row 5: two append-only events stay `partial` and nobody wrote why.** `python3 tools/append-only-audit.py --repo . --to 0163fea2` → `status=partial` for `0718b6ab SCORECARD.md` (2417 deleted, 2416 back) and `dd9f5dc6 SCORECARD.md` (31 deleted, 24 back); the lesson calls them restored. Command: `python3 …/probe-append-partial.py --repo . --to 0163fea2…` → `missing=8 superseded=7 prose-dropped=1 lost=0`, `exit=0`. Proposed fix: keep the audit as the fact and write the class next to it — the round-46 lesson's row 4 does this, and the proposed wording for round 45's row 5 is "two of the five events stay partial by supersession: 2416/2417 and 24/31". The probe's loss branch is shown to fire (`--inject` → `lost=2`, `exit=1`); note this defect does **not** by itself make C2 fail, because the frozen counter's `lane` leg requires the tool's exit code to *agree* with the recomputed events, not that no partial exists.
6. **Limitation of my own sweep, disclosed:** label-citation is not coverage; it over-reports by 3/15 (20 %). The lesson states this next to the output rather than presenting the bare list as defects.

## 4. Out of scope / not done

- I did not run C1's counter, did not read any of the 20 b11906 rows, and did not touch `registry/release-recheck-b11906.tsv` (absent). The lesson's C1 section is placeholders only.
- I did not evaluate C2 against the frozen counter (`tools/round46-append-audit-check.py`); I only re-ran the lane tool at the base.
- No services started or stopped; `gh` not used; no pacman, no installs, no tool upgrades (so nothing to record under the tooling directive).
- I did not message `agent://all`, did not spawn subagents, did not touch the lane's jj/Git state, and wrote nothing outside `…/w1/out/S9Lesson/` plus this report.
- Scratch `/fast/scratch/hyaku/kama-r46/S9Lesson` held one fixture copy under `durability-pass/` during drafting; it is deleted, and the durable copy of that fixture is in-tree at `out/S9Lesson/fixture-live/`.
