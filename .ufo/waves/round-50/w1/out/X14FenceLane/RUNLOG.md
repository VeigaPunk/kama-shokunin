# X14FenceLane run log

All commands ran from `/fast/scratch/hyaku/kama-r50/X14FenceLane` (`$S`), with
`TMPDIR=$S`. Nothing was written outside `$S` and the out directory.

## 1. clone and graph

```
$ git clone -q --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane          # exit 0
$ git -C $S/lane rev-parse HEAD                                                       # 3b79eaddf38246c637cc7ba1a94ab363422876b6
$ git -C $S/lane rev-list --count HEAD                                                # 330
$ git -C $S/lane rev-list --count 97c864bead3ee4a2f629574e77263d33834ec98a            # 327 (measured graph)
$ git -C $S/lane rev-list --merges --count 97c864bead3ee4a2f629574e77263d33834ec98a   # 2
$ git -C $S/lane fetch -q /home/vgpnk/Projects/shokunin/kama-shokunin \
      'refs/jj/keep/*:refs/jj/keep/*'                                                 # exit 0 (read-only on the lane)
$ git -C $S/lane rev-list --all --count                                               # 1052
$ git -C $S/lane rev-list --min-parents=3 --count                                     # 0 (no octopus merges)
```

## 2. blob scans

```
$ python3 scan.py $S/lane 97c864bead3ee4a2f629574e77263d33834ec98a        # exit 0
  commits 327, distinct_blobs 407, blob_hits 0, fence_heading_lines 0, cr_blobs 0
$ python3 scan.py $S/lane 97c864bead3ee4a2f629574e77263d33834ec98a all    # exit 0
  commits 1052, distinct_blobs 430, blob_hits 0, fence_heading_lines 0, cr_blobs 0
$ python3 scan2.py $S/lane --all                                          # exit 0
  revs 1052, blobs 434 (per-file instances), blocks 618, lines_inside 3428,
  heading_inside 0, section_diffs 0, cr_bytes 0
$ python3 scan3.py $S/lane                                                # exit 0
  paths 94 (all contract-matching paths ever), blobs 567, blocks 672,
  lines_inside 3690, with_fences 164, heading_inside 0, section_diffs 0, cr_bytes 0,
  unmatched_patterns []
$ python3 scan6.py $S/lane 97c864bead3ee4a2f629574e77263d33834ec98a        # exit 0
  merges 2, swap events identical, teeth test 0 -> 1 heading_inside, 0 -> 59 section diffs
```

## 3. tool and frozen counter at the measured commit

```
$ python3 kama-shokunin/tools/append-only-audit.py --repo $S/lane \
      --to 97c864bead3ee4a2f629574e77263d33834ec98a --json                 # exit 0, 4.7 s
  definition v5; summary commits 327 files 94 events 5 restored 5 unrestored 0
  ungraded_lines 89 regressed 0 vanished 0 bad_declarations 0
  events: dd9f5dc6c0e6 SCORECARD.md 31/14/17 restored
          0718b6abbda6 LOG.md 2292/2292/0 restored; SCORECARD.md 2421/2349/72 restored
          0718b6abbda6 corpus/QUALITY.md 375/375/0 restored; corpus/README.md 663/663/0 restored
$ python3 kama-shokunin/tools/round50-append-audit-v5-check.py --repo $S/lane \
      --tip 97c864bead3ee4a2f629574e77263d33834ec98a --scratch $S          # exit 0, 5.3 s
  tip=97c864bead3ee4a2f629574e77263d33834ec98a
  fixture=1 lane=1 scenarios=12/12 met=True
  detail: lane: event dd9f5dc6c0e6 SCORECARD.md ungraded 17 <= v5 natively exempt 23
  detail: lane: event 0718b6abbda6 SCORECARD.md ungraded 72 <= v5 natively exempt 72
```

## 4. merge-parent swap experiment

```
$ bash out/X14FenceLane/swap-check.sh $S/lane 97c864bead3ee4a2f629574e77263d33834ec98a $S   # exit 0
  swapped: 2f7303c2 p1=03b5f0e8 p2=893e3c5d tree=00ef375c replacement=<new>
  swapped: 5396a876 p1=69780977 p2=1e489406 tree=0665eb7f replacement=<new>
  rev-list --parents -1 under refs/r50swap: 2f7303c2 893e3c5d 03b5f0e8 / 5396a876 1e489406 69780977
  frozen threshold: sha256 62e3b5c64d46055b5f0a278fd86f2bfad394433781a86385f67c1ea2aee91922 (both) → BYTE-IDENTICAL
  --threshold 1 (instrumentation only): events 102 -> 105; ungraded_lines 201 -> 204
    + 2f7303c24231 SCORECARD.md deleted 2 ungraded
    + 2f7303c24231 corpus/README.md deleted 1 restored
    + 2f7303c24231 corpus/knowledge/consumer-registry.md deleted 1 ungraded
  replace-refs-left: 0
```

Post-experiment clone state: `rev-list --all --count` 1052, `for-each-ref refs/r50swap/` 0,
`rev-list --parents -1 2f7303c24231` back to `03b5f0e8 893e3c5d`.

## 5. leftover services

`pgrep -af llama-server` lists only processes under
`/fast/scratch/hyaku/kama-r50/Sen3Teardown/` (another seat's scratch); this seat started
no server and left none.
