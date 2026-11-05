#!/usr/bin/env python3
"""MT01SelectorBattery (kama round 87, C1 calibration): mutation battery for the rendered-cell selector.

Usage: battery.py <selector.py>

Loads the selector by path through the round-86 fixture API (fixture, grade, A, B, GOOD_CMD,
GOOD_TOKEN, GOOD_RECEIPT, GOOD_ROW, CouldNotEvaluate) and the DictTree attributes that
controls/c1-probes.py already uses (ancestors, rev_files). Every case is an in-memory fixture tree:
nothing is written to disk and no git command runs, so no TMPDIR or scratch argument is needed.

Each mutant is a stale-live fixture plus one shadow or document construct. "Stale-live" means the
live cell the mutant tries to hide (or the calibration row / closure it tries to fool) is wrong, so a
correct selector must answer RED (at least one mismatch). Verdicts per mutant:
  red     mismatches >= 1                         -> killed
  escape  exit clean, zero mismatches             -> escaped
  cne     could-not-evaluate, or a crash          -> not red, counted as escaped (not killed)

Controls (not counted in mutants=):
  C0  fenced-shadow: correct tokens inside a ```markdown fence, live cell stale. Must be red.
  CG  clean tree: live cells correct, no shadow. Must be escape. If it is red, every kill is suspect.

Output: SELECTOR_CONTROL, SELECTOR_MUTANT, SELECTOR_DETAIL, SELECTOR_VARIANT (informational), then
SELECTOR_MUTANTS mutants=9 killed=<k> escaped=<e>. Exit 0 always; the numbers are the result.
"""

import importlib.util
import sys

MUTANT_IDS = ("M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9")
PRIOR_RECEIPT = "PRE_REPORT round=85 arms=13 failed=1 uncommitted=0\n"


def load(path):
    spec = importlib.util.spec_from_file_location("selector_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verdict(R, tree):
    try:
        result = R.grade(tree)
    except R.CouldNotEvaluate as exc:
        return "cne", f"could-not-evaluate: {exc}"
    except Exception as exc:  # a crash is not a mismatch; never counted as red
        return "cne", f"crash: {type(exc).__name__}: {exc}"
    if result["mismatches"] == 0:
        return "escape", "mismatches=0"
    findings = result.get("findings") or []
    text = "; ".join(f"{item[0]}: {item[1]}" if isinstance(item, tuple) else str(item)
                     for item in findings)
    return "red", f"mismatches={result['mismatches']} {text}"


def cases(R):
    """Return {id: builder}; each builder returns a fixture tree (built lazily so one failure is isolated)."""
    A, B = R.A, R.B
    correct = ("**Current authority (round 85):** Latest measured round: 85. Terminal gate "
               f"measured at `{A}`: {R.GOOD_CMD} printed {R.GOOD_TOKEN}, exit0; receipt "
               f"`{R.GOOD_RECEIPT}`.")
    closure_path = "corpus/lessons/round-85-verifier-spotcheck.md"
    # Calibration row that names the WRONG disposition word (rejected-harmed) for round 85.
    harmed_row = ("| calibration | **7** | terminal `SELFRECORD_R85` at `" + A + "`; latest outside "
                  "closure `corpus/lessons/round-85-verifier-spotcheck.md` (round85 rejected-harmed; "
                  "round84 rejected-honest-stop) | score round1 |")

    def list_closer(closer):
        # Same shape as controls/c1-probes.py P-A: an outer ```markdown fence holds the correct
        # tokens and a `## Axes` row; the stale live cell follows the fence.
        shadow = ("```markdown\n" + closer + "\n" + correct + "\n## Axes\n\n" + R.GOOD_ROW
                  + "\n```\n")
        return R.fixture(stale_live=True, shadow=shadow)

    def extra_revision(literal):
        # M7 (frozen probe code, c1-probes.py P-C): the cell names a second revision B that does NOT
        # carry the receipt. M7L (informational, not counted): B carries the same receipt token.
        second = {R.GOOD_RECEIPT: PRIOR_RECEIPT} if literal else {}
        tree = R.fixture(stale_live=False, authority_extra=f" Also measured at `{B}`.",
                         rev_files={A: {R.GOOD_RECEIPT: PRIOR_RECEIPT}, B: second})
        tree.ancestors.add(B)
        return tree

    def closure_body(text):
        return R.fixture(stale_live=False, row=harmed_row,
                         extra_files={closure_path: "# kama round 85\n\n" + text + "\n"})

    mutants = {
        # M1 = P-A exactly: list-marker closer inside an outer ```markdown fence.
        "M1": lambda: list_closer("- ```"),
        # M2 blockquote-marked closer inside an outer fence.
        "M2": lambda: list_closer("> ```"),
        # M3 four-space-indented closer: CommonMark 4.5 says this is content, not a closer.
        "M3": lambda: list_closer("    ```"),
        # M4 closer followed by text: "```x" is never a closer.
        "M4": lambda: list_closer("```x"),
        # M5 P-B shape: disposition word rejected-harmed appears before the verdict line.
        "M5": lambda: closure_body("Earlier round 83 was rejected-harmed.\n\nverdict "
                                   "`rejected-honest-stop`"),
        # M6 two verdict lines, the wrong one first.
        "M6": lambda: closure_body("verdict `rejected-harmed`\n\nverdict `rejected-honest-stop`"),
        # M7 P-C: second revision named in the gate cell, without the receipt.
        "M7": lambda: extra_revision(literal=False),
        # M8 closer followed by a tab: the outer fence's own closer is "```<TAB>", which is valid.
        "M8": lambda: R.fixture(stale_live=True, shadow="```markdown\n" + correct + "\n## Axes\n\n"
                                + R.GOOD_ROW + "\n```\t"),
        # M9 list-item fence opener "- ```markdown" that never closes, followed by correct tokens.
        "M9": lambda: R.fixture(stale_live=True, shadow="- ```markdown\n" + correct + "\n## Axes\n\n"
                                + R.GOOD_ROW + "\n"),
    }
    controls = {
        "C0": lambda: R.fixture(stale_live=True, shadow="```markdown\n" + correct + "\n"
                                + R.GOOD_ROW + "\n```\n"),
        "CG": lambda: R.fixture(stale_live=False),
    }
    variants = {
        "M7L": lambda: extra_revision(literal=True),
    }
    return mutants, controls, variants


def run_case(R, builder):
    try:
        tree = builder()
    except Exception as exc:  # fixture construction failure: could not evaluate
        return "cne", f"fixture-build: {type(exc).__name__}: {exc}"
    return verdict(R, tree)


def main(argv):
    if len(argv) != 2:
        print("usage: battery.py <selector.py>", file=sys.stderr)
        return 0
    try:
        R = load(argv[1])
    except Exception as exc:
        print(f"SELECTOR_LOAD_ERROR {type(exc).__name__}: {exc}")
        print(f"SELECTOR_MUTANTS mutants={len(MUTANT_IDS)} killed=0 escaped={len(MUTANT_IDS)}")
        return 0

    mutants, controls, variants = cases(R)

    for cid, expect in (("C0", "red"), ("CG", "escape")):
        state, detail = run_case(R, controls[cid])
        result = "pass" if state == expect else "fail"
        status = "killed" if state == "red" else "escaped"
        print(f"SELECTOR_CONTROL {cid} expect={expect} got={state} {result} ({status})")
        print(f"SELECTOR_DETAIL {cid} {detail}")

    killed = 0
    for mid in MUTANT_IDS:
        state, detail = run_case(R, mutants[mid])
        status = "killed" if state == "red" else "escaped"
        killed += state == "red"
        print(f"SELECTOR_MUTANT {mid} expect=red got={state} {status}")
        print(f"SELECTOR_DETAIL {mid} {detail}")

    for vid, builder in variants.items():
        state, detail = run_case(R, builder)
        print(f"SELECTOR_VARIANT {vid} informational got={state} (not counted)")
        print(f"SELECTOR_DETAIL {vid} {detail}")

    escaped = len(MUTANT_IDS) - killed
    print(f"SELECTOR_MUTANTS mutants={len(MUTANT_IDS)} killed={killed} escaped={escaped}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
