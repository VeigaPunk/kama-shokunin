"""Old vs new piece predicate on live b11909 /tokenize responses (same model)."""
import importlib.util, json, sys, urllib.request
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); return m
old = load("old", "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round49-replay-witness-audit.py")
new = load("new", "apply/tools/round49-replay-witness-audit.py")
PORT = int(sys.argv[1]); MODEL = sys.argv[2]
vocab, types = new.gguf_vocab(MODEL)
assert vocab == old.gguf_tokens(MODEL), "patched vocab parse diverged"
print("types:", {k: types.count(k) for k in sorted(set(types))}, "n =", len(types))
def post(path, body):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req, timeout=30) as r:
        return json.loads(r.read(1 << 22))
def old_bad(tk):
    return [t for t in tk if not (isinstance(t.get("piece"), str) and 0 <= t["id"] < len(vocab)
                                 and vocab[t["id"]].replace("\u2581", " ") == t["piece"])]
def new_bad(tk):
    return [t for t in tk if not (isinstance(t.get("id"), int) and 0 <= t["id"] < len(vocab)
                                 and new.piece_bytes(t.get("piece")) is not None
                                 and new.piece_bytes(t.get("piece")) == new.expected_piece(
                                     t["id"], vocab[t["id"]], types[t["id"]]))]
for label, text in (("nonce", "kama witness 771f62308fafbb2f"), ("cjk", "\u667a"),
                    ("emoji", "\U0001f600"), ("mixed", "kama \u667a witness")):
    tk = post("/tokenize", {"content": text, "with_pieces": True})["tokens"]
    o, n = old_bad(tk), new_bad(tk)
    print(f"[{label}] tokens={len(tk)} old_bad={len(o)} new_bad={len(n)}")
# forgery controls: a server that lies about one piece must be caught by both
tk = post("/tokenize", {"content": "kama witness 771f62308fafbb2f", "with_pieces": True})["tokens"]
forged = [dict(t) for t in tk]; forged[0]["piece"] = "k"
forged2 = [dict(t) for t in tk]; forged2[5]["id"] = 3   # claim a byte token for a normal piece
print("forged piece  -> old_bad", len(old_bad(forged)), "new_bad", len(new_bad(forged)))
print("forged id     -> old_bad", len(old_bad(forged2)), "new_bad", len(new_bad(forged2)))
print("byte-token piece render: id 233 piece", json.dumps(post("/tokenize", {"content": "\u667a", "with_pieces": True})["tokens"][1]["piece"]))
