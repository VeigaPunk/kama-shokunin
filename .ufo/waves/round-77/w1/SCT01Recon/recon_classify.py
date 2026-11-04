#!/usr/bin/env python3
"""SCT01 independent join: audit events at base vs accepted/exempt registers and contract regions."""
import hashlib, importlib.util, json, subprocess, sys
from collections import Counter

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
BASE = "cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7"
import os
S = os.path.dirname(os.path.abspath(__file__))

spec = importlib.util.spec_from_file_location("aa", LANE + "/tools/append-only-audit.py")
aa = importlib.util.module_from_spec(spec); spec.loader.exec_module(aa)

def git(*args):
    p = subprocess.run(["git", "-C", LANE, *args], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError("git " + " ".join(args) + " => " + p.stdout.decode(errors="replace") + p.stderr.decode(errors="replace"))
    return p.stdout

data = json.load(open(S + "/audit-base.json"))
assert data["to"] == BASE, data["to"]
events = {(e["commit"], e["file"]): e for e in data["events"]}
commits = {e["commit"] for e in data["events"]}

contract_text = git("show", f"{BASE}:registry/append-only-contract.tsv").decode()
rows = aa.parse_contract(contract_text)

def tsv(path):
    text = git("show", f"{BASE}:{path}").decode()
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    header = lines.pop(0).split("\t")
    return header, [dict(zip(header, ln.split("\t"))) for ln in lines]

ah, accepted = tsv("registry/append-only-accepted.tsv")
eh, exempt = tsv("registry/append-only-exempt.tsv")
print("accepted rows:", len(accepted), "exempt rows:", len(exempt))
print("accepted header:", ah)
print("exempt header:", eh)

def sha(b):
    return hashlib.sha256(aa.key(b)).hexdigest()

# --- cache per event: parent body sections, deleted lines with parent section, hashes ---
cache = {}
def event_detail(key):
    if key in cache:
        return cache[key]
    commit, file = key
    parent = git("rev-parse", f"{commit}^1").decode().strip()
    blob = git("show", f"{parent}:{file}")
    body = aa.split_lines(blob)
    secs = aa.sections(body)
    dl = aa.deleted_lines(LANE, parent, commit, file)
    detail = []
    for pos, text, na in dl:
        title = secs[pos - 1] if 0 < pos <= len(secs) else None
        detail.append({"pos": pos, "sha": sha(text), "section": title, "adds": na})
    titles, prefixes = aa.file_regions(rows, file)
    out = {"parent": parent, "deleted_lines": detail, "exempt_titles": titles, "only_prefixes": prefixes}
    cache[key] = out
    return out

def in_region(d, prefixes):
    s = d["section"]
    return any(s is not None and s.startswith(p) for p in prefixes)

# --- accepted join: row binds when (commit,file,line_sha256) matches an undisclosed graded line
# and count equals that entry's count and class is in its classes (mechanical class) ---
acc_by_ev = {}
for r in accepted:
    acc_by_ev.setdefault((r["commit"], r["file"]), []).append(r)

accepted_events, accepted_partial = [], []
for key, e in events.items():
    rows_k = acc_by_ev.get(key, [])
    if not rows_k or e["status"] == "restored" or not e["undisclosed"]:
        continue
    want = {(u["line_sha256"]): u for u in e["undisclosed"]}
    ok = len(rows_k) == len(e["undisclosed"])
    for u in e["undisclosed"]:
        hit = [r for r in rows_k if r["line_sha256"] == u["line_sha256"] and int(r["count"]) == u["count"]]
        if not hit:
            ok = False
    (accepted_events if ok else accepted_partial).append(key)

# --- exempt join: class-bound row, count == ungraded, sections == parent sections of ungraded lines ---
ex_by_ev = {}
for r in exempt:
    ex_by_ev.setdefault((r["commit"], r["file"]), []).append(r)

def exempt_fit(key):
    e = events[key]
    if e["status"] != "ungraded":
        return None
    d = event_detail(key)
    # ungraded lines: those whose parent section is an eligible exempt title
    # replicate v6 eligibility via audit helpers over the event window
    commit, file = key
    parent = d["parent"]
    titles = d["exempt_titles"]
    # count(T,x) >= count(T,parent) over the window; window = commits from event to <to>
    # reuse audit module internals is heavy; section-membership + register count equality is the join
    par_secs = [x["section"] for x in d["deleted_lines"] if x["section"] in titles]
    ungraded_lines = sum(1 for x in d["deleted_lines"]
                         if x["section"] in titles and not in_region(x, d["only_prefixes"]))
    return d, par_secs, ungraded_lines

exempt_valid, exempt_invalid = [], []
for key, rows_k in ex_by_ev.items():
    fit = exempt_fit(key)
    if fit is None:
        exempt_invalid.append((key, "event-not-ungraded")); continue
    d, par_secs, ungraded_n = fit
    ok = False
    for r in rows_k:
        if r["class"] != "exempt-head":
            continue
        if int(r["count"]) != events[key]["ungraded"]:
            continue
        want = sorted(set(x for x in par_secs))
        got = sorted(r["sections"].split("|")) if r["sections"] else []
        if want == got:
            ok = True
    (exempt_valid if ok else exempt_invalid).append((key, "fit" if ok else "count/sections"))

exempt_keys = set(k for k, _ in exempt_valid)

# --- classification of the unaccounted (ungraded, no valid accepted/exempt row) ---
ungraded = [k for k, e in events.items() if e["status"] == "ungraded"]
unaccounted = [k for k in ungraded if k not in accepted_events and k not in exempt_keys]
print("\ndecayed: ungraded", len(ungraded), "exempt-valid", len(exempt_keys), "unaccounted", len(unaccounted))

permitted, out_of_region, head, other = [], [], [], []
for k in unaccounted:
    e = events[k]; d = event_detail(k)
    outside = bool(d["only_prefixes"]) and all(not in_region(x, d["only_prefixes"]) for x in d["deleted_lines"])
    fully_permitted = e["permitted"] == e["deleted"] and e["graded"] == 0 and e["ungraded"] == 0
    # head: every ungraded line's parent section is an exempt title and parents subset titles
    par_secs = set(x["section"] for x in d["deleted_lines"])
    is_head = bool(par_secs) and par_secs <= d["exempt_titles"]
    if fully_permitted:
        permitted.append(k)
    elif outside:
        out_of_region.append(k)
    elif is_head:
        head.append(k)
    else:
        other.append((k, e["deleted"], e["graded"], e["ungraded"], e["permitted"], sorted(par_secs), sorted(d["exempt_titles"])))

print("\n== decomposition of 41 ==")
print("fully permitted (permitted==deleted, graded==ungraded==0):", len(permitted))
for k in permitted: print("  PERMITTED", k[0], k[1])
print("out_of_region (only= contract, all deleted outside):", len(out_of_region))
for k in out_of_region: print("  OUT_OF_REGION", k[0], k[1], "prefixes", event_detail(k)["only_prefixes"])
print("exempt-head eligible (SCORECARD head):", len(head))
for k in head: print("  HEAD", k[0], k[1], "deleted", events[k]["deleted"], "ungraded", events[k]["ungraded"])
print("neither:", len(other))
for o in other: print("  OTHER", o)

print("\n== totals ==")
print("restored", sum(1 for e in events.values() if e["status"] == "restored"))
print("disclosed", sum(1 for e in events.values() if e["status"] == "disclosed"))
print("accepted", len(accepted_events), "accepted-partial", len(accepted_partial))
print("statuses", Counter(e["status"] for e in events.values()))
print("event total", len(events))

# counter-evidence: permitted event carrying graded/ungraded lines
bad_perm = [(k, e["permitted"], e["deleted"], e["graded"], e["ungraded"])
            for k, e in events.items() if e["permitted"] > 0 and (e["graded"] > 0 or e["ungraded"] > 0)]
print("permitted-and-graded events:", bad_perm)
