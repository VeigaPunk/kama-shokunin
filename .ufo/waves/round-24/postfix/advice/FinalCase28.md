# FinalCase28 — PG28-unhydrated-blobless-lane (round 24 postfix, current arm)

VERDICT: no defect found in the pinned current arm for PG28; the registered result reproduces and the graded twin equality holds. Recommendation only — not a self-admission, no score promotion.

Pin: clone detached at 92063cfc60e217fa7e2098c568578119b16a1b95. tools/report-landing-audit.py b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f; promisor-grid.py 30483830e0461898bd9b710603e755b08cf58e2a2a215a747098ebbe0383f270; expectations manifest d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1 (= grid MANIFEST_SHA256, 47 cells, untouched). Provenance/argv: `.ufo/waves/round-24/postfix/out/FinalCase28/provenance.txt`.

Graded run (CURRENT arm only, exactly 2 cells; argv above; exit 0):
- PG28-unhydrated-blobless-lane: exit 0, defects [], kinds [], met_amended true, problems [], stderr empty, objects_acquired {lane: [], fleet: []}, document status "clean" (required 1, round_commits 1, uncorrected 0).
- PG36-unused-missing-blob-plain (graded twin): exit 0, defects [], met true, objects_acquired {lane: [], fleet: []}.
- Twin: PG28.twins[PG36]=true and PG36.twins[PG28]=true; the two normalised verdict documents are identical (no twin mismatch, no constraint failure).
- Original view of PG28 is UNMET ("exit 0 != 2") and is listed in withdrawn_original_failures / amendment_changed_cases: the withdrawn unknown clause is not silently passed, and amended tests do not retroactively satisfy it.

Decisive observations (bounded probes, own scratch; raw JSON beside this file):
1. Premise of the kept PG28 fixture: the lane is a real file:// blobless partial clone (remote.origin.promisor=true, remote.origin.partialclonefilter, pack-8a32dfc9….promisor); `--no-lazy-fetch` missing set = {56d7b323865c731da81e0225cf109d66f0480919} (the unused "f" blob); fleet missing = ∅; origin present and reachable (kept in place, never repointed).
2. The two-root diagnosis is NOT an audit-completeness precondition: in-process instrumented run of the pinned auditor on that fixture gave exit 0 / 0 defects, and RepoStore.missing, unknown_citation and opaque_hole were never invoked. Positive control taken after the snapshot: the same lane, asked explicitly, yields missing={56d7b323…}, opaque=∅ — the unrelated hole exists and the audit never consulted it.
3. An absent citation keeps the registered result on this same surface (PG28 fixture + fabricated 40-hex): exit 1, defects landed-unresolved + unresolved-full-hash (token 0123456789abcdef0123456789abcdef01234567), verdict document present; counters show unknown_citation consulted for that token with matched_store=null and opaque_hole → no hole, so no refusal; objects_acquired empty.
4. A hole the audit must read still refuses, and it is not the diagnosis path: same surface with the lane carrying corpus/SOURCES.md → exit 2, stderr "could-not-evaluate: unavailable required object: master:corpus/SOURCES.md (051975b0ced83169116c235e7691c0a1a8313300)", stdout empty (no verdict document), objects_acquired empty, diagnosis counters empty (required-read path).
5. PRE-hydration absence assertion (new): instrumenting promisor-grid.hydrate shows the initial missing set is established on the clone BEFORE hydration (missing_at_hydration_time={56d7b323…}, objects_before=2) and only afterwards is it empty (premise lane_missing=[]). Negative control: a complete clone that claims to be blobless is refused with ContractViolation reason "initial-empty" and hydrate is never called — final hydrated emptiness cannot stand in for initial partialness.

Residual risk / verification gaps:
- Only 2 of 47 cells were run (PG28, PG36). No whole-grid, no 45-cell, no frozen/both-arm claim (sensitivity measures the current arm only; no CNE2 claim).
- PG28's opaque set is empty, so this cell exercises only that a blob hole is not a precondition; the hidden-name branch (missing tree/commit) is not exercised on this surface.
- Probes 3 and 4 are my own derived fixtures, not manifest rows; their expectations (registered result preserved; content-derived refusal without a verdict document) are derived from oracle-amendment-1, not from registered cells. Probe 3 duplicates the shape of PG37/PG41 on a different surface; those cells were not run.
- Nothing was self-admitted, no expectation or fixture byte was edited, no production path written.
