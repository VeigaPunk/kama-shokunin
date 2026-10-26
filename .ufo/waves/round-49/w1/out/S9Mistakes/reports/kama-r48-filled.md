# kama round 48 report

author: kama L1 (agent `KamaR48`)
date: 2026-10-26
attempt: 1 (watchdog: `2026-10-26T19:05:04-03:00 launch kama round=48 pgid=3968099 driver=hyaku-inline attempt=1`; no `lane-dead-no-report kama round=48` line, so nothing was inherited; the lane was clean at launch: `jj-lane.sh state` → `ahead=0 behind=0 tracked=0 untracked=0`)
base: `33e005827742b29772b153cda036ec9f27f653be` (round-47 verifier spot-check; lane remote tip at launch)
lane tip: `4d8334af1c45bce74fa6a3904a7f6aa3a1ec630e` (`git ls-remote origin refs/heads/master` prints it; `jj-lane.sh state` → `ahead=0 behind=0 tracked=0 untracked=0`)
measured commit: `c4b2175d2ff9466beaed039dc8330176362e7d82`; re-measured at `1541a0dd1628225b838235fe2b7b3d69ad8f50de` with the same claim values (`.ufo/waves/round-48/measured/*-final.out`, each carrying `tip=1541a0dd…`).
Stale-lane: progressing. The driver respawns the lane each round; no other mission of this lane is open.

**Round shape:** one v2 wave, `kama-r48-w1`, 69 seats, validated under policy v2 with exit 0 (`.ufo/waves/round-48/w1/dispatch.json`).
- Role mix: critic 16, reviewer 13, executor 12, scribe 11, scout 5, mutation-tester 5, connector 4, simplifier 1, revenger 1, sentinel 1.
- m_flash roles (executor, scribe, critic, simplifier, revenger, sentinel): 42/69 (61%). Attack roles (reviewer, critic, mutation-tester): 34/69 (49%).
- Ready file written 2026-10-26T22:32:39Z; marker `w1.ready.dispatched` present. WAVE-DONE received ("all 69 seats settled"; `.ufo/waves/round-48/w1/w1-results.json`).
- Reports: `python3 tools/seat-yield.py .ufo/waves/round-48/w1 --expect-reports 69` → `seats=69 status=unknown:69 reports=69 missing=0`, exit 0 (`.ufo/waves/round-48/measured/seat-yield-w1.out`).
- Dead seats: 0. Seat K1Hist yielded "Blocked" (its own recount did not implement the definitions); no finding is taken from it. Seat Sen2Live landed after the measured commit: one **High** availability finding — `verify_archive_member()` in `tools/kama-llamacpp-live.py` hashes an archive member of any declared size, so a 104-byte crafted archive makes record time hash ~10^15 bytes before the server starts (a DoS on an operator-supplied archive, no escape); routed to round 49 (member-size cap), not fixed this round. Residual call: none. **Round total: 69 seats.**
- Planner seat: held by the L1 (the validator rejects `planner` and `labrat`); the planning data-walk rode on revenger Rev1Head and connectors N4Pattern and N5Mistakes.

## Work performed

Two claims, frozen before any build at `12284ba39fb1b46b43d43ee82423bebe08c700dc` (`.ufo/waves/round-48/preregistration.json`; KQ64 check `.ufo/waves/round-48/freeze/prereg-time-check.out` → `RESULT pass`, exit 0):
- **C1, calibration 7→7** (the lowest assigned axis): append-only-audit v3 — the lane's declared append-only rule graded as declared, carve-outs included: a `region` cell in `registry/append-only-contract.tsv` (SCORECARD's five re-derived head sections `exempt=`, the consumer-registry `## Errata` region `only=`), declarations that must bind, `regressed` in the exit code (round-47 closure D5). Counter `tools/round48-append-audit-v3-check.py`.
- **C2, operability 8→8, sourced on S492 and S493:** v5 live receipts with record-time-verified provenance and a model pinned to Hugging Face revision `499bc882…`; replay of all three receipts with a stable-projection comparison and `--compare`; a counter that hashes the re-acquired files itself and refuses swapped URLs (closure D1–D4, D6). Counter `tools/round48-live-replay-v5-audit.py`.

Work items:
- **Protocol load:** `skill://godspeed`, `skill://swarm`, the round prompt, lane SCORECARD (§Planned round 48, §Round 47), the round-47 report and lesson, `corpus/lessons/round-47-verifier-spotcheck.md` (D1–D9), `considerthese/2026-10-26.md`, the round-47 wave reports Rev1Restore, K1Design, K2Design, K2Checks, X2Revision.
- **Source opening:** the pinned HF resolve URL and revision API (`.ufo/waves/round-48/c2/hf-revision-499bc882.txt`) and the huggingface_hub download guide (`.ufo/waves/round-48/c2/hf-hub-download-doc.txt`), both committed at the freeze.
- **Freeze `12284ba3`:** both counters, preregistration, controls (all `met=False`, `.ufo/waves/round-48/controls/*.out`): C1 base `selftest=0 contract=0 lane=0 fixture=0 stable=0`; C1 `junk-c1-v2-relabel` and `junk-c1-drop-scorecard` `met=False`; C2 base all legs 0; C2 `junk-c2-r47-relabel` `receipts=1` (fabricated receipts pass the structural leg) with every other leg 0. A first control run showed C2's `newrow` leg met at the base (S039 already names the commit); the leg was tightened to the full pinned URL before freezing (control receipts re-run, all `newrow=0`).
- **Build `380bcdff`:** `tools/append-only-audit.py` v3 and the v3 contract; `tools/kama-llamacpp-live.py` v5 (record-time archive/member verification, pinned model URL); `tools/kama-live-replay.py` (v4+v5, stable projection, `--compare`); three v5 b11909 receipts `.ufo/waves/round-48/c2/live/receipt-{1,2,3}.json` (11/11 checks each); SOURCES S492–S493. Build finding: v3 at the base reported `regressed=1` — the round-45 SCORECARD authority banner had been rewritten in place by rounds 46–47 without being kept, although line 6 promises it; the build appended the r45/r46 banners byte-exact (lesson Mistakes row 1).
- **Wave spec `b85783e8`.**
- **Integration (measured) `c4b2175d`:** wave findings folded in; replay hardening (seats V2Replay F1–F4/F7/F11, K2Selftest: https-only, malformed receipts refused, `--compare` validates provenance, verified digests checked, v5 rerun must carry the same commit and verified digests; `KLR_SELFTEST pass=22`); v5 support in `tests/llamacpp-live/check-receipt.py` and `tools/gguf-identity.py` (seat K0Harm F2/F3 — the build had broken them); `tools/sources-append-only.py` repaired (seat X9SourcesGuard; closure D8; 45/45 selftest, r45→r48 transitions graded); `tools/shortcut-tally.py` promoted (seat X9Tally; considerthese proposal 3); contract: lessons row re-anchored to `corpus/QUALITY.md:143` (K1Binding), `corpus/knowledge/error-is-not-a-verdict.md` `only=## Round24` added (K1Contract); r42/r43/r44 banners appended byte-exact (X1Banner) and the r47 banner when line 6 was re-derived; selftest case `preamble-graded` (X1SelftestPower; `AOA_SELFTEST pass=28`); hexrun ledger row `d0012618` (X4Hex); SKILL §Round-48 instrument registry; KQ72–KQ75; README frontier; LOG; lesson; knowledge paragraph; capability rows reworded; PROVINCE instrument cell; head re-anchors.
- **Measured results `1541a0dd`** (also fixes the head §Planned pointer to round 49 — the round-42 counter wanted it); **final-tip receipts `f5c60787`**.
- **Routed closure items:** D1–D4, D6 → C2; D5 → C1; D7 → disclosed limit and round-49 plan; D8 → fixed (frontier, no claim); D9 → lesson Mistakes row 2, and this round's regression receipts carry their `tip=` line and were re-run at `1541a0dd`.
- **Tooling:** no installs; the round-47 llama.cpp b11909 install and archive were reused. No pacman. Seats reported no installs.
- **Misroot sweep:** `git -C /home/vgpnk/Projects/shokunin status --porcelain` → empty before the report (`.ufo/waves/round-48/measured/misroot-sweep.out`). At report time three untracked fleet-root files appeared, `=1239`, `=3900` (text "tracked-all siblings SKILL.md: near tsukuroi") and an empty `T`, written 19:55–19:56 -03; none names kama or round 48, so they are not attributed to this lane's seats and were left untouched. Scratch `/fast/scratch/hyaku/kama-r48` removed.

## Landed changes

Every hash is a `landed` line from `jj-lane.sh`; each maps to `LOG.md` §Round 48.

| Change | Lane commit |
|---|---|
| Freeze: counters, preregistration, controls, start census, HF revision record | `12284ba39fb1b46b43d43ee82423bebe08c700dc` |
| Build: v3 tool + contract, banner append, live v5, replay v5, three v5 receipts, S492–S493 | `380bcdff9c8af06997c482f6eb03db926a794a2b` |
| Wave spec and dispatch | `b85783e889c261ff870da65d091ff1014ffe7c10` |
| Integration (measured commit) | `c4b2175d2ff9466beaed039dc8330176362e7d82` |
| Measured results, head Planned pointer, measured receipts | `1541a0dd1628225b838235fe2b7b3d69ad8f50de` |
| Final-tip receipts, end census, misroot sweep, late seat reports | `f5c607875cdd9a4e057dfc893db6a6af2216a7b1` |
| Wave results, seat yield, late Sen2Live report | `4d8334af1c45bce74fa6a3904a7f6aa3a1ec630e` |

## Before → after measurements

- **C1 calibration 7→7: met.** Command: `python3 tools/round48-append-audit-v3-check.py --repo <fresh clone> --tip <commit> --scratch <dir>`.
  - Base `33e00582`: `selftest=0 contract=0 lane=0 fixture=0 stable=0 rows=0 files=0 … met=False`, exit 1 (`controls/base.c1.out`). The v2 tool at the base reports 2 partial events and `regressed=1`.
  - Measured `c4b2175d`: `selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=10 files=91 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True`, exit 0 (`measured/c1-after.out`); same at `1541a0dd` (`c1-final.out`). Independent: R1Rerun (2× met at the build, base met=False), N2Couple (C1 alone on the freeze).
  - Not shown (SCORECARD §Round 48): content-blind exemption (K1Regions, latent on the lane), substring/self-declaration binding (K1Binding), a copied recompute meets the counter (K1Cheat), five unexercised clauses (K1Fixture), 21/52 counter and 15/55 tool mutants survive (M1Ctr, M1Tool), sub-20-line losses unwatched (L1Lowthr: one real `LOG.md` loss at `ed135b3c`).
- **C2 operability 8→8: met.** Command: `python3 tools/round48-live-replay-v5-audit.py --repo <fresh clone> --tip <commit> --scratch <dir>`.
  - Base: `receipts=0 recordcheck=0 replay=0 compare=0 tamper=0 urlswap=0 newrow=0 replayed=0/3 met=False`, exit 1.
  - Measured `c4b2175d`: `receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True`, exit 0 (`measured/c2-after.out`); same at `1541a0dd` (`c2-final.out`). Independent: R2Rerun, X2Replica (3/3 plus a v4 replay), L2Concurrent (24 concurrent replays clean), R2Provenance (all provenance values match upstream).
  - Not shown: a replay that never runs a server meets the counter (K2Cheat, K2Urlswap) — `replayed=3/3` proves re-acquirable inputs and comparison, not execution; record time never fetches the URLs (K2Record); projection blind spots (K2Design, K2Projection); 6/27 counter mutants survive (M2Ctr).
- **Tip regressions at `1541a0dd`** (`measured/*-final.out`): gate `registered 42 unregistered 0 defective 0`; capability census `listed 11 observed 11 met True`; r41 `mismatches=0 met=True`; r42 `mismatches=0 maxN=48 met=True`; r43 `mismatches=0 met=True`; pointer `met=True`; `hexrun-census unknown=0`; `digest-ledger unknown=0`; `append-only-audit` exit 0. At `c4b2175d` (`measured/*.out`): `sources-append-only.py --from 33e00582` exit 0; selftests AOA 28/28, KLR 22/22, check-receipt 16 VALID/107 rejected, live ok; round-47 C2 counter `met=True`. The round-47 C1 counter now fails by construction (v2 contract format superseded; seat X2V4Compat).

## Sources & frontier

- **Census validate** (`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`): start exit **0** (`.ufo/waves/round-48/census/start.out`); end exit **0** (93 W04, 0 E; `.ufo/waves/round-48/census/end.out`).
- **Row count** (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`): **232 → 234**.
- **Rows added:** two tier-A rows, mined, opened 2026-10-26 (Gate in `corpus/lessons/round-48.md`): S492 (pinned HF revision resolve URL; quote `x-repo-commit: 499bc8821c6b12b4e53c5bffcb21ec206f212d81`), S493 (huggingface_hub guide; "When using the commit hash, it must be the full-length hash instead of a 7-character commit hash.").
- **Rows touched old→new:** none (S490 stays as filed).
- **Frontier advanced:** append-only rule audited with bound regions; the SOURCES guard grades again (blind since round 45); live evidence pinned to a model revision and verified at record time; shortcut tally is a lane tool. Still frontier: execution witness for replays, content-aware exemption, sub-20 deletions, b11906 ledger population at b11909+, prerelease cliff (D7).
- **Sourced claim:** C2 rests on S492 (counter `newrow=1` requires the pinned URL row) and S493.
- **Mistakes mined:** five rows in the lesson (banner rewritten without keeping; D9 receipt-tip precision; counter trusted evidence (D1); routed items dropped without capture (N5Mistakes sweep); schema bump broke the lane's own readers again).
- **Assimilation:** none (both claims work the lane's own instruments and evidence).
- **considerthese:** `considerthese/2026-10-26.md` proposal 3 → `tools/shortcut-tally.py` (seat X9Tally); proposal 4 (pin gap) → seat U2Pins report `.ufo/waves/round-48/w1/out/U2Pins.md`; proposals table updated by seat S8Considerthese.

## Trend verdicts

- **expansion: unchanged.** No capability entered (11 → 11; two rows reworded). New ground is instrument depth (regions, record-time provenance), not new surface.
- **quality: improved.** v3 found and the round repaired five lost SCORECARD banners (r42–r46); the SOURCES guard grades again; v5 receipts readers fixed; replay hardened against six wave findings; KQ72–KQ75; regressions green at the final tip.
- **discernment: unchanged.** The outside spot-check of the S492/S493 admits and the Gate rejects (x-linked-etag as revision proof, CDN redirect as locator, relabelled-tool/dropped-row evidence) is still owed; per KQ61, `improved` waits for it.

## SHONEN

- [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources → `SKILL.md` §Round-48 instrument registry and §Re-running live evidence (v5); gate `registered 42 unregistered 0 defective 0` (`.ufo/waves/round-48/measured/gate-final.out`). Author assertion; no non-author verifier.
- [~] At least one end-to-end domain task executed and logged in LOG.md → three v5 b11909 live runs (`.ufo/waves/round-48/c2/live/receipt-1.json`…`-3.json`, `LOG.md` §Round 48) and their counter replays (`measured/c2-final.out`); seats X2Replica and L2Concurrent replayed them. A seat is not a non-author mark.
- [~] Instructions executable by an agent without oral context → seat K2Fresh re-ran and recorded a v5 receipt from SKILL and `--help` (`.ufo/waves/round-48/w1/out/K2Fresh.md`); SKILL v5 how-to added. No independent review after the fix.
- [~] No cross-domain bleed (PROVINCE.md still accurate) → `PROVINCE.md` changed only in its instrument cell; sibling scan N1Overlap reported, not absorbed.

Open L0 questions (routed around; none filed this round): `kama | round-35` (MISSION.md axes pair), `kama | round-39` (validator band and planner; the validator also rejects `labrat`), `kama | round-41..43` (parked worktree).
