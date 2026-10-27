# K1Cheat2 — round-50 C1 shortcut attack on tools/round50-replay-bind-audit.py

VERDICT: all four cheats caught — `met=False` on every decoy fixture; the counter
measures `met=True` at the real tip under the same rig, so each failure is the
cheat, not the harness. Two stated limits confirmed (exe check binds the digest,
not the path; the env check is a single-key canary, other injected variables are
invisible) plus one observation (reparented processes escape both the teardown
snapshot and the reaper).

## Rig

- Fixture identity: `git clone --shared` of the lane at `$S/lane`; each cheat is a
  single fixture commit on top of `97c864bead3ee4a2f629574e77263d33834ec98a`
  (`--tip`), replacing only `tools/kama-live-replay.py` with a decoy
  (throwaway `-c user.name/-c user.email` commit; never in the lane repo).
- Fixture tips: `.ufo/waves/round-50/w1/out/K1Cheat2/tips.json`
  - c1-verbatim  `835074470487715195c498a79d2d33355a0e349a`
  - c1-patched   `31e249edac263c05f87d9a341989404071f17eb6`
  - c2-reparent  `9caa821244504174d51b419c17baa44f4597bb2f`
  - c3-dirtyenv  `7cac8ce6cff4dd4f66e6d3aa64f1cff86ca67275`
- The decoy (out dir: `decoy-*.py`, generator `make_decoys.py`) runs a byte copy
  of the host b11909 install (`cp -r /home/vgpnk/.local/opt/llama-b11909`), serves
  the frozen model on a picked loopback port, speaks the witness handshake
  (ready.json -> hold -> release -> rerun receipt + `{"match": true, ...}` out),
  and sets its own pdeathsig plus a pdeathsig chain through its children so the
  teardown leg is not lost on collateral.
- Command per run (scratch `$S=/fast/scratch/hyaku/kama-r50/K1Cheat2`):
  `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round50-replay-bind-audit.py
   --repo $S/lane --tip <fixture tip> --scratch $S --out $S/out/<name>.out`
- Sanity control: same command at `--tip 97c864bead3ee4a2f629574e77263d33834ec98a`
  on the same clone -> `bind=1 teardown=1 newrow=1 bound=3/3 met=True`, exit 0
  (receipt `sanity-tip.out`). Rig is clean; each `met=False` is the cheat.

## Cheat 1 — verbatim receipt copy (child_pid 611093) : CAUGHT

Two fixtures, both `met=False`, exit 1.

- `c1-verbatim` (receipt copied byte-for-byte, `out`: `c1-verbatim.out`):
  `bind=0 teardown=1 newrow=1 bound=0/3 met=False`. Per leg:
  `rerun receipt does not record witness.released true`,
  `rerun child_pid 611093 != observed pid <N>`,
  `rerun model_mapping None does not record the observed mapping ('103:05', ...)`.
- `c1-patched` (verbatim copy patched with `witness.released` and a real
  `model_mapping` record; `child_pid` left at the copied 611093/612878/615051;
  `out`: `c1-patched.out`):
  `bind=0 teardown=1 newrow=1 bound=0/3 met=False`. The ONLY remaining problem per
  leg is `rerun child_pid 611093 != observed pid <N>` — the observed-pid join
  (counter lines 469-472) alone stops the receipt-copy shortcut. Exe, listen,
  nonce, tree, env and mapped all pass against a decoy-started server: it serves
  the real frozen binary and the real frozen model, so the join is exactly what
  binds the receipt to the witnessed run — the round-49 R1 hole this counter was
  built to close.

## Cheat 2 — child_pid rewritten to observed pid, server reparented : CAUGHT

`c2-reparent`: the decoy double-forks + `setsid` a grandchild which starts the
server (then exits), so `rr["child_pid"] == observed pid` and the server is
reparented to a subreaper (observed ppid 1494 = user `systemd`). Receipt
`c2-reparent.out`: `bind=0 teardown=0 newrow=1 bound=0/3 met=False`.

- Bind legs: `server pid <N> does not descend from the replay process <rp>` —
  the tree leg (counter lines 451-453, `descends_from`) still stops it with the
  join satisfied. Collateral: `server parent environ unreadable (pid 1494)` —
  the env check fails closed when the parent is not ours to read. The decoy's
  own "reparented server ppid" log line confirmed ppid=1494 before announce.
- Teardown leg: `announced pid <N> is not under the invoker` -> `teardown=0`
  (membership check, counter line 507/520). Port refused in 0.10 s only because
  my decoy planted an out-of-tree watchdog; the counter's `reap()` cannot see
  reparented processes at all (see observation below).

## Cheat 3 — environment injection; canary marker not stamped : CONFIRMED (check catches the leak; marker is python-only by construction)

`c3-dirtyenv`: the server is the decoy's direct child inheriting the counter's
whole environment (KAMA_R50_CANARY, PYTHONPATH) plus injected PYTHONSTARTUP,
XDG_CONFIG_HOME and K1CHEAT2_INJECTED. Receipt `c3-dirtyenv.out`:
`bind=0 teardown=1 newrow=1 bound=0/3 met=False`, per leg
`server pid <N> carries the planted KAMA_R50_CANARY` and
`server parent pid <N> carries the planted KAMA_R50_CANARY`.

- The planted sitecustomize marker is not stamped (and cannot be): llama-server
  is a C++ binary, no Python interpreter under the decoy imported it, and no
  `planted sitecustomize imported` detail appears in any run (the real-replay
  sanity run likewise stamps nothing; the base control shows the mechanism
  works — one stamped interpreter per leg in `controls/base.c1.out` lines 4-12).
  PYTHONSTARTUP and XDG_CONFIG_HOME injections are also inert here for the same
  reason. Confirmed limit (prereg limits #2): only those two canaries are planted.
- Additional confirmed limit, adjacent: `observe()` checks only whether the one
  name `KAMA_R50_CANARY` is present in the server's and its parent's environ
  (counter lines 353-358). Other variable names pass silently — K1CHEAT2_INJECTED,
  PYTHONSTARTUP and XDG_CONFIG_HOME reached the server with no detail line. So
  the env leg proves "the inherited environment did not reach the server", not
  "the server's environment is clean"; a hostile replay could hand the server an
  arbitrary env (e.g. LD_PRELOAD) as long as it drops one name.

## Cheat 4 — host-copy server passes exe : CONFIRMED stated limit

`sha256sum /home/vgpnk/.local/opt/llama-b11909/llama-server` =
`35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0` = `SERVER_SHA`
(the receipts themselves record that binary path/digest — the original runs used
the host install). `sha_file("/proc/<pid>/exe")` (counter line 345) hashes the
running image, not a path: every decoy run served a copy at
`$S/r50c1-*/tree-work/server-copy/llama-server` and no `exe sha256` problem was
ever logged, including the run where it was the only clean leg. Any bit-identical
binary at any path passes; the exe leg binds the digest, not provenance.

## Observation (not a kill): reparented processes escape teardown bookkeeping

`snap = descendants(invoker)` and `reap()` both walk the invoker's live tree
(counter lines 279-294, 425-437). A `double-fork`/`setsid` child is outside that
tree: it is never snapshotted, the 30 s `alive` list can be empty while it still
runs, and `reap` cannot kill it — only the `port` check and the announced-pid
membership check bound it. In c2 the teardown leg correctly FAILs, but a
reparented leak would survive the counter's own cleanup (my watchdog covered it;
`pgrep -f llama-server` clean after every run). Post-run leftover sweep remains
the counter operator's problem.

## Cleanup / discipline

- `pgrep -f llama-server` after all runs: no leftovers (exit 1).
- Clone `$S/lane` and all decoys/scratch removed with `rm -rf $S` after evidence
  was copied out (per scratch directive). Lane repo untouched (`git status`
  clean); fleet repo and shokuknow untouched. No pacman; no new tools installed.
