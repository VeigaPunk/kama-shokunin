# S9Scorecard — round-47 SCORECARD section draft and head re-anchors

**Verdict: the `## Round 47` section is drafted and the thirteen head moves it forces are validated green — a scratch clone carrying the section *and* the head re-anchors reads `mismatches=0 met=True` on both head counters (exit 0) and `met=True` on the planned-pointer check; the section alone reads `mismatches=9`, and the nine `detail:` lines are exactly the requirement list.**

## What was produced

| File | What it is |
|---|---|
| `round-47-section.md` | the section text to insert verbatim at EOF (after round 46's `### Planned (round 47)`): authority line, two-row claims table with counting commands and evidence, controls line, the build-commit audit prose, the restated `**Capabilities — canonical list as of round 47**` block (11 rows, merged from seat S9Cap's block), and `### Planned (round 48)` with two items |
| `head-reanchors.md` | the 13 required line moves with "read by" and one evidence pointer each, what stays put, and the validation table |
| `head-reanchors.diff` | `git diff` final-a → final-b: the head moves only (SCORECARD head + one PROVINCE.md cell) |
| `round-47-section.diff` | `git diff` base → final-a: the section only |
| `canon-round-47.md` | the merged canonical block as delivered (S9Cap's `canonical-round-47.md` lines 11-27, verbatim) |
| `apply-draft.py` | applies `section` or `full` to a clone; asserts the toplevel, every `old` occurring once, and refuses if a round-47 section already exists |
| `never-held.py` | names the deleted lines a mass-deletion event never holds again, from the frozen v2 definitions (hunk-header indices, byte-exact multiset, window maximum) |
| `reconcile41-*.out`, `reconcile42-*.out`, `planned-pointer-*.out`, `digest-ledger-*.out`, `hexrun-census-*.out`, `c1-counter-at-build.out`, `append-only-v2-at-build.out`, `v1-at-*.out`, `never-held-*.out` | receipts, one per run below |

## Commands and outputs

Scratch: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r47/S9Scorecard/lane`, `TMPDIR` inside the same root; the clone was deleted before this report was written.

```
$ git rev-parse --show-toplevel          # before any commit
/fast/scratch/hyaku/kama-r47/S9Scorecard/lane
$ python3 apply-draft.py <clone> section && git commit      # final-a 7ba2c796bf604d426c9c3a61d0652f5b30d88624
$ python3 apply-draft.py <clone> full    && git commit      # final-b 1d9102972faf84d38ee0a78e37ded85193ad040c
```

**Section only (final-a)** — the requirement list, verbatim:

```
$ python3 tools/round41-scorecard-reconcile.py --repo . --tip final-a
axes=6 facts=36 hash_bad=0 lines_bad=0 run_bad=1 dead=0 score_bad=0 hollow=0 mismatches=1 met=False
detail: calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '32' (exit 0)
exit 1
$ python3 tools/round42-selfdesc-reconcile.py --repo . --tip final-a
r41=1 banner=1 planned=1 retired=1 saturation=1 caps=1 receipts=0 readme=0 province=3 rel=0 mismatches=9 maxN=47 met=False
detail: r41 calibration run … no stdout line == '32'
detail: banner: head lacks 'Latest measured round: 47'
detail: planned: section does not name '### Planned (round 48)'
detail: retired: does not state '11 capabilities'
detail: saturation: does not state 'first-working rounds 10, 14, 16, 20, 25, 30, 41, 42, 43, 46, 47'
detail: caps: head names [ …10 names… ] != canon (round 47) [ …11 names including live-receipt-replay… ]
detail: province: PROVINCE.md lacks registry/append-only-contract.tsv (capability append-only-audit)
detail: province: PROVINCE.md lacks tools/round47-append-audit-v2-check.py (capability append-only-audit)
detail: province: PROVINCE.md lacks tools/kama-live-replay.py (capability live-receipt-replay)
exit 1
```

**Section + head re-anchors (final-b)**:

```
$ python3 tools/round41-scorecard-reconcile.py --repo . --tip final-b
axes=6 facts=36 hash_bad=0 lines_bad=0 run_bad=0 dead=0 score_bad=0 hollow=0 mismatches=0 met=True      exit 0
$ python3 tools/round42-selfdesc-reconcile.py --repo . --tip final-b
r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=47 met=True   exit 0
$ python3 tools/planned-pointer-check.py SCORECARD.md
pointer: ok (The live plan is `### Planned (round 48)` at the end of this file)
measured: ok (### Round-14|41|42|43|44|45|46 measured results)
met=True                                                                                                exit 0
$ python3 tools/planned-pointer-check.py <SCORECARD with a block inserted inside the pointer sentence>
pointer: first ## Planned section lacks the contiguous '…' sentence                                   exit 1
```

The two probes that close the transitive requirements:

```
$ # final-b with the coverage-row PROVINCE hash left at 659a5101…   (b0c499be)
hash_bad=1 lines_bad=0 run_bad=0 … mismatches=1 met=False
detail: coverage sha256 PROVINCE.md cited 659a5101… observed 929f3e3e…            exit 1
$ # final-b + S9Skill's round-47 SKILL.md rows, depth row not re-anchored (c77e00c9)
hash_bad=1 lines_bad=1 run_bad=1 … mismatches=3 met=False
detail: depth sha256 SKILL.md cited 1ad95066… observed 682fba3b…
detail: depth lines SKILL.md cited 1442 observed 1463
detail: depth run `grep -c '^## ' SKILL.md` no stdout line == '34'               exit 1
$ # the same with the depth row re-anchored (afbef463)
mismatches=0 met=True / mismatches=0 met=True                                     exit 0, 0
```

## Findings

**F1 — the calibration row was red before any round-47 edit (head, stale at the freeze).**
`SCORECARD.md:18` prints `→ `32`` for `corpus/lessons/*verifier-spotcheck.md`; the tree holds 33 (`ls corpus/lessons/*verifier-spotcheck.md | wc -l` → 33) since the round-46 closure landed at `172b8ad0`. Both counters were red at `46a924e0` before this seat touched anything (`reconcile41` `mismatches=1`). Fix: requirement #2. Derived, not re-typed: the run fact is the one place the count lives.

**F2 — the capability description was false at the build commit, and no counter can see it.**
`SCORECARD.md:130` (head mirror) and `:2463` (round-46 canon) describe "the lane's five append-only self-description files"; `registry/append-only-contract.tsv` expands to 85 files (`append-only-v2-at-build.out`: `summary commits=303 files=85 events=5 restored=3 partial=2 unrestored=0`), 79 of them `corpus/lessons/*.md`. The `caps` leg compares names only and the `province` leg only requires tokens to appear, so a stale capability *description* passes both — and it did: `caps=0` at final-a with the five-file text still in place. Fix: requirement #6 (the restated row). Instrument gap for a later round, not fixable in place (counters frozen): a leg that compares a canon row's declared file set with the tool's `--json .files` length.

**F3 — the eleven-capability entry is a table event, not a score move, and the preregistration does not word it as an acquisition.**
C2's preregistration text is "measured (operability, sourced on the b11909 release row opened this round)" with `8->8`; round 46's C2 was explicitly "capability acquisition". The table's own rule (`AXES.md` §Capabilities: rows enter only through a round that demonstrates the capability running) is satisfied — `tools/kama-live-replay.py` runs end to end (C2's `replay` leg; seats X2Replica and K2Fresh report the same), and seat S9Cap measured `listed 11 observed 11 missing 0 unsubstantiated 0 met True`. The draft therefore enters `live-receipt-replay` (first-working 47) and keeps the score at 8, and says both. If the L1 prefers the narrower reading (no row), then requirements #6 (second row only), #8, #9, #10 and the §Saturation sentence revert and §Retired/§Saturation stay at 10/46 — a 10-row variant was run earlier in this seat (green on both counters) and then superseded when seat S9Cap's block arrived; its receipts were overwritten by the final ones, so it is a statement about this seat's work, not a retained artifact. It is not the delivered draft because the capability genuinely runs.

**F4 — the depth row is a live requirement, not a stable one.**
If the integration applies seat S9Skill's `## Round-47 instrument registry` rows (as round 46 applied its own), `SKILL.md` becomes `682fba3b…`, 1463 lines, 35 `## ` headings and requirement #13 fires (`hash_bad=1 lines_bad=1 run_bad=1`). Recompute #13 from the applied bytes at the integration commit; do not copy these numbers if the rows differ.

## De-duplication rule for the integration

The canonical block is in **one** place: `round-47-section.md` (inside the
`## Round 47` section). Seat S9Cap's `proposed.patch` also carries the block
plus the four companion edits; applying both lands two
`**Capabilities — canonical list as of round 47**` markers. S9Cap measured the
effect as `capability_tables 14` instead of 13 (their report; not re-run here).
Take the head/PROVINCE hunks from `head-reanchors.diff` (or from
`proposed.patch`) and the canon block from the section draft — once. Placement
is not load-bearing: the block inside the section and the block before the
heading both read `caps=0`, because the canon is the first capability table
after the highest marker.

## State of the lane at report time (not mine)

The lane's committed tip is still `46a924e0`; its working tree carries the L1's
uncommitted integration (12 files, +477/−50, including `SCORECARD.md` +47,
`PROVINCE.md`, `SKILL.md` +21, `corpus/README.md` +133 and edits under
`tools/`). None of it is this seat's: every write here went to
`.ufo/waves/round-47/w1/out/S9Scorecard/` and this report, and every run used
the throwaway clone. Line numbers in `head-reanchors.md` are at `46a924e0` and
will drift with those edits; the counters, not the line numbers, are the
authority — re-run them after the integration lands.

`SKILL.md` in that working tree already carries the round-47 rows, so
requirement #13 is live: read at report time it is sha256
`ddb80f6e275d345badd2fd554b0759842d8287387a4579affe71143e0e783555`, 1463 lines,
35 `## ` headings — not the `682fba3b…` of the S9Skill-row probe. Use the
applied bytes.

## Provenance of the numbers in the drafted section

| Figure | Command | Exit | Receipt |
|---|---|---|---|
| C1 at build `selftest=1 contract=1 lane=1 fixture=1 stable=1 files=85 lane_events=5 lane_mismatch=0 fixture_mismatch=0 met=True` | `python3 tools/round47-append-audit-v2-check.py --repo <clone> --tip 3a09a1d9… --scratch <dir>` | 0 | `c1-counter-at-build.out` |
| v2 at build: 5 events, `deleted=2421 restored_max=2420`, LOG `2292/2292`, 85 files, 303 commits, exit 1 | `python3 tools/append-only-audit.py --repo <clone> --to 3a09a1d9…` | 1 | `append-only-v2-at-build.out` |
| numstat `2421` SCORECARD, `2292` LOG | `git diff --numstat --no-renames 0718b6ab^1 0718b6ab -- SCORECARD.md LOG.md` | 0 | quoted in the section |
| v1 at `4a2a4d55` `2417/2416`; at build `2417/2409`; v2 at build `2421/2420` (r46-D2 closed) | `python3 <v1 exported from 4a2a4d55> --repo <clone> --to <rev>` | 1 | `v1-at-4a2a4d55.out`, `v1-at-build.out` |
| the 7 never-held `dd9f5dc6` lines are the six round-41 `## Axes` rows and the round-41 reconcile sentence; the 1 never-held `0718b6ab` line is the round-44 `depth` row | `python3 never-held.py <clone> <commit> SCORECARD.md 3a09a1d9` | 0 | `never-held-dd9f5dc6.out`, `never-held-0718b6ab.out` |
| contract: 8 lines (header + 7 rows), expansion 85 files of which 79 lessons | `git show 3a09a1d9:registry/append-only-contract.tsv \| grep -c .`; `git ls-tree -r --name-only 3a09a1d9 \| grep -c '^corpus/lessons/.*\.md$'` | 0 | 8 / 79 |
| receipts are v4/pass/11 evaluated checks/`b11909-caa8191df`/member `llama-b11909/llama-server`/`log_path` null | `python3 -c` over the three JSON files | 0 | `.ufo/waves/round-47/c2/live/receipt-{1,2,3}.json` |
| b11910, prerelease, published 2026-10-26T21:20:07Z | `gh api 'repos/ggml-org/llama.cpp/releases?per_page=4'` (one request) | 0 | quoted in `### Planned (round 48)` item 2 |

Not run here, and therefore not claimed: the C2 counter's own legs (`replay`, `tamper`) — the section quotes the L1's pre-wave dry run `receipts=1 replay=1 tamper=1 newrow=0 rerun_checks=11 met=False` as the L1's, not as this seat's evidence; and no measured-commit receipt, because the measured commit does not exist yet.

## Out of scope / not done

- No lane product file was written. The `SCORECARD.md` and `PROVINCE.md` changes exist only as `round-47-section.md`, `head-reanchors.diff` and the clone commits named here; the only lane writes are this report and `.ufo/waves/round-47/w1/out/S9Scorecard/`.
- No counter, preregistration or control was edited. Nothing was run against the lane itself.
- The measured-results block (`### Round-47 measured results`) is not drafted: it carries numbers only the measured commit produces. When it lands, add the heading in the same commit as any `§Round-47 measured results` reference, and keep it out of the `## Planned` pointer sentence (`planned-pointer-check.py` is the guard).
- Seat S9Skill's SKILL rows, S9Quality's KQ rows, S9Lesson and S9Readme were used only as inputs to requirement #13; this seat did not review them.
- `MISSION.md:29` still says "operability + freshness" (open L0 question since round 35) — reported, not absorbed.

## Tooling

No tool was installed or upgraded; `gh` (already authenticated) was used for one releases query. `pacman` not run (host-wide pause).
