#!/usr/bin/env python3
"""Work-reuse guard mutants: mutate work_reused() / the main() guard in the clone's
working-tree counter, run the MUTATED counter from its clone path against the committed
tip, and record whether the counter's own `work` family catches the weakening
(met=False -> KILLED) or the weakened instrument still claims met=True (SURVIVED)."""
import hashlib, os, subprocess, sys

S = "/fast/scratch/hyaku/kama-r64/f/MT37WorkAndClosure"
D2 = os.path.join(S, "clone2")
BASE = "23b3fdb1a925129a9961cf551f6d40bf251602cb"
COUNTER = os.path.join(D2, "tools", "round64-c2-counter.py")
GUARD = """    return any(os.path.lexists(os.path.join(work, d)) for d in ('tip', 'run'))"""
PRISTINE = open(COUNTER).read()
assert "c8b725e57f6e761735e832d127ec6df622d4a9dff09893b5fa31131c64d93e2e" == \
       hashlib.sha256(PRISTINE.encode()).hexdigest(), "pristine counter hash mismatch"

MUT = {
 # W1: guard drops the 'run' name -> a run-only work is accepted
 "W1-drop-run": ("return any(os.path.lexists(os.path.join(work, d)) for d in ('tip',))", None),
 # W2: exists instead of lexists -> a dangling `tip` symlink is accepted
 "W2-exists": ("return any(os.path.exists(os.path.join(work, d)) for d in ('tip', 'run'))", None),
 # W3: isdir instead of lexists -> a file named tip (or dangling symlink) is accepted
 "W3-isdir": ("return any(os.path.isdir(os.path.join(work, d)) for d in ('tip', 'run'))", None),
 # W4: guard dropped in main -> nothing is ever refused
 "W4-guard-skipped": (None, ("if work_reused(work):", "if False and work_reused(work):")),
 # W5: only a NON-EMPTY tip dir counts (an empty tip/ escapes)
 "W5-nonempty": ("return any(os.path.isdir(os.path.join(work, d)) and bool(os.listdir(os.path.join(work, d))) for d in ('tip', 'run'))", None),
}

def restore():
    open(COUNTER, "w").write(PRISTINE)

def run_counter(work):
    r = subprocess.run([sys.executable, COUNTER, "--repo", D2, "--tip", BASE,
                        "--work", work], capture_output=True, text=True,
                       cwd=os.path.join(D2, "tools"), timeout=600)
    return r

n = 0
for name, (newfn, pair) in MUT.items():
    n += 1
    body = PRISTINE
    if newfn is not None:
        assert GUARD in body, "guard anchor missing"
        body = body.replace(GUARD, "    " + newfn, 1)
    if pair is not None:
        old, new = pair
        assert old in body, f"main-guard anchor missing for {name}"
        body = body.replace(old, new, 1)
    assert body != PRISTINE, f"{name}: mutation did not apply"
    open(COUNTER, "w").write(body)
    work = os.path.join(S, "work-W%d" % n)
    try:
        r = run_counter(work)
        line = [l for l in r.stdout.splitlines() if l.startswith("tip=")]
        receipts = os.path.join(S, "receipts")
        os.makedirs(receipts, exist_ok=True)
        open(os.path.join(receipts, name + ".out"), "w").write(r.stdout)
        open(os.path.join(receipts, name + ".err"), "w").write(r.stderr)
        open(os.path.join(receipts, name + ".mutant.py"), "w").write(body)
        open(os.path.join(receipts, name + ".sha256"), "w").write(hashlib.sha256(body.encode()).hexdigest() + "\n")
        escapes = [l for l in r.stderr.splitlines() if "work" in l.lower()][:3]
        print(f"### {name}  exit={r.returncode}")
        print(line[0] if line else r.stdout.strip())
        if escapes:
            print("stderr:", " | ".join(escapes)[:200])
    finally:
        restore()
        import shutil; shutil.rmtree(work, ignore_errors=True)

restore()
h = hashlib.sha256(open(COUNTER, "rb").read()).hexdigest()
print("restored counter sha:", h[:16], "OK" if h.startswith("c8b725e57f6e7617") else "MISMATCH")
