# rev=1a85a991fce5b76b60f88a5cab3df98d253b1a4a
# CON01 — sibling-overlap scan (read-only), kama r76 w1

Scanned at the freeze commit `1a85a991fce5b76b60f88a5cab3df98d253b1a4a` (lane tip == freeze).
Read-only over `/home/vgpnk/Projects/shokunin/*-shokunin/`: greps and docstring/header reads only;
no sibling file written, no network, no mutating git. Adjacency evidence only — nothing absorbed.

## 0. Method note (one tooling finding)

The fleet root `.gitignore` line `*-shokunin/` hides every lane from gitignore-respecting search:
the first grep sweep with `gitignore: true` returned zero hits over all lanes. All greps below were
(re)run with `gitignore: false` over explicit instrument dirs. Any future fleet-wide scan must do the
same or it silently scans nothing. `kagi-shokunin` has no `tools/`; its evidence is lessons-only.
`revenger/lore/game-dev-2d/game-dev-3d/audio/kasegi` expose no instrument dirs matching the three
classes (`kasegi/c2-controls/` holds scratch receipt controls, not a record instrument).

## 1. Overlap table

| Claim | Sibling lane | Path (absolute) | Overlap verdict | One-line difference |
|---|---|---|---|---|
| C1 fence-aware citation scanning | kumitate | `/home/vgpnk/Projects/shokunin/kumitate-shokunin/scripts/cite-check.mjs` | near-duplicate (core mechanism) | Mechanical citation re-verifier over SKILL.md+corpus: fence byte-ranges masked before span scans, marker-symmetric, unclosed fence masks to EOF (contract `kumitate-cite-check-v1`); resolves path/line/pin citations, but has no receipt-population classes (bound/unbound/shifted) and no record-path scope. |
| C1 | mado | `/home/vgpnk/Projects/shokunin/mado-shokunin/quality/counters/c1-r56-autoreload-entry.py` | partial | CommonMark-shaped `fence_open`/`fence_close` (char+length, 0–3 indent) + HTML comments with live_lines; mutation arms `row-in-fence`, `fence-length`, `fence-inside-comment`; scores one admission clause, not a citation population. |
| C1 | mado | `/home/vgpnk/Projects/shokunin/mado-shokunin/quality/counters/c2-r45-monitor-entry-v2.py` | partial | T3 clause binds every fenced block (whitespace-collapsed) to occur verbatim in concatenated pinned sources and demands "no fence is left open" — fence content treated as quoted material that must resolve upstream; no population classification. |
| C1 | mado | `/home/vgpnk/Projects/shokunin/mado-shokunin/quality/check-tool-ledger.py` | partial | `unfenced()`: "a fenced row is documentation, not a ledger row"; closing rule weakened to same first char ×3, so a ~~~ does not close ``` (kama's audit v5 rule is stricter). |
| C1 | kotoba | `/home/vgpnk/Projects/shokunin/kotoba-shokunin/verifiers/check_infoless_fences.py` | partial | Frozen fence-semantics instrument: info-less fences must not be read as shell; 10-case classes × seeds; checklist floor records "unclosed/mixed/blockquote fence assertions (145→150, 86→91)" (r43). Fence-toggle renderers in most `check_*.py` (`rendered()`), no closing-length rule. |
| C1 | kotodama | `/home/vgpnk/Projects/shokunin/kotodama-shokunin/tools/check-readme-heading.py`, `.../check-readme-revisions.py` | partial | Fence-aware ATX-heading / `revision:` line scan of a README record; fence machine toggles on same first char, no closing-length or indent rules. |
| C1 | chousa | `/home/vgpnk/Projects/shokunin/chousa-shokunin/tools/assimilate-rows.py` | partial | `source:`-citation scanning of registry headers with fenced example headers excluded ("lines in a fenced example are not citations"); no unclosed-fence verdict class. |
| C1 | chousa | `/home/vgpnk/Projects/shokunin/chousa-shokunin/tools/research-gate.sh` | partial | r17/r20/r23 fence pairing (same char, closing length ≥ opening, 0–3 indent, unclosed = literal to EOF, fail closed) + chain-mode hop-citation resolution; bash, corpus-boundary-bound; no exit-2 could-not-evaluate on unclosed fence. |
| C1 | kaidoku | `/home/vgpnk/Projects/shokunin/kaidoku-shokunin/tools/round-50/c2-record.py` | partial | `vis()` fence+comment visible-text filter with closing-length rule and unterminated-runs-to-EOF, LF-only split; used to grade SCORECARD atoms, i.e. quoted history is never counted. |
| C1 | kaidoku | `/home/vgpnk/Projects/shokunin/kaidoku-shokunin/tools/round-46/registry.py` | partial | Fence- and HTML-comment-aware parse of the bound registry section (`rows_in_section`) with a `m_fenced` mutation proving the fence-blind parse fails (R45-CL14 lineage). |
| C1 | kake | `/home/vgpnk/Projects/shokunin/kake-shokunin/scripts/corpus-contract.mjs` | partial | Fence-aware `## Gate` section detection in lessons ("a heading inside fenced code is not a section"); adjacent class, fence machine simple. |
| C1 | kake | `/home/vgpnk/Projects/shokunin/kake-shokunin/scripts/doc_quote_truth.py` | partial | Claim-row quoted spans must resolve inside cited receipts (elision rules), revision-citation vs digest-token classes, append-only conjunct on claim tables; no fence scoping of the citation population itself. |
| C1 | mori | `/home/vgpnk/Projects/shokunin/mori-shokunin/tools/mori-pin-check.py` | partial | Fence-aware `scan_lines` kinds (fence_open/close/body); arm `v2_fenced_example_not_counted` and fatal hidden rows inside fences — quoted rows never count as live self-test pins. |
| C1 | kengaku | `/home/vgpnk/Projects/shokunin/kengaku-shokunin/plans/attrib_probe.py` (+ `attrib-r2{1,2,3}-frozen.md`) | adjacent | Inverse pattern: the frozen fact lives *inside* a fenced block whose byte range is sha256-pinned by a following `FROZEN:` line, and the instrument reads the LAST `FROZEN:` line as live (superseded pins remain quoted in-file). |
| C1 | kama (own, baseline) | `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round53-cited-path-check.py`, `round54-cited-path-check.py` | internal precedent | Kama's own fence-scoped backtick-span citation parser ("the restored blocks of round 52 are fenced, so history kept verbatim is not a standing citation") with the arm `fenced path is not cited`; the frozen fence-blind base is `tools/round74-receipt-claim-binding.py` (`RECEIPT_CLAIM_V2`). |
| C2 self-record fact re-derivation | kaidoku | `/home/vgpnk/Projects/shokunin/kaidoku-shokunin/tools/round-44/c2-counter.py` + `tools/round-44/c2-rubric.json` | near-duplicate (correction semantics) | Frozen rubric of self-assessment statements re-derived at REV; appended `c2-correction:`/`c2-correction-value:` blocks; "a note is never evidence"; repair only when a `repair_command` re-derivation equals the asserted value; two-source rule; wrong asserted value in the rubric itself is an arm (arm B). |
| C2 | kaidoku | `/home/vgpnk/Projects/shokunin/kaidoku-shokunin/tools/round-47/record.py` | near-duplicate (correction semantics) | Append-only record card; `## Record corrections` lines exempt the atoms they name AND are themselves re-derived — a correction that disagrees with committed state keeps the atom red (`corrections_bad`, red-correction arms). |
| C2 | kaidoku | `/home/vgpnk/Projects/shokunin/kaidoku-shokunin/tools/round-26/c2-calibration.py`; `.../round-35/c2-calibration-counter.py`; `.../round-32/c2-capability-calibration-v2.py` | partial | K1–K6 record facts re-derived (rule-block counts, heading spans, PROVINCE line-count bounds K6); record-defect closure re-grading; SCORECARD capabilities vs fleet MANIFEST. Facts are per-round rubric items, not a declared cross-file population. |
| C2 | tameshi | `/home/vgpnk/Projects/shokunin/tameshi-shokunin/tools/count-recheck.py` + `count-recheck.json` | near-duplicate (log-tally class) | "A record's printed counting figure must still be the count its named command produces at the revision the record names" — standing red arms measured on every sweep until a superseding record carries corrected figures; counting command of record `git grep -c`. Exactly kama's `log-tally` fact class. |
| C2 | tameshi | `/home/vgpnk/Projects/shokunin/tameshi-shokunin/tools/pointer-recheck.py` + `pointer-recheck.json` | near-duplicate (closure-pointer class) | Record file:line pointers re-checked with verdict lines `POINTER_ROW <id> expect=<e> measured=<m> ok\|MISMATCH`; stale cells stand append-only with the drift measured; lesson erratum is the correction of record. Kama's `closure-pointer` fact is the same class with the pointer derived from the closure population (`tools/round69-newest-closure-counter.py`, `NEWEST_CLOSURE newest=<f> date=<iso> round=<n> row_names=<f> row_current=<bool>`, exit 0/1/2). |
| C2 | mori | `/home/vgpnk/Projects/shokunin/mori-shokunin/tools/mori-pin-check.py` | near-duplicate (digest facts) | SKILL.md pins: full 64-hex digest must equal the named in-tree file's sha256 (`mismatch`/`stale`), truncated `hex…` pins must prefix that file's digest, `--baseline-rev` reports dropped/rebound pins since a revision. Kama's `skill-digest`/`province-digest` facts are the same value class; kama adds line-count, correction-acceptance and the declared population. |
| C2 | mori | `/home/vgpnk/Projects/shokunin/mori-shokunin/tools/mori-round41-calibration.py` | partial | Calibration-correction line re-derived against a gate's printed summary/timing lines; a correction whose numbers do not parse from the gate output is a mismatch — value-bound correction with wrong-value refusal. |
| C2 | chousa | `/home/vgpnk/Projects/shokunin/chousa-shokunin/tools/claims-audit.py` (+v2); `.../tools/digest-in-tree.py`; `.../tools/build-spans.py` | partial | Audit rows name anchor+class and the checker re-derives the fact from committed bytes; every 64-hex pin in a receipt must re-derive from committed blobs (`DIGEST_IN_TREE=PASS/FAIL`, fail-closed when no digest); `SPANS_ROWS=n STALE=k` quote-span re-derivation. |
| C2 | kotoba | `/home/vgpnk/Projects/shokunin/kotoba-shokunin/verifiers/check_province_core.py` | partial | PROVINCE `## Core` sections must stay byte-identical to a base; a rewrite counts only when the whole section's sha256 is in an in-file append-only errata ledger **with its reason** (`ADJACENT_ERRATA`) — correction keyed by the superseded bytes' digest, the same shape as kama's "names the superseded bytes". |
| C2 | kotoba | `/home/vgpnk/Projects/shokunin/kotoba-shokunin/verifiers/check_correction_sweep.py` | partial | Declared corrections must name the correction (not just the round label) with a line number, and the stale sentence beside the weaker accepted text is kept as a measured probe — shortening the pattern turns the probe green. |
| C2 | kengaku | `/home/vgpnk/Projects/shokunin/kengaku-shokunin/plans/anchor_digest_check.py`, `.../anchor_line_check.py` | partial | Every `sha256 <hex>` claim in SOURCES must resolve to the capture its row names; append-only erratum exemption requires the erratum to carry the row's **exact wrong token** plus the correction (`erratum-incomplete` otherwise) — correction-must-name-superseded-bytes, with wrong-value staying a defect. |
| C2 | kumitate | `/home/vgpnk/Projects/shokunin/kumitate-shokunin/scripts/proxy-check.mjs` (+ `claims-check.mjs`, `counter-pins.mjs`) | partial | Scorecard claim block: all twenty-nine declared values re-derived from the trees and "never trusted" — a term or pin that disagrees is a finding; counter byte-pins fail closed. Declared-population re-derivation, but over one scorecard stanza. |
| C2 | tabi | `/home/vgpnk/Projects/shokunin/tabi-shokunin/scripts/check-freshness.mjs`, `.../check-release-pins.mjs` | partial | Pins bind target sha256 **and newline count** (`PIN_MATCH target=… sha256=… newlines=…`); a drifted registry row resolves only via `superseded_by` naming a row whose `teaches` opens `supersedes <id> —` — supersession-as-correction with the new value re-fetched. |
| C2 | kama (own, baseline) | `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round69-newest-closure-counter.py`, `tools/digest-ledger.py`, `tools/round42-selfdesc-reconcile.py` | internal precedent | Kama's own closure-pointer, digest-ledger and self-desc reconciliation counters are the C2 lineage; `round76-selfrecord-facts.py` composes their fact classes under one declared population. |
| C3 accepted-history grading + cutoffs | mori | `/home/vgpnk/Projects/shokunin/mori-shokunin/tools/mori-sources-appendonly.py` | partial | CORPUS rule-2 gate: SOURCES rows append-only (only status/recheck/used-by may change), rewritten row must be a new `supersedes S###` row, and prints `supersede_timing superseded_as_of=[…] stale_supersede=[…]` — per-row temporal discipline, no event accounting, no register cutoff. |
| C3 | tameshi | `/home/vgpnk/Projects/shokunin/tameshi-shokunin/tools/additivity-receipt.py`, `.../additivity-range.py` | partial | Append-only claims judged over declared commit ranges (`append-only-raw` vs `append-only-content` with CRLF normalization), standing red arms; pair/range views; no exempt-class grading, no cutoff/rotation arm. |
| C3 | tsukuroi | `/home/vgpnk/Projects/shokunin/tsukuroi-shokunin/tools/append-receipt.py` | partial | Same convention re-implemented over tsukuroi's own record files; header states the fleet precedent ("tameshi r63's tools/additivity-receipt.py … tameshi keeps no gate ownership here (ADJ-07: method advice, not gate transfer)"). Prints `APPEND_RECEIPT: <verdict> (N files, M clean, K violation)` and `APPEND_RECEIPT_SELFTEST: PASS (N cases…)`. |
| C3 | tabi | `/home/vgpnk/Projects/shokunin/tabi-shokunin/scripts/check-round-contract.mjs` | partial | Declared `APPEND_ONLY` list (`LOG.md SCORECARD.md SKILL.md PROVINCE.md …`) held as byte-prefix at a baseline, history-rewrite refusal, census identity pin — append-only as prefix identity, no per-event accounting. |
| C3 | kaidoku | `/home/vgpnk/Projects/shokunin/kaidoku-shokunin/tools/round-55/corrections-pin.py`; `.../round-38/registry-immutable.sh` (variant) | partial | Mechanical append-only TSV model: bytes at rev == bytes at base + appended lines only (difflib opcodes → violations); registry immutability with row-deletion/reorder arms. Ledger-level integrity, no audit-event classes, no introduction cutoff. |
| C3 | kumitate | `/home/vgpnk/Projects/shokunin/kumitate-shokunin/scripts/routed-ledger.mjs` | partial (structure only) | "Accounted for exactly once" over routed-defect items: every routed section parsed fence-aware, each item needs exactly one non-contradicted row (`UNLEDGERED`, `ROW_CONTRADICTED`, `ANSWER_DEAD`); same accounting shape as C3 but over lesson items, not audit events, and no cutoff. |
| C3 | kama (own, baseline) | `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py` (v6), `tools/round75-append-accepted.py`, `tools/round52-append-restore-check.py` | internal lineage | v6 emits the events/ungraded/disclosure classes C3 consumes; round75's `APPEND_ACCEPTED events=<e> accepted=<a> …` already carries the one-register post-introduction cutoff (sentinel SN01); round52 has the ledger cutoff fixture arms (`cutoff-after-intro`/`cutoff-before-intro`). C3 generalizes to two registers with an earliest-introduction cutoff + rotation arm. |
| C3 | kagi | `/home/vgpnk/Projects/shokunin/kagi-shokunin/corpus/lessons/round-22.md` (line ~208), `.../round-13.md` | lessons-only | Falsification evidence that CommonMark H2 recognition and fenced fake tables broke naive record parsers; no committed instrument. |

Lanes with no instrument matching any of the three classes: souji (quarantine/vault domain:
receipt re-derivation with authorization pins, `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/cand-a1-quarantine.sh` et al. — same *receipt re-derivation* verb, different surface), kasegi (scratch controls only),
revenger, lore, game-dev-2d, game-dev-3d, audio (no instrument dirs of these classes found).

## 2. Where kama's instruments are stronger (property added)

- **C1 vs all siblings.** Siblings *filter* fences; none *classifies the population*. kama's frozen
  C1 adds: (i) named population classes (`fenced_quoted` counted and shown, `live_citations`,
  `bound/unbound/shifted/nonreceipt/unclassified`) instead of a boolean skip; (ii) unclosed fence =
  exit 2 could-not-evaluate (chousa fails closed silently, mado/kotodama toggle blindly,
  kotoba asserts fences but not as an exit class on a citation population); (iii) the record-path
  scope — a delta touching only `PROVINCE.md`/`SKILL.md`/`corpus/**` does not shift a receipt while
  `tools/`/`registry/`/`.ufo/` still does. No sibling has any analogue of (iii); the closest cousin
  is tameshi `receipt-revision-gate.py` (content-identical older receipt accepted on a declared
  surface), a different mechanism. (iv) Scope ruling (a) reuses the audit's CommonMark 0.31.2 §4.5
  definition (`tools/append-only-audit.py` v5) so the lane holds one fence definition — every
  sibling listed carries its own divergent fence machine.
- **C2 vs siblings.** (i) The population is *declared* in one frozen sentence across plan, module
  constant and receipt label (`claims=8`, ten checks); kaidoku/kumitate populations live in rubric
  JSON / scorecard stanzas; (ii) a correction is accepted only when it sits after the superseded
  text, names the superseded bytes, and states a corrected value the counter re-derives
  (`correction-wrong-value` arm) — kaidoku r47 has position+re-derivation, kotoba
  `check_province_core` keys by section sha256 with reason, kengaku requires the exact wrong token;
  no sibling requires all three; (iii) the closure-pointer fact is derived from the closure
  population itself (round-69 lineage), not hand-carried.
- **C3 vs siblings.** (i) Every audit event accounted exactly once across four account classes,
  with the exempt class *mechanical*: a register row is accepted only for an event whose audit JSON
  lists `ungraded` lines, whose deleted lines' parent sections equal the row's section list, whose
  count equals the event's ungraded count, and whose `graded == 0` — no sibling grades an audit's
  exempt classes at all; (ii) the cutoff is the earliest commit adding *either* register and
  `introductions` is counted, with the `rotation-reintroduced` arm — mori's `supersede_timing` is
  per-row supersession timing, kaidoku's pin has no cutoff, tameshi/tsukuroi have no rotation arm.

## 3. Reuse assessment (licence/interface risk)

Nothing outside kama's repo is written; reuse here means "kama could adopt by reference".

- **Not reusable for the C1 counter — kumitate `cite-check.mjs`.** Node/ESM vs kama's Python;
  its own citation grammar (sticky owner, alias expansion, `«»` quotes) and its own fence mask
  would import a second fence definition, which frozen scope ruling (a) forbids ("so the lane has
  one fence definition, not two"). Cite as adjacency evidence only.
- **Not reusable for C2 — kaidoku `round-44/c2-counter.py`.** It executes rubric-declared
  `repair_command`/check argv (execution plane) and binds `expected_edits` per rubric entry; kama's
  C2 is an internal read-only re-derivation over a plan-declared population. The *concept*
  (note-never-evidence, value must re-derive) is shared and citable.
- **Method-only reuse — tameshi `count-recheck`/`pointer-recheck`, tsukuroi `append-receipt`.**
  Their rows are pinned to tameshi's/tameshi-lineage revisions and records; standing arms live in
  the sibling lane. The fleet's own ADJ-07 precedent (quoted verbatim in tsukuroi's header:
  "tameshi keeps no gate ownership here (ADJ-07: method advice, not gate transfer)") is the licence
  interface: kama re-implements the method over kama's records, as `round76-selfrecord-facts.py`
  does for the count/pointer/digest classes.
- **Borrowable shape — kotoba `check_province_core.py` `ADJACENT_ERRATA`** (rewrite allowed only
  via a ledger row keyed by the superseded section's sha256 with a reason) and **kengaku
  `anchor_digest_check.py` erratum exemption** (exempt only when the erratum carries the exact
  wrong token). Both independently converge on kama's correction rule (b) "names the superseded
  bytes"; kama's C2 is the strictest of the three.

## 4. Greps run (all with `gitignore: false`; first sweep with `gitignore: true` returned zero hits — see §0)

1. `(?i)fence` over `*-shokunin/{tools,scripts,counters,verifiers,census,reports,quality}`
2. `(?i)commonmark|0\.31` over `*-shokunin/{tools,scripts,counters,verifiers,census}` + `*-shokunin/corpus/{lessons,knowledge}`
3. `(?i)citation|receipt-claim|receipt_claim|RECEIPT_TIP|RECEIPT_CLAIM` over code dirs
4. `(?i)sha256|line[_-]?count|linecount` over code dirs (first sweep)
5. `(?i)re-?deriv|selfrecord|self-record|mismatch|drift` over code dirs
6. `(?i)ungraded|exempt` over code dirs
7. `(?i)accepted[-_ ]?history|cutoff|introductions?` over code dirs
8. `(?i)append[-_ ]?only|APPEND_ACCEPTED|restored|disclosed` over code dirs
9. Remaining-lane focus greps: `(?i)fence`; `(?i)ungraded|append[-_ ]?only|APPEND_|accepted|cutoff|introductions?\b`;
   `(?i)line[_-]?count|newest[-_ ]?closure|closure|selfrecord|sha256.*(drift|pin)|pin.*sha256` over
   `{mado,tameshi,tsukuroi,kake,souji,kotodama,kotoba,kumitate,kasegi,tabi,kengaku}` instrument dirs
10. Per-lane zero/low confirmation: `(?i)fence|ungraded|sha256|line_count|rederiv|re-deriv|append[-_ ]?only|cutoff|citation|newest`
    over `kotoba/verifiers+plans`, `souji/tools+census`, `kotodama/counters+reports`, `kumitate/scripts`,
    `kasegi/x+c2-controls`, `tabi/scripts`, `kengaku/--lane+plans`, `kake/scripts`, `mori/tools`
11. Single-file probes (interface grounding): tsukuroi `check-adjacency-table-r51.py` (full docstring),
    kama `round69-newest-closure-counter.py`, kama `round74-receipt-claim-binding.py`.

No disagreement with the frozen plan was found: predicates, exit maps and kill rules were read as
written; this seat edited nothing but this report.

## 5. Handoff note (two lines)

1. Kama's C1 scope ruling (a) — one fence definition per lane, the audit's CommonMark 0.31.2 §4.5 —
   is a candidate fleet convention: mado (c1-r56, tool-ledger), kotoba (renderers, infoless-fences),
   kumitate (cite-check mask), chousa (research-gate r17) and kotodama each run a slightly different
   fence machine, and kumitate's mutant catalogue shows exit-class divergence is already load-bearing.
2. Tameshi's `count-recheck`/`pointer-recheck` and the tameshi→tsukuroi ADJ-07 re-implementation
   precedent are the standing prior art for kama's C2 fact classes — lanes building record-fact
   counters should cite that chain (method re-implementation over own records, never gate transfer)
   instead of inventing a fourth digest/pointer instrument.
