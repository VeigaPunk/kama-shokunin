import importlib.util, json, sys
from pathlib import Path
CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase37/clone")
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
grid = load("promisor_grid", CLONE / "tests/report-audit/promisor-grid.py")
aud = load("report_landing_audit", CLONE / "tools/report-landing-audit.py")
root = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase37/tmp-inspect/root")
tmp = root / "001"; tmp.mkdir(parents=True, exist_ok=True)
built = grid.BUILDERS["c_unused_missing_blob_fabricated_plain"](root, tmp)
lane, fleet = built["lane"], built["fleet"]
stores = [aud.build_store(lane, "refs/heads/master"), aud.build_store(fleet, "HEAD")]
FAKE = built["shas"]["fake"]
print("lookup(FAKE) full-hash  ->", aud.lookup(stores, [FAKE]))
status = aud.lookup(stores, [FAKE])
print("unknown_citation(FAKE)  ->", aud.unknown_citation(stores, FAKE))
print("opaque_hole              ->", aud.opaque_hole(stores))
print("missing sets             ->", [(s.path, s.missing()) for s in stores])
try:
    aud.refuse_unknown(1, status, stores)
    print("refuse_unknown(full-hash path): NO REFUSAL (scoped path taken)")
except aud.EvalError as e:
    print("refuse_unknown(full-hash path): REFUSAL:", e)
# landed-section path: the 40-hex token is also an abbreviation candidate
cited = set(aud.ABBREV.findall("- 0123456789abcdef0123456789abcdef01234567"))
print("cited abbreviations      ->", sorted(cited))
st2 = aud.lookup(stores, [t for t in cited if aud.checkable_abbrev(t)], "^{commit}")
print("lookup(landed, ^{commit}) ->", st2)
try:
    aud.refuse_unknown(1, st2, stores)
    print("refuse_unknown(landed path): NO REFUSAL (scoped path taken)")
except aud.EvalError as e:
    print("refuse_unknown(landed path): REFUSAL:", e)
