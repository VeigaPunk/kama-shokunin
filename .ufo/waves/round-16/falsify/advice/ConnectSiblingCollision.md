# ConnectSiblingCollision — fleet-root misroot listing (read-only)

VERDICT: partial — untracked fleet-root files naming kama/round-16: one steady kama hit that is watchdog state (not a seat artifact), zero steady round-16 hits, and one **transient** round-16 seat misroot observed and then gone inside the run window.

Seat scope was read-only by assignment: `git -C /home/vgpnk/Projects/shokunin status --porcelain` plus listing; I moved nothing, deleted nothing, and wrote only this file.

## Axes named

- **A1 misroot separation** — did kama round-16 seat output land at the fleet root instead of `kama-shokunin/`?
- **A2 live-state preservation** — would a kama/round-16-keyed cleanup delete state the fleet drivers still use?
- **A3 snapshot integrity** — is an "untracked fleet-root list" stable enough to act on while siblings run?

## What I ran (commands + exit codes)

```
git -C /home/vgpnk/Projects/shokunin status --porcelain                  # exit 0
git ls-files --others --exclude-standard                                 # exit 0
git ls-files --others --exclude-standard | grep -i -e kama -e round-16   # exit 0 (hits)
git status --porcelain --ignored=matching | grep -E '^!!.*(kama|round-16)'  # exit 0 -> kama-shokunin/
git ls-files --others --ignored --exclude-standard | grep -i kama        # exit 0 -> kama-shokunin/
git check-ignore -v kama-shokunin                                        # exit 0 -> .gitignore:1:*-shokunin/
stat -c '%y %n' .ufo/state/*.report-baseline scripts/hyaku/jj-lane*.sh   # exit 0
wc -c .ufo/state/*.report-baseline                                       # exit 0 (9 x 68 bytes)
grep -rIl -i kama .ufo/waves/round-16                                     # exit 1 (no match)
git ls-files .ufo/waves/round-16                                          # exit 0 (6 tracked files)
ls .ufo/reports/round-16/kama.md                                          # exit 2 (absent)
grep -c -i -e kama -e round-16 scripts/hyaku/jj-lane.sh                   # exit 1 (0)
grep -c -i -e kama -e round-16 scripts/hyaku/jj-lane-selftest.sh          # exit 1 (0)
pgrep -af shokunin-watchdog ; pgrep -af hyaku/inline ; pgrep -x llama-server  # all exit 1 (none)
```

## Findings

### 1. Steady hit: `.ufo/state/kama.report-baseline` — not a misroot

Path names kama; the file is 68 bytes:

```
16 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

`16` is the round, `e3b0c442…` is SHA-256 of the **empty byte stream**. Provenance, all observed:

- The writer is `record_report_baseline` (`scripts/shokunin-watchdog.sh:120-133`): `state="$UFO/state/$1.report-baseline"`, writes `printf '%s %s\n' "$n" "$digest"`.
- `report_digest` is explicit that "a missing report is the empty byte stream" (`scripts/shokunin-watchdog.sh:107-115`); the hashed path is `$UFO/reports/round-$2/$1.md` (`:121`), i.e. the fleet-root report. `ls .ufo/reports/round-16/kama.md` → exit 2, so the empty digest is correct, not corrupt.
- Call site is `launch_lane`, immediately before spawn (`scripts/shokunin-watchdog.sh:203`); the in-session driver sources that file (`scripts/hyaku/inline.sh:20` — `. "$FLEET/scripts/shokunin-watchdog.sh"`) and dispatched kama: `.ufo/watchdog.log:475` `2026-10-20T10:14:08-03:00 launch kama round=16 pgid=11634 driver=hyaku-inline attempt=1`.
- File mtime `2026-10-20 10:14:06`, two seconds before that launch line.
- This convention is already documented as intentional: `.ufo/waves/kaika-w3/canonical-review.md:273` — "The baseline … (`e3b0c442…`), proven by `A-round-N-plus-1-absent-report-baseline-is-empty-digest`."

Conclusion: harness state under the shared `.ufo/state/<lane>.report-baseline` convention, one of nine identical-format files (kaidoku, kake, kama, mado, mori, souji, tabi, tameshi, tsukuroi). **Do not move or delete it as a kama round-16 artifact.**

### 2. Transient hit: a kama seat wrote round-16 advice at the fleet root

At ~10:56:5x, a diff of my first untracked snapshot against `git ls-files --others --exclude-standard` returned exit 1 adding five paths, including:

```
> .ufo/waves/round-16/falsify/advice/ScoutMetricsSource.md
```

The path is fleet-root (no `kama-shokunin/` prefix; the lane repo is excluded from this index by `.gitignore:1:*-shokunin/`). By 10:57:09 the file was absent: `ls -la .ufo/waves/round-16/falsify/advice/` printed only `.`/`..`; by 10:57:2x `find .ufo/waves/round-16 -maxdepth 3 -type f` returned exactly the six tracked files (`before.md`, `dispatch.md`, `clobber/{classify.sh,classify.out}`, `gate/{mutate.sh,runs.md}`) and `ls -la .ufo/waves/round-16/` showed no `falsify` directory.

The lane copy exists: `kama-shokunin/.ufo/waves/round-16/falsify/advice/ScoutMetricsSource.md`, 9423 bytes, mtime `2026-10-20 10:56`. [INFERENCE] the same seat wrote to the fleet root first and relocated to the lane path; I saw the fleet-root path only in the index, never its bytes, so I do not claim byte identity.

This is direct evidence that at least one kama seat resolves its `Report:` path against CWD (fleet root) before correcting — the failure mode the assignment predicted, caught live and self-healed. Empty fleet-root dirs from the episode were also removed (`find .ufo/waves -maxdepth 3 -type d -name falsify` → no output, exit 0).

### 3. Zero steady round-16 path hits

`git ls-files --others --exclude-standard | grep -i 'round-16'` → exit 1 at 10:55:35 and again at 10:57:09. The only round-16-named fleet-root tree, `.ufo/waves/round-16/`, is fully tracked (6 files, `git ls-files` exit 0) and contains no kama reference (`grep -rIl -i kama` exit 1). Fleet-root `.ufo/reports/round-16/` holds 12 tracked lane reports with no `kama.md`.

### 4. Untracked files that name kama in content but are not kama seats

`.ufo/waves/hyaku/jj-w1/` appeared mid-run (absent from the first porcelain, present 10:54:02-10:54:08) and is the only content hit:

- `spec.json` — `kama` x2: `:42 "name": "JjTrialKama"`, `:44` prompt runs `git clone --bare …/kama-shokunin …` and `rsync -a --exclude=.git … kama-shokunin/ /fast/scratch/jj-wave/JjTrialKama/lane/`; `:152 "JjAuditKama"`, `:154` prompt audits lane `kama` tooling.
- `dispatch.json` — `kama` x2 (`:68`, `:200`, plus prompt copies at `:477-479`, `:587-589`).
- `reports/swarm-registry.json` — `JjTrialKama`/`JjAuditKama` (capital K; `grep -c 'kama'` = 0).

All three: `round-16` count = 0. These are a concurrent hyaku wave's orchestration files, correctly rooted at the fleet root, not kama-seat misroots. [INFERENCE] its `rsync` of the live lane tree is read-only on the source side, but a kama seat writing during the copy yields a torn trial snapshot — a hyaku trial-fidelity risk, not a misroot.

### 5. Ignored path naming kama is the lane root itself

`git ls-files --others --ignored --exclude-standard | grep -i kama` → `kama-shokunin/`, explained by `.gitignore:1:*-shokunin/` (`git check-ignore -v` exit 0). Expected; not an untracked file.

### 6. Second-order divergence surfaced by this baseline [INFERENCE]

`.ufo/state/kama.round` is `1`, mtime `2026-10-15 01:50:57`, while `kama.report-baseline` says round 16 today. The hyaku driver keeps its round in `$HYAKU_STATE` (`scripts/hyaku/inline.sh:19` — `STATE=${HYAKU_STATE:-$HOME/.local/state/shokunin-hyaku}`) and passes its own `n` into the watchdog helper, so `.ufo/state/` now mixes legacy round files with hyaku baselines. Fleet `shokunin.conf:52` still lists `kama|kama-shokunin|…` and sets `SUBSTRATE_CMD` (`:28`). If the legacy `shokunin-watchdog.sh` ever ticks this root, `round_of kama` returns 1, `report_of` reads `.ufo/reports/round-1/kama.md` (10144 bytes, but 0 SHONEN heading/bold markers under the exact `:151` regex) and fails content, so `main()`'s `elif [ -f … ]` branch (`:397-399`) would log `lane-report-not-accepted kama round=1` and relaunch kama at **round 1**. Not live: `pgrep -af shokunin-watchdog` and `pgrep -af hyaku/inline` both exit 1. Repairing `.ufo/state` is outside this seat's write boundary.

## Proposed move (one, bounded, harms nothing)

For L1's misroot sweep: evaluate the predicate **once** from a single `git ls-files --others --exclude-standard` snapshot, and exclude the shared harness prefixes `.ufo/state/`, `.ufo/waves/hyaku/`, `scripts/hyaku/` plus the ignored lane root `kama-shokunin/`. Under the current state that yields **zero** paths, so the correct action is no moves and no deletions; specifically keep `.ufo/state/kama.report-baseline` (live `record_report_baseline` state) and leave the stale `kama.round` to the fleet owner. The non-obvious part is the new guard: add fleet-root `.ufo/waves/round-16/falsify/` to the round's misroot check so the next seat that resolves `Report:` against CWD fails loudly instead of self-healing silently, and make the lane-absolute advice target explicit in the dispatch.

## Risks

- All three porcelain snapshots differ (12 entries at start, 14 at 10:55:35, 14 with different members at 10:57). Any L1 action taken from a stale copy may point at paths that no longer exist — re-snapshot immediately before acting (A3).
- Deleting any `*.report-baseline` for a lane whose same-round report exists removes digest suppression: `report_of` compares digests only when `baseline_round == n` (`scripts/shokunin-watchdog.sh:145-163`), so a content-valid report can then re-trigger `advance` and a duplicate completion. [INFERENCE], from that code path.
- The transient fleet-root advice file may have been a collector/test artifact rather than the scout writing there; attribution rests on identical basename plus a same-minute lane copy.

## Verification

Re-run, from `/home/vgpnk/Projects/shokunin`:

```
git ls-files --others --exclude-standard | grep -i -e kama -e round-16
# expected now: exactly ".ufo/state/kama.report-baseline"; exit 0
ls .ufo/reports/round-16/kama.md          # expected exit 2 (absent)
find .ufo/waves/round-16 -maxdepth 3 -type f   # expected: only the six tracked files
git ls-files .ufo/waves/round-16          # expected exit 0, same six paths
```

## Limitations

- Read-only: no `git add/rm/restore/stash`, no file moves, no writes outside this report; no `.ufo/interactive-sessions`, session or credential stores touched; `measure.py` not run; `llama-server` not started (`pgrep -x llama-server` exit 1 at 10:55) and 8080/34113 not probed.
- Untracked set is `--exclude-standard` (non-ignored); the ignored tree was checked by name only, not enumerated.
- Installs: none.
