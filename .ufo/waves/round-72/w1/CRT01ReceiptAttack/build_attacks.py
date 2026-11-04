#!/usr/bin/env python3
"""CRT01ReceiptAttack driver - attacks round-72 C2 (receipt-tip binding) on its landed bytes.

Every fixture is its own throwaway git repo under S.  No mutating git call is ever made outside
a fixture dir; every git invocation names -C <fixture> and the toplevel is asserted first.

    python3 build_attacks.py            # run every case, write results.json + results.txt
    python3 build_attacks.py B3 B4a     # run a subset
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

S = Path("/fast/scratch/hyaku/kama-r72/CRT01ReceiptAttack")
LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
TOOL = LANE / "tools/round72-receipt-tip-binding.py"
GITID = ["-c", "user.name=fixture", "-c", "user.email=fixture@invalid", "-c", "commit.gpgsign=false"]
HEADER40 = "# tip={rev}\n"


# ---------------------------------------------------------------- git plumbing (fixture-scoped)
def sh(argv, cwd=None):
    return subprocess.run(argv, cwd=None if cwd is None else str(cwd),
                          capture_output=True, text=True)


def git(d: Path, *args, check=True):
    r = sh(["git", "-C", str(d), *GITID, *args])
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} -> {r.returncode}\n{r.stdout}{r.stderr}")
    return r


def rev(d: Path) -> str:
    return git(d, "rev-parse", "HEAD").stdout.strip()


def init(name: str) -> Path:
    S.mkdir(parents=True, exist_ok=True)
    d = Path(tempfile.mkdtemp(dir=str(S), prefix=name + ".")).resolve()
    git(d, "init", "-q", "-b", "master")
    top = Path(git(d, "rev-parse", "--show-toplevel").stdout.strip()).resolve()
    assert top == d, f"toplevel {top} != fixture {d}"
    return d


def commit(d: Path, msg: str) -> str:
    git(d, "add", "-A")
    git(d, "commit", "-q", "-m", msg)
    return rev(d)


def append(d: Path, rel: str, text: str) -> None:
    p = d / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    prev = p.read_text(encoding="utf-8") if p.exists() else ""
    p.write_text(prev + text, encoding="utf-8")


def skeleton(d: Path, instrument="print('gate v1')\n") -> None:
    (d / "plans").mkdir(parents=True)
    (d / "plans/round-72-claims.md").write_text("# kama round 72 - frozen claims (fixture)\n", encoding="utf-8")
    (d / "tools").mkdir()
    (d / "tools/gate.py").write_text(instrument, encoding="utf-8")
    (d / "corpus/lessons").mkdir(parents=True)
    (d / "LOG.md").write_text("# kama log (fixture)\n", encoding="utf-8")
    (d / "SCORECARD.md").write_text(
        "# kama scorecard (fixture)\n\n## Round 72 - fixture round\n\nNo receipt cited yet.\n", encoding="utf-8")
    (d / "corpus/lessons/round-72.md").write_text(
        "# Round 72 lesson (fixture)\n\nNo receipt cited yet.\n", encoding="utf-8")
    commit(d, "fixture skeleton")


def receipt(d: Path, rel_under_wave: str, header_rev: str | None, body: str,
            header: str | None = None) -> Path:
    rel = Path(".ufo/waves/round-72") / rel_under_wave
    p = d / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    head = "" if header_rev is None and header is None else (header or HEADER40.format(rev=header_rev))
    p.write_text(head + body + "\n", encoding="utf-8")
    return rel


def cite(d: Path, rels, also_score=True) -> None:
    lines = "\n".join(f"Receipt: `{r}`" for r in rels)
    append(d, "corpus/lessons/round-72.md", "\n" + lines + "\n")
    if also_score:
        append(d, "SCORECARD.md", "\n" + lines + "\n")


def instrument_edit(d: Path, text: str, msg="instrument edit") -> str:
    (d / "tools/gate.py").write_text(text, encoding="utf-8")
    return commit(d, msg)


def note(d: Path, msg: str, text: str | None = None) -> str:
    append(d, "LOG.md", text if text is not None else f"\n- {msg}\n")
    return commit(d, msg)


# ---------------------------------------------------------------- tool invocation
def run_tool(d: Path, rnd=72, tip="master", extra=()):
    argv = [sys.executable, str(TOOL), "--repo", str(d), "--round", str(rnd), "--tip", tip, *extra]
    r = sh(argv)
    return {
        "argv": " ".join(argv),
        "exit": r.returncode,
        "stdout": r.stdout,
        "stderr": r.stderr,
    }


CASES = {}


def case(name):
    def deco(fn):
        CASES[name] = fn
        return fn
    return deco


# ---------------------------------------------------------------- controls (rig validity)
@case("C0-clean")
def c_clean(_=None):
    """A well-formed fixture: receipt measured at the commit it names, then record commits only."""
    d = init("C0")
    skeleton(d)
    measured = rev(d)
    rel = receipt(d, "measured/after/gate.out", measured, "gate: pass")
    cite(d, [rel])
    commit(d, "receipt + citation")
    note(d, "record commit after the receipt")
    return d, run_tool(d)


@case("C1-unbound")
def c_unbound(_=None):
    """Kill-rule arm 1: a receipt with no header."""
    d = init("C1")
    skeleton(d)
    rel = receipt(d, "measured/after/gate.out", None, "gate: pass", header="")
    cite(d, [rel])
    commit(d, "headerless receipt + citation")
    return d, run_tool(d)


@case("C2-nonancestor")
def c_nonancestor(_=None):
    """Kill-rule arm 2a: a header naming a revision that is not an ancestor of the tip."""
    d = init("C2")
    skeleton(d)
    # side branch carrying one commit; header names it, then master moves on.
    git(d, "checkout", "-q", "-b", "side")
    side = note(d, "side-branch commit")
    git(d, "checkout", "-q", "master")
    rel = receipt(d, "measured/after/gate.out", side, "gate: pass (measured on the side branch)")
    cite(d, [rel])
    commit(d, "receipt naming the side commit + citation")
    return d, run_tool(d)


@case("C3-stale")
def c_stale(_=None):
    """Kill-rule arm 2b: a cited receipt that is absent at the tip."""
    d = init("C3")
    skeleton(d)
    measured = rev(d)
    rel = receipt(d, "measured/after/gate.out", measured, "gate: pass")
    cite(d, [rel])
    commit(d, "receipt + citation")
    (d / rel).unlink()
    commit(d, "receipt deleted, citation left behind")
    return d, run_tool(d)


@case("C4-toolsdelta")
def c_toolsdelta(_=None):
    """Kill-rule arm 2c: the delta names tools/ (the case B5 reuses in its swallow test)."""
    d = init("C4")
    skeleton(d)
    measured = rev(d)
    rel = receipt(d, "measured/after/gate.out", measured, "gate: pass")
    cite(d, [rel])
    commit(d, "receipt + citation")
    instrument_edit(d, "print('gate v2')\n")
    return d, run_tool(d)


# ---------------------------------------------------------------- attacks
@case("B1")
def b1(_=None):
    """B1 - header names a plausible-but-wrong ancestor taken after the measurement, before an
    unrelated record commit.  The measured bytes are the commit before the header."""
    d = init("B1")
    skeleton(d)
    measured = rev(d)                     # the measurement is taken here (body says so)
    header = note(d, "unrelated record commit after the measurement")   # header points here
    rel = receipt(d, "measured/after/gate-at-tip.out", header,
                  "gate: pass [bytes measured at the skeleton commit, header names the note commit]")
    cite(d, [rel])
    commit(d, "receipt + citation")
    note(d, "unrelated record commit after the receipt")                # tip
    return d, run_tool(d)


@case("B2")
def b2(_=None):
    """B2 - header names a revision whose instrument bytes differ from the bytes that produced
    the receipt (the edit is an ancestor of the header, so the delta is blind to it)."""
    d = init("B2")
    skeleton(d)                           # instrument v1; measurement produced here
    edited = instrument_edit(d, "print('gate v2')\n")   # instrument now differs from the run
    rel = receipt(d, "measured/after/gate.out", edited,
                  "gate: pass [output of the v1 run; header names the post-edit revision]")
    cite(d, [rel])
    commit(d, "receipt + citation")
    note(d, "record commit")
    return d, run_tool(d)


@case("B2r")
def b2r(_=None):
    """B2r - the reverted-instrument variant: v1 -> v2 -> v1, receipt names the post-revert rev.
    Content-honest but indistinguishable from B2; the delta is record-only either way."""
    d = init("B2r")
    skeleton(d)
    instrument_edit(d, "print('gate v2')\n")
    reverted = instrument_edit(d, "print('gate v1')\n", "revert instrument to v1")
    rel = receipt(d, "measured/after/gate.out", reverted, "gate: pass")
    cite(d, [rel])
    commit(d, "receipt + citation")
    note(d, "record commit")
    return d, run_tool(d)


@case("B3")
def b3(_=None):
    """B3 - a cited brace expansion whose second member is absent: {before,after}.out."""
    d = init("B3")
    skeleton(d)
    measured = rev(d)
    rel = receipt(d, "measured/before/gate.out", measured, "gate: pass")
    commit(d, "before receipt")
    append(d, "corpus/lessons/round-72.md",
           "\nCounters: `.ufo/waves/round-72/measured/{before,after}/gate.out`\n")
    append(d, "SCORECARD.md",
           "\nCounters: `.ufo/waves/round-72/measured/{before,after}/gate.out`\n")
    commit(d, "citation written as a brace expansion")
    return d, run_tool(d)


@case("B3b")
def b3b(_=None):
    """B3b - control: both brace members exist and both carry headers."""
    d = init("B3b")
    skeleton(d)
    measured = rev(d)
    receipt(d, "measured/before/gate.out", measured, "gate: pass")
    receipt(d, "measured/after/gate.out", measured, "gate: pass")
    commit(d, "both receipts")
    append(d, "corpus/lessons/round-72.md",
           "\nCounters: `.ufo/waves/round-72/measured/{before,after}/gate.out`\n")
    commit(d, "brace citation")
    return d, run_tool(d)


@case("B4a")
def b4a(_=None):
    """B4a - a fenced code block documents the header format with a path that does not exist;
    the real receipt is cited outside the fence and is valid."""
    d = init("B4a")
    skeleton(d)
    measured = rev(d)
    rel = receipt(d, "measured/after/gate.out", measured, "gate: pass")
    cite(d, [rel])
    append(d, "corpus/lessons/round-72.md",
           "\n## Header format\n\n```text\n# tip=<40-hex>\n"
           ".ufo/waves/round-72/measured/after/example-only.out\n```\n")
    commit(d, "receipt, citation, fenced example")
    return d, run_tool(d)


@case("B4b")
def b4b(_=None):
    """B4b - an HTML comment hides the only citation of a headerless receipt."""
    d = init("B4b")
    skeleton(d)
    rel = receipt(d, "measured/after/hidden.out", None, "gate: pass", header="")
    commit(d, "headerless receipt")
    append(d, "corpus/lessons/round-72.md", f"\n<!-- receipt: `{rel}` -->\n")
    commit(d, "citation inside an HTML comment")
    return d, run_tool(d)


@case("B5")
def b5(_=None):
    """B5 - the delta between the header and the tip touches tools/: shifted must fire."""
    d = init("B5")
    skeleton(d)
    measured = rev(d)
    rel = receipt(d, "measured/after/gate.out", measured, "gate: pass")
    cite(d, [rel])
    commit(d, "receipt + citation")
    instrument_edit(d, "print('gate v2')\n")
    got = run_tool(d)
    return d, got


@case("B6")
def b6(_=None):
    """B6 - the r71 defect-4 shape: the receipt is graded against an earlier revision, the
    round describes it as at the report tip, and a hand-written invariance argument fills the
    delta.  Everything in the delta is a declared record path."""
    d = init("B6")
    skeleton(d)
    instrument_edit(d, "print('gate v2')\n")            # instrument commit
    graded = rev(d)                                      # receipt measures here
    rel = receipt(d, "measured/after/pre-report-at-tip.out", graded, "PRE_REPORT round=72 arms=6 failed=0")
    cite(d, [rel], also_score=False)
    commit(d, "receipt + lesson citation")
    append(d, "corpus/lessons/round-72.md",
           "\n## Final receipts\n\nThe only commits after %s add receipts, so the run above holds at the "
           "report tip.\n" % graded[:8])
    commit(d, "hand-written invariance argument")
    append(d, "SCORECARD.md", f"\nThe receipt `{rel}` runs at the report tip.\n")
    commit(d, "scorecard names it at the tip")            # tip
    return d, run_tool(d)


@case("B7")
def b7(_=None):
    """B7 - header value is a ref name (`master`), not a 40-hex sha: resolves to the tip at run
    time, so the delta is empty by construction."""
    d = init("B7")
    skeleton(d)
    rel = receipt(d, "measured/after/gate.out", None, "gate: pass", header="# tip=master\n")
    cite(d, [rel])
    commit(d, "receipt with a ref-name header + citation")
    note(d, "record commit")
    return d, run_tool(d)


@case("B9")
def b9(_=None):
    """B9 - the receipt blob is rewritten after the measurement (record-only commit), header
    still names the measured revision: the tip's content was never the measured content."""
    d = init("B9")
    skeleton(d)
    measured = rev(d)
    rel = receipt(d, "measured/after/gate.out", measured, "gate: pass")
    cite(d, [rel])
    commit(d, "receipt + citation")
    (d / rel).write_text(HEADER40.format(rev=measured) + "gate: pass [body rewritten after the run]\n",
                         encoding="utf-8")
    commit(d, "receipt body rewritten, header untouched")
    return d, run_tool(d)


@case("B10")
def b10(_=None):
    """B10 - a cited path outside the wave dir: the predicate maps this to exit 2."""
    d = init("B10")
    skeleton(d)
    measured = rev(d)
    (d / "tools/out.txt").write_text("gate: pass\n", encoding="utf-8")
    rel = ".ufo/waves/round-72/measured/after/gate.out"
    receipt(d, "measured/after/gate.out", measured, "gate: pass")
    cite(d, [rel, "tools/out.txt"])
    commit(d, "receipt, citation, and a non-receipt cited path")
    return d, run_tool(d)


@case("B11")
def b11(_=None):
    """B11 - the short-hash header the lane's own round-71 prose quotes (# tip=4b284653)."""
    d = init("B11")
    skeleton(d)
    measured = rev(d)
    rel = receipt(d, "measured/after/gate.out", None, "gate: pass",
                  header="# tip=%s\n" % measured[:8])
    cite(d, [rel])
    commit(d, "short-hash header + citation")
    return d, run_tool(d)


@case("B12")
def b12(_=None):
    """B12 - the receipt is cited by the relative form the round-71 self-record actually uses
    (`measured/after/gate.out`), and carries no header."""
    d = init("B12")
    skeleton(d)
    rel = receipt(d, "measured/after/gate.out", None, "gate: pass", header="")
    commit(d, "headerless receipt")
    append(d, "corpus/lessons/round-72.md", "\nReceipt: `measured/after/gate.out`\n")
    append(d, "SCORECARD.md", "\nReceipt: `measured/after/gate.out`\n")
    commit(d, "relative citation")
    return d, run_tool(d)


@case("B12b")
def b12b(_=None):
    """B12b - the same escape through a w1/-relative citation of a headerless receipt."""
    d = init("B12b")
    skeleton(d)
    rel = receipt(d, "w1/SEAT01/control.out", None, "control: pass", header="")
    commit(d, "headerless w1 receipt")
    append(d, "corpus/lessons/round-72.md", "\nFixture: `w1/SEAT01/control.out`\n")
    commit(d, "w1-relative citation")
    return d, run_tool(d)


@case("B14")
def b14(_=None):
    """B14 - the round's lesson file is absent: the self-record is half unreadable (exit 2)."""
    d = init("B14")
    skeleton(d)
    measured = rev(d)
    rel = receipt(d, "measured/after/gate.out", measured, "gate: pass")
    cite(d, [rel], also_score=False)
    commit(d, "receipt + scorecard citation")
    (d / "corpus/lessons/round-72.md").unlink()
    commit(d, "lesson deleted")
    return d, run_tool(d)


@case("B16")
def b16(_=None):
    """B16 - no round-72 self-record at all: a wrong round label must not read as green."""
    d = init("B16")
    (d / "tools").mkdir()
    (d / "tools/gate.py").write_text("print('gate v1')\n", encoding="utf-8")
    (d / "corpus/lessons").mkdir(parents=True)
    (d / "SCORECARD.md").write_text(
        "# kama scorecard (fixture)\n\n## Round 71 - the previous round\n\nReceipt: `measured/after/old.out`\n",
        encoding="utf-8")
    (d / "corpus/lessons/round-71.md").write_text("# Round 71 lesson (fixture)\n", encoding="utf-8")
    commit(d, "a repo with only a round-71 record")
    return d, run_tool(d)


@case("B17")
def b17(_=None):
    """B17 - round-72 section exists but cites no receipt, lesson absent (the fully vacuous
    case): cited=0 must not exit 0."""
    d = init("B17")
    (d / "tools").mkdir()
    (d / "tools/gate.py").write_text("print('gate v1')\n", encoding="utf-8")
    (d / "SCORECARD.md").write_text(
        "# kama scorecard (fixture)\n\n## Round 72 - fixture round\n\nNo receipts here.\n",
        encoding="utf-8")
    commit(d, "round-72 section with no citation and no lesson")
    return d, run_tool(d)


@case("F1")
def f1(_=None):
    """F1 - a clean bound receipt plus one backticked short commit hash in prose.  A bare hash is
    not a path; the extractor resolves it under the wave dir and exits 2."""
    d = init("F1")
    skeleton(d)
    measured = rev(d)
    rel = receipt(d, "measured/after/gate.out", measured, "gate: pass")
    cite(d, [rel])
    commit(d, "receipt + citation")
    append(d, "corpus/lessons/round-72.md",
           "\nThe freeze commit was `b43e71a8`, two rounds before this one.\n")
    commit(d, "prose naming a short commit hash")
    return d, run_tool(d)


@case("F1b")
def f1b(_=None):
    """F1b - the same with a backticked bare word (`master`), not a hash."""
    d = init("F1b")
    skeleton(d)
    measured = rev(d)
    rel = receipt(d, "measured/after/gate.out", measured, "gate: pass")
    cite(d, [rel])
    commit(d, "receipt + citation")
    append(d, "corpus/lessons/round-72.md", "\nThe counting command names `master` as its tip.\n")
    commit(d, "prose naming a ref")
    return d, run_tool(d)


@case("F1c")
def f1c(_=None):
    """F1c - a backticked key=value token (`pass=18`)."""
    d = init("F1c")
    skeleton(d)
    measured = rev(d)
    rel = receipt(d, "measured/after/gate.out", measured, "gate: pass")
    cite(d, [rel])
    commit(d, "receipt + citation")
    append(d, "corpus/lessons/round-72.md", "\nThe selftest printed `pass=18` at the tip.\n")
    commit(d, "prose naming a tally")
    return d, run_tool(d)


@case("F1d")
def f1d(_=None):
    """F1d - control: a backticked command (whitespace) is skipped, so the same record is bound."""
    d = init("F1d")
    skeleton(d)
    measured = rev(d)
    rel = receipt(d, "measured/after/gate.out", measured, "gate: pass")
    cite(d, [rel])
    commit(d, "receipt + citation")
    append(d, "corpus/lessons/round-72.md", "\nRun `python3 tools/gate.py --tip master` to repeat.\n")
    commit(d, "prose naming a command")
    return d, run_tool(d)


@case("B4a2")
def b4a2(_=None):
    """B4a2 - a fenced documentation example carrying a backticked path that does not exist."""
    d = init("B4a2")
    skeleton(d)
    measured = rev(d)
    rel = receipt(d, "measured/after/gate.out", measured, "gate: pass")
    cite(d, [rel])
    append(d, "corpus/lessons/round-72.md",
           "\n## Header format\n\n```text\n# tip=<40-hex>\n"
           "the receipt line reads `.ufo/waves/round-72/measured/after/example-only.out`\n```\n")
    commit(d, "receipt, citation, fenced example")
    return d, run_tool(d)


@case("B4c")
def b4c(_=None):
    """B4c - a fenced example carrying a backticked path that DOES exist and is otherwise
    uncited: documentation inflates the graded population."""
    d = init("B4c")
    skeleton(d)
    measured = rev(d)
    rel = receipt(d, "measured/after/gate.out", measured, "gate: pass")
    extra = receipt(d, "measured/after/example.out", measured, "example body")
    cite(d, [rel])
    append(d, "corpus/lessons/round-72.md",
           "\n## Header format\n\n```text\n"
           "`.ufo/waves/round-72/measured/after/example.out`\n```\n")
    commit(d, "receipt, citation, fenced example that exists")
    return d, run_tool(d)


@case("B10b")
def b10b(_=None):
    """B10b - a cited repo-root, non-receipt path (`tools/out.txt`), delta clean.  The frozen
    exit map says 'a cited path that is not a receipt path' is exit 2."""
    d = init("B10b")
    skeleton(d)
    (d / "tools/out.txt").write_text("gate: pass\n", encoding="utf-8")
    measured = commit(d, "instrument output")
    rel = receipt(d, "measured/after/gate.out", measured, "gate: pass")
    cite(d, [rel, "tools/out.txt"])
    commit(d, "receipt + citations")
    return d, run_tool(d)


@case("B17b")
def b17b(_=None):
    """B17b - both record files exist and cite nothing: an empty population must be exit 2."""
    d = init("B17b")
    skeleton(d)
    return d, run_tool(d)


@case("E10")
def e10(_=None):
    """E10 - the record cites a committed non-receipt wave-dir file (a seat report .md): the
    frozen exit map calls that 'a cited path that is not a receipt path' -> exit 2."""
    d = init("E10")
    skeleton(d)
    measured = rev(d)
    rel = receipt(d, "measured/after/gate.out", measured, "gate: pass")
    (d / ".ufo/waves/round-72/w1/SEAT01.md").parent.mkdir(parents=True, exist_ok=True)
    (d / ".ufo/waves/round-72/w1/SEAT01.md").write_text("# seat report\n", encoding="utf-8")
    cite(d, [rel, "w1/SEAT01.md"])
    commit(d, "receipt + a committed seat report cited in the record")
    return d, run_tool(d)


@case("E10b")
def e10b(_=None):
    """E10b - the same citation, but the .md is NOT committed: it silently drops out of scope
    instead of reading stale, so the verdict depends on whether the seat report landed."""
    d = init("E10b")
    skeleton(d)
    measured = rev(d)
    rel = receipt(d, "measured/after/gate.out", measured, "gate: pass")
    cite(d, [rel, "w1/SEAT01.md"])
    commit(d, "receipt + citation of a path that does not exist at the tip")
    return d, run_tool(d)


@case("E11")
def e11(_=None):
    """E11 - a committed .py control cited in the record (the shape SCORECARD.md:3766 uses)."""
    d = init("E11")
    skeleton(d)
    measured = rev(d)
    rel = receipt(d, "measured/after/gate.out", measured, "gate: pass")
    (d / ".ufo/waves/round-72/controls").mkdir(parents=True, exist_ok=True)
    (d / ".ufo/waves/round-72/controls/control.py").write_text("# control\n", encoding="utf-8")
    cite(d, [rel, "controls/control.py"])
    commit(d, "receipt + a committed control script cited in the record")
    return d, run_tool(d)


@case("G7")
def g7(_=None):
    """G7 - no header line at all: the first lines are body text that mentions `tip=<sha>` in
    prose.  The predicate asks for a header; the regex asks for the substring anywhere."""
    d = init("G7")
    skeleton(d)
    measured = rev(d)
    harmless = receipt(d, "measured/after/gate.out", None,
                       "gate: pass\nnote: the run was compared with tip=%s before the edit" % measured,
                       header="")
    cite(d, [harmless])
    commit(d, "receipt with a prose tip= mention, no header line")
    note(d, "record commit")
    return d, run_tool(d)


@case("G3")
def g3(_=None):
    """G3 - a real header below a five-line preamble: unbound by the window, though the
    predicate states no position."""
    d = init("G3")
    skeleton(d)
    measured = rev(d)
    p = d / ".ufo/waves/round-72/measured/after/gate.out"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("usage: gate.py [--tip REV]\n\n"
                 "This receipt records one run of the gate.\n"
                 "The output follows after a blank line.\n"
                 "See the claims plan for the predicate.\n\n"
                 "# tip=%s\ngate: pass\n" % measured, encoding="utf-8")
    cite(d, ["measured/after/gate.out"])
    commit(d, "receipt with a preamble and a header on line 7")
    return d, run_tool(d)


@case("H1")
def h1(_=None):
    """H1 - the same B5 delta, but the invocation widens the allow-list with --record-path so
    tools/ is a record path.  The printed line is byte-identical to a truthful one."""
    d = init("H1")
    skeleton(d)
    measured = rev(d)
    rel = receipt(d, "measured/after/gate.out", measured, "gate: pass")
    cite(d, [rel])
    commit(d, "receipt + citation")
    instrument_edit(d, "print('gate v2')\n")
    return d, run_tool(d, extra=("--record-path", ".ufo/waves/round-72/", "--record-path", "tools/"))


@case("H1b")
def h1b(_=None):
    """H1b - the widening that works: every path the round commits is declared, including tools/.
    The verdict line is byte-identical to a truthful one; nothing on it names the allow-list."""
    d = init("H1b")
    skeleton(d)
    measured = rev(d)
    rel = receipt(d, "measured/after/gate.out", measured, "gate: pass")
    cite(d, [rel])
    commit(d, "receipt + citation")
    instrument_edit(d, "print('gate v2')\n")
    return d, run_tool(d, extra=("--record-path", ".ufo/waves/round-72/",
                                 "--record-path", "SCORECARD.md",
                                 "--record-path", "corpus/lessons/",
                                 "--record-path", "LOG.md",
                                 "--record-path", "tools/"))


def main(argv):
    if not TOOL.exists():
        print(f"A0 module never appeared: {TOOL}")
        return 3
    names = argv[1:] or list(CASES)
    out = S / "results.json"
    rows = []
    for name in names:
        d, r = CASES[name](None)
        verdict = [ln for ln in r["stdout"].splitlines()
                   if ln.startswith("RECEIPT_TIP_BINDING") or ln.startswith("RECEIPT_TIP_FINDING")]
        row = {"case": name, "fixture": str(d), "exit": r["exit"],
               "verdict": verdict, "stdout": r["stdout"], "stderr": r["stderr"], "argv": r["argv"]}
        rows.append(row)
        print(f"=== {name} exit={r['exit']}")
        for ln in verdict:
            print("    " + ln)
        if not verdict:
            print("    (no RECEIPT_TIP_BINDING line) " + repr(r["stdout"][-200:]))
        if r["stderr"].strip():
            print("    stderr: " + repr(r["stderr"][-300:]))
    prev = json.loads(out.read_text()) if out.exists() else []
    keep = [p for p in prev if p["case"] not in names]
    out.write_text(json.dumps(keep + rows, indent=1))
    print(f"\nresults -> {out} ({len(keep + rows)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
