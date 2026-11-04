#!/usr/bin/env python3
"""round72-receipt-tip-binding.py — bind every round-cited receipt to its revision.

Round-71's spot-check (§8 item 4) described ``measured/after/pre-report-at-tip.out``
as running "at the report tip" while the receipt header names ``4b284653``, two
commits before the measured tip; the lesson's "the only commits after it add
receipts" was a hand-written invariance argument no command checked. This tool
makes the binding mechanical: every receipt path the round's self-record cites
must exist at the tip, carry a ``# tip=<40-hex>`` / ``# rev=<40-hex>`` header,
name a revision that is an ancestor of the tip, and every commit in
``<rev>..<tip>`` must touch only the round's declared record paths.

    RECEIPT_TIP_FINDING <unbound|shifted|stale> <path> :: <detail>
    RECEIPT_TIP_BINDING round=<N> cited=<c> bound=<b> unbound=<u> shifted=<s> stale=<t>

The finding line's head is the frozen shape; the ``::`` suffix carries the detail
that names what moved -- the offending path and commit for ``shifted``, the
missing header or the absent path for ``unbound``/``stale``.

Exit map (pinned):
  0  every cited receipt is bound: cited == bound and unbound+shifted+stale == 0
  1  at least one finding; every finding is printed
  2  could-not-evaluate: CLI misuse, an unreadable self-record, a cited path that
     is not a receipt file, or a round whose self-record cites no receipt at all
     (never a silent 0 -- S052: a check that collected nothing cannot pass)

Population sources, both read as blobs at ``--tip`` (never the worktree, never the
index): ``SCORECARD.md``'s ``## Round <N>`` section (that heading to the next
``## `` heading) and the whole of ``corpus/lessons/round-<N>.md``. A missing
self-record file, a missing round section, or a round section that cites no
receipt is exit 2: the population the claim talks about cannot be read, and an
empty population would make every later line vacuously true (the control this
round replaces accepted exactly that).

Citation notations resolved mechanically (declared, so a reader can re-derive
each expansion by hand):
  * full paths, ``.ufo/waves/round-<N>/...``;
  * section-relative paths -- ``measured/...``, ``w1/...``, ``controls/...`` --
    resolved against ``.ufo/waves/round-<N>/`` when their first component is not
    a repo-root entry. This is the notation the round-71 record actually uses
    for the motivating receipt, so a binding that ignored it would be blind to
    the defect it exists to catch;
  * brace alternatives ``{a,b}``: every alternative is a separate cited path
    (a missing one is ``stale``, not an unexpandable token);
  * a ``*``/``?``/``[...]`` glob: matched by name against the tip's tree; no
    match means the literal pattern is the cited path, so it reads ``stale``;
  * a cited directory (trailing ``/`` or a tree at the tip) denotes the receipt
    files beneath it at the tip; a directory carrying none is exit 2.
Out of scope (not this round's receipts, never a finding): tokens carrying
whitespace, ``<``, ``>``, ``$``, quotes or ``...`` (commands and templates);
``.ufo/`` paths naming another round or a non-wave path; repo-relative paths
whose first component is a repo-root entry (``tools/``, ``corpus/``,
``plans/``, ...) -- those are instrument or record citations, not receipts; and
a section-relative token that neither carries a receipt extension nor exists at
the tip (a bare revision such as ``b43e71a8``, a prose token), because such a
token does not denote a file in the wave dir. A fully qualified
``.ufo/waves/round-<N>/...`` token is never filtered: it is classified strictly,
so an absent or non-receipt qualified citation is exit 2, never a silent skip.

Header and class rules (one class per receipt, first match wins):
  1. ``git cat-file -e <tip>:<path>`` fails                                  -> stale
  2. no ``tip=``/``rev=`` 40-hex match among the first five lines             -> unbound
     (short revisions are not headers; two different revisions in the window
     are ``unbound`` -- conflicting headers, no header shopping)
  3. header revision is not a commit of this repository, or is not an ancestor
     of the tip                                                               -> shifted*
  4. some commit in ``<rev>..<tip>`` touches a path outside the record paths   -> shifted
  5. otherwise                                                                 -> bound
  (*the frozen kill rule of plans/round-72-claims.md §C2 classes a non-ancestor
  header as ``shifted``; the detail names the revision and says "not an
  ancestor of <tip>", so the finding reads the same either way.)

Record paths, default: ``.ufo/waves/round-<N>/``, ``corpus/lessons/``, ``LOG.md``,
``SCORECARD.md``, ``corpus/README.md``. ``--record-path`` REPLACES that list. A
spec ending in ``/`` is a prefix; ``**`` (crosses ``/``), ``*`` (does not),
``?`` and ``[...]`` make it a glob; anything else is an exact path. Instrument
inputs (``tools/``, ``SKILL.md``, ``PROVINCE.md``, ``corpus/SOURCES.md``,
``corpus/knowledge/``, ``registry/``, ``plans/``) are never record paths.

Read-only: ``rev-parse``, ``cat-file``, ``ls-tree``, ``merge-base``, ``rev-list``,
``diff-tree``. ``--selftest`` builds throwaway fixture repositories (own
``git init``, own throwaway identity, every call names ``-C <fixture>``) and
drives the same entry point the CLI uses; it reads and writes no lane path.

Usage:
    round72-receipt-tip-binding.py --repo . --round 72 --tip master [--json]
    round72-receipt-tip-binding.py --selftest [--work DIR]
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

PREDICATE = (
    "`python3 tools/round72-receipt-tip-binding.py --repo <lane> --round <N> --tip <rev>` "
    "prints one `RECEIPT_TIP_BINDING round=<N> cited=<c> bound=<b> unbound=<u> shifted=<s> "
    "stale=<t>` line and exits 0 only when every receipt path cited by the round's "
    "self-record (`SCORECARD.md`'s round-`<N>` section and `corpus/lessons/round-<N>.md`) "
    "exists at `<rev>`, carries a `# tip=<40-hex>` or `# rev=<40-hex>` header, names a "
    "revision that is an ancestor of `<rev>`, and every commit in `<rev>..<tip>` touches "
    "only declared record paths; it exits 1 naming each "
    "`RECEIPT_TIP_FINDING <unbound|shifted|stale> <path>`."
)

RECEIPT_EXTS = (".out", ".txt", ".log", ".json")
HEADER_WINDOW = 5
HEADER_RE = re.compile(r"(?:^|[^\w-])(?:#\s*)?(?:tip|rev)=([0-9a-fA-F]{40})(?![0-9a-fA-F])")
ROUND_HEADING_RE = re.compile(r"^##\s+Round[-\s]+#?(\d+)\b")
ANY_H2_RE = re.compile(r"^##\s")
TOKEN_RE = re.compile(r"`([^`\n]+)`")
BRACE_RE = re.compile(r"\{([^{}]*)\}")
GLOB_CHARS = re.compile(r"[*?\[]")
SKIP_CHARS = '<>$"\'\\|`'
TIMEOUT = 300


class CouldNotEvaluate(Exception):
    """Fail-closed condition; maps to exit 2."""


# --------------------------------------------------------------------- git


def _git(repo, *args, check=True):
    proc = subprocess.run(
        ["git", "-C", repo, *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=TIMEOUT,
    )
    if check and proc.returncode != 0:
        raise CouldNotEvaluate(
            "git {} failed (rc={}): {}".format(
                " ".join(args[:2]),
                proc.returncode,
                proc.stderr.decode("utf-8", "replace").strip(),
            )
        )
    return proc


def _text(proc):
    return proc.stdout.decode("utf-8", "replace")


def _commit_sha(repo, rev):
    proc = _git(repo, "rev-parse", "--verify", "--quiet", rev + "^{commit}", check=False)
    if proc.returncode != 0:
        return None
    return _text(proc).strip()


def _blob(repo, rev, path):
    """Blob bytes at rev:path, or None when the path is absent (cat-file -e)."""
    probe = _git(repo, "cat-file", "-e", "{}:{}".format(rev, path), check=False)
    if probe.returncode != 0:
        return None
    return _git(repo, "cat-file", "blob", "{}:{}".format(rev, path)).stdout


def _obj_type(repo, rev, path):
    proc = _git(repo, "cat-file", "-t", "{}:{}".format(rev, path), check=False)
    if proc.returncode != 0:
        return None
    return _text(proc).strip()


def _tree_paths(repo, rev, dirpath):
    args = ["ls-tree", "-r", "--name-only", rev]
    if dirpath:
        args += ["--", dirpath.rstrip("/") + "/"]
    return [ln for ln in _text(_git(repo, *args)).splitlines() if ln.strip()]


def _is_ancestor(repo, rev, tip):
    return _git(repo, "merge-base", "--is-ancestor", rev, tip, check=False).returncode == 0


def _rev_list(repo, rev, tip):
    out = _text(_git(repo, "rev-list", "{}..{}".format(rev, tip)))
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def _diff_paths(repo, commit):
    out = _text(
        _git(
            repo,
            "diff-tree",
            "--no-commit-id",
            "--name-only",
            "--no-renames",
            "-r",
            "-m",
            commit,
        )
    )
    seen = []
    for line in out.splitlines():
        path = line.strip()
        if path and path not in seen:
            seen.append(path)
    return seen


# ------------------------------------------------------- paths and patterns


def default_record_paths(round_no):
    return [
        ".ufo/waves/round-{}/".format(round_no),
        "corpus/lessons/",
        "LOG.md",
        "SCORECARD.md",
        "corpus/README.md",
    ]


def _ext_of(path):
    return os.path.splitext(path.rsplit("/", 1)[-1])[1].lower()


def is_receipt(path):
    return _ext_of(path) in RECEIPT_EXTS


def _glob_re(pattern):
    out = []
    i = 0
    while i < len(pattern):
        ch = pattern[i]
        if ch == "*":
            if pattern[i:i + 2] == "**":
                out.append(".*")
                i += 2
            else:
                out.append("[^/]*")
                i += 1
        elif ch == "?":
            out.append("[^/]")
            i += 1
        elif ch == "[":
            close = pattern.find("]", i + 1)
            if close == -1:
                out.append(re.escape(ch))
                i += 1
            else:
                inner = pattern[i + 1:close]
                if inner.startswith("!"):
                    inner = "^" + inner[1:]
                out.append("[" + inner + "]")
                i = close + 1
        else:
            out.append(re.escape(ch))
            i += 1
    return re.compile("(?s)\\A" + "".join(out) + "\\Z")


def _record_match(path, specs):
    for spec in specs:
        if spec.endswith("/"):
            if path == spec[:-1] or path.startswith(spec):
                return True
        elif GLOB_CHARS.search(spec):
            if _glob_re(spec).match(path):
                return True
        elif path == spec:
            return True
    return False


def _brace_expand(path):
    alts = [path]
    for _ in range(8):
        nxt = []
        grew = False
        for cand in alts:
            match = BRACE_RE.search(cand)
            if not match:
                nxt.append(cand)
                continue
            grew = True
            for alt in match.group(1).split(","):
                nxt.append(cand[:match.start()] + alt.strip() + cand[match.end():])
        alts = nxt
        if not grew:
            break
    return alts


def _glob_hits(repo, tip, pattern):
    first = GLOB_CHARS.search(pattern)
    prefix = pattern[:first.start()]
    parent = prefix.rsplit("/", 1)[0] if "/" in prefix else ""
    matcher = _glob_re(pattern)
    return sorted(p for p in _tree_paths(repo, tip, parent) if matcher.match(p))


def _expand_one(repo, tip, cand, dir_hint, where):
    if GLOB_CHARS.search(cand):
        hits = _glob_hits(repo, tip, cand)
        if not hits:
            return [cand]
        out = []
        for hit in hits:
            out.extend(_expand_one(repo, tip, hit, False, where))
        return out
    if dir_hint or _obj_type(repo, tip, cand) == "tree":
        receipts = [p for p in _tree_paths(repo, tip, cand) if is_receipt(p)]
        if not receipts:
            raise CouldNotEvaluate(
                "cited directory carries no receipt file: {} ({})".format(cand, where)
            )
        return receipts
    if not is_receipt(cand):
        raise CouldNotEvaluate(
            "cited path is not a receipt file ({}): {} ({})".format(
                _ext_of(cand) or "no extension", cand, where
            )
        )
    return [cand]


def _in_scope(repo, tip, cand):
    """True when a section-relative candidate denotes something in the wave dir.

    A receipt extension claims the path even when it is absent (an uncommitted
    citation is the ``stale`` class); anything else must exist at the tip, so a
    bare revision (``b43e71a8``) or a prose token without a receipt suffix is
    not mistaken for a receipt citation. A fully qualified
    ``.ufo/waves/round-<N>/...`` token skips this test: it is unambiguous and
    classified strictly.
    """
    if GLOB_CHARS.search(cand):
        return is_receipt(cand)
    return is_receipt(cand) or _obj_type(repo, tip, cand) is not None


def _resolve_citation(repo, tip, round_no, token, where):
    """Receipt paths the token cites, or None when the token is out of scope."""
    tok = token.strip()
    while tok.startswith("./"):
        tok = tok[2:]
    tok = tok.rstrip(",;:")
    if not tok or re.search(r"\s", tok) or "..." in tok:
        return None
    if any(ch in tok for ch in SKIP_CHARS) or "<" in tok or ">" in tok or "$" in tok:
        return None
    base = ".ufo/waves/round-{}/".format(round_no)
    if tok == base.rstrip("/"):
        rel = ""
        qualified = True
    elif tok.startswith(base):
        rel = tok[len(base):]
        qualified = True
    elif tok.startswith(".ufo/"):
        return None
    else:
        head = tok.split("/", 1)[0]
        if head and _obj_type(repo, tip, head) is not None:
            return None
        rel = tok
        qualified = False
    full = base + rel
    root = full.rstrip("/")
    if not root:
        raise CouldNotEvaluate("empty citation at {}".format(where))
    dir_hint = full.endswith("/")
    out = []
    for cand in _brace_expand(root):
        if not qualified and not _in_scope(repo, tip, cand):
            continue
        out.extend(_expand_one(repo, tip, cand, dir_hint, where))
    return out


# ------------------------------------------------------------- self-record


def _round_section(text, round_no):
    """(lines, offset) of the `## Round <N>` section, or None."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        match = ROUND_HEADING_RE.match(line)
        if match and int(match.group(1)) == round_no:
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if ANY_H2_RE.match(lines[j]):
            end = j
            break
    return lines[start:end], start


def _citations(lines, offset, filename):
    for i, line in enumerate(lines):
        for match in TOKEN_RE.finditer(line):
            yield match.group(1).strip(), filename, offset + i + 1


# ---------------------------------------------------------------- grading


def _header_rev(blob):
    """(rev, problem): rev is None with a problem string, or a 40-hex revision."""
    window = blob.decode("utf-8", "replace").splitlines()[:HEADER_WINDOW]
    revs = []
    for line in window:
        for match in HEADER_RE.finditer(line):
            revs.append(match.group(1).lower())
    if not revs:
        return None, "no tip=/rev= header among the first {} lines".format(HEADER_WINDOW)
    if len(set(revs)) > 1:
        return None, "conflicting header revisions: {}".format(",".join(sorted(set(revs))))
    return revs[0], ""


def _evaluate(repo, tip, path, specs):
    blob = _blob(repo, tip, path)
    if blob is None:
        return "stale", "absent at {}".format(tip)
    rev, problem = _header_rev(blob)
    if rev is None:
        return "unbound", problem
    if _commit_sha(repo, rev) is None:
        return "shifted", "header rev {} is not a commit in this repository".format(rev)
    if not _is_ancestor(repo, rev, tip):
        return "shifted", "header rev {} is not an ancestor of {}".format(rev[:12], tip[:12])
    for commit in _rev_list(repo, rev, tip):
        for changed in _diff_paths(repo, commit):
            if not _record_match(changed, specs):
                return "shifted", "{} touched by {}".format(changed, commit[:12])
    return "bound", "rev={}".format(rev)


def summary_line(result):
    return (
        "RECEIPT_TIP_BINDING round={} cited={} bound={} unbound={} shifted={} stale={}".format(
            result["round"],
            result["cited"],
            result["bound"],
            result["unbound"],
            result["shifted"],
            result["stale"],
        )
    )


def audit(repo, tip, round_no, record_specs):
    repo = os.path.abspath(repo)
    if _git(repo, "rev-parse", "--show-toplevel", check=False).returncode != 0:
        raise CouldNotEvaluate("{} is not a git repository".format(repo))
    tip_sha = _commit_sha(repo, tip)
    if tip_sha is None:
        raise CouldNotEvaluate("tip {} is not a commit in {}".format(tip, repo))

    scorecard_path = "SCORECARD.md"
    scorecard = _blob(repo, tip_sha, scorecard_path)
    if scorecard is None:
        raise CouldNotEvaluate("{} is missing at {}".format(scorecard_path, tip))
    section = _round_section(scorecard.decode("utf-8", "replace"), round_no)
    if section is None:
        raise CouldNotEvaluate(
            "{} at {} carries no '## Round {}' section; the round's self-record "
            "cannot be read".format(scorecard_path, tip, round_no)
        )

    lesson_path = "corpus/lessons/round-{}.md".format(round_no)
    lesson = _blob(repo, tip_sha, lesson_path)
    if lesson is None:
        raise CouldNotEvaluate("{} is missing at {}".format(lesson_path, tip))

    lines, offset = section
    cites = list(_citations(lines, offset, scorecard_path))
    cites += list(_citations(lesson.decode("utf-8", "replace").splitlines(), 0, lesson_path))

    cited_by = {}
    for token, filename, lineno in cites:
        where = "{}:{}".format(filename, lineno)
        for path in _resolve_citation(repo, tip_sha, round_no, token, where) or []:
            cited_by.setdefault(path, {"token": token, "where": where})
    if not cited_by:
        raise CouldNotEvaluate(
            "the round-{} self-record cites no receipt path; nothing to bind".format(round_no)
        )

    counts = {"unbound": 0, "shifted": 0, "stale": 0}
    findings = []
    for path in sorted(cited_by):
        cls, detail = _evaluate(repo, tip_sha, path, record_specs)
        if cls != "bound":
            counts[cls] += 1
            findings.append(
                {"class": cls, "path": path, "detail": detail, "cited": cited_by[path]}
            )

    cited = len(cited_by)
    result = {
        "round": round_no,
        "tip": tip,
        "tip_commit": tip_sha,
        "repo": repo,
        "record_paths": list(record_specs),
        "cited": cited,
        "bound": cited - sum(counts.values()),
        "unbound": counts["unbound"],
        "shifted": counts["shifted"],
        "stale": counts["stale"],
        "findings": findings,
    }
    result["line"] = summary_line(result)
    clean = cited == result["bound"] and sum(counts.values()) == 0
    result["exit"] = 0 if clean else 1
    return result


def render(result):
    lines = []
    for item in result["findings"]:
        line = "RECEIPT_TIP_FINDING {} {}".format(item["class"], item["path"])
        if item["detail"]:
            line += " :: " + item["detail"]
        lines.append(line)
    lines.append(result["line"])
    return "\n".join(lines)


# ---------------------------------------------------------------- selftest


class _Fixture:
    """Throwaway repository; every git call names ``-C <path>``."""

    def __init__(self, root, name):
        self.path = os.path.join(root, name)
        os.makedirs(self.path, exist_ok=True)
        _git(self.path, "init", "-q")
        top = _text(_git(self.path, "rev-parse", "--show-toplevel")).strip()
        if os.path.realpath(top) != os.path.realpath(self.path):
            raise CouldNotEvaluate(
                "fixture {} is not its own git root ({})".format(self.path, top)
            )

    def write(self, relpath, text):
        full = os.path.join(self.path, *relpath.split("/"))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as fh:
            fh.write(text)

    def commit(self, message):
        _git(self.path, "add", "-A")
        _git(
            self.path,
            "-c", "user.name=fixture",
            "-c", "user.email=fixture@invalid",
            "-c", "commit.gpgsign=false",
            "-c", "core.autocrlf=false",
            "commit", "-q", "-m", message,
        )
        return _text(_git(self.path, "rev-parse", "HEAD")).strip()


def _run_cli(argv):
    out, err = io.StringIO(), io.StringIO()
    code = 2
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = main(argv)
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else 2
    return int(code), out.getvalue(), err.getvalue()


def _arm(outcomes, name, rc, out, err, expect_rc, must_out=(), must_err=()):
    ok = rc == expect_rc
    if ok:
        ok = all(s in out for s in must_out) and all(s in err for s in must_err)
    outcomes.append(
        {"name": name, "ok": ok, "rc": rc, "expect": expect_rc, "out": out, "err": err}
    )


RECEIPT = ".ufo/waves/round-72/measured/after/x.out"
SCORECARD_HEAD = "# Kama scorecard\n\n## Round 71 — previous round\n\nKind: n/a\n\n"


def _fixture_record(fixture, tip_line):
    fixture.write("corpus/lessons/round-72.md", "# Round 72 lesson\n\nNo citation here.\n")
    fixture.write(
        "SCORECARD.md",
        SCORECARD_HEAD + "## Round 72 — current round\n\n" + tip_line + "\n",
    )


def _selftest_arms(scratch, outcomes):
    # arm: the predicate sentence is one line carrying both output shapes
    wrapped = "\n" in PREDICATE
    _arm(
        outcomes,
        "predicate-one-line",
        1 if wrapped else 0,
        "PREDICATE wraps" if wrapped else PREDICATE,
        "",
        0,
        must_out=["RECEIPT_TIP_BINDING round=<N> cited=<c>", "RECEIPT_TIP_FINDING"],
    )

    # arm: bound and clean -> exit 0, both notations dedupe to one receipt
    fx = _Fixture(scratch, "clean")
    fx.write("tools/counter.py", "# counter\n")
    base = fx.commit("base with the instrument")
    fx.write(RECEIPT, "# tip={}\nRECEIPT bound\n".format(base))
    _fixture_record(fx, "Receipt: `{}`".format(RECEIPT))
    fx.write(
        "corpus/lessons/round-72.md",
        "# Round 72 lesson\n\nShorthand citation: `measured/after/x.out`\n",
    )
    tip = fx.commit("record plus receipt")
    rc, out, err = _run_cli(["--repo", fx.path, "--round", "72", "--tip", tip])
    _arm(
        outcomes, "clean", rc, out, err, 0,
        must_out=["RECEIPT_TIP_BINDING round=72 cited=1 bound=1 unbound=0 shifted=0 stale=0"],
    )

    # arm: receipt with no header -> unbound
    fx = _Fixture(scratch, "unbound")
    fx.write("tools/counter.py", "# counter\n")
    base = fx.commit("base")
    fx.write(RECEIPT, "RECEIPT without any header\n")
    _fixture_record(fx, "Receipt: `{}`".format(RECEIPT))
    tip = fx.commit("record")
    rc, out, err = _run_cli(["--repo", fx.path, "--round", "72", "--tip", tip])
    _arm(
        outcomes, "kill-unbound", rc, out, err, 1,
        must_out=[
            "RECEIPT_TIP_FINDING unbound " + RECEIPT,
            "RECEIPT_TIP_BINDING round=72 cited=1 bound=0 unbound=1 shifted=0 stale=0",
        ],
    )

    # arm: cited receipt absent at the tip -> stale
    fx = _Fixture(scratch, "stale")
    fx.write("tools/counter.py", "# counter\n")
    fx.commit("base")
    _fixture_record(fx, "Receipt: `{}`".format(RECEIPT))
    tip = fx.commit("record citing an absent receipt")
    rc, out, err = _run_cli(["--repo", fx.path, "--round", "72", "--tip", tip])
    _arm(
        outcomes, "kill-stale", rc, out, err, 1,
        must_out=[
            "RECEIPT_TIP_FINDING stale " + RECEIPT,
            "RECEIPT_TIP_BINDING round=72 cited=1 bound=0 unbound=0 shifted=0 stale=1",
        ],
    )

    # arm: header names an ancestor whose delta touches tools/ -> shifted
    fx = _Fixture(scratch, "shifted")
    fx.write("tools/counter.py", "v1\n")
    base = fx.commit("base")
    fx.write(RECEIPT, "# tip={}\nRECEIPT measured\n".format(base))
    _fixture_record(fx, "Receipt: `{}`".format(RECEIPT))
    fx.commit("record")
    fx.write("tools/counter.py", "v2\n")
    tip = fx.commit("instrument drift after the receipt")
    rc, out, err = _run_cli(["--repo", fx.path, "--round", "72", "--tip", tip])
    _arm(
        outcomes, "kill-shifted", rc, out, err, 1,
        must_out=[
            "RECEIPT_TIP_FINDING shifted " + RECEIPT,
            "RECEIPT_TIP_BINDING round=72 cited=1 bound=0 unbound=0 shifted=1 stale=0",
            "tools/counter.py",
            " touched by ",
        ],
    )
    rc, out, err = _run_cli(["--repo", fx.path, "--round", "72", "--tip", tip, "--json"])
    detail = ""
    try:
        detail = json.loads(out)["findings"][0]["detail"]
    except (ValueError, KeyError, IndexError):
        detail = "unparsed json: " + out.strip()[:200]
    _arm(
        outcomes, "kill-shifted-json-detail", rc, detail, "", 1,
        must_out=["tools/counter.py"],
    )

    # arm: a cited non-receipt path -> exit 2, naming it
    fx = _Fixture(scratch, "nonreceipt")
    fx.write("tools/counter.py", "# counter\n")
    fx.commit("base")
    fx.write(".ufo/waves/round-72/w1/notes.md", "# seat notes\n")
    _fixture_record(fx, "Notes: `.ufo/waves/round-72/w1/notes.md`")
    tip = fx.commit("record citing a non-receipt")
    rc, out, err = _run_cli(["--repo", fx.path, "--round", "72", "--tip", tip])
    _arm(
        outcomes, "cited-non-receipt", rc, out, err, 2,
        must_err=["is not a receipt file", ".ufo/waves/round-72/w1/notes.md"],
    )

    # arm: a qualified non-receipt citation that is absent -> exit 2, never skipped
    fx = _Fixture(scratch, "qualifiedabsent")
    fx.write("tools/counter.py", "# counter\n")
    fx.commit("base")
    _fixture_record(fx, "Notes: `.ufo/waves/round-72/w1/never-committed.md`")
    tip = fx.commit("record citing an absent non-receipt")
    rc, out, err = _run_cli(["--repo", fx.path, "--round", "72", "--tip", tip])
    _arm(
        outcomes, "qualified-absent-non-receipt", rc, out, err, 2,
        must_err=[".ufo/waves/round-72/w1/never-committed.md"],
    )

    # arm: a bare revision token is not a receipt citation (the round-71 false positive)
    fx = _Fixture(scratch, "barerev")
    fx.write("tools/counter.py", "# counter\n")
    base = fx.commit("base")
    fx.write(RECEIPT, "# tip={}\nRECEIPT bound\n".format(base))
    _fixture_record(fx, "Freeze commit `{}`, receipt: `{}`".format(base[:8], RECEIPT))
    tip = fx.commit("record naming a bare revision")
    rc, out, err = _run_cli(["--repo", fx.path, "--round", "72", "--tip", tip])
    _arm(
        outcomes, "bare-revision-token", rc, out, err, 0,
        must_out=["RECEIPT_TIP_BINDING round=72 cited=1 bound=1 unbound=0 shifted=0 stale=0"],
    )

    # arm: round section exists but cites no receipt -> exit 2
    fx = _Fixture(scratch, "empty")
    fx.write("tools/counter.py", "# counter\n")
    fx.commit("base")
    _fixture_record(fx, "Prose only, no receipt citation.")
    tip = fx.commit("record")
    rc, out, err = _run_cli(["--repo", fx.path, "--round", "72", "--tip", tip])
    _arm(
        outcomes, "empty-population", rc, out, err, 2,
        must_err=["cites no receipt path"],
    )

    # arm: no round section at the tip -> exit 2, never a silent 0
    fx = _Fixture(scratch, "nosection")
    fx.write("tools/counter.py", "# counter\n")
    fx.write("SCORECARD.md", SCORECARD_HEAD + "Kind: n/a\n")
    fx.write("corpus/lessons/round-72.md", "# Round 72 lesson\n")
    tip = fx.commit("scorecard without a round-72 section")
    rc, out, err = _run_cli(["--repo", fx.path, "--round", "72", "--tip", tip])
    _arm(
        outcomes, "missing-round-section", rc, out, err, 2,
        must_err=["carries no '## Round 72' section"],
    )

    # arm: brace alternatives plus a glob expand to three cited receipts
    fx = _Fixture(scratch, "expansion")
    fx.write("tools/counter.py", "# counter\n")
    base = fx.commit("base")
    header = "# tip={}\n".format(base)
    for name in ("a.out", "b.out", "kill-1.out"):
        fx.write(".ufo/waves/round-72/w1/EX01/{}".format(name), header + "fixture receipt\n")
    _fixture_record(
        fx,
        "Pair: `.ufo/waves/round-72/w1/EX01/{a.out,b.out}` and kills: `w1/EX01/kill-*.out`",
    )
    tip = fx.commit("record plus three receipts")
    rc, out, err = _run_cli(["--repo", fx.path, "--round", "72", "--tip", tip])
    _arm(
        outcomes, "brace-and-glob", rc, out, err, 0,
        must_out=["RECEIPT_TIP_BINDING round=72 cited=3 bound=3 unbound=0 shifted=0 stale=0"],
    )

    # arm: --record-path replaces the default list
    fx = _Fixture(scratch, "recordpath")
    fx.write("tools/counter.py", "v1\n")
    base = fx.commit("base")
    fx.write(RECEIPT, "# tip={}\nRECEIPT measured\n".format(base))
    _fixture_record(fx, "Receipt: `{}`".format(RECEIPT))
    fx.commit("record")
    fx.write("docs/note.txt", "a non-record path by default\n")
    tip = fx.commit("docs drift")
    rc, out, err = _run_cli(["--repo", fx.path, "--round", "72", "--tip", tip])
    default_shifted = rc == 1 and "RECEIPT_TIP_FINDING shifted " + RECEIPT in out
    rc, out, err = _run_cli(
        [
            "--repo", fx.path, "--round", "72", "--tip", tip,
            "--record-path", ".ufo/waves/round-72/",
            "--record-path", "corpus/lessons/",
            "--record-path", "SCORECARD.md",
            "--record-path", "docs/",
        ]
    )
    widened = rc == 0 and "cited=1 bound=1" in out
    _arm(
        outcomes,
        "record-path-replaces",
        0 if (default_shifted and widened) else 1,
        "default_shifted={} widened={}".format(default_shifted, widened),
        "",
        0,
        must_out=["default_shifted=True widened=True"],
    )

    # arm: a header naming a real but non-ancestor commit -> shifted (frozen kill rule)
    fx = _Fixture(scratch, "nonancestor")
    fx.write("tools/counter.py", "v1\n")
    base = fx.commit("base")
    tree = _text(_git(fx.path, "rev-parse", base + "^{tree}")).strip()
    side = _text(
        _git(
            fx.path,
            "-c", "user.name=fixture",
            "-c", "user.email=fixture@invalid",
            "commit-tree", tree, "-m", "divergent commit from the same tree",
        )
    ).strip()
    fx.write(RECEIPT, "# tip={}\nRECEIPT measured\n".format(side))
    _fixture_record(fx, "Receipt: `{}`".format(RECEIPT))
    tip = fx.commit("record citing a divergent header")
    rc, out, err = _run_cli(["--repo", fx.path, "--round", "72", "--tip", tip])
    _arm(
        outcomes, "non-ancestor-header", rc, out, err, 1,
        must_out=[
            "RECEIPT_TIP_FINDING shifted " + RECEIPT,
            "RECEIPT_TIP_BINDING round=72 cited=1 bound=0 unbound=0 shifted=1 stale=0",
        ],
    )

    # arm: --json carries the same counts and the exit code
    fx = _Fixture(scratch, "json")
    fx.write("tools/counter.py", "# counter\n")
    base = fx.commit("base")
    fx.write(RECEIPT, "# tip={}\nRECEIPT bound\n".format(base))
    _fixture_record(fx, "Receipt: `{}`".format(RECEIPT))
    tip = fx.commit("record")
    rc, out, err = _run_cli(["--repo", fx.path, "--round", "72", "--tip", tip, "--json"])
    doc_ok = False
    try:
        doc = json.loads(out)
        doc_ok = (
            doc["round"] == 72
            and doc["cited"] == 1
            and doc["bound"] == 1
            and doc["exit"] == 0
            and doc["line"].startswith("RECEIPT_TIP_BINDING round=72")
        )
    except (ValueError, KeyError):
        doc_ok = False
    _arm(
        outcomes, "json", rc, "doc_ok=True" if doc_ok else out, "", 0,
        must_out=["doc_ok=True"],
    )

    # arm: CLI misuse is exit 2 (missing --round, and --round 0)
    fx = _Fixture(scratch, "usage")
    fx.write("tools/counter.py", "# counter\n")
    tip = fx.commit("base")
    rc_missing, _, _ = _run_cli(["--repo", fx.path, "--tip", tip])
    rc_zero, _, _ = _run_cli(["--repo", fx.path, "--round", "0", "--tip", tip])
    _arm(
        outcomes,
        "cli-misuse",
        0 if (rc_missing == 2 and rc_zero == 2) else 1,
        "missing={} zero={}".format(rc_missing, rc_zero),
        "",
        0,
        must_out=["missing=2 zero=2"],
    )


def run_selftest(args):
    if args.work:
        root = os.path.abspath(args.work)
        os.makedirs(root, exist_ok=True)
        scratch = os.path.join(root, "selftest-{}".format(os.getpid()))
        os.makedirs(scratch, exist_ok=True)
    else:
        scratch = tempfile.mkdtemp(prefix="receipt-tip-binding-selftest-")
    outcomes = []
    try:
        _selftest_arms(scratch, outcomes)
    except (CouldNotEvaluate, OSError) as exc:
        outcomes.append(
            {
                "name": "fixture-build",
                "ok": False,
                "rc": 2,
                "expect": 0,
                "out": "",
                "err": str(exc),
            }
        )
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    for item in outcomes:
        print(
            "RECEIPT_TIP_BINDING_ARM {} expect={} got={} {}".format(
                item["name"], item["expect"], item["rc"], "ok" if item["ok"] else "FAIL"
            )
        )
        if not item["ok"]:
            for stream in ("out", "err"):
                text = item[stream].strip()
                for line in text.splitlines()[:20]:
                    print("    {}: {}".format(stream, line))
    passed = sum(1 for item in outcomes if item["ok"])
    failed = len(outcomes) - passed
    print("RECEIPT_TIP_BINDING_SELFTEST pass={} fail={}".format(passed, failed))
    return 1 if failed else 0


# -------------------------------------------------------------------- main


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="round72-receipt-tip-binding.py",
        description="Bind every receipt path a round's self-record cites to the revision it measured.",
    )
    ap.add_argument("--repo", default=".", help="repository to grade (default: .)")
    ap.add_argument("--round", dest="round_no", type=int, default=None, metavar="N",
                    help="round number whose self-record is read (required unless --selftest)")
    ap.add_argument("--tip", default="master",
                    help="revision the receipts are bound to (default: master)")
    ap.add_argument("--record-path", dest="record_paths", action="append", metavar="GLOB",
                    help="record path (repeatable; replaces the default list)")
    ap.add_argument("--work", default=None,
                    help="scratch directory for the selftest fixtures")
    ap.add_argument("--selftest", action="store_true", help="run the fixture selftest")
    ap.add_argument("--json", action="store_true",
                    help="print one JSON document instead of the text lines")
    args = ap.parse_args(argv)

    if args.selftest:
        return run_selftest(args)
    if args.round_no is None:
        ap.error("the following arguments are required: --round")
    if args.round_no < 1:
        ap.error("--round must be a positive integer")

    specs = list(args.record_paths) if args.record_paths else default_record_paths(args.round_no)
    try:
        result = audit(args.repo, args.tip, args.round_no, specs)
    except CouldNotEvaluate as exc:
        print("RECEIPT_TIP_BINDING_UNREADABLE {}".format(exc), file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=1, sort_keys=True))
    else:
        print(render(result))
    return result["exit"]


if __name__ == "__main__":
    sys.exit(main())
