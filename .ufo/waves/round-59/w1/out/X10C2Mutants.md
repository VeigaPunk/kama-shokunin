# X10C2Mutants — C2 calibration-row field falsification

**Axes:** calibration 7 (lowest assigned), operability 8. Advisory seat; not the judge.
**Attacked claim/clause:** frozen C2 predicate/sentence, `controls/freeze.txt` lines 11–15
(predicate 12, sentence 13, kill rule 15) —
per-field binding of the SCORECARD calibration row (`typed count absent`, `pinned fleet
revision absent`, `pointer round`, pointer `token` = fleet closure `verdict`, `including`
round, `command`), and the kill-rule limb *"any shortcut control meets, any field mismatch is
accepted … -> claim not met"*.

**No source edits, no commits, no installs, no lane/fleet writes.** Scratch only, removed before
yield (`/fast/scratch/hyaku/kama-r59/X10C2Mutants/`). One output file: this report.

## Method (re-derivable, scratch-only)

1. Genuine row extracted read-only from the measured tip: `git -C <lane> show
   2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35:SCORECARD.md`, first line matching
   `^\|\s*(?:\*\*)?calibration(?:\*\*)?\s*\|` inside `## Axes`.
2. Three fixture families, each a fresh `git init` repo under scratch:
   - **minimal card** — real row text inside a synthetic `## Axes` table (series 1);
   - **full document** — `git -C lane archive <tip> | tarfile` of the real `SCORECARD.md` plus
     the real `corpus/lessons/round-*-verifier-spotcheck.md` set (44 files), one row field
     replaced per commit (series 3/4);
   - **fleet blob** — scratch copy of the real `MANIFEST.json`, one closure field changed
     (series 2), passed via `--fleet-repo <fixture>`.
3. Every fixture: `git -C "$D" rev-parse --show-toplevel` asserted equal to `$D` before the
   commit; identity set only inside `$D`; `TMPDIR=/fast/scratch/hyaku/kama-r59/X10C2Mutants`.
4. Counter run exactly as frozen: `python3 <lane>/tools/round59-c2-counter.py --repo <fixture>
   --tip HEAD --fleet-repo <fixture> --fleet-ref HEAD`.

## Baseline (unchanged row, real lane)

| tip | fleet resolved | result |
|---|---|---|
| `2c7443ab…` (measured C2) | `0f99f606…` (current HEAD) | `mismatches=0 met=True` exit 0 |
| `2c7443ab…` | `58cffd1f…` — as recorded in frozen receipt `controls/c2-after.out` | `met=True` exit 0 |
| `2c7443ab…` | `3f3dd973…` — as recorded in `controls/c2-after-current-head.out` | `met=True` exit 0 |
| `aca8d006…` (C1 pass) | `0f99f606…` | `met=True` exit 0 |
| `4a541190…` (lane HEAD) | `0f99f606…` | `met=True` exit 0 |

Fleet HEAD moved `3f3dd973` → `0f99f606` between assignment and run (852 vs 851 MANIFEST rows);
the kama `lane_round=57` closure carries `rejected-honest-stop` at **both** refs, so the token is
stable. The counter prints the resolved 40-hex fleet rev each run, so the input binding is
observable — but the row's own invocation is `--fleet-ref HEAD`, a moving pointer; only the saved
receipt pins it.

## Field matrix (real full-document bytes, series 3)

Each row = one commit in one fixture that changes **only** the calibration row.

| # | field mutation (exact replacement) | exit | mismatch line | verdict |
|---|---|---|---|---|
| F0 | none (genuine) | 0 | `mismatches=0 met=True` | pass |
| F1 | `round-57-` → `round-56-verifier-spotcheck.md` in pointer | 1 | `pointer_round=1` | **rejected** ✔ |
| F2 | token `(rejected-honest-stop)` → `(admitted)` | 1 | `pointer_verdict=1` | **rejected** ✔ |
| F3 | `including round 57` → `including round 56` | 1 | `including_round=1` | **rejected** ✔ |
| F4 | `round59-c2-counter` → `round58-c2-counter` | 1 | `count_command=1` | **rejected** ✔ |
| **F4b** | `--fleet-ref HEAD` → `--fleet-reference HEAD` | **0** | `mismatches=0 met=True` | **ACCEPTED** ✘ |
| **F4c** | tool path `…-counter.py` → `…-counter.pyc` | **0** | `mismatches=0 met=True` | **ACCEPTED** ✘ |
| **F4d** | command loses `--repo <repo>` | **0** | `mismatches=0 met=True` | **ACCEPTED** ✘ |
| **F5** | `latest outside closure` → `44 outside closures on record; latest outside closure` | **0** | `mismatches=0 met=True` | **ACCEPTED** ✘ |
| **F5b** | `44 (Outside closures on record); …` (case variant) | **0** | `mismatches=0 met=True` | **ACCEPTED** ✘ |
| F6 | pin `fleet rev 58cffd1f42723048bcfe48eb0bc2f346caa9b77f;` (40-hex) | 1 | `pinned_fleet_revision=1` | **rejected** ✔ |
| **F6b** | pin short rev `fleet rev 58cffd1f;` (8-hex) | **0** | `mismatches=0 met=True` | **ACCEPTED** ✘ |
| F7 | pointer clause deleted | 1 | `pointer_missing=1` | **rejected** ✔ |

Corroborating runs: minimal-card series reproduced F1/F2/F3/F4 exactly (`pointer_round=1`,
`pointer_verdict=1`, `including_round=1`, `count_command=1`, all exit 1, one mismatch each) and
the same three command/count acceptances (`--fleet-reference`, `44 outside closures on record`,
uppercase 40-hex pin `58CFFD…B77F` also accepted — the pin regex is `[0-9a-f]{40}`,
`tools/round59-c2-counter.py:61`).

## Why those six are accepted (source lines)

`tools/round59-c2-counter.py`:

- `:60` `typed_count = bool(re.search(r"\b\d+`?\s+\(outside closures on record", row))` —
  case-sensitive, requires the parenthetical form. A literal count written any other way is
  invisible, so *"remove the hard-coded outside-closure count"* is enforced on one string shape,
  not on the presence of a fixed count.
- `:61` `pinned_rev = bool(re.search(r"\b[0-9a-f]{40}\b", row))` — lowercase 40-hex only; a
  short rev or uppercase rev is a pinned fleet revision that scores clean.
- `:62` `count_command = "tools/round59-c2-counter.py" in row and "--fleet-ref" in row` — a
  two-substring presence test, not a runnability test: `--fleet-reference` (argparse rejects it),
  `…counter.pyc` (no such file), and a command missing required `--repo` all satisfy it.

The three accepted command strings are each unrunnable, measured directly:

```text
$ python3 tools/round59-c2-counter.py --repo . --tip 2c7443ab --fleet-reference HEAD
round59-c2-counter.py: error: unrecognized arguments: --fleet-reference HEAD        exit=2
$ python3 tools/round59-c2-counter.py --tip 2c7443ab --fleet-ref HEAD
round59-c2-counter.py: error: the following arguments are required: --repo          exit=2
$ python3 tools/round59-c2-counter.pyc --repo .
python3: can't open file '…/tools/round59-c2-counter.pyc': [Errno 2] …               exit=2
```

So a row may cite an invocation that cannot run and still score `met=True`; the row's own
`--out` receipt would have to be produced by a *different* string than the one it prints.

## Spot-check record content is never read (series 4)

Same real document, genuine row, only `corpus/lessons/round-57-verifier-spotcheck.md` replaced:

| blob | bytes | exit | result |
|---|---|---|---|
| genuine | 9562 | 0 | `met=True` |
| empty file | 0 | **0** | `met=True` ✘ |
| `# round 57 spotcheck\n\nTODO\n` | 27 | **0** | `met=True` ✘ |
| content about round 40, no S517/S518 | 60 | **0** | `met=True` ✘ |
| `nothing was checked.` | 33 | **0** | `met=True` ✘ |

The counter binds filename + round number + fleet verdict only. The frozen sentence's clause
*"preserving a real outside admit/reject spot-check record for S517 and S518"* therefore has no
enforcement in the counter — and, as recorded, S517/S518 external spot-check is still
unrecorded (`corpus/lessons/round-58.md:20`).

## Input-side and cross-tree mutants (series 2)

| mutant | exit | flagged | verdict |
|---|---|---|---|
| fleet `MANIFEST.json`, kama r57 verdict `…→admitted` (row untouched) | 1 | `pointer_verdict=1` | **rejected** ✔ |
| fleet `MANIFEST.json` with r57 closure removed | 1 | `pointer_verdict=1`, `manifest=None` | **rejected** ✔ |
| extra `round-58-verifier-spotcheck.md` in tree, row untouched | 1 | `pointer_round=1 pointer_verdict=1 including_round=1` | **rejected** ✔ |
| pointer moved to `round-58…` + file added | 1 | `pointer_verdict=1 including_round=1` | **rejected** ✔ |
| calibration row absent from `## Axes` | 1 | `row_missing=1` (+3) | **rejected** ✔ |
| `--tip deadbeef…` | 2 | `could-not-evaluate: unresolvable lane tip or fleet ref` | **fail-closed** ✔ |
| `--fleet-ref nope` | 2 | `could-not-evaluate: …` | **fail-closed** ✔ |
| fleet dir without `MANIFEST.json` | 2 | `could-not-evaluate: …` | **fail-closed** ✔ |

## Committed control-set inventory (context for the kill rule)

- `controls/c2-base.out|.exit`: base tip `8f7f58cd` → `typed_count=1 pinned_fleet_revision=1
  count_command=1`, exit 1. This is the **only** committed C2 control: it exercises the old
  literal-row shape, not any individual field.
- `controls/make-variants.py` + `variant-count.out` (`variants=5`) generate mutants of
  `tools/round56-env-leg-battery.py`, i.e. **C1's** battery (`tests/round59-battery-variants/`).
  `tests/` contains no C2 variant fixtures; `grep -rl round59-c2` hits only the tool and the
  SCORECARD row.

## Findings

1. **Robust:** pointer round, pointer token/verdict, `including` round, full tool rename,
   missing pointer, missing row, extra higher-numbered spotcheck, manifest token flip, manifest
   closure absence, and all three unreadable-input shapes (exit 2). These were rejected exactly
   as the frozen sentence requires, one field per commit.
2. **Falsified limbs:** six one-field mutants meet — three command shapes (`--fleet-reference`,
   `…counter.pyc`, dropped `--repo`), two count phrasings (`44 outside closures on record`,
   `44 (Outside closures on record)`), and a short-rev pin. Under the frozen kill rule's
   *"any field mismatch is accepted"* limb these are accepted field mismatches on the `command`
   and `count` fields, so the calibration-row evidence pointer can be made unrunnable and can
   retain a literal count and a pinned revision while the counter still prints `met=True`
   (`tools/round59-c2-counter.py:60-62`).
3. **Unbound content:** the counter cannot distinguish a 9562-byte real record from an empty
   file at the same path.
4. **Calibration nuance:** determinism rides on the caller's `--fleet-ref HEAD`; the row pins
   nothing, and only the saved receipt fixes the resolution (`58cffd1f` at freeze time,
   `0f99f606` now, both with the same kama r57 verdict).

## Not claimed

No axis score move, no capability, no S517/S518 discernment progress (external spot-check still
unrecorded), no judgement of the C2 claim — that belongs to the L1/judge. These are measured
counter acceptances, each with the exact mutant string, command and exit above; anything not in
the tables is not passed.

## Files changed / installs / scratch

- Written: `.ufo/waves/round-59/w1/out/X10C2Mutants.md` (this file). Nothing else.
- Installations/upgrades: none (Python 3.14 stdlib only; `git` already present).
- Scratch `/fast/scratch/hyaku/kama-r59/X10C2Mutants/` removed before yield; all fixture commits
  were inside that directory, `rev-parse --show-toplevel` asserted per fixture.
- Blockers: none.
