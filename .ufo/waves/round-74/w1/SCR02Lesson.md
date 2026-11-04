# SCR02Lesson — round 74, wave 1

Seat axes: **calibration**. Full report: `.ufo/waves/round-74/w1/SCR02Lesson/report.md`.

Built `tools/round74-seat-count-check.py` (sha256
`e52d2183fa4cabec83eba1c3177f17434ce6f44e1e4280eedc42aafe7f03a227`, 294 lines):
`--spec` recomputes the seat count from `len(items)` and fails (exit 1) when a
prose field (`milestone`, `context`) names a different count via `N seats`/`N
seat`; `--census-order DIR` fails when the first committed
`mode=mirror-* exit=0` receipt postdates the registry-append marker. Drafted
the round-74 lesson skeleton at
`.ufo/waves/round-74/w1/SCR02Lesson/drafts/round-74.md` (`## Gate`: S546
os-release(5) — URL/access date 2026-11-04/located `ID=` quote filled from
SCR01Sources' retained bytes `c7ba68ea…` at
`.ufo/waves/round-74/w1/SCR01Sources/source/os-release.5.html`, independently
spot-checked present; assimilation **none** with id-collision receipt
`.ufo/waves/round-74/assimilation/summary.out` (collisions=9, quarantine=7);
considerthese/2026-10-26.md disposition — proposal 4 landed in round 73,
proposals 1–3 daily-pass, none adopted. `## Mistakes`: (1) number-drift, r73
spec prose says 14 seats / items carries 15, captured-by none, fixed by this
tool; (2) landing, r73 registry append preceded the first exit-0 mirror census
(`corpus/lessons/round-73-verifier-spotcheck.md` §6 item 6), captured-by none,
fixed by the runbook ordering plus this tool's census-order arm).

Measured: selftest `SEAT_COUNT_CHECK_SELFTEST pass=10 fail=0` (fixtures under
scratch TMPDIR; honest-green, r73-replay-red, flip-guard, both exit-2 arms);
real r73 spec → exit 1 naming the drift in both fields (`r73-spec.out`);
real r74 spec → exit 0, 13 items / prose 13 (`r74-spec.out`); r73 census-order
replay → exit 1, first exit-0 mirror census at
`w1/SCR01Sources/census.out:16` postdates the append marker at
`w1/SCR01Sources/census.out:2` (`census-order-r73.out`). No frozen file, r73
spec, or real lesson file was edited; no commits; scratch deleted before
yield. Disagreements with the freeze: none.
