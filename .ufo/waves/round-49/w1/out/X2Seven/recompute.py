#!/usr/bin/env python3
"""X2Seven independent per-line recomputation of the append-only carve-out.

Reads only git plumbing; does not import tools/append-only-audit.py. For each named
event commit and file it lists every deleted line with:
  parent section (from the parent blob), origin (first commit whose blob holds the
  exact line, and the ## titles holding it there), whether the origin intersects the
  contract's exempt titles for that file, v3/v4 ungraded verdicts, and the number of
  byte-exact holdings of the line at each watched revision.
"""
import collections, json, re, subprocess, sys

LANE = sys.argv[1]
TIP = sys.argv[2]
OUT = sys.argv[3]
EVENTS = [("0718b6abbda6afa6b0ce586f46739fbb92c7cf9c", "SCORECARD.md"),
          ("dd9f5dc6c0e63d038bdd070094d7f38290eeee1b", "SCORECARD.md")]
WATCH = ["82b5e9d33a19734a1f33985acabe7021593e9199",
         "74558c71c38ceaeace15fd4cf8aa9d84977584b1"]


def git(*a, inp=None):
    p = subprocess.run(["git", "-C", LANE, *a], input=inp, capture_output=True)
    if p.returncode != 0:
        raise SystemExit(f"git {' '.join(a)}: {p.returncode} {p.stderr[:300]!r}")
    return p.stdout


def blob(rev, path):
    p = subprocess.run(["git", "-C", LANE, "cat-file", "blob", f"{rev}:{path}"], capture_output=True)
    return p.stdout if p.returncode == 0 else None


def split_lines(data):
    s = data.split(b"\n")
    if s and s[-1] == b"":
        s.pop()
    return s


def sec_titles(lines):
    out, t = [], None
    for ln in lines:
        if ln.startswith(b"## "):
            t = ln.rstrip(b"\r").decode("utf-8", "replace").rstrip()
        out.append(t)
    return out


def sections_of(lines):
    """ordered [(title, [line bytes])] in file order, title None for the preamble"""
    out = []
    cur = None
    for ln, t in zip(lines, sec_titles(lines)):
        if out and out[-1][0] == t:
            out[-1][1].append(ln)
        else:
            out.append((t, [ln]))
    return out


def contract_rows(rev):
    rows = []
    for ln in git("show", f"{rev}:registry/append-only-contract.tsv").decode().split("\n")[1:]:
        if ln.strip():
            c = [x.strip() for x in ln.split("\t")]
            rows.append(dict(path=c[0], rule=c[1], declared_at=c[2], region=c[3], note=c[4]))
    return rows


def deleted(repo, parent, commit, path):
    raw = git("diff", "--no-renames", "--no-color", "--no-ext-diff", "-U0", "--text", parent, commit, "--", path)
    out, ls, i = [], raw.split(b"\n"), 0
    hunk = re.compile(rb"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
    while i < len(ls):
        m = hunk.match(ls[i]); i += 1
        if not m:
            continue
        st = int(m.group(1)); nd = int(m.group(2)) if m.group(2) is not None else 1
        na = int(m.group(4)) if m.group(4) is not None else 1
        gd = ga = 0
        while i < len(ls) and (gd < nd or ga < na):
            if ls[i].startswith(b"-") and gd < nd:
                out.append((st + gd, ls[i][1:])); gd += 1
            elif ls[i].startswith(b"+") and ga < na:
                ga += 1
            i += 1
    return out


order = git("rev-list", "--topo-order", "--reverse", "--parents", TIP).decode().split("\n")
commits, parents = [], {}
for ln in order:
    p = ln.split()
    if p:
        commits.append(p[0]); parents[p[0]] = p[1] if len(p) > 1 else None

rows = contract_rows(TIP)
prev = git("show", f"{TIP}:prev-ignore-me") if False else None
exempt_by_file = {}
for r in rows:
    m = re.fullmatch(r"exempt=(.+)@[^@:]+:\d+", r["region"])
    if m:
        exempt_by_file.setdefault(r["path"], set()).update(t.strip() for t in m.group(1).split("|") if t.strip())

res = {"tip": git("rev-parse", "--verify", TIP + "^{commit}").decode().strip(),
       "commits": len(commits), "exempt_titles": {k: sorted(v, key=str) for k, v in exempt_by_file.items()},
       "events": []}

origin_by_file = {}


def origins(path):
    if path in origin_by_file:
        return origin_by_file[path]
    orig, first_c, seen = {}, {}, set()
    specs = "\n".join(f"{c}:{path}" for c in commits) + "\n"
    chk = git("cat-file", "--batch-check=%(objectname) %(objecttype)", inp=specs.encode()).decode().split("\n")
    blobs = []
    for c, line in zip(commits, chk):
        parts = line.split()
        blobs.append((c, parts[0] if len(parts) == 2 and parts[1] == "blob" else None))
    for c, b in blobs:
        if b is None or b in seen:
            continue
        seen.add(b)
        body = split_lines(git("cat-file", "blob", b))
        # v4 first-appearance rule: every title the text holds in the FIRST blob that
        # contains it (all occurrences in that blob, before orig is updated).
        fresh = collections.defaultdict(set)
        for ln, t in zip(body, sec_titles(body)):
            if ln not in orig:
                fresh[ln].add(t)
        for ln, ts in fresh.items():
            orig[ln] = ts; first_c[ln] = c
    origin_by_file[path] = (orig, first_c)
    return orig, first_c


for commit, path in EVENTS:
    par = parents[commit]
    ex = set(exempt_by_file.get(path, ()))
    pb = blob(par, path)
    body = split_lines(pb)
    psec = sec_titles(body)
    # v3 eligibility: window max section count >= parent section count
    pcount = collections.Counter(t for t in psec)
    window = commits[commits.index(commit):]
    best = collections.Counter()
    for x in window:
        b = blob(x, path)
        if b is None:
            continue
        c = collections.Counter(sec_titles(split_lines(b)))
        for t in set(c) | set(best):
            best[t] = max(best[t], c[t])
    eligible = {t for t in ex if best[t] >= pcount[t]}
    org, first_c = origins(path)
    dl = deleted(LANE, par, commit, path)
    holds = {}
    for w in WATCH:
        wb = blob(w, path)
        wl = split_lines(wb) if wb is not None else []
        holds[w] = collections.Counter(wl)
    children = [c for c in commits if parents.get(c) == commit]
    ev = {"commit": commit, "file": path, "parent": par, "deleted": len(dl),
          "children": children, "sections_eligible": sorted(eligible, key=str),
          "sections_ineligible": sorted(ex - eligible, key=str),
          "section_parent_counts": {t: pcount[t] for t in sorted(ex)},
          "lines": []}
    for pos, text in dl:
        s = psec[pos - 1]
        o = org.get(text)
        ev["lines"].append({
            "pos": pos,
            "text": text.decode("utf-8", "replace"),
            "parent_section": s,
            "parent_section_exempt": s in ex,
            "parent_section_eligible": s in eligible,
            "origin_commit": first_c.get(text),
            "origin_sections": sorted(o, key=str) if o else None,
            "origin_exempt": bool(o) and bool(o & ex),
            "held": {w: holds[w][text] for w in WATCH},
        })
    res["events"].append(ev)

with open(OUT, "w") as fh:
    json.dump(res, fh, indent=1, sort_keys=False)
print("wrote", OUT)
