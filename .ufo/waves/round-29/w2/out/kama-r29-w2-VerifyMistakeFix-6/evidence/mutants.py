import importlib.util, subprocess, sys, os, tempfile, shutil, pathlib

REPO = "/tmp/kama-w2-VerifyMistakeFix/clone"
COMMITTED = f"{REPO}/tools/prereg-time-check.py"
WTREE = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/prereg-time-check.py"

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m

cm = load(COMMITTED, "ptc_committed")
wt = load(WTREE, "ptc_wtree")

SCRATCH = "/tmp/kama-w2-VerifyMistakeFix/scratch_mut"
os.makedirs(SCRATCH, exist_ok=True)

# M02: remove plain-space recognition from TIME_RE only
TIME_RE_SRC = 'TIME_RE = re.compile(r"\\d{4}-\\d{2}-\\d{2}(?:T| ~| )\\d{2}:\\d{2}(?::\\d{2})?Z")'
PARSE_SRC = '    m = re.fullmatch(r"(\\d{4})-(\\d{2})-(\\d{2})(?:T| ~| )(\\d{2}):(\\d{2})(?::(\\d{2}))?Z", text)'
SECS_SRC = "    y, mo, d, h, mi, s = (int(g) if g else 0 for g in m.groups())"

def m02(src):
    new = TIME_RE_SRC.replace("(?:T| ~| )", "(?:T| ~)")
    assert new != TIME_RE_SRC
    return src.replace(TIME_RE_SRC, new)

def m05(src):
    new = PARSE_SRC.replace("(?:T| ~| )", "(?:T| ~)")
    assert new != PARSE_SRC
    return src.replace(PARSE_SRC, new)

def m07(src):
    # zero parsed seconds: force the seconds group to 0 regardless of value
    new = SECS_SRC.replace("s = (int(g) if g else 0 for g in m.groups())",
                           "s = (0 if g is not None else 0 for g in m.groups())")
    assert new != SECS_SRC
    assert SECS_SRC in src, "SECS_SRC not present in source"
    return src.replace(SECS_SRC, new)

def m07surgical(src):
    # surgical M07 as MutateTimeCheck describes it: parse the seconds group but
    # force it to 0, leaving every other group intact.
    new = ("    y, mo, d, h, mi, _s = (int(g) if g else 0 for g in m.groups())\n"
           "    s = 0")
    assert SECS_SRC in src, "SECS_SRC not present in source"
    return src.replace(SECS_SRC, new)

def run_selftest(src_text, label):
    d = tempfile.mkdtemp(prefix="mut-", dir="/tmp/kama-w2-VerifyMistakeFix")
    p = os.path.join(d, "ptc.py")
    pathlib.Path(p).write_text(src_text)
    m = load(p, "mut_" + label)
    out = []
    # replicate selftest but capture per-case results
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = m.selftest(SCRATCH)
    text = buf.getvalue()
    fails = [l for l in text.splitlines() if l.startswith("[FAIL]")]
    npass = len([l for l in text.splitlines() if l.startswith("[PASS]")])
    shutil.rmtree(d, ignore_errors=True)
    return rc, npass, fails

com_src = pathlib.Path(COMMITTED).read_text()
wt_src = pathlib.Path(WTREE).read_text()

for label, fn in (("M02-no-plain-space-in-TIME_RE", m02),
                  ("M05-no-plain-space-in-parse_iso", m05),
                  ("M07-zero-parsed-seconds", m07),
                  ("M07surgical-zero-seconds-only", m07surgical)):
    print(f"=== {label} ===")
    for base, bsrc in (("committed-513eba3b", com_src), ("working-tree", wt_src)):
        try:
            msrc = fn(bsrc)
        except AssertionError as e:
            print(f"  {base}: MUTATION SOURCE NOT FOUND ({e})"); continue
        rc, npass, fails = run_selftest(msrc, label + base)
        verdict = "KILLED" if rc != 0 else "SURVIVED"
        print(f"  {base:22s} selftest exit={rc} PASS={npass} verdict={verdict}")
        for f in fails:
            print(f"      {f}")
print("MUTANTS_DONE")
