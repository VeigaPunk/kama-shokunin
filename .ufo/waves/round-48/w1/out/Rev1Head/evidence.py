#!/usr/bin/env python3
"""Evidence run: frozen C1 at base/build + counterfactual (banner rewritten in place,
not archived) to show whether v3 can see the practice."""
import json, os, subprocess, sys

S = os.environ.get("S", "/fast/scratch/hyaku/kama-r48/Rev1Head")
LANE = os.path.join(S, "lane")
COUNTER = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round48-append-audit-v3-check.py"
AUDIT = os.path.join(LANE, "tools/append-only-audit.py")
CONTRACT = os.path.join(LANE, "registry/append-only-contract.tsv")
BASE = "33e005827742b29772b153cda036ec9f27f653be"
BUILD = "380bcdff9c8af06997c482f6eb03db926a794a2b"

def run(cmd, **kw):
    p = subprocess.run(cmd, capture_output=True, text=True, **kw)
    return p.returncode, p.stdout, p.stderr

for label, tip in (("base", BASE), ("build", BUILD)):
    rc, out, err = run([sys.executable, COUNTER, "--repo", LANE, "--tip", tip,
                        "--scratch", os.path.join(S, f"c1-{label}")])
    line = [l for l in out.splitlines() if l.startswith("selftest=")]
    print(f"C1@{label} exit={rc} {line[0] if line else out.splitlines()[:1]}")

for label, tip in (("base", BASE), ("build", BUILD)):
    rc, out, err = run([sys.executable, AUDIT, "--repo", LANE, "--to", tip,
                        "--contract", CONTRACT, "--json"])
    d = json.loads(out)
    s = d["summary"]
    print(f"tool@{label} exit={rc} events={s['events']} regressed={s['regressed']} "
          f"ungraded_lines={s['ungraded_lines']}")
    for e in d["events"]:
        if e["file"] == "SCORECARD.md":
            print(f"   {e['commit'][:8]} deleted={e['deleted']} graded={e['graded']} "
                  f"ungraded={e['ungraded']} {e['status']} max={e['restored_max']} to={e['held_at_to']}")

# counterfactual: a round-48-style banner rewrite in place, no archive append
top = run(["git", "-C", LANE, "rev-parse", "--show-toplevel"])[1].strip()
assert top == LANE, (top, LANE)
run(["git", "-C", LANE, "checkout", "-q", "-B", "cf", BUILD])
sc = os.path.join(LANE, "SCORECARD.md")
lines = open(sc, encoding="utf-8").read().split("\n")
assert lines[5].startswith("**Current authority (round 47):**"), lines[5][:40]
lines[5] = lines[5].replace("(round 47)", "(round 48)").replace("Latest measured round: 47",
                                                               "Latest measured round: 48")
open(sc, "w", encoding="utf-8").write("\n".join(lines))
rc, out, err = run(["git", "-C", LANE, "-c", "user.name=Rev1Head",
                    "-c", "user.email=rev1head@scratch.local",
                    "commit", "-q", "-am", "counterfactual: banner rewritten in place, nothing archived"])
print("commit rc", rc, err.strip()[:200])
cf = run(["git", "-C", LANE, "rev-parse", "HEAD"])[1].strip()
print("cf commit", cf[:12])
rc, out, err = run([sys.executable, AUDIT, "--repo", LANE, "--to", cf,
                    "--contract", CONTRACT, "--json"])
d = json.loads(out)
s = d["summary"]
print(f"tool@cf exit={rc} events={s['events']} regressed={s['regressed']} "
      f"partial={s['partial']} unrestored={s['unrestored']} vanished={s['vanished']}")
print("   SCORECARD events:", [(e["commit"][:8], e["deleted"], e["graded"], e["status"])
                                for e in d["events"] if e["file"] == "SCORECARD.md"])
rc, out, err = run([sys.executable, AUDIT, "--repo", LANE, "--to", cf,
                    "--contract", CONTRACT, "--threshold", "1", "--json"])
d = json.loads(out)
print("   with --threshold 1:",
      [(e["commit"][:8], e["deleted"], e["graded"], e["status"], e["held_at_to"], e["restored_max"])
       for e in d["events"] if e["file"] == "SCORECARD.md"])
print("   exit with --threshold 1:", rc)
run(["git", "-C", LANE, "checkout", "-q", BUILD])
run(["git", "-C", LANE, "branch", "-q", "-D", "cf"])
