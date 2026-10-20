VERDICT: partial — most routed defects are closed, but one carry rationale is false and install disclosure is still pending.

Axes: closure coverage, truthful disposition, and evidence provenance. Scope: round-17 routed defects and jj-migration risks against the round-16 verifier spot-check, JjAuditKama §3/§6, and JjTrialKama recommendations. This is a recommendation, not an admission.

## Findings

### Medium — the prior-exposure deferral is assigned to the wrong pin

`corpus/lessons/round-17.md:125-127` says the matrix `why` citations, duplicate class, and frozen-manifest prior-exposure field “all need matrix bytes, which the round-16 digest pins.” The first two require changes to matrix JSON; the third is manifest metadata. `.ufo/waves/round-16/acceptance.json:10` pins `matrix_set_sha256`, while `.ufo/waves/round-17/frozen/manifest.json:2-5` is a separate manifest with `schema`, `source_commit`, `captured_by`, and `files`, but no `prior_exposure`. The round-17 reviewer explicitly says to add that field when regenerating the manifest (`.ufo/waves/round-17/build/advice/ReviewRound16LessonDebt.md:33`: “Add `prior_exposure` … when L1 regenerates the manifest.”). Thus the matrix digest does not explain leaving this manifest field out; the stated reason is false for that item. Record the prior-exposure metadata in an appropriate manifest revision or explicit correction rather than grouping it under the matrix pin.

### Low — AGENTS.md overstates when round-13 returns exit 4

`AGENTS.md:6` says “an uncommitted QUALITY.md now exits 4, could-not-evaluate.” The gate only assigns that finding when all other checks are clean (`.ufo/waves/round-13/measure.py:473-485`, especially `if clean and not worktree_matches_head:`); a content failure still yields `documentation_mismatch`. The selftest explicitly expects exit 1 for `live_worktree_divergent_content_failure` (`measure.py:816-824`), and the clone selftest passed 13/13. The commit-before-gate instruction is conservative and sound; qualify its parenthetical with “when every other check is clean.” This is the other demonstrably false statement found.

### Pending — round-16 install disclosure is not evidenced yet

The round-16 spot-check requires the retained tarball in the next report or an L0 follow-up (`corpus/lessons/round-16-verifier-spotcheck.md:186`: “In the next report or an L0 follow-up, name the retained tarball”). Round 17 says the report and L0 follow-up name it (`corpus/lessons/round-17.md:116-120`), but at review time the fleet `reports/round-17/` listing had no `kama.md`; the L0 file still has only the round-16 kama question at line 58, and a search for `llama-b11755-bin-ubuntu-x64` returned no match. Treat this as pending L1 handoff, not a completed fix, until the report or follow-up is actually present. The spot-check’s companion `/usr/bin/llama-server` statement is likewise not yet evidenced in a round-17 report.

## Routed-item disposition

- **Round-16 defect 1 (wave provenance):** the committed build `validation.json` has policy path/hash, `v2`, band, and the single `ensure_ascii=False` canonicalization. The live falsify wave now also has a validation record with the same policy identity and canonicalization, but that file was generated after `54a2926` and is untracked in the current worktree; do not represent it as part of the pinned commit. `dispatch-provenance.py` recovered 79 spawned members from the round-16 async result.
- **Defect 2 (summary):** strict recount is 34 confirm / 40 partial / 0 refute / 5 nonconformant; all 79 expected files are present, and the five names match the lesson. The historical `completion-summary.json` is unchanged; the correction is recorded in the new lesson and the strict counter.
- **Defect 3 (append-only SOURCES):** the guard reports the S041 `anchor` and `teaches` changes for `b8e485c..ccc4bb3` (exit 1), and reports no violation for `cff9e62..54a2926` (exit 0), with S042–S046 added. S041 remains as committed and its old values are disclosed.
- **Defect 4 and the OPTIONS / 318–320 nits:** corrections are appended to README, endpoint-identity, runtime-health-surface-matrix, SKILL, and the loading-lifecycle note. The SOURCES end note also explicitly excludes OPTIONS (SOURCES.md:140-141). The probe remains at the pinned digest `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`, and the matrix JSON files are unchanged. The stated reason for not changing the probe comment is therefore credible: doing so would change the digest used by round 16 and the current claim.
- **Defect 5:** pending, as above.
- **Defect 6:** the lesson routes the previously ungraded C1 fields and weak C2 checks to the respective repairs. M3’s remaining harness-shutdown debt and M6’s lack of a mechanical measurement guard are still named, not falsely claimed closed. The matrix `why` citations and duplicate-class debt are genuinely constrained by the round-16 matrix digest; the prior-exposure item is not.

For the jj items, R1 is supported: `.ufo/waves/round-13/measure.py --selftest` passed 13/13, including divergent-clean exit 4 and divergent-content-failure exit 1. `.gitignore` now ignores `.ufo/state/` and `__pycache__/`; `git check-ignore` confirms `.ufo/state/foo` and the pre-existing `registry/history/.lock` rule. AGENTS.md carries the helper-only, detached-HEAD and ordering rules. The fleet helper tracks requested paths and checks `jj diff --summary` before committing, printing `nothing to commit` without creating an empty commit. R2 is accurately marked not applicable because the lane has history. JjTrial recommendations 1–3 are therefore represented; no `.gitattributes` or hooks change was made.

JjAudit recommendation 6 remains intentionally open. Its cited advice says `measure.py` has no digest pin and recommends fixing the unguarded Git read (`.ufo/waves/round-17/build/advice/ReviewR16MeasureParity.md:1,11-16`). The lesson’s byte-preservation reason is a real reproducibility/auditability preference, not demonstrably false, but it does not remove the latent replace-ref / inherited-`GIT_*` risk or match that reviewer’s recommendation. Do not count the parity risk as fixed.

## Commands and results

All lane tools below ran only in the required `/tmp` clone at `54a29268e2083caa2b1e0d54ee1e7d90961302f3`; no gate or measurement ran in the lane.

```text
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17.RoutedDefects-clone && git -C /tmp/KamaR17.RoutedDefects-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3
exit 0

PYTHONDONTWRITEBYTECODE=1 python3 .ufo/waves/round-17/count-verdicts.py .ufo/waves/round-16/falsify/advice --expect-names .ufo/waves/round-16/falsify/spec.json --json
exit 0; counts 34/40/0/5, files 79/79

PYTHONDONTWRITEBYTECODE=1 python3 .ufo/waves/round-17/dispatch-provenance.py --attempt-result .ufo/waves/round-16/falsify/spawn-result.json --label spawned --out /tmp/KamaR17.RoutedDefects-clone/provenance-review.json
exit 0; spawned=79 via omp_text_spawned_header

PYTHONDONTWRITEBYTECODE=1 python3 tools/sources-append-only.py --from b8e485c --to ccc4bb3 --repo /tmp/KamaR17.RoutedDefects-clone --json
exit 1; expected S041 anchor/teaches violation

PYTHONDONTWRITEBYTECODE=1 python3 tools/sources-append-only.py --from cff9e62 --to 54a2926 --repo /tmp/KamaR17.RoutedDefects-clone --json
exit 0; no violations, S042–S046 added

PYTHONDONTWRITEBYTECODE=1 python3 .ufo/waves/round-13/measure.py --selftest
exit 0; 13 passed, 0 failed

git check-ignore -v .ufo/state/foo registry/history/.lock
exit 0; both ignored

git diff --quiet cff9e62 54a2926 -- ':(glob)tests/probe-verdicts/*.json'
exit 0; matrix JSON files unchanged

sha256sum tools/kama-probe.sh
exit 0; 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3

ls /home/vgpnk/Projects/shokunin/.ufo/reports/round-17/
exit 0; no kama.md in listing

grep -n 'llama-b11755-bin-ubuntu-x64' /home/vgpnk/Projects/shokunin/.ufo/l0-questions.md
exit 1; no match
```

An initial `git diff --quiet cff9e62 54a2926 -- tools/kama-probe.sh tests/probe-verdicts` returned 1 because the directory includes intended code changes; the narrowed JSON-only comparison above returned 0. `git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain --untracked-files=all` exited 0 and showed the falsify validation as untracked post-commit output. Cleanup `rm -rf -- /tmp/KamaR17.RoutedDefects-clone && test ! -e /tmp/KamaR17.RoutedDefects-clone` exited 0.

## Residual risk and limitations

- The final round-17 kama report and L0 follow-up may still be part of L1 handoff; this review did not create or edit either.
- I did not rerun C1/C2 control suites or any server. The C1/C2 closure status above is limited to the routed disposition and reviewed records.
- No tools were installed or updated. Scratch was confined to `/tmp/KamaR17.RoutedDefects-clone` and is removed before completion.
