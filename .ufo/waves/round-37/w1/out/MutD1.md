# Mutation probe — R36-D1 legs of `tools/round37-statement-audit.py`

Seat: `L1Kama37.RudePython` (kama lane, round 37, w1, v1).
Scope: the `R36-D1` branches of `holds()` (`tools/round37-statement-audit.py:113-119`).
No counter file, lesson file, index or jj state was edited or committed; all mutation
work happened on copies inside
`.ufo/waves/round-37/w1/out/MutD1/`.

## 1. Tracking status of `.ufo/waves/round-36/census-end.out`

Tip used for scoring: `6a4afdfe48b0b54239d127761d21a5cf21b5b0ea` (the C1 base, and the
only non-sandbox tip reachable; see §7 about lane `HEAD`).

```
$ git cat-file -e 6a4afdfe48b0b54239d127761d21a5cf21b5b0ea:.ufo/waves/round-36/census-end.out
fatal: path '.ufo/waves/round-36/census-end.out' exists on disk, but not in '6a4afdfe48b0b54239d127761d21a5cf21b5b0ea'
exit=128

$ git cat-file -e HEAD:.ufo/waves/round-36/census-end.out
fatal: path '.ufo/waves/round-36/census-end.out' exists on disk, but not in 'HEAD'
exit=128

$ git ls-files --error-unmatch .ufo/waves/round-36/census-end.out
error: pathspec '.ufo/waves/round-36/census-end.out' did not match any file(s) known to git
exit=1

$ git status --porcelain -- .ufo/waves/round-36/census-end.out
?? .ufo/waves/round-36/census-end.out

$ git log --all --oneline -- .ufo/waves/round-36/census-end.out
(empty)
```

On disk: 12426 bytes, `sha256 7f66ee93c8837cf3dcfdb52abb74556a0ab54a3059f0e6d150869dcbf6083353`,
terminated by a newline, exactly one `kama\tok` occurrence, and that occurrence is the
tail line:

```
last_nonempty  b'kama\tok\t/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md'
ok_count       1
first_line     b'kama\tW04\tS031 duplicate url docs.ollama.com/api/tags across scopes'
```

Context: `git ls-tree -r HEAD` holds census files for rounds 29-35 (8 paths); round 36's
is the only one never committed on any ref.

## 2. The legs under test

```python
113:    if sid == "R36-D1":
114:        return (
115:            census_base is None
116:            and census_tip is not None
117:            and "kama\tok" in census_tip
118:            and CENSUS_PATH in row
119:        )
```

`census_tip`/`census_base` come from `load_facts()` -> `git_show(repo, tip|BASE, CENSUS_PATH)`,
so both are `None` here (git cannot show an untracked path).

## 3. Constructed row (`row-d1.md`, sha256 `0932b572f747287ee0d3c6eefb4b5f64ea42ec01d13e950ed4551603236d51c5`)

One line, `ID: text` form as `rows_of()` requires; `\t` below is a real tab:

```
R36-D1: .ufo/waves/round-36/census-end.out exists only in the working tree (untracked at tip and at base 6a4afdfe48b0b54239d127761d21a5cf21b5b0ea); its tail line is kama<TAB>ok<TAB>/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
```

It satisfies every row-level conjunct the counter has for D1: `CENSUS_PATH` is in the row,
the id prefix is exactly `R36-D1:`, and `forbidden_in("R36-D1", row)` is `None` because the
D1 branch of `forbidden_in()` returns `None` unconditionally. It is the *honest* row: it
states the file is untracked, which is what the committed bytes say.

## 4. Detector

`d1_harness.py` (sha256 `e66eca26c87fad4ecdf969a4ca0fbfa8b432b10a1ac87f572c666b52f3813962`)
imports a given
counter file by path, calls its own `load_facts(REPO, tip)`, `holds("R36-D1", row, ...)`,
`forbidden_in("R36-D1", row)` and `score(lesson, ...)`. Two fact modes:

- `committed` — `census_tip` exactly as `load_facts()` returns it (the real counter path);
- `ondisk` — `census_tip` replaced by the working-tree bytes (counterfactual; the counter
  never does this).

The detector's contract for D1 at an untracked tip is `D1_holds=False`; the row must be
rejected. `lesson4.md` (sha256 `0c13b68cede4e45fe58f61b8c8d4f64106589e5aa15da6379bdfff42bb8100ce`)
adds the D2A/D2B/D3 rows the real base facts accept, so the full `score()` can also be read.

## 5. Results

Counter bytes: pristine `sha256 50dea74c3a3e2b20a46b3d491ed2a311a3103c043abdfe416e95275657add14f`
(= `tools/round37-statement-audit.py`), mutant `sha256 a1fbb94cdee90384abe56a65120cfa33a35cced1c6c3b2a87d5fe01dd84033ab`.

| # | counter | mode | tip | `D1_holds` | `forbidden` | `score()` | exit |
|---|---|---|---|---|---|---|---|
| A | pristine | committed | 6a4afdfe | **False** | None | `uncorrected 3 false_corrections 1 lesson_unchanged 1 report_unchanged 1 met False` | 1 |
| B | pristine | ondisk | 6a4afdfe | **True** | None | `uncorrected 3 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False` | 0 |
| C | mutant | committed | 6a4afdfe | **True** | None | `uncorrected 3 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False` | 0 |
| D | mutant | ondisk | 6a4afdfe | True | None | same as C | 0 |
| E | restored | committed | 6a4afdfe | **False** | None | `uncorrected 3 false_corrections 1 lesson_unchanged 1 report_unchanged 1 met False` | 1 |

With the four-row lesson (only the four rows differ in the lesson text; facts unchanged):

```
pristine/committed   D1_holds=False  uncorrected 0 false_corrections 1 lesson_unchanged 1 report_unchanged 1 met False   exit=1
mutant/committed     D1_holds=True   uncorrected 0 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met True    exit=0
restored/committed   D1_holds=False  uncorrected 0 false_corrections 1 lesson_unchanged 1 report_unchanged 1 met False   exit=1
```

(`uncorrected 0 false_corrections 1` on pristine proves the D2A/D2B/D3 rows pass on the real
base facts and the single false correction is D1 — the rejection is isolated, not shared blame.)

Live counter at the same tip, for parity: `uncorrected 4 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False`
(exit 1), `--selftest` -> `SELFTEST empty_met=False bad_met=False good_met=True pass=1` (exit 0),
i.e. the base tip reproduces the frozen no-op control bit for bit.

## 6. Answer to the probe question

**The counter rejects the row.** Rejection is carried by exactly one conjunct: `census_tip is not None`
is False because `git show <tip>:<path>` fails on an untracked path, so row A yields
`D1_holds=False` and `false_corrections 1` (`met False`).

Two things the probe establishes beyond that:

- The rejection is **not** caused by the row's content. Run B hands the predicate the same
  untracked file's bytes and the row passes — including the row that literally says the file
  is untracked. No conjunct reads the row's prose, no conjunct checks the ok line is *last*
  (only `"kama\tok" in census_tip`), and no conjunct checks the ok line's third column.
  The trackedness gate lives entirely in `load_facts()`/`git_show`, not in the D1 leg's
  logic.
- On the pristine counter the honest row is **unpassable** at this tip: `census_tip` will be
  `None` until `.ufo/waves/round-36/census-end.out` is committed, and the C1 precondition
  (`census_base is None`) forbids it existing at the base. A lying row ("census is tracked at
  the tip, tail kama ok") is rejected identically. So D1 can only be corrected by committing
  the file — which was outside this probe's bounds and which this report did not do.

## 7. Mutant

Smallest behavior-bearing point in the D1 leg: the pair `census_tip is not None` /
`"kama\tok" in census_tip`, relaxed to let the row supply the tail evidence when no committed
census exists.

```diff
--- counter-pristine.py
+++ counter-mutant.py
@@ -113,8 +113,7 @@
     if sid == "R36-D1":
         return (
             census_base is None
-            and census_tip is not None
-            and "kama\tok" in census_tip
+            and "kama\tok" in (census_tip or row)
             and CENSUS_PATH in row
         )
     if sid == "R36-D2A":
```

Behaviour: with `census_tip=None` and a row that contains `kama<TAB>ok`, the leg returns
`True`; row C/E therefore differ only on the tracking gate.

**Verdict: KILLED.** Detector contract expects `False` at an untracked tip; mutant returns
`True` (row C) and, with the four-row lesson, flips the whole claim from
`met False` to `met True` while the census remains untracked on disk and absent from every
commit. The kill is at predicate level, not just leg level.

**Coverage finding (the reason the mutant would otherwise survive):** the counter's own
`--selftest` never feeds `census_tip=None`. Its `good` fixture passes
`census_tip=good_census` (a fabricated string) and its `bad` fixture passes the same
`good_census`, so both selftest branches exercise only the `census_tip is not None` side; the
untracked-tip branch — the one that carries the "re-derives the cited *committed-byte* fact"
requirement — is unexercised. The mutation is also behaviourally inert whenever a census
exists at the tip (pristine and mutant both return `True`), so no in-repo fixture can ever
catch it; the kill required the out-of-band untracked-tip fixture built here. Suggested
addition (not applied): a selftest case with `census_tip=None` that must score `met False`.

This is reported as a coverage gap, not as licence to change the predicate.

## 8. Tip note (lane `HEAD` is a sandbox tip, not a scoring tip)

`git log --oneline 6a4afdfe..HEAD -- corpus/lessons/round-36.md` shows only sandbox mutation
commits (`mut1`..`mut4`, all `(sandbox only)`). At `HEAD=873c5d7774b97e7c633052456f13595a2ea5775f`
the r36 lesson blob is `0418795fa22381778fa8f7cda4f4597442b51198`, not the frozen
`6fb1ec151407b1207e8d540e83ba87d6a909d8ea`, so a `HEAD`-tip run prints
`uncorrected 4 false_corrections 0 lesson_unchanged 0 report_unchanged 1 met False` and its
selftest prints `pass=0`. That is an artefact of the sandbox mutations, not a lane defect and
not part of the D1 leg. D1's own facts are identical at both tips (`census_tip` and
`census_base` are both `None`); the base tip was used for every scored number above.

## 9. Restoration evidence

Restored by copying the pristine bytes back over the mutant copy (the lane file was never
edited at any point — only read and copied).

```
before: 50dea74c3a3e2b20a46b3d491ed2a311a3103c043abdfe416e95275657add14f  tools/round37-statement-audit.py
mutant: a1fbb94cdee90384abe56a65120cfa33a35cced1c6c3b2a87d5fe01dd84033ab  (seat copy only)
after:  50dea74c3a3e2b20a46b3d491ed2a311a3103c043abdfe416e95275657add14f  counter-pristine.py
        50dea74c3a3e2b20a46b3d491ed2a311a3103c043abdfe416e95275657add14f  counter-mutant.py
        50dea74c3a3e2b20a46b3d491ed2a311a3103c043abdfe416e95275657add14f  tools/round37-statement-audit.py
$ diff -q counter-pristine.py counter-mutant.py
restored_identical=yes
```

Post-restore detector run: `D1_holds=False`, `uncorrected 0 false_corrections 1 … met False`,
exit 1 — identical to the pre-mutation baseline. Mutant bytes were reproduced a second time
from pristine to confirm `a1fbb94c…` (seat file `mutant-bytes-replay.py`, same probe output
`met True`), so the killed verdict is attached to an exact, reproducible byte sequence. The
diff is preserved as `mutant.diff`.

Scratch artifacts (all under `.ufo/waves/round-37/w1/out/MutD1/`):
`counter-pristine.py`, `counter-mutant.py` (restored pristine), `mutant-bytes-replay.py`,
`mutant.diff`, `row-d1.md`, `lesson4.md`, `d1_harness.py`.

Not done, by instruction: counter not edited, census not committed, no git/jj mutation
commands, no sibling or fleet files touched, no tool installs or package transactions
(pacman is paused; none was needed).
