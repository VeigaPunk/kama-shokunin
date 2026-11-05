#!/usr/bin/env python3
"""MT01 vacuity probe: the three shadow arms render byte-identical verdicts to a
fixture that carries NO shadow at all, so they cannot discriminate the selector."""
import importlib.util
import os

D = "/fast/scratch/hyaku/kama-r86/MT01SelectorMutants"
BASE = os.path.join(D, "base", "round86-rendered-cells.py")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m = load("base_instrument", BASE)
A = "a" * 40
GOOD = (f"**Current authority (round 85):** Latest measured round: 85. Terminal gate measured at "
        f"`{A}`: {m.GOOD_CMD} printed {m.GOOD_TOKEN}, exit0; receipt `{m.GOOD_RECEIPT}`.")


def line(shadow):
    tree = m.fixture(stale_live=True, shadow=shadow)
    try:
        r = m.grade(tree)
        return (0 if r["mismatches"] == 0 else 1), m.render(r)
    except m.CouldNotEvaluate as exc:
        return 2, f"could-not-evaluate: {exc}"


variants = {
    "no-shadow": "",
    "fenced": "```markdown\n" + GOOD + "\n" + m.GOOD_ROW + "\n```\n",
    "commented": "<!--\n" + GOOD + "\n" + m.GOOD_ROW + "\n-->\n",
    "tilde": "~~~\n" + GOOD + "\n" + m.GOOD_ROW + "\n~~~\n",
    "indented": "    " + GOOD + "\n    " + m.GOOD_ROW + "\n",
}
base = line("")
print(f"baseline no-shadow exit={base[0]} {base[1]}")
same = 0
for name, shadow in variants.items():
    got = line(shadow)
    identical = got == base
    same += identical
    print(f"{name:10s} exit={got[0]} identical_to_no_shadow={identical} {got[1]}")
print(f"IDENTICAL={same}/{len(variants)} (all four shadow arms are indistinguishable "
      f"from a fixture with no shadow)")
