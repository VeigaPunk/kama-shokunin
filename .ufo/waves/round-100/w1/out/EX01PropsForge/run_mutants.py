#!/usr/bin/env python3
"""Build C2 probe mutants from the frozen M probe and grade them via the counter's public path.
Every mutant = git show M:tools/kama-probe.sh bytes with ONE documented change to router_autoload().
Grading: python3 tools/round100-props-status.py --repo <lane> --rev <M> --probe-file <mutant> --work <scratch>
Claim wording: 'the probe reads the router's bare /props body only on a final HTTP 200'.
A mutant VIOLATING that wording yet exiting 0 = counter blind spot.
"""
import pathlib, shutil, subprocess, sys

LANE = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
REV = "2e27e6f1e6b2514ec8ac5d6344998b3db61e16d6"
M = subprocess.run(["git", "-C", str(LANE), "show", f"{REV}:tools/kama-probe.sh"],
                   capture_output=True, check=True).stdout.decode()
OUT = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-100/w1/out/EX01PropsForge")
SCRATCH = pathlib.Path("/fast/scratch/hyaku/kama-r100/EX01PropsForge")
OUT.mkdir(parents=True, exist_ok=True); SCRATCH.mkdir(parents=True, exist_ok=True)
COUNTER = LANE / "tools/round100-props-status.py"

GATE = '[ "$pcode" = 200 ] || return 2'
assert M.count(GATE) == 1, "frozen gate not unique / not found"

def mk(name, fn):
    m = M.replace(GATE, fn) if fn != "<unchanged>" else M
    assert m != M or fn == "<unchanged>", f"{name}: no-op"
    p = OUT / f"probe-{name}.sh"; p.write_text(m); return p

U = OUT / "probe-unmodified.sh"; U.write_text(M)
print(f"unmodified sha256={__import__('hashlib').sha256(M.encode()).hexdigest()[:12]} git-hash-ok")

# (a) accept any 2xx: 200,201,202,204,... — S5-202 cell must trip it
mk("a-any2xx", 'case "$pcode" in 2??) ;; *) return 2 ;; esac')
# (b) accept <400: includes 202,302,301,... — S5,S6 must trip
mk("b-lt400", 'case "$pcode" in 3??|4??|5??) return 2 ;; esac')
# (c) -L follow redirect: no explicit gate change; S6-302 router-on + Location=/elsewhere must follow
m = M.replace("pcode=$(curl -sS --noproxy '*' --connect-timeout \"$CONNECT_TIMEOUT\" --max-time \"$TIMEOUT\" \\\n    --max-filesize \"$MAX_BODY\" -o \"$pbody\" -w '%{http_code}' \\\n    \"http://127.0.0.1:$port/props\" 2>/dev/null) || return 2",
              "pcode=$(curl -sS --noproxy '*' --connect-timeout \"$CONNECT_TIMEOUT\" --max-time \"$TIMEOUT\" \\\n    --max-filesize \"$MAX_BODY\" -L -o \"$pbody\" -w '%{http_code}' \\\n    \"http://127.0.0.1:$port/props\" 2>/dev/null) || return 2")
assert "-L" in m and m != M
(OUT / "probe-c-followL.sh").write_text(m)
# (d) read status but ignore it when body is a router doc (fall through to body parse on non-200)
mk("d-ignore-if-router", '[ "$pcode" = 200 ] || g(){ python3 -c "import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if d.get(\'role\')==\'router\' else 1)" "$pbody" 2>/dev/null || return 2; }')
# (e) only exclude 500
mk("e-not500", '[ "$pcode" != 500 ] || return 2')
# (f) drop status check entirely (= base behaviour, no gate line)
mk("f-dropped", 'true # status gate dropped')
# (g) treat 000 (transport failure) as 200 — reads an empty/stale body; stub cells all return real codes so cells differ only if body reused... expect GREEN (blind spot) or UNREAD via body-parse
mk("g-000-as-200", '[ "$pcode" = 200 ] || [ "$pcode" = 000 ] || return 2')
# (h) accept 200 or 304 (304 not in cells; must be GREEN blind spot if body-parse of empty 304 body still yields UNREAD)
mk("h-200or304", '[ "$pcode" = 200 ] || [ "$pcode" = 304 ] || return 2')
# (i) EXTRA: accept 200 or 204 — S5-202 is closest 2xx; 204 has no cell, body-parse of 204 body (router-on) would read ON while claim says only 200
mk("i-200or204", '[ "$pcode" = 200 ] || [ "$pcode" = 204 ] || return 2')
# (j) EXTRA: case glob 2* single-char class 2? — matches 202 too but different form; same trap as (a)
mk("j-glob2x", 'case "$pcode" in 2?*) ;; *) return 2 ;; esac')
# (k) EXTRA: integer test -eq 200 (numeric) — Green and wording-equivalent on stub codes, except leading zeros / "200 " untested; record.
mk("k-numeric", '[ "$pcode" -eq 200 ] 2>/dev/null || return 2')
# (l) EXTRA: accept 200 or 302 — S6 must trip (same cells as b)
mk("l-200or302", '[ "$pcode" = 200 ] || [ "$pcode" = 302 ] || return 2')
# (m) EXTRA BLIND-SPOT probe: gate checks 200 but ALSO… no. Instead: gate removed but body re-derived from status line file — out of scope.
# (m') blanket always-unread: always return 2 — P1/P2 must trip (already frozen control c2-mutant-blanket.out)
mk("m-blanket", 'return 2')
# (n) EXTRA: reads body only on 200 UNLESS body is router-on (leaky): return on for router-on under any code
mk("n-leaky-on", '[ "$pcode" = 200 ] || return 2; :')  # placeholder same as M? replaced below
# n real: remove gate, force on when router-on regardless of code
m2 = M.replace(GATE, 'true')
m2 = m2.replace("elif doc.get(\"models_autoload\") is True:\n    print(\"on\")",
                "elif doc.get(\"models_autoload\") is True:\n    print(\"on\")")
(OUT / "probe-n-leaky-on.sh").write_text(m2)  # = base behaviour; S2,S4,S5,S6,P2 distinction poor

mutants = sorted(OUT.glob("probe-*.sh"))
print(f"mutants: {len(mutants)}")
results = []
for mut in mutants:
    name = mut.stem
    work = SCRATCH / f"work-{name}"
    work.mkdir(exist_ok=True)
    p = subprocess.run(["python3", str(COUNTER), "--repo", str(LANE), "--rev", "2e27e6f1",
                        "--probe-file", str(mut), "--work", str(work)],
                       capture_output=True, text=True, timeout=600)
    (OUT / f"{name}.out.txt").write_text(p.stdout + p.stderr + f"exit={p.returncode}\n")
    last = [l for l in p.stdout.splitlines() if l.startswith("ROUTER_PROPS_STATUS100 cells=")]
    print(f"{name}: exit={p.returncode} {last}")
    results.append((name, p.returncode, last))

# verdict table
print("\n=== VERDICT TABLE ===")
for name, rc, last in results:
    print(f"{name:<28} exit={rc}")

# copy receipts into OUT (already there); ensure runner prints summary for grader
siblings = sorted([p.name for p in OUT.glob("*")])
print(f"\nout dir contents ({len(siblings)}):")
for s in siblings: print(f"  {s}")
