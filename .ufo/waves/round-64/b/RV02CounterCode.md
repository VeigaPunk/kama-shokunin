# RV02CounterCode — review of tools/round64-c1-counter.py (wave b, seat RV02, item: review counter code)

Scope: `tools/round64-c1-counter.py` at freeze tip `f6a4ea9a8b5a876d685b08e7e582ec0723412a4a` (1710 lines), read end to end.
Frozen text read: `.ufo/waves/round-64/controls/freeze.txt`. Evidence: `.ufo/waves/round-64/b/out/RV02CounterCode/` (receipts, drivers, leak log).
No lane file was edited, nothing committed. Scratch clone and driver copies lived under `/fast/scratch/hyaku/kama-r64/b/RV02CounterCode/` (removed before yield). No packages were installed (no tool/version/channel to record).

Method: line-by-line reading; then live runs of the counter at the tip; a copy of the counter with `is_hit` instrumented (scratch only) to log every control's failure-set size; small drivers that import the counter and call `witness_run` / `score_run` / `grade_binding` directly to test the defects below end to end.

## Headline

- Counter at the tip prints `met=True` (exit 0), but three defects can make it say `met=True` where the frozen predicate says no. Two are confirmed end to end (D1, D2); one is a deviation from the frozen caps that the code does not declare (D3).
- The leak path is real: when a tool fails to tear down, the held llama-server survives the counter (confirmed, D5).
- The eval selftest gate is vacuous for its envelope case (D4).
- Resource/hygiene and fail-open details are listed with their flip direction in section 3.

## 1. Verdict-capable defects (ranked)

**D1 [CONFIRMED, flips to met=True] The receipt's live answers are never bound to the held child.**
- `grade()` 523-594 checks the completion/completion2 captures only for self-consistency (envelope, headers, choice shape, usage sums, id/created, `request_sha256`, text equality between completion and completion2). Nothing compares the receipt's answer text, usage or timings with what the held child actually returns.
- The only receipt-to-live link is `live_fp_capture` (score 700-701): the receipt's `system_fingerprint` equals the probe's. By its shape (`FP_RE`, 549/651, `b<N>-<hex>`) that is a build identifier, so equality shows a build match, not that this process answered the tool's request.
- The counter's live probes (`draw_probes`, `probe`) are the counter's own prompts; the tool's PROMPT is never sent by the counter, so the tool's own completion is never checked live.
- Evidence (`out/RV02CounterCode/e1e4.out`): genuine run `met=True`; held child's answer to probe 0 is `'s.\n'`; receipt completion text is `' ground. She liked'`. I rewrote the receipt's completion and completion2 text to `' FABRICATED BY TOOL'` and re-sealed the bodies (`edit_body`): `E1 fabricated-answer receipt met=True fails=[]`.
- Contradicts the docstring claim at line 27 ("never trusts receipt-claimed results"). The freeze's C1 kill rule ("a receipt the counter accepts without its own live contact") is only partly met: the receipt is accepted with live contact for two other prompts, not for its own request.
- Fix direction (for the L1): send the tool's exact request to the held child (or the reference) and compare text, usage and finish_reason with the receipt's capture; add a control that replaces the text with a re-sealed body.

**D2 [CONFIRMED, flips to met=True] `bind_argv` and `bind_env` do not enforce the pinned argv/environment set.**
- `grade_binding` 421-433 (`argv_ok`) checks exactly four flags: `--port`, `--host`, `--alias`, `--model`. Any other flag passes (`-c`, `-t`, `--log-file`, `--load-mode`, ...). The predicate says "its argv ... are the pinned set".
- `-m` is the same option as `--model` (`llama-server --help` line 179: `-m, --model FNAME`), and the last one wins: `--model <pinned> -m <other>` loads `<other>` (verified: server log `load_model: loading model '.../does-not-exist.gguf'`, exit 1). `argv_ok` reads only `--model`, so the trailing `-m` is invisible to it.
- `bind_env` 434-437 is a denylist (`LD_*`, `GLIBC_TUNABLES`). `--help` lists env overrides such as `LLAMA_ARG_MODEL` and `LLAMA_ARG_*`; they are not checked. Synthetic test (`e1e4.out`, E5): a raw snapshot with `--log-file /tmp/x.log -c 4096` and `LLAMA_ARG_NO_MMAP` in environ gives `bind_argv=True bind_env=True`.
- End to end (`e4b.out`): a holder launched as `server --model <pinned> -m <copy> --load-mode none` (a byte-identical copy at another path; the server log confirms it loaded the copy) gives `E4b argv -m copy + --load-mode none met=True fails=[]`.
- Mitigation that exists: with the default mmap load, `bind_maps` rejects the copy (`E4 mmap met=False fails=['bind_maps']`, `e1e4.out`). The no-mmap form (`--load-mode none`) escapes every bind check. None of the 76 controls covers an extra flag, a second model flag or an env override.
- Fix direction: compare the full `cmdline` against the pinned argv (exact list, with `--model`/`-m` both checked), and compare `environ_keys` to an allowlist, not a denylist.

**D3 [CODE vs FROZEN TEXT, flips to met=True] Fake-tool controls are credited at cap 99; the freeze names 5.**
- `run_controls` 1618 calls `credit(fam, s, expect, 99, label, clean_receipt=True)` for the seven live fake scenarios. The default cap is 5 (`MAX_COLLATERAL`, line 55); the freeze text gives 5 by default, 30 for the envelope, 14 for a patched forgery, and adds "a fake-tool scenario holding a genuine receipt copy must in addition show no receipt-level failure". It names no separate cap for fake scenarios. The 99 is not declared anywhere.
- Instrumented run (`out/RV02CounterCode/is_hit.json`, `run1`/`run2`): the seven fake credits had failure-set sizes `detach 2, proxy 6, canned 16, stale_old 21, stale_future 21, preload 1, pathcopy 4`. Fail sets do not depend on the cap, so under cap 5 the four credits with n = 6, 16, 21, 21 would be escapes and the tip would print `families_exact=0 ... met=False`.
- So the printed `met=True` depends on an undeclared cap. Either the freeze text or line 1618 is wrong; the L1 must decide and record it (an amendment, not a silent change). I did not decide which.

**D4 [CONFIRMED, vacuous gate] The eval selftest passes its envelope case without the named check mattering.**
- `eval_selftest_run` 1542-1545 flips `object` to `chat.completion` and expects `is_hit(...,'completion_envelope')` at the default cap 5. That edit makes 26 checks fail (`is_hit.json`, last rows: `completion_envelope 5 26 False`), so `is_hit` is False on the cap, not on the named check. The gate counts it as refused.
- So `eval_selftest=3/3` holds even if `completion_envelope` were deleted from `grade()`. The gate can let a broken evaluator through (flip toward met=True). Fix: test the named check with the cap raised (the envelope cap of 30), and make each selftest assert the expected reason, not only "not refused".
- Selftest 1 (stale nonce, expects `live_ptok`) and selftest 3 (genuine, expects `nonce_match`) are wrong-reason checks and do work as written.

**D5 [CONFIRMED, leak; flips nothing] Holders and tool are not killed on failure paths.**
- `witness_run` 856-939 has no try/finally. Failure paths: no `hold.json` in 120 s (884-914) → release written (916), teardown loop skipped (918), `proc.wait(60)` then `proc.kill()` (929-933) kills only the tool. Teardown failure (30 s, 920-927) → the same kill, and the holders recorded in `binding['raw_a']` are never signalled. No holder is killed on any path.
- Confirmed with `leak_tool_hang.py` (never writes hold.json) and `leak_tool_noexit.py` (writes hold.json, ignores release), each spawning a real pinned llama-server with no PDEATHSIG (`e2-leak-results.txt`):
  - hang: witness returned after 180 s, no receipt/witness/binding; **llama-server pid 2443191 alive after the counter returned**.
  - noexit: returned after 91 s (30 s teardown wait + 60 s wait); **llama-server pid 2655336 alive**.
  - I killed both orphans myself after recording them (they were started by my drivers).
- The tip tool's own server child is protected: `kama-completion-live.py` 330-331 sets `preexec_fn=_preexec_pdeathsig` (`kama-llamacpp-live.py` 662-671 `prctl(PR_SET_PDEATHSIG, SIGKILL)`), so a SIGKILLed tip tool should take its server with it. [INFERENCE: not measured against the tip tool; the leak was measured with non-PDEATHSIG tools.] The leak is therefore real for forged/fake tools and for any future tool that drops PDEATHSIG; it does not flip the verdict (those paths already yield `met=False`), but it leaves a loopback server behind on every forged-tool failure.
- Fix: put the whole body in try/finally; after teardown (or on any exit), SIGKILL every recorded holder pid and the tool's process group; create the tool with `start_new_session=True`.

**D6 [flips toward met=True, needs privilege] `holder_pids` skips other-uid holders silently.**
- `holder_pids` 270-276: a `PermissionError` on `/proc/<pid>/fd` is recorded only when the pid's uid equals ours; otherwise it is skipped with no record. A root or other-uid process holding the run-port listener is invisible to `bind_holders`/`bind_listener`. The docstring says "fails closed on unreadable own-uid tables"; for foreign uids it fails open.
- Reachable on this host because passwordless sudo exists; a forger that passes a root-owned holder would not be seen. Fix: treat any unreadable holder as unreadable (record all `PermissionError`s with the uid).

**D7 [low, flips toward met=True] `maps_ok` exempts everything under `/usr/lib/`, `/lib/` and friends (`SYSTEM_PREFIXES`, 140, 451-452) without hashing.** A dlopen'd plugin placed in a root-writable system directory passes `bind_maps`. Requires root to place the file. Fix: hash mapped system files against an allowlist or drop the blanket prefix exemption.

**D8 [low] `hold_fresh` has only a lower bound on the hold.json mtime (470-471: `mt > t0`).** A hold.json dated in the future passes freshness; it is rejected only by the `start_ticks >= tool_start` test (`stale_future` escapes on that test). Defence in depth only. Fix: also require `mt <= now`.

**D9 [latent] `sha256_path` cache (166-179) is keyed by path and caches failures.** Verified: after replacing a file at a cached path, `sha256_path(p)` returns the old digest (`cached==old True`), `cache=False` returns the new one. Cached use: `argv_ok` model (432), `read_maps` libs (334), `pick_server` (1449), `grade` model/server digests (604, 607). The holder's `/proc/<pid>/exe` is hashed fresh (`holder_record` 344, `cache=False`), which is what `bind_exe` uses. No path is rewritten inside one run today (fakes write new paths), so no flip now. Fix: key by (path, st_ino, st_mtime_ns, st_size), or drop the cache.

**D10 [latent] `apply_patch` uses `patch -p1 -F3 -s` and checks only the exit code (1156-1158).** Fuzz and offset are silent. Checked: all seven forgery-A hunks match exactly once in the tip tool (lines 55, 239, 296, 316, 330, 364, 569), applied with offsets 8-55 and no fuzz text, so nothing is misplaced today. Forgery B is a delta on A; applied to A-patched it succeeds with offset 44, and I did not check that B's hunks are unique. Fix: `patch --dry-run` first and reject any output containing `fuzz` or `offset` (or assert single exact matches).

**D11 [CONFIRMED, operability, flips toward met=False] A reused `--work` breaks the fake scenarios.** Second run on the same work directory (`out/RV02CounterCode/reuse.out`): `controls_targeted=69/76 ... met=False`; all seven fake scenarios (`detach, proxy, canned, stale_old, stale_future, preload, pathcopy`) fail with `tool exited before hold.json`. Most likely cause [INFERENCE]: the fake scenario directories keep the old `hold/release`, so `hold_and_release` returns at once and the fake exits before the counter sees `hold.json`. Only the genuine tool clears its hold dir (`prepare_witness_dir`). The C1 counter has no reuse refusal (the C2 counter is meant to have one). Fix: delete `wd` (or refuse a non-empty `--work`) before a run.

**D12 [low, flips toward met=False] `pid_gone` treats unreadable/unknown as gone.** `pid_gone` 846-848: `start_ticks=None` makes it return True for a live pid (verified: `pid_gone(self, None) -> True`, `pid_gone(self, correct) -> False`); 850-853: any exception returns True. In `witness_run` 920-923, `all([])` is also True when the holder list is empty. The port-closed check (924) is the backstop, so a false "gone" needs the port check to pass too. Fix: fail closed (`return False` on unknown/unreadable), and require `hs` non-empty.

## 2. Answers to the specific review questions

- Resource leaks / servers left after an exception: no try/finally in `witness_run` (856-939) or `main` (1454-1522); a non-tool exception leaves the tool and its children to their own timeouts (D5). The reference server is torn down correctly in `reference_run`'s finally (831-839). `reference_run` opens its log before `Popen` (810), so a failed Popen leaks the file handle only.
- Ref-server teardown: `reference_run` sends SIGTERM, waits 15 s, kills, waits 10 s (831-839). The second `wait` can raise uncaught `TimeoutExpired` (838), which is an error, not a leak.
- Files outside `--work` / under `/tmp`: no file is written outside `--work` by the counter itself (decoy, tip tree, forged trees, fake scripts, hold dirs, receipts all under `work`). But `_TOOL_ENV_KEYS` (148) passes `TMPDIR` and `HOME` from the caller (868, 815), and `Popen` at 811 and 872 sets no `cwd`, so the tool and reference inherit the caller's cwd. This breaks the freeze's "never an inherited TMPDIR" rule; I did not observe the tip tool writing outside `--work`. Fix: `cwd=work`, `TMPDIR=work` in the env.
- Hardcoded paths: `~/.local/opt/llama-b11755/llama-server` (1446-1447, no realpath, so a symlink would fail `bind_exe`), `~/.cache/kama-shokunin/models/stories260K.gguf` (1466-1467), `/usr/lib/libm.so.6` (1108), and the reference's `-c 512 -t 1` (812-813) which silently mirror the tool's defaults (`kama-completion-live.py` 646-647). A tool-side change to ctx/threads gives a false live reject, not a false pass.
- Global `NONCE` (1463, 1489, 1554): the swap/restore around fake and forged scoring (1613-1617, 1655-1659, 1695-1699) is correct, and `credit()` runs after the restore. The global is fragile (any scoring before 1489 sees `''`), but no defect found.
- Timeouts: HTTP 10 s (203), reference health 60 s (820), witness hold 120 s (884), teardown 30 s (920), tool wait 60 s (930), kill wait 10 s (933, 838) with no handling of `TimeoutExpired` on the kill waits. None flips a verdict.
- Zombie handling in `pid_gone`: `Z`/`X` treated as gone (851-852). Acceptable, since a zombie holds no sockets. `rindex(')')` handles odd comm names. The real issue is the fail-open paths in D12.
- `/proc/<pid>/exe` hashing: fresh each time (`holder_record` 344, `cache=False`). The cache applies to `read_maps` (334), `argv_ok` (432), `pick_server` (1449) and `grade` (604, 607) — see D9.
- Forged-variant patch application (`patch -F3`): see D10. `forge_variants` returns `{}` (1171-1172) when a patch is missing, which counts the forge family as escaped (1624-1627): surfaced via `detail`, not via `errors`, but `met` still goes False.
- Exceptions swallowed to "no credit": these paths are recorded but not counted in `errors`, so `errors=0` can print while `met=False`: fake no-receipt (1608-1612), forge no-receipt (1652-1654), relabel could-not-run (1704-1706), forge patch missing (1624-1627). They print only the first 12 `detail` lines to stderr (1520). None can produce `met=True` (`fam_match` fails); they are a reporting gap.
- Exceptions that escape: `main` 1484 (`reference_run`), 1487 (`witness_run`), 1498 (`score_run`), 1570 (`build_controls`), 1622 (`forge_variants`) are not in a try; an exception prints a traceback and no `met=` line, exit 1. Surfaced, not swallowed.
- `grade()` 622 assumes `checks` values are dicts; a non-dict value raises `AttributeError`. Inside the fake/forge try it becomes an `errors` entry; in the live path (1498) it crashes the run. Surfaced; no flip.
- Dead/misleading check: `score_run` 1530-1532 `live_nonce` checks the counter's own `sent_prompt` (built at 762 and echoed at 777). It is always true, so it binds nothing.
- Receipt-claimed paths in `grade`: `model_digest` (604) and `server_digest` (607) hash the path the receipt names. The binding (`bind_exe`, `bind_maps`) is the real gate; these are redundant and not a flip on their own.
- Teardown holders come from the first snapshot only (`raw_a`, 919); a child that starts holding the listener after the snapshot is watched only through `port_closed`. Conservative (a false reject), not a flip.

## 3. Leak measurement (required)

Command: `pgrep -af llama-server` before and after one counter run (`out/RV02CounterCode/pgrep-before.txt`, `pgrep-after.txt`), run1 from cwd `/fast/scratch/hyaku/kama-r64/b/RV02CounterCode` with `--work` at `.../RV02CounterCode/work`.
- Before: 16 lines. After: 10 lines.
- Removed (exited): 14233 (MT06 probe-mt06), 588580/589218 (MT10 fake-pathcopy), 590194 (MT07 tool), 590478 (MT12 fake), 590499 and 591305 (kama-completion-probe servers from other seats' runs), 591662/592211 (MT11 fake and copy).
- Added during the window: 667360 (MT07 tool, another seat), 668265 and 669597 (llama-server `kama-completion-probe`, `-c 512 -t 1`, the counter's reference/held-child signature). They had exited by the time I could read their ppid or cwd, so I cannot attribute them. Nothing in my run is still alive.
- Attributable check (run2 from cwd `.../RV02CounterCode/run2`, then reuse run, then both leak drivers): a scan of every live process whose cwd or cmdline contains the RV02 scratch after each run found **zero survivors from the counter run** (`run2-before/after.txt`).
- Leaks from the deliberately broken tools (D5): 2 llama-servers (pids 2443191, 2655336), both killed by me after observation.

## 4. Verification gaps and what I did not do

- Did not mutate or commit the counter; the defects above are read from the code and checked with scratch drivers that import the committed module, not with the mutant protocol.
- D1 and D2 are shown with one fabricated-answer receipt and one `-m` holder; they are not yet shown to pass through a full live tip-tool run (a tool built to do it). The drivers used the counter's own `witness_run` path, so the holder and receipt bytes are real.
- D3's escape counts come from instrumentation of the scratch copy; they were not reproduced with a cap-5 build.
- The PDEATHSIG protection of the tip tool's server child was read from code; not measured.
- Did not run the C2 counter, the round-63 instruments or the lane's other tools.

## 5. Counter output (tip, unmodified)

`tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]` (exit 0; the same line is in `out/RV02CounterCode/run1.out`). Reused-`--work` run: `... controls_targeted=69/76 ... met=False` (exit 1; `reuse.out`).
