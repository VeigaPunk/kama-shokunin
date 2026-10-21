VERDICT: partial - ld.so(8) order confirmed verbatim; a pinned tree bypasses step 3 and, for names it supplies, steps 4-5, never step 2; the tree digest authenticates no execution (probes A10-A12); "install-tree identity boundary" overstates.

# LdsoRunpath - ld.so(8) steps vs. pinned install tree (round 19)

Seat: KamaR18Recovery.LdsoRunpath (leaf, no subagents). Evidence: `/tmp/kama-r19-LdsoRunpath/out/REPORT.md`, `receipts.md` (exits, sha256). Driver: `python3 /tmp/kama-r19-LdsoRunpath/out/probe-driver.py` → exit 0, 55/55 checks (run with explicit echo). Lane: this file is the only write.

## 1. The five steps (ld.so(8), man-pages 6.19, 2026-08-03; each quote matched once in the local page)
1. DT_RPATH, only when the object has no DT_RUNPATH.
2. LD_LIBRARY_PATH, ignored in secure-execution mode.
3. DT_RUNPATH, for direct DT_NEEDED entries only: "do not apply to those objects' children".
4. /etc/ld.so.cache; default-path entries skipped under `-z nodefaultlib`.
5. /lib, then /usr/lib; skipped under `-z nodefaultlib`.

## 2. Pinned tree: bypass vs. rely
- The pin bypasses no step. `check-receipt.py` runs outside the loader.
- Step 1: only if linked with `--disable-new-dtags` (A3, A7). Not used: all 49 ELF objects with NEEDED carry `RUNPATH [$ORIGIN]`.
- Step 2: never bypassed (A2; B2 shows it shadows names the tree lacks even under DT_RPATH). Relied on: the launcher's env scrub (tools/kama-llamacpp-live.py:84, :1307-1309, :1338).
- Step 3: the mechanism. Six in-tree sonames resolve here in the real launch. Children need their own RUNPATH (A6).
- Steps 4-5: bypassed only for names the tree supplies. Relied on for libc.so.6, libm, libstdc++, libgcc_s, libgomp, libssl, libcrypto, and transitive libz/brotli/zstd (real trace: cache, then /usr/lib). The cache holds no llama/ggml entries (`ldconfig -p`: 0 hits).
- Outside the five: PT_INTERP `/lib64/ld-linux-x86-64.so.2`; LD_PRELOAD (A9); `glibc-hwcaps/x86-64-v4|v3|v2` subdirectories, searched before the RUNPATH directory (A10); the five soname symlinks (A12).

## 3. Does a tree digest authenticate execution? No.
`install_tree()` (tools/kama-llamacpp-live.py:178-202) hashes 51 depth-1 regular files. Symlinks and subdirectories are skipped (:191-195). Same function, executed:
- A11: DECOY ran via LD_LIBRARY_PATH; digest unchanged.
- A12: a soname symlink was retargeted; ALT ran; digest unchanged.
- A10: a glibc-hwcaps library ran; digest unchanged.
- Control: one changed byte in a regular member changes the digest.

Also: the expected value comes from the same producer (`.ufo/waves/round-18/runs/run.py:57-64`); the pin never executes the server (`install-tree-grid.py:1-18`); `child_env_keys` is self-reported (`check-receipt.py:474-490`). The pre-exec race is not executed **[INFERENCE]**.

## 4. Flagged claims
- **F1 OK:** `corpus/lessons/round-19.md:29` "A tree digest authenticates execution — reject". Keep. Replace the [INFERENCE] marker with probes A10-A12.
- **F2 overstated:** `corpus/SOURCES.md:69` "grounds an install-tree identity pin"; `.ufo/waves/round-19/build/dispatch.json:421` "install-tree identity boundary". S057 grounds the resolution rule for direct DT_NEEDED names. Say that.
- **F3 overclaim:** `.ufo/waves/round-16/build/advice/ConnectSouji.md:109-112` "the receipt's identity claim becomes true of the install tree"; "a swapped … install fails loudly". Symlink retarget, hwcaps directories and env all pass.
- **F4 wording:** `tools/kama-llamacpp-live.py:178-181` and `corpus/knowledge/llamacpp-loading-lifecycle.md:106-107` "install tree of 51 files". That is 51 depth-1 regular files; the 10 symlinks are unpinned.
- **F5 self-referential pin:** `.ufo/waves/round-18/runs/run.py:57-64`, which the lane acknowledges at `corpus/lessons/round-19.md:36-40`. It needs an external anchor: the asset sha256 `753bfa73…` (S038) plus a committed member manifest.
- **F6:** `tests/llamacpp-live/check-receipt.py:474-490` validates child_env names only, not that the scrub happened.
- **F7 (already flagged):** `corpus/lessons/round-18.md:53` "four-pin schema-floor validation": the server pin covers 1 of 51 members.
- **Correct, keep:** `SCORECARD.md:834-835`; `corpus/knowledge/llamacpp-loading-lifecycle.md:285-288, 311-312`; `corpus/lessons/round-18.md:221-222`.

## 5. Advice
1. Reword S057 (F2) to "resolution rule for direct DT_NEEDED names, including $ORIGIN expansion". Keep the reject row.
2. Scope C2 to "51 depth-1 regular files at hash time".
3. For "what runs" evidence: record the objects the server maps after launch (realpath and sha256 from `/proc/<pid>/maps`), and require each to lie inside the tree or on a host allowlist.
4. Extend `install_tree` to symlinks (link text plus target digest) and subdirectories, or fail the gate on unexpected entries.
5. Anchor the expected digest outside the producer (F5).
6. Keep the env scrub. A direct run through `~/.local/bin/llama-server` is outside both the scrub and the pin.
7. Do not build the tree with `-z nodefaultlib`: host libc becomes unloadable (A14).

## 6. Limits and install record
Synthetic probes on glibc 2.44, gcc 16.2.1, binutils 2.47. The real tree was inspected read-only; no llama.cpp process was started. Install record: none (no tools installed or updated).
