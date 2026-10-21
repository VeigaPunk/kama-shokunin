#!/usr/bin/env python3
"""RevControls: control-identity probe for tools/report-landing-audit.py.

Each case builds fresh fixture repos in a temp dir under /tmp (no inherited GIT_*,
GIT_CONFIG_GLOBAL=/dev/null, GIT_CONFIG_NOSYSTEM=1), runs the FROZEN auditor
(4fe9339f blob) and a SNAPSHOT of the live working-tree auditor on identical inputs,
and compares exit status, stdout and stderr. Never touches the lane or fleet repos.
"""
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

OUT_FILE = pathlib.Path("/tmp/kama-r23-RevControls/controls-output.txt")
FROZEN_SRC = pathlib.Path("/tmp/kama-r23-RevControls/frozen-audit.py")
LIVE_SRC = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py")
WORK = pathlib.Path(tempfile.mkdtemp(prefix="revcontrols-", dir="/tmp"))
FROZEN = WORK / "frozen-audit.py"
CURRENT = WORK / "current-audit-snapshot.py"
shutil.copyfile(FROZEN_SRC, FROZEN)
shutil.copyfile(LIVE_SRC, CURRENT)
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", PYTHONDONTWRITEBYTECODE="1")
FOREIGN = "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad"  # real llama.cpp commit; absent from fixtures
FAKE = "1234567890abcdef1234567890abcdef12345678"
SCHEME = f"https://github.com/ggml-org/llama.cpp/blob/{FOREIGN}/tools/server/README.md"
CENSUS = f"github.com/ggml-org/llama.cpp/blob/{FOREIGN}/tools/server/README.md"
OTHER = f"https://github.com/ggml-org/llama.cpp/blob/{FOREIGN}/tools/server/other.cc"
GOOD_ROW = ("| S001 | llama.cpp README — {url} | docs | A | fixture | fixture | fixture "
            "| mined | 2026-10-21 | on-release | — |")
SHORT_ROW = ("| S001 | llama.cpp README — {url} | docs | A | fixture | fixture | fixture "
             "| mined | 2026-10-21 | on-release |")


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def git(repo, *args, env=None, input=None):
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          env={**ENV, **(env or {})}, input=input)
    if proc.returncode:
        raise SystemExit(f"fixture git {args!r} in {repo}: {proc.stderr.decode(errors='replace')}")
    return proc.stdout.decode("utf-8", errors="replace")


def who(author, when, committed=None):
    return {"GIT_AUTHOR_NAME": author, "GIT_COMMITTER_NAME": author,
            "GIT_AUTHOR_EMAIL": "a@x", "GIT_COMMITTER_EMAIL": "a@x",
            "GIT_AUTHOR_DATE": f"@{when} +0000",
            "GIT_COMMITTER_DATE": f"@{committed or when} +0000"}


def commit(repo, msg, author, when, committed=None, path="f", body=None):
    target = pathlib.Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "a", encoding="utf-8") as fh:
        fh.write((msg if body is None else body) + "\n")
    env = who(author, when, committed)
    git(repo, "add", path, env=env)
    git(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg, env=env)
    return git(repo, "rev-parse", "HEAD").strip()


def make_repo(path, config=None):
    path.mkdir(parents=True)
    git(path, "init", "-q", "-b", "master")
    for key, value in (config or {}).items():
        git(path, "config", key, value)
    return path


def base_lane(root, foreign="someone", config=None):
    lane = make_repo(root / "lane", config)
    c = {}
    c["A"] = commit(lane, "round-1: work", "kama-shokunin", 1000)
    c["B"] = commit(lane, "round-1:measure", "kama-shokunin", 1100)
    c["C"] = commit(lane, "checkpoint(r1) save", "kama-shokunin", 1150)
    c["D"] = commit(lane, "round-1: rebased", "kama-shokunin", 1155, committed=5000)
    c["X"] = commit(lane, "round-1: foreign author", foreign, 1160)
    commit(lane, "round-1: lookalike", "kama-shokunin-extra", 1161)
    commit(lane, "round-10: other round", "kama-shokunin", 1170)
    commit(lane, "xround-1: prefixed", "kama-shokunin", 1171)
    c["E"] = commit(lane, "round-1: at cutoff", "kama-shokunin", 1200)
    c["L"] = commit(lane, "round-1: late advice", "kama-shokunin", 1300)
    return lane, c


def fleet_with(root, report, config=None, when=1200):
    fleet = make_repo(root / "fleet", config)
    rel = pathlib.Path(".ufo/reports/round-1/kama.md")
    (fleet / rel).parent.mkdir(parents=True)
    (fleet / rel).write_bytes(report)
    env = who("fleet", when)
    git(fleet, "add", str(rel), env=env)
    git(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: kama report", env=env)
    return fleet


def empty_fleet(root):
    fleet = make_repo(root / "fleet")
    commit(fleet, "fleet readme", "fleet", 900, path="README")
    return fleet


def rpt(*lines):
    return ("\n".join(lines) + "\n").encode("utf-8")


def landed(c, keys="ABCDE"):
    short = {"A": c["A"][:9], "B": c["B"], "C": c["C"][:7], "D": c["D"], "E": c["E"][:10]}
    return ["## Landed changes"] + [f"- `{short[k]}` {k}" for k in keys]


def errata_arg(root, rows):
    path = root / "errata.tsv"
    path.write_text("".join("\t".join(str(x) for x in row) + "\n" for row in rows),
                    encoding="utf-8")
    return ["--errata", str(path)]


BULK = {}


def bulk(root):
    """One lane with 60k extra objects on refs/heads/bulk (off master) so that
    7-hex prefixes collide naturally: commit/commit, commit/blob, blob/blob."""
    if BULK:
        return BULK
    lane, c = base_lane(root / "bulk")
    n = 60000
    parts = []
    for i in range(n):
        content = f"blob {i}\n".encode()
        parts.append(f"blob\nmark :{i + 1}\ndata {len(content)}\n".encode() + content + b"\n")
    for i in range(n):
        msg = f"bulk {i}".encode()
        parts.append(f"commit refs/heads/bulk\nmark :{n + i + 1}\n"
                     f"committer bulk <b@x> {1400 + i} +0000\ndata {len(msg)}\n".encode()
                     + msg + b"\n" + f"M 100644 :{i + 1} f\n\n".encode())
    git(lane, "fast-import", "--quiet", input=b"".join(parts))
    rows = [r for r in git(lane, "cat-file", "--batch-all-objects",
                           "--batch-check=%(objectname) %(objecttype)").split("\n") if r]
    groups = {}
    for row in rows:
        sha, typ = row.split(" ")
        groups.setdefault(sha[:7], []).append(typ)

    def mixed(p):  # checkable_abbrev-style: a digit and a hex letter
        return any(ch.isdigit() for ch in p) and any(ch in "abcdef" for ch in p)

    def pick(pred):
        return next((p for p, ts in groups.items() if mixed(p) and pred(ts)), None)

    BULK.update(lane=lane, c=c, objects=len(rows),
                cc=pick(lambda ts: ts.count("commit") >= 2),
                cb=pick(lambda ts: ts.count("commit") == 1 and "blob" in ts),
                bb=pick(lambda ts: ts.count("blob") >= 2 and "commit" not in ts))
    return BULK


CASES = []


def case(name, why, mode="json", identity="exact"):
    def deco(fn):
        CASES.append(dict(name=name, why=why, mode=mode, identity=identity, build=fn))
        return fn
    return deco


# ---- clean shapes -----------------------------------------------------------
@case("clean-basic", "real bullets: 9/7/10-hex and full hashes; boundary (atime==cutoff) and "
      "rebased (committer later) commits required; post-report commit ignored")
def _(root):
    lane, c = base_lane(root)
    fleet = fleet_with(root, rpt("# round 1", "## Work performed",
                                 f"measured in `{c['B'][:9]}`.", *landed(c)))
    return dict(lane=lane, fleet=fleet, args=["--json"])


@case("clean-table-prose", "real Landed shapes: table rows and bold prose carrying full hashes")
def _(root):
    lane, c = base_lane(root)
    fleet = fleet_with(root, rpt(
        "# round 1", "## Work performed", "body",
        "## Landed changes", "| Commit | Landed change |", "|---|---|",
        f"| `{c['A']}` | work |", f"| `{c['B']}` | measure |",
        f"**Pushed lane HEAD: `{c['E']}`.**", f"- `{c['C']}` checkpoint", f"- `{c['D']}` rebased"))
    return dict(lane=lane, fleet=fleet, args=["--json"])


@case("clean-crlf", "committed report bytes with CRLF line endings (both arms normalise CR)")
def _(root):
    lane, c = base_lane(root)
    text = "\r\n".join(["# round 1", "## Work performed", "body", *landed(c), ""])
    return dict(lane=lane, fleet=fleet_with(root, text.encode("utf-8")), args=["--json"])


@case("clean-utf8-body", "em dash and accented prose in body (real reports contain these)")
def _(root):
    lane, c = base_lane(root)
    fleet = fleet_with(root, rpt("# round 1", "## Work performed", "measured — café, résumé ✓",
                                 *landed(c)))
    return dict(lane=lane, fleet=fleet, args=["--json"])


@case("clean-nonascii-foreign-author", "non-ASCII author on a non-kama commit; author filter "
      "must still reject it")
def _(root):
    lane, c = base_lane(root, foreign="Zoë Ünïcode")
    fleet = fleet_with(root, rpt("# round 1", "## Work performed", "body", *landed(c)))
    return dict(lane=lane, fleet=fleet, args=["--json"])


@case("clean-i18n-utf8-config", "lane sets i18n.logOutputEncoding=UTF-8 with a non-ASCII subject "
      "on a non-kama commit")
def _(root):
    lane, c = base_lane(root, config={"i18n.logOutputEncoding": "UTF-8"})
    commit(lane, "note café — ok", "someone", 1105)
    fleet = fleet_with(root, rpt("# round 1", "## Work performed", "body", *landed(c)))
    return dict(lane=lane, fleet=fleet, args=["--json"])


@case("clean-log-follow-config", "fleet sets log.follow=true; no rename involved")
def _(root):
    lane, c = base_lane(root)
    fleet = fleet_with(root, rpt("# round 1", "## Work performed", "body", *landed(c)),
                       config={"log.follow": "true"})
    return dict(lane=lane, fleet=fleet, args=["--json"])


@case("clean-alternates-clone-shared", "lane is clone --shared (objects/info/alternates); "
      "borrowed objects must still resolve as local")
def _(root):
    src, c = base_lane(root)
    lane = root / "clone"
    proc = subprocess.run(["git", "clone", "-q", "--shared", str(src), str(lane)],
                          capture_output=True, env=ENV)
    if proc.returncode:
        raise SystemExit(proc.stderr.decode(errors="replace"))
    if not (lane / ".git" / "objects" / "info" / "alternates").exists():
        raise SystemExit("clone --shared produced no alternates file")
    fleet = fleet_with(root, rpt("# round 1", "## Work performed", "body", *landed(c)))
    return dict(lane=lane, fleet=fleet, args=["--json"])


# ---- defects ----------------------------------------------------------------
@case("omission-uncited", "required commit B (full hash) absent from Landed and everywhere")
def _(root):
    lane, c = base_lane(root)
    fleet = fleet_with(root, rpt("# round 1", "## Work performed", "body", *landed(c, "ACDE")))
    return dict(lane=lane, fleet=fleet, args=["--json"])


@case("omission-cited-elsewhere", "required commit C cited only in Work performed (cited_elsewhere)")
def _(root):
    lane, c = base_lane(root)
    fleet = fleet_with(root, rpt("# round 1", "## Work performed",
                                 f"see `{c['C'][:9]}` checkpoint", *landed(c, "ABDE")))
    return dict(lane=lane, fleet=fleet, args=["--json"])


@case("unresolved-fabricated-full", "fabricated 40-hex in body, no replace ref, no source row")
def _(root):
    lane, c = base_lane(root)
    fleet = fleet_with(root, rpt("# round 1", "## Work performed", f"fabricated `{FAKE}`",
                                 *landed(c)))
    return dict(lane=lane, fleet=fleet, args=["--json"])


@case("unresolved-mashup-real-shape", "15-hex prefix of A spliced to 25-hex suffix of B "
      "(the round-20 real defect shape)")
def _(root):
    lane, c = base_lane(root)
    mash = c["A"][:15] + c["B"][15:]
    fleet = fleet_with(root, rpt("# round 1", "## Work performed", f"splice `{mash}`", *landed(c)))
    return dict(lane=lane, fleet=fleet, args=["--json"])


@case("landed-unresolved-typo", "Landed token deadbee1 (digit+letter, no commit)")
def _(root):
    lane, c = base_lane(root)
    fleet = fleet_with(root, rpt("# round 1", "## Work performed", "body", *landed(c),
                                 "- `deadbee1` typo"))
    return dict(lane=lane, fleet=fleet, args=["--json"])


@case("section-missing", "no ## Landed changes heading; all five required commits omitted")
def _(root):
    lane, c = base_lane(root)
    fleet = fleet_with(root, rpt("# round 1", "## Work performed",
                                 f"A `{c['A'][:9]}`, B `{c['B']}`, C `{c['C'][:7]}`, "
                                 f"D `{c['D']}`, E `{c['E'][:10]}`"))
    return dict(lane=lane, fleet=fleet, args=["--json"])


@case("section-prefix-not-heading", "'prefix ## Landed changes' is not a heading (landed_match "
      "anchor)")
def _(root):
    lane, c = base_lane(root)
    fleet = fleet_with(root, rpt("# round 1", "## Work performed",
                                 "prefix ## Landed changes is not a heading", *landed(c)[1:]))
    return dict(lane=lane, fleet=fleet, args=["--json"])


# ---- ambiguity (bulk lane) --------------------------------------------------
def bulk_case(root, key, lines_extra):
    b = bulk(root)
    if b[key] is None:
        raise SystemExit(f"no {key} collision found in bulk lane")
    fleet = fleet_with(root, rpt("# round 1", "## Work performed", "body", *landed(b["c"]),
                                 f"- `{b[key]}` collision probe"))
    return dict(lane=b["lane"], fleet=fleet, args=["--json"])


@case("ambiguous-commit-commit", "7-hex Landed token shared by two commits (expect landed-ambiguous "
      "if peel keeps bare ambiguity)")
def _(root):
    return bulk_case(root, "cc", None)


@case("ambiguous-commit-blob", "7-hex token shared by one commit and one blob; the commit is the "
      "only commit candidate, so ^{commit} peel may resolve it (type-sensitive control)")
def _(root):
    return bulk_case(root, "cb", None)


@case("ambiguous-blob-blob", "7-hex token shared only by blobs (no commit candidate)")
def _(root):
    return bulk_case(root, "bb", None)


# ---- errata -----------------------------------------------------------------
@case("errata-committed-corrects-omitted", "errata row read from committed branch blob "
      "(default path used by the historical harness)")
def _(root):
    lane, c = base_lane(root)
    commit(lane, "errata fixture", "fixture", 1250, path="registry/report-landing-errata.tsv",
           body=f"1\tlanded-omitted\t{c['B']}\t{c['B']}\tfixture")
    fleet = fleet_with(root, rpt("# round 1", "## Work performed", "body", *landed(c, "ACDE")))
    return dict(lane=lane, fleet=fleet, args=["--json"])


@case("errata-file-corrects-section-missing", "section-missing corrected by a non-commit "
      "correction '-' (kind not resolvable) plus five omitted rows")
def _(root):
    lane, c = base_lane(root)
    fleet = fleet_with(root, rpt("# round 1", "## Work performed", "body only"))
    rows = [(1, "landed-section-missing", "-", "-", "fixture")]
    rows += [(1, "landed-omitted", c[k], c[k], "fixture") for k in "ABCDE"]
    return dict(lane=lane, fleet=fleet, args=["--json", *errata_arg(root, rows)])


@case("errata-unmatched", "row for selected round matching no defect")
def _(root):
    lane, c = base_lane(root)
    fleet = fleet_with(root, rpt("# round 1", "## Work performed", "body", *landed(c)))
    rows = [(1, "landed-omitted", "0" * 40, c["A"], "pad")]
    return dict(lane=lane, fleet=fleet, args=["--json", *errata_arg(root, rows)])


@case("errata-invalid-blob-correction", "correction names a blob")
def _(root):
    lane, c = base_lane(root)
    mash = c["A"][:15] + c["B"][15:]
    fleet = fleet_with(root, rpt("# round 1", "## Work performed", f"splice `{mash}`", *landed(c)))
    blob = git(lane, "rev-parse", "HEAD:f").strip()
    rows = [(1, "unresolved-full-hash", mash, blob, "x")]
    return dict(lane=lane, fleet=fleet, args=["--json", *errata_arg(root, rows)])


@case("errata-invalid-fabricated-correction", "correction is a non-existent 40-hex")
def _(root):
    lane, c = base_lane(root)
    mash = c["A"][:15] + c["B"][15:]
    fleet = fleet_with(root, rpt("# round 1", "## Work performed", f"splice `{mash}`", *landed(c)))
    rows = [(1, "unresolved-full-hash", mash, "f" * 40, "x")]
    return dict(lane=lane, fleet=fleet, args=["--json", *errata_arg(root, rows)])


@case("errata-invalid-omitted-differs", "landed-omitted correction differs from the omitted commit")
def _(root):
    lane, c = base_lane(root)
    fleet = fleet_with(root, rpt("# round 1", "## Work performed", "body", *landed(c, "ACDE")))
    rows = [(1, "landed-omitted", c["B"], c["A"], "x")]
    return dict(lane=lane, fleet=fleet, args=["--json", *errata_arg(root, rows)])


@case("errata-abbrev-correction-accepted", "unresolved-full-hash corrected by a 10-hex abbrev of a "
      "real commit")
def _(root):
    lane, c = base_lane(root)
    mash = c["A"][:15] + c["B"][15:]
    fleet = fleet_with(root, rpt("# round 1", "## Work performed", f"splice `{mash}`", *landed(c)))
    rows = [(1, "unresolved-full-hash", mash, c["A"][:10], "x")]
    return dict(lane=lane, fleet=fleet, args=["--json", *errata_arg(root, rows)])


@case("errata-refname-correction", "correction is a branch name (non-hex); frozen accepts via "
      "rev-parse, candidate requires hex 7..40", identity="exact")
def _(root):
    lane, c = base_lane(root)
    mash = c["A"][:15] + c["B"][15:]
    fleet = fleet_with(root, rpt("# round 1", "## Work performed", f"splice `{mash}`", *landed(c)))
    rows = [(1, "unresolved-full-hash", mash, "master", "x")]
    return dict(lane=lane, fleet=fleet, args=["--json", *errata_arg(root, rows)])


# ---- registered source URLs -------------------------------------------------
def sources_text(row):
    return ("# Source registry (fixture)\n\n## Registry\n"
            "| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck "
            "| used-by |\n"
            "|---|---|---|---|---|---|---|---|---|---|---|\n"
            f"{row}\n\n## Leads\n"
            "| S002 | lead — https://example.invalid/none | docs | A | fixture | fixture "
            "| fixture | queued | 2026-10-21 | on-release | — |\n")


def src_case(root, row, body_url, landed_extra=None):
    lane, c = base_lane(root)
    if row is not None:
        commit(lane, "source registry fixture", "fixture", 1250,
               path="corpus/SOURCES.md", body=sources_text(row))
    lines = ["# round 1", "## Work performed", f"ref {body_url}", *landed(c)]
    if landed_extra:
        lines.append(landed_extra)
    return dict(lane=lane, fleet=fleet_with(root, rpt(*lines)), args=["--json"])


@case("source-registered-scheme-cited", "registered full URL cited exactly (exempt)")
def _(root):
    return src_case(root, GOOD_ROW.format(url=SCHEME), SCHEME)


@case("source-registered-census-cited", "registered URL cited census-form (no scheme), as in real "
      "round-22 lines 109-111")
def _(root):
    return src_case(root, GOOD_ROW.format(url=SCHEME), CENSUS)


@case("source-unregistered-url", "same hash, path not in the registry")
def _(root):
    return src_case(root, GOOD_ROW.format(url=SCHEME), OTHER)


@case("source-bare-copy-of-registered-hash", "bare 40-hex copy of a registered hash")
def _(root):
    return src_case(root, GOOD_ROW.format(url=SCHEME), FOREIGN)


@case("source-url-inside-landed", "registered URL placed inside Landed changes (not exempt)")
def _(root):
    return src_case(root, GOOD_ROW.format(url=SCHEME), "body", landed_extra=f"- {SCHEME} upstream")


@case("source-malformed-row", "registry row with 12 cells (not a registry row)")
def _(root):
    return src_case(root, SHORT_ROW.format(url=SCHEME), SCHEME)


@case("source-registry-absent", "no corpus/SOURCES.md on branch (legacy: no exemption)")
def _(root):
    return src_case(root, None, SCHEME)


# ---- drafts and could-not-evaluate -----------------------------------------
@case("draft-render-fleet-cutoff", "--report draft uses committed fleet cutoff; render compared",
      mode="render")
def _(root):
    lane, c = base_lane(root)
    clean = rpt("# round 1", "## Work performed", "body", *landed(c))
    fleet = fleet_with(root, clean)
    draft = root / "draft.md"
    draft.write_bytes(clean + b"- `deadbee1` typo\n")
    return dict(lane=lane, fleet=fleet, args=["--report", f"1={draft}"])


@case("draft-uncommitted-now", "uncommitted draft: cutoff = now, late commit required; render "
      "compared", mode="render")
def _(root):
    lane, c = base_lane(root)
    fleet = empty_fleet(root)
    draft = root / "draft.md"
    draft.write_bytes(rpt("# round 1", "## Work performed", "body", *landed(c)))
    return dict(lane=lane, fleet=fleet, args=["--report", f"1={draft}"])


@case("missing-report-could-not-evaluate", "no committed report, no draft: exit 2 in both arms "
      "(stderr wording differs by design)", identity="exit-only")
def _(root):
    lane, c = base_lane(root)
    return dict(lane=lane, fleet=empty_fleet(root), args=["--json"])


@case("unusable-lane-could-not-evaluate", "lane path does not exist: exit 2 in both arms",
      identity="exit-only")
def _(root):
    lane, c = base_lane(root)
    fleet = fleet_with(root, rpt("# round 1", "## Work performed", "body", *landed(c)))
    return dict(lane=root / "no-such-lane", fleet=fleet, args=["--json"])


@case("expdiff-lane-path-is-subdirectory", "lane path inside the repository, not top level: "
      "candidate refuses non-top-level repositories, frozen audits them")
def _(root):
    lane, c = base_lane(root)
    sub = lane / "sub"
    sub.mkdir()
    fleet = fleet_with(root, rpt("# round 1", "## Work performed", "body", *landed(c)))
    return dict(lane=sub, fleet=fleet, args=["--json"])


@case("expdiff-tag-shadows-branch-omitted", "lightweight tag named master at round-1 commit A: "
      "frozen resolves master through refs/tags first and misses omitted B; candidate pins "
      "refs/heads/master")
def _(root):
    lane, c = base_lane(root)
    git(lane, "tag", "master", c["A"])
    fleet = fleet_with(root, rpt("# round 1", "## Work performed", "body", *landed(c, "ACDE")))
    return dict(lane=lane, fleet=fleet, args=["--json"])


# ---- harness ----------------------------------------------------------------
def effective_args(built):
    args = list(built["args"])
    if "--errata" in args or "--no-errata" in args:
        return args
    probe = subprocess.run(["git", "-C", str(built["lane"]), "cat-file", "-e",
                            "master:registry/report-landing-errata.tsv"],
                           capture_output=True, env=ENV)
    return args if probe.returncode == 0 else args + ["--no-errata"]


def audit(script, lane, fleet, args):
    proc = subprocess.run([sys.executable, str(script), "--lane-repo", str(lane),
                           "--fleet-repo", str(fleet), "--branch", "master", "--lane", "kama",
                           "--rounds", "1", *args], capture_output=True, env=ENV)
    return (proc.returncode, proc.stdout.decode("utf-8", errors="replace"),
            proc.stderr.decode("utf-8", errors="replace"))


def summarize(out, rc, mode):
    if rc == 2:
        return "exit=2"
    if mode == "render":
        return out.strip().split("\n")[-1]
    doc = json.loads(out)
    res = doc["results"][0]
    s = doc["summary"]
    kinds = [f"{d['kind']}:{d['token'][:12]}{'*' if d['corrected_by'] else ''}"
             for d in res["defects"]]
    return (f"status={s['status']} required={res['required']} "
            f"post={len(res['post_report'])} defects={kinds} "
            f"errata_unmatched={s['errata_unmatched']} errata_invalid={s['errata_invalid']} "
            f"src_hashes={res['source_url_hashes']}")


lines = [
    f"frozen  sha256={sha256(FROZEN)} (4fe9339f blob fcc255ce…)",
    f"current sha256={sha256(CURRENT)} (snapshot of live worktree tools/report-landing-audit.py)",
    "",
]
n_same = 0
diffs = []
for spec in CASES:
    root = WORK / spec["name"]
    root.mkdir()
    built = spec["build"](root)
    args = effective_args(built)
    rc_f, out_f, err_f = audit(FROZEN, built["lane"], built["fleet"], args)
    rc_c, out_c, err_c = audit(CURRENT, built["lane"], built["fleet"], args)
    same_exit, same_out, same_err = rc_f == rc_c, out_f == out_c, err_f == err_c
    if spec["identity"] == "exit-only":
        identical = same_exit and same_out
    else:
        identical = same_exit and same_out and same_err
    n_same += identical
    if not identical:
        diffs.append(spec["name"])
    lines.append(f"{'IDENTICAL' if identical else 'DIFF':9} {spec['name']}"
                 f"  exit f={rc_f} c={rc_c} stdout={'=' if same_out else '!='}"
                 f" stderr={'=' if same_err else '!='}"
                 + (" (exit-only)" if spec["identity"] == "exit-only" else ""))
    lines.append(f"    why: {spec['why']}")
    lines.append(f"    frozen : {summarize(out_f, rc_f, spec['mode'])}")
    if not same_out or rc_f == 2:
        lines.append(f"    current: {summarize(out_c, rc_c, spec['mode'])}")
    if rc_f == 2 and not same_err:
        lines.append(f"    stderr frozen : {err_f.strip()[:160]}")
        lines.append(f"    stderr current: {err_c.strip()[:160]}")
lines.append("")
lines.append(f"cases={len(CASES)} identical={n_same} differ={len(diffs)} diff_names={diffs}")
OUT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
