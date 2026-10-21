# OracleMissingSourceTree — round-24 oracle report (leaf lane)

Lane: `OracleMissingSourceTree` (reviewer). Base `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`.
Scope: independent expected outcome + bounded offline fixture recipe for
*committed SOURCES parent subtree absent, report and commit local*.
No production file was edited; no candidate, full suite, or transport command was run.

---

## Verdict

**The case is well founded and its expected outcome is now pinned by measurement, not by
candidate behaviour: exit 2 (could-not-evaluate), stdout empty, no verdict — never exit 0
and never exit 1.**

Three findings carry the weight:

1. **The forbidden outcome is reachable and was measured.** A scratch derivative of the base
   auditor that catches the SOURCES read failure and treats it as "no source registry"
   (the *no-source exemption* shortcut) turns the unreadable-evidence fixtures into
   **exit 1 `failed`, `unresolved-full-hash`** — a plausible-looking verdict produced from
   absent evidence. That is exactly the harm this case names.
2. **`git cat-file --batch-check` cannot express the distinction.** For the path
   `master:corpus/SOURCES.md` it answers `master:corpus/SOURCES.md missing` with **rc=0** in
   the *unreadable* variants A, B, E **and** in the *genuinely absent* variant D — byte-identical
   answers for two different epistemic states. An implementation that maps "missing" to
   "absent" will silently apply the no-source exemption to unavailable evidence.
3. **One read path does separate them.** `git rev-list --objects --missing=print
   --no-object-names <root>` reports `?<sha>` for every unreadable object in the closure and
   reports nothing for D. Combined with the `ls-tree` entry read (which *errors* on an
   unreadable tree and *succeeds with an empty listing* on a genuinely absent path), the
   absence/unavailability distinction is decidable.

So the oracle is: **absence (the path is not in a readable tree) may carry a verdict;
unavailability (the tree or blob that would hold the path cannot be read) must be
exit 2.**

---

## 1. The case, defined precisely

Target text: *"Committed SOURCES parent subtree absent but report and commit local: CNE, not
no-source exemption."*

Read as git object graph terms:

* `corpus/SOURCES.md` **is committed** — the lane tip's tree contains the entry (the path is
  *known to exist*).
* the **parent subtree** of that entry — the `corpus` tree object — **cannot be read**
  locally (promisor-marked missing object).
* the **report** is committed and local (fleet repo, complete).
* the **cited commit** is local in the lane repo (the commit object and its blob are present).

Everything else in the fixture is held constant across the family, so the only variable is
*availability* — never promisor metadata.

Family members built (all five share the same lane history, report text and promisor
marking):

| variant | missing object | epistemic state |
|---|---|---|
| `A-corpus-tree-absent` | `corpus` tree `2176387b…` (the SOURCES **parent subtree**) | unavailable, path committed |
| `B-sources-blob-absent` | `corpus/SOURCES.md` blob `4896bca…` (parent subtree readable) | unavailable, path committed |
| `E-tip-tree-absent` | tip root tree `b37a4a2…` (treeless-clone shape) | unavailable, path committed |
| `C-content-complete-control` | none | available (contrast) |
| `D-sources-path-never-committed` | none, but `corpus/SOURCES.md` never committed | **genuinely absent** (contrast) |

`D` is the control that makes the case meaningful: it is the *only* member where the
no-source exemption is legitimate, because the path was never committed.

---

## 2. Contract anchors (why exit 2, and why not the exemption)

* `tools/report-landing-audit.py:42-46` — exit contract: `2 could-not-evaluate (missing/irregular
  report, unusable git or non-UTF-8 git output, …)`; `Errors are never verdicts.`
* `tools/report-landing-audit.py:259` — `load_source_urls` docstring: *"Read only the committed
  regular SOURCES.md blob; absent is legacy."* — "absent" is the state where the **tree says the
  path is not there**. It is not the state where the tree cannot be read.
* `tools/report-landing-audit.py:262-266` — the absence test is the *entry* lookup
  (`git ls-tree <branch> -- corpus/SOURCES.md`); an empty listing is "absent", a failing git
  call is `EvalError` → exit 2 (`tools/report-landing-audit.py:111-137`, `git()` raises on
  `rc != 0`).
* `tools/report-landing-audit.py:452-465` — the r23 blanket promisor refusal (pack marker,
  `extensions.partialclone`, `remote.*.promisor`). This is the refusal the round removes; the
  round must replace it with an *availability* decision, not with silence.
* `tools/report-landing-audit.py:93-97` — `GIT_ISOLATION` keeps `--no-lazy-fetch` and
  `--no-replace-objects`; unchanged by this case.
* `.ufo/waves/round-24/preregistration.json` — `expected_after[2]`: *"An unavailable required
  commit/tree/blob/report object: exit2 could-not-evaluate, never a clean or failed verdict."*;
  `expected_after[5]`: *"Metadata-only declarations do not establish incompleteness; content
  completeness and availability of required evidence determine the outcome."*

---

## 3. Fixture recipe (offline, bounded, deterministic)

Builder: `.ufo/waves/round-24/build/out/OracleMissingSourceTree/build_fixture.py`
(sha256 `41a396ce7a1268975f6c4de797c04c897e36b1e94f9838b43d261ec3ea61c805`).

```
python3 build_fixture.py /fast/scratch/hyaku/kama-r24/OracleMissingSourceTree/fixtures
```

Recipe, per variant (no clone transport, no fetch, no network):

1. `git init -q -b master` in `<variant>/lane` and `<variant>/fleet`.
2. Lane commit `l1` — author `kama-shokunin`, author time `@1000`, subject `round-1: work`,
   file `f`. This is the cited commit and the only *required* lane commit.
3. Lane commit `l2` — author `fixture`, author time `@1100`, subject `sources: registry`,
   file `corpus/SOURCES.md` containing one `## Registry` row whose source URL embeds the
   40-hex `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`. Author is **not** `<lane>-shokunin`, so
   `l2` is not a required landed commit — the only defect surface in the wrong-outcome arms is
   the source-URL hash.
4. Fleet commit at author time `@2000` adding `.ufo/reports/round-1/kama.md`:
   `## Work performed` names `l1` and the same source URL; `## Landed changes` cites `l1`.
   The cutoff (fleet first-add author time 2000) makes `l1` required and cited.
5. Promisor marking (config only, no `.promisor` pack pair), on the lane repo:
   `extensions.partialClone=origin`, `remote.origin.url=ssh://example.invalid/x.git`,
   `remote.origin.promisor=true`, `remote.origin.partialclonefilter=blob:none`,
   `core.sshCommand=<marker script that touches `transport-ran` and exits 1>`.
   The marker file is created **only** if a transport is attempted; it was absent after every
   run recorded here (`transport_attempted=false` in `measurements.json`).
6. Deletion of exactly one loose object per unavailable variant:
   `A` → `corpus` tree `2176387beb77e845f7ec939307ad194a505d35bc`;
   `B` → SOURCES blob `4896bca0bcd63ef84a5c9606a7f0376260ce3ab2`;
   `E` → tip root tree `b37a4a2866bf7221acacf8e7d4c968a51cb4795e`.
   `C` and `D` delete nothing.
7. The **working-tree copy of `corpus/SOURCES.md` stays on disk** in every variant. The auditor
   reads committed bytes only (`tools/report-landing-audit.py:259`), so a worktree copy must not
   be admissible evidence; keeping it makes that observable (git's own message becomes
   `path 'corpus/SOURCES.md' exists on disk, but not in 'master'`).

The fixture is byte-reproducible: fixed authors, dates and content give fixed object ids
(`l1=16fc48b75a999ed3ef602c49dcf61d992324fa81`, `l2=c07a93e0de943426c19aa3057bd324822a63273f`,
corpus tree `2176387b…`, SOURCES blob `4896bca…`, tip tree `b37a4a2…`), identical across two
independent rebuilds.

Premise checks recorded in `receipt.json` (all true): the dropped object existed as a loose
object and was removed; the cited commit resolves (`cat-file -t` → `commit`); the fleet report
is readable (`git show HEAD:.ufo/reports/round-1/kama.md` → rc 0); the lane repo is a sha1
top-level, non-shallow repository; `git log` over the lane branch succeeds in every variant
(commit objects are present, only trees/blobs are not).

---

## 4. Independent expected outcome (the oracle)

Graded on the **current arm**; the frozen (r23) arm is reported for history.

| variant | expected exit | stdout | expected defect kinds | forbidden |
|---|---|---|---|---|
| `A-corpus-tree-absent` | **2** | empty (no verdict document) | — | exit 0, exit 1 |
| `B-sources-blob-absent` | **2** | empty | — | exit 0, exit 1 |
| `E-tip-tree-absent` | **2** | empty | — | exit 0, exit 1 |
| `C-content-complete-control` | **0** | verdict JSON, `status=clean` | `[]` | exit 2 (the r23 harm) |
| `D-sources-path-never-committed` | **1** | verdict JSON, `status=failed` | `["unresolved-full-hash"]`, token `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` | exit 2 |

Additional graded properties for A, B, E:

* stderr begins with `could-not-evaluate:` (the `tools/report-landing-audit.py:949` path);
* no traceback, no timeout, no executed repository program (`transport-ran` absent);
* the exit-2 reason should name the unreadable object (advisory only — see §8).

Positive assertion for C: `source_url_hashes == ["704366d76f8748cf9ad3df62a464bfcc8d1ae6ad"]`
proves the registry was actually read and the URL hash classified, rather than the run
coinciding with a clean report.

D is the case's semantic anchor: the path was **never committed**, so the no-source exemption
legitimately applies and the registry URL's hash is a genuine `unresolved-full-hash` defect
(same rule as the committed selftest case `absent-source-registry-is-no-exemption`,
`tools/report-landing-audit.py:732-734`).

---

## 5. Measurements

Script: `.ufo/waves/round-24/build/out/OracleMissingSourceTree/measure_base_probes.py`
(sha256 `aca5aaf4d0077576cde5500d4b3703e8f3b17d06038391dbe026d582bbd8333e`).
Raw results: `.ufo/waves/round-24/build/out/OracleMissingSourceTree/measurements.json`
(sha256 `e6e8ef779bb3a87c995d66cf703d2966f40b876f473c229b312110e2ad217d19`).

Arms (all scratch copies of the base file; **the repository file was not modified**):

* `base` — `tools/report-landing-audit.py` as committed at the base (sha256
  `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1`). That blob is
  byte-identical at the preregistration base `0df800e8…`, at the lane's current HEAD
  `123640b4…` and in the working tree, so the matrix below still describes the file the
  repair lane is editing.
* `lifted` — base with the two blanket promisor refusal blocks removed
  (`tools/report-landing-audit.py:452-457` pack marker, `:459-465` config keys); everything
  else byte-identical. This is the r24 *shape*.
* `exempt` — `lifted` plus a catch-and-pass around the SOURCES read
  (`source_urls = load_source_urls(...)` → `try/except EvalError: source_urls = None`).
  This is the **no-source exemption** shortcut this case forbids.

Observed (exit / status / kinds / verdict-JSON / transport):

| variant | base (r23) | lifted | exempt |
|---|---|---|---|
| A | 2 — `partial clone (extensions.partialclone)` | **2** — `git ls-tree … rc=1 error: Could not read 2176387b…` | **1 failed** `unresolved-full-hash` ← forbidden |
| B | 2 — `partial clone (extensions.partialclone)` | **2** — `git cat-file blob 4896bca… rc=128 fatal: … bad file` | **1 failed** `unresolved-full-hash` ← forbidden |
| E | 2 — `partial clone (extensions.partialclone)` | **2** — `git ls-tree … rc=128 fatal: not a tree object` | **1 failed** `unresolved-full-hash` ← forbidden |
| C | 2 — metadata refusal (the r23 harm) | **0 clean**, `source_url_hashes=[704366d7…]` | 0 clean |
| D | 2 — metadata refusal | **1 failed** `unresolved-full-hash` token `704366d76f…` | 1 failed |

`transport_attempted=false` for every arm/variant pair; no traceback; no timeout.

Reading of the table:

* The base's exit 2 on A/B/E comes from **promisor metadata** — the refusal the round removes.
  It reaches the right exit class for the wrong reason, so A/B/E are **no-harm rows**: they
  must not regress to a verdict when the metadata refusal is lifted.
* `lifted` reaches exit 2 through the *object* path (git's own error), which is the desired
  mechanism: unavailability, not metadata.
* `exempt` is the failure this case exists to catch: **exit 1 `failed`** produced from evidence
  that was never read. Its token is the registry URL's hash — the defect exists only because
  the registry that would have authorised the hash could not be read.
* C and D are the policy rows: same promisor metadata, different availability, different
  outcome. C is the r24 headline (metadata alone must not refuse a content-complete repository);
  D keeps the legacy exemption honest (a genuinely absent registry is not an exemption).

---

## 6. Which read paths can decide absence vs unavailability

Script: `.ufo/waves/round-24/build/out/OracleMissingSourceTree/probe_read_paths.py`
(sha256 `0ece327847bad721df8f9cee91fd1acc860352615daa53a705cb21a9e56291de`).
Raw results: `.ufo/waves/round-24/build/out/OracleMissingSourceTree/read_paths.json`
(sha256 `8de7e85b2e40bcc35756aa919a45f10b1c78c42f098fc860e30e9aa2fb9a3593`).

All probes ran with `--no-lazy-fetch --no-replace-objects`, `GIT_CONFIG_GLOBAL=/dev/null`,
`GIT_CONFIG_NOSYSTEM=1` — the auditor's own isolation (`tools/report-landing-audit.py:93-114`).

| read path | A subtree absent | B blob absent | C complete | D path never committed | E tip tree absent |
|---|---|---|---|---|---|
| `ls-tree <tip> -- corpus/SOURCES.md` | **rc=1** `error: Could not read 2176387b…` | rc=0, entry present | rc=0, entry present | rc=0, **empty** | **rc=128** `fatal: not a tree object` |
| `ls-tree -r <tip> -- …` | rc=1 (same error) | rc=0 entry | rc=0 entry | rc=0 empty | rc=128 |
| `ls-tree <tip>` (root) | rc=0 (lists `corpus` sha) | rc=0 | rc=0 | rc=0 (no `corpus`) | rc=128 |
| `rev-parse <tip>:corpus/SOURCES.md` | rc=128 `exists on disk, but not in 'master'` | rc=0, sha | rc=0, sha | rc=128 `does not exist in 'master'` | rc=128 |
| `cat-file --batch-check` on the path | **`missing`, rc=0** | **`missing`, rc=0** | `sha blob 394`, rc=0 | **`missing`, rc=0** | **`missing`, rc=0** |
| `rev-list --objects --missing=print --no-object-names <tip>` | `?2176387b…` | `?4896bca…` | *(no `?`)* | *(no `?`)* | `?b37a4a2…` |

Consequences for the implementation:

* **`cat-file --batch-check` is unusable as the presence test** for this path: it returns the
  same answer for "not committed" (D) and "cannot be read" (A/B/E). Mapping that answer to
  "absent" is the no-source exemption and yields the forbidden exit 1.
* The **`ls-tree` entry read separates A/E (git fails) from D (empty listing)** — an
  implementation that lets the `ls-tree` failure propagate as `EvalError` satisfies A/B/E for
  free and keeps D a verdict.
* For **B** the entry exists and only the blob is unreadable: `git cat-file blob <sha>` fails
  (`rc=128`, `bad file` under `--no-lazy-fetch`), so the blob read must not be downgraded to
  "no registry".
* The **closure check** `rev-list --objects --missing=print --no-object-names <root>` reports
  exactly the unreadable objects (`?<sha>`) and reports nothing for D and C. It is the one probe
  that decides all five variants from a single reading, and it is also the probe the repair lane
  was pointed at.

---

## 7. What the candidate must satisfy (acceptance for this case)

1. A lane repository that is promisor-marked **and** missing the committed SOURCES subtree/blob
   yields **exit 2 with an empty stdout** — no verdict document, no defect kinds, no status.
2. A lane repository that is promisor-marked **and content-complete** yields the same
   substantive verdict as an otherwise identical full clone (C: exit 0 clean, registry URL
   hash classified).
3. A lane repository whose `corpus/SOURCES.md` **was never committed** still yields the legacy
   verdict (D: exit 1, `unresolved-full-hash`) — the absence/unavailability distinction is
   preserved, not collapsed.
4. No read path maps an unreadable object to "the path is absent".
5. `--no-lazy-fetch`, `--no-replace-objects`, log/signature suppression and the git timeout are
   unchanged; the fixture's `core.sshCommand` marker is never triggered.

---

## 8. Cross-lane notes and residual risk

* **Policy rows.** C and D are rows whose expected exit *changes* from the r23 arm (2 → 0 and
  2 → 1) because the refusal cause changes from promisor metadata to object availability. They
  belong in the retained-history comparison with that change stated explicitly; A, B and E are
  no-harm rows (2 → 2, same exit class, different reason).
* **Reason strings.** I deliberately did **not** pin a stderr substring for A/B/E: the
  round-24 repair may legitimately produce either an object-level reason (`Could not read`,
  `bad file`, `missing object …`) or the leftover metadata reason, and both satisfy the exit
  class this case grades. If the grid wants a pinned reason, the object-level readings measured
  above are the defensible set: `Could not read`, `bad file`, `not a tree object`,
  `missing object`. A metadata-only reason on A/B/E would be acceptable for the exit class but
  would indicate the headline repair (C) is still missing.
* **Scoping the availability check.** A closure check over the whole lane history also flags
  objects that the audit never needs. The sibling lane `OracleMissingNonrequired` owns the
  question of a missing *non-required* object; my case only fixes that the SOURCES subtree and
  blob **are** required (they are the only admissible evidence of the registry), so they must
  force exit 2.
* **Working-tree evidence.** The fixture keeps `corpus/SOURCES.md` on disk. An implementation
  that reads the worktree copy instead of the committed blob would produce C's clean verdict on
  A/B/E — a verdict from evidence the auditor's contract excludes
  (`tools/report-landing-audit.py:259`).
* **Not run.** The r24 candidate does not exist yet, so no candidate or full-suite run was
  performed (per lane bounds). `tests/report-audit/promisor-grid.py` does not exist in the
  tree yet; the rows above are specified here for it to adopt. The frozen arm of the historical
  `repo-state-grid.py` was not re-run either.

## 9. Reproduction

```
cd /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/OracleMissingSourceTree
python3 build_fixture.py /fast/scratch/hyaku/kama-r24/OracleMissingSourceTree/fixtures > receipt.json
python3 measure_base_probes.py /fast/scratch/hyaku/kama-r24/OracleMissingSourceTree/fixtures measurements.json
python3 probe_read_paths.py   /fast/scratch/hyaku/kama-r24/OracleMissingSourceTree/fixtures read_paths.json
```

Environment: git 2.56.0, python 3.14, Arch x86_64; scratch
`/fast/scratch/hyaku/kama-r24/OracleMissingSourceTree` (no `/tmp` heavy files).

## 10. Named files

* `.ufo/waves/round-24/build/out/OracleMissingSourceTree/build_fixture.py` — fixture builder.
* `.ufo/waves/round-24/build/out/OracleMissingSourceTree/measure_base_probes.py` — base/lifted/exempt measurement.
* `.ufo/waves/round-24/build/out/OracleMissingSourceTree/probe_read_paths.py` — read-path discriminator.
* `.ufo/waves/round-24/build/out/OracleMissingSourceTree/receipt.json` — fixture identity + premise checks.
* `.ufo/waves/round-24/build/out/OracleMissingSourceTree/measurements.json` — exit/status/kind matrix.
* `.ufo/waves/round-24/build/out/OracleMissingSourceTree/read_paths.json` — per-read-path outcomes.
