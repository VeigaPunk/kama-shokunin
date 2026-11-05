# kama round 86 — lesson (advisor draft for L1 integration)

Frozen plan `plans/round-86-claims.md`; frozen counter `.ufo/waves/round-86/count.py`; base
`3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d`; freeze commit
`c07e1f909414aafb2d8de5605a81fd3bd4e3550e`. Three claims: C1 calibration (rendered-cell identity),
C2 operability (mutant → owning arm + summary/failure-line cardinality), C3 freshness (pin-origin
corroboration against live upstream bytes).

Author-side advisor draft. **No claim admission is made here**: the L1 (KamaR86) is the sole
integrator and the only committer; whether C1/C2/C3 verify is settled by the L1's terminal
measurement, not by this draft. This file lives only under
`.ufo/waves/round-86/w1/out/SB01LessonDraft/` and is a proposal for the L1 to adopt, amend or reject.

Measurements below are my own re-runs of the frozen counter at `master`
(`c5a324430fb0ef04dc9d886f997d7cdacc083f7b`) with `TMPDIR` inside my seat scratch; receipts are in
`receipts/` beside this file (`receipts/final.txt`, `receipts/anchor-upstream-recheck.txt`). The L1
was still committing while this seat worked, so every measurement names its exact revision.

**One finding the L1 must see before publishing.** The counter `.ufo/waves/round-86/count.py` is
byte-identical to the freeze commit, but it executes the **worktree** instrument at
`pathlib.Path(repo).resolve() / script` — not the bytes committed at `--rev`. Two of the three
instruments were therefore *edited after the wave scored them*, and the C2 edit is what turns the
M6 survivor into a kill:

- `tools/round86-mutant-owners.py`: freeze `b7ee59ae…` → tip `e09bc83d…`
  (`1bfcd49f`, "implement the frozen C2 reconciliation clauses the classifier skipped").
- `tools/round86-rendered-cells.py`: freeze `e038b2c0…` → tip `5adaa27f…` (`c5d71b7a`, `d80d0896`,
  `7a21aaa1`).
- `tools/round86-pin-origin.py`: unchanged (`6c90e388…`).

The `PREDICATE` sentences are byte-identical in all three, and the round's wave attacks did find real
defects the amendments close (M5 receipt-at-graded-revision; M6 the classifier skipping the ARMS-line
clauses). But at the pinned tip the **frozen** C2 instrument still prints
`DEBT_MUTANT_OWNERS mutants=5 killed=4 escaped=1 invalid=0 arms=34 cardinality=ok owners=4/5` and
exits **1** — M6 escapes — because the L1's debt-tool change at `c5d71b7a` restored the summary's
round-81 shape (no `arms=` field), and the frozen classifier's cardinality clause is conditional on
that field being present. The green `owners=5/5` line exists only under the amended classifier.
The frozen C1 and C3 instruments both still print their target lines at the tip.

This is the round-85 shape of the same mistake: a verdict that depends on the instrument's *current*
bytes rather than the frozen bytes. It is the L1's disposition; this draft records it.

## Gate

Opened 2026-11-04. These are read-only reads of public documents (the CommonMark specification and
the upstream documents the pin rows name); no serving endpoint was sampled and no credential was
read.

### Rows opened or extended this round

| id | URL | access date | located quote (≤25 words) | decision and scope |
|---|---|---|---|---|
| S576 (re-opened; `used-by` extended to this lesson) | https://spec.commonmark.org/0.31.2/#atx-headings | 2026-11-04 | §4.2 ATX headings: “The opening # character may be preceded by up to three spaces of indentation.” | admit; grounds C1's 0–3-space correction-heading exclusion, not a claim of a complete CommonMark parser |
| S578 (new) | https://spec.commonmark.org/0.31.2/#fenced-code-blocks | 2026-11-04 | §4.5 Fenced code blocks: “A fenced code block begins with a code fence, preceded by up to three spaces of indentation.” | admit; grounds fence exclusion — a fenced copy of a cell is code, never the live cell |
| S579 (new) | https://spec.commonmark.org/0.31.2/#indented-code-blocks | 2026-11-04 | §4.4 Indented code blocks: “An indented chunk is a sequence of non-blank lines, each preceded by four or more spaces of indentation.” | admit; grounds the column-0 selection rule — a four-space-indented line is code |

All three quotes were located by reading the fetched page
(`curl -sS https://spec.commonmark.org/0.31.2/` → HTTP 200, 514698 bytes, sha256
`c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d`; receipts
`receipts/final.txt` §8). No row was refused this round. The census reports
`W04 duplicate url spec.commonmark.org/0.31.2 across scopes` for S576/S578/S579 because it compares
URLs without anchors — disclosed, not suppressed; `validate` exits 0.

### Upstream documents re-read live for C3 (already-filed rows)

| filed row | URL | access date | located quote (≤25 words) | corroboration |
|---|---|---|---|---|
| S564 | https://raw.githubusercontent.com/ggml-org/llama.cpp/b11755/tools/server/README.md | 2026-11-04 | line 481: “This endpoint is public (no API key check). `/v1/health` also works.” | upstream 478–490 byte-identical to `corpus/anchors/llamacpp-b11755-health.txt`; header digest matches |
| S573 | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12111/tools/server/README.md | 2026-11-04 | line 482: “This endpoint is public (no API key check). `/v1/health` also works.” | upstream 479–491 byte-identical to `corpus/anchors/llamacpp-b12111-health.txt` |
| S572 | https://raw.githubusercontent.com/ggml-org/llama.cpp/b7200/tools/server/README.md | 2026-11-04 | line 406: “This endpoint is public (no API key check). `/v1/health` also works.” | upstream 403–415 byte-identical to `corpus/anchors/llamacpp-b7200-health.txt` |
| S553, S555 | https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/tools/server/README.md | 2026-11-04 | line 2199: “Listing all models in cache. The model metadata will also include a field to indicate the status of the model:” | upstream 2197–2204 byte-identical to `corpus/anchors/llamacpp-39febd2a-router.txt` |
| — (no dedicated row) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12111/tools/server/README.md (router range) | 2026-11-04 | line 2203: “Listing all models in cache. The model metadata will also include a field to indicate the status of the model:” | upstream 2199–2206 byte-identical to `corpus/anchors/llamacpp-b12111-router.txt`; the newest-side `/models` listing has no SOURCES row of its own — see the open item below |
| S568 | https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/basic_usage/native_api.mdx | 2026-11-04 | line 109: “- `/health`: Check the health of the server.” | upstream 108–111 byte-identical to `corpus/anchors/sglang-v0.5.22-health.txt` |
| S567, S574 | https://raw.githubusercontent.com/sgl-project/sglang/v0.5.23/docs/docs/basic_usage/native_api.mdx | 2026-11-04 | line 109: “- `/health`: Check the health of the server.” | upstream 108–113 byte-identical to `corpus/anchors/sglang-v0.5.23-health.txt` |
| S570 | https://raw.githubusercontent.com/vllm-project/vllm/v0.32.0/docs/design/prefix_caching.md | 2026-11-04 | line 3: “Prefix caching kv-cache blocks is a popular optimization in LLM inference to avoid redundant prompt computations.” | upstream 1–6 byte-identical to `corpus/anchors/vllm-v0.32.0-prefix-caching.txt` |
| S569, S575 | https://raw.githubusercontent.com/vllm-project/vllm/v0.33.0/docs/design/prefix_caching.md | 2026-11-04 | line 3: “Prefix caching kv-cache blocks is a popular optimization in LLM inference to avoid redundant prompt computations.” | upstream 1–6 byte-identical to `corpus/anchors/vllm-v0.33.0-prefix-caching.txt` |

Nine committed anchor extracts across eight distinct upstream documents; all nine stored bodies equal
their declared upstream range byte for byte and every stored body's sha256 equals its header digest
(`receipts/anchor-upstream-recheck.txt`). Every fetch returned HTTP 200; no source was unreachable.

## Mistakes

One class is mined this round.

| class | evidence | captured-by | fix |
|---|---|---|---|
| `rendered-identity false green` — a raw-line selector read a **fenced copy** as the live cell, so a stale live authority paragraph and a stale live calibration row still graded green | `.ufo/waves/round-85/w1/out/SN01Scope/receipts/fenced-shadow.md` (a fenced `markdown` block carrying both correct-looking cells while the live authority line still read “under terminal measurement” and the live calibration row still named round 83) and `.ufo/waves/round-85/w1/out/CR01Cheats/receipts.json` (`fake_fenced_cells` exit 0, `AUTHORITY_CELLS facts=2 mismatches=0 gate=1 closure=1`, and `fake_html_comment_cells` exit 0 with the same green line, both against unchanged stale live cells). The frozen round-85 selector was a first-match regex over raw lines (`.ufo/waves/round-85/count.py` lines 19–21 at `948dec78`), so it had no notion of what a renderer shows | `corpus/QUALITY.md` KQ138 (line 663): “A claimed live-cell selector rejects the retained round85 fenced-example and HTML-comment shadow specimens, and binds revision/command/receipt into the assertion rather than independent token presence.” | `tools/round86-rendered-cells.py` selects cells only from **rendered** text: HTML comment blocks, backtick and tilde fences, `round-N correction` blocks and non-column-0 lines are stripped before the first `**Current authority (round N):**` line and the first `| calibration |` row inside the first `## Axes` section are chosen. Its `--selftest` arms `fenced-shadow`, `comment-shadow`, `tilde-fence-shadow`, `indent-shadow` and `unclosed-fence-fails-closed` each turn the retained shadow red (`receipts/c1.out` lineage: `.ufo/waves/round-86/measured/before/c1-selftest.out`, 11/11) |

**Why the closure pointer resolves by round number, and not by date.** The closure fact is about
*which* closure is newest, and round number is the invariant the row records. The date ordering is
unavailable for this population: `python3 tools/round69-newest-closure-counter.py --repo .` (no
`--since-round`) prints `COULD_NOT_EVALUATE closure round-10-verifier-spotcheck.md carries no
parsable ISO date (no date: field, none in a heading, none in the body)` and exits **2** — the
undated historical closure makes date ordering fail closed rather than pick a winner. The round-86
counter therefore resolves the newest closure by **highest round number** and reads that closure's
disposition word from its body. The round-69 instrument is left unchanged; its `--since-round 63`
scope remains the historical workaround. This note belongs to the same mined class: it records why
the repaired closure cell is graded by a rule that can actually be evaluated.

## Append-only provenance erratum (R84V5)

The round-84 frozen plan (`plans/round-84-claims.md` line 95) cites a red control at
`.ufo/waves/round-84/measured/before/red-selfrecord.out`. **That path does not exist** — `git show
3ff23da3:.ufo/waves/round-84/measured/before/red-selfrecord.out` exits 128 and the path is absent
from the tree. The retained red control is
`.ufo/waves/round-84/measured/after/c2-red.out`, whose header records revision
`3e93febb0f40955b08dc80367e8ef658eaccdfd6` and command
`python3 tools/round84-selfrecord-round83.py --repo . --no-corrections`, printing
`SELFRECORD_R83 claims=8 mismatches=6 corrected=0 unbacked=6` and `EXIT=1`. It is a `--no-corrections`
red demonstration, **not** the promised run on an uncorrected tree. This erratum is appended; the
frozen plan bytes and the filed round-84 receipts are never rewritten. Round 84's C2 numeric
predicate remains verified as filed.

## SCORECARD and LOG row text for C1, C2, C3

Exact verdict lines, taken verbatim from the frozen plan and the receipts, with the before/after
pair the plan froze. Line forms to carry into the records:

| claim | before / no-work control (plan) | after (measured at `master` = `c5a32443…`) | exit |
|---|---|---|---|
| C1 calibration | `RENDERED_CELLS facts=3 mismatches=3 gate=0 closure=0 disposition=0 newest_gate=85 newest_closure=85` | `RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=85 newest_closure=85` | 1 → 0 |
| C2 operability | `DEBT_MUTANT_OWNERS mutants=5 killed=3 escaped=2 invalid=0 arms=unknown cardinality=ok owners=3/5` | `DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5` | 1 → 0 |
| C3 freshness | `could-not-evaluate: no tools/round86-pin-origin.py at 3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d` | `PIN_ORIGIN rows=5 verified=5 mismatch=0 unreachable=0 bad=0` | 2 → 0 |

The C2 after-line is produced by the **amended** classifier. Under the **frozen** C2 instrument the
same tree prints `mutants=5 killed=4 escaped=1 invalid=0 arms=34 cardinality=ok owners=4/5`, exit 1.
Any row text that states the C2 after-line as the round's verdict must say which instrument produced
it, or it repeats round 85's fault in a new place.

Proposed SCORECARD row text (one row per claim; the L1 owns the final wording):

> C1 calibration — frozen `count.py c1 --repo . --rev REV --work <work>`: `RENDERED_CELLS facts=3
> mismatches=3 gate=0 closure=0 disposition=0 newest_gate=85 newest_closure=85` exit1 →
> `RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=85
> newest_closure=85` exit0; selftest 11/0 with the round-85 fenced/comment shadow arms red
> (`.ufo/waves/round-86/measured/before/c1-selftest.out`). The live cells are graded by rendered
> identity: fence, HTML comment, indented-code and `round-N correction` copies are not cells.

> C2 operability — frozen `count.py c2 --repo . --rev REV --work <work>`: `DEBT_MUTANT_OWNERS
> mutants=5 killed=3 escaped=2 invalid=0 arms=unknown cardinality=ok owners=3/5` exit1 →
> `DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5`
> exit0 under the round-86 amended classifier; the frozen `c07e1f90` classifier on the same tree
> prints `killed=4 escaped=1 … owners=4/5` exit1 (M6 escapes), so the after-line is
> instrument-dependent and the record must say so. M5 kills on `arm-count`
> (`arms=33 != expected=34`), M6 on `summary-cardinality` (`summary pass+fail=0 != arms=34`);
> pristine `APPEND_DEBT_SELFTEST pass=34 fail=0` (the round-81 summary shape; `arms=34` rides the
> separate `APPEND_DEBT_SELFTEST_ARMS` line).

> C3 freshness — frozen `count.py c3 --repo . --rev REV --work <work> --rows
> registry/pin-recheck-rows.tsv`: `could-not-evaluate: no tools/round86-pin-origin.py at
> 3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d` exit2 → `PIN_ORIGIN rows=5 verified=5 mismatch=0
> unreachable=0 bad=0` exit0; selftest 7/0 with `fabricated-hash-consistent` graded `mismatch` and
> `digest-lie` graded `bad`. Nine committed anchor extracts equal their declared upstream ranges
> byte for byte.

Proposed LOG.md round-86 row text: keep the plan's frozen before/after pairs and receipts as the
record; the §Round 86 entry should name the frozen predicate line of each claim, the before
receipt under `.ufo/waves/round-86/measured/before/`, the after receipt under
`.ufo/waves/round-86/measured/after/`, the measured revision, the exact verdict line, and — for
C2 — the instrument that produced that line. It should not claim a score move, since the plan claims
none.

**Receipt-binding caveat the L1 must resolve.** The six round-86 after-receipts carry **no `# rev=`
header** (round-85's do), so none of them names the revision it measured. Re-running the counter at
the pinned tip reproduces `after/c1.out` and `after/c3.out` byte-for-byte, but **not**
`after/c2.out`: the committed receipt's last line is
`DEBT_MUTANT_OWNERS_PRISTINE APPEND_DEBT_SELFTEST pass=34 fail=0 arms=34`, while the tip's debt tool
prints `pass=34 fail=0` (the `arms=` field was removed at `c5d71b7a`). The committed C2 receipt
reproduces only at revision `67eddac8`, the tree before that change — it is a receipt of a tree the
round has since left behind.

## Open, not repaired

- **The C2 after-verdict is instrument-dependent, and the record does not say so.** The counter
  `.ufo/waves/round-86/count.py` is byte-identical to the freeze commit, but it runs the *worktree*
  instrument (`pathlib.Path(repo).resolve() / script`), so an edit to `tools/round86-mutant-owners.py`
  changes what the frozen command measures. The L1 edited it at `1bfcd49f`, after the wave had
  scored it. At the pinned tip the frozen `c07e1f90` classifier still lets M6 escape
  (`killed=4 escaped=1 … owners=4/5`, exit 1) because `c5d71b7a` restored the summary's round-81
  shape and the frozen cardinality clause is conditional on the summary carrying `arms=`. The
  amendments themselves close real defects the wave found (M5, M6 in the committed lesson), and the
  `PREDICATE` sentences are byte-identical — but the round's C2 green is not re-derivable from the
  frozen bytes, and neither the tip `LOG.md` nor the tip lesson discloses that. **This is the same
  class the round-85 closure rejected**: a verdict that holds only because the instrument changed.
- **The committed C2 after-receipt does not re-derive at the tip.** `after/c2.out` reproduces only
  at `67eddac8`; at the tip the debt tool prints `APPEND_DEBT_SELFTEST pass=34 fail=0` while the
  receipt records `pass=34 fail=0 arms=34`. None of the six round-86 after-receipts carries a
  `# rev=` header, so no receipt names the revision it measured. `after/c1.out` and `after/c3.out`
  do re-derive byte-for-byte at the tip.
- The closure cell's disposition word comes from the closure body, and the newest-side `/models`
  listing corroborated by C3 (`corpus/anchors/llamacpp-b12111-router.txt`, upstream 2199–2206) has
  **no SOURCES row of its own**; the round opens no row for it because the round's source budget is
  the CommonMark specification. The L1 may open one next round or leave the register as it is.
- C3 proves documentary origin at fetch time. It does not prove that a row's *verdict* word
  (`holds` / `moved` / `drifted`) is the right one for a semantic change; that stays the declarer's
  judgment, and the counter only re-derives byte equality.
- `newest_gate` is derived from committed receipts under `.ufo/waves/round-*/measured/*.out`. When
  the round-86 terminal gate receipt is committed, `newest_gate` becomes 86 and the banner that
  currently names round 85's `PRE_REPORT round=85 arms=13 failed=1 uncommitted=0` becomes stale by
  construction. The C1 measurement must be re-run **after** the round-86 gate receipt is committed,
  or the banner and the receipt must land together. (At `master` today no committed round-86
  receipt carries a `PRE_REPORT` line, so `newest_gate=85` and the banner still agree.)
- R84V1 (a frozen auxiliary disclosure instruction missed) stays an honest miss: no event-loss
  disclosure is manufactured for a source event that was `ungraded`, not restored.

## Divergence from the lesson the L1 already committed

`corpus/lessons/round-86.md` is committed (first at `67eddac8…`, extended by `c5d71b7a` and
`1bfcd49f`) and now mines **six** classes: `M1` rendered-identity, `M2` calibration/tooling (the
round-69 date-ordering exit 2), `M3` fixture ordering, `M4` selftest-summary consumer coupling,
`M5` gate-fact receipt binding, `M6` C2 classifier clause coverage. This advisor draft folds the
round-69 exit-2 finding into the single mined class as the stated reason the closure pointer resolves
by round number, because that exit 2 is a fact about the *population* the closure fact grades rather
than a second independent defect. The L1 keeps the disposition; the difference is a drafting
granularity difference, not a disagreement about any measurement.

The committed lesson also does not carry the two findings above (the instrument-dependent C2
after-verdict and the non-re-deriving C2 receipt). This draft adds them.

## Frontier

CommonMark is a narrowly scoped instrument-input specification, not a new generic Markdown
province; the debt audit and the serving-lane self-assessment stay lane instruments. Model quality,
generic orchestration, research method, consumer/service restoration and credentials remain
sibling- or operator-owned. No live serving endpoint was sampled. Registry rows alone earn no
expansion credit. `Assimilation: none` — no staged theme in `considerthese/` implements these three
instrument repairs.

## Tools

No tool was installed or updated; the seat used the host's `python3` 3.14.8, `git` 2.56.0 and
`curl` 8.23.0. No pacman transaction, no service restart, no configuration or credential read.
