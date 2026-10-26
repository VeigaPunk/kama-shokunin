# M1Ctr — C1 counter mutation test (round 49, lane kama)

**Verdict: 9/20 mutants killed (7 via positive evidence, 2 via the fake-witness control flip), 11/20 survived on the available evidence; the counter's witness leg is exercised end-to-end, but the surviving mutants are real coverage gaps — most load-bearing single checks are only exercised against the side that already fails, and the archived base-based control cannot detect a removed exe check.**

## Detectors (evidence set)

| detector | repo | tip | pristine result | purpose |
|---|---|---|---|---|
| POS (lane build) | `$S/lane` (`git clone --shared` of the lane) | `74558c71c38ceaeace15fd4cf8aa9d84977584b1` | `witness=1 cap=1 newrow=1 witnessed=3/3 met=True`, exit 0 | real replay, real llama-server (3 receipts) |
| NEG (build control) | `$S/ctrl/junk-c1b` (fixture: lane @ build + commit swapping `tools/kama-live-replay.py` → `FAKE_REPLAY` from `controls/build_controls.py`) | `001e1a27efaaae597072f1b190d31981701bb6e9` | `witness=0 cap=1 newrow=1 witnessed=0/3 met=False`, exit 1 (only the exe check fails, 3×) | fake witness (K2Cheat shape): python stub serving /tokenize+/detokenize from the model's own vocab, writes ready.json, holds until release, then kills, rerun receipt `witness.released=true`, `match=true` |
| NEG (archived base control) | `$S/ctrl/junk-c1` (same recipe at BASE) | `7e030337d8a3afb2ee62893c5da139243d74d2ac` | `witness=0 cap=0 newrow=0 met=False`, exit 1 | matches archived `junk-c1-fake-witness.c1.out` verbatim (cap=0 because the pre-build live tool at BASE hangs 30 s on the sparse archive) |

Harness: pristine counter = frozen lane `tools/round49-replay-witness-audit.py`, sha256 `86b4a40dd027ad7dd62c71c9694b354d52e88ffdfc04aa83a1bb648799f0d6c1` (matches preregistration). Each mutant = one targeted edit in a scratch copy; all compile. Runs: 3 baselines + 40 mutant runs (20 mutants × POS+NEG) = 43 counter invocations; the 40 mutant runs respect the ≤40 budget. Full receipts: `results/MXX-pos.txt|neg.txt` (+ `.stdout/.stderr/.exit`), all copied to this directory.

## Results

| id | mutation (pristine file:line → change) | mutant sha256 | POS | NEG | verdict |
|---|---|---|---|---|---|---|
| M01 | SERVER_SHA last hex char `…ff0`→`…ff1` (line 31) | `d4a74f98…` | met=False exit 1 | met=False exit 1 | **killed** (POS: exe check) |
| M02 | MODEL_SHA last hex char `…256d`→`…256e` (line 34) | `96327f55…` | met=False exit 1 | met=False exit 1 | **killed** (POS: `-m` hash; also cap leg via `--model-sha256`) |
| M03 | MODEL_URL `stories260K.gguf`→`stories260Kx.gguf` (line 32-33) | `a28cff07…` | met=False exit 1 | met=False exit 1 | **killed** (POS: vocab download fails ⇒ witnesses and cap skipped) |
| M04 | README_COMMIT zeroed (line 35) | `939aecd0…` | met=False exit 1 | met=False exit 1 | **killed** (POS: newrow leg) |
| M05 | newrow `rows(tip)-rows(BASE)`→`rows(tip)-rows(tip)` (line 369) | `3c609d42…` | met=False exit 1 | met=False exit 1 | **killed** (POS: newrow leg) |
| M06 | `met = wl and cl and nl`→`wl or cl or nl` (line 438) | `59ec0be1…` | met=True exit 0 | **met=True exit 0** | **killed** (NEG flip: `or` relaxes the conjunction) |
| M07 | `if exe != SERVER_SHA:`→`if False:` (line 274) | `661c9b6e…` | met=True exit 0 | **met=True exit 0** | **killed** (NEG flip: exe check is the only check the fake witness fails) |
| M08 | `if not li or not (li & pid_socket_inodes(pid)):`→`if not li:` (line 277) | `910a9f00…` | met=True exit 0 | met=False exit 1 | survived |
| M09 | loopback-only address filter dropped (line 221-222) | `bc308b7f…` | met=True exit 0 | met=False exit 1 | survived |
| M10 | `if sha_file(mpath) != MODEL_SHA:`→`if False:` (line 286) | `002815d493…` | met=True exit 0 | met=False exit 1 | survived |
| M11 | piece-value comparison dropped (bad=[]; lines 281-282) | `aa64d24a…` | met=True exit 0 | met=False exit 1 | survived |
| M12 | /detokenize round-trip rule dropped (lines 284-286) | `a5b888f7…` | met=True exit 0 | met=False exit 1 | survived |
| M13 | `rr["witness"].get("released") is True`→`is not False` (line 306) | `82f4d74c…` | met=True exit 0 | met=False exit 1 | survived |
| M14 | teardown `pid_alive(...)` term dropped (line 310) | `030b54e8…` | met=True exit 0 | met=False exit 1 | survived |
| M15 | `port_refuses` returns True on accepted connection (line 176) | `d4740ec8…` | met=True exit 0 | met=False exit 1 | survived |
| M16 | cap expected prefix `provenance-member`→`provenance-sparse` (line 356) | `3ddf0fdb…` | met=False exit 1 | met=False exit 1 | **killed** (POS: cap leg) |
| M17 | cap subprocess `timeout=30`→`timeout=0.001` (line 351) | `a96e6477…` | met=False exit 1 | met=False exit 1 | **killed** (POS: cap leg) |
| M18 | cap positive control `good_case = True` unconditional (line 359) | `cf777dc0…` | met=True exit 0 | met=False exit 1 | survived |
| M19 | newrow `rows(tip)-rows(BASE)`→`rows(tip)` (line 369) | `89476b37…` | met=True exit 0 | met=False exit 1 | survived |
| M20 | `/tokenize` substring requirement dropped (line 371) | `a7d6abf2…` | met=True exit 0 | met=False exit 1 | survived |

## Survivors — findings with proposed killing cases

Killing cases are proposals (adding them would exceed the run budget; the evidence set is the frozen POS/NEG pair plus the archived base control).

1. **M08 (listen inode join).** The `li & pid_socket_inodes(pid)` intersection is never the deciding check on either input (real server and fake stub both own their listener). Killing case: run the real llama-server behind a loopback proxy (e.g. `socat`) so the LISTEN inode belongs to the proxy pid while ready.json claims the llama-server pid; exe/model/nonce all pass — only the intersection catches the mismatch.
2. **M09 (accepted addresses).** No evidence binds a non-loopback listener. Killing case: start llama-server with `--host 0.0.0.0` on a host with a second interface; the counter's `listen_inodes` should require 127.0.0.1/::1 — without the filter the witness accepts a server reachable beyond loopback.
3. **M10 (`-m` hashing).** Both servers parse the actual frozen model as `-m`. Killing case: serve the same vocabulary bytes from a byte-different file (e.g. the stories260K GGUF re-packaged with reordered metadata, same tokens, different sha256); exe/nonce/pieces all pass, only the `-m` hash distinguishes. (C1 limit text already acknowledges a host copy of the binary passes; the model-file identity is likewise only pinned by this hash.)
4. **M11 (piece comparison).** The fake and real servers return vocabulary-correct pieces. Killing case: a server that honors `with_pieces` by returning matching ids but empty/wrong `piece` strings (or omits them) — detokenize still round-trips because ids alone drive it.
5. **M12 (detokenize rule).** Killing case: a server whose `/detokenize` returns garbage (or a static string) while `/tokenize` is correct; the current evidence never exercises the dt equality.
6. **M13 (released check).** Both receipts record `witness.released=true`. Killing case: a rerun receipt that lies (`released=false` or absent) while the server was really held; the mutant accepts it.
7. **M14 (pid-gone).** Both servers are reaped and gone at observation time. Killing case: after release, an orphaned grandchild keeps the claimed pid alive (e.g. a `--ctx` child or a hung subprocess); `pid_alive` is the only term that catches it.
8. **M15 (port_refuses).** Both servers actually stop listening after release; `port_refuses` never returns False on the evidence. Killing case: a teardown bug that leaves the port accepting (server still up) — pristine fails, the mutant passes.
9. **M18 (positive-control logic).** The good archive is executed on both inputs. Killing case: a live tool that wrongly refuses the good (member=server) archive — marker never written — the mutant still grades the case good; only `executed` discriminates.
10. **M19 (newrow BASE diff) / M20 (`/tokenize` text test).** Both tips contain the S494 row with the README URL and `/tokenize`. Killing cases: run at a commit where the row is removed (M19: `newrow` flips 0→1; M20: a row with the README URL but no `/tokenize` literal passes the mutant). The archived base control shows `newrow=0` at BASE, so these become leg-level differences there, not met flips.

## Findings about the frozen materials (not changed; counts as findings)

- **The archived base-based control (`junk-c1-fake-witness.c1.out`) cannot detect removal of the exe check, the very check that fails on it.** At BASE its `met=False` is *also* caused by `cap=0` (pre-build live tool hangs 30 s on the sparse archive) and `newrow=0` (no S494 row). M07 (exe check skipped) survives that control — met stays False — but is killed by the build-based control where cap/newrow are intact and the witness leg is the only failure. The build-based control (`junk-c1b`, tip `001e1a27…`) is the sensitive negative detector for C1's witness claim.
- **M06 shows the `met` conjunction only bounds the all-legs-equal case.** Any setup where one leg systematically fails for unrelated reasons masks a relaxation of another leg; on the lane itself (all legs green) `and`→`or` is invisible.
- **M02 double-effect:** MODEL_SHA feeds both the witness `-m` hash and `cap_leg --model-sha256`; flipping it kills both legs, so a model-digest typo is loudly detected.
- **C1's witness leg depends on a single check (exe) to dismiss the K2Cheat-shaped fake**; every other witness check (listen ownership, model hash, nonce/pieces, detokenize, released, teardown) is duplicated correctly by the fake stub. That is by design of the control, but it means an attacker capable of running the *real* frozen binary under a *different* pid claim (M08) or with a re-packaged model (M10) is only stopped by the one check that the fake can't fake.
- No defect found in the frozen counter; the executable paths all work as documented (exit codes, leg values, detail lines).

## Method notes / evidence

- All runs: `python3 <counter> --repo <repo> --tip <tip> --scratch $S --out <receipt>`; exit codes and verdict lines in `results/` (POS: `MXX-pos.*`, NEG: `MXX-neg.*`; baselines `base-pos/base-neg/base-neg-build`).
- Mutant hashes above; pristine hash `86b4a40d…`; mutation location file:line refers to the pristine counter.
- Control fixtures were created only under `$S/ctrl/` with the `r49-control` fixture identity, toplevel asserted before the first commit, `git clone --shared` (mirrors `controls/build_controls.py`'s recipe; the archived control file was re-produced byte-identically, `base-neg` vs `junk-c1-fake-witness.c1.out`).
- No llama-server processes started by this seat remained at the end (`pgrep -af llama-server` showed none under `$S`).
- `pgrep` before/after showed only sibling seats' live servers (X1Kill/X1Hold/X1Observe), untouched.
- Scratch `$S` removed on completion; this directory holds the receipts.

## Absolute paths written
- Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/M1Ctr.md`
- Evidence dir: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/M1Ctr/`
  - `results/` (43 counter receipts: stdout/stderr/exit/txt), `mutants/` (M01.py–M20.py), `build_mutants.py`, `build_ctrl.py`, `build_ctrl_build.py`, `driver.py`
