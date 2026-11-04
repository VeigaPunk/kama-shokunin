# kama round 84 — non-author closure spot-check

author: hyaku closure (non-author integrator, @m_zfl)

Reviewed 2026-11-04. Base `aca4f33ac1e2a8cf815d97daab3b3a5cfa0d78e0`; round tip `ad370d57656a259c428db3052388659897c8e076`. Report: fleet `.ufo/reports/round-84/kama.md`; frozen contract: `plans/round-84-claims.md`. No lane-authored files changed and no sibling gate/selftest executed.

## Conformance

- `git -C /home/vgpnk/Projects/shokunin log -1 --format='%an %H' -- .ufo/reports/round-84/kama.md` observed `kama-shokunin 5b052020a13b37340c1054286d65b2514c7133d5`. Report committer time `2026-11-04T12:16:01-03:00` follows round-tip commit `2026-11-04T12:14:13-03:00`.
- `jj-lane.sh state /home/vgpnk/Projects/shokunin/kama-shokunin` observed `branch=master local=ad370d57656a259c428db3052388659897c8e076 remote=ad370d57656a259c428db3052388659897c8e076 ahead=0 behind=0 head=detached tracked=0 untracked=0`; `git status --porcelain` empty.
- Extracting every full 40-hex report citation and running `git -C <lane> merge-base --is-ancestor <hash> master` returned exit 0 for all eleven distinct hashes: 2d49bf70, 3e93febb, 4454f447, 65665250, 723253c3, aca4f33a, ad370d57, b53cd336, c0d7fbd8, eb03a64b, ffb5f797.
- Report has exactly one `## SHONEN` heading and four assessment lines, all author-asserted `[~]`. Real committed work and LOG Round84 pointers establish status **ok**, not a marker.
- Replaced `{{LANE}}`, `{{ROUND}}`, `{{FLEET_ROOT}}`, `<kama-repo>` and `{{AXES}}` in fleet `templates/round-prompt.md` with dispatched values and compared `prompt.startswith(rendered_template)`: **True**, byte-exact. Prompt committed at `e9bccde0c8bd59fce8f0e173b25cbab7568e655c`; operative mission/axes, concurrency, report, commit ordering, write/push scope and L0 clauses present. Campaign addendum explicitly maps planner to L1.
- Driver digest: `2026-11-04T11:35:47-03:00 launch kama round=84 pgid=2482641 driver=hyaku-inline attempt=1`; `2026-11-04T12:16:32-03:00 complete kama round=84; hyaku-inline attempt=1`.

## Independent measurements and claim rulings

Plain measurements below use Python standard-library parsing of `git -C <lane> show <revision>:<path>` output, not lane counters. Base and tip are the full hashes above. Gate verdicts are separately evidence-verified, not re-executed.

### C1 operability — unchanged; full frozen work missed

Independent committed-byte census over nonempty, non-comment TSV lines, excluding header:

| Surface | Base | Round tip |
|---|---:|---:|
| `registry/append-only-late.tsv` data rows | 123 | 114 |
| `registry/append-only-disclosures.tsv` data rows | 10 | 10 |
| `registry/append-only-late-r83-restored.tsv` archived rows | absent | 10 |

`git show BASE:registry/append-only-disclosures.tsv == git show TIP:registry/append-only-disclosures.tsv` is **True**. The live late register rotates ten rows out and adds one; archive keeps the ten rows. `tools/round81-append-debt.py` at tip has two occurrences of `note-wrong-deletion-round`.

Committed gate evidence under `.ufo/waves/round-84/measured/`: before `ctl-gate.out` has 12 arms and fails; report discloses that original control contains transient dirt, while independent clean no-work replay has failed=3/uncommitted=0. After `gate-selftest.out` names `3e93febb0f40955b08dc80367e8ef658eaccdfd6`, `PRE_REPORT_SELFTEST pass=35 fail=0`, EXIT=0. `after/gate-final-green.out` names **b53cd336e0cb204cf71246e95fdf7494babeafa4**, thirteen arm records, `PRE_REPORT round=84 arms=13 failed=0 uncommitted=0`, EXIT=0; its debt arm has events76/accepted53/late23/pending3/unaccepted0/bad_rows0. This is not evidence of a run at the later publication tip.

`after/c1-fixture.out` at `3e93febb` has exactly one `note-wrong-deletion-round` finding, bad_rows1, EXIT=1, alongside two disclosed count-short findings. Final gate retains debt selftest31/0, pending-falls7/0 and pin-rechecks14/0. Registry entries exist at `SKILL.md:1738-1747`.

Numeric predicates are supported, but frozen C1 work expressly requires a new disclosure row (plan lines36–41). None landed. The premise calling the event restored was false: it was ungraded; fabricating event-loss evidence would be worse. Honest narrative disclosure is appropriate but cannot retroactively replace the frozen auxiliary instruction. **Full C1 is not verified; admission stops honestly.** No axis harm is inferred from refusing fabricated evidence.

### C2 calibration — improved

Independently parsed `^corrected (F[0-9]+) old=(\S+) new=(\S+) ...` in committed lesson: exactly **F1,F2,F3,F4,F5,F8**, six unique corrections; F6/F7 remain holds. Each complete new token occurs in committed SCORECARD ordinary dated repair text: late22; window7/falls=no; delta113/103/10/10; r82-new15; selftest14; round83 closure pointer. These answer the frozen stale values, not an expanded population.

`after/c2-final.out` names `65665250e58f5deec028ad53809296e08373818a`, eight fact records, `SELFRECORD_R83 claims=8 mismatches=0 corrected=6 unbacked=0`, EXIT=0. `after/c2-red.out` demonstrates six mismatches/zero corrections/six unbacked with `--no-corrections`; it is not the promised historical uncorrected-tree run (R84V5). `after/c2-selftest.out` at `3e93febb` records sixteen PASS cases, `SELFRECORD_R83_SELFTEST pass=16 fail=0`, EXIT=0. These are committed-evidence verifications; no script was run by closure. Scope remains eight sealed facts, not whole-record correctness. KQ136 cites this round's mined stale-cell mistake.

### C3 freshness — improved

Python `csv.DictReader(..., delimiter='\t')` on committed `registry/pin-recheck-rows.tsv`: base **5 rows, holds4/ungraded1**; tip **5 rows, holds5/ungraded0**. Independently enumerated nine unique anchor paths from both extract columns, parsed each header's URL and line range, fetched eight unique URLs via `urllib.request.urlopen`, and compared `body == '\n'.join(source.splitlines()[a-1:b]) + '\n'`: **9/9 True**. SHA-256 of each committed body equals its header: **9/9 True**. Initial comparisons stripping only the stored body's trailing newline mismatched four ranges ending in blank lines; exact newline-preserving comparison resolves this, not a source defect.

`after/c3-final.out` at `65665250` records `PIN_RECHECK rows=5 graded=5 holds=5 reworded=0 moved=0 drifted=0 ungraded=0 bad=0`, EXIT=0; gate-final-green includes pin selftest14/0. All remote-origin documents were independently reopened, beyond mere hash-consistent fabricated extracts. This establishes documentary freshness only, not runtime serving health or newest-tag discovery.

## Axis verdicts and no-harm review

Ran `git -C <lane> diff BASE TIP -- SCORECARD.md` and read current axis rows. Parsed vector remains **operability8/freshness8/depth7/coverage9/calibration7/adjacency7** at both revisions; lowest assigned axis calibration was worked. Corrected adverse round83 terminal values remain explicit rather than being erased.

| Axis | Verdict | Basis |
|---|---|---|
| operability | unchanged | Numeric improvement supported, but full frozen disclosure work missed; no fabricated replacement credited. |
| calibration | improved | Six stale facts corrected, two holding facts preserved; bounded eight-fact predicate evidenced. |
| freshness | improved | Previously ungraded relation now document-backed; nine remote extract ranges independently match. |
| depth | unchanged | No depth claim or unsupported score move. |
| coverage | unchanged | Documentary extensions/coverage repairs; no new knowledge file or repertoire admitted. |
| adjacency | unchanged | Documentary cross-lane attribution retained; no sibling province or service mutation claimed. |

**Round verdict: rejected-honest-stop; status ok; admitted false.** No exploratory claim and no harmed axis.

## Outside discernment spot-check

| Item | Lane decision | Re-opened source | Outside judgment | Reason |
|---|---|---|---|---|
| S572 b7200 health README | admit | `https://raw.githubusercontent.com/ggml-org/llama.cpp/b7200/tools/server/README.md`, 2026-11-04, line406 | agree | HTTP200, 72181 bytes, sha256 `fb4ab6f2e4db180bf9c89533ef63556559c60a66f9c39a92f0c23cd88f6c6a53`; exact 11-word quote: “This endpoint is public (no API key check). `/v1/health` also works.” Supports documentary route claim, not live readiness. |
| Alternative b7200 examples/server README | reject | `https://raw.githubusercontent.com/ggml-org/llama.cpp/b7200/examples/server/README.md`, 2026-11-04 | agree | Independently returns HTTP404 body `404: Not Found`; cannot support documentary content. Flip: a retrievable revision-specific document. This is absence at this path, not evidence of absence at all paths. |

New row S572 was reopened and its ≤25-word located quote checked. Reject is recorded in Gate prose but not SOURCES; durable registry omission routed below, without reversing the substantive reject.

Required `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` ran from fleet root: exit **0**, final `kama ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`. W01 S481 tier-C mined and W04 cross-scope duplicate-URL warnings remain, not suppressed. Independent regex census `^ {0,3}\|\s*S[0-9]{3,}\s*\|` over committed registries: **311→315**, A296→300/B11→11/C4→4; mined279→283/queued8→8/rejected24→24. Committed knowledge path census `git ls-tree -r --name-only REV corpus/knowledge`: **59→59**.

## Learning trends

| Trend | Verdict | Evidence |
|---|---|---|
| expansion | unchanged | Four new A/mined rows and documentary extension, but 59→59 knowledge files, no repertoire addition; rows alone earn no expansion. |
| quality | improved | Six stale-value repairs, registered instruments and real remote documentary rechecks. Frozen C1 miss remains marked, not admitted away. |
| discernment | improved | Outside spot-check agrees with both admit and reject; previous stale-cell disagreement becomes grounded KQ136 and demonstrated red control. |

## Routed defects for kama's next round

- **R84V1:** Preserve C1 honest miss; do not retrofit the frozen instruction. A future claim must distinguish ungraded-population rotation from actual event-loss disclosure and predeclare an appropriate audit surface. Reconcile the archived rows without fabricating an event-loss declaration.
- **R84V2:** The opened/rejected alternative README appears only in lesson prose, not as a rejected SOURCES row. Add a schema-valid rejected row with reason and flip in the next curation round; do not rewrite this filed lesson/report.
- **R84V3:** Retain disclosed limits as open work: spec-only mutation study has M2/M3/M4 survivors, C2 backing-token/heading escapes, and C3 fabricated-but-hash-consistent source-origin escape. Do not credit them as killed or generalize these bounded counters.
- **R84V4:** Current SCORECARD authority still says C1 gate is “under terminal measurement” while its appended terminal section records green at b53cd336. Re-derive that current head wording next round without attributing a run to the publication tip; this is stale wording, not contradictory gate evidence or axis harm.
- **R84V5:** Frozen plan lines94–95 points to absent `measured/before/red-selfrecord.out`. Actual retained `measured/after/c2-red.out` uses `--no-corrections` at 3e93febb: a red-control demonstration, not the promised run on an uncorrected tree. Preserve this provenance limitation and correct the citation append-only next round; C2's frozen final numeric predicate remains verified.

Report attribution, chronology, clean pushed branch and prompt fidelity are conformant. SHONEN boxes remain author assertions; this closure is not an end-to-end promotion review and does not mark them checked. No promotions/mints. No tools installed or updated.

Read-only independent reviewers `CloseKamaR84.KamaC1Review` and `CloseKamaR84.KamaC23Review` corroborated the register rotation/disclosure miss and six corrections/five graded relations. C2 tool bytes match the measured selftest/final revisions and tip; C3 tool and both register bytes match final measurement and tip. Their findings supplement, not replace, closure measurements.
