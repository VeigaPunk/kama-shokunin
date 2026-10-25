# ConnSiblingScope — sibling-overlap scan (kama round 33, wave 1)

Seat: ConnSiblingScope (connector). Leaf only. Tools installed or updated: none (pacman remains paused; no package was required). No file outside this report was written. No sibling tree, fleet `PROTOCOL.md`, host config, or filed report was edited. No endpoint was sampled.

## Axes

- **C1 calibration:** KQ39 census of the three false round-32 Scorecard C2 gate-control citations (`false_at_writing` 3, valid corrections 0→3).
- **C2 operability:** four replay receipts, clean gate-tip plus thin-row, empty-exit-map, and missing-path (`complete` 0/4→4/4).
- **Adjacency (held, not a claimed delta):** do not absorb protocol gate-standard text, kake's census checker, or any sibling SCORECARD.

## Evidence

Latest committed overlap record is `.ufo/waves/round-31/w1/out/ConnSibling/overlap.md` (added `3b1e84f`, 2026-10-23). It is about a different pair of surfaces: the b11755 `/v1/chat/completions` adapter, and that round's SCORECARD claim-table rows. Its still-binding negative is: kake owns `registry_count_check` (kake round-43; kake itself called that checker "overclaimed as a gate"), and kama must not import it. Contested holdings on that scan: 0. Round-32 prepared `ConnGrammarOverlap` for the S192 grammar item; `.ufo/waves/round-32/w1/out/` is absent, so that scan was not committed. Round-29 `.ufo/waves/round-29/w1/out/ConnectorSiblings/overlap.md` remains the nearest writing-revision verdict: no sibling province owns statement-at-writing checks; tsukuroi's and kaidoku's self-assessment tools are their own claims.

This round's objects are path-local to kama:

| Object | Path | What the bytes are |
|---|---|---|
| Clean r32 gate run | `.ufo/waves/round-32/c2/gate-tip.out` | `registered 10 unregistered 0 defective 0` |
| thin-row receipt (the one that shows the defect) | `.ufo/waves/round-32/c2/controls/thin-v2.out` | `defective …/count-c1.py: thin-row` (also `empty-entry` and `empty-exit-map` on later lines) |
| empty-exit-map receipt | `.ufo/waves/round-32/c2/controls/noexit-v2.out` | `defective …: empty-exit-map` |
| missing-path receipt | `.ufo/waves/round-32/c2/controls/badpath-v2.out` | `defective …: missing-path:.ufo/waves/round-999/count-c999.py` |
| Three stale wildcard members | `thin-row-v2.out`, `empty-exit-v2.out`, `nonexistent-path-v2.out` | identical base-tree body: `unregistered` round-17 and round-26 counters, `registered 7 unregistered 2 defective 0` |
| C1 correction | `SCORECARD.md` heading `### Round 33 — correction of round-32 gate-control receipt references` (lines 1835–1848) | maps the three faults onto `thin-v2.out`, `noexit-v2.out`, `badpath-v2.out` |
| C2 replay quartet | `.ufo/waves/round-33/c2/final/gate-tip-r33.out` plus `controls/{thin-row,empty-exit-map,missing-path}-r33.out` | `FORMAT=KAMA_GATE_RECEIPT_V1`; gate-tip `--repo` is this lane, `SOURCE_REV=967d88528c1d…` |

`tools/round33-claim-audit.py` reads only `git show <rev>:` of `SCORECARD.md` and those six kama receipt paths (`FAULTS`, lines 19–35). `met` is `false_at_writing == 3` at statement rev `dc4258bdb08d658f1c5b15abc8378461659bd155` and three valid tip mappings (lines 145–146). `legacy_mislabels_at_tip` is printed and is not part of `met`. `tools/round33-gate-receipts.py` audits `.ufo/waves/round-33/c2/final` inside `--repo`. Neither script names a sibling, `PROTOCOL`, or a host path. `SKILL.md:1315–1325` registers `tools/gate-registry-check.py` as **owner: kama**. `SKILL.md:1330–1354` says the receipts grade that registry instrument, not endpoint health, and that capture writes only under `.ufo/waves/round-33/c2/`.

Sibling `PROVINCE.md` files under `/home/vgpnk/Projects/shokunin/*-shokunin/` (20 lanes besides kama) have no match for `gate-registry-check`, `thin-v2.out`, `thin-row-v2`, `noexit-v2`, `badpath-v2`, `round-32/c2/controls`, or `instrument-registry gate`.

## Boundary (named, not absorbed)

**Neither the four r32 gate outputs nor the Scorecard citation repair belong to another lane.**

The collision is the word "gate", not the object:

- Fleet roster `shokunin.conf:20` assigns **protocol** `protocol soundness, gate integrity`. `corpus/knowledge/cross-lane-scope.md:44` hands fleet gate-standard changes to protocol. Round-12 `.ufo/waves/round-12/advice/ProvinceOverlap.md` already split that: a lane-local evidence gate may comply with the outer exit shape; editing `PROTOCOL.md` is a protocol cutover. These four receipts do not change that standard. They replay kama's instrument-registry grader.
- **Kake** owns `registry_count_check` and kake's SOURCES census (round-31 overlap). Kama's C1 object is one kama SCORECARD row plus three kama receipt paths. Importing kake's checker would not move `false_at_writing`.
- **Tsukuroi / kaidoku** own their own self-assessment counters (round-29 overlap), not this row.
- **Kengaku** owns eval quality, **kumitate** route selection, **kagi** credentials, **kotoba** instruction text, **operator** host units (`PROVINCE.md:40–53`, `cross-lane-scope.md:22–31,49–51`). None of those predicates change if only these receipt bytes change. The falsifier in `cross-lane-scope.md:32` therefore keeps the finding in kama.

`thin-v2.out` also prints `empty-exit-map`, while the correction assigns that fault to `noexit-v2.out`. That is an in-lane evidence-shape fact. It is not a second owner's claim, and it is not a reason to edit the historical file.

## Why no edit outside kama

This seat writes only this report. An outside edit cannot satisfy either counter: both grade git blobs in the `--repo` they are given, which is this lane. Rewriting fleet `PROTOCOL.md`, a sibling SCORECARD, kake's checker, `~/.config`, `~/.omp`, or systemd would violate `PROVINCE.md:45–49` and the adjacency rule, and would leave `git show dc4258bd:SCORECARD.md` and the receipt paths unchanged. The filed fleet report stays immutable; the lineage note already appended in kama `SCORECARD.md:1850–1859` does not rewrite it. The three stale `*-v2.out` bodies stay byte-intact: they are the false citations. Replacing them would not clear `false_at_writing` (that count is pinned at the writing revision) and would only shrink the disclosed `legacy_mislabels_at_tip` residue.

## Proposed move

Keep the repair inside two kama path sets and do not "fix the gate" anywhere else.

1. C1's only integrating edit is the append-only SCORECARD map already shaped at lines 1835–1848: `thin-row` → `thin-v2.out`, `empty-exit-map` → `noexit-v2.out`, `missing-path` → `badpath-v2.out`, each citing the one observed defect line. Do not retarget those rows at the stale filenames, at kake's checker, or at `PROTOCOL.md`.
2. C2's only integrating artifacts are the four files under `.ufo/waves/round-33/c2/final/`. Do not back-fill `EXIT_CODE` / `EVALUATED_REV` into the round-32 `*-v2.out` bodies; those historical files are not the 4/4 population (`preregistration.json` `claim_independence`).
3. Leave the three stale bodies and the filed round-32 report untouched. Protocol may be told, in the lane report only, that kama did not propose a fleet Gate-standard change.

That keeps C1 a correction census of three frozen false citations and C2 a four-receipt replay. It does not spend either claim on another lane's gate.

## Risks

- Reading round-31's "contested scope: 0" as if it covered these receipts would hide the protocol-noun collision. The path check above is the current evidence; the 2026-10-23 scan is not.
- `met` ignores `legacy_mislabels_at_tip`. A later tip rewrite of the stale files can look like cleanup while the calibration predicate stays green. That rewrite is still out of scope.
- `thin-v2.out` carrying extra defect lines can be misread as the empty-exit receipt. The correction table, not the filename stem, is the C1 key.
- Round-33's own counters are prose in `SKILL.md`, not five-column registry rows (verifier note in `corpus/lessons/round-33-verifier-spotcheck.md`). Promoting them into the registry is a later kama-registry question, not a protocol edit and not this claim.

## Verification (for L1; not run here)

- `git show 3b1e84f:.ufo/waves/round-31/w1/out/ConnSibling/overlap.md` still contains the kake non-absorption paragraph.
- `git grep -n -e gate-registry-check -e thin-v2.out` across sibling `PROVINCE.md` files stays empty.
- `python3 tools/round33-claim-audit.py --repo . --statement-rev dc4258bdb08d658f1c5b15abc8378461659bd155 --tip <full tip>` moves only when kama `SCORECARD.md` or the six named receipt blobs move.
- `python3 tools/round33-gate-receipts.py audit --repo . --tip <full tip> --source-rev 967d88528c1d83535563f971863f7855f76b4849 --receipt-dir .ufo/waves/round-33/c2/final` does not read `PROTOCOL.md` or a sibling checkout.
- Confirm this seat's diff is only `.ufo/waves/round-33/w1/out/ConnSiblingScope.md`.
