# Proposed remediations (not applied)

## C1 path-rebind bypass

**Target:** `tools/round51-replay-exe-audit.py:351-379` (`own_exe`) and `:464-498` (the observer and receipt comparisons); replay comparison at `tools/kama-live-replay.py:355-373`.

The smallest fix for the demonstrated hardlink-rebind exploit is for the counter to also capture `os.readlink(f"/proc/{pid}/exe")` and require its canonical path to equal the expected `member_path`, rejecting deleted/ambiguous paths. The existing `got == os.stat(member_path)` comparison alone proves only that the *current* replay-controlled member pathname names the running inode. It does not prove that the executable was launched through that pathname.

That readlink check closes the demonstrated decoy-path/hardlink variant, but does not prove extraction provenance if a replay overwrites the member with a byte-identical copy and executes the member path. The original stronger predicate (“the very file the replay extracted”) requires a trust boundary the replay cannot rewrite: independently extract the pinned archive in a counter-controlled, non-writable-by-replay location and require the observed executable inode to match that protected extraction. If that isolation is not provided, narrow the claim to the observable fact (frozen digest plus current member-path inode equality), and do not describe it as archive-extraction provenance.

## btrfs maps-device false negative

**Targets:** `tools/kama-llamacpp-live.py:681-713` (`model_mapping`, especially the `sdev != dev` rejection at line 710) and `tools/round51-replay-exe-audit.py:289-316` (`mapped_model`, especially the device comparison at line 308).

Compare the `/proc/<pid>/maps` device field with the mounted device for the mapped pathname from that process's `/proc/<pid>/mountinfo` (decode the mountinfo decimal `major:minor` to the maps hexadecimal form), not with `os.stat(path).st_dev`. Keep the exact mapped pathname, inode, regular-file, size, and SHA-256 checks. On this host, `/home`'s mountinfo device is `0:30` decimal, which maps to the kernel maps value `00:1e`; `os.stat()` for a file in that btrfs subvolume instead returns `00:38`. On `/fast` XFS, maps and `os.stat()` both produce `103:05`.

## Exit between mapping and executable observation

No false-pass remediation is indicated by the test: if the child exits in this window, `server_exe()` records `opened: false`, and the witness path rejects it at `hold_for_witness()` with `witness-child-exited-before-announce`; the replay also requires `server_exe.opened == true`. Preserve these fail-closed checks.
