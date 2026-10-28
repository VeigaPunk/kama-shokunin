import sys, ast
sys.path.insert(0, '/fast/scratch/hyaku/kama-r64/b/MT04ArgvSpoof/exp')
import drive3
from drive import run_variant
from drive3 import build, MODEL_PRE
V = {
 'B6_dup_model_long': lambda: build(MODEL_PRE + "; receipt['argv'] = receipt['argv'] + ['--model', _alt]"),
 'B7_alias_comma': lambda: build("; receipt['argv'] = [('kama-completion-probe,other' if x == 'kama-completion-probe' else x) for x in receipt['argv']]"),
}
for n in sys.argv[1:]:
    text = V[n](); ast.parse(text); run_variant(n + '_r3', text)
