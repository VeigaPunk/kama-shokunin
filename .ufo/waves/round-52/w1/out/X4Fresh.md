# X4Fresh — Round 52 fresh-session replay (lane kama, operability)

**Verdict: PASS on the replay itself, FAIL on "docstring only" — a fresh session reproduces round-48 receipt-2 with `match=true` and the rerun server image is this replay's own sealed memfd, but only after supplying lane-tree siblings the docstring never mentions; the literal first attempt refused (exit 2) and two partial attempts exited 1 with 24–31 mismatches.**

Seat rule honoured: I read **only** the module docstring (extracted with `ast`, saved as `docstring.txt`) and `--help` (`help.txt`) of `tools/kama-live-replay.py` at build commit `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`; no source was read. Tool hashes at that commit:

```
9c11b2fbc77bd73e628b9870736f804c6b6be897ec59ca45ac16a81edafe7233  tools/kama-live-replay.py
424b7808b3f897dd148f7a190dffb72159f9d0fa3ad75d9bfebad8be3bdad50a  tools/kama-llamacpp-live.py
```

## 1. Required values

Result JSON `out-8-documented-default.json` (the documented usage, no `--live` override):

```json
"match": true, "refused": null, "mismatches": [], "exit": 0
"own_server": {"memfd": true, "member": "llama-b11909/llama-server",
               "sha256": "35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0",
               "seals": 15, "dev": "00:01", "inode": "165707"}
```

Rerun receipt `rerun-receipt-default.json`:

```json
"server_exe": {"dev": "00:01", "inode": "165707", "nlink": 0, "opened": true,
               "path": "/memfd:llama-server (deleted)", "seals": 15,
               "sha256": "35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0",
               "size": 17864}
```

`server_exe.dev/inode` equals `own_server.dev/inode`; the image has **no path** — the
extracted member still exists at `work8/server/llama-b11909/llama-server` with sha256
`35ac50fb…d7ff0`, `nlink=1 mode=755 size=17864`, and is byte-identical to what runs,
yet it is not the running image. A second run (explicit `--live`, `out-4-match.json` /
`rerun-receipt.json`) produced the same result with a **different** memfd inode
(`183423`), again equal in `own_server` and `server_exe` — the binding is per-run, not
to the member path.

## 2. Exact procedure that reproduced it

```bash
S=/fast/scratch/hyaku/kama-r52/X4Fresh; export TMPDIR="$S"
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
mkdir -p "$S/atbuild" && git -C "$S/lane" archive 5dacf2c7… tools registry | tar -x -C "$S/atbuild"
mkdir "$S/work8"; cd "$S/atbuild"
python3 tools/kama-live-replay.py \
  --receipt /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/c2/live/receipt-2.json \
  --work "$S/work8" --out "$S/out8.json"
# replay match=True refused=None mismatches=0 exit=0      (3.97 s wall)
```

Rerun receipt: schema `kama-llamacpp-live/v5`, outcome `pass`, port 33779,
`port_listener_ownership="child"`, teardown `returncode=0 sigterm_sent=true
sigkill_sent=false port_refuses=true`, all 10 checks evaluated and passed,
`model_mapping.mapped=true` with sha256 `270cba1b…d256d`.
`notes` holds one informational line: `tool.sha256:1e5ea0fd…9a6d2->424b7808…ad50a`
(round-48 live tool vs the build's) — a match with a newer live tool, as the docstring
says notes are informational (line 37-38).

## 3. Where the docstring was not enough

All line citations are the committed file's line numbers at 5dacf2c7 (`docstring.txt`).

| # | Gap | Proof (command → result) |
|---|---|---|
| 1 | **The live child is not self-contained.** Lines 9, 79-81 say "runs tools/kama-llamacpp-live.py" and "Deps: python3 stdlib"; nothing says that tool needs `<its dir>/kama-probe.sh` and `<parent dir>/registry/endpoint-consumers.tsv`. | `--live <copy>/kama-llamacpp-live.py` in a dir without the probe → exit **1**, 31 mismatches, `rerun.setup_error="probe-not-found:<dir>/kama-probe.sh"` (`out-2-no-probe.json`). With `tools/` present but no `registry/` → exit **1**, 24 mismatches, `setup_error="registry-unreadable:<root>/registry/endpoint-consumers.tsv"` (`out-3-no-registry.json`). |
| 2 | **`--live`'s default is undocumented** (line 33 shows it optional, no default). It resolves to `<dir of this script>/kama-llamacpp-live.py`. | A lone copy of the tool run from an empty dir → exit **2**, `refused="no-rerun-receipt:exit=2:/usr/bin/python3: can't open file '<cwd>/kama-llamacpp-live.py': [Errno 2] No such file or directory"` (`out-1-defaultlive-refused.json`). The docstring's "fresh session can re-run it" (line 4) holds only for a tree, not for the downloaded file. |
| 3 | **"Could not run" is not exit 2 in practice.** Lines 39-40 lump "or could not run" under exit 2; a live child that starts and fails setup yields a receipt, so the replay exits **1** with a mismatch list. | Gaps 1 above: exit 1, 24/31 mismatches, `outcome:pass->setup-error` as the first mismatch. |
| 4 | **JSON key list incomplete.** Lines 36-38 list schema/receipt/work/rerun_receipt/match/refused/mismatches/notes/inputs; observed extras `own_server`, `live_child`, `live_exit`. `own_server` is described in prose (line 71) but absent from the J list — and it is one of the three values this seat must report. | `out-8-documented-default.json` keys: `own_server`, `live_child` (`{"isolated":true,"env_keys":["HOME","LANG","PATH","TMPDIR"],"pdeathsig":"SIGTERM"}`), `live_exit` (0). |
| 5 | **Refusal strings are undocumented and do not match the round-52 text.** Line 68 advertises `memfd-digest-mismatch`; a receipt-level digest tamper is caught earlier. | Zeroing `server.sha256` only → exit 2, `refused="provenance-verified-member_sha256-differs"` (`out-6`). Zeroing `server.sha256` **and** `provenance.verified.member_sha256` → exit 2, `refused="member-digest-mismatch:want=0000…:got=35ac50fb…d7ff0"`, `rerun_receipt=null` (`out-7`): the member check happened before any memfd fill, so `memfd-digest-mismatch` was not reachable from a receipt. [INFERENCE from docstring ordering + these two refusals; code not read.] |
| 6 | **`--work` creation undocumented.** Line 6 says downloads go into `--work`; it is created if absent, nested paths included. | `--work "$S/work5/nested"` (nonexistent) → exit 0, `match=true` (`out-5-work-autocreated.json`). |
| 7 | **`--timeout` default unstated** (line 41; `--help` prints no default) and the Usage block (32-35) omits `--witness-dir/--witness-timeout` that lines 42-45 document. | `help.txt` lines 12-16: `--receipt/--work/--out/--live/--timeout` printed with no default (`--witness-timeout` alone shows "default 120", line 26-27); witness flags appear only in `--help`, not in the docstring Usage. |

Concrete fixes for gaps 1-7 are drafted in `proposed-docstring-additions.md` (not applied;
lane is read-only for this seat).

## 4. Documented surfaces that did work

- `--compare` offline: `--compare receipt-2.json work4/rerun-receipt.json` →
  `compare match=True mismatches=0`, exit 0 (line 76-78 contract).
- Refusals happen before execution: both tampered receipts left `rerun_receipt=null`;
  `pgrep -x llama-server` showed no server binary left after any run (the only
  `llama-server`-matching process on the host was another seat's `fake-live.py`).
- Round-52 memfd facts held: `seals=15`, `nlink=0`, `/memfd:` path, digest equal to the
  receipt's `server.sha256`, dev/inode equal to `own_server`, per-run inode (165707 vs
  183423 in two runs).
- Isolation facts recorded as documented: `live_child.isolated=true`, env keys exactly
  HOME/LANG/PATH/TMPDIR, `pdeathsig=SIGTERM`.

## 5. Limits of this evidence

- One receipt (`receipt-2.json`, v5), one host, loopback only; `--witness-dir`,
  `--selftest` and `--timeout` behaviour were not exercised.
- I did not read the tools' source, so every statement above is what the result JSONs and
  receipts show; the one inference is marked.
- Scratch `/fast/scratch/hyaku/kama-r52/X4Fresh` was removed after copying artifacts;
  artifacts here are authoritative copies.
- Tool installs: none (no pacman, no uv/npx).

## 6. Files written

- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X4Fresh.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X4Fresh/docstring.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X4Fresh/help.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X4Fresh/out-1-defaultlive-refused.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X4Fresh/out-2-no-probe.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X4Fresh/out-3-no-registry.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X4Fresh/out-4-match.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X4Fresh/out-5-work-autocreated.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X4Fresh/out-6-tampered-server-sha.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X4Fresh/out-7-tampered-member-sha.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X4Fresh/out-8-documented-default.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X4Fresh/rerun-receipt.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X4Fresh/rerun-receipt-default.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X4Fresh/proposed-docstring-additions.md
