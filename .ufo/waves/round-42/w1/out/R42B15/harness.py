#!/usr/bin/env python3
"""R42B15 fixture harness: digest-ledger.py vs the four existing citation-surface tools."""
import hashlib
import json
import os
import shutil
import subprocess
import sys

ROOT = "/fast/scratch/kama-r42/seats/R42B15"
FX = os.path.join(ROOT, "fx")
TOOLS = os.path.join(ROOT, "clone", "tools")
TMP = os.path.join(ROOT, "tmp")
FLEET = "/home/vgpnk/Projects/shokunin"
ENV = dict(os.environ, TMPDIR=TMP, GIT_CONFIG_NOSYSTEM="1",
           GIT_CONFIG_GLOBAL="/dev/null", HOME=TMP)


def sh(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, env=ENV, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def git(d, *a):
    return sh(["git", "-C", d, *a])


def newrepo(name):
    d = os.path.join(FX, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    rc, o, e = sh(["git", "init", "-q", "--template=", d])
    assert rc == 0, (rc, e)
    rc, o, e = git(d, "rev-parse", "--show-toplevel")
    assert os.path.realpath(o.strip()) == os.path.realpath(d), (o, e)
    return d


def wf(d, rel, data):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb" if isinstance(data, bytes) else "w") as f:
        f.write(data)


def commit(d, msg):
    git(d, "add", "-A")
    rc, o, e = git(d, "-c", "user.name=fixture", "-c",
                   "user.email=fixture@example.invalid", "commit", "-q", "-m", msg)
    assert rc == 0, e
    return git(d, "rev-parse", "HEAD")[1].strip()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def run_dl(d, rev="HEAD", extra=()):
    return sh([sys.executable, os.path.join(TOOLS, "digest-ledger.py"),
               "scan", "--repo", d, "--rev", rev, *extra], cwd=d)


def run_cp(d, reg, docs):
    return sh([sys.executable, os.path.join(TOOLS, "citation-provenance.py"),
               "--lane", d, "--registry", reg, "--docs", *docs,
               "--allow-off-ref"], cwd=d)


def run_sao(d, frm, to):
    return sh([sys.executable, os.path.join(TOOLS, "sources-append-only.py"),
               "--from", frm, "--to", to, "--repo", d], cwd=d)


def run_grc(d):
    return sh([sys.executable, os.path.join(TOOLS, "gate-registry-check.py"),
               "--repo", d], cwd=d)


def run_rla(d, report):
    rc, out, err = sh([sys.executable, os.path.join(TOOLS, "report-landing-audit.py"),
                       "--lane-repo", d, "--fleet-repo", FLEET,
                       "--report", f"42={report}", "--no-errata", "--json"], cwd=d)
    kinds = []
    try:
        data = json.loads(out)
        for row in data.get("results", []):
            if os.path.realpath(row.get("report", "")) == os.path.realpath(report):
                kinds = [x["kind"] for x in row["defects"]]
    except Exception:  # noqa: BLE001
        return (rc, f"unparsed err={err.splitlines()[-1][:90] if err else ''}", "")
    return (rc, f"draft_defects={len(kinds)} kinds={sorted(set(kinds))}", "")


def reg(path, rows):
    with open(path, "w") as f:
        json.dump(rows, f)


RESULTS = []


def note(case, tool, r, extra=""):
    rc, out, err = r
    line = (out.splitlines()[-1] if out else (err.splitlines()[-1] if err else ""))
    RESULTS.append(dict(case=case, tool=tool, exit=rc, line=line, extra=extra))
    print(f"{case:28s} {tool:26s} exit={rc} {line} {extra}")


# FX1: a bare wrong digest (no cite() token, no ledger row) beside a satisfied citation
def fx1():
    d = newrepo("fx1-bare-wrong")
    payload = b"payload\n"
    wf(d, "evidence.txt", payload)
    good = sha(payload)
    bad = "9" * 64
    wf(d, "doc.md", f"cite(REV, evidence.txt, sha256={good})\nbare digest {bad} for nothing\n")
    rev = commit(d, "fixture")
    doc = os.path.join(d, "doc.md")
    txt = open(doc).read().replace("REV", rev)
    open(doc, "w").write(txt)
    commit(d, "bind rev")
    rp = os.path.join(d, "required.json")
    reg(rp, [{"id": "f1", "rev": rev, "path": "evidence.txt", "sha256": good, "doc": "doc.md"}])
    note("fx1 bare wrong digest", "digest-ledger", run_dl(d))
    note("fx1 bare wrong digest", "citation-provenance", run_cp(d, rp, [doc]))
    rep = os.path.join(d, "draft.md")
    open(rep, "w").write(f"# draft\n\nA bare digest {bad} that hashes nothing.\n\n## Landed changes\n\nnothing\n")
    note("fx1 bare wrong digest", "report-landing-audit", run_rla(d, rep))
    note("fx1 bare wrong digest", "gate-registry-check", run_grc(d))
    return d


# FX2: a wrong digest that shares its first 8 hex with a real blob
def fx2():
    d = newrepo("fx2-prefix-wrong")
    payload = b"payload\n"
    wf(d, "evidence.txt", payload)
    good = sha(payload)
    near = good[:8] + "0" * 56
    wf(d, "doc.md", f"cite(REV, evidence.txt, sha256={good})\nsecond copy {near}\n")
    commit(d, "fixture")
    rev = git(d, "rev-parse", "HEAD")[1].strip()
    doc = os.path.join(d, "doc.md")
    txt = open(doc).read().replace("REV", rev)
    open(doc, "w").write(txt)
    commit(d, "bind rev")
    rp = os.path.join(d, "required.json")
    reg(rp, [{"id": "f2", "rev": rev, "path": "evidence.txt", "sha256": good, "doc": "doc.md"}])
    note("fx2 prefix-wrong digest", "digest-ledger", run_dl(d))
    note("fx2 prefix-wrong digest", "citation-provenance", run_cp(d, rp, [doc]))
    note("fx2 prefix-wrong digest", "gate-registry-check", run_grc(d))
    return d


# FX3: right digest, wrong path (digest belongs to a.txt, doc attributes it to b.txt)
def fx3():
    d = newrepo("fx3-path-swap")
    a = b"alpha\n"
    b = b"beta\n"
    wf(d, "a.txt", a)
    wf(d, "b.txt", b)
    da = sha(a)
    commit(d, "fixture")
    rev = git(d, "rev-parse", "HEAD")[1].strip()
    wf(d, "doc.md", f"b.txt carries sha256 {da} (cite({rev}, b.txt, sha256={da}))\n")
    commit(d, "doc")
    rp = os.path.join(d, "required.json")
    reg(rp, [{"id": "f3", "rev": rev, "path": "b.txt", "sha256": da, "doc": "doc.md"}])
    note("fx3 path-swapped digest", "digest-ledger", run_dl(d))
    note("fx3 path-swapped digest", "citation-provenance", run_cp(d, rp, [os.path.join(d, "doc.md")]))
    return d


# FX4: digest of a historical revision of a file, cited as the current bytes
def fx4():
    d = newrepo("fx4-history")
    v1 = b"version one\n"
    wf(d, "a.txt", v1)
    commit(d, "v1")
    dv1 = sha(v1)
    wf(d, "a.txt", b"version two\n")
    commit(d, "v2")
    rev = git(d, "rev-parse", "HEAD")[1].strip()
    wf(d, "doc.md", f"a.txt carries sha256 {dv1} (cite({rev}, a.txt, sha256={dv1}))\n")
    commit(d, "doc")
    rp = os.path.join(d, "required.json")
    reg(rp, [{"id": "f4", "rev": rev, "path": "a.txt", "sha256": dv1, "doc": "doc.md"}])
    note("fx4 historical digest", "digest-ledger", run_dl(d))
    note("fx4 historical digest", "citation-provenance", run_cp(d, rp, [os.path.join(d, "doc.md")]))
    return d


# FX5: wrong digest inside a .ufo/ wave document
def fx5():
    d = newrepo("fx5-ufo-scope")
    payload = b"receipt\n"
    wf(d, ".ufo/waves/round-42/receipt.txt", payload)
    good = sha(payload)
    wf(d, "doc.md", "see receipt\n")
    commit(d, "fixture")
    rev = git(d, "rev-parse", "HEAD")[1].strip()
    rpt = ".ufo/waves/round-42/R42.md"
    wf(d, rpt, f"receipt digest {'7' * 64} (correct is {good})\n")
    commit(d, "report")
    rp = os.path.join(d, "required.json")
    reg(rp, [{"id": "f5", "rev": rev, "path": ".ufo/waves/round-42/receipt.txt",
              "sha256": good, "doc": "R42.md"}])
    note("fx5 .ufo wrong digest", "digest-ledger", run_dl(d))
    note("fx5 .ufo wrong digest", "citation-provenance",
         run_cp(d, rp, [os.path.join(d, rpt)]))
    return d


# FX6: ledger laundering -- a `wrong` row reclassified as `unverifiable` in a later commit
def fx6():
    d = newrepo("fx6-ledger-launder")
    payload = b"real\n"
    wf(d, "evidence.txt", payload)
    good = sha(payload)
    wrong = good[:8] + "f" * 56
    hdr = "digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n"
    wf(d, "doc.md", f"digest {wrong}\n")
    wf(d, "registry/digest-ledger.tsv", hdr + f"{wrong}\twrong\tS001\t\t{good}\t\t\n")
    c1 = commit(d, "ledger says wrong")
    note("fx6 ledger row wrong", "digest-ledger", run_dl(d, rev=c1))
    wf(d, "registry/digest-ledger.tsv",
       hdr + f"{wrong}\tunverifiable\tS001\t\t\t\tthe artifact is not stored\n")
    c2 = commit(d, "reclassify as unverifiable")
    note("fx6 row reclassified", "digest-ledger", run_dl(d, rev=c2))
    note("fx6 row reclassified", "sources-append-only", run_sao(d, c1, c2))
    note("fx6 row reclassified", "gate-registry-check", run_grc(d))
    return d


# FX7: SOURCES.md anchor cell rewritten to another real digest
def fx7():
    d = newrepo("fx7-anchor-rewrite")
    one = b"source one bytes\n"
    two = b"source two bytes\n"
    wf(d, "src/one.txt", one)
    wf(d, "src/two.txt", two)
    d1, d2 = sha(one), sha(two)
    hdr = ("| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |\n"
           "|---|---|---|---|---|---|---|---|---|---|---|\n")
    row = "| S001 | https://example.invalid/a | docs | A | engine | sha256:{dg} | thing | ok | 2026-10-25 | | corpus/knowledge/x.md |\n"
    wf(d, "corpus/SOURCES.md", "## Registry\n\n" + hdr + row.format(dg=d1))
    wf(d, "corpus/knowledge/x.md", f"anchor {d1}\n")
    c1 = commit(d, "row with digest one")
    wf(d, "corpus/SOURCES.md", "## Registry\n\n" + hdr + row.format(dg=d2))
    wf(d, "corpus/knowledge/x.md", f"anchor {d2}\n")
    c2 = commit(d, "anchor rewritten to digest two")
    note("fx7 anchor rewritten", "sources-append-only", run_sao(d, c1, c2))
    note("fx7 anchor rewritten", "digest-ledger", run_dl(d, rev=c2))
    return d


# FX8: an unregistered counter tool
def fx8():
    d = newrepo("fx8-unregistered")
    hdr = ("| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |\n"
           "|---|---|---|---|---|\n")
    wf(d, "SKILL.md", "# skill\n\n## Instruments\n\n" + hdr +
       "| Other | gate: `tools/round98-other.py` | 0 clean; 1 bad | none | none |\n")
    wf(d, "tools/round98-other.py", "print('ok')\n")
    wf(d, "tools/round99-unregistered.py", "print('ok')\n")
    wf(d, "doc.md", "plain\n")
    commit(d, "fixture")
    note("fx8 unregistered counter", "gate-registry-check", run_grc(d))
    note("fx8 unregistered counter", "digest-ledger", run_dl(d))
    return d


# FX9: unresolved 40-hex commit citation in a draft report
def fx9():
    d = newrepo("fx9-commit-token")
    wf(d, "doc.md", "plain\n")
    commit(d, "fixture")
    rep = os.path.join(d, "draft.md")
    open(rep, "w").write("# draft\n\nLanded at 0123456789abcdef0123456789abcdef01234567 .\n\n"
                         "## Landed changes\n\n- 0123456789abcdef0123456789abcdef01234567 did nothing\n")
    note("fx9 unresolved commit", "report-landing-audit", run_rla(d, rep))
    note("fx9 unresolved commit", "digest-ledger", run_dl(d))
    return d


# FX10: a registered cite() token carrying a wrong digest (overlap case)
def fx10():
    d = newrepo("fx10-registered-wrong")
    payload = b"payload\n"
    wf(d, "evidence.txt", payload)
    good = sha(payload)
    near = good[:8] + "1" * 56
    commit(d, "fixture")
    rev = git(d, "rev-parse", "HEAD")[1].strip()
    wf(d, "doc.md", f"cite({rev}, evidence.txt, sha256={near})\n")
    commit(d, "doc")
    rp = os.path.join(d, "required.json")
    reg(rp, [{"id": "f10", "rev": rev, "path": "evidence.txt", "sha256": good, "doc": "doc.md"}])
    note("fx10 registered wrong cite", "digest-ledger", run_dl(d))
    note("fx10 registered wrong cite", "citation-provenance", run_cp(d, rp, [os.path.join(d, "doc.md")]))
    return d


# FX11: ledger external rows -- stale re-hash, and a row skipped by first-match-wins
def fx11():
    d = newrepo("fx11-external-bad")
    hdr = "digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n"
    outside = os.path.join(ROOT, "tmp", "fx11-outside.bin")
    with open(outside, "wb") as f:
        f.write(b"outside bytes\n")
    declared = sha(b"different bytes\n")
    wf(d, "doc.md", f"artifact digest {declared}\n")
    wf(d, "registry/digest-ledger.tsv",
       hdr + f"{declared}\texternal\ts\t{outside}\t\t\tstale re-hash\n")
    commit(d, "fixture")
    note("fx11a external stale", "digest-ledger", run_dl(d))

    d2 = newrepo("fx11b-external-shadowed")
    body = b"committed bytes\n"
    wf(d2, "artifact.bin", body)
    wf(d2, "doc.md", f"artifact digest {sha(body)}\n")
    wf(d2, "registry/digest-ledger.tsv",
       hdr + f"{sha(body)}\texternal\ts\t{outside}\t\t\tdeclared external\n")
    commit(d2, "fixture")
    note("fx11b external shadowed", "digest-ledger", run_dl(d2))
    return d


# FX12: unverifiable row with an empty note
def fx12():
    d = newrepo("fx12-unverifiable-nonote")
    hdr = "digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n"
    tok = "ab" * 32
    wf(d, "doc.md", f"digest {tok}\n")
    wf(d, "registry/digest-ledger.tsv", hdr + f"{tok}\tunverifiable\ts\t\t\t\t\n")
    commit(d, "fixture")
    note("fx12 unverifiable no note", "digest-ledger", run_dl(d))
    return d


# FX13: wrong digest in a .json receipt (not a .md/.tsv document)
def fx13():
    d = newrepo("fx13-json-receipt")
    wf(d, "doc.md", "plain\n")
    wf(d, ".ufo/waves/round-42/c2/candidate.out", f"digest={'cd' * 32}\n")
    wf(d, "receipts/candidate.json", json.dumps({"digest": "ef" * 32}))
    commit(d, "fixture")
    note("fx13 json/out receipt", "digest-ledger", run_dl(d))
    return d


for fn in (fx1, fx2, fx3, fx4, fx5, fx6, fx7, fx8, fx9, fx10, fx11, fx12, fx13):
    try:
        fn()
    except Exception as exc:  # noqa: BLE001
        print(f"{fn.__name__} HARNESS ERROR: {exc}", file=sys.stderr)
    print()

json.dump(RESULTS, open(os.path.join(ROOT, "results.json"), "w"), indent=1)
print("results:", len(RESULTS))
