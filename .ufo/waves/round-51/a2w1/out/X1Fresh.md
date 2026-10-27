PASS with a reporting defect: the docs-only round-48 replay matched and verified the replay's own server image, but an unwritable `--out` path turns a completed match into an uncaught exit 1.

## Fresh-session replay evidence

Using the `kama-live-replay.py` module docstring's Usage and witness instructions, I ran:

```sh
S=/fast/scratch/hyaku/kama-r51/X1Fresh
export TMPDIR="$S"
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-live-replay.py \
  --receipt /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/c2/live/receipt-2.json \
  --work "$S/work" --out "$S/result.json" --witness-dir "$S/wd"
```

I created `work` and `wd`, watched for `wd/ready.json`, read it, then created `wd/release` as directed. Exit **0**; stdout: `replay match=True refused=None mismatches=0 exit=0`. The captured ready file was `{"schema":"kama-live-witness/v1","port":36409,"pid":863942,"written_utc":"2026-10-27T03:48:05.752Z"}`. Result JSON: `match=true`, `refused=null`, `mismatches=[]`, `live_exit=0`; all 11 rerun checks passed. There was one informational `tool.sha256` note; the match remained true.

Requested fields (the result JSON's `own_server` is top-level; `server_exe` is in `work/rerun-receipt.json`):

- `match`: **true**.
- `server_exe`: `opened=true`, `dev="103:05"`, `inode="1956521979"`, `sha256="35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0"`.
- `own_server`: `{"path":"/fast/scratch/hyaku/kama-r51/X1Fresh/work/server/llama-b11909/llama-server","dev":"103:05","inode":"1956521979"}`.
- The original receipt's `server.sha256` is the same `35ac50fb…d7ff0`. `os.stat` of the extracted member gave inode `1956521979` and `st_dev=66309` (`0x10305`, major/minor 259:5); thus the recorded `dev="103:05"` is hexadecimal encoding, not the ordinary decimal major/minor rendering. The equal extracted-member inode, `opened=true`, and equal SHA provide observed evidence for the new server-executable check.

A second witnessed replay held release for 8 seconds: while held, no result JSON existed and the replay/server processes were alive; after release it exited 0 with `match=true`, 0 mismatches, `released=true`, `waited_ms=8175`. A no-release replay with `--witness-timeout 2` exited 0 after `waited_ms=2012`, with `released=false`, `orphaned=false`, and `match=true`. With the default timeout, no-release took 123 seconds and also exited 0/matched; the receipt recorded `waited_ms=120041`, `released=false`, `orphaned=false`. `--help` shows default 120 seconds, but the module docstring does not.

## What the docstring did and did not tell me

| Field / step | Could I tell from the docstring alone? |
|---|---|
| `match` | Yes: the comparison is described and exit 0 means the rerun matches. |
| `server_exe.opened` and `.sha256` | Mostly: the docstring states that the rerun must record an opened image and the receipt's server SHA. It does not say where in the artifacts to find it. |
| `server_exe.dev` / `.inode` | The intended object (the replay's extracted member) is stated; the encoding and string representation are not. The observed `dev` is hex-formatted. |
| `own_server` | The name is mentioned, but neither its top-level result-JSON location nor its `{path, dev, inode}` shape is included in the documented result key list. |
| Witness handoff | The docstring says to read `<dir>/ready.json` and create `<dir>/release`; it gives `{port,pid}`. It omits the actual ready-file's `schema`/`written_utc`, the witness block's shape, and the default wait. |

Other undisclosed operational details observed:

- `--witness-dir` must already exist: with it absent, the tool refused before running, exit 2, `error: --witness-dir must be an existing directory` (implementation check at `tools/kama-live-replay.py:621-622`). The module docstring did not state this; `--help` does. Conversely, an absent `--work` was created automatically (`:291`), also unstated.
- The documented result key list (`:33-35`) omits actual keys `live_child`, `witness_dir`, `live_exit`, and `own_server`; it describes `rerun_receipt` without saying that its value is a path to a separate receipt. `server_exe` must be read from that rerun receipt, not the result JSON.
- On completion, `ready.json` was removed; the witness directory retained only my `release` file. I used an empty file (`touch`); whether contents matter or a stale release pre-releases a run was not tested.
- `--out`'s parent directory must exist. This is not stated in the docstring or help.

## Defect: failed result write violates documented exit contract

I ran the same replay with a fresh absent `--work` and `--out "$S/nodir3/result3.json"`, where `nodir3` did not exist; I did create the required witness directory and released it. The replay produced `work3/rerun-receipt.json` with 11/11 checks passing. Offline comparison of the original receipt and that rerun receipt exited 0 and printed `compare match=True mismatches=0`. Yet the replay process exited **1** with an uncaught `FileNotFoundError` at `tools/kama-live-replay.py:629` (`with open(a.out, "w") as fh:`); it never wrote the result JSON or the usual summary line. The module contract assigns exit 1 to “it ran and differs” and exit 2 to “could not run.” This was a successful match that could not write its required output, so exit 1 misstates the outcome and discards the result. Exact traceback and compare output are copied in the evidence directory.

Proposed fix (not applied; exact unified diff): `.../a2w1/out/X1Fresh/kama-live-replay-out-write.patch`. It catches `OSError` while writing `--out`, reports the error, and returns 2, preserving the documented distinction between mismatch and inability to complete output.

## Cleanup and retained evidence

A post-run `pgrep -af llama-server` once showed peer servers in `N2Couple` and `J4Hardlink`; I left them untouched. After copying evidence and removing my scratch, the final `pgrep -af llama-server` and `pgrep -af '/fast/scratch/hyaku/kama-r51/X1Fresh'` both returned exit 1 (no matches). No tools were installed. Scratch `/fast/scratch/hyaku/kama-r51/X1Fresh` was removed.

Raw result/receipt copies, captured ready JSON, command logs, probe transcript, curated evidence JSON, and the proposed patch are in `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/X1Fresh/`.
