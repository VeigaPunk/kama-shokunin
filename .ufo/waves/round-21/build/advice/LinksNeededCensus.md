VERDICT: partial - grid's last link libmtmd.so.0 is DT_NEEDED and its cell breaks loading; first link libggml-base.so is a developer link no ELF NEEDs, so 8 of 9 link cells miss the loader

Scope: read-only census of ~/.local/opt/llama-b11755 (61 entries: 51 regular, 10 symlinks, 0 dirs; 50 ELF, 1 non-ELF LICENSE). Draft a29bb84 read from a scratch clone; lane not written. Raw data: build/out/LinksNeededCensus-6/ (members.tsv, links.tsv, needed.tsv, census.json, ldd-scenarios.json, ldd-real-llama.txt, grid-cell-map.tsv, grid-mirror-loader.json, unreached-members.txt).

## Commands (exit)
- `command -v readelf objdump file ldd python3; readelf --version` → 0 (GNU readelf 2.47 present; nothing installed)
- `find <tree> -printf …` → 0 (61 entries); `find <tree> -mmin -180` → 0, empty (tree unmodified)
- `git clone -q <lane> <scratch>/lane && git checkout -q a29bb84…` → 0; HEAD a29bb84…
- `readelf -d -W`, `objdump -p`, `readelf -h -W` on each of 50 ELF members → 0 in all 150 calls; readelf and objdump agree on NEEDED/SONAME/RUNPATH/RPATH for 50/50
- `file <tree>/llama` → 0 (dynamic PIE); `file <tree>/llama-connect` → 0 (static-pie, stripped)
- `env -i PATH=/usr/bin:/bin ldd <tree>/llama` → 0 (27-line closure); `readelf -d -W` on 6 host libs → 0
- `printenv LD_LIBRARY_PATH` → 1 (unset in tool env)
- Scratch `cp -a <tree> <scratch>` → 0 (ldd runs in §3-4 used only the copy); scratch and clone removed, verified

## 1. Links: loader-relevant = named by DT_NEEDED
| link | readlink | final regular | NEEDED-by | class | grid cells |
|---|---|---|---|---|---|
| libggml-base.so | libggml-base.so.0 | libggml-base.so.0.27.0 | 0 | developer | first: 8 cells |
| libggml-base.so.0 | libggml-base.so.0.27.0 | same | 33 | NEEDED | regular-append-byte (its final file) |
| libggml.so | libggml.so.0 | libggml.so.0.27.0 | 0 | developer | - |
| libggml.so.0 | libggml.so.0.27.0 | same | 8 | NEEDED | - |
| libllama-common.so | libllama-common.so.0 | libllama-common.so.0.7.0 | 0 | developer | - |
| libllama-common.so.0 | libllama-common.so.0.7.0 | same | 16 | NEEDED | - |
| libllama.so | libllama.so.0 | libllama.so.0.7.0 | 0 | developer | - |
| libllama.so.0 | libllama.so.0.7.0 | same | 18 | NEEDED | - |
| libmtmd.so | libmtmd.so.0 | libmtmd.so.0.7.0 | 0 | developer | - |
| libmtmd.so.0 | libmtmd.so.0.7.0 | same | 4 | NEEDED | last: link-retarget-second |
- All 10 final files carry DT_SONAME = the versioned name (`libX.so.0`); developer links resolve through their `.so.0` sibling and are never SONAME, NEEDED, or literal names.
- Needers of libmtmd.so.0: libllama-server-impl.so, llama-mtmd-cli, llama-mtmd-debug, llama-tts.
- Other DT_NEEDED: 8 tree regular impl libs (libllama-{batched-bench,bench,cli,completion,fit-params,perplexity,quantize}-impl.so: 2 needers each; libllama-server-impl.so: 3). 8 host sonames absent from tree (ldd → /usr/lib): libc.so.6 49, libstdc++.so.6 45, libgcc_s.so.1 45, libm.so.6 23, ld-linux-x86-64.so.2 18, libgomp.so.1 15, libcrypto.so.3 3, libssl.so.3 3.

## 2. DT_* census (members.tsv, 50 rows)
- DT_NEEDED: 21 distinct = 5 tree links + 8 tree regular + 8 host. In-tree NEEDED resolve to tree paths under `env -i` ldd; the mechanism is DT_RUNPATH=$ORIGIN on 49/50 members (llama-connect has none). No member has DT_RPATH.
- DT_SONAME: 13 members. No developer-link name appears as a literal in any ELF.
- 37 members are reached by no DT_NEEDED: 22 executables, libggml-rpc.so, 14 libggml-cpu-*.so. "libggml-cpu-" appears nowhere in the tree, so their runtime lookup is unverified [INFERENCE: runtime plugin loading].

## 3. Grid cells (draft build_cells, install-links-grid.py L113-146; run verbatim against symlink-exact mirrors with 16-byte placeholder regular files)
`first, second = links[0], links[-1]` (L113) → first = libggml-base.so (developer), second = libmtmd.so.0 (NEEDED); other_member = LICENSE (L115-116, non-ELF).
| cell(s) | changed entry | loader effect (ldd on scratch copy) |
|---|---|---|
| link-retarget-second | libmtmd.so.0 (NEEDED) | BREAKS: llama and llama-mtmd-cli rc 1, "libmtmd.so.0: invalid ELF header" |
| link-retarget-member, link-dangling, link-delete, type-link-to-regular-copy | libggml-base.so (developer) | none, closure == S0 (executed) |
| link-absolute-outside, link-dotdot, link-same-resolution-shortcut, link-loop | libggml-base.so (+ .loop) | none [INFERENCE, not executed] |
| link-add, regular-add-file | new names | none [INFERENCE] |
| regular-append-byte | libggml-base.so.0.27.0 (final of NEEDED libggml-base.so.0) | loads, closure == S0: content changes, resolution doesn't |
Answer: the first cells do not exercise a loader-relevant soname. The last cell does, but only via link-retarget-second, and its target is a non-ELF file, so it tests "unloadable", not "valid ELF with wrong soname". Non-grid check S5: dangling NEEDED link libggml-base.so.0 makes llama print "libggml-base.so.0 => not found" with rc 0, so ldd rc is not a loader gate.

## 4. Advice (L1 decides; nothing applied)
- Identity is not loader-scoped: install_links() (tools/kama-llamacpp-live.py L205-226) pins every symlink, and the gate (check-receipt.py L458-467) checks every link. Developer-link cells test identity and gate, not ld.so. The grid docstring (L105) calls all links "soname links"; 5 of 10 are not.
- For loader coverage: take first/last among the 5 NEEDED-named links and add a NEEDED-dangling cell (S5 shape). [INFERENCE: needs DT_NEEDED data via readelf or a pure-Python parser; the grid has no ELF dependency today.]
- Host closure (libc, libstdc++, libgomp, libssl, libcrypto; libz/libbrotli*/libzstd via host libcrypto's NEEDED) sits outside install identity [INFERENCE: host drift is unpinned].

## 5. Unexecuted reasoning [INFERENCE]
- ld.so searches LD_LIBRARY_PATH before DT_RUNPATH; the user's shell environment was not checked.
- llama-server reaches libmtmd.so.0 via libllama-server-impl.so (static NEEDED chain; llama-server not run).
- "Alphabetical" = Python sorted() code-point order; same first/last under locale collation by inspection.
