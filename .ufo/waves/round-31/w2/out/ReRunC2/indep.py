#!/usr/bin/env python3
# Independent re-derivation for ReRunC2 (no imports from the frozen counter).
# (a) claim-table data rows in SCORECARD.md at tip, with file:line each;
# (b) unresolved strings -> SCORECARD.md line + round;
# (c) append_only via blob prefix comparison.
import json, re, subprocess, sys

REPO = "/tmp/kama-r31w2/ReRunC2/lane"
TIP = "382d11b2107d335705875da1a4d889b074bd6fa6"
BASE = "07794a4d30a54a60ebdff50ac76d12c6df40a0f1"
CORR = "## Round 31 — claim-row evidence corrections"

def blob(rev, path):
    p = subprocess.run(["/usr/bin/git", "--no-replace-objects", "-C", REPO,
                        "cat-file", "blob", f"{rev}:{path}"], capture_output=True)
    return p.stdout if p.returncode == 0 else None

tip = blob(TIP, "SCORECARD.md")
base = blob(BASE, "SCORECARD.md")
text = tip.decode("utf-8", "replace")
lines = text.split("\n")

# (a) my own table walk: nearest preceding '## Round N' heading; data rows = '|' lines
# after a '|' header whose first cell is 'claim'; stop population at CORR heading.
round_re = re.compile(r"^## Round (\d+)\b")
heading = ""
rnd = None
pop_rows = []   # (line_no, first_cell, round, table_header)
i = 0
in_corr = False
while i < len(lines):
    ln = lines[i]
    if ln.startswith(CORR):
        in_corr = True
    if ln.startswith("## "):
        heading = ln
        m = round_re.match(ln)
        if m:
            rnd = m.group(1)
    if not in_corr and ln.startswith("|"):
        hdr = [c.strip() for c in ln.strip().strip("|").split("|")]
        j = i + 1
        if j < len(lines) and set(lines[j].replace("|", "").replace(" ", "")) <= set("-:"):
            j += 1
        while j < len(lines) and lines[j].startswith("|"):
            cs = [c.strip() for c in lines[j].strip().strip("|").split("|")]
            if hdr and hdr[0].lower() == "claim" and cs and cs[0].strip():
                pop_rows.append((j + 1, cs[0], rnd, " | ".join(hdr[:3])))
            j += 1
        i = j
        continue
    i += 1

print("== (a) claim-table data rows (population, pre-correction-section) ==")
print(f"count {len(pop_rows)}")
for n, (lno, cell, r, hdr) in enumerate(pop_rows, 1):
    print(f"{n:2d}. SCORECARD.md:{lno} round={r} claim_cell={cell[:70]!r} hdr={hdr[:60]!r}")

# (b) unresolved strings: counter receipt lists ["C1","C1","C1"]; locate every
# population row whose first cell is exactly 'C1'.
print("\n== (b) population rows whose Claim cell is exactly 'C1' ==")
for lno, cell, r, hdr in pop_rows:
    if cell == "C1":
        print(f"SCORECARD.md:{lno} round={r} line={lines[lno-1][:120]!r}")

# correction table rows (in the appended section) for context
print("\n== correction section rows (id|row|class|observed) ==")
i = 0
while i < len(lines):
    if lines[i].startswith(CORR):
        j = i + 1
        while j < len(lines):
            if lines[j].startswith("|") and "id" in lines[j] and "observed" in lines[j]:
                k = j + 2
                while k < len(lines) and lines[k].startswith("|"):
                    cs = [c.strip() for c in lines[k].strip().strip("|").split("|")]
                    print(f"SCORECARD.md:{k+1} {cs}")
                    k += 1
                break
            if j > i + 40:
                break
            j += 1
        break
    i += 1

# (c) append_only: byte prefix
print("\n== (c) append_only ==")
print(f"tip_bytes {len(tip)} base_bytes {len(base)} startswith {tip.startswith(base)}")
import hashlib
print(f"tip_sha256 {hashlib.sha256(tip).hexdigest()}")
print(f"base_sha256 {hashlib.sha256(base).hexdigest()}")
# first divergence context (should be the appended section)
pre = tip[:len(base)]
post = tip[len(base):]
print(f"prefix_identical {pre == base}")
print(f"appended_head {post[:120]!r}")
