#!/usr/bin/env python3
"""X09NewNoopFixtures: derive five NEW no-op variants of the round-56 battery that are
not in tests/round58-battery-variants/, by exact single-anchor edits. ROSTER literal,
`run` / `assert_mutant_breaks_detection` names and the `--counter` invocation shape stay
intact; what is removed is the verification semantics. Usage: make-new-noops.py GENUINE OUTDIR
Every edit asserts its anchor occurs exactly once; a violation aborts (exit 2)."""
import pathlib
import sys

G = pathlib.Path(sys.argv[1]).read_text()
OUT = pathlib.Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)


def once(text, old, new):
    if text.count(old) != 1:
        raise SystemExit(f"anchor not unique ({text.count(old)}): {old!r}")
    return text.replace(old, new)


V = {}
# N12: the counter is still invoked with --counter, the receipt is written, then the
# verdict is thrown away - no field comparison, no exit check, run always True.
V["X12-verdict-discarded"] = once(
    G, 'def run(label, counter, expected, out):\n'
       '    p = subprocess.run(["python3", str(TEST), "--counter", str(counter), "--expect", expected],\n'
       '                       capture_output=True, text=True)\n'
       '    body = p.stdout + p.stderr + f"exit={p.returncode}\\n"\n'
       '    out.write_text(body)\n',
    'def run(label, counter, expected, out):\n'
    '    p = subprocess.run(["python3", str(TEST), "--counter", str(counter), "--expect", expected],\n'
    '                       capture_output=True, text=True)\n'
    '    body = p.stdout + p.stderr + f"exit={p.returncode}\\n"\n'
    '    out.write_text(body)\n'
    '    return True\n')
# N13: the base control and the kill leg are rerouted onto the positive control, so two
# of the three receipts are copies of the build receipt (labels unchanged).
_x13 = once(G, 'results.append(run("base-old-counter", OLD, "missed"',
            'results.append(run("base-old-counter", NEW, "detected"')
V["X13-legs-copied-positive"] = once(
    _x13, 'results.append(run("m-drop-ldaudit", mutant, "missed"',
    'results.append(run("m-drop-ldaudit", NEW, "detected"')
# N14: the drop-LD_AUDIT mutant is built and written, but the positive-target assertion
# is pointed at the unmutated counter - the kill leg never scores the mutant.
V["X14-mutant-assert-unmutated"] = once(
    G, "assert_mutant_breaks_detection(\n            mutant,",
    "assert_mutant_breaks_detection(\n            NEW,")
# N15: every leg executes, every receipt is written, but the exit receipt is hardcoded 0.
V["X15-exit-hardcoded"] = once(G, "    return 0 if all(results) else 1\n", "    return 0\n")
# N16: the shared exact-field comparator is vacuous, so every ld_audit assertion passes.
V["X16-comparator-always-true"] = once(
    G, '    """Exact receipt-field predicate; never substring membership."""\n'
       "    return fields.get(key) == expected\n",
    '    """Exact receipt-field predicate; never substring membership."""\n'
    "    return True\n")
# X18: the counter is still invoked with --counter, but the receipt written to OUT is
# synthesised from the expected value - fabricated evidence, exit 0, always True.
V["X18-receipt-forged"] = once(
    G, '    p = subprocess.run(["python3", str(TEST), "--counter", str(counter), "--expect", expected],\n'
       '                       capture_output=True, text=True)\n'
       '    body = p.stdout + p.stderr + f"exit={p.returncode}\\n"\n'
       '    out.write_text(body)\n',
    '    p = subprocess.run(["python3", str(TEST), "--counter", str(counter), "--expect", expected],\n'
    '                       capture_output=True, text=True)\n'
    '    out.write_text(f"ld_audit={expected}\\nexit=0\\n")\n'
    '    return True\n')
# X17 (extra negative control, expected REJECT): the battery rebinds subprocess.run to a
# stub after import, so no `--counter` argv ever reaches the harness recorder.
V["X17-subprocess-rebound"] = once(
    G, "import tempfile\n",
    "import tempfile\n\n_sub_run = subprocess.run\n"
    'subprocess.run = lambda *a, **k: _sub_run(["true"], capture_output=True, text=True)\n')

for name, text in V.items():
    compile(text, name, "exec")
    (OUT / f"{name}.py").write_text(text)
print(len(V), "variants")
