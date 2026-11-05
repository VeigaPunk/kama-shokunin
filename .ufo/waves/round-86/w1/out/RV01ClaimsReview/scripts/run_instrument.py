#!/usr/bin/env python3
"""Run the FROZEN instrument (scratch copy, sha256 e038b2c0...) in-process at a revision,
optionally overriding SCORECARD.md with a fixture file. Repo is read-only (git show only)."""
import importlib.util
import sys

INSTR = "/fast/scratch/hyaku/kama-r86/RV01ClaimsReview/rc-freeze.py"
spec = importlib.util.spec_from_file_location("rc", INSTR)
rc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc)


class Over(rc.GitTree):
    def __init__(self, repo, rev, over):
        super().__init__(repo, rev)
        self.over = over

    def blob(self, path):
        if path in self.over:
            return self.over[path]
        return super().blob(path)


def main():
    repo, rev = sys.argv[1], sys.argv[2]
    over = {}
    if len(sys.argv) > 3:
        over["SCORECARD.md"] = open(sys.argv[3], encoding="utf-8").read()
    tree = Over(repo, rev, over)
    try:
        res = rc.grade(tree)
        print(rc.render(res) + f" rev={rev[:10]} fixture={sys.argv[3] if len(sys.argv) > 3 else '-'}")
        for fact, detail in res["findings"]:
            print(f"RENDERED_CELLS_FINDING {fact} {detail}")
        return 0 if res["mismatches"] == 0 else 1
    except rc.CouldNotEvaluate as exc:
        print(f"could-not-evaluate: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
