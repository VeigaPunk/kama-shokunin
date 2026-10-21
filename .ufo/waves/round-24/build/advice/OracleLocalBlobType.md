# OracleLocalBlobType — round-24 C1: an ordinary full-hash outside `## Landed changes` resolves as a locally present blob

**Verdict:** the expected outcome for this case is **exit 0 (clean), findings `[]`** — the
same substantive verdict, and the same summary object, as the otherwise identical full
clone — for **every** promisor-metadata variant, whether the cited blob is reachable from
the pinned lane commit root or dangling in the object store. The r23 base returns
**exit 2** for five of the seven variants I built; that blanket refusal is the harm the
round-24 repair removes. The repair must be gated on **object availability**, not on the
mere presence of promisor metadata, and a citation outside `## Landed changes` must keep
resolving by **object existence of any type** (blob included), not by commit-ness.

Everything below was measured offline in scratch before any candidate existed. No
candidate run, no grid/selftest/full-suite run, no network transport, no install.

---

## 1. The case, in r23 semantics (code anchors at base `0df800e`)

| element | r23 behavior | anchor |
|---|---|---|
| report | fleet blob `.ufo/reports/round-1/kama.md`: `## Landed changes` cites the lane commit; `## Notes` cites a **full 40-hex token of a blob** | `tools/report-landing-audit.py:302` `audit_round` |
| full-hash citation outside Landed | scanned by `FULL` (`:283` `classify_full_hashes`), resolved by `lookup(repos, full_tokens)` **without a peel** → any object type counts as found | `tools/report-landing-audit.py:325`, `:139` `lookup` |
| Landed-section citation | resolved with peel `"^{commit}"` → a blob there would *not* resolve | `tools/report-landing-audit.py:336` |
| token present in lane but absent in fleet | `lookup` iterates repos; found in **any** repo wins | `tools/report-landing-audit.py:139-176` |
| blocker | `check_history_repo` refuses the whole repository on promisor *metadata* | `tools/report-landing-audit.py:438`, `:457` (promisor pack), `:462-465` (`extensions.partialclone`, true `remote.*.promisor`) |

So the case pins three things at once: (a) promisor metadata must not pre-empt the audit,
(b) a bare (unpeeled) full-hash citation of a **blob** is a valid existence token, and
(c) "missing in the fleet" is not absence when the lane has the object.

This matches the source reading already filed by the `SrcCatFile` lane
(`build/advice/SrcCatFile.md` §5): "`cat-file --batch-check` resolves them and prints
oid/type/size; Q1 never fires … This page gives no basis to refuse the repository", and
"the bare lookup can legitimately print `found` with `%(objecttype)` = blob/tree".

## 2. Fixture recipe (bounded, offline, no clone, no transport)

Base auditor under test: `tools/report-landing-audit.py` at `0df800e` — git blob
`cf706c52233139920da60f8b55d06f031286c4f9`, sha256
`da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` (the working-tree
copy is byte-identical). git 2.56.0. Scratch:
`/fast/scratch/hyaku/kama-r24/OracleLocalBlobType/` (script `fixture.py`, artifacts in
`build/out/OracleLocalBlobType/`).

```
lane   = git init -b master ; commit "round-1: work" by kama-shokunin, author time
         @1000 +0000, containing f="round-1 work\n" AND corpus/blob.txt="local blob
         body\n"  (same commit: two commits would create a second required lane
         commit and produce a landed-omitted defect)
blob   = git rev-parse HEAD:corpus/blob.txt          # 2252b93f921956e9975ee9054771ca016b8a6350
fleet  = git init -b master ; commit ".ufo/reports/round-1/kama.md" by fleet, author
         time @2000 +0000, content:
           # kama round 1
           ## Landed changes
           - <lane commit sha>
           ## Notes
           local blob <blob sha>
```
`--rounds 1 --no-errata` (the lane repo has no `registry/report-landing-errata.tsv`, and
`load_errata` would otherwise raise). Promisor state is added **as metadata only**, never
by cloning, so the store stays complete and nothing can be fetched:

* *config* — `git config remote.origin.url <local path>`,
  `remote.origin.promisor=true`, `remote.origin.partialclonefilter=blob:none`,
  `extensions.partialclone=origin`
* *paired marker* — `git repack -a -d`, then create the sibling
  `objects/pack/pack-<id>.promisor` next to the real `pack-<id>.pack`
* *filter only* — `remote.origin.partialclonefilter=blob:none` alone
* *dangling blob* — `git hash-object -w --stdin` without `git add`: present in the
  object store, unreachable from every commit root

All commands ran with `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`,
`GIT_ALLOW_PROTOCOL=file`; no `git clone`, no `git fetch`, no network.

## 3. Measured: r23 base vs expected round-24

| id | promisor state (lane / fleet) | cited blob | r23 base | expected round-24 (frozen→current) |
|---|---|---|---|---|
| A | none / none | reachable | **0**, kinds `[]` | 0, kinds `[]` (twin reference) |
| B | config / none | reachable | **2** `partial clone (remote.origin.promisor)` | **0**, kinds `[]` |
| C | config + paired marker / none | reachable | **2** `partial clone (promisor pack)` | **0**, kinds `[]` |
| D | none / none | dangling | **0**, kinds `[]` | 0, kinds `[]` (twin reference) |
| E | config / none | dangling | **2** | **0**, kinds `[]` |
| F | config / config | reachable | **2** | **0**, kinds `[]` |
| G | filter only / none | reachable | **0**, kinds `[]` | **0**, kinds `[]` (no-harm control) |
| I | paired marker only / none | reachable | **2** `partial clone (promisor pack)` | **0**, kinds `[]` |

Expected summary for every row above (identical object to A's, since the summary holds no
path): `defects 0, uncorrected 0, corrected 0, by_kind all 0, errata_rows 0,
errata_unmatched 0, errata_invalid 0, required_commits 1, post_report_commits 0,
reports 1, rounds [1], status "clean"`.

## 4. Oracle-construction probe (r23 base minus the two promisor refusals)

`probe.py` copies the r23 auditor into scratch and deletes only the promisor-specific
`raise EvalError` lines (`:457`, `:462-465`); nothing else changes and no production file
is touched. Result — the rest of the r23 pipeline already produces the full clone's
verdict:

| row | probe exit | kinds | defects | summary == full-clone twin |
|---|---|---|---|---|
| B, C, F, G, I (reachable blob) | 0 | `[]` | `[]` | **True** |
| E (dangling blob) | 0 | `[]` | `[]` | **True** |

So for this case the round-24 repair is exactly "replace the blanket refusal by an
availability check that passes" — and the repair must not change anything else
(§1's wrongtype and cross-repo rules already hold in the base).

## 5. Git-level facts the repaired auditor can rely on (measured)

| fact | measurement |
|---|---|
| the cited blob resolves in the promisor-marked lane | `git --no-lazy-fetch cat-file --batch-check` → `2252b93f…6350 blob 16` |
| the same token in the fleet | `… missing` — so *found in any repo* must win |
| object closure of the pinned lane root | `git --no-lazy-fetch rev-list --objects --missing=print --no-object-names <lane-commit>` → rc 0, 5 lines, **0** `?`-prefixed lines (fleet: 6 lines, 0 missing) |
| **dangling** blob | **not** in the closure listing (5 lines, same as A) but `cat-file --batch-check` → `… blob 14` ⇒ closure membership is **not** a substitute for an existence check on a *citation*; the citation check must stay a cat-file existence check |
| the auditor's own git calls on promisor-marked repos | all rc 0: `rev-parse --show-object-format` → `sha1`, `--is-shallow-repository` → `false`, `--show-prefix` → empty, `config --null --list`, `log -z --format=…`, `ls-tree -r --name-only`, `rev-parse --verify HEAD^{commit}` — the pipeline is unaffected; only the refusal blocks it |

## 6. Hazard: deleting the refusal is **not** the repair

Scenario J (adjacent to my case, not my case): promisor-marked lane, report cites a
40-hex token that exists in **neither** audited repository.

| arm | outcome |
|---|---|
| r23 base | exit 2 (`partial clone (remote.origin.promisor)`) |
| refusal-removed probe | **exit 1 + `unresolved-full-hash`** — uncertain absence turned into a proved-absent verdict |
| preregistered expectation | **exit 2** (unknown; never a clean or failed verdict) |

So the discriminator must be *object presence* (present → resolve; absent → unknown in a
promisor-backed store), not the promisor flag alone. My case is the positive half
(present blob → exit 0); J is the negative half (absent → exit 2).

## 7. Transport safety of the presence check (measured, `measure2.py`)

| read | result |
|---|---|
| missing object, `--no-lazy-fetch` | `… missing`, **no** fetch, no `FETCH_HEAD` |
| missing object, **without** the flag | git **invoked the transport**: `warning: filtering not recognized by server, ignoring` / `fatal: git upload-pack: not our ref …` |
| present blob, with or without the flag | `… blob 16`, no transport |

`GIT_ISOLATION` (`tools/report-landing-audit.py:93`, which carries `--no-lazy-fetch` and
`--no-replace-objects`) is load-bearing for the *absence* path and must survive the
repair unchanged; the presence path is transport-free either way.

## 8. Grid rows proposed for `tests/report-audit/promisor-grid.py`

Frozen arm = the r23 base auditor above (blob `cf706c52…`, sha256 `da5041a8…`); the
frozen arm is expected to *fail* the new rows (that is the harm being repaired), exactly
as `repo-state-grid.py` documents for its frozen arm.

| row | fixture | frozen exit | current exit | current kinds |
|---|---|---|---|---|
| `P01-promisor-config-blob-citation` | B | 2 | **0** | `[]` |
| `P02-promisor-paired-marker-blob-citation` | C | 2 | **0** | `[]` |
| `P03-promisor-config-lane-and-fleet` | F | 2 | **0** | `[]` |
| `P04-promisor-filter-only-blob-citation` | G | 0 | **0** | `[]` (no-harm) |
| `P05-promisor-config-dangling-blob` | E | 2 | **0** | `[]` |
| `P06-promisor-config-absent-citation` | J | 2 | **2** (reason pin must change: not "partial clone") | — |

**Retained r23 rows that must be re-pinned, not silently kept** (evidence, no edits made
here): `F23-promisor-pack-without-config` (contract, exit 2, reason pin
`"promisor pack"`, `tests/report-audit/repo-state-grid.py:670`, `:704`) — its fixture is
a *blobless* clone, so exit 2 stays correct but the **reason** becomes an
availability/unresolved-citation reason; `F06-lazy-fetch-command` (`:651`, `:697`) same;
`T01-blobless-partial-clone` (tradeoff, `:689`) keeps exit 2 under the new policy while
its "tradeoff" framing is withdrawn. Controls `C09-promisor-false-config` and
`C10-orphan-promisor-marker` (`:679-680`) stay exit 0 — note `C10` writes
`pack-deadbeef.promisor` **without** a sibling `.pack`, which is *not* the paired marker
of row `I`; paired-marker detection must not fire on the orphan control.

## 9. Mutation sensitivity of this case

**Killed by my rows** (frozen/current divergence or twin divergence):
* blanket re-refusal of any promisor-marked repository → exit 2 instead of 0;
* peeling the bare full-hash lookup to `^{commit}` → the blob citation becomes
  `missing` → exit 1 + `unresolved-full-hash` (the wrongtype trap);
* treating "missing in this repo" as absence instead of found-in-any-repo → the blob is
  missing in the fleet by construction;
* gating citation resolution on closure membership instead of object existence → the
  dangling blob (rows D/E) turns into a false refusal.

**Not killed here (verification gaps, owned elsewhere):** dropping `--no-lazy-fetch`
(my objects are present, so no fetch is attempted); exit 1 instead of exit 2 for an
*unavailable* required object (row P06 / `CaseMissingLaneBlob`); timeout or FIFO-hang
regressions; signature/replace-ref regressions; the `landed-omitted` verdict under
promisor metadata (`CaseCompleteLane`/`CaseMarkerLane`).

## 10. Evidence, commands, and what was not run

* Artifacts (this wave): `build/out/OracleLocalBlobType/` — `fixture.py`,
  `measure2.py`, `probe.py`, `hazard.py`, `measurements.json`,
  `probe-results.json`, `transport-measurements.json`, `hazard-results.json`, and the
  fixture repositories (scratch copies under `/fast/scratch/hyaku/kama-r24/OracleLocalBlobType/`).
* Every audit invocation: `python3 tools/report-landing-audit.py --lane-repo … --fleet-repo
  … --rounds 1 --no-errata --json`, 30 s timeout, own process group, offline env.
* **Unrun / unverified:** no candidate implementation existed in this lane, so every
  "current" expectation above is a *prediction* derived from (a) the base semantics
  measured on the identical content without promisor metadata and (b) the
  refusal-removed probe — not a measurement of a candidate. No grid, selftest,
  full-suite, build, lint or formatter run. No network transport (the only remote
  contacted was none); no package installed or upgraded (git 2.56.0 was already
  present). Not measured here: the exit-2 *reason strings* the repaired auditor will
  use, and `git rev-list --objects --missing=print` behaviour on a genuinely blobless
  clone (another lane's case).

---

## 11. Addendum — status of this oracle and how the rows must be graded

Appended after the `CritExpected` review; the sections above stand unchanged.

**(a) Authority of the oracle.** The expectation in §3 is *construction-derived*: the
non-Landed full-hash lookup carries no peel (`tools/report-landing-audit.py:325`), the
cited blob is present in the audited object store (§5), therefore the token resolves and
the finding list is empty. The refusal-removed probe of §4 is **corroboration only** — it
is the naive repair (refusal deletion), not an authority, and it must not be cited as if
it were independent confirmation.

**(b) These rows are construction rows; they do not discriminate.** The naive repair
passes every row in §3, so on their own they leave the blanket-removal mutant alive.
They must be graded **as a group together with rows where an object is genuinely missing
or a citation is unknown** — the discriminating rows are:

| discriminating row | owner | expectation |
|---|---|---|
| `P06` (scenario J: promisor-marked lane, citation absent from both repos) | this lane (§6, §8) | exit **2**, and the reason pin must not be "partial clone"/"promisor pack" |
| `unhydrated` / `fleet-unhydrated` | `CaseHydratedLane` (`build/out/CaseHydratedLane/evidence-*.json`: exit 2, kinds `null`) | exit 2 |
| A-main unknown citation | `CaseUnknownCitation` | exit 2 (preregistration line 10) |
| `F23-promisor-pack-without-config` | retained r23 grid (`tests/report-audit/repo-state-grid.py:670`, reason pin `:704`) | exit 2 with a re-pinned reason |

A grading set that contains only §3's rows proves nothing about the repair; a set that
contains §3's rows **plus** the four above kills the blanket-removal mutant (it turns
uncertain absence into a proved-absent verdict, §6).

**(c) Pin (kind, token) and the summary, not kinds alone.** For each row of §3 the exact
pins are:

* `exit` = 0
* `defects` = `[]` — the *exact list*, so no defect of any kind and no token appears
  (a kinds-set pin would also accept a row that reports the right kinds for the wrong
  token, or the right kinds with a wrong count);
* `summary` = exactly the object below (equal to the full-clone twin's, and the summary
  carries no path, so equality is meaningful):

```json
{"by_kind": {"landed-ambiguous": 0, "landed-omitted": 0,
             "landed-section-missing": 0, "landed-unresolved": 0,
             "unresolved-full-hash": 0},
 "corrected": 0, "defects": 0, "errata_invalid": 0, "errata_rows": 0,
 "errata_unmatched": 0, "post_report_commits": 0, "reports": 1,
 "required_commits": 1, "rounds": [1], "status": "clean", "uncorrected": 0}
```

In the house case format (`build/out/CaseHydratedLane/evidence-*.json`:
`{"<scenario>/<variant>": {"exit": N, "kinds": [...]}}`) the §3 rows therefore read
`{"exit": 0, "kinds": []}` **plus** the two extra pins `defects: []` and the summary
object; §8's `P06` reads `{"exit": 2, "kinds": null}` with the re-pinned reason.

**(d) Filter-only (row G) is valid here only because the token resolves locally.**
`remote.origin.partialclonefilter=blob:none` alone does not describe a promisor remote
that can be fetched from in the r23 code path (`tools/report-landing-audit.py:462-465`
keys on `extensions.partialclone` and true `remote.*.promisor`), so the base already
exits 0 on row G — the row is a **no-harm** control, not a discriminator. With an
*unresolved* token in the same repository, preregistration line 10 governs: unknown
citation in a promisor-backed repository → exit 2, never a clean or failed verdict. Row
G must therefore not be read as evidence that filter-only stores are exempt from the
exit-2 rule; it is exempt only because the object is local.

**(e) Scope of the pins.** The `defects: []` and summary pins above are properties of
*this* fixture (one cited lane commit, one cited blob, one report). They do not license
any statement about a report whose citations are unresolvable — see §6 and §8's `P06`.

---

## 12. Amendment-conformed correction (appended after `oracle-amendment-1.json`)

Appended after (i) `.ufo/waves/round-24/oracle-amendment-1.json` (L1, appended before the
candidate was inspected) and (ii) the `CritExpected` and `CaseWrongTypeCitation` notes.
Sections 1-5, 7 and 9-10 stand unchanged; **§6 and §8 are corrected here**; §11 is
corrected in (d) below.

**(a) What the amendment supersedes.** `oracle-amendment-1.json` supersedes
*prospectively* the preregistration line `expected_after[3]` ("unknown citation in any
metadata-marked repository necessarily exit2"). Therefore:

* **§6's hazard conclusion is withdrawn as an expectation.** A fabricated citation that
  is absent from a **complete** local store in a promisor-marked repository must now
  yield the **twin verdict** — exit 1, `unresolved-full-hash`, token = that sha — because
  "promisor metadata alone never changes local-object resolution or a clean/failed
  verdict, including locally unresolved citations". The naive refusal-removal repair is
  *right* on that shape (measured: exit 1 + `unresolved-full-hash`); my earlier §6/§8
  expectation of exit 2 for it is withdrawn.
* Exit 2 remains required exactly where the citation is **known to name unavailable
  referenced local content** — the shape measured as scenario **K** in (c) below.
* **My own case is unaffected and directly endorsed** by the amendment's "complete
  marked versus unmarked twins … retain identical substantive verdicts": exit 0,
  `defects == []`, summary equal to the full-clone twin's (§3, §11(c)).

**(b) Corrected row set.** §8's rows become:

| row | shape | expected (amended) | frozen base |
|---|---|---|---|
| P01-P03, P05 | promisor metadata, cited blob **present** | exit 0, `defects == []`, summary == twin | exit 2 |
| P04 | filter-only metadata, cited blob **present** | exit 0, `defects == []`, summary == twin (no-harm) | exit 0 |
| **P06** | promisor metadata, citation absent from a **complete** store | **exit 1**, kind `unresolved-full-hash`, token = the fabricated sha (twin verdict) — *not* exit 2 | exit 2 |
| **P07** (new, scenario K) | promisor metadata, cited blob **missing from the store but referenced by a present tree** | **exit 2**, content-derived reason (must not be "partial clone"/"promisor pack") | exit 2 |

P01-P06 are **construction rows** (the naive repair passes them). P07 is the row that
discriminates the blanket-removal mutant.

**(c) P07 — the discriminating row, measured (`fixture_k.py`,
`out/OracleLocalBlobType/scenario-k-results.json`).** Fixture: promisor-marked lane
(`remote.origin.promisor=true`, `remote.origin.partialclonefilter=blob:none`,
`extensions.partialclone=origin`) whose store has a **hole**: a blob referenced by a
present tree was deleted from the object store, and the report cites that blob's sha
outside `## Landed changes` (no clone, no fetch).

| measurement | value |
|---|---|
| bounded traversal `git --no-lazy-fetch rev-list --objects --missing=print --no-object-names <lane-commit>` | rc 0, 5 lines, **missing = `["?de1d85fdd17416717224bf9faa67ca1009cc9df1"]`** — the cited token is *known* to name unavailable referenced local content |
| r23 base auditor | **exit 2** (`partial clone (remote.origin.promisor)`) |
| naive repair (refusal deletion only) | **exit 1 + `unresolved-full-hash`**, token `de1d85fd…` → **the blanket-removal mutant survives this shape and is killed by P07** |
| amended expectation | **exit 2** with a content-derived reason |

**(d) Grading coupling, corrected.** The exit-2 anchors that are safe today are the rows
where the missing object is one the audit actually reads or needs: **P07** (this lane),
`CaseMissingFleetReport` (the HEAD report blob is read), `CaseMissingLaneBlob`, the
retained `F23-promisor-pack-without-config` with its reason re-pinned
(`tests/report-audit/repo-state-grid.py:670`, `:704`), and `fleet-unhydrated` (the HEAD
report blob is read). **Not** an anchor: the lane-side `unhydrated` row of
`CaseHydratedLane` — contested by `CritExpected`'s F1 (its missing blobs are never read
by the audit, and r22 `4fe9339f` gives the correct exit 0 there) — so it is not to be
anchored on until L1 defines the required set. **P06 is no longer an exit-2 anchor**
under the amendment; it is a construction row with the twin verdict.

**(e) Alignment with the adjacent wrong-type cell.** `CaseWrongTypeCitation`
(`build/out/CaseWrongTypeCitation/expected.json`) owns the complementary cell: a
locally present blob cited **inside** `## Landed changes` must be a real failed finding
— exit 1, kind `landed-unresolved`, token = the blob sha — in the full arm *and* in the
promisor-metadata arm. The two cells are consistent and non-overlapping: the Landed path
peels `^{commit}` (`tools/report-landing-audit.py:336`) and therefore cannot resolve a
blob, while the non-Landed full-hash path does not peel (`:325`) and does resolve it.
Their "promisor-metadata arm = exit 1, not exit 2" expectation agrees with my measurement
of the base (exit 2 there) and with the amendment's twin-verdict rule.

**(f) Scope note carried by the amendment.** "Complete promisor-marked real lane,
rounds 10-22, includes an errata-corrected locally missing hash … the initial expectation
would abort before errata and fail the required restoration": an errata-corrected locally
missing hash must still be **restored** (the errata row honoured before any exit-2
abort). That is `OracleMissingErrata`'s cell; my rows use `--no-errata` and make no
errata claim.

**(g) Unrun.** P07 was measured against the r23 base and the refusal-removed probe only;
no candidate existed in this lane, so P07's "current" expectation is a prediction from
the amendment's rule plus the measured traversal output. No grid, selftest, full-suite,
build, lint or formatter run; no network transport; no install.

---

## 13. Decision recorded (L1, `landed123640b`, before candidate observation)

**L1 selected the P06/P07 distinction of §12** under
`.ufo/waves/round-24/oracle-amendment-1.json`, landed at `123640b` — i.e. **before** any
candidate was observed, so it is not candidate-fitted. Main delegated the decision to
L1; L1's ruling is not "whatever the candidate does".

**Final expectations (frozen arm = r23 base auditor, blob `cf706c52…`, sha256
`da5041a8…`):**

| row | shape | expected exit | exact defects (kind, token) | summary pin |
|---|---|---|---|---|
| P01-P03, P05 | promisor metadata, cited blob **present** (P05: present but unreachable) | **0** | **`[]`** — no defect of any kind, no token | identical to the full-clone twin's: `by_kind` all 0, `defects 0`, `uncorrected 0`, `status "clean"`, `required_commits 1`, `reports 1`, `rounds [1]` |
| P04 | filter-only metadata, cited blob present | **0** | **`[]`** | same twin summary (no-harm control; valid only because the token resolves locally) |
| P06 | promisor metadata, **fabricated token absent from a COMPLETE store** | **1** | exactly one: `{"kind": "unresolved-full-hash", "token": "<the fabricated 40-hex sha>"}`; **must not** contain `landed-unresolved`, `landed-ambiguous`, `landed-omitted`, `landed-section-missing` | `by_kind.unresolved-full-hash = 1`, others 0; `defects 1`, `uncorrected 1`, `status "failed"`, `required_commits 1`, `reports 1`, `rounds [1]` |
| P07 | promisor metadata, cited **known referenced missing required blob** | **2** | none — content-derived could-not-evaluate; **never** 0/1 | — |

Measured support for P06 (refusal-removed probe on scenario J, i.e. the repair shape
L1 selected): exit 1, `kinds ["unresolved-full-hash"]`, defect token
`0123456789abcdef0123456789abcdef01234567`, summary exactly as pinned above. **Authorized
errata may clean P06**: with a matching errata row (`round`, `unresolved-full-hash`,
token) the defect becomes corrected → `uncorrected 0` → exit 0 with `corrected_by`
set; the P06 pin is stated for the `--no-errata` arm.

Measured support for P07 (scenario K): bounded traversal
`git --no-lazy-fetch rev-list --objects --missing=print --no-object-names <lane-commit>`
→ `missing = ["?de1d85fdd17416717224bf9faa67ca1009cc9df1"]` (the cited token is known to
name unavailable referenced content), base exit 2, refusal-removal exit 1 +
`unresolved-full-hash` → the content-derived exit 2 is the discriminating behavior.

**Two prohibitions L1 attached, both reflected above:** *no full-root completeness
precondition* — the exit 2 must follow from the **cited** token being known-missing
(referenced), not from a closure precondition over the whole root; and *no blanket
promisor-unknown rule* — promisor metadata alone never changes a verdict, so the
absent-token case (P06) is an ordinary failed finding, not a could-not-evaluate.

**History preserved, never overwritten.** The original preregistration expectation for
this shape (`preregistration.json` `expected_after[3]`: unknown citation in a
promisor-backed repository ⇒ exit 2) is retained as **withdrawn / not-met** in §6 and
§8 as originally filed, and the amended prospective rule is appended here and in §12.
The two readings are kept separate: the pre-amendment registration is historical, the
amended rule governs the candidate, and the pre-amendment expectation is *not* counted
as achieved.

**Unrun.** No candidate existed in this lane; P06/P07 "current-arm" expectations are
predictions from the amendment's rule plus the measurements above. No grid, selftest,
full-suite, build, lint or formatter run; no network transport; no install.

---

## 14. Additional rows: P08 (token-scoped rule), P08b, P09 (declared non-promisor policy row)

Appended after L1's confirmation of P01-P07 (§13) and `CritExpected`'s request to
separate the amendment's **token-scoped** rule from an **over-broad** "any hole means
unknown" rule, and to declare the non-promisor policy row.

**Rule under test (L1 / `oracle-amendment-1.json`):** a locally unresolved citation is
**could-not-evaluate (exit 2)** only when it is **known to name unavailable referenced
local content** — i.e. the token appears in the store's missing set
(`git --no-lazy-fetch rev-list --objects --missing=print --no-object-names <root>`
reports it with a `?` prefix). A store that merely *has* an unrelated hole does not
make an uncited, unresolvable token unknown.

| row | store | hole | cited token | token in missing set? | expected (amended) | base (r23) | refusal-removed probe |
|---|---|---|---|---|---|---|---|
| **P08** | promisor-marked | unrelated (blob referenced by a tree, never cited) | fabricated `0123456789abcdef0123456789abcdef01234567` | **no** | **exit 1**, kind `unresolved-full-hash`, token = the fabricated sha (twin verdict) | exit 2 (blanket refusal) | exit 1 + `unresolved-full-hash` |
| **P08b** | plain (non-promisor) | unrelated (same shape) | same fabricated sha | **no** | **exit 1**, kind `unresolved-full-hash`, token = the fabricated sha | exit 1 + `unresolved-full-hash` | exit 1 + `unresolved-full-hash` |
| **P09** | plain (non-promisor) | the cited blob itself (referenced by a tree, deleted from the store) | the hole blob `de1d85fdd17416717224bf9faa67ca1009cc9df1` | **yes** | **exit 2**, content-derived CNE | exit 1 + `unresolved-full-hash` | exit 1 + `unresolved-full-hash` |

Measured missing sets (identical in all three lanes):
`missing = ["?de1d85fdd17416717224bf9faa67ca1009cc9df1"]` — the hole only; the
fabricated token is absent from it in P08/P08b, the hole token is present in it in P09.
Evidence: `out/OracleLocalBlobType/{fixture_p.py,rows-p08-p09-results.json}`.

**What each row kills.**
* **P08** kills an over-broad "the promisor-backed store has a hole ⇒ unknown" rule
  (which yields exit 2 where the twin verdict is exit 1) and, together with P07,
  separates the token-scoped rule from the hole-based one: P07's token is in the missing
  set (exit 2), P08's token is not (exit 1) although both stores have a hole.
* **P08b** pins that the same distinction holds in a **non-promisor** store, so the rule
  is uniform and not conditioned on metadata.
* **P09** is the **declared non-promisor policy row**: the token-scoped rule applies to
  every store, not only promisor-backed ones, so a *non-promisor* repository whose
  **cited** token is a known missing referenced object leaves r22/r23's exit 1 and
  becomes exit 2. This is consistent with the amendment (promisor metadata is not the
  cause; the token's known unavailability is), and it is a behaviour change on a
  non-promisor row that the grid must declare rather than leave implicit.

**Prohibitions L1 attached, restated as row properties.** *No whole-root availability
precondition:* in P08/P08b the store has a hole and the audit still produces an ordinary
verdict — a root-wide closure precondition would wrongly abort both with exit 2; only
the **cited** token's membership in the missing set matters (P07, P09). *No blanket
promisor-unknown rule:* P08's cited token is unknown in a promisor-marked store and the
verdict is the ordinary failed finding, not exit 2.

**Status of P09's expectation.** It is derived from the rule L1 selected and from
`CritExpected`'s observation that the candidate computes the missing set for every
store; it was **not** measured on a candidate in this lane (none exists here) — the
base and refusal-removed probe both give exit 1 + `unresolved-full-hash` on the cited
hole token. Unverified by this lane: the candidate's actual exit-2 reason string.

**History preserved.** The original preregistration view of this shape
(`expected_after[3]`, unknown citation in a promisor-backed repository ⇒ exit 2) stays
recorded as filed in §6/§8 and is marked **withdrawn / not achieved** in §12/§13; it is
not overwritten by P06/P08/P08b, which carry the amended prospective rule.

---

## 15. Sharpened pins: exit-2 stderr form, exact (kind, token) pairs, and the pre-amendment grid conflicts

Appended after `CritExpected`'s confirmation that my §13 P06/P07 pins match theirs
(`build/out/CritExpected/p06-p07-reconciliation.json`, `written 18:10Z`,
`candidate_consulted: false`) and their request to add the **negative stderr pin** to P07.

**(a) Exit-2 pin form (applies to P07, P09 and every exit-2 row).** An exit 2 must be a
content-derived could-not-evaluate, never the r23 blanket refusal:

| requirement | rule |
|---|---|
| must | stderr starts with `could-not-evaluate:` |
| must | stdout is **not** a JSON verdict (no `summary`/`results` document) |
| must | stderr **names the unavailable object id** (its 40-hex oid) or the required path whose object is unavailable |
| **must not** | stderr matches `partial clone \((promisor pack\|extensions\.partialclone\|remote\..*\.promisor)\)` — i.e. none of the r23 metadata-refusal wordings |

P07's concrete pin: stderr must contain `de1d85fdd17416717224bf9faa67ca1009cc9df1`
(the cited, known-missing blob) and must not match the regex above. The r23 base's
stderr for the same fixture is
`could-not-evaluate: <lane>: partial clone (remote.origin.promisor)` — it **fails both**
the "names the token" requirement and the must-not regex, which is exactly the
separation wanted between the blanket refusal and the content-derived exit 2. P09's
concrete pin is the same, with the token `de1d85fdd17416717224bf9faa67ca1009cc9df1` in
a **non-promisor** store (so the base's exit 1 + `unresolved-full-hash` is also excluded).

**(b) Exact (kind, token) pins (the defect list, `--no-errata`).**

| row | exit | defects (exact sorted list) | token rule |
|---|---|---|---|
| P01-P05 | 0 | `[]` | — |
| P06 | 1 | `[("unresolved-full-hash", "0123456789abcdef0123456789abcdef01234567")]` | the hex string as cited, lower-case |
| P07 | 2 | none (not a JSON verdict) | — |
| P08 / P08b | 1 | `[("unresolved-full-hash", "0123456789abcdef0123456789abcdef01234567")]` | idem |
| P09 | 2 | none | — |
| WrongType (Landed-scoped, sibling cell) | 1 | `[("landed-unresolved", "<blob sha>")]` and **no** `unresolved-full-hash` | idem |

The wrong-type cell's "no `unresolved-full-hash`" is the base lookup semantics
(`tools/report-landing-audit.py:139-174` at `0df800e`): the no-peel full-hash lookup
finds the blob, so a missing-object traversal must not turn a **present** blob into
exit 2. My P01-P05 rows are the discriminators for that mutation from this lane's side.

**(c) The pre-amendment grid conflicts, with amended values.** `CritExpected` located
GridOracle's expectations file at
`/fast/scratch/hyaku/kama-r24/GridOracle/tests/report-audit/promisor-grid-expectations.json`
(mtime 15:02:29 — **pre-amendment**; read-only observation by this lane). Its
`reason_classes` are substring bags (`"metadata": ["partial clone", "promisor pack"]`,
`"unavailable"`, `"unknown-citation"`) that do **not** exclude a metadata refusal, so
every exit-2 row additionally needs the must-not regex of (a). Rows that grade the
current arm as exit 2 under the withdrawn reading, and their amended values:

| row | in the pre-amendment file | amended value (current arm) | measurement backing (this lane) |
|---|---|---|---|
| `PG23-unknown-citation-complete-promisor` | exit 2, kinds `null`, reason class `unknown-citation` | **exit 1**, defects `[("unresolved-full-hash", T)]` (plus `("landed-unresolved", T)` when T is cited inside Landed) | refusal-removed repair on the same shape → exit 1 + `unresolved-full-hash`; the plain-store twin (P08b) → exit 1 + `unresolved-full-hash` |
| `PG24-unknown-citation-fleet-promisor` | exit 2, kinds `null` | **exit 1**, same pairs | as PG23 (symmetric: the marking's side does not change local resolution) |
| `PG22-unknown-citation-incomplete-promisor` | exit 2, kinds `null`, "exit 2 under both readings" | **exit 1** with the exact pairs when the cited token is **not** in the bounded missing set (P08 shape); **exit 2** only when the cited token **is** the missing object (P07 shape) | P08 measured: missing set = the unrelated hole only → exit 1 + `unresolved-full-hash` |
| `PG28-unhydrated-blobless-lane` | exit 2, reason `unavailable` | exit 2 **only** if a missing object is one the audit reads; otherwise the twin verdict | P08/P08b: a store with a hole the audit does not read keeps the ordinary verdict (CritExpected's premise-v2 `unhydrated_two_files` gives r22 exit 0) |
| `PG15/PG16-missing-lane-tree*` | exit 2 | exit 2 only if the removed tree is the tip root tree or on a read path (`corpus/`, `registry/`); a historical commit's tree is not read | **not measured by this lane** (tree removal is outside my cell) — the token-scoped rule is consistent with it, but this lane does not certify it |
| missing rows | — | add the P07 shape, the P08 shape and the WrongType Landed cell | §13/§14 |

The pre-amendment readings stay recorded as withdrawn/not-met (preregistration
`expected_after[3]`; L1's `oracle-amendment-1.json`, `landed123640b`); the amended
values above govern the current arm.

**(d) Retained r23 rows.** `F06-lazy-fetch-command` and `F27-filter-only-promisor-remote`
keep exit 1 with the exact pairs and `executed=0`; `F23-promisor-pack-without-config`
keeps exit 2 but its reason pin must become the content-derived form of (a) (it is the
P07 shape: the cited blob is the missing object reachable from the lane commit), never
`promisor pack`. Source: `build/out/CritExpected/p06-p07-reconciliation.json`; my §8
reached the same conclusion for F06/F23/T01 independently.

**(e) Unrun.** The amended values for PG15/PG16 are not measured by this lane; P09's
exit-2 expectation and every exit-2 reason string remain rule-derived (no candidate
exists in this lane); no grid, selftest, full-suite, build, lint or formatter run; no
network transport; no install.

---

## 16. Row P10 (peel path) and its plain twin P10b

Appended after `CritExpected` proposed P10 to cover the **peel** path that P08 does not:
a locally **present** blob cited inside `## Landed changes` while the store carries an
**unrelated** hole. Evidence: `out/OracleLocalBlobType/{fixture_q.py,rows-p10-results.json}`.

**Fixture.** Lane: one round-1 commit by `kama-shokunin` (author time 1000) with file
`f` (blob `T = 4c226b603e6a26a14212b131fcac232ca7318852`, **present**) and
`corpus/blob.txt` (blob `f40b7a32a3e97052a056571100bfc0d4dd76d020`, **deleted from the
store** ⇒ the unrelated hole, still referenced by the present tree). Fleet report:
`## Landed changes` cites the real lane commit **and** `T`; nothing else. `T` lies inside
the Landed span, so the no-peel full-hash scan skips it (`tools/report-landing-audit.py:283`,
`:325`) and only the peeling Landed lookup sees it (`:336`).

**Measured.**

| fact | value |
|---|---|
| `cat-file -t T` | `blob` |
| `cat-file --batch-check` with `T^{commit}` | `4c226b603e6a26a14212b131fcac232ca7318852^{commit} missing` — the peel fails |
| bounded missing set of the lane root | `missing = ["?f40b7a32a3e97052a056571100bfc0d4dd76d020"]` — **T is not in it** |
| base on the **plain** store (P10b) | exit 1, defects exactly `[{"kind": "landed-unresolved", "token": "4c226b603e6a26a14212b131fcac232ca7318852"}]` |
| base on the **promisor-marked** store (P10) | exit 2 (blanket refusal) — the r23 harm |
| refusal-removed probe (both) | exit 1, same single defect |

**Expected (amended).** P10: **exit 1**, defects exactly
`[("landed-unresolved", "4c226b603e6a26a14212b131fcac232ca7318852")]`; must not contain
`unresolved-full-hash`, `landed-ambiguous`, `landed-omitted`,
`landed-section-missing`; summary `by_kind.landed-unresolved 1` and the other four kinds
0, `defects 1`, `uncorrected 1`, `status "failed"`, `required_commits 1`, `reports 1`,
`rounds [1]`. P10b: the same, in a store with no promisor metadata (the no-harm twin).

**What P10 discriminates.** `T` is present, so no availability rule may convert this
peel failure into exit 2: an "any hole ⇒ unknown" rule applied to *peel failures* would
give exit 2 where the amended expectation is the ordinary failed finding. Together with
P08 (no-peel path) the pair covers both citation paths; together with P07/P09 (token in
the missing set ⇒ exit 2) it pins that the exit-2 trigger is the **cited token's**
missing-set membership, not the store's general incompleteness.

**Token provenance.** The `T` of this row is this fixture's `f` blob
(`4c226b603e6a26a14212b131fcac232ca7318852`); it is **not** the `T` of the sibling cell
`CaseWrongTypeCitation` (`6e98d181389d343031fd578c6a775ce0889a8b0d`) — same shape,
different fixture content, and the grid must keep the two tokens apart.

**Unrun.** No candidate existed in this lane; P10's "current" expectation is derived from
the base measurement on the plain twin (P10b, exit 1 + `landed-unresolved` on `T`), from
the refusal-removed probe, and from the amendment's token-scoped rule. No grid, selftest,
full-suite, build, lint or formatter run; no network transport; no install.

---

## 17. Pin precisions: the F06/F27 token literal, and builder-relative token pins

Appended after `CritExpected`'s two precisions to §15(d)/(b).

**(a) F06/F27 token literal.** The token is exactly
`abcdefabcdefabcdefabcdefabcdefabcdefabcd` — 40 characters ending in `abcd` (not
`…bcdef`). Sources in the retained grid: `tests/report-audit/repo-state-grid.py:275`
(`f_lazy_fetch`: `fake2 = "abcdefabcdefabcdefabcdefabcdefabcdefabcd"`) and `:487`
(`f_filter_promisor`: `fake = "abcdefabcdefabcdefabcdefabcdefabcdefabcd"`). It is pinned
for **both** kinds: `("landed-unresolved", "abcdefabcdefabcdefabcdefabcdefabcdefabcd")`
and `("unresolved-full-hash", "abcdefabcdefabcdefabcdefabcdefabcdefabcd")`.

Code-grounded reason for the second kind: in these fixtures the lane has no
`corpus/SOURCES.md`, so `classify_full_hashes` takes its early return
`FULL.findall(text)` (`tools/report-landing-audit.py:283-285`) and does **not** exclude
the Landed span — the fake token is therefore scanned by the no-peel full-hash lookup as
well as by the peeling Landed lookup, and it is absent from the store, so both defects
appear. The contrast is measured in my own P10 twin: a **present** blob cited inside
`## Landed changes` yields `landed-unresolved` **only** (`unresolved-full-hash` 0),
because the no-peel scan resolves it — so the second kind belongs to the *absent* token
rows (F06/F27), not to the wrong-type rows.

**(b) Builder-relative token pins (no hard-coded literals).** Every token in a pin —
defect tokens and exit-2 stderr pins alike — must be taken from the value the builder
returns, because fixture content is what determines it:

| row | builder expression | current literal (byte-fixed content) |
|---|---|---|
| `F23-promisor-pack-without-config` | `g(lane, "rev-parse", f"{lc}:f")` (`repo-state-grid.py:201`) | builder-returned; not fixed here |
| P07 / P09 | `rev-parse <lc>:corpus/blob.txt` (hole blob) | `de1d85fdd17416717224bf9faa67ca1009cc9df1` |
| P10 / P10b | `rev-parse <lc>:f` (present blob `T`) | `4c226b603e6a26a14212b131fcac232ca7318852` |
| P06 / P08 / P08b | hard-coded fabricated token (no object involved) | `0123456789abcdef0123456789abcdef01234567` |
| sibling cell `CaseWrongTypeCitation` | their builder's `T` | `6e98d181389d343031fd578c6a775ce0889a8b0d` |

The literals in the table are **snapshots of byte-fixed fixture content**; they are safe
only while that content is unchanged. The expectations file must therefore derive each
token at runtime from its builder (the grid already has this pattern: the retained grid
passes the builder's value into the report and derives the expectation from it), and the
stderr pin for the exit-2 rows must be matched against the builder-returned oid.

**(c) PG15/PG16.** Remains **unverified** in this lane and in `CritExpected`'s report
(tree removal is outside my cell); the token-scoped rule is consistent with the amended
value but neither lane certifies it.

**Unrun.** No candidate existed in this lane; nothing above is a candidate measurement.
No grid, selftest, full-suite, build, lint or formatter run; no network transport; no
install.

---

## 18. Correction to §16's rationale (expected values unchanged)

Appended after `CritExpected`'s check of §16 against the code. **One rationale sentence in
§16 is wrong and is superseded here; no expected value, pin, token or measurement
changes.**

**Wrong (in §16):** "`T` lies inside the Landed span, so the no-peel full-hash scan skips
it (`tools/report-landing-audit.py:283`, `:325`) and only the peeling Landed lookup sees
it (`:336`)."

**Correct:** the no-peel full-hash scan **does** see `T` — the Landed span is never
excluded from it:

* without `corpus/SOURCES.md` in the lane branch (`source_urls is None`),
  `classify_full_hashes` returns `FULL.findall(text)` over the **whole** report
  (`tools/report-landing-audit.py:285`);
* with `corpus/SOURCES.md`, the condition `lo <= start < hi` forces a token that starts
  inside the Landed span **into** the scanned set (`:293`) — only an exact Registry
  source-URL occurrence is excluded (`classified`).

So in the P10/P10b fixture `T` is seen by **both** lookups. The reason there is **no**
`unresolved-full-hash` defect is not that the scan skipped the Landed span — it is that
the no-peel lookup **resolves** `T`, because the blob is present in the store
(`cat-file --batch-check` → `<T> blob <size>`). Only the **peel** to a commit fails
(`<T>^{commit} missing`), and that failure is what produces the single defect
`("landed-unresolved", T)`.

**Unchanged by this correction:** P10/P10b expected exit 1 with defects exactly
`[("landed-unresolved", "4c226b603e6a26a14212b131fcac232ca7318852")]`, summary
`by_kind.landed-unresolved 1` and the other four kinds 0, `defects 1`, `uncorrected 1`,
`status "failed"`, `required_commits 1`, `reports 1`, `rounds [1]`; must not contain
`unresolved-full-hash`, `landed-ambiguous`, `landed-omitted`, `landed-section-missing`;
the measured base/probe results; and the discriminating weight, which still sits on the
**peel path** precisely because the no-peel lookup resolves `T` — an "any hole ⇒ unknown"
rule applied to peel failures would still produce exit 2 where the expectation is the
ordinary failed finding.

**No other section of this report is affected.** §17(a) already stated the correct
mechanism for F06/F27 (the fake token is absent, so the no-peel scan reports it as
`unresolved-full-hash` **and** the peel reports `landed-unresolved`), and §1's table
describes the no-peel lookup without claiming any Landed exclusion.

**Unrun.** No candidate existed in this lane; nothing above is a candidate measurement.
No grid, selftest, full-suite, build, lint or formatter run; no network transport; no
install.

---

## 19. Correction to §17(a): "Landed tokens are always in the no-peel scan"

Appended after `CritExpected`'s second check. **One rationale phrasing in §17(a) is
superseded; no expected value, pin, token or measurement changes.**

**Wrong (in §17(a)):** the framing that the *early return* at
`tools/report-landing-audit.py:285` is the reason the Landed tokens are scanned, with the
consequence that a `corpus/SOURCES.md`-bearing fixture would behave differently (i.e.
would give `landed-unresolved` alone).

**Correct, general statement:** **Landed-span tokens are always in the no-peel full-hash
scan**, with or without `corpus/SOURCES.md`:

* `source_urls is None` → `return FULL.findall(text), []` (`:285`) scans the whole
  report, Landed span included;
* `source_urls` present → the condition `lo <= start < hi` (`:293`) puts every token that
  starts inside the Landed span **into** `tokens`; only an exact Registry source-URL
  occurrence *outside* the Landed span is diverted to `classified` (URL classification is
  not source-validity proof — see the module docstring).

Hence an **absent** 40-hex token inside `## Landed changes` yields **both** kinds
(`landed-unresolved` from the peeling lookup and `unresolved-full-hash` from the no-peel
lookup) regardless of whether the lane carries `corpus/SOURCES.md`; and a **present**
token inside Landed yields **`landed-unresolved` only**, because the no-peel lookup
resolves it (this is the wrong-type contrast, unchanged).

**Why this matters for the grid.** If an expectation were written as "with
`corpus/SOURCES.md` the Landed token gives `landed-unresolved` alone", a correct
candidate would fail that row: the no-peel scan sees the token in every case. The F06/F27
expectation (`["landed-unresolved", abcdef…abcd]` **and**
`["unresolved-full-hash", abcdef…abcd]`) is therefore SOURCES-independent, and my
P10/P10b expectation (`landed-unresolved` only) rests on the token being **present**,
not on any SOURCES-dependent scan behaviour.

**Unchanged by this correction:** every expected value, pin, token, summary and
measurement in this report, including §13-§18.

**Unrun.** No candidate existed in this lane; nothing above is a candidate measurement.
No grid, selftest, full-suite, build, lint or formatter run; no network transport; no
install.

---

## 20. Cross-lane corroboration of the P10/P10b expectation (no candidate involved)

Appended after `CaseWrongTypeCitation` reported building the same shape independently
(six arms) and recording the token separation on their side. **No expected value, pin,
token or measurement of this report changes; this section records agreement.**

* Their **non-promisor-unrelated-hole** arm (an unrelated missing blob referenced by a
  post-report tree, deleted from the store, cited nowhere; `git log` still works) is the
  same shape as my **P10b**: frozen base exit **1**, exactly one defect
  `("landed-unresolved", T)`. My measurement on the equivalent fixture agrees — base
  exit 1, defect token `4c226b603e6a26a14212b131fcac232ca7318852`, and the
  refusal-removed probe likewise exit 1 with that single defect.
* Their **promisor-metadata-unrelated-hole** arm is my **P10**: frozen base exit 2
  (`partial clone (remote.origin.promisor)`), amended expectation exit 1 with the same
  single defect.
* Their remaining arms (full; promisor-lane-only; promisor-fleet-only;
  promisor-metadata) are the marking variants of the same cell and are all expected
  exit 1 with exactly one `landed-unresolved` defect on `T`.

**Consequence, now established by two independent lanes without any candidate
observation:** an "any hole ⇒ unknown" reading is a **candidate-introduced regression**,
not base behaviour — the plain-store arm yields exit 1 on the r23 base as well as on the
refusal-removed probe, in both lanes' fixtures. The discriminating expectation is
therefore the plain-store arm (exit 1, one `landed-unresolved` defect) and, on the marked
arm, exit 1 with that same defect rather than exit 2.

**Token separation (recorded on both sides):** peer cell `T =
6e98d181389d343031fd578c6a775ce0889a8b0d`; this lane's P10/P10b `T =
4c226b603e6a26a14212b131fcac232ca7318852`; the fabricated token of P06/P08/P08b is
`0123456789abcdef0123456789abcdef01234567`. The three must stay apart in any shared
expectations file.

**Unrun.** No candidate existed in this lane; nothing above is a candidate measurement.
No grid, selftest, full-suite, build, lint or formatter run; no network transport; no
install.
