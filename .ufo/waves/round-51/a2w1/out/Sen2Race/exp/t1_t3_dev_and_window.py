#!/usr/bin/env python3
"""Sen2Race T1 (btrfs exe dev string vs os.stat) and T3 (server_exe on an exiting child)."""
import importlib.util, os, subprocess, sys, time, json

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
live = load("kama_live", LANE + "/tools/kama-llamacpp-live.py")

def maps_dev(pid, path):
    rows = []
    with open(f"/proc/{pid}/maps") as fh:
        for row in fh:
            f = row.split(None, 5)
            if len(f) == 6 and f[5].strip() == path:
                rows.append((f[3], f[4], row.split()[0]))
    return rows

D = os.path.dirname(os.path.abspath(__file__))
exe = os.path.join(D, "sleep-btrfs")
print("== T1: btrfs (/home, st_dev 0x%x) executable ==" % os.stat(exe).st_dev)
p = subprocess.Popen([exe, "120"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    time.sleep(0.3)
    se = live.server_exe(p.pid)
    st = os.stat(exe)
    py = "%02x:%02x" % (os.major(st.st_dev), os.minor(st.st_dev))
    real = os.path.realpath(exe)
    rows = maps_dev(p.pid, real)
    print("server_exe:", json.dumps(se, sort_keys=True))
    print("os.stat   dev=%s inode=%s" % (py, st.st_ino))
    print("maps exe rows (dev,inode,range):", rows)
    print("MATCH server_exe.dev==os.stat.dev:", se.get("dev") == py,
          "| server_exe.inode==os.stat.inode:", str(se.get("inode")) == str(st.st_ino))
    print("MATCH mapping-row dev==server_exe.dev:", bool(rows) and all(r[0] == se.get("dev") for r in rows))
    print("readlink:", se.get("path"))
    # same file through /proc/<pid>/exe: fstat of the open link vs os.stat of the path
    fd = os.open(f"/proc/{p.pid}/exe", os.O_RDONLY)
    fst = os.fstat(fd); os.close(fd)
    print("fstat(/proc/pid/exe) dev=%02x:%02x inode=%d == stat(path): %s" % (
        os.major(fst.st_dev), os.minor(fst.st_dev), fst.st_ino,
        (os.major(fst.st_dev), os.minor(fst.st_dev), fst.st_ino) == (os.major(st.st_dev), os.minor(st.st_dev), st.st_ino)))
finally:
    p.kill(); p.wait()

print()
print("== T3: child exits between the live tool's _child_running and server_exe ==")
short = subprocess.Popen(["/bin/sleep", "0.4"])
try:
    a = live._child_running(short)
    # model_mapping on a live child that maps a file (use this script's own model-free stand-in)
    time.sleep(0.8)  # child is now gone but unreaped (poll() never called on it)
    zb = os.path.exists(f"/proc/{short.pid}/exe")
    try:
        os.readlink(f"/proc/{short.pid}/exe"); rl = "readlink ok"
    except OSError as e:
        rl = f"readlink OSError errno={e.errno} {e.strerror}"
    try:
        os.open(f"/proc/{short.pid}/exe", os.O_RDONLY); opn = "open ok"
    except OSError as e:
        opn = f"open OSError errno={e.errno} {e.strerror}"
    print("_child_running at start:", a, "| /proc/<pid>/exe exists on unreaped zombie:", zb)
    print("zombie:", rl, "|", opn)
    print("server_exe(zombie):", json.dumps(live.server_exe(short.pid), sort_keys=True))
    print("poll() (reaps):", short.poll(), "| /proc exists after reap:", os.path.exists(f"/proc/{short.pid}"))
    print("server_exe(reaped pid):", json.dumps(live.server_exe(short.pid), sort_keys=True))
finally:
    short.wait()
