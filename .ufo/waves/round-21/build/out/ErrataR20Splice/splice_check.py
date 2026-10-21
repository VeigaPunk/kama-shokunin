#!/usr/bin/env python3
"""Read-only check of the round-20 unresolved-full-hash errata row (token 0957ce61...).

Plumbing only: cat-file, log --find-object, merge-base, diff --quiet between two
commits, ls-tree, show. Writes nothing. Exit 0 iff every PASS/FAIL observation
below reproduces; INFO lines are measured values.
"""
import json
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
LANE_HEAD = "a29bb84abbb8b4d328f5970a89e448330a3a42ac"
TOKEN = "0957ce619789d13d894ef21bc863486bcb35b56c"  # round-20 report line 7 (defective)
CORR = "0957ce619789d13bb5779606078fa1498114d2c7"   # errata row 3 correction (measured tree)
WORK = "33a6777866d0f63d894ef21bc863486bcb35b56c"   # work/frozen-population commit
ERRATA_COMPOSITION = CORR[:16] + WORK[-24:]         # composition claimed by errata row 3 evidence
FLEET_ORIGIN = "04eb5d2d9b4712c5266bdc36fbb16c2fefd7b392"  # first fleet commit with TOKEN
LANE_ORIGIN = {"00aa1486a0dee3375d6e974adc45ee501d7ab4d7", LANE_HEAD}
HEX = set("0123456789abcdef")
failures = []


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not ok:
        failures.append(name)


def info(name, value):
    print(f"INFO {name}: {value}")


def lcp(a, b):
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


def hamming(a, b):
    return sum(x != y for x, y in zip(a, b))


def object_scan(repo, needle):
    """Every object in the store (reachable or not): count, blobs containing needle, commit ids."""
    proc = subprocess.Popen(["git", "-C", repo, "cat-file", "--batch-all-objects", "--batch"],
                            stdout=subprocess.PIPE)
    total, hits, commits = 0, [], []
    while True:
        header = proc.stdout.readline()
        if not header:
            break
        oid, kind, size = header.split()
        body = proc.stdout.read(int(size))
        proc.stdout.read(1)
        total += 1
        if kind == b"commit":
            commits.append(oid.decode())
        if needle in body:
            hits.append((oid.decode(), kind.decode()))
    proc.wait()
    return total, hits, commits


def main():
    for name, h in (("TOKEN", TOKEN), ("CORR", CORR), ("WORK", WORK)):
        check(f"{name} is 40 lowercase hex", len(h) == 40 and set(h) <= HEX)

    # 1. Which real commits does the token splice?
    lane_total, lane_hits, lane_commits = object_scan(LANE, TOKEN.encode())
    fleet_total, fleet_hits, fleet_commits = object_scan(FLEET, TOKEN.encode())
    commits = set(lane_commits) | set(fleet_commits)
    info("lane objects scanned / commit objects", f"{lane_total} / {len(lane_commits)}")
    info("fleet objects scanned / commit objects", f"{fleet_total} / {len(fleet_commits)}")
    pref = {c: lcp(TOKEN, c) for c in commits}
    suff = {c: lcp(TOKEN[::-1], c[::-1]) for c in commits}
    best_p = max(pref.items(), key=lambda kv: kv[1])
    best_s = max(suff.items(), key=lambda kv: kv[1])
    info("longest prefix donor (commit, lcp)", best_p)
    info("longest suffix donor (commit, lcs)", best_s)
    splices = []
    for a in commits:
        for b in commits:
            if a == b or pref[a] < 8 or suff[b] < 8:
                continue
            ks = [k for k in range(40 - suff[b], pref[a] + 1) if 1 <= k <= 39]
            if ks:
                splices.append((a, b, ks))
    for a, b, ks in splices:
        info("splice (prefix donor, suffix donor, split indexes)", f"{a} + {b} k={ks}")
    check("exactly one prefix/suffix splice pair with >=8 matched chars", len(splices) == 1)
    check("that pair is (CORR, WORK)", len(splices) == 1 and splices[0][:2] == (CORR, WORK))
    check("TOKEN == CORR[:15] + WORK[15:]", TOKEN == CORR[:15] + WORK[15:])
    check("errata row 3 composition CORR[:16]+WORK[-24:] does NOT reproduce TOKEN",
          ERRATA_COMPOSITION != TOKEN, ERRATA_COMPOSITION)
    info("Hamming(TOKEN, CORR) / Hamming(TOKEN, WORK)", f"{hamming(TOKEN, CORR)} / {hamming(TOKEN, WORK)}")
    info("index 15 of TOKEN / CORR / WORK", f"{TOKEN[15]} / {CORR[15]} / {WORK[15]}")

    # 2. Object existence
    check("TOKEN is not an object in lane or fleet",
          all(git(r, "cat-file", "-e", TOKEN).returncode != 0 for r in (LANE, FLEET)))
    check("CORR is a lane commit", git(LANE, "cat-file", "-t", CORR).stdout.strip() == "commit")
    check("WORK is a lane commit", git(LANE, "cat-file", "-t", WORK).stdout.strip() == "commit")
    check("CORR and WORK are not fleet objects",
          all(git(FLEET, "cat-file", "-e", h).returncode != 0 for h in (CORR, WORK)))

    # 3. What the report says (blob committed at the first fleet commit)
    report = git(FLEET, "show", f"{FLEET_ORIGIN}:.ufo/reports/round-20/kama.md").stdout
    lines = report.splitlines()
    check("report@04eb5d2d: TOKEN occurs once, on line 7",
          report.count(TOKEN) == 1 and lines[6].count(TOKEN) == 1)
    check("report line 10 cites CORR", lines[9].count(CORR) == 1)
    check("report never contains WORK's 8-hex prefix 33a67778", WORK[:8] not in report)
    check("report lines 21-27 (measurement table) contain no 0957ce61 hex",
          all(CORR[:8] not in ln and TOKEN[:8] not in ln for ln in lines[20:27]))

    # 4. Role of each commit in the round-20 documents (lane HEAD)
    log_md = git(LANE, "show", f"{LANE_HEAD}:LOG.md").stdout.splitlines()
    sc_md = git(LANE, "show", f"{LANE_HEAD}:SCORECARD.md").stdout.splitlines()
    check("LOG.md:1204 names WORK as landed work/frozen population", WORK in log_md[1203])
    check("LOG.md:1206 names CORR as measured", CORR in log_md[1205])
    check("LOG.md:1208 runs the official recipe --out runs/0957ce61", "runs/0957ce61" in log_md[1207])
    check("SCORECARD.md:891 names WORK as work/frozen-population commit", WORK in sc_md[890])
    check("SCORECARD.md:892 names CORR as measured tree", CORR in sc_md[891])

    # 5. Ancestry and content of the two lane commits
    check("WORK is an ancestor of CORR",
          git(LANE, "merge-base", "--is-ancestor", WORK, CORR).returncode == 0)
    check("recipe.json is added at CORR and absent at WORK",
          bool(git(LANE, "ls-tree", "--name-only", CORR, "--", ".ufo/waves/round-20/recipe.json").stdout.strip())
          and not git(LANE, "ls-tree", "--name-only", WORK, "--", ".ufo/waves/round-20/recipe.json").stdout.strip())
    check("CensusHarness and tools/ are identical between WORK and CORR",
          git(LANE, "diff", "--quiet", WORK, CORR, "--",
              ".ufo/waves/round-20/build/out/CensusHarness", "tools").returncode == 0)
    measured = json.loads(git(LANE, "show",
                              f"{LANE_HEAD}:.ufo/waves/round-20/runs/0957ce61/commands.json").stdout)["measured_commit"]
    check("runs/0957ce61/commands.json records measured_commit == CORR", measured == CORR, measured)

    # 6. Earliest occurrence of TOKEN in each history (all refs, every object that holds it)
    earliest = {}
    for label, repo, hits in (("lane", LANE, lane_hits), ("fleet", FLEET, fleet_hits)):
        rows = []
        for oid, kind in hits:
            out = [r for r in git(repo, "log", "--all", f"--find-object={oid}",
                                  "--format=%ct %H %s").stdout.splitlines() if r.strip()]
            print(f"  {label} {kind} {oid} is in {len(out)} commit(s):")
            for r in out:
                print("     " + r)
                ct, sha = r.split(" ", 2)[0], r.split(" ", 2)[1]
                rows.append((int(ct), sha))
        first_ct = min(rows)[0]
        earliest[label] = {sha for ct, sha in rows if ct == first_ct}
        info(f"{label} earliest commit(s) containing TOKEN", f"{sorted(earliest[label])} ct={first_ct}")
    check("fleet earliest commit containing TOKEN is 04eb5d2d", earliest["fleet"] == {FLEET_ORIGIN})
    check("lane earliest commits containing TOKEN are 00aa1486 and a29bb84", earliest["lane"] == LANE_ORIGIN)

    print("RESULT " + ("PASS" if not failures else "FAIL: " + "; ".join(failures)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
