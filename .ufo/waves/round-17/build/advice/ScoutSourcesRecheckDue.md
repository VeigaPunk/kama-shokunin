VERDICT: partial — the registry has no absolute-date or `on change` recheck cells; 4 `every round` rows are due at round 17 and 7 llama.cpp `on-release` rows had their trigger fire, but only S001's anchored file moved.

# Scout: SOURCES.md recheck-due frontier (round 17, 2026-10-20)

Read-only parse of `corpus/SOURCES.md` at lane tip `cff9e62`. 41 data rows, header at `corpus/SOURCES.md:12`.

## 1. Recheck vocabulary actually present

| token | rows | ids |
|---|---|---|
| `on-release` | 29 | S001–S010, S013–S015, S019–S026, S029, S032, S033, S035–S038, S040 |
| `90d` | 8 | S011, S012, S016, S017, S018, S027, S028, S031 |
| `every round` | 4 | S030, S034, S039, S041 |

- Zero rows carry an absolute date in `recheck`; the literal predicate "date is on/before 2026-10-20" matches no row [observed by full-table parse].
- Zero rows carry `on change` or `on-change` in the `recheck` cell (`grep -c` = 0 for exact cells). The phrase exists only in knowledge prose, e.g. `corpus/knowledge/ollama-evidence-replay.md:3`: "on-change — the `--tags/--ps/--expect/--selftest` flags". So the question's second predicate has no registry representation; `on-release` is the event-driven equivalent.

## 2. Due now: `every round` (4 rows)

| id | recheck | status | round-17 recheck result |
|---|---|---|---|
| S030 (`:42`) | every round | rejected | Source drift: anchor records "probe md5 1f81e859c2d7f43f87d1f7e01327b2cf"; that md5 is the probe at `35e9175`, while current `tools/kama-probe.sh` md5 is `e8bfdcac…` (changed in `726f737`, 2026-10-20). Evidence `.ufo/round-10/gates/check.json` is unchanged (md5 `060009f9…`, sampled 2026-10-19T21:35:49Z). Anchor pointer stale; teaches still historical. |
| S034 (`:46`) | every round | mined | Accurate. Frozen baseline `fda61e00…` equals `git show 6e348e2:.ufo/waves/round-14/measure.py`; quoted predicate still present at frozen lines 356–358: "if unique < MINIMUM_UNIQUE_CASES:". `declared` is still built and never counted. |
| S039 (`:51`) | every round | mined | Accurate. HF repo sha `499bc882…` and `lastModified 2025-10-28T10:43:38Z` unchanged; resolve header `x-linked-etag: "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"`, `x-linked-size: 1185376` — matches the row's "LFS sha256 270cba1bd510…d256d". |
| S041 (`:53`) | every round | mined | Accurate as a round-16 sample: `.ufo/waves/round-16/live/receipt.json` still has schema `kama-llamacpp-live/v1`, port 37527, 10 checks, `teardown.returncode 0`, `sigterm_sent true`, `sigkill_sent false`, tool sha256 `b8c5e8d4…`. [INFERENCE] C2 will supersede it with a v2 receipt this round; no cell change should be made until that receipt exists. |

## 3. llama.cpp `on-release` rows — trigger fired (7 rows)

New release after the pinned b11755: b11756, `published 2026-10-20T13:48:11Z`, prerelease true (`gh api repos/ggml-org/llama.cpp/releases/tags/b11756`). Tags also exist for b11756 (`d8061939…`) and b11757 (`13786fbb…`) via `git ls-remote`. Compare `704366d76...13786fbb` = `ahead_by=2` with exactly 3 changed files: `ggml/src/ggml-cuda/common.cuh`, `ggml/src/ggml-cuda/ggml-cuda.cu`, `tools/server/server-chat.cpp`. No file anchored by these rows is in the delta.

| id | recheck | status | round-17 recheck result |
|---|---|---|---|
| S001 (`:13`) | on-release | mined | README moved: hash `ad0dbc02…` at the cited file commit `c0fd786` and at master `4c3c5810`, versus `714c067b…` at current master `1ba568c5`/b11755–b11757. Diff is 2 hunks only (`@@ -208,6 +208,8 @@` adds "`--connect` | (experimental) open a peer-to-peer tunnel"; `@@ -235,7 +237,7 @@` changes `--reasoning-preserve` default). Anchored `/health`, `/v1/models`, `/metrics` text is untouched, so "`/health` is a load-state surface (503 loading, 200 loaded)" still holds; the commit pin is stale relative to master. |
| S015 (`:27`) | on-release | mined | No content change: `tools/quantize/README.md` hashes `4dcc340a…` at pinned `ad1b88ca`, at b11757, and at master. "Conversion to GGUF and quantization are separate offline phases" remains. |
| S026 (`:38`) | on-release | rejected | No flip: PR #18001 still open — release page state marker `title="Status: Open"`, page JSON `"state":"OPEN"`, title "server: add /v1/metrics endpoint". Rejection stands. |
| S035 (`:47`) | on-release | mined | Byte-identical: pinned "raw file sha256 714c067b…b75a6a37" also at b11757 and master. |
| S036 (`:48`) | on-release | mined | Byte-identical: `server-http.cpp` `24ede172…` at both `704366d76` and b11757. Claim "Every non-frontend path, `/v1/models` and `/health` included, answers 503" has no source change. |
| S037 (`:49`) | on-release | mined | Byte-identical: `server.cpp` `21439622…` at both revisions. "single-model listener answers before the model loads" has no source change. |
| S038 (`:50`) | on-release | mined | Identity verified exactly: API record gives `published 2026-10-20T11:18:44Z`, `prerelease true`, asset `llama-b11755-bin-ubuntu-x64.tar.gz` size 22240468, digest `sha256:753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226`; downloaded bytes hash to the same value. |

Release-state caveat: b11757's `/releases/tag/b11757` page returns 200 with no assets and no "Pre-release" marker, while `releases/tags/b11757` and the releases list (top 10) omit/404 it. Treat b11756 as the newest API-visible release and b11757 as a tag-only/source pin until the release object settles. Also, the releases Atom `<updated>` is an edit time, not `published_at` (b11755: atom 11:22:04Z vs published 11:18:44Z); use the API/HTML timestamp.

## 4. `on-release` rows not triggered

- SGLang: latest v0.5.22, feed updated 2026-10-19T05:55:53Z. Pinned docs are byte-identical at v0.5.22: S006 `native_api.mdx` `209087c3…`, S007 `production_metrics.mdx` `a05a6569…`, S008 `quantization.mdx` `5a441ede…`.
- vLLM: latest v0.32.1rc0, 2026-10-18T09:26:56Z. S005 pinned quantization README `d8ada8aa…` is identical at v0.32.0.
- Ollama: latest v0.40.7, 2026-10-18T00:28:57Z; all Ollama rows opened 2026-10-19/20.
- ggml spec S014: `docs/gguf.md` hash `1dead27b…` identical at pinned `6af560d5` and master.
- OTel S019: `gen-ai-metrics.md` hash `bf2359b8…` identical at pinned `547934a` and main.
- Git S032/S033: latest tag found is v2.56.0 (`git ls-remote --tags`, no 2.57); rows opened 2026-10-20, so no release after open.
- llm-d S040: v1.0.0 release exists (feed 2026-10-20T02:30:17Z), but S040 pins the versioned v0.10 URL (HTTP 200) and its own text already records the v1.0 cutover; S021's URL still returns 404 exactly as S040 states.

## 5. `90d` rows — not due

S011 (`:23`), S012 (`:24`), S016 (`:28`), S017 (`:29`), S018 (`:30`), S027 (`:39`), S028 (`:40`) opened 2026-10-19 → due 2027-01-17; S031 (`:43`) opened 2026-10-20 → due 2027-01-18. None is on/before 2026-10-20.

## Limitations

- GitHub REST was rate-limited unauthenticated (core 60/60 used); release facts above come from authenticated `gh api`, `git ls-remote`, raw.githubusercontent, and HTML pages.
- b11757 release-object state is inconsistent between HTML (200) and API (404/omitted); no claim is made beyond the tag's existence and file bytes.
- git-scm.com returned 403 to scripted fetches, so S032/S033 page-version markers were not re-read; only the Git tag ceiling was checked.
- No lane gate, `measure.py`, `mutants.py`, or `controls.py` was run; no servers were started; no ports bound. Scratch artifacts only in `/tmp`.
- [INFERENCE] marks: S041's future v2 supersession, and that omitted release rows imply no change because no release event exists.
- Installs/updates: none.
