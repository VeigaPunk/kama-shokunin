VERDICT: partial - the default grid reproduces its stated numbers (0/3 pre-pin, 3/3 pinned), but its member set drifts from the round-18 residual (libggml-base is used where the residual names libggml); proposed 3-member set: libllama-common.so.0.7.0, libggml.so.0.27.0, libllama.so.0.7.0.

# TreeMembers — lifecycle members of the llama-b11755 install tree

Receipts: `/tmp/kama-r19-TreeMembers/out/` — `reproduce.sh` (one run, exit 0), per-step exits in `reproduce-exits.txt`, `needed-graph.json`, `member-classification.json`, `cpu-variant-scores.json`, `grid-*.json`. Copy: `/tmp/kama-r19-TreeMembers`. The lane was not modified; this report is the only lane write.

## 1. Lifecycle members (DT_NEEDED closure of `llama-server`, 7 in-tree)

`llama-server` → `libllama-server-impl.so` → {`libllama-common.so.0.7.0`, `libmtmd.so.0.7.0`, `libllama.so.0.7.0`} → `libggml.so.0.27.0` → `libggml-base.so.0.27.0`

- `objdump -p llama-server` (exit 0): NEEDED `libllama-server-impl.so`, `libstdc++.so.6`, `libgcc_s.so.1`, `libc.so.6`; RUNPATH `$ORIGIN`. `ldd` (exit 0) resolves the six in-tree libraries (the launcher is the binary itself) to `/home/vgpnk/.local/opt/llama-b11755/`.
- Fan-in inside the closure: ggml-base 5, ggml 4, llama 3, common 1, mtmd 1.
- Roles (`nm -D`, exit 0): the launcher imports only `llama_server(int,char**)` from impl. Impl imports `llama_backend_init` and 37 `mtmd`-named symbols. `--offline` occurs only in libllama-common (`grep -a -c`: common 1, all other members 0). `ggml_backend_load_all*` and `ggml_backend_load` are defined only in libggml (libllama and libllama-common import `ggml_backend_load_all`); `dlopen`/`dlsym` are imported only by libggml. libggml-base has no loader symbols.

## 2. Loaded at runtime but not NEEDED (15)

- `libggml.so.0.27.0` dlopens 14 `libggml-cpu-*.so` and `libggml-rpc.so`. Observed with `LD_DEBUG=files` on `ggml_backend_load_all_from_path(<tree>)` (exit 0).
- The server path: `llama_backend_init` (libllama, 0x205ca0) calls `ggml_backend_reg_count`; when it is zero it tail-jumps to `ggml_backend_load_all` (objdump, exit 0).
- Scores from each variant's own `ggml_backend_score` (ctypes, exit 0): zen4 1984 (max), cooperlake 1728, icelake 1472, sapphirerapids 0. zen4 is the only variant loaded twice and exports `ggml_graph_compute`.
- [INFERENCE] The loader keeps the max-score variant, so zen4 is the CPU compute kernel on this host; the server's runtime dlopen set is therefore not visible in NEEDED.

## 3. Irrelevant to the lifecycle (29)

LICENSE; `ggml-rpc-server`; `libllama-{batched-bench,bench,cli,completion,fit-params,perplexity,quantize}-impl.so`; and 20 tool binaries (`llama`, `llama-batched-bench`, `llama-bench`, `llama-cli`, `llama-completion`, `llama-connect`, `llama-fit-params`, `llama-gemma3-cli`, `llama-gguf-split`, `llama-imatrix`, `llama-llava-cli`, `llama-minicpmv-cli`, `llama-mtmd-cli`, `llama-mtmd-debug`, `llama-perplexity`, `llama-quantize`, `llama-qwen2vl-cli`, `llama-results`, `llama-tokenize`, `llama-tts`). None is in the closure and none is dlopen'd. `llama` is an upward dependent (it NEEDs the impls). `llama-connect` has no NEEDED or RUNPATH (`readelf -d`, exit 0).

Partition: 7 + 15 + 29 = 51 regular files (`partition_check: true`). The receipt's tree matches the live files exactly (51 entries, combined digest `6c216313…5a2c`).

## 4. Host libraries outside the digest

Direct from the closure: `ld-linux-x86-64.so.2`, `libc.so.6`, `libm.so.6`, `libgcc_s.so.1`, `libstdc++.so.6`, `libgomp.so.1`, `libssl.so.3`, `libcrypto.so.3`. Transitive via libcrypto (`ldd`): `libz.so.1`, `libbrotlienc.so.1`, `libbrotlidec.so.1`, `libbrotlicommon.so.1`, `libzstd.so.1`. None is covered by `install_tree` or its pin.

## 5. Grid (`install-tree-grid.py`, gate = check-receipt.py, exits in reproduce-exits.txt)

| set | pre-pin | with tree pin | receipts |
|---|---|---|---|
| default `{libggml-base, libllama-common, libllama}` (install-tree-grid.py:28-29) | 0/3, harness exit 1 | 3/3, exit 0 | grid-default-*.json |
| **proposed `{libllama-common, libggml, libllama}`** | 0/3, exit 1 | 3/3, exit 0 | grid-proposed-*.json |
| fan-in `{libggml-base, libggml, libllama}` | 0/3, exit 1 | 3/3, exit 0 | grid-fanin-*.json |
| census, all 51 | 2/51 rejected (llama-server, libllama-server-impl.so) | 51/51 | grid-all-*.json |

- Pre-existing cross-checks reject the launcher (check-receipt.py:373-374, `install_tree[llama-server] != server.sha256`) and impl (:396-399, `install_tree[libllama-server-impl.so] != server_impl_sha256`). Those two must be excluded from any pre-pin grid, or the 0/3 baseline is contaminated.
- The member choice does not change the counts: the whole-tree pin rejects any changed digest. The choice only selects which pre-pin acceptances are sampled.
- Before the pin, 20 of the 22 lifecycle-relevant members (7 NEEDED + 15 dlopen) are consistently forgeable and accepted.

**Proposed 3-member set: `libllama-common.so.0.7.0`, `libggml.so.0.27.0`, `libllama.so.0.7.0`.** Reasons: it is exactly the residual's named set (corpus/knowledge/llamacpp-loading-lifecycle.md:309-311 reads `libllama-common`/`libggml`/`libllama`); all three are NEEDED-closure members not covered by a pre-existing cross-check; libggml is the dlopen gateway; libllama-common carries `--offline`; libllama is the engine.

## 6. Findings for the lane (not applied; I did not edit the lane)

1. Drift: `DEFAULT_MEMBERS` in `tests/llamacpp-live/install-tree-grid.py:28-29` uses `libggml-base.so.0.27.0`, but the residual names `libggml`. Either change the default to the proposed set or correct the residual text.
2. zen4 (`libggml-cpu-zen4.so`) executes on this host but is outside NEEDED, so no 3-member NEEDED set contains it. The census already shows it accepted pre-pin and rejected pinned. If runtime coverage is wanted, it is the natural fourth member.
3. Over-binding: the whole-tree pin also binds 29 members the server never loads, so any tool-binary update invalidates the server receipt pin. [INFERENCE from the digest definition; 51/51 measured.]
4. The 13 host libraries in section 4 sit outside the digest. A consistent-swap grid cannot test them; the receipt would need a host-library record to bind them.

## 7. Checks for the main agent

- `bash /tmp/kama-r19-TreeMembers/out/reproduce.sh` (exit 0, about 5 s). Expected exits: pre-pin harness runs 1 (mutants survive); pinned harness runs 0; `leftover-llama-procs` 1 (none); `ld-debug-version-dlopen-count` 1 (no backend load under `--version`).
- No installs or updates were performed. Tools used were already on the host: ldd, readelf, objdump, nm, sha256sum, ps.
- No server or listener was started by this agent; only `llama-server --version` was run. Listeners shown by `ss` belong to other agents and were not touched.

[INFERENCE] items (not executed): the loader keeps the max-score variant; `ggml_backend_reg_count()==0` holds at the server's call site; libmtmd is not exercised for text-only models (no `--mmproj`); zen4 runs the forward-pass kernels during inference.
