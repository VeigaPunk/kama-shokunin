#!/usr/bin/env python3
"""Generate round-92 C2 single-point mutants of tools/kama-probe.sh at M2 and run the
three assigned detectors (frozen counter, snapshot suite, verdict matrix) on each.

Writes mutants + logs under the seat scratch dir; summary JSON on stdout.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
M2 = "fa8aedb73d18448383c7a4d75405aba448fe8e38"
SCRATCH = Path("/fast/scratch/hyaku/kama-r92/MT01ProbeMutants")
COUNTER = LANE / "tools/round92-linear-paths.py"
SNAP = LANE / "tools/test-snapshot.sh"
CHECK = LANE / "tests/probe-verdicts/check.py"

MUTANTS = [
    # ---- jstr fast path / LC_ALL
    ("fp_drop_backslash",
     r"""  if [[ $s != *[\\\"$'\x01'-$'\x1f'$'\x7f']* ]]; then""",
     r"""  if [[ $s != *[\"$'\x01'-$'\x1f'$'\x7f']* ]]; then""",
     "backslash no longer forces the escaping path"),
    ("fp_drop_quote",
     r"""  if [[ $s != *[\\\"$'\x01'-$'\x1f'$'\x7f']* ]]; then""",
     r"""  if [[ $s != *[\\$'\x01'-$'\x1f'$'\x7f']* ]]; then""",
     "double quote no longer forces the escaping path"),
    ("lc_local_jstr",
     """  local s=${1-} LC_ALL=C""",
     """  local s=${1-}""",
     "jstr's shell-side locale pin removed"),
    ("lc_awk_jstr",
     """  printf '%s\\n' "$s" | LC_ALL=C awk "$AWK_JSTR\"""",
     """  printf '%s\\n' "$s" | awk "$AWK_JSTR\"""",
     "jstr's awk locale pin removed"),
    # ---- AWK_JSTR body
    ("jstr_split_quote_only",
     """{ n = split($0, b, "\\\\"); quotes(b[1]);""",
     """{ n = split($0, b, "\\""); quotes(b[1]);""",
     "record split no longer splits on backslash"),
    ("jstr_quote_unescaped",
     """  for (j = 2; j <= n; j++) { printf "%s", "\\\\\\""; piece(q[j]) }""",
     """  for (j = 2; j <= n; j++) { printf "%s", "\\""; piece(q[j]) }""",
     "quote backslash dropped from the emitted escape"),
    ("jstr_del_map_wrong",
     """  C[sprintf("%c", 127)] = "\\\\u007f";""",
     """  C[sprintf("%c", 127)] = "\\\\u00ff";""",
     "DEL escapes as u00ff"),
    ("jstr_tab_map_dropped",
     """C["\\t"] = "\\\\t"; """,
     """""",
     "TAB mapping removed from C"),
    ("jstr_nr_join_space",
     """NR > 1 { printf "%s", "\\\\n" }""",
     """NR > 1 { printf "%s", " " }""",
     "record joiner emits a space instead of \\n"),
    # ---- router_refine cand array
    ("cand_quoted",
     """cand+=($idx); ncand=$((ncand + 1))""",
     """cand+=("$idx"); ncand=$((ncand + 1))""",
     "candidate index quoted (word-splitting semantics changed)"),
    ("ncand_const1",
     """cand+=($idx); ncand=$((ncand + 1))""",
     """cand+=($idx); ncand=1""",
     "candidate count pinned at 1"),
    ("cand_failed_filter",
     """if [ "$val" = unloaded ] && [ "$failed" != 1 ]; then""",
     """if [ "$val" = unloaded ]; then""",
     "failed unloaded entries collected as autoload candidates"),
    ("nbad_le",
     """if [ "$nbad" -lt "$ncand" ]; then unloaded=1; fi""",
     """if [ "$nbad" -le "$ncand" ]; then unloaded=1; fi""",
     "all-candidates-bad still counts as loadable"),
    # ---- served_persist awk
    ("persist_trail_comma_off",
     """{ n = split($0, p, ","); if (n > 0 && substr($0, length($0)) == ",") n--""",
     """{ n = split($0, p, ","); if (0) n--""",
     "trailing empty field no longer dropped"),
    ("persist_empty_dash_off",
     """(v == "" ? "-" : v)""",
     """(v)""",
     "empty normalised id persists as empty, not -"),
    ("persist_n0_off",
     """      if (n == 0) printf "-" }'""",
     """      if (0) printf "-" }'""",
     "zero-field record prints nothing"),
    ("persist_nr_exit_off",
     """    NR > 1 { exit }""",
     """    NR > 1 { }""",
     "only the first record is honoured -> exit removed"),
    ("persist_tabcr_delete",
     """gsub(/[\\t\\r]/, " ", v)""",
     """gsub(/[\\t\\r]/, "", v)""",
     "TAB/CR deleted instead of replaced by a space"),
    ("persist_ctl_nul_only",
     """gsub(/[\\001-\\037\\177]/, "", v)""",
     """gsub(/\\000/, "", v)""",
     "only NUL deleted; other controls kept"),
]


def run(cmd, env, timeout=900, cwd=None):
    t0 = time.monotonic()
    p = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=timeout, cwd=cwd)
    return p.returncode, p.stdout, p.stderr, time.monotonic() - t0


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def metrics(name, out):
    m = {}
    if name == "counter":
        mm = re.search(r"LINEAR_PATHS cells=(\d+) mismatches=(\d+) positive_mismatches=(\d+).*probe=(\w+)", out)
        if mm:
            m = dict(cells=int(mm.group(1)), mismatches=int(mm.group(2)),
                     positive=int(mm.group(3)), mode=mm.group(4))
        fails = [l for l in out.splitlines() if "ok=0" in l]
        m["failed_cells"] = [l.split()[1] for l in fails]
    elif name == "snapshot":
        mm = re.search(r"RESULT pass=(\d+) fail=(\d+)", out)
        if mm:
            m = dict(pass_=int(mm.group(1)), fail=int(mm.group(2)))
        m["failed_lines"] = [l for l in out.splitlines() if l.startswith("FAIL")][:20]
    elif name == "check":
        mm = re.search(r"tests=(\d+) passes=(\d+) failures=(\d+)", out)
        if mm:
            m = dict(tests=int(mm.group(1)), passes=int(mm.group(2)), failures=int(mm.group(3)))
        m["failed_tests"] = [l.split()[1] if len(l.split()) > 1 else l
                             for l in out.splitlines() if l.startswith("[FAIL]")][:20]
    return m


def main() -> int:
    src = SCRATCH / "M2-probe.sh"
    data = src.read_text()
    outroot = SCRATCH / "run"
    (outroot / "mutants").mkdir(parents=True, exist_ok=True)
    (outroot / "logs").mkdir(parents=True, exist_ok=True)
    built = []
    for name, old, new, desc in MUTANTS:
        n = data.count(old)
        if n != 1:
            print(f"ABORT {name}: pattern count {n} (expected 1)", file=sys.stderr)
            return 2
        mbytes = data.replace(old, new, 1)
        if mbytes == data:
            print(f"ABORT {name}: replacement is a no-op", file=sys.stderr)
            return 2
        p = outroot / "mutants" / f"{name}.sh"
        p.write_text(mbytes)
        built.append(dict(name=name, desc=desc, path=str(p), sha=sha(mbytes.encode()),
                          bytes=len(mbytes)))
        print(f"BUILT {name} sha={sha(mbytes.encode())[:16]}", flush=True)

    def one(m):
        name = m["name"]
        logd = outroot / "logs" / name
        logd.mkdir(parents=True, exist_ok=True)
        mw = logd / "work"
        (mw / "tmp").mkdir(parents=True, exist_ok=True)
        env = dict(os.environ, TMPDIR=str(mw / "tmp"))
        env.pop("KAMA_PROBE", None)
        res = {}
        rc, so, se, dt = run([sys.executable, str(COUNTER), "--repo", str(LANE), "--rev", M2,
                              "--work", str(mw / "counter"), "--probe-file", m["path"]], env)
        (logd / "counter.out").write_text(so + se)
        res["counter"] = dict(rc=rc, seconds=round(dt, 2), **metrics("counter", so))
        env2 = dict(env, KAMA_PROBE=m["path"])
        rc, so, se, dt = run(["bash", str(SNAP)], env2)
        (logd / "snapshot.out").write_text(so + se)
        res["snapshot"] = dict(rc=rc, seconds=round(dt, 2), **metrics("snapshot", so))
        rc, so, se, dt = run([sys.executable, str(CHECK), "--probe", m["path"]], env)
        (logd / "check.out").write_text(so + se)
        res["check"] = dict(rc=rc, seconds=round(dt, 2), **metrics("check", so))
        res["name"] = name
        (logd / "summary.json").write_text(json.dumps(res, indent=2))
        print(f"DONE {name} counter_rc={res['counter']['rc']} snap_rc={res['snapshot']['rc']} "
              f"check_rc={res['check']['rc']}", flush=True)
        return res

    results = []
    with ThreadPoolExecutor(max_workers=int(os.environ.get("MUT_WORKERS", "3"))) as ex:
        for r in ex.map(one, built):
            results.append(r)

    verdicts = []
    for r, m in zip(results, built):
        c, s, k = r["counter"], r["snapshot"], r["check"]
        killed_by = []
        if c["rc"] != 0:
            killed_by.append("counter(LINEAR_PATHS)")
        if s["rc"] != 0:
            killed_by.append("snapshot")
        if k["rc"] != 0:
            killed_by.append("check")
        verdicts.append(dict(name=r["name"], desc=m["desc"], sha=m["sha"],
                             killed=bool(killed_by), killed_by=killed_by,
                             counter=c, snapshot=s, check=k))
    summary = dict(probe_m2_sha=sha((SCRATCH / "M2-probe.sh").read_bytes()),
                   mutants=verdicts)
    (outroot / "summary.json").write_text(json.dumps(summary, indent=2))
    for v in verdicts:
        print(f"RESULT {v['name']:<26} killed={int(v['killed'])} by={','.join(v['killed_by']) or 'ALL-SURVIVED'} "
              f"counter(mis={v['counter'].get('mismatches')},cells={v['counter'].get('failed_cells')}) "
              f"snap(fail={v['snapshot'].get('fail')}) check(fail={v['check'].get('failures')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
