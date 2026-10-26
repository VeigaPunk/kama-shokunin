# S9Mistake — round-44 `## Mistakes` draft for `corpus/lessons/round-44.md`

Verdict: **three rows drafted from committed bytes; (1) is `vacuous` (an alarm printed in rounds 41–42 and consumed in none), (2) and (3) are `stale-premise` and both are live at the round-44 freeze `098df344`; each row names a proposed check that fails on the defective tree and passes once fixed.**

Claim bookkeeping, stated before the evidence: this seat makes **no claim** about C1/C2 predicates and writes no ledger row. It drafts the lesson's `## Mistakes` section (assignment item S9Mistake) against the frozen round-44 contract; the C1 recheck that would close row (1) is another seat's work and the draft ledger still carries 6 `TODO` of 91 rows (`registry`-side count below).

## Method, roots, and limits

- Lane repo read-only: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show|ls-tree|log`, tips `098df344` (round-44 freeze; `git diff --stat 77d1bbf5 098df344` touches only `.ufo/waves/round-44/` files, so every cited lane path is identical at both commits), `9307b15e` (round-43 tip), `25df591a` (round-43 measured commit), `44fa5627` (interim).
- Fleet repo read-only: `git -C /home/vgpnk/Projects/shokunin show b0fd7b7f5ae6a0ad7717461c5fea8cb8a8724025:.ufo/reports/round-43/kama.md`.
- One scratch clone (`git clone --shared`, read-only use) and one fixture repo to prove the proposed (1) check can pass; both under `/fast/scratch/hyaku/kama-r44/S9Mistake`, deleted at the end (recipe for the fixture is in §4 so the pass side is re-runnable).
- No network call; no counter, control or preregistration was modified; no lane path was written.

## 1. Row (1) — pin-watch printed `behind` from round 41 on, and no row was rechecked

- **Since which round.** Round **41**: the first committed receipt carrying the line is the round-41 freeze control `pos-both.c2.out:3` (commit `6fec0c4c`, 2026-10-25 16:54:12 -0300), then the claim receipt `c2/candidate.out:3` (commit `4fe239a4`, 17:39:41).
  Command: `python3`-free read — `sed -n '3p' .ufo/waves/round-41/controls/pos-both.c2.out`, `git log --date=iso -1 -- <path>`; full transcript in `S9Mistake/a-pinwatch-history.out`.
  Output: `engine=llama.cpp pin=b11755 newest=b11887 newer=115 status=behind … exit=1`.
- **Round 42** repeats it: `.ufo/waves/round-42/w1/out/R42B14/b1.out:3` (same newest=b11887, newer=115).
- **Round 43 produced no pin-watch receipt**: `grep -rl "newest=b1" .ufo/waves/round-43` → 0 files (exit 1). The instrument was not run at all in the round that owned the `## Gate`.
- **Round 44 freeze**: `.ufo/waves/round-44/c1/pin-watch-freeze.out:3` = `engine=llama.cpp pin=b11755 newest=b11889 newer=117 status=behind`, summary line `pins=3 current=2 behind=1 missing=0 error=0`, `exit=1`.
- **Consumed by nothing.** `registry/engine-pins.tsv:4` = `llama.cpp  https://github.com/ggml-org/llama.cpp.git  b(\d+)  b11755  S038` (single source row). `corpus/SOURCES.md:50` is S038 with `recheck = on-release`, and its last edit is `b8e485cc` (round 16, 2026-10-20) — `git log -L50,50:corpus/SOURCES.md`. No row names the new commit: `grep -c d854d98b corpus/SOURCES.md` → `0`. `registry/` at `9307b15e` holds no `release-recheck-*` file (`git ls-tree --name-only 9307b15e registry/`).
- **Frozen counter agrees the population is untouched**: `.ufo/waves/round-44/controls/base.c1.out:2` = `pop=91 rows=0 valid=0 unverified=91 unchanged=0 holds=0 reworded=0 drifted=0 removed=0 flags_missing=0 section=0 met=False`, `exit=1`.
- **Captured-by: `none`.** The nearest criterion is `AXES.md:14` freshness ("Each round LOG entry includes a re-verification result"), and it read green: `LOG.md:2259` records "llama.cpp 115 builds behind (b11887)". `CORPUS.md:106` defines the `on-release` cadence and assigns no consumer. No counter mapped `behind` to a recheck obligation: `git ls-tree -r --name-only 9d9cc93e tools/` lists no `release-recheck` file (0 matches); `tools/pin-watch.py` and `tools/round41-pinwatch-audit.py` are the pin file's only readers.
- **Class: `vacuous`.** The instrument produced a true exit-1 alarm; the freshness machinery around it was decorative.

## 2. Row (2) — the round-43 tip broke SCORECARD's `## Planned` pointer, and the head counter cannot see it

- `098df344:SCORECARD.md:53` = `Superseded in round 42. The live plan is \`### Round-43 measured results` (opening backtick, no closing one); the tail of the same sentence is `SCORECARD.md:67` = `### Planned (round 44)\` at the end of this file; the round-5 plan …`. The measured-results block sits at `:55-65` in between. (`S9Mistake/d1-pointer.out`.)
- `git show 9307b15e -- SCORECARD.md` is the mutation: the single pointer line is replaced by `+Superseded in round 42. The live plan is \`### Round-43 measured results` … and `+### Planned (round 44)\` at the end of this file; …` is appended after the block (`S9Mistake/d1-commit-hunk.out`). At `25df591a:53` the line is intact — the regression is the final commit's, exactly as the outside closure routed it (`corpus/lessons/round-43-verifier-spotcheck.md` §7 D1).
- **The heading never existed**: `git show <rev>:SCORECARD.md | grep -nxF '### Round-43 measured results'` prints nothing, `exit=1`, at `9307b15e`, `25df591a` **and** `098df344`; yet the §Round 43 claim table cites `§Round-43 measured results` at `:2314-2316` since `44fa5627` (`git log -S"§Round-43 measured results" -- SCORECARD.md`). So the pointer and the three claim-table references dangle, and a fix that only restores line 53 leaves the references dangling unless the heading is created.
- **Captured-by: `none`.** The counter that owns the fact — `tools/round42-selfdesc-reconcile.py:26-31` (`planned`: must name `### Planned (round <maxN+1>)`, and that heading must exist as a line followed by a numbered item) — reads `planned=0 … mismatches=0 met=True`, `exit=0` at the defective tip: `python3 tools/round42-selfdesc-reconcile.py --repo <clone> --tip 9307b15e0731f91efbd17ea10ef0d579fc1c9065` (`S9Mistake/selfdesc-9307.out`). A split string passes a substring test. The round-43 claim's counter never looked at it: `grep -c Planned tools/round43-registry-audit.py` → `0`.
- **Class: `stale-premise`**; **live defect** at the round-44 freeze (`SCORECARD.md:53`).

## 3. Row (3) — three summaries say the round-43 census had only W04, the end receipt has a W01

- `.ufo/waves/round-43/census-end-mirror.out` has 94 finding lines: `93 W04` plus `:94` = `kama / W01 / S481 tierC mined used-by=corpus/knowledge/runtime-health-surface-processes.md, corpus/lessons/round-43.md`. Histogram via `awk -F'\t' '$2 ~ /^W[0-9]/ || $2=="E" {c[$2]++} END{…}'` → `W01 1`, `W04 93`; the start receipt is `W04 93` with no W01 (`S9Mistake/d3-census-classes.out`).
- The summaries: round-43 report `.ufo/reports/round-43/kama.md:80` at fleet `b0fd7b7f` ("exit 0, 93 W04, 0 E at start and end"), `corpus/lessons/round-43.md:57` ("validate exit 0 with 93 W04 and 0 E"), and **still live at the freeze** `SCORECARD.md:63` (same sentence). `0 E` is literally true; the defect is the omitted class — and the omitted W01 is S481, the tier-C row the round itself admitted.
- **Captured-by: `none`.** The census tool prints rows, not a summary; the sentence was hand-counted. `tools/report-landing-audit.py` audits report paths and source URLs, not warning counts; the round-43 counters score only their own `met` legs. Only the outside closure re-read the receipt (§7 D3).
- **Class: `stale-premise`**; **live defect** via `SCORECARD.md:63`.

## 4. Proposed fixes, each shown to fail on the defective tree

All three checkers are in `S9Mistake/` and are **proposals** (counters are frozen; nothing was added to `tools/`).

1. **Pin trigger consumer.** `pin-trigger-consumed.py --repo <lane clone> --tip <commit> --receipt <pin-watch out>`: every `status=behind` line must have `registry/release-recheck-<newest>.tsv` at the tip.
   - Fails now: `--tip 9307b15e… --receipt .ufo/waves/round-42/w1/out/R42B14/b1.out` → `missing llama.cpp newest=b11887: no registry/release-recheck-b11887.tsv at 9307b15e0731` / `met=False`, `exit=1`. Same against the round-44 freeze receipt at `098df344` (`b11889`).
   - Passes when fixed: fixture repo (`D=$(mktemp -d -p <scratch>)`, `git -C "$D" init -q`, `git -C "$D" rev-parse --show-toplevel` verified `= $D`, add `registry/release-recheck-b11887.tsv`, commit with `-c user.name=fixture -c user.email=fixture@localhost`) → `ok llama.cpp newest=b11887 consumer=registry/release-recheck-b11887.tsv` / `met=True`, `exit=0`.
   - Transcript: `S9Mistake/a-trigger-check.out`.
2. **Planned pointer.** `planned-pointer-check.py <SCORECARD.md>`: (i) the first `## Planned` section must contain the contiguous sentence `The live plan is `### Planned (round N)` at the end of this file`; (ii) every `§Round-<N> measured results` reference must resolve to a heading line.
   - Fails now: at `9307b15e` and `098df344` → `pointer: first ## Planned section lacks the contiguous …` and `measured: dangling reference §Round-43 measured results — no line '### Round-43 measured results'`, `met=False`, `exit=1`.
   - Discriminating, not always-red: at `25df591a` the pointer leg prints `ok (The live plan is …)`; only the older dangling `§Round-43 measured results` reference keeps that commit at `met=False`.
   - Transcript: `S9Mistake/d1-pointer-check.out`.
3. **Census summary vs receipt.** `census-summary-check.py --receipt <census out> --sentence <file>`: every warning class in the receipt must be named with its count.
   - Fails now: against the verbatim `kama.md:80` sentence → `missing class W01: receipt has 1, sentence does not name it`, `receipt=W01=1 W04=93`, `sentence=E=0 W04=93`, `met=False`, `exit=1`.
   - Passes on the corrected sentence `… with 93 W04, 1 W01 and 0 E …` → `met=True`, `exit=0`.
   - Transcript: `S9Mistake/c-census-check.out`; inputs `c-report-sentence.txt`, `c-fixed-sentence.txt`.

Fixture recipe and the exact comparison the checker makes are in `mistakes.md` N1–N5; the fixture itself was scratch and is deleted, so the pass side is re-runnable from the recipe, not from a retained path.

## 5. Findings beyond the three rows

- **F1 (counter blind spot, not fixed: counters frozen).** `tools/round42-selfdesc-reconcile.py`'s `planned` fact passes at a tree where the pointer sentence is split across 13 lines (`selfdesc-9307.out`, `planned=0 met=True`). A substring test cannot distinguish "the sentence exists" from "the sentence's first half exists somewhere in the section". The proposed contiguous-regex fact is the minimal repair and is the check in row (2).
- **F2 (pre-existing dangling reference).** `§Round-43 measured results` is cited from `SCORECARD.md:2314-2316` from commit `44fa5627` onward and never resolved to a heading in any commit. This is older than the tip regression and is not covered by closure D1's wording ("restore line 53", "give the section its own heading") unless the heading creation is understood to fix it.
- **F3 (live at freeze).** `SCORECARD.md:53` and `:63` at `098df344` carry rows (2) and (3) unchanged; any round-44 lesson that says these were repaired would be false unless a correction note lands this round.
- **F4 (row (1) not closed by this round's own contract).** The C1 draft ledger carries `holds=81 unchanged-file=4 TODO=6` of 91 (`verdict` column of `.ufo/waves/round-44/c1/draft-ledger.tsv`), and `controls/base.c1.out` reads `unverified=91`. The row must be drafted as an open defect with a standing gate, not as "fixed in round 44".

## 6. Touched surfaces and out-of-scope

- Written: `S9Mistake/mistakes.md` (draft rows + N1–N5) and the receipts/checkers under `S9Mistake/`; this report. Nothing else in the lane or fleet repo was written; no `git add/commit/checkout` in the lane; no mutating `jj`.
- Out of scope (untouched by design): C1/C2 ledgers and fragments, preregistration, counters, controls, `corpus/SOURCES.md`, `SCORECARD.md` repairs, and the round-44 lesson file itself (absent: `test -f corpus/lessons/round-44.md` → no). Proposed edits are the checkers, not in-place patches.
- Tooling: nothing installed or upgraded (no pacman, no uv/npx/binary install). Read-only git, `awk`, `python3` stdlib only.

## Artifact paths

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9Mistake.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9Mistake/mistakes.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9Mistake/a-pinwatch-history.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9Mistake/a-trigger-check.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9Mistake/pin-trigger-consumed.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9Mistake/d1-pointer.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9Mistake/d1-commit-hunk.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9Mistake/d1-pointer-check.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9Mistake/planned-pointer-check.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9Mistake/selfdesc-9307.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9Mistake/d3-census-classes.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9Mistake/c-census-check.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9Mistake/c-report-sentence.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9Mistake/c-fixed-sentence.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9Mistake/census-summary-check.py`
