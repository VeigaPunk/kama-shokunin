#!/usr/bin/env python3
"""Round-58 C1 fixture generator: derive the benign and no-op variants of the committed
round-56 battery by exact single-anchor text edits. Usage: make-variants.py GENUINE OUTDIR.
Every edit asserts its anchor occurs exactly once; a violation aborts (exit 2)."""
import pathlib
import sys

G = pathlib.Path(sys.argv[1]).read_text()
OUT = pathlib.Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

START = "    results = []\n"
END = "    return 0 if all(results) else 1\n"


def once(text, old, new):
    if text.count(old) != 1:
        raise SystemExit(f"anchor not unique ({text.count(old)}): {old!r}")
    return text.replace(old, new)


def legs():
    i = G.index(START) + len(START)
    j = G.index(END)
    return G[:i], G[i:j], G[j:]


def indent(block, pad):
    return "".join((pad + ln if ln.strip() else ln) for ln in block.splitlines(True))


V = {}
V["genuine"] = G
# --- benign: behaviour-preserving rewrites that must stay accepted ---
V["B1-rename-comment"] = G.replace("results", "outcomes") .replace(
    "    OUT.mkdir(parents=True, exist_ok=True)\n",
    "    # create the receipt directory first\n    OUT.mkdir(parents=True, exist_ok=True)\n", 1)
V["B2-helper-leg"] = once(G, "def main():\n",
                          "def _leg(label, counter, expected, out):\n    return run(label, counter, expected, out)\n\n\ndef main():\n")
V["B2-helper-leg"] = V["B2-helper-leg"].replace('results.append(run("base-old-counter"', 'results.append(_leg("base-old-counter"') \
    .replace('results.append(run("round56-counter"', 'results.append(_leg("round56-counter"') \
    .replace('results.append(run("m-drop-ldaudit"', 'results.append(_leg("m-drop-ldaudit"')
V["B3-concat-labels"] = G.replace('run("base-old-counter"', 'run("base-" + "old-counter"') \
    .replace('run("round56-counter"', 'run("round56-" + "counter"')
# --- no-op: roster literal intact, battery does not really run ---
pre, body, post = legs()
V["N01-calls-removed"] = pre + '    print("battery ok")\n' + post
V["N02-if-false"] = pre + "    if False:\n" + indent(body, "    ") + post
V["N03-unused-function"] = once(G, "def main():\n", "def _legacy_main():\n").replace(
    'if __name__ == "__main__":', "def main():\n    return 0\n\n\nif __name__ == \"__main__\":")
V["N04-early-return"] = once(G, '    scratch.mkdir(parents=True, exist_ok=True)\n',
                             '    scratch.mkdir(parents=True, exist_ok=True)\n    return 0\n')
V["N05-env-guard"] = pre + '    if os.environ.get("KAMA_R56_RUN_BATTERY") == "1":\n' + indent(body, "    ") + post
V["N06-run-body-noop"] = once(G, "def run(label, counter, expected, out):\n",
                              'def run(label, counter, expected, out):\n    print(f"{label}: pass")\n    return True\n')
V["N07-mutant-assert-noop"] = once(G, '(closure target-sentence wording)."""\n',
                                   '(closure target-sentence wording)."""\n    return True\n')
V["N08-main-not-invoked"] = once(G, "    raise SystemExit(main())\n", "    pass\n")
V["N09-empty-loop"] = pre + "    for _leg in []:\n" + indent(body, "    ") + post
V["N10-run-rebound"] = once(G, "def main():\n", "run = lambda *a, **k: True\n\n\ndef main():\n")
V["N11-try-else"] = (pre + '    try:\n        raise RuntimeError("battery disabled")\n    except RuntimeError:\n        pass\n    else:\n'
                     + indent(body, "        ") + post)
for name, text in V.items():
    compile(text, name, "exec")
    (OUT / f"{name}.py").write_text(text)
print(len(V), "variants")
