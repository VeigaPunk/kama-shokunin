# J4Decoy — C1 join/tree ablation: a decoy replay meets the frozen counter (bind=1, met=True)

Verdict: **C1 cannot distinguish a decoy replay from the lane replay.** At a fixture tree of
`97c864bead3ee4a2f629574e77263d33834ec98a` whose `tools/kama-live-replay.py` execs a decoy in
its witness path — a decoy that starts the host b11909 `llama-server` with the model itself,
writes `ready.json`, copies the original v5 receipt with `child_pid` rewritten to the observed
pid plus `witness.released` true and the observed `model_mapping`, and never runs
`tools/kama-llamacpp-live.py` — the frozen counter reports
`bind=1 teardown=1 newrow=1 bound=3/3 met=True` (exit 0). The naive decoy (no environment
sanitization, receipt copied verbatim) is stopped, but only by the env leg and by the missing
`model_mapping`; the tree leg does not stop an in-place exec, and a decoy that sanitizes its
own and the server's environment and records the mapping honestly passes all six bind legs.

## Fixture and method

- Clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`; scratch
  `S=/fast/scratch/hyaku/kama-r50/J4Decoy`; branch `j4decoy-w1` at
  `97c864bead3ee4a2f629574e77263d33834ec98a`; `git -C $S/lane rev-parse --show-toplevel`
  printed `$S/lane` before the first commit; commits used the fixture identity
  `J4Decoy fixture <j4decoy@fixture.invalid>` only inside that clone.
- Decoy: `tools/kama-live-replay-decoy.py` (saved: `out/J4Decoy/kama-live-replay-decoy.py`).
  It downloads the receipt's model (sha256 verified), starts
  `/home/vgpnk/.local/opt/llama-b11909/llama-server` on a loopback port with `-c/-t/--alias`
  from the receipt, waits for it to listen, writes `<witness-dir>/ready.json` with the real
  pid, holds until `<witness-dir>/release`, then writes
  `work/rerun-receipt.json = json.loads(original)` with only `child_pid`, `witness` and
  `model_mapping` replaced, and a replay result with `match: true`. It never invokes the live
  tool, never evaluates a check, never verifies the archive.
- Patch to the replay (fixture only), `tools/kama-live-replay.py:587-600`: after
  `set_own_pdeathsig()` in `main()`, when `--witness-dir` is given (the counter always passes
  it), it `os.execve`s the decoy in place with a clean environment
  (`PATH HOME LANG LC_ALL` + `TMPDIR`). In-place exec keeps the decoy on the replay's pid, which
  is what the tree leg measures. Full diff: `out/J4Decoy/lane-patch.diff`.

Fixtures committed (saved: `out/J4Decoy/fixture-commits.txt`):

| commit | decoy variant |
|---|---|
| `5e395e92a4bccd9f084748fa92c421256e39432e` | naive: inherited environment, receipt copied verbatim + `child_pid` |
| `e33ff79dd7b66caa219380c8299f996894164670` | decoy records the observed `model_mapping`; its env and the server's env are sanitized |
| `3c023f5df2b62ad1b506b547f7d3a08fb2b1edc6` | v2 + the decoy's server gets `PR_SET_PDEATHSIG` SIGTERM |

Each run:

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round50-replay-bind-audit.py \
  --repo $S/lane --tip <fixture commit> --scratch $S/cN --out $S/cN-receipt.txt
```

## Counter receipts (verbatim, saved under out/J4Decoy/)

Naive decoy, exit 1, 42.7 s (`c1-receipt-naive.txt`):

```
bind=0 teardown=0 newrow=1 bound=0/3 met=False
detail: bind b1: server pid 2768993 carries the planted KAMA_R50_CANARY
detail: bind b1: server parent pid 2762826 carries the planted KAMA_R50_CANARY
detail: bind b1: rerun model_mapping None does not record the observed mapping ('103:05', '551948245')
... (same for b2, b3)
detail: teardown: invoker SIGKILLed with 2 descendants; after 30.06 s alive [2794471] port ACCEPTS FAIL
detail: newrow: 3 rows new since base; 1 name proc_pid_maps(5): ['| S496 |']
```

Stealth decoy (v2), exit 1, 41.8 s (`c2-receipt-stealth-env-mapping.txt`): **bind passes 3/3**,
only the teardown leg fails:

```
bind=1 teardown=0 newrow=1 bound=3/3 met=False
detail: bind b1: pid 3747082 port 42209 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1084474195 recorded, nonce 'kama witness 71e2b4047d8d134b' round-tripped
... (b2, b3 identical)
detail: teardown: invoker SIGKILLed with 2 descendants; after 30.05 s alive [3781476] port ACCEPTS FAIL
detail: newrow: 3 rows new since base; 1 name proc_pid_maps(5): ['| S496 |']
```

Full decoy (v3), exit 0, 11.4 s (`c3-receipt-full-decoy-met.txt`):

```
bind=1 teardown=1 newrow=1 bound=3/3 met=True
detail: bind b1: pid 55226 port 47303 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 2025138593 recorded, nonce 'kama witness 2175a531229cf609' round-tripped
detail: bind b2: pid 75170 port 35825 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1020740434 recorded, nonce ...
detail: bind b3: pid 97042 port 40393 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1020740453 recorded, nonce ...
detail: teardown: invoker SIGKILLed with 2 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 3 rows new since base; 1 name proc_pid_maps(5): ['| S496 |']
```

## Which leg stopped what

- **tree** (`round50-replay-bind-audit.py:452`, `rp = ../replay_pid(p)` then
  `descends_from(pid, rp)`): does **not** stop an in-place exec decoy. The decoy replaces the
  replay in the same pid, so the server it starts is a direct child of the "replay" and
  descends from it. Only a decoy that double-forks/setsids the server (K1Cheat2's variant 2)
  would trip this leg.
- **env** (`:353-358`): stopped the naive decoy twice — the server inherited
  `KAMA_R50_CANARY` and so did the server's *parent* (the decoy process, which is the replay
  process). A decoy that execs itself with an allow-listed environment and passes the same to
  its server leaves both clean; the planted `PYTHONPATH/sitecustomize` marker stays empty
  because the decoy runs `python -I` and the server is native. The leg then passes.
- **mapped / model_mapping** (`:476`): the counter's own mapping observation passed in every
  variant once the decoy ran the real binary with the real model (it detected
  `103:05`/inode and hashed the file). The receipt-side join failed for the naive decoy only
  because the round-48 receipt has no `model_mapping`; when the decoy reads
  `/proc/<server>/maps` and records `{mapped:true, dev, inode, sha256}` it passes.
- **join** (`:470-471`): `child_pid` is a field the decoy rewrites; the join is met by
  construction.
- **exe/listen/nonce** (`:343-380`): passed, because the decoy genuinely runs the frozen
  b11909 `llama-server` (`35ac50fb…`, the same digest as
  `/home/vgpnk/.local/opt/llama-b11909/llama-server`) with the real model. This is the
  already-stated host-copy limit (K1Cheat2 item 4).
- **teardown** (`:497-540`): independent of the receipt. It failed for v1/v2 only because the
  decoy's server had no parent-death signal; giving the server `PR_SET_PDEATHSIG` SIGTERM
  (as `kama-llamacpp-live.py` does) made it pass in 0.10 s.

## Defect (C1 bind, join leg)

`tools/round50-replay-bind-audit.py:440-478` (`bind_one`) proves *the observed server is the
frozen binary with the frozen model, owned by a pid the receipt names, in a clean
environment*. It does not prove *the rerun receipt was produced by
`tools/kama-llamacpp-live.py`*. The decoy copies the original receipt (only
`child_pid`/`witness`/`model_mapping` differ; 33 other keys identical, including the round-48
`argv` with `--port 33779` and the round-48 model path) and writes `match: true` itself — the
counter accepts the replay's own verdict at `:462` without re-deriving it and never compares
the rerun receipt against the original or against the tree.

Command that shows it: the v3 run above (`--tip 3c023f5d…`, exit 0, `met=True`).

Proposed fix (cheap, structural — bind the server to the live tool's *execution*, not to a
receipt field). In `bind_one`, after `rp = replay_pid(p)` and the `descends_from` check:

```python
parent = (stat_fields(pid) or (None, None, None))[1]
try:
    with open(f"/proc/{parent}/cmdline", "rb") as fh:
        cmd = fh.read().split(b"\0")
except OSError:
    cmd = []
if not (os.path.join(tree, "tools", "kama-llamacpp-live.py").encode() in cmd
        and b"--server" in cmd and os.path.join(tree, server_rel).encode() in cmd):
    probs.append(f"server parent {parent} is not the tree's live tool: {cmd[:4]}")
```

i.e. require the server's ppid to be a process whose `/proc/<ppid>/cmdline` names
`<tree>/tools/kama-llamacpp-live.py`, `--server` and the observed server path; the honest chain is
replay → live tool → server (`kama-live-replay.py:319-332`), my decoy's server parent is the
decoy (`…/kama-live-replay-decoy.py`) and is caught. Supporting receipt joins that would also
catch a copied receipt without proof strength: `rr.tool.sha256 == sha256(tree/tools/kama-llamacpp-live.py)`,
`rr.port == observed port`, `rr.argv` contains `--port <observed port>` and
`--server <observed server>`, `rr.model.path == <work>/download/<model>`, and
`rr.started_utc` inside the run window. (All are cheaper to check than one extra replay;
none is unforgeable against a tree that lies everywhere, but together they reject a copied
receipt, which is the round-49 R1 class.)

## Secondary observations

- The counter's own `mapped_model()` detection passed on every decoy run, so the counter
  observed the honest mapping and still accepted a receipt the live tool never wrote.
- The env leg reads one exact key (`:353-358`); a decoy that never inherits the canary is not
  caught by it.
- The teardown leg is satisfiable by any chain that sets `PR_SET_PDEATHSIG` on the server; it
  certifies behavior, not authorship. A tree that both decoys the witness path and sets the
  signals is `met=True` (v3).
- No lane file was edited; the two counters, the preregistration and the controls were not
  touched. Nothing was installed or upgraded (no pacman, no uv/npx/binary install). No
  service was started beyond the decoy's own loopback `llama-server`, all of which the decoy
  stopped (checked with `pgrep -af J4Decoy` — empty after every run).
- Scratch `$S` was removed after the evidence above was copied out; the fixture commits do
  not survive, so `lane-patch.diff`, `kama-live-replay-decoy.py` and the three counter
  receipts are the complete record.

## Files

- report: `.ufo/waves/round-50/w1/out/J4Decoy.md`
- `out/J4Decoy/c1-receipt-naive.txt`, `c2-receipt-stealth-env-mapping.txt`,
  `c3-receipt-full-decoy-met.txt`
- `out/J4Decoy/lane-patch.diff`, `kama-live-replay-decoy.py`, `fixture-commits.txt`
- `out/J4Decoy/sample/{ready.json,replay-out.json,rerun-receipt.json}` (a v3 decoy run: the
  observed pid/port and the receipt the counter accepted as the rerun)
