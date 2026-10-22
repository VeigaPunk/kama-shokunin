# FinalCase02 — PG02-complete-fleet-promisor-config (current arm)

VERDICT: cell met; no falsification found in the audited candidate. Recommendation only — no score promotion, no self-admission, no claim about the withdrawn original clause or Gitfloor H2.

## Pins (all verified, not assumed)
- clone: `/fast/scratch/hyaku/kama-r24/postfix/FinalCase02/clone` (`git clone --no-hardlinks --no-local`), detached `92063cfc60e217fa7e2098c568578119b16a1b95` (== production HEAD, tree clean).
- auditor `tools/report-landing-audit.py` sha256 `b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f`; grid `tests/report-audit/promisor-grid.py` sha256 `30483830e0461898bd9b710603e755b08cf58e2a2a215a747098ebbe0383f270`; manifest `promisor-grid-expectations.json` sha256 `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1`; population_sha256 `612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88`, 47 cells. No proposal/default producer used.

## Executed (exactly 2 cells, current arm only)
- argv `python3 tests/report-audit/promisor-grid.py --arm current --case PG02-complete-fleet-promisor-config --case PG08-complete-fleet-plain --json --out <out>` with `TMPDIR=/fast/scratch/hyaku/kama-r24/postfix/FinalCase02/tmp` (existing, owned); grid exit 0, stderr empty (0 bytes).
- PG02: exit 0 (normal actual verdict), graded met=true, amended_problems=[], original_problems=[], defects=[], kinds=[], reason_class null, stderr_tail empty, no traceback/internal_error/timeout/leak, objects_acquired {lane:[], fleet:[]}, twin `PG08-complete-fleet-plain` → `twin_equal=true`, document identical (status "clean", required_commits 1, by_kind all 0). PG08: same exit 0, twin_equal=true. `violating_cases=[]`, `twin_mismatch=[]`.
- Manual re-run of the pinned auditor on the same fixture (argv `--lane-repo/--fleet-repo/--rounds 1/--json/--no-errata`): exit 0, stdout sha256 `fe4bc4daf456d45f59093f514e4d503515527686f839cbf8cec5a2459c7f71ae`, stderr empty, objects_acquired {} empty, normalised document == grid document (True).

## Decisive observations (premise, rebuilt with the grid's own builder)
- fleet is metadata-only promisor: `remote.origin.promisor=true`, `extensions.partialclone=origin`, no filter remote, no `.promisor` markers; `remote.origin.url` points at an absent path (so no lazy fetch could succeed). fleet promisor_backed=true, lane promisor_backed=false; fleet 9 objects / lane 5, `missing_objects` empty for both.
- Cross-store asymmetry is real in both directions: fleet does NOT hold the cited lane commit (`fleet_has_lane_commit=false`), lane does NOT hold the report blob (`lane_has_report_blob=false`). The verdict therefore required resolving the citation in the lane store while the marked store could not serve it → absence from the other store was not read as unreadability.
- Mechanism (tools/report-landing-audit.py:190-312): per-store `bare_objects` + `cat-file --batch-check`, RANK absent0<wrongtype1<unknown2<ambiguous3<found4; a store that cannot serve a token only contributes rank-0 "absent", "unknown" requires bare-found-with-unpeelable-target **in that same store**, and `refuse_unknown` (:482) refuses only for absent+referenced/opaque. Hence a marked-store miss cannot become exit 2 here.
- Discrimination control (manual, NOT a graded cell): same builder family + same fleet promisor marking + a fabricated 40-hex citation → exit 1, kinds `landed-unresolved`,`unresolved-full-hash`, status "failed", objects_acquired empty. So PG02's clean exit 0 is not vacuous (had the citation path been dead, `landed-omitted`/`unresolved-full-hash` would have fired).

## Residuals / verification gaps
- The frozen (r23) column of PG02 (exit 2, reason_class "metadata") was NOT re-measured — lane bound says current arm only; the historical reproduction stays unverified by me.
- `bare_objects` raises EvalError ("citation ... names a ref") when git resolves a same-named ref for a hex-like token; that path is not exercised by PG02 and is unexercised here (inference from code, not observed).
- PG08's builder is `build(root,tmp)`, identical to PG07's, so the plain twin is not fleet-specific; the PG02/PG08 pair is nonetheless the correct marked-vs-unmarked control for PG02.
- Grid twin equality compares path-normalised documents only; raw documents differ solely in fixture paths.
- The manual probe's own `survivors` list contains the probe process itself (path self-match), not an auditor leak; the grid's leak check on the same cell reported `leaked=false`.
- Original evidence unchanged: no expectation, manifest, grid, auditor or production file was edited; the withdrawn original unknown-citation clause is untouched.

Raw evidence: `.ufo/waves/round-24/postfix/out/FinalCase02/` (grid-pg02-pg08.json, candidate.json, population.json, pg02-fixture-premise.json, pg02-manual-audit.json, pg02-manual-stdout.json, discrimination-control.json, probe_*.py, README-evidence.txt). Scratch: `/fast/scratch/hyaku/kama-r24/postfix/FinalCase02/`.
