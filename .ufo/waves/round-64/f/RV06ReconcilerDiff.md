# RV06ReconcilerDiff — round 64 / wave f

Axes: calibration (assigned); operability (error-path review). Advisory review only; no claim verdict, lane source edit, integration or admission.

Reviewed base `0c1eff3c` → measured candidate `23b3fdb1a925129a9961cf551f6d40bf251602cb`, scoped to `tools/round42-selfdesc-reconcile.py`, plus X06Reconciler's wave-b report and affected consumers. Read freeze including amendments 1/1a/1b first. No tools installed or upgraded.

## Findings, by severity

No actionable end-to-end defect found in the assigned diff. One bounded diagnostic limitation:

**Low / mitigated: `closure_ptr=1` alone does not establish exact path existence.** `CLOSURE_RE` captures digits and `closure_ptr()` converts both listed round numbers and pointer numbers to integers (`tools/round42-selfdesc-reconcile.py:93,170-185`). In a fixture containing round-63 but no round-063, a pointer to `round-063-verifier-spotcheck.md` returns `closure_ptr=1`. The full canonical evaluator nevertheless rejects it through its existing round-41 dead-path check: `r41=1 mismatches=1 met=False`. Thus this is not an accepted false overall result, and is not a reason to reject the conjunct design. Consumers must not interpret the truth flag as a standalone existence proof. Ordinary absent round-64 pointers correctly fail the conjunct when the newest existing round is 63.

Evidence from committed scratch clone fixture `c23f5339b5819c36195387aae4ab524fce110dee`:
```
r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 closure_ptr=1 mismatches=1 maxN=64 met=False
detail: r41 calibration dead path corpus/lessons/round-063-verifier-spotcheck.md
exit=1
```
The defense is the canonical call to `m41.evaluate(repo, tip)` at reconciler lines 272-275, whose dead-path finding is included in `sum(c.values())`, not a special-case fix in these probes.

## Requested edge cases

Executed the actual candidate helper against committed scratch Git trees (not synthetic replacements of its algorithm):

| Probe | Observed closure_ptr | Explanation |
|---|---:|---|
| files round-9 and round-10; pointer 10 | 1 | Numeric `int`/`max`, not lexical selection |
| same files; pointer 9 | 0 | diagnostic newest round-10 |
| round-63 plus round-63-verifier-spotcheck-addendum.md; pointer 63 | 1 | `SPOT_RE.fullmatch` excludes the addendum |
| newest 63; pointer nonexistent 64 | 0 | diagnostic pointer 64 versus newest 63 |
| newest 63; pointer nonexistent 063 | 1 | Integer alias; full evaluator rejects dead path as above |
| pointer code span ends `.md/extra` | 0 | Closing backtick must directly follow `.md`; zero pointers matched |
| valid pointer code span followed by `/extra` outside backticks | 1 | Suffix is outside the cited path, not part of its code span |
| add round-100; pointer 100 | 1 | No two-digit ceiling |
| add round-100; pointer 63 | 0 | diagnostic newest round-100 |
| duplicate valid pointer | 0 | Requires exactly one matching pointer |

`git ls-tree --name-only TIP corpus/lessons/` reads the requested commit, not working files. Matching is exact for canonical filenames, so addenda do not advance the closure. `want=max(ns)` is numerically correct for 9/10 and 63/100. Missing closure populations return false. Missing/duplicate pointers return false. Stale `including round K` clauses return false independently. A false conjunct contributes exactly one mismatch regardless of the number of pointer faults (`:386-390`).

## Full selftest and caller compatibility

Ran the assigned command using the tool in the prescribed shared scratch clone, with the lane as read-only `--repo`, candidate `--tip`, and explicit scratch `--work .../RV06ReconcilerDiff/rs`. Exit 0; all five fixtures exercised the full evaluator:

- corrected row: closure_ptr=1, mismatches=0;
- stale pointer only: closure_ptr=0, mismatches=1;
- stale pointer and including clause: closure_ptr=0, mismatches=1;
- stale including clause only: closure_ptr=0, mismatches=1;
- removed pointer: closure_ptr=0, mismatches=1.

The fixtures distinguish independent pointer comparison from including-clause comparison, avoiding the masked mutant described by X06. They do not themselves test numeric ordering, future three-digit rounds or suffix rejection; the direct probes above cover those gaps for this review.

`evaluate()` now returns six fields; both in-file consumers (`selftest` and `main`) unpack six. Text fallback inspection found external counter consumers use CLI output rather than importing/unpacking this function: round58 reads `mismatches`, round63 `selfdesc_mismatches()` does likewise, and round64 `run_recon`/`recon_eval` parses named fields. The added field does not shift those parsers. Round64 additionally computes its own numeric closure check (`round64-c2-counter.py:839-876`) and runs the canonical reconciler on repaired/stale committed fixtures (`:924-942`); this is not a second serving runtime. No resume or rerouting code is affected by this diff; no saturation claim is newly made.

## What round-64 closure sees

Candidate run observed:
```
r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 closure_ptr=1 mismatches=0 maxN=64 met=True
exit=0
```

The measured candidate has newest spotcheck 63 and its calibration row names 63. Adding the next canonical `corpus/lessons/round-64-verifier-spotcheck.md` without changing that row makes its own closure tip stale by construction. A committed scratch fixture adding only that closure file, with the original candidate SCORECARD, observed:
```
r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 closure_ptr=0 mismatches=1 maxN=64 met=False
detail: closure_ptr: calibration row latest outside closure is round-63; newest at tip is round-64
exit=1
```
Repairing both pointer and including clause to 64 then observed `closure_ptr=1 mismatches=0 met=True`, exit 0. These are fixtures, not an observation of the future actual closing commit. Therefore [INFERENCE] round-64's actual closure tip will see the first outcome if it adds its closure file and retains the measured-tip row, or the repaired outcome if it updates the row too. This is honest commit-scoped calibration: the passing receipt at candidate 23b3fdb1 remains true for that candidate and must not be relabeled as a passing receipt for the later stale closure tip. X06 explicitly disclosed this intended behavior (wave-b report line 40).

## Residual risk and verification gaps

- `xd://lsp` is not mounted (device request returned `No such tool`). Semantic status/references/definition/diagnostics were unavailable; searches and targeted reads are literal fallback evidence, not semantic proof.
- No full C2 counter or live-server run was assigned or run here. This report does not claim its 120 controls pass, nor judge C1/C2 admission.
- Exact nonexistent-path defense depends on the existing round-41 evaluator; isolated closure_ptr consumers should preserve that dependency or check exact existence themselves.
- Selftest commits inside a guarded scratch clone and removes its fixture; supplied nonempty work is rejected before creating a clone. Existing error handling converts runtime/git/value failures to exit 2. No lane state was mutated by these runs.
- Scratch was removed after retaining these receipts. No tools installed, no server processes started, no listener touched.

Self-review: accuracy 4/5 (future closure explicitly conditional); completeness 4/5 (no mounted semantic server); clarity 4/5 (helper flag distinguished from full result); actionability 4/5 (exact paths/lines and fixture outputs provided, no lane patch authorized); conciseness 4/5 (edge-case evidence retained for durability). Overall 4.0. Improvement priority: use semantic references if an LSP device becomes available; do not treat helper-only truth as full evaluation. This assessment matches the assigned scope rather than extending it.

SELFDESC_SELFTEST newest=63 planted_stale=57 ok:closure_ptr=1,mismatches=0 stale_ptr:closure_ptr=0,mismatches=1 stale_both:closure_ptr=0,mismatches=1 stale_incl:closure_ptr=0,mismatches=1 no_ptr:closure_ptr=0,mismatches=1 pass=5 fail=0
