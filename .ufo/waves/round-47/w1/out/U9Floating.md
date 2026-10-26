# U9Floating report (round 47, freshness)

**Verdict: all twelve carried rows' teaches still hold today and at b11909 (llama.cpp rows re-read at `caa8191d`); the one defect is S013's citation, still unrepaired at lane HEAD `46a924e0` — re-pin to ollama `98acec40ae2b3ed361fc5117e5b2ae81a4bf5c18` (`docs/import.mdx`, blob `8a8778ce…`, equal to `main` today); `S013-repin.diff` passes `git apply --check --unidiff-zero -p1`.**

Table (quote ≤25 words, URL, access time per row): `.ufo/waves/round-47/w1/out/U9Floating/rows.md`.

## Rows
- S013: live page, `main` and `98acec40` all say "Ollama does not quantize GGUF models during import."; pinned `6d02a43a` teaches `-q/--quantize` and has no `docs/import.md`. Newest commit on the file is `98acec40` (2026-09-15). Defect remains in SOURCES.md:25 and `corpus/knowledge/gguf-runtime-compatibility-boundary.md:22`.
- S022: holds (v0.25.0 page footer July 7 2026; v0.32.0 = stable page, Sept 16 2026, same fields, adds Responses API and spec-decode sections). vLLM latest release v0.32.0 (2026-10-18).
- S026 holds: PR #18001 still open, head `aec7bdb4`; `git grep 'v1/metrics' caa8191d` exit 1 (positive control passes).
- S028 holds (dated): closed 2024-02-18 by PR #5548; `/health` documented at `tools/server/README.md:479`.
- S038, S482, S484 hold: tags, publish times, prerelease flags, asset sizes and digests unchanged (`gh api`, ls-remote, 2026-10-26T21:29Z).
- S477 holds as a dated sample; today 134 bN tags above b11755, newest **b11910**; `engine-pin-watch.md:51-54` still stale (K1Pop F2 unfixed).
- S485/S041/S046/S055 hold at b11909: `tools/server/` byte-identical b11906..b11909; b11889..b11909 touches only the mtmd plumbing in `server-context.cpp` (+9/-6), a comment in `server-models.cpp` and `tests/utils.py`. Handler lines at b11909: `server-context.cpp:5618` health body, `:5625` metrics-off error, `server-common.cpp:119` 501, `server-http.cpp:319` loading envelope, `:5503` owned_by. The L1's three b11909 receipts agree (11/11 each; 503 counts 18/34/29, all exact; returncode 0, no SIGKILL). I did not run a llama-server.

## Evidence
Commands: `curl -sL` on live pages (all 200); `gh api` pulls/18001, issues/4746 (+events/timeline), pulls/5548, releases/tags/{b11755,b11889,b11909}, ollama commits?path=docs/import.mdx, vllm releases/latest; `git clone --filter=blob:none --bare` of llama.cpp, `git grep`, `git diff --numstat`, `git rev-list --count`, `git ls-remote --tags`. Saved in the out dir: `release-*.json`, `S013-*`, `S022-*`, `S026-pr18001.json`, `S028-issue4746.json`, `ls-remote-4.txt`, `ls-remote-all.txt`, `b11909-excerpts.txt`.

## Side findings
- b11910 tag exists past the b11909 release under test (`63b4b303bd87456adc2f09d56c7e1f74e9e26673`); no release record read for it.
- No b11909 SOURCES row exists at HEAD (expected at integration, per the assignment).

No tools installed. Lane, fleet repo untouched; scratch `/fast/scratch/hyaku/kama-r47/U9Floating` removed.

## Paths written
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/U9Floating.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/U9Floating/rows.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/U9Floating/S013-repin.diff
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/U9Floating/ (evidence copies listed above)
