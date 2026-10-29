# MT06MapsLib: C1 `bind_maps` falsification (round 64, wave b, operability)

Seat: MT06MapsLib (leaf; no subagent dispatch). Tip under test: f6a4ea9a8b5a876d685b08e7e582ec0723412a4a
(frozen; freeze commit f6a4ea9a). "Unfixed" = `tools/round64-c1-counter.py` exactly as committed at the tip.
"Fixed" = a clone-only corrected copy (diff: `out/MT06MapsLib/counter-fix.diff`, 5.4 KB).
Scratch root `/fast/scratch/hyaku/kama-r64/b/MT06MapsLib/` removed after archiving. Out dir:
`.ufo/waves/round-64/b/out/MT06MapsLib/`.

## 1. Verdict summary

Forgeries were driven through the counter's own `main`. Unfixed runs used the tip counter unmodified; fixed runs
used the corrected clone copy. The forged tool is a clone-only patch of `tools/kama-completion-live.py`: three
hooks, inert unless a JSON mode file is present in the tool's `$HOME`. Each run used a private copy of the pinned
model under a private `HOME`; the shared fixture was never written (sha256 `270cba1b...` verified at the end).

| # | Forgery (unprivileged) | Unfixed counter (tip) | What decides it | Fixed counter |
|---|---|---|---|---|
| H | harness control: forger present, inert | met=True | none | met=True |
| a1 | model path bind-mounted over with other bytes, inside the server's own mount ns (`unshare -Urm`) | **SURVIVED** met=True | path-string equality (line 454); no dev/ino compare | KILLED `bind_ref_files` |
| a2 | model file swapped on disk (new inode, neutral bytes) before the server starts | **SURVIVED** met=True | cached t0 sha256 (lines 166-179, 432, 603); no fresh hash | KILLED `bind_maps`, `bind_ref_files` |
| a3 | as a2 but behaviour-changing bytes | KILLED `live_ref_text` | reference-server answer agreement (not procfs) | KILLED `bind_maps`, `bind_ref_files`, `live_ref_text` |
| a4 | model replaced by a copy with identical bytes (new inode) | **SURVIVED** met=True (content genuine) | none; identity never compared | KILLED `bind_ref_files` (identity stricter than content) |
| b1 | model replaced after load by rename (old mapping unlinked) | KILLED `bind_maps` | procfs: ` (deleted)` suffix on the model mapping (line 445) | KILLED `bind_maps`, `bind_ref_files` |
| b2 | model rewritten in place after load, neutral bytes (`MAP_SHARED`, `r--s`) | **SURVIVED** met=True | no procfs trace; only the t0 cached hash exists | KILLED `bind_maps` (fresh digest) |
| b3 | model rewritten in place after load, weight bytes changed | KILLED `live_ref_text` | reference answers disagree (not procfs) | KILLED `bind_maps`, `live_ref_text` |
| c | `libllama-cli-impl.so` (LIBS sha matches, pinned dir, never loaded by the pinned server), dlopen-injected into the live server by its parent via ptrace | **SURVIVED** met=True | `LIBS` membership only (lines 457-459) | KILLED `bind_ref_files` |
| d | `/usr/lib` file shadowed by a bind mount in the server's own mount namespace (`unshare -Urm`) | **SURVIVED** met=True | `SYSTEM_PREFIXES` skip with no identity or hash (lines 451-452) | KILLED `bind_ref_files` |

Filesystem replacement of any `/usr/lib` file as an unprivileged user: **infeasible** (section 3d).

Tally over the nine forgeries. Unfixed counter: SURVIVED 6 (a1, a2, a4, b2, c, d), KILLED 3 (b1 by procfs,
a3 and b3 by reference agreement only). Fixed counter: KILLED 9 of 9. Honest runs unchanged under the fix
(H and the frozen tool at f6a4 both met=True).

## 2. The one-line counter outputs (families[] list elided; full lines in out/)

Unfixed counter (tip):
- H: `tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True`
- a1 bindmodel-neutral: `... live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 ... errors=0 met=True`
- a2 swap-neutral: `... live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 ... errors=0 met=True`
- a3 swap-changing: `tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 ... eval_selftest=0/3 errors=1 met=False`, with `error: live: ["live_ref_text"]`
- a4 copy-same-bytes: `... live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 ... errors=0 met=True`
- b1 rename-postload: `tool_present=1 live_ok=0/1 ... errors=1 met=False`, with `error: live: ["bind_maps"]`
- b2 inplace-neutral: `... live_ok=1/1 controls_targeted=76/76 ... met=True`
- b3 inplace-changing: `... live_ok=0/1 ... met=False`, with `error: live: ["live_ref_text"]`
- c inject-cli-impl: `... live_ok=1/1 controls_targeted=76/76 ... met=True`
- d shadow: `... live_ok=1/1 controls_targeted=76/76 ... met=True`

Fixed counter (clone copy, `counter-fix.diff`):
- H (inert forger, and frozen tool at f6a4): `tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 ... errors=0 met=True`
- a1 bindmodel-neutral: `live_ok=0/1 ... errors=1 met=False`, `error: live: ["bind_ref_files"]`
- a2 swap-neutral: `live_ok=0/1 ... met=False`, `error: live: ["bind_maps", "bind_ref_files"]`
- a3 swap-changing: `error: live: ["bind_maps", "bind_ref_files", "live_ref_text"]`
- a4 copy-same-bytes: `error: live: ["bind_ref_files"]`
- b1 rename-postload: `error: live: ["bind_maps", "bind_ref_files"]`
- b2 inplace-neutral: `error: live: ["bind_maps"]`
- b3 inplace-changing: `error: live: ["bind_maps", "live_ref_text"]`
- c inject-cli-impl: `error: live: ["bind_ref_files"]`
- d shadow: `error: live: ["bind_ref_files"]`

## 3. Answers to the four attack questions

### (a) Model mapped from another path or copy: does the counter compare device/inode?

**No.** The counter has no `st_dev`, `st_ino`, `samefile` or `lstat`. Its only `os.stat` calls are on
`/proc/<pid>` (uid, line 272) and on the hold file (mtime, line 888). Evidence in the unfixed code:
- The model mapping is accepted by path only: `real = os.path.realpath(p); if real == mp: continue` (lines 454-455).
- The model is hashed once, at start: `if sha256_path(model) != MODEL_SHA` (line 1470). `sha256_path` caches results
  by path (`_HASH_CACHE`, lines 166-179; `cache=True` by default). `bind_argv` (line 432) and `model_digest`
  (line 603) reuse that cached digest and never read the file again.
- Proof of the cache: in `swap-neutral`, the on-disk model during the hold window hashes to `41e16f1c...`, not the
  pin. The unfixed counter still returned met=True, because `bind_argv` and `model_digest` passed on the cached
  `270cba1b...`.
- The mapping's own inode is in `/proc/<pid>/maps` (column 5) and was never parsed.

Hardlink to the same inode: same bytes, harmless (not run separately; [INFERENCE]). A copy with identical bytes (a4)
also passes the unfixed counter. A different-bytes model at the same path (a1, a2) passes it. Maps evidence for a1:
the model mapping is inode 144045570 (tamper bytes), while the on-disk pinned path is inode 75628428; the path string
is identical in both.

### (b) Model replaced after load: which procfs observation, which check?

- **Rename (new inode; old one unlinked): decided by procfs.** `/proc/<pid>/maps` shows
  `.../stories260K.gguf (deleted)` on the model mapping. `maps_ok` returns False on `deleted` (line 445). KILLED by
  `bind_maps`. Evidence: `procfs-unfixed/rename-postload/maps.txt`.
- **In place (same inode; `MAP_SHARED`, perms `r--s`): no procfs trace.** The maps line is unchanged and the bytes
  change underneath the server. The unfixed counter sees neither the bytes nor any identity change, so only the
  cached t0 hash exists. Neutral bytes: SURVIVED (b2). Weight bytes: KILLED, but only by reference answer
  disagreement (`live_ref_text`), not by any binding check.

### (c) Library the pinned server never loads, dlopen-injected from a forged parent

**Feasible; SURVIVED.** Yama `ptrace_scope=1` lets the tool (the child's parent) attach. The clone-only injector
`_mt06_inject` stops the server's main thread, writes the path and a return slot onto the stack, sets `rip` to
`dlopen@@GLIBC_2.34` (libc offset `0x94520`), calls `dlopen(lib, RTLD_NOW)` with an `int3` as the return target,
reads `rax`, then restores registers and detaches. The server keeps answering.

Procfs after injection (`procfs-unfixed/inject-cli-impl/maps.txt`): a new mapping
`/home/vgpnk/.local/opt/llama-b11755/libllama-cli-impl.so` (`r--p`, inode 43271250, under the pinned directory).
The unfixed `maps_ok` accepts it, because the basename's sha is in `LIBS` (lines 457-459). Nothing compares the
loaded set with the set the pinned server loads. The fixed counter rejects it: the reference server's file-backed
set does not contain it (`bind_ref_files`).

The "forged parent" framing holds: the parent is the tool, and it may trace the server only because it is an
ancestor under Yama scope 1.

### (d) `/usr/lib` replaceable without root?

- **As a plain user: infeasible.** All 13 `/usr/lib` files the pinned server maps are `root:root`, mode 644 or 755,
  under root-owned `/usr/lib` (mode 755). `test -w` is false for every one. The only user-owned entry found under
  `/usr/lib` (depth 3) is `/usr/lib/systemd/system-sleep/keyboard-backlight`, which the pinned server does not map.
- **Feasible in the process's own mount namespace: SURVIVED.** Unprivileged user namespaces are enabled
  (`max_user_namespaces=122865`). `unshare -Urm sh -c 'mount --bind SHADOW /usr/lib/libbrotlicommon.so.1.2.0 && exec llama-server ...'`
  runs the real pinned server with a shadow file at that path in its own namespace. Checked on a live server: it
  answers `/health` and `/completion` correctly. `/proc/<pid>/maps` shows `/usr/lib/libbrotlicommon.so.1.2.0` with
  inode 1543600699 on device `103:05` (the shadow's xfs). The genuine file is inode 8043 on device `00:1e`.
  `/proc/<pid>/mountinfo` shows the bind entry.
- **Decider in the unfixed counter:** `if p in SYSTEM_FILES or p.startswith(SYSTEM_PREFIXES): continue` (lines
  451-452) runs before any identity or hash check. Any file mapped at a `/usr/lib/` path passes.
- **Decider in the fixed counter:** the live `(path, dev, ino)` set must equal the reference server's. The shadow's
  device and inode differ (`bind_ref_files`).

Impact note: the shadow in this run is the genuine library with 12 inert bytes (`PADDING-MT06`) appended. That proves
the identity is unchecked. It does not prove attacker code execution. A functional payload would need a trampoline
shim (every `BIND_NOW` symbol must resolve). I did not build one.

## 4. Missing model-file inode/dev check

**Yes, missing.** Nothing compares the mapping's `(dev, ino)` with the file the counter hashed. The model hash is
path-cached and taken once before the tool runs. Consequences as shown above: a1 and a4 pass on identity; a2 and b2
pass on a stale hash. The fix in section 5 covers both.

## 5. Minimal counter fix and its met lines

Clone-only, committed in scratch and archived as `out/MT06MapsLib/counter-fix.diff` (5.4 KB, `tools/round64-c1-counter.py`
only). The shared tip is untouched. Three edits:
1. `read_maps` records each mapping's `dev`/`ino` (parsed from `/proc/<pid>/maps`) and, for the model mapping, a
   fresh (uncached) sha256. `maps_ok` requires that digest to equal `MODEL_SHA`, replacing the bare `real == mp`.
2. `reference_run` (the counter's own pinned server, alive while probed) records its file-backed
   `(path, dev, ino)` set, passed to scoring as `witness['ref_ids']`.
3. `score` adds `bind_ref_files`: the live holder's file-backed `(path, dev, ino)` set must equal the reference set.
   It is compared against the reference's own maps, not `os.stat`: on this btrfs host the maps device for
   `/usr/lib` is `00:1e` while `os.stat` reports `st_dev` 56 for the same file. A stat-based identity check fails the
   honest run. That is why my first draft (stat-based) failed honest runs with `bind_maps` and was replaced.

Honest runs after the fix: frozen tool at f6a4, `met=True` (76/76, families exact, errors=0); inert forger,
`met=True`.

## 6. Harness issues found (for the L1)

1. **Text-patch forged controls are brittle.** My first hook placement altered the `receipt['argv'], stdout=log_f`
   line inside forged tool B's patch context. The counter then printed `forge forgeB2: patch did not apply to the
   tip tool` and met=False on the inert forger. I re-anchored the hooks at lines 73, 304 and 533. Any future edit
   near those contexts breaks the `forge` family the same way.
2. **Forged tools derived from a modified tree inherit its hooks.** Without a one-shot mode file, the forgeA/A2/B2
   tools also swapped or wrapped the model. A persistent on-disk model change then made each derived tool's own
   fresh digest refuse to start (`tool exited before hold.json`; `relabel could not run`). Fixed by consuming the
   mode file on first use and restoring the pinned model at exit. The artifact is the harness, not the forgery.
3. **Sampling is two points.** The binding is read at raw_a and raw_b around the probes. A process that injects and
   then removes or self-unmaps between those points, or changes answers only for unprobed prompts, is not seen by
   the bind layer. **Not tested** [INFERENCE].
4. **Pre-load race not exercised.** I used a deterministic pre-start swap (wrapper), not a racing process. The
   outcome class is the same, but the race itself was not measured.
5. **Hardlink variant not run** (same inode, same bytes; should pass both counters) [INFERENCE].

## 7. Procedure, tools and integrity

- Clone at f6a4 via the recipe. Forger and counter fix were committed only in the scratch clone; their diffs are
  archived and the clone is deleted. No lane commit. No edit outside scratch and my report/out dir.
- Live servers: my own on loopback ports 39106-39108 (diagnostics and shadow test; all killed, none left running).
  Counter runs used its own free ports. Ports 8080 and 34113 were not touched.
- The shared fixture `~/.cache/kama-shokunin/models/stories260K.gguf` was never written; every model mutation was made
  on the private `HOME` copy. Verified intact (`270cba1b...`) at the end.
- Tools: no installs or upgrades. Used what was present: python3, util-linux `unshare`, binutils `nm`, git, the
  pinned `llama-server` (b11755, sha `b6a31a8e...`). `gdb` and `bwrap` were present but not used. Pacman: no transactions.

## 8. Archive

`.ufo/waves/round-64/b/out/MT06MapsLib/`:
- `summary.txt`: verdict lines (unfixed and fixed) per forgery.
- `unfixed-counter/*.txt`, `fixed-counter/*.txt`: full counter output (includes the 76-family list).
- `procfs-unfixed/<forgery>/maps.txt` and `mountinfo.txt`, captured at the post step.
- `counter-fix.diff` (counter), `forger-tool.diff` (forger hooks), `run-mt06b.sh` (driver), `receipts/`.

Last line (counter output at the frozen tip, and the fixed counter's honest control):
`tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True`
Forgeries: unfixed SURVIVED 6 of 9 (a1, a2, a4, b2, c, d), KILLED 3 (a3, b1, b3); fixed KILLED 9 of 9.
