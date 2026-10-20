VERDICT: confirm — re-opened S038, S039, S040 and S017 (corpus/SOURCES.md:50,51,52,29) plus their round-16 Gate quotes and re-derived every cell from upstream on 2026-10-20; no cell is false and every recorded quote is verbatim at a findable location. Four wording/provenance defects remain (one Gate-location gap, one non-sequitur, one imprecise 200-URL, one category-label location); none changes a claim.

## What I ran (read-only; no server started)

| # | Command (cwd `/tmp/kama-r16-ReviewSourcesRowsB` unless noted) | Exit | Result |
|---|---|---|---|
| 1 | `git ls-remote https://github.com/ggml-org/llama.cpp 'refs/tags/b11755*'` | 0 | `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad refs/tags/b11755` (lightweight tag, no `^{}` line) |
| 2 | `curl -sS https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/b11755` | 0 (curl), HTTP 403 | `{"message":"API rate limit exceeded for 179.218.13.209. ...` |
| 3 | `curl -sS -L https://github.com/ggml-org/llama.cpp/releases/tag/b11755` | 0, HTTP 200 | 204850 bytes |
| 4 | `curl -sS https://github.com/ggml-org/llama.cpp/releases/expanded_assets/b11755` | 0, HTTP 200 | 150224 bytes |
| 5 | `curl -sS -r 0-0 -D - -o /dev/null -L https://github.com/ggml-org/llama.cpp/releases/download/b11755/llama-b11755-bin-ubuntu-x64.tar.gz` | 0 | `content-range: bytes 0-0/22240468` |
| 6 | `curl -sS 'https://huggingface.co/api/models/ggml-org/models-moved/tree/main/tinyllamas'` | 0, HTTP 200 | 2923 bytes |
| 7 | `curl -sS https://huggingface.co/api/models/ggml-org/models-moved` | 0, HTTP 200 | 2205 bytes |
| 8 | `curl -sS -X POST -d '{"paths":["tinyllamas/stories260K.gguf"]}' https://huggingface.co/api/models/ggml-org/models-moved/paths-info/main` (also at `22027b1ab988`, `96f460f9c1e2`, `e2d5caf55872`, `499bc8821c6b`, `688f41ddf8f3`, `11b0244f476d`, `fd8b140ebdb0`) | 0, HTTP 200 each | per-revision LFS oids (see S039) |
| 9 | `git ls-remote https://huggingface.co/ggml-org/models-moved refs/heads/main` | 0 | `499bc8821c6b12b4e53c5bffcb21ec206f212d81` |
| 10 | `curl -sS https://huggingface.co/ggml-org/models-moved/raw/main/README.md` | 0, HTTP 200 | 81 bytes |
| 11 | `curl -sS -L https://llm-d.ai/docs/0.10/operations/readiness-probes` | 0, HTTP 200 | 91290 bytes |
| 12 | `curl -sS -L https://llm-d.ai/docs/operations/readiness-probes` (S021 URL) | 0, HTTP 404 | 15222 bytes, final URL unchanged (no redirect) |
| 13 | `curl -sS -L https://llm-d.ai/docs/operations/lifecycle/readiness-probes` | 0, HTTP 200 | 92009 bytes |
| 14 | `curl -sS -o /dev/null -w '%{http_code}'` on `https://llm-d.ai/docs/1.0/operations/readiness-probes`; `https://llm-d.ai/docs` | 0 / 0 | 404 / 200 |
| 15 | `curl -sS https://llm-d.ai/sitemap.xml` | 0, HTTP 200 | readiness pages at `0.7`, `0.8`, `0.9`, `0.10`, `/docs/dev/operations/lifecycle/`, `/docs/operations/lifecycle/` |
| 16 | `curl -sS -L https://kubernetes.io/docs/concepts/workloads/pods/probes/` | 0, HTTP 200 | 544899 bytes |
| 17 | `curl -sS https://raw.githubusercontent.com/kubernetes/website/main/content/en/docs/concepts/workloads/pods/probes.md` | 0, HTTP 200 | 22548 bytes; line 70 quoted below |
| 18 | `curl -sS -L https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository`; `.../rest/releases/assets` | 0/0, HTTP 200 | quotes below |
| 19 | contract awk from `.ufo/waves/kaika/SOURCES-CONTRACT-v1.md` (malformed rows, kind/status/tier enums) | 0 | `malformed=0`; no enum lines printed |
| 20 | `pgrep -x llama-server` (lane root) | 1 | no process (I started none) |

Scratch `/tmp/kama-r16-ReviewSourcesRowsB/` removed after this report. No tool installed or upgraded.

## S038 — corpus/SOURCES.md:50 (release b11755 asset identity) — confirmed

| Cell | Claim | Evidence |
|---|---|---|
| tag → commit | `b11755` → `704366d76...` | #1 exact line; #3 also prints `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` twice |
| published | `2026-10-20T11:18:44Z` | #3 `github-actions</a> released this <relative-time ... datetime="2026-10-20T11:18:44Z">` |
| Pre-release | yes | #3 `<span ... class="Label Label--warning ...">Pre-release</span>` ×2 (desktop+mobile badge) |
| asset name | `llama-b11755-bin-ubuntu-x64.tar.gz` | #4 asset block `<a href="/ggml-org/llama.cpp/releases/download/b11755/llama-b11755-bin-ubuntu-x64.tar.gz"` |
| size | `22240468` | #5 `content-range: bytes 0-0/22240468`; #4 same block displays `21.2 MB` (= 22240468/1048576 = 21.21 MiB) |
| digest | `sha256:753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226` | #4 same asset block `<span ...>sha256:753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226</span>` |
| scope "Linux x64 CPU" | CPU build | #3 release body asset legend literally lists `Ubuntu x64 (CPU)`; the family list contains separate `ubuntu-cuda-*`, `ubuntu-rocm-*`, `ubuntu-vulkan-*` assets (#4) |
| kind/tier/status/recheck | `docs`/`A`/`mined`/`on-release` | contract enums (#19); used-by file exists (`corpus/knowledge/llamacpp-loading-lifecycle.md`) |
| asset-record URL | API path valid | #2 returns rate-limit JSON, not 404 — resource exists; content claim is unaffected |

## S039 — corpus/SOURCES.md:51 (pinned GGUF identity) — confirmed

| Cell | Claim | Evidence |
|---|---|---|
| repo commit | `499bc8821c6b12b4e53c5bffcb21ec206f212d81` | #7 `"sha": "499bc8821c6b12b4e53c5bffcb21ec206f212d81"`; #9 head ref identical |
| file commit | `96f460f9c1e2ca43d0adc1c682b832525a2c0ea3` | #8 `paths-info/main` → `"lastCommit": {"id": "96f460f9c1e2ca43d0adc1c682b832525a2c0ea3", "title": "gguf : bump training context from 256 to 2048", "date": "2025-10-28T08:55:08.000Z"}` |
| size | `1185376` | #6 and #8 `"size": 1185376` for `tinyllamas/stories260K.gguf` |
| LFS sha256 | `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` | #6/#8 `"lfs": {"oid": "270cba1...", "size": 1185376, "pointerSize": 132}` |
| no license declared | yes | #7 `"tags":["gguf","endpoints_compatible","region:us"]`, `"cardData": null`; #10 README is 81 bytes: `Various models to be used in llama.cpp CI workflow.` / `Do not use it in production.` — no license line |
| three byte strings on 2025-10-28 | 3 distinct | #8 per revision: pre-day `688f41dd` = `047bf464...`; `22027b1` (08:07) = `68c694e7...`; `96f460f` (08:55) = `270cba...`; `e2d5caf` (09:18) and `499bc88` (10:43) = `270cba...` again → 3 distinct oids that day |
| kind | `dataset` | contract enum includes `dataset` (#19); first use of the value in this file |
| teaches | digest, not path, identifies | follows from the three-oid row above |

Note: the HF `commits/main?path=...` filter is **not** a change-set oracle — it lists four commits for that path on 2025-10-28 while two of them (`e2d5caf`, `499bc88`) leave the LFS oid at `270cba...`. Counting commits would yield 4; counting byte strings yields 3, as the row states.

## S040 — corpus/SOURCES.md:52 (llm-d v0.10 page, S021 404) — confirmed

| Cell | Claim | Evidence |
|---|---|---|
| v0.10 page | rendered "Version: v0.10" | #11 text `Readiness Probes Version: v0.10`; banner `This is documentation for llm-d v0.10, which is no longer actively maintained. ... latest version (v1.0 (latest)).` |
| sections | Problem Statement / `/health` Endpoint / `/v1/models` Endpoint / Probe Lifecycle | #11 all four headings present; the third renders as `"/v1/models Endpoint (OpenAI-Compatible)"` |
| quote | verbatim | #11 `<p>The vLLM <code>/health</code> endpoint only indicates that the server process is running, <strong>not</strong> that models are loaded and ready to serve.</p>` (21 words, §Problem Statement). Same string on the v1.0 page (#13) |
| S021 URL 404 | yes | #12 HTTP 404, 15222 bytes, no redirect |
| "after the v1.0 docs cutover" | directionally correct | #13 `/docs/operations/lifecycle/readiness-probes` → 200, `Version: v1.0 (latest)`, same `/health` sentence; #15 sitemap shows the v1.0 page lives under `operations/lifecycle/`. The 404 is a path change in the v1.0 tree, not a withdrawn page |
| supersedes | rule 2 format | teaches opens `supersedes S021 —`; contract rule 2 requires exactly that (#19) |
| kind/tier/status/used-by | `docs`/`A`/`mined`/file exists | #19; `corpus/knowledge/llamacpp-loading-lifecycle.md` exists |

## S017 — corpus/SOURCES.md:29 (Kubernetes probe vocabulary) — confirmed

| Cell | Claim | Evidence |
|---|---|---|
| page modified | `2026-06-30` | #16 `Last modified June 30, 2026 at 3:26 PM PST` |
| §Types of probe | present | #16 heading and `Types of probe The kubelet can optionally perform and react to three kinds of probes ...` |
| §Caution under Liveness probe | present | #16 `Caution: Liveness probes can be a powerful way to recover from application failures, but they should be used with caution.` (inside the liveness section) |
| teaches: lifecycle split | supported | `Readiness probes determine when a container is ready to accept traffic.` and `Liveness probes determine when to restart a container.` (#17 lines 70 and 44) |
| teaches: bad liveness → cascading restarts | paraphrase, grounded | #17 lines 61-62 `Incorrect implementation of liveness probes can lead to cascading failures. This results in restarting of container under high load` |
| Gate quote | exact at probes.md:70 | #17 line 70 matches lesson `corpus/lessons/round-16.md:47` verbatim (11 words) |
| status/opened/recheck/used-by | `mined`/`2026-10-19`/`90d`/two existing files | `SOURCES.md:113-115` records the used-by append; both paths exist |

## Findings (ordered by severity; all advisory, none invalidates a row)

1. **Medium-low — S040's Gate quote has no location.** `corpus/lessons/round-16.md:47` records it as `S040 (vLLM-only) "The vLLM ... serve."` — the cell names the row, not a page section/line, while the contract rule 1 requires the Gate to record "a <=25-word quote with its location grounding `teaches`" (`/home/vgpnk/Projects/shokunin/.ufo/waves/kaika/SOURCES-CONTRACT-v1.md`, Rules §1). Rounds 14 and 15 used a separate `### Opened source(s)` paragraph with URL + access date + quote + word count (`corpus/lessons/round-14.md:23`, `round-15.md:23`); round 16's Gate has no per-row URLs or word counts for S035-S041. Fix: append `§Problem Statement` (or `§/health Endpoint`) to the S040 clause, and name the five URLs somewhere in the Gate.
2. **Low — S038 `teaches` conflates two properties.** `"the release is mutable (Pre-release)"` reads as a causal claim. GitHub documents pre-release as a production-readiness flag: "to notify users that the release is not ready for production and may be unstable, select This is a pre-release" (#18). Mutability is separate (immutable releases are opt-in: "you cannot move or delete its tag while the release exists" — #18). The advice "cite the digest, not the tag alone" stands; reword the reason to "no immutability guarantee is recorded".
3. **Low — `corpus/SOURCES.md:109-110` says "v0.10 and v1.0 versioned pages → 200".** There is no versioned v1.0 route: `https://llm-d.ai/docs/1.0/operations/readiness-probes` is 404 (#14). The 200 page is the unversioned latest URL `https://llm-d.ai/docs/operations/lifecycle/readiness-probes` (#13), i.e. the page *moved under `lifecycle/`* in the v1.0 tree. A reader reconstructing the check from that sentence will get a 404 and conclude the erratum is false. Fix: name the URL.
4. **Informational — S038/S039 Gate "locations" are category labels.** "S038 asset record" and "S039 model card" identify the artifact type but not a section/line; the quotes are findable (the asset object in the release API/HTML; README line 1) but not pinned. Same rule-1 gap as finding 1, lower stakes because both quotes are one-field artifacts.
5. **Informational — S021 stays `queued` with a dead URL.** Deliberate and documented (`SOURCES.md:115` "S021's cells stay as written (status `queued`)"), consistent with rule 2's append-only constraint. No action; flagging so the round report does not read the 404 as an unhandled stale row.

Nothing else: every number, hash, date, section, enum and used-by path in the four rows re-derives from a primary record; the row-shape and enum check is clean.

## Limitations

- GitHub REST was rate-limited (403, #2), so I could not re-read `published_at`, `prerelease: true`, or the asset object's `digest` field **from the API**. The values are independently present in the release HTML (#3), the expanded-assets HTML (#4), and an HTTP range response (#5). [INFERENCE] that the HTML's `<relative-time datetime>` is the API's `published_at`; that the API's `digest` is the field documented in the assets reference (its response example shows `"digest": "sha256:2151...")`.
- [INFERENCE] "GitHub-computed": the digest is GitHub's server-side asset record (it is displayed by GitHub and served by the REST assets schema); I did not find a docs sentence calling it "computed by GitHub". The digest value itself is not inferred — it matches the row byte for byte.
- `probes.md:70` is verified at current `kubernetes/website` main, not at a commit pinned to the page's 2026-06-30 build date. The page text matches; S017's anchor uses the dated page, which the contract permits ("version, commit, or publication date").
- [INFERENCE] the knowledge entry's parenthetical "readiness (withhold traffic, **keep running**)" — the page states traffic withholding and liveness restarts but never says "keep running" literally; the inference is sound (readiness failure only removes the Pod IP from EndpointSlices).
- No live llama.cpp run was performed for this seat; S041 and the installed-tree correspondence are other seats' items. `pgrep -x llama-server` → exit 1. Ports 8080/34113 were never contacted.
