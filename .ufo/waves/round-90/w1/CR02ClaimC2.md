# CR02ClaimC2 — attack on C2's frozen counter (round 90, wave 1)

## Scope
Attacked `tools/round90-reason-rows.py` (sha256 `fa4c31771783e533aabd68bd82437fbb681e058c6a19debe3e3fbe2c90d2f095`,
identical at freeze `6f6d7873` and at M2 `2ee0b55f`). For each case I built a fresh git fixture under
`/fast/scratch/hyaku/kama-r90/CR02ClaimC2` whose `SKILL.md` is the real M2 file mutated once, whose
`tools/kama-probe.sh` is a two-line stub (`#!/bin/sh\nexit 0`), and whose receipt is rebuilt to the stub's sha;
then ran the frozen counter against that commit. Expectations were written to `expectations.md` before the
battery ran (A14/A15 appended before their run). Also reproduced the claim at M2 and re-ran the receipt producer.
No tool installed; no lane file touched; no endpoint contacted.

## Commands and outputs (true exit codes)
1. `python3 tools/round90-reason-rows.py --repo . --rev 2ee0b55f…` → **exit 0**,
   `REASON_ROWS population=23 documented=23 rows=24 bound=24 unbound=0 missing=0 duplicates=0 additional=1
   receipt=current probe_sha256=c197912f… rev=2ee0b55f…` (`out/CR02ClaimC2/rows-M2.out:1`) — predicate met.
2. Same at base `--rev 99cdb4d6…` → **exit 1**, `documented=0 rows=0 missing=23 receipt=absent
   probe_sha256=c15ffca8…` (`rows-base.out:1`; identical to `controls/c2-base.out`).
3. Same at C1's M `--rev f968fb19…` → **exit 1**, `documented=0 … receipt=absent probe_sha256=c197912f…`
   (`rows-M.out:1`): C2's receipt exists only from M2, as the claim states.
4. `python3 tools/round90-reason-capture.py --repo . --rev 2ee0b55f… --work <scratch>/capwork --out
   <scratch>/reason-cells-recapture.jsonl` → **exit 0**, `cells=24 probe_sha256=c197912f…`;
   `cmp` committed receipt vs recapture → **exit 0**, byte-identical (`recapture.out`, `reason-cells-recapture.jsonl`).
5. `python3 out/CR02ClaimC2/attack-reason-rows.py --lane … --work … --out …` → **exit 0**, 17 cases; every observed
   result equals its pre-registered expectation (`attack.out`, one `===` block per case).
6. `python3 out/CR02ClaimC2/render-check.py` → **exit 0** (`render-check.out`); `python3 out/CR02ClaimC2/depth-count.py
   --repo …` → **exit 0** (`depth-count.out`).

## Findings

**DEFECT-1 — hidden rows bind (depth is form-only).** A1 wraps all 24 rows in one `<!-- … -->`: counter prints
`documented=23 rows=24 bound=24`, **exit 0**, same counts as the faithful control A0 (`attack.out:30` vs `:1`).
The same text renders **0 tables** with HTML enabled (`render-check.out`: `A1 tables=0 tbody_rows=0`). The counter
certifies content no operator can see, on the axis that is supposed to measure what an operator learns.

**DEFECT-2 — binding has no provenance (the answer to “does anything stop a hand-written receipt?” is no).**
A7 uses the two-line stub probe, which cannot emit any reason, plus a hand-written receipt carrying the stub's
correct sha: **exit 0**, `bound=24`, same counts as A0 (`attack.out:258`). A15 adds 50 junk receipt lines with the
same sha and invented triples: still **exit 0** (`attack.out:488`). The counter checks only sha equality and
(cell, reason, verdict) equality; the frozen forgery battery tests fabricated reasons/verdicts/cells, never a
fabricated receipt (`controls/c2-forgeries.out`). The only detector is out-of-band: a fresh capture at M2 is
byte-identical (command 4), so a re-run + `cmp` would catch it — but the predicate does not require that.

**DEFECT-3 — an empty trigger binds.** A10 replaces one trigger with an empty cell
(`| `http-401` | `UNAUTHORIZED_SERVICE` |  | `R-http-401` |`): **exit 0**, `bound=24` (`attack.out:375`). Only the
reason/verdict/cell tokens are validated, so `documented=23` does not imply any row explains anything.

**DEFECT-4 — a duplicate section is never read.** A3b keeps the full table and appends a second
`## Probe reason codes` whose row says `router-unloaded` → `MODEL_OK`: **exit 0**, `rows=24` (`attack.out:115`).
A visible contradiction ships green. A3a (table only in the second section, after an intervening `## X`) is the
mirror false red: **exit 1**, `rows=0` (`attack.out:87`).

**DEFECT-5 — valid Markdown refused (6 classes).** A2 setext heading → exit 1 `rows=0` (`attack.out:59`; renders
`h2` + table); A4b two-space-indented rows → exit 1 `rows=0` (`:172`; renders 1 body row); A6 `\|` in a trigger →
exit 1 `bound=23 unbound=1` (`:229`; renders one cell with a literal `|`); A14 blockquote rows → exit 1 `rows=0`
(`:460`; renders a table); A11 a fenced block containing `## example` mid-table truncates the parse at 10/24 rows →
exit 1 `missing=13` (`:404`); A12 a literal `## Probe reason codes` inside a fence before the section zeroes it →
exit 1 `rows=0` (`:432`). A11/A12 are ordering bugs (`## ` is tested before fence state, and heading detection
ignores fences); the rest are parser narrowness. Tab-indented rows (A4, `:144`) and a fully fenced table (A13,
`:517`) are correctly refused (`render-check.out`: tab rows become a code block, 0 body rows).

**NOTE-1 — all-or-nothing staleness.** A8 (one foreign-sha line) and A8b (one non-JSON line) each drop all 24
bindings: exit 1, `bound=0 receipt=stale` (`attack.out:287`, `:316`). Docstring-compliant, but one interrupted
re-capture poisons a good receipt.

**NOTE-2 — correct refusals.** A9 two backticked tokens in the reason cell → exit 1, `documented=22 missing=1`
(`attack.out:345`); A5 CRLF document → exit 0, `bound=24` (`:200`).

## Depth judgement — real but narrow (counts)
- 24 rows = 23 frozen population + `body-too-large` (`additional=1`).
- Base `SKILL.md` at `99cdb4d6`: **9/23** codes appear as exact backticked tokens, and all 9 already share a line
  with their verdict (`connection-refused:37`, `llamacpp-loading:561`, `matched:1768`, `unresolvable-id:149`,
  `router-sleeping:1769`, `router-unloaded-autoload:1770`, `router-model-missing:1799`,
  `router-model-invalid:1800`, `router-unloaded:1819`). **13/23** appear nowhere (zero substring); `timeout`
  appears 26× only as an English word/flag. → **14 code names are new**.
- Verdict mapping is already stated at base for **19/23** (situation tables at 129–136, 1767–1773, 1798–1803,
  1818–1822). **4 new mappings**: `timeout`→DEAD, `expected-wildcard`→MODEL_OK, `schema-unrecognized`→FOREIGN_SERVICE,
  `non-model-2xx`→FOREIGN_SERVICE.
- Facts absent at base: curl `rc 7/28/52/56/63` (0 each), `4 MiB` (0), `max-filesize` (0), “header or body sniff”
  (0). 5 rows carry a curl rc, 1 the cap; `body-too-large` is wholly new.
- Trigger prose is original, not copied: best similarity of any trigger to any base line 0.515, median 0.440,
  0 rows ≥ 0.8 (`depth-count.out`).
- Answer: the table does add knowledge — a 14-code vocabulary, 5 curl-rc facts, the 4 MiB cap and 4 new verdict
  mappings — but 19/23 verdict conclusions were already derivable from SKILL.md, and the counter cannot separate
  informative from blank prose (DEFECT-3) or visible from hidden rows (DEFECT-1).

## Deliverables (in `.ufo/waves/round-90/w1/out/CR02ClaimC2/`)
`expectations.md`, `attack-reason-rows.py`, `attack.out`, `render-check.py`, `render-check.out`,
`depth-count.py`, `depth-count.out`, `rows-M2.out`, `rows-base.out`, `rows-M.out`, `recapture.out`,
`reason-cells-recapture.jsonl`.

VERDICT: holds — the frozen predicate reproduces exactly at M2 (exit 0, documented=23 rows=24 bound=24) and the receipt is byte-reproducible by its producer; the counter is a form-only judge (hidden rows, blank triggers, hand-written receipts, unread duplicate sections) and the depth gain is 14 new code names + 4 new mappings, not 23.
