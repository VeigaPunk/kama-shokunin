#!/usr/bin/env bash
# Part (c): prove on this host that `git status --porcelain -uall` does not list a
# git-ignored file while `--ignored` does. Fixture lives under $S and is removed.
set -eu
S=/fast/scratch/hyaku/kama-r72/SCT01ReceiptRecon
D=$(mktemp -d -p "$S" fixture.XXXXXX)
trap 'rm -rf -- "$D"' EXIT
echo "fixture=$D"

git -C "$D" init -q
TOP=$(git -C "$D" rev-parse --show-toplevel)
echo "toplevel=$TOP"
if [ "$TOP" != "$D" ]; then echo "ABORT: toplevel mismatch"; exit 3; fi

mkdir -p "$D/.ufo/waves/round-72" "$D/.ufo/waves/round-72-ignored-only"
printf 'ignored.out\nignored-only.out\n' > "$D/.gitignore"
printf 'tracked\n' > "$D/tracked.txt"
printf 'ignored\n' > "$D/.ufo/waves/round-72/ignored.out"
printf 'ignored\n' > "$D/.ufo/waves/round-72-ignored-only/ignored-only.out"
git -C "$D" add .gitignore tracked.txt
git -C "$D" -c user.name=fixture -c user.email=fixture@invalid commit -q -m 'fixture base'
printf 'untracked\n' > "$D/.ufo/waves/round-72/untracked.out"

echo "--- status --porcelain -uall"
git -C "$D" status --porcelain -uall; echo "rc=$?"
echo "--- status --porcelain -uall --ignored"
git -C "$D" status --porcelain -uall --ignored; echo "rc=$?"
echo "--- gate-arm form: status --porcelain -uall -- .ufo/waves/round-72"
OUT=$(git -C "$D" status --porcelain -uall -- .ufo/waves/round-72); rc=$?
printf '%s\n' "${OUT:-<empty>}"; echo "rc=$rc files=$(printf '%s\n' "$OUT" | grep -c . || true)"
echo "--- gate-arm form with --ignored"
OUT2=$(git -C "$D" status --porcelain -uall --ignored -- .ufo/waves/round-72); rc=$?
printf '%s\n' "${OUT2:-<empty>}"; echo "rc=$rc files=$(printf '%s\n' "$OUT2" | grep -c . || true)"
echo "--- ignored-only wave dir: gate-arm form (status --porcelain -uall -- .ufo/waves/round-72-ignored-only)"
OUT3=$(git -C "$D" status --porcelain -uall -- .ufo/waves/round-72-ignored-only); rc=$?
printf '%s\n' "${OUT3:-<empty>}"; echo "rc=$rc files=$(printf '%s\n' "$OUT3" | grep -c . || true)"
echo "--- ignored-only wave dir: with --ignored"
OUT4=$(git -C "$D" status --porcelain -uall --ignored -- .ufo/waves/round-72-ignored-only); rc=$?
printf '%s\n' "${OUT4:-<empty>}"; echo "rc=$rc files=$(printf '%s\n' "$OUT4" | grep -c . || true)"
echo "--- check-ignore verdict"
git -C "$D" check-ignore -v .ufo/waves/round-72/ignored.out; echo "rc=$?"
echo "--- check-ignore on a non-ignored path"
set +e
git -C "$D" check-ignore -q .ufo/waves/round-72/untracked.out; echo "rc=$?"
