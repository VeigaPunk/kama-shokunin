# FinalConsumer04 — errata-fleet-only-blob (generic consumer, outside the original47)

**VERDICT: the committed replay-v3 consumer is NOT masked and discriminates — red-before = refusal-2 at ERRATA line 1, corrected-after (92063cf) = ordinary exit 1 with kinds [landed-unresolved] and errata_invalid 1, a FULL strict-expectation match (exit AND exact kinds AND errata_invalid), not an exit-only credit.**

## Sources (hashes)
- driver: clone copy of `.ufo/waves/round-24/fixes/StoreLocalPresence/proof-driver-replay-v3.py` sha256 `5a570882189f7255b45c44d2a4c5ca844a0a8152656498de300c464e83d65a62` (committed at 92063cf; identical to the working file).
- after = `/fast/scratch/hyaku/kama-r24/postfix/FinalConsumer04/clone/tools/report-landing-audit.py` sha256 `b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f` = the tool at 92063cf. NOT used: fixes-dir `report-landing-audit-v7.py` (`c1956854…`) and `report-landing-audit.py` (`ca162c9c…`).
- before = pinned extraction from `2e254a1763a9c08aa07fc53081287f506c447d84`, sha256 `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` (driver-verified; clone detached at 92063cf, working tree clean; mutable production never read for before).

## Executed probe
- argv: `python3 <clone>/.ufo/waves/round-24/fixes/StoreLocalPresence/proof-driver-replay-v3.py --only errata-fleet-only-blob --after /fast/scratch/hyaku/kama-r24/postfix/FinalConsumer04/clone/tools/report-landing-audit.py --json`; TMPDIR=`/fast/scratch/hyaku/kama-r24/postfix/FinalConsumer04/tmp`; driver exit 0 (measurement only, no admission). Raw: `out/FinalConsumer04/replay-v3-errata-fleet-only-blob.json`.
- Fixture rebuilt independently (out/`fixture-facts.json`, scripts `reconstruct.py`/`controls.py`): body cites the valid lane commit `980344ac…` (type commit, reachable) **and** blob A `28912ce4…` (type blob, lane store only, 16 B); ledger row 1 `landed-unresolved A→B` with B `55743606…` (type blob, fleet store only, 17 B, absent from lane). A≠B and A≠B's store ⇒ the correction consumer is isolated; this is NOT the masked v1/v6 same-blob shape (that one is retained, not credited here).

## Decisive observations (raw exits/kinds/errata_invalid)
- BEFORE + ledger: exit **2**, kinds [], errata_invalid null; stderr `could-not-evaluate: errata line 1: unknown: unavailable required object: 55743606… is present but its content cannot be served` — the refusal names the ledger's correction token at ERRATA line 1.
- BEFORE control (same body, no ledger): exit **1**, kinds [landed-unresolved], errata_invalid **0** ⇒ not masked: the ledger alone turns the ordinary-1 into refusal-2.
- AFTER + ledger: exit **1**, kinds [landed-unresolved], errata_invalid **1**, errata_unmatched 0, defect token `28912ce4…` (`corrected_by [1]`), summary status failed ⇒ v3 `strict_match` true on all three fields.
- AFTER control (no ledger): exit **1**, kinds [landed-unresolved], errata_invalid **0** ⇒ with-ledger vs no-ledger invalid counts differ exactly as declared (1 vs 0).
- Valid-commit citation holds: every run has `by_kind.landed-omitted = 0`, `required_commits = 1` ⇒ no unrelated landed-omitted finding can mask the wrong-type citation; the wrong-type blob stays kind `landed-unresolved` and the run stays exit 1 (the correction is rejected, never accepted).

## Discrimination controls (out/control-variants.json)
correction=lane-only blob → after exit 1/errata_invalid 1; correction=lane commit → exit 0 clean/0; correction=fleet commit → exit 0 clean/0; correction=fleet-only blob → after exit 1/invalid 1 vs before exit 2 refusal. `errata_invalid` therefore tracks the correction's resolvability/type, not fixture identity; no wrong-type correction is ever accepted.

## Mechanism (out/before-vs-after-92063cf.diff)
92063cf makes presence per-store (`bare_objects` per store, never the merged view) and reconciles per canonical object id, so a store that *proves* the object is a non-commit yields conclusive `wrongtype` instead of the other store's `unknown` ⇒ the fleet-only blob correction becomes an invalid row instead of a refusal.

## Residuals / limits
- The red before is a **refusal (could-not-evaluate)**, not a wrong verdict: under the exit taxonomy it is repair/discrimination evidence, never a mutation kill.
- After side reports `corrected=1 / uncorrected=0` for the defect while also counting the row invalid; a reader consulting only `uncorrected` could misread it — the tool's own `status=failed`/exit 1 and `errata_invalid=1` account for it (observation, not a defect).
- Scope held: one consumer only; no grid, no selftest, no default mutant driver, no historical suite (47 frozen cells and the withdrawn original clause untouched); the other five replay-v3 consumers and the v1/v6 same-blob shape were not exercised.
- No tool installs (git 2.56.0, python 3.14.8 from the base image).
