#!/usr/bin/env python3
"""Build proposed-selftest variants of append-only-audit.py, all from frozen blobs.

Inputs (extracted with `git show <commit>:tools/append-only-audit.py`):
  $S/v4-74558c71.py  build commit 74558c71c38ceaeace15fd4cf8aa9d84977584b1
  $S/v3.py           round-48 closure 438127bc01ff3b99f98468549d58046f932490ef

Outputs:
  v4-newcases.py        v4 + 4 clause cases (all expected to pass)
  v4-newcases-defect.py v4 + 4 clause cases + the typographic-apostrophe defect case
  v3-newcases.py        v3 + the same 5 cases (the 4 clause cases must fail on v3)
  proposed-selftest-cases.diff   v4 -> v4+4
  defect-case.diff               v4+4 -> v4+4+defect
"""
import difflib

S = "/fast/scratch/hyaku/kama-r49/X2SelftestPower"
V4 = f"{S}/v4-74558c71.py"
V3 = f"{S}/v3.py"

CLAUSE_CASES = '''    def t_wildcard_token_bound():
        # v4: a wildcard row binds through a line naming its directory token as a whole word,
        # and not through the token inside a longer word. `contract` covers the positive only
        # in passing (its declaring line is the token itself, which v3's substring test also
        # accepts); this pins both sides of the rule.
        f = Fixture(root)
        f.commit({"NOTES.md": ["# n", "the logs directory is append-only",
                               "our catalogs are append-only"],
                  "corpus/logs/a.md": ["this file is append-only"],
                  CONTRACT: [HEADER, "corpus/logs/*.md\\tA\\tNOTES.md:2\\t*\\tbound by token",
                             "corpus/logs/*.md\\tA\\tNOTES.md:3\\t*\\ttoken inside longer word"]})
        res = audit(f.d, "HEAD")
        oks = [d["ok"] for d in res["declarations"]]
        return oks == [True, False] and exit_code(res) == 1, str(res["declarations"])

    def t_origin_preamble_moved_under_head():
        # preamble-born text (origin None) moved under the exempt head and dropped there while
        # the head regrows past its parent size: the carve-out needs an origin inside an exempt
        # title, so None never qualifies and the deletion is graded (v4 origin clause, None side)
        p = lines("p", 25)
        f = scored([SCORE], ["# score"] + p + head[1:] + tail)
        f.commit({"score.md": ["# score", "## Axes"] + head[2:] + p + tail})
        c = f.commit({"score.md": ["# score", "## Axes"] + head[2:] + lines("regrow", 30) + tail})
        res = audit(f.d, c)
        e = [x for x in res["events"] if x["commit"] == c]
        return (len(e) == 1 and e[0]["deleted"] == 25 and e[0]["graded"] == 25 and e[0]["ungraded"] == 0
                and e[0]["status"] == "unrestored" and exit_code(res) == 1), str(res["events"])

    def t_negation_window_three_vs_four():
        # the negation window reaches three words before append-only, not four: both sides of
        # the {0,3} bound are pinned (v3 had no window and bound both lines)
        f = Fixture(root)
        f.commit({"NOTES.md": ["# n", "score.md is not yet considered strictly append-only",
                               "LOG.md is not yet really considered strictly append-only"],
                  "score.md": ["s"], "LOG.md": ["x"],
                  CONTRACT: [HEADER, "score.md\\tA\\tNOTES.md:2\\t*\\tthree words",
                             "LOG.md\\tA\\tNOTES.md:3\\t*\\tfour words"]})
        res = audit(f.d, "HEAD")
        oks = [d["ok"] for d in res["declarations"]]
        return oks == [False, True] and exit_code(res) == 1, str(res["declarations"])

    def t_negation_curly_apostrophe():
        # a word carrying a typographic apostrophe still counts as one word inside the negation
        # window (v4 `[\\\\w'\\u2019]`); dropping U+2019 from the class binds the line
        f = Fixture(root)
        f.commit({"NOTES.md": ["# n", "score.md is not the round\\u2019s append-only log",
                               "LOG.md is not the round's append-only log"],
                  "score.md": ["s"], "LOG.md": ["x"],
                  CONTRACT: [HEADER, "score.md\\tA\\tNOTES.md:2\\t*\\tcurly",
                             "LOG.md\\tA\\tNOTES.md:3\\t*\\tascii"]})
        res = audit(f.d, "HEAD")
        oks = [d["ok"] for d in res["declarations"]]
        return oks == [False, False] and exit_code(res) == 1, str(res["declarations"])

    def t_origin_multi_title():
        # origin(l) may hold several titles; one of them being exempt keeps the line ungraded
        # (`origin ... contains one of`). A line born both under the head and under a dated
        # heading is exempt (v4); a single-origin reading grades it.
        h = lines("h", 24) + ["shared line"]
        d = ["shared line"] + lines("d", 24)
        f = scored([SCORE], ["# score", "## Axes"] + h + ["## Round 1"] + d)
        c = f.commit({"score.md": ["# score", "## Axes"] + h[:-1] + lines("regrow", 30)
                      + ["## Round 1"] + d})
        res = audit(f.d, c, threshold=1)
        e = [x for x in res["events"] if x["commit"] == c]
        return (len(e) == 1 and e[0]["deleted"] == 1 and e[0]["graded"] == 0 and e[0]["ungraded"] == 1
                and e[0]["status"] == "ungraded" and exit_code(res) == 0), str(res["events"])

'''

DEFECT_CASE = '''    def t_negation_typographic_isnt():
        # the documented negation set is `isn't`/`aren't`, but both spellings in NEGATIONS and
        # NEG_WINDOW are ASCII-only: `isn\\u2019t append-only` binds on the build commit
        # (already covered by the uncommitted integration edit from seat K2Negation F1)
        f = Fixture(root)
        f.commit({"NOTES.md": ["# n", "LOG.md isn\\u2019t append-only", "QQ.md aren\\u2019t append-only"],
                  "LOG.md": ["x"], "QQ.md": ["x"],
                  CONTRACT: [HEADER, "LOG.md\\tA\\tNOTES.md:2\\t*\\tisn't curly",
                             "QQ.md\\tA\\tNOTES.md:3\\t*\\taren't curly"]})
        res = audit(f.d, "HEAD")
        oks = [d["ok"] for d in res["declarations"]]
        return oks == [False, False], str(res["declarations"])

'''

REG4 = ('                     ("binding-v4", t_binding_v4)]:')
REG4_NEW = ('                     ("binding-v4", t_binding_v4),\n'
            '                     ("wildcard-token-bound", t_wildcard_token_bound),\n'
            '                     ("origin-preamble-moved-under-head", t_origin_preamble_moved_under_head),\n'
            '                     ("negation-window-three-vs-four", t_negation_window_three_vs_four),\n'
            '                     ("negation-curly-apostrophe", t_negation_curly_apostrophe),\n'
            '                     ("origin-multi-title", t_origin_multi_title)]:')
REG3 = '                     ("preamble-graded", t_preamble_graded)]:'
REG3_NEW = ('                     ("preamble-graded", t_preamble_graded),\n'
            '                     ("wildcard-token-bound", t_wildcard_token_bound),\n'
            '                     ("origin-preamble-moved-under-head", t_origin_preamble_moved_under_head),\n'
            '                     ("negation-window-three-vs-four", t_negation_window_three_vs_four),\n'
            '                     ("negation-curly-apostrophe", t_negation_curly_apostrophe),\n'
            '                     ("origin-multi-title", t_origin_multi_title),\n'
            '                     ("negation-typographic-isnt", t_negation_typographic_isnt)]:')
ANCHOR = '    for name, fn in [("no-deletion", t_none)'


def patch(src, cases, reg_old, reg_new, out):
    assert src.count(ANCHOR) == 1 and src.count(reg_old) == 1
    res = src.replace(ANCHOR, cases + ANCHOR, 1).replace(reg_old, reg_new, 1)
    open(out, "w", encoding="utf-8").write(res)
    return res


v4 = open(V4, encoding="utf-8").read()
v3 = open(V3, encoding="utf-8").read()
new4 = patch(v4, CLAUSE_CASES, REG4, REG4_NEW, f"{S}/v4-newcases.py")
REG4_DEFECT = REG4_NEW.replace(
    '("origin-multi-title", t_origin_multi_title)]:',
    '("origin-multi-title", t_origin_multi_title),\n'
    '                     ("negation-typographic-isnt", t_negation_typographic_isnt)]:')
def4 = patch(v4, CLAUSE_CASES + DEFECT_CASE, REG4, REG4_DEFECT, f"{S}/v4-newcases-defect.py")
patch(v3, CLAUSE_CASES + DEFECT_CASE, REG3, REG3_NEW, f"{S}/v3-newcases.py")

open(f"{S}/proposed-selftest-cases.diff", "w", encoding="utf-8").write("".join(difflib.unified_diff(
    v4.splitlines(True), new4.splitlines(True),
    "a/tools/append-only-audit.py@74558c71", "b/tools/append-only-audit.py@74558c71+cases")))
open(f"{S}/defect-case.diff", "w", encoding="utf-8").write("".join(difflib.unified_diff(
    new4.splitlines(True), def4.splitlines(True),
    "a/tools/append-only-audit.py@74558c71+cases", "b/tools/append-only-audit.py@74558c71+cases+defect")))
print("built v4-newcases.py v4-newcases-defect.py v3-newcases.py proposed-selftest-cases.diff defect-case.diff")
