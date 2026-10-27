# J1NoRecord — round-51 C1 ablation control (no `server_exe` record)

Verdict: **control holds — met=False at ablation commit 0637bc05 (bind=0 own=0 teardown=1 newrow=1, exit 1); bind drops too, because the round-51 replay tool itself refuses a rerun receipt with no `server_exe` (`server-exe:absent`, match False, exit 1) and the counter's bind leg gates on the replay's verdict, not only on its own observations. Positive control at the build commit 138af25b in the same clone met=True (exit 0), so the only difference is the two commented lines.**

## Setup

- Scratch: `/fast/scratch/hyaku/kama-r51/J1NoRecord` (`TMPDIR` set there); one `git clone --shared` of the lane at `.ufo`-less state HEAD 4eca4892, then detached `checkout 138af25b963450b6520794995605fa7dbbcd87e0` (round-51 build-fix 2). `git -C $S/lane rev-parse --show-toplevel` printed `$S/lane` before the commit.
- Frozen counter bytes: `sha256sum tools/round51-replay-exe-audit.py` = `e5753c453c30bd311e4c12fc962d324c7db482233b64b22795658b47b6ee5155`, identical to the preregistration `counter_sha256` for C1; the counter was executed from the lane's read-only copy, never edited.
- Lane tools at 138af25b: `kama-llamacpp-live.py` 00de205b…, `kama-live-replay.py` e40f472b….

## Ablation

`tools/kama-llamacpp-live.py`, the two assignments in `main()` (138af25b:2041 and :2044) commented out, with a one-line marker comment each; nothing else changed:

```
$ git -C $S/lane -c user.name=fx -c user.email=fx@invalid commit -q -am "control round-51 C1: kama-llamacpp-live.py records no server_exe (ablation, seat J1NoRecord)"
$ git -C $S/lane rev-parse HEAD
0637bc05f53306fc16e5a26238c236e34277d235
$ git -C $S/lane diff 138af25b 0637bc05 > ablation.diff     # 2 hunks, 4 added/2 removed lines, one file
```

`receipt['server_exe']` is still initialised at `tools/kama-llamacpp-live.py:1798` (`'server_exe': None`), so the rerun receipt carries the key with value **null** — not an omitted key (verified below, `rerun-receipt-server-exe-null.json`).

## Receipt (frozen C1 counter at the ablation)

```
$ python3 <lane>/tools/round51-replay-exe-audit.py --repo $S/lane --tip 0637bc05f53306fc16e5a26238c236e34277d235 --scratch $S/run --out $OUT/c1-no-server-exe.out
exit=1
tip=0637bc05f53306fc16e5a26238c236e34277d235
bind=0 own=0 teardown=1 newrow=1 bound=0/3 owned=0/3 met=False
detail: counter vocabulary: 512 tokens from its own download
detail: bind b1: replay exit 1 match False refused None
detail: own b1: own: rerun server_exe None does not record the observed image ('103:05', '2092865056')
detail: bind b2: replay exit 1 match False refused None
detail: own b2: own: rerun server_exe None does not record the observed image ('103:05', '682923609')
detail: bind b3: replay exit 1 match False refused None
detail: own b3: own: rerun server_exe None does not record the observed image ('103:05', '1353010972')
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 1 rows new since base; 1 name proc_pid_exe(5): ['| S499 |']
```

Expected and met: `own=0`, `met=False`. `teardown=1` and `newrow=1` are untouched by this mechanism, so the whole loss is bind+own.

## Why bind also drops

The removal is not confined to the counter's `own` leg: `server_exe` is part of the **replay tool's** contract, and the counter's bind leg treats a replay that did not match as a bind failure.

1. Rerun receipt has `server_exe: null` (`tools/kama-llamacpp-live.py:1798`, assignments at :2041/:2044 removed).
2. `tools/kama-live-replay.py:359-363`: `se = rr.get("server_exe")`; `not isinstance(se, dict)` → appends `server-exe:absent`; `res["match"] = not res["mismatches"]` → False → exit 1.
3. `tools/round51-replay-exe-audit.py:475-477`: the bind leg appends `replay exit {code} match {...}` to `probs` whenever the replay exit is non-zero or match is not True → bind False for all three receipts.
4. `tools/round51-replay-exe-audit.py:490-493`: the own leg separately appends `rerun server_exe None does not record the observed image {got}` → own False.

Direct capture of step 2 with the same patched clone (one replay, no witness dir; `direct-replay-result.json`):

```
$ cd $S/lane && python3 tools/kama-live-replay.py --receipt .ufo/waves/round-48/c2/live/receipt-1.json --work $S/direct-work --out $S/direct.json
exit=1  (log: replay match=False refused=None mismatches=1 exit=1)
match False  live_exit 0  refused None
mismatches ['server-exe:absent']
own_server {'path': '.../direct-work/server/llama-b11909/llama-server', 'dev': '103:05', 'inode': '1553519949'}
rerun receipt: server_exe key present True | value None ; model_mapping mapped True ; witness released None (no witness dir in this direct run)
```

So the server still ran, bound loopback, round-tripped the nonce, mapped the model and joined `child_pid` (`live_exit 0`; the counter's `own` detail still carries its own read of the running image, e.g. `('103:05', '2092865056')`), and the tree was still reaped. The bind failure is purely the counter's line 475 gate on the replay's `server-exe:absent` verdict.

Interpretation caveat for the L1 (observation, not a counter defect — the counter is a conjunction and `met` is unchanged): because `bind` is gated on the replay verdict, *any* failure of the round-51 `server_exe` contract now also zeroes `bind`, so this control is a **joint** ablation and cannot isolate `own` from `bind` on its own. Isolating `own` would need a live tool that records a `server_exe` dict the counter rejects while the replay still matches, which the replay's own :364-367 checks make impossible by construction (wrong sha or dev/inode also mismatches the replay). The preregistration's control list names exactly this control ("C1: no server_exe record"), so the joint drop is within the frozen design.

## Positive control (same clone, same scratch, build bytes)

```
$ python3 <lane>/tools/round51-replay-exe-audit.py --repo $S/lane --tip 138af25b963450b6520794995605fa7dbbcd87e0 --scratch $S/run2 --out $OUT/c1-build-138af25b.out
exit=0
bind=1 own=1 teardown=1 newrow=1 bound=3/3 owned=3/3 met=True
detail: own b1: running image 103:05:1353074200 is the extracted member, recorded in server_exe and own_server
detail: own b2: running image 103:05:1489525128 is the extracted member, recorded in server_exe and own_server
detail: own b3: running image 103:05:20425986 is the extracted member, recorded in server_exe and own_server
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 1 rows new since base; 1 name proc_pid_exe(5): ['| S499 |']
```

Reproduces the build receipt (`.ufo/waves/round-51/measured/c1-build.out`, met=True at 73bf2a7a) at 138af25b, with nonces round-tripped for all three receipts. Together with the ablation run this isolates the two commented lines as the sole cause of met=False.

## Hygiene / limits

- No tool installs or upgrades; nothing started outside the lane tools' own loopback `llama-server` children, which the counter reaps (teardown detail, `alive []`). `pgrep -af llama-server` after both runs shows no process started by this seat.
- Lane, fleet repo, shokuknow: read-only, no writes/commits/fetches; the only commit is in the scratch clone (`0637bc05`, identity `fx <fx@invalid>`, toplevel verified).
- Scratch `/fast/scratch/hyaku/kama-r51/J1NoRecord` removed after copying the evidence; no `/tmp` paths are cited.
- Limit inherited from the counter, not exercised here: C1 compares dev/inode against the replay's extracted member, so a byte-identical copy at `<work>/server/<member>` would be indistinguishable; this control says nothing about that leg.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/J1NoRecord.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/J1NoRecord/c1-no-server-exe.out` (counter receipt at 0637bc05)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/J1NoRecord/c1-no-server-exe.log`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/J1NoRecord/c1-build-138af25b.out` (positive control)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/J1NoRecord/c1-build-138af25b.log`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/J1NoRecord/ablation.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/J1NoRecord/direct-replay-result.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/J1NoRecord/direct-replay.log`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/J1NoRecord/rerun-receipt-server-exe-null.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/J1NoRecord/run-meta.txt`
