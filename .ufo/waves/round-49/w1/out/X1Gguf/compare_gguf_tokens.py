#!/usr/bin/env python3
"""Seat X1Gguf: independently decode tokenizer.ggml.tokens and compare to
gguf_tokens() in tools/round49-replay-witness-audit.py.

Run with the `gguf` PyPI package available, e.g.
  uv run --with gguf python compare_gguf_tokens.py <model.gguf> <counter.py>

Checks, all 512 entries:
  1. same length (and same n_vocab declared by the file)
  2. entry-by-entry string equality against gguf.GGUFReader().contents()
  3. raw-byte equality: the counter's decode('utf-8','replace') can only match
     the package's view when every token is valid UTF-8; verify strictly here
  4. sha256 of the newline-joined vocabulary, so this receipt is reproducible
from a file of any size (plus the same digest ordered by index).
"""
import hashlib
import importlib.metadata
import importlib.util
import json
import struct
import sys


def load_counter(path):
    spec = importlib.util.spec_from_file_location("c1counter", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def package_view(model):
    import gguf
    r = gguf.GGUFReader(model)
    f = r.get_field("tokenizer.ggml.tokens")
    def scalar(fld):
        c = fld.contents()
        return c if isinstance(c, str) else c[0]

    tok_model = scalar(r.get_field("tokenizer.ggml.model"))
    n_vocab = None
    for key in ("llama.vocab_size", "tokenizer.ggml.vocab_size"):
        fld = r.fields.get(key)
        if fld is not None:
            n_vocab = int(scalar(fld))
            break
    return (f.contents(), n_vocab, tok_model,
            importlib.metadata.version("gguf"))


def strict_utf8(model):
    """Re-decode the tokens array bytes strictly to expose invalid-UTF-8 tokens."""
    data = open(model, "rb").read()
    _nt, nkv = struct.unpack_from("<QQ", data, 8)
    off, fixed = 24, {0: 1, 1: 1, 2: 2, 3: 2, 4: 4, 5: 4, 6: 4, 7: 1, 10: 8, 11: 8, 12: 8}

    def rstr(o):
        n = struct.unpack_from("<Q", data, o)[0]
        return data[o + 8:o + 8 + n], o + 8 + n

    def skip(t, o):
        if t in fixed:
            return o + fixed[t]
        if t == 8:
            return rstr(o)[1]
        if t == 9:
            et, n = struct.unpack_from("<IQ", data, o)
            o += 12
            for _ in range(n):
                o = skip(et, o)
            return o
        raise ValueError(t)

    for _ in range(nkv):
        key, off = rstr(off)
        key = key.decode("utf-8")
        t = struct.unpack_from("<I", data, off)[0]
        off += 4
        if key == "tokenizer.ggml.tokens" and t == 9:
            et, n = struct.unpack_from("<IQ", data, off)
            off += 12
            raw = []
            for _ in range(n):
                b, off = rstr(off)
                raw.append(b)
            bad = [(i, b) for i, b in enumerate(raw) if _strict_fails(b)]
            return raw, bad
        off = skip(t, off)
    raise SystemExit("tokens absent")


def _strict_fails(b):
    try:
        b.decode("utf-8", "strict")
        return False
    except UnicodeDecodeError:
        return True


def main():
    model, counter = sys.argv[1], sys.argv[2]
    mod = load_counter(counter)
    mine = mod.gguf_tokens(model)
    theirs, n_vocab, tok_model, pkg_ver = package_view(model)
    raw, bad = strict_utf8(model)
    mism = [(i, mine[i] if i < len(mine) else None, theirs[i] if i < len(theirs) else None)
            for i in range(max(len(mine), len(theirs)))
            if (mine[i] if i < len(mine) else None) != (theirs[i] if i < len(theirs) else None)]
    sha = lambda v: hashlib.sha256("\n".join(v).encode()).hexdigest()
    out = {
        "model": model,
        "gguf_package_version": pkg_ver,
        "counter_len": len(mine),
        "package_len": len(theirs),
        "package_tokenizer_model": tok_model,
        "declared_n_vocab": n_vocab,
        "len_agrees": len(mine) == len(theirs),
        "n_vocab_agrees": n_vocab is None or n_vocab == len(mine),
        "declared_n_vocab_present": n_vocab is not None,
        "mismatches": len(mism),
        "first_mismatches": mism[:5],
        "all_512_equal": not mism and len(mine) == 512 and len(theirs) == 512,
        "counter_vocab_sha256": sha(mine),
        "package_vocab_sha256": sha(theirs),
        "raw_byte_count": len(raw),
        "invalid_utf8_count": len(bad),
        "invalid_utf8_examples": [(i, b.hex()) for i, b in bad[:5]],
        "first3": mine[:3],
        "last3": mine[-3:],
    }
    print(json.dumps(out, indent=1))
    return 0 if (out["all_512_equal"] and out["raw_byte_count"] == len(mine)
                 and not out["invalid_utf8_count"]) else 1


if __name__ == "__main__":
    sys.exit(main())
