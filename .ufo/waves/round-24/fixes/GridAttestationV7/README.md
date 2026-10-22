# GridAttestationV7 — proposal: two minimal fidelity cleanups

A **proposal only**. Nothing here is production; the L1 integrates it. V1–V6
are **kept filed** (`6d9e31b7…`, `45e778a8…`, `437128b8…`, `8e0d5c54…`,
`d2aca34a…`, `d8ff2c47…`); this directory is the V7 successor.

* proposal source: `promisor-grid.py`, sha256 `30483830e0461898bd9b710603e755b08cf58e2a2a215a747098ebbe0383f270`
* `promisor-grid-v7-delta.patch` — the **incremental** V7 delta against the V6 proposal `d8ff2c47…` (sha256 `9743395a4aab69fb858e563ef97a136ab0a799b2e0de7a546fc21f8ed2c12362`)
* `promisor-grid.patch` — the full delta against the integrated `b034e159…` (sha256 `2fcb836ea175decb047c6d213763c11f77fd09630cbdd88b4fad882110abeb4d`)

Source: the L1's V6 delta review. **No code expansion, no schema change, no
criterion change**: the two cleanups below are the whole delta (four hunks,
32 diff lines), and the emitted `kind` output and the diagnostics are
unchanged.

## 1. The unavailable-root control was too loose

The two controls (normal mode and `--selftest` mode) accepted **any** exit-2
could-not-evaluate, so an unrelated input failure could green them. The
control now requires the refusal to

* name the **actual requested root path**,
* carry the words **"requested scratch"** and **"unavailable"**, and
* be **no traceback**.

Measured refusal text: `could-not-evaluate: the requested scratch
<path> is unavailable`.

## 2. `collect_failures` had a spare parameter

`collect_failures(rows, graded, arm)` never used `rows`. The parameter is
removed and its two call sites updated (the arm summary and the
unique-violation control). The behaviour — the unique graded cases that fail
their graded view or the twin constraint, for the selected arm only — is
unchanged, as are the emitted `violations` and `violating_cases`.

## Bounded verification (no full matrix)

`--selftest` **24/24 ok** with the tightened controls: the two
unavailable-root refusals now assert the requested path, the reason words and
the absence of a traceback, and the unique-violation control still reports
exactly the two unique cases.

The bounded run used `TMPDIR` under an owned
`/fast/scratch/hyaku/kama-r24/GridAttestationV7/own-tmp` directory, not the
public temporary area. The 47 primary cases, every expected value, every
criterion, every twin link and the manifest bytes (`d86b7bea…`) are
unchanged.

**Not re-run**: the full 47-cell suite and any candidate sweep (L1
instruction).
