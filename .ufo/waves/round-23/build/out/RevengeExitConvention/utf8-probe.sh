#!/usr/bin/env bash
# Independent replication of L1 faults F1/F2 against the HEAD (4fe9339) audit copy.
set -u
AUDIT=$1
T=$(mktemp -d /tmp/kama-r23/RevengeExitConvention/fx/run.XXXX)
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
mk() { git init -q -b master "$1"; }
cm() { local f=${5:-f}; echo "$4" >> "$1/$f"; git -C "$1" add "$f"
  GIT_AUTHOR_NAME=$2 GIT_COMMITTER_NAME=$2 GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_EMAIL=a@x \
  GIT_AUTHOR_DATE="@$3 +0000" GIT_COMMITTER_DATE="@$3 +0000" \
  git -C "$1" -c commit.gpgsign=false commit -q -m "$4"; git -C "$1" rev-parse HEAD; }
base() { L=$T/$1/lane; F=$T/$1/fleet; mk "$L"; mk "$F"
  LC=$(cm "$L" kama-shokunin 1000 "round-1: work"); mkdir -p "$F/.ufo/reports/round-1"
  printf '## Landed changes\n\n- %s\n' "$LC" > "$F/.ufo/reports/round-1/kama.md"
  cm "$F" fleet 2000 "round-1: report" .ufo/reports/round-1/kama.md >/dev/null; }
run() { python3 "$AUDIT" --lane-repo "$L" --fleet-repo "$F" --rounds 1 --no-errata --json >"$T/$1.out" 2>"$T/$1.err"; local rc=$?
  echo "$1 exit=$rc last_stderr_line=[$(tail -n1 "$T/$1.err")]"; }
base control; run control
base f1; cm "$L" someone 1100 "note café" >/dev/null; git -C "$L" config i18n.logOutputEncoding ISO-8859-1; run f1-logenc
base f2; printf '\xff\xfe bad\n' >> "$F/.ufo/reports/round-1/kama.md"; cm "$F" fleet 2100 "edit" .ufo/reports/round-1/kama.md >/dev/null; run f2-report-bytes
echo "T=$T"
