# EX01HeldOutBudget — held-out router-budget shapes for round-94 C1

## Scope

Attacked and corroborated C1 (`tools/kama-probe.sh` per-file GGUF parse deadline) on stubs at base `e6f1dcce` and M1 `a27656a454b1a2364f8b6e55f42fbca8c2e86ee4`. Reused `tools/round94-router-budget.py` Stub/gguf/router_body/PROPS machinery verbatim; never edited lane files. All timing under natural host load (loadavg 148–222, no synthetic burners added).

## Commands and outputs

- `python3 e2e.py` (scratch `/fast/scratch/hyaku/kama-r94/EX01HeldOutBudget/e2e.py`) — exit 0, wrote `e2e.out`
- Direct `ROUTER_PY files` probes with `timeout 60`/`timeout 8` wrappers — exit 0/124, logged in `sweep.log` / `direct-probe.log`
- 16384-repeat body-size check: `router_body` accepted 3 309 594 bytes (< 4 MiB cap)

## Findings

### (a) N distinct slow invalid GGUFs — flip point and time

Direct `files` probe (natural load ~200):

| N | base invalid/undecided | base t | m1 invalid/undecided | m1 t (wrap60) |
|---|------------------------|--------|----------------------|---------------|
| 2 | 1/1 | 4.11s | 2/0 | 5.07s |
| 4 | 1/3 | 4.24s | 4/0 | 9.82s |
| 8 | 1/7 | 4.28s | 8/0 | 22.27s |
| 16 | 1/15 | 4.39s | 16/0 | 59.30s |
| 32 | 2/30 | 4.54s | 21/0 (rc=124 @60s) | 60.02s |
| 64 | 1/63 | 5.20s | 23/0 (rc=124) | 60.02s |
| 128 | 1/127 | 5.84s | — | — |
| 256 | 1/255 | 9.11s | — | — |

E2E `check` verdicts:

| cell | base verdict/reason | base t | m1 verdict/reason | m1 t |
|------|--------------------|--------|--------------------|-----|
| a-distinct-N2 | MODEL_OK / router-unloaded-autoload | 5.20s | MODEL_UNLOADED / router-model-invalid | 7.43s |
| a-distinct-N4 | MODEL_OK / router-unloaded-autoload | 5.11s | MODEL_UNLOADED / router-model-invalid | 12.58s |
| a-distinct-N8 | MODEL_OK / router-unloaded-autoload | 5.27s | MODEL_UNLOADED / router-model-invalid | 26.05s |

**DEFECT (base, confirmed):** shared 4 s `DEADLINE` starves all but the first slow file; undecided (`-`) candidates are graded loadable by the round-89 rule → `MODEL_OK`/`router-unloaded-autoload` for a listing of 2–256 distinct slow invalid GGUFs. Flip is immediate at N=2.

**NOTE (M1, fixed):** per-file `PER_FILE_SECONDS=15.0` gives each candidate its own budget; N=2/4/8 all reach `MODEL_UNLOADED`/`router-model-invalid`. Time scales linearly (~2.5–3.3 s/file under load ~200): N=8 → 26 s, N=16 → 59 s.

**NOTE (M1, disclosed limit):** the `timeout 60` wrapper kills the `files` call at N≈21–24 distinct slow files (~60 s wall). Unfinished candidates stay undecided → loadable → `MODEL_OK` flip returns. This is the disclosed wall-clock limit in the claim, not a predicate violation: the counter's own 20 s cell budget never reaches this N.

### (b) one slow invalid file listed 4096 and 16384 times

| rep | base verdict/reason | base t | m1 verdict/reason | m1 t |
|-----|--------------------|--------|--------------------|-----|
| 4096 | MODEL_UNLOADED / router-model-invalid | 6.04s | MODEL_UNLOADED / router-model-invalid | 5.47s |
| 16384 | MODEL_UNLOADED / router-model-invalid | 6.95s | MODEL_UNLOADED / router-model-invalid | 7.56s |

**NOTE:** `SEEN` memo (device/inode/size/mtime/ctime key, r93) collapses repeats to one parse; both revisions identical. 16384-entry body = 3 309 594 B < 4 MiB cap. No flip at any repeat count.

### (c) slow VALID GGUF repeated 2048 times → MODEL_OK

| rev | verdict/reason | t |
|-----|---------------|---|
| base | MODEL_OK / router-unloaded-autoload | 5.84s |
| m1 | MODEL_OK / router-unloaded-autoload | 4.69s |

**NOTE:** valid file parses `ok` → file_state `-` → loadable; identical on both.

### (d) mixed valid+invalid, invalid slow and listed LAST

64 × valid `ok.gguf` + 1 × slow `slow-bad.gguf` at index 64:

| rev | verdict/reason | t |
|-----|---------------|---|
| base | MODEL_OK / router-unloaded-autoload | 4.69s |
| m1 | MODEL_OK / router-unloaded-autoload | 3.60s |

**NOTE:** `router_refine` sets `unloaded=1` when `nbad < ncand` — any loadable candidate wins. The 64 valid entries make the router autoload-able regardless of the invalid tail; the slow invalid's state is irrelevant to the verdict. Direct `files` probe confirms M1 does parse index 64 as `invalid` in 2.73 s (per-file deadline reaches it), but the verdict is unchanged because valid candidates exist. No defect; expected router semantics.

### (e) slow file as `--mmproj` of distinct valid models

8 entries `[exe, -m, valid-N.gguf, --mmproj, slow-bad.gguf]`:

| rev | verdict/reason | t |
|-----|---------------|---|
| base | MODEL_UNLOADED / router-model-invalid | 4.39s |
| m1 | MODEL_UNLOADED / router-model-invalid | 5.12s |

**NOTE:** `file_state` scans all `PATH_FLAGS` including `--mmproj`; invalid mmproj → `invalid` state → `nbad == ncand` → `MODEL_UNLOADED`. Identical on both; mmproj path is covered by the same per-file deadline.

## Deliverables

- `.ufo/waves/round-94/w1/out/EX01HeldOutBudget/e2e.out` — 14 e2e cell rows (verdict/reason/time per rev)
- `.ufo/waves/round-94/w1/out/EX01HeldOutBudget/direct-probe.log` — 32 direct `files` probe timings (N=2..256, wrap 60/8)
- `.ufo/waves/round-94/w1/out/EX01HeldOutBudget/e2e.py` — sweep harness (reuses frozen counter machinery)

## Risks and blockers

- Host load 148–222 throughout; absolute times are load-sensitive. Within-run ratios (base ~4 s flat vs M1 linear ~2.5–3.3 s/file) are the reliable signal.
- M1 N≥24 distinct slow files exceeds the 60 s wrapper → disclosed limit, not a defect.
- Cell (d) is a semantic NOTE, not a falsification: mixed loadable+unloadable correctly yields MODEL_OK on both revisions.

VERDICT: holds — per-file deadline fixes the shared-budget starvation at N=2..16; disclosed 60 s wrapper limit confirmed at N≈21–24; repeats/mmproj/mixed cells identical or correct on both revisions.
