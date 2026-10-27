#!/usr/bin/env python3
"""Build (or rebuild) the six fixture repositories used by the SE01PredicateSandbox report.

Usage:  python3 build_fixtures.py <workdir> [--committed-copies]

Every fixture is a throwaway git repo under <workdir>; each is initialised with
`git -C D init -q`, the toplevel is asserted to equal D *before* the first commit, and the
identity is passed per command (`-c user.name=fixture -c user.email=fixture@localhost`)
so nothing is written to any git config. The receipt is the committed lane receipt
copied next to this script (`repro/receipt.json`), except fixC, which gets a schema- and
hash-correct receipt with one 200 000-deep capture body.

fixA  one row, predicate = 100 000 x `c['tags']`   -> ast.parse RecursionError (counter crash)
fixB  one row, predicate = 181-byte nested comp    -> one credited row, 12.7 s
fixC  valid receipt, 200k-deep JSON body           -> receipt_caps RecursionError (counter crash)
fixD  14 rows over 14 population lines, row 0 = the bomb -> met=True, ~255 s
fixE  4 rows, 2 population lines, one row = genexp whose body reads c -> silent None
fixF  14 rows, 14 population lines, every predicate cheap -> met=True, ~0.4 s
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RECEIPT = os.path.join(HERE, "receipt.json")
HEADER = "id\tpath\tline\tquote\tpredicate\tverdict\tobserved\treason\n"
BOMB = ("[[[t for t in c['show']['model_info']['tokenizer.ggml.tokens']] "
        "for _ in c['show']['model_info']['tokenizer.ggml.tokens']] "
        "for _ in c['show']['model_info']['tokenizer.ggml.tokens']]")
DEEP = "c" + "['tags']" * 100000
QUOTE = "live Ollama api tags capture inference"
CONF = "confirmed"


def repo(root, name, skill_lines, rows, receipt_bytes):
    d = os.path.join(root, name)
    os.makedirs(os.path.join(d, "registry"), exist_ok=True)
    os.makedirs(os.path.join(d, ".ufo", "waves", "round-60", "live"), exist_ok=True)
    with open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(skill_lines) + "\n")
    with open(os.path.join(d, "registry", "ollama-live-claims-r60.tsv"), "w", encoding="utf-8") as fh:
        fh.write(HEADER + "".join("\t".join(r) + "\n" for r in rows))
    with open(os.path.join(d, ".ufo", "waves", "round-60", "live", "receipt.json"), "wb") as fh:
        fh.write(receipt_bytes)
    subprocess.run(["git", "-C", d, "init", "-q"], check=True)
    top = subprocess.run(["git", "-C", d, "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True, check=True).stdout.strip()
    assert os.path.realpath(top) == os.path.realpath(d), f"toplevel mismatch: {top} != {d}"
    subprocess.run(["git", "-C", d, "add", "-A"], check=True)
    subprocess.run(["git", "-C", d, "-c", "user.name=fixture", "-c", "user.email=fixture@localhost",
                    "commit", "-qm", "fixture"], check=True)
    rev = subprocess.run(["git", "-C", d, "rev-parse", "--short", "HEAD"],
                         capture_output=True, text=True, check=True).stdout.strip()
    print(f"{name}: {rev} rows={len(rows)} pop_lines={len(skill_lines)}")
    return d


def nested_receipt(depth=200000):
    body = "[" * depth + "]" * depth
    rec = {"schema": "kama-ollama-live/v1",
           "captures": {"x": {"body": body, "sha256": hashlib.sha256(body.encode()).hexdigest()}}}
    return json.dumps(rec).encode()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    root = sys.argv[1]
    os.makedirs(root, exist_ok=True)
    receipt = open(RECEIPT, "rb").read()
    line = ("The live Ollama api/tags capture is an inference about expires_at and the loaded model.")

    repo(root, "fixA", [line],
         [["R1", "SKILL.md", "1", "live Ollama api/tags capture", DEEP, CONF, "", ""]], receipt)

    repo(root, "fixB", [line],
         [["R1", "SKILL.md", "1", "live Ollama api/tags capture", BOMB, CONF, "", ""]], receipt)

    repo(root, "fixC", [line],
         [["R1", "SKILL.md", "1", "live Ollama api/tags capture", "len(c) > 0", CONF, "", ""]],
         nested_receipt())

    rows_d = []
    for i in range(14):
        pred = BOMB if i == 0 else "c['version']['version'] != ''"
        rows_d.append([f"R{i}", "SKILL.md", str(i + 1), QUOTE, pred, CONF, "", ""])
    repo(root, "fixD", [f"{QUOTE} line{i}" for i in range(14)], rows_d, receipt)

    honest = [
        ("Claim one: the live Ollama api/tags capture lists exactly one model.",
         "len(c['tags']['models']) == 1"),
        ("Claim two: the Ollama api/tags model name equals the generate response model.",
         "c['tags']['models'][0]['name'] == c['generate']['model']"),
        ("Claim four: the Ollama version capture is a non-empty inference about version.",
         "c['version']['version'] != ''"),
        ("Claim six: every Ollama api/ps digest matches the api/tags digest inference.",
         "all(m['digest'] == c['tags']['models'][0]['digest'] for m in c['ps-after']['models'])"),
    ]
    repo(root, "fixE", [h for h, _ in honest],
         [[f"R{i}", "SKILL.md", str(i + 1), q, p, CONF, "", ""]
          for i, (q, p) in enumerate(honest)], receipt)

    rows_f = [[f"R{i}", "SKILL.md", str(i + 1), QUOTE, "c['version']['version'] != ''", CONF, "", ""]
              for i in range(14)]
    repo(root, "fixF", [f"{QUOTE} line{i}" for i in range(14)], rows_f, receipt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
