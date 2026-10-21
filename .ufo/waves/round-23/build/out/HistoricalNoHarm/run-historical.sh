#!/usr/bin/env bash
# run-historical.sh: historical no-harm baseline for the round-23 kama
# report-landing auditor (seat CloseKama22.HistoricalNoHarm).
#
# Runs the CURRENT auditor (a snapshot of the lane working-tree
# tools/report-landing-audit.py) and the FROZEN auditor (the committed blob
# 4fe9339f:tools/report-landing-audit.py) over the real fleet history, rounds
# 10-22, read-only:
#   <auditor> --rounds 10-22 --lane-repo LANE --fleet-repo FLEET --json
#   <auditor> --rounds 10-22 --lane-repo LANE --fleet-repo FLEET --json --no-errata
#   <auditor> --selftest
#
# Outputs (all in this script's directory), per run NAME in
# {current,frozen}-{history,no-errata,selftest}:
#   NAME.out NAME.err NAME.exit NAME.sha256
# plus pins.txt (lane/fleet/blob identities), <variant>.vs-diff (current vs
# frozen stdout+stderr diff, empty when identical), baseline-counts.txt
# (counts per run and per round) and a final gate line:
#   no-harm-gate=PASS  iff every current run equals its frozen run in
#                      stdout, stderr and exit status.
#
# Read-only: audited git calls are log/cat-file/rev-parse/ls-tree/show; the
# selftest runs only in TemporaryDirectory sandboxes; nothing is written to
# the lane or fleet repositories. Overrides: KAMA_LANE_REPO, KAMA_FLEET_REPO,
# PYTHON3.
set -u
umask 022

# Inherited GIT_* state (GIT_DIR, GIT_CONFIG_*, ...) must not redirect this
# harness's own git calls; the auditor strips GIT_* for its audited calls too.
for v in $(compgen -e | grep '^GIT_'); do unset "$v"; done
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 PYTHONDONTWRITEBYTECODE=1

LANE=${KAMA_LANE_REPO:-/home/vgpnk/Projects/shokunin/kama-shokunin}
FLEET=${KAMA_FLEET_REPO:-/home/vgpnk/Projects/shokunin}
BASE=4fe9339f8fc3a4a4a479d9c938a850da12f1124d
AUDIT=tools/report-landing-audit.py
ROUNDS=10-22
PY=${PYTHON3:-python3}
OUT=$(cd "$(dirname "$0")" && pwd) || exit 2

[ -d "$LANE/.git" ] || { echo "lane repo not found: $LANE" >&2; exit 2; }
[ -d "$FLEET/.git" ] || { echo "fleet repo not found: $FLEET" >&2; exit 2; }
[ -f "$LANE/$AUDIT" ] || { echo "current auditor not found: $LANE/$AUDIT" >&2; exit 2; }

WORK=$(mktemp -d /tmp/kama-r23-historical.XXXXXX) || exit 2
trap 'rm -rf "$WORK"' EXIT

# FROZEN: the exact committed base blob. CURRENT: a snapshot of the working
# copy, so the bytes that run are the bytes that are hashed.
git -C "$LANE" show "$BASE:$AUDIT" > "$WORK/frozen-audit.py" || exit 2
cp "$LANE/$AUDIT" "$WORK/current-audit.py" || exit 2

{
  echo "lane_master=$(git -C "$LANE" rev-parse --verify 'master^{commit}')"
  echo "lane_base=$(git -C "$LANE" rev-parse --verify "$BASE^{commit}")"
  echo "fleet_head=$(git -C "$FLEET" rev-parse --verify 'HEAD^{commit}')"
  echo "frozen_blob=$(git -C "$LANE" rev-parse "$BASE:$AUDIT")"
  echo "current_worktree_blob=$(git -C "$LANE" hash-object "$AUDIT")"
  echo "frozen_sha256=$(sha256sum < "$WORK/frozen-audit.py" | cut -d' ' -f1)"
  echo "current_sha256=$(sha256sum < "$WORK/current-audit.py" | cut -d' ' -f1)"
  echo "rounds=$ROUNDS"
} > "$OUT/pins.txt" || exit 2

run_one() {
  local name=$1 script=$2
  shift 2
  "$PY" "$script" "$@" > "$OUT/$name.out" 2> "$OUT/$name.err"
  echo $? > "$OUT/$name.exit"
  sha256sum "$OUT/$name.out" "$OUT/$name.err" > "$OUT/$name.sha256"
}

HIST=(--rounds "$ROUNDS" --lane-repo "$LANE" --fleet-repo "$FLEET" --json)
run_one current-history "$WORK/current-audit.py" "${HIST[@]}" &
run_one frozen-history "$WORK/frozen-audit.py" "${HIST[@]}" &
run_one current-no-errata "$WORK/current-audit.py" "${HIST[@]}" --no-errata &
run_one frozen-no-errata "$WORK/frozen-audit.py" "${HIST[@]}" --no-errata &
run_one current-selftest "$WORK/current-audit.py" --selftest &
run_one frozen-selftest "$WORK/frozen-audit.py" --selftest &
wait

gate=PASS
for v in history no-errata selftest; do
  {
    diff -u "$OUT/frozen-$v.out" "$OUT/current-$v.out"
    diff -u "$OUT/frozen-$v.err" "$OUT/current-$v.err"
  } > "$OUT/$v.vs-diff" 2>&1
  [ -s "$OUT/$v.vs-diff" ] && gate=FAIL
  [ "$(cat "$OUT/frozen-$v.exit")" = "$(cat "$OUT/current-$v.exit")" ] || gate=FAIL
done

"$PY" - "$OUT" > "$OUT/baseline-counts.txt" <<'PYEOF'
import json, re, sys
from pathlib import Path

out = Path(sys.argv[1])
lines = []


def exit_of(name):
    return (out / f"{name}.exit").read_text(encoding="utf-8").strip()


for name in ("current-history", "frozen-history",
             "current-no-errata", "frozen-no-errata"):
    try:
        doc = json.loads((out / f"{name}.out").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        lines.append(f"run={name} exit={exit_of(name)} UNPARSEABLE "
                     f"{exc.__class__.__name__}")
        continue
    s = doc["summary"]
    kinds = ",".join(f"{k}={v}" for k, v in sorted(s["by_kind"].items()))
    lines.append(
        f"run={name} exit={exit_of(name)} status={s['status']} "
        f"rounds={min(s['rounds'])}-{max(s['rounds'])} reports={s['reports']} "
        f"defects={s['defects']} corrected={s['corrected']} "
        f"uncorrected={s['uncorrected']} required={s['required_commits']} "
        f"post_report={s['post_report_commits']} "
        f"errata_rows={s['errata_rows']} "
        f"errata_unmatched={s['errata_unmatched']} "
        f"errata_invalid={s['errata_invalid']} by_kind[{kinds}]")
    if name == "current-history":
        for r in doc["results"]:
            lines.append(
                f"  round={r['round']} cutoff={r['cutoff']} "
                f"round_commits={r['round_commits']} required={r['required']} "
                f"post_report={len(r['post_report'])} "
                f"defects={len(r['defects'])}")
            for d in r["defects"]:
                mark = "corrected" if d["corrected_by"] else "UNCORRECTED"
                lines.append(f"    {mark} {d['kind']} {d['token']} "
                             f"errata_line={d['corrected_by']}")

for name in ("current-selftest", "frozen-selftest"):
    text = (out / f"{name}.out").read_text(encoding="utf-8")
    m = re.search(r"selftest cases=(\d+) failed=(\d+)\s*$", text)
    lines.append(
        f"run={name} exit={exit_of(name)} selftest cases={m.group(1)} "
        f"failed={m.group(2)}" if m
        else f"run={name} exit={exit_of(name)} NO-PARSE")

print("\n".join(lines))
PYEOF

[ -s "$OUT/baseline-counts.txt" ] || gate=FAIL
printf 'no-harm-gate=%s\n' "$gate" >> "$OUT/baseline-counts.txt"
cat "$OUT/pins.txt" "$OUT/baseline-counts.txt"
[ "$gate" = PASS ]
