Verdict: round-47 `corpus/README.md` Frontier disposition drafted and grounded on my own
runs at build `3a09a1d9` — C1 `met=True` (files=85, lane_events=5, mismatches 0) and C2
`receipts=1 replay=1 tamper=1 newrow=0 met=False`, the last leg being the b11909 registry
row the build does not yet carry. Four findings for the L1, none of them an edit to a
frozen instrument.

## What I did

Read the contract sources before writing: `corpus/README.md` §Frontier (lines 66-80) and
the round-46 disposition (lines 672-771), both counter docstrings
(`tools/round47-append-audit-v2-check.py`, `tools/round47-live-replay-audit.py`),
`.ufo/waves/round-47/preregistration.json`, `registry/append-only-contract.tsv`,
`tools/append-only-audit.py`, `tools/kama-live-replay.py`, `tools/kama-llamacpp-live.py`,
the three `c2/live` receipts, `c2/live/install.txt`,
`corpus/lessons/round-46-verifier-spotcheck.md`, and
`.ufo/waves/round-46/w1/out/Rev2Decl/contract.md`. Then every figure in the draft was
measured in a `git clone --shared` of the lane at my scratch. No lane file was written.

| # | Command (in `$S/lane`) | Output | Exit |
|---|---|---|---|
| E1 | `python3 tools/append-only-audit.py --repo . --to 3a09a1d9` | 5 events, `summary commits=303 files=85 events=5 restored=3 partial=2 unrestored=0` (dd9f5dc6 SCORECARD 31/24 partial; 0718b6ab LOG 2292/2292 restored, SCORECARD 2421/2420 partial, QUALITY 375 restored, README 663 restored) | 1 |
| E2 | `python3 tools/append-only-audit.py --selftest` | `AOA_SELFTEST pass=15 fail=0` | 0 |
| E3 | `python3 tools/round47-append-audit-v2-check.py --repo . --tip 3a09a1d9 --scratch $S/c1b` | `selftest=1 contract=1 lane=1 fixture=1 stable=1 files=85 lane_events=5 lane_mismatch=0 fixture_mismatch=0 met=True` | 0 |
| E4 | `python3 tools/round47-live-replay-audit.py --repo . --tip 3a09a1d9 --scratch $S/c2b` | `receipts=1 replay=1 tamper=1 newrow=0 rerun_checks=11 met=False`; detail `newrow: no registry row names b11909 and caa8191d…` | 1 |
| E5 | `python3 tools/kama-live-replay.py --selftest` | `KLR_SELFTEST pass=10 fail=0` | 0 |
| E6 | `python3 tools/append-only-audit.py --repo . --to <rev> --contract <tip contract>` at `172b8ad0` and at `3a09a1d9` | SCORECARD events identical at both: `dd9f5dc6 31/24`, `0718b6ab 2421/2420` | 1 |
| E7 | `git diff --numstat --no-renames 0718b6ab^1 0718b6ab -- SCORECARD.md LOG.md corpus/QUALITY.md corpus/README.md` | `2421` / `2292` / `375` / `663` (and `31` for dd9f5dc6) | 0 |
| E8 | `python3 tools/append-only-audit.py --repo . --to 3a09a1d9 --threshold 1 --json` | 91 events: 12 restored, 8 partial, 71 unrestored — 26 SCORECARD, 20 SOURCES, 13 LOG, 8 README, 26 across 15 lesson files | 1 |
| E9 | `python3 tools/hexrun-census.py scan --repo . --rev <rev>` at `42ea1204`, `e8fa87ef`, `172b8ad0`, `3a09a1d9` | `unknown=21`, `21`, `22`, `22` (all `exit 1`) | 1 |
| E10 | `gh api repos/ggml-org/llama.cpp/compare/b11906...b11909` | `total_commits 3`, 38 files changed; of the population's 16 pinned paths, `src/llama-context.cpp` (S107, S130, S132) and `src/llama-kv-cache.cpp` (S113, S135) moved | 0 |
| E11 | frozen `population()` imported from `tools/round46-release-recheck-audit.py` over `git show 3a09a1d9:corpus/SOURCES.md` | population 91; 228 rows; 180 `on-release`; out-of-population llama.cpp rows: 7 by source URL (S026, S028, S038, S477, S482, S484, S486) plus the command-source receipt rows S041, S046, S055, S485, S487 | 0 |
| E12 | `python3 tools/sources-append-only.py --selftest` (fresh clone at lane HEAD `46a924e0`; the tool is unchanged by the build) | `42/42 selftest cases passed` | 0 |

Exit codes were captured without a pipe (`> file 2>&1; echo $?`); a first pass through
`| tail` reported `tail`'s status and was discarded.

## Findings

**F1 — the "exactly 10" off-population count does not reproduce (README patch made).**
`corpus/README.md:730` (round-46 disposition) says "the llama.cpp-citing rows outside it
are exactly 10" and names S026, S028, S038, S041, S046, S055, S477, S482, S484, S485. The
frozen population function (`tools/round46-release-recheck-audit.py:140`) still selects
exactly 91 at `3a09a1d9`, but S486 (b11906 binary, `corpus/SOURCES.md:239`) and S487
(b11906 receipts, `:240`) are in the same family and absent from the list. Command: E11.
Proposed fix (not applied; the round-46 text is append-only): state the rule and re-derive
the family in the next freshness counter; my draft says "at least twelve and its count
needs re-deriving under its own stated rule" instead of quoting ten.

**F2 — `hexrun-census` went 21 → 22 at the round-46 spot-check commit, not at this
build.** E9 puts 21 at both round-46 measured tips and 22 at base `172b8ad0` and at
`3a09a1d9`; the added token is
`8bca0cf333e7ceab5e734b354c87075c6efec86c`, cited in
`corpus/lessons/round-46-verifier-spotcheck.md:23`. The draft attributes the red gate to
that citation rather than to the round-47 build, so round-46 D4 stays open.

**F3 — the v2 tool never reads the contract's `rule`/`declared_at`/`note` cells.**
`tools/append-only-audit.py:184` expands `[row[0] for row in parse_contract(text)]` only.
Consequence: the SCORECARD head carve-out (`registry/append-only-contract.tsv:3`, "a head
re-anchor is an expected partial") is documentation the audit cannot apply, so
`0718b6ab` 2420/2421 and `dd9f5dc6` 24/31 are indistinguishable from a real loss of 1 and
7 lines; and the declaring-line check exists only in the frozen counter's `contract` leg.
Proposed fix (for a later, pre-frozen instrument): make the audit read the row's rule and
validate `declared_at` contains `append`, and add region support (see F4) rather than
prose exemptions.

**F4 — the contract has no `corpus/knowledge/*.md` row, though the lane declares an
append-only region there.** `corpus/knowledge/consumer-registry.md:30` is
`## Errata — 2026-10-14 re-census (append-only; rows below keep their round-1 text)`;
`corpus/knowledge/context-capacity.md:245` (`## Errata — round 26`) carries the same
semantics without the word ("the round-25 wording above stays"). Whole-file inclusion
would be wrong (the bodies are dated censuses), and the tool cannot scope a region, so
the file-scoped contract correctly omits it and the region stays unwatched. Related edge
measured: the 20-line default hides 86 of the 91 (commit, file) deletion events at this
tip (E8), 71 of them unrestored. Both are written into the draft's "still not audited"
paragraph; neither is fixed here (contract and counters are frozen).

**F5 — C2's `newrow=0` is the pre-integration state, not a defect.** E4 reproduced the
L1's dry-run line character for character; the only unmet leg is the `corpus/SOURCES.md`
row naming b11909 and its commit, which the C2 predicate requires. The draft says the C2
predicate needs it and this build does not carry it, rather than claiming `met=True`.

## Touched surfaces

- Wrote `.ufo/waves/round-47/w1/out/S9Readme/frontier.md` and this report, plus the
  evidence files listed below, all under the wave out directory.
- No lane file, no `corpus/README.md`, no `SCORECARD.md`, no `corpus/SOURCES.md`, no
  registry or counter edit; no jj or git mutation in the lane (read-only `git show`,
  `git diff --numstat`, `git ls-tree`, `git clone --shared` into scratch).
- One `gh api` request (E10). The C2 counter's replay leg runs a llama-server on a
  tool-picked loopback port; it executed twice (the discarded piped pass and E4), and both
  instances were torn down by the tool (receipt teardown: `returncode 0`, `sigkill_sent
  false`, `port_refuses true`). No tool installed, no pacman transaction.

## Integration note and concurrent lane state

The draft is written to be appended verbatim as a new `## Frontier disposition — round 47`
section after `corpus/README.md:771` (the round-46 section is the file's last, and the file
is append-only). It cites commands a reader can re-run; no figure in it is quoted from a
seat report.

While I worked, the lane worktree changed under me: at 21:33Z `git status --porcelain`
showed ` M tests/llamacpp-live/check-receipt.py`, ` M tools/gguf-identity.py` (mtimes
21:31:53Z and 21:32:10Z) and new untracked `.ufo/waves/round-47/c2/x0-digest-rehash.txt`
plus `.ufo/waves/round-47/hexrun-evidence/` and `w1.ready.dispatched`. None of those
paths is touched by any command I ran (I read the lane only through `git show`, `git diff
--numstat`, `git ls-tree`, `git rev-parse`, and counters run against my own
`git clone --shared`), so they are concurrent seat or L1 work; reported, not mine. My
clone was taken at lane HEAD `46a924e0` before those edits, and every measurement above
names the full commit it evaluated (`3a09a1d9`, `172b8ad0`, `42ea1204`, `e8fa87ef`), so
none depends on the dirty worktree.

## Out of scope

No scorecard, capability-table, lesson or registry integration; no live page read for
S002–S004/S013/S022 (the draft says the build takes none); no b11909 population re-read.

## Artifacts (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Readme.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Readme/frontier.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Readme/audit-tip.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Readme/c1-counter.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Readme/c2-counter.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Readme/hexrun.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Readme/threshold1.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Readme/compare-b11906-b11909.json`
