# R1Old - Supersession record: round-51 C1's `own` leg at the round-52 build

**Verdict: SUPERSESSION, not harm to operability.** At `5dacf2c7` the round-51 counter reads
`own=0` because the build replaced the mechanism that leg measured (the server now runs from
a sealed anonymous memfd, not from `<work>/server/<member>`). The capability survives -
strengthened - in round-52 C1's `sealed` leg, and every pre-existing operability reading
still passes at the build. One side finding (F1): a rare, unattributable bind-leg
nondeterminism in the frozen counters, 1/13 runs at the build, 0/8 at the base.

## Environment and binding of evidence

Scratch `S=/fast/scratch/hyaku/kama-r52/R1Old`, `TMPDIR=$S`, one clone
`git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` (toplevel prints
`$S/lane`); clone HEAD `34d82600` adds only the w1 spec and the L1's receipts - `git diff
--stat 5dacf2c7 HEAD -- tools/` is empty, so the tree at `--tip 5dacf2c7` is the build.
Frozen counter bytes (from the lane, `sha256sum`):
`round50-replay-bind-audit.py ff6ac2ac…a9c5e89`, `round51-replay-exe-audit.py e5753c45…b6ee5155`,
`round52-replay-memfd-audit.py 053ff502…e1121f5` (equal to the round-52 preregistration's
`counter_sha256`). No tool was installed or changed; no lane file was written.

## The two readings asked for (commands, exits, raw output kept)

1. Round-50 bind counter, build:

```
python3 …/tools/round50-replay-bind-audit.py --repo $S/lane \
  --tip 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8 --scratch $S      # exit 0
bind=1 teardown=1 newrow=1 bound=3/3 met=True
detail: bind b1: pid 318870 port 42093 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 552000965 recorded, nonce 'kama witness a779c29fabbff5fb' round-tripped
detail: bind b2: pid 323752 port 40263 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 2027784256 recorded, nonce 'kama witness 0e1580b494659322' round-tripped
detail: bind b3: pid 328012 port 45417 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1752918461 recorded, nonce 'kama witness 102bb117e47109ee' round-tripped
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 5 rows new since base; 1 name proc_pid_maps(5): ['| S496 |']
```

2. Round-51 exe counter, build:

```
python3 …/tools/round51-replay-exe-audit.py --repo $S/lane \
  --tip 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8 --scratch $S      # exit 1
bind=1 own=0 teardown=1 newrow=1 bound=3/3 owned=0/3 met=False
detail: bind b1: pid 386265 port 43561 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1151144118 recorded, nonce 'kama witness 46e41f2f26e36e58' round-tripped
detail: own b1: own: running image dev:inode 00:01:179308 is not the replay's extracted member /fast/scratch/hyaku/kama-r52/R1Old/r51c1-sxwwn8kp/work-b1/server/llama-b11909/llama-server (103:05:482904534)
detail: own b1: own: replay own_server {'memfd': True, 'member': 'llama-b11909/llama-server', 'sha256': '35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0', 'seals': 15, 'dev': '00:01', 'inode': '179308'} does not name the observed member file
… (b2, b3 the same shape, dev 00:01:184372/180604)
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 2 rows new since base; 1 name proc_pid_exe(5): ['| S499 |']
```

Confirmed: `own=0`, `bound=3/3` (the bind leg itself is met in this run), exit 1.
The observed image and the replay's own record agree (`00:01:179308` both); they disagree
with the extracted path (`103:05`), which is exactly the build's change.

3. Same round-51 counter at the base (so the difference is the mechanism, not the host):

```
python3 …/tools/round51-replay-exe-audit.py --repo $S/lane \
  --tip 9ff76b1f763512be2f554cbbfd0b2213b63b0847 --scratch $S/base     # exit 0
bind=1 own=1 teardown=1 newrow=1 bound=3/3 owned=3/3 met=True
detail: own b1: running image 103:05:279245079 is the extracted member, recorded in server_exe and own_server
detail: own b2: running image 103:05:550440372 is the extracted member, recorded in server_exe and own_server
detail: own b3: running image 103:05:1622636249 is the extracted member, recorded in server_exe and own_server
```

4. Not asked for, run because the judgement needs it - my own run of the round-52 counter
at the same build tip (first-hand, not the L1's receipt):

```
python3 …/tools/round52-replay-memfd-audit.py --repo $S/lane \
  --tip 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8 --scratch $S/r52c1    # exit 0
bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True
detail: sealed b1: running image '/memfd:llama-server (deleted)' 00:01:174275 seals 15 is a sealed memfd with the frozen digest, recorded in server_exe and own_server
detail: sealed b2: running image '/memfd:llama-server (deleted)' 00:01:167748 seals 15 is a sealed memfd with the frozen digest, recorded in server_exe and own_server
detail: sealed b3: running image '/memfd:llama-server (deleted)' 00:01:165704 seals 15 is a sealed memfd with the frozen digest, recorded in server_exe and own_server
```

## Judgement

**Supersession.** The round-51 `own` leg conjoined two claims
(`tools/round51-replay-exe-audit.py:351-379`, `:493-498`): (1) the running image is the file
*this replay produced and verified* - the counter's own `/proc/<pid>/exe` read, the rerun
receipt's `server_exe` and the replay's `own_server` all name the same dev, inode and frozen
digest; and (2) that image is *the extracted member at `<work>/server/<member>`* - same dev
and inode as `os.stat()` of that path.

- Claim 1 is kept, unweakened, in round-52 C1 (`tools/round52-replay-memfd-audit.py:495-508`).
- Claim 2 is dropped for cause: closure D5 (`corpus/lessons/round-51-verifier-spotcheck.md`
  §6, C1) records that a byte-identical copy at the member path met the round-51 counter
  (J3CopyDecoy) and a hardlink met its own leg (J4Hardlink); rename-over was an
  `[INFERENCE]`. A path's dev/inode was never a provenance proof. The build replaces it with
  an image that has no path: `memfd_create(MFD_CLOEXEC|MFD_ALLOW_SEALING)` +
  `F_ADD_SEALS 15` (`tools/kama-live-replay.py:222-256`), exec through the inherited fd
  (`tools/kama-llamacpp-live.py:786-811`), and the counter's own reading of an anonymous,
  sealed, single-link `/memfd:` image (`tools/round52-replay-memfd-audit.py:363-395`).

Not harm, because nothing about the server got worse at the build: bind 3/3 (digest,
listener, nonce against the model's own vocabulary, tree, canary-free env, mapped model,
child_pid join, released), teardown in 0.10 s, sealed 3/3 with `/memfd:`, seals 15,
`nlink` 0. The only reading that fell is the met status of a *round-51* instrument whose
target is unreachable by construction - and the lane already records the retirement in
`SKILL.md:1552` ("the round-51 member-links case retired with the path binding") and
`SKILL.md:1557`. Nothing re-runs the round-51 counter: `grep -rn "round51-replay" tools/` hits
only its own docstring, and the wider `--include=*.md --include=*.py` hits are the round-51
lesson, the round-51 preregistration/spec/build files, the round-51 seats' scratch copies
under `.ufo/waves/round-51/a2w1/out/`, and the registry row at `SKILL.md:1530` (a
description, not an invocation), so no downstream reading breaks. Proposed bookkeeping (with a ready-to-paste paragraph) is in
`supersession-record.md`.

## F1 (finding, low severity): the frozen counters' bind failure line is unattributable, and a rare replay failure exists

In this seat's first build run of the round-51 counter, the third replay failed:

```
detail: bind b3: replay exit 1 match False refused None
bind=0 own=0 teardown=1 newrow=1 bound=2/3 owned=0/3 met=False
```
(`r51-build-flake.out`; own b3 shows the same memfd agreement as the other runs, so the
failure was the replay's own post-run comparison, not the memfd).

Why it cannot be diagnosed from the receipt: the counter prints `exit`, `match` and
`refused` but not the result JSON's `mismatches` (`tools/round51-replay-exe-audit.py:476-478`;
the same line is at `tools/round50-replay-bind-audit.py:463` and
`tools/round52-replay-memfd-audit.py:485`), and it deletes `--scratch` on exit
(`tools/round51-replay-exe-audit.py:634`), so the failing `b3.json` is gone.

Incidence, all runs this seat made at the build tip with the round-51 counter or a copy of
it: 1 failure in 13 (1 of 2 frozen-counter runs, 0 of 11 patched-copy runs); at the base
tip: 0 failures in 8. `[INFERENCE]` the mismatch is one of the rerun's own checks whose
timing depends on host load - the compared projection includes `teardown`
{returncode, sigterm_sent, sigkill_sent, port_refuses} (`tools/kama-live-replay.py:283`,
`:309`) and `teardown_graceful` requires returncode 0 (`tools/kama-llamacpp-live.py:2189-2195`) -
but this is not observed evidence and I did not reproduce it a second time.

Impact on this record: none. `own=0` reproduced in 13/13 build runs (the flake run included),
and `bind=0` there was the *other* leg of an instrument whose target is already gone. It does
matter for future reliance on the bind leg (round-50/52 counters share the code): a `met=False`
at the build can be this flake, not a regression.

Proposed fix (observability only; counters are frozen, so this is a proposal, not an edit):
print the result JSON's `mismatches` and `live_exit` in that line, and allow the scratch to
be kept (`r51diag.diff` in this directory is the exact patch I used to test it; apply the
first hunk to all three counters).

## Limits of this record

- Unexercised, preregistered: a memfd filled from the host's byte-identical install still
  meets C1, and the server's libraries still load from the extracted tree by path.
- Portability, unexercised: the build's `memfd_create` flags are `MFD_CLOEXEC|MFD_ALLOW_SEALING`
  with no `MFD_EXEC`; exec of such a memfd is allowed only while `vm.memfd_noexec` is 0
  (this host: `cat /proc/sys/vm/memfd_noexec` -> `0`, kernel 7.2.11-arch1-1). With the sysctl
  at 1 a later kernel would imply `MFD_NOEXEC_SEAL` and the exec would be denied. Not a
  defect at this tip; a residual portability risk worth a stated limit if the lane ever
  claims portability.
- The base reading here is one run (plus 7 further base runs of the patched copy, all
  `own=1`); the build reading is one clean run plus 11 further build runs, all
  `bind=1 own=0 teardown=1 newrow=1` with exit 1.

## Files written

- `kama-shokunin/.ufo/waves/round-52/w1/out/R1Old.md` (this report)
- `kama-shokunin/.ufo/waves/round-52/w1/out/R1Old/supersession-record.md`
- `…/out/R1Old/r50-build.out`, `r51-build.out`, `r51-build-flake.out`, `r51-base.out`,
  `r52c1-build.out`, `diag-build-10.out`, `diag-build-11.out`, `diag-base-6.out`,
  `diag-base-7.out`, `r51diag.py`, `r51diag.diff`
