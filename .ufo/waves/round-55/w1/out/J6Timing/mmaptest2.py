import ctypes, os, shutil, sys, time
SRC = "/home/vgpnk/.local/opt/llama-b11909/libggml-cpu-zen4.so"
CP  = "/fast/scratch/hyaku/kama-r55/w1/J6Timing/cpu.so"
shutil.copyfile(SRC, CP)
os.chmod(CP, 0o755)

# dlopen the copy: a real loader mapping (MAP_PRIVATE, PROT_READ|PROT_EXEC)
lib = ctypes.CDLL(CP, mode=os.RTLD_LAZY)

def maps_rows():
    rows = []
    with open("/proc/self/maps") as fh:
        for row in fh.read().splitlines():
            f = row.split(None, 5)
            if len(f) == 6 and f[5] == CP:
                rows.append(f)
    return rows

rows = maps_rows()
for f in rows:
    print("map:", f[0], f[1], "off=" + f[2], f[5])
exec_rows = [f for f in rows if "x" in f[1]]
assert exec_rows, "no exec mapping"
f = exec_rows[0]
lo, hi = (int(v, 16) for v in f[0].split("-"))
off = int(f[2], 16)
length = hi - lo
print("exec row: lo=%#x hi=%#x file_off=%#x len=%#x" % (lo, hi, off, length))

# byte at file offset off+0x10 (inside .init of this build)
target_off = off + 0x10
target_addr = lo + (target_off - off)
with open("/proc/self/mem", "rb", 0) as mem:
    mem.seek(target_addr)
    before = mem.read(1)
with open(CP, "rb") as fh:
    fh.seek(target_off)
    filebyte = fh.read(1)
print("file byte at %#x = %r ; mem byte = %r" % (target_off, filebyte, before))

# FLIP the byte in the file (as the mutant would)
fd = os.open(CP, os.O_RDWR)
os.pwrite(fd, bytes([filebyte[0] ^ 1]), target_off)
os.fsync(fd)
time.sleep(0.05)
with open("/proc/self/mem", "rb", 0) as mem:
    mem.seek(target_addr)
    after = mem.read(1)
with open(CP, "rb") as fh:
    fh.seek(target_off)
    fbyte2 = fh.read(1)
print("after flip: mem byte = %r ; file byte = %r" % (after, fbyte2))
print("VISIBLE_IN_MEM:", after != before)
