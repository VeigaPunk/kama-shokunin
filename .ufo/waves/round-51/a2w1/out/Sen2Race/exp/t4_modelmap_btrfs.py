#!/usr/bin/env python3
"""Sen2Race: (3) does maps' dev agree with st_dev on btrfs? (live tool model_mapping(),
(2) own_exe path rebind, mid-call TOCTOU."""
import importlib.util, os, shutil, socket, subprocess, sys, time, json

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = "/home/vgpnk/.local/opt/llama-b11909/llama-server"
MB = os.path.join(D, "exp/models/model-btrfs.gguf")
MX = "/fast/scratch/hyaku/kama-r51/Sen2Race/model-xfs.gguf"

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
live = load("kama_live", LANE + "/tools/kama-llamacpp-live.py")
ctr = load("r51c1", LANE + "/tools/round51-replay-exe-audit.py")

def start(model, port, log):
    p = subprocess.Popen([HOST, "-m", model, "--alias", "sen2race", "--host", "127.0.0.1",
                          "--port", str(port), "-c", "64", "-t", "1", "--no-webui", "--offline"],
                         stdout=open(log, "wb"), stderr=subprocess.STDOUT)
    t0 = time.monotonic()
    while time.monotonic() - t0 < 40:
        try:
            socket.create_connection(("127.0.0.1", port), timeout=0.5).close(); return p
        except OSError:
            if p.poll() is not None: raise SystemExit(f"server exited rc={p.returncode}; see {log}")
            time.sleep(0.2)
    raise SystemExit("server did not listen")

def stop(p):
    p.terminate()
    try: p.wait(10)
    except subprocess.TimeoutExpired: p.kill(); p.wait()
    time.sleep(0.3)

print("== server with model on btrfs (/home, st_dev 0x%x) ==" % os.stat(MB).st_dev)
p = start(MB, 18199, os.path.join(D, "exp/server-btrfs.log"))
try:
    time.sleep(0.5)
    se = live.server_exe(p.pid)
    st = os.stat(os.path.realpath(se["path"]))
    py = "%02x:%02x" % (os.major(st.st_dev), os.minor(st.st_dev))
    print("server_exe:", json.dumps(se, sort_keys=True))
    print("os.stat(exe) dev=%s inode=%s | server_exe dev/inode match: %s/%s" % (
        py, st.st_ino, se["dev"] == py, str(se["inode"]) == str(st.st_ino)))
    mm = live.model_mapping(p.pid, MB)
    print("model_mapping(model on btrfs):", json.dumps(mm, sort_keys=True))
    probs = []
    observed = ctr.mapped_model(p.pid, probs)
    print("counter mapped_model(model on btrfs):", observed, "| problems:", probs)
    rows = []
    with open(f"/proc/{p.pid}/maps") as fh:
        for row in fh:
            f = row.split(None, 5)
            if len(f) == 6 and f[5].strip() == os.path.realpath(MB):
                rows.append((f[3], f[4]))
    print("maps rows for the model:", rows, "| os.stat model dev:", py)

    # (2) own_exe against an honest extracted-member copy, then against a rebound path
    member = os.path.join(D, "exp/race/server/build/bin/llama-server")
    os.makedirs(os.path.dirname(member), exist_ok=True)
    if os.path.exists(member): os.unlink(member)
    shutil.copyfile(HOST, member); os.chmod(member, 0o755)
    print()
    print("== (2) counter own_exe, member = a copy of the same bytes (inode %d) ==" % os.stat(member).st_ino)
    probs = []
    got = ctr.own_exe(p.pid, member, probs)
    print("own_exe -> got", got, "probs", probs)
    os.unlink(member); os.link(HOST, member)
    print("-- rebound member to a hardlink of the running image (inode %d) --" % os.stat(member).st_ino)
    probs2 = []
    got2 = ctr.own_exe(p.pid, member, probs2)
    print("own_exe -> got", got2, "probs", probs2)
finally:
    stop(p)

print()
print("== control: same bytes, model on xfs (/fast) ==")
p = start(MX, 18198, os.path.join(D, "exp/server-xfs.log"))
try:
    time.sleep(0.5)
    mm = live.model_mapping(p.pid, MX)
    print("model_mapping(model on xfs):", json.dumps(mm, sort_keys=True))
finally:
    stop(p)
