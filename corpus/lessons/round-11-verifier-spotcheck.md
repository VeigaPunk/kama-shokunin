author: hyaku closure (non-author integrator, @m_strong)

# Kama round 11 — independent closure and discernment spot-check

Date: 2026-10-20 UTC. Reviewer: hyaku-closure, fresh orchestrator-dispatched
non-author session `CloseKamaR11`; read-only review seats `CalibrateCheck` and
`CoverageGateCheck` advised this closure, not the lane's authoring round.

**Decision: status ok; admitted true.** C1 calibration and C2 coverage verify
on the declared documentation/historical-provenance boundary. No owned axis
was harmed. This is not runtime validation, a new serving capability, a scalar
score increase, or promotion. Conformance/clarity defects are routed below.

## Revision and dispatch evidence

- Before: `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad`.
- Round after and freshly measured HEAD: `fe57cc8a01acba9b6d7ed20e11b4914dfb68d903`.
- Work commit: `3285cdf7a50481694a36c4425cf32c915ab5e5f0`.
- Fleet report: `.ufo/reports/round-11/kama.md`, committed by
  `kama-shokunin <kama@shokunin.local>` in
  `dff173077a887df99b458d6fa07f68a099d92e9d`.
- Closure instructions: fleet `.ufo/prompts/closure/kama-round-11.md`.
  Canonical PROTOCOL, its appendix, MISSION, AXES, CORPUS and LEARNING were read.

Copied dispatch/completion digest, corroborated against the mutable watchdog:

```text
2026-10-19T23:10:53-03:00 launch kama round=11 pgid=12514 driver=hyaku slot=1 attempt=1
2026-10-19T23:24:27-03:00 lane-dead-no-report kama round=11; retry same round (hyaku: headless attempt ended by operator directive to run in-session)
2026-10-20T00:41:08-03:00 launch kama round=11 pgid=288216 driver=hyaku-inline attempt=1
2026-10-20T00:59:51-03:00 complete kama round=11; hyaku-inline attempt=1
```

## Step-1 conformance

Commands used the absolute fleet/lane paths; abbreviated `git -C` targets
below refer to those same repositories.

| Check | Command / evidence | Observed result |
|---|---|---|
| Landed report and identity | `git -C <fleet> log --format='%an %H' -- .ufo/reports/round-11/kama.md`; final author/email/date inspection | `kama-shokunin dff173077a887df99b458d6fa07f68a099d92e9d`; report committed 00:59:36 -0300, after lane commits at 00:56:15 and 00:57:56 |
| Checkable report, not marker | Read report §§Work performed, Landed changes, Before → after measurements, Sources & frontier, Trend verdicts, SHONEN | Two claims, real commits and LOG pointers; four separate `[~]` SHONEN lines; no self-written `[x]` |
| Cited commits exist and remain ancestors | `git -C <lane> merge-base --is-ancestor <hash> HEAD` for before, work and after hashes above | All three exit 0 |
| Lane round work landed and pushed | `git -C <lane> status --porcelain`; `git -C <lane> rev-list --count @{u}..HEAD`; `git -C <lane> rev-parse HEAD` | Empty status; ahead count `0`; HEAD exactly the round-after hash before this verifier file was created |
| Lane commit identity | `git -C <lane> log --format='%an <%ae> %H %aI %cI' <before>..<after>` | Both round commits carry `kama-shokunin <kama@shokunin.local>` |
| Committed prompt fidelity | `git -C <fleet> ls-files --error-unmatch .ufo/prompts/kama-round-11.md`; render template placeholders and compare prefix | Tracked; prompt §§1–5 exactly equal rendered `templates/round-prompt.md`; fleet and canonical template bytes equal; §6 adds the hyaku contract |
| Axis authority | Fleet MISSION §Fleet shape, `shokunin.conf` kama row, SCORECARD §§Round 11 | Current assignment operability + calibration; calibration 7 is lowest assigned versus operability 8. Coverage is historically tracked, within province, and permitted as additional evidence-backed axis work |
| Swarm receipts | Committed build/review specs, dispatch files and spawn receipts under `.ufo/waves/round-11/` | Two validated 32-task dispatch payloads. Build receipt records 32 returned jobs. Review spawn is an asynchronous launch receipt, not a completion verdict; report/advisor artifacts provide the remaining record. L1 planner mapping is explicitly authorized by the prompt addendum/L0 answer |

The report discloses the aborted attempt and reuses its uncommitted work under
this same round. S031 first entering git in the continuation is consistent with
that disclosure, not evidence against inheritance. No live route/model policy
was changed or re-enacted by this closure.

## Fresh claim re-execution

Executed once from `/home/vgpnk/Projects/shokunin/kama-shokunin` while HEAD was
exactly the after revision:

```sh
python3 .ufo/waves/round-11/reproduce.py
```

Observed overall exit **0**, `ok: true`, `measured_commit:
fe57cc8a01acba9b6d7ed20e11b4914dfb68d903`, `frozen_digests_verified: 11`.
The runner actually invokes the following independent modes with the same
pinned baseline; outputs below are this closure's observations, not replayed
acceptance receipts:

```sh
python3 .ufo/waves/round-11/measure.py provenance --root .ufo/waves/round-11/frozen/before --baseline .ufo/waves/round-11/legacy-baseline.json
python3 .ufo/waves/round-11/measure.py provenance --root . --baseline .ufo/waves/round-11/legacy-baseline.json
python3 .ufo/waves/round-11/measure.py crosswalk --root .ufo/waves/round-11/frozen/before
python3 .ufo/waves/round-11/measure.py crosswalk --root .
python3 .ufo/waves/round-11/measure.py --selftest
```

| Measurement | Before / negative observation | After / expected observation |
|---|---|---|
| C1 provenance | 9 files, missing fields 27, prefix violations 0, exit 1 | 9 files, missing fields 0, prefix violations 0, exit 0; duplicate fields, missing headings and live-revalidation wording findings all 0 |
| C2 crosswalk metadata | Entry 0, absent trio/table, exit 1 | Entry 1, each provenance field 1, table present, exit 0; explicitly `existence/provenance only; no semantic admission` |
| Self-invocation | Isolated fixtures only | `selftest: 19/19 passed`, exit 0 |
| Missing-field isolated mutant | Remove one appended recheck field | Exit 1, `missing-field`, missing_fields 1 |
| Original-prefix isolated mutant | Flip one original byte | Exit 1, `prefix-mutation`, prefix_violations 1 |
| Baseline-byte isolated mutant | Append a space to a temporary baseline copy | Exit 2, `snapshot_tampered` |

The controls write temporary copies only. No endpoint/config/service probe,
fixture service harness, snapshot command or old provider instruction was run.
Neither claim declares capability acquisition or an exploratory claim.

### Checking frozen input correspondence, not only self-consistent digests

A separate read-only Python comparison fetched each original blob with
`git -C <lane> show 2f7303c242319c1dc96c6bcf7702ac18b3ca1aad:<relative-path>`
and compared SHA-256 with `frozen/expected.json`. All **nine knowledge blobs**
match their frozen copies and baseline digests. The current legacy byte prefixes
are preserved, as also checked by the runner and the calibration reviewer.
`git cat-file -e <before>:corpus/knowledge/served-identity-crosswalk.md` exits 128:
the actual before commit lacks that path, independently of the frozen tree.

**Auxiliary snapshot defect D1:** the frozen before SOURCES file is not an exact
copy of that commit. Actual SHA-256 is
`9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a`;
frozen SHA-256 is
`52665cf2d648112be2683c61485d42da1bf1dc859ea1df41d857672c60142fa1`.
The frozen search-log line 55 is truncated and its tail contains a tool display
marker referencing `artifact://1157`, unlike the committed source. The first
literal comparison accordingly failed on SOURCES, after the nine knowledge
comparisons passed. A green digest check proves integrity against the shipped
expected file, not correspondence with git history.

All registry rows are byte-identical between actual-before and frozen-before.
Independent parsing of actual `git show` bytes gives 30 rows, A=27/C=3,
mined=17/queued=8/rejected=5, matching the reported census. Thus D1 invalidates
the auxiliary exact-copy assertion, not the C1 denominator/prefix result, the
C2 actual-before absence or the before census numbers. An attempted census
`--file /dev/stdin` returned exit 2 (`--file not found`); its output is not counted
as a successful census. Actual-before counts above came from parsing the blob.

## Semantic review and per-axis verdicts

| Axis | Verdict | Evidence and scope |
|---|---|---|
| calibration | improved | Nine explicit supplements distinguish original dates from review dates, describe missing historical JSON honestly, and bound future rechecks. Actual source blob/prefix comparison and negative controls support the count. No 7→8 score conversion is claimed |
| coverage | improved | One documentation extension adds remote inventory, nullable loading and router-state distinctions beyond the prior tags/ps split. Crosswalk credits existing expiry, catalog and alias knowledge instead of recounting it |
| operability | unchanged | No existing `tools/` implementation, endpoint registry or probe expectations changed; new measurement tooling is evidence, not a newly claimed serving capability |
| freshness | unchanged | Metadata review is not live endpoint revalidation. Retained observations are expressly historical; no service restoration or present-health assertion is inferred |
| depth | unchanged | Additional sourced interpretation supports C2; no separate depth move is claimed |
| adjacency | unchanged | Crosswalk §Province handoff leaves routing, evaluation, credentials, web properties and host changes with their owners; PROVINCE unchanged |

The required `git diff <before> <after> -- SCORECARD.md` showed 61 additions,
no deletions: calibration 7→7 and coverage 9→9 are explicitly self-assessments,
not fabricated global numeric improvement. Changed domain files and sampled
supplements were read. In particular, snapshot rechecks name isolated history
roots and their writes; endpoint rechecks refuse obsolete config-body replay.

Adversarial review dispositions: the proposed stale-line defect at
`cross-lane-scope.md:47` is **not sustained**: its pre-existing correction A36
at line 77 explicitly names that recommendation as stale and points to the
current record. The proposed upstream-supersession defect is also **not
sustained as fact error**: S031 supersedes S011 in the lane registry, as required
by CORPUS, not in upstream documentation. Its locality consequence is a valid
inference from remote fields; wording can label that more explicitly (D4).
The dated undelivered seat plan is archival by the report's explicit ruling,
not current authorization (D5 requests a clearer in-file disclaimer).

## Outside discernment spot-check

Sources were independently reopened on 2026-10-20, not merely read from the
lane's archived scout receipts. Parent reopened Ollama tags and the exact pinned
llama.cpp README; the coverage reviewer additionally reopened pinned OpenAI and
Ollama compatibility sources.

| Item | Gate decision | Re-opened source | Agree/disagree | Reason |
|---|---|---|---|---|
| Served-identity crosswalk | admit, documentation-only | [llama.cpp README @c0fd7862](https://raw.githubusercontent.com/ggml-org/llama.cpp/c0fd78626405c6d9b934efef0ec7291fcc20e3d6/tools/server/README.md), §§GET `/v1/models`, GET `/models`, Sleeping on Idle; [Ollama tags](https://docs.ollama.com/api/tags), OpenAPI ModelSummary | agree | Nullable `meta` during loading, cache/router states and remote-origin fields support new distinctions; no local readiness certification follows |
| `/v1/models` match guarantees loaded weights/readiness | reject | Same pinned llama.cpp README, GET `/v1/models` and Sleeping on Idle | agree | The list always has one element while `meta` can be null during loading; exempt health/metadata requests need not reload sleeping weights |
| `/api/tags` membership proves local weights | reject | [Ollama tags](https://docs.ollama.com/api/tags), ModelSummary.remote_model and remote_host | agree | The documented remote fields defeat the universal locality inference; upstream still saying `locally available` in its summary does not erase those fields |
| Nine legacy supplements | admit, historical-provenance calibration only | Nine actual before blobs, retained cited paths, sampled endpoint-identity, served-model-identity and snapshot-history supplements | agree | Original bytes retained; historical versus review dates and unretained samples are distinguished; future commands require the stated authorization and scope |

New-row quote check: S031, lesson §Gate, URL
https://docs.ollama.com/api/tags, OpenAPI
`components.schemas.ModelSummary.properties.remote_model.description`:
**“Name of the upstream model, if the model is remote”** — located verbatim,
10 whitespace-delimited words, within the 25-word limit. `remote_host` likewise
names the upstream Ollama host. Tier A is appropriate for those documented
fields, not for installed-runtime behavior or independent corroboration of S011.

## Sources validation and trend verdicts

Executed:

```sh
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin kama
```

Both exit 0. Validation observed:

```text
kama W04 S031 duplicate url docs.ollama.com/api/tags across scopes
kama ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
```

Census observed 31 rows, A=28/B=0/C=3; mined=21/queued=5/rejected=5;
invalid tiers/statuses and missing registries all 0. W04 is a scoped
append-only correction sharing an existing URL, not an additional independent
source and not a waived validation failure.

- **expansion: improved.** One sourced, mined-row-backed knowledge extension
  covers the new remote/loading/router cases. Numeric entry growth alone was
  not used as semantic evidence.
- **quality: improved.** Historical records now explicitly delimit their
  evidence and safe recheck scope; fail-capable controls expose missing fields,
  original-byte mutation and baseline tampering. D1 is specifically marked here
  rather than silently treated as faithful history; its unaffected rows and
  actual before blobs independently preserve the claim comparisons.
- **discernment: improved.** Fresh outside sampling agrees on an admit and two
  substantive rejects. This supersedes the author's honest `unchanged pending
  outside sample` for closure, without editing the filed report or lesson.

## Routed defects and operator boundary

All items below are status-neutral; none changes the two verified claim deltas.
The next lane round must address its own defects by new corrections/evidence,
not rewrite this round's filed history.

1. **D1 → kama, snapshot fidelity:** add a byte-exact SOURCES snapshot produced
   directly from `git show <before>:corpus/SOURCES.md`, with a new pinned expected
   manifest and a comparison against the source commit. Append an erratum naming
   the old truncated snapshot; do not silently rewrite the old frozen receipt.
   Carry the actual-before versus frozen hashes above into the fix evidence.
2. **D2 → kama, registry navigation/date prose:** SOURCES.md:6–7 still says
   every row was opened in round 10, despite S031's round-11 date; its Paths
   section still calls the landed K02 crosswalk the `next entry`. Append a clear
   scope/navigation correction without changing immutable source-row cells.
3. **D3 → kama, criterion pointer:** SKILL.md:357 says admission remains
   KQ11–KQ13 although this round also adds and relies on KQ14. Append a precise
   pointer to the complete applicable QUALITY criteria rather than suggesting
   a reduced admission rule.
4. **D4 → kama, minor inference clarity:** label the S031 locality consequence
   and corresponding crosswalk remote-entry conclusion explicitly as inference,
   and clarify that `supersedes S011` is registry supersession, not a claimed
   upstream change. This is clarification, not rejection of the grounded caveat;
   preserve the append-only SOURCES cell contract.
5. **D5 → kama, archive clarity:** the newly committed undelivered
   `.ufo/round-10/SEAT-PROTOCOL.md` opens `binding on all 64 seats` without an
   in-file archival disclaimer. Make the report's historical/nonexecuted status
   unmistakable at that artifact before anyone reuses it; no old routing or
   host-inspection instruction is authorized by its preservation.
6. **Main/operator follow-through:** the lane disclosed three advisors initially
   writing fleet-root reports and routed their cleanup to Main. This closure
   makes no deletion or claim that cleanup ran; it never touches those files.

SHONEN remains four author-asserted boxes. This closure establishes reproducible
round-11 corpus work and bounded instructions, not a fresh end-to-end serving
execution; all four promotion boxes are **not newly certified** by this review.
No `[x]`, promotion, mint, lane-authored edit, host mutation or tool installation
was performed by this closure. Tools installed/updated: none.
