# X4Fresh — fresh-session replay (round 53, kama lane)

**Verdict: PASS on the replay itself — docstring-only replay of round-48 `receipt-2.json` at tip `c22602bd8d83ab26349d1087e916ca537ee4f9d1` gives `match=true`, `refused=null`, `own_code.verified=true` (8 archive members, 13 root-owned host files), rerun `code_mappings` 21 entries / 13 root-owned — but the docstrings are insufficient as the spec of a fresh session: they omit three mandatory lane-tree siblings (`tools/kama-llamacpp-live.py`, `tools/kama-probe.sh`, `registry/endpoint-consumers.tsv`), do not say where the rerun receipt lands, and give no JSON shape for `code_mappings`/`own_code`.**

Inputs: tip `c22602bd8d83ab26349d1087e916ca537ee4f9d1`; tool digests at the tip
`tools/kama-live-replay.py` 6c0bfbdf…988102, `tools/kama-llamacpp-live.py` 82b253e5…b349d,
`tools/kama-probe.sh` 4393ab81…64f4. Only module docstrings (extracted with
`ast.get_docstring`) and `--help` were read before the run; no tool code was read and no
counter was run. Scratch `/fast/scratch/hyaku/kama-r53/X4Fresh` (removed).

## Evidence

**Replay command and result** (empty cwd `$S/replay`, non-existent `work`, no flags):

```
$ python3 $S/lane/tools/kama-live-replay.py \
    --receipt /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/c2/live/receipt-2.json \
    --work work --out result.json
replay match=True refused=None mismatches=0 exit=0
exit=0        (2.9 s; archive 22,475,032 B + model 1,185,376 B downloaded and digest-checked)
```

`result.json` (`result.json` here): `match=true`, `refused=null`, `mismatches=[]`, notes
only `tool.sha256`/`probe.sha256` differences (informational, receipt 1e5ea0fd…/36b64978…,
rerun 82b253e5…/4393ab81…), `live_exit=0`. `own_code = {verified: true, members: 8,
host: 13}`; the 13 `host` paths are set-equal to the `uid==0` mappings
(`/usr/lib/{ld-linux-x86-64.so.2, libbrotli*, libc, libcrypto, libgcc_s, libgomp, libm,
libssl, libstdc++, libz, libzstd}`), and the 8 member basenames equal the `uid==1000`
mapping basenames (`libggml-base.so.0.27.0, libggml-cpu-zen4.so, libggml-rpc.so,
libggml.so.0.27.0, libllama-common.so.0.7.0, libllama-server-impl.so, libllama.so.0.7.0,
libmtmd.so.0.7.0`).

**Rerun receipt** (`rerun-receipt.json` here; `$S/replay/work/rerun-receipt.json`,
named by `result.json:rerun_receipt` as the relative `work/rerun-receipt.json`):
schema `kama-llamacpp-live/v5`, `outcome=pass`, `child_pid=2610669`, `port=33565`,
`server_exe` path `/memfd:llama-server (deleted)` dev `00:01` inode `190936` seals 15
nlink 0 sha `35ac50fb…7ff0`, `teardown.returncode=0`, `sigterm_sent=true`,
`port_refuses=true`.
`code_mappings = {read: true, mappings: [21 entries]}`: **21 entries, 13 root-owned
(`uid==0`, the /usr/lib files), 8 `uid==1000` (the archive libraries under
`work/server/llama-b11909/`)**, each with `path, dev, inode, size, sha256, opened=true`.
This matches the lane's build receipt `.ufo/waves/round-53/measured/c1-build.out`
(`8 archive files … 13 root-owned host files`; copy `c1-build.out` here).

**Sibling files the replay needed** (this is where the docstring stops short):
1. `tools/kama-llamacpp-live.py` — the child; `--live` default resolved to the script's
   sibling (`result.json` notes; receipt `tool.path`, sha `82b253e5…`).
2. `tools/kama-probe.sh` — probe; default resolved beside the child (receipt
   `probe.path`, sha `4393ab81…`).
3. `registry/endpoint-consumers.tsv` — mandatory but named only in the child's `--help`,
   not in either docstring. Proven by removal: `git archive c22602b | tar -x -C $S/lane2`,
   delete that file, rerun the identical command → `replay match=False refused=None
   mismatches=25 exit=1`, `live_exit=2`, rerun receipt `outcome=setup-error`,
   `setup_error="registry-unreadable:…/lane2/registry/endpoint-consumers.tsv"`,
   `port_refusal_set=[]`, `own_code={verified:false,members:{},host:[]}`
   (`result-registry-removed.json`, `rerun-receipt-registry-removed.json` here).
No other lane file was touched to complete the replay.

**Docstring gaps hit** (each cost an extra probe, none required reading code):
- `tools/kama-live-replay.py:33` — `[--live TOOL]` with no default and no statement that
  the child is the sibling of the replay script; from an empty cwd it is unclear whether
  the flag is required or the sibling path is needed.
- `tools/kama-live-replay.py:33-84` — nowhere says the replay's dependency closure is the
  lane tree (`registry/endpoint-consumers.tsv` mandatory).
- `tools/kama-live-replay.py:36` — `Writes J` does not say the rerun receipt is
  `<work>/rerun-receipt.json`, nor that `rerun_receipt` is relative to the invocation cwd
  while `work` is absolute.
- `tools/kama-live-replay.py:76-84` (Round 53) — prose only; no field shape for
  `code_mappings` (`read`, `mappings[].{path,dev,inode,uid,size,sha256,opened}`) or
  `own_code` (`verified`, `members`, `host`). A fresh session must open the outputs to
  answer "how many entries, how many root-owned".
- `tools/kama-live-replay.py:33-44` — the stdout line `replay match=… refused=…
  mismatches=… exit=…` is undocumented (only `J` is).
- `tools/kama-llamacpp-live.py:8-9` — the `--probe` default (`kama-probe.sh` beside the
  script) is undocumented in both docstring and `--help`.
- `tools/kama-llamacpp-live.py:8-9` — the `registry/endpoint-consumers.tsv` requirement is
  absent from the docstring; `--help` names the file without saying it is mandatory or
  that its absence is `registry-unreadable:<path>` (exit 2, setup-error receipt).
- `tools/kama-llamacpp-live.py:20-63` — receipt schema section stops at v5/witness; no
  `code_mappings` shape for round 53.
- Minor: `--work` need not exist (created); docstring does not state it.

## Defect and proposed fix

Defect: documentation/operability gap, not a counter or replay defect —
`tools/kama-live-replay.py` (module docstring, lines 33-36 and 76-84) and
`tools/kama-llamacpp-live.py` (lines 8-9 and 20-63) do not state the sibling dependency
closure, the rerun-receipt location, or the round-53 field shapes; the exact command that
shows it is the registry-removal replay above. Proposed fix (unified diff, verified with
`patch -p1 --dry-run`, exit 0, and both patched files compile):

`docstring-gap-fix.diff` in this directory (adds a `Requires, beside this script:` block,
the rerun-receipt location sentence, `code_mappings`/`own_code` shapes, and the child's
probe/registry requirements + round-53 shape).

## Risks / blockers

- None blocking. The replay is reproducible from an empty cwd with no flags **only while
  the tools stay inside a full lane checkout**; a copy of just the two scripts fails with
  `registry-unreadable` (measured).
- Peer seats' live children were running during the replay (J7Late, Sen2Scratch, L1 under
  `/fast/scratch/hyaku/kama-r53/…`); no process of this seat remained (`pgrep -af
  llama-server` shows none under X4Fresh) and nothing in the lane tree was modified.

## Files written (absolute)

- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X4Fresh.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X4Fresh/evidence.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X4Fresh/result.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X4Fresh/rerun-receipt.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X4Fresh/result-registry-removed.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X4Fresh/rerun-receipt-registry-removed.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X4Fresh/receipt-2.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X4Fresh/c1-build.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X4Fresh/docstring-gap-fix.diff
