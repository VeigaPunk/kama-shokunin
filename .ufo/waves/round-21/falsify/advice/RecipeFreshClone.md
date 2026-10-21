VERDICT: partial - 23/25 non-live recipe commands matched; two C1 audits returned could-not-evaluate.
Attack target: round-21 recipe exit reproducibility in a fresh clone at b76727f31e522763ce24e43d6ec86d21b507a11f.
Axes: operability (declared versus observed exits); calibration (fresh-clone reproducibility).

Method: created a no-hardlinks clone under `/tmp/kama-r21-RecipeFreshClone/lane`, checked out the requested revision detached, and confirmed `git rev-parse HEAD` printed `b76727f31e522763ce24e43d6ec86d21b507a11f`. The small sequential runner substituted `{lane}`, `{python}`, `{revision}`, and `{out}`; it used the recipe's per-command timeout and process-group kill behavior. The clone's recipe SHA-256 was `9d68997d207756f72f5471daed1798ad9a1975a2c7193d40397e38c412194d3e`, matching the official run's recorded recipe hash. No llama-server or live producer was launched.

Ran 25 of 28 entries. The three intentionally skipped entries were `c2-live-receipt`, `c2-live-gate-pinned`, and `c2-live-gate-wrong-links-pin`. Declared/observed exits for every executed entry:
```
c1-absent-at-base                 128 / 128
c1-audit-selftest                   0 / 0
c1-audit-raw                        1 / 2
c1-audit-ledger                     0 / 2
c2-grid-selftest                    0 / 0
c2-grid-frozen                      1 / 1
c2-grid-current                     0 / 0
c2-grid-both                        1 / 1
c2-gate-selftest                    0 / 0
c2-producer-selftest                0 / 0
c2-legacy-receipt-1                 0 / 0
c2-legacy-receipt-2                 0 / 0
c2-legacy-receipt-3                 0 / 0
c2-legacy-receipt-1-required        1 / 1
nh-error-pair                       0 / 0
nh-error-selftest                   0 / 0
nh-install-tree-grid-selftest       0 / 0
nh-gguf-selftest                    0 / 0
nh-gguf-measure                     0 / 0
nh-citation                         0 / 0
nh-citation-selftest                0 / 0
nh-sources-append-only              0 / 0
nh-snapshot-selftest                0 / 0
fr-sources-validate                 0 / 0
fr-sources-census                   0 / 0
```

Both mismatches (`c1-audit-raw`, `c1-audit-ledger`) emitted no stdout and the same stderr: `could-not-evaluate: git rev-parse --verify HEAD^{commit} in /tmp/kama-r21-RecipeFreshClone: rc=128 fatal: not a git repository (or any parent up to mount point /); Stopping at filesystem boundary (GIT_DISCOVERY_ACROSS_FILESYSTEM not set).` The checked-out `tools/report-landing-audit.py` sets `here` to the lane root and defaults `--fleet-repo` to `here.parent`; in this scratch layout that is `/tmp/kama-r21-RecipeFreshClone`, not a Git repository. Its docstring classifies exit 2 as “could-not-evaluate” and says errors are never verdicts. Thus these two exits do not reproduce their declared 1 and 0; they do not establish audit results for this clone layout.

Retained evidence: `.ufo/waves/round-21/falsify/out/RecipeFreshClone/recipe-exits.tsv` contains every executed entry's declared/observed exit, match and timeout flags, and stdout/stderr SHA-256. The two failing commands' captured stderr and empty stdout were retained in `/tmp/kama-r21-RecipeFreshClone/run-output/` during analysis; scratch is removed on completion. No tools were installed or updated; only this assigned advisory report and TSV were created under the lane's falsify paths; no external repository files were changed. Risk: the C1 audit outputs are not comparable to the declared exits unless the command's inferred fleet-repository location is supplied by an equivalent repository layout (not tested; `[INFERENCE]`).
