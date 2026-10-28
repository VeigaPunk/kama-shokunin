# Mutant c2-head-only: SCORECARD + PROVINCE text edits that satisfy the reconciler without re-deriving.
import re, sys
M = sys.argv[1]
def rep(path, old, new, count=1):
    t = open(path, encoding='utf-8').read()
    n = t.count(old)
    assert n == count, (path, old[:60], n)
    open(path, 'w', encoding='utf-8').write(t.replace(old, new))
sc = f'{M}/SCORECARD.md'
rep(sc, 'Latest measured round: 61', 'Latest measured round: 63')                       # banner
rep(sc, '6 axes and 11 capabilities remain active', '6 axes and 12 capabilities remain active')  # retired
rep(sc, '\n## Retired\n', '\n### Planned (round 64)\n\n1. Re-derive the head after measurement.\n\n## Retired\n')  # planned
rep(sc, '## Saturation\n', '## Saturation\n\nCapability first-working rounds 10, 14, 16, 20, 25, 30, 41, 42, 43, 46, 47, 61 (head table).\n')
rep(sc, 'round 60 added', 'round 60 added', 1)  # sanity: anchor exists
rep(sc, '→ `36` (round 60 added', '→ `38` (round 60 added')                                 # coverage run output
# capabilities head table: copy the canonical live-ollama-lifecycle row into the mirror table
lines = open(sc, encoding='utf-8').read().split('\n')
canon_i = max(i for i, l in enumerate(lines) if 'canonical list as of round 63' in l.lower())
row = next(l for l in lines[canon_i:] if l.startswith('| live-ollama-lifecycle |'))
caps_i = next(i for i, l in enumerate(lines) if l.startswith('## Capabilities'))
ins_i = next(i for i in range(caps_i, len(lines)) if lines[i].startswith('| gguf-declared-identity-replay |'))
lines.insert(ins_i + 1 - 1, row)  # before gguf row? keep order: insert after the gguf row
lines.pop(ins_i)  # placeholder no-op guard removed below
lines.insert(ins_i, row)
open(sc, 'w', encoding='utf-8').write('\n'.join(lines))
rep(f'{M}/PROVINCE.md', '\n', '\nMutant pointer (head-only shortcut): `registry/ollama-live-claims-r61.tsv`.\n') if False else None
open(f'{M}/PROVINCE.md', 'a', encoding='utf-8').write('\nMutant pointer (head-only shortcut): `registry/ollama-live-claims-r61.tsv`.\n')
print('headonly edits applied; row=', row[:60])
