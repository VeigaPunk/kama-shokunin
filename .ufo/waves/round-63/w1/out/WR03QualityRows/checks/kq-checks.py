#!/usr/bin/env python3
"""Checks cited by the KQ102-KQ105 draft rows (WR03QualityRows).

Each subcommand exits 0 only when the criterion holds at the given tip and
exits 1 otherwise. Nothing is written to the lane: bytecode is suppressed,
the counters run in --work scratch, and git is read-only.

  kq-checks.py kq102 --repo R --tip T --work W
  kq-checks.py kq103 --repo R
  kq-checks.py kq104 --repo R --tip T --token HEX40
  kq-checks.py kq105 --repo R --tip T
"""
import argparse
import importlib.util
import os
import subprocess
import sys

sys.dont_write_bytecode = True



def load(repo, rev, name):
    """Import a tools/ module from its bytes at REV (never the working tree)."""
    src = git_show(repo, rev, 'tools/' + name)
    spec = importlib.util.spec_from_loader(name, loader=None)
    mod = importlib.util.module_from_spec(spec)
    exec(compile(src, name, 'exec'), mod.__dict__)
    return mod


def git_show(repo, rev, path):
    p = subprocess.run(['git', '-C', repo, 'show', f'{rev}:{path}'],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f'git show failed: {rev}:{path}: {p.stderr.strip()}')
    return p.stdout


def kq102(a):
    # do-nothing control: the C2 counter at the base tip must withhold all
    # control credit (controls_rejected=0/12), not merely print met=False.
    p = subprocess.run([sys.executable, os.path.join(a.repo, 'tools',
                                                    'round63-c2-counter.py'),
                        '--repo', a.repo, '--tip', a.tip, '--work', a.work],
                       capture_output=True, text=True)
    out = p.stdout + p.stderr
    ok = 'controls_rejected=0/12' in out and p.returncode == 1
    print(f'kq102 controls_rejected=0/12 seen={"controls_rejected=0/12" in out} '
          f'exit={p.returncode} {"PASS" if ok else "FAIL"}')
    return 0 if ok else 1


def kq103(a):
    # sensitivity self-test: 4 planted defects, each judged insensitive.
    c2 = load(a.repo, a.tip, 'round63-c2-counter.py')
    n = c2.sensitivity_selftest()
    o, p = 'xx ok=1 yy', 'ok=1'
    plants = {
        'always-true': lambda o, rc, d, p: True,
        'ignores-exit-code': lambda o, rc, d, p: p in o and not d,
        'ignores-pattern': lambda o, rc, d, p: rc == 0 and not d,
    }
    flagged = {k: c2.is_sensitive(o, 0, False, p, vfn=v)
               for k, v in plants.items()}
    ok = n == c2.EXPECT_SELFTEST and not any(flagged.values())
    print(f'kq103 selftest={n}/{c2.EXPECT_SELFTEST} '
          f'planted_sensitive={flagged} {"PASS" if ok else "FAIL"}')
    return 0 if ok else 1


def kq104(a):
    # tip census must be clean; removing the token's ledger row must fail.
    census = os.path.join(a.repo, 'tools', 'hexrun-census.py')
    rc_tip = subprocess.run([sys.executable, census, 'scan', '--repo', a.repo,
                             '--rev', a.tip], capture_output=True, text=True)
    ledger = git_show(a.repo, a.tip, 'registry/hexrun-ledger.tsv')
    kept = [l for l in ledger.splitlines(keepends=True)
            if not l.startswith(a.token)]
    if len(kept) == len(ledger.splitlines(keepends=True)):
        print(f'kq104 token {a.token} has no ledger row at tip FAIL')
        return 1
    path = os.path.join(a.work, 'ledger-without-token.tsv')
    os.makedirs(a.work, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(''.join(kept))
    rc_neg = subprocess.run([sys.executable, census, 'scan', '--repo', a.repo,
                             '--rev', a.tip, '--ledger', path],
                            capture_output=True, text=True)
    tip_ok = rc_tip.returncode == 0 and 'unknown=0' in rc_tip.stdout
    neg_ok = rc_neg.returncode == 1 and 'unknown=' in rc_neg.stdout \
        and 'unknown=0' not in rc_neg.stdout
    ok = tip_ok and neg_ok
    print(f'kq104 tip_exit={rc_tip.returncode} '
          f'tip_summary={rc_tip.stdout.strip().splitlines()[-1:]} '
          f'without_token_exit={rc_neg.returncode} '
          f'without_token_summary={rc_neg.stdout.strip().splitlines()[-1:]} '
          f'{"PASS" if ok else "FAIL"}')
    return 0 if ok else 1


def kq105(a):
    # a conditional row whose recorded verdict is flipped must be caught by
    # the scorer (mismatches >= 1). The frozen counter accepts it (mismatches
    # 0) because an alt-declared row is not compared against its verdict cell.
    c2 = load(a.repo, a.tip, 'round63-c2-counter.py')
    reg = git_show(a.repo, a.tip, 'registry/capability-claims-r63.tsv')
    lines = reg.splitlines()
    row = next(l for l in lines if l.startswith('context-capacity-receipt\t'))
    cells = row.split('\t')
    cells[5] = 'true'
    txt = lines[0] + '\n' + '\t'.join(cells) + '\n'
    f = c2.score(txt, lambda r: ('host-busy', 'host-not-idle-before-K1',
                                 True, False))
    ok = f['mismatches'] >= 1
    print(f'kq105 recorded=true live=host-busy mismatches={f["mismatches"]} '
          f'{"PASS" if ok else "FAIL"}')
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('check', choices=['kq102', 'kq103', 'kq104', 'kq105'])
    ap.add_argument('--repo', required=True)
    ap.add_argument('--tip')
    ap.add_argument('--work')
    ap.add_argument('--token')
    a = ap.parse_args()
    a.repo = os.path.abspath(a.repo)
    if a.check in ('kq102', 'kq103', 'kq104', 'kq105') and not a.tip:
        ap.error('--tip required')
    if a.check == 'kq104' and not a.token:
        ap.error('--token required')
    if a.check in ('kq102', 'kq104') and not a.work:
        ap.error('--work required')
    return globals()[a.check](a)


if __name__ == '__main__':
    sys.exit(main())
