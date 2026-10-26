#!/usr/bin/env python3
"""M1Ctr stage 2: fixture repo, violation variants, mutants, runner."""
from __future__ import annotations
import hashlib, json, os, re, shutil, subprocess, sys

S = "/fast/scratch/hyaku/kama-r46/M1Ctr"
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
UP = "/fast/scratch/hyaku/kama-r46/L1/llama.git"
REPO = f"{S}/repos/A"
STATE = f"{S}/state.json"
PRISTINE = f"{S}/counter/pristine.py"
MUTDIR = f"{S}/counter/mutants"
RES = f"{S}/results.json"
BASELINE = f"{S}/baselines.json"

state = json.load(open(STATE))
ROWS0 = state["rows"]
TIP0 = state["tip_sources"]
KNOW0 = state["knowledge_edits"]
DR = state["drifted_id"]; RP = state["plain_removed_id"]; RS = state["short_removed_id"]
HR = state["hr_id"]; CF = state["cf_id"]; HT = state["ht_id"]; UN = state["unch_id"]

import importlib.util
spec = importlib.util.spec_from_file_location("cnt", PRISTINE)
cnt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cnt)
import m1

LANE_TIP = state["lane_tip"]
BASE_SRC = cnt.show(LANE, cnt.BASE, cnt.SOURCES)
POP = cnt.population(BASE_SRC)
TXT = {}
def texts(sid):
    if sid not in TXT:
        e = POP[sid]
        ptext = cnt.show(UP, e["pin"], e["path"]).splitlines()
        rb = cnt.blob(UP, cnt.RELEASE_COMMIT, e["path"])
        rtext = cnt.show(UP, cnt.RELEASE_COMMIT, e["path"]).splitlines() if rb != "-" else []
        TXT[sid] = (ptext, rtext)
    return TXT[sid]

def parse_spec(specstr, dash=False):
    return cnt.ranges(specstr, dash)

def P_of(sid, row):
    ptext, _ = texts(sid)
    pr = cnt.ranges(row["pin_lines"], False)
    return cnt.ws(" ".join(" ".join(ptext[p[0] - 1:p[1]]) for p in pr))

def R_of(sid, row):
    _, rtext = texts(sid)
    rr = cnt.ranges(row["release_lines"], True)
    return cnt.ws(" ".join(" ".join(rtext[r[0] - 1:r[1]]) for r in rr if r))

def PF_of(sid):
    return cnt.ws(" ".join(texts(sid)[0]))

def RF_of(sid):
    _, rtext = texts(sid)
    return cnt.ws(" ".join(rtext)) if rtext else ""

def cp_row(sid, **kw):
    r = dict(ROWS0[sid]); r.update(kw); return r

# ---------------- variant builders ----------------
def v_wp11_dr(rows, tip, know):
    r = cp_row(DR)
    wp = cnt.ws(r["witness_pin"])
    assert wp in P_of(DR, r) and wp not in RF_of(DR)
    r["witness_pin"] = wp[:11]
    rows[DR] = r

def _wn11(sid, rows):
    r = cp_row(sid)
    _, rtext = texts(sid)
    rr = cnt.ranges(r["release_lines"], True)
    R = R_of(sid, r)
    PF = PF_of(sid)
    cands = []
    for q in rr:
        if not q:
            continue
        joined = cnt.ws(" ".join(rtext[q[0] - 1:q[1]]))
        for i in range(0, max(0, len(joined) - 11)):
            c = joined[i:i + 11]
            if c in R and c not in PF:
                cands.append(c)
        if cands:
            break
    assert cands, f"no 11-char witness window for {sid}"
    r["witness_new"] = cands[0]
    rows[sid] = r

def v_wn11_hr(rows, tip, know):
    _wn11(HR, rows)

def v_wn11_dr(rows, tip, know):
    _wn11(DR, rows)

def v_wn_outside(rows, tip, know):
    r = cp_row(HR)
    _, rtext = texts(HR)
    rr = cnt.ranges(r["release_lines"], True)
    maxb = max(q[1] for q in rr if q)
    inside = {n for q in rr if q for n in range(q[0], q[1] + 1)}
    PF = PF_of(HR)
    for i, line in enumerate(rtext[:maxb], 1):
        if i in inside:
            continue
        w = cnt.ws(line)
        if len(w) >= 12 and w not in PF:
            r["witness_new"] = w
            rows[HR] = r
            return
    raise RuntimeError("no outside witness for v_wn_outside")

def v_wp_in_RF(rows, tip, know):
    r = cp_row(DR)
    ptext, _ = texts(DR)
    pr = cnt.ranges(r["pin_lines"], False)
    inside = {n for p in pr for n in range(p[0], p[1] + 1)}
    RF = RF_of(DR)
    for i, line in enumerate(ptext, 1):
        if i not in inside:
            continue
        w = cnt.ws(line)
        if len(w) >= 12 and w in RF:
            r["witness_pin"] = w
            rows[DR] = r
            return
    raise RuntimeError("no in-RF witness for v_wp_in_RF")

def v_holds_witness(rows, tip, know):
    r = cp_row(CF)
    wp_lines = []
    ptext, _ = texts(CF)
    for p in cnt.ranges(r["pin_lines"], False):
        wp_lines += [l.strip() for l in ptext[p[0] - 1:p[1]]]
    RF = RF_of(CF)
    wp = m1.find_witness(wp_lines, RF)
    assert wp and cnt.ws(wp) not in RF
    r["witness_pin"] = wp
    rows[CF] = r

def v_note39(rows, tip, know):
    r = cp_row(DR)
    assert len(r["note"]) >= 39
    r["note"] = r["note"][:39]
    rows[DR] = r

def v_newrow_partial(rows, tip, know):
    # blanket: no tip line may still carry the release commit -> newrow=0 guaranteed
    return "\n".join(x.replace(cnt.RELEASE_COMMIT, "") for x in tip.splitlines()) + "\n"

def v_section_missing(rows, tip, know):
    return "\n".join(x for x in tip.splitlines() if cnt.SECTION not in x) + "\n"

def v_cited_miss(rows, tip, know):
    e = POP["S131"]
    ptext, _ = texts("S131")
    strong, weak = cnt.cited(e["cells"])
    strongf = sorted(n for n in strong if n <= len(ptext))
    r = None
    for n0 in strongf:
        rs = m1.cover_ranges([n for n in strongf if n != n0], len(ptext), ptext)
        if not rs:
            continue
        covered = {n for a, b in rs for n in range(a, b + 1)}
        if n0 in covered:
            continue
        r = cp_row("S131", pin_lines=m1.spec_of(rs), release_lines=m1.spec_of(rs))
        break
    assert r, "v_cited_miss construction failed"
    rows["S131"] = r

def v_rel_blob(rows, tip, know):
    r = cp_row(UN)
    rb = r["release_blob"]
    r["release_blob"] = ("0" if rb[0] != "0" else "1") + rb[1:]
    rows[UN] = r

def v_changed_flag(rows, tip, know):
    rows[UN] = cp_row(UN, changed="1")

def v_holds_partial(rows, tip, know):
    r = cp_row(HT)
    ptext, rtext = texts(HT)
    pr = cnt.ranges(r["pin_lines"], False)
    rr = cnt.ranges(r["release_lines"], True)
    m = len(rtext)
    for k in range(len(rr)):
        for d in (3, -3, 5, -5, 8, -8):
            a, b = rr[k]
            a2, b2 = max(1, a + d), min(m, b + d)
            if a2 > b2 or b2 - a2 != b - a:
                continue
            if cnt.excerpt(ptext, pr[k]) == cnt.excerpt(rtext, (a2, b2)):
                continue
            rr2 = rr[:k] + [(a2, b2)] + rr[k + 1:]
            r2 = cp_row(HT, release_lines=m1.spec_of(rr2))
            rows[HT] = r2
            return
    raise RuntimeError("v_holds_partial failed")

def v_unch_on_changed(rows, tip, know):
    rows[HR] = cp_row(HR, verdict="unchanged-file", witness_pin="-", witness_new="-",
                      release_lines=ROWS0[HR]["pin_lines"], note="-")

def v_hr_all_eq(rows, tip, know):
    # in-order all-eq HR: witnesses impossible -> dies at witness_pin rule (shadowing demo)
    sid = HT  # S036, a 2-pair holds row: both pairs text-equal
    r = cp_row(sid, verdict="holds-reworded")
    pr = cnt.ranges(r["pin_lines"], False)
    rr = cnt.ranges(r["release_lines"], True)
    eqp = [(pr[k], rr[k]) for k in range(len(pr))
           if rr[k] and _ex_eq(sid, pr[k], rr[k])]
    assert len(eqp) == len(pr), "expected all-eq pairs"
    r["pin_lines"] = m1.spec_of([p for p, _ in eqp])
    r["release_lines"] = m1.spec_of([q for _, q in eqp])
    r["witness_pin"] = "-"; r["witness_new"] = "-"
    rows[sid] = r

def _ex_eq(sid, p, q):
    ptext, rtext = texts(sid)
    return cnt.excerpt(ptext, p) == cnt.excerpt(rtext, q)

def v_hr_all_eq_ooo(rows, tip, know):
    # out-of-order all-eq HR on S001 with duplicated 20+ char line L
    sid = RS  # S001
    ptext, rtext = texts(sid)
    L = '-H "Content-Type: application/json" \\'
    pi = [i + 1 for i, x in enumerate(ptext) if x.strip() == L]
    ri = [i + 1 for i, x in enumerate(rtext) if x.strip() == L]
    assert len(pi) >= 2 and len(ri) >= 2, (pi, ri)
    p1, p2 = pi[0], pi[1]
    r1, r2 = ri[0], ri[1]
    wp = cnt.ws(L + " " + L)
    RF, PF = RF_of(sid), PF_of(sid)
    assert wp not in RF and wp not in PF, "boundary witness collides"
    r = cp_row(sid)
    r.update(verdict="holds-reworded",
             pin_lines=f"{p1},{p2}", release_lines=f"{r2},{r1}",
             witness_pin=wp, witness_new=wp,
             note="M1Ctr fixture: all pairs text-equal with out-of-order ranges (boundary witnesses)")
    rows[sid] = r

def v_removed_wn(rows, tip, know):
    rows[RP] = cp_row(RP, witness_new="M1Ctr fixture: witness_new must be absent on removed")

def v_range_wide(rows, tip, know):
    ptext, _ = texts(UN)
    assert len(ptext) >= 100
    rows[UN] = cp_row(UN, pin_lines="1-100", release_lines="1-100")

def v_counts(rows, tip, know):
    r = cp_row(HT)
    rr = cnt.ranges(r["release_lines"], True)
    r["release_lines"] = m1.spec_of(rr[:-1])
    rows[HT] = r

def v_range_eof(rows, tip, know):
    ptext, _ = texts(UN)
    n = len(ptext)
    rows[UN] = cp_row(UN, pin_lines=f"{n + 1}-{n + 3}", release_lines=f"{n + 1}-{n + 3}")

def v_short_range(rows, tip, know):
    ptext, _ = texts(UN)
    for a in range(1, 30):
        if m1.nonws("".join(ptext[a - 1:a + 1])) < 20:
            rows[UN] = cp_row(UN, pin_lines=f"{a}-{a + 1}", release_lines=f"{a}-{a + 1}")
            return
    raise RuntimeError("no short window in S015")

def v_wrong_pin(rows, tip, know):
    rows[UN] = cp_row(UN, pin_commit=cnt.RELEASE_COMMIT)

def v_dup(rows, tip, know):
    rows = dict(rows)
    dup = cp_row(UN, pin_lines="5-9", release_lines="5-9")
    rows[f"{UN}#2"] = dup  # marker; writer emits it with id UN again
    return rows, tip, know, {"dup_marker": UN}

def v_flag_missing(rows, tip, know):
    # drop the appended flag line for the drifted id from its knowledge file
    know2 = dict(know)
    for u, body in know.items():
        if f"\n- {DR} drifted/removed" in body or body.startswith(f"- {DR} drifted/removed"):
            know2[u] = "\n".join(x for x in body.splitlines()
                                 if not (re.search(rf"\b{DR}\b", x) and cnt.RELEASE in x)) + "\n"
            return rows, tip, know2, None
    raise RuntimeError("no knowledge flag line to drop")

def v_sec_list_missing(rows, tip, know):
    lines = [x for x in tip.splitlines()
             if not (re.search(rf"\b{DR}\b", x) and x.lstrip().startswith("-"))]
    return "\n".join(lines) + "\n"

def v_ws_runs(rows, tip, know):
    # extend the HR row with one extra pair hosting runny (2+ space) witness lines
    sid = HR
    r = cp_row(sid)
    ptext, rtext = texts(sid)
    RF, PF = RF_of(sid), PF_of(sid)
    wps = [(i, cnt.ws(l)) for i, l in enumerate(ptext, 1)
           if re.search(r"\S {2,}\S", l) and len(cnt.ws(l)) >= 12 and cnt.ws(l) not in RF]
    wns = [(i, cnt.ws(l)) for i, l in enumerate(rtext, 1)
           if re.search(r"\S {2,}\S", l) and len(cnt.ws(l)) >= 12 and cnt.ws(l) not in PF]
    assert wps and wns, "no runny witness lines"
    pr = cnt.ranges(r["pin_lines"], False)
    rr = cnt.ranges(r["release_lines"], True)
    pr2 = pr + [(wps[0][0], wps[0][0])]
    rr2 = rr + [(wns[0][0], wns[0][0])]
    r["pin_lines"] = m1.spec_of(pr2)
    r["release_lines"] = m1.spec_of(rr2)
    r["witness_pin"], r["witness_new"] = wps[0][1], wns[0][1]
    lr = {c: r[c] for c in cnt.HEADER}
    ok, why = cnt.check_row(POP[sid], lr, UP)
    assert ok, f"v_ws_runs row invalid: {why}"
    rows[sid] = r

VARIANTS = {
    "v_wp11_dr": (v_wp11_dr, "witness_pin rule"),
    "v_wn11_hr": (v_wn11_hr, "witness_new rule"),
    "v_wn11_dr": (v_wn11_dr, "witness_new rule"),
    "v_wn_outside": (v_wn_outside, "witness_new rule"),
    "v_wp_in_RF": (v_wp_in_RF, "witness_pin rule"),
    "v_holds_witness": (v_holds_witness, "carries witnesses (want -)"),
    "v_note39": (v_note39, "note < 40 chars"),
    "v_newrow_partial": (v_newrow_partial, "newrow=0"),
    "v_section_missing": (v_section_missing, "section=0"),
    "v_cited_miss": (v_cited_miss, "pin_lines miss cited lines"),
    "v_rel_blob": (v_rel_blob, "blob mismatch"),
    "v_changed_flag": (v_changed_flag, "changed flag"),
    "v_holds_partial": (v_holds_partial, "holds needs every pair text-equal"),
    "v_unch_on_changed": (v_unch_on_changed, "unchanged-file rule"),
    "v_hr_all_eq": (v_hr_all_eq, "note < 40 chars"),
    "v_hr_all_eq_ooo": (v_hr_all_eq_ooo, "holds-reworded rule"),
    "v_removed_wn": (v_removed_wn, "removed carries witness_new (want -)"),
    "v_range_wide": (v_range_wide, "ranges do not parse or counts differ"),
    "v_counts": (v_counts, "ranges do not parse or counts differ"),
    "v_range_eof": (v_range_eof, "pin range outside file"),
    "v_short_range": (v_short_range, "carries < 20 non-whitespace chars"),
    "v_wrong_pin": (v_wrong_pin, "path/pin differ from population"),
    "v_dup": (v_dup, "duplicate ledger rows"),
    "v_flag_missing": (v_flag_missing, "not flagged in"),
    "v_sec_list_missing": (v_sec_list_missing, "not listed in SOURCES section"),
    "v_ws_runs": (v_ws_runs, None),  # must stay VALID (pristine = same as A)
}

# ---------------- repo plumbing ----------------
def sh(*args, cwd=None):
    p = subprocess.run(args, capture_output=True, text=True, cwd=cwd)
    if p.returncode != 0:
        raise RuntimeError(f"{' '.join(args[:3])} rc={p.returncode}: {p.stderr[-400:]}")
    return p.stdout.strip()

def write_fixture_files(rows, tip_src, know, extra=None):
    os.makedirs(f"{REPO}/registry", exist_ok=True)
    os.makedirs(f"{REPO}/corpus", exist_ok=True)
    led = ["\t".join(cnt.HEADER)]
    for sid in sorted(rows):
        r = rows[sid]
        sid_real = extra.get("dup_marker", sid) if extra and sid.endswith("#2") else sid
        cells = dict(r); cells["id"] = sid_real
        led.append("\t".join(cells[c] for c in cnt.HEADER))
    with open(f"{REPO}/registry/release-recheck-b11906.tsv", "w") as fh:
        fh.write("\n".join(led) + "\n")
    with open(f"{REPO}/corpus/SOURCES.md", "w") as fh:
        fh.write(tip_src)
    for u, body in know.items():
        path = f"{REPO}/{u}"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write(body)

def git_commit(msg):
    assert sh("git", "-C", REPO, "rev-parse", "--show-toplevel") == REPO
    sh("git", "-C", REPO, "add", "-A")
    sh("git", "-C", REPO, "-c", "user.name=M1Ctr fixture", "-c", "user.email=m1ctr@fixture.invalid",
       "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg)
    return sh("git", "-C", REPO, "rev-parse", "HEAD")

def build_repos():
    if os.path.exists(os.path.dirname(REPO)):
        shutil.rmtree(os.path.dirname(REPO))
    os.makedirs(os.path.dirname(REPO))
    sh("git", "clone", "--shared", "--no-checkout", "--quiet", LANE, REPO)
    assert sh("git", "-C", REPO, "rev-parse", "--show-toplevel") == REPO
    sh("git", "-C", REPO, "checkout", "--quiet", "--detach", LANE_TIP)
    write_fixture_files(ROWS0, TIP0, KNOW0)
    a_sha = git_commit("fixture A: all-valid 91-row ledger")
    shas = {"A": a_sha}
    for name, (fn, expect) in VARIANTS.items():
        sh("git", "-C", REPO, "checkout", "-q", "--detach", a_sha)
        rows, tip, know = dict(ROWS0), TIP0, dict(KNOW0)
        extra = None
        out = fn(rows, tip, know)
        if isinstance(out, str):
            tip = out
        elif isinstance(out, tuple):
            if len(out) == 4:
                rows, tip, know, extra = out
            else:
                rows, tip, know = out
        write_fixture_files(rows, tip, know, extra)
        shas[name] = git_commit(f"fixture {name}")
    json.dump(shas, open(f"{S}/shas.json", "w"))
    return shas

def run_counter(counter, repo, tip):
    p = subprocess.run([sys.executable, counter, "--repo", repo, "--tip", tip, "--upstream", UP],
                       capture_output=True, text=True, timeout=600)
    return p.returncode, p.stdout

def pristine_stage(shas):
    base = {}
    for name, sha in shas.items():
        rc, out = run_counter(PRISTINE, REPO, sha)
        base[name] = {"rc": rc, "out": out}
    json.dump(base, open(BASELINE, "w"))
    a = base["A"]
    print("A:", a["rc"], a["out"].splitlines()[1] if a["out"] else "EMPTY")
    assert a["rc"] == 0 and "met=True" in a["out"] and "detail:" not in a["out"], "fixture A not clean"
    for name, (fn, expect) in VARIANTS.items():
        b = base[name]
        if expect is None:
            assert b["rc"] == 0 and "detail:" not in b["out"], f"{name} should stay valid: {b['out'][-300:]}"
        else:
            assert expect in b["out"], f"{name} missing expected '{expect}':\n{b['out'][-400:]}"
    print("pristine baselines OK:", len(base), "fixtures")

# ---------------- mutants ----------------
def mutants_list():
    wn_rule = 'if len(wn) < 12 or wn not in R or wn in PF:'
    M = []
    def add(mid, cat, old, new, occ=None, fixtures=("A",)):
        M.append({"id": mid, "cat": cat, "old": old, "new": new, "occ": occ, "fixtures": fixtures})
    add("M01", "witness length", 'if len(wp) < 12 or wp not in P or wp in RF:',
        'if len(wp) < 5 or wp not in P or wp in RF:', fixtures=("A", "v_wp11_dr"))
    add("M02", "witness length", wn_rule, wn_rule.replace("< 12", "< 5"), occ=0, fixtures=("A", "v_wn11_hr"))
    add("M03", "witness length", wn_rule, wn_rule.replace("< 12", "< 5"), occ=1, fixtures=("A", "v_wn11_dr"))
    add("M04", "P construction", 'for p in pr))', 'for p in pr[:1]))')
    add("M05", "R construction",
        'R = ws(" ".join(" ".join(rtext[r[0] - 1:r[1]]) for r in rr if r))',
        'R = ws(" ".join(" ".join(rtext[0:r[1]]) for r in rr if r))', fixtures=("A", "v_wn_outside"))
    add("M06", "PF/RF construction", 'PF, RF = ws(" ".join(ptext)), ws(" ".join(rtext))',
        'PF, RF = ws(" ".join(rtext)), ws(" ".join(ptext))')
    add("M07", "RF construction", 'PF, RF = ws(" ".join(ptext)), ws(" ".join(rtext))',
        'PF, RF = ws(" ".join(ptext)), ws("")', fixtures=("A", "v_wp_in_RF"))
    add("M08", "in leg", 'wp not in P', 'wp in P')
    add("M09", "not-in leg", 'wn not in R', 'wn in R', occ=0)
    add("M10", "witness-presence leg", 'if wp != "-" or wn != "-":', 'if False:',
        fixtures=("A", "v_holds_witness"))
    add("M11", "note length", 'if len(note) < 40:', 'if len(note) < 30:', fixtures=("A", "v_note39"))
    add("M12", "note length", 'if len(note) < 40:', 'if len(note) <= 40:')
    add("M13", "newrow leg", 'and RELEASE in x and RELEASE_COMMIT in x for x in tip_src.splitlines()))',
        'and RELEASE in x for x in tip_src.splitlines()))', fixtures=("A", "v_newrow_partial"))
    add("M14", "newrow leg", 'ROW.match(x).group(1) not in base_ids', 'ROW.match(x).group(1) in base_ids')
    add("M15", "section leg", 'SECTION in x and x.startswith("#")', 'SECTION in x or x.startswith("#")',
        fixtures=("A", "v_section_missing"))
    add("M16", "section leg", 'SECTION = "Round-46 release re-verification"',
        'SECTION = "Round-46 release re-verificationX"')
    add("M17", "cited-line rule", '    if strong:', '    if strong and False:',
        fixtures=("A", "v_cited_miss"))
    add("M18", "cited-line rule", 'elif weak and not any(covered(n) for n in weak):', 'elif False:',
        fixtures=("A",))
    add("M19", "cited-line rule", 'strong = {n for n in strong if n <= len(ptext)}',
        'strong = {n for n in strong}', fixtures=("A",))
    add("M20", "blob check", 'if lr["pin_blob"] != pb or lr["release_blob"] != rb:',
        'if lr["pin_blob"] != pb:', fixtures=("A", "v_rel_blob"))
    add("M21", "changed check", 'changed = "0" if pb == rb else "1"',
        'changed = "0" if pb != rb else "1"')
    add("M22", "changed check", 'if lr["changed"] != changed:', 'if False:',
        fixtures=("A", "v_changed_flag"))
    add("M23", "holds rule", 'return all(eq), "holds needs every pair text-equal"',
        'return any(eq), "holds needs every pair text-equal"', fixtures=("A", "v_holds_partial"))
    add("M24", "unchanged rule",
        'return (changed == "0" and lr["release_lines"].replace(" ", "") == lr["pin_lines"].replace(" ", ""),',
        'return (lr["release_lines"].replace(" ", "") == lr["pin_lines"].replace(" ", ""),',
        fixtures=("A", "v_unch_on_changed"))
    add("M25", "unchanged rule", '== lr["pin_lines"].replace(" ", "")',
        '!= lr["pin_lines"].replace(" ", "")')
    add("M26", "holds-reworded rule", 'return all(r is not None for r in rr) and not all(eq), "holds-reworded rule"',
        'return all(r is not None for r in rr), "holds-reworded rule"',
        fixtures=("A", "v_hr_all_eq", "v_hr_all_eq_ooo"))
    add("M27", "drifted rule", 'return not all(r is None for r in rr), "drifted rule"',
        'return True, "drifted rule"', fixtures="ALL")  # all fixtures
    add("M28", "removed rule", 'if wn != "-":', 'if wn == "-":', fixtures=("A", "v_removed_wn"))
    add("M29", "removed rule", 'if first is None or first in rset:', 'if first is None or first not in rset:')
    add("M30", "removed rule", 'if len(x.strip()) >= 8', 'if len(x.strip()) >= 3')
    add("M31", "range geometry", 'if a < 1 or b < a or b - a >= 80:', 'if a < 1 or b < a or b - a >= 800:',
        fixtures=("A", "v_range_wide"))
    add("M32", "range geometry", 'if pr is None or rr is None or len(pr) != len(rr):',
        'if pr is None or rr is None:', fixtures=("A", "v_counts"))
    add("M33", "range geometry", 'if r[1] > len(ptext):', 'if r[1] > len(ptext) + 100:',
        fixtures=("A", "v_range_eof"))
    add("M34", "range geometry", 'if r and r[1] > len(rtext):', 'if r[1] > len(rtext):')
    add("M35", "20-char rule", '"".join(ptext[r[0] - 1:r[1]]))) < 20:',
        '"".join(ptext[r[0] - 1:r[1]]))) < 2:', fixtures=("A", "v_short_range"))
    add("M36", "population", 'c[9] != "on-release"', 'c[9] != "on-releas"')
    add("M37", "population", 'ROW = re.compile(r"^ {0,3}\\|\\s*(S\\d{3,})\\s*\\|")',
        'ROW = re.compile(r"^ {0,3}\\|\\s*(S\\d{4,})\\s*\\|")')
    add("M38", "release cell", 'if lr["release"] != RELEASE:', 'if lr["release"] != "b11889":')
    add("M39", "population identity", 'if lr["path"] != path or lr["pin_commit"] != pin:',
        'if lr["path"] != path:', fixtures=("A", "v_wrong_pin"))
    add("M40", "ws collapse", '    return re.sub(r"\\s+", " ", x).strip()', '    return x.strip()',
        fixtures=("A", "v_ws_runs"))
    add("M41", "excerpt", 'return "\\n".join(x.strip() for x in lines[r[0] - 1:r[1]] if x.strip())',
        'return "\\n".join(x.strip() for x in lines[r[0]:r[1] + 1] if x.strip())')
    add("M42", "dup tracking", '                    if d["id"] in ledger:', '                    if False:',
        fixtures=("A", "v_dup"))
    add("M43", "ledger header", 'if lines and lines[0].split("\\t") == HEADER:',
        'if lines and lines[0].split("\\t") != HEADER:')
    add("M44", "met composition", 'met = unverified == 0 and missing == 0 and section == 1 and newrow == 1',
        'met = unverified == 0 and section == 1 and newrow == 1', fixtures=("A", "v_flag_missing"))
    add("M45", "flags leg", 'if not any(re.search(rf"\\b{sid}\\b", x) and RELEASE in x for x in body.splitlines()):',
        'if False:', fixtures=("A", "v_flag_missing"))
    add("M46", "flags leg", 'if not any(re.search(rf"\\b{sid}\\b", x) for x in sec_lines):',
        'if False:', fixtures=("A", "v_sec_list_missing"))
    return M

def apply_mutant(src, m):
    old, new, occ = m["old"], m["new"], m["occ"]
    n = src.count(old)
    if occ is None:
        assert n == 1, f"{m['id']}: old string count {n}"
        return src.replace(old, new)
    assert n > occ, f"{m['id']}: only {n} occurrences"
    idx = -1
    for _ in range(occ + 1):
        idx = src.index(old, idx + 1)
    return src[:idx] + new + src[idx + len(old):]

def mutants_stage(shas, base, only=None):
    os.makedirs(MUTDIR, exist_ok=True)
    src = open(PRISTINE).read()
    M = mutants_list()
    if os.path.exists(RES):
        results = json.load(open(RES))
    else:
        results = {}
    for m in M:
        if only and not (only[0] <= m["id"] <= only[1]):
            continue
        mut_src = apply_mutant(src, m)
        mpath = f"{MUTDIR}/{m['id']}.py"
        with open(mpath, "w") as fh:
            fh.write(mut_src)
        fixtures = sorted(shas) if m["fixtures"] in (None, "ALL") else m["fixtures"]
        killed_at, diffs = [], {}
        for name in fixtures:
            rc, out = run_counter(mpath, REPO, shas[name])
            b = base[name]
            if (rc, out) != (b["rc"], b["out"]):
                killed_at.append(name)
                first = next((x for x, y in zip(out.splitlines(), b["out"].splitlines()) if x != y),
                             out.splitlines()[0] if out else "<empty stdout>")
                diffs[name] = {"rc": [b["rc"], rc], "first_diff": first[:160]}
        verdict = "killed" if killed_at else "survived"
        results[m["id"]] = {"cat": m["cat"], "verdict": verdict, "killed_at": killed_at,
                            "diffs": diffs, "sha256": hashlib.sha256(mut_src.encode()).hexdigest()[:16],
                            "fixtures": fixtures}
        print(m["id"], m["cat"], verdict, killed_at[:4], flush=True)
    json.dump(results, open(RES, "w"), indent=1)

if __name__ == "__main__":
    stage = sys.argv[1]
    if stage == "repos":
        shas = build_repos()
        print(json.dumps(shas, indent=1))
    elif stage == "pristine":
        pristine_stage(json.load(open(f"{S}/shas.json")))
    elif stage == "mutants":
        lo, hi = sys.argv[2], sys.argv[3]
        mutants_stage(json.load(open(f"{S}/shas.json")), json.load(open(BASELINE)), (lo, hi))
