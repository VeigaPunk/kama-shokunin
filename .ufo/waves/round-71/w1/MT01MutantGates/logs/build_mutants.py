import pathlib, sys
sys.path.insert(0, "/fast/scratch/hyaku/kama-r71/MT01MutantGates")
from mutlib import sha
S = pathlib.Path("/fast/scratch/hyaku/kama-r71/MT01MutantGates")
P = S/"pristine"; T = S/"host"/"tools"

def build(base, patches, out, tag):
    txt = base.read_text()
    for old, new in patches:
        n = txt.count(old)
        if n != 1:
            raise SystemExit(f"{tag}: want 1 occurrence of {old[:70]!r}, found {n}")
        txt = txt.replace(old, new)
    out.write_text(txt)
    compile(txt, str(out), "exec")
    print(f"{tag}\t{sha(out)}")

c1 = (P/"pre-report-gate.py").read_text()
c1p = lambda name: (P/"pre-report-gate.py")
base1 = c1p("x")
build(base1, [('        "exit": 0 if failed == 0 and uncommitted == 0 else 1,', '        "exit": 0,')], T/"pre-report-gate-m1-exit0.py", "c1-m1-exit0")
build(base1, [('    uncommitted = len(records) if code_clean == 0 else 0', '    uncommitted = 0')], T/"pre-report-gate-m2-uncommitted0.py", "c1-m2-uncommitted0")
build(base1, [('            "ok": code == 0,\n', '            "ok": code == 0 or bool(text.strip()),\n')], T/"pre-report-gate-m3-fail-only-silent.py", "c1-m3-fail-only-silent")
build(base1, [('        "ok": code_clean == 0 and uncommitted == 0,', '        "ok": code_clean == 0,')], T/"pre-report-gate-m4-roundclean-ok.py", "c1-m4-roundclean-ok")
build(base1, [('    failed = sum(1 for arm in arms if not arm["ok"])', '    failed = 0')], T/"pre-report-gate-m5-failed0.py", "c1-m5-failed0")
build(base1, [('            "ok": code == 0,\n', '            "ok": code == 0 or (name == "worktree-landing" and "MISSING" not in text),\n')], T/"pre-report-gate-m6-accept-dirty.py", "c1-m6-accept-dirty")

b2 = P/"census-waiver-boundary.py"
build(b2, [('    exit_code = 0 if (survivors == 0 and held) else 1', '    exit_code = 0')], T/"census-waiver-boundary-m1-exit0.py", "c2-m1-exit0")
build(b2, [('    survivors = len(SHIM_ORDER) - killed', '    survivors = 0')], T/"census-waiver-boundary-m2-survivors0.py", "c2-m2-survivors0")
build(b2, [('            killed = bool(failed)', '            killed = False')], T/"census-waiver-boundary-m3-killedfalse.py", "c2-m3-killedfalse")
build(b2, [('    c.add("waiver_never_covers_fail", r.code != 0, f"exit={r.code}")', '    c.add("waiver_never_covers_fail", True, f"exit={r.code}")')], T/"census-waiver-boundary-m4-drop-fail-waiver.py", "c2-m4-drop-fail-waiver")
build(b2, [('            killed = bool(failed)\n            attributed = expected in failed', '            killed = True\n            attributed = True')], T/"census-waiver-boundary-m5-accepted-as-killed.py", "c2-m5-accepted-as-killed")
build(b2, [('    held = all(c.held for c in cases)', '    held = all(c.held for c in cases if c.id != 7)')], T/"census-waiver-boundary-m6-landed-blind.py", "c2-m6-landed-blind")
build(b2, [('    c.add("waiver_keeps_not_evaluated", _has(r, "not_evaluated", "1"), _kv(r, "not_evaluated"))', '    c.add("waiver_keeps_not_evaluated", True, _kv(r, "not_evaluated"))')], T/"census-waiver-boundary-m7-drop-waiver-ne.py", "c2-m7-drop-waiver-ne")

b3 = P/"round71-province-host-claims.py"
build(b3, [('        if correction["tag"] != claim["tag"]:\n            continue\n        if correction["date"] <= claim["date"]:\n            continue\n        if correction["verdict"] != claim["live"]:\n            continue\n',
            '        if correction["tag"] != claim["tag"]:\n            continue\n')], T/"round71-province-host-claims-m1-accept-any.py", "c3-m1-accept-any")
build(b3, [('        if correction["verdict"] != claim["live"]:\n            continue\n', '')], T/"round71-province-host-claims-m2-ignore-verdict.py", "c3-m2-ignore-verdict")
build(b3, [('        if correction["tag"] != claim["tag"]:\n            continue\n', '')], T/"round71-province-host-claims-m3-wrong-tag.py", "c3-m3-wrong-tag")
build(b3, [('            base_paragraphs = marker_paragraphs(base_text)\n            tip_paragraphs = marker_paragraphs(tip_text)\n            rewritten = [tag for tag, paragraph in base_paragraphs.items()\n                         if tip_paragraphs.get(tag) != paragraph]\n            rewritten += [tag for tag in base_tags\n                          if tag not in tip_paragraphs and tag not in rewritten]\n',
            '            rewritten = []\n')], T/"round71-province-host-claims-m4-drop-rewritten.py", "c3-m4-drop-rewritten")
build(b3, [('    uncovered = sum(1 for claim in claims if claim["contradicted"] and not claim["covered"])', '    uncovered = 0')], T/"round71-province-host-claims-m5-uncovered0.py", "c3-m5-uncovered0")
build(b3, [('        if correction["date"] <= claim["date"]:\n            continue\n', '')], T/"round71-province-host-claims-m6-drop-date.py", "c3-m6-drop-date")
