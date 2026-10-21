VERDICT: confirm - all four outputs match Round 20 byte-for-byte

Axes: operability (15-cell evaluation) and calibration (pinned outcomes/source checks).

Checkout: scratch clone `/tmp/kama-r21-RegressErrorCensus-6/lane`, HEAD `a29bb84abbb8b4d328f5970a89e448330a3a42ac`; lane checkout was not edited.

Commands and observed exits (each stdout/stderr captured in scratch):

| Command | Exit | Key stdout |
|---|---:|---|
| `python3 tools/error-verdict-census.py --arm frozen --json` | 1 | 15 cells; frozen_misclassified=6; frozen_witness_mismatches=0; red_vector_mismatches=0; frozen_errors=3; unrun=[] |
| `python3 tools/error-verdict-census.py --arm current --json` | 0 | 15 cells; current_misclassified=0; current_errors=8; unrun=[] |
| `python3 tools/error-verdict-census.py --json` | 0 | 15 cells; frozen/current misclassified=6/0; witness/red-vector mismatches=0/0; errors=3/8; unrun=[] |
| `python3 tools/error-verdict-census.py --selftest` | 0 | `selftest: ok (15 pinned cells; manifest guards; error/verdict controls; survivor arm only)` |

Comparison against `.ufo/waves/round-20/runs/9add96e4/error-{frozen,current,pair,selftest}.{stdout,stderr}`: all eight `diff -u` commands exited 0; no diff hunks. Round-20 recorded exits were 1, 0, 0, 0 respectively, identical to this run. Current/official stdout SHA-256 pairs were identical: frozen `89b54fd476752e743407d66a9b7105fc9ffaa4f2a9d50c1579a21681a17c5683`; current `51745c91199adb5f6242dbf3c16cf39f4cab535b9af4ba45ab0acb4c2e93c5ab`; pair `924d52bc8e194e5b40e63f80dc854b0c1c6ff918d93c843a267aa2a1e30db425`; selftest `ce852f07092b579e2701ddec42087224d118ca4925f5be31e47fc6e66bf67d88`.

Digest evidence: `registry/error-injection-cells.json` SHA-256 is the pinned `ff3b7da9c060a7f12a7ca081c79db06899a4f5c9418d26ffe4a88bc6c607f469`. All three fixture hashes matched the runner pins: `grid-gate.py` `0e65e584fe9d7bda52af233c7fd189555d4314b1b7ae6267b12cbf1e2d3bbb5f`; `sitecustomize.py` `6a467c6306862d740416a34b22178d3aae3f72812a43de0387df91bbd5e06ab1`; `survivor-arm-probe.py` `bf031256913317e688362adc0f663f6fce77228eba00a265c11adfc8deb95014`. `git show 37bd4c5bd456a2f8a54d3312c28495c321715856:<instrument> | sha256sum` matched all frozen-source pins: install-tree grid `6f51803c47db597e2f6778b492bfaba14735a23c599bc972f8d33ab477a68f05`; citation provenance `5c887572b37a80c0757b59a7735da386be2885e463ec2682c1d59f8e9b55110b`; survivor arm `ac934794af1eee8067ea11f7f8cc31702ea7dfad257fec2649f2d638477bac75`. Census runs completed without manifest, fixture, or frozen-source digest errors.

Finding: no pinned cell changed and no census digest pin changed or failed. The `--selftest` still reports 15 pinned cells; all census JSON results are byte-identical to Round 20. [INFERENCE] The census pins instrument/fixture/manifest identities, not `check-receipt.py` or `tools/kama-llamacpp-live.py`; its grid run stages the pinned `grid-gate.py` fixture. Thus the receipt-gate selftest-count and producer changes are outside these four census executions and cannot account for a census-output change. No separate `check-receipt.py --selftest` or producer behavior was measured here.

Files changed: this advisory report only. Risks/blockers: none for the requested census comparison; standalone receipt-gate selftest behavior was not in scope.