#!/usr/bin/env python3
"""R42A06 mutant battery: does the frozen C1 counter actually compute each predicate clause?"""
import hashlib, os, re, subprocess, sys

SEAT = "/fast/scratch/kama-r42/seats/R42A06"
CLONE = f"{SEAT}/clone"
BASE = "c8c92db4bdf1c64357b995e0fe8d2a4f481fe995"
ENV = dict(os.environ, TMPDIR=f"{SEAT}/tmp")


def git(*a, **kw):
    return subprocess.run(["git", "-C", CLONE, *a], capture_output=True, text=True, **kw)


def read(p):
    return open(os.path.join(CLONE, p)).read()


def write(p, t):
    with open(os.path.join(CLONE, p), "w") as f:
        f.write(t)


def insert_after_heading(sc, pat, text):
    lines = sc.split("\n")
    idx = [i for i, l in enumerate(lines) if re.search(pat, l)]
    assert len(idx) == 1, (pat, idx)
    lines.insert(idx[0] + 1, text)
    return "\n".join(lines)


def m_extra_axis():
    sc = read("SCORECARD.md")
    sc = sc.replace("\n\n### Historical axes table",
                    "\n| **latency** | **6** | run `bash -c 'echo ok'` \u2192 `ok` | score round 42 |"
                    "\n\n### Historical axes table", 1)
    sc = sc.replace("None. 6 axes and 8 capabilities", "None. 7 axes and 8 capabilities", 1)
    sc = sc.replace("adjacency 7 (from", "adjacency 7, latency 6 (from", 1)
    return {"SCORECARD.md": sc}


def m_dup_sections():
    sc = read("SCORECARD.md")
    sc += ("\n## Retired\n\nBoth assigned axes are retired; every model endpoint is dead.\n"
           "\n## Saturation\n\n8/10 on every owned axis.\n"
           "\n## Capabilities\n\n| Capability | What it can now do | Evidence pointer | First-working round |\n"
           "|---|---|---|---|\n| sources-registry | stale mirror | `corpus/SOURCES.md` | 10 |\n")
    return {"SCORECARD.md": sc}


def m_substring_counts():
    sc = read("SCORECARD.md")
    sc = sc.replace("None. 6 axes and 8 capabilities", "None. 16 axes and 18 capabilities", 1)
    return {"SCORECARD.md": sc}


def m_province_substring():
    prov = read("PROVINCE.md")
    assert "tools/pin-watch.py" in prov
    newprov = prov.replace("tools/pin-watch.py", "tools/pin-watch.py.bak")
    old = re.search(r"`PROVINCE\.md` sha256 `([0-9a-f]{64})`", read("SCORECARD.md")).group(1)
    new = hashlib.sha256(newprov.encode()).hexdigest()
    sc = read("SCORECARD.md").replace(f"`PROVINCE.md` sha256 `{old}`", f"`PROVINCE.md` sha256 `{new}`", 1)
    return {"PROVINCE.md": newprov, "SCORECARD.md": sc}


def m_firsts_set():
    sc = read("SCORECARD.md")
    needle = "`registry/digest-ledger.tsv` | 42 |"
    i = sc.rfind(needle)                      # canon row only; head Capabilities keeps 42
    assert i > 0
    sc = sc[:i] + "`registry/digest-ledger.tsv` | 41 |" + sc[i + len(needle):]
    return {"SCORECARD.md": sc}


def m_sat_line_typed():
    sc = read("SCORECARD.md")
    assert "Saturation line **8/10**" in sc
    return {"SCORECARD.md": sc.replace("Saturation line **8/10**", "Saturation line **7/10**", 1)}


def m_receipt_missing(with_exempt):
    sc = read("SCORECARD.md")
    tok = "`.ufo/waves/round-41/missing-receipt.md`"
    sc = insert_after_heading(sc, r"^## Round 41 \u2014", f"Missing receipt cited: {tok}.")
    if with_exempt:
        sc = insert_after_heading(sc, r"^### Round-40 record corrections", f"Correction row quotes {tok}.")
    return {"SCORECARD.md": sc}


def m_hash_corrupt():
    sc = read("SCORECARD.md")
    old = "36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3"
    assert old in sc
    return {"SCORECARD.md": sc.replace(old, "46b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3", 1)}


def m_fake_needle():
    sc = read("SCORECARD.md")
    old = "run `python3 tools/pin-watch.py selftest` \u2192 `selftest pass=9 fail=0`"
    assert old in sc, "operability selftest run fact not found"
    new = "run `bash -c 'echo selftest pass=9 fail=0; : pin-watch.py selftest'` \u2192 `selftest pass=9 fail=0`"
    return {"SCORECARD.md": sc.replace(old, new, 1)}


MUTANTS = [
    ("A-extra-axis-row", m_extra_axis),
    ("B-stale-dup-sections", m_dup_sections),
    ("C-substring-counts", m_substring_counts),
    ("D-province-substring", m_province_substring),
    ("E-firsts-set-collapse", m_firsts_set),
    ("F-sat-line-typed", m_sat_line_typed),
    ("G1-receipt-missing-no-exempt", lambda: m_receipt_missing(False)),
    ("G2-receipt-missing-exempted", lambda: m_receipt_missing(True)),
    ("K-hash-corrupt", m_hash_corrupt),
    ("M-fake-needle", m_fake_needle),
]


def measure(name, tip, here=None):
    script = os.path.join(here or f"{CLONE}/tools", "round42-selfdesc-reconcile.py")
    out = f"{SEAT}/mut-{name}.out"
    p = subprocess.run([sys.executable, script, "--repo", CLONE, "--tip", tip, "--out", out],
                       cwd=CLONE, capture_output=True, text=True, env=ENV)
    lines = p.stdout.splitlines()
    summary = lines[1] if len(lines) > 1 else p.stderr.strip()[:300]
    details = [l for l in lines if l.startswith("detail:")]
    return p.returncode, summary, details


def main():
    if git("rev-parse", "--show-toplevel").stdout.strip() != CLONE:
        sys.exit(f"toplevel mismatch: {git('rev-parse','--show-toplevel').stdout}")
    git("checkout", "-q", "--detach", BASE)
    if git("status", "--porcelain").stdout.strip():
        sys.exit("dirty tree before battery")
    results = []
    for name, fn in MUTANTS:
        git("reset", "-q", "--hard", BASE)
        for path, text in fn().items():
            write(path, text)
        c = git("-c", "user.name=R42A06", "-c", "user.email=r42a06@seat.local",
                "commit", "-q", "-am", f"mutant {name}")
        if c.returncode:
            results.append((name, "COMMIT-FAIL", c.stderr.strip()[:200], []))
            continue
        tip = git("rev-parse", "HEAD").stdout.strip()
        rc, summary, details = measure(name, tip)
        results.append((name, rc, summary, details))
        print(f"### {name} tip={tip[:8]} exit={rc}\n    {summary}")
        for d in details[:6]:
            print("    " + d)
    # provenance: same corrupt-hash tip, but r41 module taken from a doctored directory
    git("reset", "-q", "--hard", BASE)
    write("SCORECARD.md", m_hash_corrupt()["SCORECARD.md"])
    git("-c", "user.name=R42A06", "-c", "user.email=r42a06@seat.local",
        "commit", "-q", "-am", "mutant K-hash-corrupt (provenance probe)")
    tip = git("rev-parse", "HEAD").stdout.strip()
    here = f"{SEAT}/here"
    os.makedirs(here, exist_ok=True)
    for f in ("round42-selfdesc-reconcile.py", "round41-scorecard-reconcile.py"):
        write_src = open(f"{CLONE}/tools/{f}").read()
        open(f"{here}/{f}", "w").write(write_src)
    with open(f"{here}/round41-scorecard-reconcile.py", "a") as f:
        f.write("\n\n_real = evaluate\n\n\ndef evaluate(repo, tip):\n"
                "    c, d = _real(repo, tip)\n    c['mismatches'] = 0\n    return c, d\n")
    rc, summary, details = measure("K-stub-r41", tip, here=here)
    print(f"### K-stub-r41 (doctored working-tree r41 module) tip={tip[:8]} exit={rc}\n    {summary}")
    for d in details[:4]:
        print("    " + d)
    results.append(("K-stub-r41", rc, summary, details))
    git("reset", "-q", "--hard", BASE)
    import json
    json.dump([{"mutant": n, "exit": r, "summary": s, "details": d} for n, r, s, d in results],
              open(f"{SEAT}/battery.json", "w"), indent=1)


main()
