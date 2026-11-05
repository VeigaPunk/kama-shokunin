# SB01LessonDraft — round-86 lesson draft (kama r86 w1)

Seat role: scribe, axis **calibration**. Author-side advisor only: **no claim admission**. The L1
(`KamaR86`) owns integration and is the only committer.

**Deliverable:** the drafted round-86 lesson and its receipts are at
`.ufo/waves/round-86/w1/out/SB01LessonDraft/`

- `round-86-lesson-draft.md` — the lesson draft (`## Gate`, `## Mistakes`, the R84V5 append-only
  provenance erratum, and the SCORECARD/LOG row text for C1, C2, C3)
- `receipts/final.txt` — every command, its true exit code and the revision it measured
- `receipts/c1.out` / `c2.out` / `c3.out` (+ empty `.err`) — the three frozen-counter outputs
- `receipts/anchor-upstream-recheck.txt` — independent byte-identity recheck of the nine committed
  anchor extracts against live upstream bytes

**Pinned measured revision (`master`): `c5a324430fb0ef04dc9d886f997d7cdacc083f7b`.** The L1 was
still committing while this seat worked, so every measurement below names its exact revision.

## What the draft contains

1. **`## Gate`** — a row for every source row the round cites, each with URL, access date
   2026-11-04 and a located ≤25-word quote: S576 (CommonMark §4.2 ATX headings, re-opened),
   S578 (§4.5 fenced code blocks, new), S579 (§4.4 indented code blocks, new), plus a second table
   for the eight upstream documents C3 corroborates live (S564, S573, S572, S553/S555, S568,
   S567/S574, S570, S569/S575), each with its located line and quote. The `W04 duplicate url
   spec.commonmark.org/0.31.2 across scopes` census warning is disclosed, not suppressed.
2. **`## Mistakes`** — exactly one mined class, `rendered-identity false green`: the round-85
   raw-line selector read a **fenced copy** as the live cell, so unchanged stale live cells still
   graded green (`.ufo/waves/round-85/w1/out/SN01Scope/receipts/fenced-shadow.md`,
   `.ufo/waves/round-85/w1/out/CR01Cheats/receipts.json` — `fake_fenced_cells` and
   `fake_html_comment_cells` both exit 0 with `mismatches=0 gate=1 closure=1`); captured-by
   `corpus/QUALITY.md` KQ138 (line 663); fixed by `tools/round86-rendered-cells.py` selecting only
   rendered cells, with the shadow arms red in the frozen selftest. The round-69 date-ordering
   **exit 2** is recorded as the reason the closure pointer resolves by **round number**:
   `python3 tools/round69-newest-closure-counter.py --repo .` prints
   `COULD_NOT_EVALUATE closure round-10-verifier-spotcheck.md carries no parsable ISO date` and
   exits 2, so date ordering cannot evaluate the population.
3. **R84V5 append-only provenance erratum** — `plans/round-84-claims.md` line 95 points at an
   absent `measured/before/red-selfrecord.out` (`git show` exits 128); the retained red control is
   `measured/after/c2-red.out` (rev `3e93febb…`, `--no-corrections`,
   `mismatches=6 corrected=0 unbacked=6`, exit 1), a red demonstration and not the promised
   uncorrected-tree run. Frozen plan bytes and filed receipts are not rewritten.
4. **SCORECARD / LOG row text for C1, C2, C3** carrying the plan's exact verdict lines and their
   before/after pairs.

## Measurements (my own re-runs, at `c5a32443…`)

| command | exit | verdict line |
|---|---:|---|
| `python3 .ufo/waves/round-86/count.py c1 --repo . --rev c5a32443… --work <scratch>/c1` | 0 | `RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=85 newest_closure=85` |
| `python3 .ufo/waves/round-86/count.py c2 --repo . --rev c5a32443… --work <scratch>/c2` | 0 | `DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5` |
| `python3 .ufo/waves/round-86/count.py c3 --repo . --rev c5a32443… --work <scratch>/c3` | 0 | `PIN_ORIGIN rows=5 verified=5 mismatch=0 unreachable=0 bad=0` |
| `python3 tools/round69-newest-closure-counter.py --repo .` | 2 | `COULD_NOT_EVALUATE closure round-10-verifier-spotcheck.md carries no parsable ISO date …` |
| `curl -sS https://spec.commonmark.org/0.31.2/` | 0 | HTTP 200, 514698 bytes, sha256 `c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d` |
| 9 read-only GETs of the anchor URLs (all HTTP 200) | 0 | all nine stored bodies equal their declared upstream ranges byte for byte; every stored body's sha256 equals its header digest |
| `bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` | 0 | `kama ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md` (W01/W04 warnings unchanged) |

## Findings for the L1 — two of them are material

### 1. The C2 after-verdict is instrument-dependent, and the record does not say so

`.ufo/waves/round-86/count.py` is byte-identical to the freeze commit (`75b91e70…`), **but it runs
the worktree instrument** — `pathlib.Path(args.repo).resolve() / script` — not the bytes committed at
`--rev`. So an edit to `tools/round86-mutant-owners.py` changes what the frozen command measures.

The L1 edited two of the three instruments **after the wave scored them**:

| instrument | freeze `c07e1f90` | tip | changed at |
|---|---|---|---|
| `tools/round86-mutant-owners.py` | `b7ee59ae…` | `e09bc83d…` | `1bfcd49f` |
| `tools/round86-rendered-cells.py` | `e038b2c0…` | `5adaa27f…` | `c5d71b7a`, `d80d0896`, `7a21aaa1` |
| `tools/round86-pin-origin.py` | `6c90e388…` | `6c90e388…` | unchanged |

The `PREDICATE` sentences are byte-identical in all three, and the amendments close real defects the
wave found (M5 receipt-at-graded-revision; M6 the classifier skipping the ARMS-line clauses). But:

- At the pinned tip, the **frozen** C2 instrument still prints
  `DEBT_MUTANT_OWNERS mutants=5 killed=4 escaped=1 invalid=0 arms=34 cardinality=ok owners=4/5`
  and exits **1** — M6 escapes. The cause is `c5d71b7a`, which restored the debt selftest's
  round-81 summary shape (no `arms=` field) to keep frozen gate arm 11 green; the frozen
  classifier's cardinality clause is conditional on that field being present.
- The green `owners=5/5` line therefore exists only under the amended classifier.
- The frozen C1 and C3 instruments both still print their target lines at the tip
  (`mismatches=0 gate=1 closure=1 disposition=1` and `rows=5 verified=5 mismatch=0 unreachable=0
  bad=0`), and the frozen C1 selftest keeps all four shadow arms red (11/0).

Neither the tip `LOG.md` nor the tip lesson discloses the divergence. This is the round-85 shape of
the same mistake — a verdict that holds because the instrument changed. The L1's disposition; my
draft records it.

### 2. The committed C2 after-receipt does not re-derive at the tip

- None of the six round-86 after-receipts carries a `# rev=` header (round-85's do), so no receipt
  names the revision it measured.
- Re-running the counter at the pinned tip reproduces `after/c1.out` and `after/c3.out`
  byte-for-byte, but **not** `after/c2.out`: the committed receipt's last line is
  `DEBT_MUTANT_OWNERS_PRISTINE APPEND_DEBT_SELFTEST pass=34 fail=0 arms=34`, while the tip's debt
  tool prints `pass=34 fail=0`.
- The committed `after/c2.out` reproduces **only at revision `67eddac8`** (with the instrument as it
  then stood) — it is a receipt of a tree the round has since left behind. It does not reproduce at
  its own commit `c5d71b7a` either.

`tools/round72-receipt-tip-binding.py --repo . --round 86 --tip master` exits 2 on
`SCORECARD.md:5262` (`RECEIPT_TIP_BINDING_UNREADABLE cited path is not a receipt file (.py):
.ufo/waves/round-86/count.py`), so the lane's own receipt-binding instrument does not currently
grade this round either.

### 3. Minor findings

- The newest-side `/models` listing corroborated by C3
  (`corpus/anchors/llamacpp-b12111-router.txt`, upstream 2199–2206) has **no SOURCES row of its
  own**. This round's source budget is the CommonMark specification, so no row was opened; the L1
  may open one next round.
- `newest_gate` is derived from committed receipts under `.ufo/waves/round-*/measured/*.out`. When a
  round-86 terminal gate receipt is committed, `newest_gate` becomes 86 and the banner naming round
  85's `PRE_REPORT round=85 arms=13 failed=1 uncommitted=0` goes stale by construction. At the pinned
  tip no committed round-86 receipt carries a `PRE_REPORT` line, so `newest_gate=85` and the banner
  still agree — but C1 must be re-measured **after** that receipt lands.
- The committed lesson `corpus/lessons/round-86.md` now mines six classes (M1–M6); this advisor
  draft folds the round-69 exit-2 finding into the single mined class, since that exit 2 is a fact
  about the population the closure fact grades rather than a second independent defect. Granularity
  difference only, no measurement disagreement.

## Boundaries observed

No production file was edited; no commit, push, tag or mutating git command was run against the
lane; the lane working tree shows only the L1's own commits and other seats' untracked wave
outputs. No fixture repository was needed (no commits required); the seat scratch
`/fast/scratch/hyaku/kama-r86/SB01LessonDraft/` held only the fetched documents and the counter work
dirs and was removed after the receipts were copied into my out dir. No service was started, no
configuration or credential file was read, and no live serving endpoint was sampled — the only
network access was read-only GET on the public specification and the eight upstream documents the
pin rows name. No tool was installed or updated: the seat used the host's `python3` 3.14.8, `git`
2.56.0 and `curl` 8.23.0; no pacman transaction was made.
