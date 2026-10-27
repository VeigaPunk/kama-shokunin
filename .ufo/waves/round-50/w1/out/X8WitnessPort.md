# X8WitnessPort — witness-directory state across repeated runs

**Verdict: three consecutive witnessed replays in one emptied witness dir are clean (exit 0, match
true, 11/11 checks, atomic per-run announce, nothing but a stale `release` left behind), but the
handshake carries no run identity: two runs in one dir destroy each other's announces, one `release`
ends every hold in the dir, and a second run's `prepare_witness_dir` interleaved with an announce
turns a good run into an uncaught `FileNotFoundError`. None of that is reachable by C1 as written
(one fresh dir per replay), so C1's `bind=1` is unaffected; the risk is any future concurrent or
shared-dir use of witnessed replays.**

Seat: X8WitnessPort (lane kama, round 50, w1 attack+frontier). Lane and counters **not edited**:
findings only, proposed patch in `proposed-witness-identity.diff`.

## What ran

- Clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r50/X8WitnessPort/lane`
  → HEAD `3b79eaddf38246c637cc7ba1a94ab363422876b6`. Build commit `97c864bead3ee4a2f629574e77263d33834ec98a`:
  `git diff --stat 97c864be… HEAD -- tools/` is empty (the only later change is
  `.ufo/waves/round-50/measured/*`), so the tools measured here are the build's tools.
  sha256 `d5c58972c0fd8f818b8dd2bd81f6cbc3a87c7f23b65805a804bf09b579a5a239` = `tools/kama-live-replay.py`,
  `61e777b743aedb55c9532c4892d14a6cf0600f9f6f260595d635ec50ff708507` = `tools/kama-llamacpp-live.py`.
- Input: `.ufo/waves/round-48/c2/live/receipt-1.json` (copy in `results/input-receipt-1.json`),
  schema `kama-llamacpp-live/v5`, model sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`,
  server sha256 `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0`.
- Every replay was the frozen pair end to end, one dir per scenario:
  `python3 <clone>/tools/kama-live-replay.py --receipt receipt-1.json --work W --out J --witness-dir D --witness-timeout T`
  (argv recorded verbatim in `results/{seq,stale,conc,inotify}.json`). `TMPDIR=/fast/scratch/hyaku/kama-r50/X8WitnessPort`,
  scratch removed at the end. Python 3.14.8. No tool installed or upgraded; no pacman (paused).
- Drivers (copied into this directory, run from the scratch clone):
  `probe.py seq|stale|conc` (outside observer polling the dir at 2 ms, plus the replay's own receipts),
  `probe_race.py` (loads the frozen tool as a module and drives `prepare_witness_dir`/`hold_for_witness`
  with stub children to make the two-run interleavings deterministic — nothing in the lane is touched),
  `watch.py` (libc inotify via ctypes on the witness dir during one real replay).
- No `llama-server`, replay or live-tool process from this seat was left behind
  (`pgrep -af llama-server | grep -c X8WitnessPort` → 0); the clone is `git status --porcelain` clean.

## Verified — operability (all exit 0)

### 1. Three consecutive witnessed replays, same dir, emptied between runs (`results/seq.json`)

| run | pre-state of dir | server pid | port | `written_utc` | bodies seen / parse errors | release→ready gone | `witness.waited_ms` | match | checks | model_mapping | port_refuses | dir after |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `[]` | 583099 | 44837 | 2026-10-27T01:01:05.547Z | 1 / 0 | 2452.8 → 2480.2 ms | 50 | true | 11/11 | true | true | `['release']` |
| 2 | `['release']` | 605737 | 43297 | 2026-10-27T01:01:08.312Z | 1 / 0 | 2399.6 → 2426.8 ms | 50 | true | 11/11 | true | true | `['release']` |
| 3 | `['release']` | 625589 | 38531 | 2026-10-27T01:01:11.015Z | 1 / 0 | 2332.9 → 2360.1 ms | 50 | true | 11/11 | true | true | `['release']` |

Every run: `ready.json` a single, always-valid body (`{schema, port, pid, written_utc}`), one body
only (zero parse errors across the run's repeated 2 ms reads), a fresh pid/port/`written_utc` per run,
`ready.json` removed 27–28 ms after the observer's `release` and before the replay exits, teardown
`returncode 0 sigterm_sent true sigkill_sent false port_refuses true`, `model_mapping.mapped true`
sha256 `270cba1b…`. Replay exit 0, `match true`, `mismatches []` in all three; the only note is the
expected `tool.sha256` difference (the receipt records the round-48 live tool, `1e5ea0fd…`).

### 2. Atomic replacement and per-run temp names, observed in the kernel (`results/inotify.json`)

One real replay under an inotify watch on its witness dir (child pid 1806082, port 37867, checks 11/11,
match true), events verbatim:

```
1946.20 CREATE       .witness-write-probe.1802937
1946.21 CLOSE_WRITE  .witness-write-probe.1802937
1946.22 DELETE       .witness-write-probe.1802937
2297.55 CREATE       ready.json.tmp.1806082
2297.56 CLOSE_WRITE  ready.json.tmp.1806082
2297.56 MOVED_FROM   ready.json.tmp.1806082
2297.56 MOVED_TO     ready.json
2333.30 CREATE       release
2333.31 CLOSE_WRITE  release
2347.76 DELETE       ready.json
```

`ready.json.tmp.1806082` is the per-run temp name keyed by the llama-server child pid
(`tools/kama-llamacpp-live.py:338`), closed before `MOVED_TO ready.json` — the announce is a real
`rename(2)` inside the directory, so no observer can read a torn body. `ready.json` is deleted
14.5 ms after the observer's release (`hold_for_witness` finally, line 367) and `release` persists.

### 3. Pre-planted stale artifacts (`results/stale.json`, `results/rerun-stale.json`)

Planted before the run: `ready.json` naming dead pid 999999 / port 41234 / `written_utc`
2026-01-01, `release` (empty), `ready.json.tmp.123456`.

```
0.1 ms    dir = ['ready.json', 'ready.json.tmp.123456', 'release']   (stale body readable)
0.1–2329.8 ms  observer reads the stale body 1112 times (pid 999999 not in /proc)
2331.9 ms dir = []            <- the live tool's prepare_witness_dir() (line 299-303)
2668.9 ms dir = ['ready.json'] <- fresh announce, pid 648123 / port 45115
4169.1 ms observer writes release (1.5 s after the announce, on purpose)
4173.8 ms dir = ['release']    <- ready.json gone
```
Receipt: `witness.released true`, `witness.waited_ms 1503`, `match true`, 11/11, exit 0. So the
planted `release` did **not** cut the hold short (it was removed before the server started) and the
stale `ready.json`/tmp were removed — but only at 2331.9 ms, i.e. after the replay's downloads
(`prepare_witness_dir` runs at argument-parse time of the live child, line 1716, which starts after
`acquire`/`extract` in `kama-live-replay.py`).

### 4. A second run started while the first is held (`results/conc.json`, `results/rerun-conc{A,B}.json`)

Both runs the same `--witness-dir`, started 1 s after A's announce:

```
A: pid 678026  port 36923  written_utc 2026-10-27T01:01:18.102Z  witness.waited_ms 3508  released true  exit 0  match true  11/11
B: pid 703502  port 39375  written_utc 2026-10-27T01:01:21.521Z  witness.waited_ms  100  released true  exit 0  match true  11/11
```
At B's announce (A's clock 5857.9 ms): both servers listening on distinct loopback ports and both
pids distinct —
`LISTEN … 127.0.0.1:36923 users:(("llama-server",pid=678026,fd=3))`,
`LISTEN … 127.0.0.1:39375 users:(("llama-server",pid=703502,fd=3))`; `/proc/678026` alive;
`ss` and `/proc/<pid>/exe` both name each run's own clone-extracted binary. A's server was never
disturbed by B, and both teardowns were clean (`port_refuses true`). Two servers on distinct ports:
**yes**.

The directory itself is not run-safe, though — see L1/L2.

## Leaks and defects between runs

**L1 (design, medium): no run identity, one shared release.** `ready.json` carries
`{schema, port, pid, written_utc}` (`tools/kama-llamacpp-live.py:332-333`) and the release trigger is
the single path `<dir>/release` (line 352, tested at line 358). Consequences, measured:
- An observer started for run B reads run A's body immediately: `results/conc.json`,
  `observerB.foreign_bodies = [{ms 0.1, pid 678026, port 36923}]`. Nothing in the body says whose
  run it is, so an outside witness cannot tell "my server is ready" from "the other run is ready".
- One release ends every hold in the dir: both observers write the same path `<dir>/release`
  (A's at 5902.3 ms; B's at 2442.1 ms after its own start) and B's hold ended 100 ms after its own
  announce (`witness.waited_ms 100`) on that shared file — a release addressed to no run. Deterministic
  proof: `probe_race.py` case3 (`results/race.json`) holds two stub runs in one dir, one `release`
  returns `released true` for both (`waited_ms 751` and `500`).
Proposed fix: per-run announce/release names or a nonce the release must echo; refuse a dir that
already holds a live handshake (flock). See `proposed-witness-identity.diff` (not applied — tools frozen).

**L2 (leak, medium): runs delete each other's announcements.** `prepare_witness_dir` unlinks
`ready.json`, `release` and `ready.json.tmp*` unconditionally (lines 299-303), and
`hold_for_witness`'s finally unlinks `ready_path` unconditionally (lines 366-371). Measured in the
concurrent run, A's observer timeline:

```
2411.4 ms ready.json appears (pid 678026)
5485.2 ms ready.json disappears        <- B's prepare_witness_dir; A's server still held and listening
5829.9 ms ready.json appears again     <- B's announce (pid 703502); A's observer sees its own body replaced
5882/5902 ms both observers write <dir>/release (shared path, no run identity)
5919.5 ms ready.json gone              <- B's hold ended and its finally removed its own body (B was
                                          released by the shared file, waited_ms 100)
5944.6 ms A's replay exits             <- A's finally unlinks ready_path unconditionally (line 367)
```
So for ~345 ms (5485.2→5829.8) the directory was empty while **both** servers were up: a late
observer cannot distinguish "run finished" from "another run preempted the handshake", and a counter
waiting for `ready.json` in that dir sees it vanish. That the hold-end unlink takes *another* run's
announcement is proven deterministically: `results/race.json` case1 —
`other_prepare_removed_first_announcement true`, and after run A's hold ends
`a_end_removed_b_announcement true` with `b_still_held_at_a_end true`, `listing_at_a_end []`
(B's announcement is deleted while B is still held).
Proposed fix: identity-checked unlink (hunk 2 of the diff).

**L3 (race, low probability, high cost): announce can fail with an uncaught `OSError`.** Between
`os.open(..., O_EXCL)` (line 343-347) and `os.replace(tmp, ready_path)` (line 351) the temp file
exists; a second run's `prepare_witness_dir` unlinks `ready.json.tmp*` (line 300) in that window and
the rename raises `FileNotFoundError`, which nothing catches (`hold_for_witness` has no handler
around the replace; the caller is inside `main`'s `except BaseException` → `_record_internal`,
`kama-llamacpp-live.py:2172/2184/2194`), so a run whose server passed all 11 checks would be emitted
as an internal-fault/setup-error receipt. Deterministic interleaving of exactly the frozen code
paths (`probe_race.py` case2, `results/race.json`): `raised {"type": "FileNotFoundError",
"str": "... ready.json.tmp.999003 -> .../ready.json"}`, `os_replace [{"src": "ready.json.tmp.999003",
"dst": "ready.json"}]`. Not observed in the real runs (announce window < 2 ms; the 2 ms observer never
saw the tmp name either) — a race, not a live failure.
Proposed fix: hunk 1 of the diff (`try/except OSError` around the replace → `witness-dir-unusable:announce-race`).

**L4 (leak, low): `release` outlives its run and cleanup starts late.** After every run the dir is
exactly `['release']` (`seq_final_dir`, and both concurrent runs' `dir_after`); nothing deletes it
when the hold ends (the finally removes only `ready.json`/tmp, lines 366-371), so it is removed only
by the next run's prepare. Between replay start and that prepare (~2.3 s of downloads here, 2331.9 ms
in the stale run) the previous state is what an observer reads: a dead-pid `ready.json` and a
`release` naming no run. A correct observer ignores a dead pid (my observer did, 1112 reads), but the
window is the whole download time, not "before the server starts" as the docstring says
(`kama-llamacpp-live.py:52-61`).
Proposed fix: unlink `release` in the hold's finally as well, and move `prepare_witness_dir` to just
before the announce (or have the replay prepare its own dir before downloading).

**L5 (clean, no action): nothing else leaked.** Per run: exactly one distinct `ready.json` body, zero
parse errors, unique pid/port/`written_utc`, no `ready.json.tmp*` or `.witness-write-probe*` residue,
`ready.json` gone before exit, teardown `port_refuses true`, exit 0.

## Risk to C1 and to this round's claims

C1's counter creates a fresh witness dir per tag and runs one replay per dir, sequentially:
`tools/round50-replay-bind-audit.py:399 os.makedirs(wd)` (no `exist_ok`, so a leftover dir is a hard
error) and `start_replay`/`wait_ready` at 396/408 with `READY_WAIT 600` (line 110). With a fresh
empty dir neither L1 (no second body) nor L2 (no second run) nor L3 (no concurrent prepare) can
occur, and L4's window holds no previous state. So C1's `bind=1` evidence is unaffected by this
report. The exposure is future work: any fan-out of witnessed replays over one directory, or a
reused dir, would give `wait_ready` a vanishing or foreign `ready.json` (a 600 s false negative per
replay) and would join the wrong pid to the wrong receipt — exactly the class of defect round-49 R1
closed. If round 51 wants concurrent witnessed replays, it needs the identity/lock change, not a
bigger timeout.

## Evidence index (this directory)

- `summary.json` — machine-readable digest of every figure cited above.
- `results/seq.json`, `results/rerun-seq{1,2,3}.json`, `results/replay-seq{1,2,3}.json` — scenario 1.
- `results/inotify.json` — scenario 2 (kernel events for one replay).
- `results/stale.json`, `results/rerun-stale.json`, `results/replay-stale.json` — scenario 3.
- `results/conc.json`, `results/rerun-conc{A,B}.json`, `results/replay-conc{A,B}.json` — scenario 4.
- `results/race.json` — deterministic interleavings (case1 cross-run deletion, case2 announce race,
  case3 shared release).
- `results/input-receipt-1.json` — the round-48 receipt replayed (copy of the lane file).
- `probe.py`, `probe_race.py`, `watch.py` — the drivers, as run.
- `proposed-witness-identity.diff` — proposed hunks for `tools/kama-llamacpp-live.py` (frozen; not applied).

The copied rerun receipts keep their original paths and argv strings under
`/fast/scratch/hyaku/kama-r50/X8WitnessPort/…`; that scratch tree was removed after the copies
(`rm -rf`, one live clone only, no `/tmp` evidence). Everything cited above is in this directory or
in the lane clone at `3b79eadd…`.

Blockers: none. Not exercised here (owned by other seats / out of scope): kills during download or
readiness, teardown of the replay under SIGKILL (C1's teardown leg, seat X1Kill), and the second
counter C2.
