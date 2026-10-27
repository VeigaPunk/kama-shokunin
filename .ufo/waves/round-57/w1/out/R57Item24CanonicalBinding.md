# R57Item24CanonicalBinding — content-bound canonical capability-row audit + omission control

Seat: `R57Item24CanonicalBinding` (scribe, leaf; item `round57/CanonicalBinding/24`), wave
`kama-r57-w1`, kama round 57. Axes: calibration + operability. Milestone: 64-seat mixed
counter repair and falsification; L1 is planner. No subagents dispatched (leaf bound).

Assignment, verbatim: *"Prototype independent content-bound canonical capability-row audit and
omission control, scratch only; no shared writes. Work only with
/home/vgpnk/Projects/shokunin/kama-shokunin; no shared writes. Return evidence at the Report
trailer path. Distinct case 45: test the assigned case independently and report a separate
evidence file."*

## Verdict in one paragraph

Two independent instruments were written, both scratch-only, neither importing a lane counter.
On the canonical capability table they agree row for row: **11 rows, generation 49, 11/11
evidence pointers resolve, 11/11 rows content-bound, mirror names 11, first-working-round
vector 11, no cross-generation loss, no witness loss.** The prototype nevertheless returns
`met=False` on the lane at the frozen base and at every later tip **for exactly one reason**,
and the second implementation is blind to it: the head `## Capabilities` mirror's
`live-receipt-replay` row **does not carry the canonical row's fourth evidence pointer**
(`.ufo/waves/round-49/measured/c1-build.out`), although the mirror prose calls itself "Mirror of
the round-49 canonical capability list". Restoring that one pointer in a mutant clears the
verdict to `met=True` with zero mismatches (`m7-mirror-repaired`, exit 0). The frozen do-nothing
instrument reports `mismatches=0 maxN=46 met=True` (exit 0) on a tree whose entire round-49
canonical block is deleted; the prototype rejects that same tree (`generation` 48 ≠ expected 49,
exit 1). So the omission control is non-vacuous, and the incumbent `caps` fact (names only) is
not sufficient.

## 1. Claim conflict recorded verbatim (not resolved)

The assignment carries:

> "C1 calibration—repair the stale canonical capability row count, counter currently reports
> maxN=56 instead of expected 46; before output mismatch=1. C2 operability—distinct, actual
> canonical-row execution/content binding; a no-op currently reports met=True exit 0."

The lane's own pre-data correction (`.ufo/waves/round-57/controls/freeze-amendment.txt`) says:

> "C1 is the frozen round56-prereg-check no-op control defect, operability axis ... C2 is the
> tools/round42-selfdesc-reconcile.py stale calibration count, calibration axis ... C1 and C2
> are distinct axes, each measured independently."

and the landed SCORECARD §Round 57 says `C1 — bind declared roster to actual battery call sites
| operability 8→8` and `C2 — re-anchor the SCORECARD verifier-spotcheck count | calibration
7→7`. The two orderings are opposite. Both are reported here; neither is resolved. Per the
seat instruction, the `MISSION.md`-vs-config axis-authority conflict is likewise left
unresolved (`SCORECARD.md:6` still records `MISSION.md:29` as an open L0 question).

## 2. What was built (scratch only)

| file | sha256 | what it is |
|---|---|---|
| `canonical_rows_audit.py` | `56efd92e3393f73a86ede9cfb03616460d08483c5aad25fd9f208ea9d4586b1b` | the prototype: 12 content-bound legs over the newest canonical table, its head mirror, the Saturation vector, the canonical lineage, and an optional witness |
| `case45_independent.py` | `2f96b65f81448d351e7cb7e11a5dd8cc91292109b8a9645ded993166f7fc74e3` | distinct case 45: a second implementation of the same five readings, different parsing, different path test |
| `build_controls.py` | `b63017b1df3a12e554d6d6142deb89a52d25d3098afacd1ae796cb1b213cebf3` | builds every control tree and writes every receipt |
| `case45.sh` | `ee140e8e9d98eac5a1be11fc869c358f7471545da630c4b87fb8aa3198ffae0f` | the assigned-case verdict, every command re-derived |
| `s515.sh` | `2da38ea0a4963a3287be4e34578c998417b4ad9d922b8b491823055d34f23a28` | the non-author S515 spot-check |

No lane source file was written. Every mutant tree is `SCORECARD.md` plus **symlinks** to the
lane's `tools/`, `registry/`, `corpus/`, `.ufo/`; the lane is read-only throughout. Tooling:
`python3` (stdlib), `git`, `curl` — **no install or upgrade was performed**.

## 3. The legs, as measured on the lane

`python3 canonical_rows_audit.py --repo <lane> --tip HEAD`

```
rows=11 stated=11 gen=49 expected=49 fail_present=0 fail_shape=0 fail_generation=0
fail_count=0 fail_mirror_names=0 fail_mirror_cells=1 fail_firsts=0 fail_evidence=0
evidence=11/11 content=11/11 fail_missing=0 fail_monotonic=0 fail_witness=0 mismatches=1 met=False
detail: mirror_cells: live-receipt-replay: head mirror evidence cell is not the canonical cell
        (canonical-only pointers ['.ufo/waves/round-49/measured/c1-build.out']; mirror-only pointers [])
```

Terms are re-derived, never typed: `gen` is the greatest `canonical list as of round N` marker;
`expected` is the greatest round the SCORECARD's own references name (`Mirror of the round-N
canonical capability list`, `the round-N canonical capability list stays canonical`); `stated`
is the cardinal in the prose between the marker and the table (`Eleven capabilities`); `firsts`
is the `capability first-working rounds <list>` vector in `## Saturation`; `evidence` and
`content` are per row (every path resolves; a declared literal's every part, or a six-word run
of the cell, occurs in the evidence text); `missing`/`monotonic`/`witness` are the omission legs.

## 4. Control matrix (all receipts in `./R57Item24CanonicalBinding/`, exits observed)

| # | control | what it varies | summary | exit |
|---|---|---|---|---|
| 1 | `lane-base` | frozen base `b89bdab2` | `mismatches=1 met=False`, the one failure `mirror_cells` | 1 |
| 2 | `lane-head` | tip `8a7f1976` + witness `b89bdab2` | `mismatches=1 met=False`, `fail_witness=0` | 1 |
| 3 | `fixture-no-canonical` | frozen `controls/no-canonical` as committed | `gen=48 expected=49`, `mirror_cells=3`, `evidence=0/11`, `mismatches=15` | 1 |
| 4 | `fixture-canonical-noop` | frozen `controls/canonical-noop` as committed | `mirror_cells=1`, `evidence=1/11`, `mismatches=11` | 1 |
| 5 | `omission-isolated` | the frozen `no-canonical` bytes **over a live tree** | `gen=48 expected=49`, `mirror_cells=3`, `mismatches=4` | 1 |
| 6 | `omission-noop-frozen` | `git show 89dc4f52:.ufo/waves/round-57/controls/noop-c2.out` | `summary=mismatches=0 maxN=46 met=True` | 0 |
| 7 | `omission-noop-repro` | the same instrument text, re-run | `summary=mismatches=0 maxN=46 met=True` | 0 |
| 8 | `canonical-noop-isolated` | the stale-calibration fixture over a live tree | `mismatches=1` (the same `mirror_cells`; the stale count is invisible to this surface, by design) | 1 |
| 9 | `m1-drop-row` | one newest canonical row deleted, everything else untouched | `count=1 mirror_names=1 firsts=1 missing=1 monotonic=1`, `mismatches=5` | 1 |
| 10 | `g1-row-drop` | that row dropped wherever the v5 wording carries it, cardinal and vector corrected | `missing=1 monotonic=1`, `mismatches=2` (older generations still name it) | 1 |
| 11 | `g2-witness` | the row scrubbed from **every** capability table and every in-file statement | `fail_witness=1`, `mismatches=1` — only the external witness sees it | 1 |
| 12 | `g2-no-witness` | the same tree with no witness | `mismatches=0 met=True` — the declared limit | 0 |
| 13 | `m3-content` | one row's capability cell replaced by vocabulary absent from its evidence | `content=10/11`, `mismatches=2` | 1 |
| 14 | `m4-evidence` | one row's evidence pointer renamed to a file that does not exist | `fail_evidence=1 evidence=10/11`, `mismatches=2` | 1 |
| 15 | `m5-generation` | the marker bumped to round 50, references left at 49 | `gen=50 expected=49`, `mismatches=2` | 1 |
| 16 | `m6-duplicate` | the newest `pin-watch` row duplicated | `rows=12 stated=11 count=1 mirror_names=2 firsts=1`, `mismatches=6` | 1 |
| 17 | `m7-mirror-repaired` | the one divergent pointer added to the head mirror | `mismatches=0 met=True` | 0 |

Receipts 6 and 7 are the operability control pair: the do-nothing instrument reports
`met=True` on the canonical question without reading anything (`canonical_table_reads=0
self_description_reads=0`), and control 5 is the tree that must not pass it. At the freeze the
worktree copies of `noop-c2.out`/`c1-noop.py` were removed while this seat ran; they were
re-read from the freeze commit `89dc4f52` rather than reconstructed.

## 5. The finding, in exact bytes

Head mirror row (`SCORECARD.md:131`, evidence cell): three pointers.
Canonical row (`SCORECARD.md:2860`, evidence cell): four pointers.

```
canon  : `tools/kama-live-replay.py`; `tools/kama-llamacpp-live.py`;
         `.ufo/waves/round-49/measured/c1-build.out`; `.ufo/waves/round-48/c2/live/receipt-1.json`
mirror : `tools/kama-live-replay.py`; `tools/kama-llamacpp-live.py`;
         `.ufo/waves/round-48/c2/live/receipt-1.json`
```

The other ten rows are cell-identical (`canonical list as of round 49` table at
`SCORECARD.md:2844`). The round-49 build is the one that added that pointer, so the mirror was
not refreshed with the row it mirrors. The lane's own `## Capabilities` fact
(`tools/round42-selfdesc-reconcile.py`, `caps`) compares **names only** (`sorted(hn) !=
sorted(names)`), so no existing counter can see this; `tools/capability-repertoire-audit.py`
compares a name set and an `any()` path test, so it cannot see it either. This is a
name-versus-content gap on a surface the lane calls canonical.

## 6. Distinct case 45 — independent test (separate evidence file)

`case45-verdict.out` is the separate file. It re-derives the assigned claim's own numbers with
shell tools and `case45_independent.py`; it shares no code with the prototype (string search and
line slicing instead of a table parser; a `git cat-file -e` child instead of `os.path.exists`).

**6a. The `maxN=56` / `expected 46` claim — falsified in its second half.** The claim:

> "counter currently reports maxN=56 instead of expected 46; before output mismatch=1"

* `mismatch=1` — **confirmed**. At `b89bdab2` the counter prints
  `r41=1 ... mismatches=1 maxN=56 met=False` and the single failure is the r41 calibration arm
  (`expected '42'`, 43 verifier-spotcheck lessons on disk).
* `maxN=56` — **confirmed and correct**, not stale. `maxN` is the greatest `^## Round (digits)`
  heading by the counter's own docstring, and an independent grep over the frozen bytes returns
  56 (57 headings, five round numbers appearing more than once). No SCORECARD surface yields 46
  as a round maximum: canonical markers `49`, first-working rounds `47`, `### Round-N measured`
  `52`, `### Planned (round N)` `57`, `## Round N` `56`, head banner `Latest measured round: 56`.
* `46` occurs only as (a) `append-only-audit`'s **first-working-round** cell (a column value, in
  every canonical generation that carries the row) and (b) the literal typed into the frozen
  do-nothing harness (`c1-noop.py:3` `print("mismatches=0 maxN=46 met=True")`; the same literal
  in the recorded `noop-c2.out`). Neither is a derived expectation.
* At the current tip the counter prints `mismatches=0 maxN=57 met=True` — `maxN` simply tracks
  the newest `## Round N` heading, which moved to 57 when §Round 57 landed.

**6b. The two implementations agree on every reading they share.** At `b89bdab2` and at
`8a7f1976` the independent program prints `gen=49 rows=11 names=11 evidence=11/11 mirror=11
firsts=11 expected=49 omission=False consistent=True` (exit 0) — the same row count,
generation, evidence coverage and mirror size the prototype reports. On the omission tree it
prints `gen=48 ... omission=True consistent=False` (exit 1) and on the dropped-row mutant
`rows=10 ... consistent=False` (exit 1). The one deliberate difference: it does not compare
mirror **cells**, so it returns `consistent=True` on the lane where the prototype returns
`met=False`. That difference is the finding, not a disagreement: the second implementation
confirms the counts and is blind to the cell drift.

## 7. Non-author spot-check — SOURCES S515 re-opened this round

`S515` (`corpus/SOURCES.md:268`, ADMIT, tier B, mined; supersedes S511) — `git-config(1)`,
<https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT>.

* Re-fetched this round: `curl -sS https://git-scm.com/docs/git-config`, exit 0,
  sha256 `706b1566467e9cd8c6cdda853a5fc82118a48fde3119777d18cefc014bcd3d5a` —
  **byte-identical** (`cmp -s`) to the round-56 snapshot
  `.ufo/waves/round-56/sources/git-docs-git-config.html`. Page still `last updated in 2.56.0`.
* Quote located at the anchor's own section, §`GIT_CONFIG_COUNT` (offset 168376), verbatim after
  normalising the page's typographic apostrophe:

  > "all environment pairs GIT_CONFIG_KEY_&lt;n&gt; and GIT_CONFIG_VALUE_&lt;n&gt; up to that
  > number will be added to the process's runtime configuration"

  **18 words ≤ 25**; the lesson (`corpus/lessons/round-56.md:18`) and the registry row both
  record 18, and the lesson's location (`§GIT_CONFIG_COUNT`) is where the anchor resolves.
* **Advice (lane-authors decide):** S515's ADMIT / tier B / mined stands as written.
* **One admit/reject decision, advised only:** the round-56 outside closure calls S513's
  rejection an outside discernment miss (`corpus/lessons/round-56-verifier-spotcheck.md:41-46`).
  My reading agrees with the recorded treatment, not with a silent repair: the reject was
  justified against "the claim's only need" (the `LD_AUDIT` variable *name*), and rtld-audit(7)
  supplies exactly that; the loss is the broader loader semantics S513's own flip condition
  names. The round-57 lesson already preserves the disagreement as
  `discernment-disagreement` (`corpus/lessons/round-57.md:25`) and requires S513 to be re-opened
  before its gate decision is reused — that is the right disposition for a non-author seat to
  confirm, not to overturn.

## 8. Cross-checks into sibling seats (read-only; not re-run as decoration)

* `E02CanonicalBinding` (same wave, operability-side prototype) reports `genuine-base ...
  mismatches=0 met=True` on the base tree. That is **not** a contradiction: its legs read the
  canonical table alone (`canon`, `evidence`, `content` = non-empty, `exec`), while this seat's
  `met` also binds the head mirror's **cells**. Both are correct on their own surfaces; the
  mirror drift is invisible to a canonical-table-only instrument.
* E02's control 13 `mut-stale` ("round-49 table removed, round-48 table then selected") is
  `met=True` in its §6 limits. This seat's `omission-isolated` is that same fixture class and
  **fails it** (`fail_generation=1`, exit 1) because `expected` is read from the SCORECARD's own
  references, not from the newest marker. That is a leg worth porting, not a defect in E02.
* `R08SelftestMutation`'s case-16 receipts (`measured/r08-case16-*.out`) mutate the round-42
  counter's `caps` fact: `missing-row.mutated` gives `caps=1 retired=1 saturation=1`, i.e. the
  incumbent catches a *name-level* omission only because the mirror and §Retired still state 11.
  Its `noop-pristine` receipt is `mismatches=0 maxN=46 met=True` with
  `scorecard_catfile_reads=0` — the same do-nothing signature this seat's control 6/7 records.

## 9. Round-56 outside defects: lesson coverage checked

`corpus/lessons/round-57.md` carries one row per routed defect: `no-op-counter` (:26),
`discernment-disagreement` (:25, the S513 miss), `inherited-append-only-governance` (:27, kept
red, "do not treat it as clean"), and `calibration-staleness` (:24, the 42→43 count). The
axis-authority conflict is preserved unresolved at `SCORECARD.md:6`. `considerthese/2026-10-26.md`
proposal 3 (a running tally of counters a shortcut can satisfy) is implemented by
`tools/shortcut-tally.py`; run read-only at the tip it exits 0 over rounds 40–56
(`proposal3-shortcut-tally.out`) and has **no row for the canonical-row question**, so this
prototype's legs are not yet tallied anywhere.

## 10. Declared limits (measured, not asserted)

1. **A fully consistent omission is invisible without a witness.** `g2-no-witness` is
   `met=True`: deleting the row from every capability table *and* correcting the stated
   cardinal, the Saturation vector and the mirror leaves nothing inside the file to contradict
   it. `g2-witness` catches it only because the lane tree is passed as `--witness-dir` /
   `--witness-tip`. A row scrubbed from every surface *and* from every witness has no in-tree
   trace; only git history would carry one.
2. **The `content` leg is a prototype oracle.** It binds a cell when every alphanumeric part of
   a distinctive literal occurs in the evidence text, or a six-word run of the cell occurs
   there. `instrument-agreement` binds only through the phrase ("run a lane instrument N times
   over one tree" is verbatim in `tools/instrument-agreement.py`), because its one literal
   `per-run` is absent from a tool that says "A run's digest". A cell rewritten to share six
   incidental words with an unrelated artifact could bind spuriously.
3. **The mirror cell leg is exact-equality on the three value cells.** A deliberately abridged
   mirror (a shorter but true pointer list) fails it. That is the intended reading of "mirror",
   but it is a policy, not a proof.
4. **The evidence and content legs read the tip's bytes, not their execution.** Whether the
   tool runs, and what it does, is `E02CanonicalBinding`'s `exec` leg; this seat measures
   declared-content discovery, which is a different question.

## 11. Touched surfaces and out-of-scope

Written: scratch `/fast/scratch/hyaku/kama-r57/R57Item24CanonicalBinding/` (removed after the
receipts were copied) and this seat's own evidence path
`.ufo/waves/round-57/w1/out/R57Item24CanonicalBinding.{md,/}`. Nothing else. No commit, push, jj
or git mutation; no fleet file (`LOG.md`, `SCORECARD.md`, `MANIFEST.json`, …); no `~/.local/bin`
unless an install — none was made; no sibling repo; no PATH write; no `/tmp` scratch. The lane's
`git rev-parse --show-toplevel` was never used on a fixture because no fixture was made a git
repository — the mutant trees are untracked directories of symlinks, so no git mutation was
possible by construction. Out of scope and untouched: the frozen counters
(`tools/round42-selfdesc-reconcile.py`, `tools/round56-prereg-check.py`), the SCORECARD
calibration row, the S515/S513 registry rows, and the round-57 lesson.

## 12. Artifacts

All under `.ufo/waves/round-57/w1/out/R57Item24CanonicalBinding/` with `ARTIFACTS.sha256`:

`canonical_rows_audit.py`, `case45_independent.py`, `build_controls.py`, `case45.sh`, `s515.sh`;
receipts `lane-base.out`, `lane-head.out`, `fixture-no-canonical.out`,
`fixture-canonical-noop.out`, `omission-isolated.out`, `omission-noop-frozen.out`,
`omission-noop-repro.out`, `canonical-noop-isolated.out`, `m1-drop-row.out`, `g1-row-drop.out`,
`g2-witness.out`, `g2-no-witness.out`, `m3-content.out`, `m4-evidence.out`, `m5-generation.out`,
`m6-duplicate.out`, `m7-mirror-repaired.out`, `case45-verdict.out`, `case45-lane-base.out`,
`case45-lane-head.out`, `case45-omission.out`, `case45-m1-drop-row.out`,
`claim-maxn-counter-base.out`, `claim-maxn-counter-head.out`,
`proposal3-shortcut-tally.out`, `s515-spotcheck.out`, `SUMMARY.out`.

Every receipt records its exact command, working directory, stdout, stderr and exit.
