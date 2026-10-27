#!/usr/bin/env python3
"""regen-cited-paths.py - seat X8Regen's INDEPENDENT recomputation of the kama
round-53 C2 cited-path misses.

Written from the claim text (round-53 preregistration, claim C2) and the seat
assignment, not from tools/round53-cited-path-check.py.  The counter is imported
only in the `--compare` step, to read its own verdict for the same revision.

Parser rules (R1-R9), stated so the result can be audited:
  R1 surfaces   SCORECARD.md, SHONEN.md, SKILL.md of --repo at --tip, read through
                `git show <tip>:<surface>` (working tree never touched).
  R2 fences     a line whose lstrip() starts with ``` toggles a fence; fenced lines
                yield no citations.  An unterminated fence swallows the rest of the
                file (reported as `unterminated-fence:<surface>:<line>`).
  R3 spans      every `...` span on a non-fenced line, at most one line long, is a
                candidate.  A line may hold several spans; each is checked.
  R4 clean      strip whitespace; drop one leading "./"; drop trailing ",;" ; cut a
                "#fragment"; cut a trailing line anchor `:N`, `:N-M`, `:N,M`
                (digits, '-' and ',' only) and remember its largest number.
  R5 path-like  after R4 the text must be non-empty, contain none of ` \t<>$=()|'"`
                and either start with a lane root (.ufo/ tools/ tests/ corpus/
                registry/ plans/ considerthese/), start with a fleet root
                (scripts/ templates/), or equal one of the lane's top-level files.
  R6 braces     `{a,b}` expands (recursively); the citation misses when ANY
                expansion misses.
  R7 range      additionally (the counter does not do this) a `M01..11` / `1..3`
                numeric range expands with zero padding preserved; ranges are
                checked separately from the literal token and reported.
  R8 resolve    a candidate resolves against a tree (git ls-tree -r --name-only)
                when: a glob (* ? [) matches with fnmatch; else it ends in "/" and
                some path starts with it; else it is a path; else some path starts
                with it + "/" (implicit directory).  The lane tree is tried first,
                then the fleet tree; the first tree that matches wins.
  R9 eof        a candidate that resolved to a plain file and carried an anchor
                misses as `beyond-eof` when the blob has fewer lines than the
                anchor's largest number.

Misses are raw: no ledger is consulted.  A citation is a miss when its token does
not resolve in either tree (any failing brace expansion makes it a miss).

Two advisory channels look for citation forms R5 rejects:
  A `loose`   path-like runs on non-fenced lines with every backtick span blanked
              out (prose pointers outside backticks).
  B `skipped` spans R5 rejected because of syntax characters, with the embedded
              root-path substring tested on its own.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys

SURFACES = ("SCORECARD.md", "SHONEN.md", "SKILL.md")
LANE_ROOTS = (".ufo/", "tools/", "tests/", "corpus/", "registry/", "plans/", "considerthese/")
FLEET_ROOTS = ("scripts/", "templates/")
TOP = ("AGENTS.md", "LOG.md", "MINT.md", "PROVINCE.md", "README.md", "SCORECARD.md",
       "SHONEN.md", "SKILL.md")
SYNTAX = set(" \t<>$=()|'\"")
ANCHOR = re.compile(r"^(.*?):(\d+(?:[-,]\d+)*)$")
GLOBCH = "*?["
ROOTPATH = re.compile(r"(?:\.ufo|tools|tests|corpus|registry|plans|considerthese|scripts|templates)/[^\s`'\"<>()\[\]]*")


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if p.returncode != 0:
        raise SystemExit(f"git {' '.join(args)[:120]}: {p.stderr.decode('utf-8', 'replace')[:200]}")
    return p.stdout


def tree_set(repo, rev):
    out = git(repo, "ls-tree", "-r", "--name-only", "-z", rev).decode("utf-8", "replace")
    return set(p for p in out.split("\0") if p)


def blob(repo, rev, path):
    p = subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"], capture_output=True)
    return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else None


def nlines(repo, rev, path):
    text = blob(repo, rev, path)
    if text is None:
        return None
    return len(text.split("\n")) - (1 if text.endswith("\n") else 0)


def clean(raw):
    s = raw.strip()
    if s.startswith("./"):
        s = s[2:]
    s = s.rstrip(",;")
    s = s.split("#", 1)[0]
    lo = hi = None
    m = ANCHOR.match(s)
    if m:
        nums = [int(x) for x in re.split(r"[-,]", m.group(2))]
        s, lo, hi = m.group(1), min(nums), max(nums)
    return s, lo, hi


def pathlike(s):
    return bool(s) and not (set(s) & SYNTAX) and (
        s.startswith(LANE_ROOTS) or s.startswith(FLEET_ROOTS) or s in TOP)


def expand_braces(s):
    m = re.search(r"\{([^{}]*)\}", s)
    if not m:
        return [s]
    out = []
    for alt in m.group(1).split(","):
        out.extend(expand_braces(s[:m.start()] + alt + s[m.end():]))
    return out


def expand_ranges(s):
    """Zero-padded numeric ranges: M01..11 -> M01..M11; only when both ends are ints."""
    m = re.search(r"([A-Za-z_]*)(\d+)\.\.(\d+)", s)
    if not m:
        return [s]
    a, b = int(m.group(2)), int(m.group(3))
    if b < a or b - a > 200:
        return [s]
    width = len(m.group(2))
    outs = []
    for n in range(a, b + 1):
        outs.extend(expand_ranges(s[:m.start()] + m.group(1) + str(n).zfill(width) + s[m.end():]))
    return outs


def resolve_one(cand, tset):
    if set(cand) & set(GLOBCH):
        return ("ok", "glob") if any(fnmatch.fnmatchcase(p, cand) for p in tset) else ("missing", "glob")
    if cand.endswith("/"):
        return ("ok", "dir") if any(p.startswith(cand) for p in tset) else ("missing", "dir")
    if cand in tset:
        return ("ok", "file")
    if any(p.startswith(cand + "/") for p in tset):
        return ("ok", "dir")
    return ("missing", "none")


def check(core, lo, hi, trees):
    """[(expansion, verdict, how, repo)]; verdict ok | missing | beyond-eof."""
    res = []
    for e in expand_braces(core):
        got = None
        for name, repo, tset, rev in trees:
            v, how = resolve_one(e, tset)
            if v == "ok":
                if hi is not None and how == "file" and e in tset:
                    n = nlines(repo, rev, e)
                    if n is None or n < max(lo, hi):
                        res.append((e, "beyond-eof", f"{n} lines", name))
                        got = True
                        break
                res.append((e, "ok", how, name))
                got = True
                break
        if not got:
            res.append((e, "missing", "none", "-"))
    return res


def citations(text):
    """(line, raw_span, core, lo, hi) plus rejected spans and fence notes."""
    out, rejected, notes = [], [], []
    fenced, fence_line = False, None
    for n, line in enumerate(text.split("\n"), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            fence_line = n if fenced else None
            continue
        if fenced:
            continue
        for span in re.findall(r"`([^`\n]*)`", line):
            core, lo, hi = clean(span)
            if pathlike(core):
                out.append((n, span.strip(), core, lo, hi))
            elif span.strip():
                rejected.append((n, span.strip(), core))
    if fenced:
        notes.append(f"unterminated-fence at line {fence_line}")
    return out, rejected, notes


def survey(repo, rev, fleet, fleet_rev):
    trees = [("lane", repo, tree_set(repo, rev), rev)]
    if fleet:
        trees.append(("fleet", fleet, tree_set(fleet, fleet_rev), fleet_rev))
    src = {s: blob(repo, rev, s) for s in SURFACES}
    cites, misses, rejected_all, notes_all = {}, {}, [], {}
    for surf in SURFACES:
        text = src[surf]
        cites[surf], misses[surf] = {}, {}
        if text is None:
            notes_all[surf] = [f"missing surface {surf}"]
            continue
        cs, rej, notes = citations(text)
        notes_all[surf] = notes
        for n, tok, core, lo, hi in cs:
            r = check(core, lo, hi, trees)
            cites[surf].setdefault(tok, []).append((n, r))
            if any(v != "ok" for _e, v, _h, _w in r):
                misses[surf].setdefault(tok, []).append((n, core, r))
        for n, tok, core in rej:
            for sub in ROOTPATH.findall(tok):
                c2, lo2, hi2 = clean(sub)
                if pathlike(c2):
                    rejected_all.append((surf, n, tok, c2, check(c2, lo2, hi2, trees)))
    return cites, misses, rejected_all, notes_all, trees


def loose_scan(text, trees, surf, repo_rev_pairs):
    """Path-like runs outside backticks on non-fenced lines."""
    out = []
    fenced = False
    for n, line in enumerate(text.split("\n"), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        masked = re.sub(r"`[^`\n]*`", lambda m: " " * len(m.group(0)), line)
        for sub in ROOTPATH.findall(masked):
            core, lo, hi = clean(sub)
            if pathlike(core):
                out.append((surf, n, core, check(core, lo, hi, trees)))
    return out


def counter_set(counter_path, lane_repo, tip, fleet, fleet_rev):
    """The counter's own unresolved set, imported read-only for comparison."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("r53c2", counter_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    lane = mod.Repo(lane_repo, tip)
    fl = mod.Repo(fleet, fleet_rev) if fleet else None
    _cited, unres = mod.survey(lane, fl)
    return {(s, t): [(e, v) for e, v in bad] for s, d in unres.items() for t, bad in d.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--base", default=None)
    ap.add_argument("--fleet", default=None)
    ap.add_argument("--fleet-rev", default="HEAD")
    ap.add_argument("--fleet-rev-secondary", default=None)
    ap.add_argument("--counter", default=None)
    ap.add_argument("--counter-fleet-rev", default=None)
    ap.add_argument("--json-out", default=None)
    ap.add_argument("--channels-out", default=None)
    a = ap.parse_args()
    fleet = a.fleet or None
    frev = a.fleet_rev
    cites, misses, rejected, notes, trees = survey(a.repo, a.tip, fleet, frev)
    n_cited = sum(len(v) for v in cites.values())
    n_miss = sum(len(v) for v in misses.values())
    print(f"tip={a.tip} fleet={frev} cited_tokens={n_cited} miss_tokens={n_miss}")
    for surf in SURFACES:
        for tok, occ in misses[surf].items():
            print(f"miss {surf} `{tok}` lines={[o[0] for o in occ]} "
                  f"detail={occ[0][2]}")
    loose = []
    for surf in SURFACES:
        loose.extend(loose_scan(blob(a.repo, a.tip, surf) or "", trees, surf, None))
    for surf, n, tok, sub, r in rejected:
        dead = any(v != "ok" for _e, v, _h, _w in r)
        print(f"{'skipped-dead' if dead else 'skipped-ok'} {surf}:{n} span=`{tok}` "
              f"embedded=`{sub}` -> {r}")
    for surf, n, core, r in loose:
        dead = any(v != "ok" for _e, v, _h, _w in r)
        print(f"{'loose-dead' if dead else 'loose-ok'} {surf}:{n} `{core}` -> {r}")
    if a.channels_out:
        with open(a.channels_out, "w") as fh:
            fh.write(f"# independent parser channels at tip={a.tip} fleet={frev}\n")
            fh.write(f"# A: spans outside fences with syntax characters (space/paren/<>/...), "
                     f"{len(rejected)} embedded candidates\n")
            for surf, n, tok, sub, r in rejected:
                fh.write(f"skipped {surf}:{n} span=`{tok}` embedded=`{sub}` -> {r}\n")
            fh.write(f"# B: path-like runs outside backticks, {len(loose)} candidates\n")
            for surf, n, core, r in loose:
                fh.write(f"loose {surf}:{n} `{core}` -> {r}\n")

    payload = {"tip": a.tip, "fleet": frev, "lane": a.repo,
               "cited_tokens": n_cited, "miss_tokens": n_miss,
               "misses": {s: {t: [[o[0], o[2]] for o in v] for t, v in d.items()}
                          for s, d in misses.items()},
               "notes": notes,
               "rejected_dead": [[s, n, tok, sub, r] for s, n, tok, sub, r in rejected
                                 if any(v != "ok" for _e, v, _h, _w in r)]}

    if a.base:
        bc, bmisses, _r, _n, _t = survey(a.repo, a.base, fleet, frev)
        bkeys = {(s, t) for s, d in bmisses.items() for t in d}
        payload["base"] = a.base
        payload["base_miss_tokens"] = len(bkeys)
        payload["base_misses"] = sorted(f"{s} `{t}`" for s, t in bkeys)
        print(f"base={a.base} base_miss_tokens={len(bkeys)}")
        for s, t in sorted(bkeys):
            print(f"base-miss {s} `{t}`")
        bset = set(bc.get("SCORECARD.md", {}))
        tset = set(cites.get("SCORECARD.md", {}))
        dropped = sorted(bset - tset)
        payload["dropped"] = dropped
        print(f"dropped SCORECARD tokens base->tip: {len(dropped)} {dropped}")
        if a.fleet_rev_secondary:
            _c2, m2, _r2, _n2, _t2 = survey(a.repo, a.tip, fleet, a.fleet_rev_secondary)
            k2 = {(s, t) for s, d in m2.items() for t in d}
            k1 = {(s, t) for s, d in misses.items() for t in d}
            payload["secondary_fleet"] = a.fleet_rev_secondary
            payload["secondary_miss_tokens"] = len(k2)
            print(f"secondary fleet={a.fleet_rev_secondary} miss_tokens={len(k2)}; "
                  f"only-at-primary={sorted(k1 - k2)}; only-at-secondary={sorted(k2 - k1)}")

    if a.counter:
        cfrev = a.counter_fleet_rev or frev
        cset = counter_set(a.counter, a.repo, a.tip, fleet, cfrev)
        mine = {(s, t) for s, d in misses.items() for t in d}
        payload["counter"] = {"path": a.counter, "fleet_rev": cfrev,
                              "unresolved": sorted(f"{s} `{t}`" for s, t in cset),
                              "only_mine": sorted(f"{s} `{t}`" for s, t in mine - set(cset)),
                              "only_counter": sorted(f"{s} `{t}`" for s, t in set(cset) - mine)}
        print(f"counter unresolved={len(cset)} only_mine={sorted(mine - set(cset))} "
              f"only_counter={sorted(set(cset) - mine)}")

    if a.json_out:
        with open(a.json_out, "w") as fh:
            json.dump(payload, fh, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
