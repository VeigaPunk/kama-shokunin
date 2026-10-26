import importlib.util, os, subprocess, sys, tempfile
spec = importlib.util.spec_from_file_location("aoa", "/fast/scratch/hyaku/kama-r48/V1Tool/tool-tip.py")
aoa = importlib.util.module_from_spec(spec); spec.loader.exec_module(aoa)
S = "/fast/scratch/hyaku/kama-r48/V1Tool"
TOOL = S + "/tool-tip.py"
LANE = S + "/lane"
TIP = "380bcdff9c8af06997c482f6eb03db926a794a2b"
CONTRACT = "registry/append-only-contract.tsv"
HEADER = aoa.HEADER

class Fx:
    IDENT = ["-c", "user.name=fx", "-c", "user.email=fx@invalid", "-c", "commit.gpgsign=false"]
    def __init__(self, name):
        self.d = tempfile.mkdtemp(prefix=name + "-", dir=S)
        aoa._git(self.d, "init", "-q")
        top = aoa._text(self.d, "rev-parse", "--show-toplevel").strip()
        assert os.path.realpath(top) == os.path.realpath(self.d), top
        self.n = 0
    def commit(self, files=None, delete=(), raw=False):
        for name, body in (files or {}).items():
            p = os.path.join(self.d, name)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "wb") as fh:
                fh.write(body if raw else "".join(x + "\n" for x in body).encode())
        for name in delete:
            aoa._git(self.d, "rm", "-q", name)
        aoa._git(self.d, "add", "-A")
        self.n += 1
        aoa._git(self.d, *self.IDENT, "commit", "-q", "--allow-empty", "-m", f"c{self.n}")
        return aoa._text(self.d, "rev-parse", "HEAD").strip()

def L(tag, n): return [f"{tag} line {i}" for i in range(n)]
def run(args):
    return subprocess.run([sys.executable, TOOL] + args, capture_output=True, text=True)

def show(label):
    print(label)

body25 = "".join(f"p{i} {i}\n" for i in range(25)).encode()

show("=== A1 parent ends w/o newline: last line replaced (1 del, pos 26) ===")
f = Fx("a1"); f.commit({"LOG.md": body25 + b"tail no nl"}, raw=True)
c = f.commit({"LOG.md": body25 + b"tail replaced"}, raw=True)
p = aoa._text(f.d, "rev-parse", f"{c}^").strip()
print("deleted_lines:", aoa.deleted_lines(f.d, p, c, "LOG.md"))

show("=== A2 parent ends w/o newline: last line deleted, marker after - line ===")
f = Fx("a2"); f.commit({"LOG.md": body25 + b"tail no nl"}, raw=True)
c = f.commit({"LOG.md": body25}, raw=True)
p = aoa._text(f.d, "rev-parse", f"{c}^").strip()
print("diff:"); print(aoa._text(f.d, "diff", "--no-renames", "--no-color", "-U0", "--text", p, c, "--", "LOG.md"))
print("deleted_lines:", aoa.deleted_lines(f.d, p, c, "LOG.md"))

show("=== A3 parent ends w/o newline: last TWO lines deleted ===")
f = Fx("a3"); f.commit({"LOG.md": body25 + b"t1\n" + b"t2 no nl"}, raw=True)
c = f.commit({"LOG.md": body25}, raw=True)
p = aoa._text(f.d, "rev-parse", f"{c}^").strip()
print("deleted_lines:", aoa.deleted_lines(f.d, p, c, "LOG.md"))

show("=== B1 -0,0 hunk (empty parent file, content added): no deletions, no crash ===")
f = Fx("b1"); f.commit({"LOG.md": b""}, raw=True)
c = f.commit({"LOG.md": L("x", 25)})
p = aoa._text(f.d, "rev-parse", f"{c}^").strip()
print("deleted_lines:", aoa.deleted_lines(f.d, p, c, "LOG.md"))
res = aoa.audit(f.d, c, files=["LOG.md"])
print("events:", res["events"], "exit", aoa.exit_code(res))

show("=== B2 +0,0 hunk (first 10 of 30 deleted): positions 1..10 ===")
f = Fx("b2"); f.commit({"LOG.md": L("k", 30)})
c = f.commit({"LOG.md": L("k", 30)[10:]})
p = aoa._text(f.d, "rev-parse", f"{c}^").strip()
print("deleted_lines:", aoa.deleted_lines(f.d, p, c, "LOG.md"))

show("=== B3 all 25 lines deleted (@@ -1,25 +0,0 @@): event, unrestored, exit 1 ===")
f = Fx("b3"); f.commit({"LOG.md": L("k", 25)})
c = f.commit({"LOG.md": []})
p = aoa._text(f.d, "rev-parse", f"{c}^").strip()
d = aoa.deleted_lines(f.d, p, c, "LOG.md")
print("deleted:", len(d), "first/last:", d[0], d[-1])
res = aoa.audit(f.d, c, files=["LOG.md"])
print("events:", [(e["deleted"], e["graded"], e["status"]) for e in res["events"]], "exit", aoa.exit_code(res))

show("=== I two hunks in one diff: positions from each header ===")
f = Fx("mh"); f.commit({"LOG.md": L("k", 30)})
c = f.commit({"LOG.md": L("k", 30)[2:18] + L("k", 30)[20:]})
p = aoa._text(f.d, "rev-parse", f"{c}^").strip()
print("headers:", [ln for ln in aoa._text(f.d, "diff", "--no-renames", "--no-color", "-U0", "--text", p, c, "--", "LOG.md").split("\n") if ln.startswith("@@")])
print("positions:", [x[0] for x in aoa.deleted_lines(f.d, p, c, "LOG.md")])

show("=== H full rewrite of 25 lines, last line w/o newline (marker mid-hunk) ===")
f = Fx("hb")
f.commit({"LOG.md": "".join(f"p{i} {i}\n" for i in range(24)).encode() + b"p24 no nl"}, raw=True)
c = f.commit({"LOG.md": "".join(f"q{i} {i}\n" for i in range(24)).encode() + b"q24 no nl"}, raw=True)
p = aoa._text(f.d, "rev-parse", f"{c}^").strip()
d = aoa.deleted_lines(f.d, p, c, "LOG.md")
print("deleted:", len(d), "first:", d[0], "last:", d[-1])

NOTES = ["# notes", "score.md is append-only below its head.",
         "The ## Axes head of score.md is re-derived in place."]
SCORE = "score.md\tA-corr\tNOTES.md:2\texempt=## Axes@NOTES.md:3\tx"
head, tail = ["# score", "## Axes"] + L("h", 24), ["## Round 1"] + L("r", 25)

show("=== C section of a deleted line computed on the PARENT (heading renamed = gutted) ===")
f = Fx("c1")
f.commit({"NOTES.md": NOTES, CONTRACT: [HEADER, SCORE], "score.md": head + tail})
c = f.commit({"score.md": ["# score", "## Renamed"] + L("h2", 24) + tail})
res = aoa.audit(f.d, c)
print("events:", [(x["deleted"], x["graded"], x["ungraded"], x["status"]) for x in res["events"]],
      "exit", aoa.exit_code(res), "(title gone at <to> -> not eligible -> graded: per definition)")

show("=== C2 deleted pre-heading lines (section None) under only= : ungraded ===")
f = Fx("c2")
KN = "know.md\tA-corr\tNOTES.md:2\tonly=## Errata@NOTES.md:2\tx"
f.commit({"NOTES.md": ["# notes", "know.md: its ## Errata region is append-only."],
          CONTRACT: [HEADER, KN], "know.md": L("pre", 25) + ["## Errata"] + L("e", 20)})
c = f.commit({"know.md": ["## Errata"] + L("e", 20)})
res = aoa.audit(f.d, c)
print("events:", [(x["deleted"], x["graded"], x["ungraded"], x["status"]) for x in res["events"]],
      "exit", aoa.exit_code(res))

show("=== D eligibility PER EVENT (c1 rewrite eligible; c2 gut not eligible) ===")
f = Fx("d1")
f.commit({"NOTES.md": NOTES, CONTRACT: [HEADER, SCORE], "score.md": head + tail})
c1 = f.commit({"score.md": ["# score", "## Axes"] + L("h2", 24) + tail})
c2 = f.commit({"score.md": ["# score", "## Axes", "collapsed"] + tail})
res = aoa.audit(f.d, c2)
ev = {(e["commit"], e["file"]): e for e in res["events"]}
print("c1:", (ev[(c1, "score.md")]["deleted"], ev[(c1, "score.md")]["graded"], ev[(c1, "score.md")]["status"]))
print("c2:", (ev[(c2, "score.md")]["deleted"], ev[(c2, "score.md")]["graded"], ev[(c2, "score.md")]["status"]))
print("exit", aoa.exit_code(res))

show("=== E1 union: row '*' + row exempt -> exempt still applies ===")
f = Fx("e1")
f.commit({"NOTES.md": NOTES, CONTRACT: [HEADER, "score.md\tA\tNOTES.md:2\t*\tx", SCORE],
          "score.md": head + tail})
c = f.commit({"score.md": ["# score", "## Axes"] + L("h2", 24) + tail})
res = aoa.audit(f.d, c)
print("events:", [(x["deleted"], x["graded"], x["ungraded"], x["status"]) for x in res["events"]],
      "exit", aoa.exit_code(res))

show("=== E2 union: exempt + only -> dated section (only region) graded ===")
f = Fx("e2")
f.commit({"NOTES.md": NOTES, CONTRACT: [HEADER, SCORE, "score.md\tA\tNOTES.md:2\tonly=## Round 1@NOTES.md:3\tx"],
          "score.md": head + tail})
c = f.commit({"score.md": head + ["## Round 1"] + L("r2", 25)})
res = aoa.audit(f.d, c)
print("events:", [(x["deleted"], x["graded"], x["ungraded"], x["status"]) for x in res["events"]],
      "exit", aoa.exit_code(res))

show("=== E3 union: only alone -> head-section deletion ungraded ===")
f = Fx("e3")
f.commit({"NOTES.md": NOTES, CONTRACT: [HEADER, "score.md\tA\tNOTES.md:2\tonly=## Round 1@NOTES.md:3\tx"],
          "score.md": head + tail})
c = f.commit({"score.md": ["# score", "## Axes"] + L("h2", 24) + tail})
res = aoa.audit(f.d, c)
print("events:", [(x["deleted"], x["graded"], x["ungraded"], x["status"]) for x in res["events"]],
      "exit", aoa.exit_code(res), "(exit 1 here = unbound only-pointer in this fixture, event itself ungraded)")

show("=== F --files mode: no regions, no declarations ===")
f = Fx("f1")
f.commit({"NOTES.md": NOTES, CONTRACT: [HEADER, SCORE], "score.md": head + tail})
c = f.commit({"score.md": head + ["## Round 1"] + L("r2", 25)})
res = aoa.audit(f.d, c, files=["score.md"])
print("events:", [(x["deleted"], x["graded"], x["ungraded"], x["status"]) for x in res["events"]],
      "declarations:", res["declarations"], "exit", aoa.exit_code(res))
res = aoa.audit(f.d, c, files=["nope.md"])
print("nonexistent path: events", res["events"], "exit", aoa.exit_code(res))
r = run(["--repo", f.d, "--files", "LOG.md", "--contract", "x.tsv"])
print("--files+--contract exit:", r.returncode, "|", r.stderr.strip()[:80])

show("=== G declaration(): missing declared file / out-of-range line / missing pointer ===")
f = Fx("g1")
f.commit({"NOTES.md": NOTES, CONTRACT: [HEADER,
          "gone.md\tA\tNOTES.md:2\t*\tdecl file missing",
          "score.md\tA\tNOTES.md:99\t*\tline out of range",
          "score.md\tA-corr\tNOTES.md:2\texempt=## Axes@missing.md:1\tpointer file missing",
          "score.md\tA-corr\tNOTES.md:2\texempt=## Axes@NOTES.md:99\tpointer line out of range"],
          "score.md": head + tail})
res = aoa.audit(f.d, "HEAD")
for dcl in res["declarations"]:
    print("  ", dcl["path"], dcl["declared_at"], dcl["region"], "ok=", dcl["ok"], "|", dcl["reason"])
print("bad_declarations:", res["summary"]["bad_declarations"], "exit", aoa.exit_code(res))

show("=== X1 --contract with an invalid-UTF-8 byte: promised exit 2, got traceback exit 1 ===")
f = Fx("x1"); f.commit({"LOG.md": L("k", 30)})
bad = os.path.join(f.d, "bad.tsv")
with open(bad, "wb") as fh:
    fh.write((HEADER + "\n").encode() + b"LOG.md\tA\tbad\xff.tsv:1\t*\tx\n")
r = run(["--repo", f.d, "--contract", bad])
print("exit:", r.returncode, "| stderr tail:", r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "")

show("=== X2 non-UTF-8 byte in a contract-matching path: UnicodeEncodeError exit 1 ===")
f = Fx("x2")
f.commit({"AGENTS.md": ["lessons are append-only"],
          CONTRACT: [HEADER, "corpus/lessons/*.md\tA-corr\tAGENTS.md:1\t*\tx"]})
os.makedirs(os.path.join(f.d.encode(), b"corpus/lessons"), exist_ok=True)
w = os.path.join(f.d.encode(), b"corpus/lessons/x\xff.md")
with open(w, "wb") as fh:
    fh.write(b"".join(b"line %d\n" % i for i in range(30)))
f.commit()
with open(w, "wb") as fh:
    fh.write(b"".join(b"line %d\n" % i for i in range(5)))
c = f.commit()
r = run(["--repo", f.d, "--to", c, "--json"])
print("exit:", r.returncode, "| stderr tail:", r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "")

show("=== X3 gitlink bump at --threshold 1: IndexError exit 1 (numstat counts 1 deletion) ===")
f = Fx("x3")
sub = os.path.join(f.d, "sub"); os.makedirs(sub, exist_ok=True)
aoa._git(sub, "init", "-q")
open(os.path.join(sub, "f.txt"), "w").write("x\n")
aoa._git(sub, *Fx.IDENT, "add", "-A"); aoa._git(sub, *Fx.IDENT, "commit", "-q", "-m", "s1")
aoa._git(f.d, "add", "sub"); f.commit()
open(os.path.join(sub, "f.txt"), "w").write("y\n")
aoa._git(sub, *Fx.IDENT, "add", "-A"); aoa._git(sub, *Fx.IDENT, "commit", "-q", "-m", "s2")
aoa._git(f.d, "add", "sub"); c = f.commit()
p = aoa._text(f.d, "rev-parse", f"{c}^").strip()
print("numstat:", aoa.numstat(f.d, p, c, ["sub"]))
r = run(["--repo", f.d, "--to", c, "--threshold", "1", "--files", "sub", "--json"])
print("exit:", r.returncode, "| stderr tail:", r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "")

show("=== J newline inside a contract-matching path: IndexError exit 1 ===")
f = Fx("j1")
f.commit({"AGENTS.md": ["lessons are append-only"],
          CONTRACT: [HEADER, "corpus/lessons/*.md\tA-corr\tAGENTS.md:1\t*\tx"]})
d = os.path.join(f.d, "corpus/lessons"); os.makedirs(d, exist_ok=True)
w = os.path.join(d.encode(), b"a\nb.md")
with open(w, "wb") as fh:
    fh.write(b"".join(b"line %d\n" % i for i in range(30)))
f.commit()
with open(w, "wb") as fh:
    fh.write(b"".join(b"line %d\n" % i for i in range(5)))
c = f.commit()
r = run(["--repo", f.d, "--to", c, "--json"])
print("exit:", r.returncode, "| stderr tail:", r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "")

show("=== X4 determinism: two lane runs byte-identical ===")
outs = []
for i in range(2):
    r = run(["--repo", LANE, "--to", TIP, "--json"])
    outs.append(r.stdout)
print("identical:", outs[0] == outs[1], "exit:", r.returncode)

show("=== PERF lane run (311 commits, 89 files, 5 events) ===")
import time
t0 = time.time()
r = run(["--repo", LANE, "--to", TIP, "--json"])
dt = time.time() - t0
j = eval(r.stdout) if False else None
import json
j = json.loads(r.stdout)
print(f"wall {dt:.2f}s exit {r.returncode} summary {j['summary']}")
