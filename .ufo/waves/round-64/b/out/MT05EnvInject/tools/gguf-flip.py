# Scratch helper (run once): copy stories260K.gguf and XOR the bytes of output.weight (else token_embd.weight)
# with 0x55, for the answer-changing KILL control (variant v8). Reads the shared fixture; writes only the copy.
import struct, os
SRC = os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf')
DST = '/fast/scratch/hyaku/kama-r64/b/MT05EnvInject/model-x/stories260K.gguf'
data = bytearray(open(SRC, 'rb').read())
pos = 0
def u32():
    global pos; v = struct.unpack_from('<I', data, pos)[0]; pos += 4; return v
def u64():
    global pos; v = struct.unpack_from('<Q', data, pos)[0]; pos += 8; return v
def gstr():
    global pos; n = u64(); s = bytes(data[pos:pos+n]); pos += n; return s
SIZES = {0:1,1:1,2:2,3:2,4:4,5:4,6:4,7:1,10:8,11:8,12:8}
def skipval(t):
    global pos
    if t == 8: gstr(); return
    if t == 9:
        et = u32(); n = u64()
        for _ in range(n): skipval(et)
        return
    pos += SIZES[t]
assert data[:4] == b'GGUF'; pos = 4
ver = u32(); nt = u64(); nkv = u64(); align = 32
for _ in range(nkv):
    k = gstr(); t = u32()
    if k == b'general.alignment': align = struct.unpack_from('<I', data, pos)[0]
    skipval(t)
tens = []
for _ in range(nt):
    name = gstr(); nd = u32(); dims = [u64() for _ in range(nd)]; typ = u32(); off = u64()
    tens.append((off, name, typ, dims))
pos = (pos + align - 1) // align * align; base = pos
tens.sort()
names = [t[1] for t in tens]
target = next(n for n in (b'output.weight', b'token_embd.weight') if n in names)
idx = names.index(target); off = tens[idx][0]
end = tens[idx+1][0] if idx + 1 < len(tens) else len(data) - base
for i in range(base + off, base + end): data[i] ^= 0x55
open(DST, 'wb').write(bytes(data))
print('target', target, 'bytes', end - off, 'wrote', DST)
