# MT15C1FakeConsistent - C1 operability attack: canned fake request plane vs unmutated counter

Seat: MT15C1FakeConsistent (mutation tester, leaf, advisory). Target: C1-r63 (`tools/round63-c1-counter.py`).
Tip under test: 03a6a1d850902a66a13dfad33f89cf3a8b759a09. Counter file: byte-identical to 03a6 in every scored clone (`cmp` SAME).

## Verdict

**ACCEPTED - SURVIVED. C1 is falsified as the predicate is operationalized.**
The unmodified counter accepts two forged clones of `tools/kama-completion-live.py` in which every request on the run
port is answered by a canned fake. Failing check names: **none** (all 23 stored checks and all recomputed checks true;
`errors=0`; 44/44 controls and 3/3 evaluator self-test credited). The predicate's requirement that the answering listener be
the pinned llama.cpp fixture is not enforced by any check the counter runs.

Scope note on the kill rule: its literal clause "a receipt the counter accepts without its own live contact" is not what
happened - the counter did contact a listener during the hold window. The falsified leg is the predicate's "runs ... on the
pinned llama.cpp fixture ... whose listener is the receipt's child": "listener is the child" was satisfied by a socket fd,
and nothing checked that the process or the answers came from llama-server.

## Counter outputs (verbatim, unmodified `round63-c1-counter.py`, run from `$clone/tools/`)

Baseline, tip 03a6a1d (unforged tool):
```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```
Forgery A, tip 304bd5b434bcdd98895f6719cf4b3674ebcafcb0 (real llama-server child owns the run-port listener; fake answers):
```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```
Forgery B, tip 75288a23505c9d3b27a4e04979f31f0f1d2f483a (no llama-server ever runs; sleeper child owns the listener):
```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```
Each forgery line is `met=True`: SURVIVED. Commands: `python3 round63-c1-counter.py --repo $D --tip $T --work $S/work-{base,forge,sleeper}`,
with `$D` the scratch clone (toplevel asserted) and `$S=/fast/scratch/hyaku/kama-r63/w/MT15C1FakeConsistent`.

## How the counter is defeated (mechanism, all from source read at 03a6)

The counter never trusts the receipt's claims *about the process*; it trusts the tip's own code for everything else:

1. **The counter executes the tip's tool.** `witness_run` runs `tiproot/tools/kama-completion-live.py`, a blob copied from the
   tip; `load_live_mod` loads `tools/kama-llamacpp-live.py` from the same tip directory. Any forged clone supplies both.
2. **Digests bind on-disk bytes, not execution.** `model_digest`/`server_digest` hash the paths the receipt names
   (`receipt.server.path`, `receipt.model.path`). The real `~/.local/opt/llama-b11755/llama-server` and the pinned
   `stories260K.gguf` exist and hash correctly; they need not run.
3. **Listener ownership is satisfied by an inherited fd.** `port_owned_by(pid, port)` checks whether `/proc/<pid>/fd` holds a
   socket inode from the LISTEN row on `port`. A listening socket created by the forger and passed with `Popen(pass_fds=...)`
   is exactly such an fd. Verified by hand (manual run, below): fd 3 of the real child is `socket:[1776981766]`, the LISTEN
   inode for the run port.
4. **The outside witness contacts whatever listens on the hold port.** `observe()` POSTs one nonce prompt to `hold.json`'s
   port and tokenizes the same prompt on that port. A fake that tokenizes consistently, reports the captured fingerprint,
   and reports `pid == receipt.child_pid` passes every `live_*` check. `hold.json` is written by the forged tool.
5. **The 44 controls and 3-plant self-test only prove field-level rejection.** They mutate a receipt; a forged-but-internally
   consistent receipt is a valid base for each mutation, so each control is still credited. They do not test provenance.

### Forgery A (`304bd5b`): real child kept for digests and pid; fake answers the run port
- `run()` binds a listener on the run port `F` and starts the real `llama-server` on a second free port `R`, passing the
  listener fd with `pass_fds`. `wait_ready` reads the real child on `R`.
- The ownership gate (`port_owned_by(child, F)`) passes through the inherited fd.
- `_start_fake` serves `F` with a `ThreadingHTTPServer` over the same listener: `/health`, `/v1/models`, `/props`, `/tokenize`
  (proxied to the real child on `R`, so counts are the pinned server's own counts for any prompt), `/v1/completions` (canned
  text, `usage.prompt_tokens` from the real tokenizer, fingerprint from one real completion on `R`), 400 for malformed bodies.
- Teardown closes the fake's listener before SIGTERM to the child, so the port-closed check passes.
- Result: receipt `verdict=REQUEST_OK`, `child_pid=2788452` (the real llama-server), `port` = fake port, all checks passed, teardown
  `port_closed=True returncode=0`. The completion `id` is `cmpl-...` (real llama-server emits `chatcmpl-...`); the text is the
  canned `" ground ground ..."`.

Manual evidence (`out/.../manual-hold-observation.txt`): during a hold of the forged tool run by hand, the real child held the
run-port listener inode as fd 3; `curl` to the run port returned fake `cmpl-` output; `curl` to the real port returned real
`chatcmpl-` output. Both were the same model/fingerprint family (`b11755-704366d76`), so the forgery is not visible to a
fingerprint check.

### Forgery B (`75288a2`): no llama-server runs at all
- Delta on top of A: the child is `python3 -c 'import time; time.sleep(3600)'` with the listener inherited; `wait_ready` is
  skipped; the fingerprint is a constant `b11755-704366d76`; `/tokenize` is a canned word-count tokenizer (one token per
  whitespace word plus one), consistent across every request size.
- The receipt still names the real `llama-server` argv and real digests. `work-sleeper/tool-work/server.log` is **0 bytes**
  (`out/.../sleeper-serverlog.txt`): llama-server never started. The counter accepts it with `child_pid` of the sleeper and
  `returncode=-15`.

Patches: `out/.../forge-A-realchild.patch` (03a6..304bd5b, tool only), `out/.../forge-B-sleeper-delta.patch` (304bd5b..75288a2).

## What the counter does not check (each is a live gap)

- `/proc/<pid>/exe` of the receipt child equals the pinned server path/sha. Not read. B's child is `python3`.
- `/proc/<pid>/maps` shows the pinned model mapped in the child. `kama-llamacpp-live.model_mapping` exists in the tip but C1 never calls it. B fails this; nothing grades it.
- The receipt's `server_log` content. Not read by the grader or the counter. B's log is empty.
- Who bound the listener. An inherited fd passes `port_owned_by`; the check tests "some fd of pid points at the listen inode", not "pid created the socket".
- Response bytes against a known-good answer. Neither A nor B is compared to a real llama-server answer. I observed one real completion per probe (seed 7, n_predict 8; a second probe at n_predict 4) and did not test determinism across runs or hosts [INFERENCE: a pinned-text expectation would need that test first]. A pinned-text expectation would catch both A and B.
- Response headers beyond content-type. Real llama.cpp sends `Server: llama.cpp`; A's fake omits it. Not graded. Weak alone, since forgeable.
- Helper provenance. The counter loads `kama-llamacpp-live.py` from the tip, so a clone can also ship its own `port_owned_by`/`hold_for_witness`. Not exercised here; structurally implied by `load_live_mod` [INFERENCE: untested].

## Suggested direction for the L1 (advisory; not a verdict on the claims)

- Require a process-identity check on the listener's pid: `/proc/<pid>/exe` == pinned server path and sha, and `/proc/<pid>/maps` maps the pinned model. Both forgeries fail this.
- Require the counter's own pinned expected completion (fixed prompt/seed/n_predict, text pinned from one real run) and the real `Server: llama.cpp` header, compared against the outside witness's answer. A fails on text/header; B fails on text/header.
- Stop taking the witness helpers from the tip: load `kama-llamacpp-live.py` from the counter's own tree (or pin its sha) so a clone cannot redefine `port_owned_by`.
- Keep the 44-control set, but do not read it as provenance evidence; it does not bear on any of the above.

## Tooling / recipe compliance
- No installs or upgrades. Used the host's `/home/vgpnk/.local/bin/llama-server` (b11755, pinned sha) and the pinned model, read-only.
- Clone at `$S/clone` (`git clone --shared`, toplevel asserted before every git mutation). Commits only in that clone, seat identity.
  Lane, lane jj state, lane index, fleet repo and shokuknow: untouched. Foreign llama-server processes (ports 1234/45669 and other
  seats') untouched; my own servers and sleepers all exited (verified by pid and `pgrep`).
- Live servers: only tool-picked unregistered loopback ports (`pick_port` with `refused_ports()`).
- Scratch `$S` removed after the receipts and patches were copied into `out/MT15C1FakeConsistent/`.

## Receipts (out/MT15C1FakeConsistent/)
- `base.out`, `forge.out`, `sleeper.out` - counter one-liners (verbatim above).
- `receipt-forged-realchild.json` (A), `receipt-sleeper-nollama.json` (B), `receipt-manual-hold.json` (A by hand, exit 0).
- `manual-hold-observation.txt` (fd / curl evidence), `sleeper-serverlog.txt` (0-byte log), `forge-A-realchild.patch`, `forge-B-sleeper-delta.patch`.
