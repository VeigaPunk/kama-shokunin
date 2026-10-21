#!/usr/bin/env bash
# ExecOldGitRun, step 1 of 2: fetch official Arch Linux archive packages git
# 2.44.0-1 and 2.45.0-1, verify each detached signature against the local Arch
# keyring (throwaway --homedir), and extract them under /tmp. Nothing is
# installed system-wide; no pacman transaction is run.
set -euo pipefail
WORK=${WORK:-/tmp/kama-r23w2/ExecOldGitRun}
OUT=${OUT:-/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/falsify/out/ExecOldGitRun}
BASE=https://archive.archlinux.org/packages/g/git
KEYRING=/usr/share/pacman/keyrings/archlinux.gpg
PKGDIR="$WORK/pkgs"
mkdir -p "$PKGDIR" "$WORK/gnupg" "$OUT"
chmod 700 "$WORK/gnupg"

{
  echo "# host tool versions"
  zstd --version
  curl --version | sed -n 1p
  gpg --version | sed -n 1p
  strace -V | sed -n 1p
  python3 --version
  echo "LANG=${LANG:-unset}"
} > "$OUT/tools.txt" 2>&1

for v in 2.44.0 2.45.0; do
  f="git-$v-1-x86_64.pkg.tar.zst"
  [ -s "$PKGDIR/$f" ] || curl -fsSL --max-time 300 -o "$PKGDIR/$f" "$BASE/$f"
  [ -s "$PKGDIR/$f.sig" ] || curl -fsSL --max-time 300 -o "$PKGDIR/$f.sig" "$BASE/$f.sig"
done

gpg --homedir "$WORK/gnupg" --batch --quiet --import "$KEYRING"
for v in 2.44.0 2.45.0; do
  f="git-$v-1-x86_64.pkg.tar.zst"
  gpg --homedir "$WORK/gnupg" --batch --status-fd 1 --verify "$PKGDIR/$f.sig" "$PKGDIR/$f" > "$OUT/gpg-verify-$v.txt" 2>&1 || true
  grep -q '^\[GNUPG:\] GOODSIG' "$OUT/gpg-verify-$v.txt" || { echo "signature check failed: $f" >&2; exit 1; }
done

sha256sum "$PKGDIR/git-2.44.0-1-x86_64.pkg.tar.zst" "$PKGDIR/git-2.45.0-1-x86_64.pkg.tar.zst" > "$OUT/packages.sha256"

for v in 2.44.0 2.45.0; do
  f="git-$v-1-x86_64.pkg.tar.zst"
  d="$WORK/old/$v"
  if [ ! -x "$d/usr/bin/git" ]; then
    rm -rf "$d"
    mkdir -p "$d"
    zstd -dc "$PKGDIR/$f" | tar -x -C "$d"
  fi
  grep -E '^(pkgname|pkgver|builddate|packager) =' "$d/.PKGINFO" > "$OUT/pkginfo-$v.txt"
  ldd "$d/usr/bin/git" > "$OUT/ldd-$v.txt" || true
  { "$d/usr/bin/git" --version; "$d/usr/bin/git" --exec-path; } > "$OUT/old-git-$v.txt" 2>&1
done
echo "fetch-ok"
