# kama round 79 — lesson

author: kama SC03Lesson (scribe seat, round 79 wave 1)

Lane: kama. Round 79, one v1 build-and-attack wave of 14 seats (4 executor, 3 scribe, 2 scout,
1 connector, 1 reviewer, 2 critic, 1 mutation-tester; attack 4/14) under `ufo-wave-policy.json`
band 8-16. Base: `ee53f1a25eab93a8ab55bbb877e49e2e731df535`. Freeze commit:
`331037039c30909aa2163b2d1de22a7964f90420`, the commit adding `plans/round-79-claims.md` and
the C1 counter; this lesson treats the plan's blockquote predicates, fact value strings and
target lines as frozen text and does not edit the plan. Sealed revision C1 grades (round 78's
tip): `7a3cd98243b69fcbee0cc9e31878782bd8459320`. Assigned axes: operability + calibration; C1
works calibration (7), the lowest assigned score, which sits below the saturation line (8/10),
so the stagnation nudge is inactive. Lane tip at this scribe cut, read as the plan directs with
`git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master` (git HEAD is detached, so
a HEAD-based read is not a tip read): `f7442dea53bd8f474293a2252437b5d869801f49`.

This is a source-and-receipt account at the scribe cut, not a claim that unexecuted counters
passed. At the cut `tools/round79-selfrecord-round78.py` (the C1 counter) is present in the
tree; `tools/round79-unregistered-census.py` (C3's counter) is not yet landed;
`tools/pre-report-gate.py` still carries the base nine-arm order (`BASE_ARM_ORDER 9
['selfdesc', 'newest-closure', 'receipt-audit', 'worktree-landing', 'round-scope', 'round-clean',
'round74-v2', 'round75-instruments', 'round77-instruments']`,
`.ufo/waves/round-79/measured/before/c2-gate-arms.out`), and `tools/kama-probe.sh listeners`
still has no `registered` column. The pre-freeze receipts quoted below are the L1's; this seat
re-read them and did not rerun them.

## The round's three claims

- **C1 — calibration.** `python3 tools/round79-selfrecord-round78.py --repo <lane>` must print
  one `SELFRECORD_R78 claims=6 mismatches=0 corrected=2 unbacked=0` line and exit 0 only when
  each of the six facts the round-78 self-record declares re-derives from the tree at the sealed
  revision `7a3cd98243b69fcbee0cc9e31878782bd8459320`, or is answered by exactly one committed
  correction block at that revision whose stated new value re-derives at the tip; it exits 1
  naming every unanswered fact otherwise. The six facts: lowest assigned axis (F1), population
  (F2), wave shape (F3), wave dead seats (F4), tip accounting (F5), pre-correction run (F6).
  Before: `SELRECORD_R78_ENUM claims=6 stale=2 corrected=0`, exit 1
  (`.ufo/waves/round-79/measured/before/c1-enum.out`); the do-nothing control is the same
  counter on the same sealed tree with no correction blocks at the tip, `SELRECORD_R78 claims=6
  mismatches=2 corrected=0 unbacked=0`, exit 1
  (`.ufo/waves/round-79/measured/before/c1-score-nocorrections.out`, F5 and F6 stale). Allowed
  to claim: each of those six declared facts re-derives, or is answered by one valid correction.
  Not allowed to claim: that the round-78 record was true beyond those six facts, that the six
  facts are all the record asserts, or that a correction repairs anything beyond the named
  fact's re-derivation. Two blocks for one fact answer nothing; a 41-character `at` token
  answers nothing (the round-78 `unresolvable-cited-hash` class).
- **C2 — operability.** `python3 tools/pre-report-gate.py --selftest` must print
  `PRE_REPORT_SELFTEST pass=26 fail=0`, and a scored run at the round-79 tip must print
  `PRE_REPORT round=79 arms=10 failed=0 uncommitted=0` and exit 0, only when the tenth arm
  `round78-instruments` runs `round78-selfrecord-round77.py --selftest`,
  `round78-append-registers.py --selftest` and `round78-live-reconcile.py --selftest`, each
  exiting 0 with its own `*_SELFTEST pass=N fail=0` summary; a red, malformed or absent
  instrument must fail the arm closed naming it, and the `SKILL.md` pre-report-gate registry row
  must name `round78-instruments` and the new tally in the same commit. The arm count is derived
  from `ARM_ORDER`, never restated independently (KQ123). Before: nine arms,
  `PRE_REPORT_SELFTEST pass=22 fail=0`
  (`.ufo/waves/round-79/measured/before/c2-gate-arms.out`, `c2-gate-selftest.out`). Allowed to
  claim: the gate composes the three round-78 instruments as its own arm and fails closed
  without them. Not allowed to claim: that the instruments are claim-grade beyond their own
  selftests, or that this seat ran the scored gate (the L1 does).
- **C3 — coverage.** `python3 tools/round79-unregistered-census.py --repo <lane>` must print one
  `UNREGISTERED_CENSUS port=<p> unregistered=1 governed=1 class_missing=0` line and exit 0 only
  when `bash tools/kama-probe.sh listeners` reports the lane-owned llama.cpp fixture, serving on
  an unregistered loopback port, as `registered=no` under a registry that does not declare that
  port and as `registered=yes` under one that does, the summary's `unregistered`/`governed`
  counts move with the class, and a probe without the class is `class_missing=1` with exit 1.
  Before: no `registered` column and no `governed`/`unregistered` summary keys; the live host
  reads `probed=33 model_endpoints=7 foreign_service=24 unauthorized_service=0 dead=2 not_http=0
  model_loading=0`, exit 0 (`.ufo/waves/round-79/measured/before/c3-listeners-base.out`), with
  no registry relation; round 78 recorded one such listener (`127.0.0.1:1234`, four LFM3 ids) as
  a manual observation only. Allowed to claim: a serving listener the registry does not govern
  is its own census class and moves the summary counts. Not allowed to claim: a loaded model,
  consumer readiness, or that a registry row was admitted — consumer pins are operator-owned and
  the live-host leg is informational, never a gate.

## Gate

- **External candidate, opened and decided this round — admit.** llama.cpp router `GET /models`,
  URL
  `https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/tools/server/README.md`
  (`tools/server/README.md` at commit `39febd2adb947b70da35e95f9351b3bf58ad170a`, the build the
  live listener runs), access date **2026-11-04**. Opened live by this seat and independently by
  the sources and scout seats this round: `curl -fsSL`, exit 0, HTTP 200, 135608 bytes, sha256
  `8fd5abde2fb52de3b30f30a170631d4c0d92febecc8da44d0541e48b132b35c6`, byte-identical to the
  pre-freeze receipt (`.ufo/waves/round-79/measured/before/source-router-models.out`) and to the
  local build tree `/home/vgpnk/src/llama.cpp` at the same commit (scout receipt
  `.ufo/waves/round-79/w1/SCT02Source/source-check.md` §0). Located quote, **16 words**: "If a
  model is not running, it will be added or updated according to the source" — line 2227, the
  second sub-bullet of note 1 under `## Using multiple models` → `### GET /models: List
  available models` (heading 2197). Scope: the router's model list is an inventory, not a
  readiness claim — built on line 2199 ("Listing all models in cache. The model metadata will
  also include a field to indicate the status of the model:"), the `status.value` vocabulary in
  the same section (`loaded` 2287, `loading` 2271, `unloaded` 2265/2278, `sleeping` 2294,
  `downloading` 2303, `incomplete` 2319 — six values, not four), and line 2230 ("does not load
  the model, download files, or run inference"). Not the direct-server `/v1/models` body
  (S001/S035), not `/v1/completions` (S526), not the live probe verdicts. Precision note carried
  from the scout: line 2227's literal subject is the `?reload=1` refresh, so the "unloaded models
  are listed" half rests on 2199 plus the non-loaded examples, not on 2227 alone. No
  `corpus/SOURCES.md` row holds this pinned URL or this surface at this cut; tier and the row
  append are the sources seat's and the L1's call.
- **Rejected candidate (same-surface duplicate), checked this round — reject.** Re-rowing the
  llama.cpp server README at a pinned commit for surfaces the registry already holds with the
  same file: the master README's route inventory `/health`, direct `/v1/models`, `/metrics`
  (S001, `corpus/SOURCES.md:13`) and the b11755 README's `/v1/completions` request surface
  (S526, `corpus/SOURCES.md:278`), with S035/S112/S134 (`/health`, context/KV, `/props`,
  `/slots`, `/metrics`) and S494 (`/tokenize`, `/detokenize`) holding this file at other pins.
  Reason: same file, same surfaces, no new anchor — a third row would duplicate scope, the
  ruling round 77's L1 applied to S549 against S073/S085/S093 and the one the round-79 plan
  applies here ("the `llama.cpp` server README already held by S001 and S526 is not re-rowed for
  the same surface"). A new pin is not by itself a new surface: S035/S112/S134/S494/S526 already
  re-read this file at pinned commits for their own surfaces. **Flip:** the router-mode
  `GET /models` section (2197-2338) with its `status.value` object — an anchor none of those rows
  names — is exactly what reopens the URL; if the pinned README lacked that section, or a held
  row already anchored it, the row stays rejected.
- **Own-work instrument class (the round's own).** The round's own-work candidate is the census
  class C3 adds: `tools/kama-probe.sh listeners` gains a `registered` column (`yes`/`no`/`-`)
  and the `governed`/`unregistered` summary keys, and `tools/round79-unregistered-census.py`
  scores the class against two scratch registries. This is an instrument class, not a package
  entry and not a verdict: it rests on the admitted upstream row above for the
  inventory-not-readiness doctrine and on the lane's round-78 live observation
  (`.ufo/waves/round-78/measured/observation/unregistered-1234.out` — `127.0.0.1:1234`, a
  llama.cpp router serving four LFM3 ids), and no registry row is admitted. At this cut the base
  probe carries no class column (summary in
  `.ufo/waves/round-79/measured/before/c3-listeners-base.out`) and the counter module is not yet
  landed; this note records the class, not a run. Bound: the seven-verdict vocabulary
  (`MODEL_OK` / `MODEL_MISMATCH` / `FOREIGN_SERVICE` / `UNAUTHORIZED_SERVICE` / `DEAD` /
  `NOT_HTTP` / `MODEL_LOADING`) is unchanged, a `status.value` is never read as consumer health,
  and the live-host leg is informational, never a gate.

## Mistakes

1. **`stale-premise`** — a record that calls an ancestor revision "the tip".

   Round 78's §Gate and tip state says "The tip accounting is the round-77 counter, which is
   green at `rev=22cce544`" (`SCORECARD.md:4538`, §Round 78 §Gate and tip state), and the
   round's quality trend repeats "the gate is green at the final tip". At the sealed revision
   the token resolves to `22cce544b23670984fa9e42bea673d603881aae7`, an ancestor of that
   revision's own tip: `git rev-parse 22cce544` → that commit; `git merge-base --is-ancestor
   22cce544 7a3cd98243b69fcbee0cc9e31878782bd8459320` exit 0; `git rev-list --count
   22cce544..7a3cd98243b69fcbee0cc9e31878782bd8459320` → 6. The same round's gate receipt
   measured `rev=2842ad29`, five commits before the tip, and the tip-accounting sentence's
   `events=250 … exempt=60` line has no committed receipt — recorded by the round-78 verifier
   spot-check as §1 defect 1 (`corpus/lessons/round-78-verifier-spotcheck.md:30-34`).

   *Class judgment:* `stale-premise`, not `number-drift`. The revision token is not a
   mis-transcription: it resolves, it is the revision the round-77 counter was actually run at,
   and the record's own arithmetic is intact. What failed is the relational premise
   `is-tip:true` — true only of the tip itself and false of this revision at the record's own
   cut. `number-drift` would require the value to disagree with the measurement it reports;
   here the value agrees and only the label drifts.

   *Captured by:* the new F5 fact, which reads exactly that sentence and derives
   `tip-accounting=rev:22cce544/is-tip:false` at the sealed revision
   (`tools/round79-selfrecord-round78.py`, `f5()`; pre-freeze enumeration
   `SELRECORD_R78_ENUM claims=6 stale=2 corrected=0`, exit 1,
   `.ufo/waves/round-79/measured/before/c1-enum.out`).

   *Fix:* the F5 block in §Corrections below records the relation as `is-tip:false`. The durable
   rule is R78V1's tip-run discipline — name the measured revision wherever "tip" is claimed,
   and commit the tip-run receipt — which round 79 discharges with a gate and counter receipt at
   the round-79 tip; the round-78 receipts stay history and are never rewritten.

## Corrections

Exactly two value-bound blocks, one per stale fact (F5, F6), in the shape the frozen plan grades:
`corrected F<n> old=<value> new=<value> at=<40-hex> date=<ISO>`, tokens unquoted so the counter's
reader matches them. `at` is the sealed revision and each `old` is the fact's declared value
string at the sealed record; the pre-freeze enumeration derives exactly these two as stale
(`.ufo/waves/round-79/measured/before/c1-enum.out`), which fixes `corrected=2` in the target
before data.

- corrected F5 old=tip-accounting=rev:22cce544/is-tip:true new=tip-accounting=rev:22cce544/is-tip:false at=7a3cd98243b69fcbee0cc9e31878782bd8459320 date=2026-11-04
- corrected F6 old=c1-pre-correction-run=committed new=c1-pre-correction-run=committed:.ufo/waves/round-79/measured/v2/c1-pre-correction.out at=7a3cd98243b69fcbee0cc9e31878782bd8459320 date=2026-11-04

**F5.** At the sealed revision `SCORECARD.md:4538` is where the record's tip accounting names a
revision, and that revision is an ancestor: `git rev-parse 22cce544` →
`22cce544b23670984fa9e42bea673d603881aae7`; `git merge-base --is-ancestor 22cce544
7a3cd98243b69fcbee0cc9e31878782bd8459320` exit 0; `git rev-list --count
22cce544..7a3cd98243b69fcbee0cc9e31878782bd8459320` → 6. The new value keeps the counter run
and its revision and corrects only the relation: at the tip that receipt's revision is not the
tip, and it is still an ancestor of the round-79 tip (`git merge-base --is-ancestor 22cce544
f7442dea53bd8f474293a2252437b5d869801f49` exit 0). Nothing in the run is withdrawn.

**F6.** At the sealed revision no blob under `.ufo/waves/round-78/` carries `mismatches=1`
(`git grep -l mismatches=1 7a3cd98243b69fcbee0cc9e31878782bd8459320 -- .ufo/waves/round-78/` →
0 files), so the record's freeze-divergence item 4 sentence names a run whose observed failure
output was never committed. The new value names the reproduced receipt landed this round:
`.ufo/waves/round-79/measured/v2/c1-pre-correction.out` carries `# rev: fa65ce2c (pre-fix module
and worktree, reproduced in a scratch shared clone of the lane; the run's tip is 381b53dc~1)`,
`SELRECORD_R77 claims=6 mismatches=1 corrected=4 unbacked=0`,
`SELRECORD_R77_FINDING mismatch F2 derived=capabilities=37/max-round=78` and `EXIT=1`;
`fa65ce2c` is `381b53dc~1` and an ancestor of the sealed revision. The counter's F6 check reads
the blob at the tip and requires its `mismatches=1` line, so the block re-derives once the L1
commits the receipt with this lesson (at this cut the file exists in the worktree, untracked).
