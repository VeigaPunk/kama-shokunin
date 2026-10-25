# Round 31 verifier spot-check (kama)

author: hyaku closure (non-author integrator, @m_kfc)
date: 2026-10-24
round: kama lane-round 31 (hyaku inline campaign; attempts 1-2 died without a report, attempt 3 landed)
report: .ufo/reports/round-31/kama.md (fleet commit eccc9b6c31a40e4b0c148f1681009632ebcce30d, author kama-shokunin)
lane before: f129e27b3b57a8fed7a34a8e6fe96d481e6c959d → after: c16fe3e5a1577c075668004d4b737a6b15061210

## Step-1 conformance

- Report committed by lane identity: `git log --format='%an %ae %H' -- .ufo/reports/round-31/kama.md` → `kama-shokunin kama@shokunin.local eccc9b6c31a40e4b0c148f1681009632ebcce30d`. PASS.
- `SHONEN` heading present with one line per box (`grep -c SHONEN` → 1 heading; four `[~]` boxes each with an evidence pointer). PASS.
- Lane commit ancestry: `git -C kama-shokunin merge-base --is-ancestor c16fe3e5a… master` → exit 0. PASS.
- Lane repo state: `jj-lane.sh state` → branch=master local=remote=c16fe3e5… ahead=0 behind=0, tracked=0 untracked=0; `git status --porcelain` empty. PASS. (Detached HEAD expected under jj colocation; branch ref used.)
- Prompt: .ufo/prompts/kama-round-31.md committed by kama-shokunin, carries the canonical round contract and hyaku addendum §6 (swarm 32-128, jj lane VCS, wave validation, claim sizing). PASS.
- Marker rule: report names three declared claims, evidence pointers, landed hashes, all required sections → real report, not a marker.
- Watchdog digest (verbatim, .ufo/watchdog.log, mutable): 2026-10-23T19:43:43 launch attempt=3 pgid=2386773; 19:47:47 lane-dead-no-report (invalidated dispatch: executor leaf role); 19:47:55 launch attempt=1 pgid=2411146; 19:57:07 lane-dead-no-report (orchestrator freeze, L1 never ran); 19:57:20 launch attempt=2 pgid=3679046; 20:17:39 lane-dead-no-report (second freeze); 20:17:51 launch attempt=3 pgid=1085203; 20:33:29 launch attempt=1 pgid=2229311; 2026-10-24T02:24:06 launch attempt=1 pgid=2686292; 02:44:11 complete kama round=31; hyaku-inline attempt=1. Complete line exists → terminal status ok.

## Per-claim re-check (committed evidence per PROTOCOL §Gate standard Closure consequence; lane-owned counters not executed by this seat)

### C1 — depth, frozen counter count-c1.py

- Counter integrity: `sha256sum .ufo/waves/round-31/count-c1.py` → `d86c4a94…9216`, byte-identical to freeze commit `0e6f8ed6891c09d5208ac1fdcb294ed9a842832e` (`git show 0e6f8ed6:… | cmp -` → identical). PASS.
- Receipt: `res/out/KamaR31a3.ResReRunC1/c1-tip.json` → `registered 18 counted 17 target 12 met True not-counted ['K31-10']`, tip f129e27b; JSON-sorted dump byte-identical to inherited `KamaR31a1b.ResReRunC1/c1-tip.json`. Matches report verbatim. PASS.
- Falsification evidence: `w2/out/CriticNoop/report.md` + receipts show an independently constructed twelve-duplicate-row no-op fixture also reads `registered 12 counted 12 target 12 met True` → the frozen counter cannot separate depth from a no-op. `w2/out/MutC1Pin/` shows pin mutants survive (counter verifies only sha256 fields read from the tip blob). Claim falsified as a depth improvement; lane reports met-on-counter, NOT admitted. RE-MEASURED (receipt bytes re-compared) + evidence-verified.

### C2 — calibration, frozen counter count-c2.py

- Counter integrity: sha256 `2d06f38d…c6fe`, byte-identical to freeze commit. PASS.
- Receipt: `res/out/KamaR31a3.ResReRunC2/c2-tip.json` → `rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0 unresolved 3 append_only True met False`. Matches report verbatim. PASS.
- Frozen predicate ("rows >= 28 and unresolved == 0 and false_corrections == 0 and append_only is True …") evaluates False (unresolved 3). Claim NOT met; lane reports counter defect (rounds 11-13 share the Claim cell `C1`; non-injective `(row, class)` key). Repair-arm evidence: `controls/RefRepair/receipt.txt` → reference repair also fails (`met False`, false_corrections 3); `w2/out/MutC2Key/` shows the key-collision mechanism. RE-MEASURED + evidence-verified.

### C3 — operability, gate-registry-check.py

- Receipt `c3/gate-after-final.out` → `registered 9 unregistered 0`, `exit=0`, measured at the round tip. PASS.
- Falsification evidence: `w2/out/ExecC3Control/report.md` — a registry row whose Name contains the tracked path but whose entry command/metadata point at a nonexistent file still flips the gate 8/1 exit 1 → 9/0 exit 0 (`04-nonexistent-path.log`, EXIT_CODE=0). Occurrence check, not a meaning check. Lane reports met-on-frozen-predicate, NOT admitted. Evidence-verified (committed receipts); the gate itself is lane-owned and was not executed by this seat.

No owned axis harmed: `git diff f129e27b c16fe3e5 --stat` is purely additive (SCORECARD +41, LOG +29, SOURCES +1, lesson +27, receipts/w3 specs under .ufo/waves/round-31/); scores held (operability 8, freshness 8, coverage 9, depth 7, adjacency 7, calibration 7); capability table untouched.

## Per-axis verdicts

| axis | verdict | basis |
|---|---|---|
| depth | unchanged | C1 7 → 7; met on frozen counter but no-op control also meets it — not admitted, defect routed to round 32 |
| calibration | unchanged | C2 7 → 7; predicate False (unresolved 3), counter defect routed |
| operability | unchanged | C3 8 → 8; met on frozen predicate but occurrence-only check exposed, routed |

## Discernment spot-check (LEARNING.md — checked from outside)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S180 admit | admit | `.ufo/waves/round-31/sources/llama.cpp-704366d/server-common.cpp:1360` | agree | `throw std::runtime_error("Cannot use both json_schema and grammar");` verbatim at line 1360 |
| S190 admit | admit | same snapshot `server-schema.cpp:47` | agree | `->add_alias("max_tokens")` verbatim at line 47; S191 line 64 likewise |
| S180-S191 (10 out of 12 sampled at their Gate lines: 1360/1375/1390/1395/1399/1411/1517/1519/1521/1530 + schema 47/64) | admit | pinned snapshot | agree | all 12 quote cells verbatim at their recorded lines; snapshot sha-pinned per SNAPSHOT.json |
| S192 admit (new row this attempt) | admit | https://developers.openai.com/api/reference/resources/chat/index.md (fetched 2026-10-24 by this seat) | agree | located quote present verbatim at the `response_format` body parameter (fetched md lines 1010-1012; lesson cites line 1008 — content moved by ~2 lines between fetches, quote itself exact); 18 words ≤ 25; tier A scoped |
| CtlTypeGuess 12 guessed rows | reject (lane) | `w1/out/CtlTypeGuess/` — not re-executable at closure (scratch fixture gone) | agree (on record) | rejections of candidate evidence recorded with the counted 1/12 receipt; control-class rejections, mechanism consistent with C1's falsified no-op class |
| RevCounterFair F3 fixture (`reject-message-not-adapter`) | reject (lane) | `w1/out/RevCounterFair/f3-receipt.json` | agree | receipt shows F3R `counted: false, reasons: ["reject-message-not-adapter"]`, `live: {}` — schema-bounds text correctly refused pre-live; full bounds string absent from the adapter snapshot (grep zero matches) |

Census: `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → exit 0, `ok kama-shokunin/corpus/SOURCES.md`, 192 `| S` rows (191 → 192 as reported; end receipt `census-end-attempt3.out` matches live output).

## Trend verdicts

- expansion — improved: S192 row committed and re-opened with a verbatim located quote; census 191 → 192 exit 0; chat-adapter surface 18 measured rows committed; wave-3 frontier scout items prepared (spec committed, validator receipts in w3/).
- quality — improved: attempt-2 corrections (six probe-falsified `meaning` cells, 404 snapshot body and duplicate snapshots removed `a9181096`, README/PROVINCE drift fixed) committed; attempt-3 re-execution byte-stable across three sessions (C1 receipts identical; C2 identical). No admitted entry failed re-check.
- discernment — improved: all three shortcut controls (no-op registry 12/12; non-injective C2 key; occurrence-only C3 gate) were found by the waves before any admission; all three claims reported not-admitted with defects routed, not prettified; mistake 9 mines the second uncommitted-receipt recurrence with an enforced fix.

## Routed defects for round 32 (lane-owned, per report's own plan)

1. C1 counter eligibility: counted row must name a parameter/value the base request does not already carry; `ignored` class excludes session-consumed keys (response_format/json_object case demonstrated by RevCounterFair F1).
2. C2 counter: round-qualified correction key with declared uniqueness precondition (candidate `w2/out/MutC2Key/counter-roundkey.py`).
3. C3 gate: occurrence check passes rows with empty exit maps and nonexistent metadata paths — grade meaning, not presence.
4. KQ42 probe gating of `meaning` cells; pin declared `bytes` and refuse working-tree pin edits (MutC1Pin).
5. New this closure: SCORECARD/report cite `w2/out/RefRepair/` — the receipt actually lives at `.ufo/waves/round-31/controls/RefRepair/receipt.txt` (pointer drift; status-neutral, fix in round-32 append).
6. New this closure: report's wave-2 seat count says 44 returned reports; `find w2/out -maxdepth 1 -type d | wc -l` → 43 seat dirs (one seat's output not present as its own directory; dead-seat claim "none recorded" unverifiable for that seat). Lane to reconcile the w2 registry against w2/out next round.

## Verdict

Rejected as admission (no claim verifies as landed improvement; the round's value is the falsification record, the frontier row, and the prepared repair wave), honest stop: no axis harmed, defects routed, evidence byte-stable. Round status ok; admitted false; verdict rejected-honest-stop.
