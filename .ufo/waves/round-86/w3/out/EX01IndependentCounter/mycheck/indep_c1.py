#!/usr/bin/env python3
"""EX01 independent C1 checker - no import of round86-*.

Renders SCORECARD.md (comment/fence/correction/indent strip), then:
 fact1 gate: first rendered top-level **Current authority (round N):** paragraph must
   name the NEWEST terminal gate receipt (scan .ufo/waves/**/measured/**/*.out at rev),
   with a 40-hex rev, the receipt path, and the exact PRE_REPORT token; rev must be an
   ancestor; receipt bytes AT that rev must contain the token; backticked gate command
   names the token's round.
 fact2 closure: first top-level | calibration | row inside first ## Axes names the
   highest-numbered corpus/lessons/round-<N>-verifier-spotcheck.md.
 fact3 disposition: row names round<N> <word> for the newest closure and <word> occurs
   in the closure body.
"""
import re, subprocess, sys

repo, rev = sys.argv[1], sys.argv[2]
show = lambda p: subprocess.check_output(["git", "-C", repo, "show", f"{rev}:{p}"], text=True,
                                         stderr=subprocess.DEVNULL)
try:
    score = show("SCORECARD.md")
except subprocess.CalledProcessError:
    sys.exit("no SCORECARD.md at rev")

# ---- rendered selection (independent implementation)
CONTAINER = r"(?: {0,3}(?:[-*+]|[0-9]{1,9}[.)])[ \t]+| {0,3}>[ \t]?)*"
FENCE = re.compile(r"^" + CONTAINER + r" {0,3}(`{3,}|~{3,})(.*)$")
FENCE_CLOSE = re.compile(r"^" + CONTAINER + r" {0,3}(`{3,}|~{3,})[ \t]*$")
CORRECTION = re.compile(r"^ {0,3}(#{1,6})\s+round-[0-9]+ correction(?:\s|$)")
HEADING = re.compile(r"^ {0,3}(#{1,6})\s+(.*)$")
lines = score.splitlines()
out, in_comment, fence, depth = [], False, None, None
for line in lines:
    if in_comment:
        if "-->" in line:
            in_comment, line = False, line.split("-->", 1)[1]
        else:
            continue
    if fence is not None:
        c = FENCE_CLOSE.match(line)
        if c and c.group(1)[0] == fence[0] and len(c.group(1)) >= fence[1]:
            fence = None
        continue
    while "<!--" in line:
        b, rest = line.split("<!--", 1)
        if "-->" in rest:
            line = b + rest.split("-->", 1)[1]
        else:
            line, in_comment = b, True
            break
    if not line.strip():
        out.append("")
        continue
    o = FENCE.match(line)
    if o and not (o.group(1)[0] == "`" and "`" in o.group(2)):
        fence = (o.group(1)[0], len(o.group(1)))
        continue
    h = CORRECTION.match(line)
    if h:
        depth = len(h.group(1))
        continue
    if depth is not None:
        oh = HEADING.match(line)
        if oh and len(oh.group(1)) <= depth:
            depth = None
        else:
            continue
    out.append(line)
body = "\n".join(out)

AUTHORITY = re.compile(r"^\*\*Current authority \(round ([0-9]+)\):")
CALIB = re.compile(r"^\|\s*calibration\s*\|")
authority, row, in_axes = None, None, False
for line in body.splitlines():
    if line.startswith("## "):
        in_axes = line.strip() == "## Axes"
        continue
    if authority is None and AUTHORITY.match(line):
        authority = line
        continue
    if in_axes and row is None and CALIB.match(line):
        row = line

print("authority-line:", (authority or "NONE")[:200])
print("calibration-row:", (row or "NONE")[:200])

# ---- population scan, independent
paths = subprocess.check_output(["git", "-C", repo, "ls-tree", "-r", "--name-only", rev],
                                text=True).splitlines()
GATE_LINE = re.compile(r"^PRE_REPORT round=([0-9]+) arms=([0-9]+) failed=([0-9]+) uncommitted=([0-9]+)$", re.M)
best_gate, best_clo = None, None
for p in paths:
    m = re.match(r"^\.ufo/waves/round-[0-9]+/measured/.*\.out$", p)
    if m:
        try:
            text = show(p)
        except subprocess.CalledProcessError:
            continue
        for G in GATE_LINE.finditer(text):
            if best_gate is None or int(G.group(1)) > best_gate[0]:
                best_gate = (int(G.group(1)), p, G.group(0))
    cm = re.match(r"^corpus/lessons/round-([0-9]+)-verifier-spotcheck\.md$", p)
    if cm and (best_clo is None or int(cm.group(1)) > best_clo[0]):
        best_clo = (int(cm.group(1)), p)
print("newest_gate:", best_gate)
print("newest_closure:", best_clo)

facts = {}

# ---- fact gate, independent token parse
tok_re = re.compile(r"`PRE_REPORT round=([0-9]+) arms=([0-9]+) failed=([0-9]+) uncommitted=([0-9]+)`")
cmd_re = re.compile(r"`python3 tools/pre-report-gate\.py[^`]*`")
rev_re = re.compile(r"`([0-9a-f]{40})`")
rec_re = re.compile(r"`([^`]*\.out)`")
tok = tok_re.search(authority or "")
findings = []
if not best_gate:
    facts["gate"] = None
elif not tok:
    findings.append("gate: no PRE_REPORT token in rendered authority cell")
else:
    round_no, rpath, rtoken = best_gate
    if int(tok.group(1)) != round_no:
        findings.append(f"gate: token round={tok.group(1)} != newest receipt round={round_no}")
    else:
        cmd = cmd_re.search(authority or "")
        if not cmd:
            findings.append("gate: no gate command")
        else:
            cr = re.search(r"--round ([0-9]+)", cmd.group(0))
            if not cr or int(cr.group(1)) != round_no:
                findings.append("gate: command round mismatch")
        revs = [m.group(1) for m in rev_re.finditer(authority)]
        recs = [m.group(1) for m in rec_re.finditer(authority)]
        if rpath not in recs:
            findings.append(f"gate: receipt path {rpath} not named in cell (named {recs})")
        coupled = []
        for rv in revs:
            anc = subprocess.run(["git", "-C", repo, "merge-base", "--is-ancestor", rv, rev],
                                 capture_output=True).returncode == 0
            if not anc:
                continue
            try:
                rt = show_path_at(rv, rpath) if False else subprocess.check_output(
                    ["git", "-C", repo, "show", f"{rv}:{rpath}"], text=True,
                    stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                continue
            if rtoken in rt:
                coupled.append(rv)
        if not coupled:
            findings.append("gate: no ancestor rev carries receipt bytes with the exact token")
        else:
            facts["gate_receipt_at"] = sorted(coupled)
    facts["gate"] = not any(f.startswith("gate") for f in findings)

# ---- closure fact
ROW_CLOSURE = re.compile(r"latest outside closure `corpus/lessons/(round-([0-9]+)-verifier-spotcheck\.md)`")
m = ROW_CLOSURE.search(row or "")
if not m:
    findings.append("closure: rendered row names no latest outside closure")
elif not best_clo:
    facts["closure"] = None
elif int(m.group(2)) != best_clo[0]:
    findings.append(f"closure: row round-{m.group(2)} != newest committed round-{best_clo[0]}")
else:
    facts["closure_name"] = m.group(1)

# ---- disposition fact
if best_clo:
    try:
        cblob = show(best_clo[1])
    except subprocess.CalledProcessError:
        cblob = ""
    DISPS = ("rejected-harmed", "rejected-honest-stop", "admitted")
    word = next((w for w in DISPS if re.search(rf"\b{w}\b", cblob)), "unknown")
    if word == "unknown":
        findings.append("disposition: closure body carries no disposition word")
    elif not re.search(rf"round{best_clo[0]} {re.escape(word)}\b", row or ""):
        findings.append(f"disposition: row does not name round{best_clo[0]} {word}")
    else:
        facts["disposition_word"] = word

facts["mismatches"] = len(findings)
import json
print(json.dumps(facts, indent=1))
print("FINDINGS:", *findings, sep="\n  ") if findings else print("FINDINGS: none")
