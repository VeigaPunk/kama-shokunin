VERDICT: partial — check.py's served_model logic catches an early-fill probe once rows carry ids, but the shipped 72-row matrix lets it pass 72/72; the oracle copies the probe.

# ServedModelOracle — R17 falsify advice (C1 served_model grading)

Attacked: the C1 claim that `tests/probe-verdicts/check.py` "grades `served_model` (derived from each row's own literal `/v1/models` body with the probe's `served_ids()` precedence)" (`corpus/lessons/round-17.md:25-26`). Questions: is the oracle independent of the probe, or a copy? Does it catch a probe that fills served_model before the auth/503 gates? Lane commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3`, read from a /tmp clone.

## Method
- Clone: `/tmp/ServedModelOracle-clone` at 54a29268. `check.py` reads its matrix only from its own directory (`check.py:47`, `load_matrix()` in `main`, `check.py:630`). So I copied `check.py` into scratch dirs and ran it with the scratch rows. The lane matrix directory was not touched.
- Scratch matrix `SMO.json`, 11 rows:
  - S1 401 + `data[]` ids
  - S2 403 + `data[]` ids
  - S3 503 exact loading envelope + `data[]`
  - S4 503 non-loading + `data[]`
  - S5 500 + `data[]`/`models[]`
  - S6 404 + `models[].name` only
  - S7 200 `models[].name`-only with a duplicate, expect `*`
  - S8 200 `models[].name`-only, expect the name
  - S9 200 `models[].id` and `.name`
  - S10 200 top-level `id` with no array
  - S11 200 `models[].model` only
- Probe variants (scratch copies of `tools/kama-probe.sh`; sha256 prefixes):
  - real `36b64978ee3a`
  - **V1 early-fill** `1e66a2b962a3`: `C_SERVED=$(served_ids …)` inserted right after the transport `case`, before the 401/403 gate (`kama-probe.sh:496`) and the 503 loading gate (`:505`)
  - V2 `models[].name` ranked before `data[].id` `268af90b0730`
  - V3 `models[].name` group dropped `028fc28e308a`
  - V4 no dedupe `f91aba30dcd5`
  - V5 `served_ids` forced onto its grep fallback `d976c3fc1ca6`

## Kill table (test failures / rows run; a failure kills the variant)
| probe | scratch SMO (11) | lane matrix (72) |
|---|---|---|
| real, scratch copy | 0 — exit 0 | 0 — exit 0 |
| real, clone path | 0 — exit 0 | 0 — exit 0 |
| **V1 early-fill** | **7 — exit 1** (S1-S6, S10: served `kama-a,kama-b` / `kama-n` / `kama-top`, expected `-`) | **0 — exit 0 (survives)** |
| V2 name-first | 1 — exit 1 (S9) | 7 — exit 1 (ReadyControls) |
| V3 no-name | 2 — exit 1 (S7, S8) | **0 — exit 0 (survives)** |
| V4 no-dedupe | 1 — exit 1 (S7 `kama-n,kama-n`) | **0 — exit 0 (survives)** |
| V5 grep fallback | 2 — exit 1 (S7, S8: served `-`) | **0 — exit 0 (survives)** |

## Findings

**F1 — The check.py logic does catch early-fill, keyed on the observed verdict.**
- Code: `check.py:354-355`, `if verdict not in ("MODEL_OK", "MODEL_MISMATCH"): return "-"`.
- With the real probe the gate passes all 11 scratch rows; V1 fails 7 of 11.
- The 401, 403, 503-loading, 503-other, 5xx, 404 and 200-no-array paths are all detected once a row's body carries ids.

**F2 — The shipped gate cannot catch early-fill.**
- Of the 72 lane rows, 61 expect a verdict other than MODEL_OK or MODEL_MISMATCH. The `/v1/models` body of every one of those 61 yields **0** ids under `served_ids_of`.
- So V1 emits `-` on all of them and passes 72/72 (exit 0).
- The served_model check on those 61 rows only detects constant forgeries, the kind the F5 control injects (`fault-controls.py:32`, "served_model forced to \"kama-forged-id\""). It does not detect body-derived leakage.
- All 11 MODEL_OK/MISMATCH rows win on `data[].id`. No row exercises `models[].id`, `.name`-only, `.model`, top-level `id`, or duplicate ids, which is why V3, V4 and V5 also survive the lane matrix.
- [INFERENCE] The claim "grades served_model" holds as code. As detector power it is limited to the `data[]`-vs-`models[].name` precedence (V2) and to forged constants.

**F3 — The oracle is a copy, not an independent derivation.**
- `check.py:294` says "Extract served ids from a /v1/models body exactly as the probe does", and `check.py:296` says "Mirrors tools/kama-probe.sh served_ids() (lines 335-368, python3 path)".
- The precedence tuple is the same in all three files: `kama-probe.sh:358-362`, `check.py:318-322`, `fault-controls.py:393-397`. All three dedupe with `dict.fromkeys` (`:366`, `:325`, `:400`). Diffing the probe and check.py blocks shows only layout differences (`diff` exit 1 on whitespace and wrapping).
- The `-` rule for other verdicts restates `classify()` control flow (`check.py:342-348` cites `kama-probe.sh:455` and `:524-529`). The contract header (`kama-probe.sh:43-48`) does not state it.
- Consequence: any error in the precedence specification itself is shared by the probe, the oracle and the detector, so none of them can see it.
- `fault-controls.py` `contract_served_model` (`:404-447`) is a second gating derivation (keyed on 2xx status plus a model array, not on the observed verdict). Across all 83 rows (72 lane + 11 scratch) it gives the same value as check.py's derivation in every case: 0 disagreements.

**F4 — The only external anchor cannot tell precedence variants apart.**
- In the three real b11755 receipts (`.ufo/waves/round-17/live/receipt-{1,2,3}.json`), `data[].id`, `models[].name` and `models[].model` all equal the `--alias` value `kama-live-probe`.
- `served_ids_of` returns `['kama-live-probe']` on all three, which matches the probe rows. But V2 and V3 would produce the same value on those bodies.
- So no live evidence independently confirms the precedence order.

**F5 — "Exactly as the probe does" is false beyond the python parse.** Edge rows `EDGE.json` against the real probe, exit 1:
- An id containing `\n`: probe `'a,b'`, oracle `'a\nb'`. **FAIL.**
- A trailing `\n`: probe `'kama'`, oracle `'kama\n'`. **FAIL.**
- A comma inside one id (`'a,b'`) cannot be told apart from two ids `a`, `b`; both rows pass. A probe that splits or merges on commas is therefore undetectable.
- Quote/backslash, tab, CR, unicode and a `-` id all passed.
- The oracle copies the python layer but not the bash `print("\n".join)` → `tr '\n' ','` transport (`kama-probe.sh:366`, `:527`).
- Severity: low. These ids are implausible live.
- Side observation: V5 shows the probe's own grep fallback (`kama-probe.sh:371-376`) returns `-` for a `models[].name`-only body, giving `MODEL_MISMATCH unresolvable-id` for S8 where the python path gives `matched`. No row grades the no-python path.

## Impacted axes
- Calibration (C1 detector power): the claim is true as code but weak with the shipped matrix.
- Provenance of the oracle: the docstring is honest that it is a mirror. "Derived from each row's own literal body" is accurate, but it does not mean independent.

## Smallest safe correction
1. Add rows like S1-S11 that carry ids on paths with other verdicts and exercise the non-`data[]` groups. With the real probe they pass 11/11 here; V1, V3, V4 and V2 each fail at least 1.
   - Tradeoff: C1 says "The nine matrix files … stay byte-identical". So this goes in a new matrix file in a later round, or into a probe-mutant control. It is not a silent edit.
2. Add probe-side mutants (V1 early-fill, V3, V4) to the `mutants.py --grid` / fault-control counting so detector power over probe defects is measured, not only check.py-weakening mutants.
3. In SKILL/lesson text, state that the served_ids oracle is a shared copy, and record its line-transport divergence (F5). Optionally, have the oracle split on `\n` and join on `,` to match the transport.

## Commands (all run in /tmp clone/scratch, `PYTHONDONTWRITEBYTECODE=1`)
- `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/ServedModelOracle-clone && git -C … checkout -q 54a29268…` → exit 0
- Scratch `matrix/check.py --probe tools/<variant>.sh --json` for real, V1-V5 and the clone's real probe → exit 0 for both real probes; exit 1 for V1-V5
- Clone `tests/probe-verdicts/check.py --probe tools/<variant>.sh --json` → exit 0 for real, clone-real, V1, V3, V4, V5; exit 1 for V2
- `matrix2/check.py --probe <clone>/tools/kama-probe.sh --json` (EDGE rows) → exit 1 (E1, E4)
- Python cross-checks with `served_ids_of` / `contract_served_model` imported from the clone, plus the live-receipt anchor → recorded above
- `ss -ltnp` with a cmdline filter → 0 listeners of mine. Only check.py's own ephemeral 127.0.0.1:0 stubs were started; no llama-server. Ports 8080 and 34113 and the registry ports were not contacted.

## Limitations
- Probe variants are single-edit hand mutants, not an exhaustive grid.
- I did not run the frozen check.py against V1. [INFERENCE] It cannot catch V1, because frozen check.py does not grade served_model (`round-17.md:20-21`).
- The fault-controls detector was not run against the probe variants. It corrupts records, not the probe.

## Installs
None.
