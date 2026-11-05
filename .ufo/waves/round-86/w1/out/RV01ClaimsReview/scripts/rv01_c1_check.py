#!/usr/bin/env python3
"""Independent re-derivation of round-86 C1 facts (RV01ClaimsReview). Not the frozen instrument.

Reads committed bytes only (git show / ls-tree / cat-file / merge-base). Optional
--scorecard FILE replaces SCORECARD.md at the graded revision (fixtures only; the repo is never written).
Prints one line per fact plus EXTRA lines for stale closure pointers the frozen predicate does not grade.
"""
import argparse
import re
import subprocess
import sys

DISP = ("rejected-harmed", "rejected-honest-stop", "admitted")
DISP_RE = re.compile(r"\b(rejected-harmed|rejected-honest-stop|admitted)\b")
AUTH_RE = re.compile(r"^\*\*Current authority \(round (\d+)\):\*\*")
ROW_RE = re.compile(r"^\|\s*calibration\s*\|")
TOKEN_RE = re.compile(r"`(PRE_REPORT round=(\d+) arms=\d+ failed=\d+ uncommitted=\d+)`")
CMD_RE = re.compile(r"`(python3 tools/pre-report-gate\.py[^`]*)`")
OUT_RE = re.compile(r"`([^`\s]+\.out)`")
HEX_RE = re.compile(r"`([0-9a-f]{40})`")
CLOSURE_RE = re.compile(r"corpus/lessons/round-(\d+)-verifier-spotcheck\.md")
RECEIPT_LINE_RE = re.compile(r"^PRE_REPORT round=(\d+) arms=\d+ failed=\d+ uncommitted=\d+$")


def git(repo, *args, text=True):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=text)


def show(repo, rev, path):
    r = git(repo, "show", f"{rev}:{path}")
    return r.stdout if r.returncode == 0 else None


def rendered_lines(text):
    """Drop HTML comments, then fenced blocks (CommonMark: backtick info may not hold a backtick)."""
    t = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    if "<!--" in t:  # unclosed comment runs to EOF
        t = t[: t.index("<!--")]
    out, fence = [], None
    for line in t.split("\n"):
        if fence is not None:
            m = re.match(r"^ {0,3}(`{3,}|~{3,})[ \t]*$", line)
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= fence[1]:
                fence = None
            continue
        m = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if m:
            if m.group(1)[0] == "`" and "`" in m.group(2):
                out.append(line)  # inline code span, not a fence opener
                continue
            fence = (m.group(1)[0], len(m.group(1)))
            continue
        out.append(line)
    return out


def select(lines):
    auth, row, in_axes = None, None, False
    for line in lines:
        if line.startswith("## "):
            in_axes = line.rstrip() == "## Axes"
            continue
        if auth is None and AUTH_RE.match(line):
            auth = line
        if in_axes and row is None and ROW_RE.match(line):
            row = line
    return auth, row


def newest_receipts(repo, rev):
    """Return (round, sorted paths, set of exact receipt lines) for the highest PRE_REPORT round."""
    r = git(repo, "grep", "-n", "-E", r"^PRE_REPORT round=[0-9]+ arms=[0-9]+ failed=[0-9]+ uncommitted=[0-9]+$",
            rev, "--", ":(glob).ufo/waves/round-*/measured/**/*.out")
    best, paths, lines = -1, set(), set()
    for raw in r.stdout.splitlines():
        body = raw[len(rev) + 1:]
        path, _, rest = body.partition(":")
        _, _, text = rest.partition(":")
        m = RECEIPT_LINE_RE.match(text)
        if not m:
            continue
        n = int(m.group(1))
        if n > best:
            best, paths, lines = n, {path}, {text}
        elif n == best:
            paths.add(path)
            lines.add(text)
    return best, paths, lines


def newest_closure(repo, rev):
    r = git(repo, "ls-tree", "--name-only", rev, "corpus/lessons/")
    best = (-1, None)
    for p in r.stdout.splitlines():
        m = re.match(r"^corpus/lessons/round-(\d+)-verifier-spotcheck\.md$", p)
        if m and int(m.group(1)) > best[0]:
            best = (int(m.group(1)), p)
    return best


def is_anc(repo, rev, r):
    if r == rev:
        return True
    return git(repo, "merge-base", "--is-ancestor", r, rev).returncode == 0


def grade(repo, rev, scorecard_override=None):
    text = scorecard_override if scorecard_override is not None else show(repo, rev, "SCORECARD.md")
    if text is None:
        return {"error": "no SCORECARD.md"}
    auth, row = select(rendered_lines(text))
    if auth is None or row is None:
        return {"error": f"auth={auth is not None} row={row is not None}"}
    out = {}
    # gate fact
    gnum, gpaths, glines = newest_receipts(repo, rev)
    gate_findings = []
    tok = TOKEN_RE.search(auth)
    if not tok:
        gate_findings.append("no backticked PRE_REPORT token")
    else:
        token, M = tok.group(1), int(tok.group(2))
        if M != gnum:
            gate_findings.append(f"token round {M} != newest receipt round {gnum}")
        cmd = CMD_RE.search(auth)
        cm = re.search(r"--round (\d+)", cmd.group(1)) if cmd else None
        if not cm or int(cm.group(1)) != M:
            gate_findings.append("command round does not name token round")
        named = OUT_RE.findall(auth)
        if not any(p in gpaths for p in named):
            gate_findings.append(f"named receipt not among newest receipts {sorted(gpaths)}")
        coupled = False
        for R in HEX_RE.findall(auth):
            if not is_anc(repo, rev, R):
                continue
            for p in named:
                body = show(repo, R, p)
                if body is not None and token in body.splitlines():
                    coupled = True
        if not coupled:
            gate_findings.append("no revision R (ancestor of graded) whose bytes at R hold the receipt with the exact token")
    out["gate"] = (not gate_findings, gate_findings, gnum)
    # closure + disposition facts
    cnum, cpath = newest_closure(repo, rev)
    cf, df = [], []
    mentions = [(int(m.group(1))) for m in CLOSURE_RE.finditer(row)]
    if not mentions:
        cf.append("row names no closure")
    elif mentions[0] != cnum:
        cf.append(f"primary row closure round-{mentions[0]} != newest round-{cnum}")
    extra = [f"round-{n}" for n in sorted(set(mentions)) if n != cnum]
    body = show(repo, rev, cpath) or ""
    verdict_words = set(re.findall(r"[Vv]erdict[:\s`*]*(rejected-harmed|rejected-honest-stop|admitted)\b", body))
    if len(verdict_words) != 1:
        df.append(f"verdict words on verdict lines: {sorted(verdict_words)}")
    else:
        word = next(iter(verdict_words))
        if not re.search(rf"round{cnum} {re.escape(word)}\b", row):
            df.append(f"row does not name `round{cnum} {word}`")
    out["closure"] = (not cf, cf, cnum)
    out["disposition"] = (not df, df, cnum)
    out["extra_stale_closure_mentions"] = extra
    out["mismatches"] = len(gate_findings) + len(cf) + len(df)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--scorecard", help="fixture SCORECARD text file replacing the rev's SCORECARD.md")
    a = ap.parse_args(argv)
    ov = open(a.scorecard, encoding="utf-8").read() if a.scorecard else None
    res = grade(a.repo, a.rev, ov)
    if "error" in res:
        print(f"RV01 could-not-evaluate {res['error']}")
        return 2
    facts = {k: res[k][0] for k in ("gate", "closure", "disposition")}
    print(f"RV01 rev={a.rev[:10]} gate={int(facts['gate'])} closure={int(facts['closure'])} "
          f"disposition={int(facts['disposition'])} mismatches={res['mismatches']} "
          f"newest_gate={res['gate'][2]} newest_closure={res['closure'][2]} extra={res['extra_stale_closure_mentions']}")
    for k in ("gate", "closure", "disposition"):
        for f in res[k][1]:
            print(f"RV01_FINDING {k} {f}")
    return 0 if res["mismatches"] == 0 and not res["extra_stale_closure_mentions"] else 1


if __name__ == "__main__":
    sys.exit(main())
