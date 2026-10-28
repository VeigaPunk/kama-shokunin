# Round 64 · wave b · SN01Sandbox · security of the C1 counter

Scope: `tools/round64-c1-counter.py` and its subprocess/patch/PATH surfaces at
f6a4ea9a8b5a876d685b08e7e582ec0723412a4a (freeze). Question set: can a tool under
judgment (a) write outside `--work`, (b) signal the counter or its reference
server, (c) read counter memory or the receipt template, (d) abuse `patch -p1`
in `apply_patch`, (e) abuse PATH lookup for server/model/patch, (f) leave
processes behind. Each feasible issue was demonstrated with a harmless proof in
scratch, then rated: **flips verdict** (false `met=True`) or **escape/DoS only**.
Nothing outside scratch was exploited; the real fixture, lane, object store and
`~/.local/bin` were not written (fixture-level tests used a scratch `HOME` with a
copy of the pinned model; see §5).

Scratch clone: `/fast/scratch/hyaku/kama-r64/b/SN01Sandbox/clone` (commits
V1..V10b are scratch-only; not in the lane). Evidence: `.ufo/waves/round-64/b/out/SN01Sandbox/`
(`variants/*.diff` = each malicious tool, `runs/` = raw outputs, `mutants/` = counter mutants,
`labs/` = side experiments).

## 0. Verdict-flip summary

| # | Issue | Demonstrated | Flips verdict? | Rating |
|---|---|---|---|---|
| F1 | Tool tampers the pinned fixture during the run, restores it before the hold window; counter still says `met=True` | V2, V10b (vs unmutated counter) | **YES — false pass** | **HIGH** (C1 "pinned fixture" half is false while `met=True`) |
| F2 | Tool leaves the shared fixture tampered | V3 | no (DoS: met=False, fixture corrupted for others) | MEDIUM |
| F3 | Tool writes outside `--work`; counter follows tool-planted symlinks outside `--work`; same-uid write to shared git object store (lane objects via `--shared` alternates) | V4 + fixture | no observed flip; host/lane integrity escape | **HIGH** (escape) |
| F4 | Post-live inputs (forge patches, tool blob, relabel text, dependency copy) are read from tip/git objects the tool can rewrite | code-read + F3 proof | not demonstrated | MEDIUM |
| F5 | `patch`/`git` resolved via PATH after the tool runs; PATH includes writable `~/.local/bin` | V8 | no (forge controls starved, met=False); arbitrary code in counter's post-live phase | MEDIUM-HIGH |
| F6 | Tool shares counter's process group (no `start_new_session`); `killpg` kills the counter | V5 | no (exit 143, no verdict line) | MEDIUM (DoS) |
| F7 | Tool writes a fake verdict line into the counter's stdout via `/proc/<ppid>/fd/1` | V6 | no (exit code stays 1); text consumers fooled | LOW-MEDIUM |
| F8 | Counter memory readable by tool | V7 (`/proc/<ppid>/mem` PermissionError, Yama=1) | no | LOW (conditional on ptrace_scope) |
| F9 | Tool leaves detached daemons behind; counter never reaps descendants | V7: 17 detached survivors across my V7 runs (one per tool invocation); killed by marker | no | LOW-MEDIUM |
| F10 | Live run failed once on `bind_holders` with no change to tool | V7 run 1 of 4 | no (fail-closed) | operability flake, cause not isolated |

Only **F1** turns a malicious tool into `met=True`. Everything else is an escape,
a DoS, or hygiene.

## 1. F1 (HIGH, flips verdict): the model digest is not bound to what the server loaded

Mechanism, from the counter at f6a4:
- `main()` hashes the fixture once at start (`sha256_path(model)`, line 1470) and
  **caches** it (`_HASH_CACHE`, lines 147/166-178).
- The live bind check `argv_ok` (line 432) compares `sha256_path(realpath(model))`
  — which returns the cached pinned digest, never the file on disk during the hold.
- The only other model identity is `w.get('model_sha256')` (line 709), which comes
  from the tool's own `hold.json` (`'model_sha256': model_sha`, tool line 539),
  i.e. self-reported and computed before the tool's own tamper.
- `grade_binding` runs in `score()` **after** the tool has exited, so any fresh
  digest taken at grade time sees the restored file.

Proof (scratch `HOME`, copy of pinned model; restored byte-identical after):
- **V2** (`68208af`): the tool appends 16 zero bytes to `--model` after its own
  digest check, starts the pinned server on it, and restores the length at exit.
  Evidence log: the file the server was started on has `size=1185392
  sha256=e5651a30…` (≠ pinned `270cba1b…`). Counter output (unmutated, saved as
  `runs/final-V2.out`):
  `tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True`
- **V10b** (`3b04ee7`): the tool swaps a tampered inode in at the fixture path, starts the server
  with `--load-mode none` (no mmap, so the file is read and closed at load), then restores the
  pinned inode by `os.replace` *before* the hold window. Evidence:
  `before-restore ino=277328512 sha=e5651a30a40f | after-restore ino=277475414 sha=270cba1bd510`.
  Unmutated counter: `... errors=0 met=True` (`runs/out-v10orig.txt`).
- Why the probes still agree: 16 trailing bytes are past the last tensor, so the held
  server answers exactly like the reference. The predicate's "pinned fixture" clause
  is therefore false while the counter prints `met=True`.

Counter-side mutants (run from the clone, committed tool, unmutated otherwise):

| Mutant | Change | on V2 | on V10b | on base f6a4 |
|---|---|---|---|---|
| M1 | `argv_ok` digest uncached (`cache=False`) at grade time | `met=True` **SURVIVED** (grade happens after restore) | not run | `met=True` |
| M2 | digest snapshot taken at collect time (`model_sha_at_collect`), graded from snapshot | `live: ["bind_argv"]`, `met=False` (exit 1) **KILLED** | `met=True` **SURVIVED** | `met=True` (not over-strict) |

M2 kills the in-run tamper, but not the restore-before-hold variant: a same-uid tool can
change what the server loaded and restore the bytes before any counter measurement.
A digest taken after the tool's last write cannot bind the loaded bytes. Fix must make
the fixture immutable to the tool (see §6).

Feasibility of the fix on this host (mechanism test, not a counter run):
`bwrap --ro-bind / / --bind <work> <work>` gives `OSError` on append to the fixture and
on writes outside work; writes inside work succeed (`labs/bwrap-mechanism.txt`). Unprivileged
user namespaces are enabled (`unshare -Ur true` ok).

## 2. F2 (MEDIUM, DoS, no false pass): persistent fixture corruption
- **V3** (`1cb93ef`): tamper without restore. The first V3 run printed `met=False` (the forged tools
  inherit the tamper and fail their own digest check, `forge=0/3`, `relabel` could not run).
  Run 2 at the same tip: `live_ok=0/1 ... errors=1 met=False` with `error: fixture model absent or not the pinned sha256`.
- The fixture lives in `~/.cache/kama-shokunin/models`, shared by other consumers; a tool
  can corrupt it for every seat until someone restores it. The counter's startup check
  catches this only for later counter runs.

## 3. F3 (HIGH, escape): writes outside `--work`, planted symlinks, shared object store

Facts from the code: the tool is `Popen`ed with the counter's uid, inherited cwd, real
`HOME`, full `PATH`, no mount/namespace confinement (`witness_run` line 872; env filter
only). `--work` is a convention, not a boundary.

- **V4** (`0936ced`): wrote `outside/proof-outside-work.txt`; then planted symlinks at paths
  the counter writes later: `work/forgeA-build -> outside/victim-dir` and
  `work/genuine-receipt.json -> outside/victim-receipt.json`. Result: the counter wrote the
  forged tool source (800 lines), `x.patch` and `.orig` into `victim-dir`
  (`apply_patch` lines 1149-1154: `makedirs` and `open(...,'w')` follow symlinks), and the
  genuine receipt JSON into `victim-receipt.json` (lines 1580-1582). Verdict unchanged
  (`met=True`) — escape only.
- `patch` itself did not follow those symlinks (see §4); the escape is the counter's own
  `open()`/`makedirs`.
- **Shared object store** (fixture test, `labs/objtamper-result.txt`): `git clone --shared`
  (the recipe) writes `objects/info/alternates` pointing at the lane's `.git/objects`
  (verified on my clone). A same-uid process can unlink and rewrite a loose blob;
  `git show` in the clone then returns the rewritten content (`before: orig-tool-text`,
  `after: EVIL-TOOL-TEXT`). `git fsck` detects it; the counter never runs fsck. The
  counter reads tip blobs with `git show` (lines 157-160, 1170-1171, 1578), so a live tool can
  rewrite the blobs read after its own run (F4), and the same write reaches the lane's
  history for every reader of the lane. I did not write to the real lane store.

## 4. F4/F5 (MEDIUM-HIGH): post-live inputs and PATH lookup

- `apply_patch` runs `patch` with `subprocess.run(['patch', ...])` (line 1156) and
  `forge_variants` runs `blob()` → `git` (line 1169-1171, 1578). Both resolve through
  PATH, with the full inherited environment. These calls happen **after** the live tool
  has run, and `~/.local/bin` (writable by the uid) is on PATH here.
- **V8** (`3aaa641`): the tool plants `patch` into a PATH directory during its run (a
  scratch stand-in for `~/.local/bin`; I did not write to the real one). The counter
  executed it: `planted patch ran: -p1 -F3 -s -i .../forgeA-build/x.patch -d .../forgeA-build` (`runs/v8-hijack.log`).
  Output: `met=False`, `forge=0/3`, `error: forge forgeA: patch did not apply to the tip tool`.
  So the counter runs attacker code in its trusted phase and can starve or feed the forged
  controls. A planted `patch` could return any forged text; I did not run that variant.
- `git` takes the same path (same mechanism). I did not run a planted `git`; [INFERENCE].
- F4 (code-read): the forge patches (`.ufo/waves/round-64/controls/forge-*.patch`, lines
  1170-1171) and the relabel source (line 1578) are read from the tip, so the thing under
  judgment supplies the forgeries it is scored against. The counter does not pin those bytes
  by sha256. The tool's dependency copy `work/tip/tools/kama-llamacpp-live.py` is written
  before the live run and re-copied into forged runs after it (run_controls, ~1630-1640);
  the tool can overwrite it [INFERENCE: code read, not run].
- Remediation: resolve `patch`/`git` to absolute paths (`/usr/bin/…`) once before the live run and
  scrub PATH for children; pin the forge patch bytes in the counter (like `LIBS`).

## 5. F6/F7/F8/F9: signals, output channel, memory, leftovers

- **F6 (signal the counter).** Tool `Popen` has no `start_new_session` (line 872), so
  the tool shares the counter's process group. **V5** (`e6825ba`): `os.killpg(getpgrp(), SIGTERM)`
  → `exit=143`, zero bytes of counter output, pgid = ppid = counter pid. Denial only; no false
  pass. Same-uid `kill(2)` also reaches any same-uid process by pid — [INFERENCE from kill(2) semantics; not exercised on other seats].
- **Reference server (F6b): not reachable.** `reference_run` (line 811) terminates the reference
  server in `finally` before `witness_run` starts (main, lines 1480-1500); no window.
- **F7 (stdout).** **V6** (`1a1dc4d`): the tool writes `…met=True` into `/proc/<ppid>/fd/1`
  (the counter's stdout) and exits 3. Output (piped): line 1 the forged `met=True` line, line 2 the
  real `live_ok=0/1 … met=False`. `exit=1`. `grep met=True` on captured output matches 1 line.
- **F8 (memory).** **V7** (`64a98d1`): `/proc/<ppid>/mem` → `PermissionError` (Yama
  `ptrace_scope=1` on this host); `/proc/<ppid>/fd/1` → open ok. The counter's secrets are the
  per-run probe prompts and reference answers; the probe nonce is not on disk
  (`grep r64p ref-server.log` = 0). No flip identified (the bind checks need the real pinned
  holder). On `ptrace_scope=0` hosts a same-uid read would be possible [INFERENCE].
- **Lab (`labs/dumpable_lab.py`)**: a child of a process that calls
  `prctl(PR_SET_DUMPABLE, 0)` gets `PermissionError` on `/proc/<parent>/fd/1` **and** `/proc/<parent>/mem`;
  default dumpable gives `open:ok` on fd/1. Setting the counter non-dumpable closes F7 and F8 on
  `ptrace_scope=0` hosts. Not in the counter; untested against the full run.
- **F9 (leftovers).** **V7**: every tool invocation left a `python3 -c …` detached (`start_new_session`)
  process; `pgrep` after the counter exited: 17 survivors (reparented to pid 1494). Killed by marker
  (only my processes; `runs/leftover-pids.txt`). The counter's teardown check covers run-port
  holders only, so non-listening leftovers are invisible.
- **F10 (flake).** V7 run 1 printed `error: live: ["bind_holders"]` (`met=False`); V7 re-runs 2
  and 3 and the debug harness printed `met=True`. Holder scan (`holder_pids`) is a non-atomic walk
  of `/proc/*/fd`; fail direction is closed. Not isolated.

## 6. Other surfaces checked

- **Path discovery for the server** (`pick_server`, lines 1443-1452): `shutil.which` then
  `realpath` then sha256 against `SERVER_SHA`; a non-pinned binary on PATH is rejected; a
  pinned-bytes copy would be accepted at its own path and the bind checks would follow that path.
  Code-read [INFERENCE], not run; no false pass because the bytes are pinned.
- **`patch -p1` path handling** (GNU patch 2.8, `labs/patch-2.8-results.txt`): `..` names refused
  ("Ignoring potentially dangerous file name"); absolute names confined under `-d`
  (`+++ /abs/...` → `d/abs/...`); symlinked targets refused ("not a regular file"); new files under a
  symlinked dir refused. The tip-supplied patch text does not escape `-d` on 2.8. The defence is
  patch's, not the counter's, and depends on the patch version.
- Holder checks fail closed on unreadable own-uid fd tables (`unreadable_own`; code-read [INFERENCE], not run), so a tool that makes
  itself non-dumpable makes the live run fail, not pass.

## 7. Mutant / control table (what each counter change does)

| Id | Scored against | Output line (verbatim prefix) | Result |
|---|---|---|---|
| base (f6a4 tool, unmutated) | f6a4 | `tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 ... met=True` | honest tip met=True |
| V2 (tamper + restore at exit) | unmutated | same prefix, `met=True` | **false pass** (F1) |
| V10b (inode swap, no-mmap, restore before hold) | unmutated | same prefix, `met=True` | **false pass** (F1) |
| M1 (uncached digest at grade) | V2 | same prefix, `met=True` | SURVIVED |
| M2 (digest snapshot at collect) | V2 | `tool_present=1 live_ok=0/1 ... errors=1 met=False` / `error: live: ["bind_argv"]` | KILLED |
| M2 | base f6a4 | `... met=True` | not over-strict |
| M2 | V10b | `... met=True` | SURVIVED |
| V3 run 2 (fixture left tampered) | V3 tip | `live_ok=0/1 controls_targeted=0/0 ... errors=1 met=False` / `fixture model absent or not the pinned sha256` | DoS |
| V8 (planted patch on PATH) | V8 tip | `... controls_targeted=73/76 ... forge=0/3 ... met=False` | DoS, code exec |
| V5 (killpg) | V5 tip | (no output), `exit=143` | DoS |
| V6 (fake verdict on stdout) | V6 tip | line 1 forged `met=True`, line 2 real `met=False`, `exit=1` | spoof |

## 8. Not exercised / inferences (labelled)
- [INFERENCE] `kill(2)` reaches any same-uid process; not run against other seats.
- [INFERENCE] planted `git` on PATH poisons `blob()` reads after the live run; same mechanism as V8, not run.
- [INFERENCE] dependency-copy injection into forged runs; code-read only.
- [INFERENCE] `ptrace_scope=0` hosts expose counter memory; not run on such a host.
- [INFERENCE] the counter cannot bind loaded model bytes by measurement alone once the tool is same-uid
  and restores before measurement (M2 + V10b is the exercised case; a proof of impossibility is not claimed).
- Not run: pick_server planted-binary cases; a full counter run with bwrap wrapping the tool (only the mechanism was tested).

## 9. Smallest remediation (ordered by leverage)
1. **Make the fixture and server immutable to the tool.** Run each witness tool in a user+mount namespace with
   `--ro-bind` on the fixture and server dirs and `--bind` only its own work dir (bwrap works here). Keep the
   counter's own digest checks as a second layer. This stops F1, F2, F3-fixture writes and V8's `~/.local/bin` write.
2. **Bind the digest to the run, not to the cache.** Take the model digest at collect time (M2) and again after
   teardown, and drop the tool-supplied `model_sha256` from `live_model_sha`. M2 alone is insufficient (V10b).
3. **Confine the counter's own writes.** Create per-run dirs with `mkdtemp`, open with `O_NOFOLLOW`, refuse
   symlinks under `work` before any write (V4).
4. **Session isolation.** `start_new_session=True` for the tool and the reference server; kill the session after
   release; verify no survivors (F6, F9).
5. **PATH.** Absolute `/usr/bin/patch` and `/usr/bin/git` resolved before the live run; scrub PATH for children (F5).
6. **Pin controls.** Embed the forge patch bytes' sha256 in the counter; read every control input before the live run (F4).
7. **Output.** Write the verdict line to a file the counter creates `O_EXCL`; the consumer must use the exit code.
   Set the counter non-dumpable (`prctl(PR_SET_DUMPABLE,0)`) as a cheap layer on `ptrace_scope=0` hosts (F7/F8).

Counter file, the lane, the object store and `~/.local/bin` were not modified. Scratch was used for all writes; the
pinned fixture in `~/.cache` was not written (scratch `HOME` used throughout; `cmp` identical after each run).

## Tool/version record
- No installs or upgrades. Used present tools: Python 3.14.8, git 2.56.0, GNU patch 2.8, bwrap (`/usr/bin/bwrap`),
  llama-server b11755 (pinned; resolved via `~/.local/bin/llama-server` → `~/.local/opt/llama-b11755`).
- No pacman transaction. No commit in the lane; scratch clone commits are local to the scratch clone.

Final counter line (unmutated base at freeze, `runs/final-base.out`):
`tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True`
