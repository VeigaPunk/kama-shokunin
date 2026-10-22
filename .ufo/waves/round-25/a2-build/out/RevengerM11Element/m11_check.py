#!/usr/bin/env python3
"""RevengerM11Element (kama round 25, attempt 2): element check for mutant M11.

Reads only the pinned clone at 1fc41e3 and git-history snapshots under SCRATCH
(each made with `git show <sha>:<path>`). Parses with ast and tokenize; runs no
auditor code and starts no server. Writes the mutated auditor copy under
SCRATCH/mut/ and the check result under OUT. Run with PYTHONDONTWRITEBYTECODE=1.
"""
import ast
import copy
import hashlib
import io
import json
import tokenize
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r25a2/RevengerM11Element/clone")
SCRATCH = Path("/fast/scratch/hyaku/kama-r25a2/RevengerM11Element")
OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/RevengerM11Element")
AUDIT = CLONE / "tools/report-landing-audit.py"
REGISTRY = CLONE / "tests/report-audit/isolation-mutants.py"

# auditor snapshots, oldest first (git log --reverse order)
HIST = ["a29bb84", "1471344", "7054dba", "6c9f58c", "80a6d07",
        "e0f0434", "34b2376", "e876b95", "ed1cc3a", "92063cf"]
# commits that must carry the same listing element (round 23 on, through 1fc41e3)
ELEMENT_COMMITS = ["e0f0434", "e876b95", "ed1cc3a", "92063cf"]
SKIP = {tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT,
        tokenize.COMMENT, tokenize.ENDMARKER}
REMOVED = [(tokenize.OP, ","), (tokenize.NAME, "errors"), (tokenize.OP, "="),
           (tokenize.STRING, '"surrogateescape"')]


def mutants_of(path):
    """The MUTANTS literal of a mutant file, read by parsing (never executed)."""
    tree = ast.parse(path.read_bytes(), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "MUTANTS" for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit(f"no MUTANTS literal in {path}")


def m11_of(mutants):
    hits = [t for t in mutants if t[0].startswith("M11-")]
    assert len(hits) == 1, hits
    return hits[0]


def listing_calls(tree):
    """git(...) calls whose literal arguments name both 'ls-tree' and '.ufo/reports'."""
    found = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "git"):
            consts = {a.value for a in node.args if isinstance(a, ast.Constant)}
            if {"ls-tree", ".ufo/reports"} <= consts:
                found.append(node)
    return found


def parent_map(tree):
    pm = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            pm[child] = node
    return pm


def context(node, pm):
    """Innermost enclosing function name, and whether the node sits in a try body."""
    fn, in_try, child, cur = None, False, node, pm.get(node)
    while cur is not None:
        if isinstance(cur, ast.Try) and any(child is s for s in cur.body):
            in_try = True
        if fn is None and isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fn = cur.name
        child, cur = cur, pm.get(cur)
    return fn, in_try


def tokens(text):
    out = []
    for tok in tokenize.generate_tokens(io.StringIO(text).readline):
        if tok.type not in SKIP:
            out.append((tok.type, tok.string, tok.start[0]))
    return out


def without_errors_kw(tree, lineno):
    """Copy of tree with the errors= keyword removed from the git call on lineno."""
    clone = copy.deepcopy(tree)
    hits = [n for n in ast.walk(clone) if isinstance(n, ast.Call)
            and n.lineno == lineno and isinstance(n.func, ast.Name)
            and n.func.id == "git"]
    assert len(hits) == 1, len(hits)
    hits[0].keywords = [k for k in hits[0].keywords if k.arg != "errors"]
    return clone


def sha12(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def main():
    orig_bytes = AUDIT.read_bytes()
    src = orig_bytes.decode("utf-8")
    checks, observed = {}, {}

    mid, anchor_now, replacement = m11_of(mutants_of(REGISTRY))
    anchors = {sha: m11_of(mutants_of(SCRATCH / f"mut-hist/mutants-{sha}.py"))
               for sha in ("e0f0434", "e876b95", "34b2376", "92063cf")}
    anchor_r23 = anchors["e876b95"][1]
    checks["round23_anchor_and_replacement_identical_in_snapshots"] = all(
        (a[1], a[2]) == (anchor_r23, replacement) for a in anchors.values())
    observed.update(M11_id=mid, anchor_now=anchor_now,
                    anchor_r23=anchor_r23, replacement=replacement)

    n_now = src.count(anchor_now)
    checks["anchor_now_count_in_1fc41e3"] = n_now
    assert n_now == 1, n_now
    mutated = src.replace(anchor_now, replacement, 1)
    mut_dir = SCRATCH / "mut"
    mut_dir.mkdir(parents=True, exist_ok=True)
    (mut_dir / "report-landing-audit.1fc41e3.py").write_bytes(orig_bytes)
    (mut_dir / "report-landing-audit.M11.py").write_bytes(mutated.encode("utf-8"))

    compiled = {}
    for label, text in (("original", src), ("mutated", mutated)):
        try:
            compile(text, f"<{label}>", "exec", dont_inherit=True)
            compiled[label] = "OK"
        except SyntaxError as exc:
            compiled[label] = f"SyntaxError line {exc.lineno}: {exc.msg}"
    checks["compile"] = compiled

    ot, mt = tokens(src), tokens(mutated)
    hits = [i for i in range(len(ot) - 3)
            if ot[i][:3] == (tokenize.OP, ",", 682)
            and ot[i + 1][:3] == (tokenize.NAME, "errors", 683)
            and ot[i + 2][:2] == (tokenize.OP, "=")
            and ot[i + 3][:2] == (tokenize.STRING, '"surrogateescape"')]
    checks["token_hits_for_removed_kwarg_on_lines_682_683"] = len(hits)
    assert len(hits) == 1, hits
    i = hits[0]
    removed = [t[:2] for t in ot[i:i + 4]]
    checks["removed_tokens"] = [list(t) for t in removed]
    checks["token_stream_equals_original_minus_removed"] = (
        [t[:2] for t in ot[:i] + ot[i + 4:]] == [t[:2] for t in mt])

    to, tm = ast.parse(src), ast.parse(mutated)
    calls = listing_calls(to)
    assert len(calls) == 1, len(calls)
    call = calls[0]
    checks["listing_call_lines_at_1fc41e3"] = [call.lineno, call.end_lineno]
    checks["listing_call_keywords_at_1fc41e3"] = [
        [k.arg, ast.unparse(k.value)] for k in call.keywords]
    checks["ast_equal_after_dropping_listing_errors_kw"] = (
        ast.dump(without_errors_kw(to, call.lineno)) == ast.dump(tm))
    checks["errors_keyword_count"] = {
        "original": sum(1 for n in ast.walk(to) if isinstance(n, ast.keyword) and n.arg == "errors"),
        "mutated": sum(1 for n in ast.walk(tm) if isinstance(n, ast.keyword) and n.arg == "errors")}

    history = {}
    for sha in HIST:
        raw = (SCRATCH / f"hist/audit-{sha}.py").read_bytes()
        text = raw.decode("utf-8")
        tree = ast.parse(raw)
        pm = parent_map(tree)
        rows = []
        for node in listing_calls(tree):
            fn, in_try = context(node, pm)
            err = [k for k in node.keywords if k.arg == "errors"]
            rows.append({
                "lines": [node.lineno, node.end_lineno],
                "function": fn,
                "in_try": in_try,
                "errors_value": (err[0].value.value if err and isinstance(err[0].value, ast.Constant) else None),
                "call_sha12": sha12(ast.dump(node)),
            })
        history[sha] = {
            "file_sha12": sha12(text),
            "anchor_r23_count": text.count(anchor_r23),
            "anchor_now_count": text.count(anchor_now),
            "listing_calls": rows,
        }
    checks["history"] = history

    now_fn, now_in_try = context(call, parent_map(to))
    now_sha = sha12(ast.dump(call))
    checks["listing_call_at_1fc41e3"] = {
        "lines": [call.lineno, call.end_lineno], "function": now_fn,
        "in_try": now_in_try, "call_sha12": now_sha}

    element = {
        "kwarg_present_in_each_element_commit": all(
            len(history[s]["listing_calls"]) == 1
            and history[s]["listing_calls"][0]["errors_value"] == "surrogateescape"
            for s in ELEMENT_COMMITS),
        "same_call_ast_round23_to_1fc41e3": all(
            history[s]["listing_calls"][0]["call_sha12"] == now_sha
            for s in ELEMENT_COMMITS),
        "same_enclosing_function": all(
            history[s]["listing_calls"][0]["function"] == now_fn
            for s in ELEMENT_COMMITS),
        "round23_anchor_matches_once_then_zero_at_92063cf": (
            all(history[s]["anchor_r23_count"] == 1
                for s in ("e0f0434", "e876b95", "ed1cc3a"))
            and history["92063cf"]["anchor_r23_count"] == 0),
        "now_anchor_matches_once_only_from_92063cf": (
            history["92063cf"]["anchor_now_count"] == 1
            and all(history[s]["anchor_now_count"] == 0
                    for s in HIST if s != "92063cf")),
        "auditor_1fc41e3_bytes_equal_92063cf_snapshot": (
            orig_bytes == (SCRATCH / "hist/audit-92063cf.py").read_bytes()),
    }
    mutation = {
        "compile_both_ok": compiled["original"] == "OK" and compiled["mutated"] == "OK",
        "removed_tokens_are_kwarg_and_separator": removed == REMOVED,
        "token_stream_equals_original_minus_removed":
            checks["token_stream_equals_original_minus_removed"],
        "ast_equal_after_dropping_listing_errors_kw":
            checks["ast_equal_after_dropping_listing_errors_kw"],
        "mutated_listing_call_has_no_errors_kw":
            checks["errors_keyword_count"]["original"]
            - checks["errors_keyword_count"]["mutated"] == 1,
    }
    checks["element_checks"] = element
    checks["mutation_checks"] = mutation
    verdict = ("SAME ELEMENT" if all(element.values()) and all(mutation.values())
               else "DIVERGES")
    result = {"verdict": verdict, "observed": observed, "checks": checks}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "M11-check-result.json").write_text(
        json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, default=str))
    return 0 if verdict == "SAME ELEMENT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
