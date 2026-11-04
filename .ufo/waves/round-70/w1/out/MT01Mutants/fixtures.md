# MT01Mutants — fixture recipes (all under `/fast/scratch/hyaku/kama-r70/MT01Mutants/`, deleted at yield)

Every fixture is a `git clone --shared` of the kama lane, checked out at a pinned rev, with
the plant committed under the fixture-only identity
`-c user.name=mt01fixture -c user.email=mt01@fixture.invalid`. Each clone asserts
`git -C <fx> rev-parse --show-toplevel` equals its own path before the first commit, and its
fixture commit is made **on a local `master`** so the repaired harness's nested clone also has a
`master` (the gate-registry-check lane-tip arm resolves that branch; see report §4 F3).

## Landed-tree fixtures (primary matrix; source = lane tip `73597158`)

| fixture | rev | plant |
|---|---|---|
| `L` | `73597158ec1cd6707a6f3abe0814615b82580d49` | none — clean clone of the landed tip |
| `fx2-nbanner` | `5bc6e2acc5dfeee68c93a20d7ae7301d9921c9f7` | head line `Latest measured round: 70` → `69` |
| `fx2-nprovince` | `12e6e5e4911a94d05201cb06f3b42c527ad10cce` | `PROVINCE.md`: `` `tools/round69-newest-closure-counter.py` `` → `` `tools/round69-newest-closure-counter` `` (backtick token no longer a `tools/` path), then the coverage row's PROVINCE sha256 + line count re-anchored so `r41` stays 0 |
| `fx2-nclosure` | `9d2c709f095946476b1e3f2bedc1187977090070` | calibration row: `latest outside closure …round-69…` → `round-68` and `including round 69` → `including round 68` |
| `fx2-nharness` | `d78f8ddbab7ec6af19dbc8de4abdfe21c1eba5ad` | calibration evidence cell gains `; run \`python3 -c "import subprocess;print('GIT_FACT_OK' if subprocess.run(['git','rev-parse','HEAD'],capture_output=True).returncode == 0 else 'NO_GIT')"\` → \`GIT_FACT_OK\`` inserted **inside** cell 2 |

Insertion point matters: a token appended after the row's trailing `|` becomes a fifth cell and
is never evaluated by `axes_table` (this seat's first attempt did exactly that and read green —
see report §4 F6).

## Synthetic fixture (cross-check; source = lane tip `0e14facd`)

Built by `mkfix.py` when EX01/EX02 had not yet landed: the round-42/41 bytes plus this seat's
reference harness repair (checkout instead of `git archive`) against a hand-repaired
self-description. Two modes:

| fixture | rev | mode |
|---|---|---|
| `fixture-gl` | `4446a1548f67efdcaf2d2e1f498357dd8939f09b` | counter green **and** selftest 5/5: the `round69 --since-round 63` run fact is **absent** from the calibration row (see report §4 F4) |
| `fixture-coupling` | `ebf2b2c4033ef0f015e456d3c4043b82caab0bcb` | counter green, selftest 1/5: the same fact kept in a satisfiable exact-line form |
| `fx-nbanner` / `fx-nprovince` / `fx-nclosure` / `fx-nharness` | `0ea62d17…` / `2b0c6da1…` / `cfd9fd38…` / `01e21bdf…` | the same four single-violation plants on `fixture-gl` |

`fixture-coupling` is the measurement behind F4: with the row fact present, the five-arm
selftest reads `ok:mismatches=1`, `stale_ptr:2`, `stale_both:2`, `stale_incl:2`, `no_ptr:2`
→ `pass=1 fail=4`, because planting the pointer also falsifies the row's own run fact (+2 per
planted arm instead of +1).

## Why the plants are single-violation

`fx2-nprovince` re-anchors the PROVINCE hash/line count; without that, editing PROVINCE.md also
breaks the coverage row's `sha256`/`lines` facts and the fixture would carry two mismatches,
which would hide a mutant that disables only the province check (the fixture would stay red).
