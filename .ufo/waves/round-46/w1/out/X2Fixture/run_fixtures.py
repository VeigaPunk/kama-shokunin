#!/usr/bin/env python3
"""X2Fixture - round-46 item X2: adversarial fixtures for tools/append-only-audit.py.

Each fixture is a throwaway git repo under <scratch>/fx.  For every fixture this
driver records:

  tool     python3 <lane>/tools/append-only-audit.py --repo D --to <tip> --json
           (exit code, parsed events, stderr)
  counter  <lane>/tools/round46-append-audit-check.py :: recompute(D, <tip>)
           (imported by path with importlib; independent frozen recomputation)
  oracle   a byte-exact reading of the contract: `git diff -U0` parsed
           *positionally* (the `---`/`+++` preamble ends at the first `@@`), and
           the tip's line set taken from `git cat-file blob` bytes without the
           phantom empty element that `split("\\n")` gives a newline-terminated
           file.  This is what "deleted = `-` lines of the diff, the `---`
           header excluded" and "occurring as some *line* of <file> at <to>"
           mean read literally.

It then reports (a) tool-vs-counter disagreements and (b) cases where the tool
and the counter agree with each other but not with the oracle.

Run:  python3 run_fixtures.py <scratch-dir>
Writes: results.json, matrix.tsv next to this file; fixtures under <scratch>/fx.
Read-only on the lane.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
TOOL = os.environ.get("AOA_TOOL", f"{LANE}/tools/append-only-audit.py")
COUNTER = f"{LANE}/tools/round46-append-audit-check.py"
DECL = ["SCORECARD.md", "LOG.md", "corpus/QUALITY.md", "corpus/README.md", "corpus/SOURCES.md"]
KEYS = ("commit", "file", "deleted", "restored_at_tip", "status", "restored_by")
IDENT = ["-c", "user.name=x2-fixture", "-c", "user.email=x2-fixture@invalid", "-c", "commit.gpgsign=false"]

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ)


def load_counter():
    spec = importlib.util.spec_from_file_location("r46_c2_counter", COUNTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


C2 = load_counter()


# ---------------------------------------------------------------- git helpers
def git(d, *a, inp=None, check=True):
    p = subprocess.run(["git", "-C", d, *a], capture_output=True, text=True, input=inp)
    if check and p.returncode != 0:
        raise RuntimeError(f"git {' '.join(a)[:160]}: {p.stderr.strip()[:300]}")
    return p


def bgit(d, *a):
    return subprocess.run(["git", "-C", d, *a], capture_output=True).stdout


def gitc(d, *a, check=True):
    """git with the fixture identity attached to the subcommand's global options."""
    return git(d, *IDENT, *a, check=check)


class Fx:
    def __init__(self, name):
        self.name = name
        self.d = tempfile.mkdtemp(prefix=name + "-", dir=FIXTURES)
        git(self.d, "init", "-q")
        top = git(self.d, "rev-parse", "--show-toplevel").stdout.strip()
        if os.path.realpath(top) != os.path.realpath(self.d):
            raise RuntimeError(f"fixture toplevel mismatch: {top} != {self.d}")
        self.n = 0

    def abspath(self, path):
        return os.path.join(self.d, path)

    def w(self, path, data):
        if isinstance(data, str):
            data = data.encode()
        p = self.abspath(path)
        parent = os.path.dirname(p)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(p, "wb") as fh:
            fh.write(data)

    def rm(self, path):
        git(self.d, "rm", "-q", "-r", "--", path)

    def mv(self, a, b):
        git(self.d, "mv", a, b)

    def commit(self, msg):
        git(self.d, "add", "-A")
        self.n += 1
        git(self.d, *IDENT, "commit", "-q", "-m", f"{msg} c{self.n}")
        return git(self.d, "rev-parse", "HEAD").stdout.strip()

    def head(self):
        return git(self.d, "rev-parse", "HEAD").stdout.strip()


# ---------------------------------------------------------------- oracle
def parse_deleted_positional(diff_bytes, path=None):
    """`-` lines of a single-file `git diff -U0`, preamble skipped by position.

    With `path`, only the section whose a-side path is exactly `path` is parsed:
    `git diff -- <path>` also matches everything under a directory of that name,
    and counting another section's lines would be an oracle artefact, not a
    property of the contract.
    """
    out = []
    for sec in diff_bytes.split(b"diff --git ")[1:]:
        head = sec.split(b"\n", 1)[0]
        if path is not None:
            want = b"a/" + path.encode()
            if not head.startswith(want + b" ") and head != want:
                continue
        in_hunk = False
        for ln in sec.split(b"\n"):
            if ln.startswith(b"@@"):
                in_hunk = True
                continue
            if in_hunk and ln.startswith(b"-"):
                out.append(ln[1:])
    return out


def blob_bytes(d, rev, path):
    p = subprocess.run(["git", "-C", d, "cat-file", "blob", f"{rev}:{path}"], capture_output=True)
    return p.stdout if p.returncode == 0 else None


def blob_line_set(b):
    if b is None:
        return None
    if b.endswith(b"\n"):
        b = b[:-1]
    if b == b"" and False:
        pass
    return set(b.split(b"\n")) if b != b"" else set()


def oracle(d, to):
    commits = bgit(d, "rev-list", "--topo-order", "--reverse", to).decode().split()
    events, binary_files, notes = [], [], []
    tips = {f: blob_line_set(blob_bytes(d, to, f)) for f in DECL}
    for i, c in enumerate(commits):
        par = subprocess.run(["git", "-C", d, "rev-parse", "--verify", "-q", c + "^1"], capture_output=True)
        if par.returncode != 0:
            continue
        p = par.stdout.decode().strip()
        for f in DECL:
            diff = bgit(d, "diff", "--no-renames", "--no-color", "--no-ext-diff", "-U0", p, c, "--", f)
            num = bgit(d, "diff", "--no-renames", "--numstat", p, c, "--", f).decode().split("\t")
            is_bin = len(num) >= 2 and num[0] == "-"
            dele = parse_deleted_positional(diff, f)
            if is_bin:
                binary_files.append((c, f))
            if len(dele) < 20:
                continue
            tip = tips[f]
            tipset = set() if tip is None else tip
            k = sum(1 for x in dele if x in tipset)
            status = "restored" if k == len(dele) else ("unrestored" if k == 0 else "partial")
            rb = None
            for c2 in commits[i + 1:]:
                have = blob_line_set(blob_bytes(d, c2, f)) or set()
                if all(x in have for x in dele):
                    rb = c2
                    break
            events.append({"commit": c, "file": f, "deleted": len(dele), "restored_at_tip": k,
                           "status": status, "restored_by": rb})
    return {"events": events, "binary": binary_files,
            "events_bytes": [{kk: (v.decode("utf-8", "backslashreplace") if isinstance(v, bytes) else v)
                              for kk, v in e.items()} for e in events]}


# ---------------------------------------------------------------- runners
def norm(evs):
    return set(tuple(e.get(k) for k in KEYS) for e in evs) if evs is not None else None


def expected_rc(evs):
    return 1 if any(e["status"] != "restored" for e in evs) else 0


def run_tool(d, to):
    t0 = time.perf_counter()
    p = subprocess.run([sys.executable, TOOL, "--repo", d, "--to", to, "--json"],
                       capture_output=True, text=True, env=ENV, timeout=1800)
    dt = time.perf_counter() - t0
    ev = None
    try:
        ev = json.loads(p.stdout)["events"]
    except Exception:
        pass
    return {"rc": p.returncode, "events": ev, "stderr": p.stderr[-600:],
            "stdout_tail": p.stdout[-400:] if ev is None else "", "secs": round(dt, 3)}


def run_counter(d, to):
    t0 = time.perf_counter()
    try:
        ev = C2.recompute(d, to)
        err = None
    except Exception as e:  # noqa: BLE001 - a crash is a result
        ev, err = None, f"{type(e).__name__}: {e}"
    return {"events": ev, "error": err, "secs": round(time.perf_counter() - t0, 3)}


def evaluate(fx, to, expect, note):
    tool = run_tool(fx.d, to)
    cnt = run_counter(fx.d, to)
    orc = oracle(fx.d, to)
    tn, cn, on = norm(tool["events"]), norm(cnt["events"]), norm(orc["events"])
    disagree = (tn != cn) or (tool["events"] is not None and tool["rc"] != expected_rc(cnt["events"] or []))
    both_wrong = (tn == cn) and (tn != on)
    return {
        "case": fx.name, "repo": fx.d, "to": to, "expect": expect, "note": note,
        "tool": tool, "counter": cnt, "oracle": {"events": orc["events_bytes"], "binary": [[c, f] for c, f in orc["binary"]]},
        "tool_vs_counter": "AGREE" if not disagree else "DISAGREE",
        "tool_vs_oracle": "match" if tn == on else "DIFFER",
        "counter_vs_oracle": "match" if cn == on else "DIFFER",
        "both_wrong_vs_oracle": both_wrong,
        "disagree_detail": None if not disagree else {
            "missing_from_tool": sorted(map(str, (cn or set()) - (tn or set())))[:6],
            "extra_in_tool": sorted(map(str, (tn or set()) - (cn or set())))[:6],
            "tool_rc": tool["rc"], "rc_for_counter_events": expected_rc(cnt["events"] or [])},
        "oracle_delta": None if tn == on else {
            "missing_from_tool": sorted(map(str, on - (tn or set())))[:6],
            "extra_in_tool": sorted(map(str, (tn or set()) - on))[:6]},
    }


# ---------------------------------------------------------------- cases
CASES = []


def case(fn):
    CASES.append(fn)
    return fn


def body(tag, n, eol=b"\n", tail=True):
    return eol.join(f"{tag} line {i:03d}".encode() for i in range(n)) + (eol if tail else b"")


@case
def crlf_relf():
    fx = Fx("crlf")
    lines = [f"crlf line {i:03d}".encode() for i in range(40)]
    fx.w("LOG.md", b"\r\n".join(lines) + b"\r\n")
    fx.commit("base CRLF")
    fx.w("LOG.md", b"\r\n".join(lines[:15]) + b"\r\n")
    c = fx.commit("delete 25 CRLF lines")
    fx.w("LOG.md", b"\n".join(lines) + b"\n")  # restore the same text, LF endings only
    r = fx.commit("restore 40 lines with LF endings")
    return evaluate(fx, fx.head(),
                    "byte-exact: the 25 deleted lines ended CRLF, the tip holds them LF -> unrestored",
                    "CRLF deleted at %s, re-added LF at %s" % (c[:12], r[:12]))


@case
def crlf_crlf_restore():
    fx = Fx("crlf2")
    lines = [f"crlf line {i:03d}".encode() for i in range(40)]
    fx.w("LOG.md", b"\r\n".join(lines) + b"\r\n")
    fx.commit("base CRLF")
    fx.w("LOG.md", b"\r\n".join(lines[:15]) + b"\r\n")
    c = fx.commit("delete 25 CRLF lines")
    fx.w("LOG.md", b"\r\n".join(lines) + b"\r\n")
    r = fx.commit("restore the same CRLF lines")
    return evaluate(fx, fx.head(), "restored at %s" % r[:12], "control for the CRLF case")


@case
def lone_cr_content():
    fx = Fx("cr")
    lines = [("lone cr item %03d" % i).encode() + b"\rTAIL" for i in range(30)]
    fx.w("LOG.md", b"\n".join(lines) + b"\n")
    fx.commit("base, embedded lone CR in every line")
    fx.w("LOG.md", b"\n".join(lines[:5]) + b"\n")
    c = fx.commit("delete 25 lines that contain a lone CR")
    fx.w("LOG.md", b"\n".join(x.split(b"\r")[0] for x in lines) + b"\n")
    r = fx.commit("re-add the 25 head fragments without the CR suffix")
    return evaluate(fx, fx.head(),
                    "byte-exact: 'item NNN\\rTAIL' is not 'item NNN' -> unrestored",
                    "deleted at %s, head-only text restored at %s" % (c[:12], r[:12]))


@case
def no_trailing_newline():
    fx = Fx("nonl")
    lines = [f"nl line {i:03d}".encode() for i in range(40)]
    fx.w("LOG.md", b"\n".join(lines))  # no trailing newline
    fx.commit("base without trailing newline")
    fx.w("LOG.md", b"\n".join(lines[:15]))  # still no trailing newline: 25 deleted
    c = fx.commit("delete 25, no trailing newline")
    fx.w("LOG.md", b"\n".join(lines) + b"\n")  # restored WITH trailing newline
    r = fx.commit("restore 40 with trailing newline")
    return evaluate(fx, fx.head(), "restored at %s (text equal; only the final newline differs)" % r[:12],
                    "deletion at %s; the last deleted line carries the no-newline marker" % c[:12])


@case
def trailing_whitespace():
    fx = Fx("ws")
    lines = [f"ws line {i:03d}".encode() for i in range(30)]
    fx.w("LOG.md", b"\n".join(lines) + b"\n")
    fx.commit("base")
    fx.w("LOG.md", b"\n".join(lines[:5] + [x + b" " for x in lines[5:]]) + b"\n")
    c = fx.commit("re-add 25 with one trailing space")
    return evaluate(fx, fx.head(), "unrestored: 'exact text' means the trailing space is a different line",
                    "event at %s has 25 deletions and 25 additions" % c[:12])


@case
def duplicate_lines():
    fx = Fx("dups")
    fx.w("LOG.md", b"dup line\n" * 30)
    fx.commit("base 30 identical lines")
    fx.w("LOG.md", b"dup line\n" * 5)
    c = fx.commit("keep 5 of 30 identical lines")
    ev = run_tool(fx.d, fx.head())
    res = evaluate(fx, fx.head(),
                   "restored per docstring: 'duplicates may share one line'",
                   "25 identical lines deleted at %s, tip still holds the same text" % c[:12])
    return res


@case
def binary_nul():
    fx = Fx("bin")
    fx.w("SCORECARD.md", bytes(range(256)) * 4)
    fx.commit("binary base")
    fx.w("SCORECARD.md", bytes(reversed(range(256))) * 2)
    c = fx.commit("binary replacement")
    return evaluate(fx, fx.head(),
                    "docstring's own definition (deleted = `-` lines of the diff) yields 0 for a binary diff",
                    "no textual deletion is observable in git diff for %s" % c[:12])


@case
def invalid_utf8_tip():
    fx = Fx("utf8")
    lines = [f"u8 line {i:03d}".encode() for i in range(40)]
    fx.w("LOG.md", b"\n".join(lines) + b"\n")
    fx.commit("text base")
    fx.w("LOG.md", b"\n".join(lines[:15]) + b"\n")
    c = fx.commit("delete 25 text lines")
    fx.w("LOG.md", b"\xff\xfe\x00\x81 not utf-8\n\xff\xfe\n")
    fx.commit("tip blob is not valid UTF-8")
    return evaluate(fx, fx.head(),
                    "tool contract: exit 2 'could not evaluate' if it cannot decode the blob",
                    "event at %s, tip blob is invalid UTF-8" % c[:12])


@case
def mode_only():
    fx = Fx("mode")
    fx.w("LOG.md", body("md", 40))
    fx.commit("base")
    os.chmod(fx.abspath("LOG.md"), 0o755)
    c = fx.commit("mode 100644 -> 100755 only")
    return evaluate(fx, fx.head(), "no event: a mode change deletes no lines",
                    "mode-only change at %s" % c[:12])


@case
def rename_roundtrip():
    fx = Fx("ren")
    lines = [f"rn line {i:03d}".encode() for i in range(30)]
    fx.w("LOG.md", b"\n".join(lines) + b"\n")
    fx.commit("base")
    fx.mv("LOG.md", "LOG2.md")
    c = fx.commit("git mv LOG.md LOG2.md")
    fx.w("corpus/README.md", b"unrelated\n")
    fx.commit("unrelated")
    fx.mv("LOG2.md", "LOG.md")
    r = fx.commit("git mv LOG2.md LOG.md")
    return evaluate(fx, fx.head(),
                    "restored at the rename-back commit; the intermediate rename is a 30-line deletion event",
                    "rename away at %s, back at %s" % (c[:12], r[:12]))


@case
def evil_merge_first_parent():
    fx = Fx("merge")
    lines = [f"mg line {i:03d}".encode() for i in range(60)]
    fx.w("LOG.md", b"\n".join(lines) + b"\n")
    fx.commit("base")
    br = git(fx.d, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    gitc(fx.d, "checkout", "-q", "-b", "side")
    fx.w("notes.md", b"side only\n")
    fx.commit("side adds notes.md")
    gitc(fx.d, "checkout", "-q", br)
    fx.w("LOG.md", b"\n".join(lines[:35]) + b"\n")
    fx.commit("main deletes 25")
    gitc(fx.d, "merge", "-q", "--no-ff", "--no-commit", "side")
    fx.w("LOG.md", b"\n".join(lines[:10]) + b"\n")  # evil: another 25 gone vs first parent
    fx.commit("evil merge deletes 25 more")
    m = fx.head()
    return evaluate(fx, m,
                    "the merge is an event against its first parent (25 deleted), status unrestored",
                    "merge commit %s deletes 25 lines relative to first parent" % m[:12])


@case
def octopus_merge():
    fx = Fx("octo")
    lines = [f"oc line {i:03d}".encode() for i in range(60)]
    fx.w("LOG.md", b"\n".join(lines) + b"\n")
    fx.commit("base")
    br = git(fx.d, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    gitc(fx.d, "checkout", "-q", "-b", "s1")
    fx.w("notes.md", b"s1\n")
    fx.commit("s1 adds notes.md")
    gitc(fx.d, "checkout", "-q", br)
    gitc(fx.d, "checkout", "-q", "-b", "s2")
    fx.w("other.md", b"s2\n")
    fx.commit("s2 adds other.md")
    gitc(fx.d, "checkout", "-q", br)
    gitc(fx.d, "merge", "-q", "--no-ff", "--no-commit", "s1", "s2")
    fx.w("LOG.md", b"\n".join(lines[:30]) + b"\n")  # 30 deleted vs first parent
    fx.commit("octopus with a deletion vs first parent")
    m = fx.head()
    parents = git(fx.d, "rev-list", "--parents", "-n", "1", m).stdout.split()
    return evaluate(fx, m,
                    "first-parent diff decides: 30 deleted; the octopus's other parents delete nothing",
                    "merge %s parents=%s" % (m[:12], [p[:12] for p in parents[1:]]))


@case
def octopus_side_delete():
    fx = Fx("octo2")
    lines = [f"od line {i:03d}".encode() for i in range(60)]
    fx.w("LOG.md", b"\n".join(lines) + b"\n")
    fx.commit("base")
    br = git(fx.d, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    gitc(fx.d, "checkout", "-q", "-b", "s1")
    fx.w("LOG.md", b"\n".join(lines[:35]) + b"\n")  # 25 deleted on a side branch
    c1 = fx.commit("s1 deletes 25")
    gitc(fx.d, "checkout", "-q", br)
    gitc(fx.d, "checkout", "-q", "-b", "s2")
    fx.w("other.md", b"s2\n")
    fx.commit("s2 adds other.md")
    gitc(fx.d, "checkout", "-q", br)
    gitc(fx.d, "merge", "-q", "--no-ff", "--no-commit", "s1", "s2")
    m = fx.commit("octopus takes s1's LOG.md")
    return evaluate(fx, m,
                    "the side deletion is an event at %s, and the octopus repeats it against its first parent"
                    % c1[:12],
                    "octopus %s; the same 25 lines are deleted in two commits" % m[:12])


@case
def same_lines_deleted_twice():
    fx = Fx("twice")
    lines = [f"tw line {i:03d}".encode() for i in range(60)]
    fx.w("LOG.md", b"\n".join(lines) + b"\n")
    fx.commit("base")
    fx.w("LOG.md", b"\n".join(lines[:20] + lines[45:]) + b"\n")  # 25 deleted
    c1 = fx.commit("delete lines 20..44")
    fx.w("LOG.md", b"\n".join(lines) + b"\n")
    r = fx.commit("restore")
    fx.w("LOG.md", b"\n".join(lines[:20] + lines[45:]) + b"\n")  # same 25 deleted again
    c2 = fx.commit("delete the same 25 again")
    return evaluate(fx, fx.head(),
                    "two events: %s restored by %s; %s unrestored" % (c1[:12], r[:12], c2[:12]),
                    "same-line double deletion")


@case
def large_file_50k():
    fx = Fx("large")
    lines = [f"big line {i:06d} padding-padding-padding".encode() for i in range(50000)]
    fx.w("LOG.md", b"\n".join(lines) + b"\n")
    fx.commit("50k lines")
    fx.w("LOG.md", b"\n".join(lines[:49975]) + b"\n")
    c = fx.commit("delete the last 25 lines")
    return evaluate(fx, fx.head(), "one unrestored event, deleted=25",
                    "50k-line file, 25 deleted at %s" % c[:12])


@case
def blank_line_phantom():
    fx = Fx("blank")
    lines = []
    for i in range(30):
        lines.append(f"bl line {i:03d}".encode())
    # 25 blank lines interleaved
    mixed = []
    for i in range(30):
        mixed.append(lines[i])
        if i < 25:
            mixed.append(b"")
    blanks = sum(1 for x in mixed if x == b"")
    fx.w("LOG.md", b"\n".join(mixed) + b"\n")
    fx.commit("base with %d blank lines" % blanks)
    fx.w("LOG.md", b"\n".join(lines) + b"\n")  # all blanks removed
    c = fx.commit("remove all %d blank lines" % blanks)
    res = evaluate(fx, fx.head(),
                   "unrestored: the tip holds no blank line (split('\\n')'s trailing '' is not a line)",
                   "%d empty lines deleted at %s; tip has none" % (blanks, c[:12]))
    return res


@case
def blank_truncate_to_empty():
    fx = Fx("trunc")
    fx.w("LOG.md", b"\n" * 30)  # 30 blank lines, nothing else
    fx.commit("base: 30 blank lines")
    fx.w("LOG.md", b"")
    c = fx.commit("truncate the declared file to 0 bytes")
    res = evaluate(fx, fx.head(),
                   "unrestored: a 0-byte file holds no lines at all",
                   "30 blank lines deleted at %s, tip file is empty" % c[:12])
    res["tip_bytes"] = len(blob_bytes(fx.d, fx.head(), "LOG.md") or b"")
    return res


@case
def lane_scorecard_blank_strip():
    """Realistic: strip every blank line from a byte copy of the lane's SCORECARD.md."""
    fx = Fx("laneblank")
    src = open(os.path.join(LANE, "SCORECARD.md"), "rb").read()
    fx.w("SCORECARD.md", src)
    fx.commit("byte copy of the lane SCORECARD.md")
    kept = [x for x in src.split(b"\n") if x != b""]
    removed = len(src.split(b"\n")) - 1 - len(kept)
    fx.w("SCORECARD.md", b"\n".join(kept) + b"\n")
    c = fx.commit("strip %d blank lines" % removed)
    res = evaluate(fx, fx.head(),
                   "unrestored: every blank line is gone from the audited file",
                   "%d blank lines deleted from a copy of the lane file at %s" % (removed, c[:12]))
    res["blanks_removed"] = removed
    return res


@case
def dash_prefixed_lines():
    fx = Fx("dash")
    lines = [f"-- dash comment {i:03d}".encode() for i in range(30)]
    fx.w("LOG.md", b"\n".join(lines) + b"\n")
    fx.commit("base 30 lines starting with --")
    fx.w("LOG.md", b"\n".join(lines[:5]) + b"\n")
    c = fx.commit("delete 25 lines starting with --")
    res = evaluate(fx, fx.head(),
                   "event with deleted=25: content lines '--x' render as '---x', not as the '---' header",
                   "25 deletions whose diff text starts with '---' at %s" % c[:12])
    res["numstat"] = bgit(fx.d, "diff", "--numstat", c + "^1", c, "--", "LOG.md").decode().strip()
    res["numstat_patch"] = bgit(fx.d, "diff", "-U0", c + "^1", c, "--", "LOG.md").decode()
    return res


@case
def dir_in_place_of_file():
    fx = Fx("dir")
    lines = [f"dr line {i:03d}".encode() for i in range(29)] + [b"child.txt"]
    fx.w("LOG.md", b"\n".join(lines) + b"\n")
    fx.commit("base; one line is literally 'child.txt'")
    os.remove(fx.abspath("LOG.md"))
    os.makedirs(fx.abspath("LOG.md"))
    fx.w("LOG.md/child.txt", b"now a directory\n")
    c = fx.commit("replace LOG.md with a directory")
    res = evaluate(fx, fx.head(),
                   "the tip holds no LOG.md *lines*: unrestored (the path is a tree at tip)",
                   "deleted lines include 'child.txt', which is also the child entry name at %s" % c[:12])
    res["show_tree"] = git(fx.d, "show", f"HEAD:LOG.md", check=False).stdout
    return res


# ---------------------------------------------------------------- main
def numstat_sweep(d, to):
    """deleted-line counts per (commit, file) in one git process, independent of diff text."""
    commits = git(d, "rev-list", "--topo-order", "--reverse", to).stdout.split()
    out = git(d, "log", "-m", "--diff-merges=first-parent", "--no-renames", "--numstat",
              "--no-color", "--format=%x01%H", to, "--", *DECL, check=False)
    if out.returncode != 0:
        out = git(d, "log", "--no-renames", "--numstat", "--no-color", "--format=%x01%H",
                  to, "--", *DECL)
    events, cur = {}, None
    for line in out.stdout.split("\n"):
        if line.startswith("\x01"):
            cur = line[1:].strip()
            continue
        if not line or cur is None:
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        add, dele, path = parts
        if dele == "-":
            events[(cur, path)] = "binary"
        else:
            events[(cur, path)] = int(dele)
    return {"events": {f"{c[:12]}:{p}": v for (c, p), v in events.items() if isinstance(v, int) and v >= 20},
            "binary": [f"{c[:12]}:{p}" for (c, p), v in events.items() if v == "binary"],
            "commits": len(commits)}


def lane_leg():
    to = git(LANE, "rev-parse", "HEAD").stdout.strip()
    tool = run_tool(LANE, to)
    cnt = run_counter(LANE, to)
    tn, cn = norm(tool["events"]), norm(cnt["events"])
    sweep = numstat_sweep(LANE, to)
    reported = set()
    if cnt["events"]:
        for e in cnt["events"]:
            reported.add(f"{e['commit'][:12]}:{e['file']}")
    sweep_keys = set(sweep["events"])
    # byte-exact recheck of every reported event
    ore = []
    for e in (cnt["events"] or []):
        dele = parse_deleted_positional(bgit(LANE, "diff", "--no-renames", "--no-color", "--no-ext-diff",
                                             "-U0", e["commit"] + "^1", e["commit"], "--", e["file"]), e["file"])
        tip = blob_line_set(blob_bytes(LANE, to, e["file"])) or set()
        k = sum(1 for x in dele if x in tip)
        ore.append({"commit": e["commit"], "file": e["file"], "deleted_bytes": len(dele),
                    "restored_bytes": k,
                    "status_bytes": "restored" if k == len(dele) else ("unrestored" if k == 0 else "partial")})
    res = {
        "to": to,
        "tool_rc": tool["rc"], "counter_error": cnt["error"],
        "tool_vs_counter": "AGREE" if tn == cn and tool["rc"] == expected_rc(cnt["events"] or []) else "DISAGREE",
        "tool_events": len(tool["events"] or []), "counter_events": len(cnt["events"] or []),
        "missing_from_tool": sorted(map(str, (cn or set()) - (tn or set())))[:6],
        "extra_in_tool": sorted(map(str, (tn or set()) - (cn or set())))[:6],
        "tool_secs": tool["secs"], "counter_secs": cnt["secs"],
        "numstat_sweep_events": len(sweep["events"]),
        "in_counter_not_in_sweep": sorted(reported - sweep_keys),
        "in_sweep_not_in_counter": sorted(sweep_keys - reported),
        "sweep_binary": sweep["binary"][:10],
        "events": cnt["events"], "byte_recheck": ore,
        "sweep": sweep["events"],
    }
    with open(os.path.join(HERE, "lane.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k not in ("events", "sweep")}, indent=1))
    return 0


def main():
    global FIXTURES
    if len(sys.argv) > 2 and sys.argv[2] == "--lane":
        return lane_leg()
    if len(sys.argv) < 2:
        print("usage: run_fixtures.py <scratch-dir>", file=sys.stderr)
        return 2
    scratch = sys.argv[1]
    FIXTURES = os.path.join(scratch, "fx")
    os.makedirs(FIXTURES, exist_ok=True)
    results = []
    for fn in CASES:
        try:
            results.append(fn())
        except Exception as e:  # noqa: BLE001
            results.append({"case": fn.__name__, "error": f"{type(e).__name__}: {e}"})
    with open(os.path.join(HERE, "results.json"), "w") as fh:
        json.dump(results, fh, indent=1)
    rows = [("case", "tool_rc", "tool_events", "counter_events", "tool_vs_counter", "tool_vs_oracle",
             "counter_vs_oracle", "both_wrong", "tool_s", "counter_s")]
    for r in results:
        if "error" in r:
            rows.append((r["case"], "-", "-", "-", "ERROR", "-", "-", "-", "-", "-"))
            continue
        rows.append((r["case"], str(r["tool"]["rc"]), str(len(r["tool"]["events"] or [])),
                     str(len(r["counter"]["events"] or [])), r["tool_vs_counter"], r["tool_vs_oracle"],
                     r["counter_vs_oracle"], str(r["both_wrong_vs_oracle"]),
                     str(r["tool"]["secs"]), str(r["counter"]["secs"])))
    with open(os.path.join(HERE, "matrix.tsv"), "w") as fh:
        for row in rows:
            fh.write("\t".join(row) + "\n")
    print("\t".join(rows[0]))
    for row in rows[1:]:
        print("\t".join(row))
    dis = [r for r in results if r.get("tool_vs_counter") == "DISAGREE"]
    wrong = [r for r in results if r.get("both_wrong_vs_oracle")]
    print(f"\nfixtures={len(results)} disagreements={len(dis)} both_wrong={len(wrong)}")
    for r in dis:
        print("DISAGREE", r["case"], json.dumps(r["disagree_detail"])[:400])
    for r in wrong:
        print("BOTH_WRONG", r["case"], json.dumps(r["oracle_delta"])[:400])
    return 0


if __name__ == "__main__":
    sys.exit(main())
