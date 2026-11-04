# SC03 search log — round-81 frontier step (2026-11-04)

**2026-11-04 — round-81 frontier step (four rows, one reject).** Question: which
first-party documents ground the round's four intended rows — (a) the corrected Ollama
OpenAI-compatibility locator behind R80V2, (b) the strict-ancestry test the late-acceptance
rule binds every late row with, (c) the NUL-delimited, rename-free record population the
frozen `tools/append-only-audit.py` parses, and (d) whether a vLLM v0.33.0 release note
belongs in this round at all? Where searched: the pinned raw documentation paths
`raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/` and
`raw.githubusercontent.com/git/git/v2.56.0/Documentation/` (including the include graph
`git-diff-tree.adoc` → `diff-options.adoc`), the GitHub release page, releases feed and
releases API of `vllm-project/vllm`, and the lane registry `corpus/SOURCES.md` for
duplicate-URL and duplicate-coverage collisions. Identified 8 URLs (2 Ollama, 3 git, 3
vLLM), screened all 8 by fetching them this round, included 3 as rows (S558, S559, S560)
with 1 control (the filed S557 locator, HTTP 404) and 1 quote source (the vLLM releases
feed, because the tag page is client-rendered), and excluded 1 candidate: S561 rejects the
vLLM v0.33.0 release note because no round-81 claim reads a vLLM behaviour, and because
the named URL carries no notes body — the repo has no release object tagged `v0.33.0`
(`releases/tags/v0.33.0` HTTP 404) and the notes named "v0.33.0" live on tag `v0.33.0rc3`.
Two further screened candidates were excluded as duplicate coverage rather than new rows:
the docs-site `git-scm.com/docs/git-merge-base` page is S175 (opened 2026-10-23, same
`--is-ancestor` semantics, different consumer list) and the docs-site
`git-scm.com/docs/git-rev-parse` page is S551. Stop rationale: each of the three included
rows has one governing first-party document that is byte-stable at a pinned tag and carries
line-addressable text for its claim, and every remaining candidate either duplicates a held
row or grounds no claim in the frozen plan, so further searching cannot change any row's
verdict this round.
