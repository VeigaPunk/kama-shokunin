# X1Offline — round 49 witness-dir failure modes (kama, operability)

**Verdict:** the round-49 witness handshake is not self-contained in its directory: a reused `--witness-dir` lets an observer read a previous (or concurrent) run's `ready.json` — with the frozen C1 counter's own `observe()` accepting a *foreign live* server as this replay's witness — and a leftover `release` (or a directory named `release`) ends the hold at once, giving `released: true, waited_ms: 0` with no observation window; an unwritable dir or a `ready.json.tmp` directory surfaces as `internal:*` only after a full server start; concurrent runs collide on the fixed `ready.json.tmp` name (4/48 crashed `internal:FileNotFoundError`). No run left a llama-server alive — every failure path still tore the child down (`sigterm_sent true`, `returncode 0`, `port_refuses true`). A proposed fix (startup clean + writability check, per-run temp name, handshake removal at hold end) is measured clean on the same six probes and on 16/16 concurrent starts.

Tested code: `tools/kama-llamacpp-live.py` at build commit `74558c71c38ceaeace15fd4cf8aa9d84977584b1`. The lane worktree file differs from that commit only in another seat's in-flight `verify_archive_member`/selftest edits; `hold_for_witness` is byte-identical in both (`sha256 cce433f479533a21e80fcee25e907111c03a046985de37ae6e2811eb6d8871c1`, 22 lines). **All line numbers below are from that commit** (`git show 74558c71:tools/kama-llamacpp-live.py`; those in-flight edits shift later lines in the worktree by +11, so cite by commit, not by today's file). Pinned inputs verified: `llama-server` sha256 `35ac50fb…7d8d7ff0` (`/home/vgpnk/.local/opt/llama-b11909/llama-server`), model sha256 `270cba1b…d3bd256d` (`~/.cache/kama-shokunin/models/stories260K.gguf`) — both equal the counter's frozen constants.

## Method

`probes/probe.py` starts the live tool as a child on a scratch witness dir and polls `<dir>/ready.json` every 20 ms from t=0 exactly as the documented observer would, recording for every distinct content `(t_ms, pid, pid_alive_at_read, port_accepts_at_read)`, then releases per scenario and records the receipt (`outcome`, `setup_error`, `witness`), the dir listing, and a `/proc` sweep for `llama-server` before/after:

```
python3 tools/kama-llamacpp-live.py --server /home/vgpnk/.local/opt/llama-b11909/llama-server \
  --model ~/.cache/kama-shokunin/models/stories260K.gguf --model-sha256 270cba1b… \
  --alias kama-x1offline --ctx 256 --threads 1 --probe tools/kama-probe.sh \
  --out RECEIPT --witness-dir D --witness-timeout 30
```

`probes/alias.py` adds the observer test that matters: run A holds its server in `D_A`; A's `ready.json` (live pid/port) is copied into `D_B` as a previous run's handshake; run B starts on `D_B`; the observer reads `D_B/ready.json` and applies **the frozen C1 counter's own `observe()`** (`tools/round49-replay-witness-audit.py:258-289`, imported from the lane file, unmodified) to it. `probes/shared.py`, `probes/stress.py` start 2, 8 and 16 runs on one directory. Nothing was written to the lane; counters, preregistration and controls were only read.

## Results — unpatched tool (all values from `probes/*.summary.json`, receipts in `receipts/`)

| scenario | exit | setup_error | witness released/waited_ms | observer saw (`t_ms, pid, alive, port-accepts`) | dir after run | server leak |
|---|---|---|---|---|---|---|
| fresh dir, observer releases | 0 pass | — | true / 50 | 303, own pid, **true, true** | `ready.json, release` | no |
| stale `ready.json` + `release` | 0 pass | — | **true / 0** | 1, 999999, false, false; 263, own pid, **false, false** | `ready.json, release` | no |
| stale `ready.json` only | 0 pass | — | true / 50 | 2, 999999, false, false; 304, own pid, true, true | `ready.json, release` | no |
| witness dir `chmod 500` | 2 | `internal:PermissionError` | none | nothing | (empty) | no |
| `ready.json.tmp` is a directory | 2 | `internal:IsADirectoryError` | none | nothing | `ready.json.tmp` (dir) | no |
| `ready.json` is a directory | 2 | `internal:IsADirectoryError` | none | nothing | `ready.json` (dir), `ready.json.tmp` (file) | no |
| `release` is a directory | 0 pass | — | **true / 0** | 263, own pid, true, false | `ready.json`, `release/` | no |
| alias (stale live pid from run A) | 0 pass (B) | — | true / 200 | **frozen counter `observe()`: problems `[]`**, nonce `kama witness 249e6259d32eb12a` round-tripped against A's pid | `ready.json, release` | no |
| 8 runs / one dir × 3 rounds | 0 ×24 | — | true ×24 | **1 ready slot per round for 8 runs** | `ready.json, release` | no |
| 16 runs / one dir × 3 rounds | 0 ×44, 2 ×4 | `internal:FileNotFoundError` ×4 | true / — | **1 ready slot per round for 16 runs** | `ready.json, release` | no |

All failure receipts show teardown of a started child (`teardown.sigterm_sent true, returncode 0, port_refuses true`; e.g. `receipts/receipt-stress2-3.json`), and a `/proc` sweep after every scenario found no `llama-server` whose cmdline names my scratch.

## Findings

**F1 — a leftover `release` ends the hold before it starts (`released: true`, `waited_ms: 0`), so the receipt asserts a witness that was never observable.**
`tools/kama-llamacpp-live.py:293-295` (`release = …; while (not os.path.exists(release) …)`) and `:299` (`'released': os.path.exists(release)`) trust any pre-existing path; nothing removes it at start (`:1581-1584` only checks `isdir`) or at end (`:298-300`). Measured: `probes/stale-ready-release.summary.json` → exit 0, `witness {released: true, waited_ms: 0}`, observer's read of the tool's own `ready.json` at 263 ms shows the pid **already dead**, port already closing. A directory named `release` does the same (`probes/release-is-dir.summary.json`). This is the field the frozen C1 counter requires (`round49-replay-witness-audit.py:53`, checked at `:324-326`), so on a reused directory the receipt satisfies that leg with no observation at all: repro `python3 probes/probe.py stale-ready-release $S`.
The frozen counter itself is **not** defeated: `witness_one()` mints its directory under a `mkdtemp` scratch (`round49-replay-witness-audit.py:292-294`) and polls at 200 ms (`:301-305`), so it never sees a file it did not cause. The defect is in the tool's documented interface (`--witness-dir` = "an existing directory", `:1264-1268`), which permits reuse — the same directory the replay tool passes through unchanged (`tools/kama-live-replay.py:275-279`).

**F2 — a stale `ready.json` is readable for the whole pre-hold phase and forever afterwards; with a live pid from another run the frozen counter's `observe()` accepts it.**
`ready.json` is written only after the server is ready (`:288-292`), so from process start until that write the previous run's file is served verbatim (measured readable at 1-2 ms and still there at 263-304 ms — the entire startup), and it is never removed when the hold ends (`:298-300`): after the baseline run the dir keeps `ready.json` naming a dead pid. The alias probe shows the severe form: an observer that applies `round49-replay-witness-audit.py:observe()` to the stale file gets **zero problems** — exe digest, LISTEN inode ownership, `-m` digest and the `/tokenize`+`/detokenize` nonce all match run A's still-live server — i.e. a replay's witness can be certified by a server that is not its own (`probes/alias.summary.json`, receipt `receipts/receipt-alias-b.json` says `released: true`). Repro: `python3 probes/alias.py $S`.

**F3 — the fixed temp name `ready.json.tmp` is shared by every run using the directory; concurrent runs crash each other inside the handshake.**
`:289-292` writes `wdir/ready.json.tmp` then `os.replace` it. Two runs writing at once: the second `os.replace` finds its source already renamed away → `FileNotFoundError`. Measured 4/48 (`probes/stress16.summary.json`, receipts `receipts/receipt-stress2-3.json`, `-stress2-11`, `-stress2-12`, `-stress3-8`): exit 2, `setup_error internal:FileNotFoundError`, **no `witness` block at all**, 11/11 checks true, server torched correctly. Repro: `python3 probes/stress.py $S 16 3`.

**F4 — directory-state failures surface as opaque `internal:*` tokens after a full server start, and leave artifacts.**
`chmod 500` → `internal:PermissionError`; `ready.json.tmp` as a directory → `internal:IsADirectoryError`, with the `ready.json.tmp` directory left in place; `ready.json` as a directory → same plus a `ready.json.tmp` **file** left behind (`probes/tmp-is-dir.summary.json`, `probes/ready-is-dir.summary.json`). Each cost a server start + teardown (~370-400 ms) before failing, and none names the actual cause as a stable token (contrast the tool's `provenance-*` / `setup_error` vocabulary).

**F5 — one directory cannot attribute a handshake: one release ends every hold and one `ready.json` serves N runs.**
8 runs/round: 24/24 released by a single release, exactly 1 discoverable ready slot per round (`probes/shared.summary.json`, and round 2 of `probes/stress.summary.json`); 16 runs/round: 3 slots for 48 runs (`probes/stress16.summary.json`). A `waited_ms` of 0 also appears when the release was written by another run's observer. Not a leak, but a consumer must never infer "N witnessed" from N receipts in one directory.

## Proposed fix

`proposed/witness-dir-hardening.diff` (applies to `tools/kama-llamacpp-live.py` at the measured commit; full patched file also at `proposed/kama-llamacpp-live.py.fixed`). Four changes, `tools/kama-llamacpp-live.py` only:

1. new `prepare_witness_dir()` called from argument validation (`:1581-1584`): unlink an earlier run's `ready.json`, `release`, `ready.json.tmp*`, stale write probes; a non-file collision raises `witness-dir-unusable:not-a-file:<name>`; then write+unlink a per-process probe file, raising `witness-dir-unwritable:<strerror>`. Both become `parser.error('--witness-dir unusable (<token>)')` — exit 2, **no server start, no receipt** (the documented argument-error contract).
2. `hold_for_witness()` writes `ready.json.tmp.<child pid>` instead of the shared name (closes F3), and reads `released`/`waited` before cleanup.
3. `hold_for_witness()` removes `ready.json` and its temp in a `finally` — the handshake names a live child only while it is up (closes the dead-pid half of F2).
4. module docstring and `--witness-dir` help state the single-run contract.

Measured with the patched file (copy in a lane-shaped tree so `LANE/registry` resolves; `probes/fixcheck.summary.json`, `probes/fixcheck-stress.summary.json`, `probes/fixcheck-alias.summary.json`):

| scenario | before | after |
|---|---|---|
| stale `ready.json` + `release` | exit 0, `released true / waited 0`, own pid observed dead | exit 0, `released true / waited 50`, own pid observed **live**, dir left `['release']` only |
| stale `ready.json` (no release) | stale readable 0-304 ms, left behind after exit | stale readable only before the child execs (first 20 ms poll at 0 ms), then absent until the real pid appears at 221 ms |
| `chmod 500` | exit 2 `internal:PermissionError` after a server start | exit 2 `--witness-dir unusable (witness-dir-unwritable:Permission denied)`, no server, no receipt |
| `ready.json.tmp` is a dir / `ready.json` is a dir | exit 2 `internal:IsADirectoryError`, artifacts left | exit 2 `witness-dir-unusable:not-a-file:…`, entry left untouched, no server |
| `release` is a dir | exit 0, `released true / waited 0` | exit 2 `--witness-dir unusable (witness-dir-unusable:not-a-file:release)`, no server (`probes/fixcheck-release-is-dir.summary.json, .stderr`) |
| alias (stale live pid) | frozen `observe()` accepts A's server as B's witness | at 50 ms the reused dir's `ready.json` is **absent** (`accepted_as_witness: false`); at 450 ms it is B's own pid |
| 16 concurrent runs on one dir | 4/48 `internal:FileNotFoundError` | 0/16 errors, 16/16 released |

## Residual limits (not fixed by the diff, stated for the integrator)

- **Process-start window.** A new process cannot remove a file before it runs: a poll at t=0 can still read the previous `ready.json`. Measured window ≤ one 20 ms poll; the frozen counter polls at 200 ms and uses a fresh directory, so it is unreachable there. An observer must still check that the announced pid is alive (the counter does: `:306-308`, `:327-329`) — the tool cannot make a stale read impossible for a reader that starts earlier than the tool.
- **Concurrency stays unsupported.** The per-run temp name removes the crash, but `ready.json` remains one slot and `release` one global path, so two live runs sharing a directory still cross-talk (F5). Closing that needs an exclusive `witness-dir-in-use` lock (O_CREAT|O_EXCL, released from main's finalizer at `:1868-1880`) or a per-run subdirectory; either is a contract change, deliberately not in this diff.
- A directory named `release` counts as released by design (`os.path.exists`, unchanged). With the fix the startup cleanup refuses it rather than deleting it: measured exit 2, `--witness-dir unusable (witness-dir-unusable:not-a-file:release)`, directory left untouched.
- The witness dir is now single-run by contract; `tools/kama-live-replay.py` needs no change for the frozen counter (it passes the dir through untouched).

## Evidence inventory

- `probes/probe.py`, `probes/shared.py`, `probes/stress.py`, `probes/alias.py` — harnesses (copy of what ran; `S=/fast/scratch/hyaku/kama-r49/X1Offline`).
- `probes/*.summary.json` — machine-readable results: `fresh`, `stale-ready-release`, `stale-ready-only`, `unwritable`, `tmp-is-dir`, `ready-is-dir`, `release-is-dir`, `shared`, `shared2`, `stress` (8×3), `stress16` (16×3), `alias`, and the patched runs `fixcheck`, `fixcheck-stress`, `fixcheck-alias`.
- `receipts/` — every live-tool receipt cited (13 unpatched scenario receipts, 48 stress receipts, alias A/B, patched `receipt-fix-*`).
- `proposed/witness-dir-hardening.diff`, `proposed/kama-llamacpp-live.py.fixed`.
- No tool installs or upgrades were needed (stdlib Python, the b11909 install already on host). No pacman transactions were run.

Scratch `/fast/scratch/hyaku/kama-r49/X1Offline` was removed after copying every cited artifact.
