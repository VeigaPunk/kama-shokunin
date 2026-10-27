# X4Fresh — docstring-only replay of round-48 receipt-2 (evidence log)

Tip under test: `c22602bd8d83ab26349d1087e916ca537ee4f9d1` (round-53 build).
Scratch: `/fast/scratch/hyaku/kama-r53/X4Fresh` (removed at the end; copies in this dir).
Nothing below was read from the tools except the module docstring (via `ast.get_docstring`)
and `--help` output before the replay. No tool code was read, no counter was run.

## 1. Tools at the tip (digests of the files actually used)

```
$ cd $S/lane && git checkout -q c22602bd8d83ab26349d1087e916ca537ee4f9d1
$ git rev-parse HEAD
c22602bd8d83ab26349d1087e916ca537ee4f9d1
$ sha256sum tools/kama-live-replay.py tools/kama-llamacpp-live.py tools/kama-probe.sh
6c0bfbdfa586e0beb47a8ba1f1c617b9db295dfe4f7357299493e04989e98102  tools/kama-live-replay.py
82b253e58ae75457b3dc81e6a7450510a50f815e3503bc6a2b61b7d1342b349d  tools/kama-llamacpp-live.py
4393ab819d6a741646237ef0268cc0836988a9711bab6b06c46cbfea382964f4  tools/kama-probe.sh
```

The rerun receipt's `tool.sha256` = `82b253e5…b349d` and `probe.sha256` = `4393ab81…64f4`
prove the rerun used exactly these sibling files from the tip.

## 2. Docstring-only extraction (no code read)

```
$ python3 - "$S/lane/tools/kama-live-replay.py" <<'PY'
import ast,sys
t=ast.parse(open(sys.argv[1]).read())
print(ast.get_docstring(t, clean=False))
PY
```

and the same for `tools/kama-llamacpp-live.py`; then

```
$ python3 tools/kama-live-replay.py --help   # exit=0
$ python3 tools/kama-llamacpp-live.py --help # exit=0
```

`--help` prints no defaults for `--live` ("kama-llamacpp-live.py path") or `--probe`
("kama-probe.sh path").

## 3. Replay exactly as documented, from an empty cwd and a non-existent work dir

```
$ cd $S/replay            # empty directory
$ python3 $S/lane/tools/kama-live-replay.py \
    --receipt /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/c2/live/receipt-2.json \
    --work work --out result.json
replay match=True refused=None mismatches=0 exit=0
real 0m2.893s
exit=0
```

No `--live` was passed. `$S/replay/work/` was created by the tool; the usage line is
`kama-live-replay.py --receipt R --work DIR --out J [--live TOOL] [--timeout S]`
(kama-live-replay.py:33).

## 4. result.json (copy: result.json)

```
schema   kama-live-replay/v1
match    true
refused  null
mismatches []
notes    ['tool.sha256:1e5ea0fd…a6d2->82b253e5…b349d',
          'probe.sha256:36b64978…29d3->4393ab81…64f4']   (informational)
work     /fast/scratch/hyaku/kama-r53/X4Fresh/replay/work   (absolute)
rerun_receipt  work/rerun-receipt.json                      (relative to cwd)
own_code {"verified": true,
          "members": 8 archive members with their digests,
          "host": 13 /usr/lib paths}
inputs   archive work/download/llama-b11909-bin-ubuntu-x64.tar.gz (22,475,032 B)
         model   work/download/stories260K.gguf (1,185,376 B)
live_exit 0; live_child {"isolated": true, "env_keys": ["HOME","LANG","PATH","TMPDIR"],
                         "pdeathsig": "SIGTERM"}
```

own_code.members (8): libggml-base.so.0.27.0, libggml-cpu-zen4.so, libggml-rpc.so,
libggml.so.0.27.0, libllama-common.so.0.7.0, libllama-server-impl.so, libllama.so.0.7.0,
libmtmd.so.0.7.0 — basenames identical to the 8 non-root mapping basenames below.

## 5. Rerun receipt (copy: rerun-receipt.json)

```
schema kama-llamacpp-live/v5, outcome pass, child_pid 2610669, port 33565
code_mappings = {"read": true, "mappings": [ ... 21 entries ... ]}
  entries:          21
  root-owned (uid 0): 13   (/usr/lib/* — set-equal to own_code.host)
  non-root (uid 1000): 8   (work/server/llama-b11909/lib*.so — archive members)
  every entry: opened true, has path, dev, inode, size, sha256
server_exe {"path": "/memfd:llama-server (deleted)", "dev": "00:01", "inode": "190936",
            "seals": 15, "nlink": 0, "opened": true, "sha256": "35ac50fb…7ff0"}
teardown  returncode 0, sigterm_sent true, sigkill_sent false, port_refuses true
```

Cross-check against measured/c1-build.out at the same tip ("8 archive files … 13
root-owned host files", copy: c1-build.out): identical counts.

## 6. Lane-tree sibling files the replay needed (measured)

Recorded by the rerun receipt:

* `tools/kama-llamacpp-live.py` — the child harness; `--live` default resolved to the
  sibling of the replay script (`$S/lane/tools/kama-llamacpp-live.py`, sha 82b253e5…).
* `tools/kama-probe.sh` — probe run by the child (sha 4393ab81…); `--probe` default
  resolved to the sibling of the child.

Not recorded, proven required by removal test: extract the tip with
`git archive c22602b | tar -x -C $S/lane2`, delete `registry/endpoint-consumers.tsv`,
replay from another empty dir with the same command (no flags):

```
$ python3 $S/lane2/tools/kama-live-replay.py --receipt …/receipt-2.json --work work --out result.json
replay match=False refused=None mismatches=25 exit=1
exit=1
```

result-registry-removed.json: match false, refused null, 25 mismatches
('outcome:pass->setup-error', 'server.sha256:…->None', every check not-evaluated),
live_exit 2, own_code {"verified": false, "members": {}, "host": []}.
rerun-receipt-registry-removed.json: outcome `setup-error`,
setup_error `"registry-unreadable:/fast/scratch/hyaku/kama-r53/X4Fresh/lane2/registry/endpoint-consumers.tsv"`,
port_refusal_set [].
=> `registry/endpoint-consumers.tsv` is a hard dependency of the child, located
relative to the child's own lane root; neither docstring states this.

## 7. Docstring gaps hit (what the docstring did not give)

| # | Where | Gap | How I resolved it |
|---|-------|-----|-------------------|
| 1 | kama-live-replay.py:33 | `[--live TOOL]` shown but no default; nothing says the child sits next to the replay script, so from an empty cwd it is unclear whether `--live` is mandatory | ran without it; success proved the sibling default |
| 2 | kama-live-replay.py:33-84 | no statement that the replay needs the lane's `registry/endpoint-consumers.tsv` (only the child's `--help` mentions the file, not that it is mandatory) | removal test -> `registry-unreadable:<path>` setup-error |
| 3 | kama-live-replay.py:36 | where the rerun receipt is written and that `rerun_receipt` is relative ("work/rerun-receipt.json") while `work` is absolute | inspected work/ after the run |
| 4 | kama-live-replay.py:76-84 (Round 53) | prose only: no JSON shape for `code_mappings` (`read`, `mappings`, `opened`, `uid`, `size`) or `own_code` (`verified`, `members`, `host`) | inspected rerun-receipt.json / result.json |
| 5 | kama-live-replay.py:33-44 | stdout line `replay match=… refused=… mismatches=… exit=…` is undocumented (J is documented) | observed |
| 6 | kama-llamacpp-live.py:8-9 | `--probe` default (sibling `kama-probe.sh`) undocumented in docstring and in --help | observed rerun receipt `probe.path` |
| 7 | kama-llamacpp-live.py:8-9 | `registry/endpoint-consumers.tsv` requirement absent from the docstring; `--help` names the file but not that it is mandatory nor the `registry-unreadable` token | removal test |
| 8 | kama-llamacpp-live.py:20-63 | receipt schema section stops at v5/witness; no `code_mappings` field shape (round 53) | inspected rerun receipt |
| 9 | both | `--work` may not exist (created); docstring does not say so | observed |

## 8. Side checks

* `pgrep -af llama-server`: no process from this seat (the three matches at the time
  were peer seats' live children under J7Late, Sen2Scratch, L1).
* `git -C $S/lane status --porcelain` empty at the tip after the run (read-only use).
* Scratch removed before finishing.
