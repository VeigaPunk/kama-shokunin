#!/usr/bin/env bash
# Round-23 scout probe: repo-local git channels vs report-landing-audit.py at base.
# All fixtures are fresh repos under /tmp. No network. GIT_CONFIG_GLOBAL=/dev/null.
set -u
ROOT=/tmp/kama-r23-scout-fs
AUDIT=$ROOT/audit_base.py
BIN=$ROOT/bin
MARK=$ROOT/markers/all.log
RESULTS=$ROOT/results.tsv
mkdir -p "$BIN" "$ROOT/markers" "$ROOT/run" "$ROOT/logs"
: > "$MARK"
: > "$RESULTS"

export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=fixture@example.invalid
export GIT_COMMITTER_NAME=fixture GIT_COMMITTER_EMAIL=fixture@example.invalid
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_OBJECT_DIRECTORY \
      GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_EXTERNAL_DIFF GIT_CONFIG_PARAMETERS \
      GIT_CONFIG_COUNT 2>/dev/null || true

say() { printf '%s\n' "$*" | tee -a "$ROOT/probe.log" >/dev/null; }
record() { printf '%s\n' "$*" >> "$RESULTS"; }

# ---------------------------------------------------------------- marker scripts
mk_marker_script() { # $1=path $2=tag $3=tail
  { printf '#!/bin/sh\nprintf "%s|%%s\\n" "$*" >> %s\n' "$2" "$MARK"
    printf '%s\n' "$3"; } > "$1"
  chmod +x "$1"
}
mk_marker_script "$BIN/fsmon-legacy.sh" fsmon-legacy 'exit 1'
mk_marker_script "$BIN/fsmonitor-watchman" fsmonitor-watchman 'exit 1'
mk_marker_script "$BIN/extdiff.sh" extdiff 'exit 0'
mk_marker_script "$BIN/altrefs.sh" altrefs 'cat "$ALT_OID_FILE"'
mk_marker_script "$BIN/filter-process.sh" filter-process 'exit 1'

{ printf '#!/bin/sh\nprintf "textconv|%%s\\n" "$*" >> %s\ncat "$1"\n' "$MARK"; } > "$BIN/textconv.sh"
chmod +x "$BIN/textconv.sh"
{ printf '#!/bin/sh\nprintf "filter-clean|%%s\\n" "$*" >> %s\ncat\n' "$MARK"; } > "$BIN/filter-clean.sh"
chmod +x "$BIN/filter-clean.sh"
{ printf '#!/bin/sh\nprintf "filter-smudge|%%s\\n" "$*" >> %s\ncat\n' "$MARK"; } > "$BIN/filter-smudge.sh"
chmod +x "$BIN/filter-smudge.sh"

mk_hooks() { # $1=dir
  mkdir -p "$1"
  for h in pre-commit post-commit post-checkout post-index-change \
           reference-transaction post-merge pre-push; do
    { printf '#!/bin/sh\nprintf "hook-%s|%%s\\n" "$*" >> %s\ncat >/dev/null 2>&1 || true\nexit 0\n' "$h" "$MARK"; } > "$1/$h"
    chmod +x "$1/$h"
  done
}

# ---------------------------------------------------------------------- fixture
newfix() { # $1=name -> sets D, LANE_SHA, SHORT
  D=$ROOT/run/$1
  rm -rf "$D"; mkdir -p "$D"
  git init -q -b master "$D/lane" || return 1
  (
    cd "$D/lane" || exit 1
    mkdir -p corpus registry
    : > registry/report-landing-errata.tsv
    printf 'lane file\n' > f
    cat > corpus/SOURCES.md <<'EOF'
## Registry
| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S001 | upstream — https://example.invalid/project/blob/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/source.cc | code | A | fixture scope | fixture anchor | fixture teaches | mined | 2026-10-21 | on-release | — |
EOF
    git add f corpus/SOURCES.md registry/report-landing-errata.tsv
    GIT_AUTHOR_NAME=kama-shokunin GIT_COMMITTER_NAME=kama-shokunin \
    GIT_AUTHOR_DATE='1234567890 +0000' GIT_COMMITTER_DATE='1234567890 +0000' \
      git commit -q -m 'round-23: fixture commit' || exit 1
    git rev-parse HEAD > "$D/lane_sha"
  ) || return 1
  LANE_SHA=$(cat "$D/lane_sha")
  SHORT=$(printf '%s' "$LANE_SHA" | cut -c1-12)
  git init -q -b master "$D/fleet" || return 1
  (
    cd "$D/fleet" || exit 1
    mkdir -p .ufo/reports/round-23 registry
    {
      printf '## Work performed\nfixture body cites %s and %s\n' "$LANE_SHA" "$SHORT"
      printf '## Landed changes\n- %s\n' "$SHORT"
    } > .ufo/reports/round-23/kama.md
    : > registry/report-landing-errata.tsv
    printf '*.md diff=tcdrv filter=evil\n' > .gitattributes
    printf 'note body\n' > note.md
    printf 'other one\n' > other.txt
    git add -A
    GIT_AUTHOR_DATE='1234567900 +0000' GIT_COMMITTER_DATE='1234567900 +0000' \
      git commit -q -m 'fleet fixture report' || exit 1
    printf 'other two\n' > other.txt
    git add other.txt
    GIT_AUTHOR_DATE='1234567910 +0000' GIT_COMMITTER_DATE='1234567910 +0000' \
      git commit -q -m 'fleet fixture churn' || exit 1
  ) || return 1
  return 0
}

# ---------------------------------------------------------------------- runner
mark_count() { [ -f "$MARK" ] && wc -l < "$MARK" || echo 0; }

audit() { # $1=name ; expects $D
  local name=$1 before after rc
  before=$(mark_count)
  ( cd "$ROOT" && python3 "$AUDIT" --lane-repo "$D/lane" \
      --fleet-repo "$D/fleet" --rounds 23 ) \
      > "$ROOT/logs/$name.audit.out" 2> "$ROOT/logs/$name.audit.err"
  rc=$?
  after=$(mark_count)
  local status line new
  status=$(grep -o 'status=[a-z]*' "$ROOT/logs/$name.audit.out" | tail -1)
  line=$(grep '^summary ' "$ROOT/logs/$name.audit.out" | tail -1)
  new=$(sed -n "$((before+1)),\$p" "$MARK" 2>/dev/null || true)
  record "AUDIT	$name	rc=$rc	$status	markers_new=$((after-before))	$line"
  if [ "$after" -gt "$before" ]; then
    printf 'AUDIT-MARKERS %s:\n%s\n' "$name" "$new" >> "$ROOT/logs/$name.audit.err"
  fi
}

control() { # $1=name $2=label; rest = command
  local name=$1 label=$2; shift 2
  local before after new rc
  before=$(mark_count)
  ( cd "$D" && "$@" ) > "$ROOT/logs/$name.$label.out" 2> "$ROOT/logs/$name.$label.err"
  rc=$?
  after=$(mark_count)
  new=$(sed -n "$((before+1)),\$p" "$MARK" 2>/dev/null || true)
  record "CONTROL	$name	$label	rc=$rc	markers_new=$((after-before))"
  if [ "$after" -gt "$before" ]; then
    printf '%s\n' "$new" >> "$ROOT/logs/$name.controls.markers"
  fi
}

gitf() { git -C "$D/fleet" "$@"; }
gitl() { git -C "$D/lane" "$@"; }

# ------------------------------------------------------------------- scenarios
# 0. baseline
newfix base && audit base
control base revparse gitf rev-parse --verify HEAD^{commit}
control base logdiff gitf log --diff-filter=A --format=%at -- .ufo/reports/round-23/kama.md
control base logfmt gitf log --format=%H%x1f%an%x1f%at%x1f%s%x1e master

# 1. core.hooksPath with a full hook set
D=$ROOT/run/hookspath; rm -rf "$D"; newfix hookspath
mk_hooks "$D/hooks"
gitf config core.hooksPath "$D/hooks"
audit hookspath
control hookspath status gitf status --porcelain
control hookspath commit gitf commit --allow-empty -m ctl
control hookspath checkout gitf checkout -q -b ctl-branch

# 2. core.fsmonitor as a hook pathname (documented legacy form)
D=$ROOT/run/fsmonlegacy; rm -rf "$D"; newfix fsmonlegacy
gitf config core.fsmonitor "$BIN/fsmon-legacy.sh"
audit fsmonlegacy
control fsmonlegacy status gitf status --porcelain

# 3. core.fsmonitor=true with an fsmonitor-watchman hook in hooksPath
D=$ROOT/run/fsmontrue; rm -rf "$D"; newfix fsmontrue
mk_hooks "$D/hooks"
gitf config core.hooksPath "$D/hooks"
gitf config core.fsmonitor true
audit fsmontrue
control fsmontrue status gitf status --porcelain

# 4. diff.external
D=$ROOT/run/diffexternal; rm -rf "$D"; newfix diffexternal
gitf config diff.external "$BIN/extdiff.sh"
audit diffexternal
control diffexternal diff gitf diff HEAD~1 HEAD
control diffexternal logpatch gitf log -p -1
control diffexternal logpatch_ext gitf log -p -1 --ext-diff
control diffexternal show_ext gitf show --ext-diff HEAD

# 5. textconv driver via diff.<drv>.textconv + committed attribute
D=$ROOT/run/textconv; rm -rf "$D"; newfix textconv
gitf config diff.tcdrv.textconv "$BIN/textconv.sh"
audit textconv
control textconv logpatch gitf log -p -1 -- .ufo/reports/round-23/kama.md
control textconv difftextconv gitf diff --textconv HEAD~1 HEAD
control textconv showblob gitf show HEAD:.ufo/reports/round-23/kama.md

# 6. filter driver clean/smudge
D=$ROOT/run/filterdrv; rm -rf "$D"; newfix filterdrv
gitf config filter.evil.clean "$BIN/filter-clean.sh"
gitf config filter.evil.smudge "$BIN/filter-smudge.sh"
gitf config filter.evil.required true
audit filterdrv
printf 'note changed\n' > "$D/fleet/note.md"
control filterdrv add gitf add note.md
control filterdrv catfile_filters gitf cat-file --filters HEAD:note.md
rm -f "$D/fleet/note.md"
control filterdrv checkout gitf checkout -- note.md

# 7. filter driver process form only
D=$ROOT/run/filterprocess; rm -rf "$D"; newfix filterprocess
gitf config filter.evil.process "$BIN/filter-process.sh"
gitf config filter.evil.required true
audit filterprocess
printf 'note changed\n' > "$D/fleet/note.md"
control filterprocess add gitf add note.md

# 8. core.alternateRefsCommand with an alternate object store
D=$ROOT/run/altrefs; rm -rf "$D"; newfix altrefs
git init -q -b master "$D/alt"
( cd "$D/alt" && printf 'alt\n' > a && git add a && \
  GIT_AUTHOR_DATE='1234567000 +0000' GIT_COMMITTER_DATE='1234567000 +0000' \
  git commit -q -m 'alt commit' && git rev-parse HEAD > "$D/alt_sha" )
printf '%s\n' "$D/alt/.git/objects" > "$D/fleet/.git/objects/info/alternates"
cp "$D/alt_sha" "$BIN/alt_oid"
export ALT_OID_FILE=$BIN/alt_oid
gitf config core.alternateRefsCommand "$BIN/altrefs.sh"
audit altrefs
control altrefs revlist_alt gitf rev-list --alternate-refs HEAD
control altrefs log_alt gitf log --alternate-refs --oneline HEAD
control altrefs revparse_all gitf rev-parse --all
control altrefs uploadpack sh -c 'cd "$1/fleet" && git upload-pack --advertise-refs . >/dev/null' _ "$D"

# 9. every channel at once
D=$ROOT/run/combined; rm -rf "$D"; newfix combined
mk_hooks "$D/hooks"
gitf config core.hooksPath "$D/hooks"
gitf config core.fsmonitor "$BIN/fsmon-legacy.sh"
gitf config diff.external "$BIN/extdiff.sh"
gitf config diff.tcdrv.textconv "$BIN/textconv.sh"
gitf config filter.evil.clean "$BIN/filter-clean.sh"
gitf config filter.evil.smudge "$BIN/filter-smudge.sh"
gitf config filter.evil.required true
printf '%s\n' "$ROOT/run/altrefs/alt/.git/objects" > "$D/fleet/.git/objects/info/alternates"
export ALT_OID_FILE=$BIN/alt_oid
gitf config core.alternateRefsCommand "$BIN/altrefs.sh"
audit combined
control combined status gitf status --porcelain

record "--- marker inventory ---"
while IFS= read -r l; do record "MARKER	$l"; done < "$MARK"
say "probe done"
