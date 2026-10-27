# A1Assim — Assimilation reconnaissance (round 53, read-only)

Verdict: **Assimilation: none for round 53.** The staged merge package is real, on-domain
for the province, but (a) partially stale — 9 of its 142 row ids now collide with lane
registry rows and 6 knowledge files + 3 amendment targets already exist in the lane in
extended form — and (b) no theme serves this round's claims (C1 process-memory code
identity, C2 evidence-pointer resolution). If L1 wants it later, re-stage; best-fit
theme is the served-identity / runtime-health-surface amendment cluster.

## What was read

- `/home/vgpnk/Projects/shokuknow/merge/kama/MERGE-REPORT.md` (148 lines) and `MERGE-REPORT.json`
- `/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md` (142 rows, ids S330–S471)
- `/home/vgpnk/Projects/shokuknow/merge/kama/knowledge/` (59 files under `corpus/knowledge/`), `amendments/` (3 files)
- Lane: `corpus/SOURCES.md`, `PROVINCE.md`, git history for collision provenance

## Themes in MERGE-REPORT.md

1. **Source-registry expansion** — `SOURCES.append.md`, 142 rows in the lane's 11-column
   `SOURCES-CONTRACT-v1` schema, ids S330–S471, mined from vLLM / SGLang / Ollama /
   llama.cpp serving documentation across 16 corpus-expansion rounds (round1–round16):
   KV-cache eviction/reclamation, prefix-cache reuse, served-name/alias resolution,
   health-route semantics (what a 503 means, per route and engine), context capacity
   (declared vs served), llama.cpp reachability + loading lifecycle, SGLang docs
   version pinning + native-API deprecation, cross-literate endpoint venues
   (Chinese/Japanese), and a spot-check protocol.
2. **Knowledge entries** — 65 proposed: 59 files under `knowledge/corpus/knowledge/`
   plus one target-path conflict folded across rounds 12–16
   (`corpus/knowledge/spot-check-protocol.md` keeps one file with dated *Superseded
   passage* headings).
3. **Append-amendments** — 3 files to append (not replace) to existing lane knowledge:
   `serving-alias-contract.md`, `endpoint-health-probe-conventions.md`,
   `served-model-id-resolution.md`.
4. **Registry-hygiene flags** — 18 staged rows share a source with a lane-held row and
   need an aspect check before adoption (e.g. S331 vs S196, S420 vs S004, S460/S471 vs
   S016); 5 `used-by` pointers corrected at packaging time (S398, S399, S405, S456,
   S457); 2 rows forced to `queued` (S464, S465 — `used-by` names a target no entry cites).
5. **Adopt checklist** — 8 procedural steps (read Gate blocks, spot-reopen a sample,
   append rows, copy knowledge, append amendments, fold duplicates, update
   QUALITY/SCORECARD/LOG, don't touch refused rows).
6. **Id-space bookkeeping claim** — "lane registry currently holds **203** rows; first
   staged id is **S330**" — see staleness below.

## Province fit (per theme)

Province (`PROVINCE.md`): local model serving & endpoint health — producer discovery,
baseURL pins, served-model-id reconciliation, liveness/readiness probe conventions,
which vLLM process serves `/health`, endpoint-drift detection, lane instruments.
Refuses: model quality/eval, credentials, dispatch/route mechanism, remote web surfaces.

| Theme | Fits province? | Note |
|---|---|---|
| Served-name/alias + served-model-id resolution (S331, S341, S358, S365, crosswalk r8–r16) | **Yes — core** | The province's "served-model-id reconciliation" surface; held K05 ground since rounds 20/31/42 |
| Runtime-health-surface matrix / which process answers `/health` (amendments r3–r16, S420/S440/S454/S462 vs S004) | **Yes — core** | Province owns `corpus/knowledge/runtime-health-surface-processes.md` (S480/S481); the "process column" gap is exactly the province's open frontier |
| Probe conventions + health-route semantics (503 taxonomy, `/ready` vs `/health`) | **Yes** | "liveness/readiness probe conventions" surface; S364, S377, S396 vs S329 |
| Context capacity declared-vs-served (r5–r11) | **Yes — already held** | Round 20 (GGUF declared identity) + round 42 (`context-capacity-engine-sides.md`) |
| llama.cpp reachability + loading lifecycle (r6–r11) | **Yes** | Lane owns the llama.cpp pin watch and the b11755/b11909 live fixtures |
| KV-cache reclamation / prefix-cache reuse (S330–S363 cluster) | **Borderline** | Engine-internal; the lane's own S333 scope cell says "engine-internal, carries no endpoint semantics". Fine as corpus knowledge, not a province surface |
| Hosted/OpenAI-compat host-vendor contracts, cross-literate venues | **Adjacent** | Source *readings* about hosted surfaces; province refuses to *sample* remote surfaces but reading their docs as sources is the lane's normal mining |
| Spot-check protocol | **Yes** | Corpus hygiene; adjacent to C2's evidence discipline |
| Registry hygiene + adopt checklist | N/A | Procedural |

No theme violates a refuse (no model quality, no credentials, no dispatch).

## Fit with this round's claims

- **C1 (process-memory code identity, S506–S508)**: no theme touches `/proc/<pid>/mem`
  code identity. Closest is the llama.cpp loading-lifecycle entry (install channels,
  where build options live) — background for the b11909 fixture, not code verification.
- **C2 (evidence-pointer resolution)**: no theme resolves citations. Closest is the
  spot-check protocol (count the coverage map before asking for work) — corpus hygiene,
  not cited-path checking.

**No theme serves round 53's claims; this is a later-round corpus/knowledge candidate.**

## ID-collision extraction (contract command)

```
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' corpus/SOURCES.md | grep -oE 'S[0-9]+' | sort > reg-ids     # 250 rows
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' merge/kama/SOURCES.append.md | grep -oE 'S[0-9]+' | sort > append-ids  # 142 rows
comm -12 reg-ids append-ids
```

**Collision count: 9** — `S330 S333 S334 S335 S346 S347 S352 S353 S363`.

All 9 are same-source rows on both sides but textually **diverged** (lane versions
re-anchored/refreshed; e.g. S333 lane anchor "§How eviction picks a victim" mined
2026-10-25 vs staged "§Eviction candidates" mined 2026-10-23; none of the 9 full rows
is byte-identical). Provenance: round-37 commit `09b4d36e` (2026-10-25 05:03 -0300)
introduced S330/S333/S334/S335/S346/S347/S363; round-38 commit `54e29520` introduced
S352/S353. The package was staged 2026-10-24 23:33 -0300 against a 203-row registry —
round-37's own assimilation artifacts (`.ufo/waves/round-37/assimilation/collisions`,
then 0) predate the lane's independent integration of the same research. A naive
append today would double-add 9 ids.

## Additional staleness (beyond ids)

- 6 of the 59 knowledge files already exist in the lane, all **larger** there (lane
  integrated and extended them): `kv-cache-reclamation-models.md` (3977 vs 3533 B),
  `prefix-cache-reuse-models.md` (2654 vs 2363 B), `sglang-docs-version-pinning.md`
  (4089 vs 2773 B), `sglang-docs-version-pinning-amendment-2026-10-23.md` (5415 vs
  2377 B), `prefix-cache-reuse-models-amendment-2026-10-23.md` (2527 vs 2155 B),
  `served-identity-crosswalk-amendment-2026-10-24-r16.md` (1083 vs 3551 B — merge copy
  is the larger here, still content-different).
- All 3 append-amendment targets exist in the lane (`serving-alias-contract.md`
  4009 B lane vs 4026 B amendment; `endpoint-health-probe-conventions.md` 4468 vs
  3800 B; `served-model-id-resolution.md` 5050 vs 3213 B) — content differs both ways;
  adopt step 5 (append as dated section) would still apply but must be diffed first.
- The report's "203 rows / first staged id S330" bookkeeping is stale (lane now 250
  rows, ids through S509).

## Recommendation

**Assimilation: none** for round 53 — nothing here feeds C1 or C2, and the wave is
already integrated. For a later round, if L1 wants this corpus expansion: re-stage the
package (fresh id assignment past the lane's max, or quarantine the 9 colliding ids +
6 existing knowledge files + 3 amendment targets), then adopt the
**served-identity crosswalk + runtime-health-surface process-column** cluster — the
strongest province fit and the gap the province's own `runtime-health-surface-processes.md`
already names. Until re-staged, treat `merge/kama/` as a stale snapshot, not a queue.
