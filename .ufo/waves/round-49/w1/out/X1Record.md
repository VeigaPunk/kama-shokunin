# X1Record — path regression: new v5 receipt, real b11909 archive, replay, witnessed record

Verdict: **no regression found.** A new v5 receipt recorded with the round-49 live tool against the real
b11909 archive passes with 11/11 checks, the record-time member-size bound accepts the real member, the
receipt replays with `match=True` (exit 0), and a second record with `--witness-dir` was observed from
outside (frozen exe digest, pid-owned LISTEN socket, frozen `-m` model, nonce round-trip through
/tokenize + /detokenize) and torn down.

Lane tools are unchanged since the build commit, and the digests that ran equal the digests in the
build commit:

```
$ git diff --stat 74558c71c38ceaeace15fd4cf8aa9d84977584b1 HEAD -- tools/ corpus/SOURCES.md   # empty, exit 0
$ git show 74558c71:tools/kama-llamacpp-live.py | sha256sum
72e76079995c5ba8269bbaa31e30b8c15c5e503de2a58e603b78561424bffd4c  -
$ git show 74558c71:tools/kama-live-replay.py | sha256sum
636074f9628f8c6106a0b5508dd7a15e8d677ea89cfbe0cd2a665f85ddd1e01a  -
```
(`receipt-record.json` records `tool.sha256 = 72e7607…`, i.e. the tool that recorded is the build-commit tool.)

## 1. Inputs acquired and pinned (scratch, then removed)

```
$ curl -sSL -o llama-b11909-bin-ubuntu-x64.tar.gz https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz
$ curl -sSL -o stories260K.gguf https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf
bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b  llama-b11909-bin-ubuntu-x64.tar.gz   (22475032 B)
270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d  stories260K.gguf                     (1185376 B)
```
Both match the frozen digests (asset bf94332a…, model 270cba1b…). The archive is a regular file of
22 MiB with 62 index entries — well inside `ARCHIVE_MAX_BYTES` / `MEMBER_MAX_COUNT`
(`tools/kama-llamacpp-live.py:212-274`).

## 2. Size check accepts the real member

`--server` was the host install `/home/vgpnk/.local/opt/llama-b11909/llama-server`
(member `llama-b11909/llama-server`).

```
$ tar -tvzf llama-b11909-bin-ubuntu-x64.tar.gz | grep 'llama-b11909/llama-server$'
-rwxr-xr-x runner/runner   17864 2026-10-26 17:52 llama-b11909/llama-server
$ stat -c '%s' /home/vgpnk/.local/opt/llama-b11909/llama-server
17864
$ sha256sum /home/vgpnk/.local/opt/llama-b11909/llama-server
35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0
```
Declared member size == `--server` file size (17864), member is a regular non-sparse file
(`st_blocks=40`, `nlink=1`), so the new `provenance-member-size-mismatch` / `-member-sparse` tokens
(`tools/kama-llamacpp-live.py:258-263`) do not fire. Called directly (importlib, read-only):

```
$ python3 -c "import importlib.util; ... verify_archive_member(arc, bf94332a…, 'llama-b11909/llama-server', 35ac50fb…, server_size=17864)"
verify_archive_member_ok ('bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b',
                          '35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0')
exit 0
```

## 3. New v5 receipt: pass, 11 checks

```
$ TMPDIR=$S/tmp python3 kama-shokunin/tools/kama-llamacpp-live.py \
    --server /home/vgpnk/.local/opt/llama-b11909/llama-server \
    --model $S/dl/stories260K.gguf --model-sha256 270cba1b… \
    --alias kama-r49-record --ctx 256 --threads 1 \
    --server-asset-url https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz \
    --server-asset-sha256 bf94332a… --server-member llama-b11909/llama-server \
    --model-url https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf \
    --server-archive $S/dl/llama-b11909-bin-ubuntu-x64.tar.gz \
    --out $S/receipt-record.json
EXIT=0
```
`out/receipt-record.json` (copied): `schema kama-llamacpp-live/v5`, `outcome pass`, `witness null`,
port 42935, `port_listener_ownership child`, all 11 checks `evaluated=True passed=True`:
`health_ready, models_alias_id, models_owned_by_llamacpp, metrics_not_enabled, props_alias,
probe_model_ok, probe_mismatch, teardown_graceful, teardown_port_closed, loading_envelope_graded,
model_unchanged`. `loading_observed=True`, `loading_envelope_exact=True` (21 × 503 repeats), probes
expect-match exit 0 and expect-mismatch exit 2, `teardown {returncode 0, sigterm_sent true,
sigkill_sent false, port_refuses true}`, `model_sha256_post == model.sha256`, and

```
provenance.verified = {at: record, archive_sha256: bf94332a…, member_sha256: 35ac50fb…, model_sha256: 270cba1b…}
```
The `at: record` block is the proof that the bounded member verification ran and accepted the real
archive before the server started (`tools/kama-llamacpp-live.py:212-274`, called from the v5 setup path).

## 4. The new receipt replays

```
$ TMPDIR=$S/tmp python3 kama-shokunin/tools/kama-live-replay.py \
    --receipt $S/receipt-record.json --work $S/replay --out $S/replay-result.json
replay match=True refused=None mismatches=0 exit=0
EXIT=0
```
`out/replay-result.json`: `match true, mismatches [], notes [], live_exit 0`; inputs archive
bf94332a…, model 270cba1b…, extracted member `$S/replay/server/llama-b11909/llama-server`.
`out/rerun-receipt-unwitnessed.json`: v5, `outcome pass`, 11/11 evaluated and passed,
`provenance.verified` present with the same three digests, own `child_pid 316112`, port 44133, log
lines show a real load (`load_model …`, `model loaded`, `listening on http://127.0.0.1:44133`) and a
clean SIGTERM teardown — the rerun ran a server rather than copying captures.

## 5. Witnessed record and outside observation

```
$ bash observe-witness.sh     # live tool in the foreground shell with --witness-dir $S/witness-rec --witness-timeout 60
ready.json: {"schema": "kama-live-witness/v1", "port": 35905, "pid": 376716, "written_utc": "2026-10-26T23:28:35.204Z"}
exe_sha256: 35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0
            (/proc/376716/exe -> /home/vgpnk/.local/opt/llama-b11909/llama-server)
model_arg_sha256: 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d
{"pid": 376716, "port": 35905, "exe_sha256": "35ac50fb…", "listen_inodes": ["620707890"],
 "socket_inodes_owned_by_pid": ["620707890"], "port_owned_by_pid": true, "vocab_size": 512,
 "detokenized": " kama witness 79ec4f0e0a29be1c", "nonce_roundtrip": true, "pieces_match_vocab": true}
observer_exit=0
live_exit=0
outcome pass witness {"dir": ".../witness-rec", "pid": 376716, "port": 35905, "released": true,
                      "schema": "kama-live-witness/v1", "waited_ms": 150}
checks 11 all_passed True evaluated 11
pid_gone=true
port_refuses=true URLError
```
Observer details (`out/nonce-observation.json`, `out/observe-witness.sh`): a LISTEN socket for the
announced port exists in `/proc/net/tcp` and its inode is an fd of the announced pid; `/proc/<pid>/exe`
hashes to the frozen server; the child's `-m` argument hashes to the frozen model; a fresh
`kama witness <16 hex>` nonce round-trips through POST /tokenize (`with_pieces`) and POST /detokenize
with every returned piece equal to the counter's own GGUF vocabulary decoding
(`tokenizer.ggml.tokens`, 512 entries, U+2581 read as a space) — the vocabulary decoder was imported
read-only from the frozen counter (`tools/round49-replay-witness-audit.py`). After `release`:
`witness.released true`, live exit 0, pid gone, port refuses.

The witnessed receipt also replays:

```
$ python3 kama-shokunin/tools/kama-live-replay.py --receipt $S/receipt-witness.json \
    --work $S/replay-witnessed --out $S/replay-witnessed-result.json
replay match=True refused=None mismatches=0 exit=0   (out/replay-witnessed-result.json)
```

## Findings

- **No defect found in the recorded paths.** Record-time bound accepts the real b11909 member
  (`kama-llamacpp-live.py:258-263` did not fire; `provenance.verified.at == record`), the v5 receipt is
  pass with 11/11, both receipts replay clean, the witness hold works end to end and the teardown is
  proven.
- Observation (not a defect): the recorded hold was short — `witness.waited_ms 150` on this host
  because the whole record completes in ~0.5 s (260K model). The hold is release-driven, not
  timer-driven, so an observer that writes `release` after its own checks is not racing a fixed
  window; my observer finished its four checks inside that 150 ms.
- Risk / inherited limit: `witness.dir` in the receipt is an absolute scratch path that the seat
  removes, and `server.arg`/`model.arg` are host/scratch paths. Neither is read by
  `kama-live-replay.py` (the stable projection excludes instance facts, `kama-live-replay.py:168-196`),
  so replayability is unaffected, but a future reader of `witness.dir` will find it gone.
- Inherited limit (already in the preregistration): the witness proves the frozen binary ran as the
  listener with the frozen model; it does not prove the binary came from the downloaded archive at
  replay time — that is the replay leg's member-digest check (`kama-live-replay.py:258-263`), which
  this run exercised (extracted member hashed before execution, match).

## Hygiene

- Scratch `/fast/scratch/hyaku/kama-r49/X1Record` removed; receipts copied first and verified
  byte-identical by sha256 (`receipt-record.json 5b4d9a40…`, `receipt-witness.json b9b64b7b…`,
  `replay-result.json 450a7575…`, `replay-witnessed-result.json 9f203c7b…`,
  `nonce-observation.json e2051f07…`).
- Ports 42935 / 35905 / 44133 / 45897 (also used by the first, superseded witness attempt) all refuse
  connections afterwards; `pgrep -af llama-server` shows only peer `X1Kill`'s replay processes — none
  started by this seat survive.
- Lane untouched: no git/jj mutation, no write outside `.ufo/waves/round-49/w1/out/`. No package
  installs were needed.
