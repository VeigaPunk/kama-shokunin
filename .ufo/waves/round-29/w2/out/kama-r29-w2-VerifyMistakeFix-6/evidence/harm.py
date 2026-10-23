import importlib.util, subprocess, sys, os

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m          # dataclass needs the module registered
    spec.loader.exec_module(m)
    return m

REPO = "/tmp/kama-w2-VerifyMistakeFix/clone"
patched = load(f"{REPO}/tools/prereg-time-check.py", "ptc_patched")
orig = load("/tmp/kama-w2-VerifyMistakeFix/tree-75b78bb4/tools/prereg-time-check.py", "ptc_orig")

def tracked(rev):
    out = subprocess.run(["git", "-C", REPO, "ls-tree", "-r", "--name-only", rev],
                         capture_output=True, text=True).stdout.splitlines()
    return [p for p in out if p.endswith((".md", ".json", ".py", ".txt", ".sh", ".yaml", ".yml", ".cfg"))]

def scan(mod, rev, label):
    files = tracked(rev)
    flagged = []
    errs = []
    for f in files:
        try:
            code, lines = mod.check(REPO, f, rev, -1)   # strict
        except Exception as e:
            errs.append((f, repr(e))); continue
        if code == 1:
            flagged.append((f, [l for l in lines if "FLAG" in l]))
        elif code == 2:
            errs.append((f, lines[0] if lines else ""))
    print(f"== {label} (rev {rev}, strict) :: {len(files)} files, flagged={len(flagged)}, errors={len(errs)}")
    for f, fl in flagged:
        print("  FLAG", f)
        for l in fl:
            print("      ", l.strip())
    for f, e in errs[:5]:
        print("  ERR", f, e)
    return flagged

print("### ORIG tool @ 513eba3b (baseline blindness)")
scan(orig, "513eba3b", "ORIG")
print()
print("### PATCHED tool @ 513eba3b (does the widened regex create new flags?)")
f_p = scan(patched, "513eba3b", "PATCHED")
print()
print("### PATCHED tool @ 75b78bb4 (the mined case)")
scan(patched, "75b78bb4", "PATCHED")
print()
print("### PATCHED tool @ d8bf1804")
scan(patched, "d8bf1804", "PATCHED")
print("HARMSCAN_DONE")
