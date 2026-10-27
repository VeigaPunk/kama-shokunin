# J6HostMemfd — round 53, C1 preregistered-limit probe

**Verdict: CONFIRMED.** A replay that fills the server memfd and every byte of the unpacked tree from the host's byte-identical `b11909` install — the archive only downloaded and digest-checked, no archive payload read — still gets `met=True` from the frozen C1 counter (`bind=1 sealed=1 code=1 teardown=1 newrow=1`, 3/3 runs). The preregistration's limit ("bytes, not provenance, are compared") is real, not hypothetical. A one-flipped-byte host install is refused (`met=False`, `code=0/3`), so the pass is not vacuous: the instrument's identity is exactly byte equality.

## What I built (fixture clone, never the lane)

- `S=/fast/scratch/hyaku/kama-r53/J6HostMemfd`; `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`, then `git -C $S/lane checkout -B probe c22602bd8d83ab26349d1087e916ca537ee4f9d1` (toplevel asserted `= $S/lane` before the first commit).
- Probe commit **c65c7b39f66496ce74458d18552fccf54315d579** (`probe(r53 J6HostMemfd): replay sources every byte from the host install`, 1 file, +130/−51; full diff in `probe.patch`, sha256 `ac60b53952c6…c8f0a9`). Edits, all in `tools/kama-live-replay.py` at that commit:
  - `:131` `HOST_INSTALL = "/home/vgpnk/.local/opt/llama-b11909"`.
  - `:235` `unpack_from_host(archive, into)` replaces `extract()`: the archive supplies **member names, modes and symlink targets only**; every regular member's bytes are `shutil.copyfile`d from `HOST_INSTALL`, mode from the tar header. No archive byte is written to disk or executed.
  - `:272` `_seal_stream(name, src, want, member)` = the round-52 memfd writer, factored out unchanged (hash on write, `SEALS_ALL`, re-hash of the sealed bytes).
  - `:321` `sealed_member()` keeps its archive-stream source for the selftest; `:336` `sealed_host(member, want)` fills the same sealed memfd from `open(<HOST_INSTALL>/<basename>, "rb")`, still refusing on `memfd-digest-mismatch` / `memfd-content-mismatch`.
  - `:505` `res["inputs"]["from_host"] = unpack_from_host(archive, tree)`; `:546` `own_fd, own = sealed_host(need["server.member"], want_srv)`.
  - `:629`/`:630`/`:887` selftest gets a fixture host dir built from the fake archive's own members (byte-identity preserved offline).
- `python3 -I tools/kama-live-replay.py --selftest --scratch $TMPDIR` → `KLR_SELFTEST pass=43 fail=0`, exit 0 (the rest of the tool's contract is unchanged).
- Control commit **11930992f91e71ae90765a678764c6cb536acc70**: same tree, `HOST_INSTALL` pointed at `$S/host-mut`, a copy of the install with one byte flipped in `libggml-rpc.so` at file offset `0x13000` (inside the `R E` LOAD segment `0x012000..0x031469`, i.e. a mapped executable range; `243 → 12`), digest `4b6be3e1…338d → 862522c3…66e0`.

Host install vs archive, independent of the probe: all 51 regular members of `llama-b11909-bin-ubuntu-x64.tar.gz` (sha256 `bf94332a…695b`) are byte-equal to `/home/vgpnk/.local/opt/llama-b11909/*`; `regular members=51 byte-equal-with-host=51 differ=0`; `sha256(llama-server)=35ac50fb…7ff0` equals the frozen `SERVER_SHA`.

## Frozen counter runs (counters untouched; sha256 still `1a7a1442…5d8f` C1 / `1afb8b9d…3080` C2, as frozen)

```
python3 .../kama-shokunin/tools/round53-replay-code-audit.py --repo $S/lane \
  --tip c65c7b39f66496ce74458d18552fccf54315d579 --scratch $S/c1probe --out $S/c1-probe.out
tip=c65c7b39f66496ce74458d18552fccf54315d579
bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 met=True
detail: code b1..b3: 8 archive files (8 executable ranges) byte-equal in /proc/<pid>/mem to the
  counter's own archive, 13 root-owned host files; ... ['libggml-base.so.0.27.0',
  'libggml-cpu-zen4.so', 'libggml-rpc.so', 'libggml.so.0.27.0', 'libllama-common.so.0.7.0',
  'libllama-server-impl.so', 'libllama.so.0.7.0', 'libmtmd.so.0.7.0']
detail: sealed b1..b3: running image '/memfd:llama-server (deleted)' … seals 15 is a sealed
  memfd with the frozen digest, recorded in server_exe and own_server
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 4 rows new since base; 1 name proc_pid_mem(5): ['| S506 |']
exit=0        (wall 20.4 s)
```
Same command at `--tip 11930992…` (byte-flipped host install):
```
bind=0 sealed=1 code=0 teardown=1 newrow=1 bound=0/3 sealedruns=3/3 coderuns=0/3 met=False
detail: code b1..b3: mapped bytes 7fac…-7fac… (offset 00012000) of llama-b11909/libggml-rpc.so
  differ from the archive member
detail: code b1..b3: rerun code_mappings has no entry …/libggml-rpc.so … with the archive digest
exit=1        (wall 19.4 s)
```
Both legs fire independently: the counter's own `/proc/<pid>/mem` comparison catches the mapped byte, and `verify_code`'s member digest catches the whole file.

## Proof the probe really sourced host bytes (not archive bytes)

One standalone probe replay of `.ufo/waves/round-48/c2/live/receipt-1.json` (`--work $S/rr/w`):

- `replay match=True refused=None mismatches=0 exit=0`; result (`probe-replay-summary.json`): `host_install=/home/vgpnk/.local/opt/llama-b11909`, `from_host_members=51`, `own_code.verified=true`, all 8 mapped tree libraries `mapping_sha256 == tree_sha256 == host_sha256`.
- `strace -f -y -s 0 -e trace=openat,read` of the same replay (`trace-summary.txt`):

| observation | base `c22602bd` | probe `c65c7b39` |
|---|---|---|
| `openat` of `/home/vgpnk/.local/opt/llama-b11909/…` | 0 | 51 unique (all 51 members) |
| `read()` on fd of the host `llama-server` | 0 | 3 (17,864-byte image) |
| `read()` calls / bytes on the downloaded `.tar.gz` fd | 872 / 152,151,696 | 633 / 121,025,912 |

- Cheap *metadata* side effect, measured: base tree member mtime `2026-10-26 17:52:20` (= tar header mtime); probe tree mtime `2026-10-27 03:19:57` (= copy time).

## What observation would distinguish it, and is any cheap?

1. **Byte comparison: provably cannot.** Both sources are byte-identical (51/51), so `/proc/<pid>/mem` ranges, the sealed-image hash and the member digests are all equal by construction — measured, `met=True`. No threshold or extra comparison over the same bytes separates them.
2. **Syscall-level I/O provenance: distinguishes, cheap to *run*, not adoptable inside this counter.** The trace above separates them cleanly (51 host opens + 3 host reads vs 0 + 0). Cost to run: one `strace` call, 2.9 s. Cost to adopt: the counter would have to trace the replay's descendants (ptrace/eBPF/audit), i.e. become a tracer — out of scope and against this wave's "no tracer around the counter" rule; the archive-read byte count (152 MB → 121 MB) is *not* a clean substitute because gzip forces both variants to stream the whole archive for member listing and digesting.
3. **Policy instead of observation: the cheapest sound adoption.** Run the replay under a Landlock (or seccomp) ruleset that denies read access outside the counter's scratch tree — then a host-install-sourced replay cannot read `/home/vgpnk/.local/opt/llama-b11909` and fails, while a provenance-true replay is unaffected. Unprivileged, no tracer, ≈60 lines around `start_replay()`. This is the only candidate I would put in round 54.
4. **File metadata: cheap but unsound.** A 3-line check that each mapped tree file's `mtime` equals its archive member's `mtime` would have failed *this* probe as written (data above) and passed the base. One `os.utime()` in `unpack_from_host` defeats it, so it is a heuristic, not an identity — it cannot carry the claim.

## Risks / notes

- No defect found in the frozen counter, the preregistration or the build; the probe is an answer, not a fix. Worth recording that C1's predicate sentence reads "an archive member under the replay's unpacked tree whose … bytes … equal that member's bytes" — satisfied by content identity alone, which is exactly why this probe meets.
- The docstring of `tools/kama-live-replay.py` (base `:75`, "a memfd filled from a byte-identical host install still matches") pre-announces this limit; the measurement now backs it with a run.
- The lane repo was not written to: `git -C …/kama-shokunin status --porcelain` shows only pre-existing integrator state (`M .ufo/waves/round-53/measured/*`, `M SKILL.md`, `M registry/hexrun-ledger.tsv`, `M tools/kama-live-replay.py`, `M tools/kama-llamacpp-live.py`, untracked wave dirs) that was already there; my clone and my scratch are the only trees I changed. No processes left behind (`pgrep -af "llama-server|kama-live-replay"` empty after the runs). No tool installs were needed (`strace` already present). Scratch `$S` removed after copying the receipts below.

## Files written

- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J6HostMemfd.md (this report)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J6HostMemfd/probe.patch
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J6HostMemfd/c1-probe.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J6HostMemfd/c1-mutant.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J6HostMemfd/probe-replay-summary.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J6HostMemfd/trace-summary.txt
