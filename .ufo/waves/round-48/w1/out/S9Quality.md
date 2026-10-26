# S9Quality — round 48 wave-1 report (kama), leaf seat

**Verdict: KQ72–KQ75 are drafted, paste-ready, and every `Check:` inside them was run this seat at the round-48 build (`380bcdff9c8af06997c482f6eb03db926a794a2b`) with the exit codes the rows state; four criteria-level findings are filed below (one stale prose declaration of record, one KQ66 byte-count gap, one region narrower than its row's rule, one counter guard that forbids the strictly-better state), and no lane file was edited.**

Deliverable for integration: append the block in `.ufo/waves/round-48/w1/out/S9Quality/criteria.md` at the end of `corpus/QUALITY.md` (after the round-47 footer, currently line 400). The block is a heading, an intro line, a four-row table with the same columns as the file, and a drafted-by footer naming suppressions (KQ72→KQ71, KQ73→KQ52, KQ74/KQ75→KQ69).

## The four rows and what each is bound to

| Row | Subject | Check the row names | Receipt this seat wrote |
|---|---|---|---|
| KQ72 | region-scoped append-only claims (a carve-out is real only as a bound `region` cell that the audit grades) | `python3 tools/append-only-audit.py --repo <clone> --to <tip> --contract registry/append-only-contract.tsv --json` → `files=89 events=5 restored=5 regressed=0 bad_declarations=0 ungraded_lines=89`, exit 0 | `aoa-v3-lane.json` |
| KQ73 | superseded SCORECARD head text (rewrite ⇒ append the replaced lines byte-exact; `regressed=0`) | same tool at the landed tip vs the base; byte equality of `SCORECARD.md:2740`/`:2742` against `SCORECARD.md:6` at `82b5e9d3`/`4340cf2f` | `aoa-v3-lane.json`, `aoa-v3-at-base.json`, `banner-bytes.out` |
| KQ74 | record-time provenance (v5 `verified` block bound to the run's own inputs, model pinned to a 40-hex revision) | `.ufo/waves/round-48/w1/out/S9Quality/receipt-provenance-check.py receipt-{1,2,3}.json` → `receipts=3 bound=1`, exit 0; mutants exit 1 | `provenance-check.out`, `provenance-check-mutants.out` |
| KQ75 | replay comparison (pass/fail is not a reproduction; stable surfaces are compared) | `python3 tools/kama-live-replay.py --compare A B` → instance-only copy exit 0, five single-surface stable changes exit 1 | `compare-instance.out`, `compare-stable.out` |

## Commands run (all from the fleet root, all read-only on the lane)

```
S=/fast/scratch/hyaku/kama-r48/S9Quality; O=<lane>/.ufo/waves/round-48/w1/out/S9Quality
git clone -q --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"      # ok; clone HEAD b85783e8 (lane past the build), every measurement names 380bcdff explicitly
python3 tools/round48-append-audit-v3-check.py --repo "$S/lane" --tip 380bcdff… --scratch "$S/c1" --out "$O/c1-check.out"
   → selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True   exit=0
python3 tools/round48-live-replay-v5-audit.py --repo "$S/lane" --tip 380bcdff… --scratch "$S/c2" --out "$O/c2-check.out"
   → receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True   exit=0
python3 tools/append-only-audit.py --repo "$S/lane" --to 380bcdff… --contract registry/append-only-contract.tsv --json
   → commits=311 files=89 events=5 restored=5 partial=0 unrestored=0 regressed=0 vanished=0 bad_declarations=0 ungraded_lines=89   exit=0
python3 tools/append-only-audit.py --repo "$S/lane" --to 33e0058… --contract <tip contract, `$S/contract-v3.tsv`> --json
   → commits=309 files=89 events=5 restored=5 regressed=1 ungraded_lines=89   exit=1
     (0718b6ab SCORECARD.md restored_max=2349 held_at_to=2348 → 2349/2349 at the tip: one graded line, the round-45 banner)
python3 kama-live-replay.py --compare receipt-1.json <instance-only copy>   → compare match=True mismatches=0  exit=0
python3 kama-live-replay.py --compare receipt-1.json <n_ctx 256→512 copy>   → compare match=False mismatches=1, mismatch: projection:props:…256…->…512…  exit=1
python3 receipt-provenance-check.py receipt-{1,2,3}.json                    → receipts=3 bound=1  exit=0
python3 receipt-provenance-check.py <commit/url→main copy> <archive digest first hex digit altered>
                                                                           → commit-40hex=0 / archive-digest=0, receipts=2 bound=0  exit=1
```

Both frozen counters reproduce the L1's pre-wave dry run exactly on an independent clone (C1 `rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 met=True`; C2 `replayed=3/3 met=True`). No counter, contract, preregistration or control was modified; the C2 run downloaded from github.com and huggingface.co into its own scratch and left nothing behind.

## Evidence that grounds the new rows (not decoration — each row asserts it)

- **89 ungraded lines are exactly the exempt head.** `dd9f5dc6` SCORECARD.md ungraded 17 + `0718b6ab` SCORECARD.md ungraded 72 = 89; the other four events have `ungraded=0` (`aoa-v3-lane.json`). So KQ72's "the round states the ungraded mass" has a real number and a named composition.
- **The region fixtures fail as declared.** Athwart the carved-out `## Axes`, the counter's constructed fixtures read `exempt-rewritten` deleted 24 / graded 0 / exit 0 and `exempt-gutted` 24 / 24 / unrestored / exit 1, `only-errata` body 25 lines graded 0 and Errata 20 graded 20 (`tools/round48-append-audit-v3-check.py:500-560`, names at the `yield` sites). A line-count-preserving head rewrite is therefore *unwatched*, which is why KQ72 also requires the head reconcilers.
- **Byte-exact supersession.** `SCORECARD.md:2740` sha256 `01f0f0fa65de…3b43` equals `SCORECARD.md:6` at `82b5e9d3`; `:2742` sha256 `ee3ce7e2405b…8fb6` equals `SCORECARD.md:6` at `4340cf2f`; 754 and 758 bytes, `equal=True` (`banner-bytes.out`, produced by reading both blobs).
- **Record-time refusal precedes execution.** `tools/kama-llamacpp-live.py:193-218` (`verify_archive_member`, three refusal tokens) is called at `:1559`, before `Popen` at `:1648`; the `recordcheck` leg drives five refusals with a stub server (marker absent) and a positive control (marker written) — `recordcheck=1`.
- **Pin binding.** `tools/kama-llamacpp-live.py:71` `PINNED_MODEL_URL`, refusal at `:1475-1479`; the three receipts carry `commit=499bc8821c6b12b4e53c5bffcb21ec206f212d81` and `/resolve/499bc882…/` in `provenance.model.url` (`provenance-check.out`).
- **Projection shape.** `tools/kama-live-replay.py:154-175` names the eight compared surfaces; `compare` at `:177-202` adds `original:no-evaluated-check` at `:191`, so an empty check list cannot pass vacuously.

## Findings

### F1 — `corpus/README.md:759-761` still declares five append-only files while the round-48 contract declares nine rows / 89 files, and that sentence is the `declared_at` of three rows

- File/line: `corpus/README.md:759-761` (unchanged at `380bcdff`; `git diff --stat 33e0058 380bcdff` lists no `corpus/README.md`). Contract rows binding to it: `registry/append-only-contract.tsv:4` (`corpus/QUALITY.md`), `:5` (`corpus/README.md`), `:3` (`SCORECARD.md`).
- Repro: `git show 380bcdff9c8af06997c482f6eb03db926a794a2b:corpus/README.md | sed -n '759,761p'` → "sets the five files the lane treats as append-only (SCORECARD.md, LOG.md, corpus/QUALITY.md, corpus/README.md, corpus/SOURCES.md)"; `python3 tools/append-only-audit.py … --json | jq .files | length` → 89.
- Why it matters: KQ71's rejected cell names this exact sentence as the prose-set defect, and the round *widened* the contract (two rows, `registry/report-landing-errata.tsv` and the consumer-registry Errata region) without appending a superseding sentence. A reader who follows the prose alone audits five files; the declaring line of three rows is itself false about the population. README.md is append-only, so the fix is an append, not an edit.
- Proposed fix (append at the end of `corpus/README.md`):
  `Round-48 correction (appended; supersedes the five-file sentence at corpus/README.md:761 above): registry/append-only-contract.tsv declares nine rows — the five files named there plus corpus/lessons/*.md, registry/history/DELTA.md, registry/report-landing-errata.tsv and the ## Errata region of corpus/knowledge/consumer-registry.md — and at 380bcdff9c8af06997c482f6eb03db926a794a2b the audit's population is files=89, regressed=0, ungraded_lines=89, exit 0.`

### F2 — the v5 receipts meet KQ69 but only two thirds of KQ66: no byte count for the archive, the member or the model

- File/line: `provenance` block of `.ufo/waves/round-48/c2/live/receipt-1.json` (keys `model{commit,sha256,url}`, `server{asset_sha256,asset_url,member}`, `verified{archive_sha256,at,member_sha256,model_sha256}` — no size field anywhere); the inputs are still named by host path (`server.arg=/home/vgpnk/.local/opt/llama-b11909/llama-server`, `model.path=/fast/scratch/hyaku/kama-r48/L1/live/stories260K.gguf`).
- Repro: `python3 -c "import json;d=json.load(open('<receipt-1>'));print(sorted(d['provenance']),sorted(d['provenance']['server']),sorted(d['provenance']['model']))"`; a `size`/`bytes` grep on the file finds only occurrences inside captured response bodies (`"size\":1171200`), none for the archive or the model (round-47 Gate records the asset at 22475032 bytes and the model at 1185376 bytes, from `corpus/lessons/round-47.md` — the receipts record neither).
- Why it matters: KQ66 requires "re-fetch URL, byte count and SHA-256" for every input named by host path; KQ69 supplements it and does not drop the byte count. Round 47's lesson rejected the host path as a locator — the URL and digest fix re-fetch, the missing size is the one leg of KQ66 left unaddressed, and `model.path` now names deleted seat scratch.
- Proposed fix (two options, either closes it): (a) lane — add `bytes` to `provenance.server` (archive), `member_bytes` and `provenance.model.bytes` in `tools/kama-llamacpp-live.py` where `verify_archive_member` runs (`:193-218`), bump the receipt schema and the replay's expected keys; or (b) corpus — append a superseding KQ row stating that a receipt that a replay re-acquires and hashes twice satisfies the byte-count leg without recording it, and that a host-path input record with URL + SHA-256 + a passing replay is not a dead pointer. (b) is the smaller change and keeps QUALITY.md append-only.

### F3 — the consumer-registry row's `only=## Errata` region is narrower than the row's `A-corr` rule: 52 of 414 lines graded, and the sections below Errata are ungraded with no note saying so

- File/line: `registry/append-only-contract.tsv:10` (`rule A-corr`, `region only=## Errata@corpus/knowledge/consumer-registry.md:30`, note "only the `## Errata` region is declared append-only …; the dated census body above it may be edited").
- Repro: section counts at `380bcdff` — `## Errata — 2026-10-14 …` 52 lines, `## Consumer table` 101, `## Live verdicts` 75, `## Correct-pin exemplars` 45, `## Search roots` 29, `## Non-model loopback pins` 16, `## Corrections — round 10` 16, `## The one-line finding` 14, `## Provenance supplement` 14, `## Open gaps` 15, `## Cross-lane demand evidence` 13, `## Correction — round 16` 9, head 15.
- Why it matters: `only=` is a whitelist, so a deletion anywhere outside Errata is ungraded — including the three appended correction sections (`## Corrections — round 10`, `## Provenance supplement — round 11`, `## Correction — round 16`) that the `A-corr` rule exists to protect. The note reads like a blacklist of one section ("the dated census body above it may be edited") and under-describes the region by 362 lines. A round that cites KQ72 would report the mass; the contract itself should say it.
- Proposed fix (contract-row change, both rows bind): append inside the Errata section of `corpus/knowledge/consumer-registry.md` the line `The ## Correction and ## Provenance supplement sections below are append-only as well.`, then add a contract row `corpus/knowledge/consumer-registry.md	A-corr	corpus/knowledge/consumer-registry.md:<that line>	only=## Correction@corpus/knowledge/consumer-registry.md:<that line>` (a file may carry several rows; `tools/append-only-audit.py:351-362` unions the prefixes). The C1 counter's contract leg asserts required rows, not an exact set (`tools/round48-append-audit-v3-check.py:665-700`), so an additional bound row keeps `contract=1`, and `files` stays 89.
- Alternative if the narrowing is intended: change the row's rule from `A-corr` to `A` and write the narrowed scope in the note ("only the `## Errata` section is append-only; every other section may be edited"), so the note and the region say the same thing.

### F4 — the C1 counter's lane verdict requires `ungraded_lines > 0`, so a lane with no carve-outs (strictly better append-only discipline) cannot read `met=True`

- File/line: `tools/round48-append-audit-v3-check.py:89` ("… regressed 0, vanished 0, bad declarations 0, ungraded lines > 0") and the code at `:718-720` (`verdict = (… and ung > 0 and rc["exit"] == 0)`).
- Repro: `grep -n 'ungraded lines > 0' tools/round48-append-audit-v3-check.py` → line 89; `sed -n '715,722p'` shows the `ung > 0` conjunct. Any contract that grades every line, or a lane whose head sections simply stop moving, yields `ungraded_lines=0` and `met=False` with `lane=0`.
- Why it matters: the guard exists so the region code cannot be vacuous (a fair concern for *this* round), but as a standing criterion it ranks the weaker discipline above the stronger one, and the next round inherits a red that is not a defect. My KQ72 avoids importing the same shape: it requires the ungraded mass to be *stated*, not to be positive.
- Proposed fix: replace `ung > 0` with "the region code was exercised at least once", e.g. require `ung > 0 or (a fixture exercised the region at the tip's contract and `vn`/`only` rows still bind)`; or record the limit in the preregistration's `limits` cell so a later `ungraded_lines=0` lane is diagnosed instead of trusted. Either way it is a counter change for the lane, not for this frozen counter — this seat only records it.

### F5 — KQ71's embedded census counts no longer reproduce (17/15/2 at the build, not 13/11/2)

- File/line: `corpus/QUALITY.md:398` (KQ71's check cell: "`heading-census.py --repo <clone> --head <tip>` prints `headings=13 covered=11 uncovered=2`").
- Repro: `python3 .ufo/waves/round-47/w1/out/S9Quality/heading-census.py --repo <clone> --head 380bcdff9c8af06997c482f6eb03db926a794a2b` → `headings=17 covered=15 uncovered=2`; both uncovered headings are `SKILL.md:1434` and `SKILL.md:1444` instrument-registry headings, and `corpus/knowledge/consumer-registry.md:30` now reads `covered=yes` because the round-48 row covers it.
- Why it matters: this is the defect my new rows are written to avoid — a criterion that embeds a moving count goes stale the moment a round appends. The predicate (`uncovered ⊆ dispositioned headings`) still holds; only the numbers are wrong, so the row is misleading without being false about the rule.
- Proposed fix: append a superseding note row (QUALITY.md is append-only) with the shape-only wording: "`heading-census.py … --head <tip>` prints `uncovered=<n>` and each uncovered heading is dispositioned; the counts move as files grow and are cited from the round's receipt, never embedded in the criterion." No tool change needed.

## Handoff notes for the L1

- The four rows cite `corpus/lessons/round-48.md` §Claims C1, §Claims C2 (with its `limits` cell), §Claims C1 build finding and §Gate — the section names the round-47 lesson uses. If the round-48 lesson names them differently (it did not exist when this block was drafted), map the citations to its headings; no row depends on a count from it.
- The block is 12 lines: one `## Criteria added — round 48 …` heading, one intro paragraph, a header row, a separator, KQ72–KQ75 and the drafted-by footer. Table shape validated (`|`-split: 4 cells per row). Insert at the end of `corpus/QUALITY.md`, after the round-47 footer at line 400; nothing above moves.
- Two rows (KQ72, KQ73) name counters whose receipts are in this directory; KQ74 names `receipt-provenance-check.py`, which is a seat artefact, not a lane tool — if the L1 wants it cited from a lane document it must be moved into `tools/` by the integration commit, which is a lane change this seat may not make.

## What I did not do (scope)

- No lane file edited, no `git add/commit/checkout/stash/reset`, no jj mutation; every lane read went through `git -C <shared clone>` or `git show` at an explicit revision.
- No counter, contract, preregistration or control changed (frozen); F3's and F4's fixes are proposals with exact text, in this report only.
- No service started or stopped; the C2 counter's own replay lifecycle ran entirely under `$S/c2` with `HOME`, `XDG_CACHE_HOME` and `TMPDIR` inside it, and the lane tool picked its own loopback port.
- No subagent dispatch (leaf), no message to `agent://all`.
- Known integration items (gate-registry unregistered counters, the 33-vs-34 spot-check count, hexrun unknown `d0012618`) not re-reported.
- Tooling: nothing installed or upgraded this round.

## Artifacts written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Quality.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Quality/criteria.md` (KQ72–KQ75, paste-ready)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Quality/receipt-provenance-check.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Quality/c1-check.out`, `c1-check.stdout`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Quality/c2-check.out`, `c2-check.stdout`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Quality/aoa-v3-lane.json`, `aoa-v3-lane.err`, `aoa-v3-at-base.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Quality/provenance-check.out`, `provenance-check-mutants.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Quality/compare-instance.out`, `compare-stable.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Quality/banner-bytes.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Quality/receipt-1.json` (cited receipt copied from `380bcdff:.ufo/waves/round-48/c2/live/receipt-1.json`)
