#!/usr/bin/env python3
"""probe1.py - edge-behavior probes against the FROZEN counter bytes
(lane tools/round44-verdict-ledger-audit.py, sha256 1933e75b...) in a
fixture clone under /fast/scratch (identity r44-control@fixture.invalid).
P1 unicode-digit line field; P2 out-of-population row; P3 bad tip exit code;
P4 read-only claim on --repo."""
import subprocess, os, shutil
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
S = "/fast/scratch/hyaku/kama-r44/V2Code"
D = os.path.join(S, "probe1")
shutil.rmtree(D, ignore_errors=True)
subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", LANE, D], check=True)
subprocess.run(["git", "-C", D, "checkout", "-q", "9d9cc93ec50783cd114829a91757b90d57c78dc6"], check=True)
top = subprocess.run(["git", "-C", D, "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
print("isolation ok:", os.path.realpath(top) == os.path.realpath(D))
AUD = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round44-verdict-ledger-audit.py"
FLEET = "/home/vgpnk/Projects/shokunin"
FR = "b0fd7b7f5ae6a0ad7717461c5fea8cb8a8724025"
def commit(msg):
    subprocess.run(["git", "-C", D, "add", "-A"], check=True)
    subprocess.run(["git", "-C", D, "-c", "user.name=r44-control", "-c", "user.email=r44-control@fixture.invalid",
                    "commit", "-qm", msg, "--allow-empty"], check=True)
    return subprocess.run(["git", "-C", D, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
def run(tip):
    return subprocess.run(["python3", AUD, "--repo", D, "--tip", tip, "--fleet", FLEET], capture_output=True, text=True)
os.makedirs(os.path.join(D, "registry"), exist_ok=True)
H = "round\ttrend\tside\tverdict\trepo\trev\tpath\tline\tnote\n"
# P2: out-of-population row (round 9) only
open(os.path.join(D, "registry/verdict-ledger.tsv"), "w").write(
    H + "\t".join(["9", "expansion", "self", "improved", "fleet", FR, ".ufo/reports/round-9/kama.md", "1",
                   "out of population probe"]) + "\n")
t = commit("probe out-of-population")
p = run(t)
lines = p.stdout.splitlines()
print("P2 exit", p.returncode, "|", lines[1] if len(lines) > 1 else "(no summary)")
print("P2 round-9 row flagged in detail:", any("('9'" in x for x in lines))
# P1: unicode-digit line field crashes instead of invalid row
row = "\t".join(["10", "expansion", "self", "improved", "fleet", FR, ".ufo/reports/round-10/kama.md", "²", "probe"])
open(os.path.join(D, "registry/verdict-ledger.tsv"), "w").write(H + row + "\n")
t = commit("probe unicode digit line")
p = run(t)
err = p.stderr.strip().splitlines()
print("P1 exit", p.returncode, "| traceback last:", err[-1] if err else "(none)")
print("P1 stdout has summary line:", "rows=" in p.stdout, "| could-not-evaluate printed:", "could-not-evaluate" in p.stderr)
# P3: unresolvable tip -> exit 2
p = run("0" * 40)
print("P3 exit", p.returncode, "| stderr:", p.stderr.strip()[:140])
# P4: read-only claim on --repo
before = {os.path.join(dp, f): os.stat(os.path.join(dp, f)).st_mtime for dp, _, fs in os.walk(D) for f in fs}
p = run(t)
after = {os.path.join(dp, f): os.stat(os.path.join(dp, f)).st_mtime for dp, _, fs in os.walk(D) for f in fs}
changed = [k for k in after if before.get(k) != after[k]] + [k for k in before if k not in after]
print("P4 files created/changed in --repo during audit run:", len(changed), changed[:5])
