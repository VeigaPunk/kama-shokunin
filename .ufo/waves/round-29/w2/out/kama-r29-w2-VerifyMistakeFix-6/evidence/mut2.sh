#!/bin/bash
# Subprocess-based confirmation that the committed-tip tool still lets the
# plain-space mutant survive, and the working-tree tool kills it.
set -u
BASE=/tmp/kama-w2-VerifyMistakeFix
COMMITTED=$BASE/clone/tools/prereg-time-check.py
WTREE=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/prereg-time-check.py
SCRATCH=$BASE/scratch_subproc
mkdir -p "$SCRATCH" "$BASE/mut2"

python3 - "$COMMITTED" "$WTREE" "$BASE" <<'EOF'
import pathlib, sys
com = pathlib.Path(sys.argv[1]).read_text()
wt  = pathlib.Path(sys.argv[2]).read_text()
BASE = sys.argv[3]
TIME_RE = 'TIME_RE = re.compile(r"\\d{4}-\\d{2}-\\d{2}(?:T| ~| )\\d{2}:\\d{2}(?::\\d{2})?Z")'
PARSE   = '    m = re.fullmatch(r"(\\d{4})-(\\d{2})-(\\d{2})(?:T| ~| )(\\d{2}):(\\d{2})(?::(\\d{2}))?Z", text)'
SECS    = "    y, mo, d, h, mi, s = (int(g) if g else 0 for g in m.groups())"

def w(path, src):
    pathlib.Path(path).write_text(src)

def m02(src):
    new = TIME_RE.replace("(?:T| ~| )", "(?:T| ~)")
    assert TIME_RE in src and new != TIME_RE
    return src.replace(TIME_RE, new)

def m07s(src):
    assert SECS in src
    return src.replace(SECS,
        "    y, mo, d, h, mi, _s = (int(g) if g else 0 for g in m.groups())\n    s = 0")

for tag, fn in (("m02", m02), ("m07s", m07s)):
    w(f"{BASE}/mut2/{tag}-committed.py", fn(com))
    w(f"{BASE}/mut2/{tag}-wtree.py",   fn(wt))
print("mutants written")
EOF

for m in m02 m07s; do
  for v in committed wtree; do
    out=$(python3 "$BASE/mut2/$m-$v.py" --selftest --scratch "$SCRATCH" 2>&1) && rc=0 || rc=$?
    np=$(echo "$out" | grep -c '^\[PASS\]')
    nf=$(echo "$out" | grep -c '^\[FAIL\]')
    verdict=$([ "$rc" != "0" ] && echo KILLED || echo SURVIVED)
    echo "mutant=$m base=$v selftest_exit=$rc PASS=$np FAIL=$nf verdict=$verdict"
    echo "$out" | grep '^\[FAIL\]' | sed 's/^/    /'
  done
done
echo "SUBPROC_MUTANTS_DONE"
