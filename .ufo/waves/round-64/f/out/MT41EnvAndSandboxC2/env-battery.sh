#!/bin/bash
# Environment battery for the C2 counter at the measured tip.
# Each case runs the UNMODIFIED counter from the scratch clone, with a
# different caller environment, and records the one-line verdict.
set -u
S=/fast/scratch/hyaku/kama-r64/f/MT41EnvAndSandboxC2
D=$S/clone
TIP=23b3fdb1a925129a9961cf551f6d40bf251602cb
OUT=$S/out-env
mkdir -p $OUT

run_case() {
  name=$1; shift
  work=$S/work-env-$name
  rm -rf "$work"
  cd $D/tools
  env "$@" python3 round64-c2-counter.py --repo $D --tip $TIP --work "$work" \
      > $OUT/$name.out 2> $OUT/$name.err
  rc=$?
  echo "--- case=$name exit=$rc"
  cat $OUT/$name.out
  if [ -s $OUT/$name.err ]; then echo "  stderr:"; tail -3 $OUT/$name.err; fi
}

# 1. hostile caller env: proxy, python path/startup, git dir, git config count
run_case hostile \
  HTTP_PROXY=http://127.0.0.1:9 \
  HTTPS_PROXY=http://127.0.0.1:9 \
  http_proxy=http://127.0.0.1:9 \
  https_proxy=http://127.0.0.1:9 \
  NO_PROXY= \
  PYTHONPATH=/fast/scratch/hyaku/kama-r64/f/MT41EnvAndSandboxC2/fixtures/pypath \
  PYTHONSTARTUP=/fast/scratch/hyaku/kama-r64/f/MT41EnvAndSandboxC2/fixtures/pystartup.py \
  GIT_DIR=/fast/scratch/hyaku/kama-r64/f/MT41EnvAndSandboxC2/fixtures/gitdir \
  GIT_CONFIG_COUNT=1 \
  GIT_CONFIG_KEY_0=core.pager \
  GIT_CONFIG_VALUE_0=/bin/false \
  GIT_CONFIG_GLOBAL=/fast/scratch/hyaku/kama-r64/f/MT41EnvAndSandboxC2/fixtures/gitconfig \
  GIT_CONFIG_NOSYSTEM=1 \
  GIT_ASKPASS=/bin/false \
  GIT_TERMINAL_PROMPT=0 \
  LANG=C \
  LC_ALL=C

# 2. env -i (no environment at all)
work=$S/work-env-envi
rm -rf "$work"
cd $D/tools
env -i python3 round64-c2-counter.py --repo $D --tip $TIP --work "$work" \
    > $OUT/envi.out 2> $OUT/envi.err
echo "--- case=env-i exit=$?"
cat $OUT/envi.out
tail -3 $OUT/envi.err

# 3. env -i with only PATH/HOME (minimal but usable)
work=$S/work-env-envimin
rm -rf "$work"
cd $D/tools
env -i PATH=/usr/bin:/bin HOME="$HOME" python3 round64-c2-counter.py \
    --repo $D --tip $TIP --work "$work" > $OUT/envimin.out 2> $OUT/envimin.err
echo "--- case=env-i-min exit=$?"
cat $OUT/envimin.out
tail -3 $OUT/envimin.err

# 4. different locale
work=$S/work-env-locale
rm -rf "$work"
cd $D/tools
env LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 python3 round64-c2-counter.py \
    --repo $D --tip $TIP --work "$work" > $OUT/locale.out 2> $OUT/locale.err
echo "--- case=locale exit=$?"
cat $OUT/locale.out
tail -3 $OUT/locale.err
