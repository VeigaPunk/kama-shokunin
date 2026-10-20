# Review — S012 `teaches` wording (round-15 verifier defect 6)

**Seat:** read-only reviewer. **Verdict (advice only; L1 integrates and runs measurements):** the appended registry note is sufficient for defect 6 as stated; a superseding row is not required. A superseding row becomes mandatory only if L1 decides to narrow the cell itself (then Rule 2 requires it). Exact paste-ready text for both branches is below.

**Axis relevance:** this is a corpus-provenance precision item. It changes no probe verdict, no calibration measurement and no operability capability, so it earns no calibration or operability credit by itself.

## 1. Defect and cell

- `corpus/lessons/round-15-verifier-spotcheck.md:170`: “Existing S012.teaches summarizes a separation from the available list, while the reopened ps page alone describes the running list.” (20 words)
- `corpus/SOURCES.md:24` (S012): “Separates running models from the available-model list and exposes digest, context length, VRAM use, and expiry.” (18 words)
- The round-10 Gate quote for S012 is `corpus/lessons/round-10.md:72`: “Models currently loaded into memory” — it grounds the loaded-list/field half, not the separation clause.

## 2. Reopened source (2026-10-20)

- `https://docs.ollama.com/api/ps` — HTTP 200, 291108 bytes, fetched 2026-10-20.
- Published OpenAPI behind the docs page: `https://docs.ollama.com/openapi.yaml` — HTTP 200, 87346 bytes; `openapi: 3.1.0`; `info.version: 0.1.0`. The rendered page and the YAML agree on both quotes below.
- `GET /api/ps` summary: “Retrieve a list of models that are currently running” (9 words).
- `GET /api/ps` 200 response description: “Models currently loaded into memory” (5 words).
- The ps row items are the `Ps` schema; the fields relevant to the cell are `digest` (“SHA256 digest of the model”), `context_length` (“Context length for the running model”), `size_vram` (“VRAM usage in bytes”) and `expires_at` (“Time when the model will be unloaded”).
- Negative sweep for available-list wording inside the operation: bounded extraction from `^  /api/ps:` to `^  /api/show:` in the published OpenAPI, `grep -ci available` → `0` (grep exit 1). In the rendered page's extracted visible text the sole `available` line is “Use this file to discover all available pages before exploring further.” — Mintlify boilerplate, not API prose.
- The available-list wording belongs to S011, not ps: `GET /api/tags` 200 description “List available models” (3 words); `ModelSummary` description “Summary information for a locally available model” (7 words).

**Conclusion:** the ps page alone grounds the running/loaded list and the field claims; the separation clause is a two-source synthesis with S011. It is true, but it is not a ps-only sentence.

## 3. Contract analysis

- Rule 1 (`CORPUS.md:112-115`): “The round lesson's `## Gate` records, for every new row, the URL, the access date, and a ≤25-word quote” grounding `teaches`. The round-10 quote grounds only the ps half.
- Rule 2 (`CORPUS.md:116-118`): “Only `status`, `recheck` and `used-by` change in place” (7 words); “A correction is a new row whose `teaches` opens `supersedes S0NN —`” (12 words).
- Rule 4 (`CORPUS.md:123-125`): “a short registry of opened, honestly tiered rows beats a long one.” (13 words)
- The cell is not false; defect 6 asks for an explicit synthesis mark, not withdrawal of the claim. Appending prose changes no cell and triggers no Rule 2 correction. The lane already uses this form: `corpus/SOURCES.md:70-72` says “No row, cell or line above changes, and these paragraphs are correction prose, not open leads.” (18 words)
- This exact remedy has verifier precedent: round-11 D4 asked to “clarify that `supersedes S011` is registry supersession, not a claimed upstream change” (13 words, `corpus/lessons/round-11-verifier-spotcheck.md:221-224`); the lane answered with the D4 prose note, not a new row, and the round-12 verifier accepted it — “D4 accurately labels kama's locality conclusion as inference and its S031/S011 supersession as lane-registry scope” (17 words, `corpus/lessons/round-12-verifier-spotcheck.md:108`).
- The matrix already performs the attribution correctly in appended prose: `corpus/knowledge/runtime-health-surface-matrix.md:47-49` grounds tags “List available models” in S011 and ps “Models currently loaded into memory” in S012 separately, instead of folding both into one row's cell.
- S031's superseding row (`corpus/SOURCES.md:43`: “supersedes S011 — available inventory may include `remote_model`/`remote_host`”, 9 words) corrected a substantive implication (local residency). It proves the row mechanism exists; it does not make a row mandatory for an attribution mark.
- A new ps row would duplicate the URL (`W04`/`E04` mechanics at `scripts/sources-census.sh:645-649`), add no new source ground, and require id/status/used-by/Gate coupling. The note avoids that surface. If L1 chooses a row anyway, `E12` requires it inside `## Registry` — before `## Paths` at `corpus/SOURCES.md:48` (`scripts/sources-census.sh:611-622`).

## 4. Exact text — primary recommendation

Append at the end of `corpus/SOURCES.md` after the round-15 supplement (currently `corpus/SOURCES.md:80-93`), leaving every existing cell untouched:

```markdown
**2026-10-20 (UTC) — S012 wording note (round-15 verifier defect 6; registry prose only, not a lead).** No registry row or cell above changes. Reopened `https://docs.ollama.com/api/ps` as its published OpenAPI 3.1.0 text, info.version 0.1.0: `GET /api/ps` summary “Retrieve a list of models that are currently running”; 200 response description “Models currently loaded into memory”. The `/api/ps` operation contains no available-list wording (bounded extraction between `/api/ps:` and `/api/show:` in `https://docs.ollama.com/openapi.yaml`, `grep -ci available`, printed 0; in the extracted visible text of the rendered page the sole `available` is the Mintlify boilerplate “Use this file to discover all available pages before exploring further.”). S012's `teaches` clause “Separates running models from the available-model list” is therefore **cross-source synthesis [INFERENCE]** with S011 (`https://docs.ollama.com/api/tags`: 200 “List available models”; `ModelSummary` “Summary information for a locally available model”), not a ps-only assertion; the ps-only ground for the cell is the running/loaded list plus the `Ps` fields `digest`, `context_length`, `size_vram` and `expires_at`. S012's `status`, `tier`, `scope`, `opened` and `recheck` cells remain unchanged; any later `used-by` addition is logged old→new under Rule 2. If a later round chooses to narrow the cell itself, it MUST append a row whose `teaches` opens `supersedes S012 —`; rewriting the cell is not permitted.
```

## 5. Rule 5 companion

The reopen is a bounded search; insert this bullet under `## Search log`, before `## Leads (unopened)`:

```markdown
- **2026-10-20 — S012 wording re-open.** Question: does the `/api/ps` page alone document a separation from the available-model list? Where: `https://docs.ollama.com/api/ps` (published OpenAPI 3.1.0, info.version 0.1.0) and `https://docs.ollama.com/openapi.yaml`. Identified 1, screened 1, included 0 new rows, excluded 0; the ps operation documents only the running list, so the separation is marked as cross-source synthesis with S011 in the registry correction note. Stop: the ps-only wording and the absence sweep are located.
```

## 6. Conditional alternative — only if L1 narrows the cell

If the decision is that S012's `teaches` must no longer claim the separation, a note cannot fix it; Rule 2 requires a new row. Exact row, to be inserted after S034 (`corpus/SOURCES.md:46`) and before `## Paths` (`corpus/SOURCES.md:48`) so it is inside `## Registry`:

```markdown
| S035 | Ollama List running models (loaded-list attribution) — https://docs.ollama.com/api/ps | docs | A | Ollama model inventory currently loaded into memory | OpenAPI 3.1.0, info.version 0.1.0; List running models; GET /api/ps; summary and 200 response description | supersedes S012 — confined to the available-vs-running clause: ps alone says “Retrieve a list of models that are currently running” and “Models currently loaded into memory”; the separation from the available-model list is cross-source synthesis [INFERENCE] with S011 (`/api/tags`), not ps's own wording; S012's field claims stand. | queued | 2026-10-20 | 90d | — |
```

Branch notes:

- The row is 11 columns (`NF=13` under `awk -F'|'`), matching the registry shape; the `teaches` cell contains no `|`.
- Scope is S012's scope verbatim (`corpus/SOURCES.md:24`), so no `W04`; the `supersedes S012` token suppresses `E04` for the duplicate URL+scope (`scripts/sources-census.sh:645-649`).
- `status: queued` / `used-by: —` until a round file cites S035; then change both in place (Rule 2 allows `status`, `recheck`, `used-by`) and log old→new. If the round-16 lesson cites it, `used-by: corpus/lessons/round-16.md`; the census's missing-path check requires that file to exist.
- Rule 1 Gate entry for S035: URL `https://docs.ollama.com/api/ps`, access date 2026-10-20, quote “Retrieve a list of models that are currently running” (9 words) at the `GET /api/ps` summary.
- Do not also append the §4 note if the row is used; the row's `teaches` is the mark. The §5 search-log bullet still applies.
- I did not run the census against this row (read-only seat); the `E04`/`W04`/`E12` expectations are read from the validator source, not measured. [INFERENCE] L1 should run the census after insertion.

## 7. Residual risk and verification gaps

- The note is prose; no machine check enforces that a future reader treats the separation as synthesis. If a machine-visible mark in the row itself is required, only the §6 row delivers it.
- S011 has the reciprocal clause: `corpus/SOURCES.md:23` says “availability is distinct from running state” (7 words), while the tags operation's own wording is “List available models” / “Summary information for a locally available model”. No running-state wording was found in the tags block: bounded extraction from `^  /api/tags:` to `^  /api/ps:` in the published OpenAPI, `grep -i 'running\|loaded\|memory'` → no match (grep exit 1). Defect 6 names only S012. If L1 wants the pair marked, add one sentence to the §4 note; I did not expand the primary text beyond the routed defect. [INFERENCE] the verifier would apply the same treatment to S011.
- The docs page exposes only `info.version 0.1.0`; these quotes are dated 2026-10-20 and S012's 90d recheck is the freshness guard.
- Read-only seat: no pre-existing lane file was changed; only this new report was written. No census/harness/test was run against the lane and no install was made; the `/tmp` files are fetches/scratch outside the lane.
- No `.ufo/interactive-sessions/`, session/history store, credential store or environment dump was read; evidence is the public pages plus the lane corpus and validator-source files cited above.
