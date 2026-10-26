# S9D2Row — registry row S483 (`vllm/entrypoints/cli/preload.py` at v0.31.0) and Gate line

Round-43 closure defect **D2** (`corpus/lessons/round-43-verifier-spotcheck.md:106`): the
process-attribution claim in `corpus/knowledge/runtime-health-surface-processes.md` rests on
tier-C S481 plus a committed `preload.py` copy that had no registry row. This seat registers
that code source and cites it from the entry's `source:` line.

## Re-fetch and digest comparison

```
curl -sS -o preload-refetched.py https://raw.githubusercontent.com/vllm-project/vllm/v0.31.0/vllm/entrypoints/cli/preload.py   # HTTP 200
sha256sum preload-refetched.py .ufo/waves/round-43/c3/vllm-v0.31.0-preload.py
d2704e80c08f49455c048724dce8d1eeb22bfa9bc97961ef567106425effa57d  preload-refetched.py
d2704e80c08f49455c048724dce8d1eeb22bfa9bc97961ef567106425effa57d  .ufo/waves/round-43/c3/vllm-v0.31.0-preload.py
```

Byte-identical, 12631 bytes both, `content-length: 12631` in the response headers
(`fetch-head.txt`). Independently, the blob at the PR's merge commit
`e7900156e130c9880eb03b7c1f2df32820e7a2be` (`gh api repos/vllm-project/vllm/contents/vllm/entrypoints/cli/preload.py?ref=e7900156…`, git blob sha1
`50734a052bb01b613a831f982c3ad0449951a123`, 12631 bytes) has the same SHA-256;
`cmp` reports identical (`mergecommit-e7900156-preload.py`).

## The route lines (tag v0.31.0, 339 lines)

| line | text | role |
|---|---|---|
| 70 | `def _build_health_app(state: _HealthState) -> FastAPI:` | app builder |
| 73 | `    @app.get("/health", include_in_schema=False)` | route registration |
| 74 | `    async def health() -> Response:` | handler |
| 75 | `        return Response(status_code=200 if state.is_ready else 503)` | the only status expression |
| 63-67 | `is_ready` property; line 67 `return ready and not any(proc.exitcode is not None for proc in self.processes)` | readiness predicate |
| 302 | `        health_state.mark_ready()` | reached after the startup loop; the exit path (288-301) ends in `sys.exit` |
| 133-138 | `--weight-cache-health-port`, `default=None`, line 137 `help="Port for the parent /health endpoint; disabled by default."` | opt-in gate |

Mechanical quote check: all 10 quoted line texts above were compared to the fetched file
line by line — 0 mismatches.

## Registry row (exact 11-cell schema, `| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |`)

Insert as line 235 of `corpus/SOURCES.md`, directly after S481 (line 234).

| S483 | vLLM preload health route @ v0.31.0 — https://raw.githubusercontent.com/vllm-project/vllm/v0.31.0/vllm/entrypoints/cli/preload.py | code | A | which process answers the `/health` route that v0.31.0 ships and the HTTP states it can return — one file at one tag; not the inference server's `/health` (S004), not the pull request's description of the change (S481), and not runtime behaviour or a later tag | §`_build_health_app` lines 70-77: route registration line 73 `@app.get("/health", include_in_schema=False)` and handler line 75 `return Response(status_code=200 if state.is_ready else 503)` §`_HealthState.is_ready` lines 63-67, line 67 `return ready and not any(proc.exitcode is not None for proc in self.processes)` §startup gate line 302 `health_state.mark_ready()`, reached only if no rank exited during startup (the exit path at lines 288-301 ends in `sys.exit`) §opt-in flag lines 133-138, help line 137 "Port for the parent /health endpoint; disabled by default." §tag v0.31.0; raw SHA-256 d2704e80c08f49455c048724dce8d1eeb22bfa9bc97961ef567106425effa57d, 12631 bytes, re-fetched 2026-10-26 (copy .ufo/waves/round-44/w1/out/S9D2Row/vllm-v0.31.0-preload.py), byte-identical to the committed copy .ufo/waves/round-43/c3/vllm-v0.31.0-preload.py and to the blob at merge commit e7900156e130c9880eb03b7c1f2df32820e7a2be (git blob sha1 50734a052bb01b613a831f982c3ad0449951a123) | the `/health` route in v0.31.0 is served by the preload CLI's own health app for the weight-cache daemon parent, not by the inference server; it returns exactly two HTTP outcomes — 200 only while `is_ready` holds (every daemon process alive and `mark_ready` already called after startup) and 503 otherwise, so `starting` and `failed` are indistinguishable on the wire — and no listener exists unless `--weight-cache-health-port` is set | mined | 2026-10-26 | on-release | corpus/knowledge/runtime-health-surface-processes.md |

Twelve `|` characters = 11 cells; no cell contains a pipe. Duplicate-URL check: `grep -c 'preload.py' corpus/SOURCES.md` → 0 before this row, so the URL and scope are new.

## Gate line (for the round lesson)

- **S483** — https://raw.githubusercontent.com/vllm-project/vllm/v0.31.0/vllm/entrypoints/cli/preload.py, accessed 2026-10-26 (`curl -sSI`, HTTP 200, `content-length: 12631`; SHA-256 `d2704e80c08f49455c048724dce8d1eeb22bfa9bc97961ef567106425effa57d`, copy `.ufo/waves/round-44/w1/out/S9D2Row/vllm-v0.31.0-preload.py`; equal to the tag file named by `refs/tags/v0.31.0` and to the merged blob at `e7900156e130c9880eb03b7c1f2df32820e7a2be`). Located quote for the process half, line 73: `@app.get("/health", include_in_schema=False)` inside `_build_health_app` (line 70), which `_start_health_server` (line 80) is called with only when `args.weight_cache_health_port is not None` (line 263) — i.e. the preload CLI's own app. Located quote for the states half, line 75: `return Response(status_code=200 if state.is_ready else 503)` (**11 words**). Read beside line 67, `is_ready` is false until `mark_ready()` (line 302), so 503 covers both "starting" and "failed" and the wire carries no distinction. The scope is one file at one tag: it is not evidence about the inference server's `/health` (S004), not runtime behaviour, and not a later tag.

## One-line edit of the entry's `source:` line

`corpus/knowledge/runtime-health-surface-processes.md:1` (704 chars today) gains one S483 clause and
nothing else changes. Full proposed line 1 (`entry-source-line.proposed.txt`, 1234 chars):

```
source: S480 — vLLM v0.31.0 release notes — https://github.com/vllm-project/vllm/releases/tag/v0.31.0 — §Fast restart — opened 2026-10-25 (`gh api repos/vllm-project/vllm/releases/tags/v0.31.0`, tag published 2026-10-05T06:44:55Z, 60454 bytes, SHA-256 `20c282d566d6788b0913bae9090b85a36263d0adb6ecb9112ea923100a71ab21`, copy `.ufo/waves/round-43/c3/vllm-v0.31.0-release.json`); S481 — vLLM pull request 58552 — https://github.com/vllm-project/vllm/pull/58552 — §Purpose — opened 2026-10-25 (`gh api repos/vllm-project/vllm/pulls/58552`, merged 2026-09-27T17:48:55Z, 25514 bytes, SHA-256 `976ea2ea9d6230005eda35adc3b49cbf048fb4f7c37756c461b70a3781a314b9`, copy `.ufo/waves/round-43/c3/vllm-pr-58552.json`); S483 — vLLM `preload.py` at tag v0.31.0 — https://raw.githubusercontent.com/vllm-project/vllm/v0.31.0/vllm/entrypoints/cli/preload.py — §`_build_health_app` lines 70-77 — opened 2026-10-26 (raw re-fetched 2026-10-26, 12631 bytes, SHA-256 `d2704e80c08f49455c048724dce8d1eeb22bfa9bc97961ef567106425effa57d`, byte-identical to the committed copy `.ufo/waves/round-43/c3/vllm-v0.31.0-preload.py` and to the merged blob at `e7900156e130c9880eb03b7c1f2df32820e7a2be`, copy `.ufo/waves/round-44/w1/out/S9D2Row/vllm-v0.31.0-preload.py`)
```

Unified diff: `entry-source-line.diff`.

## Validation

`scripts/sources-census.sh validate --file <copy>` resolves every `used-by` path relative to
`dirname(file)/..` (`scripts/sources-census.sh:497-503`), so the copy must keep the lane's
directory shape or every `used-by` path in the file reports E11. Two runs, both pasted:

1. Lane-shaped copy (`$S/lane-copy/corpus/SOURCES.md`, lane's trees symlinked beside it) —
   candidate row inserted, **exit 0, 0 E**, output byte-identical to the same run on the
   pristine file (94 warning lines plus the `ok` trailer; `diff` clean):

```
exit 0 · 0 E · 94 W (93 W04, 1 W01 S481) · trailer `file\tok\t<copy path>` · output identical to the pristine run
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
file	W01	S481 tierC mined used-by=corpus/knowledge/runtime-health-surface-processes.md, corpus/lessons/round-43.md
```

2. Flat copy (`$S/SOURCES.candidate.md`, no lane trees beside it) — **exit 1**, 408 E11 lines
   (94 W plus 408 E = 502 lines) for pre-existing rows plus `E11 S483 missing used-by corpus/knowledge/runtime-health-surface-processes.md`;
   the S483 E11 is the same location artifact as S480/S481's, not a property of the row.
   Full output: `validate-flat-copy.out`.

`census` before → after: rows 222 → 223, tier.A 211 → 212, status.mined 203 → 204, queued 8,
rejected 11, missing 0, exit 0 both.

## What the row does not claim

- It does not say the route answers anywhere; no vLLM process was run (KQ4).
- It does not read v0.32.0 or `main`; `on-release` re-opens the tag file.
- It does not restate S481's three-state vocabulary as three wire outcomes — the code gives two.
- Registering S483 removes S481's status as sole support for the process sentence, but S481's
  `W01` line stays (it is tier C with a non-`—` `used-by`); clearing W01 would need a tier
  change, which this seat does not make.
