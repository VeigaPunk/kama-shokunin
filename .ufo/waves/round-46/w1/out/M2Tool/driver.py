#!/usr/bin/env python3
"""M2Tool C2 mutation driver: mutate tools/append-only-audit.py, run --selftest +
frozen counter legs on a fixture clone of the lane at 4a2a4d5."""
import os
import re
import subprocess
import sys

S = "/fast/scratch/hyaku/kama-r46/M2Tool"
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FIX = os.path.join(S, "fixture")
FROZEN = "4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050"
COUNTER = os.path.join(LANE, "tools", "round46-append-audit-check.py")
IDENT = ["-c", "user.name=aoa-fixture", "-c", "user.email=aoa-fixture@invalid", "-c", "commit.gpgsign=false"]

pristine = open(os.path.join(S, "pristine.py")).read()

# (id, family, [(old, new), ...])
MUTANTS = [
    ("M01", "threshold-cmp", [('            if len(dele) < threshold:', '            if len(dele) <= threshold:')]),
    ("M02", "threshold-cmp", [('            if len(dele) < threshold:', '            if len(dele) < threshold + 1:')]),
    ("M03", "threshold-default", [('    ap.add_argument("--threshold", type=int, default=20)', '    ap.add_argument("--threshold", type=int, default=21)')]),
    ("M04", "threshold-validation", [('''    if a.threshold < 1:
        print("could-not-evaluate: --threshold must be >= 1", file=sys.stderr)
        return 2
''', '')]),
    ("M05", "header-exclusion", [('if x.startswith("-") and not x.startswith("---")]', 'if x.startswith("-")]')]),
    ("M06", "header-exclusion", [('and not x.startswith("---")]', 'and not x.startswith("----")]')]),
    ("M07", "deletion-text", [('dele = [x[1:] for x in d.split("\\n")', 'dele = [x for x in d.split("\\n")')]),
    ("M08", "first-parent", [('parents[parts[0]] = parts[1] if len(parts) > 1 else None', 'parents[parts[0]] = parts[-1] if len(parts) > 1 else None')]),
    ("M09", "root-commit", [('        if p is None:\n            continue\n', '        if p is None:\n            pass\n')]),
    ("M10", "first-parent-all-parents", [
        ('    parents = {}\n', '    parents = {}\n    allpars = {}\n'),
        ('            parents[parts[0]] = parts[1] if len(parts) > 1 else None',
         '            parents[parts[0]] = parts[1] if len(parts) > 1 else None\n            allpars[parts[0]] = parts[1:] or []'),
        ('            d = _git(repo_path, "diff", "--no-renames", "--no-color", "--no-ext-diff", "-U0", p, c, "--", f)',
         '            d = "".join(_git(repo_path, "diff", "--no-renames", "--no-color", "--no-ext-diff", "-U0", p2, c, "--", f) for p2 in (allpars.get(c) or [p]))'),
    ]),
    ("M10b", "first-parent-all-parents-strong", [
        ('    parents = {}\n', '    parents = {}\n    allpars = {}\n'),
        ('            parents[parts[0]] = parts[1] if len(parts) > 1 else None',
         '            parents[parts[0]] = parts[1] if len(parts) > 1 else None\n            allpars[parts[0]] = parts[1:] or []'),
        ('        changed = set(_git(repo_path, "diff", "--no-renames", "--name-only", p, c, "--", *files).split("\\n")) - {""}',
         '        changed = set("".join(_git(repo_path, "diff", "--no-renames", "--name-only", p2, c, "--", *files) for p2 in (allpars.get(c) or [p])).split("\\n")) - {""}'),
        ('            d = _git(repo_path, "diff", "--no-renames", "--no-color", "--no-ext-diff", "-U0", p, c, "--", f)',
         '            d = "".join(_git(repo_path, "diff", "--no-renames", "--no-color", "--no-ext-diff", "-U0", p2, c, "--", f) for p2 in (allpars.get(c) or [p]))'),
    ]),
    ("M11", "set-vs-multiset", [('            need = set(dele)', '            need = list(dele)')]),
    ("M12", "set-vs-multiset", [('            k = sum(1 for x in dele if x in tip_lines)', '            k = len({x for x in dele if x in tip_lines})')]),
    ("M13", "set-vs-multiset", [('self._blob_lines[blob] = frozenset(_git(self.path, "cat-file", "blob", blob).split("\\n"))', 'self._blob_lines[blob] = _git(self.path, "cat-file", "blob", blob).split("\\n")')]),
    ("M14", "restored-by-start", [('            later = commits[i + 1:]', '            later = commits[i:]')]),
    ("M15", "restored-by-start", [('            later = commits[i + 1:]', '            later = commits[i + 2:]')]),
    ("M16", "restored-by-order", [('            for c2 in later:', '            for c2 in reversed(later):')]),
    ("M17", "restored-by-start", [('            later = commits[i + 1:]', '            later = []')]),
    ("M18", "restored-by-last", [('                    rb = c2\n                    break\n', '                    rb = c2\n')]),
    ("M19", "restored-by-any", [('                if need <= r.lines(later_blobs[f"{c2}:{f}"]):', '                if need & r.lines(later_blobs[f"{c2}:{f}"]):')]),
    ("M20", "status-labels", [('status = "restored" if k == len(dele) else ("unrestored" if k == 0 else "partial")', 'status = "unrestored" if k == len(dele) else ("restored" if k == 0 else "partial")')]),
    ("M21", "status-threshold", [('status = "restored" if k == len(dele) else ("unrestored" if k == 0 else "partial")', 'status = "restored" if k > 0 else "unrestored"')]),
    ("M22", "status-threshold", [('status = "restored" if k == len(dele) else ("unrestored" if k == 0 else "partial")', 'status = "restored" if k == len(dele) else ("unrestored" if k < len(dele) else "partial")')]),
    ("M23", "summary-counts", [('"partial": sum(e["status"] == "partial" for e in events)', '"partial": sum(e["status"] != "restored" for e in events)')]),
    ("M24", "exit-code", [('    return 1 if s["partial"] or s["unrestored"] else 0', '    return 1 if s["events"] else 0')]),
    ("M25", "exit-code", [('    return 1 if s["partial"] or s["unrestored"] else 0', '    return 1 if s["unrestored"] else 0')]),
    ("M26", "exit-code", [('    return 1 if s["partial"] or s["unrestored"] else 0', '    return 1 if s["partial"] and s["unrestored"] else 0')]),
    ("M27", "exit-code", [('    return 1 if s["partial"] or s["unrestored"] else 0', '    return 0')]),
    ("M28", "rename-both", [
        ('changed = set(_git(repo_path, "diff", "--no-renames", "--name-only", p, c, "--", *files).split("\\n")) - {""}',
         'changed = set(_git(repo_path, "diff", "--name-only", p, c, "--", *files).split("\\n")) - {""}'),
        ('            d = _git(repo_path, "diff", "--no-renames", "--no-color", "--no-ext-diff", "-U0", p, c, "--", f)',
         '            d = _git(repo_path, "diff", "--no-color", "--no-ext-diff", "-U0", p, c, "--", f)'),
    ]),
    ("M29", "rename-prefilter", [('changed = set(_git(repo_path, "diff", "--no-renames", "--name-only", p, c, "--", *files).split("\\n")) - {""}',
                                  'changed = set(_git(repo_path, "diff", "--name-only", p, c, "--", *files).split("\\n")) - {""}')]),
    ("M30", "rename-udiff", [('            d = _git(repo_path, "diff", "--no-renames", "--no-color", "--no-ext-diff", "-U0", p, c, "--", f)',
                              '            d = _git(repo_path, "diff", "--no-color", "--no-ext-diff", "-U0", p, c, "--", f)')]),
    ("M31", "catfile-type-check", [('res[spec] = parts[0] if len(parts) == 2 and parts[1] == "blob" else None',
                                    'res[spec] = parts[0] if len(parts) == 2 else None')]),
    ("M32", "catfile-zip", [('for spec, line in zip(specs, out.split("\\n")):', 'for spec, line in zip(specs, out.split("\\n")[1:]):')]),
    ("M33", "catfile-type-invert", [('parts[0] if len(parts) == 2 and parts[1] == "blob" else None',
                                     'parts[0] if len(parts) == 2 and parts[1] != "blob" else None')]),
    ("M34", "catfile-field", [('res[spec] = parts[0] if len(parts) == 2 and parts[1] == "blob" else None',
                               'res[spec] = parts[1] if len(parts) == 2 and parts[1] == "blob" else None')]),
    ("M35", "catfile-lines-split", [('frozenset(_git(self.path, "cat-file", "blob", blob).split("\\n"))',
                                     'frozenset(_git(self.path, "cat-file", "blob", blob).split())')]),
    ("M36", "revlist-reverse", [('"rev-list", "--topo-order", "--reverse", to_full).split()', '"rev-list", "--topo-order", to_full).split()')]),
    ("M37", "revlist-topo", [('"rev-list", "--topo-order", "--reverse", to_full).split()', '"rev-list", "--reverse", to_full).split()')]),
    ("M38", "name-status", [('"diff", "--no-renames", "--name-only", p, c, "--", *files', '"diff", "--no-renames", "--name-status", p, c, "--", *files')]),
]


def run(cmd, env=None, timeout=600):
    e = dict(os.environ)
    if env:
        e.update(env)
    p = subprocess.run(cmd, capture_output=True, text=True, env=e, timeout=timeout)
    return p.returncode, p.stdout, p.stderr


def git(*args, check=True):
    p = subprocess.run(["git", "-C", FIX, *args], capture_output=True, text=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.strip()[:300]}")
    return p.stdout


def main():
    tsv = open(os.path.join(S, "results.tsv"), "w")
    tsv.write("id\tfamily\tbuild\tdirect_selftest_rc\tdirect_selftest_line\tcounter_rc\tlegs\tmet\tverdict\n")
    for mid, family, pairs in MUTANTS:
        body = pristine
        build = "ok"
        for old, new in pairs:
            n = body.count(old)
            if n != 1:
                build = f"BAD-ANCHOR(n={n}): {old[:60]!r}"
                break
            body = body.replace(old, new)
        mut_path = os.path.join(S, "mut", f"{mid}.py")
        with open(mut_path, "w") as fh:
            fh.write(body)
        if build != "ok":
            tsv.write(f"{mid}\t{family}\t{build}\t-\t-\t-\t-\t-\tskipped\n")
            tsv.flush()
            print(f"{mid} {build}", flush=True)
            continue

        # 1. direct selftest
        rc1, out1, err1 = run([sys.executable, mut_path, "--selftest", "--scratch", os.path.join(S, "st")],
                              env={"TMPDIR": os.path.join(S, "st")})
        m = re.search(r"AOA_SELFTEST pass=(\d+) fail=(\d+)", out1)
        st_line = m.group(0) if m else f"no-line rc={rc1} err={err1.strip()[:80]!r}"
        with open(os.path.join(S, "logs", f"{mid}-selftest.txt"), "w") as fh:
            fh.write(out1 + "\n--stderr--\n" + err1)

        # 2. commit mutant into fixture at frozen tip
        git("checkout", "-q", "--detach", FROZEN)
        top = git("rev-parse", "--show-toplevel").strip()
        assert os.path.realpath(top) == os.path.realpath(FIX), f"toplevel {top} != {FIX}"
        with open(os.path.join(FIX, "tools", "append-only-audit.py"), "w") as fh:
            fh.write(body)
        git("add", "tools/append-only-audit.py")
        git(*IDENT, "commit", "-q", "-m", f"mutant {mid} {family}")
        tip = git("rev-parse", "HEAD").strip()
        par = git("rev-parse", "HEAD^").strip()
        assert tip != FROZEN and par == FROZEN

        # 3. frozen counter
        rc2, out2, err2 = run([sys.executable, COUNTER, "--repo", FIX, "--tip", tip,
                               "--scratch", os.path.join(S, "ctr")],
                              env={"TMPDIR": os.path.join(S, "ctr")})
        with open(os.path.join(S, "logs", f"{mid}-counter.txt"), "w") as fh:
            fh.write(f"tip={tip} rc={rc2}\n" + out2 + "\n--stderr--\n" + err2)
        lm = re.search(r"selftest=(\d) fixture=(\d) lane=(\d) table=(\d) lane_events=(\d+) "
                       r"lane_unrestored=(\d+) lane_partial=(\d+) met=(\w+)", out2)
        if lm:
            stl, fx, ln, tb, ev, unr, parn, met = lm.groups()
            legs = f"selftest={stl} fixture={fx} lane={ln} table={tb}"
        else:
            legs, met = f"NO-LINE rc={rc2} err={err2.strip()[:120]!r}", "-"

        # 4. verdict on legs (table is constant 0 at the frozen tip, baseline included)
        if build != "ok":
            verdict = "skipped"
        elif rc1 != 0 or (m and int(m.group(2)) > 0) or "fail=0" not in st_line:
            verdict = "killed-by-selftest"
        elif lm and (stl == "0"):
            verdict = "killed-by-selftest"
        elif lm and (fx == "0" or ln == "0"):
            verdict = "killed-by-counter"
        elif lm and stl == "1" and fx == "1" and ln == "1":
            verdict = "survived"
        else:
            verdict = "inconclusive"

        tsv.write(f"{mid}\t{family}\t{build}\t{rc1}\t{st_line}\t{rc2}\t{legs}\t{met}\t{verdict}\n")
        tsv.flush()
        print(f"{mid}\t{verdict}\t{st_line}\t{legs}", flush=True)
    tsv.close()
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
