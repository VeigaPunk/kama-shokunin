#!/usr/bin/env bash
# Re-record the five round-19 lane selftests (plus the C1 counting command that
# round-19 evidence/final-selftests.txt carried) on a clean checkout of a commit.
#
# Usage: run-selftests-at-commit.sh CLONE_DIR EXPECTED_REV OUT_FILE
#
# CLONE_DIR is a throwaway clone checked out at EXPECTED_REV; never the lane.
# Every selftest writes only to its own tempfile.TemporaryDirectory; this
# runner captures stdout/stderr into a private mktemp directory and records
# `git status --porcelain` before and after, so a dirty tree is visible.
set -u
if [ "$#" -ne 3 ]; then
  echo "usage: $0 CLONE_DIR EXPECTED_REV OUT_FILE" >&2
  exit 2
fi
clone=$1
expected=$2
out=$3
if [ -e "$out" ]; then
  echo "refusing to overwrite $out" >&2
  exit 2
fi
cap=$(mktemp -d) || exit 2
trap 'rm -rf "$cap"' EXIT
cd "$clone" || exit 2

count_lines() {
  if [ -s "$1" ]; then wc -l <"$1"; else echo 0; fi
}

emit_file() {
  cat "$1"
  # keep the next record on its own line if the capture lacks a final newline
  if [ -s "$1" ] && [ -n "$(tail -c1 "$1")" ]; then
    echo
    echo "[capture had no trailing newline]"
  fi
}

summary=""
run_case() {
  local key=$1 label=$2 script=$3
  shift 3
  local t0 t1 rc
  echo "=== $label ==="
  echo "command: python3 $script${*:+ $*}"
  echo "blob=$(git rev-parse "HEAD:$script") sha256=$(sha256sum "$script" | cut -d' ' -f1)"
  t0=$(date +%s%N)
  python3 "$script" "$@" >"$cap/stdout" 2>"$cap/stderr"
  rc=$?
  t1=$(date +%s%N)
  echo "--- stdout ($(count_lines "$cap/stdout") lines) ---"
  emit_file "$cap/stdout"
  echo "--- stderr ($(count_lines "$cap/stderr") lines) ---"
  emit_file "$cap/stderr"
  echo "exit=$rc wall_ms=$(( (t1 - t0) / 1000000 ))"
  summary="$summary $key=$rc"
}

{
  rev=$(git rev-parse HEAD)
  echo "measured_tree=commit:$rev"
  if [ "$rev" = "$expected" ]; then
    echo "expected_rev=$expected match=yes"
  else
    echo "expected_rev=$expected match=NO"
  fi
  echo "head_ref=$(git symbolic-ref -q HEAD || echo detached)"
  echo "clone_of=$(git remote get-url origin)"
  echo "measured_utc_start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "python3=$(command -v python3) $(python3 --version 2>&1)"
  git --version
  echo "kernel=$(uname -sr)"
  git status --porcelain >"$cap/status_before"
  echo "status_porcelain_before_lines=$(count_lines "$cap/status_before")"
  emit_file "$cap/status_before"

  run_case gate "gate selftest" tests/llamacpp-live/check-receipt.py --selftest
  run_case grid "grid selftest" tests/llamacpp-live/install-tree-grid.py --selftest
  run_case citation "citation-provenance selftest" tools/citation-provenance.py --selftest
  run_case live "kama-llamacpp-live selftest (no server; ephemeral tcp6 loopback listeners)" tools/kama-llamacpp-live.py --selftest
  run_case sources "sources-append-only selftest" tools/sources-append-only.py --selftest
  run_case c1 "extra: C1 counting command (round-19 final-selftests.txt §C1 shape)" tools/citation-provenance.py

  echo "=== tree after ==="
  echo "rev_after=$(git rev-parse HEAD)"
  git status --porcelain >"$cap/status_after"
  echo "status_porcelain_after_lines=$(count_lines "$cap/status_after")"
  emit_file "$cap/status_after"
  git status --porcelain --ignored >"$cap/status_ignored"
  echo "status_porcelain_ignored_after_lines=$(count_lines "$cap/status_ignored")"
  emit_file "$cap/status_ignored"
  echo "measured_utc_end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "summary:$summary porcelain_after_lines=$(count_lines "$cap/status_after")"
} >"$out"
