# ExecValidate — SOURCES append block, scratch-mirror validation

Seat: `.ufo/waves/round-37/w1/out/ExecValidate/`. The real `corpus/SOURCES.md` was never
written: sha256 `1e44b4f314f2eb7f671feb537d03030af145713d484cbd326017fcbb5a83e8fe` before and
after this seat's work.

## Mirror built

- `.ufo/waves/round-37/w1/out/ExecValidate/root/corpus/SOURCES.md` — byte copy of
  `corpus/SOURCES.md` (sha256 `51168655a98cd9e436e7f3687cc9ae2833f8dd7d32bfd589d666b3fa3367b359`) with the seven
  normalized rows inserted after line 215 (`| S329 | …`), i.e. inside `## Registry` (line 9)
  and before `## Paths` (line 224). `diff corpus/SOURCES.md <mirror>` shows exactly seven
  added lines (`215a216,222`), nothing else.
- `root/` exists because `sources-census.sh --file` derives the lane directory as
  `realpath(dirname(file)/..)`; used-by (E11) is resolved against that directory. `root/` is a
  seat-local symlink farm over every lane top-level entry and every `corpus/` child except
  `corpus/SOURCES.md`, so E11 resolves exactly as it would in the lane while the registry
  itself is the scratch copy. A naive copy (`raw-copy/corpus/SOURCES.md`, output
  `validate-A.out`) was also tested: it makes every pre-existing row fail E11, because the
  derived directory is the seat dir. That is a property of `--file`, not of the rows.

Normalization applied to the staged rows (source: `/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md`):

- `status` = `mined` (already so), `recheck` = `90d` (the staged cell carried a re-run command
  whose `curl … \| grep …` held a literal pipe; the pipe is gone with the command text),
  `used-by` = the three `corpus/knowledge/` paths, `opened` preserved at `2026-10-23` (the
  staged open date).
- No pipe in any cell: each appended line is `NF=13` under `awk -F'|'` (= 11 cells) and contains
  zero `\|` sequences. The staged rows' only pipes were the escaped `\|` inside the recheck cell.
- Data rows only; the staged file's repeated `| id | … |` header and `|---|---|` separator were
  not appended.

Appended rows as written (mirror lines 216–222):

```markdown
| S330 | vLLM V1 Guide — https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/ | docs | A | vLLM V1 scheduling and batching model as the project documents it; not a runtime observation | §Scheduler — "V1's unified scheduler treats both prompt and output tokens the same way"; §Chunked Prefill — "Chunked prefill is enabled by default whenever possible"; docs page version v0.19.1 | one token budget spans prompt and output tokens; chunked prefill is on by default; FCFS or priority scheduling via `--scheduling-policy` | mined | 2026-10-23 | 90d | corpus/knowledge/kv-cache-reclamation-models.md, corpus/knowledge/prefix-cache-reuse-models.md, corpus/knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md |
| S333 | SGLang Radix Eviction Policy — https://docs.sglang.io/docs/advanced_features/radix_eviction_policy | docs | A | the SGLang KV-cache reclamation rule; engine-internal, carries no endpoint semantics | §Eviction candidates — "The policy scores each candidate and the lowest score is evicted first."; source docs/docs/advanced_features/radix_eviction_policy.mdx @ sgl-project/sglang 77091cea68d0701d6cc71edfb45f2815c4f8d791 (2026-09-29) | only evictable leaves are candidates (unlocked and not shadowed by a child still holding KV); the lowest score goes first; a policy scores but cannot pin KV | mined | 2026-10-23 | 90d | corpus/knowledge/kv-cache-reclamation-models.md, corpus/knowledge/prefix-cache-reuse-models.md, corpus/knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md |
| S334 | SGLang Session-Aware Radix Cache — https://docs.sglang.io/docs/advanced_features/session_radix_cache | docs | A | SGLang session-reference semantics; a session is not a KV pin | §Session references — "Session references are soft protection, not memory pins."; source docs/docs/advanced_features/session_radix_cache.mdx @ sgl-project/sglang d34f7b2326a10cb5f3ba8ec95efb31c761237750 (2026-09-22) | referenced KV can still be evicted; the `session_id` labels cache references only and does not append or reconstruct conversation context | mined | 2026-10-23 | 90d | corpus/knowledge/kv-cache-reclamation-models.md, corpus/knowledge/prefix-cache-reuse-models.md, corpus/knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md |
| S335 | SGLang: Efficient Execution of Structured Language Model Programs — https://arxiv.org/abs/2312.07104 | paper | A | the primary statement of RadixAttention's evictability rule; historical, revision-free by arXiv id | §RadixAttention — "A node is evictable if its reference counter is zero."; arXiv:2312.07104 (abs page) and arXiv:2312.07104v1 (HTML full text) | nodes used by the running batch are protected by a per-node reference counter; LRU eviction recursively removes leaf nodes; cache-aware scheduling sorts the queue by matched prefix length | mined | 2026-10-23 | 90d | corpus/knowledge/kv-cache-reclamation-models.md, corpus/knowledge/prefix-cache-reuse-models.md, corpus/knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md |
| S346 | llm 教程 第 6 章 推理引擎 — https://github.com/AaronYang238/llm/blob/35b83cee12ae26f10b58d4163298352384503907/chapters/06-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E.md | community | B | Chinese reverse-engineering write-up of vLLM and SGLang internals; reproducible file-level detail the upstream docs do not present as a source map, but not authoritative for engine behaviour | §6.4 RadixAttention — "`mem_cache/radix_cache.py` `RadixCache` 基数树 prefix cache" and "`managers/schedule_policy.py` `SchedulePolicy` LPM 等调度策略" | a Chinese-language source map contrasting vLLM's flat hash-chain prefix cache with SGLang's radix tree, naming the concrete source files that implement each | mined | 2026-10-23 | 90d | corpus/knowledge/kv-cache-reclamation-models.md, corpus/knowledge/prefix-cache-reuse-models.md, corpus/knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md |
| S347 | vLLM Automatic Prefix Caching (design) — https://docs.vllm.ai/en/v0.9.0/design/v1/prefix_caching.html | docs | A | vLLM's own prefix-cache design at v0.9.0: how a kv-cache block is keyed and which blocks are reusable; the design page, not an observed runtime | §Automatic Prefix Caching → "Hashing" — "vLLM chooses a hash-based approach"; §Eviction (LRU); docs page version v0.9.0 | each kv-cache block is hashed by its own tokens plus the tokens of the prefix before it, so reuse requires an exact prefix match; only full blocks are cached; the hash key is not collision-free and SHA256 is advised for multi-tenant use | mined | 2026-10-23 | 90d | corpus/knowledge/kv-cache-reclamation-models.md, corpus/knowledge/prefix-cache-reuse-models.md, corpus/knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md |
| S363 | vLLM Automatic Prefix Caching (design), current documentation line — https://docs.vllm.ai/en/v0.32.0/design/prefix_caching/ | docs | A | vLLM's prefix-cache design at the current documentation line, including the hashing default that changed after the page the lane already holds | §Automatic Prefix Caching → Note 2 — "As of v0.11, the default hashing algorithm is sha256, which addresses collision risks."；docs page version v0.32.0 | the SHA256 advice the v0.9.0 page gave became the default at v0.11 and is selectable with `--prefix-caching-hash-algo`; the collision caveat is therefore historical, not a current obligation | mined | 2026-10-23 | 90d | corpus/knowledge/kv-cache-reclamation-models.md, corpus/knowledge/prefix-cache-reuse-models.md, corpus/knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md |
```

## Prescribed command — verbatim

```
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file .ufo/waves/round-37/w1/out/ExecValidate/root/corpus/SOURCES.md
```

Exit code: **1**

```text
file	W04	S031 duplicate url docs.ollama.com/api/tags across scopes
file	W04	S043 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp across scopes
file	W04	S056 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp across scopes
file	W04	S060 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S064 duplicate url docs.python.org/3.14/library/subprocess.html across scopes
file	W04	S065 duplicate url docs.python.org/3.14/library/sys.html across scopes
file	W04	S067 duplicate url man7.org/linux/man-pages/man8/ld.so.8.html across scopes
file	W04	S071 duplicate url git-scm.com/docs/git-cat-file across scopes
file	W04	S077 duplicate url docs.python.org/3.14/library/os.html across scopes
file	W04	S078 duplicate url man7.org/linux/man-pages/man8/ldconfig.8.html across scopes
file	W04	S079 duplicate url man7.org/linux/man-pages/man8/ld.so.8.html across scopes
file	W04	S080 duplicate url nix.dev/manual/nix/2.34/protocols/nix-archive across scopes
file	W04	S081 duplicate url go.googlesource.com/mod/+/refs/tags/v0.42.0/sumdb/dirhash/hash.go across scopes
file	W04	S082 duplicate url git-scm.com/docs/gitrevisions across scopes
file	W04	S083 duplicate url git-scm.com/docs/git-cat-file across scopes
file	W04	S084 duplicate url docs.jj-vcs.dev/latest/cli-reference across scopes
file	W04	S085 duplicate url git-scm.com/docs/git-log across scopes
file	W04	S086 duplicate url tldp.org/HOWTO/Program-Library-HOWTO/shared-libraries.html across scopes
file	W04	S087 duplicate url docs.python.org/3.14/builtins/functions.html across scopes
file	W04	S088 duplicate url docs.python.org/3.14/library/os.html across scopes
file	W04	S093 duplicate url git-scm.com/docs/git-log across scopes
file	W04	S097 duplicate url docs.python.org/3.14/library/subprocess.html across scopes
file	W04	S100 duplicate url git-scm.com/docs/git-config across scopes
file	W04	S103 duplicate url git-scm.com/docs/partial-clone across scopes
file	W04	S105 duplicate url docs.python.org/3.14/builtins/stdtypes.html across scopes
file	W04	S108 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp across scopes
file	W04	S109 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S110 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp across scopes
file	W04	S112 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md across scopes
file	W04	S114 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S115 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S116 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S117 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S118 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S119 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S120 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S121 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S122 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S123 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S124 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S125 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S127 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S129 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/ggml/src/gguf.cpp across scopes
file	W04	S130 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp across scopes
file	W04	S131 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/fit.cpp across scopes
file	W04	S132 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp across scopes
file	W04	S133 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S134 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md across scopes
file	W04	S135 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-kv-cache.cpp across scopes
file	W04	S137 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S141 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S142 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S143 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S144 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S145 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S146 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S147 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S148 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S149 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S150 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S151 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S152 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S153 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S154 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S155 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S156 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S157 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S158 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S159 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S160 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S161 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S162 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S163 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S164 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S165 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S166 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S167 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S168 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S169 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S170 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S171 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S172 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S173 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S181 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S182 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S183 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S184 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S185 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S186 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S187 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S188 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S189 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S191 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	E11	S330 missing used-by corpus/knowledge/kv-cache-reclamation-models.md
file	E11	S330 missing used-by corpus/knowledge/prefix-cache-reuse-models.md
file	E11	S330 missing used-by corpus/knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md
file	E11	S333 missing used-by corpus/knowledge/kv-cache-reclamation-models.md
file	E11	S333 missing used-by corpus/knowledge/prefix-cache-reuse-models.md
file	E11	S333 missing used-by corpus/knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md
file	E11	S334 missing used-by corpus/knowledge/kv-cache-reclamation-models.md
file	E11	S334 missing used-by corpus/knowledge/prefix-cache-reuse-models.md
file	E11	S334 missing used-by corpus/knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md
file	E11	S335 missing used-by corpus/knowledge/kv-cache-reclamation-models.md
file	E11	S335 missing used-by corpus/knowledge/prefix-cache-reuse-models.md
file	E11	S335 missing used-by corpus/knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md
file	E11	S346 missing used-by corpus/knowledge/kv-cache-reclamation-models.md
file	E11	S346 missing used-by corpus/knowledge/prefix-cache-reuse-models.md
file	E11	S346 missing used-by corpus/knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md
file	E11	S347 missing used-by corpus/knowledge/kv-cache-reclamation-models.md
file	E11	S347 missing used-by corpus/knowledge/prefix-cache-reuse-models.md
file	E11	S347 missing used-by corpus/knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md
file	E11	S363 missing used-by corpus/knowledge/kv-cache-reclamation-models.md
file	E11	S363 missing used-by corpus/knowledge/prefix-cache-reuse-models.md
file	E11	S363 missing used-by corpus/knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md
```

(`validate-root.out`, sha256 `953e9cd7e261f460f7ef677eabe21500678b9972570427d30654bc394c5540ef`.)

## Findings

| code | count | scope |
|---|---|---|
| W04 | 93 | pre-existing rows only; identical to the baseline run of the real `corpus/SOURCES.md` (exit 0) |
| E11 | 21 | exactly S330, S333, S334, S335, S346, S347, S363 × the three knowledge paths |
| E01, E12, E02–E10, W01–W03 | 0 | — |

The only E-level finding is E11, and it is environmental: at this instant
`corpus/knowledge/` contains none of `kv-cache-reclamation-models.md`,
`prefix-cache-reuse-models.md`, `prefix-cache-reuse-models-amendment-2026-10-23.md`
(`ls` fails for all three). The append block itself is clean:

- **E12 trap avoided**: the seven rows sit at mirror lines 216–222, after `## Registry` (line 9)
  and before `## Paths` (line 224); the validator emitted no E12. Appending after `## Paths`
  (or under any later heading) would trip E12.
- **E01 avoided**: every appended line parses as exactly 13 bar-delimited fields = 11 cells.
  The only pipe characters in the staged rows were the escaped `\|` inside the recheck
  commands; normalizing `recheck` to `90d` removed them, so no cell holds a literal pipe.
- **E03/E04 avoided**: ids absent from the lane registry (collision check by another seat,
  `ExecCollision.md`: `comm -12` empty), and no appended URL duplicates an existing
  URL+scope pair.
- **Enums**: kinds `docs`/`paper`/`community`; tier A for docs/paper and B for the community
  row (community never tier A); status `mined`; `opened 2026-10-23` is a past date; recheck
  `90d` is a valid cadence.

## Isolation run (E11 removed without touching the lane)

`iso/` is the same mirror plus a materialised `iso/corpus/knowledge/` holding symlinks to the
lane's 27 existing knowledge files and three zero-byte placeholders named exactly as the three
new entries. This only proves E11 is the sole blocker; the placeholders are scratch, never
copied into the lane.

```
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file .ufo/waves/round-37/w1/out/ExecValidate/iso/corpus/SOURCES.md
```

Exit code: **0**

```text
file	W04	S031 duplicate url docs.ollama.com/api/tags across scopes
… 92 further W04 lines, byte-identical to the W04 block of the primary run (`diff` of
  the W04 subsets is empty), elided here only for length …
file	ok	/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-37/w1/out/ExecValidate/iso/corpus/SOURCES.md
```

Counts in that run (`validate-iso.out`, 94 lines): W04=93, ok=1.
No W/E line names S330, S333, S334, S335, S346, S347 or S363. So once the three entries exist
in `corpus/knowledge/`, this append block validates clean against the real lane.

## Risks / notes for the parent

1. **Ordering**: the append must land after (or together with) the three knowledge files.
   Appending first leaves `validate` exiting 1 with the 21 E11 lines above.
2. **`--file` root derivation**: never validate an append from a bare seat copy; the derived
   directory is the seat, and every used-by path in the whole registry then reports E11
   (see `validate-A.out`). Mirror the lane layout (`root/`) or run the validator in the lane.
3. `opened` was kept at the staged `2026-10-23`; the lane's own re-open of these sources this
   round is recorded in the fetch seat artefacts (`FetchS333/`, `FetchS334/`, `FetchS335/`,
   `FetchS346/`, `FetchS347.md`, `FetchS363/`), not in the registry cell.
4. No tool installs or upgrades were needed.
5. Snapshot: the mirror was cut from `corpus/SOURCES.md` while that file carried the lane's
   pre-existing uncommitted round-36 state (git reports it modified against HEAD; that is not
   this seat's doing — its bytes were `1e44b4f…` at first observation and at close). If another
   seat appends to the registry concurrently, re-cut the mirror before comparing.
   Baseline run of the untouched file is saved in the seat dir as `baseline-real.out`
   (exit 0, the same 93 W04 lines).
