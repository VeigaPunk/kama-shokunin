#!/usr/bin/env python3
"""R1Sample hand-check: per-line v3 grading of the two SCORECARD events.

Reuses the frozen counter's own functions (sections, del_positions, Blobs) so the
semantics are exactly the contract. Computes, for each deleted line of
dd9f5dc6/SCORECARD.md and for the section breakdown of 0718b6ab/SCORECARD.md:
parent section, parent count, window max (with argmax commit), eligibility under
v3 window-max, under Rev1Restore's tip-only guard (both at the round-47 tip and
at the build tip), and whether the deleted text is present beyond kept
occurrences at the build tip (relocation check).
"""
import collections
import importlib.util
import json
import sys

CNT = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round48-append-audit-v3-check.py"
spec = importlib.util.spec_from_file_location("c1", CNT)
c1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c1)

REPO = "/fast/scratch/hyaku/kama-r48/R1Sample/lane"
PATH = "SCORECARD.md"
TITLES = sorted(c1.HEAD_TITLES)  # ## Axes ## Capabilities ## Planned ## Retired ## Saturation
TIP = "380bcdff9c8af06997c482f6eb03db926a794a2b"
BASE = "33e005827742b29772b153cda036ec9f27f653be"
R47TIP = "3a09a1d93dcc16799cf6c4b48786e6440af134c4"

B = c1.Blobs(REPO)


def full(x):
    return c1.git(REPO, "rev-parse", "--verify", x + "^{commit}").stdout.decode().strip()


TIP, BASE, R47TIP = full(TIP), full(BASE), full(R47TIP)
order, parent = [], {}
for line in c1.git(REPO, "rev-list", "--topo-order", "--reverse", "--parents", TIP).stdout.decode().split("\n"):
    ps = line.split()
    if ps:
        order.append(ps[0])
        parent[ps[0]] = ps[1] if len(ps) > 1 else None
idx = {c: i for i, c in enumerate(order)}


def counts(x):
    sec = c1.sections(B.get(x, PATH))
    return {t: sum(1 for s in sec if s == t) for t in TITLES}


def window_max(t, window):
    best, arg = -1, None
    for x in window:
        v = counts(x)[t]
        if v > best:
            best, arg = v, x
    return best, arg


def event(c, out_prefix, per_line=True):
    c = full(c)
    i = idx[c]
    p = parent[c]
    window = order[i:]
    pl = B.get(p, PATH)
    psec = c1.sections(pl)
    pos = c1.del_positions(REPO, p, c, PATH)
    pc, tipc, r47c = counts(p), counts(TIP), counts(R47TIP)
    wm = {t: window_max(t, window) for t in TITLES}
    elig_win = {t for t in TITLES if wm[t][0] >= pc[t]}
    elig_380 = {t for t in TITLES if tipc[t] >= pc[t]}
    elig_r47 = {t for t in TITLES if r47c[t] >= pc[t]}
    print(f"== event {c[:12]} parent {p[:12]} window={len(window)} commits ({window[0][:12]}..{window[-1][:12]})")
    print(f"   deleted={len(pos)}")
    hdr = f"   {'title':<18}{'parent':>7}{'@event':>7}{'@82b5e9':>8}{'@r47tip':>8}{'@base':>7}{'@tip380':>8}{'winmax':>7}  argmax            elig_win elig_380 elig_r47"
    print(hdr)
    ev = counts(c)
    REPAIR = full("82b5e9d3")
    repc = counts(REPAIR)
    basec = counts(BASE)
    for t in TITLES:
        bm, ba = wm[t]
        print(f"   {t:<18}{pc[t]:>7}{ev[t]:>7}{repc.get(t,'-'):>8}{r47c[t]:>8}{basec[t]:>7}{tipc[t]:>8}{bm:>7}  {ba[:12]:<16}"
              f" {'ELIG' if t in elig_win else 'elig-no':<8} {'ELIG' if t in elig_380 else 'elig-no':<8} {'ELIG' if t in elig_r47 else 'elig-no'}")
    bysec = collections.Counter(psec[k - 1] for k in pos)
    u_win = collections.Counter(psec[k - 1] for k in pos if psec[k - 1] in elig_win)
    u_380 = collections.Counter(psec[k - 1] for k in pos if psec[k - 1] in elig_380)
    u_r47 = collections.Counter(psec[k - 1] for k in pos if psec[k - 1] in elig_r47)
    g_win = len(pos) - sum(u_win.values())
    g_380 = len(pos) - sum(u_380.values())
    g_r47 = len(pos) - sum(u_r47.values())
    print(f"   graded/ungraded  window-max(v3)={g_win}/{sum(u_win.values())}  tip-only@380={g_380}/{sum(u_380.values())}  tip-only@r47tip={g_r47}/{sum(u_r47.values())}")
    for t in [None] + TITLES:
        if bysec.get(t):
            print(f"   section {str(t):<18} deleted={bysec[t]:>5} ungraded_win={u_win.get(t, 0):>5} ungraded_380={u_380.get(t, 0):>5} ungraded_r47={u_r47.get(t, 0):>5}")
    # content presence beyond kept at tips (relocation / real-loss check)
    D = collections.Counter(pl[k - 1] for k in pos)
    K = collections.Counter(pl) - D

    def beyond(x):
        M = collections.Counter(B.get(x, PATH))
        return sum(max(0, M[l] - K[l]) for l in D), {l.decode('utf-8', 'replace'): M[l] - K[l] for l in D if M[l] > K[l]}

    held380, det380 = beyond(TIP)
    heldr47, detr47 = beyond(R47TIP)
    print(f"   deleted line-text occurrences present beyond kept @tip380: {held380}/{len(pos)}   @r47tip: {heldr47}/{len(pos)}")
    if per_line:
        with open(out_prefix + ".tsv", "w") as f:
            f.write("parent_pos\tsection\tv3_ungraded(winmax)\tungraded(tip-only@380)\tungraded(tip-only@r47tip)\tat_tip380_beyond_kept\ttext\n")
            for k in pos:
                s = psec[k - 1]
                txt = pl[k - 1].decode("utf-8", "replace")
                f.write(f"{k}\t{s}\t{'Y' if s in elig_win else 'n'}\t{'Y' if s in elig_380 else 'n'}\t{'Y' if s in elig_r47 else 'n'}\t{'Y' if det380.get(txt, 0) > 0 else 'n'}\t{txt[:100]}\n")
        print(f"   per-line TSV -> {out_prefix}.tsv")
    else:
        with open(out_prefix + "-ungraded.txt", "w") as f:
            for k in pos:
                s = psec[k - 1]
                if s in elig_win:
                    f.write(f"{k}\t{s}\t{pl[k-1].decode('utf-8','replace')[:100]}\n")
        print(f"   ungraded lines (window-max) -> {out_prefix}-ungraded.txt  ({sum(u_win.values())} lines)")
    return dict(c=c, p=p, deleted=len(pos), g_win=g_win, u_win=sum(u_win.values()),
                g_380=g_380, u_380=sum(u_380.values()), g_r47=g_r47, u_r47=sum(u_r47.values()),
                pc=pc, tipc=tipc, r47c=r47c, wm={t: wm[t] for t in TITLES},
                elig_win=sorted(elig_win), elig_380=sorted(elig_380), elig_r47=sorted(elig_r47))


dd9 = event("dd9f5dc6", "/fast/scratch/hyaku/kama-r48/R1Sample/dd9", per_line=True)
print()
e0718 = event("0718b6ab", "/fast/scratch/hyaku/kama-r48/R1Sample/0718", per_line=False)

# --- which 9 lines are the delta between window-max and tip-only@r47tip at dd9
i = idx[dd9["c"]]
p = dd9["p"]
pl = B.get(p, PATH)
psec = c1.sections(pl)
pos = c1.del_positions(REPO, p, dd9["c"], PATH)
delta = [(k, psec[k - 1]) for k in pos
         if (psec[k - 1] in dd9["elig_win"]) and not (psec[k - 1] in dd9["elig_r47"])]
print(f"\n== dd9 delta lines: ungraded under window-max but GRADED under Rev1 tip-only@r47tip: {len(delta)}")
for k, s in delta:
    print(f"   parent:{k}  [{s}]  {pl[k-1].decode('utf-8', 'replace')[:100]}")

json.dump(dict(dd9=dd9, e0718=e0718,
               delta=[(k, s) for k, s in delta]),
          open("/fast/scratch/hyaku/kama-r48/R1Sample/summary.json", "w"), indent=1, default=str)
print("\nwrote summary.json")
