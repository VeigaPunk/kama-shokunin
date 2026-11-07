# EX01HeldOutCells — round-92 C2 held-out cells (BASE vs M2)

## Scope
Held-out cells for C2 operability (not in `tools/round92-linear-paths.py`): BASE probe
`git show ed018ca0fa956c5052b3dc6b714a2cb72973da21:tools/kama-probe.sh` (sha256
0aa43573be3a52fa22d9b419049814133324e423dcd22429f107ad28ee0a75da) vs M2 probe
`git show fa8aedb73d18448383c7a4d75405aba448fe8e38:tools/kama-probe.sh` (sha256
36631d498901c40f76e1c36471166fecb71a2e84124c4795c301e9e8e5cbf962), run against
lane-owned loopback stubs (free ports, killed via context exit). Kill 180 s per run.
Harm = base right and M2 differs (verdict/reason/bytes). Reusable script + raw results:
`held_out.py` + `results.json` in this out dir.

## Commands and outputs
```
mkdir -p /fast/scratch/hyaku/kama-r92/EX01HeldOutCells
git show ed018ca0fa956c5052b3dc6b714a2cb72973da21:tools/kama-probe.sh > .../base.sh  # rc=0
git show fa8aedb73d18448383c7a4d75405aba448fe8e38:tools/kama-probe.sh > .../m2.sh    # rc=0
python3 held_out.py --base .../base.sh --m2 .../m2.sh --out results.json --kill 180  # rc=0
uptime  # load 34-62 (high host load) during runs; see results.json times
```
H6 sizing note: 80 000 entries with per-entry paths exceed the 4 MiB `MAX_BODY` cap
(min ~55 B/entry ≈ 4.4 MB), so H6 uses the path-missing form (no `path` field) —
body 3.28 MB. This matches the frozen counter D9, whose top-level `path` is not
`status.args`, so `file_state` returns `-` (undecidable, stays loadable) in both probes.

| cell | BASE verdict rc sec | M2 verdict rc sec | harm |
|---|---|---|---|
| H1 models[] not data[], 200k ids, expect m000123 | MODEL_OK matched 0 1.84 | MODEL_OK matched 0 1.72 | no (bytes equal, len 1601006) |
| H2 ids under `model` key, 5000 | MODEL_MISMATCH served-id-mismatch 2 0.15 | same 2 0.16 | no (bytes equal) |
| H3 CRLF inside ids (good, a\r\nb, c\r\nd, x\ry, p\nq) | MODEL_OK matched 0 0.16 | same 0 0.16 | no (bytes equal) |
| H4 100k duplicate ids "good" | MODEL_OK matched 0 1.38 | same 0 1.34 | no (bytes equal) |
| H5 router 60k entries status unloaded failed:true | MODEL_UNLOADED router-unloaded-failed 2 1.36 | same 2 1.28 | no (bytes equal) |
| H6 router autoload, 80k unloaded matching, path missing | killed 180 s | MODEL_OK router-unloaded-autoload 0 3.44 | no (M2 fixes super-linear path; not harm) |
| H7 table mode (no --json), 1.9 MB backslash id | killed 180 s | MODEL_MISMATCH 2 3.44 (3.8 MB output) | no (M2 fixes jstr; not harm) |
| H8 registry-mode `check --registry` 3 rows (good/missing/*) | row0 MODEL_OK, row1 MODEL_MISMATCH, row2 MODEL_OK, rc 2, 0.65 s | identical rows, rc 2, 0.56 s | no (byte diff was temp registry paths; same-dir re-run byte-equal) |
| H9 SECOND snapshot over 16k ids | first run killed 180 s (no baseline; both runs killed) | first 0.6 s, second 1.16 s, transitions=0 (identical), drift-second transitions=3 (verdict/reason/served) rc 2 | no (base cannot produce baseline in budget) |
| H10 served list mixing quotes/backslashes/controls, 30k ids (~268 B each) | MODEL_MISMATCH served-id-mismatch 2 0.18 | same 2 0.18 | no (bytes equal) |

## Findings
- NOTE (held_out.py:60-68 `record`; results.json): no harm. All cells where base completes are byte-equal base==M2 (H1-H5, H10; H8 byte-equal on same-dir re-run). Cells where base times out (H6, H7, H9-first) are the C2 super-linear paths M2 fixes; M2 answers are semantically correct (H6 router-unloaded-autoload via 80k file_states args, H7 MODEL_MISMATCH with 3.8 MB escaped output, H9 transitions=0 identical / 3 on drift).
- NOTE (H9): seat asked "second snapshot so DELTA transitions are computed". Base cannot complete even the first 16k snapshot in 180 s (counter L5 already: killed at 120 s). M2 second snapshot over identical answers correctly records 0 transitions and does not advance baseline; with drifted answers (x99999 only) it records verdict/reason/served_model transitions and flips to MODEL_MISMATCH rc=2.
- NOTE (H6): 80k entries with real per-entry paths cannot be built under the probe's 4 MiB cap; the path-missing form exercises the same `router_file_states` 80k-argv + cand-array scale. A genuine missing-file sweep at 80k would need entries ≤ ~52 B, impossible with id+status+args present.

## Deliverables
- `.ufo/waves/round-92/w1/out/EX01HeldOutCells/held_out.py` — reusable held-out runner (usage in docstring)
- `.ufo/waves/round-92/w1/out/EX01HeldOutCells/results.json` — raw per-cell verdicts/rc/seconds/hashes
- `.ufo/waves/round-92/w1/out/EX01HeldOutCells/run2.log` — suite stdout log

VERDICT: holds — no held-out harm; base==M2 byte-equal where base completes, M2 fixes H6/H7/H9 timeouts with correct verdicts.
