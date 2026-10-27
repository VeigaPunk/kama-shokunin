import ctypes, glob, os, sys, json
out = {}
for p in sorted(glob.glob("/home/vgpnk/.local/opt/llama-b11909/libggml-cpu-*.so")):
    h = ctypes.CDLL(p, mode=ctypes.RTLD_LOCAL)
    try:
        f = h.ggml_backend_score
    except AttributeError:
        out[os.path.basename(p)] = "no-symbol"; continue
    f.restype = ctypes.c_int
    f.argtypes = []
    out[os.path.basename(p)] = int(f())
print(json.dumps(out, indent=0, sort_keys=True))
