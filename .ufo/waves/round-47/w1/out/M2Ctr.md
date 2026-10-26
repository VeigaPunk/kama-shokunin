# M2Ctr — round 47 C2 counter mutation test (kama, w1)

**Verdict: the C2 counter `tools/round47-live-replay-audit.py` has teeth — 13/23 mutants killed, 10 survived as one coverage family (weakened equality/floor checks with no negative-control subject), 0 inconclusive; no mutant produced a false `met=True` on a lying-replay subject, and the pristine counter correctly returns `met=True` on the compare()-lie subject (its own re-verification, not the tool's `compare()`, carries the predicate).**

All work in scratch `/fast/scratch/hyaku/kama-r47/M2Ctr/` (removed at end); lane untouched.

## 1. Specimen and subjects

- Pristine counter: copied from the lane working tree to `<S>/counter-pristine.py`;
  sha256 `15408dce5b2f8f5dbe4dd7bacf17ddb0737fcbe480686907f40483273b128b0f` — identical to
  `git show 3a09a1d93dcc16799cf6c4b48786e6440af134c4:tools/round47-live-replay-audit.py` and to the
  preregistration `claims[1].counter_sha256` (frozen bytes; re-verified after all runs, §5).
- One shared clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`,
  detached at the build commit `3a09a1d93dcc16799cf6c4b48786e6440af134c4` (to `rev-parse --show-toplevel`
  asserted = clone dir before every commit; fixture identity `M2Ctr fixture <m2ctr@fixture.invalid>`,
  `commit.gpgsign=false`).
- Subjects (full diffs: `subjects.patch` in this directory):
  - **A (healthy)** `0b646115c99ea6703ca35e0f4f2b9176b38093b2` — appends SOURCES row `| S488` naming
    b11909 + `caa8191d…` (the newrow leg's missing piece; dry run had `newrow=0`).
  - **B1 (compare-lie)** `1341ca0065d586f757a9a47edd7d9ba90174307c` — A + `tools/kama-live-replay.py`
    `compare()` returns `[]` unconditionally (line 108-109 of the subject's copy).
  - **B2 (digest-lie)** `eaab5e9a8799b9c83b361130d897bcd68dffae12` — A + `acquire()` digest-mismatch
    branch disabled (`if False and got != sha:`).
- Counter invocation (each run): `python3 <counter> --repo $S/lane --tip <A|B1|B2> --scratch $S/runs/<tag> --out <out>/<tag>.receipt.txt`; stdout+exit captured to `<out>/<tag>.txt`.
- Budget: **52 counter runs** (< 60), each ≈ 46 MB downlink (replay leg 23.7 MB + tamper-asset 22.5 MB; the tamper-model copy is refused at the provenance check before any download).

## 2. Baselines (pristine counter)

| subject | tip | exit | line |
|---|---|---|---|
| A | `0b646115` | 0 | `receipts=1 replay=1 tamper=1 newrow=1 rerun_checks=11 met=True` |
| B1 | `1341ca00` | 0 | `receipts=1 replay=1 tamper=1 newrow=1 rerun_checks=11 met=True` |
| B2 | `eaab5e9a` | 1 | `receipts=1 replay=1 tamper=0 newrow=1 rerun_checks=11 met=False` — `detail: tamper-asset: exit 0, rerun outcome pass: not refused` |

B1 being `met=True` is correct, not a miss: the predicate ("replay re-acquires, digest-verifies, reproduces receipt-1's checks") still holds on B1 — the lifecycle genuinely reruns — and the counter judges it from the rerun receipt itself (per-check loop at `round47-live-replay-audit.py:287`, freshness `:276`, sha equality `:279-282`, inside-scratch `:283`), never from the tool's `match` claim. B2 violates the predicate (a wrong recorded digest is accepted) and is caught by the tamper leg (`:316`).

## 3. Mutants and verdicts

23 single-site mutants (generator `mutant-manifest.json` has exact old→new strings + per-mutant sha256).
Kill rule: a mutant is **killed** if its (summary-line, exit) differs from the same subject's pristine baseline on any subject; **equivalent** if identical everywhere. No environmental failures, so 0 inconclusive.

| id | site (pristine line) | mutation | A | B1 | B2 | verdict |
|---|---|---|---|---|---|---|
| M01 | `:98` SCHEMA | v4→v5 | met=F (receipts=0, replay=0) | met=F | — | **killed** |
| M02 | `:268` replay-json schema | v1→v9 | met=F (replay=0) | met=F | — | **killed** |
| M03 | `:145` outcome | "pass"→"ok" | met=F (receipts=0) | met=F | — | **killed** |
| M04 | `:274` rerun outcome | "pass"→"ok" | met=F (replay=0) | met=F | — | **killed** |
| M05 | `:148` floor 10 | →12 | met=F (receipts=0) | met=F | — | **killed** |
| M06 | `:148` floor 10 | →1 | met=T | met=T | — | equivalent |
| M07 | `:153` asset_url | `!=`→`==` | met=F (receipts=0) | met=F | — | **killed** |
| M08 | `:153` asset_url | →https-prefix only | met=T | met=T | — | equivalent |
| M09 | `:157` member | drop non-empty clause | met=T | met=T | — | equivalent |
| M10 | `:159` model url | https→http | met=F (receipts=0) | met=F | — | **killed** |
| M11 | `:163` model sha | drop `== msha` clause | met=T | met=T | — | equivalent |
| M12 | `:169` build_info | drop `+"-"` | met=T | met=T | — | equivalent |
| M13 | `:175` log_path | null flagged (`else:`) | met=F (receipts=0) | met=F | — | **killed** |
| M14 | `:276` started_utc | `<`→`>` | met=F (replay=0) | met=F | — | **killed** |
| M15 | `:276` started_utc | drop freshness clause | met=T | met=T | — | equivalent |
| M16 | `:130` inside() | strict→prefix | met=T | met=T | — | equivalent |
| M17 | `:287` per-check loop | `ev1.items()`→`[]` | met=T | met=T | — | equivalent |
| M18 | `:305` tamper flip | →no-op | met=F (tamper=0) | met=F (tamper=0) | met=F (=P) | **killed** |
| M19 | `:316` tamper exit rule | inverted | met=F (tamper=0) | met=F (tamper=0) | met=F (=P) | **killed** |
| M20 | `:323` newrow | drop COMMIT clause | met=T | met=T | — | equivalent |
| M21 | `:323` newrow pattern | `\| S`→`\| R` | met=F (newrow=0) | met=F | — | **killed** |
| M22 | `:96` receipts list | (1,2,3)→(1,2) | met=T | met=T | — | equivalent |
| M23 | `:155` asset_sha | `!=`→`==` | met=F (receipts=0) | met=F | — | **killed** |

Summary: **13 killed / 10 equivalent / 0 inconclusive**. Every kill flips the leg the mutation sits in — the legs are wired to real evidence, and no counter mutant passed a lying subject (B2's only runs, M18/M19, correctly stayed `met=False`).

## 4. Coverage findings (survivors; no contract change proposed)

All 10 survivors are one family: sub-checks that can only *tighten* acceptance were weakened, and no subject carries non-conforming data for them, so the relaxation is invisible:

1. **No negative control for the receipts leg** (M06, M08, M09, M11, M12, M22): with three genuinely conforming receipts at every tip, the frozen url/digest equalities (`:153`, `:155`), the member non-empty rule (`:157`), the ≥10 floor (`:148`), the provenance↔model digest equality (`:163`), and receipt-3's coverage (`:96`) can all be neutered undetected. The freeze-time control `junk-c2-r46-relabel` exercised this leg at the builder, but the wave subject set does not. A single negative-control subject (one receipt with a flipped digest/short checks) would kill the whole family.
2. **Replay-leg sub-oracles unexercised** (M15, M16, M17): no subject offers a stale rerun (`started_utc` < counter start), a sibling-of-scratch escape (`inside()` at `:130` relaxed to a bare prefix would accept `/…/M2Ctr2`), or a check mismatch only the counter's own loop catches. M17 is the sharpest: combined with the B1 result, the counter's per-check re-verification at `:287` is the *only* guard on check-equality — the tool's `compare()` is not consulted — and it is removable without any of these subjects noticing.
3. **newrow commit containment** (M20): a `| S` row naming b11909 without the release commit would satisfy `:323`.

Framing note: B1 (`compare()` always True) is an *equivalent subject* for the pristine counter by oracle design — the counter never trusts the tool's agreement claim — so a lying `compare()` in the lane's replay tool is invisible to C2 unless it also breaks refusal/digest behavior (B2 shows the tamper leg catches that class).

## 5. Restoration and hygiene evidence

- Lane counter bytes before == after all runs: sha256 `15408dce…b128b0f` (§1; re-hash after wave 2 identical). Mutants live only as scratch copies `$S/mut/M*.py`.
- Fixture clone left clean at A: `git -C $S/lane rev-parse HEAD` → `0b646115…`, `status --porcelain` → 0 lines; lineage `0b646115 → 3a09a1d9 (build) → bbcc6dc2 (freeze) → 172b8ad0 (r46)`.
- `restored-a` (pristine bytes re-run after all 46 mutant runs): `receipts=1 replay=1 tamper=1 newrow=1 rerun_checks=11 met=True`, exit 0 — environment stable, verdict reproducible.
- Cited receipt copied and hash-verified: `receipt-1.cited.json` sha256 `a4caf311ac030ce3c50373d7f2c37aa62895bcec5deb93bfa8bbd24e0706e80d` == lane `receipt-1.json`.
- Tooling: nothing installed (python3 + git only); no pacman transactions. Scratch `/fast/scratch/hyaku/kama-r47/M2Ctr` removed after copying evidence.

## 6. Defects

None found in the frozen counter: every killed mutant flips exactly its own leg, no mutant yields a false `met=True`, and both lying-subject baselines are judged correctly (B2 `met=False`, B1 `met=True` with the predicate genuinely holding). The survivor family in §4 is a test-subject coverage gap for future waves, not a counter defect; per freeze discipline the counter is not edited.

## Evidence files (this directory)

- `runs-summary.tsv` — all 52 runs: tag, tip, exit, summary line.
- `runs/*.txt`, `runs/*.receipt.txt` — per-run full counter output.
- `mutant-manifest.json` — 23 mutants: category, old→new, sha256.
- `subjects.patch` — A/B1/B2 fixture diffs (against `3a09a1d9`/A).
- `receipt-1.cited.json` — cited receipt copy (sha-verified).
