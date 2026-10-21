#!/usr/bin/env bash
# graft-shallow-fixture.sh -- reusable fixtures for repo-local grafts and shallow state
# (.git/info/grafts, .git/shallow, grafts converted to replace refs) measured against
# report-landing-audit.py. Scratch only: every repository is created by git init under
# the work directory. Never point these helpers at the lane or fleet repositories.
#
#   bash graft-shallow-fixture.sh AUDITOR.py [WORKDIR]   # full matrix -> WORKDIR/results.tsv
#     WORKDIR must be fresh: fixtures are built by commits and are not idempotent (default: mktemp).
#   bash graft-shallow-fixture.sh AUDITOR.py [WORKDIR] promisor   # lazy-fetch probe on a promisor shallow clone
#   source graft-shallow-fixture.sh                      # then, per case:
#     gf_build DIR FAMILY; gf_fault NAME DIR; gf_run AUDITOR LANE FLEET DIR MODE
#
# Families = which lane commits the fleet report cites under "## Landed changes":
#   A: C1 C2 C3    B: C1 C3 (omits C2)    C: C3 only    D: nothing
# Lane (kama-shokunin round commits): R0 "base: lane init" @900, C1 "round-1: work" @1000,
#   C2 "round-1: measure" @1100, C3 "checkpoint(r1) save" @1150, C4 "round-1: late" @2050 (tip).
# Fleet: P0 "fleet: init" @1500, report commit F "round-1: report" @2000 (audit cutoff),
#   P1 "fleet: later" @2100 (HEAD).
# Neutralizer modes are PATH shims around the real git. The auditor's git_env() strips
# inherited GIT_* variables, so a neutralizer has to be applied where git reads it: the shim.

GF_REAL_GIT=$(command -v git)
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1

# ---- commit helpers: fixed identity and epoch dates; each prints the new full sha ----
gf_empty() { # REPO AUTHOR EPOCH SUBJECT
  GIT_AUTHOR_NAME=$2 GIT_COMMITTER_NAME=$2 GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_EMAIL=a@x \
  GIT_AUTHOR_DATE="@$3 +0000" GIT_COMMITTER_DATE="@$3 +0000" \
    git -C "$1" -c commit.gpgsign=false commit -q --allow-empty -m "$4" || return 1
  git -C "$1" rev-parse HEAD
}

gf_file() { # REPO AUTHOR EPOCH SUBJECT RELPATH CONTENT
  mkdir -p "$1/$(dirname "$5")" && printf '%s' "$6" >"$1/$5" && git -C "$1" add -- "$5" || return 1
  GIT_AUTHOR_NAME=$2 GIT_COMMITTER_NAME=$2 GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_EMAIL=a@x \
  GIT_AUTHOR_DATE="@$3 +0000" GIT_COMMITTER_DATE="@$3 +0000" \
    git -C "$1" -c commit.gpgsign=false commit -q -m "$4" || return 1
  git -C "$1" rev-parse HEAD
}

gf_orphan() { # REPO AUTHOR EPOCH SUBJECT RELPATH CONTENT: unreferenced root commit
  local tmp blob tree
  tmp=$(mktemp -d /tmp/gf-index.XXXXXX) || return 1
  blob=$(printf '%s' "$6" | git -C "$1" hash-object -w --stdin) || return 1
  GIT_INDEX_FILE=$tmp/index git -C "$1" update-index --add --cacheinfo "100644,$blob,$5" || return 1
  tree=$(GIT_INDEX_FILE=$tmp/index git -C "$1" write-tree) || return 1
  rm -rf "$tmp"
  GIT_AUTHOR_NAME=$2 GIT_COMMITTER_NAME=$2 GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_EMAIL=a@x \
  GIT_AUTHOR_DATE="@$3 +0000" GIT_COMMITTER_DATE="@$3 +0000" \
    git -C "$1" commit-tree "$tree" -m "$4"
}

gf_report() { # CITED-FULL-SHAS...: report text; each citation is a 12-hex prefix line
  printf '## Work performed\n\n- round 1 lane work\n\n## Landed changes\n\n'
  local s
  for s in "$@"; do printf -- '- %s round-1 commit\n' "${s:0:12}"; done
  printf '\n## Notes\n\n- fixture\n'
}

# gf_build DIR FAMILY: lane DIR/lane (round commits), fleet DIR/fleet (round-1 report at F).
# Sets GF_R0 GF_C1 GF_C2 GF_C3 GF_C4 (lane), GF_F (report commit), GF_P1 (fleet HEAD).
gf_build() {
  local w=$1 fam=$2 cited
  mkdir -p "$w" || return 1
  git init -q -b master "$w/lane" || return 1
  GF_R0=$(gf_empty "$w/lane" kama-shokunin 900 "base: lane init") || return 1
  GF_C1=$(gf_empty "$w/lane" kama-shokunin 1000 "round-1: work") || return 1
  GF_C2=$(gf_empty "$w/lane" kama-shokunin 1100 "round-1: measure") || return 1
  GF_C3=$(gf_empty "$w/lane" kama-shokunin 1150 "checkpoint(r1) save") || return 1
  GF_C4=$(gf_empty "$w/lane" kama-shokunin 2050 "round-1: late") || return 1
  case $fam in
    A) cited="$GF_C1 $GF_C2 $GF_C3" ;;
    B) cited="$GF_C1 $GF_C3" ;;
    C) cited="$GF_C3" ;;
    D) cited="" ;;
    *) echo "gf_build: unknown family $fam" >&2; return 1 ;;
  esac
  git init -q -b master "$w/fleet" || return 1
  gf_file "$w/fleet" fleet 1500 "fleet: init" README.md "fleet
" >/dev/null || return 1
  GF_F=$(gf_file "$w/fleet" fleet 2000 "round-1: report" .ufo/reports/round-1/kama.md "$(gf_report $cited)") || return 1
  GF_P1=$(gf_file "$w/fleet" fleet 2100 "fleet: later" README.md "later
") || return 1
}

# gf_fault NAME DIR: applies one repo-local fault. Sets GF_LANE_EFF = the lane the auditor audits.
gf_fault() {
  local name=$1 w=$2 l=$2/lane f=$2/fleet y z
  GF_LANE_EFF=$l
  case $name in
    none) ;;
    lane-graft-hide-mid) printf '%s %s\n' "$GF_C3" "$GF_C1" >"$l/.git/info/grafts" ;;
    lane-graft-tip-root) printf '%s\n' "$GF_C4" >"$l/.git/info/grafts" ;;
    lane-graft-inject-decoy)
      z=$(gf_orphan "$l" kama-shokunin 1020 "round-1: decoy" decoy.txt "decoy") || return 1
      printf '%s %s\n' "$GF_C1" "$z" >"$l/.git/info/grafts" ;;
    lane-graft-hide-mid-converted)
      printf '%s %s\n' "$GF_C3" "$GF_C1" >"$l/.git/info/grafts"
      git -C "$l" replace --convert-graft-file >/dev/null 2>&1 || return 1 ;;
    lane-shallow-tip) printf '%s\n' "$GF_C4" >"$l/.git/shallow" ;;
    lane-shallow-mid) printf '%s\n' "$GF_C2" >"$l/.git/shallow" ;;
    lane-realclone-depth1)
      git clone -q --depth 1 "file://$l" "$w/lane-clone" || return 1
      GF_LANE_EFF=$w/lane-clone ;;
    fleet-graft-cutoff-early)
      y=$(gf_orphan "$f" fleet 1050 "fleet: early draft" .ufo/reports/round-1/kama.md \
            "$(git -C "$f" show "$GF_F:.ufo/reports/round-1/kama.md")") || return 1
      printf '%s %s\n' "$GF_F" "$y" >"$f/.git/info/grafts" ;;
    fleet-shallow-at-report) printf '%s\n' "$GF_F" >"$f/.git/shallow" ;;
    fleet-shallow-at-head) printf '%s\n' "$GF_P1" >"$f/.git/shallow" ;;
    *) echo "gf_fault: unknown fault $name" >&2; return 1 ;;
  esac
}

# gf_shim DIR MODE: writes DIR/git, a PATH shim that runs the real git with one neutralizer.
#   none | nro (--no-replace-objects) | nro-env (GIT_NO_REPLACE_OBJECTS=1)
#   nograft (GIT_GRAFT_FILE=/dev/null) | noshallow (GIT_SHALLOW_FILE=/dev/null)
#   nro+nograft+noshallow (all three)
#   nolazy (GIT_NO_LAZY_FETCH=1) | noshallow+nolazy | noshallow+nolazyflag (--no-lazy-fetch flag)
gf_shim() {
  local d=$1 mode=$2 env_ext="" opt=""
  case $mode in
    none) return 0 ;;
    nro) opt=--no-replace-objects ;;
    nro-env) env_ext="GIT_NO_REPLACE_OBJECTS=1" ;;
    nograft) env_ext="GIT_GRAFT_FILE=/dev/null" ;;
    noshallow) env_ext="GIT_SHALLOW_FILE=/dev/null" ;;
    nro+nograft+noshallow) opt=--no-replace-objects
      env_ext="GIT_GRAFT_FILE=/dev/null GIT_SHALLOW_FILE=/dev/null" ;;
    nolazy) env_ext="GIT_NO_LAZY_FETCH=1" ;;
    noshallow+nolazy) env_ext="GIT_SHALLOW_FILE=/dev/null GIT_NO_LAZY_FETCH=1" ;;
    noshallow+nolazyflag) opt=--no-lazy-fetch
      env_ext="GIT_SHALLOW_FILE=/dev/null" ;;
    *) echo "gf_shim: unknown mode $mode" >&2; return 1 ;;
  esac
  mkdir -p "$d" && printf '#!/bin/sh\nexec env %s "%s" %s "$@"\n' "$env_ext" "$GF_REAL_GIT" "$opt" >"$d/git" \
    && chmod +x "$d/git"
}

# gf_row RC JSON ERR: TSV "rc status round_commits required cutoff defects" (or could-not-evaluate)
gf_row() {
  if [ -s "$2" ] && jq -e '.results' "$2" >/dev/null 2>&1; then
    printf '%s\t' "$1"
    jq -r '.summary.status as $s | .results[0] | [$s, .round_commits, .required, .cutoff,
      ([.defects[] | "\(.kind):\(.token[0:12])"] | if length == 0 then "-" else join(" ") end)] | @tsv' "$2"
  else
    printf '%s\tcould-not-evaluate\t-\t-\t-\t%s\n' "$1" "$(tail -n 1 "$3" | tr '\t' ' ')"
  fi
}

# gf_run AUDITOR LANE FLEET DIR MODE: one auditor run under MODE; prints the TSV row + visible lane subjects
gf_run() {
  local aud=$1 lane=$2 fleet=$3 d=$4 mode=$5 path=$PATH rc row vis
  if [ "$mode" != none ]; then
    gf_shim "$d/shim-$mode" "$mode" || return 1
    path=$d/shim-$mode:$PATH
  fi
  PATH=$path python3 "$aud" --lane-repo "$lane" --fleet-repo "$fleet" --rounds 1 --no-errata --json \
    >"$d/out-$mode.json" 2>"$d/err-$mode.txt"
  rc=$?
  row=$(gf_row "$rc" "$d/out-$mode.json" "$d/err-$mode.txt")
  vis=$(PATH=$path git -C "$lane" log --format=%s master 2>/dev/null | paste -sd'|' -)
  printf '%s\t%s\n' "$row" "${vis:--}"
}

# gf_plain_one OUT FAULT LANE SHIMROOT: plain-git observations per neutralizer (no auditor)
gf_plain_one() {
  local out=$1 fault=$2 lane=$3 sr=$4 mode path gd
  gd=$(git -C "$lane" rev-parse --absolute-git-dir 2>/dev/null)
  {
    echo "== $fault"
    echo "   raw parents of master: $(git -C "$lane" cat-file -p master | grep '^parent' | paste -sd' ' -)"
    echo "   info/grafts: $([ -e "$gd/info/grafts" ] && echo present || echo absent);" \
         "shallow file: $([ -e "$gd/shallow" ] && echo present || echo absent);" \
         "is-shallow-repository: $(git -C "$lane" rev-parse --is-shallow-repository)"
    echo "   replace refs: $(git -C "$lane" for-each-ref --format='%(refname)' refs/replace | paste -sd' ' -)"
    for mode in none nro nro-env nograft noshallow; do
      path=$PATH
      if [ "$mode" != none ]; then gf_shim "$sr/$mode" "$mode" || return 1; path=$sr/$mode:$PATH; fi
      echo "   [$mode] log master (%h>%p subject): $(PATH=$path git -C "$lane" log --format='%h>%p %s' master 2>/dev/null | paste -sd';' -)"
      echo "   [$mode] stderr hint lines: $(PATH=$path git -C "$lane" log master 2>&1 >/dev/null | grep -c '^hint:')"
    done
  } >>"$out"
}

# gf_matrix AUDITOR [WORKDIR]: every fault x family x neutralizer -> WORKDIR/results.tsv
gf_matrix() {
  local aud=$1 root=${2:-}
  local faults="none lane-graft-hide-mid lane-graft-tip-root lane-graft-inject-decoy lane-graft-hide-mid-converted lane-shallow-tip lane-shallow-mid lane-realclone-depth1 fleet-graft-cutoff-early fleet-shallow-at-report fleet-shallow-at-head"
  local modes="none nro nro-env nograft noshallow nro+nograft+noshallow"
  local fault fam mode d row
  [ -n "$root" ] || root=$(mktemp -d /tmp/gf-matrix.XXXXXX) || return 1
  mkdir -p "$root" || return 1
  printf 'fault\tfamily\tneutral\trc\tstatus\tround_commits\trequired\tcutoff\tdefects\tlane_visible_round_subjects\n' >"$root/results.tsv"
  : >"$root/plain-git-semantics.txt"
  for fault in $faults; do
    for fam in A B C D; do
      d=$root/$fault-$fam
      if ! { gf_build "$d" "$fam" && gf_fault "$fault" "$d"; } >>"$root/build.log" 2>&1; then
        printf '%s\t%s\tBUILD-FAIL\n' "$fault" "$fam" >>"$root/results.tsv"
        continue
      fi
      if [ "$fam" = B ]; then gf_plain_one "$root/plain-git-semantics.txt" "$fault" "$GF_LANE_EFF" "$d/plain-shims"; fi
      for mode in $modes; do
        row=$(gf_run "$aud" "$GF_LANE_EFF" "$d/fleet" "$d" "$mode")
        printf '%s\t%s\t%s\t%s\n' "$fault" "$fam" "$mode" "$row" >>"$root/results.tsv"
      done
    done
  done
  echo "$root"
}

# gf_promisor_probe AUDITOR [WORKDIR]: a real shallow clone that is also a promisor remote at
# ssh://example.invalid whose core.sshCommand writes a marker and fails. The fleet report cites the
# three missing lane commits by full 40-hex sha (full-OID lookups reach lazy fetch; 12-hex do not).
# Prints per neutralizer: rc, whether the repo-configured command EXECUTED, last auditor stderr line.
gf_promisor_probe() {
  local aud=$1 w=$2 mode c1 c2 c3 M L F rc path
  [ -n "$w" ] || w=$(mktemp -d /tmp/gf-promisor.XXXXXX) || return 1
  gf_build "$w" A && gf_fault lane-realclone-depth1 "$w" || return 1
  L=$GF_LANE_EFF F=$w/fleet M=$w/marker
  c1=$(git -C "$w/lane" rev-parse master~3)
  c2=$(git -C "$w/lane" rev-parse master~2)
  c3=$(git -C "$w/lane" rev-parse master~1)
  printf '## Work performed\n\n- fixture\n\n## Landed changes\n\n- %s round-1 commit\n- %s round-1 commit\n- %s round-1 commit\n\n## Notes\n\n- fixture\n' \
    "$c1" "$c2" "$c3" >"$F/.ufo/reports/round-1/kama.md"
  GIT_AUTHOR_NAME=fleet GIT_COMMITTER_NAME=fleet GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_EMAIL=a@x \
  GIT_AUTHOR_DATE="@2200 +0000" GIT_COMMITTER_DATE="@2200 +0000" \
    git -C "$F" -c commit.gpgsign=false commit -q -am "report: full sha citations" || return 1
  git -C "$L" config extensions.partialClone origin
  git -C "$L" config core.repositoryformatversion 1
  git -C "$L" config remote.origin.url ssh://example.invalid/x.git
  git -C "$L" config remote.origin.promisor true
  git -C "$L" config core.sshCommand "touch $M; false"
  printf 'neutral\trc\tconfigured-command\tlast-stderr-line\n'
  for mode in none noshallow nolazy noshallow+nolazy noshallow+nolazyflag; do
    rm -f "$M"
    path=$PATH
    if [ "$mode" != none ]; then gf_shim "$w/shim-$mode" "$mode" || return 1; path=$w/shim-$mode:$PATH; fi
    PATH=$path python3 "$aud" --lane-repo "$L" --fleet-repo "$F" --rounds 1 --no-errata --json \
      >"$w/promisor-out-$mode.json" 2>"$w/promisor-err-$mode.txt"
    rc=$?
    printf '%s\t%s\t%s\t%s\n' "$mode" "$rc" "$([ -e "$M" ] && echo EXECUTED || echo not-executed)" \
      "$(tail -n 1 "$w/promisor-err-$mode.txt" | tr '\t' ' ')"
  done
  echo "$w"
}

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  [ $# -ge 1 ] || { echo "usage: bash $0 AUDITOR.py [WORKDIR] [promisor]" >&2; exit 2; }
  if [ "${3:-}" = promisor ]; then gf_promisor_probe "$1" "${2:-}"; else gf_matrix "$1" "${2:-}"; fi
fi
