PASS — frozen ordering, counters, controls, and timestamp check are consistent.

- Ordering: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --format='%H %cI %s' 9ff76b1f763512be2f554cbbfd0b2213b63b0847..5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8` returned freeze `8551ba7f2056f2465d20f5b50586978133212fe1` at `2026-10-27T01:42:07-03:00`, then build `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8` at `2026-10-27T01:56:49-03:00`.
- Counter hashes at build: `sha256sum .../tools/round52-replay-memfd-audit.py .../tools/round52-append-restore-check.py` yielded `053ff50261812de3236697dd8dc847b3dff9507f8290b0d42aaf65c12e1121f5` and `29dfd886d858f24d7cbd7a62d829c35545fc39294fe7923c59eae1ecc30853ea`; both equal `preregistration.json` lines 20 and 33.
- Frozen-vs-build counter diff: `git -C ... diff 8551... 5dacf... -- tools/round52-*` had no output (exit 0).
- Control provenance: `git -C ... ls-tree 8551... .ufo/waves/round-52/controls/` shows committed blobs `base.c1.out` (`bf92c5ad...`) and `base.c2.out` (`eabd10b8...`).
- Timestamp: `python3 .../tools/prereg-time-check.py --help` exited 0. Invoked checker with repo lane, rev freeze, prereg path, scratch `/fast/scratch/hyaku/kama-r52/Sc1Freeze`: exit 0, `committer_time=2026-10-27T01:42:07-03:00`, line 6 timestamp `2026-10-27T04:42:00Z` reported at/before commit; `RESULT pass`.

No inconsistency observed. Report covers ordering, frozen bytes, committed controls, and prereg timestamp; no counter executions were required.