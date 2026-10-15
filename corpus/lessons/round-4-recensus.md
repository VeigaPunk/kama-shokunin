# round-4 re-census — source-root derivation already correct; endpoints dead

2026-10-14. Steered round 4. Advisory inventories:
`../.ufo/waves/shokunin12h-20261014-p1-repair/members/Kama*.md`.

## Verdict lines (measured)

- `bash tools/kama-probe.sh consumers` → exit 0; `$UFO_SRC` rows resolve
  `file_match=yes` against `~/Projects/ufo-fsd-alpha` (HEAD `964f443e`).
- `bash tools/kama-probe.sh check` → **exit 2** (`DEAD` / connection-refused) —
  the correct identity verdict while nothing serves; not a probe defect.
- `bash tools/kama-probe.sh listeners` → exit 0 (`FOREIGN_SERVICE` on a
  non-model port, classified, not a fault).
- `bash tools/test-snapshot.sh` → `RESULT pass=24 fail=0`.

## No repair warranted

`tools/kama-probe.sh` already implements the authorized order — explicit
`--ufo-src` (bad override dies at parse) → `$UFO_SRC` (dir-only) → first
existing of `~/Projects/ufo-fsd-alpha` then `~/Projects/origin-work/ufo-fsd-alpha`
→ fail-closed. Re-repairing it would be churn.

## Named debt

Dead positive controls (`ufo-fsd-thetick`, `ufo-fsd-local-helper`): correct pin,
dead endpoint. `qwen-coder.service` gone; `34113` and `8080` refuse. Unblock:
operator restores a serving unit. Province contraction remains an L0 decision.

Stale live prose recorded, not rewritten: `SKILL.md` still teaches a live
11-row `MODEL_OK` world; `PROVINCE.md:10-11` owns deleted host pins;
`endpoint-identity.md` line citations drifted (`:481-487` is the match path).
