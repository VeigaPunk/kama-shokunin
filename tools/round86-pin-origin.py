#!/usr/bin/env python3
"""round86-pin-origin.py - round-86 C3 (freshness): corroborate every pin-recheck row
against the SOURCE BYTES themselves, not against hash integrity of a local extract.

Round-83/84 graded a row by comparing two committed anchor extracts. A hash-consistent
extract pair is still only a local claim: the digest proves the file is unchanged, never
that it was ever acquired from the named URL. This instrument closes that gap: for each
row it re-reads the two anchor headers (``# url=... sha256=... ref=... lines=a-b``),
recomputes the digest over the stored body, fetches the URL live, and compares the stored
body with the upstream range byte for byte.

Row verdicts (a row with two anchors takes the worst):
  verified    both anchors: digest matches the stored body and the stored body equals the
              upstream bytes at the declared line range
  mismatch    an anchor's stored body differs from the upstream bytes at that range
  unreachable the URL could not be fetched (HTTP error, timeout, network refusal)
  bad         an anchor header is malformed or its declared digest does not match the body

Output: one ``PIN_ORIGIN rows=<n> verified=<v> mismatch=<m> unreachable=<u> bad=<b>`` line,
then one ``PIN_ORIGIN_ROW <engine>/<ref> verdict=<v> anchors=<ok>/<total> <detail>`` line
per row.

Exit: 0 every row verified; 1 any mismatch, unreachable or bad row; 2 could-not-evaluate
(absent rows register, unreadable anchor, no fetch possible at all) - never silently 0.

``--selftest`` builds fixture registers and anchors in $TMPDIR and injects a recorded
fetcher: a fabricated but hash-consistent extract must grade ``mismatch``, never
``verified``.
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import sys
import tempfile
import urllib.error
import urllib.request

PREDICATE = (
    "`python3 tools/round86-pin-origin.py --repo <lane> --rev <rev> --rows "
    "registry/pin-recheck-rows.tsv` prints one `PIN_ORIGIN rows=5 verified=5 mismatch=0 "
    "unreachable=0 bad=0` line and exits 0 only when every row's two committed anchor extracts "
    "match the live upstream bytes at their declared ranges; a hash-consistent extract whose "
    "bytes differ from upstream is `mismatch`, never `verified`."
)

ROWS = "registry/pin-recheck-rows.tsv"
HEADER = ("engine", "ref", "newest", "verdict", "date", "quote_pin", "line_pin",
          "quote_newest", "line_newest", "extract_pin", "extract_newest", "note")
ANCHOR = re.compile(r"^# url=(\S+) sha256=([0-9a-f]{64}) ref=(\S+) lines=([0-9]+)-([0-9]+)$")
USER_AGENT = "kama-shokunin-pin-origin/1 (read-only documentary check)"


class CouldNotEvaluate(Exception):
    pass


def live_fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def read_text(repo: pathlib.Path, rev: str, rel: str):
    if rev == "worktree":
        path = repo / rel
        if not path.is_file():
            return None
        return path.read_text(encoding="utf-8", errors="surrogateescape")
    import subprocess
    try:
        return subprocess.check_output(["git", "-C", str(repo), "show", f"{rev}:{rel}"],
                                       text=True, errors="surrogateescape")
    except subprocess.CalledProcessError:
        return None


def parse_anchor(text: str):
    lines = text.split("\n")
    match = ANCHOR.match(lines[0])
    if not match:
        raise CouldNotEvaluate(f"malformed anchor header: {lines[0][:80]}")
    body = "\n".join(lines[1:])
    return {"url": match.group(1), "sha256": match.group(2), "ref": match.group(3),
            "start": int(match.group(4)), "end": int(match.group(5)), "body": body}


def check_anchor(repo, rev, rel, cache, fetch):
    text = read_text(repo, rev, rel)
    if text is None:
        return "bad", f"anchor absent at {rev}: {rel}"
    try:
        info = parse_anchor(text)
    except CouldNotEvaluate as exc:
        return "bad", f"{rel}: {exc}"
    stored = info["body"].encode("utf-8", errors="surrogateescape")
    if hashlib.sha256(stored).hexdigest() != info["sha256"]:
        return "bad", f"{rel}: declared digest does not match the stored body"
    if info["url"] not in cache:
        try:
            cache[info["url"]] = fetch(info["url"])
        except (urllib.error.URLError, OSError, ValueError) as exc:
            cache[info["url"]] = exc
    upstream = cache[info["url"]]
    if isinstance(upstream, Exception):
        return "unreachable", f"{rel}: {info['url']}: {upstream}"
    text_lines = upstream.decode("utf-8", errors="surrogateescape").splitlines()
    if info["end"] > len(text_lines) or info["start"] < 1:
        return "mismatch", f"{rel}: declared range {info['start']}-{info['end']} outside upstream " \
                           f"({len(text_lines)} lines)"
    window = "\n".join(text_lines[info["start"] - 1:info["end"]]) + "\n"
    if window.encode("utf-8", errors="surrogateescape") != stored:
        return "mismatch", f"{rel}: stored body differs from upstream {info['start']}-{info['end']}"
    return "verified", f"{rel}: upstream {info['start']}-{info['end']} byte-identical"


def parse_rows(text: str):
    rows = []
    lines = [line for line in text.splitlines() if line.strip() and not line.startswith("#")]
    if not lines:
        raise CouldNotEvaluate("rows register is empty")
    header = tuple(cell.strip() for cell in lines[0].split("\t"))
    if header != HEADER:
        raise CouldNotEvaluate(f"rows register header mismatch: {header}")
    for line in lines[1:]:
        cells = line.split("\t")
        if len(cells) != len(HEADER):
            raise CouldNotEvaluate(f"rows register row has {len(cells)} cells: {line[:80]}")
        rows.append(dict(zip(HEADER, (cell.strip() for cell in cells))))
    return rows


def grade(repo: pathlib.Path, rev: str, rows_path: str, fetch=live_fetch):
    text = read_text(repo, rev, rows_path)
    if text is None:
        raise CouldNotEvaluate(f"no {rows_path} at {rev}")
    rows = parse_rows(text)
    cache = {}
    results = []
    for row in rows:
        anchors = [row["extract_pin"], row["extract_newest"]]
        verdicts = []
        details = []
        for rel in anchors:
            verdict, detail = check_anchor(repo, rev, rel, cache, fetch)
            verdicts.append(verdict)
            details.append(detail)
        for worst in ("bad", "mismatch", "unreachable", "verified"):
            if worst in verdicts:
                verdict = worst
                break
        ok = sum(1 for v in verdicts if v == "verified")
        results.append({"key": f"{row['engine']}/{row['ref']}", "verdict": verdict,
                        "ok": ok, "total": len(verdicts), "detail": "; ".join(details)})
    counts = {name: sum(1 for r in results if r["verdict"] == name)
              for name in ("verified", "mismatch", "unreachable", "bad")}
    return {"results": results, "rows": len(results), **counts}


def render(result):
    return (f"PIN_ORIGIN rows={result['rows']} verified={result['verified']} "
            f"mismatch={result['mismatch']} unreachable={result['unreachable']} "
            f"bad={result['bad']}")


# ---------------------------------------------------------------- selftest

UPSTREAM = ("# LLaMA.cpp HTTP Server\n"
            "line-two\n"
            "This endpoint is public (no API key check). `/v1/health` also works.\n"
            "line-four\n"
            "line-five\n")
URL = "https://example.invalid/fixture/README.md"


def write_anchor(root: pathlib.Path, rel: str, url: str, ref: str, start: int, end: int,
                 lines, body_override=None):
    body = body_override if body_override is not None else "\n".join(lines) + "\n"
    digest = hashlib.sha256(body.encode()).hexdigest()
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# url={url} sha256={digest} ref={ref} lines={start}-{end}\n{body}",
                    encoding="utf-8")
    return body


def write_rows(root: pathlib.Path, pin: str, newest: str, engine="fixture", ref="v1"):
    path = root / ROWS
    path.parent.mkdir(parents=True, exist_ok=True)
    cells = [engine, ref, "v2", "holds", "2026-11-04", "q", "3", "q", "3", pin, newest, "n"]
    path.write_text("\t".join(HEADER) + "\n" + "\t".join(cells) + "\n", encoding="utf-8")


def selftest():
    arms = []
    upstream_lines = UPSTREAM.splitlines()

    def arm(name, build, fetch, want_verdict):
        with tempfile.TemporaryDirectory(prefix="r86-origin-") as directory:
            root = pathlib.Path(directory)
            pin, newest = build(root)
            try:
                result = grade(root, "worktree", ROWS, fetch=fetch)
                verdict = result["results"][0]["verdict"]
            except CouldNotEvaluate as exc:
                verdict = f"could-not-evaluate: {exc}"
        arms.append((name, verdict == want_verdict, f"verdict={verdict} want={want_verdict}"))

    def good(root):
        pin = "corpus/anchors/a.txt"
        newest = "corpus/anchors/b.txt"
        write_anchor(root, pin, URL, "v1", 1, 5, upstream_lines)
        write_anchor(root, newest, URL, "v2", 1, 5, upstream_lines)
        write_rows(root, pin, newest)
        return pin, newest

    def fabricated(root):
        pin = "corpus/anchors/a.txt"
        newest = "corpus/anchors/b.txt"
        write_anchor(root, pin, URL, "v1", 1, 5, upstream_lines)
        write_anchor(root, newest, URL, "v2", 1, 5, None,
                     body_override="fabricated body that still hashes\n")
        write_rows(root, pin, newest)
        return pin, newest

    def digest_lie(root):
        pin = "corpus/anchors/a.txt"
        newest = "corpus/anchors/b.txt"
        write_anchor(root, pin, URL, "v1", 1, 5, upstream_lines)
        path = root / newest
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# url={URL} sha256={'0' * 64} ref=v2 lines=1-5\nanything\n",
                        encoding="utf-8")
        write_rows(root, pin, newest)
        return pin, newest

    def malformed(root):
        pin = "corpus/anchors/a.txt"
        newest = "corpus/anchors/b.txt"
        write_anchor(root, pin, URL, "v1", 1, 5, upstream_lines)
        path = root / newest
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("no header here\nbody\n", encoding="utf-8")
        write_rows(root, pin, newest)
        return pin, newest

    def missing(root):
        pin = "corpus/anchors/a.txt"
        newest = "corpus/anchors/b.txt"
        write_anchor(root, pin, URL, "v1", 1, 5, upstream_lines)
        write_rows(root, pin, newest)
        return pin, newest

    good_fetch = lambda url: UPSTREAM.encode()
    arm("verified", good, good_fetch, "verified")
    arm("fabricated-hash-consistent", fabricated, good_fetch, "mismatch")
    arm("digest-lie", digest_lie, good_fetch, "bad")
    arm("malformed-header", malformed, good_fetch, "bad")
    arm("missing-anchor", missing, good_fetch, "bad")

    def refused(url):
        raise urllib.error.URLError("connection refused")
    arm("unreachable", good, refused, "unreachable")
    arm("range-outside-upstream", lambda root: (write_anchor(
        root, "corpus/anchors/a.txt", URL, "v1", 1, 99, upstream_lines),
        write_anchor(root, "corpus/anchors/b.txt", URL, "v2", 1, 5, upstream_lines),
        write_rows(root, "corpus/anchors/a.txt", "corpus/anchors/b.txt"),
        ("corpus/anchors/a.txt", "corpus/anchors/b.txt"))[3], good_fetch, "mismatch")
    fail = sum(1 for _, ok, _ in arms if not ok)
    for name, ok, detail in arms:
        print(f"PIN_ORIGIN_SELFTEST_{'PASS' if ok else 'FAIL'} {name} {detail}")
    print(f"PIN_ORIGIN_SELFTEST pass={len(arms) - fail} fail={fail}")
    return 0 if fail == 0 else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--rev", default="master")
    parser.add_argument("--rows", default=ROWS)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    try:
        result = grade(pathlib.Path(args.repo).resolve(), args.rev, args.rows)
    except CouldNotEvaluate as exc:
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        print(render(result))
        for row in result["results"]:
            print(f"PIN_ORIGIN_ROW {row['key']} verdict={row['verdict']} "
                  f"anchors={row['ok']}/{row['total']} {row['detail']}")
    return 0 if (result["verified"] == result["rows"] and result["mismatch"] == 0
                 and result["unreachable"] == 0 and result["bad"] == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
