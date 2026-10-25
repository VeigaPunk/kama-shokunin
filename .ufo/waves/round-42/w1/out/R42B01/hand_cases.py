#!/usr/bin/env python3
"""R42B01 C2 hand fixtures the counter generator cannot produce.

Each case builds a fixture dir `d` inside its own export dir `e` (which also
carries tools/digest-ledger.py). The counter's reference (ref_dir) runs in this
process (the counter's cwd); the tool runs as the counter runs it
(cwd=export, --dir <abs d>). Agreement = equal summary line and exit code.
A second reference is computed with cwd = d to expose cwd-sensitive rules.
"""
import hashlib
import importlib.util
import json
import os
import shutil
import sys

CLONE = "/fast/scratch/kama-r42/seats/R42B01/clone"
SEAT = "/fast/scratch/kama-r42/seats/R42B01"
ROOT = os.path.join(SEAT, "hand")
HDR = "digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote"


def load_counter():
    spec = importlib.util.spec_from_file_location(
        "r42digest", os.path.join(CLONE, "tools", "round42-digest-audit.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_counter()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def put(path, data):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb" if isinstance(data, bytes) else "w") as f:
        f.write(data)


def ledger_text(rows, header=True):
    return "\n".join(([HDR] if header else []) + ["\t".join(r) for r in rows]) + "\n"


CASES = {}


def case(fn):
    CASES[fn.__name__] = fn
    return fn


@case
def uppercase_hex(e, d):
    """Uppercase 64-hex run must not be a token; the lower-case digest must."""
    body = b"payload-upper\n"
    put(os.path.join(d, "data.bin"), body)
    real = sha(body)
    put(os.path.join(d, "doc.md"), f"# d\n{real.upper()}\n{real}\n")
    return "uppercase 64-hex run plus the same digest in lower case"


@case
def hex_65_run(e, d):
    """A 65-char lower-case hex run matches at no offset (neighbour hex char)."""
    body = b"payload-65\n"
    put(os.path.join(d, "data.bin"), body)
    real = sha(body)
    put(os.path.join(d, "doc.md"), f"# d\n{real}f\nf{real}\n{real}\n")
    return "65-hex runs (suffix and prefix) plus the bare digest"


@case
def crlf_docs_and_ledger(e, d):
    """CRLF document and CRLF ledger: token set and note-cell CR handling."""
    body = b"payload-crlf\n"
    put(os.path.join(d, "data.bin"), body)
    real = sha(body)
    unknown, unv = "12" * 32, "34" * 32
    put(os.path.join(d, "doc.md"), f"# d\r\n{real}\r\n{unknown}\r\n{unv}\r\n".encode())
    put(os.path.join(d, "registry", "digest-ledger.tsv"),
        ledger_text([(unv, "unverifiable", "u", "", "", "2026-10-25", "no host copy")]).replace("\n", "\r\n"))
    return "CRLF .md and CRLF ledger (note cell keeps a trailing CR)"


@case
def token_split_by_line_break(e, d):
    """A real blob digest split across a markdown hard break is not a token."""
    body = b"payload-split\n"
    put(os.path.join(d, "data.bin"), body)
    real = sha(body)
    put(os.path.join(d, "doc.md"),
        "# d\n" + real[:32] + "  \n" + real[32:] + "\n" + real[:40] + "\\\n" + real[40:] + "\n")
    return "digest halves joined by a two-space and a backslash markdown break"


@case
def non_utf8_md(e, d):
    """A .md with invalid UTF-8 bytes around a real digest and an unknown token."""
    body = b"payload-binary\n"
    put(os.path.join(d, "data.bin"), body)
    real = sha(body)
    unknown = "56" * 32
    put(os.path.join(d, "doc.md"),
        b"# d\n\xff\xfe\x80 bad bytes\n" + real.encode() + b"\n\xc3\x28 " + unknown.encode()
        + b"\n\xf0\x28\x8c\x28\n")
    return "invalid UTF-8 sequences interleaved with the digests"


@case
def md_symlink(e, d):
    """A .md symlink is skipped; its target inside the dir is a blob, not a doc."""
    body = b"payload-symlink\n"
    put(os.path.join(d, "data.bin"), body)
    real = sha(body)
    put(os.path.join(d, "store", "blob.bin"), b"target-body\n")
    put(os.path.join(d, "doc.md"), f"# d\n{real}\n")
    os.symlink(os.path.join(d, "store", "blob.bin"), os.path.join(d, "link.md"))
    os.symlink("../store/blob.bin", os.path.join(d, "rel-link.md"))
    return "link.md and rel-link.md -> store/blob.bin (bytes are not documents)"


@case
def empty_ledger(e, d):
    """A zero-byte registry/digest-ledger.tsv is an empty ledger, not a doc."""
    body = b"payload-empty-ledger\n"
    put(os.path.join(d, "data.bin"), body)
    real = sha(body)
    put(os.path.join(d, "doc.md"), f"# d\n{real}\n")
    put(os.path.join(d, "registry", "digest-ledger.tsv"), "")
    return "zero-byte ledger file present"


@case
def ledger_without_header(e, d):
    """A ledger whose first line is a data row must not lose that row."""
    body = b"payload-noheader\n"
    put(os.path.join(d, "data.bin"), body)
    real = sha(body)
    unv = "78" * 32
    put(os.path.join(d, "doc.md"), f"# d\n{real}\n{unv}\n")
    put(os.path.join(d, "registry", "digest-ledger.tsv"),
        ledger_text([(unv, "unverifiable", "u", "", "", "2026-10-25", "why")], header=False))
    return "ledger with no header line (first row is data)"


@case
def uppercase_extension(e, d):
    """Suffix match is case-sensitive: doc.MD is not a document, dir.md/ is not one."""
    body = b"payload-ext\n"
    put(os.path.join(d, "data.bin"), body)
    real = sha(body)
    unknown = "9a" * 32
    put(os.path.join(d, "doc.MD"), f"# d\n{real}\n{unknown}\n")
    put(os.path.join(d, "dir.md", "inner.txt"), f"{unknown}\n")
    return "doc.MD and a directory named dir.md"


@case
def relative_external_path(e, d):
    """Ledger external row with a relative path: resolution depends on cwd.

    The counter computes ref_dir in its own process but runs the tool with
    cwd = export, so a relative `path` can resolve to different files.
    """
    body = b"payload-relative\n"
    # the external artifact sits one level above the export dir, i.e. it is
    # reachable as ../payload.bin only when cwd == export
    put(os.path.join(e, "..", "payload.bin"), body)
    real = sha(body)
    put(os.path.join(d, "doc.md"), f"# d\n{real}\n")
    put(os.path.join(d, "registry", "digest-ledger.tsv"),
        ledger_text([(real, "external", "x", "../payload.bin", "", "2026-10-25", "relative path")]))
    return "external row path='../payload.bin' (relative to what?)"


def ref_with_cwd(d):
    here = os.getcwd()
    os.chdir(d)
    try:
        return MOD.ref_dir(d)
    finally:
        os.chdir(here)


def main():
    if os.path.isdir(ROOT):
        shutil.rmtree(ROOT)
    rows = []
    for name, fn in CASES.items():
        e = os.path.join(ROOT, name, "export")
        os.makedirs(os.path.join(e, "tools"))
        shutil.copy2(os.path.join(CLONE, "tools", "digest-ledger.py"),
                     os.path.join(e, "tools", "digest-ledger.py"))
        d = os.path.join(e, "fixture")
        os.makedirs(d)
        desc = fn(e, d)
        want = MOD.ref_dir(d)
        alt = ref_with_cwd(d)
        got, code, err = MOD.run_tool(e, ["scan", "--dir", d])
        agree = got.strip() == MOD.summary(want) and code == MOD.exit_of(want)
        rows.append(dict(case=name, desc=desc, agree=agree,
                         ref=MOD.summary(want), ref_exit=MOD.exit_of(want),
                         ref_cwd_fixture=MOD.summary(alt), ref_cwd_fixture_exit=MOD.exit_of(alt),
                         tool=got.strip(), tool_exit=code,
                         stderr=err.strip()[:200], fixture=d))
    print(json.dumps(rows, indent=1))
    with open(os.path.join(SEAT, "hand-result.json"), "w") as f:
        json.dump(rows, f, indent=1)
    bad = [r for r in rows if not r["agree"]]
    print(f"\nagree={len(rows)-len(bad)}/{len(rows)} disagree={len(bad)}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
