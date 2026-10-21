VERDICT: confirm - hand re-derivation of C1 for round-13 finds 0 defects; tool agrees exactly (exit 0, no false pos/neg); one benign tool-invisible citation exists (941bb32 = round-12 commit).

Axes (assigned): operability 8, calibration 7. This audit serves C1 calibration only (report-landing integrity, round 13).
Scope: lane=/home/vgpnk/Projects/shokunin/kama-shokunin, fleet=/home/vgpnk/Projects/shokunin. All commands read-only; lane untouched.

HAND DERIVATION (every command executed by me, exit shown)
1. Candidates: `git -C <lane> log --format='%H %an %ct %s' master` (exit 0, 82 lines); filter `^[0-9a-f]{40} kama-shokunin [0-9]+ (round-13:|checkpoint\(r13\))` (exit 0) -> exactly 2:
   - `641e1b6f1bef0e12d14c2e23388d7592ff0cb594` ct=1792472729 "round-13: correct criterion finding and comparison precision"
   - `370c066f093bd286bb0a98963f255590e3a7016d` ct=1792472845 "round-13: record measured criterion precision and census"
   No `checkpoint(r13)` commits exist. `git show -s` on both confirms author kama-shokunin <kama@shokunin.local> (exit 0).
2. Adder: `git -C <fleet> log --diff-filter=A --format='%H %ct' -- .ufo/reports/round-13/kama.md` (exit 0) -> `3ecce9536774b3c4eb8a472db0272a74f50db741 1792472920`, the only commit ever touching the path; worktree clean (`git status --porcelain=v1 --` empty, exit 0), so audited text == committed text.
3. Split: both candidates ct <= 1792472920 -> required(pre)=2, post_report=0.
4. Citations: `## Landed changes` present (no landed-section-missing). Boundary-regex tokens in section: `641e1b6f...`, `370c066f...` (x2), `941bb32`, `370c066`. Both required commits cited by full hash -> 0 landed-omitted.
5. Resolution: `git cat-file -t` in lane -> `commit` exit 0 for 941bb32c..., 641e1b6f..., 370c066f... (and for short forms 941bb32, 370c066, exit 0 each); in fleet -> exit 128 for all three (lane-OR-fleet rule satisfied via lane). `git rev-parse 370c066 941bb32` (exit 0) resolves each to exactly one object — no ambiguous abbreviation.
6. 40-hex tokens anywhere: the same three hashes (x2 occurrences each) — all resolve; 0 unresolved-full-hash. The two 64-hex SHA-256 blob digests cannot match the tool's exact-40 boundary regex (any 40-window inside a 64-run has hex neighbors); correctly ignored.

HAND VERDICT: round 13 raw defects = 0 (all four kinds).

TOOL COMPARISON
- `python3 <lane>/tools/report-landing-audit.py --rounds 13 --no-errata --json` -> exit 0; defects:[], round_commits=2, required=2, post_report=[], cutoff=1792472920, status "clean". Exact agreement with hand derivation: no false negative, no false positive.
- Same run with default errata -> exit 1, but solely from 9 errata-unmatched rows belonging to rounds 20/18/10 (ledger at <lane>/registry/report-landing-errata.tsv has zero round-13 rows; `awk -F'\t' '$1==13'` empty, exit 0). That is a --rounds 13 scoping artifact, not a round-13 defect.

TOOL-BLIND DEFECT SCAN (kinds the tool cannot see)
1. Cited-but-other-round: EXISTS, benign. The Landed section (and body) cites `941bb32`/`941bb32c3f591bc63cbf7579b2b6c552228307cd` — a real lane commit, but author `protocol-shokunin`, subject "round-12 verifier spot-check (integrator, hyaku): non-author admit/reject", ct=1792471586: a round-12 commit, not a round-13 landing. The tool only tests resolvability, so it is silent by design. Not a C1 defect: it is cited as the starting tree / push-range base (`941bb32..370c066`), which is accurate usage.
2. Wrong hash resolving to an unrelated object: none. Every token resolves to the object it purports to name; the two table rows' described changes match the two round-13 commit subjects.
3. False-positive hazard checked: prose word "succeeded" inside the Landed section yields the 7-hex maximal run `cceeded`; a naive tokenizer would flag landed-unresolved. The tool's `(?<![0-9A-Za-z])` lookbehind excludes it (verified regex match False, exit 0). No exposure.

Confidence: high — mechanical, both derivations fully executed with recorded exits. Residual unknowns: none in scope. No installs performed; no tooling added.
