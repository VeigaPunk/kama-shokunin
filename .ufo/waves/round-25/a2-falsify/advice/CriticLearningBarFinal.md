VERDICT: defect found. C2 as landed clears the learning bar through "admitted knowledge on uncovered ground", plus a capability shown running this round, but not through supersession. The entry's `verified-at` names the wrong run, and two of its statements overclaim. All three are fixable in place without narrowing the target.

Seat: KamaR25a2.CriticLearningBarFinal (critic, read-only, wave 2). Lane tip fa3b62ae6475d111eb466d79af616aeebb08bbb9. No llama-server child started, no port opened. Sources re-opened fresh 2026-10-22 at llama.cpp 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad.

## Axes

- Learning (bar lines 145-149 of `.scratch/goal-20261022-hyaku-12h.md`): does C2 change what the lane knows or can do in K05?
- Provenance: does each landed statement rest on the committed bytes it names?
- Calibration: are replication and prediction matches labelled as such?

## Which bar route the landed C2 uses

| Bar route (line 145-148) | Landed? | Reason |
|---|---|---|
| admitted knowledge on uncovered ground | yes, pending closure admission | K05 is frontier (`PROVINCE.md` lines 88 and 105 at efe58e9). No admitted entry before round 25 names the KV pool, fit raising a context, or the shared-pool failure (`git grep` over efe58e9 corpus for `kv_unified`, `Context size has been exceeded`, `n_ctx_seq`, `KV pool`, `fit.cpp`: no knowledge hits besides `gguf-declared-identity.md:28,31`). |
| stronger entry superseding a weaker one | no | The rule it corrects lives only in round-20 wave evidence (`SrcServerNctx.md:6`, `nctx-crosscheck.py:41`), not in an admitted entry. The entry says so itself (`context-capacity.md:83-92`). |
| SKILL.md decision table grounded in admitted entries | conditional | `SKILL.md:676-689` (four rows) is grounded only in the round-25 entry. It counts only if the closure admits that entry. |
| capability shown running, row in SCORECARD | yes | `SCORECARD.md:1283-1287` follows the round-20 `capabilities: append` convention (line 909). The tool sha256 at 5c95c8f and at fa3b62a is `589841cd…4c27`, the same as receipt `tool.sha256`. It ran this round from 09:42:42Z to 09:42:50Z. |

The counter re-derives from committed bytes: `python3 .ufo/waves/round-25/count-c2.py` on the fa3b62a receipt printed `registered 14 observed 14 bound True missing []`, exit 0.

## New knowledge versus replication

The full per-statement table is `out/CriticLearningBarFinal/statement-classification.tsv`.

**New knowledge** (not held by any admitted entry or by round-20 wave evidence):
1. The KV pool is a second number per launch, and the three endpoints do not show it. K1 and X2 report identical endpoints on pools of 2048 and 8192 (`context-capacity.md:8-12, 133-146`).
2. With `-c` unset, fit on and a split cache, the pool rises to training context × slots. X1 gave pool 8192 and 2048 per slot; X3 with `--fit off` gave 2048 and 512 (`:71-82`). This is the first admitted statement. The attempt-1 record E09 observed the effect earlier but was not admitted (`:39-41`).
   - Re-read S106 `fit.cpp:197` `n_streams = cparams->kv_unified ? 1 : …n_seq_max`, `:270-272` `cparams->n_ctx = n_ctx_max;`.
   - X1 raw log lines 283 (2048), 812 and 1344 (8192), and 1610 (`n_ctx_slot = 2048`) match.
3. `--kv-unified-per-slot N` without `-c` sizes the pool to slots × N even when the cache is split (K7, pool 1024). The round-20 model implies 2048 for this cell. Re-read S108 `server.cpp:177-186`.
4. On a shared pool, concurrent requests are bounded by the pool total, and every processing slot fails together (`:101-130`).
   - L1 raw log lines 1849-1866 show `Context size has been exceeded.` at `n_batch = 1`, `send_error` for tasks 2 and 3, and both slots released at `n_tokens = 1025`.
   - Re-read S109 `server-context.cpp:4318-4330`.
   - L2 and L3 are the controls.
5. Smaller new statements:
   - The pool line needs `-v` or `-lv 4`.
   - K5's cap leaves only a log warning.
   - K6's log says "rounding down to 1536" while the value went up.
   - Explicit `-c 0` disables fit's context reduction. This one is source-only and not observed on this fixture (S110 `arg.cpp:1646-1649`, re-read).

**Replication or calibration** (correctly labelled as such at `:36-41`):
- The per-slot values on K1-K8, X2 and X3 (10 of 11 configuration cells) match round-20 `predict()` and the admitted `gguf-declared-identity.md:16-21`.
- The rule that all three endpoints read `n_ctx_slot()`.
- The per-slot cap by `--kv-unified-per-slot` and by training context.
- Padding to 256 and split division (round-20 `SrcServerNctx.md` already read `llama-context.cpp:377-393`). The K6 values are new observations of that rule.
- Unset `-np` giving 4 unified slots.
- The pool values K5-K8 were predicted from source before the runs. They are new to the corpus but are confirmations, not discoveries.
- The kengaku 34113 capture is another lane's historical evidence and is labelled that way (`:177-185`).

## Defects

**D1 — false provenance in `verified-at` (`context-capacity.md:2`).**
- The entry says "14 fixture cells observed 2026-10-22T09:36:51Z to 09:36:59Z".
- That window belongs to the receipt committed at 5ea4fc4 (and unchanged at 46fb04b). The committed receipt (5c95c8f, unchanged at fa3b62a) ran 09:42:42.481Z to 09:42:50.463Z.
- Under the registered amendment-4 counter, the 09:36 receipt scores `registered 14 observed 11 bound True missing ['L1', 'L2', 'L3']` (exit 0, `out/CriticLearningBarFinal/commands.txt`).
- So the entry stamps itself with a run that does not meet the claim. SCORECARD's capability row (`SCORECARD.md:1287`) gives 09:42:42Z to 09:42:50Z, so two landed files disagree about one receipt.
- Per-cell values are equal across both receipts, so no knowledge value is wrong; only the provenance is.
- This is the "false timestamp" class that `corpus/lessons/round-25.md:52` mined as this round's mistake.
- Smallest correction: change line 2 to "09:42:42Z to 09:42:50Z (receipt 5c95c8f)".

**D2 — untested claim stated as fact (`context-capacity.md:11-12`).**
- The entry says two launches "still differ fourfold in how many full-context requests they can run at once".
- Only the pool ratio (2048 against 8192) was observed. The L cells ran two requests of 1000 + 600 tokens each, and the entry's own `:129-130` says "No claim is made for other request counts or sizes".
- Wave 1 (`a2-build/advice/CriticLearningBarA2.md` Counterexample 4) flagged this, and it survived landing.
- Smallest correction: "…and still differ fourfold in KV pool size (K1 2048, X2 8192)". Alternatively, mark the concurrency count [INFERENCE].

**D3 — misattributed cell and an unrowed source (`context-capacity.md:59-60`).**
- The entry says "Giving `-np` keeps the default split cache (S110; common.h 580). K1 versus K2 shows the switch."
- K2's args include `--no-kv-unified` explicitly, so K2 cannot show the default. K4 (`-c 1024 -np 1`), K5 and K7 do: each logs `kv_unified = 'false'` with no layout flag.
- `common/common.h` has no SOURCES row (`git grep 'common.h' fa3b62a -- corpus/SOURCES.md` finds nothing). I re-read line 580, `bool kv_unified = false; // enable unified KV cache` (sha256 `8bcc5708…40a9`); it supports the statement, but it is not a registered source.
- Smallest correction: change "K1 versus K2" to "K1 versus K4 (or K7)", and cite common.h through a SOURCES row or drop the locator.

**Tradeoff, not a defect.**
- SKILL row 2 (`SKILL.md:687`) covers only "`-c` unset". By `fit.cpp:198` (`n_ctx_auto = cparams->n_ctx == 0`), an explicit `-c 0` split launch should rise the same way [INFERENCE, unrun].
- The entry lists that case as not run (`:173-174`). The row's scope header keeps it safe, so this is a gap the judge may accept.

## Impact on the claim

D1 to D3 do not change any number. The claim value stays `registered 14 observed 14 bound True` on committed bytes. As landed, the learning credit holds on the five new-knowledge groups above, provided that:
- D1 is fixed, or the closure accepts that the entry cites the wrong run;
- the closure credits the "uncovered ground" route, not supersession.

## Files written

- `.ufo/waves/round-25/a2-falsify/advice/CriticLearningBarFinal.md` (this report)
- `.ufo/waves/round-25/a2-falsify/out/CriticLearningBarFinal/statement-classification.tsv`
- `.ufo/waves/round-25/a2-falsify/out/CriticLearningBarFinal/commands.txt`
- Scratch: `/fast/scratch/hyaku/kama-r25a2w2/CriticLearningBarFinal/` (receipt and counter copies, `src/` pinned sources)

Tools installed or updated: none.
