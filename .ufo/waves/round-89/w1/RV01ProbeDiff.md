# RV01ProbeDiff — C1 diff review of tools/kama-probe.sh (round 89 w1)

## Scope
Line-by-line review of `git diff 56174a1 4f9eacf7 -- tools/kama-probe.sh` (router GGUF-header
grading): (1) set -euo pipefail hazards, (2) probe checks vs S584 gguf.cpp @ 6c01da62 +
llama-model-loader tensor-bounds check, (3) QSIZES vs S585 constants.py (QK_K=256),
(4) precedence, (5) no-python3 and `--model=PATH`. Probe bytes run from scratch copies:
base `99dd1ab8d41bb682…`, measured `a4f496bb0ed93179…` (git show of the pinned revs; base
sha matches the claims' do-nothing-control probe). Server: b12177 sha256 `ba272ee3…b362b0`
(claims pin). All children were my own, loopback, killed by process group; scratch
/fast/scratch/hyaku/kama-r89/RV01ProbeDiff removed after receipt copy. No live-1234 POSTs.
No tool installs were needed (pacman untouched).

## Commands and outputs (exit codes)
- `git -C <lane> diff 56174a1 4f9eacf7 -- tools/kama-probe.sh` → 255 lines (out/c1-probe.diff), exit 0.
- `python3 out/RV01ProbeDiff/run_all.py` (stub scenarios + fixtures + real-loader falsification
  + QSIZES diff; exit 0). 20 scenarios, 28 fixtures. Highlights (M=measured, B=base):
  - h1 missing -m path: M=MODEL_UNLOADED/router-model-missing/exit2 | B=MODEL_OK/router-unloaded-autoload/exit0
  - h2 args-as-string, h3 args[0]-not-a-file, h5 garbage /v1/models: M==B, old verdicts kept.
  - h4 /props without models_autoload (router_autoload exits 1 inside `&&` list):
    M=MODEL_UNLOADED/router-unloaded/exit2 — probe did NOT die (set -e safe).
  - p1 wild{unloadable+loadable-unloaded}→M=B=MODEL_OK router-unloaded-autoload;
    p2 wild{unloadable+plain-unloaded}→M=B=MODEL_OK; p7 sleeping wins; p8 loaded wins.
  - p3 wild{unloadable+loading}: M=MODEL_LOADING/router-loading vs B=MODEL_OK/router-unloaded-autoload.
  - p6 wild{down+unloadable}: M=MODEL_UNLOADED/router-model-missing vs B=MODEL_OK/router-unloaded-autoload.
  - p4 no-autoload: M=B=MODEL_UNLOADED/router-unloaded (reason unchanged, required).
  - p5 failed:true: M=B=MODEL_UNLOADED/router-unloaded-failed.
  - e1 `--model=PATH`, e3 `--model-draft PATH`, e4 `--mmproj=PATH`, e5 `-mm PATH` missing:
    all M=MODEL_UNLOADED/router-model-missing (B=MODEL_OK false green). e6 relative, e7 all-valid: M=B old verdict.
  - nopy (PATH without python3): M=MODEL_OK/matched/exit0 — round-88 verdict kept, exit 0.
- Fixtures (probe via stub entries, loader ground truth = `llama-server -ngl 0 -m <file>`):
  17/17 probe-invalid files also fail the real loader (exit 1), e.g. pasteof.gguf →
  `tensor 'blk.0.weight' data is not within the file bounds` (loader-logs/load-pasteof.gguf.log);
  positive control stories260K-real.gguf: probe keeps MODEL_OK, loader LOADED (listening line in
  loader-logs/load-stories260K-real.gguf.log). **Zero false reds observed.**
  6 fixtures loader-rejects-but-probe-keeps-old-verdict: duptensor, emptykey, longname, nestedarr,
  type4, type44 (details in Findings N2).
- QSIZES: `identical: True | probe entries: 36 | s585 entries: 36` (regenerated from S585
  constants.py with QK_K=256 and ordinals from ggml.h enum; gaps = removed types 4,5,31–33,36–38).

## Findings
- **NOTE N1 (citation nit)** claims + probe comment attribute "tensor data past end of file" to
  S584 ggml/src/gguf.cpp @ 6c01da62; at that commit gguf.cpp has no such check (it computes
  ctx->size only); the rejection lives in `src/llama-model-loader.h:44-46`
  (`offs + ggml_nbytes(tensor) > file->size()` → throw → 500). Behavior matches the binary
  (pasteof fixture proves both); only the source pointer is imprecise.
  Evidence: src/llama-model-loader.h:38-47 (fetched copy), loader-logs/load-pasteof.gguf.log.
- **NOTE N2 (remaining false greens — declared-acceptable direction)** loader checks the probe
  skips; each verified live (probe keeps round-88 verdict, real loader exits 1):
  empty KV key (gguf.cpp `key is empty`), duplicate KV keys and duplicate tensor names
  (`seen_keys`/`seen_tensor_names`, gguf.cpp:606/690; dup-tensor fixture), nested arrays
  (inner ARRAY → `invalid GGUF type`), tensor name ≥ GGML_MAX_NAME=64, tensor types 4/44
  (loader: range/blck-0 reject, `type 4 (DEPRECATED)`; probe: not in QSIZES → "-"),
  plus arch/tokenizer-level failures (valid-template fixture: `unknown model architecture:
  'stories'`) and split-shard loss (code-level, not fixture-tested). This matches the frozen
  rule "unknown … → no change (a false red is worse)".
- **NOTE N3 (drift-set change vs base, outside frozen cells)** because unloadable entries no
  longer count as plain-unloaded: wildcard {unloadable+loading} flips MODEL_OK→MODEL_LOADING
  (p3), wildcard {down+unloadable} flips MODEL_OK→MODEL_UNLOADED router-model-missing (p6).
  Both are oracle-consistent (no matching entry answers 200); not covered by the frozen 11 cells
  or the K2 harm cells, which were measured green at M.
- **NOTE N4 (contrived false-red path, code-level only)** duplicate model flags: probe unions
  every -m/--model/-mm/-md occurrence and missing/invalid wins over ok; the server keeps the
  LAST flag. An entry with `-m <missing> -m <loadable>` would be graded router-model-missing
  while the server loads the second path. Not exercised live; requires a duplicate-flag entry.
- **No BLOCKER, no DEFECT.** Set -e audit: the 4-field `read` always receives newline-terminated
  4-field lines (python `print`); `router_autoload "$port" && autoload=1` inside the `if` body
  cannot kill the probe (failing command is non-final in the && list; verified live in h4, exit 2
  not 1); `[ … ] && return 0` / `|| return 0` patterns are pre-existing and exercised in every
  scenario; heredoc failure modes (garbage body h5, props parse failure h4) keep old behavior.
  Checks the probe applies map 1:1 onto loader checks (magic, v0/v1/v>3/byte-swapped, alignment
  type+power-of-2, n_dims>4, ne[0]%blk incl. nd=0→ne=1, offset contiguity+pad, bounds vs st_size,
  n_kv*13+n_tensors*24 fit budget — sound lower bounds 14/25 bytes); fixture matrix found none
  that the loader accepts.

## Deliverables (out/RV01ProbeDiff/)
- c1-probe.diff — the reviewed diff. results.json — all 20 scenarios + 28 fixtures with
  verdicts/reasons/exits, loader outcomes and log tails, QSIZES diff.
- stub_router.py (stub router; GET-only), make_gguf.py (24 crafted GGUF fixtures), run_all.py
  (harness). loader-logs/ — b12177 ground-truth logs per fixture.
- Report: this file. Scratch dir removed after receipt copy.

VERDICT: holds — the C1 diff implements exactly the loader's header-check set with no observed
false reds (17/17 invalid fixtures confirmed by the real loader, positive control loads), QSIZES
byte-identical to S585, set -e safe, precedence per the frozen rule; residual false greens are
the declared conservative design (N2) and the S584 citation should point at llama-model-loader.h.
