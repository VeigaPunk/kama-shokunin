#!/usr/bin/env python3
"""R42D07 counter-mutant generator. Emits mutated copies of the two round-42
counters into seat/mut/<id>.py plus a manifest with before/after sha256."""
import hashlib, os, sys

SEAT = "/fast/scratch/kama-r42/seats/R42D07"
CLONE = f"{SEAT}/clone"
SRC = {
    "c2": f"{CLONE}/tools/round42-digest-audit.py",
    "c3": f"{CLONE}/tools/round42-capacity-audit.py",
}

# (id, counter, description, old, new) -- old must occur exactly once in source
MUTS = [
    # ---- C2: tools/round42-digest-audit.py
    ("M01", "c2", "live leg: external_ok >= 4 relaxed to >= 0",
     'ref["unknown"] == 0 and ref["external_ok"] >= 4)',
     'ref["unknown"] == 0 and ref["external_ok"] >= 0)'),
    ("M02", "c2", "hygiene leg forced to 1 (leak check dropped)",
     '        legs["hygiene"] = int(not left and all(os.path.isfile(os.path.join(src, t)) for t in (\n'
     '            "tools/round41-scorecard-reconcile.py", "tools/round41-pinwatch-audit.py")))',
     '        legs["hygiene"] = 1'),
    ("M03", "c2", "contract cases 8 -> 1",
     "CASES = 8", "CASES = 1"),
    ("M04", "c2", "absent external evidence counted as external_ok",
     '                    n["external_absent"] += 1',
     '                    n["external_ok"] += 1'),
    ("M05", "c2", "live leg drops summary byte-equality (exit-only)",
     'good = (out.strip() == summary(ref) and code == exit_of(ref) and ref["ledger_bad"] == 0',
     'good = (code == exit_of(ref) and ref["ledger_bad"] == 0'),
    ("M06", "c2", "'wrong' row: correct digest no longer must be in blob set",
     'good = bool(re.fullmatch(r"[0-9a-f]{64}", c)) and c in blobs and c[:8] == t[:8]',
     'good = bool(re.fullmatch(r"[0-9a-f]{64}", c))'),
    ("M07", "c2", "documents under .ufo/ no longer excluded from token scan",
     '    if path.startswith(".ufo/") or path == LEDGER:',
     '    if path == LEDGER:'),
    ("M08", "c2", "exit_of ignores unknown tokens",
     '    return 1 if n["ledger_bad"] + n["wrong_unflagged"] + n["unknown"] > 0 else 0',
     '    return 1 if n["ledger_bad"] + n["wrong_unflagged"] > 0 else 0'),
    ("M09", "c2", "unverifiable row: empty note accepted",
     'n["unverifiable" if r["note"].strip() else "ledger_bad"] += 1',
     'n["unverifiable"] += 1'),
    ("M10", "c2", "external re-hash compares 8-char prefix only",
     'n["external_ok" if h == t else "ledger_bad"] += 1',
     'n["external_ok" if h[:8] == t[:8] else "ledger_bad"] += 1'),
    ("M11", "c2", "capability row: evidence cell no longer checked",
     'if len(r) >= 3 and r[0].strip("` *") == "digest-ledger" and "tools/digest-ledger.py" in r[2]:',
     'if len(r) >= 3 and r[0].strip("` *") == "digest-ledger":'),
    ("M12", "c2", "capability: first canonical table wins instead of highest round",
     "        if m and int(m.group(1)) > best:",
     "        if m and best < 0:"),
    ("M13", "c2", "contract case: summary bytes no longer compared (exit-only)",
     "                    if out.strip() != summary(want) or code != exit_of(want):",
     "                    if code != exit_of(want):"),
    ("M14", "c2", "hygiene: leaked temp entries ignored (file presence still required)",
     'legs["hygiene"] = int(not left and all(os.path.isfile',
     'legs["hygiene"] = int(all(os.path.isfile'),
    # ---- C3: tools/round42-capacity-audit.py
    ("N01", "c3", "gate quote word limit 25 -> 250",
     "len(x.split()) <= 25", "len(x.split()) <= 250"),
    ("N02", "c3", "coverage: base-absence of the entry no longer required",
     '    if blob(repo, base, ENTRY) is not None:\n        ok = False\n        d.append("detail: entry already present at base")',
     '    if False:\n        ok = False\n        d.append("detail: entry already present at base")'),
    ("N03", "c3", "census leg forced to 1",
     '            legs["census"] = int(p.returncode == 0)',
     '            legs["census"] = 1'),
    ("N04", "c3", "rows leg: absent evidence copy accepted (digest check skipped)",
     "        if c is None or ev[sid] is None:",
     "        if c is None:"),
    ("N05", "c3", "entry leg reads corpus/README.md instead of the entry",
     "    entry = blob(repo, tip, ENTRY)",
     '    entry = blob(repo, tip, "corpus/README.md")'),
    ("N06", "c3", "rows leg: anchor digest no longer checked",
     '        if digest not in c[5]: bad.append("anchor lacks copy sha256")',
     '        if not digest: bad.append("anchor lacks copy sha256")'),
    ("N07", "c3", "gate: access date no longer required on the quote line",
     "            if url in sec and DATE in l and any(",
     "            if url in sec and any("),
    ("N08", "c3", "gate: non-empty collisions without renumber map accepted",
     '        elif s == "collisions" and b.strip() and "renumber" not in les.lower():',
     '        elif False and b.strip() and "renumber" not in les.lower():'),
    ("N09", "c3", "gate: empty quarantine-slice accepted",
     '        elif s == "quarantine-slice" and not b.strip():',
     '        elif False and not b.strip():'),
    ("N10", "c3", "entry provenance: source line need not name S478/S479",
     '            and head[2].startswith("recheck:") and "S478" in head[0] and "S479" in head[0]',
     '            and head[2].startswith("recheck:")'),
    ("N11", "c3", "max_model_len count computed on the vLLM copy instead of llama.cpp",
     'mm=lc.decode(errors="replace").count("max_model_len"))',
     'mm=vl.decode(errors="replace").count("max_model_len"))'),
    ("N12", "c3", "coverage: base tree no longer scanned for pre-existing ground",
     '    for p in git(repo, "ls-tree", "-r", "--name-only", "-z", base).split("\\0"):',
     "    for p in []:"),
    ("N13", "c3", "coverage: corpus/README.md naming line no longer required",
     '    if not any(ENTRY in l for l in rd.split("\\n")):',
     "    if False:"),
]

def main():
    os.makedirs(f"{SEAT}/mut", exist_ok=True)
    os.makedirs(f"{SEAT}/artifacts", exist_ok=True)
    srcs = {k: open(p, "rb").read() for k, p in SRC.items()}
    rows = ["id\tcounter\tdescription\tbefore_sha256\tafter_sha256\tapplied"]
    for mid, ctr, desc, old, new in MUTS:
        s = srcs[ctr].decode()
        n = s.count(old)
        if n != 1:
            print(f"FATAL anchor {mid}: {n} occurrences of {old!r}", file=sys.stderr)
            return 1
        out = s.replace(old, new).encode()
        p = f"{SEAT}/mut/{mid}.py"
        open(p, "wb").write(out)
        rows.append("\t".join([mid, ctr, desc,
                               hashlib.sha256(srcs[ctr]).hexdigest(),
                               hashlib.sha256(out).hexdigest(), "1"]))
    open(f"{SEAT}/artifacts/mutants.tsv", "w").write("\n".join(rows) + "\n")
    print(f"{len(MUTS)} mutants written; manifest {SEAT}/artifacts/mutants.tsv")
    return 0

if __name__ == "__main__":
    sys.exit(main())
