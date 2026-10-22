# Advice report — ExecPromisorAnchorCount (kama round 25, C1 scope disclosure)

Verdict: No. The sibling registered instrument `tests/report-audit/promisor-mutants.py`
has no blocking stale anchor at base 147f5bdd: all 10 executed mutants still apply
exactly once and compile, so it does not share the C1 stale-anchor class in the
mutant-level sense; four individual edits inside it match zero times, so it does
carry four dead fallback edits that a later drift would expose.

## What was measured

Target measured: `tools/report-landing-audit.py` at base
`147f5bdd3228ab712520b5f377346cb2d9a64769` (sha256
`b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f`, 82288 bytes
on disk).

The instrument measured: `tests/report-audit/promisor-mutants.py` (sha256
`971c3ecbc1af05d4e6806ed06e8d3c7499ff55caf09e7bbc2c5ae2992204f200`), whose frozen
inventory is the `MUTANTS` list at lines 258-484 (11 entries; PM08 is `review-only`
and carries no source assertion).

Both files in the lane working tree are byte-identical to their base-revision
content, so the base measurement is also the lane-tip measurement:

```
$ cd /home/vgpnk/Projects/shokunin/kama-shokunin
$ git show 147f5bdd3228ab712520b5f377346cb2d9a64769:tools/report-landing-audit.py | sha256sum
b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f  -
$ sha256sum tools/report-landing-audit.py
b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f  tools/report-landing-audit.py
$ git show 147f5bdd3228ab712520b5f377346cb2d9a64769:tests/report-audit/promisor-mutants.py | sha256sum
971c3ecbc1af05d4e6806ed06e8d3c7499ff55caf09e7bbc2c5ae2992204f200  -
$ sha256sum tests/report-audit/promisor-mutants.py
971c3ecbc1af05d4e6806ed06e8d3c7499ff55caf09e7bbc2c5ae2992204f200  tests/report-audit/promisor-mutants.py
```

Lane state at the time of the measurement: `git log --oneline -3` shows
`147f5bd` (the base) as HEAD; `git status --porcelain` shows only the untracked
`.ufo/waves/round-25/`. No lane write was performed.

## The apply rule I respected

`apply_mutation` in `tests/report-audit/promisor-mutants.py:678-700`:

* `replace`: `source.count(old)` must be exactly 1;
* `regex`: `len(re.findall(pattern, source, re.DOTALL))` must be exactly 1;
* `insert`: `source.count(anchor)` must be exactly 1;
* the alternatives of a mutant are tried in order and the first one with count
  exactly 1 is applied; a mutant with no such alternative returns
  `(None, "no alternative applied cleanly: ...")` and the runner records it as
  `could-not-evaluate`, which kills nothing (docstring lines 85-96).

So "stale" is measured twice: per edit (the count is not 1) and per mutant (no
alternative reaches count 1, so the mutant cannot be applied at all).

## Command and output

Script written by me:
`.ufo/waves/round-25/build/out/ExecPromisorAnchorCount/anchor-count.py`
(read-only; it loads the instrument's own `MUTANTS` table and reuses the
instrument's own `apply_mutation` for the compile check; no grid is run, no file
is modified).

```
$ cd /home/vgpnk/Projects/shokunin/kama-shokunin
$ python3 .ufo/waves/round-25/build/out/ExecPromisorAnchorCount/anchor-count.py \
    --clone /fast/scratch/hyaku/kama-r25/ExecPromisorAnchorCount/clone \
    --out .ufo/waves/round-25/build/out/ExecPromisorAnchorCount/anchor-count.json
```

Exit code 0. Output (also saved as
`.ufo/waves/round-25/build/out/ExecPromisorAnchorCount/anchor-count.txt`):

```
base 147f5bdd3228ab712520b5f377346cb2d9a64769
auditor sha256 b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f
mutants 11
PM01-blanket-metadata-refusal: [0]regexx0 [1]insertx1 -> applies via alternative 1, compiles=True
PM02-blanket-unknown-refusal: [0]insertx1 -> applies via alternative 0, compiles=True
PM03-skip-required-object-availability: [0]regexx0 [1]regexx1 -> applies via alternative 1, compiles=True
PM04-accept-unavailable-referenced-object: [0]regexx1 [1]regexx1 -> applies via alternative 0, compiles=True
PM05-ignore-second-repo: [0]regexx1 [1]regexx1 -> applies via alternative 0, compiles=True
PM06-swallow-actual-read-error: [0]insertx1 -> applies via alternative 0, compiles=True
PM07-full-all-missing-gate: [0]regexx1 [1]regexx0 [2]regexx0 -> applies via alternative 0, compiles=True
PM08-no-lazy-fetch-review-only: review-only (no source assertion)
PM09-peel-bare-full-hash-lookup: [0]replacex1 -> applies via alternative 0, compiles=True
PM10-ignore-opaque-nonleaf-missing: [0]insertx1 -> applies via alternative 0, compiles=True
PM11-any-hole-refusal: [0]insertx1 -> applies via alternative 0, compiles=True
mutants with no applicable alternative: 0 []
edits total 16: exactly once 12, zero times 4, more than once 0
  zero-match edit: PM01-blanket-metadata-refusal alternative 0 (regex): '(    state = promisor_state\(repo\)\n)'
  zero-match edit: PM03-skip-required-object-availability alternative 0 (regex): 'self\._missing = set\(missing_reachable\(self\.path, self\.root\)\)'
  zero-match edit: PM07-full-all-missing-gate alternative 1 (regex): '(    roots = present_commits\(repo\)\n)'
  zero-match edit: PM07-full-all-missing-gate alternative 2 (regex): '("--no-object-names",\s*)root'
stale anchors present: False
```

## Per-mutant counts

| mutant | edit 0 | edit 1 | edit 2 | applies via | compiles |
|---|---|---|---|---|---|
| PM01-blanket-metadata-refusal | regex x0 | insert x1 | - | 1 | yes |
| PM02-blanket-unknown-refusal | insert x1 | - | - | 0 | yes |
| PM03-skip-required-object-availability | regex x0 | regex x1 | - | 1 | yes |
| PM04-accept-unavailable-referenced-object | regex x1 | regex x1 | - | 0 | yes |
| PM05-ignore-second-repo | regex x1 | regex x1 | - | 0 | yes |
| PM06-swallow-actual-read-error | insert x1 | - | - | 0 | yes |
| PM07-full-all-missing-gate | regex x1 | regex x0 | regex x0 | 0 | yes |
| PM08-no-lazy-fetch-review-only | review-only, no source assertion | | | - | - |
| PM09-peel-bare-full-hash-lookup | replace x1 | - | - | 0 | yes |
| PM10-ignore-opaque-nonleaf-missing | insert x1 | - | - | 0 | yes |
| PM11-any-hole-refusal | insert x1 | - | - | 0 | yes |

## Why the four zero-match edits miss (anchored in the auditor at base)

* `PM01` alternative 0, pattern `    state = promisor_state(repo)\n`: the auditor
  has no `promisor_state` function at all. `grep -n "promisor_state" tools/report-landing-audit.py`
  returns nothing; the only `promisor` occurrences in the auditor are the policy
  text at lines 58-59 and 134 and the store walk note at line 749, plus the
  self-test fixture that writes the promisor config at lines 1355-1362. The
  spelling-independent insert alternative (alternative 1) is the live one.
* `PM03` alternative 0, pattern `self._missing = set(missing_reachable(self.path, self.root))`:
  the store's computation at `tools/report-landing-audit.py:129` reads
  `self._missing = missing_reachable(self.path, self.root)` (no `set(...)`
  wrapper; the function returns the `(missing, opaque)` pair), so the wrapped
  spelling is dead and alternative 1 is the live one.
* `PM07` alternative 1, pattern `    roots = present_commits(repo)\n`: the
  auditor has `present_roots` (`tools/report-landing-audit.py:717`) and no
  `present_commits`; `grep -n "present_commits" tools/report-landing-audit.py`
  returns nothing.
* `PM07` alternative 2, pattern `("--no-object-names",\s*)root`: the walk at
  `tools/report-landing-audit.py:758` spells the argument list as
  `"--objects", "--missing=print", "--no-object-names", *extra,` and the second
  walk at line 1539 uses `"--no-object-names",` followed by other arguments, so
  the `root` spelling is dead.

Every one of the four is a fallback alternative that the instrument never
reaches, because an earlier alternative of the same mutant already matches
exactly once. None of them can stop a mutant from applying today.

## Cross-check with the instrument's own anchor mode

The instrument already exposes a no-grid anchor report. Running it (read-only;
no grid run, no source file written) reproduces my numbers exactly:

```
$ cd /home/vgpnk/Projects/shokunin/kama-shokunin
$ python3 tests/report-audit/promisor-mutants.py --anchors tools/report-landing-audit.py --json
exit 0
PM01-blanket-metadata-refusal [('regex', 0), ('insert', 1)] applicable 1 compiles True
PM02-blanket-unknown-refusal [('insert', 1)] applicable 0 compiles True
PM03-skip-required-object-availability [('regex', 0), ('regex', 1)] applicable 1 compiles True
PM04-accept-unavailable-referenced-object [('regex', 1), ('regex', 1)] applicable 0 compiles True
PM05-ignore-second-repo [('regex', 1), ('regex', 1)] applicable 0 compiles True
PM06-swallow-actual-read-error [('insert', 1)] applicable 0 compiles True
PM07-full-all-missing-gate [('regex', 1), ('regex', 0), ('regex', 0)] applicable 0 compiles True
PM08-no-lazy-fetch-review-only [] applicable None compiles None review-only
PM09-peel-bare-full-hash-lookup [('replace', 1)] applicable 0 compiles True
PM10-ignore-opaque-nonleaf-missing [('insert', 1)] applicable 0 compiles True
PM11-any-hole-refusal [('insert', 1)] applicable 0 compiles True
```

Saved as `.ufo/waves/round-25/build/out/ExecPromisorAnchorCount/instrument-anchors.json`.

## Answer for C1's scope disclosure

* Mutant-level (the instrument's own apply rule, the level that decides whether
  a run can happen at all): **no stale anchors**. 10 of 10 executed mutants have
  an alternative that matches exactly once, and the mutated source compiles for
  every one of them. The promisor instrument is not part of C1's counted set and
  does not need a re-anchor.
* Edit-level: 4 of 16 edits match zero times (PM01[0], PM03[0], PM07[1],
  PM07[2]); none matches more than once, so there is no "two call sites" style
  ambiguity of the M17 kind here. Two mutants (PM04, PM05) have two live
  alternatives that both match exactly once; the instrument uses the first and
  keeps the second as a fallback, which is a robustness property, not a defect.
* Contrast with the C1 finding on `tests/report-audit/isolation-mutants.py`
  (M11 zero matches, M17 two matches): there the registered counting command
  aborts with exit 2 before any mutant runs. Here nothing aborts: the
  promisor inventory is fully applicable at base 147f5bdd.

## Risks and limits

* The four dead fallback edits are latent drift exposure: if the live
  alternative of PM01, PM03 or PM07 ever drifts, the mutant falls back to an
  edit that no longer matches and the mutant then reports
  `could-not-evaluate` instead of a kill. I did not change the instrument
  (read-only seat; the repair seat owns the instrument files).
* I did not run the promisor grid, as instructed; no kill or survival claim is
  made here. Only anchor applicability and compilability are reported.
* The auditor I measured is the one at base 147f5bdd, which is also the current
  lane HEAD content; a future landing that edits the auditor could change the
  counts, so the counts are tied to the sha256 above.

## Files written by this seat

* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/build/advice/ExecPromisorAnchorCount.md` (this report)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/build/out/ExecPromisorAnchorCount/anchor-count.py` (the counting script)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/build/out/ExecPromisorAnchorCount/anchor-count.json` (machine-readable counts)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/build/out/ExecPromisorAnchorCount/anchor-count.txt` (the run output above)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/build/out/ExecPromisorAnchorCount/instrument-anchors.json` (cross-check output)

Scratch (outside the lane): `/fast/scratch/hyaku/kama-r25/ExecPromisorAnchorCount/clone`
(a `git clone --no-hardlinks` of the lane, used only to read the base revision
with `git show`; no checkout, no branch, no commit).

## Tools

No tool was installed or upgraded: the measurement used only the system
`python3` (standard library: `importlib`, `json`, `re`, `hashlib`,
`subprocess`). Nothing was added to `~/.config`, `~/.omp`, or any systemd unit.
