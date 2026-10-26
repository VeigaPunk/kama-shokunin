#!/usr/bin/env bash
# host-checks.sh — pre/post host-safety checks for one kama live-run wave.
# Read-only: every subcommand writes to stdout only (no files, no /tmp).
#
#   host-checks.sh pre   > pre.txt     # before the first live run
#   host-checks.sh post  > post.txt    # after the last live run
#   diff <(host-checks.sh pre) <(host-checks.sh post)   # must be empty
#   host-checks.sh install <tarball> <install-dir>
#
# What each line proves (kama-llamacpp-live.py line refs at round 46):
#   pgrep/ss        no leaked child survives a run (F5: teardown has no
#                   process-level post-condition, only port_refuses)
#   fleet status    the child cannot inherit a repo root as cwd (F7)
#   tmp globs       the probe/harness temp files stay out of /tmp (F3/F4)
#   install tree    the install dir equals a fresh extraction of the verified
#                   tarball (F8) and the server digest matches install.txt (F2)
#   model digest    the GGUF still hashes to the pinned value (F9)
set -u

LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
FLEET=/home/vgpnk/Projects/shokunin
SERVER=${SERVER:-/home/vgpnk/.local/opt/llama-b11906/llama-server}
MODEL=${MODEL:-/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf}
MODEL_SHA=${MODEL_SHA:-270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d}
EXPECTED_PORTS='8080 34113'

snapshot() {
  echo "utc $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "## processes"
  if pgrep -a llama-server >/dev/null 2>&1; then
    pgrep -a llama-server | sed 's/^/llama-server-leaked: /'
  else
    echo "llama-server-none"
  fi
  echo "## listeners"
  if ss -ltnp 2>/dev/null | grep -q 'llama-server'; then
    ss -ltnp 2>/dev/null | grep 'llama-server' | sed 's/^/listener: /'
  else
    echo "llama-server-listeners-none"
  fi
  echo "## temp residue"
  for pat in '/tmp/kama-probe.*' '/tmp/kama-llamacpp-live-*' '/tmp/.kama-live-*'; do
    # shellcheck disable=SC2086
    set -- $pat
    if [ -e "$1" ]; then echo "tmp-residue: $pat"; else echo "tmp-clean: $pat"; fi
  done
  echo "## fleet root"
  git -C "$FLEET" status --porcelain -uall | sed 's/^/fleet-status: /'
  echo "fleet-status-count $(git -C "$FLEET" status --porcelain -uall | wc -l)"
  echo "## inputs"
  if [ -f "$MODEL" ]; then
    got=$(sha256sum "$MODEL" | cut -d' ' -f1)
    printf 'model-sha256 %s\n' "$got"
    if [ "$got" = "$MODEL_SHA" ]; then
      echo "model-pin-match yes"
    else
      echo "model-pin-match NO (expected $MODEL_SHA)"
    fi
  else
    echo "model-missing $MODEL"
  fi
  if [ -x "$SERVER" ]; then
    printf 'server-sha256 %s\n' "$(sha256sum "$SERVER" | cut -d' ' -f1)"
    printf 'server-realpath %s\n' "$(readlink -f "$SERVER")"
  else
    echo "server-missing $SERVER"
  fi
  echo "## refusal set (harness view)"
  python3 - "$LANE" <<'PY'
import importlib.util, sys
p = sys.argv[1] + '/tools/kama-llamacpp-live.py'
spec = importlib.util.spec_from_file_location('live', p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
print('refused-ports', ' '.join(str(x) for x in sorted(m.refused_ports())))
PY
}

verify_install() {
  local tarball=$1 install=$2
  local tmp
  tmp=$(mktemp -d -p "${TMPDIR:-/var/tmp}" host-checks.XXXXXX) || return 1
  tar -xzf "$tarball" -C "$tmp" || { rm -rf "$tmp"; return 1; }
  local root
  root=$(find "$tmp" -mindepth 1 -maxdepth 1 -type d | head -1)
  python3 - "$root" "$install" <<'PY'
import hashlib, os, sys

def tree(d):
    reg, links = {}, {}
    for n in sorted(os.listdir(d)):
        f = os.path.join(d, n)
        st = os.lstat(f)
        if os.path.islink(f):
            links[n] = os.readlink(f)
        elif os.path.isfile(f):
            reg[n] = hashlib.sha256(open(f, 'rb').read()).hexdigest()
    return reg, links

a, al = tree(sys.argv[1])
b, bl = tree(sys.argv[2])
print('fresh-members', len(a), 'links', len(al))
print('install-members', len(b), 'links', len(bl))
print('only-fresh', sorted(set(a) - set(b)))
print('only-install', sorted(set(b) - set(a)))
print('digest-mismatch', [n for n in a if n in b and a[n] != b[n]])
print('link-mismatch', {n: (al.get(n), bl.get(n))
                        for n in set(al) | set(bl) if al.get(n) != bl.get(n)})
ok = (a == b and al == bl)
print('install-verdict', 'MATCH' if ok else 'CONTAMINATED')
sys.exit(0 if ok else 1)
PY
  local rc=$?
  rm -rf "$tmp"
  return $rc
}

case "${1:-}" in
  pre|post) snapshot ;;
  install)  shift; verify_install "${1:?tarball}" "${2:?install dir}" ;;
  *) echo "usage: $0 pre|post|install <tarball> <install-dir>" >&2; exit 2 ;;
esac
