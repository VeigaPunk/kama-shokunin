#!/usr/bin/env python3
"""M2Ctr mutant generator: applies single-site textual mutations to pristine.py.

Each mutant must apply to exactly one site (count==1) so the mutant is minimal.
Writes mut/<name>.py and mut/manifest.json.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(HERE, "pristine.py")).read()

LAUNDER_ROW = "LOG.md\\tA\\tNOTES.md:1\\t*\\tfixture"
SCORE_ROW = "SCORE.md\\tA\\tNOTES.md:1\\t*\\tfixture"
WSELF_ROW = "notes/*.md\\tA-corr\\tnotes/a.md:1\\t*\\tfixture"
WNAMED_ROW = "notes/*.md\\tA-corr\\tREADME.md:1\\t*\\tfixture"

MUTANTS = [
    # --- NEG3 / NEGW -------------------------------------------------------
    ("M01-neg3-empty", "NEG3 tuple emptied", 'NEG3 = ("not append-only", "not append only", "no longer append", "never append-only")', "NEG3 = ()"),
    ("M02-negw-window2", "NEGW negation window 3 -> 2 words", "{0,3}?", "{0,2}?"),
    ("M03-negw-window6", "NEGW negation window 3 -> 6 words", "{0,3}?", "{0,6}?"),
    ("M04-negw-drop-nor", "NEGW drops 'nor' from the negator alternation", "no|nor|neither", "no|neither"),
    ("M05-negw-drop-non", "NEGW drops 'non' from the negator alternation", "non|isn't", "isn't"),
    ("M06-negw-hyphen-only", "NEGW 'append[- ]only' -> 'append-only' (space variant lost)", '[\\s\\-]+append[- ]only")', '[\\s\\-]+append-only")'),
    ("M07-says-drop-negw", "says() no longer consults NEGW", "and not any(n in low for n in NEG3) \\\n        and not NEGW.search(low)", "and not any(n in low for n in NEG3)"),
    # --- token() / word regex / wild detection / self-declaration ----------
    ("M08-token-wild-base", "wildcard token uses base name not parent dir", 'return parts[-2] if len(parts) > 1 else ""', "return parts[-1]"),
    ("M09-token-keep-ext", "token() keeps the extension", 'return base.rsplit(".", 1)[0] if "." in base else base', "return base"),
    ("M10-word-lookahead", "word regex lookahead [a-z0-9_] -> [a-z]", 're.escape(tok) + r"(?![a-z0-9_])"', 're.escape(tok) + r"(?![a-z])"'),
    ("M11-self-wild-bind", "self-declaration binds even under a wildcard row", "if not wild and fnmatch.fnmatchcase(decl_path, pattern):", "if fnmatch.fnmatchcase(decl_path, pattern):"),
    ("M12-wild-const-false", "wild detection disabled (wild=False)", 'wild = any(ch in pattern for ch in "*?[")', "wild = False"),
    ("M13-wild-star-only", "wild detection sees only '*'", 'wild = any(ch in pattern for ch in "*?[")', 'wild = any(ch in pattern for ch in "*")'),
    # --- counter's own lane-leg sections/origins/native --------------------
    ("M14-sections-hash1", "sections() keys on '# ' not '## '", 'if ln.startswith(b"## "):', 'if ln.startswith(b"# "):'),
    ("M15-origin-all", "origin membership any-title -> all-titles", "if psec[pos - 1] in ex and org.get(text, set()) & ex", "if psec[pos - 1] in ex and ex <= org.get(text, set())"),
    ("M16-native-ge", "native overshoot check > -> >=", 'if e["ungraded"] > native:', 'if e["ungraded"] >= native:'),
    ("M17-events-ge6", "lane events threshold >=5 -> >=6", 'len(j.get("events") or []) >= 5', 'len(j.get("events") or []) >= 6'),
    ("M18-events-gt5", "lane events threshold >=5 -> >5", 'len(j.get("events") or []) >= 5', 'len(j.get("events") or []) > 5'),
    ("M19-lane-exit-le0", "lane tool exit ==0 -> <=0", 'ok = p.returncode == 0 and s.get("bad_declarations") == 0', 'ok = p.returncode <= 0 and s.get("bad_declarations") == 0'),
    ("M20-drop-baddecl", "lane bad_declarations==0 clause removed", ' and s.get("bad_declarations") == 0 and len(j.get("events") or []) >= 5', ' and len(j.get("events") or []) >= 5'),
    ("M21-scenarios-7", "fl requires 7/8 scenarios not 8/8", "fl = len(res) == 8 and all(res)", "fl = len(res) == 7 and all(res)"),
    ("M22-met-or", "met = fl and ll -> fl or ll", "met = fl and ll", "met = fl or ll"),
    ("M23-launder-exit0", "launder want_exit 1 -> 0", 'check("launder", code, j, 1, (c3,', 'check("launder", code, j, 0, (c3,'),
    ("M24-launder-graded", "launder want graded 25 -> 24", '{"deleted": 25, "graded": 25, "ungraded": 0, "status": "unrestored"}', '{"deleted": 25, "graded": 24, "ungraded": 0, "status": "unrestored"}'),
    ("M25-nativehead-ungraded", "native-head want ungraded 25 -> 24", '{"deleted": 25, "graded": 0, "ungraded": 25, "status": "ungraded"}', '{"deleted": 25, "graded": 0, "ungraded": 24, "status": "ungraded"}'),
    ("M26-datedloss-exit", "dated-loss want_exit 1 -> 0", 'check("dated-loss", code, j, 1, (c2,', 'check("dated-loss", code, j, 0, (c2,'),
    ("M27-substring-exit", "substring want_exit 1 -> 0", f'{LAUNDER_ROW}", 1, 1),', f'{LAUNDER_ROW}", 0, 1),'),
    ("M28-wordtoken-exit", "word-token want_exit 0 -> 1", f'{LAUNDER_ROW}", 0, 0),', f'{LAUNDER_ROW}", 1, 0),'),
    ("M29-negated-exit", "negated want_exit 1 -> 0", f'{SCORE_ROW}", 1, 1),', f'{SCORE_ROW}", 0, 1),'),
    ("M30-wildself-exit", "wildcard-self want_exit 1 -> 0", f'{WSELF_ROW}", 1, 1),', f'{WSELF_ROW}", 0, 1),'),
    ("M31-wildnamed-exit", "wildcard-named want_exit 0 -> 1", f'{WNAMED_ROW}", 0, 0)):', f'{WNAMED_ROW}", 1, 0)):'),
    ("M32-wildself-bad", "wildcard-self want bad_declarations 1 -> 0", f'{WSELF_ROW}", 1, 1),', f'{WSELF_ROW}", 1, 0),'),
    # --- run_tool / plumbing ----------------------------------------------
    ("M33-runtool-path", "run_tool contract path drops the scenario name", 'f"{name}.contract.tsv"', '"contract.tsv"'),
    ("M34-runtool-flag", "run_tool passes --contract-typo", '"--contract", cpath', '"--contract-typo", cpath'),
    ("M35-exit-always-0", "exit code always 0", "return 0 if met else 1", "return 0"),
    ("M36-exit-invert", "exit code inverted", "return 0 if met else 1", "return 1 if met else 0"),
    ("M37-archive-head", "tool archived from HEAD instead of --tip", 'git(a.repo, "archive", "--format=tar", tip)', 'git(a.repo, "archive", "--format=tar", "HEAD")'),
    ("M38-revlist-noreverse", "origin rev-list loses --reverse (first -> last appearance)", '"rev-list", "--topo-order", "--reverse", "--parents", tip', '"rev-list", "--topo-order", "--parents", tip'),
    ("M39-region-relax", "exempt region regex loosened ([^@:]+:\\d+ -> [^@:]*:\\d*)", 're.fullmatch(r"exempt=(.+)@[^@:]+:\\d+", region)', 're.fullmatch(r"exempt=(.+)@[^@:]*:\\d*", region)'),
    ("M40-region-never", "exempt region regex never matches", 're.fullmatch(r"exempt=(.+)@[^@:]+:\\d+", region)', 're.fullmatch(r"exempt=(.+?)@", region)'),
    ("M41-titles-split", "multi-title split '|' -> whitespace", 'm.group(1).split("|")', "m.group(1).split()"),
    ("M42-ex-fnmatch-eq", "exempt-row file match fnmatch -> equality", 'if fnmatch.fnmatchcase(f or "", pat):', "if f == pat:"),
    ("M43-diff-U3", "deleted_with_pos runs with -U3 instead of -U0", '"-U0", "--text"', '"-U3", "--text"'),
    ("M44-header-row", "parse_contract includes the header row", 'for ln in text.split("\\n")[1:]:', 'for ln in text.split("\\n"):'),
    # --- Fx fixture class ---------------------------------------------------
    ("M45-fx-no-trailing-nl", "Fx.commit writes without trailing newline", 'fh.write("".join(x + "\\n" for x in body))', 'fh.write("\\n".join(body))'),
    ("M46-ident-name", "fixture commit identity renamed", "user.name=r49c2-fixture", "user.name=r49c2"),
    ("M47-toplevel-guard", "fixture toplevel guard disabled", "if os.path.realpath(top) != os.path.realpath(self.d):", "if False:"),
    # --- origins first-appearance ------------------------------------------
    ("M48-origins-lastwins", "origins() keeps the LAST section holding the text", """            fresh = collections.defaultdict(set)
            for ln, t in zip(body, sections(body)):
                if ln not in orig:
                    fresh[ln].add(t)
            orig.update(fresh)""", """            for ln, t in zip(body, sections(body)):
                orig[ln] = {t}"""),
    ("M49-negw-apos", "NEGW middle-word class drops apostrophes", "[\\w'’]+", "[\\w]+"),
]


def main():
    man = []
    for name, desc, old, new in MUTANTS:
        n = SRC.count(old)
        assert n == 1, f"{name}: {n} occurrences of {old!r}"
        out = SRC.replace(old, new, 1)
        path = os.path.join(HERE, "mut", name + ".py")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write(out)
        man.append({"name": name, "desc": desc, "old": old, "new": new})
    with open(os.path.join(HERE, "mut", "manifest.json"), "w") as fh:
        json.dump(man, fh, indent=1)
    print(f"{len(man)} mutants written")


if __name__ == "__main__":
    main()
