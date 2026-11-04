#!/usr/bin/env bash
set -u
S=/fast/scratch/hyaku/kama-r71/SCT01HostCensus
out="$S/census-raw.out"
: > "$out"
say() { printf '%s\n' "$*" >> "$out"; }
runcmd() { # label, command string evaluated by bash
  local label="$1"; shift
  say "## $label"
  say "CMD: $*"
  local tmp="$S/.cmd.out"
  : > "$tmp"
  bash -c "$*" >> "$tmp" 2>&1
  local rc=$?
  cat "$tmp" >> "$out"
  say "EXIT=$rc"
  rm -f "$tmp"
}

say "=== host identity ==="
runcmd "uname-a" 'uname -a'
runcmd "uname-s" 'uname -s'
runcmd "os-release" 'grep -E "^(NAME|VERSION_ID|PRETTY_NAME)=" /etc/os-release'

say "=== path tags (declared probe: test -e PATH) ==="
checkpath() { # tag path
  local tag="$1" path="$2"
  say "## $tag"
  say "CMD: test -e $path; echo EXIT=\$?"
  if [ -e "$path" ]; then
    say "EXIT=0"
    ls -ld "$path" >> "$out" 2>&1
    if [ -f "$path" ]; then
      file -b "$path" >> "$out" 2>&1
      sha256sum "$path" >> "$out" 2>&1
    fi
    if [ -d "$path" ]; then
      say "ENTRIES=$(find "$path" -mindepth 1 -maxdepth 1 | wc -l)"
      find "$path" -mindepth 1 -maxdepth 1 -printf '%y %p\n' 2>/dev/null | sort | sed -n '1,30p' >> "$out"
    fi
  else
    say "EXIT=1"
  fi
}

checkpath "omp-binary" "$HOME/.local/bin/omp"
checkpath "llama-b11755-install" "$HOME/.local/opt/llama-b11755"
checkpath "llama-server-link" "$HOME/.local/bin/llama-server"
checkpath "kama-cache-gguf" "$HOME/.cache/kama-shokunin"
checkpath "llama-b11755-archive" "$HOME/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz"
checkpath "qwen-coder-unit" "$HOME/.config/systemd/user/qwen-coder.service"
checkpath "opencode-json" "$HOME/.config/opencode/opencode.json"
checkpath "janitor-md" "$HOME/.config/opencode/agents/janitor.md"
checkpath "janitor-dir" "$HOME/.config/opencode/agents"
checkpath "ollama-v04011-install" "$HOME/.local/opt/ollama-v0.40.11"
checkpath "fixture-gguf-model" "$HOME/.cache/kama-shokunin/models/stories260K.gguf"

say "=== ufo-src (declared probe: env UFO_SRC) ==="
say "CMD: printenv UFO_SRC (empty output = unset); echo EXIT=\$?"
printf 'UFO_SRC=%s\n' "${UFO_SRC-<unset>}" >> "$out"
printenv UFO_SRC >> "$out" 2>&1
say "EXIT=$?"
say "CMD: command -v ufo; echo EXIT=\$?"
command -v ufo >> "$out" 2>&1
say "EXIT=$?"

say "=== python3-interpreter (declared probe: spawn kind = real run) ==="
say 'CMD: python3 -c "import sys"; echo EXIT=$?'
python3 -c "import sys" >> "$out" 2>&1
say "EXIT=$?"
say "CMD: command -v python3; type -a python3; python3 -VV"
command -v python3 >> "$out" 2>&1
type -a python3 >> "$out" 2>&1
python3 -VV >> "$out" 2>&1
say "EXIT=$?"
say 'CMD: python -c "import sys"; echo EXIT=$?'
python -c "import sys" >> "$out" 2>&1
say "EXIT=$?"

say "=== ss/flock absence prose claim ==="
say "CMD: command -v ss; echo EXIT=\$?"
command -v ss >> "$out" 2>&1
say "EXIT=$?"
say "CMD: command -v flock; echo EXIT=\$?"
command -v flock >> "$out" 2>&1
say "EXIT=$?"
say "CMD: ss -ltn | wc -l"
ss -ltn 2>&1 | wc -l >> "$out"
say "EXIT=$?"

say "=== qwen-coder-unit prose clause: systemd presence ==="
say "CMD: command -v systemctl; echo EXIT=\$?"
command -v systemctl >> "$out" 2>&1
say "EXIT=$?"
say "CMD: test -d $HOME/.config/systemd/user; echo EXIT=\$?"
test -d "$HOME/.config/systemd/user"; say "EXIT=$?"

say "=== opencode dir shape (read-only) ==="
say "CMD: ls -la $HOME/.config/opencode 2>&1; echo EXIT=\$?"
ls -la "$HOME/.config/opencode" >> "$out" 2>&1
say "EXIT=$?"

say "=== omp dir shape (read-only) ==="
say "CMD: ls -la $HOME/.omp 2>&1; echo EXIT=\$?"
ls -la "$HOME/.omp" >> "$out" 2>&1
say "EXIT=$?"
