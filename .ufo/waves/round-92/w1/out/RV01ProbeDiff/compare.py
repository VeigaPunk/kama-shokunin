#!/usr/bin/env python3
"""Compare base vs M2 outputs byte-for-byte over the generated corpus."""
import json, subprocess, sys, os

SC = "/fast/scratch/hyaku/kama-r92/RV01ProbeDiff"
with open(f"{SC}/cases.json") as f:
    cases = json.load(f)

def run_rev(rev, loc, fn):
    """Run all cases of fn under h{rev} in one bash process; return (outs, rcs, err)."""
    cmd = ["bash", "-c", f'''
rev={rev!r}; loc={loc!r}; fn={fn!r}
source {SC}/h{rev}.sh
source {SC}/cases_{fn}.bash
i=0
for c in "${{CASES[@]}}"; do
  rc=0; case "$fn" in jstr) jstr "$c" ;; sp) served_persist "$c" ;; esac > "{SC}/run.$rev.$loc.$fn.$i" 2> "{SC}/run.$rev.$loc.$fn.$i.err" || rc=$?
  echo "$rc" > "{SC}/run.$rev.$loc.$fn.$i.rc"
  i=$((i+1))
done
echo "n=$i" > "{SC}/run.$rev.$loc.$fn.count"
''']
    env = dict(os.environ)
    env.pop("LANG", None); env.pop("LC_ALL", None); env.pop("LC_CTYPE", None)
    if loc != "NONE":
        env["LC_ALL"] = loc
    p = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if p.returncode != 0:
        print(f"FATAL rev={rev} loc={loc} fn={fn}: {p.stderr[:500]}", file=sys.stderr)
        sys.exit(1)
    n = int(open(f"{SC}/run.$rev.$loc.$fn.count".replace("$", "")).read().split("=")[1]) if False else None
    n = int(open(f"{SC}/run.{rev}.{loc}.{fn}.count").read().split("=")[1])
    outs, rcs, errs = [], [], []
    for i in range(n):
        outs.append(open(f"{SC}/run.{rev}.{loc}.{fn}.{i}", "rb").read())
        rcs.append(int(open(f"{SC}/run.{rev}.{loc}.{fn}.{i}.rc").read()))
        e = open(f"{SC}/run.{rev}.{loc}.{fn}.{i}.err", "rb").read()
        errs.append(e)
    return outs, rcs, errs

mismatches = []
for fn in ("jstr", "sp"):
    for loc in ("C", "en_US.UTF-8", "NONE"):
        b_out, b_rc, b_err = run_rev("B", loc, fn)
        m_out, m_rc, m_err = run_rev("M2", loc, fn)
        assert len(b_out) == len(m_out) == len(cases[fn])
        for i, (b, m) in enumerate(zip(zip(b_out, b_rc, b_err), zip(m_out, m_rc, m_err))):
            if b != m:
                mismatches.append({
                    "fn": fn, "loc": loc, "case": i,
                    "input": bytes(cases[fn][i]),
                    "base_out": b[0], "base_rc": b[1], "base_err": b[2],
                    "m2_out": m[0], "m2_rc": m[1], "m2_err": m[2],
                })
print(f"total comparisons: {sum(len(c) for c in cases.values()) * 3}")
print(f"mismatches: {len(mismatches)}")
for mm in mismatches:
    def x(bs, cap=160):
        return bs[:cap].hex(" ") + (" ..." if len(bs) > cap else "")
    print("=" * 70)
    print(f"fn={mm['fn']} loc={mm['loc']} case#{mm['case']}")
    print(f"  input({len(mm['input'])}B): {mm['input'][:80].hex(' ')}")
    print(f"  base rc={mm['base_rc']} out({len(mm['base_out'])}B): {x(mm['base_out'])}")
    if mm["base_err"]: print(f"  base err: {mm['base_err'][:200]}")
    print(f"  m2   rc={mm['m2_rc']} out({len(mm['m2_out'])}B): {x(mm['m2_out'])}")
    if mm["m2_err"]: print(f"  m2 err: {mm['m2_err'][:200]}")
with open(f"{SC}/mismatches.json", "w") as f:
    json.dump(mismatches, f, default=bytes)
