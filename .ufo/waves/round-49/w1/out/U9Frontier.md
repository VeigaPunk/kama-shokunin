# U9Frontier report (round 49, w1)

Verdict: the b11906 ledger population needs a next-round read of 2 files / 5 rows only (S107 S130 S132 S113 S135, all text-equal with renumbered lines, same at b11912); S013's pin is worse than round 46 said (the cited `6d02a43a` mdx teaches that Ollama quantizes, the row's text first appears at `98acec40`, 2026-09-15); the ten off-population llama.cpp rows are now 14 plus one new in-rule row (S494, population 92), and nothing the C1 witness checks can change before a re-frozen binary digest.

Full detail, line maps and URLs: `.ufo/waves/round-49/w1/out/U9Frontier/frontier.md`.

Findings that add to what the lane already knows:
1. S013 (`corpus/SOURCES.md:25`) and `corpus/knowledge/gguf-runtime-compatibility-boundary.md:22` cite `docs/import.md` at `6d02a43a` (2025-10-28). At that commit the file is `docs/import.mdx` and lines 111-128 say "Ollama can quantize FP16 and FP32 based models ... `ollama create --quantize q4_K_M`"; the strings "does not quantize GGUF models during import" and "wildcard" are absent there and at `948f69330acf` (`imp-*.mdx`, `s013-revisions.out`). First revision carrying the row's text: `98acec40ae2b3ed361fc5117e5b2ae81a4bf5c18` (blob `8a8778ce...` = `main` today, lines 35 and 43). Fix: re-anchor both places to that commit and date 2026-09-15.
2. Population rule now selects 92 rows at lane HEAD 122c4ee9: S494 is the 92nd (`raw.githubusercontent.com/.../caa8191d.../tools/server/README.md`, on-release, mined). Its README blob `8e27e37b8d4a` is identical at b11906, b11909, b11912; the lane copy `.ufo/waves/round-49/c1/server-README-caa8191d.md` equals `git show b11909:tools/server/README.md`.
3. S477 count: 135 bN tags above b11755 today (highest b11912), row says 115.
4. Off-population family: S486-S489 (binary and receipt rows for b11906, b11909) join the ten; two rows per replayed build, none reopened by any population rule.
5. Witness: `/tokenize` and `/detokenize` handlers are text-identical at b11755, b11909, b11912; `src/llama-vocab.cpp`, `common/`, `tools/server` trees identical b11906..b11912. Only the binary digest differs by release (b11912 asset `sha256:344ea88c...`). Assets for b11755, b11889, b11906, b11909, b11912 and the HF model URL all answer 200 today; all recent releases are `prerelease: true`, b11889/b11909 `immutable: false`. The counter has no `<0xNN>` case (`tools/round49-replay-witness-audit.py:280-281`), but every nonce-alphabet character is a plain vocab token of stories260K, so no defect for the frozen model.

Not run: no llama-server, no replay, no b11912 live receipt (statements "hold at b11912" are source reading plus tree identity). Tools installed: none. Scratch `/fast/scratch/hyaku/kama-r49/U9Frontier` removed after copying receipts. One-request-per-object GitHub API use: releases list, releases/tags/b11889, ollama contents x5, commits x3.

Wrote:
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/U9Frontier.md
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/U9Frontier/frontier.md
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/U9Frontier/rng.py
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/U9Frontier/rng.out
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/U9Frontier/tree-ids.out
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/U9Frontier/tokenize-handler.out
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/U9Frontier/asset-retention.out
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/U9Frontier/s013-revisions.out
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/U9Frontier/imp-6d02a43a75cd3364b3c230e9070f1413e60f0d02.mdx
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/U9Frontier/imp-948f.mdx
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/U9Frontier/imp-98acec40ae2b3ed361fc5117e5b2ae81a4bf5c18.mdx
