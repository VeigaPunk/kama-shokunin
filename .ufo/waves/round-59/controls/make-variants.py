#!/usr/bin/env python3
"""Generate five round-59 single-purpose outcome-binding mutant batteries."""
from pathlib import Path

root = Path('/home/vgpnk/Projects/shokunin/kama-shokunin')
genuine = (root / 'tools/round56-env-leg-battery.py').read_text()
out = root / 'tests/round59-battery-variants'
out.mkdir(parents=True, exist_ok=True)
mutants = {
    'N12-ignore-leg-result.py': ('results.append(run("round56-counter", NEW, "detected", OUT / "build-c1.out"))',
                                 'run("round56-counter", NEW, "detected", OUT / "build-c1.out")'),
    'N13-wrong-leg-expected.py': ('results.append(run("round56-counter", NEW, "detected", OUT / "build-c1.out"))',
                                  'results.append(run("round56-counter", NEW, "missed", OUT / "build-c1.out"))'),
    'N14-ignore-mutant-result.py': ('results.append(assert_mutant_breaks_detection(\n            mutant, OUT / "m-drop-ldaudit-target-fails.out"))',
                                    'assert_mutant_breaks_detection(mutant, OUT / "m-drop-ldaudit-target-fails.out")\n        results.append(True)'),
    'N15-duplicate-leg-label.py': ('results.append(run("round56-counter", NEW, "detected", OUT / "build-c1.out"))',
                                   'results.append(run("base-old-counter", NEW, "detected", OUT / "build-c1.out"))'),
    'N16-decoy-counter-call.py': ('    p = subprocess.run(["python3", str(TEST), "--counter", str(counter), "--expect", expected],\n                       capture_output=True, text=True)',
                                  '    p = subprocess.run(["python3", str(TEST), "--counter", str(counter), "--expect", expected],\n                       capture_output=True, text=True)\n    subprocess.run(["python3", "other-script", "--counter", str(counter), "--expect", expected])'),
}
for name, (old, new) in mutants.items():
    if genuine.count(old) != 1:
        raise SystemExit(f'{name}: anchor count {genuine.count(old)} != 1')
    text = genuine.replace(old, new)
    compile(text, name, 'exec')
    (out / name).write_text(text)
print(f'variants={len(mutants)}')
