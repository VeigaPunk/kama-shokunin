#!/usr/bin/env python3
"""R42A03 C1 fact-mutation driver (kama round 42).

Sandbox: /fast/scratch/kama-r42/seats/R42A03/clone (branch `mutants`, claim tip
3d9bd8d72366e281fab291874524130428ee423d). For every mutant: reset --hard to the
claim tip, apply ONE single-token edit to SCORECARD.md / README.md / PROVINCE.md,
commit with git -C, run tools/round42-selfdesc-reconcile.py at the mutant commit
(TMPDIR pointed at the seat's private tmp), record summary+exit, then move on.
Ends with a reset to the pristine tip, byte-hash comparison and a restored-bytes
counter run. Never touches /fast/scratch/kama-r42/clone.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

SEAT = "/fast/scratch/kama-r42/seats/R42A03"
CLONE = os.path.join(SEAT, "clone")
OUT = os.path.join(SEAT, "out")
TMP = os.path.join(SEAT, "tmp")
PRIS = os.path.join(SEAT, "pristine")
TIP = "3d9bd8d72366e281fab291874524130428ee423d"
FILES = ("SCORECARD.md", "README.md", "PROVINCE.md")
for d in (OUT, TMP, PRIS):
    os.makedirs(d, exist_ok=True)


def git(*a):
    p = subprocess.run(["git", "-C", CLONE, *a], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(a), p.stderr))
    return p.stdout.strip()


def counter(tip, outpath):
    env = dict(os.environ, TMPDIR=TMP)
    p = subprocess.run(
        [sys.executable, "tools/round42-selfdesc-reconcile.py",
         "--repo", CLONE, "--tip", tip, "--out", outpath],
        capture_output=True, text=True, cwd=CLONE, env=env, timeout=900)
    summary = ""
    for line in p.stdout.splitlines():
        if "mismatches=" in line:
            summary = line
    return {"exit": p.returncode, "summary": summary,
            "stderr": p.stderr.strip()[:400]}


ROW_DL = ("| digest-ledger | Find every full SHA-256 the lane's documents cite and "
          "classify it: a committed blob, a ledger-declared external artifact re-hashed "
          "on this host, an unverifiable digest with its reason, or a flagged known-wrong "
          "digest; exit 1 on any unexplained digest | `tools/digest-ledger.py`; "
          "`registry/digest-ledger.tsv` | 42 |\n")

MUTS = [
    dict(id="M01", leg="banner", file="SCORECARD.md", n=1,
         old="the assigned axes are operability + calibration (`shokunin.conf`",
         new="the assigned axes are operability & calibration (`shokunin.conf`"),
    dict(id="M02", leg="banner", file="SCORECARD.md", n=1,
         old="Latest measured round: 42", new="Latest measured round: 41"),
    dict(id="M03", leg="banner", file="SCORECARD.md", n=1,
         old="still says operability + freshness, an open L0 question since round 35). Latest measured round: 42",
         new="still says operability and freshness, an open L0 question since round 35). Latest measured round: 42"),
    dict(id="M04", leg="planned", file="SCORECARD.md", n=1,
         old="The live plan is `### Planned (round 43)`",
         new="The live plan is `### Planned (round 42)`"),
    dict(id="M05", leg="planned (heading at line 2271)", file="SCORECARD.md", n=1,
         old="\n### Planned (round 43)\n", new="\n### Planned (round 44)\n"),
    dict(id="M06", leg="planned (numbered item)", file="SCORECARD.md", n=1,
         old="1. Calibration: the second half", new="- Calibration: the second half"),
    dict(id="M07", leg="planned (forbidden continuation path)", file="SCORECARD.md", n=1,
         old="Superseded in round 42. The live plan",
         new="Superseded in round 42; see `.ufo/round-5/continuation.md`. The live plan"),
    dict(id="M08", leg="planned (forbidden freshness move)", file="SCORECARD.md", n=1,
         old="Superseded in round 42. The live plan",
         new="Superseded in round 42; the next freshness move is queued. The live plan"),
    dict(id="M09", leg="retired (axes count)", file="SCORECARD.md", n=1,
         old="None. 6 axes and 8 capabilities", new="None. 5 axes and 8 capabilities"),
    dict(id="M10", leg="retired (capabilities count)", file="SCORECARD.md", n=1,
         old="None. 6 axes and 8 capabilities", new="None. 6 axes and 7 capabilities"),
    dict(id="M11", leg="retired (forbidden Both assigned axes)", file="SCORECARD.md", n=1,
         old="None. 6 axes", new="None. Both assigned axes retired; 6 axes"),
    dict(id="M12", leg="retired (forbidden every endpoint dead)", file="SCORECARD.md", n=1,
         old="sample DEAD (`registry/history/latest.tsv`; restoring a serving runtime is operator-owned), while the lane-owned llama.cpp fixture reaches",
         new="sample DEAD (`registry/history/latest.tsv`; every model endpoint is dead; restoring a serving runtime is operator-owned), while the lane-owned llama.cpp fixture reaches"),
    dict(id="M13", leg="saturation (nudge flip)", file="SCORECARD.md", n=1,
         old="so nudge inactive. A capability", new="so nudge active. A capability"),
    dict(id="M14", leg="saturation (vector score)", file="SCORECARD.md", n=1,
         old="score vector operability 8, freshness 8",
         new="score vector operability 9, freshness 8"),
    dict(id="M15", leg="saturation (first-working rounds)", file="SCORECARD.md", n=1,
         old="capability first-working rounds 10, 14, 16, 20, 25, 30, 41, 42",
         new="capability first-working rounds 9, 14, 16, 20, 25, 30, 41, 42"),
    dict(id="M16", leg="saturation (forbidden 8/10 phrasing)", file="SCORECARD.md", n=1,
         old="Saturation line **8/10** (declared round 10, unchanged)",
         new="Saturation line **8/10 on every owned axis** (declared round 10, unchanged)"),
    dict(id="M17", leg="saturation (vector coverage)", file="SCORECARD.md", n=1,
         old="score vector operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7",
         new="score vector operability 8, freshness 8, depth 7, coverage 8, calibration 7, adjacency 7"),
    dict(id="M18", leg="caps (drop head capability row)", file="SCORECARD.md", n=2, first=True,
         old=ROW_DL, new=""),
    dict(id="M19", leg="caps (rename head capability)", file="SCORECARD.md", n=3, first=True,
         old="| pin-watch | List upstream release tags",
         new="| pin-watch2 | List upstream release tags"),
    dict(id="M20", leg="probe: head-table first-working column unchecked", file="SCORECARD.md", n=2, first=True,
         old="`tools/digest-ledger.py`; `registry/digest-ledger.tsv` | 42 |",
         new="`tools/digest-ledger.py`; `registry/digest-ledger.tsv` | 43 |"),
    dict(id="M22", leg="r41 score (operability)", file="SCORECARD.md", n=1,
         old="| **operability** | **8** | registry gate",
         new="| **operability** | **9** | registry gate"),
    dict(id="M23", leg="r41 score (calibration)", file="SCORECARD.md", n=1,
         old="| calibration | **7** | run `python3 tools/capability-repertoire-audit.py",
         new="| calibration | **8** | run `python3 tools/capability-repertoire-audit.py"),
    dict(id="M24", leg="r41 hash fact", file="SCORECARD.md", n=1,
         old="sha256 `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`",
         new="sha256 `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d4`"),
    dict(id="M25", leg="r41 lines fact", file="SCORECARD.md", n=1,
         old="(1138 lines)", new="(1137 lines)"),
    dict(id="M26", leg="r41 run fact (expected output)", file="SCORECARD.md", n=1,
         old="run `python3 tools/pin-watch.py selftest` → `selftest pass=9 fail=0`",
         new="run `python3 tools/pin-watch.py selftest` → `selftest pass=8 fail=0`"),
    dict(id="M27", leg="r41 run + rel needle (calibration glob)", file="SCORECARD.md", n=1,
         old="glob.glob('corpus/lessons/*verifier-spotcheck.md')",
         new="glob.glob('corpus/lessons/*verifier-spotchek.md')"),
    dict(id="M28", leg="r41 run + rel needle (operability cmd)", file="SCORECARD.md", n=1,
         old="run `python3 tools/pin-watch.py selftest` → `selftest pass=9 fail=0`",
         new="run `python3 tools/pin-wath.py selftest` → `selftest pass=9 fail=0`"),
    dict(id="M29", leg="r41 dead/hash path (depth)", file="SCORECARD.md", n=1,
         old="`corpus/knowledge/endpoint-identity.md` sha256 `0100ac6d",
         new="`corpus/knowledge/endpoint-identiy.md` sha256 `0100ac6d"),
    dict(id="M30", leg="readme (top-level name)", file="README.md", n=1,
         old="- `tests/` — fixtures", new="- `test/` — fixtures"),
    dict(id="M31", leg="readme (drop top-level bullet)", file="README.md", n=1,
         old="- `LOG.md` — append-only round log: the evidence that motivated each change\n",
         new=""),
    dict(id="M32", leg="probe: extra README name unchecked", file="README.md", n=1,
         old="- `MINT.md` — the mint record\n",
         new="- `MINT.md` — the mint record (see also `HANDBOOK.md`)\n"),
    dict(id="M33", leg="province (drop ledger tsv token)", file="PROVINCE.md", n=1,
         old="`tools/digest-ledger.py` with `registry/digest-ledger.tsv` (classification",
         new="`tools/digest-ledger.py` (classification"),
    dict(id="M34", leg="province (rename pin-watch token)", file="PROVINCE.md", n=1,
         old="`tools/pin-watch.py` with `registry/engine-pins.tsv` (newer-release",
         new="`tools/pin-watchx.py` with `registry/engine-pins.tsv` (newer-release"),
    dict(id="M35", leg="probe: province token not cited by canon", file="PROVINCE.md", n=1,
         old="`tools/kama-probe.sh listeners` (`ss -ltn`",
         new="`tools/kama-probe.sh listenerz` (`ss -ltn`"),
]


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    results = []
    git("reset", "--hard", TIP)
    for f in FILES:
        shutil.copy2(os.path.join(CLONE, f), os.path.join(PRIS, f))
    pristine_hashes = {f: sha256(os.path.join(PRIS, f)) for f in FILES}
    pristine_before = counter(TIP, os.path.join(OUT, "pristine-before.out"))
    print("PRISTINE-BEFORE", pristine_before, flush=True)

    for m in MUTS:
        rec = dict(id=m["id"], leg=m["leg"], file=m["file"])
        try:
            git("reset", "--hard", TIP)
            path = os.path.join(CLONE, m["file"])
            text = open(path, encoding="utf-8").read()
            cnt = text.count(m["old"])
            if cnt != m["n"]:
                rec["error"] = "anchor count %d != expected %d" % (cnt, m["n"])
                results.append(rec)
                print("SKIP", m["id"], rec["error"], flush=True)
                continue
            open(path, "w", encoding="utf-8").write(
                text.replace(m["old"], m["new"], 1))
            git("add", m["file"])
            git("commit", "-q", "-m", "mutant %s: %s" % (m["id"], m["leg"]))
            rec["commit"] = git("rev-parse", "HEAD")
            rec["result"] = counter(rec["commit"],
                                    os.path.join(OUT, "%s.out" % m["id"]))
            print(m["id"], m["leg"], "->", rec["result"]["exit"],
                  rec["result"]["summary"], flush=True)
        except Exception as e:  # noqa: BLE001 - record and continue
            rec["error"] = repr(e)[:400]
            print("ERR", m["id"], rec["error"], flush=True)
        results.append(rec)

    git("reset", "--hard", TIP)
    restored = {
        "head": git("rev-parse", "HEAD"),
        "status_porcelain": git("status", "--porcelain"),
        "hashes_match_pristine": {f: sha256(os.path.join(CLONE, f)) == pristine_hashes[f]
                                  for f in FILES},
    }
    pristine_after = counter(TIP, os.path.join(OUT, "pristine-after.out"))
    out = {
        "tip": TIP,
        "pristine_before": pristine_before,
        "mutants": results,
        "restored": restored,
        "pristine_after": pristine_after,
        "tmp_leftover": sorted(os.listdir(TMP)),
    }
    with open(os.path.join(SEAT, "results.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print("RESTORED", restored, flush=True)
    print("PRISTINE-AFTER", pristine_after, flush=True)
    print("DONE mutants=%d" % len(results), flush=True)


if __name__ == "__main__":
    main()
