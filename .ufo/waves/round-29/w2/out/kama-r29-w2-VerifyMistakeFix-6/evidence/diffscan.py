import importlib.util, subprocess, sys

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m

REPO = "/tmp/kama-w2-VerifyMistakeFix/clone"
patched = load(f"{REPO}/tools/prereg-time-check.py", "ptc_patched")
orig = load("/tmp/kama-w2-VerifyMistakeFix/tree-75b78bb4/tools/prereg-time-check.py", "ptc_orig")

def tracked(rev):
    out = subprocess.run(["git", "-C", REPO, "ls-tree", "-r", "--name-only", rev],
                         capture_output=True, text=True).stdout.splitlines()
    return [p for p in out if p.endswith((".md", ".json", ".py", ".txt", ".sh", ".yaml", ".yml", ".cfg"))]

def flags(mod, rev, path, mf):
    try:
        code, lines = mod.check(REPO, path, rev, mf)
    except Exception:
        return None
    if code != 1:
        return []
    return [l.strip() for l in lines if "FLAG" in l]

for mf, label in ((86400, "default-horizon(86400)"), (-1, "strict")):
    files = tracked("513eba3b")
    new_only = []
    for f in files:
        po = flags(orig, "513eba3b", f, mf)
        pp = flags(patched, "513eba3b", f, mf)
        if po is None or pp is None:
            continue
        if len(pp) > len(po):
            new_only.append((f, po, pp))
    print(f"### mf={mf} ({label}): {len(files)} files; PATCHED-only extra flags in {len(new_only)} file(s)")
    for f, po, pp in new_only:
        print("  FILE", f)
        print("    ORIG   :", po or "(none)")
        for l in pp:
            print("    PATCHED:", l)
    print()
print("DIFF_DONE")
