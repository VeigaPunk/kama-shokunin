VERDICT: partial — S035–S041 (corpus/SOURCES.md:47-53) and the round-16 Gate (corpus/lessons/round-16.md:36-58), checked against /home/vgpnk/Projects/shokunin/CORPUS.md §SOURCES.md v1 (lines 64-147)

Seat: KamaR16.CriticSourceRows (critic, falsify wave). Read-only on the lane. The only things I wrote are this Report and scratch files under /tmp/kama-r16-CriticSourceRows/, which I deleted at the end. I did not start llama-server. I did not run measure.py.

## Axes

The v1 shape checks, tier/scope, anchor and digest fidelity, append-only and supersede, mined status against used-by, Gate quote location and the 25-word limit, Gate grounding of `teaches`, and search-log arithmetic.

## What holds (confirm)

1. **v1 mechanical checks.** I ran the CORPUS.md:135-147 commands in the lane root, all exit 0. Results: rows `41`, malformed `0`, tiers `A=38 C=3`, status `mined=31 queued=5 rejected=5`. The duplicate, enum/tier-inflation and missing-used-by checks printed nothing. The kinds of S035–S041 are docs/code/code/docs/dataset/docs/own-work. All are allowed values and none is `community`.
2. **Pinned digests and lines.** `sha256sum` over `.ufo/waves/round-16/sources/llama.cpp-704366d/*` matches the row anchors: README `714c067b…6a37` = S035, server-http.cpp `24ede172…5fdb` = S036, server.cpp `21439622…aef4` = S037. The cited lines check out by `sed -n` / `grep -n`:
   - README:486 is the body and :487 the explanation.
   - README:1258 is the `meta` sentence.
   - server-http.cpp:309-311 is the frontend exemption, :312 the quoted comment, :318-320 the body, :354 the state gate and :357 the API-key check.
   - server.cpp:460 is the router `is_ready.store(true)`, :493 the quoted comment and :515 the single-model `is_ready.store(true)`.
3. **S038.** The API returned 403 (rate limit), so I checked the HTML instead. `curl …/releases/tag/b11755` returned 200: the page contains "Pre-release", commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` and datetime `2026-10-20T11:18:44Z`. `…/releases/expanded_assets/b11755` returned 200 and shows `sha256:753bfa73…e226` for `llama-b11755-bin-ubuntu-x64.tar.gz` (21.2 MB). The tarball-to-install tie is in SentinelInstallChain.md:22, where the local sha256 equals the API digest.
4. **S039.** HF `paths-info/main` gives size 1185376, LFS oid `270cba1b…256d`, last commit `96f460f9…`; the repo sha is `499bc882…`. The model card says "Various models to be used in llama.cpp CI workflow." `cardData` is null and there is no license tag, so "no license declared" holds. I also checked the claim "three different byte strings on 2025-10-28" with paths-info at each revision:
   - 11b0244 `047bf46455a5`
   - 22027b1 `68c694e7584c`
   - 96f460f `270cba1bd510`

   It is true, and all three have the same size, 1185376. That supports the teaches point that only the digest identifies the file, and shows the size in the anchor does not.
5. **S040 supersedes S021.**
   - The S021 URL returns 404, and `/docs/0.10/operations/readiness-probes` returns 200, rendered "Version: v0.10".
   - The quoted sentence is on the page under §Problem Statement.
   - S040's teaches cell opens with the string `supersedes S021 —`, as rule 2 requires.
   - `git diff 20e392e HEAD -- corpus/SOURCES.md` changes only one existing line (S017 used-by, logged old→new at round-16.md:54-58). The rest is new rows S035–S041 plus appended prose. S021 is unchanged and still `queued`.
6. **S041 as own-work, tier A.** This fits CORPUS.md:94-95 ("the lane's own re-runnable gate output"). It also fits the round-10 D-1 ruling (round-10.md:152): lane-own local runs are in-province, and the documentation-only rule targets external live targets. The scope is narrowed to one sampled instant on an unregistered port. The receipt is tracked (`git ls-files`). It matches the anchor: schema `kama-llamacpp-live/v1`, 13:49:38.040Z–.170Z, port 32845, 10 checks all passed. It pins the probe sha256 `6edd3c4c…fa50`, which equals the current `tools/kama-probe.sh`. Checks 0, 1, 2, 3, 5 and 6 ground every teaches clause.
7. **mined status and used-by.** Every used-by path exists and cites its row (`grep -rlw S0NN corpus registry SKILL.md README.md`).
8. **Every Gate quote is located and within 25 words.** I matched each one in the pinned or fetched source and counted words with `str.split`:

   | Gate row | Quote (location) | Words |
   |---|---|---|
   | S036 | server-http.cpp:312 | 13 |
   | S036 | server-http.cpp:318 | 3 |
   | S037 | server.cpp:493 | 15 |
   | (not a row) | server-context.cpp:5396 | 3 |
   | (not a row) | server-models.cpp:2585 | 7 |
   | S035 | README:1258 | 14 |
   | S035 | README:487 | 7 |
   | S017 | probes.md:70 (kubernetes/website main) | 11 |
   | S040 | §Problem Statement | 21 |
   | S038 | digest | 2 |
   | S039 | model card | 9 |
   | S041 | receipt observed object | 6 |

## Defects and counterexamples

| # | Rule / axis | Counterexample + evidence | Smallest safe correction |
|---|---|---|---|
| D1 | Rule 1: the Gate must record the URL for every new row (CORPUS.md:112-114) | The round-16 Gate table has no URLs, only S-ids, and one blanket date (round-16.md:38). Round 15's Gate did record one: "S012 https://docs.ollama.com/api/ps opened by L1 on 2026-10-20" (round-15.md:23). | Append a Gate supplement with one line per new row: S0NN, URL, opened date. |
| D2 | Rule 1: each quote must ground `teaches` | (a) The S039 quote is from the repo model card, not the row's file page, and grounds none of the teaches cell (sha256, size, three byte strings). (b) The S040 quote has no location; it is under §Problem Statement. (c) The S041 quote is a compact re-serialization of receipt.json:150-154, which are indented multi-line, but round-16.md:38 says "Quotes are verbatim". (d) The S038 quote grounds the digest only. | Append grounding lines: S039 paths-info `"oid": "270cba…"` @ 96f460f, plus the three-revision oids; S040 "§Problem Statement"; S041 "receipt.json:149-154 (JSON re-serialized)". |
| D3 | `teaches` overreach, S036 | The cell says "Every non-frontend path … answers 503". But server-http.cpp:347-353 handles `OPTIONS` (blank text/html) before the state gate at :354, and that range is inside the row's own anchor "347-359". GET probes are unaffected, so the verdict holds. | An appended note or a correction row: "every non-frontend, non-OPTIONS request". |
| D4 | Unswept negative claim, S037 ("the router … never emits that body") | Cited lines 440-462 show only router `is_ready` being set. In server-models.cpp @704366d (fetched, sha256 `9c5a6f2c…8b4a`): `proxy_get` serves `/metrics`, `/slots` and lora (server.cpp:242, 262, 264). With `autoload=false`, `router_validate_model` accepts a LOADING model, because `is_running()` includes LOADING (server-models.h:98-100). `proxy_request` then forwards to the child, and `make_header_msg` relays the child's status and body (server-models.cpp:2855-2858, 2877-2879). The child is a single-model server that is not ready until load, so the router can relay the exact `Loading model` 503. [INFERENCE: static read, not executed.] Router `/v1/models` uses its own `get_router_models` (server.cpp:269, 284), so kama's `/v1/models` verdict is unaffected. | Narrow the wording: "the router's own handlers never emit it; proxied GET routes may relay a loading child's body." |
| D5 | Scope and tier, S040 | The scope says "as guidance", but teaches states vLLM `/health` semantics as fact. The primary row for that is S004: `/health` calls `check_health()`, 503 only on `EngineDeadError`. S040 is A for llm-d's guidance, not for vLLM handler semantics. The teaches clause "after the v1.0 docs cutover" is marked `[INFERENCE]` in ScoutLlmdReadiness.md:21, but the row states it as fact. | Wording note: "llm-d v0.10 guidance; vLLM `/health` semantics stay with S004; cutover cause inferred." |
| D6 | Cross-source synthesis in `teaches` | S035's teaches cell says README:1258 "is contradicted by S036", which is outside S035's declared `/health`-only scope. S037's teaches leans on S036 the same way. Round 16 flags exactly this pattern for S012 (SOURCES.md:122-127). | A tradeoff, not a hard defect. Add the same kind of appended note for S035 and S037 for consistency. |
| D7 | Rule 5: search-log arithmetic and provenance | SOURCES.md:113-114 reads "Identified 9 … included 7 … reopened 1 … excluded 0", which accounts for 8 of 9. The Gate also cites `server-context.cpp:5396` and `server-models.cpp:2585`. Neither file is in the "Where" list (SOURCES.md:105-106) or pinned under sources/. I fetched both at the commit and the quotes are there (sha256 `dd1de0f2…2329` and `9c5a6f2c…8b4a`). pins.json lists 4 files and omits server.cpp, even though the file is pinned and its hash matches S037. | Append a log note that reconciles the count, names those two files, and pins them; add server.cpp to the manifest. |
| D8 | Learner path | The Health path (SOURCES.md:57) still routes to S021, whose URL is 404; S040 is on no path. There is precedent (S031/S011, line 58 is unchanged), but the learner still hits a dead URL. | Append a path line that uses S040. |

The impacted axes are calibration (D3, D4, D5: overstated rows feeding KQ19 knowledge) and freshness/provenance (D1, D2, D7, D8). None of these breaks a v1 must-print-nothing check, and none changes the C1 stub matrix or the C2 receipt verdicts. All are fixable by appending; none needs rejecting by the judge.

## Commands run (all exit 0 unless noted)

- `sed -n …`, `awk -F'|' …` and the CORPUS.md:135-147 check block on corpus/SOURCES.md.
- `git log`, `git diff 20e392e HEAD -- corpus/SOURCES.md`, `git ls-files .ufo/waves/round-16/{live,sources}`.
- `sha256sum` on the pinned copies and `tools/kama-probe.sh`.
- `curl` for the 3 llm-d URLs: 404 for `/docs/operations/readiness-probes`, 200 for `/docs/0.10/…`, 404 for `/docs/1.0/…`. The real v1.0 page is `/docs/operations/lifecycle/readiness-probes` per the advice; I did not fetch it.
- `curl` to the GitHub API returned 403 (rate limited); the release HTML and expanded_assets returned 200.
- `curl` to HF `api/models`, `paths-info` (main + 4 revisions), `commits/main` and `raw/main/README.md`: all 200.
- `curl` for raw server-models.cpp, server-context.cpp and server-models.h @704366d, and kubernetes/website `probes.md` @main: all 200.
- python3 for receipt inspection and word counts.

## Limitations

- D4 comes from reading the code. I did not run router mode.
- I counted words by whitespace split.
- The S017 line number was checked against kubernetes/website main today, not a pinned commit.
- I did not re-open the S035 rendered blob page, only the raw pinned copy.

## Installs

None.
