# W1C06 claims — draft B: which process owns vLLM's shipped `/health` (round 43, C3)

Scope: the two frozen objects only — `.ufo/waves/round-43/c3/vllm-v0.31.0-release.json`
(placeholder row **S480**, release page, docs/A) and `.../vllm-pr-58552.json`
(placeholder row **S481**, pull request, community/tier C). Verdicts: **verified** = the
exact string or field was found in the named object at the named place on 2026-10-25;
**falsified** = the claimed string or reading is not there; **not covered** = out of this
entry's evidence. Every quote below was tested by whitespace-normalised substring
containment against the committed copy, not against staged prose.

## A. The release page (S480)

| # | claim | anchor in the copy | verbatim fragment | words | check | verdict |
|---|---|---|---|---|---|---|
| A1 | v0.31.0 lists a `/health` endpoint, tagged #58552, among the Fast restart features | `body` §Highlights, body line 8 | "a `/health` endpoint (#58552) and a readiness wait (#58370)" | 9 | substring of `body` | verified |
| A2 | the same item is restated in a second section | `body` §Engine Core, body line 66 | "readiness wait (#58370), `/health` (#58552)" | 5 | substring of `body` | verified |
| A3 | the release frames the endpoint under the preload feature, not under the inference server | `body` §Highlights, line 8 | "**Fast restart**: the new `vllm preload` CLI launches the weight-cache daemon" | 11 | substring of `body` | verified |
| A4 | the release never names the inference server in either `/health` mention | both occurrences of `/health` in `body` (2) | — | — | enclosing sentence of each occurrence read | verified (scope: this body only) |
| A5 | the release spells the process **weight-cache daemon** (hyphen); the unhyphenated "weight cache daemon" occurs 0 times | `body` | — | — | `count("weight-cache daemon")` = 1, `count("weight cache daemon")` = 0 | verified |
| A6 | release is tag `v0.31.0`, published 2026-10-05T06:44:55Z | top-level `tag_name`, `published_at` | — | — | fields read from the copy | verified |
| A7 | `/ready` occurs 0 times in the release body | `body` | — | — | `count("/ready")` = 0 | verified (absence in this page only) |

## B. The pull request (S481)

| # | claim | anchor in the copy | verbatim fragment | words | check | verdict |
|---|---|---|---|---|---|---|
| B1 | the change adds an HTTP `/health` endpoint to the weight cache daemon **parent** process | `body` §Purpose | "Add an HTTP `/health` endpoint to the weight cache daemon parent process." | 12 | substring of `body` | verified |
| B2 | the description names three states | `body` §Purpose | "The endpoint reports `starting` while daemon ranks are loading, `ready` after all expected target and draft ranks are available, and `failed` if a daemon process exits." | 26 | substring of `body` | verified (as description; see C4) |
| B3 | the stated purpose is to separate startup from readiness | `body` §Purpose | "This allows external service management systems to distinguish daemon startup from readiness." | 12 | substring of `body` | verified |
| B4 | the pull request is merged | top-level `state`, `merged`, `merged_at`, `merge_commit_sha` | — | — | closed / true / 2026-09-27T17:48:55Z / e7900156e130c9880eb03b7c1f2df32820e7a2be | verified |
| B5 | it is stacked on another pull request | `body` §Purpose | "Stacked on #58370." | 3 | substring of `body` | verified |
| B6 | title | top-level `title` | "[Fast Start] Add `/health` endpoint for the weight cache daemon" | 10 | field read | verified |
| B7 | `/ready` occurs 0 times in the PR body | `body` | — | — | `count("/ready")` = 0 | verified (absence in this page only) |
| B8 | the PR body spells it unhyphenated: "weight cache daemon" 1x, "weight-cache daemon" 0x | `body` | — | — | counts | verified |

## C. The pull request's commit list and merged file (read by `gh api`, 2026-10-25)

| # | claim | anchor | evidence | verdict |
|---|---|---|---|---|
| C1 | a commit titled "[Fast Start] Move daemon health endpoint to preload CLI" is in this pull request | `gh api repos/vllm-project/vllm/pulls/58552/commits` | sha `ff54ad893015a13e869a9c51b8f30f44dfbb8ef7`, committer date 2026-09-27T07:56:50Z | verified |
| C2 | that commit is what puts the endpoint into the preload CLI module | `gh api repos/vllm-project/vllm/commits/ff54ad893015` | files: `vllm/entrypoints/cli/preload.py` (+87/-0), `tests/model_executor/model_loader/test_weight_cache.py` (+19/-0) | verified |
| C3 | the commit is the pull request's **first**, not a follow-on: list is `ff54ad89` 07:56:50Z then `087ebc20` "Merge branch 'main' into vllm-daemon-health" 16:40:56Z | same commits endpoint, ordered | two commits, dates in order | verified (falsifies "follow-on", C8) |
| C4 | at the merge commit the route returns two HTTP codes, not three states | `gh api 'repos/vllm-project/vllm/contents/vllm/entrypoints/cli/preload.py?ref=e7900156…'` | `@app.get("/health", include_in_schema=False)` → `Response(status_code=200 if state.is_ready else 503)`, no body | verified |
| C5 | no state name ships: `failed` 0x; `starting` 1x and only inside "restarting" in the module docstring | same file | grep counts: `failed`=0, `starting`=1, `restarting`=1 | verified |
| C6 | the endpoint is off unless the operator sets a port | same file | `--weight-cache-health-port`, help "Port for the parent /health endpoint; disabled by default.", `if args.weight_cache_health_port is not None` gates `_start_health_server` | verified |
| C7 | a dead rank is folded into not-ready, and a startup death ends the supervisor | same file | `is_ready` = `ready and not any(proc.exitcode is not None …)`; on `queue.Empty` with dead ranks: log, terminate, `sys.exit(...)` | verified |
| C8 | the module belongs to a different process than the engines it serves | same file, docstring | "Launches one weight cache daemon per GPU"; "Engines then load from the daemons with:" a `vllm serve` command carrying `--load-format ipc_cache` | verified |

## D. Falsifiers on the staged package (read-only, `/home/vgpnk/Projects/shokuknow/merge/kama/`)

These are findings for the L1, not edits: staged rows must not be copied verbatim.

| # | staged location | staged text | finding | proposed fix |
|---|---|---|---|---|
| D1 | `SOURCES.append.md:107` (S430) | quote "a /health endpoint ( #58552 ) and a readiness wait ( #58370 )" | **falsified as a quotation**: neither half occurs in the release body (actual: "a \`/health\` endpoint (#58552) and a readiness wait (#58370)") — spaces inside the parentheses and stripped backticks make it a re-rendering | quote the two exact fragments, or mark the elision |
| D2 | `SOURCES.append.md:107` (S430) | second quote "readiness wait ( #58370 ), /health ( #58552 )" | **falsified**: not a substring of the body (§Engine Core reads "readiness wait (#58370), \`/health\` (#58552)") | same |
| D3 | `SOURCES.append.md:108` (S431) | title quote "[Fast Start] Add /health endpoint for the weight cache daemon - # 58552" | **falsified**: actual title is "[Fast Start] Add \`/health\` endpoint for the weight cache daemon" | use the top-level `title` field verbatim |
| D4 | `SOURCES.append.md:118` (S441) | source cell ends "saved copy: lanes/kama/round13/evidence/text/vllm_pr_58552.html.txt" | provenance defect of the kind round 42 rejected for S424: campaign-repo-relative path, outside the lane (file exists in shokuknow, 152138 bytes, 2026-10-24 17:34) | anchor on the lane copy `.ufo/waves/round-43/c3/vllm-pr-58552.json` (sha256 below) |
| D5 | `...amendment-2026-10-24-r12.md:30` | "That three-way split is the liveness-versus-readiness distinction … It is real, it is shipped" | **true of the description, false of the merged route**: C4/C5 show 200/503 and no state name, so a client cannot separate `failed` from `starting` | say the description names three states and the merged route reports two codes |
| D6 | `...amendment-2026-10-24-r13.md:50` | "carries a follow-on commit titled "Move daemon health endpoint to preload CLI" … it moved from the daemon to the preload CLI" | commit is real (C1) but is the PR's **first** commit and adds +87/-0, so "follow-on" and "moved" overstate what this PR's history shows | "the commit that carries the endpoint into `vllm/entrypoints/cli/preload.py`" |
| D7 | r13 `source:` line (S441), dated opened 2026-10-24 | staged read date | not a defect; but the lane row must carry `opened 2026-10-25`. The committed copies were fetched 2026-10-26T01:46:17Z UTC, which is 2026-10-25T22:46:17-03 on this host — the lane's date is the local date | keep `opened 2026-10-25` |
| D8 | `...amendment-2026-10-24-r12.md:20` | "Both belong to `vllm preload`" | supported by the release item's own frame (A3), but it is the release's grouping, not a statement that the daemon ranks and the CLI are one process | keep, scoped to "the release's Fast restart item" |

## E. Handoff obligations for the L1 (what this seat deliberately did not do)

- **Ids.** Draft B uses placeholders **S480** (release) and **S481** (PR). Registry at HEAD `1af8d516` holds 220 rows, highest `S479`, so both are free today. The counter's `entry` leg requires the entry's `source:` line to name the ids it finds as *new rows by URL*, so entry and rows must be renumbered together in one step.
- **Anchors (sha256 of the committed copy bytes).** release `20c282d566d6788b0913bae9090b85a36263d0adb6ecb9112ea923100a71ab21`; pull request `976ea2ea9d6230005eda35adc3b49cbf048fb4f7c37756c461b70a3781a314b9`. The PR object is volatile: a 2026-10-25 re-fetch matched `body`/`title` but differed in `.base.repo.open_issues` (9432 vs 9433), `.base.repo.open_issues_count` and `.base.repo.size` (328195 vs 328276); the release object re-fetched byte-identical. Any re-fetch changes the PR bytes, so recompute the anchor from whatever copy is finally committed.
- **Lesson Gate quotes (<= 25 words, must occur in the copy).** S480: "a `/health` endpoint (#58552)" (4 words). S481: "Add an HTTP `/health` endpoint to the weight cache daemon parent process." (12) or "distinguish daemon startup from readiness" (5). The full three-state sentence is 26 words and would fail the gate cap.
- **Counter legs outside this seat.** `corpus/README.md` line naming the entry; `corpus/lessons/round-43.md` §Gate + §Assimilation set; `.ufo/waves/round-43/assimilation/{reg-ids,staged-ids,collisions,quarantine-slice,guard/}`; the six registry cells `kind/tier/status/opened/recheck/used-by`.
- **One open decision.** Entry lines 33-52 (commit-list and merged-file paragraphs) cite `gh api` reads for which no copy is committed. Either commit one (e.g. `.ufo/waves/round-43/c3/vllm-merge-e7900156-preload.py`, sha256 of the fetched bytes) and extend S481's anchor cell, or drop those paragraphs. The frozen counter does not need them; the finding does.
- **Base coverage precondition, checked.** `git -C /fast/scratch/kama-r43/clone grep -n -i -E 'weight cache daemon|weight-cache daemon|vllm preload' 6897ead5… -- '*.md' ':!.ufo/'` → exit 1, no matches; the entry path is absent at base and at HEAD.

## F. Not verified here

Pull requests #58370, #46811 and #59179 (referenced, not opened); the inference server's live docs page (S004 read from the lane's registry cell, not re-fetched); the release page as rendered HTML (only the JSON API object); daemon-rank internals beyond the merged `preload.py`.
