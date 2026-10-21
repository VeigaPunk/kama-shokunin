#!/usr/bin/env python3
"""citation-provenance.py — machine-checkable revision-qualified citations.

Round-18 routed defects (S055/Gate/SCORECARD) were pointer drift: prose cited a
path at a revision where the described bytes did not exist, or the tip's
artifacts replaced the cited ones. This tool makes each material citation a
token the documents must carry:

    cite(<rev>, <path>, sha256=<64 lowercase hex>)

and verifies, for every required row in the registry, that (a) some document
carries the exact token, and (b) `git cat-file` at `<rev>:<path>` yields a blob
whose SHA-256 equals the token's digest. Missing or mismatching rows are
counted; exit 0 only when both counts are zero.

    citation-provenance.py [--registry PATH] [--docs PATH ...] [--lane PATH]
                           [--json] [--selftest]

Exit: 0 all required citations found and verified; 1 missing/mismatch;
      2 unusable registry/docs/git.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

TOKEN = re.compile(
    r"cite\(([0-9a-f]{7,40}), ([^,()\s]+), sha256=([0-9a-f]{64})\)")
DEFAULT_DOCS = ("corpus/lessons/round-18.md", "corpus/lessons/round-19.md",
                "corpus/SOURCES.md", "SCORECARD.md", "LOG.md")
DEFAULT_REGISTRY = "registry/required-citations.json"


def git_blob(lane, rev, path):
    """(sha256, raw) of rev:path, or (None, reason)."""
    try:
        raw = subprocess.run(
            ["git", "-C", str(lane), "cat-file", "blob", f"{rev}:{path}"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=60).stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired,
            OSError) as exc:
        err = getattr(exc, "stderr", b"") or b""
        return None, (err.decode("utf-8", "replace").strip()
                      or type(exc).__name__)
    return hashlib.sha256(raw).hexdigest(), None


def scan(docs):
    """([(doc, rev, path, sha)], unreadable_docs) for the documents."""
    found = []
    unreadable = []
    for doc in docs:
        try:
            text = Path(doc).read_text(encoding="utf-8")
        except OSError as exc:
            print(f"citation-provenance: cannot read {doc}: {exc}",
                  file=sys.stderr)
            unreadable.append(str(doc))
            continue
        for match in TOKEN.finditer(text):
            found.append((str(doc), match.group(1), match.group(2),
                          match.group(3)))
    return found, unreadable


def check(lane, registry, docs, allow_off_ref=False):
    probe = subprocess.run(["git", "-C", str(lane), "rev-parse", "--git-dir"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if probe.returncode != 0:
        raise ValueError(f"lane is not a git repository: {lane}")
    rows = json.loads(Path(registry).read_text(encoding="utf-8"))
    if not isinstance(rows, list) or not rows:
        raise ValueError("registry must be a non-empty JSON array")
    tokens, unreadable = scan(docs)
    results = []
    for row in rows:
        rid, rev, path = row.get("id"), row.get("rev"), row.get("path")
        want = row.get("sha256")
        doc_bind = row.get("doc")
        if not all(isinstance(v, str) and v
                   for v in (rid, rev, path, want)):
            raise ValueError(f"invalid registry row: {row!r}")
        if doc_bind is not None and not isinstance(doc_bind, str):
            raise ValueError(f"invalid registry doc: {row!r}")
        same_target = [t for t in tokens if t[1] == rev and t[2] == path]
        hits = [t for t in same_target if t[3] == want
                and (doc_bind is None or str(t[0]).endswith(doc_bind))]
        stale = [t for t in same_target if t[3] != want]
        observed, error = git_blob(lane, rev, path)
        status = "ok"
        if stale:
            status = "mismatch"
        elif not hits:
            status = "missing"
        elif error is not None or observed != want:
            status = "mismatch"
        elif not allow_off_ref:
            anc = subprocess.run(
                ["git", "-C", str(lane), "merge-base", "--is-ancestor",
                 rev, "origin/master"], stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            if anc.returncode != 0:
                status = "off-ref"
        results.append({
            "id": rid, "rev": rev, "path": path, "sha256": want,
            "documents": sorted({h[0] for h in hits}),
            "observed_sha256": observed, "error": error, "status": status})
    counts = {
        "required": len(results),
        "docs_unreadable": len(unreadable),
        "found": sum(1 for r in results if r["documents"]),
        "verified": sum(1 for r in results if r["status"] == "ok"),
        "missing": sum(1 for r in results if r["status"] == "missing"),
        "mismatch": sum(1 for r in results if r["status"] == "mismatch"),
        "off_ref": sum(1 for r in results if r["status"] == "off-ref"),
    }
    return counts, results


def selftest():
    failures = []
    with tempfile.TemporaryDirectory(prefix="citation-provenance-") as tmp:
        lane = Path(tmp) / "lane"
        lane.mkdir()
        env = {"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
               "HOME": tmp, "PATH": "/usr/bin:/bin"}

        def git(*argv):
            return subprocess.run(["git", "-C", str(lane), *argv],
                                  check=True, env=env,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True).stdout
        git("init", "-q", "--template=")
        target = lane / "evidence.txt"
        target.write_text("payload\n", encoding="utf-8")
        git("add", "--", "evidence.txt")
        git("-c", "user.name=t", "-c", "user.email=t@example.invalid",
            "commit", "-q", "-m", "fixture")
        rev = git("rev-parse", "HEAD").strip()
        digest = hashlib.sha256(b"payload\n").hexdigest()
        doc = lane / "doc.md"
        registry = lane / "required.json"
        registry.write_text(json.dumps([{
            "id": "fixture", "rev": rev, "path": "evidence.txt",
            "sha256": digest}]), encoding="utf-8")

        def run(text, expect):
            doc.write_text(text, encoding="utf-8")
            counts, _ = check(lane, registry, [doc], allow_off_ref=True)
            ok = ((counts["missing"], counts["mismatch"]) == (0, 0)
                  if expect == 0 else
                  (counts["missing"], counts["mismatch"]) != (0, 0))
            if not ok:
                failures.append(f"{expect}: {counts}")
            return counts
        run(f"cite({rev}, evidence.txt, sha256={digest})", 0)
        run(f"cite({rev}, evidence.txt, sha256={digest})\n"
            f"cite({rev}, evidence.txt, sha256={digest})", 0)
        run(f"cite({rev[:6]}, evidence.txt, sha256={digest})", 1)
        run(f"cite({rev.upper()}, evidence.txt, sha256={digest.upper()})", 1)
        run(f"cite({rev}, evidence.txt, sha256={digest})\n"
            f"cite({rev}, evidence.txt, sha256={'1' * 64})", 1)
        run("no token here", 1)
        run(f"cite({rev}, evidence.txt, sha256={'0' * 64})", 1)
        run(f"cite({'f' * 40}, evidence.txt, sha256={digest})", 1)
        run(f"cite({rev}, absent.txt, sha256={digest})", 1)
        run(f"cite({rev[:1]}, evidence.txt, sha256={digest})", 1)
        stale = "2" * 64
        doc.write_text(f"cite({rev}, evidence.txt, sha256={stale})",
                       encoding="utf-8")
        counts, _ = check(lane, registry, [doc], allow_off_ref=True)
        if counts["mismatch"] != 1:
            failures.append(f"stale-equal: {counts}")
        if not DEFAULT_DOCS or not all(d for d in DEFAULT_DOCS):
            failures.append("default docs list is empty")
        other = lane / "other.md"
        other.write_text(f"cite({rev}, evidence.txt, sha256={digest})",
                         encoding="utf-8")
        bound = json.loads(registry.read_text(encoding="utf-8"))
        bound[0]["doc"] = "doc.md"
        registry.write_text(json.dumps(bound), encoding="utf-8")
        counts, _ = check(lane, registry, [other], allow_off_ref=True)
        if counts["missing"] != 1:
            failures.append(f"doc-binding: {counts}")
        doc.write_text(f"cite({rev}, evidence.txt, sha256={digest})",
                       encoding="utf-8")
        counts, _ = check(lane, registry, [doc], allow_off_ref=True)
        if (counts["missing"], counts["verified"]) != (0, 1):
            failures.append(f"doc-binding-ok: {counts}")
        counts, _ = check(lane, registry, [doc, lane / "absent.md"], allow_off_ref=True)
        if counts["docs_unreadable"] != 1 or counts["verified"] != 1:
            failures.append(f"unreadable-doc: {counts}")
    if failures:
        for f in failures:
            print(f"SELFTEST FAIL {f}", file=sys.stderr)
        return 1
    print("selftest: ok (15 cases)")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--registry", default=None)
    ap.add_argument("--docs", nargs="+", default=None)
    ap.add_argument("--lane", default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--allow-off-ref", action="store_true",
                    help="accept revisions that are not ancestors of origin/master")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    lane = Path(args.lane or Path(__file__).resolve().parent.parent)
    docs = args.docs or [str(lane / d) for d in DEFAULT_DOCS]
    registry = args.registry or str(lane / DEFAULT_REGISTRY)
    try:
        counts, results = check(lane, registry, docs,
                               allow_off_ref=args.allow_off_ref)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"citation-provenance: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({"counts": counts, "results": results}, indent=1))
    else:
        print(" ".join(f"{k}={v}" for k, v in counts.items()))
        for row in results:
            if row["status"] != "ok":
                print(f"  {row['status']}: {row['id']} "
                      f"{row['rev']}:{row['path']} "
                      f"expected={row['sha256']} "
                      f"observed={row['observed_sha256'] or 'absent'}"
                      + (f" ({row['error']})" if row["error"] else ""))
    if counts["docs_unreadable"]:
        return 2
    return 0 if counts["missing"] == 0 and counts["mismatch"] == 0 \
        and counts["off_ref"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
