#!/usr/bin/env python3
"""canonical_rows_audit.py - round-57 seat R57Item24CanonicalBinding (scratch prototype).

Independent, content-bound audit of the lane's CANONICAL capability table, plus an
omission control.  It shares no code with the lane's own counters: it does not import
tools/round42-selfdesc-reconcile.py (which supplies maxN) or
tools/capability-repertoire-audit.py (which supplies "listed/observed/unsubstantiated").
Every term below is re-derived from the bytes at --tip.

Questions:
  1. Is the canonical capability table present, and is the generation it claims the
     generation the SCORECARD's own prose points at?
  2. Do its rows (count, names, first-working rounds, evidence) agree with the two
     independent statements the SCORECARD makes about it - the `## Capabilities` mirror
     table and the Saturation section's "capability first-working rounds" vector?
  3. Is every row's evidence pointer present, and does the row's declared vocabulary
     occur in the artifact it points at (content binding, not just path existence)?
  4. Has a row been OMITTED - either from the newest canonical table while an older
     generation or another capability table still names it, or relative to a witness
     revision (--witness-tip)?

Declared terms (all from the tree at --tip; none typed in):
  marker      a line matching `**Capabilities - canonical list as of round N**`.
  gen         the greatest N over all markers (the newest canonical table).
  ctable      the first markdown table at or after the `gen` marker whose header has
              four cells and whose fourth header cell matches `first.working round`.
  stated      the cardinal in the prose between the `gen` marker and `ctable`
              ("Eleven capabilities" or "11 capabilities"); number words accepted.
  expected    the greatest round named by the SCORECARD's own references to the
              canonical list: `Mirror of the round-N canonical capability list` and
              `the round-N canonical capability list stays canonical`.
  mirror      the first four-column table inside `## Capabilities` (the head mirror).
  firsts      the integer vector in `capability first-working rounds <list>`.
  exists(p)   `git cat-file -e tip:p` at --tip, else os.path.exists.
  literal     a token of a capability cell matching `--flag`, an ALL_CAPS identifier, a
              compound identifier (`a.b`, `a/b`, `a_b`, `a-b`), or a hyphen compound.
  found(lit)  every alphanumeric part of `lit` occurs case-insensitively in the row's
              evidence text.  (No head-final tolerance: a part that is absent is absent.)
  phrase      six consecutive normalised words of the capability cell occur verbatim in
              the evidence text - the leg that binds prose-described rows whose only
              distinctive literal is inflected (`per-run` vs "a run's digest").
  bound       a row with a found literal or a found phrase.
  mirror_cells for each canonical name, the head-mirror row must carry the same
              capability, evidence and first-working-round cells (a mirror is a mirror).

Facts (each failed item adds 1 to its counter):
  present     a marker exists.
  shape       ctable exists with >=1 body row.
  generation  gen == expected.
  count       stated == len(ctable body rows).
  mirror      mirror names == canonical names (both directions), names unique.
  mirror_cells every canonical row's three value cells equal its head-mirror row's.
  firsts      sorted(first-working round ints) == sorted(firsts vector).
  evidence    every backticked path token of every row exists; every row has >=1.
  content     every row is `bound` (evidence and content coverage reported as
              `evidence=<present>/<rows>` and `content=<bound>/<checked>`).
  missing     no name of any other capability table is absent from the canonical table.
  monotonic   every older canonical generation's names are contained in the newest.
  witness     with --witness-tip: newest canonical names at the witness are contained
              in the newest canonical names at --tip.

mismatches = present + shape + generation + count + mirror + mirror_cells + firsts +
             evidence + content + missing + monotonic + witness;  met = mismatches == 0.

Output: `tip=...`, one summary line, then `detail:` lines.  Exit 0 met, 1 not met,
2 could not evaluate.  Read-only on --repo.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

MARKER_RE = re.compile(r"canonical list as of round\s+(\d+)\*\*", re.I)
MIRROR_RE = re.compile(r"Mirror of the round-(\d+) canonical capability list", re.I)
STAYS_RE = re.compile(r"the round-(\d+) canonical capability list stays canonical", re.I)
FIRSTS_RE = re.compile(r"capability first-working rounds\s+([0-9][0-9,\s]*)", re.I)
COUNT_RE = re.compile(r"\b(\w+)\s+capabilities\b", re.I)
PATH_RE = re.compile(r"`([^`]+)`")
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
         "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
         "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
         "eighteen": 18, "nineteen": 19, "twenty": 20}
SIG_RES = (re.compile(r"--[a-z0-9][a-z0-9-]{2,}"),
           re.compile(r"\b[A-Z][A-Z0-9_]{2,}\b"),
           re.compile(r"\b[a-z0-9]+(?:[._/-][a-z0-9]+)+\b"),
           re.compile(r"\b[a-z]{2,}-[a-z0-9]{2,}\b"))


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    return p.returncode, p.stdout, p.stderr.decode(errors="replace").strip()


def read_at(repo, tip, path):
    if tip:
        rc, out, _ = git(repo, "show", "%s:%s" % (tip, path))
        return out.decode("utf-8", "replace") if rc == 0 else None
    full = os.path.join(repo, path)
    if not os.path.isfile(full):
        return None
    with open(full, encoding="utf-8", errors="replace") as f:
        return f.read()


def exists(repo, tip, path):
    if tip:
        return git(repo, "cat-file", "-e", "%s:%s" % (tip, path.rstrip("/")))[0] == 0
    return os.path.exists(os.path.join(repo, path))


def rev(repo, tip):
    if not tip:
        return "worktree"
    rc, out, _ = git(repo, "rev-parse", "--verify", "%s^{commit}" % tip)
    if rc != 0:
        raise RuntimeError("cannot resolve tip %r" % tip)
    return out.decode().strip()


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def table_from(lines, start):
    """(header cells, body rows) for the first markdown table at/after index start."""
    i = start
    n = len(lines)
    while i < n and not lines[i].lstrip().startswith("|"):
        i += 1
    if i >= n:
        return None, []
    block = []
    while i < n and lines[i].lstrip().startswith("|"):
        block.append(cells(lines[i]))
        i += 1
    if len(block) < 2:
        return block[0] if block else None, []
    hdr = block[0]
    body = [r for r in block[2:]] if all(re.fullmatch(r":?-{2,}:?", c) for c in block[1]) else block[1:]
    return hdr, [r for r in body if any(c for c in r)]


def is_cap_hdr(hdr):
    return bool(hdr) and len(hdr) == 4 and re.search(r"first.working round", hdr[3], re.I)


def name_of(row):
    return (row[0] if row else "").strip().strip("`").strip()


def markers(lines):
    return [(int(m.group(1)), i) for i, l in enumerate(lines)
            for m in [MARKER_RE.search(l)] if m]


def canon_at(lines):
    """(gen, body rows) for the newest canonical table, or (None, [])."""
    ms = markers(lines)
    if not ms:
        return None, []
    best = max(ms, key=lambda t: t[0])
    hdr, body = table_from(lines, best[1] + 1)
    if not is_cap_hdr(hdr):
        return best[0], []
    return best[0], body


def section(lines, heading):
    """Body lines of the first line equal to `## <heading>`."""
    for i, l in enumerate(lines):
        if l.strip() == "## " + heading:
            out = []
            for l2 in lines[i + 1:]:
                if l2.startswith("## "):
                    break
                out.append(l2)
            return out
    return []


def literals(text):
    out = set()
    for r in SIG_RES:
        out |= set(r.findall(text))
    return sorted(t for t in out if t not in ("--",))


def parts(lit):
    return [p for p in re.split(r"[._/-]+", lit) if p]


def found(lit, low):
    """A literal binds when every alphanumeric part occurs in the evidence text."""
    ps = parts(lit)
    return bool(ps) and all(p.lower() in low for p in ps)


def tokens(text):
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).split()


def phrase_bound(cap, text, width=6):
    """The cell binds when a >=width-word run of it occurs verbatim in the evidence."""
    cw, tw = tokens(cap), " ".join(tokens(text))
    if len(cw) < width:
        return False
    return any(" ".join(cw[i:i + width]) in tw for i in range(len(cw) - width + 1))


def audit(repo, tip, witness_tip, witness_dir):
    lines = (read_at(repo, tip, "SCORECARD.md") or "").split("\n")
    d = []
    c = dict(present=0, shape=0, generation=0, count=0, mirror=0, mirror_cells=0,
             firsts=0, evidence=0, content=0, missing=0, monotonic=0, witness=0)

    def bad(k, msg):
        c[k] += 1
        d.append("detail: %s: %s" % (k, msg))

    ms = markers(lines)
    if not ms:
        bad("present", "no '**Capabilities - canonical list as of round N**' marker")
    gen, body = canon_at(lines)
    if gen is None:
        d.append("detail: shape: no canonical marker to shape-check")
    elif not body:
        bad("shape", "marker round %d has no four-column table with a First-working round column" % gen)

    # expected generation from the SCORECARD's own references
    exp = [int(m.group(1)) for l in lines for m in [MIRROR_RE.search(l)] if m]
    exp += [int(m.group(1)) for l in lines for m in [STAYS_RE.search(l)] if m]
    expected = max(exp) if exp else None
    if expected is None:
        bad("generation", "SCORECARD names no canonical generation to bind against")
    elif gen != expected:
        bad("generation", "canonical table is round %s; SCORECARD's own references name round %d"
            % (gen, expected))

    # stated cardinal in the prose between the marker and the table
    stated = None
    if gen is not None:
        mi = [i for n, i in ms if n == gen][0]
        hi = mi + 1
        while hi < len(lines) and not lines[hi].lstrip().startswith("|"):
            for m in COUNT_RE.finditer(lines[hi]):
                w = m.group(1).lower()
                stated = WORDS.get(w) if w in WORDS else (int(w) if w.isdigit() else None)
            hi += 1
        if stated is None:
            bad("count", "no '<n> capabilities' cardinal in the prose after the round-%d marker" % gen)
        elif stated != len(body):
            bad("count", "prose states %d capabilities; table carries %d rows" % (stated, len(body)))

    names = [name_of(r) for r in body if name_of(r)]
    if len(names) != len(set(names)):
        bad("mirror", "duplicate capability names in the canonical table: %s" % names)

    # head mirror table inside `## Capabilities`
    mhdr, mbody = table_from(section(lines, "Capabilities"), 0)
    if not is_cap_hdr(mhdr):
        bad("mirror", "no four-column capability table inside '## Capabilities'")
    else:
        mnames = [name_of(r) for r in mbody if name_of(r)]
        if sorted(mnames) != sorted(names):
            only_c = sorted(set(names) - set(mnames))
            only_m = sorted(set(mnames) - set(names))
            bad("mirror", "head mirror != canonical (canonical-only %s; mirror-only %s)"
                % (only_c, only_m))
        # a mirror is a mirror: every canonical row's three value cells must match
        mrow = {name_of(r): r for r in mbody if name_of(r)}
        for r in body:
            nm = name_of(r)
            other = mrow.get(nm)
            if other is None:
                continue
            for k, label in ((1, "capability"), (2, "evidence"), (3, "first-round")):
                if k < len(r) and k < len(other) and r[k] != other[k]:
                    if k == 2:
                        def paths(cell):
                            return {t for t in PATH_RE.findall(cell) if "/" in t}
                        lost = sorted(paths(r[2]) - paths(other[2]))
                        extra = sorted(paths(other[2]) - paths(r[2]))
                        bad("mirror_cells",
                            "%s: head mirror evidence cell is not the canonical cell "
                            "(canonical-only pointers %s; mirror-only pointers %s)"
                            % (nm, lost, extra))
                    else:
                        bad("mirror_cells", "%s: head mirror %s cell differs from canonical"
                            % (nm, label))

    # first-working-round vector from the Saturation section
    sat = "\n".join(section(lines, "Saturation"))
    fm = FIRSTS_RE.search(sat)
    if not fm:
        bad("firsts", "Saturation states no 'capability first-working rounds' vector")
    else:
        want = [int(x) for x in re.findall(r"\d+", fm.group(1))]
        got = []
        for r in body:
            if len(r) >= 4 and re.findall(r"\d+", r[3]):
                got.append(int(re.findall(r"\d+", r[3])[-1]))
        if sorted(got) != sorted(want) or len(got) != len(body):
            bad("firsts", "row first-working rounds %s != Saturation vector %s (rows %d)"
                % (sorted(got), sorted(want), len(body)))

    # evidence existence + content binding
    ev_ok = ev_n = ct_ok = ct_n = 0
    for r in body:
        ev_n += 1
        nm = name_of(r)
        ev = r[2] if len(r) > 2 else ""
        cap = r[1] if len(r) > 1 else ""
        toks = [t for t in PATH_RE.findall(ev) if "/" in t and not t.startswith(("/", "~"))]
        if not toks:
            bad("evidence", "%s: evidence cell names no path token" % nm)
            continue
        missing = [t for t in toks if not exists(repo, tip, t)]
        if missing:
            bad("evidence", "%s: evidence path(s) absent at tip: %s" % (nm, missing))
            continue
        ev_ok += 1
        ct_n += 1
        text = "".join((read_at(repo, tip, t) or "") for t in toks)
        low = text.lower()
        sigs = literals(cap)
        if not sigs:
            bad("content", "%s: capability cell names no distinctive literal" % nm)
            continue
        hit = [s for s in sigs if found(s, low)]
        if not hit and not phrase_bound(cap, text):
            bad("content", "%s: no declared literal of the capability cell occurs in %s "
                "and no six-word run of the cell occurs there (tested %s)"
                % (nm, toks, sigs[:6]))
        else:
            ct_ok += 1

    # omission: any capability table anywhere names a row the canonical table lacks
    all_names = set()
    idx = 0
    while idx < len(lines):
        if lines[idx].lstrip().startswith("|"):
            h, b = table_from(lines, idx)
            if is_cap_hdr(h):
                all_names |= {name_of(r) for r in b if name_of(r)}
            idx += 1 + len(b) + 1
        else:
            idx += 1
    absent = sorted(all_names - set(names))
    if absent:
        bad("missing", "capability tables name rows the newest canonical table lacks: %s" % absent)

    # monotonic canonical lineage
    gens = sorted({n: i for n, i in markers(lines)}.items())
    prev = None
    for n, i in gens:
        h, b = table_from(lines, i + 1)
        if not is_cap_hdr(h):
            if n == gen:
                pass
            continue
        cur = {name_of(r) for r in b if name_of(r)}
        if prev is not None and not prev[1] <= cur:
            bad("monotonic", "canonical round %d drops row(s) held at round %d: %s"
                % (n, prev[0], sorted(prev[1] - cur)))
        prev = (n, cur)

    # witness: newest canonical names at an earlier revision must survive at --tip
    if witness_tip or witness_dir:
        if witness_tip:
            wlines = (read_at(repo, witness_tip, "SCORECARD.md") or "").split("\n")
            wlabel = witness_tip
        else:
            wlines = (read_at(os.path.abspath(witness_dir), None, "SCORECARD.md") or "").split("\n")
            wlabel = os.path.abspath(witness_dir)
        wgen, wbody = canon_at(wlines)
        wnames = {name_of(r) for r in wbody if name_of(r)}
        if not wnames:
            bad("witness", "witness %s has no canonical capability table" % wlabel)
        else:
            lost = sorted(wnames - set(names))
            if lost:
                bad("witness", "rows held at witness (%s, round %s) are absent at tip: %s"
                    % (wlabel, wgen, lost))

    mism = sum(c.values())
    return c, mism, d, gen, expected, stated, len(body), (ev_ok, ev_n, ct_ok, ct_n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--tip", default=None, help="commit to audit; omit for the worktree")
    ap.add_argument("--witness-tip", default=None, help="earlier commit whose canonical rows must survive")
    ap.add_argument("--witness-dir", default=None, help="worktree whose canonical rows must survive")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    repo = os.path.abspath(a.repo)
    try:
        tip = rev(repo, a.tip)
        witness = rev(repo, a.witness_tip) if a.witness_tip else None
        c, mism, d, gen, expected, stated, rows, counts = audit(
            repo, tip if a.tip else None, witness, a.witness_dir)
    except (RuntimeError, ValueError) as e:
        print("could-not-evaluate: %s" % e, file=sys.stderr)
        return 2
    met = mism == 0
    wit = "na" if not (a.witness_tip or a.witness_dir) else str(c["witness"])
    line = ("rows=%d stated=%s gen=%s expected=%s fail_present=%d fail_shape=%d "
            "fail_generation=%d fail_count=%d fail_mirror_names=%d fail_mirror_cells=%d "
            "fail_firsts=%d fail_evidence=%d evidence=%d/%d content=%d/%d fail_missing=%d "
            "fail_monotonic=%d fail_witness=%s mismatches=%d met=%s"
            % (rows, stated, gen, expected, c["present"], c["shape"], c["generation"],
               c["count"], c["mirror"], c["mirror_cells"], c["firsts"], c["evidence"],
               counts[0], counts[1], counts[2], counts[3], c["missing"], c["monotonic"],
               wit, mism, met))
    out = "\n".join(["tip=%s" % tip, line, *d]) + "\n"
    sys.stdout.write(out)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(out)
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
