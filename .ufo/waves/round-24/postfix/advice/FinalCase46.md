# FinalCase46 — PG47-opaque-tree-with-unresolved-fabricated-token (current arm)

VERDICT: NOT FALSIFIED. PG47 met on the current arm (graded `met_amended=true`, `met_original=true`). The supplemental metadata-only companion gives exit 2 on both variants, and this is diagnostic-only (2→2), not a document equality.

Pin and identities: clone `--no-hardlinks` detached at 92063cfc60e217fa7e2098c568578119b16a1b95. auditor b9be4f42…6b26f, grid 30483830…0f270, manifest d86b7bea…14cd1 (47 cells), population 612b0a74…ed88. Authority inputs: prereg 6dde0d72…, amend-1 930b087a…, snapshot 1f5a4699…, supplement-2 4600a8c3…. git 2.56.0, Python 3.14.8. No tools were installed.

Primary argv (cwd=clone, TMPDIR=/fast/scratch/hyaku/kama-r24/postfix/FinalCase46/tmp/grid): `python3 tests/report-audit/promisor-grid.py --arm current --current <clone>/tools/report-landing-audit.py --case PG47-opaque-tree-with-unresolved-fabricated-token --json --keep --out out/FinalCase46/grid`. Grid exit 0, graded=1, violations=0, no traceback, internal_error, timeout or leak.
- Premise (observed in `grid/premise.txt`, `--no-lazy-fetch`): lane `master:d` = 2a675c1a…8ab6. It is the only `?` object in the lane walk, and the fleet walk has none. FAKE 01234567…01234567 is absent from both stores (`cat-file -e` returns 128). The fleet report cites the present lane commit and has the Notes line `fake <FAKE>`. Lane config: `remote.origin.promisor=true`, `extensions.partialclone=origin`, url `<case>/absent-remote.git` (the target does not exist). The pack dir is empty, so there are no markers.
- Cell result: exit 2 (expected 2, `reason_class` unavailable). defects/kinds are null and there is no verdict document. `objects_acquired` is empty for both lane and fleet. Refusal identity: `could-not-evaluate: round 1: unknown: unavailable required object: <FAKE> could be hidden behind the missing tree or commit 2a675c1a… in <lane>`. It names both `$fake` and `$missing_subtree` and contains neither `partial clone (` nor `promisor pack`.
- Twin: none. The manifest has `twin: null`, `twin_compared=0`, and no twin document was compared.
- [INFERENCE] From reading source, the refusal comes from `refuse_unknown` → `opaque_hole` (audit.py:505-510). The `--filter=blob:none` walk is rooted only at the pinned lane tip, so it reports tree `d` as a non-leaf hole, and only because a citation is unresolved. That matches supplement-2's rule. No blanket precondition is visible on this path.

Supplemental companion (OUTSIDE the 47; does not add to the score, the manifest or any twin link). Driver: `out/FinalCase46/supplement/supplement_driver.py` (sha256 af170f41…a865), run with TMPDIR=<scratch>/tmp/supp, exit 0.
- It built the UNRUN PG47 fixture with the pinned builder and filesystem-copied lane and fleet with `shutil.copytree` before any auditor ran. In the copy it unset only `remote.origin.promisor` and `extensions.partialclone`. There were no paired `.promisor` markers to remove.
- Attested, all true: no-lazy object inventories equal for lane and fleet; objects-directory byte digests equal; refs equal; missing sets equal and exactly [2a675c1a…]; that object is lane-tip `:d` and is absent in both; FAKE is absent in all four repos; the report blob is equal; fleet config is equal.
- Origin url string is unchanged, and its target is absent in both, so availability is unchanged. The config difference is exactly the two removed keys. `promisor_backed` was true on the original and false on the companion.
- Results: promisor exit 2 and plain exit 2. Both have `met_amended=true` and empty `objects_acquired`. After path normalisation the two refusals are byte-identical, with no document on either side. Class: diagnostic-only. This confirms metadata-only invariance for this cell; it is not verdict-document equality.

Residuals / not exercised:
- No other cells were run: no PG46/PG48 pair, no frozen arm, and no mutants. The companion's url still points at the original fixture's absent-remote path (unchanged string; neither one is connected).
- The original unknown clause stays WITHDRAWN/NOT-ACHIEVED, Gitfloor H2 stays open, and there is no score promotion.

Raw evidence: `out/FinalCase46/grid/{stdout.json,candidate.json,population.json,stderr.txt,exit.txt,premise.txt}` and `out/FinalCase46/supplement/{supplement.json,stdout.json,stderr.txt,exit.txt,supplement_driver.py}`. Kept fixtures are under /fast/scratch/hyaku/kama-r24/postfix/FinalCase46/tmp/.
