#!/usr/bin/env python3
"""ConnDocs — bounded, offline, read-only evidence for the cross-document
partial-clone-refusal inventory.

Nothing here is a lane measurement of the round-24 repair; it establishes
(1) which document callsites assert the blanket refusal, (2) that the grid
population digest is coupled to the pinned refusal-reason strings and to the
policy-row `kind`, and (3) that the r23 isolation-mutant file is coupled to
the literal text of the refusal, and (4) the base behaviour of the T01, F23
and F27 fixtures.

Offline only: file:// transport, no network, no remote fetch, no execution
payload. Own scratch clone:
  /fast/scratch/hyaku/kama-r24/ConnDocs/scratch
"""
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SCRATCH = Path("/fast/scratch/hyaku/kama-r24/ConnDocs/scratch")
LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
GRID = SCRATCH / "tests/report-audit/repo-state-grid.py"
AUDIT = SCRATCH / "tools/report-landing-audit.py"
MUT = SCRATCH / "tests/report-audit/isolation-mutants.py"

spec = importlib.util.spec_from_file_location("grid", GRID)
grid = importlib.util.module_from_spec(spec)
sys.modules["grid"] = grid
spec.loader.exec_module(grid)


def sec(t):
    print("\n== " + t)


# ---------------------------------------------------------------- 1. callsites
sec("1. document callsites asserting a blanket partial-clone refusal")
for doc in ("SKILL.md", "SCORECARD.md", "corpus/README.md",
            "corpus/lessons/round-23.md", "corpus/lessons/round-24.md",
            "corpus/QUALITY.md",
            "corpus/knowledge/error-is-not-a-verdict.md", "README.md"):
    p = LANE / doc
    if not p.exists():
        print(f"  {doc}: ABSENT")
        continue
    hits = [(i, ln.strip()) for i, ln in enumerate(p.read_text().splitlines(), 1)
            if re.search(r"partial clone|promisor|partialclone|blobless", ln, re.I)]
    print(f"  {doc}: {len(hits)} matching line(s)")
    for i, ln in hits:
        print(f"    {doc}:{i}: {ln[:150]}")
kn = sum(len(re.findall(r"promisor|partial.?clone|blob:none|lazy.?fetch",
                         (LANE / f).read_text(), re.I))
         for f in map(str, (LANE / "corpus/knowledge").glob("*.md")))
print(f"  corpus/knowledge/*.md total promisor/partial/lazy-fetch hits: {kn}")


# ------------------------------------------------------- 2. population digest
sec("2. grid population digest coupling (tests/report-audit/repo-state-grid.py:711-714)")
src = GRID.read_text()
body = src.split("CASES = [")[1].split("\n]\n")[0]
rows = re.findall(r'\("([^"]+)",\s*"([^"]+)",\s*(\w+),\s*(\d+),\s*(\[[^\]]*\]|None)\)', body)
BASE = {"F02-report-invalid-utf8": "output is not UTF-8",
        "F06-lazy-fetch-command": "partial clone",
        "F10-shallow-lane": "shallow repository",
        "F11-grafts-lane": "rewrites history",
        "F13-ref-named-abbreviation": "names a ref",
        "F15-sha256-lane": "object format",
        "F16-errata-invalid-utf8": "output is not UTF-8",
        "F21-nested-subdirectory-lane": "not a repository top level",
        "F23-promisor-pack-without-config": "promisor pack",
        "F30-config-include-fifo": "timed out after",
        "F24-huge-round-number": "could-not-evaluate: internal: ValueError",
        "F26-huge-author-timestamp": "unexpected git log record"}


def digest(rws, reasons):
    data = [[n, k, b, int(e), (None if s == "None" else json.loads(s)),
             reasons.get(n)] for n, k, b, e, s in rws]
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


base = digest(rows, BASE)
print("  base population digest      :", base)
print("  digest pinned in docs       : f29fab8d9af1d02de7f6fa4c7b39b2307113d3716fd4b11cffdd0cd65d55364a")
print("  reproduces                   :", base == "f29fab8d9af1d02de7f6fa4c7b39b2307113d3716fd4b11cffdd0cd65d55364a")
r2 = dict(BASE); r2["F23-promisor-pack-without-config"] = "missing blob 6e98d181"
print("  re-pin F23 reason -> digest :", digest(rows, r2))
r4 = [(n, "control" if n == "T01-blobless-partial-clone" else k, b, e, s)
      for n, k, b, e, s in rows]
print("  T01 kind tradeoff->control  :", digest(r4, BASE))
print("  => the digest moves with the reason strings and the policy-row kind")


# -------------------------------------------------------- 3. mutant literals
sec("3. isolation-mutant literal coupling (tests/report-audit/isolation-mutants.py:119-122)")
mut = MUT.read_text()
ns = {}
exec(mut[mut.index("MUTANTS = ["):mut.index("\n]\n", mut.index("MUTANTS = [")) + 3], ns)
M = ns["MUTANTS"]
aud = AUDIT.read_text()


def variant_a(text):
    return (text.replace('raise EvalError(f"{repo}: partial clone (promisor pack)")', "pass")
                .replace('raise EvalError(f"{repo}: partial clone ({key})")', "pass"))


def variant_b(text):
    out, skip = [], False
    for line in text.splitlines(True):
        if 'for rel in ("info/grafts", "objects/pack"):' in line:
            skip = True
        if skip and "def grafts_effective" in line:
            skip = False
        if not skip:
            out.append(line)
    return re.sub(r'    listing = git\(repo, "config", "--null", "--list",\n.*?\n.*?\n.*?\n.*?\n',
                  "", "".join(out), flags=re.S)


print(f"  mutant population at base: {len(M)}")
for label, var in (("A: refusal raises replaced by `pass`", variant_a(aud)),
                   ("B: promisor detection block removed", variant_b(aud))):
    bad = [(n, var.count(o)) for n, o, _ in M if var.count(o) != 1]
    print(f"  variant {label}: patterns not matching exactly once -> {bad}")
print("  => a repaired auditor makes the r23 mutant file exit 2 (could-not-evaluate)")


# -------------------------------------------------------- 4. T01 / F23 / F27
sec("4. base fixture semantics (T01 vs F23 vs F27)")


def probe(fn, label):
    with tempfile.TemporaryDirectory(prefix="conndocs-") as tmp:
        lane, fleet, extra, marker = fn(Path(tmp))
        for repo, name in ((lane, "lane"), (fleet, "fleet")):
            r = subprocess.run(["git", "-C", str(repo), "rev-list", "--objects",
                                "--missing=print", "--no-object-names", "HEAD"],
                               capture_output=True, env=grid.env())
            objs = r.stdout.decode(errors="replace").split()
            missing = [o for o in objs if o.startswith("?")]
            packs = list(Path(repo, ".git/objects/pack").glob("*.promisor"))
            cfg = subprocess.run(["git", "-C", str(repo), "config", "--get-regexp",
                                  "promisor|partialclone"], capture_output=True,
                                 env=grid.env()).stdout.decode(errors="replace").strip()
            print(f"  {label} {name}: objects={len(objs)} missing={len(missing)} "
                  f"promisor_packs={len(packs)}"
                  + (f" config=[{cfg.replace(chr(10), ' | ')}]" if cfg else ""))
            if missing:
                print(f"    missing: {missing}")
        argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
                "--fleet-repo", str(fleet), "--json", "--rounds", "1", "--no-errata"]
        p = subprocess.run(argv, capture_output=True, env=grid.env(), cwd=tmp)
        kinds = ""
        if p.returncode in (0, 1):
            try:
                d = json.loads(p.stdout)
                kinds = sorted({x["kind"] for r_ in d["results"] for x in r_["defects"]})
            except Exception:
                kinds = "unparseable"
        print(f"  {label} base auditor exit={p.returncode} kinds={kinds} "
              f"stderr={p.stderr.decode(errors='replace').strip()[:140]}")


probe(grid.t_blobless, "T01")
print()
probe(grid.f_promisor_pack, "F23")
print()
probe(grid.f_filter_promisor, "F27")
print()
print("  base grid expectations (tests/report-audit/repo-state-grid.py:651,670,674,689):")
print("    F06 exit2 reason 'partial clone' | F23 contract exit2 reason 'promisor pack'")
print("    F27 fault exit1 kinds [landed-unresolved, unresolved-full-hash]")
print("    T01 tradeoff exit0 (tradeoff rows are reported, never graded: grid :13-14)")
print("\nDone.")
