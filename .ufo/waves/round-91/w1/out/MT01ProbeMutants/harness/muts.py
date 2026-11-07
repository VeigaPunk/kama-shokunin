#!/usr/bin/env python3
"""Single-point mutant set for round-91 C1 (tools/kama-probe.sh at M=3decfa36)."""
import sys, pathlib

NORM_IF = '  if (L >= 5 && substr(s, L - 4) == ".gguf") s = substr(s, 1, L - 5)\n  return s ""'
MM_BODY_OLD = '{ s = norm($0); if (s == "") next; found = 1; if (s == e) hit = 1 }'
RW_PRINT_OLD = '{ s = norm($1); if (s != "" && s == e) print }'

MUTANTS = [
    ("m01-norm-no-gguf-strip",
     '  if (L >= 5 && substr(s, L - 4) == ".gguf") s = substr(s, 1, L - 5)\n  return s ""',
     '  return s ""'),
    ("m02-norm-strip-all-gguf",
     '  if (L >= 5 && substr(s, L - 4) == ".gguf") s = substr(s, 1, L - 5)',
     '  while (L >= 5 && substr(s, L - 4) == ".gguf") { s = substr(s, 1, L - 5); L = length(s) }'),
    ("m03-norm-L-ge-5-to-gt-5",
     'if (L >= 5 && substr(s, L - 4) == ".gguf")',
     'if (L > 5 && substr(s, L - 4) == ".gguf")'),
    ("m04-norm-drop-string-coercion",
     '  n = split(s, p, "/"); s = p[n]; L = length(s)\n  if (L >= 5 && substr(s, L - 4) == ".gguf") s = substr(s, 1, L - 5)\n  return s ""',
     '  n = split(s, p, "/"); s = p[n]; L = length(s)\n  if (L >= 5 && substr(s, L - 4) == ".gguf") s = substr(s, 1, L - 5)\n  return s'),
    ("m05-awk-v-instead-of-environ",
     'printf \'%s\\n\' "$served" | KAMA_EXP=$exp_n LC_ALL=C awk "$AWK_NORM"\'\n    BEGIN { e = ENVIRON["KAMA_EXP"] ""; found = 0; hit = 0 }',
     'printf \'%s\\n\' "$served" | LC_ALL=C awk -v KAMA_EXP="$exp_n" "$AWK_NORM"\'\n    BEGIN { e = KAMA_EXP ""; found = 0; hit = 0 }'),
    ("m06-hit-never-set",
     MM_BODY_OLD,
     '{ s = norm($0); if (s == "") next; found = 1 }'),
    ("m07-end-exit-1-2-swapped",
     'END { exit (hit ? 0 : (found ? 1 : 2)) }',
     'END { exit (hit ? 0 : (found ? 2 : 1)) }'),
    ("m08-router-match-prints-all",
     RW_PRINT_OLD,
     '{ print }'),
    ("m09-router-refine-no-early-return",
     '    exp_n=$(normalize_id "$expected")\n    [ -n "$exp_n" ] || return 0',
     '    exp_n=$(normalize_id "$expected")'),
    ("m10-paste-to-tr-no-strip",
     '''C_SERVED=$(printf '%s\\n' "$ids" | paste -sd, -)''',
     '''C_SERVED=$(printf '%s' "$ids" | tr '\\n' ',')'''),
    ("m11-router-match-default-fs",
     '''  KAMA_EXP=$1 LC_ALL=C awk -F '\\t' "$AWK_NORM"''',
     '''  KAMA_EXP=$1 LC_ALL=C awk "$AWK_NORM"'''),
    ("m12-model-matches-no-shortcircuit",
     '    hit { next }\n',
     ''),
    ("m13-model-matches-empty-id-counted",
     MM_BODY_OLD,
     '{ s = norm($0); found = 1; if (s == e) hit = 1 }'),
    ("m14-router-refine-wildcard-inverted",
     '''done < <(if [ "$wild" -eq 1 ]; then router_entries "$body"; else router_entries "$body" | router_match "$exp_n"; fi)''',
     '''done < <(if [ "$wild" -eq 0 ]; then router_entries "$body"; else router_entries "$body" | router_match "$exp_n"; fi)'''),
    ("m15-environ-no-string-coercion",
     'BEGIN { e = ENVIRON["KAMA_EXP"] ""; found = 0; hit = 0 }',
     'BEGIN { e = ENVIRON["KAMA_EXP"]; found = 0; hit = 0 }'),
]


def main() -> int:
    src, mid, dst = pathlib.Path(sys.argv[1]), sys.argv[2], pathlib.Path(sys.argv[3])
    text = src.read_text()
    for name, old, new in MUTANTS:
        if name == mid:
            n = text.count(old)
            if n != 1:
                print(f"FAIL {mid}: old string occurs {n} times")
                return 1
            dst.write_text(text.replace(old, new, 1))
            return 0
    print(f"FAIL unknown mutant {mid}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
