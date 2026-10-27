Verdict: Independent regeneration exactly matches the disclosure ledger for whole-file-graded files; no discrepancy found.

Evidence

- Contract: `registry/append-only-contract.tsv:3` declares SCORECARD.md's exempt regions; line 6 declares corpus/SOURCES.md A-row; lines 10-11 declare the two knowledge `only=` regions. The v6 contract is `tools/append-only-audit.py:15-25`.
- `a2w1/out/X7Regen/regen_ledger.py:1-29` documents an independent implementation that uses git first-parent diffs and does not call `build_ledger.py` or read audit JSON/`undisclosed`. Traversal, permitted-row and held-at-tip calculations, and ledger comparison are at lines 142-241.
- Exact invocation (against private shared clone `$S/lane`):
  `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/X7Regen/regen_ledger.py "$S/lane" 138af25b963450b6520794995605fa7dbbcd87e0 /home/vgpnk/Projects/shokunin/kama-shokunin/registry/append-only-disclosures.tsv "$S/regen.tsv"`
  Exit 0. `a2w1/out/X7Regen/regen-run.out:1-4`: 341 commits, 93 whole-file-graded files, 68 deletion events, 3,540 deleted lines, 58 permitted A-row lines, 3,482 graded lines and 142 unheld disclosure lines. Regenerated and actual scoped ledgers each contain 142 rows / 142 lines; `only_in_regen=0`, `only_in_ledger=0`, `problems=[]`.
- `a2w1/out/X7Regen/ledger.diff:1-17` records 142 data rows on each side, empty unified diff and successful `cmp` (byte- and order-identical). As assigned, SCORECARD.md and the two `only=` knowledge files are excluded; the ledger slice shows SCORECARD.md contributes 24 rows / 24 lines.
- Independent row/event verifier: `a2w1/out/X7Regen/verify-rows.out:1-12` reports 68 deletion events, all 142 scoped ledger rows checked, 58 permitted A-row IDs retained with immutable cells, zero CR-bearing preimages and zero violations.
- Mutation probes: `a2w1/out/X7Regen/mutation-proof.out:1-24`. Removing a graded row, changing class/count/hash, or adding a fabricated row causes a nonzero diff. Removing a SCORECARD.md row is invisible as expected under the requested exclusion.
- Ledger blob stability: `a2w1/out/X7Regen/commit-match.out:1-6` records `git diff --exit-code 138af25b963450b6520794995605fa7dbbcd87e0 4eca4892acca6ca4072a0a6fad577d0dd78a5dda -- registry/append-only-disclosures.tsv` with exit 0; both blobs are `f2b91ee50e614ebd9cf406d409c5a84b34eefb23`.
- Held-at-tip sensitivity probe: at earlier tip `97c864bead3ee4a2f629574e77263d33834ec98a`, regeneration emitted the deleted blank-line key `e3b0c442…` from the `corpus/SOURCES.md` hunk; at requested tip 138af25b it was not emitted, consistent with the later blank-line restoration. The earlier-tip full-ledger diff also naturally includes later/absent history, so this is only a focused sensitivity probe.

Risks / blockers: none found in this scoped regeneration. No lane files or frozen counters were modified; no repository build, lint, formatter, or tests were run.

Files written: `a2w1/out/X7Regen/regen_ledger.py`, `verify_rows.py`, `regen-run.out`, `verify-rows.out`, `ledger.diff`, `mutation-proof.out`, `commit-match.out`, and this report.
