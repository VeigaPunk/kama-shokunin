#!/usr/bin/env python3
"""Build the CR01 forgeries of the frozen round-92 C2 counter's subject.

Each forgery is the measured C2 probe (M2 = fa8aedb7:tools/kama-probe.sh) with ONE change, chosen
so the probe keeps every frozen cell green while a held-out shape shows it still super-linear or
wrong. The counter is frozen (tools/round92-linear-paths.py @ 309eadaf); this script only copies it.

  FG1 jstr: the linear awk pass is taken only when the value does not mix `\\` with `"`; a mixed
            value (a legal 3.2 MB answer) falls back to the base ``${s//pat/repl}`` substitutions,
            which are the quadratic path SC02 F1 measured.
  FG2 router_entries: output capped at 85 000 lines. L3 has 80 000, L4 60 001; a 90 001-entry
            answer whose last entry is the loaded one is truncated before it.
  FG3 served_persist: collections of >1000 ids normalise by stripping ``/m/`` (not the last path
            component). Correct for L5 (all ``/m/xNNNNN.gguf``), wrong for any other directory.
  FG4 served_ids: a trailing space is stripped from each id (no frozen cell carries an id with a
            trailing space; the verdict on such an id changes).
  FG5 served_persist: at most 20 000 ids persisted (L5 has 16 000).

Usage: build-forgeries.py --probe <M2 probe path> --base <BASE probe path> --out DIR
"""
import argparse
import hashlib
from pathlib import Path

FG2_OLD = r'  python3 -c "$ROUTER_PY" "$1" entries 2>/dev/null || true'
FG2_NEW = ('  # FORGERY (CR01 FG2): output capped at 85 000 entries (L3 80 000, L4 60 001).\n'
           r'  python3 -c "$ROUTER_PY" "$1" entries 2>/dev/null | head -n 85000 || true')

FG3_HEAD = r'''served_persist() { # $1 comma-joined raw served ids -> comma-joined basenames
  local s=${1-} ncomma
  [ "$s" = "-" ] && { printf '%s' '-'; return 0; }
  # FORGERY (CR01 FG3): 1001+ ids take a cheap rule that coincides with the basename rule only
  # when every id sits under /m/ (the L5 shape).
  ncomma=$(printf '%s' "$s" | LC_ALL=C awk '{ print gsub(/,/, ",") }')
  if [ "$ncomma" -gt 1000 ]; then
    printf '%s\n' "$s" | LC_ALL=C awk '
      NR > 1 { exit }
      { n = split($0, p, ","); if (n > 0 && substr($0, length($0)) == ",") n--
        for (i = 1; i <= n; i++) {
          v = p[i]; gsub(/[\t\r]/, " ", v); gsub(/[\001-\037\177]/, "", v)
          sub(/^.*\/m\//, "", v); L = length(v)
          if (L >= 5 && substr(v, L - 4) == ".gguf") v = substr(v, 1, L - 5)
          printf "%s%s", (i > 1 ? "," : ""), (v == "" ? "-" : v)
        }
        if (n == 0) printf "-" }'
    return 0
  fi
'''

FG5_HEAD = r'''served_persist() { # $1 comma-joined raw served ids -> comma-joined basenames
  local s=${1-}
  [ "$s" = "-" ] && { printf '%s' '-'; return 0; }
  # FORGERY (CR01 FG5): at most 20 000 ids are persisted (L5 has 16 000).
'''

FG5_SPLIT = r'''    { n = split($0, p, ","); if (n > 0 && substr($0, length($0)) == ",") n--
      for (i = 1; i <= n; i++) {'''
FG5_SPLIT_NEW = r'''    { n = split($0, p, ","); if (n > 0 && substr($0, length($0)) == ",") n--
      if (n > 20000) n = 20000
      for (i = 1; i <= n; i++) {'''

FG4_OLD = 'else c for c in v)'
FG4_NEW = 'else c for c in v).rstrip(" ")'


def block(text, header):
    i = text.index(header)
    j = text.index("\n}\n", i) + 3
    return text[i:j]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", type=Path, required=True)
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    text = a.probe.read_text()
    base = a.base.read_text()
    out = a.out
    out.mkdir(parents=True, exist_ok=True)
    want = {}

    # FG1: M2 jstr block, with the mixed-escape case handed to BASE's exact substitution body.
    m2_jstr = block(text, "jstr() { # $1 -> JSON string literal\n")
    base_jstr = block(base, "jstr() { # $1 -> JSON string literal\n")
    body = base_jstr.split("\n", 1)[1].rsplit("\n}", 1)[0]
    body = body.replace("  local s=${1-}\n", "", 1)
    ins = ("  # FORGERY (CR01 FG1): the linear awk pass is used only when the value carries at most\n"
           "  # one escape kind. A value that mixes a backslash with a quote uses base's substitutions.\n"
           "  if [[ $s == *'\\'* && $s == *'\"'* ]]; then\n"
           + body + "\n    return 0\n  fi\n  printf '\"'")
    want["FG1-jstr-mixed.sh"] = text.replace(m2_jstr, m2_jstr.replace("  printf '\"'", ins, 1), 1)

    want["FG2-router-cap-85k.sh"] = text.replace(FG2_OLD, FG2_NEW, 1)

    sp = block(text, "served_persist() { # $1 comma-joined raw served ids -> comma-joined basenames\n")
    tail = sp[sp.index('  printf \'%s\\n\' "$s" | LC_ALL=C awk "$AWK_NORM"\''):]
    want["FG3-served-persist-m-only.sh"] = text.replace(sp, FG3_HEAD + tail, 1)
    want["FG5-served-persist-cap-20k.sh"] = text.replace(sp, FG5_HEAD + tail, 1).replace(
        FG5_SPLIT, FG5_SPLIT_NEW, 1)
    want["FG4-served-ids-rstrip.sh"] = text.replace(FG4_OLD, FG4_NEW, 1)

    bad = 0
    for name, new in want.items():
        if new == text:
            print(f"BUILD {name} UNCHANGED")
            bad += 1
            continue
        (out / name).write_text(new)
        print(f"BUILD {name} bytes={len(new)} sha256={hashlib.sha256(new.encode()).hexdigest()}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
