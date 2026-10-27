# CN01SiblingLiveEngines: round-60 sibling-overlap scan (read-only)

Seat: CN01SiblingLiveEngines (leaf, no dispatch). Scope: the 20 `*-shokunin` siblings other than kama, under `/home/vgpnk/Projects/shokunin/`. No file was edited. The only writes are this report and `out/CN01SiblingLiveEngines/grep-nonufo-counts.txt`.

Question: does a sibling touch a live local engine, hold Ollama claims, or overlap kama's new lifecycle tool `tools/kama-ollama-live.py` in province (kengaku model eval, kumitate dispatch, chousa research method, kagi credentials)?

## 1. Commands and hit counts

Pattern A (scoped to SKILL.md, PROVINCE.md, corpus/knowledge, tools):
```
P='ollama|11434|llama-server|llama\.cpp|registry\.ollama\.ai|ollama serve|live (engine|server)|stories260K'
cd /home/vgpnk/Projects/shokunin/<sibling> && { for f in SKILL.md PROVINCE.md; do [ -f $f ] && echo $f; done; find corpus/knowledge tools -type f; } | xargs -r grep -iEc "$P" | grep -v ':0$'
```
Scoped results: kengaku 28 hits in 11 files; kagi 8 in 6; kotoba 5 in 3; game-dev-3d 1; kake 1; kumitate 1; all other siblings 0.

Pattern A, whole repo (includes `.ufo/` wave artifacts and scratch):
```
grep -rIiEc "$P" <sibling> | awk -F: '{s+=$NF} END{print s+0}'
```
audio 190, chousa 6, game-dev-2d 221, game-dev-3d 496, kagi 78, kaidoku 41, kake 196, kasegi 0, kengaku 2057, kotoba 354, kotodama 11, kumitate 106, lore 0, mado 122, mori 25, revenger 4, souji 25, tabi 129, tameshi 57, tsukuroi 45. These totals are noisy. They are dominated by `.ufo/` and scratch copies, and `11434` matches hex hashes and digit runs.

Pattern B, excluding `.ufo/`, `.git/`, `.jj/` (the signal that counts). Receipt: `out/CN01SiblingLiveEngines/grep-nonufo-counts.txt`.
```
P='ollama|11434|llama-server|llama\.cpp|registry\.ollama\.ai|ollama serve|ollama pull|api/tags|api/ps'
grep -rIiEc --exclude-dir=.ufo --exclude-dir=.git --exclude-dir=.jj -E "$P" <sibling> | awk -F: '{s+=$NF} END{print s+0}'
```
audio 100, game-dev-3d 52, kengaku 188, kake 20, kagi 10, souji 17, tabi 15, game-dev-2d 3, kaidoku 5, kotoba 5. All other siblings are 0. Per-line checks showed that most non-`.ufo` hits in audio, tabi and game-dev-2d are false positives. `11434` matches inside hex commit hashes (`36240c70ee114347…`), filenames (`v16_fullpos_11434`) and digit runs. The `ollama` hits in game-dev-3d are a provider-name list in a captured API body and a query-trigger string.

Registry-URL check:
```
grep -rIil --exclude-dir=.git --exclude-dir=.jj "registry\.ollama\.ai" . | grep -v kama-shokunin
```
Output: empty across all siblings (pipeline exit status not captured). So no sibling fetches a model from `registry.ollama.ai`.

Live-engine start/import tokens:
```
grep -rIEc -e 'ollama serve' -e 'ollama create' -e 'kama-ollama' -e 'kama-llamacpp' -e 'stories260K' -e 'ollama-v0' -e 'llama-server --' <sibling>
```
No sibling runs `ollama serve`, `ollama create`, or imports the `stories260K` fixture. Matches are `llama-server --` argv quotes in kengaku's probe evidence (r10, r12) and in wave artifacts of mado, mori, tabi, tameshi, tsukuroi and kake. The mori round-56 artifact (`.ufo/waves/round-56/w1/Mo56ScoutSiblingOverlap.md`, 4 matches) was not read; that verdict is deferred.

Province claims, grep plus sed of ownership lines: kama PROVINCE.md lines 1-60; kengaku PROVINCE.md 1-30 and SKILL.md 338-344 and 784; kagi PROVINCE.md 1-45 and credential-isolation.md 30-38; kake PROVINCE.md 1-45 and 350-358; kaidoku EXAMPLE.kama.md 55-75; kumitate PROVINCE.md 25-32; kotoba PROVINCE.md line 63.

## 2. Sibling-touch facts

- kengaku owns model eval and its evidence touches the live engine. Its PROVINCE.md line 14 pins `http://127.0.0.1:34113` as "Served local model", with `llama-server` pid 1299, and kengaku's probe artifacts (r10, r12, r14) attest that process pin, and `ss -ltnp` on 34113. SKILL.md 784 records the endpoint as refusing connections since 2026-10-15, and the unit as deleted. So the kengaku live-engine evidence is historical.
- kengaku's round-9 record (`corpus/evidence/round9-fleet/sibling-overlap.md:43,55`) says no lane owns the model-serving plane. That is stale against kama's current PROVINCE claim.
- kagi records the configured endpoint `127.0.0.1:8080` (dead, Jitsi) against the live llama-server on 34113 (PROVINCE.md:42; SKILL.md:43; corpus/knowledge/credential-isolation.md:35; handler-trust-boundary.md:131). These are Janitor-consumer config observations, and kagi's province is credentials.
- kake refused the staged Ollama OpenAPI row (S358) as kama's province (PROVINCE.md:355; corpus/lessons/round-57.md:54-56; round-48.md:81-85). It holds no live engine.
- kotoba PROVINCE.md:63 declares kama adjacent: kama owns local endpoint identity and health; kotoba owns instruction text.
- kumitate PROVINCE.md:29 routes "Local model serving and endpoints → kama".
- kaidoku `EXAMPLE.kama.md` is an example kama-shaped file. It repeats kama's boundary text and the 8080→34113 history. kaidoku has no live engine.
- souji census rows (`census/round-29/waves/w1/deliver-sibling-overlap.tsv:194-195`) list `kama-shokunin/corpus/knowledge/ollama-evidence-replay.md` as an "incidental" byte-identical hit. Its round-26 ConnSiblings routes llama-server teardown to kama.
- tameshi round-24 `OverlapKama` artifact concludes zero kama/mori byte dependency. Historical only.
- tsukuroi `.ufo/waves/round-19/l1-capture/siblings/kama/…/PROVINCE.md` holds a captured snapshot of kama's PROVINCE. Historical only.

## 3. Verdicts (one per sibling)

| Sibling | Verdict | Basis |
|---|---|---|
| kengaku | **contested** | Owns model eval (out of kama's scope) and holds the endpoint-freshness and process-pin evidence (r10, r12, r14; SKILL.md 341) for the same surface kama's C1 lifecycle exercises. Kama PROVINCE claims "endpoint-drift detection / liveness probe conventions"; kengaku's round-9 record says the plane is unowned. Narrowed: kama's C1 starts its own child on a free port and does not touch 34113. No quality or eval overlap. |
| kagi | adjacent-report | Endpoint-config observation (8080 dead, 34113 live) that is kama's baseURL-drift domain; credentials are kagi's and kama's tool does not read them. |
| kotoba | adjacent-report | PROVINCE.md:63 names kama as the endpoint owner. No live engine touched. |
| kake | adjacent-report | Refused Ollama OpenAPI row routed to kama. No live engine. |
| kaidoku | adjacent-report | `EXAMPLE.kama.md` repeats kama's boundary. No live engine. |
| souji | adjacent-report | Census treats kama's `ollama-evidence-replay.md` as incidental duplicate; routes llama-server teardown to kama. |
| tameshi | none | Round-24 scan found zero kama byte dependency; non-`.ufo` count is 0. |
| tsukuroi | none | Non-`.ufo` count is 0. The `.ufo` kama PROVINCE capture is historical. |
| mori | none | Non-`.ufo` count is 0. The round-56 artifact (4 matches) is unread, so this verdict is provisional. |
| kumitate | none | PROVINCE.md:29 routes local serving to kama; non-`.ufo` count is 0. |
| chousa | none | Only 6 whole-repo hits, all digit collisions in wave logs. |
| audio | none | 100 non-`.ufo` hits are `11434`/`digit` collisions and filenames. |
| game-dev-3d | none | 52 non-`.ufo` hits are a provider-name list and a query string; no engine token. |
| game-dev-2d | none | 3 non-`.ufo` hits are digit collisions. |
| tabi | none | 15 non-`.ufo` hits are hex-hash collisions. |
| kasegi | none | 0 hits. |
| kotodama | none | 0 non-`.ufo` hits. |
| lore | none | 0 hits. |
| mado | none | 0 non-`.ufo` hits. |
| revenger | none | 0 non-`.ufo` hits. |

## 4. Overlap with kama's new lifecycle tool

Checked `tools/kama-ollama-live.py` and `tools/round60-c1-counter.py` exist at the kama tip (both present). Their functions are not read from sibling repos. No sibling token references the tool, the Ollama v0.40.11 release, or the stories260K fixture. Kama's C1 does not contest kumitate dispatch, chousa research method, or kagi credentials.

The single real contest is kengaku, on endpoint-liveness and process-pin evidence for local engines. The stale kengaku round-9 "unowned" record should be corrected in the integration step. Nothing here is a verdict on kama's claims.

## 5. Limits

- `.ufo/` wave artifacts were counted but not individually classified, except the sampled lines above.
- The mori round-56 artifact was not read.
- Ownership text was read from province files, not from every knowledge file.
- No sibling was run or contacted; no live engine was started by this seat.
