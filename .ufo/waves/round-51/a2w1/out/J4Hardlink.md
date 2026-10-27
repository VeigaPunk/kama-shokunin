# J4Hardlink — Round 51 C1

**Verdict: the C1 `own` leg accepts a hardlink-substituted member, including the host install's exact inode; the literal host-inode probe's full C1 run was blocked by a separate btrfs model-mapping mismatch.**

## Evidence

The C1 contract is documented in `tools/round51-replay-exe-audit.py` lines 31–37 and 351–380: it compares the running `/proc/<pid>/exe` `(dev,inode)` and digest with `os.stat(<work>/server/<member>)`, then checks the rerun receipt and `own_server`. The replay verifies the extracted member's digest at `tools/kama-live-replay.py` lines 302–310, then proceeds with that path; its `own_server` check is at lines 355–367. Neither check verifies that the path still names the extracted inode or checks link count.

### Literal host-install inode probe

Environment facts:

- `stat -c '%d %i %n' /home/vgpnk/.local/opt/llama-b11909/llama-server` → device `56`, inode `238037577`.
- `sha256sum` → `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0`, the frozen C1 server digest.
- A hardlink test from that file into my assigned `out/J4Hardlink/.linktest` succeeded and reported `dev=38 ino=238037577 nlink=2 same=True`; the equivalent link into `/fast/scratch/hyaku/kama-r51/J4Hardlink` failed with `Errno 18 Invalid cross-device link`.
- Thus I ran the literal host-inode replay with `--scratch` on `/home` (device 56). The replay fixture first verified the archive member, unlinked it, then hardlinked the host install at that path (fixture patch: `probe-a-hostlink.patch`).

Saved direct replay evidence: `out/J4Hardlink/hostlink-replay-a.json` and `out/J4Hardlink/rerun-receipt-a.json`:

- `probe_hardlink`: host `/home/vgpnk/.local/opt/llama-b11909/llama-server`, `dev=00:38`, `inode=238037577`, `nlink=2`.
- `own_server`: `dev=00:38`, `inode=238037577`.
- rerun `server_exe`: `opened=true`, same dev/inode, frozen SHA-256.
- `mismatches` contained only `model-mapping:mapped-file-is-not-the-model-path`; no server-exe/member mismatch. Replay exit was 1 for that unrelated mapping mismatch.

The frozen counter was run at unpatched build commit `138af25b963450b6520794995605fa7dbbcd87e0` and host-link fixture commit `5dc84775d327330633e3995e0139cdb7f24e53cd`. Both receipts show `bind=0 own=1 teardown=1 newrow=1 bound=0/3 owned=3/3 met=False`. Each host-link own detail reports `running image 00:38:238037577 is the extracted member, recorded in server_exe and own_server`; the control reports distinct extracted-member inodes. Receipts: `out/J4Hardlink/c1-control-138af25b.out` and `out/J4Hardlink/c1-hardlink-5dc84775.out`.

### Full counter pass with an external hardlink decoy

To isolate the own-leg defect from the btrfs mismatch, a second fixture staged a byte-identical copy of the host install beside the work directory on xfs, unlinked the extracted member and hardlinked the staged copy there (`probe-b-decoy.patch`). Command:

`python3 tools/round51-replay-exe-audit.py --repo <fixture-clone> --tip 0fb4044f653d62989f991be94858318fb7bec665 --scratch /fast/scratch/hyaku/kama-r51/J4Hardlink/xfs-scratch --out <out>/c1-hardlink-decoy-0fb4044f.out`

Observed output: `bind=1 own=1 teardown=1 newrow=1 bound=3/3 owned=3/3 met=True`, exit 0. All three own details report the same decoy inode `103:05:1890860146` as “the extracted member.” This demonstrates the C1 counter can fully pass while the running file is an external, replay-staged hardlink rather than the archive extraction. Full receipt: `out/J4Hardlink/c1-hardlink-decoy-0fb4044f.out`.

### Independent btrfs limitation

On `/home` scratch, the honest control and host-link attack both failed the unchanged bind leg. The counter's map reader at `tools/round51-replay-exe-audit.py` around lines 279–347 requires the `/proc/<pid>/maps` device to equal `stat(path).st_dev`; the live tool at `tools/kama-llamacpp-live.py` lines 678–727 makes the analogous check. Observed for the same downloaded model file: maps device `00:1e`, inode equal to the path inode; `stat()` device `00:38`, same inode. `/proc/self/mountinfo` reports `/home` as btrfs mount device `0:30` (hex `00:1e`). A direct mmap probe reproduced `stat_dev=00:38 maps_dev=['00:1e']` both under `/home` and in my assigned output directory; on xfs both were `103:05`.

This explains the `bind=0/3` in both btrfs runs and prevents a truthful full counter pass for a host-inode hardlink attack on this host. The xfs decoy run establishes the counter hole end-to-end without that environmental limitation.

## Proposed fixes (not applied to lane)

- `out/J4Hardlink/fix-nlink.patch` is a minimal candidate counter patch: flag `st_nlink != 1` on the member path. I exercised this copied counter: against the xfs decoy attack it returned `bind=1 own=0 teardown=1 newrow=1`, `owned=0/3`; against the honest build it returned `bind=1 own=1 teardown=1 newrow=1`, `met=True`. Receipts: `fix-run1-decoy-nlinkfix.out` and `fix-run2-honest-nlinkfix.out`.
- **[INFERENCE]** `st_nlink == 1` alone does not prove extraction provenance: a replay could rename a separate file over the member path. The robust check is for the counter to independently obtain/extract the receipt's archive member in counter-owned scratch, then compare the observed executable inode to that counter-owned extraction (and verify its digest). The replay-controlled member path should not be the sole reference.
- `out/J4Hardlink/fix-nlink-and-mountdev.patch` contains an exploratory counter-side mount-device allowance. It was not a complete/tested fix: the replay's bundled live tool still independently rejected the btrfs mapping as `mapped-file-is-not-the-model-path`. A complete btrfs fix must consistently account for the mountinfo device in both the counter and `tools/kama-llamacpp-live.py`, while retaining inode and content-hash checks. The attempted run is recorded in `fix-run3-hostlink-bothfixes.out` and still had `bind=0 own=0`.

No lane files, frozen counters, receipts, controls, or global files were edited. Host install link count was checked after cleanup: `nlink=1`, device `56`, inode `238037577`. No J4Hardlink processes remained. All my scratch was removed. No tools installed.

## Exact fixture commands / outcomes

- C1 control and literal host-link runs are recorded in their `.out` receipts above; both exited 1 because of btrfs mapping mismatch, while `own=1` (3/3).
- C1 xfs decoy command above exited 0; `met=True`.
- Copied nlink-fix counter against decoy tip exited 1 as expected (`own=0`, 0/3); against honest build tip exited 0 (`met=True`).
- Fixture commits were confined to `/fast/scratch/hyaku/kama-r51/J4Hardlink/lane`, removed before completion. Commit IDs: host-link `5dc84775d327330633e3995e0139cdb7f24e53cd`; xfs decoy `0fb4044f653d62989f991be94858318fb7bec665`.
