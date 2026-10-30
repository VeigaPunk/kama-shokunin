# MT25RefFilesBypass: C1 `bind_ref_files` falsification (round 64, wave f, operability)

Seat: MT25RefFilesBypass (leaf; no subagent dispatch). Tip under test: 23b3fdb1a925129a9961cf551f6d40bf251602cb
(counter sha256 `1ffea590bcb4a2db3e1183221ebe1f2dd9841f4811c9bcd54de80f2484b817d9`, AMENDMENT 1a/1b;
tool byte-identical to the freeze commit). Scratch root
`/fast/scratch/hyaku/kama-r64/f/MT25RefFilesBypass/` (removed after archiving). Out dir:
`.ufo/waves/round-64/f/out/MT25RefFilesBypass/`.

## 1. Verdict summary

Forgeries were driven through the counter's own live path. Two channels: (i) a harness that imports
`tools/round64-c1-counter.py` by path and calls its `reference_run` / `witness_run` / `collect` /
`score_run` (the counter's own grading code, no re-implementation); (ii) the unmutated counter run
end-to-end at a committed forged tip in the scratch clone (forged tool only; the counter file
untouched; forge-A/forge-B dry-runs verified to apply without fuzz on the hooked text first, so
`families_exact=1` held in every accepted run). Model forgeries used a private HOME copy of the
fixture (byte-identical, pinned sha verified before every run); the shared fixture was never
written (sha re-verified after all runs).

| # | attack | verdict | deciding check / observation |
|---|---|---|---|
| a | honest-run false-fail rate, 70 tool runs (30 idle, 20 under 28-way CPU load, 20 with a second pinned server already running) | **0/70 `bind_ref_files` failures** | ref/child/raw_b file sets 24==24==24 in every run; the 6 honest non-mets are `bind_holders` flakes, not this check |
| b | lazy mappings: reference server (3 requests) vs held child (~10 requests) | no divergence (0/70) | set constant 24 from process start through every request type (lazy_probe); libgomp mapped in both; no locale-archive/libnss in either |
| c1 | in-place neutral rewrite of the mapped model during the hold, restored before exit | **SURVIVED** (`met=True`, 91/91) | sha of the model on disk during the hold `267e752756f7…` ≠ pin `270cba1bd510…`; nothing hashes the mapped model during the hold |
| c2 | same, left in place | KILLED | `["bind_argv", "inconsistent:model_digest", "model_digest"]` — the post-run *path* digest; `bind_ref_files` irrelevant (identity unchanged) |
| c3 | weight-region rewrite (4 KiB) during the hold, restored | KILLED | `["live_ref_text"]` — answer probes; no mapping check sees content |
| c4 | weight-region rewrite immediately after release (after raw_a, raw_b, probes), restored before exit | **SURVIVED** (`met=True`, 91/91) | model bytes hashed only after the run; nothing grades them in the (release, exit) window |
| c5 | reflink swap: same bytes, new inode at the model path before the child starts | KILLED | `["bind_ref_files"]` — the amendment's clean kill (MT06 a4 reproduced at the tip) |
| c6 | hardlink of the same inode | met=True | identity and content identical — nothing to detect; no check fires (expected, not a forgery) |
| c7 | bind mount of the model onto itself inside a private mount ns | KILLED | `["bind_env", "bind_ns"]` — AMENDMENT 1's ns check kills mount tricks before `bind_ref_files` is consulted (`bind_env` here is a wrapper artifact: /bin/sh adds PWD/SHLVL to the child environ) |
| d0 | forged tool dlopens `libllama-cli-impl.so` into the held child before raw_a (delay 0 ms and 300 ms) | KILLED | `["bind_ref_files"]` both times — the check has teeth at its snapshot |
| d1 | **same dlopen injected strictly between raw_a and raw_b (delay 600 ms)** | **SURVIVED** (`met=True`, 91/91) | raw_b contained the extra mapping (25 vs reference 24); no check compares raw_b's file set; `bind_stable` signature (pid, start_ticks, exe_sha256) unchanged |
| d2 | same dlopen injected after raw_b (delay 1200 ms) | **SURVIVED** (`met=True`, 91/91) | invisible in both snapshots |

Tally: SURVIVED 4 (c1, c4, d1, d2), KILLED 6 (c2, c3, c5, c7, d0×2), no-op 2 (c6, plus b's none).

## 2. (a) honest-run false-fail rate of `bind_ref_files`

70 harness runs of the genuine tip tool (the harness imports the counter by path and drives its own
`reference_run`/`witness_run`/`collect`/`score_run`): 30 idle, 20 with 28 CPU burners, 20 with a
second pinned llama-server already running (my own, on a free loopback port).

- `bind_ref_files` failures: **0/70**. Reference set, child raw_a set and raw_b set were the same
  24 (path, dev, inode) triples in every run; `ref_eq_a`, `ref_eq_b`, `a_eq_b` true in 70/70.
- met: 64/70 (28/30 idle, 18/20 load, 18/20 second-server). All 6 failures were `bind_holders`
  with holder_pids == {hold_pid} (the genuine child alone) — the failure came from
  `unreadable_own`: unrelated processes created after the tool started whose `/proc/<pid>/fd`
  raises EACCES (measured live: 7,732 of 7,740 kthread-like pids on this host are EACCES; the
  observed offenders were on-demand `xfs-conv` kworkers on /fast, plus a 26-pid burst of
  foreign-uid pids in one run). AMENDMENT 1's rule "unreadable fd tables of ANY uid graded when
  the process started after the tool" fails `bind_holders` closed on those.
- Full honest counter runs at the tip: 3 → 2× `met=True` (91/91), 1× `met=False`
  `error: live: ["bind_holders"]` (host under my concurrent falsification load). No honest run
  ever failed on `bind_ref_files`.

## 3. (b) lazy mappings

`lazy_probe.py`: pinned server started with the counter's own flags/env; file-backed set
snapshotted after start, after /health, /v1/models, /props, /v1/completions, /tokenize, the second
completion, the malformed request, and after each of the counter's three reference probes.
Result: the set was 24 at every one of the 33 snapshots across 3 rounds; zero additions/removals.
In the 70 harness runs the reference server (3 requests) and the held child (~10 requests) had
identical 24-entry sets. The 24 entries: /etc/ld.so.cache, the model (stories260K.gguf), 9 pinned
llama libs + the exe, and 12 /usr/lib libs including `libgomp.so.1.0.0`; no locale-archive, no
libnss in either process. Conclusion: no request-induced lazy mapping exists on this host, so the
strict set equality held in every honest run — the equality is safe here but is a latent
false-fail risk on any host where a request loads a file.

## 4. (c) content forgeries that keep identical (path, dev, inode)

Mechanism (tip counter): `read_maps()` hashes only files under the server dir; `maps_ok()` skips
the model mapping (`real == mp → continue`); the model's content is graded only post-run via the
path digest (`bind_argv` `sha256_path(mp) == MODEL_SHA`, `model_digest`). AMENDMENT 1a's sentence
"the model digest in maps is hashed fresh (no cache)" is therefore implemented as a post-run path
hash — nothing binds the mapped model's *bytes* during the hold. Neutral target: GGUF alignment
padding at [14152,14176) (between tensor-info end and tensor data start), never read for
inference; weight target: 4 KiB at offset 16176 (inside `token_embd.weight`).

- c1 (neutral, restored before exit): **met=True, 91/91.** Evidence json: `sha_in_hold =
  267e752756f7…` vs pin `270cba1bd510…`; `ref_eq_a/ref_eq_b/a_eq_b` all true; probe answers equal
  the reference's. The child answered the graded probes while the pinned path held non-pinned
  bytes, and no check observed it.
- c2 (neutral, persistent): met=False via the post-run path digest — i.e. only because the forger
  forgot to restore; `bind_ref_files` contributes nothing (identity unchanged).
- c3 (weights, restored): met=False via `live_ref_text` only — content divergence is caught, when
  it is caught, by the two answer probes, not by any mapping check.
- c4 (weights, corrupted immediately after release, restored before exit): **met=True, 91/91.**
  After release there is no probe, no snapshot and no digest until after the tool exits; the
  restore then makes the post-run hash pass. The held child spent the end of its life serving from
  corrupted mapped weights with zero counter observability.
- c5 (reflink swap, same bytes new inode): met=False via `bind_ref_files` — the check's real value
  is identity, and it fires exactly here.
- c6/c7: see table.

## 5. (d) forged tool maps extra files AFTER raw_a

Measured window (5 dlopen runs): hold.json → raw_a ≈ 393–469 ms; raw_a → raw_b ≈ 361–472 ms.
The forged hook sleeps N ms after writing hold.json, then ptrace-injects `dlopen` of the pinned
but never-loaded `libllama-cli-impl.so` into the child (injector adapted from the MT06 forger diff,
archived; parent→child tracing is allowed under Yama scope 1) and detaches before raw_b.

| delay | injection position | verdict | counter line (abridged) |
|---|---|---|---|
| 0 ms | before raw_a | KILLED | `live_ok=0/1 … met=False`, `error: live: ["bind_ref_files"]` |
| 300 ms | before raw_a | KILLED | same as above |
| 600 ms | **strictly between raw_a and raw_b** | **SURVIVED** | full line in §7, `met=True`, 91/91 |
| 1200 ms | after raw_b | SURVIVED | `met=True`, 91/91 |

Harness snapshot for the 600 ms case: raw_a = 24 mappings == reference set; raw_b = 25 mappings
(`b_minus_a = ['/home/vgpnk/.local/opt/llama-b11755/libllama-cli-impl.so']`); holders_signature
`(pid, start_ticks, exe_sha256)` identical across snapshots; `fails = []`. Mechanism: `score()`
grades `bind_ref_files` from **raw_a holders only** (`hs_a = (raw_a or {}).get('holders')`);
`grade_binding(raw_b)` contributes only `bind_state` and `bind_trace`; `bind_stable` compares
`(pid, start_ticks, exe_sha256)` — maps are not in the signature. The counter's own second
snapshot *contained* the divergent mapping and no check consumed it. The answer to the seat's
question is: no — `raw_b`'s `bind_stable` does not catch it, and neither does anything else.

## 6. Reading of the amended claim

`bind_ref_files` does what AMENDMENT 1a says (identity equality against the reference server's
set, and it kills same-bytes/new-inode swaps and pre-snapshot dlopen), but it is a one-shot
snapshot at raw_a and an identity-only check:
1. the raw_a→raw_b window is unguarded for mappings — a live, answering child may carry extra
   mapped code for the whole second half of the hold and the full counter still prints met=True;
2. the model's mapped content has no in-hold binding at all — a same-inode rewrite restored
   before exit passes the entire instrument, and a corruption in the post-release window is
   equally invisible;
3. honest-run flakiness sits in `bind_holders` (unreadable foreign/kthread fd tables created
   after tool start), not in the new check.
Advisory only (no edits made): grade the file set on both snapshots or fold maps into
`bind_stable`; state plainly that the model binding is post-run-digest + answer-probe only;
consider grading `unreadable_own` only for pids that could hold the port.

## 7. Counter outputs at the forged tip (unmutated counter, clone commit 4b654a828995dd401d1dc42951a6419732734e26)

- D_gap600 (SURVIVED): `tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 missing_families=[] eval_selftest=8/8 errors=0 met=True families[bind=30/30 … witness=5/5]`
- C1_neutral_restore (SURVIVED): same line, `met=True`.
- C2_neutral_persist (KILLED): `live_ok=0/1 … errors=1 met=False`, `error: live: ["bind_argv", "inconsistent:model_digest", "model_digest"]`
- C3_weight_hold_restore (KILLED): `live_ok=0/1 … met=False`, `error: live: ["live_ref_text"]`
- C4_native_reflink (KILLED): `live_ok=0/1 … met=False`, `error: live: ["bind_ref_files"]`
- C5_native_hardlink: `met=True` (identity+content identical; nothing to detect).
- C6_weight_post_release (SURVIVED): `met=True`, 91/91.

## 8. Procedure, tools, integrity

- Clone per recipe; every counter run with a fresh `--work`; counter invoked from `$D/tools`.
- Forged tool committed only in the scratch clone (tips 677d794a…, 4b654a82… = empty commit on
  top); the counter file never modified (sha verified equal to the tip blob before and after).
- Live servers: counter/harness-owned on free loopback ports; all torn down; 0 processes of mine
  left (checked at the end); ports 8080/34113 untouched; no foreign process killed.
- Shared fixture `~/.cache/kama-shokunin/models/stories260K.gguf` never written; sha `270cba1b…`
  re-verified after all runs. Private model copy under the scratch HOME.
- No tools installed or upgraded (python3, git, cp/unshare/ln, patch, nm already present); no
  pacman transactions.

## 9. Archive

`.ufo/waves/round-64/f/out/MT25RefFilesBypass/`:
`honest/` (honest30/load20/second20 json+logs, lazy.json, counter/{r1,r2,r3}+rcs),
`variants/` (12 harness runs: harness.json/log + evidence.json each),
`counter/` (7 official runs: stdout/stderr/evidence + summary.json),
`tools/` (harness, lazy_probe, mkforge, run_variants, run_counter_variants, analyse),
`forged-tool.diff` (204 lines, hook insertion + MT06-derived injector).

Last line (the counter one-liner for the headline forgery, D_gap600 at the forged tip):

`tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 missing_families=[] eval_selftest=8/8 errors=0 met=True families[bind=30/30 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 receiptbind=4/4 relabel=1/1 replay=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]`
