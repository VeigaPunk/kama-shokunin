#!/bin/bash
# Probe: does the audited repo's object format (sha1 vs sha256 vs compat) change
# tools/report-landing-audit.py's verdict?  Base master 4fe9339f.
# Runs only in fresh temp repos with global/system git config disabled.
set -u
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=kama-shokunin GIT_COMMITTER_NAME=kama-shokunin
export GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_EMAIL=a@x
ROOT=$(mktemp -d /tmp/kama-r23-objectfmt-XXXXXX)
AUDIT=${AUDIT:-/home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py}

init() { rm -rf "$ROOT/$1"; git init -q ${2:+--object-format=$2} -b master "$ROOT/$1"; }
commit() { # repo msg when [path]
  local r=$1 msg=$2 when=$3 p=${4:-f}
  mkdir -p "$ROOT/$r/$(dirname "$p")"
  printf '%s\n' "$msg" >> "$ROOT/$r/$p"
  GIT_AUTHOR_DATE="@$when +0000" GIT_COMMITTER_DATE="@$when +0000" git -C "$ROOT/$r" add -A
  GIT_AUTHOR_DATE="@$when +0000" GIT_COMMITTER_DATE="@$when +0000" \
    git -C "$ROOT/$r" -c commit.gpgsign=false commit -q -m "$msg" >/dev/null
  git -C "$ROOT/$r" rev-parse HEAD
}
report() { # fleet body
  mkdir -p "$ROOT/$1/.ufo/reports/round-1"
  printf '%b' "$2" > "$ROOT/$1/.ufo/reports/round-1/kama.md"
  git -C "$ROOT/$1" add -A
  GIT_AUTHOR_DATE="@1300 +0000" GIT_COMMITTER_DATE="@1300 +0000" \
    git -C "$ROOT/$1" -c commit.gpgsign=false commit -q -m "round-1: kama report"
}
run() { # label lane fleet
  local out rc
  out=$(python3 "$AUDIT" --lane-repo "$ROOT/$2" --fleet-repo "$ROOT/$3" \
        --branch master --rounds 1 --no-errata 2>&1); rc=$?
  local msg
  if [ "$rc" = 2 ]; then msg=$(printf '%s' "$out" | head -1); else msg=$(printf '%s' "$out" | tail -1); fi
  printf '%s\trc=%s\t%s\n' "$1" "$rc" "$msg"
}
FAKE64=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
FAKE40=0123456789abcdef0123456789abcdef01234567

# 1 control: sha1 lane, full native 40-hex citations
init L1 ""; init F1 ""
S1=$(commit L1 "round-1: work" 1000); S2=$(commit L1 "round-1: measure" 1100)
report F1 "# r1\n## Landed changes\n- \`$S1\` work\n- \`$S2\` measure\n"
run control-sha1-full L1 F1

# 2 sha256 lane, full native 64-hex citations (correct report)
init L2 sha256; init F2 sha256
S1=$(commit L2 "round-1: work" 1000); S2=$(commit L2 "round-1: measure" 1100)
report F2 "# r1\n## Landed changes\n- \`$S1\` work\n- \`$S2\` measure\n"
run sha256-full L2 F2

# 3 sha256 lane, zero pre-cutoff commits, fabricated 64-hex citation
init L3 sha256; init F3
commit L3 "round-1: after report" 2000 >/dev/null
report F3 "# r1\n## Landed changes\n- \`$FAKE64\` fabricated\n"
run sha256-fabricated64 L3 F3

# 4 sha1 control, zero pre-cutoff commits, fabricated 40-hex citation
init L4; init F4
commit L4 "round-1: after report" 2000 >/dev/null
report F4 "# r1\n## Landed changes\n- \`$FAKE40\` fabricated\n"
run sha1-fabricated40 L4 F4

# 5 sha256 lane, correct 12-hex native prefix citations
init L5 sha256; init F5
S1=$(commit L5 "round-1: work" 1000); S2=$(commit L5 "round-1: measure" 1100)
report F5 "# r1\n## Landed changes\n- \`${S1:0:12}\` work\n- \`${S2:0:12}\` measure\n"
run sha256-prefix12 L5 F5

# 6 sha256+compatObjectFormat=sha1 lane, compat sha1 name citations
init L6 sha256; init F6
git -C "$ROOT/L6" config extensions.compatObjectFormat sha1
S1=$(commit L6 "round-1: work" 1000); S2=$(commit L6 "round-1: measure" 1100)
C1=$(git -C "$ROOT/L6" rev-parse --output-object-format=sha1 "$S1")
C2=$(git -C "$ROOT/L6" rev-parse --output-object-format=sha1 "$S2")
report F6 "# r1\n## Landed changes\n- \`$C1\` work\n- \`$C2\` measure\n"
run compat-sha1-names L6 F6

# 7 flip extensions.objectFormat=sha256 on an existing sha1 repo
init L7 ""; init F7
commit L7 "round-1: work" 1000 >/dev/null
git -C "$ROOT/L7" config extensions.objectFormat sha256
run flip-objectFormat L7 F7

# 8 flip extensions.compatObjectFormat=sha1 on an existing sha1 repo
init L8 ""; init F8
commit L8 "round-1: work" 1000 >/dev/null
git -C "$ROOT/L8" config extensions.compatObjectFormat sha1
run flip-compatObjectFormat L8 F8

# 9 sha256 fleet only, sha1 lane with full 40-hex citations
init L9 ""; init F9 sha256
S1=$(commit L9 "round-1: work" 1000); S2=$(commit L9 "round-1: measure" 1100)
report F9 "# r1\n## Landed changes\n- \`$S1\` work\n- \`$S2\` measure\n"
run sha256-fleet-only L9 F9

rm -rf "$ROOT"
