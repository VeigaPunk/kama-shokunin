#!/usr/bin/env python3
"""X2Fixtures round-49 driver: build the five edge fixtures, run the audit at the build
commit, compare against expectations.json (written before any run).

Reads $S (scratch), writes results/*.json|*.txt and compare.json|compare.txt into
OUT=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X2Fixtures
"""
import json
import os
import subprocess
import sys
import time

S = os.environ["S"]
OUT = os.environ["OUT"]
TOOL = os.path.join(S, "tool.py")
FX = os.path.join(S, "fx")
CT = os.path.join(S, "contracts")
IDENT = ["-c", "user.name=r49x2", "-c", "user.email=r49x2@invalid", "-c", "commit.gpgsign=false"]
HEADER = "path\trule\tdeclared_at\tregion\tnote"
NOTES_EX = ["SCORE.md is append-only.",
            "The Axes head of SCORE.md is re-derived in place.",
            "The Axes and Planned heads of SCORE.md are re-derived in place."]
NOTES_LESSONS = ["The lessons under corpus/lessons are append-only."]
EX_ROW = "SCORE.md\tA-corr\tNOTES.md:1\texempt=## Axes@NOTES.md:2\tfixture"


def git(d, *args, inp=None):
    p = subprocess.run(["git", "-C", d, *args], input=inp, capture_output=True)
    if p.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {p.stderr.decode()[:400]}")
    return p.stdout.decode()


class Fixture:
    def __init__(self, name):
        self.d = os.path.join(FX, name)
        os.makedirs(self.d)
        git(self.d, "init", "-q")
        top = os.path.realpath(git(self.d, "rev-parse", "--show-toplevel").strip())
        if top != os.path.realpath(self.d):
            raise SystemExit(f"{name}: toplevel {top} != {self.d}")
        self.tags = {}
        self.n = 0

    def w(self, name, body):
        p = os.path.join(self.d, name)
        os.makedirs(os.path.dirname(p) or self.d, exist_ok=True)
        if isinstance(body, bytes):
            with open(p, "wb") as fh:
                fh.write(body)
        else:
            with open(p, "w", encoding="utf-8", newline="") as fh:
                fh.write("".join(x + "\n" for x in body))

    def commit(self, tag, files, moves=()):
        for name, body in files.items():
            self.w(name, body)
        for a, b in moves:
            git(self.d, "mv", a, b)
        git(self.d, "add", "-A")
        self.n += 1
        git(self.d, *IDENT, "commit", "-q", "--allow-empty", "-m", f"{tag} (r49 X2Fixtures)")
        self.tags[tag] = git(self.d, "rev-parse", "HEAD").strip()
        return self.tags[tag]

    def log(self):
        return git(self.d, "log", "--reverse", "--format=%h %s")


def L(tag, n, sfx):
    return [f"{tag}{i} r49{sfx}" for i in range(n)]


def parent_of(d, sha):
    p = subprocess.run(["git", "-C", d, "rev-parse", "--verify", "-q", sha + "^"], capture_output=True)
    return p.stdout.decode().strip() or None


def diff_of(d, sha, name):
    par = parent_of(d, sha)
    if par is None:
        return subprocess.run(["git", "-C", d, "show", "--no-renames", "-U0", "--format=", sha, "--", name],
                              capture_output=True, text=True).stdout
    return git(d, "diff", "--no-renames", "-U0", par, sha, "--", name)


def contract(fx_id, rows):
    p = os.path.join(CT, f"{fx_id}.tsv")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(HEADER + "\n" + "".join(r + "\n" for r in rows))
    return p


def run_tool(d, cpath):
    p = subprocess.run([sys.executable, TOOL, "--repo", d, "--to", "HEAD", "--contract", cpath,
                        "--json", "--threshold", "20"], capture_output=True, text=True, timeout=300)
    try:
        j = json.loads(p.stdout)
    except ValueError:
        j = None
    return p.returncode, j, p.stderr, p.stdout


SCENARIOS = {}


def scenario(fn):
    SCENARIOS[fn.__name__] = fn
    return fn


@scenario
def fence_heading_move():
    fx_id = "fence-heading-move"
    f = Fixture(fx_id)
    h, d, fz, g = L("h", 5, "a"), L("d", 5, "a"), L("f", 25, "a"), L("g", 30, "a")
    cpath = contract(fx_id, [EX_ROW])
    f.commit("c1", {"NOTES.md": NOTES_EX,
                    "SCORE.md": ["# score", "## Axes"] + h + ["## Round 1"] + d
                    + ["```", "## Axes"] + fz + ["```"]})
    f.commit("c2", {"SCORE.md": ["# score", "## Axes"] + h + fz + ["## Round 1"] + d
                    + ["```", "## Axes", "```"]})
    f.commit("c3", {"SCORE.md": ["# score", "## Axes"] + h + g + ["## Round 1"] + d
                    + ["```", "## Axes", "```"]})
    return fx_id, f, cpath


@scenario
def fence_control_no_fence():
    fx_id = "fence-control-no-fence"
    f = Fixture(fx_id)
    h, d, fz, g = L("h", 5, "a"), L("d", 5, "a"), L("f", 25, "a"), L("g", 30, "a")
    cpath = contract(fx_id, [EX_ROW])
    f.commit("c1", {"NOTES.md": NOTES_EX,
                    "SCORE.md": ["# score", "## Axes"] + h + ["## Round 1"] + d + fz})
    f.commit("c2", {"SCORE.md": ["# score", "## Axes"] + h + fz + ["## Round 1"] + d})
    f.commit("c3", {"SCORE.md": ["# score", "## Axes"] + h + g + ["## Round 1"] + d})
    return fx_id, f, cpath


@scenario
def star_control_star_only():
    fx_id = "star-control-star-only"
    f = Fixture(fx_id)
    cpath = contract(fx_id, ["SCORE.md\tA-corr\tNOTES.md:1\t*\twhole-file row only"])
    o, o2, d3 = L("orig", 25, "e"), L("new", 25, "e"), L("d", 3, "e")
    f.commit("c1", {"NOTES.md": NOTES_EX,
                    "SCORE.md": ["# score", "## Axes"] + o + ["## Round 1"] + d3})
    f.commit("c2", {"SCORE.md": ["# score", "## Axes"] + o2 + ["## Round 1"] + d3})
    return fx_id, f, cpath


@scenario
def crlf_dated_to_head():
    fx_id = "crlf-dated-to-head"
    f = Fixture(fx_id)
    cpath = contract(fx_id, [EX_ROW])
    hraw = "".join(x + "\n" for x in L("h", 5, "c")).encode()
    crlf = "".join(f"d{i} r49c\r\n" for i in range(25)).encode()
    grow = "".join(x + "\n" for x in L("g", 30, "c")).encode()
    f.commit("c1", {"NOTES.md": NOTES_EX,
                    "SCORE.md": b"# score\n## Axes\n" + hraw + b"## Round 1\n" + crlf})
    f.commit("c2", {"SCORE.md": b"# score\n## Axes\n" + hraw + crlf + b"## Round 1\n"})
    f.commit("c3", {"SCORE.md": b"# score\n## Axes\n" + hraw + grow + b"## Round 1\n"})
    return fx_id, f, cpath


@scenario
def crlf_normalized_move():
    fx_id = "crlf-normalized-move"
    f = Fixture(fx_id)
    cpath = contract(fx_id, [EX_ROW])
    hraw = "".join(x + "\n" for x in L("h", 5, "c")).encode()
    crlf = "".join(f"d{i} r49c\r\n" for i in range(25)).encode()
    lf = "".join(f"d{i} r49c\n" for i in range(25)).encode()
    grow = "".join(x + "\n" for x in L("g", 30, "c")).encode()
    f.commit("c1", {"NOTES.md": NOTES_EX,
                    "SCORE.md": b"# score\n## Axes\n" + hraw + b"## Round 1\n" + crlf})
    f.commit("c2", {"SCORE.md": b"# score\n## Axes\n" + hraw + lf + b"## Round 1\n"})
    f.commit("c3", {"SCORE.md": b"# score\n## Axes\n" + hraw + grow + b"## Round 1\n"})
    return fx_id, f, cpath


@scenario
def crlf_normalized_subthreshold():
    fx_id = "crlf-normalized-subthreshold"
    f = Fixture(fx_id)
    cpath = contract(fx_id, [EX_ROW])
    hraw = "".join(x + "\n" for x in L("h", 5, "c")).encode()
    crlf = [f"d{i} r49c\r\n" for i in range(25)]
    lf = [f"d{i} r49c\n" for i in range(25)]
    grow = "".join(x + "\n" for x in L("g", 30, "c")).encode()
    f.commit("c1", {"NOTES.md": NOTES_EX,
                    "SCORE.md": b"# score\n## Axes\n" + hraw + b"## Round 1\n"
                    + "".join(crlf).encode()})
    f.commit("c2", {"SCORE.md": b"# score\n## Axes\n" + hraw + "".join(lf[:13]).encode()
                    + b"## Round 1\n" + "".join(crlf[13:]).encode()})
    f.commit("c3", {"SCORE.md": b"# score\n## Axes\n" + hraw + "".join(lf).encode()
                    + b"## Round 1\n"})
    f.commit("c4", {"SCORE.md": b"# score\n## Axes\n" + hraw + grow + b"## Round 1\n"})
    return fx_id, f, cpath


@scenario
def preamble_to_head_dropped():
    fx_id = "preamble-to-head-dropped"
    f = Fixture(fx_id)
    cpath = contract(fx_id, [EX_ROW])
    p, h, d3, g = L("p", 25, "b"), L("h", 5, "b"), L("d", 3, "b"), L("g", 30, "b")
    f.commit("c1", {"NOTES.md": NOTES_EX,
                    "SCORE.md": ["# score"] + p + ["## Axes"] + h + ["## Round 1"] + d3})
    f.commit("c2", {"SCORE.md": ["# score", "## Axes"] + h + p + ["## Round 1"] + d3})
    f.commit("c3", {"SCORE.md": ["# score", "## Axes"] + h + g + ["## Round 1"] + d3})
    return fx_id, f, cpath


@scenario
def two_rows_two_titles():
    fx_id = "two-rows-two-titles"
    f = Fixture(fx_id)
    rows = ["SCORE.md\tA-corr\tNOTES.md:1\texempt=## Axes@NOTES.md:3\trow A",
            "SCORE.md\tA-corr\tNOTES.md:1\texempt=## Planned@NOTES.md:3\trow B"]
    cpath = contract(fx_id, rows)
    h, q, g = L("h", 5, "d"), L("q", 25, "d"), L("g", 30, "d")
    f.commit("c1", {"NOTES.md": NOTES_EX,
                    "SCORE.md": ["# score", "## Axes"] + h + ["## Planned"] + q})
    f.commit("c2", {"SCORE.md": ["# score", "## Axes"] + h + q + ["## Planned"]})
    f.commit("c3", {"SCORE.md": ["# score", "## Axes"] + h + g + ["## Planned"]})
    return fx_id, f, cpath


@scenario
def star_plus_exempt_row():
    fx_id = "star-plus-exempt-row"
    f = Fixture(fx_id)
    rows = ["SCORE.md\tA-corr\tNOTES.md:1\t*\twhole-file row",
            "SCORE.md\tA-corr\tNOTES.md:1\texempt=## Axes@NOTES.md:2\texempt row"]
    cpath = contract(fx_id, rows)
    o, o2, d3 = L("orig", 25, "e"), L("new", 25, "e"), L("d", 3, "e")
    f.commit("c1", {"NOTES.md": NOTES_EX,
                    "SCORE.md": ["# score", "## Axes"] + o + ["## Round 1"] + d3})
    f.commit("c2", {"SCORE.md": ["# score", "## Axes"] + o2 + ["## Round 1"] + d3})
    return fx_id, f, cpath


@scenario
def only_plus_exempt_rows():
    fx_id = "only-plus-exempt-rows"
    f = Fixture(fx_id)
    notes = ["SCORE.md is append-only.",
             "SCORE.md keeps its Errata region append-only.",
             "The Axes head of SCORE.md is re-derived in place."]
    rows = ["SCORE.md\tA-corr\tNOTES.md:1\tonly=## Errata@NOTES.md:2\tonly row",
            "SCORE.md\tA-corr\tNOTES.md:1\texempt=## Axes@NOTES.md:3\texempt row"]
    cpath = contract(fx_id, rows)
    z, z2, e3 = L("zed", 25, "i"), L("znew", 25, "i"), L("e", 3, "i")
    f.commit("c1", {"NOTES.md": notes,
                    "SCORE.md": ["# score", "## Axes"] + z + ["## Errata"] + e3})
    f.commit("c2", {"SCORE.md": ["# score", "## Axes"] + z2 + ["## Errata"] + e3})
    return fx_id, f, cpath


@scenario
def rename_declared_away():
    fx_id = "rename-declared-away"
    f = Fixture(fx_id)
    cpath = contract(fx_id, [EX_ROW])
    a, d = L("a", 25, "f"), L("d", 25, "f")
    f.commit("c1", {"NOTES.md": NOTES_EX,
                    "SCORE.md": ["# score", "## Axes"] + a + ["## Round 1"] + d})
    f.commit("c2", {}, moves=[("SCORE.md", "OTHER.md")])
    return fx_id, f, cpath


@scenario
def rename_within_wildcard():
    fx_id = "rename-within-wildcard"
    f = Fixture(fx_id)
    cpath = contract(fx_id, ["corpus/lessons/*.md\tA-corr\tNOTES.md:1\t*\tfixture"])
    f.commit("c1", {"NOTES.md": NOTES_LESSONS, "corpus/lessons/r1.md": L("r", 30, "g")})
    f.commit("c2", {}, moves=[("corpus/lessons/r1.md", "corpus/lessons/r2.md")])
    return fx_id, f, cpath


@scenario
def rename_into_declared():
    fx_id = "rename-into-declared"
    f = Fixture(fx_id)
    cpath = contract(fx_id, [EX_ROW])
    f.commit("c1", {"NOTES.md": NOTES_EX, "DRAFT.md": ["# draft", "## Axes"] + L("a", 25, "h")})
    f.commit("c2", {}, moves=[("DRAFT.md", "SCORE.md")])
    return fx_id, f, cpath


def compare(exp, runs, mtimes):
    out = []
    for sc in exp["scenarios"]:
        fx_id = sc["id"]
        r = runs[fx_id]
        pred, j, code = sc["predicted"], r["json"], r["exit"]
        tags = r["tags"]
        checks = []
        if j is None:
            checks.append(("json", False, None, None))
            out.append({"id": fx_id, "agree": False, "checks": checks})
            continue
        want = {tags[e["tag"]]: {k: v for k, v in e.items() if k != "tag"} for e in pred["events"]}
        got = {e["commit"]: e for e in j["events"]}
        checks.append(("event_set", set(want) == set(got),
                       sorted(t[:8] for t in want), sorted(c[:8] for c in got)))
        for sha, fields in want.items():
            e = got.get(sha)
            bad = {k: (fields[k], None) for k in fields} if e is None else \
                {k: (fields[k], e.get(k)) for k in fields if e.get(k) != fields[k]}
            checks.append((f"event {[t for t, s in tags.items() if s == sha][0]}", not bad,
                           fields, {k: v for k, v in (e or {}).items() if k != "commit"} if not bad else bad))
        checks.append(("exit", code == pred["exit"], pred["exit"], code))
        checks.append(("vanished", (j.get("vanished") or []) == pred["vanished"],
                       pred["vanished"], j.get("vanished")))
        checks.append(("unmatched_patterns", (j.get("unmatched_patterns") or []) == pred["unmatched_patterns"],
                       pred["unmatched_patterns"], j.get("unmatched_patterns")))
        checks.append(("bad_declarations", (j.get("summary") or {}).get("bad_declarations")
                       == pred["bad_declarations"],
                       pred["bad_declarations"], (j.get("summary") or {}).get("bad_declarations")))
        agree = all(c[1] for c in checks)
        # intended comparison (report only): same mechanical test against sc["intended"]
        iw = {tags[e["tag"]]: {k: v for k, v in e.items() if k != "tag"} for e in sc["intended"]["events"]}
        ig = got
        intended_ok = (set(iw) == set(ig) and all(
            all(e.get(k) == v for k, v in f.items()) for sha, f in iw.items() for e in [ig[sha]])
            and code == sc["intended"]["exit"])
        out.append({"id": fx_id, "agree": agree, "intended_met": intended_ok,
                    "checks": [{"check": c[0], "ok": c[1], "want": c[2], "got": c[3]} for c in checks],
                    "predicted_events": pred["events"], "intended_events": sc["intended"]["events"],
                    "actual_events": [{"tag": [t for t, s in tags.items() if s == e["commit"]][0],
                                       "commit": e["commit"], "deleted": e["deleted"], "graded": e["graded"],
                                       "ungraded": e["ungraded"], "status": e["status"],
                                       "restored_max": e["restored_max"], "held_at_to": e["held_at_to"]}
                                      for e in j["events"]],
                    "tags": tags})
    return out


def main():
    os.makedirs(FX, exist_ok=True)
    os.makedirs(CT, exist_ok=True)
    os.makedirs(os.path.join(OUT, "results"), exist_ok=True)
    exp_path = os.path.join(OUT, "expectations.json")
    exp_mtime = os.path.getmtime(exp_path)
    with open(exp_path) as fh:
        exp = json.load(fh)
    add_path = os.path.join(OUT, "expectations-addendum.json")
    add_mtime = None
    if os.path.isfile(add_path):
        add_mtime = os.path.getmtime(add_path)
        with open(add_path) as fh:
            add = json.load(fh)
        exp["scenarios"] = exp["scenarios"] + add["scenarios"]
    runs, first_run, run_times = {}, None, []
    for fid, fn in [(s["id"], SCENARIOS[s["id"].replace("-", "_")]) for s in exp["scenarios"]]:
        fx_id, f, cpath = fn()
        code, j, err, raw = run_tool(f.d, cpath)
        if first_run is None:
            first_run = time.time()
        run_times.append((fx_id, time.time()))
        runs[fx_id] = {"exit": code, "json": j, "stderr": err, "tags": f.tags}
        snap = [f"fixture {fx_id} at {f.d} (temporary)", "", "git log:", f.log()]
        for tag, sha in f.tags.items():
            for name in ("SCORE.md", "corpus/lessons/r1.md", "DRAFT.md"):
                dif = diff_of(f.d, sha, name)
                if dif.strip():
                    snap += ["", f"--- diff {tag} {name} ({sha[:12]}) ---", dif]
        for name in ("SCORE.md", "NOTES.md", "corpus/lessons/r1.md", "corpus/lessons/r2.md",
                     "OTHER.md", "DRAFT.md"):
            p = os.path.join(f.d, name)
            if os.path.isfile(p):
                with open(p, "rb") as fh:
                    body = fh.read()
                snap += ["", f"--- {name} at tip ({len(body)} bytes) ---",
                         repr(body) if len(body) < 400 else repr(body[:200]) + " ... " + repr(body[-120:])]
        contract_text = open(cpath).read()
        snap += ["", "--- contract ---", contract_text]
        with open(os.path.join(OUT, "results", f"{fx_id}.txt"), "w") as fh:
            fh.write(f"fixture {fx_id}\nexit {code}\nstderr {err.strip()[:400]}\n\n")
            fh.write("\n".join(snap) + "\n")
        with open(os.path.join(OUT, "results", f"{fx_id}.json"), "w") as fh:
            json.dump({"fixture": fx_id, "exit": code, "stderr": err, "tags": f.tags,
                       "audit": j, "raw_stdout_sha256": __import__("hashlib").sha256(raw.encode()).hexdigest()},
                      fh, indent=1)
        print(f"{fx_id}: exit {code} events {len((j or {}).get('events') or [])}")
    ctl_path = os.path.join(OUT, "controls.json")
    ctl_doc = None
    if os.path.isfile(ctl_path):
        with open(ctl_path) as fh:
            ctl = json.load(fh)
        ctl_runs, ctl_mtime = {}, os.path.getmtime(ctl_path)
        ctl_first = None
        for fid, fn in [(s["id"], SCENARIOS[s["id"].replace("-", "_")]) for s in ctl["scenarios"]]:
            fx_id, f, cpath = fn()
            code, j, err, raw = run_tool(f.d, cpath)
            if ctl_first is None:
                ctl_first = time.time()
            ctl_runs[fx_id] = {"exit": code, "json": j, "stderr": err, "tags": f.tags}
            with open(os.path.join(OUT, "results", f"{fx_id}.json"), "w") as fh:
                json.dump({"fixture": fx_id, "exit": code, "stderr": err, "tags": f.tags, "audit": j}, fh, indent=1)
            lines = [f"fixture {fx_id} (control)", f"git log:", f.log()]
            for tag, sha in f.tags.items():
                dif = diff_of(f.d, sha, "SCORE.md")
                if dif.strip():
                    lines += ["", f"--- diff {tag} SCORE.md ({sha[:12]}) ---", dif]
            lines += ["", "--- contract ---", open(cpath).read()]
            with open(os.path.join(OUT, "results", f"{fx_id}.txt"), "w") as fh:
                fh.write("\n".join(lines) + "\n")
            print(f"{fx_id} (control): exit {code} events {len((j or {}).get('events') or [])}")
        ctl_doc = {"controls_path": ctl_path, "controls_mtime": ctl_mtime,
                   "controls_before_own_run": ctl_mtime < ctl_first,
                   "agree": sum(r["agree"] for r in compare(ctl, ctl_runs, {})),
                   "total": len(ctl["scenarios"]),
                   "scenarios": compare(ctl, ctl_runs, {})}
    res = compare(exp, runs, {"expectations": exp_mtime, "first_run": first_run})
    doc = {"seat": "X2Fixtures", "round": 49, "tool": TOOL, "controls": ctl_doc,
           "tool_source_commit": exp["tool_source_commit"], "tool_sha256": exp["tool_sha256"],
           "expectations_path": exp_path, "expectations_mtime": exp_mtime, "first_run_mtime": first_run,
           "expectations_before_runs": exp_mtime < first_run,
           "addendum": add_path if add_mtime else None, "addendum_mtime": add_mtime,
           "addendum_before_runs": (add_mtime < first_run) if add_mtime else None,
           "run_times": run_times,
           "agree": sum(r["agree"] for r in res), "total": len(res),
           "scenarios": res}
    with open(os.path.join(OUT, "compare.json"), "w") as fh:
        json.dump(doc, fh, indent=1)
    lines = [f"expectations_mtime={exp_mtime} first_run_mtime={first_run} "
             f"expectations_before_runs={exp_mtime < first_run}",
             f"agree={doc['agree']}/{doc['total']}", ""]
    for r in res:
        lines.append(f"{r['id']}: agree={r['agree']} intended_met={r['intended_met']}")
        for c in r["checks"]:
            if not c["ok"]:
                lines.append(f"  DISAGREE {c['check']}: want {c['want']!r} got {c['got']!r}")
        lines.append(f"  actual {[(e['tag'], e['deleted'], e['graded'], e['ungraded'], e['status']) for e in r['actual_events']]}")
        lines.append(f"  predicted {[(e['tag'], e['deleted'], e['graded'], e['ungraded'], e['status']) for e in r['predicted_events']]}")
        lines.append(f"  intended {[(e['tag'], e.get('deleted'), e.get('graded'), e.get('ungraded'), e.get('status')) for e in r['intended_events']]}")
    with open(os.path.join(OUT, "compare.txt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    if ctl_doc:
        lines.append("")
        lines.append(f"controls agree={ctl_doc['agree']}/{ctl_doc['total']}")
        for r in ctl_doc["scenarios"]:
            lines.append(f"{r['id']}: agree={r['agree']} intended_met={r['intended_met']}")
            for c in r["checks"]:
                if not c["ok"]:
                    lines.append(f"  DISAGREE {c['check']}: want {c['want']!r} got {c['got']!r}")
            lines.append(f"  actual {[(e['tag'], e['deleted'], e['graded'], e['ungraded'], e['status']) for e in r['actual_events']]}")
            lines.append(f"  predicted {[(e['tag'], e['deleted'], e['graded'], e['ungraded'], e['status']) for e in r['predicted_events']]}")
    with open(os.path.join(OUT, "compare.txt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if doc["agree"] == doc["total"] else 1


if __name__ == "__main__":
    sys.exit(main())
