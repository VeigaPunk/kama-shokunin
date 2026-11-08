#!/usr/bin/env python3
"""round94-setter-sweep.py - round-94 C2 (depth) frozen counter.

Extends the round-93 setter counter to the round-94 population and row shape. The round-94
section "Listen port and slot-count setters (round 94 revision)" supersedes the round-93 port/slot
rows: it adds the config.ini route (load_from_ini/apply_to_params/apply_system_config/config.ini/
fs_get_config_directory/SERVER_ENV_ROUTER_PORT/LLAMA_SERVER_ROUTER_PORT), the entry-point anchors
(cli-server.h, server_role_detect, update_args, server_connect::start), the common_arg::operator<
preset ordering, and get_environment in server-models.cpp, over every *.cpp/*.h/*.hpp under
common/ and tools/ of the pinned llama.cpp b12177 archive.

Row (12 cells): `| Pnn | file | line | text | parameter | entry | scope | condition | effect | value | source |`
  parameter in {port, n_parallel, -}; entry in {server, cli, router-child, router, shared, other,
  unrelated}; effect in {default, overrides, declares, copies, unrelated}.
  B4 pairing: parameter `-` <=> effect in {copies, declares, unrelated} (mechanism/text, never a
  value setter); parameter port/n_parallel <=> effect in {default, overrides, copies, unrelated}.
  B5 value: effect default/overrides -> value non-empty and not `-`, and when the assignment
  right-hand side is an integer literal the value cell equals that literal; other effects `-`.
  B6 source: an S-id whose SOURCES.md row cells contain `/b12177/<file>`.
  B7 derived (common/arg.cpp only): same add_opt block rule as round 93 (condition names the
  block's first long option; scope lists the set_examples names).
D-row (7 cells): `| R18 | port | <entry summary> | <condition> | <ids> | <decision> | <sources> |`
  and `| R19 | n_parallel | ... |`. The id set must equal the set of bound P-rows with that
  parameter, effect in {default, overrides}, and entry not in {other, unrelated}; the decision
  cell must name every one of those ids.

Exit: 0 predicate met | 1 not met | 2 could-not-evaluate.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

HEAD = "## Listen port and slot-count setters (round 94 revision)"
URL = "https://codeload.github.com/ggml-org/llama.cpp/tar.gz/refs/tags/b12177"
TARBALL_SHA256 = "f50a52f4ba45dd5b4b906db97cf230ce2e3b1117a0b9017411322ecba63eea13"
ROOTS = ("common/", "tools/")
EXTS = (".cpp", ".h", ".hpp")
POP_RE = re.compile(r'\b(port|n_parallel)\s*=[^=]|LLAMA_ARG_PORT|LLAMA_ARG_N_PARALLEL|"--port"|"--parallel"|AIP_HTTP_PORT')
CFG_SUBSTR = ("load_from_ini", "apply_to_params", "apply_system_config", "config.ini",
              "fs_get_config_directory", "SERVER_ENV_ROUTER_PORT", "LLAMA_SERVER_ROUTER_PORT")
ENTRY_SUBSTR = ("cli-server.h", "server_role_detect", "update_args", "server_connect::start")
PORT_TOK = re.compile(r'\bport\s*=[^=]|LLAMA_ARG_PORT|"--port"|AIP_HTTP_PORT')
NP_TOK = re.compile(r'\bn_parallel\s*=[^=]|LLAMA_ARG_N_PARALLEL|"--parallel"')
INT_RHS = re.compile(r'\b(?:port|n_parallel)\s*=\s*(-?\d+)\s*;')
P_RE = re.compile(r"^\| *(P\d+) *\|")
D_RE = re.compile(r"^\| *(R18) *\|")
SRC_RE = re.compile(r"^ {0,3}\| *(S\d{3,}) *\|")
MIN_POP = 90
PARAMS = {"port", "n_parallel", "-"}
ENTRIES = {"server", "cli", "router-child", "router", "shared", "other", "unrelated"}
EFFECTS = {"default", "overrides", "declares", "copies", "unrelated"}
D_PARAM = {"R18": "port", "R19": "n_parallel"}


class CannotEvaluate(Exception):
    pass


def show(repo, rev, path) -> str:
    p = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"], capture_output=True)
    if p.returncode != 0:
        raise CannotEvaluate(f"{path} absent at {rev}")
    return p.stdout.decode("utf-8", "replace")


def rendered_lines(text: str):
    in_comment = False
    fence = None
    for line in text.split("\n"):
        if fence is not None:
            if line.strip().startswith(fence):
                fence = None
            continue
        if in_comment:
            if "-->" in line:
                in_comment = False
                line = line.split("-->", 1)[1]
                if not line.strip():
                    continue
            else:
                continue
        while "<!--" in line:
            pre, rest = line.split("<!--", 1)
            if "-->" in rest:
                line = pre + rest.split("-->", 1)[1]
            else:
                line = pre
                in_comment = True
                break
        s = line.lstrip()
        if s.startswith("```") or s.startswith("~~~"):
            fence = s[:3]
            continue
        yield line


def split_cells(line: str):
    cells, cur, i, s = [], [], 0, line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            cur.append("|")
            i += 2
            continue
        if s[i] == "|":
            cells.append("".join(cur).strip())
            cur = []
        else:
            cur.append(s[i])
        i += 1
    cells.append("".join(cur).strip())
    return cells


def section_rows(skill: str):
    prow, drow, inside = [], [], False
    for line in rendered_lines(skill):
        if line.startswith("## "):
            inside = line.rstrip() == HEAD
            continue
        if not inside:
            continue
        if P_RE.match(line):
            prow.append(split_cells(line))
        elif D_RE.match(line):
            drow.append(split_cells(line))
    return prow, drow


def sources(text: str):
    out = {}
    for line in text.split("\n"):
        m = SRC_RE.match(line)
        if m:
            out.setdefault(m.group(1), split_cells(line))
    return out


def load_archive(work: Path, archive: Path | None):
    if archive is None:
        archive = work / "b12177.tar.gz"
        p = subprocess.run(["curl", "-sfL", "--max-time", "300", "-o", str(archive), URL], capture_output=True)
        if p.returncode != 0:
            raise CannotEvaluate(f"download failed rc={p.returncode}")
    data = archive.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != TARBALL_SHA256:
        raise CannotEvaluate(f"archive sha256 {digest} != pinned {TARBALL_SHA256}")
    files = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
        for m in tf.getmembers():
            if not m.isfile():
                continue
            rel = m.name.split("/", 1)[1] if "/" in m.name else m.name
            if rel.startswith(ROOTS) and rel.endswith(EXTS):
                files[rel] = tf.extractfile(m).read().decode("utf-8", "replace").split("\n")
    return files, digest


def population(files):
    pop = {}
    for rel in sorted(files):
        for i, line in enumerate(files[rel], 1):
            hit = bool(POP_RE.search(line)) or any(s in line for s in CFG_SUBSTR) or any(s in line for s in ENTRY_SUBSTR)
            if rel == "common/arg.h" and "operator<" in line:
                hit = True
            if rel == "tools/server/server-models.cpp" and "get_environment" in line:
                hit = True
            if hit:
                pop[(rel, i)] = line
    return pop


def arg_block(lines, ln):
    i = ln - 1
    start = None
    while i >= 0:
        t = lines[i]
        if "add_opt(common_arg(" in t:
            start = i
            break
        if i < ln - 1 and re.match(r"\s*\)\s*(\.set_\w+\(.*\))*\s*\)\s*;", t):
            return None
        i -= 1
    if start is None:
        return None
    end = None
    for j in range(ln - 1, len(lines)):
        if re.match(r"\s*\)(\.set_\w+\(.*\))*\s*\)\s*;", lines[j]) or re.search(r"\)\);\s*$", lines[j]):
            end = j
            break
    if end is None:
        return None
    block = "\n".join(lines[start:end + 1])
    opts = re.findall(r'"(--[A-Za-z0-9][\w.-]*)"', "\n".join(lines[start:min(start + 3, end + 1)]))
    m = re.search(r"\.set_examples\(\{([^}]*)\}\)", lines[end]) or re.search(r"\.set_examples\(\{([^}]*)\}\)", block[-400:])
    ex = sorted(x.strip() for x in m.group(1).split(",") if x.strip()) if m else ["LLAMA_EXAMPLE_COMMON"]
    return (opts[0] if opts else None), ex


def grade_p(cells, pop, files, srcs, seen):
    if len(cells) != 11:
        return False, f"cells={len(cells)}", 0, 0, None
    rid, f, ln, text, param, entry, scope, cond, effect, value, src = cells
    if not ln.isdigit():
        return False, "line", 0, 0, None
    key = (f, int(ln))
    if key not in pop:
        return False, "fabricated", 0, 0, key
    if key in seen:
        return False, "duplicate", 0, 0, key
    line = pop[key]
    t = text.strip()
    if t.startswith("`") and t.endswith("`") and len(t) >= 2:
        t = t[1:-1]
    if t != line.strip():
        return False, "text", 0, 0, key
    if param not in PARAMS:
        return False, "parameter-enum", 0, 0, key
    if param == "n_parallel" and not NP_TOK.search(line):
        return False, "parameter-token", 0, 0, key
    if param == "port" and not PORT_TOK.search(line):
        return False, "parameter-token", 0, 0, key
    if entry not in ENTRIES:
        return False, "entry-enum", 0, 0, key
    if effect not in EFFECTS:
        return False, "effect-enum", 0, 0, key
    if param == "-":
        if effect in ("default", "overrides"):
            return False, "dash-param-setter", 0, 0, key
    else:
        if effect == "unrelated":
            return False, "param-unrelated", 0, 0, key
    m = INT_RHS.search(line)
    if effect in ("default", "overrides"):
        if m and value != m.group(1):
            return False, "value-literal", 0, 0, key
        if not value or value == "-":
            return False, "value-empty", 0, 0, key
    elif value != "-":
        return False, "value-not-dash", 0, 0, key
    row = srcs.get(src)
    if row is None or not any(f"/b12177/{f}" in c for c in row):
        return False, "source", 0, 0, key
    if not cond:
        return False, "condition-empty", 0, 0, key
    checked = disagree = 0
    if f == "common/arg.cpp":
        lines = files[f]
        b = arg_block(lines, int(ln))
        if b is not None:
            opt, ex = b
            checked += 2
            if opt is None or opt not in cond:
                disagree += 1
            if [x.strip() for x in scope.split(",")] != ex:
                disagree += 1
        else:
            prev = " ".join(lines[max(0, int(ln) - 3):int(ln) - 1])
            mm = re.search(r"ex == (LLAMA_EXAMPLE_\w+)", prev)
            if mm:
                checked += 1
                if mm.group(1) not in cond:
                    disagree += 1
    if disagree:
        return False, "derived", checked, disagree, key
    return True, "bound", checked, 0, key


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--archive", type=Path)
    ap.add_argument("--skill-file", type=Path)
    ap.add_argument("--sources-file", type=Path)
    a = ap.parse_args()
    a.work.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="r94-setters-", dir=a.work)).resolve()
    try:
        rv = subprocess.run(["git", "-C", str(a.repo), "rev-parse", "--verify", a.rev + "^{commit}"],
                            capture_output=True, text=True)
        if rv.returncode != 0:
            raise CannotEvaluate(f"unresolvable rev {a.rev}")
        rev = rv.stdout.strip()
        skill = a.skill_file.read_text() if a.skill_file else show(a.repo, rev, "SKILL.md")
        srcs = sources(a.sources_file.read_text() if a.sources_file else show(a.repo, rev, "corpus/SOURCES.md"))
        files, digest = load_archive(work, a.archive)
        pop = population(files)
    except CannotEvaluate as e:
        print(f"SETTER_SWEEP could-not-evaluate: {e}")
        return 2
    finally:
        shutil.rmtree(work, ignore_errors=True)
    prow, drow = section_rows(skill)
    seen, bound, unbound, dup, fab, dchk, ddis = {}, 0, 0, 0, 0, 0, 0
    for cells in prow:
        ok, why, c, d, key = grade_p(cells, pop, files, srcs, seen)
        dchk += c
        ddis += d
        if why == "duplicate":
            dup += 1
        if why == "fabricated":
            fab += 1
        if ok:
            bound += 1
            seen[key] = cells
        else:
            unbound += 1
        print(f"SETTER_ROW {cells[0] if cells else '?'} {'bound' if ok else 'unbound'} {why}")
    missing = sum(1 for k in pop if k not in seen)
    for k in pop:
        if k not in seen:
            print(f"SETTER_MISSING {k[0]}:{k[1]}")
    dbound = 0
    dids = set()
    for cells in drow:
        did = cells[0]
        ok, why = False, "cells"
        if len(cells) == 7 and did in D_PARAM and did not in dids:
            dids.add(did)
            param = D_PARAM[did]
            _, p, _entrysum, _cond, over, dec, _srcs = cells
            want = {r[0] for r in seen.values()
                    if r[4] == param and r[8] in ("default", "overrides") and r[5] not in ("other", "unrelated")}
            got = {x.strip() for x in over.split(",") if x.strip()}
            if p != param:
                why = "header"
            elif got != want or not want:
                why = f"setter-set want={len(want)} got={len(got)}"
            elif any(not re.search(r"\b" + re.escape(x) + r"\b", dec) for x in want):
                why = "decision-names"
            else:
                ok, why = True, "bound"
        if ok:
            dbound += 1
        print(f"SETTER_DECISION {did} {'bound' if ok else 'unbound'} {why}")
    n = len(pop)
    met = (n >= MIN_POP and len(prow) == n and bound == n and unbound == 0 and missing == 0 and dup == 0
           and fab == 0 and ddis == 0 and len(drow) == 2 and dbound == 2)
    print(f"SETTER_SWEEP {n} {len(prow)} {len(drow)} {bound} {unbound} {missing} {dup} {fab} "
          f"derived_checked={dchk} derived_disagree={ddis} decisions={dbound}/2 pop={n} met={met}")
    print(f"SETTER_DIGEST {digest}")
    return 0 if met and not (a.skill_file or a.sources_file) else 1


if __name__ == "__main__":
    sys.exit(main())
