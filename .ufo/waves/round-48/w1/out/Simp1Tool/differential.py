import os, subprocess, sys, json
S = os.environ["TMPDIR"]; LANE = os.path.join(S, "lane")
def run(tool, args):
    p = subprocess.run([sys.executable, tool, *args], capture_output=True, text=True, timeout=900)
    return p.returncode, p.stdout, p.stderr
tips = ["380bcdff9c8af06997c482f6eb03db926a794a2b", "b85783e889c261ff870da65d091ff1014ffe7c10",
        "3a09a1d9" , "33e005827742b29772b153cda036ec9f27f653be", "383f1fc7", "b85895f4"]
revs = subprocess.run(["git","-C",LANE,"rev-list","--topo-order","380bcdff9c8af06997c482f6eb03db926a794a2b"],
                      capture_output=True, text=True).stdout.split()
spread = [revs[i] for i in range(0, len(revs), max(1, len(revs)//8))][:8]
rows, bad = [], 0
for tip in tips + spread:
    for extra in (["--json"], []):
        a = run(os.path.join(S,"work/before.py"), ["--repo", LANE, "--to", tip, *extra])
        b = run(os.path.join(S,"work/after.py"),  ["--repo", LANE, "--to", tip, *extra])
        same = a == b
        bad += not same
        rows.append(f"{'same' if same else 'DIFF'} rc={a[0]}/{b[0]} {tip[:12]} {' '.join(extra) or 'text'}"
                    + ("" if same else f" out={a[1][:200]!r} vs {b[1][:200]!r} err={a[2][:120]!r}/{b[2][:120]!r}"))
# explicit-contract and files modes plus the error paths
C = os.path.join(S,"lane","registry","append-only-contract.tsv")
extra_cases = [
  ("contract-file", ["--repo", LANE, "--to", "380bcdff9c8af06997c482f6eb03db926a794a2b", "--contract", C, "--json"]),
  ("files-mode", ["--repo", LANE, "--to", "380bcdff9c8af06997c482f6eb03db926a794a2b", "--files", "SCORECARD.md,LOG.md", "--json"]),
  ("files-text", ["--repo", LANE, "--to", "380bcdff9c8af06997c482f6eb03db926a794a2b", "--files", "SCORECARD.md"]),
  ("bad-threshold", ["--repo", LANE, "--to", "380bcdff", "--threshold", "0"]),
  ("both-modes", ["--repo", LANE, "--to", "380bcdff", "--files", "LOG.md", "--contract", C]),
  ("missing-to", ["--repo", LANE, "--to", "no-such-rev"]),
]
for name, args in extra_cases:
    a = run(os.path.join(S,"work/before.py"), args); b = run(os.path.join(S,"work/after.py"), args)
    same = a == b
    bad += not same
    rows.append(f"{'same' if same else 'DIFF'} rc={a[0]}/{b[0]} {name}"
                + ("" if same else f" {a[1][:200]!r} vs {b[1][:200]!r} err={a[2][:150]!r}/{b[2][:150]!r}"))
print("\n".join(rows))
print(f"\nDIFFERENCES={bad} comparisons={len(rows)}")
sys.exit(1 if bad else 0)
