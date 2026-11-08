#!/usr/bin/env python3
"""round98-self-assessment-audit.py - round-98 C1 (calibration, lowest axis 7) frozen counter.

PREDICATE (frozen: plans/round-98-claims.md section C1):

    `python3 tools/round98-self-assessment-audit.py --repo . --rev <M1>` prints
    `SELF_ASSESS98 checks=20 mismatches=0 met=True rev=<resolved> ...` and exits 0 at the
    measured commit M1; the counter's own bytes never change after the freeze commit (kill rule K1).

Successor to tools/round97-self-assessment-audit.py (18 checks, frozen, never edited). Round-97's
wave found the round-97 audit blind to the SKILL section HEADING's count word: check 16 reads
the section body but `section()` excludes the heading line itself, so the live "three graded
forgeries" heading passed while the body said four. Round 98 grades the heading, and rolls the
count surfaces forward after C2 adds the overcharge mutant and W18/W19 (new set = six cells,
mutants = five, cells=19).

A calibration claim counts mismatches between what the lane says about itself and the repository
it claims to describe. The round-97 counter graded eighteen surfaces but read the §Round 97
section BODY only: its heading ("the three graded forgeries") was never graded, and the body
prose ("four probe variants survive all 13 of its cells") described only the four round-97
mutants. This version grades the heading's count word and rolls every count surface forward
after C2 adds W18/W19 and the overcharge mutant (six new cells, five mutants, cells=19).

  1-3  SCORECARD live `depth` row: SKILL.md sha256, line count, `^## ` section count.
  4-5  SCORECARD live `adjacency` row: the file exists, its sha256 and pipe-line count.
  6    SCORECARD capability row `router-byte-decided`: its pointer and its "measured against"
       commit both resolve and are ancestors, the pointer strictly precedes the graded revision,
       and BOTH cited `.ufo/waves/...` evidence paths exist at the pointer.
  7    The probe's ceiling comment states `5 + nd`, carries no constant-6 sentence, and no line
       that says "binding" names 1 000 000 or 6 steps/header (RV01 A1-A3).
  8    The probe comment carries every per-rank ceiling (nd = 0..4) from (MAX_STEPS - 4)/(5 + nd).
  9    SKILL.md's `### Round 96 correction` section carries its five table rows, each header count
       recomputed from MAX_STEPS.
  10   S621 exists, status `mined`, `teaches` opens `supersedes S618 —` with `5 + nd`.
  11   S620 exists, status `mined`, kind `spec`, tier `A`.
  12   `tools/round96-router-budget.py` at `f175a902` is byte-identical to the graded file and
       SCORECARD names `f175a902`.
  13   The round-96 C1 receipt carries `cells=13 mismatches=0 positive_mismatches=0 load_cells=13
       load_stable=1` and SCORECARD quotes that summary.
  14   The round-96 C2/C3 receipts carry their summary needles and SCORECARD quotes them.
  15   The two round-98 counters' docstrings state the probe's MAX_STEPS, MAX_META and the
       `4 + T x (5 + nd)` formula.
  16   The count claims agree with the counter's own sets: SCORECARD's depth row, SKILL's
       §Round 97 body and the counter docstring each name W14-W19 and say five mutants,
       six cells; `cells=19`; SKILL's §Round 97 cites S620 and S621.
  17   SOURCES.md ids are unique (last-wins).
  18   The probe's tensor loop charges exactly the four declared call sites (name, nd, dims, type
       + offset) and its preamble exactly three reads (magic, version, n_tensors/n_kv); a flat-6,
       6+nd or +1/header parser fails the set equality.
  19   The §Round 97 HEADING's count word equals the counter's graded-mutant count (round-97
       check-16 blindness: the heading line was never graded).
  20   The overcharge surface is named: the depth row and SKILL §Round 97 body name W18/W19 and
       the overcharge mutant, and the budget counter's MUTANTS set parses to five.

Disclosed limits: checks 13-14 grade the committed receipt needles and the SCORECARD quote of
them, not every number in the headers; checks 16/19/20 grade the named count statements, not
prose elsewhere; check 18 is a source-shape check, not a behavioral measurement (C2's W14-W19
grade the probe's behavior). Exit: 0 met | 1 mismatches>0 | 2 could-not-evaluate.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

PREAMBLE = 4
COUNTER96 = "tools/round96-router-budget.py"
IDENTITY_REV = "f175a902"
WORDS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
         "seven": 7, "eight": 8, "nine": 9}


def show(repo: Path, rev: str, path: str):
    p = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"], capture_output=True)
    return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else None


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def sources_rows(text: str):
    rows, ids = {}, []
    for line in (text or "").splitlines():
        m = re.match(r"^ {0,3}\| *(S\d{3,}) *\|", line)
        if m:
            ids.append(m.group(1))
            rows[m.group(1)] = [c.strip() for c in line.split("|")]
    return rows, ids


def section(text: str, heading: str):
    lines = (text or "").splitlines()
    start = next((i for i, l in enumerate(lines) if l.startswith(heading)), None)
    if start is None:
        return None
    out = []
    for l in lines[start + 1:]:
        if l.startswith("### ") or l.startswith("## "):
            break
        out.append(l)
    return out


def norm(s: str) -> str:
    return re.sub(r"[,_ ]", "", s)


def docstring(text: str) -> str:
    parts = (text or "").split('"""')
    return parts[1] if len(parts) >= 3 else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--rev", required=True)
    a = ap.parse_args()
    rv = git(a.repo, "rev-parse", "--verify", a.rev + "^{commit}")
    if rv.returncode != 0:
        print(f"SELF_ASSESS98 could-not-evaluate: unresolvable rev {a.rev}")
        return 2
    rev = rv.stdout.strip()
    skill = show(a.repo, rev, "SKILL.md")
    score = show(a.repo, rev, "SCORECARD.md")
    probe = show(a.repo, rev, "tools/kama-probe.sh")
    sources = show(a.repo, rev, "corpus/SOURCES.md")
    if skill is None or score is None or probe is None or sources is None:
        print("SELF_ASSESS98 could-not-evaluate: SKILL.md, SCORECARD.md, tools/kama-probe.sh "
              "or corpus/SOURCES.md missing at the graded revision")
        return 2

    checks = 0
    mismatches = 0

    # 1-3: the live depth row must describe SKILL.md at this revision.
    depth = next((l for l in score.splitlines() if l.startswith("| depth |")), "")
    declared_sha = re.search(r"sha256 `([0-9a-f]{64})`", depth)
    declared_lines = re.search(r"\((\d+) lines\)", depth)
    declared_sections = re.search(r"grep -c '\^## ' SKILL\.md` → `(\d+)`", depth)
    observed = git(a.repo, "show", f"{rev}:SKILL.md").stdout
    checks += 1
    if not declared_sha or hashlib.sha256(observed.encode()).hexdigest() != declared_sha.group(1):
        mismatches += 1
    checks += 1
    if not declared_lines or int(declared_lines.group(1)) != len(skill.splitlines()):
        mismatches += 1
    checks += 1
    if not declared_sections or int(declared_sections.group(1)) != sum(
            1 for l in skill.splitlines() if l.startswith("## ")):
        mismatches += 1

    # 4-5: the adjacency row's digest and pipe-line count, over an existing file.
    adj = next((l for l in score.splitlines() if l.startswith("| adjacency |")), "")
    adj_sha = re.search(r"sha256 `([0-9a-f]{64})`", adj)
    adj_pipes = re.search(r"→ `(\d+)` \(lines starting with a table pipe", adj)
    cross = show(a.repo, rev, "corpus/knowledge/cross-lane-scope.md")
    checks += 1
    if cross is None or not adj_sha or hashlib.sha256(cross.encode()).hexdigest() != adj_sha.group(1):
        mismatches += 1
    checks += 1
    if cross is None or not adj_pipes or int(adj_pipes.group(1)) != sum(
            1 for l in cross.splitlines() if l.startswith("|")):
        mismatches += 1

    # 6: the capability pointer: both commits, both paths, pointer strictly before the revision.
    cap = next((l for l in score.splitlines()
                if l.startswith("|") and "`router-byte-decided`" in l), "")
    hexes = re.findall(r"`([0-9a-f]{7,40})`", cap)
    evs = re.findall(r"`(\.ufo/waves/[^`]+)`", cap)
    checks += 1
    if len(hexes) < 2 or len(evs) < 2:
        mismatches += 1
    else:
        ok = hexes[0] != rev
        for h in hexes[:2]:
            ok = ok and git(a.repo, "merge-base", "--is-ancestor", h, rev).returncode == 0
        for e in evs[:2]:
            ok = ok and show(a.repo, hexes[0], e) is not None
        if not ok:
            mismatches += 1

    # 7-8: the probe's ceiling comment: arithmetic, no false binding line, every rank ceiling.
    lines = probe.splitlines()
    mi = next((i for i, l in enumerate(lines) if l.startswith("MAX_STEPS = ")), None)
    m = re.search(r"^MAX_STEPS = ([0-9_]+)", probe, re.M)
    max_steps = int(m.group(1).replace("_", "")) if m else None
    region = ""
    if mi is not None:
        lo = mi
        while lo > 0 and lines[lo - 1].startswith("#"):
            lo -= 1
        hi = mi + 1
        while hi < len(lines) and lines[hi].startswith("#"):
            hi += 1
        region = "\n".join(lines[lo:hi])
    checks += 1
    bad_binding = False
    for l in region.splitlines():
        low = l.lower()
        if "binding" in low and any(x in low for x in ("1 000 000", "1,000,000", "6 steps", "6 read")):
            bad_binding = True
    if "5 + nd" not in region or "6 steps per tensor header" in probe or bad_binding:
        mismatches += 1
    checks += 1
    if max_steps is None:
        mismatches += 1
    else:
        for nd in range(0, 5):
            want = "{:,}".format((max_steps - PREAMBLE) // (5 + nd))
            if want not in region:
                mismatches += 1
                break

    # 9: the Round-96 step-cost section's five rows recompute.
    sec96 = section(skill, "### Round 96 correction") or []
    checks += 1
    ok = True
    rows_seen = 0
    for l in sec96:
        rm = re.match(r"^\|\s*(\d)\s*\|\s*(\d+)\s*\|\s*([\d,]+)\s*\|\s*$", l.strip())
        if not rm:
            continue
        nd, steps, headers = int(rm.group(1)), int(rm.group(2)), int(rm.group(3).replace(",", ""))
        want_steps = 5 + nd
        want_headers = (max_steps - PREAMBLE) // want_steps if max_steps else None
        rows_seen += 1
        if steps != want_steps or want_headers != headers:
            ok = False
    if rows_seen != 5 or not ok:
        mismatches += 1

    # 10-11: the correction row and the spec row.
    rows, ids = sources_rows(sources)
    s621 = rows.get("S621", [])
    checks += 1
    if len(s621) < 12:
        mismatches += 1
    else:
        if not s621[7].startswith("supersedes S618 —") or "5 + nd" not in s621[7] \
                or s621[8] != "mined":
            mismatches += 1
    s620 = rows.get("S620", [])
    checks += 1
    if len(s620) < 12:
        mismatches += 1
    else:
        if s620[3] != "spec" or s620[4] != "A" or s620[8] != "mined":
            mismatches += 1

    # 12: the round-96 identity clause names a revision whose bytes are the current bytes.
    checks += 1
    cur = show(a.repo, rev, COUNTER96)
    old = show(a.repo, IDENTITY_REV, COUNTER96)
    if cur is None or old is None or cur != old or IDENTITY_REV not in score:
        mismatches += 1

    # 13-14: the round-96 receipts' summaries and SCORECARD's quotes of them.
    c1_receipt = show(a.repo, rev, ".ufo/waves/round-96/measured/c1.out") or ""
    c1_needle = "cells=13 mismatches=0 positive_mismatches=0 load_cells=13 load_stable=1"
    checks += 1
    if c1_needle not in c1_receipt or c1_needle not in score.replace("`", ""):
        mismatches += 1
    checks += 1
    ok = True
    for path, needle in ((".ufo/waves/round-96/measured/c2.out",
                          "DEPTH_AUDIT checks=14 mismatches=0"),
                         (".ufo/waves/round-96/measured/c3.out",
                          "DISCLOSURE_AUDIT checks=6 mismatches=0")):
        receipt = show(a.repo, rev, path) or ""
        ok = ok and needle in receipt and needle in score.replace("`", "")
    if not ok:
        mismatches += 1

    # 15: the round-97 counters' docstrings state the probe's constants and the formula.
    checks += 1
    rb = show(a.repo, rev, "tools/round98-router-budget.py")
    db = show(a.repo, rev, "tools/round98-depth-boundary-audit.py")
    ok = rb is not None and db is not None
    if ok and max_steps is not None:
        rdoc, ddoc = docstring(rb), docstring(db)
        ok = ("MAX_STEPS" in rdoc and norm(str(max_steps)) in norm(rdoc)
              and "MAX_META" in rdoc and "512" in rdoc
              and norm("4 + T") in norm(ddoc) and norm("5 + nd") in norm(ddoc))
    if not ok:
        mismatches += 1

    # 16: the count claims agree with the counter's own cell/mutant sets.
    checks += 1
    new_cells, mutants = [], []
    if rb is not None:
        mm = re.search(r"NEW_CELLS = \{(.*?)\}", rb, re.S)
        if mm:
            new_cells = re.findall(r'"(W\d\d-[^"]+)"', mm.group(1))
        mm = re.search(r"MUTANTS = \{(.*?)\n\}", rb, re.S)
        if mm:
            mutants = re.findall(r'^\s{4}"(\w+)":', mm.group(1), re.M)
    depth_forgeries = re.search(r"(\w+) graded probe forgeries", depth)
    sec97 = "\n".join(section(skill, "### Round 97 correction") or [])
    skill_variants = re.search(r"(\w+) probe variants", sec97)
    rdoc = docstring(rb or "")
    doc_cells = re.search(r"adds (\w+) cells", rdoc)
    ok = (len(new_cells) == 6 and len(mutants) == 5
          and depth_forgeries and WORDS.get(depth_forgeries.group(1).lower()) == len(mutants)
          and skill_variants and WORDS.get(skill_variants.group(1).lower()) == len(mutants)
          and doc_cells and WORDS.get(doc_cells.group(1).lower()) == len(new_cells)
          and "cells=19" in rdoc
          and all(w in depth for w in new_cells)
          and all(w in sec97 for w in new_cells)
          and "S620" in sec97 and "S621" in sec97)
    if not ok:
        mismatches += 1

    # 17: SOURCES ids are unique.
    checks += 1
    if len(ids) != len(set(ids)):
        mismatches += 1

    # 18: the tensor loop and preamble charge exactly the declared reads.
    checks += 1
    loop = []
    li = next((i for i, l in enumerate(lines) if l.startswith("            for _ in range(n_tensors):")), None)
    if li is not None:
        for l in lines[li + 1:]:
            if l.strip().startswith("infos.append"):
                break
            loop.append(l.strip())
    def charge_line(l: str) -> str:
        l = l.split("#")[0].strip()
        return l if any(t in l for t in ("need(", "rd(", "u64()", "u32()", "skip(")) else ""
    charged = [charge_line(l) for l in loop]
    charged = [c for c in charged if c]
    want_charged = ["skip(u64())", "nd = u32()", "ne = [u64() for _ in range(nd)] or [1]",
                    "tt, off = u32(), u64()"]
    pre = probe.split("def gguf_parse", 1)[-1].split("for _ in range(n_kv):", 1)[0]
    pre_ok = ('rd(4) != b"GGUF"' in pre and "ver = u32()" in pre
              and "n_tensors, n_kv = u64(), u64()" in pre)
    if charged != want_charged or not pre_ok:
        mismatches += 1

    # 19: the section HEADING's count word (never graded by the round-97 audit).
    checks += 1
    heading = next((l for l in skill.splitlines()
                    if l.startswith("### Round 97 correction")), "")
    hm = re.search(r"the (\w+) graded forgeries", heading)
    if not hm or WORDS.get(hm.group(1).lower()) != len(mutants) or len(mutants) != 5:
        mismatches += 1

    # 20: the overcharge surface is named in the depth row, the §Round 97 body, the budget
    # docstring and the MUTANTS set (five).

    checks += 1
    ok = (len(mutants) == 5 and "overcharge" in mutants
          and "overcharge" in depth.lower() and "overcharge" in sec97.lower()
          and "overcharge" in rdoc.lower()
          and all(w in depth for w in ("W18-800k-nd1", "W19-520k-nd4"))
          and all(w in sec97 for w in ("W18-800k-nd1", "W19-520k-nd4")))
    if not ok:
        mismatches += 1

    meta = hashlib.sha256(observed.encode()).hexdigest()
    print(f"SELF_ASSESS98 checks={checks} mismatches={mismatches} met={mismatches == 0} "
          f"rev={rev} skill_sha256={meta}")
    return 0 if mismatches == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
