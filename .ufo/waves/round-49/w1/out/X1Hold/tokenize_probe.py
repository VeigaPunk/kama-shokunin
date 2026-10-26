#!/usr/bin/env python3
"""X1Hold bonus probe: does the witness observer's own /tokenize+/detokenize traffic
change a receipt surface the replay compares? (/slots body_sha256 is compared.)"""
import hashlib, json, os, signal, subprocess, time, urllib.request, urllib.error

S = "/fast/scratch/hyaku/kama-r49/X1Hold"
srv = f"{S}/work-b/server/llama-b11909/llama-server"
model = f"{S}/work-b/download/stories260K.gguf"
port = 39041
p = subprocess.Popen([srv, "-m", model, "--alias", "kama-r48-live", "--host", "127.0.0.1",
                      "--port", str(port), "-c", "256", "-t", "1", "--no-webui", "--offline"],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
try:
    for _ in range(600):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2) as r:
                if r.status == 200:
                    break
        except Exception:
            pass
        time.sleep(0.1)

    def get(path):
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as r:
            return r.read()

    def post(path, obj):
        req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=json.dumps(obj).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    before = {"slots": get("/slots"), "props": get("/props"), "health": get("/health")}
    st, body = post("/tokenize", {"content": "X1Hold nonce 7f3a91c4", "with_pieces": True})
    print("tokenize status", st, body[:400].decode("utf-8", "replace"))
    tok = json.loads(body)
    st2, body2 = post("/detokenize", {"tokens": tok.get("tokens", []), "with_pieces": True})
    print("detokenize status", st2, body2[:300].decode("utf-8", "replace"))
    after = {"slots": get("/slots"), "props": get("/props"), "health": get("/health")}
    for k in before:
        print(k, "equal_after_tokenize", before[k] == after[k],
              "sha_before", hashlib.sha256(before[k]).hexdigest()[:16],
              "sha_after", hashlib.sha256(after[k]).hexdigest()[:16])
    pb, pa = json.loads(before["props"]), json.loads(after["props"])
    print("compared props.fields after:", {k: pa.get(k) for k in
          ("model_alias", "total_slots", "is_sleeping", "build_info")},
          "n_ctx", pa["default_generation_settings"]["n_ctx"])
    print("media_marker stable within process:", pb.get("media_marker") == pa.get("media_marker"))
finally:
    try:
        os.killpg(p.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        p.wait(timeout=15)
    except Exception:
        pass
