# MT09ReceiptTamper — round 64 wave b, C1 receipt/tool tamper (advisory seat)

Tip under test: `f6a4ea9a8b5a876d685b08e7e582ec0723412a4a` (freeze). Counter: `tools/round64-c1-counter.py`, unmodified, scored from my scratch clone. Every mutant is a patch to the **tool** (`tools/kama-completion-live.py`), committed in the clone, scored by the unmodified counter with a fresh `--work`. Receipt-level mutants edit the receipt the tool writes at `main()` after its genuine run, so the live process is never touched by my edits.

Evidence: `.ufo/waves/round-64/b/out/MT09ReceiptTamper/` (patches, all stdout/stderr, receipts, runner scripts, diagnostic counter copy).

## Verdict in one screen

- **SURVIVED, forgery (high):** T04b. The tool rewrites the captured fixed-prompt completion to `' FORGED TEXT'` (both `completion` and `completion2`, with body sha, byte count and `content-length` resealed). Counter: met=True. Nothing live asks the held server the captured request; the counter's only live contact is two random probes.
- **SURVIVED, identity attribution (low-medium):** T03b. The tool gets its captures from pinned child A, then kills A and relaunches pinned server B on the same port, and records B as child and listener holder. Counter: met=True. Both processes are the pinned binary; the forgery is which one produced the captured bytes.
- **SURVIVED, not a forgery:** M02 (reordering the holder list of one holder is an identity edit; the counter compares sorted content) and T01 (`hold.json` `holders` emptied; the counter never reads that field, so it is decorative).
- **KILLED:** M01, M03, M03b, M04a, M04b, M05a, M05b, M06a, M06b, T05, T06. T02 is a true fabrication: the live binding accepted it (live_ok=1/1), and the overall met=False comes from the forge fixture anchor, not from the holder check.
- **Counter operability defect found while scoring:** reusing a `--work` directory makes 7 of the 76 controls fail (`tool exited before hold.json`), and the summary line still prints `errors=0`. Confirmed on the unmodified baseline. Details under O1.

## Baseline (unmutated, fresh `--work`)

```
tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
```
Baseline reproduced in a second fresh directory (`baseline-rerun`). Exit 0.

Command used: `cd $S && python3 $D/tools/round64-c1-counter.py --repo $D --tip $T --work $S/w-<name>` with `D` the clone, `T` the mutant commit, `S` the scratch root.

## Receipt-level mutants (edit the receipt the tool writes)

Killed lines are shown with the `missing_families` list elided as `[…]` (all 28 families missing when live fails); the full line is in `out/outputs/<name>.out`. `live:` is the counter's own failing-check set (stderr).

| ID | Edit to the receipt | Verdict | Check(s) that named it (stderr `live:`) | Procfs observation that decides it |
|---|---|---|---|---|
| M01 | drop `listener_holders` | KILLED | `bind_claim`, `listener_holders_pinned`, `inconsistent:listener_holders_pinned` | counter's own holder snapshot (one pinned holder) vs. empty receipt list |
| M02 | reverse the holder list (1 entry) | SURVIVED, equivalent | none, `met=True` | none needed: identity edit, counter compares sorted `(pid,exe,sha)` |
| M03 | append holder `{pid:1, exe:pinned, sha:pinned}` | KILLED | `bind_claim`, `listener_holders_pinned`, `inconsistent:listener_holders_pinned` | holder set from `/proc/net/tcp*` inode → `/proc/<pid>/fd`: {child} only |
| M03b | duplicate the child entry (len 2) | KILLED | same as M03 | same |
| M04a | holder `exe` = `~/.local/bin/llama-server` (symlink spelling), `server.path` canonical | KILLED | `bind_claim`, `listener_holders_pinned` | `/proc/<pid>/exe` readlink is the canonical path; the symlink string can never equal it |
| M04b | holder `exe` **and** `server.path` both the symlink spelling | KILLED | `bind_claim` only | same as M04a. The receipt is internally consistent (`listener_holders_pinned` and `server_digest` both pass), so only the procfs comparison catches it |
| M05a | holder `pid` +1 | KILLED | `bind_claim`, `listener_holders_pinned`, `inconsistent:listener_holders_pinned` (run 2; run 1 also `bind_holders`, see O2) | counter's raw holder pid vs. receipt pid |
| M05b | holder `pid` +1 and `child_pid` +1 (self-consistent) | KILLED | `bind_claim`, `live_pid` | raw holder pid vs. receipt; `live_pid` = hold.json pid (tool-written) vs. receipt child |
| M06a | holder `exe_sha256` upper-case | KILLED | `bind_claim`, `listener_holders_pinned`, `inconsistent:listener_holders_pinned` | counter's own sha is lowercase hexdigest; string inequality |
| M06b | holder sha and `server.sha256` upper-case | KILLED | `bind_claim`, `listener_holders_pinned`, `server_digest`, `live_server_sha`, `inconsistent:*` | same, plus the server digest check |

Full met lines for the killed rows follow the template `tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 missing_families=[…] eval_selftest=0/3 errors=1 met=False families[]`; e.g. M04b:
`tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 missing_families=[…] eval_selftest=0/3 errors=1 met=False families[]` with `error: live: ["bind_claim"]`.

## Tool-level mutants (the tool itself lies or races)

| ID | Edit to the tool | Verdict | Named by | Notes |
|---|---|---|---|---|
| T01 | hold.json `'holders': holders` → `'holders': []` | SURVIVED, dead field | none | `met=True 76/76`. The counter never reads `hold.json` `holders` (only `pid`, `port`, `schema`, mtime). The freeze lists it as part of the v3 binding. |
| T02 | `holders = _proc_holders(port)` → `holders = [{child, pinned exe, pinned sha}]` (a true claim) | not a binding kill | none; `live_ok=1/1` | Live binding accepted the true claim (correct). The line `met=False` comes from `families[forge=1/3]`: forgeA2/forgeB2 are built by textual replacement of `holders = _proc_holders(port)` and were not applied (`error: forge forgeA2: patch did not apply to the tip tool`). See O3. |
| T03 | (first, untraced) after captures: SIGKILL child, relaunch pinned server on the same port, make it the child and listener holder | SURVIVED, see T03b | none | `met=True 76/76` in a fresh directory. |
| T03b | same as T03, plus `receipt['_mutant_first_child_pid'] = <first pid>` | SURVIVED (forgery, identity) | none; `live_ok=1/1`, 76/76, errors=0, met=True in a fresh dir (run twice) | Fresh receipt: captures producer pid **2717368**, receipt `child_pid` and listener holder **2718131**, both `/home/.../llama-b11755/llama-server`, teardown observed. Holder argv, maps, environ and ancestry all pinned and correct. |
| T04 | rewrite captured completion texts, reseal sha/bytes only | KILLED (incidental) | `completion_untruncated` | Stale `content-length` header; the counter's own check (correct). Fixed in T04b. |
| T04b | rewrite `completion` and `completion2` text to `' FORGED TEXT'`; reseal sha, bytes and `content-length` | SURVIVED (forgery, captured bytes) | none; `live_ok=1/1`, 76/76, errors=0, met=True in a fresh dir (run twice) | Fresh receipt verdict `REQUEST_OK`, text `' FORGED TEXT'`. The genuine answer to the same request (baseline receipt, same model/seed) is `' ground. She liked'`. No counter check asks the held server this prompt. |
| T05 | `holders = _proc_holders(port)` → `raise OSError` | KILLED, fail-closed | `live: no receipt/witness ['tool exited before hold.json']` | Setup-error path returns before hold.json; the counter refuses. |
| T06 | after the holder check (before hold.json): swap to a second pinned server, receipt left stale (`child_pid`, holder list unchanged) | KILLED | `bind_claim`, `live_pid` | The tool does not notice; the counter's hold-time snapshot does. |

Full met lines for the two survivors (fresh directories; `out/outputs/fresh-T03b_stitch_recorded.out`, `fresh-T04b_captures_rewritten_clen.out`):
`tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]`

## What decides each survivor (procfs, or its absence)

- **T04b:** no procfs observation of any kind. The counter's live contact is two random-prompt probes (`probe_fails`, `live_ref_text`); the captured `completion`/`completion2` bytes are only re-hashed and checked for internal shape. The counter's own kill rule ("a receipt the counter accepts without its own live contact") is met under a strict reading: the receipt's fixed-prompt answer was never contacted.
- **T03b:** the procfs snapshot at hold time sees exactly what a pinned server looks like (exe/sha, argv, environ, maps, ancestry to the tool, start ticks after the tool). The first child is dead by then, so the observation that would distinguish it is absent. Any counter-side replay on B returns A's text (same model, temp 0, same seed), so a replay alone does not kill this mutant.

## Tool diff review — `git diff 0c1eff3c f6a4ea9a -- tools/kama-completion-live.py`

- **D1 race (holder snapshot vs hold window).** `_proc_holders` runs once at line ~521 and the same list goes into the receipt and hold.json (line ~542). Nothing re-checks the listener between that and hold.json or during the hold. The counter's own snapshot at hold time is the only live binding. Consequences: a post-check swap is caught only by the counter (T06 killed, the tool does not notice). Worse, nothing binds the captured bytes to a pid: `listener_owned` is checked once at first answer (line ~364), the captures are taken afterwards, and no capture records which process answered it. That gap is exactly T03b (and T04b on the content side).
- **D2 fail-open enumeration.** `_proc_holders` skips any fd table it cannot read (`except OSError: continue` around `/proc/<pid>/fd` and `readlink`) and records no unreadable marker. The counter fails closed on unreadable own-uid fd tables that appeared after the tool started (`unreadable_own`), but not on older ones. So the tool can certify `holders=[child]` while a hidden holder exists. [INFERENCE] Not run; the first-answer gate and free-port selection make a pre-existing hidden holder of the same port unlikely.
- **D3 hold.json `holders` is dead data.** Written at line ~542, never graded (T01 survived). Either bind it to the counter's snapshot or drop it; the freeze's fix list names it.
- **D4 setup-error paths.** T05 (raise before holders) is killed fail-closed. Not run [INFERENCE]: if `_live.hold_for_witness` raises after hold.json is written, the outer `except` kills the child and returns SETUP_ERROR, but `os.unlink(hold.json)` sits after the call and is skipped, leaving a stale hold.json with a dead pid. The counter's witness loop breaks on tool exit, and the pid/ancestry/fresh checks would then fail closed, so this is hygiene, not a bypass.
- **D5 minor.** `finally: pass` is a no-op; `log_f` is not closed on early returns. No effect on the verdict.

## Counter defects found while scoring (operability)

- **O1 reused `--work` breaks 7 controls, summary says `errors=0`.** Unmutated baseline, same `--work` twice: run 1 `met=True 76/76`; run 2 `met=False`, `controls_targeted=69/76 families_exact=0 errors=0`, stderr `error: fake {detach,proxy,canned,stale_old,stale_future,preload,pathcopy}: no receipt/witness ['tool exited before hold.json']` (7 lines). Cause: the counter's teardown writes `release` into each witness hold dir; a second run in the same `--work` reuses `fake-*/hold/release`, and the fake tools do not call `prepare_witness_dir`, so they exit before the counter reads hold.json. The live tool does call it, which is why the live row still passes. This also explains the "repeat" failures of T03b/T04b, which I first misread as mutant effects; fresh-directory runs of the same commits gave `met=True`. A diagnostic copy with fake stderr captured (`outputs/counter-diag-stderr-capture.py`, not committed) reproduced `met=True` on a fresh dir. The `met` line also reports `errors=0` when fake witnesses fail, since they land in `detail`, not `errors`.
- **O2 one-off flake on the live binding.** M05a first execution: `error: live: ["bind_claim", "bind_holders", "inconsistent:listener_holders_pinned", "listener_holders_pinned"]`; the extra `bind_holders` is not a property of my edit (the counter's raw snapshot does not read the receipt). Second execution (one re-run, same work dir): `["bind_claim", "inconsistent:listener_holders_pinned", "listener_holders_pinned"]`. The first stderr was overwritten by the rerun; `outputs/M05a_second-execution.*` is the second. Host load average was 30–50 at 21:19 with other seats' live servers and counters running. Cause not identified; I did not re-run it further, so this is one unexplained divergence, not a reproduced flake.
- **O3 forge fixtures are text-anchored.** `forge_variants` builds forgeA2/forgeB2 by replacing the literal `holders = _proc_holders(port)`. Any rephrase (T02) silently drops them: the forge family shows 1/3 and `met=False`, the reason only appears in `detail` on stderr. Fail-closed, but the kill is for a different reason than the binding.

## Recommendations for the L1 (not committed; any counter change is a numbered amendment before the next wave)

1. **Close T04b with a live check.** Replay the captured `completion` request (`captures.completion.request_body`, plus `completion2`) against the held pid, and require the held server's text to equal the captured text. Temperature 0 and a fixed seed make this byte-deterministic (already graded by `completion_deterministic`). This is one extra request in the counter's own reference set, not a new family. It would also cover the same content gap for any other capture the counter does not re-ask.
2. **T03b cannot be closed by counter-side replay.** A relaunched pinned server returns the same bytes. Either weaken the claim to "the captured bytes were produced by a pinned server" (what the predicate literally says) or make the tool attest per-capture pid+start_ticks, which the counter still cannot verify independently. I recommend the former with the caveat stated.
3. **Add offline controls for the holder fields.** M01/M03/M04a/M04b/M05a/M06a are killed only via the relabel control and my own edits, not one of the 76 frozen controls. Adding pid±1, sha case, symlink spelling and a second holder would make the holder-field kill rule explicit. M04b in particular is decided only by `/proc/<pid>/exe` being canonical.
4. **Fix O1.** Refuse a non-empty `--work` (as the C2 counter refuses `work-reused`) or clear the witness dirs, and make a fake-witness failure set `errors`, so the summary cannot print `errors=0` with `met=False`.
5. **Tool: D1/D3.** Re-collect holders immediately before writing hold.json and record the pid that answered each capture; bind or drop `hold.json` `holders`.

## Reproduction

```
S=/fast/scratch/hyaku/kama-r64/b/MT09ReceiptTamper; D=$S/clone
git -C $D checkout -q f6a4ea9a8b5a876d685b08e7e582ec0723412a4a
$S/mut/run.sh $S/mut/<patch>.patch      # reset, git apply --unidiff-zero --recount, commit, score (reuses w-<name>; see O1)
$S/mut/run_fresh.sh $S/mut/<patch>.patch # fresh --work per run (use this, see O1)
```
Patches are in `out/MT09ReceiptTamper/patches/` (receipt edits are the `M*` files; tool edits the `T*`). `run.sh` reuses `w-<name>` and is therefore subject to O1 on repeats; the fresh runner was used for the survivors' confirmation.

Tools installed or upgraded: none. Pacman untouched. No commits outside my clone; the lane and fleet trees were only read.

Counter one-liner (freeze tip, unmodified counter, fresh `--work`): `tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True` (full line above).
