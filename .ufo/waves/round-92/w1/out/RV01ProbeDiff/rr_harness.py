#!/usr/bin/env python3
"""router_refine harness v2: stubs defined AFTER source; word dump to file."""
import json, os, shlex, subprocess, sys

SC = "/fast/scratch/hyaku/kama-r92/RV01ProbeDiff"

CASES = [
    ("normal",          ["m\tunloaded\t0\t5"], "*", [], "", "missing"),
    ("idx-space",       ["m\tunloaded\t0\t5 6"], "*", [], "", "missing"),
    ("idx-glob-star-dir-empty", ["m\tunloaded\t0\t*"], "*", [], "", "missing"),
    ("idx-glob-star-dir-files", ["m\tunloaded\t0\t*"], "*", ["a", "b", "ax"], "", "missing"),
    ("idx-glob-class-match",    ["m\tunloaded\t0\t[a-z]"], "*", ["a", "b"], "", "missing"),
    ("idx-glob-class-nomatch",  ["m\tunloaded\t0\t[a-z]"], "*", [], "", "missing"),
    ("idx-glob-qmatch",  ["m\tunloaded\t0\t?x"], "*", ["ax", "b"], "", "missing"),
    ("idx-glob-trail",   ["m\tunloaded\t0\tx*"], "*", ["xy", "z"], "", "missing"),
    ("idx-empty-3field", ["m\tunloaded\t0"], "*", [], "", "missing"),
    ("idx-empty-4field", ["m\tunloaded\t0\t"], "*", [], "", "missing"),
    ("idx-dash-n",       ["m\tunloaded\t0\t-n"], "*", [], "", "missing"),
    ("idx-dash-dash",    ["m\tunloaded\t0\t--"], "*", [], "", "missing"),
    ("two-entries",      ["m1\tunloaded\t0\t5", "m2\tunloaded\t0\t6"], "*", [], "", "missing"),
    ("space-glob-space", ["m\tunloaded\t0\t5 * 6"], "*", ["aa"], "", "missing"),
    ("star-star",        ["m1\tunloaded\t0\t*", "m2\tunloaded\t0\t*"], "*", ["aa", "bb"], "", "missing"),
    ("failed-1",         ["m\tunloaded\t1\t5"], "*", [], "", "missing"),
    ("failed-empty",     ["m\tunloaded\t\t5"], "*", [], "", "missing"),
    ("status-tab-in-id", ["m\tx\tunloaded\t0\t7"], "*", [], "", "missing"),
    ("fs-dash-mode",     ["m\tunloaded\t0\t5"], "*", [], "", "dash"),
    ("fs-empty-mode",    ["m\tunloaded\t0\t5"], "*", [], "", "empty"),
    ("loaded-only",      ["m\tloaded\t0\t5"], "*", [], "", "missing"),
    ("sleeping",         ["m\tsleeping\t0\t5"], "*", [], "", "missing"),
    ("loading",          ["m\tloading\t0\t5"], "*", [], "", "missing"),
    ("mixed-ok",         ["m1\tunloaded\t0\t5", "m2\tloaded\t0\t6"], "*", [], "", "missing"),
    ("status-dash",      ["m\t-\t0\t5"], "*", [], "", "missing"),
    ("nonwild-match",    ["m\tunloaded\t0\t5"], "dir/m.gguf", [], "", "missing"),
    ("nonwild-nomatch",  ["zz\tunloaded\t0\t5"], "dir/m.gguf", [], "", "missing"),
    ("idx-space-ifs-colon", ["m\tunloaded\t0\t5 6"], "*", [], ":", "missing"),
    ("idx-glob-ifs-colon",  ["m\tunloaded\t0\t*"], "*", ["a", "b"], ":", "missing"),
    ("idx-space-ifs-vert",  ["m\tunloaded\t0\t5 6"], "*", [], "|", "missing"),
    ("idx-space-ifs-spc",   ["m\tunloaded\t0\t5 6"], "*", [], " ", "missing"),
    ("idx-nl-in-id",     ["m\tunloaded\t0\t5\n6"], "*", [], "", "missing"),
    ("many-entries",     [f"m{i}\tunloaded\t0\t{i}" for i in range(50)], "*", [], "", "missing"),
    ("unloadable-verdict", ["m\tunloaded\t0\t5"], "*", [], "", "missing"),
]

STUB = r'''
router_entries() { printf '%s\n' "$KAMA_CANNED"; }
router_autoload() { return 0; }
router_file_states() {
  local body=$1; shift
  { printf 'NARGS=%d\n' "$#"
    local a
    for a in "$@"; do printf 'ARG=%s\n' "$(printf '%s' "$a" | od -An -tx1 | tr -d ' \n')"; done
  } >> "$KAMA_DUMP"
  case "$KAMA_FSMODE" in
    missing) for a in "$@"; do printf '%s\tmissing\n' "$a"; done ;;
    dash)    for a in "$@"; do printf '%s\t-\n' "$a"; done ;;
    empty)   : ;;
  esac
}
'''

def run(rev, canned, exp, files, ifs, fsmode, tag):
    wd = f"{SC}/rr2/{rev}.{tag}"
    os.makedirs(wd, exist_ok=True)
    for f in files:
        open(os.path.join(wd, f), "w").write("x")
    dump = f"{wd}/dump.txt"
    if os.path.exists(dump):
        os.remove(dump)
    env = dict(os.environ)
    env.pop("LANG", None); env.pop("LC_ALL", None)
    env["KAMA_CANNED"] = "\n".join(canned)
    env["KAMA_FSMODE"] = fsmode
    env["KAMA_DUMP"] = dump
    if ifs:
        env["KAMA_IFS"] = ifs
    else:
        env.pop("KAMA_IFS", None)
    script = f'''
source {SC}/h{rev}.sh
cd {wd}
{STUB}
if [ -n "${{KAMA_IFS:-}}" ]; then IFS=$KAMA_IFS; fi
router_refine bodyfile {shlex.quote(exp)} 9999 >/dev/null 2>&1 || echo "REFINE_RC=$?"
echo "V=$RT_VERDICT R=$RT_REASON"
'''
    p = subprocess.run(["bash", "-c", script], env=env, capture_output=True, text=True, cwd=wd)
    dump_txt = open(dump).read() if os.path.exists(dump) else "<no dump: file_states never called>"
    return p.stdout, dump_txt, p.stderr

diffs = 0
rows = []
for name, canned, exp, files, ifs, fsmode in CASES:
    b_out, b_dump, b_err = run("B", canned, exp, files, ifs, fsmode, name)
    m_out, m_dump, m_err = run("M2", canned, exp, files, ifs, fsmode, name)
    same = (b_out == m_out) and (b_dump == m_dump)
    tag = "SAME" if same else "DIFF"
    if not same:
        diffs += 1
    rows.append((tag, name, b_out, b_dump, m_out, m_dump))
    if same:
        v = b_out.strip().replace("\n", " ")
        nargs = b_dump.splitlines()[0] if b_dump.startswith("NARGS") else b_dump.strip()
        print(f"[{tag}] {name} fs={fsmode} ifs='{ifs}' | {nargs} | {v}")
    else:
        print(f"[{tag}] {name} fs={fsmode} ifs='{ifs}' files={files}")
        print(f"  base out: {b_out!r}\n  base dump: {b_dump!r}")
        print(f"  m2   out: {m_out!r}\n  m2   dump: {m_dump!r}")
print(f"\nrouter_refine cases: {len(CASES)}, diffs: {diffs}")
with open(f"{SC}/rr_results.txt", "w") as f:
    for tag, name, b, bd, m, md in rows:
        f.write(f"[{tag}] {name}\nbase : {b!r} dump={bd!r}\nm2   : {m!r} dump={md!r}\n\n")
