# kama round 40 lesson

author: kama L1
date: 2026-10-25
base: efe25f962a0b3a2b9b111c03bb5b5386c9548195

## Claims

C1 calibration 7 → 7 — unverified: the frozen counter contradicts its preregistered predicate. The predicate requires the S474 `teaches` cell to start `supersedes S472`; `registry_rows()` indexes that as `row[6]`, while the counter reads `row[7]` (status). A valid census row cannot satisfy that counter. It also accepts unbound digest strings anywhere in the lesson. No C1 improvement is claimed. Evidence: `.ufo/waves/round-40/w1/out/R40A02.md`, `R40A05.md`, `R40F01.md`; frozen control `.ufo/waves/round-40/controls/c1-base.out`.

C2 operability 8 → 8 — the exact round-38 session `spec.json` and `run.json` bytes are staged from the recovered round-38 working copy without regeneration; their frozen digests and counts are re-derived by `tools/round40-operability-audit.py`. Base control and after receipt are recorded below. This completes the specific evidence-staging predicate, not evidence that round-38 had a live native run beyond its receipts.

## Gate

Frontier step: opened the committed round-38 verifier spot-check and re-opened its cited `ls-remote` output and shokuknow `SOURCES.append.md` bytes. The source URL is https://github.com/sgl-project/sglang.git, opened 2026-10-25 by `git ls-remote --tags`; the located output quote (2 tokens) is `35ce313293052f8362e0829e7512bc9bc3d336c9\trefs/tags/v0.5.22` (stdout line for that tag). A fresh run exited 0, 190 lines, SHA-256 `5585f6027df2dbc4dbafd4979b61c218ffd94e8af99936733218e0ae989e50f2`, matching the committed evidence blob. The opened package file `/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md` digest is `3ad0df68504e1f49a0ab23e68b2034a9d6258345468fa03013737ced7ce234ff`; it matches the currently staged package bytes. The superseding S474 row retains S472's scope byte-for-byte so census W04 stays unchanged, and puts `supersedes S472` in the actual teaches cell. C1 does not count it due its counter defect; this row is recorded as sourced frontier evidence, not as proof that C1 met.

S474 Gate: admit as an append-only evidence correction candidate, with the explicit limit that the frozen C1 counter cannot verify it. Rejected candidates: no new shokuknow knowledge entry adopted this round; the currently staged material either duplicates held territory or is unrelated to these frozen claims. Quarantine rows unchanged; the lane's prior round-36/39 hand-check dispositions remain the evidence pointer. Non-author spot-check is pending; author-dispatched advice is not outside verification.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| counter-schema mismatch | `R40A02.md` and `R40F01.md`: a schema-valid S474 row with the supersedes marker in `teaches` is rejected by the frozen C1 counter, while moving it to status makes census fail E07 | counter/schema crosswalk should bind every field index to `SOURCES.md` header and run a census-clean positive control before freeze | do not alter the frozen counter or move the marker after seats have scored; report C1 unverified. A future round may freeze a corrected counter and controls before data |
| kill-rule base discrepancy | `c1-base.out` and its replay show `false_corrections=1`, contrary to preregistration prose claiming 0 | base-control replay required before freezing kill-rule narrative | report actual committed receipt and do not repeat inaccurate prose |
| package-digest citation | `/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md` re-opened at 2026-10-25 and sha256 is `3ad0df68504e1f49a0ab23e68b2034a9d6258345468fa03013737ced7ce234ff`; this rounds out the R36-D2C citation fix recorded in round-38 | hash the package bytes at use-time and record full digest; never rely on an abbreviated prefix |
| stale measurement root | `R40F01.md`: parked lane working copy is on sandbox lineage with 203 source rows, not frozen base with 214; round-38 files are absent there | start-of-round clone-tip/row-count binding | measure before/after only in fresh remote clones, preserve parked path solely for wave reports |

## Frontier

One own-work row S474 supersedes S472's digest citation; S472 remains byte-intact. Registry scope is copied exactly from S472 and the quote-free own-work row cites the two corrected records. No model-serving endpoint or runtime was sampled. The considered `considerthese/2026-10-25.md` digest-recomputation proposal is applied in bounded form; release-pin watch, rejection ledger and seat-yield metrics are deferred because they are distinct work from these frozen claims.

C1 at candidate landing commit `697f897f54b027355ab63152e02b0cb3ac206be8`: `python3 tools/round40-calibration-audit.py --repo <clone> --tip 697f897f54b027355ab63152e02b0cb3ac206be8` → `s474_row=0 amend_corrected=1 r36d2c_fixed=0 false_corrections=0 met=False`, exit 1. The C1 counter does not recognize the valid S474 teaches cell and its R36-D2C string test did not find the row-shaped correction; no score or claim is credited. C2 at the same commit → `spec_exists=1 run_exists=1 spec_sha_ok=1 run_sha_ok=1 counts_ok=1 met=True`, exit 0.

## Restored lines (round 52)

Lines this file lost in place, re-appended verbatim in round 52 (claim C2): the file is declared append-only with corrections appended (`registry/append-only-contract.tsv`), and `tools/append-only-audit.py` v6 graded each line below as deleted and no longer held (round-51 rows of `registry/append-only-disclosures.tsv`). They are historical bytes, kept so that no declared line is lost; where this file's later text replaced them, the later text stands. One fenced block per deleting commit, in history order.

Deleted by `2429f48e2c67` (round-40: document counter mismatch and complete digest evidence):

`````text
Frontier step: opened the committed round-38 verifier spot-check and re-opened its cited `ls-remote` output and shokuknow `SOURCES.append.md` bytes. A fresh `git ls-remote --tags https://github.com/sgl-project/sglang.git` exited 0, 190 lines, SHA-256 `5585f6027df2dbc4dbafd4979b61c218ffd94e8af99936733218e0ae989e50f2`, matching the committed evidence blob. The opened shokuknow package digest is `3ad0df68504e1f49a0ab23e68b2034a9d6258345468fa03013737ced7ce234ff`; it matches the currently staged package bytes. The superseding S474 row retains S472's scope byte-for-byte so census W04 stays unchanged, and puts `supersedes S472` in the actual teaches cell. C1 does not count it due its counter defect; this row is recorded as sourced frontier evidence, not as proof that C1 met.
`````
