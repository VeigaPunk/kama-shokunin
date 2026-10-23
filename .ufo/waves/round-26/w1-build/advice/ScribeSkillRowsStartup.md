VERDICT: Drafted 15 startup-family rows and the requested scope paragraph; the artifacts are ready for L1 integration, but no integrated counter result is claimed while final source-row and registry IDs remain pending.

## Behavior

- `.ufo/waves/round-26/w1-build/out/ScribeSkillRowsStartup/rows.md` contains proposed IDs `E26-S01`–`E26-S15`: missing model, non-GGUF file, unknown CLI flag, eleven invalid-value/assertion triggers, and port already bound. Each row gives the exact source literal, trigger arguments, observed supervisor exit status, meaning and next action. The shared `exiting due to model loading error` phrase is described as the process-level result of the missing/non-GGUF rows, not duplicated as a second signature for those same triggers.
- `.ufo/waves/round-26/w1-build/out/ScribeSkillRowsStartup/header.md` is one paragraph covering build 11755 / commit 704366d, the SHA-pinned fixture, loopback `127.0.0.1`, the frozen count predicate, and the re-observe rule for another build.
- Style checked against `SKILL.md:167-191` (Historical error signatures) and `SKILL.md:193-244` (Checklist). The frozen predicate is `count-c1.py:4-29`; the target is preregistration `:14-17`.

## Execution evidence (peer artifacts; this seat ran no server)

These observations come from the executors' recorded runs, not from a launch by this scribe:

- Missing model: `out/ExecMissingModel/RUNS.txt:6-13` records two `timeout 40 ... -t 2` launches on ports 47632/47633; each exited 1 and printed `failed to open GGUF file`. The base `git grep` returned 1 (absent), the healthy baseline had zero matches, and help/version each exited 0 with zero matches (`RUNS.txt:15-27`). The corrected trigger includes `args=["-t","2"]` (`candidates.json:7`); its scratch counter result is `registered 1 counted 1 target 12 met False not-counted []`, counter exit 0 (`RUNS.txt:34-38`).
- Non-GGUF: `out/ExecJunkModel/RUNS.txt:13-17` records two `timeout 30 ... -t 2` launches on ports 47636/47637; each exited 1 with `invalid magic characters: 'this', expected 'GGUF'`. Base/help/version exclusions and fresh-source checks are recorded at `RUNS.txt:20-32`. The final isolated scratch counter result is `registered 1 counted 1 target 12 met False not-counted []`, exit 0 (`RUNS.txt:38-39`).
- CLI argument/value family: `out/ExecBadArgs/RUNS.txt:14-49` records two runs for each of 12 retained triggers: 11 exited 1; `--ctx-size -5` exited 134 / SIGABRT. After the thread-cap correction, every registry argument list begins with `-t`, `2`; the scratch archive counter returned `registered 12 counted 12 target 12 met True not-counted []`, exit 0 (`RUNS.txt:77-83`; receipt `out/ExecBadArgs/counter-receipt3.json:321-324`).
- Port already bound: `out/ExecPortInUse/RUNS.txt:14-31` records two launches on ports 47644/47645 after a process bound each loopback port; each llama-server exited 1. The final candidate arguments include `-t`,`2` (`RUNS.txt:64-71`); its isolated scratch counter returned `registered 1 counted 1 target 12 met False not-counted []`, exit 0 (`RUNS.txt:70-71`).

Those four scratch counts are separate candidate checks, not a combined or landed-tip count. Their scratch registry IDs and SOURCES rows do not establish the final lane registry. No build, test, final lane counter, port probe, or server launch was run by this scribe. No tool was installed.

## Source provenance and exact commands

I created `/fast/scratch/hyaku/kama-r26/KamaR26.ScribeSkillRowsStartup/` with `mkdir -p /fast/scratch/hyaku/kama-r26/KamaR26.ScribeSkillRowsStartup` (exit 0; no output), then fetched each requested source afresh from raw.githubusercontent.com at commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`. Each command below completed with exit 0; its output is the SHA-256 shown:

- `timeout 40 curl -fLsS 'https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/common.cpp' -o common.cpp && sha256sum common.cpp` → `d10ea1ff4253a1d6aedef3e73f16c3f2297975ca17254a82fac395aa2213ebd4 common.cpp`.
- `timeout 40 curl -fLsS 'https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/ggml/src/gguf.cpp' -o gguf.cpp && sha256sum gguf.cpp` → `7505d6a434dc740941a682fd3b476ef9bd9893ab76adf18c9969daa528bd5be5 gguf.cpp`.
- `timeout 40 curl -fLsS 'https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama.cpp' -o llama.cpp && sha256sum llama.cpp` → `8058a140d444b67bf64a1ce393d241dfd60080f4b117130c6f82e637e2109233 llama.cpp`.
- `timeout 40 curl -fLsS 'https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-model-loader.cpp' -o llama-model-loader.cpp && sha256sum llama-model-loader.cpp` → `7975d83406627e405d36876472495c6111696e70db66c65a629d6213ec54fc04 llama-model-loader.cpp`.
- `timeout 40 curl -fLsS 'https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp' -o arg.cpp && sha256sum arg.cpp` → `bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d arg.cpp`.
- `timeout 40 curl -fLsS 'https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp' -o server.cpp && sha256sum server.cpp` → `2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4 server.cpp`.
- `timeout 40 curl -fLsS 'https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-http.cpp' -o server-http.cpp && sha256sum server-http.cpp` → `24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb server-http.cpp`.
- For the separately reported `--ctx-size -5` assertion: `timeout 40 curl -fLsS 'https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp' -o llama-context.cpp && sha256sum llama-context.cpp` → `2a25e556cb0d16725e01ce853fb1b76da91dcb41b803ce1a6bacec89bfb94aa5 llama-context.cpp`.

I compared the seven requested lane snapshots with `sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/{common.cpp,gguf.cpp,llama.cpp,llama-model-loader.cpp,arg.cpp,server.cpp,server-http.cpp}` (exit 0). The seven output hashes, in the same order, were exactly the seven hashes above. The separate command `sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/sources/llama.cpp-704366d/llama-context.cpp` (exit 0) returned `2a25e556cb0d16725e01ce853fb1b76da91dcb41b803ce1a6bacec89bfb94aa5`, equal to the fresh fetch. These values also match `count-c1.py:59-73`. `rows.md` carries pinned-commit GitHub URLs with line anchors, access date 2026-10-23, and short located quotes for the selected source literals and exit paths.

## Conflicts and integration limits

The source-row draft IDs collide. The exact draft outputs are:

- ScribeSourcesContext: “VERDICT: Prepared 18 ordered source-row drafts and quote gates; this is source evidence, not live-reproduction evidence.” Its finding says: “The 18 requested rows exceed the specified ID range `S114–S129` by two. Drafts use provisional IDs `S114–S131` for the L1 to renumber.” Its `rows.md:19-20` assigns S130/S131 to `server-context.cpp`.
- ScribeSourcesStartup: `rows.md:5-14` assigns S130 to `common.cpp`, S131/S132 to `gguf.cpp`, and S133-S139 to other startup sources.
- The later L1 instruction relayed by ScribeSourcesStartup was: “do not renumber the source drafts; L1 assigns final S### IDs during integration across drafts. Leave my S130–S139 draft unchanged and do not hard-code these provisional IDs into the skill table; use placeholders until L1 integration.”

I followed that instruction: `rows.md` uses `S###` placeholders, not the conflicting provisional IDs. They must be replaced with final, unique IDs before a counter run. The table proposes `E26-S01`–`E26-S15`; current executor registries still contain `TBD` or `R26-C1-STARTUP-*` IDs, so L1 must make each registry ID match its SKILL-row ID. The `E26-S14` assertion cites a freshly fetched and hash-matched `llama-context.cpp`, but no assigned new SOURCES row for that file appears in the startup source draft; L1 must open one before that row can count. No `SKILL.md`, `corpus/SOURCES.md`, or registry file was changed by this seat.

## Touched surfaces and artifacts

Written by this seat:

- `.ufo/waves/round-26/w1-build/out/ScribeSkillRowsStartup/header.md`
- `.ufo/waves/round-26/w1-build/out/ScribeSkillRowsStartup/rows.md`
- `.ufo/waves/round-26/w1-build/advice/ScribeSkillRowsStartup.md` (this report)

Read-only evidence referenced: `.ufo/waves/round-26/preregistration.json`, `.ufo/waves/round-26/count-c1.py`, `SKILL.md`, the pinned source snapshot, and executor artifacts under `w1-build/out/{ExecMissingModel,ExecJunkModel,ExecBadArgs,ExecPortInUse}/`. The fresh source files are preserved under `/fast/scratch/hyaku/kama-r26/KamaR26.ScribeSkillRowsStartup/`. No product files, source registry rows, or canonical registry IDs were edited; no server processes were started by this seat.