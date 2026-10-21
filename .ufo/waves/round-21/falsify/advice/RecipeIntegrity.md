VERDICT: partial - run b76727f3 is genuine and reproduces from committed bytes, but the recipe asserts exit codes only, 7 claims have no command, and the lane tree drifted after the run.

Attacked: runs/b76727f3 (commands.json, stdout/stderr/exit, live-receipt.json), recipe.json, run.py, clean start and ancestry of b76727f3, and recipe coverage of corpus/lessons/round-21.md. Read-only; scratch clone pinned to b76727f3. Commands, exits and claim matrix: falsify/out/RecipeIntegrity/evidence.md.

## Verified (exit 0 unless stated)
- commands.json vs recipe: 28 = 28, same order; recipe_sha256 9d68997d… = committed blob at b76727f3 = working file; every .stdout/.stderr sha256 and .exit file matches; as_expected 28/28; no timeouts.
- Clean start: run.py:25-29 reads master, refuses on `git status --porcelain`, creates out only after that. b76727f3 exported 11:13:58 UTC; commands ran 11:14:00.27 to 11:14:13.73.
- Ancestry: b76727f3 is in master and in a6617149. No runs files at b76727f3; a6617149 adds 86 files, all under runs/b76727f3/. b76727f3 vs recipe commit 4e75d9e: advice/out files only, no code.
- Rerun from committed bytes: 24 of 25 non-live commands match exit, stdout and stderr; the 25th matches exit and stdout, stderr differs by a random temp name. Not rerun: c2-live-receipt and c2-producer-selftest (launch the live tool), nh-snapshot-selftest (fixture server).
- Separability (lesson L29-32, no recipe command): reverting C2 files leaves all C1 outputs byte-identical; removing C1 files leaves all C2 outputs byte-identical.
- Lesson numbers hold: 9 defects (landed-omitted 8: r10x1 r18x3 r20x4; unresolved-full-hash 1: r20), required 42, post-report 4, ledger corrected 9, selftest 32/0; frozen link 0/13, subdir 0/1; current 13/13, 1/1; regular 3/3, type 1/1; null 0/1; install_tree_sha256 equal across arms; live receipt 10 links; no llama-server alive now.

## Findings
1. HIGH - Lane tree drifted after the run. `GIT_OPTIONAL_LOCKS=0 git diff --name-status`: M tools/report-landing-audit.py and tools/kama-llamacpp-live.py (11:23:17 UTC), M tests/llamacpp-live/check-receipt.py (11:21:47), M SCORECARD.md (11:19:11). HEAD copies equal the measured bytes, so a6617149 is consistent; the working tree is not. The audit edit (128 diff lines) switches detector input from working-tree fleet reports to `git show HEAD:` bytes and adds cases; the other two are selftest-only. Do not commit these without a fresh official run.
2. HIGH - Exit-code-only contract. recipe.json has no stdout or JSON assertions. c1-audit-raw exit 1 is the generic "defects found" code and does not pin 9. c2-grid-frozen exit 1 does not pin 0/13 or 0/1. c2-grid-both exit 1 comes from the frozen arm, so back_compat_install_tree_sha256_equal is never gated. "28/28 declared exits met" overstates what is checked.
3. MED - Lesson claims with no command:
   a. "the round-21 report passes it before its fleet commit" (L17): none. The current draft fails: `--rounds 21 --report 21=ReportFormatDraft/r21-draft.md` exit 1, 3 landed-omitted (b76727f3, 4e75d9e, 1471344).
   b. "0 false positives, 0 false negatives, 11 scouts" (L15-16): hand recounts live in advice; no labelled-set comparison.
   c. "three R18 receipts ... INVALID with --require-install-links": the flag runs on receipt-1 only. Receipts 2-3 also exit 1 in my run, so the claim holds but is unmeasured.
   d. "ephemeral llama-server, torn down": no check. ps is clean now, which says nothing about run time.
   e. "S066-S074 quotes <=25 words verbatim" (L34-50): no check; nh-citation validates cite() tokens only (citation-provenance.py:9-14).
   f. Frontier "census before 65 rows": tracked census-before.txt, not regenerated at 7a6bc91.
4. MED - Lesson errors. L12 says "four" defect kinds; report-landing-audit.py:61-62 defines five (landed-section-missing is the fifth). "validate exit 0" is true, but validate now prints 8 W04 duplicate-URL warnings (was 6; S067 and S071 are new).
5. MED - Unpinned external state. (a) commands.json records no fleet revision, and the C1 tool reads fleet reports from the working tree. Fleet kama reports are committed and unmodified now and the C1 rerun matches, so results hold today; equivalence at 11:14 is [INFERENCE]. Fleet HEAD in window: 7fd7c785 (fleet reflog lines 753-754). (b) fr-* run fleet-root scripts/sources-census.sh on the lane path, not the commit. (c) python 3.14.8 and git 2.56.0 are not recorded.
6. LOW - kama-llamacpp-live.py:1155-1157 runs the unreadable-member check only `if not os.access(lib, R_OK)`; root ignores mode bits, so the check passes vacuously under root. Run uid is 1000, so this run was not vacuous.
7. LOW - Clean guard: porcelain ignores ignored files (1004 entries here, mostly .jj and __pycache__); run.py does not check HEAD == refs/heads/master. No run-time cache writes seen.

## Recommendations (L1 decides; nothing applied)
- recipe.json: assert stdout/JSON (defects==9; frozen link.changed==0; back_compat==true; receipts 2-3 with --require-install-links exit 1); add the final round-21 audit (--report 21= after the last round commit) and separability reverts; record fleet HEAD, python and git versions in commands.json.
- Lesson: change "four" to five kinds; disclose the 8 W04 warnings.
- Re-run the recipe after any edit to the four drifted files, before committing them.

## Process
- Installs: none (git 2.56.0 and /usr/bin/python3 3.14.8 already present). Lane not modified except this new report file, which the assignment named. Scratch /tmp/kama-r21-RecipeIntegrity removed after writing evidence.
