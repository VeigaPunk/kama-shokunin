#!/usr/bin/env python3
"""MT02 mutation harness for the frozen r94 C2 counter.

Single-point mutants of tools/round94-setter-sweep.py (M2 bytes, sha256
49c5d0cb346ff4d693aecc5a287dc6bf09f916e0acc69ef5f8872366e41b9fff).
Detector A (committed control): counter must print the c2.out shape on the
M2 SKILL.md section + M2 corpus/SOURCES.md.
Detector B (forgery): for control-survivors, a forged section that the
pristine counter rejects must still be rejected by the mutant.
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
S = Path("/fast/scratch/hyaku/kama-r94/MT02SetterCounterMutants")
WT = S / "wt"
REV = "6aa5fa6bd9bbf44c4b2ca3f1e2158e7d5aa92623"
ARCHIVE = S / "b12177.tar.gz"
WORK = S / "work"
FORGE = S / "forge"
SKILL = OUT / "SKILL.M2.md"
SOURCES = OUT / "SOURCES.M2.md"
PRISTINE = OUT / "counter.M2.py"
HEAD = "## Listen port and slot-count setters (round 94 revision)"

# id -> (label, old, new). Exactly one occurrence required.
MUTANTS = [
    ("m01", "POP_RE narrowed: drop \"--parallel\"",
     '|"--port"|"--parallel"|AIP_HTTP_PORT\')',
     '|"--port"|AIP_HTTP_PORT\')'),
    ("m02", "POP_RE narrowed: generic n_parallel assignment dropped",
     "POP_RE = re.compile(r'\\b(port|n_parallel)\\s*=[^=]|LLAMA_ARG_PORT",
     "POP_RE = re.compile(r'\\bport\\s*=[^=]|LLAMA_ARG_PORT"),
    ("m03", "CFG_SUBSTR population clause dropped",
     "            hit = bool(POP_RE.search(line)) or any(s in line for s in CFG_SUBSTR) or any(s in line for s in ENTRY_SUBSTR)",
     "            hit = bool(POP_RE.search(line)) or any(s in line for s in ENTRY_SUBSTR)"),
    ("m04", "ENTRY_SUBSTR population clause dropped",
     "            hit = bool(POP_RE.search(line)) or any(s in line for s in CFG_SUBSTR) or any(s in line for s in ENTRY_SUBSTR)",
     "            hit = bool(POP_RE.search(line)) or any(s in line for s in CFG_SUBSTR)"),
    ("m05", "common/arg.h operator< population case dropped",
     '            if rel == "common/arg.h" and "operator<" in line:\n                hit = True\n',
     "            pass\n"),
    ("m06", "server-models.cpp get_environment population case dropped",
     '            if rel == "tools/server/server-models.cpp" and "get_environment" in line:\n                hit = True\n',
     "            pass\n"),
    ("m07", "PORT_TOK / NP_TOK checks swapped",
     '    if param == "n_parallel" and not NP_TOK.search(line):\n'
     '        return False, "parameter-token", 0, 0, key\n'
     '    if param == "port" and not PORT_TOK.search(line):\n'
     '        return False, "parameter-token", 0, 0, key\n',
     '    if param == "n_parallel" and not PORT_TOK.search(line):\n'
     '        return False, "parameter-token", 0, 0, key\n'
     '    if param == "port" and not NP_TOK.search(line):\n'
     '        return False, "parameter-token", 0, 0, key\n'),
    ("m08", "D_RE narrowed to R18 only",
     'D_RE = re.compile(r"^\\| *(R1[89]) *\\|")',
     'D_RE = re.compile(r"^\\| *(R18) *\\|")'),
    ("m09", "n_parallel parameter-token check removed",
     '    if param == "n_parallel" and not NP_TOK.search(line):\n'
     '        return False, "parameter-token", 0, 0, key\n',
     ""),
    ("m10", "entry-enum check removed",
     '    if entry not in ENTRIES:\n        return False, "entry-enum", 0, 0, key\n',
     ""),
    ("m11", "effect-enum check removed",
     '    if effect not in EFFECTS:\n        return False, "effect-enum", 0, 0, key\n',
     ""),
    ("m12", "dash-param-setter rule removed",
     '        if effect in ("default", "overrides"):\n',
     '        if False and effect in ("default", "overrides"):\n'),
    ("m13", "param-unrelated rule removed",
     '        if effect == "unrelated":\n',
     '        if False:\n'),
    ("m14", "INT_RHS literal check dropped (m = None)",
     "    m = INT_RHS.search(line)\n",
     "    m = None\n"),
    ("m15", "value-empty rule removed",
     '        if not value or value == "-":\n            return False, "value-empty", 0, 0, key\n',
     "        pass\n"),
    ("m16", "B2 text compare relaxed to substring",
     "    if t != line.strip():\n",
     "    if t not in line:\n"),
    ("m17", "source check removed",
     '    row = srcs.get(src)\n'
     '    if row is None or not any(f"/b12177/{f}" in c for c in row):\n'
     '        return False, "source", 0, 0, key\n',
     "    row = srcs.get(src)\n"),
    ("m18", "source containment relaxed to 'b12177'",
     '    if row is None or not any(f"/b12177/{f}" in c for c in row):\n',
     '    if row is None or not any("b12177" in c for c in row):\n'),
    ("m19", "derived set_examples scope check removed",
     '            if [x.strip() for x in scope.split(",")] != ex:\n',
     "            if False:\n"),
    ("m20", "arg_block option index opts[0] -> opts[-1]",
     "    return (opts[0] if opts else None), ex\n",
     "    return (opts[-1] if opts else None), ex\n"),
    ("m21", "decision set equality -> subset (want <= got)",
     "            elif got != want or not want:\n",
     "            elif not (want <= got) or not want:\n"),
    ("m22", "decision header (parameter cell) check removed",
     "            if p != param:\n",
     "            if False:\n"),
    ("m23", "decision-names check removed",
     '            elif any(not re.search(r"\\b" + re.escape(x) + r"\\b", dec) for x in want):\n',
     "            elif False:\n"),
    ("m24", "decision id-uniqueness check removed",
     "        if len(cells) == 7 and did in D_PARAM and did not in dids:\n",
     "        if len(cells) == 7 and did in D_PARAM:\n"),
    ("m25", "MIN_POP lowered 90 -> 1",
     "MIN_POP = 90\n",
     "MIN_POP = 1\n"),
    ("m26", "duplicate-row detection removed",
     '    if key in seen:\n        return False, "duplicate", 0, 0, key\n',
     ""),
    ("m27", "section heading test startswith('## ') -> startswith('##')",
     '        if line.startswith("## "):\n',
     '        if line.startswith("##"):\n'),
    ("m28", "condition-empty check removed",
     '    if not cond:\n        return False, "condition-empty", 0, 0, key\n',
     ""),
    ("m29", "rows==population guard removed from met",
     "    met = (n >= MIN_POP and len(prow) == n and bound == n and unbound == 0 and missing == 0 and dup == 0\n",
     "    met = (n >= MIN_POP and bound == n and unbound == 0 and missing == 0 and dup == 0\n"),
]


def run(counter: Path, skill: Path, sources: Path, tag: str) -> tuple[int, str]:
    cmd = [sys.executable, str(counter), "--repo", str(WT), "--rev", REV,
           "--work", str(WORK), "--archive", str(ARCHIVE),
           "--skill-file", str(skill), "--sources-file", str(sources)]
    p = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, "TMPDIR": str(S)})
    return p.returncode, p.stdout + (("STDERR:" + p.stderr) if p.stderr else "")


def met_of(txt: str):
    m = re.search(r"SETTER_SWEEP .* met=(True|False)", txt)
    return None if m is None else m.group(1) == "True"


def split_cells(line: str):
    import importlib.util
    spec = importlib.util.spec_from_file_location("sw", PRISTINE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.split_cells(line)


def join_cells(cells):
    return "| " + " | ".join(cells) + " |"


def section_bounds(lines):
    start = next(i for i, l in enumerate(lines) if l.rstrip() == HEAD)
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## "):
            end = i
            break
    return start, end


def find_row(lines, rid):
    for i in range(*section_bounds(lines)):
        if re.match(r"^\| *" + rid + r" *\|", lines[i]):
            return i
    raise SystemExit(f"row {rid} not found")


def row_id_by_loc(lines, rel, ln):
    for i in range(*section_bounds(lines)):
        m = re.match(r"^\| *(P\d+) *\|", lines[i])
        if not m:
            continue
        c = split_cells(lines[i])
        if c[1] == rel and c[2] == str(ln):
            return i
    raise SystemExit(f"row {rel}:{ln} not found")


def forge(name, ops):
    lines = SKILL.read_text().split("\n")
    for op in ops:
        kind = op[0]
        if kind == "cell":
            _, rid, idx, val = op
            i = find_row(lines, rid)
            c = split_cells(lines[i])
            old = c[idx]
            c[idx] = val
            lines[i] = join_cells(c)
            note = f"{rid} cell[{idx}]: {old!r} -> {val!r}"
        elif kind == "loc":
            _, rel, ln, idx, val = op
            i = row_id_by_loc(lines, rel, ln)
            c = split_cells(lines[i])
            old = c[idx]
            c[idx] = val
            lines[i] = join_cells(c)
            note = f"{c[0]} ({rel}:{ln}) cell[{idx}]: {old!r} -> {val!r}"
        elif kind == "copyrow":
            _, dst, src = op
            i = find_row(lines, dst)
            j = find_row(lines, src)
            lines[i] = lines[j]
            note = f"row {dst} replaced by a copy of {src}"
        elif kind == "insert":
            _, before, text = op
            i = find_row(lines, before)
            lines.insert(i, text)
            note = f"inserted {text!r} before {before}"
        elif kind == "duprow":
            _, src, newid = op
            i = find_row(lines, src)
            c = split_cells(lines[i])
            c[0] = newid
            lines.insert(i + 1, join_cells(c))
            note = f"duplicated {src} as {newid}"
        else:
            raise SystemExit(kind)
        notes.append((name, note))
    p = FORGE / f"{name}.md"
    p.write_text("\n".join(lines))
    return p


notes: list[tuple[str, str]] = []
FORGES = {
    "f01_text_substring": [("cell", "P19", 3, "params.port")],
    "f02_source_missing_sid": [("cell", "P19", 10, "S999")],
    "f03_source_wrong_file": [("cell", "P19", 10, "S604")],
    "f04_scope_derived": [("cell", "P19", 6, "LLAMA_EXAMPLE_SERVER, LLAMA_EXAMPLE_EMBEDDING")],
    "f05_entry_bogus": [("cell", "P19", 5, "bogus")],
    "f06_value_literal": [("cell", "P21", 9, "9999")],
    "f07_value_empty": [("cell", "P19", 9, "-")],
    "f08_decision_superset": [("cell", "R18", 4, None)],  # filled below
    "f09_decision_duplicate": [("copyrow", "R19", "R18")],
    "f10_dash_setter": [("cell", "P03", 8, "overrides"), ("cell", "P03", 9, "4")],
    "f11_param_unrelated": [("loc", "tools/server/server-http.cpp", 116, 8, "unrelated"),
                            ("loc", "tools/server/server-http.cpp", 116, 9, "-")],
    "f12_entry_bogus_p01": [("cell", "P01", 5, "bogus")],
    "f13_effect_bogus": [("cell", "P01", 8, "bogus")],
    "f14_cond_empty": [("cell", "P92", 7, "")],
    "f15_subheading": [("insert", "P50", "#### note")],
    "f16_np_token": [("loc", "tools/server/server-http.cpp", 116, 4, "n_parallel")],
    "f17_decision_header": [("cell", "R18", 1, "n_parallel")],
    "f18_decision_names": [("cell", "R18", 5, None)],  # filled below
    "f20_duplicate_row": [("duprow", "P19", "P93")],
}

# f08: append a bogus id to R18's overriding set.
_lines = SKILL.read_text().split("\n")
_c = split_cells(_lines[find_row(_lines, "R18")])
FORGES["f08_decision_superset"] = [("cell", "R18", 4, _c[4] + ", P99")]
# f18: remove every mention of P19 from R18's decision prose.
FORGES["f18_decision_names"] = [("cell", "R18", 5, re.sub(r"\bP19\b,? ?", "", _c[5]).strip())]

# mutant -> forge that should kill it
PAIR = {
    "m09": ["f16_np_token"], "m10": ["f05_entry_bogus", "f12_entry_bogus_p01"],
    "m11": ["f13_effect_bogus"], "m12": ["f10_dash_setter"], "m13": ["f11_param_unrelated"],
    "m14": ["f06_value_literal"], "m15": ["f07_value_empty"], "m16": ["f01_text_substring"],
    "m17": ["f02_source_missing_sid"], "m18": ["f03_source_wrong_file"],
    "m19": ["f04_scope_derived"], "m21": ["f08_decision_superset"],
    "m22": ["f17_decision_header"], "m23": ["f18_decision_names"],
    "m24": ["f09_decision_duplicate"], "m26": ["f20_duplicate_row"],
    "m27": ["f15_subheading"], "m28": ["f14_cond_empty"],
}


def main():
    OUT.joinpath("mutants").mkdir(exist_ok=True)
    OUT.joinpath("runs").mkdir(exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    FORGE.mkdir(parents=True, exist_ok=True)
    src = PRISTINE.read_text()
    assert hashlib.sha256(src.encode()).hexdigest() == "49c5d0cb346ff4d693aecc5a287dc6bf09f916e0acc69ef5f8872366e41b9fff"
    made = {}
    for mid, label, old, new in MUTANTS:
        n = src.count(old)
        if n != 1:
            raise SystemExit(f"{mid}: old string occurs {n}x")
        mp = OUT / "mutants" / f"{mid}.py"
        mp.write_text(src.replace(old, new))
        r = subprocess.run([sys.executable, "-m", "py_compile", str(mp)], capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit(f"{mid} does not compile: {r.stderr}")
        made[mid] = (mp, label)

    # Detector A: committed control shape.
    rc0, base = run(PRISTINE, SKILL, SOURCES, "baseline")
    (OUT / "runs" / "baseline.out").write_text(base)
    base_met = met_of(base)
    print(f"# baseline rc={rc0} met={base_met} lines={len(base.splitlines())}", flush=True)
    rows = []
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(run, made[mid][0], SKILL, SOURCES, mid): mid for mid in made}
        for f in cf.as_completed(futs):
            mid = futs[f]
            rc, out = f.result()
            (OUT / "runs" / f"{mid}.outing").write_text(out)
            if out == base:
                verdict, why = "SURVIVED-CONTROL", "byte-identical stdout"
            else:
                diff = [l for l in out.splitlines() if l not in base.splitlines() and not l.startswith("SETTER_ROW")]
                met = met_of(out)
                verdict = "KILLED-CONTROL"
                why = f"met={met}; " + ("; ".join(diff[:3]) if diff else "row lines differ")
            rows.append((mid, made[mid][1], verdict, why))

    # Detector B: forgeries against control-survivors.
    surviving = {r[0] for r in rows if r[2] == "SURVIVED-CONTROL"}
    forge_files = {}
    fdiff = []
    for fname, ops in FORGES.items():
        forge_files[fname] = forge(fname, ops)
        fdiff.extend(f"{fname}: {n}" for f, n in notes if f == fname)
    (OUT / "runs" / "forges.diff.txt").write_text("\n".join(fdiff) + "\n")

    pri = {}
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(run, PRISTINE, p, SOURCES, f"pri-{n}"): n for n, p in forge_files.items()}
        for f in cf.as_completed(futs):
            n = futs[f]
            rc, out = f.result()
            (OUT / "runs" / f"forge-pri-{n}.out").write_text(out)
            pri[n] = (met_of(out), out)

    pairs = [(mid, fname) for mid, fs in PAIR.items() if mid in surviving for fname in fs]
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(run, made[mid][0], forge_files[fname], SOURCES, f"{mid}-{fname}"): (mid, fname)
                for mid, fname in pairs}
        for f in cf.as_completed(futs):
            mid, fname = futs[f]
            rc, out = f.result()
            (OUT / "runs" / f"forge-{mid}-{fname}.out").write_text(out)
            pmet = pri[fname][0]
            mmet = met_of(out)
            unbound = [l for l in out.splitlines() if l.startswith("SETTER_ROW") and " unbound " in l] or \
                      [l for l in out.splitlines() if l.startswith("SETTER_DECISION") and " unbound " in l]
            if pmet is False and mmet is True:
                verdict, why = "KILLED-FORGERY", f"{fname}: pristine rejects, mutant accepts (false green)"
            elif pmet is True and mmet is False:
                verdict, why = "KILLED-FORGERY-STRICT", f"{fname}: pristine accepts, mutant rejects (false red)"
            elif pmet is False and mmet is False:
                verdict, why = "SURVIVED-FORGERY", f"{fname}: both reject (mutant first: {unbound[:2]})"
            else:
                verdict, why = "FORGERY-INEFFECTIVE", f"{fname}: pristine also accepts"
            for i, r in enumerate(rows):
                if r[0] == mid:
                    rows[i] = (mid, r[1], verdict, why)
    for i, r in enumerate(rows):
        if r[0] in surviving and r[2] == "SURVIVED-CONTROL":
            rows[i] = (r[0], r[1], "SURVIVED (no paired forgery)", r[3])

    rows.sort()
    tsv = ["mutant\tlabel\tverdict\tevidence"] + ["\t".join(r) for r in rows]
    (OUT / "runs" / "summary.tsv").write_text("\n".join(tsv) + "\n")
    print("\n".join(tsv))


if __name__ == "__main__":
    main()
