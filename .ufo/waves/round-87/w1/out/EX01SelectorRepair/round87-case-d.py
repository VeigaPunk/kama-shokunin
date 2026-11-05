#!/usr/bin/env python3
"""EX01 case (d) fixtures (plans/round-87-claims.md R1): a list-marker closer, a
blockquote-marked closer and a four-space-indented closer must NOT close a fence.
Each shadow carries a green authority cell plus a GOOD_ROW inside the fence; the
selector must stay red (mismatches > 0, gate False). Usage: case-d.py <selector.py>
"""
import importlib.util
import sys


def load(path):
    spec = importlib.util.spec_from_file_location("selector_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv):
    R = load(argv[1])
    correct = ("**Current authority (round 85):** Latest measured round: 85. Terminal gate "
               f"measured at `{R.A}`: {R.GOOD_CMD} printed {R.GOOD_TOKEN}, exit0; receipt "
               f"`{R.GOOD_RECEIPT}`.")
    inner = correct + "\n## Axes\n\n" + R.GOOD_ROW + "\n"
    cases = {
        "list-marker-closer": "```markdown\n- ```\n" + inner + "```\n",
        "blockquote-marked-closer": "```markdown\n> ```\n" + inner + "```\n",
        "four-space-indented-closer":
            "```markdown\n" + inner + "    ```\nTAIL-CELLS-RENDER\n```\n",
    }
    fails = 0
    for name, shadow in cases.items():
        try:
            result = R.grade(R.fixture(stale_live=True, shadow=shadow))
            line = R.render(result)
            state = "escape" if result["mismatches"] == 0 else "red"
            exit_code = 0 if result["mismatches"] == 0 else 1
            ok = result["mismatches"] > 0 and not result["facts"]["gate"]
        except R.CouldNotEvaluate as exc:
            line, state, exit_code, ok = f"could-not-evaluate: {exc}", "cne", 2, False
        fails += not ok
        print(f"CASE_D {name} {state} closer-not-a-closer={ok} exit={exit_code} {line}")
    print(f"CASE_D cases=3 pass={3 - fails} fail={fails}")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
