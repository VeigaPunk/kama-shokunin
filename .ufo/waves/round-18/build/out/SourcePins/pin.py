#!/usr/bin/env python3
"""Fetch and verify round-18 read-only source pins for loopback socket formats.

Raw bodies are saved byte-for-byte under raw/ beside this script.  Every line
range in pins.json is recomputed from unique regular-expression anchors; no
line numbers are embedded in the locator table.  ``--verify`` re-fetches all
sources and checks their SHA-256 digests and located excerpts.  ``--selftest``
is offline and also checks the saved artifact when pins.json exists.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
import os
import re
import ssl
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
PINS_PATH = ROOT / "pins.json"
USER_AGENT = "kama-shokunin-source-pins/18"
TIMEOUT = 12
SCHEMA = "kama-source-pins/v1"
LINUX_TAG = "v7.2"
LINUX_TAG_COMMIT = "8d3ae59288f1e7d58d76558a6ee96d533bc5019f"
LINUX_TAG_NOTE = "v7.2 exists; no v7.x fallback was used (git ls-remote, 2026-10-20)."

# Each source is fetched with urllib.request.urlopen (GET).  Archive members are
# copied from the received tarball bytes without invoking an extractor command.
SOURCES = {
    "linux_tcp6": {
        "url": "https://raw.githubusercontent.com/torvalds/linux/v7.2/net/ipv6/tcp_ipv6.c",
        "saved_as": "raw/linux/v7.2/net/ipv6/tcp_ipv6.c",
        "format": "text", "family": "linux", "version": "Linux v7.2",
    },
    "linux_tcp4": {
        "url": "https://raw.githubusercontent.com/torvalds/linux/v7.2/net/ipv4/tcp_ipv4.c",
        "saved_as": "raw/linux/v7.2/net/ipv4/tcp_ipv4.c",
        "format": "text", "family": "linux", "version": "Linux v7.2",
    },
    "linux_proc_net_tcp": {
        "url": "https://raw.githubusercontent.com/torvalds/linux/v7.2/Documentation/networking/proc_net_tcp.rst",
        "saved_as": "raw/linux/v7.2/Documentation/networking/proc_net_tcp.rst",
        "format": "text", "family": "linux", "version": "Linux v7.2",
    },
    "rfc4291": {
        "url": "https://www.rfc-editor.org/rfc/rfc4291.txt",
        "saved_as": "raw/www.rfc-editor.org/rfc/rfc4291.txt",
        "format": "text", "family": "rfc",
    },
    "python_exceptions": {
        "url": "https://docs.python.org/3.14/library/exceptions.html",
        "saved_as": "raw/docs.python.org/3.14/library/exceptions.html",
        "format": "html", "family": "python",
    },
    "pytest_exit_codes": {
        "url": "https://docs.pytest.org/en/stable/reference/exit-codes.html",
        "saved_as": "raw/docs.pytest.org/en/stable/reference/exit-codes.html",
        "format": "html", "family": "pytest",
    },
    "pytest_options": {
        "url": "https://docs.pytest.org/en/stable/_static/documentation_options.js",
        "saved_as": "raw/docs.pytest.org/en/stable/_static/documentation_options.js",
        "format": "text", "family": "pytest-options",
    },
    "automake_page": {
        "url": "https://www.gnu.org/software/automake/manual/html_node/Scripts_002dbased-Testsuites.html",
        "saved_as": "raw/www.gnu.org/software/automake/manual/html_node/Scripts_002dbased-Testsuites.html",
        "format": "html", "family": "automake-page",
        "note": "S053 rejected-as-basis: requested HTML page was unreachable here and is not the citation basis; official release-source fallback is pinned below.",
    },
    "automake_release": {
        "url": "https://ftp.gnu.org/gnu/automake/automake-1.19.tar.xz",
        "saved_as": "raw/ftp.gnu.org/gnu/automake/automake-1.19.tar.xz",
        "format": "tar.xz", "family": "automake-release",
        "members": {
            "automake_texi": "automake-1.19/doc/automake.texi",
            "automake_version": "automake-1.19/doc/version.texi",
        },
        "note": "Official GNU release tarball used only as a transparent substitute for the unreachable requested HTML page.",
    },
}

DOCS = {
    "linux_tcp6": {"saved_as": SOURCES["linux_tcp6"]["saved_as"], "format": "text"},
    "linux_tcp4": {"saved_as": SOURCES["linux_tcp4"]["saved_as"], "format": "text"},
    "linux_proc_net_tcp": {"saved_as": SOURCES["linux_proc_net_tcp"]["saved_as"], "format": "text"},
    "rfc4291": {"saved_as": SOURCES["rfc4291"]["saved_as"], "format": "text"},
    "python_exceptions": {"saved_as": SOURCES["python_exceptions"]["saved_as"], "format": "html"},
    "pytest_exit_codes": {"saved_as": SOURCES["pytest_exit_codes"]["saved_as"], "format": "html"},
    "pytest_options": {"saved_as": SOURCES["pytest_options"]["saved_as"], "format": "text"},
    "automake_html": {"saved_as": SOURCES["automake_page"]["saved_as"], "format": "html"},
    "automake_texi": {"saved_as": "raw/ftp.gnu.org/gnu/automake/automake-1.19/doc/automake.texi", "format": "text"},
    "automake_version": {"saved_as": "raw/ftp.gnu.org/gnu/automake/automake-1.19/doc/version.texi", "format": "text"},
}

# Locators use searched anchors and delimiters, never baked-in line numbers.
# All public evidence quotes are short enough to transfer into a SOURCES row.
PINS = {
    "tcp6_socket_row": {
        "doc": "linux_tcp6", "kind": "block",
        "start": r"^static void get_tcp6_sock\(struct seq_file \*seq, struct sock \*sp, int i\)$",
        "quotes": [
            "%08X%08X%08X%08X:%04X",
            "src->s6_addr32[0], src->s6_addr32[1],",
            "dest->s6_addr32[0], dest->s6_addr32[1],",
        ],
    },
    "tcp4_socket_row": {
        "doc": "linux_tcp4", "kind": "block",
        "start": r"^static void get_tcp4_sock\(struct sock \*sk, struct seq_file \*f, int i\)$",
        "quotes": [
            "%08X:%04X %08X:%04X",
            "__be32 src = inet->inet_rcv_saddr;",
            "sock_i_ino(sk)",
        ],
    },
    "proc_net_tcp_fields": {
        "doc": "linux_proc_net_tcp", "kind": "span",
        "start": r"^These /proc interfaces provide information about currently active TCP$",
        "end": r"^TCP connections\. A typical entry of /proc/net/tcp would look like this",
        "quotes": [
            "implemented by tcp4_seq_show() in net/ipv4/tcp_ipv4.c and tcp6_seq_show()",
            "currently active TCP connections",
        ],
    },
    "proc_net_tcp_example": {
        "doc": "linux_proc_net_tcp", "kind": "span",
        "start": r"^   46: 010310AC:9C4C 030310AC:1770 01$",
        "end": r"^   \|----------------------------------> number of entry$",
        "quotes": [
            "010310AC:9C4C 030310AC:1770 01",
            "local IPv4 address",
            "remote TCP port number",
        ],
    },
    "rfc4291_mapped_ipv6": {
        "doc": "rfc4291", "kind": "span",
        "start": r"^2\.5\.5\.2\.\s+IPv4-Mapped IPv6 Address$",
        "end": r"^\s+See \[RFC4038\] for background on the usage of the",
        "quotes": [
            "IPv4 nodes as IPv6 addresses.",
            "|0000..............................0000|FFFF|",
            "IPv4-mapped IPv6 address",
        ],
    },
    "rfc4291_loopback": {
        "doc": "rfc4291", "kind": "span",
        "start": r"^2\.5\.3\.\s+The Loopback Address$",
        "end": r"^   be dropped\.$",
        "quotes": [
            "0:0:0:0:0:0:0:1 is called the loopback address.",
            "must not be used as the source address in IPv6 packets",
        ],
    },
    "python_baseexception": {
        "doc": "python_exceptions", "kind": "span",
        "start": r'^<dt class="sig sig-object py" id="BaseException">$',
        "end": r"</p>", "quotes": [
            "The base class for all built-in exceptions.",
            "not meant to be directly inherited by user-defined classes",
        ],
    },
    "python_keyboardinterrupt": {
        "doc": "python_exceptions", "kind": "span",
        "start": r'^<dt class="sig sig-object py" id="KeyboardInterrupt">$',
        "end": r"</p>", "quotes": [
            "Raised when the user hits the interrupt key",
            "The exception inherits from BaseException",
        ],
    },
    "python_systemexit": {
        "doc": "python_exceptions", "kind": "span",
        "start": r'^<dt class="sig sig-object py" id="SystemExit">$',
        "end": r"</p>", "quotes": [
            "This exception is raised by the sys.exit() function.",
            "It inherits from BaseException instead of Exception",
            "it specifies the system exit status",
        ],
    },
    "python_exception_hierarchy": {
        "doc": "python_exceptions", "kind": "span",
        "start": r'^<section id="exception-hierarchy">$',
        "end": r"</section>", "quotes": [
            "BaseException ├── BaseExceptionGroup ├── GeneratorExit ├── KeyboardInterrupt ├── SystemExit └── Exception",
        ],
    },
    "pytest_exit_code_conventions": {
        "doc": "pytest_exit_codes", "kind": "span",
        "start": r'<section id="exit-codes">',
        "end": r"</section>", "quotes": [
            "Test execution was interrupted by the user",
            "Internal error happened while executing tests",
            "No tests were collected",
        ],
    },
    "pytest_documentation_version": {
        "doc": "pytest_options", "kind": "span",
        "start": r"^\s*VERSION: '9\.1',$", "end": r"^\s*VERSION: '9\.1',$",
        "quotes": ["VERSION: '9.1'"]
    },
    "automake_html_exit_conventions": {
        "doc": "automake_html", "kind": "span",
        "start": r"^<h1[^>]*>Scripts-based Testsuites",
        "end": r"^</section>$", "quotes": [
            "an exit status of 0 from a test script will denote a success",
            "an exit status of 77 a skipped test",
            "an exit status of 99 a hard error",
        ],
    },
    "automake_source_exit_conventions": {
        "doc": "automake_texi", "kind": "span",
        "start": r"^When no test protocol is in use, an exit status of 0 from a test script will$",
        "end": r"^a hard error, and any other exit status will denote a failure\.$", "quotes": [
            "an exit status of 0 from a test script will denote a success",
            "an exit status of 77 a skipped test",
            "an exit status of 99 a hard error",
            "any other exit status will denote a failure",
        ],
    },
    "automake_source_hard_error": {
        "doc": "automake_texi", "kind": "span",
        "start": r"^Many testing environments and frameworks distinguish between test failures$",
        "end": r"^@node Simple Tests$", "quotes": [
            "happens when e.g., the set-up of a test case scenario fails",
        ],
    },
    "automake_version": {
        "doc": "automake_version", "kind": "span",
        "start": r"^@set VERSION 1\.19$", "end": r"^@set VERSION 1\.19$",
        "quotes": ["@set VERSION 1.19"],
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_lines(data: bytes) -> list[str]:
    """Split only on LF so RFC form-feeds do not shift line numbers."""
    return [line.removesuffix("\r") for line in data.decode("utf-8").split("\n")]


def normalize(value: str) -> str:
    return " ".join(value.split())


def html_visible(value: str) -> str:
    return html.unescape(re.sub(r"<[^>]*>", " ", value))


def find_one(lines: list[str], pattern: str, start: int = 0) -> int:
    rx = re.compile(pattern)
    hits = [i for i in range(start, len(lines)) if rx.search(lines[i])]
    if len(hits) != 1:
        raise ValueError(f"anchor {pattern!r}: expected one match after line {start + 1}, found {len(hits)}")
    return hits[0]

def find_next(lines: list[str], pattern: str, start: int) -> int:
    """Find the first end delimiter at or after a unique start anchor."""
    rx = re.compile(pattern)
    for i in range(start, len(lines)):
        if rx.search(lines[i]):
            return i
    raise ValueError(f"end delimiter {pattern!r} not found after line {start + 1}")


def closing_brace(lines: list[str], start: int) -> int:
    """Find matching C brace while ignoring quoted strings and comments."""
    depth = 0
    opened = False
    in_block = False
    in_string = None
    escaped = False
    for i in range(start, len(lines)):
        line = lines[i]
        j = 0
        while j < len(line):
            ch = line[j]
            nxt = line[j + 1] if j + 1 < len(line) else ""
            if in_block:
                if ch == "*" and nxt == "/":
                    in_block = False
                    j += 2
                    continue
                j += 1
                continue
            if in_string:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == in_string:
                    in_string = None
                j += 1
                continue
            if ch == "/" and nxt == "*":
                in_block = True
                j += 2
                continue
            if ch == "/" and nxt == "/":
                break
            if ch in ("\"", "'"):
                in_string = ch
                j += 1
                continue
            if ch == "{":
                depth += 1
                opened = True
            elif ch == "}":
                depth -= 1
                if opened and depth == 0:
                    return i
            j += 1
    raise ValueError("unclosed brace block")


def locate(spec: dict, lines: list[str]) -> tuple[int, int]:
    start = find_one(lines, spec["start"])
    if spec["kind"] == "block":
        end = closing_brace(lines, start)
    elif spec["kind"] == "span":
        end = find_next(lines, spec["end"], start)
    else:
        raise ValueError(f"unknown locator kind: {spec['kind']}")
    if end < start:
        raise ValueError("locator end precedes start")
    return start + 1, end + 1


def quote_matches(spec: dict, doc_meta: dict, lines: list[str], bounds: tuple[int, int]) -> list[dict]:
    start, end = bounds
    excerpt = "\n".join(lines[start - 1:end])
    searchable = html_visible(excerpt) if doc_meta["format"] == "html" else excerpt
    haystack = normalize(searchable)
    result = []
    for quote in spec["quotes"]:
        result.append({"quote": quote, "matched": normalize(quote) in haystack})
    return result


def _version_identity(doc_id: str, text: str, pytest_version: str | None, automake_version: str | None) -> dict:
    title = None
    version = None
    extra = {}
    if doc_id == "linux_tcp6":
        m = re.search(r"^\s*\*\s*(TCP over IPv6)$", text, re.M)
        title, version = (m.group(1), "Linux v7.2") if m else (None, "Linux v7.2")
    elif doc_id == "linux_tcp4":
        m = re.search(r"^\s*\*\s*(IPv4 specific functions)$", text, re.M)
        title, version = (m.group(1), "Linux v7.2") if m else (None, "Linux v7.2")
    elif doc_id == "linux_proc_net_tcp":
        m = re.search(r"^([^\n]+ variables)$", text, re.M)
        title, version = (m.group(1).strip(), "Linux v7.2") if m else (None, "Linux v7.2")
    elif doc_id == "rfc4291":
        t = re.search(r"^\s+(IP Version 6 Addressing Architecture)\s*$", text, re.M)
        n = re.search(r"^Request for Comments:\s*(\d+)", text, re.M)
        d = re.search(r"^\s+(February 2006)\s*$", text, re.M)
        title = t.group(1) if t else None
        version = f"RFC {n.group(1)}" if n else None
        extra["publication_date"] = d.group(1) if d else None
    elif doc_id in ("python_exceptions", "pytest_exit_codes", "automake_html"):
        m = re.search(r"<title>(.*?)</title>", text, re.S | re.I)
        title = html.unescape(m.group(1)).strip() if m else None
        if doc_id == "python_exceptions":
            v = re.search(r"Python\s+(\d+\.\d+(?:\.\d+)?)\s+documentation", title or "")
            version = f"Python {v.group(1)}" if v else None
            u = re.search(r"Last updated on ([^<]+?)\.", text)
            extra["last_updated"] = u.group(1) if u else None
        elif doc_id == "pytest_exit_codes":
            version = pytest_version
            g = re.search(r"<!-- Generated with (.*?) -->", text)
            extra["generated_with"] = g.group(1) if g else None
        else:
            v = re.search(r"Automake[^0-9]{0,20}([0-9]+\.[0-9]+(?:\.[0-9]+)?)", html_visible(text), re.I)
            version = f"Automake {v.group(1)}" if v else None
    elif doc_id == "pytest_options":
        title = "pytest documentation build options"
        m = re.search(r"\bVERSION:\s*'([^']+)'", text)
        version = f"pytest documentation {m.group(1)}" if m else None
    elif doc_id == "automake_texi":
        m = re.search(r"^@settitle\s+(.+)$", text, re.M)
        title = m.group(1).strip() if m else None
        version = f"Automake {automake_version}" if automake_version else None
    elif doc_id == "automake_version":
        title = "Automake version metadata"
        m = re.search(r"^@set VERSION (.+)$", text, re.M)
        version = f"Automake {m.group(1)}" if m else None
        u = re.search(r"^@set UPDATED (.+)$", text, re.M)
        extra["updated"] = u.group(1) if u else None
    return {"title": title, "version": version, **extra}


def derive_documents(doc_data: dict[str, bytes]) -> tuple[dict, dict, list[str]]:
    """Derive page identity and all line/quote pins from the captured bytes."""
    identities = {}
    failures = []
    pytest_version = None
    automake_version = None
    if "pytest_options" in doc_data:
        m = re.search(rb"\bVERSION:\s*'([^']+)'", doc_data["pytest_options"])
        if m:
            pytest_version = "pytest documentation " + m.group(1).decode("ascii", "replace")
    if "automake_version" in doc_data:
        m = re.search(rb"^@set VERSION (.+)$", doc_data["automake_version"], re.M)
        if m:
            automake_version = m.group(1).decode("utf-8", "replace")
    for doc_id, data in doc_data.items():
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            failures.append(f"{doc_id}: UTF-8 decode failed: {exc}")
            continue
        identities[doc_id] = _version_identity(doc_id, text, pytest_version, automake_version)
    pins = {}
    for name, spec in PINS.items():
        doc_id = spec["doc"]
        if doc_id not in doc_data:
            pins[name] = {"doc": doc_id, "status": "not-evaluated", "reason": "source-unavailable"}
            continue
        try:
            lines = source_lines(doc_data[doc_id])
            bounds = locate(spec, lines)
            checks = quote_matches(spec, DOCS[doc_id], lines, bounds)
            record = {
                "doc": doc_id,
                "locator": {k: v for k, v in spec.items() if k != "quotes"},
                "ranges": [[bounds[0], bounds[1]]],
                "verbatim": "\n".join(lines[bounds[0] - 1:bounds[1]]),
                "verbatim_sha256": sha256("\n".join(lines[bounds[0] - 1:bounds[1]]).encode("utf-8")),
                "quotes": checks,
            }
            missing = [q["quote"] for q in checks if not q["matched"]]
            if missing:
                record["status"] = "failed"
                record["error"] = "quotes-not-found: " + "; ".join(missing)
                failures.append(f"{name}: {record['error']}")
            else:
                record["status"] = "located"
            pins[name] = record
        except (ValueError, re.error, UnicodeError) as exc:
            pins[name] = {"doc": doc_id, "status": "failed", "error": str(exc)}
            failures.append(f"{name}: {exc}")
    return identities, pins, failures


class _Redirects(urllib.request.HTTPRedirectHandler):
    def __init__(self):
        super().__init__()
        self.chain = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.chain.append({"status": code, "from": req.full_url, "to": newurl})
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_url(url: str) -> dict:
    redirects = _Redirects()
    opener = urllib.request.build_opener(redirects)
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": USER_AGENT})
    try:
        with opener.open(req, timeout=TIMEOUT) as response:
            data = response.read()
            headers = response.headers
            return {
                "status": "fetched", "http_status": response.status,
                "final_url": response.geturl(), "redirects": redirects.chain,
                "headers": {k: headers.get(k) for k in ("Content-Type", "Last-Modified", "ETag") if headers.get(k)},
                "data": data,
            }
    except urllib.error.HTTPError as exc:
        status = "gone" if exc.code in (404, 410) else "unreachable"
        return {"status": status, "http_status": exc.code, "final_url": exc.geturl(),
                "redirects": redirects.chain, "headers": {}, "error": f"HTTP {exc.code} {exc.reason}"}
    except (urllib.error.URLError, TimeoutError, OSError, ssl.SSLError) as exc:
        return {"status": "unreachable", "http_status": None, "final_url": None,
                "redirects": redirects.chain, "headers": {}, "error": f"{type(exc).__name__}: {exc}"}


def extract_member(archive: bytes, member_name: str) -> bytes:
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:xz") as tf:
        member = tf.getmember(member_name)
        if not member.isfile():
            raise ValueError(f"archive member is not a regular file: {member_name}")
        stream = tf.extractfile(member)
        if stream is None:
            raise ValueError(f"cannot read archive member: {member_name}")
        return stream.read()


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp_name, 0o644)
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def _source_record(spec: dict, fetched: dict) -> dict:
    record = {k: v for k, v in fetched.items() if k != "data"}
    record["url"] = spec["url"]
    record["saved_as"] = spec["saved_as"]
    if spec.get("note"):
        record["note"] = spec["note"]
    if fetched.get("status") == "fetched":
        data = fetched["data"]
        record["sha256"] = sha256(data)
        record["bytes"] = len(data)
    return record


def capture(fetcher=fetch_url) -> tuple[dict, dict[str, bytes], list[str], list[str]]:
    source_records = {}
    doc_data: dict[str, bytes] = {}
    failures = []
    unevaluated = []
    for source_id, spec in SOURCES.items():
        fetched = fetcher(spec["url"])
        source_records[source_id] = _source_record(spec, fetched)
        if fetched["status"] != "fetched":
            msg = f"{source_id}: {fetched.get('error', fetched['status'])}"
            (failures if fetched["status"] == "gone" else unevaluated).append(msg)
            continue
        data = fetched["data"]
        atomic_write(ROOT / spec["saved_as"], data)
        if spec.get("members"):
            for doc_id, member_name in spec["members"].items():
                try:
                    member_data = extract_member(data, member_name)
                    doc_data[doc_id] = member_data
                    atomic_write(ROOT / DOCS[doc_id]["saved_as"], member_data)
                    source_records[source_id].setdefault("members", {})[doc_id] = {
                        "member": member_name, "saved_as": DOCS[doc_id]["saved_as"],
                        "sha256": sha256(member_data), "bytes": len(member_data),
                    }
                except (KeyError, OSError, tarfile.TarError, lzma_error(), ValueError) as exc:
                    failures.append(f"{source_id}:{member_name}: {type(exc).__name__}: {exc}")
        else:
            doc_id = source_id
            if source_id == "automake_page":
                doc_id = "automake_html"
            doc_data[doc_id] = data
    # Record the requested tag and the resolved commit observed for v7.2.
    source_records["linux_tag"] = {
        "tag": LINUX_TAG, "commit": LINUX_TAG_COMMIT, "note": LINUX_TAG_NOTE,
        "remote": "https://github.com/torvalds/linux",
    }
    return source_records, doc_data, failures, unevaluated


def lzma_error():
    # Lazily named to keep the import surface minimal on Python builds without lzma.
    try:
        import lzma
        return lzma.LZMAError
    except ImportError:
        return OSError


def make_record() -> tuple[dict, list[str], list[str]]:
    sources, doc_data, failures, unevaluated = capture()
    identities, pins, pin_failures = derive_documents(doc_data)
    failures.extend(pin_failures)
    documents = {}
    for doc_id, data in doc_data.items():
        documents[doc_id] = {
            "saved_as": DOCS[doc_id]["saved_as"], "format": DOCS[doc_id]["format"],
            "sha256": sha256(data), "bytes": len(data), "identity": identities.get(doc_id, {}),
        }
    for name, pin in pins.items():
        if pin["status"] == "not-evaluated":
            unevaluated.append(f"{name}: {pin['reason']}")
    return {
        "schema": SCHEMA,
        "pinned_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pinned_by": Path(__file__).name,
        "sources": sources,
        "documents": documents,
        "pins": pins,
        "failures": failures,
        "unevaluated": unevaluated,
        "linux_tag": {"tag": LINUX_TAG, "commit": LINUX_TAG_COMMIT, "note": LINUX_TAG_NOTE},
    }, failures, unevaluated




def read_record(path: Path = PINS_PATH) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema") != SCHEMA:
        raise ValueError(f"unsupported pins schema in {path}")
    return value


def verify_record(record: dict, fetcher=fetch_url) -> tuple[int, list[str]]:
    problems = []
    unevaluated = []
    fresh_sources = {}
    fresh_docs: dict[str, bytes] = {}
    # Re-fetch each configured URL; source digests are compared byte-for-byte.
    for source_id, spec in SOURCES.items():
        fresh = fetcher(spec["url"])
        old = record.get("sources", {}).get(source_id, {})
        if fresh["status"] == "gone":
            problems.append(f"{source_id}: gone ({fresh.get('error')})")
            continue
        if fresh["status"] != "fetched":
            unevaluated.append(f"{source_id}: unreachable ({fresh.get('error')})")
            continue
        data = fresh["data"]
        fresh_sources[source_id] = _source_record(spec, fresh)
        if old.get("status") != "fetched" or not old.get("sha256"):
            unevaluated.append(f"{source_id}: no baseline digest was recorded")
        elif sha256(data) != old["sha256"]:
            problems.append(f"{source_id}: SHA-256 changed (recorded {old['sha256']}, observed {sha256(data)})")
        if spec.get("members"):
            try:
                for doc_id, member in spec["members"].items():
                    member_data = extract_member(data, member)
                    fresh_docs[doc_id] = member_data
                    member_old = old.get("members", {}).get(doc_id, {})
                    if not member_old.get("sha256"):
                        unevaluated.append(f"{doc_id}: no baseline member digest was recorded")
                    elif sha256(member_data) != member_old["sha256"]:
                        problems.append(f"{doc_id}: member SHA-256 changed")
            except (KeyError, OSError, tarfile.TarError, lzma_error(), ValueError) as exc:
                problems.append(f"{source_id}: archive member extraction failed: {type(exc).__name__}: {exc}")
        else:
            doc_id = "automake_html" if source_id == "automake_page" else source_id
            fresh_docs[doc_id] = data
    # Check local raw copies independently from remote contents.
    for doc_id, meta in record.get("documents", {}).items():
        path = ROOT / meta.get("saved_as", "")
        try:
            local_data = path.read_bytes()
        except OSError as exc:
            problems.append(f"{doc_id}: saved raw copy unavailable: {exc}")
            continue
        if sha256(local_data) != meta.get("sha256"):
            problems.append(f"{doc_id}: saved raw copy SHA-256 mismatch")
    for source_id, old in record.get("sources", {}).items():
        if source_id in SOURCES and old.get("status") == "fetched":
            path = ROOT / SOURCES[source_id]["saved_as"]
            try:
                local_data = path.read_bytes()
            except OSError as exc:
                problems.append(f"{source_id}: saved source copy unavailable: {exc}")
            else:
                if sha256(local_data) != old.get("sha256"):
                    problems.append(f"{source_id}: saved source SHA-256 mismatch")
    identities, fresh_pins, derive_failures = derive_documents(fresh_docs)
    problems.extend(derive_failures)
    for name, current in fresh_pins.items():
        old = record.get("pins", {}).get(name)
        if old is None:
            problems.append(f"{name}: pin missing from baseline")
        elif old.get("status") == "not-evaluated":
            if current.get("status") != "not-evaluated":
                unevaluated.append(f"{name}: no baseline evidence was recorded for comparison")
        elif old != current:
            problems.append(f"{name}: located pin/quote record differs from baseline")
    for name in record.get("pins", {}):
        if name not in PINS:
            problems.append(f"{name}: baseline pin is not defined by this pin.py")
    for doc_id, data in fresh_docs.items():
        old = record.get("documents", {}).get(doc_id)
        if old is None:
            unevaluated.append(f"{doc_id}: no baseline document digest was recorded")
        elif sha256(data) != old.get("sha256"):
            # Source hashes normally caught this; member hashes are checked above.
            if doc_id not in ("automake_texi", "automake_version"):
                problems.append(f"{doc_id}: document SHA-256 changed")
        if old is not None and old.get("identity") != identities.get(doc_id, {}):
            problems.append(f"{doc_id}: page title/version identity changed")
    if problems:
        status = 1
    elif unevaluated:
        status = 2
    else:
        status = 0
    for line in problems:
        print(f"FAIL {line}")
    for line in unevaluated:
        print(f"NOT-EVALUATED {line}")
    return status, problems + unevaluated


def _artifact_selfcheck() -> tuple[int, str]:
    if not PINS_PATH.exists():
        return 0, "artifact check skipped (pins.json absent)"
    try:
        record = read_record()
        docs = {}
        for doc_id, meta in record.get("documents", {}).items():
            data = (ROOT / meta["saved_as"]).read_bytes()
            if sha256(data) != meta.get("sha256"):
                return 1, f"artifact check failed: {doc_id} saved digest mismatch"
            docs[doc_id] = data
        identities, pins, failures = derive_documents(docs)
        if failures:
            return 1, "artifact check failed: " + "; ".join(failures)
        for doc_id, meta in record.get("documents", {}).items():
            if meta.get("identity") != identities.get(doc_id, {}):
                return 1, f"artifact check failed: {doc_id} identity differs"
        if record.get("pins") != pins:
            return 1, "artifact check failed: pins.json does not re-derive from raw copies"
        referenced = {meta["saved_as"] for meta in record.get("documents", {}).values()}
        for source in record.get("sources", {}).values():
            if source.get("status") == "fetched" and source.get("saved_as"):
                referenced.add(source["saved_as"])
            for member in source.get("members", {}).values():
                referenced.add(member["saved_as"])
        raw_files = {str(p.relative_to(ROOT)) for p in RAW.rglob("*") if p.is_file()}
        orphans = sorted(raw_files - referenced)
        if orphans:
            return 1, "artifact check failed: unreferenced raw files: " + ", ".join(orphans)
        return 0, f"artifact check passed ({len(docs)} raw documents re-derived)"
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        return 1, f"artifact check failed: {type(exc).__name__}: {exc}"


def _selftest() -> int:
    checks = []
    def check(name, callback):
        try:
            callback()
            checks.append((name, True, ""))
        except Exception as exc:
            checks.append((name, False, f"{type(exc).__name__}: {exc}"))

    def test_lines_and_formfeed():
        got = source_lines(b"a\n\fb\nc\n")
        assert got == ["a", "\fb", "c", ""]
    def test_block_lexing():
        lines = ['void f() {', '  const char *s = "}";', '  /* { ignored */', '  if (1) {', '  }', '}']
        assert closing_brace(lines, 0) == 5
    def test_span_and_anchor_uniqueness():
        lines = ["start", "body", "end"]
        assert locate({"kind": "span", "start": "^start$", "end": "^end$"}, lines) == (1, 3)
        duplicates = ["start", "body", "end", "start", "end"]
        try:
            find_one(duplicates, "^start$")
        except ValueError:
            return
        raise AssertionError("duplicate anchor accepted")
    def test_html_quote():
        meta = {"format": "html"}
        spec = {"quotes": ["A < b & c"]}
        checks_ = quote_matches(spec, meta, ["<p>A &lt; b &amp; <em>c</em></p>"], (1, 1))
        assert checks_[0]["matched"]
    def test_digest_control():
        payload = b"pinned bytes"
        assert sha256(payload) == hashlib.sha256(payload).hexdigest()
        assert sha256(payload) != sha256(payload + b"x")
    def test_word_bound():
        for spec in PINS.values():
            for quote in spec["quotes"]:
                assert len(quote.split()) <= 25, (spec["doc"], quote)
    for name, fn in (
        ("LF line counting preserves form-feed pages", test_lines_and_formfeed),
        ("C brace scanner ignores strings and comments", test_block_lexing),
        ("span locators and duplicate-anchor rejection", test_span_and_anchor_uniqueness),
        ("HTML entities and tags in quote matching", test_html_quote),
        ("SHA-256 control detects changed bytes", test_digest_control),
        ("citation quotes stay within 25 words", test_word_bound),
    ):
        check(name, fn)
    artifact_code, artifact_message = _artifact_selfcheck()
    checks.append(("saved artifact re-derivation", artifact_code == 0, artifact_message))
    for name, ok, reason in checks:
        print(("PASS " if ok else "FAIL ") + name + (f": {reason}" if reason else ""))
    failed = sum(not ok for _, ok, _ in checks)
    print(f"SELFTEST {'PASS' if not failed else 'FAIL'} checks={len(checks)} failed={failed}")
    return 1 if failed else 0


def _pin() -> int:
    record, failures, unevaluated = make_record()
    data = (json.dumps(record, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    atomic_write(PINS_PATH, data)
    for source_id, source in record["sources"].items():
        if source_id == "linux_tag":
            print(f"PIN {source_id} {source['tag']} commit={source['commit']}")
        elif source.get("status") == "fetched":
            print(f"PIN {source_id} bytes={source['bytes']} sha256={source['sha256']}")
        else:
            print(f"{source.get('status', 'unknown').upper()} {source_id}: {source.get('error', '')}")
    for name, pin in record["pins"].items():
        print(f"{'PIN' if pin['status'] == 'located' else 'NOT-EVALUATED' if pin['status'] == 'not-evaluated' else 'FAIL'} {name}: {pin.get('ranges', pin.get('reason', pin.get('error')))}")
    code = 1 if failures else 2 if unevaluated else 0
    print(f"WROTE {PINS_PATH} failures={len(failures)} unevaluated={len(unevaluated)} exit={code}")
    return code


def _verify() -> int:
    record = read_record()
    code, details = verify_record(record)
    print(f"VERIFY {'PASS' if code == 0 else 'FAIL' if code == 1 else 'NOT-EVALUATED'} issues={len(details)} exit={code}")
    return code


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--verify", action="store_true", help="re-fetch each URL and compare raw digests and pin excerpts")
    group.add_argument("--selftest", action="store_true", help="run offline implementation and artifact self-tests")
    args = parser.parse_args(argv)
    try:
        if args.selftest:
            return _selftest()
        if args.verify:
            return _verify()
        return _pin()
    except KeyboardInterrupt:
        print("COULD-NOT-EVALUATE: interrupted", file=sys.stderr)
        return 2
    except BaseException as exc:
        print(f"COULD-NOT-EVALUATE: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
