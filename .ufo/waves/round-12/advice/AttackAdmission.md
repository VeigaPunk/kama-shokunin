# AttackAdmission — is D1 repair causal calibration or paperwork?

Author-dispatched critic seat, round 12. Static review only. This is **not**
an outside review. No runs of `fidelity.py`, `reproduce.py`, census, builds or
tests: those files did not exist when I reviewed, and unrun is not passing.
The evidence below comes from file reads and read-only `git show`, `git
cat-file`, `git ls-tree`, `git hash-object`, `git replace -l` and `sha256sum`.
Tools installed or updated: none.

## Axes

The claim axis is calibration (7 → 7, delta 0). Operability is affected only if
the gate is registered as a capability, and it is not. Freshness, depth,
coverage and adjacency are untouched. The judgement trends (quality and
discernment) are at risk if the count is presented as improved judgement.

## Verdict (bounded)

The count **"old auxiliary snapshot mismatches 1 → 0" is paperwork by
itself.** The calibration improvement that is actually causal is narrower:

1. A committed, fail-capable instrument that reports source correspondence
   separately from digest integrity.
2. An erratum at the place where round 11 overstated fidelity.

C1 is admissible only if it is framed that way, with its denominator stated
(see the correction below). Without that framing it repeats the round-11
mistake one level up: a green check that is true by construction is being
presented as evidence.

## Strongest sustained weakness: the measured delta carries no new information

**CE1 — the result after the fix is true by construction.** The new snapshot
is written from the `git show 2f7303c…:corpus/SOURCES.md` bytes, as the spec
requires. The checker then compares the snapshot against those same bytes, so
"0 mismatches" follows from how the file was made; nothing was discovered. The
only output that could fail is the old snapshot reporting 1. That was already
measured, with both hashes, by the round-11 closure
(`corpus/lessons/round-11-verifier-spotcheck.md:101-110`). I reproduced it
read-only: the git blob is `9dc40d25…093a` (18,898 bytes, 60 lines) and the
frozen copy is `52665cf2…42fa1` (18,793 bytes, 62 lines). The diff is line 55
truncated plus an appended marker,
`[Some lines truncated … artifact://1157 …]`.

**CE2 — no claim or number depends on the defective file.**
- `measure.py`, `reproduce.py`, `claims.json` and `acceptance.json` from round
  11 contain no reference to `SOURCES` (grep found 0 matches).
- The file's only consumer was the `census --file` frozen-before record
  (`sources-census-final.json:3-5`). Its counts (30, A27/C3, 17/8/5) were
  independently matched from the actual blob by the closure (`:112-118`).
- The closure classifies D1 as status-neutral: "none changes the two verified
  claim deltas" (`:204`).

So the repair changes no recorded measurement.

**CE3 — the denominator was chosen after the fact (KQ12).** KQ12
(`corpus/QUALITY.md:39`) requires claims to state their fixed denominator and
any prior overlapping coverage. "1 → 0" has a denominator of exactly the one
file D1 already named. I checked the whole population read-only, comparing
each round-11 `frozen/expected.json` input against `git show 2f7303c:<path>`:

| Input class | Count | Result |
|---|---|---|
| Knowledge files | 9 | All correspond (sha256 equal) |
| `corpus/SOURCES.md` | 1 | Mismatch (D1) |
| `.ufo/waves/round-11/legacy-baseline.json` | 1 | Authored in round 11; not present at `2f7303c` (`git cat-file -e` exit 128). Not git-sourced, so correspondence does not apply |

The closure had already done this 10-input check by hand (`:91-99`), which is
prior overlapping coverage. Round 11's `frozen_digests_verified: 11`
(`acceptance.json:4`) is therefore integrity 11/11, correspondence 9/10, and
1 input where correspondence does not apply.

**CE4 — the lane's own precedent.** In round 5, `SCORECARD.md:90` set
calibration to *unchanged* with the reason that "correction of overclaims is
not proof of externally calibrated judgment". It also labelled a sibling
mismatch count of 3 → 0 a "local documentation delta". Fixing one overclaimed
receipt fits that precedent. Only the instrument and the correction of the
claim site go beyond it.

## Counterexample against the instrument (fixable defect)

**CE5 — a manifest can redirect the authority to a real blob that matches the
truncated copy.** I observed that
`git show fe57cc8:.ufo/waves/round-11/frozen/before/corpus/SOURCES.md |
sha256sum` returns `52665cf2…42fa1`, the truncated copy itself, stored in
immutable history. Suppose `fidelity.py` takes `source_commit`/`source_path`
from the manifest (the spec says the manifest "pins … source commit/path").
Then this manifest reports **clean (exit 0)** for the old D1 snapshot, using
only real objects:

```text
source_commit:   fe57cc8a01acba9b6d7ed20e11b4914dfb68d903
source_path:     .ufo/waves/round-11/frozen/before/corpus/SOURCES.md
snapshot_sha256: 52665cf2d648112be2683c61485d42da1bf1dc859ea1df41d857672c60142fa1
```

That run would make D1 look correct again. The spec's coherent-mutation attack
mutates only the snapshot and its digest. It does not cover this stronger
redirect.

**CE6 — hardening data for the source-pin gap.** ReviewSourcePin's
`SOURCE_BLOB_OID` is listed as "NOT observed". I observed it:
`git --no-replace-objects show 2f7303c:corpus/SOURCES.md | git hash-object
--stdin` returns `7de1360655eadada356fe110813c6e1338142551`, equal to
`git ls-tree 2f7303c corpus/SOURCES.md`. `git replace -l` lists 0 entries.

## Impacted axes

- **Calibration:** the risk is an overclaim. If the round-12 axis verdict says
  "improved" because of the count, that is exactly the integrity-as-evidence
  error D1 names.
- **Quality and discernment trends:** affected the same way.
- **Operability:** no harm, provided the SKILL registry row stays labelled as
  lane-local evidence (it currently is, in the worktree `SKILL.md` diff).
- **No other axis is harmed.**

## Smallest safe correction

1. **Rescope the C1 wording.** Applies to `claims.json`, `SCORECARD.md` §Round
   12 and `lessons/round-12.md` §Declared claim; no code change needed. Say
   that the denominator is 1 file, preselected by D1. Say that the closure had
   already covered the population: 10 git-sourced inputs, 9 corresponding, plus
   1 round-authored input where correspondence does not apply. State that
   "after = 0" is a construction check. Put the calibration credit on two
   things: the separated integrity/correspondence instrument with controls that
   are shown to fail, and the erratum.
   - A stronger optional fix: a constant table in `fidelity.py` covering all 10
     git-sourced paths and their blob sha256 values. That replaces the
     preselected denominator with the full population. Only the Fidelity owner
     can do this.
2. **Authority constants, not manifest fields.** The manifest's
   `source_commit` and `source_path` must equal the constants in `fidelity.py`
   (`2f7303c…`, `corpus/SOURCES.md`, blob sha256 `9dc40d25…`, blob OID
   `7de13606…`). Any difference must exit 2 and must never be followed.
   Add the CE5 manifest to the runner's isolated attacks, with the expected
   result non-zero and not clean. Read git with `--no-replace-objects`.
3. **Erratum at the overstatement site.** `LOG.md:547` says "frozen source
   bytes … are in `.ufo/waves/round-11/frozen/`". The worktree has no LOG
   change yet; I checked with `git status`. Append a dated erratum that names
   the truncated `52665cf…` copy, the actual `9dc40d25…`, the new snapshot path,
   and the fact that `frozen_digests_verified: 11` was integrity only. The
   round-12 lesson's Gate row names the hashes but does not correct the
   original sentence.

## Checks for L1 (not run here)

1. Run `git show 2f7303c:corpus/SOURCES.md | sha256sum` and
   `sha256sum .ufo/waves/round-12/frozen/corpus/SOURCES.md`. Both should give
   `9dc40d25…`.
2. In an isolated temp copy, give `fidelity.py` the CE5 manifest together with
   the old snapshot. Any exit 0 rejects C1.
3. Grep `fidelity.py`: the values used for authority must not come from the
   manifest's `source_commit`/`source_path`, and no CLI flag may override them.
4. Old snapshot with no manifest should exit 1 (`source_mismatch`). Coherent
   snapshot+manifest mutation should exit 1. Tamper only should exit 2.
   Unavailable source should exit 2.
5. A LOG erratum should exist naming both hashes.
   `.ufo/waves/round-11/frozen/expected.json`, `acceptance.json` and the old
   frozen tree must be byte-unchanged against `79fa257`.
6. The final SCORECARD/report verdict wording should credit the instrument and
   the erratum, not the 1 → 0 count, and keep 7 → 7.
