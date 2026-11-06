#!/usr/bin/env bash
# round-90 C2 forgery battery (pre-freeze). Builds a scratch fixture repo and runs the frozen counter.
set -u
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
SCR=${HYAKU_SCRATCH:-/fast/scratch/hyaku}/kama-r90/L1
mkdir -p "$SCR"
D=$(mktemp -d "$SCR/c2fix.XXXXXX")
trap 'rm -rf -- "$D"' EXIT
git -C "$D" init -q
[ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ] || { echo "fixture toplevel mismatch"; exit 2; }
mkdir -p "$D/tools" "$D/.ufo/waves/round-90/measured"
printf 'probe bytes v1\n' > "$D/tools/kama-probe.sh"
SHA=$(sha256sum "$D/tools/kama-probe.sh" | cut -d' ' -f1)
cat > "$D/.ufo/waves/round-90/measured/reason-cells.jsonl" <<J
{"cell": "R-matched", "reason": "matched", "verdict": "MODEL_OK", "probe_sha256": "$SHA"}
{"cell": "R-timeout", "reason": "timeout", "verdict": "DEAD", "probe_sha256": "$SHA"}
{"cell": "R-http-401", "reason": "http-401", "verdict": "UNAUTHORIZED_SERVICE", "probe_sha256": "$SHA"}
J
cat > "$D/SKILL.md" <<'M'
# fixture

| reason | verdict | trigger | cell |
|---|---|---|---|
| `http-403` | `UNAUTHORIZED_SERVICE` | row OUTSIDE the section | `R-http-401` |

## Probe reason codes

| reason | verdict | trigger | cell |
|---|---|---|---|
| `matched` | `MODEL_OK` | T1 true row | `R-matched` |
| `timeout` | `MODEL_OK` | T2 wrong verdict | `R-timeout` |
| `schema-unrecognized` | `FOREIGN_SERVICE` | T3 fabricated (no receipt line) | `R-schema` |
| `matched` | `MODEL_OK` | T4 duplicate of T1 | `R-matched` |
| `http-401` | `UNAUTHORIZED_SERVICE` | T5 cell name mismatch | `R-other` |
```
| `http-401` | `UNAUTHORIZED_SERVICE` | T6 inside a fence | `R-http-401` |
```
  | `empty-reply` | `NOT_HTTP` | T7 indented, not column 0 | `R-x` |

## Next section

| `connection-reset` | `NOT_HTTP` | T8 after the section | `R-y` |
M
git -C "$D" add -A && git -C "$D" -c user.name=fixture -c user.email=fixture@invalid commit -qm battery
echo "== battery (expect rows=5 bound=2 (T1 and its duplicate T4) unbound=3 duplicates=1 documented=4, exit 1; first draft of this label said bound=1 unbound=4, corrected before freeze)"
python3 "$LANE/tools/round90-reason-rows.py" --repo "$D" --rev HEAD | grep -E '^REASON_ROW |^REASON_ROWS' ; echo "exit=${PIPESTATUS[0]}"
# stale receipt: probe bytes change, receipt does not
printf 'probe bytes v2\n' > "$D/tools/kama-probe.sh"
python3 - "$D/SKILL.md" <<'P'
import sys
p=sys.argv[1]; s=open(p).read()
import re
s=s.split("## Probe reason codes")[0]+"## Probe reason codes\n\n| reason | verdict | trigger | cell |\n|---|---|---|---|\n| `matched` | `MODEL_OK` | true row | `R-matched` |\n"
open(p,"w").write(s)
P
git -C "$D" add -A && git -C "$D" -c user.name=fixture -c user.email=fixture@invalid commit -qm stale
echo "== stale receipt (expect bound=0 unbound=1 receipt=stale, exit 1)"
python3 "$LANE/tools/round90-reason-rows.py" --repo "$D" --rev HEAD | grep -E '^REASON_ROWS'; echo "exit=${PIPESTATUS[0]}"
# prose-only: all 23 population rows, no receipt at all
git -C "$D" rm -q ".ufo/waves/round-90/measured/reason-cells.jsonl"
python3 - "$D/SKILL.md" <<'P'
import sys
pop="connection-refused timeout empty-reply connection-reset no-http-response http-401 http-403 llamacpp-loading expected-wildcard matched unresolvable-id served-id-mismatch html-non-model schema-unrecognized non-model-2xx non-2xx-non-model-http router-sleeping router-unloaded-autoload router-loading router-downloading router-model-missing router-model-invalid router-unloaded".split()
p=sys.argv[1]; s=open(p).read().split("## Probe reason codes")[0]
s+="## Probe reason codes\n\n| reason | verdict | trigger | cell |\n|---|---|---|---|\n"+"".join(f"| `{r}` | `MODEL_OK` | prose only | `R-{r}` |\n" for r in pop)
open(p,"w").write(s)
P
git -C "$D" add -A && git -C "$D" -c user.name=fixture -c user.email=fixture@invalid commit -qm prose
echo "== prose-only table, receipt absent (expect documented=23 missing=0 bound=0 unbound=23, exit 1)"
python3 "$LANE/tools/round90-reason-rows.py" --repo "$D" --rev HEAD | grep -E '^REASON_ROWS'; echo "exit=${PIPESTATUS[0]}"
