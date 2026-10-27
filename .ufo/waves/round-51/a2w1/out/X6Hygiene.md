Verdict: end-of-wave hygiene is clean — no llama-server process or listener remains anywhere on the host, scratch dropped 12G→8.2G and 44→19 seat dirs, the only fleet-root untracked file is another lane's own report, and the only live lane-tree item is the L1's post-integration-commit 4-line `server_exe` OSError hardening in `tools/kama-llamacpp-live.py`, which no `-int` receipt measures.

Final sample 2026-10-27T01:04:27-03:00 (52/66 reports landed; remaining were the long mutation/review seats). Full evidence + verbatim transcript: `.ufo/waves/round-51/a2w1/out/X6Hygiene/hygiene.md` and `late-sample.txt`.

## The four assigned checks

**1. `pgrep -af llama-server` → exit 1 (none).** No listener owned by
llama-server; all build/control ports (42881, 38973, 36071, 40177, 35825,
39165) refuse. In-flight-but-legitimate at sample time (named by owner, not
leftovers): seat **M2Live** mid-C1-counter (`round51-replay-exe-audit.py` pid
2868238 on `ctr-L04-fstat-from-path`, tip 261817b8…); one non-kama process
(tameshi lane `measure.py`). At ~00:50 X1Fresh held a replay on
127.0.0.1:38799 — gone by the final sample, so no teardown leak.

**2. `du` top 10 (MiB):** L1 2636, M2Live 756, X7Regen 378, V3Review 378,
Sen3Ledger 378, X8Restore 377, X3R41 377, T6Skill 377, T4Quality 377, Sen1Exe
377 — total 8.2G across 19 seat dirs (from 12G/44 dirs; finished seats did
clean). Lane clones (`*/lane`) remain in 13 dirs: reports already landed for
**J8OneClass, N1Overlap, T4Quality, T6Skill, X7Regen** (cleanup may still be in
flight); the other 8 are still-running seats.

**3. Fleet `git status --porcelain`:** only `?? .ufo/reports/round-45/kengaku.md`
— kengaku lane's own report (mtime Oct 26 23:47), not a kama seat. The 00:50
untracked `.ufo/reports/round-48/mado.md` is now committed (`a72080e7`) — a
mado-lane write resolved by its own L1. No tracked fleet file modified.

**4. Lane `git status --porcelain`:** ` M tools/kama-llamacpp-live.py` +
untracked `a2w1/out/` and 23 `measured/*-int.out` receipts — all the L1's
integration in flight at tip `c5ec93d5`. `-int` receipts observed: c1
`met=True` 3/3+3/3, c2 `met=True` 9/9 disclosed=165, `gate-int` now
`registered 48 unregistered 0` (the wave's known "unregistered 2" item closed).

## Integration item (named, not a defect)

`tools/kama-llamacpp-live.py` (+4 lines, `except OSError` → `opened:False,
reason:exe-read-failed:…`, crediting V2Review) is uncommitted and post-dates
`c5ec93d5` (sha256 `863aea6d…` vs `00de205b…`). If committed, the C1 counter's
`-int` receipt needs a rerun to cover the tool bytes as integrated; the change
touches only an error path the counter never exercises, so this is a receipt
freshness note, not a met risk.

## Supplementary cleanliness checks (all clean)

`~/.local/bin`/`~/.local/opt` untouched in the last 3h; no ignored-path writes
inside lane `tools/`/`corpus/`/`registry/`; every `out/` root `.md` matches a
spec.json seat name (66 name-checked); no `.git/index.lock` or stray locks;
earlier mid-wave working-tree changes (SCORECARD banner 36→37, QUALITY
KQ85–88, SKILL registry, append-only-audit ledger-cutoff + selftest) were
committed and re-measured in `c5ec93d5` before the final sample — resolved.

Paths: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/X6Hygiene.md`
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/X6Hygiene/hygiene.md`
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/X6Hygiene/late-sample.txt`
