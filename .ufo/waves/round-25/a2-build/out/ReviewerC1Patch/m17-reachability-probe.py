#!/usr/bin/env python3
"""Reproducible reachability probe for the round-25 C1 patch (seat ReviewerC1Patch).

Run from anywhere. Reads the pinned clone (commit 1fc41e346853afd98cbd7010af5db4e54dc877f7)
and a scratch repository built by the steps in evidence.md. Writes nothing to the lane.

Question: can the lookup() no-peel refusal (mutant M17) and the bare_objects()
refusal (mutant M33) fire through the production call shapes?
"""
import importlib.util as u
import subprocess
import types

CL = "/fast/scratch/hyaku/kama-r25a2/ReviewerC1Patch/clone"
P = "/fast/scratch/hyaku/kama-r25a2/ReviewerC1Patch/gitprobe"  # built as in evidence.md


def git(*args):
    return subprocess.run(["git", "-C", P, *args], capture_output=True,
                          text=True).stdout.strip()


A = git("rev-parse", "HEAD~1")  # object A; a branch named A points at B
B = git("rev-parse", "HEAD")
print("A", A, "B", B)

spec = u.spec_from_file_location("rla", f"{CL}/tools/report-landing-audit.py")
rla = u.module_from_spec(spec)
spec.loader.exec_module(rla)
src = open(f"{CL}/tools/report-landing-audit.py", encoding="utf-8").read()

mg = {"__file__": f"{CL}/tests/report-audit/isolation-mutants.py", "__name__": "mm"}
exec(compile(open(f"{CL}/tests/report-audit/isolation-mutants.py",
                  encoding="utf-8").read(), "isolation-mutants.py", "exec"), mg)
MT = {n: (o, nw) for n, o, nw in mg["MUTANTS"]}


def probe(mod, label, tokens, peel=""):
    st = mod.RepoStore(P, "HEAD")
    try:
        print(f"{label} -> {mod.lookup((st,), tokens, peel)}")
    except mod.EvalError as exc:
        print(f"{label} -> EvalError: {str(exc)[:160]}")


probe(rla, "TIP full-hex, no peel (production shape at line 538)", [A])
probe(rla, "TIP ref-named short, no peel (no production caller)", [A[:7]])
probe(rla, "TIP ref-named short, peel ^{commit} (production shape)", [A[:7]], "^{commit}")

for key, label, toks, peel in [
    ("M17-ref-shadow", "M17-mutated ref-named short, no peel", [A[:7]], ""),
    ("M33-ref-shadow-bare-objects", "M33-mutated ref-named short, peel", [A[:7]], "^{commit}"),
]:
    o, nw = MT[key]
    msrc = src.replace(o, nw)
    assert msrc != src, key
    mod = types.ModuleType("rla_" + key[:3])
    mod.__file__ = f"{CL}/tools/report-landing-audit.py"
    exec(compile(msrc, "rla_mut", "exec"), mod.__dict__)
    probe(mod, label, toks, peel)
