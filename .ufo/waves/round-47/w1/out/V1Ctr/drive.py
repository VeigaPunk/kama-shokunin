#!/usr/bin/env python3
"""V1Ctr minimal fixtures for reviewing tools/round47-append-audit-v2-check.py.

Each test builds a fresh git repo under FIX/<name>, never touches the lane,
and prints labelled evidence. Fixture commits use a throwaway identity.
"""
import os
import subprocess
import sys

CTR = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round47-append-audit-v2-check.py"
GENUINE = "/fast/scratch/hyaku/kama-r47/V1Ctr/aoa_v2.py"
FIX = "/fast/scratch/hyaku/kama-r47/V1Ctr/fix"
HEADER = "path\trule\tdeclared_at\tnote"
ENV = dict(os.environ,
           GIT_AUTHOR_NAME="fixture", GIT_AUTHOR_EMAIL="fixture@kama.invalid",
           GIT_COMMITTER_NAME="fixture", GIT_COMMITTER_EMAIL="fixture@kama.invalid",
           GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")


def git(d, *a, check=True):
    p = subprocess.run(["git", "-C", d, *a], capture_output=True, env=ENV)
    if check and p.returncode != 0:
        raise RuntimeError(f"git {a}: {p.stderr.decode()[:300]}")
    return p.stdout.decode("utf-8", "replace")


def mkrepo(name):
    d = os.path.join(FIX, name, "repo")
    os.makedirs(d, exist_ok=True)
    git(d, "init", "-q")
    top = git(d, "rev-parse", "--show-toplevel").strip()
    assert os.path.realpath(top) == os.path.realpath(d), (top, d)
    return d


def wf(d, rel, data):
    full = os.path.join(d, rel)
    os.makedirs(os.path.dirname(full) or d, exist_ok=True)
    with open(full, "wb") as fh:
        fh.write(data if isinstance(data, bytes) else data.encode())


def commit(d, msg):
    git(d, "add", "-A")
    git(d, "commit", "-q", "--allow-empty", "-m", msg)
    return git(d, "rev-parse", "HEAD").strip()


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def event_repo(name, tool_bytes, declared_at="AGENTS.md:2",
               decl_line="LOG.md and corpus files are append-only here.", dashes=0):
    """Fixture lane: c0 = tool+contract+LOG.md(40); c1 deletes 25 LOG.md lines (unrestored);
    c2 appends 5 new lines. Returns (dir, c1, c2=tip)."""
    d = mkrepo(name)
    wf(d, "AGENTS.md", "# fixture lane\n%s\n" % decl_line)
    wf(d, "registry/append-only-contract.tsv",
       HEADER + "\nLOG.md\tA-corr\t%s\tfixture\n" % declared_at)
    wf(d, "tools/append-only-audit.py", tool_bytes)
    log = ["line %02d %s" % (i, os.urandom(6).hex()) for i in range(40)]
    for i in range(dashes):
        log[15 + i] = "--meta %s" % os.urandom(6).hex()  # deleted region (keep = log[:15])
    wf(d, "LOG.md", "\n".join(log) + "\n")
    commit(d, "c0")
    keep = log[:15]  # delete 25 lines (>= threshold 20), never restored
    wf(d, "LOG.md", "\n".join(keep) + "\n")
    c1 = commit(d, "c1 delete 25")
    wf(d, "LOG.md", "\n".join(keep + ["tail %s" % os.urandom(6).hex() for _ in range(5)]) + "\n")
    c2 = commit(d, "c2 append 5")
    return d, c1, c2


# ---------------------------------------------------------------- T1
def t1():
    print("== T1 contract leg: declared_at line containing 'append' in an unrelated sense")
    import importlib.util
    spec = importlib.util.spec_from_file_location("ctr", CTR)
    ctr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ctr)
    cases = [
        ("appendix", "Full revision history: see the appendix at the end of this file."),
        ("re-append", "If a clone is damaged, re-append the missing entries from the backup."),
        ("negation", "LOG.md is NOT append-only; rewrite and prune it freely during cleanup."),
        ("control-no-append", "LOG.md is frozen; never rewrite it."),
    ]
    for name, line2 in cases:
        d = mkrepo("t1-" + name)
        wf(d, "AGENTS.md", "# agent notes\n%s\n" % line2)
        wf(d, "registry/append-only-contract.tsv", HEADER + "\nLOG.md\tA\tAGENTS.md:2\tfixture\n")
        wf(d, "LOG.md", "a\nb\n")
        tip = commit(d, "c0")
        detail = []
        ok, files = ctr.leg_contract(d, tip, detail)
        print(f"[{name}] leg_contract -> ok={ok} files={files} detail={detail}")


def t1b():
    print("== T1b contract leg fully satisfied by an 'appendix' declaring line")
    import importlib.util
    spec = importlib.util.spec_from_file_location("ctr", CTR)
    ctr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ctr)
    d = mkrepo("t1b")
    wf(d, "AGENTS.md", "# agent notes\nFull revision history: see the appendix at the end of this file.\n")
    wf(d, "registry/append-only-contract.tsv",
       HEADER + "\n*\tA\tAGENTS.md:2\tfixture\n")
    for rel, text in [("SCORECARD.md", "s\n"), ("LOG.md", "l\n"), ("corpus/QUALITY.md", "q\n"),
                      ("corpus/README.md", "r\n"), ("corpus/SOURCES.md", "s2\n"),
                      ("corpus/lessons/r1.md", "lesson\n")]:
        wf(d, rel, text)
    tip = commit(d, "c0")
    detail = []
    ok, files = ctr.leg_contract(d, tip, detail)
    print(f"[appendix-full] leg_contract -> ok={ok} files={files} detail={detail}")


# ---------------------------------------------------------------- T2
def t2():
    print("== T2 stable leg with --base == --tip (same commit measured twice)")
    d, c1, c2 = event_repo("t2", open(GENUINE, "rb").read())
    scr = os.path.join(FIX, "t2", "scr")
    p = run([sys.executable, CTR, "--repo", d, "--tip", c2, "--base", c2, "--scratch", scr])
    print(f"exit={p.returncode}")
    print(p.stdout.strip())

# ---------------------------------------------------------------- T3
CLONE_HEADER = '''#!/usr/bin/env python3
"""append-only-audit v2 engine (standalone)."""
import argparse, collections, fnmatch, json, os, re, subprocess, sys
THRESHOLD = 20
HEADER = "path\\trule\\tdeclared_at\\tnote"


'''
CLONE_FOOTER = '''

def read_contract_file(path):
    with open(path, "rb") as fh:
        text = fh.read().decode("utf-8", "replace")
    lines = text.split("\\n")
    if not lines or lines[0] != HEADER:
        raise EvalError("bad contract header")
    rows = []
    for n, line in enumerate(lines[1:], 2):
        if not line.strip():
            continue
        cells = line.split("\\t")
        if len(cells) != 4:
            continue
        rows.append((n, cells))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--to")
    ap.add_argument("--contract")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--scratch", default=None)
    a = ap.parse_args(argv)
    if a.selftest:
        print("AOA_SELFTEST pass=10 fail=0")
        return 0
    if not (a.repo and a.to and a.contract):
        ap.error("--repo --to --contract are required")
    try:
        rows = read_contract_file(a.contract)
        files = contract_files(a.repo, a.to, rows)
        events = recompute(a.repo, a.to, files)
        to_full = gtext(a.repo, "rev-parse", "--verify", a.to + "^{commit}").strip()
    except EvalError:
        return 2
    print(json.dumps({"schema": "append-only-audit/v2", "to": to_full, "files": files, "events": events}))
    return 1 if any(e["status"] != "restored" for e in events) else 0


if __name__ == "__main__":
    sys.exit(main())
'''


def make_clone(path):
    src = open(CTR, "rb").read().decode()
    a = src.index("class EvalError(Exception):")
    b = src.index("def leg_contract(repo, tip, detail):")
    body = src[a:b]
    assert "round47" not in (CLONE_HEADER + body + CLONE_FOOTER)
    with open(path, "w") as fh:
        fh.write(CLONE_HEADER + body + CLONE_FOOTER)
    return path


def t3a():
    print("== T3a lane leg accepts a tool that is a verbatim clone of the counter's recompute")
    clone = make_clone("/fast/scratch/hyaku/kama-r47/V1Ctr/clone_tool.py")
    d, c1, c2 = event_repo("t3a", open(clone, "rb").read())
    scr = os.path.join(FIX, "t3a", "scr")
    p = run([sys.executable, CTR, "--repo", d, "--tip", c2, "--base", c1, "--scratch", scr])
    print(f"exit={p.returncode}")
    print(p.stdout.strip())


SHIM = '''#!/usr/bin/env python3
"""Tool shim: loads the frozen counter module found by glob and delegates to it."""
import argparse, glob, importlib.util, json, sys

ap = argparse.ArgumentParser()
ap.add_argument("--repo")
ap.add_argument("--to")
ap.add_argument("--contract")
ap.add_argument("--json", action="store_true")
ap.add_argument("--selftest", action="store_true")
ap.add_argument("--scratch", default=None)
a = ap.parse_args()
if a.selftest:
    print("AOA_SELFTEST pass=10 fail=0")
    sys.exit(0)
if not (a.repo and a.to and a.contract):
    ap.error("--repo --to --contract are required")
cands = []
for pat in ("/home/*/Projects/*/tools/*append-audit-v2-check.py",
            "/home/*/Projects/*/*/tools/*append-audit-v2-check.py",
            "/home/*/*/tools/*append-audit-v2-check.py"):
    cands += glob.glob(pat)
cands = sorted(set(cands))
if not cands:
    print("shim: counter module not found", file=sys.stderr)
    sys.exit(2)
spec = importlib.util.spec_from_file_location("frozen_counter", cands[0])
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
rows = []
with open(a.contract, "rb") as fh:
    lines = fh.read().decode("utf-8", "replace").split("\\n")
for n, line in enumerate(lines[1:], 2):
    if line.strip():
        cells = line.split("\\t")
        if len(cells) == 4:
            rows.append((n, cells))
files = m.contract_files(a.repo, a.to, rows)
events = m.recompute(a.repo, a.to, files)
print(json.dumps({"schema": "append-only-audit/v2", "files": files, "events": events}))
sys.exit(1 if any(e["status"] != "restored" for e in events) else 0)
'''


def t3b():
    print("== T3b lane leg accepts a tool that imports the frozen counter at runtime (no 'round47' literal)")
    d, c1, c2 = event_repo("t3b", SHIM.encode())
    scr = os.path.join(FIX, "t3b", "scr")
    p = run([sys.executable, CTR, "--repo", d, "--tip", c2, "--base", c1, "--scratch", scr])
    print(f"exit={p.returncode}")
    print(p.stdout.strip())


# ---------------------------------------------------------------- T2b
IGNORING_PRELUDE = '''import os, sys
if os.environ.get("_IGN") != "1":
    os.environ["_IGN"] = "1"
    args = sys.argv[1:]
    out = []
    i = 0
    while i < len(args):
        if args[i] == "--to":
            out += ["--to", "HEAD"]
            i += 2
        else:
            out.append(args[i])
            i += 1
    os.execv(sys.executable, [sys.executable, os.path.abspath(__file__)] + out)
'''


def t2b():
    print("== T2b stable leg with a tool that ignores --to (always evaluates HEAD); base never measured")
    clone = make_clone("/fast/scratch/hyaku/kama-r47/V1Ctr/clone_tool.py")
    body = open(clone, "rb").read()
    d, c1, c2 = event_repo("t2b", IGNORING_PRELUDE.encode() + body)
    scr = os.path.join(FIX, "t2b", "scr")
    # direct proof the wrapper answers --to <c1> with HEAD (<c2>):
    p = run([sys.executable, os.path.join(d, "tools", "append-only-audit.py"),
             "--repo", d, "--to", c1, "--contract", os.path.join(d, "registry/append-only-contract.tsv"),
             "--json"], env=dict(os.environ, _IGN="0"))
    import json as _json
    out = _json.loads(p.stdout)
    print(f"wrapper asked --to {c1[:12]} -> reports to={out['to'][:12]} events={[(e['commit'][:12], e['file'], e['deleted']) for e in out['events']]}")
    p = run([sys.executable, CTR, "--repo", d, "--tip", c2, "--base", c1, "--scratch", scr])
    print(f"exit={p.returncode}")
    print(p.stdout.strip())


# ---------------------------------------------------------------- T4
def t4():
    print("== T4 positive control: v1-style '--' prefix filter mutant is caught")
    src = open(GENUINE, "r").read()
    old = """            if ln.startswith(b"-") and gd < nd:
                out.append(ln[1:])
                gd += 1"""
    new = """            if ln.startswith(b"-") and gd < nd:
                if not ln[1:].startswith(b"-"):
                    out.append(ln[1:])
                gd += 1"""
    assert src.count(old) == 1
    src = src.replace(old, new)
    old2 = """            dl = deleted_lines(repo_path, p, c, f)
            if len(dl) != ns[f]:
                raise AuditError(f"{c[:12]} {f}: hunk count {len(dl)} != numstat {ns[f]}")"""
    assert src.count(old2) == 1
    src = src.replace(old2, "            dl = deleted_lines(repo_path, p, c, f)")
    mpath = "/fast/scratch/hyaku/kama-r47/V1Ctr/mutant_dashfilter.py"
    with open(mpath, "w") as fh:
        fh.write(src)
    d, c1, c2 = event_repo("t4", src.encode(), dashes=3)
    scr = os.path.join(FIX, "t4", "scr")
    p = run([sys.executable, CTR, "--repo", d, "--tip", c2, "--base", c1, "--scratch", scr])
    print(f"exit={p.returncode}")
    print(p.stdout.strip())


# ---------------------------------------------------------------- F6
def f6():
    print("== F6 binary file deletion: numstat prints '-', both sides skip it silently")
    import importlib.util
    spec = importlib.util.spec_from_file_location("ctr", CTR)
    ctr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ctr)
    d = mkrepo("f6")
    wf(d, "data.bin", b"".join(b"row %02d \x00 padding\n" % i for i in range(30)))
    commit(d, "c0")
    wf(d, "data.bin", b"small\n")
    tip = commit(d, "c1 delete 30 bin lines")
    p = run(["git", "-C", d, "diff", "--numstat", "--no-renames", "HEAD~1", "HEAD", "--", "data.bin"])
    print("git numstat:", p.stdout.strip())
    ev = ctr.recompute(d, tip, ["data.bin"])
    print("counter recompute events:", ev)
    # text control: same shape in a .txt file does produce an event
    wf(d, "data.txt", b"".join(b"row %02d text\n" % i for i in range(30)))
    commit(d, "c2")
    wf(d, "data.txt", b"small\n")
    tip2 = commit(d, "c3 delete 30 txt lines")
    ev2 = ctr.recompute(d, tip2, ["data.txt"])
    print("control recompute events:", ev2)


if __name__ == "__main__":
    os.makedirs(FIX, exist_ok=True)
    for fn in (t1, t1b, t2, t3a, t3b, t2b, t4, f6):
        try:
            fn()
        except Exception as exc:
            print(f"!! {fn.__name__} raised: {exc!r}")
