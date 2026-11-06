import json, os, socket, shutil, subprocess, sys, time, urllib.request, urllib.error, signal
SERVER = os.path.expanduser("~/.local/opt/llama-b11755/llama-server")
MODEL = os.path.expanduser("~/.cache/kama-shokunin/models/stories260K.gguf")
MID = "stories260K"
WORK = os.path.abspath("rx-work")
PROBE = os.path.abspath("probe-M.sh")

def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p

def http(method, url, body=None, timeout=60):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")

def status_of(port):
    try:
        code, txt = http("GET", f"http://127.0.0.1:{port}/v1/models", timeout=5)
    except Exception:
        return ""
    try:
        for e in json.loads(txt).get("data", []):
            if e.get("id") == MID:
                return (e.get("status") or {}).get("value", "")
    except Exception:
        return ""
    return ""

def wait_status(port, want, secs=90):
    end = time.time() + secs
    while time.time() < end:
        if status_of(port) == want:
            return True
        time.sleep(0.2)
    return False

def probe(port):
    p = subprocess.run(["bash", PROBE, "check", "--port", str(port), "--expect", MID, "--json",
                        "--timeout", "3", "--connect-timeout", "1"], capture_output=True, text=True, timeout=60)
    try:
        doc = json.loads(p.stdout)
        row = (doc.get("consumers") or doc.get("rows") or doc.get("results") or [])[0]
        return p.returncode, row.get("verdict"), row.get("reason")
    except Exception:
        return p.returncode, "UNPARSEABLE", p.stdout[:80] + p.stderr[:80]

def completion(port, max_tokens=2):
    return http("POST", f"http://127.0.0.1:{port}/v1/chat/completions",
                {"model": MID, "messages": [{"role": "user", "content": "hi"}], "max_tokens": max_tokens}, timeout=120)

def scenario(name, extra):
    shutil.rmtree(WORK, ignore_errors=True); os.makedirs(WORK)
    models = os.path.join(WORK, "models"); os.makedirs(models)
    shutil.copyfile(MODEL, os.path.join(models, MID + ".gguf"))
    port = free_port()
    log = open(os.path.join(WORK, "router.log"), "w")
    child = subprocess.Popen([SERVER, "--models-dir", models, "--models-max", "1",
                              "--host", "127.0.0.1", "--port", str(port)] + extra,
                             stdout=log, stderr=subprocess.STDOUT, cwd=WORK, start_new_session=True)
    out = {"scenario": name, "args": extra, "port": port}
    try:
        t0 = time.time()
        while time.time() - t0 < 60 and not status_of(port):
            time.sleep(0.2)
        out["status_start"] = status_of(port)
        if name.startswith("default-hasautoload"):
            code, txt = http("POST", f"http://127.0.0.1:{port}/models/unload", {"model": MID})
            out["unload_http"] = [code, txt[:120]]
            out["unloaded_reached"] = wait_status(port, "unloaded", 60)
        elif "sleep" in name:
            code, txt = http("POST", f"http://127.0.0.1:{port}/models/load", {"model": MID})
            out["load_http"] = [code, txt[:120]]
            out["loaded_reached"] = wait_status(port, "loaded", 60)
            out["sleeping_reached"] = wait_status(port, "sleeping", 60)
        else:
            out["unloaded_reached"] = wait_status(port, "unloaded", 30)
        out["status_before_probe"] = status_of(port)
        out["probe_start"] = probe(port)
        code, txt = completion(port)
        out["completion_start"] = {"http": code, "body": txt[:160]}
        out["status_after_completion"] = status_of(port)
        print(json.dumps(out))
    finally:
        try: os.killpg(child.pid, 15)
        except ProcessLookupError: pass
        try: child.wait(timeout=15)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, 9); child.wait()
        log.close()
        try:
            out["router_log_tail"] = open(os.path.join(WORK, "router.log")).read()[-1200:]
        except Exception:
            pass
        shutil.rmtree(WORK, ignore_errors=True)

if __name__ == "__main__":
    which = sys.argv[1]
    if which == "autoload":
        scenario("default-hasautoload-unloaded", [])
    elif which == "noautoload":
        scenario("no-autoload-unloaded", ["--no-models-autoload"])
    elif which == "sleep":
        scenario("sleep-idle-sleeping", ["--sleep-idle-seconds", "2"])
