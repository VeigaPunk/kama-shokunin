# U9Frontier report (round 48, w1)

**Verdict: nothing on the carried llama.cpp/Ollama frontier can change what the v5 receipts check. `tools/`, `common/` and `include/` are byte-identical b11906 → b11909 → b11912 (newest tag; b11911 was never tagged); the b11906 ledger's five src/ rows hold at b11912 by exact-block match; the S013 re-pin must be a new row, not an edit; the off-population llama.cpp rows are 14, not 10; and the v5 receipts still have no registry row.**

Full analysis, per-row read lists and ordered next-round plan: `.ufo/waves/round-48/w1/out/U9Frontier/frontier.md`. Evidence: `.../U9Frontier/evidence.txt`, `ranges.out`, `sweep.out` (+ `ranges.py`, `sweep.py`; they read scratch inputs deleted at the end).

## Evidence in brief
- Tags (bare blobless clone, `git rev-parse`): b11906 `4d71b42fd87d`, b11909 `caa8191df159f764fb0160e3d2fc6be008948aee`, b11910 `63b4b303bd87`, b11912 `961c376a2daa42220ec09663b9bde32c5fba1f70`; b11911 absent (`releases/tags/b11911` 404). `git diff --stat b11909 b11912` = 4 files (workflow, opencl, `src/llama-arch.cpp` +1, `src/llama-graph.cpp` 1 line, both laguna-gated); `-- tools common include ggml/include` empty at both steps. Server-file blobs equal b11909 = b11912 (server-context 9043fa2c, server-http cf147c7e, server.cpp b6ebf752).
- Ledger rows S107/S113/S130/S132/S135 (`registry/release-recheck-b11906.tsv`): every `release_lines` range except S113's 65-98 (constructor signature hunk) matches exactly at b11912 (e.g. S107 4132-4136→4133, S130 2642→2643, S113 1222-1234→1197); S113's cited statements inside 65-98 match at 85, 94-99, 137. Confirms and extends round-47 U2Server (`…/round-47/w1/out/U2Server.md`).
- v5 receipt statement sites at b11912: `server-context.cpp` 5503 (`owned_by`), 5609-5619 (health), 5625 (`/metrics`), `server-http.cpp` 308-330 (503 "Loading model"), `server.cpp` 318-325, 645-648, 671 (SIGTERM → `start_loop`). Only `build_info` changes per release.
- Round-47 U2Server finding 3b refined: the `704366d` permalinks in the receipts' `documented_by` are *correct for b11755* (I read 5288-5299, 314-325, 519-534 there); they document the old build, not a wrong span. Fix for a later tool version: add a second permalink at the receipt's own build commit (the tool builds URLs from `LLAMA_COMMIT`, `tools/kama-llamacpp-live.py:79-80`).
- S013: `docs/import.mdx` at 98acec40 (2026-09-15) is the only revision with "does not quantize" (line 35) and the wildcard sentence (43); 6d02a43a and three later revisions teach the `--quantize` flag. 98acec40 is still the newest commit for the file; main blob = 98acec40 blob `8a8778ce`; live `docs.ollama.com/import` and `/import.md` carry the sentences. `SOURCES.md:25` still cites 6d02a43a. In-place edit of the anchor cell breaks `tools/sources-append-only.py` (anchor is immutable); `tools/append-only-audit.py` v3 would not flag it (threshold 20 deleted lines). Append a new row (S494-class) and move `corpus/knowledge/gguf-runtime-compatibility-boundary.md` lines 2/22/63.
- Off-population: 14 llama.cpp rows at `380bcdff` (K1Pop's ten + S486, S487, S488, S489); population still exactly 91. S477 count above b11755: 115 (b11887), 130 (b11906), 133 (b11909), **135 (b11912)**; S026 `git grep v1/metrics b11912` exit 1.
- Not previously reported (new): no S-row names `round-48/c2/live` (v5 receipts); HF model pin `499bc882…` is still the head of `ggml-org/models-moved` (repo name is a rename risk; sha256 `270cba1b…` is the stable key); b11912 asset digest `344ea88c09666c1fb3eb5f7a649ada48ff753daaa660c7d7bc0b614cda49a078`.

## Not run
No counter, replay or live server was run by this seat. [INFERENCE] a b11912 live run would pass 11/11 (nothing the receipts touch changed); not executed. Tooling installed: none. Scratch removed.

Wrote:
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/U9Frontier.md
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/U9Frontier/frontier.md
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/U9Frontier/evidence.txt
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/U9Frontier/ranges.out
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/U9Frontier/sweep.out
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/U9Frontier/ranges.py
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/U9Frontier/sweep.py
