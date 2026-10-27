# M2Live — round-51 live/replay mutation test (lane kama, seat M2Live)

**Verdict: 26 mutants of `server_exe()` and the replay's server-exe block — 6 killed-by-selftest, 10 killed-by-counter, 8 survived with demonstrated killing probes (coverage findings, proposals in `out/M2Live/proposals/`), 2 equivalent (L08 perf-only, L12 coerced at every current comparator). All verdicts are actual detector runs on pristine, mutated, and restored bytes; the frozen detectors' contract held — no counter defect found.**

## Scope and method

Targets (frozen bytes, lane commit 138af25b963450b6520794995605fa7dbbcd87e0):
`tools/kama-llamacpp-live.py` `server_exe()` (lines 738–761: readlink, open flags, fstat, S_ISREG,
hash loop, left check, dev/inode format) and `tools/kama-live-replay.py` server-exe block
(lines 358–368: opened check, sha compare, dev/inode compare, own_server record).

Detectors (the frozen ones only; mutants were made in scratch copies, never in the lane):
- `python3 kama-live-replay.py --selftest --scratch <root>` — offline, 26 cases.
- `python3 kama-llamacpp-live.py --selftest` — offline.
- `python3 tools/round51-replay-exe-audit.py --repo <clone> --tip <sha> --scratch <dir>` — frozen C1 counter (22 runs total, ~17 s each: 1 pristine baseline, 20 mutants, 1 restored confirmation).

Baselines (all exit 0 before any mutant ran):
- replay selftest: `KLR_SELFTEST pass=26 fail=0` (evidence/base-replay-selftest.txt).
- live selftest: `selftest: ok; closed tcp6 listeners …` (evidence/base-live-selftest.txt).
- C1 counter at 138af25b in my `git clone --shared` fixture: `bind=1 own=1 teardown=1 newrow=1 bound=3/3 owned=3/3 met=True`, exit 0 (evidence/ctr-base.out); observed image dev `103:05`, inodes distinct per replay.

Restored bytes after the sweep (mutation cycle closed):
- counter re-run at pristine 138af25b, clean worktree: `met=True`, exit 0 (evidence/ctr-restored.out).
- replay selftest re-run: `pass=26 fail=0` (evidence/restored-replay-selftest.txt).

Method notes: the live tool resolves `LANE = SCRIPT.parent.parent` and reads
`registry/endpoint-consumers.tsv` (kama-llamacpp-live.py:91-93), so every scratch tree mirrors the
repo layout `tools/` + `registry/`; a flat copy fails its selftest with
`SetupError: registry-unreadable` (environmental, not a bytes defect). Mutant commits were made
only inside my scratch clone (identity `fx <fx@invalid>`, `rev-parse --show-toplevel` asserted
before every commit). No lane file was edited; the lane was only read.

## Mutant table

Legend: live-st = `kama-llamacpp-live.py --selftest`; rpl-st = replay `--selftest`; C1 = frozen
counter (exit code and `bind/own/met` from its summary line). Full outputs under
`out/M2Live/evidence/`; per-mutant file hashes in `evidence/mutants.json`.

| id | target (file:function:line) | mutation | live-st | rpl-st | C1 | verdict |
|---|---|---|---|---|---|---|
| L01 | live:740 | `path = os.readlink(link) + '~'` | pass | n/a | 0, met=True | **survived-frozen**; killed by proposed probe `path_is_readlink` (demonstrated) |
| L02 | live:741 | `os.open(..., os.O_RDONLY \| os.O_NOFOLLOW)` | pass | n/a | 1, bind=0 own=0 met=False | **killed-by-counter** (`exe-unreadable:Too many levels of symbolic links`) |
| L03 | live:741 | `fd = os.open(path, …)` — open the readlink text, not the magic link | pass | n/a | 0, met=True | **survived-frozen** (reinstates the J4Decoy weakness); killed by proposed probe `open_targets_proc_link` |
| L04 | live:745 | `st = os.stat(path)` instead of `os.fstat(fd)` | pass | n/a | 0, met=True | **survived-frozen**; killed by proposed probe `never_stats_the_path` |
| L05 | live:746-747 | S_ISREG check deleted | pass | n/a | 0, met=True | **survived-frozen** (check unreachable for a live exe); killed by proposed probe `fifo_mode_refused` |
| L06 | live:746 | S_ISREG inverted | pass | n/a | 1, bind=0 own=0 met=False | **killed-by-counter** (every run `exe-not-a-regular-file`) |
| L07 | live:748 | `left = st.st_size // 2` | pass | n/a | 1, met=False | **killed-by-counter** (sha of first half ≠ frozen `35ac50fb…`) |
| L08 | live:750 | chunk `1 << 20` → `4096` | pass | n/a | 0, met=True | **equivalent** (performance only; identical output; all probes pass) |
| L09 | live:752 | `h.update(chunk)` deleted | pass | n/a | 1, met=False | **killed-by-counter** (empty-input sha `e3b0c442…`) |
| L10 | live:755 | `if left != 0:` → `if left < 0:` | pass | n/a | 0, met=True | **survived-frozen** (no detector produces a short read); killed by proposed probe `short_read_reported` |
| L11 | live:760 | dev `'%02x:%02x'` → `'%x:%x'` | pass | n/a | 1, met=False | **killed-by-counter** (`'103:5'` vs own `‘103:05’`) |
| L12 | live:761 | `'inode': st.st_ino` (int, not str) | pass | n/a | 0, met=True | **equivalent at current comparators** (replay 366 and counter both `str()` it); killed only by the proposed type-strict `path_is_readlink` |
| L13 | live:760 | major/minor swapped | pass | n/a | 1, met=False | **killed-by-counter** (`'05:103'` vs `'103:05'`) |
| L14 | live:741 | `os.open(os.devnull, …)` | pass | n/a | 1, met=False | **killed-by-counter** (char device → `exe-not-a-regular-file`; shows L05's check is load-bearing) |
| L15 | live:738 | `f'/proc/{pid + 1}/exe'` | pass | n/a | 1, met=False | **killed-by-counter** (`exe-unreadable:No such file or directory`) |
| R01 | replay:362 | `is not True` → `is not False` | n/a | **fail** (match, v5-match, witness-passthrough) | not run | **killed-by-selftest** |
| R02 | replay:362 | opened value no longer checked | n/a | 26/26 | 0, met=True | **survived-frozen**; killed by proposed case `server-exe-opened-false` (demonstrated) |
| R03 | replay:364 | `!=` → `==` | n/a | **fail** (match, v5-match, and digest-differs now exit 0) | not run | **killed-by-selftest** |
| R04 | replay:364 | `want_srv` → `need["model.sha256"]` | n/a | **fail** (match, v5-match, witness-passthrough) | not run | **killed-by-selftest** |
| R05 | replay:366 | compare dev only | n/a | **fail** (server-exe-not-own-member exit 0) | not run | **killed-by-selftest** (the decoy copy shares the device, so dev-only still passes happy paths — but the frozen case catches it) |
| R06 | replay:366 | compare inode only | n/a | 26/26 | 0, met=True | **survived-frozen** (no case has right-inode/wrong-dev); killed by proposed case `server-exe-foreign-dev` (demonstrated) |
| R07 | replay:366 | dev/inode compare deleted | n/a | **fail** (server-exe-not-own-member exit 0) | not run | **killed-by-selftest** |
| R08 | replay:360 | own_id `'%02x:%02x'` → `'%x:%x'` | n/a | **fail** (match/v5-match: `103:05 != 103:5`) | not run | **killed-by-selftest** |
| R09 | replay:361 | own_server.dev as decimal `str(st.st_dev)` | n/a | 26/26 (own_server unasserted) | 1, bind=1 **own=0** met=False | **killed-by-counter** (`own_server {'dev': '66309', …} does not name the observed member file`) |
| R10 | replay:361 | own_server.path key dropped | n/a | 26/26 | 1, bind=1 **own=0** met=False | **killed-by-counter** (`own_server {'dev': …, 'inode': …} does not name the observed member file`) |
| R11 | replay:362 | `is not True` → `is False` (missing key passes) | n/a | 26/26 | 0, met=True | **survived-frozen**; killed by proposed case `server-exe-opened-absent` (demonstrated) |

Counts: 6 killed-by-selftest + 10 killed-by-counter + 8 survived-with-demonstrated-probe (L01, L03,
L04, L05, L10, R02, R06, R11) + 2 equivalent (L08, L12) = 26.

## Coverage findings (survivors; proposals, not lane edits)

1. **`server_exe()` is never executed by the live tool's frozen selftest** — all 15 of its mutants
   pass `--selftest`. Proposed `_server_exe_selftest()` with five probes
   (`proposals/live-server-exe-selftest.diff`, runnable copy `probes/probe_live.py`): pristine
   passes all five; each targeted survivor fails its dedicated probe (evidence/probe-live.out).
2. **Replay server-exe cases are under-selected**: the `opened` value is only exercised as `True`
   (R02/R11 survive), the `own_server` record is never asserted (R09/R10 pass selftest; the counter
   catches them), and the not-own-member decoy is a same-device copy so the dev dimension is
   untested (R06 survives). Proposed three cases (`proposals/replay-selftest-cases.diff`,
   demonstrated in evidence/probe-replay.out): `server-exe-opened-false`, `server-exe-opened-absent`,
   `server-exe-foreign-dev`.
3. **Descriptor-vs-path observation is invisible to every frozen detector** (L03, L04): while the
   readlink text still names the running image, opening/stat-ing the path is indistinguishable from
   the proc_pid_exe(5) contract the counter's own leg implements (`own_exe()`,
   round51-replay-exe-audit.py:345-367). The unit probes pin the contract cheaply; a counter-grade
   fix (swap the path mid-hold) would need a new leg and is the lane's call, not this seat's.

No defect was found in the frozen counters, selftests, preregistration, or controls. Known
integration items (SKILL registry, r41-r43 spot counts, census E11, round-50 C2 lane=0, hexrun
unknown=2) were not re-examined.

## Compliance

- Scratch `/fast/scratch/hyaku/kama-r51/M2Live/` removed after this report was written; `/tmp` never used.
- Lane touched read-only only; my fixture clone's worktree was restored to 138af25b (clean,
  `git status --porcelain` = 0 lines) before removal; fixture commits (`fx` identity) exist only in
  that clone. Fleet repo and /home/vgpnk/Projects/shokuknow untouched.
- Counters started/stopped their own llama-servers; final `pgrep -af llama-server`: no leftovers.
- No pacman, no tool installs or upgrades (none needed); no services started or stopped by me.
- Evidence: 27 files in `out/M2Live/evidence/` (baseline, restored, per-mutant counter/selftest
  outputs, probe transcripts, mutant hashes); proposals in `out/M2Live/proposals/`; probes in
  `out/M2Live/probes/`.
