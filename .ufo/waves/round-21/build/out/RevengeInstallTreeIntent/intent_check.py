#!/usr/bin/env python3
"""RevengeInstallTreeIntent probe (KamaR21). Read-only on the lane (git show only),
on the installed tree and on the upstream tarball. Writes summary.json beside this
file; the sandbox directory it creates under /tmp is removed before exit."""
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tarfile
import tempfile

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
INSTALL = "/home/vgpnk/.local/opt/llama-b11755"
TARBALL = "/home/vgpnk/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz"
HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = "tools/kama-llamacpp-live.py"
CHECK = "tests/llamacpp-live/check-receipt.py"
INTRO = "b8e485c"
FROZEN = "7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d"
DRAFT = "a29bb84abbb8b4d328f5970a89e448330a3a42ac"
PIN = "6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c"
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append({"check": name, "ok": bool(ok), "detail": str(detail)})
    line = ("PASS " if ok else "FAIL ") + name
    if detail != "":
        line += " :: " + str(detail)
    print(line)


def git_show(rev, path):
    r = subprocess.run(["git", "-C", LANE, "show", f"{rev}:{path}"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"git show {rev}:{path} failed rc={r.returncode}: {r.stderr.strip()}")
    return r.stdout


def func_body(src, name):
    a = src.index(f"\ndef {name}(") + 1
    b = src.find("\ndef ", a + 5)
    return src[a:] if b == -1 else src[a:b]


def ns_for(rev, names):
    src = git_show(rev, TOOL)
    ns = {"os": os, "stat": stat, "hashlib": hashlib}
    for n in names:
        exec(func_body(src, n), ns)
    return ns


def sha16(text):
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def write_file(path, data):
    with open(path, "wb") as fh:
        fh.write(data)


# 1. install_tree() body identity across the three revisions
bodies = {r: sha16(func_body(git_show(r, TOOL), "install_tree")) for r in (INTRO, FROZEN, DRAFT)}
print("install_tree() body sha256[:16]:", bodies)
check("install_tree body identical at introduction, frozen tip and draft",
      len(set(bodies.values())) == 1, bodies)

# 2. producer functions from committed blobs, run read-only on the real install dir
draft = ns_for(DRAFT, ["sha256_file", "install_tree", "install_links"])
frozen = ns_for(FROZEN, ["sha256_file", "install_tree"])
server = os.path.realpath(os.path.join(INSTALL, "llama-server"))
tree_f, tsha_f = frozen["install_tree"](server)
tree, tsha = draft["install_tree"](server)
links, lsha = draft["install_links"](server)
check("install_tree_sha256 frozen == draft on real install", tsha_f == tsha, tsha)
check("install_tree_sha256 equals receipt pin", tsha == PIN, tsha)
check("install_tree members == 51", len(tree) == 51, len(tree))
check("install_links entries == 10", len(links) == 10, len(links))
check("install_links_sha256 is 64-hex", isinstance(lsha, str) and len(lsha) == 64, lsha)

names = os.listdir(INSTALL)
kinds = [stat.S_IFMT(os.lstat(os.path.join(INSTALL, n)).st_mode) for n in names]
n_reg = sum(1 for k in kinds if stat.S_ISREG(k))
n_lnk = sum(1 for k in kinds if stat.S_ISLNK(k))
check("install dir = 51 regular + 10 symlink + 0 other",
      (n_reg, n_lnk, len(names) - n_reg - n_lnk) == (51, 10, 0),
      (n_reg, n_lnk, len(names)))
check("no link name is an install_tree member", not (set(links) & set(tree)))

# 3. the gate's own link_chain_problem() from the draft blob, applied to real links
gate = {}
exec(func_body(git_show(DRAFT, CHECK), "link_chain_problem"), gate)
lcp = gate["link_chain_problem"]
reasons = {n: lcp(n, links, tree) for n in sorted(links)}
check("every real link chain ends at a pinned regular member (gate rule)",
      all(r is None for r in reasons.values()),
      {n: r for n, r in reasons.items() if r})

# 4. counterfactual: if symlinks had been members (resolved sha), the pin would move
hyp = dict(tree)
for n in links:
    with open(os.path.realpath(os.path.join(INSTALL, n)), "rb") as fh:
        hyp[n] = hashlib.sha256(fh.read()).hexdigest()
hyp_digest = hashlib.sha256(''.join(f'{k} {hyp[k]}\n' for k in sorted(hyp)).encode()).hexdigest()
check("counterfactual symlink-as-member digest differs from pin", hyp_digest != PIN, hyp_digest)
check("counterfactual: gate 'also a regular install_tree member' rule would flag all links",
      sum(1 for n in links if n in hyp) == 10, sum(1 for n in links if n in hyp))

# 5. upstream release tarball: does it ship the same links and depth-1 regular set?
with tarfile.open(TARBALL, "r:gz") as tf:
    members = tf.getmembers()
up_links = {os.path.basename(m.name): m.linkname for m in members
            if m.issym() and m.name.count("/") == 1}
up_regs = {os.path.basename(m.name) for m in members
           if m.isreg() and m.name.count("/") == 1}
check("upstream tarball ships the same 10 symlinks with identical link text",
      up_links == links, len(up_links))
check("upstream tarball depth-1 regular names == install_tree members",
      up_regs == set(tree), len(up_regs))

# 6. sandbox retargets: install_tree pins regular bytes only; install_links records topology
tmp = tempfile.mkdtemp(prefix="kama-r21-RevengeInstallTreeIntent-", dir="/tmp")
try:
    inst = os.path.join(tmp, "inst")
    ext = os.path.join(tmp, "ext")
    os.mkdir(inst)
    os.mkdir(ext)
    write_file(os.path.join(inst, "llama-server"), b"server")
    write_file(os.path.join(inst, "libllama.so.0.7.0"), b"A" * 64)
    write_file(os.path.join(inst, "libllama-common.so.0.7.0"), b"B" * 64)
    write_file(os.path.join(ext, "libllama.so.0.7.0"), b"X" * 64)
    link = os.path.join(inst, "libllama.so.0")
    os.symlink("libllama.so.0.7.0", link)
    srv = os.path.realpath(os.path.join(inst, "llama-server"))
    t0, s0 = draft["install_tree"](srv)
    l0, ls0 = draft["install_links"](srv)
    os.unlink(link)
    os.symlink("libllama-common.so.0.7.0", link)
    t1, s1 = draft["install_tree"](srv)
    l1, ls1 = draft["install_links"](srv)
    check("same-dir soname retarget: install_tree_sha256 unchanged", s0 == s1, s1)
    check("same-dir soname retarget: install_links_sha256 changes", ls0 != ls1, ls1)
    os.unlink(link)
    os.symlink(os.path.join(ext, "libllama.so.0.7.0"), link)
    t2, s2 = draft["install_tree"](srv)
    l2, ls2 = draft["install_links"](srv)
    check("absolute retarget outside dir: install_tree_sha256 unchanged", s1 == s2, s2)
    check("absolute retarget outside dir: install_links_sha256 changes", ls1 != ls2, ls2)
    check("absolute retarget outside dir: gate rule rejects it",
          lcp("libllama.so.0", l2, t2) is not None, lcp("libllama.so.0", l2, t2))
    check("install_tree membership identical across all retargets", t0 == t1 == t2, len(t0))
finally:
    shutil.rmtree(tmp)

# 7. informational: explicit symlink tests in the draft consumers (line numbers at DRAFT)
pat = re.compile(r"islink|S_ISLNK|is_symlink|follow_symlinks")
scan = {}
for p in [TOOL, CHECK, "tests/llamacpp-live/install-tree-grid.py",
          "tests/llamacpp-live/install-links-grid.py", "tests/llamacpp-live/controls.py"]:
    txt = git_show(DRAFT, p)
    scan[p] = [i + 1 for i, line in enumerate(txt.splitlines()) if pat.search(line)]
print("explicit symlink-test lines at draft (info):", json.dumps(scan))

ok = all(r["ok"] for r in RESULTS)
with open(os.path.join(HERE, "summary.json"), "w", encoding="utf-8") as fh:
    json.dump({"intro": INTRO, "frozen": FROZEN, "draft": DRAFT, "pin": PIN,
               "install_tree_sha256_real": tsha, "install_links_sha256_real": lsha,
               "checks": RESULTS, "explicit_symlink_test_lines_draft": scan}, fh, indent=2)
print("ALL_OK" if ok else "NOT_ALL_OK")
raise SystemExit(0 if ok else 1)
