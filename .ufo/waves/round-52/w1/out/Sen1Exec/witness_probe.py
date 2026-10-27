#!/usr/bin/env python3
"""Sen1Exec probe: run the lane's live tool the way the round-52 replay does
(sealed memfd + --server-fd) under --witness-dir, and read, from another process:

  * the server's own fd table (/proc/<server>/fd) - is the memfd leaked in?
  * the live tool's fd table (/proc/<tool>/fd) and whether a same-uid process can open
    the sealed memfd there for write (seals) and for read
  * which shared libraries the server mapped, by path (LD_LIBRARY_PATH question)
  * /proc/<server>/exe identity (the counter's own witness)

usage: witness_probe.py <live-tool.py> <tag>
"""
import fcntl, hashlib, json, os, socket, subprocess, sys, time, urllib.request

SRC = "/home/vgpnk/.local/opt/llama-b11909/llama-server"
MODEL = "/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf"
MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
F_ADD_SEALS, F_GET_SEALS = 1033, 1034
SEALS = 15
S = os.path.dirname(os.path.abspath(__file__))


def memfd_of(path):
    fd = os.memfd_create(os.path.basename(path), os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING)
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
            os.write(fd, chunk)
    fcntl.fcntl(fd, F_ADD_SEALS, SEALS)
    return fd, h.hexdigest()


def fd_table(pid):
    out = {}
    for name in sorted(os.listdir(f"/proc/{pid}/fd"), key=lambda s: (len(s), s)):
        try:
            out[name] = os.readlink(f"/proc/{pid}/fd/{name}")
        except OSError as exc:
            out[name] = f"<{exc.strerror}>"
    return out


def memfd_maps(pid):
    rows = []
    with open(f"/proc/{pid}/maps") as fh:
        for ln in fh:
            if "/memfd:" in ln:
                rows.append(ln.rstrip("\n"))
    return rows


def lib_maps(pid):
    out = {}
    with open(f"/proc/{pid}/maps") as fh:
        for ln in fh:
            if ".so" in ln and "/" in ln:
                path = ln.split()[-1]
                out[path] = out.get(path, 0) + 1
    return out


def open_as_third_party(pid, fd):
    path = f"/proc/{pid}/fd/{fd}"
    res = {}
    for mode, flags in (("O_RDONLY", os.O_RDONLY), ("O_WRONLY", os.O_WRONLY), ("O_RDWR", os.O_RDWR)):
        try:
            h = os.open(path, flags)
            try:
                st = os.fstat(h)
                res[mode] = {"ok": True, "seals": fcntl.fcntl(h, F_GET_SEALS),
                             "nlink": st.st_nlink,
                             "sha256": hashlib.sha256(os.read(h, 1 << 30)).hexdigest()
                             if mode == "O_RDONLY" else None}
            finally:
                os.close(h)
        except OSError as exc:
            res[mode] = {"ok": False, "errno": exc.errno, "strerror": exc.strerror}
    return res


def main():
    live, tag = sys.argv[1], sys.argv[2]
    wd = os.path.join(S, f"witness-{tag}")
    os.makedirs(wd, exist_ok=True)
    fd, sha = memfd_of(SRC)
    receipt = os.path.join(S, f"receipt-{tag}.json")
    log = open(os.path.join(S, f"live-{tag}.log"), "wb")
    argv = [sys.executable, "-I", live, "--server", SRC, "--model", MODEL,
            "--model-sha256", MODEL_SHA, "--alias", "kama-r48-live", "--ctx", "64",
            "--threads", "1", "--server-fd", str(fd), "--witness-dir", wd,
            "--witness-timeout", "90", "--ready-timeout", "120", "--out", receipt]
    p = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT, pass_fds=(fd,))
    res = {"tag": tag, "memfd_sha": sha, "live_pid": p.pid, "memfd_fd": fd}
    ready = os.path.join(wd, "ready.json")
    t0 = time.monotonic()
    rj = None
    while time.monotonic() - t0 < 120:
        if os.path.exists(ready):
            try:
                rj = json.load(open(ready))
            except ValueError:
                rj = None
            if rj:
                break
        if p.poll() is not None:
            break
        time.sleep(0.05)
    res["ready"] = rj
    if rj:
        spid, port = rj["pid"], rj["port"]
        res["live_fd_table"] = fd_table(p.pid)
        res["live_memfd_from_third_party"] = open_as_third_party(p.pid, fd)
        res["server_fd_table"] = fd_table(spid)
        res["server_exe"] = os.readlink(f"/proc/{spid}/exe")
        st = os.stat(f"/proc/{spid}/exe")
        res["server_exe_stat"] = {"nlink": st.st_nlink,
                                  "dev": "%02x:%02x" % (os.major(st.st_dev), os.minor(st.st_dev)),
                                  "inode": str(st.st_ino)}
        res["server_memfd_maps"] = memfd_maps(spid)
        res["server_libs"] = lib_maps(spid)
        res["server_environ_ld"] = [k.decode(errors="replace") for k in
                                    open(f"/proc/{spid}/environ", "rb").read().split(b"\0")
                                    if k.startswith(b"LD_LIBRARY_PATH=")]
        # the server also answers: prove it is really serving from the memfd image
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=10) as r:
                res["health"] = [r.status, r.read(200).decode()]
        except OSError as exc:
            res["health"] = f"{type(exc).__name__}: {exc}"
        open(os.path.join(wd, "release"), "w").close()
    rc = p.wait(timeout=180)
    log.close()
    res["live_exit"] = rc
    if os.path.exists(receipt):
        r = json.load(open(receipt))
        res["receipt_server_exe"] = r.get("server_exe")
        res["receipt_server_fd"] = (r.get("server") or {}).get("fd")
        res["receipt_child_pid"] = r.get("child_pid")
        res["receipt_child_env_keys"] = r.get("child_env_keys")
    res["live_log_tail"] = open(os.path.join(S, f"live-{tag}.log"), "rb").read()[-2000:].decode(errors="replace")
    print(json.dumps(res, indent=1))
    os.close(fd)


main()
