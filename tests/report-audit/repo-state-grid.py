#!/usr/bin/env python3
"""Round-23 repository-state fault grid for tools/report-landing-audit.py.

Each case builds fresh scratch lane/fleet repositories, verifies the fixture
premise (a fixture whose fault never materialized makes the grid exit 2, not
a pass), and runs an auditor as a subprocess with a timeout. Arms:

  frozen   the auditor blob at FROZEN (git cat-file from this lane)
  current  tools/report-landing-audit.py beside this test (or --current PATH)

Graded rows are `fault` (repository-local state must not crash, flip or
hijack the verdict) and `control` (ordinary verdicts both arms must keep).
`open` rows (known unhandled channels) and `tradeoff` rows (declared new
refusals) are reported, never graded.

Exit: 0 every graded row of every selected arm met its expectation; 1 at
least one did not; 2 could not evaluate (fixture premise failed, git or
auditor unusable). `--arm frozen` is expected to exit 1.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

FROZEN = "4fe9339f8fc3a4a4a479d9c938a850da12f1124d"
AUDIT = "tools/report-landing-audit.py"
LANE_DIR = Path(__file__).resolve().parents[2]
REL = ".ufo/reports/round-1/kama.md"
FAKE = "1234567890abcdef1234567890abcdef12345678"
TIMEOUT = 30


class Premise(Exception):
    """The fixture did not establish its fault: cannot evaluate."""


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def g(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], input=data,
                       capture_output=True, env=env(**extra))
    if check and p.returncode:
        raise Premise(f"git {' '.join(map(str, args))}: "
                      f"{p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode(errors="surrogateescape").strip()


def init(path, fmt=None):
    args = ["init", "-q", "-b", "master"] + ([f"--object-format={fmt}"]
                                              if fmt else [])
    g(path.parent, *args, str(path))
    return path


def commit(repo, author, when, msg, path="f", content=None):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if content is None:
        with open(target, "ab") as fh:
            fh.write((msg + "\n").encode())
    else:
        target.write_bytes(content)
    g(repo, "add", "--", path)
    stamp = f"@{when} +0000"
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
      GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
      GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    return g(repo, "rev-parse", "HEAD")


def raw_commit(repo, tree, parents, message, when, author="kama-shokunin",
               headers=b""):
    """Hash a commit object from raw bytes (signature headers, bad bytes)."""
    body = b"tree " + tree.encode() + b"\n"
    for p in parents:
        body += b"parent " + p.encode() + b"\n"
    who = author.encode() + b" <a@x> " + str(when).encode() + b" +0000"
    body += b"author " + who + b"\ncommitter " + who + b"\n" + headers
    body += b"\n" + message
    return g(repo, "hash-object", "-t", "commit", "-w", "--stdin", data=body)


def report(cites, extra=b""):
    lines = b"".join(b"- " + c.encode() + b"\n" for c in cites)
    return b"# kama round 1\n\n## Landed changes\n\n" + lines + extra


def pair(tmp, lane_fmt=None):
    lane, fleet = Path(tmp, "lane"), Path(tmp, "fleet")
    init(lane, lane_fmt)
    init(fleet)
    return lane, fleet


def publish(fleet, text, when=2000, path=REL):
    commit(fleet, "fleet", when, "round-1: report", path, text)


def base(tmp):
    """Lane with one cited round-1 commit; fleet report citing it."""
    lane, fleet = pair(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    publish(fleet, report([lc]))
    return lane, fleet, lc


def require(cond, what):
    if not cond:
        raise Premise(what)


# ------------------------------------------------------------------ cases
# Each builder returns (lane, fleet, argv_extra, marker_or_None).

def c_clean(tmp):
    lane, fleet, _ = base(tmp)
    return lane, fleet, [], None


def c_omission(tmp):
    lane, fleet, _ = base(tmp)
    commit(lane, "kama-shokunin", 1500, "round-1: more")
    return lane, fleet, [], None


def c_fake_full(tmp):
    lane, fleet = pair(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    publish(fleet, report([lc]) + b"\n## Notes\n\nsee " + FAKE.encode() + b"\n")
    return lane, fleet, [], None


def c_no_landed(tmp):
    lane, fleet = pair(tmp)
    commit(lane, "kama-shokunin", 1000, "round-1: work")
    publish(fleet, b"# kama round 1\n\nno section\n")
    return lane, fleet, [], None


def c_shared_clone(tmp):
    lane, fleet, _ = base(tmp)
    shared = Path(tmp, "shared")
    g(tmp, "clone", "-q", "--shared", str(lane), str(shared))
    require(Path(shared, ".git/objects/info/alternates").exists(),
            "clone --shared wrote no alternates")
    return shared, fleet, [], None


def c_errata_ok(tmp):
    lane, fleet, _ = base(tmp)
    x = commit(lane, "kama-shokunin", 1500, "round-1: more")
    commit(lane, "fixture", 1600, "errata", "registry/report-landing-errata.tsv",
           f"1\tlanded-omitted\t{x}\t{x}\tev\n".encode())
    return lane, fleet, ["errata"], None


def c_crlf(tmp):
    lane, fleet = pair(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    publish(fleet, report([lc]).replace(b"\n", b"\r\n"))
    return lane, fleet, [], None

def c_cr_only(tmp):
    """Old-Mac line endings: text-mode reads translated lone CR."""
    lane, fleet = pair(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    publish(fleet, report([lc]).replace(b"\n", b"\r"))
    return lane, fleet, [], None


def f_utf16_cutoff(tmp):
    """Fleet-local UTF-16 log output reaches the %at cutoff digits."""
    lane, fleet, _ = base(tmp)
    g(fleet, "config", "i18n.logOutputEncoding", "UTF-16")
    out = subprocess.run(["git", "-C", str(fleet), "log", "--format=%at"],
                         capture_output=True, env=env()).stdout
    require(b"\x00" in out, "UTF-16 log output not observed")
    return lane, fleet, [], None


def f_promisor_pack(tmp):
    """A blobless clone whose promisor config was removed still lacks the
    blob the report cites; absence there is not evidence."""
    lane, fleet = pair(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    blob = g(lane, "rev-parse", f"{lc}:f")
    g(lane, "config", "uploadpack.allowFilter", "true")
    clone = Path(tmp, "blobless")
    g(tmp, "-c", "protocol.file.allow=always", "clone", "-q", "--no-checkout",
      "--filter=blob:none", "--no-local", f"file://{lane}", str(clone))
    for key in ("remote.origin.promisor", "remote.origin.partialclonefilter",
                "extensions.partialclone"):
        g(clone, "config", "--unset", key, check=False)
    publish(fleet, report([lc]) + b"\n## Notes\n\nblob " + blob.encode() + b"\n")
    packs = list(Path(clone, ".git/objects/pack").glob("*.promisor"))
    missing = subprocess.run(["git", "-C", str(clone), "cat-file", "-e", blob],
                             capture_output=True, env=env()).returncode
    require(packs and missing != 0, "promisor pack/missing blob not observed")
    return clone, fleet, [], None



def f_log_encoding(tmp):
    lane, fleet, _ = base(tmp)
    commit(lane, "someone", 1100, "note caf\u00e9")
    g(lane, "config", "i18n.logOutputEncoding", "ISO-8859-1")
    out = subprocess.run(["git", "-C", str(lane), "log", "-1", "--format=%s"],
                         capture_output=True, env=env()).stdout
    require(b"\xe9" in out, "log output not re-encoded to Latin-1")
    return lane, fleet, [], None


def f_report_bytes(tmp):
    lane, fleet = pair(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    publish(fleet, report([lc]) + b"\xff\xfe bad\n")
    return lane, fleet, [], None


def f_replace_omission(tmp):
    lane, fleet, lc = base(tmp)
    x = commit(lane, "kama-shokunin", 1200, "round-1: more")
    y = raw_commit(lane, g(lane, "rev-parse", f"{x}^{{tree}}"), [lc],
                   b"unrelated\n", 1200, author="fixture")
    g(lane, "replace", x, y)
    require(g(lane, "log", "-1", "--format=%s") == "unrelated",
            "replace ref not effective")
    return lane, fleet, [], None


def f_replace_fabricated(tmp):
    lane, fleet = pair(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    publish(fleet, report([lc, FAKE]))
    g(lane, "update-ref", f"refs/replace/{FAKE}", lc)
    require(g(lane, "cat-file", "-t", FAKE) == "commit",
            "fabricated replace ref not effective")
    return lane, fleet, [], None


def f_replace_report(tmp):
    lane, fleet, lc = base(tmp)
    x = commit(lane, "kama-shokunin", 1500, "round-1: more")
    real = g(fleet, "rev-parse", "HEAD")
    # decoy report citing both commits, swapped in by refs/replace
    blob = g(fleet, "hash-object", "-w", "--stdin", data=report([lc, x]))
    r1 = g(fleet, "mktree", data=f"100644 blob {blob}\tkama.md\n".encode())
    r2 = g(fleet, "mktree", data=f"040000 tree {r1}\tround-1\n".encode())
    r3 = g(fleet, "mktree", data=f"040000 tree {r2}\treports\n".encode())
    tree = g(fleet, "mktree", data=f"040000 tree {r3}\t.ufo\n".encode())
    decoy = raw_commit(fleet, tree, [], b"round-1: report\n", 2000,
                       author="fleet")
    g(fleet, "replace", real, decoy)
    require(x in g(fleet, "show", f"HEAD:{REL}"), "report replace not effective")
    return lane, fleet, [], None


def f_lazy_fetch(tmp):
    lane, fleet = pair(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    fake2 = "abcdefabcdefabcdefabcdefabcdefabcdefabcd"
    publish(fleet, report([lc, fake2]))
    marker = Path(tmp, "lazy-fetch-ran")
    for k, v in (("extensions.partialClone", "origin"),
                 ("remote.origin.url", "ssh://example.invalid/x.git"),
                 ("remote.origin.promisor", "true"),
                 ("core.sshCommand", f"touch {marker}; false")):
        g(lane, "config", k, v)
    subprocess.run(["git", "-C", str(lane), "cat-file", "-e", fake2],
                   capture_output=True, env=env())
    require(marker.exists(), "lazy fetch did not run the configured command")
    marker.unlink()
    return lane, fleet, [], marker


def f_log_follow(tmp):
    lane, fleet = pair(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    commit(lane, "kama-shokunin", 2000, "round-1: more")
    commit(fleet, "fleet", 1500, "draft", "drafts/kama.md", report([lc]))
    Path(fleet, REL).parent.mkdir(parents=True)
    g(fleet, "mv", "drafts/kama.md", REL)
    g(fleet, "commit", "-q", "-m", "round-1: report",
      GIT_AUTHOR_DATE="@2500 +0000", GIT_COMMITTER_DATE="@2500 +0000")
    g(fleet, "config", "log.follow", "true")
    require(g(fleet, "log", "--diff-filter=A", "--format=%at", "--", REL)
            .split()[-1] == "1500", "log.follow did not move the first add")
    return lane, fleet, [], None


def f_show_root(tmp):
    lane, fleet = pair(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    commit(lane, "kama-shokunin", 3500, "round-1: after report")
    publish(fleet, report([lc]), when=2000)       # root commit adds report
    g(fleet, "rm", "-q", REL)
    g(fleet, "commit", "-q", "-m", "drop", GIT_AUTHOR_DATE="@3000 +0000",
      GIT_COMMITTER_DATE="@3000 +0000")
    publish(fleet, report([lc]), when=4000)
    g(fleet, "config", "log.showRoot", "false")
    require(g(fleet, "log", "--diff-filter=A", "--format=%at", "--", REL)
            .split()[-1] == "4000", "log.showRoot=false did not hide root add")
    return lane, fleet, [], None


def f_signature_program(tmp):
    lane, fleet, lc = base(tmp)
    marker = Path(tmp, "gpg-ran")
    prog = Path(tmp, "fake-gpg")
    prog.write_text(f"#!/bin/sh\ntouch {marker}\nexit 1\n")
    prog.chmod(0o755)
    sig = (b"gpgsig -----BEGIN PGP SIGNATURE-----\n \n iQE=\n"
           b" -----END PGP SIGNATURE-----\n")
    signed = raw_commit(lane, g(lane, "rev-parse", f"{lc}^{{tree}}"), [lc],
                        b"signed note\n", 1100, author="someone", headers=sig)
    g(lane, "update-ref", "refs/heads/master", signed)
    g(lane, "config", "log.showSignature", "true")
    g(lane, "config", "gpg.program", str(prog))
    subprocess.run(["git", "-C", str(lane), "log", "-1"], capture_output=True,
                   env=env())
    require(marker.exists(), "showSignature did not run gpg.program")
    marker.unlink()
    return lane, fleet, [], marker


def _hidden_history(tmp):
    """Omitted round commit X older than the cited tip LC."""
    lane, fleet = pair(tmp)
    commit(lane, "kama-shokunin", 900, "round-1: omitted")
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    publish(fleet, report([lc]))
    return lane, fleet, lc


def f_shallow(tmp):
    lane, fleet, lc = _hidden_history(tmp)
    Path(lane, ".git/shallow").write_text(lc + "\n")
    require(g(lane, "rev-list", "--count", "HEAD") == "1", "shallow ineffective")
    return lane, fleet, [], None


def f_grafts(tmp):
    lane, fleet, lc = _hidden_history(tmp)
    Path(lane, ".git/info").mkdir(exist_ok=True)
    Path(lane, ".git/info/grafts").write_text(lc + "\n")
    require(g(lane, "rev-list", "--count", "HEAD") == "1", "grafts ineffective")
    return lane, fleet, [], None


def f_tag_shadow(tmp):
    lane, fleet, lc = base(tmp)
    commit(lane, "kama-shokunin", 1500, "round-1: more")
    g(lane, "tag", "master", lc)
    require(g(lane, "rev-parse", "master") == lc, "tag did not shadow branch")
    return lane, fleet, [], None


def f_ref_abbrev(tmp):
    lane, fleet = pair(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    publish(fleet, report([lc, "deadbee1"]))
    g(lane, "tag", "deadbee1", lc)
    require(g(lane, "cat-file", "-t", "deadbee1") == "commit",
            "ref name did not resolve the abbreviation")
    return lane, fleet, [], None


def f_mailmap_fifo(tmp):
    lane, fleet, _ = base(tmp)
    os.mkfifo(Path(lane, ".mailmap"))
    p = subprocess.run(["timeout", "5", "git", "-C", str(lane), "log", "-1"],
                       capture_output=True, env=env())
    require(p.returncode == 124, "FIFO .mailmap did not block git log")
    return lane, fleet, [], None


def f_sha256_lane(tmp):
    lane, fleet = pair(tmp, lane_fmt="sha256")
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    require(len(lc) == 64, "lane is not sha256")
    publish(fleet, report([lc]))
    return lane, fleet, [], None


def f_errata_bytes(tmp):
    lane, fleet, _ = base(tmp)
    commit(lane, "fixture", 1600, "errata", "registry/report-landing-errata.tsv",
           b"# \xff bad\n")
    return lane, fleet, ["errata"], None


def f_errata_revision(tmp):
    lane, fleet = pair(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    publish(fleet, report([lc]) + b"\n## Notes\n\nsee " + FAKE.encode() + b"\n")
    commit(lane, "fixture", 1600, "errata", "registry/report-landing-errata.tsv",
           f"1\tunresolved-full-hash\t{FAKE}\tHEAD\tev\n".encode())
    return lane, fleet, ["errata"], None


def _bad_subject(tmp, round_subject):
    lane, fleet, lc = base(tmp)
    msg = (b"round-1: caf\xe9\n" if round_subject else b"note caf\xe9\n")
    bad = raw_commit(lane, g(lane, "rev-parse", f"{lc}^{{tree}}"), [lc], msg,
                     1100, author="kama-shokunin")
    g(lane, "update-ref", "refs/heads/master", bad)
    return lane, fleet, [], None


def f_bad_subject(tmp):
    return _bad_subject(tmp, False)


def f_bad_round_subject(tmp):
    return _bad_subject(tmp, True)


def f_quote_path(tmp):
    """A committed fleet path with raw Latin-1 bytes; fleet-local
    core.quotePath=false makes `ls-tree` emit them unquoted."""
    lane, fleet, _ = base(tmp)
    odd = os.path.join(os.fsencode(fleet), b".ufo/reports/caf\xe9.md")
    with open(odd, "wb") as fh:
        fh.write(b"x\n")
    g(fleet, "add", "-A")
    g(fleet, "commit", "-q", "-m", "odd", GIT_AUTHOR_DATE="@2100 +0000",
      GIT_COMMITTER_DATE="@2100 +0000")
    g(fleet, "config", "core.quotePath", "false")
    raw = subprocess.run(["git", "-C", str(fleet), "ls-tree", "-r",
                          "--name-only", "HEAD"], capture_output=True,
                         env=env()).stdout
    require(b"caf\xe9.md" in raw, "ls-tree did not emit raw path bytes")
    return lane, fleet, ["open-range"], None


def o_alternates(tmp):
    lane, fleet = pair(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    donor = init(Path(tmp, "donor"))
    foreign = commit(donor, "x", 900, "foreign")
    publish(fleet, report([lc, foreign]))
    Path(lane, ".git/objects/info/alternates").write_text(
        str(Path(donor, ".git/objects")) + "\n")
    return lane, fleet, [], None


def t_blobless(tmp):
    lane, fleet, _ = base(tmp)
    g(lane, "config", "uploadpack.allowFilter", "true")
    clone = Path(tmp, "blobless")
    g(tmp, "-c", "protocol.file.allow=always", "clone", "-q",
      "--filter=blob:none", "--no-local", f"file://{lane}", str(clone))
    return clone, fleet, [], None


def f_nested_subdir(tmp):
    """--lane-repo names a plain subdirectory of an enclosing repository
    whose own history lacks the omission; git silently discovers upward."""
    outer = init(Path(tmp, "outer"))
    commit(outer, "fixture", 500, "outer")
    sub = Path(outer, "lane")
    sub.mkdir()
    lane, fleet, _ = base(tmp)
    commit(lane, "kama-shokunin", 1500, "round-1: more")
    require(g(sub, "rev-parse", "--show-prefix") == "lane/",
            "subdirectory not discovered inside the enclosing repo")
    return sub, fleet, [], None


def o_gitfile(tmp):
    lane, fleet, _ = base(tmp)
    commit(lane, "kama-shokunin", 1500, "round-1: more")
    decoy = init(Path(tmp, "decoy"))
    commit(decoy, "kama-shokunin", 1000, "round-1: work")
    front = Path(tmp, "front")
    front.mkdir()
    Path(front, ".git").write_text(f"gitdir: {Path(decoy, '.git')}\n")
    return front, fleet, [], None


CASES = [
    # name, kind, builder, expected {exit, kinds}
    ("C01-clean", "control", c_clean, 0, []),
    ("C02-real-omission", "control", c_omission, 1, ["landed-omitted"]),
    ("C03-fabricated-full-hash", "control", c_fake_full, 1,
     ["unresolved-full-hash"]),
    ("C04-landed-section-missing", "control", c_no_landed, 1,
     ["landed-omitted", "landed-section-missing"]),
    ("C05-shared-clone-clean", "control", c_shared_clone, 0, []),
    ("C06-errata-corrects-omission", "control", c_errata_ok, 0,
     ["landed-omitted"]),
    ("C07-crlf-report", "control", c_crlf, 0, []),
    ("C08-cr-only-report", "control", c_cr_only, 0, []),
    ("F01-log-output-encoding", "fault", f_log_encoding, 0, []),
    ("F02-report-invalid-utf8", "fault", f_report_bytes, 2, None),
    ("F03-replace-hides-omission", "fault", f_replace_omission, 1,
     ["landed-omitted"]),
    ("F04-replace-fabricated-citation", "fault", f_replace_fabricated, 1,
     ["landed-unresolved", "unresolved-full-hash"]),
    ("F05-replace-fleet-report", "fault", f_replace_report, 1,
     ["landed-omitted"]),
    ("F06-lazy-fetch-command", "fault", f_lazy_fetch, 2, None),
    ("F07-log-follow-cutoff", "fault", f_log_follow, 1, ["landed-omitted"]),
    ("F08-log-showroot-cutoff", "fault", f_show_root, 0, []),
    ("F09-signature-program", "fault", f_signature_program, 0, []),
    ("F10-shallow-lane", "fault", f_shallow, 2, None),
    ("F11-grafts-lane", "fault", f_grafts, 2, None),
    ("F12-tag-shadows-branch", "fault", f_tag_shadow, 1, ["landed-omitted"]),
    ("F13-ref-named-abbreviation", "fault", f_ref_abbrev, 2, None),
    ("F14-mailmap-fifo", "fault", f_mailmap_fifo, 0, []),
    ("F15-sha256-lane", "fault", f_sha256_lane, 2, None),
    ("F16-errata-invalid-utf8", "fault", f_errata_bytes, 2, None),
    ("F17-errata-revision-correction", "fault", f_errata_revision, 1,
     ["unresolved-full-hash"]),
    ("F18-bad-byte-unrelated-subject", "fault", f_bad_subject, 0, []),
    ("F19-bad-byte-round-subject", "fault", f_bad_round_subject, 1,
     ["landed-omitted"]),
    ("F20-quotepath-open-range", "fault", f_quote_path, 0, []),
    ("F21-nested-subdirectory-lane", "fault", f_nested_subdir, 2, None),
    ("F22-utf16-log-cutoff", "fault", f_utf16_cutoff, 0, []),
    ("F23-promisor-pack-without-config", "fault", f_promisor_pack, 2, None),
    ("O01-alternates-foreign-object", "open", o_alternates, 1,
     ["landed-unresolved", "unresolved-full-hash"]),
    ("O02-gitfile-redirect", "open", o_gitfile, 1, ["landed-omitted"]),
    ("T01-blobless-partial-clone", "tradeoff", t_blobless, 0, []),
]


# An exit-2 expectation also pins the refusal reason, so an unrelated
# startup error cannot pass as the intended refusal.
REASONS = {
    "F02-report-invalid-utf8": "output is not UTF-8",
    "F06-lazy-fetch-command": "partial clone",
    "F10-shallow-lane": "shallow repository",
    "F11-grafts-lane": "rewrites history",
    "F13-ref-named-abbreviation": "names a ref",
    "F15-sha256-lane": "object format",
    "F16-errata-invalid-utf8": "output is not UTF-8",
    "F21-nested-subdirectory-lane": "not a repository top level",
    "F23-promisor-pack-without-config": "promisor pack",
}


def population():
    rows = [[n, k, b.__name__, e, s, REASONS.get(n)] for n, k, b, e, s in CASES]
    blob = json.dumps(rows, sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()


def run_case(auditor, case, tmp):
    name, kind, build, want_exit, want_kinds = case
    lane, fleet, extra, marker = build(tmp)
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--json"]
    argv += ["--rounds", "1-" if "open-range" in extra else "1"]
    if "errata" not in extra:
        argv.append("--no-errata")
    try:
        p = subprocess.run(argv, capture_output=True, timeout=TIMEOUT,
                           env=env(), cwd=tmp)
        code, out, err, timed_out = p.returncode, p.stdout, p.stderr, False
    except subprocess.TimeoutExpired as exc:
        code, out, err, timed_out = None, exc.stdout or b"", exc.stderr or b"", True
    kinds = None
    if code in (0, 1):
        try:
            doc = json.loads(out)
            kinds = sorted({d["kind"] for r in doc["results"]
                            for d in r["defects"]})
        except (ValueError, KeyError, TypeError):
            kinds = "unparseable"
    traceback = b"Traceback (most recent call last)" in err
    executed = bool(marker and marker.exists())
    reason = REASONS.get(name)
    met = (not timed_out and not traceback and not executed
           and code == want_exit
           and (want_kinds is None or kinds == sorted(want_kinds))
           and (reason is None or reason.encode() in err))
    return {"case": name, "kind": kind, "exit": code, "kinds": kinds,
            "traceback": traceback, "executed": executed,
            "timed_out": timed_out, "expected_exit": want_exit,
            "expected_kinds": want_kinds, "met": met,
            "stderr_tail": err.decode(errors="replace").strip()[-200:]}


def frozen_auditor(tmp):
    p = subprocess.run(["git", "-C", str(LANE_DIR), "cat-file", "blob",
                        f"{FROZEN}:{AUDIT}"], capture_output=True, env=env())
    if p.returncode:
        raise Premise(f"cannot read frozen auditor: {p.stderr.decode().strip()}")
    path = Path(tmp, "frozen-audit.py")
    path.write_bytes(p.stdout)
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--arm", choices=("frozen", "current", "both"),
                    default="both")
    ap.add_argument("--current", default=str(LANE_DIR / AUDIT))
    ap.add_argument("--case", action="append", help="run only these cases")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    arms = ("frozen", "current") if args.arm == "both" else (args.arm,)
    cases = [c for c in CASES if not args.case or c[0] in args.case]
    doc = {"frozen_revision": FROZEN, "population_sha256": population(),
           "timeout_seconds": TIMEOUT, "arms": {}}
    try:
        with tempfile.TemporaryDirectory(prefix="repo-state-grid-") as root:
            auditors = {"frozen": None, "current": Path(args.current)}
            if "frozen" in arms:
                auditors["frozen"] = frozen_auditor(root)
            doc["auditor_sha256"] = {
                a: hashlib.sha256(Path(auditors[a]).read_bytes()).hexdigest()
                for a in arms}
            for arm in arms:
                rows = []
                for i, case in enumerate(cases):
                    tmp = Path(root, arm, f"{i:02d}")
                    tmp.mkdir(parents=True)
                    rows.append(run_case(auditors[arm], case, tmp))
                graded = [r for r in rows if r["kind"] in ("fault", "control")]
                doc["arms"][arm] = {
                    "faults": sum(r["kind"] == "fault" for r in rows),
                    "faults_met": sum(r["met"] for r in rows
                                      if r["kind"] == "fault"),
                    "controls": sum(r["kind"] == "control" for r in rows),
                    "controls_met": sum(r["met"] for r in rows
                                        if r["kind"] == "control"),
                    "tracebacks": sum(r["traceback"] for r in rows),
                    "commands_executed": sum(r["executed"] for r in rows),
                    "timeouts": sum(r["timed_out"] for r in rows),
                    "violations": sum(not r["met"] for r in graded),
                    "rows": rows}
    except Premise as exc:
        print(f"could-not-evaluate: fixture premise: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # errors are never grid verdicts
        print(f"could-not-evaluate: {type(exc).__name__}: {exc}",
              file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(doc, indent=1, sort_keys=True))
    else:
        for arm, res in doc["arms"].items():
            for r in res["rows"]:
                print(f"{arm} {r['case']} {r['kind']} exit={r['exit']} "
                      f"kinds={r['kinds']} tb={int(r['traceback'])} "
                      f"exec={int(r['executed'])} "
                      f"timeout={int(r['timed_out'])} "
                      f"{'met' if r['met'] else 'NOT-MET'}")
            print(f"{arm} faults={res['faults_met']}/{res['faults']} "
                  f"controls={res['controls_met']}/{res['controls']} "
                  f"tracebacks={res['tracebacks']} "
                  f"executed={res['commands_executed']} "
                  f"timeouts={res['timeouts']} violations={res['violations']}")
    bad = any(res["violations"] for res in doc["arms"].values())
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
