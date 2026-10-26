import json, secrets, sys, urllib.request, time
PORT = int(sys.argv[1]); nonce = f"kama witness {secrets.token_hex(8)}"
def post(path, body):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with op.open(req, timeout=30) as r:
        return json.loads(r.read(1 << 22))
print("NONCE", repr(nonce))
tk = post("/tokenize", {"content": nonce, "with_pieces": True})["tokens"]
print("TOKENIZE_PIECES", json.dumps(tk))
ids = [t["id"] for t in tk]
dt = post("/detokenize", {"tokens": ids})["content"]
print("DETOKENIZE", repr(dt), "equals_nonce", dt == nonce, "equals_space_nonce", dt == " " + nonce)
tk_ns = post("/tokenize", {"content": nonce})["tokens"]
print("TOKENIZE_IDSONLY", tk_ns, "same_ids", tk_ns == ids)
tk_bos = post("/tokenize", {"content": nonce, "add_special": True})["tokens"]
print("TOKENIZE_ADD_SPECIAL", tk_bos)
for probe in ("caf\u00e9", "\u20ac", "<s>", ""):
    r = post("/tokenize", {"content": probe, "with_pieces": True})["tokens"]
    print("PROBE", repr(probe), json.dumps(r), "detok", repr(post("/detokenize", {"tokens": [t["id"] for t in r]})["content"]))
