#!/usr/bin/env python3
"""C1 critic probes for kama tools/report-landing-audit.py (round 21, draft a29bb84).

Read-only against the lane and fleet repos. Fixtures and a throwaway lane clone live
under /tmp/kama-r21-C1ClaimCritic/probe (recreated on every run). Each probe states the
exit code and a summary substring it expects; a mismatch prints MISMATCH and the script
exits 1. Transcript: probe-transcript.txt next to this file. Stdlib + git only.
Usage: python3 c1_probes.py
"""
import datetime
import json
import os
import pathlib
import platform
import shutil
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
GATE = f"{LANE}/tools/report-landing-audit.py"
LEDGER = pathlib.Path(LANE, "registry/report-landing-errata.tsv")
A29 = "a29bb84abbb8b4d328f5970a89e448330a3a42ac"      # draft commit under attack
BOGUS = "0957ce619789d13d894ef21bc863486bcb35b56c"    # r20 report line 7 (closure D1)
R20_FIX = "0957ce619789d13bb5779606078fa1498114d2c7"  # measured commit (r20 line 10)
SCR = pathlib.Path("/tmp/kama-r21-C1ClaimCritic/probe")
OUT = pathlib.Path(__file__).resolve().parent
LOG = []
RESULTS = []


def say(line):
    LOG.append(line)
    print(line, flush=True)


def git(repo, *args, env=None):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=env)


def genv(author, when):
    return dict(os.environ, GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
                GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
                GIT_AUTHOR_DATE=f"@{when} +0000", GIT_COMMITTER_DATE=f"@{when} +0000")


def gate(*args, lane=LANE, fleet=FLEET):
    p = subprocess.run(["python3", GATE, "--lane-repo", str(lane), "--fleet-repo", str(fleet), *args],
                       capture_output=True, text=True, cwd="/tmp")
    return p.returncode, p.stdout, p.stderr


def check(name, want_rc, got, contains=(), forbids=()):
    rc, out, err = got
    text = out + err
    ok = rc == want_rc and all(c in text for c in contains) and not any(f in text for f in forbids)
    line = next((l for l in out.splitlines() if l.startswith("summary")), "") or \
        next((l for l in text.splitlines() if "selftest" in l or "could-not" in l), "")
    RESULTS.append(ok)
    say(f"[{'OK' if ok else 'MISMATCH'}] {name} | exit={rc} (want {want_rc}) | {line.strip()}")
    return rc, out, err


def write(path, text):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return str(path)


def into_landed(text, block):
    """Insert block at the end of the '## Landed changes' section (before the next '## ')."""
    start = text.index("## Landed changes")
    cut = text.index("\n## ", start + 5) + 1
    return text[:cut] + block + "\n" + text[cut:]


def main():
    if SCR.exists():
        shutil.rmtree(SCR)
    SCR.mkdir(parents=True)
    gitver = subprocess.run(["git", "--version"], capture_output=True, text=True).stdout.strip()
    say(f"# C1 probes {datetime.datetime.now().isoformat(timespec='seconds')} "
        f"python={platform.python_version()} {gitver}")
    base20 = pathlib.Path(FLEET, ".ufo/reports/round-20/kama.md").read_text(encoding="utf-8")
    base19 = pathlib.Path(FLEET, ".ufo/reports/round-19/kama.md").read_text(encoding="utf-8")
    ledger = LEDGER.read_text(encoding="utf-8")

    say("== official commands and population ==")
    check("P0 raw baseline, default window 10-20", 1, gate("--no-errata"),
          ["defects=9 ", "uncorrected=9 "])
    check("P1 default ledger, default window 10-20", 0, gate(),
          ["corrected=9 ", "status=clean"])
    check("P2 selftest", 0, gate("--selftest"), ["cases=15 failed=0"])
    check("P3 window includes absent r21 report", 2, gate("--rounds", "10-21", "--no-errata"),
          ["could-not-evaluate"])
    check("P4 wide raw population 1,2,4,6-20 (r3,r5 absent)", 1,
          gate("--rounds", "1,2,4,6-20", "--no-errata"), ["defects=19 "])

    say("== round-21 draft path ==")
    d1 = write(SCR / "d1.md", f"# probe\n## Work performed\nC1 calibration 7 -> 9 (unsupported probe).\n"
                              f"## Landed changes\n- `{A29}` round-21 commit\n## Before → after\nnone\n")
    check("P5a r21-only run with default ledger", 1, gate("--rounds", "21", "--report", f"21={d1}"),
          ["errata_unmatched=9 "])
    check("P5b default population, draft with unsupported claim", 0, gate("--report", f"21={d1}"),
          ["status=clean"])
    d2 = write(SCR / "d2.md", "# probe\n## Landed changes\n- none\n")
    check("P6 draft that omits a29bb84", 1, gate("--report", f"21={d2}"),
          ["UNCORRECTED landed-omitted"])
    d3u = write(SCR / "d3u.md", f"# probe\n## Landed changes\n- `{A29}`\n## Work performed\n"
                                f"bogus `{BOGUS.upper()}`\n")
    check("P7a uppercase bogus 40-hex passes (false negative)", 0,
          gate("--rounds", "21", "--report", f"21={d3u}", "--no-errata"), ["defects=0 "])
    d3l = write(SCR / "d3l.md", f"# probe\n## Landed changes\n- `{A29}`\n## Work performed\nbogus `{BOGUS}`\n")
    check("P7b lowercase bogus 40-hex fails (control)", 1,
          gate("--rounds", "21", "--report", f"21={d3l}", "--no-errata"), ["unresolved-full-hash"])
    d7 = write(SCR / "d7.md", f"# probe\n## Landed changes\n- `{A29}` round-21 commit; defaced prose\n")
    check("P8 hex-letter prose word inside Landed fails", 1,
          gate("--rounds", "21", "--report", f"21={d7}", "--no-errata"), ["landed-unresolved defaced"])

    say("== round-20 mutants of the committed text (draft mode, raw) ==")
    v1 = write(SCR / "v1.md", base20.replace(BOGUS, BOGUS.upper()))
    check("P9 r20 bogus hash uppercased (defect disappears)", 1,
          gate("--rounds", "20", "--report", f"20={v1}", "--no-errata"), ["defects=4 "])
    omit4 = ["33a6777866d0f63d894ef21bc863486bcb35b56c", R20_FIX,
             "92b146253fd3a8c4bfade94c909dc63b13d6f4a8", "846e366dc9dbac58463494a7e05ad060ae3ed3b0"]
    v2 = write(SCR / "v2.md", into_landed(base20, "# Addendum\n" + "\n".join(f"- `{h}`" for h in omit4) + "\n"))
    check("P10 four omitted commits moved under '# Addendum' inside Landed", 1,
          gate("--rounds", "20", "--report", f"20={v2}", "--no-errata"), ["defects=1 "])
    v3 = write(SCR / "v3.md", into_landed(base20, "- `846e366` — NOT landed (rejected in review)\n"))
    check("P11 omitted commit listed as NOT landed inside Landed", 1,
          gate("--rounds", "20", "--report", f"20={v3}", "--no-errata"), ["defects=4 "])
    v4 = write(SCR / "v4.md", base20.replace("## Landed changes", "## Landed", 1))
    raw4 = check("P12a Landed heading renamed (raw)", 1,
                 gate("--rounds", "20", "--report", f"20={v4}", "--no-errata", "--json"),
                 ['"defects": 11'])
    doc = json.loads(raw4[1])
    rows = []
    for res in doc["results"]:
        for d in res["defects"]:
            corr = {"unresolved-full-hash": R20_FIX, "landed-section-missing": "x"}.get(d["kind"], d["token"])
            rows.append(f"{res['round']}\t{d['kind']}\t{d['token']}\t{corr}\tauto-generated from gate --json")
    auto = write(SCR / "v4-auto-ledger.tsv", "\n".join(ledger.splitlines()[:2] + rows) + "\n")
    check("P12b same report; ledger rows generated from the gate's own JSON", 0,
          gate("--rounds", "20", "--report", f"20={v4}", "--errata", auto), ["corrected=11 ", "status=clean"])
    v5 = write(SCR / "v5.tsv", ledger.replace(f"{BOGUS}\t{R20_FIX}",
                                              f"{BOGUS}\t7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d"))
    check("P13 real ledger; hash correction retargeted to unrelated commit 7a6bc91", 0,
          gate("--errata", v5), ["status=clean"])
    v6 = write(SCR / "v6.tsv", ledger.replace("round-20 report line 7 splices",
                                              "round-20 report line 7 contains a hash"))
    check("P14 existing ledger row evidence rewritten (no append-only check)", 0,
          gate("--errata", v6), ["status=clean"])

    say("== exemptions, precision and ancestry ==")
    check("P15a r19 as committed: post-report exemption in force", 0,
          gate("--rounds", "19", "--no-errata"), ["defects=0 "])
    v19 = write(SCR / "v19.md", base19)
    check("P15b same r19 text audited as a pre-commit draft", 1,
          gate("--rounds", "19", "--report", f"19={v19}", "--no-errata"), ["defects=4 "])
    v8 = write(SCR / "v8.md", into_landed(base20, "- measured 2026102 rows\n"))
    check("P16 numeric token inside Landed flagged as an unresolved commit", 1,
          gate("--rounds", "20", "--report", f"20={v8}", "--no-errata"), ["landed-unresolved 2026102"])
    tree = git(LANE, "rev-parse", f"{A29}^{{tree}}").stdout.strip()
    v9 = write(SCR / "v9.md", base20 + f"\nTree probe `{tree}`\n")
    check("P17 tree object cited in prose passes the full-hash check", 1,
          gate("--rounds", "20", "--report", f"20={v9}", "--no-errata"), ["defects=5 "],
          forbids=[f"unresolved-full-hash {tree}"])

    am = SCR / "amend"
    LN, FL = am / "lane", am / "fleet"
    LN.mkdir(parents=True)
    FL.mkdir(parents=True)
    git(LN, "init", "-q", "-b", "master")
    git(FL, "init", "-q", "-b", "master")
    (LN / "f").write_text("a\n", encoding="utf-8")
    git(LN, "add", "f", env=genv("kama-shokunin", 1000))
    git(LN, "commit", "-q", "-m", "round-1: work", env=genv("kama-shokunin", 1000))
    a = git(LN, "rev-parse", "HEAD").stdout.strip()
    (LN / "f").write_text("a\nb\n", encoding="utf-8")
    git(LN, "add", "f", env=genv("kama-shokunin", 1100))
    git(LN, "commit", "-q", "-m", "round-1: measure", env=genv("kama-shokunin", 1100))
    write(FL / ".ufo/reports/round-1/kama.md", f"# r1\n## Landed changes\n- `{a[:9]}` work\n")
    git(FL, "add", ".ufo/reports/round-1/kama.md", env=genv("kama-shokunin", 1200))
    git(FL, "commit", "-q", "-m", "round-1: kama report", env=genv("kama-shokunin", 1200))
    check("P18a fixture: uncited round-1 commit before the report fails", 1,
          gate("--rounds", "1", "--no-errata", lane=LN, fleet=FL), ["UNCORRECTED landed-omitted"])
    git(LN, "commit", "-q", "--amend", "-m", "round-1: measure (amended after report)",
        env=genv("kama-shokunin", 1300))
    check("P18b same commit amended after the report: requirement lapses", 0,
          gate("--rounds", "1", "--no-errata", lane=LN, fleet=FL), ["defects=0 "])

    clone = SCR / "lane-clone"
    subprocess.run(["git", "clone", "-q", LANE, str(clone)], check=True, capture_output=True)
    orphan = git(clone, "commit-tree", git(clone, "rev-parse", f"{A29}^{{tree}}").stdout.strip(),
                 "-m", "round-21: orphan probe (not on master)",
                 env=genv("kama-shokunin", 1792578300)).stdout.strip()
    anc = subprocess.run(["git", "-C", str(clone), "merge-base", "--is-ancestor", orphan, "master"]).returncode
    d5 = write(SCR / "d5.md", f"# probe\n## Landed changes\n- `{A29}` round-21 commit\n"
                              f"- `{orphan}` orphan probe commit\n")
    check(f"P19 cites non-ancestor commit {orphan[:9]} (is-ancestor rc={anc}) as landed", 0,
          gate("--rounds", "21", "--report", f"21={d5}", "--no-errata", lane=clone), ["defects=0 "])

    say(f"== {sum(RESULTS)}/{len(RESULTS)} probes matched expectation ==")
    (OUT / "probe-transcript.txt").write_text("\n".join(LOG) + "\n", encoding="utf-8")
    return 0 if all(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
