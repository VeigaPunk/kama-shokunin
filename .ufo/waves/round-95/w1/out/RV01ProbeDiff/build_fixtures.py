import os, struct, sys
D = "/fast/scratch/hyaku/kama-r95/RV01ProbeDiff/fx"
os.makedirs(D, exist_ok=True)
MAGIC=b"GGUF"
def hdr(n_tensors, n_kv):
    return MAGIC + struct.pack("<IQQ", 3, n_tensors, n_kv)

# A: 900k tensor infos, F32 ne0=1, consistent offsets
p = os.path.join(D, "tens900k.gguf")
with open(p, "wb") as f:
    f.write(hdr(900_000, 0))
    buf = bytearray()
    for i in range(900_000):
        buf += struct.pack("<Q", 0)        # name len 0
        buf += struct.pack("<I", 1)        # nd
        buf += struct.pack("<Q", 1)        # ne0
        buf += struct.pack("<I", 0)        # type F32 (blk 1)
        buf += struct.pack("<Q", i * 4)    # offset consistent, 4 bytes each
        if len(buf) > 1 << 20:
            f.write(buf); buf = bytearray()
    f.write(buf)
print(p, os.path.getsize(p))

# B: one KV array, element type 8 (string), n = 49,000,000 zero-length strings,
#    then one F32 tensor with a bad offset -> invalid, at 49M-element cost
def arr_file(name, n, bad_off):
    p = os.path.join(D, name)
    kv = struct.pack("<Q", 0) + b"" + struct.pack("<I", 9) + struct.pack("<I", 8) + struct.pack("<Q", n)
    # after the array elements: tensor info (1 tensor)
    ti = struct.pack("<Q", 0) + struct.pack("<I", 1) + struct.pack("<Q", 32) + struct.pack("<I", 0) + struct.pack("<Q", bad_off)
    head = hdr(1, 1) + kv
    total = len(head) + 8 * n + len(ti)
    with open(p, "wb") as f:
        f.write(head)
        f.seek(len(head) + 8 * n)   # sparse zeros = 8-byte zero length prefixes
        f.write(ti)
        f.truncate(total)
    return p, total

for name, n, bad in [("arr49m_bad.gguf", 49_000_000, 1024), ("big200.gguf", 25_000_000, 1024)]:
    p, sz = arr_file(name, n, bad)
    print(p, sz)

# ok.gguf: 1 F32 tensor of 32 elements, data present
p = os.path.join(D, "ok.gguf")
with open(p, "wb") as f:
    head = hdr(1, 0)
    ti = struct.pack("<Q", 0) + struct.pack("<I", 1) + struct.pack("<Q", 32) + struct.pack("<I", 0) + struct.pack("<Q", 0)
    body = head + ti
    pad = (-len(body)) % 32
    body += b"\0" * pad
    body += b"\0" * 128
    f.write(body)
print(p, os.path.getsize(p))

# fast invalid: 192 bytes non-GGUF
p = os.path.join(D, "fast_bad.bin")
with open(p, "wb") as f:
    f.write(b"X" * 192)
print(p, os.path.getsize(p))
