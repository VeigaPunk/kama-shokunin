NO BYTE-SUBSTITUTION WINDOW FOUND in the proposed archive-to-exec path.

Axes: operability (time-of-check/time-of-use byte identity; provenance and execution identity).

Evidence (lane snapshot 8551ba7f2056f2465d20f5b50586978133212fe1):
- `tools/kama-live-replay.py:204-210`: `acquire()` downloads then hashes the archive and refuses unless its digest matches the receipt.
- `tools/kama-live-replay.py:360-369`: extraction and extracted member digest check follow; this path check alone would be susceptible to replacement, but it is not the executed image.
- `tools/kama-live-replay.py:397-404`: `sealed_member()` constructs the descriptor from the archive member stream, passes that same descriptor to the child, and keeps it open. At `:222-250`, member bytes are SHA-256 hashed while copied to memfd; mismatch against receipt server digest raises `Refused` before sealing/launch. Seal flags include WRITE/SHRINK/GROW/SEAL.
- `tools/kama-live-replay.py:420-437`: rerun receipt's opened `/proc/<pid>/exe` must match this replay memfd's dev/inode, digest, seals, nlink=0, and `/memfd:` path.
- `tools/kama-llamacpp-live.py:217-284`: record-time `verify_archive_member()` DOES re-read the archive. It opens once, hashes that descriptor, seeks the same descriptor, parses the archive and hashes the selected member. This is called in `main()` at `:1892-1897`; it is separate from replay's memfd source, not a later authority for execution.

Counterexample attempted: on an isolated clone, constructed archive A whose member `bin/server` contained `GOOD`; recorded A's archive hash and GOOD member digest, then atomically replaced the archive pathname with archive B containing `EVIL` before calling the actual `sealed_member(A-path, member, GOOD-digest)`. Command: `python3 -c '<inline harness importing tools/kama-live-replay.py; create tar A and tar B; os.replace(B,A); call sealed_member(A,"bin/server",sha256(GOOD))>'`. Observed: exit 1, `Refused: memfd-digest-mismatch:want=278f14e96cc67489e5c0d6cebec8a2718fb158ec656fd41fed7ecd031cd472b2:got=a4cae81b6d0480d3ab6b52a6dfb5eae63346252bd00c4df5e27fcf96851bb84e`. Therefore same-uid pathname replacement after `acquire()` is possible but does not pass the member digest gate with changed bytes. Atomic replacement during `sealed_member()` likewise cannot redirect its already-open tar descriptor; mutation of the same inode cannot alter the final accepted bytes without the strong member digest failing (and memfd becomes immutable once sealed).

Disposition: no defect; no proposed patch. The path-extracted member may differ under a same-uid race, but it is not the executable image; executed image is built from the archive stream and independently required to match the receipt and this replay's sealed memfd identity. No counter, preregistration, or lane file modified.

Scratch clone: `/fast/scratch/hyaku/kama-r52/K3Window/lane`. The attempted harness intentionally exited 1 on the expected refusal. No server started.