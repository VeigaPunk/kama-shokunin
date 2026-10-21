VERDICT: partial - round 13 reproduces exactly and time-basis / batch-vs-per-token switches change no classification here; detector ambiguity kind and citation filter have verified FP/FN.
Attacked: C1 round 13 at a6617149 - time basis (%at vs %ct), lookup (batch `cat-file --batch-check` vs per-token), hex citation filter, round-13 report text. Answers: author-vs-committer time: no change; batch-vs-per-token: no change on real data, but synthetic ambiguity misclassified; FP/FN list below. Lane, fleet and siblings untouched.

## Executed (exit codes)
- Scratch clone at a6617149 (`git clone -q --no-hardlinks`, `checkout -q`): 0.
- `tools/report-landing-audit.py --lane-repo <clone> --fleet-repo /home/vgpnk/Projects/shokunin --rounds 13 --no-errata --json`: exit 0; required 2, round_commits 2, post 0, defects 0, cutoff 1792472920; identical to the committed raw round-13 entry.
- Same with `--rounds 10-20`: exit 1; results and summary identical to `runs/b76727f3/c1-audit-raw.stdout`.
- `--selftest`: exit 0, 32/32; no case names an ambiguity (out/Recheck13/clone-selftest.txt).
- No replace refs, grafts or shallow history in lane, fleet or clone. Report-add 3ecce953: at=ct=1792472920, in HEAD; working-tree report = HEAD blob = add blob (rounds 10-20).
- `python3 out/Recheck13/c1_probe.py`: exit 0, `PROBE OK` (probe-run.txt).

## Round 13 derivation (`git log --format='%H %an %at %ct %s' master`, unit-separated because one author name has a space)
- kama round-13 commits: 641e1b6f (at=ct=1792472729), 370c066f (at=ct=1792472845); both pre-cutoff, both in Landed.
- e1b3d746 (protocol-shokunin, at=1792473289) excluded by author and post-cutoff.
- My independent derivation equals the tool for rounds 10-20 (42 required, 4 post, 9 defects).

## Time basis (author vs committer)
- Round 13: at==ct on every relevant commit, so no change.
- Rounds 10-20: 14 round-subject commits have at!=ct; none straddles a cutoff; closest committer-time margin 17 s (24adc8ed, round 19). Committer-time variant: identical results.
- Selftest discriminates: committer time fails 4/32 (subject-without-space-required, author-time-cutoff-survives-rebase, post-report-excluded, draft-uses-fleet-cutoff).
- Executed (probe part F): work cited under its pre-rebase SHA, then rebased (same author time, later committer time), is `landed-omitted` under author time and silently accepted under committer time. Neither basis checks reachability from master. [INFERENCE] how often this occurs in practice: not observed in this history.

## Lookup (batch vs per-token)
- Rounds 10-20: identical (no ambiguous token occurs).
- Synthetic 80k-object repo, 17 seven-hex collision groups (7 commit-commit, 8 blob-commit, 2 blob-blob):
  - commit-commit: tool peeled batch `^{commit}` gives missing (7/7); per-token gives ambiguous; typed commit count gives 2.
  - blob-blob: batch missing; per-token ambiguous; typed 0.
  - blob-commit: batch found (8/8); per-token found; typed 1.
- The peeled batch never printed "ambiguous" (0/17), so `landed-ambiguous` is unreachable on this path. `audit_round` on commit-commit prefix 3308b9a yields `landed-unresolved`.

## Round-13 report mutations (CLI `--report 13=draft`; out/Recheck13/drafts/results.json)
- Correct: unchanged report (0 defects); drop 641e row gives landed-omitted; `deadbe1` gives landed-unresolved; heading renamed gives section-missing + 2 omitted; 641e as 7-hex prefix accepted.
- FP: uppercase `641E...` row gives landed-omitted. Git resolves uppercase (`cat-file -t` rc 0); the regex is lowercase-only.
- FN: `deadbee` (hex, no digit); `1234567` (digits only); digit-only ambiguous `0269408`; non-round commit e1b3d746 in Landed (370c still cited by "Pushed lane HEAD" and "Observed push"); start-tree 941bb32c cited; cross-repo `0269408` split across two repos gives found (typed union 2).
- Double count: fake 40-hex in Landed gives unresolved-full-hash + landed-unresolved (one token, two defects).
- Round 13 as written: 0 defects. Its only non-round citation is the push-range base `941bb32..370c066`, which resolves. Rounds 10-20 contain no uppercase hex and no unchecked Landed token (landed-unchecked-and-uppercase-r10-20.json), so the official 9 defects are unaffected by these classes.

## Fixes (not applied; lane untouched)
- Ambiguity: count commit candidates with `rev-parse --disambiguate` across both repos (>1 gives ambiguous), not the peeled batch.
- Citation filter: accept `[0-9A-Fa-f]`; document or check digit-only and no-digit tokens.
- Selftests: commit-commit collision, uppercase citation, cross-repo ambiguity, non-round Landed commit.

## Residual risk
- One git version (2.56.0) tested; [INFERENCE] peel ambiguity output may differ by git version (untested). The citation-filter and selftest fixes above are untested suggestions.
- The tool audits fleet working-tree text, not the committed blob; equal here, not enforced.
- jj-lane.sh recovery path not exercised.

## Tools and artifacts
- Installed or updated: none (git 2.56.0 and Python 3.14.8 pre-existing).
- out/Recheck13/: c1_probe.py, probe-run.txt, probe-summary.json, clone-*.json/txt, derive-r10-20.json, variants.json, batch-check-collisions.json, ambiguity-audit.json, landed-unchecked-and-uppercase-r10-20.json, drafts/.
- Scratch /tmp/kama-r21-Recheck13 removed after the run. Re-run: recreate the clone at a6617149 (see Executed), then `python3 out/Recheck13/c1_probe.py`; the probe asserts the pin and does not create the clone.
- Fleet HEAD moved from 9881be6 to cb581d9 during the run (other seats' commits; my fleet commands were read-only). Report-add 3ecce953 is still an ancestor of HEAD and the round-13 report is unchanged since add (checked rc 0).
