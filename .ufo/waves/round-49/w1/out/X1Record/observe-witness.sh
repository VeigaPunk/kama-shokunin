#!/usr/bin/env bash
# Round-49 seat X1Record: record one v5 receipt with --witness-dir and observe the held
# server from outside (exe digest, LISTEN socket owned by the pid, -m model digest, fresh
# nonce through /tokenize + /detokenize with pieces checked against the model's own GGUF
# vocabulary), then release and confirm teardown.
set -u
S=/fast/scratch/hyaku/kama-r49/X1Record
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
W="$S/witness-rec"
MODEL="$S/dl/stories260K.gguf"
ARCHIVE="$S/dl/llama-b11909-bin-ubuntu-x64.tar.gz"
rm -rf "$W"; mkdir -p "$S/tmp" "$W"
export TMPDIR="$S/tmp"

python3 "$LANE/tools/kama-llamacpp-live.py" \
  --server /home/vgpnk/.local/opt/llama-b11909/llama-server \
  --model "$MODEL" --model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d \
  --alias kama-r49-witness --ctx 256 --threads 1 \
  --server-asset-url https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz \
  --server-asset-sha256 bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b \
  --server-member llama-b11909/llama-server \
  --model-url https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf \
  --server-archive "$ARCHIVE" \
  --witness-dir "$W" --witness-timeout 60 \
  --out "$S/receipt-witness.json" &
LPID=$!

for _ in $(seq 1 1200); do
  [ -f "$W/ready.json" ] && break
  sleep 0.1
done
echo "ready.json:"; cat "$W/ready.json"; echo

read -r PORT SPID <<EOF
$(python3 -c "import json;d=json.load(open('$W/ready.json'));print(d['port'],d['pid'])")
EOF
echo "announced port=$PORT pid=$SPID"

echo "exe_sha256: $(sha256sum /proc/$SPID/exe | cut -d' ' -f1)  (/proc/$SPID/exe -> $(readlink /proc/$SPID/exe))"
echo "cmdline:"; tr '\0' '\n' < /proc/$SPID/cmdline | sed -n '1,6p'
MARG=$(tr '\0' '\n' < /proc/$SPID/cmdline | sed -n '3p')
echo "model_arg=$MARG"
echo "model_arg_sha256: $(sha256sum "$MARG" | cut -d' ' -f1)"

python3 - "$W" "$SPID" "$PORT" "$S/nonce-observation.json" "$MODEL" "$LANE/tools/round49-replay-witness-audit.py" <<'PY'
import hashlib, importlib.util, json, os, sys, urllib.request
w, spid, port, out, model, counter = (sys.argv[1], int(sys.argv[2]), int(sys.argv[3]),
                                      sys.argv[4], sys.argv[5], sys.argv[6])
def listen_inodes(p):
    res = []
    for path in ("/proc/net/tcp", "/proc/net/tcp6"):
        try:
            lines = open(path).read().splitlines()[1:]
        except OSError:
            continue
        for ln in lines:
            f = ln.split()
            if len(f) < 10 or f[3] != "0A":
                continue
            if int(f[1].rsplit(":", 1)[1], 16) == p:
                res.append(f[9])
    return res
inodes = listen_inodes(port)
try:
    fds = set(os.listdir(f"/proc/{spid}/fd"))
except OSError:
    fds = set()
owned = []
for ino in inodes:
    for fd in fds:
        try:
            if os.readlink(f"/proc/{spid}/fd/{fd}") == f"socket:[{ino}]":
                owned.append(ino); break
        except OSError:
            pass
exe = hashlib.sha256(open(f"/proc/{spid}/exe", "rb").read()).hexdigest()
op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
def post(p, body):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{p}", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with op.open(req, timeout=10) as r:
        return json.loads(r.read(1 << 20))
nonce = "kama witness " + os.urandom(8).hex()
tok = post("/tokenize", {"content": nonce, "with_pieces": True})["tokens"]
ids = [t["id"] for t in tok]
det = post("/detokenize", {"tokens": ids})["content"]
# the counter's own GGUF vocabulary decoder (imported read-only from the frozen counter)
spec = importlib.util.spec_from_file_location("r49counter", counter)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
vocab = mod.gguf_tokens(model)
bad = [t for t in tok if not (isinstance(t.get("piece"), str) and 0 <= t["id"] < len(vocab)
                              and vocab[t["id"]].replace("\u2581", " ") == t["piece"])]
res = {"witness_dir": w, "pid": spid, "port": port, "exe_sha256": exe,
       "listen_inodes": inodes, "socket_inodes_owned_by_pid": owned,
       "port_owned_by_pid": bool(inodes) and len(owned) == len(inodes),
       "vocab_size": len(vocab), "nonce": nonce, "pieces": tok, "token_ids": ids,
       "detokenized": det, "nonce_roundtrip": det in (nonce, " " + nonce),
       "pieces_match_vocab": not bad, "bad_pieces": bad[:3]}
json.dump(res, open(out, "w"), indent=1)
print(json.dumps({k: res[k] for k in ("pid", "port", "exe_sha256", "listen_inodes",
      "socket_inodes_owned_by_pid", "port_owned_by_pid", "vocab_size", "detokenized",
      "nonce_roundtrip", "pieces_match_vocab")}))
PY
OBS=$?
echo "observer_exit=$OBS"

touch "$W/release"
wait $LPID
echo "live_exit=$?"
python3 -c "import json;r=json.load(open('$S/receipt-witness.json'));print('outcome',r['outcome'],'witness',json.dumps(r.get('witness')));print('checks',len(r['checks']),'all_passed',all(c['passed'] for c in r['checks'] if c['evaluated']),'evaluated',sum(1 for c in r['checks'] if c['evaluated']));print('verified',json.dumps(r['provenance'].get('verified')))"
kill -0 "$SPID" 2>/dev/null && echo "PID_STILL_ALIVE" || echo "pid_gone=true"
python3 -c "
import json,urllib.request
op=urllib.request.build_opener(urllib.request.ProxyHandler({}))
port=int(json.load(open('$S/receipt-witness.json'))['witness']['port'])
try:
    op.open(f'http://127.0.0.1:{port}/health',timeout=2); print('port_still_answers=true')
except Exception as e: print('port_refuses=true', type(e).__name__)
"
