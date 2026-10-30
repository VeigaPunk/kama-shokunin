# MT30AdaptiveForgeProc — C1 adaptive forger (process level), round 64 wave f

**Item attacked.** The cheapest forged tool that makes `tools/round64-c1-counter.py`
print `met=True` at tip `23b3fdb1a925129a9961cf551f6d40bf251602cb` **without a pinned
llama-server answering the counter's probes and the tool's request**.

**Verdict in one line.** No forgery of the *answering process* survives the amended
counter (two independent barriers, F1 and F2 below). One forgery of the *holder
uniqueness* clause **SURVIVES**: a forged tool that hands a duplicate of the run-port
LISTEN socket to a pre-existing, non-dumpable helper is scored `met=True` (3 runs of 3).

## Method (all inside my scratch; the lane was only read)

* Clone per the recipe: `/fast/scratch/hyaku/kama-r64/f/MT30AdaptiveForgeProc/clone`
  (`git clone --shared` of the lane), checked out at `23b3fdb1a925129a9961cf551f6d40bf251602cb`.
* Every forgery replaces `tools/kama-completion-live.py` **in the clone only**; the
  counter is never touched — its sha256 in the clone is byte-identical to the tip's
  (`1ffea590bcb4a2db3e1183221ebe1f2dd9841f4811c9bcd54de80f2484b817d9`).
* Scoring: `git add -A; git -c user.name=seat … commit -m wip`; `T=$(git rev-parse HEAD)`;
  `python3 tools/round64-c1-counter.py --repo $D --tip $T --work $S/work-<label>` with a
  fresh `--work` each time (the counter refuses a reused one).
* Baseline control (unmutated tip): **met=True, 91/91, 8/8** (`receipts/base.out`).

## Results

| # | forgery | mechanism (one line) | verdict |
|---|---------|----------------------|---------|
| F1 | `forged-f1-forwarder.py` | real pinned server moved to a private port; a **python forwarder** takes the advertised run port and relays the counter's probes to it | **KILLED** |
| F2 | `forged-f2-canned.py` | **no inference engine at all**: a python HTTP server emits llama.cpp-shaped JSON on the run port | **KILLED** |
| F3 | `forged-f3-fdleak.py` | the genuine tool, plus: the child's run-port LISTEN socket is duplicated (`pidfd_getfd`) and handed to a **pre-existing, non-dumpable helper** over `SCM_RIGHTS` | **SURVIVED** |

Diffs: `out/MT30AdaptiveForgeProc/receipts/diff-f{1,1b,2,2b,3,3b,3c}.patch`
(per-run copies; `diff-f1.patch` is F1, `diff-f2.patch` F2, `diff-f3c.patch` the final F3).

### F1 — the answering process is a forwarder — KILLED

F1 is the sharpest attack on the claim's wording: the *answers* are genuine (a real
pinned llama-server answers on a private port and the forwarder relays them byte for
byte), so every answer-agreement check **passes**; only the process binding fails.

```
tool_present=1 live_ok=0/1 controls_targeted=0/0 of 91 families_exact=0 missing_families=[…] eval_selftest=0/8 errors=1 met=False families[]
error: live: ["bind_argv", "bind_exe", "bind_maps", "bind_ref_files", "listener_holders_pinned", "verdict"]
```

Second run (same forgery) added one host-churn failure:

```
error: live: ["bind_argv", "bind_exe", "bind_holders", "bind_maps", "bind_ref_files", "listener_holders_pinned", "verdict"]
```

`bind_holders` fails only when `unreadable_own` is non-empty — a process that started
after the tool and whose fd table was unreadable at the four re-reads AMENDMENT 1b
allows. With ~40 seats running live servers that is the known flake class, not a
property of the forgery (the baseline and all three F3 runs passed `bind_holders`).

**Which observation saw it:** `bind_exe` (the holder's `/proc/<pid>/exe` is the python
interpreter, not the pinned server), `bind_argv`, `bind_maps`, `bind_ref_files` (the
holder's mapped-file set is not the reference server's), plus the tool's own
`listener_holders_pinned`. **Which observation did not see it:** none of the answer
checks — `live_ref_text`, `live_ref_usage`, `receipt_ref_text`, `receipt_ref_usage`
all passed, because the answers were real. The binding, not the answer agreement, is
what binds the process.

### F2 — no inference engine at all — KILLED

Two independent barriers bite at once: the process binding **and** the reference
agreement.

```
error: live: ["bind_argv", "bind_exe", "bind_maps", "bind_ref_files",
               "listener_holders_pinned", "live_ref_text", "live_ref_usage",
               "receipt_ref_text", "receipt_ref_usage", "verdict"]
```

(reproduced identically in two runs). The canned server is shape-perfect: after fixing
my own two shape bugs (`/health` body `{"status":"ok"}` byte-exact, fingerprint
`b1-c0ffee1234`), `health_ready`, `completion_fingerprint`, `live_fp_shape`,
`completion_envelope`, `completion_usage`, `completion_timings`,
`completion_prompt_tokens`, `bad_request_graded`, `models_alias_id`, `props_alias`,
`teardown_*` all pass — only the *content* comparison with the counter's own reference
server fails, plus the holder binding.

**Which observation saw it:** `live_ref_text`/`live_ref_usage` (the counter's answer
must equal the reference server's text and token counts for a prompt drawn at random
per run — a canned answerer cannot know them) and `bind_exe`/`bind_argv`/`bind_maps`/
`bind_ref_files`.

### F3 — a second, invisible holder of the run-port listener — SURVIVED

Mechanism (cheapest possible, no engine, no substitute):

1. The tool starts the genuine pinned server exactly as the tip tool does.
2. After the server is ready, the tool picks the child's fd whose `/proc/<pid>/fd`
   link is `socket:[inode]` with that inode among the run port's LISTEN inodes, and
   duplicates it with `pidfd_getfd` (syscall 438 on x86-64; `/proc/<pid>/fd` cannot be
   opened for a socket — ENXIO).
3. The duplicate is passed over a unix socket (`SCM_RIGHTS`) to a helper that was
   started **before** the counter run and has called `prctl(PR_SET_DUMPABLE, 0)`, so
   its `/proc/<pid>/fd` is root-owned and unreadable by the counter's own-uid scan.
4. The helper never accepts on the socket (so the answers still come from the pinned
   server) and closes the duplicate after the server's pid disappears, so the port
   still closes for the counter's teardown observation.

Result — **three runs of three, `met=True`** (f3, f3b, f3c):

```
tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 missing_families=[] eval_selftest=8/8 errors=0 met=True families[bind=30/30 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 receiptbind=4/4 relabel=1/1 replay=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
```

(verbatim line in `receipts/out-f3c.txt`; the two earlier F3 runs, `out-f3.txt` and
`out-f3b.txt`, are byte-identical.)

Proof that the helper really held the run-port listener during the live contact —
helper log of the f3c run (`receipts/helper-f3c.log`):

```
1793357850.199 helper-ready
1793357851.552 helper-got fd=5 link=socket:[2227025361] server_pid=1399893 listening_inodes=[('8CA5', '0A')]
1793357853.324 helper-closed
```

`0x8CA5 = 36005` is the tool's run port in that run (`receipt.json: port 36005`,
`child_pid 1399893` = the pinned server), and `0A` is `TCP_LISTEN`. The helper held
that socket for 1.77 s, spanning the counter's `collect()` snapshot, its two outside
probes and its teardown observation.

**Which observation failed to see it:** `unreadable_old`. The counter's
`collect()` splits unreadable fd tables into `unreadable_own` (graded: fails
`bind_holders`) and `unreadable_old` (recorded, never graded). A holder that started
before the tool is by construction in `unreadable_old`, so "every holder of the
run-port listener is the hold pid" was **false** during the live contact and the
counter still printed `met=True`.

This is a re-verification of a limit the freeze already discloses ("a non-dumpable
own-uid helper that existed before the tool and holds a duplicate of the listener
(unreadable_old is recorded, never graded; MT01 O3/O4, MT08 f2)"), not a new hole; the
mechanism above is a concrete, ~40-line recipe for it. Scope of the violation: the
*holder-uniqueness* clause of the C1 sentence, not the substance — in F3 the answers
still came from the pinned server.

## Why "met=True with no pinned llama-server answering" is not reachable here

Two counter properties, each independently fatal to an answer substitution, and each
verified by a forgery above rather than argued only:

1. **Answer agreement** (`live_ref_text`, `live_ref_usage`, `receipt_ref_text`,
   `receipt_ref_usage`): the counter draws three requests per run (random word
   sequences, random `n_predict`, random seed, per-run nonce), starts its own pinned
   reference server and requires the held child's text and token counts to equal the
   reference's. F2 shows a shape-perfect canned answerer is rejected on exactly this.
2. **Process binding** (`bind_exe`, `bind_argv`, `bind_env`, `bind_ns`, `bind_trace`,
   `bind_state`, `bind_maps`, `bind_ref_files`, `bind_ancestry`, `hold_fresh`,
   `bind_holders`): the run-port listener's holder must be a process whose
   `/proc/<pid>/exe` re-hashes to the pinned digest at the counter's chosen path, whose
   argv is exactly the tool's argv, whose mapped-file set equals the counter's own
   reference server's, which shares the counter's namespaces, is untraced, is not
   stopped, is a descendant of the tool and started after it. That is the pinned
   llama-server itself, so any holder substitution (F1) dies here even when its
   answers are perfect.

F1 is the decisive datum: with every answer check green, the substitution still fails
on `bind_exe`/`bind_argv`/`bind_maps`/`bind_ref_files`. The claim's sentence binds the
*process*, and the process binding is what enforces it.

Residual, not attempted and marked **[INFERENCE]**: a forger that reads the counter's
own memory could recover the drawn prompts (they carry a per-run nonce and are
contiguous strings), but not the reference *answers* nor `n_predict`/`seed`, and even a
forger that recomputed them would still have to satisfy clause 2, which pins the
answering process to the pinned server.

## Coverage notes (observations the counter does not make)

* The counter grades the **listener's holders**, never the **acceptor**: nothing ties
  the connection the counter's probe opened to the pid it bound. A holder that accepts
  would have to produce model-correct answers to survive clause 1, so it is not a
  cheap route — but the acceptor is ungraded, and F3 shows extra holders are possible.
* The receipt's `model.path` is graded by digest only (`model_digest` re-hashes the
  path the receipt names), so a forged tool may name any path holding the pinned
  bytes; "the pinned fixture" is a digest claim in the receipt, not a path claim.
* The fixture digests are re-hashed at collect time (`bind_argv` re-hashes the model,
  `bind_exe` the server), which closes the obvious "swap the fixture bytes mid-run"
  route: the bytes would have to be the patched ones for the reference server's load
  and the pinned ones again at both collect snapshots. **[INFERENCE]** — not attempted.
* The counter's control construction is *source-sensitive*: a forged tool that edits
  the regions the committed round-63 forge patches touch makes `forge_variants` fail
  ("dry-run failed or fuzzed"), and the counter then reports `forge=0/3`,
  `errors=1`, `met=False`. My first F3 attempt was killed this way; moving the edit
  above the patched hunk restored 91/91. Worth knowing before scoring a patched tool.

## Reproduction

```
S=/fast/scratch/hyaku/kama-r64/f/MT30AdaptiveForgeProc; O=<lane>/.ufo/waves/round-64/f/out/MT30AdaptiveForgeProc
mkdir -p $S
python3 $O/build_forgeries.py $O/base-tool.py $O $S/helper.sock      # rebuilds F1/F2/F3
bash $O/score.sh $O/forged-f3-fdleak.py f3c $O/helper-holder.py      # -> met=True
```

`$O/base-tool.py` is the tip's `tools/kama-completion-live.py` verbatim
(`git show 23b3fdb1a925129a9961cf551f6d40bf251602cb:tools/kama-completion-live.py`).

## Files

* `out/MT30AdaptiveForgeProc/build_forgeries.py` — the builder (string-anchored,
  reproducible patches of the tip tool).
* `out/MT30AdaptiveForgeProc/base-tool.py` — the tip's tool, verbatim (input to the builder).
* `out/MT30AdaptiveForgeProc/forged-f{1-forwarder,2-canned,3-fdleak}.py` — the forged tools.
* `out/MT30AdaptiveForgeProc/helper-holder.py` — the pre-existing non-dumpable holder.
* `out/MT30AdaptiveForgeProc/score.sh` — the scoring harness (clone-only).
* `out/MT30AdaptiveForgeProc/receipts/` — counter stdout/stderr per run, helper logs,
  diffs, the baseline receipt.

## Compliance

* Lane read-only; all writes in my scratch clone, my out dir and this report. No
  commit, push or mutating git in the lane; no `git add` there. No jj operation.
* No pacman / uv / npx transaction, no package installed or upgraded: the base
  python3 (3.14), git and patch sufficed. Nothing was written to any PATH directory.
* Only processes I started were killed (the helper, my counter runs' children). No
  port was touched other than the loopback ports the counter and my forgeries picked;
  8080/34113 were never used.
* The scratch root was removed after the receipts were copied into the out dir.

## One-line counter output for this item (F3, the surviving forgery)

```
tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 missing_families=[] eval_selftest=8/8 errors=0 met=True families[bind=30/30 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 receiptbind=4/4 relabel=1/1 replay=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
```
