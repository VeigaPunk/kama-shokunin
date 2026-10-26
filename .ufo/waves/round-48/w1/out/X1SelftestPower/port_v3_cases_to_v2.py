#!/usr/bin/env python3
"""port_v3_cases_to_v2.py - run the 27 selftest cases of append-only-audit.py v3 against the v2
tool (git 33e0058:tools/append-only-audit.py).

Two modes, both keeping the v3 case text and only touching what v2 cannot express:

  verbatim  the v3 case body as written: five-cell contract rows, v3 HEADER, v3 assertions.
            A case that raises (AuditError on `5 cells, want 4`, KeyError on a v3-only field)
            counts as a failed case, exactly as v3's own `case()` treats an exception.

  compat    the most generous adaptation that is not a field rename: v2's parse_contract is
            wrapped so a fifth `region` cell is dropped before v2's four-cell validation. All
            assertions stay verbatim. Anything that still fails is a behavioural gap, not a
            schema gap.

Every v3 conjunction term is kept character-identical but split into its own check, so a failure
points at the term. Fixtures are built with the v2 module's own Fixture/lines/AuditError, so the
only thing under test is v2's audit/exit_code/parse_contract.

Source of the cases: kama-shokunin/tools/append-only-audit.py:507-849 (v3).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import tempfile


def load(path):
    spec = importlib.util.spec_from_file_location("aoa_v2", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class Ctx:
    def __init__(self, v, root):
        self.v, self.root = v, root


def cap(res):
    """What v2 actually computed, for the report."""
    if not isinstance(res, dict):
        return {}
    ev = res.get("events", [])
    return {"keys": sorted(res.keys()), "summary": dict(res.get("summary", {})),
            "event_keys": sorted(ev[0].keys()) if ev else [],
            "events": [dict(e) for e in ev]}


def ev_key(ev, k):
    """Field access that names the missing key instead of a bare KeyError trace."""
    if k not in ev:
        raise KeyError(f"event has no {k!r} (v3-only field; v2 event keys {sorted(ev)})")
    return ev[k]


# ------------------------------------------------------------------ the 27 cases
def build_cases(ctx):
    v = ctx.v
    root = ctx.root
    F = ["LOG.md", "SCORECARD.md", "corpus/QUALITY.md", "corpus/README.md", "corpus/SOURCES.md"]
    NOTES = ["# notes", "score.md is append-only below its head.",
             "The ## Axes and ## Plan heads of score.md are re-derived in place.",
             "know.md keeps its ## Errata region append-only.",
             "score.md gets appended to.", "score.md is not append-only.", "LOG.md is append-only."]
    SCORE = "score.md\tA-corr\tNOTES.md:2\texempt=## Axes|## Plan@NOTES.md:3\tx"
    KNOW = "know.md\tA-corr\tNOTES.md:4\tonly=## Errata@NOTES.md:4\tx"
    head, tail = ["# score", "## Axes"] + v.lines("h", 24), ["## Round 1"] + v.lines("d", 25)

    def scored(rows, body):
        f = v.Fixture(root)
        f.commit({"NOTES.md": NOTES, v.CONTRACT: [v.HEADER] + rows, "score.md": body})
        return f

    cases = []

    def case(name, fn):
        cases.append((name, fn))

    def c_none():
        f = v.Fixture(root)
        a = v.lines("a", 30)
        f.commit({"LOG.md": a})
        t = f.commit({"LOG.md": a + v.lines("b", 5)})
        res = v.audit(f.d, t, files=F)
        return [("events == []", lambda: res["events"] == []),
                ("exit_code == 0", lambda: v.exit_code(res) == 0)], cap(res)

    def c_below():
        f = v.Fixture(root)
        a = v.lines("a", 40)
        f.commit({"LOG.md": a})
        t = f.commit({"LOG.md": a[:21]})          # 19 deleted
        res = v.audit(f.d, t, files=F)
        return [("events == []", lambda: res["events"] == []),
                ("exit_code == 0", lambda: v.exit_code(res) == 0)], cap(res)

    def c_exact_unrestored():
        f = v.Fixture(root)
        a = v.lines("a", 40)
        f.commit({"corpus/QUALITY.md": a})
        c = f.commit({"corpus/QUALITY.md": a[20:]})   # exactly 20 deleted
        res = v.audit(f.d, c, files=F)
        e = res["events"]
        return [("len(events) == 1", lambda: len(e) == 1),
                ("commit == c", lambda: e[0]["commit"] == c),
                ("deleted == 20", lambda: e[0]["deleted"] == 20),
                ("status == unrestored", lambda: e[0]["status"] == "unrestored"),
                ("restored_by is None", lambda: e[0]["restored_by"] is None),
                ("restored_best is None", lambda: e[0]["restored_best"] is None),
                ("exit_code == 1", lambda: v.exit_code(res) == 1)], cap(res)

    def c_restored():
        f = v.Fixture(root)
        a = v.lines("a", 50)
        f.commit({"SCORECARD.md": a})
        c = f.commit({"SCORECARD.md": a[:10]})
        f.commit({"notes.md": ["x"]})
        r = f.commit({"SCORECARD.md": a + ["appended"]})
        t = f.commit({"SCORECARD.md": a + ["appended", "more"]})
        res = v.audit(f.d, t, files=F)
        e = res["events"]
        return [("len(events) == 1", lambda: len(e) == 1),
                ("commit == c", lambda: e[0]["commit"] == c),
                ("restored_by == r", lambda: e[0]["restored_by"] == r),
                ("restored_best == r", lambda: e[0]["restored_best"] == r),
                ("status == restored", lambda: e[0]["status"] == "restored"),
                ("restored_max == 40", lambda: e[0]["restored_max"] == 40),
                ("exit_code == 0", lambda: v.exit_code(res) == 0)], cap(res)

    def c_partial():
        f = v.Fixture(root)
        a = v.lines("a", 60)
        f.commit({"corpus/README.md": a})
        f.commit({"corpus/README.md": a[:20]})        # 40 deleted
        t = f.commit({"corpus/README.md": a[:40]})    # 20 back
        res = v.audit(f.d, t, files=F)
        e = res["events"]
        return [("len(events) == 1", lambda: len(e) == 1),
                ("status == partial", lambda: e[0]["status"] == "partial"),
                ("restored_max == 20", lambda: e[0]["restored_max"] == 20),
                ("restored_best == t", lambda: e[0]["restored_best"] == t),
                ("restored_by is None", lambda: e[0]["restored_by"] is None),
                ("exit_code == 1", lambda: v.exit_code(res) == 1)], cap(res)

    def c_undeclared():
        f = v.Fixture(root)
        a = v.lines("a", 50)
        f.commit({"notes.md": a, "corpus/other.md": a})
        t = f.commit({"notes.md": a[:5], "corpus/other.md": a[:5]})
        res = v.audit(f.d, t, files=F)
        return [("events == []", lambda: res["events"] == []),
                ("exit_code == 0", lambda: v.exit_code(res) == 0)], cap(res)

    def c_file_removed():
        f = v.Fixture(root)
        a = v.lines("a", 25)
        f.commit({"corpus/SOURCES.md": a, "LOG.md": ["keep"]})
        c = f.commit({}, delete=["corpus/SOURCES.md"])
        res = v.audit(f.d, c, files=["corpus/SOURCES.md"])
        e = res["events"]
        return [("len(events) == 1", lambda: len(e) == 1),
                ("deleted == 25", lambda: e[0]["deleted"] == 25),
                ("status == unrestored", lambda: e[0]["status"] == "unrestored"),
                ("exit_code == 1", lambda: v.exit_code(res) == 1)], cap(res)

    def c_merge_first_parent():
        f = v.Fixture(root)
        a = v.lines("a", 40)
        f.commit({"LOG.md": a})
        v._git(f.d, "checkout", "-q", "-b", "side")
        f.commit({"LOG.md": a[:10]})                  # side deletes 30
        v._git(f.d, "checkout", "-q", "-")
        f.commit({"LOG.md": a + ["main"]})
        v._git(f.d, *v.Fixture.IDENT, "merge", "-q", "-s", "ours", "--no-edit", "side")
        m = v._text(f.d, "rev-parse", "HEAD").strip()
        res = v.audit(f.d, m, files=F)
        e = res["events"]
        return [("len(events) == 1", lambda: len(e) == 1),
                ("commit != m", lambda: e[0]["commit"] != m),
                ("deleted == 30", lambda: e[0]["deleted"] == 30),
                ("status == restored", lambda: e[0]["status"] == "restored")], cap(res)

    def c_dashdash():
        f = v.Fixture(root)
        a = v.lines("a", 30) + ["--out x", "---", "--- y"]
        f.commit({"LOG.md": a})
        c = f.commit({"LOG.md": a[19:30]})            # deletes 19 plain + 3 dashed = 22
        res = v.audit(f.d, c, files=F)
        e = res["events"]
        return [("len(events) == 1", lambda: len(e) == 1),
                ("deleted == 22", lambda: e[0]["deleted"] == 22),
                ("status == unrestored", lambda: e[0]["status"] == "unrestored")], cap(res)

    def c_crlf_and_eof():
        f = v.Fixture(root)
        body = "".join(f"p{i} {os.urandom(3).hex()}\n" for i in range(25)).encode()
        crl = b"crlf line\r\n"
        f.commit({"LOG.md": body + crl + b"no newline at end"}, raw=True)
        c = f.commit({"LOG.md": b""}, raw=True)        # 27 deleted
        t = f.commit({"LOG.md": body + b"crlf line\n"}, raw=True)
        res = v.audit(f.d, t, files=F)
        e = res["events"]
        return [("len(events) == 1", lambda: len(e) == 1),
                ("commit == c", lambda: e[0]["commit"] == c),
                ("deleted == 27", lambda: e[0]["deleted"] == 27),
                ("restored_max == 25", lambda: e[0]["restored_max"] == 25),
                ("status == partial", lambda: e[0]["status"] == "partial")], cap(res)

    def c_multiset():
        f = v.Fixture(root)
        a = v.lines("a", 20) + ["dup"] * 3
        f.commit({"LOG.md": a})
        f.commit({"LOG.md": []})                     # 23 deleted
        t = f.commit({"LOG.md": a[:20] + ["dup"]})
        res = v.audit(f.d, t, files=F)
        e = res["events"]
        return [("len(events) == 1", lambda: len(e) == 1),
                ("restored_max == 21", lambda: e[0]["restored_max"] == 21),
                ("status == partial", lambda: e[0]["status"] == "partial")], cap(res)

    def c_window_max():
        f = v.Fixture(root)
        a = v.lines("a", 40)
        f.commit({"SCORECARD.md": a})
        f.commit({"SCORECARD.md": a[:15]})           # 25 deleted
        r = f.commit({"SCORECARD.md": a})
        t = f.commit({"SCORECARD.md": a[:35]})       # 5 of them deleted again (no event)
        res = v.audit(f.d, t, files=F)
        e = res["events"]
        return [("len(events) == 1", lambda: len(e) == 1),
                ("restored_max == 25", lambda: e[0]["restored_max"] == 25),
                ("restored_by == r", lambda: e[0]["restored_by"] == r),
                ("status == restored", lambda: e[0]["status"] == "restored"),
                ("held_at_to == 20", lambda: e[0]["held_at_to"] == 20),
                ("summary.regressed == 1", lambda: res["summary"]["regressed"] == 1),
                ("exit_code == 1", lambda: v.exit_code(res) == 1)], cap(res)

    def c_relocation():
        f = v.Fixture(root)
        a = v.lines("a", 50)
        f.commit({"LOG.md": a})
        c = f.commit({"LOG.md": a[25:] + a[:25]})
        res = v.audit(f.d, c, files=F)
        e = res["events"]
        return [("len(events) == 1", lambda: len(e) == 1),
                ("restored_by == c", lambda: e[0]["restored_by"] == c),
                ("status == restored", lambda: e[0]["status"] == "restored")], cap(res)

    def c_contract():
        f = v.Fixture(root)
        a = v.lines("a", 30)
        f.commit({"AGENTS.md": ["lessons are append-only"], "corpus/lessons/r1.md": a, "notes.md": a,
                  v.CONTRACT: [v.HEADER, "corpus/lessons/*.md\tA-corr\tAGENTS.md:1\t*\tx"]})
        t = f.commit({"corpus/lessons/r1.md": a[:5], "notes.md": a[:5]})
        res = v.audit(f.d, t)
        e = res["events"]
        checks = [("files == ['corpus/lessons/r1.md']", lambda: res["files"] == ["corpus/lessons/r1.md"]),
                  ("len(events) == 1", lambda: len(e) == 1),
                  ("events[0].file==r1", lambda: e[0]["file"] == "corpus/lessons/r1.md"),
                  ("declarations[0].ok is True", lambda: res["declarations"][0]["ok"] is True)]
        bads = ("path\trule\n", v.HEADER + "\nLOG.md\tA\tAGENTS.md:1\tx\n",
                v.HEADER + "\nLOG.md\tA\tAGENTS.md:1\texempt=Axes@AGENTS.md:1\tx\n",
                v.HEADER + "\nLOG.md\tA\tAGENTS.md:1\tonly=## E\tx\n")
        for i, bad in enumerate(bads):
            checks.append((f"bad contract {i + 1} rejected", lambda b=bad: rejects(b)))
        return checks, cap(res)

    def rejects(text):
        try:
            v.parse_contract(text)
        except v.AuditError:
            return True
        return False

    def c_threshold_flag():
        f = v.Fixture(root)
        a = v.lines("a", 40)
        f.commit({"LOG.md": a})
        t = f.commit({"LOG.md": a[:35]})              # 5 deleted
        res = v.audit(f.d, t, threshold=5, files=F)
        return [("len(events) == 1", lambda: len(res["events"]) == 1),
                ("exit_code == 1", lambda: v.exit_code(res) == 1)], cap(res)

    def c_crlf_restore_exact():
        f = v.Fixture(root)
        plain = [f"p{i} {os.urandom(3).hex()}" for i in range(30)]
        base = ("\n".join(plain) + "\n").encode()
        f.commit({"LOG.md": base + b"crlf line\r\n"}, raw=True)
        c = f.commit({"LOG.md": ("\n".join(plain[:10]) + "\n").encode()}, raw=True)
        t = f.commit({"LOG.md": base + b"crlf line\r\n"}, raw=True)
        res = v.audit(f.d, t, files=F)
        e = res["events"]
        return [("len(events) == 1", lambda: len(e) == 1),
                ("commit == c", lambda: e[0]["commit"] == c),
                ("deleted == 21", lambda: e[0]["deleted"] == 21),
                ("restored_max == 21", lambda: e[0]["restored_max"] == 21),
                ("status == restored", lambda: e[0]["status"] == "restored")], cap(res)

    def c_dup_kept_not_restored():
        f = v.Fixture(root)
        a = v.lines("a", 30) + ["dup"] * 3
        f.commit({"LOG.md": a})
        f.commit({"LOG.md": a[:10] + ["dup"]})
        t = f.commit({"LOG.md": a[:10] + ["dup", "unrelated"]})
        res = v.audit(f.d, t, files=F)
        e = res["events"]
        return [("len(events) == 1", lambda: len(e) == 1),
                ("deleted == 22", lambda: e[0]["deleted"] == 22),
                ("restored_max == 0", lambda: e[0]["restored_max"] == 0),
                ("status == unrestored", lambda: e[0]["status"] == "unrestored")], cap(res)

    def c_final_segment():
        return [("split_lines(x\\n)", lambda: v.split_lines(b"x\n") == [b"x"]),
                ("split_lines(x)", lambda: v.split_lines(b"x") == [b"x"]),
                ("split_lines(a\\n\\n)", lambda: v.split_lines(b"a\n\n") == [b"a", b""]),
                ("split_lines()", lambda: v.split_lines(b"") == []),
                ("split_lines(a\\r\\n)", lambda: v.split_lines(b"a\r\n") == [b"a\r"])], {}

    def c_vanished_and_paths():
        f = v.Fixture(root)
        a = v.lines("a", 25)
        contract = [v.HEADER, "corpus/lessons/*.md\tA-corr\tAGENTS.md:1\t*\tx",
                    "nope/*.md\tA\tAGENTS.md:1\t*\tx"]
        f.commit({"AGENTS.md": ["lessons and nope are append-only"], "corpus/lessons/gone.md": a,
                  "corpus/lessons/caf\u00e9.md": a, v.CONTRACT: contract})
        f.commit({"corpus/lessons/caf\u00e9.md": a + ["more"]}, delete=["corpus/lessons/gone.md"])
        t = f.commit({"corpus/lessons/bin.md": b"\x00\x01" * 40}, raw=True)
        t = f.commit({"corpus/lessons/bin.md": b"\x00\x02" * 41}, raw=True)
        res = v.audit(f.d, t)
        return [("files", lambda: res["files"] == ["corpus/lessons/bin.md", "corpus/lessons/caf\u00e9.md"]),
                ("vanished", lambda: res["vanished"] == ["corpus/lessons/gone.md"]),
                ("unmatched_patterns", lambda: res["unmatched_patterns"] == ["nope/*.md"]),
                ("binary_changes == 2", lambda: len(res["binary_changes"]) == 2),
                ("summary.bad_declarations == 0", lambda: res["summary"]["bad_declarations"] == 0),
                ("exit_code == 1", lambda: v.exit_code(res) == 1),
                ("CRLF contract rejected",
                 lambda: rejects(v.HEADER + "\r\nLOG.md\tA\tAGENTS.md:1\t*\tx\r\n"))], \
            {"files": res["files"], "vanished": res["vanished"],
             "unmatched_patterns": res["unmatched_patterns"], "binary_changes": res["binary_changes"]}

    # ---- v3 (round 48): regions, binding, regressed
    def c_exempt_rewritten():
        f = scored([SCORE], head + tail)
        c = f.commit({"score.md": ["# score", "## Axes"] + v.lines("h2", 24) + tail})
        res = v.audit(f.d, c)
        e = res["events"]
        return [("len(events) == 1", lambda: len(e) == 1),
                ("deleted == 24", lambda: e[0]["deleted"] == 24),
                ("graded == 0", lambda: ev_key(e[0], "graded") == 0),
                ("ungraded == 24", lambda: ev_key(e[0], "ungraded") == 24),
                ("status == ungraded", lambda: e[0]["status"] == "ungraded"),
                ("restored_best is None", lambda: e[0]["restored_best"] is None),
                ("summary.ungraded_lines == 24", lambda: res["summary"]["ungraded_lines"] == 24),
                ("exit_code == 0", lambda: v.exit_code(res) == 0)], cap(res)

    def c_exempt_gutted():
        f = scored([SCORE], head + tail)
        c = f.commit({"score.md": ["# score", "## Axes", "collapsed"] + tail})
        res = v.audit(f.d, c)
        e = res["events"]
        return [("len(events) == 1", lambda: len(e) == 1),
                ("graded == 24", lambda: ev_key(e[0], "graded") == 24),
                ("status == unrestored", lambda: e[0]["status"] == "unrestored"),
                ("exit_code == 1", lambda: v.exit_code(res) == 1)], cap(res)

    def c_exempt_gutted_then_regrown():
        f = scored([SCORE], head + tail)
        c = f.commit({"score.md": ["# score", "## Axes", "collapsed"] + tail})
        t = f.commit({"score.md": ["# score", "## Axes"] + v.lines("h3", 30) + tail})
        res = v.audit(f.d, t)
        e = res["events"]
        return [("len(events) == 1", lambda: len(e) == 1),
                ("commit == c", lambda: e[0]["commit"] == c),
                ("ungraded == 24", lambda: ev_key(e[0], "ungraded") == 24),
                ("status == ungraded", lambda: e[0]["status"] == "ungraded"),
                ("exit_code == 0", lambda: v.exit_code(res) == 0)], cap(res)

    def c_dated_rewritten():
        f = scored([SCORE], head + tail)
        c = f.commit({"score.md": head + ["## Round 1"] + v.lines("d2", 25)})
        res = v.audit(f.d, c)
        e = res["events"]
        return [("len(events) == 1", lambda: len(e) == 1),
                ("graded == 25", lambda: ev_key(e[0], "graded") == 25),
                ("ungraded == 0", lambda: ev_key(e[0], "ungraded") == 0),
                ("status == unrestored", lambda: e[0]["status"] == "unrestored"),
                ("exit_code == 1", lambda: v.exit_code(res) == 1)], cap(res)

    def c_only_errata():
        f = v.Fixture(root)
        body, errata = ["# know", "## Body"] + v.lines("k", 25), ["## Errata \u2014 x"] + v.lines("e", 20)
        f.commit({"NOTES.md": NOTES, v.CONTRACT: [v.HEADER, KNOW], "know.md": body + errata})
        c1 = f.commit({"know.md": ["# know", "## Body"] + errata})
        c2 = f.commit({"know.md": ["# know", "## Body", "## Errata \u2014 x"]})
        res = v.audit(f.d, c2)
        ev = {e["commit"]: e for e in res["events"]}
        def g(commit, key):
            return lambda: ev_key(ev[commit], key)
        return [("len(events) == 2", lambda: len(ev) == 2),
                ("c1 status == ungraded", lambda: ev[c1]["status"] == "ungraded"),
                ("c1 ungraded == 25", g(c1, "ungraded")),
                ("c2 graded == 20", g(c2, "graded")),
                ("c2 status == unrestored", lambda: ev[c2]["status"] == "unrestored"),
                ("exit_code == 1", lambda: v.exit_code(res) == 1)], cap(res)

    def c_clamp():
        f = v.Fixture(root)
        u = v.lines("u", 20)
        f.commit({"LOG.md": ["dup"] * 30 + u})
        f.commit({"LOG.md": ["dup"] * 10})          # 20 dup + 20 unique deleted
        t = f.commit({"LOG.md": u})                  # uniques back, every dup gone
        res = v.audit(f.d, t, files=F)
        e = res["events"]
        return [("len(events) == 1", lambda: len(e) == 1),
                ("deleted == 40", lambda: e[0]["deleted"] == 40),
                ("restored_max == 20", lambda: e[0]["restored_max"] == 20),
                ("status == partial", lambda: e[0]["status"] == "partial")], cap(res)

    def c_bad_declarations():
        f = v.Fixture(root)
        f.commit({"NOTES.md": NOTES, "score.md": head + tail, "LOG.md": ["x"],
                  v.CONTRACT: [v.HEADER, "score.md\tA\tNOTES.md:5\t*\tno append-only",
                               "score.md\tA\tNOTES.md:6\t*\tnegation",
                               "score.md\tA-corr\tNOTES.md:2\texempt=## Axes|## Round 1@NOTES.md:3\tunnamed",
                               "LOG.md\tA\tNOTES.md:2\t*\ttoken missing",
                               "LOG.md\tA\tNOTES.md:7\t*\tbound"]})
        res = v.audit(f.d, "HEAD")
        return [("oks == [F,F,F,F,T]", lambda: [d["ok"] for d in res["declarations"]] == [False, False, False, False, True]),
                ("exit_code == 1", lambda: v.exit_code(res) == 1)], cap(res)

    def c_clean():
        f = scored([SCORE, "LOG.md\tA\tNOTES.md:7\t*\tx"], head + tail)
        a = v.lines("c", 30)
        f.commit({"LOG.md": a})
        f.commit({"LOG.md": a[20:], "score.md": ["# score", "## Axes"] + v.lines("h4", 24) + tail})
        t = f.commit({"LOG.md": a})
        res = v.audit(f.d, t)
        s = res["summary"]
        return [("events == 2", lambda: s["events"] == 2),
                ("restored == 1", lambda: s["restored"] == 1),
                ("ungraded == 1", lambda: s["ungraded"] == 1),
                ("regressed == 0", lambda: s["regressed"] == 0),
                ("bad_declarations == 0", lambda: s["bad_declarations"] == 0),
                ("exit_code == 0", lambda: v.exit_code(res) == 0)], cap(res)

    for name, fn in [("no-deletion", c_none), ("below-threshold", c_below),
                     ("exact-threshold-unrestored", c_exact_unrestored), ("restored-later", c_restored),
                     ("partial", c_partial), ("undeclared-file", c_undeclared),
                     ("declared-file-removed", c_file_removed), ("merge-first-parent", c_merge_first_parent),
                     ("dashdash-lines", c_dashdash), ("crlf-and-eof", c_crlf_and_eof), ("multiset", c_multiset),
                     ("window-max", c_window_max), ("relocation", c_relocation), ("contract", c_contract),
                     ("threshold-flag", c_threshold_flag), ("crlf-restore-exact", c_crlf_restore_exact),
                     ("dup-kept-not-restored", c_dup_kept_not_restored), ("final-segment", c_final_segment),
                     ("vanished-and-paths", c_vanished_and_paths), ("exempt-rewritten", c_exempt_rewritten),
                     ("exempt-gutted", c_exempt_gutted), ("exempt-gutted-then-regrown", c_exempt_gutted_then_regrown),
                     ("dated-rewritten", c_dated_rewritten), ("only-errata", c_only_errata), ("clamp", c_clamp),
                     ("bad-declarations", c_bad_declarations), ("clean", c_clean)]:
        case(name, fn)
    return cases


def compat_parse_contract(v):
    """v2's parser, tolerating the fifth `region` cell: the most generous non-rename adaptation."""
    orig = v.parse_contract

    def parse_contract(text):
        lines = text.split("\n")
        if "\r" in text:
            raise v.AuditError("contract contains a carriage return (CRLF contract)")
        if not lines or lines[0].split("\t")[:4] != v.HEADER.split("\t") and lines[0] != v.HEADER:
            raise v.AuditError("contract header is not path<TAB>rule<TAB>declared_at<TAB>note")
        rows = []
        for n, line in enumerate(lines[1:], 2):
            if not line.strip():
                continue
            cells = line.split("\t")
            if len(cells) == 5:
                cells = cells[:3] + cells[4:]
            if len(cells) != 4:
                raise v.AuditError(f"contract line {n}: {len(cells)} cells, want 4")
            pat, rule, decl, note = (c.strip() for c in cells)
            if not pat or rule not in v.RULES or not __import__("re").fullmatch(r"[^:]+:\d+", decl):
                raise v.AuditError(f"contract line {n}: bad path, rule or declared_at")
            rows.append((pat, rule, decl, note))
        if not rows:
            raise v.AuditError("contract has no rows")
        return rows

    v.parse_contract = parse_contract
    return orig


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--v2", required=True, help="path to the v2 tool (git show <base>:tools/append-only-audit.py)")
    ap.add_argument("--mode", choices=("verbatim", "compat"), required=True)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--json", help="write per-case results here")
    a = ap.parse_args(argv)

    root = tempfile.mkdtemp(prefix=f"x1-{a.mode}-", dir=a.scratch)
    v = load(a.v2)
    if v.SCHEMA != "append-only-audit/v2":
        print(f"wrong tool: schema {v.SCHEMA}", file=sys.stderr)
        return 2
    patched_header = None
    if a.mode == "compat":
        compat_parse_contract(v)

    results = []
    for name, fn in build_cases(Ctx(v, root)):
        try:
            checks, captured = fn()
        except Exception as e:  # noqa: BLE001 - v3's own case() treats a crash as a failed case
            results.append({"case": name, "ok": False, "exception": f"{type(e).__name__}: {e}",
                            "checks": [], "captured": {}})
            print(f"FAIL {name}: exception {type(e).__name__}: {e}")
            continue
        evaluated, bad = [], []
        for label, thunk in checks:
            try:
                ok = bool(thunk())
            except Exception as e:  # noqa: BLE001 - a check that cannot be evaluated has failed
                ok, label = False, f"{label} [EXC {type(e).__name__}: {e}]"
            evaluated.append({"check": label, "ok": ok})
            if not ok:
                bad.append(label)
        results.append({"case": name, "ok": not bad, "exception": None,
                        "checks": evaluated,
                        "captured": captured})
        print(f"{'pass' if not bad else 'FAIL'} {name}" + ("" if not bad else " | failed: " + "; ".join(bad)))

    fails = sum(1 for r in results if not r["ok"])
    print(f"X1_PORT mode={a.mode} cases={len(results)} pass={len(results) - fails} fail={fails}")
    if a.json:
        with open(a.json, "w") as fh:
            json.dump({"mode": a.mode, "tool": a.v2, "cases": results}, fh, indent=1, sort_keys=True)
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
