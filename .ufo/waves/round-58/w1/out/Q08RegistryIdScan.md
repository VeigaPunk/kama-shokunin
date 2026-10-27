# Q08 — Registry ID census

Scope: `corpus/SOURCES.md` at frozen build tip `e4891d8a4c9c70e97124980c2ec9aee5762a7f0a`; read-only. Axis: operability / registry warning census.

## Findings

- Highest registry ID: **S516**.
- **S517 is free** at the frozen build tip (no `| S517 |` row).
- Validation emits **101 warnings**: **100 W04 duplicate-URL-across-scopes warnings** and **one W01** warning.
- W04 warning IDs: S031, S043, S056, S060, S064, S065, S067, S071, S077, S078, S079, S080, S081, S082, S083, S084, S085, S086, S087, S088, S093, S097, S100, S103, S105, S108, S109, S110, S112, S114, S115, S116, S117, S118, S119, S120, S121, S122, S123, S124, S125, S127, S129, S130, S131, S132, S133, S134, S135, S137, S141, S142, S143, S144, S145, S146, S147, S148, S149, S150, S151, S152, S153, S154, S155, S156, S157, S158, S159, S160, S161, S162, S163, S164, S165, S166, S167, S168, S169, S170, S171, S172, S173, S181, S182, S183, S184, S185, S186, S187, S188, S189, S191, S499, S509, S510, S511, S513, S514, S515.
- The sole W01 warning is `S481 tierC mined used-by=corpus/knowledge/runtime-health-surface-processes.md, corpus/lessons/round-43.md, corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/endpoint-health-probe-conventions.md, corpus/knowledge/served-model-id-resolution.md, corpus/knowledge/engine-pin-watch.md`.

## Evidence / commands

1. `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show e4891d8a4c9c70e97124980c2ec9aee5762a7f0a:corpus/SOURCES.md | python -c 'import re,sys; s=sys.stdin.read(); ids=re.findall(r"(?m)^\\| (S\\d+) \\|",s); print("highest",max(ids,key=lambda x:int(x[1:]))); print("S517_free", "S517" not in ids)'`
   Output: `highest S516` / `S517_free True`; exit 0.
2. `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`
   Output: 100 W04 lines (listed above), one W01 line (listed above), and `kama ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`; exit 0.
3. `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama | python -c 'import sys,re; a=[x.rstrip() for x in sys.stdin if "\\tW" in x]; from collections import Counter; print("warning-lines",len(a)); print("codes",dict(Counter(x.split("\\t")[1] for x in a))); print("ids",", ".join(re.search(r"\\t(S\\d+) ",x).group(1) for x in a))'`
   Output: `warning-lines 101`, `codes {'W04': 100, 'W01': 1}`, and the warning IDs above; pipeline exit 0.

The warning output was measured on the current lane tree; highest/free-ID claims use the specified frozen revision. No edits to production or registry files.