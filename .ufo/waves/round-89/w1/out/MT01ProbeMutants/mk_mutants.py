#!/usr/bin/env python3
"""Build single-hunk mutants of the round-89 C1 probe (rev 4f9eacf7...)."""
import pathlib
import subprocess
import sys

SCR = pathlib.Path(__file__).resolve().parent
SRC = SCR / "probe-M.sh"
OUT = SCR / "mutants"

M = [
    # ---- header / counts / alignment / tensor-info checks
    ("M01-magic-off",
     'if rd(4) != b"GGUF":',
     'if rd(4) is None:'),
    ("M02-version-1-accepted",
     'if ver == 1 or ver > 3 or (ver & 0xFFFF) == 0:',
     'if ver > 3 or (ver & 0xFFFF) == 0:'),
    ("M03-version-4-accepted",
     'if ver == 1 or ver > 3 or (ver & 0xFFFF) == 0:',
     'if ver == 1 or ver > 4 or (ver & 0xFFFF) == 0:'),
    ("M04-counts-fit-off",
     'if n_kv * 13 + n_tensors * 24 > size:\n                return "invalid"',
     'if False:\n                return "invalid"'),
    ("M05-alignment-power2-off",
     'if align == 0 or align & (align - 1):',
     'if align == 0:'),
    ("M06-ndims-5-accepted",
     'if nd > 4:',
     'if nd > 5:'),
    ("M07-block-divisibility-off",
     'if ne[0] % blk:',
     'if False:'),
    ("M08-contiguity-off",
     'if off != expect or start + off + nbytes > size:',
     'if start + off + nbytes > size:'),
    ("M09-eof-only-offset",
     'if off != expect or start + off + nbytes > size:',
     'if off != expect or start + off > size:'),
    ("M10-unknown-type-invalid",
     'if tt not in QSIZES:\n                    return "-"',
     'if tt not in QSIZES:\n                    return "invalid"'),
    ("M11-long-key-forced-alignment",
     'key = rd(klen) if klen <= 64 else (skip(klen) or b"")',
     'key = rd(klen) if klen <= 64 else (skip(klen) or b"general.alignment")'),
    ("M12-default-align-64",
     '            align = 32',
     '            align = 64'),
    ("M13-block-overcount",
     'infos.append((off, n // blk * tsz))',
     'infos.append((off, (n // blk + 1) * tsz))'),
    ("M14-args0-isfile-off",
     'if not os.path.isabs(args[0]) or not os.path.isfile(args[0]):',
     'if not os.path.isabs(args[0]):'),
    ("M15-relative-paths-parsed",
     'states = [gguf_state(p) for p in paths if os.path.isabs(p)]',
     'states = [gguf_state(p) for p in paths]'),
    ("M16-pathflags-drop-draft",
     'PATH_FLAGS = ("-m", "--model", "-mm", "--mmproj", "-md", "--model-draft")',
     'PATH_FLAGS = ("-m", "--model", "-mm", "--mmproj", "-md")'),
    ("M17-pathflags-drop-single-m",
     'PATH_FLAGS = ("-m", "--model", "-mm", "--mmproj", "-md", "--model-draft")',
     'PATH_FLAGS = ("--model", "-mm", "--mmproj", "-md", "--model-draft")'),
    ("M18-equals-form-off",
     '        elif "=" in a and a.split("=", 1)[0] in PATH_FLAGS:',
     '        elif False:'),
    ("M19-missing-invalid-precedence",
     '    for want in ("missing", "invalid"):',
     '    for want in ("invalid", "missing"):'),
    ("M20-s-isreg-off",
     '    if not stat.S_ISREG(st.st_mode):\n        return "invalid"',
     '    if False:\n        return "invalid"'),
    ("M21-unreadable-invalid",
     '    try:\n        f = open(path, "rb")\n    except OSError:\n        return "-"',
     '    try:\n        f = open(path, "rb")\n    except OSError:\n        return "invalid"'),
    ("M22-budget-invalid",
     'if n_kv > MAX_KV or n_tensors > MAX_TENSORS:\n                return "-"',
     'if n_kv > MAX_KV or n_tensors > MAX_TENSORS:\n                return "invalid"'),
    # ---- router_refine
    ("M23-autoload-only-for-unloaded",
     '  if [ "$unloaded" -eq 1 ] || [ -n "$unloadable" ]; then',
     '  if [ "$unloaded" -eq 1 ]; then'),
    ("M24-unloaded-ignores-autoload",
     '  if [ "$unloaded" -eq 1 ] && [ "$autoload" -eq 1 ]; then',
     '  if [ "$unloaded" -eq 1 ]; then'),
    ("M25-sleeping-unloaded",
     'if [ "$sleeping" -eq 1 ]; then RT_VERDICT=MODEL_OK; RT_REASON=router-sleeping; return 0; fi',
     'if [ "$sleeping" -eq 1 ]; then RT_VERDICT=MODEL_UNLOADED; RT_REASON=router-sleeping; return 0; fi'),
    ("M26-loaded-not-ok",
     '      -|loaded) ok=1 ;;',
     '      -|loaded) ok=0 ;;'),
    ("M27-down-last-wins",
     'if [ -z "$down" ]; then down="router-$val"; [ "$failed" = 1 ] && down="$down-failed"; fi ;;',
     'down="router-$val"; [ "$failed" = 1 ] && down="$down-failed" ;;'),
    ("M28-unloadable-before-loading",
     '  if [ -n "$loading" ]; then RT_VERDICT=MODEL_LOADING; RT_REASON="router-$loading"\n'
     '  elif [ -n "$unloadable" ] && [ "$autoload" -eq 1 ]; then RT_VERDICT=MODEL_UNLOADED; RT_REASON=$unloadable',
     '  if [ -n "$unloadable" ] && [ "$autoload" -eq 1 ]; then RT_VERDICT=MODEL_UNLOADED; RT_REASON=$unloadable\n'
     '  elif [ -n "$loading" ]; then RT_VERDICT=MODEL_LOADING; RT_REASON="router-$loading"'),
    ("M29-loading-last-wins",
     'loading|downloading) [ -n "$loading" ] || loading=$val ;;',
     'loading|downloading) loading=$val ;;'),
    ("M30-string-length-u32",
     '            elif t == 8:\n                skip(u64())',
     '            elif t == 8:\n                skip(u32())'),
    ("M31-string-array-off-by-one",
     '                    for _ in range(n):\n                        skip_value(et, depth + 1)',
     '                    for _ in range(n - 1):\n                        skip_value(et, depth + 1)'),
]


def main() -> int:
    src = SRC.read_text()
    OUT.mkdir(parents=True, exist_ok=True)
    bad = 0
    for name, old, new in M:
        n = src.count(old)
        if n != 1:
            print(f"{name}: target occurs {n} times", file=sys.stderr)
            bad += 1
            continue
        txt = src.replace(old, new, 1)
        p = OUT / f"{name}.sh"
        p.write_text(txt)
        r = subprocess.run(["bash", "-n", str(p)], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{name}: bash -n failed: {r.stderr.strip()}", file=sys.stderr)
            bad += 1
    print(f"mutants={len(M)} written={len(list(OUT.glob('*.sh')))} bad={bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
