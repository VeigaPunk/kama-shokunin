#!/usr/bin/env python3
"""M1Ctr fixture builder for the C1 counter mutation battery.

Builds under $SCRATCH/ctl:
  basecheckout        throwaway BASE checkout, used to run release-recheck.py draft once
  pass                synthetic fully-valid ledger (6 TODO rows completed mechanically,
                      oracle-validated with the PRISTINE counter) + SOURCES section + flags
  F01..F32            pass + exactly one defect each
  IN2/IN3             mirrors of build_controls.py junk-c1-allunchanged / junk-c1-draftonly
Writes fixtures.json {name: {repo, tip}} and prints the pristine baseline per fixture.
"""
import importlib.util, json, os, re, shutil, subprocess, sys

SCRATCH = "/fast/scratch/hyaku/kama-r44/M1Ctr"
LANE = os.path.join(SCRATCH, "lane")
UP = "/fast/scratch/hyaku/kama-r44/shared/llama.cpp"
BASE = "9d9cc93ec50783cd114829a91757b90d57c78dc6"
REL = "d854d98bae598388ecea1ed84396587e5edc326d"
BC_PATH = os.path.join(LANE, ".ufo", "waves", "round-44", "controls", "build_controls.py")
CTL = os.path.join(SCRATCH, "ctl")
LEDGER_REL = "registry/release-recheck-b11889.tsv"
COUNTER = os.path.join(LANE, "tools", "round44-release-recheck-audit.py")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


c1 = load(COUNTER, "c1")
bc = load(BC_PATH, "bc")
os.makedirs(CTL, exist_ok=True)
fixtures = {}


def nonws(lines):
    return len(re.sub(r"\s", "", "".join(lines)))


def ptext_of(ent):
    return (c1.show(UP, ent["pin"], ent["path"]) or "").splitlines()


def rtext_of(ent):
    return (c1.show(UP, REL, ent["path"]) or "").splitlines() if c1.blob(UP, REL, ent["path"]) != "-" else []


def cover_ranges(ent, ptext):
    """Pin ranges covering all strong cited lines (else one weak), each span<=79, >=20 non-ws chars."""
    strong, weak = c1.cited(ent["cells"])
    strong = sorted(n for n in strong if 1 <= n <= len(ptext))
    weak = sorted(n for n in weak if 1 <= n <= len(ptext))
    targets = strong or weak[:1]
    n = len(ptext)
    if not targets:
        for a in range(1, min(n, 60)):
            for w in (3, 6, 12, 30):
                b = min(n, a + w - 1)
                if nonws(ptext[a - 1:b]) >= 20:
                    return [(a, b)]
        raise SystemExit(f"no >=20-char window in {ent['path']}")
    groups, cur = [], [targets[0]]
    for t in targets[1:]:
        if t - cur[0] <= 76:
            cur.append(t)
        else:
            groups.append(cur)
            cur = [t]
    groups.append(cur)
    out = []
    for g in groups:
        a, b = max(1, g[0] - 1), min(n, g[-1] + 1)
        while nonws(ptext[a - 1:b]) < 20 and b - a < 79:
            if a > 1:
                a -= 1
            if b < n and b - a < 79:
                b += 1
        out.append((a, b))
    return out


def rng_str(rs):
    return ",".join(f"{a}-{b}" for a, b in rs)


def parse_ranges(spec):
    return [tuple(map(int, x.split("-"))) if "-" in x else (int(x), int(x)) for x in spec.split(",")]


def make_lr(sid, ent, verdict, pin_lines, release_lines, note):
    pb = c1.blob(UP, ent["pin"], ent["path"])
    rb = c1.blob(UP, REL, ent["path"])
    changed = "0" if pb == rb else "1"
    return dict(zip(c1.HEADER, [sid, ent["path"], ent["pin"], "b11889", pb, rb, changed,
                                pin_lines, release_lines, verdict, note]))


# ---- draft once ----
base_tree = bc.clone(LANE, CTL, "basecheckout")
p = subprocess.run([sys.executable, os.path.join(LANE, "tools", "release-recheck.py"), "draft",
                    "--sources", os.path.join(base_tree, "corpus", "SOURCES.md"),
                    "--upstream", UP, "--release-name", "b11889", "--release-commit", REL],
                   capture_output=True, text=True)
draft_lines = [x for x in p.stdout.splitlines() if x.strip()]
assert draft_lines and draft_lines[0].split("\t") == c1.HEADER, f"draft bad: {p.stderr[:300]}"
draft = {}
for x in draft_lines[1:]:
    f = x.split("\t")
    draft[f[0]] = dict(zip(c1.HEADER, f))
print("draft rows:", len(draft))

base_src = c1.show(LANE, BASE, c1.SOURCES)
pop = c1.population(base_src)
assert set(pop) == set(draft), set(pop) ^ set(draft)

# ---- PASS rows (oracle = pristine counter) ----
pass_rows = {}
for sid in sorted(pop):
    ent, d = pop[sid], draft[sid]
    if d["verdict"] != "TODO":
        lr = {k: d[k] for k in c1.HEADER}
        ok, why = c1.check_row(ent, lr, UP)
        assert ok, f"draft row {sid} not valid under pristine counter: {why}"
        pass_rows[sid] = lr
        continue
    ptext = ptext_of(ent)
    pr = d["pin_lines"] if d["pin_lines"] != "-" else rng_str(cover_ranges(ent, ptext))
    pb, rb = c1.blob(UP, ent["pin"], ent["path"]), c1.blob(UP, REL, ent["path"])
    changed = "0" if pb == rb else "1"
    if changed == "0":
        lr = make_lr(sid, ent, "unchanged-file", pr, pr, f"mutation fixture: file unchanged at b11889 ({sid})")
    else:
        lr = make_lr(sid, ent, "drifted", pr, ",".join(["1-1"] * len(pr.split(","))),
                     f"mutation fixture: drifted placeholder for {sid}")
    ok, why = c1.check_row(ent, lr, UP)
    if not ok and d["pin_lines"] == "-":
        pr = rng_str(cover_ranges(ent, ptext))
        lr = make_lr(sid, ent, "unchanged-file" if changed == "0" else "drifted", pr,
                     pr if changed == "0" else ",".join(["1-1"] * len(pr.split(","))), lr["note"])
        ok, why = c1.check_row(ent, lr, UP)
    assert ok, f"PASS row {sid} invalid: {why}"
    pass_rows[sid] = lr
print("PASS rows validated:", len(pass_rows))


# ---- tree helpers ----
def ledger_text(rows):
    return "\t".join(c1.HEADER) + "\n" + "\n".join("\t".join(lr[k] for k in c1.HEADER) for lr in rows) + "\n"


def flag_targets(rows):
    sec, kb = [], {}
    for lr in rows:
        if lr["verdict"] not in ("drifted", "removed"):
            continue
        sid = lr["id"]
        sec.append(f"- {sid}: flagged {lr['verdict']} at b11889 (mutation fixture)")
        for u in [u.strip() for u in pop[sid]["cells"][10].split(",")]:
            if re.fullmatch(r"corpus/knowledge/[\w.\-]+\.md", u) and c1.show(LANE, BASE, u) is not None:
                kb.setdefault(u, []).append(f"- {sid} re-verified at b11889 (mutation fixture)")
    return sec, kb


def write_tree(name, rows):
    d = bc.clone(LANE, CTL, name)
    os.makedirs(os.path.join(d, "registry"), exist_ok=True)
    with open(os.path.join(d, LEDGER_REL), "w") as fh:
        fh.write(ledger_text(rows))
    sec, kb = flag_targets(rows)
    if sec:
        with open(os.path.join(d, "corpus", "SOURCES.md"), "a") as fh:
            fh.write("\n## Round-44 release re-verification\n\n" + "\n".join(sec) + "\n")
    for u, lines in kb.items():
        with open(os.path.join(d, u), "a") as fh:
            fh.write("\n".join(lines) + "\n")
    fixtures[name] = {"repo": d, "tip": bc.commit(d, name)}
    return d


def led_path(d):
    return os.path.join(d, LEDGER_REL)


def read_led(d):
    return open(led_path(d)).read()


def write_led(d, t):
    open(led_path(d), "w").write(t)


def edit_row(text, sid, col, value):
    out, hit = [], 0
    for x in text.splitlines():
        f = x.split("\t")
        if len(f) == 11 and f[0] == sid:
            f[col] = value
            hit += 1
            out.append("\t".join(f))
        else:
            out.append(x)
    assert hit == 1, f"edit_row {sid} hit={hit}"
    return "\n".join(out) + "\n"


def sources_path(d):
    return os.path.join(d, "corpus", "SOURCES.md")


def kb_paths_of(sid):
    return [u for u in [u.strip() for u in pop[sid]["cells"][10].split(",")]
            if re.fullmatch(r"corpus/knowledge/[\w.\-]+\.md", u) and c1.show(LANE, BASE, u) is not None]


def add_flags_for(d, sid, verdict):
    with open(sources_path(d), "a") as fh:
        fh.write(f"- {sid}: flagged {verdict} at b11889 (mutation fixture)\n")
    for u in kb_paths_of(sid):
        with open(os.path.join(d, u), "a") as fh:
            fh.write(f"- {sid} re-verified at b11889 (mutation fixture)\n")


def drop_sources_line(sid):
    def f(d):
        p = sources_path(d)
        lines = [x for x in open(p).read().splitlines()
                 if not (f"- {sid}:" in x and "mutation fixture" in x)]
        open(p, "w").write("\n".join(lines) + "\n")
    return f


def drop_kb_line(sid):
    def f(d):
        for u in kb_paths_of(sid):
            p = os.path.join(d, u)
            lines = [x for x in open(p).read().splitlines()
                     if not (f"- {sid} " in x and "mutation fixture" in x)]
            open(p, "w").write("\n".join(lines) + "\n")
    return f


def defect(name, fn):
    d = os.path.join(CTL, name)
    shutil.rmtree(d, ignore_errors=True)
    shutil.copytree(pass_tree, d, symlinks=True)
    fn(d)
    fixtures[name] = {"repo": d, "tip": bc.commit(d, name)}


# ---- PASS tree ----
pass_tree = write_tree("pass", [pass_rows[sid] for sid in sorted(pass_rows)])
pr = subprocess.run([sys.executable, COUNTER, "--repo", pass_tree, "--tip", fixtures["pass"]["tip"],
                     "--upstream", UP], capture_output=True, text=True)
print("PASS pristine exit", pr.returncode, (pr.stdout.splitlines()[1] if len(pr.stdout.splitlines()) > 1 else pr.stderr[:200]))
assert pr.returncode == 0 and "met=True" in pr.stdout, "PASS fixture does not pass pristine counter"

# IN1: lane clone read at BASE (no ledger, no section)
fixtures["IN1-base"] = {"repo": LANE, "tip": BASE}

# IN2 junk-c1-allunchanged (mirrors build_controls.py)
d = bc.clone(LANE, CTL, "junk-c1-allunchanged")
rows = [draft_lines[0]]
for x in draft_lines[1:]:
    f = x.split("\t")
    lines = f[7] if f[7] != "-" else "1-3"
    f[5], f[6], f[8], f[9], f[10] = f[4], "0", lines, "unchanged-file", "shortcut control"
    f[7] = lines
    rows.append("\t".join(f))
os.makedirs(os.path.join(d, "registry"), exist_ok=True)
open(os.path.join(d, LEDGER_REL), "w").write("\n".join(rows) + "\n")
open(os.path.join(d, "corpus/SOURCES.md"), "a").write("\n## Round-44 release re-verification (control)\n\nnone\n")
fixtures["IN2-allunchanged"] = {"repo": d, "tip": bc.commit(d, "junk-c1-allunchanged")}

# IN3 junk-c1-draftonly (mirrors build_controls.py)
d = bc.clone(LANE, CTL, "junk-c1-draftonly")
os.makedirs(os.path.join(d, "registry"), exist_ok=True)
open(os.path.join(d, LEDGER_REL), "w").write("\n".join(draft_lines) + "\n")
fixtures["IN3-draftonly"] = {"repo": d, "tip": bc.commit(d, "junk-c1-draftonly")}

# ---- defect fixtures ----
defect("F01-relblob", lambda d: write_led(d, edit_row(read_led(d), "S001", 5, pass_rows["S001"]["pin_blob"])))
defect("F02-pinblob", lambda d: write_led(d, edit_row(read_led(d), "S001", 4, "0" * 40)))
defect("F03-changed", lambda d: write_led(d, edit_row(read_led(d), "S001", 6, "0")))

# F04 80-line cap bust on S037
ent37 = pop["S037"]
s37 = sorted(n for n in c1.cited(ent37["cells"])[0] if n <= len(ptext_of(ent37)))
a4 = max(1, min(s37) - 1)
b4 = max(a4 + 81, max(s37) + 1)
assert b4 <= len(ptext_of(ent37)) and b4 - a4 >= 80, (a4, b4)
defect("F04-cap80", lambda d: write_led(d, edit_row(edit_row(read_led(d), "S037", 7, f"{a4}-{b4}"),
                                                    "S037", 8, "1-1")))
print("F04 range", a4, b4)

# F05 20-char rule: first row with a 2..19-char strong-cited line, pinned to exactly that line
f05 = None
for sid in sorted(pop):
    ent = pop[sid]
    ptext = ptext_of(ent)
    st = sorted(n for n in c1.cited(ent["cells"])[0] if n <= len(ptext))
    for n in st:
        if 2 <= nonws([ptext[n - 1]]) < 20:
            f05 = (sid, n, [x for x in st if x != n], ent, ptext)
            break
    if f05:
        break
assert f05, "no 2-19-char cited line found"
sid5, n5, rest5, ent5, pt5 = f05
groups, cur = [], [rest5[0]] if rest5 else []
for t in rest5[1:]:
    if t - cur[0] <= 76:
        cur.append(t)
    else:
        groups.append(cur)
        cur = [t]
if cur:
    groups.append(cur)
prs5 = [(n5, n5)] + [(max(1, g[0] - 1), min(len(pt5), g[-1] + 1)) for g in groups]
pin5, rel5 = rng_str(prs5), ",".join(["1-1"] * len(prs5))


def f05_edit(d):
    t = edit_row(read_led(d), sid5, 7, pin5)
    t = edit_row(t, sid5, 8, rel5)
    t = edit_row(t, sid5, 9, "drifted")
    t = edit_row(t, sid5, 10, f"mutation fixture: short cited line {n5} ({sid5})")
    write_led(d, t)
    add_flags_for(d, sid5, "drifted")


defect("F05-20char", f05_edit)
print("F05 row", sid5, "line", n5, "chars", nonws([pt5[n5 - 1]]), "pin", pin5)

# F06 strong-miss: drop one of S043's pin ranges that covers a strong line
ent43 = pop["S043"]
s43 = sorted(n for n in c1.cited(ent43["cells"])[0] if n <= len(ptext_of(ent43)))
pr43 = parse_ranges(pass_rows["S043"]["pin_lines"])
drop6 = next(i for i, (a, b) in enumerate(pr43) if any(a <= n <= b for n in s43))
keep43 = [f"{a}-{b}" for j, (a, b) in enumerate(pr43) if j != drop6]
defect("F06-strongmiss", lambda d: write_led(d, edit_row(edit_row(read_led(d), "S043", 7, ",".join(keep43)),
                                                         "S043", 8, ",".join(["1-1"] * len(keep43)))))
print("F06 dropped", pr43[drop6], "kept", keep43)

# F08 holds->any: multi-pair holds row, second release pair shifted until text differs
sid8 = next(s for s in sorted(pop) if draft[s]["verdict"] == "holds" and "," in draft[s]["pin_lines"])
ent8, lr8 = pop[sid8], pass_rows[sid8]
pt8, rt8 = ptext_of(ent8), rtext_of(ent8)
rr8 = parse_ranges(lr8["release_lines"])
a8, b8 = rr8[1]
new8 = None
for sh in (1, 2, 3, 5, 8):
    na, nb = a8 + sh, b8 + sh
    if nb <= len(rt8) and c1.excerpt(pt8, (a8, b8)) != c1.excerpt(rt8, (na, nb)):
        new8 = f"{na}-{nb}"
        break
assert new8, "no differing shift found"
rel8 = lr8["release_lines"].split(",")
rel8[1] = new8
defect("F08-holdsany", lambda d: write_led(d, edit_row(read_led(d), sid8, 8, ",".join(rel8))))
print("F08 row", sid8, "pair2", (a8, b8), "->", new8)

# F09 holds-reworded on an all-equal single-pair holds row
sid9 = next(s for s in sorted(pop) if draft[s]["verdict"] == "holds" and "," not in draft[s]["pin_lines"])
defect("F09-rewordedeq", lambda d: write_led(d, edit_row(edit_row(read_led(d), sid9, 9, "holds-reworded"),
                                                         sid9, 10, "mutation fixture: reworded placeholder note")))
print("F09 row", sid9)

# F10 reworded note too short; F11 reworded with a '-' release element (S043)
defect("F10-rewordednote", lambda d: write_led(d, edit_row(edit_row(read_led(d), "S001", 9, "holds-reworded"),
                                                           "S001", 10, "x")))
defect("F11-rewordeddash", lambda d: write_led(d, edit_row(edit_row(edit_row(
    read_led(d), "S043", 8, "1-1,-,1-1,1-1,1-1"), "S043", 9, "holds-reworded"),
    "S043", 10, "mutation fixture: reworded placeholder note")))

# F12 drifted with all-'-' release; F13 drifted note too short (S001)
defect("F12-driftednone", lambda d: write_led(d, edit_row(read_led(d), "S001", 8, "-")))
defect("F13-driftednote", lambda d: write_led(d, edit_row(read_led(d), "S001", 10, "x")))

# F14 removed while pin text still present (single-pair holds row -> removed)
def f14_edit(d):
    t = edit_row(edit_row(edit_row(read_led(d), sid9, 8, "-"), sid9, 9, "removed"),
                 sid9, 10, "mutation fixture: removed placeholder note")
    write_led(d, t)
    add_flags_for(d, sid9, "removed")


defect("F14-removedpresent", f14_edit)
print("F14 row", sid9)

# natural removed row? try S037 then S108 (oracle decides)
removed_sid, removed_k = None, 0
for cand in ("S037", "S108"):
    ent = pop[cand]
    k = len(pass_rows[cand]["pin_lines"].split(","))
    lr = make_lr(cand, ent, "removed", pass_rows[cand]["pin_lines"], ",".join(["-"] * k),
                 f"mutation fixture: removed placeholder for {cand}")
    ok, why = c1.check_row(ent, lr, UP)
    print("removed candidate", cand, "valid" if ok else f"invalid: {why}")
    if ok:
        removed_sid, removed_k = cand, k
        break


def removed_edit(d, sid, k, note, rel=None):
    t = edit_row(edit_row(edit_row(read_led(d), sid, 8, rel or ",".join(["-"] * k)),
                          sid, 9, "removed"), sid, 10, note)
    write_led(d, t)


if removed_sid:
    defect("F15-removednote", lambda d: removed_edit(d, removed_sid, removed_k, "x"))
    defect("F16-removedrel", lambda d: removed_edit(d, removed_sid, removed_k,
                                                    f"mutation fixture: removed placeholder for {removed_sid}",
                                                    rel=",".join(["1-1"] * removed_k)))

    def f20_edit(d):
        removed_edit(d, removed_sid, removed_k, f"mutation fixture: removed placeholder for {removed_sid}")
        drop_sources_line(removed_sid)(d)
        drop_kb_line(removed_sid)(d)

    defect("F20-removedunflagged", f20_edit)

# F17 remove S001 SOURCES line; F18 remove S001 knowledge flags; F19 strip b11889 from one
KB1 = kb_paths_of("S001")
assert KB1, "S001 has no existing knowledge file"
defect("F17-nosourcesline", drop_sources_line("S001"))
defect("F18-nokbline", drop_kb_line("S001"))


def f19_edit(d):
    p = os.path.join(d, KB1[0])
    lines = [x.replace("re-verified at b11889", "re-verified recently") if "- S001 " in x else x
             for x in open(p).read().splitlines()]
    open(p, "w").write("\n".join(lines) + "\n")


defect("F19-kbnorelease", f19_edit)
print("F17-F19 kb file:", KB1[0])

# F21 no section at all; F22 section text not a heading
def drop_section(d):
    p = sources_path(d)
    out, in_sec = [], False
    for x in open(p).read().splitlines():
        if x.startswith("#") and "Round-44 release re-verification" in x:
            in_sec = True
            continue
        if in_sec and x.startswith("#"):
            in_sec = False
        if not in_sec:
            out.append(x)
    open(p, "w").write("\n".join(out) + "\n")


defect("F21-nosection", drop_section)


def unheading_section(d):
    p = sources_path(d)
    lines = [x.lstrip("#").strip() if x.startswith("#") and "Round-44 release re-verification" in x else x
             for x in open(p).read().splitlines()]
    open(p, "w").write("\n".join(lines) + "\n")


defect("F22-unheading", unheading_section)

# F23 wrong header; F24 duplicate S001 row; F25 release cell; F26 path cell
defect("F23-header", lambda d: write_led(d, read_led(d).replace("\tverdict\t", "\tverdicts\t", 1)))
defect("F24-duprow", lambda d: open(led_path(d), "a").write("\t".join(pass_rows["S001"][k] for k in c1.HEADER) + "\n"))
defect("F25-releasecell", lambda d: write_led(d, edit_row(read_led(d), "S001", 3, "b11888")))
defect("F26-pathcell", lambda d: write_led(d, edit_row(read_led(d), "S001", 1, "tools/server/readme.md")))

# F27 release range outside file; F28 pin range outside file; F32 release range b<a
defect("F27-reloutside", lambda d: write_led(d, edit_row(read_led(d), "S001", 8, "1-999999")))
defect("F28-pinoutside", lambda d: write_led(d, edit_row(read_led(d), "S001", 7, "1-999999")))
defect("F32-relb<a", lambda d: write_led(d, edit_row(read_led(d), "S001", 8, "5-3")))

# ---- pristine baseline on every fixture ----
baseline = {}
for name, fx in sorted(fixtures.items()):
    p = subprocess.run([sys.executable, COUNTER, "--repo", fx["repo"], "--tip", fx["tip"], "--upstream", UP],
                       capture_output=True, text=True)
    baseline[name] = {"exit": p.returncode, "stdout": p.stdout, "stderr": p.stderr[-500:]}
    s = p.stdout.splitlines()[1] if len(p.stdout.splitlines()) > 1 else p.stderr[:150]
    print(f"baseline {name}: exit={p.returncode} {s}")

json.dump({"fixtures": fixtures, "baseline": baseline},
          open(os.path.join(SCRATCH, "fixtures.json"), "w"), indent=1)
print("fixtures:", len(fixtures))
