# kama — round 13

## Work performed

Declared **C1 — calibration**, the lowest assigned axis (7 versus operability
8, `shokunin.conf:52`): correct two routed KQ15 formulations, distinguishing
finding IDs from exit classes and historical capture from blob comparison.
The fixed-denominator documentation measure moves **2 missing precise
assertions → 0**. Calibration stays **7 → 7, delta 0**. This is a narrow
criterion-correspondence improvement, not discovery of a new defect, a
semantic proof from strings, a serving capability or domain expansion.

- Appended KQ16, preserving historical KQ15 and all its other applicable
  boundaries. Mapping `source_mismatch=1; snapshot_tampered=2;
  source_unavailable=2` applies to the selected **primary finding**. A
  higher-ranked integrity failure can coexist with mismatch; a mismatch is
  counted only with a verified source anchor. `unpinned` ranks below
  `source_mismatch`, contrary to an inaccurate old code comment now explicitly
  marked in SKILL/LOG/lesson without rewriting historical code. Evidence:
  lane `corpus/QUALITY.md:51–61`, `SKILL.md:411–436`,
  `corpus/lessons/round-13.md:60–79`, `advice/ReviewExit.md`.
- Capture via `git show` is **author-recorded provenance**, not derivable from
  matching bytes. The comparison implementation uses `git cat-file blob`,
  manifest-independent but reading the same object store, not an external
  provenance authority. Actual code and historical receipt review ground
  these distinctions; S033 supports method only. Evidence:
  `.ufo/waves/round-12/fidelity.py:261–323`, round-12 `acceptance.json`,
  round-13 `advice/{EvidenceScribe,ReceiptFacts,ReviewMethods}.md`.
- Added a bounded textual evidence gate, its registry, pinned before/after
  QUALITY inputs and real child-CLI selftest. It checks wording adoption,
  preservation and named contradictions, not arbitrary natural-language
  truth or endpoint readiness. Evidence: `.ufo/waves/round-13/measure.py`,
  `frozen/expected.json`, `acceptance.json`; `SKILL.md:430`.
- Curated opened S033, preserving every old source row. Its transformation
  consequence is explicitly inference; all source quotes, dates and row
  changes are in lesson Gate. Evidence: `corpus/SOURCES.md:45`,
  `corpus/lessons/round-13.md:34–58`, `advice/Sources.md`.
- Mined our prior incomplete correction sweep: the earlier critic flagged
  capture/comparison conflation, but its correction missed KQ15. Discovery
  credit belongs to CloseKamaR12 and partly the prior author critic. Addressed
  the routed quality-attribution item by crediting round-12 D4's stronger
  served-identity interpretation, not gate machinery. That is prior-round
  credit, not new round-13 quality. Evidence: lesson Mistakes and Scope;
  `LOG.md:730–755`; `corpus/knowledge/served-identity-crosswalk.md:87–134`.
- One **validated 32-seat wave**, dispatched as one unchanged validator
  `taskCall`, no model argument: executor 3, revenger 1, scout 6, connector 4,
  reviewer 8, critic 5, sentinel 2, scribe 3. **L1 KamaR13 holds the canonical
  planner seat**; PlannerWalk is bounded revenger advice, not an unvalidated
  planner role. Spec/dispatch/registry/role evidence:
  `.ufo/waves/round-13/{spec,dispatch,wave-summary,record-relative}.json` and
  `advice/swarm-registry.json`. Advice is author-side, never outside closure.

Starting tree was clean at `941bb32c3f591bc63cbf7579b2b6c552228307cd`;
no interrupted lane edits were inherited. The prior non-author verifier file
was read but not edited or swept. No operator lesson file was found by the
bounded teaching sweep (`advice/TeachingSweep.md`); no teaching was silently
ignored. Stale-lane: respawn-per-round; no other mission of kama is open.
Tools installed/updated: **none**. No endpoint, service, consumer config,
environment-value, credential or old serving/fidelity gate was executed.

## Landed changes

Lane commits carry `kama-shokunin <kama@shokunin.local>`:

| Commit | Landed changes | LOG binding |
|---|---|---|
| `641e1b6f1bef0e12d14c2e23388d7592ff0cb594` | KQ16; local textual gate and frozen inputs; SKILL registry; S033 and source clarification; corpus navigation; declaration/lesson; complete validated wave and advice | `LOG.md:702–755` |
| `370c066f093bd286bb0a98963f255590e3a7016d` | Measured acceptance/census receipts; final SCORECARD/lesson/LOG results; supersession sweep and final advisory disposition | `LOG.md:757–789`; `SCORECARD.md:368–396` |

**Pushed lane HEAD:** `370c066f093bd286bb0a98963f255590e3a7016d`.
Observed push: `941bb32..370c066 master -> master` to the lane origin.
The final `git status --porcelain=v1` produced empty output before this report
was written. The report is written only after that lane push; no history was
amended. Superseded-claim sweep is committed in
`.ufo/waves/round-13/supersession-sweep.json`: retained hits are historical
KQ15, explicit diagnoses or the LOG phrase superseded by its appended erratum.

The initial registry-record attempt supplied an absolute registry path and
was refused before mutation; the required lane-relative retry succeeded.
Both receipts are retained. It did not alter the validated wave payload or
split the one dispatch. Integration decisions and nonblocking limits are
recorded in `.ufo/waves/round-13/integration-review.json`.

## Before → after measurements

**Measured revision:** `641e1b6f1bef0e12d14c2e23388d7592ff0cb594`.
Complete commands, cwd, stdout, stderr, exit codes and parsed results are in
`.ufo/waves/round-13/acceptance.json`: `ok: true`, errors empty.
Each named command ran once after integration, from the lane root:

```sh
python3 .ufo/waves/round-13/measure.py --manifest .ufo/waves/round-13/frozen/expected.json --quality .ufo/waves/round-13/frozen/before/corpus/QUALITY.md
python3 .ufo/waves/round-13/measure.py --manifest .ufo/waves/round-13/frozen/expected.json --quality .ufo/waves/round-13/frozen/after/corpus/QUALITY.md
python3 .ufo/waves/round-13/measure.py
python3 .ufo/waves/round-13/measure.py --selftest
```

| Observation | Real exit / finding | Count/result |
|---|---|---|
| Selected frozen before | 1 / `documentation_mismatch` | 2 missing assertions |
| Selected frozen after | 0 / `clean` | 0 missing assertions |
| Live committed file, original git blob read separately | 0 / `clean` | before 2 / after 0; original prefix preserved; final QUALITY equals measured HEAD |
| CLI selftest | 0 / `clean` | 10 passed, 0 failed |

Controls observed: removing either literal returns exit 1/missing1;
reintroducing bad exit/comparison wording, reversed roles or a conflicting
exit value returns exit 1 even with missing-count zero; missing KQ16 returns
exit 1/missing2; changed pinned input returns exit 2/`snapshot_tampered`
before counting. Those controls demonstrate the textual gate can fail, not
that it understands arbitrary semantics. Its `--help` remains conventional
plaintext; only evaluation modes promise a JSON object. Exit 3/`probe_error`
is declared could-not-evaluate, not claimed as an exercised acceptance case.

Independent raw-byte calculations in the receipt used `git
--no-replace-objects -C <lane> cat-file blob
941bb32c3f591bc63cbf7579b2b6c552228307cd:corpus/QUALITY.md`:

- Frozen-before equals actual start git blob; SHA-256
  `157495271d58d6deb56260b093923961e40fb8402ed7475bc4a05c88cdd173cf`.
- Frozen-after equals final QUALITY; SHA-256
  `596f87caf560a5b6c70e7796597a9d2788b9074149ae99f205b73ef2dbb813da`.
- Original QUALITY bytes are an exact prefix; all old S001–S032 source-row
  strings equal their start-commit versions. Only S033 is added.

**C1 verdict: improved**, with score unchanged. The denominator comes from
outside D1 plus static code/recorded-results review, not from inventing two
new strings. Red-before literal absence is construction/conformance evidence,
not independent semantic falsification. Frozen manifest labels alone are not
historical correspondence proof; the live read and independent byte check
supply that separate evidence. Literal paraphrase/negation and exotic
Markdown remain human-review boundaries. No serving capability is added.

| Other axis | Verdict / evidence |
|---|---|
| operability | unchanged; serving implementations, registry expectations and endpoint behavior not changed or sampled |
| freshness | unchanged; historical criterion repair is not live runtime revalidation |
| depth | unchanged; no additional serving-knowledge entry or technical capability |
| coverage | unchanged; no new serving ground; S033 is method support |
| adjacency | unchanged; routes, services, credentials, scheduling and fleet protocol remain with their owners |

No axis harm was observed within this bounded scope. **Admission remains
pending independent non-author round-13 admit/reject sampling**. A closure
should inspect committed receipts and independently recount committed
criterion/source bytes; it must not execute a sibling gate merely because
this report documents a rerun command. Author-dispatched reviewers are not
independent closure or promotion verifiers.

## Sources & frontier

Required validation command, both invocations exit **0**:

```sh
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
```

Before output:
```text
kama W04 S031 duplicate url docs.ollama.com/api/tags across scopes
kama ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
```

After output:
```text
kama W04 S031 duplicate url docs.ollama.com/api/tags across scopes
kama ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
```

Whitespace above separates raw TSV columns; complete raw streams/exits are
preserved in `.ufo/waves/round-13/{sources-before,sources-final}.json`.
Existing W04 denotes scoped same-URL curation, not independent corroboration.

Counting command, both invocations exit **0**:
```sh
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin kama
```

| Census field | Before → after |
|---|---|
| rows | 32 → 33 |
| tiers | A 29 → 30; B 0 → 0; C 3 → 3 |
| statuses | mined 22 → 23; queued 5 → 5; rejected 5 → 5 |
| invalid tiers/statuses; missing registry | 0 → 0 |

Added by tier: **A +1, B +0, C +0**. S033: absent → mined, docs/A,
opened 2026-10-20, recheck on-release, used-by
`corpus/lessons/round-13.md`. No existing status/recheck/used-by changes;
S032 was reopened and retained unchanged. New-row Gate includes URL, date
and the 15-word located OUTPUT quote: “If <type> is specified, the raw
(though uncompressed) contents of the <object> will be returned.” OPTIONS
quotes ground the transformation caveat; its application is labeled inference.

Search: three distinct pages opened/screened (git-cat-file latest, matching
2.55.0 manual, git-show), one new row included, two retained for
version/existing-row corroboration, zero quality exclusions; stop after the
bounded method distinction was located. Evidence: source Search log,
`advice/Sources.md`, lesson Gate and final Census section.

Frontier ground advanced: **none**; no new knowledge entry or capability.
K02 remains held; K05 context capacity still needs an authorized serving
runtime. Mistakes include our prior incomplete correction sweep, not merely
an external wording observation. No old frozen receipt or non-author lesson
was rewritten.

## Trend verdicts

- **expansion — unchanged:** zero new knowledge entries, serving surfaces,
  frontier ground or capabilities. Registry growth alone is not expansion.
- **quality — unchanged:** no new/rechecked serving-knowledge entry. The prior
  round-12 quality verdict is grounded in D4's stronger retained crosswalk
  interpretation (source wording versus inference; registry versus upstream
  supersession), not gate machinery, and is not reclaimed this round.
- **discernment — unchanged pending outside sampling:** KQ16 completes routed
  precision debt. Round-12 closure agreed with its sampled gate choices and
  already credited its discernment subject to this repair; there is no new
  gate disagreement to double-count. Evidence: lesson Scope,
  `advice/{AttackAdmission,AttackQuality}.md`, LOG appended correction.

No new L0 question. Standing operator-dependent runtime restoration/retirement
and invocation-timer questions remain outside this claim; no service action,
provider substitution or schedule is authorized here. The planner taxonomy
question is routed around using the orchestrator's explicit L1 planner-seat
ruling. Prior C0 closure-prompt alignment belongs to the orchestrator/protocol
owner, not kama; this round modifies no fleet protocol, prompt or runtime.
Required orchestrator action: independent closure and ledger append after
source/claim sampling; no lane admission or promotion is self-certified.

## SHONEN

- [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources — author assertion; `SKILL.md:125–181,191–241,308–345`; no new named non-author promotion verifier.
- [~] At least one end-to-end domain task executed and logged in LOG.md — historical author evidence in LOG rounds 1–3; this criterion repair is not a fresh serving task or readiness demonstration.
- [~] Instructions executable by an agent without oral context — author assertion; SKILL current checklist and local registry, snapshot-history run instructions; independent promotion review remains open.
- [~] No cross-domain bleed (PROVINCE.md still accurate) — author assertion; `PROVINCE.md:40–52`, cross-lane-scope corpus and round-13 scope. No operator/sibling surface is absorbed.
