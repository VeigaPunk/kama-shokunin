# MT13C1NoRehash — round 63 C1 counter mutation probe (operability)

Advisory leaf finding. No verdict on the C1 claim; no commit to the lane; no lane edit.
Tip under test: `03a6a1d850902a66a13dfad33f89cf3a8b759a09`.
Counter under test: `tools/round63-c1-counter.py` (blob sha256 `35af5c980254e25b5035c599bf818ebd8143dd1f341280a74d9d0a4ebe45dbcd`, identical to the lane tip blob).
Tool under test: `tools/kama-completion-live.py` (schema `kama-completion-live/v2`).
Evidence: `.ufo/waves/round-63/w1/out/MT13C1NoRehash/` (outputs, stderr, mutant diffs, receipts for base/m1b/m3/m5, manifest with mutant commit hashes).
Tools installed or upgraded: none.

## 1. Baseline and restoration (unmutated counter, pristine clone)

```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]   (exit 0)
```

Re-run after all mutants, from the pristine clone bytes: identical line, exit 0 (`out-restored.txt`).
Note for the digest family: at this tip it is a **single** control (`digest=1/1`), the decoy `model.path` swap. The
`model.sha256 = '0'*64` tamper is in the `tamper` family, not `digest`.

## 2. Mutants (each in its own clone, committed as `mutant`, scored from the clone path)

Clones: `$S/clone-<id>` under `/fast/scratch/hyaku/kama-r63/w/MT13C1NoRehash/` (removed before yield). Mutant commit hashes are in `out/…/manifest.txt`.

### 2a. Mutation A — `sha256_path` returns a pinned digest without hashing

Two variants, because "the pinned digest" is ambiguous when the function is not told which pin applies.

**A1 (literal: `return MODEL_SHA` for every path)** — KILLED, by collateral only.
```
tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]
error: live: ["inconsistent:server_digest", "server_digest"]
```
The genuine receipt fails `server_digest` (the `llama-server` path is hashed to `MODEL_SHA`), so no control is scored and the
digest family is never reached. This kill says nothing about the decoy control.

**A2 (role-keyed: `return SERVER_SHA if 'llama-server' in path else MODEL_SHA`)** — KILLED, by the digest decoy escaping.
```
tool_present=1 live_ok=1/1 controls_targeted=43/44 eval_selftest=3/3 errors=0 met=False families[digest=0/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
error: escape digest expect=model_digest fails=[]
```
Escaping control: family **`digest`** (the only `model_digest`-naming control, which swaps `model.path` to the counter's decoy file).
Its re-score has `fails=[]`: with the file un-hashed the decoy receipt is accepted in full, so the decoy is the only control that
exercises the re-hash, and it is the one that goes. Every other family still hits. The tamper of `model.sha256`, which uses the
receipt-claimed digest, still hits because it is not a re-hash.

### 2b. Mutation B — drop the `model_digest` decoy control (`add('digest', …)`, lines 614–615)

**B1 (pure drop)** — KILLED, by the total-count gate only.
```
tool_present=1 live_ok=1/1 controls_targeted=43/43 eval_selftest=3/3 errors=0 met=False families[fake=2/2 hdr=2/2 … witness=6/6]
```
- The only reason for `met=False` is `total == EXPECT_CONTROLS (44)` failing at 43.
- The printed line shows `controls_targeted=43/43 … errors=0 met=False`, and **no error line is printed**, so a reader sees a clean tally with a
  failing verdict. The `digest` family silently vanishes from `families[]`.

**B2 (drop the decoy and duplicate a passing `stale` control in its place, total kept at 44)** — **SURVIVED**.
```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]   (exit 0)
```
The gate `total == EXPECT_CONTROLS` and `rejected == EXPECT_CONTROLS` counts controls, not families or their named checks. A duplicate
of any passing family keeps the gate green, and no check requires that `digest` (or any other family) be present. **This is a defect of
the control set/gate, reported prominently.**

## 3. Live receipt with a decoy `model.path` (tool edited in the clone, scored by the unmutated counter)

**M3 — tool records `receipt.model.path` = a decoy file, the real model still runs; `model.sha256` recorded as the real digest.**
Receipt confirmed: `"path": "/fast/scratch/…/decoy-live.bin"` (`receipt-m3.json`).
```
tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]
error: live: ["inconsistent:model_digest", "model_digest"]
```
KILLED. The counter re-hashes `model.path` by itself, so the substitution is caught as `model_digest` and as an inconsistency with the
stored check. This is the honest path: the re-hash works.

**M4 — M3 tool edit + A2 counter edit (no-rehash, role-keyed) together.**
```
tool_present=1 live_ok=1/1 controls_targeted=43/44 eval_selftest=3/3 errors=0 met=False families[digest=0/1 …]
error: escape digest expect=model_digest fails=[]
```
With the re-hash removed, the **decoy-path receipt is accepted as a genuine live receipt** (`live_ok=1/1`, `errors=0`). Only the
digest decoy control, which is again the escaping one, keeps `met=False`.

**M5 — M4 plus B2 (decoy control dropped, duplicate `stale` in its place).**
```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[… stale=2/2 …]   (exit 0)
```
**SURVIVED.** The decoy-path receipt goes through the live gate and the full 44-control gate with `met=True`. The counter's only
model-identity binding is the re-hash of `receipt.model.path`, and when that re-hash is removed together with its only control, nothing
else catches a substituted model file. `hold.json`'s `model_sha256` is the tool's own digest of the file passed to `--model`, not of
`receipt.model.path`, so the live witness (`live_model_sha`) does not bind the receipt path either. (Read from the tool code,
`kama-completion-live.py` lines 236, 480–486, and the counter's `score()` `live_model_sha` check.)

## 4. Findings (prominent)

1. **SURVIVED — B2 and M5.** The `EXPECT_CONTROLS = 44` gate is a total-count gate. It does not check family presence or per-family
   expected counts. Removing the `model_digest` decoy and adding a passing control keeps `met=True`. Suggested direction (advisory, not
   implemented): assert the expected family set and per-family counts (`fam_tot == EXPECTED_FAMILIES`), so a dropped or doubled family fails
   by name.
2. **Single point of failure for model identity.** `model.path` is bound to the pinned model only by `sha256_path()` plus one control
   (`digest=1/1`). When the re-hash is hollowed, the decoy is accepted outright (`fails=[]`, A2 and M4). Recommend a second, independent
   binding (e.g., a live check that `model.path` equals the `--model` argv the tool actually launched, and a control that breaks
   `receipt.model.path` without touching the hash) so no one edit removes the only guard.
3. **Operability of the tally line.** B1 prints `controls_targeted=43/43 … errors=0 met=False` with no reason printed. The
   verdict is correct but the line does not say why. Suggested direction: print the failing gate (`controls_total=43!=44`) to stderr.
4. **A1 is caught only by collateral.** The literal pin breaks the genuine receipt (`server_digest`) before any control is scored; the counter
   reports `controls_targeted=0/0`, so it gives no evidence about the digest family. Only A2 exercises the family.

## 5. Host notes

- Every live run used the lane tool on unregistered loopback ports; the runs took about 1.5–2 s each. The registered consumer ports and
  the operator's llama-server processes on 1234 and 45669 were not touched.
- A `llama-server --model …/stories260K.gguf --alias kama-completion-probe --port 39997` process (PID 2406236, parent 2406168, started
  19:42:33) is **not** a child of any of my runs (my child PIDs are listed in each `work-*/receipt.json`). It belongs to another seat or lane.
  I did not signal it.
- No git mutation touched the lane. All commits were made in my own clones (`git -c user.name=seat …`); the lane was only read
  (`clone --shared`, `show`, `rev-parse`).

## 6. Tally

`mutants: KILLED=5 (A1 collateral, A2 digest-escape, B1 count-gate, M3 live-model-path, M4 composition) SURVIVED=2 (B2 duplicate-family, M5 composition with B2)`

`tip=03a6a1d850902a66a13dfad33f89cf3a8b759a09 baseline: tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True`
