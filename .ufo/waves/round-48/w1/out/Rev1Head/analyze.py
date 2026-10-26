#!/usr/bin/env python3
"""Classify every SCORECARD.md head-region rewrite since a start rev.

head region = lines before the `## Round 6` heading in the PARENT version.
For each commit (first-parent diff) that touches SCORECARD.md:
  - parse `git diff -U0` hunks, keep those whose old line number < boundary
  - classify each deleted/added line by parent section + kind
  - for each deleted non-blank line, ask whether its text is still in the FILE
    at the commit (stripped compare; also byte-exact with multiplicity via
    difflib-free multiset count)
Outputs JSON to stdout (--json) and a table.
"""
import json, re, subprocess, sys, collections

REPO = sys.argv[1]
START = sys.argv[2]
TIPS = sys.argv[3:] or [None]

def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], check=True,
                          capture_output=True).stdout

def show(rev, path="SCORECARD.md"):
    try:
        return git("show", f"{rev}:{path}").decode("utf-8", "replace")
    except subprocess.CalledProcessError:
        return None

H2 = re.compile(r"^## ")

def sections(lines):
    """section title per line index (0-based): last '## ' at or before."""
    out, cur = [], None
    for ln in lines:
        if ln.startswith("## "):
            cur = ln.rstrip()
        out.append(cur)
    return out

def boundary(lines):
    for i, ln in enumerate(lines):
        if ln.startswith("## Round 6"):
            return i
    return len(lines)

def kind(sec, text, idx, prev_blank_ctx):
    t = text.strip()
    if sec is None:
        return "banner(preamble)"
    title = sec[3:].strip()
    base = title.split(" — ")[0].split(" (")[0].strip()
    if base == "Axes":
        if t.startswith("|"):
            return "Axes:row"
        if "Historical axes table" in "".join(prev_blank_ctx):
            return "Axes:historical"
        return "Axes:prose"
    if base == "Planned":
        return "Planned:pointer"
    if base == "Saturation":
        return "Saturation"
    if base == "Capabilities":
        return "Capabilities:mirror"
    if base == "Retired":
        return "Retired"
    if base == "Move log":
        return "Move log"
    if base.startswith("Actual round 5"):
        return "Actual round 5"
    if base.startswith("Historical head sections"):
        return "Historical head sections"
    return "other:" + base[:30]

def hunks(diff_text):
    """yield (old_start, old_count, new_start, new_count, [-lines], [+lines])"""
    cur = None
    for ln in diff_text.splitlines():
        m = re.match(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", ln)
        if m:
            if cur:
                yield cur
            cur = [int(m.group(1)), int(m.group(2) or 1),
                   int(m.group(3)), int(m.group(4) or 1), [], []]
            continue
        if cur is None:
            continue
        if ln.startswith("-") and not ln.startswith("---"):
            cur[4].append(ln[1:])
        elif ln.startswith("+") and not ln.startswith("+++"):
            cur[5].append(ln[1:])
    if cur:
        yield cur

commits = git("rev-list", "--first-parent", "--reverse", f"{START}..HEAD",
              "--", "SCORECARD.md").decode().split()
if START not in commits:
    commits = [START] + commits

rows = []
for c in commits:
    parent = git("rev-parse", f"{c}^").decode().strip()
    old = show(parent) or ""
    new = show(c) or ""
    olines = old.split("\n")
    b = boundary(olines)
    secs = sections(olines)
    dtext = git("diff", "-U0", "--no-color", parent, c, "--", "SCORECARD.md").decode("utf-8", "replace")
    new_set = collections.Counter(x.strip() for x in new.split("\n"))
    head_del = head_add = 0
    classes = collections.Counter()
    dropped = []
    kept = []
    escaped = 0
    for os_, oc, ns, nc, dels, adds in hunks(dtext):
        # old hunk spans os_..os_+oc-1 (1-based)
        if oc == 0:
            start_idx = os_          # pure insertion after line os_
        else:
            start_idx = os_ - 1
        if start_idx >= b:
            continue
        if oc == 0:
            # insertion into head: boundary in new file not needed; count
            head_add += len(adds)
            sec = secs[start_idx - 1] if start_idx - 1 >= 0 else None
            classes[kind(sec, adds[0] if adds else "", start_idx, [])+":+"] += len(adds)
            continue
        # clamp to head
        n = min(oc, b - start_idx)
        escaped += oc - n
        for k in range(n):
            idx = start_idx + k
            sec = secs[idx]
            ctx = olines[max(0, idx - 4):idx]
            k_ = kind(sec, olines[idx], idx, ctx)
            classes[k_] += 1
            head_del += 1
            s = olines[idx].strip()
            if s and new_set.get(s, 0) == 0:
                dropped.append((k_, olines[idx][:160]))
            elif s:
                kept.append(k_)
        head_add += len(adds)
    rows.append(dict(commit=c[:8], parent=parent[:8],
                     subject=git("log", "-1", "--format=%s", c).decode().strip()[:110],
                     boundary=b, head_deleted=head_del, head_added=head_add,
                     classes=dict(classes), dropped=len(dropped),
                     dropped_samples=dropped[:6], escaped_beyond_head=escaped))

print(json.dumps(rows, indent=1))
