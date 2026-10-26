# S8Considerthese — round-49 proposal tracker (considerthese 2026-10-22 … 2026-10-26)

**Verdict: the table is updated through round 49 and six numbered proposals are still unimplemented (3, 4, 5, 6, 7, 11), two are partial (1, 2), one lives only in the reflection series (8), one is delivered solely as a wave artifact (20) and ten have a landed lane artifact — but round 49 itself takes up no proposal by name and says so nowhere, because its preregistration dropped the `frontier.considerthese` field every round since 46 carried, and the lesson, LOG entry, SCORECARD section and wave spec carry no proposal line either; beside that, three instruments that serve landed proposals are decayed: the shortcut tally's default population stops at round 47, seat-yield left the measured set in round 48, and the pin table does not carry the b11909 binary the round's own C1 replays rest on.**

Lane `kama-shokunin`, read-only. HEAD `122c4ee95701587cef7f4342c3d175622ec2f4ad` (round-49 wave spec) plus an integration worktree, snapshot `2026-10-26T23:38Z`. No lane write, no git/jj mutation, no counter run, no claim re-measured, no server started, no tool installed.

## Behavior

1. Read `considerthese/2026-10-26.md` and the older days the table still needs (proposals only, `:20-35` and `:23-41` slices), the round-48 table `.ufo/waves/round-48/w1/out/S8Considerthese/table.md` (rows at `:32-51`), and the round-47 table `.ufo/waves/round-47/w1/out/S8Proposals/table.md` (rows at `:11-30`).
2. Established round 49's uptake from five surfaces: the preregistration, the lesson, `LOG.md`, the SCORECARD round-49 section, and the wave spec (`build_spec.py` seat texts). Built a two-set phrase matrix (round-49 artifacts vs lane implementation surfaces) and a per-day path census; both in this directory.
3. Read the round-48 outside closure in full (verdict `admitted`, `corpus/lessons/round-48-verifier-spotcheck.md:7`) and checked what it rules on the three frontier products of rounds 47-48.
4. Checked, per proposal, whether a lane artifact performs its ask — not whether a round mentioned it — and wrote a one-round uptake sketch for each of the six unimplemented ones (instrument, counter legs, fail-capable fixtures, frozen surface touched).
5. Found and documented five instrument defects (F3, F4, F7, F8 and the tracker's own missing verdict F5) plus two record defects (F1, F2) and one ownership defect (F6). No lane file was edited; every fix is a proposal in the table.

## Gates / checks run (all read-only)

| Check | Command (abbreviated) | Result |
|---|---|---|
| Lane tip + worktree | `git -C <lane> rev-parse HEAD; git status --porcelain` | `122c4ee9`; 10 modified files, 5 untracked paths (`commands.txt` §1) |
| Round-49 prereg keys | `python3 -c "print(list(json.load(open(.../round-49/preregistration.json")).keys()))"` | `[…,'claims','controls','limits']` — **no `frontier`, no `routed`** |
| Rounds 46-49 `frontier.considerthese` | `for r in 46 47 48 49; do …` | 46/47/48 carry it; **49 → `None`** |
| Lesson proposal line | `grep -cE 'considerthese\|proposal' corpus/lessons/round-49.md` | `0`, exit 1 (same for round-48; rounds 41-47 each carry one) |
| `LOG.md` round-49 slice | `sed -n '2331,$p' LOG.md \| grep -cE 'considerthese\|proposal'` | `0`, exit 1 |
| SCORECARD round-49 section | `awk '/^## Round 49/{f=1} f' SCORECARD.md \| grep -cE 'considerthese\|proposal'` | `0`, exit 1 (section is working-tree only; `HEAD` has none) |
| Round-48 closure rules | `grep -nE 'S8Considerthese\|S8Proposals\|X9Tally\|considerthese\|proposal\|tally' corpus/lessons/round-48-verifier-spotcheck.md` | exit 1, 0 hits |
| Tally population | `grep -n 'default="40-47"' tools/shortcut-tally.py`; `sed -n '2p' .ufo/waves/round-49/measured/tally-build.out` | `895: … default="40-47"`; receipt prints `rounds=40-47` |
| Measured set contents | `grep -n '^run ' .ufo/waves/round-49/measured/measure.sh` | 19 runs, `:20-38`; no seat-yield, no round44/45 ledger audit |
| Seat yield history | `grep -c 'seat yield' SCORECARD.md`; `cat .ufo/waves/round-48/measured/seat-yield-w1.out` | hits only at `:2674` (r46), `:2721` (r47); round-48 receipt `seats=69 … missing=0` |
| Pin table vs replay binary | `cat registry/engine-pins.tsv`; `U2Pins.md:13` | pins `b11755 S038`; b11909 in no row |
| Claim receipts (not measured by me) | `tail -1 measured/c1-build.out`, `c2-build.out` | `witness=1 cap=1 newrow=1 witnessed=3/3 met=True`; `fixture=1 lane=1 scenarios=8/8 met=True`; all 5 controls `met=False` |
| Leftover servers | `pgrep -af llama-server` | two pairs, both from sibling seats (`…/M1Live/…`, `…/Sen2Archive/…`); **none started by this seat** |

## Touched surfaces

Wrote only, under `.ufo/waves/round-49/w1/out/S8Considerthese/`:
`table.md` (the deliverable), `refs-matrix.txt` (per-proposal phrase matrix, 20 sections, `R=M:<line>`), `refs-files.txt` (per-day path census over 108 preregs+lessons, `R=F:<line>`), `commands.txt` (every command with its exit code), and this report one level up.
Created and removed `/fast/scratch/hyaku/kama-r49/S8Considerthese` (never used: no clone, no fixture). No write anywhere else; the lane's index, jj state and files are untouched.

## Findings (each with the command that shows it and a proposed fix)

- **F1 — round 49's preregistration dropped `frontier.considerthese`.** `.ufo/waves/round-49/preregistration.json` keys end `…'claims','controls','limits'`; rounds 46-48 each carry `frontier.considerthese` (`.ufo/waves/round-46/preregistration.json:150`, `round-47:56`, `round-48:55`). Show: the `for r in 46 47 48 49` loop in `commands.txt`. Fix: restore the field with a declared `"none"` and the mining route — a declared none is a record, an absent field is not.
- **F2 — rounds 48 and 49 both lack the lesson proposal line that rounds 41-47 kept.** `grep -cE 'considerthese|proposal' corpus/lessons/round-49.md` → 0 (and round-48 → 0), against `round-47.md:37`, `round-46.md:11`, `round-45.md:21`, `round-44.md:41`, `round-43.md:62`, `round-42.md:42`, `round-41.md:123`. Fix: one line at the end of `## Claims`: `considerthese: <day> proposal N → <artifact>` or `considerthese: none (reason)`.
- **F3 — the proposal-19 running count stopped at round 47.** `tools/shortcut-tally.py:895` hardcodes `--rounds` default `"40-47"`; round 49 calls it with no range (`.ufo/waves/round-49/measured/measure.sh:36`), so the receipt prints `rounds=40-47` (`measured/tally-build.out:2`) and the table ends at round 47 (`:4-11`), and the round-49 SCORECARD draft writes that limit into the record as the count (`S9Scorecard/SCORECARD.round49.draft.md:2866`). Fix: derive the default top from the highest `## Round N` present, keep `--rounds` for the selftest, and pass `--rounds 40-<N>` explicitly in `measure.sh`.
- **F4 — seat-yield (proposal 16) left the per-round regression set.** `grep -c 'seat-yield' .ufo/waves/round-49/measured/measure.sh` → 0; round 48's measured set had `.ufo/waves/round-48/measured/seat-yield-w1.out`; SCORECARD's regression lines carry it at `:2674` (r46) and `:2721` (r47) and not at `:2807` (r48) or in the round-49 section (`SCORECARD.md:2813+`, 0 `seat yield` hits). Fix: add `run yield python3 tools/seat-yield.py .ufo/waves/round-49/w1 --expect-reports 71` to `measure.sh`, or state the exclusion.
- **F5 — no closure has ever ruled the tracker or its products.** Round-47 and round-48 closures admit their rounds (`round-47-verifier-spotcheck.md:12`, `round-48-verifier-spotcheck.md:7`) with 0 hits for `S8Considerthese|S8Proposals|X9Tally|proposal|tally`. Fix: one line per frontier artifact a closure does not rule, in the shape the round-48 closure already uses for owner labels (`:113`).
- **F6 — an orchestrator-owned defect is booked as a lane mistake.** `corpus/lessons/round-49.md:35` (Mistakes row 3, stale prompt route map) records closure R4, which the closure files as "**(orchestrator/operator, prompt route map)**" (`corpus/lessons/round-48-verifier-spotcheck.md:113`). Fix: an owner column on Mistakes rows (proposal 4's one-round sketch, §3.2).
- **F7 — instrument regressions are invisible because `measure.sh` is hand-written.** F3 and F4 are the same defect: nothing pins which instruments the measured set must run. Fix: `registry/per-round-instruments.tsv` plus one `gate-registry-check.py` leg that fails when a required instrument has no `run` line.
- **F8 — the pin instrument watches a pin the round's capability does not use.** C1's replays and witness rest on llama.cpp **b11909**, but `registry/engine-pins.tsv:4` pins `b11755 S038`; the round's own U2Pins seat states it: "**b11909 appears in no pin row**" (`.ufo/waves/round-49/w1/out/U2Pins.md:13`), and `behind` is permanent (135 newer tags, ~22-26/day, `:14`). Fix (U2Pins's, `:37`): add a `llama.cpp-replay … b11909` row and wire `replay-inputs-probe.py` beside pin-watch.

## Out of scope / not re-reported

Round 49's claims, counters, controls and preregistration are frozen; nothing here touches them and I ran none of them (C1/C2 receipts quoted only as already-measured, `measured/c1-build.out`, `c2-build.out`, controls all `met=False`). The seat spec's known integration items were not re-reported: the two round-49 counters were unregistered at the build (`measured/gate-build.out`) and their registry rows are now in the working tree (`SKILL.md:1486-1496`); the SCORECARD/LOG/lesson/QUALITY/README entries are mid-integration (`git diff --stat` 10 files, 442/35); S494/S495 `used-by` already names `corpus/lessons/round-49.md` (`corpus/SOURCES.md:247-248`). Because the L1 was integrating while this seat read, every "absent" statement in the table is timestamped to `122c4ee9` + worktree at 23:38Z and is backed by a command in `commands.txt`.

## Artifact paths (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S8Considerthese/table.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S8Considerthese/refs-matrix.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S8Considerthese/refs-files.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S8Considerthese/commands.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S8Considerthese.md` (this report)
