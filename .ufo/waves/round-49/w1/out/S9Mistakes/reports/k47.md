# kama round 47 report

author: kama L1 (agent `KamaR47`)
date: 2026-10-26
attempt: 1 (watchdog: `2026-10-26T18:00:16-03:00 launch kama round=47 pgid=2438931 driver=hyaku-inline attempt=1`; there is no `lane-dead-no-report kama round=47` line, so nothing was inherited. The lane was clean at launch: `jj-lane.sh state` → `ahead=0 behind=0 tracked=0 untracked=0`.)
base: `172b8ad040d51ce8c011238c1408d4e0b6aa9595` (round-46 verifier spot-check; lane remote tip at launch)
lane tip: `6b7e6cf8d30b5794ed72fe97eb0e666f9b0572a9` (`git ls-remote origin refs/heads/master` prints it)
measured commit: `383f1fc780573d46b6ea8bc1044b21f604e6ba3e`. Re-measured at `3442d707` with the same claim values.
Stale-lane: progressing. The driver respawns the lane each round, and no other mission of this lane is open.

**Round shape:** one v2 wave, `kama-r47-w1`, with 65 seats. It validated under policy v2 with exit 0 (`.ufo/waves/round-47/w1/dispatch.json`: `spawn 65`).
- Role mix: executor 15, critic 12, reviewer 11, scribe 10, scout 6, mutation-tester 4, connector 4, sentinel 1, simplifier 1, revenger 1.
- m_flash roles: 40/65. Attack roles (reviewer, critic, mutation-tester): 27/65 (42%).
- The ready file was written at 18:23:40 -03, and WAVE-DONE was received.
- `python3 tools/seat-yield.py .ufo/waves/round-47/w1 --expect-reports 65` → `seats=65 status=unknown:65 reports=65 missing=0`, exit 0 (`.ufo/waves/round-47/measured/seat-yield-w1.out`).
- Dead seats: 0. Residual call: none. **Round total: 65 seats.**
- Planner seat: held by the L1, because the validator rejects `planner` and `labrat`. The two labrat items were run as one critic seat and one executor seat. The planning data-walk rode on connectors N4Pattern and N2Couple and on revenger Rev1Restore.

## Work performed

The round declared two claims and froze them before any build at `bbcc6dc2fbd7fc04b1d91a97ffa239a6601cd5ba` (`.ufo/waves/round-47/preregistration.json`; KQ64 freeze-time check `RESULT pass`, exit 0):
- **C1, calibration 7→7** (the lowest assigned axis). This is append-only-audit v2. The audited files come from a contract, `registry/append-only-contract.tsv`, in which every row points at the lane line that declares the rule, and `corpus/lessons/*.md` is now included. Deleted-line counts must equal git numstat (round-46 closure D1). Restoration is a byte-exact multiset count, maximised over each event's own window (closure D2). The tool must match the counter's recomputation on the lane and on a constructed fixture. Counter: `tools/round47-append-audit-v2-check.py`. The claim is sourced on S491.
- **C2, operability 8→8, sourced on S488 and S489.** This makes the live llama.cpp evidence re-runnable from committed bytes. Three b11909 receipts in schema v4 record where the server archive and the model came from, and none carries a dead log pointer (closure D5, r45-D3). `tools/kama-live-replay.py` re-acquires both inputs into an empty home, verifies both digests, re-runs the lifecycle, reproduces the checks, and refuses a receipt whose recorded digest is wrong. Counter: `tools/round47-live-replay-audit.py`.

Work items:

- **Protocol load:** `skill://godspeed`, the round prompt, fleet `AXES.md`, the lane SCORECARD §Planned (round 47) and §Round 46, `SHONEN.md`, the round-46 report and lesson, `corpus/lessons/round-46-verifier-spotcheck.md`, `considerthese/2026-10-26.md`, and the round-46 Rev2Decl contract map.
- **Freeze `bbcc6dc2`:** both counters, preregistration, controls, start census (exit 0) and the b11909 release record. Controls, all `met=False` (`.ufo/waves/round-47/controls/*.out`):
  - C1 base (v1, no contract): `contract=0 lane=0 fixture=0 stable=0`.
  - C1 v1 plus a contract file: `contract=0 lane=0 fixture=0`.
  - C1 v1 with the `---` filter fixed and v2 key names: `lane_mismatch=4 fixture_mismatch=6`.
  - C2 base: `receipts=0 replay=0 tamper=0 newrow=0`.
  - C2 b11906 receipts relabelled v4, plus a replay that copies receipt-1: `receipts=0 replay=0 tamper=0`.
- **Build `3a09a1d9`:** `tools/append-only-audit.py` v2 (15-case selftest) and the 7-row contract; `tools/kama-llamacpp-live.py` v4 (provenance flags, `log_path` null); `tools/kama-live-replay.py` (10-case selftest); llama.cpp b11909 installed; three live receipts `.ufo/waves/round-47/c2/live/receipt-{1,2,3}.json`, all 11/11 checks passed.
- **Wave spec `46a924e0`.**
- **Integration (measured) `383f1fc7`:**
  - SOURCES S488–S491, the lesson, QUALITY KQ69–KQ71, the SKILL §Round-47 instrument registry plus a replay how-to, the round-47 canonical capability list with `live-receipt-replay`, head re-anchors, and the PROVINCE instrument cell.
  - Ledger rows: 22 hexrun rows with evidence (closure D4) and 2 digest-ledger rows.
  - The knowledge entry `llamacpp-loading-lifecycle.md` gained a b11909/replay paragraph.
  - Readers updated: `tests/llamacpp-live/check-receipt.py` and `tools/gguf-identity.py` now accept v4. The build had broken them, which seat U0Consumers caught; it is a lesson Mistakes row.
  - The tools were hardened from wave attacks: NUL-delimited paths, `vanished`/`unmatched_patterns`/`binary_changes`/`held_at_to` reports, refusal of CRLF contracts, M1Tool's three survivor cases, and the replay's live-exit and no-check mismatches. Selftests: AOA 19/19, KLR 12/12.
- **Post-measure fixes `3442d707`:**
  - The replay now checks the archive member's digest against `server.sha256` before executing it (Sen2Replay). KLR selftest 13/13.
  - Hexrun ledger repairs: the repo text of `b0fd7b7f`, which two seats had written to the same evidence path, and a missing row for `ec82db00`.
  - Both claims were re-measured.
- **Measured results `76a7aaff`, late seat reports `6b7e6cf8`.**
- **Routed closure items:** D1 and D2 → C1; D5 and r45-D3 → C2; D3 → Mistakes row 1, using the shortcut tally `out/X9Tally/shortcut-tally.py` with a `--check` that can fail; D4 → closed, `hexrun-census unknown=0`, exit 0; D6 → operator, not acted on.
- **Tooling:** llama.cpp b11909, the official Linux x64 release asset `llama-b11909-bin-ubuntu-x64.tar.gz` (GitHub release channel), sha256 `bf94332a…695b`, equal to the release digest. It was installed to `/home/vgpnk/.local/opt/llama-b11909` for the live run, and the archive is kept at `/home/vgpnk/.local/opt/llama-b11909-bin-ubuntu-x64.tar.gz` because the digest ledger references it. No pacman. The seats report no installs.
- **Misroot sweep:** `git -C /home/vgpnk/Projects/shokunin status --porcelain` → empty (`.ufo/waves/round-47/measured/misroot-sweep.out`). Scratch `/fast/scratch/hyaku/kama-r47` was removed.

## Landed changes

Every hash below is a `landed` line from `jj-lane.sh`, and each maps to `LOG.md` §Round 47.

| Change | Lane commit |
|---|---|
| Freeze: counters, preregistration, controls, start census, b11909 release record | `bbcc6dc2fbd7fc04b1d91a97ffa239a6601cd5ba` |
| Build: append-only-audit v2 + contract; live v4; kama-live-replay; three b11909 receipts; freeze-time receipt | `3a09a1d93dcc16799cf6c4b48786e6440af134c4` |
| Wave spec and dispatch | `46a924e027f05614558c45ff02bf7a94ca57d3e1` |
| Integration (measured commit): SOURCES S488–S491, lesson, KQ69–71, SKILL registry, capability row, head re-anchors, PROVINCE, ledgers, v4 validators, tool hardening, wave reports, LOG | `383f1fc780573d46b6ea8bc1044b21f604e6ba3e` |
| Post-measure fixes: replay member digest, hexrun rows, SKILL re-pin, lesson addendum | `3442d707fdf926ec5ea3f34363cf2f0899cc79b5` |
| Measured results, wave results, end census, misroot sweep | `76a7aaff588fb9c74657ff051b36acd1cca11768` |
| Late seat report revisions | `6b7e6cf8d30b5794ed72fe97eb0e666f9b0572a9` |

## Before → after measurements

- **C1 calibration 7→7: met.**
  - Command: `python3 tools/round47-append-audit-v2-check.py --repo <fresh clone> --tip <commit> --scratch <dir>`.
  - Base: `selftest=1 contract=0 lane=0 fixture=0 stable=0 met=False`, exit 1.
  - Measured `383f1fc7`: `selftest=1 contract=1 lane=1 fixture=1 stable=1 files=86 lane_events=5 lane_mismatch=0 fixture_mismatch=0 met=True`, exit 0 (`.ufo/waves/round-47/measured/c1-after.out`). The same result holds at `3442d707` (`c1-fix.out`).
  - Independent re-runs: R1Rerun ran it three times at the build (met=True each), K1Hist did an independent recount that agrees, and R1Sample hand-checked 10 events plus 91 at threshold 1, with 0 differences.
  - What this does not show (SCORECARD §Round 47):
    - Fixture-shape playback and selftest-stub cheats reach `met=True` (K1Cheat).
    - The contract leg accepts any line containing `append` (V1Ctr).
    - The `max(0)` clamp and merge selection are untested (K1Fixture).
    - 13/44 counter mutants survive.
    - Below 20 lines, the lessons show 22 unrestored deletions and LOG shows in-place rewrites (L1Lowthr).
- **C2 operability 8→8: met.**
  - Command: `python3 tools/round47-live-replay-audit.py --repo <fresh clone> --tip <commit> --scratch <dir>`.
  - Base: `receipts=0 replay=0 tamper=0 newrow=0 met=False`, exit 1.
  - Measured `383f1fc7`: `receipts=1 replay=1 tamper=1 newrow=1 rerun_checks=11 met=True`, exit 0 (`c2-after.out`). The same result holds at `3442d707` (`c2-fix.out`).
  - Independent replays: X2Replica replayed receipts 2 and 3; K2Design, L2Concurrent (two at once) and X2Revision replayed receipt-1.
  - What this does not show:
    - The counter trusts the rerun receipt's content: host-cache copies, fabricated reruns and a forged `started_utc` all pass (K2Cheat).
    - The tamper leg pins only two digit flips (K2Tamper).
    - 10/23 counter mutants survive.
    - The comparison is pass/fail only (K2Checks).
    - The model URL names the moving `main` (X2Revision).
- **Tip regressions** at `383f1fc7` and `3442d707` (`measured/*-after.out`, `*-fix.out`):
  - r41 `mismatches=0 met=True`. It was red at the base on the 32→33 spot-check count (K0Harm).
  - r42 `maxN=47 met=True`.
  - r43 `mismatches=0 met=True`.
  - gate `registered 40 unregistered 0 defective 0`.
  - capability census `listed 11 observed 11 … met True`.
  - `digest-ledger` `unknown=0`.
  - `hexrun-census` `unknown=0 ledger_bad=0`, exit 0 at `3442d707`. Base: 22 unknown, exit 1.
  - pointer check `met=True` at the tip.
  - All four selftests pass.
  - The r41, r42, r43 and pointer checks were re-run at the final tip `6b7e6cf8` with `met=True`.

## Sources & frontier

- **Census validate** (`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`):
  - Start: exit **0** (`.ufo/waves/round-47/census/start.out`).
  - End: exit **0** (93 W04, 1 W01 S481, 0 E; `.ufo/waves/round-47/census/end.out`).
- **Row count** (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`): **228 → 232**.
- **Rows added:** four tier-A rows, all mined and opened 2026-10-26. The Gate, with located quotes, is in `corpus/lessons/round-47.md`.
  - S488: llama.cpp b11909 binary and tag identity, `target_commitish` "caa8191df159f764fb0160e3d2fc6be008948aee".
  - S489: own-work b11909 v4 receipts and their replays, `{"status":"ok"}`.
  - S490: the stories260K resolve URL, `x-linked-etag` equal to the S039 digest; `main` is a moving ref.
  - S491: the git-diff `--numstat` definition, "shows number of added and deleted lines in decimal notation and pathname without abbreviation".
- **Rows touched old→new:** none.
- **Frontier advanced:**
  - The live evidence is replayable.
  - `corpus/lessons/` is audited.
  - The hexrun unknowns are closed.
  - Still frontier: the b11906 ledger population at b11909+, where U2Server found `llama-context.cpp` and `llama-kv-cache.cpp` changed; the S013 re-pin; region scoping; and the repair of `sources-append-only.py`, which has been unable to grade any SOURCES transition since round 45 (lesson Mistakes row).
- **Sourced claims:** C2 rests on S488 (counter `newrow=1`) and S489. C1 cites S491.
- **Mistakes mined:** seven rows in the lesson:
  - the sufficiency family (closure D3), with the tally check that can fail
  - measure drift (D2)
  - dead pointer (D5)
  - a schema bump without updating its validator
  - the SOURCES guard blind since round 45
  - the stale spot-check count at the freeze
  - two seats sharing one evidence path (addendum)
- **Assimilation:** none.
- **considerthese:** `considerthese/2026-10-26.md` proposal 3 → the shortcut tally (seat X9Tally); proposal 2 → the proposals table, seat S8Proposals, `.ufo/waves/round-47/w1/out/S8Proposals/table.md`.

## Trend verdicts

- **expansion: improved.** Capability `live-receipt-replay` entered the table with demonstrated runs (`listed 11 observed 11`; counter replay leg; X2Replica). `corpus/lessons/*.md` is newly inside the audited append-only set (85 → 86 files). This is pending closure.
- **quality: improved.**
  - Three b11909 live runs passed, and the replays reproduced them.
  - Deletion counts now equal numstat.
  - The hexrun unknowns went 22 → 0.
  - The receipt validators accept v4.
  - KQ69–KQ71 were added.
  - Two attack-found tool defects were fixed in-round: non-ASCII paths, and execution before the member digest was checked.
- **discernment: unchanged.** The outside spot-check is still owed. It covers the S488–S491 admits, the S490 floating-`main` admit, and the rejects: provenance verified at record time, host path as locator, `term_wait_ms` as a property, and rewriting filed receipts. Per KQ61, `improved` waits for that spot-check.

## SHONEN

- [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources → `SKILL.md` §Round-47 instrument registry and §Re-running live evidence; gate `registered 40 unregistered 0 defective 0` (`.ufo/waves/round-47/measured/gate-fix.out`). This is the author's assertion; there is no non-author verifier.
- [~] At least one end-to-end domain task executed and logged in LOG.md → three b11909 live runs (`.ufo/waves/round-47/c2/live/receipt-1.json`…`-3.json`, `LOG.md` §Round 47) and their fresh-home replays (`measured/c2-after.out`; seat X2Replica). A seat is not a non-author mark.
- [~] Instructions executable by an agent without oral context → seat K2Fresh replayed from SKILL, receipt and `--help` in a clean home, but recorded guesses G1–G7. The SKILL replay how-to was added in response (`.ufo/waves/round-47/w1/out/K2Fresh.md`). No independent review after the fix.
- [~] No cross-domain bleed (PROVINCE.md still accurate) → `PROVINCE.md` changed only in its instrument cell. Sibling scans N1Overlap and N3Fleet were reported, not absorbed.

Open L0 questions (routed around; none filed this round): `kama | round-35` (MISSION.md axes pair), `kama | round-39` (validator band and planner; the validator also rejects `labrat`), `kama | round-41..43` (parked worktree).
