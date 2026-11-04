# SK01 — pin-watch recon + pinned-document anchors (r82 w1, 2026-11-04)

Read-only. Base `aaf974db`, lane tip at seat start `bacae072`, clock 2026-11-04T10:07-03:00. Every command, exit code and full table is in `SK01PinRecon/raw-fetch-log.md`.

## 1. pin-watch verdict
`check --repo <lane>` — the exact form in this dispatch and in `corpus/knowledge/pin-recheck-trigger.md:5` — **exit 2**, empty stdout, stderr
`pin-watch.py check: error: the following arguments are required: --pins` (the tool has no `--repo`; `--help` lists only `--pins [--tags-dir]`).
Correct `check --pins registry/engine-pins.tsv` — **exit 1**, live 1.37 s — `sglang pin=v0.5.22 newest=v0.5.23 newer=1`, `vllm pin=v0.32.0 newest=v0.33.0 newer=1`,
`llama.cpp pin=b11755 newest=b12110 newer=280`, `pins=3 current=0 behind=3 missing=0 error=0`. It was live, not cached: `b12110` is absent from the committed r80 tag receipt (max `b12103`).
## 2. Fetches — all HTTP 200; bytes / sha256[:12] / lines are of the received body
llama.cpp `tools/server/README.md` — b11755 119661/`714c067bdbc4`/2402 · b12103 136429/`eafc1b53abd7`/2620 · b12110 136429/`eafc1b53abd7`/2620 (**byte-identical to b12103**) · 39febd2a 135608/`8fd5abde2fb5`/2616.
SGLang `docs/docs/basic_usage/native_api.mdx` — v0.5.22 17359/`209087c3d30d` · v0.5.23 18295/`3ed171186990`; SGLang `python/sglang/srt/entrypoints/http_server.py` v0.5.23 119569/`d5d7ae6c5e8f`.
vLLM `docs/design/prefix_caching.md` — v0.32.0 13916/`67ee4e2b7bc2` · v0.33.0 13916/`67ee4e2b7bc2` (**byte-identical**).
## 3. `/health`, `/props`, `/slots` heading lines
b11755: `/health` 479 · GET `/props` 839 · POST `/props` 935 · GET `/slots` 983 · POST `/slots/{id}` 1157/1177/1197.
b12103 (= b12110): 480 · 930 · 1027 · 1075 · 1249/1269/1289. 39febd2a: GET `/models` 2197 (relation row 2's ref).
## 4. b11755→b12103: 15 hunks, 27509 bytes, **no hunk in §`/health`** (479-490 byte-identical apart from the offset)
Readiness-adjacent only: `@@ -926` GET /props adds `voices` + `chat_template_caps.reasoning_effort_levels` (`total_slots` untouched); `@@ -1262` GET /v1/models adds an `audio` modality;
`@@ -1990` Routing requests adds WS `/v1/realtime` + "Memory-based unloading" (`--models-memory-margin`); `@@ -2025` GET /models adds an `audio` clause (note 1 + the not-running bullet are context);
`@@ -2242` adds a `model_memory` event. No readiness statement is reworded, added or removed at any ref.

## 5. Held anchors at the newest ref: 21/21 **hold**
`/health` quote 481→482 byte-identical; 503 envelope 486→487; "`meta` can be `null`" 1258→1350; /props 927/928→1018/1019; /slots 983→1075;
options 50/165/169/177 unmoved; /metrics 1131→1223; /v1/completions 1314→1407 + OpenAI deferral 1320→1413; S555 router anchor
2197/2225/2227 (39febd2a) → 2201/2229/2231 (b12103), re-derives exactly. SGLang: `/get_model_info` is still the only route the page names
(v0.5.23:9,71) and the code deprecation holds (806-807, `/model_info` 812; v0.5.22's 790-791/796 shifted 16 lines).
## 6. The one real freshness finding is SGLang's, not llama.cpp's
v0.5.23 `## Health Check` 109-112 adds `/ready` (200 accepting, 503 starting/paused/unhealthy/shutting down) and `/ping` (SageMaker; stays 200 while
generation is paused) — absent at v0.5.22 and absent from `corpus/`. The held sentence is verbatim, so the four-value vocabulary has no word for an
addition: the honest value is `holds` + `new=/ready,/ping`; `drifted` would overstate.
## 7. Per relation row (register → today; can a recheck row be written mechanically?)
1 llama.cpp b11755 b12103/278 → b12110/280 — yes — `2026-11-04 trigger=newest:b12110 verdict=holds`; 2 llama.cpp 39febd2a b12103/110 → b12110/112 — yes — same value.
3 llama.cpp b7200 b12103/3395 → b12110/3397 — **numbers only, no verdict**: the lane holds no document at that ref.
4 sglang v0.5.22 v0.5.23/1 → v0.5.23/1 — yes — `2026-11-04 trigger=newest:v0.5.23 verdict=holds new=/ready,/ping`; 5 vllm v0.32.0 v0.33.0/1 → unchanged — yes — `2026-11-04 trigger=newest:v0.33.0 verdict=holds`.

## 8. Defects (not fixed — the lane tree is read-only for this seat)
D1 `corpus/knowledge/pin-recheck-trigger.md:5` ships an unrunnable recheck command (`--repo`); round-41's receipts use `--pins`. D2 no register defect: the
three llama.cpp rows moved because b12109+b12110 (b12110 = `v0.9.0`'s commit) appeared and b12104-b12108 never did, after the 07:45 receipt; sglang/vllm
lists are byte-identical. D3 row 3's role `cross-lane kengaku S178` collides with kama's own S178 (`corpus/SOURCES.md:190`, a kumitate instrument row).
