import pathlib, struct, os, sys
s = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh").read_text()
i = s.index("ROUTER_PY=$(cat <<'PY'\n"); j = s.index("\nPY\n", i)
body = s[i+len("ROUTER_PY=$(cat <<'PY'\n"):j]
ls = body.splitlines(True)
k = next(k for k,l in enumerate(ls) if "json.load(open(sys.argv[1]))" in l)
ns = {}; exec(compile("".join(ls[:k-1]), "t.h","exec"), ns)

def gguf_nd(n_tensors, nd, elems=1):
    out = [b"GGUF", struct.pack("<I",3), struct.pack("<QQ", n_tensors, 0)]
    off = 0
    for t in range(n_tensors):
        name = b"t%07d" % t
        dims = b"".join(struct.pack("<Q", elems) for _ in range(nd))
        out.append(struct.pack("<Q", len(name)) + name + struct.pack("<I", nd) + dims + struct.pack("<IQ", 0, off))
        off += (elems*4 + 31)//32*32
    head = b"".join(out)
    pad = (len(head)+31)//32*32 - len(head)
    return head + b"\0"*pad + b"\0"*off

def v(n, nd):
    p = f"fixtures/e_{nd}_{n}.gguf"; open(p,"wb").write(gguf_nd(n, nd))
    return ns["gguf_state"](os.path.abspath(p))

print("nd=3 (SKILL.md claims 625,000 decidable headers):")
for n in (624998, 624999, 625000, 625001):
    print(f"  n={n:,} -> {v(n,3)!r}")
print("derived (5,000,000-4)//8 =", (5_000_000-4)//8)
