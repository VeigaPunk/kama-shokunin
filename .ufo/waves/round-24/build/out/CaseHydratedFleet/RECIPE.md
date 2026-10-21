# CaseHydratedFleet — oracle recipe and expected outcomes

Round 24, C1 calibration. One offline oracle case: a **genuine `file://`
`blob:none` fleet clone, hydrated by explicit local copying**, must be
auditable with the **same report bytes, the same cutoff and the same
substantive verdict** as an otherwise identical full clone — with **no lazy
fetch**.

This file states the expected exits and findings **before** any candidate
implementation is exercised. The builder that realises it is
`hydrated_fleet_case.py` in this directory; the recorded runs are
`run-base.txt` (the r23 base tool) and `run-achievable.txt` (a
metadata-blind probe variant, kept only to show the expectations are
reachable, not to stand in for a candidate).

---

## 1. What varies and what does not

The **audited lane** is always a plain, complete, non-promisor local
repository. The **audited fleet** is the only variable.

| side | property | value |
|---|---|---|
| lane | promisor metadata | none |
| lane | closure | complete (`rev-list --objects --all --missing=print` → no `?oid`) |
| lane | configured programs | none |
| lane | commits | `a` = `round-1: work` (author t=1000), `b` = `round-1: extra` (author t=1500), author `kama-shokunin` |
| fleet | report | `.ufo/reports/round-1/kama.md`, first added by a fleet commit at author t=2000 → **cutoff 2000** |
| fleet | promisor metadata | `remote.origin.promisor=true`, `remote.origin.partialclonefilter=blob:none`, `extensions.partialclone=blob`, and a `.promisor` pack marker |

Both lane commits are pre-cutoff (1000, 1500 < 2000), so both are *required*
commits in every shape.

## 2. Arms

| arm | fleet repository | content state |
|---|---|---|
| `full` | plain full `file://` clone (`--no-local`, no filter) | complete |
| `hydrated` | real `--filter=blob:none --no-local --no-checkout file://` clone, promisor metadata **retained**, missing blobs supplied by a **plain file copy of the origin's object store** | complete |
| `unhydrated` | the same blob:none clone, left alone | incomplete (the report blob is missing) |
| `gap` | the same blob:none clone, hydrated **except** `notes.txt` — an object no evidence depends on | complete for all required evidence; one unrelated blob missing |

Hydration is a file copy (`shutil.copyfile` of loose object files, plus any
`.pack`/`.idx`). There is no transport, no network and no program in the
hydration step. The `file://` transport is used **once**, for the initial
clone.

`extensions.partialclone` is written explicitly on the blobless arms: git
2.56 writes only the two `remote.origin.*` keys, so a candidate that fixed
only one of the base's two detectors (the `.promisor` pack marker at
`tools/report-landing-audit.py:454-457`, the config key at `:462-465`) would
still refuse every arm. With all three markers present, the case cannot be
passed by fixing only one detector.

## 3. Shapes

| shape | report cites | expected defect |
|---|---|---|
| `clean` | `a` and `b` | none |
| `omission` | `a` only | `landed-omitted` on `b` |

## 4. Expected exits and findings

Derived from the constructed history above, **not** from any candidate run.

| arm | shape | expected exit | expected findings | expected stderr |
|---|---|---|---|---|
| `full` | clean | 0 | none | empty |
| `full` | omission | 1 | `landed-omitted` | empty |
| `hydrated` | clean | **0** | none | **empty — no refusal at all** |
| `hydrated` | omission | **1** | `landed-omitted` | **empty — no refusal at all** |
| `unhydrated` | clean | 2 | none (no verdict) | a refusal naming the unavailable report object |
| `unhydrated` | omission | 2 | none (no verdict) | a refusal naming the unavailable report object |
| `gap` | clean | 0 | none | empty — **advisory, see §6** |
| `gap` | omission | 1 | `landed-omitted` | empty — **advisory, see §6** |

### 4.1 The three load-bearing assertions

1. **Same report bytes.** The `hydrated` fleet must yield byte-identical
   report content to the `full` fleet. Measured SHA-256:
   `a50b7523a7309c854a40bcbb1dab0e1140e8448874d1d97f8b37bcd904d7cd6b`
   (clean) and
   `a04146349ad4a7844e2bb12e58bcff162a8f5963b61089b4e0d961ef035ac1d3`
   (omission). The comparison is byte-exact, not just digest-equal.

2. **Same cutoff.** `hydrated` and `full` must both yield cutoff `2000`.
   The cutoff is the author time of the fleet commit that first added the
   report; it is derived from the fleet's history, so it is the value most
   likely to move if the candidate treats a promisor-marked fleet's history
   as unavailable.

3. **No lazy fetch.** Verified three ways, per arm:
   - the fleet's pack set is unchanged across the audit (a fetch adds a
     `.pack`/`.idx` pair);
   - the fleet's object count is unchanged (a fetch adds objects);
   - the fleet origin is **deleted before the audit**, so `git ls-remote
     origin` fails with rc=128 — a lazy fetch could not have succeeded
     quietly even if the auditor had tried.

   The auditor under test runs every git call with `--no-lazy-fetch`
   (`tools/report-landing-audit.py:93-96`), so the fixture cannot fetch even
   if the audit attempted it.

### 4.2 The refusal discriminator

`hydrated` must not merely *reach* the right exit code: it must produce
**no refusal**. The builder greps the stderr for refusal markers
(`partial clone`, `shallow repository`, `rewrites history`, `not sha1`,
`not a repository top level`, `could-not-evaluate`) and fails the row if
any appear. A refusal that happens to carry exit 2 with the right shape is
the r23 harm in another guise, and the row must not be satisfiable by it.

Conversely `unhydrated` must exit 2 **with** a refusal. Under the base tool
the unhydrated arm's exit 2 comes from the metadata check, not from the
missing evidence; after the repair it must come from the unavailable
required object instead. The builder therefore requires a refusal marker on
`unhydrated` and forbids one on `hydrated`.

This is the preregistration's "missing required object evidence is exit2,
never guessed absence": the `unhydrated` fleet holds no report blob, so the
audit cannot be evaluated and must not invent a clean or failed verdict.

## 5. Pair equality

`full` and `hydrated` must agree on exit code, defect kinds **and** cutoff,
for both shapes. This is the direct form of "restore correct clean/omission
verdicts" and is checked independently of the per-row exit table, so a row
that passes by accident still fails the pair.

## 6. The `gap` arm is advisory

The preregistration says "content completeness **and** availability of
required evidence determine the outcome", and separately "an unavailable
**required** commit/tree/blob/report object: exit2". The `gap` arm's missing
blob (`notes.txt`) is **not** required by any evidence:

- a candidate that requires only the *required* evidence answers
  exit 0 / exit 1, like the full clone;
- a candidate that demands whole-repository closure answers exit 2.

Both readings are defensible. The `gap` row therefore **never fails the
run**; it is recorded and reported, and the wave must declare which
reading it implements. It is excluded from the pair-equality check and from
the byte/cutoff kill check for the same reason.

## 7. Reproducing

```sh
OUT=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/CaseHydratedFleet
SCRATCH=/fast/scratch/hyaku/kama-r24/CaseHydratedFleet

# the base (r23) behaviour: the case must FAIL here
python3 $OUT/hydrated_fleet_case.py \
  --root $SCRATCH/run-base \
  --tool /home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py \
  --expect base --out $SCRATCH/run-base/evidence.json

# the achievable behaviour (metadata-blind probe, NOT a candidate)
python3 $OUT/hydrated_fleet_case.py \
  --root $SCRATCH/run-cand \
  --tool $OUT/audit-metadata-blind-probe.py \
  --expect candidate --out $SCRATCH/run-cand/evidence.json
```

Expected: `--expect base` reports 4 failures (2 pair failures + 2 refusal
failures on the `hydrated` arms); `--expect candidate` reports 0.

## 8. Fixture discipline

* Every path is created under the caller-supplied scratch root and the
  builder asserts it (`escape_check`): no fixture path may live outside the
  scratch root.
* Only local `file://` transport, only for the initial clone. No network
  transport, no script execution, no execution payload.
* No repository program is configured or invoked in any fixture: no
  `core.sshCommand`, no `gpg.program`, no hook, no `filter.*` helper, no
  `credential.helper`. The builder asserts the config and the executable
  hooks are empty for both the lane and the fleet.
* Every fixture git call uses `--no-lazy-fetch`.
* The fixture is deterministic: two independent runs produced identical
  commit ids, report digests, cutoffs, exits and findings.

## 9. What this case does NOT establish

* It does not cover the **lane** side being promisor-marked; the lane is
  plain in every arm here. (The sibling `CaseHydratedLane` covers that.)
* It does not cover a **citation that resolves only in the promisor remote**
  — the "unknown citation in a promisor-backed repository is exit2 unless
  resolved locally by another audited repository" rule. (The sibling
  `CaseUnreachableCitation` covers that.)
* It does not cover `extensions.objectFormat=sha256`, alternates, grafts,
  shallow boundaries, replace refs, `log.follow`, `log.showSignature`,
  `i18n.logOutputEncoding` or `.mailmap`. Those are outside this wave's
  claim and are not re-litigated here.
* It does not measure the historical rounds 10–22 ledger.
* It exercises the auditor's *fleet* read path only. It says nothing about
  the lane's `git log` path under promisor marking.
