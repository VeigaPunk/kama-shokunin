VERDICT: confirm — the R18 frozen-arm counts and the R17 committed 6/1 baseline reproduce on the assigned commit.

# Scope and axes

Axes attacked: **C1 operability (8→8, no score movement claimed)** and calibration of the C1 frozen-arm measurement. This is a bounded rerun, not an outside non-author admission; L1 owns admission. Round 18 assigns the v3 tool/gate and controls to C1 and states the not-evaluated/failure split (`corpus/lessons/round-18.md:13-29`; `SCORECARD.md:744-751`). KQ24’s rule is that an unobserved trigger is not-evaluated, neither pass nor failure (`corpus/QUALITY.md:125-133`).

# Results

## R18 exact counting invocation at the assigned revision

Clone command:

```sh
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen && git -C /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen switch -q -c seat/KamaR18.RerunC1Frozen 1c325b2e58fcfdc6761f645b44cedfb1d65243e6
```

`git -C /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen rev-parse HEAD` → `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`.

I ran `/usr/bin/python3 /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/.ufo/waves/round-18/c1/measure.py --help`; it exposed measurement mode with `--controls`, `--frozen-tool`, `--frozen-gate`, `--tool`, `--gate`, `--probe`, `--json`, and `--out`, as well as `--selftest` and self-mutant modes. The official raw argv is `runs/commands.json:169-198`; the following rerun preserves those options and inputs, changing only the lane root to the required clone and the output location to scratch:

```sh
/usr/bin/python3 /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/.ufo/waves/round-18/c1/measure.py --controls /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/tests/llamacpp-live/controls.py --frozen-tool /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py --frozen-gate /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/.ufo/waves/round-18/frozen/tests_llamacpp-live_check-receipt.py --tool /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/tools/kama-llamacpp-live.py --gate /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/tests/llamacpp-live/check-receipt.py --probe /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/tools/kama-probe.sh --json --out /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/c1-current-controls.json > /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/c1-current-controls.stdout 2> /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/c1-current-controls.stderr
```

Process exit **0** (`EXIT=0`); JSON says `exit: 0`, `current_clean: true`, `faults: []`. Stderr was empty (SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`). Captured JSON/stdout SHA-256: `7429abd92c0071a8729360f7c7d4c0a9e65dffc03bac63c70b506e0f1d0d5873` (the `--out` JSON and stdout were byte-identical). Both measure arms report `leaked_processes: []`.

### R18 current controls: frozen v2 before → current v3 after

| control | frozen before classification [counter bucket] | current after classification [counter bucket] |
|---|---|---|
| k0 | accepted [ok] | accepted [ok] |
| k1 | rejected-targeted [ok] | rejected-targeted [ok] |
| k2 | rejected-targeted [ok] | rejected-targeted [ok] |
| k3 | rejected-targeted [ok] | rejected-targeted [ok] |
| k4 | rejected-targeted [ok] | rejected-targeted [ok] |
| k5 | rejected-targeted [ok] | rejected-targeted [ok] |
| k6 | rejected-targeted [ok] | rejected-targeted [ok] |
| k7 | rejected-untargeted [ok] | rejected-untargeted [ok] |
| k8 | rejected-targeted [ok] | rejected-targeted [ok] |
| k9 | rejected-targeted [ok] | rejected-targeted [ok] |
| k10 | rejected-targeted [ok] | rejected-targeted [ok] |
| k11 | rejected-targeted [ok] | rejected-targeted [ok] |
| k12 | rejected-targeted [ok] | rejected-targeted [ok] |
| k13 | rejected-targeted [ok] | rejected-targeted [ok] |
| k14 | rejected-targeted [ok] | rejected-targeted [ok] |
| k15 | rejected-targeted [ok] | rejected-targeted [ok] |
| k16 zero-loading | rejected-targeted [misclassified] | not-evaluated [ok] |
| k17 IPv4-mapped dual-stack good listener | rejected-targeted [good_rejected] | accepted [ok] |
| k18 KeyboardInterrupt | accepted [accepted_bad] | rejected-targeted [ok] |
| k19 v3 schema floor | accepted [accepted_bad] | rejected-targeted [ok] |
| k20 exact argv | accepted [accepted_bad] | rejected-targeted [ok] |
| k21 every loading transition | accepted [accepted_bad] | rejected-targeted [ok] |
| k22 duplicate host flag | accepted [accepted_bad] | rejected-targeted [ok] |

Aggregate before → after: `accepted_bad` **5→0**; `good_rejected` **1→0**; `misclassified` **1→0**; `uncontrolled_checks` **0→0**; `gate_flip_bad` **0→0**; `inconclusive` **0→0**; `good_ok` true on both. Frozen before therefore has five accepted-bad controls (k18–k22), one false rejection (k17), and the zero-loading false failure (k16); v3 records the latter as not-evaluated and accepts k17. Every row is represented in the table; `[ok]` means the row’s result matched its expected classification.

**No schema/argparse credit:** k19’s frozen v2 gate reports `usage_error: true` and `flag_gate_exit: 2` for the unsupported `--require-schema v3` option; its fallback flagless run exits 0 and accepts the forged v1 receipt, so the before classification is `accepted`, not a rejection. The v3 gate reports `usage_error: false`, `flag_gate_exit: 1`, and the specific problem `schema 'kama-llamacpp-live/v1' is below --require-schema v3`; only that observed gate refusal is counted as `rejected-targeted` after. The before row remains one of the five accepted-bads. k20–k22 similarly change from gate VALID to gate INVALID naming argv/transition predicates, not a command-line failure.

### Reproduction of the R17 frozen baseline

For the separate historic comparison, the old round-17 controls were staged under a scratch lane-shaped directory because their `LANE` is derived from the script path. The controls bytes are the frozen copy `round-18/frozen/tests_llamacpp-live_controls.py` (SHA-256 `aad8b1c758fe9616ecd7ad78538dbfd82227c7e99df3b051d2bf82d34d6e3a06`; same as the round-17 control digest in `round-17/build/advice/C2Controls.md:7`). The old pair is `round-17/frozen`, not the R18 v2 comparator:

```sh
mkdir -p /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/r17-replay/tests/llamacpp-live /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/r17-replay/registry /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/r17-replay/tools /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/tmp
cp /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/.ufo/waves/round-18/frozen/tests_llamacpp-live_controls.py /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/r17-replay/tests/llamacpp-live/controls.py
git -C /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen show 54a29268e2083caa2b1e0d54ee1e7d90961302f3:registry/endpoint-consumers.tsv > /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/r17-replay/registry/endpoint-consumers.tsv
git -C /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen show 54a29268e2083caa2b1e0d54ee1e7d90961302f3:tools/kama-probe.sh > /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/r17-replay/tools/kama-probe.sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/tmp /usr/bin/python3 /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/r17-replay/tests/llamacpp-live/controls.py --tool /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/.ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py --gate /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/.ufo/waves/round-17/frozen/tests_llamacpp-live_check-receipt.py --probe /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/r17-replay/tools/kama-probe.sh --json > /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/r17-frozen-controls.json 2> /tmp/kama-r18-falsify-KamaR18.RerunC1Frozen/r17-frozen-controls.stderr
```

SHA-256 inputs: round-17 controls `aad8b1c758fe9616ecd7ad78538dbfd82227c7e99df3b051d2bf82d34d6e3a06`; frozen tool `b8c5e8d402595f3b919ea82f29c87f9a2b5d5c2d88bccffa48f1f8880c2f4fe4`; frozen gate `6b9576a13dde1872977a6af4547599a75cf484f37fe6fe0f4f5557349b09ced6`; probe from the reported 54a292 revision `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`; registry `bf343625188d9f486a6f6d13c60c946e23c21d05ee1bef881204dfa14c62bc6c`.

The controls process exit was **1**, the expected dirty-baseline result, not a harness/argparse fault. JSON stdout SHA-256 `dc293bb1deb3ddfc873bdc55a07f059a564a0d5e78fb23fc7333d26b73cea148`; stderr empty, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. It reported `accepted_bad: 6`, `gate_flip_bad: 0`, `inconclusive: 1`, `good_ok: true`, with the exact frozen tool/gate SHA values above. Per-control result: k0 accepted good; k1, k2, k4, k5, k6 and k8 accepted-bad; k3 inconclusive (tool 2 / gate 1, no targeted failed check); k7 rejected fail-closed (tool 2 / gate 1); k6 was an escape (tool 4, no receipt), not a targeted rejection. This matches the committed R17 frozen result and details (`round-17/build/advice/C2Controls.md:83-100`; `round-17/falsify/advice/RerunControlsFrozen.md:7-15`). No outcome discrepancy; the temporary path embedded in the k6 traceback is naturally different.

# Difference from the retained R18 official artifact

The preserved pre-integration official run is not overwritten: `round-18/runs/commands.json:169-198` records `c1-measure` exit **2**; `round-18/runs/c1-measure.json:424-427` gives the fault `before: misclassified=1 but 0 row(s) classified misclassified`. Its recorded raw counts are the same before/after values reproduced above (`runs/c1-measure.json:380-422`), but its counter rejected its own classification cross-check. On target commit `1c325...`, the input subject/control digests match the official record; the measure script is now SHA-256 `a9577ed889572e929b404268b87d50000c56e62c36e6c54f6f9113a3012a490f` (official measured script was `55b26b3b47e316f6b013fae980550073bad3972009c7dcee75d8d0da9e568c17`), correctly reports k16 as `misclassified` on the before arm, and the full measurement exits 0 with no faults. Thus the historic exit-2 remains a recorded counter failure; the new clone run is a separate corrected measurement.

# Cleanup, limits, installs

After both runs, the C1 measure reports no leaked processes on either arm; the scoped `pgrep -af 'kama-r18-falsify-KamaR18.RerunC1Frozen|fake_server.py|kama-llamacpp-live.py'` had no matching output. The post-run `ss -ltnp` snapshot showed no seat-owned listener and no ports 8080 or 34113; other shared-host loopback listeners, including Python listeners on ephemeral ports, were visible and left untouched rather than attributed or terminated. Tests use fake servers and do not establish behavior of a live llama.cpp service, registered consumer health, or untested checks. No ports/services/global configuration were changed. No tools installed or updated.

Files changed: this advisory report only, `.ufo/waves/round-18/falsify/advice/RerunC1Frozen.md`. No production, test, fleet, frozen-evidence, or historical lesson files changed. The clone, staged round-17 replay, output files, and other scratch under `/tmp/kama-r18-falsify-KamaR18.RerunC1Frozen` were removed before completion.
