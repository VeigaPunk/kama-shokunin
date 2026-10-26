# Simp1Tool — YAGNI review of `tools/append-only-audit.py` v3 (C1, round 48)

**Verdict: no defect — v3 carries eight pieces of dead or doubled code (3 net lines, 9 hunks, stdout/stderr/exit/JSON byte-identical everywhere I ran it); and no selftest case tests nothing distinct (32-mutant kill matrix: every one of the 27 cases is killed by at least one mutant), so this review proposes zero test deletions.**

Lane tree untouched; the tool under review is `ec9c6d206fccfd9b9b04526b54da34207c48ab9f0768c3285128cd59fcf60f72`
(`tools/append-only-audit.py` at `380bcdff9c8af06997c482f6eb03db926a794a2b`), reviewed from a
`git clone --shared` copy in my scratch. The proposal is a unified diff, not an edit:
`out/Simp1Tool/simplify.diff` (applies with `patch -p1` from the lane root; verified against a
mirror of the lane tree, result `cmp`-equal to `append-only-audit-after.py`).

## 1. What the scan found (and what it did not)

| scan | result |
|---|---|
| `uvx pyflakes 4.0.3 work/before.py` | exit 0, no output — no unused import, no unused local, no redefinition |
| AST load-count of every top-level name | every function/class/constant has ≥1 load; **no unused helper** exists |
| doubled work / doubled spelling / dead branch, by reading | 8 items (§2) |

So the "unused helpers" half of the item is empty. v2 left no orphan function behind: the surviving
v2 weight is prose (§5 item 1) and three unreachable conditions (§2 items 3, 6, 8).

## 2. Proposed deletions (8 items, 9 hunks, 898 → 895 lines)

`file:line` is the lane file at `380bcdff`.

| # | line | dead weight | why it is provably dead | evidence |
|---|------|-------------|-------------------------|----------|
| 1 | `:117` | `HUNK` captures the plus-side start, `\+(\d+)`, which nothing reads | the only reader (`deleted_lines`) reads groups 1, 2 and the plus **count**; the plus start is never used to place anything | `grep -n "m\.group(" …` → `group(1)`, `group(2)`, `group(4)` only; behaviour checked by the `declared-file-removed` case (hunk `+0,0`) and the one-line-hunk twins, both byte-identical after the change |
| 2 | `:284` | after #1 the plus count becomes group 3 | mechanical consequence of #1 | idem |
| 3 | `:162` | `if not lines or lines[0] != HEADER` — the `not lines` conjunct | `str.split("\n")` never returns `[]`; `"".split("\n") == [""]`, so the empty contract already fails on `lines[0]` | `python3 -c 'print("".split("\n"))'` → `['']` |
| 4 | `:218` | `if region[0] == "*"` — the same sentinel spelled twice, since `WHOLE = ("*",)` at `:120` | `parse_region` returns exactly `WHOLE` for a whole-file row; comparing against the constant is the same test with one spelling | `WHOLE` has one load site (`:142`, the return); no other `"*"` sentinel exists |
| 5 | `:261` | `seen = {t.strip("\n") for t in seen}` — a second normalisation of the NUL-delimited name set | `git log -z --name-only` emits no newline byte at all, so the strip is the identity on every member; the comprehension on `:260` already skips empty members | probe on 1 564 605 bytes of this history (`git log -z --format= --name-only --no-renames 380bcdff…`): `raw.count(b"\n") == 0`, so no member can carry a byte the strip would remove |
| 6 | `:305-306` | `if not specs: return {}` in `Repo.blobs` | both call sites pass a non-empty list (`:402` one spec, `:405` the non-empty window); and even a `[]` call is answered correctly by git (` missing`, rc 0) and by the `zip` | `printf '\n' \| git cat-file --batch-check='%(objectname) %(objecttype)'` → ` missing`, rc 0 |
| 7 | `:401`, `:403`, `:412` | `dl` is traversed twice: a comprehension builds `D`, then the region loop builds `G`; `K` is computed from `D` before `G` exists | `D[text] += 1` inside the existing loop builds the identical multiset, and `K = r.lines(pb) - D` only needs `D` after the loop | differential §3 |
| 8 | `:886` | `if a.contract and files is None:` — the second conjunct is always true there | the exclusivity check at `:880-882` returns 2 when both `--files` and `--contract` are given, so at `:886` `a.contract` implies `files is None` | read, and `both-modes` in the differential returns 2 in both versions |

The diff also keeps two things that look like duplication but are not: `expand`/`unmatched` share a
tree walk that cannot be merged (different result shapes), and `deleted_lines` re-deriving counts
that `--numstat` also gives is the frozen cross-check, not redundancy.

## 3. Evidence that behaviour is preserved

All commands in `out/Simp1Tool/commands.txt`; `$S` is my scratch.

| check | result |
|---|---|
| `--selftest --scratch` before | exit 0, `AOA_SELFTEST pass=27 fail=0` (`selftest-before.out`) |
| `--selftest --scratch` after | exit 0, `AOA_SELFTEST pass=27 fail=0` (`selftest-after.out`) — output files `cmp`-identical, 570 bytes |
| lane run at `380bcdff…` (text) before/after | exit 0 both; **byte-identical**, 1 003 bytes, sha256 `7b5c065c834d58ca…878e4` (`lane-before/after-380bcdff.out`) |
| lane run at `380bcdff…` `--json` before/after | exit 0 both; **byte-identical**, 7 085 bytes, sha256 `2cfcafe942308075…64ce1` (`lane-before/after-380bcdff.json`) |
| that JSON's summary | `commits=311 files=89 events=5 restored=5 partial=0 unrestored=0 ungraded=0 ungraded_lines=89 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=0` — the build's own numbers |
| differential `work/differential.py` | **34 comparisons, 0 differences**: 6 named revs (`380bcdff`, lane `b85783e8`, `3a09a1d9`, `33e00582`, `383f1fc7`, `b85895f4`) × (text, `--json`), 8 revs spread over the first-parent history × 2, plus `--contract`, `--files` (text and `--json`), `--threshold 0` → 2, both-modes → 2, missing rev → 2; each compares stdout, stderr and exit code (`differential.txt`) |
| differential over older history | 14 revs spread over 311 commits **with the tip contract passed explicitly**, so the grading path really runs (exit 1 = regressed/partial events on those revs): **0 differences**, JSON byte-equal (`differential-oldhistory.txt`) |
| patch provenance | `patch -p1` of `simplify.diff` on a mirror of the lane tree → `cmp`-equal to `append-only-audit-after.py` |
| `py_compile` + `pyflakes` on the proposal | exit 0, no output |
| cost | median 0.734 s (before) vs 0.744 s (after), 5 runs each — within noise; no performance claim is made |

Why byte-identity is the right bar: the frozen C1 counter (`tools/round48-append-audit-v3-check.py`)
compares the tool's `files`, per-event `EVKEYS`, `SUMKEYS` and exit code against its own
recomputation, and reads the tool's source from the tip tree (counter `:647-648`). Identical JSON
plus identical exit therefore preserves the counter's verdict by construction; I did not re-run the
frozen counter (it would only re-measure the build's own tool).

## 4. Selftest: every case is distinct (no deletion proposed)

I built 32 single-defect mutants of the v3 grading logic (`out/Simp1Tool/mutants.py`: threshold
`<=` and a hard-coded threshold, a zero-deletion guard, `deleted=graded`, restored off-by-one,
`restored_by` on ungraded, ungraded status, eligibility `>=`→`>`, titles-for-eligible, only-prefix
`startswith`→`in`, section `## `→`# `, no `rstrip`, `split_lines` keeps the final segment, `K`
without `D`, no `max(0, …)` clamp, set instead of multiset, 2-commit window, hunk-count check
skipped, `vanished` reports everything, binary read as zero, `binds` without negation/token test,
exempt without `re-derived`, four `exit_code` variants, deleted position `+1`, 5→4 cell contract,
whole-file region, CRLF contract accepted, no `unmatched`, no `vanished`, `numstat` without pathspec)
and ran `--selftest` under each: `out/kill-matrix.txt`.

**Result: 27 cases, 27 killed at least once; 10 cases have exactly one kill; the widest is `clean`
with 9.** No case tests nothing distinct, so the honest YAGNI answer is to delete none.

Near miss worth recording, because it is the one deletion I nearly made: `no-deletion` looks
subsumed by `below-threshold` (both assert `events == []` and exit 0 through the same
`if ns[f] < threshold: continue`). It is not. The mutant `if 0 < ns[f] < threshold: continue`
(the "someone adds a truthiness guard" defect) **fails `no-deletion` and passes `below-threshold`**
— `no-deletion` is the only case pinning "a pure append never forms an event". Likewise
`below-threshold` is the only case killed by a hard-coded `ns[f] < 5`. Both stay.

## 5. Candidates considered and NOT deleted (calibration)

1. **The v2 docstring block, `:36-82`.** `:36` says `v2 (round 47) text, kept:` — explicitly marked
   historical, so it stays. But the marker's scope is mixed: the block after it also holds the
   still-normative `Definitions` list (`:51-69`) that the v3 header calls "beyond v2". A future
   round that wants to shorten prose should split the marker, not delete the block — I did not
   touch it, and `:53`'s four-cell header is *correct history* (v2's header had no `region` cell),
   superseded by the v3 header at `:25`, not a defect.
2. **`RULES` / the `rule` cell (`:116`, `:164-166`).** Validated, never graded (`_rule` at `:212`).
   Kept: the cell is contract data, the validation is what makes a typo'd rule fail, and the frozen
   C1 contract leg depends on rows parsing.
3. **`--files`, `--threshold`, and the `--files`/`--contract` exclusivity error.** No lane file
   invokes either flag (grep over `tools/*.py`, the round-48 controls and `SKILL.md`); both are
   documented as the interface at `SKILL.md:1473` (v3 row) and `:1453` (v2 row), and 16
   `audit(…, files=F)` calls across the 27 fixtures use the internal `files=` mode. Retiring the
   flags alone would need a `SKILL.md` correction entry, which is outside this seat's write scope;
   the internal parameter must stay either way. Deferred, recorded here rather than done.
4. **`expand`/`unmatched` each calling `tree_paths` (`:247-255`).** One duplicate `git ls-tree` per
   audit, measured at 0.0074 s of a 0.734 s run (1 %). Rejected: two signature changes for a
   percent, and the helpers keep a shape (`(repo, rev, patterns)`) that reads better.
5. **The `"region"` key in each `declaration` dict (`:214`).** Unread by the tool (`render` uses
   `path`/`declared_at`/`reason`) and unread by the C1 counter (`path`, `ok`). Kept: it is the only
   place the JSON says which row kind failed, and deleting an output key costs debugging value to
   save one string.

## 6. Tradeoffs of what the diff does remove

- #6: the guard's *intent* (skip the subprocess) is lost. No caller passes `[]`; with `[]` git is
  invoked once and answers ` missing`/rc 0, which the existing `zip` turns into `{}` anyway.
- #7: `D` now accumulates inside the region loop, so a reader has to see that `D[text] += 1` runs
  before the two `continue`s while `G` does not. One loop instead of two; the JSON is identical.
- #1/#2: group numbers shift by one; any later use of the plus-side start must use group 3 (there is
  none today).
- Net: 3 lines out of 898. Small, deliberate: the rest of the file is the historical docstring and
  27 fixtures, both refused above for evidence-backed reasons. Schema stays `append-only-audit/v3`
  — nothing observable changed, so no version bump and no docstring edit is proposed.

## 7. Tooling record

- `uvx pyflakes 4.0.3` (uv 0.13.0, ephemeral under `~/.cache/uv`), reason: unused-name scan. No
  system install, no `pacman` transaction, nothing written to a PATH directory.

## 8. Artifacts

`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/Simp1Tool/`

- `simplify.diff` — the proposal (9 hunks); `append-only-audit-before.py` / `-after.py` — the two files
- `selftest-before.out`, `selftest-after.out` — `pass=27 fail=0` both, byte-identical
- `lane-before-380bcdff.{out,json}`, `lane-after-380bcdff.{out,json}` — byte-identical pairs, exit 0
- `differential.txt` (34 comparisons), `differential-oldhistory.txt` (14), `kill-matrix.txt` (27×32)
- `mutants.py`, `differential.py`, `commands.txt` — reproduction harness and the exact command list

Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/Simp1Tool.md`
