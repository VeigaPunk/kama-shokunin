#!/usr/bin/env python3
"""Round-63 C2 counter: capability self-assessment bound to live checks,
with a sensitivity test that can fail.

Usage: python3 tools/round63-c2-counter.py --repo REPO --tip REV --work DIR

Frozen predicate (identical to .ufo/waves/round-63/controls/freeze.txt):
  C2-r63: at the tip, each of the 12 frozen capabilities in MANIFEST appears
  exactly once in the newest canonical capabilities list of SCORECARD.md
  (round 63) with its frozen row prefix; each is covered by a row of
  registry/capability-claims-r63.tsv that binds exactly its manifest run
  template (placeholders %T tip tree, %S scratch, %R repo, TIPREV tip);
  the template is executed live in an allowlisted environment (PATH, HOME,
  LANG, LC_ALL, TMPDIR only) and its outcome - verdict true (pattern emitted,
  exit 0) or, for context-capacity-receipt only, verdict host-busy (exit 2
  `host-not-idle-before-K1` with a foreign llama-server listed by pgrep
  before and after) - equals the recorded verdict or is one of the row's two
  declared outcomes; the verdict is sensitive - the verdict function applied
  to the output with the pattern removed until it no longer occurs, and to
  the output with the exit code changed (0 to 1, else to 0), flips to false - and the
  counter's own sensitivity self-test rejects all 4 planted defective
  verdict functions; no bound target path is dead; mismatches=0; the lane's
  own self-description reconciler `tools/round42-selfdesc-reconcile.py
  --repo REPO --tip TIP` reports mismatches=0 (the base tip reports 8); and
  all 12 control families are rejected, each by the failure it names and
  credited only while the unmutated baseline itself is met, errors=0.

The counter trusts nothing recorded: it re-executes each bound command at
the tip tree, recomputes every verdict, and feeds the same scoring 12
mutated registries (the control families). Output: one line, exit 0 iff
met. Every scratch path is under --work.
"""
import argparse
import os
import re
import subprocess
import sys

REG = 'registry/capability-claims-r63.tsv'
ROW_RE = re.compile(r'^\|\s*([a-z0-9-]+)\s*\|')
HEAD_RE = re.compile(r'canonical list as of round\s*(\d+)', re.I)
ENV_KEYS = ('PATH', 'HOME', 'LANG', 'LC_ALL')
HOSTBUSY_TEXT = 'host-not-idle-before-K1'

MODEL = os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf')
MSHA = '270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d'
# (slug, 48-char prefix of the canonical row, [allowed run templates]).
# A bound row's `run` must equal its manifest template; its `quote` must be a
# >=8-char substring of the prefix. `alt`: a second declared outcome.
_MANIFEST = [
    ('sources-registry',
     '| sources-registry | Curate where kama learns: t',
     [{'id': 'census',
       'run': 'python3 %T/tools/sources-append-only.py --selftest',
       'pattern': '45/45 selftest cases passed'}]),
    ('ollama-offline-evidence-replay',
     '| ollama-offline-evidence-replay | Reconcile ca',
     [{'id': 'selftest',
       'run': 'python3 %T/tools/kama-ollama-evidence.py --selftest',
       'pattern': '"failed": 0'}]),
    ('live-llamacpp-lifecycle',
     '| live-llamacpp-lifecycle | Start the pinned l',
     [{'id': 'live',
       'run': 'python3 %T/tools/kama-llamacpp-live.py --model ' + MODEL
              + ' --model-sha256 ' + MSHA,
       'pattern': '"outcome": "pass"'}]),
    ('gguf-declared-identity-replay',
     '| gguf-declared-identity-replay | Decode bound',
     [{'id': 'selftest',
       'run': 'python3 %T/tools/gguf-identity.py --selftest',
       'pattern': '"status": "passed"'}]),
    ('context-capacity-receipt',
     '| context-capacity-receipt | Run the registere',
     [{'id': 'cell',
       'run': 'python3 %T/tools/kama-context-capacity.py --only K1'
              + ' --host-idle-timeout 20'
              + ' --scratch %S/context-capacity --out %S/cc.json',
       'pattern': '"all_ports_closed": true',
       'alt': HOSTBUSY_TEXT}]),
    ('instrument-agreement',
     '| instrument-agreement | Run a lane instrument',
     [{'id': 'selftest',
       'run': 'python3 %T/tools/instrument-agreement.py --selftest',
       'pattern': 'IA_SELFTEST pass='}]),
    ('pin-watch',
     '| pin-watch | List upstream release tags for e',
     [{'id': 'selftest',
       'run': 'python3 %T/tools/pin-watch.py selftest',
       'pattern': 'selftest pass=9 fail=0'}]),
    ('digest-ledger',
     '| digest-ledger | Find every full SHA-256 the',
     [{'id': 'scan',
       'run': 'python3 %T/tools/digest-ledger.py scan --repo %R --rev TIPREV',
       'pattern': 'unknown=0'}]),
    ('hexrun-census',
     '| hexrun-census | Find every lower-case hex ru',
     [{'id': 'scan',
       'run': 'python3 %T/tools/hexrun-census.py scan --repo %R --rev TIPREV',
       'pattern': 'unknown=0'}]),
    ('append-only-audit',
     '| append-only-audit | Set the lane\'s contract-',
     [{'id': 'selftest',
       'run': 'python3 %T/tools/append-only-audit.py --selftest'
              + ' --scratch %S/aoa',
       'pattern': 'AOA_SELFTEST pass='}]),
    ('live-receipt-replay',
     '| live-receipt-replay | Re-acquire a `kama-lla',
     [{'id': 'selftest',
       'run': 'python3 %T/tools/kama-live-replay.py --selftest'
              + ' --scratch %S/klr',
       'pattern': 'KLR_SELFTEST pass=48 fail=0'}]),
    ('live-ollama-lifecycle',
     '| live-ollama-lifecycle | Start the pinned Ol',
     [{'id': 'live',
       'run': 'python3 %T/tools/kama-ollama-live.py --work %S/ollama'
              + ' --nonce ctrun0001',
       'pattern': '"verdict": "MODEL_OK"'}]),
]
MANIFEST = {slug: (prefix, runs) for slug, prefix, runs in _MANIFEST}
MIN_ROWS = len(_MANIFEST)
EXPECT_FAMILIES = 12
EXPECT_SELFTEST = 4

COLS = ['cap', 'quote', 'binding', 'run', 'pattern', 'verdict',
        'observed', 'note']
_EXEC_CACHE = {}


def git(repo, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    return subprocess.run(['git', '-C', str(repo), *args],
                          capture_output=True, env=env)


def blob(repo, rev, path):
    p = git(repo, 'show', f'{rev}:{path}')
    return p.stdout.decode('utf-8', 'replace') if p.returncode == 0 else None


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
    """(round_no, rows, problems) for the newest canonical list."""
    can_n, can_rows = canonical_rows(sc_text)
    probs = []
    if not can_rows:
        return can_n, can_rows, ['no canonical list section at tip']
    if can_n != 63:
        probs.append(f'newest canonical list is round {can_n}')
    slugs = [s for s, _ in can_rows]
    expected = [s for s, _, _ in _MANIFEST]
    if len(slugs) != len(set(slugs)) or not set(expected).issubset(slugs):
        probs.append('canonical rows must contain each frozen capability '
                     f'once: {slugs}')
    for slug, prefix, _ in _MANIFEST:
        row_text = next((t for seen, t in can_rows if seen == slug), '')
        if not row_text.startswith(prefix):
            probs.append(f'prefix:{slug}')
    return can_n, can_rows, probs


def parse_registry(text):
    rows, errors = [], []
    if not text:
        return rows, ['registry absent']
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
            errors.append(f'cols={len(cells)}')
            continue
        rows.append(dict(zip(header, cells)))
    if header is None:
        errors.append('header')
    return rows, errors


def placeholders(run, tip_tree, scratch, repo, tip):
    return (run.replace('%T', tip_tree).replace('%S', scratch)
               .replace('%R', str(repo)).replace('TIPREV', tip))


# ------------------------------------------------------ verdict function #

def verdict_fn(out, rc, dead, pat):
    """The one verdict function every bound row is graded with."""
    return (not dead) and bool(pat) and pat in out and rc == 0


def strip_all(out, pat):
    """Remove the pattern until it no longer occurs (a replacement token
    could itself carry the pattern; removal cannot, and every pass shortens
    the text, so the loop ends)."""
    while pat and pat in out:
        out = out.replace(pat, '')
    return out


def refusal_fn(out, rc, dead, pat):
    """Verdict function of the declared refusal outcome (exit 2 + text)."""
    return (not dead) and bool(pat) and pat in out and rc == 2


def is_sensitive(out, rc, dead, pat, vfn=verdict_fn):
    """True iff the verdict is true on the real output and flips to false
    both when the pattern is removed and when the exit code is changed
    (0 -> 1, anything else -> 0)."""
    if not vfn(out, rc, dead, pat):
        return False
    return ((not vfn(strip_all(out, pat), rc, dead, pat))
            and (not vfn(out, 1 if rc == 0 else 0, dead, pat)))


def r62_formula(out, rc, dead, pat):
    """The round-62 sensitivity expression, kept to witness its defect."""
    mut = out.replace(pat, '__kama_mut__')
    return not (pat in mut and rc == 0 and not dead)


def sensitivity_selftest():
    """Plant defective verdict functions and a pattern-bearing token: the
    sensitivity test must call each insensitive. Returns the passed count
    (expected EXPECT_SELFTEST)."""
    n = 0
    out, pat = 'xx ok=1 yy', 'ok=1'
    n += int(not is_sensitive(out, 0, False, pat,
                              vfn=lambda o, rc, d, p: True))
    n += int(not is_sensitive(out, 0, False, pat,
                              vfn=lambda o, rc, d, p: rc == 0 and not d))
    n += int(not is_sensitive(out, 0, False, pat,
                              vfn=lambda o, rc, d, p: p in o and not d))
    # the round-62 expression called pattern 'a' in output 'a' insensitive
    # only by accident of its token; the corrected test must not share that
    # defect: a real verdict on a pattern that the old token would carry
    n += int(is_sensitive('a', 0, False, 'a') and not r62_formula(
        'a', 0, False, 'a'))
    return n


# ----------------------------------------------------------------- scoring #

def score(reg_text, scorer, manifest=MANIFEST, population=None):
    """Score a registry text. `scorer(row) -> (verdict_str, observed,
    sensitive, dead)` for bound rows. Returns facts."""
    rows, errors = parse_registry(reg_text)
    facts = {'population': len(population or manifest),
             'rows': len(rows), 'covered': 0, 'bound': 0,
             'eval_lines': 0, 'sensitive': 0, 'dead': 0,
             'mismatches': 0, 'errors': len(errors), 'host_busy': 0}
    errs = list(errors)
    covered = set()
    seen = {}
    for row in rows:
        cap = row['cap']
        seen[cap] = seen.get(cap, 0) + 1
        if cap not in manifest:
            errs.append(f'unbound-cap:{cap}')
            continue
        if seen[cap] > 1:
            errs.append(f'dup-row:{cap}')
            continue
        prefix, templates = manifest[cap]
        if row['quote'] not in prefix or len(row['quote']) < 8:
            errs.append(f'quote:{cap}')
            continue
        tpl = next((t for t in templates if t['id'] == row['binding']), None)
        if tpl is None:
            errs.append(f'binding:{cap}:{row["binding"]}')
            continue
        if row['run'] != tpl['run']:
            errs.append(f'run:{cap}')
            continue
        if row['pattern'] != tpl['pattern']:
            errs.append(f'pattern:{cap}')
            continue
        rec = row['verdict'].lower()
        if rec not in ('true', 'host-busy'):
            errs.append(f'verdict-value:{cap}:{rec}')
            continue
        if rec == 'host-busy' and 'alt' not in tpl:
            errs.append(f'hostbusy-not-declared:{cap}')
            continue
        facts['bound'] += 1
        outcome, observed, sensitive, dead = scorer(row)
        facts['dead'] += int(dead)
        facts['eval_lines'] += 1
        facts['sensitive'] += int(sensitive)
        facts['host_busy'] += int(outcome == 'host-busy')
        declared = {'true'} | ({'host-busy'} if 'alt' in tpl else set())
        ok = (outcome in declared
              and (outcome == rec or 'alt' in tpl))
        if not ok or (outcome == 'true' and not sensitive) or dead:
            facts['mismatches'] += 1
        want_obs = tpl['pattern'] if outcome == 'true' else tpl.get('alt', '')
        if row['observed'] and row['observed'] not in (want_obs or '') \
                and row['observed'] not in observed:
            facts['mismatches'] += 1
        covered.add(cap)
    facts['covered'] = len(covered)
    facts['err_list'] = errs
    facts['errors'] = len(errs)
    facts['tags'] = {e.split(':')[0] for e in errs}
    return facts


def pgrep_foreign():
    p = subprocess.run(['pgrep', '-x', 'llama-server'],
                       capture_output=True, text=True)
    return sorted(int(x) for x in p.stdout.split() if x.isdigit())


def run_bound(row, templates, tip_tree, scratch, repo, tip, env):
    """Execute the row's bound run template. Returns (outcome, observed,
    sensitive, dead)."""
    tpl = next(t for t in templates if t['id'] == row['binding'])
    cmd = placeholders(tpl['run'], tip_tree, scratch, repo, tip)
    dead = False
    m = re.search(r'(%T|[^ ]+)/tools/([a-z0-9-]+\.py)', tpl['run'])
    tool_rel = 'tools/' + m.group(2) if m else None
    if tool_rel and not os.path.isfile(os.path.join(tip_tree, tool_rel)):
        dead = True
    before = pgrep_foreign() if 'alt' in tpl else None
    try:
        p = subprocess.run(['bash', '-c', cmd], capture_output=True,
                           text=True, timeout=900, cwd=tip_tree, env=env)
        out = p.stdout + p.stderr
        rc = p.returncode
    except subprocess.TimeoutExpired:
        out, rc = 'TIMEOUT', 124
    pat = tpl['pattern']
    if verdict_fn(out, rc, dead, pat):
        return ('true', pat, is_sensitive(out, rc, dead, pat), dead)
    if 'alt' in tpl and rc == 2 and tpl['alt'] in out and not dead:
        after = pgrep_foreign()
        if before and after:
            # the refusal is itself the observed outcome; sensitivity of the
            # alternative is the same flip on its own pattern
            return ('host-busy', tpl['alt'],
                    is_sensitive(out, rc, dead, tpl['alt'],
                                 vfn=refusal_fn), dead)
    return ('false', out[:400], False, dead)


def score_registry(reg_text, tip_tree, scratch, repo, tip, env,
                   population=None, manifest=MANIFEST):
    def scorer(row):
        cap = row['cap']
        key = (tip, cap)
        if key not in _EXEC_CACHE:
            _EXEC_CACHE[key] = run_bound(row, manifest[cap][1], tip_tree,
                                         scratch, repo, tip, env)
        return _EXEC_CACHE[key]
    return score(reg_text, scorer, manifest=manifest, population=population)


def is_met(f):
    return (f['covered'] == f['population'] and f['mismatches'] == 0
            and f['errors'] == 0 and f['dead'] == 0
            and f['bound'] >= f['population'])


def controls(reg_text, tip_tree, scratch, repo, tip, env, population,
             canon_text):
    """12 control families: each a mutated registry (or canonical list)
    re-scored by the same scorer; every family must score not-met."""
    lines = [l for l in reg_text.splitlines() if l.strip()]
    header = [l for l in lines if l.startswith('cap\t')][0]
    data = [l for l in lines if '\t' in l and not l.startswith('cap\t')
            and not l.startswith('#')]

    def rescore(text):
        return score_registry(text, tip_tree, scratch, repo, tip, env,
                              population=population)

    def j(rows):
        return header + '\n' + '\n'.join(rows) + '\n'

    def cells(l):
        return l.split('\t')

    muts = {}
    muts['drop'] = j(data[1:])
    muts['rename'] = j(data).replace('sources-registry', 'sources-fakery', 1)
    muts['binding'] = j(l.replace('\tlive\t', '\tselftest\t', 1)
                        if '\tlive\t' in l else l for l in data)
    muts['verdict'] = j(data).replace('\ttrue\t', '\tfalse\t', 1)
    muts['quote'] = j(cells(l)[0] + '\tNOT-A-PREFIX-QUOTE\t'
                      + '\t'.join(cells(l)[2:]) for l in data)
    muts['free'] = j(['sources-registry\tCurate where\tfree\t'
                      'bash -c "echo ok"\tok\ttrue\techo\tfree'] + data[1:])
    muts['weak'] = j(data).replace('45/45 selftest cases passed', 'pass', 1)
    muts['notobs'] = j(re.sub(r'\t(live|selftest|scan|cell|census)\t',
                              '\tnotobs\t', l) for l in data)
    # round-63 families
    # 9: host-busy declared on a row that has no declared alternative
    muts['hostbusy'] = j(data).replace('\ttrue\t', '\thost-busy\t', 1)
    # 10: the same capability bound twice
    muts['duprow'] = j(data + [data[0]])
    # 11: a forged `observed` that the live output never carried
    muts['observed'] = j(
        '\t'.join(cells(l)[:6] + ['FORGED-OBSERVATION'] + cells(l)[7:])
        for l in data)
    # each control must be rejected for the reason it names: a mutation
    # that a failing baseline would reject anyway earns no credit
    expect = {'drop': 'covered', 'rename': 'unbound-cap',
              'binding': 'binding', 'verdict': 'verdict-value',
              'quote': 'quote', 'free': 'binding', 'weak': 'pattern',
              'notobs': 'binding', 'hostbusy': 'hostbusy-not-declared',
              'duprow': 'dup-row', 'observed': 'mismatch'}
    rejected = 0
    detail = {}
    for name, text in muts.items():
        f = rescore(text)
        tags = set(f['tags'])
        if f['covered'] < f['population']:
            tags.add('covered')
        if f['mismatches']:
            tags.add('mismatch')
        met = is_met(f)
        hit = (not met) and expect[name] in tags
        detail[name] = {'met': met, 'hit': hit, 'tags': sorted(tags)}
        if hit:
            rejected += 1
    # 12: the canonical list loses one frozen row - judged by the same
    # canonical-list rule main() applies, not by the registry
    lines_c = (canon_text or '').splitlines()
    kept = [l for l in lines_c if not l.startswith('| sources-registry |')]
    _, _, probs = canon_problems('\n'.join(kept))
    detail['canon-drop'] = {'met': not probs, 'hit': bool(probs),
                            'tags': probs[:2]}
    if probs:
        rejected += 1
    return rejected, len(muts) + 1, detail


def selfdesc_mismatches(tip_tree, repo, tip, env):
    """Run the lane's self-description reconciler at the tip; return its
    mismatch count, or None when it printed no count."""
    p = subprocess.run(
        [sys.executable, os.path.join(tip_tree, 'tools',
                                      'round42-selfdesc-reconcile.py'),
         '--repo', str(repo), '--tip', tip],
        capture_output=True, text=True, env=env, cwd=tip_tree, timeout=600)
    m = re.search(r'mismatches=(\d+)', p.stdout)
    return int(m.group(1)) if m and p.returncode == 0 else (
        int(m.group(1)) if m else None)


def checkout_tip(repo, tip, work):
    tree = os.path.join(work, 'tip')
    if os.path.isdir(tree):
        return tree
    os.makedirs(tree, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    archive = subprocess.Popen(['git', '-C', str(repo), 'archive', tip],
                               stdout=subprocess.PIPE, env=env)
    tar = subprocess.run(['tar', '-x', '-C', tree], stdin=archive.stdout)
    archive.stdout.close()
    archive_rc = archive.wait()
    return tree if tar.returncode == 0 and archive_rc == 0 else None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True)
    ap.add_argument('--tip', required=True)
    ap.add_argument('--work', required=True)
    args = ap.parse_args(argv)
    repo = os.path.abspath(args.repo)
    work = os.path.abspath(args.work)
    scratch = os.path.join(work, 'run')
    for d in (work, scratch):
        os.makedirs(d, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if k in ENV_KEYS}
    env['TMPDIR'] = scratch

    tip_tree = checkout_tip(repo, args.tip, work)
    if not tip_tree:
        print('errors=1 met=False  (tip checkout failed)')
        return 1

    sc = blob(repo, args.tip, 'SCORECARD.md')
    can_n, can_rows, canon_mismatch = canon_problems(sc)
    population = ([(slug, MANIFEST[slug][0]) for slug, _, _ in _MANIFEST]
                  if can_rows else None)

    reg_text = blob(repo, args.tip, REG)
    st = sensitivity_selftest()
    facts = score_registry(reg_text or '', tip_tree, scratch, repo, args.tip,
                           env, population=population)
    rejected, total, cdetail = (controls(
        reg_text, tip_tree, scratch, repo, args.tip, env, population, sc)
        if reg_text else (0, EXPECT_FAMILIES, {}))

    selfdesc = selfdesc_mismatches(tip_tree, repo, args.tip, env)
    baseline = bool(can_rows) and not canon_mismatch and is_met(facts)
    credited = rejected if baseline else 0
    met = (baseline and selfdesc == 0
           and credited == total == EXPECT_FAMILIES
           and st == EXPECT_SELFTEST and population is not None
           and len(population) == MIN_ROWS
           and facts['sensitive'] == facts['bound'])
    print(f"population={facts['population']} rows={facts['rows']} "
          f"covered={facts['covered']}/{facts['population']} "
          f"bound={facts['bound']} eval_lines={facts['eval_lines']} "
          f"sensitive={facts['sensitive']}/{facts['bound']} "
          f"dead={facts['dead']} host_busy={facts['host_busy']} "
          f"mismatches={facts['mismatches']} canonical={can_n} "
          f"selfdesc_mismatches={selfdesc} "
          f"sens_selftest={st}/{EXPECT_SELFTEST} "
          f"controls_rejected={credited}/{total} "
          f"errors={facts['errors'] + len(canon_mismatch)} met={met}")
    for e in canon_mismatch + facts['err_list'][:8]:
        print('error:', e, file=sys.stderr)
    if not baseline:
        print('note: baseline not met - control credit withheld '
              f'(would be {rejected}/{total})', file=sys.stderr)
    for k, v in cdetail.items():
        if not v['hit']:
            print(f'control-escape: {k} {v}', file=sys.stderr)
    return 0 if met else 1


if __name__ == '__main__':
    sys.exit(main())
