# ReviewScorecardCurrency — stale current-tense statements in SCORECARD.md

Seat: reviewer (read-only, leaf). Scope: `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md`
lines 1–60 and 120–135, checked against the round-11–15 supersession sections and
observed repo state at the round-16 build-wave start (2026-10-20, ~10:2x -03).

Method: reads, `md5sum`, `wc`, `grep`, `ss -ltn`, `systemctl --user`, `test -f`,
and the committed census receipt `.ufo/waves/round-16/sources-before-census.txt`.
No lane gate, harness, selftest or serving probe was executed; no file other than
this report was written; no tool was installed (tooling directive: nothing needed).

Authority used throughout: `../shokunin.conf:52` —
`kama|kama-shokunin|operability + calibration (local model serving and endpoint health)`.

## Findings, by severity

### F1 (high) — top "Current authority" block asserts the wrong axes and a frozen score ledger

`SCORECARD.md:6-7`: "Current authority (actual round 5, blocked attempt): assigned LIVE axes
remain operability and freshness". Contradicted by `../shokunin.conf:52` ("operability +
calibration") and by every round 11–15 header (e.g. `SCORECARD.md:399` "Current assignment
remains operability + calibration"; `SCORECARD.md:402` "historical, not current assignment
authority"). `SCORECARD.md:8` says "freshness is the lower inherited author assessment";
freshness is 8, calibration is the lower assigned axis (7). `SCORECARD.md:10` "no scalar
score is advanced" is stale: the §Erratum at `SCORECARD.md:211-214` advances freshness
7 → 8 and coverage 8 → 9 at round 10. The block is explicitly labelled *current*, so it
is the single most misleading current-tense statement in the file.

### F2 (high) — §Capabilities sources-registry row is four rounds behind, and the canonical table omits the round-14 capability

`SCORECARD.md:126`: "30 opened … (17 mined by 3 knowledge entries, 8 queued, 5 rejected";
pointer "(rows 30, …)". Observed: `34` registry rows, A=31/B=0/C=3, mined=24, queued=5,
rejected=5, missing=0, exit 0 (`.ufo/waves/round-16/sources-before-census.txt:1-14`);
`grep -c '^source: S[0-9]' corpus/knowledge/*.md` lists 5 knowledge files, not 3;
`grep -c '^- \*\*2026' corpus/SOURCES.md` = 7 search-log notes, not 3; the 4 study paths
in `corpus/SOURCES.md:48-53` are still 4. Also "census runs clean" vs validate
`corpus/SOURCES.md` W04 "S031 duplicate url" (intentional, exit 0 —
`.ufo/waves/round-16/sources-before-validate.txt:1`) — "clean" needs the W04 qualifier.
The canonical §Capabilities table (`SCORECARD.md:124-126`) carries only `sources-registry`;
the round-14 row `ollama-offline-evidence-replay` exists only inside the round section at
`SCORECARD.md:459`, so the contract table is incomplete (AXES.md §Capabilities requires the
single table; round 15 added none, so two rows is the correct current count).

### F3 (high) — §Saturation round line is a round-10 reading presented as current

`SCORECARD.md:132`: "Round 10: not saturated (depth/calibration/adjacency self-assessed 7),
nudge inactive." A capability entered the table in round 14 (`SCORECARD.md:459`,
first-working round 14), restarting the no-capability window; round 15 is 1 consecutive
round without one. The nudge is still inactive, but for a different reason than the text
gives: the precondition "When every axis the lane owns sits at or above the lane's saturation
line" (`../AXES.md:68`) fails because calibration is 7 < 8. The sentence therefore reports
the right status for a round that is five rounds old; it must be re-derived, not carried.

### F4 (medium) — §Planned is superseded five times and names a disowned axis

`SCORECARD.md:47-48`: "a fresh session remeasures the lowest LIVE axis and chooses the next
falsifiable freshness move" — freshness is no longer assigned, and rounds 11–15 already
remeasured. Each round 10–15 appends its own "Planned — supersedes earlier planned"
(`SCORECARD.md:270-272`, `:330-332`, `:364-366`, `:445-447`, `:539-542`), so the block at
`:45-55` is the oldest surviving plan, and its pointer "See `.ufo/round-5/continuation.md`"
(`:51`) is a round-5 artifact (file exists but is stale history, not the plan).
`SCORECARD.md:53-54` "no current serving context is available" needs a qualifier, not a
delete: round 16 C2 launches an ephemeral lane-owned llama-server, but no *registered*
consumer context exists (`registry/endpoint-consumers.tsv` has 3 rows, all DEAD), so the
blocked-feature statement survives round 16 only if it says "registered".

### F5 (medium) — §Axes rows mix superseded scores with present-tense evidence prose

- `:20` freshness `6 → 7`, "Last change round 3" — superseded by `:211` "freshness (LIVE) |
  **7 → 8**" (round 10). Same row's `RESULT pass=24 fail=0`: round 16 `SnapshotCompat`
  declares one added test case, so the count changes at integration — [INFERENCE] pending
  that item's landing.
- `:22` coverage `1 → 8`, "Last change round 1" — superseded by `:214` coverage 8 → 9,
  round 10.
- `:21` depth: "SKILL.md (323 lines: 12-row decision table, 11 verbatim error signatures,
  11 anti-patterns, 14-step checklist)". Observed 504 lines; decision table still 12 data
  rows, anti-patterns still 11 items, but the Checklist section now has 8 top-level steps,
  and rounds 11–15 appended further SKILL sections (`SKILL.md:347,376,388,411,438,478`),
  so the line/step counts are stale as a present file description.
- `:23` calibration: "runtime fixtures are explicitly parser evidence, not vLLM/Ollama
  integration" — as a *current* limit this is superseded by the round-14 offline replay
  capability (`:459`) and will be further qualified by C2's live llama.cpp harness.
- `:19` operability: "(shellcheck absent on this box)" is false now — `/usr/bin/shellcheck`
  exists; `md5 1f81e859…`/1092 lines is still byte-true at review time (`md5sum` matched,
  0755) but C1 changes it at integration, so this cell must not be read as post-round-16
  state.
- `:19` "live `check` → … drift=3 exit=2" is a round-3 observation; the only committed
  registry sample is `registry/history/latest.tsv` `20261014T124232Z` (3 rows, all
  `DEAD connection-refused`). No current `check` sample exists (and this seat must not run
  one); `ss -ltn` confirms no listener on 8080/34113, so the verdicts remain consistent,
  but the timestamp is 6 days old.

### F6 (medium) — "Why operability stops at 8 and freshness at 7" is a stale present-tense thesis

`SCORECARD.md:26`: "Why operability stops at 8 and freshness at 7" — freshness is 8 since
round 10. `:27-28` "the gate is verified against a real llama.cpp runtime only … comparison
is still **invocation-driven**. No clock runs `snapshot`" — the invocation-driven half is
still true (`systemctl --user list-timers --all` has no kama entry; `crontab -l` has none),
and the llama.cpp-only half stays true after C2 (C2 adds a second llama.cpp path, not a
second engine), but the sentence's headline and its roll-up of the 7s must be rewritten in
the append block rather than read as current.

### F7 (medium) — §Retired asserts the wrong assigned pair

`SCORECARD.md:59`: "None. Both assigned axes remain active" — the assigned pair is
operability + calibration; freshness is owned and scored 8 but is not assigned since round
11. The retirement evidence is still live and was re-sampled: `qwen-coder.service` is
`inactive` and its unit is `absent`; nothing listens on 34113. Record that as the round-16
sample, not as round 3's observation.

### F8 (low) — §Move log stops at round 9 while five measured rounds exist

`SCORECARD.md:66-76` last row is "| 9 (blocked dispatch) | — | — | — |". `LOG.md` carries
rounds 10–15 with measured entries (`LOG.md:516`, `:606`, `:702`, `:791`, `:854`, `:883`).
The table is append-only history, not a false claim, but as the file's own move ledger it
is incomplete by six rows.

### F9 (low) — report inventory sentence is stale

`SCORECARD.md:11`: "Historical reports exist for rounds 1, 2 and 4; round 3's report gap
remains unresolved." Fleet reports exist for rounds 1,2,4,6,7,8,9,10,11,12,13,14,15
(`test -f ../.ufo/reports/round-N/kama.md`); only rounds 3 and 5 are absent. The round-3
gap statement itself is correct and still worth keeping.

### F10 (low) — carried-debt unblock wording no longer matches host state

`SCORECARD.md:42`: "Unblock: operator restarts `qwen-coder.service` (or a successor unit)".
The unit is absent (not merely stopped), so "restarts" presumes a unit that is not
installed; `:43` "`model_ok=0` is ground truth" should carry the `20261014T124232Z` sample
date. The debt itself is real and round 16's ephemeral C2 server does not discharge it
(no registered port is served).

## Recommended append-only block

Append at EOF (after `SCORECARD.md:555`). It supersedes the *current-state reading* of the
top authority block, the §Axes last-change cells, the "Why … stops at" paragraph, §Planned,
§Retired's first sentence, §Move log's coverage, and the §Capabilities/§Saturation
denominators. It rewrites no historical line and advances no score; round-16 results stay
pending L1 measurement.

````markdown
## Current state (round 16) — append-only supersession of current-tense readings

Appended 2026-10-20 (round 16, hyaku phase 2 build wave). This block governs how the
blocks above are *read today*. It supersedes the current-state reading of the top
authority block (`:6-13`), the §Axes "Last change" cells and count prose, the
paragraph "Why operability stops at 8 and freshness at 7" (`:26-29`), §Planned
(`:45-55`), §Retired's "Both assigned axes" (`:59`), the §Move log's round coverage
(`:66-76`), and the §Capabilities and §Saturation denominators (`:126`, `:132`). It
rewrites no filed line and advances no score.

**Assignment authority.** `../shokunin.conf:52`: kama is
`operability + calibration (local model serving and endpoint health)`. `../MISSION.md`
calls its nine-lane YAML "Historical example — the upstream fleet's initial nine-lane
config, not the current roster", so its `kama … operability + freshness` row is not
authority. Operability 8 and calibration 7 are the assigned pair; calibration is lower.

**Axes as of round 15, all deltas 0 in rounds 11–15.** operability 8; calibration 7;
freshness 8 (round 10); depth 7; coverage 9 (round 10); adjacency 7. Freshness/coverage
evidence is the §Erratum above; the other four are unchanged since rounds 11–15. Round 16
declares C1 (calibration) and C2 (operability capability); neither is a measured score
move yet, and no scalar is advanced by this block.

**Outside admission.** Rounds 11, 12, 13, 14 and 15 each closed `status ok; admitted
true` — `corpus/lessons/round-11-verifier-spotcheck.md:9`, `round-12-…:5`, `round-13-…:10`,
`round-14-…:7`, `round-15-…:7`. No outside round admission is pending as of this append.
Round-15 admission covers only the declared duplicate-name guard and the fixed offline
corpus.

**Capabilities (canonical table; supersedes `:124-126` for current content).**

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| sources-registry | Curates where kama learns: 34 registered rows (24 mined, 5 queued, 5 rejected with reason + flip; A=31/B=0/C=3), 4 study paths, 7 search-log notes; census and validation exit 0 with the intentional W04 for S031 | `corpus/SOURCES.md`; `.ufo/waves/round-16/sources-before-census.txt`; `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin kama` | 10 |
| ollama-offline-evidence-replay | Reconcile caller-supplied tags/ps captures using exact names/digests and fail-closed remote/unknown/invalid classifications, with readiness always unknown | `python3 tools/kama-ollama-evidence.py --selftest`; `.ufo/waves/round-14/acceptance.json` | 14 |

Round-16 rows added by `ScribeSourcesRows` are pending L1's final census; do not fold a
pre-integration count into the row. No round-16 capability is claimed here; C2 enters the
repertoire only if L1 measures the live harness and its teardown proof.

**Saturation.** Line 8/10; stagnation window N = 4. A capability entered in round 14
(`ollama-offline-evidence-replay`), which restarted the no-capability window; round 15 is 1
consecutive round without one. The nudge remains inactive because `../AXES.md:68` requires
every owned axis at or above the line and calibration is 7 < 8. The round-10 sentence at
`:132` is a round-10 reading, not current.

**Observed endpoint state (2026-10-20, read-only).** `registry/history/latest.tsv` snapshot
`20261014T124232Z`: 3 rows, all `DEAD connection-refused`, `model_ok=0`. Nothing listens on
8080 or 34113; `qwen-coder.service` is inactive and its unit is absent. No kama timer or
crontab entry runs `snapshot`, so recording stays invocation-driven — a transition between
invocations is still invisible. Round-16 C2's server is ephemeral, lane-owned and bound to a
non-registered loopback port; it is not a registered consumer endpoint and is not service
restoration.

**Pointer freshness.** `tools/kama-probe.sh` md5 `1f81e859…` / 1092 lines was byte-true at
round-16 start and C1 changes it; cite the post-integration digest from the round-16 results,
never from `:19`. `tools/test-snapshot.sh` md5 `860f26ac…` and its `pass=24` line are
round-3/round-start pointers and move with `SnapshotCompat`. `shellcheck` is installed
(`/usr/bin/shellcheck`), so "shellcheck absent" at `:19` is no longer a fact. `DELTA.md` is
`registry/history/DELTA.md`.

**Planned (round 16, declared; supersedes `:45-55`).** C1 calibration: admit `MODEL_LOADING`
/ `llamacpp-loading` only for the exact 503 loading envelope (message `Loading model`, type
`unavailable_error`, code 503), with the stub matrix red on the frozen probe and green on the
repaired probe plus positive controls that defeat reject-all/loading-all. C2 operability
capability: `tools/kama-llamacpp-live.py` starts an ephemeral pinned llama.cpp, captures the
documented lifecycle surfaces, probes them and proves teardown. Neither is measured by this
block. After L1's measurement, choose the next move from observed serving-domain evidence,
not from bookkeeping; declared-vs-served context size remains blocked because no *registered*
serving context exists, and service restoration, scheduling and route changes stay
operator-owned.

**Retired / move log.** None retired. Operability + calibration are the active assigned axes;
freshness stays owned at 8 but unassigned. Rounds 10–15 moves are recorded in `LOG.md`
(`:516`, `:606`, `:702`, `:791`, `:854`, `:883`); the §Move log above is not extended here.
````

## Post-review observation (same session, build wave still running)

While this review was written, sibling executor items landed working-tree edits:
`git status --porcelain` now shows ` M tools/kama-probe.sh`, ` M tools/test-snapshot.sh`,
and untracked `tests/probe-verdicts/`, `tests/llamacpp-live/`. That makes the §Axes
`kama-probe.sh` md5/line-count and `test-snapshot.sh pass=24` pointers stale as current
state *already*, before any L1 integration, and reinforces F5: those cells must be
re-cited from the round-16 measurement, not from round 3.

## Limitations and verification gaps

- Registry `check` was not executed (L1 owns measurement); F5's "live check" point rests on
  the committed `latest.tsv` and `ss`, not a fresh probe run.
- `tools/kama-probe.sh` md5 and `test-snapshot.sh` md5 were true at review time; sibling
  executor items (`ProbeLoadingVerdict`, `SnapshotCompat`) were still in flight, so the
  post-integration digests and test counts are untested here — the block is written to force
  re-citation rather than guess.
- Round-16 sources may gain rows after this review; the 34/24/5/5 figures are the committed
  round-start baseline only.
- The recommended block is advice; placement, wording and any score language remain L1's
  decision, and only L1 may append it.
