#!/usr/bin/env python3
"""ConnectKengaku (kama round 20): compare the llama-server's own header decode,
already captured in a sha-pinned v3 live receipt (/v1/models data[0].meta), with
llama.cpp's official gguf-py reader on the same file bytes. Read-only.
Usage: uv run --with gguf python3 engine_vs_oracle.py MODEL RECEIPT
Exit 0 = every compared pair agrees, 1 = a pair disagrees, 2 = could not evaluate."""
import hashlib, importlib.metadata as md, json, os, sys

def main(model, receipt_path):
    from gguf import GGUFReader
    raw = open(model, "rb").read()
    sha = hashlib.sha256(raw).hexdigest()
    rec = json.load(open(receipt_path))
    body = rec["captures"]["models"]["body"]
    body_sha_ok = hashlib.sha256(body.encode()).hexdigest() == rec["captures"]["models"]["body_sha256"]
    meta = json.loads(body)["data"][0]["meta"]
    r = GGUFReader(model)
    f = r.fields
    def scalar(k):
        x = f.get(k)
        if x is None:
            return "ABSENT"
        p = x.parts[x.data[0]]
        return bytes(p).decode() if x.types[0].name == "STRING" else p.tolist()[0]
    arch = scalar("general.architecture")
    keys = {k: scalar(k) for k in ["general.architecture", "general.name", f"{arch}.context_length",
            f"{arch}.block_count", f"{arch}.embedding_length", "general.file_type",
            "general.alignment", "tokenizer.ggml.model"]}
    tok = f.get("tokenizer.ggml.tokens")
    n_tok = len(tok.data) if tok is not None else "ABSENT"
    sum_ne = sum(int(t.n_elements) for t in r.tensors)
    sum_nb = sum(int(t.n_bytes) for t in r.tensors)
    out = {
        "gguf_py_version": md.version("gguf"),
        "model": model, "size": os.path.getsize(model), "sha256": sha,
        "receipt_model_sha256_post": rec["model_sha256_post"],
        "receipt_models_body_sha256_ok": body_sha_ok,
        "version": scalar("GGUF.version"), "tensor_count": scalar("GGUF.tensor_count"),
        "kv_count": scalar("GGUF.kv_count"), "keys": keys, "tokenizer.ggml.tokens_len": n_tok,
        "alignment_used": int(r.alignment), "data_offset": int(r.data_offset),
        "sum_tensor_n_elements": sum_ne, "sum_tensor_n_bytes": sum_nb,
        "engine_meta": meta,
    }
    pairs = [
        ("sha256 == receipt.model_sha256_post", sha, rec["model_sha256_post"]),
        (f"{arch}.context_length == meta.n_ctx_train", keys[f"{arch}.context_length"], meta["n_ctx_train"]),
        (f"{arch}.embedding_length == meta.n_embd", keys[f"{arch}.embedding_length"], meta["n_embd"]),
        ("len(tokenizer.ggml.tokens) == meta.n_vocab", n_tok, meta["n_vocab"]),
        ("sum(n_elements) == meta.n_params", sum_ne, meta["n_params"]),
        ("sum(n_bytes) == meta.size", sum_nb, meta["size"]),
        ("general.file_type ABSENT <=> meta.ftype startswith '(guessed)'",
         keys["general.file_type"] == "ABSENT", meta["ftype"].startswith("(guessed)")),
        ("data_offset + sum(n_bytes) == file size", r.data_offset + sum_nb, os.path.getsize(model)),
    ]
    out["pairs"] = [{"check": c, "left": l, "right": rr, "agree": l == rr} for c, l, rr in pairs]
    print(json.dumps(out, indent=1, default=str))
    if not body_sha_ok:
        return 2
    return 0 if all(p["agree"] for p in out["pairs"]) else 1

if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1], sys.argv[2]))
    except Exception as e:
        print(f"ERROR could-not-evaluate: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(2)
