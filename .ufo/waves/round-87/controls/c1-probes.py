#!/usr/bin/env python3
"""Frozen round-87 C1 probe battery (kama r87). Usage: c1-probes.py <selector.py>

Loads a rendered-cell selector by path (the round-86 instrument or a successor that keeps
its fixture API: fixture, grade, GOOD_*, A, B) and runs one control plus three
false-green probes. A probe is an ESCAPE when the selector grades it with zero
mismatches. The control is a stale live cell with no shadow text and must be red.

Probes (frozen; reproduced at master 362b0d4a against round86-rendered-cells.py):
  P-A  a fence closed early by an indented-list line "- ```" (CommonMark 0.31.2 4.5: a
       closer may only be indented by 0-3 spaces and carry nothing but spaces after it)
  P-B  the disposition oracle takes a fixed-order word from anywhere in the closure body
  P-C  a gate cell naming a second revision that carries the same receipt token

Output: one `C1_PROBE <name> <red|escape|cne>` line per case and one final line
`C1_PROBES probes=3 escapes=<n> control=<red|green>`. Exit 0 only when control is red and
escapes == 0; exit 1 otherwise. `cne` (could-not-evaluate) is never counted as red.
"""
import importlib.util
import sys


def load(path):
    spec = importlib.util.spec_from_file_location("selector_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verdict(R, tree):
    try:
        result = R.grade(tree)
    except R.CouldNotEvaluate:
        return "cne"
    return "escape" if result["mismatches"] == 0 else "red"


def build(R):
    A, B = R.A, R.B
    correct = ("**Current authority (round 85):** Latest measured round: 85. Terminal gate "
               f"measured at `{A}`: {R.GOOD_CMD} printed {R.GOOD_TOKEN}, exit0; receipt "
               f"`{R.GOOD_RECEIPT}`.")
    shadow_a = "```markdown\n- ```\n" + correct + "\n## Axes\n\n" + R.GOOD_ROW + "\n```\n"
    tree_a = R.fixture(stale_live=True, shadow=shadow_a)
    body_b = "# kama round 85\n\nVerdict: rejected-honest-stop. Earlier round 83 was rejected-harmed.\n"
    row_b = ("| calibration | **7** | terminal `SELFRECORD_R85` at `" + A + "`; latest outside "
             "closure `corpus/lessons/round-85-verifier-spotcheck.md` (round85 rejected-harmed; "
             "round84 rejected-honest-stop) | score round1 |")
    tree_b = R.fixture(stale_live=False, row=row_b,
                       extra_files={"corpus/lessons/round-85-verifier-spotcheck.md": body_b})
    tree_c = R.fixture(stale_live=False, authority_extra=f" Also measured at `{B}`.")
    tree_c.ancestors.add(B)
    tree_c.rev_files = {A: {R.GOOD_RECEIPT: "PRE_REPORT round=85 arms=13 failed=1 uncommitted=0\n"},
                        B: {}}
    return tree_a, tree_b, tree_c


def main(argv):
    if len(argv) != 2:
        print("usage: c1-probes.py <selector.py>", file=sys.stderr)
        return 2
    R = load(argv[1])
    control = verdict(R, R.fixture(stale_live=True))
    print(f"C1_PROBE control-stale-live-no-shadow {control}")
    escapes = 0
    for name, tree in zip(("P-A-list-marker-closes-fence", "P-B-wrong-disposition-word-in-row",
                           "P-C-extra-revision-without-receipt"), build(R)):
        state = verdict(R, tree)
        escapes += state == "escape"
        print(f"C1_PROBE {name} {state}")
    ctrl = "red" if control == "red" else "green"
    print(f"C1_PROBES probes=3 escapes={escapes} control={ctrl}")
    return 0 if ctrl == "red" and escapes == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
