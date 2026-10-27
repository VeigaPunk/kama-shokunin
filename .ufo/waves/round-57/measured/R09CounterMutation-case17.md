# R09CounterMutation — distinct case 17

Axes: calibration and operability. Frozen input tip: `b89bdab2cc114735ec5d331c6c610134258f7864`. No lane source files were changed; mutations ran in `/fast/scratch/hyaku/kama-r57/R09CounterMutation/` and the fixture was restored before cleanup.

## Derivation finding

`tools/round42-selfdesc-reconcile.py` computes `rounds` from SCORECARD lines matching `^## Round (\d+)`, then sets `maxn = max(rounds)`. Thus maxN is derived from the greatest SCORECARD round heading, not from report-authority rounds and not from the canonical capability-table heading. `canon()` separately selects the highest `**Capabilities — canonical list as of round N**` marker; it does not feed `maxn`.

At the frozen tip: 57 matching round headings, maximum `56`; SCORECARD head says “Latest measured round: 56”; highest canonical-list marker is round `49`; the exact `corpus/lessons/*verifier-spotcheck.md` glob count is `43`, while its SCORECARD RUN-fact expected literal is `42`. The working tree has a `round-57` wave directory, while the frozen tip's top-level wave-directory tail ends at round 56. The claimed expected `46` is not one of these observed derivation anchors (the frozen no-op control merely prints it).

## Detector and mutation results

Detector command pattern (all calls used the same pristine counter unless noted):

```sh
TMPDIR="$SCRATCH/tmp" python3 "$COUNTER" --repo "$REPO" --tip "$TIP" --out "$OUT"
```

- **Pristine frozen baseline** (`COUNTER=pristine/round42-selfdesc-reconcile.py`, `REPO=lane`, `TIP=b89bdab2…`): `tip=b89bdab2cc114735ec5d331c6c610134258f7864`; `r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False`; detail: calibration run had no stdout line equal to `42` (run exit 0); process exit `1`. Its counter bytes match the frozen `base-c1.out` counter portion; that receipt also has harness trailer `base_c1_exit=1`.
- **M1 — force maxN to 46** in a scratch copy of the counter; run against corrected positive-control fixture (SCORECARD literal `43`, tip `eed1fb529d4523968ba4ed1481777789a7b740a3`). Corrected pristine counter baseline: `r41=0 ... mismatches=0 maxN=56 met=True`, exit `0`. Mutant: `r41=0 banner=1 planned=1 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=2 maxN=46 met=False`; details `head lacks 'Latest measured round: 46'` and `section does not name '### Planned (round 47)'`; exit `1`. **KILLED**: the detector observes forced 46 against its head/planned facts.
- **M1b — replace `max(rounds)` with `rounds[-1]`** on the same passing fixture. Output exactly matches the corrected pristine output (`mismatches=0 maxN=56 met=True`), exit `0`. **SURVIVED**: this corpus cannot distinguish greatest numeric heading from last-listed heading; coverage finding.
- **Literal sensitivity control — change expected RUN output `42`→`43`** in scratch SCORECARD, commit only in fixture, run pristine counter: `r41=0 ... mismatches=0 maxN=56 met=True`, exit `0`. This is the measured correction, not a defect mutant; actual glob count is 43.
- **Stale-literal defect — change `42`→`44`**: detector output `r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False`; detail says no stdout line equal to `44` (run exit 0); process exit `1`. **INCONCLUSIVE** as a strict mutation verdict because the pristine frozen baseline already fails (the protocol treats baseline failure as inconclusive, not a kill). The 43 correction control passes, and the wrong 44 expectation fails, demonstrating the RUN fact is behavior-bearing.
- **Restored frozen bytes**: reset scratch fixture to original frozen tip; output exactly matches pristine baseline, exit `1`; fixture status was clean before trap cleanup.

## Hashes and receipts

- `round42-selfdesc-reconcile.py`: pristine/restored `9736923ec3086c6e56512cd67fa7c00a22cbb8ac63022bef45a676f2200f9ef0`; M1 forced-46 `a464efe5c93e49df526f78a31630841adc59b4308215935a3f808e7786d9f0a7`; M1b last-listed `bf70cc20e0af4d1aa5195eb76f3599591eaab6a0ab034774e52b23cd817b580f`. `round41-scorecard-reconcile.py` pristine/restored: `eff934a27b3e7525226c78e376ce774f3ab0b225ab98427b19201e5312176cd6`.
- SCORECARD blob: frozen/restored literal-42 `9a8d594b18db8d7b31675ef3a31ff3e70e364ca66816e2489bc8b3c35d29dd35`; corrected literal-43 `e5e396fac31d8351f3f7b7f8413ed39b58de03a54db9fdf14a57c9a18c63d9a5`; wrong literal-44 `9b4c70d9be6ba4d7071b52acc3f758d620b859609f196fba49bc44863c5ba2c4`.
- Raw outputs and pristine tool hashes are in sibling `R09CounterMutation-case17-*.out` and `R09CounterMutation-case17-pristine-tool-hashes.txt` receipts. Scratch cleanup used an EXIT trap after receipts were copied.
- No installs or tool updates.

Advisory only (this is a lane-author seat): a non-author seat should reopen SOURCES S515 against the Git manual and do the required admit/reject decision spot-check.

Report: `.ufo/waves/round-57/measured/R09CounterMutation-case17.md`
