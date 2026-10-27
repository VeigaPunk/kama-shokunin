# X6Hygiene — end-of-wave hygiene detail (kama round 51, wave a2w1)

Final sample: **2026-10-27T01:04:27-03:00** (52/66 seat reports landed at `out/` at
that moment; the 14 missing were the L1-named long mutation/review seats). Earlier
in-flight sample at ~00:50:38, mid-wave.

## 1. `pgrep -af llama-server` — clean at both samples

```
### 1. pgrep -af llama-server          (01:04:27)   exit=1  (no process)
### 1b. ss -ltnp | grep llama-server                 exit=1  (no listener)
### 1d. build/control receipt ports 42881,38973,36071,40177,35825,39165 listening?
                                                     exit=1  (none)
```

Early sample (~00:50): seat **X1Fresh** legitimately held a replay
(`llama-server` pid 979061 on 127.0.0.1:38799, parent chain
`kama-live-replay.py` 976714 → `kama-llamacpp-live.py` 978513 → server); it was
in-flight work and is gone — no leftover. At the final sample no llama-server
anywhere on the host; no loopback listener it owns; every port printed in the
base controls and the C1 build receipt refuses.

In-flight-but-legitimate at 01:04–01:05 (named, not called leftovers):

- Seat **M2Live** was mid-C1-counter: `python3 tools/round51-replay-exe-audit.py
  --repo $S/M2Live/lane --tip 261817b8… --scratch $S/M2Live/ctr-L04-fstat-from-path`
  (pid 2868238; earlier pid 2609182 on `ctr-L01-readlink-suffix` at tip
  820807ee…). Its own llama-server children are part of the replay and teardown
  is the counter's own leg.
- One tameshi (other-lane) process: `python3
  .ufo/evidence/round-51/c3/measure.py --lane .../tameshi-shokunin` — not kama,
  named so it is not misattributed.

## 2. `du` of `/fast/scratch/hyaku/kama-r51` (top 10, MiB)

At the final sample the tree had dropped 12G → 8.2G and 44 → 19 seat dirs
(finished seats removed their scratch per the operator directive).

```
2636  L1          756  M2Live        378  X7Regen   378  V3Review
378   Sen3Ledger  377  X8Restore     377  X3R41     377  T6Skill
377   T4Quality   377  Sen1Exe
```

L1's 2.6G is its measuring scratch (`meas-build`, `meas-int`, `base`, `dry`,
`bld` clones) — expected while it integrates.

Scratch still holding a `git clone --shared` lane clone at the final sample —
13 dirs; owner status cross-checked against `out/`:

- report already landed, scratch remains (possible cleanup miss; the seat may
  still be finishing): **J8OneClass, N1Overlap, T4Quality, T6Skill, X7Regen**
- report not yet landed (still legitimately working): **M1Ctr, M2Live,
  M5Digest, Sen1Exe, Sen3Ledger, V3Review, X3R41, X8Restore**

My own scratch was `/fast/scratch/hyaku/kama-r51/X6Hygiene/` and is removed
after copying cited artifacts here.

## 3. `git -C /home/vgpnk/Projects/shokunin status --porcelain`

```
?? .ufo/reports/round-45/kengaku.md        exit=0
```

One untracked file; it is **not a kama seat's write**: header reads `# kengaku —
round 45 report`, authored by lane kengaku's L1 (`KengakuR45`), mtime
2026-10-26T23:47. Left in place per the directive.

Between the two samples, `.ufo/reports/round-48/mado.md` was untracked at 00:50
and is now committed at `a72080e7` ("round-48: mado report") — resolved by that
lane's own L1; no kama seat wrote it either. No fleet-root tracked file was
modified by any kama seat (verified: `git status` shows no `M` anywhere, and
`.ufo/reports/round-51/` contains only other lanes' tracked reports — no
`kama.md` yet, the lane L1's own landing step).

## 4. `git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain`

```
 M tools/kama-llamacpp-live.py
?? .ufo/waves/round-51/a2w1/out/
?? .ufo/waves/round-51/measured/*-int.out   (23 integration receipts)
```

Everything except the first entry is the L1's integration in flight:

- `*-int.out` receipts at tip `c5ec93d5` ("round-51: integration — SCORECARD,
  SKILL registry, QUALITY KQ85–88, ledger cutoff, ledger regenerated"): `c1-int`
  `bind=1 own=1 teardown=1 newrow=1 bound=3/3 owned=3/3 met=True` exit 0;
  `c2-int` `fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=165 met=True`
  exit 0; `aoa-selftest-int` `pass=51 fail=0`; `gate-int` `registered 48
  unregistered 0 defective 0` — the wave's known "gate unregistered 2" item is
  now closed by the SKILL.md registry rows.
- `a2w1/out/` untracked is normal for a wave in flight (the round-50 out dir is
  also untracked at HEAD; seat reports are not committed).
- Earlier working-tree changes I observed at ~00:57 (`M SCORECARD.md`,
  `M corpus/QUALITY.md`, `M SKILL.md`, `M tools/append-only-audit.py` — the
  round-51 banner re-anchor 36→37, KQ85–88, the registry rows, and the ledger
  cutoff rule + `t_v6_ledger_cutoff` selftest case) are now committed in
  `c5ec93d5` and re-measured by the `-int` receipts, including the C2 lane leg
  run on the new tool bytes. That finding resolved before I finished sampling.

### One live integration item (named, not a defect)

` M tools/kama-llamacpp-live.py` — 4 insertions, post-`c5ec93d5`, uncommitted at
the sample: a `server_exe()` `except OSError` hardening returning
`{'opened': False, 'reason': 'exe-read-failed:…'}` (diff credits seat
V2Review). sha256 worktree `863aea6d…` ≠ `c5ec93d5` `00de205b…`. The C1 `-int`
receipt at `c5ec93d5` therefore does not measure these bytes; if the L1 commits
this, a fresh C1 counter run is needed for the receipt to cover the tool as
integrated. (Change is defensive — an OSError path the frozen counter never
triggers — so risk is receipt freshness, not a met flip.)

### Supplementary (all exit-clean)

- `find ~/.local/bin ~/.local/opt -newermt '-3h'` → empty: the host's b11909
  install and PATH dirs untouched by the wave.
- `git status --porcelain --ignored` lane sweep: only expected ignored paths
  (`registry/history/.lock` and its siblings per the lane's own
  `registry/history/.gitignore`, `tools/__pycache__/`, `.jj/`, prior-wave
  `__pycache__` dirs) — no seat smuggled an ignored write into `tools/`,
  `corpus/` or `registry/`.
- `out/` contains only seat-named `.md`/dirs plus the orchestrator's
  `swarm-registry.json`; every root `.md` name matches a spec.json seat id
  (66/66 name-checked); no stray paths.
- No `.git/index.lock` in the lane; no `*.lock` outside the ignored history
  locks.

## Raw transcript

`late-sample.txt` in this directory is the verbatim capture of the final
sample (all commands + exits, 2026-10-27T01:04:27).
