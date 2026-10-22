# RerunC2Counter: falsify of the C2 claim value (round 25, attempt 2, wave 2)

Target: committed counter and receipt at lane tip fa3b62ae6475d111eb466d79af616aeebb08bbb9.
Seat: KamaR25a2.RerunC2Counter (leaf member, no subagents, no llama-server started).

**Verdict: defect found in the counter; the claim value itself holds.** On fa3b62ae the committed receipt reads `registered 14 observed 14 bound True missing []` with exit 0 under every requested run. But the committed counter also prints `observed 14` for mutated receipts whose own tool verdict, teardown record, or cross-checked values are wrong: 12 in my battery, plus 2 more from a sibling-seat cross-check (raw hashes zeroed, `cells_drift` noise; section 3a). A scratch candidate closes the original 12 and still reads 14 on the committed receipt; it does not close the 2 addendum cases (section 5). The committed receipt itself has no such faults (checked below), so the reported value is not affected today.

## 1. Requested runs (exact outputs, exit codes)

Source: `.ufo/waves/round-25/a2-falsify/out/RerunC2Counter/RUNS.txt` (one read-only run, 2026-10-22T10:17:31Z UTC, plus R7 appended later).

```
## R1 committed counter fa3b62ae, exact assignment pipeline, worktree receipt
+ git show fa3b62ae:.ufo/waves/round-25/count-c2.py | (cd lane && python3 - .ufo/waves/round-25/final/context-capacity-receipt.json)
registered 14 observed 14 bound True missing []
exit=0
## R2 committed counter fa3b62ae, receipt bytes from git show fa3b62ae
+ git show fa3b62ae:.ufo/waves/round-25/final/context-capacity-receipt.json > receipt-fa3b62ae.json ; git show fa3b62ae:.ufo/waves/round-25/count-c2.py | python3 - receipt-fa3b62ae.json
registered 14 observed 14 bound True missing []
exit=0
## R3 amendment-2 counter 5388b7cf, worktree receipt
+ git show 5388b7cf:.ufo/waves/round-25/count-c2.py | (cd lane && python3 - .ufo/waves/round-25/final/context-capacity-receipt.json)
registered 14 observed 14 bound True missing []
exit=0
## R4 amendment-2 counter 5388b7cf, materialized receipt
registered 14 observed 14 bound True missing []
exit=0
## R5 superseded preregistration C2 command (counts the tool's own observed flag)
cells 14 observed 14
exit=0
## R6 receipt identity
cmp_worktree_exit=0
blob=516f46002197dce8526f5af71831e1a99e9b3364 materialized=516f46002197dce8526f5af71831e1a99e9b3364
## R7 superseded command on mutants (see section 3 for the mutant definitions)
m00_base: cells 14 observed 14 exit=0
m01_observed_false_error_K1: cells 14 observed 13 exit=0
m18_X2_observed_false_only: cells 14 observed 13 exit=0
m20_top_exit_1_error: cells 14 observed 14 exit=0
```

Byte identity: the committed counter at fa3b62ae is 6193 bytes (blob 9fdab9e7, sha256 7bf3f9cd...), identical to the worktree file (`cmp` exit 0). The amendment-2 counter at 5388b7cf is 4115 bytes (blob 1c78a96b, sha256 e8553c5b...). The receipt is 413554 bytes, blob 516f4600, identical in fa3b62ae and 5c95c8f1.

Timeline (`git log`, committer times): amendment 4 (46fb04b) 09:42:31Z; receipt run started 09:42:42.438Z and ended 09:42:50.502Z; receipt commit (5c95c8f1) 09:42:57Z. The receipt postdates the counter that scores it. [checked, no finding]

## 2. The receipt's own values (is 14 a real observation?)

All checks below read the committed bytes (materialized to scratch by `git show` or `git archive`). Outputs are in out/RerunC2Counter/.

- **Top level** (`receipt-dump-fa3b62ae.txt`): `exit_code: 0`, `error: null`, `cells_drift: []`, `summary: {cells 14, observed 14, all_ports_closed true}`, `server_version: "version: 0.7.0-dev (build 11755, commit 704366d76)"`, `model_sha256: 270cba1b...256d`.
- **Per cell** (`consistency-fa3b62ae.txt`, 0 failures): `observed` true, `error` null, `child_returncode` 0, `port_closed` true, `ss_listen_lines_after` empty for all 14 cells. Child windows do not overlap; ports 47400 to 47413 are distinct and outside the refusal set [8080, 34113], which equals the consumer ports in `registry/endpoint-consumers.tsv`. `argv` ends with the registered args, its `--port` equals the cell port, its `-m` equals the fixture path. Per-slot `n_ctx` equals `props_n_ctx` everywhere; `n_slots` and `n_ctx_slot` in the log agree with `total_slots` and the slot list; the pool equals the last log pool line. L1 has two HTTP 500 answers with `Context size has been exceeded.`; L2 and L3 have two HTTP 200 answers each with `tokens_predicted` 600 and `truncated` false. `concurrency_delta_s` is 0.0001 for L1 and L2. (My first run of this check reported one failure, on L3, because my script wrongly required a concurrency delta on the sequential cell. The tool records None there, which is correct. I fixed the script and re-ran; the file shows 0 failures.)
- **Raw bytes** (`raw-check-fa3b62ae.txt`, 0 failures): all 70 committed raw files (`git archive fa3b62ae .ufo/waves/round-25/final/raw`) hash to the receipt's `raw_*` values. Props `n_ctx`, slot count, per-slot `n_ctx`, `n_ctx_train`, and the pool lines all agree with the raw bodies.
- **Server logs** (`log-check-fa3b62ae.txt`): every receipt `log_lines` entry appears in the committed raw `server.log` (the receipt keeps a filtered subset). The raw K1 and L1 logs both print `build 11755 (704366d76)`, which independently backs the bound check. L1, L2, and L3 each carry two `task.n_tokens = 1000` lines.
- **On-disk binaries** (hashes only, nothing run): `/home/vgpnk/.local/opt/llama-b11755/llama-server` sha256 b6a31a8e... equals the receipt's `server.sha256`; `stories260K.gguf` sha256 270cba1b... equals `model_sha256`; `tools/kama-context-capacity.py` at fa3b62ae sha256 589841cd... equals the receipt's `tool.sha256`.
- **Calibration only, not claim value**: the 13 gradable predictions in amendments 1 and 2 (K1 to K5, K7, K8, X1 to X3, L1 to L3) agree with the receipt per-slot and pool values. K6 is recorded without a grade. X1 gives pool 8192 and per-slot 2048, not the round-20 value of 512.

## 3. Counter strength: negative battery

Scripts: `scripts/battery.py`, `scripts/battery_candidate.py`. Results: `battery.txt`, `candidate-battery.txt`. Each mutant is one edit to the committed receipt, run in its own process under both counter byte sets. The committed counter read is `fa3b62ae`; "A2" is amendment-2 bytes `5388b7cf`; "Cand" is the scratch candidate in section 5. Exit code is 0 in every run.

| mutant | what is wrong | fa3b62ae | A2 5388b7cf | Cand |
|---|---|---|---|---|
| m00 | none (control) | 14 True | 14 True | 14 True |
| m01 | K1 `observed` false, `error` set (tool verdict) | 14 True | 14 True | 13 [K1] |
| m02 | K2 port still listening, child code null, `observed` false (teardown) | 14 True | 14 True | 13 [K2] |
| m03 | K3 `error` "ready-timeout", `observed` false | 14 True | 14 True | 13 [K3] |
| m04 | K4 cell `server_sha256` differs from top level | 14 True | 14 True | 13 [K4] |
| m05 | K5 cell `model_sha256` wrong | 14 False | 14 True | 14 False |
| m06 | top-level build "117550" | 14 False | 14 True | 14 False |
| m07 | K1 last log pool line 12048, `kv_pool_n_ctx` 2048 | 13 [K1] | 14 True | 13 [K1] |
| m08 | K1 `slots_n_ctx` [1,1,1,1] against log `n_ctx_slot` 2048 | 14 True | 14 True | 13 [K1] |
| m09 | K2 `props_n_ctx` 7 against slots 1024 | 14 True | 14 True | 13 [K2] |
| m10 | K6 argv `--port` 47999, cell port 47405 | 14 True | 14 True | 13 [K6] |
| m11 | K7 argv `-m` /tmp/other.gguf | 14 True | 14 True | 13 [K7] |
| m12 | L3 sequential requests overlap in time | 13 [L3] | 14 True | 13 [L3] |
| m13 | L2 one request HTTP 503 (counted by design: integer status) | 14 True | 14 True | 14 True |
| m14 | L2 HTTP 200 answers with `tokens_predicted` 0 | 14 True | 14 True | 13 [L2] |
| m15 | K8 removed | 13 [K8] | 13 [K8] | 13 [K8] |
| m16 | K1 duplicated | 13 [K1] | 13 [K1] | 13 [K1] |
| m17 | K5 args with trailing space | 13 [K5] | 13 [K5] | 13 [K5] |
| m18 | X2 `observed` false only | 14 True | 14 True | 13 [X2] |
| m19 | K4 child return code null | 14 True | 14 True | 13 [K4] |
| m20 | top-level `exit_code` 1, `error` set | 14 True | 14 True | 0 True (all missing) |
| m21 | K1 `total_slots` "4" (string) | 13 [K1] | 13 [K1] | 13 [K1] |
| m22 | K1 `props_n_ctx` true (boolean) | 13 [K1] | 13 [K1] | 13 [K1] |
| m23 | K1 `kv_pool_n_ctx` 8 against log 2048 (suffix) | 13 [K1] | 14 True | 13 [K1] |
| m24 | no `server_version` | 14 False | 14 False | 14 False |
| m25 | K3 slot list length 1 against total 2 | 13 [K3] | 14 True | 13 [K3] |
| m26 | L1 three requests | 13 [L1] | 14 True | 13 [L1] |
| m27 | L2 requests without timings | 13 [L2] | 14 True | 13 [L2] |
| m28 | L2 request status 700 | 13 [L2] | 14 True | 13 [L2] |
| m29 | top-level model sha wrong | 14 False | 14 False | 14 False |

Reading the table:
- Besides the control m00, the committed counter prints `observed 14` for 16 mutants: fourteen contain a real fault (m01 to m04, m08 to m11, m14, m18 to m20, plus the addendum's m30 and m31), and m13 (one HTTP 503 answer) and m32 (L1 answers flipped to HTTP 200) are counted by the registered rule on purpose (addendum).
- Six of the fourteen ignore the tool's own verdict or teardown record (m01, m02, m03, m18, m19, m20). The other eight are internal contradictions that the counter does not compare (m04, m08, m09, m10, m11, m14, m30, m31).
- A2 (amendment 2) accepts nine receipts that the committed counter rejects: m05 and m06 differ only in the bound flag; m07, m12, m23, m25 to m28 change the count. This matches the amendment 3 and 4 history.
- Battery predictions: 59 of 60 runs matched. The one miss was my own error: I predicted A2 would reject m05, but A2 checks only the top-level model sha. Candidate predictions matched 30 of 30.
- The committed counter reads none of these fields: `observed`, `error`, `teardown`, `server_sha256`, `exit_code`, `port`, `port_closed`, `concurrency_delta_s`, `tokens_predicted`, `truncated`, `task.n_tokens` (`grep -n` exit 1, no output, on the fa3b62ae counter).

History control (receipt 5ea4fc44, which amendment 4 says scores 11 of 14): committed counter prints `registered 14 observed 11 bound True missing ['L1', 'L2', 'L3']`, exit 0. A2 prints 14. This reproduces amendment 4's claim.

Exit code: the committed counter exits 0 for every verdict, including 11 of 14 and 0 of 14 (`counter line 24` says so; `line 144` is `return 0`). A closure gate that tests the exit code would pass the 11-of-14 receipt and the m20 receipt.

Wave-1 corpus (`.ufo/waves/round-25/a2-build/out/MutationC2Counter/receipts/`, 45 files, committed): committed counter rejects all 45 (`attack-receipts-committed-counter-results.tsv`). This corpus has no positive control under the current rules. `valid_all_14.json` has no `argv` in its cells, so the counter rejects it as incomplete, not for any fault it was built to test. The 45-of-45 result therefore shows field-presence rejection only.

### 3a. Addendum: cross-check with ReplicateReceipt

Sibling seat KamaR25a2.ReplicateReceipt independently reproduced the committed receipt (three fresh 14-cell runs plus two load-only runs of tools/kama-context-capacity.py at fa3b62ae, every cell value identical; committed counter 14/14 on each; transcript `.ufo/waves/round-25/a2-falsify/out/ReplicateReceipt/counter-probes.txt`, not re-verified by me) and reported a counter probe list that matches my battery. Their list adds three cases I had not tested; I ran them as m30 to m32 (`out/RerunC2Counter/addendum-replicate-cross-check.txt`, each exit 0):

| mutant | what is wrong | fa3b62ae | Cand |
|---|---|---|---|
| m30 | K1 per-cell raw sha256 values all zeroed | 14 True | 14 True |
| m31 | top-level `cells_drift` non-empty | 14 True | 14 True |
| m32 | L1's two answers flipped to HTTP 200 with 600 tokens (the opposite of the recorded failure) | 14 True | 14 True |

- The committed counter cannot see any of the three: it reads neither `raw` hashes nor `cells_drift`, and it accepts any 200 answer whose token fields match its constants. On argv their probe and mine agree once split: the counter rejects argv edits that break shape (args suffix, missing launch flags) and accepts value edits it never cross-checks (my m10 `--port`, my m11 `-m`).
- The candidate closes none of the three as built. m32 is by design: the registered rule counts recorded outcomes, not predictions, so an L1 that succeeds is a legitimate prediction-falsifying observation. m30 and m31 are real candidate gaps; closing m30 truthfully needs the raw files, which the counter does not read today.

## 4. Findings, by severity

**F1, medium: the counter does not read the tool's own verdict or teardown.**
- Evidence: the tool sets `observed` at `tools/kama-context-capacity.py:396-416`, from `error`, child return code, port closed, and load-request rules. Its own comment at lines 398-399 says a cell whose child was not reaped or whose port did not close is never an observation. The tool proves teardown in `_teardown` at lines 556-595, and sets top-level `exit_code` at lines 817-826. The committed counter never reads any of these (grep exit 1).
- Effect: m01, m02, m03, m18, m19, m20 print `observed 14`. The registered measure says "torn down in the same run" (`preregistration.json`, `claims[C2].measure`), and amendment 2's `launch_rule` says "killed and port confirmed closed". The counter does not enforce either.
- Committed receipt: not affected. Every cell's verdict is clean (section 2).
- Note: the superseded command in `preregistration.json` (R5 and R7) does read `observed`, so it catches m01 and m18, but not m20.

**F2, medium-low: cross-field contradictions are accepted.**
- Evidence: `count-c2.py` (fa3b62ae) checks types, presence, positivity, and one pool line (lines 69-110). It never compares a cell's `server_sha256` with the top-level binary hash, its `slots_n_ctx` with the log `n_ctx_slot`, its `props_n_ctx` with its slots, its argv `--port` or `-m` with the cell, or a 200 answer's `tokens_predicted` with the requested 600.
- Effect: m04, m08, m09, m10, m11, m14 print `observed 14`. The bound check (line 137) covers only the top-level version text and model sha, plus cell-level model sha. It does not bind the binary identity per cell.

**F3, low: exit code carries no verdict.**
- Evidence: `count-c2.py` line 24 ("Exit 0 always when the receipt parses") and line 144 (`return 0`).
- Effect: a gate that reads the exit code passes 11-of-14 and 0-of-14 receipts.

**F4, low: the 1000-token check reads the tool's constant, not the server's count.**
- Evidence: the tool writes `prompt_tokens: LOAD_PROMPT_TOKENS` and `n_predict: LOAD_N_PREDICT` into every request record, including error records (`tools/kama-context-capacity.py:439, 477, 526-527`). The counter checks those fields against `LOAD_REQUEST` (`count-c2.py:32, 102-103`).
- Effect: the check confirms the tool's own input size, not the server's acknowledgement. The server log carries `task.n_tokens = 1000` lines (two per load cell, in the receipt and in the raw logs), which the counter does not read.

**F5, low: coverage of the instrument.** The 45-file wave-1 corpus has no positive control under the current rules (section 3). Its rejections come from missing fields, so it does not test the field-level contradictions in F1 and F2.

**Info, no effect on the count:**
- The registered launch line names `~/.local/bin/llama-server`, but `argv[0]` is the symlink target `/home/vgpnk/.local/opt/llama-b11755/llama-server`. Same binary, same sha256.
- The receipt's `log_lines` are a filtered subset of the raw server logs, not identical copies. Every line is present in the raw logs.
- The earlier draft of my own consistency check had a bug; it is fixed and the saved output is the corrected run.

## 5. Smallest correction (recommendation for L1; not applied, lane files untouched)

Candidate, scratch only: `out/RerunC2Counter/count-c2.candidate.py`, 202 lines (committed counter 148 lines), sha256 214d8be9bd75ee8f8961a50cc45b7c1539b2397bd3370cca129e4d71ad544c17. It is the committed counter plus one function, `verdict_ok`, and a top-level gate:
1. top-level `exit_code` is 0 and `error` is null, else observed is 0;
2. per cell: `observed` is true, `error` is null, `teardown.port_closed` is true, `child_returncode` is an integer, `ss_listen_lines_after` is empty;
3. per cell: `server_sha256` equals the top-level `server.sha256`;
4. argv `--port` equals the cell port and argv `-m` equals `model.realpath`;
5. log `n_slots` and `n_ctx_slot` agree with `total_slots` and every slot entry, and `props_n_ctx` equals every slot entry;
6. load cells: any HTTP 200 answer has `tokens_predicted` 600 and `truncated` false; the concurrent cells have `concurrency_delta_s` at most 0.05.

Because it only adds conditions, the candidate accepts a subset of what the committed counter accepts. Results (`candidate-battery.txt`): the committed receipt reads `registered 14 observed 14 bound True missing []`, exit 0; the earlier receipt 5ea4fc44 reads `observed 11 ... missing ['L1', 'L2', 'L3']`; 12 of the 12 original blind mutants are rejected; m13 is still counted, by design; 30 of 30 battery predictions matched what I predicted before the run. Candidate gaps found in the addendum: m30 (raw hashes) and m31 (`cells_drift`) are still accepted, and m32 (an L1 that succeeds) is accepted by design. Closing m30 truthfully needs the raw files, which the counter does not read today; `cells_drift == []` is a one-line check the candidate could take.

Recommended change, through the registered amendment chain (the counter is a registered instrument, so the change must be recorded as an amendment, not a silent edit):
- register the six checks above as amendment 5;
- make the exit code 1 unless observed equals registered and bound is True;
- commit the committed receipt as the positive control and the 12 blind mutants as negative controls;
- optionally check the server's `task.n_tokens = 1000` lines instead of the tool constant (F4).

The committed receipt's claim value (14 observed, bound True) does not change under any of this.

## 6. Residual risk and verification gaps

- No live run: I started no llama-server, per the assignment. The raw bodies and logs agree with the receipt and with the on-disk binary and model hashes, but I did not independently re-observe the live server.
- I audited only the tool paths that feed the counter (observed, teardown, request records, refusal set, exit code). I did not audit the rest of the tool.
- Not checked, outside this attack: the knowledge entry, the SKILL decision rows, the SCORECARD row, the report draft, and the critic's 20,000-cell comparison.
- Mutants: 30 single edits to one receipt, plus m30 to m32 from the ReplicateReceipt cross-check. This is a negative-control set, not an exhaustive search. The fresh receipt re-runs behind the cross-check are that seat's evidence, not re-verified by me.
- The `lsp` device is not in this seat's tool list. The counter is a standalone Python script, so caller graphs do not apply. I used script runs and direct reads, and I did not use grep output as semantic proof.
- Prediction grades are calibration only and are not part of the claim value.

## 7. Tools and installs

- No installs or upgrades. I did not open `/home/vgpnk/.omp/agent/RULES.md`, since nothing needed installing.
- Tools used: `/usr/bin/python3` (Python 3.14.8), `git` (read-only: `log`, `cat-file`, `rev-parse`, `show`, `ls-tree`, `archive` piped to scratch, `hash-object` without `-w`), `sha256sum`, `cmp`, `tar`, `grep`, `pgrep`.
- No jj command, no git write, no commit, no push, no reset, no stash.
- llama-server: none started. `pgrep -a llama-server` returned none running. No port was opened.

## 8. Files written

Advice report (lane): `.ufo/waves/round-25/a2-falsify/advice/RerunC2Counter.md` (this file).

Outputs (lane, `.ufo/waves/round-25/a2-falsify/out/RerunC2Counter/`):
- `RUNS.txt` (R1 to R7, one log)
- `battery.txt` (30 mutants under both counters, history control, full stdout and stderr)
- `candidate-battery.txt` (candidate on the same mutants, history control, sha256)
- `addendum-replicate-cross-check.txt` (m30 to m32 under both counters, from the ReplicateReceipt cross-check)
- `attack-receipts-committed-counter-results.tsv` (committed counter on the 45 wave-1 receipts)
- `consistency-fa3b62ae.txt`, `consistency.stderr` (empty)
- `receipt-dump-fa3b62ae.txt`, `receipt-dump.stderr` (empty)
- `log-check-fa3b62ae.txt`
- `raw-check-fa3b62ae.txt`
- `count-c2.fa3b62ae.py`, `count-c2.5388b7cf.py`, `count-c2.candidate.py` (copies of the scored bytes; the first two match the committed blobs)
- `run1-committed-counter-fa3b62ae-worktree-receipt.stdout`, `run1.stderr`, `run3-amendment2-counter-5388b7cf-worktree-receipt.stdout`, `run3.stderr`
- `scripts/analyze_receipt.py`, `scripts/consistency.py`, `scripts/battery.py`, `scripts/battery_candidate.py`, `scripts/raw_check.py`, `scripts/log_check.py`

Scratch (heavy, `/fast/scratch/hyaku/kama-r25a2w2/RerunC2Counter/`, not in the lane): materialized receipts (`receipt-fa3b62ae.json`, `receipt-5ea4fc44.json`), the same counter copies, `mutants/` (33 receipts), `committed-raw/` (70 files extracted from fa3b62ae), `attack-receipts/` (45 files extracted from fa3b62ae), the scripts, and stdout and stderr logs.

Report: `.ufo/waves/round-25/a2-falsify/advice/RerunC2Counter.md`.
