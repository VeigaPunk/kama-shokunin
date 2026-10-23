ATTACK E26-15 (`failed to open GGUF file`, S128 = gguf.cpp:1021): partial

The signature reproduces, is the fault's own error-level text, and its source pin is correct. The "next action" cell and the trigger wording are too narrow: the same line is printed for any GGUF file llama-server fails to open (draft model, mmproj, split shard), and for errors other than a missing file (for example `Permission denied`). Severity: medium (the diagnosis can be wrong), no counter impact.

Seat: KamaR26.AttackE2615, port block 47756-47759. Access date 2026-10-23.

## Fixture pins (observed)

`sha256sum ~/.local/bin/llama-server ~/.cache/kama-shokunin/models/stories260K.gguf`:
- `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804  llama-server`, which equals count-c1.py `SERVER_SHA256`.
- `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d  stories260K.gguf`, which equals `MODEL_SHA256`.
- `sha256sum .ufo/waves/round-26/count-c1.py` = `6501737c...c796588`, which matches the frozen value.

## (1) Re-run of the registered trigger: holds

Registry entry (`registry/error-signatures-r26.json:383-395`): channel `startup`, args `["-t","2"]`, model `missing`, occupy_port false, source S128 gguf.cpp.

Before the runs, `ss -ltn | rg ':4775[6-9]'` returned exit 1 (all ports free). Command, run twice:
`timeout 40 ~/.local/bin/llama-server -m /nonexistent/kama-r26/missing.gguf --host 127.0.0.1 --port $P -t 2 </dev/null`

| run | port | exit | signature line |
|---|---|---|---|
| 1 | 47756 | 1 | `run1.log:5` and `:9`: `E gguf_init_from_file: failed to open GGUF file '/nonexistent/kama-r26/missing.gguf' (No such file or directory)` |
| 2 | 47757 | 1 | `run2.log:5` and `:9` (same text) |

Both logs end with `E srv  llama_server: exiting due to model loading error`, and both runs exited within 0.02 s. The signature appears twice per run: first from the memory-fit pass (`common_fit_params: encountered an error ...`, line 8) and then from the real load (`common_init_: failed to load model`, line 12). Raw logs: `out/AttackE2615/run1.log`, `run2.log`.

## (2) Fault's own text, not F1/F2/F3: holds

- It is not a warning. The line is logged at level `E` by `gguf_init_from_file`, the function the row names. The only `W` line in the log is the unrelated API-key/CORS warning at `run1.log:3`, which does not contain the signature.
- It does not come from an unrelated path. The line is produced by the `-m` open failure itself, and both occurrences carry the `-m` path.
- It is not echoed from the trigger (F2/F3). There is no HTTP request. The only trigger bytes are the argv, and the extra argv is `-t 2` plus the path `/nonexistent/kama-r26/missing.gguf`. Neither contains `failed to open GGUF file`. No argument file is used.
- Cross-check against the registry: no other registered signature (E26-01..17) occurs in `run1.log`. Only E26-15's own signature does (python scan over `signatures[]`).

## (3) Pinned source and the "meaning (code)" cell: holds (one gap)

I fetched fresh copies with `curl -fsSL https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/<path>`, all with exit 0. Each sha256 equals the lane snapshot and the count-c1.py pin:
- gguf.cpp `7505d6a4...bd5be5`
- llama-model-loader.cpp `7975d834...fc04`
- server.cpp `21439622...aef4`
- common.cpp `d10ea1ff...ebd4`
- llama.cpp `8058a140...9233`
- server-context.cpp `dd1de0f2...c2329`

The fetched gguf.cpp, lines 1017-1022:
- 1017: `struct gguf_context * gguf_init_from_file(const char * fname, struct gguf_init_params params) {`
- 1018: `FILE * file = ggml_fopen(fname, "rb");`
- 1020: `if (!file) {` (the guard)
- 1021: `GGML_LOG_ERROR("%s: failed to open GGUF file '%s' (%s)\n", __func__, fname, strerror(errno));`
- 1022: `return nullptr;`

The cell's citation `gguf.cpp:1017-1022` and "logs the path and the system error" are correct.

Gap: the cell says "the process exits", but it cites no code for the exit, and the trigger column claims "exit 1". The exit comes from `server.cpp:507-511` (`if (!ctx_server.load_model(params)) { ... SRV_ERR("%s", "exiting due to model loading error\n"); return 1; }`), reached through `llama-model-loader.cpp:571-574` (`metadata == nullptr` → `throw ... failed to load model from`). The exit status is observed, so this is low severity.
- Smallest correction: append `; server.cpp:507-511 returns 1` to the meaning cell.

## (4) The "next action" cell: partial (overreach)

The cell says: "Fix the `-m` path or the mount; the system error at the end of the line (for example `No such file or directory`) names the cause. Not a model-format problem."

- "Not a model-format problem" holds, because the guard fires at `fopen` before any byte is read.
- "the system error ... names the cause" holds (`strerror(errno)`).
- "Fix the `-m` path" overreaches. `gguf_init_from_file` is also called for other files: mmproj (`clip.cpp:1232`), split shards (`llama-model-loader.cpp:631`, where the `-m` file exists but a sibling shard is missing), and `common_get_gguf_info` (`common.cpp:1210`). I ran three extra live tests on my block, one server at a time:

| test | command extra | exit | signature |
|---|---|---|---|
| missing draft model | `-m <fixture> -md /nonexistent/kama-r26/draft-missing.gguf`, port 47758 | 1 | `draft.log:4,6,14`: `failed to open GGUF file '/nonexistent/kama-r26/draft-missing.gguf' (No such file or directory)` |
| missing mmproj | `-m <fixture> --mmproj /nonexistent/kama-r26/mmproj-missing.gguf`, port 47759 | 1 | `mmproj.log:5,12`: same signature with the mmproj path |
| unreadable model | `-m <scratch>/noperm.gguf` (mode 000), port 47758 | 1 | `eacces.log:5,9`: `failed to open GGUF file '...noperm.gguf' (Permission denied)` |

So with a valid `-m`, the line can still come from `-md` or `--mmproj`, and it can mean a permissions problem rather than a wrong path. A reader who follows the cell would check the wrong flag.
- Smallest correction for the next-action cell: "Fix the file named in quotes. It may be the `-m` model, a `-md` draft, an `--mmproj` projector or a split shard. The system error in parentheses names the cause (`No such file or directory`: path or mount; `Permission denied`: file permissions). Not a model-format problem."
- Optionally, change the trigger cell to "startup with a GGUF path (here `-m`) that cannot be opened → exit 1".

This does not change the count. The registered trigger is unchanged, and none of the alternate triggers matches another registered row.

## (5) SOURCES row S128 and the lesson Gate quote: holds (one low note)

- `corpus/SOURCES.md:140`: the URL `.../704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/ggml/src/gguf.cpp#L1021` points at the emitting line. The anchor `gguf.cpp line 1021 @ 704366d...; sha256 7505d6a434dc740941a682fd3b476ef9bd9893ab76adf18c9969daa528bd5be5` equals the fresh-fetch sha256. Kind `code`, tier A, and scope "at commit 704366d76 only" are consistent.
- Teaches cell: it repeats the meaning cell, including "the process exits". gguf.cpp alone does not teach the exit (that is server.cpp:507-511). This is low severity.
  - Smallest correction: replace "model loading fails and the process exits" with "returns nullptr (`gguf.cpp:1022`)", or add the server.cpp citation as in (3).
- Lesson Gate `corpus/lessons/round-26.md:41`: the URL and access date 2026-10-23 match. The quote `line 1021: GGML_LOG_ERROR("%s: failed to open GGUF file '%s' (%s)\n", __func__, fname, strerror(errno));` matches the fresh line 1021 byte for byte (apart from indentation) and is 11 words, within the 25-word limit.

## Process hygiene

- All five of my servers exited by themselves with status 1; none was left listening. `ss -ltn | rg ':4775[6-9]'` after the runs returned exit 1 (no listeners).
- `pgrep -af llama-server` at the end showed only pid 1435447 (`--port 47720 --embeddings -t 2`, started about 20 s before the check). That port and those args are outside my block and none of my commands started it, so I left it alone.
- I did not run the frozen counter. My seat does not need it, and the trigger was run directly as specified.
- Tools installed or updated: none.

## Files written

- `.ufo/waves/round-26/w2-falsify/advice/AttackE2615.md` (this report)
- `.ufo/waves/round-26/w2-falsify/out/AttackE2615/run1.log`, `run2.log`, `draft.log`, `mmproj.log`, `eacces.log`
- Scratch: `/fast/scratch/hyaku/kama-r26w2/AttackE2615/` (same logs, `noperm.gguf`, and `fetch/` with the fresh source files)
