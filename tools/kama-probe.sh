#!/usr/bin/env bash
# kama-probe.sh — loopback model-endpoint probe + consumer-registry reconciler.
#
# Domain: local model serving & endpoint health (kama-shokunin).
# Answers exactly one question: "is the thing at this baseURL the model this config
# believes it is, right now" — never "is the model good" (kengaku) or "is the request
# safe" (kagi).
#
# Read-only. Probes 127.0.0.1 only (--noproxy '*'); never touches a consumer config.
# Writes only under ${KAMA_PROBE_TMPDIR:-/tmp}/kama-probe.XXXXXX (removed on exit).
# Deterministic: no timestamps, no ordering by hash; output is byte-stable for
# identical live state.
#
# Subcommands:
#   listeners   enumerate loopback TCP listeners (ss -ltn) and classify each
#   consumers   resolve each registry consumer's declared baseURL FROM ITS OWN FILE
#               (never from the TSV text) and report declared-vs-actual
#   check       reconcile registry entries against live classification (exit gate)
#
# Flags (all subcommands): --json  --port N  --expect ID  --id KEY  --registry PATH
#                          --timeout S  --connect-timeout S  --help
#
# Verdict vocabulary (exact strings):
#   MODEL_OK MODEL_MISMATCH FOREIGN_SERVICE UNAUTHORIZED_SERVICE DEAD NOT_HTTP
#
# Exit codes: 0 every declared consumer reconciles | 2 at least one drift
#             1 probe error (bad arg, missing dep, unreadable registry) — never a verdict
#
# Served-id rules (contract v2):
#   extraction precedence, first non-empty wins:
#     data[].id -> models[].id -> models[].name -> models[].model -> top-level id
#   both served and expected ids are NORMALISED before comparison: drop the directory
#   (basename) then strip ONE trailing ".gguf"; comparison is case-sensitive.
#   If normalisation leaves either side empty -> MODEL_MISMATCH, reason unresolvable-id.
#
# Deps: ss, curl, coreutils. python3 optional (exact JSON-pointer resolution and
# exact served-id extraction; grep fallbacks used when absent).
set -euo pipefail
umask 077

VOCAB="MODEL_OK MODEL_MISMATCH FOREIGN_SERVICE UNAUTHORIZED_SERVICE DEAD NOT_HTTP"

SELF_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd -- "$SELF_DIR/.." && pwd)
REGISTRY_DEFAULT="$REPO_ROOT/registry/endpoint-consumers.tsv"

TIMEOUT=5
CONNECT_TIMEOUT=2
JSON_OUT=0
OPT_PORT=""
OPT_EXPECT=""
OPT_ID=""
OPT_REGISTRY="$REGISTRY_DEFAULT"
SUBCOMMAND=""

HAVE_PY=0
command -v python3 >/dev/null 2>&1 && HAVE_PY=1

TMP_ROOT=""
F_RC=0 F_CODE=000 F_CT="" F_SIZE=0 F_SERVER="" F_ERRMSG=""
FBODY="" FHDR="" FERR=""
C_VERDICT='' C_SERVED='-' C_EVIDENCE='' C_REASON=''

warn() { printf '[kama-probe] %s\n' "$*" >&2; }
die()  { printf 'kama-probe: %s\n' "$*" >&2; exit 1; }

cleanup() { [ -n "$TMP_ROOT" ] && [ -d "$TMP_ROOT" ] && rm -rf -- "$TMP_ROOT"; return 0; }
trap cleanup EXIT INT TERM

usage() {
  cat <<'EOF'
usage: kama-probe.sh <listeners|consumers|check> [flags]

  listeners            enumerate loopback TCP listeners and classify each
  consumers            resolve each registry consumer's baseURL from its own file
  check                reconcile registry entries against live classification

flags:
  --json               emit JSON on stdout (diagnostics stay on stderr)
  --port N             probe only port N (single-port mode; pair with --expect for matrices)
  --expect ID          expected model id for --port mode ("*" or "-" = any)
  --id KEY             row id to label --port mode with (default cli-override)
  --registry PATH      registry TSV to use (default registry/endpoint-consumers.tsv)
  --timeout S          per-request curl --max-time in seconds (default 5)
  --connect-timeout S  per-request curl --connect-timeout in seconds (default 2)
  --help               this text

verdicts: MODEL_OK MODEL_MISMATCH FOREIGN_SERVICE UNAUTHORIZED_SERVICE DEAD NOT_HTTP
exit: 0 reconciled | 2 drift | 1 probe error
EOF
}

parse_args() {
  while [ $# -gt 0 ]; do
    case "$1" in
      listeners|consumers|check) [ -z "$SUBCOMMAND" ] && SUBCOMMAND=$1 || die "duplicate subcommand: $1" ;;
      --json) JSON_OUT=1 ;;
      --port) shift; [ $# -gt 0 ] || die "--port needs a value"; OPT_PORT=$1 ;;
      --port=*) OPT_PORT=${1#*=} ;;
      --expect) shift; [ $# -gt 0 ] || die "--expect needs a value"; OPT_EXPECT=$1 ;;
      --expect=*) OPT_EXPECT=${1#*=} ;;
      --id) shift; [ $# -gt 0 ] || die "--id needs a value"; OPT_ID=$1 ;;
      --id=*) OPT_ID=${1#*=} ;;
      --registry) shift; [ $# -gt 0 ] || die "--registry needs a value"; OPT_REGISTRY=$1 ;;
      --registry=*) OPT_REGISTRY=${1#*=} ;;
      --timeout) shift; [ $# -gt 0 ] || die "--timeout needs a value"; TIMEOUT=$1 ;;
      --timeout=*) TIMEOUT=${1#*=} ;;
      --connect-timeout) shift; [ $# -gt 0 ] || die "--connect-timeout needs a value"; CONNECT_TIMEOUT=$1 ;;
      --connect-timeout=*) CONNECT_TIMEOUT=${1#*=} ;;
      --help|-h) usage; exit 0 ;;
      *) die "unknown argument: $1 (see --help)" ;;
    esac
    shift
  done
  [ -n "$SUBCOMMAND" ] || { usage >&2; exit 1; }
  local v
  for v in "$TIMEOUT" "$CONNECT_TIMEOUT"; do
    case "$v" in ''|*[!0-9]*) die "timeouts must be positive integers" ;; esac
    [ "$v" -ge 1 ] || die "timeouts must be >= 1"
  done
  if [ -n "$OPT_PORT" ]; then
    case "$OPT_PORT" in *[!0-9]*|'') die "--port must be a numeric port" ;; esac
    { [ "$OPT_PORT" -ge 1 ] && [ "$OPT_PORT" -le 65535 ]; } || die "--port out of range: $OPT_PORT"
  fi
  if [ -n "$OPT_EXPECT" ] && [ -z "$OPT_PORT" ]; then
    die "--expect is only meaningful with --port (matrix mode)"
  fi
}

# ---------------------------------------------------------------- json helpers
jstr() { # $1 -> JSON string literal
  local s=${1-}
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}
  s=${s//$'\n'/\\n}
  s=${s//$'\r'/\\r}
  printf '"%s"' "$s"
}

emit_json() { # $1 = JSON text; validated/normalised when python3 is present
  if [ "$HAVE_PY" -eq 1 ]; then
    if ! printf '%s\n' "$1" | python3 -c 'import json,sys; print(json.dumps(json.load(sys.stdin), indent=2))'; then
      die "internal error: generated JSON failed to parse (this is a probe bug)"
    fi
  else
    printf '%s\n' "$1"
  fi
}

json_array() { # rows on argv, each already a JSON object -> array body (no trailing comma)
  local out='' first=1 r
  for r in "$@"; do
    if [ "$first" -eq 1 ]; then out=$r; first=0; else out="$out,"$'\n'"$r"; fi
  done
  printf '%s' "$out"
}

# ---------------------------------------------------------------- table render
print_table() { # rows on stdin, tab-separated; first row is the header
  local -a rows=() widths=()
  local line
  while IFS= read -r line; do
    [ -n "$line" ] && rows+=("$line")
  done
  [ ${#rows[@]} -eq 0 ] && return 0

  local row ncol=0 i
  for row in "${rows[@]}"; do
    local -a c=()
    IFS=$'\t' read -r -a c <<< "$row"
    for ((i=0; i<${#c[@]}; i++)); do
      local L=${#c[i]}
      [ "$L" -gt "${widths[i]:-0}" ] && widths[i]=$L
    done
    [ ${#c[@]} -gt "$ncol" ] && ncol=${#c[@]}
  done

  local out pad
  for row in "${rows[@]}"; do
    local -a c=()
    IFS=$'\t' read -r -a c <<< "$row"
    out=""
    for ((i=0; i<ncol; i++)); do
      if [ "$i" -eq $((ncol-1)) ]; then
        out+="${c[i]:-}"
      else
        printf -v pad '%-*s' "${widths[i]:-0}" "${c[i]:-}"
        out+="$pad | "
      fi
    done
    printf '%s\n' "$out"
  done
}

# ---------------------------------------------------------------- listeners
declare -a SS_LINES=()
declare -A OWNER=()

load_listeners() {
  local line
  SS_LINES=()
  while IFS= read -r line; do
    [ -n "$line" ] && SS_LINES+=("$line")
  done < <(ss -ltnpH 2>/dev/null || ss -ltnH 2>/dev/null || true)

  local st rq sq localaddr peer rest name pid port
  for line in "${SS_LINES[@]}"; do
    # shellcheck disable=SC2086,SC2034
    read -r st rq sq localaddr peer rest <<< "$line"
    [ -n "${localaddr:-}" ] || continue
    port=${localaddr##*:}
    case "$port" in *[!0-9]*|'') continue ;; esac
    rest=${rest:-}
    if [ -n "$rest" ]; then
      name=$(sed -E 's/.*users:\(\(\"([^\"]+)\".*/\1/' <<< "$rest")
      pid=$(sed -E 's/.*pid=([0-9]+).*/\1/' <<< "$rest")
      if [ "$name" != "$rest" ] && [ "$pid" != "$rest" ] && [ -z "${OWNER[$port]:-}" ]; then
        OWNER[$port]="$name(pid=$pid)"
      fi
    fi
    [ -n "${OWNER[$port]:-}" ] || OWNER[$port]="-"
  done
}

# -> sorted unique "port<TAB>scope" lines
loopback_ports() {
  local line st rq sq localaddr peer rest addr port scope
  for line in "${SS_LINES[@]}"; do
    # shellcheck disable=SC2086,SC2034
    read -r st rq sq localaddr peer rest <<< "$line"
    [ -n "${localaddr:-}" ] || continue
    addr=${localaddr%:*}
    port=${localaddr##*:}
    case "$port" in *[!0-9]*|'') continue ;; esac
    scope=""
    case "$addr" in
      127.*|"[::1]"|"::1") scope=loopback ;;
      0.0.0.0|"[::]"|"::"|"*") scope=wildcard ;;
    esac
    [ -n "$scope" ] && printf '%s\t%s\n' "$port" "$scope"
  done | sort -n -u -k1,1
}

# ---------------------------------------------------------------- fetch
# shellcheck disable=SC2034
fetch() { # $1 port, $2 path, $3 tag -> sets F_*
  local port=$1 path=$2 tag=$3
  FBODY="$TMP_ROOT/$tag.body"
  FHDR="$TMP_ROOT/$tag.hdr"
  FERR="$TMP_ROOT/$tag.err"
  local w rc=0
  w=$(curl -sS --noproxy '*' --connect-timeout "$CONNECT_TIMEOUT" --max-time "$TIMEOUT" \
        -o "$FBODY" -D "$FHDR" \
        -w '%{http_code}|%{content_type}|%{size_download}' \
        "http://127.0.0.1:$port$path" 2>"$FERR") || rc=$?
  F_RC=$rc
  F_CODE=${w%%|*}
  w=${w#*|}
  F_CT=${w%%|*}
  F_SIZE=${w##*|}
  F_SERVER=""
  if [ -f "$FHDR" ]; then
    F_SERVER=$(grep -i '^server:' "$FHDR" 2>/dev/null | head -n1 | sed -E 's/^[Ss]erver:[[:space:]]*//; s/\r$//' || true)
  fi
  F_ERRMSG=""
  if [ -s "$FERR" ]; then
    F_ERRMSG=$(head -n1 "$FERR" | sed -E 's/^curl: \([0-9]+\) //' || true)
  fi
}

# A foreign service can answer 200 on a non-model path (jvb's /metrics on 8080 returns
# openmetrics). Recording it shows why a status-code-only liveness check false-passes.
metrics_trap() { # $1 port -> "" or "; GET /metrics -> ... (status-only liveness would false-pass)"
  local m
  m=$(probe_short "$1" "/metrics")
  case "$m" in
    200\|*) printf '; GET /metrics -> %s (status-only liveness would false-pass)' "$m" ;;
    *) printf '' ;;
  esac
}

probe_short() { # $1 port, $2 path -> "code|ct" or "err-<rc>"
  local port=$1 path=$2 rc=0 w
  w=$(curl -sS --noproxy '*' --connect-timeout "$CONNECT_TIMEOUT" --max-time "$TIMEOUT" \
        -o /dev/null -w '%{http_code}|%{content_type}' \
        "http://127.0.0.1:$port$path" 2>/dev/null) || rc=$?
  if [ "$rc" -eq 0 ]; then printf '%s' "$w"; else printf 'err-%s' "$rc"; fi
}

# ---------------------------------------------------------------- model ids
# extraction precedence, first non-empty group wins:
#   data[].id -> models[].id -> models[].name -> models[].model -> top-level id
served_ids() { # $1 body -> one id per line
  local body=$1
  if [ "$HAVE_PY" -eq 1 ]; then
    python3 - "$body" <<'PY' 2>/dev/null || true
import json, sys
try:
    doc = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(0)
if not isinstance(doc, dict):
    sys.exit(0)

def group(seq, key):
    out = []
    if isinstance(seq, list):
        for item in seq:
            if isinstance(item, dict):
                v = item.get(key)
                if isinstance(v, str) and v:
                    out.append(v)
    return out

groups = [
    group(doc.get("data"), "id"),
    group(doc.get("models"), "id"),
    group(doc.get("models"), "name"),
    group(doc.get("models"), "model"),
    [doc["id"]] if isinstance(doc.get("id"), str) and doc.get("id") else [],
]
for g in groups:
    if g:
        print("\n".join(dict.fromkeys(g)))
        break
PY
    return 0
  fi
  # grep fallback: approximate the same precedence ("id" before "model"/"name")
  local out
  out=$({ grep -oE '"id"[[:space:]]*:[[:space:]]*"[^"]*"' "$body" 2>/dev/null || true; } | sed -E 's/.*:[[:space:]]*"//; s/"$//' || true)
  [ -n "$out" ] && { printf '%s\n' "$out"; return 0; }
  { grep -oE '"model"[[:space:]]*:[[:space:]]*"[^"]*"' "$body" 2>/dev/null || true; } |
    sed -E 's/.*:[[:space:]]*"//; s/"$//' || true
}

# drop directory, strip ONE trailing .gguf
normalize_id() { local s=${1-}; s=${s##*/}; s=${s%.gguf}; printf '%s' "$s"; }

# $1 newline-joined served ids, $2 expected id -> 0 match, 1 mismatch, 2 unresolvable
model_matches() {
  local served=$1 expected=$2
  local exp_n; exp_n=$(normalize_id "$expected")
  [ -n "$exp_n" ] || return 2
  local s sn found=0
  while IFS= read -r s; do
    [ -n "$s" ] || continue
    sn=$(normalize_id "$s")
    [ -n "$sn" ] || continue
    found=1
    [ "$sn" = "$exp_n" ] && return 0
  done <<< "$served"
  [ "$found" -eq 0 ] && return 2
  return 1
}

# A model array must be PRESENT for MODEL_OK. v3: a status code or a `Server: llama.cpp`
# header is never proof on its own.
body_has_model_array() { # $1 body -> 0 when data[] or models[] is present
  local body=$1
  if [ "$HAVE_PY" -eq 1 ]; then
    python3 - "$body" <<'PY' 2>/dev/null
import json, sys
try:
    doc = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(1)
if not isinstance(doc, dict):
    sys.exit(1)
for key in ("data", "models"):
    if isinstance(doc.get(key), list):
        sys.exit(0)
sys.exit(1)
PY
    return $?
  fi
  grep -qE '"(data|models)"[[:space:]]*:[[:space:]]*\[' "$body" 2>/dev/null
}

# ---------------------------------------------------------------- classify
# shellcheck disable=SC2034
classify() { # $1 port, $2 expected -> sets C_VERDICT C_SERVED C_EVIDENCE C_REASON
  local port=$1 expected=${2:-}
  C_VERDICT='' C_SERVED='-' C_EVIDENCE='' C_REASON=''
  fetch "$port" "/v1/models" "m$port"

  local base="GET /v1/models -> $F_CODE"
  [ -n "$F_CT" ] && base="$base ${F_CT}"
  [ -n "$F_SERVER" ] && base="$base (Server: $F_SERVER)"

  case "$F_RC" in
    0) : ;;
    6|7)
      C_VERDICT=DEAD
      C_REASON=$([ "$F_RC" = 7 ] && echo connection-refused || echo dns-failure)
      C_EVIDENCE="rc=$F_RC ${F_ERRMSG:-connect failed}; $base"
      return 0 ;;
    28)
      C_VERDICT=DEAD
      C_REASON=timeout
      C_EVIDENCE="rc=28 timeout (connect=${CONNECT_TIMEOUT}s max=${TIMEOUT}s); $base"
      return 0 ;;
    52)
      C_VERDICT=NOT_HTTP
      C_REASON=empty-reply
      C_EVIDENCE="rc=52 empty reply on a TCP-accepted port; $base"
      return 0 ;;
    56)
      C_VERDICT=NOT_HTTP
      C_REASON=connection-reset
      C_EVIDENCE="rc=56 ${F_ERRMSG:-connection reset}; $base"
      return 0 ;;
    1|2|92)
      C_VERDICT=NOT_HTTP
      C_REASON=no-http-response
      C_EVIDENCE="rc=$F_RC ${F_ERRMSG:-no usable HTTP response}; $base"
      return 0 ;;
    *)
      C_VERDICT=NOT_HTTP
      C_REASON=no-http-response
      C_EVIDENCE="rc=$F_RC ${F_ERRMSG:-no HTTP response}; $base"
      return 0 ;;
  esac

  case "$F_CODE" in
    401) C_VERDICT=UNAUTHORIZED_SERVICE; C_REASON=http-401 ;;
    403) C_VERDICT=UNAUTHORIZED_SERVICE; C_REASON=http-403 ;;
  esac
  if [ -n "$C_VERDICT" ]; then
    C_EVIDENCE="$base; $(probe_short "$port" "/") @ /"
    return 0
  fi

  local is2=0 ishtml=0 has_models=0
  case "$F_CODE" in 2*) is2=1 ;; esac
  # HTML at ANY status: header, or a body sniff (v3 rule 4)
  case "$F_CT" in *html*) ishtml=1 ;; esac
  if [ "$ishtml" -eq 0 ] && [ -s "$FBODY" ]; then
    case "$(head -c 64 "$FBODY" | tr -d '[:space:]' | tr '[:upper:]' '[:lower:]')" in
      '<html'*|'<!doctype'*'html'*) ishtml=1 ;;
    esac
  fi
  # MODEL_OK requires a model array; status code / Server header alone is not proof (v3)
  if [ -s "$FBODY" ] && body_has_model_array "$FBODY"; then has_models=1; fi

  if [ "$is2" -eq 1 ] && [ "$has_models" -eq 1 ]; then
    local ids
    ids=$(served_ids "$FBODY")
    C_SERVED=$(printf '%s' "$ids" | tr '\n' ',')
    C_SERVED=${C_SERVED%,}
    [ -n "$C_SERVED" ] || C_SERVED='-'
    local runtime="other"
    [ "$F_SERVER" = "llama.cpp" ] && runtime="llama.cpp"
    case "$expected" in
      ''|'*'|'-')
        C_VERDICT=MODEL_OK; C_REASON='expected-wildcard' ;;
      *)
        local mrc=0
        model_matches "$ids" "$expected" || mrc=$?
        case "$mrc" in
          0) C_VERDICT=MODEL_OK; C_REASON=matched ;;
          2) C_VERDICT=MODEL_MISMATCH; C_REASON=unresolvable-id ;;
          *) C_VERDICT=MODEL_MISMATCH; C_REASON='served-id-mismatch' ;;
        esac ;;
    esac
    local ev="$base (runtime=$runtime; expected=${expected:--}; reason=$C_REASON)"
    local h; h=$(probe_short "$port" "/health")
    case "$h" in 200\|*json*) ev="$ev; GET /health -> $h" ;; esac
    C_EVIDENCE="$ev"
    return 0
  fi

  if [ "$ishtml" -eq 1 ]; then
    C_VERDICT=FOREIGN_SERVICE
    C_REASON=html-non-model
    C_EVIDENCE="$base; $(probe_short "$port" "/") @ /$(metrics_trap "$port")"
    return 0
  fi

  C_VERDICT=FOREIGN_SERVICE
  if [ "$is2" -eq 1 ]; then
    case "$F_CT" in
      *json*) C_REASON=schema-unrecognized ;;
      *)      C_REASON=non-model-2xx ;;
    esac
    C_EVIDENCE="$base (2xx service with no recognisable model array); $(probe_short "$port" "/") @ /$(metrics_trap "$port")"
  else
    C_REASON=non-2xx-non-model-http
    C_EVIDENCE="$base (non-2xx HTTP from a non-model service); $(probe_short "$port" "/") @ /$(metrics_trap "$port")"
  fi
  return 0
}

# ---------------------------------------------------------------- resolve
expand_path() { # $1 -> ~ expanded, relative paths anchored at the repo root
  local p=$1
  # shellcheck disable=SC2088  # the quoted '~' is a literal prefix we substitute ourselves
  case "$p" in
    "~"|"~/"*) p="$HOME${p#\~}" ;;
  esac
  case "$p" in
    /*) printf '%s' "$p" ;;
    *) printf '%s' "$REPO_ROOT/$p" ;;
  esac
}

resolve_json_pointer() { # $1 file, $2 pointer -> value on stdout
  local file=$1 ptr=$2
  if [ "$HAVE_PY" -eq 1 ]; then
    python3 - "$file" "$ptr" <<'PY'
import json, sys
doc = json.load(open(sys.argv[1]))
cur = doc
for tok in sys.argv[2].split('/'):
    if tok == '':
        continue
    tok = tok.replace('~1', '/').replace('~0', '~')
    cur = cur[int(tok)] if isinstance(cur, list) else cur[tok]
print(cur if isinstance(cur, str) else json.dumps(cur))
PY
    return 0
  fi
  # leaf-key fallback: first "<leaf>": "<value>" occurrence
  local leaf=${2##*/}
  grep -oE "\"$leaf\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" "$file" 2>/dev/null | head -n1 |
    sed -E 's/.*:[[:space:]]*"//; s/"$//' || true
}

# -> "<resolved>|<kind>"; kind = url | port:<n> | raw | empty | error
#    raw = the resolver matched something that is neither a URL nor a port
#    (the baseURL is then inherited from the provider named in the file)
resolve_spec() { # $1 consumer path, $2 resolver spec
  local file=$1 spec=$2 raw rc=0
  case "$spec" in
    json:*) raw=$(resolve_json_pointer "$file" "${spec#json:}") || rc=$? ;;
    grep:*) raw=$(grep -a -oE -m1 -e "${spec#grep:}" "$file" 2>/dev/null) || rc=$? ;;
    *)      raw=$(grep -a -oE -m1 -e "$spec" "$file" 2>/dev/null) || rc=$? ;;
  esac
  [ "$rc" -ne 0 ] && { printf '|error'; return 0; }
  raw=${raw%%$'\n'*}
  if [[ $raw =~ https?://[^\"\ ]+ ]]; then
    local url=${BASH_REMATCH[0]}
    url=${url%%/}
    printf '%s|url' "$url"
    return 0
  fi
  # Port synthesis only from an EXPLICIT port marker. A bare digit run must never be
  # read as a port: a model id like "Qwen3-Coder-30B-A3B" would otherwise resolve to
  # port 30 and report a false DEAD.
  local pnum=''
  if [[ $raw =~ port[[:space:]]*=[[:space:]]*([0-9]{2,5})([^0-9A-Za-z]|$) ]]; then
    pnum=${BASH_REMATCH[1]}
  elif [[ $raw =~ (--port|-p)[[:space:]]+([0-9]{2,5})([^0-9A-Za-z]|$) ]]; then
    pnum=${BASH_REMATCH[2]}
  elif [[ $raw =~ :([0-9]{2,5})([^0-9A-Za-z]|$) ]]; then
    pnum=${BASH_REMATCH[1]}
  fi
  if [ -n "$pnum" ]; then
    printf 'http://127.0.0.1:%s/v1|port:%s' "$pnum" "$pnum"
    return 0
  fi
  if [ -n "$raw" ]; then printf '%s|raw' "$raw"; else printf '|empty'; fi
}

url_port() {
  local u=${1#*://}
  u=${u%%/*}
  case "$u" in *:*) printf '%s' "${u##*:}" ;; *) printf '80' ;; esac
}

url_host() {
  local u=${1#*://}
  u=${u%%/*}
  case "$u" in *:*) printf '%s' "${u%:*}" ;; *) printf '%s' "$u" ;; esac
}

# ---------------------------------------------------------------- registry read
declare -a REG_IDS=() REG_PATHS=() REG_SPECS=() REG_DECLARED=() REG_EXPECT=() REG_NOTES=()
REG_ROWS=0

read_registry() { # $1 path
  local path=$1
  [ -f "$path" ] || die "registry not found: $path"
  [ -r "$path" ] || die "registry not readable: $path"
  local id cpath spec declared expected notes lineno=0
  REG_IDS=() REG_PATHS=() REG_SPECS=() REG_DECLARED=() REG_EXPECT=() REG_NOTES=()
  REG_ROWS=0
  while IFS=$'\t' read -r id cpath spec declared expected notes || [ -n "${id:-}" ]; do
    lineno=$((lineno+1))
    case "${id:-}" in ''|'#'*) continue ;; esac
    [ "$id" = "id" ] && continue   # header row
    if [ -z "${cpath:-}" ] || [ -z "${spec:-}" ] || [ -z "${declared:-}" ]; then
      warn "registry line $lineno: malformed (id, consumer_path, resolver, declared_baseurl required) — skipped"
      continue
    fi
    REG_IDS+=("$id"); REG_PATHS+=("$cpath"); REG_SPECS+=("$spec")
    REG_DECLARED+=("$declared"); REG_EXPECT+=("${expected:--}"); REG_NOTES+=("${notes:-}")
    REG_ROWS=$((REG_ROWS+1))
  done < "$path"
  [ "$REG_ROWS" -gt 0 ] || die "registry has no usable rows: $path"
}

# ---------------------------------------------------------------- subcommands
cmd_listeners() {
  local -a ports=() scopes=()
  local port scope
  if [ -n "$OPT_PORT" ]; then
    ports=("$OPT_PORT"); scopes=("override")
  else
    while IFS=$'\t' read -r port scope; do
      [ -n "${port:-}" ] && { ports+=("$port"); scopes+=("$scope"); }
    done < <(loopback_ports)
  fi

  local -a json_rows=() table=()
  table+=("$(printf 'port\tbind\towner\tverdict\treason\tserved_model\tevidence')")
  local i n_model=0 n_dead=0 n_foreign=0 n_nothttp=0 n_unauth=0
  for ((i=0; i<${#ports[@]}; i++)); do
    port=${ports[i]}
    classify "$port" "${OPT_EXPECT:-}"
    case "$C_VERDICT" in
      MODEL_OK|MODEL_MISMATCH) n_model=$((n_model+1)) ;;
      DEAD) n_dead=$((n_dead+1)) ;;
      FOREIGN_SERVICE) n_foreign=$((n_foreign+1)) ;;
      NOT_HTTP) n_nothttp=$((n_nothttp+1)) ;;
      UNAUTHORIZED_SERVICE) n_unauth=$((n_unauth+1)) ;;
    esac
    table+=("$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s' \
      "$port" "${scopes[i]}" "${OWNER[$port]:--}" "$C_VERDICT" "$C_REASON" "$C_SERVED" "$C_EVIDENCE")")
    json_rows+=("$(printf '    {"port":%s,"bind":%s,"owner":%s,"verdict":%s,"reason":%s,"served_model":%s,"evidence":%s}' \
      "$port" "$(jstr "${scopes[i]}")" "$(jstr "${OWNER[$port]:--}")" \
      "$(jstr "$C_VERDICT")" "$(jstr "$C_REASON")" "$(jstr "$C_SERVED")" "$(jstr "$C_EVIDENCE")")")
  done

  if [ "$JSON_OUT" -eq 1 ]; then
    emit_json "$(printf '{\n  "schema": "kama-probe/v1",\n  "subcommand": "listeners",\n  "verdict_vocabulary": "%s",\n  "exit_codes": {"0": "probe completed", "2": "drift (listeners does not gate)", "1": "probe error"},\n  "summary": {"probed": %s, "model_endpoints": %s, "foreign_service": %s, "unauthorized_service": %s, "dead": %s, "not_http": %s},\n  "listeners": [\n%s\n  ]\n}\n' \
      "$VOCAB" "${#ports[@]}" "$n_model" "$n_foreign" "$n_unauth" "$n_dead" "$n_nothttp" "$(json_array "${json_rows[@]}")")"
    return 0
  fi
  printf '%s\n' "${table[@]}" | print_table
  printf 'probed=%s model_endpoints=%s foreign_service=%s unauthorized_service=%s dead=%s not_http=%s\n' \
    "${#ports[@]}" "$n_model" "$n_foreign" "$n_unauth" "$n_dead" "$n_nothttp"
}

# shared row builder: resolve a registry row's file value
# sets R_RESOLVED R_KIND R_ENDPOINT R_FMATCH
R_RESOLVED='' R_KIND='' R_ENDPOINT='' R_FMATCH=''
resolve_row() { # $1 consumer path, $2 resolver spec, $3 declared baseurl
  local cpath=$1 spec=$2 declared=$3 file rspec
  R_RESOLVED='' R_KIND='' R_ENDPOINT='' R_FMATCH=''
  file=$(expand_path "$cpath")
  if [ ! -f "$file" ]; then
    R_KIND=error; R_FMATCH=missing; R_ENDPOINT=$declared
    return 0
  fi
  rspec=$(resolve_spec "$file" "$spec")
  R_RESOLVED=${rspec%|*}; R_KIND=${rspec##*|}
  case "$R_KIND" in
    url|port:*)
      R_ENDPOINT=$R_RESOLVED
      if [ "$R_RESOLVED" = "$declared" ]; then R_FMATCH=yes; else R_FMATCH=no; fi ;;
    raw)
      R_ENDPOINT=$declared; R_FMATCH=inherited ;;
    *)
      R_ENDPOINT=$declared; R_FMATCH=unresolved ;;
  esac
  return 0
}

cmd_consumers() {
  local -a table=() json_rows=()
  table+=("$(printf 'id\tconsumer\tdeclared\tresolved_from_file\tfile_match\tresolver_kind\tendpoint\tport\tverdict\tserved_model')")
  local exit_code=0

  if [ -n "$OPT_PORT" ]; then
    local v_id="${OPT_ID:-cli-override}"
    local declared="http://127.0.0.1:$OPT_PORT/v1"
    classify "$OPT_PORT" "${OPT_EXPECT:-}"
    table+=("$(printf '%s\t--port override\t%s\t%s\tyes\tcli-override\t%s\t%s\t%s\t%s' \
      "$v_id" "$declared" "$declared" "$declared" "$OPT_PORT" "$C_VERDICT" "$C_SERVED")")
    json_rows+=("$(printf '    {"id":%s,"consumer_path":"-","declared":%s,"resolved_from_file":%s,"file_match":"yes","resolve_kind":"cli-override","endpoint":%s,"port":%s,"expected_model_id":%s,"verdict":%s,"reason":%s,"served_model":%s,"evidence":%s,"notes":""}' \
      "$(jstr "$v_id")" "$(jstr "$declared")" "$(jstr "$declared")" "$(jstr "$declared")" \
      "$OPT_PORT" "$(jstr "${OPT_EXPECT:--}")" "$(jstr "$C_VERDICT")" "$(jstr "$C_REASON")" \
      "$(jstr "$C_SERVED")" "$(jstr "$C_EVIDENCE")")")
  else
    read_registry "$OPT_REGISTRY"
    local i id declared expected pnum
    for ((i=0; i<REG_ROWS; i++)); do
      id=${REG_IDS[i]}; declared=${REG_DECLARED[i]}; expected=${REG_EXPECT[i]}
      resolve_row "${REG_PATHS[i]}" "${REG_SPECS[i]}" "$declared"
      [ "$R_FMATCH" = no ] && exit_code=2
      [ "$R_FMATCH" = missing ] && exit_code=2
      pnum=$(url_port "$R_ENDPOINT")
      classify "$pnum" "$expected"
      table+=("$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' \
        "$id" "${REG_PATHS[i]}" "$declared" "${R_RESOLVED:--}" "$R_FMATCH" "$R_KIND" \
        "$R_ENDPOINT" "$pnum" "$C_VERDICT" "$C_SERVED")")
      json_rows+=("$(printf '    {"id":%s,"consumer_path":%s,"resolver":%s,"declared":%s,"resolved_from_file":%s,"file_match":%s,"resolve_kind":%s,"endpoint":%s,"port":%s,"expected_model_id":%s,"verdict":%s,"reason":%s,"served_model":%s,"evidence":%s,"notes":%s}' \
        "$(jstr "$id")" "$(jstr "${REG_PATHS[i]}")" "$(jstr "${REG_SPECS[i]}")" "$(jstr "$declared")" \
        "$(jstr "${R_RESOLVED:--}")" "$(jstr "$R_FMATCH")" "$(jstr "$R_KIND")" "$(jstr "$R_ENDPOINT")" \
        "$pnum" "$(jstr "$expected")" "$(jstr "$C_VERDICT")" "$(jstr "$C_REASON")" \
        "$(jstr "$C_SERVED")" "$(jstr "$C_EVIDENCE")" "$(jstr "${REG_NOTES[i]}")")")
    done
  fi

  if [ "$JSON_OUT" -eq 1 ]; then
    emit_json "$(printf '{\n  "schema": "kama-probe/v1",\n  "subcommand": "consumers",\n  "registry": %s,\n  "verdict_vocabulary": "%s",\n  "exit_codes": {"0": "registry text matches every file", "2": "registry text disagrees with a file", "1": "probe error"},\n  "summary": {"consumer_rows_registered": %s, "consumer_rows_evaluated": %s, "exit": %s},\n  "consumers": [\n%s\n  ]\n}\n' \
      "$(jstr "$OPT_REGISTRY")" "$VOCAB" "${REG_ROWS:-${#json_rows[@]}}" "${#json_rows[@]}" "$exit_code" \
      "$(json_array "${json_rows[@]}")")"
    return "$exit_code"
  fi
  printf '%s\n' "${table[@]}" | print_table
  printf 'consumer_rows_evaluated=%s exit=%s\n' "${#json_rows[@]}" "$exit_code"
  return "$exit_code"
}

cmd_check() {
  local -a table=() json_rows=()
  table+=("$(printf 'id\tconsumer\tdeclared\tverdict\treason\tserved_model\tevidence')")
  local exit_code=0 n_ok=0 n_drift=0

  if [ -n "$OPT_PORT" ]; then
    local v_id="${OPT_ID:-cli-override}"
    local declared="http://127.0.0.1:$OPT_PORT/v1"
    classify "$OPT_PORT" "${OPT_EXPECT:-}"
    if [ "$C_VERDICT" = "MODEL_OK" ]; then n_ok=1; else n_drift=1; exit_code=2; fi
    table+=("$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s' \
      "$v_id" "--port $OPT_PORT override" "$declared" "$C_VERDICT" "$C_REASON" "$C_SERVED" "$C_EVIDENCE")")
    json_rows+=("$(printf '    {"id":%s,"consumer_path":"-","declared":%s,"file_match":"cli-override","resolver_kind":"cli-override","expected_model_id":%s,"verdict":%s,"reason":%s,"served_model":%s,"drift":%s,"evidence":%s,"notes":""}' \
      "$(jstr "$v_id")" "$(jstr "$declared")" "$(jstr "${OPT_EXPECT:--}")" "$(jstr "$C_VERDICT")" \
      "$(jstr "$C_REASON")" "$(jstr "$C_SERVED")" \
      "$([ "$C_VERDICT" = MODEL_OK ] && echo false || echo true)" "$(jstr "$C_EVIDENCE")")")
  else
    read_registry "$OPT_REGISTRY"
    local i id declared expected pnum verdict drift
    for ((i=0; i<REG_ROWS; i++)); do
      id=${REG_IDS[i]}; declared=${REG_DECLARED[i]}; expected=${REG_EXPECT[i]}
      resolve_row "${REG_PATHS[i]}" "${REG_SPECS[i]}" "$declared"
      pnum=$(url_port "$R_ENDPOINT")
      classify "$pnum" "$expected"
      verdict=$C_VERDICT
      drift=false
      if [ "$verdict" != "MODEL_OK" ]; then drift=true; fi
      case "$R_FMATCH" in yes|inherited) : ;; *) drift=true ;; esac
      if [ "$drift" = true ]; then n_drift=$((n_drift+1)); exit_code=2; else n_ok=$((n_ok+1)); fi
      table+=("$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s' \
        "$id" "${REG_PATHS[i]}" "$declared" "$verdict" "$C_REASON" "$C_SERVED" \
        "file=$R_FMATCH via $R_KIND @$pnum; $C_EVIDENCE")")
      json_rows+=("$(printf '    {"id":%s,"consumer_path":%s,"resolver":%s,"declared":%s,"resolved_from_file":%s,"file_match":%s,"resolve_kind":%s,"endpoint":%s,"port":%s,"expected_model_id":%s,"verdict":%s,"reason":%s,"served_model":%s,"drift":%s,"evidence":%s,"notes":%s}' \
        "$(jstr "$id")" "$(jstr "${REG_PATHS[i]}")" "$(jstr "${REG_SPECS[i]}")" "$(jstr "$declared")" \
        "$(jstr "${R_RESOLVED:--}")" "$(jstr "$R_FMATCH")" "$(jstr "$R_KIND")" "$(jstr "$R_ENDPOINT")" \
        "$pnum" "$(jstr "$expected")" "$(jstr "$verdict")" "$(jstr "$C_REASON")" \
        "$(jstr "$C_SERVED")" "$drift" "$(jstr "$C_EVIDENCE")" "$(jstr "${REG_NOTES[i]}")")")
    done
  fi

  local evaluated=${#json_rows[@]}
  if [ "$JSON_OUT" -eq 1 ]; then
    emit_json "$(printf '{\n  "schema": "kama-probe/v1",\n  "subcommand": "check",\n  "registry": %s,\n  "verdict_vocabulary": "%s",\n  "exit_codes": {"0": "every declared consumer reconciles", "2": "at least one drift", "1": "probe error"},\n  "summary": {"registry_rows_evaluated": %s, "model_ok": %s, "drift": %s, "exit": %s},\n  "rows": [\n%s\n  ]\n}\n' \
      "$(jstr "$OPT_REGISTRY")" "$VOCAB" "$evaluated" "$n_ok" "$n_drift" "$exit_code" \
      "$(json_array "${json_rows[@]}")")"
    return "$exit_code"
  fi

  printf '%s\n' "${table[@]}" | print_table
  printf 'registry_rows_evaluated=%s model_ok=%s drift=%s exit=%s\n' "$evaluated" "$n_ok" "$n_drift" "$exit_code"
  return "$exit_code"
}

# ---------------------------------------------------------------- main
main() {
  parse_args "$@"
  command -v ss >/dev/null 2>&1 || die "missing dependency: ss"
  command -v curl >/dev/null 2>&1 || die "missing dependency: curl"
  if [ "$HAVE_PY" -eq 0 ]; then
    warn "python3 not found — using grep fallbacks for JSON-pointer and model-id parsing"
  fi
  TMP_ROOT=$(mktemp -d "${KAMA_PROBE_TMPDIR:-/tmp}/kama-probe.XXXXXX")

  case "$SUBCOMMAND" in
    listeners) load_listeners; cmd_listeners ;;
    consumers) cmd_consumers ;;
    check) cmd_check ;;
    *) usage >&2; exit 1 ;;
  esac
}

main "$@"