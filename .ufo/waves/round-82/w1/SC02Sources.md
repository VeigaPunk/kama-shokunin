# SC02Sources — round-82 scribe report (SOURCES rows)

Seat: SC02Sources, leaf scribe, kama round 82 wave 1. Date 2026-11-04.
Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`, read at tip
`bacae0726d7c53455bd083bc6d478bbcd6e7fffc` (`git -C … rev-parse master`, exit 0). The sealed
revision and the base revision were read from the frozen plan and not used for writes. The lane tip
had moved again by the end of the seat (`384ef1d5bcbf737183571398ecb0955ea5074609` at 10:14 local,
not read by this seat); every read above is at `bacae072` and remains reproducible from `curl.txt`.

## Behavior

1. Read the frozen plan `plans/round-82-claims.md` in full before touching the registry; treated its
   blockquote predicates, fact tokens, target lines and controls as read-only text.
2. Read the registry (`corpus/SOURCES.md`), the round lesson `corpus/lessons/round-82.md` §Gate, the
   knowledge entry `corpus/knowledge/pin-recheck-trigger.md`, `registry/engine-pins.tsv`,
   `registry/engine-pin-relations.tsv`, `tools/pin-watch.py` and the round-80 tag receipt. All reads
   were read-only; no production file was written or proposed as an edit.
3. Fetched every candidate URL myself (no inherited quote, no cached page): 10 curl fetches
   (4 row sources, 4 comparison/verification fetches, 2 excluded or same-class pages) plus 6
   auxiliary calls (3 GitHub API JSON endpoints, 2 `releases/latest` redirect checks, 1 read-only
   `git ls-remote --tags`). Each fetch's HTTP status, bytes, sha256 and anchor line is in `curl.txt`.
4. Drafted four SOURCES rows in the exact contract-v1 11-column shape, one row per line, no `|` in any
   cell: S563 (llama.cpp b12103, mined), S564 (llama.cpp b11755, mined, with one located sameness and
   one located difference against S563), S565 (SGLang native_api v0.5.23, mined, 17-word located
   quote), S566 (llama.cpp b12103 release note, rejected with reason and flip).
5. Wrote the bounded search log: question, where, date, identified/screened/included/excluded, stop
   rationale — with the one 404 recorded as excluded, never guessed.

Everything the rows assert was located in bytes this seat fetched; the only reused text is the
frozen plan's own target wording, which is not a source row.

## Gates and receipts

- Table shape validator (`python3`, inline): 4 rows, each 11 data cells and 12 pipes, no empty cell;
  S565 quote = 17 words (limit 25). Exit 0.
- `sha256sum` over my own `curl` output: S563 `eafc1b53…a137` (136429 bytes, 2620 lines), S564
  `714c067b…6a37` (119661 bytes, 2402 lines), S565 native_api `3ed17118…7a3c` (18295 bytes, 471
  lines), S566 release page `e71c6e36…ac86` (174444 bytes, 203 rendered lines). Exit 0.
- `diff -u` S564→S563: exit 1 (differences found), 15 hunks; the health heading is unchanged context
  and the anchored sentence is byte-identical. `diff -u` SGLang v0.5.22→v0.5.23 native_api: exit 1,
  health hunk `@@ -108,6 +108,8 @@` adding exactly the `/ready` and `/ping` bullets.
- Release-page text extraction (`python3`, strip script/style/tags): 203 rendered lines; `/health`,
  `/v1/models` and `GET /` each 0 occurrences. Exit 0.
- Read-only git used only: `rev-parse master`, `log --oneline`, `show --stat 962bd251`,
  `log -S… -- corpus/SOURCES.md`, `status --porcelain`. No `git add`, commit, checkout, stash, switch,
  reset, pull; no jj; no scratch clone was needed.
- No tool install or upgrade was required; nothing was written to `~/.local/bin` or any PATH
  directory; no pacman transaction was attempted.
- No subagent dispatched (leaf); no `agent://all` message.
- Scratch root `/fast/scratch/hyaku/kama-r82/SC02Sources` created, used for all downloads and
  comparison diffs, and deleted before yield (`rm -rf`); only hashes/anchors were copied into the
  seat dir. The scratch tree is gone (verified absent after deletion).

## Touched surfaces

Written (only these):
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/SC02Sources/sources-rows.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/SC02Sources/curl.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/SC02Sources/search-log.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/SC02Sources.md` (this report)

Read-only (no edits): `plans/round-82-claims.md`, `corpus/SOURCES.md`,
`corpus/lessons/round-82.md`, `corpus/knowledge/pin-recheck-trigger.md`,
`registry/engine-pins.tsv`, `registry/engine-pin-relations.tsv`, `tools/pin-watch.py`,
`.ufo/waves/round-80/measured/after/c2-tags/llama.cpp.txt`. The lane worktree showed a deleted
`.ufo/waves/round-82/w1.ready.partial` and an untracked `w1.ready.dispatched` in
`git status --porcelain`; neither change is mine.

## Findings

1. **Id collision — the dispatch's S563–S566 ids were partly consumed before this seat read.**
   Commit `962bd251` (round-82 record commit, `show --stat`: `corpus/SOURCES.md | 3 +`) filed S563
   (llama.cpp b12103, mined), S564 (llama.cpp b11755, mined) and S565 (SGLang README v0.5.23,
   rejected). The registry table therefore holds 305 rows, not the dispatch's 302; next free id is
   S566. My S563/S564 rows independently reproduce the filed rows cell-for-cell on hashes, byte
   counts, line counts and anchor lines (480/482, 479/481) — nothing to file. My S565 (mined SGLang
   native_api) and S566 (rejected llama.cpp release note) are **not** in the registry. Recommended
   append-only filing: keep filed S563/S564/S565, file the mined native_api row at **S566** and the
   rejected release-note row at **S567**, and add those two rows to the lesson §Gate table. Filing
   them under the dispatch's S565/S566 ids would require superseding the already-cited rejected
   README row — not recommended.

2. **The register's `newest` cell moved during the round, and the held statement did not.**
   `releases/latest` for llama.cpp resolves to `v0.9.0` (published 2026-11-04T13:08:06Z); build
   releases b12109 (12:33:27Z) and b12110 (12:52:04Z) already existed at my first fetch (13:07:36Z);
   `git ls-remote --tags` shows newest build tag **b12110**, commit `cd959bae99ff`, the same commit
   as tag v0.9.0. Build tags above b11755 are now 280 (register records 278; b12104–b12108 do not
   exist). The README is byte-identical at b12103, b12110 and v0.9.0 — sha256 `eafc1b53…a137`,
   136429 bytes, 2620 lines, quote at line 482 — so the newer release is a trigger whose verdict is
   `holds`, not drift. This is the round's own thesis observed live.

3. **SGLang's newest tag adds two health surfaces the pin does not have.** `native_api.mdx` at
   v0.5.23 (§Health Check, line 108) lists `/health`, `/health_generate`, `/ready` and `/ping`; the
   `/ready` and `/ping` bullets (lines 111–112) are absent at the lane's pin v0.5.22 (diff hunk
   `@@ -108,6 +108,8 @@`). The two held lines are byte-identical. This is knowledge-entry material for
   the L1 (`S006`/`S007` cite the older doc); I did not edit `corpus/knowledge/`.

4. **`corpus/knowledge/pin-recheck-trigger.md` overstates the tag gap** (report-only; not my file).
   Its sentence "The release gap of 348 tags" is the build-*number* delta (12103 − 11755). The
   register's `newer=278` and the receipt's own count of build tags strictly above b11755 are both
   278, because build numbers are skipped (b12104–b12108 missing). `tools/pin-watch.py` counts with
   `b(\d+)` keys (`sum(1 for k in tags.values() if k > key)`), which matches 278, not 348.

5. **vLLM newest-tag probe has no path at v0.33.0.** `docs/serving/online_serving.md` returns HTTP
   404 (14 bytes). Excluded rather than guessed, so this seat produced three llama.cpp/SGLang rows
   and no vLLM row; a vLLM row needs the tag's real docs path first.

6. **The filed S565 rejection is corroborated on my own fetch.** SGLang `README.md` at v0.5.23:
   9472 bytes, sha256 `a7654a48…303c`, 120 lines, zero occurrences of `/health`, `/v1/models`,
   `health` or `served`. It cannot ground a check of the pinned SGLang document.

7. **Release notes are not uniformly route-free.** The SGLang v0.5.23 release page mentions
   `/health_generate` once ("rust-server: Attach configured metadata headers to a healthy
   /health_generate"), so a blanket "release notes never name a route" rule would be false. The
   rejected row (S566) is scoped to the llama.cpp b12103 page, whose rendered text has zero route
   occurrences; the SGLang page is recorded in `curl.txt` as the same rejection class but not filed.

## Out of scope (deliberately not done)

- No edit to `corpus/SOURCES.md`, `corpus/lessons/round-82.md`, `corpus/knowledge/*`, `registry/*`,
  `tools/*`, `SCORECARD.md`, `LOG.md`, `SKILL.md` or any other production file.
- No commit, `git add`, checkout/stash/reset/pull in the lane; no jj mutation; no scratch clone
  (read-only `git ls-remote` only, against the public upstream).
- No `pre-report-gate.py`, C1/C2 counter run, build, lint, test or scored-mode instrument; the L1
  owns filing, grading and the gate. No platform-service restart, no pacman, no installs.
- Did not re-open the vLLM docs by guessing a path; the 404 is the finding, not a prompt to search
  the whole repository tree (bounded search stop).
- Did not touch `/home/vgpnk/Projects/shokunin` fleet-root files, `.ufo/state/`,
  `.ufo/watchdog.log`, `.scratch/`, `l0-questions.md`, a sibling repo or `shokuknow`.

## Artifact paths

- Draft rows: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/SC02Sources/sources-rows.md`
- Fetch receipts: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/SC02Sources/curl.txt`
- Search log: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/SC02Sources/search-log.md`
- This report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/SC02Sources.md`

Known limits: sha256 values bind the bytes served by `raw.githubusercontent.com` /
`github.com` at the recorded times; upstream tags can move after 2026-11-04 13:12Z, which finding 2
already demonstrates. The two filed rows I reproduced (S563/S564) are cited from the registry, not
from a lesson I authored; my re-derivation is the evidence, and no claim here upgrades a filed row
into a scored one.
