# round 51 preregistration: frozen_at erratum (appended, the preregistration is not edited)

`.ufo/waves/round-51/preregistration.json` line 6 says `"frozen_at_utc": "2026-10-27T03:38:30Z"`.
The freeze commit `804bde75164444bdf0fe6783d7aa45774bf562bd` has committer time
`2026-10-27T00:38:24-03:00` (= 03:38:24Z), 6 s earlier. The L1 typed an anticipated time
instead of reading the clock when the file was written; KQ64's check caught it
(`freeze/prereg-time-check.out`: `FLAG line 6 ... later than commit by 6s`, `RESULT fail`, exit 1).
The freeze time of record is the committer time, 2026-10-27T03:38:24Z. The counters'
sha256 in the preregistration equal the committed bytes at `804bde75` (no change). Mined
as round-51 lesson Mistakes #1.
