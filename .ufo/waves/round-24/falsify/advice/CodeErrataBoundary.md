# CodeErrataBoundary — `apply_errata` / `refuse_unknown` boundary falsification (round 24)

VERDICT: **HOLDS** for the assigned claim — an ordinary absent fake is a real corrected
finding, and actual unavailable content is **not** rescued by the ledger (exit 2, content-derived
reason, no verdict document, identical with and without the authorized errata row). One
**confirmed source defect (F1, medium)** was found at the same boundary: the ledger's *verdict*
path (`errata-invalid`) is not scoped to the audited rounds, so an out-of-scope ledger row can
decide the verdict, and content the tool cannot read is turned into a "not a lane/fleet commit"
verdict instead of the refusal the very same content gets in an audited round.

Scope: exactly one bounded selection — seven arms of one fixture family (the round-24 grid's own
builders for the PG29/PG30/PG34 shapes), one direct auditor invocation per arm, one pinned-vs-corrected
A/B over the same arms, and one read-only A/B over the real rounds 10–20 population. No full grid, no
mutation grid, no `--selftest`, no execution-bearing probe, no network/transport payload, no lazy
fetch, PM08 not executed. Production `production/.jj/index`, fleet, sibling lanes, operator config,
routing, services and real object stores were not touched; the only production writes are this report
and the `out/CodeErrataBoundary/` artefacts.

## Axes and results

| # | Axis | Result |
|---|---|---|
| A1 | Ordinary absent fake + authorized ledger row = real corrected finding | PASS (observed) — PG29 plain shape: exit 0, `status clean`, `corrected 1`, `uncorrected 0`, uncorrected defects `[]`, the raw defect `(unresolved-full-hash, 58866b563cd900dd894ef21bc863486bcb35b56c)` retained with a non-empty `corrected_by` |
| A2 | Same row under promisor metadata alone (PG30 shape) | PASS (observed) — exit 0, `status clean`, `corrected 1`, `uncorrected 0`; byte-identical summary to the plain twin ⇒ metadata alone changes no verdict and the ledger still corrects |
| A3 | Actual unavailable content is not rescued by the ledger | PASS (observed) — control (no ledger) and counterexample (well-formed authorized row whose *token is the unavailable cited blob*) return the **same** exit 2 and the **same** stderr; stdout empty in both ⇒ the ledger row changed nothing |
| A4 | The exit-2 form satisfies the grader's `check_exit2_form` | PASS (observed) — stderr starts `could-not-evaluate:`, stdout 0 bytes (no verdict document), reason names the unavailable object `56d7b323865c731da81e0225cf109d66f0480919`, no forbidden metadata phrase (`partial clone (` / `promisor pack`) |
| A5 | The ledger's own path refuses an unavailable correction | PASS (observed) — selected-round row whose correction names unavailable referenced content ⇒ exit 2, `errata line 1: unknown: unavailable required object: 56d7b32… is referenced by the history of … but the repository cannot serve it` |
| A6 | Ledger verdict path is scoped to the audited rounds | **FAIL (observed)** — an out-of-scope (round-2) row flips a clean round-1 audit to exit 1 `failed`; the same unavailable content in that row yields exit 1 (verdict) instead of exit 2 (refusal). See F1 |
| A7 | No-harm of the proposed one-line correction on the real population | PASS (observed) — rounds 10–20, 11 reports, 42 required commits, 9 defects / 9 corrected / 0 uncorrected, `errata_rows 9`, `errata_unmatched 0`, `errata_invalid 0`, exit 0 `clean`: pinned and corrected verdicts are identical |
| A8 | Frozen (r23) arm / withdrawn original view | NOT MEASURED — out of my bounded scope; the withdrawn unknown-from-metadata expectation is **not** relabelled as passed here, and no row of mine is claimed for the original view |

## Snapshot, digests, environment (observed)

```
$ git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin \
      /fast/scratch/hyaku/kama-r24/falsify/CodeErrataBoundary
$ git -C /fast/scratch/hyaku/kama-r24/falsify/CodeErrataBoundary \
      checkout --detach 2e254a1763a9c08aa07fc53081287f506c447d84
HEAD = 2e254a1763a9c08aa07fc53081287f506c447d84 (detached, tracked tree clean)
tree = 90d19f20e02caf0c7a52e152f020e98e3c416af3
```

| Item | Digest / value | Cross-check |
|---|---|---|
| pinned revision | `2e254a1763a9c08aa07fc53081287f506c447d84` | matches the assignment |
| auditor `tools/report-landing-audit.py` | sha256 `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` | matches the assignment's source tool |
| runner `tests/report-audit/promisor-grid.py` | sha256 `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` | matches the assignment's runner (used as the fixture builder, not as a suite) |
| manifest `tests/report-audit/promisor-grid-expectations.json` | sha256 `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` | matches the assignment's manifest |
| toolchain | `git version 2.56.0` (≥ the inherited 2.45 floor), `Python 3.14.8` | pre-existing; **no install or update was performed** in this lane |

## Fixture family (one, reused from the grid's own builders)

Every arm is built by `promisor-grid.build()` — the same builder that produces the PG29/PG30/PG34
shapes — so the fixtures *are* the oracle's fixtures, not a paraphrase:

* lane repo (`master`): commit `round-1: work` by `kama-shokunin` at author time 1000, sha
  `58866b563cd900df310588effe79028efc104c33`; tree holds `f` ("fixture file"), `corpus/SOURCES.md`
  and, in the ledger arms, `registry/report-landing-errata.tsv` committed by author `fixture` at 1600;
* fleet repo: `fleet: init` (1900) then `round-1: report` (2000) writing
  `.ufo/reports/round-1/kama.md` whose `## Landed changes` cites the lane commit `58866b56…`; its
  `## Notes` may cite the lane blob `56d7b323865c731da81e0225cf109d66f0480919`;
* the unavailable object: the lane's `f` blob `56d7b323865c731da81e0225cf109d66f0480919` is
  removed from the lane object store (`grid.drop_object`), so the lane history **references** it and
  the store **cannot serve** it (the PG34 shape);
* the ledger rows are committed into the lane's `registry/report-landing-errata.tsv` (copied verbatim
  into `out/CodeErrataBoundary/*.errata-row.tsv`).

The auditor was invoked exactly as the grid invokes it (same argv, same `--rounds 1`, same
`--no-lazy-fetch` isolation inside the tool), once per arm:

```
$ TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CodeErrataBoundary/tmp \
  python3 tools/report-landing-audit.py --lane-repo fx/<ARM>/lane \
      --fleet-repo fx/<ARM>/fleet --rounds 1 --json
```

## The arms (observed)

| Arm | Fixture | Ledger row (round, kind, token → correction) | Expected from the local contract | Observed |
|---|---|---|---|---|
| A1 `control_pg34_plain` | PG34 plain: report cites the unavailable blob | none | exit 2, content-derived reason naming the blob | **exit 2**, stdout 0 bytes, stderr `could-not-evaluate: round 1: unknown: unavailable required object: 56d7b323865c731da81e0225cf109d66f0480919 is referenced by the history of …/lane but the repository cannot serve it` |
| A2 `counterexample_unavailable_rescued` | PG34 plain **+ an authorized row that claims to correct exactly that citation** | `1, unresolved-full-hash, 56d7b32… → 58866b56…310588effe79028efc104c33` | exit 2 — a ledger row must not rescue unavailable content (exit 0 would be a false clean) | **exit 2**, stdout 0 bytes, stderr **identical to A1** ⇒ the row changed nothing |
| A3 `pg29_errata_corrected_plain` | PG29 plain: report cites the spliced 40-hex, no audited repository holds it | `1, unresolved-full-hash, 58866b563cd900dd894ef21bc863486bcb35b56c → 58866b563cd900df310588effe79028efc104c33` | exit 0 clean, uncorrected defects `[]` | **exit 0**, `status clean`, `defects 1`, `corrected 1`, `uncorrected 0`, `errata_rows 1`, `errata_unmatched 0`, `errata_invalid 0`; raw defect `(unresolved-full-hash, 58866b56…d894ef21bc863486bcb35b56c)` retained with `corrected_by` non-empty |
| A4 `pg30_errata_corrected_promisor` | A3 + promisor-marked lane (`remote.origin.promisor`, `extensions.partialclone`, remote URL = deliberately absent path) | same row as A3 | exit 0 clean — metadata alone changes no verdict | **exit 0**, summary **identical to A3** (`corrected 1`, `uncorrected 0`, `errata_invalid 0`) |
| A5 `unselected_round_unresolvable_correction` | clean round-1 report, `--rounds 1` | `2, unresolved-full-hash, 0123…4567 → deadbeef…deadbeef` (fabricated absent correction, **round 2 = not audited**) | no effect on the verdict (exit 0): `errata-unmatched` is scoped to selected rounds since round 21; `errata-invalid` is not | **exit 1 `failed`**, `errata_rows 1`, `errata_unmatched 0`, **`errata_invalid 1`**, `defects 0`, `uncorrected 0` ⇒ an out-of-scope row alone decided the verdict |
| A6 `unavailable_correction_unselected_round` | clean round-1 report + the lane blob `56d7b32…` dropped (unavailable referenced content), `--rounds 1` | `2, unresolved-full-hash, 0123…4567 → 56d7b323865c731da81e0225cf109d66f0480919` (**round 2 = not audited**) | no verdict about content the tool cannot read (an out-of-scope row is not required evidence) | **exit 1 `failed`**, `errata_invalid 1`, `defects 0`, stdout is a verdict document, stderr empty ⇒ "its correction is not a lane/fleet commit" is asserted about content the tool could not read |
| A7 `unavailable_correction_selected_round` | same fixture, the same unavailable content named by a **round-1 (audited)** row | `1, unresolved-full-hash, 0123…4567 → 56d7b323865c731da81e0225cf109d66f0480919` | exit 2, content-derived reason naming the object | **exit 2**, stdout 0 bytes, stderr `could-not-evaluate: errata line 1: unknown: unavailable required object: 56d7b323865c731da81e0225cf109d66f0480919 is referenced by the history of …/lane but the repository cannot serve it` |

### What the assigned claim means, measured

* **"ordinary absent fake is a real corrected finding"** — *observed* (A3, A4). The defect is a
  real defect (`unresolved-full-hash`), the authorized row matches it on (round, kind, token), the
  row's correction is a real lane commit, and the audit is clean (exit 0) with the defect still
  visible in the raw list. Under promisor metadata the same thing happens (A4), so the metadata
  changes nothing and the ledger still works.
* **"actual unavailable content cannot be rescued by the ledger"** — *observed* (A1 vs A2). A2 is
  the exact counterexample asked for: the fixture of A1 plus a **well-formed, authorized** errata
  row whose token *is* the unavailable cited blob and whose correction is a real lane commit — a row
  that would mark the defect corrected if the ledger were applied. The outcome is byte-identical to
  the no-ledger control: exit 2, empty stdout, the same content-derived reason. The refusal is
  reached in `audit_round` → `refuse_unknown` (`tools/report-landing-audit.py:476`) *before* the
  defect list is built and before `apply_errata` runs (`:768`, `:771-772`), so the ledger never gets
  the chance to rescue it. The same holds on the ledger's own path for the audited round (A7).
  [INFERENCE, from the observed order of operations]: the same ordering holds for every defect
  kind, because every defect token is either refusal-checked (`full` at `:476`, `cited` at `:489`)
  or is a locally present lane commit (`landed-omitted`, `:502`).

## F1 (medium, source defect) — the errata verdict path is not scoped to the audited rounds

**Where:** `tools/report-landing-audit.py:583-585`

```python
    invalid = [e for e in errata if e["kind"] in RESOLVABLE and (
        status.get(hexed.get(e["line"])) != "found"
        or (e["kind"] == "landed-omitted" and e["correction"] != e["token"]))]
```

**Invariant broken:** every other ledger path is scoped to the audited population —
`unmatched` (`:553-554`) filters `e["round"] in selected`, and the refusal loop (`:561-564`)
skips rows whose round is not selected — but `invalid` is not. Consequences, both *observed*:

1. **An out-of-scope row can decide the verdict** (A5): auditing round 1 only, a clean report and
   zero uncorrected defects, a **round-2** row with an unresolvable correction yields exit 1
   `failed` with `errata_invalid 1`. The verdict of an audit of round 1 depends on a row about
   round 2. (This is the same asymmetry the round-21 review closed for `unmatched`: see
   `.ufo/waves/round-21/build/advice/AuditExitContract.md:38` — "apply_errata: unmatched only for
   selected rounds".)
2. **Unreadable content becomes a verdict instead of a refusal** (A6 vs A7): the *same* unavailable
   object `56d7b32…` yields exit 2 with a content-derived reason when the row is in the audited
   round (A7) and exit 1 with the verdict "its correction is not a lane/fleet commit" when the row
   is in an unselected round (A6). The exit-1 outcome asserts a *proved absence* about content the
   tool could not read, which is exactly what the live contract forbids: "never guessed empty
   data" (oracle-amendment-1 `prospective_expected[1]`), "a locally unresolved citation known to
   name unavailable referenced local content must be could-not-evaluate rather than proved absent"
   (`prospective_expected[2]`), and "unrelated unavailable objects must not become a blanket
   precondition" / "Never use any missing-object state as an unconditional audit precondition"
   (oracle-supplement-2 `rule`). The two outcomes for one object also violate "one canonical
   runtime, same-identity rerouting": the same content is a verdict in one scope and a refusal in
   another.

**Minimal correction (one line; verified on a scratch copy, production untouched):** scope
`invalid` to the audited rounds, exactly like `unmatched`:

```python
    invalid = [e for e in errata if e["round"] in selected
               and e["kind"] in RESOLVABLE and (
                   status.get(hexed.get(e["line"])) != "found"
                   or (e["kind"] == "landed-omitted"
                       and e["correction"] != e["token"]))]
```

The candidate copy is `out/CodeErrataBoundary/audit.errata-scoped.py`; `diff` against the pinned
tool is exactly the three lines above (nothing else changed).

**Measured effect of the correction** (pinned vs corrected, same fixtures, same argv):

| Arm | pinned | corrected |
|---|---|---|
| A1 control | exit 2 (same stderr) | exit 2 (same stderr) |
| A2 counterexample | exit 2 (same stderr) | exit 2 (same stderr) |
| A3 PG29 plain | exit 0 clean, corrected 1 | exit 0 clean, corrected 1 |
| A4 PG30 promisor | exit 0 clean, corrected 1 | exit 0 clean, corrected 1 |
| A5 out-of-scope row | exit 1 failed, `errata_invalid 1` | **exit 0 clean**, `errata_invalid 0` |
| A6 out-of-scope unavailable correction | exit 1 failed, `errata_invalid 1` | **exit 0 clean**, `errata_invalid 0` |
| A7 in-scope unavailable correction | exit 2 (refusal) | exit 2 (refusal, identical) |

**No-harm on the real population** (read-only A/B, lane = the scratch clone at the pinned
revision with the same committed `registry/report-landing-errata.tsv`, fleet = the real fleet repo,
`--rounds 10-20`): both auditors return exit 0 `clean` with an **identical** summary —
`reports 11`, `required_commits 42`, `defects 9`, `corrected 9`, `uncorrected 0`,
`errata_rows 9`, `errata_unmatched 0`, `errata_invalid 0`, `by_kind {landed-omitted 8,
unresolved-full-hash 1}` — because every committed ledger row (rounds 10, 18, 20) is inside the
audited population. The correction therefore changes no byte of the real verdict and only removes
the out-of-scope influence.

**Why scoping and not refusing:** refusing an out-of-scope row with an unavailable correction would
make an unrelated unavailable object a precondition of the whole audit, which the amendment
forbids ("unrelated unavailable objects must not become a blanket precondition"; "a whole
pinned-root reachable-tree precondition is broader than availability of objects actually required
by the audit"). An out-of-scope row is not required evidence, so it must not decide the verdict —
the same treatment `unmatched` already has.

**Not claimed:** the correction is a proposal; production was not edited. L1 owns integration, the
full grid, `--selftest` and the mutation contract. A *complete* fix could additionally report
out-of-scope invalid rows as a non-verdict counter in the summary; that is beyond the minimal
correction and is not proposed here.

## Residual risk / verification gaps

* The frozen (r23 base) arm was not executed, and the 47-row grid was not run (both outside my
  bounded assignment); my arms reuse the grid's *builders*, not its runner. The grid's PG29/PG30/
  PG34 rows therefore remain unmeasured here, though my A3/A4/A1 reproduce their expectations
  exactly.
* The withdrawn original expectation ("unknown citation in a promisor-backed repository ⇒ exit 2")
  is **not** measured and **not** relabelled as achieved; my A2/A4 arms concern the amended local
  contract only.
* [INFERENCE] The defect's generalization beyond `unresolved-full-hash` was not measured: the same
  edit also affects the `landed-omitted` clause (`correction != token`) of the same comprehension,
  so an out-of-scope `landed-omitted` row with a mismatched correction becomes invisible in a
  narrow-round audit. I did not build that arm.
* F1's practical reach depends on the ledger containing rows for rounds outside the audited
  population: the committed registry currently holds rows for rounds 10/18/20 only, all inside the
  default population, which is why the real audit is unaffected (measured, A7 row of the no-harm
  table above).
* The grader's `check_exit2_form` was satisfied by inspection of the observed stderr/stdout for A1,
  A2 and A7 (typed prefix, empty stdout, reason names the object, no metadata phrase); the grader
  itself was not executed on these arms.
* Cross-lane hazard adopted from `KamaR23-2.CaseFleetBlobless`: a blobless clone keeps a reachable
  `file://` origin, so any probe without `--no-lazy-fetch` can materialise missing blobs and turn
  a refusal into a false clean. My fixtures are plain repos (no promisor config) except A4, whose
  remote URL is a deliberately absent path, and I used the grid's `--no-lazy-fetch` helpers only —
  no manual git probe touched a fixture.
* No source-ledger row is proposed by this lane: the finding is in the audit tool, and the
  source-census final verification is L1-owned after this stage.

## Files written

* `.ufo/waves/round-24/falsify/advice/CodeErrataBoundary.md` — this report (append-only).
* `.ufo/waves/round-24/falsify/out/CodeErrataBoundary/` — `probe_errata_boundary.py` (the seven-arm
  fixture/measurement script), `exit2_form.py` (+ `exit2_form.json`), `ab_pinned_vs_scoped.py` (+
  `ab_pinned_vs_scoped.json`), `real_no_harm.py` (+ `real_no_harm.json`), `audit.errata-scoped.py`
  (the one-line corrected copy, scratch only), `summary.json`, one `*.json` per arm, and the
  verbatim committed ledger row of each ledger arm (`*.errata-row.tsv`).
* Scratch only (not production): `/fast/scratch/hyaku/kama-r24/falsify/CodeErrataBoundary/` — the
  `--no-hardlinks` clone at the pinned revision, the fixtures under `fx/`, and `tmp/` as `TMPDIR`.

## Installs

None. No pacman transaction, no host service or configuration change, no network access, no model
override, no credential use. Only the pre-existing `git 2.56.0` and `Python 3.14.8` were used.

---

## Addendum — the ledger READ path (arm A8), corroborating `KamaR23-2.CodeRequiredReads` F1

Observed here, in the same errata boundary, at the *read* side of the ledger (the finding itself is
theirs; this is an independent corroboration with my own fixture, and their minimal correction is
not re-proposed here).

Fixture (arm `A8_ledger_blob_missing`): the PG29/PG30 shape (ledger commit present and authorized,
report intact), then the ledger's own blob is dropped from the lane store —
`746d177022bb0cc5befd64cfabf2806e839cab1f` (`HEAD:registry/report-landing-errata.tsv`).

```
$ TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CodeErrataBoundary/tmp \
  python3 tools/report-landing-audit.py --lane-repo fx/A8_ledger_blob_missing/lane \
      --fleet-repo fx/A8_ledger_blob_missing/fleet --rounds 1 --json
exit=2   stdout_bytes=0
stderr: could-not-evaluate: git show 51f8d61968405f9a32de2b1f72673aad3f2a94ab:registry/report-landing-errata.tsv
        in …/fx/A8_ledger_blob_missing/lane: rc=128 fatal: bad object
        51f8d61968405f9a32de2b1f72673aad3f2a94ab:registry/report-landing-errata.tsv
```

What this shows at my boundary: the ledger's *read* failure is still **never a verdict and never a
rescue** — exit 2, empty stdout, no verdict document, and the ordinary defects of the round are not
reported (the refusal precedes any verdict), so a ledger that cannot be read cannot turn an
unavailable citation into a clean exit. What it lacks is the sibling refusal form used by the
history/tree/SOURCES/report reads: the missing blob id `746d177022bb0cc5befd64cfabf2806e839cab1f`
is not named, only the `rev:path` and the git rc (corroborating
`KamaR23-2.CodeRequiredReads` F1, `load_errata()` at `tools/report-landing-audit.py:539` not being
wrapped in `required_read()`). No oracle row is violated by this; it is a naming/consistency gap on
the refusal's content-derived reason.

This addendum changes no earlier verdict: the assigned claim still **holds** (A1/A2), and F1 (the
unscoped `errata-invalid` verdict path) is unaffected — A8 exercises `load_errata`, not
`apply_errata`'s verdict path.

---

## Addendum 2 — F1 is inherited from the r23 frozen base, not a round-24 regression

The provenance of F1 was raised by `KamaR23-2.CodeRequiredReads`; I verified it here independently,
read-only, from the pinned scratch clone (a blob read, never a worktree path):

```
$ git -C /fast/scratch/hyaku/kama-r24/falsify/CodeErrataBoundary \
      cat-file blob 0df800e896f6bce285a81e794ad4ae1d1e6c3a71:tools/report-landing-audit.py | sha256sum
da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1      # == oracle derived_from.frozen_auditor_sha256
```

| Statement | r23 frozen base (`0df800e8…`) | pinned current (`2e254a17…`) |
|---|---|---|
| `invalid = [e for e in errata if e["kind"] in RESOLVABLE and (` | :405-407, **byte-identical text, no `selected` filter** | :583-585, same text, no `selected` filter |
| `unmatched = [e for e in errata if e["round"] in selected …` | :397-398, scoped | :553-554, scoped |
| partial-clone refusal | `:457` `partial clone (promisor pack)`; `:465` `partial clone ({key})` — refused outright | replaced by the round-24 local-object contract |

Reading (mine, with the peer's observation as the trigger): the scoping asymmetry between `unmatched`
and `invalid` is **inherited verbatim from the r23 base**; in r23 it was practically unreachable
because r23 refused partial clones before the ledger was ever applied. Round 24 is the first
revision in which an unavailable object can reach `apply_errata`'s verdict path at all, so round 24
makes the inherited defect *reachable* — it does not introduce it.

Consequences for the record (no change to any earlier verdict):

* F1 is **not** a round-24 regression, so it does not weigh against the round-24 repair's own
  calibration claim; it is an inherited defect that the round-24 contract now exposes.
* The corrected line numbers for the pinned tool are `:583-585` (the peer quoted `:581-584`, two
  lines off); the pinned frozen blob's own numbers are `:405-407` / `:397-398`.
* The minimal correction proposed in F1 (scope `invalid` to `selected`) remains the same, remains
  unapplied in production by both lanes, and remains verified no-harm on the real rounds 10–20
  population.
* Per the peer's judgement, which I record as a judgement and not as an oracle claim: an
  out-of-scope ledger row is evidence the audit does not read, so refusing the whole audit for it
  would be a scope error of its own — ignoring the row (the proposed fix) is the consistent
  reading; either way the present exit 1 verdict is wrong.

Report: .ufo/waves/round-24/falsify/advice/CodeErrataBoundary.md
