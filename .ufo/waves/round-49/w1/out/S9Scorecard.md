# S9Scorecard — round 49: SCORECARD.md `## Round 49` section and the head re-anchors (draft)

**Verdict: the draft is complete and self-consistent — `round41-scorecard-reconcile.py` `mismatches=0 met=True`, `round42-selfdesc-reconcile.py` `mismatches=0 maxN=49 met=True`, `planned-pointer-check.py` `met=True`, and `round43-registry-audit.py` fails with exactly 3 mismatches that are all the known `SKILL.md` registry integration item; applying seat S9Skill's six registry rows clears all three (gate `registered 44 unregistered 0 defective 0`, r43 `mismatches=0 met=True`), proven by simulation.**

Seat: leaf scribe, lane kama, axis calibration. No product file was edited; the draft exists as a unified diff plus the full drafted file in the out directory. Lane read-only; all runs on `git clone --shared` in `/fast/scratch/hyaku/kama-r49/S9Scorecard/lane` (toplevel asserted, HEAD `122c4ee95701587cef7f4342c3d175622ec2f4ad` = lane HEAD). Draft commit `e68ba975d2b1a15258c2138a2564346c57ec6c60` touches `SCORECARD.md` only (+67/−8). No tool installed; no pacman; no service started or stopped by this seat.

## 1. What the draft contains

Head re-anchors (drafted file line numbers at `e68ba975`):

| # | Surface | Change |
|---|---|---|
| 1 | authority banner, `SCORECARD.md:6` | round 48 → round 49; `Latest measured round: 49`; "kept current in rounds 43, 44, 45, 46, 47, 48 and 49"; MISSION/`exempt=` sentences kept |
| 2 | `### Superseded head banners` heading, `:2736` | "(kept verbatim; round 48)" → "(kept verbatim; round 49)" |
| 3 | superseded banners, `:2754-2756` | the round-48 banner appended **byte-exact** (verified `cmp` against `git show 122c4ee9:SCORECARD.md \| sed -n 6p`), plus a one-line provenance note naming that command |
| 4 | `## Axes` calibration row, `:18` | spot-check count `34` → `35` (the tree holds 35 `corpus/lessons/*verifier-spotcheck.md` blobs at this tip); latest outside closure `round-47-verifier-spotcheck.md` → `round-48-verifier-spotcheck.md`; "re-anchored round 48" → 49. Every other axis row re-verified unchanged at this tip (hashes, line counts, run facts) |
| 5 | `## Planned` pointer, `:53` | `### Planned (round 49)` → `### Planned (round 50)` |
| 6 | `## Capabilities` mirror intro + two rows, `:117`, `:130-131` | "round-49 canonical list that §Round 49 carries"; `append-only-audit` reworded for v4, `live-receipt-replay` reworded for the witness + bounded archive member; names unchanged (11) |
| 7 | `## Saturation`, `:137` | "(kept current in round 47)" → "(kept current in round 49)"; vector, first-working rounds, nudge-inactive unchanged (both claims are `8→8` and `7→7`, no capability enters) |

New `## Round 49 — the replay execution witness (operability) and append-only-audit v4 by line origin (calibration) (2026-10-26)` at `:2813`, in the round-48 shape:

- `:2815` authority line — `shokunin.conf` axes, lowest non-retired axes, C2→calibration / C1→operability, nudge inactive; base `438127bc…` (round-48 closure = start census); freeze `36d5ed26…` (frozen 2026-10-26T23:17:45Z) with both counter sha256 values, controls dir, freeze-time receipt and start census (both exit 0), C1 source captures; build `74558c71…` with what it landed; separability as frozen.
- `:2817-2820` claims table — C1 operability 8→8 and C2 calibration 7→7, each with the base line from the committed control (`witness=0 cap=0 newrow=0 witnessed=0/3 met=False`; `fixture=0 lane=0 scenarios=4/8 met=False`), the counting command with `--repo/--tip/--scratch/--out`, and the evidence cells.
- `:2822` controls line — all five controls with their exact summary lines and the builder sha256 `9e7a7873…0eba2`; the three junk builds described from `build_controls.py` (fake replay → host binary observed; exempt `continue` removed → `scenarios=4/8`, lane `regressed=1`; word token without origin → `scenarios=7/8`).
- `:2824` `### What met=True does not show (round-49 wave attacks)` — the four preregistration limits as "disclosed before the wave"; C1 findings from the seats whose reports have landed (K1Cheat, K1Design, X1Timeout, X1Compat, U1Prior, R1Provenance, K1Fresh, X1Record); C2 findings (K2Origin, K2Binding, K2Negation, V2Ctr, V2Sample); a marked "still in flight at draft time" line for the mutation/fixture/cross-lane/simplification seats; separability (N2Couple).
- `:2832` scores held + capability sentence; `:2834` canonical list as of round 49 (11 rows, round-48 list byte-intact, two rows reworded, first-working rounds 46/47 unchanged); `:2852` `### Planned (round 50)` with the two items drawn from the wave findings; `:2857` `### Round-49 measured results` with `pending` placeholders, the base lines, and a regressions paragraph that separates **build-time** values at `74558c71` from what the measured run must re-take.

## 2. Evidence

Receipts in the out directory; commands and exits in `runs.txt`.

| Run (tip `e68ba975`) | Output | Exit |
|---|---|---|
| `round41-scorecard-reconcile.py --repo . --tip …` | `axes=6 facts=36 hash_bad=0 lines_bad=0 run_bad=0 dead=0 score_bad=0 hollow=0 mismatches=0 met=True` | 0 |
| `round42-selfdesc-reconcile.py --repo . --tip …` | `r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=49 met=True` | 0 |
| `round43-registry-audit.py --repo . --tip …` | `unreg=2 defect=0 flags=0 pins=0 selftest=1 dc=0 spot=0 hidden=0 pop=44 registered=42 mismatches=3 met=False` | 1 |
| `planned-pointer-check.py SCORECARD.md` | `pointer: ok (… round 50 …)`, 11 `measured: ok` (Round-14 … Round-49), `met=True` | 0 |
| `digest-ledger.py scan --rev …` | `tokens=130 blob=114 … unknown=0` | 0 |
| `append-only-audit.py --repo . --to …` | `events=5 restored=5 ungraded_lines=82 regressed=0 bad_declarations=0` | 0 |
| `hexrun-census.py scan --rev …` | `unknown=2` — identical at base `438127bc` | 1 |
| simulation A: S9Skill's six rows in `SKILL.md`, tip `9b272dce` | gate `registered 44 unregistered 0 defective 0`; r43 `unreg=0 … selftest=0 … mismatches=0 met=True` | 0 / 0 |
| simulation B: canon evidence cells citing `tools/round49-*.py`, tip `8dfe3f17` | r42 `province=2 mismatches=2 met=False` | 1 |

Both simulations were reset away; the clone is back at `e68ba975`. The scratch clone was removed at the end of the seat (every cited receipt was copied here first). The head-table run facts were re-executed at the tip the draft applies to (test-snapshot `pass=30`, pin-watch `pass=9`, report-landing `cases=79`, sources-append-only `45/45`, citation `24 cases`, capability-repertoire `pass=2`, instrument-agreement `pass=4`, recheck count `218`, spotcheck `35`, verdict-ledger `204` rows, knowledge `34`, cross-lane `16`).

## 3. What the four tools require

- **round41-scorecard-reconcile.py** — 6 axis rows, each score equal to the frozen vector (8, 8, 7, 9, 7, 7); every `PATH`+digest and `PATH`+(N lines) fact must re-derive at the tip; every `run `CMD` → `OUT`` must print that exact stdout line (and exit, when stated) inside a throwaway `git archive` export; every other backticked path must exist; no row without a hash or run fact. **The calibration row's run fact had to change: the glob prints `35` at this tip, and the round-48 row stated `34`** (that single stale value was the build-time `mismatches=1`).
- **round42-selfdesc-reconcile.py** — imports r41 unchanged, then: banner contains `operability + calibration`, not `operability and freshness`, not `adds **zero** verified completed rounds`, and states `Latest measured round: <maxN>`; the first `## Planned` section names `### Planned (round <maxN+1>)` and that heading exists with a numbered item under it; `## Retired` states `6 axes` and `11 capabilities`; `## Saturation` states the vector in head-table order, the canonical first-working rounds, and `nudge inactive`; the head `## Capabilities` names equal the canonical list's names and any `N (opened|mined|queued|rejected)` equals the SOURCES census; every backticked `.ufo/…` token in round-40/41-headed sections resolves; README names every non-dot top-level entry; **every `tools/`/`registry/` token in a canonical-row evidence cell appears in `PROVINCE.md`**; each axis row's run fact contains its needle.
- **round43-registry-audit.py** — `unreg=0` (the gate's population must be registered), `flags`/`pins` for its frozen `NEWSET` (round-43-era counters only), `selftest` = `GATE_SELFTEST pass=6 fail=0` run in a clone with `master` at the tip, its round-42 search-log `dc` line, `spot` equal to the tip's spotcheck blob count (`35` now), `hidden`, `pop >= 28`, `registered >= 28`.
- **planned-pointer-check.py** — the contiguous sentence in the first `## Planned` section, and every `§Round-<N> measured results` reference must have a matching `### Round-<N> measured results` line (so the new section must carry that heading, which it does).

## 4. Findings (defects / couplings this seat adds)

**F1 — the gate's own selftest is coupled to the lane's registry state (defect, new).**
`tools/gate-registry-check.py:47` documents arm 6 as evaluating "this lane's own tree at its branch tip"; `selftest()` (`tools/gate-registry-check.py:257`) grades the clone's HEAD, so *any* unregistered counter makes the gate's documented `GATE_SELFTEST pass=6 fail=0` (`SKILL.md:1330`) become `pass=5 fail=1`. Shown by `python3 tools/gate-registry-check.py --selftest` at `74558c71`, `122c4ee9` and `e68ba975` → `FAIL lane-tip …: exit=1 line='registered 42 unregistered 2 defective 0'`. Consequence: `round43-registry-audit.py`'s `selftest` fact fails for a reason that is not about the gate's own logic, and the failure cannot be cleared except by landing the registry rows. Proposed fix: pin arm 6 to a sandbox fixture revision (the fixture machinery already exists at `:237`) or exclude the unregistered population from that arm; the integration alternative — landing S9Skill's rows — is proven to clear it (simulation A).

**F2 — the canonical-row evidence cell is coupled to `PROVINCE.md` (coupling, new).**
`tools/round42-selfdesc-reconcile.py`'s `province` fact requires every `tools/`/`registry/` token in a canonical evidence cell to appear in `PROVINCE.md`; `PROVINCE.md:17` does not name either round-49 counter (`grep -c` → 0). With the evidence cells this draft uses (`.ufo/waves/round-49/measured/c1-build.out`, `c2-build.out`) the fact is clean; with the cells seat S9Cap's draft uses (`tools/round49-replay-witness-audit.py`, `tools/round49-append-audit-v4-check.py`) it reports `province=2 met=False` (simulation B, receipt `r42-with-s9cap-cells.out`). Proposed fix: either keep this draft's cells or add the two tokens to `PROVINCE.md:17` the way round 48 added its counter — exact insertion text in `proposed-province-tokens.txt`.

**F3 — `hexrun-census` `unknown=2` is pre-existing (not this round's).** Identical at base `438127bc` and at the draft tip (`tokens=1832 … unknown=2` vs `tokens=1837 … unknown=2`); the two runs are fleet object ids cited by `corpus/lessons/round-48-verifier-spotcheck.md` (seat K0Harm's finding, independently reproduced here). Not fixable inside this lane without ledger rows; recorded in the draft's regressions paragraph as open at build time.

**F4 — the round-48 C1 counter fails by construction at v4.** `tools/round48-append-audit-v3-check.py` recomputes v3 while `tools/append-only-audit.py` grades v4: `.ufo/waves/round-49/measured/r48c1-build.out` → `lane_events=5 lane_failures=0` but `ungraded_lines tool=82 counter=89`, `met=False`, exit 1. Disclosed in the draft's regressions paragraph (same pattern as round 48's note about the round-47 counter); no action available in this seat.

**F5 — observation, host hygiene (not this seat's).** `pgrep -af llama-server` at report time lists live `llama-server` children and their live-tool parents under sibling seats' scratch trees (`/fast/scratch/hyaku/kama-r49/M1Live/…`, `/fast/scratch/hyaku/kama-r49/X1Kill/…`). This seat started none; the integrator should confirm those seats reap them before the host check.

## 5. Not done / out of scope

- The measured run itself (L1's): the `### Round-49 measured results` table carries `pending`; build-time values are labelled as build time, not as the measurement.
- The wave seats still running at draft time (mutation censuses, fixture census, cross-lane regrade, simplification) — the draft marks that line as "fill at integration" instead of inventing findings.
- `SKILL.md` registry rows (S9Skill), `LOG.md`/lesson/QUALITY/README entries (the other scribes), `corpus/lessons/round-49.md` (lands at integration), and any `PROVINCE.md` edit (proposal only).

## 6. Artifacts (absolute paths)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Scorecard.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Scorecard/SCORECARD-round49.diff` (apply to the lane's `SCORECARD.md`)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Scorecard/SCORECARD.round49.draft.md` (full drafted file)
- `…/S9Scorecard/runs.txt`, `r41.out`, `r42.out`, `r43.out`, `pointer.out`, `gate-with-skillrows.out`, `r43-with-skillrows.out`, `r42-with-s9cap-cells.out`, `proposed-province-tokens.txt`
