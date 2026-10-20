VERDICT: partial — KQ20 and KQ22 align with their tools; KQ21’s gate-flip evidence is confounded for some controls.

# Scope attacked

Reviewed the round-17 additions KQ20–KQ22 in `corpus/QUALITY.md` at commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3`: column shape, cited-lesson grounding, testability, and consistency with fault-controls F0/F1–F8, mutant `site_missing`, live-control gate-flip, and the SOURCES append-only guard.

# Findings

## Medium — KQ21 gate-flip can reject for an independent setup error

`corpus/QUALITY.md:122` requires that “the gate also rejects that control's receipt with only the failing check flipped to passed.” However, `tests/llamacpp-live/controls.py:471-474` flips every false `checks[].passed` value, and `:489-491` explicitly warns that a non-null `setup_error` means “this arm does not isolate check re-derivation for this receipt.” The committed current results still count those arms as rejected: K3 has two failed checks plus `post-probes:child-exited-rc0` (`.ufo/waves/round-17/runs/controls-current.json:80-90`); K6 retains `internal:RuntimeError` (`:167-176`); K7 has three failed checks plus `ready-timeout` (`:191-202`). A gate rejecting on that independent error can therefore satisfy the gate-flip clause without demonstrating that it re-derived the named check. Require an isolated arm (e.g. no `setup_error`, with a single targeted failed check or one-at-a-time flips) before counting it as check-specific evidence.

## Low — KQ21’s exact exit-2 requirement is not enforced by K6’s control result

`corpus/QUALITY.md:122` says “An internal fault still writes a receipt and exits 2.” `tests/llamacpp-live/controls.py:561-563` documents exit 2 but accepts “any nonzero+receipt as a rejection”; an exit 1 would still avoid `accepted_bad`. The current K6 artifact records `tool_exit: 2` (`.ufo/waves/round-17/runs/controls-current.json:178-184`), so the observed case meets the clause, but `controls.py`’s green summary does not enforce it. Make K6 require `tool_exit == 2`, or explicitly treat the exact recorded exit as a separate admission check.

# Checks that align

- **Column shape:** the three rows use the existing four-column header (`corpus/QUALITY.md:119-123`). The actual round diff is append-only: 14 additions, zero deletions.
- **Lesson grounding:** KQ20 cites `lessons/round-17.md` C1/Mistakes; KQ21 cites C2; KQ22 cites M1 and the round-16 spot-check’s routed defect 3. The cited round-17 sections contain the corresponding claims and mistake.
- **KQ20:** F0 is implemented as a positive identity control: `fault-controls.py:482-518` requires exit 0 and every listed row passing. Fault runs require exit 1, the faulted rows to fail, and the targeted conjunct to be among the failed conjuncts (`:519-538`), so a wrapper crash is not mistaken for field detection. `mutants.py:9-12, 925-930, 1011-1018` reports `site_missing` separately with `killed: null`, not as a survivor, and the grid pins the matrix digest (`:1078-1090`). This matches KQ20’s F0, per-mutant/per-detector denominator and digest conditions.
- **KQ22:** the guard’s comparator allows only `status`, `recheck`, and `used-by` to change in place and reports other changed cells/removals (`tools/sources-append-only.py:14-18, 164-190`). Its documented historical control reproduced: `b8e485c` → `ccc4bb3` exited 1 and reported S041 `anchor` and `teaches`; the round transition `cff9e62` → `54a2926` exited 0 and reported S042–S046 as added. The round tip’s parent is the stated start commit, and it is the only SOURCES-touching commit in that interval, so this is the only round pair to grade.

# Residual risk

The 11/11 live receipt count is a count of passing checks, not evidence that all eleven are independently fail-capable subject checks. The current bad-control catalog targets health, loading, and teardown/internal-fault behavior (`controls.py:300-326`); it has no targeted subject fault for `models_alias_id`, `models_owned_by_llamacpp`, `metrics_not_enabled`, `props_alias`, `probe_model_ok`, or `probe_mismatch`. `model_unchanged` is correctly marked “lane input integrity, not subject behaviour” in the receipt (`live/receipt-1.json:209-210`). Under KQ21, do not count unmatched checks as evidence about subject behavior unless the control coverage is extended and reported by check ID.

# Verification gaps and limits

- No LSP device is mounted: requesting `xd://lsp` returned “No such tool.” I used direct source and committed-artifact reads; grep/search was only used to locate fields, not as semantic proof.
- I did not launch a server, run the live controls, or rerun the mutant grid. Those observations come from committed source and round-17 artifacts. No ports were bound or contacted.
- Commands run (clone was the required isolated checkout; only the report was written in the lane):
  - `rm -rf /tmp/KamaR17.KQRowsReview-clone && git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17.KQRowsReview-clone && git -C /tmp/KamaR17.KQRowsReview-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3 && git -C /tmp/KamaR17.KQRowsReview-clone log -1 --format='%H %s' && echo CLONE_OK` — exit 0.
  - `cd /tmp/KamaR17.KQRowsReview-clone && wc -l tests/probe-verdicts/fault-controls.py .ufo/waves/round-17/c1/mutants.py tests/llamacpp-live/controls.py tools/sources-append-only.py tests/llamacpp-live/check-receipt.py tools/kama-llamacpp-live.py && ls .ufo/waves/round-17/runs/` — exit 0.
  - `cd /tmp/KamaR17.KQRowsReview-clone && PYTHONDONTWRITEBYTECODE=1 python3 tools/sources-append-only.py --from b8e485c --to ccc4bb3 --path corpus/SOURCES.md --repo /tmp/KamaR17.KQRowsReview-clone` — guard exit 1 (expected); shell printed `EXIT=1`.
  - `cd /tmp/KamaR17.KQRowsReview-clone && PYTHONDONTWRITEBYTECODE=1 python3 tools/sources-append-only.py --from cff9e62f05aa7cfb9059444f62eb787100719713 --to 54a29268e2083caa2b1e0d54ee1e7d90961302f3 --path corpus/SOURCES.md --repo /tmp/KamaR17.KQRowsReview-clone` — guard exit 0; S042–S046 reported added.
  - `cd /tmp/KamaR17.KQRowsReview-clone && git log --reverse --format='%H %s' cff9e62f05aa7cfb9059444f62eb787100719713..54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- corpus/SOURCES.md` — exit 0.
  - `cd /tmp/KamaR17.KQRowsReview-clone && git diff --unified=3 cff9e62f05aa7cfb9059444f62eb787100719713 54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- corpus/QUALITY.md` — exit 0; 14 additions, 0 deletions.
  - `cd /tmp/KamaR17.KQRowsReview-clone && git rev-parse 54a29268e2083caa2b1e0d54ee1e7d90961302f3^ && git log --reverse --format='%H %s' cff9e62f05aa7cfb9059444f62eb787100719713..54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- corpus/SOURCES.md` — exit 0.
  - `rm -rf /tmp/KamaR17.KQRowsReview-clone && test ! -e /tmp/KamaR17.KQRowsReview-clone && printf 'SCRATCH_REMOVED\n'` — exit 0; scratch removed.
- Installs/updates: none.