# CaseCitedHole — PG33/PG34 cited-hole promisor-grid falsification (round 24)

VERDICT: **HOLDS** for the graded contract. Both assigned rows meet their **amended**
(live) expectation under the pinned candidate, and the *frozen* r23 arm fails the very same
amended columns — so the row measures a real repair, not a frozen-history artefact. **No
source defect was found** in `tools/report-landing-audit.py` on the surface this family
exercises. Four **fixture / expectation-metadata** weaknesses are reported separately below
(F1–F4); none of them changes the grading of these two rows, but F1 and F4 bound what the
family is able to prove.

Scope: exactly one bounded selection — `python3 tests/report-audit/promisor-grid.py --arm both
--case PG33-missing-cited-blob-promisor --case PG34-missing-cited-blob-plain --json` — run once
in a pinned scratch clone, plus the read-only static reads and two direct auditor invocations
against the *same* two registered fixtures (rebuilt with the grid's own builders, unmodified)
that were needed to assert the premises, the missing/present objects, the finding/token pairs,
the reason class, the no-acquisition property and the twin equality. No other lane suite, no
full grid, no mutation grid, no execution-bearing probe, no network/transport payload. PM08 was
not executed. No production file other than this report and the `out/` artifacts was written;
production `production/.jj/index`, the fleet, sibling lanes, operator config, routing, services
and real object stores were not touched.

## Axes and results

| # | Axis | Result |
|---|---|---|
| A1 | Assigned command, exit, in the pinned clone | PASS — exit **0**, stderr **empty (0 bytes)**, 2 graded rows per arm, `violations 0` in both arms, 0 tracebacks / 0 timeouts / 0 harness leaks |
| A2 | Actual missing / present objects asserted on the built fixture | PASS (observed) — cited blob `56d7b323865c731da81e0225cf109d66f0480919` **ABSENT** from lane *and* fleet, while the lane's **present** tip tree still names it (`100644 blob 56d7b32…\tf`); every other object the audit reads is **PRESENT** (lane commit, lane tip tree, `corpus/SOURCES.md` blob, fleet commit, fleet report blob, fleet tip tree); the store's missing-object set is **exactly** `{56d7b32…}` |
| A3 | Promisor marking is the only difference between the twins | PASS (observed) — PG33 lane: `remote.origin.promisor=true`, `extensions.partialclone=origin`, `remote.origin.partialclonefilter` present → `promisor_backed: true`; PG34 lane and both fleets: **no** promisor config, no `.promisor` marker → `promisor_backed: false`; all four fixtures share the same commit `58866b563cd900df310588effe79028efc104c33`, the same report bytes and the same cited OID |
| A4 | Exact finding / token pairs | PASS — current arm produces **no verdict document** (exit 2, stdout empty) for both rows, so there are no defect pairs, exactly as the amended column requires (`kinds: null`, `defects: null`). The frozen arm's PG34 pair is reproduced exactly: `('unresolved-full-hash', '56d7b323865c731da81e0225cf109d66f0480919')` |
| A5 | Content-derived reason IDs | PASS — current-arm stderr for both rows: `could-not-evaluate: round 1: unknown: unavailable required object: 56d7b323865c731da81e0225cf109d66f0480919 is referenced by the history of <lane> but the repository cannot serve it` — it names the **cited OID** (`names_any_of: ["$cited_blob"]` satisfied), it is in the `unavailable` reason class, and it is **not** the r23 metadata refusal (`partial clone (` / `promisor pack` absent). Frozen arm PG33 for contrast: `could-not-evaluate: <lane>: partial clone (remote.origin.promisor)` |
| A6 | No objects acquired | PASS (observed twice, two independent methods) — grid pin `objects_acquired {lane: [], fleet: []}` on all four rows; independently, a **full `.git` tree fingerprint** (every file: path, size, `mtime_ns`, sha256) of both audited repositories is **byte-identical before and after** the current-arm run (lane 27 files, fleet 32 files, 0 added / 0 removed / 0 content-changed) — no pack, no loose object, no `FETCH_HEAD`, no alternates |
| A7 | Actual twin document comparison | PASS, but **by an independent route** — the grid's own twin mechanism is **vacuous** for this family (`twins {PG34…: null}`, `twin_equal: null`, `twin_pairs_compared: []`): both twins refuse, so there is no JSON document to compare and the grid contributes nothing here. I therefore compared the twins myself: same exit (2), same cited OID, and stderr **identical after path normalisation** (`same_stderr_modulo_path: true`) — the substantive verdict of the marked and the unmarked twin is the same |
| A8 | Original (withdrawn) view kept visible | PASS — the two rows are **not** symmetrical here, and the grid says so: PG33 carries **no** `amended` key (its `original` column *is* the graded column: exit 2 / `unavailable`), so `met_original: true`; PG34 carries an `amended` column (exit 2) that **supersedes** its `original` (exit 1 / `unresolved-full-hash`), so the current arm reports `met_original: false` and lists PG34 in `withdrawn_original_failures: ["PG34-missing-cited-blob-plain"]`. The superseded r23 expectation for PG34 is therefore reported as **withdrawn**, never relabelled passed |
| A9 | Frozen history is not the improvement | PASS — in the frozen arm both rows **fail** the amended column (`amended_view_unmet: ["PG33-missing-cited-blob-promisor", "PG34-missing-cited-blob-plain"]`, `amended_view_met 0/2`) while meeting their frozen column (`met_frozen: true` both). The r23 harm this family removes is therefore measured, not assumed: r23 refused the marked twin for the **wrong reason** (metadata) and reported a **guessed absence** (exit 1) for the plain twin |
| A10 | Expectation integrity (no post-hoc fitting) | PASS — the live manifest's 44 original rows are **byte-identical** to the pre-inspection snapshot (`differing case rows: []`); the live file adds exactly the 3 registered opaque cells (PG46/PG47/PG48) and the same one open row (PG40). PG33/PG34 were **not** edited to fit the candidate; the snapshot row for PG34 already carried the amended exit 2 |
| A11 | Rows are load-bearing for the mutation contract | PASS (static) — `PM04-accept-unavailable-referenced-object` — the mutant that removes exactly this decision — is attributed to `PG33, PG34, PG46, PG47` (`tests/report-audit/promisor-mutants.py:326`), and the landed mutation report records it as **killed (2) — PG33, PG34** (`.ufo/waves/round-24/build/advice/MutationOracle.md:120,165`): this family is half of PM04's kill set. `PM03` and `PM02` also list PG33/PG34; `PM11` (any-hole refusal) lists them. The PM04 patch targets still exist in the pinned source (`def unknown_citation(stores, token):` + its `for store in stores:` loop and its `return None`), so the mutant is well-formed and not silently skipped |
| A12 | Lazy-fetch hazard from the sibling blobless family does not apply here | PASS (observed) — neither fixture uses a blobless clone: PG33's marked lane points `remote.origin.url` at `<case dir>/absent-remote.git`, which **does not exist on disk** (`origin_url_exists_on_disk: false`), and the fleet has no remote at all, so no probe can materialise the dropped blob `56d7b32…` by lazy fetch. Every content-touching probe I ran used `--no-lazy-fetch` explicitly, and the byte-identical `.git` fingerprint (A6) proves the auditor itself materialised nothing |

## Exact commands, exits and observations

```
$ git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin \
      /fast/scratch/hyaku/kama-r24/falsify/CaseCitedHole          # exit 0
$ git checkout --detach 2e254a1763a9c08aa07fc53081287f506c447d84 # exit 0, HEAD=2e254a1…

$ TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseCitedHole/tmp \
  python3 tests/report-audit/promisor-grid.py --arm both \
    --case PG33-missing-cited-blob-promisor \
    --case PG34-missing-cited-blob-plain --json                  # exit 0, stderr empty
```

(The assigned command was run with `TMPDIR` pointed at the mandated scratch root; that is the
only addition to the assigned argv.)

Grid output (assigned run, `out/CaseCitedHole/grid-PG33-PG34.json`, sha256
`f67244552ca480761395fee447e2c2ccc657ec3fbb77a73bcd8c16f5cf9c90c7`):

```
frozen_revision 0df800e896f6bce285a81e794ad4ae1d1e6c3a71
expectations_sha256 d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1
population_sha256  612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88  (47 rows)
auditor_sha256     frozen  da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1
                   current ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220
```

Frozen arm (r23 baseline, blob `0df800e8…`, never a target):

| case | exit | observed | amended column |
|---|---|---|---|
| PG33 | 2 | stderr `…: partial clone (remote.origin.promisor)` (metadata reason) | **not met** |
| PG34 | 1 | verdict document, defect `('unresolved-full-hash','56d7b32…')` | **not met** |

Current arm (pinned candidate `ea51bc35…`):

| case | exit | stderr / verdict | amended column | original column |
|---|---|---|---|---|
| PG33 | 2 | `could-not-evaluate: round 1: unknown: unavailable required object: 56d7b323865c731da81e0225cf109d66f0480919 is referenced by the history of <lane> but the repository cannot serve it`; stdout empty | met | met (identical column) |
| PG34 | 2 | same message, same OID, stdout empty | met | **not met → withdrawn, listed in `withdrawn_original_failures`** |

Both rows: `objects_acquired {lane: [], fleet: []}`, `traceback false`, `timed_out false`,
`leaked false`, `met_amended true`.

Independent premise + observation pass (`out/CaseCitedHole/verify_cited_hole.py` →
`premises.json`, exit 0) and full-`.git`-fingerprint acquisition pass
(`out/CaseCitedHole/check_acquisition_and_mutants.py` → `acquisition-and-mutants.json`, exit 0)
rebuilt the two registered fixtures with the grid's own builders and observed:

```
cited_blob == f_blob                                   : true (both rows)
lane tip tree entry "f"                                : 100644 blob 56d7b32… f   (present tree names the absent blob)
git --no-lazy-fetch cat-file -e 56d7b32…  lane / fleet : absent / absent
git rev-parse <lane-commit>:f                          : 56d7b32…   (the store still claims it)
store missing-object set (rev-list --objects --missing=print over every present object)
                                                        : exactly {56d7b32…}
report bytes                                           : "## Landed changes\n\n- 58866b5…\n\n## Notes\n\nblob 56d7b32…"
                                                         → the OID occurs exactly once, in the Notes section, not in Landed
all other required reads (lane commit, lane tip tree, corpus/SOURCES.md blob,
fleet commit, fleet report blob, fleet tip tree)      : PRESENT in both rows
promisor facts   PG33 lane: promisor_backed=true ; PG34 lane+fleet: promisor_backed=false
current arm      exit 2, stdout empty, names the OID, no metadata wording, no acquisition
frozen arm       PG33 exit 2 metadata refusal ; PG34 exit 1 with ('unresolved-full-hash','56d7b32…')
```

## Fixture / expectation-metadata weaknesses (reported separately from source findings)

**F1 — the family cannot discriminate "token-scoped refusal" from "any hole + any unresolved
token" (discrimination gap; grading unaffected).** In both fixtures the store's missing-object
set is **exactly** `{56d7b32…}`, i.e. the single missing object *is* the cited one. A coarse
implementation that refuses whenever the store holds *any* missing object and the report holds
*any* unresolved full hash would produce the identical observable verdict on PG33/PG34. The
correct discrimination is only visible in rows whose hole is **unrelated** to the citation
(PG22/PG37/PG41/PG42: unrelated hole + fabricated citation ⇒ ordinary failed verdict). The
source does implement the token-scoped rule (`unknown_citation` matches
`oid == token or oid.startswith(token)` against the store's missing set — the token, not the
store, is the trigger), and PM11 (any-hole refusal) is killed elsewhere, but **PG33/PG34 alone
cannot prove it**. *Minimal correction (not applied):* give one of the two rows a second,
uncited missing blob, so the token-scope is discriminated inside the family. I did not modify
any expected cell or fixture.

**F2 — PG33's promisor marking cannot observe a *successful* lazy fetch (fixture strength).**
`mark_config` points `remote.origin.url` at `<case dir>/absent-remote.git`, which does not
exist on disk (verified: `origin_url_exists_on_disk: false`). A lazy-fetch regression would
therefore fail rather than silently hydrate, and no acquisition could succeed in this row at
all; the "no objects acquired" property is only weakly exercised here. It is genuinely covered
elsewhere (the auditor's own `--no-lazy-fetch` isolation on every git call, and the real
`file://` blobless clones in PG13/PG28/PG43). *Minimal correction (not applied):* point the
marked lane at a real local origin that actually holds the blob, so a fetch regression would be
observable. Out of my assigned family; noted for L1.

**F3 — PG34's row metadata is internally inconsistent (labelling only).** `kind: "control"`,
while PG34's own `notes` call it "the declared non-promisor **policy** row", and the mutation
runner's comment defines *control* cells as "the no-harm twins" (`promisor-mutants.py:117-120`).
PG34 is not a no-harm twin of the r23 behaviour — its live expectation deliberately departs from
the frozen one (exit 1 → exit 2). Grading is unaffected (`GRADED_KINDS` treats `policy` and
`control` identically, and `graded = [r for r in rows if r["kind"] in ("policy","control")]`),
but a reader taking `kind` at face value would misread the row. *Minimal correction (not
applied):* set `kind: "policy"` for PG34, or amend the runner's comment. Documentation/metadata
only — no behaviour change.

**F4 — the grid's twin-document comparison is inert for this family.** For rows that refuse
(exit 2) there is no verdict document, so `normalise_document` returns `None` and the twin
comparison yields `None`/`null` instead of a verdict (`twin_pairs_compared: []`,
`twin_mismatch: []`). The amendment's requirement "complete marked versus unmarked twins
retain identical substantive verdicts" is therefore **not** enforced by the grid for PG33/PG34;
I enforced it independently (same exit, same cited OID, stderr identical after path
normalisation). *Minimal correction (not applied):* compare the refusal reason as well as the
document when both twins refuse. L1-owned; I did not change the grid.

## Source findings

**None.** On the surface this family exercises — `refuse_unknown` → `unknown_citation` →
`RepoStore.missing()` → `missing_reachable` — the pinned source produces the declared,
content-derived, token-scoped refusal with no metadata-driven shortcut, no fetch, and no
verdict document. Read-only inspection of `tools/report-landing-audit.py` found no defect to
report and no minimal correction to propose.

## Residual risk (observed vs inferred)

- **Observed:** the refusal escalates a *prose* 40-hex token that names an unavailable
  referenced object from an r23 failed finding (`unresolved-full-hash`, exit 1) to a whole-audit
  `could-not-evaluate` (exit 2) — and it does so on **plain, non-promisor** repositories too
  (PG34). This is sanctioned by the amendment (`prospective_expected[2]`, "applied to every
  store"), and the grid's `PG34` expectation was pre-registered before candidate inspection
  (snapshot `f66b226`), so it is a legitimate declared policy change rather than a defect. It
  is nonetheless an observable contract change on the non-promisor path: a report that merely
  *mentions* a pruned upstream hash now blocks the whole audit instead of producing a named
  finding. Worth being visible in the scorecard as a non-promisor behaviour change.
  *Inferred* (not measured here): operators who relied on exit 1 + `unresolved-full-hash` for
  plain lanes will now see exit 2 and a manual-intervention path.
- **Observed:** the match is `oid == token or oid.startswith(token)`, so a *short* prefix
  citation of an unavailable object also refuses (desirable); a token that is a prefix of a
  *present* object resolves normally.
- **Inferred (not exercised):** `missing_reachable` walks every present object of the store;
  `RepoStore.missing()` memoises it per store (`tools/report-landing-audit.py:124-130`), so the
  cost is one walk per store per run, not one per token. Not measured under load.
- **Inferred (not exercised):** a locally *pruned* object (e.g. after `git gc --prune` that
  leaves a tree naming a vanished blob) is indistinguishable from the fixture's shape and will
  produce the same CNE. That is the intended "never guessed absence" behaviour, but it means a
  store damaged by pruning becomes unauditable rather than failed.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/CaseCitedHole.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseCitedHole/grid-PG33-PG34.json` — assigned run stdout (both arms, 2 cases), sha256 `f6724455…`
- `…/out/CaseCitedHole/grid-PG33-PG34.stderr.txt` — empty stderr capture (0 bytes)
- `…/out/CaseCitedHole/verify_cited_hole.py` + `…/premises.json` — independent premise/observation verifier (rebuilds the two registered fixtures with the grid's own builders; asserts missing/present objects, promisor facts, exact tokens, twin stderr equality)
- `…/out/CaseCitedHole/check_acquisition_and_mutants.py` + `…/acquisition-and-mutants.json` — full-`.git` fingerprint acquisition check and the static mutation-patch applicability check
- Scratch (outside the repo): `/fast/scratch/hyaku/kama-r24/falsify/CaseCitedHole` — clone at detached `2e254a1763a9c08aa07fc53081287f506c447d84`, `tmp/` fixture roots, raw grid output

Production lane `production/.jj/index`, the fleet, sibling lanes, operator config, routing,
services and real object stores were not touched. No network, transport or execution payload
was used; PM08 was not executed; no mutant was executed. No tool was installed or updated (git
2.56.0 and Python 3.14.8 were already present).

## Unverified items

- The full 47-row population was **not** run; only PG33 and PG34 were executed (once through
  the grid, twice more through direct auditor invocations against the same fixtures).
- The auditor's `selftest`, the grid's `--selftest` and the mutation grid were **not** run;
  the mutation claims in A11 are a static reading of `tests/report-audit/promisor-mutants.py`
  plus the already-landed `.ufo/waves/round-24/build/advice/MutationOracle.md` kill table
  (PM04 killed by PG33, PG34), not a fresh execution.
- The frozen arm was exercised only through the grid's frozen blob `0df800e8…`; I did not diff
  the r23 auditor source against the pinned one.
- Whether the `absent-remote.git` path (F2) could be reachable in another environment was not
  probed; no network use was permitted and none was attempted.
- The r23 behaviour on a **plain** repository where a cited hash is genuinely absent *and*
  unclaimed by the store (the PG25/PG37 shape) is outside this family and was not executed.

Report: .ufo/waves/round-24/falsify/advice/CaseCitedHole.md
