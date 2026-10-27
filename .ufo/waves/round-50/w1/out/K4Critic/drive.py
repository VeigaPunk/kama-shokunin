#!/usr/bin/env python3
"""K4Critic round-50: CRLF-normalization attack fixtures against append-only-audit.py v5.

Hand expectations are encoded per fixture BEFORE any run (EXPECT dicts below).
Builds byte-exact fixture repos (mixed LF/CRLF) via write-tree/commit-tree, runs
--json, and cross-checks graded+ungraded==deleted and deleted==numstat for every event.
"""
import json, os, re, subprocess, sys

S = "/fast/scratch/hyaku/kama-r50/K4Critic"
TOOL = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py"
IDENT = ["-c", "user.name=k4-fixture", "-c", "user.email=k4@invalid", "-c", "commit.gpgsign=false"]
HEADER = "path\trule\tdeclared_at\tregion\tnote"
EX_ROW = HEADER + "\nSCORE.md\tA-corr\tNOTES.md:1\texempt=## Axes@NOTES.md:2\tfixture\n"
ONLY_ROW = (HEADER + "\nKNOW.md\tA\tNOTES.md:1\tonly=## Errata@NOTES.md:3\tfixture\n")


def git(repo, *args, inp=None):
    p = subprocess.run(["git", "-C", repo, *args], input=inp, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git -C {repo} {' '.join(args)}: {p.stderr.decode()[-300:]}")
    return p.stdout


class Fx:
    def __init__(self, name):
        self.d = os.path.join(S, "fx-" + name)
        os.makedirs(self.d)
        git(self.d, "init", "-q")
        top = os.path.realpath(git(self.d, "rev-parse", "--show-toplevel").decode().strip())
        if top != os.path.realpath(self.d):
            raise RuntimeError(f"toplevel {top} != {self.d}")
        self.files = {}

    def commit(self, files, parents=None):
        """files: {path: bytes}. Earlier files persist (counter Fx semantics)."""
        self.files.update(files)
        for name in os.listdir(self.d):
            if name != ".git":
                p = os.path.join(self.d, name)
                if os.path.isdir(p):
                    import shutil; shutil.rmtree(p)
                else:
                    os.unlink(p)
        for name, body in self.files.items():
            p = os.path.join(self.d, name)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "wb") as fh:
                fh.write(body)
        git(self.d, "add", "-A")
        tree = git(self.d, "write-tree").decode().strip()
        if parents is None:
            p = subprocess.run(["git", "-C", self.d, "rev-parse", "-q", "--verify", "HEAD^{commit}"],
                               capture_output=True)
            head = p.stdout.decode().strip()
            parents = [head] if p.returncode == 0 and head else []
        argv = ["commit-tree", tree, "-m", "fx"]
        for q in parents:
            argv += ["-p", q]
        c = git(self.d, *IDENT, *argv).decode().strip()
        git(self.d, "update-ref", "HEAD", c)
        return c


def B(*items):
    """items: str -> LF line; bytes -> taken verbatim (already holds \\r\\n)."""
    out = b""
    for x in items:
        out += x if isinstance(x, bytes) else (x + "\n").encode()
    return out


def CRLF(x):
    return (x + "\r\n").encode()


def run_tool(repo, contract_text, name, to="HEAD"):
    cpath = os.path.join(S, name + ".contract.tsv")
    with open(cpath, "w") as fh:
        fh.write(contract_text)
    p = subprocess.run([sys.executable, TOOL, "--repo", repo, "--to", to,
                        "--contract", cpath, "--json"], capture_output=True, text=True, timeout=300)
    j = json.loads(p.stdout) if p.stdout.strip().startswith("{") else None
    return p.returncode, j


def numstat(repo, parent, commit, f):
    out = git(repo, "diff", "--numstat", "--no-renames", parent, commit, "--", f).decode()
    return int(out.split("\t")[1]) if out.split("\t")[1].isdigit() else None


def first_parent(repo, c):
    ps = git(repo, "rev-list", "--parents", "-1", c).decode().split()
    return ps[1] if len(ps) > 1 else None


def check(name, code, j, want_exit, want_events, repo):
    """want_events: {commit: {field: val}}."""
    ok = True
    notes = []
    if code != want_exit:
        ok = False
        notes.append(f"exit {code} != {want_exit}")
    events = {e["commit"]: e for e in (j or {}).get("events", [])}
    # accounting cross-check on every event the tool reported
    for c, e in events.items():
        if e["graded"] + e["ungraded"] != e["deleted"]:
            ok = False
            notes.append(f"{c[:8]} graded+ungraded != deleted")
        par = first_parent(repo, c)
        ns = numstat(repo, par, c, e["file"]) if par else None
        if ns is not None and ns != e["deleted"]:
            ok = False
            notes.append(f"{c[:8]} deleted {e['deleted']} != numstat {ns}")
    for c, want in want_events.items():
        e = events.get(c)
        if e is None:
            ok = False
            notes.append(f"event {c[:8]} missing (have {[k[:8] for k in events]})")
            continue
        for k, v in want.items():
            if e.get(k) != v:
                ok = False
                notes.append(f"{c[:8]} {k}={e.get(k)} want {v}")
    return ok, notes


def L(tag, n, crlf=False):
    return [CRLF(f"{tag} line {i} k4") if crlf else f"{tag} line {i} k4" for i in range(n)]


NOTES_EX = B("SCORE.md is append-only",
             "the ## Axes head of SCORE.md is re-derived in place")

results = []

# ---------------------------------------------------------------- F1 carry LF->CRLF
# victim born LF under ## Axes (c1). c2 copies it into ## Round 1 as CRLF
# (key "victim line" already held -> no new birth; origin stays {Axes}).
# c3 deletes the whole Axes block incl. victim LF while Axes regrows.
# EXPECT: victim ungraded (born in exempt section; ending change on the copy
# does not launder). del=25 g=0 u=25 status=ungraded exit 0.
f = Fx("f1-carry")
head24 = L("hd", 24)
f.commit({"NOTES.md": NOTES_EX,
          "SCORE.md": B("# s", "## Axes", *head24, "victim line", "## Round 1", *L("r", 3))})
f.commit({"SCORE.md": B("# s", "## Axes", *head24, "victim line",
                        "## Round 1", *L("r", 3), CRLF("victim line"))})
c3 = f.commit({"SCORE.md": B("# s", "## Axes", *L("nh", 30),
                             "## Round 1", *L("r", 3), CRLF("victim line"))})
code, j = run_tool(f.d, EX_ROW, "f1")
ok, notes = check("f1", code, j, 0, {c3: {"deleted": 25, "graded": 0, "ungraded": 25,
                                         "status": "ungraded"}}, f.d)
results.append(("F1 carry LF->CRLF: victim deleted from Axes ungraded",
                ok, notes, code))

# ---------------------------------------------------------------- F2 born CRLF in R1
# "cvictim line\r" born under ## Round 1 (c1). c2 adds the LF twin under ## Axes
# (no birth - key held). c3 deletes Axes block incl. the LF twin.
# EXPECT: twin graded (origin {Round 1}), head lines ungraded.
# del=25 g=1 u=24; nothing byte-restored -> unrestored exit 1.
f = Fx("f2-born-crlf")
f.commit({"NOTES.md": NOTES_EX,
          "SCORE.md": B("# s", "## Axes", *head24, "## Round 1", *L("r", 3),
                        CRLF("cvictim line"))})
f.commit({"SCORE.md": B("# s", "## Axes", *head24, "cvictim line",
                        "## Round 1", *L("r", 3), CRLF("cvictim line"))})
c3 = f.commit({"SCORE.md": B("# s", "## Axes", *L("nh", 30),
                             "## Round 1", *L("r", 3), CRLF("cvictim line"))})
code, j = run_tool(f.d, EX_ROW, "f2")
ok, notes = check("f2", code, j, 1, {c3: {"deleted": 25, "graded": 1, "ungraded": 24,
                                         "status": "unrestored", "restored_max": 0}}, f.d)
results.append(("F2 born-CRLF in R1: LF twin deleted from Axes graded",
                ok, notes, code))

# ---------------------------------------------------------------- F3 mixed-endings restore
# Two repos (a restore commit itself deletes the other variant's lines, so
# flip and byte-exact get separate histories).
# f3-flip: 12 LF + 12 CRLF dated lines deleted at c2, re-added with FLIPPED
# endings at c3 -> byte-exact held=0 -> unrestored exit 1.
f = Fx("f3-flip")
ml, mc = L("md", 12), L("mc", 12, crlf=True)
f.commit({"NOTES.md": NOTES_EX,
          "SCORE.md": B("# s", "## Axes", *L("h", 5), "## Round 1", *ml, *mc)})
c2 = f.commit({"SCORE.md": B("# s", "## Axes", *L("h", 5), "## Round 1", "kept")})
f.commit({"SCORE.md": B("# s", "## Axes", *L("h", 5), "## Round 1",
                        *L("md", 12, crlf=True), *L("mc", 12))})   # flipped endings
code, j = run_tool(f.d, EX_ROW, "f3a")
ok1, n1 = check("f3-flip", code, j, 1,
                {c2: {"deleted": 24, "graded": 24, "restored_max": 0,
                      "status": "unrestored"}}, f.d)
# f3-exact: same deletion at c2, byte-exact restore at c3 -> restored exit 0.
f = Fx("f3-exact")
f.commit({"NOTES.md": NOTES_EX,
          "SCORE.md": B("# s", "## Axes", *L("h", 5), "## Round 1", *ml, *mc)})
c2 = f.commit({"SCORE.md": B("# s", "## Axes", *L("h", 5), "## Round 1", "kept")})
c3 = f.commit({"SCORE.md": B("# s", "## Axes", *L("h", 5), "## Round 1", *ml, *mc)})
code, j = run_tool(f.d, EX_ROW, "f3b")
ok2, n2 = check("f3-exact", code, j, 0,
                {c2: {"deleted": 24, "graded": 24, "restored_max": 24,
                      "restored_by": c3, "status": "restored"}}, f.d)
results.append(("F3 flipped-endings restore held=0; byte-exact restore held=24",
                ok1 and ok2, n1 + n2, (code)))
# ---------------------------------------------------------------- F7 fully-CRLF file
# Every line CRLF incl. `## ` headings: b = ln.rstrip(b"\\r") still parses the
# section. c2 deletes the Axes block (25 incl. CRLF head lines) -> ungraded;
# c3 deletes the dated block -> graded.
f = Fx("f7-allcrlf")
f.commit({"NOTES.md": NOTES_EX,
          "SCORE.md": B(*[CRLF(x) for x in ["# s", "## Axes"] + head24 + ["## Round 1"]],
                        *L("dd", 25, crlf=True))})
c2 = f.commit({"SCORE.md": B(*[CRLF(x) for x in ["# s", "## Axes"]] + L("nh", 30, crlf=True)
                             + [CRLF("## Round 1")], *L("dd", 25, crlf=True))})
c3 = f.commit({"SCORE.md": B(*[CRLF(x) for x in ["# s", "## Axes"]] + L("nh", 30, crlf=True)
                             + [CRLF("## Round 1"), CRLF("kept")])})
code, j = run_tool(f.d, EX_ROW, "f7")
ok, notes = check("f7", code, j, 1, {
    c2: {"deleted": 24, "graded": 0, "ungraded": 24, "status": "ungraded"},
    c3: {"deleted": 25, "graded": 25, "ungraded": 0, "status": "unrestored"}}, f.d)
results.append(("F7 fully-CRLF file: headings parse, Axes ungraded / Round 1 graded",
                ok, notes, code))


# ---------------------------------------------------------------- F4 key collision
# c1: R1 holds "dup line\r" (key "dup line") and "deep line\r\r" (key "deep line\r").
# c2: Axes gains "dup line" (key held -> NO birth; org stays {Round 1}) and
#     "deep line\r" (key "deep line" absent in c1 -> birth under Axes).
# c3: Axes block deleted (head24 + "dup line" + "deep line\r" = 26).
# EXPECT (set semantics over stripped keys): the LF "dup line" sitting in Axes is
# GRADED (its key was born in Round 1); "deep line\r" is ungraded (its key's
# first birth is under Axes - the CRCRLF twin escaped collision). g=1 u=25.
f = Fx("f4-collision")
f.commit({"NOTES.md": NOTES_EX,
          "SCORE.md": B("# s", "## Axes", *head24, "## Round 1", *L("r", 3),
                        CRLF("dup line"), CRLF("deep line\r"))})
f.commit({"SCORE.md": B("# s", "## Axes", *head24, "dup line", CRLF("deep line"),
                        "## Round 1", *L("r", 3), CRLF("dup line"), CRLF("deep line\r"))})
c3 = f.commit({"SCORE.md": B("# s", "## Axes", *L("nh", 30),
                             "## Round 1", *L("r", 3), CRLF("dup line"), CRLF("deep line\r"))})
code, j = run_tool(f.d, EX_ROW, "f4")
ok, notes = check("f4", code, j, 1, {c3: {"deleted": 26, "graded": 1, "ungraded": 25,
                                         "status": "unrestored"}}, f.d)
results.append(("F4 key collision: Axes-seated LF twin graded (origin {Round 1}); "
                "CRCRLF twin escapes collision", ok, notes, code))

# ---------------------------------------------------------------- F5 only= region
# only=## Errata: lines inside a non-matching section are skipped (ungraded),
# CRLF lines inside Errata grade the same as LF.
# c1: Errata 12 LF + 12 CRLF; Main 10. c2 deletes all 24 Errata + 4 Main = 28.
# EXPECT: g=24 u=4, status unrestored, exit 1.
f = Fx("f5-only")
notes_only = B("KNOW.md is append-only",
               "the ## Axes head of KNOW.md is re-derived in place",
               "only the ## Errata tail of KNOW.md is append-only")
f.commit({"NOTES.md": notes_only,
          "KNOW.md": B("# k", "## Errata", *L("oe", 12), *L("oc", 12, crlf=True),
                       "## Main", *L("m", 10))})
c2 = f.commit({"KNOW.md": B("# k", "## Errata", "## Main", *L("m", 6))})
code, j = run_tool(f.d, ONLY_ROW, "f5")
ok, notes = check("f5", code, j, 1, {c2: {"deleted": 28, "graded": 24, "ungraded": 4,
                                         "status": "unrestored"}}, f.d)
results.append(("F5 only= region: CRLF lines inside ## Errata graded; "
                "outside lines skipped->ungraded", ok, notes, code))

# ---------------------------------------------------------------- F6 merge-birth (suspected defect)
# c1 base. cB adds "ml victim\r" under ## Round 1 (birth {Round 1}). cA unchanged.
# cm merges parents=[cA,cB]; blob places "ml victim" LF under ## Axes too.
# Spec (counter docstring): birth = no *parent* holds the key -> cm is NOT a
# birth (cB holds it) -> origin {Round 1} -> the Axes copy is graded at ce.
# Tool suspected: origins() iterates only the FIRST parent (parents[x]=parts[1])
# -> pkeys=keys(cA) lacks the key -> cm counted as a birth -> origin gains {Axes}
# -> ungraded. ce deletes Axes block (head24 + "ml victim").
f = Fx("f6-merge")
c1 = f.commit({"NOTES.md": NOTES_EX,
               "SCORE.md": B("# s", "## Axes", *head24, "## Round 1", *L("r", 3))})
ca = f.commit({"SCORE.md": B("# s", "## Axes", *head24, "## Round 1", *L("r", 3))}, [c1])
cb = f.commit({"SCORE.md": B("# s", "## Axes", *head24, "## Round 1", *L("r", 3),
                             CRLF("ml victim"))}, [c1])
cm = f.commit({"SCORE.md": B("# s", "## Axes", *head24, "ml victim",
                             "## Round 1", *L("r", 3), CRLF("ml victim"))}, [ca, cb])
ce = f.commit({"SCORE.md": B("# s", "## Axes", *L("nh", 30),
                             "## Round 1", *L("r", 3), CRLF("ml victim"))}, [cm])
code, j = run_tool(f.d, EX_ROW, "f6")
# predicted TOOL behaviour (defect): ungraded, exit 0. SPEC verdict: g=1 u=24 unrestored, exit 1.
tool_ok, tnotes = check("f6-tool", code, j, 0,
                        {ce: {"deleted": 25, "graded": 0, "ungraded": 25,
                              "status": "ungraded"}}, f.d)
spec_ok, snotes = check("f6-spec", code, j, 1,
                        {ce: {"deleted": 25, "graded": 1, "ungraded": 24,
                              "status": "unrestored"}}, f.d)
results.append(("F6 merge-birth: tool=" + ("ungraded(defect)" if tool_ok else "?")
                + " spec=" + ("graded(correct)" if spec_ok else "not-graded")
                + f" exit={code}", spec_ok, tnotes + snotes, code))

print("=" * 100)
for name, ok, notes, code in results:
    print(f"[{'PASS' if ok else 'FAIL'}] {name}   (exit {code})")
    for n in notes:
        print(f"      {n}")
print("=" * 100)
