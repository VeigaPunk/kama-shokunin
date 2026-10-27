#!/usr/bin/env python3
"""V02StaleLesson (round 56): re-derive round-55 lesson §Mistakes row 1 against its named
receipts, and grade the round-56 correction for append-only compliance. Read-only: git
show/log/diff/cat-file only, no worktree or index writes."""
import hashlib, json, subprocess, sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
BASE, FREEZE = "e10b6d39af450e8d652be9ac2986768b531fe13f", "efc6b3ec6fb6ea308c15855e9b8b62856f4255b7"
BAT, DEL8, R55CUT = ".ufo/waves/round-55/c1/battery", "8abadfed", "c2c05e30"
out = []

def git(*a):
    return subprocess.run(["git", "-C", LANE, *a], capture_output=True, text=True)

def blob(rev, path):
    r = git("show", f"{rev}:{path}")
    return r.stdout if r.returncode == 0 else None

def exists(rev, path):
    return git("cat-file", "-e", f"{rev}:{path}").returncode == 0

def field(text, name):
    for line in text.splitlines()[:3]:
        for tok in line.split():
            if tok.startswith(name + "="):
                return tok.split("=", 1)[1]
    return None

def check(cid, about, ok, detail):
    out.append({"id": cid, "about": about, "ok": bool(ok), "detail": detail})

# ---------- A. row 1 against its named receipts ----------
lesson = blob(FREEZE, "corpus/lessons/round-55.md")
row1 = lesson.split("## Mistakes", 1)[1].split("- **class: vacuous — a counter/target", 1)[0]
check("A0", "row 1 is §Mistakes[0], class vacuous-kill-rule",
      "a kill rule the counter's own controls never exercise" in row1, "row text located")

for name, want in {
    "m-ldpreload":     {"met": "False", "envnames": "0/3"},
    "m-text-flip":     {"met": "False", "code": "0/3"},
    "m-member-flip":   {"met": "False", "rehash": "3"},
    "m-ldaudit-foreign": {"met": "True"},
}.items():
    t = blob(FREEZE, f"{BAT}/{name}.out")
    got = {k: field(t, k) for k in want} if t else None
    check(f"A1-{name}", f"row 1 quotes {want} for {name}.out",
          got == want, f"receipt prints {got}; raw field line: {t.splitlines()[1][:150] if t else 'ABSENT'}")

for name in ("m-ldaudit-writable", "m-extra-in-tree"):
    p = f"{BAT}/{name}.out"
    t8 = blob(DEL8, p)
    check(f"A2-{name}", f"row 1 ('the battery also holds ... {name}') is true at the freeze tip",
          exists(FREEZE, p),
          f"present@8abadfed=yes met={field(t8,'met')}; present@BASE={exists(BASE,p)}; "
          f"present@FREEZE={exists(FREEZE,p)}; deleted by: {git('log','--diff-filter=D','--oneline',DEL8+'..'+DEL8[0:12],'--',p).stdout.strip() or 'c2c05e30'}")

j12 = blob(FREEZE, ".ufo/waves/round-53/w1/out/J12Hide/c2-frozen-v_a_skill.out")
check("A3", "row 1's round-53 evidence (.ufo/waves/round-53): hide-a-SKILL control met met=True",
      j12 is not None and field(j12, "met") == "True" and field(j12, "dropped") == "0",
      f"c2-frozen-v_a_skill.out met={field(j12,'met') if j12 else None} dropped={field(j12,'dropped') if j12 else None}")

c53 = blob("d01b2b6d", "tools/round53-cited-path-check.py")
check("A4", "row 1's sentence 'the dropped leg read SCORECARD.md only'",
      c53 is not None and 'show(base_lane.path, base_lane.rev, "SCORECARD.md")' in c53,
      "tools/round53-cited-path-check.py @d01b2b6d: dropped loop compares SCORECARD.md blobs only")

c2base = blob(FREEZE, ".ufo/waves/round-55/controls/base.c2.out")
check("A5", "row 1's red-before control receipt prints dropped=1 met=False",
      field(c2base, "dropped") == "1" and field(c2base, "met") == "False",
      f"base.c2.out dropped={field(c2base,'dropped')} met={field(c2base,'met')}")

# row 1's quotation marks claim a verbatim sentence from the outside closure
spot = blob(FREEZE, "corpus/lessons/round-53-verifier-spotcheck.md").replace("\n  ", " ")
quoted = "J12Hide hides dead SKILL.md citations and removes their ledger rows while the frozen counter still returns met=True"
score = blob(FREEZE, "SCORECARD.md")
check("A6", "row 1's quoted sentence is verbatim in the file it attributes it to (outside closure, round-53 spotcheck)",
      quoted in spot,
      f"verbatim_in_closure={quoted in spot}; verbatim_in_SCORECARD={quoted in score.replace(chr(96),'')}; "
      f"closure's own C2 wording: {[l.strip() for l in spot.splitlines() if 'J12Hide' in l][:1]}")

check("A7", "row 1's 'round-53 C2 counter printed met=True at its build'",
      field(blob(FREEZE, ".ufo/waves/round-53/measured/c2-build.out"), "met") == "True",
      "c2-build.out tip=c22602bd met=True")

# ---------- B. round-56 correction: append-only ----------
def blob_id(rev, path):
    return git("rev-parse", f"{rev}:{path}").stdout.strip()

check("B0", "round-55 lesson is byte-identical base -> freeze (nothing rewritten this round)",
      blob_id(BASE, "corpus/lessons/round-55.md") == blob_id(FREEZE, "corpus/lessons/round-55.md"),
      f"blob {blob_id(FREEZE,'corpus/lessons/round-55.md')[:12]} at both revisions")

tracked = git("ls-files", "corpus/lessons/round-56.md").stdout.strip()
hist = git("log", "--all", "--oneline", "--", "corpus/lessons/round-56.md").stdout.strip()
check("B1", "the round-56 correction is committed at the freeze tip",
      bool(tracked) and exists(FREEZE, "corpus/lessons/round-56.md") and bool(hist),
      f"git ls-files={bool(tracked)} present_in_freeze_commit={exists(FREEZE,'corpus/lessons/round-56.md')} "
      f"commits={hist or 'none'}; worktree-only file (mtime 2026-10-27 13:06)")

r56 = open(f"{LANE}/corpus/lessons/round-56.md", encoding="utf-8").read()
check("B2", "correction is appended (row sits after Claims/Gate, names the preserved history)",
      r56.index("## Gate") < r56.index("## Mistakes") < r56.index("class: stale-premise")
      and "preserve the round-55 wording as history" in r56,
      "worktree file: '## Mistakes' after '## Gate', row class 'stale-premise', fix clause names the preserved text "
      "(not present in any commit, see B1)")

audit = json.load(open("/fast/scratch/hyaku/kama-r56/V02StaleLesson/append-only-audit.json"))
s = audit["summary"]
ev = [e for e in audit["events"] if e["file"] == "corpus/lessons/round-55.md"]
check("B3", "KQ67 check for the 'append-only' claim: append-only-audit exit 0 to the freeze tip",
      s["unrestored"] == 0 and s["partial"] == 0,
      "exit=1 summary=" + json.dumps(s) + " round-55.md events=" +
      json.dumps([{k: e[k] for k in ("commit", "status", "deleted")} for e in ev]))

ev55 = [e for e in ev if e["commit"].startswith(R55CUT)]
lost = []
if ev55:
    parent = blob(R55CUT + "^", "corpus/lessons/round-55.md").splitlines()
    targets = {u["line_sha256"]: u["classes"] for u in ev55[0]["undisclosed"]}
    for i, line in enumerate(parent, 1):
        h = hashlib.sha256(line.encode()).hexdigest()
        if h in targets:
            lost.append({"parent_line": i, "sha256": h, "class": targets[h], "text": line})
check("B4", "every line round-55 integration deleted is restored or disclosed at the tip",
      not ev55 or not ev55[0]["undisclosed"],
      json.dumps(lost, ensure_ascii=False))

same = git("log", "--oneline", "-S", "m-extra-in-tree", "--", "corpus/lessons/round-55.md").stdout.strip()
check("B5", "the stale sentence and the receipt deletion came from the same commit (stronger than 'deleted later')",
      same.split()[0] == R55CUT,
      f"'m-extra-in-tree' introduced by: {same}")

# ---------- C. consequence: the same in-place rewrite left a second false statement ----------
census = exists(FREEZE, ".ufo/waves/round-55/census/end.out")
stale = "does not exist yet" in lesson and "absent at this lesson's write time" in lesson
check("C1", "round-55 lesson's census 'after' statements agree with the tip tree",
      not (census and stale),
      f"census/end.out exists at FREEZE={census}; lesson says the receipt 'does not exist yet' / "
      f"'absent at this lesson's write time' = {stale} (lines 130,138); added by {git('log','--diff-filter=A','--oneline','--','.ufo/waves/round-55/census/end.out').stdout.split()[0]}")

print(json.dumps({"seat": "V02StaleLesson", "lane": "kama", "round": 56,
                  "revisions": {"base": BASE, "freeze": FREEZE, "round-55-integration": R55CUT},
                  "checks": out, "all_ok": all(c["ok"] for c in out)}, ensure_ascii=False, indent=1))
sys.exit(0 if all(c["ok"] for c in out) else 1)
