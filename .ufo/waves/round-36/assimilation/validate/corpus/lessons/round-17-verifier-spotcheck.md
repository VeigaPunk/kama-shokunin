author: hyaku closure (non-author integrator, @m_opus)

# Round 17 — non-author closure and verifier spot-check

## Decision

**Status: ok; admitted: true; verdict: admitted.** The report is real and committed, not a
marker. Both declared claims verify within their declared scope, and no owned axis is harmed
against `cff9e62f05aa7cfb9059444f62eb787100719713`.

- **C1 calibration (7 → 7): improved, bounded.** I re-measured the grading conjunct and the
  identity of the matrix and probe bytes myself. I verified the fault-control and mutant
  numbers from committed run evidence, binding them to blob digests I recomputed. The claim is
  "each documented grading has a killing fault", not "check.py cannot be weakened": the H1–H3
  and H5–H7 mutants still survive.
- **C2 operability (8 → 8, sourced): improved.** I verified the controls and live receipts from
  committed evidence and re-opened its sources (S042, S044, S047) at the pinned bytes.
  **Trade ruling under the no-trade rule: no axis is harmed.** In the one failing run, the
  1/60 false failure under 32x CPU load observed **zero** 503s (`LiveUnderLoad.md`: "The
  failure captured **zero**"). v1 graded the loading envelope with nothing, so v1's pass in
  that state asserted nothing. v2 refuses to certify a property it did not observe, which is
  what KQ21 requires ("an unobserved state passes vacuously" is a reject criterion). No
  behaviour that was verified before regressed: v1 receipts stay `VALID`, the probe is
  unchanged, and the round-16 measure PASSes. The defect is the exit-code classification: zero
  observation should be could-not-evaluate (exit 2), not failed (exit 1). It is routed below
  (R4) and is also the lane's own planned item 1. Six v2 checks have no retained bad control,
  so C2 is admitted only on the four checks the controls flip, which is how the lane scopes
  it.

The driver lines, copied from `.ufo/watchdog.log` because the log is mutable:

```
2026-10-20T11:52:26-03:00 launch kama round=17 pgid=3049098 driver=hyaku-inline attempt=1
2026-10-20T16:35:17-03:00 complete kama round=17; hyaku-inline attempt=1
```

## 1. Step-1 conformance

| Check | Command | Observed | Result |
|---|---|---|---|
| Report landed by lane identity | `git -C /home/vgpnk/Projects/shokunin log --format='%an <%ae> %H %s' -- .ufo/reports/round-17/kama.md` | `kama-shokunin <kama@shokunin.local> 543437674dcef7939618cd29a08218724da77d0d round-17: kama report` | pass |
| `SHONEN` heading, one line per box | read report §SHONEN | 4 lines, all `[~]` with pointers | pass |
| Cited commits exist and are ancestors of `refs/heads/master` | `git cat-file -t H; git merge-base --is-ancestor H refs/heads/master` for cff9e62…, 54a29268…, 5e9ae6e9…, 54a2926, b8e485c, ccc4bb3 | all `commit`, all `anc=0` | pass |
| Content digests the report cites (these are not commits) | `git show REV:path \| sha256sum` | check.py at cff9e62 = `b853576e…` (frozen); at 54a2926 and 5e9ae6e = `ddc3f3cc…`; `tools/kama-probe.sh` = `36b64978…` at all three revisions; live tool cff9e62 `b8c5e8d4…` → 54a2926/5e9ae6e `0efd1723…`; gate `6b9576a1…` → `ad680179…` | match the run JSONs |
| Lane pushed, nothing uncommitted | `scripts/hyaku/jj-lane.sh state …`; `git status --porcelain`; `git ls-remote origin refs/heads/master` | `local=remote=5e9ae6e93dce529a48229647e482f18a291463cd ahead=0 behind=0 … tracked=0 untracked=0`; porcelain empty; remote `5e9ae6e9…` | pass |
| Prompt carries the template contract | `diff <(sed -n 1,140p .ufo/prompts/kama-round-17.md) templates/round-prompt.md` (fleet copy is `cmp`-identical to the kimi-shokunin one) | differs only at `{{LANE}}/{{ROUND}}/{{FLEET_ROOT}}/{{AXES}}`; §6 hyaku addendum follows line 140 | pass |
| Quoted L2 route map vs `MISSION.md` bucket | `MISSION.md:63-65` vs prompt lines 202-207 | MISSION puts connector in the heavy-reasoning bucket and critic/sentinel in economy. The addendum routes connector → m_flash and critic/sentinel → m_opus. No alias→bucket table exists to reconcile them. | defect (R8, orchestrator/protocol; not lane) |
| Evidence timestamps | `git log -2 --format='%H %cI %aI'`; receipts `started_utc` | receipts 15:57Z, before 54a2926 committed at 13:24:57-03:00 (16:24:57Z) | pass |

The 54a2926 *author* date (11:50:45-03:00) is earlier than the launch line (11:52:26). This
fits jj stamping the working-copy change when it was created. The committer date is the
landing time. Recorded as an observation, not a defect.

## 2. Per-claim re-check

**Separability.** Re-measured with
`git diff --name-status cff9e62 5e9ae6e`. C1 changes only `tests/probe-verdicts/check.py`,
`tests/probe-verdicts/fault-controls.py` and `.ufo/waves/round-17/c1/mutants.py`. C2 changes
only `tools/kama-llamacpp-live.py`, `tests/llamacpp-live/check-receipt.py` and
`tests/llamacpp-live/controls.py`. No file belongs to both claims, and the probe is
byte-identical. Separability holds by file set. Its falsify critic (`SeparabilityNoHarm`) died
on a 429, so this is the only outside check of it.

### C1 — calibration

Re-measured (plain commands over committed bytes):

- `git show cff9e62:tests/probe-verdicts/check.py | sed -n 340,347p`: before, the pass
  conjunct is verdict, reason, exit and drift. `served_model` is only copied into the record
  (lines 297, 337).
- `git show 5e9ae6e:…check.py | sed -n 474,484p`: after, the conjunct adds
  `and record["served_model_ok"]` and `and record["route_ok"] is not False`. Lines 280-284
  catch `UnicodeDecodeError` as malformed probe output, and line 462 records
  `malformed probe output: …` per row.
- `git show cff9e62:SKILL.md | sed -n 533p`: the old self-description "grades verdict,
  reason, exit and drift" is confirmed as the claim's starting point.
- Matrix bytes: `git diff --quiet cff9e62 5e9ae6e -- tests/probe-verdicts/*.json` exits 0. I
  recomputed the round-16 formula (sorted `name sha256` lines, then sha256) at both revisions:
  `bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32` both times. jq over
  the 9 files counts 72 rows.

Evidence-verified (lane detectors; this closure does not execute a sibling's gate):

- `jq` over `.ufo/waves/round-17/runs/fault-controls-{frozen,current}.json`:
  - frozen: `check_sha256` = `b853576e…`, accepted 3 (`F5:served_model`, `F6:route`,
    `F8:error`), detected 5, F0 positive control detected.
  - current: `check_sha256` = `ddc3f3cc…`, accepted 0, detected 8.
  - The `.exit` files read `exit=1` (frozen) and `exit=0` (current).
- `jq '.cells[].totals' runs/mutants-grid.json`:

  | check.py | Detector | Killed / applicable | Site missing |
  |---|---|---|---|
  | frozen | pair | 1/8 | 2 |
  | frozen | full | 7/8 (M8 survives) | 2 |
  | current | pair | 1/10 | 0 |
  | current | full | 10/10 | 0 |

  This matches the report: 7/8 → 10/10, and the pair detector kills only M9 (reject-all).
- Committed selftests:
  - `check.py --selftest`: `tests=72 passes=72 failures=0`, then `5/5`. The 5 are 4
    malformed tests plus the duplicate-name case, which the docstring describes correctly.
  - `noharm-r16-measure-clone.txt`: `result: PASS … measure exit=0`.
  - `noharm-test-snapshot.txt`: `RESULT pass=30 fail=0`.

Verdict: **improved**. The bound (H1–H3 and H5–H7 survive both detectors, and the
detector-of-detector survivors from `MutFaultControlsSelf`) is disclosed in the lesson
§Falsify wave and in SCORECARD.

### C2 — operability (sourced)

Evidence-verified:

- `jq` over `runs/controls-{frozen,current}.json`:
  - frozen (tool `b8c5e8d4…`, gate `6b9576a1…`): `accepted_bad=6 inconclusive=1`. K1, K2,
    K4, K5, K6 and K8 were accepted; K3 was inconclusive; K7 was rejected with no attribution.
  - current (tool `0efd1723…`, gate `ad680179…`): `accepted_bad=0 inconclusive=0
    gate_flip_bad=0 good_ok=true`. The failed checks per control:

    | Control | Failed checks |
    |---|---|
    | K1 | `health_ready` |
    | K2 | `loading_envelope_graded` |
    | K3 | `teardown_graceful`, `teardown_port_closed` |
    | K4–K6, K8 | `teardown_graceful` |
    | K7 | 3 checks, attributed `null` (setup error, untargeted, as corrected in the lesson) |

  - The union of flipped checks is {health_ready, loading_envelope_graded, teardown_graceful,
    teardown_port_closed}, which confirms "six v2 checks have no retained bad control" out of
    11.
- `jq` over `live/receipt-{1,2,3}.json`: each is `kama-llamacpp-live/v2` with `11/11` passed.
  `live/gate.txt` shows 3× `VALID`, probe and tool pins, and `run-exits.txt` shows 3× `exit=0`.
- `runs/selftest-check-receipt.txt`: "2 valid receipt(s) accepted; 39 mutations + unreadable
  case all rejected", exit 0. The report's 26 v1 + 13 v2 split is not printed separately, but
  the total matches.
- `runs/v1-receipts-current-gate.txt`: both round-16 v1 receipts are `VALID`, and the
  frozen-probe receipt still exits 1 against the current probe pin.
- `falsify/advice/LiveUnderLoad.md` (the trade evidence) gives 59/60 passes under load and a
  failing run with zero 503s captured, `setup_error null`, `internal_fault null`. Idle runs
  pass 11/11. My ruling is in §Decision above.

Sourced: S042, S044 and S047 were re-opened by this closure (§3), and all three agree.

Verdict: **improved**, admitted on the four control-flipped checks.

### No-harm

`git diff cff9e62 5e9ae6e -- SCORECARD.md` only appends §Round 17 and the falsify results.
No axis score moved: calibration 7, operability 8, freshness 8, depth 7, coverage 9,
adjacency 7.

`git diff --numstat` over `LOG.md SKILL.md SHONEN.md PROVINCE.md corpus README.md AGENTS.md
.gitignore` shows 0 deletions except:

- PROVINCE.md and SKILL.md, where the only deletion is the missing trailing newline;
- SHONEN.md, where box 2's pointer line was extended;
- AGENTS.md, where the round's own VCS line was corrected in the correction commit. AGENTS.md
  is not an append-only file.

`SOURCES.md` has no `-` lines from cff9e62 to 5e9ae6e, and from 54a2926 to 5e9ae6e it has 1
insertion and 0 deletions, so no row was edited in place.

| Axis | Verdict |
|---|---|
| calibration | improved |
| operability | improved |
| freshness | unchanged |
| depth | unchanged |
| coverage | unchanged |
| adjacency | unchanged |

## 3. Discernment spot-check (`corpus/lessons/round-17.md` `## Gate`)

| Item | Decision | Re-opened source | Agree? | Reason |
|---|---|---|---|---|
| `/health` 200 body is exactly `{"status":"ok"}` | admit (S042) | `raw.githubusercontent.com/ggml-org/llama.cpp/704366d7…/tools/server/server-context.cpp`, sha256 `dd1de0f2…` (= `sources/pins.json`) | agree | Line 5297 is `res->ok({{"status", "ok"}});` and line 5289 is `// error and loading states are handled by middleware`. `ok()` at 4868-4871 sets 200 and `safe_json_to_str`. The quote is verbatim and ≤25 words. |
| Negative returncode = death by signal N | admit (S044) | `docs.python.org/3.14/library/subprocess.html` (title "Python 3.14.8 documentation") | agree | §`Popen.returncode` contains "A negative value -N indicates that the child was terminated by signal N (POSIX only)." verbatim (14 words). The host runs `Python 3.14.8`. |
| First SIGTERM after install ends in `return 0` | admit (S043), superseded in-round by S047 | `server.cpp` sha256 `21439622…` and `server-queue.cpp` sha256 `168385b7…` at 704366d7 | **disagree with the build-time admit; agree with the S047 correction** | `terminate()` (132-136) sets `running = false`, and `start_loop()` sets `running = true` at 279. A signal handled before `start_loop` is therefore lost, and S043's unscoped claim overstates the code. The lane caught this itself (M8, S047), but M8 added no `QUALITY.md` criterion (R2). |
| Grade the README bytes `{"status": "ok" }` | reject | `tools/server/README.md` @ 704366d7, sha256 `714c067b…` | agree | Line 489 reads ``- Body: `{"status": "ok" }` ``, a spaced documentation form. The handler emits compact JSON, so a byte compare would fail a correct server. |
| Cite the `/3/` Python docs page | reject | `docs.python.org/3/library/subprocess.html` | agree | Its title is now "Python 3.15.0 documentation", while the host runs 3.14.8. |
| A newer llama.cpp build changed these surfaces | reject (checked) | `git ls-remote …llama.cpp refs/tags/b11757` = `13786fbb…`; raw files at `b11757` | agree | `server-context.cpp`, `server.cpp` and `server-http.cpp` hash `dd1de0f2…`, `21439622…` and `24ede172…`, identical to the 704366d7 pins. |

**Newly written `SOURCES.md` rows re-opened:**

- S042: the Gate quote is verbatim (above).
- S044: the quote is verbatim, 14 words.
- S047: the `teaches` cell matches the code (lines 132-136, 141-143, 278-280). But **S047 has
  no `## Gate` row** with URL, access date and a ≤25-word quote, which `CORPUS.md` §SOURCES
  rule 1 requires for every new row (R1).

**Census:** `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root
/home/vgpnk/Projects/shokunin kama` exits 0, with `W04 S031` and `W04 S043` (the shared
server.cpp URL, disclosed). Row counts recomputed by parsing both revisions:

| Count | cff9e62 | 5e9ae6e |
|---|---|---|
| Rows | 41 | 47 |
| Tier A | 38 | 44 |
| Tier C | 3 | 3 |
| mined | 31 | 37 |
| queued | 5 | 5 |
| rejected | 5 | 5 |

This matches the report.

## 4. Trend verdicts

- **expansion: unchanged** (agree with the lane). No new `knowledge/` file and no new
  coverage-map ground; README row 238 says "no new ground". No capability row was added.
- **quality: improved** (agree):
  - A stale reading (S043) was superseded by a stronger row (S047) within the round, with an
    appended correction in `knowledge/llamacpp-loading-lifecycle.md`.
  - The round-16 v1 limits were superseded by graded, controlled checks.
  - OPTIONS overstatements were corrected by appended text.
  - No admitted entry was found false and left unmarked. The one stale pointer is the
    README:238 coverage row (R3), which still cites S043 for exit statuses and does not
    mention S047. It is a map pointer, not a false entry.
- **discernment: improved** (this closure's outside judgment; the lane wrote `unchanged`
  pending outside review). The outside sample agrees with the gate on 2/2 sampled admits that
  stand (S042, S044) and on 3/3 rejects. The one gate error (the S043 admit) was caught,
  superseded and mined as a lesson inside the round. The missing criterion for it is routed
  as R2, not netted out.

## 5. Routed defects (lane owes next round unless noted)

1. **R1 — S047 Gate row missing.** `corpus/lessons/round-17.md` `## Gate` has no S047 row
   (URL, access date, ≤25-word quote with location). Search:
   `git grep -n S047 5e9ae6e -- corpus/lessons/round-17.md` finds only lines 224 and 309.
   Append one in the next lesson. Do not edit round 17's.
2. **R2 — M8 has no `QUALITY.md` criterion.** M8's captured-by says no criterion requires
   reading the whole control path (LEARNING.md step 3). Add a KQ citing round-17 M8, or state
   why not.
3. **R3 — the correction sweep missed one mention.** `corpus/README.md:238` attributes "the
   SIGINT/SIGTERM shutdown path and exit statuses" to S043 alone. Append a pointer to S047.
4. **R4 — C2 exit classification.** Zero observed 503s fails `loading_envelope_graded` with
   exit 1. It should be could-not-evaluate (exit 2). This is planned item 1 in SCORECARD.
5. **R5 — KQ21 coverage.** Retain bad controls for the six v2 checks (`models_alias_id`,
   `models_owned_by_llamacpp`, `metrics_not_enabled`, `props_alias`, `probe_model_ok`,
   `probe_mismatch`). Until then, do not count them as subject evidence.
6. **R6 — receipt-gate trust boundary (disclosed debt).** Outstanding items:
   - a receipt that self-declares v1 escapes the v2 predicates (`--require-schema v2`);
   - extra argv flags validate;
   - a non-exact 503 in `transitions` validates;
   - `::1` and IPv4-mapped listeners are not recognised as child-owned;
   - `BaseException` and epilogue faults escape without a receipt;
   - K6 accepts any nonzero exit;
   - `documented_by` still cites the `/3/` docs path.

   Handoffs advised to kagi (argv credentials) stay advisory.
7. **R7 — detectors of detectors and provenance.**
   - `fault-controls.py` survives F0 bypass, a shared F6 cache, and dropping the
     targeted-conjunct requirement.
   - `controls.py` survives dropping the gate-flip arm.
   - `sources-append-only.py` survives dropping the `opened` cell.
   - A refused task call records `refused: 0`.
   - Seven falsify seats died and were not respawned: `C1AdmissionCritic`,
     `C2AdmissionCritic`, `C2SourcedClaim`, `ControlsSafety`, `MistakesFailCapable`,
     `SeparabilityNoHarm`, `TrendVerdicts`. Their attacks remain undone; this closure
     covered only separability (by file set) and the sourced claim (by re-open).
8. **R8 — prompt route map vs `MISSION.md` buckets (orchestrator/protocol, not lane).** The
   §6 addendum's role→alias map routes connector to m_flash, while MISSION puts connector in
   the heavy-reasoning bucket. It routes critic and sentinel to m_opus, while MISSION puts
   them in economy. No published alias→bucket table reconciles the two.

Tool installs: none by this closure. The report's unattributed `uv tool` ruff 0.17.1 and
vulture 2.16 were disclosed by tameshi r17, one of its seats. They are not a kama install.

## 6. SHONEN note for the operator

All four boxes remain `[~]` and are not yet checkable by a non-author:

- Box 2 is a lane-owned live control, not consumer reconciliation.
- Box 3 still has no independent execution review.
- Boxes 1 and 4 are author assertions with no outside review of the round-17 SKILL rows or
  PROVINCE handoffs.

No promotion is implied.
