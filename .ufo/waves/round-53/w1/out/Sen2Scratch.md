# Round 53 · seat Sen2Scratch (lane kama) — `/tmp` independence of C1 after round-52 F1

**Verdict:** clean — no defect on this surface. Round-52 integration closed round-52 F1
(`tools/kama-probe.sh:1128` now prefers `TMPDIR` over `/tmp`; byte-identical at base
`4229ea1b` and build `c22602bd`, sha256 `4393ab81…`), and **C1 still meets with `/tmp`
read-only**: at `c22602bd`, inside a private mount namespace whose `/tmp` is genuinely
remounted `ro` (a `mktemp` in it fails `EROFS`), the counter returns
`bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 met=True`
(exit 0) — the same result as the ordinary host run. Reverting that one probe line in my
clone reopens the defect under the same read-only mount (`bind=0 … met=False`, exit 1), so
the fix is load-bearing and the read-only mount is enforced through the counter's whole
descendant tree. Neither round-53 counter nor either changed tool carries a hardcoded
`/tmp`. One caution, *not* a build defect: the round-52 bwrap watcher is not transferable to
C1 — bwrap is not setuid on this host, its user namespace shows host root as uid 65534, and
the C1 code leg fails closed on that (`code-mapping:foreign`), so a bwrap run reports
`met=False` for reasons unrelated to `/tmp`; a mount-namespace recipe that keeps real uid
semantics is delivered here.

## 1 Runs

| # | harness | tip | TMPDIR / --scratch | exit | result |
|---|---|---|---|---|---|
| 1 | host, no namespace | `c22602bd` | `$S/t-host` | 0 | `met=True`, `bound=3/3 sealedruns=3/3 coderuns=3/3` |
| 2 | `unshare -m` (root) + `setpriv` → uid 1000, `/tmp` bind + `remount,ro` | `c22602bd` | `$S/t-mntro` | 0 | **`met=True`** (`c1-mntro.out`) |
| 3 | same, `/tmp` bind left writable (control) | `c22602bd` | `$S/t-mntrw` | 0 | `met=True` (`c1-mntrw.out`) |
| 4 | round-52's `bwrap --bind / / --dev /dev --proc /proc --tmpfs /tmp --remount-ro /tmp` | `c22602bd` | `$S/t-ro` | 1 | `bind=0 code=0 met=False` — **userns artifact**, §5 |
| 5 | harness 2 again, tip = my clone's fixture commit `95d3231a` (probe fix reverted) | `95d3231a` | `$S/t-ctl-prefix-probe` | 1 | `bind=0 sealed=1 code=1 teardown=1 newrow=1 bound=0/3 met=False` |

All five: `pgrep -af 'Sen2Scratch.*llama-server'` → none after the runs, no `llama-server`
left behind (`c1-mntro-run.txt`, `c1-ctl-prefix-probe-run.txt`). `/tmp` in run 2 is
`/dev/nvme1n1p1 xfs ro,nosuid,nodev,noatime,…` in that namespace (`c1-mntro-run.txt:1`),
`TMP-READONLY (mktemp -d /tmp/r53probe.XXXXXX failed)`; the host's `/tmp` was not touched
(the remount is namespace-local).

Measured against the committed tree: `--repo $S/lane` (`git clone --shared` of the lane at
`bc8e6e7f`), `--tip c22602bd8d83ab26349d1087e916ca537ee4f9d1`; the counter extracts the tip's
tree with `git archive` (`tools/round53-replay-code-audit.py:723-731`), so the L1's
uncommitted worktree edits are not in any measurement. The clone was verified with
`git -C $S/lane rev-parse --show-toplevel` = `$S/lane` before the fixture commit; the lane
repo itself was never written (`git -C <lane> status --porcelain` unchanged by me).

## 2 Hardcoded `/tmp` audit (`grep-tmp-audit.txt`)

```
--- tools/round53-replay-code-audit.py ---            (no match)
--- tools/round53-cited-path-check.py ---             (no match)
--- tools/kama-llamacpp-live.py ---                   (no match)
--- tools/kama-live-replay.py ---
48:LIVE_ENV_KEYS (TMPDIR set to <work>/tmp), and with a parent-death signal (SIGTERM,
--- tools/kama-probe.sh (C1's operative path, unchanged file) ---
1128:  TMP_ROOT=$(mktemp -d "${KAMA_PROBE_TMPDIR:-${TMPDIR:-/tmp}}/kama-probe.XXXXXX")  # round 52 (seat Sen2Scratch): honour TMPDIR
```

`kama-live-replay.py:48` is a docstring line; the only `/tmp` literal in the whole C1 path
is the probe's documented last-resort fallback. How the scratch reaches the probe:
counter `prepare_env` pins `TMPDIR=<scratch>/tmp-<tag>`
(`tools/round53-replay-code-audit.py:496-502`), the replay pins
`TMPDIR=<work>/tmp` for the launcher (`tools/kama-live-replay.py:149-152`) and creates it
(`:471`), and the launcher passes it to the probe (`CHILD_ENV_KEYS` includes `TMPDIR`,
`tools/kama-llamacpp-live.py:126`, used at `:2149`). Note `LIVE_ENV_KEYS`
(`tools/kama-live-replay.py:122`) deliberately omits `TMPDIR`, so the pin is explicit, not
inherited.

## 3 C1 with a genuine read-only `/tmp` — met

`c1-mntro.out` (exit 0, 23 s):

```
tip=c22602bd8d83ab26349d1087e916ca537ee4f9d1
bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 met=True
detail: code b1: 8 archive files (8 executable ranges) byte-equal in /proc/<pid>/mem to the counter's own archive, 13 root-owned host files; recorded in code_mappings and own_code: ['libggml-base.so.0.27.0', 'libggml-cpu-zen4.so', 'libggml-rpc.so', 'libggml.so.0.27.0', 'libllama-common.so.0.7.0', 'libllama-server-impl.so', 'libllama.so.0.7.0', 'libmtmd.so.0.7.0']
…
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 4 rows new since base; 1 name proc_pid_mem(5): ['| S506 |']
```

This reproduces the L1's `.ufo/waves/round-53/measured/c1-build.out` leg for leg (same 8
members, same 13 root-owned host files) with `/tmp` unwritable, and the 3/3 code runs show
the server's host libraries were still seen as **uid 0** — i.e. the harness did not perturb
the ownership test at `tools/round53-replay-code-audit.py:447-450`.

Attribution on `/tmp`: run 3 (writable `/tmp`, 21 s) polled `/tmp` for `kama*`/`r53c1-*`
throughout and recorded **0** paths (`c1-mntrw-tmp-poll-uniq.txt` is empty), and run 2's
read-only mount made any such write impossible. The host-level poll in run 1 saw only
`/tmp/r53c2-lesson.md`, `/tmp/r53c2-sources.md`, `/tmp/r53c2-spans.tsv`; those are not the
C2 counter's (`tools/round53-cited-path-check.py` creates no fixed filenames; its scratch is
`tempfile.mkdtemp(prefix="r53c2-", dir=root)`, `:473`), they belong to another seat, and no
`kama*` path appeared.

## 4 Positive control: the mount bites and the fix is load-bearing

Reverting `tools/kama-probe.sh:1128` to the pre-round-52 form
(`${KAMA_PROBE_TMPDIR:-/tmp}`) in my own clone (fixture commit `95d3231a`, parent
`bc8e6e7f`; `git diff c22602bd 95d3231a` = `M tools/kama-probe.sh` plus the `.ufo/` wave
files only) and rerunning under the *same* read-only `/tmp`:

```
tip=95d3231aec3a44c0df5381fc8aafe740ee355d3e
bind=0 sealed=1 code=1 teardown=1 newrow=1 bound=0/3 sealedruns=3/3 coderuns=3/3 met=False
detail: code b1: 8 archive files (8 executable ranges) byte-equal … 13 root-owned host files
detail: bind b1: replay exit 1 match False refused None
```

`code=1` while `bind=0` localises the failure to the probe path (the round-52 signature).
Probe level (`probe-ro-tmp.txt`), same namespace, `TMPDIR` set, `/tmp` read-only:

* tip `c22602bd` probe: prints its listener table, leaves no residue under `TMPDIR`;
* pre-fix probe (`95d3231a`):
  `mktemp: failed to create directory via template '/tmp/kama-probe.XXXXXX': Read-only file system`.

So `met=True` in §3 is not vacuous: the read-only mount is enforced through the counter's
children, and the one-line round-52 fix is the mechanism that makes C1 survive a host whose
`/tmp` is unwritable.

## 5 Caution for future rounds: the round-52 bwrap watcher cannot measure C1

`bwrap --bind / / --dev /dev --proc /proc --tmpfs /tmp --remount-ro /tmp`
(the exact form recorded in `.ufo/waves/round-52/w1/out/Sen2Scratch.md:103,159`) applied to
the round-53 C1 counter yields `bind=0 sealed=1 code=0 teardown=1 newrow=1 met=False`
(`c1-bwrap-ro.txt`, exit 1, 19 s), with 39 detail lines of the form

```
detail: code b1: code: executable mapping /usr/lib/libzstd.so.1.5.7 (00:1e 8527) is neither an archive file under the unpacked tree nor a root-owned host file (uid 65534, 00:20 8527, writable False)
```

Cause: `/usr/bin/bwrap` is not setuid here (`-rwxr-xr-x root root`), so bubblewrap always
creates a user namespace; inside it the caller's uid is mapped and host root is unmapped,
hence uid 65534. Both ownership tests then fail closed — the counter's host-file test
(`tools/round53-replay-code-audit.py:447-450`) and the replay's own
`code-mapping:foreign:{path}:uid=`
(`tools/kama-live-replay.py:348`, reached from `verify_code` at `:308-353`), which makes the
replay exit 1 and so the bind leg 0. Round-52's counter had no ownership leg, which is why
the same harness was valid then. **This is a harness limitation, not a counter or build
defect**; nothing in §3 depends on it.

Replacement recipe (delivered as `c1-mountns.sh`; used for runs 2, 3 and 5):

```sh
sudo -n unshare -m sh -c "mount --bind /tmp /tmp && mount -o remount,ro,bind /tmp && \
  exec setpriv --reuid=1000 --regid=1000 --init-groups sh <scratch>/c1-ns-tip.sh <label> <tip>"
```

A private mount namespace owned by root, `/tmp` remounted `ro` inside it only, privileges
then dropped to the operator uid — no user namespace, so `/usr/lib` stays uid 0, the `/proc`
view and Yama scope 1 are the host's (no tracer is involved), and the counter's own
`/proc/<pid>/mem` reads are unaffected. Drop the `remount,ro` for the read-write control.

## 6 Boundary observations (not defects, no action requested)

1. `tools/kama-probe.sh:1128` still falls back to `/tmp` when neither `KAMA_PROBE_TMPDIR` nor
   `TMPDIR` is set, so an operator running the probe by hand on a host with a read-only
   `/tmp` still fails (`probe-ro-tmp.txt`). Inside C1 that path is unreachable because the
   replay always pins `TMPDIR`; this is the documented last resort, not F1 reopened.
2. `tools/kama-llamacpp-live.py:2170` creates the server log with
   `tempfile.mkstemp(prefix='kama-llamacpp-live-', suffix='.log')` and no `dir=`, so it
   follows `tempfile.gettempdir()`; the tool has no `--scratch` of its own. It is scratch-clean
   under C1 only because the replay pins `TMPDIR=<work>/tmp` (`kama-live-replay.py:151`,
   `:471`). A direct live-tool run with no `TMPDIR` on a read-only `/tmp` would fail at
   `log-mkstemp-failed` (`:2173`) — outside C1's predicate, and not observed here.
3. Attribution caveat: an interleaved read-write run on this shared host cannot distinguish
   my `/tmp` writes from other seats' by polling alone (run 3's poll held 27,688 host
   entries); the decisive evidence is run 2, where `/tmp` is read-only for the whole tree.
4. The lane worktree was dirty while I measured (L1 edits to `tools/kama-live-replay.py`,
   `tools/kama-llamacpp-live.py`, `SKILL.md`, `registry/hexrun-ledger.tsv`,
   `.ufo/waves/round-53/measured/c1-build.out`, …); every number here comes from
   `git archive c22602bd`, i.e. the committed build.

## 7 Reproduction

```sh
S=/fast/scratch/hyaku/kama-r53/Sen2Scratch; mkdir -p "$S"; export TMPDIR="$S"
git clone -q --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
# read-only /tmp, real uid (the decisive run)
sudo -n unshare -m sh -c "mount --bind /tmp /tmp && mount -o remount,ro,bind /tmp && \
  exec setpriv --reuid=1000 --regid=1000 --init-groups sh $S/c1-ns-tip.sh mntro c22602bd8d83ab26349d1087e916ca537ee4f9d1"
# control with the probe fix reverted (fixture commit, my clone only)
sed -i 's|${KAMA_PROBE_TMPDIR:-${TMPDIR:-/tmp}}|${KAMA_PROBE_TMPDIR:-/tmp}|' "$S/lane/tools/kama-probe.sh"
git -C "$S/lane" rev-parse --show-toplevel        # must print $S/lane
git -C "$S/lane" -c user.name=fx -c user.email=fx@invalid -c commit.gpgsign=false commit -qam fixture
sudo -n unshare -m sh -c "mount --bind /tmp /tmp && mount -o remount,ro,bind /tmp && \
  exec setpriv --reuid=1000 --regid=1000 --init-groups sh $S/c1-ns-tip.sh ctl-prefix-probe 95d3231aec3a44c0df5381fc8aafe740ee355d3e"
```

Tools installed: none (existing `sudo`, `unshare`, `setpriv`, `bwrap 0.13.1`; no pacman, no
network installs). Scratch `/fast/scratch/hyaku/kama-r53/Sen2Scratch` removed after the
evidence was copied.

## 8 Artifacts (`kama-shokunin/.ufo/waves/round-53/w1/out/Sen2Scratch/`)

`c1-host.{txt,out}`, `c1-host-run.txt`, `c1-host-tmp-poll-uniq.txt`;
`c1-mntro.{txt,out}`, `c1-mntro-run.txt`; `c1-mntrw.{txt,out}`, `c1-mntrw-run.txt`;
`c1-bwrap-ro.{txt,out}`, `c1-bwrap-ro-run.txt`; `c1-ctl-prefix-probe.{txt,out}`,
`c1-ctl-prefix-probe-run.txt`; `probe-ro-tmp.txt`; `grep-tmp-audit.txt`;
drivers `c1-ns-tip.sh`, `c1-ns-run.sh`, `c1-host-run.sh`, `c1-mountns.sh`; `SHA256SUMS`.
