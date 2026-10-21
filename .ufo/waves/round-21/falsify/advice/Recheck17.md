VERDICT: confirm - C1 round-17 audit reproduced exactly (exit 0, required 2, 0 defects); no FP/FN; author-time and cross-repo batch-check choices are outcome-neutral for r17
Attacked: C1 `tools/report-landing-audit.py`, round-17 path, at a6617149722c73d90e142fbdc8154d6967055f7e.
Scratch: /tmp/kama-r21-Recheck17/lane — clone of kama-shokunin, checkout a6617149 (clone+checkout exit 0; lane untouched).

## Reproduction vs official raw

1. `python3 tools/report-landing-audit.py --lane-repo <clone> --fleet-repo /home/vgpnk/Projects/shokunin --rounds 17 --no-errata --json` → exit 0; r17 entry: cutoff 1792524895, round_commits 2, required 2, defects [], post_report [], report_committed true. Every field equals the round-17 entry of the official `runs/b76727f3/c1-audit-raw.stdout`.
2. Official argv (commands.json `c1-audit-raw`): `--rounds 10-20 --no-errata --json` with argparse defaults (lane-repo = script dir.parent, fleet-repo = its parent, branch master; official exit 1 comes only from rounds 10/18/20). Tool logs only `master`; my clone's master tip is a6617149, so both runs walk the same history for r17.
3. Own derivation: fleet first-add of `.ufo/reports/round-17/kama.md` = 543437674dce…, at=ct=1792524895, single add (log --reverse --diff-filter=A, exit 0). Lane commits matching `^(round-17:|checkpoint\(r17\))` with author kama-shokunin: 54a29268… (at 1792507845), 5e9ae6e9… (at 1792524834). Both ≤ cutoff → required 2; both prefix-cited in `## Landed changes` (`54a29268`, `5e9ae6e9`) → 0 omissions. protocol-shokunin's e75cf680… ("round-17 verifier spot-check") is correctly excluded by author and by the anchored subject pattern. Matches tool and official.

## Author vs committer time

- Real divergence exists in this round: 54a29268 at=1792507845 vs ct=1792513497 (+5652 s — the jj-rebase signature the docstring cites). 5e9ae6e9 and fleet add 54343767 have at==ct.
- Executed counterfactual: copy of the tool with `%at`→`%ct` in BOTH round_commits and report_cutoff (two edits under /tmp), rerun → exit 0, r17 JSON byte-identical (cutoff 1792524895, required 2, defects []).
- Why invariant: the only divergent commit is 5652 s under a cutoff that is itself identical under both clocks. 5e9ae6e9 sits only 61 s before cutoff, but both round-17 commits are Landed-cited, so a required↔post_report flip cannot create any r17 defect (omission is the only cutoff-sensitive kind). No classification change from the author-time switch on r17.

## batch-check vs alternative lookup

- Executed replication of the tool's regexes on the report: whole-text 40-hex tokens = {cff9e62f…, 54a29268…, 5e9ae6e9…}; Landed-section abbrevs = {54a29268, 5e9ae6e9}; coverage of both required commits = True/True. The 64-hex sha256 `753bfa73…` is correctly NOT matched (boundary lookahead); `36b64978…`-style truncated hashes sit outside the Landed section → unchecked, by design.
- Per-repo `cat-file -t` with scrubbed env: all 5 token forms resolve `commit` in lane; ALL fail in fleet ("could not get object info" / "Not a valid object name"). Direct `cat-file --batch-check` with the tool's exact stdin incl. `^{commit}` peel: all found, none ambiguous. So batch-check vs cat-file -t changes nothing for r17; the load-bearing choice is the lane+fleet union (lane-only lookup would also give the same clean r17, but fleet-only would invert it into 3 unresolved-full-hash + 2 landed-unresolved false positives). The union is present.

## False positives / negatives

None found for round 17. "Clean" is correct: 2/2 required commits cited and resolvable, all three full-text hashes resolve (lane), section present, no errata (`--no-errata`).

## Residual risk / gaps

- [INFERENCE] report_cutoff takes `out[-1]` of a newest-first add log = OLDEST add; r17 has one add, so multi-add behavior is untested here.
- The 61 s skew margin between 5e9ae6e9 and the fleet add is real but harmless for r17 (both commits cited); docstring itself concedes cross-repo clock skew is undetectable.
- Landed coverage uses all section abbrevs before the checkable/resolvable filter, so an all-digit 7+ hex token could in principle prefix-cover a commit without resolution — theoretical, not triggerable by this report.
- Fleet working-tree report verified clean vs HEAD (porcelain empty; blob ba6b24f24…), so official and my run read identical bytes.
No tool installs performed. Scratch /tmp/kama-r21-Recheck17 deleted after this report.
