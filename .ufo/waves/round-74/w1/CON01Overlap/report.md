# CON01Overlap — report, kama round 74 wave 1

Seat: CON01Overlap (connector, cross-lane overlap scan) · lane kama-shokunin · 2026-11-04.
Milestone: kama r74 w1. Scope: READ-ONLY everywhere except the wave out dir; write scope
exercised: this directory and `.ufo/waves/round-74/w1/CON01Overlap.md` only. No git/jj
mutations anywhere (none needed — no fixtures). No tools installed or upgraded (none
needed; pacman pause honoured). No scratch dir was created (pure read scan; all outputs
landed directly in the wave out dir), so there is nothing under
`/fast/scratch/hyaku/kama-r74/` to delete. No peer messages sent; no blockers.

## Verdict

No sibling lane implements, amends, or names any of the round's three frozen instruments
or their module names. One **strong** prior-art candidate per leg (plus strong C2 extras)
exists in sibling lanes; every one differs from kama's frozen predicate in surface or
direction. Nothing found rises to **identical**; nothing contests kama's scope. No
contested-scope report is owed. Actions are all "cite sibling prior art in the knowledge
entry / receipt", detailed in `overlap.md`.

## Commands used (all from `/home/vgpnk/Projects/shokunin` unless noted)

1. Roster: `ls -d *-shokunin` → 21 lane repos.
2. Frozen claims: read `kama-shokunin/plans/round-74-claims.md` in full (208 lines).
3. MANIFEST: python3 json parse of `MANIFEST.json` (roster + `rounds[]`, 1139 entries);
   kama's last closure = `rounds[1135]`, `MANIFEST.json:41567-41579`, verdict
   `rejected-honest-stop` (r73, 2026-11-04), routed defects (1,2,5) → this round's C1/C2/C3.
4. Class scan (the seat's core command), python3 over all 20 siblings — every `tools/**`
   file, every `registry*` path, each lane's 5 newest lessons, against
   `canon|selfdesc|reconcile|receipt.*bind|claim.*bind|host.*drift|host-identity|recorded at`:
   ```python
   patterns = [re.compile(p, re.I) for p in (r'canon', r'selfdesc', r'reconcile',
     r'receipt.*bind', r'claim.*bind', r'host.*drift', r'host-identity', r'recorded at')]
   # for lane in <20 siblings>: scan tools/**, registry*, 5 newest corpus/lessons/*.md
   ```
   Result counts per lane (matches, incl. incidental `canon`/`reconcile` words):
   audio 6, chousa 96, game-dev-2d 2, game-dev-3d 0, kagi 10, kaidoku 399, kake 11,
   kasegi 5, kengaku 4, kotoba 5, kotodama 1093, kumitate 2, lore 7, mado 30, mori 120,
   revenger 1, souji 941, tabi 9, tameshi 247, tsukuroi 86. Manual triage of every
   filename hit + content hits in tools kept the 13 table rows in `overlap.md`; the bulk
   (kotodama/souji/kaidoku/mori/tameshi counts) is incidental vocabulary
   (`canonical`/`reconcile` in unrelated docstrings) — none implements the three classes.
5. Filename census: tools with `receipt|claim|bind` or `host|reconcile` in the name
   (command: python3 `glob` over `*-shokunin/tools/**` + basename filter) → the candidate
   list behind the table (tameshi receipt-*, kaidoku round-56/57/62 tools, souji
   citation-reconcile, tsukuroi check-revision-binding, mado/mori/tsukuroi host tools, etc.).
6. `recorded at` token census in all sibling tools/registry: 7 hits, all incidental
   (`argv was recorded at all`, `evidence recorded at stage time`) — none is a host-block
   `recorded at <rev>` predicate.
7. Recent-amendment sweep: `git -C <lane> log --since=2026-10-28 --name-only --format=… -- tools/ registry/ verifiers/`
   filtered to keyword paths → recent touches: tameshi `wave-reconcile.py` (r73–75),
   `receipt-commit-bind.py` (r65–66), tsukuroi receipt tools (r54–63), kaidoku
   `record-receipt-audit.py`/`receipt-audit.py` (r56–57), souji `souji-citation-reconcile.py`
   (r37–39), mado `mado-receipt-citecheck.py` (r64–67), chousa `receipt-pin.py` (r65).
   None in kama's three classes beyond the table rows.
8. Round-74 tool-name uniqueness: `grep -rn "round74-selfdesc-canon\|round74-receipt-claim-binding\|round74-province-host-drift" -l` → 0 hits outside `kama-shokunin/`.
9. Spotcheck/closure grep: python3 scan of `*-shokunin/corpus/lessons/*verifier-spotcheck.md`
   (round ≥ 70) and `.ufo/reports/round-7[0-4]/*.md` for `kama` → the reverse-direction
   table (kumitate/tameshi/tsukuroi/kotoba/kengaku/kake rows; kama's own r70–r73
   spotchecks excluded as author-lane files).
10. Sibling round-74 wave grep: python3 scan of `*-shokunin/.ufo/waves/round-74/**/*.md`
    for `kama` → `T74W1CN1.md`, `K74ConnectorOverlap.md`, `C1Connector.md`,
    `ScoutSibKamaKasegiR74.md`, kotoba Exec/Scout files (mechanical census only).
11. Citation pinning: `grep -n` for every quoted line
    (souji `round-57.md:172`, kengaku `round-72.md:126`, tameshi spotcheck `:149`,
    MANIFEST `:41567-41579`, etc.); `wc -l kama-shokunin/tools/append-only-audit.py
    kama-shokunin/tools/round50-append-audit-v5-check.py` → 1529 / 545, and
    `sed -n '585,590p' …/append-only-audit.py` → `rev-list --topo-order --reverse --parents`
    at `:587` (grounds the tameshi-citation correction in `overlap.md` §Contradictions 2).

## Findings (summary — the table lives in overlap.md)

- **C1 (selfdesc-canon)**: strong — souji `souji-citation-reconcile.py` (self-assessment
  reconciler, different leg); weak — mori r75/r77 closures grade the same SCORECARD
  capabilities-table surface by heading-count continuity; weak — tameshi `wave-reconcile.py`
  (record-span scoping). Lane-first on the bold/unbolded resolution-semantics predicate.
- **C2 (receipt-claim-binding)**: strong — tameshi `receipt-revision-gate.py` +
  `receipt-commit-bind.py`, kaidoku `round-62/base-binding-sweep.py`; weak — tsukuroi
  `check-revision-binding.py`, souji r57 LANE-FIRST/SHARED ruling (`round-57.md:170-172`),
  kengaku r72 lesson row `:126` (the same wrapped/offset escape class, named).
- **C3 (province-host-drift)**: strong — kaidoku `round-29/freeze-gate.py:132` (same
  two-revision byte-identity mechanism, different surface, no `recorded at` token);
  weak — kotoba `check_host_skill_surfaces.py` (live drift census),
  tameshi `additivity-receipt.py` (byte-preservation receipts). Lane-first on the
  host-block `recorded at` preservation predicate.
- **Reverse direction**: kumitate's r74 connector-overlap scanned all 20 siblings and
  ruled kama "none … zero surface overlap" while observing this wave's KamaR74a2 live;
  tameshi's r74 connector cites kama's `append-only-audit.py:587` (frame general,
  attribution lane-local); tsukuroi/kotoba ruled no overlap; kengaku r72/r73 named kama's
  r50 canary arm as a routed sibling site; kake's r71 closure admits a kama knowledge file
  as its C1 source. No sibling contests kama's round-74 scope.
- **MANIFEST**: kama's last closure is r73 `rejected-honest-stop`; C1/C2/C3 are its
  routed defects 1/2/5 — the carry-in grounding the plan already records.

## The one bounded proposal (synthesis across the round's sibling moves)

**Mirror the T74W1CN1 convention inside kama's own round-74 record.** Tameshi's connector
(:183-198) set the fleet's prior-art citation format when *it* cited kama: one prior-art
line per overlapping lane in the C2 receipt, a `## Gate` citation in the round lesson,
novelty narrowed to "the part that is actually new", and a mandatory
"read-only primary surface, not a governed leg" label. Kama should apply the same shape to
its own knowledge entries this round:

- C2 knowledge entry: prior-art lines for tameshi `receipt-revision-gate.py:2-4` +
  `receipt-commit-bind.py:1-2`, kaidoku `base-binding-sweep.py:2-4`; novelty rests on the
  paragraph-scoped record→receipt direction and case-insensitive hex binding.
- C3 knowledge entry (`corpus/knowledge/host-block-base-revision.md`): prior-art line for
  kaidoku `round-29/freeze-gate.py:132`; novelty rests on the `recorded at <rev>` token
  over PROVINCE host blocks.
- C1 knowledge entry: prior-art lines for souji `souji-citation-reconcile.py:2` and the
  mori r77 spotcheck `:98-99`; novelty rests on heading-markup resolution semantics.
- Affected axes: **adjacency** (named-sibling read evidence, both directions) and
  **calibration** (receipt truthfulness — narrowed novelty clauses, the tameshi lesson of
  r64/r65); no harm to operability/freshness; no instrument byte is touched, so the
  frozen predicates stay byte-equal to the plan sentences.
- Risks: (a) a prior-art line misread as contested scope — mitigated by the not-a-governed-leg
  label plus souji's LANE-FIRST/SHARED precedent; (b) predicate-sentence drift — mitigated
  by keeping citations on record surfaces only (knowledge entries, lesson Gate, receipts),
  never in module `PREDICATE` constants; (c) tameshi's two-text tension on generality must
  be cited with both sides (`overlap.md` §Contradictions).
- Verification of the move: `grep -n` the three knowledge entries + `corpus/lessons/round-74.md`
  `## Gate` for the six cited path:line strings; `cmp` each module's `PREDICATE` constant
  against the plan's frozen sentence; re-run
  `python3 .ufo/waves/round-74/controls/score-survivors.py` — exit codes must be unchanged.

## Deliverables

- `overlap.md` (this directory) — the master table, reverse-direction table, MANIFEST row,
  contradictions, scan coverage.
- This report.
- `.ufo/waves/round-74/w1/CON01Overlap.md` — the scoped findings file (Report: trailer path).

Nothing else was written, edited, or deleted. Fleet root, sibling repos, MANIFEST.json,
`.ufo/state/`, `.ufo/watchdog.log`, `.scratch/`, and `~/.omp/agent/config.yml` untouched.
