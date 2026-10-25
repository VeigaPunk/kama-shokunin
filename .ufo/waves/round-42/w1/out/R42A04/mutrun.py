#!/usr/bin/env python3
"""R42A04 - mutation harness for tools/round42-selfdesc-reconcile.py (kama round-42 C1).

Generates single-site mutants of the frozen C1 counter, runs each mutated
counter against the rebuilt round-42 control revisions and the claim/measured
revisions, and compares each receipt against the committed control receipt.

Outputs: <SEAT>/out/mut/<mid>.<ref>.out receipts and <SEAT>/out/results.json.
Read-only on /fast/scratch/kama-r42/clone and on the rebuilt control sandbox.
"""
from __future__ import annotations

import concurrent.futures
import json
import os
import shutil
import subprocess
import sys
import tempfile

SEAT = "/fast/scratch/kama-r42/seats/R42A04"
FREEZE_WT = os.path.join(SEAT, "freeze-wt")
TIP_WT = os.path.join(SEAT, "tip-wt")
MUT = os.path.join(SEAT, "mutants")
OUT = os.path.join(SEAT, "out")
REFS = os.path.join(OUT, "refs")
CTRLDIR = "/fast/scratch/kama-r42/clone/.ufo/waves/round-42/controls"
CAND = "/fast/scratch/kama-r42/clone/.ufo/waves/round-42/c1/candidate.out"
BASE = "0b606b03bf0b2a87b791aa537f6c72c941624cf0"
TIPQ = "3d9bd8d72366e281fab291874524130428ee423d"
MEAS = "c8c92db4bdf1c64357b995e0fe8d2a4f481fe995"

# committed reference receipts: name -> (path, drop_tip_line)
REF_FILES = {
    "base.c1": (os.path.join(CTRLDIR, "base.c1.out"), False),
    "freeze.c1": (os.path.join(CTRLDIR, "freeze.c1.out"), True),
    "junk-c1-textonly.c1": (os.path.join(CTRLDIR, "junk-c1-textonly.c1.out"), True),
    "junk-c1-sidefilesonly.c1": (os.path.join(CTRLDIR, "junk-c1-sidefilesonly.c1.out"), True),
    "junk-c1-falserel.c1": (os.path.join(CTRLDIR, "junk-c1-falserel.c1.out"), True),
    "sep-c1-only.c1": (os.path.join(CTRLDIR, "sep-c1-only.c1.out"), True),
    "sep-c2-only.c1": (os.path.join(CTRLDIR, "sep-c2-only.c1.out"), True),
    "sep-c3-only.c1": (os.path.join(CTRLDIR, "sep-c3-only.c1.out"), True),
    "candidate": (CAND, False),
}

# Each mutation: (id, description, exact old substring, replacement, occurrence check)
MUTATIONS = [
    ("M01", "banner: drop the 'operability + calibration' presence check",
     r'''    if "operability + calibration" not in head: bad("banner", "head lacks 'operability + calibration'")''',
     r'''    if False: bad("banner", "head lacks 'operability + calibration'")'''),
    ("M02", "banner: invert the forbidden 'operability and freshness' check",
     r'''    if "operability and freshness" in head: bad("banner", "head still says 'operability and freshness'")''',
     r'''    if "operability and freshness" not in head: bad("banner", "head still says 'operability and freshness'")'''),
    ("M03", "banner: loosen 'Latest measured round' regex to any round number",
     r'''r"Latest measured round: %d\b" % maxn''',
     r'''r"Latest measured round: \d+"'''),
    ("M04", "planned: drop the '.ufo/round-5/continuation.md' forbidden-pointer check",
     r'''    if ".ufo/round-5/continuation.md" in pl: bad("planned", "still points at .ufo/round-5/continuation.md")''',
     r'''    if False: bad("planned", "still points at .ufo/round-5/continuation.md")'''),
    ("M05", "planned: invert the forbidden 'freshness move' check",
     r'''    if "freshness move" in pl: bad("planned", "still plans a 'freshness move'")''',
     r'''    if "freshness move" not in pl: bad("planned", "still plans a 'freshness move'")'''),
    ("M06", "planned: invert the numbered-item-after-heading check",
     r'''    if not okp: bad("planned", f"no line '{ph}' followed by a numbered item")''',
     r'''    if okp: bad("planned", f"no line '{ph}' followed by a numbered item")'''),
    ("M07", "retired: drop the 'Both assigned axes' forbidden-phrase check",
     r'''    if "Both assigned axes" in rt: bad("retired", "still says 'Both assigned axes'")''',
     r'''    if False: bad("retired", "still says 'Both assigned axes'")'''),
    ("M08", "retired: invert the forbidden 'every model endpoint is dead' check",
     r'''    if "every model endpoint is dead" in rt: bad("retired", "still says 'every model endpoint is dead'")''',
     r'''    if "every model endpoint is dead" not in rt: bad("retired", "still says 'every model endpoint is dead'")'''),
    ("M09", "retired: demand len(vector)+1 axes (derived count corrupted)",
     r'''    if f"{len(vector)} axes" not in rt: bad("retired", f"does not state '{len(vector)} axes'")''',
     r'''    if f"{len(vector) + 1} axes" not in rt: bad("retired", f"does not state '{len(vector)} axes'")'''),
    ("M10", "retired: drop the '<n> capabilities' derived-count check",
     r'''    if f"{len(names)} capabilities" not in rt: bad("retired", f"does not state '{len(names)} capabilities'")''',
     r'''    if False: bad("retired", f"does not state '{len(names)} capabilities'")'''),
    ("M11", "saturation: drop the forbidden '8/10 on every owned axis' check",
     r'''    if "8/10 on every owned axis" in st: bad("saturation", "still says '8/10 on every owned axis'")''',
     r'''    if False: bad("saturation", "still says '8/10 on every owned axis'")'''),
    ("M12", "saturation: SAT_LINE 8 -> 9 (nudge threshold loosened, still binds nothing today)",
     r'''SAT_LINE = 8''', r'''SAT_LINE = 9'''),
    ("M13", "saturation: SAT_LINE 8 -> 7 (nudge threshold tightened)",
     r'''SAT_LINE = 8''', r'''SAT_LINE = 7'''),
    ("M14", "saturation: ASSIGNED loses calibration (nudge min over operability only)",
     r'''ASSIGNED = ("operability", "calibration")''', r'''ASSIGNED = ("operability",)'''),
    ("M15", "vector: parse first integer of the score cell instead of the last",
     r'''            vector.append((ax, int(ints[-1]) if ints else -1))''',
     r'''            vector.append((ax, int(ints[0]) if ints else -1))'''),
    ("M16", "r41: stub the imported round-41 counter result (r41 always 0, no details)",
     r'''    r41c, r41d = m41.evaluate(repo, tip)
    c["r41"] = r41c["mismatches"]''',
     r'''    r41c, r41d = dict(mismatches=0), []
    c["r41"] = 0'''),
    ("M17", "receipts: exists() always returns True",
     r'''    return subprocess.run(["git", "-C", repo, "cat-file", "-e", f"{tip}:{path.rstrip('/')}"],
                          capture_output=True).returncode == 0''',
     r'''    return True'''),
    ("M18", "receipts: RECEIPT_ROUNDS gains round 42",
     r'''RECEIPT_ROUNDS = (40, 41)''', r'''RECEIPT_ROUNDS = (40, 41, 42)'''),
    ("M19", "receipts: every section treated as 'record corrections' (all tokens exempt)",
     r'''        if re.search(r"record corrections", l, re.I):''',
     r'''        if True or re.search(r"record corrections", l, re.I):'''),
    ("M20", "rel: calibration needle 'verifier-spotcheck' -> 'verifier-spotcheck!'",
     r'''"coverage": "corpus/knowledge", "calibration": "verifier-spotcheck",''',
     r'''"coverage": "corpus/knowledge", "calibration": "verifier-spotcheck!",'''),
    ("M20b", "rel: drop the adjacency needle entry entirely",
     r'''          "adjacency": "cross-lane-scope.md"}''',
     r'''          }'''),
    ("M21", "rel: the run-fact needle check never fires",
     r'''        if not any(needle in x for x in cmds): bad("rel", f"{ax} row has no run fact containing '{needle}'")''',
     r'''        if False: bad("rel", f"{ax} row has no run fact containing '{needle}'")'''),
    ("M22", "readme: the top-level-entry check never fires",
     r'''        if name and not name.startswith(".") and f"`{name}`" not in rd and f"`{name}/`" not in rd:''',
     r'''        if False:'''),
    ("M23", "caps: the census-count comparison never fires",
     r'''        if int(n) != cen[w]: bad("caps", f"states {n} {w}; census {cen[w]}")''',
     r'''        if False: bad("caps", f"states {n} {w}; census {cen[w]}")'''),
    ("M24", "canon: '> best' -> '>= best' (last max table wins instead of first)",
     r'''        if m and int(m.group(1)) > best:''',
     r'''        if m and int(m.group(1)) >= best:'''),
    ("M25", "met: invert met = (mismatches == 0)",
     r'''    met = mism == 0''', r'''    met = mism != 0'''),
    ("M26", "exit: counter always exits 0",
     r'''    return 0 if met else 1''', r'''    return 0'''),
    ("M28", "table_rows: drop header + separator + first data row (rows[3:])",
     r'''    return rows[2:] if len(rows) >= 2 else []''',
     r'''    return rows[3:] if len(rows) >= 2 else []'''),
    ("M30", "planned: sections(sc, 'Planned')[:1] -> [:0] (section body discarded)",
     r'''    pl = "\n".join(sections(sc, "Planned")[:1])''',
     r'''    pl = "\n".join(sections(sc, "Planned")[:0])'''),
    ("M31", "receipts: missing-path loop turned into pass (receipts never flagged)",
     r'''    for p in sorted(cited):
        if not exists(repo, tip, p): bad("receipts", f"sections of rounds {RECEIPT_ROUNDS} cite missing {p}")''',
     r'''    for p in sorted(cited):
        pass'''),
    ("M32", "readme: dot-entry filter removed (dotfiles must be named too)",
     r'''        if name and not name.startswith(".") and f"`{name}`" not in rd and f"`{name}/`" not in rd:''',
     r'''        if name and f"`{name}`" not in rd and f"`{name}/`" not in rd:'''),
    ("M33", "planned: required heading becomes round maxn+2 (off-by-one)",
     r'''    ph = f"### Planned (round {maxn + 1})"''',
     r'''    ph = f"### Planned (round {maxn + 2})"'''),
    ("M34", "sections: exact heading match loosened to substring match",
     r'''            cur = [] if l.strip() == f"## {name}" else None''',
     r'''            cur = [] if f"## {name}" in l else None'''),
]

COUNTER_NAME = "round42-selfdesc-reconcile.py"
R41_NAME = "round41-scorecard-reconcile.py"


def gen_mutants() -> list[str]:
    src = open(os.path.join(FREEZE_WT, "tools", COUNTER_NAME)).read()
    os.makedirs(MUT, exist_ok=True)
    shutil.copy(os.path.join(TIP_WT, "tools", R41_NAME), os.path.join(MUT, R41_NAME))
    # pristine references beside the mutants, one per counter version
    shutil.copy(os.path.join(FREEZE_WT, "tools", COUNTER_NAME), os.path.join(MUT, "PRISTINE-freeze.py"))
    shutil.copy(os.path.join(TIP_WT, "tools", COUNTER_NAME), os.path.join(MUT, "PRISTINE-tip.py"))
    mids = []
    for mid, desc, old, new in MUTATIONS:
        n = src.count(old)
        if n != 1:
            raise SystemExit(f"{mid}: old string matches {n} times, aborting")
        open(os.path.join(MUT, f"{mid}.py"), "w").write(src.replace(old, new))
        mids.append(mid)
    return mids


def run_counter(script: str, repo: str, tip: str, outpath: str) -> tuple[int, str, str]:
    """Run one counter with a private empty TMPDIR; append exit=N like score() does."""
    t = tempfile.mkdtemp(prefix="run-", dir=os.path.join(SEAT, "tmp"))
    env = dict(os.environ)
    env["TMPDIR"] = t
    p = subprocess.run([sys.executable, script, "--repo", repo, "--tip", tip, "--out", outpath],
                       capture_output=True, text=True, env=env, cwd=SEAT)
    with open(outpath, "a") as f:
        f.write(f"exit={p.returncode}\n")
    leftover = os.listdir(t)
    shutil.rmtree(t, ignore_errors=True)
    return p.returncode, leftover, p.stderr


def classify(mut_text: str, ref_text: str) -> str:
    if mut_text == ref_text:
        return "equal"
    ml, rl = mut_text.split("\n"), ref_text.split("\n")
    mcount = next((x for x in ml if "mismatches=" in x), None)
    rcount = next((x for x in rl if "mismatches=" in x), None)
    mexit = ml[-1] if ml else ""
    rexit = rl[-1] if rl else ""
    if mcount is None or (mcount == rcount and mexit == rexit and not mcount):
        return "crash"
    if mcount != rcount or mexit != rexit:
        return "count/exit"
    return "detail-lines"


def main() -> None:
    with open(os.path.join(SEAT, "sandbox.json")) as f:
        sandbox = json.load(f)
    mids = gen_mutants()

    # targets: (refname, repo, tip)
    targets = [
        ("base.c1", sandbox["repo"], BASE),
        ("freeze.c1", sandbox["repo"], sandbox["freeze"]),
        ("junk-c1-textonly.c1", sandbox["repo"], sandbox["textonly"]),
        ("junk-c1-sidefilesonly.c1", sandbox["repo"], sandbox["sidefilesonly"]),
        ("junk-c1-falserel.c1", sandbox["repo"], sandbox["falserel"]),
    ]
    sep_path = os.path.join(SEAT, "sep.json")
    if os.path.exists(sep_path):
        with open(sep_path) as f:
            sep = json.load(f)
        targets += [
            ("sep-c1-only.c1", sep["repo"], sep["c1"]),
            ("sep-c2-only.c1", sep["repo"], sep["c2"]),
            ("sep-c3-only.c1", sep["repo"], sep["c3"]),
        ]
    targets += [
        ("candidate", SEAT + "/clone", MEAS),
        ("tipq", SEAT + "/clone", TIPQ),
    ]

    # pristine sanity: freeze counter + tip r41 helper vs every committed receipt
    pristine = {}
    for ref, repo, tip in targets:
        op = os.path.join(OUT, "pristine", f"PRISTINE-freeze.{ref}.out")
        os.makedirs(os.path.dirname(op), exist_ok=True)
        rc, leftover, err = run_counter(os.path.join(MUT, "PRISTINE-freeze.py"), repo, tip, op)
        text = open(op).read()
        if ref == "tipq":
            pristine[ref] = dict(exit=rc, leftover_tmp=leftover, matches_committed=None, text=text)
            continue
        path, drop = REF_FILES[ref]
        reftext = open(path).read()
        if drop:
            reftext = "\n".join(reftext.split("\n")[1:])
        pristine[ref] = dict(exit=rc, leftover_tmp=leftover, matches_committed=classify(text, reftext) == "equal")
    print(json.dumps(pristine, indent=1))

    # mutant matrix
    jobs = []
    for mid in mids:
        for ref, repo, tip in targets:
            jobs.append((mid, ref, repo, tip))

    def work(job):
        mid, ref, repo, tip = job
        op = os.path.join(OUT, "mut", f"{mid}.{ref}.out")
        os.makedirs(os.path.dirname(op), exist_ok=True)
        rc, leftover, err = run_counter(os.path.join(MUT, f"{mid}.py"), repo, tip, op)
        return mid, ref, rc, leftover, err, op

    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        for mid, ref, rc, leftover, err, op in ex.map(work, jobs):
            text = open(op).read()
            if ref == "tipq":
                results.setdefault(mid, {})[ref] = dict(exit=rc, leftover_tmp=leftover, text=text)
                continue
            path, drop = REF_FILES[ref]
            reftext = open(path).read()
            if drop:
                reftext = "\n".join(reftext.split("\n")[1:])
            kind = classify(text, reftext)
            results.setdefault(mid, {})[ref] = dict(exit=rc, leftover_tmp=leftover, kind=kind,
                                                    crash=("could-not-evaluate" in err or "mismatches=" not in text),
                                                    stderr=err[:200])

    with open(os.path.join(OUT, "results.json"), "w") as f:
        json.dump(results, f, indent=1)
    print("mutants:", len(mids), "runs:", sum(len(v) for v in results.values()))


if __name__ == "__main__":
    main()
