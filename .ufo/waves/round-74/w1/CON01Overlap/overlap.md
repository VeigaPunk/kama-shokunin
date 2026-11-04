# CON01Overlap — cross-lane overlap scan, kama round 74 w1

Scan target: the round's three frozen instruments (`tools/round74-selfdesc-canon.py` C1,
`tools/round74-receipt-claim-binding.py` C2, `tools/round74-province-host-drift.py` C3,
frozen in `plans/round-74-claims.md`) against all 20 sibling lane repos under
`/home/vgpnk/Projects/shokunin/`. Read-only everywhere except this wave out dir.
Date: 2026-11-04. Scanner seat: CON01Overlap (kama lane, round 74, wave 1).

Overlap classes: **identical** = same predicate over the same surface · **strong** = same
instrument class with a materially shared mechanism or the same graded surface, different
predicate · **weak** = same broad frame, different surface and mechanism · **none**.

## Master table — sibling tools / registry files / newest lessons vs kama's three classes

| lane | class | surface (path:line) | overlap | action for kama's report |
|---|---|---|---|---|
| souji | C1 | `souji-shokunin/tools/souji-citation-reconcile.py:2` — r37–r39 self-assessment citation reconciler: re-derives register rows over committed bytes, binds citation line ↔ receipt blob at `receipt_rev`, r38 arm binds a 40-hex commit id with an ancestor check | strong | cite as prior art in the C1 knowledge entry (same self-assessment-reconciler class; different leg — citation→receipt binding, not capability-heading repertoire resolution); no contested scope |
| mori | C1 | `mori-shokunin/corpus/lessons/round-77-verifier-spotcheck.md:98-99` and `:193-195` — non-author closures grade *canonical SCORECARD capabilities-table headings* (`grep -c 'Capability \| What it can now do'`, 26 → 26 entering→landing); r75 discharged "the register the closures grade against does not match the demonstrated state" as its C1 | weak | cite as same-surface/different-check precedent (heading-count continuity vs bold/unbolded resolution semantics); no contested scope |
| tameshi | C1 | `tameshi-shokunin/tools/wave-reconcile.py:2` (r73–r75) — record-span-scoped binding of the round record's claims to wave-artifact re-derivations | weak | cite in the C1/C2 knowledge entries as the paragraph-scoping precedent on a different surface (wave artifacts, not receipts) |
| tameshi | C2 | `tameshi-shokunin/tools/receipt-revision-gate.py:2-4` — r55–56, byte-frozen: binds a receipt's own `rev=` to the revision it certifies (equality, content-drift, ancestor arms); "a verdict is evidence only for the content it was measured against" | strong | cite as prior art in the C2 knowledge entry (`receipt-tip-binding.md` line) and one prior-art line in the C2 receipt, per the T74W1CN1 convention |
| tameshi | C2 | `tameshi-shokunin/tools/receipt-commit-bind.py:1-2` — r65–66: commit-message receipt-name spans bound to commit bytes across line breaks; delimited-token v2 kills suffix collisions | strong | cite as the line-split-escape sibling of wrapped/offset claims (message spans vs record paragraphs) |
| kaidoku | C2 | `kaidoku-shokunin/tools/round-62/base-binding-sweep.py:2-4,20-31` — r62: threads the receipt's OWN `base:` 40-hex rev-name binding scanned from committed bytes into the byte-pinned frozen gate | strong | cite as explicit-revision-binding prior art (self-binding receipt→base; kama's leg is cross-binding record→receipt) |
| tsukuroi | C2 | `tsukuroi-shokunin/tools/check-revision-binding.py:1-2` — r17–18: every tool `--revision` gate bound to landed/pushed revisions via sandbox probes | weak | cite frame-level only (tool gates, not record↔receipt) |
| souji | C2 | `souji-shokunin/corpus/lessons/round-57.md:170-172` — connector ruling: "receipt revision binding exists in other lanes … none binds the instrument's committed blob at the receipt's revision — **LANE-FIRST on C2's digest binding, SHARED on the general idea**" | weak | cite as the house precedent for how to phrase kama's novelty (specific predicate lane-first, general frame shared) |
| kengaku | C2 | `kengaku-shokunin/corpus/lessons/round-72.md:126` — "a presence check read as an attribution check": revision tokens present-but-unbound (swapped) still print ok | weak | cite as the named wrapped/offset failure class in a sibling lesson (kills the same escape kama C2 kills) |
| kaidoku | C3 | `kaidoku-shokunin/tools/round-29/freeze-gate.py:132` — per-commit any-change disclosure walk over `git rev-list --reverse '{freeze}..{measured}' -- path` (finding `INSTRUMENT_REVISED`) | strong | cite as the closest mechanism prior art for C3's preservation leg (two-revision byte-identity of a recorded block); different surface (frozen instrument revisions) and no `recorded at` token semantics |
| kotoba | C3 | `kotoba-shokunin/verifiers/check_host_skill_surfaces.py` (r82+, per `kotoba-shokunin/corpus/lessons/round-82-verifier-spotcheck.md:35-37`) — live host installed-skill drift census (`identical/drifted/lane-absent` counts) | weak | cite as different-frame adjacency: live re-measurement, no recorded-revision byte-preservation |
| tameshi | C3 | `tameshi-shokunin/tools/additivity-receipt.py:1-4` — r63: receipts on committed bytes disclosing raw vs CR-normalized rewrites; per-commit EOL attribution | weak | cite as the byte-preservation receipt frame; note tameshi already cites kama's own audit as prior art (see reverse table) |
| kumitate | C3 | `kumitate-shokunin/corpus/lessons/round-74.md:4,68` — "omp-census host drift (NEW, routed — not a round-74 claim)" | none | no action (routed, explicitly not claimed) |
| audio, chousa, game-dev-2d, game-dev-3d, kagi, kaidoku (C1/C3), kake, kasegi, kengaku (C1/C3), kotoba (C1/C2), kotodama, lore, mado, mori (C2/C3), revenger, souji (C3), tabi, tsukuroi (C1/C3) | — | no files or lessons in any of the three classes (see §Scan coverage) | none | none |

No lane scores **identical** on any class. No sibling implements, amends, or names
kama's three round-74 module names: `grep -rn "round74-selfdesc-canon\|round74-receipt-claim-binding\|round74-province-host-drift"` outside `kama-shokunin/` returns 0 files
(only `kama-shokunin/plans/round-74-claims.md` and
`kama-shokunin/.ufo/waves/round-74/controls/score-survivors.py` carry them).

## Reverse direction — sibling round-70+ closures / spot-checks / round-74 waves touching kama

| lane | surface | what it says about kama | overlap class | action |
|---|---|---|---|---|
| kumitate | `kumitate-shokunin/.ufo/waves/round-74/w1/K74ConnectorOverlap.md:11,16` | r74 connector-overlap swept all 20 siblings; kama verdict **none** (zero surface overlap); observed "kama-shokunin: mid-round 74a2 (task KamaR74a2)… zero surface overlap" | none | record in the round report as live-sibling observation; no citation owed |
| tameshi | `tameshi-shokunin/.ufo/waves/round-74/w1/T74W1CN1.md:47-53,150,173-198` + `tameshi-shokunin/corpus/lessons/round-74-verifier-spotcheck.md:149` | r74 connector cites kama `tools/append-only-audit.py:587` as two-lane evidence that "range additivity, per-commit line removal" is **general**; the r74 closure ruled adjacency unchanged with "the KAMA sibling instrument is reported as a different frame and the pattern is **not** claimed general (one lane only)" | weak (frame-level, already mutual) | none required; if kama cites tameshi's binding gates, carry both tameshi texts (see Contradictions) |
| tsukuroi | `tsukuroi-shokunin/.ufo/waves/round-74/w1/C1Connector.md:152-153` | r74 C1 connector's overlap-risk analysis: measuring `systemd-sysupdate.timer` does not overlap kama (kama inspects serving ports; OS-level maintenance) | none | none |
| kotoba | `kotoba-shokunin/.ufo/waves/round-74/w1/ScoutSibKamaKasegiR74.md:3,23` | r74 C2 sibling re-read: kama `adjacent`, clause 2, "nothing differs from r49 in class or basis" | none (scope arbitration, not instruments) | none |
| kengaku | `.ufo/reports/round-72/kengaku.md:237,291`; `.ufo/reports/round-73/kengaku.md:15,19` | r72 SiblingOverlapR72 named kama's `KAMA_R50_CANARY` + `/proc/<pid>/environ` arm as a surface-level sibling site (process-provenance), routed not absorbed; r73 retained the observation without copying | none (process-provenance class, not r74 classes) | none |
| kake | `kake-shokunin/corpus/lessons/round-71-verifier-spotcheck.md:59`; `.ufo/reports/round-71/kake.md:25,30` | r71 closure admits S132 = kama's `corpus/knowledge/self-assessment-at-writing.md` (sha256 `cd6e3730…`) as the sourced basis for kake's C1 | weak (knowledge surface, not tools) | none; kama's file is read-only cited, unmodified |
| kotodama | `kotodama-shokunin/.ufo/waves/round-74/w1/ConnectorSiblings.md:35` | r74 connector checked kama for completeness: no overlap | none | none |

## MANIFEST.json — kama's last closure verdict

`MANIFEST.json:41567-41579` (`rounds[]` index 1135): kama round 73, 2026-11-04, verdict
**`rejected-honest-stop`** (admitted: false) — "lane's own honest stop on C2's full frozen
clean-fixture clause (unprovable on committed bytes); landed work verified and stays in the
lane." Axis verdicts: calibration/operability/freshness **improved**; depth/coverage/
adjacency **unchanged**. Trends expansion/quality/discernment improved.
`capabilities_added`: round-scope-cases, receipt-claim-binding, province-host-drift.
Six routed defects: (1)→this round's C1, (2)→C2, (5)→C3, (3)→calibration SCORECARD row,
(4)→stays queued (disclosed), (6)→lesson mistake 2. Action: the round report records this
carry-in grounding (already the plan's §Carry-in); no contested scope.

## Contradictions stated, not smoothed

1. **tameshi's two round-74 texts disagree on generality** unless read carefully:
   `T74W1CN1.md:150` rules "range additivity, per-commit line removal" **general** as a
   frame on kama+kaidoku evidence, while `round-74-verifier-spotcheck.md:149` rules the
   kama citation "a different frame and the pattern is **not** claimed general (one lane
   only)". Reconcilable (frame-general vs novelty-claim; the connector itself narrows
   novelty to the attribution element, `:211-213`), but a kama report citing either text
   should carry both.
2. **Minor mislabel in tameshi's citation of kama**: `T74W1CN1.md:53` names the 1529-line
   file `kama-shokunin/tools/round50-append-audit-v5-check.py`, but the 1529-line file with
   `rev-list --topo-order --reverse --parents` at `:587` is `kama-shokunin/tools/append-only-audit.py`
   (verified: `wc -l` → `append-only-audit.py` 1529, `round50-append-audit-v5-check.py` 545).
   Kama's report should cite the correct path if it echoes the receipt.

## Scan coverage (what was searched, all 20 siblings)

- Whole-repo filename census for `selfdesc` → only kama's own
  `tools/round42-selfdesc-reconcile.py` (plus its `__pycache__`).
- Every sibling `tools/**` filename + content against
  `canon|selfdesc|reconcile|receipt.*bind|claim.*bind|host.*drift|host-identity|recorded at`;
  every sibling `registry*` path; each lane's 5 newest `corpus/lessons/*.md`.
- `git -C <lane> log --since=2026-10-28 --name-only -- tools/ registry/ verifiers/`
  filtered to keyword-matching paths (catches "recently amending").
- `*-shokunin/corpus/lessons/*verifier-spotcheck.md` round ≥ 70 and
  `.ufo/reports/round-7[0-4]/*.md` grepped for `kama`.
- Sibling `.ufo/waves/round-74/**` grepped for `kama`.
- MANIFEST.json parsed (roster + all 1139 `rounds[]` entries).

Full commands and outputs: `report.md` in this directory.
