# ScribeScorecard — round 34, wave 1

## Behavior and delivered draft

Created `.ufo/waves/round-34/w1/out/ScribeScorecard/SCORECARD-round-34-draft.md` without editing `SCORECARD.md`. The draft contains:

- a `## Round 34 - ...` claims table with the requested six columns, the two frozen counting commands, and **PENDING** before/after, measured-commit, and evidence cells;
- explicit reminders that the C1/C2 results and their separate do-nothing controls must come from receipts;
- the exact `**Capabilities - canonical list as of round 34**` heading and one four-column capability table with six demonstrated capabilities and first-working rounds 10, 14, 16, 20, 25, and 30.

The canonical rows are `sources-registry`, `ollama-offline-evidence-replay`, `live-llamacpp-lifecycle`, `gguf-declared-identity-replay`, `context-capacity-receipt`, and `instrument-agreement`. No round-34 capability row was invented: the declared C1 repertoire reconciliation and C2 registry repair are not new serving operations.

## Axes

- **Calibration:** the draft reconciles all six historical capability demonstrations and makes every retained capability evidence pointer lane-relative and resolvable. This is drafting support only; no calibration score move or C1 pass is asserted.
- **Operability:** the C2 frozen command and receipt placeholders are present. This seat did not run or widen the registry gate and asserts no C2 pass.

## Provenance

Read `SCORECARD.md` in full, including every capability-shaped table at lines 122-128 (top one-row table), 434-459 (round-14 measured capability), 621-628 (round-16 canonical list), 909-913 (round-20 append), 1298-1302 (round-25 append), and 1551-1555 (round-30 append). The round-16 list already subsumes the top and round-14 rows; duplicates were emitted only once. Historical volatile source counts were not promoted into a new current count.

The path audit's read-only Git provenance was HEAD `5c9ef1fe1938baa06f7bd8acd2bad9fa6f7ba185`. This is **not** a round-34 measured commit; those cells remain PENDING.

## Commands, outcomes, and pointer repairs

### 1. Required `test -e` audit

Executed from `/home/vgpnk/Projects/shokunin/kama-shokunin`:

```bash
paths=(
  'corpus/SOURCES.md'
  'scripts/sources-census.sh'
  'tools/kama-ollama-evidence.py'
  '.ufo/waves/round-14/acceptance.json'
  '.ufo/waves/round-16/live/receipt.json'
  'check-receipt.py'
  'tests/llamacpp-live/check-receipt.py'
  'SKILL.md'
  'tools/gguf-identity.py'
  '.ufo/waves/round-18/live-recovery/receipt-1.json'
  'runs/0957ce61/gguf-receipt.stdout'
  '.ufo/waves/round-20/runs/0957ce61/gguf-receipt.stdout'
  '.ufo/waves/round-20/runs/9add96e4/gguf-receipt.stdout'
  'tools/kama-context-capacity.py'
  '.ufo/waves/round-25/final/context-capacity-receipt.json'
  '.ufo/waves/round-25/count-c2.py'
  'tools/instrument-agreement.py'
  '.ufo/waves/round-30/c2/receipt-a.json'
  'tools/error-verdict-census.py'
)
for p in "${paths[@]}"; do
  if test -e "$p"; then
    printf 'PRESENT\t%s\n' "$p"
  else
    printf 'MISSING\t%s\n' "$p"
  fi
done
```

Outcome: exit 0; 16 PRESENT and 3 MISSING. Repairs in the draft:

- MISSING `scripts/sources-census.sh` — omitted rather than represented as lane-relative; the valid `corpus/SOURCES.md` evidence remains.
- MISSING `check-receipt.py` — corrected to PRESENT `tests/llamacpp-live/check-receipt.py`.
- MISSING `runs/0957ce61/gguf-receipt.stdout` — corrected to PRESENT `.ufo/waves/round-20/runs/0957ce61/gguf-receipt.stdout`.

The additional later-receipt candidate `.ufo/waves/round-20/runs/9add96e4/gguf-receipt.stdout` was also PRESENT, but the draft uses the minimal correction to the originally cited round-20 capability evidence.

### 2. Read-only HEAD existence cross-check

Executed from the same lane root:

```bash
printf 'HEAD\t'; git rev-parse HEAD
paths=(
  'corpus/SOURCES.md'
  'tools/kama-ollama-evidence.py'
  '.ufo/waves/round-14/acceptance.json'
  '.ufo/waves/round-16/live/receipt.json'
  'tests/llamacpp-live/check-receipt.py'
  'SKILL.md'
  'tools/gguf-identity.py'
  '.ufo/waves/round-18/live-recovery/receipt-1.json'
  '.ufo/waves/round-20/runs/0957ce61/gguf-receipt.stdout'
  'tools/kama-context-capacity.py'
  '.ufo/waves/round-25/final/context-capacity-receipt.json'
  '.ufo/waves/round-25/count-c2.py'
  'tools/instrument-agreement.py'
  '.ufo/waves/round-30/c2/receipt-a.json'
  'tools/error-verdict-census.py'
)
for p in "${paths[@]}"; do
  if git cat-file -e "HEAD:$p" 2>/dev/null; then
    printf 'HEAD_PRESENT\t%s\n' "$p"
  else
    printf 'HEAD_MISSING\t%s\n' "$p"
  fi
done
```

Outcome: exit 0; HEAD was the provenance hash above and all 15 selected draft evidence paths printed `HEAD_PRESENT`. This supplements, not replaces, the required `test -e` checks.

### 3. Final artifact structure and extracted-pointer audit

Executed from the same lane root after writing the draft:

```bash
draft='.ufo/waves/round-34/w1/out/ScribeScorecard/SCORECARD-round-34-draft.md'
mapfile -t paths < <(python3 - "$draft" <<'PY'
from pathlib import Path
import re
import sys

text = Path(sys.argv[1]).read_text()
claims_part, capabilities_part = text.split('**Capabilities - canonical list as of round 34**', 1)
claims = [line for line in claims_part.splitlines() if re.match(r'^\| C[12] ', line)]
assert len(claims) == 2, len(claims)
for row in claims:
    cells = [cell.strip() for cell in row.strip('|').split('|')]
    assert len(cells) == 6, cells
    assert all('PENDING' in cells[index] for index in (2, 4, 5)), cells
rows = [line for line in capabilities_part.splitlines() if line.startswith('| ')][1:]
expected = [
    ('sources-registry', '10'),
    ('ollama-offline-evidence-replay', '14'),
    ('live-llamacpp-lifecycle', '16'),
    ('gguf-declared-identity-replay', '20'),
    ('context-capacity-receipt', '25'),
    ('instrument-agreement', '30'),
]
assert len(rows) == len(expected), len(rows)
for row, wanted in zip(rows, expected):
    cells = [cell.strip() for cell in row.strip('|').split('|')]
    assert len(cells) == 4, cells
    assert (cells[0], cells[3]) == wanted, (cells[0], cells[3], wanted)
    pointers = re.findall(r'`([^`]+)`', cells[2])
    assert pointers, cells[0]
    for pointer in pointers:
        assert not pointer.startswith('/'), pointer
        assert '..' not in Path(pointer).parts, pointer
        print(pointer)
print('STRUCTURE_OK claims=2 capabilities=6 evidence_paths=15', file=sys.stderr)
PY
)
if (( ${#paths[@]} != 15 )); then
  printf 'PATH_EXTRACTION_FAILED count=%s\n' "${#paths[@]}"
  exit 1
fi
failures=0
for p in "${paths[@]}"; do
  if test -e "$p"; then
    printf 'FINAL_PRESENT\t%s\n' "$p"
  else
    printf 'FINAL_MISSING\t%s\n' "$p"
    failures=$((failures + 1))
  fi
done
printf 'FINAL_PATH_AUDIT present=%s missing=%s\n' "$(( ${#paths[@]} - failures ))" "$failures"
(( failures == 0 ))
```

Outcome: exit 0; `STRUCTURE_OK claims=2 capabilities=6 evidence_paths=15`, every extracted pointer printed `FINAL_PRESENT`, and `FINAL_PATH_AUDIT present=15 missing=0`.

Validation-history disclosure: the first version of this validator selected claim rows with `line.startswith('| C')`, which also selected the `| Claim ...` header. It failed with `AssertionError: 3` followed by `PATH_EXTRACTION_FAILED count=0`. The corrected command above uses `re.match(r'^\| C[12] ', line)`. This was a validator-selection defect, not an artifact edit; the draft was unchanged between those two runs.

## Gates and evidence limits

- Neither frozen claim counter was executed. No before/after counter line, measured commit, target met result, or do-nothing-control result is claimed.
- A direct Read attempt for `tools/capability-repertoire-audit.py` returned `does not exist` at audit time. The command is retained verbatim in the draft for the builder/L1; this seat did not create the tool or infer a result from its contract.
- Structural/path validation is not capability re-execution. Historical receipts and tools were used as pointers; their serving runs were not replayed.
- No service restoration, endpoint readiness, model quality, current registered-consumer health, or cross-lane scope transfer is claimed. No external source tree, network resource, service, or model endpoint was accessed.

## Touched surfaces

Created only:

1. `.ufo/waves/round-34/w1/out/ScribeScorecard/SCORECARD-round-34-draft.md`
2. `.ufo/waves/round-34/w1/out/ScribeScorecard.md` (this report)

No product code, `SCORECARD.md`, sibling-seat output, fleet file, jj state, or Git index was modified. No commit, push, install, pacman transaction, subagent dispatch, or delegation occurred.

## Out-of-scope items and handoff

Frontier source admission and `considerthese/2026-10-23.md` mining were not part of this seat and were not performed. The L1/builder must supply actual C1/C2 before/after and do-nothing-control receipts, replace every PENDING cell, and keep the claims causally separable before landing the draft. The path audit establishes current lane-root and audited-HEAD resolution only; the claim counter must still evaluate its own pinned full commit.

## Artifact paths

- Draft: `.ufo/waves/round-34/w1/out/ScribeScorecard/SCORECARD-round-34-draft.md`
- Report: `.ufo/waves/round-34/w1/out/ScribeScorecard.md`
