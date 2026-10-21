# CritAxisScore — round 23 falsify: is "calibration 7 → 7 (narrow), no harm" honest?

Seat: `CloseKama22.CritAxisScore-2` (critic, leaf). Base `245a37f69628c2c6bb29bbf17897d8fb5946c857`
(clone `/tmp/kama-r23w2/CritAxisScore`, `git rev-parse HEAD` = base). Findings only.

## Verdict: partially falsified

- **The score of 7 → 7 (narrow, improved) holds.** It matches lane precedent, and 8 is not supportable. Moving it
  to "unchanged" is not warranted.
- **"No harm" is falsified.** Operability has a measured, partly undeclared regression: inputs where the
  frozen arm gave a correct clean verdict (exit 0) now get could-not-evaluate (exit 2). One of those cases is
  live right now on the real fleet repository (see the next section).
- **Calibration records at the base commit do not match repository state.** These are fixable by appended
  corrections and do not change the score.

## Incident: the fleet repository is contaminated (reported to CloseKama22)

`/home/vgpnk/Projects/shokunin/.git/objects/pack/` now holds four zero-byte `*.promisor` markers:
`pack-22727cb1…`, `pack-3cd47c8a…`, `pack-e193a790…` and `pack-deadbeef.promisor`. All have mtime
`2026-10-21 12:50:16 -0300`. A peer wrote a fault fixture into the fleet root, which the contract forbids.
I did not touch the files. `git -C <fleet> config --get-regexp 'remote\..*\.promisor|extensions\.partialclone'`
exits 1, so no promisor configuration exists.

| Command (lane=`…/kama-shokunin`, fleet=`…/shokunin`, `--rounds 10-22 --json`) | Before 12:50 | After 12:50 |
|---|---|---|
| current `tools/report-landing-audit.py` | exit 0, sha256 `1ae84922…` (byte-identical to frozen) | **exit 2**: `could-not-evaluate: /home/vgpnk/Projects/shokunin: partial clone (promisor pack)` |
| frozen blob `4fe9339f:tools/report-landing-audit.py` | exit 0, `1ae84922…` | exit 0, `1ae84922…` (unchanged) |

Consequences:

- Any no-harm rerun of the rounds 10–22 ledger on the real fleet after 12:50 -0300 is contaminated.
- This is also a live counterexample to the no-harm claim. On the supported population, which KQ32 limits to
  the trusted lane and fleet repositories, one stray marker file with no partial-clone configuration turns the
  gate from a verdict into a refusal. No override flag exists.

## Counterexample 1: undeclared operability regressions (no-trade rule)

AXES.md (fleet `AXES.md`, §Working the axes) says: "A round is admitted only if every claim verifies **and no
axis is harmed** — a trade anywhere is not an improvement: report every verdict and let the operator rule."

The declared tradeoff covers only T01 (shallow and partial clones; lesson `corpus/lessons/round-23.md:83-84`).
I reproduced three more frozen-0 → current-2 flips on ordinary full clones. Each fixture is the grid's own
`base(tmp)` lane/fleet pair, run with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1` and
`--rounds 1-1 --no-errata`. Output is in `out/CritAxisScore/inert-config-probe.txt`.

| Mutation applied to a clean full-clone lane | Frozen arm | Current arm |
|---|---|---|
| Append `[branch "caf\xe9"]\n\tdescription = harmless\n` to `.git/config` | 0 → 0, same stdout | 0 → **2**: "output is not UTF-8" (strict decode of `git config --list --name-only`, `tools/report-landing-audit.py:445` via `:122-127`) |
| `git config remote.origin.promisor false` | 0 → 0 | 0 → **2**: "partial clone (remote.origin.promisor)" (`:445-448`, which matches the key name and ignores the value) |
| Zero-byte `objects/pack/pack-deadbeef.promisor` with no matching pack and no config | 0 → 0 | 0 → **2**: "partial clone (promisor pack)" (`:438-444`, which matches any `*.promisor` file) |

The declared T01 row also regresses in a measurable way. In `out/CritAxisScore/grid-both.json`,
`T01-blobless-partial-clone` gives frozen exit 0 (met) and current exit 2, while every cited object is local.

This differs from round 17's accepted "refuses to certify what it did not observe" ruling
(`corpus/lessons/round-17-verifier-spotcheck.md:18-22`):

- In round 17, the frozen pass was vacuous.
- In T01 and the three rows above, the frozen exit-0 verdicts rest on objects that are present. They are sound
  positive evidence, not unobserved states.

Impacted axis: operability. The SKILL row
`SKILL.md:683` defines "2 could-not-evaluate (missing/irregular report, unusable git, malformed ledger, empty round set, output failure)".
None of these new refusal causes appears in it.

## Counterexample 2: a git ≥ 2.45 floor bought by a non-load-bearing element

- The tool's own header says "git >= 2.45 is required" (`tools/report-landing-audit.py:55`). The only element
  that sets the floor is `"--no-lazy-fetch"` (`:93`).
- The round's own mutant result calls that element defensive-only: survivor M02 (lesson `:79-82`). The
  promisor refusal runs first.
- The installed docs (git 2.56.0, `man git`) say "This is equivalent to setting the GIT_NO_LAZY_FETCH environment
  variable to 1."
- Variant (`out/CritAxisScore/env-variant.diff`): drop the flag from `GIT_ISOLATION` and add
  `GIT_NO_LAZY_FETCH="1"` to `git_env()`. Measured results:
  - `repo-state-grid.py --arm current --current <variant> --json` exits 0: faults 26/26, controls 8/8,
    tracebacks 0, executed 0, timeouts 0.
  - Variant `--selftest` gives cases=50 failed=0.
- Not verified: how the variant behaves on git < 2.45. No old git is available, and pacman is paused. That an
  older git ignores the unknown variable, losing the defense but not crashing, is [INFERENCE].
- On this host (git 2.56.0) the floor causes no observed harm. It is a hypothetical harm only. It is documented
  in the tool header and the lesson, but not in `SKILL.md:683`.

## Counterexample 3: calibration records at 245a37f do not match repository state

The calibration axis is defined as "SHONEN.md/SCORECARD entries match observed repo state." Four records at the
base commit do not:

1. **Dangling rule reference.** Lesson `corpus/lessons/round-23.md:64` (M1, "fix" column) cites **KQ34**.
   `git grep -n KQ34 245a37f` matches only that line. `corpus/QUALITY.md` ends at KQ33 (`:171`).
2. **Stale traceback count.** M1 says the frozen arm had "8 tracebacks". Two independent frozen runs at the base
   give **tracebacks 9**: F01, F02, F16, F18, F19, F20, F22, F24, F26 (`grid-both.json`, `grid-frozen2.json`).
   The other figures match: faults 0/26, executed 2 (F06, F09), timeouts 1 (F14).
3. **Stale skill boundary.** `SKILL.md:731-738` still says "UTF-8/error/top-level handling … remain unclaimed
   until separately hardened". Round 23 hardened exactly those. `SKILL.md:683` also lacks the new exit-2
   causes and the git floor.
4. **No round-23 score entry.** `SCORECARD.md` and `LOG.md` have no round-23 section. The "7 → 7 narrow"
   claim lives only in the dispatch prompt.
   - Precedent: round 22 committed its declaration before measurement (`SCORECARD.md:1036-1047`).
   - AXES.md requires recording before→after in `SCORECARD.md`.

## Score judgment

**7 → 7, improved (narrow), holds.** The reasons it should stay at 7:

- **Precedent.** Every calibration claim from round 11 to round 22 landed at 7 → 7 (`SCORECARD.md:240, 299, 356, 417,
  501, 610, 680, 753, 871`). Round 19's 7 → 8 was withdrawn as "improved-bounded" (`:845`).
- **Round 17 rule.** "an instrument's self-description made true is a bounded calibration repair"
  (`SCORECARD.md:662`) covers M1. The docstring now discloses O01/O02 (`tools/report-landing-audit.py:52-55`)
  and does not overclaim.
- **8 lacks support:**
  - KQ32 stays in force.
  - O01/O02 still give exit 0 where 1 is expected (`grid-both.json`).
  - The sibling tools remain unisolated.
  - There is no outside non-author spot-check (`SCORECARD.md:90, 199`).
  - Counterexample 3 shows the round's own records mismatching.
- **"Unchanged" is not warranted.** The graded delta is real and fail-capable: frozen 0/26 faults → current
  26/26, controls 8/8 in both arms, verified twice.
  - Caveat on one row: F23's frozen "violation" (exit 1, `unresolved-full-hash` for a blob absent from the
    clone) matches the frozen docstring's literal definition ("no git object in the lane or fleet repo").
  - So F23 is a redefinition of the spec, not a crash, flip or hang relative to the frozen spec.
  - The F23 framing belongs to CritFrozenFairness or CritRefusalScope. It does not move the score.

## Harmed axes

| Axis | Ruling at 245a37f | Evidence |
|---|---|---|
| calibration | improved narrowly, 7 → 7. The records need correction (Counterexample 3); the score does not change. | grid, docstring, lesson lines above |
| operability | **harmed (narrow)**, not "unchanged". There are new exit-2 refusals on sound-verdict inputs: T01 plus three undeclared rows, one of which is live on the fleet now. The git floor is a hypothetical harm. | Counterexamples 1 and 2; incident table |
| freshness, coverage, depth, adjacency | not affected by this change (not measured beyond reading) | — |

## Smallest safe corrections

These are for L1. The canonical judge decides whether the trade is admissible.

1. **Report the trade instead of claiming no harm.** Write "operability: trade, operator rules". List T01, the
   non-UTF-8 config subsection, `promisor=false`, and the orphan marker with frozen-0 → current-2 evidence. This
   is the AXES no-trade rule.
2. **Or remove the over-refusals,** which would make "no harm" true:
   - Decode the config census with `surrogateescape`, since it matches ASCII key names only.
   - Evaluate `remote.*.promisor` with git boolean semantics (CritRefusalScope's correction).
   - Count a `.promisor` marker only when its `pack-*.pack` exists.
   - Each change needs a grid control row in both arms.
   - T01 remains a declared trade unless refusal is deferred until a token is actually missing in a promisor
     repository.
3. **Remove the git floor.** Replace `--no-lazy-fetch` with `GIT_NO_LAZY_FETCH=1` in `git_env()`. This is
   measured above at 26/26 faults, 8/8 controls and 50/50 selftest. Alternatively, keep the flag and add the
   floor to `SKILL.md:683`.
4. **Append record corrections:**
   - Add the KQ34 row to `corpus/QUALITY.md`, or retarget M1 to KQ32.
   - Correct "8 tracebacks" to 9.
   - Supersede `SKILL.md:731-738` and update the exit-2 map at `SKILL.md:683`.
   - Commit a round-23 SCORECARD/LOG declaration of calibration 7 → 7 with the operability verdict above.
5. **Fleet contamination.** The owning seat or L1 should remove the four `*.promisor` markers from the fleet root.
   Then rerun the real rounds 10–22 ledger and record the time window.

## Commands run (all exit codes observed)

- Real population, before contamination, from the clone:
  - `python3 {frozen,current} --lane-repo …/kama-shokunin --fleet-repo …/shokunin --rounds 10-22 [--no-errata] --json`
  - Results: 0 / 1 / 0 / 1. Outputs byte-identical across arms (`1ae84922…`, no-errata `13b17b1c…`).
- Same command after contamination: current exits 2, frozen exits 0 (`real-current-2.err`, `real-frozen-2.json`).
- `python3 tests/report-audit/repo-state-grid.py --arm both --json` exits 1 (expected). Wall time 45 s.
- `python3 tests/report-audit/repo-state-grid.py --arm frozen --json` exits 1. Tracebacks 9 again.
- `python3 tools/report-landing-audit.py --selftest` gives cases=50 failed=0, exit 0.
- Variant grid exits 0; variant selftest gives 50/50.

## Not verified

- `isolation-mutants.py` was not run. The M02 status is taken from the lesson.
- The variant's behavior on git < 2.45 (no old git available).
- The actual-pack-marker refusal measured against git's own `is_promisor_object` semantics.
- Who wrote the fleet markers.
- Any freshness, coverage, depth or adjacency measurement.
- Upstream web pages were not fetched. The `GIT_NO_LAZY_FETCH` quote comes from the installed git 2.56.0 manual
  page.

No tools were installed.

## Files written

- `.ufo/waves/round-23/falsify/advice/CritAxisScore.md` (this file).
- In `.ufo/waves/round-23/falsify/out/CritAxisScore/`:
  - `grid-both.json` (`73cebfa0…`)
  - `grid-frozen2.json` (`86e64758…`)
  - `grid-variant.json` (`ea418a95…`)
  - `env-variant.diff` (`2bc1803e…`)
  - `real-frozen.json`, `real-current.json`, `real-frozen-2.json` (all `1ae84922…`)
  - `real-current-2.json` (empty)
  - `real-current-2.err` (`b34bb93a…`)
  - `inert-config-probe.txt` (`a2b7aaf9…`)
- Scratch only: `/tmp/kama-r23w2/CritAxisScore` and `/tmp/kama-r23w2/CritAxisScore-out`.
