#!/usr/bin/env bash
# Exit-contract probes for tools/report-landing-audit.py (kama lane, round 21, AuditExitContract).
# Usage: repro-exit-contract.sh LANE_REPO FLEET_REPO AUDIT_PY
# Read-only on LANE_REPO and FLEET_REPO. Fixtures live in a mktemp dir removed on exit.
set -u
LANE=${1:?usage: repro-exit-contract.sh LANE_REPO FLEET_REPO AUDIT_PY}
FLEET=${2:?usage: repro-exit-contract.sh LANE_REPO FLEET_REPO AUDIT_PY}
AUD=${3:?usage: repro-exit-contract.sh LANE_REPO FLEET_REPO AUDIT_PY}
PY=${PY:-/usr/bin/python3}
W=$(mktemp -d /tmp/aud-exit-repro.XXXXXX)
trap 'rm -rf "$W"' EXIT
echo "git=$(git --version) python=$("$PY" --version 2>&1)"

echo "== 0a baseline: default range + default errata (expect exit 0, status=clean)"
"$PY" "$AUD" --lane-repo "$LANE" --fleet-repo "$FLEET" 2>&1 | tail -n 1; echo "   exit=${PIPESTATUS[0]}"
echo "== 0b baseline: --no-errata (expect exit 1, uncorrected=9)"
"$PY" "$AUD" --lane-repo "$LANE" --fleet-repo "$FLEET" --no-errata 2>&1 | tail -n 1; echo "   exit=${PIPESTATUS[0]}"
echo "== 0c selftest, clean environment (expect exit 0, failed=0)"
"$PY" "$AUD" --selftest 2>&1 | tail -n 1; echo "   exit=${PIPESTATUS[0]}"

echo "== 1 git missing from PATH (expect exit 1 with traceback: escape from main)"
env PATH=/nonexistent "$PY" "$AUD" --lane-repo "$LANE" --fleet-repo "$FLEET" --no-errata 2>&1 | tail -n 2; echo "   exit=${PIPESTATUS[0]}"

echo "== 2 reversed range --rounds 20-10 --no-errata (expect exit 0, reports=0)"
"$PY" "$AUD" --lane-repo "$LANE" --fleet-repo "$FLEET" --rounds 20-10 --no-errata 2>&1 | tail -n 1; echo "   exit=${PIPESTATUS[0]}"

echo "== 3 single round --rounds 10 with default errata (expect exit 1; round 10 corrected, rows of rounds 18/20 unmatched)"
"$PY" "$AUD" --lane-repo "$LANE" --fleet-repo "$FLEET" --rounds 10 2>&1 | tail -n 1; echo "   exit=${PIPESTATUS[0]}"

echo "== 4 override without =PATH (expect exit 1; baseline --rounds 19 --no-errata is exit 0)"
"$PY" "$AUD" --lane-repo "$LANE" --fleet-repo "$FLEET" --rounds 19 --no-errata 2>&1 | tail -n 1; echo "   baseline_exit=${PIPESTATUS[0]}"
"$PY" "$AUD" --lane-repo "$LANE" --fleet-repo "$FLEET" --rounds 19 --report 19 --no-errata 2>&1 | tail -n 1; echo "   exit=${PIPESTATUS[0]}"

echo "== 5 committed report passed by path (expect exit 1; docstring cutoff applies only to uncommitted reports)"
"$PY" "$AUD" --lane-repo "$LANE" --fleet-repo "$FLEET" --rounds 19 --report "19=$FLEET/.ufo/reports/round-19/kama.md" --no-errata 2>&1 | tail -n 1; echo "   exit=${PIPESTATUS[0]}"
"$PY" "$AUD" --lane-repo "$LANE" --fleet-repo "$FLEET" --rounds 19 --report "19=$FLEET/.ufo/reports/round-19/kama.md" --no-errata --json 2>/dev/null | "$PY" -c 'import json,sys; r=json.load(sys.stdin)["results"][0]; print("   override json: report_committed=%s cutoff=%s required=%s" % (r["report_committed"], r["cutoff"], r["required"]))'
"$PY" "$AUD" --lane-repo "$LANE" --fleet-repo "$FLEET" --rounds 19 --no-errata --json 2>/dev/null | "$PY" -c 'import json,sys; r=json.load(sys.stdin)["results"][0]; print("   no-override json: report_committed=%s cutoff=%s required=%s" % (r["report_committed"], r["cutoff"], r["required"]))'

echo "== 6 stdout is /dev/full on a clean run (expect exit 1 traceback: clean verdict becomes failed)"
"$PY" "$AUD" --lane-repo "$LANE" --fleet-repo "$FLEET" --json > /dev/full 2>"$W/e6"; echo "   exit=$?"; tail -n 1 "$W/e6"

echo "== 7 reader closes pipe on a clean run (expect exit 1 BrokenPipeError)"
"$PY" "$AUD" --lane-repo "$LANE" --fleet-repo "$FLEET" --json 2>"$W/e7" | true; echo "   exit=${PIPESTATUS[0]}"; tail -n 1 "$W/e7"

echo "== 8 stdout closed on a clean run (expect exit 0 with no output)"
"$PY" "$AUD" --lane-repo "$LANE" --fleet-repo "$FLEET" --json >&- 2>"$W/e8"; echo "   exit=$?"; tail -n 1 "$W/e8"

echo "== 9 report path is a FIFO (expect exit 124 from timeout: never returns)"
mkfifo "$W/fifo"; timeout 5 "$PY" "$AUD" --lane-repo "$LANE" --fleet-repo "$FLEET" --rounds 1 --report "1=$W/fifo" --no-errata >/dev/null 2>&1; echo "   exit=$?"

echo "== 10 selftest under user gitconfig with gpgsign and missing gpg (expect traceback, exit 1)"
mkdir -p "$W/home"; printf '[commit]\n\tgpgsign = true\n[gpg]\n\tprogram = /nonexistent-gpg\n' > "$W/home/.gitconfig"
HOME="$W/home" "$PY" "$AUD" --selftest 2>&1 | tail -n 1; echo "   exit=${PIPESTATUS[0]}"

echo "== 11 ambiguous 7-hex abbreviation in Landed changes (git exit 128 recorded as absent: expect exit 1)"
AMB=$("$PY" - "$W" <<'PYEOF'
import collections, pathlib, subprocess, sys
W = pathlib.Path(sys.argv[1]); ROOT = W / "amb"; ROOT.mkdir()
subprocess.run(["git", "init", "-q", "-b", "master", str(ROOT)], check=True)
parts = []
for i in range(60000):
    msg = f"c{i}\n".encode()
    parts.append(f"commit refs/heads/master\nmark :{i+1}\ncommitter Amb <a@x> {1700000000+i} +0000\ndata {len(msg)}\n".encode())
    parts.append(msg)
    if i:
        parts.append(f"from :{i}\n".encode())
    parts.append(b"\n")
subprocess.run(["git", "-C", str(ROOT), "fast-import", "--quiet"], input=b"".join(parts), check=True, capture_output=True)
shas = subprocess.run(["git", "-C", str(ROOT), "rev-list", "master"], capture_output=True, text=True, check=True).stdout.split()
by = collections.defaultdict(list)
for s in shas:
    by[s[:7]].append(s)
amb = next(v[0][:7] for v in by.values() if len(v) > 1)
(W / "amb-draft.md").write_text(f"## Landed changes\n- `{amb}` x\n## End\n", encoding="utf-8")
print(amb)
PYEOF
)
echo "   ambiguous_prefix=$AMB"
"$PY" "$AUD" --lane-repo "$W/amb" --fleet-repo "$FLEET" --rounds 1 --report "1=$W/amb-draft.md" --no-errata 2>&1 | tail -n 2; echo "   exit=${PIPESTATUS[0]}"
git -C "$W/amb" cat-file -e "$AMB^{commit}" 2>&1 | tail -n 1; echo "   git cat-file -e $AMB^{commit} exit=${PIPESTATUS[0]}"

echo "== 12 unrelated commit subject with U+2028 (expect exit 0 control, then exit 2 for the same report)"
M="$W/meta"; mkdir "$M"; git -C "$M" init -q -b master
export GIT_AUTHOR_NAME=kama-shokunin GIT_COMMITTER_NAME=kama-shokunin GIT_AUTHOR_EMAIL=x@x GIT_COMMITTER_EMAIL=x@x
git -C "$M" -c commit.gpgsign=false commit -q --allow-empty -m 'round-1: work'
SHA9=$(git -C "$M" rev-parse --short=9 HEAD)
printf '## Landed changes\n- `%s` work\n## End\n' "$SHA9" > "$W/draft-meta.md"
"$PY" "$AUD" --lane-repo "$M" --fleet-repo "$FLEET" --rounds 1 --report "1=$W/draft-meta.md" --no-errata 2>&1 | tail -n 1; echo "   control_exit=${PIPESTATUS[0]}"
git -C "$M" -c commit.gpgsign=false commit -q --allow-empty -m "$(printf 'round-9: a\342\200\250b')"
"$PY" "$AUD" --lane-repo "$M" --fleet-repo "$FLEET" --rounds 1 --report "1=$W/draft-meta.md" --no-errata 2>&1 | tail -n 1; echo "   exit=${PIPESTATUS[0]}"
unset GIT_AUTHOR_NAME GIT_COMMITTER_NAME GIT_AUTHOR_EMAIL GIT_COMMITTER_EMAIL

echo "== 13 controls: documented exit-2 inputs (expect exit 2 each)"
printf 'x \377\n' > "$W/bad-utf8.md"
"$PY" "$AUD" --lane-repo "$LANE" --fleet-repo "$FLEET" --rounds 1 --report "1=$W/bad-utf8.md" --no-errata 2>&1 | tail -n 1; echo "   utf8_report_exit=${PIPESTATUS[0]}"
"$PY" "$AUD" --lane-repo "$LANE" --fleet-repo "$FLEET" --rounds 21 --no-errata 2>&1 | tail -n 1; echo "   missing_report_exit=${PIPESTATUS[0]}"
"$PY" "$AUD" --lane-repo "$LANE" --fleet-repo "$FLEET" --rounds 1-x --no-errata 2>&1 | tail -n 1; echo "   bad_rounds_exit=${PIPESTATUS[0]}"
"$PY" "$AUD" --lane-repo "$LANE" --fleet-repo "$FLEET" --branch nope --rounds 20 --no-errata 2>&1 | tail -n 1; echo "   bad_branch_exit=${PIPESTATUS[0]}"
"$PY" "$AUD" --lane-repo "$W" --fleet-repo "$FLEET" --rounds 20 --no-errata 2>&1 | tail -n 1; echo "   lane_not_repo_exit=${PIPESTATUS[0]}"

echo "== 14 ledger row whose correction is not a commit (expect exit 1: errata-invalid)"
awk -F'\t' -v OFS='\t' '$1==20 && $2=="unresolved-full-hash" {$4="0000000000000000000000000000000000000000"} {print}' "$LANE/registry/report-landing-errata.tsv" > "$W/ledger.tsv"
"$PY" "$AUD" --lane-repo "$LANE" --fleet-repo "$FLEET" --rounds 10-20 --errata "$W/ledger.tsv" 2>&1 | tail -n 2; echo "   exit=${PIPESTATUS[0]}"
echo "== 15 ledger row with unknown kind (expect exit 2: malformed ledger)"
printf '1\tnot-a-kind\tx\ty\tz\n' > "$W/bad-kind.tsv"
"$PY" "$AUD" --lane-repo "$LANE" --fleet-repo "$FLEET" --rounds 10-20 --errata "$W/bad-kind.tsv" 2>&1 | tail -n 1; echo "   exit=${PIPESTATUS[0]}"

echo "== 16 audit references in the lane tree (expect only the tool itself and its errata ledger)"
grep -rl 'report-landing-audit' "$LANE/tools" "$LANE/registry" "$LANE/tests" "$LANE/corpus" "$LANE/SKILL.md" 2>/dev/null; echo "   grep_exit=$?"

echo "== 17 git exit semantics on the ambiguous repo (absent vs ambiguous vs present)"
R="$W/amb"
git -C "$R" cat-file -e 0000000000000000000000000000000000000001 2>/dev/null; echo "   absent_fullhash_no_peel_exit=$?"
git -C "$R" cat-file -e 0000000000000000000000000000000000000001^{commit} 2>/dev/null; echo "   absent_fullhash_commit_peel_exit=$?"
git -C "$R" cat-file -e "$AMB^{commit}" 2>/dev/null; echo "   ambiguous_commit_peel_exit=$?"
git -C "$R" rev-parse -q --verify "$AMB^{commit}" >/dev/null 2>&1; echo "   ambiguous_revparse_quiet_exit=$?"
printf '%s\n0000000000000000000000000000000000000001\n' "$AMB" | git -C "$R" cat-file --batch-check='%(objectname) %(objecttype)' 2>/dev/null; echo "   batch_check_exit=${PIPESTATUS[1]}"
echo "done"
