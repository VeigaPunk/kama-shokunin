VERDICT: confirm - six malformed-hex CLI pin cases added to the gate selftest.

Axes: operability (pin intake) and calibration (format refusal). Changed only `/tmp/kama-r19-PinFormatTests/tests/llamacpp-live/check-receipt.py`; each of model, server, server-impl, install-tree, probe, and tool uses the valid base receipt plus a 64-character value ending in invalid hex `g`. Expected exit: 1 (`INVALID`) for each. [INFERENCE] These expected exits are encoded in the selftest but were not exercised in this editing wave.

Receipt: `/tmp/kama-r19-PinFormatTests/out/PinFormatTests.receipt.txt`. Executed `mkdir -p out && sha256sum tests/llamacpp-live/check-receipt.py` from `/tmp/kama-r19-PinFormatTests`; exit 0; stdout `759ea7281b25b29f05e9c5fb1c36f44ea466d163beae688492af4ecadbf7d62a  tests/llamacpp-live/check-receipt.py`. Selftest not run; parent owns post-integration checks. No installs. No blockers.
