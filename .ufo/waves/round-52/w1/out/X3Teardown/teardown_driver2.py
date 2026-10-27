#!/usr/bin/env python3
"""X3Teardown v2: strict pid attribution (children of the invoker only), full fd/socket
inventory, SIGKILL of the invoker, and proof that every process of this run and its memfd
are gone within 30 s."""
import fcntl, json, os, signal, socket, subprocess, sys, time

S = "/fast/scratch/hyaku/kama-r52/X3Teardown"
LANE = os.path.join(S, "lane")
REPLAY = os.path.join(LANE, "tools", "kama-live-replay.py")
RECEIPT = ("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/"
           "c2/live/receipt-1.json")
WORK, OUT, WD = os.path.join(S, "w2"), os.path.join(S, "r2.json"), os.path.join(S, "wd2")
INV = "import subprocess,sys;sys.exit(subprocess.call(sys.argv[1:]))"
F_GET_SEALS = 1034
SEALS_ALL = 15

for d in (WORK, WD):
    os.makedirs(d, exist_ok=True)
os.environ["TMPDIR"] = S

log = []
T0 = time.monotonic()


def note(text, t=None):
    t = time.monotonic() if t is None else t
    log.append({"t": round(t - T0, 3), "text": text})
    print(f"[{t - T0:8.3f}] {text}", flush=True)


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return {"cmd": cmd, "exit": p.returncode, "out": p.stdout, "err": p.stderr}


def procs():
    """{pid: (uid, ppid, state, cmdline)} for every process we may read."""
    out = {}
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        pid = int(name)
        try:
            uid = os.stat("/proc/" + name).st_uid
        except OSError:
            continue
        st, cmd = {}, ""
        try:
            with open(f"/proc/{pid}/status") as fh:
                for line in fh:
                    k, _, v = line.partition(":")
                    if k in ("Name", "State", "PPid", "Pid", "Pgrp", "Seccomp"):
                        st[k] = v.strip()
        except OSError:
            continue
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as fh:
                cmd = fh.read().replace(b"\0", b" ").decode("utf-8", "replace").strip()
        except OSError:
            pass
        out[pid] = {"uid": uid, "ppid": st.get("PPid"), "state": st.get("State"),
                    "cmd": cmd}
    return out


def children(pid, table=None):
    t = table or procs()
    return [p for p, v in t.items() if v["ppid"] == str(pid)]


def status_of(pid):
    d = {}
    try:
        with open(f"/proc/{pid}/status") as fh:
            for line in fh:
                k, _, v = line.partition(":")
                if k in ("Name", "State", "PPid", "Pid", "Pgrp", "Seccomp", "NoNewPrivs"):
                    d[k] = v.strip()
    except OSError:
        return None
    return d


def alive(pid):
    st = status_of(pid)
    return None if st is None else "Z" not in st.get("State", "")


def fd_table(pid):
    out = {}
    d = f"/proc/{pid}/fd"
    try:
        names = sorted(os.listdir(d), key=lambda x: int(x))
    except OSError as exc:
        return {"error": str(exc)}
    for n in names:
        try:
            out[n] = os.readlink(os.path.join(d, n))
        except OSError as exc:
            out[n] = f"<unreadable:{exc.strerror}>"
    return out


def memfd_holders(mine_paths):
    """All fds of all my-uid processes whose target names the llama-server memfd, with
    attribution: 'this-run' when the holder's cmdline names one of my scratch paths."""
    found = []
    t = procs()
    for pid, v in t.items():
        if v["uid"] != os.getuid():
            continue
        d = f"/proc/{pid}/fd"
        try:
            names = os.listdir(d)
        except OSError:
            continue
        for n in names:
            try:
                tgt = os.readlink(os.path.join(d, n))
            except OSError:
                continue
            if "memfd:llama" in tgt:
                found.append({"pid": pid, "fd": int(n), "target": tgt,
                              "cmd": v["cmd"][:200],
                              "scope": ("this-run" if any(p in v["cmd"] for p in mine_paths)
                                        else "other")})
    return found


def sock_inode_lookup(inodes):
    """map socket inode -> /proc/net row (local addr:port, state) for tcp and unix."""
    want = {str(i) for i in inodes}
    res = {}
    for name in ("/proc/net/tcp", "/proc/net/tcp6"):
        try:
            with open(name) as fh:
                next(fh)
                for line in fh:
                    f = line.split()
                    if len(f) > 9 and f[9] in want:
                        res[f[9]] = {"file": name, "local": f[1], "rem": f[2],
                                     "state": f[3]}
        except OSError:
            pass
    return res


def memfd_id(pid, fd):
    try:
        st = os.stat(f"/proc/{pid}/fd/{fd}")
        return {"dev": "%02x:%02x" % (os.major(st.st_dev), os.minor(st.st_dev)),
                "ino": st.st_ino, "nlink": st.st_nlink}
    except OSError as exc:
        return {"error": str(exc)}


def exe_seals(pid):
    """open /proc/<pid>/exe (the counter's own check) and read F_GET_SEALS + fstat."""
    link = f"/proc/{pid}/exe"
    try:
        fd = os.open(link, os.O_RDONLY)
    except OSError as exc:
        return {"error": f"{exc.strerror}"}
    try:
        st = os.fstat(fd)
        try:
            seals = fcntl.fcntl(fd, F_GET_SEALS)
        except OSError:
            seals = None
        return {"path": os.readlink(link),
                "dev": "%02x:%02x" % (os.major(st.st_dev), os.minor(st.st_dev)),
                "ino": st.st_ino, "nlink": st.st_nlink, "size": st.st_size,
                "seals": seals, "seals_all": seals is not None and seals & SEALS_ALL == SEALS_ALL}
    finally:
        os.close(fd)


def port_probe(port):
    s = socket.socket()
    s.settimeout(0.5)
    try:
        s.connect(("127.0.0.1", port))
        return "open"
    except ConnectionRefusedError:
        return "refused"
    except OSError as exc:
        return type(exc).__name__
    finally:
        s.close()


evidence = {"schema": "x3teardown/v2", "scratch": S, "replay": REPLAY,
            "receipt": RECEIPT, "work": WORK, "witness_dir": WD,
            "commit": run(["git", "-C", LANE, "rev-parse", "HEAD"])["out"].strip(),
            "tool_sha256": run(["sha256sum", REPLAY])["out"].split()[0],
            "pgrep_before_exact": run(["pgrep", "-x", "llama-server"]),
            "pgrep_before_argv": run(["bash", "-c", "pgrep -af '/llama-server( |$)'"])}
note("baseline exact pgrep llama-server: " + repr(evidence["pgrep_before_exact"]["out"]))

argv = [sys.executable, "-c", INV, sys.executable, REPLAY,
        "--receipt", RECEIPT, "--work", WORK, "--out", OUT,
        "--witness-dir", WD, "--witness-timeout", "300"]
evidence["invoker_argv"] = argv
inv = subprocess.Popen(argv, stdout=open(os.path.join(S, "invoker2.out"), "wb"),
                       stderr=subprocess.STDOUT, cwd=S)
evidence["invoker_pid"] = inv.pid
note(f"invoker pid={inv.pid}")

import atexit


def _cleanup():
    try:
        if inv.poll() is None:
            os.kill(inv.pid, signal.SIGKILL)
            print("CLEANUP: killed invoker on unexpected exit", flush=True)
    except ProcessLookupError:
        pass


atexit.register(_cleanup)

ready_path = os.path.join(WD, "ready.json")
deadline = time.monotonic() + 300
ready = None
while time.monotonic() < deadline:
    if os.path.exists(ready_path):
        try:
            with open(ready_path) as fh:
                ready = json.load(fh)
            break
        except (OSError, ValueError):
            pass
    if inv.poll() is not None:
        note(f"invoker exited early rc={inv.returncode}")
        break
    time.sleep(0.02)
if ready is None:
    evidence["fatal"] = "no-ready.json"
    evidence["log"] = log
    evidence["invoker_exit"] = inv.poll()
    print(json.dumps(evidence, indent=1))
    sys.exit(3)
note("ready.json: " + json.dumps(ready))
evidence["ready"] = ready

# ---- deterministic tree: invoker -> replay -> live -> server --------------
t = procs()
assert t[inv.pid]["cmd"].startswith(sys.executable + " -c import subprocess")
kids = children(inv.pid, t)
replay_pid = next((p for p in kids if "kama-live-replay.py" in t[p]["cmd"]
                   and S in t[p]["cmd"]), None)
if replay_pid is None:
    evidence["fatal"] = "replay-not-a-child-of-invoker"
    evidence["children_of_invoker"] = {p: t[p]["cmd"] for p in kids}
    print(json.dumps(evidence, indent=1))
    sys.exit(4)
live_pid = next((p for p in children(replay_pid) if "kama-llamacpp-live.py" in procs()[p]["cmd"]), None)
server = int(ready["pid"])
tree_ids = [inv.pid, replay_pid, live_pid, server]
tree_ids = [p for p in tree_ids if p]
t = procs()
evidence["pids"] = {"invoker": inv.pid, "replay": replay_pid, "live": live_pid,
                    "server": server, "tree": tree_ids}
evidence["parentage"] = {str(p): {"ppid": t[p]["ppid"], "state": t[p]["state"]}
                         for p in tree_ids}
assert t[replay_pid]["ppid"] == str(inv.pid)
assert t[live_pid]["ppid"] == str(replay_pid)
assert t[server]["ppid"] == str(live_pid)
note(f"pids invoker={inv.pid} replay={replay_pid} live={live_pid} server={server} "
     f"(parentage verified: invoker->replay->live->server)")

# ---- observation while up -------------------------------------------------
obs = {"ps": run(["ps", "-o", "pid,ppid,pgid,sid,stat,etime,cmd", "-p",
                  ",".join(str(p) for p in tree_ids)]),
       "status": {str(p): status_of(p) for p in tree_ids},
       "cmdline": {str(p): t[p]["cmd"] for p in tree_ids},
       "ls_server_exe_and_fd": run(["ls", "-l", f"/proc/{server}/exe", f"/proc/{server}/fd"]),
       "ls_replay_fd": run(["ls", "-l", f"/proc/{replay_pid}/fd"]),
       "ls_live_fd": run(["ls", "-l", f"/proc/{live_pid}/fd"]),
       "ls_invoker_fd": run(["ls", "-l", f"/proc/{inv.pid}/fd"]),
       "server_exe_readlink": os.readlink(f"/proc/{server}/exe"),
       "server_exe_seals": exe_seals(server),
       "fd_tables": {"invoker": fd_table(inv.pid), "replay": fd_table(replay_pid),
                     "live": fd_table(live_pid), "server": fd_table(server)}}
try:
    with open(f"/proc/{server}/maps") as fh:
        obs["server_maps_memfd"] = [ln.strip() for ln in fh if "memfd" in ln]
except OSError as exc:
    obs["server_maps_memfd"] = [f"error:{exc}"]
socks = [int(ln.split("socket:[")[1].rstrip("]")) for ln in
         obs["fd_tables"]["server"].values() if isinstance(ln, str) and "socket:[" in ln]
obs["server_socket_inodes"] = socks
obs["server_socket_lookup"] = sock_inode_lookup(socks)
obs["memfd_holders_up"] = memfd_holders([S])
obs["memfd_identity"] = {f"{h['pid']}:{h['fd']}": memfd_id(h["pid"], h["fd"])
                         for h in obs["memfd_holders_up"]}
obs["raw_ls_proc_fd_grep"] = run(["bash", "-c",
                                  "ls -l /proc/*/fd 2>/dev/null | grep 'memfd:llama'"])
obs["port_up_probe"] = port_probe(int(ready["port"]))
obs["extracted_member"] = run(["stat", "-c", "size=%s mode=%A nlink=%h",
                               os.path.join(WORK, "server", "llama-b11909", "llama-server")])
obs["extracted_member_sha256"] = run(["sha256sum",
                                      os.path.join(WORK, "server", "llama-b11909",
                                                   "llama-server")])
evidence["observe"] = obs
note("memfd holders while up: " + json.dumps(obs["memfd_holders_up"]))
note("server fds: " + json.dumps(obs["fd_tables"]["server"]))
note("server exe seals: " + json.dumps(obs["server_exe_seals"]))
note("socket lookup: " + json.dumps(obs["server_socket_lookup"]))

# ---- the kill -------------------------------------------------------------
kill_t = time.monotonic()
os.kill(inv.pid, signal.SIGKILL)
note("SIGKILL invoker")
inv.wait()
evidence["kill_at_invoker_exit_s"] = round(time.monotonic() - kill_t, 3)

gone_at, last_holders = {}, []
deadline = kill_t + 30.0
while time.monotonic() < deadline:
    now = time.monotonic()
    for p in tree_ids:
        if p not in gone_at and alive(p) is None:
            gone_at[p] = round(now - kill_t, 3)
    holders = memfd_holders([S])
    if holders:
        last_holders = holders
    if len(gone_at) == len(tree_ids) and not holders:
        break
    time.sleep(0.02)
evidence["gone_at_s"] = {str(k): v for k, v in gone_at.items()}
evidence["all_gone_within_30s"] = len(gone_at) == len(tree_ids)
evidence["memfd_holders_after"] = memfd_holders([S])
evidence["memfd_holders_last_seen"] = last_holders
evidence["last_holder_seen_at_s"] = (round(time.monotonic() - kill_t, 3)
                                     if last_holders else None)
evidence["port_after_probe"] = port_probe(int(ready["port"]))
evidence["post_at_s"] = round(time.monotonic() - kill_t, 3)
note(f"gone_at={evidence['gone_at_s']} all_gone={evidence['all_gone_within_30s']} "
     f"memfd_after={evidence['memfd_holders_after']} port={evidence['port_after_probe']}")

time.sleep(0.5)
evidence["post"] = {
    "pgrep_exact": run(["pgrep", "-x", "llama-server"]),
    "pgrep_argv": run(["bash", "-c", "pgrep -af '/llama-server( |$)'"]),
    "tree_left": {p: procs().get(p) for p in tree_ids},
    "raw_ls_proc_fd_grep": run(["bash", "-c",
                                "ls -l /proc/*/fd 2>/dev/null | grep 'memfd:llama'"]),
    "memfd_holders_scoped": memfd_holders([S]),
    "out_exists": os.path.exists(OUT), "ready_exists": os.path.exists(ready_path),
    "witness_listing": sorted(os.listdir(WD)),
    "work_listing": sorted(os.listdir(WORK)),
    "invoker_log": open(os.path.join(S, "invoker2.out")).read()[-1500:],
    "at_s": round(time.monotonic() - kill_t, 3)}
note("post pgrep exact: " + repr(evidence["post"]["pgrep_exact"]["out"].strip()))
note("post raw memfd grep exit=" + str(evidence["post"]["raw_ls_proc_fd_grep"]["exit"])
     + " out=" + repr(evidence["post"]["raw_ls_proc_fd_grep"]["out"]))
evidence["log"] = log
json.dump(evidence, open(os.path.join(S, "evidence2.json"), "w"), indent=1)
print("EVIDENCE WRITTEN")
