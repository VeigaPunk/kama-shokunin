VERDICT: partial - empty glibc-hwcaps/ refuses before launch as claimed (exit 2, no spawn, gate INVALID); symlinked glibc-hwcaps and access()-OK read failures pass the producer and would launch.
Attacked: C2 `install-tree-unpinnable` fail-closed, end-to-end at a6617149 (clean scratch clone), plus its boundary. No server started; no install change.

## 1. Target run (official CLI, executed)
- `python3 <scratch>/tools/kama-llamacpp-live.py --server <tree>/llama-server --model ~/.cache/kama-shokunin/models/stories260K.gguf --model-sha256 270cba…d256d --out <scratch>/r.json` -> exit 2, empty stdout/stderr, 0.09 s.
- Receipt: outcome setup-error; setup_error `install-tree-unpinnable:glibc-hwcaps:not-regular-or-symlink`; child_pid, port, argv null; checks 0. Refusal at kama-llamacpp-live.py:1375-1379; Popen at :1454.
- `pgrep -af llama-server`: before exit 1, after exit 1. Nothing launched; nothing to kill.
- Gate `check-receipt.py r.json`: exit 1 INVALID, 33 problems; first line: setup_error is 'install-tree-unpinnable:glibc-hwcaps:not-regular-or-symlink' (a complete run has setup_error null). With --require-install-links: exit 1.
- Control (same copy minus the dir, dry-run): tree_sha 6c216313…, links_sha 5cb9f486…, 51 members, 10 links = live receipt b76727f3 values; reaches launch (1 suppressed attempt). The refusal is caused by the directory.

## 2. Boundary variants (dry-run harness: producer unmodified; only Popen of a llama-server basename refused and recorded)
- empty glibc-hwcaps (target) | exit 2 | install-tree-unpinnable:glibc-hwcaps:not-regular-or-symlink | 0 launch attempts | gate 1
- glibc-hwcaps -> abs dir (symlink) | exit 2 | launch-failed:OSError (launch reached) | 1 | gate 1: install_links['glibc-hwcaps'] "leaves the pinned directory"
- unreadable member (chmod 000) | exit 2 | install-tree-unpinnable:libllama-common.so.0.7.0:unreadable | 0 | gate 1
- dir not listable (mode 311) | exit 2 | install-tree-unpinnable:listdir:Permission denied | 0 | gate 1
- name lib\x01x.so | exit 2 | install-tree-unpinnable:'lib\x01x.so':control-character-in-name | 0 | gate 1
- FIFO libfifo.so | exit 2 | install-tree-unpinnable:libfifo.so:not-regular-or-symlink | 0 | gate 1
- non-UTF-8 regular member | exit 2 | internal:UnicodeEncodeError | 0 | gate 1
- simulated EIO on 2 members, access R_OK true | exit 2 | launch-failed:OSError (49 of 51 members) | 1 | gate 1, names only the 2 soname links

## 3. Loader probe (ld.so --list, LD_TRACE mode; no server code runs)
- ld.so --help (glibc 2.44): "x86-64-v3 (supported, searched)". llama-server readelf: RUNPATH [$ORIGIN]; NEEDED libllama-server-impl.so.
- glibc-hwcaps as symlink to a dir: loader reports .../glibc-hwcaps/x86-64-v3/libllama-server-impl.so ("file too short"); a real dir gives the same path; no hwcaps dir -> "not found".

## 4. Findings
- F1 (gap, symlinked hwcaps): install_links() records any symlink (:236-238) and never inspects its target, so `glibc-hwcaps -> dir` passes pre-launch; the loader searches that path first (sec. 3). Only the gate's chain rule rejects it (check-receipt.py:181-198, :464-468). _outcome_exit (kama-llamacpp-live.py:916-928) ignores install_links, so a run whose own checks pass would exit 0 [INFERENCE: code-derived; no live run]. Needs write access to the install dir; detection is gate-only.
- F2 (gap vs. the code's own promise): install_tree() drops a member on any OSError from sha256_file (:196-199); install_links() only probes os.access(R_OK) (:241-242). A member readable per access() but failing open/read is silently dropped; the selftest comment promises "never a silently smaller identity" (:1102-1105). Simulated (monkeypatched EIO on real, readable files): 49 vs 51 members, tree_sha differs from live, launch reached, no refusal. Gate names only the link chains; libggml-cpu-x64.so (non-link) is named nowhere; only --expect-install-tree-sha256 catches it.
- F3 (minor): a non-UTF-8 regular member makes install_tree's .encode() (:201) raise UnicodeEncodeError -> internal:UnicodeEncodeError, not install-tree-unpinnable. Still exit 2, no launch.
- F4 (adjacent, outside C2 text): identity captured once, pre-launch (install_tree/install_links called only at :1375-1376 in main). No post-run re-hash of server, libs or links; the model gets model_sha256_post/model_unchanged (:1676-1683).
- Not exercised: lstat/readlink error branches. Unreachable end-to-end as non-root: the server's own isfile() (:1359) fails first on an unsearchable dir [INFERENCE from code order]. F2 uses simulated I/O; no real EIO was produced.

## 5. Installs, environment, cleanup
- No installs or upgrades. Used pre-existing git, python3 3.14.8, pgrep, getconf, readelf, /lib64/ld-linux-x86-64.so.2.
- Producer sha256 e4cc6d88…; gate sha256 6b876437… (scratch at a6617149; status clean).
- Source ~/.local/opt/llama-b11755 read-only (cp -a copies); still 61 entries, no glibc-hwcaps.
- No subagent dispatch; no model download; no server launched. Scratch /tmp/kama-r21-C2UnpinnableEndToEnd removed.

## 6. Evidence (falsify/out/C2UnpinnableEndToEnd/)
- identities.json; producer-primary.{stdout,stderr,exit}; receipt-primary.json; pgrep-{before,after}.*; gate-primary*.{stdout,stderr,exit}.
- dryrun-<variant>.{receipt.json,stdout,stderr,exit}; gate-dryrun-<variant>.*; dryrun-summary.json; dryrun-harness.py; dryrun-simread-harness.py.
- ld-so-help.stdout; readelf-dynamic-server.stdout; loader-*.{stdout,stderr,exit}; commands-*.json (command, argv, exit).
- First nolist run (mode 711: owner kept read, listdir succeeded) kept as dryrun-nolist-misconfigured-mode711.*; excluded from sec. 2.
- A bash fixture batch exited 1 (tool reported invalid UTF-8 at the non-UTF-8 filename); fixtures were recreated via bytes paths and confirmed by the dry-run receipts.

## 7. For main agent
- Re-grade falsify/out/C2UnpinnableEndToEnd/receipt-primary.json with check-receipt.py (expect exit 1).
- Candidate fixes (not implemented): refuse symlinked glibc-hwcaps; refuse members whose read fails; re-hash install identity after the run; add grid cases for both.
