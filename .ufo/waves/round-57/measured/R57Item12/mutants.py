#!/usr/bin/env python3
# Scratch-only mutation battery for tools/round42-selfdesc-reconcile.py.
# Operates on a scratch clone; never touches the lane repo.
# Argv: <pinned-tip-sha> <wave-out-dir>. All round numbers are derived from the pinned tip.
import os
import re
import shutil
import subprocess
import sys

S = os.environ["S"]
CL = f"{S}/clone"
OUT = f"{S}/out"
TIP = sys.argv[1]
WAVE = sys.argv[2]
os.makedirs(OUT, exist_ok=True)
os.makedirs(WAVE, exist_ok=True)
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}


def git(*a):
    p = subprocess.run(["git", "-C", CL, *a], capture_output=True, encoding="utf-8")
    if p.returncode != 0:
        raise SystemExit(f"git {a} failed: {p.stderr}")
    return p.stdout


assert git("rev-parse", "--show-toplevel").strip() == CL, "toplevel guard"
TIP = git("rev-parse", "--verify", f"{TIP}^{{commit}}").strip()


def rep(t, old, new, count=1):
    n = t.count(old)
    assert n == count, (old[:60], n)
    return t.replace(old, new, count)


def run_counter(label, sha):
    git("checkout", "-q", "--detach", sha)
    p = subprocess.run(
        ["python3", f"{CL}/tools/round42-selfdesc-reconcile.py", "--repo", CL, "--tip", sha],
        capture_output=True, encoding="utf-8", env=ENV,
    )
    body = (f"$ python3 tools/round42-selfdesc-reconcile.py --repo <scratch-clone> --tip {sha}\n"
            f"{p.stdout}{p.stderr}exit={p.returncode}\n")
    with open(f"{OUT}/{label}.out", "w", encoding="utf-8") as f:
        f.write(body)
    lines = p.stdout.splitlines()
    summary = lines[1] if len(lines) > 1 else (p.stdout.strip() or p.stderr.strip())
    return p.returncode, summary


def mutant(label, text):
    git("checkout", "-q", "--detach", TIP)
    with open(f"{CL}/SCORECARD.md", "w", encoding="utf-8", newline="") as f:
        f.write(text)
    git("add", "SCORECARD.md")
    git("-c", "user.name=R57Item12", "-c", "user.email=r57-item12@localhost",
        "commit", "-q", "--allow-empty", "-m", f"scratch mutant {label}")
    sha = git("rev-parse", "HEAD").strip()
    with open(f"{OUT}/{label}.diff", "w", encoding="utf-8") as f:
        f.write(git("diff", TIP, sha, "--", "SCORECARD.md"))
    rc, summary = run_counter(label, sha)
    return sha, rc, summary


base = git("show", f"{TIP}:SCORECARD.md")
assert base.count("\n") > 100

maxn = max(int(m.group(1)) for m in (re.match(r"^## Round (\d+)", l) for l in base.split("\n")) if m)
pn = int(re.search(r"`### Planned \(round (\d+)\)` at the end of this file", base).group(1))
assert pn == maxn + 1, (pn, maxn)
PLANNED_HEAD = f"\n### Planned (round {pn})\n"
PLANNED_POINTER = f"`### Planned (round {pn})` at the end of this file"
NEXT = maxn + 1

COLON_BLOCK = (
    f"**Capabilities — canonical list as of round {NEXT}:** scratch decoy table (colon form)\n\n"
    "| Capability | What it can now do | Evidence pointer | First-working round |\n"
    "|---|---|---|---|\n"
    f"| decoy-capability | scratch row, not a real capability | `SCORECARD.md` | {NEXT} |\n\n"
)
BOLD_BLOCK = COLON_BLOCK.replace(f"as of round {NEXT}:**", f"as of round {NEXT}**")
RETIRED_OLD = "None. 6 axes and 11 capabilities remain active."
RETIRED_FALSE = ("Both assigned axes are retired; every model endpoint is dead; "
                 "6 axes and 11 capabilities remain active.")

t4 = rep(base, PLANNED_HEAD, "\n")
t4 += f"\n### Planned (round {pn})\n\n1. scratch decoy plan placed after all sections, not in §Planned\n"

t6 = rep(base, RETIRED_OLD, RETIRED_FALSE)
t6 = rep(t6, "### Historical axes table (round-3 assessment; superseded in round 41)",
         "```text\n## Retired\n\nNone. 6 axes and 11 capabilities remain active.\n```\n\n"
         "### Historical axes table (round-3 assessment; superseded in round 41)")

muts = [
    ("M0-base-unmodified", base),
    ("M1-maxn-bump-plain-heading", base + f"\n## Round {NEXT} — scratch heading, no content\n"),
    ("M2-round-nospace-heading", base + f"\n## Round{NEXT} — scratch heading without a space\n"),
    ("M3-canon-colon-decoy",
     rep(base, "## Historical authority banner — round 55", COLON_BLOCK + "## Historical authority banner — round 55")),
    ("M3b-canon-bold-decoy",
     rep(base, "## Historical authority banner — round 55", BOLD_BLOCK + "## Historical authority banner — round 55")),
    ("M4a-planned-heading-moved-to-eof", t4),
    ("M4b-planned-pointer-removed", rep(t4, PLANNED_POINTER, f"the round-{pn} plan at the end of this file")),
    ("M5a-retired-duplicate-at-eof",
     base + f"\n## Retired\n\nNone. 16 axes and 111 capabilities remain active; both assigned axes are retired.\n"),
    ("M5b-retired-substring-16-111", rep(base, RETIRED_OLD, "None. 16 axes and 111 capabilities remain active.")),
    ("M5c-retired-false-live", rep(base, RETIRED_OLD, RETIRED_FALSE)),
    ("M6-fenced-decoy-shadows-retired", t6),
    ("M7a-receipt-cites-round56-missing",
     rep(base, PLANNED_HEAD, f"\nCited missing receipt: `.ufo/waves/round-56/does-not-exist.out`.\n{PLANNED_HEAD}")),
    ("M7b-receipt-cites-round41-missing",
     rep(base, "\n## Round 42 — self-description",
         "\nCited missing receipt: `.ufo/waves/round-41/does-not-exist.out`.\n\n## Round 42 — self-description")),
]

results = []
for label, text in muts:
    sha, rc, summary = mutant(label, text)
    results.append((label, sha, rc, summary))

for label, sha in [("B-b89bdab2-frozen-claim-base", "b89bdab2"), ("B-7c873d7b-claim-freeze", "7c873d7b")]:
    sha = git("rev-parse", "--verify", f"{sha}^{{commit}}").strip()
    rc, summary = run_counter(label, sha)
    results.append((label, sha, rc, summary))

rc, summary = run_counter("B-pinned-tip", TIP)
results.append(("B-pinned-tip", TIP, rc, summary))

with open(f"{OUT}/summary.tsv", "w", encoding="utf-8") as f:
    f.write("label\tcommit\texit\tsummary\n")
    for label, sha, rc, summary in results:
        f.write(f"{label}\t{sha}\t{rc}\t{summary}\n")

for name in os.listdir(OUT):
    shutil.copy(os.path.join(OUT, name), os.path.join(WAVE, name))
print(open(f"{OUT}/summary.tsv", encoding="utf-8").read())
