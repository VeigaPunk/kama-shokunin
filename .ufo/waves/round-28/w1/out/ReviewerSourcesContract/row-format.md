# Row format for a new `corpus/SOURCES.md` row (round-28 request-field outcomes)

Ground rules from `CORPUS.md` §"SOURCES.md — where a shokunin learns" (contract
`SOURCES-CONTRACT-v1`, frozen 2026-10-19) and the live kama registry. Verified
against `scripts/sources-census.sh` and `count-c1.py` clause (c); nothing was
modified.

## Placement and shape

- Rows live only inside the `## Registry` table — append after the last row
  (currently `S139`, line 151), before `## Paths` (line 153). A `#`-level
  heading ends the registry (`E12` fires on any `| S### |` row outside it).
- Exactly **11 cells** (`awk -F'|'` `NF==13`; `E01` otherwise). No `|`
  inside any cell; `—` allowed in `used-by`; `//` URLs fine since split is on
  `|` only.
- 0–3 leading spaces tolerated by the maintained parser; 4+ is indented code
  and the row is ignored. Keep column zero.
- `id` — `S` + ≥3 digits, next unused, never reused: **S140 onward** for
  round 28 (no S14x exists). The counter also requires the id absent from
  `corpus/SOURCES.md` at base 4179301f — any S140+ id satisfies that.

## Column order and allowed values

`| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |`

- **source** — `title — canonical URL` (or DOI; repo path/command for
  `own-work`). Kama code rows use
  `llama.cpp <file> @ 704366d76 (release b11755) — <URL>`. A `#L<line>`
  fragment is allowed in the URL (census strips it for dedup; the counter
  still sees it in the raw row).
- **kind** — enum `spec|docs|paper|code|tool|dataset|talk|book|community|own-work`
  (`E05`). server-schema.cpp rows: `code`.
- **tier** — `A|B|C` (`E06`), scoped to `scope`, never global. Source code at
  a pinned commit is primary → `A`. `community` is never A (`E10`).
- **scope** — what the tier applies to, stated with exclusions
  ("…at commit 704366d76 only; not other builds"). **Must be unique per row
  when the URL is shared**: `url_of` normalizes away scheme case, `#fragment`
  and trailing `/`, so all ~18 round-28 rows citing the same raw
  server-schema.cpp URL share one normalized URL; a repeated `(url, scope)`
  pair among non-rejected rows without `supersedes S###` in `teaches` → `E04`.
  Embed the field name and line in the scope.
- **anchor** — exact section/heading/line plus revision; never a bare URL.
  Kama convention for one declared line (S114–S130, S137):
  `server-schema.cpp line 44 @ 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad
  (block lines 44-48); raw sha256 <sha256 of fetched file>`. Carries both the
  counter's `line 44` spelling and the full hash containing `704366d`.
- **teaches** — one grounded learner benefit drawn from what the row's anchor
  shows. Rejected rows read `REJECTED: <reason>; flip: <what would flip>`
  (`W02` if under 8 chars). Corrections are new rows opening
  `supersedes S0NN —` — never edits (append-only rule 2; only `status`,
  `recheck`, `used-by` may change in place, logged in the round lesson).
- **status** — `queued|mined|rejected` (`E07`). Round-28 rows are cited by
  the SKILL.md table's `source` cell and the registry JSON, so `mined` is the
  honest end state. `mined` + `used-by: —` → `W03` warning; `queued` + `—` is
  the safe fallback but misstates a row that is in fact cited.
- **opened** — ISO date the row's author opened the source, ≤ today UTC
  (`E08`; today 2026-10-23).
- **recheck** — ISO date, `NNd`, or any letter-leading cadence matching
  `^[A-Za-z][A-Za-z0-9 _-]*$` (`on-release`, `every round`, `180d`; `E09`).
  Pinned-commit code rows carry `on-release` by convention (S035–S038,
  S114–S138).
- **used-by** — comma-separated lane-relative paths that **exist on disk**
  (`E11`, checked for `mined` rows) or `—`. At the measured tip all of
  `SKILL.md`, `registry/request-field-outcomes-r28.json` and
  `corpus/lessons/round-28.md` exist — list all three.

## Counter clause (c) — what the row must contain verbatim

From `count-c1.py` (`sources_rows`, `static_checks`): the counter matches
the **whole raw row line** as `srow` and requires, per registry entry:

- `srow` exists in the measured `corpus/SOURCES.md` and the id is absent at
  base 4179301f;
- substring `server-schema.cpp` anywhere in the line (registry `file`
  field must equal `server-schema.cpp`);
- substring `704366d` anywhere in the line — the full hash
  `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` contains it;
- regex `(#L44\b|\bL44\b|line 44\b)` for `line=44` — `#L44` in the URL
  fragment, `L44` or `line 44` in the anchor all satisfy it.

Separately, clause (b) (not this file's job, listed for completeness): the
pinned snapshot line `44` is `add((new field_num("n_predict",
params.n_predict))` — contains `new field_` and the literal `"n_predict"`
(verified, `.ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp`
lines 44–48; the block sets `set_hard_limits(-1, INT32_MAX)` at line 45,
aliases at 46–47, `set_desc` at 48). One row per field and per declaring
line — S114–S130 already model per-line rows; `source-misuse` control
refuses one S### cited by many rows or a row citing a description/other
field's line.

## Lesson `## Gate` — required per new row (contract rule 1)

`corpus/lessons/round-28.md` §Gate records for every new row:

1. the URL (the exact one in the `source` cell),
2. the access date (`opened`),
3. a ≤25-word quote with its location grounding `teaches`.

For a code-line row the natural quote is the declaring line itself, e.g.
`add((new field_num("n_predict", params.n_predict))` (4 tokens) at
"server-schema.cpp line 44 @ 704366d76"; record the raw sha256 equality to
the pinned snapshot (`1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050`)
as the fetch grounding. Non-author verification re-opens a sample.

## `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`

Resolves `kama` via `shokunin.conf`/`root` dirs to
`kama-shokunin/corpus/SOURCES.md` (missing registry → `missing`, exit 2).
Checks, per registry row (all read-only, stdout TSV `lane<TAB>code<TAB>detail`):

- **E01** row not exactly 11 cells · **E02** id not `S[0-9]{3,}` · **E03**
  duplicate id · **E04** duplicate normalized URL+scope among non-rejected
  rows whose `teaches` lacks `supersedes S###` · **E05/E06/E07** kind/tier/
  status enum violations · **E08** `opened` invalid or future ISO date ·
  **E09** `recheck` not ISO date / `NNd` / symbolic cadence · **E10**
  `community` at tier `A` · **E11** `mined` row `used-by` path missing on
  disk (separate pass, lane-dir relative) · **E12** `| S### |`-shaped row
  outside `## Registry`.
- **W01** tier-C `mined` with non-`—` used-by · **W02** `rejected` teaches
  <8 chars · **W03** `mined` with `used-by: —` · **W04** same normalized URL
  across different scopes.
- Exit: 0 clean or warnings-only; 1 any E finding; 2 env/missing registry.
  The ~17 extra rows sharing the server-schema.cpp URL will each emit `W04`
  — expected, exit stays 0; do not "fix" it by varying the URL (dedup is
  normalized) or by reusing `scope` (that turns W04 into E04).

## Worked example — `n_predict`, line 44 (registry `source.row: "S140"`, `file: "server-schema.cpp"`, `line: 44`)

| S140 | llama.cpp server-schema.cpp @ 704366d76 (release b11755) — https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L44 | code | A | n_predict request-field declaration at commit 704366d76 only: the declaring line and its hard limits and aliases; not runtime behaviour, not other fields' lines, not other builds | server-schema.cpp line 44 @ 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad, block lines 44-48 (set_hard_limits at 45, aliases 46-47, set_desc 48); raw sha256 1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050 | line 44 binds the n_predict request field to params.n_predict via new field_num; the following four lines bound it to -1..INT32_MAX, alias max_completion_tokens and max_tokens, and describe the cache-evaluation semantics at 0 | mined | 2026-10-23 | on-release | SKILL.md, registry/request-field-outcomes-r28.json, corpus/lessons/round-28.md |

Clause (c) trace: `server-schema.cpp` ✓ (title+URL+anchor), `704366d` ✓
(full hash), `#L44` fragment plus `line 44` ✓, id S140 not at base ✓.
Census: 11 cells, no pipes, `code`/`A`/`mined`, opened ≤ today, symbolic
recheck, all three used-by paths exist at the measured tip → clean (one W04
warning at most, shared with the other round-28 rows).
