#!/usr/bin/env python3
"""MT01 guard probes: show that each surviving selector rule is load-bearing in
production (a shadow-only tree must fail closed) while no declared selftest arm
notices its removal. Also tests one extra fence mutant (tilde fences)."""
import hashlib
import importlib.util
import os
import subprocess
import sys

D = "/fast/scratch/hyaku/kama-r86/MT01SelectorMutants"
BASE = os.path.join(D, "base", "round86-rendered-cells.py")
A = "a" * 40


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def grade_or_exit(module, score_text, mutate_tree=None):
    tree = module.fixture(stale_live=False)
    tree.files["SCORECARD.md"] = score_text
    if mutate_tree:
        mutate_tree(tree)
    try:
        result = module.grade(tree)
    except module.CouldNotEvaluate as exc:
        return 2, f"could-not-evaluate: {exc}", None
    return (0 if result["mismatches"] == 0 else 1), module.render(result), result["facts"]


def live_authority(m):
    return (f"**Current authority (round 85):** assigned axes are operability + calibration; "
            f"Latest measured round: 85. Terminal gate measured at `{A}`: {m.GOOD_CMD} printed "
            f"{m.GOOD_TOKEN}, exit0; receipt `{m.GOOD_RECEIPT}`.")


SHADOWS = {
    "fenced": lambda m: "```markdown\n" + live_authority(m) + "\n```",
    "commented": lambda m: "<!--\n" + live_authority(m) + "\n-->",
    "tilde-fenced": lambda m: "~~~\n" + live_authority(m) + "\n~~~",
    "correction": lambda m: "# round-42 correction\n\n" + live_authority(m),
    "indented": lambda m: "    " + live_authority(m),
}


def authority_only(m, shadow_kind):
    return "# fixture\n\n" + SHADOWS[shadow_kind](m) + "\n\n## Axes\n\n" + m.GOOD_ROW + "\n"


def row_only_indented(m):
    return ("# fixture\n\n" + live_authority(m) + "\n\n## Axes\n\n    " + m.GOOD_ROW + "\n")


def main():
    base = load("base_instrument", BASE)
    print(f"BASE sha256={hashlib.sha256(open(BASE,'rb').read()).hexdigest()}")

    cases = []
    for kind in SHADOWS:
        cases.append((f"shadow-only-authority/{kind}", "a-fence-exclusion-off", kind))
    cases.append(("shadow-only-authority/commented", "b-comment-exclusion-off", "commented"))
    cases.append(("shadow-only-authority/correction", "c-correction-exclusion-off", "correction"))
    cases.append(("shadow-only-authority/indented", "d-column0-relaxed", "indented"))
    cases.append(("indented-row-only", "d2-calibration-column0-relaxed", None))
    cases.append(("shadow-only-authority/tilde-fenced", "f-tilde-fence-off", "tilde-fenced"))

    # extra mutant: tilde fences no longer recognised (single-site regex)
    text = open(BASE).read()
    old = 'FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")'
    new = 'FENCE = re.compile(r"^ {0,3}(`{3,})(.*)$")'
    assert text.count(old) == 1
    tilde_path = os.path.join(D, "mutants", "f-tilde-fence-off.py")
    open(tilde_path, "w").write(text.replace(old, new))
    print(f"mutant f sha256={hashlib.sha256(open(tilde_path,'rb').read()).hexdigest()}")

    modules = {}
    for name in ("a-fence-exclusion-off", "b-comment-exclusion-off",
                 "c-correction-exclusion-off", "d-column0-relaxed",
                 "d2-calibration-column0-relaxed", "f-tilde-fence-off"):
        modules[name] = load(name.replace("-", "_"), os.path.join(D, "mutants", name + ".py"))

    print("\n# pristine vs mutant on shadow-only trees (production shape: the only\n"
          "# candidate cell lives in a fence/comment/correction/indented block)")
    rows = []
    for label, mutant, kind in cases:
        if kind is None:
            score = lambda m: row_only_indented(m)
        else:
            score = lambda m, k=kind: authority_only(m, k)
        p_exit, p_line, _ = grade_or_exit(base, score(base))
        m_exit, m_line, _ = grade_or_exit(modules[mutant], score(modules[mutant]))
        rows.append((label, mutant, p_exit, m_exit, p_line, m_line))
        print(f"{label} mutant={mutant} pristine_exit={p_exit} mutant_exit={m_exit}")
        print(f"  pristine: {p_line}")
        print(f"  mutant  : {m_line}")
    false_green = [r for r in rows if r[2] == 2 and r[3] == 0]
    print(f"\nFALSE_GREEN_COUNT={len(false_green)} of {len(rows)} probes "
          f"(pristine fails closed exit 2, mutant grades green exit 0)")
    print(f"BASE_AFTER sha256={hashlib.sha256(open(BASE,'rb').read()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
