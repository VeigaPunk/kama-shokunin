#!/usr/bin/env bash
# kama-probe.sh — loopback model-endpoint probe + consumer-registry reconciler.
#
# Domain: local model serving & endpoint health (kama-shokunin).
# Answers exactly one question: "is the thing at this baseURL the model this config
# believes it is, right now" — never "is the model good" (kengaku) or "is the request
# safe" (kagi).
#
# Read-only toward live services and consumer configs. listeners/consumers/check
# write only to a removed mktemp dir. snapshot additionally writes inside its
# explicit history dir. Non-snapshot output is byte-stable for identical state;
# snapshot intentionally carries UTC ids/timestamps and a predecessor link.
#
# Subcommands:
#   listeners   enumerate loopback TCP listeners (ss -ltn) and classify each
#   consumers   resolve each registry consumer's declared baseURL FROM ITS OWN FILE
#               (never from the TSV text) and report declared-vs-actual
#   check       reconcile registry entries against live classification (exit gate)
#   snapshot    run the check evaluation AND persist it: dated JSON + a TSV baseline
#               + a transition ledger under a history dir. On every run after the
#               first, each row is diffed against the previous baseline and verdict/
#               served-model/port/file-match transitions are appended to DELTA.md —
#               the bounded drift window a manual `check` cannot give (v4 contract).
#
# Common flags: --json  --registry PATH  --timeout S  --connect-timeout S  --help
# Matrix flags: --port N  --expect ID  --id KEY | snapshot-only: --history DIR
#
# Verdict vocabulary (exact strings):
#   MODEL_OK MODEL_MISMATCH FOREIGN_SERVICE UNAUTHORIZED_SERVICE DEAD NOT_HTTP
#   MODEL_LOADING
#
# MODEL_LOADING: GET /v1/models answered 503 with the exact llama.cpp single-model
# loading envelope {"error":{"message":"Loading model","type":"unavailable_error","code":503}}
# (b11755 tools/server/server-http.cpp:307-328). Drift (exit 2): not ready. A body-shape
# match only — runtime identity and served model are unverified. Router mode never
# emits it; requires python3 (without it the body keeps FOREIGN_SERVICE).
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
# History layout (snapshot; DIR default <repo>/registry/history, override --history):
#   <ISO-UTC>.json   dated, persistence-safe row state (schema kama-probe/v2)
#   latest.tsv       baseline, one row per consumer: id,verdict,reason,served,port,fmatch
#   DELTA.md         append-only ledger; one line per transition, "<ts> id field old->new"
# First run writes a "baseline" line and records no transitions. A corrupt or
# unreadable latest.tsv rebaselines (warned + noted) rather than breaking the
# gate. snapshot refuses --port mode: a matrix probe has no registry baseline.
# Persisted rows exclude evidence, notes, resolved URLs and raw model paths;
# served ids use the same basename/.gguf normalization as identity comparison.
#
# Deps: ss, curl, flock, coreutils. python3 optional (exact JSON-pointer/model-id
# parsing and generated-JSON validation; grep fallbacks used when absent).
set -euo pipefail
umask 077

VOCAB="MODEL_OK MODEL_MISMATCH FOREIGN_SERVICE UNAUTHORIZED_SERVICE DEAD NOT_HTTP MODEL_LOADING"

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
OPT_HISTORY="$REPO_ROOT/registry/history"
OPT_UFO_SRC=""
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
usage: kama-probe.sh <listeners|consumers|check|snapshot> [flags]

  listeners            enumerate loopback TCP listeners and classify each
  consumers            resolve each registry consumer's baseURL from its own file
  check                reconcile registry entries against live classification
  snapshot             check + persist: dated JSON, TSV baseline, DELTA.md ledger
                       under a history dir (see the header contract)

flags:
  --json               emit JSON on stdout (diagnostics stay on stderr)
  --port N             probe only port N (single-port mode; pair with --expect for matrices)
  --expect ID          expected model id for --port mode ("*" or "-" = any)
  --id KEY             row id to label --port mode with (default cli-override)
  --registry PATH      registry TSV to use (default registry/endpoint-consumers.tsv)
  --history DIR        snapshot history dir (default registry/history; snapshot only)
  --ufo-src DIR        ufo-fsd-alpha checkout for '$UFO_SRC/...' registry rows
                       (default: $UFO_SRC env, else first existing of
                       ~/Projects/ufo-fsd-alpha then ~/Projects/origin-work/ufo-fsd-alpha;
                       if none exists, $UFO_SRC rows resolve as file=missing)
  --timeout S          per-request curl --max-time in seconds (default 5)
  --connect-timeout S  per-request curl --connect-timeout in seconds (default 2)

verdicts: MODEL_OK MODEL_MISMATCH FOREIGN_SERVICE UNAUTHORIZED_SERVICE DEAD NOT_HTTP MODEL_LOADING
exit: 0 reconciled | 2 drift | 1 probe error
EOF
}

parse_args() {
  while [ $# -gt 0 ]; do
    case "$1" in
      listeners|consumers|check|snapshot) [ -z "$SUBCOMMAND" ] && SUBCOMMAND=$1 || die "duplicate subcommand: $1" ;;
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
      --history) shift; [ $# -gt 0 ] || die "--history needs a value"; OPT_HISTORY=$1 ;;
      --ufo-src) shift; [ $# -gt 0 ] || die "--ufo-src needs a value"; OPT_UFO_SRC=$1 ;;
      --ufo-src=*) OPT_UFO_SRC=${1#*=} ;;
      --history=*) OPT_HISTORY=${1#*=} ;;
      --help|-h) usage; exit 0 ;;
      *) die "unknown argument: $1 (see --help)" ;;
    esac
    shift
  done
  if [ -n "$OPT_UFO_SRC" ]; then
    [ -d "$OPT_UFO_SRC" ] || die "--ufo-src is not a directory: $OPT_UFO_SRC"
  fi
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
  if [ "$SUBCOMMAND" = "snapshot" ] && [ -n "$OPT_PORT" ]; then
    die "snapshot refuses --port: a matrix probe has no registry baseline to persist"
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

# llama.cpp loading gate (b11755 tools/server/server-http.cpp:307-325): while
# is_ready is false every non-frontend path returns 503 with the exact envelope
# {"error":{"message":"Loading model","type":"unavailable_error","code":503}}.
# That is not-ready drift; the body shape does not prove the runtime. Exact match only —
# any deviation (e.g. "no slot available" unavailable_error, code as string or
# float, non-503 status) falls through to the generic path. Requires python3:
# a grep approximation cannot prove the exact envelope, so without python3 the
# body keeps its old FOREIGN_SERVICE verdict (fail closed, never false-pass).
body_is_llamacpp_loading() { # $1 body file -> 0 only on the exact loading envelope
  [ "$HAVE_PY" -eq 1 ] || return 1
  python3 - "$1" <<'PY' 2>/dev/null
import json, sys
try:
    doc = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(1)
if not isinstance(doc, dict):
    sys.exit(1)
err = doc.get("error")
if not isinstance(err, dict):
    sys.exit(1)
code = err.get("code")
if err.get("message") == "Loading model" and err.get("type") == "unavailable_error" \
        and not isinstance(code, bool) and isinstance(code, int) and code == 503:
    sys.exit(0)
sys.exit(1)
PY
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

  if [ "$F_CODE" = "503" ] && [ -s "$FBODY" ] && body_is_llamacpp_loading "$FBODY"; then
    C_VERDICT=MODEL_LOADING
    C_REASON=llamacpp-loading
    C_EVIDENCE="$base (body matches the llama.cpp loading envelope: not ready; runtime identity and served model unverified); GET /health -> $(probe_short "$port" "/health")"
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

# ---------------------------------------------------------------- ufo-fsd source root
# Cross-repo consumer rows cite the ufo-fsd-alpha checkout as '$UFO_SRC/<relpath>'
# so the registry survives a relocation of that tree (2026-10-12: it moved from
# ~/Projects/origin-work/ to ~/Projects/; the old root may exist again or not).
# Resolution order, first match wins: --ufo-src flag > $UFO_SRC env > first
# existing candidate dir. If nothing resolves, the row degrades to file=missing
# (an honest DEAD/absent verdict), never to a silently guessed path.
UFO_SRC_CACHE=""
UFO_SRC_RESOLVED=0

ufo_src() { # -> resolved dir on stdout (may be empty)
  if [ "$UFO_SRC_RESOLVED" -eq 0 ]; then
    UFO_SRC_RESOLVED=1
    if [ -n "$OPT_UFO_SRC" ]; then
      UFO_SRC_CACHE=$OPT_UFO_SRC
    elif [ -n "${UFO_SRC:-}" ] && [ -d "${UFO_SRC:-}" ]; then
      UFO_SRC_CACHE=$UFO_SRC
    else
      local cand
      for cand in "$HOME/Projects/ufo-fsd-alpha" "$HOME/Projects/origin-work/ufo-fsd-alpha"; do
        if [ -d "$cand" ]; then UFO_SRC_CACHE=$cand; break; fi
      done
    fi
  fi
  printf '%s' "$UFO_SRC_CACHE"
}

# ---------------------------------------------------------------- resolve
expand_path() { # $1 -> ~ expanded, $UFO_SRC/ resolved, relative paths anchored at the repo root
  local p=$1
  case "$p" in
    '$UFO_SRC/'*|'$UFO_SRC')
      local src; src=$(ufo_src)
      if [ -n "$src" ]; then p="$src${p#\$UFO_SRC}"; else printf '%s' ""; return 0; fi ;;
  esac
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
    # never surface credentials: strip userinfo and query/fragment from the
    # resolved endpoint before it reaches output or the ledger (sentinel r2)
    url=${url%%\?*}; url=${url%%\#*}
    if [[ $url =~ ^https?://[^/]*@ ]]; then url="${url%%://*}://${url#*@}"; fi
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
  local i n_model=0 n_dead=0 n_foreign=0 n_nothttp=0 n_unauth=0 n_loading=0
  for ((i=0; i<${#ports[@]}; i++)); do
    port=${ports[i]}
    classify "$port" "${OPT_EXPECT:-}"
    case "$C_VERDICT" in
      MODEL_OK|MODEL_MISMATCH) n_model=$((n_model+1)) ;;
      DEAD) n_dead=$((n_dead+1)) ;;
      FOREIGN_SERVICE) n_foreign=$((n_foreign+1)) ;;
      NOT_HTTP) n_nothttp=$((n_nothttp+1)) ;;
      UNAUTHORIZED_SERVICE) n_unauth=$((n_unauth+1)) ;;
      MODEL_LOADING) n_loading=$((n_loading+1)) ;;
    esac
    table+=("$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s' \
      "$port" "${scopes[i]}" "${OWNER[$port]:--}" "$C_VERDICT" "$C_REASON" "$C_SERVED" "$C_EVIDENCE")")
    json_rows+=("$(printf '    {"port":%s,"bind":%s,"owner":%s,"verdict":%s,"reason":%s,"served_model":%s,"evidence":%s}' \
      "$port" "$(jstr "${scopes[i]}")" "$(jstr "${OWNER[$port]:--}")" \
      "$(jstr "$C_VERDICT")" "$(jstr "$C_REASON")" "$(jstr "$C_SERVED")" "$(jstr "$C_EVIDENCE")")")
  done

  if [ "$JSON_OUT" -eq 1 ]; then
    emit_json "$(printf '{\n  "schema": "kama-probe/v1",\n  "subcommand": "listeners",\n  "verdict_vocabulary": "%s",\n  "exit_codes": {"0": "probe completed", "2": "drift (listeners does not gate)", "1": "probe error"},\n  "summary": {"probed": %s, "model_endpoints": %s, "foreign_service": %s, "unauthorized_service": %s, "dead": %s, "not_http": %s, "model_loading": %s},\n  "listeners": [\n%s\n  ]\n}\n' \
      "$VOCAB" "${#ports[@]}" "$n_model" "$n_foreign" "$n_unauth" "$n_dead" "$n_nothttp" "$n_loading" "$(json_array "${json_rows[@]}")")"
    return 0
  fi
  printf '%s\n' "${table[@]}" | print_table
  printf 'probed=%s model_endpoints=%s foreign_service=%s unauthorized_service=%s dead=%s not_http=%s model_loading=%s\n' \
    "${#ports[@]}" "$n_model" "$n_foreign" "$n_unauth" "$n_dead" "$n_nothttp" "$n_loading"
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

# ---------------------------------------------------------------- row evaluation
# Shared by check and snapshot. Fills EV_* parallel arrays + EV_JSON (pretty-printed
# row objects, 4-space indented). Returns the gate exit code (0 clean / 2 drift).
EV_N=0 EV_OK=0 EV_DRIFT=0 EV_JSON=''
declare -a EV_IDS=() EV_PATHS=() EV_DECLARED=() EV_RESOLVED=() EV_FMATCH=() EV_RKIND=()
declare -a EV_ENDPOINT=() EV_PORT=() EV_EXPECT=() EV_VERDICT=() EV_REASON=()
declare -a EV_SERVED=() EV_DRIFTROW=() EV_EVIDENCE=() EV_NOTES=()

eval_rows() {
  local -a json_rows=()
  EV_N=0 EV_OK=0 EV_DRIFT=0 EV_JSON=''
  EV_IDS=() EV_PATHS=() EV_DECLARED=() EV_RESOLVED=() EV_FMATCH=() EV_RKIND=()
  EV_ENDPOINT=() EV_PORT=() EV_EXPECT=() EV_VERDICT=() EV_REASON=()
  EV_SERVED=() EV_DRIFTROW=() EV_EVIDENCE=() EV_NOTES=()

  if [ -n "$OPT_PORT" ]; then
    local v_id="${OPT_ID:-cli-override}"
    local declared="http://127.0.0.1:$OPT_PORT/v1"
    classify "$OPT_PORT" "${OPT_EXPECT:-}"
    EV_IDS=("$v_id"); EV_PATHS=("-"); EV_DECLARED=("$declared"); EV_RESOLVED=("-")
    EV_FMATCH=("cli-override"); EV_RKIND=("cli-override"); EV_ENDPOINT=("$declared")
    EV_PORT=("$OPT_PORT"); EV_EXPECT=("${OPT_EXPECT:--}"); EV_VERDICT=("$C_VERDICT")
    EV_REASON=("$C_REASON"); EV_SERVED=("$C_SERVED"); EV_EVIDENCE=("$C_EVIDENCE")
    EV_NOTES=(""); EV_N=1
    if [ "$C_VERDICT" = "MODEL_OK" ]; then EV_OK=1; EV_DRIFTROW=(false)
    else EV_DRIFT=1; EV_DRIFTROW=(true); fi
    json_rows+=("$(printf '    {"id":%s,"consumer_path":"-","declared":%s,"file_match":"cli-override","resolver_kind":"cli-override","expected_model_id":%s,"verdict":%s,"reason":%s,"served_model":%s,"drift":%s,"evidence":%s,"notes":""}' \
      "$(jstr "$v_id")" "$(jstr "$declared")" "$(jstr "${OPT_EXPECT:--}")" "$(jstr "$C_VERDICT")" \
      "$(jstr "$C_REASON")" "$(jstr "$C_SERVED")" \
      "${EV_DRIFTROW[0]}" "$(jstr "$C_EVIDENCE")")")
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
      if [ "$drift" = true ]; then EV_DRIFT=$((EV_DRIFT+1)); else EV_OK=$((EV_OK+1)); fi
      EV_IDS+=("$id"); EV_PATHS+=("${REG_PATHS[i]}"); EV_DECLARED+=("$declared")
      EV_RESOLVED+=("${R_RESOLVED:--}"); EV_FMATCH+=("$R_FMATCH"); EV_RKIND+=("$R_KIND")
      EV_ENDPOINT+=("$R_ENDPOINT"); EV_PORT+=("$pnum"); EV_EXPECT+=("$expected")
      EV_VERDICT+=("$verdict"); EV_REASON+=("$C_REASON"); EV_SERVED+=("$C_SERVED")
      EV_DRIFTROW+=("$drift"); EV_EVIDENCE+=("$C_EVIDENCE"); EV_NOTES+=("${REG_NOTES[i]}")
      EV_N=$((EV_N+1))
      json_rows+=("$(printf '    {"id":%s,"consumer_path":%s,"resolver":%s,"declared":%s,"resolved_from_file":%s,"file_match":%s,"resolve_kind":%s,"endpoint":%s,"port":%s,"expected_model_id":%s,"verdict":%s,"reason":%s,"served_model":%s,"drift":%s,"evidence":%s,"notes":%s}' \
        "$(jstr "$id")" "$(jstr "${REG_PATHS[i]}")" "$(jstr "${REG_SPECS[i]}")" "$(jstr "$declared")" \
        "$(jstr "${R_RESOLVED:--}")" "$(jstr "$R_FMATCH")" "$(jstr "$R_KIND")" "$(jstr "$R_ENDPOINT")" \
        "$pnum" "$(jstr "$expected")" "$(jstr "$verdict")" "$(jstr "$C_REASON")" \
        "$(jstr "$C_SERVED")" "$drift" "$(jstr "$C_EVIDENCE")" "$(jstr "${REG_NOTES[i]}")")")
    done
  fi
  EV_JSON=$(json_array "${json_rows[@]}")
  [ "$EV_DRIFT" -gt 0 ] && return 2 || return 0
}

cmd_check() {
  # `eval_rows || exit_code=$?`: a bare call would trip set -e on the drift exit 2
  local exit_code=0
  eval_rows || exit_code=$?
  if [ "$JSON_OUT" -eq 1 ]; then
    emit_json "$(printf '{\n  "schema": "kama-probe/v1",\n  "subcommand": "check",\n  "registry": %s,\n  "verdict_vocabulary": "%s",\n  "exit_codes": {"0": "every declared consumer reconciles", "2": "at least one drift", "1": "probe error"},\n  "summary": {"registry_rows_evaluated": %s, "model_ok": %s, "drift": %s, "exit": %s},\n  "rows": [\n%s\n  ]\n}\n' \
      "$(jstr "$OPT_REGISTRY")" "$VOCAB" "$EV_N" "$EV_OK" "$EV_DRIFT" "$exit_code" \
      "$EV_JSON")"
    return "$exit_code"
  fi

  local -a table=()
  table+=("$(printf 'id\tconsumer\tdeclared\tverdict\treason\tserved_model\tevidence')")
  local i
  for ((i=0; i<EV_N; i++)); do
    table+=("$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s' \
      "${EV_IDS[i]}" "${EV_PATHS[i]}" "${EV_DECLARED[i]}" "${EV_VERDICT[i]}" \
      "${EV_REASON[i]}" "${EV_SERVED[i]}" \
      "file=${EV_FMATCH[i]} via ${EV_RKIND[i]} @${EV_PORT[i]}; ${EV_EVIDENCE[i]}")")
  done
  printf '%s\n' "${table[@]}" | print_table
  printf 'registry_rows_evaluated=%s model_ok=%s drift=%s exit=%s\n' "$EV_N" "$EV_OK" "$EV_DRIFT" "$exit_code"
  return "$exit_code"
}

# ---------------------------------------------------------------- snapshot
# Compute row-set transitions against the previous latest.tsv baseline — pure
# comparison, no writes; the caller decides when DELTA.md is appended (after the
# dated JSON validates, so a failed snapshot re-derives transitions next run).
# Baseline row format: id \t verdict \t reason \t served \t port \t fmatch.
# Sets DELTA_LINES[], N_TRANS, PREV_ID. $1 ts, $2 history dir.
declare -a DELTA_LINES=()
N_TRANS=0 PREV_ID='-'

diff_baseline() {
  local ts=$1 hist=$2
  local -A PV_V=() PV_R=() PV_S=() PV_P=() PV_F=()
  PREV_ID='-'
  local -a MAL_NOTES=()
  if [ -f "$hist/latest.tsv" ] && [ ! -r "$hist/latest.tsv" ]; then
    # unreadable baseline: rebaseline rather than die with a bare shell redirect
    # error (contract: losing a baseline must never break the gate)
    warn "latest.tsv unreadable — rebaselining"
    MAL_NOTES+=("- $ts baseline-note unreadable-latest.tsv; rebaseline")
  elif [ -f "$hist/latest.tsv" ]; then
    local id v r s p f bad=0
    while IFS=$'\t' read -r id v r s p f; do
      case "${id:-}" in ''|'#'*)
        case "${id:-}" in '#@snapshot_id'*) PREV_ID=${id##* } ;; esac
        continue ;;
      esac
      # a baseline row is only believable if its verdict is in the vocabulary —
      # garbage lines are dropped (warned + noted in DELTA.md), not turned into
      # phantom row-absent transitions and not silently forgiven
      case " ${v:-} " in
        *\ MODEL_OK\ *|*\ MODEL_MISMATCH\ *|*\ FOREIGN_SERVICE\ *|*\ UNAUTHORIZED_SERVICE\ *|*\ DEAD\ *|*\ NOT_HTTP\ *|*\ MODEL_LOADING\ *) : ;;
        *) warn "latest.tsv: dropping malformed baseline row for id='$id'"
           MAL_NOTES+=("- $ts baseline-note malformed-row-dropped id='$(persist_clean "$id")'")
           bad=1; continue ;;
      esac
      PV_V[$id]=${v:-} PV_R[$id]=${r:-} PV_S[$id]=${s:-} PV_P[$id]=${p:-} PV_F[$id]=${f:-}
    done < "$hist/latest.tsv"
    if [ "${#PV_V[@]}" -eq 0 ]; then
      warn "latest.tsv has no usable baseline rows — rebaselining"
    elif [ "$bad" -eq 1 ]; then
      warn "latest.tsv had malformed rows (dropped); this snapshot rebaselines them"
    fi
  fi

  DELTA_LINES=() N_TRANS=0
  [ "${#MAL_NOTES[@]}" -gt 0 ] && DELTA_LINES+=("${MAL_NOTES[@]}")
  local i rid
  if [ "${#PV_V[@]}" -eq 0 ]; then
    DELTA_LINES+=("- $ts baseline recorded ($EV_N rows); transitions begin with the next snapshot")
  else
    local -A SEEN=()
    for ((i=0; i<EV_N; i++)); do
      rid=$(persist_clean "${EV_IDS[i]}")
      SEEN[$rid]=1
      if [ -z "${PV_V[$rid]+x}" ]; then
        DELTA_LINES+=("- $ts $rid row-added verdict=${EV_VERDICT[i]} port=${EV_PORT[i]} served=$(served_persist "${EV_SERVED[i]}")")
        N_TRANS=$((N_TRANS+1))
        continue
      fi
      local fields=(verdict reason served_model port file_match)
      # served_model compares PERSISTED form (normalised basename) on both sides —
      # a raw GGUF-path change that keeps the basename is not an identity change.
      local vals_new=("${EV_VERDICT[i]}" "$(persist_clean "${EV_REASON[i]}")" "$(served_persist "${EV_SERVED[i]}")" "$(persist_clean "${EV_PORT[i]}")" "$(persist_clean "${EV_FMATCH[i]}")")
      local vals_old=("$(persist_clean "${PV_V[$rid]}")" "$(persist_clean "${PV_R[$rid]}")" "$(persist_clean "${PV_S[$rid]}")" "$(persist_clean "${PV_P[$rid]}")" "$(persist_clean "${PV_F[$rid]}")")
      local k
      for ((k=0; k<${#fields[@]}; k++)); do
        if [ "${vals_new[k]}" != "${vals_old[k]}" ]; then
          DELTA_LINES+=("- $ts $rid ${fields[k]} ${vals_old[k]:--} -> ${vals_new[k]:--}")
          N_TRANS=$((N_TRANS+1))
        fi
      done
    done
    # sorted for deterministic output (planner r2: assoc-array order is arbitrary)
    while IFS= read -r rid; do
      if [ -z "${SEEN[$rid]+x}" ]; then
        DELTA_LINES+=("- $ts $(persist_clean "$rid") row-absent (was verdict=$(persist_clean "${PV_V[$rid]}") port=$(persist_clean "${PV_P[$rid]}"))")
        N_TRANS=$((N_TRANS+1))
      fi
    done < <(printf '%s\n' "${!PV_V[@]}" | sort)
  fi
}

# ------------------------------------------------- persisted-field hygiene
# Fields that land in latest.tsv / DELTA.md must not carry control chars (a
# hostile loopback service can inject TAB/CR via Server/Content-Type headers and
# corrupt the TSV trust anchor — sentinel round-2) or URL userinfo/query (creds
# in a baseURL must never persist to the ledger).
persist_clean() { # $1 -> single-line, tab-free, control-stripped value
  local s=${1-}
  s=${s//$'\t'/ }; s=${s//$'\n'/ }; s=${s//$'\r'/ }
  s=$(printf '%s' "$s" | tr -d '[:cntrl:]')
  printf '%s' "$s"
}

# served ids persist as NORMALISED basenames (matches contract v2 semantics):
# two ids differing only in directory or a trailing .gguf are the same model.
served_persist() { # $1 comma-joined raw served ids -> comma-joined basenames
  local s=${1-} out='' parts=() p
  [ "$s" = "-" ] && { printf '%s' '-'; return 0; }
  IFS=',' read -r -a parts <<< "$s"
  for p in "${parts[@]}"; do
    p=$(normalize_id "$(persist_clean "$p")")
    [ -n "$p" ] || p='-'
    out+="${out:+,}$p"
  done
  printf '%s' "${out:--}"
}

cmd_snapshot() {
  # `eval_rows || exit_code=$?`: a bare call would trip set -e on the drift exit 2
  local exit_code=0
  eval_rows || exit_code=$?
  local hist=$OPT_HISTORY ts snap_id snap_file
  ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  snap_id=$(date -u +%Y%m%dT%H%M%SZ)
  snap_file="$hist/$snap_id.json"
  if [ -e "$snap_file" ] || [ -L "$snap_file" ]; then
    snap_file="$hist/$snap_id-p$$.json"
    { [ ! -e "$snap_file" ] && [ ! -L "$snap_file" ]; } ||
      die "snapshot filename collision: $snap_file"
  fi

  # symlink refusal before mkdir -p: a planted link would aim the writes outside
  # the lane's repo (sentinel round-2 finding — containment check on history dir)
  [ -L "$hist" ] && die "history dir is a symlink (refused): $hist"
  mkdir -p -- "$hist" || die "cannot create history dir: $hist"
  [ -d "$hist" ] && [ -w "$hist" ] || die "history dir not writable: $hist"
  local output_path
  for output_path in "$hist/.lock" "$hist/DELTA.md" "$hist/latest.tsv"; do
    [ -L "$output_path" ] && die "history output is a symlink (refused): $output_path"
  done

  # Serialise snapshots: concurrent runs would interleave DELTA.md and tear the
  # baseline. Snapshot integrity requires flock; other subcommands do not.
  command -v flock >/dev/null 2>&1 || die "missing snapshot dependency: flock"
  exec 9>"$hist/.lock" || die "cannot open snapshot lock: $hist/.lock"
  flock -w 10 9 || die "snapshot lock busy: $hist/.lock"

  diff_baseline "$ts" "$hist"

  # Dated JSON first — if validation/write fails, the baseline is not advanced
  # and DELTA.md is not appended. Persist only the transition contract fields:
  # no registry notes, probe evidence, resolved URLs, or raw filesystem paths.
  local -a snap_rows=()
  local i
  for ((i=0; i<EV_N; i++)); do
    snap_rows+=("$(printf '    {"id":%s,"consumer_path":%s,"port":%s,"expected_model_id":%s,"verdict":%s,"reason":%s,"served_model":%s,"file_match":%s,"drift":%s}' \
      "$(jstr "$(persist_clean "${EV_IDS[i]}")")" "$(jstr "$(persist_clean "${EV_PATHS[i]}")")" \
      "${EV_PORT[i]}" "$(jstr "$(persist_clean "${EV_EXPECT[i]}")")" \
      "$(jstr "${EV_VERDICT[i]}")" "$(jstr "$(persist_clean "${EV_REASON[i]}")")" \
      "$(jstr "$(served_persist "${EV_SERVED[i]}")")" \
      "$(jstr "$(persist_clean "${EV_FMATCH[i]}")")" "${EV_DRIFTROW[i]}")")
  done
  local snap_json
  snap_json=$(printf '{\n  "schema": "kama-probe/v2",\n  "subcommand": "snapshot",\n  "snapshot": {"id": %s, "ts": %s, "prev_snapshot": %s, "registry": %s, "history_dir": %s},\n  "verdict_vocabulary": "%s",\n  "exit_codes": {"0": "every declared consumer reconciles", "2": "at least one drift", "1": "probe error"},\n  "summary": {"registry_rows_evaluated": %s, "model_ok": %s, "drift": %s, "transitions": %s, "exit": %s},\n  "rows": [\n%s\n  ]\n}\n' \
    "$(jstr "$snap_id")" "$(jstr "$ts")" "$(jstr "$PREV_ID")" \
    "$(jstr "$(persist_clean "$OPT_REGISTRY")")" "$(jstr "$(persist_clean "$hist")")" \
    "$VOCAB" "$EV_N" "$EV_OK" "$EV_DRIFT" "$N_TRANS" "$exit_code" \
    "$(json_array "${snap_rows[@]}")")
  if [ "$HAVE_PY" -eq 1 ]; then
    printf '%s\n' "$snap_json" | python3 -c 'import json,sys; json.load(sys.stdin)' \
      || die "internal error: generated snapshot JSON failed to parse (probe bug)"
  fi
  printf '%s\n' "$snap_json" > "$snap_file" || die "cannot write snapshot file: $snap_file"

  if [ ! -f "$hist/DELTA.md" ]; then
    printf '# kama snapshot DELTA.md — endpoint-verdict transition ledger\n#\n' > "$hist/DELTA.md" \
      || die "DELTA.md not writable: $hist"
    printf '# Append-only; one line per row-field change between snapshots, in\n# chronological order. Generated by kama-probe.sh snapshot; never hand-edited.\n\n' \
      >> "$hist/DELTA.md"
  fi
  if [ ${#DELTA_LINES[@]} -gt 0 ]; then
    printf '%s\n' "${DELTA_LINES[@]}" >> "$hist/DELTA.md" || die "DELTA.md not writable: $hist"
  fi

  # Advance tracked state only when the state changed (or recovery rebaselined).
  # Stable scheduled runs must not dirty the repository merely by changing a
  # snapshot id. tmp+mv prevents a killed write from tearing latest.tsv.
  if [ ${#DELTA_LINES[@]} -gt 0 ]; then
    {
      printf '#@snapshot_id %s\t# columns: id\tverdict\treason\tserved_model\tport\tfile_match\n' "$snap_id"
      local i
      for ((i=0; i<EV_N; i++)); do
        printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
          "${EV_IDS[i]}" "${EV_VERDICT[i]}" "$(persist_clean "${EV_REASON[i]:--}")" \
          "$(served_persist "${EV_SERVED[i]:--}")" "${EV_PORT[i]}" "$(persist_clean "${EV_FMATCH[i]:--}")"
      done
    } > "$hist/latest.tsv.new.$$" || die "cannot write baseline: $hist/latest.tsv"
    mv -- "$hist/latest.tsv.new.$$" "$hist/latest.tsv" || die "cannot replace baseline: $hist/latest.tsv"
  fi

  if [ "$JSON_OUT" -eq 1 ]; then
    emit_json "$snap_json"
  else
    local -a table=()
    table+=("$(printf 'id\tconsumer\tverdict\treason\tserved_model\tport\tfile_match')")
    for ((i=0; i<EV_N; i++)); do
      table+=("$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s' \
        "${EV_IDS[i]}" "${EV_PATHS[i]}" "${EV_VERDICT[i]}" "${EV_REASON[i]}" \
        "${EV_SERVED[i]}" "${EV_PORT[i]}" "${EV_FMATCH[i]}")")
    done
    printf '%s\n' "${table[@]}" | print_table
    printf 'snapshot=%s prev=%s rows=%s model_ok=%s drift=%s transitions=%s exit=%s\n' \
      "$snap_id" "$PREV_ID" "$EV_N" "$EV_OK" "$EV_DRIFT" "$N_TRANS" "$exit_code"
    printf 'history=%s (dated JSON + latest.tsv baseline + DELTA.md ledger)\n' "$hist"
  fi
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
    snapshot) cmd_snapshot ;;
    *) usage >&2; exit 1 ;;
  esac
}

main "$@"