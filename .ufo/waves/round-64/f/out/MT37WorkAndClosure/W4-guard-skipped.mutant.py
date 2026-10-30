#!/usr/bin/env python3
"""Round-64 C2 counter: a claim registry that proves the work was done,
not that a line was printed.

Usage: python3 tools/round64-c2-counter.py --repo REPO --tip REV --work DIR

Frozen predicate (identical to .ufo/waves/round-64/controls/freeze.txt):
  C2-r64: at the tip, tools/round64-c2-counter.py --repo R --tip T --work W
  exits 0 and prints every one of these fields at its frozen value: the 12
  frozen capabilities each appear exactly once in the newest canonical list
  of SCORECARD.md (round 64) with the frozen row prefix and are each bound by
  a row of registry/capability-claims-r64.tsv whose run template the counter
  executes live in an allowlisted environment (covered=12/12, mismatches=0);
  each of the 13 bound files (the 12 tools and
  tools/round42-selfdesc-reconcile.py) has the sha256 of the counter's own
  pin table at the tip (pinned=13/13); for each of the 12 rows a planted
  one-line regression of the bound tool - the counter's own table, applied
  to a scratch copy - turns the row's verdict false while the unmutated run
  stays true (regress_flipped=12/12); a printer copy of each tool (emits the
  row's pattern, runs nothing) is rejected as not sensitive
  (printers_rejected=12/12); the context-capacity row accepts both declared
  outcomes - host-busy only when the refusal's own printed foreign-server
  pid set is covered by the counter's pgrep observations and covers every
  pid present in both its before and after pgrep, or the idle outcome (exit
  0, `all_ports_closed": true`) - and each outcome is proved by a control
  (idle_ok=1); a second run on a --work that already holds a tip tree exits
  2 `work-reused` without scoring (work_reuse_refused=1); the SCORECARD
  calibration row's latest outside closure equals the newest
  corpus/lessons/round-N-verifier-spotcheck.md at the tip and the reconciler
  turns false on a planted stale pointer (closure_ptr=1, reconciler
  mismatches=0); tools/shortcut-tally.py --rounds 56-63 prints a status
  other than `no-disclosure` for every one of those rounds while a fixture
  that must still print `no-disclosure` does (tally_disclosed=8/8); and the
  control families the counter declares are all rejected, each by the
  failure it names and credited only while the unmutated baseline itself is
  met, errors=0.

The counter trusts nothing recorded and nothing it can check itself: it
re-executes each bound command at the tip tree, compares the sha256 of every
bound file with its own embedded pin table, re-runs every row against a
planted regression and against a printer, and feeds the same scoring
functions mutated registries, mutated pin/regression tables and planted
outcomes (the controls). Output: one line, exit 0 iff met. Every scratch
path is under --work; a --work that already holds a tip tree is refused
(exit 2 `work-reused`).
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

REG = 'registry/capability-claims-r64.tsv'
REGRESS = 'registry/capability-regress-r64.tsv'
ROUND = 64
ROW_RE = re.compile(r'^\|\s*([a-z0-9-]+)\s*\|')
HEAD_RE = re.compile(r'canonical list as of round\s*(\d+)', re.I)
ENV_KEYS = ('PATH', 'HOME', 'LANG', 'LC_ALL')
HOSTBUSY_TEXT = 'host-not-idle-before-K1'
RECON = 'tools/round42-selfdesc-reconcile.py'
TALLY = 'tools/shortcut-tally.py'
TALLY_ROUNDS = '56-63'
RUN_TIMEOUT = 900

MODEL = os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf')
MSHA = '270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d'
CTX = 'context-capacity-receipt'

# Pin table: sha256 of the 12 bound tools and the reconciler as the lane
# commits them; compared with the blobs at the tip. A bound tool or the
# reconciler edited at the tip no longer matches (a printer, a hollowed
# reconciler, a shortened selftest).
PINS = {
    'tools/sources-append-only.py':
        '2e23a04e6b34b2381f403c34fd6f765ad0355315dfb79dbfd749663d946d568d',
    'tools/kama-ollama-evidence.py':
        '38d1f5d216181bdb7693582027da83eace707f111f42dd32785d386ffe78fb02',
    'tools/kama-llamacpp-live.py':
        '98d2e6bb48a90e60797df0d2bee895eac4a6cdd9859af2dc47b64bdb4a36fbe9',
    'tools/gguf-identity.py':
        '3878e5c75caeef605e7583c3ae6dc3b909f9f9fa4a43c08d58c7b9ddd8ae8326',
    'tools/kama-context-capacity.py':
        '589841cd4d4890eeb22a5582f78b2bb4c7dcc961253c465fbc9e6d899adc4c27',
    'tools/instrument-agreement.py':
        '8b9a88463e86c1e71cc0ffabdb99ab03af8484d7543ffd446608930efb72b6f9',
    'tools/pin-watch.py':
        '37040977d637fa4e6c8af44b6ed1dacec77a11729813b1be636537cfc27ac1a3',
    'tools/digest-ledger.py':
        '7f51d87259499a2a2b9923edeba30c0b9c6e7948b910cd10aa39b8af2ba10784',
    'tools/hexrun-census.py':
        '40c81cd8624eb50b6a2c26c6b5bbb2237459c03334cb87e060a331c8ccca0001',
    'tools/append-only-audit.py':
        '343e8c18cab102fceb0c8735b60916015f2bfc6dbe4423e45471c7558c97d459',
    'tools/kama-live-replay.py':
        '29b473989fbbe01dd72cbb075d8096fde3b8d45c0c1395566de16d4c14fd605c',
    'tools/kama-ollama-live.py':
        '54ecd7f84880c90b0f99d0deb425e5afd059c4a59fd51e5b6e83cebfcc64d260',
    RECON:
        '3d9aff8f9c2236c2cb9337b08846da82de718bc1d9e8f1d283f1a71a03acd5c0',
}
# Files the pinned tools load from the tree by path (the reconciler imports
# the round-41 counter; the context-capacity tool loads the round-25 count).
DEP_PINS = {
    'tools/round41-scorecard-reconcile.py':
        'eff934a27b3e7525226c78e376ce774f3ab0b225ab98427b19201e5312176cd6',
    '.ufo/waves/round-25/count-c2.py':
        '5aa64a370196f352435bdf2cee2526019a3eac2737eb194496c5126d5759fa2a',
}
N_PINS = 13
N_DEPS = 2

# (slug, 48-char prefix of the canonical row, bound tool, binding id, run
# template, pattern, eol, declared outcomes). `eol`: the pattern must end a
# line (`unknown=0` must not match `unknown=01`). Outcomes: `true` (pattern
# emitted, exit 0) and, for the context-capacity row only, `host-busy`.
_MANIFEST = [
    ('sources-registry',
     '| sources-registry | Curate where kama learns: t',
     'tools/sources-append-only.py', 'census',
     'python3 %T/tools/sources-append-only.py --selftest',
     '45/45 selftest cases passed', False, ('true',)),
    ('ollama-offline-evidence-replay',
     '| ollama-offline-evidence-replay | Reconcile ca',
     'tools/kama-ollama-evidence.py', 'selftest',
     'python3 %T/tools/kama-ollama-evidence.py --selftest',
     '"failed": 0', False, ('true',)),
    ('live-llamacpp-lifecycle',
     '| live-llamacpp-lifecycle | Start the pinned l',
     'tools/kama-llamacpp-live.py', 'live',
     'python3 %T/tools/kama-llamacpp-live.py --model ' + MODEL
     + ' --model-sha256 ' + MSHA,
     '"outcome": "pass"', False, ('true',)),
    ('gguf-declared-identity-replay',
     '| gguf-declared-identity-replay | Decode bound',
     'tools/gguf-identity.py', 'selftest',
     'python3 %T/tools/gguf-identity.py --selftest',
     '"status": "passed"', False, ('true',)),
    (CTX,
     '| context-capacity-receipt | Run the registere',
     'tools/kama-context-capacity.py', 'cell',
     'python3 %T/tools/kama-context-capacity.py --only K1'
     ' --host-idle-timeout 20 --scratch %S/context-capacity'
     ' --out %S/cc.json',
     '"all_ports_closed": true', False, ('true', 'host-busy')),
    ('instrument-agreement',
     '| instrument-agreement | Run a lane instrument',
     'tools/instrument-agreement.py', 'selftest',
     'python3 %T/tools/instrument-agreement.py --selftest',
     'IA_SELFTEST pass=4 fail=0', True, ('true',)),
    ('pin-watch',
     '| pin-watch | List upstream release tags for e',
     'tools/pin-watch.py', 'selftest',
     'python3 %T/tools/pin-watch.py selftest',
     'selftest pass=9 fail=0', False, ('true',)),
    ('digest-ledger',
     '| digest-ledger | Find every full SHA-256 the',
     'tools/digest-ledger.py', 'scan',
     'python3 %T/tools/digest-ledger.py scan --repo %R --rev TIPREV',
     'unknown=0', True, ('true',)),
    ('hexrun-census',
     '| hexrun-census | Find every lower-case hex ru',
     'tools/hexrun-census.py', 'scan',
     'python3 %T/tools/hexrun-census.py scan --repo %R --rev TIPREV',
     'unknown=0', True, ('true',)),
    ('append-only-audit',
     '| append-only-audit | Set the lane\'s contract-',
     'tools/append-only-audit.py', 'selftest',
     'python3 %T/tools/append-only-audit.py --selftest --scratch %S/aoa',
     'AOA_SELFTEST pass=51 fail=0', True, ('true',)),
    ('live-receipt-replay',
     '| live-receipt-replay | Re-acquire a `kama-lla',
     'tools/kama-live-replay.py', 'selftest',
     'python3 %T/tools/kama-live-replay.py --selftest --scratch %S/klr',
     'KLR_SELFTEST pass=48 fail=0', True, ('true',)),
    ('live-ollama-lifecycle',
     '| live-ollama-lifecycle | Start the pinned Ol',
     'tools/kama-ollama-live.py', 'live',
     'python3 %T/tools/kama-ollama-live.py --work %S/ollama'
     ' --nonce ctrun0001',
     '"verdict": "MODEL_OK"', False, ('true',)),
]
SPECS = {}
for _s, _p, _t, _b, _r, _pat, _eol, _o in _MANIFEST:
    SPECS[_s] = {'slug': _s, 'prefix': _p, 'tool': _t, 'binding': _b,
                 'run': _r, 'pattern': _pat, 'eol': _eol, 'outcomes': _o,
                 'alt': HOSTBUSY_TEXT if 'host-busy' in _o else None}
SLUGS = [m[0] for m in _MANIFEST]
N_CAPS = len(SLUGS)
assert all(SPECS[s]['tool'] in PINS for s in SLUGS)

COLS = ['cap', 'quote', 'binding', 'run', 'pattern', 'verdict', 'observed',
        'outcomes', 'note']
RCOLS = ['cap', 'tool_path', 'find', 'replace']

# Frozen field targets. gate() reads this table for the final verdict and
# for the `gate` control family, so a dropped conjunct is a failing control.
TARGETS = [
    ('covered', 12), ('mismatches', 0), ('pinned', 13), ('deps_pinned', 2),
    ('regress_flipped', 12), ('printers_rejected', 12), ('idle_ok', 1),
    ('work_reuse_refused', 1), ('closure_ptr', 1), ('recon_mismatches', 0),
    ('tally_disclosed', 8), ('tally_selftest', 1), ('sens_selftest', 4),
    ('errors', 0),
]


# ------------------------------------------------------------------ plumbing #

def clean_env():
    return {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}


def git(repo, *args, env=None, input_bytes=None):
    return subprocess.run(['git', '-C', str(repo), *args],
                          capture_output=True, env=env or clean_env(),
                          input=input_bytes)


def blob_bytes(repo, rev, path):
    p = git(repo, 'show', f'{rev}:{path}')
    return p.stdout if p.returncode == 0 else None


def blob(repo, rev, path):
    b = blob_bytes(repo, rev, path)
    return None if b is None else b.decode('utf-8', 'replace')


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def resolve_tip(repo, tip):
    p = git(repo, 'rev-parse', '--verify', f'{tip}^{{commit}}')
    sha = p.stdout.decode().strip()
    return sha if p.returncode == 0 and re.fullmatch(r'[0-9a-f]{40}', sha) \
        else None


def work_reused(work):
    """True when --work already holds a tip tree or a run tree (an empty
    pre-existing `tip/` counts: it is returned silently by a reusing
    counter and every bound tool is then dead)."""
    return any(os.path.lexists(os.path.join(work, d)) for d in ('tip', 'run'))


def checkout_tip(repo, tip, work):
    tree = os.path.join(work, 'tip')
    os.makedirs(tree)
    archive = subprocess.Popen(['git', '-C', str(repo), 'archive', tip],
                               stdout=subprocess.PIPE, env=clean_env())
    tar = subprocess.run(['tar', '-x', '-C', tree], stdin=archive.stdout)
    archive.stdout.close()
    archive_rc = archive.wait()
    return tree if tar.returncode == 0 and archive_rc == 0 else None


def pgrep_set():
    """Live llama-server pids (`pgrep -x llama-server`), zombies dropped
    through /proc/<pid>/stat as the context-capacity tool does."""
    p = subprocess.run(['pgrep', '-x', 'llama-server'], capture_output=True,
                       text=True)
    pids = set()
    for tok in p.stdout.split():
        if not tok.isdigit():
            continue
        try:
            with open(f'/proc/{tok}/stat') as fh:
                state = fh.read().rsplit(')', 1)[1].split()[0]
        except (OSError, IndexError):
            continue
        if state != 'Z':
            pids.add(int(tok))
    return pids


def placeholders(run, tree, scratch, repo, tip):
    return (run.replace('%T', tree).replace('%S', scratch)
               .replace('%R', str(repo)).replace('TIPREV', tip))


# ------------------------------------------------------- canonical list #

def canonical_rows(text):
    """(round_no, [(slug, row_text)]) for the highest-numbered canonical
    capabilities heading, or (None, [])."""
    if not text:
        return None, []
    lines = text.splitlines()
    best = None
    for i, ln in enumerate(lines):
        m = HEAD_RE.search(ln)
        if m and 'canonical list' in ln.lower():
            if best is None or int(m.group(1)) > best[0]:
                best = (int(m.group(1)), i)
    if best is None:
        return None, []
    n, start = best
    rows = []
    for ln in lines[start + 1:start + 40]:
        if ln.startswith('## ') or ln.startswith('### '):
            break
        m = ROW_RE.match(ln)
        if m and m.group(1) not in ('capability', '---', '-'):
            rows.append((m.group(1), ln))
    return n, rows


def canon_problems(sc_text):
    """(round_no, rows, problems) for the newest canonical list. Tags:
    canon-absent, canon-round, canon-missing, canon-dup, prefix."""
    can_n, can_rows = canonical_rows(sc_text)
    if not can_rows:
        return can_n, can_rows, ['canon-absent: no canonical list at tip']
    probs = []
    if can_n != ROUND:
        probs.append(f'canon-round: newest canonical list is round {can_n}')
    slugs = [s for s, _ in can_rows]
    if len(slugs) != len(set(slugs)):
        probs.append(f'canon-dup: {slugs}')
    for slug in SLUGS:
        if slug not in slugs:
            probs.append(f'canon-missing: {slug}')
            continue
        row_text = next(t for seen, t in can_rows if seen == slug)
        if not row_text.startswith(SPECS[slug]['prefix']):
            probs.append(f'prefix: {slug}')
    return can_n, can_rows, probs


# ----------------------------------------------------------------- pins #

def check_pins(read, table, expect_n):
    """(ok_count, problems). `read(path)` returns the bytes at the tip or
    None. A table that does not carry expect_n files is itself a problem
    (pin-table), so the 13/13 cannot be reached by dropping entries."""
    probs = []
    if len(table) != expect_n:
        probs.append(f'pin-table: {len(table)} entries, want {expect_n}')
    ok = 0
    for path, want in table.items():
        data = read(path)
        if data is None:
            probs.append(f'pin-absent:{path}')
        elif sha256(data) != want:
            probs.append(f'pin:{path}')
        else:
            ok += 1
    return ok, probs


# ------------------------------------------------------ verdict function #

def pat_hit(out, pat, eol=False):
    if not pat:
        return False
    if eol:
        return re.search(re.escape(pat) + r'[ \t]*$', out, re.M) is not None
    return pat in out


def verdict_fn(out, rc, dead, pat, eol=False):
    """The one verdict function every bound row is graded with."""
    return (not dead) and pat_hit(out, pat, eol) and rc == 0


def strip_all(out, pat):
    """Remove the pattern until it no longer occurs (a replacement token
    could itself carry the pattern; removal cannot, and every pass shortens
    the text, so the loop ends)."""
    while pat and pat in out:
        out = out.replace(pat, '')
    return out


def structural_sensitive(out, rc, dead, pat, vfn=verdict_fn):
    """True iff the verdict is true and flips to false both when the pattern
    is removed and when the exit code is changed. Structural only: the live
    sensitivity of each row is the regression flip and the printer refusal."""
    if not vfn(out, rc, dead, pat):
        return False
    return ((not vfn(strip_all(out, pat), rc, dead, pat))
            and (not vfn(out, 1 if rc == 0 else 0, dead, pat)))


def sensitivity_selftest():
    """Plant four defective verdict functions (each is a function handed to
    structural_sensitive, not a witness): each must be called insensitive,
    and the shipped verdict function must be called sensitive."""
    out, pat = 'xx ok=1 yy', 'ok=1'
    planted = [
        lambda o, rc, d, p: True,                       # always true
        lambda o, rc, d, p: rc == 0 and not d,          # ignores the output
        lambda o, rc, d, p: p in o and not d,           # ignores the exit
        lambda o, rc, d, p: rc == 0 or p in o,          # OR for AND
    ]
    n = sum(int(not structural_sensitive(out, 0, False, pat, vfn=f))
            for f in planted)
    return n if structural_sensitive(out, 0, False, pat) else 0


# ----------------------------------------------- context-capacity outcome #

def _json_or_none(text):
    try:
        return json.loads(text)
    except (TypeError, ValueError):
        return None


def _receipt(receipt_text):
    rec = _json_or_none(receipt_text)
    return rec if isinstance(rec, dict) else None


def _summary(rec):
    s = rec.get('summary')
    return s if isinstance(s, dict) else {}


def _is_pid_list(seen):
    return (isinstance(seen, list)
            and all(isinstance(x, int) and not isinstance(x, bool)
                    for x in seen))


def idle_check(out, rc, receipt_text, pat):
    """(ok, reason): the declared idle outcome. Exit 0 with the pattern is
    not enough: `"all_ports_closed": true` is printed vacuously on an empty
    cell list. The receipt the tool wrote must show at least one cell that
    ran and was observed, a host probe that found the host idle and saw no
    foreign server at any point."""
    if rc != 0 or pat not in out:
        return False, 'rc-or-pattern'
    rec = _receipt(receipt_text)
    if rec is None:
        return False, 'no-receipt'
    s = _summary(rec)
    hi = rec.get('host_idle')
    if (rec.get('exit_code') != 0 or rec.get('error')
            or not isinstance(s.get('cells'), int) or s['cells'] < 1
            or not isinstance(s.get('observed'), int) or s['observed'] < 1
            or s.get('all_ports_closed') is not True):
        return False, 'idle-cells'
    if (not isinstance(hi, dict) or hi.get('ok') is not True
            or hi.get('other_pids_seen') != []):
        return False, 'idle-host'
    return True, 'idle'


def busy_check(out, rc, receipt_text, before, after, alt):
    """(ok, reason): the declared host-busy outcome. The refusal is exit 2
    with its text; the receipt it wrote names the refusal, ran no cell and
    carries host_idle.ok false. Its other_pids_seen is the union over the
    tool's whole polling window, so it is not tested against the counter's
    two snapshots as a subset; the check that cannot be met by an invented
    set is the reverse one: every llama-server pid the counter saw in both
    its before and its after snapshot (zombies dropped) stood throughout the
    window and must appear in the printed set."""
    if rc != 2:
        return False, 'rc'
    if alt not in out:
        return False, 'text'
    rec = _receipt(receipt_text)
    if rec is None:
        return False, 'no-receipt'
    if (rec.get('error') != alt or rec.get('exit_code') != 2
            or _summary(rec).get('cells') != 0 or rec.get('cells')):
        return False, 'receipt-error'
    hi = rec.get('host_idle')
    if not isinstance(hi, dict) or hi.get('ok') is not False:
        return False, 'no-host-idle'
    seen = hi.get('other_pids_seen')
    if not _is_pid_list(seen) or not seen:
        return False, 'seen-empty'
    if not (set(before) & set(after)) <= set(seen):
        return False, 'intersection-not-seen'
    return True, 'busy'


def classify(spec, run):
    """(outcome, reason) for one execution of a bound row."""
    if run['dead']:
        return 'false', 'dead'
    if spec['alt']:
        ok, why = idle_check(run['out'], run['rc'], run.get('receipt'),
                             spec['pattern'])
        if ok:
            return 'true', why
        ok, why2 = busy_check(run['out'], run['rc'], run.get('receipt'),
                              run.get('before', set()),
                              run.get('after', set()), spec['alt'])
        if ok:
            return 'host-busy', why2
        return 'false', (why if run['rc'] == 0 else why2)
    if verdict_fn(run['out'], run['rc'], False, spec['pattern'],
                  spec['eol']):
        return 'true', 'pattern'
    return 'false', 'pattern-or-rc'


# ------------------------------------------------------------- registry #

def parse_registry(text):
    rows, errors = [], []
    if not text:
        return rows, ['registry-absent']
    header = None
    for ln in text.splitlines():
        if not ln.strip() or ln.startswith('#'):
            continue
        cells = [c.strip() for c in ln.split('\t')]
        if header is None:
            if cells == COLS:
                header = cells
                continue
            return rows, ['header']
        if len(cells) != len(header):
            errors.append(f'cols:{len(cells)}')
            continue
        rows.append(dict(zip(header, cells)))
    if header is None:
        errors.append('header')
    return rows, errors


def want_observed(spec, verdict):
    return spec['pattern'] if verdict == 'true' else spec['alt']


def score(reg_text, outcome_of, population):
    """Score a registry text. `outcome_of(cap) -> (outcome, dead)` is the
    live result of the bound run. Returns facts with error tags."""
    rows, errors = parse_registry(reg_text)
    f = {'population': population, 'rows': len(rows), 'covered': 0,
         'bound': 0, 'dead': 0, 'mismatches': 0, 'host_busy': 0}
    errs = list(errors)
    covered, seen = set(), {}
    mism = []
    for row in rows:
        cap = row['cap']
        seen[cap] = seen.get(cap, 0) + 1
        if cap not in SPECS:
            errs.append(f'unbound-cap:{cap}')
            continue
        if seen[cap] > 1:
            errs.append(f'dup-row:{cap}')
            continue
        spec = SPECS[cap]
        if (row['quote'] not in spec['prefix'] or len(row['quote']) < 8):
            errs.append(f'quote:{cap}')
            continue
        if row['binding'] != spec['binding']:
            errs.append(f'binding:{cap}:{row["binding"]}')
            continue
        if row['run'] != spec['run']:
            errs.append(f'run:{cap}')
            continue
        if row['pattern'] != spec['pattern']:
            errs.append(f'pattern:{cap}')
            continue
        if row['outcomes'] != ','.join(spec['outcomes']):
            errs.append(f'outcomes:{cap}')
            continue
        rec = row['verdict'].lower()
        if rec not in ('true', 'host-busy'):
            errs.append(f'verdict-value:{cap}:{rec}')
            continue
        if rec not in spec['outcomes']:
            errs.append(f'hostbusy-not-declared:{cap}')
            continue
        f['bound'] += 1
        covered.add(cap)
        outcome, dead = outcome_of(cap)
        f['dead'] += int(dead)
        f['host_busy'] += int(outcome == 'host-busy')
        if outcome not in spec['outcomes'] or dead:
            f['mismatches'] += 1
            mism.append(f'outcome:{cap}:{outcome}')
        if row['observed'] != want_observed(spec, rec):
            f['mismatches'] += 1
            mism.append(f'observed:{cap}')
    f['covered'] = len(covered)
    f['err_list'] = errs + mism
    f['errors'] = len(errs)
    f['tags'] = {e.split(':')[0] for e in errs}
    if f['mismatches']:
        f['tags'].add('mismatch')
    if f['covered'] < population:
        f['tags'].add('covered')
    return f


def reg_met(f):
    return (f['covered'] == f['population'] and f['mismatches'] == 0
            and f['errors'] == 0 and f['dead'] == 0
            and f['bound'] >= f['population'])


# ----------------------------------------------------- regression table #

def parse_regress(text):
    """(rows, errors); rows are dicts keyed by RCOLS. find/replace are kept
    verbatim (indentation is part of a one-line regression)."""
    rows, errors = [], []
    if not text:
        return rows, ['regress-absent']
    for ln in text.split('\n'):
        if not ln.strip() or ln.startswith('#'):
            continue
        cells = ln.split('\t')
        if cells[0] == 'cap' and cells[:4] == RCOLS:
            continue
        if len(cells) != 4:
            errors.append(f'regress-cols:{len(cells)}')
            continue
        rows.append(dict(zip(RCOLS, cells)))
    return rows, errors


def apply_regression(src, find, replace):
    """New source bytes, or (None, tag). find must occur exactly once."""
    try:
        s = src.decode('utf-8')
    except UnicodeDecodeError:
        return None, 'regress-undecodable'
    if not find or '\n' in find or '\n' in replace:
        return None, 'regress-multiline'
    if s.count(find) != 1:
        return None, 'regress-inapplicable'
    if replace == find:
        return None, 'regress-noop'
    out = s.replace(find, replace, 1)
    try:
        compile(out, 'regressed', 'exec')
    except (SyntaxError, ValueError):
        return None, 'regress-syntax'
    return out.encode('utf-8'), None


def regress_plan(table_text, read_tool):
    """cap -> (regressed_bytes | None, tag | None) for every manifest cap,
    plus table-level errors. Tags: regress-absent, regress-cols,
    regress-missing, regress-dup, regress-unbound, regress-path and the
    apply_regression tags."""
    rows, errs = parse_regress(table_text)
    plan = {}
    by_cap = {}
    for r in rows:
        by_cap.setdefault(r['cap'], []).append(r)
    for cap in by_cap:
        if cap not in SPECS:
            errs.append(f'regress-unbound:{cap}')
    for cap in SLUGS:
        rs = by_cap.get(cap, [])
        if not rs:
            plan[cap] = (None, 'regress-missing')
            continue
        if len(rs) > 1:
            plan[cap] = (None, 'regress-dup')
            continue
        r = rs[0]
        if r['tool_path'] != SPECS[cap]['tool']:
            plan[cap] = (None, 'regress-path')
            continue
        src = read_tool(r['tool_path'])
        if src is None:
            plan[cap] = (None, 'regress-inapplicable')
            continue
        plan[cap] = apply_regression(src, r['find'], r['replace'])
    return plan, errs


# ------------------------------------------------------------- execution #

class Runner:
    """Executes bound run templates in an allowlisted environment against
    the tip tree or an overlay of it."""

    def __init__(self, repo, tip, work, tip_tree):
        self.repo, self.tip, self.work, self.tip_tree = repo, tip, work, \
            tip_tree
        self.runroot = os.path.join(work, 'run')
        os.makedirs(self.runroot)
        self.env = {k: v for k, v in os.environ.items() if k in ENV_KEYS}
        self.env['TMPDIR'] = self.runroot
        self.env['PYTHONDONTWRITEBYTECODE'] = '1'
        self.cache = {}
        self.overlays = {}

    def overlay(self, label, replacements):
        """A tree whose top-level entries other than tools/ are symlinks to
        the tip tree and whose tools/ is a real copy with `replacements`
        ({relpath: bytes}) written over it."""
        if label in self.overlays:
            return self.overlays[label]
        dest = os.path.join(self.work, 'ovl', label)
        os.makedirs(dest)
        for name in os.listdir(self.tip_tree):
            if name != 'tools':
                os.symlink(os.path.join(self.tip_tree, name),
                           os.path.join(dest, name))
        shutil.copytree(os.path.join(self.tip_tree, 'tools'),
                        os.path.join(dest, 'tools'))
        for rel, data in replacements.items():
            with open(os.path.join(dest, rel), 'wb') as fh:
                fh.write(data)
        self.overlays[label] = dest
        return dest

    def run(self, cap, label, tree, fake_idle=False):
        """One execution. `fake_idle`: a copy of the tool is run with a
        `pgrep` that reports no process first on PATH (the fixture the
        idle outcome needs on a host that is never idle); the tool's own
        code path runs unmodified."""
        key = (label, cap)
        if key in self.cache:
            return self.cache[key]
        spec = SPECS[cap]
        scratch = os.path.join(self.runroot, label, cap)
        os.makedirs(scratch, exist_ok=True)
        cmd = placeholders(spec['run'], tree, scratch, self.repo, self.tip)
        m = re.search(r'%T/(tools/[A-Za-z0-9._-]+\.py)', spec['run'])
        dead = not (m and os.path.isfile(os.path.join(tree, m.group(1))))
        busy_row = spec['alt'] is not None and not fake_idle
        env = dict(self.env)
        if fake_idle:
            fakebin = os.path.join(scratch, 'fakebin')
            os.makedirs(fakebin)
            fake = os.path.join(fakebin, 'pgrep')
            with open(fake, 'w') as fh:
                fh.write('#!/bin/bash\nexit 1\n')
            os.chmod(fake, 0o755)
            env['PATH'] = fakebin + os.pathsep + env.get('PATH', '')
        before = pgrep_set() if busy_row else set()
        t0 = time.monotonic()
        p = subprocess.Popen(['bash', '-c', cmd], stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, text=True, cwd=tree,
                             env=env, start_new_session=True)
        try:
            out, _ = p.communicate(timeout=RUN_TIMEOUT)
            rc = p.returncode
        except subprocess.TimeoutExpired:
            self.kill_group(p.pid)
            out, _ = p.communicate()
            out, rc = (out or '') + '\nTIMEOUT', 124
        self.kill_group(p.pid)
        after = pgrep_set() if busy_row else set()
        receipt = None
        if spec['alt']:
            try:
                with open(os.path.join(scratch, 'cc.json')) as fh:
                    receipt = fh.read()
            except OSError:
                receipt = None
        res = {'out': out, 'rc': rc, 'dead': dead, 'before': before,
               'after': after, 'receipt': receipt,
               'secs': round(time.monotonic() - t0, 1)}
        self.cache[key] = res
        return res

    @staticmethod
    def kill_group(pid):
        try:
            os.killpg(pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass

    def outcome(self, cap, label, tree, fake_idle=False):
        run = self.run(cap, label, tree, fake_idle=fake_idle)
        return classify(SPECS[cap], run)


def printer_source(cap):
    """A tool that emits what the row's pattern needs and runs nothing. The
    context-capacity printer also writes the idle receipt it was asked for
    (`--out`), so only the sensitivity check can refuse it."""
    spec = SPECS[cap]
    if not spec['alt']:
        return f'import sys\nprint({spec["pattern"]!r})\nsys.exit(0)\n'
    summary = {'all_ports_closed': True, 'cells': 1, 'observed': 1,
               'ports_used': [47401]}
    receipt = {'error': None, 'exit_code': 0, 'cells': [{'observed': True}],
               'summary': summary,
               'host_idle': {'ok': True, 'other_pids_seen': [],
                             'waited_s': 0.0, 'cell': 'K1'}}
    return ('import json, sys\n'
            f'summary = {json.dumps(summary)!r}\n'
            f'receipt = {json.dumps(receipt)!r}\n'
            'a = sys.argv\n'
            'if "--out" in a:\n'
            '    open(a[a.index("--out") + 1], "w").write(receipt)\n'
            'print(summary)\n'
            'sys.exit(0)\n')

def decoy_source(cap, orig):
    """A printer that keeps the original source commented out, so a planted
    regression still applies (once) but changes nothing the printer does."""
    body = ''.join('# ' + ln for ln in orig.decode('utf-8').splitlines(True))
    return (printer_source(cap) + body + '\n').encode('utf-8')


# ------------------------------------------------------ reconciler/tally #

def parse_kv(line):
    return dict(re.findall(r'([A-Za-z0-9_]+)=(\S+)', line))


def recon_eval(rc, out):
    """(mismatches | None, fields, ok): the reconciler counts only when it
    exits 0 and prints mismatches=0 with met=True; a count printed beside a
    non-zero exit, or no count at all, is not zero."""
    line = next((ln for ln in out.splitlines()
                 if ln.startswith('r41=') and 'mismatches=' in ln), None)
    if line is None:
        return None, {}, False
    kv = parse_kv(line)
    try:
        n = int(kv['mismatches'])
    except (KeyError, ValueError):
        return None, kv, False
    ok = rc == 0 and n == 0 and kv.get('met') == 'True'
    return n, kv, ok


def run_recon(tip_tree, repo, tip, env, cwd):
    p = subprocess.run(
        [sys.executable, os.path.join(tip_tree, RECON), '--repo', str(repo),
         '--tip', tip], capture_output=True, text=True, env=env, cwd=cwd,
        timeout=600)
    return p.returncode, p.stdout + p.stderr


CLOSURE_RE = re.compile(
    r'latest outside closure\s+`corpus/lessons/round-(\d+)-verifier-spotcheck'
    r'\.md`')
INCL_RE = re.compile(r'including round (\d+)')
SPOT_RE = re.compile(r'^corpus/lessons/round-(\d+)-verifier-spotcheck\.md$')


def calibration_row(sc_text):
    """The one `| calibration |` row of the current axes table: the rows of
    `## Axes` before its first `###` subsection (the historical table that
    follows carries another calibration row), or None."""
    rows, inside = [], False
    for ln in (sc_text or '').splitlines():
        if ln.startswith('## ') or ln.startswith('### '):
            inside = ln.strip() == '## Axes'
            continue
        if inside and ln.startswith('| calibration |'):
            rows.append(ln)
    return rows[0] if len(rows) == 1 else None


def closure_check(sc_text, lesson_paths):
    """(ok, tag, ptr, newest): the calibration row names exactly one
    latest-outside-closure pointer and it is the newest spotcheck file."""
    nums = [int(m.group(1)) for p in lesson_paths
            for m in [SPOT_RE.match(p)] if m]
    if not nums:
        return False, 'closure-nofiles', None, None
    newest = max(nums)
    row = calibration_row(sc_text)
    if row is None:
        return False, 'closure-norow', None, newest
    ptrs = [int(x) for x in CLOSURE_RE.findall(row)]
    if len(ptrs) != 1:
        return False, 'closure-nopointer', None, newest
    if ptrs[0] != newest:
        return False, 'closure-stale', ptrs[0], newest
    return True, 'closure', ptrs[0], newest


def set_pointer(sc_text, n):
    """The calibration row's pointer and `including round` set to round n."""
    row = calibration_row(sc_text)
    if row is None:
        return None
    new = CLOSURE_RE.sub(
        lambda m: m.group(0).replace(f'round-{m.group(1)}', f'round-{n}'),
        row)
    new = INCL_RE.sub(f'including round {n}', new)
    return sc_text.replace(row, new, 1)


def make_fixture_commit(repo, tip, work, name, sc_text):
    """A commit on a shared clone of the lane (alternates only; the lane is
    not written) whose SCORECARD.md is sc_text. Returns (fixture, sha)."""
    fx = os.path.join(work, 'fx-' + name)
    env = clean_env()
    p = subprocess.run(['git', 'clone', '-q', '--shared', '--no-checkout',
                        str(repo), fx], capture_output=True, env=env)
    if p.returncode != 0:
        return None, None
    idx = os.path.join(work, f'fx-{name}.index')
    env2 = dict(env, GIT_INDEX_FILE=idx,
                GIT_AUTHOR_NAME='c2', GIT_AUTHOR_EMAIL='c2@c2.invalid',
                GIT_COMMITTER_NAME='c2', GIT_COMMITTER_EMAIL='c2@c2.invalid')

    def g(*a, input_bytes=None):
        return subprocess.run(['git', '-C', fx, *a], capture_output=True,
                              env=env2, input=input_bytes)
    if g('read-tree', tip).returncode != 0:
        return None, None
    h = g('hash-object', '-w', '--stdin',
          input_bytes=sc_text.encode('utf-8'))
    if h.returncode != 0:
        return None, None
    u = g('update-index', '--cacheinfo',
          f'100644,{h.stdout.decode().strip()},SCORECARD.md')
    w = g('write-tree')
    if u.returncode != 0 or w.returncode != 0:
        return None, None
    c = g('commit-tree', w.stdout.decode().strip(), '-p', tip, '-m', name)
    sha = c.stdout.decode().strip()
    return (fx, sha) if c.returncode == 0 and sha else (None, None)


def closure_planted(repo, tip, tip_tree, work, env, sc_text, newest, stale):
    """Run the tip reconciler on a repaired and on a stale-pointer copy of
    the tip: the stale one must print closure_ptr=0 and more mismatches than
    the repaired one, with a `closure_ptr` detail line."""
    fixed = set_pointer(sc_text, newest)
    bad = set_pointer(sc_text, stale)
    if fixed is None or bad is None:
        return False, 'closure-norow', {}
    res = {}
    for name, text in (('fixed', fixed), ('stale', bad)):
        fx, sha = make_fixture_commit(repo, tip, work, name, text)
        if not sha:
            return False, 'fixture', {}
        rc, out = run_recon(tip_tree, fx, sha, env, tip_tree)
        n, kv, _ = recon_eval(rc, out)
        res[name] = {'n': n, 'kv': kv, 'out': out}
    f, s = res['fixed'], res['stale']
    ok, tag = planted_verdict(f, s)
    return ok, tag, {k: v['n'] for k, v in res.items()}


def planted_verdict(f, s):
    """(ok, tag) for the repaired (`f`) and stale (`s`) reconciler runs: each
    of the five clauses is one named failure."""
    if f['n'] is None or s['n'] is None:
        return False, 'planted-nocount'
    if f['kv'].get('closure_ptr') != '1':
        return False, 'planted-fixed-fails'
    if s['kv'].get('closure_ptr') != '0':
        return False, 'planted-stale-passes'
    if not s['n'] > f['n']:
        return False, 'planted-no-increase'
    if 'closure_ptr:' not in s['out'] or 'closure_ptr:' in f['out']:
        return False, 'planted-no-detail'
    return True, 'planted'


def tally_count(records, rounds):
    """Rounds in `rounds` whose status is neither no-disclosure nor
    unreadable (a status the tool computed from a disclosure)."""
    by = {r.get('round'): r.get('status', '') for r in records}
    return sum(1 for n in rounds
               if by.get(n) and by[n] != 'no-disclosure'
               and not by[n].startswith('unreadable'))


def run_tally(tip_tree, repo, tip, env, cwd, rounds=TALLY_ROUNDS):
    p = subprocess.run(
        [sys.executable, os.path.join(tip_tree, TALLY), '--repo', str(repo),
         '--rev', tip, '--rounds', rounds, '--json'],
        capture_output=True, text=True, env=env, cwd=cwd, timeout=300)
    d = _json_or_none(p.stdout)
    recs = d.get('records') if isinstance(d, dict) else None
    return recs if isinstance(recs, list) else []


def tally_fixture(tip_tree, work, env):
    """A fixture repo whose round 56 has a `## Round 56` section and no
    disclosure block: the tally must still print no-disclosure for it."""
    fx = os.path.join(work, 'fx-tally')
    os.makedirs(fx)
    e = dict(clean_env(), GIT_AUTHOR_NAME='c2', GIT_AUTHOR_EMAIL='c2@c2.invalid',
             GIT_COMMITTER_NAME='c2', GIT_COMMITTER_EMAIL='c2@c2.invalid')

    def g(*a):
        return subprocess.run(['git', '-C', fx, *a], capture_output=True,
                              env=e)
    g('init', '-q')
    os.makedirs(os.path.join(fx, '.ufo', 'waves', 'round-56'))
    with open(os.path.join(fx, '.ufo', 'waves', 'round-56', 'NOTE.txt'),
              'w') as fh:
        fh.write('fixture\n')
    with open(os.path.join(fx, 'SCORECARD.md'), 'w') as fh:
        fh.write('# Scorecard\n\n## Round 56 - fixture without a disclosure '
                 'block\n\nNothing is disclosed here.\n')
    g('add', '-A')
    g('commit', '-q', '-m', 'fixture')
    sha = g('rev-parse', 'HEAD').stdout.decode().strip()
    if not sha:
        return None
    recs = run_tally(tip_tree, fx, sha, env, work, rounds='56-56')
    return recs[0].get('status') if recs else None


def tally_selftest(tip_tree, work, env):
    scratch = os.path.join(work, 'tally-selftest')
    os.makedirs(scratch)
    e = dict(env, TMPDIR=scratch)
    p = subprocess.run(
        [sys.executable, os.path.join(tip_tree, TALLY), '--selftest',
         '--scratch', scratch], capture_output=True, text=True, env=e,
        cwd=work, timeout=300)
    out = p.stdout + p.stderr
    return p.returncode == 0 and 'fail=0' in out and 'no-disclosure' in out


# ------------------------------------------------------------- the gate #

def flip_status(spec, base_outcome, mutated_outcome):
    """A planted regression counts when the unmutated run is one of the
    row's declared outcomes and the regressed run is not."""
    if base_outcome not in spec['outcomes']:
        return 'base-' + str(base_outcome)
    return 'flipped' if mutated_outcome == 'false' else 'not-flipped'


def printer_status(printer_outcome, real_flipped, regress_tag,
                   regressed_outcome):
    """(rejected, tag) for a printer copy of a tool. It is rejected as not
    sensitive only when the verdict function accepts it, the row's own
    regression flips the real tool, and that regression either does not
    apply to the printer or leaves it accepted."""
    if printer_outcome != 'true':
        return False, 'printer-not-accepted'
    if not real_flipped:
        return False, 'no-working-regression'
    if regress_tag is not None:
        return True, regress_tag
    if regressed_outcome == 'true':
        return True, 'not-flipped'
    return False, 'printer-sensitive'


def gate(facts):
    """Names of the fields that miss their frozen target."""
    bad = []
    for name, want in TARGETS:
        got = facts.get(name)
        if got is None or got != want:
            bad.append(name)
    if facts.get('population') != N_CAPS:
        bad.append('population')
    return bad


# -------------------------------------------------------------- controls #

class Controls:
    """Each control mutates one input and re-runs the check it names; a
    control is rejected when the failure it names is among the tags the
    re-run produced and the unmutated input does not produce that tag."""

    def __init__(self):
        self.items = []     # (family, name, expect_tag, tags, base_tags)

    def add(self, family, name, expect, tags, base_tags=()):
        self.items.append((family, name, expect, set(tags), set(base_tags)))

    def results(self):
        out = []
        for fam, name, expect, tags, base in self.items:
            out.append((fam, name, expect, expect in tags
                        and expect not in base, sorted(tags)[:4]))
        return out


def reg_tags(reg_text, outcome_of):
    f = score(reg_text, outcome_of, N_CAPS)
    return set(f['tags']) | ({'unmet'} if not reg_met(f) else set()), f


def build_registry_controls(ctl, reg_text, outcome_of):
    lines = [ln for ln in reg_text.splitlines() if ln.strip()]
    header = next(ln for ln in lines if ln.startswith('cap\t'))
    data = [ln for ln in lines if '\t' in ln and not ln.startswith('cap\t')
            and not ln.startswith('#')]

    def j(rows):
        return header + '\n' + '\n'.join(rows) + '\n'

    def cells(ln):
        return ln.split('\t')

    def col(ln, i, val):
        c = cells(ln)
        c[i] = val
        return '\t'.join(c)

    base_tags, _ = reg_tags(reg_text, outcome_of)
    first = data[0]
    muts = {
        'drop': ('covered', j(data[1:])),
        'rename': ('unbound-cap', j([col(first, 0, 'sources-fakery')]
                                    + data[1:])),
        'binding': ('binding', j([col(first, 2, 'selftest')] + data[1:])),
        'verdict-value': ('verdict-value', j([col(first, 5, 'false')]
                                             + data[1:])),
        'quote-prefix': ('quote', j([col(first, 1, 'NOT-A-PREFIX-QUOTE')]
                                    + data[1:])),
        'quote-short': ('quote', j([col(first, 1, 'Curate')] + data[1:])),
        'quote-empty': ('quote', j([col(first, 1, '')] + data[1:])),
        'free': ('binding', j(['sources-registry\tCurate where\tfree\t'
                               'bash -c "echo ok"\tok\ttrue\tok\ttrue\tfree']
                              + data[1:])),
        'weak-pattern': ('pattern', j([col(first, 4, 'pass')] + data[1:])),
        'hostbusy-undeclared': ('hostbusy-not-declared',
                                j([col(first, 5, 'host-busy')] + data[1:])),
        'outcomes-forged': ('outcomes', j([col(first, 7, 'true,host-busy')]
                                          + data[1:])),
        'dup-identical': ('dup-row', j(data + [first])),
        'dup-conflict': ('dup-row',
                         j(data + [col(col(first, 3, 'echo conflict'),
                                       4, 'conflict')])),
        'run-tamper': ('run', j([col(first, 3, 'python3 %T/tools/pin-watch.py'
                                     ' selftest')] + data[1:])),
        'observed-forged': ('mismatch', j([col(first, 6, 'FORGED-OBSERVATION')]
                                          + data[1:])),
        'observed-blank': ('mismatch', j([col(first, 6, '')] + data[1:])),
        'observed-fragment': ('mismatch', j([col(first, 6, '45')]
                                            + data[1:])),
    }
    for name, (expect, text) in muts.items():
        tags, _ = reg_tags(text, outcome_of)
        ctl.add('registry', name, expect, tags, base_tags)


def build_canon_controls(ctl, sc_text):
    _, _, base = canon_problems(sc_text)
    base_tags = {p.split(':')[0] for p in base}
    lines = sc_text.splitlines()
    n, rows = canonical_rows(sc_text)
    start = next(i for i, ln in enumerate(lines) if HEAD_RE.search(ln)
                 and 'canonical list' in ln.lower()
                 and int(HEAD_RE.search(ln).group(1)) == n)

    def tags(text):
        return {p.split(':')[0] for p in canon_problems(text)[2]}

    drop = [ln for ln in lines if not ln.startswith('| sources-registry |')]
    ctl.add('canon', 'canon-drop-row', 'canon-missing',
            tags('\n'.join(drop)), base_tags)
    old = list(lines)
    old[start] = re.sub(r'round\s*\d+', 'round 63', old[start], count=1)
    ctl.add('canon', 'canon-old-round', 'canon-round', tags('\n'.join(old)),
            base_tags)
    def newest_row(ls):
        return next(k for k in range(start, len(ls))
                    if ls[k].startswith('| pin-watch |'))
    pre = list(lines)
    i = newest_row(pre)
    pre[i] = pre[i].replace('| pin-watch | List', '| pin-watch | Lisp', 1)
    ctl.add('canon', 'canon-prefix', 'prefix', tags('\n'.join(pre)),
            base_tags)
    dup = list(lines)
    i = newest_row(dup)
    dup.insert(i + 1, dup[i])
    ctl.add('canon', 'canon-dup-row', 'canon-dup', tags('\n'.join(dup)),
            base_tags)


def build_pin_controls(ctl, read):
    def tags_for(rd, table, n):
        return {p.split(':')[0] for p in check_pins(rd, table, n)[1]}

    base = tags_for(read, PINS, N_PINS)
    tool = 'tools/pin-watch.py'
    ctl.add('pins', 'pin-tool-edit', 'pin',
            tags_for(lambda p: (b'print("ok")\n' if p == tool else read(p)),
                     PINS, N_PINS), base)
    ctl.add('pins', 'pin-reconciler-edit', 'pin',
            tags_for(lambda p: ((read(p) or b'') + b'\n# mism = 0\n'
                                if p == RECON else read(p)), PINS, N_PINS),
            base)
    ctl.add('pins', 'pin-absent', 'pin-absent',
            tags_for(lambda p: None if p == tool else read(p), PINS,
                     N_PINS), base)
    short = {k: v for k, v in PINS.items() if k != RECON}
    ctl.add('pins', 'pin-table-short', 'pin-table',
            tags_for(read, short, N_PINS), base)
    dbase = tags_for(read, DEP_PINS, N_DEPS)
    dep = '.ufo/waves/round-25/count-c2.py'
    ctl.add('pins', 'dep-edit', 'pin',
            tags_for(lambda p: (b'x = 1\n' if p == dep else read(p)),
                     DEP_PINS, N_DEPS), dbase)


def idle_controls(ctl, spec):
    """Positive and negative controls of both declared outcomes. Returns
    (accepted positives, positives)."""
    alt, pat = spec['alt'], spec['pattern']
    standing = [242776, 1706355, 3262613]
    before = set(standing)
    after = set(standing) | {9000}
    out_busy = (f'kama-context-capacity: {alt}\n{{"all_ports_closed": true, '
                f'"cells": 0, "observed": 0, "ports_used": []}}\n')
    out_idle = ('{"all_ports_closed": true, "cells": 1, "observed": 1, '
                '"ports_used": [47401]}\n')

    def busy_rec(seen=None, ok=False, error=alt, cells=0, code=2,
                 host_idle=True):
        r = {'error': error, 'exit_code': code, 'cells': [] if not cells
             else [{'observed': True}] * cells,
             'summary': {'cells': cells, 'observed': 0,
                         'all_ports_closed': True}}
        if host_idle:
            r['host_idle'] = {'ok': ok, 'cell': 'K1', 'waited_s': 20.1,
                              'other_pids_seen': standing + [9000, 9001]
                              if seen is None else seen}
        return json.dumps(r)

    def idle_rec(ok=True, seen=None, cells=1, observed=1, code=0,
                 error=None, closed=True):
        return json.dumps({
            'error': error, 'exit_code': code,
            'cells': [{'observed': True}] * cells,
            'summary': {'cells': cells, 'observed': observed,
                        'all_ports_closed': closed},
            'host_idle': {'ok': ok, 'cell': 'K1', 'waited_s': 0.0,
                          'other_pids_seen': [] if seen is None else seen}})

    def busy(rec, rc=2, text=out_busy, b=before, a=after):
        return busy_check(text, rc, rec, b, a, alt)

    def idle(rec, rc=0, text=out_idle):
        return idle_check(text, rc, rec, pat)

    pos = [busy(busy_rec()),
           busy(busy_rec(seen=standing)),            # churn-free
           busy(busy_rec(seen=standing + [9000, 9001, 9002])),  # churn
           idle(idle_rec())]
    pos_ok = sum(1 for ok, _ in pos if ok)
    # outcome by the shipped classifier on a recorded run
    run = {'out': out_idle, 'rc': 0, 'dead': False, 'receipt': idle_rec()}
    pos_ok += int(classify(spec, run)[0] == 'true')
    run = {'out': out_busy, 'rc': 2, 'dead': False, 'receipt': busy_rec(),
           'before': before, 'after': after}
    pos_ok += int(classify(spec, run)[0] == 'host-busy')
    n_pos = len(pos) + 2

    def tag(res):
        return {res[1]}
    ctl.add('idle', 'busy-invented-set', 'intersection-not-seen',
            tag(busy(busy_rec(seen=[999991, 999992]))))
    ctl.add('idle', 'busy-standing-pid-omitted', 'intersection-not-seen',
            tag(busy(busy_rec(seen=[1706355, 3262613]))))
    ctl.add('idle', 'busy-empty-set', 'seen-empty',
            tag(busy(busy_rec(seen=[]))))
    ctl.add('idle', 'busy-no-host-idle', 'no-host-idle',
            tag(busy(busy_rec(host_idle=False))))
    ctl.add('idle', 'busy-host-idle-ok', 'no-host-idle',
            tag(busy(busy_rec(ok=True))))
    ctl.add('idle', 'busy-no-receipt', 'no-receipt', tag(busy(None)))
    ctl.add('idle', 'busy-wrong-error', 'receipt-error',
            tag(busy(busy_rec(error='other'))))
    ctl.add('idle', 'busy-ran-a-cell', 'receipt-error',
            tag(busy(busy_rec(cells=1))))
    ctl.add('idle', 'busy-exit-0', 'rc', tag(busy(busy_rec(), rc=0)))
    ctl.add('idle', 'busy-text-missing', 'text',
            tag(busy(busy_rec(), text='refused\n')))
    ctl.add('idle', 'idle-exit-1', 'rc-or-pattern', tag(idle(idle_rec(), rc=1)))
    ctl.add('idle', 'idle-pattern-missing', 'rc-or-pattern',
            tag(idle(idle_rec(), text='ok\n')))
    ctl.add('idle', 'idle-pattern-only', 'no-receipt',
            tag(idle(None, text='"all_ports_closed": true\n')))
    ctl.add('idle', 'idle-zero-cells', 'idle-cells',
            tag(idle(idle_rec(cells=0, observed=0))))
    ctl.add('idle', 'idle-unobserved', 'idle-cells',
            tag(idle(idle_rec(observed=0))))
    ctl.add('idle', 'idle-cells-zero-observed-one', 'idle-cells',
            tag(idle(idle_rec(cells=0, observed=1))))
    ctl.add('idle', 'idle-ports-open', 'idle-cells',
            tag(idle(idle_rec(closed=False))))
    ctl.add('idle', 'idle-exit-code-in-receipt', 'idle-cells',
            tag(idle(idle_rec(code=2))))
    ctl.add('idle', 'idle-errored', 'idle-cells',
            tag(idle(idle_rec(error='boom'))))
    ctl.add('idle', 'idle-host-not-ok', 'idle-host',
            tag(idle(idle_rec(ok=False))))
    ctl.add('idle', 'idle-foreign-pids-seen', 'idle-host',
            tag(idle(idle_rec(seen=[1706355]))))
    return pos_ok, n_pos


def work_controls(ctl, work, probe):
    scratch = os.path.join(work, 'wr')
    os.makedirs(scratch)
    empty_tip = os.path.join(scratch, 'a')
    os.makedirs(os.path.join(empty_tip, 'tip'))
    clean = os.path.join(scratch, 'b')
    os.makedirs(clean)
    run_only = os.path.join(scratch, 'c')
    os.makedirs(os.path.join(run_only, 'run'))
    ctl.add('work', 'empty-tip-dir', 'work-reused',
            {'work-reused'} if work_reused(empty_tip) else {'work-free'},
            {'work-reused'} if work_reused(clean) else set())
    ctl.add('work', 'run-dir-only', 'work-reused',
            {'work-reused'} if work_reused(run_only) else {'work-free'},
            {'work-reused'} if work_reused(clean) else set())
    rc, out, free = probe
    ctl.add('work', 'second-run-same-work', 'work-reused',
            {'work-reused'} if (rc == 2 and 'work-reused' in out
                                and 'met=' not in out) else {'rc%d' % rc})
    return int(free)


def closure_controls(ctl, sc_text, lesson_paths):
    _, base_tag, _, newest = closure_check(sc_text, lesson_paths)
    base = {base_tag}
    older = max([int(m.group(1)) for p in lesson_paths
                 for m in [SPOT_RE.match(p)] if m and int(m.group(1))
                 < (newest or 0)] or [0])
    stale = set_pointer(sc_text, older)
    ctl.add('closure', 'closure-stale-pointer', 'closure-stale',
            {closure_check(stale, lesson_paths)[1]} if stale else set(),
            base)
    row = calibration_row(sc_text)
    nop = sc_text.replace(row, CLOSURE_RE.sub('latest outside closure', row),
                          1) if row else sc_text
    ctl.add('closure', 'closure-no-pointer', 'closure-nopointer',
            {closure_check(nop, lesson_paths)[1]}, base)
    ctl.add('closure', 'closure-no-row', 'closure-norow',
            {closure_check(sc_text.replace('| calibration |', '| calib |'),
                           lesson_paths)[1]}, base)
    ctl.add('closure', 'closure-no-files', 'closure-nofiles',
            {closure_check(sc_text, ['corpus/lessons/round-1-x.md'])[1]},
            base)
    ctl.add('closure', 'closure-pointer-above-newest', 'closure-stale',
            {closure_check(set_pointer(sc_text, (newest or 0) + 1),
                           lesson_paths)[1]}, base)


def recon_controls(ctl):
    good = ('r41=0 banner=0 closure_ptr=1 mismatches=0 maxN=63 met=True')
    base = {'ok'} if recon_eval(0, good)[2] else {'bad'}

    def tag(rc, out):
        n, kv, ok = recon_eval(rc, out)
        return {'ok' if ok else ('nocount' if n is None else
                                 'nonzero' if n else 'exit-or-met')}
    ctl.add('reconciler', 'recon-exit-1-with-zero', 'exit-or-met',
            tag(1, good), base)
    ctl.add('reconciler', 'recon-no-count', 'nocount',
            tag(0, 'detail: crashed\n'), base)
    ctl.add('reconciler', 'recon-crash-silent', 'nocount', tag(1, ''), base)
    ctl.add('reconciler', 'recon-count-nonzero', 'nonzero',
            tag(1, good.replace('mismatches=0', 'mismatches=2')), base)
    ctl.add('reconciler', 'recon-met-false-zero', 'exit-or-met',
            tag(0, good.replace('met=True', 'met=False')), base)
    fixed = {'n': 0, 'kv': {'closure_ptr': '1'}, 'out': 'met=True\n'}
    stale = {'n': 1, 'kv': {'closure_ptr': '0'},
             'out': 'detail: closure_ptr: round-57 vs round-63\n'}
    pbase = {planted_verdict(fixed, stale)[1]}
    ctl.add('reconciler', 'planted-no-count', 'planted-nocount',
            {planted_verdict(dict(fixed, n=None), stale)[1]}, pbase)
    ctl.add('reconciler', 'planted-fixed-fails', 'planted-fixed-fails',
            {planted_verdict(dict(fixed, kv={'closure_ptr': '0'}),
                             stale)[1]}, pbase)
    ctl.add('reconciler', 'planted-stale-passes', 'planted-stale-passes',
            {planted_verdict(fixed, dict(stale, kv={'closure_ptr': '1'}))[1]},
            pbase)
    ctl.add('reconciler', 'planted-no-increase', 'planted-no-increase',
            {planted_verdict(fixed, dict(stale, n=0))[1]}, pbase)
    ctl.add('reconciler', 'planted-no-detail', 'planted-no-detail',
            {planted_verdict(fixed, dict(stale, out='nothing\n'))[1]}, pbase)
    ctl.add('reconciler', 'planted-detail-on-fixed', 'planted-no-detail',
            {planted_verdict(dict(fixed, out='detail: closure_ptr: x\n'),
                             stale)[1]}, pbase)


def tally_fixture_ok(status):
    """The fixture round without a disclosure block must still print
    `no-disclosure`: a tool that disclosed everything by relabelling is not
    a reader."""
    return status == 'no-disclosure'


def tally_controls(ctl):
    rounds = list(range(56, 64))
    good = [{'round': n, 'status': 'ok'} for n in rounds]
    base = {'tally-undisclosed'} if tally_count(good, rounds) != 8 else set()

    def t(recs):
        return {'tally-undisclosed'} if tally_count(recs, rounds) < 8 \
            else set()
    ctl.add('tally', 'tally-all-no-disclosure', 'tally-undisclosed',
            t([dict(r, status='no-disclosure') for r in good]), base)
    ctl.add('tally', 'tally-one-no-disclosure', 'tally-undisclosed',
            t(good[:-1] + [{'round': 63, 'status': 'no-disclosure'}]), base)
    ctl.add('tally', 'tally-unreadable', 'tally-undisclosed',
            t(good[:-1] + [{'round': 63, 'status': 'unreadable:x'}]), base)
    ctl.add('tally', 'tally-round-missing', 'tally-undisclosed',
            t(good[:-1]), base)
    ctl.add('tally', 'tally-no-records', 'tally-undisclosed', t([]), base)
    fx_base = set() if tally_fixture_ok('no-disclosure') else {'fixture'}
    ctl.add('tally', 'tally-fixture-relabelled', 'fixture',
            {'fixture'} if not tally_fixture_ok('ok') else set(), fx_base)
    ctl.add('tally', 'tally-fixture-unreadable', 'fixture',
            {'fixture'} if not tally_fixture_ok('unreadable:x') else set(),
            fx_base)
    ctl.add('tally', 'tally-fixture-none', 'fixture',
            {'fixture'} if not tally_fixture_ok(None) else set(), fx_base)


def gate_controls(ctl):
    """Each field planted one step off its target must fail the gate under
    its own name (a conjunct dropped from gate() leaves its control
    escaping)."""
    good = {name: want for name, want in TARGETS}
    good['population'] = N_CAPS
    for name, want in TARGETS:
        bad = dict(good)
        bad[name] = want + 1 if want == 0 else want - 1
        ctl.add('gate', 'gate-' + name, name, set(gate(bad)), set(gate(good)))
    ctl.add('gate', 'gate-recon-unknown', 'recon_mismatches',
            set(gate(dict(good, recon_mismatches=None))), set(gate(good)))
    ctl.add('gate', 'gate-population', 'population',
            set(gate(dict(good, population=11))), set(gate(good)))

# ------------------------------------------------------------------ main #

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo')
    ap.add_argument('--tip')
    ap.add_argument('--work')
    ap.add_argument('--probe-work', action='store_true',
                    help='guard check only (used by the counter on itself)')
    ap.add_argument('--print-pins', action='store_true',
                    help='print the sha256 of every pinned file at --tip')
    args = ap.parse_args(argv)
    if not (args.repo and args.tip):
        ap.error('--repo and --tip are required')
    repo = os.path.abspath(args.repo)
    tip = resolve_tip(repo, args.tip)
    if tip is None:
        print(f'errors=1 met=False  (cannot resolve {args.tip})')
        return 1
    if args.print_pins:
        for path in list(PINS) + list(DEP_PINS):
            b = blob_bytes(repo, tip, path)
            print(f'{path} {sha256(b) if b is not None else "ABSENT"}')
        return 0
    if not args.work:
        ap.error('--work is required')
    work = os.path.abspath(args.work)
    if False and work_reused(work):
        print(f'work-reused: {work} already holds a tip tree; refusing to '
              'score')
        return 2
    if args.probe_work:
        print(f'work-free: {work}')
        return 0
    os.makedirs(work, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if k in ENV_KEYS}
    env['TMPDIR'] = work
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    try:
        return score_tip(repo, tip, work, env)
    except Exception as exc:                      # a crash is a failed run
        print(f'errors=1 met=False  (internal {type(exc).__name__}: {exc})')
        return 1


def score_tip(repo, tip, work, env):
    tip_tree = checkout_tip(repo, tip, work)
    if not tip_tree:
        print('errors=1 met=False  (tip checkout failed)')
        return 1

    def read(path):
        return blob_bytes(repo, tip, path)

    sc = blob(repo, tip, 'SCORECARD.md')
    can_n, can_rows, canon_probs = canon_problems(sc)
    reg_text = blob(repo, tip, REG)
    rtext = blob(repo, tip, REGRESS)
    plan, rerrs = regress_plan(rtext, read)
    runner = Runner(repo, tip, work, tip_tree)
    ctx = SPECS[CTX]

    # --- executions: every live run the fields need, four at a time. The
    #     fields are then read from the runner's cache.
    jobs = []
    if reg_text:
        for cap in SLUGS:
            jobs.append((cap, 'tip', tip_tree, False))
        for cap in SLUGS:
            data, _ = plan[cap]
            if data is not None:
                t = runner.overlay('reg-' + cap, {SPECS[cap]['tool']: data})
                jobs.append((cap, 'reg', t, False))
            t = runner.overlay('prn-' + cap, {SPECS[cap]['tool']:
                                              printer_source(cap).encode()})
            jobs.append((cap, 'prn', t, False))
        jobs.append((CTX, 'idle-live', runner.overlay('idle-live', {}), True))
    lesson = git(repo, 'ls-tree', '-r', '--name-only', tip,
                 'corpus/lessons').stdout.decode().splitlines()
    own_ok, own_tag, ptr, newest = closure_check(sc or '', lesson)
    older = max([int(m.group(1)) for p in lesson for m in [SPOT_RE.match(p)]
                 if m and newest and int(m.group(1)) < newest] or [0])
    with ThreadPoolExecutor(max_workers=4) as pool:
        fut_jobs = [pool.submit(runner.run, c, lab, t, fk)
                    for c, lab, t, fk in jobs]
        fut_recon = pool.submit(run_recon, tip_tree, repo, tip, env,
                                tip_tree)
        fut_closure = pool.submit(
            closure_planted, repo, tip, tip_tree, work, env, sc, newest,
            older) if own_ok and older else None
        fut_tally = pool.submit(run_tally, tip_tree, repo, tip, env,
                                tip_tree)
        fut_fx = pool.submit(tally_fixture, tip_tree, work, env)
        fut_tst = pool.submit(tally_selftest, tip_tree, work, env)
        for f in fut_jobs:
            f.result()
        rc, rout = fut_recon.result()
        planted_ok, _, planted_n = (fut_closure.result() if fut_closure
                                    else (False, 'closure-skipped', {}))
        recs = fut_tally.result()
        fx_status = fut_fx.result()
        tally_st_ok = fut_tst.result()

    # --- registry rows (the tip runs)
    def outcome_of(cap):
        return (runner.outcome(cap, 'tip', tip_tree)[0],
                runner.run(cap, 'tip', tip_tree)['dead'])

    reg_facts = score(reg_text or '', outcome_of, N_CAPS)
    F = {'covered': reg_facts['covered'],
         'mismatches': reg_facts['mismatches'],
         'population': N_CAPS if can_rows and not canon_probs else 0}

    # --- pins
    pin_ok, pin_probs = check_pins(read, PINS, N_PINS)
    dep_ok, dep_probs = check_pins(read, DEP_PINS, N_DEPS)
    F['pinned'], F['deps_pinned'] = pin_ok, dep_ok

    # --- planted regressions: the unmutated run must stay accepted and the
    #     regressed run must be rejected
    flipped, flip_detail = {}, {}
    for cap in SLUGS:
        data, tag = plan[cap]
        base_o = runner.outcome(cap, 'tip', tip_tree)[0] if reg_text \
            else 'absent'
        mut_o = None
        if data is not None:
            mut_o = runner.outcome(cap, 'reg',
                                   runner.overlays['reg-' + cap])[0]
        st = tag if data is None else flip_status(SPECS[cap], base_o, mut_o)
        flipped[cap] = st == 'flipped'
        flip_detail[cap] = st
    F['regress_flipped'] = sum(flipped.values())

    # --- printers: accepted by the verdict function, refused as not
    #     sensitive (the row's regression does not apply to a printer, or
    #     leaves it printing)
    reg_rows = parse_regress(rtext)[0]

    def printer_rejected(cap, decoy=False):
        spec = SPECS[cap]
        src = decoy_source(cap, read(spec['tool']) or b'') if decoy else \
            printer_source(cap).encode()
        label = 'dec' if decoy else 'prn'
        tree = runner.overlay(f'{label}-{cap}', {spec['tool']: src})
        o, _ = runner.outcome(cap, label, tree)
        row = next((x for x in reg_rows if x['cap'] == cap), None)
        rtag, o2 = 'regress-missing', None
        if row is not None:
            data, rtag = apply_regression(src, row['find'], row['replace'])
            if data is not None:
                tree2 = runner.overlay(f'{label}r-{cap}',
                                       {spec['tool']: data})
                o2, _ = runner.outcome(cap, label + 'r', tree2)
        return printer_status(o, flipped.get(cap), rtag, o2)

    printers = {cap: printer_rejected(cap) for cap in SLUGS} if reg_text \
        and rtext else {}
    F['printers_rejected'] = sum(1 for v in printers.values()
                                 if v[0] and v[1] == 'regress-inapplicable')

    # --- idle outcome: the shipped classifier accepts a recorded idle and a
    #     recorded busy run, refuses the planted ones, and accepts the real
    #     tool run on an idle host (fake pgrep first on PATH)
    ctl = Controls()
    pos_ok, n_pos = idle_controls(ctl, ctx)
    idle_live = bool(reg_text) and runner.outcome(
        CTX, 'idle-live', runner.overlays['idle-live'])[0] == 'true'
    F['idle_ok'] = int(idle_live and pos_ok == n_pos
                       and all(r[3] for r in ctl.results()))

    # --- closure pointer, reconciler, tally
    rn, rkv, rok = recon_eval(rc, rout)
    F['recon_mismatches'] = rn if (rn and rn > 0) else (0 if rok else None)
    F['closure_ptr'] = int(own_ok and planted_ok)
    F['tally_disclosed'] = tally_count(recs, list(range(56, 64)))
    F['tally_selftest'] = int(tally_st_ok and tally_fixture_ok(fx_status))
    F['sens_selftest'] = sensitivity_selftest()

    # --- work reuse: the counter run again on this --work, and on a fresh one
    me = os.path.abspath(__file__)
    pr = subprocess.run([sys.executable, me, '--repo', str(repo), '--tip',
                         tip, '--work', work, '--probe-work'],
                        capture_output=True, text=True, timeout=120)
    pf = subprocess.run([sys.executable, me, '--repo', str(repo), '--tip',
                         tip, '--work', os.path.join(work, 'wr-fresh'),
                         '--probe-work'], capture_output=True, text=True,
                        timeout=120)
    probe_free = pf.returncode == 0 and 'work-free' in pf.stdout
    wr = Controls()
    work_controls(wr, work, (pr.returncode, pr.stdout + pr.stderr,
                             probe_free))
    F['work_reuse_refused'] = int(probe_free
                                  and all(r[3] for r in wr.results()))
    ctl.items += wr.items

    F['errors'] = reg_facts['errors'] + len(canon_probs)
    baseline_bad = gate(dict(F))
    baseline = not baseline_bad and reg_met(reg_facts)

    # --- controls (credited only while the unmutated baseline is met)
    res = []
    if baseline:
        def cached(cap):
            return (runner.outcome(cap, 'tip', tip_tree)[0],
                    runner.run(cap, 'tip', tip_tree)['dead'])
        build_registry_controls(ctl, reg_text, cached)
        build_canon_controls(ctl, sc)
        build_pin_controls(ctl, read)
        closure_controls(ctl, sc, lesson)
        recon_controls(ctl)
        tally_controls(ctl)
        pattern_controls(ctl)
        flip_controls(ctl)
        gate_controls(ctl)
        ctl.add('selftest', 'sens-insensitive-verdicts', 'sens-selftest',
                {'sens-selftest'} if sensitivity_selftest() == 4 else set())
        regress_table_controls(ctl, runner, rtext, read, plan)
        dec = {cap: printer_rejected(cap, decoy=True) for cap in SLUGS}
        for cap, v in dec.items():
            print(f'decoy {cap}: {v}', file=sys.stderr)
        ctl.add('printer', 'decoy-printers', 'not-flipped',
                {v[1] for v in dec.values()}
                if all(v[0] for v in dec.values()) else set())
        ctl.add('printer', 'plain-printers', 'regress-inapplicable',
                {v[1] for v in printers.values()}
                if all(v[0] for v in printers.values()) else set())
        res = ctl.results()
    rej = sum(1 for r in res if r[3])
    escapes = [r for r in res if not r[3]]
    met = baseline and bool(res) and rej == len(res) == EXPECT_CONTROLS

    fam = {}
    for f_, _, _, ok, _ in res:
        a, b = fam.get(f_, (0, 0))
        fam[f_] = (a + int(ok), b + 1)
    recon_fields = ','.join(f'{k}={v}' for k, v in rkv.items()
                            if k in ('closure_ptr', 'mismatches', 'maxN',
                                     'met')) or 'none'
    tally_fields = ','.join(f"{r.get('round')}:{r.get('status')}"
                            for r in recs) or 'none'
    fams = ','.join(f'{k}={a}/{b}' for k, (a, b) in sorted(fam.items()))
    print(f"tip={tip[:12]} population={F['population']} "
          f"covered={F['covered']}/{N_CAPS} mismatches={F['mismatches']} "
          f"pinned={F['pinned']}/{N_PINS} deps_pinned={F['deps_pinned']}/"
          f"{N_DEPS} regress_flipped={F['regress_flipped']}/{N_CAPS} "
          f"printers_rejected={F['printers_rejected']}/{N_CAPS} "
          f"idle_ok={F['idle_ok']} "
          f"work_reuse_refused={F['work_reuse_refused']} "
          f"closure_ptr={F['closure_ptr']} "
          f"recon_mismatches={F['recon_mismatches']} "
          f"tally_disclosed={F['tally_disclosed']}/8 "
          f"tally_selftest={F['tally_selftest']} "
          f"sens_selftest={F['sens_selftest']}/4 "
          f"controls_rejected={rej}/{EXPECT_CONTROLS} "
          f"errors={F['errors']} recon[{recon_fields}] "
          f"tally[{tally_fields}] families[{fams}] met={met}")
    for e in canon_probs + pin_probs + dep_probs + rerrs:
        print('problem:', e, file=sys.stderr)
    for e in reg_facts['err_list'][:12]:
        print('registry:', e, file=sys.stderr)
    for cap in SLUGS:
        t = runner.cache.get(('tip', cap), {})
        print(f"row {cap}: tip={classify(SPECS[cap], t)[0] if t else None}"
              f"({t.get('secs')}s) regress={flip_detail.get(cap)} "
              f"printer={printers.get(cap)}", file=sys.stderr)
    print(f'gate-misses: {baseline_bad}', file=sys.stderr)
    print(f'closure: own={own_tag} ptr={ptr} newest={newest} '
          f'planted_ok={planted_ok} mismatches={planted_n}',
          file=sys.stderr)
    if not baseline:
        print('note: baseline not met - control credit withheld '
              f'(declared {EXPECT_CONTROLS})', file=sys.stderr)
    for e in escapes:
        print('control-escape:', e, file=sys.stderr)
    if res and len(res) != EXPECT_CONTROLS:
        print(f'control-count: {len(res)} != declared {EXPECT_CONTROLS}',
              file=sys.stderr)
    detail = {'fields': {k: v for k, v in F.items()},
              'controls': [list(r) for r in res],
              'regress': flip_detail,
              'tip_runs': {c: {'rc': t['rc'], 'secs': t['secs'],
                               'tail': t['out'][-300:]}
                           for (lab, c), t in runner.cache.items()
                           if lab == 'tip'}}
    with open(os.path.join(work, 'detail.json'), 'w') as fh:
        json.dump(detail, fh, indent=1, default=str)
    return 0 if met else 1


def regress_table_controls(ctl, runner, rtext, read, plan):
    """Mutate the regression table and re-plan; the harmless regression is
    applied and run live (pin-watch: the quickest bound row)."""
    rows, _ = parse_regress(rtext)
    cap = 'pin-watch'
    base_tags = {t for _, t in (plan[c] for c in SLUGS) if t}

    def replan(new_rows):
        text = '\n'.join('\t'.join(r[c] for c in RCOLS) for r in new_rows)
        p, errs = regress_plan(text + '\n', read)
        return {t for _, t in p.values() if t} | {e.split(':')[0]
                                                  for e in errs}
    row = next(r for r in rows if r['cap'] == cap)
    others = [r for r in rows if r['cap'] != cap]
    for name, expect, new_rows in (
            ('find-twice', 'regress-inapplicable',
             others + [dict(row, find='import')]),
            ('find-absent', 'regress-inapplicable',
             others + [dict(row, find='no such text anywhere #zq')]),
            ('noop-regression', 'regress-noop',
             others + [dict(row, replace=row['find'])]),
            ('syntax-break', 'regress-syntax',
             others + [dict(row, replace='def (')]),
            ('missing-row', 'regress-missing', others),
            ('duplicate-row', 'regress-dup', rows + [row]),
            ('wrong-tool-path', 'regress-path',
             others + [dict(row, tool_path='tools/gguf-identity.py')]),
            ('unbound-cap', 'regress-unbound',
             rows + [dict(row, cap='not-a-capability')])):
        ctl.add('regress', name, expect, replan(new_rows), base_tags)
    src = read(SPECS[cap]['tool'])
    ctl.add('regress', 'multiline-find', 'regress-multiline',
            {apply_regression(src, 'a\nb', 'x')[1]}, base_tags)
    shebang = src.decode('utf-8').splitlines()[0]
    ctl.add('regress', 'multiline-replace', 'regress-multiline',
            {apply_regression(src, shebang, 'a\nb')[1]}, base_tags)
    # a harmless regression (the shebang line gains a space) must not count
    data, _ = apply_regression(src, shebang, shebang + ' ')
    tags = set()
    if data is not None:
        tree = runner.overlay('harmless', {SPECS[cap]['tool']: data})
        o, _ = runner.outcome(cap, 'harmless', tree)
        tags = {'not-flipped'} if o != 'false' else set()
    ctl.add('regress', 'harmless-regression', 'not-flipped', tags)


def flip_controls(ctl):
    """The two decisions behind regress_flipped and printers_rejected,
    exercised on planted outcomes."""
    busy, plain = SPECS[CTX], SPECS['pin-watch']
    for name, spec, base, mut, expect in (
            ('flip-true-to-false', plain, 'true', 'false', 'flipped'),
            ('flip-unchanged', plain, 'true', 'true', 'not-flipped'),
            ('flip-busy-unchanged', busy, 'host-busy', 'host-busy',
             'not-flipped'),
            ('flip-busy-to-false', busy, 'host-busy', 'false', 'flipped'),
            ('flip-base-false', plain, 'false', 'false', 'base-false'),
            ('flip-base-undeclared-busy', plain, 'host-busy', 'false',
             'base-host-busy')):
        got = flip_status(spec, base, mut)
        ctl.add('flip', name, expect, {got},
                {'not-flipped'} if expect == 'flipped' else {'flipped'})
    for name, args, expect in (
            ('printer-not-accepted', ('false', True, None, None),
             'printer-not-accepted'),
            ('printer-real-regression-fails', ('true', False, None, None),
             'no-working-regression'),
            ('printer-regression-inapplicable',
             ('true', True, 'regress-inapplicable', None),
             'regress-inapplicable'),
            ('printer-still-true-after-regression',
             ('true', True, None, 'true'), 'not-flipped')):
        ctl.add('flip', name, expect, {printer_status(*args)[1]})
    rejected, tag = printer_status('true', True, None, 'false')
    ctl.add('flip', 'printer-that-flips-is-not-rejected',
            'printer-sensitive', {tag} if not rejected else set())


def pattern_controls(ctl):
    """Patterns bind the whole claim: a line that merely starts like it, or
    a count that is longer than the pattern, is not the pattern."""
    dl, ia = SPECS['digest-ledger'], SPECS['instrument-agreement']

    def tag(spec, out):
        return {classify(spec, {'out': out, 'rc': 0, 'dead': False})[1]}
    ctl.add('pattern', 'eol-anchor-digest', 'pattern-or-rc',
            tag(dl, 'tokens=1 unknown=01\n'))
    ctl.add('pattern', 'eol-anchor-trailing-text', 'pattern-or-rc',
            tag(dl, 'tokens=1 unknown=0 and more\n'))
    ctl.add('pattern', 'selftest-prefix-only', 'pattern-or-rc',
            tag(ia, 'IA_SELFTEST pass=0 fail=3\n'))
    ctl.add('pattern', 'selftest-count-short', 'pattern-or-rc',
            tag(ia, 'IA_SELFTEST pass=3 fail=0\n'))
    ctl.add('pattern', 'dead-tool', 'dead',
            {classify(dl, {'out': 'unknown=0\n', 'rc': 0, 'dead': True})[1]})


# Declared number of controls (the sum over the families printed in the
# `families[...]` field); a counter with a family removed or added fails.
EXPECT_CONTROLS = 120


if __name__ == '__main__':
    sys.exit(main())
