# J3NoMapping — C1 mapped-leg ablation control (round-50 w1)

**Verdict: control met=False as required.** Removing the `model_mapping` record from
`tools/kama-llamacpp-live.py` at fixture commit `534fe065beb4eb07da0ab8a3441c77225855a887`
turns C1's mapped leg from 3/3 to 0/3 — `bind=0 teardown=1 newrow=1 bound=0/3 met=False`
(twice, identical) — while the same frozen counter binary on the same host against the
intact build `97c864bead3ee4a2f629574e77263d33834ec98a` gives
`bind=1 teardown=1 newrow=1 bound=3/3 met=True`. The record is load-bearing, and the
collapse is confined to the bind leg: teardown and newrow stay 1, so the ablation is
specific, not a general breakage.

## 1. Fixture

```
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r50/J3NoMapping/lane
git -C $S/lane switch -c ablate-nomapping 97c864bead3ee4a2f629574e77263d33834ec98a
git -C $S/lane rev-parse --show-toplevel   # /fast/scratch/hyaku/kama-r50/J3NoMapping/lane (asserted before commit)
```

Tools at `97c864bead3ee4a2f629574e77263d33834ec98a` are byte-identical to the lane tip I
cloned (`git diff --stat 97c864bead 3b79eadd -- tools/` empty), so the fixture is the
build, not the tip. Patch = the two recording sites and nothing else (`ablation.diff`,
sha256 `42b7a962602526bb3c9cbb8316a76b65b8c190439eba24071c7bae1a7af8bf4c`):

- `tools/kama-llamacpp-live.py:1763` — drop the `'model_mapping': None` receipt placeholder
  (build line numbers), so the key is absent rather than null;
- `tools/kama-llamacpp-live.py:1999-2005` — drop the record block
  (`receipt['model_mapping'] = model_mapping(proc.pid, args.model)` and the
  `server-not-running` branch).

Kept: `model_mapping()` itself (`:678`, now uncalled), the isolation/`-I`/`pdeathsig` paths,
the witness hold, every check. `ast.parse` on the patched file: ok.

Commit (fixture identity, `-c user.name`/`-c user.email` on the fixture only):
`534fe065beb4eb07da0ab8a3441c77225855a887` (parent `97c864be`, 1 file, +2 −8; metadata in
`fixture-commit.txt`).

## 2. Counter identity

`sha256sum tools/round50-replay-bind-audit.py` = `ff6ac2ace541ea35a4d240ceebb019653c11a2a08c025e514770f3f94a9c5e89`
= preregistration `claims[0].counter_sha256`. The counter was read from the lane and
never edited; the fixture patch does not touch it.

## 3. Results

| run | tip | command | exit | verdict line |
|---|---|---|---|---|
| ablated, run 1 | `534fe065` | `--repo $S/lane --tip 534fe065… --scratch $S/c1 --out …/c1-ablated.json` | **1** | `bind=0 teardown=1 newrow=1 bound=0/3 met=False` |
| ablated, run 2 | `534fe065` | same, fresh scratch `$S/c1r2` | **1** | `bind=0 teardown=1 newrow=1 bound=0/3 met=False` |
| paired intact | `97c864be` | `--tip 97c864be…` | **0** | `bind=1 teardown=1 newrow=1 bound=3/3 met=True` |

Wall clock: 16.3 s, 17.1 s, 21.7 s. Full receipts: `c1-ablated.json`,
`c1-ablated-run2.json`, `c1-paired-build.json` (each also as `.stdout`; run 1 has an empty
`c1-ablated.stderr`).

Ablated detail, both runs, every leg (verbatim, run 1):

```
detail: bind b1: replay exit 1 match False refused None
detail: bind b1: rerun model_mapping None does not record the observed mapping ('103:05', '1693400267')
detail: bind b2: replay exit 1 match False refused None
detail: bind b2: rerun model_mapping None does not record the observed mapping ('103:05', '813227211')
detail: bind b3: replay exit 1 match False refused None
detail: bind b3: rerun model_mapping None does not record the observed mapping ('103:05', '1753683144')
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 3 rows new since base; 1 name proc_pid_maps(5): ['| S496 |']
```

Paired intact detail shows the mapped leg green with dev/inode joined
(`mapping dev 103:05 inode 616804516 recorded`, nonce round-tripped, `child_pid joined`).

## 4. Causal chain (three independent observations, per leg)

1. **The record is gone from the receipt.** Rerun receipts captured directly from the
   ablated tree (`tools/kama-live-replay.py` run once at the ablated tip, kept as
   `ablated-rerun-receipt.json`): `model_mapping` key **absent**, `schema
   kama-llamacpp-live/v5`, `outcome pass`, 11/11 checks passed, `child_pid 2388792`,
   live exit 0. So nothing else about the live tool regressed; only the record is missing.
2. **The replay refuses it.** `ablated-replay-out.json`: `match False`, `live_exit 0`,
   `mismatches ['model-mapping:absent']`, replay exit **1** — the branch at
   `tools/kama-live-replay.py:343-346` (build tree) reports the key as *absent*, which is
   why the counter's per-leg `replay exit 1 match False` appears.
3. **The counter's own mapped check fires too** — `tools/round50-replay-bind-audit.py:473-476`
   compares the rerun `model_mapping` against its own `/proc` observation (dev, inode), and
   reports `does not record the observed mapping ('103:05', <inode>)`. In every ablated leg
   the counter *did* independently observe a file-backed mapping hashing to the frozen model
   (`('103:05', …)` non-None), i.e. the server still mapped the model; only the record is
   absent. The two mechanisms are separately load-bearing here; separating them is
   M2Live's mutant scope (`build_spec.py:73`: "mapping-mismatch refusal, model-mapping:absent refusal").

## 5. Paired A/B rerun receipts (same host, same receipt-1, same counter-independent path)

| tree | replay exit | mismatches | `model_mapping` |
|---|---|---|---|
| ablated `534fe065` | 1 | `['model-mapping:absent']` | **absent** |
| intact `97c864be` | 0 | `[]` | `{"mapped": true, "sha256": "270cba1b…6d", "dev": "103:05", "inode": "1555071986", "size": 1185376, "path": …/stories260K.gguf}` |

Files: `ablated-replay-out.json`, `ablated-rerun-receipt.json`, `intact-replay-out.json`,
`intact-rerun-receipt-1.json`, `ablated-replay.log`, `intact-replay.log`.

## 6. Coverage note (not a defect, but why this control matters)

`python3 tests/llamacpp-live/check-receipt.py ablated-rerun-receipt.json` → `VALID`, exit
**0** (and `VALID` on the intact receipt too). The receipt-shape validator does not know
`model_mapping`, consistent with the build comment "recorded, never a check id: v1-v5 check
lists stay as they were" (`tools/kama-llamacpp-live.py:2000-2002` at `97c864be`). Consequence:
the record's absence is caught **only** by the replay's mismatch check and by C1's mapped
leg — so this ablation is exactly the gate that proves the leg, and no other lane
instrument silently backstops it.

## 7. Findings

**F1 (low, cosmetic/audit legibility) — `tools/round50-replay-bind-audit.py:476` conflates
"key absent" with "key null" in its problem text.** Observed in both ablated runs:
`rerun model_mapping None does not record the observed mapping (…)` — an absent key prints
as `None`, the same string a present `model_mapping: null` would print, whereas the replay
says `model-mapping:absent` (`tools/kama-live-replay.py:346`). Repro:
`python3 tools/round50-replay-bind-audit.py --repo <clone with 534fe065> --tip 534fe065beb4eb07da0ab8a3441c77225855a887 --scratch <dir>`
→ that detail line. Proposed fix (report-only, counters are frozen):

```diff
-            mm = rr.get("model_mapping") if isinstance(rr, dict) else None
-            if not (isinstance(mm, dict) and mm.get("sha256") == MODEL_SHA and mapped is not None
-                    and str(mm.get("dev")) == mapped[0] and str(mm.get("inode")) == mapped[1]):
-                probs.append(f"rerun model_mapping {mm!r} does not record the observed mapping {mapped}")
+            mm = rr.get("model_mapping") if isinstance(rr, dict) else None
+            shown = "absent" if not (isinstance(rr, dict) and "model_mapping" in rr) else repr(mm)
+            if not (isinstance(mm, dict) and mm.get("sha256") == MODEL_SHA and mapped is not None
+                    and str(mm.get("dev")) == mapped[0] and str(mm.get("inode")) == mapped[1]):
+                probs.append(f"rerun model_mapping {shown} does not record the observed mapping {mapped}")
```

No other defect found in the C1 counter, the replay or the live tool on this leg.

## 8. Limits of this control

- The ablation removes the **record and its cross-check only**; `/proc` maps reading and
  hashing are untouched (the counter still observed `('103:05', …)` per ablated leg, and the
  helper `model_mapping()` remains defined at `:678`). A mutant of the maps parse /
  O_NOFOLLOW / fstat comparison is M2Live's scope, not this seat's.
- The single-replay A/B uses `round-48/c2/live/receipt-1.json` only; the counter run covers
  all three committed receipts (3/3 legs shown above).
- No edits to the lane: counter, replay, live tool, preregistration and controls were read
  from the lane and are unchanged; the only mutated copy is the fixture clone in scratch.

## 9. Environment

- Tools installed/upgraded: none (no pacman, no uv/npx).
- No service started or stopped by me outside the tools' own loopback llama-server
  processes; after the runs `pgrep -af llama-server` shows only sibling seats' processes
  (`X11ModelSwap`, `U1Fresh` paths), none under `/fast/scratch/hyaku/kama-r50/J3NoMapping`.
- Scratch `/fast/scratch/hyaku/kama-r50/J3NoMapping` removed after the artifacts below were
  copied out; no `/tmp` path is cited.

## 10. Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/J3NoMapping.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/J3NoMapping/c1-ablated.json`
- `…/J3NoMapping/c1-ablated.stdout`, `…/J3NoMapping/c1-ablated.stderr`
- `…/J3NoMapping/c1-ablated-run2.json`, `…/J3NoMapping/c1-ablated-run2.stdout`
- `…/J3NoMapping/c1-paired-build.json`, `…/J3NoMapping/c1-paired-build.stdout`
- `…/J3NoMapping/ablated-replay-out.json`, `…/J3NoMapping/ablated-rerun-receipt.json`, `…/J3NoMapping/ablated-replay.log`
- `…/J3NoMapping/intact-replay-out.json`, `…/J3NoMapping/intact-rerun-receipt-1.json`, `…/J3NoMapping/intact-replay.log`
- `…/J3NoMapping/ablation.diff`, `…/J3NoMapping/fixture-commit.txt`, `…/J3NoMapping/MANIFEST.sha256`
