# EX02LiveRouterBudget — live router budget (C1 operability)

## Scope
End-to-end on REAL lane-owned `llama-server` b12177 router children only (free
127.0.0.1 ports, `--models-dir/--models-preset` in scratch, process-group kill;
never 127.0.0.1:1234 — only read-only process table peek). Seat spec verbatim:
preset >=12 entries naming one slow invalid GGUF (150 000 tensor infos, truncated,
counter's bytes) + one valid entry; `nproc` burners; probe at base vs M1 with
single `--expect` and `--expect '*'`; oracle POST /v1/chat/completions
(max_tokens 2) per spec. This seat also ran a discriminating distinct-files
variant (reason: same-file dedup, below) — full verbatim kept in out dir.

Revisions: base B=e6f1dccecbad6dea44a129dabc928822c458e824; M1=a27656a454b1a2364f8b6e55f42fbca8c2e86ee4.
Probe sha256: B=1e21c1fb5d3fac1d6abc06ef1c541531e261acba36fb6678c1fb3fe9591e29c3,
M1=27065a5c487ec819a975cc96d3c990ab5161d0e55d82be02a87dde86974ed3b4 (matches c1.out).

## Commands and outputs (exit codes)
- `TMPDIR=<scratch> python3 driver.py` → exit 0, 18.7s, log `run.log`. Preset 13
  entries (bad00..bad11 → slow.gguf 6 000 048 B sha256 02184c6be8d9872e…; valid1 →
  good.gguf 192 B). Router auto-listed +2 dir entries (slow, good) = 15 listed.
  Contamination note: oracle ran before probe-load, flipping bad00 to
  `failed` (reason router-unloaded-failed thereafter) — superseded by driver2.
- `TMPDIR=<scratch> python3 driver2.py` → exit 0, 77s, log `run2.log`. Fresh
  router per (rev,rep), 2 reps, `nproc`=32 burners, probe-load BEFORE oracle.
- `TMPDIR=<scratch> python3 driver3.py` → exit 0, 90.6s, log `run3.log`.
  Discriminating shape: 8 DISTINCT slow files s0..s7 (6 000 048..6 000 272 B),
  empty models-dir, wildcard + s07 probes under 32 burners, oracle after.
- All routers process-group killed; burners stopped (leftover `while True: pass`
  PIDs 1330409+ are PPID 1487, elapsed 39 min — other seats', NOT mine, untouched).
- Scratch `/fast/scratch/hyaku/kama-r94/EX02LiveRouterBudget/` removed after
  copying drivers+logs to out dir.

## Findings
- vc (spec shape, single file ×12 + valid): BOTH revisions agree, no B flip.
  - B under load (32 burners, load1 128.9-190.3): `--expect bad00` →
    MODEL_UNLOADED/router-model-invalid (3.34s, 2.15s); `--expect '*'` →
    MODEL_OK/router-unloaded-autoload (1.85s, 3.48s — CORRECT: valid1 loadable
    wins per router_refine precedence). Oracle bad00 (after): 500 failed-to-load.
  - M1 under load (load1 158.1-194.8): bad00 → MODEL_UNLOADED/router-model-invalid
    (6.66s, 3.95s); `'*'` → MODEL_OK/router-unloaded-autoload (7.76s, 3.33s). Oracle: 500.
  - Verdicts identical B vs M1 on every cell; oracle agrees (MODEL_UNLOADED) in all 4.
- NOTE: Spec shape does NOT exercise the C1 mechanism. One invalid file repeated
  12× is parsed ONCE (SEEN dedup by dev/ino/size/mtime/ctime,
  kama-probe.sh:589-602), so the shared 4s deadline is never consumed 12×; B
  cannot flip here. The counter's live analog is: many DISTINCT slow files.
- DEFECT (B only, discriminating shape, reproduced 2/2 reps): under 32 burners
  with 8 DISTINCT slow invalid files and no valid entry, `--expect '*'`:
  - B: MODEL_OK/router-unloaded-autoload, rc=0 (4.75s @load1 190.69; 4.91s
    @185.09) — FALSE GREEN. Router truth is unloadable: oracle s07 → 500
    "failed to load"; single-entry `--expect s07` agrees (MODEL_UNLOADED/
    router-model-invalid, 3.70s/2.97s). Wildcard flips; named entry does not.
    Mechanism: shared DEADLINE (kama-probe.sh:570, B-era) spent on s00..s0k,
    later candidates undecided `-` → loadable → `nbad < ncand` (line 884) → MODEL_OK.
  - M1: MODEL_UNLOADED/router-model-invalid, rc=2 (22.60s @188.20; 17.11s
    @193.14) — correct. `--expect s07` agrees (1.50s/2.05s); oracle 500 both reps.
  - Ratio (within-run, M1/B wall): 4.8×/3.5× slower wall but correct verdict —
    per-file 15s slices × 8 files ≈ 17-23s total, inside wrapper `timeout 60`.
    This is the C1 claim exactly, on a live router.
- NOTE: Host load1 was 128-210 throughout (32-core box, other agents) — all timing
  cells carry load1; wall times are load-inflated, verdicts are load-invariant
  for M1 and load-flipped for B. No time-over-budget claim made.
- NOTE: No rule change, no tracked-file edit; drivers/logs only in out dir.

## Deliverables (paths in out dir)
- `.ufo/waves/round-94/w1/out/EX02LiveRouterBudget/driver.py` (spec-shape run 1)
- `.ufo/waves/round-94/w1/out/EX02LiveRouterBudget/driver2.py` (fresh-router reps)
- `.ufo/waves/round-94/w1/out/EX02LiveRouterBudget/driver3.py` (distinct-files, discriminating)
- `.ufo/waves/round-94/w1/out/EX02LiveRouterBudget/run.log` (exit 0)
- `.ufo/waves/round-94/w1/out/EX02LiveRouterBudget/run2.log` (exit 0)
- `.ufo/waves/round-94/w1/out/EX02LiveRouterBudget/run3.log` (exit 0)

VERDICT: holds — Live router confirms C1: B flips wildcard to MODEL_OK under load (false green vs oracle 500), M1 stays MODEL_UNLOADED; spec's same-file preset is non-discriminating (dedup), distinct-files variant reproduces B-flip 2/2 and M1-stability 2/2
