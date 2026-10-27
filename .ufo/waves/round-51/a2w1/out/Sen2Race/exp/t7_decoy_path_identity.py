#!/usr/bin/env python3
"""Directly observe a byte-identical install copied elsewhere and hardlinked over member."""
import importlib.util, os, shutil, socket, subprocess, time
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
HOSTDIR = "/home/vgpnk/.local/opt/llama-b11909"
MODEL = "/fast/scratch/hyaku/kama-r51/Sen2Race/model-xfs.gguf"
ROOT = "/fast/scratch/hyaku/kama-r51/Sen2Race/decoy-path-proof"
DECOY = os.path.join(ROOT, "decoy-install")
MEMBER = os.path.join(ROOT, "work/server/llama-b11909/llama-server")
LOG = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/Sen2Race/exp/server-decoy-path.log"
spec = importlib.util.spec_from_file_location("kama_live", LANE + "/tools/kama-llamacpp-live.py")
live = importlib.util.module_from_spec(spec); spec.loader.exec_module(live)
shutil.copytree(HOSTDIR, DECOY, symlinks=True)
decoy_server = os.path.join(DECOY, "llama-server")
os.makedirs(os.path.dirname(MEMBER), exist_ok=True)
shutil.copyfile(decoy_server, MEMBER); os.chmod(MEMBER, 0o755)
os.unlink(MEMBER); os.link(decoy_server, MEMBER)
log = open(LOG, "wb")
p = subprocess.Popen([decoy_server, "-m", MODEL, "--alias", "decoy", "--host", "127.0.0.1",
                      "--port", "18195", "-c", "64", "-t", "1", "--no-webui", "--offline"],
                     stdout=log, stderr=subprocess.STDOUT)
try:
    t0 = time.monotonic()
    while time.monotonic() - t0 < 40:
        try:
            socket.create_connection(("127.0.0.1", 18195), timeout=0.5).close(); break
        except OSError:
            if p.poll() is not None: raise RuntimeError("decoy server exited; see log")
            time.sleep(0.2)
    else: raise RuntimeError("decoy server did not listen")
    se = live.server_exe(p.pid)
    ms = os.stat(MEMBER)
    print("server_exe:", se)
    print("member path:", MEMBER)
    print("member stat dev/inode:", "%02x:%02x" % (os.major(ms.st_dev), os.minor(ms.st_dev)), ms.st_ino)
    print("exe readlink path differs from member:", os.path.realpath(se["path"]) != os.path.realpath(MEMBER))
    print("exe dev/inode equals member:", se["dev"] == "%02x:%02x" % (os.major(ms.st_dev), os.minor(ms.st_dev)) and str(se["inode"]) == str(ms.st_ino))
finally:
    p.terminate()
    try: p.wait(timeout=10)
    except subprocess.TimeoutExpired: p.kill(); p.wait()
    log.close()
