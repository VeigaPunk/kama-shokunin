# CaseHydratedLane — round-24 oracle case

**Lane:** leaf member, one offline oracle case (no subagent dispatch).
**Subject:** a genuine `file://` `blob:none` lane clone, hydrated locally
offline, must yield the same substantive clean/omission verdicts as a full
clone; an *incomplete* promisor repository must yield exit 2, never a
clean or failed verdict.
**Verdict:** the case is **specified, built offline, executed against the
frozen r23 base, and shown satisfiable**. The r23 base fails 8 of 16 arms
(all promisor-marked-but-complete arms) and 8 of 8 pair equalities; a
minimal content-completeness repair passes 16/16 and 8/8; the
"metadata-only removal" mutant passes 12/16 and is killed by 4 arms.

---

## 1. Base and provenance

| item | value |
|---|---|
| prereg | `.ufo/waves/round-24/preregistration.json` (base `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`) |
| lane master at wave start | `0df800e` (r23 final) |
| r24 prereg commit | `d1b9d95` — `git show --stat d1b9d95` touches only `.ufo/waves/round-24/preregistration.json` and `LOG.md`; `tools/` and `tests/` are identical to the base |
| audited tool at base | `tools/report-landing-audit.py`, blob `cf706c52233139920da60f8b55d06f031286c4f9`, sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` |
| git | `git version 2.56.0` (tool requires ≥ 2.45 for `--no-lazy-fetch`) |
| scratch | `/fast/scratch/hyaku/kama-r24/CaseHydratedLane/` (clone of the lane repo + `work-*` fixture roots) |
| artifacts | `.ufo/waves/round-24/build/out/CaseHydratedLane/` |

No install was needed or performed: git 2.56.0 and python3 are already on
the host, so the tooling directive produced no pacman/uv/cargo transaction.

## 2. The defect under repair (base citations)

`tools/report-landing-audit.py` refuses an audited repository because of
promisor **metadata**, never looking at its content:

* `tools/report-landing-audit.py:454-457` — a `.promisor` marker next to a
  `.pack` raises `partial clone (promisor pack)`.
* `tools/report-landing-audit.py:459-465` — the config keys
  `extensions.partialclone` or `remote.<name>.promisor` (truthy) raise
  `partial clone ({key})`.
* `tools/report-landing-audit.py:51` — the module docstring states that
  "shallow, grafted, partial-clone, non-sha1 and non-top-level
  repositories … are refused".
* `tools/report-landing-audit.py:93` — `GIT_ISOLATION` already carries
  `--no-lazy-fetch` and `--no-replace-objects`; the repair must keep them.

Consequence measured below: a repository whose object store is **complete**
is refused with exit 2 (could-not-evaluate), so a correct clean or
`landed-omitted` verdict is never reached. That is the r23 harm.

## 3. The fixture

### 3.1 Recipe (exact, offline)

`out/CaseHydratedLane/recipe.sh` (run verbatim; output reproduced in §5.0):

1. lane origin with two `round-1:` commits by `kama-shokunin`
   (author times 1000 and 1500, fixed ⇒ deterministic SHAs
   `166f01c6f35c…` = "round-1: work", `82ade1340915…` = "round-1: extra");
   `uploadpack.allowFilter=true` so the server really filters;
2. `git -c protocol.file.allow=always clone --no-local --filter=blob:none
   --no-checkout file://<origin> <clone>` — a **genuine** blobless clone
   (`remote.origin.promisor=true`, `remote.origin.partialclonefilter=blob:none`,
   a `*.promisor` pack marker). `--no-checkout` is essential: a checkout
   asks the promisor remote for the tip blobs and hydrates the fixture
   (this is exactly what happens in the historical row T01, §6);
3. **hydration offline**: the origin's loose object files are copied into
   the clone's object store. A plain file copy — no transport, no program.
   The promisor marks stay in place;
4. proof of closure: `git rev-list --objects --all --missing=print`
   (`?`-prefixed lines = missing objects) and the plain walk
   `git rev-list --objects --all` (rc 0 ⇔ content complete).

### 3.2 Builder and grid shape

`out/CaseHydratedLane/hydrated_lane_case.py` is a candidate builder for
`tests/report-audit/promisor-grid.py`: it exports `build_arm(root, arm,
shape)`, the expectation table `EXPECTED`, the pair table `PAIRS` and a
grid-style `build_cases()` returning `(name, kind, builder, exit, kinds)`.
Eight arms × two report shapes = 16 cases:

| arm | lane side | fleet side | content | promisor marks |
|---|---|---|---|---|
| `full` | full clone | full clone | complete | none |
| `marked` | clone that *asks* for a filter from an origin that does not offer one (server sends everything) | full clone | complete | **yes** |
| `hydrated` | genuine blobless clone + offline hydration | full clone | complete | **yes** |
| `unhydrated` | genuine blobless clone, untouched | full clone | 2 blobs missing | yes |
| `partial` | genuine blobless clone, 1 of 2 blobs supplied | full clone | 1 blob missing | yes |
| `fleet-hydrated` | full clone | genuine blobless clone + hydration | complete | yes (fleet) |
| `fleet-unhydrated` | full clone | genuine blobless clone | report blob missing | yes (fleet) |
| `fleet-marked` | full clone | clone that asks for a filter from a non-filtering origin | complete | yes (fleet) |

Shapes: `clean` (the report cites both lane commits) and `omission`
(the report cites only "round-1: work", so "round-1: extra" is a
pre-cutoff lane commit that the report omits). The fleet report is
committed at author time 2000, so both lane commits are pre-cutoff.

### 3.3 Fixture premises (all proved, see the `fixture` block of the JSON)

* every commit SHA is identical in all 16 arms (same construction ⇒ the
  arms are true pairs, not variants);
* the blobless clones are genuinely incomplete before hydration: 2 missing
  blobs, plain walk rc 128 `fatal: missing blob object 'b8f99f5b…'`;
* after hydration the clone holds **all** origin objects (6/6), the
  closure is complete (0 missing, plain walk rc 0) **and the promisor
  marks are still there**;
* `marked` arms: promisor marks present, content complete (0 missing);
* `fleet-unhydrated`: the missing object is exactly the report blob
  `e9695bd8592467e1c33044894b533a2fb54a0ad6`;
* `program_surface` is empty for every clone and origin: no
  `core.sshCommand`, no `core.gitProxy`, no `filter.*.process`, no
  `uploadpack.packObjectsHook`, no executable hook. Nothing in the fixture
  can execute anything;
* every fixture path is under the arm root, and every arm root is under
  the given scratch root (guard in code + verified over all three runs);
* `GIT_ALLOW_PROTOCOL=file` is set for every git call of the fixture, so a
  network transport would fail loudly rather than happen silently; the
  fixture needs only `file://` and the re-run with that restriction
  produced identical results;
* the fixture uses no temporary directory of its own (`/tmp` shows no
  artefact of this lane).

## 4. Expected exits and findings (fixed before any candidate run)

Derived from the constructed history, not from a candidate run.

| case | expected exit | expected finding kinds |
|---|---|---|
| `full/clean` | 0 | — |
| `full/omission` | 1 | `landed-omitted` |
| `marked/clean` | 0 | — |
| `marked/omission` | 1 | `landed-omitted` |
| `hydrated/clean` | 0 | — |
| `hydrated/omission` | 1 | `landed-omitted` |
| `unhydrated/clean` | 2 | none (never a verdict) |
| `unhydrated/omission` | 2 | none (never a verdict) |
| `partial/clean` | 2 | none (never a verdict) |
| `partial/omission` | 2 | none (never a verdict) |
| `fleet-hydrated/clean` | 0 | — |
| `fleet-hydrated/omission` | 1 | `landed-omitted` |
| `fleet-unhydrated/clean` | 2 | none |
| `fleet-unhydrated/omission` | 2 | none |
| `fleet-marked/clean` | 0 | — |
| `fleet-marked/omission` | 1 | `landed-omitted` |

Pair equalities (substantive verdict of the promisor-marked arm must equal
the full-clone arm, metadata notwithstanding): `full==marked`,
`full==hydrated`, `full==fleet-hydrated`, `full==fleet-marked`, each for
both shapes (8 equalities).

## 5. Executed evidence

All runs: `python3 .ufo/waves/round-24/build/out/CaseHydratedLane/hydrated_lane_case.py
--scratch <scratch> --auditor <path> --out <json>`. Only the fixture and
the auditor under test were run; no suite (neither the r23 grid nor a
candidate grid) was executed.

### 5.0 Recipe output (verbatim, `recipe.sh`)

```
--- promisor metadata:
remote.origin.promisor=true
remote.origin.partialclonefilter=blob:none
--- closure before hydration (missing objects are named ?<oid>):
82ade13409156edd9fb1f57933fa0419f6edb8e1
166f01c6f35cc28e414ecc942b789e13534d3b20
b68b1ebf4bc0ddeec7d024ee7d164e3b147816af
d55d8b6cb083f9e459fb8c97a448c6b8d84212ff
?0f2287157f7cb0dd40498c7a92f74b6975fa2d57
?b8f99f5be53f536f79ef622abaa77b9942a9e142
--- closure after hydration:
82ade13409156edd9fb1f57933fa0419f6edb8e1
166f01c6f35cc28e414ecc942b789e13534d3b20
b68b1ebf4bc0ddeec7d024ee7d164e3b147816af
b8f99f5be53f536f79ef622abaa77b9942a9e142 f
0f2287157f7cb0dd40498c7a92f74b6975fa2d57 g
d55d8b6cb083f9e459fb8c97a448c6b8d84212ff
--- plain walk (rc 0 means the content is complete):
content complete
--- promisor metadata still there:
remote.origin.promisor=true
remote.origin.partialclonefilter=blob:none
--- object counts (clone vs origin):
6
6
```

### 5.1 Frozen r23 base (`evidence-base.json`) — 8/16 rows met

Base exit codes: `full/*` 0/1 as expected; `marked/*`, `hydrated/*`,
`fleet-hydrated/*`, `fleet-marked/*` → **exit 2** with
`could-not-evaluate: …: partial clone (promisor pack)`; `unhydrated/*`,
`partial/*`, `fleet-unhydrated/*` → exit 2 as expected (but for the
metadata reason, not a content reason). All 8 pair equalities are false.

### 5.2 Candidate repair (`evidence-candidate.json`) — 16/16 rows met, 8/8 pairs equal

`candidate/0001-promisor-content-completeness.patch` (also as a runnable
copy `candidate/report-landing-audit.promisor-complete.py`) replaces the
two metadata refusals with a content probe:

```python
def check_content_complete(repo):
    out = git(repo, "rev-list", "--objects", "--all", "--missing=print")
    missing = [line[1:] for line in out.split("\n") if line.startswith("?")]
    if missing:
        raise EvalError(f"{repo}: partial clone with missing objects "
                        f"({len(missing)} missing)")
```

Observed: `marked/hydrated/fleet-hydrated/fleet-marked` → 0 / 1
`landed-omitted` (identical to `full`); `unhydrated` → exit 2
"partial clone with missing objects (2 missing)"; `partial` → exit 2
"(1 missing)"; `fleet-unhydrated` → exit 2 "(1 missing)".

The patch applies cleanly to the base tree (`git apply --check -p1` in the
scratch clone, then applied there and reverted) and the tool's own selftest
passes with it applied (`selftest cases=50 failed=0`). That selftest run
is a bounded no-harm check of my candidate copy in the scratch clone; it
is not the round's grid and no production file was touched.

### 5.3 Mutant M1 (`evidence-mutant-M1.json`) — 12/16 rows met, killed

`candidate/mutant-M1-metadata-only.py` deletes the metadata refusal and
adds **no** content check (the plausible "just stop refusing" repair).
It passes `marked`, `hydrated`, `fleet-hydrated`, `fleet-marked` — the
harm arms alone do not kill it — and is killed by

| killed case | mutant | expected |
|---|---|---|
| `unhydrated/clean` | exit 0, no defect | exit 2 |
| `unhydrated/omission` | exit 1, `landed-omitted` | exit 2 |
| `partial/clean` | exit 0, no defect | exit 2 |
| `partial/omission` | exit 1, `landed-omitted` | exit 2 |

i.e. the mutant turns an incomplete repository into a clean/failed
verdict — exactly what the prereg forbids ("never a clean or failed
verdict"). `fleet-unhydrated` survives M1 (the report blob is needed, so
the audit fails on its own).

## 6. Cross-check with the historical r23 grid (independent finding)

`tests/report-audit/repo-state-grid.py` already encodes the round-24
policy in its expectation table, and the r23 base violates it:

* `tests/report-audit/repo-state-grid.py:689` — `T01-blobless-partial-clone`
  ("tradeoff") expects **exit 0, no defects**.
* I reproduced T01's fixture exactly (`work-t01`): the clone is
  promisor-marked (`remote.origin.promisor=true`) **and content-complete**
  — the clone's own checkout lazily fetched the tip blob, so the plain walk
  `git rev-list --objects --all` returns rc 0 and the blob is present.
  The base auditor still refuses it:
  `could-not-evaluate: …/blobless: partial clone (promisor pack)`.
  ⇒ the round-24 repair must make this historical row MET again (exit 0)
  in the current arm; the frozen arm (`4fe9339`, whose auditor contains no
  promisor code at all) already gives 0, so the repair restores parity
  instead of moving the goalposts.
* `tests/report-audit/repo-state-grid.py:670` / `:704` — `F23-promisor-pack-without-config`
  expects exit 2 with the pinned reason string `promisor pack`. Its
  fixture is genuinely incomplete (the cited blob is absent), so under the
  repair it still exits 2, but the **reason string changes**; the
  `REASONS` entry needs a documented policy-row update.
* `tests/report-audit/repo-state-grid.py:674` — `F27-filter-only-promisor-remote`
  expects exit 1 with `landed-unresolved` + `unresolved-full-hash`. Under
  the prereg bullet "a missing citation in any promisor-backed repository
  is unknown, not proved absent: exit2 unless resolved locally by another
  audited repository", this row must become exit 2 — a policy-row change
  that belongs to the citation lane, not to this one.
* `tests/report-audit/repo-state-grid.py:679-680` — `C09-promisor-false-config`
  and `C10-orphan-promisor-marker` (both exit 0) must stay exit 0 under
  the repair; my table's `marked` arms are the positive version of the
  same distinction and are satisfied by the candidate of §5.2.
* The r23 wave reviewers already flagged this gap:
  `.ufo/waves/round-23/build/advice/RevControls.md:125` ("Grid T01
  (tradeoff) expects exit 0 for a blobless partial clone. I did not verify
  that expectation against the promisor refusal in `check_history_repo`")
  and `.ufo/waves/round-23/build/advice/RevSkillText.md:323` ("T01:
  candidate rc 2 … frozen rc 0 `clean`. Expectation: exit 0.").

## 7. Notes for the candidate (from measurement, not from theory)

1. **Detect by content, not by marks.** git 2.56.0 does **not** write
   `extensions.partialclone` for a `file://` blobless clone; the marks are
   `remote.origin.promisor=true`, `remote.origin.partialclonefilter=blob:none`
   and the `*.promisor` pack marker. A candidate keyed only on
   `extensions.partialclone` would not even see these repositories.
2. **The probe works under the existing isolation.**
   `git rev-list --objects --all --missing=print` runs with `--no-lazy-fetch`
   (so no promisor remote is contacted) and names missing objects as
   `?<oid>`; the plain walk additionally fails rc 128 with
   `fatal: missing blob object '<oid>'`. Keep `--no-lazy-fetch` and
   `--no-replace-objects` in `GIT_ISOLATION`; a completeness probe without
   `--no-lazy-fetch` would itself fetch.
3. **Scope the probe.** `--all` walks every ref. The audit only reads the
   lane branch and the fleet `HEAD`; a repository with an unrelated
   incomplete ref would be refused for evidence nobody needs. The
   candidate must choose and document the scope (per-ref completeness of
   the audited refs is the tighter reading).
4. **Do not re-use the metadata machinery** (`git_bool`,
   `remote.*.promisor` inspection) for the new rule: that is precisely the
   rule being removed.
5. The candidate of §5.2 is deliberately minimal (one function, 10 lines)
   and changes no other behaviour; the `full/*` rows of all three runs are
   byte-identical across base, candidate and mutant (non-promisor no-harm).

## 8. Residual risk and verification gaps

* **Suites were not run.** The r23 grid and any candidate
  `tests/report-audit/promisor-grid.py` were not executed (contract: no
  suite runs in this wave). Every expectation above comes from the fixture
  plus the base auditor applied to the fixture only. The grader's grid must
  carry these 16 rows (or the subset it adopts) as its own rows.
* **Ambiguity in "required evidence" — L1 must ratify my reading.** I
  pinned the *strict* reading: any missing reachable object in an audited
  repository ⇒ exit 2, even when no determination reads that object
  (`unhydrated`, `partial`). The prereg supports it ("an unavailable
  required commit/tree/blob/report object: exit2"; "metadata-only
  declarations do not establish incompleteness"; "a missing citation in any
  promisor-backed repository is unknown"). A weaker reading (only objects
  the determinations read) would let `unhydrated/*` and `partial/*` keep
  exit 0/1, and my two control arms would then be wrong; the mutant M1
  result shows the weaker reading is exactly what a "just stop refusing"
  repair produces.
* **git version coverage.** Measured on git 2.56.0 only. The tool
  requires ≥ 2.45. Older gits may write `extensions.partialclone` and may
  name promisor objects differently; the content-based probe is
  version-robust, a marker-based one is not.
* **`--no-checkout` is load-bearing.** A blobless clone that checks out is
  hydrated by its own lazy fetch (T01). Any grader fixture that wants an
  incomplete repository must use `--no-checkout` (or delete the objects),
  and any fixture that wants a complete promisor-marked repository may
  simply let the checkout happen.
* **The "marked" arms depend on the server ignoring the filter**
  (`uploadpack.allowFilter` unset). Observed on 2.56.0: the client still
  records the promisor marks. A grader may prefer `fleet-marked` to be
  built by a filtering server that is then filled offline (that is the
  `hydrated` arm) — both are present here.
* **Not claimed:** no claim that any arbitrary/untrusted repository is
  safe, no closure of the r23 alternates/gitfile/parser/size-limit
  findings, no claim about live serving, no claim about the scalar score.
  The citation rule for promisor-backed repositories (§6, F27) is out of
  this lane's scope and was not implemented or measured here.

## 9. Artifacts (all under `.ufo/waves/round-24/build/out/CaseHydratedLane/`)

| file | sha256 | content |
|---|---|---|
| `hydrated_lane_case.py` | `89ca13d35e50e87efb58cbbb2384fcb7c53cce2a7a00ea7d960091ac43eb6a57` | candidate fixture builder + expectation table + runner |
| `recipe.sh` | `6e0e9af3e9b1b2f343162c9b40940b72b297abf8db086f887b3cb6e9077d8e79` | exact offline shell recipe |
| `candidate/0001-promisor-content-completeness.patch` | `3d47b0ac8eeb97435a67cff91be6420f35406e1aca800a38e60e5eab538f4970` | candidate repair (unified diff vs base tool, applies with `-p1`) |
| `candidate/report-landing-audit.promisor-complete.py` | `bcded88df3ced7420c9173a13ff47fa143908b7a2df07e98bfab4deb2f30a5a9` | runnable copy of the candidate repair |
| `candidate/mutant-M1-metadata-only.py` | `d2238db57302b9f86ba9b12312f98e7429b73ff8f22d526be90ff2954273858c` | mutant: metadata refusal removed, no content check |
| `evidence-base.json` | `ca5912bda8e80aa898bc3fcdf19ec4e5f85dae2a76c3c0580b72d39662d7cd21` | r23 base run: 8/16 rows met, 8/8 pairs false |
| `evidence-candidate.json` | `667a23b6d2784a3c86a528312e0cba75ed128da53d5acabee5a582e544f53f26` | candidate run: 16/16 rows met, 8/8 pairs equal |
| `evidence-mutant-M1.json` | `518b576d949b113a99e35290a5f7d79f19e874208524e7f4448ce2abab40d849` | mutant run: 12/16 rows met, killed by 4 arms |

Each JSON holds the full fixture proof per row (promisor metadata, closure
before/after, object counts, origin coverage, program surface, path
containment) and the observed exit/kinds/stderr of the auditor.

Report trailer path: `.ufo/waves/round-24/build/advice/CaseHydratedLane.md`
