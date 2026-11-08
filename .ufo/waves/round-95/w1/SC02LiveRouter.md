# SC02LiveRouter — live-router end-to-end attack on C1 (operability)

## Scope

Seat: SC02LiveRouter. Question: on a **real** lane-owned llama.cpp b12177 router (not the round-95
counter's stub HTTP server), does the round-95 tip probe (`tools/kama-probe.sh` at `f6325660`)
still decide the router file-state verdict from the bytes, and does the round-94 base probe
(`a27656a4`) still false-green there?

Base lane rev `2011161d5e5612fa953708cf54084b7f10ce99b1`; freeze `c798e831`; M1 probe `f6325660`;
M2 `beef8922`. Probes used, sha256 of the file bytes:

- tip  `436d994c71c0af3a96bc1f5ab0f884f629395313f3c02716738cf7af7931b722` (`git show f6325660:tools/kama-probe.sh`)
- base `27065a5c487ec819a975cc96d3c990ab5161d0e55d82be02a87dde86974ed3b4` (`git show a27656a4:tools/kama-probe.sh`)

Router binary `/home/vgpnk/.local/opt/llama-b12177/llama-server`, sha256
`ba272ee3446d9b98c9150c79667e6a8b217f25ee58ce0c6156cc96d2b5b362b0` (matches the pin in
`tools/round89-unloadable-cells.py`). Archive `b12177` sha256
`f50a52f4ba45dd5b4b906db97cf230ce2e3b1117a0b9017411322ecba63eea13` (verified). Build `b12177-6c01da627`.

No POST/completion was ever sent to any router. 127.0.0.1:1234 (the operator's live router) was
never contacted. Only `GET /v1/models` and `GET /props` were used, on free loopback ports owned by
this seat. Every router child was started with `start_new_session=True` (own process group) and
killed by `killpg` in a `finally`; the 64 burners of the load arm were also process-group-owned.

## Commands and outputs (exit codes)

```
$ sha256sum probe-tip/kama-probe.sh probe-base/kama-probe.sh
436d994c...b722  probe-tip/kama-probe.sh
27065a5c...ed3b4  probe-base/kama-probe.sh

$ python3 driver.py --phase live8   --files 8  --reps 2     # exit 0
$ python3 driver.py --phase live40  --files 40 --reps 2     # exit 0
$ python3 driver.py --phase live700k --files 8 --fxdir fx700k --reps 2   # exit 0
$ python3 driver.py --phase live40load --files 40 --reps 1 --burners 64  # exit 0
$ ORACLE_FX=fx8   python3 oracle.py    # exit 0
$ ORACLE_FX=fx700k python3 oracle.py   # exit 0
```

Router: `llama-server --models-dir <dir> --port <free> --host 127.0.0.1 --models-max 4`, with
`LLAMA_CACHE`/`HF_HOME` under the seat scratch. The router listed every fixture as
`status.value=unloaded` with `status.args` ending `--model <abs path>` (`live8-models.json`),
and `GET /props` returned `{"role":"router",...,"models_autoload":true,...}`.

### Per-repetition results (verdict / reason / exit / wall_s / load1 before→after)

| phase | n files | probe | rep | verdict | reason | exit | wall_s | load1 before→after |
|---|---|---|---|---|---|---|---|---|
| live8 | 8 | tip | 1 | MODEL_UNLOADED | router-model-invalid | 2 | 39.24 | 106.32→112.32 |
| live8 | 8 | tip | 2 | MODEL_UNLOADED | router-model-invalid | 2 | 54.13 | 122.43→127.61 |
| live8 | 8 | base | 1 | MODEL_UNLOADED | router-model-invalid | 2 | 53.40 | 112.32→122.43 |
| live8 | 8 | base | 2 | MODEL_UNLOADED | router-model-invalid | 2 | 57.21 | 127.61→137.37 |
| live40 | 40 | tip | 1 | MODEL_UNLOADED | router-model-invalid | 2 | 133.42 | 142.80→96.40 |
| live40 | 40 | tip | 2 | MODEL_UNLOADED | router-model-invalid | 2 | 158.35 | 93.98→124.04 |
| live40 | 40 | base | 1 | **MODEL_OK** | router-unloaded-autoload | **0** | **60.33** | 96.40→93.98 |
| live40 | 40 | base | 2 | **MODEL_OK** | router-unloaded-autoload | **0** | **60.43** | 124.04→98.36 |
| live40load | 40 | tip | 1 | MODEL_UNLOADED | router-model-invalid | 2 | 247.06 | 83.70→145.82 |
| live700k | 8 | tip | 1 | **MODEL_OK** | router-unloaded-autoload | **0** | 19.62 | 76.45→71.79 |
| live700k | 8 | tip | 2 | **MODEL_OK** | router-unloaded-autoload | **0** | 20.17 | 73.19→74.62 |
| live700k | 8 | base | 1 | **MODEL_OK** | router-unloaded-autoload | **0** | 24.83 | 71.79→73.19 |
| live700k | 8 | base | 2 | **MODEL_OK** | router-unloaded-autoload | **0** | 21.70 | 74.62→70.90 |

### Oracle — the router's own answer for the same model

`oracle.py` ran the router with `load-on-startup = true` in the preset's `[*]` section, so the
router itself spawned a child per model and recorded the outcome. Both fixture sets:

```
ORACLE_ENTRY id=slow_000 value=unloaded failed=True exit_code=1 args_model=[.../slow_000.gguf]   (x8, fx8)
ORACLE_ENTRY id=slow_000 value=unloaded failed=True exit_code=1 args_model=[.../slow_000.gguf]   (x8, fx700k)
ORACLE loader_child rc=1
```

Child log (`oracle-router.log`, `oracle-loader.log`):

```
E llama_model_load: error loading model: tensor 't0000001_000' data is not within the file bounds, model is corrupted or incomplete
E llama_model_load_from_file_impl: failed to load model
E srv    load_model: failed to load model, '.../fx8/slow_000.gguf'
E srv    server_run_i: exiting due to model loading error
```

So the router's own verdict for every fixture is **the model can never load** (`failed=true`,
`exit_code=1`, child refuses the file). The oracle does not depend on either probe.

## Findings

**F1 — BLOCKER (against the round-95 tip on a live router): the tip probe false-greens on a listing
whose files the router itself rejects.** `live700k`: 8 distinct fixtures of 700 000 tensor headers.
Both revisions graded `MODEL_OK / router-unloaded-autoload` (exit 0), i.e. "loadable", while the
oracle says `failed=true exit_code=1` for all 8 — a false green on the live router, not only in the
stub. Cause, measured: the tip charges **6 steps per tensor header**, so 700 000 tensors = 4 200 000
steps > `MAX_STEPS = 4_000_000`; the parse raises `Unknown` and the state becomes `-`
(undecidable → loadable). The effective tensor ceiling is therefore `4 000 000 / 6 = 666 666`
tensors, **333 334 tensors below the `MAX_TENSORS = 1 000 000`** that the plan's disclosed limit
(a) names. The plan discloses "exceeds `MAX_TENSORS` **or** needs more than `MAX_STEPS`", so the
step branch is disclosed in words — but the disclosed limit is stated as a *tensor count*
(`MAX_TENSORS`), and the counter's W09 cell uses 1 200 000 tensors, which is above `MAX_TENSORS`
and therefore exercises the **other** branch. Nothing in the frozen cells puts a file between
666 666 and 1 000 000 tensors, i.e. the branch that actually bites first on a live listing is
ungraded, and on a real router that branch yields `MODEL_OK` for a model that cannot load.
Evidence: `live700k-probe-tip-1.json`, `live700k-probe-tip-2.json`, `live700k.log`,
`oracle-router.log` (fx700k run).

**F2 — BLOCKER (round-94 base probe, reproduced live): the base probe false-greens on a 40-file
live listing.** `live40`: base graded `MODEL_OK / router-unloaded-autoload` (exit 0) in both
repetitions, at wall 60.33 s and 60.43 s — its constant `timeout 60` truncating the pass, leaving
the truncated candidates undecided. The tip graded `MODEL_UNLOADED / router-model-invalid` (exit 2)
at 133.42 s / 158.35 s against a derived ceiling of `20 + 15*40 = 620 s`. The oracle rejects all
40 files. This is round-94's D3/SC02-F2/F3 defect reproducing on a real router: the round-95 tip
does fix it, and this is the live confirmation that the fix is load-relevant rather than a stub
artefact. Evidence: `live40-probe-base-1.json`, `live40-probe-base-2.json`,
`live40-probe-tip-1.json`, `live40-probe-tip-2.json`, `live40.log`.

**F3 — NOTE (the tip's own ceiling is load-stable, verified once):** `live40load` (64 burners, own
process group, killed and verified absent): tip held `MODEL_UNLOADED / router-model-invalid`
(exit 2) at 247.06 s, i.e. 40 % of the 620 s derived ceiling, while the same listing's base probe
had already truncated at 60 s in the unloaded arms. The tip's decision did **not** flip under
synthetic load. One repetition only (budget).

**F4 — NOTE (counter-shape step accounting, worth one line in the plan):** the tip's step budget
does not bound *wall time* uniformly across parse paths. The tensor path charges 6 steps/header
(0.87 µs per charged step measured); the KV string-array path charges `steps += n//64` while
performing n Python iterations (10.7 µs per charged step, ~12x more wall per charged step). One
50 M-string fixture charges 781 250 steps (19.5 % of `MAX_STEPS`) and still costs ~8 s of parse. So
the derived ceiling `20 + 15*ncand` s is a *wall-clock* ceiling in the end, and a listing whose
per-file parse exceeds 15 s can still truncate the pass — the round-95 change moved the clock from
the per-file decision to the pass wrapper rather than removing it. Not falsified on the cells I
ran; recorded as the residual the plan's disclosed limit (d) already gestures at.

**F5 — NOTE (the round-95 counter's cells never put a file in the branch that bites first):** the
counter's own fixture class is `TENSORS = 600 000` (3 600 004 steps, 90 % of `MAX_STEPS`, decided
`invalid`) and W09's is 1 200 000 (`MAX_TENSORS` branch). The live `700 000` band between them is
where the tip returns `-`. The counter's `fixture_class()` oracle would classify 700 000 tensors as
`invalid` (its rule is `> 1_000 000 → "-"`, else `> 2 → invalid`), so a cell at 700 000 would be
graded `invalid` while the probe answers `-`: the frozen oracle and the probe disagree there, and
no frozen cell sits in that band.

## Deliverables

`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-95/w1/out/SC02LiveRouter/`
(all inside this seat's own out dir; no tracked lane file was modified):

- `live8-probe-{tip,base}-{1,2}.json`, `live8-models.json`, `live8-props.json`, `live8.log`
- `live40-probe-{tip,base}-{1,2}.json`, `live40-models.json`, `live40-props.json`, `live40.log`
- `live40load-probe-tip-1.json`, `live40load-models.json`, `live40load-props.json`, `live40load.log`
- `live700k-probe-{tip,base}-{1,2}.json`, `live700k-models.json`, `live700k-props.json`, `live700k.log`
- `oracle-router.log`, `oracle-loader.log`, `oracle-router-models.json`, `router-smoke.log`

Scratch `/fast/scratch/hyaku/kama-r95/SC02LiveRouter/` was removed after copying these.

## Not run / limits of this seat

- `live40load` (64 burners) ran **one** tip repetition only (not 2, and no base arm) — the budget
  stopped the arm; the base's behaviour under load is already established by F2 (its constant
  60 s ceiling is load-independent by construction).
- No repetition of the live700k arm under synthetic load.
- The string-array fixtures of F4 were measured on the parser directly, **not** through a live
  router listing (the 50 M-string file is 400 MB and the 200 M-string one 1.6 GB; I aborted that
  build when the budget notice arrived). F4 is therefore a NOTE on the parser, not a live-router
  false green; F1 and F2 are live-router findings.
- The oracle was obtained via `load-on-startup`, not by asking a running router to load the model
  (which would need a POST). Both are the router's own answer for the same bytes.
- Tooling: no package was installed or upgraded this run (nothing needed installing).

## Cleanup

All seat-started children are gone: no `llama-server` from this seat's scratch remains (the
surviving `llama-server` on port 1234 is the operator's, started before this seat, never
contacted); no `driver.py`/`oracle.py` remains; the 64 burners are killed and verified absent
(`pgrep -f 'while True: pass'` → 0). The seat scratch directory was removed.

VERDICT: falsified — the round-95 tip probe still false-greens on a real router (700 000-tensor
files: MODEL_OK while the router reports failed=true/exit_code=1 for every one of them, because
MAX_STEPS bites at 666 666 tensors, below the MAX_TENSORS the disclosure names); the round-94
base probe's false green was reproduced live on a 40-file listing (MODEL_OK at its constant 60 s
timeout, where the tip answers MODEL_UNLOADED against a 620 s derived ceiling).
