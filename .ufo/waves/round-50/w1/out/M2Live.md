VERDICT: 27 mutants against kama-llamacpp-live.py + kama-live-replay.py at 97c864be — 2 killed-by-selftest (M26 witness timeout, M27 TMPDIR KeyError), 9 killed-by-counter (M01, M02, M06, M08, M12, M14, M15, M16 on bind; M20 on teardown), 16 survived: 4 equivalent-class (M05, M10, M11, M22) and 12 coverage findings — the counter cannot see O_NOFOLLOW/fstat/hashing-race guards, the second (server-side) env allowlist, PYTHONPATH/TMPDIR value checks, the pdeathsig layer under its single kill point, or the replay's own model_mapping refusals on the honest path. No contract change proposed; survivors are findings, not license.

# M2Live — round-50 C1 mutation probe (operability)

Detector stack: per-mutant `--selftest`, then the frozen counter
`tools/round50-replay-bind-audit.py --repo $S/lane --tip <mutant commit> --scratch <scratch>`
(each mutant = a one-file commit on top of 97c864bead3ee4a2f629574e77263d33834ec98a in a
`git clone --shared` fixture; the counter materializes the tip via `git archive`, so only
committed bytes are measured; `git diff --name-only <tip> <mutant>` verified = exactly the
mutated file for all 27).

## Baselines (pristine bytes, before any mutant)

| check | result |
|---|---|
| `kama-live-replay.py --selftest` | exit 0, `KLR_SELFTEST pass=23 fail=0` |
| `kama-llamacpp-live.py --selftest` | exit 0, `selftest: ok` (must run inside a lane tree: `refused_ports()` reads `registry/endpoint-consumers.tsv`) |
| counter on tip commit | exit 0, `bind=1 teardown=1 newrow=1 bound=3/3 met=True` (15.6 s wall) |

Pristine sha256 (== lane tip blobs, before and after all runs):
- `tools/kama-live-replay.py`  `d5c58972c0fd8f818b8dd2bd81f6cbc3a87c7f23b65805a804bf09b579a5a239`
- `tools/kama-llamacpp-live.py` `61e777b743aedb55c9532c4892d14a6cf0600f9f6f260595d635ec50ff708507`

## Results

Counter output columns: `bind teardown newrow bound met` + exit code. `counter` = frozen C1.

### kama-llamacpp-live.py mutants (all selftest exit 0 — selftest never exercises model_mapping/_preexec/spawn)

| id | line | mutation | counter output | verdict |
|----|------|----------|----------------|---------|
| M01 | 696 | `f[5] == want` → `f[4] == want` (compare model path to the inode field) | `bind=0 teardown=1 newrow=1 bound=0/3 met=False` exit 1 | **killed-by-counter** — rerun `model-mapping:model-path-not-in-maps`, replay exit 1 |
| M02 | 696 | `f[4] != '0'` → `f[4] == '0'` (accept only pseudo/inode-0 mappings) | `bind=0 teardown=1 newrow=1 bound=0/3 met=False` exit 1 | **killed-by-counter** — same `not-in-maps` surface |
| M03 | 704 | drop `O_NOFOLLOW` from the model open | `bind=1 teardown=1 newrow=1 bound=3/3 met=True` exit 0 | **survived** — symlink-plant race never exercised |
| M04 | 711 | drop `sdev == dev or st_ino == ino` equality (keep `S_ISREG`) | `bind=1 … met=True` exit 0 | **survived** — path-swap race never exercised |
| M05 | 716 | `os.read(fd, min(1<<20, left))` → `os.read(fd, 1<<20)` | `bind=1 … met=True` exit 0 | **survived / equivalent** — `os.read` cannot pass EOF; only a growing file diverges |
| M06 | 719 | `h.update(chunk)` → `h.update(chunk[:4096])` | `bind=0 teardown=1 bound=0/3 met=False` exit 1 | **killed-by-counter** — recorded sha256 `00d77d80…` ≠ frozen model; replay `model-mapping:sha256` mismatch AND counter's own receipt check |
| M07 | 721 | `if left != 0:` → `if False:` (drop model-shrank check) | `bind=1 … met=True` exit 0 | **survived** — model stable during hash |
| M08 | 2002 | `if _child_running(proc):` → `if False:` (records `server-not-running`) | `bind=0 teardown=1 bound=0/3 met=False` exit 1 | **killed-by-counter** — `model-mapping:server-not-running` |
| M09 | 1858 | `child_env` over `CHILD_ENV_KEYS` → over `os.environ` | `bind=1 … met=True` exit 0 | **survived** — upstream `live_env` already strips; second allowlist unobservable alone |
| M10 | 668 | server pdeathsig `SIGKILL` → `SIGTERM` | `bind=1 … met=True` exit 0 | **survived / equivalent** — server exits on SIGTERM; pdeathsig never fires under the counter's kill path |
| M11 | 669–670 | drop `getppid() != _FORKED_PPID[0]` exit (race check) | `bind=1 … met=True` exit 0 | **survived / equivalent** — nanosecond race window |
| M12 | 1882 | `_FORKED_PPID[0] = os.getpid()` → `pass` (stays 0) | `bind=0 teardown=0 bound=0/3 met=False` exit 1 | **killed-by-counter** — every forked server exits(1): `no ready.json (invoker exit 1)` on all legs |
| M13 | 1888 | `preexec_fn=_preexec_pdeathsig` → `None` | `bind=1 … met=True` exit 0 | **survived** — `killpg` teardown covers; server pdeathsig unreachable (live tool never hard-dies) |
| M14 | 726 | record `'dev': ino, 'inode': dev` (swap) | `bind=0 teardown=1 bound=0/3 met=False` exit 1 | **killed-by-counter** — counter's own maps dev/inode join catches the swapped record even though sha256 was correct |
| M15 | 698 | `if not hits:` → `if hits:` | `bind=0 teardown=1 bound=0/3 met=False` exit 1 | **killed-by-counter** — real mapping reported `not-in-maps` |

### kama-live-replay.py mutants

| id | line | mutation | selftest | counter output | verdict |
|----|------|----------|----------|----------------|---------|
| M16 | 88 | `LIVE_ENV_KEYS += "KAMA_R50_CANARY"` | exit 0 | `bind=0 teardown=1 bound=0/3 met=False` exit 1 | **killed-by-counter** — `server parent pid N carries the planted KAMA_R50_CANARY` ×3 |
| M17 | 88 | `LIVE_ENV_KEYS += "PYTHONPATH"` | exit 0 | `bind=1 … met=True` exit 0 | **survived** — PYTHONPATH reaches the live child's environ but `-I` makes it inert; counter checks only the canary *name*, not the environ key set |
| M18 | 114 | `env["TMPDIR"]=work/tmp` → inherit caller's TMPDIR | exit 0 | `bind=1 … met=True` exit 0 | **survived** — TMPDIR *value* never checked anywhere |
| M19 | 319 | `argv` drops `"-I"` | exit 0 | `bind=1 … met=True` exit 0 | **survived** — env stripping already blocks the PYTHONPATH vector; see proposed kill below |
| M20 | 587 | `set_own_pdeathsig()` → `pass` | exit 0 | `bind=1 teardown=0 bound=3/3 met=False` exit 1 | **killed-by-counter** — `teardown: invoker SIGKILLed with 3 descendants; after 30.09 s alive [pids] port ACCEPTS FAIL`. The one mutant that fails teardown while passing bind: proves the replay's own pdeathsig is the root link of the cascade |
| M21 | 316 | `prctl(PDEATHSIG, SIGTERM)` → `prctl(PDEATHSIG, 0)` (cleared) | exit 0 | `bind=1 … met=True` exit 0 | **survived** — live tool's `hold_for_witness` `getppid` poll covers the counter's only kill point |
| M22 | 317–318 | drop `getppid() != me` exit in `_child_pdeathsig` | exit 0 | `bind=1 … met=True` exit 0 | **survived / equivalent** — race window |
| M23 | 332 | `subprocess.run(..., env=env, preexec_fn=_child_pdeathsig)` → drop `preexec_fn` | exit 0 | `bind=1 … met=True` exit 0 | **survived** — same cover as M21 |
| M24 | 347 | `elif mm.sha256 != need:` → `elif False:` | exit 0 | `bind=1 … met=True` exit 0 | **survived** — counter exercises only the honest path; the refusal is dead code under it |
| M25 | 344 | `mm.get("mapped") is not True` → `False` | exit 0 | `bind=1 … met=True` exit 0 | **survived** — same reason |
| M26 | 330 | `"--witness-timeout", str(witness_timeout)` → `"120.0"` | **exit 1** (`FAIL witness-passthrough: timeout=120.0`) | not run | **killed-by-selftest** |
| M27 | 114 | `env["TMPDIR"]=work/tmp` → `pass` | **exit 1** (`KeyError: 'TMPDIR'` at `os.makedirs(env["TMPDIR"])`, uncaught — escapes the `except (OSError, ValueError, TypeError, AttributeError, …)` list) | not run | **killed-by-selftest** |

## Coverage findings (surviving mutants) + proposed killing cases

1. **model_mapping's trust anchors are selftest-blind AND counter-blind on the honest path** (M03, M04, M07). The counter verifies the *result* (recorded dev/inode/sha vs its own observation) but cannot distinguish a correct-by-luck record: nothing exercises the symlink, swapped-inode, or shrinking-file paths. Proposed: add selftest cases to `kama-llamacpp-live.py::_selftest` — (a) `model_mapping(pid, symlinked_path)` must return `mapped: False`/`model-open-failed`; (b) rename a different regular file over the model path between maps read and hash → `mapped-file-is-not-the-model-path`; (c) truncate between fstat and hash → `model-shrank-while-hashed` (needs a one-chunk file or a read hook seam). Each kills its mutant without the 46 s counter.
2. **The server-side env allowlist (`CHILD_ENV_KEYS`, M09) is defense-in-depth the counter cannot isolate.** It only differs from the live_env allowlist when the live child's env already carries extras. Killing case: counter asserts the *server's* `/proc/<pid>/environ` name set ⊆ the rerun receipt's `child_env_keys` (today it checks only the canary name); composes with M17 to become observable.
3. **`LIVE_ENV_KEYS` admits arbitrary names (M17 PYTHONPATH, M18 TMPDIR-value).** The canary check is name-specific (`KAMA_R50_CANARY` in environ keys), so a `PYTHONPATH` leak is invisible — inert only because `-I` neutralizes it. Killing case: counter asserts the live child's environ name set ⊆ `{PATH,HOME,LANG,LC_ALL,TMPDIR}` (or the recorded `env_keys`), and/or a `live_env()` unit selftest on the returned dict.
4. **`-I` is killable today via the user-site vector (M19).** The child inherits `HOME` (allowed). A planted `$HOME/.local/lib/python3.X/site-packages/sitecustomize.py` in the counter-prepared HOME dir is imported by a non-isolated interpreter and stamps the marker — no PYTHONPATH needed. Proposed counter change: `prepare_env` drops a `sitecustomize.py` into `home-<tag>/.local/lib/python*/site-packages/` in addition to the PYTHONPATH dir.
5. **The replay→live-child pdeathsig (M21, M23) and the server's own pdeathsig (M10, M13) are unreachable under the counter's single kill point.** Killing the invoker always flows through `hold_for_witness`'s `os.getppid() == parent` poll and the live tool's `killpg` teardown; the prctl layer only matters when the replay dies at a point where the live tool isn't in the witness hold (non-witness replays, or mid-readiness). Proposed: a teardown leg that SIGKILLs the *replay pid* (invoker left alive) during the hold — under M21/M23 the live child must still die within 30 s; and a leg that SIGKILLs the *live tool* — under M13 the server must die via its own pdeathsig. Honest caveat: under the counter's current instrumented kill point these are equivalent-class.
6. **The replay's own model_mapping refusals (M24 sha check, M25 mapped/absent check) never fire** — the real live tool always records a correct mapping, and the counter re-derives everything from `/proc` itself. These are cheap to kill in the replay's `--selftest`: add a fake live that emits `model_mapping={'mapped': False, 'reason': 'x'}` and one with `sha256` = wrong hex → expect exit 1 with `model-mapping:*` mismatches. Currently no such selftest case exists.
7. **Selftest does catch the honest-path mutants it can see**: M26 (witness timeout passthrough) and M27 (TMPDIR override delete → uncaught `KeyError`, which also shows `replay()`'s `except` tuple omits `KeyError` — a `KeyError` inside `replay()` escapes the `refused` envelope entirely).

## Not killed (equivalent under this detector)

M05 (read bound — EOF caps anyway), M10 (SIGTERM exits the server as cleanly as SIGKILL), M11/M22 (pre-exec ppid race windows; killing them needs a fault injected between fork and prctl — no such seam in either tool or counter).

## Commands (exact)

```
git clone --shared $LANE $S/lane && git -C $S/lane checkout -q 97c864be…
# per mutant:
git -C $S/lane checkout -q 97c864be… -- tools/kama-llamacpp-live.py tools/kama-live-replay.py
<edit>                                   # 27 single-site mutants, manifest.json records each
python3 tools/kama-llamacpp-live.py --selftest                      # live mutants
python3 tools/kama-live-replay.py --selftest --scratch $S/rst-Mnn   # replay mutants
git -c user.email=m2live@r50 -c user.name=M2Live commit -qam "<id>"
python3 $LANE/tools/round50-replay-bind-audit.py --repo $S/lane --tip <mutant sha> --scratch $S/laneN --out $S/Mnn.txt
```

Per-mutant sha256, commits, expected detectors: `manifest.json`. Mutated sources: `mut/`.
Selftest logs: `selftest-logs/`. Counter receipts (stdout + `--out`): `counter/` — e.g.
`counter/M20.stdout` (`teardown … 30.09 s alive […] port ACCEPTS FAIL`), `counter/M16.stdout`
(`server parent pid … carries the planted KAMA_R50_CANARY`), `counter/M06.stdout`
(recorded `00d77d80…` vs frozen `270cba1b…`), `counter/M12.stdout` (`no ready.json`).

## Restoration evidence

- Worktree files after the last mutant: sha256 `d5c58972…` / `61e777b7…` — identical to the pristine copies and to `git show 97c864be:tools/…` of the real lane (verified; `counter/` has `baseline.stdout`).
- Lane repo untouched (all mutations inside `git clone --shared` fixture; mutant commits are children of the tip chain in the clone only). Fixture clone and scratch removed after evidence copy. No llama-server leftovers (`pgrep -f` clean at end).
- Tool installs: none (no package installed or upgraded; only `git`, `python3`, lane tools used).

## Artifacts

- Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/M2Live.md`
- Manifest: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/M2Live/manifest.json`
- Mutated sources (27): `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/M2Live/mut/`
- Selftest logs (27 + pristine): `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/M2Live/selftest-logs/`
- Counter outputs (baseline + 25 mutants): `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/M2Live/counter/`
