# Oracle — paired promisor pack marker, no remotes, all contents local (round-24, C1)

Lane: `OracleNoConfigPack` (leaf, no dispatch). Base `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`.
Preregistration: `.ufo/waves/round-24/preregistration.json`.

## Verdict

The case is well posed, and the repair must produce **the same substantive verdict as an
otherwise identical full clone**, never the r23 blanket refusal:

* paired `.promisor` marker + **no** promisor remote + **every** required object local →
  the audit runs and returns the full clone's verdict (`0 clean` or `1 failed` with the same
  finding kinds and tokens). r23 returns `2 could-not-evaluate: partial clone (promisor pack)`
  — that is the harm this wave repairs.
* promisor **metadata** alone (`extensions.partialClone`, `remote.*.promisor`,
  `remote.*.partialclonefilter`, paired marker) with all content local is likewise **not**
  a refusal reason.
* a **missing citation** in a repository that is promisor-*backed* (a promisor remote exists)
  is unknown → `2`; in a repository that is promisor-*marked only* (paired marker, no remote)
  absence is plain (`git cat-file --batch-check` answers `missing`, rc 0) → the verdict equals
  the full-clone twin. This is the one open calibration question (§6.1).
* an unavailable **required** object (report blob, cited commit, tree) → `2`, never clean/failed.

## 1. Axes (godspeed)

| axis | what it measures here |
|---|---|
| A1 calibration (C1) | the omission detector's finding set on promisor-marked repos equals the full clone's |
| A2 operability | complete local repos are never refused as `2` |
| A3 honesty | an unavailable required object is `2`, never a guessed clean/failed |
| A4 safety | no transport, no lazy fetch, no hang, no traceback |
| A5 determinism | identical evidence ⇒ identical exit code and identical finding tokens |

## 2. What the case is, in git terms

* A **paired marker** is `objects/pack/pack-<hash>.promisor` next to a real
  `pack-<hash>.pack` — the state r23 refuses at `tools/report-landing-audit.py:454-457`.
  The `.promisor` file's *presence* is the signal; an **empty** `.promisor` file is what git
  itself writes (official `git-repack` documentation: "an empty `.promisor` file corresponding
  to the new separate pack"; local copy `/usr/share/man/man5/gitformat-pack.5.gz`).
* **No remotes** = `git config --get-regexp '^remote\.'` is empty in lane and fleet: nothing
  can be fetched, nothing can be asked, so the store can never learn more.
* **All contents local** = the object closure of the pinned roots is complete:
  `git rev-list --objects --missing=print --no-object-names <root>` prints no `?`-prefixed id.
* r23's blanket refusal is `check_history_repo()` (`:438-465`), called for lane and fleet at
  `:514-515` **before** any audit work; the config branch uses `git_bool()` (`:482-487`),
  which treats an unrecognised boolean token as false — the "unknown token" behaviour is
  already there, but it is only reached *after* the marker branch has already refused.

## 3. Fixture recipe (bounded, local, offline)

Recipe file: `.ufo/waves/round-24/build/out/OracleNoConfigPack/make-fixture.py`
Runner: `.ufo/waves/round-24/build/out/OracleNoConfigPack/measure.py`
(`.ufo/waves/round-24/build/out/OracleNoConfigPack/run-arm.sh` runs one arm.)

```
python3 .ufo/waves/round-24/build/out/OracleNoConfigPack/make-fixture.py \
        --root /fast/scratch/hyaku/kama-r24/OracleNoConfigPack/fixture --json
python3 .ufo/waves/round-24/build/out/OracleNoConfigPack/measure.py \
        --auditor <candidate> --root /fast/scratch/hyaku/kama-r24/OracleNoConfigPack/fixture \
        --json <out>.json
```

Construction (no clone, no remote, no network, no transport process, no payload):

* lane: `git init -b master`; commit `round-1: work` (author `kama-shokunin`, author time
  1000) → `db796f8b820bf3825c58832419138cdba23206a7`; optional second commit
  `round-1: more` (author time 1500) → `29e8ea69cc44bbb72af22255c5231a7d13b577e0`.
* fleet: `git init -b master`; commit `.ufo/reports/round-1/kama.md` (author `fleet`, author
  time 2000 → the cutoff) whose `## Landed changes` lists the cited commit.
* both repos are `git repack -a -d`ed, so the **only** difference between a `full-*` arm and
  its `promisor-*` twin is one empty `pack-<hash>.promisor` file beside the pack.
* the recipe verifies each premise before the arm is used (top level, not shallow, sha1,
  no remote config, complete closure, marker present/absent as claimed, marker paired with a
  real `.pack`), and refuses to build an arm whose premise does not hold.

Arms (13): `full-clean`, `promisor-clean`, `full-omission`, `promisor-omission`,
`full-fabricated`, `promisor-fabricated`, `tok-bool-maybe`, `tok-filter`, `tok-extensions`,
`promisor-hostile-ssh` (adjacent safety arm), `full-missing-unrelated-blob`,
`promisor-missing-unrelated-blob`, `promisor-missing-report-blob`.

## 4. Independent expected outcome (derived from the construction, not from a run)

Derivation: the lane's author times (1000, 1500) are both ≤ the fleet report's author time
(2000) ⇒ both lane commits are *required*; the report cites only the 1000 one ⇒ the 1500 one
is not cited ⇒ exactly one `landed-omitted` with token = that commit's sha. A fabricated
40-hex id is in no repository ⇒ `unresolved-full-hash`. Everything else is clean.

| arm | exit | kinds / tokens | summary facts |
|---|---|---|---|
| `full-clean` | 0 | `[]` | defects 0, uncorrected 0, required_commits 1, status clean |
| `promisor-clean` | 0 | `[]` — **identical to `full-clean`** | same |
| `full-omission` | 1 | `['landed-omitted']`, token `29e8ea69cc44bbb72af22255c5231a7d13b577e0` | defects 1, uncorrected 1, required_commits 2, status failed |
| `promisor-omission` | 1 | `['landed-omitted']`, token `29e8ea69…577e0` — **identical to `full-omission`** | same |
| `full-fabricated` | 1 | `['unresolved-full-hash']`, token `1234567890abcdef1234567890abcdef12345678` | defects 1, required_commits 1, status failed |
| `promisor-fabricated` | 1 | `['unresolved-full-hash']`, same token — **identical to `full-fabricated`** (primary reading, §6.1) | same |
| `tok-bool-maybe` (`remote.origin.promisor=maybe`) | 0 | `[]` | identical to `full-clean`; no crash, no hang |
| `tok-filter` (`remote.origin.partialclonefilter=blob:none`) | 0 | `[]` | identical to `full-clean` |
| `tok-extensions` (`extensions.partialClone=origin`, no such remote) | 0 | `[]` | identical to `full-clean` |
| `promisor-hostile-ssh` | 0 | `[]` | identical to `full-clean`; **the transport marker file must not exist**; no timeout |
| `full-missing-unrelated-blob` | 0 | `[]` | twin baseline (audit never reads that blob) |
| `promisor-missing-unrelated-blob` | 2 (probe, §6.2) | — | marked store with a hole in the pinned closure ⇒ `2` (recommended policy (i)); its non-promisor twin stays `0` |
| `promisor-missing-report-blob` | 2 | — | required object unavailable ⇒ `2`, never clean/failed |

Document-equality rule for "identical to the full clone": the JSON documents of a promisor arm
and its full twin must be equal after substituting the fleet path string (only
`results[].report` embeds it). Every other field — `summary.by_kind`, `required_commits`,
`cutoff`, `required`, `round_commits`, `defects[].token`, `cited_elsewhere` — must match.

## 5. Measured facts this expectation rests on (all local, offline)

1. `git rev-list --objects --missing=print --no-object-names <root>` prints missing ids with a
   literal `?` prefix (kept even with `--no-object-names`) and exits 0.
2. That command **does not fetch**: with `remote.origin.url=ssh://example.invalid/x.git`,
   `remote.origin.promisor=true`, `extensions.partialClone=origin` and
   `core.sshCommand="touch <marker>; false"`, the marker file was **not** created — with and
   without `--no-lazy-fetch`. A closure check is therefore transport-free by construction.
3. `git cat-file --batch-check` in a repo with **only** a paired marker answers an absent id
   as `… missing`, rc 0 (no promisor remote is consulted) — absence is plain.
4. `git cat-file --batch-check` for an absent id in a repo with `remote.origin.promisor=maybe`
   fails rc 128, `fatal: bad boolean config value 'maybe' for 'remote.origin.promisor'`.
   With all objects present the same repo audits fine. The invalid token is fatal **only on
   the missing-object path** ⇒ it must yield `2` (never a verdict, never a traceback).
5. `git rev-list --missing=print` does not consult the promisor remote either: invalid bool +
   `extensions.partialClone=origin` still exits 0 with the `?`-prefixed id.
6. `git cat-file -e <absent>` in the same repo → same rc 128 bad-boolean failure.
7. **Backed repos are the ones that reach for the remote.** With a promisor source present
   (`remote.origin.url=file://<nonexistent local path>` + `remote.origin.promisor=true` +
   `extensions.partialClone=origin`) and one missing blob, a **plain** `git cat-file -e <absent>`
   asks the remote and fails with `fatal: Could not read from remote repository.` (local file
   path, no network, no data transfer). The same call under `--no-lazy-fetch` stays silent
   (rc 1), `--no-lazy-fetch cat-file --batch-check` answers `… missing` rc 0, and
   `--no-lazy-fetch rev-list --objects --missing=print --no-object-names` prints the `?`-prefixed
   id rc 0. ⇒ the isolation flag `--no-lazy-fetch` in `GIT_ISOLATION` (`:93-96`) is what makes
   the *backed* case transport-free; the new closure check must run through the same `git()`
   wrapper and keep that flag, and the candidate must not add any git call that bypasses it.
8. **Program-free fetch detection (adopted from `CaseUnknownCitation-2`'s stronger check).**
   `measure.py` now snapshots each audited repository's object store before and after the run
   (pack file list, `FETCH_HEAD` presence, loose-object count) and reports `fetch_observed`:
   any new pack, a new `FETCH_HEAD`, or a changed loose count is a fetch. Base r23 measures
   `fetch_observed=false` and `transport_marker_created=false` in **all 13 arms**
   (`base-r23-fetchcheck.json`) — so a candidate that adds a git call outside the isolation
   wrapper is caught by a state diff, not by a repository program.

## 6. Calibration questions the candidate must answer (owner: L1 / AuditRepair)

### 6.1 "promisor-marked" vs "promisor-backed" (the only reading-sensitive arm)

The preregistration distinguishes the two words: `expected_after[0]` says *promisor-marked*
complete clones must give "exact same substantive clean/failed findings as otherwise identical
full clones, not exit2"; `expected_after[3]` says a missing citation "in any promisor-backed
repository is unknown, not proved absent: exit2 unless resolved locally by another audited
repository".

Primary reading used above: **marked** = metadata present (paired marker, promisor config);
**backed** = a promisor remote exists that could still supply the object. A paired marker with
no remote is marked, not backed; fact 3 shows git itself reports absence plainly there, so the
`promisor-fabricated` arm is a proved absence ⇒ `1`, identical to the twin.
Alternative (literal) reading: any promisor metadata makes absence uncertain ⇒
`promisor-fabricated` becomes `2`.
**Action:** L1 picks one; the grid must pin that one. `promisor-fabricated` is the only arm in
my lane where the two readings differ (1 vs 2). Message sent to `CaseUnknownCitation-2` to
reconcile; both readings are identical for every other arm (no missing citation there).
`CaseUnknownCitation-2` confirmed (its advice §4a) that its own arms carry a promisor source
(URL + filter) and are therefore **reading-invariant** — they must be `2` under either reading.
Consequently **exactly one row in the whole wave is reading-sensitive: my `promisor-fabricated`**
(marker only, no URL, fabricated id). L1's choice moves that one row and nothing else, so the
decision is cheap and low-blast-radius — and it must be made explicitly rather than by accident.
Note the asymmetry that makes the literal reading costly: a promisor-marked repo with an
invalid/absent remote would then never produce a `1` verdict at all.

**Where the distinction must land.** `tools/report-landing-audit.py:326-327` emits
`unresolved-full-hash` for every token whose lookup status is not `found`, so a *proved*
absence and an *unknown* absence are the same line of code today; `lookup()` (`:139`) documents
exactly three states — `'found'|'ambiguous'|'missing'` (`:140`) — and has no fourth status for
"unknown", so the repair has to introduce the distinction (a new status from `lookup()`, or a
promisor-aware decision at the call site) rather than reuse `missing`. The distinction: `missing`
in a marked-only store is final (my `promisor-fabricated` ⇒ `1`), `missing` in a backed store is
unknown (`CaseUnknownCitation-2`'s A-main ⇒ `2`). That lane's A-main exit 2 **together with** its
B-control exit 0 (same lane, citation removed) is the attribution pair that keeps the two rules
apart; my lane supplies the marked-side rows (metadata alone never changes the verdict) and the
metadata-only arms that would break if the repair tied the refusal to the metadata instead of to
the citation.

### 6.2 Closure scope: whole pinned root vs required objects only — coupled to the retained F23 row

The executor target names `git rev-list --objects --missing=print --no-object-names` on the
pinned lane/fleet roots, i.e. the **whole** closure. Two consequences must be decided together
with the retained r23 grid, because they pull the same lever:

* `expected_after[2]` speaks of *required* objects ("an unavailable required
  commit/tree/blob/report object: exit2"), while `expected_after[5]` says "metadata-only
  declarations do not establish incompleteness; **content completeness and availability of
  required evidence** determine the outcome".
* The retained r23 row **F23** (marker-only repo whose pinned closure really has a hole:
  `tests/report-audit/repo-state-grid.py:670`, fixture `f_promisor_pack` at `:195-213`) is
  expected to stay `exit 2`. Its missing blob is *not* an object the auditor reads — it is a
  hole in the pinned closure, and the report merely mentions its oid. Under a
  "required-objects-only" policy F23 would flip to `1` (`unresolved-full-hash`), i.e. a
  policy-row change; under a whole-closure policy F23 stays `2` and only its REASONS pin
  (`:704`) has to change.

**Recommended policy (i): run the closure check on the pinned roots of a repository that is
promisor-marked or promisor-backed; leave ordinary repositories as they are.**
* promisor-marked/backed + complete closure ⇒ the twin's verdict (my primary arms);
* promisor-marked/backed + incomplete closure ⇒ `2` (unavailable required evidence) — this is
  F23's shape and keeps that row at `2`;
* ordinary repository (no promisor metadata) ⇒ r23 behaviour, no new refusals (no arbitrary
  hardening): a missing blob the audit never reads stays invisible, exactly as r23 does it
  (`full-missing-unrelated-blob` = `0 clean`).
Under (i) my probe arm `promisor-missing-unrelated-blob` is expected `2` (its marker says the
store was filtered, so the hole is meaningful) while its non-promisor twin is `0` — the same
divergence r23 already had in F23, now with a truthful reason instead of "promisor pack".
Alternative policy (ii), required-objects-only: `promisor-missing-unrelated-blob` = `0` and
F23 must be re-pinned to `1` (a documented policy-row change). The preregistration does not
pin this; L1's call. The fixture arms exist so the choice can be measured, not argued.

### 6.3 Unknown promisor tokens

`git_bool()` (`:482-487`) already treats an unrecognised boolean as false; keep that. The
danger is not the boolean but the **missing-object path** (fact 4): `cat-file` then dies rc 128
and the auditor must convert that into `2` with a git-level reason, never into a verdict and
never into a traceback. `tok-bool-maybe` (complete content) must stay `0`, exactly as r23 does
— the repair must not turn an unknown token into a new refusal.

## 7. Base-r23 behaviour (measured, `expected_before`)

Auditor: `tools/report-landing-audit.py` at base `0df800e`, sha256
`da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` (the worktree copy is
byte-identical to the base blob; `git diff 0df800e -- tools/report-landing-audit.py` is empty).
Evidence file: `.ufo/waves/round-24/build/out/OracleNoConfigPack/base-r23-measurement.json`.

| arm | exit | kinds | stderr |
|---|---|---|---|
| full-clean | 0 | `[]` | — |
| **promisor-clean** | **2** | — | `could-not-evaluate: …/promisor-clean/lane: partial clone (promisor pack)` |
| full-omission | 1 | `['landed-omitted']` | — |
| **promisor-omission** | **2** | — | `… partial clone (promisor pack)` |
| full-fabricated | 1 | `['unresolved-full-hash']` | — |
| **promisor-fabricated** | **2** | — | `… partial clone (promisor pack)` |
| tok-bool-maybe | 0 | `[]` | — |
| tok-filter | 0 | `[]` | — |
| **tok-extensions** | **2** | — | `… partial clone (extensions.partialclone)` |
| **promisor-hostile-ssh** | **2** | — | `… partial clone (promisor pack)` |
| full-missing-unrelated-blob | 0 | `[]` | — |
| **promisor-missing-unrelated-blob** | **2** | — | `… partial clone (promisor pack)` |
| promisor-missing-report-blob | 2 | — | `… partial clone (promisor pack)` |

No timeout, no traceback, no transport marker in any arm (the marker stayed absent because
r23 refuses before touching the objects).

## 8. Grid rows to pin, and one r23 pin that must change

Sent to `GridOracle-2`. Rows (expected after the repair; base exit in brackets):
`P01` promisor-marker-clean `control` exit 0 `[]` [2]; `P02` promisor-marker-omission
`control` exit 1 `['landed-omitted']` token `<omitted sha>` [2]; `P03` promisor-marker-fabricated
`control` exit 1 `['unresolved-full-hash']` [2] (2 under the alternative reading of §6.1);
`P04` promisor-metadata-extensions `control` exit 0 [2]; `P05` promisor-metadata-filter
`control` exit 0 [0]; `P06` promisor-invalid-bool-token `control` exit 0 [0] plus a
missing-id variant expecting `2` (git: "bad boolean config value"); `P07` promisor-hostile-ssh
`fault` exit 0, no transport marker, no timeout [2]; `P08` promisor-missing-report-blob
`contract` exit 2 [2]; `P09` promisor-missing-unrelated-blob `probe` exit 2 under the recommended
policy (i) — marked store with a hole in the pinned closure (F23's shape) — while its
non-promisor twin `full-missing-unrelated-blob` stays `0`; policy (ii) would flip P09 to `0`
and F23 to `1` (§6.2).

**The wave's measurement command does not exist at base.** The preregistration names
`python3 tests/report-audit/promisor-grid.py --arm both --json`; `tests/report-audit/` at base
`0df800e` contains no `promisor-grid.py` (only `repo-state-grid.py`, `isolation-mutants.py`,
`citation-provenance.py`, `error-verdict-census.py`, `gguf-identity.py`, `kama-llamacpp-live.py`,
`kama-ollama-evidence.py`, `report-landing-audit.py`, `sources-append-only.py`,
`test-snapshot.sh`, `kama-probe.sh`). The promisor grid must be created by the grid/audit
seats before that command can be run; my recipe is the arm source for it.

**Pin that must change in the retained r23 grid:** `tests/report-audit/repo-state-grid.py:704`
`REASONS["F23-promisor-pack-without-config"] = "promisor pack"`. Under policy (i) (§6.2) F23's
exit stays `2` — its blob really is missing from the pinned closure — but the reason becomes the
*unavailable required object* refusal, so the old string pin will fail against a repaired
auditor — a documented policy-row change, exactly what the preregistration's "explicitly
documented policy-row expectation changes" allows. Under policy (ii) F23's exit itself would
have to be re-pinned to `1`; §6.2 argues against that.
Unchanged: `:670` F23 remains a `contract` row; `:679` C09 (`remote.origin.promisor=false`) and
`:680` C10 (orphan marker without a `.pack`) stay exit 0; `:674` F27 (filter + real remote URL)
and `:689` T01 (blobless clone) are the *backed* counterparts of my arms and belong to the
sibling lanes.

## 9. Harm guards the repair must satisfy (each has an arm above)

1. No refusal of a promisor-marked repository whose required objects are all local →
   `promisor-clean`, `tok-extensions`, `tok-filter` must be `0`.
2. No weakening of the omission detector in promisor repositories → `promisor-omission` must
   stay `1` with the same token `29e8ea69…577e0` (a repair that treats every lane commit in a
   promisor repo as uncertain and refuses to report the omission would silently lose C1).
3. No guessed absence → an unavailable required object is `2`, never `0`/`1`
   (`promisor-missing-report-blob`).
4. No proved absence where the store could still supply the object → a missing citation in a
   *backed* repository is `2` (sibling lane; §6.1).
5. No transport, no lazy fetch, no program execution → `promisor-hostile-ssh`: the
   `core.sshCommand` marker file must not exist, **and** `measure.py`'s `fetch_observed`
   (pack/`FETCH_HEAD`/loose-object diff) must be `false` in every arm (fact 8; base r23 already
   measures `false` everywhere). Fact 2 shows `rev-list --missing=print` never fetches; fact 7
   shows only a *backed* repo would try, and `--no-lazy-fetch` in `GIT_ISOLATION` is what stops
   it — so the new closure call must not bypass that wrapper.
6. No hang and no traceback → every arm must finish inside 30 s with no `Traceback` on stderr
   (facts 4 and 5 define the invalid-token failure mode: rc 128 ⇒ `2`).
7. `--no-lazy-fetch`, `--no-replace-objects`, the log/signature suppression and the 20 s git
   deadline of `GIT_ISOLATION` (`:93-96`) must survive the change; the closure check must run
   through the same `git()` wrapper (`:111-137`) so the timeout and the error mapping apply.

## 10. Residual risk and verification gaps

* **The candidate was not run.** Every "expected" row is derived from the fixture construction
  and the preregistration; the base-r23 numbers are the only executions I made. All
  post-repair exit codes in §4 are *unverified against a candidate* until L1 runs the grid.
* §6.1 is an open reading, not a measurement (though `CaseUnknownCitation-2` reached the same
  marked≠backed split); §6.2 is an unpinned policy choice with a recommendation (policy (i)).
  Both are L1's to decide; my arms exist so the decision can be measured.
* The fixture uses only a two-commit lane and a one-line report. It exercises the omission
  detector's *core* path (cited / uncited pre-cutoff lane commit) but not the errata path,
  the ambiguous-abbreviation path, the `--report N=PATH` draft path, or multi-round selection;
  those stay with the existing grid rows.
* **My arm set does not discriminate marked-vs-backed on its own.** `tok-filter` has the filter
  key but no URL, so it is *marked, not backed*; it carries no missing citation and no missing
  object, so it is `0` under either reading. The discriminating pair spans two lanes: my
  `promisor-fabricated` (marker only, no remote → `1 unresolved-full-hash`) against
  `CaseUnknownCitation-2`'s A-main (filter + URL → `2`). Together they pin the whole policy:
  `1` for marked, `2` for backed.
* The `promisor-hostile-ssh` arm uses the r23 grid's `core.sshCommand` idiom (a local `touch`);
  it creates no network traffic and no payload, but it is outside my lane's "no remotes"
  wording and is labelled adjacent.
* I did not measure git behaviour with a *blobless* (filter-created) pack, because creating one
  needs a transport (`git clone --filter=blob:none file://…`), which my lane forbids; the
  blobless case is the sibling `T01`/`OracleMissingNonrequired` territory.
* Cross-repository clock skew is not detectable and is out of scope (documented in the tool's
  own docstring).

## 11. Files

* `.ufo/waves/round-24/build/advice/OracleNoConfigPack.md` (this report)
* `.ufo/waves/round-24/build/out/OracleNoConfigPack/make-fixture.py` (fixture recipe, 13 arms)
* `.ufo/waves/round-24/build/out/OracleNoConfigPack/measure.py` (bounded runner: exit, kinds,
  summary, timeout, traceback, transport marker)
* `.ufo/waves/round-24/build/out/OracleNoConfigPack/run-arm.sh` (single-arm runner)
* `.ufo/waves/round-24/build/out/OracleNoConfigPack/base-r23-measurement.json` (base-r23 evidence)
* `.ufo/waves/round-24/build/out/OracleNoConfigPack/base-r23-fetchcheck.json` (second base-r23
  measurement with the program-free fetch detector: `fetch_observed=false` in all 13 arms)
* `.ufo/waves/round-24/build/out/OracleNoConfigPack/fixture-facts.json` (per-arm premise facts:
  marker names, cited/omitted shas, missing blobs, injected config tokens)
* scratch (not part of the lane deliverable): `/fast/scratch/hyaku/kama-r24/OracleNoConfigPack/`
  (`fixture/`, `base-r23-measurement.json`, `probe-missing*/`, `probe-lazy/`, `probe-tokens/`)

No production file was modified; no network, transport or payload command was used; no tool was
installed.
