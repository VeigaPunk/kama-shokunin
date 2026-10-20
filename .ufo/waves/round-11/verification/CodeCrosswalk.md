# CodeCrosswalk — advisory review of `measure.py crosswalk` mode (kama round 11)

Scope: `.ufo/waves/round-11/measure.py` crosswalk mode (`check_crosswalk`, lines 326-373, plus the crosswalk docstring lines 70-77 and selftest case 11/13 lines 507-537), and the provenance frontmatter of `corpus/knowledge/served-identity-crosswalk.md`.
Method: static reading only. No execution of `measure.py` or `--selftest`, no build, no lint, no tests. Line claims below were derived by reading the code and the entry bytes. One public URL was opened (S001, pinned revision) to test a frontmatter section anchor.
Advisory only. Non-author review remains a separate step.

Installs/updates: none. No tool was installed, upgraded, or invoked beyond `read`, `grep`, `glob`, and `bash` read-only listing. No repository file was modified except this report.

## Axes

1. Tally vs admission: does the output separate "existence/metadata counted" from "semantically admitted"?
2. Frontmatter provenance: are `source:`, `verified-at:`, `recheck:` present, unique, and accurate against the registry?
3. Guard coverage: does the wording guard catch the claim class it names?

## What is already correct

- Trio check (`_scan_supplement`, lines 144-175): on the entry, `source:`, `verified-at:`, `recheck:` each appear exactly once at column zero in lines 1-3 (confirmed by grep). No fence, duplicate, or indented-only false result.
- The docstring for crosswalk (lines 70-77) states that the check "is an existence/provenance count only: it does not judge wording, semantics, or the meaning of availability vs loaded-model claims — a human reviewer does." That disclaimer is accurate to the code.
- The live-claim guard passes the entry's current `verified-at` (`2026-10-20 (actual UTC review date …) — five public documentation pages re-opened read-only this round`). It contains no "live revalidated/revalidation" phrase, so no false positive.
- Missing entry → exit 1 with `entry=0` and a `missing-file` finding (lines 336-341). Unreadable entry → exit 2 (lines 342-343). No crash path.
- Registry rows exist for all five required IDs (S001 line 13, S010 line 22, S011 line 23, S012 line 24, S016 line 28) and for S031 (line 43), all tier A, `mined`. Entry body and frontmatter cite only these IDs.
- S001 anchors cited in the entry frontmatter exist on the pinned page. Fetched `tools/server/README.md` at commit `c0fd78626405c6d9b934efef0ec7291fcc20e3d6`: `### GET \`/v1/models\`` (line 1255), `### GET \`/models\`: List available models` (line 1995), and `## Sleeping on Idle` (line 2332). Located quote, line 2334: "The server supports an automatic sleep mode that activates after a specified period of inactivity" (15 words; fetched in this run). Section-name case differs from the entry's `§Sleeping on idle`; the anchor is real.

## Findings by severity

### M1 (medium) — the source-id "occurrence" tally is satisfied by the frontmatter alone

Evidence:
- `check_crosswalk` lines 354-360 counts `\bS###\b` over the whole text, including the frontmatter. It does not exclude the trio lines and does not count body or table citations separately.
- Entry line 1 (`source:`) contains S016, S001, S010, S011, S012, S031. Entry line 3 (`recheck:`) contains S001, S010, S011, S012, S016, S031. Each of the five required IDs therefore has ≥2 occurrences before the body is read. `missing-source-id` (line 359) cannot fire for this entry, even if the body cites none of them.
- Selftest case 11 (lines 507-522) asserts "crosswalk clean" on a fixture whose only source-ID occurrences are the `source:` line; the table has no IDs. The selftest therefore codifies frontmatter-only citation as a pass.

Why it matters: the payload `sources` field (line 370) reads as citation evidence. It is an occurrence count of IDs anywhere in the file. Under the wording "required source ids" (docstring line 74), a reader will take a clean result as "each required source is cited", which is a semantic claim the tool does not make.

Smallest repair (not applied): count occurrences only outside the trio/frontmatter lines, and report `source_id_mentions_frontmatter` and `source_id_mentions_body` separately. Require body ≥1 per ID. Add a selftest where the frontmatter lists all five IDs and the body mentions none; it must produce `missing-source-id`.

### M2 (medium) — the payload does not mark that a clean result is not admission

Evidence:
- The crosswalk payload (lines 370-372) returns `entry`, `fields`, `sources`, `table`, `table_rows`, `findings`, and `ok`. Nothing in the payload says `ok` is existence-only. The only disclaimer is the docstring (lines 72-77).
- `ok: true` with exit 0 is the same signal the provenance mode uses for "clean measurement". A reader of the JSON alone sees a pass.
- The entry itself has a section headed `## QUALITY clearance` (line 60) with a KQ1-KQ10 checklist ("KQ1: no present endpoint claim …"). That is author self-attestation of admission criteria. The tool does not check any of it, and the entry does not label it as self-check. The wave's own rule (outside non-author review remains separate) is not reflected in the entry.

Smallest repair (not applied): add `"semantic_admission": "not evaluated by measure.py; human non-author review required"` to the crosswalk payload, and rename `ok` to `existence_ok` in crosswalk mode. In the entry, retitle `## QUALITY clearance` to `## Author self-check (not admission)`.

### L1 (low) — `table_rows` is mislabeled

Evidence: `_markdown_table` (lines 178-188) counts every line that starts with `|` and has ≥2 pipes, including the header and the separator. On entry lines 17-22 there are 6 pipe lines: header (17), separator (18), and 4 data rows (19-22). The payload reports `table_rows: 6`, which a reader will take as 6 engine rows.

Smallest repair: count data rows only (exclude header and separator), or rename the field to `table_pipe_lines`.

### L2 (low) — the live-claim guard misses natural phrasings of the claim it names

Evidence: `_live_claim_re` (lines 125-130) matches only `live revalidated|live revalidation|revalidated live` followed by `today` or the run date. These phrasings are not matched and therefore pass silently:
- "re-opened live today" (no "revalidated" token)
- "verified live today"
- "live-checked 2026-10-20"

Separately, `NEGATION_WINDOW` (line 106) suppresses a real claim if any negation token appears in the 24 characters before it. For example, "not a re-check; live revalidated today" is suppressed.

The docstring (lines 50-58) says the guard is "literal, bounded" and "not a truth parser", which is honest. The gap is that crosswalk mode carries the same narrow guard and the selftest covers only "live revalidated today" (line 472).

Smallest repair: either document the literal scope in the crosswalk section, or add `live[\s-]+(?:re-?)?(?:checked|opened|verified|probed)` alternatives plus two selftest cases. The current entry passes either way.

### L3 (low) — the frontmatter is not reconciled with `corpus/SOURCES.md`

Evidence (current bytes):
- S001 registry row (SOURCES.md line 13) lists sections `§GET /health`, `§GET /v1/models`, `§GET /metrics`, with `opened 2026-10-19`. The entry frontmatter and body cite `§GET /models` and `§Sleeping on idle`. Both exist on the pinned page (see "What is already correct"), but the registry row does not list them.
- S010 registry row (line 22) lists `§Endpoints /v1/models` only. The entry frontmatter cites `§Endpoints /v1/models` + `§Models`; the Cited sources section adds `§Default model names`. Neither extra section is in the registry. I did not open this page.
- S011 (line 23), S012 (line 24), and S016 (line 28) show `opened 2026-10-19`. The entry says "re-opened 2026-10-20".
- S031 (line 43) is consistent with the entry.

The tool does not cross-check any of this. The registry may still be in-flight from the SourceCurator seat, so this may be a timing gap, not a defect. The entry's claim that it satisfies KQ6 ("cites an opened SOURCES.md row") is currently true only for the row IDs, not for the section anchors.

Smallest repair: SourceCurator updates the registry rows (sections and opened dates) before admission. Optional tool addition: verify each frontmatter S-ID exists in `corpus/SOURCES.md`. This is not required for this round.

### L4 (low) — the table check is shape-only, but its failure message implies content

Evidence: lines 361-364 check for any pipe table with a separator. The failure detail says "expected the per-engine route/identity table". Nothing checks engine rows, route columns, or header tokens. A table of unrelated content passes.

Smallest repair: reword the detail to "no markdown table with a separator line" so it does not imply a content check.

### I1 (info) — trio position and fence markers

- The trio scan is document-wide (line 345 passes `True` and scans everything), not limited to frontmatter at the top. A column-zero `source:` line anywhere in the body counts toward duplicates. Currently none exists.
- Only triple-backtick fences are recognized (line 159). A `~~~` fence would let fields inside it count.

No action required for the current entry.

## Residual risk

- With M1 unfixed, a crosswalk entry can pass with a frontmatter that lists five IDs and a table, even if no body text cites them. The tool would report clean. This is the exact tally-vs-admission conflation the target asked to separate.
- With M2 unfixed, the crosswalk `ok` will be read as admission by downstream consumers that do not read the docstring.
- The S001 anchors are grounded. S010, S011, S012, S016, and S031 anchors were not opened in this review. Their accuracy is not established by this report.
- The `verified-at` line asserts that five pages were re-opened on 2026-10-20 and that S001 sections were "verified at that pinned revision". The tool cannot check this. Only the S001 anchor existence was checked here.

## Verification gaps

- No execution: `measure.py crosswalk` and `--selftest` were not run. The table counts (L1) and regex behavior (L2) come from reading the code, not from runtime output.
- Not opened: S010, S011, S012, S016, S031 public pages. Section anchors and quotes for those are unverified here.
- Not reviewed: the provenance mode and `legacy-baseline.json`, which are out of this assignment's scope.
- Entry body claims (for example, llama.cpp "meta can be null while still loading") were not checked against sources.

## Summary

Crosswalk mode is honest in its docstring and its payload stays clean on this entry. Its clean result, however, is reachable from frontmatter plus any table (M1). Its `ok`/`entry` payload has no admission marker (M2). Lower-priority issues are the mislabeled `table_rows` (L1), a narrow live-claim guard (L2), missing registry reconciliation (L3), and shape-only table wording (L4). The entry's frontmatter is structurally correct and its S001 anchors are real.
