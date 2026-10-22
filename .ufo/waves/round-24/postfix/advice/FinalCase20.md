# FinalCase20 — PG20-missing-fleet-tree-plain (round-24 postfix wave3, pin 92063cfc)

**VERDICT: PASS.** The current arm keeps the *actual* unavailable-object refusal and its strong identity: no metadata substitution, no substituted verdict. No actionable defect in scope.

**Pin / provenance (all observed in my own clone)**
- clone `/fast/scratch/hyaku/kama-r24/postfix/FinalCase20/clone` (`git clone --no-hardlinks`), detached `92063cfc60e217fa7e2098c568578119b16a1b95`.
- auditor `tools/report-landing-audit.py` sha256 `b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f`; grid `tests/report-audit/promisor-grid.py` sha256 `30483830e0461898bd9b710603e755b08cf58e2a2a215a747098ebbe0383f270`.
- expectations manifest sha256 `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1`; `population_sha256 612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88` (47 cases).
- builder `c_missing_fleet_tree_plain` = `build(root, tmp, drop=("fleet_tip_tree",))`; PG20 row: frozen/original/amended all `{exit 2, kinds null, defects null, reason_class "unavailable"}`, `names_any_of ["$fleet_tip_tree"]`, `twin null`.

**Executed (2 cells, current arm only; no grid/selftest/mutant run)**
- `TMPDIR=<mine> python3 tests/report-audit/promisor-grid.py --arm current --case PG20-missing-fleet-tree-plain --json` → exit 0 (`out/FinalCase20/pg20-current.json`).
- `... --arm current --case PG19-missing-fleet-tree-promisor --case PG20-missing-fleet-tree-plain --json` → exit 0 (`out/FinalCase20/pg19-pg20-current.stdout`).
- PG20 row: `exit=2`, `met=true` (problems/amended_problems/original_problems all `[]`), `defects=null`, `kinds=null`, `document=null`, `objects_acquired {lane: [], fleet: []}`, traceback/internal_error/timeout/leak all false; arm `violations=0`, `amended_view_met 1/1`. PG19 row (same run): `exit=2`, `met=true`, acquired empty, `document=null`.

**Decisive observations** (full stderr captured by my own re-derivation, `out/FinalCase20/rederivation.json`)
- full stderr = `could-not-evaluate: unavailable required object: .ufo/reports/round-1/kama.md at fleet HEAD (tip tree b1e11739fedfb736f2936bd9addf7e4a286d462e, <fleet>): git show HEAD:.ufo/reports/round-1/kama.md ... rc=128 fatal: path '...' exists on disk, but not in 'HEAD'`.
- the strong pin is met by the *actually missing* object: premise `fleet_missing == [b1e11739…]` (exactly the dropped fleet tip tree) and that OID is in the refusal text; stdout is 0 bytes — no verdict document; no `partial clone`/`promisor` text (premise `fleet_promisor=false`, `lane_promisor=false`) → neither a metadata refusal nor a verdict.
- refusal is object-specific, not a blanket precondition: same fixture **without** the drop → exit 0 with a clean JSON verdict; same fixture with an unrelated lane subtree hole → exit 0 clean verdict (the scoped missing cache does not promote unrelated holes).

**Twin equality: not established, not claimed.** PG20's declared twin is `null`; the manifest link `PG19→PG20` is one-way. Executed pair: `twins {PG20: None}` / `{PG19: None}`, `twin_equal null`, `twin_compared 0`, `twin_pairs_compared []`, `twin_mismatch []` — both rows are refusals with no verdict document, so two missing documents are **not** twin equality; any PG19/PG20 "identical refusal" claim stays manual.

**Residuals / verification gaps**
- Frozen arm **not** executed (out of bounds); inspected only: the r23 base blob has no `required_read` (grep count 0) and its fleet-report failure text is `round N: cannot read <rel> at fleet HEAD: …` (base line 312) with no object id → the strong identity is a current-arm property; the frozen column's PG20 metness is historical.
- The grader's strong-name pin is "OID appears somewhere in stderr", not "OID is the object that is actually missing"; my controls cover the causal link for this cell, but a mutant that prints the OID while refusing for another reason would still satisfy the pin (no mutant run in my lane).
- `objects_acquired` covers the audited lane/fleet only; PG20's fleet has no remote at all, so this cell has no fetch channel; the promisor sibling PG19 (absent `remote.origin.url`) also acquired nothing.
- PM08 (`--no-lazy-fetch` gate) is static/manual by contract — not asserted here.

No production writes; scratch under `/fast/scratch/hyaku/kama-r24/postfix/FinalCase20/`. Raw artifacts: `.ufo/waves/round-24/postfix/out/FinalCase20/{provenance.json, pg20-current.json, candidate.json (= same bytes as pg20-current.json), population.json, pg19-pg20-current.stdout, pg19-pg20-current-artifacts/, rederivation.json}`.
