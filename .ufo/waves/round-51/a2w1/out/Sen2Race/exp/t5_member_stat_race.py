#!/usr/bin/env python3
"""Deterministically replace the counter's replay-owned member after own_exe has
opened/fstat'ed/hashed /proc/<pid>/exe but immediately before its os.stat(member)."""
import importlib.util, os, shutil, socket, subprocess, time

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
HOST = "/home/vgpnk/.local/opt/llama-b11909/llama-server"
MODEL = "/fast/scratch/hyaku/kama-r51/Sen2Race/model-xfs.gguf"
OUT = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/Sen2Race/exp"
MEMBER = os.path.join(OUT, "race/member-stat-race/llama-server")

spec = importlib.util.spec_from_file_location("r51c1", LANE + "/tools/round51-replay-exe-audit.py")
ctr = importlib.util.module_from_spec(spec); spec.loader.exec_module(ctr)
os.makedirs(os.path.dirname(MEMBER), exist_ok=True)
log = open(os.path.join(OUT, "server-race.log"), "wb")
p = subprocess.Popen([HOST, "-m", MODEL, "--alias", "race", "--host", "127.0.0.1",
                      "--port", "18197", "-c", "64", "-t", "1", "--no-webui", "--offline"],
                     stdout=log, stderr=subprocess.STDOUT)
try:
    t0 = time.monotonic()
    while time.monotonic() - t0 < 40:
        try:
            socket.create_connection(("127.0.0.1", 18197), timeout=0.5).close(); break
        except OSError:
            if p.poll() is not None: raise RuntimeError("server exited; see server-race.log")
            time.sleep(0.2)
    else: raise RuntimeError("server did not listen")
    host_st = os.stat(HOST)
    print("running exe inode:", host_st.st_ino, "dev:", "%02x:%02x" % (os.major(host_st.st_dev), os.minor(host_st.st_dev)))
    shutil.copyfile(HOST, MEMBER); os.chmod(MEMBER, 0o755)
    copy_st = os.stat(MEMBER)
    print("member before call: copy inode", copy_st.st_ino, "(distinct from running exe)")
    real_stat = os.stat
    injected = []
    def swap_then_stat(path, *args, **kwargs):
        if os.fspath(path) == MEMBER and not injected:
            # own_exe has already opened/fstat'ed/hashed /proc/<pid>/exe; this is its
            # next and only stat of the replay-controlled member path.
            os.unlink(MEMBER)
            os.link(HOST, MEMBER)
            injected.append((real_stat(MEMBER).st_ino, real_stat(f"/proc/{p.pid}/exe").st_ino))
            print("replacement at member os.stat boundary: member/exe inode", injected[-1])
        return real_stat(path, *args, **kwargs)
    ctr.os.stat = swap_then_stat
    probs = []
    got = ctr.own_exe(p.pid, MEMBER, probs)
    ctr.os.stat = real_stat
    print("own_exe got:", got)
    print("own_exe problems:", probs)
    print("PASS after between-observations replacement:", not probs and bool(injected) and injected[0][0] == injected[0][1])
finally:
    ctr.os.stat = os.stat
    p.terminate()
    try: p.wait(timeout=10)
    except subprocess.TimeoutExpired: p.kill(); p.wait()
    log.close()
