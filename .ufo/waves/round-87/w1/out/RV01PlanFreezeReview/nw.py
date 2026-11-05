"""no-work probe suite (item 2) at the frozen selector, plain fixture API unmodified."""
import importlib.util, sys
spec = importlib.util.spec_from_file_location("r", sys.argv[1])
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
A = R.A

# variant 1: closure-file verdict line reworded to the R2 shape; SCORECARD row names round-85 as-is
body = "# kama round 86\n\nverdict `rejected-honest-stop`\n\nVerdict: rejected-honest-stop. admitted false.\n"
tree = R.fixture(stale_live=False, extra_files={"corpus/lessons/round-86-verifier-spotcheck.md": body})
r = R.grade(tree); print("closure-file-only ->", R.render(r), "exit", 1 if r["mismatches"] else 0)

# variant 2: SCORECARD calibration row corrected, closure file untouched
row = ("| calibration | **7** | terminal `SELFRECORD_R85` at `" + A + "`; latest outside closure "
       "`corpus/lessons/round-86-verifier-spotcheck.md` (round86 rejected-honest-stop; "
       "round85 rejected-honest-stop) | score round1 |")
tree2 = R.fixture(stale_live=False, row=row)
r2 = R.grade(tree2); print("scorecard-row-only ->", R.render(r2), "exit", 1 if r2["mismatches"] else 0)

# variant 3: both edits (violates the fresh-start history clause)
tree3 = R.fixture(stale_live=False, row=row, extra_files={"corpus/lessons/round-86-verifier-spotcheck.md": body})
r3 = R.grade(tree3); print("both-edits ->", R.render(r3), "exit", 1 if r3["mismatches"] else 0)
