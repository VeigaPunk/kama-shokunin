# Sources — SOURCES.md registry update (round 14)

**Seat:** `KamaR14.Sources` (executor, leaf)
**Owned file:** `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md` (only file edited)
**Date:** 2026-10-20 UTC (actual access date for both URLs below)
**Assignment:** re-open S011/S012/S031 URLs, add S034 only if genuinely needed, prefer
used-by additions for S012/S031, append a bounded search note, keep every immutable cell.

## Opened locations

1. `https://docs.ollama.com/api/tags` — opened 2026-10-20 (UTC); the site served its own
   published markdown alternate (`/api/tags.md`) of the same OpenAPI excerpt. Covers S011 and
   S031. Still `openapi: 3.1.0`, `info.version: 0.1.0`, `GET /api/tags`, `ListResponse` →
   `ModelSummary`. Quotes, each ≤25 words:
   - `ModelSummary.description`: “Summary information for a locally available model” (7 words).
   - `digest`: “SHA256 digest identifier of the model contents” (7 words).
   - `remote_model`: “Name of the upstream model, if the model is remote” (10 words).
   - `remote_host`: “URL of the upstream Ollama host, if the model is remote” (11 words).
2. `https://docs.ollama.com/api/ps` — opened 2026-10-20 (UTC); same alternate-markdown
   delivery. Covers S012. Still `openapi: 3.1.0`, `info.version: 0.1.0`, `GET /api/ps`,
   `PsResponse` → `Ps`. Quotes, each ≤25 words:
   - page summary: “Retrieve a list of models that are currently running” (9 words).
   - `expires_at`: “Time when the model will be unloaded” (7 words).
   - `digest`: “SHA256 digest of the model” (6 words).

Schema shape matches the recorded S011/S012/S031 rows; nothing was added to their
anchor/teaches/status/opened/recheck cells.

## Registry change (old → new, used-by only)

- **S012** old: `corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/served-identity-crosswalk.md`
  → new: `corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/served-identity-crosswalk.md, corpus/knowledge/ollama-evidence-replay.md`
- **S031** old: `corpus/knowledge/served-identity-crosswalk.md`
  → new: `corpus/knowledge/served-identity-crosswalk.md, corpus/knowledge/ollama-evidence-replay.md`
- **S011** (same tags URL): all cells unchanged, including used-by; the remote caveat lives in
  S031 and the replay entry is the local/loaded reconciliation, so S012+S031 are the two rows
  credited.
- All other rows and cells unchanged. `opened` dates were not rewritten. Registry row count
  stays 33 (S001–S033). No S034 was added:
  the existing three rows already name every field the replay classifier consumes
  (`name`, `model`, `digest`, `remote_model`, `remote_host`, plus the ps list/`expires_at`
  fields), so a new row would duplicate scope.

## Search-log append

One bullet, “2026-10-20 (UTC) — round-14 offline replay re-open”, placed between the round-13
bullet and `## Leads`. Counts: 2 URLs screened, 3 existing rows covered, 0 new rows, 0 excluded.
It records the quoted schema snippets per URL, the matching schema version, and the stop
condition.

## Source-vs-inference boundary

- The opened pages **define fields and list semantics**; they **do not define** kama's
  digest-join policy, verdict precedence, remote-over-digest precedence or duplicate/conflict
  classification. Those replay rules are `[INFERENCE]` / own-work and are marked so in the new
  search note and in the appended round-14 paragraph.
- `remote_model`/`remote_host` quotes support only the conditional remote-entry wording; the
  “membership is not proof of local residency” conclusion remains the already-labeled
  inference carried by S031 and the crosswalk, not page text.
- The ps wording “currently running” describes a live response; an exported capture read
  offline is a historical artifact, so no current-liveness/readiness claim is made anywhere.
- No digest join is documented upstream; the classifier's exit-0 meaning is metadata
  correspondence only, never readiness.

## Appended clarification paragraph

`**Round-14 used-by addition (2026-10-20 UTC).**` after the round-13 paragraph records the same
old → new used-by values, S011's unchanged cells, the no-S034 decision, and the
`[INFERENCE]`/own-work status of the join policy.

## Limits and risks

- `corpus/knowledge/ollama-evidence-replay.md` was absent at registry-edit time
  (`KamaR14.ReplayKnowledge` in flight) but landed afterwards at the exact assigned path
  (observed 2026-10-20, 16,273 bytes), so both used-by references resolve; its `source:` line
  cites S012 and S031 and not S011, matching the credited rows. The E11 ordering concern is
  closed without further registry edits.
- Only the two documentation URLs were fetched; `localhost:11434`, probes and all runtime
  surfaces were untouched. No acquisition feature, no writes beyond this owned file and this
  report.
- The documentation host served its markdown alternate automatically; content is the site's
  own published OpenAPI excerpt, not a third-party mirror.
- No verification, census, build, lint, formatter or smoke run was performed (leaf contract).
  L1 should run `sources-census.sh validate` and its usual link/table checks after integration.
- Preexisting census warning `S031 duplicate url docs.ollama.com/api/tags across scopes` was
  not introduced or modified this round.

## Tooling

No tools installed or updated.
