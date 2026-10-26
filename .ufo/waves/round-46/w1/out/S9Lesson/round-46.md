# kama round 46 lesson

author: kama L1 (agent `KamaR46`) — skeleton drafted by wave seat `S9Lesson`
date: 2026-10-26
base: `0163fea2dab3f282ebd70c71da9ab5de4cedf733`
freeze: `5790944350ae41bfe2ce50934bba59e086e747f4` (preregistration `.ufo/waves/round-46/preregistration.json`, `frozen_at_utc` 2026-10-26T19:50:02Z; KQ64 receipt `.ufo/waves/round-46/freeze/prereg-time-check.out` → `RESULT pass: no timestamp later than the committer time`, `exit=0`)

status: **skeleton.** Every `[FILL]` is a value only the L1's committed receipts can supply. Nothing below is a measured outcome; the two places that carry numbers today (the C2 base receipt and the wave-yield counts) say where the number came from and when.

## Claims

- **C1 freshness 8→8 (sourced on `[FILL: the b11906 row id]`).** The 91 on-release llama.cpp registry rows re-verified at b11906 `4d71b42fd87db24b8b7c808c151b713aa4459cfd` (17 commits after b11889 `d854d98bae598388ecea1ed84396587e5edc326d`): `registry/release-recheck-b11906.tsv`, `[FILL verdict histogram: unchanged-file / holds / holds-reworded / drifted / removed]`. Counter at `[FILL measured commit]`: `pop=91 rows=91 valid=[FILL] unverified=0 flags_missing=0 section=1 newrow=1 met=[FILL]`, receipt `[FILL .ufo/waves/round-46/c1/*.out]`. Kill rule: `met=False` at the measured commit is C1 not achieved (honest stop, never narrowed after data).
  - Population source is the base tree: **the 20 rows that need reading** are S037 S042 S043 S060 S108 S109 S114 S115 S116 S117 S118 S119 S120 S121 S122 S123 S124 S125 S133 S138 (`tools/server/server-context.cpp`, `server-models.cpp`, and the b11889 `holds-reworded` rows S037/S043/S108); the other 71 rows' files are byte-identical between b11889 and b11906. `[FILL: which of the 20 the ledger files as holds-reworded/drifted/removed, and each one's witness pair]`
  - Controls (frozen, `.ufo/waves/round-46/controls/`): `base.c1.out` `unverified=91 met=False`; `junk-c1-carryforward.c1.out` `valid=71 unverified=20 met=False`; `junk-c1-massreworded.c1.out` `valid=6 unverified=85 met=False`. `[FILL: measured-commit receipt and its line]`
- **C2 calibration 7→7 (capability acquisition).** `tools/append-only-audit.py` (landed `4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050`, after the freeze) versus the lane's own history: `[FILL: the frozen counter's line, selftest= fixture= lane= table= met=]`, receipt `[FILL .ufo/waves/round-46/c2/*.out]`.
  - Base state, independently re-run by this seat (read-only): `python3 tools/append-only-audit.py --repo . --to 0163fea2…` → `summary commits=292 events=5 restored=3 partial=2 unrestored=0`, `exit=1` (`.ufo/waves/round-46/w1/out/S9Lesson/c2-at-base.out`): `0718b6ab` LOG/QUALITY/README restored by `82b5e9d3`, `0718b6ab` SCORECARD partial (2416/2417), `dd9f5dc6` SCORECARD partial (24/31) — both by supersession, not loss (Mistakes row 4).
  - r45-D1 (claim-outcome reader re-freeze) is **deferred** by the round-46 preregistration, so no ledger is re-scored this round: `[FILL: the frontier sample control's path and what it scored]`

## Gate

Rows opened this round (both `mined`, opened 2026-10-26). The row ids are placeholders: the next free id at the base is S486, but seats may have taken ids in this wave.

- **`[FILL: S486]`** — https://github.com/ggml-org/llama.cpp/releases/download/b11906/llama-b11906-bin-ubuntu-x64.tar.gz, accessed 2026-10-26 (asset record `gh api repos/ggml-org/llama.cpp/releases/tags/b11906`, copy `.ufo/waves/round-46/c1/release-b11906.json`). Verified from that copy by this seat: `tag_name` b11906, `target_commitish` `4d71b42fd87db24b8b7c808c151b713aa4459cfd`, `published_at` 2026-10-26T19:45:36Z, `prerelease` true; asset `llama-b11906-bin-ubuntu-x64.tar.gz` 22478121 bytes, `digest` `sha256:064ade6220799fd9e7b1804b574f5f92c38dde358cc987c6b8283cfaeb1eeef3`, equal to the sha256 of the downloaded tarball in `.ufo/waves/round-46/c1/live/install.txt`. Extracted `llama-server` sha256 `c949950e…f3ff`, `--version` "build 11906, commit 4d71b42fd". Located quote `[FILL: the asset digest field, ≤25 words, with location]`. Scope: binary identity and which commit the release names — not runtime behaviour.
- **`[FILL: S487]`** — own-work, `python3 tools/kama-llamacpp-live.py` against the b11906 binary, receipts `.ufo/waves/round-46/c1/live/receipt-1.json` `..-3.json` (sha256 `9ad6ad36…`, `09f049cf…`, `33f1dd57…`). Verified from those receipts: schema `kama-llamacpp-live/v3`, `outcome` pass, ports 33179 / 46073 / 44923, model sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`, tool sha256 `8c0dbb2b…62f3` (equal to `sha256sum tools/kama-llamacpp-live.py` at HEAD `96d32918`), `/health` 200 `{"status":"ok"}`, `/metrics` 501. `[FILL: started/ended UTC, the located quote, and the git commit that makes the receipts tracked — at draft time `git status --porcelain` shows `?? .ufo/waves/round-46/c1/`, so every citation to them is untracked evidence]` Scope: three sampled instants on unregistered loopback ports; not timing, model quality or other builds.

Decisions (the round's admit and reject set; `[FILL: add the seat-driven ones]`):

- **Admit** the b11906 row above, scoped to release→commit identity and the Linux x64 CPU binary. The asset digest, the downloaded tarball's sha256 and the extracted binary's sha256 are three independent checks of the same artifact.
- **Admit** the live-receipt row only with its commit: a receipt that is untracked at the tip cannot support a `mined` row whose `recheck` cell cites it. Round 45 admitted S485 after committing `052cb1e9`; the same order is owed here.
- **Reject** re-asserting a teardown duration as a b11906 property. The three b11906 receipts give `teardown.term_wait_ms` 3, 3, 3; the b11889 receipts gave 15, 9, 7, and round 45's own reject recorded the same reason (`corpus/lessons/round-45.md` Gate, last bullet). Three samples are an observation, not a property.
- **Reject** filing any of the 20 readable rows as `holds` because its file "did not change much". `junk-c1-carryforward.c1.out` is the control: the carried forward b11889 ledger scores `valid=71 unverified=20 met=False`, and its detail line is `S037 invalid: witness_pin rule (… absent from release file)`. A row whose file changed needs its b11906 range read.
- **Reject** treating S039's Hugging Face page as the model re-fetch record that r45-D3 asked for: `corpus/SOURCES.md:51` is the `blob/main` page (no raw URL, no sha), and at the round-46 base the S485 row carries no `models-moved` text (`git show 0163fea2:corpus/SOURCES.md | sed -n 238p | grep -c 'models-moved'` → `0`). The record that closes D3 is `.ufo/waves/round-46/c1/live/model-fetch.txt` (url, path, 1185376 bytes, sha256 `270cba1b…`), and it is a seat-side file, not a registry cell — see Mistakes row 1.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| evidence-durability (round-45 closure **N-E**, routed **r45-D3**) | The b11889 live receipts name their model as the cache path `~/.cache/kama-shokunin/models/stories260K.gguf` and record its sha256; the file was gone at the round-45 closure (`find / -xdev -name 'stories260K*.gguf'` → nothing, closure §1 N-E), and neither the S485 row nor anything under `tools/` held a locator: at the round-46 base `git show 0163fea2:corpus/SOURCES.md \| sed -n 238p \| grep -c 'models-moved\|huggingface'` → `0`, and `git grep -n 'models-moved' 0163fea2 -- tools/` → no output. A sha256 without a locator cannot be re-fetched. The round-46 b11906 run only re-ran because seat X1Live re-downloaded 1185376 bytes first (`.ufo/waves/round-46/c1/live/model-fetch.txt`). | none — the receipt schema records `model.sha256`, never how to obtain it, and the SOURCES `recheck` cell is prose written before the loss | `probe-receipt-durability.py` (this seat, `out/S9Lesson/`): every path a receipt names must exist with the recorded sha256 **and** have a record beside the receipts naming that sha256 plus a locator (URL or `asset <name>`). Shown able to fail: on the round-45 live directory `model=fail:no-side-record-of-sha` for 3/3 receipts, `exit=1` (`durability-r45.out`); on round 46 `model=pass` because `model-fetch.txt` carries the URL, but see row 3; on the in-tree fixture `out/S9Lesson/fixture-live/` (the same receipts plus one log file per receipt), all legs pass, `exit=0` (`durability-fixture.out`). |
| wave-stall-blind (round-45 closure **N-D**) | The round-45 wave was dispatched with 64 seats and **0** took a turn; the lesson recorded "no falsification credit" but no check ran before that sentence. The check that exists for exactly this — `tools/seat-yield.py` (round 45, considerthese proposal 4) — cannot evaluate the case: on `.ufo/waves/round-45/w1` it prints `could-not-evaluate: no *-results.json or results.json`, `exit=2`, because the stalled wave never wrote a results JSON (`seat-yield-r45.out`). It does work on a wave that completed: `.ufo/waves/round-44/w1 --expect-reports 65` → `seats=65 reports=65 missing=0`, `exit=0` (`seat-yield-r44.out`). So the one stall in the corpus is exactly the one the counter is blind to. | `tools/seat-yield.py` — present, runnable, and returns "could not evaluate" instead of "0 of 64" | `probe-wave-yield-fallback.py` (this seat): denominator from `dispatch.json` `taskCall.tasks[].name`, numerator from `out/<seat>.md` and `out/<seat>/<seat>.md`, no results JSON required. Shown able to fail and to pass: round-44 `seats=65 reports=65 missing=0 driver-log=9`, `exit=0`; round-45 `seats=64 reports=0 missing=64 driver-log=18`, `exit=1`; round-46 at 20:03:04Z `seats=65 reports=32 missing=33 driver-log=5`, `exit=1` (`wave-yield-r44.out`, `-r45.out`, `-r46.out`). |
| dead-pointer (this round's own live evidence) | All three b11906 receipts record `teardown.log_path` under `/fast/scratch/hyaku/kama-r46/X1Live/kama-llamacpp-live-*.log` — the seat scratch the operator directive deletes before the seat finishes. The receipts inline the 3-line tail (`teardown.log_lines`, `log_lines_truncated: false`), so the loss is bounded, but the recorded path will not resolve for a later reader. Same class as row 1, one level down. | none — the operator scratch directive (2026-10-25) is driver-side, and the live receipt schema has no field policing where a cited path lives | The same probe's log leg: a `log_path` pass requires the path to be in-tree or its basename copied beside the receipts. Shown able to fail: `log=fail:dead-pointer` for 3/3 b11906 receipts today (`durability-r46.out`), and `log=pass:copied-beside-receipt` on the in-tree fixture `out/S9Lesson/fixture-live/` (`durability-fixture.out`). Proposed lane fix: have `tools/kama-llamacpp-live.py` write the run log next to `--receipt-dir`, or record `log_path` only when it is in-tree. |
| stale-premise, undisclosed partial (round-45 lesson **row 5**) | The round-45 lesson says the four truncated files were "Restored from `21945c61` plus the appendix in `82b5e9d3`". The lane's own append-only audit at the round-46 base shows **2 of 5 events still `partial`**: `0718b6ab SCORECARD.md deleted=2417 restored_at_tip=2416` and `dd9f5dc6 SCORECARD.md deleted=31 restored_at_tip=24`. The 8 missing lines, re-derived here: the one `0718b6ab` line is the old depth head row (`SKILL.md` sha256 `91440eb8…`, 1420 lines), superseded by `82b5e9d3`'s `3046955b…` depth row; the seven `dd9f5dc6` lines are the six pre-round-42 head-axis rows (`**operability**`, `**freshness**`, `depth`, `coverage`, `calibration`, `adjacency`) plus the prose line "Reconciled in round 41 against the measured commit …", superseded by the round-42 head. Supersession, not loss — but the lesson never wrote that, and `partial` is what a later reader sees. | `tools/append-only-audit.py` reports `status=partial` (landed `4a2a4d55`, after the round-46 freeze); before it nothing distinguished "restored by a rewrite" from "lost" | `probe-append-partial.py` (this seat): every missing deleted line is classed `superseded` (its first-cell key, the axis name, exists at the audited revision with different text), `prose-dropped` (not a table row, no replacement owed) or `lost` (a table row whose key vanished). Shown both ways: at `0163fea2` → `partials=2 missing=8 superseded=7 prose-dropped=1 lost=0`, `exit=0` (`append-partial-base.out`); with one synthetic head row whose key is absent → `lost=1`, `exit=1` (`append-partial-injected.out`). |

### Sweep: routed items of the round-40..45 closures against the lesson corpus

The question the sweep answers: which items a closure routed to the lane were never turned into a lesson row. Command (this seat, read-only; script and full output in `out/S9Lesson/`):

```
python3 .ufo/waves/round-46/w1/out/S9Lesson/sweep-closures-vs-lessons.py > .ufo/waves/round-46/w1/out/S9Lesson/sweep.out
```

It extracts the `## … Routed defects` list of `corpus/lessons/round-{40..45}-verifier-spotcheck.md` (33 items), then probes only **later** files (`round-<m>.md`, `round-<m>-verifier-spotcheck.md`, m > source round) for (a) the item's label with its round (`r45-D1`, `round-45 … D1`) and (b) any backticked path/tool the item names. Tail of the output:

```
summary items=33 uncited_by_label=24 uncited_by_both=15
  bare: r40 D3 -- **D3 — correction sweep incomplete.** `corpus/lessons/round-38.md:67` 
  bare: r41 #1 -- C1's counter proves facts true, not relevant; strengthen the head-tabl
  bare: r42 #2 -- **Counters prove facts, not sufficiency (C1 relevance needles, C2 `con
  bare: r42 #3 -- **Restate the head's `verifier-spotcheck` count** (28 at the measured 
  bare: r42 #4 -- README names no hidden top-level entries (`.gitignore`, `.ufo`); eithe
  bare: r42 #5 -- Operator-owned and still open: the parked worktree `/home/vgpnk/Projec
  bare: r43 D4 -- **D4 (lane, evidence):** commit a tip-side `gate-registry-check.py --s
  bare: r43 #7 -- **Operator:** the parked worktree is now attached at the tip and clean
  bare: r44 #5 -- **Carried (lane):** counters prove facts, not sufficiency. K1Cheat and
  bare: r44 #6 -- **Operator:** L0 `kama | round-35` (MISSION.md axes pair), `kama | rou
  bare: r45 D1 -- **D1 (lane, calibration re-claim):** the 126-row ledger is now known d
  bare: r45 D2 -- **D2 (lane, freeze timestamp):** apply KQ64 at the round-46 freeze, an
  bare: r45 D3 -- **D3 (lane, evidence durability):** S485 and the S041/S046/S055 re-run
  bare: r45 #4 -- **Carried (lane):** still frontier: S013, S022, the floating-series ro
  bare: r45 #5 -- **Operator / driver:** the inline dispatcher stalled at 32/64 seats sp
```

Hand-read of the 15 bare rows (the sweep is a pointer, not a proof — a lesson may address the subject without citing the label):

| bare row | disposition found by hand | evidence |
|---|---|---|
| r40 D3 | **closed** — append-only pointer added to `round-38.md` | `corpus/lessons/round-41.md:117`; sweep false negative (it cites S474, not the label) |
| r41 #1, r42 #2, r43 #6, r44 #5, r45 #4 | **one family, never a lesson row** — "counters prove facts, not sufficiency", carried in four consecutive closures | no `## Mistakes` row in any round-40..45 lesson; `grep -c sufficiency .ufo/waves/round-46/preregistration.json` → `0`, so round 46 does not carry it either |
| r42 #3 | closed without a lesson row — the spot-check count was restated in `SCORECARD.md` (31) | round-45 closure §Claims, `SCORECARD.md:18` |
| r42 #4 | **closed** — `README.md:28` names `.gitignore` and `.ufo/` | `corpus/lessons/round-43-verifier-spotcheck.md:38` |
| r42 #5, r43 #7, r44 #6, r45 #5 | operator/driver items, still open by statement | round-45 closure §7.5 |
| r43 D4 | **closed** — tip-side `--selftest` receipt committed | `corpus/lessons/round-44.md:54`, `.ufo/waves/round-44/c1/gate-selftest-tip.out` |
| r45 D1, D2, D3 | dispositioned in the round-46 preregistration `routed` block (deferred / landed / landed-as-side-file) | `.ufo/waves/round-46/preregistration.json` `routed`; row 1 above for D3 |

Two findings the sweep yields that the closures did not state:

1. **The sufficiency family lost its carrier.** "Counters prove facts, not sufficiency" was routed in round 41 (#1), 42 (#2), 43 (#6), 44 (#5) and 45 (#4), never became a `## Mistakes` row, and is absent from the round-46 preregistration. The rounds do pay for it — round-45's C2 ledger is honest and still fails its own counter (KQ65), and round-44's K1Cheat/K2Cheat met both frozen counters with shortcuts — so the item is real, not stale. Proposed rule: a carried item that survives three closures without a lesson row must be either written as a row with a fail-capable check or dropped with a stated reason; carrying it a fourth time is the defect.
2. **Label-citation is not coverage.** Three of the 15 bare rows (r40 D3, r42 #4, r43 D4) are closed and their fix is cited in a later lesson, just not by label. Any future "routed items addressed" counter must read substance; this sweep's `bare` list over-reports by 3/15 (20%).

## Wave

`kama-r46-w1` (`.ufo/waves/round-46/w1/dispatch.json`: `{"spawn": 65, "resume": 0, "total": 65}`), L1 `KamaR46`. At draft time: `[FILL: lunch/scaffold line from `.ufo/state/inline-dispatcher.log`, wall-clock of the last seat]`, and the yield measured by `probe-wave-yield-fallback.py` at 2026-10-26T20:03:04Z: `seats=65 reports=32 missing=33 driver-log=5` (`out/S9Lesson/wave-yield-r46.out`) — a snapshot, not the wave's outcome. The round-45 wave's 64 seats produced 0 reports (round-45 closure N-D); the fallback probe now makes that visible (`reports=0 missing=64`, `exit=1`) where `tools/seat-yield.py` says `could-not-evaluate`, `exit=2`. `[FILL: which seats attacked C1 and C2, and what they found; a claim with no seat attack is written as unattacked, not as verified]`
