VERDICT: confirm — v2 misclassified consistency now follows outcome buckets; the exact rawbefore k16 mismatch has a regression fixture.

# Axes

- Operability: deterministic serial before/after controls runs, bounded subprocesses, frozen-byte pinning and reportable exit states.
- Calibration: counts are read from the controls JSON rather than inferred when absent; the self-mutant detector records `site_missing`, unstable baselines and the exact changed signature.

# Delivered

- New file: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/C1Measure-2/measure.py`
- SHA-256: `55b26b3b47e316f6b013fae980550073bad3972009c7dcee75d8d0da9e568c17` (69,785 bytes).
- New file, so no frozen-copy unified diff was produced. The lane target itself was not edited; L1 integrates from `build/out`.
- Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/advice/C1Measure.md`

# Behavior and evidence

- Measurement runs the same `controls.py --json` serially against frozen then current tool/gate. It hashes the script, controls, tools, gates, probe and controls-resolved registry; records raw and canonical controls-JSON digests; reports before/after count deltas and per-control classification diffs. Frozen inputs are refused unless their exact bytes match the round-start Git blobs. `measure.py:185-218` — quote: “git -C ... show”; `measure.py:745-814` — quote: “before = frozen pair, after = current pair”.
- The v1 compatibility path derives only `good_rejected` from `good_ok`; it leaves `misclassified` and `uncontrolled_checks` null and makes the result not-clean rather than inventing those values. `model_unchanged` is excluded from `uncontrolled_checks`. `measure.py:440-576` — quote: “misclassified: not reported by kama-live-controls/v1”; `measure.py:598-610` — quote: “fails the four requested count criteria”.
- The three single-site self-mutants are exact-string edits on a staged copy. A missing/ambiguous/invalid site is reported distinctly; numeric comparison includes the gate-flip arm count, and only stable baseline differences earn kill credit. `measure.py:134-149` — quote: “drop-gate-flip-arm”; `measure.py:817-1000` — quote: “site_missing”; `measure.py:1332-1518` — selftest and classifier cases.
- Frozen-byte check during the final measurement: `tools/kama-llamacpp-live.py` SHA-256 `0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac`, 57,556 bytes, verified against `e75cf680b53484a61709ee1b2787d8dbc6419f74:tools/kama-llamacpp-live.py`; `tests/llamacpp-live/check-receipt.py` SHA-256 `ad6801791f2ada896a7ee188609391aac86185c47320dbf415331869ca9cd2a5`, 60,756 bytes, verified against the corresponding Git blob.
- Input SHA-256 values in that run: controls `aad8b1c758fe9616ecd7ad78538dbfd82227c7e99df3b051d2bf82d34d6e3a06`; probe `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`; registry `bf343625188d9f486a6f6d13c60c946e23c21d05ee1bef881204dfa14c62bc6c`. Current tool/gate were byte-identical to the frozen tool/gate in this clone.
- Frozen-controls comparison (scratch/advisory): `accepted_bad` 0→0; `good_rejected` 0→0 (derived from `good_ok=true`); `misclassified` unavailable→unavailable; `uncontrolled_checks` unavailable→unavailable; `good_ok=true` on both sides; gate-flip arms 8→8. Both controls JSON stdout digests were `75fd6ca93d423c68ecae57937a0577e308fe1e8d10d0f2f22b298b379ce7a315`; both canonical digests were `ec9fa14f55a77ca7d10a3bb6d124a25145201ebd333db8bc92fce316f7700597`. The command exited 1 because the v1 controls cannot report the two required coverage metrics; this is the intended honest result, not a pass.
- Frozen-controls self-mutants (scratch/advisory): exit 1; both numeric baselines were stable. `drop-gate-flip-arm` was killed on current and frozen pairs by `gate_flip_arms: 8 -> 0`; `loosen-k0-exit` survived because this run did not exercise its `tool_exit == -15` branch; `k6-any-nonzero` was `site_missing` in frozen v1 controls. Frozen controls’ `--selftest` is unavailable (argparse exit 2 because frozen v1 requires `--tool` and `--gate`); numeric runs were used instead.

# Commands run (in `/tmp/kama-r18-C1Measure`)

- `python3 -m py_compile .ufo/waves/round-18/c1/measure.py` — exit 0.
- `python3 -B .ufo/waves/round-18/c1/measure.py --selftest` — exit 0; 36/36 cases passed.
- `python3 -B .ufo/waves/round-18/c1/measure.py --controls tests/llamacpp-live/controls.py --frozen-tool .ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py --frozen-gate .ufo/waves/round-18/frozen/tests_llamacpp-live_check-receipt.py --tool tools/kama-llamacpp-live.py --gate tests/llamacpp-live/check-receipt.py --probe tools/kama-probe.sh --out /tmp/kama-r18-C1Measure-evidence/measure-frozen-controls-final.json` — exit 1, as described above.
- `python3 -B .ufo/waves/round-18/c1/measure.py --self-mutants --controls tests/llamacpp-live/controls.py --frozen-tool .ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py --frozen-gate .ufo/waves/round-18/frozen/tests_llamacpp-live_check-receipt.py --tool tools/kama-llamacpp-live.py --gate tests/llamacpp-live/check-receipt.py --probe tools/kama-probe.sh --out /tmp/kama-r18-C1Measure-evidence/self-mutants-final.json` — exit 1; one killed, one survived, one `site_missing`, per the classifications above.
- `ss -ltnp` after the final run — exit 0; no listener on 8080 or 34113 and no fake control listener remained.

# Risks and limitations

- The earlier scratch behavior run used frozen v1 controls. L1's later c6dc46f run supplied the actual v2 output used for the regression fixture; L1 should rerun the counter with this corrected code.
- A consistently falsified controls report (self-consistent but wrong counts and classifications) is outside this counter’s ability to detect. Staged self-mutants preserve controls-directory siblings and registry, but code that reads other external lane files may still differ. A leaked daemon that re-execs without retaining the scratch path in its command line may escape process cleanup.
- `loosen-k0-exit` survived the frozen K0 observations because the accepted `-15` path was not observed. `k6-any-nonzero` was `site_missing` only in frozen v1; its current v2 source anchor is present, as confirmed below.
- No tools were installed or updated.

## Follow-up: integrated controls exact-site compatibility

- Checked only the three self-mutant source anchors against the integrated `tests/llamacpp-live/controls.py`; each exact source string in `measure.py:138-150` occurs once, so no compatible alternatives were needed. `controls.py:1135` — quote: `gate_flip = _gate_flip(st, gate, receipt_doc, failed)`; `controls.py:1028` — quote: `accepted = (tool_exit == 0 and gate_exit == 0`; `controls.py:1031` — quote: `exit_ok = tool_exit in spec.exits`.
- The previously observed `k6-any-nonzero: site_missing` applied to frozen v1 only; integrated v2 has the exact K6 anchor. The K0 `accepted` expression is in the shared `classify_run` path, not a dedicated K0-only block; the existing edit matches, and this follow-up did not change mutant scope.
- No controls run, build, test, or selftest was run for this interface-only follow-up. The refreshed delivered file is byte-identical to the prior copy: SHA-256 `55b26b3b47e316f6b013fae980550073bad3972009c7dcee75d8d0da9e568c17`.

## Follow-up: misclassified bucket root fix

- Root cause: v2 preserves two axes. `classification` is the observed result; `bucket` records whether it matched the control's expected outcome. The top-level `misclassified` count is aggregated from `bucket`, not the classification string. `controls.py:56-60` — quote: “any other mismatch -> misclassified”; `controls.py:1248-1249` — quote: `res[r['bucket']] += 1`.
- `measure.py` now cross-checks `misclassified` against row `bucket` when present, preserves classification and bucket separately in row summaries/diffs and self-mutant signatures, and uses classification only as the compatibility fallback for older reported rows without bucket. Invalid present buckets remain faults; the consistency check is not suppressed. `measure.py:491-503,572-585,658-705` — quote: `bucket_source = 'reported'`.
- Added a selftest projection of the exact rawbefore `k16` record: `.ufo/waves/round-18/runs/c1-measure.json` `.runs.before.doc.controls[id=k16]` — quote: `"classification":"rejected-targeted","bucket":"misclassified","expected":"not-evaluated"`. The fixture asserts the top-level count remains 1 while preserving both row values. `measure.py:1406-1429` — quote: `rawbefore k16: count bucket without relabeling classification`.
- Verification in the clone: `python3 -m py_compile .ufo/waves/round-18/c1/measure.py` exited 0; `python3 -B .ufo/waves/round-18/c1/measure.py --selftest` exited 0 (38/38). No real controls run was performed; L1 owns the counter rerun.
- Refreshed deliverable: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/C1Measure-2/measure.py`, SHA-256 `a9577ed889572e929b404268b87d50000c56e62c36e6c54f6f9113a3012a490f`. New-file deliverable; no unified diff.
