#!/usr/bin/env python3
"""L4Slice round-52: confirm commit attribution of restored blocks in
corpus/lessons/round-{16,18,19,25,26,27,28}.md at the build commit.

For every restored line L in every block (all 67, not just 25):
  1. the block's named commit C actually deleted L from this file
     (multiset: count(parent,C^) > count(C)), C's subject matches the header;
  2. the block content multiset == the commit's deleted-line multiset D
     (full verbatim restoration of that commit's losses);
  3. L was still lost at base 9ff76b1 (count(base) < count(parent))
     so the restoration was warranted, not duplicating;
  4. sha256(key(L)) matches a round-51 disclosure row for the file at base
     and that row's commit equals C (two independent attribution sources);
  5. one block per deleting commit, blocks in history order.
Read-only on the clone. Prints a machine-readable table + summary.
"""
import hashlib
import subprocess
import sys
from collections import Counter, OrderedDict

LANE = "/fast/scratch/hyaku/kama-r52/L4Slice/lane"
TIP = "5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8"
BASE = "9ff76b1f763512be2f554cbbfd0b2213b63b0847"
FILES = [f"corpus/lessons/round-{n}.md" for n in (16, 18, 19, 25, 26, 27, 28)]

def key(line: bytes) -> bytes:
    return line[:-1] if line.endswith(b"\r") else line

def lines_of(rev: str, path: str):
    """Line multiset of a blob; empty if the file does not exist at rev."""
    r = subprocess.run(["git", "-C", LANE, "cat-file", "blob", f"{rev}:{path}"],
                       capture_output=True)
    if r.returncode != 0:
        return Counter()
    data = r.stdout
    ls = data.split(b"\n")
    if ls and ls[-1] == b"":
        ls.pop()
    return Counter(key(l) for l in ls)

def git(*args):
    return subprocess.run(["git", "-C", LANE, *args], capture_output=True)

def full_hash(short: str) -> str:
    r = git("rev-parse", f"{short}^{{commit}}")
    return r.stdout.decode().strip() if r.returncode == 0 else None

def subject(full: str) -> str:
    return git("log", "-1", "--format=%s", full).stdout.decode().rstrip("\n")

def cdate(full: str) -> str:
    return git("log", "-1", "--format=%ct", full).stdout.decode().strip()

# ---- parse disclosure rows at base: file -> list of (commit, sha256, class)
disc = {f: [] for f in FILES}
r = git("show", f"{BASE}:registry/append-only-disclosures.tsv")
for raw in r.stdout.decode().splitlines()[1:]:
    c = raw.split("\t")
    if len(c) >= 5 and c[1] in disc:
        disc[c[1]].append((c[0], c[2], c[4]))

fail = 0
total_lines = 0
report = []
for f in FILES:
    blob = git("show", f"{TIP}:{f}").stdout.decode()
    ls = blob.split("\n")
    # locate restored section
    try:
        start = next(i for i, l in enumerate(ls)
                     if l.startswith("## Restored lines (round 52)"))
    except StopIteration:
        report.append(f"FAIL {f}: no restored section"); fail += 1; continue
    # parse blocks
    blocks = []  # (commit_short, subject, [lines])
    i = start; cur = None; infence = False
    for l in ls[start:]:
        if l == "`````text" and not infence and cur is None:
            pass
        if cur is None:
            if l.startswith("Deleted by `") and l.endswith("):"):
                inner = l[len("Deleted by `"):-2]
                short, _, subj = inner.partition("` (")
                cur = [short, subj, []]
        else:
            if not infence:
                if l == "`````text":
                    infence = True
                # blank line between header and open fence is not content
            elif l == "`````":
                blocks.append(tuple(cur)); cur = None; infence = False
            else:
                cur[2].append(l)
    order_ok = all(int(cdate(full_hash(b[0])) or "0") <= int(cdate(full_hash(blocks[j+1][0])) or "0")
                   for j, b in enumerate(blocks[:-1]))
    dupes = len({b[0] for b in blocks}) != len(blocks)
    fsum = 0
    print(f"### {f}: {len(blocks)} block(s), history-order={order_ok}, unique-commits={not dupes}")
    if not order_ok or dupes:
        fail += 1
    for short, subj, content in blocks:
        C = full_hash(short)
        if C is None:
            print(f"  FAIL block commit {short}: not resolvable"); fail += 1; continue
        Cs = subject(C)
        if not Cs.startswith(subj[:60]):
            print(f"  FAIL {short}: subject mismatch\n    header: {subj}\n    actual: {Cs}")
            fail += 1
        P = C + "^"
        par, com = lines_of(P, f), lines_of(C, f)
        bas = lines_of(BASE, f)
        D = par - com  # exact deleted multiset
        B = Counter(key(l.encode()) for l in content)
        fsum += len(content)
        total_lines += len(content)
        if B != D:
            miss = D - B; extra = B - D
            print(f"  FAIL block {short[:12]}: block multiset != deleted multiset "
                  f"(block={sum(B.values())} deleted={sum(D.values())}); "
                  f"missing={dict(miss)} extra={dict(extra)}")
            fail += 1
        else:
            print(f"  OK block {short[:12]}: {sum(B.values())} restored lines == "
                  f"{sum(D.values())} lines deleted by that commit (subject match: {Cs[:70]})")
        # per-line checks
        seen = Counter()
        for l in content:
            k = key(l.encode()); seen[k] += 1
            sha = hashlib.sha256(k).hexdigest()
            present_parent = par[k] - com[k] >= seen[k]
            still_lost_base = bas[k] < par[k]
            rows = [row for row in disc[f] if row[1] == sha]
            disc_commit = rows[0][0] if rows else None
            disc_commit_ok = disc_commit is not None and full_hash(disc_commit[:12]) == C
            ok = present_parent and still_lost_base and disc_commit_ok
            if not ok:
                fail += 1
                print(f"    LINE FAIL: {l!r}\n"
                      f"      deleted-by-named-commit={present_parent} "
                      f"(par={par[k]} com={com[k]} seen={seen[k]}) "
                      f"still-lost-at-base={still_lost_base} (base={bas[k]}) "
                      f"disclosure-row={'yes' if rows else 'NO'} "
                      f"disclosure-commit-agrees={disc_commit_ok}"
                      f"{' (' + disc_commit[:12] + ')' if disc_commit and not disc_commit_ok else ''}")
        # disclosure rows of this file whose line is NOT in this block's commit check
    # every disclosure row for this file must be consumed by some block
    blockshas = set()
    for short, subj, content in blocks:
        for l in content:
            blockshas.add(hashlib.sha256(key(l.encode())).hexdigest())
    for row_commit, row_sha, row_class in disc[f]:
        if row_sha not in blockshas:
            print(f"  FAIL {f}: disclosure row {row_commit[:12]} sha {row_sha[:12]} "
                  f"class={row_class} has no restored line at tip")
            fail += 1
    print(f"  == {f}: restored lines={fsum}, base disclosure rows={len(disc[f])} "
          f"{'MATCH' if fsum == len(disc[f]) else 'MISMATCH'}")
    if fsum != len(disc[f]):
        fail += 1

print(f"\nTOTAL restored lines across 7 files: {total_lines} (expected 67)")
print(f"FAILURES: {fail}")
sys.exit(1 if fail else 0)
