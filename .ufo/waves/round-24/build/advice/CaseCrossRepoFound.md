# CaseCrossRepoFound — offline oracle case: token absent in the promisor lane, locally present in the fleet

**Lane:** leaf reviewer/case-builder, `CaseCrossRepoFound-2`. **Base:** `0df800e896f6bce285a81e794ad4ae1d1e6c3a71` (r23) — the auditor under test is `tools/report-landing-audit.py`, byte-identical at `0df800e` and at the current `d1b9d95` (`git diff 0df800e d1b9d95 -- tools/report-landing-audit.py` is empty).
**Round:** 24, C1 calibration 7→7 (operability-harm repair). **Status:** case specified, fixture built, expected exits fixed before any candidate implementation, discrimination measured.

---

## 1. The case

A lane under audit is a **promisor-marked partial clone** (git's own `--filter=blob:limit=1024` clone: `remote.origin.promisor=true`, `remote.origin.partialclonefilter=blob:limit=1024`, `core.repositoryformatversion=1`, a paired `<pack>.promisor` next to `<pack>.pack`). Its local object store is missing exactly **one** object: the cited source blob, which the size filter left out.

The report cites three tokens:

| token | where | in the lane? | in the fleet? |
|---|---|---|---|
| `f7b2c0c1…` lane commit | `## Landed changes` | yes (commits are not filtered) | no |
| `134d48e1…` source blob | report body | **no** (filtered out; present in the lane's upstream) | **yes** (the fleet vendors the file byte for byte, so both sides hold one blob OID) |
| `ed493219…` fleet commit | `## Landed changes` | **no** | **yes** |

Both fleet-resident tokens are absent from the lane's local object store and present in the fleet's. The audit must resolve them **from the fleet**, and must **not refuse the lane before it has looked at the fleet**.

The two fleet-resident tokens cover the two lookup shapes the auditor has:

* the **bare** lookup (`lookup(repos, tokens)` — the body scan, `tools/report-landing-audit.py:139`, called at `:325`), and
* the **peeled** lookup (`lookup(repos, tokens, "^{commit}")` — the Landed-section scan at `:336-337`), whose implementation asks the **bare name first** through a recursive call (`:148-150`, the recursive call at `:149`) and only then loops over the repositories with the peeled names (`:152-153`).

### Expected result (fixed before implementation; twin-derived)

| arm | base (r23 `0df800e`) | expected after the r24 repair |
|---|---|---|
| promisor-marked lane | **exit 2**, `could-not-evaluate: <lane>: partial clone (promisor pack)` | **exit 0**, no findings |
| full-clone twin (same upstream, same commits, same report, same fleet, same binary, same run) | **exit 0**, `status: clean`, `by_kind` all zero | exit 0, no findings |

The expectation is the **twin's observed verdict**, not a value copied from any implementation under test. The grading rule is *equality with the twin* — "not exit 2" is weaker and is not the contract.

---

## 2. Why this case exists (what it catches)

Measured with four bounded mutants of the base auditor (`out/CaseCrossRepoFound/mutants.py`, evidence `evidence-mutants.json`):

| variant | exit | findings | case verdict |
|---|---|---|---|
| base (r23), no edit | 2 | — | **fails** (blanket refusal) |
| **M1** naive repair: remove the up-front promisor refusal only | 0 | [] | passes |
| **M2** M1 + resolve citations in the lane only (`repos = (lane_repo,)`) | 1 | `landed-unresolved`, `unresolved-full-hash` ×2 | **fails** |
| **M3** M1 + raise `EvalError` on a lane-side miss *before* the fleet is consulted | 2 | — | **fails** (`required object … is not available in a promisor-backed repository`) |
| **M4** M1 + raise `EvalError` **inside the bare recursion** of the peeled lookup (`:147-151`) | 2 | — | **fails** (same reason as M3) |

So the case rejects: keeping the up-front refusal (base), stopping the cross-repository lookup (M2), giving up before the fleet is consulted (M3), and refusing *inside* the peeled lookup's bare recursion before the fleet is read (M4).

M3 and M4 carry a **different reason string** from the base's `partial clone (promisor pack)`, so a grid that pins only "exit 2" would still miss them — the row must pin exit **0** / equality with the twin.

**Pin the row's expectation, not the mutants' failure shape.** The exits in the table above are the *base's* semantics for those mutants. Under the repair shape sketched in `advice/ConnPlan.md` (`lookup` returning a `notcommit`/`unknown` status instead of raising, with uncertainty decided at store level), a lane-only lookup would surface as exit 2 (unknown) rather than exit 1 (`unresolved-full-hash`): the row still fails, but the *shape* of the failure differs. Only the normative expectation — promisor lane == full-clone twin, exit 0, no findings — may be pinned; the mutant rows above are evidence that the row is discriminating, not expected values for the grid.

My case is compatible with that design as stated: all three cited tokens are **valid** citations (the lane commit, the source blob, the fleet's own commit) and all resolve, so neither the `notcommit` nor the `unknown` branch is reached — which is also why this row must not be used to probe the preregistration's conflict between item 1 (complete promisor parity) and item 4 (uncertainty ⇒ exit 2); the `CaseUnknownCitation` cell owns that direction.

**M4 is why the fleet-resident commit is in the Landed section.** Measured: with the report's Landed section listing only the lane commit (the first version of this fixture), M4 exits **0** — the case did not catch it, because the bare recursion only runs on the peeled path and its only token was present in the lane. After the fleet-resident commit was added to the Landed section, M4 exits **2** and is caught. (Flagged by `KamaR23-2.ConnPlan-2`; the load-bearing constraint is that the uncertainty decision — "absent everywhere while some audited store is promisor-backed ⇒ exit 2" — must be taken **after every repository has been consulted**, and `lookup()` must **return a status, not raise**.)

**Implementation constraint this case pins.** A citation resolves against the whole object store, not the branch closure, so no `rev-list`/`rev-list --objects` closure test can decide "is this citation missing" — only `cat-file --batch-check` can, and it must be asked of **every** audited repository before any repository-side absence is treated as evidence.

**Pairing requirement (do not drop).** M1 passes this row. This row therefore does **not** by itself force availability checking; it must be graded in the same arm as a row whose lane genuinely lacks a required object that no other audited repository holds (the round-23 `f_promisor_pack` row, `tests/report-audit/repo-state-grid.py:195`). Paired, M1 turns that row into a false `unresolved-full-hash` exit 1 and the repair must add availability checking. This row is what forbids the opposite over-correction (M2, M3, M4). Same requirement as the sibling `CaseMarkerLane` fragment, from the opposite side.

**Complementarity with the opposite-direction row (for the executor and the adopting grid).** This row and the `CaseUnknownCitation` cell fix both directions and must be graded together:

* **this row** — a citation resolvable in another audited repository must resolve (exit 0). A premature refusal (M3/M4) yields a **false exit 2** here.
* **`CaseUnknownCitation`** — a citation absent from *every* audited repository while a store is promisor-backed must be **exit 2 (unknown)**, not an `unresolved-full-hash` defect. M1-style removal of the refusal without the unknown rule yields a **false defect** (exit 1 where exit 2 is required) there.

These are the two halves of the mutant pair already listed for `MutationOracle` ("skip uncertainty lookup refusal" vs "premature unknown rejection"). Neither row is sufficient alone.

---

## 3. The fixture (reproducible recipe)

Everything is local and offline. The only transport is the local `file://` clone that creates the partial clone — git's filter machinery needs it; no host is contacted, no credential or program is configured, nothing is executed.

```
origin/   git init -b master; config uploadpack.allowFilter true
          commit "round-1: work"  @1000 by kama-shokunin  -> notes.md  (4097 bytes, the cited blob)
          commit "registry: errata" @1100                  -> registry/report-landing-errata.tsv (empty)

lane/     git -c protocol.file.allow=always clone --no-local --no-checkout \
            --filter=blob:limit=1024 file://<origin> lane
          -> promisor-marked; notes.md's blob is ABSENT from the local store

twin/     git -c protocol.file.allow=always clone --no-local file://<origin> twin
          -> the same upstream, complete (the control that fixes the expectation)

fleet/    git init -b master
          commit "round-1: evidence vendor" @1500 -> vendor/notes.md  (byte-identical content
                                                        => the same blob OID as the lane's)
          commit "round-1: report"        @2000 -> .ufo/reports/round-1/kama.md
                    "# kama round 1\n\nblob <BLOB>\n\n## Landed changes\n\n- <LANE_COMMIT>\n- <FLEET_COMMIT>\n"
```

Two placement rules learned while building the fixture (both measured):

* the **blob** is cited in the report **body**, before `## Landed changes`: a token inside the Landed section is peeled with `^{commit}`, and a blob there becomes a `landed-unresolved` defect (measured — that mistake was made and corrected while building the grid fragment);
* the **fleet commit** is cited **inside** the Landed section on purpose: that is the path that exercises the peeled lookup and its bare recursion.

Commands to run the case (bounded, local):

```
python3 .ufo/waves/round-24/build/out/CaseCrossRepoFound/xrepo_found_case.py \
        --workdir /fast/scratch/hyaku/kama-r24/CaseCrossRepoFound/fix \
        --lane-repo /home/vgpnk/Projects/shokunin/kama-shokunin \
        --out .../evidence-case.json
python3 .ufo/waves/round-24/build/out/CaseCrossRepoFound/mutants.py \
        --workdir /fast/scratch/hyaku/kama-r24/CaseCrossRepoFound/mut \
        --lane-repo /home/vgpnk/Projects/shokunin/kama-shokunin \
        --out .../evidence-mutants.json
```

---

## 4. Premises (observed, `evidence-case.json`)

| # | premise | observed |
|---|---|---|
| P1 | the lane is promisor-marked with git's own metadata | `remote.origin.promisor=true`, `remote.origin.partialclonefilter=blob:limit=1024`, `core.repositoryformatversion=1`, `pack-7203317….promisor` paired with `pack-7203317….pack` |
| P2 | the cited blob `134d48e195528a24f3e7322863c3f5aae6476e03` is absent from the lane's local store | `git rev-list --objects --all --missing=print` → `?134d48e1…`; `git cat-file --batch-check` → `… missing` |
| P3 | the blob exists in the lane's promisor upstream, so the absence is "not fetched yet", not "never existed" | `git -C origin cat-file -t` → `blob` |
| P4 | the blob is present in the fleet's local store | `git -C fleet cat-file -t` → `blob`, size 4123 |
| P5 | the lane is otherwise complete for this audit | errata blob local (`e69de29b…`), not shallow, sha1, top level, no `info/grafts` |
| P6 | the fleet holds the report at HEAD, cutoff = 2000 | `git -C fleet show HEAD:.ufo/reports/round-1/kama.md` contains both fleet-resident tokens; `--diff-filter=A` → `2000` |
| P7 | the lane has the cited lane commit locally (commits are not filtered) | `cat-file -t f7b2c0c1…` → `commit` |
| P13 | the fleet-resident commit `ed49321974a15e71241353bed979591ab0eb7b70` is absent from the lane and present in the fleet | lane `cat-file --batch-check` → `… missing`; fleet `cat-file -t` → `commit` |
| P8 | the twin is complete | `--missing=print` → empty |
| P9/P11 | **the audit fetched nothing**: the lane's object inventory (all present objects + pack file names) is byte-identical before and after the run | `P11_no_fetch = true` |
| P12 | the cited blob is still absent from the lane after the audit | `P12_blob_still_absent = true` |

`git fsck` on the promisor lane prints **nothing** (git tolerates the missing promisor object) — the fixture is a legitimate partial clone, not a corrupted repository.

### The expected verdict follows from the tool's own resolution path

With the base module imported and its own `lookup()` used (`tools/report-landing-audit.py:139`):

```
lookup([lane, fleet], [blob])        -> {'134d48e1…': 'found'}
lookup([lane],        [blob])         -> {'134d48e1…': 'missing'}
```

The cross-repository resolution **already exists** in `audit_round` (`repos = (lane_repo, fleet_repo)`, `tools/report-landing-audit.py:320`; `:339` is the `if state == "missing":` branch of the Landed lookup). The r23 damage is only the up-front refusal in `check_history_repo` (`:457` "partial clone (promisor pack)", `:465` "partial clone ({key})" for `extensions.partialclone` / `remote.*.promisor`). So the expected exit 0 needs no new resolution machinery — it needs the refusal replaced by availability checking, exactly as the preregistration states ("Metadata-only declarations do not establish incompleteness; content completeness and availability of required evidence determine the outcome").

---

## 5. Safety and containment

* **No network.** The only transport is the local `file://` clone at fixture-build time. The audit itself must not fetch, and that is asserted (P9/P11/P12), not assumed.
* **No program execution.** No `core.sshCommand`, `uploadpack.*` hook, `credential.helper`, `gpg.program` or `filter.*` is configured anywhere in the fixture; the audit's `GIT_ISOLATION` (`--no-replace-objects`, `--no-lazy-fetch`, `-c log.showSignature=false`, `-c log.mailmap=false`) is left intact. This case is **not** a transport test and **not** a script-execution test.
* **A trap worth recording:** `git cat-file --batch-check` **without** `--no-lazy-fetch` in a promisor repo *silently performs the lazy fetch* and the object then appears local (observed during construction: the 4097-byte blob reappeared after an unguarded `cat-file`, while the empty blob stayed missing). Every premise check in this case therefore uses `git --no-lazy-fetch …` or `rev-list --missing=print` (which never fetches). A grid that checks "is the blob still missing?" with a bare `cat-file` will observe a false absence and pass a broken repair. Note the scope difference: `rev-list --objects --missing=print` is whole-repo scoped (it prints every missing object with a `?` prefix), so for a **cited token** only `cat-file --batch-check` can decide absence.
* **No fixture escaped the scratch area.** All fixture repositories live under `/fast/scratch/hyaku/kama-r24/CaseCrossRepoFound/` (`fix2/`, `mut2/`, `oldstyle/`, `probe/`, `probe2/`, `scratch/`); `find /tmp -maxdepth 2 -iname '*xrepo*' -o -iname '*CrossRepoFound*' -o -iname '*kama-r24*'` returns nothing; the lane worktree shows no new tracked-file changes from this lane (the ` M LOG.md`, ` M corpus/SOURCES.md`, `?? corpus/lessons/round-24.md` entries are other lanes' concurrent work in the main checkout — this lane wrote only under `.ufo/waves/round-24/build/out/CaseCrossRepoFound/` and this advice file). No commits, no pushes, no `.jj`, no sibling lane touched, no production file edited.

---

## 6. Files (this lane's output)

* `out/CaseCrossRepoFound/xrepo_found_case.py` — the case builder + evidence producer (self-contained; builds the fixture, asserts P1–P13, runs the auditor on both arms, records the no-fetch invariant).
* `out/CaseCrossRepoFound/mutants.py` — the four mutants M1–M4 and their measured outcomes.
* `out/CaseCrossRepoFound/grid_fragment.py` — **candidate** grid fragment for `tests/report-audit/promisor-grid.py` (not production code): `c_promisor_lane_token_found_in_fleet` and its twin, with the row names `C16-promisor-lane-token-found-in-fleet` / `C16-twin-full-clone`. Validated by executing it against the round-23 grid's own helpers (`pair/init/commit/publish/report/g/require`): lane arm → base exit 2 `partial clone (promisor pack)`, twin arm → exit 0, no findings.
* `out/CaseCrossRepoFound/evidence-case.json`, `evidence-mutants.json`, `evidence-fragment.json` — the measured evidence.
* This file: `.ufo/waves/round-24/build/advice/CaseCrossRepoFound.md`.

Scratch only: `/fast/scratch/hyaku/kama-r24/CaseCrossRepoFound/{fix2,mut2,oldstyle,probe,probe2,scratch}` and the lane's own scratch clone `…/CaseCrossRepoFound/scratch` (`git clone --no-hardlinks` of the lane, used only to read the base). No `/tmp` heavy clone.

---

## 7. Not verified / limits

* The expectation is fixed for **one** auditor build (git 2.56.0). `git --no-lazy-fetch` needs git ≥ 2.45; below that the base refuses every repository (see the round-23 `OldGitFloor` advice) — this case inherits that floor and does not measure it.
* The fleet contains the cited blob by **vendoring identical content**, and the fleet-resident commit is the fleet's own "evidence vendor" commit. The kama fleet does not normally hold lane objects; the case is synthetic by construction and says so in the report text it plants. A fleet-resident commit of another lane's history would be equivalent for the resolution path and is not built.
* The lane's missing object is a **blob**. The sibling rows own the missing-commit, missing-tree and missing-report-object shapes; this row deliberately owns only "absent in the lane, present in the fleet".
* Not measured here: the same case under a candidate that changes `lookup()`'s repository set, the historical rounds 10–22 ledger under the repair, and any real lane/fleet repository (the real lane and fleet are not partial clones: no `remote.*.promisor`, no `extensions.partialclone`, no `*.promisor` pack — unchanged by this wave).
* No production file was edited; the L1 owns the repair and the adopting grid.
