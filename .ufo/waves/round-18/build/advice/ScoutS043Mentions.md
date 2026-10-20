VERDICT: confirm — R3 holds and is the only remaining un-annotated S043 credit: 29 `S043` occurrences across 8 tracked docs, one of which (`corpus/README.md`) has no `S047` anywhere and still attributes "the SIGINT/SIGTERM shutdown path and exit statuses" to S043 alone.

# Scope and method
- Read-only. Lane tip at investigation time: `e75cf680b53484a61709ee1b2787d8dbc6419f74` (`git rev-parse master`), identical to the round-start commit; all eight files below are tracked (`git ls-files`).
- Sweep: `grep -rn "S043" . --exclude-dir=.ufo --exclude-dir=interactive-sessions --exclude-dir=.git --exclude-dir=.jj` → 8 files, 26 lines, 29 occurrences. Case/variant sweep `grep -rnE '\bS0*43\b' … | grep -v S043` → 0 hits (no `S43` form).
- No `S043` in any code, test, registry or receipt file: the tool writes `source_binding` rows as `row: null` (`SKILL.md:592`), so every mention is documentation prose.
- Nothing was started, bound, installed or edited. The only file written is this Report.

# Census (occurrences per file)
| File | Occurrences | Lines |
|---|---|---|
| `corpus/knowledge/llamacpp-loading-lifecycle.md` | 3 | 153, 174, 218 |
| `corpus/lessons/round-17.md` | 11 | 39, 62, 63, 78, 222, 223, 224, 225, 309 (×3 on 309) |
| `corpus/lessons/round-17-verifier-spotcheck.md` | 7 | 177 (×2), 191, 210, 215, 219, 233 |
| `corpus/SOURCES.md` | 3 | 55, 59, 169 |
| `SKILL.md` | 2 | 573, 592 |
| `corpus/README.md` | 1 | 238 |
| `LOG.md` | 1 | 1040 |
| `SCORECARD.md` | 1 | 716 |

# Classification
Class A = superseded-by-S047 already noted in the same document (the note itself, or a correction in the same section/file). Class B = mention is not a source credit (census warning, artifact name, evidence pointer). Class C = still credits S043 alone for shutdown/exit statuses with no S047 in the document.

## C — the one gap (R3 target)
- `corpus/README.md:238` — "the SIGINT/SIGTERM shutdown path and exit statuses (S043)" (8 words). The row sits in `## Round-17 graded fields and fail-capable live checks` (heading at 234) and reads in full: "the exact `/health` ready body in code (S042), the SIGINT/SIGTERM shutdown path and exit statuses (S043), Python returncode semantics (S044), three v2 live runs (S046); deepens the round-16 entry, no new ground".
  - `grep -n "S047" corpus/README.md` → no output; `grep -n "supersed\|lost\|start_loop" corpus/README.md` → no output. The document's only round-17 correction (`corpus/README.md:230-232`) covers the loading-gate OPTIONS scope, not the signal rows.
  - Independently identified by the outside check: `corpus/lessons/round-17-verifier-spotcheck.md:232-233` — "attributes 'the SIGINT/SIGTERM shutdown path and exit statuses' to S043 alone. Append a pointer to S047." (18 words); and `:215` — "which still cites S043 for exit statuses and does not mention S047" (13 words).
  - Severity: map pointer, not a false entry — `corpus/lessons/round-17-verifier-spotcheck.md:216`: "It is a map pointer, not a false entry." (9 words). S043 still grounds the handler-install order and the second-signal `exit(1)`; only the first-SIGTERM-ends-in-0 claim needed scoping.

## A — annotated (no action needed for R3)
- `corpus/knowledge/llamacpp-loading-lifecycle.md:218` — "(S047, supersedes S043; static ordering, not reproduced)" (6 words). The note itself, in the same appended §Round-17 section.
- `corpus/knowledge/llamacpp-loading-lifecycle.md:174` — "(S043). The first signal calls `ctx_server.terminate()` (519-523), which stops" (11 words). Section-level, not inline: the correction is 44 lines later at 218 in the same section. Consistent with the lane's append-only correction style; flagged only for distance.
- `corpus/knowledge/llamacpp-loading-lifecycle.md:153` — "S043" in the provenance-supplement list of sources; S043 remains the ground for the handler-install ordering, so the listing is still accurate; same section carries 218.
- `corpus/lessons/round-17.md:39` — "returncode 0 and no SIGKILL (S043, S044), ownership-gated `teardown_port_closed`" (4-word span); the declared C2 claim as written before the correction. Same file's §Corrected (222-225) records the supersession.
- `corpus/lessons/round-17.md:62` — "admit, scoped (S043)" (3 words). Corrected by `:222` — "S043's `teaches` overstated" (3 words) — and `:224` — "New row **S047 supersedes S043**; the knowledge entry carries" (9 words).
- `corpus/lessons/round-17.md:63` — "A second signal exits 1 | admit (S043)" (7 words). Still correct under S047, which says the lost signal's successor "exits 1" (`corpus/SOURCES.md:59`); not stale, and the same file carries the supersede note.
- `corpus/lessons/round-17.md:78` — "and S043 (`server.cpp` signal path); the rows" (7 words) — describes the receipt's `row: null` bindings; same file carries 224/309.
- `corpus/lessons/round-17.md:222-225` — the correction paragraph; `:225` reads "an appended correction. S043's cells are untouched (KQ22)." (8 words).
- `corpus/lessons/round-17.md:309` — M8 row: "superseding row S047; knowledge correction." (5 words). Explicit.
- `corpus/lessons/round-17-verifier-spotcheck.md:177` — "admit (S043), superseded in-round by S047" (7 words); the same cell adds "S043's unscoped claim overstates the code" (6 words span).
- `corpus/lessons/round-17-verifier-spotcheck.md:210` — "A stale reading (S043) was superseded by a stronger row (S047)" (12 words).
- `corpus/lessons/round-17-verifier-spotcheck.md:219` — "The one gate error (the S043 admit) was caught" (9 words).
- `corpus/SOURCES.md:59` — S047's `teaches`: "supersedes S043 — a first SIGTERM ends in `return 0` only once `start_loop` is running" (17 words). The registry-level supersede note.
- `SOURCES.md:55` — S043's own row, `teaches`: "A first SIGTERM after the handler is installed ends in `return 0`" (12 words). Its immutable cells carry no marker; the supersede lives in S047's row four lines below. This matches existing registry precedent — `SOURCES.md:121`: "S040 supersedes S021 by row; S021's cells stay" (9 words), with S021 (`:33`) likewise unmarked. Not a defect.
- `SKILL.md:592` — "their rows are S042 and S043/S047" (7 words), in the appended round-17 falsify-correction paragraph.
- `SKILL.md:573` — capability row's pinned cell: "sources bound in-receipt (`source_binding`: llama.cpp 704366d76 spans, S036, S042, S043)" (10-word span). Names S043 alone, but the same section's correction at 592 supersedes that cell's reading (says the spans carry `row: null`). Annotated at section level; no edit needed for R3.
- `LOG.md:1040` — "S047 supersedes S043 (lost-signal window)" (5 words).
- `SCORECARD.md:715-716` — "Rows 46 → 47 (S047 supersedes S043; A 43 → 44, mined 36 → 37)." (14 words).

## B — non-credit mentions
- `corpus/SOURCES.md:169` — "S043 shares S037's URL (census W04) with a different scope and anchor" (13 words). Census hygiene, not an exit-status credit.
- `corpus/lessons/round-17-verifier-spotcheck.md:191` — "with `W04 S031` and `W04 S043` (the shared" (8 words). Same census warning.
- `corpus/lessons/round-17.md:223` — `ReopenS043` is an advice-artifact name; `:309` carries the same name plus two genuine S043 cites.

# Consequence for the frontier step R3
- Only `corpus/README.md` needs the pointer; every other document already carries an S047 reference. A second edit there would duplicate advice already recorded at `corpus/lessons/round-17-verifier-spotcheck.md:232-233`.
- Placement: the §Round-17 section is the file's last section (file ends at line 245), so an appended correction paragraph goes after line 245. That mirrors the existing house form at `corpus/README.md:230` — "§Correction — round 17 (loading-gate scope, OPTIONS; routed by `lessons/round-16-verifier-spotcheck.md` defect 4)." (13-word span) — which corrects row text by appending prose rather than editing the row.
- Draft text for L1 (advice only, not applied): a paragraph headed `§Correction — round 17 (signal rows; routed by `lessons/round-17-verifier-spotcheck.md` R3).` stating that line 238's row names S043 for the SIGINT/SIGTERM shutdown path and exit statuses, that S047 supersedes S043 for the first-SIGTERM claim (a signal after handler install at `server.cpp:534` but before `start_loop` sets `running = true` at `server-queue.cpp:279` is lost, the server keeps serving, and a later signal exits 1), and that S043 still grounds the handler-install order and the second-signal `exit(1)`.
- Do not touch S043's `teaches`/`anchor`/`scope` cells: `corpus/lessons/round-17.md:225` records "S043's cells are untouched (KQ22)". A pointer in the mutable `status`/`recheck` cells would be legal under the append-only guard's mutable set (`SKILL.md` row: "a changed cell outside `status`/`recheck`/`used-by`"), but R3 asks for the README pointer, and the S047 row already carries the supersession — leaving S043 unmarked is registry convention (S021/S040, S011/S031), not a defect. [INFERENCE] that L1 will prefer the convention over an extra cell edit.

# Limits
- Line numbers reflect the committed lane tip `e75cf680…`; if build-wave seats land files in the same docs, numbers can shift (only `SKILL.md` and `corpus/lessons/round-18.md` are plausible movers; the R3 target line is late in a file with no round-18 section yet).
- `.ufo/waves/**` was excluded per the item, so wave advice and round-17 receipts were not censused; receipts carry `row: null` by design (`SKILL.md:592`), so no S043 credit can hide there.
- No git blame was used (`git blame -L 238,238` returned no output in this checkout); provenance of line 238 was established from content and the spotcheck, not from history.
- No external source was opened this round: the question is internal-consistency, and the S047 code facts are already pinned at `corpus/SOURCES.md:59` and re-verified by `build/advice/ScribeS047Gate.md`.

# Installs
None.
