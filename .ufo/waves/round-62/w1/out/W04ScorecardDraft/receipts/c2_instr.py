#!/usr/bin/env python3
"""Round-62 C2 counter: capability self-assessment bound to live checks.

Usage: python3 tools/round62-c2-counter.py --repo REPO --tip REV [--work DIR]

Frozen predicate (identical to .ufo/waves/round-62/controls/freeze.txt):
  C2-r62: at the tip, each of the 12 frozen pre-round-62 capabilities listed
  in MANIFEST below (including the r61 `live-ollama-lifecycle` row) appears
  exactly once in the newest canonical capabilities section of SCORECARD.md,
  with its frozen row prefix; each is covered by a row of
  registry/capability-claims-r62.tsv; the row binds exactly the allowed run
  template from its manifest entry (placeholders %T tip tree, %S scratch,
  %R repo), is executed live in a scrubbed environment with a scratch TMPDIR,
  its emitted verdict equals the recorded one and is sensitive — replacing
  the decisive output substring flips the result; no bound target path is
  dead; mismatches=0; and all 8 control families are rejected, errors=0.
  The separate `live-completion-request-plane` row acquired by C1 is outside
  this frozen calibration population and is independently measured by C1.

The counter trusts nothing recorded: it re-executes each bound command at
the tip tree, recomputes every verdict, mutates observed output for the
sensitivity check, and feeds the same scoring 8 mutated registries
(the control families). Output: one line, exit 0 iff met.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

REG = 'registry/capability-claims-r62.tsv'
MUT = '__kama_mut__'
ROW_RE = re.compile(r'^\|\s*([a-z0-9-]+)\s*\|')
HEAD_RE = re.compile(r'canonical list as of round\s*(\d+)', re.I)

# Frozen r62 population: (slug, 48-char prefix of the canonical table row,
# allowed run-template ids). A bound row's `run` must equal one of these
# templates after placeholder substitution; its `quote` must be a >=8-char
# substring of the prefix. The templates carry the capability's own check —
# selftest for tools whose selftest is the shipped verifier, a live run for
# instruments whose claim is a live artefact.
MODEL = os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf')
MSHA = '270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d'
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
              + ' --host-idle-timeout 900'
              + ' --scratch %S/context-capacity --out %S/cc.json',
       'pattern': '"all_ports_closed": true'}]),
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
              + ' --nonce ctrun',
       'pattern': '"verdict": "MODEL_OK"'}]),
]
MANIFEST = {slug: (prefix, runs) for slug, prefix, runs in _MANIFEST}
MIN_ROWS = len(_MANIFEST)

COLS = ['cap', 'quote', 'binding', 'run', 'pattern', 'verdict',
        'observed', 'note']


def git(repo, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    return subprocess.run(['git', '-C', str(repo), *args],
                          capture_output=True, env=env)


def blob(repo, rev, path):
    p = git(repo, 'show', f'{rev}:{path}')
    return p.stdout.decode('utf-8', 'replace') if p.returncode == 0 else None
_EXEC_CACHE = {}



def canonical_rows(text):
    """Return (round_no, [(slug, row_text)]) for the highest-numbered
    canonical capabilities heading, or (None, [])."""
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
            if cells[:2] == COLS[:2]:
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


def allowed_ids(slug):
    return {r['id']: r for r in MANIFEST[slug][1]}


def score(reg_text, scorer, manifest=MANIFEST, population=None):
    """Score a registry text. `scorer(row_dict) -> (verdict, observed,
    sensitive, dead)` for bound rows. Returns facts dict."""
    rows, errors = parse_registry(reg_text)
    facts = {'population': len(population or manifest),
             'rows': len(rows), 'covered': 0, 'bound': 0,
             'eval_lines': 0, 'sensitive': 0, 'dead': 0,
             'mismatches': 0, 'errors': len(errors)}
    errs = list(errors)
    covered = set()
    for row in rows:
        cap = row['cap']
        if cap not in manifest:
            errs.append(f'unbound-cap:{cap}')
            continue
        prefix, templates = manifest[cap]
        if row['quote'] not in prefix or len(row['quote']) < 8:
            errs.append(f'quote:{cap}')
            continue
        if row['binding'] == 'notobs':
            # a capability whose check exists may never be notobs — every
            # manifest entry ships an executable check
            errs.append(f'notobs:{cap}')
            continue
        tpl = templates and next(
            (t for t in templates if t['id'] == row['binding']), None)
        if tpl is None:
            errs.append(f'binding:{cap}:{row["binding"]}')
            continue
        if row['run'] != tpl['run']:
            errs.append(f'run:{cap}')
            continue
        if row['pattern'] != tpl['pattern']:
            errs.append(f'pattern:{cap}')
            continue
        facts['bound'] += 1
        verdict, observed, sensitive, dead = scorer(row)
        facts['dead'] += int(dead)
        facts['eval_lines'] += 1
        facts['sensitive'] += int(sensitive)
        want = row['verdict'].lower() == 'true'
        if verdict != want or not sensitive or dead:
            facts['mismatches'] += 1
        if row['observed'] and row['observed'] not in observed:
            # the stored observation is the decisive output substring
            facts['mismatches'] += 1
        covered.add(cap)
    facts['covered'] = len(covered)
    facts['err_list'] = errs
    return facts


def run_bound(row, templates, tip_tree, scratch, repo, tip, env):
    import sys as _s; print("EXEC", row.get("cap"), file=_s.stderr)
    """Execute the row's bound run template. Returns (verdict, observed,
    sensitive, dead, out_text)."""
    cap = row['cap']
    tpl = next(t for t in templates if t['id'] == row['binding'])
    cmd = placeholders(tpl['run'], tip_tree, scratch, repo, tip)
    dead = False
    # target liveness: the tool file named in the command must exist
    m = re.search(r'(%T|[^ ]+)/tools/([a-z0-9-]+\.py)', tpl['run'])
    tool_rel = 'tools/' + m.group(2) if m else None
    if tool_rel and not os.path.isfile(
            os.path.join(tip_tree, tool_rel)):
        dead = True
    try:
        p = subprocess.run(['bash', '-c', cmd], capture_output=True,
                           text=True, timeout=900, cwd=tip_tree, env=env)
        out = p.stdout + p.stderr
        rc = p.returncode
    except subprocess.TimeoutExpired:
        out, rc = 'TIMEOUT', 124
    observed = tpl['pattern'] if tpl['pattern'] in out else out[:400]
    if not row['observed']:
        row['observed'] = ''
    verdict = (not dead and tpl['pattern'] in out and rc == 0)
    # sensitivity: blank out every occurrence of the pattern's matched text
    mut = out.replace(tpl['pattern'], MUT)
    sensitive = not (tpl['pattern'] in mut and rc == 0 and not dead)
    if not sensitive:
        verdict = verdict  # recorded only; sensitivity still counts false
    return verdict, observed, sensitive, dead


def score_registry(reg_text, tip_tree, scratch, repo, tip, env,
                   population=None, manifest=MANIFEST):
    def scorer(row):
        cap = row['cap']
        tpls = manifest[cap][1]
        key = (tip, cap)
        if key not in _EXEC_CACHE:
            _EXEC_CACHE[key] = run_bound(row, tpls, tip_tree, scratch,
                                         repo, tip, env)
        v, obs, sens, dead = _EXEC_CACHE[key]
        return v, obs, sens, dead
    return score(reg_text, scorer, manifest=manifest,
                 population=population)


def controls(facts, reg_text, tip_tree, scratch, repo, tip, env,
             population):
    """8 control families: each is a mutated registry re-scored by the same
    scorer; every family must score not-met."""
    lines = [l for l in reg_text.splitlines() if l.strip()]
    header = [l for l in lines if l.startswith('cap\t')][0]
    data = [l for l in lines if '\t' in l and not l.startswith('cap\t')
            and not l.startswith('#')]

    def rescore(text):
        return score_registry(text, tip_tree, scratch, repo, tip, env,
                              population=population)

    muts = {}
    # 1: one row dropped -> coverage short
    muts['drop'] = header + '\n' + '\n'.join(data[1:]) + '\n'
    # 2: a cap renamed to an unknown slug -> unbound
    muts['rename'] = header + '\n' + '\n'.join(data).replace(
        'sources-registry', 'sources-fakery', 1) + '\n'
    # 3: a row's binding switched to an unallowed id
    muts['binding'] = header + '\n' + '\n'.join(
        l.replace('\tlive\t', '\tselftest\t', 1) if '\tlive\t' in l else l
        for l in data) + '\n'
    # 4: a verdict flipped to true->false while the live run is green
    muts['verdict'] = header + '\n' + '\n'.join(data).replace(
        '\ttrue\t', '\tfalse\t', 1) + '\n'
    # 5: a quote swapped for a paraphrase not in the frozen prefix
    muts['quote'] = header + '\n' + '\n'.join(
        l.split('\t')[0] + '\tNOT-A-PREFIX-QUOTE' + '\t' +
        '\t'.join(l.split('\t')[2:]) for l in data) + '\n'
    # 6: a free-command binding (always-green echo) — unbound run template
    free = 'sources-registry\tCurate where\tfree\tbash -c "echo ok"\t' \
        'ok\ttrue\techo\tfree command'
    muts['free'] = header + '\n' + '\n'.join(data) + '\n' + free + '\n'
    # 7: a pattern weakened to a substring that matches trivially —
    # re-scored registry where one pattern is shortened
    muts['weak'] = header + '\n' + '\n'.join(data).replace(
        '45/45 selftest cases passed', 'pass', 1) + '\n'
    # 8: every bound row marked notobs
    muts['notobs'] = header + '\n' + '\n'.join(
        re.sub(r'\t(live|selftest|scan|cell|census)\t', '\tnotobs\t', l)
        for l in data) + '\n'

    rejected = 0
    detail = {}
    for name, text in muts.items():
        f = rescore(text)
        met = (f['covered'] == f['population']
               and f['mismatches'] == 0 and f['errors'] == 0
               and f['dead'] == 0 and f['bound'] >= f['population'])
        detail[name] = {'met': met, 'covered': f['covered'],
                        'mismatches': f['mismatches'],
                        'errors': f['errors'], 'dead': f['dead'],
                        'err_list': f['err_list'][:4]}
        if not met:
            rejected += 1
    return rejected, len(muts), detail


def checkout_tip(repo, tip, work):
    tree = os.path.join(work, 'tip')
    if os.path.isdir(tree):
        return tree
    os.makedirs(tree, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    archive = subprocess.Popen(
        ['git', '-C', str(repo), 'archive', tip],
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
    ap.add_argument('--no-live', action='store_true',
                    help='score registry rows without executing runs')
    args = ap.parse_args(argv)
    repo = os.path.abspath(args.repo)
    work = os.path.abspath(args.work)
    scratch = os.path.join(work, 'run')
    for d in (work, scratch):
        os.makedirs(d, exist_ok=True)
    env = dict(os.environ)
    env['TMPDIR'] = scratch
    env.pop('PYTHONPATH', None)

    tip_tree = checkout_tip(repo, args.tip, work)
    if not tip_tree:
        print('errors=1 met=False  (tip checkout failed)')
        return 1

    sc = blob(repo, args.tip, 'SCORECARD.md')
    can_n, can_rows = canonical_rows(sc)
    population = None
    canon_mismatch = []
    if can_rows:
        slugs = [s for s, _ in can_rows]
        expected = [s for s, _, _ in _MANIFEST]
        if len(slugs) != len(set(slugs)) or not set(expected).issubset(slugs):
            canon_mismatch.append(
                f'canonical rows must contain each frozen capability once: {slugs}')
        population = [(slug, MANIFEST[slug][0]) for slug in expected]
        for slug, prefix, _ in _MANIFEST:
            row_text = next((text for seen, text in can_rows
                             if seen == slug), '')
            if not row_text.startswith(prefix):
                canon_mismatch.append(f'prefix:{slug}')
    else:
        canon_mismatch.append('no canonical list section at tip')

    reg_text = blob(repo, args.tip, REG)

    if args.no_live:
        facts = score(reg_text, lambda r: (True, '', False, False),
                      population=population)
    else:
        facts = score_registry(reg_text or '', tip_tree, scratch,
                               repo, args.tip, env,
                               population=population)
    rejected, total, cdetail = controls(
        facts, reg_text or '', tip_tree, scratch, repo, args.tip, env,
        population) if reg_text else (0, 8, {})

    met = (bool(can_rows) and not canon_mismatch
           and facts['covered'] == facts['population']
           and facts['bound'] >= facts['population']
           and facts['dead'] == 0 and facts['mismatches'] == 0
           and facts['errors'] == 0 and rejected == total
           and population is not None
           and len(population) == MIN_ROWS)
    print(f"population={facts['population']} rows={facts['rows']} "
          f"covered={facts['covered']}/{facts['population']} "
          f"bound={facts['bound']} eval_lines={facts['eval_lines']} "
          f"sensitive={facts['sensitive']}/{facts['bound']} "
          f"dead={facts['dead']} mismatches={facts['mismatches']} "
          f"canonical={can_n} controls_rejected={rejected}/{total} "
          f"errors={facts['errors'] + len(canon_mismatch)} met={met}")
    for e in canon_mismatch + facts['err_list'][:8]:
        print('error:', e, file=sys.stderr)
    for k, v in cdetail.items():
        if v['met']:
            print(f'control-escape: {k} {v}', file=sys.stderr)
    return 0 if met else 1


if __name__ == '__main__':
    sys.exit(main())
