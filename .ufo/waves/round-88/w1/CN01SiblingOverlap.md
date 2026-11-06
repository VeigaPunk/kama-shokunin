# CN01SiblingOverlap — sibling-overlap scan (kama round 88, wave 1)

## Scope

Read-only scan of every sibling lane repo under `/home/vgpnk/Projects/shokunin/*-shokunin/` (kama excluded)
for work on llama.cpp router mode, `/v1/models` status, model readiness/health probes, llama-server, Ollama
readiness, and the `stories260K` fixture. Searched `SKILL.md`, `PROVINCE.md`, `corpus/knowledge/`, `tools/`;
additionally read `kengaku-shokunin/plans/round51_surfaces.py` because kengaku's knowledge entry names it as
its endpoint re-prober. Also read `kama-shokunin/corpus/knowledge/cross-lane-scope.md` for an ownership row
covering router mode. No lane file was modified, no endpoint contacted (b7200 README is a public GET named by
a sibling's own source line). Lanes with zero hits: chousa, kaidoku, kotodama, mado, mori, audio,
game-dev-2d/3d, lore, revenger, tabi, kumitate. `stories260K` appears in **no** sibling file (0 of the fleet).

## Commands and outputs (exit codes)

| Command | rc | Output |
|---|---|---|
| `grep -rIl 'stories260K' */ --include='*.md' --include='*.py' --include='*.sh' --include='*.json' --include='*.tsv'` filtered to non-kama, non-`.ufo` | 0 | `0` files |
| `grep -Hn -iE 'llama[-_. ]?cpp|llama-server|/v1/models|router[- ]mode\|stories260K\|ollama' */{SKILL.md,PROVINCE.md}` | 0 | hits in kagi, kengaku, kake, kotoba, tsukuroi only (table) |
| `grep -rIl <same pattern> */corpus/knowledge */tools` | 0 | kagi 3, kengaku 10, kotoba 11, tsukuroi 2; **no** sibling `tools/` hit |
| `curl -sS -o b7200-readme.md -w '%{http_code} %{size_download}' …/ab49f094d…/tools/server/README.md` | 0 | `HTTP=200 bytes=72181`; `sha256 fb4ab6f2e4db180bf9c89533ef63556559c60a66f9c39a92f0c23cd88f6c6a53` |
| `grep -ci router` / `grep -ci 'status object'` / `grep -ci unloaded` on that file | 1 / 1 / 1 | `0` / `0` / `0` (no-match rc) |
| `grep -n 'v1/models' b7200-readme.md` | 0 | `1157:### GET /v1/models: OpenAI-compatible Model Info API` — "The returned list always has one **single** element" |
| `git -C kengaku-shokunin log -1 --format='%H %ad %s' --date=short -- corpus/knowledge/served-endpoint-identity-pin.md` | 0 | `11e79380d33d6e811f0010f2a2a0c22a3cdc359e 2026-10-28 …` |
| `git -C kama-shokunin rev-parse 9b4c7af1:corpus/knowledge/unregistered-listener-census.md` | 0 | `b042425b515d684de276e6851267baa64ee6ab13` |
| `git show 9b4c7af1:corpus/knowledge/unregistered-listener-census.md \| grep -n 'not a readiness claim\|status.value'` | 0 | `28:## Why a model list is not a readiness claim`, `32:… status.value — loaded, loading, unloaded, sleeping …` |
| `git -C kama-shokunin cat-file -e 9b4c7af1:corpus/knowledge/router-mode-readiness.md` | 128 | `fatal: … exists on disk, but not in 9b4c7af1…` (file is new this round) |
| `git show 9b4c7af1:corpus/SOURCES.md \| grep -c '^| S553 '` | 0 | `1` (S553 present at base) |
| `wc -l kengaku-shokunin/corpus/evidence/round51/surfaces/endpoints.txt` | 0 | 15 lines; `:1234/health -> 200`, `MODELS1234 [5 ids]`, **no `status` field read** |

## Overlap table

| Lane | path:line | Claims | Class | Contradicts r88 rule? |
|---|---|---|---|---|
| kengaku | `corpus/knowledge/served-endpoint-identity-pin.md:57` | "the router's list is a **catalogue, not a statement about what is loaded**" (2026-10-28, `11e7938`) | **duplicate** (prior semantic art) | No — corroborates. Its own source S178 = b7200, where `router`/`unloaded`/`status object` occur **0** times, and its receipt records ids only; so the sentence is inference, and kama's S581/S553 supply the doc basis kengaku lacks |
| kengaku | `PROVINCE.md:15`, `:1029` | `:1234` router "present", lists 5 ids, `/health` `/props`; `:45669` ABSENT 2026-11-04 | complementary (presence, not readiness) | No — but "present" is HTTP-200 presence, the same shape C1 rejects one level down |
| kengaku | `SKILL.md:368` | battery step 1 "Probe the endpoint, not the config: `GET /v1/models` + `/health`"; names kama as serving-plane health owner in the same paragraph | contested (procedure) | **Yes on the readiness leg**: both routes pass while a router model is `unloaded`; the sentence's ownership clause is consistent with kama's rule |
| kengaku | `SKILL.md:915` | freeze gate "Probe every endpoint before freeze (`/v1/models`, `/health`)" | contested (gate) | **Yes on the readiness leg**: same false-green; `MODEL_UNLOADED` is the discriminator |
| kengaku | `plans/round51_surfaces.py:127-129` | surface re-prober grades presence by `r.status == 200` | contested (instrument) | **Yes**: a 200 from a router with nothing resident passes; kama's verdict is the missing leg, kengaku's instrument is not kama's to change |
| kagi | `SKILL.md:43` | "Verify model endpoint is real: `curl /health` → `{"status":"ok"}`" | complementary (identity) | No — proves llama.cpp answers, not that a model is loaded; C1 recorded `/health` 200 with no resident model, so this row must not be extended to readiness |
| kagi | `corpus/knowledge/op-cli-surface.md:86-91` | cheap drift check; "a foreign listener 404s or closes" | complementary | No — foreign-vs-llama.cpp is orthogonal to loaded/unloaded |
| kagi | `PROVINCE.md:63` | "8080 (dead: Jitsi) vs live llama-server on `34113`" | duplicate + stale | No — kengaku `PROVINCE.md:15` records `:34113` ABSENT 2026-11-04; kama `cross-lane-scope.md` corrections A29/A34 already cover |
| kake | `PROVINCE.md:355`; `corpus/lessons/round-{48,49,50,57}*.md` | Ollama OpenAPI refused as kama's province; "kama owns local model-serving endpoints" | complementary (ownership) | No — kama `SOURCES.md` S519-S525/S554/S557/S558 already hold those Ollama rows |
| tsukuroi | `PROVINCE.md:122` (OUT-002/ADJ-01), `:46` | kama owns `/v1/models` vs `--alias` vs configured id reconciliation | complementary (ownership prior art) | No — supports ownership; the row names identity, not readiness, so r88 silently widens it |
| souji | `census/round-43/waves/w1/R43connector01/scan-receipts.json:81,305,481` | frozen copies of kama `SKILL.md:129` and `:308` probe rows | duplicate (frozen copy) | No — stale-copy hazard: they cannot carry the r88 verdict table |
| tameshi | `corpus/knowledge/fleet-kill-rate-ledger.md:127`; `fleet-suite-census.md:625` | kama `tools/{kama-probe,test-snapshot}.sh` = "sightings … not queued"; gate-ness `U` | none | No — an explicit non-verdict |
| kotoba | `SKILL.md:151-154`; `corpus/knowledge/harness-router-models-round9.md` | "Router model" = harness/model routing | **none (homonym)** | No — excluded; a keyword count would wrongly credit sibling coverage |

## Findings

- **F1 DEFECT — the round's "new coverage ground" reason is false.** `corpus/lessons/round-88.md` §Gate admits
  `corpus/knowledge/router-mode-readiness.md` as "New coverage ground (router mode was not on the coverage
  map)". At base `9b4c7af1`, `corpus/knowledge/unregistered-listener-census.md` (blob `b042425b…`, lines 28-36)
  already has `## Why a model list is not a readiness claim` and the identical `status.value` vocabulary,
  sourced S553 (present at base); S553's consequence cell reads "a model list is not proof of a loaded model or
  of consumer readiness". kengaku stated the same at `served-endpoint-identity-pin.md:57` on 2026-10-28.
  Evidence: commands above. The C1 **predicate** (counter, `mismatches=0`) is untouched; only the admission
  reason and the frontier/lesson wording. The entry's residual novelty is the verdict map + observation table
  + the 400 `model is not loaded` oracle — that should be what the Gate names, with S553/census and kengaku:57
  cited as prior art rather than claimed as new ground.
- **F2 NOTE — kengaku's endpoint probes are readiness-blind in exactly the shape r88 fixes.** `SKILL.md:368`
  and `:915` gate a battery on `/v1/models` + `/health`; `plans/round51_surfaces.py:127-129` grades by 200.
  kengaku's own 2026-10-28 receipt shows `:1234/health -> 200` beside five listed ids and **no** status read —
  it cannot say whether anything was resident. Report only; kengaku concedes serving-plane health to kama in
  the same paragraph (`SKILL.md:368`).
- **F3 NOTE — kagi's `/health` row is identity, not readiness, and is not contradicted.** `SKILL.md:43` and
  `op-cli-surface.md:86-91` distinguish a foreign listener (404/close) from llama.cpp (200 `{"status":"ok"}`).
  C1's finding is that the 200 survives with no resident model, so the row stays valid for the Jitsi class and
  must not be cited as a model-available check.
- **F4 NOTE — no ownership row names router mode.** `cross-lane-scope.md` assigns "identity and current health
  of a local model endpoint" to kama (line 3) and endpoint probes in the systemd-unit consumer row, but no row
  names router mode, `status.value`, `MODEL_UNLOADED`, or any sibling's endpoint-readiness check; the round-71
  and round-72 overlap sections name four instrument families (pre-report gates, waivers, PROVINCE
  reconciliation, receipt-tip binding) and none of them is an endpoint-readiness gate. The gap is naming, not
  authority: F2/F3 are consumer-side checks whose readiness leg is already kama's.
- **F5 NOTE — stale host facts, already routed.** kagi `PROVINCE.md:63` still calls `:34113` live; kengaku
  `PROVINCE.md:15` records it ABSENT 2026-11-04 and only `:1234` answering. `cross-lane-scope.md` corrections
  A29/A34 already flag the old 34113/8080 rows as historical.
- **F6 NOTE — souji's cached kama rows.** `scan-receipts.json:81,305,481` embeds kama `SKILL.md:129`/`:308`
  text. Any audit that reads souji's census instead of kama's SKILL.md will miss this round's
  `MODEL_UNLOADED` row.

## Adjacency recommendation (report, never absorb)

Kama should not absorb any of these surfaces; it should name them. Concretely: (1) land one
`cross-lane-scope.md` row that says router-mode **readiness** — `status.value` on a listed id, the
`MODEL_LOADING`/`MODEL_UNLOADED` verdicts — is kama's, while kengaku's battery/freeze gates
(`SKILL.md:368,915`, `plans/round51_surfaces.py`) and kagi's `/health` identity check (`SKILL.md:43`) remain
their owners' and are **consumer-side checks that kama's verdict discriminates**, citing S581 and S553; (2)
correct the round-88 Gate admission reason to name the residual novelty (verdict map, live oracle) and cite
S553 + `unregistered-listener-census.md:28-36` + kengaku `served-endpoint-identity-pin.md:57` as prior art,
which also converts a duplicate into a corroboration; (3) note to kengaku (report line only, no edit) that
S581 at b11755 is the documentation its rule 4 infers from b7200 (0 router hits there), so the offer is a
source, not a verdict; (4) record souji's census copies and kagi's `:34113` line as non-citable current state.

## Deliverables

- `.ufo/waves/round-88/w1/out/CN01SiblingOverlap/receipts.txt` — every command, exit code, raw output.
- `.ufo/waves/round-88/w1/out/CN01SiblingOverlap/CN01SiblingOverlap.md` — copy of this report.
- `.ufo/waves/round-88/w1/CN01SiblingOverlap.md` — this report (Report trailer path).

VERDICT: partial — no sibling contradicts the frozen C1 rule (kengaku:57 and kagi:43 corroborate it), but the round's "new coverage ground" admission reason is falsified by kama's own base corpus and kengaku's prior rule, and cross-lane-scope has no router-mode row.
