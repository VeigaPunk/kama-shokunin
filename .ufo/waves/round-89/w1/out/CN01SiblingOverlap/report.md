# CN01SiblingOverlap — sibling-overlap scan for the round-89 surfaces

Seat: CN01SiblingOverlap (leaf). Read-only. No lane file edited, nothing installed, no endpoint
contacted (no GET, no POST), no git/jj mutation, no clone.

## Scope

Swept all 19 sibling lanes under `/home/vgpnk/Projects/shokunin/*-shokunin` (kama excluded) for the
three round-89 surfaces: **(a) GGUF header/loadability checks, (b) llama.cpp router readiness,
(c) router API error signatures**. Keywords: `gguf`, `router`, `models-dir`, `failed to load`,
`llama-server`, `kama-probe`. Read `SKILL.md`, `PROVINCE.md`, `corpus/knowledge/`; narrowed into
`tools/`, `plans/`, `registry/`, `corpus/evidence/` and each lane's current `round-89` wave only where a
hit needed an owner. Compared against kama `corpus/knowledge/router-unloadable-model.md`,
`SKILL.md:1789-1828` (§§ Round-89 unloadable router models, Router error signatures),
`corpus/knowledge/cross-lane-scope.md:10-30`, `PROVINCE.md:6-30`.

## Commands and outputs (true exit codes)

1. `grep -Eic 'gguf|[^a-z]router|models-dir|failed to load|llama-server|kama-probe'` over every sibling
   `SKILL.md`/`PROVINCE.md` → 38 files present, **30 with zero hits**; nonzero: kagi `SKILL.md` 2,
   kagi `PROVINCE.md` 1, kaidoku `SKILL.md` 1, kake `SKILL.md` 1, kasegi `SKILL.md` 1,
   kengaku `SKILL.md` 3, kengaku `PROVINCE.md` 5, kotoba `SKILL.md` 8. Loop rc=0.
2. `grep -rEin 'gguf|models-dir|failed to load|llama-server|llama\.cpp|kama-probe'` over sibling
   `SKILL.md`, `PROVINCE.md`, `corpus/knowledge/` → substantive hits only in kengaku (endpoint/env rows),
   kagi (endpoint/env rows), tameshi (2 rows naming *kama's own* tools). rc=0.
3. `grep -rEin 'router' … | grep -Ei 'llama|model|gguf|1234|lfm3|autoload|unloaded|endpoint'` → llama.cpp-router
   hits only in kengaku. rc=0. Every kotoba/kumitate/kaidoku/kake/kasegi/mado `router` hit was opened and is a
   homonym (skill routing, dispatch route, `react-router`, `router-fs`).
4. `grep -rEin 'model is not loaded|model name=|/models/load|/models/unload|models-max|MODEL_UNLOADED'`
   fleet-wide, kama lane excluded → hits only in kengaku's saved upstream README copy, kengaku's wave
   receipts, and the fleet's own `.ufo/reports/round-88/kama.md` (kama's work, not a sibling claim). rc=0.
5. `grep -rIil 'gguf' kengaku-shokunin --exclude-dir=.git --exclude-dir=.jj | wc -l` → **287** files; all are
   `corpus/evidence` receipts, knowledge prose and wave copies — **no GGUF instrument** in any lane but kama.
   rc=0.
6. Re-read kama receipts for the cross-lane check: `controls/harm-base-operator-1234.out` (4 ids,
   `MODEL_OK router-unloaded-autoload`, `/health` 200) and `measured/harm-M.out:18-21` (same 4 ids at M,
   same verdicts). Read-only file reads; the router was not contacted by this seat.

## Findings

### Contested-scope table

| # | Lane | Evidence | What it owns | vs round-89 kama entries | One-line recommendation |
|---|---|---|---|---|---|
| 1 | kengaku | `PROVINCE.md:26-27` — "**Not owned:** the model-serving plane (llama-server flags, slot/batch config) — no lane owns it; escalate to the integrator" | round-9 refusal block | **CONTEST — stale.** Contradicts its own `PROVINCE.md:15` ("flag authority is kama's (serving plane)") and kama `PROVINCE.md:6-19`. r89 makes router argv (`status.args`) a graded evidence source (`SKILL.md:1795-1801`), i.e. exactly the "serving plane" this block calls unowned | Report to kengaku: re-point its own refusal block at kama; no kama edit |
| 2 | kengaku | `corpus/knowledge/served-endpoint-identity-pin.md:56-57` — "the router's list is a catalogue, not a statement about what is loaded" (2026-10-28) | served-endpoint identity pin (eval-side) | **DUPLICATES the inventory half** kama already held (r88 `SKILL.md:1763-1766`, S553/S581). Does **not** cover r89's half ("cannot load" before any request) | kama r89 adds one clause citing kengaku S178:57 as the adjacent prior statement; novelty stays the loader-rejection half |
| 3 | kengaku | `served-endpoint-identity-pin.md:35` — `--models-dir /home/vgpnk/models/lfm3 --models-max 2`, "lists 5 model ids" | operator router :1234 pin (capture-time) | **COMPLEMENTS, count stale.** max 2 with 5 ids ⇒ ≥3 entries unloaded at any instant — precisely kama's false-red population. kama's own GET at 2026-11-06 lists **4** ids (`harm-base-operator-1234.out:…served_model`; `harm-M.out:18-21`), verdict unchanged | Report: kengaku re-takes under its own rule 2 ("re-take it, do not extend it"); kama keeps its 4-id receipt |
| 4 | kengaku | `served-endpoint-identity-pin.md:19` — argv `--alias`,`--model` / `/props.model_path` | identity pin fields | **COMPLEMENTS, different reach.** kengaku's argv read needs a *running* instance; r89 reads per-entry `status.args` for entries that **never ran** (`router-unloadable-model.md` §3) | One clause in the r89 entry so the fleet does not read the two argv reads as one technique |
| 5 | kengaku | `.ufo/waves/round-51/w1/SrcLlamaServer.md:157` — dropped "the doc's model-catalog/router material (`/models`, `/models/load`, L2197+) because the lane's surface is a single served endpoint" | eval surface scope | **COMPLEMENTS.** The router-API ground r89 C2 now holds (`SKILL.md:1809-1828`) was read and deliberately refused by kengaku; no competing row exists | No action; cite as the boundary that left this ground to kama |
| 6 | kengaku | `corpus/evidence/round12-fleet/r12-endpoint-freshness.md:350-…` — stdlib GGUF header walk, "never reads a payload byte" | header-parse technique (for a `meta.size` delta) | **DUPLICATES technique only**; kama `PROVINCE.md:100-102` (round-20) already says the overlap is acknowledged, not absorbed. r89's new material is the *loader check set* (S584/S585), not header reading | No action |
| 7 | kagi | `SKILL.md:43` — "Verify model endpoint is real \| `curl -fsS <endpoint>/health` → `{"status":"ok"}`" | credential/auth lane, but the row is endpoint identity | **CONTESTED PURPOSE.** A router answers `/health` 200 while listed entries cannot load (r89 C1; `harm-base-operator-1234.out` shows `GET /health -> 200` beside `router-unloaded-autoload`). `/health` proves a listener, not a loadable model | Report: kagi's row states "listener identity only" and cites r89 for the per-model layer; kama does not absorb the recipe |
| 8 | kagi | `PROVINCE.md:63` — "configured model endpoint `127.0.0.1:8080` (dead: Jitsi) vs live llama-server on `34113`" | historical endpoint drift | **COMPLEMENTS, premise stale**: kama's last recorded listener census (round 65, `PROVINCE.md:250-258`) found no listener on 8080/34113 and the unit is absent; r89 sampled neither port | Report only (kagi's file) |
| 9 | tameshi | `corpus/knowledge/fleet-kill-rate-ledger.md:125-127`, `fleet-suite-census.md:623-625` — kama `tools/{kama-probe,test-snapshot}.sh` are "sightings … file existence is O; gate-ness U" | fleet suite census / kill-rate | **NO CONTEST; census gap.** r89 adds `tools/round89-unloadable-cells.py`, `tools/round89-signature-rows.py` and a probe decision rule, none surveyed or queued | Report the two counter paths to tameshi; kama claims no fleet gate-ness |
| 10 | revenger | `.ufo/waves/round-89/w1/ConnectorR89.md:36` — kama "not contested" (cites kama `PROVINCE.md:10-13`, `round79-unregistered-census.py`) | this round's own sibling scan | **CORROBORATES** | No action |
| 11 | kotoba | `SKILL.md:151` "## Router model — which harness, which gate"; `corpus/knowledge/harness-router-models-round9.md`; `sibling-overlap-census-round49.md:76` (kama "adjacent") | harness/skill routing; description-level overlap census | **HOMONYM only** — no serving surface | No action |
| 12 | kumitate | `corpus/knowledge/seat-route-from-session-transcripts.md:79` ("reported by a router") | dispatch/route mechanism | **HOMONYM.** `POST /models/load` is server state, not route selection; kama `SKILL.md:1828` already forbids it against an operator router | No action |
| 13 | chousa | `.ufo/waves/round-40/w1/ConnectorSiblingScan.md`, `round-73/80/82` wave dirs | research lane; holds *copies* of kama's `kama-probe.sh`/counters as blobs | **NO CLAIM** — copies for source-curation scans | No action |
| 14 | mado, kaidoku, kake, kasegi | `walker-route-r18.md`, `2026-10-13-r4-06`, `SKILL.md:755` (`react-router`), `SKILL.md:1021` | — | **HOMONYMS** | No action |

### Labelled findings

- **DEFECT (kengaku `PROVINCE.md:26-27`).** A round-9 refusal still says the model-serving plane is
  unowned and "escalate to the integrator", while the same file's round-51 row (`:15`) hands flag authority
  to kama and kama has owned that plane since `PROVINCE.md:6-19`. Round 89 makes the contradiction
  load-bearing: C1 grades `status.args` argv paths and C2 grades router endpoints. A sibling seat that
  reads `:26` would treat r89's evidence class as out of province. Owner: kengaku.
- **DEFECT (stale pin, low severity).** kengaku `served-endpoint-identity-pin.md:35` says the operator
  router "lists 5 model ids"; kama's GET-only receipts list 4 at 2026-11-06
  (`controls/harm-base-operator-1234.out`; `measured/harm-M.out:18-21`), names `LFM3-1.7B`,
  `LFM3-1.7B-Uncensored`, `LFM3-Omni-2B`, `LFM3-VL-2B`. Capture-time drift, not a contradiction of r89.
- **NOTE — r89 cites no sibling at all.** `corpus/knowledge/router-unloadable-model.md`,
  `corpus/lessons/round-89.md` and `SKILL.md:1789-1828` name only kama's own prior art (S553, S581, S583-585).
  Three one-clause placements exist: kengaku `served-endpoint-identity-pin.md:57` (catalogue≠loaded),
  kengaku `:19` (argv reach), kengaku `:35`/`--models-max 2` (why the non-false-red guard matters on the
  operator's live router: ≥2 of 4 entries are unloaded at all times and stayed `MODEL_OK` at M).
- **NOTE — the `/health` false-green class is fleet-wide, not probe-local.** r89 closes it inside
  `kama-probe.sh` but kagi's `SKILL.md:43` remains a `/health`-only recipe for "is the endpoint real".
  kama's `cross-lane-scope.md:12` already assigns credential/auth to kagi and endpoint identity to kama;
  the recipe is kagi's to re-word.
- **NOTE — no sibling holds a GGUF instrument.** 287 kengaku files mention GGUF; none parses a header.
  r89's `QSIZES`/loader-check set has no fleet competitor, and no lane contests C2's signature rows.

## Deliverables

- `.ufo/waves/round-89/w1/CN01SiblingOverlap.md` (this report)
- `.ufo/waves/round-89/w1/out/CN01SiblingOverlap/contested-scope.md` (table + recommendations, standalone)

VERDICT: holds — no sibling contests round 89's kama ground; kengaku `PROVINCE.md:26-27` is a stale contradiction to report, not edit.
