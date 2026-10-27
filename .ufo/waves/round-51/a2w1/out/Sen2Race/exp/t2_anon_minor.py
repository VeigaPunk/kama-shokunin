#!/usr/bin/env python3
"""Sen2Race T2: does '%02x:%02x' of st_dev match /proc/<pid>/maps for an anon device
with minor > 255? Run inside a private user+mount namespace and mount tmpfs instances,
whose s_dev is anonymous (major 0, minor from the global anon-bdev IDA)."""
import mmap, os, subprocess, sys, tempfile

base = os.path.dirname(os.path.abspath(__file__))
n = int(sys.argv[1]) if len(sys.argv) > 1 else 400
root = os.path.join(base, "t2-mnts")
os.makedirs(root, exist_ok=True)
made = []
for i in range(n):
    d = os.path.join(root, f"m{i}")
    os.makedirs(d, exist_ok=True)
    r = subprocess.run(["mount", "-t", "tmpfs", "tmpfs", d], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"mount {i} failed: {r.stderr.strip()}"); break
    made.append(d)
print("mounts made:", len(made))
best = None
for d in made:
    st = os.stat(d)
    maj, mi = os.major(st.st_dev), os.minor(st.st_dev)
    if mi > 255:
        best = (d, st, maj, mi); break
if best is None:
    print("no mount with minor>255 among", len(made), "-> minors:", sorted({os.minor(os.stat(d).st_dev) for d in made}))
    sys.exit(3)
d, st, maj, mi = best
print(f"chosen {d}: raw st_dev=0x{st.st_dev:x} os.major={maj} os.minor={mi} fmt={'%02x:%02x' % (maj, mi)}")
f = os.path.join(d, "mapped.bin")
with open(f, "wb") as fh: fh.write(b"x" * 65536)
mm = mmap.mmap(os.open(f, os.O_RDONLY), 65536, prot=mmap.PROT_READ)
rows = []
with open("/proc/self/maps") as fh:
    for row in fh:
        p = row.split(None, 5)
        if len(p) == 6 and p[5].strip() == f:
            rows.append((p[3], p[4]))
print("maps dev/inode rows for the mapping:", rows)
print("kernel maps dev string:", rows[0][0] if rows else None)
print("python  dev string:", '%02x:%02x' % (maj, mi))
print("MATCH:", bool(rows) and rows[0][0] == '%02x:%02x' % (maj, mi))
mm.close()
