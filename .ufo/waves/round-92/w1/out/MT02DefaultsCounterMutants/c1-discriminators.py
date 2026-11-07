#!/usr/bin/env python3
"""c1-discriminators.py - per-rule fixtures the frozen 9-case battery does not contain.

Every fixture is the pre-freeze candidate table (controls/c1-candidate-section.md, byte-equal to the
landed M1 section) with one rule-relevant change, plus the two candidate SOURCES rows, built into a
throwaway git repo under --work. Against the pristine counter every fixture must exit 1; a counter
that lost the matching rule is expected to exit 0, so a fixture DISCRIMINATES a mutant when the two
exits differ.

  X01-short-rows-12        MIN_ROWS     12 bound rows, supersedes still 14, engines 3
  X02-two-engines-14rows   MIN_ENGINES  7 llama.cpp + 7 ollama rows, supersedes 14, help_checked 7
  X03-help-checked-6       MIN_HELP     14 bound rows, 6 help-checked
  X04-empty-decision-cell  B1           R03's decision cell emptied (T03 re-homed to R02)
  X05-duplicate-pair       duplicates   R16 repeats (S594, 281)
  X06-moving-ref           B4/MOVING    a source row on the live /main/ ollama URL, sha pinned to live bytes
  X07-sha-mismatch         B5           a source row whose anchor sha256 is 64 f's
  X08-literal-not-at-line  B6           R03's literal cited at S593 line 633
  X09-name-not-in-literal  B7           R03's parameter cell holds a backticked token absent from the line
  X10-source-tier-C        B3           S594 tier A -> C
  X11-pin-not-in-url       B4           R09 pin v9.9.9 (T08 re-homed to R10)
  X12-engine-not-in-url    B4           R09 engine name goose (pin v0.40.11 kept)
  X13-derived-nonserver    H2           derived (flag `-`) row on tools/llama-bench at b12177
  X14-env-flag-with-h7     H3           R01 flag names the env var, a 7th help-checked row keeps h=7
  X15-supersede-membership  supersedes   R15 names T15 and T14 goes missing (13 real ids)
Usage: c1-discriminators.py --lane DIR --work DIR --binary PATH --section FILE --rows FILE
                             --counter FILE [--only NAME]
Prints `FIX <name> exit=<n>` (+ the counter's summary, and all rows with --only); exit 2 on setup
failure, else 0.
"""
import argparse, hashlib, re, shutil, subprocess, sys, tempfile
from pathlib import Path

BASE = "ed018ca0fa956c5052b3dc6b714a2cb72973da21"


def sh(*a, **k):
    return subprocess.run(list(a), capture_output=True, text=True, **k)


def row_of(sec, rid):
    return next(l for l in sec.split("\n") if l.startswith(f"| {rid} |"))


def cells_of(sec, rid):
    return [c.strip() for c in row_of(sec, rid).strip().strip("|").split("|")]


def render(cells):
    return "| " + " | ".join(cells) + " |"


def put(sec, rid, cells):
    return sec.replace(row_of(sec, rid), render(cells), 1)


def set_cell(sec, rid, i, v):
    c = cells_of(sec, rid)
    c[i] = v
    return put(sec, rid, c)


def append_after(sec, rid, cells):
    return sec.replace(row_of(sec, rid) + "\n",
                       row_of(sec, rid) + "\n" + render(cells) + "\n", 1)


def drop(sec, rid):
    return sec.replace(row_of(sec, rid) + "\n", "", 1)


def src_row(srcs, sid):
    return next(l for l in srcs.split("\n") if l.startswith(f"| {sid} |"))


def src_cells(srcs, sid):
    return [c.strip() for c in src_row(srcs, sid).strip().strip("|").split("|")]


def src_put(srcs, sid, cells):
    return srcs.replace(src_row(srcs, sid), render(cells), 1)


def src_add_alias(srcs, newid, fromid):
    r = src_row(srcs, fromid)
    new = r.replace(f"| {fromid} |", f"| {newid} |", 1)
    return srcs.replace(r, r + "\n" + new, 1)


def live(url):
    p = sh("curl", "-sfL", "--max-time", "60", url)
    return p.stdout if p.returncode == 0 else ""


LLAMA_URL = "https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/llama-bench/llama-bench.cpp"
OLLAMA_MAIN = "https://raw.githubusercontent.com/ollama/ollama/main/envconfig/config.go"


def live_row(sid, url, pin_word, engine_cell, flag, note):
    """A source row bound to the URL's live bytes plus one row that cites a number on one of its lines."""
    body = live(url)
    if not body:
        return None
    sha = hashlib.sha256(body.encode()).hexdigest()
    lines = body.split("\n")
    pick = None
    for i, l in enumerate(lines, 1):
        m = re.search(r"=\s*(\d+)", l)
        tok = re.search(r"([A-Za-z_][A-Za-z0-9_]{2,})\s*=", l)
        if m and tok and len(l.strip()) > 10:
            pick = (i, l.strip(), m.group(1), tok.group(1))
            break
    if pick is None:
        return None
    ln, lit, val, tok = pick
    src = (f"| {sid} | {note} — {url} | code | A | fixture | Tag, sha256 {sha}, opened2026-11-06: fixture | "
           f"fixture | mined | 2026-11-06 | on-release | fixture |")
    row = ["R18", engine_cell, f"probe `{tok}`", flag, val, sid, str(ln), f"`{lit}`", "T01", "fixture row"]
    return src, row


def build_cases(section, srcs):
    cases = []

    # X01 short table, supersedes and engines intact
    s = set_cell(section, "R09", 8, "T08 T10")
    s = set_cell(s, "R10", 8, "T09 T11 T12")
    for rid in ("R11", "R12", "R13"):
        s = drop(s, rid)
    cases.append(("X01-short-rows-12", s, srcs))

    # X02 two engines
    s = section
    for rid in ("R08", "R14", "R15"):
        s = drop(s, rid)
    r16 = cells_of(s, "R09"); r16[0] = "R16"; r16[5] = "S598"; r16[6] = "23"; r16[8] = "T13"
    r17 = cells_of(s, "R10"); r17[0] = "R17"; r17[5] = "S598"; r17[6] = "130"; r17[8] = "T14"
    s = append_after(s, "R13", r16)
    s = append_after(s, "R16", r17)
    cases.append(("X02-two-engines-14rows", s, src_add_alias(srcs, "S598", "S594")))

    # X03 six help-checked rows
    cases.append(("X03-help-checked-6", drop(section, "R07"), srcs))

    # X04 empty decision cell (T03 re-homed so only B1 can block)
    s = set_cell(section, "R02", 8, "T02 T03")
    s = set_cell(s, "R03", 9, "")
    cases.append(("X04-empty-decision-cell", s, srcs))

    # X05 duplicate (S594, 281) pair under a fresh id
    s = section
    r16 = cells_of(s, "R13"); r16[0] = "R16"; r16[8] = "T12"
    cases.append(("X05-duplicate-pair", append_after(s, "R15", r16), srcs))

    # X06 moving ref: live /main/ URL, sha pinned to the bytes it returns now
    got = live_row("S599", OLLAMA_MAIN, "main", "ollama main", "`OLLAMA_FIXTURE`",
                   "ollama envconfig/config.go at branch main")
    if got:
        src, row = got
        s = append_after(section, "R15", row)
        cases.append(("X06-moving-ref", s, srcs.replace(src_row(srcs, "S595"),
                                                        src_row(srcs, "S595") + "\n" + src, 1)))
    else:
        print("FIX X06-moving-ref SKIPPED fetch-failed")

    # X07 anchor sha256 wrong
    s2 = src_add_alias(srcs, "S598", "S594")
    c = src_cells(s2, "S598")
    c[5] = c[5][:c[5].index("sha256 ") + 7] + "f" * 64 + ", opened"
    s2 = src_put(s2, "S598", c)
    row = ["R18", "ollama v0.40.11", "parallel `NumParallel`", "`OLLAMA_NUM_PARALLEL`", "1", "S598",
           "277", "`NumParallel = Uint(\"OLLAMA_NUM_PARALLEL\", 1)`", "T11", "fixture row"]
    cases.append(("X07-sha-mismatch", append_after(section, "R15", row), s2))

    # X08 literal cited at a line that does not hold it
    s = set_cell(section, "R02", 8, "T02 T03")
    cases.append(("X08-literal-not-at-line", set_cell(s, "R03", 6, "633"), srcs))

    # X09 parameter token absent from the literal
    s = set_cell(section, "R02", 8, "T02 T03")
    cases.append(("X09-name-not-in-literal", set_cell(s, "R03", 2, "SSE ping `absent_token`"), srcs))

    # X10 source tier C
    s2 = src_set = src_cells(srcs, "S594")
    s2[3] = "C"
    cases.append(("X10-source-tier-C", section, src_put(srcs, "S594", s2)))

    # X11 pin not in URL (T08 re-homed)
    s = set_cell(section, "R09", 1, "ollama v9.9.9")
    s = set_cell(s, "R10", 8, "T09 T08")
    cases.append(("X11-pin-not-in-url", s, srcs))

    # X12 engine name not in URL
    s = set_cell(section, "R09", 1, "goose v0.40.11")
    s = set_cell(s, "R10", 8, "T09 T08")
    cases.append(("X12-engine-not-in-url", s, srcs))

    # X13 derived default bound to a non-server llama.cpp tool
    got = live_row("S599", LLAMA_URL, "b12177", "llama.cpp b12177", "-",
                   "llama.cpp tools/llama-bench at tag b12177")
    if got:
        src, row = got
        s = append_after(section, "R15", row)
        cases.append(("X13-derived-nonserver", s, srcs.replace(src_row(srcs, "S595"),
                                                              src_row(srcs, "S595") + "\n" + src, 1)))
    else:
        print("FIX X13-derived-nonserver SKIPPED fetch-failed")

    # X14 H3: an env-var flag cell, with a 7th help-checked row keeping h >= 7
    s = set_cell(section, "R01", 3, "`LLAMA_ARG_PORT`")
    s = set_cell(s, "R02", 8, "T02 T01")
    row = ["R18", "llama.cpp b12177", "router model limit `models_max`", "`--models-max`", "4", "S598",
           "703", "`int models_max = 4;`", "T06", "fixture row"]
    s = append_after(s, "R15", row)
    cases.append(("X14-env-flag-with-h7", s, src_add_alias(srcs, "S598", "S593")))

    # X15 supersedes: one cell names T15 (not a round-91 id) and T14 goes missing
    cases.append(("X15-supersede-membership", set_cell(section, "R15", 8, "T15"), srcs))
    return cases


def main():
    ap = argparse.ArgumentParser()
    for x in ("--lane", "--work", "--binary", "--section", "--rows", "--counter"):
        ap.add_argument(x, required=True)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    lane = Path(a.lane).resolve()
    counter = Path(a.counter).resolve()
    section = Path(a.section).read_text()
    rows = Path(a.rows).read_text()
    skill = sh("git", "-C", str(lane), "show", f"{BASE}:SKILL.md").stdout
    srcs = sh("git", "-C", str(lane), "show", f"{BASE}:corpus/SOURCES.md").stdout
    anchor = src_row(srcs, "S595")
    srcs = srcs.replace(anchor, anchor + "\n" + rows.rstrip("\n"), 1)
    work = Path(a.work)
    work.mkdir(parents=True, exist_ok=True)
    bad = 0
    for name, sec, sr in build_cases(section, srcs):
        if a.only and a.only != name:
            continue
        d = Path(tempfile.mkdtemp(prefix="r92-disc-", dir=work)).resolve()
        try:
            sh("git", "-C", str(d), "init", "-q")
            top = sh("git", "-C", str(d), "rev-parse", "--show-toplevel").stdout.strip()
            if Path(top).resolve() != d:
                print(f"FIX {name} SETUP-REFUSED toplevel={top}")
                bad += 1
                continue
            (d / "corpus").mkdir()
            (d / "SKILL.md").write_text(skill.rstrip("\n") + "\n\n" + sec)
            (d / "corpus" / "SOURCES.md").write_text(sr)
            sh("git", "-C", str(d), "add", "-A")
            c = sh("git", "-C", str(d), "-c", "user.name=fixture", "-c", "user.email=fixture@invalid",
                   "commit", "-q", "-m", name)
            if c.returncode != 0:
                print(f"FIX {name} SETUP-FAILED {c.stderr.strip()}")
                bad += 1
                continue
            p = sh(sys.executable, str(counter), "--repo", str(d), "--rev", "HEAD", "--binary", a.binary)
            out = p.stdout.splitlines()
            print(f"FIX {name} exit={p.returncode}")
            for l in out:
                if l.startswith("SERVER_DEFAULTS") or (a.only and l.startswith("SERVER_DEFAULT ")) \
                        or (not a.only and l.startswith("SERVER_DEFAULT ") and "bound=0" in l):
                    print("  " + l)
        finally:
            shutil.rmtree(d, ignore_errors=True)
    return 2 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
