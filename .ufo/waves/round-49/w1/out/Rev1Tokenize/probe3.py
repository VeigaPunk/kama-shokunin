import importlib.util, json, secrets, sys, urllib.request
spec = importlib.util.spec_from_file_location(
    "c1", "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round49-replay-witness-audit.py")
c1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1)
PORT = int(sys.argv[1]); MODEL = sys.argv[2]; N = int(sys.argv[3])
vocab = c1.gguf_tokens(MODEL)
def post(path, body):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req, timeout=30) as r:
        return json.loads(r.read(1 << 22))
fails, byte_hits, allids = 0, 0, set()
for _ in range(N):
    nonce = f"kama witness {secrets.token_hex(8)}"
    tk = post("/tokenize", {"content": nonce, "with_pieces": True})["tokens"]
    ids = [t["id"] for t in tk]; allids |= set(ids)
    bad = [t for t in tk if not (isinstance(t.get("piece"), str) and 0 <= t["id"] < len(vocab)
                                 and vocab[t["id"]].replace("\u2581", " ") == t["piece"])]
    byte_hits += sum(1 for i in ids if 3 <= i <= 258)   # stories260K byte tokens
    dt = post("/detokenize", {"tokens": ids})["content"]
    if bad or dt != " " + nonce:
        fails += 1
        if fails <= 3: print("FAIL", repr(nonce), bad[:3], repr(dt))
print(json.dumps({"trials": N, "fails": fails, "byte_token_uses": byte_hits,
                  "distinct_ids": len(allids), "id_range": [min(allids), max(allids)],
                  "vocab_len": len(vocab), "model_sha_ok": c1.sha_file(MODEL) == c1.MODEL_SHA}))
alphabet = sorted((set("kama witness") | set("0123456789abcdef")) - {" "})
print("nonce alphabet:", "".join(alphabet))
print("alphabet ids (all must be NORMAL, i.e. outside the byte range 3..258):",
      {ch: vocab.index(ch) for ch in alphabet})
print("lone U+2581 token id:", vocab.index("\u2581"))
