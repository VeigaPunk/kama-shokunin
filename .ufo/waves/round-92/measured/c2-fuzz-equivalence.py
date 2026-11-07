import random, subprocess, sys, os
random.seed(int(os.environ.get("SEED","92")))
alpha = ["\udcff","\udc85","\udcc3",'a','b','/','.gguf','\\','"','\t','\n','\r','\x01','\x1b','\x1f','\x7f',',',' ','é','ж','\u0085','\xff','-','*','%s','%','$','`']
cases = ["", "-", "a", ",", "a,", "a,,", ",a", "c/", ".gguf", "x.gguf.gguf", "/m/a.gguf,b.gguf.gguf,c/", "a\nb,c", "t\tz,q\rr"]
for _ in range(3000):
    cases.append("".join(random.choice(alpha) for _ in range(random.randint(0, 25))))
def run(lib, fn):
    script = f'source {lib}; set +e; while IFS= read -r -d "" x; do {fn} "$x"; printf "\\0"; done'
    data = b"".join(c.encode('utf-8','surrogateescape') + b"\0" for c in cases)
    p = subprocess.run(["bash", "-c", script], input=data, capture_output=True)
    return p.stdout.split(b"\0")
bad = 0
for fn in ("jstr", "served_persist"):
    a = run("lib-base.sh", fn); b = run("lib-new.sh", fn)
    diff = [(cases[i], a[i], b[i]) for i in range(len(cases)) if a[i] != b[i]]
    print(fn, "cases", len(cases), "diffs", len(diff), "lens", len(a), len(b))
    for d in diff[:5]: print("  ", repr(d))
    bad += len(diff)
sys.exit(1 if bad else 0)
