# GridAttestationV6 — proposal: interface findings N2, N4, N5, N9 (and the digest placement)

A **proposal only**. Nothing here is production; the L1 integrates it. V1
(`6d9e31b7…`), V2 (`45e778a8…`), V3 (`437128b8…`), V4 (`8e0d5c54…`) and V5
(`d2aca34a…`) are **kept filed**; this directory is the V6 successor.

* proposal source: `promisor-grid.py`, sha256 `d8ff2c473a28249433cc52dd42c67252a5af1c54b59c4d3aeee3c243e3cf654f`
* `promisor-grid-v6-delta.patch` — the **incremental** V6 delta against the V5 proposal `d2aca34a…` (243 diff lines, sha256 `05461d8d…`)
* `promisor-grid.patch` — the full delta against the integrated `b034e159…` (829 diff lines, sha256 `4371082f…`)
* the 47 primary cases, every expected value, every criterion and every twin link are **unchanged**; the manifest stays byte-identical (`d86b7bea…`)

Source: `.ufo/waves/round-24/postfix/interface-findings-contract.txt` (the
GridOracle owner items).

## N2 — the violation count was inflated

Twin-mismatch rows were appended to **both** the live and the frozen failure
lists, and a cell that missed its own view *and* broke a twin was counted
twice. `violations` and `violating_cases` now count the **unique** graded
cases that fail their graded view **or** the twin constraint, **for the
selected arm only** (`collect_failures`). The graded view is the amended view
for the current arm and the historical frozen column for the frozen arm. The
twin equality criterion and the twin links are untouched.

*Control*: a synthetic asymmetric two-cell twin example (one cell breaking a
twin, one cell missing its own view, plus a third row belonging to the other
arm) must report exactly **two** unique violating cases.

## N4 — the grade explanations were lost

`grade()`'s actual problem messages are now kept per named view:

* `problems` — the graded view: the historical frozen column for the frozen
  arm, the amended view for the current arm;
* `amended_problems` — the strict comparable amended target, in **both** arms;
* `original_problems` — the original (pre-amendment) view, for the current
  arm.

The comparison work is done once per view and reused; no rule was weakened
and no frozen expectation changed. Measured on the frozen arm, the amended
view now explains itself: PG13 reads `["reason not in class unavailable",
"reason is the r23 metadata refusal", "reason does not name the unavailable
object"]` — the r23 base's metadata refusal, named as the reason the amended
policy is not met.

## N5 — the fixture root was baked in

The hard-coded `/fast/scratch/hyaku/kama-r24` root is gone. The caller's
`TMPDIR` is honoured; an explicitly requested scratch that is not usable is a
**could-not-evaluate (exit 2) before any fixture or auditor exists** — never
a silent fallback elsewhere, never a traceback with exit 1. With no `TMPDIR`
the standard temporary-directory selection is used. The per-fixture
containment guards (fixture root inside the grid root, `rev-parse
--show-toplevel` equality, `--absolute-git-dir`) are unchanged.

*Controls*: the requested root is honoured (a `promisor-grid-*` entry appears
inside it) and an unavailable requested root is refused with exit 2 in
**both** the normal and the `--selftest` mode.

## N9 — the dead kind translation

`run_case`'s kind translation was dead: `main` assigns the canonical
manifest kind to every row before any CLI output, so the translated value was
never emitted. It is removed. The **emitted** values stay the canonical
`policy` / `control` / `open`, and the real consumers are unaffected.

> Coordination note: because the translation was dead, no consumer ever saw
> the translated value — the emitted `kind` has always been `policy` /
> `control` / `open`. A mutation runner whose graded set is keyed on
> `kind` must therefore include `policy`; the attribution by cell-id prefix
> is unaffected.

## Digest placement (N8 coordination)

The run document now carries the byte identities of everything that was
actually measured, next to each other at the top level:

| field | meaning |
|---|---|
| `doc["auditor_sha256"][arm]` | the auditor blob that arm actually ran (`frozen` = the pinned r23 base, `current` = the candidate path given to `--current`) |
| `doc["grid_sha256"]` | the producer's own source digest |
| `doc["expectations_sha256"]` | the pinned expectation manifest digest |
| `doc["population_sha256"]` | the case-table digest |

## Bounded verification (no full suite)

`--selftest` **24/24 ok** — the three negative capabilities, the four
command-line controls, the three stand-in controls, the two root controls
(requested root honoured; unavailable root refused in both modes), the
specific-clause fixture control, the valid hydration path, the five premise
checks and the unique-violation control.

A bounded three-cell run (PG13, PG26, PG27) against the candidate
`ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220`:
`auditor_sha256 = {frozen: da5041a8…, current: ea51bc35…}`,
`expectations_sha256 = d86b7bea…`, `population_sha256 = 612b0a74…`,
`grid_sha256 = d8ff2c47…`; 0 violations in both arms; the twin pair
PG26/PG27 reports `twin_equal = true`; the per-view problem lists are
populated as described.

The bounded runs were executed with `TMPDIR` pointing at an owned
`/fast/scratch/hyaku/kama-r24/GridAttestationV6/own-tmp` directory, not the
public temporary area.

**Not re-run**: the full 47-cell suite and any candidate sweep (L1
instruction).
