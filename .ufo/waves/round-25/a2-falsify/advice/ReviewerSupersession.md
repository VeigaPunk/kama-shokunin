# ReviewerSupersession — falsify the round-20 supersession (round 25, attempt 2, wave 2)

Verdict: **holds** — the entry's supersession bullet is accurate in both line
references, its 512-for-X1 claim reproduces by execution of the committed
round-20 bytes, the one-case scoping is exact (10 of 11 config cells agree, the
single disagreement is X1), and no production file needs a correction. One
informational nuance below (the round-20 checker refuses X3's argv; only the
formula value is comparable).

## What I ran

`python3 /fast/scratch/hyaku/kama-r25a2w2/ReviewerSupersession/verify_supersession.py`
(exit 0; full stdout in `.ufo/waves/round-25/a2-falsify/out/ReviewerSupersession/verify-output.txt`).
It loads the round-20 tool from `git show fa3b62ae6475d111eb466d79af616aeebb08bbb9:.ufo/waves/round-20/build/out/SrcServerNctx/nctx-crosscheck.py`
and checks the advice file the same way. Committed tip bytes equal the working
copy for both files (sha256 `b1d8172d…51f26`, `18db7366…f3b9aeba`), so every
line reference holds at the landed tip. No llama-server child was started.

## Findings

1. **Line references are accurate.** `corpus/knowledge/context-capacity.md:83-86`
   cites `.ufo/waves/round-20/build/advice/SrcServerNctx.md` line 6 and
   `nctx-crosscheck.py` `predict()` (line 41). Verified: advice line 6 is the
   sentence "`n_ctx` starts from explicit context size, or training context when
   zero, then rounds up to 256. … split KV uses `GGML_PAD(n_ctx / n_seq_max, 256)`"
   (824 chars, one line). In the script, `def predict` is line 38; line 41 is
   `n_ctx = pad256(ctx if ctx else n_ctx_train)` — the exact bare-training-context
   substitution the bullet describes (the split itself is line 42). The entry's
   "models fit only as something that can lower a context" also matches: `fit`
   occurs in the script only in docstring line 13 ("assumes that no --fit run
   lowered n_ctx"); `predict()` has no fit parameter.

2. **predict() on X1 returns 512 — entry claim reproduced.** Committed-bytes
   execution: `launch_settings(["-np","4","--no-kv-unified"])` →
   `{ctx:0, np:4, kvu:False}` → `predict(0,2048,4,False,0)` = **512**. Observed
   X1 serves 2048 per slot (receipt `props_n_ctx` 2048; raw log line 1610
   `n_ctx_slot = 2048, kv_unified = 'false'`). Contradiction confirmed, and it is
   instrument-level, not just formula-level: `check()` on a synthetic
   round-18-format receipt with the X1 argv and observed 2048 exits **1** with
   `INCONSISTENT props==predicted … predicted=512 props.n_ctx=2048`.

3. **"Other ten config cells agree" is exact.** Round-20 predict vs committed
   receipt /props over K1-K8, X1-X3: 10 AGREE, 1 DISAGREE (X1, 512 vs 2048).
   K6 padding (1024→512), K5 training-context cap, K7/K8 `--kv-unified-per-slot`
   all replicate. The entry's count "ten" is correct.

4. **Supersession is scoped to the one case.** The bullet (entry lines 83-92)
   limits the correction to build 11755 + unset `-c` + fit on (default) + split
   cache, holds X3 (`--fit off`) under the round-20 value, leaves the admitted
   `corpus/knowledge/gguf-declared-identity.md` standing, and that entry indeed
   now points here (its lines 31-34: "Do not divide `ctx` by `total_slots`
   blindly… Round 25: the rule, the KV pool and the fit step are in
   `corpus/knowledge/context-capacity.md`"). `SKILL.md:687` scopes the same
   correction to its one decision row ("Do not use the round-20
   `nctx-crosscheck.py` value **for this case**"), and the entry's last bullet
   explicitly excludes the kengaku production capture (`-c` explicit, fit off,
   unified). No overreach found.

5. **Informational, no defect: X3 is comparable only at formula level.**
   `launch_settings(["-np","4","--no-kv-unified","--fit","off"])` raises
   `Unusable: argv element '--fit' is not modelled`; `check()` exits **2**
   COULD-NOT-EVALUATE on an X3-shaped receipt. The round-20 *value* (512) that
   X3 replicates comes from `predict(0,2048,4,False,0)`, not from running the
   round-20 checker on X3's argv. The entry says "the round-20 value holds"
   (value, not verdict) and cites `predict()`, so the wording is defensible;
   recorded so nobody expects CONSISTENT from the checker on X3. Same nuance
   applies to my finding 3: X3's agreement is formula-derived, the other nine
   run through `launch_settings` cleanly.

6. **Entry's raw-log citations verified.** `final/raw/X1.server.log`: line 283
   fit probe `llama_context: n_ctx = 2048` (line 284 `n_ctx_seq = 512`, line 295
   the `< n_ctx_train` warning), serving `n_ctx = 8192` at lines 812 and 1344
   (`n_ctx_seq = 2048`), `load_model: initializing, n_slots = 4, n_ctx_slot =
   2048, kv_unified = 'false'` at line 1610 — exactly as entry lines 76-82 and
   amendment 3's "fit logs a probe value first on X1" state. Note the log pads
   the field name (`n_ctx                 = 8192`); a literal `n_ctx =` grep
   misses these lines, the amendment-4 counter regex does not.

## Residual risk and verification gaps

- I did not re-observe X1/X3 live (assignment forbids starting a server); the
  observed values rest on the committed receipt and raw log, which
  `count-c2.py` scores `registered 14 observed 14 bound True missing []`.
- The source basis of the fit claim (S106/S111, fit.cpp/common.cpp) was not
  re-opened by me; SrcServerNctx/CriticLearningBar seats own it. My scope was
  the round-20 artifacts' behavior, which is falsified exactly as the entry
  says.
- No tool was installed or updated (no need; python3 and git sufficed).

## Files written

- `.ufo/waves/round-25/a2-falsify/out/ReviewerSupersession/verify-output.txt`
  (script stdout + log grep record)
- `.ufo/waves/round-25/a2-falsify/advice/ReviewerSupersession.md` (this report)
- Scratch only: `/fast/scratch/hyaku/kama-r25a2w2/ReviewerSupersession/`
  (`verify_supersession.py`, `nctx-crosscheck.py` tip copy, `receipt-X1.json`,
  `receipt-X3.json` synthetic)
