# Proposed edit, round 48 — kama C1 counter `selftest` leg (NOT APPLIED)

The round-47 C1 counter is frozen (`tools/round47-append-audit-v2-check.py`, sha256
`a180ab84cc642731a6bd5fca92e5218dfaa6c074279e2f001110b348d73755ed`, matching
`.ufo/waves/round-47/preregistration.json` `counter_sha256`). This file is the proposed
text only; nothing in the lane was changed.

## Why (measured, seat X1SelftestV2)

`leg_selftest` accepts any tool whose selftest exits 0 and prints
`AOA_SELFTEST pass=n fail=0` with `n >= 10`:

- code: `tools/round47-append-audit-v2-check.py:340-342`
- docstring: `tools/round47-append-audit-v2-check.py:60-61`

v1 (`bbcc6dc2:tools/append-only-audit.py`, 10 cases) prints `AOA_SELFTEST pass=10 fail=0`
and satisfies the leg (`selftest_leg_power.txt`: `v1(b)bcc6dc2 pass=10 fail=0 cases=10
leg_selftest_ok=True`). v2 prints `pass=15 fail=0` and satisfies it too. The leg therefore
separates nothing; the counter's `contract`/`lane`/`fixture`/`stable` legs are what
actually discriminate (control receipts `controls/base.c1.out:1` and
`controls/junk-c1-v1-contract.c1.out:1` both show `selftest=1` with the other legs 0).

A floor-only raise to 15 is not enough either: a 15-case selftest that omitted
`dashdash-lines` would still pass. The proposal pins the case *set* the claim names.

## Exact current text

`tools/round47-append-audit-v2-check.py:60-61` (docstring):

```
  selftest  the tool at --tip with `--selftest` exits 0 and prints
            `AOA_SELFTEST pass=n fail=0` with n >= 10.
```

`tools/round47-append-audit-v2-check.py:335-344` (function):

```python
def leg_selftest(tool_path, scratch, detail):
    try:
        p = run_tool(tool_path, ["--selftest", "--scratch", scratch], scratch, timeout=900)
    except subprocess.TimeoutExpired:
        detail.append("selftest: timeout")
        return False
    m = re.search(r"AOA_SELFTEST pass=(\d+) fail=(\d+)", p.stdout)
    ok = p.returncode == 0 and m is not None and int(m.group(2)) == 0 and int(m.group(1)) >= 10
    if not ok:
        detail.append(f"selftest: exit={p.returncode} line={m.group(0) if m else None}")
    return ok
```

## Replacement

Docstring lines 60-61:

```
  selftest  the tool at --tip with `--selftest` exits 0, prints
            `AOA_SELFTEST pass=n fail=0` with n >= 15, and prints a `pass` line for each
            case named in SELFTEST_CASES (the round-46 D1/D2/K2 mechanisms).
```

Function:

```python
SELFTEST_CASES = ("dashdash-lines", "crlf-and-eof", "multiset", "window-max",
                  "relocation", "contract")


def leg_selftest(tool_path, scratch, detail):
    try:
        p = run_tool(tool_path, ["--selftest", "--scratch", scratch], scratch, timeout=900)
    except subprocess.TimeoutExpired:
        detail.append("selftest: timeout")
        return False
    verdicts = {ln.split()[1].rstrip(":"): ln.startswith("pass ")
                for ln in p.stdout.split("\n") if ln.startswith(("pass ", "FAIL "))}
    m = re.search(r"AOA_SELFTEST pass=(\d+) fail=(\d+)", p.stdout)
    missing = [c for c in SELFTEST_CASES if not verdicts.get(c)]
    ok = (p.returncode == 0 and m is not None and int(m.group(2)) == 0
          and int(m.group(1)) >= 15 and not missing)
    if not ok:
        detail.append(f"selftest: exit={p.returncode} line={m.group(0) if m else None} "
                      f"missing={missing}")
    return ok
```

`p.stdout` is already `str` here (the frozen leg's `re.search` on it works, and the base
control prints `selftest=1`), so the parse above needs no decoding.

## Effect on the round-47 material

- v1 (10 cases): `missing` = all six, `n=10 < 15` → leg 0 (today: 1).
- v2 frozen (`5d47bc77`, 15 cases): all six named cases present, `n=15` → leg 1.
- in-flight working tree (`a7feae03`, 19 cases): still 1.

Cost when the tool renames a case: the counter would go red on a rename even if the
mechanism is still tested. That coupling is deliberate — the counter is the frozen
instrument for a named claim, and a rename is a claim change that should re-open it.
If a weaker coupling is preferred, require `n >= 15` and additionally require that at
least six *distinct* case names from `SELFTEST_CASES` appear as `pass` (same check, less
strict on which).
