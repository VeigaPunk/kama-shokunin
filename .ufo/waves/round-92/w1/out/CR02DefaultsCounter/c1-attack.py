#!/usr/bin/env python3
"""CR02DefaultsCounter attack battery against tools/round92-server-defaults.py (frozen C1 counter).

Each case: a fixture git repo under --work holding SKILL.md and corpus/SOURCES.md at M1 with one
(or, where labelled, two) mutation(s), then the frozen counter is run on it unchanged.
Prints CASE <name> want=<exit> got=<exit> plus the summary line and every unbound row.
"""
import argparse, shutil, subprocess, sys, tempfile
from pathlib import Path

HEAD = "## Serving defaults (round 92 revision)"


def sh(*a, **k):
    return subprocess.run(list(a), capture_output=True, text=True, **k)


def main():
    ap = argparse.ArgumentParser()
    for x in ("--lane", "--work", "--binary", "--rev"):
        ap.add_argument(x, required=True)
    a = ap.parse_args()
    lane = Path(a.lane).resolve()
    counter = lane / "tools" / "round92-server-defaults.py"
    skill = sh("git", "-C", str(lane), "show", f"{a.rev}:SKILL.md").stdout
    srcs = sh("git", "-C", str(lane), "show", f"{a.rev}:corpus/SOURCES.md").stdout
    # sanity: the section and its rows must be the M1 ones
    assert HEAD in skill, "section absent at rev"

    sec_start = skill.index(HEAD)
    section = skill[sec_start:]
    rows = {l.split("|")[1].strip(): l for l in section.split("\n") if l.startswith("| R")}

    def row(rid):
        return rows[rid]

    def swap(rid, **changes):
        r = row(rid)
        cells = r.split(" | ")
        # cells: ['| R01', 'llama.cpp b12177', 'param', 'flag', 'value', 'S..', 'line', 'lit', 'sup', 'decision |']
        idx = dict(engine=1, name=2, flag=3, value=4, sid=5, line=6, lit=7, sup=8, decision=9)
        for k, v in changes.items():
            cells[idx[k]] = v
        return " | ".join(cells)

    def put(sec, rid, new):
        return sec.replace(row(rid), new, 1)

    def after_section(sec, extra):
        return sec.rstrip("\n") + "\n" + extra + "\n"

    cases = []
    cases.append(("P1-baseline-M1", section, 0))
    # F1 unit blind spot: keep-alive default is 5 MINUTES; value cell says 5 s
    cases.append(("F1-unit-keepalive-5s", put(section, "R10", swap("R10", value="5 s")), 0))
    # F2 substring blind spot: MaxQueue default is 512; value cell says 12
    cases.append(("F2-substring-maxqueue-12", put(section, "R13", swap("R13", value="12")), 0))
    # F2b substring on the vLLM engine-ready default 600 -> 6
    cases.append(("F2b-substring-engine-ready-6", put(section, "R14", swap("R14", value="6 s")), 0))
    # F3 wrong option, same numeric help default (-1): --parallel -> -t (threads)
    cases.append(("F3-wrong-flag-same-default", put(section, "R07", swap("R07", flag="`-t`")), 0))
    # F4 wrong line semantics: line 129 (the assignment) -> 127 (the printf format string)
    cases.append(("F4-log-line-not-assignment",
                  put(section, "R08", swap("R08", line="127",
                                           lit='`using n_parallel = 4 and kv_unified = true`')), 0))
    # F5 duplicate (S,line) pair hidden by a numeric alias 632 -> 0632
    dup = "| R16 | llama.cpp b12177 | listen port `port` | `--port` | 9931 | S593 | 0632 | `int32_t port                = 9931;` | T01 | clone of R01 at the same source line |"
    cases.append(("F5-duplicate-line-alias", after_section(section, dup), 0))
    # F6 a rendered but uncounted row (one leading space) stating a wrong default
    ind = " | R16 | llama.cpp b12177 | listen port `port` | `--port` | 9999 | S593 | 632 | `int32_t port                = 9931;` | T01 | forged indented row |"
    cases.append(("F6-indented-row-uncounted", after_section(section, ind), 0))
    # F7 H2 bypass: a fabricated "derived" default on an arbitrary /tools/server/ line (272, a 403 handler)
    fab = '| R16 | llama.cpp b12177 | fabricated derived default `res_403` | - | 4 | S597 | 272 | `ctx_http.get ("/cors-proxy",      ex_wrapper(res_403));` | T01 | forged derived default |'
    cases.append(("F7-fabricated-derived", after_section(section, fab), 0))
    # F8 engine-name dodge: "llama b12177" is not "llama.cpp", so H1/H2/H3 are skipped; value 8 for 8192
    #    plus one help-checked row (R16) so help_checked stays 7 and the h>=7 gate still passes
    f8 = put(section, "R04", swap("R04", engine="llama b12177", value="8"))
    f8 = after_section(f8, "| R16 | llama.cpp b12177 | HTTP read timeout `timeout_read` | `--timeout` | 3600 s | S593 | 0634 | `int32_t timeout_read        = 3600;` | T02 | helps keep help_checked at 7 |")
    cases.append(("F8-engine-name-dodge", f8, 0))
    # F9 decorative pin: engine pin token truncated to a substring of the URL
    cases.append(("F9-pin-substring", put(section, "R01", swap("R01", engine="llama.cpp b121")), 0))
    # F11 alias cell: first option checked, a wrong second option in the same cell is not
    cases.append(("F11-second-alias-unchecked", put(section, "R02", swap("R02", flag="`--timeout` `-t`")), 0))
    # F10 false red: a CORRECT row for a non-numeric default (--reuse-port default disabled / false)
    nonnum = "| R16 | llama.cpp b12177 | reuse_port `reuse_port` | `--reuse-port` | false | S593 | 633 | `bool    reuse_port          = false;` | T01 | a correct non-numeric default |"
    cases.append(("F10-correct-non-numeric", after_section(section, nonnum), 1))

    Path(a.work).mkdir(parents=True, exist_ok=True)
    bad = 0
    mis = 0
    for name, sec, want in cases:
        d = Path(tempfile.mkdtemp(prefix="r92-c1a-", dir=a.work)).resolve()
        try:
            sh("git", "-C", str(d), "init", "-q")
            top = sh("git", "-C", str(d), "rev-parse", "--show-toplevel").stdout.strip()
            if Path(top).resolve() != d:
                print(f"CASE {name} SETUP-REFUSED toplevel={top!r}")
                bad += 1
                continue
            (d / "corpus").mkdir()
            # SKILL.md: M1 prefix up to the section, then the mutated section
            prefix = skill[:sec_start]
            (d / "SKILL.md").write_text(prefix + sec)
            (d / "corpus" / "SOURCES.md").write_text(srcs)
            sh("git", "-C", str(d), "add", "-A")
            c = sh("git", "-C", str(d), "-c", "user.name=fixture", "-c", "user.email=fixture@invalid",
                   "commit", "-q", "-m", name)
            if c.returncode != 0:
                print(f"CASE {name} SETUP-FAILED {c.stderr.strip()}")
                bad += 1
                continue
            p = sh(sys.executable, str(counter), "--repo", str(d), "--rev", "HEAD", "--binary", a.binary)
            got = p.returncode
            summary = [l for l in p.stdout.splitlines() if l.startswith("SERVER_DEFAULTS")]
            whys = [l for l in p.stdout.splitlines() if l.startswith("SERVER_DEFAULT ") and "bound=0" in l]
            flag = "as-expected" if got == want else "UNEXPECTED"
            mis += got != want
            print(f"CASE {name} want={want} got={got} {flag}")
            for l in summary + whys:
                print("   " + l)
            if p.stderr.strip():
                print("   stderr: " + p.stderr.strip().splitlines()[-1])
        finally:
            shutil.rmtree(d, ignore_errors=True)
    print(f"C1_ATTACK cases={len(cases)} as_expected={len(cases)-bad-mis}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
