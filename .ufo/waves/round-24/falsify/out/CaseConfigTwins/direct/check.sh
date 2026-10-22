#!/bin/bash
# Independent (non-grid) bounded check for the ConfigTwins family.
# Rebuilds a PG01-equivalent fixture with the candidate's own builder, runs the
# candidate auditor with a git shim that logs every git invocation, and proves:
#   * every git call carries --no-lazy-fetch isolation
#   * no transport/fetch-family git command is ever issued
#   * the promisor-marked repository is really audited (required/round_commits)
#   * the object inventory is unchanged after the audit
set -u
ROOT=/fast/scratch/hyaku/kama-r24/falsify/CaseConfigTwins/mycheck
CLONE=/fast/scratch/hyaku/kama-r24/falsify/CaseConfigTwins
LOG=$ROOT/git-calls.log
rm -rf "$ROOT/case1" "$ROOT/shim" "$LOG"
mkdir -p "$ROOT/shim" "$ROOT/case1"

# 1. build the fixture with the candidate's own builder (offline, local only)
python3 - "$ROOT" <<'PY'
import importlib.util, sys, json
root = sys.argv[1]
spec = importlib.util.spec_from_file_location(
    "grid", "/fast/scratch/hyaku/kama-r24/falsify/CaseConfigTwins/tests/report-audit/promisor-grid.py")
grid = importlib.util.module_from_spec(spec); spec.loader.exec_module(grid)
built = grid.BUILDERS["c_complete_lane_config"](root, root + "/case1")
print("PREMISE", json.dumps(built["premise"], sort_keys=True))
print("LANE", built["lane"]); print("FLEET", built["fleet"])
print("SHAS", json.dumps(built["shas"], sort_keys=True))
PY
BUILD_RC=$?
echo "build_rc=$BUILD_RC"
[ "$BUILD_RC" -eq 0 ] || exit 3

# 2. git shim that records argv
REALGIT=$(command -v git)
printf '#!/bin/sh\nprintf "%%s\\n" "$*" >> %s\nexec %s "$@"\n' "$LOG" "$REALGIT" > "$ROOT/shim/git"
chmod +x "$ROOT/shim/git"

# 3. object inventory before
git --no-lazy-fetch -C "$ROOT/case1/lane" cat-file --batch-all-objects --batch-check='%(objectname)' | sort > "$ROOT/lane-objs.before"
git --no-lazy-fetch -C "$ROOT/case1/fleet" cat-file --batch-all-objects --batch-check='%(objectname)' | sort > "$ROOT/fleet-objs.before"

# 4. run the candidate auditor with the shim first on PATH
cd "$ROOT/case1"
PATH="$ROOT/shim:$PATH" python3 "$CLONE/tools/report-landing-audit.py" \
  --lane-repo "$ROOT/case1/lane" --fleet-repo "$ROOT/case1/fleet" \
  --rounds 1 --no-errata --json > "$ROOT/audit.stdout" 2> "$ROOT/audit.stderr"
echo "audit_rc=$?"

# 5. object inventory after
git --no-lazy-fetch -C "$ROOT/case1/lane" cat-file --batch-all-objects --batch-check='%(objectname)' | sort > "$ROOT/lane-objs.after"
git --no-lazy-fetch -C "$ROOT/case1/fleet" cat-file --batch-all-objects --batch-check='%(objectname)' | sort > "$ROOT/fleet-objs.after"

echo "--- stdout"; cat "$ROOT/audit.stdout"
echo "--- stderr"; cat "$ROOT/audit.stderr"
echo "--- git calls: $(wc -l < "$LOG")"
echo "--- calls WITHOUT --no-lazy-fetch: $(grep -vc -- '--no-lazy-fetch' "$LOG")"
grep -v -- '--no-lazy-fetch' "$LOG" | head -20
echo "--- transport-family calls (fetch/ls-remote/clone/push): $(grep -Ec '(^| )(fetch|fetch-pack|ls-remote|clone|push|remote-ext|remote-https)($| )' "$LOG")"
grep -E '(^| )(fetch|fetch-pack|ls-remote|clone|push)($| )' "$LOG" | head -20
echo "--- calls mentioning the marked lane path: $(grep -c "$ROOT/case1/lane" "$LOG")"
echo "--- calls mentioning the fleet path: $(grep -c "$ROOT/case1/fleet" "$LOG")"
echo "--- lane objects delta: $(diff "$ROOT/lane-objs.before" "$ROOT/lane-objs.after" | wc -l) lines"
echo "--- fleet objects delta: $(diff "$ROOT/fleet-objs.before" "$ROOT/fleet-objs.after" | wc -l) lines"
echo "--- FETCH_HEAD: $(ls "$ROOT/case1/lane/.git/FETCH_HEAD" "$ROOT/case1/fleet/.git/FETCH_HEAD" 2>&1 | tr '\n' ' ')"
echo "--- refs after:"; git -C "$ROOT/case1/lane" for-each-ref --format='%(refname)'; git -C "$ROOT/case1/fleet" for-each-ref --format='%(refname)'
echo "--- full git call log:"; cat -n "$LOG"
