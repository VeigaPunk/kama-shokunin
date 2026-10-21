#!/usr/bin/env bash
# RevProbeScript corrected fault grid for tools/report-landing-audit.py.
# Scratch only: fixtures live in fresh temp repos under /tmp; identity is pinned;
# every fixture step is checked and aborts with FIXTURE-ERROR (exit 3) on failure.
set -uo pipefail
AUDIT=${AUDIT:?set AUDIT=path/to/report-landing-audit.py}
BASE=/tmp/kama-r23/RevProbeScript
mkdir -p "$BASE"
T=$(mktemp -d "$BASE/fixed.XXXX")
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=fixture@example.invalid
export GIT_COMMITTER_NAME=fixture GIT_COMMITTER_EMAIL=fixture@example.invalid
die() { echo "FIXTURE-ERROR: $*" >&2; exit 3; }
mk() { git init -q -b master "$1" || die "init $1"; }
CM=
cmf() { # repo author time msg : commit what is staged, sets CM
  GIT_AUTHOR_NAME=$2 GIT_COMMITTER_NAME=$2 GIT_AUTHOR_DATE="@$3 +0000" \
    GIT_COMMITTER_DATE="@$3 +0000" git -C "$1" -c commit.gpgsign=false \
    commit -q -m "$4" || die "commit in $1: $4"
  CM=$(git -C "$1" rev-parse HEAD) || die "rev-parse in $1"
}
cm() { # repo author time subject [file] : append line, stage, commit, sets CM
  local f=${5:-f}
  echo "$4" >> "$1/$f"
  git -C "$1" add "$f" || die "add $f in $1"
  cmf "$1" "$2" "$3" "$4"
}
run() { # name : run auditor once, print exit code, traceback flag, verdict
  local name=$1
  python3 "$AUDIT" --lane-repo "$L" --fleet-repo "$F" --rounds 1 --no-errata \
    --json >"$T/$name.out" 2>"$T/$name.err"
  local rc=$? tb=no
  grep -q Traceback "$T/$name.err" && tb=yes
  printf '%-24s exit=%s traceback=%s replace_refs=%s\n' "$name" "$rc" "$tb" \
    "$(git -C "$L" replace -l | wc -l)"
  python3 - "$T/$name.out" "$T/$name.err" <<'EOF' 2>/dev/null || echo "   (no JSON verdict; stderr tail: $(tail -c 120 "$T/$name.err" | tr '\n' ' '))"
import json, sys
d = json.load(open(sys.argv[1]))
r = d["results"][0]
print("   status", d["summary"]["status"], "defects",
      [(x["kind"], x["token"][:12]) for x in r["defects"]],
      "required", r["required"], "cutoff", r["cutoff"])
EOF
}
base() { # name : lane LC at t=1000; fleet report committed at t=2000 listing LC
  L=$T/$1/lane; F=$T/$1/fleet; mk "$L"; mk "$F"
  cm "$L" kama-shokunin 1000 "round-1: work"; LC=$CM
  mkdir -p "$F/.ufo/reports/round-1"
  printf '## Landed changes\n\n- %s\n' "$LC" > "$F/.ufo/reports/round-1/kama.md"
  git -C "$F" add .ufo/reports/round-1/kama.md || die "add report"
  cmf "$F" fleet 2000 "round-1: report"
}
echo "T=$T"
echo "AUDIT=$AUDIT"

# control
base control; run control

# F1: lane logOutputEncoding=ISO-8859-1 + non-ASCII non-round subject
base f1; cm "$L" someone 1100 "note café"
git -C "$L" config i18n.logOutputEncoding ISO-8859-1 || die cfg
run f1-logenc

# F2: invalid UTF-8 bytes in the committed fleet report
base f2; printf '\xff\xfe bad\n' >> "$F/.ufo/reports/round-1/kama.md"
cm "$F" fleet 2100 "edit" .ufo/reports/round-1/kama.md; run f2-report-bytes

# F3: replace ref hides an omitted round commit (identity pinned for commit-tree)
base f3c; cm "$L" kama-shokunin 1200 "round-1: more"; run f3-control-no-replace
base f3; cm "$L" kama-shokunin 1200 "round-1: more"; X=$CM
Y=$(git -C "$L" commit-tree -p "$LC" -m "unrelated" "$X^{tree}") || die "commit-tree"
[ -n "$Y" ] || die "commit-tree produced no object"
git -C "$L" replace "$X" "$Y" || die "replace"
run f3-replace-omit

# F4: replace ref for a fabricated full hash cited in the Landed section (+ control)
FAKE=1234567890abcdef1234567890abcdef12345678
base f4c; printf -- '- also %s\n' "$FAKE" >> "$F/.ufo/reports/round-1/kama.md"
cm "$F" fleet 2100 "edit" .ufo/reports/round-1/kama.md; run f4-control-no-replace
base f4; printf -- '- also %s\n' "$FAKE" >> "$F/.ufo/reports/round-1/kama.md"
cm "$F" fleet 2100 "edit" .ufo/reports/round-1/kama.md
git -C "$L" update-ref "refs/replace/$FAKE" "$LC" || die "update-ref"
run f4-replace-fake

# F5: promisor lazy fetch executing repo-configured core.sshCommand (example.invalid only)
FAKE2=abcdefabcdefabcdefabcdefabcdefabcdefabcd
base f5c; printf -- '- also %s\n' "$FAKE2" >> "$F/.ufo/reports/round-1/kama.md"
cm "$F" fleet 2100 "edit" .ufo/reports/round-1/kama.md
git -C "$L" config extensions.partialClone origin && git -C "$L" config remote.origin.url ssh://example.invalid/x.git \
  && git -C "$L" config remote.origin.promisor true && git -C "$L" config core.sshCommand "false" || die cfg
run f5-control-ssh-false
base f5; printf -- '- also %s\n' "$FAKE2" >> "$F/.ufo/reports/round-1/kama.md"
cm "$F" fleet 2100 "edit" .ufo/reports/round-1/kama.md
M5=$T/f5/marker
git -C "$L" config extensions.partialClone origin && git -C "$L" config remote.origin.url ssh://example.invalid/x.git \
  && git -C "$L" config remote.origin.promisor true && git -C "$L" config core.sshCommand "touch $M5; false" || die cfg
run f5-lazyfetch; if [ -e "$M5" ]; then echo "   MARKER CREATED: repo-configured command executed"; else echo "   no marker"; fi

# F6: log.follow cutoff. Draft at old path (t=1000) renamed into place (t=2000);
# round commit X (t=1500) is omitted from the report, so it is required only if cutoff=2000.
f6() { # name fleet-log.follow-value-or-empty
  L=$T/$1/lane; F=$T/$1/fleet; mk "$L"; mk "$F"
  cm "$L" kama-shokunin 1000 "round-1: work"; LC=$CM
  mkdir -p "$F/old" "$F/.ufo/reports/round-1"
  printf '## Landed changes\n\n- %s\n' "$LC" > "$F/old/k.md"
  git -C "$F" add old/k.md || die "add draft"; cmf "$F" fleet 1000 "draft"
  git -C "$F" mv old/k.md .ufo/reports/round-1/kama.md || die "mv into place"
  cmf "$F" fleet 2000 "round-1: report renamed into place"
  cm "$L" kama-shokunin 1500 "round-1: more"
  if [ -n "$2" ]; then git -C "$F" config log.follow "$2" || die cfg; fi
  run "$1"
}
f6 f6-follow-unset ""
f6 f6-follow-true true

# F7 (extension, not in the L1 grid): repo-local log.showSignature runs gpg.program
base f7; SIG_TREE=$(git -C "$L" rev-parse "$LC^{tree}") || die tree
RAW=$(printf 'tree %s\nparent %s\nauthor fixture <fixture@example.invalid> 1300 +0000\ncommitter fixture <fixture@example.invalid> 1300 +0000\ngpgsig -----BEGIN PGP SIGNATURE-----\n fake\n -----END PGP SIGNATURE-----\n\nnote signed\n' "$SIG_TREE" "$LC")
S7=$(printf '%s' "$RAW" | git -C "$L" hash-object -t commit -w --stdin) || die "hash-object"
git -C "$L" update-ref refs/heads/master "$S7" || die "update-ref"
M7=$T/f7/marker
printf '#!/bin/sh\ntouch "%s"\nexit 1\n' "$M7" > "$T/f7/fakegpg" && chmod +x "$T/f7/fakegpg" || die fakegpg
git -C "$L" config gpg.program "$T/f7/fakegpg" && git -C "$L" config gpg.openpgp.program "$T/f7/fakegpg" \
  && git -C "$L" config log.showSignature true || die cfg
run f7-showsignature; if [ -e "$M7" ]; then echo "   MARKER CREATED: repo-configured gpg.program executed"; else echo "   no marker"; fi

echo "done"
