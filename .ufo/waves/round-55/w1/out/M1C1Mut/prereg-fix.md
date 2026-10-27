# Proposed amendment — round-55 preregistration C1 battery wording (M1C1Mut finding 4)

Proposed edits only; preregistration is frozen and must not be edited in place.
Apply to `.ufo/waves/round-55/preregistration.json` if a re-freeze round allows it.

## Defect

`controls.c1_kill_battery.mutants` names four mutants:

    ["m-ldpreload (envnames leg)", "m-ldaudit-writable (code leg)",
     "m-ldaudit-foreign (hostlibs leg)", "m-member-flip (rehash leg)"]

and `claims.C1.target` requires "each named mutant receipt prints met=False (exit 1)
with its named leg failing"; `claims.C1.kill_rule` falsifies the claim "if any battery
mutant prints met=True".

The executed battery (`.ufo/waves/round-55/c1/battery/run-battery.py` `MUTANTS`) is
`{m-ldpreload, m-text-flip, m-ldaudit-foreign, m-member-flip}`:

- `m-text-flip` is executed and killed but never named in the prereg.
- `m-ldaudit-writable` is named but was never executed by the final driver; its only
  (pre-freeze) receipt printed `met=True` and was removed from the battery dir.
- `m-ldaudit-foreign` is `kind="vector"` in the driver — a void LD_AUDIT vector whose
  receipt `m-ldaudit-foreign.out:2` prints `met=True` BY DESIGN ("the vector is void:
  the mutant passes, which is the finding"). By the kill rule's letter, that
  met=True receipt falsifies C1.

## Proposed target/kill-rule wording

    "target": "...; kill battery: each kill-kind mutant receipt prints met=False
     (exit 1) with its named leg failing (m-ldpreload envnames, m-text-flip code,
     m-member-flip rehash); the m-ldaudit-foreign vector-analysis receipt prints
     met=True (exit 0), recording that the hostlibs kill is root-gated on this
     glibc; the unmutated positive control prints met=True."

    "kill_rule": "the claim is falsified if the base/do-nothing control prints
     met=True, if any kill-kind battery mutant prints met=True, if the build
     measurement prints met=False, or if the counter bytes at measurement differ
     from counter_sha256"

    "controls.c1_kill_battery.mutants":
     ["m-ldpreload (envnames leg, kill)", "m-text-flip (code leg, kill)",
      "m-member-flip (rehash leg, kill)",
      "m-ldaudit-foreign (hostlibs leg, vector analysis, expect met=True)",
      "m-ldaudit-writable (dropped pre-freeze vector; receipt removed; recorded
       here for provenance only)"]

## Evidence

- `run-battery.py` MUTANTS keys and `kind` fields (`vector`/`kill` handling in `main()`).
- `m-ldaudit-foreign.out:2` — `envnames=3/3 hostlibs=3/3 … met=True` (copied: `frozen/m-ldaudit-foreign.out`).
- `m-ldaudit-writable.out` (pre-freeze, `met=True`, `envnames b1: 6 environment variable names`) — preserved at `frozen/m-ldaudit-writable.out`.
- `m-ldpreload.out`, `m-text-flip.out`, `m-member-flip.out`, `control.out` — all copied under `frozen/`.
