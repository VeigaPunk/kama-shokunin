Seat: F32W1ProbeFindings
Axes: operability, calibration.
Evidence: W1 P01ErrorSignatures findings and raw captures (four live runs, v0.40.11), plus frozen claims.
P01 supports exact observed endpoint signatures, and /api/ps residency transition; scope is version/model/run-bounded.
Key distinction: /api/tags and /v1/models inventory do not imply residency; /api/ps distinguishes loaded state.
F1-F7 claims supported only where tied to raw endpoint/state observations; no clear contradiction found.
Overclaim risk: extrapolation beyond captured version, payloads, endpoints, or fixture; P01 states bounds.
Cross-check caveat: assigned W1 artifacts do not include lane skill/probe-table/docs row for comparison.
Move: keep endpoint+state-specific distinctions in C2 statements; no predicate or verdict change.
Risk: capture observations may be misread as cross-version protocol guarantees.
Verification: raw captures corroborate; independent rerun not performed; no tool installation.
Detailed evidence: .ufo/waves/round-60/w2/out/F32W1ProbeFindings/findings.md