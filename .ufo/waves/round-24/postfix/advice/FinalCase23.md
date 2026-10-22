# FinalCase23 — PG23-unknown-citation-complete-promisor (postfix wave3, pin 92063cfc60e217fa7e2098c568578119b16a1b95)

VERDICT: PASS on the graded (amended) view — the pinned candidate returns the registered PG23 result; no blanket unknown, no whole-tree precondition, no lost ordinary finding.
Recommendation only: no score change, no self-admission; the original unknown-citation clause stays WITHDRAWN/NOT-ACHIEVED.

## Setup (pinned, private)
- Clone --no-hardlinks at /fast/scratch/hyaku/kama-r24/postfix/FinalCase23/clone, detached 92063cf, clean tree.
- Digests: auditor tools/report-landing-audit.py b9be4f42…; grid 30483830…; manifest d86b7bea… (47 cells; population 612b0a74…).
- TMPDIR=/fast/scratch/hyaku/kama-r24/postfix/FinalCase23/tmp/run1 (existing, owned; no baked-in root fallback). git 2.56.0, python 3.14.8. No installs, no network.

## Falsification attempted (current arm only, 2 cells = allowed max)
- argv: `python3 tests/report-audit/promisor-grid.py --arm current --current <clone>/tools/report-landing-audit.py --case PG23-unknown-citation-complete-promisor --case PG25-unknown-citation-plain --json --keep --out <out>/run1`
- Grid exit 0; arms.current: graded 2, violations 0, violating_cases [], amended_view_met 2/2, amended_view_unmet [], twin_mismatch [], tracebacks 0, timeouts 0, harness_leaks 0.

## Decisive observations
- PG23 premise (probe, --no-lazy-fetch): lane promisor-marked (remote.origin.promisor=true; remote url = local nonexistent `absent-remote.git`), fleet plain; lane closure complete (`rev-list --objects --missing=print` from lane HEAD: zero `?` ids); token 0123…4567 absent from both stores (`cat-file -e` rc=1); report cites the real lane commit plus that fake 40-hex in the Landed section.
- PG23 result: exit 1, met_graded_amended true; defects [landed-unresolved $fake, unresolved-full-hash $fake] (token 0123…4567); kinds [landed-unresolved, unresolved-full-hash]; stderr empty; objects_acquired {lane: [], fleet: []} (no lazy fetch); no traceback/timeout/leak.
- Original view not met: met_original false ("exit 1 != 2"); PG23 appears in original_view_unmet and withdrawn_original_failures → the original clause is NOT-ACHIEVED, not passed retroactively by the amendment.
- PG25 twin (graded control): exit 1, same defects/kinds, stderr empty, objects_acquired empty; twin equality is real — grid twin_equal true, both verdict documents exist and are identical after path normalisation (documents_identical true, diff_keys []), not two missing documents.
- Independent re-observation of the same 2 cells (no new cell): auditor re-run directly on the kept fixtures (`… --rounds 1 --json --no-errata`): exit 1 both, same two defects, document summary status "failed", errata_rows 0, corrected 0, stderr 0 bytes (out/FinalCase23/direct-00{0,1}.stdout).
- Mechanism (tools/report-landing-audit.py @92063cf): selected-ledger filtering = apply_errata l.610-655 restricts correction lookup and invalidity to audited rounds, so an unaudited row neither refuses nor erases a finding; scoped opacity = missing_reachable l.733-764 computes the opaque set from the pinned root only, and opaque_hole l.792-805 is consulted only on the unresolved-citation path (refuse_unknown l.482-510) and the errata path — build_store l.767-774 states the root is a context, not a completeness gate. In PG23 neither refusal branch is reachable (unknown_citation l.776-790 and opaque_hole find nothing), so the ordinary absent-token findings survive.

## Residuals / verification gaps (gaps, not failures)
1. "Authorized corrections" unexercised: PG23/PG25 carry no ledger (--no-errata, errata_rows 0). Prior-wave corroboration (falsify/advice/CaseErrataSplice.md, PG29/PG30) was produced against auditor sha ea51bc35…, not the pinned b9be4f42…, so it is not transferable without re-running PG29/PG30 (outside my bound).
2. The opacity refusal branches (hidden cited blob, unrelated hole) belong to other cells (PG22/PG37/opaque family), not run by bound; this verdict covers only the complete-promisor + plain-twin pair.
3. My first premise probe used `git cat-file -e` without --no-lazy-fetch and attempted a lazy fetch to the fixture's local nonexistent remote; it failed (no network, no object added; lane store still 5 objects, no packs). Every decisive probe was re-run with --no-lazy-fetch; the auditor isolates via GIT_ISOLATION l.140-143.
4. Exit class: both cells exit 1 (same-verdict-exit, identical detail); no refusal-2, verdict-change, diagnostic-only or unclassified row in this run.

Raw evidence, argv and digests: .ufo/waves/round-24/postfix/out/FinalCase23/ (grid-run1.json, grid-run1-candidate.json, direct-00{0,1}.stdout, premise-probe.json, FinalCase23-summary.json).
