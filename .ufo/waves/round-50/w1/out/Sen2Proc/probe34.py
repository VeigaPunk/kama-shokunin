#!/usr/bin/env python3
"""Sen2Proc probes 3 and 4: model_mapping (live tool) and mapped_model (counter) against
(a) the mapped model deleted while the server runs, (b) a model on btrfs (/home).
Starts one llama-server from the b11909 install and stops it itself (loopback, own port)."""
import importlib.util
import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.request

S = "/fast/scratch/hyaku/kama-r50/Sen2Proc"
SERVER = "/home/vgpnk/.local/opt/llama-b11909/llama-server"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


c1 = load("c1", os.path.join(S, "imp", "c1.py"))
live = load("live", os.path.join(S, "imp", "live.py"))


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def wait_health(port, proc, timeout=90):
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        if proc.poll() is not None:
            raise RuntimeError(f"server exited rc={proc.returncode}")
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1) as r:
                if r.status == 200:
                    return round(time.monotonic() - t0, 2)
        except Exception:
            pass
        time.sleep(0.05)
    raise RuntimeError("health timeout")


def devstr(dev):
    return "%02x:%02x" % (os.major(dev), os.minor(dev))


def run(model_path, delete_after_ready=False):
    model = os.path.abspath(model_path)
    port = free_port()
    log = open(os.path.join(S, "server.log"), "wb")
    proc = subprocess.Popen(
        [SERVER, "-m", model, "--alias", "sen2proc", "--host", "127.0.0.1",
         "--port", str(port), "-c", "256", "-t", "1", "--no-webui", "--offline"],
        stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    out = {"model_arg": model, "port": port, "pid": proc.pid}
    try:
        out["ready_after_s"] = wait_health(port, proc)
        st_before = os.stat(model)
        out["stat_before"] = {"dev": devstr(st_before.st_dev), "st_dev_raw": st_before.st_dev,
                              "inode": st_before.st_ino, "size": st_before.st_size}
        out["mountinfo"] = [ln.strip() for ln in open("/proc/self/mountinfo")
                            if model in ln]
        with open(f"/proc/{proc.pid}/maps") as fh:
            rows = [ln.rstrip("\n") for ln in fh if model.encode() in ln.encode()]
        out["maps_rows_path"] = rows[:4]
        devino = set()
        for ln in rows:
            f = ln.split(None, 5)
            devino.add((f[3], f[4]))
        out["maps_dev_inode"] = sorted(devino)
        if delete_after_ready:
            os.unlink(model)
            time.sleep(0.3)
            with open(f"/proc/{proc.pid}/maps") as fh:
                drows = [ln.rstrip("\n") for ln in fh if model in ln or "(deleted)" in ln]
            out["maps_rows_after_unlink"] = [r for r in drows if model in r][:4]
            out["maps_deleted_rows"] = [r for r in drows if "(deleted)" in r][:6]
        probs = []
        out["live_model_mapping"] = live.model_mapping(proc.pid, model)
        out["counter_mapped_model"] = c1.mapped_model(proc.pid, probs)
        out["counter_problems"] = probs
        out["server_alive_at_read"] = proc.poll() is None
    finally:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except OSError:
            pass
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except OSError:
                pass
            proc.wait()
        log.close()
        out["rc"] = proc.returncode
        s = socket.socket()
        s.settimeout(2)
        try:
            s.connect(("127.0.0.1", port))
            out["port_refuses_after_stop"] = False
        except OSError:
            out["port_refuses_after_stop"] = True
        finally:
            s.close()
    return out


if __name__ == "__main__":
    scenario, path = sys.argv[1], sys.argv[2]
    print(json.dumps({"scenario": scenario, "result": run(path, scenario == "deleted")}, indent=1))
