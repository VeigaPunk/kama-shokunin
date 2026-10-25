#!/usr/bin/env python3
"""R42D07: build derived probe states in the replay sandbox D.

Probe states demonstrate, for mutants that no committed control kills, that the
mutated counter accepts a defect the pristine counter rejects. Each probe is a
commit in the SAME fixture sandbox (fixture identity only). Emits probes.rev.
"""
import hashlib, importlib.util, os, random, re, shutil, subprocess, sys

SEAT = "/fast/scratch/kama-r42/seats/R42D07"
CLONE = f"{SEAT}/clone"
D = f"{SEAT}/fixtures/replay"
TIP = "3d9bd8d72366e281fab291874524130428ee423d"
BASE = "0b606b03bf0b2a87b791aa537f6c72c941624cf0"
ENTRY = "corpus/knowledge/context-capacity-engine-sides.md"
LESSON = "corpus/lessons/round-42.md"
VLLM = f"{CLONE}/.ufo/waves/round-42/c3/vllm-v0.32.0-kv_cache_utils.py"

def g(*a):
    return subprocess.run(["git", "-C", D, *a], check=True, capture_output=True, text=True).stdout

def commit(msg):
    g("add", "-A")
    subprocess.run(["git", "-C", D, "-c", "user.name=r42-control",
                    "-c", "user.email=r42-control@fixture.invalid",
                    "commit", "-q", "--allow-empty", "-m", msg], check=True)
    return g("rev-parse", "HEAD").strip()

def rd(p):
    return open(os.path.join(D, p)).read()

def wr(p, s):
    fp = os.path.join(D, p)
    os.makedirs(os.path.dirname(fp) or D, exist_ok=True)
    open(fp, "w").write(s)

def norm(s):
    return re.sub(r"\s+", " ", s).strip()

with open(f"{SEAT}/probes.rev", "w") as f:
    def emit(k, v):
        revs[k] = v
        f.write(f"{k}={v}\n")
        print(k, v)
    revs = dict(l.strip().split("=", 1) for l in open(f"{SEAT}/replay.rev") if "=" in l)

    # P-M01: junk-c2-allunverifiable + the tip's round-41 counters (no leak)
    g("checkout", "-q", "--detach", revs["R-ALLUNV"])
    for p in ("tools/round41-scorecard-reconcile.py", "tools/round41-pinwatch-audit.py"):
        wr(p, subprocess.run(["git", "-C", CLONE, "cat-file", "-p", f"{TIP}:{p}"],
                             check=True, capture_output=True).stdout.decode())
    emit("P-M01", commit("probe: allunverifiable with clean round-41 counters"))

    # P-M02: sep-c2-only with the BASE (leaky) round-41 counters
    g("checkout", "-q", "--detach", revs["R-SEPC2"])
    for p in ("tools/round41-scorecard-reconcile.py", "tools/round41-pinwatch-audit.py"):
        wr(p, subprocess.run(["git", "-C", CLONE, "cat-file", "-p", f"{BASE}:{p}"],
                             check=True, capture_output=True).stdout.decode())
    emit("P-M02", commit("probe: sep-c2-only with leaky round-41 counters"))

    # P-M03: sep-c2-only with a ledger tool that crashes (exit 2) on --dir
    # fixtures containing data3.bin (present only in contract case 3, seed 42)
    g("checkout", "-q", "--detach", revs["R-SEPC2"])
    tool = open(os.path.join(CLONE, "tools/digest-ledger.py")).read()
    anchor = '    a = ap.parse_args()\n    if a.cmd == "selftest":'
    assert tool.count(anchor) == 1, "main anchor"
    tool = tool.replace(anchor,
           '    a = ap.parse_args()\n'
           '    if a.dir and os.path.isfile(os.path.join(a.dir, "data3.bin")):\n'
           '        sys.exit(2)\n'
           '    if a.cmd == "selftest":')
    wr("tools/digest-ledger.py", tool)
    emit("P-M03", commit("probe: sep-c2-only with a case-3-crashing ledger tool"))

    # P-M13: sep-c2-only with a ledger tool that swaps tokens/blob in the
    # rendered summary (exit unchanged) when data3.bin is present
    g("checkout", "-q", "--detach", revs["R-SEPC2"])
    tool = open(os.path.join(CLONE, "tools/digest-ledger.py")).read()
    anchor = '    n, detail = classify(tok, blobs, led)\n    print(render(n))'
    assert tool.count(anchor) == 1, "render anchor"
    tool = tool.replace(anchor,
           '    n, detail = classify(tok, blobs, led)\n'
           '    if a.dir and os.path.isfile(os.path.join(a.dir, "data3.bin")):\n'
           '        n["tokens"], n["blob"] = n["blob"], n["tokens"]\n'
           '    print(render(n))')
    wr("tools/digest-ledger.py", tool)
    emit("P-M13", commit("probe: sep-c2-only with a summary-swapping ledger tool"))

    # P-M05: sep-c2-only with a git-mode-only lying digest-ledger.py (exit-neutral)
    g("checkout", "-q", "--detach", revs["R-SEPC2"])
    tool = open(os.path.join(CLONE, "tools/digest-ledger.py")).read()
    anchor = ('    if ledger_file is not None:\n'
              '        with open(ledger_file, encoding="utf-8", errors="replace") as f:\n'
              '            ledger = parse_ledger(f.read())\n'
              '    return tokens, blobs, ledger\n\n\ndef render')
    assert tool.count(anchor) == 1, "scan_git tail anchor"
    tool = tool.replace(anchor,
           '    if ledger_file is not None:\n'
           '        with open(ledger_file, encoding="utf-8", errors="replace") as f:\n'
           '            ledger = parse_ledger(f.read())\n'
           '    fake = hashlib.sha256(b"r42d07 git-mode lie").hexdigest()\n'
           '    tokens.add(fake)\n'
           '    blobs.add(fake)\n'
           '    return tokens, blobs, ledger\n\n\ndef render')
    wr("tools/digest-ledger.py", tool)
    emit("P-M05", commit("probe: sep-c2-only with git-mode lying ledger tool"))

    # P-M11: sep-c2-only with the capability row evidence cell pointing elsewhere
    g("checkout", "-q", "--detach", revs["R-SEPC2"])
    sc = rd("SCORECARD.md")
    cell = "`tools/digest-ledger.py`; `registry/digest-ledger.tsv`"
    assert sc.count(cell) == 1, "capability evidence cell"
    wr("SCORECARD.md", sc.replace(cell, "somewhere/else.py"))
    emit("P-M11", commit("probe: sep-c2-only with evidence cell pointing elsewhere"))

    # P-N01: sep-c3-only with the S478 gate quote replaced by a 30-word span
    g("checkout", "-q", "--detach", revs["R-SEPC3"])
    ev = norm(open(VLLM, errors="replace").read()).split(" ")
    span = None
    for i in range(len(ev) - 30):
        w = ev[i:i + 30]
        if not any('"' in x or "|" in x for x in w):
            span = " ".join(w)
            break
    assert span, "no 30-word span"
    les = rd(LESSON)
    old_q = '"num_blocks = available_memory // bytes_per_block"'
    assert les.count(old_q) == 1, "S478 quote anchor"
    wr(LESSON, les.replace(old_q, f'"{span}"'))
    emit("P-N01", commit("probe: sep-c3-only with a 30-word S478 gate quote"))

    # P-N03: sep-c3-only with a malformed SOURCES row (census must reject)
    g("checkout", "-q", "--detach", revs["R-SEPC3"])
    wr("corpus/SOURCES.md", rd("corpus/SOURCES.md") +
       "| S999 | junk | code |\n")
    ok = subprocess.run(["bash", "/home/vgpnk/Projects/shokunin/scripts/sources-census.sh",
                         "validate", "--file", os.path.join(D, "corpus/SOURCES.md")],
                        capture_output=True, text=True)
    if ok.returncode == 0:
        wr("corpus/SOURCES.md", rd("corpus/SOURCES.md").replace(
            "| S999 | junk | code |\n",
            "| S999 | junk | code | A | x | y | z | mined | 2026-13-45 | 90d | nowhere |\n"))
        ok = subprocess.run(["bash", "/home/vgpnk/Projects/shokunin/scripts/sources-census.sh",
                             "validate", "--file", os.path.join(D, "corpus/SOURCES.md")],
                            capture_output=True, text=True)
    if ok.returncode != 0:
        emit("P-N03", commit("probe: sep-c3-only with a census-rejected SOURCES row"))
    else:
        print("WARN: census validate accepts the junk row; P-N03 skipped")

    # P-N06: sep-c3-only with the S478/S479 anchor digests replaced
    g("checkout", "-q", "--detach", revs["R-SEPC3"])
    srcs = rd("corpus/SOURCES.md")
    n = 0
    for hexd in ("af4164bca819f1cdc416077522a7019936fd38a523a482283eb91b08dae0e57a",
                 "9c5a6f2cc7997a3a409482c53119a2462e8c409ddf001cc568a9a8740e708b4a"):
        if hexd in srcs:
            srcs = srcs.replace(hexd, "anchor")
            n += 1
    assert n == 2, f"anchor digest occurrences {n}"
    wr("corpus/SOURCES.md", srcs)
    emit("P-N06", commit("probe: sep-c3-only with anchor cells lacking the copy digest"))

    # P-N07: sep-c3-only with the S478 gate line undated
    g("checkout", "-q", "--detach", revs["R-SEPC3"])
    les = rd(LESSON)
    old = "accessed 2026-10-25 (curl, 111612 bytes"
    assert les.count(old) == 1, "S478 date anchor"
    wr(LESSON, les.replace(old, "accessed 2026-10-24 (curl, 111612 bytes"))
    emit("P-N07", commit("probe: sep-c3-only with an undated S478 gate quote"))

    # P-N08: sep-c3-only with collisions non-empty and no renumber map in the lesson
    g("checkout", "-q", "--detach", revs["R-SEPC3"])
    les = rd(LESSON)
    assert "renumber" in les.lower()
    les = les.replace("Renumber map, by document:", "Mapping, by document:")
    assert "renumber" not in les.lower(), "renumber still present"
    wr(LESSON, les)
    assert rd(".ufo/waves/round-42/assimilation/collisions").strip()
    emit("P-N08", commit("probe: sep-c3-only, collisions non-empty, no renumber map"))

    # P-N09: sep-c3-only with an emptied quarantine-slice
    g("checkout", "-q", "--detach", revs["R-SEPC3"])
    wr(".ufo/waves/round-42/assimilation/quarantine-slice", "")
    emit("P-N09", commit("probe: sep-c3-only with an empty quarantine-slice"))

    # P-N10: sep-c3-only with the entry source line not naming S478/S479
    g("checkout", "-q", "--detach", revs["R-SEPC3"])
    ent = rd(ENTRY)
    head = ent.split("\n", 1)
    assert head[0].startswith("source:"), "entry head"
    wr(ENTRY, "source: control\n" + head[1])
    emit("P-N10", commit("probe: sep-c3-only with an anonymous entry source line"))

    # P-N13: sep-c3-only with the base README (no entry naming line)
    g("checkout", "-q", "--detach", revs["R-SEPC3"])
    wr("corpus/README.md", subprocess.run(
        ["git", "-C", CLONE, "cat-file", "-p", f"{BASE}:corpus/README.md"],
        check=True, capture_output=True).stdout.decode())
    emit("P-N13", commit("probe: sep-c3-only without the README coverage line"))

    # B-N12: base + a corpus file already holding the ground (for --base variant)
    g("checkout", "-q", "--detach", BASE)
    wr("corpus/zz-ground.md", "kv_cache_size_tokens\n")
    emit("B-N12", commit("probe-base: ground already in corpus"))
print("probes.rev written")
