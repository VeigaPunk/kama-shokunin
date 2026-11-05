#!/usr/bin/env python3
"""Build the fabricated-but-hash-consistent fixture repo for round-86 C3.

Two rows against the real, fetchable llama.cpp b12111 server README URL:
  row 'fab'  - both anchors carry a fabricated body that differs from upstream,
               with the header digest correctly computed over the fabricated body
               (hash-consistent). Must grade mismatch, never verified.
  row 'lie'  - one anchor declares a digest that does not match its stored body
               (digest-lie -> bad), the other is hash-consistent-but-fabricated
               (mismatch). Row takes the worst: bad.
"""
import hashlib
import pathlib
import subprocess

D = pathlib.Path("/fast/scratch/hyaku/kama-r86/EX03OriginFetch/fixture")
URL = "https://raw.githubusercontent.com/ggml-org/llama.cpp/b12111/tools/server/README.md"
HEADER = ("engine", "ref", "newest", "verdict", "date", "quote_pin", "line_pin",
          "quote_newest", "line_newest", "extract_pin", "extract_newest", "note")


def write_anchor(rel, digest, ref, start, end, body):
    p = D / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"# url={URL} sha256={digest} ref={ref} lines={start}-{end}\n{body}",
                 encoding="utf-8")


FAB = ("FABRICATED BODY - this text was never acquired from the named URL.\n"
       "Second fabricated line, one byte different from anything upstream.\n")
LIE = "LIE BODY - the declared digest deliberately does not match this body.\n"

write_anchor("corpus/anchors/fab-pin.txt", hashlib.sha256(FAB.encode()).hexdigest(),
             "fab-pin", 479, 491, FAB)
write_anchor("corpus/anchors/fab-newest.txt", hashlib.sha256(FAB.encode()).hexdigest(),
             "fab-newest", 479, 491, FAB)
write_anchor("corpus/anchors/lie-pin.txt", "0" * 64, "lie-pin", 479, 491, LIE)
write_anchor("corpus/anchors/lie-newest.txt", hashlib.sha256(LIE.encode()).hexdigest(),
             "lie-newest", 479, 491, LIE)

rows = D / "registry/pin-recheck-rows.tsv"
rows.parent.mkdir(parents=True, exist_ok=True)


def row(engine, ref, pin, newest, note):
    cells = [engine, ref, "v2", "holds", "2026-11-04", "q", "3", "q", "3", pin, newest, note]
    return "\t".join(cells) + "\n"


rows.write_text("\t".join(HEADER) + "\n"
                + row("fixture", "fab", "corpus/anchors/fab-pin.txt",
                      "corpus/anchors/fab-newest.txt", "fabricated hash-consistent pair")
                + row("fixture", "lie", "corpus/anchors/lie-pin.txt",
                      "corpus/anchors/lie-newest.txt", "digest-lie pin + fabricated newest"),
                encoding="utf-8")

subprocess.run(["git", "-C", str(D), "init", "-q"], check=True)
top = subprocess.check_output(["git", "-C", str(D), "rev-parse", "--show-toplevel"],
                              text=True).strip()
assert top == str(D), f"toplevel mismatch: {top!r} != {D}"
subprocess.run(["git", "-C", str(D), "config", "user.email", "ex03@fixture.invalid"], check=True)
subprocess.run(["git", "-C", str(D), "config", "user.name", "EX03OriginFetch fixture"], check=True)
subprocess.run(["git", "-C", str(D), "add", "-A"], check=True)
subprocess.run(["git", "-C", str(D), "commit", "-q",
                "-m", "round-86 C3 fabricated-pair fixture"], check=True)
print(subprocess.check_output(["git", "-C", str(D), "rev-parse", "HEAD"], text=True).strip())
