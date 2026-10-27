# M3Live — round-52 live-tool mutation probe (seat report)

**Verdict:** 15 mutants of the round-52 surface of `tools/kama-llamacpp-live.py` (frozen build bytes `424b7808…`, commit `5dacf2c7…`): the tool's `--selftest` killed **0/15** (before X5 it never executes `sealed_fd`/`file_seals`/`server_exe`), the frozen C1 counter killed **6/15** (M05 M06 M07 M12 M13 M14) and passed 9; of the 9, M08 is equivalent-by-construction, M01/M02/M03/M04/M09 are killed by the in-flight X5Selftest already sitting uncommitted in the lane worktree, and **M10 + M11 (`server_exe` forged `nlink`/`seals`) and M15 (model `abspath`) survive every detector that exists today** — a verified ~20-line `_server_exe_selftest()` patch kills M10/M11 and runs clean on pristine (proposed, not applied).

## 1. Scope and method

- Target: build bytes `424b7808b3f897dd148f7a190dffb72159f9d0fa3ad75d9bfebad8be3bdad50a`, proven equal to `git -C <lane> show 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8:tools/kama-llamacpp-live.py | sha256sum` (both `424b7808…`).
- Scratch `S=/fast/scratch/hyaku/kama-r52/M3Live` (TMPDIR pointed there). One `--shared` clone at `$S/lane`, detached at `5dacf2c7…`; `git rev-parse --show-toplevel` asserted equal to `$S/lane` before every fixture commit (identity `fx <fx@invalid>`, message `mutant <id> (M3Live fixture, scratch clone only)`); after every counter run `git -C $S/lane reset -q --hard 5dacf2c7…` and the file sha256 re-verified — **all 15 rows show `restored`** (`counter-outputs`/`c1-matrix.tsv`).
- Detector 1 (bounded, per role): `python3 <layout>/tools/kama-llamacpp-live.py --selftest` on each mutant, restored from pristine after each run (sha asserted each iteration).
- Detector 2 (for survivors): frozen C1 `python3 <lane>/tools/round52-replay-memfd-audit.py --repo $S/lane --tip <mutant commit> --scratch $S/c1-<id>`, one fixture commit per mutant.
- **Baseline C1 (pristine, unmodified tip `5dacf2c7…`): `bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True`, exit 0** (37.2 s) — see `c1-base.out`. Without this green baseline every mutant verdict would have been inconclusive; it was run first.

## 2. Detector-1 baseline note (operability, not a lane defect)

The first pristine baseline failed: `--selftest` on a bare detached copy exits 1 with `kama-llamacpp-live selftest: SetupError`; the traceback is `refused_ports()` → `SetupError('registry-unreadable:…')` because `REGISTRY` resolves as `<script>/../registry/endpoint-consumers.tsv` (pristine `:520-525`; `REGISTRY = LANE / 'registry' / 'endpoint-consumers.tsv'`). Fix: mirror the lane layout (`layout/tools/…` + `layout/registry/endpoint-consumers.tsv`). After that the pristine baseline is `selftest: ok …`, exit 0. Any seat testing this tool outside the tree must copy the registry file too.

**Detector-1 result: 15/15 mutants pass `--selftest` (exit 0, `selftest: ok`).** `_selftest()` (pristine `:1630-1734`) calls `_install_identity_selftest()` and `_provenance_selftest()` only; grep over the build bytes shows `sealed_fd` called only at `:1955`, `file_seals` at `:747/:780(seal-def)/:795`, `server_exe` at `:2113/:2116` — none under `_selftest`. X5's in-flight docstring says the same ("No case called sealed_fd before this one, so deleting the seal test or the digest comparison from it left the selftest green").

## 3. Mutant matrix (pristine line numbers)

Full diffs in `diffs/M*.diff`, mutant hashes in `selftest-matrix.json`, raw counter outputs in `counter-outputs/c1-M*.out`, machine summary in `c1-matrix.tsv`.

| id | site (pristine) | mutation | selftest | C1 | verdict |
|----|-----------------|----------|----------|-----|---------|
| M01 | `sealed_fd` :796 | mask check `!= SEALS_ALL` → `!= 0` | pass | `met=True` rc=0 | **survived** (X5 kills; my patch kills) |
| M02 | :775 `SEALS_ALL = 15` | → `1` | pass | `met=True` rc=0 | **survived** (X5 seals=3 case kills) |
| M03 | :796 | drop `seals is None or` | pass | `met=True` rc=0 | **survived** (X5 unsealable case → TypeError; my kill2) |
| M04 | :798 size check | `!=` → `>` | pass | `met=True` rc=0 | **survived** C1 — masked by digest; X5's `want_size=len+1` case kills |
| M05 | :807 digest compare | `!=` → `==` | pass | rc=1, all legs 0 | **killed** (`bind b1: no ready.json (invoker exit 1)`) |
| M06 | :819 pread | offset arg dropped | pass | rc=1, all legs 0 | **killed** (digest diverges >1 MiB → refusal) |
| M07 | :800 | `off = 0` → `1` | pass | rc=1, all legs 0 | **killed** |
| M08 | :828 return | `'sha256': h.hexdigest()` → `want_sha` | pass | `met=True` rc=0 | **survived — equivalent by construction**: the return is reachable only after `h.hexdigest() != want_sha` raised, so the two values are equal on every reachable return. Probe-design error on my side; no tool finding. |
| M09 | `file_seals` :795 | `except OSError: return None` → `return 15` | pass | `met=True` rc=0 | **survived** — strongest false-accept: any unsealable regular file with matching size+digest is accepted as a "sealed memfd", i.e. the exact round-51 copy-at-member-path decoy class this round was built against. X5 kills it; counter never can (see §5.4). |
| M10 | `server_exe` :771 | `'nlink': st.st_nlink` → `0` | pass | `met=True` rc=0 | **survived — open gap** (no detector reads receipt `server_exe.nlink`) |
| M11 | `server_exe` :747 | `seals = file_seals(fd)` → `SEALS_ALL` | pass | `met=True` rc=0 | **survived — open gap** (counter requires only "seals including those four"; a constant 15 satisfies it) |
| M12 | main :1995-1997 | `executable=/proc/<pid>/fd/N` → `server_real` | pass | rc=1, `bind=0 sealed=0 teardown=1` | **killed** — counter's own sealed leg: `running image link '…/work-b1/server/llama-b11909/llama-server' is not an anonymous memfd`, `F_GET_SEALS … Invalid argument`. The core round-52 witness demonstrably detects an exec-from-disk swap. |
| M13 | main :1957 | `LD_LIBRARY_PATH` line deleted | pass | rc=1, all legs 0 | **killed** (server cannot load install-tree libs) |
| M14 | main :1997 | `cwd` line deleted | pass | rc=1, all legs 0 | **killed** (ggml backend lookup) |
| M15 | main :1961 | `os.path.abspath(args.model)` → `args.model` | pass | `met=True` rc=0 | **survived — open gap at replay level**: the replay always passes an absolute `--model` (`kama-live-replay.py:354`, `os.path.join(work, "download", …)`), so the counter cannot see the abspath. |

## 4. Proposed killing cases (verified)

Two patches, both **run clean on pristine and verified to kill** by loading each mutant module and running the new assertions (matrix in `proposal-kill-matrix.json`); neither applied to the lane:

- `proposed-sealed-fd-selftest.patch` — `_sealed_fd_selftest()`: refuses a sealing-capable **unsealed** memfd (`F_GET_SEALS == 0`; kills M01 — note `seals=1` alone does *not* discriminate M01, pristine refuses it too), a single-seal memfd (`F_SEAL_SEAL` only; kills M02), an unsealable regular file (kills M09; M03 surfaces as the `TypeError: unsupported operand type(s) for &: 'NoneType' and 'int'` instead of a clean `SetupError`), plus `server_exe` on a plain child (kills M10/M11). Verified: pristine clean; M01 `kill1(bit=None)`, M02 `kill1(bit=1)`, M03 TypeError, M09/M10/M11 AssertionError.
- `proposed-server-exe-selftest.patch` — `_server_exe_selftest()` alone: `server_exe()` on a plain `python3 -c 'import time; sleep'` child must record `seals is None` and a real `nlink`. Verified: pristine clean; M10 → `KILLED … nlink forged on path-backed image`; M11 → `KILLED … seals forged on plain image`. **This is the minimal delta over the in-flight X5Selftest, which does not touch `server_exe`.**

M15 has no selftest-level kill (the path is built in `main`); the kill case is a replay/invoker variant passing a **relative** `--model` from a foreign cwd — the mapped model must still hash correctly (`model_mapping`); not runnable against the frozen counter, left as a proposal. M04/M08 need none (see table).

## 5. Findings

1. **Selftest coverage gap (pre-X5), confirmed with killed mutants:** before X5, `--selftest` exercised none of the round-52 functions (0/15). The uncommitted worktree adds `_server_fd_selftest()` (worktree `tools/kama-llamacpp-live.py:1650-1719`, worktree sha `71deb078…`) whose cases kill M01/M02/M03/M04/M09 — my independent matrix confirms each claimed kill semantics (including that its `want_size=len+1` case catches M04, which the counter never can).
2. **Open gap — `server_exe` forged fields (M10/M11):** the counter's `sealed` leg requires the receipt's `server_exe` to have "opened true, the frozen digest, the same dev and inode, and seals including those four"; a constant `nlink=0`/`seals=15` satisfies it, and no selftest reads those fields. Fix proposed and verified (`proposed-server-exe-selftest.patch`).
3. **Open gap — model abspath unobservable (M15):** the round-52 "gets an absolute model path" guarantee (main :1958-1961) is dead weight under the frozen replay, which always passes absolute paths. Either accept it as caller-contract defense or add a relative-path replay case.
4. **Counter-level observation:** the frozen C1 counter's positive replay never presents a bad `--server-fd`, so **no false-accept in `sealed_fd` (M01/M02/M03/M04/M09-class) can ever be caught by C1** — C1 kills image swaps (M12) through its own `/proc/<pid>/exe` witness, not fd validation. Tool-selftest coverage (X5 + the exe patch) is the only line of defense for fd validation; worth a line in the scorecard census.
5. **Lane state observation (not my change):** lane worktree `tools/kama-llamacpp-live.py` is modified-uncommitted (`71deb078…`) while `HEAD:tools/…` (`34d8260…`) still hashes the build bytes `424b7808…`; the worktree also adds `F_SEAL_EXEC`/`memfd_noexec()` (worktree :776, :779, :810-814) absent from the frozen build bytes — outside this probe's frozen target.
6. No tools were installed or updated. Process hygiene: `pgrep -af llama-server` shows one family left over **from sibling seat M1Ctr's scratch** (`/fast/scratch/hyaku/kama-r52/M1Ctr/…`, pid 3231311) — not started by me, left untouched; zero leftovers under `M3Live` paths. All 16 counter runs exited (rc 0/1, no timeouts); each proved its own teardown leg or failed before ready.

## 6. Restoration evidence

Per-mutant, in order: mutant file copied into `$S/lane` → toplevel asserted → fixture commit `<12-hex tip>` (column 2 of `c1-matrix.tsv`) → frozen counter run → `git reset -q --hard 5dacf2c7…` → `sha256sum` recomputed equal to `424b7808…` (column 5 `restored`, 15/15). The scratch layout copy was restored from pristine bytes after every selftest with the same sha assertion. The lane repo, its worktree, and its jj/git state were never written by this seat; scratch `$S` removed after this report was written.
