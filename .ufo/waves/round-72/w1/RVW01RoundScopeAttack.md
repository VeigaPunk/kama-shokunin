# RVW01RoundScopeAttack — round 72 C1

Built A1–A7 Git fixtures and ran 27 final pinned-source invocations plus complementary A6/submodule checks. No lane tool edits or installations.

## Findings by severity

- P2: A7 submodule ignore=all survives, exit 0; direct submodule status shows modified/untracked files, forced-parent status shows ` M sub`.
- Scope survivors: A5 linked-worktree dirt (primary exit 0, linked checkout exit 1); A6 valid round-71 label with ignored round-72 work (exit 0 versus 1 with round 72). These are not asserted to violate the narrower frozen supplied-round/worktree rules.
- Killed: A1 staged addition/modification (1), A2 staged deletion (1), A3 special-name stray/ignored (1/1), A4b untracked ignored payload (1), A6 missing-plan/misheading (1/1), A7 default submodule and allow-boundary probes (1).
- A4 tracked-pattern match exits 0 but is not a demonstrated ignored-path defect: canonical check-ignore exits 1 on the indexed path.

## Evidence and gaps

Full findings, every final command and observed verdict, frozen-kill coverage, source anchors and procedural limitations: [attack.md](RVW01RoundScopeAttack/attack.md). Exact commands/stdout/stderr/exits are in receipts/*.out, summary.json and supplemental-commands.json. Drivers and fixture metadata are preserved. Tested-source.sha256 pins the tested landed bytes. LSP device unavailable; no semantic references/diagnostics or instrument selftest claimed.

Initial base-arm comparison had a wrong path and was corrected before final receipts. Fixture-helper cwd Git spelling, multiple-clone and childrepo assertion deviations are disclosed in attack.md. Scratch was deleted after preserving evidence. Report-writing helper initially failed due to a local variable shadowing the tool proxy; this affected no tested bytes and this write completed via the file-write helper. No admission judgment.

## Exact persisted files written

- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/attack.md`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/build_fixtures.py`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/build_seed.py`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/fixtures-meta.json`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/a1-staged-new-basearm.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/a1-staged-new.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/a2-staged-delete-basearm.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/a2-staged-delete.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/a3-space-newline-stray.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/a3i-space-newline-ignored.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/a4-tracked-ignored-basearm.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/a4-tracked-ignored.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/a4b-tracked+untracked-ignored.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/a5-worktree-linked.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/a5-worktree-primary-basearm.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/a5-worktree-primary.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/a6-prompt+plan-clean.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/a6b-prompt-yes-plan-gone.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/a6c-plan-no-prompt.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/a6d-plan-mislabelled-heading.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/a6e-round71-wronglabel.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/a7allow-glob-star.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/a7allow-glob-starstar.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/a7allow-prefix-dir-slash.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/a7allow-prefix-dir.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/a7sub-submodule-default.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/a7sub2-submodule-ignore-all-basearm.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/a7sub2-submodule-ignore-all.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/b0-round99-wronglabel.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/b0-seed-basearm.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/b0-seed-clean.out`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/receipts/summary.json`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/run_attacks.py`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/supplemental-commands.json`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/tested-round72-round-scope.py`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack/tested-source.sha256`
- `.ufo/waves/round-72/w1/RVW01RoundScopeAttack.md`
