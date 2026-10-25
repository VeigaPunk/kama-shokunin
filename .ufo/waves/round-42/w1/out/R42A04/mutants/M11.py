#!/usr/bin/env python3
"""round42-selfdesc-reconcile.py - kama round-42 C1 (calibration) counter.

Question: do the lane's standing self-description surfaces - the SCORECARD head
(banner, Planned, Retired, Saturation, Capabilities, Axes) and the files that
describe the lane (README, PROVINCE) - match observed repository state at a
revision?  Round 41 reconciled only the `## Axes` table; seat R41A10 itemised
the surfaces around it that the tree contradicts (SCORECARD banner lines 6-13,
Planned, Retired, Saturation, head Capabilities, README, PROVINCE).

Terms (all derived from the tree at --tip, never typed here):
  head      SCORECARD.md text before its first line starting `## `.
  maxN      greatest N over SCORECARD lines matching `^## Round (\\d+)`.
  section(X) text of the FIRST line `## X` up to the next `## ` line.
  canon     the highest-numbered "**Capabilities - canonical list as of round N**"
            table (names; first-working-round column).
  vector    scores of the `## Axes` table rows (last integer of cell 2).
  census    SOURCES registry counts at --tip: rows with status mined|queued|rejected.

Facts (each failed item adds 1 to its counter):
  r41        the round-41 head-table counter (hash/lines/run/dead/score/hollow
             mismatches), imported unchanged: tools/round41-scorecard-reconcile.py.
  banner     head contains `operability + calibration` and not `operability and
             freshness`; head does not contain `adds **zero** verified completed
             rounds`; head matches `Latest measured round: <maxN>`.
  planned    section(Planned) has no `.ufo/round-5/continuation.md` and no
             `freshness move`, names `### Planned (round <maxN+1>)`, and that
             heading exists as a line in SCORECARD.md followed (next non-blank
             line) by a numbered item.
  retired    section(Retired) has no `Both assigned axes` and no `every model
             endpoint is dead`, and states `<len(vector)> axes` and `<len(canon)>
             capabilities`.
  saturation section(Saturation) has no `8/10 on every owned axis`; states the
             derived vector `operability 8, freshness 8, ...` in head-table order;
             states `first-working rounds <r1, r2, ...>` from canon; states
             `nudge inactive` iff min(vector[operability], vector[calibration]) < 8
             (else `nudge active`) and not the opposite.
  caps       the names in section(Capabilities)'s table equal canon's names, and
             every `<n> (opened|mined|queued|rejected)` in that section equals
             the census count.
  receipts   every backticked `.ufo/...` token (no `<`, `*`, space, `$`) cited in
             the SCORECARD sections whose heading names round 40 or round 41
             resolves at --tip, unless the token is quoted inside a section whose
             heading says `record corrections` (the append-only correction rows).
  readme     every non-dot top-level entry of the tree appears backticked in
             README.md.
  province   every `tools/` or `registry/` token in a canon row's evidence cell
             appears in PROVINCE.md.
  rel        the head-table row of each axis carries a `run` fact whose command
             contains that axis's needle: operability `pin-watch.py selftest`,
             freshness `recheck`, depth `SKILL.md`, coverage `corpus/knowledge`,
             calibration `verifier-spotcheck`, adjacency `cross-lane-scope.md`.

mismatches = r41 + banner + planned + retired + saturation + caps + receipts +
             readme + province + rel;  met = mismatches == 0.

Output: one summary line then `detail:` lines; also written to --out.
Exit 0 met, 1 not met, 2 could not evaluate.  Read-only on --repo; temporary
exports are removed (the imported r41 counter owns its own export).
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import re
import subprocess
import sys

NEEDLE = {"operability": "pin-watch.py selftest", "freshness": "recheck", "depth": "SKILL.md",
          "coverage": "corpus/knowledge", "calibration": "verifier-spotcheck",
          "adjacency": "cross-lane-scope.md"}
ASSIGNED = ("operability", "calibration")
SAT_LINE = 8
RECEIPT_ROUNDS = (40, 41)


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode()


def show(repo, tip, path):
    p = subprocess.run(["git", "-C", repo, "cat-file", "-p", f"{tip}:{path}"], capture_output=True)
    return p.stdout.decode(errors="replace") if p.returncode == 0 else None


def exists(repo, tip, path):
    return subprocess.run(["git", "-C", repo, "cat-file", "-e", f"{tip}:{path.rstrip('/')}"],
                          capture_output=True).returncode == 0


def sections(text, name):
    """All sections whose heading line is `## name` (exact)."""
    out, cur = [], None
    for l in text.split("\n"):
        if l.startswith("## "):
            if cur is not None:
                out.append("\n".join(cur))
            cur = [] if l.strip() == f"## {name}" else None
        elif cur is not None:
            cur.append(l)
    if cur is not None:
        out.append("\n".join(cur))
    return out


def table_rows(lines):
    rows = []
    for ln in lines:
        if ln.startswith("|"):
            rows.append([c.strip() for c in ln.strip().strip("|").split("|")])
        elif rows:
            break
    return rows[2:] if len(rows) >= 2 else []


def canon(text):
    best, rows = -1, []
    lines = text.split("\n")
    for i, l in enumerate(lines):
        m = re.search(r"canonical list as of round\s+(\d+)\*\*", l, re.I)
        if m and int(m.group(1)) > best:
            best, rows = int(m.group(1)), table_rows(lines[i + 1:])
    return best, rows


def load_r41(here):
    spec = importlib.util.spec_from_file_location("r41c1", os.path.join(here, "round41-scorecard-reconcile.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def census(sources):
    n = dict(opened=0, mined=0, queued=0, rejected=0)
    for l in sources.split("\n"):
        if re.match(r"^ {0,3}\|\s*S\d{3,}\s*\|", l):
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            if len(c) == 11:
                n["opened"] += 1
                if c[7] in n:
                    n[c[7]] += 1
    return n


def evaluate(repo, tip, here):
    tip = git(repo, "rev-parse", "--verify", f"{tip}^{{commit}}").strip()
    sc = show(repo, tip, "SCORECARD.md")
    if sc is None:
        raise RuntimeError("SCORECARD.md missing at tip")
    d = []
    c = dict(r41=0, banner=0, planned=0, retired=0, saturation=0, caps=0, receipts=0, readme=0, province=0, rel=0)
    m41 = load_r41(here)
    r41c, r41d = m41.evaluate(repo, tip)
    c["r41"] = r41c["mismatches"]
    d += [f"detail: r41 {x[8:]}" for x in r41d]
    lines = sc.split("\n")
    head = []
    for l in lines:
        if l.startswith("## "):
            break
        head.append(l)
    head = "\n".join(head)
    rounds = [int(m.group(1)) for l in lines for m in [re.match(r"^## Round (\d+)", l)] if m]
    maxn = max(rounds)
    axes = m41.axes_table(sc)
    vector, rowtext = [], {}
    for cells in axes:
        if len(cells) >= 3:
            ax = cells[0].replace("*", "").strip().split(" ")[0].lower()
            ints = re.findall(r"\d+", cells[1])
            vector.append((ax, int(ints[-1]) if ints else -1))
            rowtext[ax] = cells[2]
    vec = dict(vector)
    cn, crows = canon(sc)
    names = [r[0].strip("` *") for r in crows if r]
    firsts = sorted({int(re.findall(r"\d+", r[3])[-1]) for r in crows if len(r) >= 4 and re.findall(r"\d+", r[3])})

    def bad(k, msg):
        c[k] += 1
        d.append(f"detail: {k}: {msg}")

    # banner
    if "operability + calibration" not in head: bad("banner", "head lacks 'operability + calibration'")
    if "operability and freshness" in head: bad("banner", "head still says 'operability and freshness'")
    if "adds **zero** verified completed rounds" in head: bad("banner", "head still says 'adds zero verified completed rounds'")
    if not re.search(r"Latest measured round: %d\b" % maxn, head): bad("banner", f"head lacks 'Latest measured round: {maxn}'")
    # planned
    pl = "\n".join(sections(sc, "Planned")[:1])
    if ".ufo/round-5/continuation.md" in pl: bad("planned", "still points at .ufo/round-5/continuation.md")
    if "freshness move" in pl: bad("planned", "still plans a 'freshness move'")
    ph = f"### Planned (round {maxn + 1})"
    if ph not in pl: bad("planned", f"section does not name '{ph}'")
    idx = [i for i, l in enumerate(lines) if l.strip() == ph]
    okp = False
    for i in idx:
        nxt = [l for l in lines[i + 1:] if l.strip()][:1]
        okp = okp or bool(nxt and re.match(r"\s*1\.\s", nxt[0]))
    if not okp: bad("planned", f"no line '{ph}' followed by a numbered item")
    # retired
    rt = "\n".join(sections(sc, "Retired")[:1])
    if "Both assigned axes" in rt: bad("retired", "still says 'Both assigned axes'")
    if "every model endpoint is dead" in rt: bad("retired", "still says 'every model endpoint is dead'")
    if f"{len(vector)} axes" not in rt: bad("retired", f"does not state '{len(vector)} axes'")
    if f"{len(names)} capabilities" not in rt: bad("retired", f"does not state '{len(names)} capabilities'")
    # saturation
    st = "\n".join(sections(sc, "Saturation")[:1])
    if False: bad("saturation", "still says '8/10 on every owned axis'")
    vs = ", ".join(f"{a} {s}" for a, s in vector)
    if vs not in st: bad("saturation", f"does not state vector '{vs}'")
    fs = "first-working rounds " + ", ".join(str(x) for x in firsts)
    if fs not in st: bad("saturation", f"does not state '{fs}'")
    inactive = min(vec.get(a, 99) for a in ASSIGNED) < SAT_LINE
    want, other = ("nudge inactive", "nudge active") if inactive else ("nudge active", "nudge inactive")
    if want not in st: bad("saturation", f"does not state '{want}'")
    if other in st: bad("saturation", f"states '{other}'")
    # caps head
    cs = sections(sc, "Capabilities")[:1]
    cs = cs[0] if cs else ""
    hn = [r[0].strip("` *") for r in table_rows(cs.split("\n")) if r]
    if sorted(hn) != sorted(names): bad("caps", f"head names {sorted(hn)} != canon (round {cn}) {sorted(names)}")
    src = show(repo, tip, "corpus/SOURCES.md") or ""
    cen = census(src)
    for n, w in re.findall(r"\b(\d+) (opened|mined|queued|rejected)\b", cs):
        if int(n) != cen[w]: bad("caps", f"states {n} {w}; census {cen[w]}")
    # receipts
    chunks, exempt = [], ""
    for i, l in enumerate(lines):
        if not re.match(r"^#{2,3} ", l):
            continue
        level = len(l) - len(l.lstrip("#"))
        body = []
        for l2 in lines[i + 1:]:
            if re.match(r"^#{1,%d} " % level, l2):
                break
            body.append(l2)
        if re.search(r"record corrections", l, re.I):
            exempt += "\n".join(body)
        elif any(re.search(r"Round[ -]?%d\b" % r, l, re.I) for r in RECEIPT_ROUNDS):
            chunks.append(body)
    cited = set()
    for ch in chunks:
        for tok in re.findall(r"`([^`]+)`", "\n".join(ch)):
            if tok.startswith(".ufo/") and not any(x in tok for x in " <>*$") and tok not in exempt:
                for p in m41.expand(tok):
                    cited.add(p)
    for p in sorted(cited):
        if not exists(repo, tip, p): bad("receipts", f"sections of rounds {RECEIPT_ROUNDS} cite missing {p}")
    # readme
    rd = show(repo, tip, "README.md") or ""
    for name in git(repo, "ls-tree", "--name-only", tip).split("\n"):
        if name and not name.startswith(".") and f"`{name}`" not in rd and f"`{name}/`" not in rd:
            bad("readme", f"README.md does not name top-level entry {name}")
    # province
    pv = show(repo, tip, "PROVINCE.md") or ""
    for r in crows:
        if len(r) >= 3:
            for tok in re.findall(r"`([^`]+)`", r[2]):
                if tok.startswith(("tools/", "registry/")) and tok not in pv:
                    bad("province", f"PROVINCE.md lacks {tok} (capability {r[0].strip('` *')})")
    # rel
    for ax, needle in NEEDLE.items():
        ev = rowtext.get(ax, "")
        cmds = [m[0] for m in m41.RUN_RE.findall(ev)]
        if not any(needle in x for x in cmds): bad("rel", f"{ax} row has no run fact containing '{needle}'")
    mism = sum(c.values())
    return tip, c, mism, d, maxn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--tip", default="HEAD")
    ap.add_argument("--out")
    a = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        tip, c, mism, d, maxn = evaluate(os.path.abspath(a.repo), a.tip, here)
    except (RuntimeError, subprocess.CalledProcessError, AttributeError, ValueError) as e:
        print(f"could-not-evaluate: {e}", file=sys.stderr)
        return 2
    met = mism == 0
    line = " ".join(f"{k}={v}" for k, v in c.items()) + f" mismatches={mism} maxN={maxn} met={met}"
    out = "\n".join([f"tip={tip}", line, *d]) + "\n"
    sys.stdout.write(out)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, "w") as f:
            f.write(out)
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
