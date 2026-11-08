import pathlib, struct, os
def head(path):
    s = pathlib.Path(path).read_text()
    i = s.index("ROUTER_PY=$(cat <<'PY'\n"); j = s.index("\nPY\n", i)
    ls = s[i+len("ROUTER_PY=$(cat <<'PY')\n"):j].splitlines(True)
    k = next(k for k,l in enumerate(ls) if "json.load(open(sys.argv[1]))" in l)
    ns = {}; exec(compile("".join(ls[:k-1]), path+".h","exec"), ns); return ns
base = head("base_probe.sh")
tip  = head("/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh")
print("MAX_STEPS base=%d tip=%d" % (base["MAX_STEPS"], tip["MAX_STEPS"]))
def gguf_nd(n_tensors, nd, elems=1):
    out=[b"GGUF",struct.pack("<I",3),struct.pack("<QQ",n_tensors,0)]; off=0
    for t in range(n_tensors):
        nm=b"t%07d"%t; dims=b"".join(struct.pack("<Q",elems) for _ in range(nd))
        out.append(struct.pack("<Q",len(nm))+nm+struct.pack("<I",nd)+dims+struct.pack("<IQ",0,off))
        off+=(elems*4+31)//32*32
    h=b"".join(out); pad=(len(h)+31)//32*32-len(h); return h+b"\0"*pad+b"\0"*off
p="fixtures/w11.gguf"; open(p,"wb").write(gguf_nd(700_000,1)); ap=os.path.abspath(p)
print("W11 700k nd=1 -> base probe: %r   tip probe: %r" % (base["gguf_state"](ap), tip["gguf_state"](ap)))
import importlib.util
spec=importlib.util.spec_from_file_location("c","/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round96-router-budget.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
q="fixtures/w12.gguf"; open(q,"wb").write(m.gguf_strbig()); qp=os.path.abspath(q)
print("W12 amended     -> base probe: %r   tip probe: %r" % (base["gguf_state"](qp), tip["gguf_state"](qp)))
