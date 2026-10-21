#!/usr/bin/env bash
# Refusal-policy grid: frozen / candidate / split / allsur arms on scratch repos.
set -u
ARMS=/tmp/kama-r23/crp-arms
T=$(mktemp -d /tmp/kama-r23/crp-arms/run.XXXX)
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
mk() { git init -q -b master "$1"; }
cm() { # repo author time subject [file] [extra -c]
  local f=${5:-f}
  printf '%s\n' "$4" >> "$1/$f"
  git -C "$1" add -- "$f"
  GIT_AUTHOR_NAME=$2 GIT_COMMITTER_NAME=$2 GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_EMAIL=a@x \
  GIT_AUTHOR_DATE="@$3 +0000" GIT_COMMITTER_DATE="@$3 +0000" \
    git -C "$1" -c commit.gpgsign=false ${6:+-c "$6"} commit -q -m "$4" 2>/dev/null
  git -C "$1" rev-parse HEAD
}
report() { # extra-landed-lines extra-tail
  mkdir -p "$F/.ufo/reports/round-1"
  printf '## Landed changes\n\n- %s\n%b' "$LC" "$1" > "$F/.ufo/reports/round-1/kama.md"
  printf '%b' "${2:-}" >> "$F/.ufo/reports/round-1/kama.md"
  cm "$F" fleet 2000 "round-1: report" .ufo/reports/round-1/kama.md >/dev/null
}
raw() { # repo author time subject-bytes(%b) -> sha; bypasses commit verify_utf8
  local tree parent sha
  tree=$(git -C "$1" rev-parse 'HEAD^{tree}'); parent=$(git -C "$1" rev-parse HEAD)
  sha=$(printf 'tree %s\nparent %s\nauthor %b <a@x> %s +0000\ncommitter %b <a@x> %s +0000\n\n%b\n' \
    "$tree" "$parent" "$2" "$3" "$2" "$3" "$4" | git -C "$1" hash-object -t commit -w --stdin)
  git -C "$1" update-ref refs/heads/master "$sha"; echo "$sha"
}
lane() { L=$T/$1/lane; F=$T/$1/fleet; mk "$L"; mk "$F"; LC=$(cm "$L" kama-shokunin 1000 "round-1: work"); }
run() { # name [extra args...]
  local n=$1; shift
  local line="$n"
  for arm in frozen candidate split allsur; do
    python3 "$ARMS/$arm.py" --lane-repo "$L" --fleet-repo "$F" --no-errata --json "$@" >"$T/$n.$arm.out" 2>"$T/$n.$arm.err"
    local rc=$? tb=""
    grep -q Traceback "$T/$n.$arm.err" && tb="TB"
    local k
    k=$(python3 -c 'import json,sys
try:
  d=json.load(open(sys.argv[1])); print(",".join(x["kind"] for r in d["results"] for x in r["defects"]) or "-")
except Exception: print("")' "$T/$n.$arm.out")
    line="$line | $arm=$rc$tb${k:+[$k]}"
  done
  echo "$line"
}
lane ctl; report ""; run ctl --rounds 1
lane u1; cm "$L" someone 1100 $'note \xff\xfe' >/dev/null; report ""; run u1-unrelated-subject --rounds 1
lane u2; cm "$L" $'some\xffone' 1100 "note" >/dev/null; report ""; run u2-unrelated-author --rounds 1
lane e1; cm "$L" someone 1100 $'caf\xe9' f i18n.commitEncoding=x-bogus >/dev/null; report ""; run e1-bogus-encoding-header --rounds 1
lane e2; cm "$L" someone 1100 $'caf\xe9' f i18n.commitEncoding=ISO-8859-1 >/dev/null; report ""; run e2-latin1-header --rounds 1
lane r1; cm "$L" kama-shokunin 1100 $'round-1: caf\xe9' >/dev/null; report ""; run r1-round-nonutf8-omitted --rounds 1
lane r2; X=$(cm "$L" kama-shokunin 1100 $'round-1: caf\xe9'); report "- $X\n"; run r2-round-nonutf8-cited --rounds 1
lane ru1; raw "$L" someone 1100 'note \xff\xfe' >/dev/null; report ""; run ru1-RAW-unrelated-subject --rounds 1
lane ru2; raw "$L" 'some\xffone' 1100 'note' >/dev/null; report ""; run ru2-RAW-unrelated-author --rounds 1
lane rr1; raw "$L" kama-shokunin 1100 'round-1: caf\xe9' >/dev/null; report ""; run rr1-RAW-round-omitted --rounds 1
lane rr2; X=$(raw "$L" kama-shokunin 1100 'round-1: caf\xe9'); report "- $X\n"; run rr2-RAW-round-cited --rounds 1
lane rz2; raw "$L" kama-shokunin 1100 '\xc1\xb2ound-1: hidden' >/dev/null; report ""; run rz2-RAW-overlong-prefix-omitted --rounds 1
lane rp; raw "$L" kama-shokunin 1100 '\xffround-1: hidden' >/dev/null; report ""; run rp-RAW-byte-prefix-omitted --rounds 1
lane rk; raw "$L" kama-shokunin 1100 'round-1: x\xff' >/dev/null; report ""; run rk-RAW-round-omitted-r2only --rounds 2 --report "2=$T/rk/fleet/.ufo/reports/round-1/kama.md"
lane z1; cm "$L" kama-shokunin 1100 $'\u200bround-1: hidden' >/dev/null; report ""; run z1-zwsp-prefix-omitted --rounds 1
lane z2; cm "$L" kama-shokunin 1100 $'\xc1\xb2ound-1: hidden' >/dev/null; report ""; run z2-overlong-prefix-omitted --rounds 1
lane q0; report ""; mkdir -p "$F/.ufo/reports/round-1"; : > "$F/.ufo/reports/round-1/"$'\xff'.md; git -C "$F" add -A; cm "$F" fleet 2100 "x" g >/dev/null; run q0-nonutf8-filename-default --rounds 1-
lane q1; report ""; mkdir -p "$F/.ufo/reports/round-1"; : > "$F/.ufo/reports/round-1/"$'\xff'.md; git -C "$F" add -A; cm "$F" fleet 2100 "x" g >/dev/null; git -C "$F" config core.quotePath false; run q1-nonutf8-filename-quotePath-false --rounds 1-
lane b1; report "" '\n## Notes\n\xff\n'; run b1-report-byte-outside-landed --rounds 1
lane b2; report "- also 1234567890abcdef1234\xff567890abcdef12345678\n"; run b2-report-byte-splits-fake-hash --rounds 1
lane b3; report "- also 1234567890abcdef1234\xc3\xa9567890abcdef12345678\n"; run b3-same-with-valid-e-acute --rounds 1
lane b4; report "- also 1234567890abcdef1234\xe2\x80\x8b567890abcdef12345678\n"; run b4-same-with-zwsp --rounds 1
lane d1; report ""; D=$T/d1/draft.md; printf '## Landed changes\n\n- %s\n\xff\n' "$LC" > "$D"; run d1-draft-byte --rounds 1 --report "1=$D"
echo T=$T
