#!/usr/bin/env python3
"""M2Ctr seat: mutation-test the frozen C2 counter tools/round44-verdict-ledger-audit.py.

Subcommands:
  build-good        Build FIX-GOOD (valid 204-row auto ledger + exact SCORECARD) and
                    every hand fixture; record the pristine counter's verdict per fixture.
  run-mutant <ID>   Run one mutant: committed controls via build_controls.py (mutant in
                    the scratch lane's tools/) + every hand fixture; convergence-patch
                    scorecards against the mutant, then cross-check pristine.
  collect           Aggregate mut/*/results.json into mutants.tsv on stdout.

All state lives under /fast/scratch/hyaku/kama-r44/M2Ctr. The lane repo is only read
(git clone --shared); fixture commits happen only inside scratch clones.
"""
import ast
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys

S = "/fast/scratch/hyaku/kama-r44/M2Ctr"
LANE_SRC = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
UPSTREAM = "/fast/scratch/hyaku/kama-r44/shared/llama.cpp"
COUNTER_REL = "tools/round44-verdict-ledger-audit.py"
PRISTINE_SHA = "1933e75b2a5308d09d0cfafd166c95cfcb1b7c15eaf1bf9ad2b321a453224bd1"
COMMITTED = os.path.join(LANE_SRC, ".ufo/waves/round-44/controls")
BUILDER_SRC = os.path.join(COMMITTED, "build_controls.py")
BASE = "9d9cc93ec50783cd114829a91757b90d57c78dc6"
FLEET_REV = "b0fd7b7f5ae6a0ad7717461c5fea8cb8a8724025"
HEADER = ["round", "trend", "side", "verdict", "repo", "rev", "path", "line", "note"]
TRENDS = ("expansion", "quality", "discernment")
ABSENT_NOTE = "automatic control: no line gives this trend a verdict"
C2_CONTROLS = ("base", "junk-c2-allimproved", "junk-c2-noscorecard")

AXES_ROW_DEFAULT = ("| **calibration** | **7** | calibration ledger cite: "
                    "registry/verdict-ledger.tsv (round-44 C2) | score round 44 |")


def gshow(repo, rev, path):
    p = subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"], capture_output=True, text=True)
    return p.stdout if p.returncode == 0 else None


def sh(*a, check=True):
    return subprocess.run(a, capture_output=True, text=True, check=check)


def pristine_source():
    src = open(os.path.join(S, "lane", COUNTER_REL)).read()
    assert hashlib.sha256(src.encode()).hexdigest() == PRISTINE_SHA, "pristine counter hash mismatch"
    return src


def load_pristine_module():
    spec = importlib.util.spec_from_file_location("c2p", os.path.join(S, "lane", COUNTER_REL))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- mutant specs
MUTANTS = {
    "M01a": {
        "family": "read_line nearest-preceding-trend rule",
        "desc": "verdict words attach to the FIRST trend word on the line instead of the nearest preceding one",
        "edits": [
            ("    out, cur = {}, None\n    for m in TOK.finditer(line):\n        if m.group(1):\n"
             "            cur = m.group(1).lower()\n            continue\n",
             "    out, cur, first = {}, None, None\n    for m in TOK.finditer(line):\n        if m.group(1):\n"
             "            cur = m.group(1).lower()\n            if first is None:\n                first = cur\n"
             "            continue\n", 1),
            ("        out.setdefault(cur, set()).add(v)\n", "        out.setdefault(first, set()).add(v)\n", 1),
        ],
    },
    "M01b": {
        "family": "read_line nearest-preceding-trend rule",
        "desc": "verdict words attach to the NEXT trend word (deferred) instead of the nearest preceding one",
        "edits": [
            ("    out, cur = {}, None\n    for m in TOK.finditer(line):\n        if m.group(1):\n"
             "            cur = m.group(1).lower()\n            continue\n        if cur is None:\n"
             "            continue\n        if m.group(2):\n            v = \"unprovable-but-better\"\n"
             "        elif m.group(3):\n            v = \"unprovable\"\n        else:\n"
             "            v = m.group(4).lower()\n        out.setdefault(cur, set()).add(v)\n    return out\n",
             "    out, pending = {}, []\n    for m in TOK.finditer(line):\n        if m.group(1):\n"
             "            t = m.group(1).lower()\n            for v in pending:\n"
             "                out.setdefault(t, set()).add(v)\n            pending = []\n            continue\n"
             "        if m.group(2):\n            v = \"unprovable-but-better\"\n        elif m.group(3):\n"
             "            v = \"unprovable\"\n        else:\n            v = m.group(4).lower()\n"
             "        pending.append(v)\n    return out\n", 1),
        ],
    },
    "M02": {
        "family": "unprovable-but-better / unprovable distinction",
        "desc": "the token 'unprovable-but-better' on a cited line parses as plain 'unprovable' (distinction collapsed)",
        "edits": [("            v = \"unprovable-but-better\"\n", "            v = \"unprovable\"\n", 1)],
    },
    "M03a": {
        "family": "mixed rule",
        "desc": "mixed accepted with only ONE distinct verdict word on the cited line (>=2 -> >=1)",
        "edits": [("                                ok = len(got) >= 2\n",
                   "                                ok = len(got) >= 1\n", 1)],
    },
    "M03b": {
        "family": "mixed rule",
        "desc": "mixed requires EXACTLY two distinct verdict words (>=2 -> ==2)",
        "edits": [("                                ok = len(got) >= 2\n",
                   "                                ok = len(got) == 2\n", 1)],
    },
    "M03c": {
        "family": "mixed rule",
        "desc": "mixed accepted with ZERO verdict words on the cited line (>=2 -> !=1)",
        "edits": [("                                ok = len(got) >= 2\n",
                   "                                ok = len(got) != 1\n", 1)],
    },
    "M04a": {
        "family": "absent rule (note/line form)",
        "desc": "absent rows no longer need line '-' and a >=20-char note",
        "edits": [("                            if len(d[\"note\"]) < 20 or d[\"line\"] != \"-\":\n",
                   "                            if False:\n", 1)],
    },
    "M04b": {
        "family": "absent rule (no-verdict-line check)",
        "desc": "absent accepted even when a line of the file gives the trend a verdict word",
        "edits": [("                            elif text is not None and any(tr in read_line(x) for x in text):\n",
                   "                            elif False:\n", 1)],
    },
    "M04c": {
        "family": "absent rule (file missing vs no verdict line)",
        "desc": "absent accepted ONLY when the file is missing at the rev (no-verdict-line files must not be absent)",
        "edits": [("                            elif text is not None and any(tr in read_line(x) for x in text):\n",
                   "                            elif text is not None:\n", 1)],
    },
    "M05a": {
        "family": "repo/rev/path pinning",
        "desc": "repo/rev/path equality with the side's file no longer checked",
        "edits": [("                    elif (d[\"repo\"], d[\"rev\"], d[\"path\"]) != (repo, rev, path):\n",
                   "                    elif False:\n", 1)],
    },
    "M05b": {
        "family": "repo/rev/path pinning",
        "desc": "only repo is pinned; wrong rev/path accepted",
        "edits": [("                    elif (d[\"repo\"], d[\"rev\"], d[\"path\"]) != (repo, rev, path):\n",
                   "                    elif d[\"repo\"] != repo:\n", 1)],
    },
    "M06a": {
        "family": "duplicate keys",
        "desc": "duplicate (round,trend,side) rows no longer rejected (last row silently wins)",
        "edits": [("                    if seen[k] > 1:\n", "                    if False:\n", 1)],
    },
    "M07a": {
        "family": "ORDER comparison (overclaim/underclaim)",
        "desc": "overclaim and underclaim swapped (ORDER[s] > ORDER[o] -> <)",
        "edits": [("                elif ORDER[s] > ORDER[o]:\n", "                elif ORDER[s] < ORDER[o]:\n", 1)],
    },
    "M07b": {
        "family": "ORDER comparison (overclaim/underclaim)",
        "desc": "equal-verdict pairs no longer 'agree' (fall through to the ORDER check -> underclaim)",
        "edits": [("                elif s == o:\n                    agree += 1\n"
                   "                elif ORDER[s] > ORDER[o]:\n",
                   "                elif ORDER[s] > ORDER[o]:\n", 1)],
    },
    "M08a": {
        "family": "SCORECARD table set-equality",
        "desc": "extra scorecard table rows no longer rejected (textra dropped from met)",
        "edits": [("    met = len(valid) == total and tmiss == 0 and textra == 0 and summary == 1 and axes == 1\n",
                   "    met = len(valid) == total and tmiss == 0 and summary == 1 and axes == 1\n", 1)],
    },
    "M08b": {
        "family": "SCORECARD table set-equality",
        "desc": "table rows matched on (round,trend) only; the self/outside verdict cells are ignored",
        "edits": [
            ("                trow.add((c[0], c[1], c[2], c[3]))\n", "                trow.add((c[0], c[1]))\n", 1),
            ("mism.add((str(rnd), tr, s, o))\n", "mism.add((str(rnd), tr))\n", 3),
        ],
    },
    "M08c": {
        "family": "SCORECARD table set-equality",
        "desc": "missing scorecard table rows no longer rejected (tmiss dropped from met)",
        "edits": [("    met = len(valid) == total and tmiss == 0 and textra == 0 and summary == 1 and axes == 1\n",
                   "    met = len(valid) == total and textra == 0 and summary == 1 and axes == 1\n", 1)],
    },
    "M09a": {
        "family": "summary line",
        "desc": "the agreement-figures summary line is no longer required (summary forced to 1)",
        "edits": [("        summary = int(any(want in x for x in sec))\n", "        summary = 1\n", 1)],
    },
    "M09b": {
        "family": "summary line",
        "desc": "summary must match the wanted string EXACTLY (substring search dropped)",
        "edits": [("        summary = int(any(want in x for x in sec))\n",
                   "        summary = int(any(x.strip() == want for x in sec))\n", 1)],
    },
    "M09c": {
        "family": "summary line",
        "desc": "summary denominator n computed as agree only (drops overclaim+underclaim)",
        "edits": [("        n = agree + over + under\n", "        n = agree\n", 1)],
    },
    "M10a": {
        "family": "Axes calibration-row cite",
        "desc": "the ## Axes calibration row naming the ledger is no longer required (axes forced to 1)",
        "edits": [("        axes, inax = 0, False\n", "        axes, inax = 1, False\n", 1)],
    },
    "M10b": {
        "family": "Axes calibration-row cite",
        "desc": "the 'calibration' word requirement in the Axes row's second cell dropped (any row naming the ledger passes)",
        "edits": [("            if inax and x.lstrip().startswith(\"|\") and \"calibration\" in x.split(\"|\")[1].lower()"
                   " and LEDGER in x:\n",
                   "            if inax and x.lstrip().startswith(\"|\") and LEDGER in x:\n", 1)],
    },
}


def apply_edits(src, edits):
    for old, new, count in edits:
        got = src.count(old)
        assert got == count, f"anchor matched {got}x (want {count}): {old[:70]!r}"
        src = src.replace(old, new)
    return src


# ---------------------------------------------------------------- ledger + fixtures
def auto_ledger_lines():
    mod = load_pristine_module()
    lines = ["\t".join(HEADER)]
    for r in range(10, 44):
        for side in ("self", "outside"):
            repo, rev, path = mod.side_spec(r, side)
            text = gshow(FLEET if repo == "fleet" else os.path.join(S, "lane"), rev, path)
            for t in TRENDS:
                hits = [] if text is None else [
                    (i + 1, mod.read_line(x)[t]) for i, x in enumerate(text.splitlines()) if t in mod.read_line(x)]
                if not hits:
                    lines.append("\t".join([str(r), t, side, "absent", repo, rev, path, "-", ABSENT_NOTE]))
                else:
                    ln, vs = hits[-1]
                    v = sorted(vs)[0] if len(vs) == 1 else "mixed"
                    lines.append("\t".join([str(r), t, side, v, repo, rev, path, str(ln), "automatic"]))
    return lines


def row_index(ledger_lines):
    idx = {}
    for x in ledger_lines[1:]:
        f = x.split("\t")
        idx[(f[0], f[1], f[2])] = x
    return idx


def edit_row(ledger_lines, r, t, side, field, value):
    """field: 3=verdict 5=rev 6=path 7=line 8=note (0-based split index)."""
    out = []
    hit = 0
    for x in ledger_lines:
        f = x.split("\t")
        if len(f) == 9 and (f[0], f[1], f[2]) == (r, t, side):
            f[field] = value
            hit += 1
            out.append("\t".join(f))
        else:
            out.append(x)
    assert hit == 1, f"edit_row {(r, t, side)} hit {hit}"
    return out


def scorecard_text(table_rows, summary, axes_row, summary_absent=False):
    parts = [
        "# kama-shokunin — SCORECARD (M2Ctr mutation fixture)",
        "",
        "## Axes",
        "",
        "| Axis | Score | Evidence pointer (re-derivable at the measured commit) | Last change |",
        "|---|---|---|---|",
        axes_row,
        "",
        "### Round-44 calibration ledger",
        "",
        "| round | trend | self | outside | note |",
        "|---|---|---|---|---|",
    ]
    for (r, t, sv, ov) in table_rows:
        parts.append(f"| {r} | {t} | {sv} | {ov} | outside closure disagrees |")
    parts.append("")
    if not summary_absent:
        parts.append(summary)
    return "\n".join(parts) + "\n"


def build_fixture_dir(name, ledger_lines, table_rows, summary, axes_row,
                      summary_absent=False, write_scorecard=True, droot=None):
    d = os.path.join(droot, name)
    shutil.rmtree(d, ignore_errors=True)
    sh("git", "clone", "-q", "--shared", os.path.join(S, "lane"), d)
    sh("git", "-C", d, "checkout", "-q", BASE)
    top = sh("git", "-C", d, "rev-parse", "--show-toplevel").stdout.strip()
    assert os.path.realpath(top) == os.path.realpath(d), f"isolation check failed for {d}"
    os.makedirs(os.path.join(d, "registry"), exist_ok=True)
    with open(os.path.join(d, "registry/verdict-ledger.tsv"), "w") as fh:
        fh.write("\n".join(ledger_lines) + "\n")
    if write_scorecard:
        with open(os.path.join(d, "SCORECARD.md"), "w") as fh:
            fh.write(scorecard_text(table_rows, summary, axes_row, summary_absent))
    sh("git", "-C", d, "add", "-A")
    sh("git", "-C", d, "-c", "user.name=m44-m2ctr", "-c", "user.email=m44-m2ctr@fixture.invalid",
       "commit", "-qm", f"fixture {name}")
    tip = sh("git", "-C", d, "rev-parse", "HEAD").stdout.strip()
    return d, tip


def run_counter(counter_path, repo, tip, out_path):
    p = subprocess.run([sys.executable, counter_path, "--repo", repo, "--tip", tip, "--fleet", FLEET,
                        "--out", out_path], capture_output=True, text=True)
    return p


def parse_counter_output(text):
    counts, detail, met = {}, [], None
    for x in text.splitlines():
        if x.startswith("rows="):
            for tok in x.split():
                if "=" in tok:
                    k, v = tok.split("=", 1)
                    counts[k] = v
            met = counts.get("met") == "True"
        elif x.startswith("detail: "):
            detail.append(x[len("detail: "):])
    return {"counts": counts, "met": met, "detail": detail, "counts_line":
            next((x for x in text.splitlines() if x.startswith("rows=")), "")}


def norm_receipt(path):
    return "\n".join(x for x in open(path).read().splitlines() if not x.startswith("tip="))


# ---------------------------------------------------------------- fixture specs
def fixture_specs(good):
    """good = {ledger_lines, table_rows, summary, axes_row}."""
    L, T, SUM, AX = good["ledger_lines"], good["table_rows"], good["summary"], good["axes_row"]
    specs = {}

    def T2(rows):
        return sorted(rows, key=lambda x: (int(x[0]), x[1], x[2], x[3]))

    # ns-good: pristine-generated auto ledger, NO scorecard rewrite (BASE scorecard stays)
    specs["ns-good"] = dict(ledger=L, table=T, summary=SUM, axes=AX, write_scorecard=False, converge=False)
    # good: the anchor — pristine must say met=True
    specs["good"] = dict(ledger=L, table=T, summary=SUM, axes=AX, write_scorecard=True, converge=False)

    # k2 (M02): outside 28/expansion verdict ubb -> unprovable on the same ubb line 198
    led = edit_row(L, "28", "expansion", "outside", 3, "unprovable")
    tab = T2([("28", "expansion", "improved", "unprovable") if x[:2] == ("28", "expansion") else x for x in T])
    specs["k2"] = dict(ledger=led, table=tab, summary=SUM, axes=AX, write_scorecard=True, converge=True)

    # k2b (M02): BOTH ubb rows claimed as plain 'unprovable' on their ubb lines
    led = edit_row(edit_row(L, "28", "expansion", "outside", 3, "unprovable"),
                   "43", "quality", "self", 3, "unprovable")
    tab = T2([("28", "expansion", "improved", "unprovable") if x[:2] == ("28", "expansion")
              else ("43", "quality", "unprovable", "mixed") if x[:2] == ("43", "quality") else x for x in T])
    specs["k2b"] = dict(ledger=led, table=tab, summary=SUM, axes=AX, write_scorecard=True, converge=True)

    # k3a (M03a): self 10/expansion improved -> mixed on the same 1-verdict line 91
    led = edit_row(L, "10", "expansion", "self", 3, "mixed")
    tab = T2(T + [("10", "expansion", "mixed", "improved")])
    specs["k3a"] = dict(ledger=led, table=tab, summary=SUM, axes=AX, write_scorecard=True, converge=True)

    # k3c (M03c): outside 11/discernment -> mixed citing line 3 (trend word, zero verdicts)
    led = edit_row(edit_row(L, "11", "discernment", "outside", 3, "mixed"), "11", "discernment", "outside", 7, "3")
    tab = T2([("11", "discernment", "unchanged", "mixed") if x[:2] == ("11", "discernment") else x for x in T])
    specs["k3c"] = dict(ledger=led, table=tab, summary=SUM, axes=AX, write_scorecard=True, converge=True)

    # k4a (M04a): absent row with a 1-char note
    led = edit_row(L, "20", "expansion", "outside", 8, "x")
    specs["k4a"] = dict(ledger=led, table=T, summary=SUM, axes=AX, write_scorecard=True, converge=False)

    # k4b (M04b): 10/expansion outside claimed absent while line 17 gives it 'improved'
    led = edit_row(edit_row(edit_row(L, "10", "expansion", "outside", 3, "absent"),
                            "10", "expansion", "outside", 7, "-"),
                   "10", "expansion", "outside", 8,
                   "control: absent claimed while the file gives the trend a verdict")
    specs["k4b"] = dict(ledger=led, table=T, summary=SUM, axes=AX, write_scorecard=True, converge=True)

    # k5 (M05a/M05b): self 10/expansion path corrupted
    led = edit_row(L, "10", "expansion", "self", 6, ".ufo/reports/round-10/kama.md.bak")
    specs["k5"] = dict(ledger=led, table=T, summary=SUM, axes=AX, write_scorecard=True, converge=False)

    # k6 (M06a): duplicate row appended
    led = L + [row_index(L)[("10", "expansion", "self")]]
    specs["k6"] = dict(ledger=led, table=T, summary=SUM, axes=AX, write_scorecard=True, converge=False)

    # k7a (M07a): summary overclaim/underclaim swapped
    specs["k7a"] = dict(ledger=L, table=T,
                        summary="agreement=61/72 overclaim=8 underclaim=3 other=15 absent=15",
                        axes=AX, write_scorecard=True, converge=False)

    # k7b (M07b): an equal pair listed as a mismatch row, summary shifted to underclaim
    tab = T2(T + [("10", "expansion", "improved", "improved")])
    specs["k7b"] = dict(ledger=L, table=tab,
                        summary="agreement=60/72 overclaim=3 underclaim=9 other=15 absent=15",
                        axes=AX, write_scorecard=True, converge=True)

    # k8a (M08a): one extra table row for an agreeing key
    tab = T2(T + [("10", "expansion", "improved", "improved")])
    specs["k8a"] = dict(ledger=L, table=tab, summary=SUM, axes=AX, write_scorecard=True, converge=False)

    # k8b (M08b): one table row's self/outside cells swapped
    tab = T2([("19", "expansion", "unchanged", "improved") if x[:2] == ("19", "expansion") else x for x in T])
    specs["k8b"] = dict(ledger=L, table=tab, summary=SUM, axes=AX, write_scorecard=True, converge=False)

    # k8c (M08c): one mismatch row removed from the table
    tab = T2([x for x in T if x[:2] != ("10", "discernment")])
    specs["k8c"] = dict(ledger=L, table=tab, summary=SUM, axes=AX, write_scorecard=True, converge=False)

    # k9a (M09a): summary line removed
    specs["k9a"] = dict(ledger=L, table=T, summary=SUM, axes=AX, write_scorecard=True,
                        summary_absent=True, converge=False)

    # k9b (M09b): summary line with trailing prose (substring still matches)
    specs["k9b"] = dict(ledger=L, table=T, summary=SUM + " (auto)", axes=AX, write_scorecard=True,
                        converge=False)

    # k10a (M10a): Axes calibration row without the ledger cite
    specs["k10a"] = dict(ledger=L, table=T, summary=SUM,
                         axes="| **calibration** | **7** | calibration evidence without a ledger cite | score round 44 |",
                         write_scorecard=True, converge=False)

    # k10b (M10b): Axes row names the ledger without the word 'calibration' in cell 1
    specs["k10b"] = dict(ledger=L, table=T, summary=SUM,
                         axes="| C2 ledger | registry/verdict-ledger.tsv carries the calibration rows | round 44 |",
                         write_scorecard=True, converge=False)
    return specs


# ---------------------------------------------------------------- phases
def cmd_build_good():
    lane = os.path.join(S, "lane")
    assert os.path.isdir(lane), "run inside a prepared scratch: $S/lane must exist"
    pristine_source()  # hash gate
    ledger = auto_ledger_lines()
    assert len(ledger) == 205, f"auto ledger has {len(ledger)} lines"

    # ledger-only fixture first: parse the pristine counter's wanted table + summary
    specs = {"ns-good": dict(ledger=ledger, table=[], summary="", axes=AXES_ROW_DEFAULT,
                             write_scorecard=False, converge=False)}
    d, tip = build_fixture_dir("ns-good", ledger, [], "", AXES_ROW_DEFAULT,
                               write_scorecard=False, droot=os.path.join(S, "fix"))
    p = run_counter(os.path.join(S, "lane", COUNTER_REL), d, tip, os.path.join(S, "fix", "ns-good.pristine.out"))
    res = parse_counter_output(p.stdout)
    miss = sorted(ast.literal_eval(x[len("table missing "):]) for x in res["detail"] if x.startswith("table missing "))
    want = [x[len("summary line wanted: "):] for x in res["detail"] if x.startswith("summary line wanted: ")]
    assert len(miss) == 26 and want, f"unexpected ns-good detail: {len(miss)} missing, want={want}"
    good = {"ledger_lines": ledger, "table_rows": miss, "summary": want[0], "axes_row": AXES_ROW_DEFAULT}

    # good fixture: pristine must say met=True
    d, tip = build_fixture_dir("good", ledger, miss, want[0], AXES_ROW_DEFAULT,
                               write_scorecard=True, droot=os.path.join(S, "fix"))
    p = run_counter(os.path.join(S, "lane", COUNTER_REL), d, tip, os.path.join(S, "fix", "good.pristine.out"))
    res = parse_counter_output(p.stdout)
    assert res["met"] and p.returncode == 0, f"good fixture not met: {res['counts_line']} {res['detail'][:3]}"

    # all fixtures + pristine verdicts
    specs.update(fixture_specs(good))
    pristine = {}
    for name, sp in specs.items():
        if name in ("ns-good", "good"):
            pristine[name] = {"met": res["met"] if name == "good" else parse_counter_output(
                open(os.path.join(S, "fix", "ns-good.pristine.out")).read())["met"],
                "exit": p.returncode if name == "good" else None}
            continue
        d, tip = build_fixture_dir(name, sp["ledger"], sp["table"], sp["summary"], sp["axes"],
                                   sp.get("summary_absent", False), sp["write_scorecard"],
                                   droot=os.path.join(S, "fix"))
        p = run_counter(os.path.join(S, "lane", COUNTER_REL), d, tip, os.path.join(S, "fix", f"{name}.pristine.out"))
        pr = parse_counter_output(p.stdout)
        pristine[name] = {"met": pr["met"], "exit": p.returncode, "counts": pr["counts_line"]}
        print(f"pristine {name}: met={pr['met']} exit={p.returncode}")
    json.dump({"good": good, "specs": {k: {kk: vv for kk, vv in v.items()} for k, v in specs.items()},
               "pristine": pristine},
              open(os.path.join(S, "fixtures.json"), "w"), indent=1)
    print("build-good done; pristine met per fixture:",
          {k: v["met"] for k, v in pristine.items()})


def converge(spec, counter, droot):
    table, summary = list(spec["table"]), spec["summary"]
    d = tip = res = None
    for it in range(4):
        d, tip = build_fixture_dir(spec["name"], spec["ledger"], table, summary, spec["axes"],
                                   spec.get("summary_absent", False), spec["write_scorecard"], droot)
        p = run_counter(counter, d, tip, os.path.join(droot, f"{spec['name']}.mut.out"))
        res = parse_counter_output(p.stdout)
        if res["met"]:
            return d, tip, res, it
        miss = [ast.literal_eval(x[len("table missing "):]) for x in res["detail"] if x.startswith("table missing ")]
        extra = [ast.literal_eval(x[len("table extra "):]) for x in res["detail"] if x.startswith("table extra ")]
        want = [x[len("summary line wanted: "):] for x in res["detail"] if x.startswith("summary line wanted: ")]
        rows = [t for t in table if t not in extra]
        for t in miss:
            if t not in rows:
                rows.append(t)
        table = sorted(rows, key=lambda x: (int(x[0]), x[1], x[2], x[3]))
        if want:
            summary = want[0]
    return d, tip, res, -1


def cmd_run_mutant(mid):
    m = MUTANTS[mid]
    mdir = os.path.join(S, "mut", mid)
    shutil.rmtree(mdir, ignore_errors=True)
    os.makedirs(mdir)
    lane = os.path.join(mdir, "lane")
    sh("git", "clone", "-q", "--shared", os.path.join(S, "lane"), lane)
    src = pristine_source()
    mut = apply_edits(src, m["edits"])
    cpath = os.path.join(lane, COUNTER_REL)
    with open(cpath, "w") as fh:
        fh.write(mut)
    with open(os.path.join(mdir, "mutant.diff"), "w") as fh:
        p = subprocess.run(["diff", "-u", os.path.join(S, "lane", COUNTER_REL), cpath], capture_output=True, text=True)
        fh.write(p.stdout)
    mut_sha = hashlib.sha256(mut.encode()).hexdigest()
    shutil.copy(BUILDER_SRC, os.path.join(mdir, "build_controls.py"))

    # 1) committed controls, mutant in tools/
    p = subprocess.run([sys.executable, os.path.join(mdir, "build_controls.py"), "--lane", lane,
                        "--upstream", UPSTREAM, "--fleet", FLEET, "--scratch", os.path.join(mdir, "ctl")],
                       capture_output=True, text=True)
    builder_rc = p.returncode
    controls = {}
    for name in C2_CONTROLS:
        mine = os.path.join(mdir, f"{name}.c2.out")
        ref = os.path.join(COMMITTED, f"{name}.c2.out")
        if os.path.exists(mine) and os.path.exists(ref):
            a, b = norm_receipt(mine), norm_receipt(ref)
            controls[name] = {"match": a == b, "diff": "-" if a == b else _first_diff(b, a)}
        else:
            controls[name] = {"match": False, "diff": "receipt missing"}
    c1_match = all(norm_receipt(os.path.join(mdir, f"{n}.c1.out")) == norm_receipt(os.path.join(COMMITTED, f"{n}.c1.out"))
                   for n in ("base", "junk-c1-allunchanged", "junk-c1-draftonly",
                             "junk-c2-allimproved", "junk-c2-noscorecard")
                   if os.path.exists(os.path.join(mdir, f"{n}.c1.out")))

    # 2) hand fixtures
    fx = json.load(open(os.path.join(S, "fixtures.json")))
    specs, pristine_exp, good = fx["specs"], fx["pristine"], fx["good"]
    fixtures = {}
    for name, sp in specs.items():
        spec = dict(name=name, ledger=sp["ledger"], table=sp["table"], summary=sp["summary"],
                    axes=sp["axes"], summary_absent=sp.get("summary_absent", False),
                    write_scorecard=sp["write_scorecard"])
        droot = os.path.join(mdir, "fix")
        if sp["converge"]:
            d, tip, res, iters = converge(spec, cpath, droot)
            pr = run_counter(os.path.join(S, "lane", COUNTER_REL), d, tip,
                             os.path.join(droot, f"{name}.pristine.out"))
            prres = parse_counter_output(pr.stdout)
            fixtures[name] = {"mut_met": res["met"], "mut_exit": None, "mut_counts": res["counts_line"],
                              "converged": res["met"], "iters": iters,
                              "pristine_met_on_final": prres["met"], "pristine_exit_on_final": pr.returncode}
        else:
            d, tip = build_fixture_dir(name, spec["ledger"], spec["table"], spec["summary"], spec["axes"],
                                       spec["summary_absent"], spec["write_scorecard"], droot)
            p = run_counter(cpath, d, tip, os.path.join(droot, f"{name}.mut.out"))
            res = parse_counter_output(p.stdout)
            fixtures[name] = {"mut_met": res["met"], "mut_exit": p.returncode, "mut_counts": res["counts_line"],
                              "converged": True, "iters": 0,
                              "pristine_met_on_final": pristine_exp[name]["met"],
                              "pristine_exit_on_final": pristine_exp[name]["exit"]}
    out = {"id": mid, "family": m["family"], "desc": m["desc"], "mutant_sha256": mut_sha,
           "builder_exit": builder_rc,
           "controls": controls, "c1_controls_identical": c1_match, "fixtures": fixtures}
    json.dump(out, open(os.path.join(mdir, "results.json"), "w"), indent=1)
    print(f"{mid}: controls_diff={[k for k, v in controls.items() if not v['match']]} "
          "fixtures={" + ", ".join(f"{k}:{v['mut_met']}" for k, v in fixtures.items()) + "}")


def _first_diff(ref, mine):
    a, b = ref.splitlines(), mine.splitlines()
    for i in range(max(len(a), len(b))):
        x = a[i] if i < len(a) else "<eof>"
        y = b[i] if i < len(b) else "<eof>"
        if x != y:
            return f"L{i + 1}: committed={x[:110]!r} mutant={y[:110]!r}"
    return "identical"


def cmd_collect():
    rows = ["mutant\tfamily\tmutation\tcontrols_diff\tfixture_kills\tverdict\tsmallest_killing_fixture\tnote"]
    for mid in sorted(MUTANTS):
        r = json.load(open(os.path.join(S, "mut", mid, "results.json")))
        cdiff = [k for k, v in r["controls"].items() if not v["match"]]
        kills = []
        for name, f in r["fixtures"].items():
            pm = f["pristine_met_on_final"]
            if f["mut_met"] != pm:
                direction = "over-accepts" if f["mut_met"] else "over-rejects"
                kills.append(f"{name}({direction})")
        verdict = "killed" if (cdiff or kills) else "survivor"
        smallest = ""
        if kills:
            order = ["good", "k4a", "k5", "k6", "k9a", "k10a", "k10b", "k7a", "k8a", "k8b", "k8c",
                     "k2", "k2b", "k3a", "k3c", "k4b", "k7b", "k9b", "ns-good"]
            smallest = sorted(kills, key=lambda k: order.index(k.split("(")[0]))[0]
        note = ""
        if mid in ("M01a", "M01b", "M02") and "junk-c2-noscorecard" in cdiff:
            note = "noscorecard diff partly generation-coupled (mutant's read_line builds that control's ledger); see ns-good fixture"
        rows.append("\t".join([mid, r["family"], r["desc"], ",".join(cdiff) or "-", ";".join(kills) or "-",
                               verdict, smallest.split("(")[0] if smallest else "-", note]))
    print("\n".join(rows))


if __name__ == "__main__":
    if sys.argv[1] == "build-good":
        cmd_build_good()
    elif sys.argv[1] == "run-mutant":
        cmd_run_mutant(sys.argv[2])
    elif sys.argv[1] == "collect":
        cmd_collect()
    else:
        raise SystemExit("unknown subcommand")
