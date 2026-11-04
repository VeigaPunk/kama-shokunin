## Correction — round 83

Line 5's recheck command was unrunnable as introduced (`962bd251`). It read
`python3 tools/pin-watch.py check --repo .`; `tools/pin-watch.py` has never accepted `--repo` — the command
exits 2 with `the following arguments are required: --pins`. The corrected command is
`python3 tools/pin-watch.py check --pins registry/engine-pins.tsv`; run 2026-11-04 it exits 1 with three
`status=behind` lines (a `behind` count is a recheck trigger, not a failure). The command cell was repaired
in place at `8a3e8af2`; this block records the superseded text, per round-82 `SK01` D1
(`.ufo/waves/round-82/w1/SK01PinRecon/SK01.md:37`, `raw-fetch-log.md:336`).
