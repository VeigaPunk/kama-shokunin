# K1Design — C1 design critic: registry/append-only-contract.tsv at 3a09a1d93dcc16799cf6c4b48786e6440af134c4

**Verdict: calibration holds — all 7 contract rows point at lines that genuinely declare the rule for the audited path at the tip, and the expanded population (85 files) matches the repo state; residual gaps are three omission classes (knowledge §Errata regions, which the v2 format cannot scope; two declared ledgers; the SCORECARD head carve-out, expressible only as note prose), none of which changes the current 5-event result if fixed without adding whole-file knowledge.**

Audited tip: `3a09a1d93dcc16799cf6c4b48786e6440af134c4` ("round-47: build - append-only-audit v2 + contract (C1); …"). All evidence is read-only against a `git clone --shared` of the lane in scratch (`S=/fast/scratch/hyaku/kama-r47/K1Design`, clone at `$S/lane`, checked out to the tip). No tools were installed (python3/git only; no pacman, no uv, no npx).

## 1. Baseline runs (exit codes, outputs)

| # | Command | Result |
|---|---|---|
| M0 | `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`; `git -C $S/lane checkout 3a09a1d9…` | `git rev-parse HEAD` = `3a09a1d93dcc16799cf6c4b48786e6440af134c4`; `git status --porcelain` empty |
| M1 | `python3 tools/append-only-audit.py --repo $S/lane --to 3a09a1d9… --json` | `schema=append-only-audit/v2`, `files=85`, `commits=303`, `events=5`, exit **1** |
| M2 | same with `--contract <proposed>` (2 new ledger rows) | `files=87`, same 5 events, exit **1** |
| M3 | `--files corpus/knowledge/*.md` (36 files) | `events=3` all `unrestored`: `726f737a` llamacpp-loading-lifecycle.md 21/0, `c0a9b029` context-capacity.md 47/0, `d183ec57` echo-discriminating-counters.md 29/0 |
| M4 | `--files registry/claim-outcome-ledger.tsv` and `--files registry/report-landing-errata.tsv` | 0 events each |
| M5 | deficit multiset recomputation (tool's own functions, window = event commit..tip) | see §3 |

M1's events (identical to the pre-wave dry run): `dd9f5dc6c0e6` SCORECARD.md **31/24 partial**; `0718b6abbda6` LOG.md 2292/2292 restored (by `82b5e9d3`), SCORECARD.md **2421/2420 partial**, corpus/QUALITY.md 375/375 restored, corpus/README.md 663/663 restored.

## 2. The 7 rows: does declared_at declare the rule for the path?

Contract at tip = 8 lines (header + 7), byte-identical to `registry/append-only-contract.tsv` (read via `git show 3a09a1d9…:registry/append-only-contract.tsv`). Verified per row (`git show <tip>:<path>` at the cited line; the C1 counter leg requires the line to contain "append" case-insensitively — all 7 pass):

| Row | Path | Rule | declared_at | Line at tip (verbatim, trimmed) | Declares the rule? |
|---|---|---|---|---|---|
| 1 | LOG.md | A-corr | README.md:16 | "`LOG.md` — append-only round log: the evidence that motivated each change" | **Yes** — whole-file append-only; corrections-as-new-entries carried by note (PROTOCOL.md:463). |
| 2 | SCORECARD.md | A-corr | corpus/README.md:521 | "append-only records in `corpus/lessons/round-33.md` and `SCORECARD.md`." | **Yes for append-only** — but does **not** itself declare the head carve-out; that lives at SCORECARD.md:6 ("… are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` … kept current in rounds 43, 44, 45 and 46; the round-5 banner and the head sections they replace are kept verbatim under §Historical head sections"), which contains no "append" and therefore **cannot** be a declared_at under the frozen leg (see §5 D1). |
| 3 | corpus/QUALITY.md | A-corr | corpus/QUALITY.md:24 | "Same columns as the table above; appended so no existing line moves. Source tiers are defined in `SOURCES.md`." | **Yes** — criteria rows appended; supersession-names-old-criterion at lines 4–5 ("Criteria are added as new rows; supersession names the old criterion instead of erasing it."). |
| 4 | corpus/README.md | A-corr | corpus/README.md:86 | "Appended rather than inserted, so no existing line moves (`QUALITY.md` KQ7)." | **Yes, partially** — declares coverage-map appendedness. The frontier-prose/corrections side has stronger anchors at :361 ("Appended; the sections above stay as filed.") and :637 ("The bullet above is left as written (append-only)."); re-anchoring changes no events (note only). |
| 5 | corpus/SOURCES.md | A-row | SKILL.md:578 | "| SOURCES append-only guard | gate: `python3 tools/sources-append-only.py --from A --to B` | 0 no violation, 1 removed row or a changed cell outside `status`/`recheck`/`used-by` | … |" | **Yes** — this is the gate row declaring the exact A-row rule (KQ22). The round-46 map's flagship citation CORPUS.md:116 is stale: **CORPUS.md does not exist at the tip** (`git show 3a09a1d9…:CORPUS.md` → fatal), and the contract correctly does not rely on it. |
| 6 | corpus/lessons/*.md | A-corr | corpus/lessons/round-23.md:100 | "…was written at `245a37f6` and stays unchanged; corrections below are append-only." | **Yes** — section-local but genuine; global anchor round-44.md:37 ("lessons are append-only history and the next release recheck should carry it") corroborates. Pattern expands to all 79 lesson md files (flat dir; no subdirs, no non-md). |
| 7 | registry/history/DELTA.md | A | registry/history/DELTA.md:3 | "# Append-only; one line per row-field change between snapshots, in chronological order. Generated by kama-probe.sh snapshot; never hand-edited." | **Yes** — whole-file generated A. |

Population check: `files=85` = 79 lessons + LOG.md, SCORECARD.md, corpus/QUALITY.md, corpus/README.md, corpus/SOURCES.md, registry/history/DELTA.md — exactly the expansion of the 7 patterns over `git ls-tree -r --name-only <tip>`; no contracted file is absent at tip.

## 3. The two partial events are exactly the SCORECARD head carve-out text

M5 (deficit multiset; `debug2.py` using the tool's own `deleted_lines`/`Repo`/`held` semantics over the event's window at tip):

- `dd9f5dc6` SCORECARD.md deleted=31, restored_max=24, **deficit=7** — the 7 never-held deleted lines sit at parent lines **17 and 21–26**: the pre-round-42 reconciler blurb and the six pre-42 Axes-table rows (old hashes, e.g. `SKILL.md` sha `151023b99…` 1375 lines, `PROVINCE.md` sha `dbb5f4f7…`). This is exactly the §Historical-head region the file's own line 6 says is re-derived/kept-verbatim — the round-46 D2 finding (no pre-42 Axes-table render retained) reproduces at the round-47 tip.
- `0718b6ab` SCORECARD.md deleted=2421, restored_max=2420, **deficit=1** — the single unmet deleted line is parent line **16**: the `| depth | **7** | … SKILL.md sha256 91440eb8… (1420 l …` Axes-table head row (re-anchored again in the repair commit `82b5e9d3`).

So both `partial` statuses (hence the exit 1) are caused solely by head-region text that SCORECARD.md:6 declares exempt. The contract's note already documents this ("a head re-anchor is an expected partial"); the machine-readable form cannot carry it (rule vocabulary has no R/region token — see §5 D1).

## 4. Omissions vs the round-46 map (verified at tip)

| Omitted surface | Declaring line at tip | Probe result | Event change if added |
|---|---|---|---|
| `corpus/knowledge/*.md` §Errata regions (only `consumer-registry.md:30` — "## Errata — 2026-10-14 re-census (append-only; rows below keep their round-1 text)" — and `context-capacity.md:245` carry `## Errata` headings; LOG.md:231 corroborates; KQ3 (QUALITY.md:11, "Corrections preserve old corpus bytes" — no "append", unusable as declared_at) | consumer-registry.md:30; LOG.md:231; QUALITY.md:11 | M3: **+3 events, all unrestored** — and all three are body edits outside Errata regions (round-46 M3 recheck; confirmed the 3 files' deletions are not inside an Errata section). Whole-file inclusion would be **false positives** | **Changes events (+3)** if added as whole-file; **0** if region-scoped — which the v2 format cannot express |
| `registry/claim-outcome-ledger.tsv` (only dated declaration in the lane) | corpus/lessons/round-21.md:67: "(the ledger was created this round; append-only applies after measurement)" | M4: 0 events | No change (files 85→86) |
| `registry/report-landing-errata.tsv` (self-declared) | registry/report-landing-errata.tsv:1: "# Append-only corrections for defects found by tools/report-landing-audit.py in fleet reports …" | M4: 0 events | No change (files 86→87) |
| Other ledgers (`verdict-ledger`, `engine-pins`, `digest-ledger`, `recheck-r45`, `release-recheck-b11889/b11906`, `staged-refusals`, `hexrun-ledger`) | no declaration line with "append" (row-level uses of the word are notes, not rules); round-46 map's "inferred" status stands | M4 (2026-46) 0 events | not addable under the frozen leg (declared_at must contain "append") |
| SCORECARD head carve-out | SCORECARD.md:6 (no "append"; see §5 D1) | n/a | represented only as note prose; event set unchanged |

## 5. Defects / findings (frozen counters untouched; proposed fixes only)

- **D1 (format/leg)**: the C1 counter's contract leg (`tools/round47-append-audit-v2-check.py:293`) requires every `declared_at` line to contain "append". The SCORECARD head carve-out's natural declaring line (SCORECARD.md:6) does not, so the exemption can never be a machine-readable row; and the rule vocabulary `A | A-row | A-corr` is whole-file only, so region scoping (knowledge §Errata, SCORECARD head) is unrepresentable. *Fix (future counter, not frozen)*: allow an optional region qualifier (`declared_at` already carries a line; extend rule to `A-corr@<heading>` or add a `region` column) and relax the "append" requirement to "declares the rule" or keep the word check but permit the cave-out to be carried as a separate machine-readable "exemption" row. The frozen counter cannot express any of this; the note column is the only current carrier.
- **D2 (coverage)**: `corpus/knowledge/*.md` §Errata is declared append-only (consumer-registry.md:30) and unguarded. Adding the whole directory is **wrong** (+3 false-positive unrestored events, M3); the correct guard needs region scoping (D1). Recommend: leave omitted until the format supports regions; record the gap in the SCORECARD calibration row.
- **D3 (coverage, safe)**: two declared ledgers are omitted: `registry/claim-outcome-ledger.tsv` (round-21.md:67) and `registry/report-landing-errata.tsv` (self-header line 1). Both pass the leg (rule A-row/A, declared_at contains "append", path exists) and add **0 events**. Adding them increases calibration coverage without disturbing the audit result.
- **D4 (weakest anchor)**: corpus/README.md:86 declares only the coverage-map appendedness; the A-corr note also covers frontier/corrections, better anchored at :361/:637. No event change.
- **D5 (stale map citation, not a contract defect)**: CORPUS.md:116 (round-46 map) does not exist at the tip; row 5's SKILL.md:578 anchor is correct and sufficient.

## 6. Corrected contract (full text — see `K1Design/contract-proposed.tsv`)

```
path	rule	declared_at	note
LOG.md	A-corr	README.md:16	round log; corrections land as new entries (PROTOCOL.md: LOG.md is append-only)
SCORECARD.md	A-corr	corpus/README.md:521	dated round sections append-only; the head sections named at SCORECARD.md:6 are re-derived in place since round 42, so a head re-anchor is an expected partial (verified: the only unmet lines of dd9f5dc6 and 0718b6ab are Axes-table/head text)
corpus/QUALITY.md	A-corr	corpus/QUALITY.md:24	criteria appended as new rows; supersession names the old criterion (QUALITY.md:4-5)
corpus/README.md	A-corr	corpus/README.md:86	coverage map and frontier prose appended, corrections appended
corpus/SOURCES.md	A-row	SKILL.md:578	registry rows appended; only status, recheck and used-by change in place (KQ22, tools/sources-append-only.py)
corpus/lessons/*.md	A-corr	corpus/lessons/round-23.md:100	filed lessons stay; corrections appended (KQ26, round-44.md:37)
registry/history/DELTA.md	A	registry/history/DELTA.md:3	generated by kama-probe.sh snapshot; never hand-edited
registry/claim-outcome-ledger.tsv	A-row	corpus/lessons/round-21.md:67	ledger was created this round; append-only applies after measurement (rows appended, cells untouched)
registry/report-landing-errata.tsv	A	registry/report-landing-errata.tsv:1	self-declared: "# Append-only corrections for defects found by tools/report-landing-audit.py" (header line 1)
```

**Rows that would change the audit's events**: only a whole-file `corpus/knowledge/*.md` row would (+3 unrestored false positives — do not add). The two ledger rows change the file population (85→87) but **not** the event set; all declared_at re-anchors (rows 2/4/6) are provenance-only. Removing the SCORECARD row would drop both partials and flip the exit to 0 — not recommended: it would stop guarding a declared append-only surface (dated round sections) and would calibrate by shrinking coverage.

## 7. Evidence files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/K1Design.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/K1Design/contract-at-tip.tsv` (frozen contract read at tip)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/K1Design/contract-proposed.tsv` (corrected contract)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/K1Design/audit-at-tip.json` (M1 tool JSON, 85 files / 5 events)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/K1Design/deficits.txt` (M5 deficit lines with parent positions)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/K1Design/knowledge-ledger-impact.txt` (M3/M4/M2 probes)

Scratch `/fast/scratch/hyaku/kama-r47/K1Design` will be removed on finish; the clone was read-only (`git checkout` in the scratch clone only; nothing written to the lane or fleet).
