#!/usr/bin/env python3
"""V2Tool seat driver: run the two new v4 selftest fixtures plus origin edge fixtures
against BOTH the base (v3, 438127bc) and tip (v4, 74558c71) append-only-audit.py."""
import importlib.util
import os
import subprocess
import sys
import time

S = os.path.dirname(os.path.abspath(__file__))
TIP = os.path.join(S, "lane", "tools", "append-only-audit.py")
BASE = os.path.join(S, "aoa_v3.py")
IDENT = ["-c", "user.name=v2tool", "-c", "user.email=v2tool@invalid", "-c", "commit.gpgsign=false"]
HEADER = "path\trule\tdeclared_at\tregion\tnote"
CONTRACT = "registry/append-only-contract.tsv"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


v4 = load(TIP, "aoa_v4")
v3 = load(BASE, "aoa_v3")


class Fixture:
    def __init__(self, root):
        self.d = os.path.join(root, f"fx{time.perf_counter_ns()}")
        os.makedirs(self.d)
        subprocess.run(["git", "-C", self.d, "init", "-q"], check=True)
        self.n = 0

    def commit(self, files):
        for name, body in files.items():
            p = os.path.join(self.d, name)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as fh:
                fh.write("".join(x + "\n" for x in body))
        subprocess.run(["git", "-C", self.d, "add", "-A"], check=True)
        self.n += 1
        subprocess.run(["git", "-C", self.d, *IDENT, "commit", "-q", "--allow-empty",
                        "-m", f"c{self.n}"], check=True)
        return subprocess.run(["git", "-C", self.d, "rev-parse", "HEAD"], check=True,
                              capture_output=True, text=True).stdout.strip()


def lines(tag, n):
    import random
    return [f"{tag} line {i} {random.randrange(1 << 32):08x}" for i in range(n)]


NOTES = ["# notes", "score.md is append-only below its head.",
         "The ## Axes and ## Plan heads of score.md are re-derived in place.",
         "know.md keeps its ## Errata region append-only.",
         "score.md gets appended to.", "score.md is not append-only.", "LOG.md is append-only."]
SCORE = "score.md\tA-corr\tNOTES.md:2\texempt=## Axes|## Plan@NOTES.md:3\tx"


def show(tag, res, want_commit=None):
    evs = res["events"]
    if want_commit:
        evs = [e for e in evs if e["commit"] == want_commit]
    print(f"  {tag}: exit={v4 and None} summary_events={res['summary']['events']} "
          f"bad_decl={res['summary']['bad_declarations']}")
    for e in evs:
        print(f"    {tag} event {e['commit'][:8]} deleted={e['deleted']} graded={e['graded']} "
              f"ungraded={e['ungraded']} status={e['status']}")


def run_both(label, build):
    print(f"== {label}")
    for name, mod in (("v3/base", v3), ("v4/tip", v4)):
        f = build()
        res = mod.audit(f.d, "HEAD")
        print(f"  [{name}] events:")
        for e in res["events"]:
            print(f"    {e['commit'][:8]} deleted={e['deleted']} graded={e['graded']} "
                  f"ungraded={e['ungraded']} status={e['status']}")


# ---- 1. exact copy of selftest t_launder_through_head
head, tail = ["# score", "## Axes"] + lines("h", 24), ["## Round 1"] + lines("d", 25)


def mk_launder():
    f = Fixture(S)
    f.commit({"NOTES.md": NOTES, CONTRACT: [HEADER, SCORE], "score.md": head + tail})
    f.commit({"score.md": head + tail[1:] + ["## Round 1", "kept"]})
    f.commit({"score.md": head + lines("regrow", 30) + ["## Round 1", "kept"]})
    return f


run_both("1. selftest t_launder_through_head (v4 expects graded=25 exit-1; v3 left ungraded)", mk_launder)

# ---- 2. exact copy of selftest t_binding_v4
print("== 2. selftest t_binding_v4 (expect oks [F,F,F,T] on v4)")
BIND_FILES = {"NOTES.md": ["# n", "the catalog is append-only", "score.md is not strictly append-only",
                           "LOG.md is append-only"],
              "notes/a.md": ["this file is append-only"], "notes/b.md": ["x"], "score.md": ["s"],
              "LOG.md": ["x"],
              CONTRACT: [HEADER, "LOG.md\tA\tNOTES.md:2\t*\tsubstring token",
                         "score.md\tA\tNOTES.md:3\t*\tnegation window",
                         "notes/*.md\tA\tnotes/a.md:1\t*\twildcard self-declaration",
                         "LOG.md\tA\tNOTES.md:4\t*\tbound"]}
for name, mod in (("v3/base", v3), ("v4/tip", v4)):
    f = Fixture(S)
    f.commit(BIND_FILES)
    res = mod.audit(f.d, "HEAD")
    print(f"  [{name}] oks={[d['ok'] for d in res['declarations']]} "
          f"exit={res['summary']['bad_declarations']}")

# ---- 3. NEW: origin must use full rev-list, not first-parent (side-branch birth under a
# dated title, merge moves the text under an exempt title, then deleted there)
print("== 3. merge/side-branch origin (v4 frozen definition: origin = full rev-list first")
print("   appearance => side birth under '## Round 9' is graded even when merged under '## Plan')")
s24 = lines("s", 24)
h24 = [l for l in head[2:]]


def mk_merge():
    f = Fixture(S)
    c1 = f.commit({"NOTES.md": NOTES, CONTRACT: [HEADER, SCORE],
                   "score.md": head + tail})
    subprocess.run(["git", "-C", f.d, "checkout", "-q", "-b", "side"], check=True)
    f.commit({"score.md": head + ["## Round 9"] + s24 + tail})
    subprocess.run(["git", "-C", f.d, "checkout", "-q", "-"], check=True)
    f.commit({"score.md": head + tail + ["mainline 0"]})
    subprocess.run(["git", "-C", f.d, *IDENT, "merge", "-q", "--no-edit", "-m", "m", "side"], check=True)
    # move the s-block under exempt ## Plan, dropping the Round 9 heading+block (event, dated -> graded)
    f.commit({"score.md": head + ["## Plan"] + s24 + tail + ["mainline 0"]})
    # delete the s-block there while ## Plan regrows: origin test
    f.commit({"score.md": head + ["## Plan"] + lines("regrow", 30) + tail + ["mainline 0"]})
    return f


f = mk_merge()
for name, mod in (("v3/base", v3), ("v4/tip", v4)):
    res = mod.audit(f.d, "HEAD")
    print(f"  [{name}]")
    for e in res["events"]:
        print(f"    {e['commit'][:8]} deleted={e['deleted']} graded={e['graded']} "
              f"ungraded={e['ungraded']} status={e['status']}")

# ---- 4. NEW: preamble-born text laundered under the exempt head (origin {None} -> graded)
p24 = lines("p", 24)


def mk_preamble():
    f = Fixture(S)
    f.commit({"NOTES.md": NOTES, CONTRACT: [HEADER, SCORE],
              "score.md": ["# score"] + p24 + head[1:] + tail})
    f.commit({"score.md": ["# score", "## Axes"] + p24 + head[2:] + tail})
    f.commit({"score.md": ["# score", "## Axes"] + lines("regrow", 30) + head[2:] + tail})
    return f


run_both("4. preamble-born text moved under ## Axes then deleted there (v4: graded)", mk_preamble)

# ---- 5. duplicate text born in BOTH sections at first appearance (registered limit:
# counts as exempt-born -> ungraded)
x24 = lines("x", 24)


def mk_dup():
    f = Fixture(S)
    f.commit({"NOTES.md": NOTES, CONTRACT: [HEADER, SCORE],
              "score.md": head + x24 + ["## Round 1"] + x24})
    f.commit({"score.md": head + lines("regrow", 30) + ["## Round 1"] + x24})
    return f


run_both("5. identical text born under ## Axes and ## Round 1, Axes copy deleted (limit: ungraded)", mk_dup)

# ---- 6. native head carve-out must survive (born exempt, rewritten in place -> ungraded)
def mk_native():
    f = Fixture(S)
    f.commit({"NOTES.md": NOTES, CONTRACT: [HEADER, SCORE], "score.md": head + tail})
    f.commit({"score.md": ["# score", "## Axes"] + lines("h2", 24) + tail})
    return f


run_both("6. native-head rewrite (v4 must KEEP the carve-out: ungraded=24)", mk_native)
print("done")
