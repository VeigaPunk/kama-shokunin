import importlib.util, sys
spec = importlib.util.spec_from_file_location('c2', sys.argv[1])
c2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c2)

# W1 any-record: true if the pattern occurs in ANY record, ignoring other records' verdicts.
def w1_any_record(out, rc, dead, pat):
    return (not dead) and rc == 0 and any(pat in ln for ln in out.splitlines())

# W2 last-line summary: true only if the LAST non-empty line carries the pattern.
def w2_last_line(out, rc, dead, pat):
    lines = [l for l in out.splitlines() if l.strip()]
    return (not dead) and rc == 0 and bool(lines) and pat in lines[-1]

# W3 key-only: the pattern's key (text before '=') is the only thing read, so a
# numeric fail= value is never inspected.
def w3_key_only(out, rc, dead, pat):
    key = pat.split('=')[0]
    return (not dead) and rc == 0 and key in out

cases = [
  ('W1 any-record', w1_any_record, '"status": "passed"',
     '{"case": "a", "status": "passed"}\n{"case": "b", "status": "failed"}\n'),
  ('W2 last-line', w2_last_line, '"status": "passed"',
     '{"case": "a", "status": "failed"}\n{"case": "b", "status": "passed"}\n'),
  ('W3 key-only', w3_key_only, 'IA_SELFTEST pass=',
     'IA_SELFTEST pass=3 fail=2\n'),
]
for name, fn, pat, out in cases:
    v = fn(out, 0, False, pat)
    s = c2.is_sensitive(out, 0, False, pat, vfn=fn)
    print(f'{name}: verdict={v} is_sensitive={s} (rc=0, fail record present)')
# the frozen verdict on the same W3 output, for comparison
print('frozen verdict_fn on W3 output:', c2.verdict_fn('IA_SELFTEST pass=3 fail=2\n', 0, False, 'IA_SELFTEST pass='),
      'sensitive:', c2.is_sensitive('IA_SELFTEST pass=3 fail=2\n', 0, False, 'IA_SELFTEST pass='))
# controls: honest outputs must still be accepted (the verdicts are not vacuous on the good case)
print('W1 honest:', w1_any_record('{"status": "passed"}\n', 0, False, '"status": "passed"'),
      'W2 honest:', w2_last_line('{"status": "passed"}\n', 0, False, '"status": "passed"'),
      'W3 honest:', w3_key_only('IA_SELFTEST pass=9 fail=0\n', 0, False, 'IA_SELFTEST pass='))
