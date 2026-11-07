# EX01 HeldOutRepeat — C1 held-out shapes

## Scope
Held-out C1 shapes on stubs reusing `tools/round93-router-repeat.py` fixtures (GGUF slow-invalid 150k tensors, ok.gguf). Ran `bash <probe> check --port <stub> --expect good --json` at base `5af794958b0fc08f574aa2e67650282269549b02` (probe sha 36631d498901) and M1 `fe5f031cb1b9d33e1160360d892149b8ac3c7771` (probe sha 159c80688c5d), 2 runs per cell, load1 73–76. Cells: (a) distinct slow-invalid copies N=2..256, (b) one slow-invalid x4096/x16384, (c) hard link + attempted bind mixed with one valid file, (d) slow-valid x2048, (e) slow file as --mmproj of distinct valid models x64. No live 1234 traffic; stub on loopback only.

## Commands and outputs
```
export TMPDIR=/fast/scratch/hyaku/kama-r93/EX01HeldOutRepeat
python3 heldout.py --work /fast/scratch/hyaku/kama-r93/EX01HeldOutRepeat --out .ufo/waves/round-93/w1/out/EX01HeldOutRepeat  # exit 0, 221s
```
Receipts: `.ufo/waves/round-93/w1/out/EX01HeldOutRepeat/heldout.out`, `results.json`, `heldout.py`.

## Findings
- **NOTE** (a) Distinct copies share the deadline at both revisions — disclosed limit, NOT a regression: N=2 both invalid (1.4s), N=8 borderline flip both (one run MODEL_OK each), N>=16 both MODEL_OK/router-unloaded-autoload in ~4.3–5.3s. First flip at N=16 (base and M1 identical); no N where base is right and M1 wrong in (a).
- **NOTE** (b) Single-file repeats: base wrong at both N (4096: MODEL_OK 8.4s; 16384: MODEL_OK 9.0s); M1 correct (MODEL_UNLOADED/router-model-invalid, 1.1–2.2s). Doubling 4096→16384: base 1.06×, M1 1.7× (both ~constant; base time driven by 8s timeout kill, M1 by one parse + 16384 JSON entries).
- **NOTE** (c) Hard link (same inode) mixed with valid: both MODEL_OK as expected; M1 faster (1.0s vs 4.6s). Bind mount attempt `mount --bind` rc=32 (permission) — bind sub-case not exercised; hard-link coverage stands.
- **NOTE** (d) Slow-valid repeated 2048× (10.8MB, 150k tensors, data present): both MODEL_OK/router-unloaded-autoload; base 8.4s, M1 1.6s. No verdict change (valid stays loadable), M1 only faster.
- **NOTE** (e) --mmproj = slow file, 64 distinct valid models: base MODEL_OK (false green, 4.8s); M1 MODEL_UNLOADED/router-model-invalid (1.1–1.5s). This is the R06 shape with distinct models — M1 correct, base wrong.
- No cell where base is right and M1 wrong; no BLOCKER. All positive cells (c valid-mixed, d) hold at M1.

## Deliverables
`.ufo/waves/round-93/w1/out/EX01HeldOutRepeat/heldout.out`, `results.json`, `heldout.py`.

VERDICT: holds — no base-right/M1-wrong cell; (a) distinct-copy deadline-sharing confirmed at both revisions (disclosed limit), (b)(c)(d)(e) as expected with M1 strictly faster or correct where base false-greens.
