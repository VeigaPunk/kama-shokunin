# J4Hardlink — Round 52 C1 control (round-51 J4Hardlink shape)

**Verdict: the frozen C1 counter rejects the attack — a hardlink to the host b11909 install at `<work>/server/<member>`, exec'd by path, gives `bind=1 sealed=0 teardown=1 newrow=1 bound=3/3 sealedruns=0/3 met=False` (exit 1); the literal host inode cannot be linked into the mandated xfs scratch (EXDEV, btrfs vs xfs), and a same-filesystem byte-identical hardlink is rejected with the same `link count 2, not 0` / `not an anonymous memfd` sealed-leg evidence.**

## 1. Filesystem gate: the literal host inode cannot be staged on the mandated scratch

`fs-check.txt` (all commands run from the fleet root; `$S=/fast/scratch/hyaku/kama-r52/J4Hardlink`):

```
$ stat -c '%d %i %h %n' /home/vgpnk/.local/opt/llama-b11909/llama-server /fast/scratch/hyaku/kama-r52
56 238037577 1 /home/vgpnk/.local/opt/llama-b11909/llama-server
66309 1543504119 37 /fast/scratch/hyaku/kama-r52
$ stat -f -c '%T %i' /home/vgpnk/.local/opt/llama-b11909/llama-server /fast/scratch/hyaku/kama-r52
btrfs cc4be4baa8652d82
xfs 10305
$ df -T /fast/scratch/hyaku/kama-r52 /home/vgpnk/.local/opt/llama-b11909
/dev/nvme1n1p2   xfs   842131708 236170840 605960868  29% /fast
/dev/mapper/root btrfs 974646272 321267720 616574392  35% /home
$ ln /home/vgpnk/.local/opt/llama-b11909/llama-server $S/host-server.link
ln: failed to create hard link ... => '.../host-server.link': Invalid cross-device link
ln_exit=1
$ sha256sum /home/vgpnk/.local/opt/llama-b11909/llama-server
35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0  (the frozen server digest)
```

Host install: dev `56` (btrfs), inode `238037577`, nlink 1. Assigned scratch: dev `66309` (xfs, fs id `10305`). The seat's same-filesystem condition is **false**, so the fixture's literal `os.link(HOST_SERVER, member)` raises `EXDEV` at run time; the run below records that (`own_server.source = staged-hardlink:18:Invalid cross-device link`) and falls back to a byte-identical hardlink on the scratch filesystem — the round-51 J4Hardlink decoy shape, identical bytes and link count.

## 2. The literal host inode through `/proc/<pid>/exe` (direct probe)

`hostlink-probe.json`: the host install itself hardlinked at `out/J4Hardlink/run/llama-server.hostlink` (btrfs, `same_file: true`), exec'd on loopback `127.0.0.1:47201`, image read through `/proc/<pid>/exe`, then stopped:

```
proc_exe: link ".../run/llama-server.hostlink", dev "00:38", inode "238037577",
          nlink 2, seals null, seals_error "Invalid argument",
          sha256 35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0
port_refuses_after: true; host_nlink_after: 1; link_exists_after: false
```

The counter's sealed leg (`tools/round52-replay-memfd-audit.py:361-393`) appends a problem for each of exactly these facts: `:381-382` (link does not start with `/memfd:`), `:387-388` (`st_nlink != 0`), `:375-378` (`F_GET_SEALS` fails). **So a literal host-inode hardlink is `sealed=0` as well** — [INFERENCE] for the counter *outcome*, since the counter cannot be run with that link on xfs (EXDEV) and a btrfs scratch would independently fail the bind leg on the btrfs maps/mount-device mismatch measured in round 51 (`out/../round-51/a2w1/out/J4Hardlink.md`, maps `00:1e` vs stat `00:38`). The host inode was restored: nlink 1, link removed.

## 3. Fixture commit and frozen-counter run (the stageable hardlink)

- Clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`; checked out build `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`; `git rev-parse --show-toplevel` = `/fast/scratch/hyaku/kama-r52/J4Hardlink/lane` before committing.
- Patch (fixture only; `hardlink-member.patch`): `tools/kama-live-replay.py` gains `HOST_SERVER` + `hardlink_member()` (unlinks the digest-checked member, `os.link(HOST_SERVER, server)`; on `EXDEV` stages a `copy2` byte-identical copy under `<work>` and hardlinks it at the member path; re-checks the linked digest), calls it instead of `sealed_member()` (no `--server-fd`, no `pass_fds`), and deletes the replay-side `/memfd:`/seal/nlink criteria — the live tool then execs `<work>/server/<member>` by path exactly as at base.
- Fixture commit `c2313c3a91221058a7557289c8c1c4b3cea032a1` (parent `5dacf2c7…`, identity `fx <fx@invalid>`).
- Counter command and result:

```
$ python3 tools/round52-replay-memfd-audit.py --repo $S/lane \
    --tip c2313c3a91221058a7557289c8c1c4b3cea032a1 --scratch $S \
    --out .ufo/waves/round-52/w1/out/J4Hardlink/c1-hardlink-c2313c3a.out
tip=c2313c3a91221058a7557289c8c1c4b3cea032a1
bind=1 sealed=0 teardown=1 newrow=1 bound=3/3 sealedruns=0/3 met=False
exit=1
```

The counter file hashed `053ff50261812de3236697dd8dc847b3dff9507f8290b0d42aaf65c12e1121f5`, equal to the preregistration's `counter_sha256` (`.ufo/waves/round-52/preregistration.json`, C1). Per-replay sealed details (`c1-hardlink-c2313c3a.out`), identical for b1/b2/b3:

```
sealed bN: sealed: F_GET_SEALS on the running image failed: Invalid argument
sealed bN: sealed: running image link '<scratch>/work-bN/server/llama-b11909/llama-server' is not an anonymous memfd
sealed bN: sealed: running image has link count 2, not 0
sealed bN: sealed: rerun server_exe {..., 'nlink': 2, 'seals': None, 'sha256': 35ac50f…} does not record the observed sealed image ('103:05', '<inode>')
sealed bN: sealed: replay own_server {'memfd': False, ..., 'source': 'staged-hardlink:18:Invalid cross-device link', 'nlink': 2, 'dev': '103:05', 'inode': '<same>' } does not name the observed memfd
bind bN: pid … exe+listen+tree+env+mapped ok, child_pid joined, … nonce '…' round-tripped
teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
newrow: 1 rows new since base; 1 name memfd_create(2): ['| S500 |']
```

`bind=1` means the patched replay ran the hardlinked image to a full matching rerun (exit 0 at the live layer); the sealed leg still refuses it 3/3 on the counter's own `/proc/<pid>/exe` read (`sealed_exe`, `:361-393`, called at `:475`), independent of the replay's self-report. Base contrast: `.ufo/waves/round-52/controls/base.c1.out` at `9ff76b1f…` reports `sealed=0` with `link count 1`; this control reports `link count 2` — the hardlink shape is distinguished and rejected.

## 4. Findings, risks, blockers

- **No defect in the frozen counter.** The sealed leg rejects both the build's sealed-memfd image (measured, L1 battery `met=True`) and the hardlink substitution (`sealed=0`), and its observations do not trust the replay JSON: `sealed_exe` problems are collected from the counter's own `open("/proc/<pid>/exe")`, so a replay that falsely recorded `memfd: true` over a hardlink would still fail `bind_one` (`:475`, `:526-530`).
- **Environmental blocker (not a counter defect):** the literal host-inode hardlink cannot exist under the mandated `/fast` scratch (EXDEV, btrfs `56` vs xfs `66309`). A btrfs scratch would let the link be created but would fail the bind leg for the round-51 btrfs maps/mount-device mismatch (`00:1e` vs `00:38`), so there is no truthful full-counter pass for the literal host inode on this host; the direct probe (§2) and the same-fs hardlink run (§3) together cover the shape.
- **Fixture-only:** the replay's own `--selftest` cases `server-exe-not-own-memfd` / `not-sealed-memfd` (build `tools/kama-live-replay.py:576-592`) expect the removed check, so they would fail on the fixture; the frozen counter never runs `--selftest`. This is a property of the control patch, not a proposed lane change.
- One fixture iteration is disclosed: the first fixture commit (`baf2cc5c`) used `shutil.copyfile` for the staged fallback, which drops the execute bit, so the live tool refused with `server-not-executable` (`bind=0`); fixed to `copy2` and the commit amended to `c2313c3a` (the superseded receipt was deleted; its tip no longer exists).
- Constraints honoured: no lane/counter/lesson/registry edits (read-only); no git mutation outside `$S/lane`; no pacman or installs; no services started except the probe's own loopback server (port 47201, stopped, port refusing confirmed); scratch removed; host install nlink back to 1. Other seats' llama-server/replay processes under `/fast/scratch/hyaku/kama-r52/` were left untouched.

## Files

- `.ufo/waves/round-52/w1/out/J4Hardlink/c1-hardlink-c2313c3a.out` — frozen C1 receipt (exit 1).
- `.ufo/waves/round-52/w1/out/J4Hardlink/fs-check.txt` — stat/stat -f/df/EXDEV/host digest.
- `.ufo/waves/round-52/w1/out/J4Hardlink/hostlink-probe.json` — literal host-inode `/proc/<pid>/exe` probe.
- `.ufo/waves/round-52/w1/out/J4Hardlink/hardlink-member.patch` — fixture diff (`tools/kama-live-replay.py`), commit `c2313c3a` on top of `5dacf2c7`.
