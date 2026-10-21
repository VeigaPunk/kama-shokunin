# CaseWrongTypeCitation — offline oracle: a locally present blob cited as a Landed commit

## Verdict

**The case is constructible, offline, deterministic, and discriminating.** One fixture, six
arms, fixed expected exits/findings written down before the builder existed
(`out/CaseWrongTypeCitation/expected.json`, written before `build_case.py`; the later arms are
recorded as dated amendments in that same file, never as silent edits).

- **Expected (candidate, r24):** every arm → **exit 1**, exactly one defect,
  kind `landed-unresolved`, token = the blob sha `6e98d181…8b0d`. No `unresolved-full-hash`,
  no `landed-omitted`, no `landed-ambiguous`, no `landed-section-missing`.
  Six arms: `full`, `non-promisor-unrelated-hole`, `promisor-lane-only`,
  `promisor-fleet-only`, `promisor-metadata`, `promisor-metadata-unrelated-hole`.
- **Frozen (r23 base `0df800e`):** `full` and `non-promisor-unrelated-hole` → exit 1 (same
  single finding); all four promisor-marked arms → exit 2, `could-not-evaluate: …: partial
  clone (remote.origin.promisor)`.
- **L1 preintegration decision (`.ufo/waves/round-24/oracle-amendment-1.json`, commit
  `123640b`):** the four known-present blob-in-Landed arms **remain exit 1 /
  `landed-unresolved` with the same token `T`**; no metadata blanket unknown; the initial
  "unknown citation ⇒ exit 2" expectation is retained as **withdrawn / not met** in a separate
  view, not relabelled passed. This cell is unchanged by that correction.

The case is the *discrimination* between **proved wrong type** and **unknown absence**, and it
is the guard against the most likely way the r24 promisor repair over-corrects: treating every
citation that does not peel to a commit as "unknown" in a promisor-backed repository. Here the
object is **present locally**, so its type is known — the report's Landed claim is *proved
false*, not undecidable. This expectation is unchanged by
`.ufo/waves/round-24/oracle-amendment-1.json`, which withdraws the blanket
"unknown citation ⇒ exit 2" rule prospectively and states the stronger rule this case
already relies on: *promisor metadata alone never changes local-object resolution or a
clean/failed verdict*.

## Axes

Calibration (7, the assigned axis) and operability (8). The r24 repair moves promisor-marked
repositories from "refuse everything" (exit 2) to "judge what is present". A repair that
replaces one blanket refusal with another blanket refusal — "in a promisor repository a
citation that does not resolve is unknown" — keeps the calibration axis at zero while looking
like a fix. This case is the smallest cell that separates the two.

## Why this is a real failed finding, not an uncertain missing

The auditor already distinguishes the two states at the git level; it only needs to keep them
apart when the repository is promisor-marked.

Command evidence (git 2.56.0, fixture lane; full capture in
`out/CaseWrongTypeCitation/git-semantics.txt`):

```
$ git cat-file -t 6e98d181389d343031fd578c6a775ce0889a8b0d
blob
$ printf '%s\n' 6e98d181…8b0d | git cat-file --batch-check
6e98d181389d343031fd578c6a775ce0889a8b0d blob 14          # exists, is a blob
$ printf '%s\n' '6e98d181…8b0d^{commit}' | git cat-file --batch-check
6e98d181389d343031fd578c6a775ce0889a8b0d^{commit} missing  # stdout, rc=0
stderr: error: …^{commit}: expected commit type, but the object dereferences to blob type
```

Code path in `tools/report-landing-audit.py` (base `0df800e`):

- `tools/report-landing-audit.py:327` — the full-hash **existence** scan calls
  `lookup(repos, full_tokens)` with **no peel**. `lookup` parses the batch-check line
  `… blob 14` at `tools/report-landing-audit.py:166-173` and marks the token `found`
  (line 173). Therefore a present blob is **not** an `unresolved-full-hash` defect —
  correct, because the object exists.
- **Mechanism note (corrected, confirmed independently by peers `ConnPlan` and
  `OracleLocalBlobType`):** Landed-span tokens are **always** inside that scan. Without
  `corpus/SOURCES.md`, `classify_full_hashes` returns `FULL.findall(text)` over the whole
  report (`tools/report-landing-audit.py:285`); with `SOURCES.md`, `:293`
  (`lo <= start < hi`) puts every Landed-span token **into** the scanned set, and only an
  exact Registry-URL occurrence *outside* the Landed span is diverted to `classified`. So `T`
  is seen by **both** lookups: the no-peel lookup resolves it (the blob is present) while the
  peel to a commit fails — that pair is what produces the single `landed-unresolved` finding.
  The absence of `unresolved-full-hash` here is therefore **not** a Landed-span exclusion
  effect, and this cell's expectation must not be written as SOURCES-dependent.
- `tools/report-landing-audit.py:336-340` — the Landed section calls
  `lookup(repos, […], "^{commit}")`; the peeled batch-check line ends in ` missing`, which
  `lookup` skips at `tools/report-landing-audit.py:160-161`, so the state stays `missing`
  and `tools/report-landing-audit.py:339-340` emits
  `{"kind": "landed-unresolved", "token": <T>}`.
- The defect taxonomy already has the right home: `unresolved-full-hash` is documented as
  "no git object in the lane or fleet repo" (`tools/report-landing-audit.py:14-17`), and
  `landed-unresolved` as a Landed token that "is no commit in either repo"
  (`tools/report-landing-audit.py:20-21`). `T` is an object and is not a commit, so
  `landed-unresolved` is the single correct finding; `KINDS` (line 78) needs no new member.
- The exit-2 path is the promisor refusal in `check_history_repo`
  (`tools/report-landing-audit.py:461-465`, `partial clone ({key})`), surfaced by
  `main` as `could-not-evaluate` → exit 2 (`tools/report-landing-audit.py:948-950`).
  That refusal is what the r24 repair must narrow, and this case must still produce a
  verdict afterwards.

**Repair handle (observation only — not implemented in this lane).** The type is already on
the table: the peeled lookup first runs a **bare** pass (`tools/report-landing-audit.py:149`,
`bare = lookup(repos, tokens)`) whose batch-check line is `<oid> blob <size>` — but only the
"ambiguous" verdict is carried over (`:150-151`), and the parsed record keeps only presence
(`parts[1]`, the type, is discarded at `:173`). So a third state, *present but not a commit*,
is distinguishable from *absent* with **no new git call and no new transport**. Peer
`ConnPlan` measured the same split independently (git 2.56.0, stdout alone cannot separate
absent from wrong-type; the bare pass can): `out/ConnPlan/probe-output.txt` (Q7) and
`advice/ConnPlan.md`. My cell adds the regression guard for it: with a promisor mark added,
the same blob must stay a definite `landed-unresolved`, never exit 2.

## Fixture recipe (bounded, offline)

Builder: `out/CaseWrongTypeCitation/build_case.py` (runs the fixture and the auditor).
Recipe in words:

1. `git init -b master` an origin lane and an origin fleet under the scratch root.
2. Lane: one commit `round-1: work` by `kama-shokunin` at author time `@1000`, containing
   file `f`. `T = git rev-parse HEAD:f` (a **blob**, present locally).
3. Fleet: commit `round-1: report` at author time `@2000` adding
   `.ufo/reports/round-1/kama.md`, whose `## Landed changes` section cites `LC` (the lane
   commit) and `T`, and no other hex token.
4. Clone both origins with `git clone --no-hardlinks` (object copy, no transport, no network)
   into four arm directories: `full`, `promisor-lane-only`, `promisor-fleet-only`,
   `promisor-metadata`.
5. Marking for the promisor arms (metadata only, every object stays present):
   `git config core.repositoryformatversion 1`,
   `git config remote.origin.promisor true`,
   `git config remote.origin.partialclonefilter blob:none`.
   `extensions.partialClone` is deliberately **not** set (git 2.56 `clone --filter=blob:none`
   writes the `remote.*` keys, per the round-23 lessons).
6. Run the auditor as a subprocess:
   `python3 <auditor> --lane-repo <lane> --fleet-repo <fleet> --rounds 1 --no-errata --json`.

Commands actually executed (all local, no network):

```
python3 out/CaseWrongTypeCitation/build_case.py --out out/CaseWrongTypeCitation/results
python3 out/CaseWrongTypeCitation/prove_containment.py
python3 out/CaseWrongTypeCitation/capture_git_semantics.py
```

## Frozen measurement (auditor blob `0df800e:tools/report-landing-audit.py`, sha256 `da5041a8…65af1`)

| arm | marking | hole | exit | kinds | token | stderr tail |
|---|---|---|---|---|---|---|
| `full` | none | – | **1** | `['landed-unresolved']` | `6e98d181…8b0d` | – |
| `non-promisor-unrelated-hole` | none | unrelated missing blob | **1** | `['landed-unresolved']` | `6e98d181…8b0d` | – |
| `promisor-lane-only` | lane | – | **2** | – | – | `partial clone (remote.origin.promisor)` |
| `promisor-fleet-only` | fleet | – | **2** | – | – | `partial clone (remote.origin.promisor)` |
| `promisor-metadata` | both | – | **2** | – | – | `partial clone (remote.origin.promisor)` |
| `promisor-metadata-unrelated-hole` | both | unrelated missing blob | **2** | – | – | `partial clone (remote.origin.promisor)` |

`non-promisor-unrelated-hole` is the anchor for the P10 row: at base an unrelated missing blob
(a blob referenced by a **post-report** tree, deleted from the store, cited nowhere, and not
needed by any audit read) leaves the verdict **unchanged** — exit 1, same single defect. So
"an unrelated hole ⇒ exit 2" is a candidate-introduced regression, not a base behaviour, and
the promisor-marked variant of the same row must stay exit 1 after the repair.

The hole is built inside the lane clone: a post-report commit (`round-1: later`, author time
3000 > cutoff 2000, so not a required commit) whose tree references a blob that is then
deleted from the object store; premises confirm the blob is absent, is referenced by a present
tree, is cited nowhere, and that `git log` over the lane still works.

`full` arm JSON: `defects=1`, `uncorrected=1`, `by_kind={landed-unresolved:1}`,
`unresolved-full-hash=0`, `landed-omitted=0`, `required_commits=1`, `cutoff=2000`,
`post_report_commits=0`, `status=failed`.

Fixture constants are deterministic (fixed identities and pinned author/committer dates):
`LC=db796f8b820bf3825c58832419138cdba23206a7`, `T=6e98d181389d343031fd578c6a775ce0889a8b0d`;
a second full build reproduced both.

## What fails the case (the falsifiers)

1. **exit 2 on any promisor arm** — the r23 harm survives; "metadata alone refuses complete
   repositories" is not repaired. This violates preregistration `expected_after[1]`, and it
   also violates `oracle-amendment-1.json` ("promisor metadata alone never changes
   local-object resolution or a clean/failed verdict"), which makes exit 2 here wrong under
   either reading.
2. **exit 1 but with an extra `unresolved-full-hash` defect** — the candidate peeled the
   existence scan too, so a *present* blob was reported as a non-existent object. The finding
   set must be exactly `{landed-unresolved: T}`.
3. **exit 0** — the wrong-type citation was accepted (the blob was treated as the landed
   commit).
4. **a different token** — the defect must name the cited object `T`, not the real commit `LC`
   and not an errata row.
5. **a renamed/new defect kind** — the tool's kind vocabulary (`KINDS`, line 78) is part of
   its documented contract; a new kind is allowed only with an explicit documentation change,
   and it must still be a definite failed finding naming `T` (not an "unknown" marker).

## Discrimination against the neighbouring cells

- **vs `CaseUnknownCitation`** (citation *absent*): that cell is now governed by
  `.ufo/waves/round-24/oracle-amendment-1.json`, which supersedes preregistration
  `expected_after[3]` prospectively — promisor metadata alone never changes the verdict, so an
  absent token in a metadata-marked but **complete** repository keeps the twin verdict
  (ordinary failed 1 + `unresolved-full-hash`, peer row **P06**), and exit 2 is reserved for a
  citation **known to name unavailable referenced local content** (peer rows **P07/P09**).
  **This cell is unaffected by that withdrawal:** `T` is *present* in the lane, so the wrong
  type is proved evidence and the verdict is exit 1 `landed-unresolved` under the original
  registration and under the amendment alike.
- **vs `OracleLocalBlobType`** (a present blob cited *outside* `## Landed changes`): there the
  blob satisfies an existence requirement → clean (exit 0). Here the same blob sits in the
  Landed section, where a **commit** is required → failed finding. Same object, opposite
  verdicts, which is exactly the point of the taxonomy split. Peer-confirmed complementary
  and non-overlapping; the analogous mutation (peeling the *bare* existence lookup) would turn
  their cell into exit 1 + `unresolved-full-hash` and would also break this cell's
  "exactly one defect, no `unresolved-full-hash`" expectation.

### Amendment note (recorded, not relabelled)

`.ufo/waves/round-24/oracle-amendment-1.json` was appended (commit `123640b`) before any
candidate was inspected, measured or integrated. It withdraws the "unknown citation in any
metadata-marked repository ⇒ exit 2" expectation prospectively; the initial registration stays
immutable and must be reported separately, not relabelled as passed. **My expectation is
unchanged by the amendment** — it strengthens it: "promisor metadata alone never changes
local-object resolution or a clean/failed verdict" is precisely what this case demands of the
metadata-marked arms (same exit 1, same single `landed-unresolved` finding as the unmarked
twin). One wording in an earlier draft of `expected.json` ("absent token in a promisor-backed
repository ⇒ exit 2") reflected the superseded `expected_after[3]`; it has been corrected and
marked as withdrawn in that file rather than deleted.

### Exact pairs to reconcile with GridOracle / CritExpected

| cell | object state | expected exit | expected finding |
|---|---|---|---|
| **C-WT1 (this lane)**, all four arms | blob **present** in the store, cited inside `## Landed changes` | **1** | exactly one `landed-unresolved`, token `T` = `6e98d181…8b0d`; `by_kind.landed-unresolved=1`, all others 0, `defects=1`, `uncorrected=1`, `status=failed`, `required_commits=1`, `reports=1`, `rounds=[1]`; **must not** contain `unresolved-full-hash` / `landed-ambiguous` / `landed-omitted` / `landed-section-missing` |
| peer **P06** | fabricated token **absent** from a **complete** store, promisor metadata on | **1** (ordinary failed) | exactly `{unresolved-full-hash, the fabricated sha}` |
| peer **P08 / P08b** | **unrelated** hole + fabricated token (promisor / non-promisor) | **1** | `{unresolved-full-hash, 0123456789abcdef0123456789abcdef01234567}` |
| peer **P07 / P09** | cited token **known to name unavailable referenced local content** | **2** (CNE) | content-derived reason, never a guessed empty verdict |
| peer **P01/P02/P03/P05/P04** | complete store, resolvable token | **0** | `defects []`, summary identical to the full-clone twin |
| **C-WT1 P10 variant** (this lane) | present blob in Landed + **unrelated** missing blob (referenced by a post-report tree, deleted from the store, cited nowhere) | **1** | exactly `{landed-unresolved, T=6e98d181…8b0d}`; base-anchored: the same row without promisor metadata already measures exit 1 today |

**Token separation.** Peer `OracleLocalBlobType` built the same shape as its P10/P10b with a
*different* fixture token `4c226b603e6a26a14212b131fcac232ca7318852`. That token belongs to
the peer fixture and must stay apart from `T=6e98d181389d343031fd578c6a775ce0889a8b0d` in
every expectations file; this file records the separation explicitly. Three tokens are live
across the wave and must not be mixed: mine `T=6e98d181…8b0d`, the peer's
`4c226b603e6a26a14212b131fcac232ca7318852`, and the fabricated token of P06/P08/P08b
`0123456789abcdef0123456789abcdef01234567`.

**Corroboration.** Two lanes built the same shape independently and their measurements agree:
my `non-promisor-unrelated-hole` = the peer's P10b (frozen base exit 1, exactly one
`landed-unresolved` defect), my `promisor-metadata-unrelated-hole` = the peer's P10 (frozen
base exit 2 `partial clone (remote.origin.promisor)`; amended expectation exit 1 with the same
single defect). Peer corroboration: `advice/OracleLocalBlobType.md` §18-§20.

The pair that must hold: *present but wrong type → failed 1* (C-WT1); *present but unavailable
required content → CNE 2* (P07/P09); *absent in a complete store → ordinary failed 1*
(P06/P08). No metadata blanket unknown in any row. A candidate that maps "does not peel to a
commit" onto exit 2 breaks C-WT1; a candidate that maps "does not peel to a commit" onto an
ordinary failed finding breaks P07/P09.

**Repair constraint this case pins (peer `ConnPlan` §3(f)).** `unknown` may arise only from a
**cited** token's absence. An unrelated hole — a missing blob in a post-report tree, cited
nowhere, needed by no audit read — must stay **exit 1 with the same single defect**,
promisor-marked or not. A store-wide closure check (for example
`rev-list --objects --missing=print`) answers "this store has a hole" and would refuse,
turning that legitimate exit 1 into exit 2; my `non-promisor-unrelated-hole` arm is the
measured counter-example (frozen base: exit 1, one `landed-unresolved` defect), so **a hole
must never be able to trigger exit 2 by itself**.

**Filed vs amended view.** `out/CaseWrongTypeCitation/expected.json` keeps the original
registration wording as filed under `discrimination_filed_view` (immutable original view) and
records the amended distinction separately under `discrimination_amended_view`; the withdrawn
`expected_after[3]` wording is *marked*, not deleted, and is not used as an expectation. The
C-WT1 expectations themselves are identical in both views.

## Containment and offline proof (`out/CaseWrongTypeCitation/containment.json`)

- Every fixture path is under the assigned scratch root
  `/fast/scratch/hyaku/kama-r24/CaseWrongTypeCitation/` (`scratch_root_inside_assigned_scratch:
  true`); the builder uses no `tempfile`, no `/tmp`.
- Lane repository: `git rev-parse HEAD` unchanged across the run; `git status --porcelain`
  delta empty; no fixture directory (`lane*`, `fleet*`, `origin*`) anywhere in the repository
  or under `.ufo/waves/round-24/`.
- No transport and no executed payload: the only remote URL in any fixture repository is a
  local filesystem path; no `core.sshCommand`, `credential.helper`, `core.gitProxy`,
  `remote.*.uploadpack`, `gpg.program` or `core.askPass` is configured (premise
  `no-remote-command-or-credential`); the fixture contains no marker program at all, so no
  arm can silently "prove" execution suppression.
- No lazy fetch: the object inventory of both repositories is byte-identical before and after
  the auditor ran (lane 3 objects / 0 packs, fleet 6 objects / 0 packs, `no_new_objects:
  true`), and the arm repositories carry no `*.promisor` pack marker.
- The only `/tmp` path touched in the measurement window belongs to **another lane**: this run
  saw `/tmp/repo-state-grid-8ywbfs55` (the r23 grid harness's own temp dir; an earlier run
  saw `/tmp/chousa-research-gate-selftest.an84Kb`). A controlled window test — snapshot
  `/tmp`, run only this builder, snapshot again — shows **no new `/tmp` entry** and no entry
  owned by this builder; `build_case.py` does not import `tempfile` and writes only under the
  scratch root.

## Not verified (unrun)

- **No candidate was measured.** At measurement time `tools/report-landing-audit.py` was
  byte-identical to the base blob (`da5041a8…65af1`); the r24 implementation did not exist
  yet, so every "expected (candidate)" row above is a **specification**, not a measurement.
- The full auditor selftest and the r23 `repo-state-grid.py` were **not** run (out of scope
  for this lane; the L1 runs them once after integration).
- Tree-typed, tag-typed and abbreviated wrong-type citations were **not** built; only the
  40-hex blob case is claimed.
- A wrong-type citation that is *also* absent, and citations in a repository whose object
  format is not sha1, are **not** claimed.
- The unrelated-hole arms build the hole in the **lane** only, and as a blob referenced by a
  **post-report** tree (so it is not a required commit). A hole referenced by a *required*
  commit's tree, or a hole in the fleet, was **not** built.
- Behaviour on git < 2.45 (`--no-lazy-fetch` unsupported) is **not** claimed for this case.
- No claim is made about untrusted repositories, live serving capability, or a higher scalar
  score.

## Files

Advice (this file):
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/advice/CaseWrongTypeCitation.md`

Artifacts (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/CaseWrongTypeCitation/`):

| file | content |
|---|---|
| `expected.json` | expected exits/findings, written **before** the builder; later arms recorded as dated amendments; filed vs amended views kept separate |
| `build_case.py` | fixture builder + auditor runner (6 arms, premise checks, unrelated-hole construction) |
| `prove_containment.py` | containment/offline proof runner |
| `capture_git_semantics.py` | captures the git-level type semantics |
| `results/results.json` | frozen measurement, all six arms, premises, inventories |
| `observed-frozen.md` | human-readable frozen result table and reproduction commands |
| `containment.json` | containment proof output |
| `git-semantics.txt` | captured `cat-file` / `rev-parse` evidence |

Scratch (fixture lives only here):
`/fast/scratch/hyaku/kama-r24/CaseWrongTypeCitation/{run,probe}`.

No production file was edited, no commit, no push, no lane Git index write, no `.jj` write.

Report: .ufo/waves/round-24/build/advice/CaseWrongTypeCitation.md
