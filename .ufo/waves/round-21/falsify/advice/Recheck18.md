VERDICT: partial - round-18 defects reproduce; neither switch changes any classification; landed-ambiguous is dead code; 101f3991 is a contestable FP.
Attack: C1 round-18 output at a6617149 (`--rounds 18 --no-errata --json`), author vs committer time, batch-check vs `cat-file -e`. Scratch clone: master = a6617149 (verified). No writes to lane, fleet or MANIFEST (one read-only fleet `git status`, see F4). Installs: none (git, python3 stdlib).

## Executed (exit observed)
- Target, scratch clone: exit 1. required 7, post 0; defects landed-omitted 101f3991d, 1c325b2e5, c6dc46fab.
- Parsed compare to `runs/b76727f3/c1-audit-raw.stdout`: round-18 entry equal; `--rounds 10-20` (exit 1) full document equal.
- `--selftest`: exit 0, 32/32.
- Tool file last changed in 1471344, before measured commit b76727f3 (`git log -- tools/report-landing-audit.py`, exit 0).
- Pre-switch tool `a29bb84` (`%ct` + `cat-file -e`), `--rounds 10-20`: exit 1, equal to current.
- V1 = current with `%at`→`%ct` on both sides (asserted one match each): exit 1, equal to current.
- V2 = current with batch lookup replaced by per-token `cat-file -e`: exit 1, equal to current.
- `derive-round18.py` (no tool import): exit 0. Author and committer time both give 7 candidates, 7 pre, same 3 omitted.
- Probes in scratch repos: 4-hex and 7-hex commit-vs-commit prefixes, 4-hex blob-vs-commit prefix; synthetic lane+fleet end-to-end (exit 1).

## Answers
1. Author vs committer time: no change. Fleet cutoffs have at == ct for rounds 10-20 and no lane round commit straddles a cutoff. Round-18 rebased commits (ct > at): c6dc46fab +10326 s, eb78788b3 +422, 888cd384a +18, 1b85a24ec +1993. Closest margin: 1b85a24ec is 37 s before the cutoff under committer time (2030 s under author time). It is cited, so no defect either way; if uncited, committer time would silently drop it. The switch is protective, not classification-changing, on this data.
2. batch-check vs `cat-file -e`: no change. Identical for every round-18 token (4 full hashes, 5 abbreviations, both repos), for rounds 10-20 (incl. round-20 nonexistent full hash 0957ce619789... flagged unresolved-full-hash under both), and for the blob-vs-commit probe (`ac05^{commit}` found under both).
3. batch-check's ambiguous branch is dead for Landed tokens. Commit-vs-commit `74e1117` (7 hex): `git cat-file --batch-check` on `74e1117^{commit}` prints `missing` (exit 0; stderr says ambiguous); the no-peel form prints `ambiguous`. `cat-file -e` and `rev-parse --verify` exit 128. Tool lookup gives missing; synthetic end-to-end (exit 1) gives `landed-unresolved 74e1117`. The docstring and KINDS promise `landed-ambiguous` (lines 17, 61-63, 94, 109-111, 194-195); the selftest span (366-527) contains no `ambiguous` reference.

## Findings
- F1 [medium-low, detector]: `landed-ambiguous` never fires for Landed tokens. Presence stays correct (fail-closed); the kind is wrong. A ledger row with that kind can never match and so fails the audit [INFERENCE from apply_errata keying on kind]. Not triggered in any measured round.
- F2 [low, contestable FP, round 18]: 101f3991d, subject `checkpoint(r18): ...; unadmitted`. The rule counts `checkpoint(rN)` by design. The round-18 report cites it (lines 17-19) and says its content was reused after re-verification (lines 25-29). Rule-consistent; a reviewer who treats checkpoints as non-landings would call it FP. c6dc46fab and 1c325b2e are `round-18:` implementation commits the report calls reused: TP.
- F3 [low, FN class, not triggered]: `checkable_abbrev` skips existence checks for tokens lacking a digit or an a-f letter (`abcdefa` False, `1234567` False; executed). A nonexistent Landed token of that shape is never flagged. Uppercase hex is invisible to the `[0-9a-f]` regexes; round 18 has none (grep: no matches).
- F4 [process]: `git status --porcelain` on the fleet repo (exit 0) may refresh the fleet index stat cache; no content change. An earlier `--all --not master` count (114) was not reproducible (clone: 0; fleet root: 7 at re-check); not used.

## FP / FN, round 18
- FP: none mechanical. F2 is contestable.
- FN: none. All 7 kama round-18 commits are accounted for: 4 cited (0c75c61, 888cd38, eb78788, 1b85a24) and 3 omitted. Clone has 0 kama commits off master (`rev-list --all --not master --count`, exit 0). Non-kama `8bf99cae7` (protocol-shokunin, post-report) is correctly excluded.

## Suggested fixes (not applied)
- Detect ambiguity without the peel, or drop `landed-ambiguous` and its docs; add a selftest with two commits sharing a 7-hex prefix that expects the chosen kind.
- Add selftest cases for letters-only and digit-only Landed tokens, and for uppercase hex.
- Keep checkpoint counting; document that an "unadmitted" checkpoint still needs a Landed entry.

## Artifacts
Out dir `.ufo/waves/round-21/falsify/out/Recheck18/`: derive-round18.py/.stdout, variant-V1-committer-time.py, variant-V2-per-token-cat-file-e.py, audit-a29bb84-pre-switch.py, variant-*-10-20.json, collision7-probe.txt, collision7-end-to-end-*.json, collision-test-notes.txt. Scratch `/tmp/kama-r21-Recheck18` removed after writing.
