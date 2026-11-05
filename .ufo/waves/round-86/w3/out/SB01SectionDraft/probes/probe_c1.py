import importlib.util, sys, subprocess, json
COPY="/fast/scratch/hyaku/kama-r86/SB01SectionDraft/copy"
def load(name, rel):
    spec=importlib.util.spec_from_file_location(name, f"{COPY}/tools/{rel}")
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
R=load("r86rc","round86-rendered-cells.py")
A,B=R.A,R.B
correct=("**Current authority (round 85):** Latest measured round: 85. Terminal gate "
         f"measured at `{A}`: {R.GOOD_CMD} printed {R.GOOD_TOKEN}, exit0; receipt `{R.GOOD_RECEIPT}`.")
def run(name, tree):
    try:
        res=R.grade(tree); line=R.render(res); rc=0 if res["mismatches"]==0 else 1
        print(f"[{name}] exit={rc} {line}")
        for f in res["findings"]: print(f"   finding {f}")
        return res
    except R.CouldNotEvaluate as e:
        print(f"[{name}] exit=2 could-not-evaluate: {e}")
# control: live stale cells, no shadow -> must be red
run("control-stale-live-no-shadow", R.fixture(stale_live=True))
# P-A: a fence closed early by an indented-list fence line "- ```" (CommonMark 4.5: not a closer)
shadowA=("```markdown\n- ```\n"+correct+"\n## Axes\n\n"+R.GOOD_ROW+"\n```\n")
treeA=R.fixture(stale_live=True, shadow=shadowA)
run("P-A-list-marker-closes-fence", treeA)
open(f"{COPY}/../P-A.md","w").write(treeA.files["SCORECARD.md"])
# P-B: disposition oracle takes the first fixed-order word anywhere in the body
bodyB="# kama round 85\n\nVerdict: rejected-honest-stop. Earlier round 83 was rejected-harmed.\n"
rowB=("| calibration | **7** | terminal `SELFRECORD_R85` at `"+A+"`; latest outside closure "
      "`corpus/lessons/round-85-verifier-spotcheck.md` (round85 rejected-harmed; round84 rejected-honest-stop) | score round1 |")
run("P-B-wrong-disposition-word-in-row", R.fixture(stale_live=False, row=rowB, extra_files={"corpus/lessons/round-85-verifier-spotcheck.md": bodyB}))
# P-C: a cell naming two revisions; the coupling accepts ANY ancestor that carries the token
t=R.fixture(stale_live=False, authority_extra=f" Also measured at `{B}`.")
t.ancestors.add(B)
t.rev_files={A:{R.GOOD_RECEIPT: "PRE_REPORT round=85 arms=13 failed=1 uncommitted=0\n"}, B:{}}
run("P-C-extra-revision-without-receipt", t)
