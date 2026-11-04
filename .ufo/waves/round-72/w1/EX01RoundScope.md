# EX01RoundScope — C1 `round-scope` instrument (kama round 72, wave 1)

Seat: leaf executor, one item (C1). Frozen claim read in full from
`plans/round-72-claims.md` before any work. No lane file outside my assignment was
touched: I wrote `tools/round72-round-scope.py` and this seat's wave dir only.
`tools/pre-report-gate.py` (EX03), `SKILL.md`, `SCORECARD.md`, `LOG.md`, `corpus/` were
not edited; the freeze plan was not edited.

## What was built

`tools/round72-round-scope.py` — one git-state instrument, three fixed cases, one verdict line.

CLI: `--repo PATH` (default `.`), `--round N` (required unless `--selftest`), `--tip REV`
(default `master`), `--lane NAME` (default: repo dir name minus a trailing `-shokunin`;
recorded in `--json` only), `--allow PATH` (repeatable, default empty; exact path or a
trailing-`/` directory prefix; validated, bad entry = exit 2), `--work DIR`, `--selftest`,
`--json`.

- `--repo` is resolved through `git rev-parse --show-toplevel`; every git call names
  `-C <toplevel>`, so findings are repository-root-relative porcelain paths (verified for a
  subdirectory invocation).
- A `label`: `git cat-file -e <tip>:plans/round-<N>-claims.md`, then `cat-file -t` (must be
  a blob), then `cat-file -p`: the first markdown heading must name round `<N>`
  (`round[ _.-]*<N>` with a right word boundary, so `round 720` does not match 72).
  Distinct details: `status=absent`, `status=not-a-blob`, `status=no-heading`,
  `status=heading-mismatch heading=...`.
- B `stray`: `git status --porcelain -uall` over the whole repo; one finding per unallowed
  path, `detail = "<path> status=<XY>"`. Porcelain C-quoting is decoded (octal escapes) and
  rename/copy records are split into source and destination.
- C `ignored`: `git status --porcelain -uall --ignored -- .ufo/waves/round-<N>`; every `!!`
  record is one finding. No allow-list escape (frozen non-goal).
- Output: `ROUND_SCOPE_FINDING <case> <detail>` per finding (case order label, stray,
  ignored; details sorted) then `ROUND_SCOPE round=<N> cases=3 findings=<f>`.
- Exit: `0` clean, `1` findings, `2` could-not-evaluate (CLI misuse, `--repo` not a git
  repository, `--tip` not resolvable to a commit, a failing git call, unbuildable fixture).
  A scored run never exits 2 for a finding.
- `--selftest`: throwaway git repos under `--work` (must be absent or empty) or a fresh
  TMPDIR dir; every fixture asserts its toplevel before the first commit and commits with
  `-c user.name=fixture -c user.email=fixture@invalid` (no `git config`). Fixture tree and
  the three defect mutations mirror the pre-score control harness
  `controls/round-scope-control.py`, plus wrong-round heading, heading-less plan,
  allow-listed stray, allow-listed directory, rename/quote parsing, subdir invocation,
  unresolvable tip, bad allow entry, non-git dir, CLI misuse and `--json` round-trip.

## Frozen predicate line (verbatim, 472 bytes, one line)

```
`python3 tools/round72-round-scope.py --repo <lane> --round <N> --tip <rev>` prints one `ROUND_SCOPE round=<N> cases=3 findings=<f>` line and exits 0 only when the round's frozen claims plan `plans/round-<N>-claims.md` exists at `<rev>` with a first heading naming round `<N>`, no path outside the declared record allow-list is uncommitted, and no path under `.ufo/waves/round-<N>/` is git-ignored; it exits 1 naming every finding as `ROUND_SCOPE_FINDING <case> <detail>`.
```

It is the module's `PREDICATE` constant and is byte-equal to the plan's C1 blockquote at
lane tip `a3cc39f0` (committed blob `7642c3a1`, plan sha256
`39f4ddbcd084c05213dd389decaa997e7128a7d1f8a7aebe325fe1dfdc6ad933` — the exact line
`controls/freeze.txt` records) and to the current worktree plan bytes (sha256
`c656e66b…`, whose only delta from the committed plan is freeze amendment 2 in C2). The
selftest carries the comparison as the `predicate` arm; receipt `predicate-committed.out`
records `PREDICATE_MATCH committed=1 worktree=1 len=472 lines=1`.

## Disagreement with the seat spec (freeze not edited)

The seat text names case A `prompt` and anchors it on
`git cat-file -e <tip>:.ufo/prompts/<lane>-round-<N>.md`. The frozen plan carries a
**pre-score** freeze amendment (22:45 -03, before any seat returned a score) that moved
case A to the lane-owned `plans/round-<N>-claims.md` with a first-heading round check and
renamed the case `label`, because the fleet prompt is not a lane path. Observed:
`git -C <lane> cat-file -e master:.ufo/prompts/kama-round-72.md` → exit 128 (`path … does
not exist in 'master'`). I implemented the frozen plan's amended case A — the seat text
itself says the predicate blockquote is the frozen sentence — and kept the assigned receipt
name `kill-prompt.out` for the missing-plan kill. Implementing the pre-amendment anchor
would make every real-lane run exit 1 on a path that cannot exist in a lane tip, which is
the vacuous-unexecutable state the amendment removed. Report, not edit.

## Receipts — `.ufo/waves/round-72/w1/EX01RoundScope/`

Each receipt carries a `# tip=<40-hex>` header, the verbatim module output, and `EXIT=<n>`.

| receipt | fixture / repo | command | exit |
|---|---|---|---|
| `selftest.out` | lane, `--repo <lane>` | `python3 tools/round72-round-scope.py --repo <lane> --selftest --work <scratch>/selftest-work` | **0** (`pass=16 fail=0`) |
| `clean.out` | fixture `clean` | `… --repo <fixture> --round 72 --tip master` | **0** (`findings=0`) |
| `kill-prompt.out` | fixture `label-missing` | same | **1** (`label … status=absent`) |
| `kill-label-wronground.out` | fixture `label-wrong-round` | same | **1** (`label … status=heading-mismatch heading=kama round 71 — frozen claims`) |
| `kill-stray.out` | fixture `stray-root` | same | **1** (`stray stray-note.md status=??`) |
| `kill-ignored.out` | fixture `ignored-in-wave` | same | **1** (`ignored .ufo/waves/round-72/scratch.log`) |
| `allow.out` | fixture `stray-root` + `--allow stray-note.md` | same + allow | **0** (`findings=0`) |
| `real-base-d30a8696.out` | shared clone at `d30a8696` | `… --repo <clone> --round 72 --tip d30a8696` | **1** (`label … status=absent`) |
| `real-freeze-090a0b25.out` | shared clone at `090a0b25` | `… --tip 090a0b25` | **0** |
| `real-amend-a3cc39f0.out` | shared clone at `a3cc39f0` | `… --tip a3cc39f0…` | **0** |
| `real-worktree-master.out` | live lane worktree | `… --repo <lane> --round 72 --tip master` | **1** (47 findings at capture) |
| `real-worktree-master-allow.out` | live lane worktree | same + `--allow .ufo/waves/round-72/ --allow plans/round-72-claims.md --allow tools/round72-round-scope.py` | **1** (7 findings at capture) |
| `predicate-committed.out` | committed + worktree plan | inline extraction/compare | n/a (data) |

All fixture receipts were produced twice and the stdout/exit pair compared (deterministic).
Each run was `PYTHONDONTWRITEBYTECODE=1`; no bytecode was written for this module.

## Measured real-lane results

- `d30a8696` (the pre-freeze base the control receipt names) → exit 1, one `label` finding:
  the freeze plan does not exist before the freeze commit. The counter is not vacuous at
  the base the claim's before-measurement used; the freeze commit adds the anchor.
- `090a0b25` (freeze commit) → exit 0, `findings=0`.
- `a3cc39f0` (current lane master, the pre-score anchor amendment) → exit 0, `findings=0`.
- Live worktree at `a3cc39f0`, capture time: 47 findings — every untracked wave record of
  every live seat, my own receipts, and 7 modified/untracked non-receipt paths
  (`corpus/QUALITY.md`, `corpus/README.md`, `corpus/SOURCES.md`,
  `corpus/knowledge/receipt-tip-binding.md`, `corpus/lessons/round-72.md`,
  `tools/pre-report-gate.py`, `tools/round72-receipt-tip-binding.py`). With the round's
  record paths allow-listed, 7 findings remain: those sibling in-flight edits. That is the
  arm working as frozen: the gate is green only after the round's records — and any sibling
  edit outside the declared allow-list — are committed or declared.

## Wiring note for gate arm 6 (EX03 owns `tools/pre-report-gate.py`; not edited)

`python3 tools/round72-round-scope.py --repo <repo> --round <N> --tip <tip>` — exit 0 is
the arm pass, exit 1 is a named failure, exit 2 is "could not evaluate" and must not be
scored as a pass. Because case B is whole-repo, the arm must run after the round's records
are committed or with `--allow` entries the plan declares; mid-wave it fails by design.
Receipt label for the plan's "same sentence in three places" is this document's predicate
block plus the module constant and `kill-prompt.out`'s `label` finding.

## Risks / limits

- Whole-repo case B makes the arm sensitive to any seat's scratch writes outside the wave
  dir (observed: `corpus/*`, `tools/*` in-flight edits). Intended by the frozen sentence
  ("no path outside the declared record allow-list"), but it means the arm cannot be green
  mid-wave.
- Case C has no allow list by design (frozen non-goal); an ignored path under the wave dir
  is always a finding.
- A rename record yields one finding per unallowed path (two for a rename); not exercised
  by the claim's fixture set, covered in the selftest.
- `--lane` is metadata for `--json` only; the frozen predicate has no lane-dependent path,
  so a wrong `--lane` cannot mask a finding.
- `--tip` must resolve to a commit; worktree cleanliness is graded at the worktree
  regardless of `--tip` (documented in the module). A caller grading a clone should check
  out `--tip` first, as the `real-*` receipts do.

## Files written

- `tools/round72-round-scope.py`
- `.ufo/waves/round-72/w1/EX01RoundScope.md` (this report)
- `.ufo/waves/round-72/w1/EX01RoundScope/{selftest,clean,kill-prompt,kill-label-wronground,kill-stray,kill-ignored,allow,real-base-d30a8696,real-freeze-090a0b25,real-amend-a3cc39f0,real-worktree-master,real-worktree-master-allow,predicate-committed}.out`

Nothing committed, nothing staged. Scratch `/fast/scratch/hyaku/kama-r72/EX01RoundScope`
(clone + fixtures, ~512 MB) is deleted before yielding.
