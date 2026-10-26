#!/usr/bin/env python3
"""M1Ctr - C1 counter (round46-release-recheck-audit.py) mutation test.

Stages:
  build     - construct fixture artifacts (full 91-row valid ledger, tip SOURCES,
              knowledge flags) from real llama.git bytes; one fixture repo.
  variants  - one branch/commit per pristine-rejected violation fixture.
  pristine  - run pristine counter on A + all variants; record baselines.
  mutants   - apply mutants to a scratch copy of the counter, run fixture sets,
              compare against baselines, verdict killed/survived/equivalent.
  report    - dump results.json + mutant diffs into the out dir.
"""
from __future__ import annotations
import difflib, hashlib, importlib.util, json, os, re, subprocess, sys

S = "/fast/scratch/hyaku/kama-r46/M1Ctr"
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
UP = "/fast/scratch/hyaku/kama-r46/L1/llama.git"
REPO = f"{S}/repos/A"
STATE = f"{S}/state.json"
PRISTINE = f"{S}/counter/pristine.py"
MUTDIR = f"{S}/counter/mutants"
RES = f"{S}/results.json"

spec = importlib.util.spec_from_file_location("cnt", PRISTINE)
cnt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cnt)

_gitcache = {}
def git(*args, repo=None):
    key = (repo, args)
    if key in _gitcache:
        return _gitcache[key]
    p = subprocess.run(["git", "-C", repo or LANE, *args], capture_output=True, text=True)
    _gitcache[key] = p
    return p

def show(repo, rev, path):
    return cnt.show(repo, rev, path)

def nonws(s):
    return len(re.sub(r"\s", "", s))

def sh(*args, cwd=None, env=None):
    p = subprocess.run(args, capture_output=True, text=True, cwd=cwd, env=env)
    if p.returncode != 0:
        raise RuntimeError(f"{' '.join(args[:2])}... rc={p.returncode}: {p.stderr[-500:]}")
    return p.stdout

# ---------- geometry helpers ----------

def eq_blocks(ptext, rtext):
    pf = [(i, x.strip()) for i, x in enumerate(ptext) if x.strip()]
    rf = [(j, x.strip()) for j, x in enumerate(rtext) if x.strip()]
    sm = difflib.SequenceMatcher(None, [x[1] for x in pf], [x[1] for x in rf], autojunk=False)
    out = []
    for i, j, n in sm.get_matching_blocks():
        if n == 0:
            continue
        out.append((pf[i][0] + 1, pf[i + n - 1][0] + 1, rf[j][0] + 1, rf[j + n - 1][0] + 1))
    return out

def chunk_block(b, ptext, rtext, maxlen=79):
    """Split an equal block into (pin_range, rel_range) chunks each <= maxlen wide on both sides."""
    pa, pb, ra, rb = b
    pf = [i for i, x in enumerate(ptext) if x.strip() and pa <= i + 1 <= pb]
    rf = [j for j, x in enumerate(rtext) if x.strip() and ra <= j + 1 <= rb]
    assert len(pf) == len(rf), (len(pf), len(rf))
    chunks, i = [], 0
    while i < len(pf):
        j = i
        while (j + 1 < len(pf) and pf[j + 1] - pf[i] + 1 <= maxlen
               and rf[j + 1] - rf[i] + 1 <= maxlen):
            j += 1
        chunks.append(((pf[i] + 1, pf[j] + 1), (rf[i] + 1, rf[j] + 1)))
        i = j + 1
    return chunks

def strong_weak(ent):
    s, w = cnt.cited(ent["cells"])
    return s, w

def cover_ranges(needles, filelen, ptext, pad=True):
    """Ranges (<=79 wide, >=20 non-ws, inside file) covering every needle <= filelen."""
    need = sorted(n for n in needles if 1 <= n <= filelen)
    if not need:
        return []
    runs = []
    a = b = need[0]
    for n in need[1:]:
        if n == b + 1:
            b = n
        else:
            runs.append((a, b)); a = b = n
    runs.append((a, b))
    out = []
    for a, b in runs:
        # split long runs
        while a <= b:
            e = min(b, a + 78)
            out.append((a, e))
            a = e + 1
    # widen to satisfy 20 non-ws
    fixed = []
    for a, b in out:
        while b < filelen and nonws("".join(ptext[a - 1:b])) < 20 and b - a + 1 < 79:
            b += 1
        if nonws("".join(ptext[a - 1:b])) >= 20:
            fixed.append((a, b))
        elif pad:
            # try shifting start
            a2 = a
            while a2 > 1 and nonws("".join(ptext[a2 - 1:b])) < 20 and b - a2 + 1 < 79:
                a2 -= 1
            if nonws("".join(ptext[a2 - 1:b])) >= 20:
                fixed.append((a2, b))
    return fixed

def spec_of(ranges):
    parts = []
    for r in ranges:
        if not isinstance(r, tuple):
            parts.append("-")
        else:
            a, b = r
            parts.append(f"{a}-{b}" if b > a else f"{a}")
    return ",".join(parts)

def parse(specstr):
    return cnt.ranges(specstr, False)

def find_witness(lines, other_ws, minlen=12, prefer_runs=True):
    cands = []
    for x in lines:
        w = cnt.ws(x)
        if len(w) >= minlen and w not in other_ws:
            cands.append(w)
    if prefer_runs:
        runny = [c for c in cands if re.search(r"\S {2,}\S", c)]
        if runny:
            return runny[0]
    if cands:
        return cands[0]
    joined = cnt.ws(" ".join(lines))
    for i in range(0, max(0, len(joined) - minlen), 5):
        c = joined[i:i + minlen + 8]
        if len(c) >= minlen and c not in other_ws:
            return c
    return None

# ---------- row builders (each returns a ledger dict or None) ----------

def base_row(sid, ent):
    return {"id": sid, "path": ent["path"], "pin_commit": ent["pin"], "release": cnt.RELEASE}

def row_unchanged(sid, ent, ptext):
    pb = cnt.blob(UP, ent["pin"], ent["path"])
    strong, weak = strong_weak(ent)
    rs = cover_ranges(strong, len(ptext), ptext)
    if not rs:
        # default dense range near top
        for a in range(1, max(2, len(ptext) - 4)):
            b = min(len(ptext), a + 4)
            if nonws("".join(ptext[a - 1:b])) >= 20:
                rs = [(a, b)]
                break
    if not rs:
        return None
    r = base_row(sid, ent)
    r.update(pin_blob=pb, release_blob=pb, changed="0",
             pin_lines=spec_of(rs), release_lines=spec_of(rs),
             witness_pin="-", witness_new="-", verdict="unchanged-file", note="-")
    return r

def row_holds(sid, ent, ptext, rtext, min_pairs=1):
    pb, rb = cnt.blob(UP, ent["pin"], ent["path"]), cnt.blob(UP, cnt.RELEASE_COMMIT, ent["path"])
    strong, weak = strong_weak(ent)
    blocks = eq_blocks(ptext, rtext)
    pairs, covered = [], set()
    for b in blocks:
        for (pr, rr) in chunk_block(b, ptext, rtext):
            if nonws("".join(ptext[pr[0] - 1:pr[1]])) < 20:
                continue
            pairs.append((pr, rr))
            covered.update(range(pr[0], pr[1] + 1))
    need = {n for n in strong if n <= len(ptext)}
    if not need <= covered:
        return None
    if weak and not (need or any(n in covered for n in weak if n <= len(ptext))):
        # keep a pair that covers a weak number
        wset = {n for n in weak if n <= len(ptext)}
        if not any(any(a <= n <= b for (a, b) in [p]) for p, _ in pairs for n in wset):
            return None
    if len(pairs) < min_pairs:
        return None
    if not pairs:
        return None
    # verify equality exactly as the counter does
    for (pa, pb2), (ra, rb2) in pairs:
        if cnt.excerpt(ptext, (pa, pb2)) != cnt.excerpt(rtext, (ra, rb2)):
            return None
    r = base_row(sid, ent)
    r.update(pin_blob=pb, release_blob=rb, changed="1",
             pin_lines=spec_of([p for p, _ in pairs]), release_lines=spec_of([q for _, q in pairs]),
             witness_pin="-", witness_new="-", verdict="holds", note="-")
    r["_pairs"] = pairs
    return r

def citation_pin_ranges(ent, ptext):
    strong, weak = strong_weak(ent)
    rs = cover_ranges(strong, len(ptext), ptext)
    if not rs:
        wset = {n for n in weak if 1 <= n <= len(ptext)}
        rs = cover_ranges(wset, len(ptext), ptext) if wset else []
    if not rs:
        for a in range(1, max(2, len(ptext) - 4)):
            b = min(len(ptext), a + 4)
            if nonws("".join(ptext[a - 1:b])) >= 20:
                rs = [(a, b)]
                break
    return rs

def changed_region(ptext, rtext):
    """A (pin_range, rel_range) pair whose texts differ."""
    pf = [(i, x.strip()) for i, x in enumerate(ptext) if x.strip()]
    rf = [(j, x.strip()) for j, x in enumerate(rtext) if x.strip()]
    sm = difflib.SequenceMatcher(None, [x[1] for x in pf], [x[1] for x in rf], autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag not in ("replace", "delete"):
            continue
        pa = pf[i1][0] + 1; pbe = pf[min(i2 - 1, len(pf) - 1)][0] + 1
        while pbe - pa + 1 > 79:
            pbe -= 1
        if nonws("".join(ptext[pa - 1:pbe])) < 20:
            continue
        if tag == "delete" or j2 == j1:
            return (pa, pbe), None
        ra = rf[j1][0] + 1
        rbe = rf[j2 - 1][0] + 1
        while rbe - ra + 1 > 79:
            rbe -= 1
        if cnt.excerpt(ptext, (pa, pbe)) != cnt.excerpt(rtext, (ra, rbe)):
            return (pa, pbe), (ra, rbe)
    return None, None

def any_diff_pair(ptext, rtext, seeds):
    """(pin_range, rel_range) with differing texts, pin >= 20 non-ws, both inside files."""
    n, m = len(ptext), len(rtext)
    tried = set()
    cands = []
    for p in seeds:
        a, b = p
        for d in (0, 1, -1, 2, -2):
            a2, b2 = max(1, a + d), min(m, b + d)
            if a2 <= b2:
                cands.append(((a, b), (a2, b2)))
    for start in range(1, max(2, n - 5), 3):
        a, b = start, min(n, start + 4)
        a2, b2 = max(1, a), min(m, b)
        if a2 <= b2:
            cands.append(((a, b), (a2, b2)))
    for p, r in cands:
        if (p, r) in tried:
            continue
        tried.add((p, r))
        if p[1] > n or r[1] > m or nonws("".join(ptext[p[0] - 1:p[1]])) < 20:
            continue
        if cnt.excerpt(ptext, p) != cnt.excerpt(rtext, r):
            return p, r
    return None, None

def row_reworded(sid, ent, ptext, rtext):
    """holds-reworded: eq pairs covering citations + one changed pair; real witnesses."""
    pb, rb = cnt.blob(UP, ent["pin"], ent["path"]), cnt.blob(UP, cnt.RELEASE_COMMIT, ent["path"])
    PF, RF = cnt.ws(" ".join(ptext)), cnt.ws(" ".join(rtext))
    pin_ranges = citation_pin_ranges(ent, ptext)
    cp, cr = changed_region(ptext, rtext)
    if cp is None or cr is None:
        cp, cr = any_diff_pair(ptext, rtext, pin_ranges)
    if cp is None or cr is None:
        return None
    prs = pin_ranges + [cp] if cp not in pin_ranges else pin_ranges
    rrs = []
    for p in prs:
        if p == cp:
            rrs.append(cr)
        else:
            a, b = p
            b2 = min(b, len(rtext))
            rrs.append((a, b2) if a <= len(rtext) else (1, min(2, len(rtext))))
    wp_lines = [l.strip() for p in prs for l in ptext[p[0] - 1:p[1]]]
    wn_lines = [l.strip() for q in rrs if q for l in rtext[q[0] - 1:q[1]]]
    wp = find_witness(wp_lines, RF)
    wn = find_witness(wn_lines, PF)
    if not wp or not wn:
        return None
    if cnt.ws(wp) in RF or cnt.ws(wn) in PF:
        return None
    r = base_row(sid, ent)
    r.update(pin_blob=pb, release_blob=rb, changed="1",
             pin_lines=spec_of(prs), release_lines=spec_of(rrs),
             witness_pin=wp, witness_new=wn, verdict="holds-reworded",
             note=f"M1Ctr fixture: anchored text reworded between pin and {cnt.RELEASE} (real bytes)")
    return r

def row_drifted(sid, ent, ptext, rtext):
    pb, rb = cnt.blob(UP, ent["pin"], ent["path"]), cnt.blob(UP, cnt.RELEASE_COMMIT, ent["path"])
    PF, RF = cnt.ws(" ".join(ptext)), cnt.ws(" ".join(rtext))
    pin_ranges = citation_pin_ranges(ent, ptext)
    cp, cr = changed_region(ptext, rtext)
    if cp is None or cr is None:
        cp, cr = any_diff_pair(ptext, rtext, pin_ranges)
    if cp is None or cr is None:
        return None
    # pair layout: [changed pair (non-dash), filler pin range -> dash]
    filler = None
    for p in pin_ranges:
        if p != cp:
            filler = p
            break
    if filler is None:
        a = max(1, min(cp[0] - 10, len(ptext) - 2))
        filler = (a, min(len(ptext), a + 3))
        if nonws("".join(ptext[filler[0] - 1:filler[1]])) < 20:
            return None
    prs = [cp, filler]
    rrs = [cr, None]
    wp = find_witness([l.strip() for l in ptext[cp[0] - 1:cp[1]]], RF)
    wn = find_witness([l.strip() for l in rtext[cr[0] - 1:cr[1]]], PF)
    if not wp or not wn or cnt.ws(wp) in RF or cnt.ws(wn) in PF:
        return None
    r = base_row(sid, ent)
    r.update(pin_blob=pb, release_blob=rb, changed="1",
             pin_lines=spec_of(prs), release_lines=spec_of([cr, "-"]),
             witness_pin=wp, witness_new=wn, verdict="drifted",
             note="M1Ctr fixture: pinned anchor moved/removed upstream, part of range has no counterpart")
    return r

def row_removed(sid, ent, ptext, rtext, want_short=False, avoid=(), exclude_sids=()):
    if sid in exclude_sids:
        return None
    pb, rb = cnt.blob(UP, ent["pin"], ent["path"]), cnt.blob(UP, cnt.RELEASE_COMMIT, ent["path"])
    rset = {x.strip() for x in rtext} if rtext else set()
    RF = cnt.ws(" ".join(rtext)) if rtext else ""
    strong, weak = strong_weak(ent)
    strongf = {n for n in strong if n <= len(ptext)}
    wset = {n for n in weak if 1 <= n <= len(ptext)}
    n = len(ptext)

    def emit(prs):
        wp_lines = [l.strip() for p in prs for l in ptext[p[0] - 1:p[1]]]
        wp = find_witness(wp_lines, RF)
        if not wp or cnt.ws(wp) in RF:
            return None
        r = base_row(sid, ent)
        r.update(pin_blob=pb, release_blob=rb, changed="1",
                 pin_lines=spec_of(prs), release_lines="-",
                 witness_pin=wp, witness_new="-", verdict="removed",
                 note="M1Ctr fixture: pinned lines no longer occur verbatim anywhere in the release file")
        return r

    if strongf:
        # strong-covering removal: each range starts on a line absent from the release
        # file (that is the range's first >= 8-char line); strongs inside are fine.
        runs, cur = [], None
        for a in sorted(strongf):
            if cur and a == cur[1] + 1:
                cur[1] = a
            else:
                if cur:
                    runs.append(tuple(cur))
                cur = [a, a]
        if cur:
            runs.append(tuple(cur))
        prs = []
        for a, b in runs:
            while b - a + 1 > 79:
                prs.append((a, a + 78)); a += 79
            prs.append((a, b))
        fixed = []
        for a, b in prs:
            ok = None
            for a2 in range(a, max(1, a - 12) - 1, -1):
                if b - a2 + 1 > 79:
                    break
                seg = ptext[a2 - 1:b]
                first8 = next((x.strip() for x in seg if len(x.strip()) >= 8), None)
                if first8 is not None and first8 not in rset and nonws("".join(seg)) >= 20:
                    ok = (a2, b)
                    break
            if ok is None:
                return None
            fixed.append(ok)
        prs = fixed
        if wset and not any(any(p[0] <= w <= p[1] for p in prs) for w in wset):
            # extend the last range to reach a weak number
            a, b = prs[-1]
            for w in sorted(wset):
                if w > b and w - a + 1 <= 79:
                    seg = ptext[a - 1:w]
                    first8 = next((x.strip() for x in seg if len(x.strip()) >= 8), None)
                    if first8 is not None and first8 not in rset and nonws("".join(seg)) >= 20:
                        prs[-1] = (a, w)
                        break
            else:
                return None
        r = emit(prs)
        return (r, prs[0]) if r else None

    for start in range(1, n - 1):
        end = min(n, start + 3)
        if (start, end) in avoid:
            continue
        window = ptext[start - 1:end]
        stripped = [x.strip() for x in window]
        first8 = next((x for x in stripped if len(x) >= 8), None)
        if first8 is None or first8 in rset:
            continue
        if nonws("".join(window)) < 20:
            continue
        if wset and not any(start <= w <= end for w in wset):
            continue
        if want_short:
            s3 = next((x for x in stripped if len(x) >= 3), None)
            if not (s3 and 3 <= len(s3) <= 7 and s3 in rset):
                continue
            if s3 == first8:
                continue
        r = emit([(start, end)])
        if r:
            return r, (start, end)
    return None

# ---------- fixture build ----------

def build():
    base_src = show(LANE, cnt.BASE, cnt.SOURCES)
    pop = cnt.population(base_src)
    assert len(pop) == 91, len(pop)
    b11889 = {}
    with open(f"{LANE}/registry/release-recheck-b11889.tsv") as fh:
        for i, line in enumerate(fh):
            f = line.rstrip("\n").split("\t")
            if i and len(f) >= 10:
                b11889[f[0]] = f
    entries = []
    for sid, e in sorted(pop.items()):
        pb = cnt.blob(UP, e["pin"], e["path"])
        rb = cnt.blob(UP, cnt.RELEASE_COMMIT, e["path"])
        ptext = show(UP, e["pin"], e["path"]).splitlines()
        rtext = show(UP, cnt.RELEASE_COMMIT, e["path"]).splitlines() if rb != "-" else []
        entries.append({"sid": sid, "ent": e, "pb": pb, "rb": rb, "ptext": ptext, "rtext": rtext})
    rows, log = {}, []
    pools = {"unch": [], "chg": []}
    for x in entries:
        pools["unch" if x["pb"] == x["rb"] else "chg"].append(x)

    used = set()
    # 1) unchanged rows
    for x in pools["unch"]:
        r = row_unchanged(x["sid"], x["ent"], x["ptext"])
        assert r, x["sid"]
        rows[x["sid"]] = r; used.add(x["sid"])
    log.append(f"unchanged-file rows: {sorted(rows)}")

    # 7) authoritative validation helper (frozen counter's own check_row)
    def valid_row(sid, ent, r):
        lr = {c: r[c] for c in cnt.HEADER}
        ok, why = cnt.check_row(ent, lr, UP)
        return ok, why

    # 2) removed rows (short-window + plain), prefer ns==0 changed rows
    def ns0(x):
        s, w = strong_weak(x["ent"])
        return not any(1 <= n <= len(x["ptext"]) for n in s)
    cands = [x for x in pools["chg"] if ns0(x)] + [x for x in pools["chg"] if not ns0(x)]
    short = plain = None
    for x in cands:
        if short is None:
            got = row_removed(x["sid"], x["ent"], x["ptext"], x["rtext"], want_short=True)
            if got and valid_row(x["sid"], x["ent"], got[0])[0]:
                short, short_win, short_src = got[0], got[1], x
        if plain is None and short is not None and x["sid"] != short["id"]:
            got = row_removed(x["sid"], x["ent"], x["ptext"], x["rtext"])
            if got and valid_row(x["sid"], x["ent"], got[0])[0]:
                plain, plain_src = got[0], x
        if short and plain:
            break
    assert plain and short, "removed constructions failed"
    rows[plain["id"]] = plain; used.add(plain["id"])
    rows[short["id"]] = short; used.add(short["id"])
    log.append(f"removed rows: {plain['id']} (plain, win {plain['pin_lines']}), "
               f"{short['id']} (short-window, win {short['pin_lines']}); file {plain_src['ent']['path']}")

    # 3) drifted row: any changed row not used
    drifted = None
    for x in pools["chg"]:
        if x["sid"] in used:
            continue
        cand = row_drifted(x["sid"], x["ent"], x["ptext"], x["rtext"])
        if cand and valid_row(x["sid"], x["ent"], cand)[0]:
            drifted, drifted_src = cand, x
            break
    assert drifted, "drifted construction failed"
    rows[drifted["id"]] = drifted; used.add(drifted["id"])
    log.append(f"drifted row: {drifted['id']} ({drifted_src['ent']['path']})")

    # 4) holds-reworded on a real changed row (S042/S060 have real reworded regions)
    hr = None
    for sid in ("S042", "S060", "S108", "S037", "S043"):
        x = next(e for e in entries if e["sid"] == sid)
        cand = row_reworded(sid, x["ent"], x["ptext"], x["rtext"])
        if cand and valid_row(sid, x["ent"], cand)[0]:
            hr, hr_src = cand, x
            break
    assert hr, "holds-reworded construction failed"
    rows[hr["id"]] = hr; used.add(hr["id"])
    log.append(f"holds-reworded row: {hr['id']} ({hr_src['ent']['path']})")

    # 5) carry-forward holds from the b11889 holds set, fallback any changed row
    cf = None
    for sid in ("S035", "S036", "S047", "S054", "S056", "S060", "S042"):
        if sid in used:
            continue
        x = next(e for e in entries if e["sid"] == sid)
        cand = row_holds(sid, x["ent"], x["ptext"], x["rtext"])
        if cand and valid_row(sid, x["ent"], cand)[0]:
            cf, cf_src = cand, x
            break
    if cf is None:
        for x in pools["chg"]:
            if x["sid"] in used:
                continue
            cand = row_holds(x["sid"], x["ent"], x["ptext"], x["rtext"])
            if cand and valid_row(x["sid"], x["ent"], cand)[0]:
                cf, cf_src = cand, x
                break
    assert cf, "carry-forward holds failed"
    rows[cf["id"]] = cf; used.add(cf["id"])
    log.append(f"carry-forward holds row: {cf['id']} ({cf_src['ent']['path']})")

    # 6) a second holds row with >=2 pairs (M23/M32 target)
    ht = None
    for x in pools["chg"]:
        if x["sid"] in used:
            continue
        cand = row_holds(x["sid"], x["ent"], x["ptext"], x["rtext"], min_pairs=2)
        if cand and valid_row(x["sid"], x["ent"], cand)[0]:
            ht, ht_src = cand, x
            break
    assert ht, "2-pair holds failed"
    rows[ht["id"]] = ht; used.add(ht["id"])
    log.append(f"2-pair holds row: {ht['id']} ({ht_src['ent']['path']})")

    # 6b) remaining changed rows: holds else holds-reworded else drifted, validated
    fails = {}
    for x in pools["chg"]:
        if x["sid"] in used:
            continue
        r = None
        for builder in (row_holds, row_reworded, row_drifted):
            cand = builder(x["sid"], x["ent"], x["ptext"], x["rtext"])
            if cand and valid_row(x["sid"], x["ent"], cand)[0]:
                r = cand
                break
        if r is None:
            fails[x["sid"]] = "no valid construction"
            continue
        rows[x["sid"]] = r; used.add(x["sid"])
    assert not fails, f"unconstructible rows: {fails}"

    for x in pools["unch"]:
        used.add(x["sid"])
    assert len(rows) == 91, len(rows)

    # 8) final authoritative validation of every constructed row with the frozen counter
    invalid = {}
    for sid in sorted(rows):
        lr = {c: rows[sid][c] for c in cnt.HEADER}
        ok, why = cnt.check_row(pop[sid], lr, UP)
        if not ok:
            invalid[sid] = why
    assert not invalid, f"invalid fixture rows: {invalid}"
    log.append("check_row validation: all 91 rows valid")

    # note length boundary: drifted note exactly 40 chars (M12 killer via A)
    dn = rows[drifted["id"]]["note"]
    nn = (dn + "x" * 40)[:40]
    assert len(nn) == 40
    rows[drifted["id"]]["note"] = nn

    # tip SOURCES: lane tip content + section + flags + newrow
    lane_tip = git("rev-parse", "HEAD").stdout.strip()
    tip_src = show(LANE, lane_tip, cnt.SOURCES)
    flag_ids = [drifted["id"], plain["id"], short["id"]]
    sec = ["", "## Round-46 release re-verification", ""]
    for sid in flag_ids:
        sec.append(f"- {sid}: anchored statement drifted/removed at {cnt.RELEASE}; see knowledge entry.")
    sec.append("")
    sec.append("| S901 | tools/server/server-context.cpp | "
               f"https://github.com/ggml-org/llama.cpp/blob/{cnt.RELEASE_COMMIT}/tools/server/server-context.cpp "
               f"| opened at {cnt.RELEASE} | note | mined | on-release | - | - | - | - |")
    tip_src2 = tip_src.rstrip("\n") + "\n" + "\n".join(sec) + "\n"

    # knowledge flags (accumulate: several flag ids may share one knowledge file)
    knowledge_edits = {}
    for sid in flag_ids:
        for u in [u.strip() for u in pop[sid]["cells"][10].split(",")]:
            if not re.fullmatch(r"corpus/knowledge/[\w.\-]+\.md", u):
                continue
            body = show(LANE, lane_tip, u)
            if body is None:
                continue
            knowledge_edits.setdefault(u, body.rstrip("\n"))
            knowledge_edits[u] += \
                f"\n- {sid} drifted/removed at {cnt.RELEASE} {cnt.RELEASE_COMMIT} (M1Ctr fixture)"

    # ledger text
    def ledger_text(rws):
        out = ["\t".join(cnt.HEADER)]
        for sid in sorted(rws):
            r = rws[sid]
            out.append("\t".join(r[c] for c in cnt.HEADER))
        return "\n".join(out) + "\n"

    state = {
        "lane_tip": lane_tip,
        "rows": rows,
        "tip_sources": tip_src2,
        "knowledge_edits": knowledge_edits,
        "flag_ids": flag_ids,
        "drifted_id": drifted["id"], "plain_removed_id": plain["id"], "short_removed_id": short["id"],
        "hr_id": hr["id"], "cf_id": cf["id"], "ht_id": ht["id"],
        "unch_id": sorted(x["sid"] for x in pools["unch"])[0],
        "log": log,
        "base_sha256": hashlib.sha256(open(PRISTINE, "rb").read()).hexdigest(),
    }
    json.dump(state, open(STATE, "w"))
    print(json.dumps(log, indent=1))
    print("class counts:", {v: sum(1 for r in rows.values() if r["verdict"] == v)
                            for v in ("unchanged-file", "holds", "holds-reworded", "drifted", "removed")})

if __name__ == "__main__":
    {"build": build}.get(sys.argv[1], build)()
