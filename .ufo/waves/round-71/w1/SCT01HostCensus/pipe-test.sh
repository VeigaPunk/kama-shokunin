#!/usr/bin/env bash
set -u
S=/fast/scratch/hyaku/kama-r71/SCT01HostCensus
D=$(mktemp -d -p "$S" pipetest.XXXXXX)
out="$S/pipe-checkout.out"
: > "$out"
say() { printf '%s\n' "$*" >> "$out"; }
say "FIXTURE=$D"
git -C "$D" init -q >> "$out" 2>&1; say "INIT_EXIT=$?"
git -C "$D" config user.email probe@example.invalid
git -C "$D" config user.name probe
top=$(git -C "$D" rev-parse --show-toplevel); say "TOPLEVEL=$top"
if [ "$top" != "$D" ]; then say "TOPLEVEL_MISMATCH expected=$D got=$top"; exit 9; fi
say "TOPLEVEL_ASSERT=ok"
ft="$D/dir/out/c -l\` → 18\`|"
mkdir -p "$D/dir/out"
printf 'pipe-path-payload\n' > "$ft"
say "CREATED: $(ls -l "$D/dir/out" | sed -n '2p')"
say "CMD: git -C D add -- 'dir/out/c -l\` → 18\`|'; echo EXIT=\$?"
git -C "$D" add -- "dir/out/c -l\` → 18\`|" >> "$out" 2>&1; say "EXIT=$?"
say "CMD: git -C D commit -m pipe-path"
git -C "$D" commit -q -m 'pipe path' >> "$out" 2>&1; say "EXIT=$?"
say "CMD: git -C D ls-files -z | tr | od (tracked bytes)"
git -C "$D" ls-files -z | tr '\0' '\n' | od -c | sed -n '1,8p' >> "$out"
rm -f "$ft"
say "REMOVED_WORKTREE_COPY=yes"
say "CMD: git -C D checkout -- 'dir/out/c -l\` → 18\`|'; echo EXIT=\$?"
git -C "$D" checkout -- "dir/out/c -l\` → 18\`|" >> "$out" 2>&1; say "EXIT=$?"
if [ -f "$ft" ]; then say "RESTORED=yes PAYLOAD=$(cat "$ft")"; else say "RESTORED=no"; fi
say "CMD: git -C D status --porcelain"
git -C "$D" status --porcelain >> "$out" 2>&1; say "EXIT=$?"
echo "PIPE_TEST_EXIT=$?"
cat "$out"
