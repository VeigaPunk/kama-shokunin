import os, re, sys, importlib.util
sys.path.insert(0, "/fast/scratch/hyaku/kama-r57/R57Item32CounterSemantics")
from driver import *
PIN = "7c873d7b4e3839489a93d6334cdf93fe5d34d19f"

def repair_calibration(t):
    old = "`python3 -c \"import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))\"` → `42`"
    assert t.count(old) == 1
    return t.replace(old, old.replace("`42`", "`43`"))

def shadow_retired(t):
    lines = t.split("\n")
    i = lines.index("## Retired")
    j = i + 1
    while j < len(lines) and not lines[j].startswith("## "):
        j += 1
    stale = ["Both assigned axes are retired; every model endpoint is dead.", ""]
    shadow = ["```text", "## Retired", "6 axes; 11 capabilities.", "```", ""]
    return "\n".join(lines[:i] + shadow + ["## Retired"] + stale + lines[j:])

def colon_canon(t):
    rows = ["| Capability | What it can now do | Evidence pointer | First-working round |",
            "|---|---|---|---|"]
    rows.append("| sources-registry | x | `corpus/SOURCES.md` | 10 |")
    rows.append("| shadow-cap-r57 | decoy row for the colon-heading test | `tools/none.py` | 57 |")
    block = "**Capabilities — canonical list as of round 57:**\n\nDecoy table, colon heading form.\n\n" + "\n".join(rows) + "\n\n"
    anchor = "## Historical authority banner — round 55"
    assert t.count(anchor) == 1
    return t.replace(anchor, block + anchor)

def drop_round49_table(t):
    lines = t.split("\n")
    i = [k for k, l in enumerate(lines) if "canonical list as of round 49**" in l][0]
    j = i + 1
    while j < len(lines) and not lines[j].startswith("|"): j += 1
    k = j
    while k < len(lines) and lines[k].startswith("|"): k += 1
    return "\n".join(lines[:j] + ["(table moved elsewhere)"] + lines[k:])

def fenced_round_quote(t):
    anchor = "## Historical authority banner — round 55"
    block = "`````text\n## Round 57 — quoted planned text\n`````\n\n"
    return t.replace(anchor, block + anchor)

def unspaced_round57(t):
    anchor = "## Historical authority banner — round 55"
    block = "## Round57 — measured round 57 (unspaced heading)\n\nMeasured text for round 57 that the counter must see.\n\n"
    return t.replace(anchor, block + anchor)

if __name__ == "__main__":
    base = f"{FX}/base"
    clone(LANE, base)
    r = sh("git", "checkout", "-q", "--detach", PIN, cwd=base); assert r.returncode == 0, r.stderr
    assert_top(base)
    report(f"F0-base-{PIN[:8]}", base)
    scen = {
        "F1-repaired-calibration-count": [repair_calibration],
        "F2-shadow-retired": [repair_calibration, shadow_retired],
        "F3-colon-canonical-round57": [repair_calibration, colon_canon],
        "F4-drop-round49-table": [repair_calibration, drop_round49_table],
        "F5-fenced-round57-quote": [repair_calibration, fenced_round_quote],
        "F6-unspaced-round57-heading": [repair_calibration, unspaced_round57],
    }
    for name, fns in scen.items():
        d = f"{FX}/{name}"
        clone(base, d)
        r = sh("git", "checkout", "-q", "--detach", PIN, cwd=d); assert r.returncode == 0, r.stderr
        assert_top(d)
        def comp(t, fns=fns):
            for f in fns: t = f(t)
            return t
        mutate_commit(d, name, comp)
        report(name, d)
