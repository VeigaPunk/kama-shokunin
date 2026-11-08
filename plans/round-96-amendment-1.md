# Round 96 — amendment 1 (instrument regex anchor; no claim change)

Date: 2026-11-08. Author: L1 `KamaR96`. Freeze commit `58001b71`; this amendment `e2fed9f5`.

The freeze-commit audits (run after F) came back red on a defect of the instruments, not of the work:
`MAX_STEPS = 5 000 000` in the probe's prose comment matched the unanchored regex before the real
assignment `MAX_STEPS = 5_000_000`, so `max_steps` parsed as `5`. The anchored regex
`^MAX_STEPS = ([0-9_]+)` (multiline) reads the assignment only.

- `tools/round96-depth-audit.py` and `tools/round96-disclosure-audit.py`: anchor + `re.M`.
- No predicate, cell, fixture or tolerance changes; no claim wording changes.
- Base controls re-run: `DEPTH_AUDIT checks=7 mismatches=6 met=False` at `5d43528b` and
  `DISCLOSURE_AUDIT checks=5 mismatches=2 met=False` at `5d43528b` (re-committed as amended controls).
