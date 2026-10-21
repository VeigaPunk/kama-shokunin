#!/usr/bin/env python3
"""Mutation-test the 32 --selftest cases of tools/report-landing-audit.py
at lane commit a6617149722c73d90e142fbdc8154d6967055f7e.

For each mutation (a surgical break of the code a case name claims to test)
we run the mutated tool's --selftest in a scratch copy and record which
baseline-ok cases stop passing. A named case is mutation-confirmed when some
mutation of ITS claimed code flips it. Survivors are vacuity evidence.

Read-only w.r.t. the lane: source is read from the scratch clone; mutant
copies live under /tmp/kama-r21-C1SelftestReview/mut.
"""
import concurrent.futures
import json
import subprocess
import sys
import time
from pathlib import Path

SRC = Path("/tmp/kama-r21-C1SelftestReview/lane/tools/report-landing-audit.py")
MUTDIR = Path("/tmp/kama-r21-C1SelftestReview/mut")

# name -> list of (old, new) exact-substring replacements (all must match once)
MUTS = {
    # exit-status computation (raw-fails)
    "M01-exit-always-zero": [(
        'status = 0 if (summary["uncorrected"] == 0 and not unmatched',
        'status = 0 if (True or summary["uncorrected"] == 0 and not unmatched')],
    # unresolved-full-hash detection (mashup-detected)
    "M02-fullhash-never": [(
        'for t, s in full.items() if s != "found"]',
        'for t, s in full.items() if s == "gone"]')],
    # checkpoint(rN) subject form (checkpoint-without-colon-omission-detected)
    "M03-checkpoint-pattern-dropped": [(
        'pat = re.compile(rf"^(?:round-{rnd}:|checkpoint\\(r{rnd}\\))")',
        'pat = re.compile(rf"^(?:round-{rnd}:)")')],
    # landed-unresolved reporting (bad-abbrev-detected)
    "M04-landed-missing-never": [(
        'if state == "missing":',
        'if state == "gone":')],
    # citation filter in omission/status lookup (exact-defect-set FP control)
    "M05-checkable-filter-dropped": [(
        'status = lookup(repos, [t for t in cited if checkable_abbrev(t)],',
        'status = lookup(repos, [t for t in cited],')],
    # subject need not have a space after the colon (subject-without-space-required)
    "M06-require-space-after-colon": [(
        'pat = re.compile(rf"^(?:round-{rnd}:|checkpoint\\(r{rnd}\\))")',
        'pat = re.compile(rf"^(?:round-{rnd}:\\s|checkpoint\\(r{rnd}\\))")')],
    # exact author match (author-exact-other-round-and-prefix-ignored)
    "M07-author-startswith": [(
        'if author == f"{lane}-shokunin" and pat.match(subject):',
        'if author.startswith(f"{lane}-shokunin") and pat.match(subject):')],
    # prefix subject xround-1: ignored via left-anchored match (same case)
    "M08-match-to-search": [(
        'if author == f"{lane}-shokunin" and pat.match(subject):',
        'if author == f"{lane}-shokunin" and pat.search(subject):')],
    # redundant-^ no-op probe (same case)
    "M09-caret-dropped-noop-probe": [(
        'pat = re.compile(rf"^(?:round-{rnd}:|checkpoint\\(r{rnd}\\))")',
        'pat = re.compile(rf"(?:round-{rnd}:|checkpoint\\(r{rnd}\\))")')],
    # round-10 colon boundary (same case)
    "M10-round-colon-dropped": [(
        'pat = re.compile(rf"^(?:round-{rnd}:|checkpoint\\(r{rnd}\\))")',
        'pat = re.compile(rf"^(?:round-{rnd}|checkpoint\\(r{rnd}\\))")')],
    # author time vs committer time (author-time-cutoff-survives-rebase,
    # post-report-excluded)
    "M11-atime-to-ctime": [(
        'out = git(lane_repo, "log", f"--format=%H{SEP}%an{SEP}%at{SEP}%s{END}",',
        'out = git(lane_repo, "log", f"--format=%H{SEP}%an{SEP}%ct{SEP}%s{END}",')],
    # post_report computation (post-report-excluded)
    "M12-post-always-empty": [(
        'post = [c for c in commits if c["atime"] > cutoff]',
        'post = []')],
    # token length bounds (token-bounds)
    "M13-full-39": [(
        'FULL = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{40}(?![0-9A-Za-z])")',
        'FULL = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{39,40}(?![0-9A-Za-z])")')],
    "M14-abbrev-min-6": [(
        'ABBREV = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{7,40}(?![0-9A-Za-z])")',
        'ABBREV = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{6,40}(?![0-9A-Za-z])")')],
    "M15-abbrev-trailing-boundary-dropped": [(
        'ABBREV = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{7,40}(?![0-9A-Za-z])")',
        'ABBREV = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{7,40}")')],
    # leading boundary never exercised anywhere? (vacuity probe -> token-bounds)
    "M16-abbrev-leading-boundary-dropped": [(
        'ABBREV = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{7,40}(?![0-9A-Za-z])")',
        'ABBREV = re.compile(r"[0-9a-f]{7,40}(?![0-9A-Za-z])")')],
    # heading anchor (heading-anchor)
    "M17-heading-anchor-dropped": [(
        'match = re.search(r"^## Landed changes[^\\n]*\\n(.*?)(?=^## |\\Z)", text,',
        'match = re.search(r"## Landed changes[^\\n]*\\n(.*?)(?=^## |\\Z)", text,')],
    # digit+letter rule (hex-words-not-citations)
    "M18-checkable-and-to-or": [(
        'and re.search(r"[a-f]", token) is not None)',
        'or re.search(r"[a-f]", token) is not None)')],
    # errata defect matching (errata-clean)
    "M19-token-match-negated": [(
        'and e["token"] == defect["token"]]',
        'and e["token"] != defect["token"]]')],
    # round/kind/token equality (round-must-equal, kind-must-equal, token-must-equal)
    "M20-round-clause-dropped": [(
        'match = [e for e in errata if e["round"] == res["round"]',
        'match = [e for e in errata if True')],
    "M21-kind-clause-dropped": [(
        'and e["kind"] == defect["kind"]',
        'and True'),
        ('and e["token"] == defect["token"]]',
         'and True]')],
    "M22-token-clause-dropped": [(
        'and e["token"] == defect["token"]]',
        'and True]')],
    # unmatched computation (unmatched-errata-fails)
    "M23-unmatched-summary-zeroed": [(
        '"errata_unmatched": len(unmatched),',
        '"errata_unmatched": 0,')],
    # unselected-round filter (unselected-round-row-ignored)
    "M24-selected-filter-dropped": [(
        'if e["round"] in selected and e["line"] not in used]',
        'if e["line"] not in used]')],
    # correction resolvability (invalid-correction-fails)
    "M25-correction-status-never-invalid": [(
        'status.get(e["correction"]) != "found"',
        'status.get(e["correction"]) == "gone"')],
    # ^{commit} peel (blob-is-not-a-correction)
    "M26-peel-dropped": [(
        'if e["kind"] in RESOLVABLE], "^{commit}")',
        'if e["kind"] in RESOLVABLE], "")')],
    # landed-omitted correction equality (omitted-correction-must-be-the-commit)
    "M27-omitted-equality-dropped": [(
        'or (e["kind"] == "landed-omitted" and e["correction"] != e["token"]))]',
        'or False)]')],
    # errata row validation (malformed-errata-is-error)
    "M28-kind-validation-dropped": [(
        'if len(parts) != 5 or not parts[0].isdigit() or parts[1] not in KINDS:',
        'if len(parts) != 5 or not parts[0].isdigit():')],
    "M29-shape-validation-dropped-probe": [(
        'if len(parts) != 5 or not parts[0].isdigit() or parts[1] not in KINDS:',
        'if parts[1] not in KINDS:')],
    # draft cutoff source (draft-uses-fleet-cutoff)
    "M30-draft-ignores-fleet-cutoff": [(
        'cutoff = report_cutoff(fleet_repo, rel)',
        'cutoff = None if path is not None else report_cutoff(fleet_repo, rel)')],
    # section-missing defect (missing-section-fails)
    "M31-section-missing-defect-dropped": [(
        'defects.append({"kind": "landed-section-missing", "token": "-"})',
        'pass')],
    # uncommitted-draft "now" fallback (uncommitted-draft-uses-now)
    "M32-now-fallback-epoch0-vacuity-probe": [(
        'cutoff = int(time.time())',
        'cutoff = 0')],
    "M33-now-fallback-removed": [(
        'cutoff = int(time.time())',
        'pass')],
    # no-fleet-commit guard (missing-report-is-error)
    "M34-no-fleet-commit-guard-dropped-probe": [(
        'raise EvalError(f"round {rnd}: {rel} has no fleet commit")',
        'cutoff = 0')],
    # report readability (missing-report-is-error, irregular-report-is-error,
    # empty-report-path-is-error)
    "M35-read-failure-swallowed": [(
        'raise EvalError(f"cannot read {path}: {exc}") from exc',
        'return ""')],
    # reversed-range guard (reversed-range-is-error)
    "M36-reversed-guard-dropped-probe": [(
        'if hi < lo:',
        'if False:')],
    # empty-selection guard (same case; the real teeth)
    "M37-empty-selection-guard-dropped": [(
        'raise EvalError("no rounds selected")',
        'rounds = []')],
    "M38-reversed-plus-empty-guards-dropped": [
        ('if hi < lo:', 'if False:'),
        ('raise EvalError("no rounds selected")', 'rounds = []')],
    # --report value guard (empty-report-path-is-error)
    "M39-empty-value-guard-dropped-probe": [(
        'if not sep or not key.isdigit() or not value:',
        'if not sep or not key.isdigit():')],
    # regular-file check (irregular-report-is-error)
    "M40-isreg-check-dropped-probe": [(
        'if not stat.S_ISREG(os.stat(path).st_mode):',
        'if False:')],
    # git failure -> EvalError (unusable-git-is-error)
    "M41-git-raise-dropped": [(
        'if proc.returncode != 0:',
        'if False:')],
    # open range (open-range-finds-reports)
    "M42-open-range-exclusive": [(
        'rounds.update(n for n in present if n >= lo)',
        'rounds.update(n for n in present if n > lo)')],
    # git_env GIT_* stripping (inherited-GIT_DIR-untouched)
    "M43-git-env-keeps-GIT_DIR": [(
        'env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}',
        'env = {k: v for k, v in os.environ.items() if not '
        '(k.startswith("GIT_") and k != "GIT_DIR")}')],
    # combos: cases whose guards are singly redundant
    # irregular-report-is-error: S_ISREG + OSError->EvalError pair
    "M44-both-read-guards-dropped": [
        ('if not stat.S_ISREG(os.stat(path).st_mode):', 'if False:'),
        ('raise EvalError(f"cannot read {path}: {exc}") from exc', 'return ""')],
    # unusable-git-is-error: git-raise + lookup strict-parse pair
    "M45-git-raise-and-lookup-leniency": [
        ('if proc.returncode != 0:', 'if False:'),
        ('raise EvalError(f"cat-file in {repo}: unexpected {line!r}")',
         'continue')],
    # author-exact prefix aspect: unanchored pattern AND search()
    "M46-unanchored-search": [
        ('pat = re.compile(rf"^(?:round-{rnd}:|checkpoint\\(r{rnd}\\))")',
         'pat = re.compile(rf"(?:round-{rnd}:|checkpoint\\(r{rnd}\\))")'),
        ('if author == f"{lane}-shokunin" and pat.match(subject):',
         'if author == f"{lane}-shokunin" and pat.search(subject):')],
    # missing-report-is-error: no-fleet-commit guard + read-error pair
    "M47-no-fleet-guard-and-read-swallow": [
        ('raise EvalError(f"round {rnd}: {rel} has no fleet commit")',
         'cutoff = 0'),
        ('raise EvalError(f"cannot read {path}: {exc}") from exc', 'return ""')],
    # FULL lookbehind probe (leading boundary, full-hash regex)
    "M48-full-leading-boundary-dropped": [(
        'FULL = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{40}(?![0-9A-Za-z])")',
        'FULL = re.compile(r"[0-9a-f]{40}(?![0-9A-Za-z])")')],
    # unusable-git triple: git-raise + short-output + strict-parse all dropped
    "M49-git-failure-fully-silent": [
        ('if proc.returncode != 0:', 'if False:'),
        ('raise EvalError(f"cat-file --batch-check in {repo}: short output")',
         'pass'),
        ('raise EvalError(f"cat-file in {repo}: unexpected {line!r}")',
         'continue')],
}

CASES = ["raw-fails", "mashup-detected",
         "checkpoint-without-colon-omission-detected", "bad-abbrev-detected",
         "exact-defect-set", "subject-without-space-required",
         "author-exact-other-round-and-prefix-ignored",
         "author-time-cutoff-survives-rebase", "post-report-excluded",
         "token-bounds", "heading-anchor", "hex-words-not-citations",
         "errata-clean", "unmatched-errata-fails",
         "unselected-round-row-ignored", "round-must-equal",
         "kind-must-equal", "token-must-equal", "invalid-correction-fails",
         "blob-is-not-a-correction", "omitted-correction-must-be-the-commit",
         "malformed-errata-is-error", "draft-uses-fleet-cutoff",
         "missing-section-fails", "uncommitted-draft-uses-now",
         "missing-report-is-error", "reversed-range-is-error",
         "empty-report-path-is-error", "irregular-report-is-error",
         "unusable-git-is-error", "open-range-finds-reports",
         "inherited-GIT_DIR-untouched"]


def run_tool(py: Path):
    r = subprocess.run([sys.executable, str(py), "--selftest"],
                       capture_output=True, text=True, timeout=300)
    oks, fails = [], []
    summary = None
    for line in r.stdout.splitlines():
        if line.startswith("ok "):
            oks.append(line[3:])
        elif line.startswith("FAIL "):
            fails.append(line[5:])
        elif line.startswith("selftest cases="):
            summary = line
    err_tail = r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ""
    return {"rc": r.returncode, "ok": oks, "fail": fails, "summary": summary,
            "crashed": summary is None, "stderr_tail": err_tail}


def run_mutation(item):
    name, pairs = item
    src = SRC.read_text()
    for old, _ in pairs:
        n = src.count(old)
        if n != 1:
            return name, {"error": f"anchor count {n} != 1"}
    for old, new in pairs:
        src = src.replace(old, new, 1)
    p = MUTDIR / f"{name}.py"
    p.write_text(src)
    try:
        res = run_tool(p)
    except subprocess.TimeoutExpired:
        res = {"rc": None, "timeout": True, "crashed": True, "ok": [],
               "fail": [], "summary": None, "stderr_tail": "timeout"}
    killed = sorted(set(base["ok"]) - set(res["ok"]))
    unevaluated = sorted(set(CASES) - set(res["ok"]) - set(res["fail"]))
    res["killed"] = killed
    res["unevaluated"] = unevaluated
    return name, res


MUTDIR.mkdir(parents=True, exist_ok=True)
t0 = time.time()
base = run_tool(SRC)
print("BASELINE:", json.dumps(
    {"rc": base["rc"], "cases": len(base["ok"]), "failed": len(base["fail"]),
     "summary": base["summary"], "crashed": base["crashed"]}))
assert sorted(base["ok"]) == sorted(CASES), "baseline case set mismatch"

results = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    for name, res in ex.map(run_mutation, MUTS.items()):
        results[name] = res
        tag = "ERROR" if "error" in res else (
            "CRASH" if res.get("crashed") else
            ("KILLED:" + ",".join(res["killed"]) if res["killed"] else "SURVIVED"))
        print(f"{name:48s} {tag}")

print(f"elapsed={time.time()-t0:.1f}s")
out = {"baseline": base, "mutations": results,
       "case_order": CASES,
       "source": str(SRC),
       "commit": "a6617149722c73d90e142fbdc8154d6967055f7e"}
dest = Path(__file__).resolve().parent / "mutation-results.json"
dest.write_text(json.dumps(out, indent=1))
print("wrote", dest)
