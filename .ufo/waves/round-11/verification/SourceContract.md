# Round-11 advisory — SourceContract (kama corpus/SOURCES.md vs baseline 2f7303c)

Advisory, non-author. No implementation or corpus edits made; no census/build/lint/test run; no endpoint or service probes. Public documentation opened read-only (`docs.ollama.com`, `developers.openai.com`).

## Scope and evidence basis

- Baseline: `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad` ("Integrate remote documentation; preserve local round log"), resolved in the kama lane repo `/home/vgpnk/Projects/shokunin/kama-shokunin`. The fleet repo (`/home/vgpnk/Projects/shokunin`) does not contain `2f7303c`; the lane repo does.
- Target: `kama-shokunin/corpus/SOURCES.md` working tree, sha256 `06ecc9926089ea51bedf7b39b8370a44fbb334e6f8e25e8fcc84575c57cb268c`, read 2026-10-20T03:45Z. The file changed on disk during review (a header edit was present at first read and later reverted; a trailing "Round-11 clarification" section was added). All findings below are against the later snapshot.
- Contract: `CORPUS.md` §SOURCES.md (contract v1): Rule 1 (new row needs URL, access date, ≤25-word located quote in the round `## Gate`), Rule 2 (append-only: only `status`, `recheck`, `used-by` change in place; every such change logged old→new in the round lesson; correction = new row whose `teaches` opens `supersedes S0NN —`), Shape (Registry, Paths, Search log, Leads).
- Row counts (read-only observation, not the census): baseline 30 rows (S001–S030), current 31 (S031 added). No duplicate ids observed.
- Install/update record: none. No tools installed or upgraded.

## Diff audit (baseline → current)

Only the following changed. All other registry bytes are identical to baseline.

| id | change | allowed? |
|---|---|---|
| S001 | used-by `+ corpus/knowledge/served-identity-crosswalk.md` | yes (used-by) |
| S010 | used-by `+ corpus/knowledge/served-identity-crosswalk.md` | yes (used-by) |
| S011 | status `queued→mined`; used-by `— → runtime-health-surface-matrix.md, served-identity-crosswalk.md`; recheck `90d` unchanged | yes |
| S012 | status `queued→mined`; used-by `— → runtime-health-surface-matrix.md, served-identity-crosswalk.md`; recheck `90d` unchanged | yes |
| S016 | status `queued→mined`; used-by `— → served-identity-crosswalk.md`; recheck `90d` unchanged | yes |
| S031 | new row, appended after S030 | new row; see obligations |
| header prose | baseline bytes restored in current file (no hunk at lines 1–9) | n/a — reverted |
| Search log | one bullet appended dated 2026-10-20 (UTC) | append; allowed |
| Trailing section | `## Round-11 clarification (2026-10-20 UTC)` appended after Leads | **not in contract Shape** — see F2 |

`opened` cells for S001/S010/S011/S012/S016 keep 2026-10-19. That is compliant with Rule 2 (`opened` is not an editable cell); the 2026-10-20 reopen is recorded only in the Search log. No `anchor`, `teaches`, `source`, `kind`, `tier`, `scope` cell changed on any existing row (checked field-by-field against baseline for all five touched rows).

## Findings (ordered by severity)

### F1 — HIGH (parent-owned): round lesson is missing; obligations unmet

- `corpus/lessons/round-11*` does not exist (`ls` → no such file). The contract requires `lessons/round-11.md` `## Gate` (Rule 1) and an old→new change log (Rule 2). The kama prompt also requires `## Mistakes` (§2b.3) and a sourced claim (§2b.4).
- Dangling pointers to the missing lesson: SOURCES.md line 70 ("changes and new-row quote are recorded in `lessons/round-11.md` §Gate"); the Search-log bullet dated 2026-10-20 ("Round 11 reopened…"); `knowledge/served-identity-crosswalk.md` `recheck:`/body; `QUALITY.md` KQ12/KQ13 cite `lessons/round-11.md` Gate/Mistakes. Until the file exists, none of these resolve.
- Smallest repair: create `corpus/lessons/round-11.md` containing:
  - `## Gate` row for S031: URL `https://docs.ollama.com/api/tags`; accessed 2026-10-20; quote (≤25 words, located at OpenAPI `components/schemas/ModelSummary/properties/remote_host`, page §OpenAPI): **"URL of the upstream Ollama host, if the model is remote"** (11 words). Supporting quote, same page, `ModelSummary` description: **"Summary information for a locally available model"** (7 words) — this is the S011 wording S031 supersedes. Optional: `remote_model` description "Name of the upstream model, if the model is remote" (10 words).
  - `## Gate` rows for S011/S012/S016 status changes naming the reopen date and the quote that grounds the teaches (S012 verified below; S016 verified below; S011 verified below via the same tags page).
  - Old→new change log: S001 used-by +crosswalk; S010 used-by +crosswalk; S011 `queued→mined`, used-by `—→matrix,crosswalk`; S012 `queued→mined`, used-by `—→matrix,crosswalk`; S016 `queued→mined`, used-by `—→crosswalk`. Recheck: no change on any row.
  - `## Mistakes`: at least one row (class · evidence · captured-by · fix), or a pasted sweep showing none. Candidate from this round: S011 `teaches` ("Lists locally available models") shipped in round 10 without reading the schema's `remote_*` fields — class `stale-premise`/`scope`, captured-by QUALITY.md KQ13 (currently unmet), fix = S031 supersession plus KQ13 gate.
- Census: not run by me (no-checks assignment). Parent should run `scripts/sources-census.sh validate` (or the CORPUS.md census) once after the lesson lands; expected: used-by paths exist (they do, see F4).

### F2 — MEDIUM: trailing section outside contract Shape

- SOURCES.md lines 73–79 (`## Round-11 clarification (2026-10-20 UTC)`) follow `## Leads (unopened)`. Contract Shape is Registry / Paths / Search log / Leads. The section also re-describes the round-10 header sentence and points at the missing lesson.
- The same content is already recorded in the Search-log bullet. Smallest repair: delete the trailing section (the Search-log bullet already carries the reopen, the S031 addendum, and the matrix used-by note). If a note must stay, fold it into that bullet — do not add a heading.

### F3 — LOW: S031 `teaches` states an inference as a page fact

- S031 teaches: "list membership does not prove local residency". The page does not say this verbatim. It is a reasonable inference from `remote_model`/`remote_host` being present on list entries. Contract §teaches requires "one grounded learner benefit".
- Smallest repair: keep the row, but the lesson Gate should quote the two `remote_*` descriptions and label the residency sentence `[INFERENCE]`. No registry edit needed (append-only would require a further supersession row to change teaches).

### F4 — INFO (compliant): used-by paths and citations

- All `mined` rows' used-by paths exist on disk: `corpus/knowledge/served-identity-crosswalk.md` (14,658 B, 2026-10-19 23:23) and `corpus/knowledge/runtime-health-surface-matrix.md` (7,139 B).
- Reverse-citation check: the crosswalk body cites S001, S010, S011, S012, S016, S031 (source line, Crosswalk table, failure cases 6–7, kama use); the matrix cites S011/S012 only inside its appended `## Correction — round 11` section (matrix lines ~42–56). The S011/S012 used-by entries therefore depend on that appended matrix section. If that section is removed, those two used-by entries become false.

### F5 — INFO: S031 duplicates S011's URL

- S031 and S011 point to the same `docs.ollama.com/api/tags` page. Contract does not forbid this; the `supersedes S011 —` opener makes the relationship explicit. No defect.

## Source spot-checks (public docs opened this round)

- `https://docs.ollama.com/api/tags` (opened 2026-10-20, markdown alternate of OpenAPI 3.1.0 / info.version 0.1.0): ModelSummary description "Summary information for a locally available model"; `remote_model` "Name of the upstream model, if the model is remote"; `remote_host` "URL of the upstream Ollama host, if the model is remote". **S031 supported; S011 "locally available" wording confirmed as the page's own schema text, so supersession is grounded.**
- `https://docs.ollama.com/api/ps` (opened 2026-10-20): 200 description "Models currently loaded into memory"; `expires_at` "Time when the model will be unloaded"; `size_vram` "VRAM usage in bytes"; `context_length` "Context length for the running model". **S012 teaches supported.**
- `https://developers.openai.com/api/reference/resources/models/methods/list` (opened 2026-10-20): "Lists the currently available models, and provides basic information about each one such as the owner and availability." `shutdown_date` "The date when the model will shut down, or null if not announced." **S016 teaches supported; "does not establish local-server health or loaded weights" is consistent with the page, which has no loaded-state field.**
- Not re-opened by me: S001 (llama.cpp README, large) and S010 (Ollama OpenAI compatibility). The Search-log claim that they were reopened is unverified here.

## What is already correct

- Registry cell discipline: only status/used-by changed on existing rows; recheck and opened untouched; no anchor/teaches rewritten.
- S031 row shape: 11 cells, `kind`=docs, `tier`=A (curation within scope), `status`=mined with an existing used-by path, `opened` ISO, `recheck` 90d, `teaches` opens `supersedes S011 —` as Rule 2 requires, no `|` inside cells.
- Header prose restored to baseline bytes.
- Search-log bullet names the actual review date (2026-10-20 UTC) and explains that `opened` keeps round-10 dates.

## Residual risk and verification gaps

- No round lesson exists, so Rule 1 and Rule 2 conformance cannot be shown as satisfied until F1 lands. This is the one item that makes the wave non-conformant as shipped.
- The sibling-editable file changed during this review; re-check the sha256 above before acting on F2.
- Census command not executed (assignment forbids checks); the parent must run it after F1/F2.
- Advisory only; outside non-author review remains separate.
