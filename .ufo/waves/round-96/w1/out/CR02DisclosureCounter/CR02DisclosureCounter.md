# CR02 — attack on the frozen C3 counter (`tools/round96-disclosure-audit.py`)

Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`. Base `5d43528b`, freeze `58001b71`,
amendment 1 `e2fed9f5`, tip `bbdfc930`. No tracked file was modified; all mutants ran in a
`git clone --shared` under `/fast/scratch/hyaku/kama-r96/CR02DisclosureCounter/` (deleted on exit).

**Headline at-tip answers (as asked).**
- Ceiling-comment check at the tip: **passes** (`MAX_STEPS = 5_000_000`, phrase present).
- Formula check at the tip: **passes as a literal substring test**, not as a comparison to the
  wrapper (see B3).
- Capability-row check at the tip: **passes**; `c810f51e` resolves and is an ancestor of tip.
- Base control: **red** (`checks=5 mismatches=2`), but **not for the reasons the claims give** (B2/B4).

Verdict: the aggregate tip/base behaviour is green/red as filed, but **C3 as frozen cannot be
satisfied**: the identity clause and the `met=True` clause are jointly unsatisfiable (B1), and
three of the five checks do not discriminate the filings they are declared to grade (B2–B4).
B1 is a defect, not a tradeoff; B2/B3 are visible in the counter's own bytes; B4 is a defect of
the claims narrative plus one unresolvable evidence path.

---

## B1 (blocker, identity change) — no revision satisfies the frozen predicate

Frozen clause (claims C3, unchanged in the claims file at tip):
`prints ... met=True at the measured commit M3, the counter's bytes identical to this freeze commit.`

Measured:

```
git show 58001b71:tools/round96-disclosure-audit.py | sha256sum
  62c79775c282198e53a02cb3d5eaafe407768f353ec4f4e230108a778694512f  -
git show bbdfc930:tools/round96-disclosure-audit.py | sha256sum
  39ab0575dac980ced568666bd15ffabcee7b7c0c9e91d44338bc69c1b6bb90ae  -
```

The counters are **not byte-identical**: amendment 1 `e2fed9f5` edited this counter after F
(`git show --stat e2fed9f5` → `tools/round96-depth-audit.py`, `tools/round96-disclosure-audit.py`).
The commit message says "restate predicates", but `git diff 58001b71 bbdfc930 -- plans/round-96-claims.md`
is **empty**; `.ufo/waves/round-96/claims.json` contains neither `58001b71` nor `e2fed9f5`.

Using the frozen bytes (identity clause honoured), the audit **never passes at or after F**:

```
frozen audit bytes --rev 58001b71  -> DISCLOSURE_AUDIT checks=5 mismatches=1 met=False  exit=1
frozen audit bytes --rev e2fed9f5  -> DISCLOSURE_AUDIT checks=5 mismatches=1 met=False  exit=1
frozen audit bytes --rev bbdfc930  -> DISCLOSURE_AUDIT checks=5 mismatches=1 met=False  exit=1
frozen audit bytes --rev 5d43528b  -> DISCLOSURE_AUDIT checks=5 mismatches=2 met=False  exit=1
```

Root cause is exactly the one amendment 1 describes: the unanchored regex captures `'5'` from the
prose line `# ... MAX_STEPS = 5 000 000 puts the ceiling ...`. So:

- frozen bytes ⇒ `met=False` always; amended bytes ⇒ `met=True`, but the bytes moved, so the
  identity clause is false. **Both clauses are never true together.**
- K2 ("the counter changes after this commit") is mechanically fired by `e2fed9f5`; C1's counter
  did *not* move (`sha256` of `tools/round96-router-budget.py` is
  `3f6107c3…8069f` at F and at tip), so the lane demonstrably knows how to keep a counter frozen.
- Contradiction inside the claims: C3 line 119 says "C1's counter bytes are immutable after F",
  while C3's own bytes are not.

**Smallest safe correction.** Restate the C3 predicate to bind the counter at `e2fed9f5` (or
refreeze it as `round96-disclosure-audit-v2.py`) **in the claims file**, and reword K2 to
"after the amended freeze". Amendment 1 alone cannot cure this because the binding document still
names `58001b71`. This is a predicate change — L1's decision, not a seat's.

Impacted axis: calibration, and the claim's own identity/provenance; no other claim depends on it.

---

## B2 (defect) — check 2 is dead code and cannot see a false ceiling sentence

Code (`tools/round96-disclosure-audit.py:54`):

```python
if "MAX_TENSORS = 1_000_000" in probe and "the ceiling is 1,000,000" in probe:
    mismatches += 1
```

Neither literal exists in **any** revision: the constant is a tuple element
(`MAX_KV, MAX_ARR, MAX_TENSORS, MAX_META = …, 1_000_000, …`), so `MAX_TENSORS = 1_000_000` never
appears; `git log --all -S "the ceiling is 1,000,000" -- tools/kama-probe.sh` returns **nothing**,
and `git log --all -S "1,000,000" -- tools/kama-probe.sh` also returns nothing. The check has never
fired and cannot fire. Consequences measured:

| mutant (clone tip) | result |
|---|---|
| M1 comment calls 1 000 000 **NON-binding** | `mismatches=0 met=True` — no distinction, as the check is substring-based |
| M2 re-add `(kept for history: the ceiling is 1,000,000 tensor headers)` | `mismatches=0 met=True` — exact comma form required, so the false sentence passes |
| M21 append `# In practice the ceiling is 1 000 000 tensor headers for ordinary files.` (binding prose) | `mismatches=0 met=True` — spaced form passes |

**What this falsifies.** The claims' check (1) says the counter grades that the comment "no longer
names 1 000 000 as the enforced ceiling"; it does not. The base-control narrative says "the old
ceiling sentence still present" — but the base probe's comment contains no `1,000,000`/`1 000 000`
sentence at all (base lines 569–575). The base red (`mismatches=2`) comes from (a) `MAX_STEPS`
4 M and the missing phrase, (b) the round-96 counter not existing at base. So the receipt is red,
but for checks other than the two routed defects.

**Smallest safe correction (if C3 is refiled).** Parse `MAX_STEPS`, compute the enforced ceiling
`MAX_STEPS // 6 = 833_333`, normalise digits in the corrected sentence
(`833 333` / `833,333` / `~833333`) and compare; reject any sentence claiming `1,000,000`/`1 000 000`
as the tensor ceiling in the same paragraph, independent of comma/spacing. Otherwise delete check 2
and print `checks=4` — a dead check that still increments the counter is worse than no check,
because `checks=5` is printed unconditionally.

---

## B3 (defect) — the "docstring vs wrapper literal" check never reads the wrapper

The docstring (line 13) promises the C1 counter's formula "matches the shell wrapper literal".
The code only does two independent greps: `counter` must contain `20 + 25 * npaths` and must not
contain `20 + 15 * ncand` (check 3); `probe` must contain `20 + 25 * npaths` somewhere (check 5).
It never extracts the wrapper line `local limit=$((20 + 25 * npaths))` (probe:871) and never
compares numbers. Measured:

| mutant | result |
|---|---|
| M18 wrapper computes `20 + 15 * npaths`, a comment above it carries `20 + 25 * npaths` | `mismatches=0 met=True` — **the exact defect the check claims to grade passes** |
| M23 docstring says `20 + 30 * npaths`, decoy comment carries the literal | `mismatches=0 met=True` — wrong formula in the docstring passes |
| M3 wrapper literal replaced by `20 + 15 * npaths` (no decoy) | `mismatches=1` — caught only because check 5's substring disappears |
| M19 docstring `20 + 15 * ncand` + decoy literal | `mismatches=1` — caught only by the banned historical string, not by a comparison |
| M24 wrapper line deleted (`local limit=60`), literal gone | `mismatches=1` — caught |

So the counter catches *removal* of the literal, not *divergence* between docstring and wrapper.
The assignment's second question — "a counter whose docstring carries the formula while the
wrapper uses another number (can the counter catch it?)" — is answered **no** whenever the literal
survives anywhere in the file, and the probe currently has exactly one occurrence, so a comment
decoy is a one-line defeat.

**Smallest safe correction (if refiled).** Extract both sides with a regex and compare tuples:
probe `local limit=\$\(\((\d+) \+ (\d+) \* (\w+)\)\)` vs counter docstring
`(\d+) \+ (\d+) \* (\w+)`; require exactly one match on each side. That also removes the
whitespace brittleness (`20+25*npaths` would currently redden).

---

## B4 (defect of provenance / narrative) — check 4 is satisfied by the base and by the stale pointer

Check 4's frozen *narrowed* property ("resolves as a git object and lies at or before the tip")
is implemented correctly: `c810f51e` resolves and is an ancestor of tip; a nonexistent hash (M7
`deadbeefdead`) and a descendant commit (M26, `2e2a3007` on a side branch) both redden. But:

- `f6325660` resolves and is an ancestor of **base** `5d43528b` → check 4 is **green at base**.
  The stale pointer that C3 was opened to close is not detectable, by construction (stale ≠
  non-landing). Restoring it at tip: M6 → `mismatches=0 met=True`.
- K3 reads "a check is true of the base revision too (the instrument cannot discriminate)".
  Literally, **two of five checks are true at base** (check 2 is vacuous, check 4 passes),
  so K3 fires unless it is read as an aggregate rule. That is a claims-text issue for L1.
- Row selection takes the **last** matching line (`for … if "router-byte-decided" in line`).
  M28: real row made stale (`f6325660`) + later decoy row citing `c810f51e` → `met=True`.
  Duplicate authority silently masks the stale row.
- Short prefixes are accepted: M13 `at \`c810\`` → `met=True` (unambiguous 4-char prefix). Not a
  live defect, but a 4-char pointer is weaker provenance than the full hash.
- The same row's **file** pointers do not resolve at tip: `measured/c1-m1b.out` was never committed
  (`git log --all -- measured/c1-m1b.out` empty; no `measured/` tree at tip),
  and `controls/c1-base.out` does not exist at the lane root (the real receipt is
  `.ufo/waves/round-96/controls/c1-base.out`). Check 4 grades only the hash.
- The row's cited counter is still `tools/round95-router-budget.py`, whose docstring at tip still
  reads `20 + 15 * ncand`. The very formula defect the claim says it closes persists in the row's
  cited evidence, and the audit reads only `tools/round96-router-budget.py`.

**Smallest safe correction.** Either grade the row's cited paths at the cited commit (and require
exactly one `router-byte-decided` row), or narrow the docstring/claims to "the hash resolves and
precedes the tip" and reattribute the base red honestly. The first is a real check; the second is
an honest disclosed limit.

---

## Residual robustness (not live defects; report only)

- M25b: a dead earlier `MAX_STEPS = 5_000_000` assignment followed by the real
  `MAX_STEPS = 4_000_000` → `mismatches=0 met=True`. `re.search` takes the first assignment; the
  amendment's anchor does not require uniqueness. A single-assignment assertion would close it.
- M27: the negated sentence "The binding ceiling is **not** 6 steps per tensor header, but 4 steps"
  → `met=True` (substring). Phrase presence is not a statement about arithmetic.
- M10: `~833 333` → `~666 666` with `MAX_STEPS = 5_000_000` kept → `met=True`.
- M11: the step sum `tensor type+offset 2 = 6` → `= 7` → `met=True`.
  M10/M11 are inside check 1's declared surface ("agrees with the MAX_STEPS value"), not the
  disclosed-limit escape ("not the truth of each filing's prose"): ceiling × 6 vs `MAX_STEPS` is
  arithmetic consistency with the bytes. If C3 is refiled, compute the ratio.
- `checks` is incremented unconditionally five times; it is a constant, not a count of checks that
  evaluated real content. `checks=5` printed for a repo whose three files are empty.
- Deleting the probe reddens 1 check (checks 5 is skipped when `probe == ""`), so file absence is
  still caught by check 1. Fail-closed, no finding.

---

## Mutation matrix (all in the shared clone, tip `bbdfc930`, audit bytes at tip)

| # | mutation | audit result |
|---|---|---|
| — | tip, unmutated | `checks=5 mismatches=0 met=True` exit 0 |
| — | base `5d43528b`, unmutated | `checks=5 mismatches=2 met=False` exit 1 |
| M1 | comment names 1 000 000 as NON-binding | green |
| M2 | re-add `the ceiling is 1,000,000` (exact comma form) | green |
| M3 | counter docstring+bytes `20 + 25` → `20 + 15` | red |
| M3b | wrapper `25` → `15`, docstring unchanged | red |
| M4 | `MAX_STEPS` back to 4 000 000, comment kept | red |
| M5 | one of two `6 steps per tensor header` phrases → "six" | green (phrase occurs twice) |
| M6 | SCORECARD pointer → stale `f6325660` | **green** |
| M7 | SCORECARD pointer → `deadbeefdead` | red |
| M8 | docstring keeps 25 and adds old `20 + 15 * ncand` | red |
| M9 | docstring `20 + 25 * ncand` (var typo) | red |
| M10 | ceiling number `833 333` → `666 666` | **green** |
| M11 | step sum `= 6` → `= 7` | **green** |
| M12 | pointer → freeze commit `58001b71` (ancestor) | green (correct) |
| M13 | pointer → `c810` (4-char prefix) | green |
| M14 | capability row deleted | red |
| M15 | probe file deleted | red |
| M16 | real `MAX_STEPS = 4_000_000`, comment says 5 M | red |
| M17 | second `MAX_STEPS = 4_000_000` appended after first 5 M | green (first wins) |
| M18 | wrapper computes `20 + 15`, comment carries `20 + 25` | **green** |
| M19 | docstring `20 + 15 * ncand` + decoy literal | red (banned string) |
| M20 | docstring `20 + 15 * ncand`, wrapper 25 | red |
| M21 | contradictory "ceiling is 1 000 000" sentence appended | **green** |
| M22 | decoy row after real, dead hash | red (last row) |
| M23 | docstring `20 + 30 * npaths` + decoy literal | **green** |
| M24 | wrapper formula removed (`limit=60`), literal gone | red |
| M25b | dead `MAX_STEPS = 5_000_000` then real `4_000_000` | **green** |
| M26 | pointer to descendant commit after tip | red |
| M27 | negated phrase "not 6 steps per tensor header" | **green** |
| M28 | stale real row + later decoy row with valid hash | **green** |

Bold = false green on a filing the counter declares it grades.

---

## Impacted axes

- **calibration (C3, claimed, 7)** — B1 voids the predicate's identity clause; B2/B3/B4 make three
  checks non-discriminating; two false ceiling sentences and a stale pointer are green.
- **adjacency (7, adjacent)** — evidence-pointer hygiene: the capability row's cited file paths do
  not resolve, its cited counter still carries the stale formula, and duplicate rows mask each
  other.
- No impact on **operability** or **depth**: C1's counter bytes are identical F→tip
  (`3f6107c3…`), and C2's audit was amended identically to C3's, so B1 repeats there only in the
  same K2/identity sense, not in C3's independently measured way.

## What must not be mistaken for a defect

- The green at tip and red at base are real; the base's `mismatches=2` is reproducible with both the
  frozen and the amended bytes. K3 fires only under the literal per-check reading.
- Hardcoding `5_000_000` and the exact commit in the audit is the point of a frozen target check.
- The disclosed limit (semantic prose is the non-author gate) legitimately covers sentence *truth*;
  it does not cover arithmetic that contradicts `MAX_STEPS` (M10/M11) or a check that never
  evaluates its subject (B2).

## Commands (reproducible, from a `--shared` clone of the lane)

```
python3 tools/round96-disclosure-audit.py --repo . --rev bbdfc930   # green
python3 tools/round96-disclosure-audit.py --repo . --rev 5d43528b   # mismatches=2
python3 frozen-audit-at-F.py --repo . --rev bbdfc930               # mismatches=1 (never green)
python3 frozen-audit-at-F.py --repo . --rev 58001b71               # mismatches=1 (never green)
git show 58001b71:tools/round96-disclosure-audit.py | sha256sum ; git show bbdfc930:tools/round96-disclosure-audit.py | sha256sum
git diff 58001b71 bbdfc930 -- plans/round-96-claims.md              # empty
git log --all -S "the ceiling is 1,000,000" -- tools/kama-probe.sh  # empty
git log --all -- measured/c1-m1b.out                                # empty
```

Receipts in this directory: `RECEIPT-core-runs.txt` (the seven commands above, captured),
`RECEIPT-mutants.txt` (the mutation matrix, re-run end-to-end), `frozen-audit-at-F.py` (the
freeze-time counter bytes). Scratch clone deleted; no tracked file modified.
