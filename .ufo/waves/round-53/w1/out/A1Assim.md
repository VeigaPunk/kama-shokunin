# A1Assim — round-53 seat report

Verdict: **Assimilation: none.** The staged `shokunin`-side merge package for kama is
on-domain but stale (9 row-id collisions + 9 pre-existing file targets against the
current lane tree) and no theme serves round 53's claims (C1 process-memory code
identity, C2 evidence-pointer resolution). No lane defect found; nothing edited
(read-only seat). Full analysis: `.ufo/waves/round-53/w1/out/A1Assim/assim.md`.

## Assignment

Read-only recon: list themes of `/home/vgpnk/Projects/shokuknow/merge/kama/MERGE-REPORT.md`,
check each against `PROVINCE.md` and this round's claims, run the contracted id-collision
extractor, recommend `Assimilation: none` or one later-round theme. No counter run was
assigned to this seat; counters/preregistration/controls are frozen and were not touched.

## Evidence

Scratch: `/fast/scratch/hyaku/kama-r53/A1Assim` (removed after the run). Lane read-only
throughout; no git/jj mutation anywhere.

1. **Themes** (from `MERGE-REPORT.md`, 148 lines): source-registry expansion
   (`SOURCES.append.md`, 142 rows, ids S330–S471, 16 corpus-expansion rounds);
   65 knowledge entries (59 files, one 4-round duplicate-target fold on
   `spot-check-protocol.md`); 3 append-amendments; registry-hygiene flags (18 staged
   rows needing aspect check vs lane-held sources, 5 `used-by` corrections, S464/S465
   forced `queued`); 8-step adopt checklist. Details with per-theme province fit table:
   `out/A1Assim/assim.md` §Themes / §Province fit.
2. **Province fit**: served-identity/alias resolution, runtime-health-surface process
   column, probe conventions, context capacity, llama.cpp lifecycle — fit (several
   already held: rounds 20/31/42/43). KV-cache/prefix-cache internals — borderline
   (engine-internal, "carries no endpoint semantics" per the lane's own S333 scope
   cell). Hosted vendor contracts / cross-literate venues — adjacent source readings,
   no refuse violated (no model quality, no credentials, no dispatch).
3. **Round-53 claim fit**: none. C1 — no theme touches `/proc/<pid>/mem` code identity;
   closest is llama.cpp loading-lifecycle background. C2 — no theme resolves citations;
   closest is the spot-check protocol (corpus hygiene, not cited-path checking).
4. **Collision extraction** (contract command, run in scratch):
   - lane `corpus/SOURCES.md` registry rows: **250** (`grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' … | sort | wc -l`)
   - append rows: **142** (ids S330–S471; header schema matches the lane's 11-column
     `SOURCES-CONTRACT-v1` format)
   - `comm -12` → **collision count 9**: `S330 S333 S334 S335 S346 S347 S352 S353 S363`
   - all 9 same-source but textually diverged (0 of 9 full rows byte-identical; e.g.
     S333 lane anchor "§How eviction picks a victim" mined 2026-10-25 vs staged
     "§Eviction candidates" mined 2026-10-23)
   - provenance: round-37 `09b4d36e` introduced S330/S333/S334/S335/S346/S347/S363;
     round-38 `54e29520` introduced S352/S353 (verified by `git log -S'| <id> ' -- corpus/SOURCES.md`)
   - staging mtime 2026-10-24 23:33 -0300 vs round-37 commit 2026-10-25 05:03 -0300;
     the report's "203 rows / first staged id S330" bookkeeping is stale (lane now 250
     rows, ids through S509; round-37's own `.ufo/waves/round-37/assimilation/collisions`
     was 0 before the lane integrated the same research)
5. **File-target staleness**: 6 of 59 knowledge files already exist in the lane in
   extended/diverged form (`cmp` differs on all 6: kv-cache-reclamation-models,
   prefix-cache-reuse-models, sglang-docs-version-pinning, sglang-docs-version-pinning-
   amendment-2026-10-23, prefix-cache-reuse-models-amendment-2026-10-23,
   served-identity-crosswalk-amendment-2026-10-24-r16); all 3 amendment targets exist
   (content differs both directions, e.g. served-model-id-resolution 5050 B lane vs
   3213 B amendment).

## Defects

None. The staleness lives in the shokuknow staged package (outside the lane, not a
lane file; per province rule "out of province → report, never absorb" this is reported
here, not fixed). The lane's round-37/38 integration of the same research is committed
and internally consistent.

## Recommendation

`Assimilation: none` this round. Later round: re-stage (fresh ids past the lane max, or
quarantine the 9 colliding ids + 6 existing knowledge files + 3 amendment targets),
then adopt the served-identity crosswalk + runtime-health-surface process-column
cluster — strongest province fit, matches the open gap the province's own
`runtime-health-surface-processes.md` names.

## Written paths

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/A1Assim/assim.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/A1Assim.md`
