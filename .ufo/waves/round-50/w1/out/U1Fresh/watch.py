#!/usr/bin/env python3
"""U1Fresh watcher: poll a counter scratch root; log timing events, process
births/deaths (llama-server / replay / live tool / invoker), the gguf maps
line + stat of any llama-server, and du -sb of the scratch root.
Usage: watch.py <scratch_root> <out_log> <stop_flag_file>
"""
import json, os, stat as stmod, subprocess, sys, time

root, out, stopf = sys.argv[1], sys.argv[2], sys.argv[3]
ev = []
def ts():
    return time.time()
def log(kind, **kw):
    ev.append({"t": ts(), "ev": kind, **kw})

ready_seen = set()
release_seen = set()
outj_seen = set()
procs = {}          # pid -> (first_seen, cmdline_key)
dead_logged = set()
maps_done = set()
du_peak = 0
du_last = 0
t0 = ts()

while ts() - t0 < 1200:
    if os.path.exists(stopf) and ts() - os.path.getmtime(stopf) > 2:
        break
    # 1) ready.json / release / out json
    try:
        for dirpath, _dirs, files in os.walk(root):
            for f in files:
                p = os.path.join(dirpath, f)
                try:
                    m = os.path.getmtime(p)
                except OSError:
                    continue
                if f == "ready.json" and p not in ready_seen:
                    ready_seen.add(p)
                    try:
                        d = json.load(open(p))
                    except Exception:
                        d = None
                    log("ready", path=p, mtime=m, content=d)
                elif f == "release" and p not in release_seen:
                    release_seen.add(p)
                    log("release", path=p, mtime=m)
                elif f.endswith(".json") and os.path.basename(dirpath) == os.path.basename(root.rstrip("/")) and p not in outj_seen:
                    # top-level json in scratch (b1.json etc.)
                    outj_seen.add(p)
                    log("outjson", path=p, mtime=m)
    except OSError:
        pass
    # 2) process scan
    alive_now = set()
    try:
        names = os.listdir("/proc")
    except OSError:
        names = []
    for n in names:
        if not n.isdigit():
            continue
        pid = int(n)
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as fh:
                cl = fh.read().replace(b"\0", b" ").decode("utf-8", "replace").strip()
            with open(f"/proc/{pid}/stat") as fh:
                rest = fh.read().rsplit(")", 1)[1].split()
            state, ppid, startt = rest[0], int(rest[1]), int(rest[19])
        except (OSError, IndexError, ValueError):
            continue
        if not (("llama" in cl) or ("kama-live" in cl) or ("subprocess.call" in cl)):
            continue
        if state in ("Z", "X"):
            state = "Z"
        alive_now.add(pid)
        if pid not in procs:
            procs[pid] = (ts(), cl[:200])
            log("proc_born", pid=pid, ppid=ppid, start=startt, state=state, cmd=cl[:200])
        if ("llama-server" in cl) and pid not in maps_done:
            # dump file-backed .gguf mappings + stat
            maps_done.add(pid)
            rows = []
            try:
                with open(f"/proc/{pid}/maps") as fh:
                    for row in fh.read().splitlines():
                        if ".gguf" in row:
                            f = row.split(None, 5)
                            ent = {"maps_row": row}
                            if len(f) >= 6:
                                try:
                                    s = os.stat(f[5])
                                    ent["stat"] = {
                                        "st_dev_hex": f"{os.major(s.st_dev):02x}:{os.minor(s.st_dev):02x}",
                                        "st_ino": s.st_ino, "size": s.st_size}
                                except OSError as e:
                                    ent["stat_err"] = str(e)
                            rows.append(ent)
            except OSError as e:
                rows.append({"maps_err": str(e)})
            log("server_maps", pid=pid, gguf_mappings=rows)
    for pid in list(procs):
        if pid not in alive_now and pid not in dead_logged:
            dead_logged.add(pid)
            log("proc_dead", pid=pid, cmd=procs[pid][1])
    # 3) du
    try:
        r = subprocess.run(["du", "-sb", root], capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            du_last = int(r.stdout.split()[0])
            du_peak = max(du_peak, du_last)
    except Exception:
        pass
    time.sleep(0.2)

log("watch_end", du_peak=du_peak, du_last=du_last, procs_total=len(procs))
with open(out, "w") as fh:
    json.dump(ev, fh, indent=1)
