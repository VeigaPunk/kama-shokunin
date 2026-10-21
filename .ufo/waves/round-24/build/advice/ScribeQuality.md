# ScribeQuality — KQ35 draft (round 24 build)

**Verdict: draft complete.** KQ35 is drafted in the `corpus/QUALITY.md` four-column format with
the round-23 closure named, the blanket-refusal mutant defined, and its kill requirement
pinned to the complete-local paired row. Nothing was applied: `corpus/QUALITY.md` is untouched
(177 lines at the observed base, highest ID KQ34). A candidate unified patch is provided for
L1; it applies cleanly.

Seat: `KamaR23-2.ScribeQuality` (scribe, leaf; no subagent dispatch). Observed base
`0df800e896f6bce285a81e794ad4ae1d1e6c3a71`; scratch clone
`/fast/scratch/hyaku/kama-r24/ScribeQuality` at HEAD `d1b9d95` (base + the round-24
preregistration commit, which touches only `.ufo/waves/round-24/preregistration.json` and
`LOG.md`).

## Behavior

Drafted KQ35 as one row for a new `## Criterion added — round 24 (metadata is not missing
evidence)` section appended after the round-23 KQ34 block. The row's operative claims:

1. **Metadata is not missing evidence.** A promisor/partial-clone declaration
   (`extensions.partialclone`, `remote.<name>.promisor`, `remote.<name>.partialclonefilter`, a
   `.promisor` marker beside its pack) is evidence of a transport arrangement, never evidence
   that a required object is absent. A refusal is credited only when the run establishes per
   required object (commit, tree, blob, committed report) that the object is not in the local
   object store.
2. **Refusing a correct complete-state workflow is operability harm even when disclosed.** The
   round-23 closure is named explicitly: it closed C1/D4 by refusing every promisor-marked
   repository with exit 2 and recording that refusal as a declared trade. Disclosure does not
   cure it.
3. **Outcome follows the measured state.** Every required object local → the same substantive
   finding as an otherwise identical full clone (exit 0 clean, or the same exit 1 with the same
   finding kinds). A genuinely unavailable required object → could-not-evaluate exit 2 with a
   reason naming the object and its repository, never a clean or failed verdict. An
   unresolvable citation in a promisor-backed repository → unknown (exit 2) unless the object is
   found locally in another audited repository.
4. **The detector.** A blanket-refusal mutant (repaired auditor + the round-23 unconditional
   metadata refusal restored) must be killed by complete-local paired rows on grid exit 1, with
   the failed rows pasted; a grid that could not evaluate kills nothing.

The draft also names why the round-23 grid could not have killed that mutant (mutual
blindness): F23 refuses in both arms, T01 is a `tradeoff` row that is reported and never
graded, and no complete-local metadata-marked row existed.

## Gates

- **ID collision:** none. `corpus/QUALITY.md:1-177` at the observed base contains rows
  KQ1–KQ34; `grep -o "KQ3[0-9]" .ufo/waves/round-24/build/spec.json | sort | uniq -c` returns
  `1 KQ35`, i.e. this lane is the only round-24 lane drafting KQ35.
- **Format:** one row in the existing four-column table (ID | Admit only when | Reject or limit
  when | Motivating lesson), appended under a new section header; no existing line moved.
- **Anchors:** KQ20 (detector must be able to fail), KQ24/KQ17 (could-not-evaluate is not a
  failed observation), KQ25 (kill credit only on exit 1), KQ32 (trusted-repository limit,
  unchanged), KQ33/KQ28 (unchanged). Each is named with its relation in the draft.
- **Patch applies:** `git apply --check .ufo/waves/round-24/build/out/ScribeQuality/QUALITY-KQ35.patch`
  in the scratch clone → exit 0 ("APPLIES CLEANLY").

## Touched surfaces

- Written: `.ufo/waves/round-24/build/out/ScribeQuality/KQ35.md` (draft, 16 130 bytes).
- Written: `.ufo/waves/round-24/build/out/ScribeQuality/QUALITY-KQ35.patch` (candidate unified
  patch against `corpus/QUALITY.md`, `@@ -175,3 +175,9 @@`).
- Written: `.ufo/waves/round-24/build/advice/ScribeQuality.md` (this report).
- Not written: `corpus/QUALITY.md`, `corpus/lessons/round-24.md`, `corpus/SOURCES.md`,
  `SKILL.md`, `README.md`, `SCORECARD.md`, `LOG.md`, `tools/report-landing-audit.py`,
  `tests/report-audit/*`. No commit, no push, no `.jj` or lane Git index write, no fleet write.
- `advice/swarm-registry.json` (mode 0600, another writer) was not opened.

## Out-of-scope items

- The availability measurement, its deadline, and the paired fixtures are owned by the repair
  and grid lanes (AuditRepair, GridOracle, MutationDesign). I did not evaluate their
  correctness and did not propose a mechanism in the row.
- The r24 policy-row expectation changes (F23 / F06 reason strings, T01's kind) are recorded
  in the draft as notes for L1; I did not change any grid row.
- No network access, no remote clone, no promisor fetch, no execution payload; no probe,
  selftest, grid or mutant run was executed by this seat (the lane contract reserves those
  runs for the assigned lanes).

## Findings (exact)

1. **The r23 closure, named** — `tools/report-landing-audit.py:438-465`
   (`check_history_repo`): `:455-457` raises
   `EvalError(f"{repo}: partial clone (promisor pack)")` for any `.promisor` marker whose
   `.pack` sibling exists; `:462-465` raises
   `EvalError(f"{repo}: partial clone ({key})")` for `extensions.partialclone` or any
   boolean-true `remote.*.promisor`. `tools/report-landing-audit.py:948-950` maps `EvalError`
   to `could-not-evaluate` and exit 2. The refusal is unconditional on content — it fires
   before any check that the audited objects are present locally — while the function's own
   docstring (`:438-443`) states the rule the code does not apply: "whose missing objects
   belong to a promisor remote (absence is not evidence there)".
2. **The r23 closure was disclosed as a trade, not a defect** —
   `corpus/lessons/round-23.md:83-84`: "Declared tradeoffs: partial clones and shallow clones
   are refused even when every cited object is local (grid T01; RevCalibrationAxis,
   CritNoHarm)"; `corpus/lessons/round-23.md:206-209`: "a complete blobless partial clone
   (T01) and a paired promisor pack without promisor config (F23) are refused (exit 2) where
   frozen gave a verdict".
3. **Git itself does not assert what the metadata-based refusal assumes** — `corpus/SOURCES.md`
   row S099 (supersedes S092, opened 2026-10-21, tier A): partial-clone §Handling Missing
   Objects, "no check as to whether the missing object is actually a promisor object is
   performed".
4. **The r23 grid cannot kill the blanket-refusal mutant** — `F23` expects exit 2 in both arms
   (`tests/report-audit/repo-state-grid.py:670`, fixture `:195-212` whose premise is a
   genuinely absent blob); `T01` is kind `tradeoff` (`:689`) and the grid docstring `:13-15`
   says `tradeoff` rows "are reported, never graded"; `C09` (`:679`, fixture `:539-543`) and
   `C10` (`:680`, fixture `:545-549`) carry no live promisor metadata; and no graded row pairs
   a complete-local metadata-marked clone against its full-clone twin. KQ35 requires that pair.
5. **Two exit-2 rows are pinned to metadata reasons** — `REASONS`
   (`tests/report-audit/repo-state-grid.py:695-708`): `"F23-promisor-pack-without-config":
   "promisor pack"` (`:704`) and `"F06-lazy-fetch-command": "partial clone"` (`:698`). Under the
   availability policy both refusals remain correct (the blob for F23, the cited commit for
   F06 — fixture `:272-287` cites a commit that does not exist and proves the lazy fetch ran),
   but the reason must name the unavailable object. These are the policy-row expectation
   changes the round-24 preregistration requires be recorded explicitly.
6. **The mutant family already exists in the r23 runner, in the opposite direction** —
   `tests/report-audit/isolation-mutants.py:46-47` (`M14-promisor-config`), `:64-65`
   (`M22-promisor-pack`), `:75` (`M27-promisor-boolean`), `:78-79`
   (`M29-promisor-pack-pairing`) all *remove* the promisor refusal. The round-24 mutant must
   do the opposite (re-instate the refusal in the repaired auditor), because the round-24
   defect is over-refusal, not under-refusal.
7. **Precedent for the harm class inside r23 itself** — `corpus/lessons/round-23.md:173` (M6):
   "Over-refusal shipped as isolation: the first integration refused any existing info/grafts
   file, so a complete repository with a comment-only grafts file went from a correct frozen
   verdict to exit 2". KQ35 is the same class one level up (the whole promisor class instead of
   one grafts spelling), and the M6 remedy pattern applies: a control row plus a mutant that
   the control kills.
8. **`T01` cannot serve as the complete-local twin** — its fixture
   (`tests/report-audit/repo-state-grid.py:596-602`) is a `--filter=blob:none` clone, which
   genuinely lacks blobs. A "complete local" case needs a full clone that merely *carries*
   promisor metadata, or a partial clone whose required objects are all present locally. This
   is recorded as drafting note 3.

## Unverified

- Every line citation above was read in the scratch clone at the observed base, but **no code
  was executed**: no grid, no mutant run, no selftest, no probe. Behavioural claims about the
  r23 grid's current/frozen arms are taken from the r23 lesson's own measured statements
  (`corpus/lessons/round-23.md`, falsify-wave integration section), not re-measured here.
- That the repaired auditor can actually satisfy the paired-row expectations (that a
  complete-local metadata-marked clone yields the same finding as its full-clone twin) is a
  property of the repair lane's implementation; the criterion constrains the outcome, and this
  seat did not verify that any candidate meets it.
- Whether the r24 grid will pin F06's and F23's refusal reasons to the unavailable object
  (finding 5) is a grid-lane decision; the draft records it as required by the row, not as
  done.
- The round-24 preregistration's `expected_after` items on unknown citations ("exit2 unless
  resolved locally by another audited repository") were read from the preregistration file and
  are reflected in the row; no implementation of that cross-repository resolution was reviewed.

## Tooling

No installs, updates or package transactions were performed. No tool was added or upgraded by
this seat; the only tools used were `git`, `grep`, `diff` and `python3` already present in the
host image (git 2.56.0, Python 3.14.8 per the r23 lesson's environment statement). No
`pacman` transaction was attempted (all pacman transactions are paused for the wave).

## Artifacts

- `.ufo/waves/round-24/build/out/ScribeQuality/KQ35.md`
- `.ufo/waves/round-24/build/out/ScribeQuality/QUALITY-KQ35.patch`
- `.ufo/waves/round-24/build/advice/ScribeQuality.md`
