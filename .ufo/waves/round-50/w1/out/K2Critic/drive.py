#!/usr/bin/env python3
"""K2Critic r50: adversarial DAGs vs append-only-audit.py v5 origin semantics.

Builds fixture repos under scratch with commit-tree plumbing (controlled parents
and dates), runs the tool extracted at the measured tip, and prints per-event
verdicts vs hand expectations.
"""
import json
import os
import re
import shutil
import subprocess
import sys

S = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(S, "tool-at-tip.py")
IDENT = ["-c", "user.name=k2critic", "-c", "user.email=k2critic@invalid", "-c", "commit.gpgsign=false"]
HEADER = "path\trule\tdeclared_at\tregion\tnote"
EX_ROW = HEADER + "\nSCORE.md\tA-corr\tNOTES.md:1\texempt=## Axes@NOTES.md:2\tfixture\n"
NOTES = ["SCORE.md is append-only", "the ## Axes head of SCORE.md is re-derived in place"]
BASE_DATE = 1_700_000_000


def git(repo, *args, inp=None, env=None, ok=(0,)):
    e = dict(os.environ)
    if env:
        e.update(env)
    p = subprocess.run(["git", "-C", repo, *args], input=inp, capture_output=True, env=e)
    if p.returncode not in ok:
        raise RuntimeError(f"git {' '.join(args)}: rc={p.returncode} {p.stderr[-300:]!r}")
    return p.stdout


def denv(t):
    s = f"{t} +0000"
    return {"GIT_AUTHOR_DATE": s, "GIT_COMMITTER_DATE": s}


class Fx:
    """Commit-tree fixture: files dict accumulates; parents & dates explicit."""

    def __init__(self, root, name):
        self.d = os.path.join(root, name)
        os.makedirs(self.d)
        git(self.d, "init", "-q")
        top = git(self.d, "rev-parse", "--show-toplevel").decode().strip()
        if os.path.realpath(top) != os.path.realpath(self.d):
            raise RuntimeError(f"{name}: toplevel {top} != {self.d}")
        self.files = {}
        self.n = 0
        self.c = {}

    def commit(self, key_, files, parents=None, date=None, delete=()):
        self.files.update(files)
        for dn in delete:
            self.files.pop(dn, None)
        for name in os.listdir(self.d):
            if name != ".git":
                p = os.path.join(self.d, name)
                shutil.rmtree(p) if os.path.isdir(p) else os.unlink(p)
        for name, body in self.files.items():
            p = os.path.join(self.d, name)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "wb") as fh:
                fh.write(body if isinstance(body, bytes) else "".join(x + "\n" for x in body).encode())
        git(self.d, "add", "-A")
        tree = git(self.d, "write-tree").decode().strip()
        self.n += 1
        argv = ["commit-tree", tree, "-m", f"{self.d.split('/')[-1]}:{key_}"]
        if parents is None:
            head = git(self.d, "rev-parse", "-q", "--verify", "HEAD^{commit}", ok=(0, 1)).decode().strip()
            parents = [head] if head else []
        for q in parents:
            argv += ["-p", q]
        c = git(self.d, *IDENT, *argv, env=denv(date if date is not None else BASE_DATE + self.n)).decode().strip()
        git(self.d, "update-ref", "HEAD", c)
        self.c[key_] = c
        return c

    def revlist(self, to="HEAD"):
        out = git(self.d, "rev-list", "--topo-order", "--reverse", "--parents", to).decode()
        return [ln.split() for ln in out.split("\n") if ln.strip()]


def L(tag, n):
    return [f"{tag} line {i}" for i in range(n)]


def run_tool(repo, name, contract=EX_ROW):
    cpath = os.path.join(S, f"{name}.contract.tsv")
    with open(cpath, "w") as fh:
        fh.write(contract)
    p = subprocess.run([sys.executable, TOOL, "--repo", repo, "--to", "HEAD",
                        "--contract", cpath, "--json"], capture_output=True, text=True, timeout=300)
    try:
        j = json.loads(p.stdout)
    except ValueError:
        j = None
    with open(os.path.join(S, "results", f"{name}.json"), "w") as fh:
        fh.write(p.stdout)
        fh.write(f"\n\n--- stderr rc={p.returncode} ---\n{p.stderr}")
    return p.returncode, j


def evs(j):
    return [{k: e[k] for k in ("commit", "file", "deleted", "graded", "ungraded", "status")} for e in (j or {}).get("events", [])]


def report(name, f, code, j, expect, note=""):
    order = [(w[0][:8], [q[:8] for q in w[1:]]) for w in f.revlist()]
    ids = {k: v[:8] for k, v in f.c.items()}
    print(f"\n=== {name} ===")
    print(f"  commits: {ids}")
    print(f"  rev-list --topo-order --reverse --parents: {order}")
    print(f"  tool exit={code} events={json.dumps(evs(j))}")
    print(f"  summary={json.dumps((j or {}).get('summary'))}")
    print(f"  EXPECT: {expect}")
    if note:
        print(f"  NOTE: {note}")
    return code, j


def base_score(hn=24):
    return ["# s", "## Axes"] + L("h", hn) + ["## Round 1"] + L("r", 3)


# ---------------------------------------------------------------- fixtures
def f1_merge_launder(root):
    """Key born under ## Round 1 on a branch, merged under ## Axes (merge blob
    differs from both parents), then deleted under ## Axes.
    v5 spec: parent2 holds the key -> NOT a birth at the merge -> origin {R1}
    -> deleted under Axes = GRADED (laundering must fail).
    Tool (suspected): first-parent-only pkeys -> order (dummy, dated) registers
    a spurious birth under ## Axes -> ungraded."""
    out = {}
    for name, swap in (("f1a-p12", False), ("f1b-p21", True)):
        f = Fx(root, name)
        c1 = f.commit("c1", {"NOTES.md": NOTES, "SCORE.md": base_score(5)})
        # dated branch: 25 d-lines born under ## Round 1
        cb = f.commit("cB", {"SCORE.md": ["# s", "## Axes"] + L("h", 5) +
                             ["## Round 1"] + L("r", 3) + L("d", 25)}, [c1])
        # dummy sibling branch: keeps the BASE SCORE blob (d-lines absent from it)
        ca = f.commit("cA", {"SCORE.md": base_score(5), "DUMMY.txt": ["dummy work on branch A"]}, [c1])
        mtree = ["# s", "## Axes"] + L("h", 5) + L("d", 25) + ["## Round 1"] + L("r", 3)
        cm = f.commit("cM", {"SCORE.md": mtree}, [cb, ca] if swap else [ca, cb])
        ce = f.commit("cE", {"SCORE.md": ["# s", "## Axes"] + L("nh", 30) +
                             ["## Round 1"] + L("r", 3)}, [cm])
        out[name] = (f, ce)
    return out


def f2_multibirth(root):
    """twinA born under Axes then reborn under R1; twinB born under R1 then
    reborn under Axes. Union origin => both ungraded when deleted under Axes.
    first-birth-only => twinB graded; latest-birth-only => twinA graded."""
    f = Fx(root, "f2-multibirth")
    c1 = f.commit("c1", {"NOTES.md": NOTES, "SCORE.md": base_score(23)})
    f.commit("c2", {"SCORE.md": ["# s", "## Axes"] + L("h", 23) + ["twinA",
                    "## Round 1"] + L("r", 3) + ["twinB"]}, [c1])
    f.commit("c3", {"SCORE.md": base_score(23)})          # both twins deleted (2 < 20)
    f.commit("c4", {"SCORE.md": ["# s", "## Axes"] + L("h", 23) + ["twinB",
                    "## Round 1"] + L("r", 3) + ["twinA"]}, )  # reborn, swapped titles
    f.commit("c5", {"SCORE.md": ["# s", "## Axes"] + L("h", 23) + ["twinB", "twinA",
                    "## Round 1"] + L("r", 3)})           # twinA moved under Axes
    ce = f.commit("cE", {"SCORE.md": ["# s", "## Axes"] + L("nh", 30) +
                         ["## Round 1"] + L("r", 3)})
    return {"f2-multibirth": (f, ce)}


def f3_same_blob_parents(root):
    """Merge whose both parents hold the SAME SCORE blob (twin under R1); merge
    re-titles twin under Axes. Spec: no birth at merge; origin {R1} -> graded."""
    f = Fx(root, "f3-sameblob")
    c0 = f.commit("c0", {"NOTES.md": NOTES, "SCORE.md": base_score(24) + ["twin"]})
    ca = f.commit("cA", {"DA.txt": ["a"]}, [c0])
    cb = f.commit("cB", {"DB.txt": ["b"]}, [c0])
    # twin sits at end of R1 in parents; merge moves it under Axes
    cm = f.commit("cM", {"SCORE.md": ["# s", "## Axes"] + L("h", 24) + ["twin",
                         "## Round 1"] + L("r", 3)}, [ca, cb])
    ce = f.commit("cE", {"SCORE.md": ["# s", "## Axes"] + L("nh", 30) +
                         ["## Round 1"] + L("r", 3)}, [cm])
    return {"f3-sameblob": (f, ce)}


def f4_octopus(root):
    """Three-parent merge; twin held ONLY by the third parent, merged under
    ## Axes. Spec: not a birth at M -> origin {R1} -> graded.
    Tool first-parent-only -> spurious Axes birth -> ungraded."""
    f = Fx(root, "f4-octopus")
    c0 = f.commit("c0", {"NOTES.md": NOTES, "SCORE.md": base_score(24)})
    p1 = f.commit("p1", {"D1.txt": ["1"]}, [c0])
    p2 = f.commit("p2", {"D2.txt": ["2"]}, [c0])
    p3 = f.commit("p3", {"SCORE.md": base_score(24) + ["twin"]}, [c0])
    cm = f.commit("cM", {"SCORE.md": ["# s", "## Axes"] + L("h", 24) + ["twin",
                         "## Round 1"] + L("r", 3)}, [p1, p2, p3])
    ce = f.commit("cE", {"SCORE.md": ["# s", "## Axes"] + L("nh", 30) +
                         ["## Round 1"] + L("r", 3)}, [cm])
    return {"f4-octopus": (f, ce)}


def f5_crlf_birth(root):
    """x born under R1 as LF, moved under Axes as CRLF (same key, no birth),
    then deleted there as x\\r. Spec: key(x\\r)=x origin {R1} -> graded."""
    f = Fx(root, "f5-crlf")
    body0 = ("# s\n## Axes\n" + "".join(x + "\n" for x in L("h", 24)) +
             "## Round 1\n" + "".join(x + "\n" for x in L("r", 3)) + "x\n").encode()
    c0 = f.commit("c0", {"NOTES.md": NOTES, "SCORE.md": body0})
    body1 = ("# s\n## Axes\n" + "".join(x + "\n" for x in L("h", 24)) + "x\r\n" +
             "## Round 1\n" + "".join(x + "\n" for x in L("r", 3))).encode()
    c1 = f.commit("c1", {"SCORE.md": body1}, [c0])
    body2 = ("# s\n## Axes\n" + "".join(x + "\n" for x in L("nh", 30)) +
             "## Round 1\n" + "".join(x + "\n" for x in L("r", 3))).encode()
    ce = f.commit("cE", {"SCORE.md": body2}, [c1])
    return {"f5-crlf": (f, ce)}
def f8_absent_first_parent(root):
    """File absent in first parent, present in second (twin under R1); merge
    holds the file with twin under Axes. Spec: p2 holds twin -> not a birth;
    origin {R1} -> graded. Tool: pkeys=set() -> all keys birth under Axes."""
    f = Fx(root, "f8-absentp1")
    c0 = f.commit("c0", {"NOTES.md": NOTES, "SCORE.md": base_score(24)})
    pa = f.commit("pA", {"DA.txt": ["a"]}, [c0], delete=("SCORE.md",))  # file deleted on this branch
    pb = f.commit("pB", {"SCORE.md": base_score(24) + ["twin"]}, [c0])
    cm = f.commit("cM", {"SCORE.md": ["# s", "## Axes"] + L("h", 24) + ["twin",
                         "## Round 1"] + L("r", 3)}, [pa, pb])
    ce = f.commit("cE", {"SCORE.md": ["# s", "## Axes"] + L("nh", 30) +
                         ["## Round 1"] + L("r", 3)}, [cm])
    return {"f8-absentp1": (f, ce)}




def f6_order_probe(root, equal_dates=True):
    """Counter-style order-a/order-b: twin born under Axes on one branch, under
    R1 on the other; merge holds both; event deletes 24h+twin under Axes.
    Same dates on siblings + swapped parents: check rev-list flips and the
    verdict is identical (ungraded) in both -> v5 order-independence holds."""
    out = {}
    d1 = d2 = BASE_DATE + 100
    for name, swap in (("f6a-pAB", False), ("f6b-pBA", True)):
        f = Fx(root, name)
        c1 = f.commit("c1", {"NOTES.md": NOTES, "SCORE.md": base_score(24)}, date=BASE_DATE)
        ca = f.commit("cA", {"SCORE.md": ["# s", "## Axes"] + L("h", 24) + ["twin",
                             "## Round 1"] + L("r", 3)}, [c1], date=d1 if equal_dates else BASE_DATE + 1)
        cb = f.commit("cB", {"SCORE.md": ["# s", "## Axes"] + L("h", 24) +
                             ["## Round 1"] + L("r", 3) + ["twin"]}, [c1], date=d2 if equal_dates else BASE_DATE + 2)
        both = ["# s", "## Axes"] + L("h", 24) + ["twin", "## Round 1"] + L("r", 3) + ["twin"]
        cm = f.commit("cM", {"SCORE.md": both}, [cb, ca] if swap else [ca, cb], date=BASE_DATE + 3)
        ce = f.commit("cE", {"SCORE.md": ["# s", "## Axes"] + L("nh", 30) +
                             ["## Round 1"] + L("r", 3) + ["twin"]}, [cm], date=BASE_DATE + 4)
        out[name] = (f, ce)
    return out


def f7_window_order(root):
    """Event guts ## Axes (24h deleted); sibling cS regrows Axes to 30; merge tip
    keeps cE's gutted tree. Eligibility of ## Axes for the cE event hinges on
    whether cS lands in window(cE) = commits[i:] of rev-list --reverse.
    a/b: all dates equal, parent order swapped -> rev-list tie-break flip?
    c/d: parent order fixed (cE first), cS newer vs older than cE."""
    out = {}
    specs = (("f7a-eq-ES", (1, 0), BASE_DATE + 1, BASE_DATE + 1),   # parents (cE,cS), same dates
             ("f7b-eq-SE", (1, 0), BASE_DATE + 1, BASE_DATE + 1),   # parents (cS,cE), same dates
             ("f7c-Snew",  (0, 0), BASE_DATE + 1, BASE_DATE + 2),   # (cE,cS), cS newer
             ("f7d-Sold",  (0, 0), BASE_DATE + 2, BASE_DATE + 1))   # (cE,cS), cS older
    for name, swap, de, ds in specs:
        f = Fx(root, name)
        c0 = f.commit("c0", {"NOTES.md": NOTES, "SCORE.md": base_score(24)}, date=BASE_DATE)
        ce = f.commit("cE", {"SCORE.md": ["# s", "## Axes", "## Round 1"] + L("r", 3)}, [c0], date=de)
        cs = f.commit("cS", {"SCORE.md": ["# s", "## Axes"] + L("s", 30) +
                             ["## Round 1"] + L("r", 3)}, [c0], date=ds)
        pars = [cs, ce] if name.startswith("f7b") else [ce, cs]
        # merge resolves to cE's (gutted) tree
        ct = f.commit("cT", {"SCORE.md": ["# s", "## Axes", "## Round 1"] + L("r", 3)},
                      pars, date=BASE_DATE + 3)
        out[name] = (f, ct)
    return out


def main():
    os.makedirs(os.path.join(S, "results"), exist_ok=True)
    F = os.path.join(S, "fx")
    shutil.rmtree(F, ignore_errors=True)
    os.makedirs(F)

    ex = {}
    ex.update(f1_merge_launder(F))
    ex.update(f2_multibirth(F))
    ex.update(f3_same_blob_parents(F))
    ex.update(f4_octopus(F))
    ex.update(f5_crlf_birth(F))
    ex.update(f6_order_probe(F))
    ex.update(f7_window_order(F))
    ex.update(f8_absent_first_parent(F))

    expects = {
        "f1a-p12": ("SPEC: origin {R1} -> cE deleted=30 graded=25 ungraded=5 unrestored exit1. "
                    "TOOL-BUG prediction: d birthed at cM under Axes -> cE ungraded=30 exit0", ),
        "f1b-p21": ("SPEC: cE graded=25 ungraded=5 exit1; plus cM event (25d moved, restored same-commit)", ),
        "f2-multibirth": ("union -> deleted=25 graded=0 ungraded=25 status=ungraded exit0; any single-birth rule -> ungraded=24", ),
        "f3-sameblob": ("no birth at merge -> twin origin {R1} -> deleted=25 graded=1 ungraded=24 exit1", ),
        "f4-octopus": ("SPEC: graded=1 ungraded=24 exit1; TOOL SUSPECT: ungraded=25 exit0", ),
        "f5-crlf": ("key(x\\r)=x born under R1 -> graded: deleted=25 graded=1 ungraded=24 exit1", ),
        "f6a-pAB": ("union {Axes,R1} -> ungraded=25 exit0", ),
        "f6b-pBA": ("identical to f6a -> ungraded=25 exit0", ),
        "f7a-eq-ES": ("cE event: cS in window iff tie-break puts cS before cE in reverse list", ),
        "f7b-eq-SE": ("mirror of f7a + extra event at cT (30s deleted vs cS, graded)", ),
        "f7c-Snew": ("cS newer -> emitted before cE forward -> in window -> Axes eligible -> ungraded", ),
        "f7d-Sold": ("cS older -> after cE forward -> NOT in window -> graded unrestored", ),
        "f8-absentp1": ("SPEC: twin origin {R1} (p2 holds it) -> graded=1 ungraded=24 exit1; "
                        "TOOL-BUG prediction: pkeys empty -> all keys born under Axes -> ungraded=25 exit0", ),
    }
    for name, (f, _tip) in ex.items():
        code, j = run_tool(f.d, name)
        report(name, f, code, j, expects[name][0])


if __name__ == "__main__":
    main()
