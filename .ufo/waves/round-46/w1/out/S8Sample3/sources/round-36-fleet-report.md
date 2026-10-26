# kama — round 36

author: Kimi fresh L1 (attempt 2; attempt 1's L1 died on a provider-route failure before committing anything)
date: 2026-10-24
lane tip (landed): `6a4afdfe48b0b54239d127761d21a5cf21b5b0ea`
claim measurement commit (landed): `2e8beda5b2a2dcc62d6782838ee6e47cda04df55`
base: `e5a8ececf3d60fd53b36bb74299693a29e8f74b6`
round shape: three v1 waves, 96 seats, 53 dead — see **Waves**

## Work performed

Round 36 declared **two** claims. Both were frozen before any seat scored, in
`.ufo/waves/round-36/preregistration.json`, by the attempt-1 L1; this attempt
kept the predicates, the counters and the do-nothing controls byte-for-byte and
re-measured them. The round worked the lane's lowest non-retired numeric axis
(calibration 7, tied with depth and adjacency) in C1, and coverage in C2.

- **C1 — calibration 7 → 7.** Four statements the round-35 closure routed are
  corrected by append only in `corpus/lessons/round-36.md`, and the counter
  re-derives each correction from committed bytes
  (`tools/round36-statement-audit.py`).
- **C2 — coverage 9 → 9.** The round-36 coverage block names
  `corpus/knowledge/sglang-native-route-deprecation.md`, that entry exists, and
  it cites registry ids that are present at the tip and absent at the base
  (`tools/round36-coverage-audit.py`).

Work items, each with its evidence pointer:

- Froze the claims, the counters and the failing do-nothing controls before
  any seat could score: `.ufo/waves/round-36/preregistration.json`,
  `.ufo/waves/round-36/controls/c1-noop.out` (`met False`, exit 1),
  `.ufo/waves/round-36/controls/c2-base.out` (`met False`, exit 1),
  `.ufo/waves/round-36/controls/c1-selftest.out`,
  `.ufo/waves/round-36/controls/c2-selftest.out` — landed at
  `9014843cb7de8fbe87a97954c13832b67d55f046` by the attempt-1 L1.
- Corrected the four routed r35 statements by append, without rewriting the
  r35 lesson or the r35 fleet report: `corpus/lessons/round-36.md` §Corrections
  (rows `R35-S211`, `R35-WORDS`, `R35-MIRROR`, `R35-KEEP`).
- Hand-checked all seven kama rows of the campaign absent-defect register
  myself, with direct fetches, and recorded a verdict, a reason and a flip
  condition per row: `corpus/lessons/round-36.md` §Gate quarantine table;
  slice receipt `.ufo/waves/round-36/assimilation/quarantine-slice`.
- Opened the two adopted sources myself and located each quote and line
  (`corpus/lessons/round-36.md` §Gate): the SGLang native-API page at tag
  v0.5.22 (HTTP 200, `get_model_info` twice, `/model_info` zero times, route
  list at line 9) and that tag's `http_server.py` (HTTP 200, deprecation
  warning at lines 790-791, route registrations at 786 and 796).
- Ran the id-collision check in scratch with the 0-3 leading-space pattern and
  proved the guard can see an indented row the column-zero pattern misses:
  `.ufo/waves/round-36/assimilation/guard/` (col0 collisions empty, space
  collisions `S002`); the live check found registry 201, staged 134, one
  collision (`S327`) — `.ufo/waves/round-36/assimilation/collisions`.
- Ran the validate-before-append gate and let it catch a real defect: the
  first mirror build failed with **E12 on both new rows** (appended at the end
  of `corpus/SOURCES.md` they fell outside the Registry section). The rows were
  re-placed inside the table and the gate then exited 0 with 93 pre-existing
  W04 warnings — `.ufo/waves/round-36/assimilation/validate-census.out`, last
  line `file ok`.
- Landed the two registry rows inside the Registry table and the coverage
  block in the map: `corpus/SOURCES.md` (S328, S329),
  `corpus/README.md` §Coverage map — round 36 addition.
- Mined one still-unimplemented `considerthese` proposal and grounded it by
  opening what it points at: `corpus/QUALITY.md` KQ45, from
  `considerthese/2026-10-24.md` proposal 2, grounded on the drift measured on
  S174, S192 and S193 (below). The operator's file was not edited.
- Repaired the C2 counter's selftest fixture, which had been built from the
  tip's README and entry and therefore reported `met True` for its "base" arm
  once the round landed: `tools/round36-coverage-audit.py` (both arms now load
  the BASE revision); `score()`, `PREDICATE`, `HEADING`, `ENTRY` and `BASE` are
  unchanged and the measurement line is byte-identical before and after.
- Swept the fleet root for misroots: `git -C /home/vgpnk/Projects/shokunin
  status --porcelain` lists 14 untracked paths, none of which names kama or
  round-36 (they are other lanes' fetch captures and driver state). Nothing was
  moved or deleted; wave-3 seats re-checked the same list independently
  (`.ufo/waves/round-36/w3/out/ExecSweep.md`,
  `.ufo/waves/round-36/w3/out/RevMisroot.md`).

## Landed changes

Both lane commits were produced by `scripts/hyaku/jj-lane.sh` and verified
against the lane remote; only the helper's `landed` lines are cited.

- `2e8beda5b2a2dcc62d6782838ee6e47cda04df55` — "round-36: claim work — r35
  routed corrections, published-vs-engine route entry, S328/S329, KQ45":
  `corpus/lessons/round-36.md`,
  `corpus/knowledge/sglang-native-route-deprecation.md`, `corpus/SOURCES.md`,
  `corpus/README.md`, `corpus/QUALITY.md`, `tools/round36-statement-audit.py`,
  `tools/round36-coverage-audit.py`, and the round's wave evidence under
  `.ufo/waves/round-36/`. Log entry: `LOG.md` §round 36.
- `6a4afdfe48b0b54239d127761d21a5cf21b5b0ea` — "round-36: SCORECARD and LOG
  rows, wave-3 evidence, C2 selftest fixture repair": `SCORECARD.md` §Round 36,
  `LOG.md` §round 36, `tools/round36-coverage-audit.py` (selftest fixture),
  and the wave-3 evidence and measurement receipts under
  `.ufo/waves/round-36/`. Log entry: `LOG.md` §round 36.

Files the helper skipped, deliberately: `.ufo/waves/round-36/w1/out/MutKeepTracked.md`
(1169902 bytes) and its two 1134872-byte scratch dumps, and
`.ufo/waves/round-36/w2/out/RevQ210/{follow,nofollow}.html` (1112304 bytes each)
— over 1 MiB inside named directories, skipped with a warning. The seat reports
that describe them are committed.

## Before → after measurements

Both counters are the frozen ones; both were re-run at the commit named.

- **C1 (calibration 7 → 7).** Command:
  `python3 tools/round36-statement-audit.py --repo . --tip <full-commit>`.
  Before, at base `e5a8ececf3d60fd53b36bb74299693a29e8f74b6`:
  `uncorrected 4 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met
  False` (exit 1). After, at `2e8beda5b2a2dcc62d6782838ee6e47cda04df55`:
  `uncorrected 0 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met
  True` (exit 0). Receipts: `.ufo/waves/round-36/controls/c1-noop.out`,
  `.ufo/waves/round-36/c1/after.out`. The selftest at the same tip prints
  `SELFTEST empty_met=False bad_met=False words=20 pass=1` (exit 0) —
  `.ufo/waves/round-36/c1/selftest.out`.
- **C2 (coverage 9 → 9).** Command:
  `python3 tools/round36-coverage-audit.py --repo . --tip <full-commit>`.
  Before, at base `e5a8ececf3d60fd53b36bb74299693a29e8f74b6`: `named 0
  file_exists 0 cited_new 0 met False` (exit 1). After, at
  `2e8beda5b2a2dcc62d6782838ee6e47cda04df55`: `named 1 file_exists 1 cited_new 1
  met True` (exit 0). Receipts: `.ufo/waves/round-36/controls/c2-base.out`,
  `.ufo/waves/round-36/c2/after.out`. The selftest at the same tip prints
  `SELFTEST base_met=False outside_met=False old_id_met=False pass=1` (exit 0)
  — `.ufo/waves/round-36/c2/selftest.out`.

The do-nothing controls were printed before any data and both fail their
targets; the counters are self-verifying, so the controls cannot reach the
target without the claimed work. No axis score moved: calibration 7 → 7,
coverage 9 → 9, operability 8, freshness 8, depth 7, adjacency 7.

## Sources & frontier

SOURCES rows before → after, counting command
`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`:
**201 → 203**. Rows added: **S328** (tier A, docs) and **S329** (tier A, code),
both `mined`, both opened 2026-10-24, recheck `90d`, both used by
`corpus/knowledge/sglang-native-route-deprecation.md`. Rows touched old → new:
**none** — no existing row was edited, and the r35 rows S327, S206 and S202 are
byte-unchanged. Frontier rows advanced: **one** — the coverage map gains
`knowledge/sglang-native-route-deprecation.md`
(`corpus/README.md` §Coverage map — round 36 addition).

Census, both runs at the lane root:
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root
/home/vgpnk/Projects/shokunin kama` — round start
(`.ufo/waves/round-36/census-start.out`) exits **0** and ends `kama ok`; round
end (`.ufo/waves/round-36/census-end.out`) exits **0** and ends `kama ok`.
Rows by tier at the tip: A 194, B 6, C 3. Status: mined 184, queued 8,
rejected 11.

**Assimilation decisions (one theme).** Theme: a published native route name
is not the engine's current route. From the read-only package
`/home/vgpnk/Projects/shokuknow/merge/kama/` (never written, never a campaign
tool run), one entry is admitted and two rows are appended; the rest are
refused with reasons and flip conditions in `corpus/lessons/round-36.md` §Gate.

- Admitted: `corpus/knowledge/sglang-native-route-deprecation.md`, citing the
  two rows this lane opened and located itself (S328, S329).
- Refused — `hosted-health-route-configuration.md`: a remote-platform
  deployment field (Google Cloud `serving_container_health_route`,
  `containerSpec.healthRoute`, `AIP_HEALTH_ROUTE`); remote endpoint health
  belongs to kake. Flip: a local container on this host whose configured health
  route differs from the engine route, observed by the lane's own probe.
- Refused — `sglang-native-api-deprecation-amendment-2026-10-23-r4.md` as a
  byte-copy: its staged rows cite campaign-provisional ids and anchor cells
  this round did not re-ground. The theme is adopted as a lane-written entry
  instead. Flip: a round that re-opens every anchor of that file may append it.
- Refused — staged rows S359, S360, S372 (the same `http_server.py` URL): one
  URL, one row. Flip: an admitted entry that needs the readiness, model-card
  or OpenAI-compatible reading of that file may add its own row.
- Refused — the staged `endpoint-health-probe-conventions.md` as a byte-copy:
  it cites S331-S334, which this round did not open. Flip: re-open those four
  and admit only the sentences whose quotes locate.
- Quarantine, hand-checked this round with direct fetches: **S202 present, not
  appended** (the span is on the Compose page; no admitted entry cites it);
  **S206 present, not appended** (the span is on the Alibaba Cloud PAI page,
  and the material is a hosted platform, out of province); **S230 present,
  covered by the lane's own S329 row** (same URL and anchor; a second row would
  duplicate the URL); **S200 absent** (the quoted cell is not on the arXiv
  page); **S210 absent** (the quoted cell `Page Not Found` is not on the
  page, which is reachable and carries `sglang.launch_server`); **S211
  absent** (the page is reachable and the token `still-live` occurs nowhere in
  it); **S224 quote not located** (`check_health` is present, `render-only` and
  `always return 200` are not). No register row is appended and the register
  was not edited.
- Id collision: registry 201, staged 134 (S325 to S458), collisions 1 (S327 —
  the same document the lane already holds, so it is neither re-appended nor
  renumbered). The adopted ids follow the lane's registry (S328, S329); no
  adopted row re-points a staged citation by arithmetic.

## Trend verdicts

- **expansion — improved.** One new coverage-map entry on ground the lane did
  not hold: at tag v0.5.22 the published SGLang native-API page still lists
  `/get_model_info` while the same tag's server source warns in the handler
  that the route is deprecated and names `/model_info` as the replacement
  (`corpus/knowledge/sglang-native-route-deprecation.md`, S328, S329). The
  lane's matrix records which route answers what but not that the documented
  route is one the engine itself deprecates. Bounded: a documentation-and-source
  reading of one tag, not a live server sample.
- **quality — improved.** Four statements the round-35 closure routed now
  carry append-only corrections the counter re-derives from committed bytes,
  and the r35 lesson blob and the r35 fleet report blob are unchanged — the
  filed report was not rewritten. The do-nothing control still fails. The
  validate-before-append gate caught a real defect (E12 on both new rows)
  before the append reached the registry, and the counter's own selftest had a
  tip-relative fixture that was repaired so it reads a base state at any tip.
  One cost is recorded honestly: the S211 reason was wrong, and the correction
  is an appended row rather than a fix to the file that carried the wrong
  reason.
- **discernment — improved.** The lane's own hand-check separated three
  different verdicts the register's single `payload-absent` class cannot
  distinguish — present (S202, S206, S230), absent (S200, S210, S211) and
  quote-not-located (S224) — and it refused to adopt a row that located only
  because the lane had no admitted entry citing it. The considerthese
  proposal was mined by opening what it points at: the drift on S174 (the live
  manual reads "in the given file"; the row's verbatim quote reads "in the
  file"), S193 (the committed gate docstring reads ``registered`` with markup;
  the row's quote drops it) and S192 (the quoted sentence is absent from the
  fetched bytes of a client-rendered page, so it is unverifiable-by-fetch, not
  drift) — measured here, not copied from the reflection.

## SHONEN

- [~] SKILL.md contains real decision tables, error patterns, checklists, cited
  sources → `SKILL.md` §§Decision table, Error signatures, Checklist;
  `corpus/knowledge/sglang-native-route-deprecation.md` adds one cited route
  decision for this round. Author assertion; no named non-author verifier, so
  this is not a promotion-checkable box.
- [~] At least one end-to-end domain task executed and logged in LOG.md →
  `LOG.md` §round 36 records the executed corpus-census gate, both frozen
  counters and the three wave dispatches; `.ufo/waves/round-36/census-end.out`
  (exit 0) and `.ufo/waves/round-36/c1/after.out`, `c2/after.out` (exit 0).
  Author assertion; no named non-author verifier.
- [~] Instructions executable by an agent without oral context →
  `SKILL.md` §Checklist, `corpus/knowledge/snapshot-history.md` §Run it, and
  the round's own runnable receipts under `.ufo/waves/round-36/`. Author
  assertion; independent execution review remains open.
- [~] No cross-domain bleed (PROVINCE.md still accurate) →
  `PROVINCE.md` §Write boundary, `corpus/knowledge/cross-lane-scope.md`; the
  staged hosted-platform entry was refused as out of province and the
  sibling-overlap question was re-checked by two connector seats
  (`.ufo/waves/round-36/w2/out/ConnScope.md`,
  `.ufo/waves/round-36/w3/out/ConnScope2.md`). Author assertion; no
  non-author verifier.

## Waves

Three v1 waves, 96 seats total, 53 dead. Every wave was validated under
`scripts/hyaku/ufo-wave-policy.json` (band 32-64) and dispatched as one
batched call; the transport was `kimi -p` without `--auto`, because this L1
has no AgentSwarm tool. The seat grant was taken immediately before each wave
with `scripts/hyaku/wave-slot.sh acquire` and released only after settlement.

| Wave | Seats | exited 0 | dead | attack roles | role mix |
|---|---|---|---|---|---|
| w1 (inherited from attempt 1) | 32 | 14 | 18 (provider 403) | 12 | scout 11, reviewer 5, executor 4, mutation-tester 4, critic 3, scribe 3, connector 1, revenger 1 |
| w2 (falsify the frozen claims) | 32 | 3 | 29 (killed at the 480 s seat bound) | 18 | reviewer 10, executor 5, revenger 4, critic 4, mutation-tester 4, scribe 3, connector 1, scout 1 |
| w3 (falsify the landed draft bytes) | 32 | 24 | 6 (killed at the 900 s seat bound) | 22 | reviewer 17, executor 3, mutation-tester 3, revenger 2, critic 2, scribe 2, connector 1, scout 1, sentinel 1 |

Round total 96 seats, attack roles 52 (54%). Dead seats, with their last
error text, stay in the evidence: w1's 18 seats all exited `rc=1` with
`provider.auth_error: 403 "You have run out of credits or need a Grok
subscription"` — the same provider-route failure that killed the attempt-1 L1,
and the reason this round is attempt 2; 20 of w1's 32 report files are stdout
transcripts, not seat-written reports. w2's 29 seats were killed by the L1's
own 480 s seat bound (`rc=143`), which was too short for the working route —
w3 was dispatched with a 900 s bound and 24 of 32 seats finished. w3's dead
seats: `CritC1Sound`, `MutLessonRow`, `MutRowPipe`, `ExecCounters`,
`ScribeQual`, `SentFinal`. No timed-out seat was replaced. The canonical
planner seat was held by this L1, as the orchestrator ruling requires; a
bounded planning data-walk rode the connector and scout items. Seats never
mutated the fleet repo, a sibling lane, the lane jj state or the lane Git
index — with one exception, recorded next.

## Round-35 repairs

1. **S211 reason.** The r35 lesson records the row as unreachable; that reason
   is false and is **not** restated. The r35 lesson was not rewritten. The
   correction is the appended row `R35-S211` in `corpus/lessons/round-36.md`:
   the closure spot-check records HEAD 200 for the same URL
   (`corpus/lessons/round-35-verifier-spotcheck.md:95,118`), this round's own
   fetch returned HTTP 200, and the seat report records a successful fetch with
   the token `still-live` absent from the page. S211 stays unappended: no
   located quote exists for it.
2. **Word count.** The S327 quote is **20 words**, not the 18 its paragraph
   records — re-derived three ways from the committed lesson blob
   `428f1f8a0e8871022f7c1e8ea47e50ba5a8d6412` (whitespace split, `wc -w`, and
   the counter's own extractor). Corrected by the appended row `R35-WORDS`; the
   r35 lesson is not rewritten. The quote itself is unchanged and still inside
   the 25-word bound.
3. **Seven leftovers, classified and not swept.** Three post-commit seat-log
   flushes (`.ufo/waves/round-35/w1/out/ConnSibling/seat.log`,
   `.../ExecDisposition/seat.log`, `.../ScoutCoverageAbsence/seat.log`), one
   report overwrite (`.ufo/waves/round-35/w1/out/ExecDisposition.md`, whose
   working-tree copy replaces the committed 1994-line thinking dump — **not
   committed**), one mixed mirror (`.ufo/waves/round-35/assimilation/validate/`,
   11 symlinks and 84 regular files including a recursive `.ufo` link — **not
   committed**), and two helper-skipped files of 1066624 bytes each
   (`.ufo/waves/round-35/w1/out/ScribeGate/fetch/docker-dockerfile.html` and
   `.../dockerfile.html`) — **left unforced**; over 1 MiB inside a named
   directory they are skipped by the helper, and this round did not force them
   in. The appended row `R35-KEEP` names all seven with their classes.
4. **MISSION.md.** Not edited and not duplicated: the r35 L0
   (`kama | round-35 | MISSION.md:29 still says operability + freshness …`) is
   still open, and this round names the conflict without re-filing it.
5. **The mirror description.** The r35 report calls the validate tree a
   symlink tree; it is a mixed mirror. The r35 report is not rewritten; the
   correction is the appended row `R35-MIRROR`. This round's own mirror is a
   plain copy, and the lesson says so.
6. **The S211 and word-count disagreements** were also carried into the round's
   own wave: `ReviewS211` and `ReviewWordCount` in
   `.ufo/waves/round-36/w1/out/` reached the same two conclusions, and wave 3
   re-derived them against the landed bytes (`RevLessonGate`,
   `RevLessonQuotes`).

## Deviations and incidents, recorded

1. **A seat parked the lane's jj working copy.** The wave-3 mutation-tester
   seat ran `jj commit` inside the lane repo instead of its sandbox clone, and
   left the working copy on three foreign-identity commits
   (`28a8bf50` "baseline", `10094ed1b9eb` "mut1", `f3517a161e97` "mut2",
   author `MutLessonRow sandbox <sandbox@mut.invalid>`). `jj-lane.sh commit`
   refuses a non-empty working copy on a non-tip base by design, and
   `jj-lane.sh recover` needs a candidate that is both a direct child of the
   tip and the working copy's direct parent — no commit in the chain is both.
   The claim work was therefore committed and pushed **through
   `jj-lane.sh`** in a scratch clone of the lane remote, and the lane's own
   branch was advanced by `jj-lane.sh push`, which printed
   `landed 6a4afdfe48b0b54239d127761d21a5cf21b5b0ea`. One deviation from the
   letter of the lane rules: a single `jj git fetch --remote origin` was run in
   the lane so the local repo could see the moved remote tip — it is the exact
   command the helper itself runs inside `recover_remote_move`, it creates no
   commit, it touches no index entry, and the three foreign commits were never
   pushed and are not ancestors of the branch tip. The lane's working copy is
   still parked on them; that is filed as an L0 question, along with a
   request for a mechanical guard against seat-side VCS mutations.
2. **The attempt-1 L1's wave-1 report files are transcript dumps.** 20 of the
   32 are stdout, not seat-written reports, because the seats whose agent card
   carries no Write tool could not write their own file. They are committed as
   the evidence they are, and no killed seat is credited as a finished one.
3. **The C2 selftest fixture was tip-relative** and was repaired after the
   round landed; the measurement is unchanged and both selftest arms now read
   the BASE revision. The repair is a separate commit, after the claim commit,
   so the claim's measurement is read at a commit whose counter bytes are the
   frozen ones.

## Stale-lane

Stale-lane: none. This is a respawn-per-round driver lane; no other mission
of kama is open, and no round other than 36 was started.

## Tool installs

None. No tool was installed or upgraded this round, so no tool, version or
channel is recorded. The pacman guard (all pacman transactions paused
host-wide) was carried in every wave context and no seat ran pacman.

## Erratum — the parked chain grew after the first description

The deviation section above named three foreign-identity commits on the lane's
parked working copy. When the round was verified at the final lane tip the
chain was five commits deep, because the same wave-3 seat kept committing in
the lane repo as it worked:

    tip 6a4afdfe48b0
      -> 28a8bf50  "baseline: round-36 draft lesson bytes (sandbox only)"
      -> 10094ed1b9eb  "mut1: delete R35-WORDS correction row (sandbox only)"
      -> f3517a161e97  "mut2: one-word change 20->19 in R35-WORDS row (sandbox only)"
      -> f3bdcd036878  "mut3: unchecked word change in R35-WORDS row (sandbox only)"
      -> 873c5d7774b9  "mut4: corrupt cited blob hash in R35-WORDS row (sandbox only)"
      -> 6ae4da76c9ff  @ (lane identity, empty description)

All four mut commits carry the foreign identity
`MutLessonRow sandbox <sandbox@mut.invalid>`; none of them is an ancestor of
the branch tip and none was pushed. The seat's own working-tree mutations were
reverted by the seat before it exited, and the committed bytes are the correct
ones: the counter re-measures `met True` at the final lane tip
`6a4afdfe48b0b54239d127761d21a5cf21b5b0ea`, and the committed blobs of the
four tracked round-35 paths are byte-identical to their round-35 values
(`ExecDisposition.md` is still `9307c5d61c1942857a17cb259b4313460b37d0da`), so
the overwrite, the three seat-log flushes, the mixed mirror and the two
helper-skipped HTML files all remain uncommitted exactly as the round-35
closure required. The lane's working copy is still parked on this chain; the
L0 question filed with this report stands, with the corrected chain depth.
