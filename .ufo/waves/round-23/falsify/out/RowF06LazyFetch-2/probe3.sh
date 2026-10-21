#!/bin/bash
# Round-3 probes on the same channel: config-name shapes that may evade the
# auditor's line-based detection regex remote\..+\.promisor while git still
# treats the remote as a promisor (and would lazy fetch).
set -eu
ROOT=/tmp/f06-hand
BASE_ENV="env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=a@x GIT_COMMITTER_NAME=fixture GIT_COMMITTER_EMAIL=a@x"
FAKE2=abcdefabcdefabcdefabcdefabcdefabcdefabcd
MARKER="$ROOT/probe3-ran"

mk() {
  D=$1
  rm -rf "$D"; $BASE_ENV git init -q -b master "$D"
  printf 'round-1: work\n' >> "$D/f"
  $BASE_ENV git -C "$D" add -- f
  $BASE_ENV GIT_AUTHOR_DATE="@1000 +0000" GIT_COMMITTER_DATE="@1000 +0000" \
    git -C "$D" -c commit.gpgsign=false commit -q -m 'round-1: work' \
    --author='kama-shokunin <a@x>'
  $BASE_ENV git -C "$D" config core.sshCommand "touch $MARKER; false"
}
probe() {
  D=$1
  rm -f "$MARKER"
  set +e
  timeout 10 $BASE_ENV git -C "$D" cat-file -e "$FAKE2" >/dev/null 2>&1
  RC=$?
  set -e
  echo "  probe $(basename "$D"): rc=$RC marker=$([ -e "$MARKER" ] && echo PRESENT || echo absent)"
  echo -n "  detected-by-regex: "
  python3 "$ROOT/detect.py" "$D"
}

# E1 empty remote name via config file
mk "$ROOT/e1"
cat >> "$ROOT/e1/.git/config" <<EOF
[remote ""]
	url = ssh://example.invalid/x.git
	promisor = true
EOF
echo "E1 config listing:"; $BASE_ENV git -C "$ROOT/e1" config --list --name-only | sed 's/^/  /'
echo "E1 remote names: [$($BASE_ENV git -C "$ROOT/e1" remote)]"
probe "$ROOT/e1"

# E2 literal newline inside quoted subsection in the config file
mk "$ROOT/e2"
python3 - "$ROOT/e2/.git/config" <<'PY'
import sys
open(sys.argv[1], "ab").write(
    b'[remote "a\nb"]\n\turl = ssh://example.invalid/x.git\n\tpromisor = true\n')
PY
echo "E2 config listing (od):"; $BASE_ENV git -C "$ROOT/e2" config --list --name-only | od -c | sed 's/^/  /'
echo "E2 remote names (od):"; $BASE_ENV git -C "$ROOT/e2" remote | od -c | sed 's/^/  /'
probe "$ROOT/e2"

# E3 name with a literal backslash-n (escape processed or not?)
mk "$ROOT/e3"
printf '[remote "a\\\\nb"]\n\turl = ssh://example.invalid/x.git\n\tpromisor = true\n' >> "$ROOT/e3/.git/config"
echo "E3 config listing:"; $BASE_ENV git -C "$ROOT/e3" config --list --name-only | sed 's/^/  /'
echo "E3 remote names: [$($BASE_ENV git -C "$ROOT/e3" remote)]"
probe "$ROOT/e3"
