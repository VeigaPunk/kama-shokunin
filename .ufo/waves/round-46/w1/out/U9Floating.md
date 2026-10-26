# U9Floating report (round 46, freshness)

Verdict: S002, S003, S004, S022 teaches hold today; S013 teaches holds on the live page but the cited revision (6d02a43) contradicts it - citation defect, proposed pin 98acec40ae2b3ed361fc5117e5b2ae81a4bf5c18 (docs/import.mdx, 2026-09-15).

Full table with quotes, URLs, access times: .ufo/waves/round-46/w1/out/U9Floating/rows.md

Evidence: curl -sL on each URL (all HTTP 200, 2026-10-26T19:58-19:59Z); `gh api repos/ollama/ollama/contents/docs/import.mdx?ref=<sha>` for 6d02a43a, 98acec40 and main (blob 8a8778ce for both 98acec40 and main); `gh api repos/ollama/ollama/commits?path=docs/import.md[x]`; `gh api repos/vllm-project/vllm/releases/latest` -> v0.32.0 2026-10-18. Footer dates match the rows (S002 Oct 8, S003/S004 Oct 17, S022 Jul 7 2026). `docs/import.md` returns 404 at 6d02a43a (renamed to .mdx in that commit).
Side finding: S022 stable-alias page now dated Sept 16 2026 adds Responses API and spec-decode acceptance sections; non-contradicting.
No tools installed. Scratch removed.
