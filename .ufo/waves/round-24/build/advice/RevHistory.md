# RevHistory — rounds 10–23 historical semantics, errata ledger, and the exact committed inputs for byte-identical parity

Seat: `KamaR23-2.RevHistory-2` (leaf member; no subagent dispatch).
Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`, base `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`.
Scope: bounded static review of the historical rounds 10–23 semantics and errata, and the
identification of the exact committed inputs that a byte-identical parity check depends on.
No production edit, no commit, no grid/selftest/mutant run, no network.

Tools already present, no installs or updates: git 2.56.0, Python 3.14.8.

---

## Verdict

1. **The rounds 10–23 ledger is intact and reproducible today.** The r23 base tool
   (`0df800e:tools/report-landing-audit.py`, blob `cf706c52…`, sha256 `da5041a8…`) run read-only
   against the real lane and fleet repositories with `--rounds 10-23` exits **0**:
   14 reports, 59 required commits, 9 defects, 9 corrected, 0 unmatched, 0 invalid,
   `status=clean`. `--no-errata` exits **1** with the same 9 defects uncorrected.
2. **The r23 filed evidence is reproduced byte-for-byte for rounds 10–22.** The per-round result
   dicts of today's base run are equal (JSON-canonical) to
   `.ufo/waves/round-23/final/audit-historical-ledger.stdout` for every round 10–22, and the
   10–22 summary matches the filed summary exactly (13 reports, 54 required, 9 defects,
   9 corrected, 0 unmatched, 0 invalid, clean). Verified by direct comparison.
3. **The r24 promisor repair needs no change to the historical semantics**, because neither audited
   repository carries promisor metadata (no `extensions.partialclone`, no true `remote.*.promisor`,
   no `.promisor` marker, no `objects/info/alternates`, no grafts, sha1, top-level, non-shallow —
   both repos, checked read-only). The whole "absence" surface of rounds 10–23 is **two** tokens:
   one genuine absence (round 20) and one exemption (round 22, inside a Registry URL). Section 6.
4. **Byte-identical parity is mechanically checkable and needs exactly four committed inputs**
   (two frozen auditor blobs, one errata-ledger blob, one SOURCES blob) plus the fleet report
   blobs and lane commit tuples that fix the cutoffs. All are enumerated with digests in
   `.ufo/waves/round-24/build/out/RevHistory/parity-manifest.json`. Section 4.
5. **Two policy decisions remain open for L1** and they decide the retained r23 grid's promisor-row
   expectations (F23 reason, F27 exit, T01 exit) and one availability rule (missing `corpus/SOURCES.md`
   blob in a promisor-backed lane). They are stated in Section 7 with the exact consequence of each
   option. They are *not* decided here.

---

## 1. Method and commands actually run

Read-only against the real repositories; no writes to any repository, index or `.jj`.

```
git -C /home/vgpnk/Projects/shokunin/kama-shokunin cat-file blob 0df800e:tools/report-landing-audit.py | sha256sum
python3 tools/report-landing-audit.py --lane-repo <lane> --fleet-repo /home/vgpnk/Projects/shokunin --rounds 10-23 --json
python3 tools/report-landing-audit.py --lane-repo <lane> --fleet-repo /home/vgpnk/Projects/shokunin --rounds 10-23
python3 tools/report-landing-audit.py --lane-repo <lane> --fleet-repo /home/vgpnk/Projects/shokunin --rounds 10-23 --no-errata --json
python3 tools/report-landing-audit.py --lane-repo <lane> --fleet-repo /home/vgpnk/Projects/shokunin --rounds 10- --json
python3 .ufo/waves/round-24/build/out/RevHistory/make-manifest.py
```

Scratch clone (observation only, per contract):
`git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r24/RevHistory/lane`
(HEAD `d1b9d956a0beda9ac32a1a2cf6ced875faeada0d`; the clone's `master` == the lane's `master`).

Lane tip drift during the wave: `master` is now `d1b9d956` ("round-24: preregister promisor
completeness repair and correct r23 closure interpretation"), one commit ahead of the preregistered
base `0df800e`; it touches only `.ufo/waves/round-24/preregistration.json` and `LOG.md`
(`git diff --stat 0df800e master` → 2 files, 39 insertions). The three parity-critical lane blobs
are **identical** at base and at `master` (Section 4).

---

## 2. What rounds 10–23 mean (semantics, frozen)

Base tool at `0df800e`, real repositories, `--rounds 10-23`. `cutoff` = author time of the
*earliest* fleet add-event of `.ufo/reports/round-N/kama.md` (`report_cutoff`, base blob lines
215–219: `git log --diff-filter=A --format=%at` and `out[-1]`). `required` = lane commits by
`kama-shokunin` whose subject starts `round-N:` or `checkpoint(rN)` with author time ≤ cutoff.

| round | fleet report blob | add-event (cutoff) | lane round-commits | required | post_report | defects | errata rows |
|---|---|---|---|---|---|---|---|
| 10 | `371a19e2…` | `b69b7ba2…` @1792450135 | 2 | 2 | 0 | `landed-omitted 40660352…` | 11 |
| 11 | `6a683517…` | `dff17307…` @1792468776 | 2 | 2 | 0 | — | — |
| 12 | `08c3333a…` | `5ee71e4c…` @1792471121 | 2 | 2 | 0 | — | — |
| 13 | `965fd043…` | `3ecce953…` @1792472920 | 2 | 2 | 0 | — | — |
| 14 | `f8d76a8f…` | `52c833d1…` @1792478534 | 2 | 2 | 0 | — | — |
| 15 | `f7ec3bd2…` | `402b93b5…` @1792485831 | 3 | 3 | 0 | — | — |
| 16 | `5906d891…` | `9ec9c524…` @1792505790 | 3 | 3 | 0 | — | — |
| 17 | `ba6b24f2…` | `54343767…` @1792524895 | 2 | 2 | 0 | — | — |
| 18 | `df4ea712…` | `23bdc3f8…` @1792561152 | 7 | 7 | 0 | `landed-omitted 101f3991…`, `1c325b2e…`, `c6dc46fa…` | 8, 9, 10 |
| 19 | `09de243f…` | `ac9859f4…` @1792565257 | 12 | 8 | 4 | — | — |
| 20 | `54b1aff4…` | `04eb5d2d…` @1792577594 | 9 | 9 | 0 | `unresolved-full-hash 0957ce61…`, `landed-omitted 846e366d…`, `92b14625…`, `0957ce61…`, `33a67778…` | 3, 7, 6, 5, 4 |
| 21 | `1e90c07f…` | `7bc15cdf…` @1792582628 | 8 | 7 | 1 | — | — |
| 22 | `a260f8a5…` | `36e37a3b…` @1792593755 | 5 | 5 | 0 | — | — |
| 23 | `6dbb1a2f…` | `410b5110…` @1792603243 | 5 | 5 | 0 | — | — |

Totals: 14 reports, 59 required, 5 post-report commits, 9 defects (8 `landed-omitted`,
1 `unresolved-full-hash`), 9 corrected, `status=clean`, exit 0.

Semantics that the r24 candidate must preserve verbatim (base blob, `0df800e`):

- `lookup` (139–174): `missing` is a **verdict input** (`unresolved-full-hash` / `landed-unresolved`),
  not an error. Line 159–160 (`if line.endswith(" missing"): continue`) is the exact place where the
  r24 promisor rule must branch — and it must branch **only** for promisor-backed repositories.
- `classify_full_hashes` (283–300): a 40-hex token inside an exact Registry URL from the committed
  `corpus/SOURCES.md` blob, outside `## Landed changes`, is classified (not a citation).
- `audit_round` (302–357): `landed-omitted` is decided from the **presence** of a lane commit
  (author-time ≤ cutoff) and the **absence of a citation prefix** in the Landed section
  (lines 343–352). Presence is local, so an omission stays provable in a promisor-backed clone.
- `apply_errata` (387–409): a `landed-omitted` row is valid only when its correction equals the
  omitted token exactly (line 401–402); a resolvable row is valid only when the correction resolves
  to a commit (line 398–400).
- `load_errata` (374–385) reads the ledger from the **committed lane blob** at the pinned tip
  (`git show <tip>:registry/report-landing-errata.tsv`).
- `load_source_urls` (258–281) reads `corpus/SOURCES.md` from the **committed lane blob** at the tip;
  absent ⇒ `None` ⇒ "legacy, no registry".

`--rounds 10-` (open range) selects the same 14 rounds today, because the fleet has no committed
`.ufo/reports/round-24/kama.md` (`git rev-parse HEAD:.ufo/reports/round-24/kama.md` → MISSING).
**This will change when the fleet lands the round-24 report** — see hazard H5.

---

## 3. Errata ledger audit (rounds 10–23)

Committed input: `registry/report-landing-errata.tsv`
— git blob `90d84c9d94a781e425c06c96f78467483b63be98`, sha256
`3b98184195302539ee8bee69f31997f291006fabd392156466a2e70b381adb7c`, 2706 bytes,
identical at `0df800e` and at `master` (`d1b9d956`).

Rows (file line numbers are the `corrected_by` values in the audit output):

| line | round | kind | token | correction | correction == token? | resolves to |
|---|---|---|---|---|---|---|
| 3 | 20 | `unresolved-full-hash` | `0957ce619789d13d894ef21bc863486bcb35b56c` | `0957ce619789d13bb5779606078fa1498114d2c7` | no (deliberate: a spliced hash) | lane commit `0957ce61…` |
| 4 | 20 | `landed-omitted` | `33a6777866d0f63d894ef21bc863486bcb35b56c` | same | yes | lane commit |
| 5 | 20 | `landed-omitted` | `0957ce619789d13bb5779606078fa1498114d2c7` | same | yes | lane commit |
| 6 | 20 | `landed-omitted` | `92b146253fd3a8c4bfade94c909dc63b13d6f4a8` | same | yes | lane commit |
| 7 | 20 | `landed-omitted` | `846e366dc9dbac58463494a7e05ad060ae3ed3b0` | same | yes | lane commit |
| 8 | 18 | `landed-omitted` | `101f3991d3570bc9350fbf9c5561f4be1185699d` | same | yes | lane commit |
| 9 | 18 | `landed-omitted` | `1c325b2e58fcfdc6761f645b44cedfb1d65243e6` | same | yes | lane commit |
| 10 | 18 | `landed-omitted` | `c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d` | same | yes | lane commit |
| 11 | 10 | `landed-omitted` | `40660352d4a9eb00a5d6195f0f064f5c64618143` | same | yes | lane commit |

Observed ledger state in the base run: `errata_rows 9`, `errata_unmatched 0`, `errata_invalid 0`,
`corrected 9`, `uncorrected 0`. All 9 corrections resolve as commits (`cat-file --batch-check`:
`0957ce61…` → `commit`). Ledger semantics audited:

- 8 of 9 rows are "the correction is the omitted commit itself"; 1 row (line 3) corrects a
  *spliced* token to the real measured-tree commit.
- Every correction is a **lane** commit; no row is resolved by a fleet-only object.
- `errata_unmatched` is computed only for selected rounds (base blob 388–389) while `errata_invalid`
  is not round-filtered (396–398): an invalid row for an unselected round still fails the run.
- The ledger is append-only by contract (`registry/report-landing-errata.tsv` header). Appending a
  row **after line 11** keeps existing `corrected_by` line numbers stable but changes
  `errata_rows` (9 → 10) in the JSON — so the parity measurement must be taken with the ledger
  blob unchanged, or the expected digest recomputed.

### 3.1 Round-23 filed-evidence erratum (the one the preregistration asks to append)

The preregistration's `expected_after[6]` asks for corrections to the r23 filed evidence:
"69 falsify-wave lane reports, not 68; 40 of 56 killed FIFO-process identities retained, not full
identity evidence."

- The correction is **already committed** in the lane `LOG.md` round-24 section
  (`LOG.md:1417–1420`, committed in `d1b9d956`): "falsify wave has 69 durable lane reports, not 68
  (RowC03 wrote before its final response aborted); 40 of the 56 killed FIFO-process identities were
  retained, not all 56. Filed round-23 bytes remain immutable."
- I independently re-derived the first half from the committed falsify evidence:
  `.ufo/waves/round-23/falsify/advice/` holds **70** entries, of which one is
  `swarm-registry.json` (not a lane report) ⇒ **69 durable lane reports**, and
  `RowC03FabricatedFull.md` (the seat whose final response aborted) is present. The falsify
  registry (`.ufo/waves/round-23/falsify/registry.json`) lists 73 members, matching the filed
  report's "Wave 2 falsify: 73 seats … Dead: 4".
- The filed fleet report bytes are untouched and still say "56 orphaned FIFO-blocked git processes
  from this round were killed" (`.ufo/reports/round-23/kama.md:34`) and "Wave 1 build: 68 seats"
  (`:143`) — immutable by contract, corrected only in `LOG.md`.
- **Unverified by me:** I did not locate a committed artifact that enumerates the 56 killed
  FIFO-blocked git processes or the 40 retained identities, so the second half of the erratum stays
  a filed-claim correction whose underlying measurement is not re-checkable from the committed r23
  evidence. No r23 file contradicts it; nothing in the committed evidence re-derives it either.

---

## 4. Exact committed inputs required for byte-identical parity

Machine-readable form (regenerable with `make-manifest.py`):
`.ufo/waves/round-24/build/out/RevHistory/parity-manifest.json`.

### 4.1 The two frozen auditors (must be reachable via `git cat-file` in the lane repo)

| role | rev | git blob | sha256 | bytes |
|---|---|---|---|---|
| frozen arm of the **round-24** grid (= r23 base = preregistration base) | `0df800e896f6bce285a81e794ad4ae1d1e6c3a71` | `cf706c52233139920da60f8b55d06f031286c4f9` | `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` | 46778 |
| frozen arm of the **retained r23** grid (unchanged) | `4fe9339f8fc3a4a4a479d9c938a850da12f1124d` | `fcc255ce5115a749dfbd09cf992ba9851a2dc90a` | `09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f` | 40404 |

Both are committed objects in the lane repo (verified by `git cat-file blob`).

### 4.2 The two lane blobs the audit reads

| input | path | git blob | sha256 |
|---|---|---|---|
| errata ledger | `registry/report-landing-errata.tsv` | `90d84c9d94a781e425c06c96f78467483b63be98` | `3b98184195302539ee8bee69f31997f291006fabd392156466a2e70b381adb7c` |
| source registry | `corpus/SOURCES.md` | `bf54e3d9d8bc3e65371e0c701096242e6d9ae747` | `274d50916eb04b158f4f2b2fbc0ffdfaec56270aeb54282d4f2d95d193744993` |

Both are byte-identical at `0df800e` and at `master` (`d1b9d956`). The r24 candidate must not
modify either (the ledger is append-only; the registry is append-only per
`tools/sources-append-only.py`).

### 4.3 The fleet inputs (round report bytes + add-events)

Per round: the fleet report blob id and the add-event commit + author time are in
`parity-manifest.json` → `rounds[]` (`fleet_report_blob`, `fleet_add_events`) and the full table is
in Section 2. Each round has exactly **one** add-event (no delete/re-add), so the cutoff is unique
and stable. Fleet HEAD at measurement: `be5a23eb39df0ec5f3231c360ec6e2ae381a8673`
(`/home/vgpnk/Projects/shokunin`).

### 4.4 The lane inputs (round-commit tuples)

per round, the tuple (sha, author, atime, subject) of every commit matching
`^(round-N:|checkpoint(rN))` by `kama-shokunin`, as returned by
`git log -z --format=%H%x00%an%x00%at%x00%s <tip>` — in `parity-manifest.json` →
`rounds[]` → `lane_round_commits`. **64** such commits across rounds 10–23
(per round 2,2,2,2,2,3,3,2,7,12,9,8,5,5) = **59 required + 5 post-report**.

### 4.5 The repository-state facts that decide `check_history_repo` (base blob 438–465)

| fact | lane | fleet |
|---|---|---|
| `--show-object-format` | `sha1` | `sha1` |
| `--is-shallow-repository` | `false` | `false` |
| `--show-prefix` | `` (top level) | `` (top level) |
| promisor/partialclone config keys | none | none |
| `.promisor` pack markers | none | none |
| `objects/info/alternates` | absent | absent |
| `.git/info/grafts` | absent | absent |

Because all four refusal inputs are negative in both repositories, the **r24 candidate's new
promisor rule cannot fire on the historical range** — the audit's "missing" path must keep producing
verdicts, not exit 2. That is the single most important no-harm property for this lane.

### 4.6 What the new `tests/report-audit/promisor-grid.py` must pin (committed inputs)

Modeled on the committed r23 grid (`tests/report-audit/repo-state-grid.py`, docstring lines 1–17,
`FROZEN` line 32, `TIMEOUT` line 37, `population()` lines 711–715, `run_case()` 717–768, `main()` 771–840):

- the **frozen auditor rev** `0df800e896f6bce285a81e794ad4ae1d1e6c3a71` and its blob
  `cf706c52233139920da60f8b55d06f031286c4f9` / sha256 `da5041a8…` (Section 4.1) — the frozen arm
  must be read with `git cat-file blob <rev>:tools/report-landing-audit.py` from the lane repo, so
  the frozen bytes stay committed and hermetic against the moving working tree;
- the **current arm** = `tools/report-landing-audit.py` beside the grid (or `--current PATH`), with
  its sha256 recorded per arm in the JSON document (r23 grid, `main()` lines 787–790);
- a **population sha256** over the case table *and* the reason table (r23 grid `population()`:
  `json.dumps(rows, sort_keys=True)` over `[name, kind, builder, exit, kinds, reason]`), so a silent
  change of an expectation or a reason pin is visible;
- the **per-case timeout** that kills the auditor's whole session (r23 grid `TIMEOUT = 30` (line 37),
  `start_new_session=True` + `os.killpg`), because a FIFO-blocked git grandchild must not survive
  the case;
- the **fixture premise** check per case (r23 grid `require(...)`): a fixture whose fault never
  materialized must make the grid exit 2, not a pass. For the promisor fixtures this means the
  premise must assert *both* that the missing object is really missing and that no transport ran;
- the **non-promisor no-harm rows** carried over from the r23 grid, with their exit *and* reason
  pins unchanged (F10 `shallow repository`, F11 `rewrites history`, F13 `names a ref`, F15
  `object format`, F21 `not a repository top level`, F30 `timed out after`).

---

## 5. Byte-identity targets (what "byte-identical parity" means concretely)

Measured with the r23 base tool against the real repositories, fleet path
`/home/vgpnk/Projects/shokunin`:

| artifact | exit | sha256 | sha256 with the fleet path replaced by `<FLEET>` |
|---|---|---|---|
| `base-10-23.json` (`--rounds 10-23 --json`) | 0 | `efb3870ca95061b74c0f4258d4e75cdb0228d707976a2c1ac5ffa6ac275c035e` | `d63f902f32059d3918c5cbb2a4d94541d9da7a8863ee904f2628229e58889a8b` |
| `base-10-23.txt` (text render) | 0 | `e81d809b569660afaf7c31d986c6056dfa05f873a58373bfeb208960ea240a59` | same (no path in the text output) |
| `base-10-23-noerrata.json` (`--no-errata --json`) | 1 | `6c5430970595ec3fe3d58a97c23441316af0671a2c9b8db70a4e0ec9c538d19f` | `c1342fb2352df4e51e7a1c56057cfb5291bce193b55b2be1fbfdb0e4b8e2e813` |

Files: `.ufo/waves/round-24/build/out/RevHistory/base-10-23.{json,txt}`,
`…/base-10-23-noerrata.json`.

**The JSON embeds the absolute fleet report path** (`"report": "/home/vgpnk/Projects/shokunin/.ufo/reports/round-10/kama.md"`).
Therefore byte-identical comparison between the frozen and the current arm is only meaningful when
**both arms run against the same fleet repository path**. The r23 falsify wave already does this:
its `nh-history-parity` harness (`.ufo/waves/round-23/falsify/out/CritNoHarmRecipe/parity-commands.json`)
compares `(returncode, stdout, stderr)` of both arms against the same `lane`/`fleet` arguments, and
the lane arm is a clone (`KAMA_LANE_REPO=<clone>`) so the auditor bytes are hermetic against the
moving working tree. **Reuse that harness for r24** with two edits (Section 8, H1/H2).

---

## 6. The absence surface of rounds 10–23 (what the promisor rule must do here)

Token universe of the 14 fleet report blobs: **56** distinct 40-hex tokens.
Resolution against the two repositories (`cat-file --batch-check`):

- 54 resolve (54 lane commits live only in the lane repo; the fleet repo holds none of them —
  this is normal, the reports cite lane work).
- **2 are absent from both repositories:**
  1. `0957ce619789d13d894ef21bc863486bcb35b56c` — **round 20 only**. This is the deliberate splice
     defect: it is the round-20 `unresolved-full-hash` defect, corrected by errata line 3.
     It is the **only genuine absence** in rounds 10–23.
  2. `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` — **round 22 only**. It is **not** a citation: it
     occurs inside exact Registry source URLs in the committed `corpus/SOURCES.md`
     (rows S035–S060, e.g. `https://github.com/ggml-org/llama.cpp/blob/704366d7…/tools/server/README.md`),
     so `classify_full_hashes` classifies it and it never becomes a defect. An implementation that
     turns "absent object" into exit 2 *before* URL classification would wrongly refuse round 22.

Consequences for the r24 policy, stated as acceptance points:

- **A1.** In a repository pair where neither side is promisor-backed, an absent token must stay a
  verdict: round 20's `0957ce61…` remains `unresolved-full-hash` (corrected by errata line 3), and the
  run stays `status=clean` exit 0. A candidate that maps "missing" → exit 2 globally breaks
  byte-parity on rounds 10–23 (the baseline becomes exit 2 with 1 unresolved token).
- **A2.** URL classification must run **before** any promisor-absence rule: round 22's
  `704366d7…` is absent from both repositories and must not become exit 2, a defect, or a
  "citation unavailable" observation.
- **A3.** Under the preregistration's rule "a missing citation in any promisor-backed repository is
  unknown … exit2", the *real* rounds 10–23 **cannot** be reproduced as clean under a promisor-marked
  clone: round 20's absent splice token would become exit 2. Therefore the promisor-parity fixture
  must be a **local synthetic offline fixture** (as the preregistration's `oracle` says), not a
  promisor-marked clone of the real repositories. The historical parity check (rounds 10–23) and the
  promisor check (synthetic fixture) are two different measurements and must not be merged.
- **A4.** A *genuine omission* must stay exit 1 under promisor metadata: the omission is proved by
  the **presence** of a lane commit and the absence of a citation prefix, both local facts. No
  promisor rule may convert `landed-omitted` into exit 2.

---

## 7. Parity hazards for the r24 implementation (with acceptance points)

Line numbers refer to the r23 base blob `0df800e:tools/report-landing-audit.py`.

**H1 — the parity harness must repin the frozen arm.**
The r23 recipe entry `nh-history-parity` pins the frozen auditor at `4fe9339f…` and the ranges
`10-21`/`10-22` (`.ufo/waves/round-23/recipe.json`, entry `nh-history-parity`; same body in
`.ufo/waves/round-23/falsify/out/CritNoHarmRecipe/parity-commands.json`). For r24 the frozen arm is
the r23 base `0df800e…` and the range is `10-23` (plus `10-22` to stay comparable with the r23
filed evidence). Acceptance: the recipe entry names `0df800e896f6bce285a81e794ad4ae1d1e6c3a71` as the
frozen rev and prints `10-23 [] current 0 frozen 0 same` and
`10-23 ['--no-errata'] current 1 frozen 1 same`.

**H2 — the r24 grid's own frozen arm is a different blob.**
`tests/report-audit/repo-state-grid.py` pins `FROZEN = "4fe9339f8fc3a4a4a479d9c938a850da12f1124d"`
(line 32). A new `tests/report-audit/promisor-grid.py` must pin `0df800e…` instead (Section 4.1).
Keeping the retained r23 grid's own `FROZEN` at `4fe9339f…` is correct — that is its historical
frozen arm; do not re-pin it.

**H3 — the recipe's historical entries must move to `10-23`.**
`.ufo/waves/round-23/recipe.json` has `audit-historical-ledger` (`--rounds 10-22`, exit 0) and
`audit-historical-raw` (`--rounds 10-22`, exit 1). For r24 they become `10-23` (exit 0 / exit 1)
and their stdout digests become the Section 5 targets — except that the digest changes if the
fleet path changes, so pin the *path-normalized* digest as the stable value.

**H4 — `check_history_repo` must keep its other refusals.**
Base blob 438–465: sha1 (443–445), top level (446–447), non-shallow (448–449), grafts (450–453),
promisor pack (454–457), promisor config (458–465). Only the last two are in scope for the r24
repair. The retained grid rows F10 (`shallow repository`), F11 (`rewrites history`), F15
(`object format`), F21 (`not a repository top level`) pin the first four by **reason string**
(`tests/report-audit/repo-state-grid.py:695–708`); changing their wording breaks those rows.

**H5 — the open range `--rounds 10-` is not a stable parity target.**
Today `10-` == `10-23` (no committed `.ufo/reports/round-24/kama.md` in the fleet). When the fleet
lands the round-24 report, `10-` becomes `10-24` and the open-range output changes for reasons
unrelated to the candidate. Use the explicit range `10-23` for parity.

**H6 — the lane tip moves; the historical commit set must not.**
`resolve_branch` (489–499) pins `refs/heads/<branch>` once. r24 work adds lane commits; a commit
whose subject starts `round-10:` … `round-23:` by author `kama-shokunin` would change
`round_commits`, `required` and `post_report` for that round and break parity. The commits already
on `master` are safe: `d1b9d956` is `round-24: …`. Acceptance: after the r24 work, re-run the
parity harness; if a historical count moved, the cause is a lane commit, not the auditor.

**H7 — the JSON's absolute fleet path and the errata line numbers.**
The JSON embeds the fleet report path and the `corrected_by` line numbers of the ledger rows.
Byte-identity therefore requires the same fleet path and the same ledger blob (Section 4.2).
Appending to the ledger (allowed, append-only) changes `errata_rows` in the summary and breaks the
digest — recompute the target after any ledger append, or measure parity with a pinned ledger copy
(`--errata PATH`) — but note that `--errata PATH` changes the *inputs*, not the code path; the
committed-blob path must still be measured once.

**H8 — `--no-errata` parity is a separate measurement.**
`--no-errata` (base blob 374–376) drops the ledger entirely: the 9 defects become uncorrected and
the exit becomes 1. Both variants must be byte-identical between the arms; the r23 harness already
runs both.

---

## 8. Promisor rows of the retained r23 grid — policy decisions for L1 (not decided here)

The preregistration allows "explicitly documented policy-row expectation changes and non-promisor
no-harm". The four promisor-related rows of `tests/report-audit/repo-state-grid.py` are:

| row | kind | fixture | r23 expectation | what r24 does to it |
|---|---|---|---|---|
| `F23-promisor-pack-without-config` (case table line 670, builder `f_promisor_pack` 195–212) | contract | lane = blobless clone with the promisor config removed but the `.promisor` pack kept; the fleet report cites the **missing blob** | exit **2**, reason pinned to `"promisor pack"` (REASONS line 704) | The metadata alone must no longer refuse (preregistration: "metadata-only declarations do not establish incompleteness"), but the cited blob is genuinely absent ⇒ the honest outcome is still exit 2, with a **different reason** (unavailable evidence). Either way the REASONS pin must be rewritten. |
| `F27-filter-only-promisor-remote` (case table 674, builder `f_filter_promisor` 482–496) | fault | lane has `remote.origin.partialclonefilter=blob:none` + `core.sshCommand` marker; the report cites a fabricated sha | exit **1**, kinds `[landed-unresolved, unresolved-full-hash]` | **Policy decision.** If a filter-only remote counts as "promisor-backed", the fabricated citation is *unknown*, not absent ⇒ expectation becomes exit 2 (the transport still must not run). If it does not count, the row stays exit 1. The r23 SKILL text (Round-23 section) says a filter-only remote is "not refused"; the r24 rule "a missing citation in any promisor-backed repository is unknown" pulls the other way. |
| `T01-blobless-partial-clone` (case table 689, builder `t_blobless` 596–605) | **tradeoff** | lane = blobless clone with full promisor config; the fleet is complete; the report cites a lane commit (present) | frozen 0 → current 2 — the *declared trade* r24 is repairing | Under the r24 rule this becomes a **parity row**: the required objects (the cited commit) are present, so the current arm must give the same verdict as the full clone (exit 0). The r23 SKILL "Declared trades (frozen 0 → current 2 on complete repositories): … T01" must be withdrawn in the r24 SKILL section. |
| `C09-promisor-false-config` / `C10-orphan-promisor-marker` (case table 679–680) | control | `remote.origin.promisor=false`; a stray `.promisor` file with no `.pack` | exit 0 / exit 0 | unchanged (metadata alone never refuses). |

**Decision D1 (L1):** is a `remote.*.partialclonefilter`-only remote "promisor-backed"?
Option A (counts): F27 expectation changes 1 → 2, reason pinned to the new unavailable-evidence text.
Option B (does not count): F27 stays 1 with the same kinds. Either way the row must keep proving
that **no transport ran** (`core.sshCommand` marker absent) — that part of the r23 guarantee is
independent of the decision and must not regress.

**Decision D2 (L1):** what happens when a promisor-backed lane clone is missing the
`corpus/SOURCES.md` blob (the normal state of a blobless clone)? The base code path
`load_source_urls` (258–281) calls `git cat-file blob <sha>`; with `--no-lazy-fetch` the blob is
absent ⇒ git fails ⇒ `EvalError` ⇒ exit 2. That is the honest answer (the registry is required
evidence for URL classification), but it must be reached **deliberately**, with the new reason text;
it must not surface as "partial clone", and it must not silently fall back to "legacy, no
registry" (that fallback would turn round 22's `704366d7…` into a false `unresolved-full-hash`).
Note the retained grid's own fixtures have **no** `corpus/SOURCES.md` in the lane, so `None` (legacy)
is correct there and D2 does not apply to T01/F23/C09/C10.

**Limitation L-1 (applies to any D1 choice).** "Absence is not evidence" can only be applied where
the promisor marking is still visible. F23's lane keeps its `.promisor` pack marker although the
promisor *config* was stripped, so the marking survives the config removal. A repository whose
promisor marking was removed **and** whose objects are missing cannot be told apart from a complete
repository by metadata alone; there the absence is the only evidence available and the audit must
treat it as a verdict (absence ⇒ defect), not silently refuse. Any stronger rule would need a
content-completeness check over the objects the audit actually needs
(e.g. `git rev-list --objects --missing=print`) — [INFERENCE], not run here, and not required by the
preregistration.

---

## 9. Acceptance points (concrete, for L1's integration check)

1. **Historical parity (real repos, explicit range).** With the frozen arm = `0df800e:tools/report-landing-audit.py`
   and the current arm = the candidate, both run against the *same* lane path and the *same* fleet
   path `/home/vgpnk/Projects/shokunin`:
   `--rounds 10-23 --json` ⇒ both exit 0 and stdout byte-identical to
   `base-10-23.json` (sha256 `efb3870c…`, path-normalized `d63f902f…`);
   `--rounds 10-23 --no-errata --json` ⇒ both exit 1 and stdout byte-identical to
   `base-10-23-noerrata.json` (`6c543097…`, path-normalized `c1342fb2…`).
   Reuse the r23 harness shape (`.ufo/waves/round-23/falsify/out/CritNoHarmRecipe/parity-commands.json`).
2. **Filed-evidence continuity.** The per-round dicts for rounds 10–22 of the candidate's
   `10-23 --json` equal the filed `.ufo/waves/round-23/final/audit-historical-ledger.stdout`
   per-round dicts (today's base arm satisfies this exactly; the candidate must too).
3. **Summary invariants for 10–23:** `reports=14`, `required_commits=59`, `defects=9`,
   `corrected=9`, `uncorrected=0`, `errata_rows=9`, `errata_unmatched=0`, `errata_invalid=0`,
   `post_report_commits=5`, `status=clean`, exit 0.
4. **Absence semantics (A1/A2):** the candidate's `10-23` run contains exactly one
   `unresolved-full-hash` defect (round 20, token `0957ce619789d13d894ef21bc863486bcb35b56c`,
   `corrected_by [3]`) and **no** defect or refusal for round 22's `704366d7…`.
5. **Promisor parity (synthetic, offline):** for a locally constructed complete clone pair
   (full clone vs promisor-marked clone with identical content), the candidate's substantive
   findings (defect kinds, tokens, exit) are identical, and the promisor-marked arm is **not** exit 2.
6. **Unavailable evidence:** a promisor-marked clone that genuinely lacks a required object ⇒
   exit 2 with the new reason (never exit 0/1), and the transport is never invoked (the
   `core.sshCommand` marker stays absent).
7. **No-harm on the retained r23 grid:** every non-promisor row of
   `tests/report-audit/repo-state-grid.py` keeps its expectation and its reason pin; the
   promisor rows change only as recorded in Section 8, with the change documented in the r24
   SKILL section.
8. **Isolation preserved:** `--no-lazy-fetch`, `--no-replace-objects`, `log.showSignature=false`,
   `log.follow=false`, `log.showRoot=true`, `log.mailmap=false`, strict UTF-8 decode and the 20 s
   per-call timeout stay in `GIT_ISOLATION` (base blob 93–97) and in `git()` (111–137).

---

## 10. Not verified / residual risk

- I did **not** run the auditor `--selftest`, `tests/report-audit/repo-state-grid.py`,
  `tests/report-audit/isolation-mutants.py`, or any mutant/fault harness: out of scope for this
  lane and prohibited as a full-suite run. All grid expectations quoted above are read from the
  committed grid source and its case table, not re-measured.
- The r24 candidate does not exist yet; every "the candidate must …" statement is a prediction
  from the base code, not an observation.
- The "40 of 56 killed FIFO-process identities" erratum is not re-derivable from the committed r23
  evidence (Section 3.1); only the "69 durable lane reports" half was re-derived.
- Git versions other than 2.56.0 were not exercised; `--no-lazy-fetch` requires git ≥ 2.45
  (unchanged by the r24 repair, but a floor that stays documented).
- The lane working tree is dirty with `.ufo/waves/round-24/build/` (untracked); the lane `master`
  moved to `d1b9d956` during the wave. The parity targets in Section 5 were measured with the base
  tool at that tip; re-measure after the r24 work lands (the three parity-critical blobs are
  unchanged, so the targets should hold).
- The fleet repository is a moving target (`HEAD be5a23eb…` at measurement time); the 14 report
  blobs and add-events listed in Section 2 are the values that pin the cutoffs.
- Non-UTF-8 locale behaviour, `--report N=PATH` draft mode and `landed-section-missing` rows were
  not exercised here; they are unaffected by the promisor rule but were not re-measured.

---

## 11. Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/advice/RevHistory.md` — this report.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/RevHistory/parity-manifest.json` — the exact committed inputs (frozen auditors, lane blobs, per-round fleet blobs + add-events + lane commit tuples + expected verdicts, repo-state facts, token universe, baseline output digests).
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/RevHistory/make-manifest.py` — regenerates the manifest (read-only; `python3 make-manifest.py`).
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/RevHistory/base-10-23.json`, `…/base-10-23.txt`, `…/base-10-23-noerrata.json` — the base arm's outputs (the byte-identity targets).
- Scratch only, not a deliverable: `/fast/scratch/hyaku/kama-r24/RevHistory/lane` (`git clone --no-hardlinks`, observation only).

No production file was edited, no commit, no push, no `.jj` or lane index write, no installs or
updates.
