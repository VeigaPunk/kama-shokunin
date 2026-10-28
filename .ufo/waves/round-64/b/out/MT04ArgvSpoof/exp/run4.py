import sys, ast
sys.path.insert(0, '/fast/scratch/hyaku/kama-r64/b/MT04ArgvSpoof/exp')
import drive3
from drive import run_variant
for n in sys.argv[1:]:
    text = drive3.V[n]()
    ast.parse(text)
    run_variant(n + '_r3', text)
