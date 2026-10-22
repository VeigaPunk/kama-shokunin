# FinalCase06 — PG06-hydrated-blobless-fleet (round-24 postfix, wave3)

VERDICT (recommendation only, no admission): no defect observed on this surface — the per-store bare lookup keeps
the metadata-only complete control clean, absence from the other store is not turned into unreadability, and the
PRE-hydration absence assertion is genuine and load-bearing (fleet path).

PINS (sha256, my detached --no-hardlinks clone): commit 92063cfc60e217fa7e2098c568578119b16a1b95;
tools/report-landing-audit.py b9be4f42…de3b26f (= run's auditor_sha256); promisor-grid.py 30483830…f270 (= grid_sha256);
manifest d86b7bea…14cd1; population 612b0a74…ed88 / size 47 = committed GridOracle population.json → frozen47 unchanged.

EXECUTED (current arm only, 2 cells): TMPDIR=<own>/tmp/run1 python3 tests/report-audit/promisor-grid.py --arm current
--case PG06-hydrated-blobless-fleet --case PG08-complete-fleet-plain --json --keep --out <out/FinalCase06> → exit 0, stderr empty.
- PG06: exit 0, met_amended true, met_original true, problems [], defects [], kinds [], stderr_tail "",
  objects_acquired {lane: [], fleet: []}, twin_equal true.
- PG08: exit 0, met true, twin_equal true; normalized documents byte-identical, raw documents differ only in the
  fixture path field ("report"); independent re-invocation of the pinned auditor on the kept fixtures reproduces both.

PRE-HYDRATION ABSENCE (new-source probe; pinned repo untouched, in-memory monkeypatch): builder
c_hydrated_blobless_fleet = build(fleet_mark=config, blobless_fleet, hydrate_fleet) (promisor-grid.py:590);
missing_objects = --no-lazy-fetch rev-list --missing=print (…:373).
- OBSERVED: fleet pre-hydration missing set non-empty, contains report blob 0cf7ed5c…b302b (+ bfa65511…); both
  still missing at hydrate() entry; empty after hydration.
- OBSERVED: negative control (filter ignored, complete_clone=True) → ContractViolation reason "initial-empty", hydrate
  never called ⇒ the pre-hydration clause, not final hydrated emptiness, establishes partialness (fleet path).
- NOTE (not a defect): premise["fleet_missing"] is computed AFTER hydration ([]) and alone proves nothing.

STORE SEPARATION (kept PG06 fixture): cited lane commit 58866b56… is bare "absent" in the fleet store and bare
"found" in the lane store; lookup status "found"; fleet diagnosis missing []/opaque []; unknown_citation None;
opaque_hole (None, None) → no refusal identity.

RESIDUALS: the opposite direction (citation held only in the fleet store) is PG26-cross-repo-found-promisor (twin
PG27) — outside my 2-cell bound, not run; the reachable local origin fleet-origin is still in place (not deleted or
repointed) and the fleet held 9 objects before and after every run (no acquisition); no tool install needed (git
2.56.0, python 3.14.8 pre-existing); original unknown clause stays WITHDRAWN/NOT-ACHIEVED, Gitfloor H2 open.

RAW: .ufo/waves/round-24/postfix/out/FinalCase06/raw/ (grid-run1-current-PG06-PG08.json, prehydrate-probe.json,
lookup-probe.json, auditor-PG06/PG08.stdout.json, the two probe sources).
