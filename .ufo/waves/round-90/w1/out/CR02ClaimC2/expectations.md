# CR02ClaimC2 — pre-registered expectations (written before any fixture run)

Counter under attack: `tools/round90-reason-rows.py` at 6f6d7873 (sha256 fa4c3177…, identical at M2 2ee0b55f).
Fixture SKILL.md = real SKILL.md at M2; fixture `tools/kama-probe.sh` = a two-line stub whose sha is *not* the
real probe's; receipt lines are rebuilt to that stub sha unless a case says otherwise. Fixture repo is a fresh
`mktemp -d` git repo under the seat scratch.

| case | mutation | my expected counter result | my expected judgement |
|---|---|---|---|
| A0 | none (faithful copy) | `documented=23 rows=24 bound=24 unbound=0 missing=0 duplicates=0`, exit 0 | positive control |
| A1 | all table rows wrapped in one `<!--` … `-->` | `rows=24 bound=24`, exit 0 | false green: nothing renders; counter cannot tell hidden rows from visible ones |
| A2 | heading written as setext (`Probe reason codes` + `---`) | `rows=0 documented=0 missing=23`, exit 1 | false red: same section, valid Markdown, table rendered |
| A3a | table moved under a second `## Probe reason codes` after an intervening `## X` | `rows=0 documented=0 missing=23`, exit 1 | false red: duplicate heading is ignored, not merged |
| A3b | full first section + second `## Probe reason codes` holding a contradicting row | `rows=24 bound=24`, exit 0 | false green: second section never inspected |
| A4 | every row prefixed with one tab | `rows=0 documented=0 missing=23`, exit 1 | acceptable (tab = code block in Markdown) |
| A4b | every row prefixed with two spaces | `rows=0 documented=0 missing=23`, exit 1 | false red: 1–3 space indent still renders a GFM table |
| A5 | whole SKILL.md converted to CRLF | `rows=24 bound=24`, exit 0 | acceptable (parser survives CRLF) |
| A6 | `\|` inside one trigger cell | `rows=24 bound=23 unbound=1 documented=23`, exit 1 | false red: escaped pipe is legal GFM and renders |
| A7 | hand-written receipt, correct sha, 2-line stub probe that cannot emit any reason | `rows=24 bound=24`, exit 0 | BLOCKER-grade: binding has no provenance; “captured” is unverifiable |
| A8 | valid 24-line receipt + one line with a foreign probe sha | `bound=0 unbound=24 receipt=stale`, exit 1 | brittle: one foreign line wipes all bindings |
| A8b | valid 24-line receipt + one non-JSON line | `bound=0 unbound=24 receipt=stale`, exit 1 | same brittleness via malformed line |
| A9 | `reason` cell with two backticked tokens | `rows=24 bound=23 unbound=1 documented=22 missing=1`, exit 1 | correct refusal |
| A10 | one row with an empty trigger cell | `rows=24 bound=24 documented=23`, exit 0 | depth blind spot: a row that teaches nothing still binds |
| A11 | fenced block containing a line `## example` mid-table | rows before the fence only, `missing>0`, exit 1 | false red: `## ` is checked before fence state |
| A12 | a fenced block before the real section containing literal `## Probe reason codes` | `rows=0 missing=23`, exit 1 | false red: heading detection ignores fences |

Depth test: for each of the 23 frozen population codes, `grep`-equivalent count in `SKILL.md` at
99cdb4d6; also count whether the base line already carries the verdict, and whether the table's
trigger facts (curl rc numbers, 4 MiB cap, sniff rule) exist at base.

## Added before their run (same discipline)

| case | mutation | expected | judgement |
|---|---|---|---|
| A14 | every table row prefixed with `> ` (blockquote table) | `rows=0 documented=0 missing=23`, exit 1 | false red: GFM renders a table inside a blockquote |
| A15 | valid 24-line receipt plus 50 junk lines with the same probe sha and invented triples | `rows=24 bound=24`, exit 0 | receipt accepts arbitrary extra claims; nothing audits them |
