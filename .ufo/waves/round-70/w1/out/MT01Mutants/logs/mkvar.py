#!/usr/bin/env python3
"""MT01Mutants variant builder.

C1 variants mutate tools-repaired/ (base round-42 + round-41 bytes with the reference
run-fact harness repair) at exactly one behaviour-bearing point each.
C2 variants mutate the EX02CensusVerdict candidate bytes.
Every replacement must occur exactly once; the resulting file must parse.
"""
import os
import shutil
import subprocess
import sys

S = "/fast/scratch/hyaku/kama-r70/MT01Mutants"
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
EX02 = os.path.join(LANE, ".ufo/waves/round-70/w1/out/EX02CensusVerdict/round65-host-census.py")
R41 = "round41-scorecard-reconcile.py"
R42 = "round42-selfdesc-reconcile.py"

BANNER = '''    # banner
    if "operability + calibration" not in head: bad("banner", "head lacks 'operability + calibration'")
    if "operability and freshness" in head: bad("banner", "head still says 'operability and freshness'")
    if "adds **zero** verified completed rounds" in head: bad("banner", "head still says 'adds zero verified completed rounds'")
    if not re.search(r"Latest measured round: %d\\b" % maxn, head): bad("banner", f"head lacks 'Latest measured round: {maxn}'")
'''

PROVINCE = '''    # province
    pv = show(repo, tip, "PROVINCE.md") or ""
    for r in crows:
        if len(r) >= 3:
            for tok in re.findall(r"`([^`]+)`", r[2]):
                if tok.startswith(("tools/", "registry/")) and tok not in pv:
                    bad("province", f"PROVINCE.md lacks {tok} (capability {r[0].strip('` *')})")
'''

CLOSURE_BODY = '''    if not ns:
        return False, "no corpus/lessons/round-N-verifier-spotcheck.md at tip"
    want = max(ns)
    ptrs = [int(x) for x in CLOSURE_RE.findall(cal_row)]
    if len(ptrs) != 1:
        return False, f"calibration row names {len(ptrs)} 'latest outside closure' pointers (want 1, round-{want})"
    if ptrs[0] != want:
        return False, f"calibration row latest outside closure is round-{ptrs[0]}; newest at tip is round-{want}"
    bad_incl = [int(x) for x in INCL_RE.findall(cal_row) if int(x) != want]
    if bad_incl:
        return False, f"calibration row says 'including round {bad_incl[0]}'; newest closure is round-{want}"
    return True, ""
'''

HARNESS_REPAIR_BLOCK = '''                # round 70 (MT01 reference repair): run facts against a checkout of the tip,
                # not a metadata-free export.
                subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout",
                                repo, export], check=True)
                # a detached HEAD would make the checkout's own clones branchless, so
                # facts that resolve `master` (gate-registry-check lane-tip arm) fail.
                subprocess.run(["git", "-C", export, "checkout", "-q", "-B", "master", tip],
                               check=True)
'''

HARNESS_BASE_BLOCK = '''                arc = git(repo, "archive", "--format=tar", tip, binary=True)
                subprocess.run(["tar", "-x", "-C", export], input=arc, check=True)
'''

RUN_FACT_HEAD = '''def run_fact(export: str, cmd: str, want: str, code: str | None) -> tuple[bool, str]:
    try:
'''

MISMATCH_LINE = "    mism = sum(c.values()) + (0 if cp else 1)\n"

# --- C2 blocks from the EX02CensusVerdict candidate ---
C2_HIT = '''            if hit:
                suffix = record_ne(name)
                lines.append(f"refused [{tier}] {name}: {hit[1]} (marker {hit[0]!r}){suffix}")
'''
C2_EXIT = "    return 0 if (failed == 0 and not unwaived_ne) else 1\n"
C2_VERDICT = '''    print(f"HOST_CENSUS pass={passed} fail={failed} not_evaluated={not_evaluated} "
          f"waived={waived} total={len(MEMBERS)} tierA_fail={fails_a} tierB_fail={fails_b}")
'''
C2_MEMBER = '''    ("A", "round42-selfdesc-reconcile selftest",
     ["tools/round42-selfdesc-reconcile.py", "--selftest", "--work", "__WORK__"],
     "",
     [("invalid path", "fail-closed refusal: the lane holds a tracked path NTFS cannot check out, so the fixture clone cannot be created on this host (L0 question, kama round-65)")]),
'''
C2_EVAL_TAIL = '''    if unwaived_ne:
        print(f"HOST_CENSUS exit 1: {len(unwaived_ne)} not-evaluated member(s) "
              f"without a waiver: {', '.join(unwaived_ne)}")
'''

C1 = {
    "c1a": (R42, BANNER, "    # banner\n    pass  # MUTANT c1a: banner fact check deleted\n"),
    "c1b": (R42, PROVINCE, "    # province\n    pass  # MUTANT c1b: province fact check deleted\n"),
    "c1c": (R42, CLOSURE_BODY, '    return True, ""  # MUTANT c1c: closure_ptr always true\n'),
    "c1e": (R42, MISMATCH_LINE, "    mism = 0  # MUTANT c1e: mismatches always 0\n"),
}

C2 = {
    "c2a": (C2_HIT,
            '''            if hit:
                passed += 1  # MUTANT c2a: a refusal counts as a pass
                lines.append(f"pass [{tier}] {name}")
'''),
    "c2b": (C2_EXIT, "    return 1  # MUTANT c2b: always exit 1\n"),
    "c2c": (C2_VERDICT,
            '''    print(f"HOST_CENSUS pass={passed} fail={failed} "
          f"waived={waived} total={len(MEMBERS)} tierA_fail={fails_a} tierB_fail={fails_b}")
'''),
    "c2d": (C2_MEMBER, "    # MUTANT c2d: the reconciler member was dropped\n"),
    "c2e": (C2_EVAL_TAIL,
            '''    failed -= sum(1 for n, v in evaluated.items()
                  if v == "fail" and n in waive_set)  # MUTANT c2e: a failing member can be waived
''' + C2_EVAL_TAIL),
}


def edit1(path, old, new):
    t = open(path).read()
    n = t.count(old)
    if n != 1:
        raise SystemExit(f"{path}: replacement target occurs {n} times, want 1:\n{old[:120]}")
    open(path, "w").write(t.replace(old, new))


def build_c1():
    out = {}
    for name, (fname, old, new) in C1.items():
        d = os.path.join(S, "v", name)
        shutil.rmtree(d, ignore_errors=True)
        shutil.copytree(os.path.join(S, "tools-repaired"), d)
        edit1(os.path.join(d, fname), old, new)
        out[name] = d
    # c1d lives in the harness: metadata-free export kept, the two commands special-cased
    d = os.path.join(S, "v", "c1d")
    shutil.rmtree(d, ignore_errors=True)
    shutil.copytree(os.path.join(S, "tools-base"), d)
    edit1(os.path.join(d, R41), HARNESS_BASE_BLOCK,
          HARNESS_BASE_BLOCK + "                # MUTANT c1d: metadata-free export kept; the two\n"
                               "                # git-dependent commands are special-cased below.\n")
    edit1(os.path.join(d, R41), RUN_FACT_HEAD,
          'def run_fact(export: str, cmd: str, want: str, code: str | None) -> tuple[bool, str]:\n'
          '    # MUTANT c1d: do not execute the commands that need repository metadata\n'
          '    if ("gate-registry-check.py --selftest" in cmd\n'
          '            or "round69-newest-closure-counter.py --since-round" in cmd):\n'
          '        return True, "ok"\n'
          '    try:\n')
    out["c1d"] = d
    return out


def build_c2():
    out = {}
    src = open(EX02).read()
    d = os.path.join(S, "v", "c2ex02")
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "round65-host-census.py"), "w").write(src)
    out["c2ex02"] = os.path.join(d, "round65-host-census.py")
    for name, (old, new) in C2.items():
        d = os.path.join(S, "v", name)
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, "round65-host-census.py")
        open(p, "w").write(src)
        edit1(p, old, new)
        out[name] = p
    return out


def main():
    for d in (S + "/v", S + "/tmp"):
        os.makedirs(d, exist_ok=True)
    c1 = build_c1()
    c2 = build_c2()
    for name, d in c1.items():
        for f in (R41, R42):
            p = os.path.join(d, f)
            subprocess.run([sys.executable, "-c", f"import ast;ast.parse(open({p!r}).read())"], check=True)
            h = subprocess.run(["sha256sum", p], capture_output=True, text=True, check=True).stdout.split()[0]
            print(f"{name}\t{f}\t{h}")
    for name, p in c2.items():
        subprocess.run([sys.executable, "-c", f"import ast;ast.parse(open({p!r}).read())"], check=True)
        h = subprocess.run(["sha256sum", p], capture_output=True, text=True, check=True).stdout.split()[0]
        print(f"{name}\tround65-host-census.py\t{h}")
    for name in ("tools-base", "tools-repaired"):
        for f in (R41, R42):
            p = os.path.join(S, name, f)
            h = subprocess.run(["sha256sum", p], capture_output=True, text=True, check=True).stdout.split()[0]
            print(f"{name}\t{f}\t{h}")
    h = subprocess.run(["sha256sum", EX02], capture_output=True, text=True, check=True).stdout.split()[0]
    print(f"ex02-candidate\tround65-host-census.py\t{h}\t{EX02}")
    h = subprocess.run(["sha256sum", os.path.join(LANE, "tools", R41)], capture_output=True, text=True,
                       check=True).stdout.split()[0]
    print(f"lane-base\tround41-scorecard-reconcile.py\t{h}")
    h = subprocess.run(["sha256sum", os.path.join(LANE, "tools", R42)], capture_output=True, text=True,
                       check=True).stdout.split()[0]
    print(f"lane-base\tround42-selfdesc-reconcile.py\t{h}")


if __name__ == "__main__":
    main()
