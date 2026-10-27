"""Behaviour-equivalence probe: baseline live tool (build commit) vs the patched one.
Loads both modules by path, drives model_mapping / server_exe / code_mappings on the same
process, and compares the returned dicts field for field."""
import importlib.util, json, os, shutil, subprocess, sys, time

S = sys.argv[1]
base_p, patch_p = os.path.join(S, "lane/tools/kama-llamacpp-live.py"), os.path.join(S, "patch/tools/kama-llamacpp-live.py")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


A, B = load("live_base", base_p), load("live_patch", patch_p)
w = os.path.join(S, "eq")
os.makedirs(w, exist_ok=True)
exe = os.path.join(w, "sleeper")
shutil.copyfile(shutil.which("sleep") or "/usr/bin/sleep", exe)
os.chmod(exe, 0o700)
proc = subprocess.Popen([exe, "60"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
fails = 0


def cmp(label, x, y):
    global fails
    ok = x == y
    fails += not ok
    print(f"{'same' if ok else 'DIFF'} {label}")
    if not ok:
        print("  base :", json.dumps(x, sort_keys=True)[:600])
        print("  patch:", json.dumps(y, sort_keys=True)[:600])


try:
    time.sleep(0.2)
    for label, fn in (("code_mappings", lambda m: m.code_mappings(proc.pid)),
                      ("model_mapping", lambda m: m.model_mapping(proc.pid, exe)),
                      ("server_exe", lambda m: m.server_exe(os.getpid())),
                      ("code_mappings:absent-pid", lambda m: m.code_mappings(2 ** 22 + 7)),
                      ("model_mapping:absent-pid", lambda m: m.model_mapping(2 ** 22 + 7, exe))):
        cmp(label, fn(A), fn(B))
    decoy = os.path.join(w, "decoy")
    with open(decoy, "wb") as fh:
        fh.write(b"not the mapped file")
    os.replace(decoy, exe)
    cmp("code_mappings:after-rename-over", A.code_mappings(proc.pid), B.code_mappings(proc.pid))
    cmp("model_mapping:after-rename-over", A.model_mapping(proc.pid, exe), B.model_mapping(proc.pid, exe))
    for m in (A, B):
        cms = m.code_mappings(proc.pid)
        ent = [e for e in cms.get("mappings") or [] if e["path"].startswith(exe)]
        print(f"  {m.__name__}: {ent}")
finally:
    proc.kill()
    proc.wait()
print("EQ", "pass" if fails == 0 else f"fail={fails}")
sys.exit(0 if fails == 0 else 1)
