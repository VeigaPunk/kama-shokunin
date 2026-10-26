import importlib.util, json, sys, urllib.request
spec = importlib.util.spec_from_file_location(
    "c1", "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round49-replay-witness-audit.py")
c1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1)
PORT = int(sys.argv[1]); MODEL = sys.argv[2]
vocab = c1.gguf_tokens(MODEL)
print("counter gguf_tokens: n =", len(vocab), "sha ok =", c1.sha_file(MODEL) == c1.MODEL_SHA)
def post(path, body):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req, timeout=30) as r:
        return json.loads(r.read(1 << 22))
def counter_check(text):
    tk = post("/tokenize", {"content": text, "with_pieces": True})["tokens"]
    ids = [t["id"] for t in tk]
    bad = [t for t in tk if not (isinstance(t.get("piece"), str) and 0 <= t["id"] < len(vocab)
                                 and vocab[t["id"]].replace("\u2581", " ") == t["piece"])]
    dt = post("/detokenize", {"tokens": ids})["content"]
    ok_dt = dt in (text, " " + text)
    return tk, ids, bad, dt, ok_dt
nonce = "kama witness %016x" % 0x771f62308fafbb2f
for label, text in (("nonce", nonce), ("cafe", "caf\u00e9"), ("cjk", "\u667a"), ("emoji", "\U0001f600"),
                    ("plain", "kama witness ")):
    tk, ids, bad, dt, ok_dt = counter_check(text)
    print(f"[{label}] text={text!r}")
    print("   ids      =", ids)
    print("   pieces   =", json.dumps([t["piece"] for t in tk], ensure_ascii=False))
    print("   vocab[id]=", json.dumps([vocab[i] for i in ids if 0 <= i < len(vocab)], ensure_ascii=False)[:400])
    print("   counter_bad =", json.dumps(bad, ensure_ascii=False)[:300], "n_bad", len(bad))
    print("   detok =", repr(dt), "counter_detok_ok =", ok_dt)
print("byte-token ids in vocab range 0..258:", [i for i in range(0, 12)])
print("vocab[3]=", repr(vocab[3]), "vocab[485]=", repr(vocab[485]), "vocab[503]=", repr(vocab[503]))
print("detokenize([3,4]) =", repr(post("/detokenize", {"tokens": [3, 4, 65]})["content"]))
