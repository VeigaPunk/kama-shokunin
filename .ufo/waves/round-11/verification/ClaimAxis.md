# ClaimAxis — round-11 critic: axis binding, lowest axis, separability, denominators

Seat: KamaR11.ClaimAxis (critic, author-side advisor; not a non-author verifier).
Review date: 2026-10-20 (UTC). Scope: read-only file reads, `git grep`/`git diff --numstat`/`git status` fact queries in the lane. I ran no tests, builds, lints, formatters, `measure.py`, census or endpoint probes, and opened no network source. Installs: **none**.
Axis source used: `../shokunin.conf:52` current row `kama|kama-shokunin|operability + calibration (...)`. The `MISSION.md:16-31` block is labeled "Historical example … not the current roster", so I did not treat it as an assignment.

## Verdict summary

| # | Claim under test | Result | Severity |
|---|---|---|---|
| A | `mission_axes = [operability, calibration]` | **Holds** | — |
| B | "lowest live axis = calibration (7; operability 8)" | **Outcome holds, reasoning narrower than the rule** | Low |
| C | C1 is a calibration move | **Contestable**: the counted quantity is freshness-shaped metadata presence | Medium (judge tradeoff) |
| D | C1 denominator 27 → 0 | **Holds as defined**. It is the appended-supplement trio, not CORPUS "opens with" conformance | Low–Medium |
| E | C2 net-new over prior coverage | **Partly survives**. Prior llama.cpp id/alias and loaded≠which-model coverage is not credited | Medium |
| F | C2 is coverage, not depth | **Contestable**. PROVINCE already lists the surface; only edge classes are new | Low–Medium (judge tradeoff) |
| G | C1 ⟂ C2 causal separability | **Holds** for the measures. Unclaimed shared correction text exists | Low |
| H | Scores unchanged, with no objective denominator | **Holds**, but SCORECARD still records round-10 count-based deltas and MISSION authority | High if not integrated |
| I | No axis harmed | **Mostly holds**. Date-first `verified-at` values are a machine-reading hazard | Low–Medium |

## A. Axis binding — holds
- `shokunin.conf:52`: `kama|kama-shokunin|operability + calibration (local model serving and endpoint health)`.
- `claims.json:4` declares `["operability","calibration"]`. In `axis-binding-after.json:7` the stdout has `axis_binding_clean`, and declared equals actual. `axis-binding-before.json:7` shows the earlier freshness mismatch, which is kept as evidence.
- The generated prompt `../.ufo/prompts/kama-round-11.md:6` says "Your lane axes: operability + calibration". Prompt, conf and claims all agree.
- `claims.json:26` (`declaration_erratum`) correctly retains `spec.json:3` ("C1 freshness … MISSION assigns operability+freshness (both 8)") as superseded history.

## B. Lowest axis — the outcome holds, the reasoning is too narrow
- The rule text is "the lane's **lowest-scoring non-retired axis**" (`AXES.md:33`, echoed in `kama-round-11.md:15-16`). It does not say "lowest assigned axis".
- Current scores from `SCORECARD.md:211-213`: operability 8, freshness 8, coverage 9, depth 7, calibration 7, adjacency 7. `SCORECARD.md:57-59` retires nothing.
- Over all non-retired axes, calibration **ties** with depth and adjacency at 7. `claims.json:5` compares calibration only with operability, which is the assigned-only reading.
- C1 is on calibration, which is in the tie, so the obligation is met under either reading.
- Stagnation nudge: the saturation line is 8 (`SCORECARD.md:132`). Calibration 7 < 8, so the nudge is inactive and the lowest-axis duty applies. This is correct.
- **Smallest correction:** reword `claims.json:5` to "calibration 7 ties lowest non-retired with depth and adjacency (7); it is also the lowest assigned axis (operability 8)."

## C. Is C1 calibration? Strongest counterexample
- **Same measurement, different label.** `spec.json:3` declared "C1 freshness: 9 legacy knowledge files missing 27 provenance fields -> 0". `claims.json:9-11` keeps the identical before→after and only relabels the axis. The axis changed when the binding check failed; the measured quantity did not change.
- **The fleet contract treats the trio as freshness input.** `CORPUS.md:163-167` says provenance in prose "is unreadable to a freshness sweep". `AXES.md:14` defines freshness as stale items being flagged. Two of the three counted fields (`verified-at`, `recheck`) are freshness metadata by name.
- **The calibration substance is not what gets counted.** That substance is: separating original-observation date from review date, giving an explicit "no live revalidation" limit, and saying "confidence is provenance-of-record only". It is real (e.g. `endpoint-identity.md:152`) and is required by KQ11 (`corpus/QUALITY.md` round-11 rows). `measure.py` mechanizes only one piece of it: the negation-aware wording guard against "live revalidat* today" (`measure.py:50-58`). The count 27 → 0 measures field presence (`measure.py:285-294`).
- **Defense:** `AXES.md:15` calibration covers "gaps named honestly, confidence graded, overreach caught", and the supplements do name gaps and limits. So this is a judge-level tradeoff, not a mechanical defect.
- **Smallest correction (no new work):** in `claims.json:10-12`, state that the count is presence, and that calibration content is KQ11 conformance, which remains author-asserted pending outside review. Optionally add a second count measured by command: legacy supplements whose `verified-at` names both an original-observation date (or "unknown") and the review date, before 0/9 → after 9/9.
- Related unmeasured calibration work: overreach corrections appended this round are not tied to either claim's measure.
  - `endpoint-identity.md:155-164`: the "Identity readiness" overstatement.
  - `runtime-health-surface-matrix.md:42-57`: the S009/S010 citation mismatch.
  - `corpus/README.md:96-112`: the line-32 overclaim.
  - `SKILL.md` round-11 section (+30 lines per `git diff --numstat`).

  These are arguably the strongest calibration evidence in the round. Record them in the lesson as supporting C1's limits text, not as an extra claim.

## D. C1 denominator — holds as defined; state what it is not
- **Before = 27, genuinely.**
  - `legacy-baseline.json:1-83` lists 9 files, each with `missing:[source, verified-at, recheck]`.
  - A grep for `^(source|verified-at|recheck)\s*:` over `.ufo/waves/round-11/frozen/before/corpus/knowledge` found **0 matches**.
  - So "lack all 27" is true even counting the whole file, not just the empty appended region.
- **After, by reading (not by running `measure.py`).** A grep for `^(source|verified-at|recheck):` finds exactly one of each in all 9 legacy files:
  - `alias-endpoint-normalization.md:68-70`
  - `consumer-registry.md:393-395`
  - `cross-lane-scope.md:83-85`
  - `drift-timeline.md:32-34`
  - `endpoint-identity.md:151-153`
  - `free-tier-provider-limits.md:73-75`
  - `listener-census.md:385-387`
  - `served-model-identity.md:40-42`
  - `snapshot-history.md:102-104`

  That is 27 lines.
- **Prefix:** `git diff --numstat` shows 0 deletions on 7 of the 9 files. `listener-census.md` shows 1 deletion; `git diff` shows it is the old final line re-emitted with a newline (`\ No newline at end of file`), which is consistent with an append-only change. The byte check is `measure.py`'s job, and I did not run it.
- **18 → 9:** the plan's 18 (`SCORECARD.md:203`) is 9 legacy knowledge entries plus 9 pre-round-10 lessons, from the `corpus/lessons/` listing: round-1, -1-citations, -1-critic, -1-relaunch-freshness, -1-safety, -2, -4-recensus, -5, probe-mutation-matrix. `CORPUS.md:18-20` requires the trio for `knowledge/` only; lessons need `## Gate`. Narrowing to 9 is justified.
  - The phrasing at `claims.json:25` ("actual knowledge census contains 9 legacy and 3 round-10 entries") reads as if the plan miscounted.
  - `corpus/README.md:110-112` states it correctly: "the old SCORECARD plan's eighteen included lessons".
  - **Fix:** mirror the README wording in `claims.json:25`.
- **What the denominator is not:** `CORPUS.md:18` says each knowledge entry "**opens with**" the trio, and `CORPUS.md:163-165` says the trio "come first". The 9 supplements are appended at the end, so a head-of-file reader still finds 9/9 not opening with the trio.
  - This is a deliberate trade against `CORPUS.md:53` ("Corrections are new entries, never rewrites"), and KQ11 exempts legacy files.
  - **Fix:** add to `claims.json:12` limit: "satisfies the appended-trio measure; legacy entries still do not *open* with the trio (CORPUS.md:18), by append-only design."
- **No collision with the round-10 coverage counter:** no legacy `source:` value begins `S[0-9]{3}`. The `grep -lE '^source: S[0-9]{3}'` counter from `SCORECARD.md:212` moves only through the new crosswalk. ReviewContract S1's contamination risk is cleared.

## E. C2 net-new — the survivor class recurs
The crosswalk credits only the tags/ps split (`served-identity-crosswalk.md:13`). Two more pieces of prior coverage exist at baseline `2f7303c` and are not credited:
1. `runtime-health-surface-matrix.md:14` (round 10) already states that the llama.cpp identity route is `GET /v1/models` with `data[].id` = the `-m` path or `--alias`. It also says "200 proves a model finished loading, not which model". Crosswalk lines 20 and 36 restate the id/`--alias` rule, and lines 43-45 restate loaded≠identity.
2. `listener-census.md:86-90` (round 1, read via `git show 2f7303c:`) already documents that `--alias` set to the full GGUF path makes served `id` differ from the bare model key, so `MODEL_MISMATCH`.

Also, `PROVINCE.md:12` lists "served-model-id reconciliation | `GET /v1/models` vs `--alias` vs the configured model id" as an owned surface.

Genuinely new, as far as these reads show:
- `remote_model`/`remote_host` (S031)
- `expires_at` (S012)
- `meta: null` while loading (S001)
- router `status.value` states and the exempt `/health` (S001)
- comma-separated alias ambiguity and `--tags` (S001)
- the digest-join limit (S011/S012)
- OpenAI `shutdown_date`/`owned_by` as catalog fields (S016)

These match the residual list at `claims.json:18`.

**Smallest correction:** append to the crosswalk's §Prior coverage that the id = `-m` path / `--alias` rule and "200 ≠ which model" come from matrix:14 and `listener-census.md:86-90`, and claim only the residual list. Without this, a reviewer can repeat AttackCoverage's survivor finding on llama.cpp. The round-11 lesson Mistakes row at `round-11.md:85` covers Ollama only.

Measure gap: `measure.py:110` `REQUIRED_SOURCE_IDS = (S001, S010, S011, S012, S016)` omits **S031**, the row that carries the claimed remote-inventory novelty (`claims.json:19`). If S031 were dropped from the entry, the crosswalk check would still pass. **Fix:** add S031 to the tuple, or state in the claim that S031's presence is human-reviewed.

## F. Coverage vs depth for C2 — judge tradeoff
- **For coverage:** `AXES.md:12` counts "edge classes". Remote inventory, expiry, the router state machine and mid-load listing are edge classes not previously governed.
- **Against coverage:**
  - The governed surface itself is unchanged: `PROVINCE.md:12`, and `PROVINCE.md` is unmodified (`git status`).
  - Novelty partly rests on this round's own correction that downgrades the baseline index row `corpus/README.md:32` (`README.md:102-107`). That makes "uncovered ground" partly self-established.
  - The content fits `AXES.md:11` depth ("verifiable technical detail … cited sources") at least as well.
- Coverage is also not in the conf assignment. `MISSION.md:49-51` allows adding axes "on evidence (falsifiable claim per move)". No SCORECARD row records coverage as added, although it has been scored since round 1 and claimed in round 10.
- **Smallest correction:** keep coverage, but have the SCORECARD round-11 row cite the edge-class reading of `AXES.md:12` explicitly. Note that depth (7, tied lowest) would be the alternative label.

## G. Separability — holds
- `measure.py provenance` reads only baseline files and checks only the trio, the heading and the prefix. `measure.py crosswalk` reads only `served-identity-crosswalk.md`. Neither measure reads the other's output, so each verifies without the other.
- C1's `source:` lines cite retained in-repo history, not S031 or crosswalk rows, so SOURCES ordering (ReviewContract S2) affects only C2.
- Residual coupling: `endpoint-identity.md:155-164` sits inside C1's measured appended region but cites C2's sources (S001/S011/S012). It does not change C1's counts. If C2 were rejected, this block would need its own attribution. **Fix:** name it in the lesson as an unclaimed correction.

## H. Scores and authority — integration must-dos (parent, after the wave)
- Keeping calibration 7 and coverage 9 unchanged is consistent with "no objective denominator". 27 → 0 closes a fixed 9-file population, not a 0–10 axis scale.
- **Inconsistency:** `SCORECARD.md:196-197,211-212` keeps round-10's count-based moves (freshness 7→8, coverage 8→9) as measured deltas. Under round 11's own rule (`claims.json:13,21`), those are self-assessments too. **Fix:** the appended round-11 SCORECARD section should say so. Do not rewrite or re-derive the round-10 deltas.
- **Duplicate authority (High if missed):** the SCORECARD is unmodified in `git status`, and several lines still bind axes to MISSION or plan freshness moves:
  - `SCORECARD.md:6-7`: "assigned LIVE axes remain operability and freshness (`../MISSION.md`)"
  - `SCORECARD.md:48`: "next falsifiable freshness move"
  - `SCORECARD.md:192`: "Axis authority: `MISSION.md:29`"
  - `SCORECARD.md:203` (1): freshness

  Meanwhile `SKILL.md` (round-11 section), KQ12, `round-11.md:84` and `claims.json:5` cite the conf. **Fix:** an appended SCORECARD round-11 supersession that names `shokunin.conf:52` as the authority and marks those lines historical.

## I. Harm check — date-first `verified-at`
- 8 of 9 legacy `verified-at:` values begin with the review date 2026-10-20 (or `metadata review only, 2026-10-20`). Only `endpoint-identity.md:152` leads with the original observation date (2026-09-28).
- The prose disclaimers are present everywhere. But a date-extracting freshness sweep — the purpose CORPUS `:167` and kaika `mistakes.md:469-472` give for the trio — would read these entries as verified 2026-10-20, even though the observations date from 2026-08-20 to 2026-10-19.
- I found no current fleet parser that does this (grep of `scripts/` and several lane `tools/`: no `verified-at` date parser). So this is a latent false-freshness signal, not an observed harm.
- **Smallest correction:** these files are still uncommitted. Normalize the first token to the original observation date or "unknown", followed by the metadata-review date, as `endpoint-identity.md:152` already does. Alternatively, record the convention in KQ11.

## Already correct
- The axis binding matches the conf. The historical MISSION example is not used as an assignment, and the prior error is preserved, not hidden.
- C1/C2 are on distinct axes, there are 2 claims (≤ 3), and one claim is on a tied-lowest axis.
- Baseline digests are pinned, and `measure.py` fails closed on baseline tampering (`measure.py:234-239`).
- No legacy supplement contaminates the `^source: S###` counter.
- Lessons are excluded from C1, with the CORPUS basis recorded in `README.md:110-112`.
- No numeric score is advanced, and no outside review is fabricated (`round-11.md:72-77`).

## Limits
- Counts come from reads and greps, not from executing `measure.py` or the census; prefix integrity is inferred from `git diff --numstat`.
- No public source was opened, and S-row quotes were not checked by this seat.
- The TameshiR12 IRC routing instruction (tameshi round-12 path) does not apply to this Kama seat; this report stays at its assigned path.
