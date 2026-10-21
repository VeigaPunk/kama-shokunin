VERDICT: partial - round 19 reproduces exactly (0 defects, no FP/FN on the real report); author-vs-committer time and batch-vs-per-token change no classification on any real round; but landed-ambiguous is unreachable (an ambiguous prefix reports as landed-unresolved) and uppercase, extra-citation and role gaps remain.

Attacked: C1 detector `tools/report-landing-audit.py` at a6617149 (byte-identical at b76727f3; the 86 files changed between them all sit under runs/b76727f3/). Axes: time basis (author vs committer), lookup mode (batch-check vs per-token), FP/FN against the fleet round-19 report.
Out: falsify/out/Recheck19/ (derive.py, harness.py, derive.json, harness.json, harness_runlog.json, cli-*.json). Scratch removed. Installs: none (git 2.56.0, Python 3.14.8 pre-existing).

## Executed (command -> exit)
- CLI `--rounds 19 --no-errata --json` -> 0: required 8, post 4, round_commits 12, defects 0, clean.
- CLI `--rounds 10-20 --no-errata --json` -> 1: 9 defects (landed-omitted 8, unresolved-full-hash 1), required 42, post 4; identical to committed c1-audit-raw.stdout.
- CLI `--selftest` -> 0: 32 cases, 0 failed.
- derive.py (independent re-implementation of the docstring) -> 0: 0 mismatches vs the tool, rounds 10-20.
- harness.py (15 mutants, 3 fixtures; base, CLI, ct, pt variants) -> 0.
- `git log --format='%H %an %at %ct %s' master` -> 0 (86 commits); fleet `git log --diff-filter=A -- .ufo/reports/round-19/kama.md` -> 0: one add, ac9859f4, at=ct=1792565257.
- git probes (2.56.0): `rev-parse --verify -q 86a2056^{commit}` rc 1; `cat-file -t 86a2056` rc 128 ("ambiguous"); `rev-parse -q 84CF2F76^{commit}` rc 0.

## 1. Round 19 vs own derivation (author and committer time)
- Cutoff 1792565257. Pre-report (8), each cited in Landed by a >=7-hex prefix: 7229fa95, 5b108c1a, f1790e25, 84cf2f76, 028235e6, 05f0f6c7, 30ed3783, 24adc8ed.
- Post-report (4): 8d9191f5, 60e8fd8a, 464ea5a3, 3389513f (all at=ct > cutoff).
- at != ct for six round-19 commits (7229fa95 +2381 s, 84cf2f76 +210, f1790e25 +78, 30ed3783 +14, 05f0f6c7 +13, 24adc8ed +11). None straddles the cutoff; committer time also gives 8/4.

## 2. Did the switches change any classification?
- Author -> committer time: rounds 10-20 unchanged (0 rounds differ, straddling commits = none; 16 kama commits have at != ct, none straddles).
- Batch-check -> per-token: no difference on any real token, mutant, or F1-F3; the only classification that moves is F3 (below).

## 3. Defect: landed-ambiguous is unreachable
- lookup() yields "ambiguous" only for peel-less names (lines 109-111). audit_round looks abbreviations up with `^{commit}` (lines 189-190); full hashes cannot be ambiguous.
- git batch-check with `^{commit}` prints `86a2056^{commit} missing` for an ambiguous prefix; without peel it prints `86a2056 ambiguous` (harness.json, batch_check_raw).
- F1 (lane with two commits sharing 86a2056; draft cites it): tool reports landed-unresolved, exit 1. Detection holds; the kind is wrong. Selftest has no ambiguity case (no "ambiguous" hit after line 346).
- [INFERENCE from lines 243-249] an errata row written with the documented kind is errata-unmatched and exits 1.

## 4. Round 19 FP/FN
- Real report: no FP, no FN on the five kinds. Every Landed token resolves to exactly one master commit; no uppercase hex, no letters-only token, no foreign citation.
- Not detectable (resolves, wrong role): Work performed l.54 says the harness "started on the clean tree `7229fa9`"; Landed l.76 names "measured work commit ... `028235e6`"; Before->after l.87 says "measured commit for both claims is `7229fa95`". The report contradicts itself; the detector passes it.

## 5. Mutations and fixtures (tool result -> verdict)
- M00 identity -> none (ok).
- M01 drop 24adc8ed from Landed -> landed-omitted (TP).
- M02 028235e6 -> 028235e7 (both cites) -> landed-omitted 028235e6 + landed-unresolved 028235e7 (TP).
- M03 84cf2f76 written uppercase -> landed-omitted (FP: git resolves the uppercase form).
- M04 fabricated uppercase 40-hex in Landed -> none (FN: uppercase never matched).
- M05 fabricated lowercase 40-hex -> unresolved-full-hash + landed-unresolved (TP).
- M06 f1790e25 -> f1790e (6 chars) -> landed-omitted (FP by the >=7 rule).
- M07 `deadbeef` in Landed -> none (FN by design: letters-only skipped).
- M08 tree id of 24adc8ed in Landed -> landed-unresolved (TP).
- M09 round-18 commit 1b85a24e in Landed -> none (FN: extras unchecked).
- M10 24adc8ed only in Work performed -> landed-omitted, cited_elsewhere=true (TP).
- M11 heading renamed -> landed-section-missing + 8 omitted (TP).
- M12 post-report 8d9191f5 in Landed -> none (extras, by design).
- M13 nonexistent abcdef1 -> landed-unresolved (TP).
- M14 fabricated lowercase hash in Work performed -> unresolved-full-hash (TP).
- F1 ambiguous prefix -> landed-unresolved, not landed-ambiguous (kind bug).
- F2 lane: two commits share prefix, fleet holds one -> none (FN, rare).
- F3 C2 orphaned by a rewrite with later committer date, draft cites C2 -> author: landed-omitted C2' (TP); committer: none (FN).

## 6. Verdict detail
- Round-19 classification is correct and reproduced independently; author time and batch-check change nothing on real data.
- Overstated: "5 mechanical kinds" (landed-ambiguous is dead code).
- Remaining gaps: uppercase (M03/M04), extra citations (M09/M12), letters-only (M07), union (F2), role errors (l.54/76/87).
- [INFERENCE] author time is forgeable via GIT_AUTHOR_DATE just as committer time is; both rest on a non-adversarial lane.
- Not checked: whether the nine round 10-20 defects are right beyond mechanical reproduction; C2 claims (out of target).
