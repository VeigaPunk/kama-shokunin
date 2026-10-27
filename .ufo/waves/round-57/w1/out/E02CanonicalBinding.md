# E02CanonicalBinding — operability-side canonical-row binding prototype + no-op omission control

Seat: `E02CanonicalBinding` (executor, leaf), kama round 57, wave `kama-r57-w1`.
Assigned item: prototype an **operability-side** tool/check whose input is the lane's
**actual canonical capability rows**, with a **no-op omission control**. Distinct from the
calibration stale-count item; no shared edits. Distinct case 4 evidence is a separate file
(`.ufo/waves/round-57/reports/E02CanonicalBinding-case04.md`).

Scope compliance: every file written by this seat is under
`/fast/scratch/hyaku/kama-r57/E02CanonicalBinding/` (scratch, 411 MB of hardlinked fixtures)
or under this seat's exclusive wave evidence path
`.ufo/waves/round-57/w1/out/E02CanonicalBinding/`. No lane source file was edited, no
commit/jj/push, no fleet file, no sibling repo. Tooling: `python3` (stdlib) + `git` CLI
only — **no install or upgrade was performed in this seat**.

## 1. What the prototype is

`canon-binding.py` (sha256 `2ea0c67e3e5ae9be1fbbaf266432f2ae1017687f422c92fbe5142a2c0993006c`),
copied to `.ufo/waves/round-57/w1/out/E02CanonicalBinding/canon-binding.py`.

Two modes over one read surface (`git cat-file` at `--tip`, or a filesystem `--root` for
fixtures). It imports no lane counter, so it is an independent second instrument on a
surface the frozen counters also read.

* `audit` — derive the canonical table from the **single highest-numbered**
  `**Capabilities — canonical list as of round N**` heading at the tip, then bind each row:
  * `canon` — a canonical heading exists and the table has ≥ 1 row;
  * `evidence` — every backticked path token of every row's evidence cell resolves at the tip;
  * `content` — every resolved evidence blob is **non-empty** (a declared path whose file is
    empty is a name, not content);
  * `exec` — every distinct `tools/*.py` evidence token is **executed from the tip's own
    bytes** (`--help`, exit 0, non-empty stdout) and at least one such token exists.
  Every canonical row is emitted as its own line with its own digest, so the row set cannot
  be summarised away: `rows_bound` is compared against the number of rows the table actually has.
* `verify` — independently re-derives every fact from the same tree and compares it with an
  instrument's `audit` output. It rejects a summary that omits the canonical rows, a digest the
  tree does not support, a row set from another revision, and a `met` verdict the tree does not
  support. With `--instrument-cmd` it also **runs the instrument afresh with a per-run nonce**,
  so a recorded receipt cannot be replayed onto a different tree.

## 2. Frozen baseline (before) and the prototype's verdict (after)

The frozen no-op, as committed at `7c873d7b` (copies retrieved from that commit into
`.../E02CanonicalBinding/frozen/`, because the worktree copies moved during the wave):

```
$ python3 frozen/c1-noop.py
mismatches=0 maxN=46 met=True
exit=0

$ cat frozen/noop-c2.out
control=no-op instrument
canonical_table_reads=0
self_description_reads=0
summary=mismatches=0 maxN=46 met=True
exit=0
```

A do-nothing instrument that reads nothing reports `met=True` and exits 0 — this is the
defect the assigned item names, reproduced here as the frozen control.

The same output under the prototype's verification at the frozen base `b89bdab2`:

```
$ python3 canon-binding.py verify --repo <lane> --tip b89bdab2 --scratch <dir> \
      --instrument-out frozen/noop-c2.out
tip=b89bdab2cc114735ec5d331c6c610134258f7864
instrument=frozen/noop-c2.out
claims_met=True tree_met=True claimed_rows=0 derived_rows=11 mismatches=6 rejected=1 accepted=0
detail: canon_sha256 claim None != derived e27664aa8213cbe977cc83b6971e841686c4aff5ed23caae415d32f79c1a1b19
detail: canon_rows claim None != derived 11
detail: row lines: missing=['append-only-audit', 'context-capacity-receipt', 'digest-ledger', 'gguf-declared-identity-replay', 'hexrun-census', 'instrument-agreement', 'live-llamacpp-lifecycle', 'live-receipt-replay', 'ollama-offline-evidence-replay', 'pin-watch', 'sources-registry'] extra=[] differ=[]
detail: rows_bound claim None != derived 11
detail: evidence claim None != derived (20, 20)
detail: exec claim None != derived (10, 10)
exit=1
```

`tree_met` is the verdict on the **tree**, not on the instrument: at the base the tree is
green (the canonical rows do bind), while the instrument is rejected (`rejected=1`) for
claiming a green it never derived. The genuine instrument on the same tree is accepted:

```
$ python3 canon-binding.py audit --repo <lane> --tip b89bdab2 --scratch <dir>
tip=b89bdab2cc114735ec5d331c6c610134258f7864
canon_round=49 canon_rows=11 canon_sha256=e27664aa8213cbe977cc83b6971e841686c4aff5ed23caae415d32f79c1a1b19
row=sources-registry ev=1/1 ex=0/0 content=1/1 sha=a40969f7b0589153
row=ollama-offline-evidence-replay ev=1/1 ex=1/1 content=1/1 sha=319e0f2c00359f8c
row=live-llamacpp-lifecycle ev=1/1 ex=0/0 content=1/1 sha=b00340ff1839d433
row=gguf-declared-identity-replay ev=1/1 ex=1/1 content=1/1 sha=988e9f69e58ca642
row=context-capacity-receipt ev=1/1 ex=1/1 content=1/1 sha=ddd6046494a1a6e7
row=instrument-agreement ev=1/1 ex=1/1 content=1/1 sha=350efa1054f65142
row=pin-watch ev=3/3 ex=1/1 content=3/3 sha=f91c58d94912d478
row=digest-ledger ev=2/2 ex=1/1 content=2/2 sha=7d0df8a9e68ec2fc
row=hexrun-census ev=2/2 ex=1/1 content=2/2 sha=11c5add6fb6f0d79
row=append-only-audit ev=3/3 ex=1/1 content=3/3 sha=3f674d13736a5eae
row=live-receipt-replay ev=4/4 ex=2/2 content=4/4 sha=60907b36cd446e12
rows_bound=11/11 evidence=20/20 content=20/20 exec=10/10
canon=0 evidence=0 content=0 exec=0 mismatches=0 met=True
exit=0
```

So the item's predicate holds on this prototype: **the no-op is rejected (exit 1) while the
genuine canonical-row set is accepted (exit 0)**.

## 3. Control matrix (every receipt is in `.../E02CanonicalBinding/receipts/`, exits in `.../exits/`)

`met` is the audit leg verdict; `rejected/accepted` is the verify verdict.

| # | Control | Input | Observed summary | Exit |
|---|---|---|---|---|
| 1 | `genuine-base` | audit, `--tip b89bdab2` | `rows_bound=11/11 evidence=20/20 content=20/20 exec=10/10 … mismatches=0 met=True` | 0 |
| 2 | `genuine-3d2d5d4d` | audit, later tip | `canon_sha256=e27664aa…` identical, `met=True` | 0 |
| 3 | `genuine-8a7f1976` | audit, later tip | `canon_sha256=e27664aa…` identical, `met=True` | 0 |
| 4 | `noop-rows-only` | audit, frozen `controls/canonical-noop` (rows present, supporting tree absent) | `rows_bound=1/11 evidence=1/20 content=1/20 exec=0/0` → `canon=0 evidence=1 content=0 exec=1 mismatches=2 met=False` | 1 |
| 5 | `no-canonical` | audit, frozen `controls/no-canonical` | `canon_round=48 rows_bound=0/11 evidence=0/19` → `mismatches=2 met=False` | 1 |
| 6 | `no-heading` | audit, tree with every canonical table stripped | `canon_round=-1 canon_rows=0` → `canon=1 evidence=1 content=0 exec=1 mismatches=3 met=False` | 1 |
| 7 | `mut-delete` | base tree, one evidence blob deleted | `rows_bound=10/11 evidence=19/20 … evidence=1 mismatches=1 met=False` | 1 |
| 8 | `mut-empty` | base tree, one evidence blob emptied | `content=19/20 … content=1 mismatches=1 met=False` (only the content leg fires) | 1 |
| 9 | `mut-exec` | base tree, `tools/pin-watch.py` replaced by an exit-1 stub | `exec=9/10 … exec=1 mismatches=1 met=False` | 1 |
| 10 | `mut-silent` | base tree, `tools/digest-ledger.py` exits 0 printing nothing | `exec=9/10 … exec=1 mismatches=1 met=False` | 1 |
| 11 | `mut-extra-row` | base tree, one row appended to the canonical table (evidence resolves) | `canon_rows=12 rows_bound=12/12 exec=11/11 met=True` | 0 |
| 12 | `mut-rename` | base tree, one row renamed | `row=hexrun-census-renamed … canon_rows=11 met=True` | 0 |
| 13 | `mut-stale` | base tree, round-49 table removed (round-48 table then selected) | `canon_round=48 canon_rows=11 canon_sha256=a30fc405…`, `met=True` (see §6 limit) | 0 |
| 14 | `verify-genuine` | verify, receipts/genuine-base.out | `accepted=1 rejected=0 mismatches=0` | 0 |
| 15 | `verify-frozen-noop` | verify, regenerated frozen no-op output | `claimed_rows=0 derived_rows=11 mismatches=6 rejected=1` | 1 |
| 16 | `verify-frozen-noop-c2-receipt` | verify, committed `controls/noop-c2.out` | `rejected=1 mismatches=6` | 1 |
| 17 | `verify-frozen-noop-c1-receipt` | verify, committed `controls/noop-c1.out` | `rejected=1 mismatches=6` | 1 |
| 18 | `verify-forged-sha` | verify, genuine output with one digest nibble flipped | `canon_sha256 claim f27664aa… != derived e27664aa…` → `rejected=1` | 1 |
| 19 | `verify-forged-omit` | verify, genuine summary with **every `row=` line deleted** | `row lines: missing=[11 names]` → `rejected=1` | 1 |
| 20 | `verify-stale-table` | verify, an output derived from the round-48 table | `mismatches=4 rejected=1` (`canon_sha256 a30fc405… != e27664aa…`, `differ=['append-only-audit', 'live-receipt-replay']`, `evidence (19,19) != (20,20)`, `exec (11,11) != (10,10)`) | 1 |
| 21 | `verify-mut-extra-row` | verify, 12-row output against the 11-row tree | `row lines: extra=['probe-row-e02']`, `canon_rows 12 != 11` → `rejected=1` | 1 |
| 22 | `verify-mut-rename` | verify, renamed-row output against the real tree | `missing=['hexrun-census'] extra=['hexrun-census-renamed']` → `rejected=1` | 1 |
| 23 | `verify-base-as-if-noop-rows` | verify, a red-fixture output against the green base tree | `instrument met=False vs independently derived met=True` → `rejected=1` | 1 |
| 24 | `verify-noop-rows-against-fixture` | verify, genuine output against the omitting fixture | `rejected=1` (fixture tree itself red: 1/11 rows bound) | 1 |
| 25 | `verify-cmd-genuine` | verify, instrument **run afresh** with a nonce | `nonce=<fresh> … accepted=1` | 0 |
| 26 | `verify-cmd-noop` | verify, no-op run afresh with the same nonce | `rejected=1 mismatches=6` | 1 |
| 27 | `verify-cmd-copycat-othertree` | verify, a recorded receipt replayed with the nonce onto another tree | `canon_sha256 … != derived 8e14ef32…`, `canon_rows 11 != 12`, `rejected=1` | 1 |
| 28 | `verify-cmd-copycat-sametip` | verify, the same replay onto the **same** tip | `accepted=1` — honest residual, §6 | 0 |

Battery summary verbatim: `.../receipts/battery-summary.txt`.

### Legs are load-bearing (no leg passes only because the other side already failed)

| Leg | Mutant that fires it and nothing else | Receipt |
|---|---|---|
| `canon` | `no-heading` — no canonical table anywhere | `receipts/no-heading.out` |
| `evidence` | `mut-delete` — one evidence path removed | `receipts/mut-delete.out` |
| `content` | `mut-empty` — one evidence file emptied, path still resolves | `receipts/mut-empty.out` |
| `exec` | `mut-exec` (exit 1) and `mut-silent` (exit 0, no stdout) | `receipts/mut-exec.out`, `receipts/mut-silent.out` |

### The input is the table, not a constant

`mut-extra-row` makes the table 12 rows and the tool reports `canon_rows=12`, binds and
executes the added row (`row=probe-row-e02 ev=1/1 ex=1/1`), and `mut-rename` renames a row
and the tool reports the new name. `independent-derive.py` (a separate one-off route, no
import of the prototype) agrees on the base: `routeA_rows=11`,
`routeA_names=sources-registry,…,live-receipt-replay`, `routeA_firsts=10,14,16,20,25,30,41,42,43,46,47`
and the §Saturation prose list is byte-identical to that firsts list
(`receipts/independent-derive.out`).

## 4. Reproduce

```sh
SEAT=/fast/scratch/hyaku/kama-r57/E02CanonicalBinding        # or any writable dir
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
EV=$LANE/.ufo/waves/round-57/w1/out/E02CanonicalBinding
python3 $EV/canon-binding.py audit  --repo $LANE --tip b89bdab2 --scratch $SEAT/tmp
python3 $EV/canon-binding.py verify --repo $LANE --tip b89bdab2 --scratch $SEAT/tmp \
        --instrument-out $EV/frozen/noop-c2.out
bash $EV/run-controls.sh                                   # rebuilds the whole matrix in $SEAT
```

`run-controls.sh` needs the fixture trees described in §5 (it rebuilds the frozen controls
from commit `7c873d7b` but not the mutation trees); scratch was cleaned after the receipts were
copied, so the fixtures must be rebuilt before rerunning the battery.

## 5. Fixtures

Frozen, read-only, from the wave's own controls dir (not modified):
`controls/canonical-noop` (real SCORECARD with 11 canonical rows; `tools/`, `registry/`,
`.ufo/`, `corpus/knowledge/` absent) and `controls/no-canonical` (SCORECARD only).

Built in scratch from `git archive b89bdab2` (411 MB, hardlinked per mutant, so no mutation
leaks between trees): `base-tree`, `mut-exec`, `mut-silent`, `mut-delete`, `mut-empty`,
`mut-stale`, `mut-extra-row`, `mut-rename`, `no-heading`. Each mutation removes the file and
writes a new inode, so the hardlinked base is never rewritten.

## 6. What `met=True` does not show (limits, measured or by construction)

1. **Replay of the same tip is indistinguishable.** `verify-cmd-copycat-sametip` (control 28)
   is accepted: a recorded receipt replayed with a fresh nonce onto the tip it was recorded at
   carries facts that *are* true there. The cheat that remains is a receipt replayed onto a
   changed tree, which `verify-cmd-copycat-othertree` rejects. The nonce binds a run, not a reader.
2. **Verify's independence is code-level, not implementation-level.** `verify` re-derives from
   the tree in the same file with the same parsing helpers, so a systematic parsing error
   (e.g. "the highest canonical heading is the right one") is invisible to it. A second
   implementation written from this docstring is the missing control.
3. **Staleness is not graded.** `mut-stale` is `met=True`: a round-48 table whose evidence all
   resolves is *content-bound*; that it is out of date is the calibration item's surface, not
   this instrument's. Cross-checking the table against the §Saturation prose list would be a
   calibration leg and was deliberately not added (scope boundary, §7).
4. **Execution is `--help` only.** The `exec` leg proves the tool's own bytes run and print;
   it does not prove the capability's described behaviour (no model, no endpoint, no receipt).
   It also accepts any exit-0 printer, so it binds *executability*, not *correctness*.
5. **`--root` fixtures are filesystem state, not commits.** The frozen omission fixtures are
   plain trees; their evidence "misses" are true of those trees, and the same tree could exist
   untracked anywhere. Only git-mode runs bind to immutable bytes.
6. **`tools/*.py` is the only executed token class.** `corpus/SOURCES.md`, `.tsv` registries and
   `.json` receipts are resolved and hashed but not parsed for content, so an evidence file
   could exist, be non-empty, and be unrelated to its row.
7. **Duplicate row names are not graded** by this instrument (the sibling item-04 prototype
   grades `distinct`); a duplicated canonical row would bind twice here.

## 7. Boundaries and overlap

* **Assigned item vs the calibration claim.** This report grades only the operability side:
  canonical rows bound to content and execution. It does not touch
  `tools/round42-selfdesc-reconcile.py`, its `maxN`, or the round-56 spotcheck count — the
  frozen counter is the calibration item's surface, and no file under `tools/`, `corpus/`,
  `registry/` or the SCORECARD was edited by this seat.
* **Sibling `R57Item04CanonicalBinding`** (scribe, item 04) prototyped a content-bound audit
  with `bind` / `rounds` / `mirror` / `distinct` legs and a `canonical_reads=0` harness. This
  seat's prototype is a second, independent instrument on the same input with different legs
  (`content` non-emptiness and **execution from the tip's bytes**) plus a nonce-bound `verify`
  mode; the two agree on `rows=11` and on the row names, which is corroboration, not a shared
  artifact. No file of that seat was read-modified or overwritten.
* **Item numbering.** The dispatch text numbers the operability no-op item `C2` and the
  calibration stale-count item `C1`; `controls/freeze-amendment.txt` numbers them the other
  way (`C1` = operability no-op, `C2` = calibration stale count). Reported as-is, not resolved
  here.

## 8. Advisory to the L1 (observations, no edits made)

1. **Frozen control receipts moved mid-wave.** `controls/noop-c1.out`, `controls/noop-c2.out`
   and `controls/c1-noop.py` are absent from the worktree after the post-freeze commits, while
   `freeze.txt` still cites them. They exist at `7c873d7b`; this seat read them from that
   commit. Any seat that resolves them by worktree path will now fail to open them (this seat
   hit exactly that: two `could-not-evaluate` exits before pinning to the commit).
2. **`controls/no-canonical` is not a no-canonical-table tree.** Its SCORECARD still carries
   the round-48 canonical list, so a counter that selects the *highest* canonical heading
   still derives `canon_round=48, canon_rows=11`. It is a content-omission fixture
   (`rows_bound=0/11`), not a "no canonical table" fixture; a true absence fixture is
   `no-heading` here (`canon_rows=0`).
3. **The canonical table is stable across this wave.** `canon_sha256=e27664aa…` and
   `canon_rows=11` at `b89bdab2`, `3d2d5d4d` and `8a7f1976`, so a frozen count of 11 does not
   move under the round-57 commits so far.
4. **§Saturation's prose `first-working rounds` list equals the table's first-working column**
   (11 values, identical order) at the base — a consistency datum for whichever seat grades
   the truth mirror; this seat deliberately did not make it a leg.
5. **Outside closure obligations owned by other seats, not performed here** (this is a
   lane-author seat): the non-author spot-check must re-open SOURCES **S515** (Git config
   runtime environment pairs) this round and report the located quote (≤ 25 words) with its
   URL and access date, plus one admit/reject decision spot check — advised for
   `S01SourcesReopen` / `R05SourcesGate` / `R57Item06` / `R57Item13`; the round-56 outside
   defects must land in the round-57 lesson Gate/Mistakes (`Q01CritiqueRound56` /
   `R57Item07`); `considerthese/2026-10-26.md` proposal 3 (self-description counter shortcut
   tally) is the opened proposal this round (`R06Assimilation` / `R57Item14`).

## 9. Artifacts

```
.ufo/waves/round-57/w1/out/E02CanonicalBinding.md                    this report
.ufo/waves/round-57/reports/E02CanonicalBinding-case04.md            distinct case 4 evidence
.ufo/waves/round-57/w1/out/E02CanonicalBinding/canon-binding.py      prototype (2ea0c67e…)
.ufo/waves/round-57/w1/out/E02CanonicalBinding/noop-instrument.py    no-op control (b7ba6204…)
.ufo/waves/round-57/w1/out/E02CanonicalBinding/copycat-instrument.py replay control (4281137b…)
.ufo/waves/round-57/w1/out/E02CanonicalBinding/run-controls.sh       battery (7d4b0287…)
.ufo/waves/round-57/w1/out/E02CanonicalBinding/receipts/             34 receipts (27 with recorded exit codes)
.ufo/waves/round-57/w1/out/E02CanonicalBinding/exits/                27 exit codes
.ufo/waves/round-57/w1/out/E02CanonicalBinding/frozen/               controls as committed at 7c873d7b
.ufo/waves/round-57/w1/out/E02CanonicalBinding/independent-derive.py independent cross-check
```

Scratch: `/fast/scratch/hyaku/kama-r57/E02CanonicalBinding/`, cleaned after every receipt was
copied here; the tool, instruments, receipts, exits and frozen controls above are the durable
copy, and the mutation fixtures are rebuildable with `git archive b89bdab2` plus the mutations
listed in §5.
