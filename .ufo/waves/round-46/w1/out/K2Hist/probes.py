"""K2Hist behavioural probes of tools/append-only-audit.py's deleted-line rule.

Three deterministic fixtures (own repo each, under $1): a plain mass deletion,
a mass deletion whose removed lines start with '--', and a 21-line deletion with
two '--' lines (true count >= the frozen threshold of 20).  Prints git's own
deletion count (--numstat) next to the tool's `deleted` and exit code.
"""
import json, os, subprocess, sys, tempfile
TOOL = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py"
root = sys.argv[1]

def build(prefix, lines, keep):
    D = tempfile.mkdtemp(dir=root, prefix=prefix + ".")
    def g(*a):
        p = subprocess.run(["git", "-C", D, *a], capture_output=True, text=True)
        if p.returncode:
            raise SystemExit("git fail: " + p.stderr)
        return p.stdout
    g("init", "-q")
    top = g("rev-parse", "--show-toplevel").strip()
    assert os.path.realpath(top) == os.path.realpath(D), top
    open(os.path.join(D, "LOG.md"), "w").write("\n".join(lines) + "\n")
    g("add", "-A")
    g("-c", "user.name=k2", "-c", "user.email=k2@local", "commit", "-qm", "base")
    open(os.path.join(D, "LOG.md"), "w").write("\n".join(keep) + "\n")
    g("add", "-A")
    g("-c", "user.name=k2", "-c", "user.email=k2@local", "commit", "-qm", "mass-delete")
    ns = g("diff", "--numstat", "HEAD^1", "HEAD", "--", "LOG.md").split("\t")
    p = subprocess.run(["python3", TOOL, "--repo", D, "--to", "HEAD", "--json"],
                       capture_output=True, text=True)
    j = json.loads(p.stdout)
    return top, int(ns[1]), p.returncode, [(e["deleted"], e["status"]) for e in j["events"]]

body = [f"plain {i:02d}" for i in range(40)]

# A: 25 removed, two of them start with '--' (the shape 0718b6ab has on the lane)
a = body + ["--out .ufo/waves/round-20/runs/0957ce61` ran 21 commands"]
top, ns, rc, ev = build("fxA", a, body[:14])
print(f"A toplevel={top} numstat_deleted={ns} tool_exit={rc} tool_events={ev}")

# B: prefix boundary -- which removed texts survive the rule
b = body + ["--x", "-- y", "--- z", "++ w"]
top, ns, rc, ev = build("fxB", b, body[:5])
print(f"B toplevel={top} numstat_deleted={ns} tool_exit={rc} tool_events={ev}")

# C: 21 removed (>= 20) with two '--' lines -> does the detector see the event at all
c = body + ["-- wide-table header", "--verbatim quote row"]
top, ns, rc, ev = build("fxC", c, body[:21])
print(f"C toplevel={top} numstat_deleted={ns} tool_exit={rc} tool_events={ev}")
