#!/usr/bin/env python3
"""indep-c2-probe.py - X7Rerun's independent re-implementation of the C2 citation survey.

Not the frozen counter (tools/round53-cited-path-check.py): written from the counter's
frozen docstring, used only to check that the frozen counter's published counts
(cited / unresolved / dropped) replicate on a second parser.  Read-only.
"""
import fnmatch
import re
import subprocess
import sys

LANE_ROOTS = (".ufo/", "tools/", "tests/", "corpus/", "registry/", "plans/", "considerthese/")
FLEET_ROOTS = ("scripts/", "templates/")
TOP = ("AGENTS.md", "LOG.md", "MINT.md", "PROVINCE.md", "README.md", "SCORECARD.md",
       "SHONEN.md", "SKILL.md")
BAD = set(" <>$=()|'\"")
ANCHOR = re.compile(r"^(.*?):(\d+(?:[-,]\d+)*)$")


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if p.returncode:
        raise SystemExit(f"git {' '.join(args)} failed: {p.stderr.decode()[:200]}")
    return p.stdout.decode("utf-8", "replace")


def show(repo, rev, path):
    p = subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"], capture_output=True)
    return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else None


def tree(repo, rev):
    out = git(repo, "ls-tree", "-r", "--name-only", "-z", rev)
    return set(x for x in out.split("\0") if x)


def expand(token):
    m = re.search(r"\{([^{}]*)\}", token)
    if not m:
        return [token]
    out = []
    for alt in m.group(1).split(","):
        out += expand(token[:m.start()] + alt + token[m.end():])
    return out


def spans(line):
    return re.findall(r"`([^`]+)`", line)


def citations(text):
    """[(line_no, raw_span, token, anchor_numbers)] outside ``` fences."""
    out, fenced = [], False
    for no, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        for raw in spans(line):
            tok = raw.split("#", 1)[0]
            nums = None
            m = ANCHOR.match(tok)
            if m:
                tok = m.group(1)
                nums = [int(x) for x in re.split(r"[,-]", m.group(2)) if x]
            if not tok or any(c in BAD for c in tok):
                continue
            if not (tok.startswith(LANE_ROOTS) or tok.startswith(FLEET_ROOTS) or tok in TOP):
                continue
            out.append((no, raw, tok, nums))
    return out


def hit(path, paths):
    if path.endswith("/") or "*" in path or "?" in path or "[" in path:
        return any(fnmatch.fnmatchcase(p, path.rstrip("/") + "/*") if path.endswith("/")
                   else fnmatch.fnmatchcase(p, path) for p in paths)
    return path in paths or any(p.startswith(path + "/") for p in paths)


def lines_at(repo, rev, path):
    t = show(repo, rev, path)
    return None if t is None else len(t.splitlines())


def survey(repo, rev, fleet, frev, surfaces=("SCORECARD.md", "SHONEN.md", "SKILL.md")):
    lp, fp = tree(repo, rev), tree(fleet, frev)
    cited = 0
    unres = []
    for surface in surfaces:
        text = show(repo, rev, surface)
        if text is None:
            continue
        for no, raw, tok, nums in citations(text):
            for e in expand(tok):
                cited += 1
                if hit(e, lp):
                    if nums and e.endswith("/") is False and not ("*" in e or "?" in e or "[" in e):
                        n = lines_at(repo, rev, e)
                        if n is not None and n < max(nums):
                            unres.append((surface, no, raw, e, "beyond-eof"))
                    continue
                if hit(e, fp):
                    continue
                unres.append((surface, no, raw, e, "missing"))
    return cited, unres


def main():
    repo, tip, fleet, frev = sys.argv[1:5]
    cited, unres = survey(repo, tip, fleet, frev)
    base_tip, base_frev = sys.argv[5], sys.argv[6]
    bcited, bunres = survey(repo, base_tip, fleet, base_frev, surfaces=("SCORECARD.md",))
    t_cited, t_unres = survey(repo, tip, fleet, frev, surfaces=("SCORECARD.md",))
    btoks = set(e for _, _, _, e, _ in bunres)
    print(f"independent: cited={cited} unresolved={len(unres)}")
    print(f"independent: scard@base cited={bcited} unresolved={len(bunres)}; "
          f"scard@tip cited={t_cited} unresolved={len(t_unres)}")
    print(f"scard base unresolved tokens still unresolved at tip: "
          f"{len(btoks & set(e for _, _, _, e, _ in t_unres))}/{len(btoks)}")
    print("per-surface unresolved:")
    for s in ("SCORECARD.md", "SHONEN.md", "SKILL.md"):
        rows = [r for r in unres if r[0] == s]
        print(f"  {s}: {len(rows)}")
        for r in rows:
            print(f"    L{r[1]} {r[3]} [{r[4]}]")


if __name__ == "__main__":
    main()
