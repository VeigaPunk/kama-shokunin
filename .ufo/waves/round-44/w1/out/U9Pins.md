# U9Pins — non-llama.cpp `on-release` pins: verdict

**Verdict:** 174 SOURCES.md rows are `on-release`; 93 name llama.cpp (91 are the C1 population, plus S026 and S038 outside it). The other ~81 pin 13 projects, plus own-work and sibling-lane rows. Of those, 3 are demonstrably changed (S010, S048, S019) and 1 is likely changed (S013, doc moved .md→.mdx). git, Go x/mod, sglang, ggml and pitest have no newer release. Dated 2026-10-26; every upstream query was a single `git ls-remote --tags --refs <repo>` or `gh api .../commits?path=` per file.

Deliverable: `pins.tsv` (columns project / pinned / newest / rows / changed?). Raw tag lists: `receipts/*.tags`.

## Rows a future release-recheck round would re-verify

| Priority | Rows | Why |
|---|---|---|
| Changed upstream, re-verify first | S010 (Ollama openai-compatibility.mdx, last commit 675150d = tip of v0.40.11, 2026-10-23, pin c173758); S048 (linux net/ipv6/tcp_ipv6.c, v7.2→v7.3, last file commit 2026-07-21 → 2026-09-15); S019 (OTel GenAI metrics, file last commit is HEAD 20259355 2026-10-26, pin 547934a 2026-10-18; repo has no tags) | file demonstrably touched after the pin |
| Likely changed | S013 (Ollama import: docs/import.mdx now exists, last commit 98acec4 2026-09-15; pin was docs/import.md 6d02a43); S022 (vLLM v0.25.0 per-request-metrics page; the file's last commit fbf2c5e is 2026-09-16, path guessed); S048's sibling S049 is NOT changed (file untouched since 2020) | needs a byte diff |
| New release exists, content unknown | Python series rows S044,S051,S061,S064,S065,S075,S076,S077,S087,S088,S095,S096,S097,S098,S105 (3.14.10 and 3.15.2 out); man7 rows S057,S066,S067,S078,S079 (man-pages 6.19→6.20); jj S072,S084 (installed 0.45.1→v0.46.0; docs "latest" floats); llm-d S040 (v0.10 page frozen, v1.0.0 out, S021 URL dead) ; pytest S052 (9.1.1, stable alias, page states no version) | pin is a floating URL or an old series, so a live re-read is the only check |
| Unpinned vLLM stable-doc pages | S002,S003,S004 | footer dates only, no commit; compare live pages |
| No newer release — recheck not due | git S032,S033,S070,S071,S073,S082,S083,S085,S089-S094,S099-S104,S174-S177,S475 (all v2.56.0, newest tag v2.56.0, no 2.57 rc); sglang S020 (v0.5.22 newest), S006/S007/S008 (file last commit == pin); vLLM S478 (v0.32.0 newest final), S005, S023 (file last commit == pin); Ollama S009, S025 (file untouched since before pin); ggml S014, S058; Go x/mod S069,S081 (v0.42.0 newest); pitest S063 | newest tag equals pin, or file last-commit equals pin |
| Exclude from a release round | S178,S179 (sibling lanes), S192 (OpenAI, unversioned), S193,S194 (own work), S021/S024/S026/S029/S053 (queued, rejected or dead) | not upstream release pins (S053 Automake: not queried; the savannah tag list returned no usable tags) |

## Per project: pinned vs newest

- vllm: v0.32.0 (S478) = newest final; v0.32.1rc0 is the only later tag. S002–S004 unpinned.
- sglang: v0.5.22 (S020) = newest.
- ollama: newest v0.40.11 (2026-10-23). S010 changed in that tip.
- ggml: pinned by commit (6af560d, da8e2a5), newest tag v0.27.0; file unchanged between them.
- git: pinned v2.56.0 = newest. `master` fsck.c moved 2026-10-08 (cbfd4cb) but that is not a release.
- linux: pinned v7.2, newest final v7.3 (tag 091b063; v7.3-rc* also listed).
- python: pinned 3.14.8/3.14.9 series URLs; newest 3.14.10 and 3.15.2.
- man-pages: 6.19 → 6.20.
- jj: 0.45.1 → v0.46.0.
- pytest: 9.1.1 newest; page unversioned.
- pitest: newest 1.30.1; S063's file unchanged since 2026-05-22.
- llm-d: v0.10 → v1.0.0.
- Go x/mod: v0.42.0 = newest.
- OTel semantic-conventions-genai: no tags.

## Caveats (not verified)

- "changed?" for docs rows rests on the GitHub last-commit-touching-path, not byte diffs. vLLM S002/S003/S022 source paths are guesses (the rows give none). Release dates for newest tags were not fetched (ls-remote gives none), except where the commits endpoint gave a date.
- A tag peeled (`--refs`) shows the tag object sha for annotated tags (e.g. linux v7.3 091b063), not the commit.
- Scratch removed. No tools installed, no lane files edited. Requests: 14 ls-remote, ~30 gh api commit queries (above the one-per-object suggestion for projects with several rows; one per row).

Paths written:
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/U9Pins/pins.tsv
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/U9Pins/receipts/*.tags
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/U9Pins.md
