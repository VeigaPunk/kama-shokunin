# CaseHydratedFleet — oracle case for a hydrated promisor-marked fleet clone

**Lane:** leaf member, no dispatch. **Wave:** round 24, C1 calibration.
**Base observed:** `0df800e896f6bce285a81e794ad4ae1d1e6c3a71` (preregistration base).

## Verdict

The case is **constructed, measured and reproducible**. The base tool
(`tools/report-landing-audit.py`, sha256 `da5041a…5af1`, byte-identical to
the preregistration base) **fails** it in exactly the way the
preregistration predicts — it refuses a promisor-marked fleet on its
metadata alone, even when the fleet's content is complete — and a
metadata-blind variant of the same tool **passes** it with 0 failures. The
expectations are therefore both **specified before implementation** and
**demonstrably reachable**; they are not vacuous.

This is a case *builder*, not a repair. I did not modify
`tools/report-landing-audit.py` or any production file.

---

## 1. What the case is

One offline oracle case with a **single variable**: the audited **fleet**
repository. The audited **lane** is always a plain, complete, non-promisor
local repository, so nothing else can explain a verdict difference.

| arm | fleet repository | content |
|---|---|---|
| `full` | plain full `file://` clone (`--no-local`, no filter) | complete |
| `hydrated` | genuine `--filter=blob:none --no-local --no-checkout file://` clone, **promisor metadata retained**, missing blobs supplied by an **offline plain file copy** of the origin's object store | complete |
| `unhydrated` | the same blob:none clone, left alone | the report blob is missing |
| `gap` | the same blob:none clone, hydrated **except** `notes.txt` (an object no evidence depends on) | required evidence complete, one unrelated blob missing |

Two report **shapes** (decided from the constructed history, before any
candidate run): `clean` (the report cites both pre-cutoff lane commits) and
`omission` (it cites one, so the other is `landed-omitted`).

Fixed history: lane commits `a` = `round-1: work` (author t=1000) and
`b` = `round-1: extra` (author t=1500), author `kama-shokunin`; the fleet
report `.ufo/reports/round-1/kama.md` first added at author t=2000, so
**cutoff = 2000** and both lane commits are required.

## 2. Expected exits and findings (specified before implementation)

| arm | shape | exit | findings | stderr |
|---|---|---|---|---|
| `full` | clean | 0 | — | empty |
| `full` | omission | 1 | `landed-omitted` | empty |
| `hydrated` | clean | **0** | — | **empty — no refusal at all** |
| `hydrated` | omission | **1** | `landed-omitted` | **empty — no refusal at all** |
| `unhydrated` | clean | 2 | none (no verdict) | refusal naming the unavailable report object |
| `unhydrated` | omission | 2 | none (no verdict) | refusal naming the unavailable report object |
| `gap` | clean | 0 | — | empty (**advisory**, §6) |
| `gap` | omission | 1 | `landed-omitted` | empty (**advisory**, §6) |

Three load-bearing assertions:

1. **Same report bytes.** The `hydrated` fleet must yield *byte-identical*
   report content to the `full` fleet. Measured SHA-256: `a50b7523a7309c85…`
   (clean), `a04146349ad4a784…` (omission). The comparison is byte-exact.
2. **Same cutoff.** `hydrated` and `full` must both yield cutoff `2000`.
   The cutoff is read from the fleet's *history*, so it is the value most
   likely to move if a candidate treats a promisor-marked fleet's history as
   unavailable.
3. **No lazy fetch.** Three independent observations per arm: the fleet's
   pack set is unchanged across the audit; its object count is unchanged;
   and the fleet **origin is deleted before the audit**, so
   `git ls-remote origin` fails with rc=128 — a lazy fetch could not have
   succeeded quietly even if attempted. The tool under test runs every git
   call with `--no-lazy-fetch` (`tools/report-landing-audit.py:93-96`).

**Refusal discriminator.** `hydrated` must not merely *reach* the right
exit code; it must produce **no refusal**. The builder greps stderr for
`partial clone`, `shallow repository`, `rewrites history`, `not sha1`,
`not a repository top level`, `could-not-evaluate` and fails the row if any
appear. Conversely `unhydrated` must exit 2 *with* a refusal. This is the
preregistration's "missing required object evidence is exit2, never guessed
absence": the `unhydrated` fleet holds no report blob, so the audit cannot
be evaluated and must not invent a clean or failed verdict.

## 3. Measurements

### 3.1 Base (`--expect base`): 4 failures — the case discriminates

```
ok     full/clean        exit=0 kinds=[]        cutoff=2000
FAIL   hydrated/clean    exit=2  … refused: ['partial clone', 'could-not-evaluate']
       stderr: could-not-evaluate: …/fleet: partial clone (promisor pack)
ok     unhydrated/clean  exit=2  … partial clone (promisor pack)
ok     gap/clean         exit=2  … partial clone (promisor pack)
ok     full/omission     exit=1 kinds=['landed-omitted'] cutoff=2000
FAIL   hydrated/omission exit=2  … refused: ['partial clone', 'could-not-evaluate']
FAIL pair full vs hydrated shape=clean
FAIL pair full vs hydrated shape=omission
arms=8 failures=4 expect=base
```

The refusal comes from `tools/report-landing-audit.py:454-457` (the
`.promisor` pack marker) — and, on a git 2.56 clone, that is the *only*
detector that fires, because `clone --filter=blob:none` writes only
`remote.origin.promisor` and `remote.origin.partialclonefilter`, not
`extensions.partialclone`. See §5.

### 3.2 Achievable (`--expect candidate`): 0 failures

A metadata-blind probe variant of the same tool (`audit-metadata-blind-probe.py`
— the base with the two promisor refusals at `:454-465` removed, kept **only**
to show the expectations are reachable; **not** a candidate and not proposed
for integration) gives:

```
ok full/clean        exit=0 kinds=[]               cutoff=2000
ok hydrated/clean    exit=0 kinds=[]               cutoff=2000   ← same bytes, same cutoff, no refusal
ok unhydrated/clean  exit=2  cannot read .ufo/reports/round-1/kama.md at fleet HEAD
ok gap/clean         exit=0 kinds=[]               cutoff=2000
ok full/omission     exit=1 kinds=['landed-omitted'] cutoff=2000
ok hydrated/omission exit=1 kinds=['landed-omitted'] cutoff=2000   ← same bytes, same cutoff, no refusal
ok unhydrated/omission exit=2  cannot read .ufo/reports/round-1/kama.md at fleet HEAD
ok gap/omission      exit=1 kinds=['landed-omitted'] cutoff=2000
arms=8 failures=0 expect=candidate
```

Pair failures 0, byte/cutoff failures 0, scratch escapes 0.

### 3.3 Non-vacuity: two single-detector mutations, both killed

The base has **two** promisor detectors: the `.promisor` pack marker
(`:454-457`) and the config key (`:462-465`). I mutated the base to remove
**only one** at a time:

| mutation | `hydrated/clean` | `hydrated/omission` | result |
|---|---|---|---|
| remove only the pack-marker detector | exit 2, `partial clone (remote.origin.promisor)` | exit 2 | **killed** (4 failures) |
| remove only the config-key detector | exit 2, `partial clone (promisor pack)` | exit 2 | **killed** (4 failures) |

So the case cannot be passed by fixing one detector. To guarantee that, the
builder writes `extensions.partialclone=blob` explicitly on the blobless
arms (git 2.56 does not write it on clone), so all three markers
(`remote.origin.promisor`, `remote.origin.partialclonefilter`,
`extensions.partialclone`) plus the `.promisor` pack marker are present on
every blobless arm.

### 3.4 Determinism

Two independent runs produced identical commit ids, report digests, cutoffs,
exits, findings and pair results.

## 4. Fixture discipline — evidence

* **No fixture escaped scratch.** Every path is created under the
  caller-supplied root and the builder asserts it (`escape_check` walks the
  tree for stray paths): `escapes=0` in both evidence files. Nothing was
  written outside `/fast/scratch/hyaku/kama-r24/CaseHydratedFleet/`.
* **No transport beyond one local `file://` clone.** Hydration is
  `shutil.copyfile` of loose object files (plus any `.pack`/`.idx`). No
  network transport, no script execution, no execution payload.
* **Nothing executable in any fixture.** The builder asserts the config and
  the executable hooks are empty on both the lane and the fleet (no
  `core.sshCommand`, `gpg.program`, hook, `filter.*` or `credential.helper`).
* **The fleet origin is deleted before the audit**, so the dead-remote proof
  is positive, not assumed.
* **The real repositories are untouched** by this lane: the lane repo's only
  untracked addition from me is
  `.ufo/waves/round-24/build/out/CaseHydratedFleet/`; the modified
  `corpus/QUALITY.md`, `corpus/SOURCES.md` and the fleet's `.ufo/state/*`
  are sibling agents' work, not mine. I did not write to the lane's Git
  index, `.jj`, the fleet root or any operator config.

## 5. Findings for the wave

1. **The base's fleet-side promisor refusal is metadata-only.**
   `tools/report-landing-audit.py:454-457` and `:462-465` refuse a
   repository for *declaring* a promisor remote, without asking whether the
   evidence it needs is present. On a complete, locally hydrated
   promisor-marked fleet this is a false refusal — exit 2 where the
   preregistration expects exit 0 / exit 1 with the same findings as the
   full clone. Measured above.

2. **Two detectors, and only one of them fires on git 2.56.**
   `clone --filter=blob:none` writes `remote.origin.promisor=true` and
   `remote.origin.partialclonefilter=blob:none` but **not**
   `extensions.partialclone` (observed `git config --local --list` on a
   git 2.56.0 clone). The base's first check to fire is therefore the
   `.promisor` pack marker. A repair that removes only the config-key check
   leaves the fleet case failing; a repair that removes only the pack
   marker leaves it failing through the config key. **Both must go**, and
   the case now pins that (§3.3).

3. **The refusal reason must move from "metadata" to "evidence".** In the
   base, the `unhydrated` arm exits 2 for the *wrong* reason (it is refused
   as a partial clone, not because the report blob is unavailable). After
   the repair the same arm must exit 2 because `git show HEAD:…/kama.md`
   fails — the preregistration's "missing required object evidence is
   exit2, never guessed absence". The `hydrated`/`unhydrated` refusal
   asymmetry in §2 is what pins this; without it, a candidate that simply
   never evaluates a promisor-marked fleet would pass the exit-code table.

4. **The cutoff is reachable without the blob.** Measured: the cutoff
   (2000) is computable in the `unhydrated` arm too, because
   `git log --diff-filter=A --format=%at` walks commits and trees only. So
   the cutoff is *not* a discriminator of completeness on its own; the
   report **bytes** are. Both are asserted anyway, since a candidate that
   treated a promisor-marked fleet's history as unavailable would move the
   cutoff while leaving the bytes intact.

5. **The `gap` arm is a policy fork the wave must declare.** The
   preregistration says "content completeness **and** availability of
   required evidence determine the outcome" and separately "an unavailable
   **required** commit/tree/blob/report object: exit2". `gap`'s missing blob
   (`notes.txt`) is **not** required by any evidence. A candidate that
   requires only the required evidence answers exit 0 / exit 1 like the full
   clone; a candidate that demands whole-repository closure answers exit 2.
   Both readings are defensible, so I made `gap` **advisory**: it is
   recorded and reported, never fails the run, and is excluded from the
   pair-equality and byte/cutoff kill checks. **The wave must state which
   reading it implements.** This is the one open policy question in this
   lane.

## 6. Residual risk and verification gaps

* **Not measured on a real candidate.** I have no repaired tool to run. The
  achievable result comes from a metadata-blind probe, which shows the
  expectations are *reachable*, not that any particular repair satisfies
  them. A real candidate must be run against this builder.
* **The probe removes the refusals wholesale.** It does not implement the
  preregistration's "availability of required evidence" rule; it simply
  stops refusing. A candidate that implements the rule properly (rather
  than dropping the check) is untested here — the `unhydrated` arm is the
  row that would catch a candidate that drops the check *and* then guesses
  a verdict.
* **Fleet side only.** The lane side is plain in every arm. The lane-side
  promisor case belongs to the sibling `CaseHydratedLane` lane.
* **Not covered here:** a citation resolvable only in the promisor remote
  ("unknown citation in a promisor-backed repository is exit2 unless
  resolved locally by another audited repository") — sibling
  `CaseUnreachableCitation`; sha256 object format; alternates; grafts;
  shallow boundaries; replace refs; `log.follow`; `log.showSignature`;
  `i18n.logOutputEncoding`; `.mailmap`; the historical rounds 10–22 ledger.
* **No measurement of the historical ledger** and no full-suite run, per the
  wave contract.
* **`gap` policy is unresolved** (§5.5).

## 7. Artifacts

Under `.ufo/waves/round-24/build/out/CaseHydratedFleet/`:

| file | sha256 / content |
|---|---|
| `hydrated_fleet_case.py` | `69724c99b9207bd2eabc62a0d8fb81b4b14be282cee27d0027b5e519e2de2b7e` — the case builder |
| `RECIPE.md` | `26d7fcd2b4e8fb5cd2abf130810cf2969acf204700a3174dd9d5de5f64ff20ca` — the recipe with the expected exits/findings stated first |
| `evidence-base.json` | base run: 4 failures |
| `evidence-achievable.json` | metadata-blind probe run: 0 failures |
| `run-base.txt`, `run-achievable.txt` | the two recorded runs |
| `run-mutations.txt` | both single-detector mutations, killed |
| `audit-metadata-blind-probe.py` | `a07f29cd00aa2dd178c9be0b6f80fb5965ebf6187a2b0d34b0cbab4c5133ccc6` — the probe (not a candidate) |

Scratch (not artifacts): `/fast/scratch/hyaku/kama-r24/CaseHydratedFleet/`
— `run-base/`, `run-cand/`, `final/`, `mut/`, `probe/`, `probe2/`.

## 8. How to adopt

```sh
OUT=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/CaseHydratedFleet
SCRATCH=/fast/scratch/hyaku/kama-r24/CaseHydratedFleet

python3 $OUT/hydrated_fleet_case.py \
  --root $SCRATCH/run-<arm> \
  --tool <the candidate tools/report-landing-audit.py> \
  --expect candidate --out $SCRATCH/run-<arm>/evidence.json
```

Exit 0 means the candidate satisfies every assertion in §2. Exit 1 names the
failing row, its expected value, the observed exit/kinds/cutoff, the refusal
markers found and any premise violation.

## 9. Tooling

No packages installed, no system changes, no pacman transaction. Only
`git 2.56.0` and `python3 3.14.8` (both already present) were used.
