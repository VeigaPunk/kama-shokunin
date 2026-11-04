# Search log — SC02Sources, round 82 (2026-11-04)

**Question.** The round's frontier step opens the pinned documents behind the `pin-watch` `behind`
relations: which newest-tag documents ground a recheck of the health surface the lane probes, for
llama.cpp (pin b11755), SGLang (pin v0.5.22) and vLLM (pin v0.32.0)?

**Where.** `raw.githubusercontent.com` at named tags (the same raw-file form the lane already uses in
S001/S006/S015/S561), GitHub release/tag pages, and the GitHub REST API (`releases`, `tags`,
`git/ref/tags`) for tag identity and publication times. Nothing was searched on the open web; no
search engine and no local mirror were used.

**Date.** 2026-11-04, 13:07–13:10 UTC (10:07–10:10 local -0300). Every fetch is receipted with HTTP
status, bytes and sha256 in `curl.txt`.

**Identified (7 URLs).**
1. `llama.cpp/tools/server/README.md` at b12103 (newest tag the relation register names).
2. The same file at the lane's pin b11755.
3. `sglang/docs/docs/basic_usage/native_api.mdx` at v0.5.23 (SGLang's newest tag).
4. The same file at the lane's SGLang pin v0.5.22 (comparison side).
5. `llama.cpp/releases/tag/b12103` (build-release note).
6. `sglang/releases/tag/v0.5.23` (release note).
7. `vllm/docs/serving/online_serving.md` at v0.33.0 (vLLM's newest tag).

The assignment's four candidates also named vLLM as the alternative to SGLang for S565; SGLang was
chosen because the page states the health surface directly and sits on the exact `behind` relation
(v0.5.22 → v0.5.23), so the newest-tag and pin-tag sides could be compared like with like.

**Screened (7).** All seven were fetched; none was described from memory.

**Included (4 rows).**
- S563 — llama.cpp b12103 README, mined, anchor line 480/482.
- S564 — llama.cpp b11755 README, mined, anchor line 479/481, with one located sameness and one
  located difference against S563.
- S565 — SGLang native_api v0.5.23, mined, anchor line 108/111, quote line 111 (17 words).
- S566 — llama.cpp b12103 release note, rejected, with reason and flip.

**Excluded (3 fetches, no row).**
- vLLM `docs/serving/online_serving.md` at v0.33.0: HTTP 404, 14 bytes — the path does not exist at
  that tag. Excluded rather than guessed; a vLLM newest-tag row would need the tag's real docs path.
- SGLang v0.5.22 native_api: comparison evidence for the S565 diff only (the pin side, already
  covered by the lane's S006/S007 docs rows), not a separate row.
- SGLang v0.5.23 release note: same rejection class as S566 (a release note names a change — here a
  rust-server metadata-header bullet that mentions `/health_generate` once — not the surface's
  semantics), so only one release-note row was filed and the second is recorded here.

Also fetched but not a row: llama.cpp `v0.9.0` README and `b12110` README (both byte-identical to
b12103, establishing that the stable release and the then-newest build tag carry the same anchored
sentence), the SGLang v0.5.23 `README.md` (verification of the already-filed S565 rejection), and
three GitHub API JSON endpoints plus two `releases/latest` redirect checks for tag identity and
publication times.

**Stop rationale.** Each of the three pinned engines now has either a newest-tag document read and
anchored (llama.cpp, SGLang) or a recorded 404 that blocks the read (vLLM). The four rows the
dispatch bounds this seat to are covered; another URL could add a fifth engine's page but could not
change the verdicts of S563–S566, because both sides of the llama.cpp comparison and the SGLang
pin/newest pair are already located byte-for-byte.
