VERDICT: partial - round-10 result holds (1 true positive, 0 FP/FN, unchanged by both switches); but batch-check labels an ambiguous Landed token `landed-unresolved`, so `landed-ambiguous` is never emitted for Landed tokens in any tested case, and selftest has no ambiguous case.
Attacked: C1 round 10 at a6617149 (`tools/report-landing-audit.py`, blob 62bef09f, identical at measured b76727f3). Switches: author vs committer time; batch-check vs per-token `cat-file`. Lane not modified (read-only git only); no installs.

## 1. Reproduction (executed)
- `git clone -q .../kama-shokunin <scratch>/lane && git checkout -q a6617149…`: rc 0.
- `python3 tools/report-landing-audit.py --lane-repo <clone> --fleet-repo /home/vgpnk/Projects/shokunin --rounds 10 --no-errata --json`: rc 1; one defect `landed-omitted 40660352d4a9…`, cited_elsewhere true.
- `--rounds 10-20 --no-errata --json`: rc 1; 9 defects, required 42; stdout sha256 af2707ad… = official `c1-audit-raw.stdout` (commands.json: exit 1, same hash).
- `--selftest`: rc 0, 32/0; byte-equal to committed `c1-audit-selftest.stdout`.

## 2. Round-10 derivation (own code: `git log %H|%an|%at|%ct`, fleet `--diff-filter=A`, report text)
- Fleet add `b69b7ba2` (author kama-shokunin, at=ct=1792450135; committer protocol-shokunin). Sole commit touching the report; worktree blob = HEAD blob (371a19e2).
- Lane round-10 commits (author kama-shokunin, subject `round-10:` / `checkpoint(r10)`): `1e41928` (at=ct=1792449282) and `40660352` "round-10: post-review fixes" (at=ct=1792450060). Both ≤ cutoff under author and under committer: required 2, post 0.
- Landed section (report lines 28-39) cites only `1e41928` (line 30): "All changes are in lane commit `1e41928`…".
- `40660352` appears only as `4066035` (line 114, Post-review), which lists LOG.md +5, SCORECARD.md +17, corpus/lessons/round-10.md +15 and one new file. The Landed list is incomplete: **true positive**.
- FN sweep: master commits matching `round-10|r10|checkpoint\(r10` are the two above plus `03b5f0e8` (protocol-shokunin integrator; adds corpus/lessons/round-10-verifier-spotcheck.md +17). It is excluded by the documented author rule, so not an FN under that rule. No round-10 kama commit in `jj/keep` refs.
- Judgement, not mechanical: "cited elsewhere" does not exempt an omission under the documented rule. Exempting it would make this a non-defect.

## 3. Switch 1: author vs committer time
- Round 10: all four timestamps equal, so no change. Variant (`%ct` in `round_commits` and `report_cutoff`): per-round cutoff, required, post and defects identical to shipped for rounds 10 and 10-20 (diff rounds = []).
- Fleet add at==ct for rounds 10-20. 16 kama commits on master have at≠ct; none straddles a cutoff.
- Not neutral in general: the committer variant fails 4 selftest cases (rc 1): subject-without-space-required, author-time-cutoff-survives-rebase, post-report-excluded, draft-uses-fleet-cutoff. Author time is load-bearing for rebases (tool docstring lines 25-26). Late-committed lane-authored report case: [INFERENCE], not executed.

## 4. Switch 2: batch-check vs per-token
- Corpus rounds 10-20 and round 10: identical. Per-token variant selftest: 32/0, rc 0.
- Git 2.56.0 raw (executed, rc 0): `3cee^{commit} missing` but `3cee ambiguous` without peel. Landed lookups always peel `^{commit}` (lines 189-190), so ambiguity yields `missing` and then `landed-unresolved` (line 193). In every tested case the peeled path printed `missing`, so `landed-ambiguous` (lines 194-195) was not reached.
- Blob-vs-commit prefix under `^{commit}` resolves to the commit (`found`): no false ambiguity.
- E2E fixture (60,001 commits; 7-char collision `378f9d0` vs `378f9d043b4c`, `378f9d0e9ee4`), both rc 1:
  - shipped: `[landed-unresolved 378f9d0]`
  - per-token: `[landed-ambiguous 378f9d0]`
- Errata (same fixture, `--errata`): shipped + row kind `landed-ambiguous` → rc 1 (errata_unmatched 1); shipped + row `landed-unresolved` → rc 0; per-token + `landed-ambiguous` → rc 0. The documented kind fails closed. The docstring (lines 14-16) defines landed-unresolved as "no commit in either repo", which is false for this token.
- Corpus rounds 10-20 contain no ambiguous Landed token, so no observed classification change there.

## 5. Other
- [INFERENCE, not executed] An ambiguous Landed prefix counts as landed for every commit it prefixes (lines 197-198), so the omitted check is coarser for that token.
- Independent derivation re-implements the documented rule: it checks implementation fidelity, not rule correctness.

## 6. Artifacts and commands
- Out dir `falsify/out/Recheck10/`: `variants/v_{shipped,committer,pertoken,both}.py`, `runs/*.json` (incl. e2e), `mechanism-summary.txt`, `summary-cell1.txt`, `commands.log` (61 executed commands with rc). Copy of this report there too.
- Scratch `/tmp/kama-r21-Recheck10` removed after writing.
