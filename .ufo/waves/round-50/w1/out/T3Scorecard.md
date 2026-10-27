# T3Scorecard — round-50 SCORECARD draft and head re-anchors

**Verdict:** the draft is complete and self-consistent — at the final draft tip the round-41 axes counter and the round-42 self-description counter both reach `mismatches=0 met=True` (`maxN=50`), `planned-pointer-check` is met, the draft keeps the lane's append-only record clean (`regressed=0 ungraded_lines=89`), and the round-43 registry audit is left failing only by the two round-50 counters not yet in `SKILL.md`'s registry (which also breaks the gate selftest's `lane-tip` arm); inserting the two supplied registry rows closes both, after which the depth row must be re-anchored to the new `SKILL.md` digest. The wave subsection now carries the 37 seat reports landed by 22:05, including the C1 and C2 defects they found.

## Behaviour

Wrote the round-50 SCORECARD section and the head re-anchors into a scratch clone of the lane
(`git clone --shared`, one clone per pass under `/fast/scratch/hyaku/kama-r50/T3Scorecard/lane`)
and committed them there as `7d254da39ca457fb7eea7a3a2813014218f2e691` (clone only; the lane was
never written). The deliverable `T3Scorecard/scorecard.md` is that commit's `SCORECARD.md`
verbatim — 2927 lines, sha256
`35f08433f15393bee40f6ef038e7d1007703154a34ebe0fb30d20503af9a4abf`.

Section content (`scorecard.md:2876`–`2927`): authority line with base `26ecba64`, freeze
`601c8889`, the two frozen counter digests, the build `97c864be` and the two follow-ups
(`3d42897b`, `3b79eadd`); the two-claim table with both counting commands, base values and build
receipts; the controls line (the two base controls, the seven missing ablations, and the wave's
ablation results); `### What met=True does not show (round-50 wave attacks)` with the prereg's five
disclosed limits and the folded C1/C2 seat findings; scores held and the 11→11 capability note;
the round-50 canonical capability list (11 rows, two reworded); `### Planned (round 51)` with the
two required items, now naming the wave's gaps; and `### Round-50 measured results` with `pending`
cells, build values, and a regressions paragraph that records the hexrun and battery gaps.

Head re-anchors: authority banner (round 49→50, `Latest measured round: 50`, `kept current in
rounds 43 … 49 and 50`); calibration row `35`→`36` outside closures and latest closure
`round-48-verifier-spotcheck.md`→`round-49-verifier-spotcheck.md` (re-anchored round 50);
`## Planned` pointer → `### Planned (round 51)`; `## Capabilities` mirror header → round 50 and
its two reworded rows; `## Saturation` kept-current round; `### Superseded head banners` heading →
round 50 with the round-49 banner appended byte-exact (984 bytes, sha256
`afb94e914b91ef8aa8320ff628a1f624b7befdeb1bd1f769c4fec94a5a2640ce`; source
`git show 24e906f0:SCORECARD.md | sed -n 6p`, byte-identical to the tip's line 6 — `cmp` exit 0).

## Gates (final draft `7d254da3`, exit codes as recorded)

| Gate | Command | Result |
|---|---|---|
| round-41 axes | `python3 tools/round41-scorecard-reconcile.py --repo . --tip HEAD` | `axes=6 facts=36 hash_bad=0 lines_bad=0 run_bad=0 dead=0 score_bad=0 hollow=0 mismatches=0 met=True`, exit 0 (`draft-r41.out`) |
| round-42 self-desc | `python3 tools/round42-selfdesc-reconcile.py --repo . --tip HEAD` | `r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=50 met=True`, exit 0 (`draft-r42.out`) |
| round-43 registry | `python3 tools/round43-registry-audit.py --repo . --tip HEAD` | `unreg=2 defect=0 flags=0 pins=0 selftest=1 dc=0 spot=0 hidden=0 pop=46 registered=44 mismatches=3 met=False`, exit 1 (`draft-r43.out`): `gate unregistered tools/round50-append-audit-v5-check.py`, `gate unregistered tools/round50-replay-bind-audit.py`, `selftest: documented 'GATE_SELFTEST pass=6 fail=0', run printed 'GATE_SELFTEST pass=5 fail=1'` |
| planned pointer | `python3 tools/planned-pointer-check.py SCORECARD.md` | `pointer: ok (### Planned (round 51))`, `measured: ok (### Round-50 measured results)`, `met=True`, exit 0 (`draft-pointer.out`) |
| append-only audit | `python3 tools/append-only-audit.py --repo . --to HEAD` | 5 events, `restored=5 partial=0 unrestored=0 ungraded=0 ungraded_lines=89 regressed=0 bad_declarations=0`, exit 0 (`draft-aoa.out`) — the draft deletes nothing the contract grades |

Baseline on the pristine tip `3b79eadd`: round-41 `run_bad=1 mismatches=1 met=False` (calibration
run printed 36, row stated 35), round-43 `mismatches=4 met=False` (two `unreg`, the `selftest` arm,
and `spot: calibration row states 35, tree holds 36`), pointer `met=True` (pointer then
`round 50`). Files: `base-r41.out`, `base-r43.out`. The first draft commit (`6b2ccd37`, before the
wave findings were folded) measured identically on all four gates; the receipts in the artifact
directory are the final ones.

### What r43 requires, and that it is sufficient

Both remaining mismatch classes are one cause: the two round-50 counters have no `SKILL.md`
registry row, and the gate selftest's arm 6 (`lane-tip`) fails *only* because of that
(`PASS valid-row … FAIL lane-tip 7d254da39ca4: exit=1 line='registered 44 unregistered 2 defective 0'`,
`GATE_SELFTEST pass=5 fail=1`). Simulated in the same clone (commit `d3e1a374`, two rows inserted
after `SKILL.md:1496`): `GATE_SELFTEST pass=6 fail=0` exit 0 (`sim-gate-selftest.out`),
`unreg=0 defect=0 flags=0 pins=0 selftest=0 dc=0 spot=0 hidden=0 pop=46 registered=46 mismatches=0
met=True` exit 0 (`sim-r43.out`). The rows are supplied verbatim in
`proposed-skill-registry-rows.md`. The insertion changes `SKILL.md`, so the depth row must be
re-anchored in the same commit — verified at `d3e1a374`: round-41 reports `hash_bad=1 lines_bad=1
mismatches=2 met=False` with `SKILL.md` cited `0ad48efc…` / `1504 lines` vs observed
`d1f9db94cf4c4c43edce3fbe1b8af9296bd3b3338ce756d1ef1c108d30480b73` / `1506 lines` (`sim-r41.out`);
`grep -c '^## '` stays 37.

## Wave findings folded into the section (37 seat reports, landed by 2026-10-26 22:05)

- **C1 controls hold:** J1NoEnv (allow-list removed → bind 0/3), J2NoPdeathsig (teardown 0;
  descendants alive at 30.02 s), J3NoMapping (mapped leg 0/3), each `met=False`.
- **C1 open defects:** J4Decoy — a decoy replay that sanitizes its environment and records the
  observed mapping still reaches `bind=1 teardown=1 newrow=1 met=True` without running the live
  tool; Sen1Env — the live tool hands `PATH`/`HOME` to `tools/kama-probe.sh`, which runs
  `python3` without `-I`, so five vectors execute code inside the replay; X11ModelSwap — an
  in-place model rewrite with different bytes *after* the sample passes every check while the
  server's tokens change; X10NonceEdge — 60/60 fresh nonces round-trip but 10/20 edge forms fail
  the rule closed (string-and-literals-only).
- **C2 open gaps:** J6Ablation — the three definition ablations are caught, but the not-gutted
  `eligible` test and `only=` prefix regions have zero coverage (the `eligible` gap is 6 of the
  89 lane ungraded lines); V3Stable — exit 2 on the round-47 tip (pre-`region` contract) discards
  computed fixture results; N3Pattern2 — the lane leg still takes the event population and
  restoration half on self-report; the binder is still the v4 copy (V2Ctr).
- **No-defect reports:** X9Descend, U1Fresh (btrfs fails closed as the stated `dev` limit),
  X1Observe2, R1Rerun2, R2Rerun2, R3Provenance, R4Check, V1Prereg2, V4Determinism, S2Gate2
  (ADMIT), X13Threshold; S2Gate2 reports one minor defect in both frozen counters (`--out` opened
  without creating its parent directory).
- The section states the fold point; reports landing after 22:05 fold at integration.

## Findings

1. **Closed at `3d42897b` (recorded in the draft's regressions paragraph):** the S498 row as it
   first landed made the source append gate fail. At `97c864be`:
   `python3 tools/sources-append-only.py --from 26ecba64ad6fb571d09074b07202d1618a46ecd1 --to 97c864bead3ee4a2f629574e77263d33834ec98a`
   → `error: 97c864bead3ee4a2f629574e77263d33834ec98a:corpus/SOURCES.md:251: unterminated table row
   (no closing pipe)`, exit 2 (`.ufo/waves/round-50/measured/sao-build.out`). At `3b79eadd` the same
   command prints `added S496 (allowed)`, `added S497 (allowed)`, `added S498 (allowed)`,
   `no append-only violations`, exit 0 (run in my clone).
2. **Open, blocks the measured commit's controls claim:** `.ufo/waves/round-50/controls/` holds only
   `base.c1.out` and `base.c2.out`; the prereg's seven ablations are uncommitted, though the wave's
   seats (J1NoEnv, J2NoPdeathsig, J3NoMapping, J4Decoy, J6Ablation) have produced the `met=False`
   results in their own scratch fixtures. Receipts must land under `controls/` before measurement.
3. **Open, integration-owned:** `hexrun-census` `unknown=1` exit 1 at the build. Seat T1Log F1
   traces it to `corpus/lessons/round-49-verifier-spotcheck.md:21`, which cites the **fleet-repo**
   commit `f8cdb853…` as lane evidence, and proposes one append-only `unverifiable` row in
   `registry/hexrun-ledger.tsv`; seat X5Digest2 agrees there is no new digest-ledger row (measured
   `digest-ledger unknown=0`).
4. **Open, integration-owned:** seat T1Log F3 — `measure.sh:37`–`:39` run the round-48 v5 replay
   counter and both round-49 counters with no committed receipt, so their state at the battery tip
   is unobserved. Either add the three receipts or remove the three lines with a note.
5. **Registration and depth re-anchor** as in §"What r43 requires": two rows and one digest swap;
   the wave's T2Skill/X3Gate2 propose a different row shape (a new section), so integration must
   pick one set and re-anchor to the digest it then observes.
6. **Measured cells stay `pending`:** L1 takes the measured commit after integration. The banner
   says `Latest measured round: 50` because the round-42 counter requires it once the round-50
   heading exists; this follows the round-49 precedent (banner 49 before measurement, measured
   paragraph appended afterwards), and the measured paragraph must be appended, not the `pending`
   cells rewritten.

## Out of scope / limits

- I did not run the two claim counters (network, ~46 s and ~5 s); the C1/C2 build values cited are
  the committed receipts `.ufo/waves/round-50/measured/{c1,c2}-build.out`, produced by
  `measure.sh` and re-run at `3b79eadd`, not re-executed by me. The measured cells are placeholders.
- I did not re-run any wave seat's experiment; the wave findings are reported as the seats state
  them, with their verdicts quoted.
- I did not edit `SKILL.md`, `LOG.md`, the lesson, `corpus/QUALITY.md`, `README.md`, the controls,
  the counters or the preregistration; the only proposed non-SCORECARD edit is
  `proposed-skill-registry-rows.md`, as text.
- Tooling: nothing installed (no pacman, no uv/npx); no service started or stopped. Servers seen at
  finish belong to other seats' scratch roots, not mine.
- Scratch `/fast/scratch/hyaku/kama-r50/T3Scorecard` was removed after copying the receipts.

## Artifacts

- `.ufo/waves/round-50/w1/out/T3Scorecard/scorecard.md` — full proposed `SCORECARD.md` (final draft `7d254da3`).
- `.ufo/waves/round-50/w1/out/T3Scorecard/proposed-skill-registry-rows.md` — the two registry rows, the depth-row re-anchor, and the alternative wave shape.
- `.ufo/waves/round-50/w1/out/T3Scorecard/{draft-r41,draft-r42,draft-r43,draft-pointer,draft-aoa,draft-gate-selftest,base-r41,base-r43,sim-r41,sim-r43,sim-gate-selftest}.out` — the receipts cited above.
