Verdict: Freeze ordering, counter bytes, and controls are consistent; the preregistration timestamp is six seconds late, explicitly caught and corrected by the erratum.

Evidence (axes: calibration/freeze integrity; operability/freeze integrity):

- Command: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --format='%H %cI %s' 57a2e25bf702b03aa61f9265e968cf68058ecb82..138af25b963450b6520794995605fa7dbbcd87e0`. Output, oldest to newest: `804bde75164444bdf0fe6783d7aa45774bf562bd 2026-10-27T00:38:24-03:00` (freeze); `b6bed925b032ac2c19b63ef4af358ebdd5922c26 2026-10-27T00:39:06-03:00` (build); `73bf2a7a17104a62a3e442912c8776cbd8dedbd5 2026-10-27T00:39:57-03:00` (build-fix); `138af25b963450b6520794995605fa7dbbcd87e0 2026-10-27T00:42:07-03:00` (build-fix 2). Ordering is consistent.
- `sha256sum tools/round51-replay-exe-audit.py tools/round51-append-audit-v6-check.py` returned respectively `e5753c453c30bd311e4c12fc962d324c7db482233b64b22795658b47b6ee5155` and `254e63bab046428d4099d008929751701ed7b0600b96874760838a56eb9a1660`; both equal the preregistration `counter_sha256` values. Preregistration lines 18 and 29 contain those values.
- `git -C ... diff 804bde75164444bdf0fe6783d7aa45774bf562bd 138af25b963450b6520794995605fa7dbbcd87e0 -- tools/round51-*` produced no output (empty). `git show --stat --oneline 804bde75164444bdf0fe6783d7aa45774bf562bd` lists both round51 counters and `controls/base.c1.out`, `controls/base.c2.out`; therefore controls and counter bytes were committed at the freeze.
- `freeze/prereg-time-check.out` records `committer_time=2026-10-27T00:38:24-03:00`, flags preregistration line 6 (`2026-10-27T03:38:30Z`, six seconds later), `RESULT fail`, `exit=1`. `freeze/frozen-at-erratum.md` lines 3-9 explicitly records the correction: time of record is commit time `2026-10-27T03:38:24Z`; preregistration remains unchanged. This is a disclosed inconsistency, not an unreported one.

No other inconsistency found in the assigned freeze-ordering checks.
