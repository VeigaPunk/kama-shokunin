# J2NoPdeathsig — C1 teardown-leg ablation: the replay's parent-death signal (round 50, lane kama)

**Verdict: the preregistered control "no replay parent-death signal" holds. At fixture commit `91762081352d3ace99937320c92693827ccf76ac` (build `97c864b…` with both `PR_SET_PDEATHSIG` requests removed from `tools/kama-live-replay.py`) the frozen C1 counter returns `bind=1 teardown=0 newrow=1 bound=3/3 met=False` (exit 1) — after the invoker SIGKILL all three descendants are alive at 30.02 s with the witness port still accepting, and they only die at 120.07 s when the live tool's 120 s witness hold expires. The paired run at the unpatched build in the same clone returns `bind=1 teardown=1 newrow=1 bound=3/3 met=True` (exit 0), teardown in 0.10 s. The teardown leg is the only gate that this ablation moves: bind stays 3/3 and newrow stays 1.**

## Axes / scope

- Operability (C1, 8→8). The round-50 build claims closure R2 (round-49 seat X1Kill: "a killed counter left replay, live tool and server up; pdeathsig covered only live tool → server"): `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md` S497 grounds the mechanism, the build wires it at `tools/kama-live-replay.py:587` (`set_own_pdeathsig()`, defined `:100`) and `:314/:332` (`_child_pdeathsig` via `preexec_fn`), and the counter's `teardown_leg` (`tools/round50-replay-bind-audit.py:497`, `KILL_WAIT = 30` at `:112`) is the instrument.
- This seat asks the ablation question: **remove that mechanism and nothing else — does the frozen counter notice?** Preregistration (`/.ufo/waves/round-50/preregistration.json`, `controls`): "after the build, ablation controls on the build tree, each removing one claimed mechanism — C1: … no replay parent-death signal … Every control must be met=False." My result matches the frozen expectation.
- No lane file was edited, added, committed, checked out or reset in `/home/vgpnk/Projects/shokunin/kama-shokunin`: read-only `git show`/`rev-parse`/`archive` and `sha256sum` only. The patch exists only in a scratch `git clone --shared` fixture.

## Frozen inputs (checked, not assumed)

```
$ sha256sum kama-shokunin/tools/round50-replay-bind-audit.py
ff6ac2ace541ea35a4d240ceebb019653c11a2a08c025e514770f3f94a9c5e89  tools/round50-replay-bind-audit.py
   == preregistration.json claims[id=C1].counter_sha256 (same value)
$ git -C kama-shokunin rev-parse 97c864bead3ee4a2f629574e77263d33834ec98a:tools/kama-live-replay.py
4d675380c5f00c57a890aeeeb78d47d2972ef766
$ sha256sum kama-shokunin/tools/kama-live-replay.py      # content of that blob
d5c58972c0fd8f818b8dd2bd81f6cbc3a87c7f23b65805a804bf09b579a5a239
```

Counter, preregistration and controls were read-only for this seat; nothing in `tools/` was modified.

## Fixture (scratch clone, fixture identity, `toplevel-ok` asserted before commit)

```
$ S=/fast/scratch/hyaku/kama-r50/J2NoPdeathsig
$ git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
$ git -C $S/lane checkout --detach 97c864bead3ee4a2f629574e77263d33834ec98a
$ TOP=$(git -C $S/lane rev-parse --show-toplevel); [ "$TOP" = "$S/lane" ]   # toplevel=/fast/scratch/hyaku/kama-r50/J2NoPdeathsig/lane
$ git -C $S/lane -c user.name=J2NoPdeathsig -c user.email=j2-nopdeathsig@round50.invalid commit …
91762081352d3ace99937320c92693827ccf76ac
J2NoPdeathsig <j2-nopdeathsig@round50.invalid>   (author and committer)
parent 97c864bead3ee4a2f629574e77263d33834ec98a
 tools/kama-live-replay.py | 47 ++++++++---------------------------------------
 1 file changed, 8 insertions(+), 39 deletions(-)
blob 97c864b:tools/kama-live-replay.py  4d675380c5f00c57a890aeeeb78d47d2972ef766
blob 9176208:tools/kama-live-replay.py  75f79d2f861c708809b2e4d6974f58c7ab04168b
sha256 content at tip                   c60c1766110f8b1adb70328673c921320cf3c72ce9af4c8b4438264ed7c3df46
$ python3 -I tools/kama-live-replay.py --selftest --scratch $S/selftest
KLR_SELFTEST pass=23 fail=0
```

The whole delta (`ablation.diff`, `ablation.patch` in this directory) is the two mechanisms the claim names and their now-dead helpers:

- `set_own_pdeathsig()` (build `tools/kama-live-replay.py:100-110`) plus `_prctl()`/`PR_SET_PDEATHSIG` and the `ctypes`/`signal` imports: removed; the call at build `:587` is gone, so **the replay no longer dies with whatever started it**.
- `_child_pdeathsig` and `preexec_fn=_child_pdeathsig` (build `:314-318`, `:332`): removed, so **nothing signals the live child when the replay dies**; `res["live_child"]["pdeathsig"]` now honestly records `None`.
- Untouched: `python -I` on the live child, `LIVE_ENV_KEYS`, `model_mapping`, the live tool `tools/kama-llamacpp-live.py` in full (so its `hold_for_witness` parent poll at `:359/:363` and its own live→server `preexec_fn=_preexec_pdeathsig` at `:661/:1888` are intact).

## Frozen counter on the ablation (the control run)

```
$ TMPDIR=$S python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round50-replay-bind-audit.py \
    --repo $S/lane --tip 91762081352d3ace99937320c92693827ccf76ac --scratch $S/c1 --out $S/c1-ablation.txt
tip=91762081352d3ace99937320c92693827ccf76ac
bind=1 teardown=0 newrow=1 bound=3/3 met=False
detail: counter vocabulary: 512 tokens from its own download
detail: bind b1: pid 2413043 port 39671 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1022172686 recorded, nonce 'kama witness d22f0d2763c7ee70' round-tripped
detail: bind b2: pid 2433536 port 38437 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 616636283 recorded, nonce 'kama witness 69a507fb86804597' round-tripped
detail: bind b3: pid 2451771 port 34411 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 2092956011 recorded, nonce 'kama witness e4f8238ec46c1d31' round-tripped
detail: teardown: invoker SIGKILLed with 3 descendants; after 30.07 s alive [2454243, 2465825, 2468193] port ACCEPTS FAIL
detail: newrow: 3 rows new since base; 1 name proc_pid_maps(5): ['| S496 |']

exit 1   (48.0 s wall)
```

## Paired build run (same clone, same scratch root, unpatched tip)

```
$ TMPDIR=$S python3 …/round50-replay-bind-audit.py \
    --repo $S/lane --tip 97c864bead3ee4a2f629574e77263d33834ec98a --scratch $S/c1b --out $S/c1-build-control.txt
tip=97c864bead3ee4a2f629574e77263d33834ec98a
bind=1 teardown=1 newrow=1 bound=3/3 met=True
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok

exit 0   (16.4 s wall)
```

Same host, same clone, same counter bytes, same three committed v5 receipts: the only difference is the fixture commit. The teardown leg separates 0.10 s from >30 s (with the tree still refusing to go at 120 s).

## Attribution: which edge the ablation removes, measured

The build has three separately-clocked teardown edges. I killed one member per run at the fixture (same invoker/env/witness nit as the counter, `start_replay` reused verbatim from the frozen counter by `obs-edge.py`/`obs-timeline.py`; window 45 s / 240 s, sampling 0.5 s):

| edge killed (`SIGKILL`) | mechanism at build | in fixture | tree gone after | port |
|---|---|---|---|---|
| invoker (the counter's leg) | replay's own `PR_SET_PDEATHSIG`, build `tools/kama-live-replay.py:100,587` — one-shot, **no polling fallback** | removed | **120.07 s** (whole tree), 3/3 alive at 30.02 s | accepting until 120.07 s |
| replay | live child `preexec_fn` prctl (`:314/:332`) **and** the live tool's 50 ms `os.getppid() == parent` poll (`kama-llamacpp-live.py:359`) | both intact | ≤0.5 s | refuses |
| live tool | live tool's own live→server prctl (`kama-llamacpp-live.py:661,1888`) | intact | ≤0.5 s | refuses |

So the surviving tree in the counter's teardown leg is attributable to the removed **outer** edge only (invoker → replay); the inner edges still collapse in one poll interval. That is also why the ablation is a *teardown* control and not a general "everything leaks" control.

The orphaned tree is not idle while it refuses to die — it finishes the job nobody is waiting for:

- `timeline-observation-invoker-kill.json`: 241 samples; pids `2966533` (replay), `2987107` (live tool), `2990076` (server, `ready.json` pid) all alive at 0/10/20/30/60/90/110/119 s, `port_refuses=false` throughout, empty + refusing at 120.07 s.
- `replay-out-after-invoker-kill.json`: the replay — whose invoker has been SIGKILLed — completed normally: `"match": true`, `"refused": null`, `"live_exit": 0`, `"live_child": {"isolated": true, "pdeathsig": null}`.
- `rerun-receipt-after-invoker-kill.json`: `witness {released: false, orphaned: false, waited_ms: 120029, pid: 2990076, port: 33123}`, `model_mapping {mapped: true, sha256: 270cba1b…bd256d, dev: 103:05}`.

Read: the exposure is a **live, serving server plus a working replay for 120 s after the parent is gone**, and the bound is the live tool's witness hold, not the parent's death. `waited_ms 120029` == the replay's default `--witness-timeout 120.0` (`tools/kama-live-replay.py:276,554`, passed to the child at `:330`); [INFERENCE] a replay started with `--witness-timeout S` (accepted up to 3600 s, `:584`) would leave the tree up for ~`S` seconds, so the ablation's damage scales with an argument unrelated to teardown.

## Why the counter catches it, and what stays green

- `teardown_leg` (`tools/round50-replay-bind-audit.py:497-535`) is the sole gate on R2: it snapshots every descendant of the invoker, SIGKILLs the invoker, and requires all snapshotted pids gone **and** the port refusing within `KILL_WAIT = 30` (`:112`). At 30.02 s the fixture has 3/3 alive and `port ACCEPTS` ⇒ `teardown=0`, `met=False` (exit 1). Nothing in the leg depends on the bind legs, so the ablation is not confounded.
- `bind` is unaffected (`3/3`): isolation, allow-listed environment, canary absence, pid/`child_pid` join, nonce round-trip and `model_mapping` all still hold — my patch does not touch the R1 mechanisms, and the counter says so.
- `newrow` is unaffected (`3 rows new since base; 1 name proc_pid_maps(5): ['| S496 |']`).
- The teardown signature at the build fixture (`3 descendants alive, port ACCEPTS`) is the same shape as the base control's teardown signature (`.ufo/waves/round-50/controls/base.c1.out`: `after 30.06 s alive [531059, 568483, 573554] port ACCEPTS FAIL`) — but at the build commit, where bind and newrow are already green. That is the sharpest statement of the control: **at the build, the only thing standing between `met=True` and `met=False` on this leg is the pair of prctl calls**.

## Limits / caveats (mine, on top of the preregistered ones)

- One run per leg. The raw separation is 0.10 s vs 120.07 s against a 30 s budget, so the gate has ~4× margin at the ablation and ~300× at the build; I claim the direction and the margin, not a distribution.
- The counter SIGKILLs the invoker only, during the witness hold (preregistration limit: "kills during download or readiness are not exercised"; peer `Sen3Teardown` owns the kill-variant matrix). I did not exercise SIGTERM to the invoker, `SIGHUP` on a controlling terminal close, or `PDEATHSIG` races (the build's `set_own_pdeathsig` re-reads `os.getppid()` after the prctl and exits if it changed, `tools/kama-live-replay.py:107-108`).
- `--witness-timeout` was left at the replay default 120 s, exactly as the counter starts it (`start_replay` passes no `--witness-timeout`), so the 120.07 s figure is the counter's real exposure, not a knob I chose.
- My fixture also deleted the now-unused `_prctl`/`ctypes`/`signal` helper code and adjusted the module docstring's R2 sentence to say the mechanism is ablated; neither is executable behaviour. The selftest passes 23/23 at the fixture, so the ablation is not a broken file.

## Findings

**No defect in the frozen counter, the preregistration, or the build.** The counter's teardown leg is live, load-bearing and correctly the only leg that moves under this control; the build's outer-edge mechanism is a single, one-shot prctl with no polling fallback (`tools/kama-live-replay.py:100-110` is called once at `:587`), which is precisely what makes the control a real removal rather than a redundancy test — and it is caught. No patch is proposed (counters and preregistration are frozen; a finding would be reported, not fixed).

Residual observation for the L1, not a defect: the inner edges have two independent detectors (prctl + 50 ms `getppid()` poll at `kama-llamacpp-live.py:359`), the outer edge has one. If a future round adds a fallback clock to the replay (e.g. poll `os.getppid()` in the replay's wait), the counter's 30 s teardown leg would still pass — the control above is what would catch its removal, and it can be re-run from `ablation.patch` at any tip.

## Hygiene

- Lane/fleet/shokuknow untouched: every git command in `/home/vgpnk/Projects/shokunin/kama-shokunin` was `show`/`rev-parse`/`archive`/`log`; the only commit was inside `$S/lane`, whose `rev-parse --show-toplevel` was asserted to be that directory, with fixture identity `J2NoPdeathsig <j2-nopdeathsig@round50.invalid>`.
- No service was started or stopped; the counter and my two probes started llama-server only on the loopback port the live tool picked, and every tree I started was reaped. `pgrep -af "J2NoPdeathsig.*llama"` is empty after all runs; the llama-server processes visible during the window belong to peers' scratch dirs (`X11ModelSwap`, `J3NoMapping`) and were not touched.
- No tool was installed or upgraded (nothing outside the stdlib was needed).
- Scratch `/fast/scratch/hyaku/kama-r50/J2NoPdeathsig` (one `--shared` clone, model/archive downloads, one extracted tree) is removed; every artifact cited here is copied into this directory first. Base control run wall times: ablation 48.0 s, build 16.4 s, timeline 122.8 s, edge probes 6.2 s.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/J2NoPdeathsig.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/J2NoPdeathsig/ablation.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/J2NoPdeathsig/ablation.patch`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/J2NoPdeathsig/c1-ablation-receipt.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/J2NoPdeathsig/c1-build-control-receipt.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/J2NoPdeathsig/fixture-commit.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/J2NoPdeathsig/timeline-observation-invoker-kill.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/J2NoPdeathsig/replay-out-after-invoker-kill.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/J2NoPdeathsig/rerun-receipt-after-invoker-kill.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/J2NoPdeathsig/edge-kill-replay.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/J2NoPdeathsig/edge-kill-live.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/J2NoPdeathsig/obs-timeline.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/J2NoPdeathsig/obs-edge.py`
